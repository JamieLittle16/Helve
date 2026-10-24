"""25th 26.2 original source Mapped/Mapped numeric and structural transport."""
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
import worldgen_26_2_stock_final_density_twenty_fifth_layer as owner  # noqa: E402
import test_worldgen_26_2_stock_final_density_twenty_fourth_layer as previous_test  # noqa: E402


class OriginalTwoMappedRealChildrenSourceTests(unittest.TestCase):
    def frames(self, *, change_old: bool = False) -> str:
        old = owner.prior_fixture.load()
        lines = ["not-a-JVM-record"]
        for group, seed in enumerate(owner.FINAL.SEEDS):
            lines.append("|".join((
                owner.HEAD, str(group), seed,
                owner.CLASS + "Mapped$Type", "ABS", owner.CLASS + "Noise",
                owner.CLASS + "Mapped$Type", "SQUEEZE", owner.CLASS + "Constant",
            )))
            for j in range(32):
                i = group * 32 + j
                first, second = old[i]
                if change_old and i == 0:
                    first = "0000000000000000"
                lines.append("|".join((
                    owner.VALUE, str(i),
                    "3ff0000000000000", "0000000000000000",
                    first, second,
                )))
            lines.append("|".join((owner.END, str(group), "32")))
        return "\n".join(lines)+"\n"

    def report(self) -> dict:
        report = previous_test.ActualOriginalNineteenthLeftSourceProbeTests().report()
        shapes, vectors = owner.parse_output(self.frames())
        report["kind"] = owner.KIND
        report["shapes"] = shapes
        report["vectors"] = vectors
        report.pop("new_twenty_fourth_nineteenth_left_ap2_children_observed")
        report.pop("left_ap2_arithmetic_candidate_telemetry")
        report["new_twenty_fifth_two_real_mapped_inputs_observed"] = True
        report["mapped_inputs_candidate_telemetry"] = owner.candidate_telemetry(shapes, vectors)
        report["prior_twenty_fourth_fixture_sha256"] = owner.prior_fixture.FIXTURE_SHA256
        report["prior_twenty_fourth_report_sha256"] = owner.prior_fixture.REPORT_SHA256
        report.update({gate: False for gate in owner.GATES})
        return report

    def test_real_twenty_fourth_new_only_fixture_sha_and_max_winner_coverage(self):
        self.assertEqual(owner.prior_fixture.FIXTURE_BYTES, 4352)
        self.assertEqual(owner.prior_fixture.FIXTURE_SHA256,
                         "dc44a67d9ce942d5591cdf02cef388dedabedbe4b85e5c9d27f729e4e42fe343")
        self.assertEqual(owner.prior_fixture.REPORT_BYTES, 45989)
        self.assertEqual(owner.prior_fixture.REPORT_SHA256,
                         "3c92faf8f74d8d6f4f45fa39e6d07a5dbfe9dc6ba9e7406a8e78e0e3afbe545f")
        self.assertEqual(len(owner.prior_fixture.load()), 128)
        self.assertEqual(owner.prior_fixture.TELEMETRY["arithmetic_candidate_mismatches"], 0)
        self.assertEqual(owner.prior_fixture.SHAPE["left_ap2_op"], "MAX")

    def test_25th_real_mapped_child_frames_and_source_provenance(self):
        shapes, rows = owner.parse_output(self.frames())
        self.assertEqual((len(shapes), len(rows)), (4, 128))
        self.assertEqual(owner.NEW_FIELDS, ("first_mapped_input_bits", "second_mapped_input_bits"))
        self.assertEqual(owner.OLD_FIELDS, ("old_first_mapped_bits", "old_second_mapped_bits"))
        self.assertEqual(owner.candidate_telemetry(shapes, rows)["genuinely_new_sample_ieee_words"], 256)
        owner.validate(self.report())
        self.assertFalse(any(self.report()[gate] for gate in owner.GATES))

    def test_old_mapped_anchors_bad_enum_class_and_gates_fail_closed(self):
        with self.assertRaises(owner.TwentyFifthLayerError):
            owner.parse_output(self.frames(change_old=True))
        for old,new in (
            ("DensityFunctions$Mapped$Type", "DensityFunctions$Ap2$Type"),
            ("|ABS|", "|unbounded-invalid|"),
            (owner.VALUE, "unexpected-value"),
        ):
            with self.subTest(old=old),self.assertRaises(owner.TwentyFifthLayerError):
                owner.parse_output(self.frames().replace(old,new,1))
        for k in (
            "twenty_fifth_all_input_mapped_laws_admitted",
            "prior_twenty_fourth_fixture_sha256",
            "prior_twenty_fourth_report_sha256",
        ):
            report=self.report()
            report[k]=True if isinstance(report[k],bool) else "modified"
            with self.subTest(k=k),self.assertRaises(owner.TwentyFifthLayerError):
                owner.validate(report)

    def test_original_stock_absent_fails_closed(self):
        with tempfile.TemporaryDirectory() as td:
            dest=Path(td)
            output=dest/"uncreated.json"
            with contextlib.redirect_stderr(io.StringIO()):
                result=owner.main([
                    "--source",str(dest/"no_source.zip"),
                    "--db",str(dest/"no_atlas.sqlite"),
                    "--lock",str(dest/"no.lock"),
                    "--server-jar",str(dest/"no_jar.bin"),
                    "--output",str(output),
                ])
            self.assertEqual(result,2)
            self.assertFalse(output.exists())

    @unittest.skipUnless(shutil.which("javac"), "source-free javac required")
    @unittest.skipUnless(shutil.which("javac"), "source-free javac required")
    def test_source_free_twenty_fifth_complete_bridge_compiles(self):
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
            owner.previous.JAVA_SOURCE,
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
