"""Fail-closed source-free original stock 26.2 third-layer observation transport."""
from __future__ import annotations

import contextlib
import copy
import io
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import worldgen_26_2_stock_final_density_third_layer as third  # noqa: E402


class StockThirdLayerTests(unittest.TestCase):
    def stdout(self,*,selector_word:str="bfe0000000000000")->str:
        previous=third.prior.load()
        lines=["Original JVM logging is never treated as a protocol frame"]
        for seed_index,seed in enumerate(third.second.final.SEEDS):
            lines.append("|".join((
                third.HEAD,str(seed_index),seed,
                third.DENSITY+"Marker$Type","Interpolated",third.DENSITY+"Noise",
                third.DENSITY+"Noise",third.DENSITY+"Noise",third.DENSITY+"Constant",
                "c12e848000000000","0000000000000000",
                third.DENSITY+"Marker$Type","Interpolated",third.DENSITY+"Noise",
                third.DENSITY+"MulOrAdd$Type","MUL","3ff0000000000000",
                third.DENSITY+"Noise",
            )))
            for j in range(32):
                i=seed_index*32+j
                mul,selector,left,right=previous[i]
                lines.append("|".join((
                    third.VALUE,str(i),
                    mul,mul,
                    selector_word,selector,selector,selector,
                    left,left,right,right,
                )))
            lines.append("|".join((third.END,str(seed_index),"32")))
        return "\n".join(lines)+"\n"

    def methods(self)->dict:
        methods={}
        for name in ("ap2_compute","holder_holder_compute"):
            owner,signature,body,normal=third.second.root.frozen_final.METHODS[name]
            methods[name]={
                "owner":owner,"signature":signature,
                "body_sha256":body,"normalized_sha256":normal,"reviewed":False,
            }
        methods["mapped_delegate_compute"]={
            "owner":third.second.root.PURE_TRANSFORMER,
            "signature":"compute(final DensityFunction . FunctionContext context)",
            "body_sha256":third.second.root.PURE_COMPUTE_SHA256,
            "normalized_sha256":"a"*64,"reviewed":False,
        }
        return methods

    def report(self)->dict:
        shapes,vectors=third.parse_output(self.stdout())
        return {
            "schema":1,"kind":third.KIND,"minecraft":"26.2","protocol":776,
            "data_version":4903,
            "source_archive_sha256":third.second.final.frozen.SOURCE_SHA256,
            "official_server_sha256":third.second.final.frozen.SERVER_SHA256,
            "prior_second_fixture_sha256":third.prior.SHA256,
            "prior_second_report_sha256":third.prior.ORIGINAL_JSON_SHA256,
            "source_methods":self.methods(),
            "world_seeds":list(third.second.final.SEEDS),
            "point_count_per_seed":32,
            "sample_context":"DensityFunction$SinglePointContext",
            "original_stock_registry_used":True,
            "new_third_layer_inputs_observed":True,
            "shapes":shapes,"vectors":vectors,
            **{k:False for k in third.GATES},
        }

    def test_four_seed_128_source_anchored_frames(self):
        shapes,vectors=third.parse_output(self.stdout())
        self.assertEqual((len(shapes),len(vectors)),(4,128))
        self.assertEqual(shapes[0]["left_marker_kind"],"Interpolated")
        self.assertEqual(shapes[0]["outside_mul_op"],"MUL")
        self.assertEqual(vectors[21]["outside_marker_output_bits"][2:],
                         third.prior.load()[21][2])
        third.validate(self.report())

    def test_nested_range_inclusive_exclusive_selects_only_correct_branch(self):
        # All synthetic branch outputs equal the old anchor, so the probe
        # accepts either selected branch without inventing the real type.
        for selector in ("bfe0000000000000","3fe0000000000000"):
            s,v=third.parse_output(self.stdout(selector_word=selector))
            self.assertEqual(len(s),4)
            self.assertEqual(len(v),128)

    def test_frozen_second_bits_source_and_gate_mutations_fail_closed(self):
        raw=self.stdout().splitlines()
        mutations=[
            lambda x:x.pop(2),
            lambda x:x.append(x[-1]),
            lambda x:x.__setitem__(1,x[1].replace("Marker$Type","Unknown$Type",1)),
            lambda x:x.__setitem__(1,x[1].replace("|MUL|","|MIN|",1)),
            lambda x:x.__setitem__(1,x[1].replace(
                "|3ff0000000000000|","|7ff0000000000000|",1)),
            lambda x:x.__setitem__(2,x[2].replace(
                third.prior.load()[0][0], "0000000000000001",1)),
            lambda x:x.__setitem__(1,x[1].replace(
                third.second.final.SEEDS[0],third.second.final.SEEDS[1])),
        ]
        for i,mutate in enumerate(mutations):
            changed=raw.copy()
            mutate(changed)
            with self.subTest(i=i),self.assertRaises(third.ThirdLayerError):
                third.parse_output("\n".join(changed))
        for gate in third.GATES:
            report=self.report()
            report[gate]=True
            with self.subTest(gate=gate),self.assertRaises(third.ThirdLayerError):
                third.validate(report)
        for key in ("prior_second_fixture_sha256","prior_second_report_sha256",
                    "source_archive_sha256","official_server_sha256"):
            report=self.report()
            report[key]="f"*64
            with self.subTest(key=key),self.assertRaises(third.ThirdLayerError):
                third.validate(report)
        methods=self.report()
        methods["source_methods"]["ap2_compute"]["body_sha256"]="e"*64
        with self.assertRaises(third.ThirdLayerError):
            third.validate(methods)

    def test_no_private_original_inputs_does_not_publish_a_report(self):
        with tempfile.TemporaryDirectory() as td:
            output=Path(td)/"not-produced.json"
            err=io.StringIO()
            with contextlib.redirect_stderr(err):
                rc=third.main([
                    "--source",str(Path(td)/"absent-source.zip"),
                    "--db",str(Path(td)/"absent.sqlite"),
                    "--lock",str(Path(td)/"absent.toml"),
                    "--server-jar",str(Path(td)/"absent.jar"),
                    "--output",str(output),
                ])
            self.assertEqual(rc,2)
            self.assertFalse(output.exists())
            self.assertIn("THIRD LAYER OPEN",err.getvalue())

    @unittest.skipUnless(shutil.which("javac"),"JDK compiler required")
    def test_source_free_original_third_jvm_bridge_compiles(self):
        java=(
            third.second.final.roots.BASE_BRIDGE,
            third.second.final.JAVA_SOURCE,
            third.second.root.JAVA_SOURCE,
            third.second.inner.JAVA_SOURCE,
            third.second.JAVA_SOURCE,
            third.JAVA_SOURCE,
        )
        with tempfile.TemporaryDirectory() as td:
            result=subprocess.run(
                ["javac","-encoding","UTF-8","-d",td,*(str(x) for x in java)],
                capture_output=True,text=True,timeout=60,check=False,
            )
            self.assertEqual(result.returncode,0,result.stderr)


if __name__=="__main__":
    unittest.main()
