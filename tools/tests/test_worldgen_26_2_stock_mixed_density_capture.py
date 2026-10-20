"""Independent synthetic JVM and strict schema checks for 1,920 mixed values."""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import worldgen_26_2_stock_mixed_density_capture as target  # noqa: E402
import worldgen_26_2_stock_worldseed_fixture as original  # noqa: E402


class StockMixedDensityCaptureTests(unittest.TestCase):
    @staticmethod
    def methods():
        def method(owner, name, sha="a" * 64):
            return {
                "owner": owner, "signature": name,
                "body_sha256": sha, "normalized_sha256": "b" * 64,
            }
        return {
            "worldseed_noise": {"stock_vanilla_lookup":
                method("net.minecraft.data.registries.VanillaRegistries", "createLookup()",
                       original.VANILLA_STOCK_LOOKUP_SHA256)},
            "density_primitives": {
                "gradient_factory": method("net.minecraft.world.level.levelgen.DensityFunctions",
                                           "yClampedGradient(int,int,double,double)")},
            "composition_factories": {
                "add_factory": method("net.minecraft.world.level.levelgen.DensityFunctions",
                                      "add(DensityFunction,DensityFunction)",
                                      target.METHOD_BODY_PINS["add_factory"]),
                "mul_factory": method("net.minecraft.world.level.levelgen.DensityFunctions",
                                      "mul(DensityFunction,DensityFunction)",
                                      target.METHOD_BODY_PINS["mul_factory"]),
            },
        }

    @staticmethod
    def delegates():
        return {
            p: {
                "implementation_class": "net.minecraft.world.level.levelgen.DensityFunctions$Ap2",
                "compute_declaring_class": "net.minecraft.world.level.levelgen.DensityFunctions$Ap2",
                "superclass": "java.lang.Object",
            }
            for p in target.PROFILES
        }

    def sample_manifest(self):
        return {
            "schema": 1, "kind": target.KIND, "minecraft": "26.2",
            "protocol": 776, "data_version": 4903,
            "source_archive_sha256": original.SOURCE_SHA256,
            "official_server_sha256": original.SERVER_SHA256,
            "frontier_sha256": target.stock.FRONTIER_SHA256,
            "original_stock_fixture_sha256": original.FIXTURE_SHA256,
            "heldout_stock_fixture_sha256": target.heldout_fixture.FIXTURE_SHA256,
            "source_methods": self.methods(),
            "delegates": self.delegates(),
            "profiles": list(target.PROFILES),
            "world_seeds": list(target.SEEDS),
            "noise_keys": list(target.KEYS),
            "points": [list(p) for p in target.POINTS],
            "xz_scale_bits": "0x3fd0000000000000",
            "y_scale_bits": "0x3fe0000000000000",
            "stock_registry_used": True,
            "world_seed_random_state_observed": True,
            "world_seed_random_state_bound": False,
            "source_text_included": False,
            "independent_var_sem_admitted": False,
            "production_worldgen_enabled": False,
            "vectors": [dict(row, value_bits="0x3ff0000000000000")
                        for row in target.inputs()],
        }

    def check(self, data):
        target.validate(data, source_sha=original.SOURCE_SHA256,
                        server_sha=original.SERVER_SHA256,
                        methods=self.methods(), delegates=self.delegates())

    def test_request_grid_is_exact_nonduplicated_and_zero_gradient_discriminating(self):
        rows = target.inputs()
        self.assertEqual(len(rows), 1920)
        self.assertEqual(len({tuple(row.values()) for row in rows}), 1920)
        self.assertEqual(len(target.SEEDS), 4)
        self.assertEqual(len(target.PROFILES), 10)
        self.assertEqual(len(target.KEYS), 3)
        self.assertIn((0, 128, 0), target.POINTS)
        self.assertEqual(
            rows[0], {"profile": target.PROFILES[0],
                      "world_seed_bits": target.SEEDS[0],
                      "noise_key": target.KEYS[0],
                      "block_x": 0, "block_y": 128, "block_z": 0})
        self.check(self.sample_manifest())

    def test_strict_1920_schema_order_source_and_unadmitted_gate_mutations(self):
        changes = [
            lambda a: a["vectors"].pop(),
            lambda a: a["vectors"].reverse(),
            lambda a: a["vectors"][0].__setitem__("profile", "unapproved"),
            lambda a: a["vectors"][0].__setitem__("block_y", 0),
            lambda a: a["vectors"][0].__setitem__("value_bits", "NaN"),
            lambda a: a["vectors"][0].__setitem__("noise_key", "UNKNOWN"),
            lambda a: a["profiles"].reverse(),
            lambda a: a["noise_keys"].reverse(),
            lambda a: a["points"].reverse(),
            lambda a: a.__setitem__("source_archive_sha256", "bad"),
            lambda a: a.__setitem__("heldout_stock_fixture_sha256", "bad"),
            lambda a: a.__setitem__("source_methods", {}),
            lambda a: a.__setitem__("delegates", {}),
            lambda a: a.__setitem__("xz_scale_bits", "0x3ff0000000000000"),
            lambda a: a.__setitem__("world_seed_random_state_bound", True),
            lambda a: a.__setitem__("independent_var_sem_admitted", True),
            lambda a: a.__setitem__("production_worldgen_enabled", True),
            lambda a: a.__setitem__("source_text_included", True),
        ]
        for change in changes:
            with self.subTest(change=str(change)):
                payload = self.sample_manifest()
                change(payload)
                with self.assertRaises(target.MixedDensityCaptureError):
                    self.check(payload)

    def test_tagged_parser_preserves_signed_zero_delegates_and_strict_indices(self):
        delegates = [
            target.DELEGATE_PREFIX+p+
            "|net.minecraft.world.level.levelgen.DensityFunctions$Ap2"
            "|net.minecraft.world.level.levelgen.DensityFunctions$Ap2|java.lang.Object"
            for p in target.PROFILES
        ]
        values = [
            target.BIT_PREFIX+str(i)+"|"+("8000000000000000" if i==0
                                           else f"{i:016x}")
            for i in range(1920)
        ]
        bits, classes = target.parse_output("\n".join(["[INFO] bootstrap", *delegates, *values]))
        self.assertEqual(len(bits), 1920)
        self.assertEqual(bits[0], "0x8000000000000000")
        self.assertEqual(bits[-1], "0x000000000000077f")
        self.assertEqual(len(classes), 10)
        for corrupted in (
            values[:-1], values + values[:1],
            [values[1], values[0]] + values[2:],
            [values[0], values[0]] + values[2:],
            [values[0].replace("8000000000000000", "not-hex")] + values[1:],
        ):
            with self.subTest(length=len(corrupted)):
                with self.assertRaises(target.MixedDensityCaptureError):
                    target.parse_output("\n".join([*delegates, *corrupted]))
        with self.assertRaisesRegex(target.MixedDensityCaptureError, "JVM PHASE"):
            target.parse_output(target.FAILURE_PREFIX +
                                "stock-registry-createLookup|java.lang.IllegalStateException"
                                "|java.lang.reflect.InvocationTargetException|bad registry")

    def test_stock_primitives_factories_are_source_pinned_not_inferred(self):
        fake = self.methods()["composition_factories"]
        with mock.patch.object(target.stock, "source_methods",
                               return_value=self.methods()["worldseed_noise"]), \
             mock.patch.object(target.primitive, "bound_methods",
                               return_value=self.methods()["density_primitives"]), \
             mock.patch.object(target.composed, "bound_composition_methods",
                               return_value=fake):
            result = target.source_method_inventory({}, object())
            self.assertEqual(result["composition_factories"], fake)
            wrong = {**fake, "add_factory": {**fake["add_factory"], "body_sha256": "0"*64}}
            with mock.patch.object(target.composed, "bound_composition_methods",
                                   return_value=wrong):
                with self.assertRaises(target.MixedDensityCaptureError):
                    target.source_method_inventory({}, object())

    def test_mocked_capture_only_writes_external_exclusive_no_production_admission(self):
        with tempfile.TemporaryDirectory() as name:
            base = Path(name)
            pin = base/"lock.toml"
            pin.write_text(
                'minecraft="26.2"\nprotocol=776\ndata_version=4903\n'
                '[runtime]\nserver_sha256="' + original.SERVER_SHA256 + '"\n')
            outfile = base/"mix.json"
            with mock.patch.object(target.stock, "reference_frontier", return_value={}), \
                 mock.patch.object(target.vanilla_atlas, "connect_db") as db, \
                 mock.patch.object(target.source_probe, "require_pinned_source",
                                   return_value=original.SOURCE_SHA256), \
                 mock.patch.object(target, "source_method_inventory",
                                   return_value=self.methods()), \
                 mock.patch.object(target.official, "sha256_file",
                                   return_value=original.SERVER_SHA256), \
                 mock.patch.object(target, "observe",
                                   return_value=(["0x3ff0000000000000"]*1920,
                                                 self.delegates())):
                summary = target.capture(
                    source=base/"source.zip", db=base/"atlas.db", lock=pin,
                    server=base/"official.jar", frontier=base/"frontier.json",
                    output=outfile)
                self.assertEqual(summary["vectors"], 1920)
                self.assertFalse(summary["rust_mixed_semantics_qualified"])
                self.assertFalse(summary["independent_var_sem_admitted"])
                self.assertTrue(db.return_value.close.called)
                result = json.loads(outfile.read_text())
                self.check(result)
                with self.assertRaises(ValueError):
                    target.capture(source=base/"source.zip", db=base/"atlas.db", lock=pin,
                                   server=base/"official.jar", frontier=base/"frontier.json",
                                   output=outfile)

    @unittest.skipUnless(shutil.which("javac") and shutil.which("java"),
                         "Java toolchain required for original bridge synthetic end-to-end")
    def test_actual_java_bridge_with_stock_provider_and_delegate_class_observation(self):
        with tempfile.TemporaryDirectory(prefix="helve-stock-mixed-toy-") as folder:
            work = Path(folder)
            root = work/"src"
            def file(package, name, text):
                target_path=root/package.replace(".","/")/(name+".java")
                target_path.parent.mkdir(parents=True,exist_ok=True)
                target_path.write_text("package "+package+";\n"+text+"\n")

            file("net.minecraft","SharedConstants",
                 "public class SharedConstants {"
                 "public static void tryDetectVersion() {} }")
            file("net.minecraft.server","Bootstrap",
                 "public class Bootstrap { public static void bootStrap(){"
                 "System.setOut(new java.io.PrintStream(new java.io.ByteArrayOutputStream()));}}")
            file("net.minecraft.resources","ResourceKey",
                 "public record ResourceKey(String name) {}")
            file("net.minecraft.core","Holder",
                 "public interface Holder { class Reference implements Holder {} }")
            file("net.minecraft.core","HolderGetter",
                 "public interface HolderGetter {"
                 "Holder.Reference getOrThrow(net.minecraft.resources.ResourceKey key);"
                 "interface Provider {HolderGetter lookupOrThrow("
                 "net.minecraft.resources.ResourceKey registry);}}")
            file("net.minecraft.core","HolderLookup",
                 "public interface HolderLookup {"
                 "interface Provider extends HolderGetter.Provider {} }")
            file("net.minecraft.core.registries","Registries",
                 "public class Registries { public static final"
                 " net.minecraft.resources.ResourceKey NOISE="
                 "new net.minecraft.resources.ResourceKey(\"NOISE\"); }")
            file("net.minecraft.data.registries","VanillaRegistries",
                 "public class VanillaRegistries {"
                 "public static net.minecraft.core.HolderLookup.Provider createLookup(){"
                 "return registry -> { if (!registry.equals("
                 "net.minecraft.core.registries.Registries.NOISE))"
                 "throw new IllegalArgumentException(\"wrong registry\");"
                 "return key -> {if (!java.util.Set.of(\"TEMPERATURE\","
                 "\"CONTINENTALNESS\",\"EROSION\").contains(key.name()))"
                 "throw new IllegalArgumentException(\"unknown key\");"
                 "return new net.minecraft.core.Holder.Reference();};};}}")
            level="net.minecraft.world.level.levelgen"
            file(level,"NoiseGeneratorSettings",
                 "public class NoiseGeneratorSettings {"
                 "public static final net.minecraft.resources.ResourceKey OVERWORLD="
                 "new net.minecraft.resources.ResourceKey(\"OVERWORLD\");}")
            file(level,"Noises",
                 "public class Noises {"
                 "public static final net.minecraft.resources.ResourceKey TEMPERATURE="
                 "new net.minecraft.resources.ResourceKey(\"TEMPERATURE\");"
                 "public static final net.minecraft.resources.ResourceKey CONTINENTALNESS="
                 "new net.minecraft.resources.ResourceKey(\"CONTINENTALNESS\");"
                 "public static final net.minecraft.resources.ResourceKey EROSION="
                 "new net.minecraft.resources.ResourceKey(\"EROSION\");}")
            file(level+".synth","NormalNoise",
                 "public record NormalNoise(double bias) {"
                 "public double getValue(double x,double y,double z){"
                 "return bias+x*0.125+y*0.25+z*0.5;}}")
            file(level,"RandomState",
                 "public record RandomState(long seed) {"
                 "public static RandomState create(net.minecraft.core.HolderGetter.Provider provider,"
                 "net.minecraft.resources.ResourceKey settings,long seed) {"
                 "if(!settings.equals(NoiseGeneratorSettings.OVERWORLD))"
                 "throw new IllegalArgumentException(\"not OVERWORLD\");"
                 "return new RandomState(seed);}"
                 "public net.minecraft.world.level.levelgen.synth.NormalNoise getOrCreateNoise("
                 "net.minecraft.resources.ResourceKey key) {"
                 "return new net.minecraft.world.level.levelgen.synth.NormalNoise("
                 "(seed%1009)+key.name().length());}}")
            file(level,"DensityFunction",
                 "public interface DensityFunction {"
                 "double compute(FunctionContext pos);"
                 "interface FunctionContext {int blockX();int blockY();int blockZ();}"
                 "record SinglePointContext(int blockX,int blockY,int blockZ)"
                 "implements FunctionContext {}"
                 "record NoiseHolder(net.minecraft.core.Holder holder,"
                 "net.minecraft.world.level.levelgen.synth.NormalNoise noise) {} }")
            file(level,"DensityFunctions",
                 "public class DensityFunctions {"
                 "public record Noise(DensityFunction.NoiseHolder held,"
                 "double xz,double y) implements DensityFunction {"
                 "public double compute(DensityFunction.FunctionContext pos){"
                 "return held.noise().getValue(pos.blockX()*xz,"
                 "pos.blockY()*y,pos.blockZ()*xz);}}"
                 "public record Constant(double v) implements DensityFunction {"
                 "public double compute(DensityFunction.FunctionContext pos){return v;}}"
                 "public record Gradient(int lo,int hi,double a,double b)"
                 "implements DensityFunction {"
                 "public double compute(DensityFunction.FunctionContext pos){"
                 "double t=Math.max(0.0,Math.min(1.0,"
                 "(double)(pos.blockY()-lo)/(hi-lo)));return a+t*(b-a);}}"
                 "public record Ap2(DensityFunction l,DensityFunction r,boolean mul)"
                 "implements DensityFunction {"
                 "public double compute(DensityFunction.FunctionContext pos){"
                 "double x=l.compute(pos);if(mul && Double.doubleToRawLongBits(x)==0L)"
                 "return 0.0;return mul?x*r.compute(pos):x+r.compute(pos);}}"
                 "public static DensityFunction constant(double value){return new Constant(value);}"
                 "public static DensityFunction yClampedGradient("
                 "int lo,int hi,double a,double b){return new Gradient(lo,hi,a,b);}"
                 "public static DensityFunction add(DensityFunction x,DensityFunction y){"
                 "return new Ap2(x,y,false);}"
                 "public static DensityFunction mul(DensityFunction x,DensityFunction y){"
                 "return new Ap2(x,y,true);}"
                 "}")
            classes=work/"out"
            built=subprocess.run(
                ["javac","-encoding","UTF-8","-d",str(classes),
                 *[str(p) for p in root.rglob("*.java")]],
                capture_output=True,text=True,check=False,timeout=45)
            self.assertEqual(built.returncode,0,built.stderr)
            with mock.patch.object(target.official, "extract_classpath",
                                   return_value=[classes]):
                words, metadata=target.observe(work/"toy.jar",target.inputs(),timeout=90)
            self.assertEqual(len(words),1920)
            self.assertEqual(len(metadata),10)
            self.assertEqual(
                metadata["mul_gradient_noise"]["implementation_class"],
                "net.minecraft.world.level.levelgen.DensityFunctions$Ap2")
            # The toy is independent and deliberately models a +0 early return
            # for the gradient-first multiply profile at block Y=128.
            for key_index in range(3):
                row=((target.PROFILES.index("mul_gradient_noise")*4)*3+key_index)*16
                self.assertEqual(words[row],"0x0000000000000000")
            self.assertNotEqual(words[0],words[16])


if __name__=="__main__":
    unittest.main()
