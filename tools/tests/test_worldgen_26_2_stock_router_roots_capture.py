"""Stock 26.2 NoiseRouter root inventory: strict parse, source and toy JVM."""
from __future__ import annotations

import copy
import shutil
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import worldgen_26_2_stock_router_roots_capture as router  # noqa: E402


class RouterRootsTests(unittest.TestCase):
    def methods(self):
        return {
            label: {
                "owner": owner, "signature": name + "()",
                "body_sha256": digest, "normalized_sha256": "b"*64,
                "reviewed": False,
            }
            for label, owner, name, digest in (
                ("router_map_all", router.ROUTER, "mapAll", router.ROUTER_MAP_ALL_SHA256),
                ("random_state_router", router.STATE, "router", "a"*64),
            )
        }

    def roots(self):
        return [{
            "world_seed_bits": seed,
            "fields": [{
                "field": f"root{i:02d}",
                "implementation_class": ("net.minecraft.world.level.levelgen.DensityFunctions$Mul"
                                         if i == 0 else
                                         "net.minecraft.world.level.levelgen.DensityFunctions$Constant"),
                "compute_declaring_class": ("net.minecraft.world.level.levelgen.DensityFunctions$Mul"
                                           if i == 0 else
                                           "net.minecraft.world.level.levelgen.DensityFunctions$Constant"),
                "first_level_density_children": ([
                    {"slot": "left",
                     "implementation_class":
                     "net.minecraft.world.level.levelgen.DensityFunctions$Constant"},
                    {"slot": "right",
                     "implementation_class":
                     "net.minecraft.world.level.levelgen.DensityFunctions$Constant"},
                ] if i == 0 else []),
            } for i in range(15)]
        } for seed in router.SEEDS]

    def tagged(self):
        lines = ["minecraft starts here"]
        for j, seed in enumerate(self.roots()):
            lines.append(router.TAG_HEADER + f"{j}|15|{router.ROUTER}")
            for i, field in enumerate(seed["fields"]):
                children = field["first_level_density_children"]
                lines.append(router.TAG_FIELD +
                             f"{j}|{i}|{field['field']}|{field['implementation_class']}|"
                             f"{field['compute_declaring_class']}|{len(children)}")
                for k, child in enumerate(children):
                    lines.append(router.TAG_CHILD +
                                 f"{j}|{i}|{k}|{child['slot']}|"
                                 f"{child['implementation_class']}")
        return lines

    def manifest(self):
        return {
            "schema": 1, "kind": router.KIND, "minecraft": "26.2",
            "protocol": 776, "data_version": 4903,
            "source_archive_sha256": router.frozen.SOURCE_SHA256,
            "official_server_sha256": router.frozen.SERVER_SHA256,
            "frontier_sha256": router.stock.FRONTIER_SHA256,
            "original_stock_noise_fixture_sha256": router.frozen.FIXTURE_SHA256,
            "original_mixed_density_fixture_sha256": router.mixed.FIXTURE_SHA256,
            "source_methods": self.methods(), "world_seeds": list(router.SEEDS),
            "noise_router_field_count": 15,
            "stock_registry_used": True, "world_seed_random_state_observed": True,
            "world_seed_random_state_bound": False,
            "router_numeric_parity_qualified": False, "router_full_graph_qualified": False,
            "source_text_included": False, "independent_var_sem_admitted": False,
            "production_worldgen_enabled": False,
            "bound_router_roots": self.roots(),
        }

    def test_parse_four_seeds_all_fifteen_ordered_roots_and_first_level_edges(self):
        parsed = router.parse_output("\n".join(self.tagged()))
        self.assertEqual(parsed, self.roots())
        self.assertEqual(sum(len(x["fields"]) for x in parsed), 60)
        self.assertEqual(parsed[2]["fields"][0]["first_level_density_children"][1]["slot"],
                         "right")
        router.validate(self.manifest(), methods=self.methods())

    def test_mutated_transport_requires_all_seeds_and_canonical_order(self):
        full = self.tagged()
        tags = [i for i, line in enumerate(full)
                if line.startswith(router.TAG_FIELD)]
        for trial in (
            full[:-1], full + full[-1:],
            full[:tags[2]] + full[tags[2]+1:],
            full[:tags[2]] + full[tags[2]:tags[2]+1] + full[tags[2]:],
            full[:tags[1]] + full[tags[2]:tags[3]] +
            full[tags[1]:tags[2]] + full[tags[3]:],
            [line.replace("root01", "root00") if line.startswith(router.TAG_FIELD)
             else line for line in full],
        ):
            with self.subTest(size=len(trial)):
                with self.assertRaises(router.RouterRootsError):
                    router.parse_output("\n".join(trial))
        with self.assertRaisesRegex(router.RouterRootsError, "JVM PHASE"):
            router.parse_output(router.TAG_FAILURE +
                                "stock-RandomState-router|java.lang.IllegalStateException"
                                "|java.lang.reflect.InvocationTargetException|unknown getter")

    def test_schema_rejects_any_gate_flip_names_duplicate_children_or_bad_source(self):
        mutations = [
            lambda r: r.__setitem__("world_seed_random_state_bound", True),
            lambda r: r.__setitem__("router_numeric_parity_qualified", True),
            lambda r: r.__setitem__("router_full_graph_qualified", True),
            lambda r: r.__setitem__("production_worldgen_enabled", True),
            lambda r: r.__setitem__("independent_var_sem_admitted", True),
            lambda r: r.__setitem__("source_text_included", True),
            lambda r: r.__setitem__("original_mixed_density_fixture_sha256", "bad"),
            lambda r: r.__setitem__("source_methods", {}),
            lambda r: r["bound_router_roots"].reverse(),
            lambda r: r["bound_router_roots"][0]["fields"].pop(),
            lambda r: r["bound_router_roots"][0]["fields"][0].__setitem__("field", "bad|name"),
            lambda r: r["bound_router_roots"][0]["fields"][0]
                    ["first_level_density_children"].append({
                        "slot": "left", "implementation_class":
                        "net.minecraft.world.level.levelgen.DensityFunctions$Constant"}),
        ]
        for mutate in mutations:
            data = copy.deepcopy(self.manifest())
            mutate(data)
            with self.subTest(change=str(mutate)):
                with self.assertRaises(router.RouterRootsError):
                    router.validate(data, methods=self.methods())

    def test_atlas_exact_router_method_body_pins_are_rechecked(self):
        conn = sqlite3.connect(":memory:")
        conn.row_factory = sqlite3.Row
        conn.executescript("""
            CREATE TABLE types(id INTEGER PRIMARY KEY,qualified_name TEXT);
            CREATE TABLE methods(id INTEGER PRIMARY KEY, type_id INTEGER,
                name TEXT, signature TEXT, param_count INTEGER,
                body_sha256 TEXT, normalized_sha256 TEXT);
            INSERT INTO types VALUES(1,'net.minecraft.world.level.levelgen.NoiseRouter');
            INSERT INTO types VALUES(2,'net.minecraft.world.level.levelgen.RandomState');
        """)
        conn.executemany(
            "INSERT INTO methods VALUES(?,?,?,?,?,?,?)",
            [(1, 1, "mapAll", "mapAll(Visitor)", 1,
              router.ROUTER_MAP_ALL_SHA256, "b"*64),
             (2, 2, "router", "router()", 0, "a"*64, "b"*64)],
        )
        methods = router.source_methods(conn)
        self.assertEqual(methods["router_map_all"]["body_sha256"],
                         router.ROUTER_MAP_ALL_SHA256)
        self.assertFalse(methods["random_state_router"]["reviewed"])
        conn.execute("UPDATE methods SET body_sha256=? WHERE id=1", ("f"*64,))
        with self.assertRaisesRegex(router.RouterRootsError, "mapAll"):
            router.source_methods(conn)
        conn.close()

    def test_mocked_capture_uses_source_pinned_stock_provider_and_exclusive_output(self):
        import json
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            lock = root/"lock.toml"
            lock.write_text(
                'minecraft="26.2"\nprotocol=776\ndata_version=4903\n'
                '[runtime]\nserver_sha256="'+router.frozen.SERVER_SHA256+'"\n')
            output = root/"official-router.json"
            with mock.patch.object(router.stock, "reference_frontier"), \
                 mock.patch.object(router.vanilla_atlas, "connect_db"), \
                 mock.patch.object(router.source_probe, "require_pinned_source",
                                   return_value=router.frozen.SOURCE_SHA256), \
                 mock.patch.object(router, "source_methods",
                                   return_value=self.methods()), \
                 mock.patch.object(router.official, "sha256_file",
                                   return_value=router.frozen.SERVER_SHA256), \
                 mock.patch.object(router, "observe", return_value=self.roots()):
                result = router.capture(source=root/"source.zip", db=root/"atlas",
                                        lock=lock, server=root/"server.jar",
                                        frontier=root/"frontier", output=output)
            self.assertEqual(result["bound_density_roots"], 60)
            self.assertFalse(result["complete_router_qualified"])
            self.assertFalse(result["production_worldgen_enabled"])
            observed = json.loads(output.read_text())
            router.validate(observed, methods=self.methods())
            with self.assertRaises(router.improved.CaptureError):
                # Only the existing destination rejection is exercised.
                with mock.patch.object(router.stock, "reference_frontier"), \
                     mock.patch.object(router.vanilla_atlas, "connect_db"), \
                     mock.patch.object(router.source_probe, "require_pinned_source",
                                       return_value=router.frozen.SOURCE_SHA256), \
                     mock.patch.object(router, "source_methods",
                                       return_value=self.methods()), \
                     mock.patch.object(router.official, "sha256_file",
                                       return_value=router.frozen.SERVER_SHA256), \
                     mock.patch.object(router, "observe", return_value=self.roots()):
                    router.capture(source=root/"source.zip", db=root/"atlas",
                                   lock=lock, server=root/"server.jar",
                                   frontier=root/"frontier", output=output)

    @unittest.skipUnless(shutil.which("javac") and shutil.which("java"),
                         "Java toolchain required for independent toy JVM transport")
    def test_actual_java_bridge_reflects_real_record_components_with_redirected_stdout(self):
        with tempfile.TemporaryDirectory(prefix="helve-router-shape-toy-") as folder:
            workspace = Path(folder)
            source = workspace/"java"
            def java(package, name, body):
                path=source/package.replace(".","/")/(name+".java")
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(f"package {package};\n{body}\n")
            java("net.minecraft", "SharedConstants",
                 "public class SharedConstants {"
                 "public static void tryDetectVersion() {} }")
            java("net.minecraft.server", "Bootstrap",
                 "public class Bootstrap { public static void bootStrap(){"
                 "System.setOut(new java.io.PrintStream(new java.io.ByteArrayOutputStream()));}}")
            java("net.minecraft.resources", "ResourceKey",
                 "public record ResourceKey(String name) {}")
            java("net.minecraft.core", "HolderGetter",
                 "public interface HolderGetter { interface Provider {} }")
            java("net.minecraft.core", "HolderLookup",
                 "public interface HolderLookup { interface Provider "
                 "extends net.minecraft.core.HolderGetter.Provider {} }")
            level="net.minecraft.world.level.levelgen"
            java("net.minecraft.data.registries", "VanillaRegistries",
                 "public class VanillaRegistries {"
                 "public static net.minecraft.core.HolderLookup.Provider createLookup()"
                 "{ return new net.minecraft.core.HolderLookup.Provider(){};}}")
            java(level, "NoiseGeneratorSettings",
                 "public class NoiseGeneratorSettings {"
                 "public static final net.minecraft.resources.ResourceKey OVERWORLD="
                 "new net.minecraft.resources.ResourceKey(\"OVERWORLD\");}")
            java(level, "DensityFunction",
                 "public interface DensityFunction {"
                 "double compute(FunctionContext context);"
                 "interface FunctionContext {} }")
            java(level, "DensityFunctions",
                 "public class DensityFunctions {"
                 "public record Constant(double value) implements DensityFunction {"
                 "public double compute(DensityFunction.FunctionContext c){return value;}}"
                 "public record Mul(DensityFunction left,DensityFunction right)"
                 "implements DensityFunction {"
                 "public double compute(DensityFunction.FunctionContext c) {"
                 "return left.compute(c)*right.compute(c);}}"
                 # Deliberately package-private with a public generated accessor.
                 "record FindTopSurface(DensityFunction delegate)"
                 "implements DensityFunction {"
                 "public double compute(DensityFunction.FunctionContext c){"
                 "return delegate.compute(c);}}}")
            fields=", ".join("DensityFunction root%02d"%i for i in range(15))
            ctor=", ".join((
                "new DensityFunctions.Mul(new DensityFunctions.Constant(1.0),"
                "new DensityFunctions.Constant(2.0))"
                if i==0 else
                "new DensityFunctions.FindTopSurface("
                "new DensityFunctions.Constant(42.0))"
                if i==10 else
                "new DensityFunctions.Constant("+str(i)+".0)")
                for i in range(15))
            java(level, "NoiseRouter",f"public record NoiseRouter({fields}) {{}}")
            java(level,"RandomState",
                 "public class RandomState {"
                 "public static RandomState create("
                 "net.minecraft.core.HolderGetter.Provider p,"
                 "net.minecraft.resources.ResourceKey settings,long seed)"
                 "{return new RandomState();}"
                 f"public NoiseRouter router() {{return new NoiseRouter({ctor});}}"
                 "}")
            out=workspace/"classes"
            built=subprocess.run(
                ["javac","-encoding","UTF-8","-d",str(out),
                 *[str(path) for path in source.rglob("*.java")]],
                capture_output=True,text=True,check=False,timeout=45)
            self.assertEqual(built.returncode,0,built.stderr)
            with mock.patch.object(router.official, "extract_classpath",
                                   return_value=[out]):
                records=router.observe(workspace/"toy.jar",timeout=90)
            self.assertEqual(len(records),4)
            self.assertEqual(len(records[0]["fields"]),15)
            self.assertEqual(
                [item["slot"] for item in
                 records[0]["fields"][0]["first_level_density_children"]],
                ["left", "right"])
            self.assertEqual(records[0]["fields"][0]["field"],"root00")
            # Exact official failure analogue: field 10 contains a
            # package-private nested record whose typed child accessor must
            # be explicitly accessible to the standalone reflection probe.
            self.assertEqual(
                records[0]["fields"][10]["implementation_class"],
                level+".DensityFunctions$FindTopSurface",
            )
            for seed in records:
                self.assertEqual(
                    seed["fields"][10]["first_level_density_children"],
                    [{"slot": "delegate",
                      "implementation_class": level+".DensityFunctions$Constant"}],
                )


if __name__ == "__main__":
    unittest.main()
