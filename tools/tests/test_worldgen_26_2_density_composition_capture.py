"""Fail-closed, source-free tests for the candidate 26.2 composition oracle.

The JVM fixtures are original toy code, not the Minecraft add/mul laws.
No official runtime, source archive or Java bytecode is redistributed.
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
import worldgen_26_2_density_composition_capture as composed  # noqa: E402


class ComposedDensityCaptureTests(unittest.TestCase):
    @staticmethod
    def lock() -> dict:
        return {
            "minecraft": "26.2", "protocol": 776, "data_version": 4903,
            "source": {"archive_sha256": "a" * 64},
            "runtime": {"server_sha256": "b" * 64},
        }

    @staticmethod
    def fake_methods(spec: dict) -> dict:
        return {
            label: {
                "owner": owner,
                "signature": name + "(" + ", ".join(
                    f"final {type_} arg{i}" for i, type_ in enumerate(types)
                ) + ")",
                "body_sha256": "c" * 64,
                "normalized_sha256": "d" * 64,
            }
            for label, (owner, name, types) in spec.items()
        }

    def manifest(self) -> dict:
        lock = self.lock()
        return {
            "schema": 1, "kind": composed.KIND,
            "minecraft": "26.2", "protocol": 776, "data_version": 4903,
            "stage": "composed_density",
            "source_archive_sha256": lock["source"]["archive_sha256"],
            "official_server_sha256": lock["runtime"]["server_sha256"],
            "source_text_included": False,
            "independent_var_sem_admitted": False,
            "production_worldgen_enabled": False,
            "runtime_startup_sequence": composed.primitive.STARTUP_SEQUENCE.copy(),
            "primitive_methods": self.fake_methods(composed.primitive.METHODS),
            "composition_methods": self.fake_methods(composed.COMPOSITION_METHODS),
            "profiles": copy.deepcopy(composed.PROFILES),
            "vectors": [
                dict(row, value_bits="0x8000000000000000")
                for row in composed.inputs()
            ],
        }

    def test_exact_inputs_metadata_and_complete_1280_contexts(self):
        records = composed.inputs()
        self.assertEqual(len(records), 1280)
        self.assertEqual(len(set((r["profile"], r["seed_bits"], r["block_x"],
                                  r["block_y"], r["block_z"]) for r in records)), 1280)
        self.assertEqual(set(composed.PROFILES), {r["profile"] for r in records})
        self.assertEqual(set(composed.primitive.SEEDS), {r["seed_bits"] for r in records})
        self.assertIn("add_zero_left", composed.PROFILES)
        self.assertIn("add_zero_right", composed.PROFILES)
        self.assertIn("mul_zero_left", composed.PROFILES)
        self.assertIn("mul_zero_right", composed.PROFILES)
        composed.validate(self.manifest(), self.lock())

    def test_corruption_substitutions_and_open_gates_refused(self):
        mutations = [
            ("vector", lambda m: m["vectors"].pop()),
            ("context", lambda m: m["vectors"][1].__setitem__("block_y", -12345)),
            ("profile", lambda m: m["profiles"].pop("mul_half")),
            ("raw-bit", lambda m: m["vectors"][0].__setitem__("value_bits", "NaN")),
            ("extra-source", lambda m: m.__setitem__("source_java", "do not admit")),
            ("bootstrap", lambda m: m["runtime_startup_sequence"].reverse()),
            ("var-sem", lambda m: m.__setitem__("independent_var_sem_admitted", True)),
            ("publication", lambda m: m.__setitem__("production_worldgen_enabled", True)),
            ("source", lambda m: m["composition_methods"]["add_factory"].__setitem__("signature", "add(double a)")),
            ("fingerprint", lambda m: m["composition_methods"]["mul_factory"].__setitem__("body_sha256", "")),
            ("duplicate", lambda m: m["composition_methods"]["mul_factory"].__setitem__(
                "signature", m["composition_methods"]["add_factory"]["signature"]
            )),
            ("seed", lambda m: m["vectors"][32].__setitem__("seed_bits", "0" * 16)),
        ]
        for label, mutate in mutations:
            with self.subTest(label=label):
                manifest = self.manifest()
                mutate(manifest)
                with self.assertRaises(composed.CompositionCaptureError):
                    composed.validate(manifest, self.lock())

    def test_atlas_composition_declarations_must_exist_once_with_exact_sha(self):
        expected = self.fake_methods(composed.COMPOSITION_METHODS)
        rows = [dict(item, id=i) for i, item in enumerate(expected.values(), start=1)]
        def template(conn, row, label):
            return {"source": dict(row, type=row["owner"])}
        with mock.patch.object(composed.projection, "_exact_type_methods", return_value=rows), \
             mock.patch.object(composed.source_probe, "record_template", side_effect=template):
            self.assertEqual(composed.bound_composition_methods(mock.MagicMock()), expected)
            rows.append(rows[0])
            with self.assertRaisesRegex(composed.CompositionCaptureError, "exactly one"):
                composed.bound_composition_methods(mock.MagicMock())
            rows.pop()
            rows[1]["normalized_sha256"] = None
            with self.assertRaisesRegex(composed.CompositionCaptureError, "fingerprints"):
                composed.bound_composition_methods(mock.MagicMock())

    def test_source_pins_exclusive_output_and_closed_gates(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            lock_path = root / "target.toml"
            lock_path.write_text(
                'minecraft = "26.2"\nprotocol = 776\ndata_version = 4903\n'
                f'[source]\narchive_sha256 = "{"a"*64}"\n'
                f'[runtime]\nserver_sha256 = "{"b"*64}"\n', encoding="utf-8"
            )
            conn = mock.MagicMock()
            output = root / "composed.json"
            with mock.patch.object(composed.vanilla_atlas, "connect_db", return_value=conn), \
                 mock.patch.object(composed.source_probe, "require_pinned_source", return_value="a"*64), \
                 mock.patch.object(composed.primitive, "bound_methods", return_value=self.fake_methods(composed.primitive.METHODS)), \
                 mock.patch.object(composed, "bound_composition_methods", return_value=self.fake_methods(composed.COMPOSITION_METHODS)), \
                 mock.patch.object(composed.official, "sha256_file", return_value="b"*64), \
                 mock.patch.object(composed, "runtime_bits", return_value=["0x8000000000000000"]*1280):
                summary = composed.capture(
                    source=root / "source.zip", db=root / "atlas.sqlite",
                    lock=lock_path, server=root / "runtime.jar", output=output
                )
                self.assertEqual(summary["rows"], 1280)
                self.assertFalse(summary["production_worldgen_enabled"])
                composed.validate(json.loads(output.read_text()), tomllib.loads(lock_path.read_text()))
                self.assertTrue(conn.close.called)
                with self.assertRaisesRegex(ValueError, "already exists"):
                    composed.capture(source=root, db=root, lock=lock_path,
                                     server=root, output=output)

    @unittest.skipUnless(shutil.which("java") and shutil.which("javac"),
                         "Java toolchain unavailable for original synthetic reflection")
    def test_original_toy_java_composition_and_registry_bootstrap(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            src = root / "src"
            shared = src / "net/minecraft"
            bootstrap = src / "net/minecraft/server"
            functions = src / "net/minecraft/world/level/levelgen"
            for directory in (shared, bootstrap, functions):
                directory.mkdir(parents=True, exist_ok=True)
            (shared / "SharedConstants.java").write_text(
                """package net.minecraft;
                public final class SharedConstants {
                  private static boolean detected;
                  public static void tryDetectVersion() { detected = true; }
                  public static boolean detected() { return detected; }
                }""", encoding="utf-8"
            )
            (bootstrap / "Bootstrap.java").write_text(
                """package net.minecraft.server;
                public final class Bootstrap {
                  private static boolean ready;
                  public static void bootStrap() {
                    if (!net.minecraft.SharedConstants.detected())
                      throw new IllegalStateException("version was not detected");
                    ready = true;
                  }
                  public static boolean ready() { return ready; }
                }""", encoding="utf-8"
            )
            (functions / "DensityFunction.java").write_text(
                """package net.minecraft.world.level.levelgen;
                public interface DensityFunction {
                  double compute(FunctionContext context);
                  public interface FunctionContext {
                    int blockX(); int blockY(); int blockZ();
                  }
                  public record SinglePointContext(int blockX, int blockY, int blockZ)
                    implements FunctionContext {}
                }""", encoding="utf-8"
            )
            (functions / "DensityFunctions.java").write_text(
                """package net.minecraft.world.level.levelgen;
                public final class DensityFunctions {
                  static {
                    if (!net.minecraft.server.Bootstrap.ready())
                      throw new ExceptionInInitializerError("Not bootstrapped");
                  }
                  public static DensityFunction constant(double d) { return new Constant(d); }
                  public static DensityFunction yClampedGradient(int fromY, int toY,
                      double fromValue, double toValue) {
                    return new Gradient(fromY, toY, fromValue, toValue);
                  }
                  public static DensityFunction add(DensityFunction x, DensityFunction y) {
                    return new Add(x,y);
                  }
                  public static DensityFunction mul(DensityFunction x, DensityFunction y) {
                    return new Mul(x,y);
                  }
                  public record Constant(double v) implements DensityFunction {
                    public double compute(DensityFunction.FunctionContext c) { return v; }
                  }
                  // Synthetic Y law: deliberately NOT the official Minecraft interpolation.
                  public record Gradient(int a,int b,double c,double d) implements DensityFunction {
                    public double compute(DensityFunction.FunctionContext p) {
                      if (p.blockY() <= a) return c;
                      if (p.blockY() >= b) return d;
                      return (double)p.blockY();
                    }
                  }
                  public record Add(DensityFunction x,DensityFunction y) implements DensityFunction {
                    public double compute(DensityFunction.FunctionContext p) {
                      return x.compute(p) + y.compute(p);
                    }
                  }
                  public record Mul(DensityFunction x,DensityFunction y) implements DensityFunction {
                    public double compute(DensityFunction.FunctionContext p) {
                      return x.compute(p) * y.compute(p);
                    }
                  }
                }""", encoding="utf-8"
            )
            classes = root / "classes"
            compiled = subprocess.run(
                ["javac", "-encoding", "UTF-8", "-d", str(classes),
                 *[str(x) for x in src.rglob("*.java")]],
                text=True, capture_output=True, check=False, timeout=30,
            )
            self.assertEqual(compiled.returncode, 0, compiled.stderr)
            with mock.patch.object(composed.official, "extract_classpath", return_value=[classes]):
                bits = composed.runtime_bits(root / "toy.jar", composed.inputs(), timeout=30)
            self.assertEqual(len(bits), 1280)
            self.assertEqual(bits[0], "0x3fe0000000000000", "two toy low endpoints: -1 + .5")
            self.assertEqual(bits[160], "0xbfe0000000000000", "toy low endpoints: -1 * .5")
            self.assertEqual(bits[320], "0xbff0000000000000", "toy signed -0 + -1")
            self.assertEqual(bits[480], "0xbff0000000000000", "toy signed -1 + -0")
            self.assertEqual(bits[640], "0x0000000000000000", "toy signed zero * negative")
            self.assertEqual(bits[800], "0x0000000000000000", "toy negative * signed zero")
            self.assertEqual(bits[960], "0xc000000000000000", "toy add-self doubles -1")
            self.assertEqual(bits[1120], "0xbfe0000000000000", "toy mul-half at low Y")
            with mock.patch.object(composed.official, "extract_classpath", return_value=[classes]):
                with self.assertRaisesRegex(composed.CompositionCaptureError, "exactly 1280"):
                    composed.runtime_bits(root / "toy.jar", composed.inputs()[:-1])


if __name__ == "__main__":
    unittest.main()
