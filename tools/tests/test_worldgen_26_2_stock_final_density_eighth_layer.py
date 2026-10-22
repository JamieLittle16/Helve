"""Eighth-layer real original JVM Ap2 operands and two selector target records."""
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
import worldgen_26_2_stock_final_density_eighth_layer as eighth  # noqa: E402


class EighthOwnerFrameTests(unittest.TestCase):
    def shape_fields(self)->tuple[str,...]:
        c=eighth.CLASS
        return (
            c+"TwoArgumentSimpleFunction$Type","ADD",c+"Noise",c+"Constant",
            c+"YClampedGradient","-4064","4062","c0afc00000000000","40afbc0000000000",
            c+"YClampedGradient","-4064","4062","c0afc00000000000","40afbc0000000000",
        )

    def stdout(self)->str:
        old=eighth.prior.load()
        lines=["original JVM console logs do not form capture frames"]
        for i,seed in enumerate(eighth.seventh.sixth.fifth.fourth.third.second.final.SEEDS):
            lines.append("|".join((eighth.HEAD,str(i),seed,*self.shape_fields())))
            for j in range(32):
                idx=32*i+j
                a=old[idx][0]
                left=old[idx][1]
                right=old[idx][4]
                words=(a,"0000000000000000",a,left,left,right,right)
                lines.append("|".join((eighth.VALUE,str(idx),*words)))
            lines.append("|".join((eighth.END,str(i),"32")))
        return "\n".join(lines)+"\n"

    def methods(self)->dict:
        root=eighth.seventh.sixth.fifth.fourth.third.second.root
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
            "normalized_sha256":"a"*64,"reviewed":False,
        }
        return methods

    def report(self)->dict:
        shapes,vectors=eighth.parse_output(self.stdout())
        return {
            "schema":1,"kind":eighth.KIND,"minecraft":"26.2","protocol":776,
            "data_version":4903,
            "source_archive_sha256":eighth.seventh.sixth.fifth.fourth.third.second.final.frozen.SOURCE_SHA256,
            "official_server_sha256":eighth.seventh.sixth.fifth.fourth.third.second.final.frozen.SERVER_SHA256,
            "prior_seventh_fixture_sha256":eighth.prior.SHA256,
            "prior_seventh_report_sha256":eighth.prior.REPORT_SHA256,
            "source_methods":self.methods(),
            "world_seeds":list(eighth.seventh.sixth.fifth.fourth.third.second.final.SEEDS),
            "point_count_per_seed":32,
            "sample_context":"DensityFunction$SinglePointContext",
            "original_stock_registry_used":True,"new_eighth_layer_inputs_observed":True,
            "source_text_included":False,
            "shapes":shapes,"vectors":vectors,
            "ap2_candidate_observation":eighth.ap2_candidate_observation(shapes,vectors),
            **{gate:False for gate in eighth.GATES},
        }

    def test_four_seed_strict_128_original_ap2_children_and_target_matches(self):
        s,v=eighth.parse_output(self.stdout())
        self.assertEqual((len(s),len(v)),(4,128))
        self.assertEqual(v[0]["ap2_old_bits"][2:],eighth.prior.load()[0][0])
        self.assertEqual(v[-1]["right_target_bits"][2:],eighth.prior.load()[-1][4])
        eighth.validate(self.report())

    def test_changed_original_enum_or_parent_or_target_rejected(self):
        original=self.stdout().splitlines()
        changes=[
            lambda l:l.pop(2),
            lambda l:l.append(l[-1]),
            lambda l:l.__setitem__(1,l[1].replace("|ADD|","|UNSUPPORTED|",1)),
            lambda l:l.__setitem__(1,l[1].replace("|-4064|4062|","|4062|-4064|",1)),
            lambda l:l.__setitem__(2,l[2].replace(
                eighth.prior.load()[0][0],"3ff0000000000000",1)),
            lambda l:l.__setitem__(2,l[2].replace(
                eighth.prior.load()[0][1], "3ff0000000000000",1)),
        ]
        for i,mutation in enumerate(changes):
            lines=original.copy()
            mutation(lines)
            with self.subTest(i=i),self.assertRaises(eighth.EighthLayerError):
                eighth.parse_output("\n".join(lines))
        for key in ("source_text_included","prior_seventh_fixture_sha256",
                    "prior_seventh_report_sha256","source_archive_sha256"):
            report=self.report()
            report[key]=True
            with self.subTest(key=key),self.assertRaises(eighth.EighthLayerError):
                eighth.validate(report)
        for gate in eighth.GATES:
            report=self.report()
            report[gate]=True
            with self.subTest(gate=gate),self.assertRaises(eighth.EighthLayerError):
                eighth.validate(report)

    def test_unreviewed_ap2_arithmetic_divergence_is_observed_not_silenced(self):
        frames=self.stdout().splitlines()
        # Hold the separately frozen original Ap2 parent constant. Change an
        # artificial operand to deliberately violate naive ADD arithmetic;
        # it must be recorded as a counterexample, not discarded or admitted.
        words=frames[2].split("|")
        self.assertEqual(words[0],eighth.VALUE)
        words[3]="3ff0000000000000"  # new second operand, old parent unchanged
        frames[2]="|".join(words)
        shapes,vectors=eighth.parse_output("\n".join(frames))
        obs=eighth.ap2_candidate_observation(shapes,vectors)
        self.assertEqual(obs["candidate_operand_pairs_checked"],128)
        self.assertEqual(obs["raw_ieee_mismatch_count"],1)
        self.assertEqual(obs["raw_ieee_first_mismatch_index"],0)
        self.assertEqual(obs["positive_zero_shortcircuit_mismatch_count"],1)
        self.assertIs(obs["source_law_admitted"],False)
        report=self.report()
        report["vectors"]=vectors
        report["ap2_candidate_observation"]=obs
        eighth.validate(report)
        report["ap2_candidate_observation"]={**obs,"source_law_admitted":True}
        with self.assertRaises(eighth.EighthLayerError):
            eighth.validate(report)

    def test_positive_zero_mul_shortcircuit_candidate_not_source_admission(self):
        class_shape={"deep_ap2_op":"MUL"}
        # IEEE-754 multiplication of +0 by negative finite yields negative
        # zero; the existing explicitly distinct Ap2 candidate returns +0.
        original=eighth.pack(0.0)
        vectors=[{
            "ap2_left_bits":original,
            "ap2_right_bits":eighth.pack(-3.0),
            "ap2_old_bits":original,
        }]
        obs=eighth.ap2_candidate_observation([class_shape],vectors)
        self.assertEqual(obs["raw_ieee_mismatch_count"],1)
        self.assertEqual(obs["positive_zero_shortcircuit_mismatch_count"],0)
        self.assertIs(obs["source_law_admitted"],False)

    def test_private_source_absent_fails_before_output(self):
        with tempfile.TemporaryDirectory() as td:
            target=Path(td)/"should-not-exist.json"
            err=io.StringIO()
            with contextlib.redirect_stderr(err):
                rc=eighth.main([
                    "--source",str(Path(td)/"missing.zip"),
                    "--db",str(Path(td)/"missing.sqlite"),
                    "--lock",str(Path(td)/"missing.toml"),
                    "--server-jar",str(Path(td)/"missing.jar"),
                    "--output",str(target),
                ])
            self.assertEqual(rc,2)
            self.assertFalse(target.exists())
            self.assertIn("EIGHTH LAYER OPEN",err.getvalue())

    @unittest.skipUnless(shutil.which("javac"),"requires javac")
    def test_new_eighth_java_bridge_compiles_without_stock_server(self):
        f=eighth.seventh.sixth.fifth
        sources=(
            f.fourth.third.second.final.roots.BASE_BRIDGE,
            f.fourth.third.second.final.JAVA_SOURCE,
            f.fourth.third.second.root.JAVA_SOURCE,
            f.fourth.third.second.inner.JAVA_SOURCE,
            f.fourth.third.second.JAVA_SOURCE,
            f.fourth.third.JAVA_SOURCE,
            f.fourth.JAVA_SOURCE,
            f.JAVA_SOURCE,
            eighth.seventh.sixth.JAVA_SOURCE,
            eighth.seventh.JAVA_SOURCE,
            eighth.JAVA_SOURCE,
        )
        with tempfile.TemporaryDirectory() as td:
            p=subprocess.run(
                ["javac","-encoding","UTF-8","-d",td,*(str(x) for x in sources)],
                capture_output=True,text=True,timeout=65,check=False,
            )
            self.assertEqual(p.returncode,0,p.stderr)


if __name__=="__main__":
    unittest.main()
