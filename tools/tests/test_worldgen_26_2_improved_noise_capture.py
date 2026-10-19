"""Synthetic, source-free tests for the official 26.2 ImprovedNoise capture boundary."""
from __future__ import annotations

import json
import shutil
import struct
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import worldgen_26_2_improved_noise_capture as capture  # noqa: E402
import worldgen_noise_oracle as differential  # noqa: E402


class CaptureTests(unittest.TestCase):
    def test_exact_overload_is_required(self) -> None:
        intended = {
            "name": "noise", "signature":
            "public double noise(double x, double y, double z)",
        }
        five = {
            "name": "noise", "signature":
            "noise(double x,double y,double z,double yScale,double yMax)",
        }
        wrong = {"name": "noise", "signature": "noise(float x,float y,float z)"}
        self.assertIs(capture.select_source_method([five, intended, wrong]), intended)
        with self.assertRaisesRegex(capture.CaptureError, "got 0"):
            capture.select_source_method([five, wrong])
        with self.assertRaisesRegex(capture.CaptureError, "got 2"):
            capture.select_source_method([intended, intended])

    def test_frozen_source_free_probe_set_is_diverse_and_bitwise_distinct(self) -> None:
        vectors = capture.probes()
        self.assertEqual(len(vectors), 5 * 32)
        self.assertEqual(len({
            tuple(vector.items()) for vector in vectors
        }), len(vectors))
        self.assertGreaterEqual(len({v["seed_bits"] for v in vectors}), 3)
        self.assertIn("0x8000000000000000", {v["x_bits"] for v in vectors})
        self.assertIn("0x0000000000000000", {v["x_bits"] for v in vectors})
        self.assertIn("0x8000000000000000", {v["seed_bits"] for v in vectors})
        self.assertEqual(capture.float_bits(-0.0), "0x8000000000000000")
        self.assertEqual(capture.float_bits(0.0), "0x0000000000000000")

    def test_destination_is_exclusive_and_outside_repository(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            target = Path(folder) / "oracle.json"
            self.assertEqual(capture.external_output(target), target.resolve())
            target.write_text("existing", encoding="utf-8")
            with self.assertRaisesRegex(capture.CaptureError, "already exists"):
                capture.external_output(target)
        with self.assertRaisesRegex(capture.CaptureError, "outside"):
            capture.external_output(capture.ROOT / "src/generated-noise.json")

    def test_source_fingerprint_rejects_empty_or_missing_body(self) -> None:
        row = {"name": "noise", "signature": "noise(double a,double b,double c)"}
        with mock.patch.object(capture.projection, "_exact_type_methods", return_value=[row]), \
             mock.patch.object(capture.source_probe, "record_template") as evidence:
            evidence.return_value = {
                "source": {"type": capture.OWNER, "body_sha256": None,
                           "normalized_sha256": "a" * 64}
            }
            with self.assertRaisesRegex(capture.CaptureError, "fingerprint"):
                capture.source_fingerprint(mock.MagicMock())
            evidence.return_value["source"]["body_sha256"] = "b" * 64
            self.assertEqual(capture.source_fingerprint(mock.MagicMock()), "b" * 64)

    def test_pinned_capture_writes_only_source_free_unadmitted_bits(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            output = root / "probe.json"
            lock = root / "lock.toml"
            source_sha = "a" * 64
            runtime_sha = "b" * 64
            lock.write_text(
                f'minecraft = "26.2"\nprotocol = 776\ndata_version = 4903\n'
                f'[source]\narchive_sha256 = "{source_sha}"\n'
                f'[runtime]\nserver_sha256 = "{runtime_sha}"\n',
                encoding="utf-8",
            )
            conn = mock.MagicMock()
            with mock.patch.object(capture.vanilla_atlas, "connect_db", return_value=conn), \
                 mock.patch.object(capture.source_probe, "require_pinned_source", return_value=source_sha), \
                 mock.patch.object(capture, "source_fingerprint", return_value="c" * 64), \
                 mock.patch.object(capture.official, "sha256_file", return_value=runtime_sha), \
                 mock.patch.object(capture, "read_runtime_bits", side_effect=lambda jar, rows: [
                     "0x0000000000000000" for _ in rows
                 ]) as runner:
                result = capture.capture(
                    source=root / "dummy-src.zip", db=root / "dummy.sqlite",
                    lock=lock, server=root / "dummy-server.jar", output=output,
                )
                self.assertEqual(result["vectors"], 160)
                self.assertTrue(conn.close.called)
                self.assertEqual(runner.call_count, 1)
                manifest = json.loads(output.read_text(encoding="utf-8"))
                self.assertEqual(len(manifest["vectors"]), 160)
                self.assertEqual(set(manifest["vectors"][0]), set(differential.VECTOR_FIELDS))
                self.assertEqual(manifest["method_body_sha256"], "c" * 64)
                self.assertEqual(manifest["stage"], "improved_noise")
                self.assertFalse(manifest["production_worldgen_enabled"])
                self.assertFalse(manifest["independent_var_sem_admitted"])
                self.assertEqual(differential.validate(
                    manifest,
                    {"minecraft": "26.2", "protocol": 776, "data_version": 4903,
                     "source": {"archive_sha256": source_sha},
                     "runtime": {"server_sha256": runtime_sha}},
                    "official_26_2_noise_oracle_candidate",
                )[(manifest["vectors"][0]["seed_bits"], manifest["vectors"][0]["x_bits"],
                    manifest["vectors"][0]["y_bits"], manifest["vectors"][0]["z_bits"])],
                    "0x0000000000000000")
                with self.assertRaisesRegex(capture.CaptureError, "already exists"):
                    capture.capture(
                        source=root / "dummy-src.zip", db=root / "dummy.sqlite",
                        lock=lock, server=root / "dummy-server.jar", output=output,
                    )

    @unittest.skipUnless(shutil.which("javac") and shutil.which("java"),
                         "JDK not installed in source-free test environment")
    def test_reflective_java_stub_preserves_signed_zero_from_independent_fixture(self) -> None:
        # Compile only original synthetic test Java. No official runtime or
        # Mojang source is accessed. The stub tests the reflection boundary.
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            pkg = root / "src/net/minecraft/util"
            pkg.mkdir(parents=True)
            (pkg / "RandomSource.java").write_text(
                "package net.minecraft.util;\n"
                "public interface RandomSource {\n"
                "  long seed();\n"
                "  static RandomSource create(long seed) { return () -> seed; }\n"
                "}\n", encoding="utf-8",
            )
            synth = root / "src/net/minecraft/world/level/levelgen/synth"
            synth.mkdir(parents=True)
            (synth / "ImprovedNoise.java").write_text(
                "package net.minecraft.world.level.levelgen.synth;\n"
                "import net.minecraft.util.RandomSource;\n"
                "public final class ImprovedNoise {\n"
                "  private final long seed;\n"
                "  public ImprovedNoise(RandomSource src) { seed = src.seed(); }\n"
                "  public double noise(double x,double y,double z) {\n"
                "    if (Double.doubleToRawLongBits(x)==Long.MIN_VALUE) return -0.0;\n"
                "    return x+y+z+(seed&1L);\n"
                "  }\n"
                "}\n", encoding="utf-8",
            )
            classes = root / "classes"
            comp = subprocess.run([
                "javac", "-d", str(classes),
                str(pkg / "RandomSource.java"), str(synth / "ImprovedNoise.java"),
            ], check=False, text=True, capture_output=True, timeout=30)
            self.assertEqual(comp.returncode, 0, comp.stderr)
            selected = capture.probes()[:16]
            with mock.patch.object(capture.official, "extract_classpath", return_value=[classes]):
                outputs = capture.read_runtime_bits(root / "synthetic.jar", selected, timeout=30)
            self.assertEqual(len(outputs), len(selected))
            self.assertEqual(outputs[0], "0x0000000000000000")
            self.assertEqual(outputs[1], "0x8000000000000000")
            self.assertEqual(outputs[2], "0x0000000000000000")
            self.assertEqual(outputs[5], "0x3ff8000000000000")  # 0.5 + 0.5 + 0.5 = 1.5
            self.assertEqual(outputs[5], capture.float_bits(1.5))


if __name__ == "__main__":
    unittest.main()
