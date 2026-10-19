"""Source-free negative tests and independent toy JVM for the density delegate frontier.

The toy code demonstrates only reflection, not any Minecraft implementation.
"""
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
import worldgen_26_2_density_delegate_frontier as frontier  # noqa: E402


class DensityDelegateFrontierTests(unittest.TestCase):
    @staticmethod
    def classes():
        root = "net.minecraft.world.level.levelgen.DensityFunctions"
        return {
            name: {
                "implementation_class": root + ("$Add" if name.startswith("add") else "$Mul"),
                "compute_declaring_class": root + ("$Add" if name.startswith("add") else "$Mul"),
                "superclass": "java.lang.Record",
            }
            for name in frontier.PROFILES
        }

    @staticmethod
    def lock():
        return {
            "source": {"archive_sha256": "a" * 64},
            "runtime": {"server_sha256": "b" * 64},
        }

    def test_exact_eight_reflection_profiles_and_java_record_superclass(self):
        records = self.classes()
        lines = "\n".join(
            "\t".join((name, data["implementation_class"],
                       data["compute_declaring_class"], data["superclass"]))
            for name, data in records.items()
        )
        self.assertEqual(frontier.parse_runtime_output(lines), records)
        with self.assertRaises(frontier.DelegateFrontierError):
            frontier.parse_runtime_output(lines.replace("add_gradients", "mul_gradients", 1))
        with self.assertRaises(frontier.DelegateFrontierError):
            frontier.parse_runtime_output(lines.replace("java.lang.Record", "injected.Bad", 1))
        with self.assertRaises(frontier.DelegateFrontierError):
            frontier.parse_runtime_output(lines + "\nextra")

    def manifest(self):
        classes = self.classes()
        roots = sorted(set(frontier.REQUIRED_ROOTS) | {
            data["compute_declaring_class"] for data in classes.values()
        })
        indexed = []
        for name in roots:
            methods = []
            if name.endswith("$Add") or name.endswith("$Mul"):
                methods = [{
                    "owner": name,
                    "signature": "compute(final DensityFunction . FunctionContext context)",
                    "body_sha256": "c" * 64,
                    "normalized_sha256": "d" * 64,
                    "atlas_observed_hazards": [],
                    "atlas_classifications": [],
                    "calls": {"call_sites": 0, "resolved_targets": [],
                              "unresolved_call_sites": 0, "top_unresolved_callees": []},
                    "reviewed": False,
                }]
            indexed.append({
                "type": name,
                "status": "indexed_not_reviewed",
                "method_count": len(methods),
                "methods": methods,
            })
        return {
            "schema": 1, "kind": frontier.KIND, "minecraft": "26.2",
            "protocol": 776, "data_version": 4903,
            "stage": "density_router_delegate_discovery",
            "source_archive_sha256": "a" * 64,
            "official_server_sha256": "b" * 64,
            "runtime_startup_sequence": frontier.primitive.STARTUP_SEQUENCE.copy(),
            "composition_factories": frontier.COMPOSITION_BODY_PINS.copy(),
            "runtime_profiles": classes,
            "atlas_frontier": {
                "types": indexed, "nested_density_type_count": 2,
                "selected_method_count": 2,
            },
            "source_text_included": False,
            "independent_var_sem_admitted": False,
            "production_worldgen_enabled": False,
        }

    def test_metadata_and_admission_mutations_fail_closed(self):
        manifest = self.manifest()
        frontier.validate(manifest, self.lock())
        mutations = [
            lambda m: m.__setitem__("source_text_included", True),
            lambda m: m.__setitem__("independent_var_sem_admitted", True),
            lambda m: m.__setitem__("production_worldgen_enabled", True),
            lambda m: m["composition_factories"].__setitem__("mul_factory", "0"*64),
            lambda m: m["runtime_startup_sequence"].reverse(),
            lambda m: m["runtime_profiles"].pop("mul_half"),
            lambda m: m["runtime_profiles"]["mul_gradients"].__setitem__(
                "compute_declaring_class", "java.lang.Reflect"),
            lambda m: m["atlas_frontier"].__setitem__("selected_method_count", 1),
            lambda m: m["atlas_frontier"]["types"][-1]["methods"][0].__setitem__("reviewed", True),
            lambda m: m["atlas_frontier"]["types"][-1]["methods"][0].__setitem__(
                "body_sha256", "unbound"),
            lambda m: m["atlas_frontier"]["types"].pop(0),
            lambda m: m.__setitem__("unqualified_router", {}),
        ]
        for mutate in mutations:
            with self.subTest(mutate=str(mutate)):
                trial = copy.deepcopy(manifest)
                mutate(trial)
                with self.assertRaises(frontier.DelegateFrontierError):
                    frontier.validate(trial, self.lock())

    def test_pinned_sqlite_inventory_selects_actual_runtime_compute_owners(self):
        conn = sqlite3.connect(":memory:")
        conn.row_factory = sqlite3.Row
        conn.executescript("""
        CREATE TABLE source_files (id INTEGER PRIMARY KEY, path TEXT);
        CREATE TABLE types (id INTEGER PRIMARY KEY, qualified_name TEXT, file_id INTEGER);
        CREATE TABLE methods (
            id INTEGER PRIMARY KEY, type_id INTEGER, name TEXT, signature TEXT,
            param_count INTEGER, start_line INTEGER, end_line INTEGER
        );
        INSERT INTO source_files VALUES(1,'synthetic-source.java');
        """)
        roots = [frontier.primitive.DENSITY,
                 "net.minecraft.world.level.levelgen.DensityFunction",
                 frontier.primitive.DENSITY + "$Add", frontier.primitive.DENSITY + "$Mul"]
        for i, name in enumerate(roots, start=1):
            conn.execute("INSERT INTO types VALUES(?,?,1)", (i, name))
        conn.executemany("INSERT INTO methods VALUES(?,?,?,?,?,?,?)", [
            (1,1,"add","add(DensityFunction x, DensityFunction y)",2,10,13),
            (2,1,"mul","mul(DensityFunction x, DensityFunction y)",2,15,18),
            (3,3,"compute","compute(DensityFunction.FunctionContext context)",1,25,28),
            (4,4,"compute","compute(DensityFunction.FunctionContext context)",1,32,36),
        ])
        def template(_conn, row, _label):
            return {
                "source": {"type": row["qualified_name"], "signature": row["signature"],
                           "body_sha256": "a"*64, "normalized_sha256": "b"*64},
                "atlas_observed_hazards": [], "classifications": [],
            }
        with mock.patch.object(frontier.source_probe, "record_template", side_effect=template), \
             mock.patch.object(frontier.projection, "_call_inventory", return_value={
                 "call_sites": 0, "resolved_targets": [],
                 "unresolved_call_sites": 0, "top_unresolved_callees": [],
             }):
            result = frontier.inventory(conn, self.classes())
            self.assertEqual(result["selected_method_count"], 4)
            self.assertEqual(result["nested_density_type_count"], 2)
            self.assertTrue(all(m["reviewed"] is False for item in result["types"]
                                for m in item["methods"]))
            self.assertEqual(next(item for item in result["types"]
                                  if item["type"] == roots[2])["methods"][0]["signature"],
                             "compute(DensityFunction.FunctionContext context)")
            conn.execute("DELETE FROM methods WHERE id=3")
            with self.assertRaisesRegex(frontier.DelegateFrontierError, "compute source method"):
                frontier.inventory(conn, self.classes())
        conn.close()

    @unittest.skipUnless(shutil.which("javac") and shutil.which("java"),
                         "Java toolchain unavailable for independent synthetic reflection")
    def test_original_jvm_reflection_reports_real_compute_declaring_type(self):
        with tempfile.TemporaryDirectory() as folder:
            base = Path(folder)
            java_root = base / "src"
            root = java_root / "net/minecraft"
            boot = root / "server"
            density = root / "world/level/levelgen"
            for path in (root, boot, density):
                path.mkdir(parents=True, exist_ok=True)
            (root / "SharedConstants.java").write_text(
                """package net.minecraft;
                public final class SharedConstants {
                  public static boolean ready;
                  public static void tryDetectVersion() { ready = true; }
                }""", encoding="utf-8")
            (boot / "Bootstrap.java").write_text(
                """package net.minecraft.server;
                public final class Bootstrap {
                  static boolean ready;
                  public static void bootStrap() {
                    if (!net.minecraft.SharedConstants.ready)
                       throw new IllegalStateException("bad startup");
                    ready = true;
                  }
                  public static boolean ready() { return ready; }
                }""", encoding="utf-8")
            (density / "DensityFunction.java").write_text(
                """package net.minecraft.world.level.levelgen;
                public interface DensityFunction {
                  double compute(FunctionContext c);
                  interface FunctionContext {}
                }""", encoding="utf-8")
            (density / "DensityFunctions.java").write_text(
                """package net.minecraft.world.level.levelgen;
                public final class DensityFunctions {
                  static {
                    if (!net.minecraft.server.Bootstrap.ready())
                      throw new ExceptionInInitializerError("not bootstrapped");
                  }
                  public static DensityFunction constant(double d) {
                    return new Constant(d);
                  }
                  public static DensityFunction yClampedGradient(
                      int a,int b,double c,double d) {
                    return new Gradient(c,d);
                  }
                  public static DensityFunction add(DensityFunction a,DensityFunction b) {
                    return new Add(a,b);
                  }
                  public static DensityFunction mul(DensityFunction a,DensityFunction b) {
                    return new Mul(a,b);
                  }
                  public record Constant(double v) implements DensityFunction {
                    public double compute(DensityFunction.FunctionContext c) {return v;}
                  }
                  public record Gradient(double a,double b) implements DensityFunction {
                    public double compute(DensityFunction.FunctionContext c) {return a+b;}
                  }
                  public record Add(DensityFunction a,DensityFunction b) implements DensityFunction {
                    public double compute(DensityFunction.FunctionContext c) {
                      return a.compute(c)+b.compute(c);
                    }
                  }
                  public record Mul(DensityFunction a,DensityFunction b) implements DensityFunction {
                    public double compute(DensityFunction.FunctionContext c) {
                      return a.compute(c)*b.compute(c);
                    }
                  }
                }""", encoding="utf-8")
            classes = base / "classes"
            compile_result = subprocess.run(
                ["javac", "-encoding", "UTF-8", "-d", str(classes),
                 *[str(p) for p in java_root.rglob("*.java")]],
                text=True, capture_output=True, timeout=30,
            )
            self.assertEqual(compile_result.returncode, 0, compile_result.stderr)
            with mock.patch.object(frontier.official, "extract_classpath", return_value=[classes]):
                result = frontier.runtime_classes(base / "toy.jar", timeout=30)
            self.assertEqual(result, self.classes())


if __name__ == "__main__":
    unittest.main()
