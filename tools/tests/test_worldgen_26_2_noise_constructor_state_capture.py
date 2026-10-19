"""Fail-closed source-free numerical-state observations from an ORIGINAL fake JVM."""
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
import worldgen_26_2_noise_constructor_state_capture as state  # noqa: E402


class NoiseConstructorStateTests(unittest.TestCase):
    @staticmethod
    def fake_records() -> str:
        permutation = "".join(f"{i:02x}" for i in range(256))
        lines = []
        for seed in state.SEEDS:
            lines.extend([
                f"A\t{seed}\troot\tamplitudes_0\t3ff0000000000000",
                f"D\t{seed}\troot\tlowestFreqInputFactor\t3fe0000000000000",
                f"P\t{seed}\troot/noiseLevels[0]\tp\t{permutation}",
                f"P\t{seed}\troot/noiseLevels[2]\tp\t{permutation}",
            ])
        return "\n".join(lines)

    def test_canonical_seeds_and_strict_state_record_shape(self):
        self.assertEqual(len(state.SEEDS), 5)
        self.assertEqual(state.SEEDS, (
            "0x0000000000000000", "0x0000000000000001",
            "0xffffffffffffffff", "0x8000000000000000",
            "0x9e3779b97f4a7c15",
        ))
        observed = state.parse_records(self.fake_records(), state.SEEDS)
        self.assertEqual(len(observed), 5)
        self.assertTrue(all(len(x["records"]) == 4 for x in observed))
        self.assertEqual(observed[0]["records"][1]["value"], "3fe0000000000000")
        self.assertEqual(observed[0]["records"][2]["kind"], "P")

    def test_invalid_state_records_reject_before_any_admission(self):
        source = self.fake_records()
        cases = [
            source.replace("3fe0000000000000", "3fe0", 1),
            source.replace("\tamplitudes_0\t", "\t../../garbage\t", 1),
            source.replace("\tamplitudes_0\t", "\tnoise_no_amp\t", 1).replace("\tA\t", "\tD\t", 1),
            source.replace("\tp\t00010203", "\tp\tzzzz0203", 1),
            source.replace("\tp\t00010203", "\tp\t00000203", 1),
            source.replace("P\t", "X\t", 1),
            source.replace("0xffffffffffffffff", "0x4444444444444444", 1),
        ]
        # The mutated "noise_no_amp" label is still valid, so remove a real
        # amplitude record instead to test missing typed scalar coverage.
        cases[2] = "\n".join(line for line in source.splitlines() if not line.startswith("A\t"))
        for case in cases:
            with self.subTest(case=case[:40]), self.assertRaises(state.StateCaptureError):
                state.parse_records(case, state.SEEDS)
        with self.assertRaisesRegex(state.StateCaptureError, "incomplete"):
            state.parse_records("\n".join(source.splitlines()[:4]), state.SEEDS)
        with self.assertRaisesRegex(state.StateCaptureError, "excessive"):
            state.parse_records((source + "\n") * 90, state.SEEDS)

    def make_family_oracle(self, stage: str) -> dict:
        methods = {
            name: {"owner": owner, "signature": signature, "body_sha256": sha}
            for name, (owner, signature, sha) in state.family.EXPECTED[stage].items()
        }
        return {
            "schema": 1, "kind": state.family.KIND, "minecraft": "26.2",
            "protocol": 776, "data_version": 4903,
            "source_archive_sha256": "a" * 64,
            "official_server_sha256": "b" * 64,
            "stage": stage, "method_body_sha256": methods["get_value_3"]["body_sha256"],
            "source_text_included": False, "independent_var_sem_admitted": False,
            "production_worldgen_enabled": False,
            "profile": dict(state.family.PROFILE), "source_methods": methods,
            "vectors": [dict(item, value_bits="0x8000000000000000")
                        for item in state.improved.probes()],
        }

    def test_pinned_reference_and_exclusive_source_free_state(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            lock = root / "vanilla.toml"
            lock.write_text(
                f'minecraft = "26.2"\nprotocol = 776\ndata_version = 4903\n'
                f'[source]\narchive_sha256 = "{"a" * 64}"\n'
                f'[runtime]\nserver_sha256 = "{"b" * 64}"\n', encoding="utf-8",
            )
            for stage in state.family.STAGES:
                reference = root / f"reference-{stage}.json"
                reference.write_text(json.dumps(self.make_family_oracle(stage)), encoding="utf-8")
                target = root / f"observed-{stage}.json"
                conn = mock.MagicMock()
                samples = state.parse_records(self.fake_records(), state.SEEDS)
                with mock.patch.object(state.vanilla_atlas, "connect_db", return_value=conn), \
                     mock.patch.object(state.source_probe, "require_pinned_source", return_value="a" * 64), \
                     mock.patch.object(state.family, "bound_methods",
                                       return_value=self.make_family_oracle(stage)["source_methods"]), \
                     mock.patch.object(state.official, "sha256_file", return_value="b" * 64), \
                     mock.patch.object(state, "run_official_state", return_value=samples) as bridge:
                    result = state.capture(
                        source=root / "zip", db=root / "db", lock=lock,
                        server=root / "jar", reference=reference, output=target,
                    )
                    self.assertEqual(result["seeds"], 5)
                    self.assertEqual(result["records"], 20)
                    bridge.assert_called_once()
                    self.assertTrue(conn.close.called)
                    content = json.loads(target.read_text(encoding="utf-8"))
                    self.assertFalse(content["independent_var_sem_admitted"])
                    self.assertFalse(content["production_worldgen_enabled"])
                    self.assertFalse(content["source_text_included"])
                    self.assertEqual(content["stage"], stage)
                    self.assertEqual(len(content["samples"]), 5)
                    with self.assertRaisesRegex(ValueError, "already exists"):
                        state.capture(
                            source=root / "zip", db=root / "db", lock=lock,
                            server=root / "jar", reference=reference, output=target,
                        )
                changed = json.loads(reference.read_text(encoding="utf-8"))
                changed["profile"]["first_octave"] = -2
                reference.write_text(json.dumps(changed), encoding="utf-8")
                with mock.patch.object(state.vanilla_atlas, "connect_db") as no_db:
                    with self.assertRaises(state.family.CaptureError):
                        state.capture(
                            source=root / "zip", db=root / "db", lock=lock,
                            server=root / "jar", reference=reference, output=root / "no.json",
                        )
                    no_db.assert_not_called()

    @unittest.skipUnless(shutil.which("java") and shutil.which("javac"), "JDK absent")
    def test_actual_reflective_transport_against_original_synthetic_stateful_jvm(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            src = root / "src"
            java_sources = {
                "net/minecraft/util/RandomSource.java": """
package net.minecraft.util;
public interface RandomSource {
  long seed();
  static RandomSource create(long seed) { return () -> seed; }
}
""",
                "it/unimi/dsi/fastutil/doubles/DoubleList.java": """
package it.unimi.dsi.fastutil.doubles;
public interface DoubleList {
  int size();
  double getDouble(int index);
}
""",
                "net/minecraft/world/level/levelgen/synth/ImprovedNoise.java": """
package net.minecraft.world.level.levelgen.synth;
public final class ImprovedNoise {
  private final double xo=0.0, yo=-0.0, zo=1.0;
  private final byte[] p=new byte[256];
  public ImprovedNoise() {
    for(int i=0;i<256;i++) p[i]=(byte)i;
  }
}
""",
                "net/minecraft/world/level/levelgen/synth/PerlinNoise.java": """
package net.minecraft.world.level.levelgen.synth;
import net.minecraft.util.RandomSource;
import it.unimi.dsi.fastutil.doubles.DoubleList;
public final class PerlinNoise {
  private final double lowestFreqInputFactor=0.125, lowestFreqValueFactor=0.25;
  private final int firstOctave=-3;
  private final DoubleList amplitudes=new ToyAmplitudes();
  private final ImprovedNoise[] noiseLevels=new ImprovedNoise[4];
  private static final class ToyAmplitudes implements DoubleList {
    public int size(){ return 4; }
    public double getDouble(int i) {return new double[]{1.0,0.0,0.5,1.0}[i];}
  }
  private PerlinNoise(RandomSource random) {
    noiseLevels[0]=new ImprovedNoise();
    noiseLevels[2]=new ImprovedNoise();
    noiseLevels[3]=new ImprovedNoise();
  }
  public static PerlinNoise create(RandomSource r,int octave,double first,double... rest) {
    if(octave!=-3||first!=1.0||rest.length!=3||rest[1]!=0.5) throw new IllegalStateException();
    return new PerlinNoise(r);
  }
}
""",
                "net/minecraft/world/level/levelgen/synth/NormalNoise.java": """
package net.minecraft.world.level.levelgen.synth;
import net.minecraft.util.RandomSource;
public final class NormalNoise {
  private final double valueFactor=1.0181268882175227;
  private final PerlinNoise first, second;
  private NormalNoise(RandomSource r) {
    first=PerlinNoise.create(r,-3,1.0,0.0,0.5,1.0);
    second=PerlinNoise.create(r,-3,1.0,0.0,0.5,1.0);
  }
  public static NormalNoise create(RandomSource r,int octave,double... amplitudes) {
    if(octave!=-3||amplitudes.length!=4) throw new IllegalStateException();
    return new NormalNoise(r);
  }
}
""",
            }
            for name, text in java_sources.items():
                path = src / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(text, encoding="utf-8")
            classes = root / "classes"
            compiled = subprocess.run(
                ["javac", "-d", str(classes), *[str(src / n) for n in java_sources]],
                text=True, capture_output=True, check=False, timeout=30,
            )
            self.assertEqual(compiled.returncode, 0, compiled.stderr)
            for stage in state.family.STAGES:
                with mock.patch.object(state.official, "extract_classpath", return_value=[classes]):
                    samples = state.run_official_state(root / "toy.jar", stage, timeout=30)
                self.assertEqual(len(samples), 5)
                for sample in samples:
                    rows = sample["records"]
                    expect_perm = 3 if stage == "perlin_noise" else 6
                    self.assertEqual(sum(r["kind"] == "P" for r in rows), expect_perm)
                    self.assertIn("8000000000000000", [r["value"] for r in rows if r["kind"] == "D"])
                    self.assertTrue(any(r["kind"] == "Z" for r in rows))
                    self.assertTrue(any(r["kind"] == "A" for r in rows))


if __name__ == "__main__":
    unittest.main()
