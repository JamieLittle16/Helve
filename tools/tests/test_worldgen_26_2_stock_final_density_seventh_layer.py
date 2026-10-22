"""Seventh-layer original 26.2 JVM source-free three-parent-anchor gate."""
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
import worldgen_26_2_stock_final_density_seventh_layer as seventh  # noqa: E402


class RealSeventhSourceOwnedTransportTests(unittest.TestCase):
    def stdout(self)->str:
        previous=seventh.prior.load()
        cl=seventh.CLASS
        lines=["stock JVM logs are not diagnostic frames"]
        for i,seed in enumerate(seventh.sixth.fifth.fourth.third.second.final.SEEDS):
            fields=(
                cl+"MulOrAdd$Type","ADD","0000000000000000",cl+"Noise",
                "bff0000000000000","3ff0000000000000",
                cl+"Constant",cl+"Noise",cl+"Constant",
                "bff0000000000000","3ff0000000000000",
                cl+"Constant",cl+"Noise",cl+"Constant",
            )
            lines.append("|".join((seventh.HEAD,str(i),seed,*fields)))
            for j in range(32):
                k=32*i+j
                old=previous[k]
                words=(
                    old[0],old[0],
                    "0000000000000000",old[2],old[2],old[2],
                    "0000000000000000",old[3],old[3],old[3],
                )
                lines.append("|".join((seventh.VALUE,str(k),*words)))
            lines.append("|".join((seventh.END,str(i),"32")))
        return "\n".join(lines)+"\n"

    def methods(self)->dict:
        root=seventh.sixth.fifth.fourth.third.second.root
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
        shapes,vectors=seventh.parse_output(self.stdout())
        return {
            "schema":1,"kind":seventh.KIND,"minecraft":"26.2","protocol":776,
            "data_version":4903,
            "source_archive_sha256":seventh.sixth.fifth.fourth.third.second.final.frozen.SOURCE_SHA256,
            "official_server_sha256":seventh.sixth.fifth.fourth.third.second.final.frozen.SERVER_SHA256,
            "prior_sixth_fixture_sha256":seventh.prior.SHA256,
            "prior_sixth_report_sha256":seventh.prior.REPORT_SHA256,
            "source_methods":self.methods(),
            "world_seeds":list(seventh.sixth.fifth.fourth.third.second.final.SEEDS),
            "point_count_per_seed":32,
            "sample_context":"DensityFunction$SinglePointContext",
            "original_stock_registry_used":True,"new_seventh_layer_inputs_observed":True,
            "source_text_included":False,
            "shapes":shapes,"vectors":vectors,
            **{gate:False for gate in seventh.GATES},
        }

    def test_four_seed_exact_128_parent_anchored_frames(self):
        shapes,vectors=seventh.parse_output(self.stdout())
        self.assertEqual((len(shapes),len(vectors)),(4,128))
        self.assertEqual(vectors[0]["left_deep_output_bits"][2:],
                         seventh.prior.load()[0][0])
        seventh.validate(self.report())

    def test_synthetic_mutations_are_rejected(self):
        original=self.stdout().splitlines()
        changes=[
            lambda l:l.pop(2),
            lambda l:l.append(l[-1]),
            lambda l:l.__setitem__(1,l[1].replace("MulOrAdd$Type","Unsupported",1)),
            lambda l:l.__setitem__(1,l[1].replace("|ADD|","|MIN|",1)),
            lambda l:l.__setitem__(1,l[1].replace(
                "|bff0000000000000|3ff0000000000000|",
                "|3ff0000000000000|bff0000000000000|",1)),
            lambda l:l.__setitem__(1,l[1].replace(
                "0000000000000000","7ff0000000000000",1)),
            lambda l:l.__setitem__(2,l[2].replace(
                seventh.prior.load()[0][0],"3ff0000000000000",1)),
        ]
        for i,change in enumerate(changes):
            raw=original.copy()
            change(raw)
            with self.subTest(i=i),self.assertRaises(seventh.SeventhLayerError):
                seventh.parse_output("\n".join(raw))
        for pin in ("source_text_included","prior_sixth_fixture_sha256",
                    "prior_sixth_report_sha256","official_server_sha256"):
            record=self.report()
            record[pin]=True
            with self.subTest(pin=pin),self.assertRaises(seventh.SeventhLayerError):
                seventh.validate(record)
        for gate in seventh.GATES:
            record=self.report()
            record[gate]=True
            with self.subTest(gate=gate),self.assertRaises(seventh.SeventhLayerError):
                seventh.validate(record)

    def test_no_source_no_generated_output(self):
        with tempfile.TemporaryDirectory() as td:
            output=Path(td)/"absent-seventh.json"
            err=io.StringIO()
            with contextlib.redirect_stderr(err):
                rc=seventh.main([
                    "--source",str(Path(td)/"absent.zip"),
                    "--db",str(Path(td)/"absent.sqlite"),
                    "--lock",str(Path(td)/"absent.toml"),
                    "--server-jar",str(Path(td)/"absent.jar"),
                    "--output",str(output),
                ])
            self.assertEqual(rc,2)
            self.assertFalse(output.exists())
            self.assertIn("SEVENTH LAYER OPEN",err.getvalue())

    @unittest.skipUnless(shutil.which("javac"),"JDK javac required")
    def test_actual_seventh_source_free_bridge_compiles(self):
        f=seventh.sixth.fifth
        sources=(
            f.fourth.third.second.final.roots.BASE_BRIDGE,
            f.fourth.third.second.final.JAVA_SOURCE,
            f.fourth.third.second.root.JAVA_SOURCE,
            f.fourth.third.second.inner.JAVA_SOURCE,
            f.fourth.third.second.JAVA_SOURCE,
            f.fourth.third.JAVA_SOURCE,
            f.fourth.JAVA_SOURCE,
            f.JAVA_SOURCE,
            seventh.sixth.JAVA_SOURCE,
            seventh.JAVA_SOURCE,
        )
        with tempfile.TemporaryDirectory() as td:
            result=subprocess.run(
                ["javac","-encoding","UTF-8","-d",td,*(str(p) for p in sources)],
                capture_output=True,text=True,timeout=65,check=False,
            )
            self.assertEqual(result.returncode,0,result.stderr)


if __name__=="__main__":
    unittest.main()
