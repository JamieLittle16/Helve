"""Fail-closed source-owning sixth original-26.2 JVM transport and JDK bridge."""
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
import worldgen_26_2_stock_final_density_sixth_layer as sixth  # noqa: E402


class SixthLayerTransportTests(unittest.TestCase):
    def stdout(self)->str:
        previous=sixth.prior.load()
        cl=sixth.CLASS
        lines=["JVM console logging does not become a source-free evidence frame"]
        for i,seed in enumerate(sixth.fifth.fourth.third.second.final.SEEDS):
            shape=(
                "-64","-40","0000000000000000","3ff0000000000000",
                "-4064","4062","c0afc00000000000","40afbc0000000000",
                cl+"MulOrAdd$Type","ADD","0000000000000000",cl+"Noise",
                cl+"MulOrAdd$Type","ADD","0000000000000000",cl+"Noise",
                cl+"Marker$Type","Interpolated",cl+"Noise",
                cl+"Marker$Type","Interpolated",cl+"Noise",
            )
            lines.append("|".join((sixth.HEAD,str(i),seed,*shape)))
            for j in range(32):
                k=i*32+j
                old=previous[k]
                words=(
                    old[0],old[1],old[1],
                    old[2],old[3],old[3],
                    old[4],old[4],old[5],old[5],
                )
                lines.append("|".join((sixth.VALUE,str(k),*words)))
            lines.append("|".join((sixth.END,str(i),"32")))
        return "\n".join(lines)+"\n"

    def methods(self)->dict:
        root=sixth.fifth.fourth.third.second.root
        result={}
        for name in ("ap2_compute","holder_holder_compute"):
            owner,sig,body,norm=root.frozen_final.METHODS[name]
            result[name]={
                "owner":owner,"signature":sig,
                "body_sha256":body,"normalized_sha256":norm,"reviewed":False,
            }
        result["mapped_delegate_compute"]={
            "owner":root.PURE_TRANSFORMER,
            "signature":"compute(final DensityFunction . FunctionContext context)",
            "body_sha256":root.PURE_COMPUTE_SHA256,
            "normalized_sha256":"a"*64,"reviewed":False,
        }
        return result

    def report(self)->dict:
        shapes,vectors=sixth.parse_output(self.stdout())
        return {
            "schema":1,"kind":sixth.KIND,"minecraft":"26.2","protocol":776,
            "data_version":4903,
            "source_archive_sha256":sixth.fifth.fourth.third.second.final.frozen.SOURCE_SHA256,
            "official_server_sha256":sixth.fifth.fourth.third.second.final.frozen.SERVER_SHA256,
            "prior_fifth_fixture_sha256":sixth.prior.SHA256,
            "prior_fifth_report_sha256":sixth.prior.REPORT_SHA256,
            "source_methods":self.methods(),
            "world_seeds":list(sixth.fifth.fourth.third.second.final.SEEDS),
            "point_count_per_seed":32,
            "sample_context":"DensityFunction$SinglePointContext",
            "original_stock_registry_used":True,"new_sixth_layer_inputs_observed":True,
            "source_text_included":False,
            "shapes":shapes,"vectors":vectors,
            **{gate:False for gate in sixth.GATES},
        }

    def test_128_original_fifth_parent_bound_child_frames(self):
        shapes,vectors=sixth.parse_output(self.stdout())
        self.assertEqual((len(shapes),len(vectors)),(4,128))
        self.assertEqual(shapes[0]["outside_mul_op"],"ADD")
        self.assertEqual(vectors[0]["left_gradient_old_bits"][2:],
                         sixth.prior.load()[0][0])
        sixth.validate(self.report())

    def test_mutating_previous_input_or_runtime_enum_fails(self):
        original=self.stdout().splitlines()
        mutators=[
            lambda a:a.pop(2),
            lambda a:a.append(a[-1]),
            lambda a:a.__setitem__(1,a[1].replace("Marker$Type","Unknown",1)),
            lambda a:a.__setitem__(1,a[1].replace("|ADD|","|MIN|",1)),
            lambda a:a.__setitem__(1,a[1].replace("|-64|-40|","|-40|-64|",1)),
            lambda a:a.__setitem__(1,a[1].replace("|0000000000000000|","|7ff0000000000000|",1)),
            lambda a:a.__setitem__(1,a[1].replace(
                sixth.fifth.fourth.third.second.final.SEEDS[0],
                sixth.fifth.fourth.third.second.final.SEEDS[1])),
            lambda a:a.__setitem__(2,a[2].replace(
                sixth.prior.load()[0][0],"3ff0000000000000",1)),
        ]
        for i,mutator in enumerate(mutators):
            changed=original.copy()
            mutator(changed)
            with self.subTest(i=i),self.assertRaises(sixth.SixthLayerError):
                sixth.parse_output("\n".join(changed))
        for key in ("prior_fifth_fixture_sha256","prior_fifth_report_sha256",
                    "official_server_sha256","source_archive_sha256"):
            report=self.report()
            report[key]="f"*64
            with self.subTest(key=key),self.assertRaises(sixth.SixthLayerError):
                sixth.validate(report)
        for gate in sixth.GATES:
            report=self.report()
            report[gate]=True
            with self.subTest(gate=gate),self.assertRaises(sixth.SixthLayerError):
                sixth.validate(report)

    def test_missing_source_owner_never_writes_json(self):
        with tempfile.TemporaryDirectory() as td:
            output=Path(td)/"not_original.json"
            err=io.StringIO()
            with contextlib.redirect_stderr(err):
                rc=sixth.main([
                    "--source",str(Path(td)/"absent.zip"),
                    "--db",str(Path(td)/"absent.sqlite"),
                    "--lock",str(Path(td)/"absent.toml"),
                    "--server-jar",str(Path(td)/"absent.jar"),
                    "--output",str(output),
                ])
            self.assertEqual(rc,2)
            self.assertFalse(output.exists())
            self.assertIn("SIXTH LAYER OPEN",err.getvalue())

    @unittest.skipUnless(shutil.which("javac"),"JDK compiler required")
    def test_source_free_real_sixth_java_bridge_compiles(self):
        f=sixth.fifth
        sources=(
            f.fourth.third.second.final.roots.BASE_BRIDGE,
            f.fourth.third.second.final.JAVA_SOURCE,
            f.fourth.third.second.root.JAVA_SOURCE,
            f.fourth.third.second.inner.JAVA_SOURCE,
            f.fourth.third.second.JAVA_SOURCE,
            f.fourth.third.JAVA_SOURCE,
            f.fourth.JAVA_SOURCE,
            f.JAVA_SOURCE,
            sixth.JAVA_SOURCE,
        )
        with tempfile.TemporaryDirectory() as td:
            p=subprocess.run(
                ["javac","-encoding","UTF-8","-d",td,*(str(x) for x in sources)],
                capture_output=True,text=True,timeout=60,check=False,
            )
            self.assertEqual(p.returncode,0,p.stderr)


if __name__=="__main__":
    unittest.main()
