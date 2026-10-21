"""Bounded fifth-layer original stock JVM transport and fail-closed tests."""
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
import worldgen_26_2_stock_final_density_fifth_layer as fifth  # noqa: E402


class FifthLayerTransportTests(unittest.TestCase):
    def stdout(self)->str:
        rows=fifth.prior.load()
        cl=fifth.CLASS
        lines=["Unrelated JVM logging never becomes a captured data field"]
        for i,seed in enumerate(fifth.fourth.third.second.final.SEEDS):
            line=[
                fifth.HEAD,str(i),seed,
                cl+"TwoArgumentSimpleFunction$Type","ADD",cl+"Noise",cl+"Constant",
                "-64","320","bff0000000000000","3ff0000000000000",
                cl+"YClampedGradient",
                cl+"MulOrAdd$Type","MUL","3ff0000000000000",cl+"Noise",
                cl+"Mapped$Type","SQUEEZE",cl+"Noise",
                cl+"Mapped$Type","ABS",cl+"Noise",
            ]
            lines.append("|".join(line))
            for j in range(32):
                index=i*32+j
                old=rows[index]
                words=[
                    old[0], "0000000000000000", old[0],
                    old[2],old[2],
                    old[3],old[3],
                    old[5],old[5],
                    old[6],old[6],
                ]
                lines.append("|".join((fifth.VALUE,str(index),*words)))
            lines.append("|".join((fifth.END,str(i),"32")))
        return "\n".join(lines)+"\n"

    def methods(self)->dict:
        root=fifth.fourth.third.second.root
        methods={}
        for name in ("ap2_compute","holder_holder_compute"):
            owner,sig,body,norm=root.frozen_final.METHODS[name]
            methods[name]={
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
        shapes,vectors=fifth.parse_output(self.stdout())
        return {
            "schema":1,"kind":fifth.KIND,"minecraft":"26.2","protocol":776,
            "data_version":4903,
            "source_archive_sha256":fifth.fourth.third.second.final.frozen.SOURCE_SHA256,
            "official_server_sha256":fifth.fourth.third.second.final.frozen.SERVER_SHA256,
            "prior_fourth_fixture_sha256":fifth.prior.SHA256,
            "prior_fourth_report_sha256":fifth.prior.REPORT_SHA256,
            "source_methods":self.methods(),
            "world_seeds":list(fifth.fourth.third.second.final.SEEDS),
            "point_count_per_seed":32,
            "sample_context":"DensityFunction$SinglePointContext",
            "original_stock_registry_used":True,
            "new_fifth_layer_inputs_observed":True,
            "shapes":shapes,"vectors":vectors,
            **{key:False for key in fifth.GATES},
        }

    def test_original_parent_bound_128_context_transport(self):
        shapes,vectors=fifth.parse_output(self.stdout())
        self.assertEqual((len(shapes),len(vectors)),(4,128))
        self.assertEqual(vectors[0]["left_ap2_output_bits"][2:],fifth.prior.load()[0][0])
        fifth.validate(self.report())

    def test_wrong_original_classes_old_bits_or_admission_fail(self):
        lines=self.stdout().splitlines()
        mutations=[
            lambda a:a.pop(2),
            lambda a:a.append(a[-1]),
            lambda a:a.__setitem__(1,a[1].replace("YClampedGradient","Unexpected",1)),
            lambda a:a.__setitem__(1,a[1].replace("|-64|320|","|320|-64|",1)),
            lambda a:a.__setitem__(1,a[1].replace("3ff0000000000000","7ff0000000000000",1)),
            lambda a:a.__setitem__(2,a[2].replace(
                fifth.prior.load()[0][2],"3ff0000000000000",1)),
        ]
        for i,mutate in enumerate(mutations):
            bad=lines.copy()
            mutate(bad)
            with self.subTest(i=i),self.assertRaises(fifth.FifthLayerError):
                fifth.parse_output("\n".join(bad))
        for k in ("source_archive_sha256","prior_fourth_fixture_sha256",
                  "official_server_sha256","prior_fourth_report_sha256"):
            report=self.report()
            report[k]="e"*64
            with self.subTest(k=k),self.assertRaises(fifth.FifthLayerError):
                fifth.validate(report)
        for gate in fifth.GATES:
            report=self.report()
            report[gate]=True
            with self.subTest(gate=gate),self.assertRaises(fifth.FifthLayerError):
                fifth.validate(report)

    def test_no_private_owner_no_new_original_capture(self):
        with tempfile.TemporaryDirectory() as td:
            output=Path(td)/"unqualified.json"
            err=io.StringIO()
            with contextlib.redirect_stderr(err):
                rc=fifth.main([
                    "--source",str(Path(td)/"missing-source.zip"),
                    "--db",str(Path(td)/"missing.sqlite"),
                    "--lock",str(Path(td)/"missing.lock"),
                    "--server-jar",str(Path(td)/"missing-server.jar"),
                    "--output",str(output),
                ])
            self.assertEqual(rc,2)
            self.assertFalse(output.exists())
            self.assertIn("FIFTH LAYER OPEN",err.getvalue())

    @unittest.skipUnless(shutil.which("javac"),"JDK javac required")
    def test_original_source_owned_fifth_java_bridge_compiles(self):
        fourth=fifth.fourth
        sources=(
            fourth.third.second.final.roots.BASE_BRIDGE,
            fourth.third.second.final.JAVA_SOURCE,
            fourth.third.second.root.JAVA_SOURCE,
            fourth.third.second.inner.JAVA_SOURCE,
            fourth.third.second.JAVA_SOURCE,
            fourth.third.JAVA_SOURCE,
            fourth.JAVA_SOURCE,
            fifth.JAVA_SOURCE,
        )
        with tempfile.TemporaryDirectory() as td:
            run=subprocess.run(
                ["javac","-encoding","UTF-8","-d",td,*(str(x) for x in sources)],
                capture_output=True,text=True,timeout=60,check=False,
            )
            self.assertEqual(run.returncode,0,run.stderr)


if __name__=="__main__":
    unittest.main()
