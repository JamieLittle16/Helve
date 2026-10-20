"""Fail-closed 26.2 official RandomState and registry shape frontier.

No actual Minecraft code or distribution of any private source is used in
the synthetic JVM test. This probes only signatures and schema boundaries.
"""
from __future__ import annotations

import copy
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
import worldgen_26_2_random_state_binding_frontier as target  # noqa: E402


class RandomStateBindingTests(unittest.TestCase):
    @staticmethod
    def lock():
        return {
            "minecraft": "26.2", "protocol": 776, "data_version": 4903,
            "source": {"archive_sha256": "a" * 64},
            "runtime": {"server_sha256": "b" * 64},
        }

    @staticmethod
    def atlas():
        values = {
            key: {"status": "indexed_not_reviewed", "methods": []}
            for key in target.TYPES
        }
        for owner, name, kinds, digest in target.BODY_PINS.values():
            signature = (
                name + "(" + ", ".join("final " + kind + " argument"
                for kind in kinds) + ")"
            )
            values[owner]["methods"].append({
                "name": name, "signature": signature,
                "body_sha256": digest, "normalized_sha256": "c" * 64,
                "call_sites": 3, "unresolved_call_sites": 1,
                "reviewed": False,
            })
        return values

    @staticmethod
    def runtime():
        rows = []
        for index, name in enumerate(target.TYPES):
            rows.append(f"{target.TAG}|{index}|TYPE|{name}|present")
            members = []
            if index == 0:
                members = [
                    ("METHOD", "create", name, "static",
                     target.TYPES[1] + "," + target.TYPES[8] + ",long"),
                    ("METHOD", "getOrCreateNoise", "java.lang.Object",
                     "instance", "net.minecraft.resources.ResourceKey"),
                ]
            elif index == 3:
                members = [("METHOD", "mapAll", name, "instance",
                            "net.minecraft.world.level.levelgen.DensityFunction$Visitor")]
            for row in sorted("|".join(parts) for parts in members):
                rows.append(f"{target.TAG}|{index}|{row}")
        return target.parse_runtime("\n".join(rows))

    def manifest(self):
        return {
            "schema": 1, "kind": target.KIND, "stage": target.STAGE,
            "minecraft": "26.2", "protocol": 776, "data_version": 4903,
            "source_archive_sha256": "a" * 64,
            "official_server_sha256": "b" * 64,
            "startup": target.primitive.STARTUP_SEQUENCE.copy(),
            "source_atlas": self.atlas(),
            "runtime_reflection": self.runtime(),
            "source_text_included": False,
            "world_seed_random_state_bound": False,
            "independent_var_sem_admitted": False,
            "production_worldgen_enabled": False,
        }

    def test_three_pinned_source_methods_and_source_free_manifest(self):
        self.assertEqual(len(target.TYPES), 12)
        self.assertEqual(set(target.BODY_PINS),
                         {"state_create", "state_get_noise", "router_map"})
        target.validate(self.manifest(), self.lock())

    def test_atlas_callsite_counts_are_integers_not_lists(self):
        def fake_methods(_conn, owner, _limit):
            matches = [
                {"id": n, "name": name, "owner": owner,
                 "signature": name + "(" + ", ".join(
                     "final " + kind + " x" for kind in kinds) + ")",
                 "body": digest}
                for n, (_, name, kinds, digest) in
                enumerate(target.BODY_PINS.values(), start=1)
                if target.BODY_PINS[list(target.BODY_PINS)[n - 1]][0] == owner
            ]
            if not matches and owner in target.REQUIRED:
                matches.append({"id": 99, "name": "value", "owner": owner,
                                "signature": "value()", "body": "d" * 64})
            return matches

        def template(_conn, row, _candidate):
            return {"source": {
                "type": row["owner"], "signature": row["signature"],
                "body_sha256": row["body"], "normalized_sha256": "e" * 64,
            }}

        with mock.patch.object(target.projection, "_exact_type_methods",
                               side_effect=fake_methods), \
             mock.patch.object(target.source_probe, "record_template",
                               side_effect=template), \
             mock.patch.object(target.projection, "_call_inventory",
                               return_value={"call_sites": 3,
                                             "unresolved_call_sites": 1}):
            result = target.atlas_binding(object())
        self.assertEqual(result[target.TYPES[0]]["methods"][0]["call_sites"], 3)
        self.assertEqual(result[target.TYPES[0]]["methods"][0]["unresolved_call_sites"], 1)

    def test_fail_closed_source_runtime_gate_and_method_mutations(self):
        changes = [
            lambda v: v.__setitem__("source_text_included", True),
            lambda v: v.__setitem__("world_seed_random_state_bound", True),
            lambda v: v.__setitem__("independent_var_sem_admitted", True),
            lambda v: v.__setitem__("production_worldgen_enabled", True),
            lambda v: v.__setitem__("schema", 2),
            lambda v: v.__setitem__("source_java", "private"),
            lambda v: v["source_atlas"][target.TYPES[0]]["methods"][0].__setitem__(
                "body_sha256", "d" * 64),
            lambda v: v["source_atlas"][target.TYPES[0]]["methods"][0].__setitem__(
                "reviewed", True),
            lambda v: v["source_atlas"][target.TYPES[0]]["methods"][0].__setitem__(
                "unresolved_call_sites", 10),
            lambda v: v["source_atlas"][target.TYPES[3]]["methods"].clear(),
            lambda v: v["runtime_reflection"][target.TYPES[0]]["members"].clear(),
            lambda v: v["runtime_reflection"][target.TYPES[8]].__setitem__("status", "absent"),
            lambda v: v["runtime_reflection"][target.TYPES[3]]["members"][0].__setitem__(
                "erased_args", "java.lang.String"),
        ]
        for change in changes:
            with self.subTest(change=str(change)):
                report = self.manifest()
                change(report)
                with self.assertRaises(target.BindingFrontierError):
                    target.validate(report, self.lock())

    def test_reflection_tags_strict_order_class_ownership_and_bootstrap_logs(self):
        src = self.runtime()
        raw = []
        for index, owner in enumerate(target.TYPES):
            raw.append(f"{target.TAG}|{index}|TYPE|{owner}|present")
            for rec in src[owner]["members"]:
                raw.append("|".join((
                    target.TAG, str(index), rec["kind"], rec["name"],
                    rec["return_or_type"], rec["linkage"], rec["erased_args"])))
        self.assertEqual(target.parse_runtime("[LOG] bootstrap\n" + "\n".join(raw)), src)
        examples = [
            raw[1:], raw + raw[:1],
            [raw[0], raw[0]] + raw[1:],
            [raw[0]] + [x.replace("|1|TYPE", "|0|TYPE")
                        if "|1|TYPE" in x else x for x in raw[1:]],
            [raw[0].replace("RandomState", "FakeState")] + raw[1:],
            ["[logger] " + x for x in raw],
        ]
        for payload in examples:
            with self.assertRaises(target.BindingFrontierError):
                target.parse_runtime("\n".join(payload))
        self.assertRaises(target.BindingFrontierError,
                          target.parse_runtime, "\n".join(raw) + "\n" + "a" * 262145)

    def test_mocked_capture_is_exclusive_and_leaves_world_seed_gate_closed(self):
        with tempfile.TemporaryDirectory() as temp:
            home = Path(temp)
            lock = home / "vanilla.toml"
            lock.write_text('minecraft="26.2"\nprotocol=776\ndata_version=4903\n'
                            '[source]\narchive_sha256="' + "a" * 64 + '"\n'
                            '[runtime]\nserver_sha256="' + "b" * 64 + '"\n')
            output = home / "source-free.json"
            with mock.patch.object(target.vanilla_atlas, "connect_db") as db, \
                 mock.patch.object(target.source_probe, "require_pinned_source", return_value="a" * 64), \
                 mock.patch.object(target, "atlas_binding", return_value=self.atlas()), \
                 mock.patch.object(target.official, "sha256_file", return_value="b" * 64), \
                 mock.patch.object(target, "runtime_shape", return_value=self.runtime()):
                result = target.capture(source=home/"private.zip", db=home/"db",
                    lock=lock, server=home/"official.jar", output=output)
                self.assertEqual(result["jvm_types"], 12)
                self.assertFalse(result["world_seed_random_state_bound"])
                target.validate(json.loads(output.read_text()), tomllib.loads(lock.read_text()))
                self.assertTrue(db.return_value.close.called)
                with self.assertRaises(ValueError):
                    target.capture(source=home/"private.zip", db=home/"db",
                        lock=lock, server=home/"official.jar", output=output)

    @unittest.skipUnless(shutil.which("java") and shutil.which("javac"),
                         "JVM compiler and runtime required")
    def test_original_synthetic_jvm_signature_probe_and_stdout_redirect(self):
        with tempfile.TemporaryDirectory() as temp:
            home = Path(temp)
            src = home / "src"
            def put(pkg: str, name: str, body: str):
                path = src / (pkg.replace(".", "/") + "/" + name + ".java")
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text("package " + pkg + ";\n" + body + "\n", encoding="utf-8")

            put("net.minecraft", "SharedConstants",
                "public final class SharedConstants { public static boolean ready;"
                " public static void tryDetectVersion(){ready=true;} }")
            put("net.minecraft.server", "Bootstrap",
                "public final class Bootstrap { public static void bootStrap(){"
                " if(!net.minecraft.SharedConstants.ready) throw new IllegalStateException();"
                " System.setOut(new java.io.PrintStream(new java.io.ByteArrayOutputStream())); } }")
            root = "net.minecraft.world.level.levelgen"
            put(root, "NoiseGeneratorSettings", "public final class NoiseGeneratorSettings {}")
            put("net.minecraft.core", "HolderGetter", "public interface HolderGetter {}")
            put("net.minecraft.resources", "ResourceKey", "public final class ResourceKey {}")
            put(root, "RandomState", "public final class RandomState {"
                "public static RandomState create(NoiseGeneratorSettings s,"
                "net.minecraft.core.HolderGetter getter,long seed){return new RandomState();}"
                "public Object getOrCreateNoise(net.minecraft.resources.ResourceKey k){return null;}"
                "private RandomState(){} }")
            put(root, "DensityFunction", "public interface DensityFunction {"
                "interface Visitor {} record NoiseHolder(Object a,Object b){} }")
            put(root, "NoiseRouter", "public final class NoiseRouter {"
                "public NoiseRouter mapAll(DensityFunction.Visitor v){return this;} }")
            put(root, "Noises", "public final class Noises {"
                "public static Object instantiate(net.minecraft.core.HolderGetter h, Object k)"
                "{return null;} }")
            put(root, "NoiseRouterData", "public final class NoiseRouterData {}")
            put(root, "DensityFunctions", "public final class DensityFunctions {"
                "public static final class Noise {} }")
            put(root+".synth", "NormalNoise", "public final class NormalNoise {"
                "public record NoiseParameters(int firstOctave) {} }")
            put("net.minecraft.core", "Holder", "public interface Holder {}")
            put("net.minecraft.core.registries", "Registries",
                "public final class Registries { public static final int NOISE = 42; }")

            classes = home / "classes"
            compiled = subprocess.run(
                ["javac", "-encoding", "UTF-8", "-d", str(classes),
                 *[str(p) for p in src.rglob("*.java")]],
                capture_output=True, text=True, timeout=30)
            self.assertEqual(compiled.returncode, 0, compiled.stderr)
            with mock.patch.object(target.official, "extract_classpath", return_value=[classes]):
                runtime = target.runtime_shape(home/"toy.jar", timeout=30)
            self.assertEqual(runtime[target.TYPES[0]]["status"], "present")
            self.assertEqual(runtime[target.TYPES[3]]["status"], "present")
            self.assertTrue(any(
                m["name"] == "instantiate"
                for m in runtime[target.TYPES[2]]["members"]))
            self.assertTrue(any(
                m["name"] == "NOISE"
                for m in runtime[target.TYPES[11]]["members"]))


if __name__ == "__main__":
    unittest.main()
