"""Synthetic tests for strictly source-locked, real-JVM Perlin/Normal capture.

The private official source/JAR never enters hosted CI. The only Java classes
compiled here are original tiny synthetic fixtures with checked signatures.
"""
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
import worldgen_26_2_perlin_normal_capture as capture  # noqa: E402


class NoiseFamilyCaptureTests(unittest.TestCase):
    def make_methods(self, stage: str):
        lookup = {}
        for index, (owner, signature, sha) in enumerate(capture.EXPECTED[stage].values()):
            lookup.setdefault(owner, []).append(
                {"id": index + 1, "signature": signature, "hash": sha, "owner": owner}
            )
        return lookup

    def test_exact_source_dependencies_match_captured_26_2_method_signatures(self):
        for stage in capture.STAGES:
            by_owner = self.make_methods(stage)

            def rows(conn, owner, limit):
                self.assertEqual(limit, 64)
                return by_owner[owner]

            def template(conn, row, candidate):
                return {"source": {
                    "type": row["owner"], "signature": row["signature"],
                    "body_sha256": row["hash"], "normalized_sha256": "f" * 64,
                }}

            with mock.patch.object(capture.projection, "_exact_type_methods", side_effect=rows), \
                 mock.patch.object(capture.source_probe, "record_template", side_effect=template):
                methods = capture.bound_methods(mock.MagicMock(), stage)
                self.assertEqual(set(methods), set(capture.EXPECTED[stage]))
                self.assertEqual(
                    methods["get_value_3"]["body_sha256"],
                    capture.EXPECTED[stage]["get_value_3"][2],
                )

    def test_missing_changed_or_duplicated_method_always_rejects(self):
        stage = "perlin_noise"
        rows = self.make_methods(stage)
        with mock.patch.object(capture.projection, "_exact_type_methods", side_effect=lambda conn, owner, limit: rows[owner][:-1]):
            with self.assertRaisesRegex(capture.CaptureError, "missing exact source method"):
                capture.bound_methods(mock.MagicMock(), stage)
        rows = self.make_methods(stage)
        with mock.patch.object(capture.projection, "_exact_type_methods", side_effect=lambda conn, owner, limit: rows[owner]), \
             mock.patch.object(capture.source_probe, "record_template", side_effect=lambda conn, row, candidate: {
                 "source": {"type": row["owner"], "signature": row["signature"],
                            "body_sha256": "0" * 64, "normalized_sha256": "f" * 64}
             }):
            with self.assertRaisesRegex(capture.CaptureError, "source body fingerprint differs"):
                capture.bound_methods(mock.MagicMock(), stage)
        rows[capture.PERLIN].append(rows[capture.PERLIN][0])
        with mock.patch.object(capture.projection, "_exact_type_methods", side_effect=lambda conn, owner, limit: rows[owner]):
            with self.assertRaisesRegex(capture.CaptureError, "ambiguous"):
                capture.bound_methods(mock.MagicMock(), stage)

    def make_manifest(self, stage: str):
        methods = {
            name: {"owner": owner, "signature": sig, "body_sha256": sha}
            for name, (owner, sig, sha) in capture.EXPECTED[stage].items()
        }
        inputs = capture.improved.probes()
        return {
            "schema": 1, "kind": capture.KIND, "minecraft": "26.2",
            "protocol": 776, "data_version": 4903,
            "source_archive_sha256": "a" * 64, "official_server_sha256": "b" * 64,
            "stage": stage, "method_body_sha256": methods["get_value_3"]["body_sha256"],
            "source_text_included": False, "independent_var_sem_admitted": False,
            "production_worldgen_enabled": False,
            "profile": dict(capture.PROFILE),
            "source_methods": methods,
            "vectors": [dict(v, value_bits="0x8000000000000000") for v in inputs],
        }

    def make_lock(self):
        return {
            "minecraft": "26.2", "protocol": 776, "data_version": 4903,
            "source": {"archive_sha256": "a" * 64},
            "runtime": {"server_sha256": "b" * 64},
        }

    def test_both_family_manifests_validate_and_profile_mutations_reject(self):
        for stage in capture.STAGES:
            manifest = self.make_manifest(stage)
            self.assertEqual(len(capture.validate_family(manifest, self.make_lock())), 160)
            manifest["profile"]["first_octave"] = -2
            with self.assertRaisesRegex(capture.CaptureError, "construction profile"):
                capture.validate_family(manifest, self.make_lock())
            manifest = self.make_manifest(stage)
            manifest["source_methods"]["get_value_3"]["body_sha256"] = "0" * 64
            with self.assertRaisesRegex(capture.CaptureError, "source method identity"):
                capture.validate_family(manifest, self.make_lock())
            manifest = self.make_manifest(stage)
            manifest["vectors"][1]["value_bits"] = "uncontrolled"
            with self.assertRaisesRegex(capture.raw_oracle.OracleError, "expected 0x"):
                capture.validate_family(manifest, self.make_lock())
            manifest = self.make_manifest(stage)
            manifest["source_text"] = "private bytes"
            with self.assertRaisesRegex(capture.CaptureError, "source-rich fields"):
                capture.validate_family(manifest, self.make_lock())

    def test_pin_preflight_and_exclusive_local_output(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            lock = root / "target.toml"
            lock.write_text(
                f'minecraft = "26.2"\nprotocol = 776\ndata_version = 4903\n'
                f'[source]\narchive_sha256 = "{"a" * 64}"\n'
                f'[runtime]\nserver_sha256 = "{"b" * 64}"\n',
                encoding="utf-8",
            )
            for stage in capture.STAGES:
                target = root / (stage + ".json")
                connection = mock.MagicMock()
                with mock.patch.object(capture.vanilla_atlas, "connect_db", return_value=connection), \
                     mock.patch.object(capture.source_probe, "require_pinned_source", return_value="a" * 64), \
                     mock.patch.object(capture, "bound_methods", return_value=self.make_manifest(stage)["source_methods"]), \
                     mock.patch.object(capture.official, "sha256_file", return_value="b" * 64), \
                     mock.patch.object(capture, "capture_runtime_bits", side_effect=lambda server, family, inputs: [
                         "0x8000000000000000" for _ in inputs
                     ]) as bridge:
                    result = capture.capture(
                        source=root / "zip", db=root / "atlas", lock=lock,
                        server=root / "jar", stage=stage, output=target,
                    )
                    self.assertEqual(result["vectors"], 160)
                    self.assertEqual(bridge.call_count, 1)
                    self.assertTrue(connection.close.called)
                    data = json.loads(target.read_text(encoding="utf-8"))
                    self.assertEqual(len(capture.validate_family(data, tomllib.loads(lock.read_text()))), 160)
                    self.assertFalse(data["independent_var_sem_admitted"])
                    self.assertFalse(data["production_worldgen_enabled"])
                    with self.assertRaisesRegex(ValueError, "already exists"):
                        capture.capture(
                            source=root / "zip", db=root / "atlas", lock=lock,
                            server=root / "jar", stage=stage, output=target,
                        )
            wrong_lock = root / "wrong.toml"
            wrong_lock.write_text('minecraft = "26.1"\nprotocol = 776\ndata_version = 4903\n')
            with mock.patch.object(capture.vanilla_atlas, "connect_db") as connection:
                with self.assertRaisesRegex(capture.CaptureError, "not the pinned"):
                    capture.capture(
                        source=root / "zip", db=root / "atlas", lock=wrong_lock,
                        server=root / "jar", stage="perlin_noise", output=root / "bad.json",
                    )
                connection.assert_not_called()

    @unittest.skipUnless(shutil.which("java") and shutil.which("javac"),
                         "JDK not installed in source-free test environment")
    def test_reflective_probe_with_original_synthetic_java_families(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            pkg = root / "src/net/minecraft/util"
            pkg.mkdir(parents=True)
            (pkg / "RandomSource.java").write_text(
                "package net.minecraft.util;\n"
                "public interface RandomSource {\n"
                "  long seed();\n"
                "  static RandomSource create(long seed) { return () -> seed; }\n"
                "}\n",
                encoding="utf-8",
            )
            synth = root / "src/net/minecraft/world/level/levelgen/synth"
            synth.mkdir(parents=True)
            (synth / "PerlinNoise.java").write_text(
                "package net.minecraft.world.level.levelgen.synth;\n"
                "import net.minecraft.util.RandomSource;\n"
                "public final class PerlinNoise {\n"
                "  private final long seed;\n"
                "  private final int octave;\n"
                "  private PerlinNoise(RandomSource r,int o) { seed=r.seed(); octave=o; }\n"
                "  public static PerlinNoise create(RandomSource r,int o,double first,double... rest) {\n"
                "    if(o!=-3 || first!=1.0 || rest.length!=3 || rest[0]!=0.0 || rest[1]!=0.5 || rest[2]!=1.0)\n"
                "      throw new IllegalArgumentException(\"incorrect explicit profile\");\n"
                "    return new PerlinNoise(r,o);\n"
                "  }\n"
                "  public double getValue(double x,double y,double z) {\n"
                "    if(Double.doubleToRawLongBits(x)==Long.MIN_VALUE) return -0.0;\n"
                "    return x+y+z+(seed&1L)+octave;\n"
                "  }\n"
                "}\n", encoding="utf-8",
            )
            (synth / "NormalNoise.java").write_text(
                "package net.minecraft.world.level.levelgen.synth;\n"
                "import net.minecraft.util.RandomSource;\n"
                "public final class NormalNoise {\n"
                "  private final long seed;\n"
                "  private NormalNoise(RandomSource r) { seed=r.seed(); }\n"
                "  public static NormalNoise create(RandomSource r,int o,double... amps) {\n"
                "    if(o!=-3 || amps.length!=4 || amps[0]!=1.0 || amps[1]!=0.0 || amps[2]!=0.5 || amps[3]!=1.0)\n"
                "      throw new IllegalArgumentException(\"incorrect explicit profile\");\n"
                "    return new NormalNoise(r);\n"
                "  }\n"
                "  public double getValue(double x,double y,double z) {\n"
                "    if(Double.doubleToRawLongBits(x)==Long.MIN_VALUE) return -0.0;\n"
                "    return x+y+z+(seed&1L);\n"
                "  }\n"
                "}\n", encoding="utf-8",
            )
            classes = root / "classes"
            compiled = subprocess.run([
                "javac", "-d", str(classes),
                str(pkg / "RandomSource.java"), str(synth / "PerlinNoise.java"),
                str(synth / "NormalNoise.java"),
            ], capture_output=True, text=True, check=False, timeout=30)
            self.assertEqual(compiled.returncode, 0, compiled.stderr)
            inputs = capture.improved.probes()[:20]
            for stage in capture.STAGES:
                with mock.patch.object(capture.official, "extract_classpath", return_value=[classes]):
                    bits = capture.capture_runtime_bits(root / "synthetic.jar", stage, inputs, timeout=30)
                self.assertEqual(len(bits), 20)
                self.assertEqual(bits[1], "0x8000000000000000")
                self.assertEqual(bits[0], "0xc008000000000000" if stage == "perlin_noise" else
                                 "0x0000000000000000")
                self.assertEqual(bits[5], "0xbff8000000000000" if stage == "perlin_noise" else
                                 "0x3ff8000000000000")


if __name__ == "__main__":
    unittest.main()
