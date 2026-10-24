"""Sealed 26th IntervalSelect source fields and 27th genuine list/input transport."""
from __future__ import annotations

import contextlib
import io
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import worldgen_26_2_stock_final_density_twenty_seventh_layer as owner  # noqa: E402
import worldgen_26_2_stock_finaldensity_twenty_sixth_declarations_receipt as receipt  # noqa: E402
import test_worldgen_26_2_stock_final_density_twenty_sixth_layer as previous_test  # noqa: E402


class OriginalTwentySeventhIntervalListTests(unittest.TestCase):
    def frames(self, *, alter_old: bool = False) -> str:
        old = owner.prior_25.load()
        lines = ["non-source stderr transport"]
        typ = owner.CLASS + "DensityFunctions$Noise"
        const = owner.CLASS + "DensityFunctions$Constant"
        for group, seed in enumerate(owner.FINAL.SEEDS):
            lines.append("|".join((
                owner.HEAD, str(group), seed,
                typ, "0x0000000000000000,0x3ff0000000000000", const + "," + typ,
                typ, "0xbff0000000000000", typ + "," + const,
            )))
            for j in range(32):
                i = 32 * group + j
                a, b = old[i]
                if alter_old and i == 0:
                    a = "0000000000000000"
                lines.append("|".join((
                    owner.VALUE, str(i),
                    "3fe0000000000000", "bfe0000000000000", a, b,
                )))
            lines.append("|".join((owner.END, str(group), "32")))
        return "\n".join(lines) + "\n"

    def report(self) -> dict:
        prior = previous_test.Actual25thABSAnd26thIntervalSourceTests().report()
        shapes, vectors = owner.parse_output(self.frames())
        prior["kind"] = owner.KIND
        prior["shapes"] = shapes
        prior["vectors"] = vectors
        prior.pop("new_twenty_sixth_two_interval_declared_shapes_observed")
        prior.pop("interval_declarations_candidate_telemetry")
        prior["new_twenty_seventh_two_interval_input_lists_observed"] = True
        prior["interval_input_lists_candidate_telemetry"] = owner.candidate_telemetry(shapes,vectors)
        prior["prior_twenty_sixth_report_sha256"] = receipt.REPORT_SHA256
        prior.update({g: False for g in owner.GATES})
        return prior

    def test_previous_actual_original_26th_fields_are_exactly_anchored(self):
        self.assertEqual(receipt.REPORT_BYTES, 39040)
        self.assertEqual(receipt.REPORT_SHA256,
            "ada7937510777d744d612de17486981a485c1714863cffb2e98096dc069cfb44")
        self.assertEqual(receipt.DECLARED_FIELDS,
            "functions~java.util.List;input~net.minecraft.world.level.levelgen.DensityFunction;"
            "thresholds~it.unimi.dsi.fastutil.doubles.DoubleList")
        self.assertEqual(receipt.TELEMETRY["new_numeric_ieee_words"], 0)
        self.assertEqual(len(receipt.old.load()), 128)

    def test_synthetic_complete_27th_two_new_inputs_and_old_original_anchors(self):
        shapes, vectors = owner.parse_output(self.frames())
        self.assertEqual((len(shapes), len(vectors)), (4, 128))
        self.assertEqual(owner.NEW_FIELDS, ("first_selector_input_bits","second_selector_input_bits"))
        self.assertEqual(owner.OLD_FIELDS, ("old_first_interval_bits","old_second_interval_bits"))
        self.assertEqual(owner.candidate_telemetry(shapes,vectors)["genuinely_new_selector_ieee_words"], 256)
        owner.validate(self.report())
        self.assertFalse(any(self.report()[g] for g in owner.GATES))

    def test_changed_old_original_values_lists_and_source_gates_are_rejected(self):
        with self.assertRaises(owner.TwentySeventhLayerError):
            owner.parse_output(self.frames(alter_old=True))
        for mutant in (
            lambda s: s.replace("0x3ff0000000000000", "not-hex", 1),
            lambda s: s.replace(owner.CLASS + "DensityFunctions$Noise", "invalid class name", 1),
            lambda s: s.replace(owner.HEAD, "OTHER_FRAME", 1),
        ):
            with self.subTest(mutant=str(mutant)), self.assertRaises(owner.TwentySeventhLayerError):
                owner.parse_output(mutant(self.frames()))
        for key in (
            "prior_twenty_sixth_report_sha256",
            "twenty_seventh_all_input_interval_selection_admitted",
        ):
            report=self.report()
            report[key]=True if isinstance(report[key], bool) else "tampered"
            with self.subTest(key=key), self.assertRaises(owner.TwentySeventhLayerError):
                owner.validate(report)

    def test_original_26th_private_receipt_rejects_unpinned_data(self):
        with tempfile.TemporaryDirectory() as td:
            path=Path(td)/"made-up-private.json"
            path.write_text(json.dumps(previous_test.Actual25thABSAnd26thIntervalSourceTests().report()))
            with self.assertRaises(receipt.OriginalTwentySixthReceiptError):
                receipt.validate_original(path)

    def test_private_original_27th_absent_fails_closed(self):
        with tempfile.TemporaryDirectory() as td:
            base=Path(td)
            output=base/"not-created.json"
            with contextlib.redirect_stderr(io.StringIO()):
                result=owner.main([
                    "--source",str(base/"absent-source.zip"),
                    "--db",str(base/"absent.sqlite"),
                    "--lock",str(base/"absent.lock"),
                    "--server-jar",str(base/"absent-jar.bin"),
                    "--output",str(output),
                ])
            self.assertEqual(result, 2)
            self.assertFalse(output.exists())

    @unittest.skipUnless(shutil.which("javac"),"javac required")
    def test_source_free_complete_twenty_seventh_java_bridge_compiles(self):
        o=probe
        f=o.eighteenth.seventeenth.sixteenth.fifteenth.fourteenth.thirteenth.twelfth.eleventh.tenth.ninth.eighth.seventh.sixth.fifth
        sources=(
            f.fourth.third.second.final.roots.BASE_BRIDGE,
            f.fourth.third.second.final.JAVA_SOURCE,
            f.fourth.third.second.root.JAVA_SOURCE,
            f.fourth.third.second.inner.JAVA_SOURCE,
            f.fourth.third.second.JAVA_SOURCE,
            f.fourth.third.JAVA_SOURCE,
            f.fourth.JAVA_SOURCE,
            f.JAVA_SOURCE,
            o.eighteenth.seventeenth.sixteenth.fifteenth.fourteenth.thirteenth.twelfth.eleventh.tenth.ninth.eighth.seventh.sixth.JAVA_SOURCE,
            o.eighteenth.seventeenth.sixteenth.fifteenth.fourteenth.thirteenth.twelfth.eleventh.tenth.ninth.eighth.seventh.JAVA_SOURCE,
            o.eighteenth.seventeenth.sixteenth.fifteenth.fourteenth.thirteenth.twelfth.eleventh.tenth.ninth.eighth.JAVA_SOURCE,
            o.eighteenth.seventeenth.sixteenth.fifteenth.fourteenth.thirteenth.twelfth.eleventh.tenth.ninth.JAVA_SOURCE,
            o.eighteenth.seventeenth.sixteenth.fifteenth.fourteenth.thirteenth.twelfth.eleventh.tenth.JAVA_SOURCE,
            o.eighteenth.seventeenth.sixteenth.fifteenth.fourteenth.thirteenth.twelfth.eleventh.JAVA_SOURCE,
            o.eighteenth.seventeenth.sixteenth.fifteenth.fourteenth.thirteenth.twelfth.JAVA_SOURCE,
            o.eighteenth.seventeenth.sixteenth.fifteenth.fourteenth.thirteenth.JAVA_SOURCE,
            o.eighteenth.seventeenth.sixteenth.fifteenth.fourteenth.JAVA_SOURCE,
            o.eighteenth.seventeenth.sixteenth.fifteenth.JAVA_SOURCE,
            o.eighteenth.seventeenth.sixteenth.JAVA_SOURCE,
            o.eighteenth.seventeenth.JAVA_SOURCE,
            o.eighteenth.JAVA_SOURCE,
            o.previous_24.JAVA_SOURCE,
            o.previous.JAVA_SOURCE,
            o.previous_26.JAVA_SOURCE,
            o.JAVA_SOURCE,
        )
        with tempfile.TemporaryDirectory() as td:
            p=subprocess.run(["javac","-encoding","UTF-8","-d",td,
                              *(str(x) for x in sources)],
                             capture_output=True,text=True,timeout=90,check=False)
            self.assertEqual(p.returncode,0,p.stderr)


if __name__ == "__main__":
    unittest.main()
