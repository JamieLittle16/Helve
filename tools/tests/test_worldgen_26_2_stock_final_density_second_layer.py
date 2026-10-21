"""Strict source-free transport tests for real stock 26.2 second-layer review."""
from __future__ import annotations

import contextlib
import copy
import io
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
import subprocess

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import worldgen_26_2_stock_final_density_second_layer as second  # noqa: E402


class StockSecondLayerTests(unittest.TestCase):
    def stdout(self)->str:
        prev=second.prior.load()
        lines=["Normal private stock Minecraft logging is not a protocol row"]
        for seed_index,seed in enumerate(second.final.SEEDS):
            lines.append("|".join((
                second.HEAD,str(seed_index),seed,
                second.DENSITY+"MulOrAdd$Type",
                "MUL","3ff0000000000000",
                second.DENSITY+"Noise",
                second.DENSITY+"Marker$Type",
                "Interpolated",second.DENSITY+"MulOrAdd",
                second.DENSITY+"TwoArgumentSimpleFunction$Type",
                "ADD",second.DENSITY+"Noise",second.DENSITY+"Constant",
            )))
            for j in range(32):
                i=seed_index*32+j
                earlier=prev[i]
                lines.append("|".join((
                    second.VALUE,str(i),
                    earlier[1],earlier[1],
                    "3fe0000000000000",earlier[3],
                    "3fe0000000000000","3fe0000000000000",earlier[5],
                )))
            lines.append("|".join((second.END,str(seed_index),"32")))
        return "\n".join(lines)+"\n"

    def methods(self)->dict:
        records={}
        for name in ("ap2_compute","holder_holder_compute"):
            owner,signature,body,normalized=second.root.frozen_final.METHODS[name]
            records[name]={
                "owner":owner,"signature":signature,
                "body_sha256":body,"normalized_sha256":normalized,
                "reviewed":False,
            }
        records["mapped_delegate_compute"]={
            "owner":second.root.PURE_TRANSFORMER,
            "signature":"compute(final DensityFunction . FunctionContext context)",
            "body_sha256":second.root.PURE_COMPUTE_SHA256,
            "normalized_sha256":"a"*64,
            "reviewed":False,
        }
        return records

    def report(self)->dict:
        shapes,vectors=second.parse_output(self.stdout())
        return {
            "schema":1,"kind":second.KIND,"minecraft":"26.2",
            "protocol":776,"data_version":4903,
            "source_archive_sha256":second.final.frozen.SOURCE_SHA256,
            "official_server_sha256":second.final.frozen.SERVER_SHA256,
            "prior_inner_fixture_sha256":second.prior.SHA256,
            "prior_inner_report_sha256":second.prior.ORIGINAL_JSON_SHA256,
            "source_methods":self.methods(),
            "world_seeds":list(second.final.SEEDS),
            "point_count_per_seed":32,
            "sample_context":"DensityFunction$SinglePointContext",
            "original_stock_registry_used":True,
            "new_second_layer_inputs_observed":True,
            "shapes":shapes,"vectors":vectors,
            **{k:False for k in second.GATES},
        }

    def test_real_previous_inner_oracle_is_anchored_all_128(self):
        s,v=second.parse_output(self.stdout())
        self.assertEqual(len(s),4)
        self.assertEqual(len(v),128)
        self.assertEqual(s[0]["mul_op"],"MUL")
        self.assertEqual(v[21]["outer_output_bits"],"0x"+second.prior.load()[21][5])
        second.validate(self.report())

    def test_specifictype_enum_and_real_operand_bits_fail_closed(self):
        # MulOrAdd.specificType is a *record* component. type() is a
        # different inherited interface method; do not conflate them.
        java=second.JAVA_SOURCE.read_text(encoding="utf-8")
        self.assertIn('member(mul,"specificType")',java)
        self.assertNotIn('enumClass(mul,"type")',java)
        original=self.stdout().splitlines()
        for changed in ("wrong_enum","wrong_op","wrong_argument","wrong_input"):
            lines=original.copy()
            if changed=="wrong_enum":
                lines[1]=lines[1].replace(
                    second.DENSITY+"MulOrAdd$Type",
                    second.DENSITY+"TwoArgumentSimpleFunction$Type",1)
            elif changed=="wrong_op":
                lines[1]=lines[1].replace("|MUL|","|MIN|",1)
            elif changed=="wrong_argument":
                lines[1]=lines[1].replace(
                    "|3ff0000000000000|","|3fe0000000000000|",1)
            else:
                fields=lines[2].split("|")
                fields[2]=f"{int(fields[2],16)^1:016x}"
                lines[2]="|".join(fields)
            with self.subTest(changed=changed),self.assertRaises(second.SecondLayerError):
                second.parse_output("\n".join(lines))

    def test_cold_qualification_gates_remain_false(self):
        report=self.report()
        for gate in second.GATES:
            mutated=copy.deepcopy(report)
            mutated[gate]=True
            with self.subTest(gate=gate),self.assertRaises(second.SecondLayerError):
                second.validate(mutated)
        for key in ("source_archive_sha256","official_server_sha256",
                    "prior_inner_fixture_sha256","prior_inner_report_sha256"):
            mutated=copy.deepcopy(report)
            mutated[key]="a"*64
            with self.subTest(key=key),self.assertRaises(second.SecondLayerError):
                second.validate(mutated)

    def test_frame_source_and_original_operand_mutations_fail_closed(self):
        lines=self.stdout().splitlines()
        modifications=[
            lambda x:x.pop(2),
            lambda x:x.append(x[-1]),
            lambda x:x.__setitem__(1,x[1].replace("DensityFunctions$Noise","UntrustedInput",1)),
            lambda x:x.__setitem__(1,x[1].replace("|MUL|","|mul with spaces|",1)),
            lambda x:x.__setitem__(1,x[1].replace("|3ff0000000000000|","|7ff0000000000000|",1)),
            lambda x:x.__setitem__(2,x[2].replace("|"+second.prior.load()[0][1]+"|","|0000000000000000|",1)),
            lambda x:x.__setitem__(2,x[2][:-16]+"7ff8000000000000"),
            lambda x:x.__setitem__(1,x[1].replace(second.final.SEEDS[0],second.final.SEEDS[1])),
        ]
        for index,change in enumerate(modifications):
            case=lines.copy()
            change(case)
            with self.subTest(case=index),self.assertRaises(second.SecondLayerError):
                second.parse_output("\n".join(case))
        malformed=self.report()
        malformed["vectors"][0]["mul_input_bits"]="0xzzz"
        with self.assertRaises(second.SecondLayerError):
            second.validate(malformed)

    def test_original_method_sha_mismatch_cannot_admit(self):
        for label in ("ap2_compute","mapped_delegate_compute","holder_holder_compute"):
            report=self.report()
            report["source_methods"][label]["body_sha256"]="f"*64
            with self.subTest(method=label),self.assertRaises(second.SecondLayerError):
                second.validate(report)

    def test_no_private_source_fails_without_creating_output(self):
        with tempfile.TemporaryDirectory() as td:
            dest=Path(td)/"not-produced.json"
            err=io.StringIO()
            with contextlib.redirect_stderr(err):
                code=second.main([
                    "--source",str(Path(td)/"missing.zip"),
                    "--db",str(Path(td)/"missing.sqlite"),
                    "--lock",str(Path(td)/"missing.toml"),
                    "--server-jar",str(Path(td)/"missing.jar"),
                    "--output",str(dest),
                ])
            self.assertEqual(code,2)
            self.assertFalse(dest.exists())
            self.assertIn("SECOND LAYER OPEN",err.getvalue())

    @unittest.skipUnless(shutil.which("javac"),"JDK compiler required")
    def test_read_only_original_jvm_bridge_compiles_source_free(self):
        java=(
            second.final.roots.BASE_BRIDGE,second.final.JAVA_SOURCE,
            second.root.JAVA_SOURCE,second.inner.JAVA_SOURCE,second.JAVA_SOURCE,
        )
        with tempfile.TemporaryDirectory() as td:
            result=subprocess.run(
                ["javac","-encoding","UTF-8","-d",td,*(str(x) for x in java)],
                text=True,capture_output=True,timeout=60,check=False,
            )
            self.assertEqual(result.returncode,0,result.stderr)


if __name__=="__main__":
    unittest.main()
