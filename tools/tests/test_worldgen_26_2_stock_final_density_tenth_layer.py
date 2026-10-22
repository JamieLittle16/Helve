"""Source-free tenth original Java true RangeChoice branch/selector evidence."""
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
import worldgen_26_2_stock_final_density_tenth_layer as tenth  # noqa: E402


class TenthOriginalRangeChoiceTests(unittest.TestCase):
    def stdout(self)->str:
        parents=tenth.prior.load()
        cl=tenth.ninth.eighth.CLASS
        shapes=(
            "c04e000000000000","4074100000000000",
            cl+"YClampedGradient",cl+"Noise",cl+"Constant",
        )
        lines=["noise in JVM console does not authenticate source frames"]
        for group,seed in enumerate(
                tenth.ninth.eighth.seventh.sixth.fifth.fourth.third.second.final.SEEDS):
            lines.append("|".join((tenth.HEAD,str(group),seed,*shapes)))
            for j in range(32):
                i=group*32+j
                lines.append("|".join((tenth.VALUE,str(i),
                    "0000000000000000",parents[i],"0000000000000000",parents[i])))
            lines.append("|".join((tenth.END,str(group),"32")))
        return "\n".join(lines)+"\n"

    def methods(self)->dict:
        root=tenth.ninth.eighth.seventh.sixth.fifth.fourth.third.second.root
        methods={}
        for k in ("ap2_compute","holder_holder_compute"):
            owner,sig,body,norm=root.frozen_final.METHODS[k]
            methods[k]={
                "owner":owner,"signature":sig,"body_sha256":body,
                "normalized_sha256":norm,"reviewed":False,
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
        shapes,vectors=tenth.parse_output(self.stdout())
        return {
            "schema":1,"kind":tenth.KIND,"minecraft":"26.2",
            "protocol":776,"data_version":4903,
            "source_archive_sha256":tenth.ninth.eighth.seventh.sixth.fifth.fourth.third.second.final.frozen.SOURCE_SHA256,
            "official_server_sha256":tenth.ninth.eighth.seventh.sixth.fifth.fourth.third.second.final.frozen.SERVER_SHA256,
            "prior_ninth_fixture_sha256":tenth.prior.SHA256,
            "prior_ninth_report_sha256":tenth.prior.REPORT_SHA256,
            "source_methods":self.methods(),
            "world_seeds":list(tenth.ninth.eighth.seventh.sixth.fifth.fourth.third.second.final.SEEDS),
            "point_count_per_seed":32,
            "sample_context":"DensityFunction$SinglePointContext",
            "original_stock_registry_used":True,"new_tenth_layer_children_observed":True,
            "source_text_included":False,
            "shapes":shapes,"vectors":vectors,
            "rangechoice_candidate_telemetry":tenth.choice_telemetry(shapes,vectors),
            **{gate:False for gate in tenth.GATES},
        }

    def test_four_shapes_128_real_prior_parents_and_range_candidate(self):
        shapes,vectors=tenth.parse_output(self.stdout())
        self.assertEqual((len(shapes),len(vectors)),(4,128))
        self.assertEqual(vectors[0]["old_rangechoice_bits"][2:],
                         tenth.prior.load()[0])
        self.assertEqual(tenth.choice_telemetry(shapes,vectors)["naive_candidate_mismatches"],0)
        tenth.validate(self.report())

    def test_source_owned_previous_parent_and_record_mutations_are_blocked(self):
        original=self.stdout().splitlines()
        def mutate_parent(lines):
            words=lines[2].split("|")
            words[-1]="3ff0000000000000"
            lines[2]="|".join(words)
        mutations=[
            lambda lines:lines.pop(2),
            lambda lines:lines.append(lines[-1]),
            lambda lines:lines.__setitem__(
                1,lines[1].replace("c04e000000000000","4074100000000000",1)),
            lambda lines:lines.__setitem__(1,lines[1].replace("YClampedGradient","UnsafeClass",1)),
            mutate_parent,
        ]
        for i,mutation in enumerate(mutations):
            lines=original.copy()
            mutation(lines)
            with self.subTest(case=i),self.assertRaises(tenth.TenthLayerError):
                tenth.parse_output("\n".join(lines))
        for name in ("source_text_included","prior_ninth_fixture_sha256",
                     "prior_ninth_report_sha256","official_server_sha256"):
            report=self.report()
            report[name]=True
            with self.subTest(pin=name),self.assertRaises(tenth.TenthLayerError):
                tenth.validate(report)
        for gate in tenth.GATES:
            report=self.report()
            report[gate]=True
            with self.subTest(gate=gate),self.assertRaises(tenth.TenthLayerError):
                tenth.validate(report)

    def test_observed_not_predicted_choice_disagreement_is_reported(self):
        lines=self.stdout().splitlines()
        words=lines[2].split("|")
        words[3]="3ff0000000000000"  # genuine NEW branch changed, old parent immutable
        lines[2]="|".join(words)
        shapes,vectors=tenth.parse_output("\n".join(lines))
        obs=tenth.choice_telemetry(shapes,vectors)
        self.assertEqual(obs["naive_candidate_mismatches"],1)
        self.assertIs(obs["source_law_admitted"],False)
        report=self.report()
        report["vectors"]=vectors
        report["rangechoice_candidate_telemetry"]=obs
        tenth.validate(report)
        report["rangechoice_candidate_telemetry"]={**obs,"source_law_admitted":True}
        with self.assertRaises(tenth.TenthLayerError):
            tenth.validate(report)

    def test_missing_private_source_fails_without_report(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/"not-created.json"
            err=io.StringIO()
            with contextlib.redirect_stderr(err):
                status=tenth.main([
                    "--source",str(Path(td)/"missing.zip"),
                    "--db",str(Path(td)/"missing.sqlite"),
                    "--lock",str(Path(td)/"missing.toml"),
                    "--server-jar",str(Path(td)/"missing.jar"),
                    "--output",str(p),
                ])
            self.assertEqual(status,2)
            self.assertFalse(p.exists())
            self.assertIn("TENTH LAYER OPEN",err.getvalue())

    @unittest.skipUnless(shutil.which("javac"),"JDK javac required")
    def test_original_tenth_bridge_compiles_source_free(self):
        f=tenth.ninth.eighth.seventh.sixth.fifth
        sources=(
            f.fourth.third.second.final.roots.BASE_BRIDGE,
            f.fourth.third.second.final.JAVA_SOURCE,
            f.fourth.third.second.root.JAVA_SOURCE,
            f.fourth.third.second.inner.JAVA_SOURCE,
            f.fourth.third.second.JAVA_SOURCE,
            f.fourth.third.JAVA_SOURCE,
            f.fourth.JAVA_SOURCE,
            f.JAVA_SOURCE,
            tenth.ninth.eighth.seventh.sixth.JAVA_SOURCE,
            tenth.ninth.eighth.seventh.JAVA_SOURCE,
            tenth.ninth.eighth.JAVA_SOURCE,
            tenth.ninth.JAVA_SOURCE,
            tenth.JAVA_SOURCE,
        )
        with tempfile.TemporaryDirectory() as td:
            p=subprocess.run(
                ["javac","-encoding","UTF-8","-d",td,*(str(s) for s in sources)],
                capture_output=True,text=True,timeout=75,check=False)
            self.assertEqual(p.returncode,0,p.stderr)


if __name__=="__main__":
    unittest.main()
