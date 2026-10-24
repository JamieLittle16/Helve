"""Actual 26.2 nineteenth LEFT Ap2 sibling source-owned 24th transport."""
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
import worldgen_26_2_stock_final_density_twenty_fourth_layer as owner  # noqa: E402
import test_worldgen_26_2_stock_final_density_nineteenth_layer as previous_test  # noqa: E402


class ActualOriginalNineteenthLeftSourceProbeTests(unittest.TestCase):
    def frames(self, *, corrupt: bool = False) -> str:
        old = owner.old_nineteenth.load()
        lines = ["non-frame original logging"]
        for group, seed in enumerate(owner.FINAL.SEEDS):
            lines.append("|".join((
                owner.HEAD, str(group), seed,
                owner.CLASS + "TwoArgumentSimpleFunction$Type",
                "ADD", owner.CLASS + "Constant", owner.CLASS + "Noise"
            )))
            for j in range(32):
                index = group * 32 + j
                old_left = old[index][0]
                if corrupt and index == 0:
                    old_left = "0000000000000000"
                lines.append("|".join((
                    owner.VALUE, str(index), old[index][0],
                    "0000000000000000", old_left
                )))
            lines.append("|".join((owner.END, str(group), "32")))
        return "\n".join(lines) + "\n"

    def report(self) -> dict:
        previous = previous_test.NineteenthOriginalAp2SourceTransport().report()
        shapes, vectors = owner.parse_output(self.frames())
        previous["kind"] = owner.KIND
        previous["shapes"] = shapes
        previous["vectors"] = vectors
        previous.pop("new_nineteenth_actual_clampwrapped_ap2_children_observed")
        previous.pop("ap2_arithmetic_candidate_telemetry")
        previous["new_twenty_fourth_nineteenth_left_ap2_children_observed"] = True
        previous["left_ap2_arithmetic_candidate_telemetry"] = owner.candidate_telemetry(shapes, vectors)
        previous["prior_nineteenth_two_new_fixture_sha256"] = owner.old_nineteenth.SHA256
        previous["prior_nineteenth_report_sha256"] = owner.old_nineteenth.REPORT_SHA256
        previous["prior_twenty_third_report_sha256"] = owner.previous_parameters.REPORT_SHA256
        previous.update({name: False for name in owner.GATES})
        return previous

    def test_original_nineteenth_left_fixture_is_strict_independent_anchor(self):
        rows = owner.old_nineteenth.load()
        self.assertEqual(len(rows), 128)
        self.assertEqual(owner.NEW_FIELDS,
                         ("left_ap2_first_child_bits", "left_ap2_second_child_bits"))
        self.assertEqual(owner.OLD_FIELDS, ("old_nineteenth_left_bits",))
        self.assertEqual(owner.previous_parameters.FIRST_OCTAVE, "-8")
        self.assertEqual(owner.previous_parameters.AMPLITUDES, "3ff0000000000000")

    def test_two_new_128_children_and_old_parent_transport(self):
        shapes, vectors = owner.parse_output(self.frames())
        self.assertEqual((len(shapes), len(vectors)), (4, 128))
        self.assertEqual(owner.candidate_telemetry(shapes, vectors)["original_bounded_points"], 128)
        owner.validate(self.report())
        self.assertTrue(all(self.report()[gate] is False for gate in owner.GATES))

    def test_any_old_jvm_anchor_drift_is_rejected(self):
        with self.assertRaises(owner.TwentyFourthLayerError):
            owner.parse_output(self.frames(corrupt=True))
        for token in (owner.HEAD, owner.VALUE, owner.END):
            with self.subTest(token=token), self.assertRaises(owner.TwentyFourthLayerError):
                owner.parse_output(self.frames().replace(token, "altered", 1))
        changed = self.report()
        changed["twenty_fourth_all_input_left_ap2_law_admitted"] = True
        with self.assertRaises(owner.TwentyFourthLayerError):
            owner.validate(changed)
        changed = self.report()
        changed["prior_nineteenth_report_sha256"] = "0"*64
        with self.assertRaises(owner.TwentyFourthLayerError):
            owner.validate(changed)
        changed = self.report()
        changed["shapes"][0]["left_ap2_op"] = "NOT_OBSERVED"
        with self.assertRaises(owner.TwentyFourthLayerError):
            owner.validate(changed)

    def test_missing_real_stock_source_or_jar_fails_closed(self):
        with tempfile.TemporaryDirectory() as td:
            dest = Path(td)
            output = dest / "should-not-exist.json"
            with contextlib.redirect_stderr(io.StringIO()):
                result = owner.main([
                    "--source", str(dest / "missing-source.zip"),
                    "--db", str(dest / "missing.sqlite"),
                    "--lock", str(dest / "missing.lock"),
                    "--server-jar", str(dest / "missing-server.jar"),
                    "--output", str(output),
                ])
            self.assertEqual(result, 2)
            self.assertFalse(output.exists())

    @unittest.skipUnless(shutil.which("javac"), "source-free javac required")
    def test_source_free_twenty_fourth_complete_bridge_compiles(self):
        f = owner.eighteenth.seventeenth.sixteenth.fifteenth.fourteenth.thirteenth.twelfth.eleventh.tenth.ninth.eighth.seventh.sixth.fifth
        sources = (
            f.fourth.third.second.final.roots.BASE_BRIDGE,
            f.fourth.third.second.final.JAVA_SOURCE,
            f.fourth.third.second.root.JAVA_SOURCE,
            f.fourth.third.second.inner.JAVA_SOURCE,
            f.fourth.third.second.JAVA_SOURCE,
            f.fourth.third.JAVA_SOURCE,
            f.fourth.JAVA_SOURCE,
            f.JAVA_SOURCE,
            owner.eighteenth.seventeenth.sixteenth.fifteenth.fourteenth.thirteenth.twelfth.eleventh.tenth.ninth.eighth.seventh.sixth.JAVA_SOURCE,
            owner.eighteenth.seventeenth.sixteenth.fifteenth.fourteenth.thirteenth.twelfth.eleventh.tenth.ninth.eighth.seventh.JAVA_SOURCE,
            owner.eighteenth.seventeenth.sixteenth.fifteenth.fourteenth.thirteenth.twelfth.eleventh.tenth.ninth.eighth.JAVA_SOURCE,
            owner.eighteenth.seventeenth.sixteenth.fifteenth.fourteenth.thirteenth.twelfth.eleventh.tenth.ninth.JAVA_SOURCE,
            owner.eighteenth.seventeenth.sixteenth.fifteenth.fourteenth.thirteenth.twelfth.eleventh.tenth.JAVA_SOURCE,
            owner.eighteenth.seventeenth.sixteenth.fifteenth.fourteenth.thirteenth.twelfth.eleventh.JAVA_SOURCE,
            owner.eighteenth.seventeenth.sixteenth.fifteenth.fourteenth.thirteenth.twelfth.JAVA_SOURCE,
            owner.eighteenth.seventeenth.sixteenth.fifteenth.fourteenth.thirteenth.JAVA_SOURCE,
            owner.eighteenth.seventeenth.sixteenth.fifteenth.fourteenth.JAVA_SOURCE,
            owner.eighteenth.seventeenth.sixteenth.fifteenth.JAVA_SOURCE,
            owner.eighteenth.seventeenth.sixteenth.JAVA_SOURCE,
            owner.eighteenth.seventeenth.JAVA_SOURCE,
            owner.eighteenth.JAVA_SOURCE,
            owner.JAVA_SOURCE,
        )
        with tempfile.TemporaryDirectory() as td:
            result = subprocess.run(
                ["javac", "-encoding", "UTF-8", "-d", td, *(str(path) for path in sources)],
                capture_output=True, text=True, timeout=90, check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr)


if __name__ == "__main__":
    unittest.main()
