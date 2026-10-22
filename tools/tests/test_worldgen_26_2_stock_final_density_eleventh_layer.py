"""Synthetic strict 26.2 eleventh actual Marker+two Ap2 source-free frames."""
from __future__ import annotations

import contextlib
import io
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import worldgen_26_2_stock_final_density_eleventh_layer as eleventh  # noqa: E402


class EleventhActualSourceOwnerTests(unittest.TestCase):
    def frames(self)->str:
        original=eleventh.prior.load()
        cls=eleventh.tenth.ninth.eighth.CLASS
        shape=(
            cls+"Marker$Type","CacheOnce",cls+"Noise",
            cls+"TwoArgumentSimpleFunction$Type","ADD",cls+"Noise",cls+"Constant",
            cls+"TwoArgumentSimpleFunction$Type","MUL",cls+"Noise",cls+"Constant",
        )
        lines=["untrusted logging is not source-owner frames"]
        for group,seed in enumerate(
                eleventh.tenth.ninth.eighth.seventh.sixth.fifth.fourth.third.second.final.SEEDS):
            lines.append("|".join((eleventh.HEAD,str(group),seed,*shape)))
            for j in range(32):
                idx=group*32+j
                words=("3ff0000000000000",)*5+original[idx]
                lines.append("|".join((eleventh.VALUE,str(idx),*words)))
            lines.append("|".join((eleventh.END,str(group),"32")))
        return "\n".join(lines)+"\n"

    def source_methods(self)->dict:
        root=eleventh.tenth.ninth.eighth.seventh.sixth.fifth.fourth.third.second.root
        methods={}
        for k in ("ap2_compute","holder_holder_compute"):
            owner,signature,body,normalized=root.frozen_final.METHODS[k]
            methods[k]={
                "owner":owner,"signature":signature,
                "body_sha256":body,"normalized_sha256":normalized,
                "reviewed":False,
            }
        methods["mapped_delegate_compute"]={
            "owner":root.PURE_TRANSFORMER,
            "signature":"compute(final DensityFunction . FunctionContext context)",
            "body_sha256":root.PURE_COMPUTE_SHA256,
            "normalized_sha256":"a"*64,
            "reviewed":False,
        }
        return methods

    def report(self)->dict:
        shapes,vectors=eleventh.parse_output(self.frames())
        f=eleventh.tenth.ninth.eighth.seventh.sixth.fifth.fourth.third.second.final
        return {
            "schema":1,"kind":eleventh.KIND,"minecraft":"26.2",
            "protocol":776,"data_version":4903,
            "source_archive_sha256":f.frozen.SOURCE_SHA256,
            "official_server_sha256":f.frozen.SERVER_SHA256,
            "prior_tenth_fixture_sha256":eleventh.prior.SHA256,
            "prior_tenth_report_sha256":eleventh.prior.REPORT_SHA256,
            "source_methods":self.source_methods(),
            "world_seeds":list(f.SEEDS),
            "point_count_per_seed":32,
            "sample_context":"DensityFunction$SinglePointContext",
            "original_stock_registry_used":True,
            "new_eleventh_layer_children_observed":True,
            "source_text_included":False,
            "shapes":shapes,"vectors":vectors,
            "marker_candidate_telemetry":eleventh.marker_candidate_telemetry(shapes,vectors),
            **{gate:False for gate in eleventh.GATES},
        }

    def test_real_tenth_parents_pinned_and_records_not_guessed(self):
        shapes,vectors=eleventh.parse_output(self.frames())
        self.assertEqual((len(shapes),len(vectors)),(4,128))
        self.assertEqual(
            [vectors[0][k][2:] for k in eleventh.OLD_FIELDS],
            list(eleventh.prior.load()[0]))
        self.assertEqual(eleventh.marker_candidate_telemetry(shapes,vectors)["original_bounded_points"],128)
        eleventh.validate(self.report())

    def test_seed_shape_method_source_and_old_parent_mutations_rejected(self):
        original=self.frames().splitlines()
        changes=[
            lambda x:x.pop(2),
            lambda x:x.append(x[-1]),
            lambda x:x.__setitem__(1,x[1].replace("Marker$Type","NotMarker",1)),
            lambda x:x.__setitem__(1,x[1].replace("TwoArgumentSimpleFunction$Type","Other",1)),
        ]
        def old_anchor(x):
            row=x[2].split("|")
            row[-1]="7ff0000000000000"
            x[2]="|".join(row)
        changes.append(old_anchor)
        for i,modify in enumerate(changes):
            rows=original.copy()
            modify(rows)
            with self.subTest(case=i),self.assertRaises(eleventh.EleventhLayerError):
                eleventh.parse_output("\n".join(rows))
        for pin in ("source_text_included","prior_tenth_fixture_sha256",
                    "official_server_sha256","prior_tenth_report_sha256"):
            report=self.report()
            report[pin]=True
            with self.subTest(pin=pin),self.assertRaises(eleventh.EleventhLayerError):
                eleventh.validate(report)
        for gate in eleventh.GATES:
            report=self.report()
            report[gate]=True
            with self.subTest(gate=gate),self.assertRaises(eleventh.EleventhLayerError):
                eleventh.validate(report)

    def test_marker_delegate_candidate_not_automatically_admitted(self):
        shape,vectors=eleventh.parse_output(self.frames())
        telemetry=eleventh.marker_candidate_telemetry(shape,vectors)
        self.assertIs(telemetry["source_law_admitted"],False)
        self.assertEqual(telemetry["original_bounded_points"],128)
        report=self.report()
        report["marker_candidate_telemetry"]={**telemetry,"source_law_admitted":True}
        with self.assertRaises(eleventh.EleventhLayerError):
            eleventh.validate(report)

    def test_private_source_missing_fails_without_new_output(self):
        with tempfile.TemporaryDirectory() as td:
            output=Path(td)/"should-not-exist.json"
            err=io.StringIO()
            with contextlib.redirect_stderr(err):
                rc=eleventh.main([
                    "--source",str(Path(td)/"missing.zip"),
                    "--db",str(Path(td)/"missing.sqlite"),
                    "--lock",str(Path(td)/"missing.toml"),
                    "--server-jar",str(Path(td)/"missing.jar"),
                    "--output",str(output),
                ])
            self.assertEqual(rc,2)
            self.assertFalse(output.exists())
            self.assertIn("ELEVENTH LAYER OPEN",err.getvalue())

    @unittest.skipUnless(shutil.which("javac"),"JDK javac required")
    def test_java_bridge_compiles_without_original_source(self):
        f=eleventh.tenth.ninth.eighth.seventh.sixth.fifth
        sources=(
            f.fourth.third.second.final.roots.BASE_BRIDGE,
            f.fourth.third.second.final.JAVA_SOURCE,
            f.fourth.third.second.root.JAVA_SOURCE,
            f.fourth.third.second.inner.JAVA_SOURCE,
            f.fourth.third.second.JAVA_SOURCE,
            f.fourth.third.JAVA_SOURCE,
            f.fourth.JAVA_SOURCE,
            f.JAVA_SOURCE,
            eleventh.tenth.ninth.eighth.seventh.sixth.JAVA_SOURCE,
            eleventh.tenth.ninth.eighth.seventh.JAVA_SOURCE,
            eleventh.tenth.ninth.eighth.JAVA_SOURCE,
            eleventh.tenth.ninth.JAVA_SOURCE,
            eleventh.tenth.JAVA_SOURCE,
            eleventh.JAVA_SOURCE,
        )
        with tempfile.TemporaryDirectory() as td:
            proc=subprocess.run(
                ["javac","-encoding","UTF-8","-d",td,*(str(p) for p in sources)],
                capture_output=True,text=True,timeout=75,check=False,
            )
            self.assertEqual(proc.returncode,0,proc.stderr)


if __name__=="__main__":
    unittest.main()
