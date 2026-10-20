"""Fail-closed direct-seeded 26.2 Noise.compute capture contracts.

The independent toy JVM deliberately has no Minecraft classes or maths.
It checks only reflection, constructor binding, output framing and ownership.
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
import worldgen_26_2_noise_density_direct_capture as captured  # noqa: E402


class DirectNoiseDensityCaptureTests(unittest.TestCase):
    @staticmethod
    def lock():
        return {
            "minecraft": "26.2", "protocol": 776, "data_version": 4903,
            "source": {"archive_sha256": "a" * 64},
            "runtime": {"server_sha256": "b" * 64},
        }

    @staticmethod
    def methods():
        return {
            key: {"owner": owner, "signature": signature,
                  "body_sha256": digest, "normalized_sha256": "c" * 64}
            for key, (owner, signature, digest) in captured.SOURCE_LOCKED_METHODS.items()
        }

    def manifest(self):
        return {
            "schema": 1, "kind": captured.KIND, "stage": captured.STAGE,
            "minecraft": "26.2", "protocol": 776, "data_version": 4903,
            "source_archive_sha256": "a" * 64,
            "official_server_sha256": "b" * 64,
            "source_methods": self.methods(),
            "runtime_startup_sequence": captured.primitive.STARTUP_SEQUENCE.copy(),
            "profiles": copy.deepcopy(captured.PROFILES),
            "seeds": list(captured.SEEDS),
            "rng_construction": "RandomSource.create(long) direct; NOT world RandomState",
            "noise_construction": (
                "NormalNoise.create(RandomSource,-3,[1,0,0.5,1]) to NoiseHolder/Noise constructor"
            ),
            "world_seed_random_state_bound": False,
            "source_text_included": False,
            "independent_var_sem_admitted": False,
            "production_worldgen_enabled": False,
            "vectors": [
                dict(row, value_bits="0x8000000000000000")
                for row in captured.inputs()
            ],
        }

    def test_strict_480_ordered_xyz_inputs_and_source_free_gate(self):
        values = captured.inputs()
        self.assertEqual(len(values), 480)
        self.assertEqual(len(set((v["profile"], v["seed_bits"], v["block_x"],
                                  v["block_y"], v["block_z"]) for v in values)), 480)
        self.assertEqual(set(captured.PROFILES), {v["profile"] for v in values})
        captured.validate(self.manifest(), self.lock())

    def test_bad_metadata_vectors_and_noise_source_fingerprints_reject(self):
        changes = [
            lambda x: x.__setitem__("stage", "random_state_router"),
            lambda x: x.__setitem__("world_seed_random_state_bound", True),
            lambda x: x.__setitem__("independent_var_sem_admitted", True),
            lambda x: x.__setitem__("production_worldgen_enabled", True),
            lambda x: x.__setitem__("source_text_included", True),
            lambda x: x.__setitem__("source_java", "private"),
            lambda x: x["source_methods"]["density_noise_compute"].__setitem__(
                "body_sha256", "a" * 64),
            lambda x: x["source_methods"].pop("normal_get_value"),
            lambda x: x["profiles"]["unit"].__setitem__(0, "0x0000000000000000"),
            lambda x: x["seeds"].reverse(),
            lambda x: x["vectors"].pop(),
            lambda x: x["vectors"][0].__setitem__("block_x", 99999),
            lambda x: x["vectors"][1].__setitem__("value_bits", "NaN"),
            lambda x: x["vectors"][1].__setitem__("seed_bits", "0xaaaa"),
        ]
        for change in changes:
            with self.subTest(change=str(change)):
                mutated = self.manifest()
                change(mutated)
                with self.assertRaises(captured.DirectNoiseCaptureError):
                    captured.validate(mutated, self.lock())

    def test_explicit_tagged_result_count_order_and_replacement(self):
        lines = [f"{captured.PREFIX}{i}|{i:016x}" for i in range(480)]
        with_logs = "[INFO] starting\n" + "\n[INFO] registry booted\n".join(lines) + "\nOK"
        self.assertEqual(captured.parse_output(with_logs), [f"0x{i:016x}" for i in range(480)])
        alterations = [
            lines[:-1], lines + lines[:1],
            ["HELVE26_2_DIRECT_NOISE_DENSITY|bad|1234"] + lines[1:],
            [lines[0], lines[0]] + lines[2:],
            ["[stdout] " + line for line in lines],
        ]
        for records in alterations:
            with self.assertRaises(captured.DirectNoiseCaptureError):
                captured.parse_output("\n".join(records))

    def test_mocked_pinned_capture_writes_exclusive_no_admission_evidence(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            lock_path = root / "target.toml"
            lock_path.write_text(
                'minecraft = "26.2"\nprotocol = 776\ndata_version = 4903\n'
                f'[source]\narchive_sha256 = "{"a"*64}"\n'
                f'[runtime]\nserver_sha256 = "{"b"*64}"\n',
                encoding="utf-8",
            )
            output = root / "direct_noise.json"
            with mock.patch.object(captured.vanilla_atlas, "connect_db") as connection, \
                 mock.patch.object(captured.source_probe, "require_pinned_source", return_value="a"*64), \
                 mock.patch.object(captured, "source_methods", return_value=self.methods()), \
                 mock.patch.object(captured.official, "sha256_file", return_value="b"*64), \
                 mock.patch.object(captured, "runtime_bits", return_value=["0x8000000000000000"]*480):
                result = captured.capture(source=root/"source.zip", db=root/"db.sqlite",
                    lock=lock_path, server=root/"official.jar", output=output)
                self.assertEqual(result["rows"], 480)
                self.assertFalse(result["world_seed_random_state_bound"])
                self.assertFalse(result["production_worldgen_enabled"])
                self.assertTrue(connection.return_value.close.called)
                manifest = json.loads(output.read_text())
                captured.validate(manifest, tomllib.loads(lock_path.read_text()))
                with self.assertRaises(ValueError):
                    captured.capture(source=root/"source.zip", db=root/"db.sqlite",
                        lock=lock_path, server=root/"official.jar", output=output)

    @unittest.skipUnless(shutil.which("java") and shutil.which("javac"),
                         "Java toolchain needed to verify original synthetic reflection")
    def test_original_toy_jvm_with_bootstrap_redirect_and_480_outputs(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            src = root / "src"

            def add(path, code):
                target = src / path
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text(code, encoding="utf-8")

            add("net/minecraft/SharedConstants.java", """
                package net.minecraft;
                public final class SharedConstants {
                  public static boolean ready;
                  public static void tryDetectVersion() { ready=true; }
                }""")
            add("net/minecraft/server/Bootstrap.java", """
                package net.minecraft.server;
                public final class Bootstrap {
                  public static void bootStrap() {
                    if (!net.minecraft.SharedConstants.ready)
                      throw new IllegalStateException("no version detection");
                    System.setOut(new java.io.PrintStream(new java.io.ByteArrayOutputStream()));
                  }
                }""")
            add("net/minecraft/util/RandomSource.java", """
                package net.minecraft.util;
                public interface RandomSource {
                  long seed();
                  static RandomSource create(long s) {
                    return new RandomSource() { public long seed() { return s; } };
                  }
                }""")
            add("it/unimi/dsi/fastutil/doubles/DoubleList.java", """
                package it.unimi.dsi.fastutil.doubles;
                public interface DoubleList {}""")
            add("it/unimi/dsi/fastutil/doubles/DoubleArrayList.java", """
                package it.unimi.dsi.fastutil.doubles;
                public final class DoubleArrayList implements DoubleList {
                  public static DoubleList wrap(double[] values) { return new DoubleArrayList(); }
                }""")
            add("net/minecraft/core/Holder.java", """
                package net.minecraft.core;
                public record Holder(Object data) {
                  public static Holder direct(Object data) { return new Holder(data); }
                }""")
            add("net/minecraft/world/level/levelgen/synth/NormalNoise.java", """
                package net.minecraft.world.level.levelgen.synth;
                import it.unimi.dsi.fastutil.doubles.DoubleList;
                import net.minecraft.util.RandomSource;
                public record NormalNoise(double bias) {
                  public static NormalNoise create(RandomSource r, int octave, double[] amplitudes) {
                    return new NormalNoise(r.seed()%1024+octave+amplitudes[0]);
                  }
                  public double getValue(double x,double y,double z) {
                    return bias + x*0.125 + y*0.25 + z*0.5;
                  }
                  public record NoiseParameters(int firstOctave, DoubleList amplitudes) {}
                }""")
            add("net/minecraft/world/level/levelgen/DensityFunction.java", """
                package net.minecraft.world.level.levelgen;
                import net.minecraft.core.Holder;
                import net.minecraft.world.level.levelgen.synth.NormalNoise;
                public interface DensityFunction {
                  double compute(FunctionContext c);
                  interface FunctionContext {
                    int blockX(); int blockY(); int blockZ();
                  }
                  record SinglePointContext(int blockX,int blockY,int blockZ)
                      implements FunctionContext {}
                  record NoiseHolder(Holder parameters, NormalNoise noise) {}
                }""")
            add("net/minecraft/world/level/levelgen/DensityFunctions.java", """
                package net.minecraft.world.level.levelgen;
                public final class DensityFunctions {
                  public record Noise(DensityFunction.NoiseHolder noise,double xzScale,
                                      double yScale) implements DensityFunction {
                    public double compute(DensityFunction.FunctionContext c) {
                      return noise.noise().getValue(c.blockX()*xzScale,
                                                    c.blockY()*yScale,
                                                    c.blockZ()*xzScale);
                    }
                  }
                }""")
            classes = root / "classes"
            compiled = subprocess.run(
                ["javac", "-encoding", "UTF-8", "-d", str(classes),
                 *[str(p) for p in src.rglob("*.java")]],
                capture_output=True, text=True, timeout=30,
            )
            self.assertEqual(compiled.returncode, 0, compiled.stderr)
            with mock.patch.object(captured.official, "extract_classpath", return_value=[classes]):
                bits = captured.runtime_bits(root / "toy.jar", captured.inputs(), timeout=30)
            self.assertEqual(len(bits), 480)
            self.assertTrue(all(captured.BITS.fullmatch(v) for v in bits))
            self.assertNotEqual(bits[0], bits[32])
            self.assertNotEqual(bits[0], bits[160])


if __name__ == "__main__":
    unittest.main()
