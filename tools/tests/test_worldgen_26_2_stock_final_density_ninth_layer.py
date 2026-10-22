"""Synthetic source-free ninth original JVM bounded gradient and MulOrAdd frames."""
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
import worldgen_26_2_stock_final_density_ninth_layer as ninth  # noqa: E402


class OriginalNinthSourceOwnedTests(unittest.TestCase):
    def stdout(self)->str:
        old=ninth.prior.load()
        cl=ninth.CLASS
        out=["unrelated stock JVM logs are not bounded source frames"]
        for group,seed in enumerate(ninth.eighth.seventh.sixth.fifth.fourth.third.second.final.SEEDS):
            fields=(
                "240","256","3ff0000000000000","0000000000000000",
                cl+"MulOrAdd$Type","ADD","0000000000000000",cl+"Noise",
            )
            out.append("|".join((ninth.HEAD,str(group),seed,*fields)))
            for j in range(32):
                i=group*32+j
                left,right=old[i]
                out.append("|".join((ninth.VALUE,str(i),right,right,left)))
            out.append("|".join((ninth.END,str(group),"32")))
        return "\n".join(out)+"\n"

    def methods(self)->dict:
        root=ninth.eighth.seventh.sixth.fifth.fourth.third.second.root
        methods={}
        for k in ("ap2_compute","holder_holder_compute"):
            owner,sig,body,norm=root.frozen_final.METHODS[k]
            methods[k]={
                "owner":owner,"signature":sig,
                "body_sha256":body,"normalized_sha256":norm,
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
        shapes,vectors=ninth.parse_output(self.stdout())
        return {
            "schema":1,"kind":ninth.KIND,"minecraft":"26.2",
            "protocol":776,"data_version":4903,
            "source_archive_sha256":ninth.eighth.seventh.sixth.fifth.fourth.third.second.final.frozen.SOURCE_SHA256,
            "official_server_sha256":ninth.eighth.seventh.sixth.fifth.fourth.third.second.final.frozen.SERVER_SHA256,
            "prior_eighth_fixture_sha256":ninth.prior.SHA256,
            "prior_eighth_report_sha256":ninth.prior.REPORT_SHA256,
            "source_methods":self.methods(),
            "world_seeds":list(ninth.eighth.seventh.sixth.fifth.fourth.third.second.final.SEEDS),
            "point_count_per_seed":32,
            "sample_context":"DensityFunction$SinglePointContext",
            "original_stock_registry_used":True,"new_ninth_layer_child_observed":True,
            "source_text_included":False,
            "shapes":shapes,"vectors":vectors,
            "muloradd_candidate_telemetry":ninth.candidate_telemetry(shapes,vectors),
            **{gate:False for gate in ninth.GATES},
        }

    def test_128_real_eighth_parent_anchors_four_seed_shapes(self):
        shapes,vectors=ninth.parse_output(self.stdout())
        self.assertEqual((len(shapes),len(vectors)),(4,128))
        self.assertEqual(vectors[0]["old_right_muloradd_bits"][2:],
                         ninth.prior.load()[0][1])
        self.assertEqual(ninth.candidate_telemetry(shapes,vectors)["naive_muloradd_mismatch_count"],0)
        ninth.validate(self.report())

    def test_mutated_old_parent_and_false_source_gates_denied(self):
        original=self.stdout().splitlines()
        mutations=[
            lambda x:x.pop(2),
            lambda x:x.append(x[-1]),
            lambda x:x.__setitem__(1,x[1].replace("|ADD|","|UNKNOWN|",1)),
            lambda x:x.__setitem__(1,x[1].replace("|240|256|","|256|240|",1)),
            lambda x:x.__setitem__(1,x[1].replace("MulOrAdd$Type","Unsupported",1)),
            lambda x:x.__setitem__(2,"|".join(
                [*(x[2].split("|")[:3]),"3ff0000000000000",x[2].split("|")[4]])),
        ]
        for i,mut in enumerate(mutations):
            changed=original.copy()
            mut(changed)
            with self.subTest(i=i),self.assertRaises(ninth.NinthLayerError):
                ninth.parse_output("\n".join(changed))
        for k in ("prior_eighth_fixture_sha256","prior_eighth_report_sha256",
                  "source_archive_sha256","source_text_included"):
            report=self.report()
            report[k]=True
            with self.subTest(pin=k),self.assertRaises(ninth.NinthLayerError):
                ninth.validate(report)
        for gate in ninth.GATES:
            report=self.report()
            report[gate]=True
            with self.subTest(gate=gate),self.assertRaises(ninth.NinthLayerError):
                ninth.validate(report)

    def test_nonmatching_candidate_is_reported_not_promoted(self):
        lines=self.stdout().splitlines()
        parts=lines[2].split("|")
        parts[2]="0000000000000000"  # change only NEW child, keep frozen parents
        lines[2]="|".join(parts)
        shapes,vectors=ninth.parse_output("\n".join(lines))
        telemetry=ninth.candidate_telemetry(shapes,vectors)
        self.assertEqual(telemetry["naive_muloradd_mismatch_count"],1)
        self.assertIs(telemetry["source_law_admitted"],False)
        report=self.report()
        report["vectors"]=vectors
        report["muloradd_candidate_telemetry"]=telemetry
        ninth.validate(report)
        report["muloradd_candidate_telemetry"]={**telemetry,"source_law_admitted":True}
        with self.assertRaises(ninth.NinthLayerError):
            ninth.validate(report)

    def test_missing_private_owner_cannot_write_report(self):
        with tempfile.TemporaryDirectory() as td:
            output=Path(td)/"no-private-receipt.json"
            err=io.StringIO()
            with contextlib.redirect_stderr(err):
                rc=ninth.main([
                    "--source",str(Path(td)/"absent.zip"),
                    "--db",str(Path(td)/"absent.sqlite"),
                    "--lock",str(Path(td)/"absent.toml"),
                    "--server-jar",str(Path(td)/"absent.jar"),
                    "--output",str(output),
                ])
            self.assertEqual(rc,2)
            self.assertFalse(output.exists())
            self.assertIn("NINTH LAYER OPEN",err.getvalue())

    @unittest.skipUnless(shutil.which("javac"),"JDK javac required")
    def test_ninth_source_free_original_jvm_bridge_compiles(self):
        f=ninth.eighth.seventh.sixth.fifth
        sources=(
            f.fourth.third.second.final.roots.BASE_BRIDGE,
            f.fourth.third.second.final.JAVA_SOURCE,
            f.fourth.third.second.root.JAVA_SOURCE,
            f.fourth.third.second.inner.JAVA_SOURCE,
            f.fourth.third.second.JAVA_SOURCE,
            f.fourth.third.JAVA_SOURCE,
            f.fourth.JAVA_SOURCE,
            f.JAVA_SOURCE,
            ninth.eighth.seventh.sixth.JAVA_SOURCE,
            ninth.eighth.seventh.JAVA_SOURCE,
            ninth.eighth.JAVA_SOURCE,
            ninth.JAVA_SOURCE,
        )
        with tempfile.TemporaryDirectory() as td:
            result=subprocess.run(
                ["javac","-encoding","UTF-8","-d",td,*(str(p) for p in sources)],
                capture_output=True,text=True,timeout=75,check=False,
            )
            self.assertEqual(result.returncode,0,result.stderr)


if __name__=="__main__":
    unittest.main()
