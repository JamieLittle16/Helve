"""Bounded original 26.2 registered spaghetti NoiseParameters structural probe."""
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
sys.path.insert(0, str(Path(__file__).resolve().parent))
import worldgen_26_2_stock_final_density_twenty_third_layer as owner  # noqa: E402
import test_worldgen_26_2_stock_final_density_twenty_second_layer as previous_tests  # noqa: E402


class OriginalTwentyThirdSpaghettiParametersTests(unittest.TestCase):
    def report(self) -> dict:
        # The previous synthetic report is only for transport mutation tests,
        # NEVER a substitute for true JVM-observed spaghetti parameters.
        report = previous_tests.OriginalTwentySecondNoiseStructureTests().report()
        report["kind"] = owner.KIND
        report["prior_twenty_second_report_sha256"] = owner.prior_structure.REPORT_SHA256
        report["original_twenty_third_spaghetti_noise_parameters_observed"] = True
        report["shapes"] = [{
            **shape,
            "noise_parameters_key": "minecraft:spaghetti_3d_thickness",
            "noise_first_octave": "-7",
            "noise_amplitudes_rawbits": "3ff0000000000000,0000000000000000,3fe0000000000000",
        } for shape in report["shapes"]]
        report["parameter_candidate_telemetry"] = owner.candidate_telemetry(
            report["shapes"], report["vectors"]
        )
        report.pop("noise_structure_candidate_telemetry")
        return report

    def frames(self) -> str:
        r = self.report()
        lines = ["unrelated JVM bootstrap logs"]
        for group, shape in enumerate(r["shapes"]):
            lines.append("|".join((owner.HEAD, str(group), shape["world_seed_bits"],
                                   *(shape[k] for k in owner.SHAPE_FIELDS))))
            for j in range(32):
                i = group * 32 + j
                lines.append("|".join((owner.VALUE, str(i),
                                       r["vectors"][i]["old_twenty_first_noise_bits"][2:])))
            lines.append("|".join((owner.END, str(group), "32")))
        return "\n".join(lines) + "\n"

    def test_source_owned_previous_noise_and_bounded_parameters(self):
        r = self.report()
        owner.validate(r)
        shapes, rows = owner.parse_output(self.frames())
        self.assertEqual(len(shapes), 4)
        self.assertEqual(len(rows), 128)
        self.assertEqual(owner.NEW_FIELDS, ())
        self.assertEqual(owner.prior_structure.REPORT_BYTES, 32822)
        self.assertEqual(shapes[0]["noise_parameters_key"], "minecraft:spaghetti_3d_thickness")
        self.assertEqual(shapes[0]["noise_first_octave"], "-7")
        self.assertEqual(len(shapes[0]["noise_amplitudes_rawbits"].split(",")), 3)
        self.assertEqual(owner.candidate_telemetry(shapes, rows)["genuinely_new_sample_ieee_words"], 0)

    def test_invalid_params_synthetic_transport_and_provenance_are_rejected(self):
        lines = self.frames().splitlines()
        substitutions = (
            ("|-7|", "|999|"),
            ("|3ff0000000000000,0000000000000000,3fe0000000000000", "|hello"),
            ("minecraft:spaghetti_3d_thickness", "minecraft:erosion"),
            ("|3ff0000000000000|", "|7ff0000000000000|"),
        )
        for old, new in substitutions:
            self.assertIn(old, lines[1])
            altered = list(lines)
            altered[1] = altered[1].replace(old, new, 1)
            with self.subTest(token=old), self.assertRaises(owner.TwentyThirdLayerError):
                owner.parse_output("\n".join(altered))
        for key in (
            "source_archive_sha256", "official_server_sha256",
            "prior_twenty_first_report_sha256", "prior_twenty_second_report_sha256",
            *owner.GATES,
        ):
            changed = self.report()
            changed[key] = not changed[key] if isinstance(changed[key], bool) else "tampered"
            with self.subTest(provenance=key), self.assertRaises(owner.TwentyThirdLayerError):
                owner.validate(changed)

    def test_missing_original_source_fails_closed_without_side_effect(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td)
            err = io.StringIO()
            with contextlib.redirect_stderr(err):
                result = owner.main([
                    "--source", str(p / "missing.zip"),
                    "--db", str(p / "absent.sqlite"),
                    "--lock", str(p / "absent.lock"),
                    "--server-jar", str(p / "missing.jar"),
                    "--output", str(p / "should-not-exist.json"),
                ])
            self.assertEqual(result, 2)
            self.assertFalse((p / "should-not-exist.json").exists())
            self.assertIn("TWENTY_THIRD LAYER OPEN", err.getvalue())

    @unittest.skipUnless(shutil.which("javac"), "source-free javac required")
    def test_source_free_23rd_jvm_bridge_compiles_with_all_previous_real_observers(self):
        # Reuse exact independent 22nd javac source closure and extend by
        # precisely the new 23rd helper, not a hand-waved source stub.
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
            owner.previous.JAVA_SOURCE,
            owner.JAVA_SOURCE,
        )
        with tempfile.TemporaryDirectory() as td:
            result = subprocess.run(
                ["javac", "-encoding", "UTF-8", "-d", td,
                 *(str(path) for path in sources)],
                capture_output=True, text=True, timeout=90, check=False
            )
            self.assertEqual(result.returncode, 0, result.stderr)


if __name__ == "__main__":
    unittest.main()
