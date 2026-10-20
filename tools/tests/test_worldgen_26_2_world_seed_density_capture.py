"""Fail-closed 26.2 stock-registry RandomState/Noise.compute collector tests."""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
import tomllib
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import worldgen_26_2_world_seed_density_capture as target  # noqa: E402


class StockWorldSeedDensityTests(unittest.TestCase):
    @staticmethod
    def lock():
        return {
            "minecraft": "26.2", "protocol": 776, "data_version": 4903,
            "source": {"archive_sha256": "a" * 64},
            "runtime": {"server_sha256": "b" * 64},
        }

    @staticmethod
    def reference():
        data = {"source_atlas": {}, "runtime_reflection": {}}
        for _, (owner, method, args, digest) in target.SOURCE_PINS.items():
            data["source_atlas"].setdefault(owner, {"methods": []})["methods"].append({
                "signature": method + "(" + ", ".join(
                    "final " + x + " arg" for x in args) + ")",
                "body_sha256": digest,
                "normalized_sha256": "c" * 64,
            })
        return data

    def methods(self):
        result = {}
        for label, (owner, name, types, digest) in target.SOURCE_PINS.items():
            matches = [
                row for row in self.reference()["source_atlas"][owner]["methods"]
                if target.binding.match_args(row["signature"], name, types)
            ]
            self.assertEqual(len(matches), 1)
            result[label] = {
                "owner": owner, "signature": matches[0]["signature"],
                "body_sha256": digest, "normalized_sha256": "c" * 64,
            }
        result["stock_vanilla_lookup"] = {
            "owner": target.VANILLA_REGISTRIES, "signature": "createLookup()",
            "body_sha256": "d" * 64, "normalized_sha256": "e" * 64,
        }
        return result

    def report(self):
        return {
            "schema": 1, "kind": target.KIND, "stage": target.STAGE,
            "minecraft": "26.2", "protocol": 776, "data_version": 4903,
            "source_archive_sha256": "a" * 64,
            "official_server_sha256": "b" * 64,
            "frontier_sha256": target.FRONTIER_SHA256,
            "source_methods": self.methods(),
            "profiles": target.PROFILES.copy(),
            "world_seeds": list(target.SEEDS), "noise_keys": list(target.NOISE_KEYS),
            "world_seed_random_state_observed": True, "stock_registry_used": True,
            "world_seed_random_state_bound": False,
            "source_text_included": False, "independent_var_sem_admitted": False,
            "production_worldgen_enabled": False,
            "vectors": [
                dict(row, value_bits="0x8000000000000000")
                for row in target.input_rows()
            ],
        }

    def test_exact_stock_noise_seeds_keys_coordinates_and_schema(self):
        points = target.input_rows()
        self.assertEqual(len(points), 1440)
        self.assertEqual(len({tuple(sorted(v.items())) for v in points}), 1440)
        self.assertEqual({row["noise_key"] for row in points}, set(target.NOISE_KEYS))
        target.validate(self.report(), self.lock(), self.reference())

    def test_no_bypass_of_stock_registry_or_worldseed_admission(self):
        edits = [
            lambda x: x.__setitem__("source_text_included", True),
            lambda x: x.__setitem__("world_seed_random_state_bound", True),
            lambda x: x.__setitem__("independent_var_sem_admitted", True),
            lambda x: x.__setitem__("production_worldgen_enabled", True),
            lambda x: x.__setitem__("stock_registry_used", False),
            lambda x: x.__setitem__("world_seed_random_state_observed", False),
            lambda x: x.__setitem__("frontier_sha256", "f" * 64),
            lambda x: x.__setitem__("source_java", "private"),
            lambda x: x["source_methods"]["noises_instantiate"].__setitem__(
                "body_sha256", "a" * 64),
            lambda x: x["source_methods"]["stock_vanilla_lookup"].__setitem__(
                "signature", "createFakeLookup()"),
            lambda x: x["world_seeds"].reverse(),
            lambda x: x["noise_keys"].reverse(),
            lambda x: x["profiles"].pop("unit"),
            lambda x: x["vectors"].pop(),
            lambda x: x["vectors"][0].__setitem__("block_x", 17),
            lambda x: x["vectors"][1].__setitem__("noise_key", "FAKE"),
            lambda x: x["vectors"][2].__setitem__("value_bits", "NaN"),
            lambda x: x["vectors"][3].__setitem__("world_seed_bits", "0x1"),
        ]
        for change in edits:
            with self.subTest(change=str(change)):
                data = self.report()
                change(data)
                with self.assertRaises(target.WorldSeedNoiseError):
                    target.validate(data, self.lock(), self.reference())

    def test_tagged_transport_count_order_and_ieee_sign_preservation(self):
        lines = [f"{target.PREFIX}{i}|{i:016x}" for i in range(1440)]
        observed = target.parse_bits("[INFO] boot\n" + "\n[INFO] step\n".join(lines))
        self.assertEqual(observed, [f"0x{i:016x}" for i in range(1440)])
        for altered in (
            lines[:-1], lines + lines[:1], [lines[1], lines[0]] + lines[2:],
            [lines[0], lines[0]] + lines[2:],
            [line.replace(target.PREFIX, "FAKE|") for line in lines],
            [lines[0].replace("|0000000000000000", "|not-hex")] + lines[1:],
        ):
            with self.assertRaises(target.WorldSeedNoiseError):
                target.parse_bits("\n".join(altered))

    def test_invalid_or_substituted_frontier_sha_fails_before_probe(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "altered-frontier.json"
            path.write_text(json.dumps({"stage": target.STAGE}))
            with self.assertRaisesRegex(target.WorldSeedNoiseError, "SHA changed"):
                target.reference_frontier(path, self.lock())

    def test_vanilla_lookup_and_five_real_pinned_source_method_identities(self):
        ref = self.reference()
        with mock.patch.object(target.projection, "_exact_type_methods",
                               return_value=[{
                                   "name": "createLookup", "signature": "createLookup()",
                                   "id": 2}]), \
             mock.patch.object(target.source_probe, "record_template",
                               return_value={"source": {
                                   "type": target.VANILLA_REGISTRIES,
                                   "signature": "createLookup()",
                                   "body_sha256": "d" * 64,
                                   "normalized_sha256": "e" * 64}}):
            self.assertEqual(target.source_methods(ref, object()), self.methods())

    def test_mocked_capture_is_exclusive_and_refuses_promoting_captured_seed_law(self):
        with tempfile.TemporaryDirectory() as temp:
            home = Path(temp)
            lock = home / "vanilla.toml"
            lock.write_text(
                'minecraft="26.2"\nprotocol=776\ndata_version=4903\n'
                '[source]\narchive_sha256="' + "a" * 64 + '"\n'
                '[runtime]\nserver_sha256="' + "b" * 64 + '"\n')
            output = home / "source-free.json"
            with mock.patch.object(target, "reference_frontier",
                                   return_value=self.reference()), \
                 mock.patch.object(target.vanilla_atlas, "connect_db") as db, \
                 mock.patch.object(target.source_probe, "require_pinned_source",
                                   return_value="a" * 64), \
                 mock.patch.object(target, "source_methods",
                                   return_value=self.methods()), \
                 mock.patch.object(target.official, "sha256_file",
                                   return_value="b" * 64), \
                 mock.patch.object(target, "oracle",
                                   return_value=["0x8000000000000000"] * 1440):
                observed = target.capture(source=home/"src.zip",db=home/"atlas",
                    lock=lock,server=home/"jar",frontier=home/"frontier",output=output)
                self.assertEqual(observed["vectors"],1440)
                data = json.loads(output.read_text())
                target.validate(data,tomllib.loads(lock.read_text()),self.reference())
                self.assertFalse(data["world_seed_random_state_bound"])
                self.assertTrue(db.return_value.close.called)
                with self.assertRaises(ValueError):
                    target.capture(source=home/"src.zip",db=home/"atlas",
                        lock=lock,server=home/"jar",frontier=home/"frontier",output=output)

    def test_raw_stdout_jvm_failure_tag_is_single_bounded_and_fail_closed(self):
        tag = target.FAILURE_TAG
        event = (
            tag + "stock-registry-createLookup|java.lang.NoSuchMethodException|"
            "java.lang.reflect.InvocationTargetException|"
            "net.minecraft.data.registries.VanillaRegistries.createLookup()"
        )
        expected = target.java_probe_failure("[INFO] boot\n" + event + "\n")
        self.assertIn("JVM PHASE: stock-registry-createLookup", expected)
        self.assertIn("ROOT CAUSE: java.lang.NoSuchMethodException", expected)
        self.assertIn("VanillaRegistries.createLookup()", expected)
        for corrupted in (event + "\n" + event,
                          tag + "bad|unexpected|row",
                          tag + "stock-registry-createLookup|java.lang.Error|"
                                "java.lang.Error|bad|extra",
                          tag + "stock-registry-createLookup|java.lang.Error|"
                                "java.lang.Error|bad" + chr(0) + "message"):
            with self.subTest(corrupted=repr(corrupted)[:55]):
                with self.assertRaises(target.WorldSeedNoiseError):
                    target.java_probe_failure(corrupted)
        self.assertIsNone(target.java_probe_failure("unrelated bootstrap output"))

    def test_raw_stdout_jvm_error_takes_priority_over_broken_stderr(self):
        error = (
            target.FAILURE_TAG
            + "noise-registry-lookup|java.lang.IllegalStateException|"
            "java.lang.reflect.InvocationTargetException|unbound stock noise registry"
        )
        with mock.patch.object(target.official, "extract_classpath", return_value=[]), \
             mock.patch.object(target.subprocess, "run", side_effect=[
                 subprocess.CompletedProcess(["javac"], 0, "", ""),
                 subprocess.CompletedProcess(["java"], 2, error + "\n",
                                             'Exception in thread "main"\n'),
             ]):
            with self.assertRaises(target.WorldSeedNoiseError) as caught:
                target.oracle(Path("/tmp/official-runtime.jar"), target.input_rows())
        self.assertIn("JVM PHASE: noise-registry-lookup", str(caught.exception))
        self.assertIn("unbound stock noise registry", str(caught.exception))
        self.assertNotIn('Exception in thread "main"', str(caught.exception))

    def test_java_exception_is_not_hidden_by_terminally_deprecated_joml_warnings(self):
        warnings = (
            "WARNING: A terminally deprecated method in sun.misc.Unsafe has been called\n"
            "WARNING: sun.misc.Unsafe::objectFieldOffset has been called by org.joml.MemUtil\n"
            + "WARNING: Please consider reporting this to the maintainers\n" * 20
        )
        exception = (
            'Exception in thread "main" java.lang.reflect.InvocationTargetException\n'
            "    at java.base/java.lang.reflect.Method.invoke(Method.java:578)\n"
            "Caused by: java.lang.NoSuchMethodException: example.StockLookup()\n"
            "    at java.base/java.lang.Class.getMethod(Class.java:2417)\n"
        )
        detail = target.java_failure_detail(warnings + exception)
        self.assertTrue(detail.startswith("JVM ROOT CAUSE: java.lang.NoSuchMethodException: example.StockLookup()"))
        self.assertIn("NoSuchMethodException", detail)
        self.assertNotIn("terminally deprecated", detail)
        self.assertEqual(
            target.java_failure_detail("Error: Could not find or load main class").splitlines()[0],
            "JVM ROOT CAUSE: Error: Could not find or load main class",
        )

        # A deliberately long reflective invocation stack must still retain
        # both the initial JVM exception AND the deepest root cause.
        deep = (
            'Exception in thread "main" java.lang.reflect.InvocationTargetException\n'
            + "    at example.Stack.method(Stack.java:10)\n" * 600
            + "Caused by: java.lang.IllegalStateException: stock registry unavailable\n"
        )
        short = target.java_failure_detail(warnings + deep)
        self.assertLessEqual(len(short), 6000)
        self.assertIn("InvocationTargetException", short)
        self.assertIn("stock registry unavailable", short.splitlines()[0])
        self.assertIn("InvocationTargetException", short.splitlines()[0])
        self.assertIn("intermediate JVM frames omitted", short)
        self.assertNotIn("sun.misc.Unsafe", short)

    def test_oracle_failure_reports_actual_exception_not_jvm_warning_preface(self):
        warnings = "WARNING: sun.misc.Unsafe is terminally deprecated\n" * 60
        error = (
            'Exception in thread "main" java.lang.NoSuchMethodException: '
            'net.minecraft.data.registries.VanillaRegistries.createLookup()\n'
            "    at java.base/java.lang.Class.getMethod(Class.java:2417)\n"
        )
        with mock.patch.object(target.official, "extract_classpath", return_value=[]), \
             mock.patch.object(target.subprocess, "run", side_effect=[
                 subprocess.CompletedProcess(["javac"], 0, "", ""),
                 subprocess.CompletedProcess(["java"], 1, "", warnings + error),
             ]):
            with self.assertRaises(target.WorldSeedNoiseError) as failed:
                target.oracle(Path("/tmp/official-runtime.jar"), target.input_rows())
        diagnostic = str(failed.exception)
        self.assertIn("VanillaRegistries.createLookup()", diagnostic.splitlines()[0])
        self.assertTrue(diagnostic.startswith("real stock-registry 26.2 world-seed JVM path is NOT VERIFIED (no tagged Java error): JVM ROOT CAUSE:"))
        self.assertNotIn("terminally deprecated", diagnostic)

    @unittest.skipUnless(shutil.which("javac") and shutil.which("java"),
                         "Java toolchain required to check full original synthetic bridge")
    def test_original_jvm_bridge_uses_real_stock_lookup_not_manual_holder(self):
        with tempfile.TemporaryDirectory() as temp:
            work = Path(temp)
            src = work / "src"
            def file(package, name, body):
                dst = src / package.replace(".","/") / (name + ".java")
                dst.parent.mkdir(parents=True,exist_ok=True)
                dst.write_text("package " + package + ";\n" + body + "\n")

            file("net.minecraft","SharedConstants",
                 "public class SharedConstants { static boolean ready;"
                 " public static void tryDetectVersion(){ready=true;} }")
            file("net.minecraft.server","Bootstrap",
                 "public class Bootstrap {public static void bootStrap(){"
                 "net.minecraft.SharedConstants.tryDetectVersion();"
                 "System.setOut(new java.io.PrintStream(new java.io.ByteArrayOutputStream()));}}")
            file("net.minecraft.resources","ResourceKey",
                 "public record ResourceKey(String name) {}")
            file("net.minecraft.core","Holder",
                 "public interface Holder { public static class Reference implements Holder {} }")
            file("net.minecraft.core","HolderGetter",
                 "public interface HolderGetter {"
                 "Holder.Reference getOrThrow(net.minecraft.resources.ResourceKey k);"
                 "interface Provider {HolderGetter lookupOrThrow(net.minecraft.resources.ResourceKey key);}}")
            file("net.minecraft.core","HolderLookup",
                 "public interface HolderLookup {"
                 "interface Provider extends HolderGetter.Provider {}}")
            file("net.minecraft.core.registries","Registries",
                 "public class Registries {public static final net.minecraft.resources.ResourceKey"
                 " NOISE=new net.minecraft.resources.ResourceKey(\"NOISE\");}")
            file("net.minecraft.data.registries","VanillaRegistries",
                 "public class VanillaRegistries {"
                 "public static net.minecraft.core.HolderLookup.Provider createLookup(){"
                 "return () -> registry -> {"
                 "if (!registry.equals(net.minecraft.core.registries.Registries.NOISE))"
                 " throw new IllegalArgumentException(\"not real noise registry\");"
                 "return key -> {if(!java.util.Set.of(\"TEMPERATURE\",\"EROSION\","
                 "\"CONTINENTALNESS\").contains(key.name()))"
                 " throw new IllegalArgumentException(\"unknown registered key\");"
                 "return new net.minecraft.core.Holder.Reference();};};}}")
            root="net.minecraft.world.level.levelgen"
            file(root,"NoiseGeneratorSettings","public class NoiseGeneratorSettings {"
                 "public static final net.minecraft.resources.ResourceKey OVERWORLD="
                 "new net.minecraft.resources.ResourceKey(\"OVERWORLD\");}")
            file(root,"Noises","public class Noises {"
                 "public static final net.minecraft.resources.ResourceKey TEMPERATURE="
                 "new net.minecraft.resources.ResourceKey(\"TEMPERATURE\");"
                 "public static final net.minecraft.resources.ResourceKey CONTINENTALNESS="
                 "new net.minecraft.resources.ResourceKey(\"CONTINENTALNESS\");"
                 "public static final net.minecraft.resources.ResourceKey EROSION="
                 "new net.minecraft.resources.ResourceKey(\"EROSION\");}")
            file(root+".synth","NormalNoise","public record NormalNoise(double bias) {"
                 "public double getValue(double x,double y,double z){"
                 "return bias+x*0.125+y*0.25+z*0.5;}}")
            file(root,"RandomState",
                 "public record RandomState(long seed) {"
                 "public static RandomState create(net.minecraft.core.HolderGetter.Provider lookup,"
                 "net.minecraft.resources.ResourceKey settings,long seed){"
                 "if(!settings.equals(NoiseGeneratorSettings.OVERWORLD))"
                 "throw new IllegalArgumentException(\"not overworld\");"
                 "return new RandomState(seed);}"
                 "public net.minecraft.world.level.levelgen.synth.NormalNoise getOrCreateNoise("
                 "net.minecraft.resources.ResourceKey key){"
                 "return new net.minecraft.world.level.levelgen.synth.NormalNoise("
                 "(seed % 1009) + key.name().length());}}")
            file(root,"DensityFunction","public interface DensityFunction {"
                 "interface FunctionContext {int blockX();int blockY();int blockZ();}"
                 "record SinglePointContext(int blockX,int blockY,int blockZ)"
                 " implements FunctionContext {}"
                 "record NoiseHolder(net.minecraft.core.Holder holder,"
                 "net.minecraft.world.level.levelgen.synth.NormalNoise noise) {} }")
            file(root,"DensityFunctions","public class DensityFunctions {"
                 "public record Noise(DensityFunction.NoiseHolder held,"
                 "double xz,double y) {"
                 "public double compute(DensityFunction.FunctionContext pos){"
                 "return held.noise().getValue(pos.blockX()*xz,"
                 "pos.blockY()*y,pos.blockZ()*xz);}}}")

            output = work / "out"
            compiled=subprocess.run(
                ["javac","-encoding","UTF-8","-d",str(output),
                 *[str(p) for p in src.rglob("*.java")]],
                capture_output=True,text=True,timeout=30)
            self.assertEqual(compiled.returncode,0,compiled.stderr)
            with mock.patch.object(target.official,"extract_classpath",
                                   return_value=[output]):
                observed=target.oracle(work/"fake.jar",target.input_rows(),timeout=60)
            self.assertEqual(len(observed),1440)
            self.assertTrue(all(target.BITS.fullmatch(word) for word in observed))
            self.assertNotEqual(observed[0],observed[32])
            self.assertNotEqual(observed[0],observed[96])
            self.assertNotEqual(observed[0],observed[288])

            # Negative experiment with a REAL compiled independent toy JVM.
            # Its Bootstrap replaces System.out, its registry method throws,
            # and default System.err may be incomplete. The original bridge
            # must emit the typed ROOT CAUSE via FileDescriptor.out.
            file("net.minecraft.data.registries", "VanillaRegistries",
                 "public class VanillaRegistries {"
                 "public static net.minecraft.core.HolderLookup.Provider createLookup(){"
                 "throw new IllegalStateException(\"missing authentic noise registry\");}}")
            changed=subprocess.run(
                ["javac","-encoding","UTF-8","-d",str(output),
                 *[str(p) for p in src.rglob("*.java")]],
                capture_output=True,text=True,timeout=30)
            self.assertEqual(changed.returncode, 0, changed.stderr)
            with mock.patch.object(target.official, "extract_classpath",
                                   return_value=[output]):
                with self.assertRaises(target.WorldSeedNoiseError) as failed:
                    target.oracle(work/"fake.jar",target.input_rows(),timeout=60)
            detail = str(failed.exception)
            self.assertIn("JVM PHASE: stock-registry-createLookup", detail)
            self.assertIn("ROOT CAUSE: java.lang.IllegalStateException", detail)
            self.assertIn("missing authentic noise registry", detail)

            # Negative: a provider with the OLD unrelated interface shape
            # must be rejected, not wrapped or treated as a valid getter.
            file("net.minecraft.core", "HolderLookup",
                 "public interface HolderLookup {"
                 "interface Provider {String marker();}}")
            file("net.minecraft.data.registries", "VanillaRegistries",
                 "public class VanillaRegistries {"
                 "public static net.minecraft.core.HolderLookup.Provider createLookup(){"
                 "return () -> \"wrong interface relationship\";}}")
            bad_provider=subprocess.run(
                ["javac", "-encoding", "UTF-8", "-d", str(output),
                 *[str(p) for p in src.rglob("*.java")]],
                capture_output=True,text=True,timeout=30)
            self.assertEqual(bad_provider.returncode,0,bad_provider.stderr)
            with mock.patch.object(target.official, "extract_classpath",
                                   return_value=[output]):
                with self.assertRaises(target.WorldSeedNoiseError) as failed_provider:
                    target.oracle(work/"fake.jar",target.input_rows(),timeout=60)
            self.assertIn("JVM PHASE: stock-registry-provider-subtype",
                          str(failed_provider.exception))
            self.assertIn("ROOT CAUSE: java.lang.IllegalStateException",
                          str(failed_provider.exception))
            self.assertIn("not a HolderGetter.Provider",
                          str(failed_provider.exception))


if __name__=="__main__":
    unittest.main()
