"""Source-free, fail-closed tests for the pinned 26.2 density primitive probe.

The synthetic JVM classes below are original toy behavior, deliberately not
Mojang/26.2 math. Only the user's source-owning official runtime can create
a valid real Minecraft density oracle.
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
import worldgen_26_2_density_primitive_capture as capture  # noqa: E402


class DensityPrimitiveCaptureTests(unittest.TestCase):
    @staticmethod
    def lock() -> dict:
        return {
            "minecraft": "26.2", "protocol": 776, "data_version": 4903,
            "source": {"archive_sha256": "a" * 64},
            "runtime": {"server_sha256": "b" * 64},
        }

    @staticmethod
    def methods() -> dict:
        return {
            name: {
                "owner": owner,
                "signature": symbol + "(" + ", ".join(
                    f"final {kind} arg{i}" for i, kind in enumerate(argtypes)
                ) + ")",
                "body_sha256": "c" * 64,
                "normalized_sha256": "d" * 64,
            }
            for name, (owner, symbol, argtypes) in capture.METHODS.items()
        }

    def manifest(self) -> dict:
        lock = self.lock()
        return {
            "schema": 1, "kind": capture.KIND,
            "minecraft": lock["minecraft"], "protocol": lock["protocol"],
            "data_version": lock["data_version"], "stage": "density_primitive",
            "source_archive_sha256": lock["source"]["archive_sha256"],
            "official_server_sha256": lock["runtime"]["server_sha256"],
            "source_text_included": False,
            "independent_var_sem_admitted": False,
            "production_worldgen_enabled": False,
            "methods": self.methods(), "profiles": capture.PROFILES,
            "vectors": [dict(row, value_bits="0x8000000000000000")
                        for row in capture.inputs()],
        }

    def test_640_deterministic_integer_contexts_and_closed_gates(self):
        rows = capture.inputs()
        self.assertEqual(len(rows), 640)
        self.assertEqual(len({(r["profile"], r["seed_bits"], r["block_x"],
                               r["block_y"], r["block_z"]) for r in rows}), 640)
        self.assertEqual(set(capture.PROFILES), {r["profile"] for r in rows})
        self.assertEqual(set(capture.SEEDS), {r["seed_bits"] for r in rows})
        for row in rows:
            self.assertIs(type(row["block_x"]), int)
            self.assertIs(type(row["block_y"]), int)
            self.assertIs(type(row["block_z"]), int)
        self.assertIn(-64, {r["block_y"] for r in rows})
        self.assertIn(320, {r["block_y"] for r in rows})
        self.assertTrue(any(r["block_x"] < 0 for r in rows))
        capture.validate(self.manifest(), self.lock())

    def test_corruption_profile_missing_rows_bits_and_admission_are_rejected(self):
        mutations = [
            ("vectors", lambda m: m["vectors"].pop()),
            ("profile", lambda m: m["profiles"].pop("constant_fraction")),
            ("context", lambda m: m["vectors"][17].__setitem__("block_y", 12345)),
            ("binary", lambda m: m["vectors"][0].__setitem__("value_bits", "0xg000000000000000")),
            ("source-rich", lambda m: m.__setitem__("source_java", "not allowed")),
            ("admission", lambda m: m.__setitem__("independent_var_sem_admitted", True)),
            ("publication", lambda m: m.__setitem__("production_worldgen_enabled", True)),
            ("method", lambda m: m["methods"]["constant_compute"].__setitem__("body_sha256", "wrong")),
            ("source", lambda m: m.__setitem__("source_archive_sha256", "0" * 64)),
            ("seed", lambda m: m["vectors"][0].__setitem__("seed_bits", "0" * 16)),
        ]
        for label, corrupt in mutations:
            with self.subTest(label=label):
                m = copy.deepcopy(self.manifest())
                corrupt(m)
                with self.assertRaises(capture.DensityCaptureError):
                    capture.validate(m, self.lock())

    def test_bound_source_methods_require_unique_exact_nonempty_bodies(self):
        records = self.methods()
        owner_rows: dict[str, list[dict]] = {}
        for index, row in enumerate(records.values()):
            owner_rows.setdefault(row["owner"], []).append(
                dict(row, id=index+1)
            )

        def template(conn, row, label):
            return {"source": dict(row, type=row["owner"])}

        with mock.patch.object(capture.projection, "_exact_type_methods",
                               side_effect=lambda conn, owner, limit: owner_rows.get(owner, [])), \
             mock.patch.object(capture.source_probe, "record_template", side_effect=template):
            result = capture.bound_methods(mock.MagicMock())
            self.assertEqual(result, records)
            owner_rows[capture.CONSTANT].append(owner_rows[capture.CONSTANT][0])
            with self.assertRaisesRegex(capture.DensityCaptureError, "exactly one"):
                capture.bound_methods(mock.MagicMock())
            owner_rows[capture.CONSTANT].pop()
            owner_rows[capture.CONSTANT][0]["body_sha256"] = None
            with self.assertRaisesRegex(capture.DensityCaptureError, "fingerprints"):
                capture.bound_methods(mock.MagicMock())

    def test_pinned_preflight_exclusive_output_and_source_free_result(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            lock_path = root / "26.2.toml"
            lock_path.write_text(
                'minecraft = "26.2"\nprotocol = 776\ndata_version = 4903\n'
                f'[source]\narchive_sha256 = "{"a"*64}"\n'
                f'[runtime]\nserver_sha256 = "{"b"*64}"\n', encoding="utf-8"
            )
            output = root / "density.json"
            connection = mock.MagicMock()
            with mock.patch.object(capture.vanilla_atlas, "connect_db", return_value=connection), \
                 mock.patch.object(capture.source_probe, "require_pinned_source", return_value="a" * 64), \
                 mock.patch.object(capture, "bound_methods", return_value=self.methods()), \
                 mock.patch.object(capture.official, "sha256_file", return_value="b" * 64), \
                 mock.patch.object(capture, "runtime_bits",
                                   side_effect=lambda server, rows: ["0x8000000000000000"] * len(rows)):
                summary = capture.capture(
                    source=root / "private-src.zip", db=root / "atlas.sqlite",
                    lock=lock_path, server=root / "private.jar", output=output
                )
                self.assertEqual(summary["rows"], 640)
                self.assertFalse(summary["independent_var_sem_admitted"])
                self.assertFalse(summary["production_worldgen_enabled"])
                self.assertTrue(connection.close.called)
                output_json = json.loads(output.read_text())
                capture.validate(output_json, tomllib.loads(lock_path.read_text()))
                with self.assertRaisesRegex(ValueError, "already exists"):
                    capture.capture(
                        source=root / "private-src.zip", db=root / "atlas.sqlite",
                        lock=lock_path, server=root / "private.jar", output=output
                    )
            lock_path.write_text('minecraft = "26.1"\nprotocol = 776\ndata_version = 4903\n')
            with mock.patch.object(capture.vanilla_atlas, "connect_db") as atlas:
                with self.assertRaisesRegex(capture.DensityCaptureError, "wrong pinned"):
                    capture.capture(source=root, db=root, lock=lock_path,
                                    server=root, output=root / "never.json")
                atlas.assert_not_called()

    @unittest.skipUnless(shutil.which("java") and shutil.which("javac"),
                         "Java toolchain not available for synthetic reflection test")
    def test_original_toy_jvm_contract_and_preserved_signed_zero(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            src = root / "src/net/minecraft/world/level/levelgen"
            src.mkdir(parents=True)
            (src / "DensityFunction.java").write_text(
                """package net.minecraft.world.level.levelgen;
                public interface DensityFunction {
                  double compute(FunctionContext context);
                  public interface FunctionContext {
                    int blockX(); int blockY(); int blockZ();
                  }
                  public record SinglePointContext(int blockX, int blockY, int blockZ)
                    implements FunctionContext {}
                }
                """, encoding="utf-8"
            )
            (src / "DensityFunctions.java").write_text(
                """package net.minecraft.world.level.levelgen;
                public final class DensityFunctions {
                  public static DensityFunction constant(double d) { return new Constant(d); }
                  public static DensityFunction yClampedGradient(int a,int b,double from,double to) {
                    return new YClampedGradient(a,b,from,to);
                  }
                  public record Constant(double value) implements DensityFunction {
                    public double compute(DensityFunction.FunctionContext p) { return value; }
                  }
                  // Toy contract only: deliberately NOT Minecraft's interpolation formula.
                  public record YClampedGradient(int a,int b,double from,double to)
                    implements DensityFunction {
                    public double compute(DensityFunction.FunctionContext p) {
                      if(p.blockY()<a) return from;
                      if(p.blockY()>b) return to;
                      return (double)p.blockY();
                    }
                  }
                }
                """, encoding="utf-8"
            )
            classes = root / "classes"
            compiled = subprocess.run(
                ["javac", "-d", str(classes), str(src / "DensityFunction.java"),
                 str(src / "DensityFunctions.java")], text=True,
                capture_output=True, check=False, timeout=30,
            )
            self.assertEqual(compiled.returncode, 0, compiled.stderr)
            with mock.patch.object(capture.official, "extract_classpath", return_value=[classes]):
                raw = capture.runtime_bits(root / "synthetic.jar", capture.inputs(), timeout=30)
            self.assertEqual(len(raw), 640)
            self.assertEqual(raw[0], "0x8000000000000000")
            self.assertEqual(raw[160], "0x3fe0000000000000")
            self.assertEqual(raw[320], "0xbff0000000000000")
            self.assertEqual(raw[321], "0xbff0000000000000")
            self.assertEqual(raw[322], "0xc050000000000000")  # exact -64.0 toy result
            self.assertEqual(raw[32], raw[0], "seed-independent constant")
            with mock.patch.object(capture.official, "extract_classpath", return_value=[classes]):
                with self.assertRaisesRegex(capture.DensityCaptureError, "exact 640"):
                    capture.runtime_bits(root / "synthetic.jar", capture.inputs()[:-1])


if __name__ == "__main__":
    unittest.main()
