"""Source-free twenty-second actual NoiseHolder/registry/scale observation tests."""
from __future__ import annotations

import contextlib
import io
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import worldgen_26_2_stock_final_density_twenty_second_layer as owner  # noqa: E402


class OriginalTwentySecondNoiseStructureTests(unittest.TestCase):
    def frames(self) -> str:
        old = owner.prior_leaf.load()
        shape = (
            owner.CLASS + "Noise", "3ff0000000000000", "3ff0000000000000",
            "net.minecraft.world.level.levelgen.DensityFunction$NoiseHolder",
            "net.minecraft.core.Holder$Reference", "minecraft:erosion",
            "net.minecraft.world.level.levelgen.synth.NormalNoise",
        )
        lines = ["unrelated original boot log"]
        for group, seed in enumerate(owner.FINAL.SEEDS):
            lines.append("|".join((owner.HEAD, str(group), seed, *shape)))
            for j in range(32):
                i = group * 32 + j
                lines.append("|".join((owner.VALUE, str(i), old[i])))
            lines.append("|".join((owner.END, str(group), "32")))
        return "\n".join(lines) + "\n"

    def methods(self) -> dict:
        items = {}
        for name in ("ap2_compute", "holder_holder_compute"):
            cls, sig, body, normalized = owner.ROOT.frozen_final.METHODS[name]
            items[name] = {
                "owner": cls, "signature": sig, "body_sha256": body,
                "normalized_sha256": normalized, "reviewed": False,
            }
        items["mapped_delegate_compute"] = {
            "owner": owner.ROOT.PURE_TRANSFORMER,
            "signature": "compute(final DensityFunction . FunctionContext context)",
            "body_sha256": owner.ROOT.PURE_COMPUTE_SHA256,
            "normalized_sha256": "a" * 64,
            "reviewed": False,
        }
        return items

    def report(self) -> dict:
        shapes, vectors = owner.parse_output(self.frames())
        f = owner.twentieth.nineteenth.seventeenth_fixture
        return {
            "schema": 1, "kind": owner.KIND, "minecraft": "26.2",
            "protocol": 776, "data_version": 4903,
            "source_archive_sha256": owner.FINAL.frozen.SOURCE_SHA256,
            "official_server_sha256": owner.FINAL.frozen.SERVER_SHA256,
            "prior_thirteenth_fixture_sha256": f.prior.prior.SHA256,
            "prior_sixteenth_fixture_sha256": f.prior.SHA256,
            "prior_seventeenth_fixture_sha256": f.SHA256,
            "prior_eighteenth_override_fixture_sha256": owner.prior_nineteenth.prior.SHA256,
            "prior_nineteenth_fixture_sha256": owner.prior_nineteenth.SHA256,
            "prior_twentieth_fixture_sha256": owner.prior.SHA256,
            "prior_twenty_first_fixture_sha256": owner.prior_leaf.SHA256,
            "prior_thirteenth_report_sha256": f.prior.prior.REPORT_SHA256,
            "prior_fourteenth_report_sha256": f.prior.receipt.owner.previous.REPORT_SHA256,
            "prior_fifteenth_report_sha256": f.prior.receipt.REPORT_SHA256,
            "prior_sixteenth_report_sha256": f.prior.REPORT_SHA256,
            "prior_seventeenth_report_sha256": f.REPORT_SHA256,
            "prior_eighteenth_report_sha256": owner.prior_nineteenth.prior.REPORT_SHA256,
            "prior_nineteenth_report_sha256": owner.prior_nineteenth.REPORT_SHA256,
            "prior_twentieth_report_sha256": owner.prior.REPORT_SHA256,
            "prior_twenty_first_report_sha256": owner.prior_leaf.REPORT_SHA256,
            "source_methods": self.methods(),
            "world_seeds": list(owner.FINAL.SEEDS),
            "point_count_per_seed": 32,
            "sample_context": "DensityFunction$SinglePointContext",
            "original_stock_registry_used": True,
            "original_twenty_second_real_noise_leaf_structure_observed": True,
            "source_text_included": False,
            "shapes": shapes, "vectors": vectors,
            "noise_structure_candidate_telemetry": owner.candidate_telemetry(shapes, vectors),
            **{gate: False for gate in owner.GATES},
        }

    def test_original_old_noise_anchor_128_no_new_leaf_ieee_words(self):
        shape, rows = owner.parse_output(self.frames())
        self.assertEqual(len(shape), 4)
        self.assertEqual(len(rows), 128)
        self.assertEqual(shape[0]["noise_node_class"], owner.CLASS + "Noise")
        self.assertEqual(shape[0]["noise_parameters_key"], "minecraft:erosion")
        self.assertEqual(rows[0]["old_twenty_first_noise_bits"],
                         "0x3fe48f11c0c8841c")
        self.assertEqual(owner.NEW_FIELDS, ())
        self.assertEqual(owner.candidate_telemetry(shape, rows)["genuinely_new_ieee_words"], 0)
        owner.validate(self.report())

    def test_source_ancestry_and_all_gates_fail_closed(self):
        frames = self.frames().splitlines()
        invalid = [
            frames[:-1], frames + [frames[-1]],
            [frames[0], frames[1].replace("DensityFunctions$Noise", "DensityFunctions$Ap2"), *frames[2:]],
            [frames[0], frames[1].replace("|3ff0000000000000|", "|7ff0000000000000|", 1), *frames[2:]],
            [frames[0], frames[1].replace("minecraft:erosion", "nonstock-key"), *frames[2:]],
            [frames[0], frames[1].replace("Holder$Reference", "Holder$Invalid"), *frames[2:]],
        ]
        old = frames[2].split("|")
        old[2] = "0000000000000000"
        invalid.append([*frames[:2], "|".join(old), *frames[3:]])
        for i, lines in enumerate(invalid):
            with self.subTest(frame=i), self.assertRaises(owner.TwentySecondLayerError):
                owner.parse_output("\n".join(lines))
        keys = (
            "source_archive_sha256", "official_server_sha256",
            "prior_thirteenth_fixture_sha256", "prior_sixteenth_fixture_sha256",
            "prior_seventeenth_fixture_sha256", "prior_eighteenth_override_fixture_sha256",
            "prior_nineteenth_fixture_sha256", "prior_twentieth_fixture_sha256",
            "prior_twenty_first_fixture_sha256", "prior_thirteenth_report_sha256",
            "prior_fourteenth_report_sha256", "prior_fifteenth_report_sha256",
            "prior_sixteenth_report_sha256", "prior_seventeenth_report_sha256",
            "prior_eighteenth_report_sha256", "prior_nineteenth_report_sha256",
            "prior_twentieth_report_sha256", "prior_twenty_first_report_sha256",
            *owner.GATES,
        )
        for key in keys:
            changed = self.report()
            changed[key] = not changed[key] if isinstance(changed[key], bool) else "altered"
            with self.subTest(pin=key), self.assertRaises(owner.TwentySecondLayerError):
                owner.validate(changed)

    def test_missing_official_source_fails_without_output(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td)
            err = io.StringIO()
            with contextlib.redirect_stderr(err):
                result = owner.main([
                    "--source", str(p / "source.zip"), "--db", str(p / "atlas.sqlite"),
                    "--lock", str(p / "lock.toml"),
                    "--server-jar", str(p / "missing.jar"),
                    "--output", str(p / "must-not-exist.json"),
                ])
            self.assertEqual(result, 2)
            self.assertFalse((p / "must-not-exist.json").exists())
            self.assertIn("TWENTY_SECOND LAYER OPEN", err.getvalue())

    @unittest.skipUnless(shutil.which("javac"), "source-free javac required")
    def test_twenty_second_full_source_bridge_compiles(self):
        f = owner.twentieth.nineteenth.eighteenth.seventeenth.sixteenth.fifteenth.fourteenth.thirteenth.twelfth.eleventh.tenth.ninth.eighth.seventh.sixth.fifth
        sources = (
            f.fourth.third.second.final.roots.BASE_BRIDGE,
            f.fourth.third.second.final.JAVA_SOURCE,
            f.fourth.third.second.root.JAVA_SOURCE,
            f.fourth.third.second.inner.JAVA_SOURCE,
            f.fourth.third.second.JAVA_SOURCE,
            f.fourth.third.JAVA_SOURCE,
            f.fourth.JAVA_SOURCE,
            f.JAVA_SOURCE,
            owner.twentieth.nineteenth.eighteenth.seventeenth.sixteenth.fifteenth.fourteenth.thirteenth.twelfth.eleventh.tenth.ninth.eighth.seventh.sixth.JAVA_SOURCE,
            owner.twentieth.nineteenth.eighteenth.seventeenth.sixteenth.fifteenth.fourteenth.thirteenth.twelfth.eleventh.tenth.ninth.eighth.seventh.JAVA_SOURCE,
            owner.twentieth.nineteenth.eighteenth.seventeenth.sixteenth.fifteenth.fourteenth.thirteenth.twelfth.eleventh.tenth.ninth.eighth.JAVA_SOURCE,
            owner.twentieth.nineteenth.eighteenth.seventeenth.sixteenth.fifteenth.fourteenth.thirteenth.twelfth.eleventh.tenth.ninth.JAVA_SOURCE,
            owner.twentieth.nineteenth.eighteenth.seventeenth.sixteenth.fifteenth.fourteenth.thirteenth.twelfth.eleventh.tenth.JAVA_SOURCE,
            owner.twentieth.nineteenth.eighteenth.seventeenth.sixteenth.fifteenth.fourteenth.thirteenth.twelfth.eleventh.JAVA_SOURCE,
            owner.twentieth.nineteenth.eighteenth.seventeenth.sixteenth.fifteenth.fourteenth.thirteenth.twelfth.JAVA_SOURCE,
            owner.twentieth.nineteenth.eighteenth.seventeenth.sixteenth.fifteenth.fourteenth.thirteenth.JAVA_SOURCE,
            owner.twentieth.nineteenth.eighteenth.seventeenth.sixteenth.fifteenth.fourteenth.JAVA_SOURCE,
            owner.twentieth.nineteenth.eighteenth.seventeenth.sixteenth.fifteenth.JAVA_SOURCE,
            owner.twentieth.nineteenth.eighteenth.seventeenth.sixteenth.JAVA_SOURCE,
            owner.twentieth.nineteenth.eighteenth.seventeenth.JAVA_SOURCE,
            owner.twentieth.nineteenth.eighteenth.JAVA_SOURCE,
            owner.twentieth.nineteenth.JAVA_SOURCE,
            owner.twentieth.JAVA_SOURCE,
            owner.predecessor.JAVA_SOURCE,
            owner.JAVA_SOURCE,
        )
        with tempfile.TemporaryDirectory() as td:
            result = subprocess.run(
                ["javac", "-encoding", "UTF-8", "-d", td,
                 *(str(path) for path in sources)],
                capture_output=True, text=True, timeout=90, check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr)


if __name__ == "__main__":
    unittest.main()
