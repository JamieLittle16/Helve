"""Fail-closed fourth-layer original stock 26.2 graph transport and Java bridge."""
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
import worldgen_26_2_stock_final_density_fourth_layer as fourth  # noqa: E402


class StockFourthLayerTests(unittest.TestCase):
    def stdout(self,*,select_inside:bool=True)->str:
        old=fourth.prior.load()
        density=fourth.DENSITY
        lines=["Original Java logging is ignored, never treated as an evidence frame"]
        for seed_index,seed in enumerate(fourth.third.second.final.SEEDS):
            lines.append("|".join((
                fourth.HEAD,str(seed_index),seed,
                density+"MulOrAdd$Type","MUL","3ff0000000000000",
                density+"Noise",density+"YClampedGradient",
                density+"Noise",density+"Noise",density+"Constant",
                "bff0000000000000","3ff0000000000000",
                density+"TwoArgumentSimpleFunction$Type","ADD",
                density+"Noise",density+"Constant",
            )))
            for j in range(32):
                i=seed_index*32+j
                left,holder,_,_,outside,mul=old[i]
                selector="0000000000000000" if select_inside else "4000000000000000"
                inp=outside if select_inside else "0000000000000000"
                out="0000000000000000" if select_inside else outside
                lines.append("|".join((
                    fourth.VALUE,str(i),
                    left,left,holder,holder,
                    selector,inp,out,outside,
                    mul,"0000000000000000",mul,
                )))
            lines.append("|".join((fourth.END,str(seed_index),"32")))
        return "\n".join(lines)+"\n"

    def methods(self)->dict:
        methods={}
        root=fourth.third.second.root
        for name in ("ap2_compute","holder_holder_compute"):
            owner,sig,body,normalized=root.frozen_final.METHODS[name]
            methods[name]={
                "owner":owner,"signature":sig,"body_sha256":body,
                "normalized_sha256":normalized,"reviewed":False,
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
        shapes,vectors=fourth.parse_output(self.stdout())
        return {
            "schema":1,"kind":fourth.KIND,"minecraft":"26.2","protocol":776,
            "data_version":4903,
            "source_archive_sha256":fourth.third.second.final.frozen.SOURCE_SHA256,
            "official_server_sha256":fourth.third.second.final.frozen.SERVER_SHA256,
            "prior_third_fixture_sha256":fourth.prior.SHA256,
            "prior_third_report_sha256":fourth.prior.ORIGINAL_JSON_SHA256,
            "source_methods":self.methods(),
            "world_seeds":list(fourth.third.second.final.SEEDS),
            "point_count_per_seed":32,
            "sample_context":"DensityFunction$SinglePointContext",
            "original_stock_registry_used":True,
            "new_fourth_layer_inputs_observed":True,
            "shapes":shapes,"vectors":vectors,
            **{k:False for k in fourth.GATES},
        }

    def test_128_observations_strict_parent_bound(self):
        shapes,vectors=fourth.parse_output(self.stdout())
        self.assertEqual((len(shapes),len(vectors)),(4,128))
        self.assertEqual(shapes[0]["left_mul_op"],"MUL")
        self.assertEqual(shapes[0]["right_ap2_op"],"ADD")
        self.assertEqual(vectors[0]["left_mul_output_bits"][2:],
                         fourth.prior.load()[0][0])
        fourth.validate(self.report())

    def test_both_nested_range_branches_can_be_selected(self):
        for is_inside in (True,False):
            shapes,vectors=fourth.parse_output(
                self.stdout(select_inside=is_inside))
            self.assertEqual(len(shapes),4)
            self.assertEqual(len(vectors),128)

    def test_mutation_of_source_pin_or_old_anchors_fails(self):
        raw=self.stdout().splitlines()
        changes=[
            lambda lines:lines.pop(2),
            lambda lines:lines.append(lines[-1]),
            lambda lines:lines.__setitem__(1,lines[1].replace(
                "MulOrAdd$Type","UnknownType",1)),
            lambda lines:lines.__setitem__(1,lines[1].replace(
                "|MUL|","|MIN|",1)),
            lambda lines:lines.__setitem__(1,lines[1].replace(
                "|3ff0000000000000|","|7ff0000000000000|",1)),
            lambda lines:lines.__setitem__(2,lines[2].replace(
                fourth.prior.load()[0][0],"0000000000000001",1)),
            lambda lines:lines.__setitem__(1,lines[1].replace(
                fourth.third.second.final.SEEDS[0],
                fourth.third.second.final.SEEDS[1])),
        ]
        for i,change in enumerate(changes):
            lines=raw.copy()
            change(lines)
            with self.subTest(i=i),self.assertRaises(fourth.FourthLayerError):
                fourth.parse_output("\n".join(lines))
        for field in ("prior_third_fixture_sha256","prior_third_report_sha256",
                      "source_archive_sha256","official_server_sha256"):
            report=self.report()
            report[field]="f"*64
            with self.subTest(field=field),self.assertRaises(fourth.FourthLayerError):
                fourth.validate(report)
        for gate in fourth.GATES:
            report=self.report()
            report[gate]=True
            with self.subTest(gate=gate),self.assertRaises(fourth.FourthLayerError):
                fourth.validate(report)

    def test_no_private_source_never_emits_fake_capture(self):
        with tempfile.TemporaryDirectory() as td:
            output=Path(td)/"never.json"
            err=io.StringIO()
            with contextlib.redirect_stderr(err):
                rc=fourth.main([
                    "--source",str(Path(td)/"missing.zip"),
                    "--db",str(Path(td)/"missing.sqlite"),
                    "--lock",str(Path(td)/"missing.toml"),
                    "--server-jar",str(Path(td)/"missing.jar"),
                    "--output",str(output),
                ])
            self.assertEqual(rc,2)
            self.assertFalse(output.exists())
            self.assertIn("FOURTH LAYER OPEN",err.getvalue())

    @unittest.skipUnless(shutil.which("javac"),"JDK compiler required")
    def test_original_jvm_fourth_bridge_compiles_without_vanilla_binary(self):
        java=(
            fourth.third.second.final.roots.BASE_BRIDGE,
            fourth.third.second.final.JAVA_SOURCE,
            fourth.third.second.root.JAVA_SOURCE,
            fourth.third.second.inner.JAVA_SOURCE,
            fourth.third.second.JAVA_SOURCE,
            fourth.third.JAVA_SOURCE,
            fourth.JAVA_SOURCE,
        )
        with tempfile.TemporaryDirectory() as td:
            result=subprocess.run(
                ["javac","-encoding","UTF-8","-d",td,*(str(x) for x in java)],
                capture_output=True,text=True,timeout=60,check=False,
            )
            self.assertEqual(result.returncode,0,result.stderr)


if __name__=="__main__":
    unittest.main()
