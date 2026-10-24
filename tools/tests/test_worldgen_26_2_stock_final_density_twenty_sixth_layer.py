"""Original 25th ABS/IntervalSelect receipt and 26th structural frontier guards."""
from __future__ import annotations

import contextlib
import io
import json
import hashlib
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import worldgen_26_2_stock_finaldensity_twenty_fifth_layer_fixture as frozen  # noqa: E402
import worldgen_26_2_stock_final_density_twenty_sixth_layer as probe  # noqa: E402
import test_worldgen_26_2_stock_final_density_twenty_fifth_layer as prev_test  # noqa: E402


class Actual25thABSAnd26thIntervalSourceTests(unittest.TestCase):
    FIRST = (
        "input~net.minecraft.world.level.levelgen.DensityFunction;"
        "whenInside~net.minecraft.world.level.levelgen.DensityFunction;"
        "whenOutside~net.minecraft.world.level.levelgen.DensityFunction;"
        "minInclusive~double;maxExclusive~double"
    )
    SECOND = FIRST

    def frames(self, *, mutate_old: bool = False) -> str:
        old = frozen.load()
        lines = ["non-source-message"]
        for group, seed in enumerate(probe.FINAL.SEEDS):
            lines.append("|".join((probe.HEAD,str(group),seed,self.FIRST,self.SECOND)))
            for j in range(32):
                index=group*32+j
                first,second=old[index]
                if mutate_old and index==0:
                    first="0000000000000000"
                lines.append("|".join((probe.VALUE,str(index),first,second)))
            lines.append("|".join((probe.END,str(group),"32")))
        return "\n".join(lines)+"\n"

    def report(self) -> dict:
        report=prev_test.OriginalTwoMappedRealChildrenSourceTests().report()
        shapes,vectors=probe.parse_output(self.frames())
        report["kind"]=probe.KIND
        report["shapes"]=shapes
        report["vectors"]=vectors
        report.pop("new_twenty_fifth_two_real_mapped_inputs_observed")
        report.pop("mapped_inputs_candidate_telemetry")
        report["new_twenty_sixth_two_interval_declared_shapes_observed"]=True
        report["interval_declarations_candidate_telemetry"]=probe.candidate_telemetry(shapes,vectors)
        report["prior_twenty_fifth_fixture_sha256"]=frozen.FIXTURE_SHA256
        report["prior_twenty_fifth_report_sha256"]=frozen.REPORT_SHA256
        report.update({g:False for g in probe.GATES})
        return report

    def test_original_25th_pins_and_all_256_genuine_abs_outputs(self):
        self.assertEqual(frozen.REPORT_BYTES,52861)
        self.assertEqual(frozen.REPORT_SHA256,
                         "ae0ea421f3d0643f28ba07c8f1e2d5767a1ad5291c313cabbfebd6378447db50")
        self.assertEqual(frozen.FIXTURE_SHA256,
                         "4ac7d5ca7e89bfc4b962651ec829a2a8f39b94dbb38126a9a8d2da05eca40c41")
        self.assertEqual(len(frozen.load()),128)
        self.assertEqual(frozen.SHAPE["first_mapped_kind"],"ABS")
        self.assertEqual(frozen.SHAPE["second_mapped_kind"],"ABS")
        self.assertEqual(frozen.SHAPE["first_mapped_input_class"],
                         probe.CLASS+"IntervalSelect")

    def test_26th_structure_only_fixture_anchored_transport(self):
        shapes,vectors=probe.parse_output(self.frames())
        self.assertEqual((len(shapes),len(vectors)),(4,128))
        self.assertEqual(probe.NEW_FIELDS,())
        self.assertEqual(probe.OLD_FIELDS,("old_first_interval_bits","old_second_interval_bits"))
        self.assertEqual(probe.candidate_telemetry(shapes,vectors)["new_numeric_ieee_words"],0)
        probe.validate(self.report())

    def test_bad_previous_bits_field_names_provenance_and_gates_fail_closed(self):
        with self.assertRaises(probe.TwentySixthLayerError):
            probe.parse_output(self.frames(mutate_old=True))
        for change in (
            lambda s:s.replace("whenInside~","bad space~",1),
            lambda s:s.replace(self.FIRST,self.FIRST+";"*15,1),
            lambda s:s.replace(probe.HEAD,"unrecognized-tag",1),
        ):
            with self.subTest(change=str(change)),self.assertRaises(probe.TwentySixthLayerError):
                probe.parse_output(change(self.frames()))
        for key in (
            "prior_twenty_fifth_fixture_sha256",
            "prior_twenty_fifth_report_sha256",
            "twenty_sixth_all_input_interval_semantics_admitted",
        ):
            report=self.report()
            report[key]=True if isinstance(report[key],bool) else "tampered"
            with self.subTest(key=key),self.assertRaises(probe.TwentySixthLayerError):
                probe.validate(report)

    def test_no_private_original_stock_fails_closed(self):
        with tempfile.TemporaryDirectory() as td:
            base=Path(td)
            dest=base/"not-created.json"
            with contextlib.redirect_stderr(io.StringIO()):
                result=probe.main([
                    "--source",str(base/"absent-source.zip"),
                    "--db",str(base/"absent.sqlite"),
                    "--lock",str(base/"absent.lock"),
                    "--server-jar",str(base/"absent.bin"),
                    "--output",str(dest),
                ])
            self.assertEqual(result,2)
            self.assertFalse(dest.exists())

    @unittest.skipUnless(shutil.which("javac"),"javac required")
    def test_source_free_complete_twenty_sixth_java_bridge_compiles(self):
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
            o.JAVA_SOURCE,
        )
        with tempfile.TemporaryDirectory() as td:
            p=subprocess.run(["javac","-encoding","UTF-8","-d",td,
                              *(str(x) for x in sources)],
                             capture_output=True,text=True,timeout=90,check=False)
            self.assertEqual(p.returncode,0,p.stderr)


if __name__=="__main__":
    unittest.main()
