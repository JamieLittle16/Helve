"""Source-free original Java 26.2 finalDensity inner-graph review transport."""
from __future__ import annotations

import contextlib
import copy
import io
import shutil
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import worldgen_26_2_stock_final_density_inner_semantics as inner  # noqa: E402


class StockFinalDensityInnerFrontierTests(unittest.TestCase):
    @staticmethod
    def stdout()->str:
        anchor=inner.observed.read_words()
        lines=["Stock vanilla startup logs do not count as diagnostic records"]
        for seed_idx,seed in enumerate(inner.final.SEEDS):
            lines.append("|".join((
                inner.HEAD,str(seed_idx),seed,
                "net.minecraft.world.level.levelgen.DensityFunctions$Marker$Type",
                "CacheAllInCell",
                "net.minecraft.world.level.levelgen.DensityFunctions$Ap2",
                "net.minecraft.world.level.levelgen.DensityFunctions$Marker",
                "net.minecraft.world.level.levelgen.DensityFunctions$Constant",
                "net.minecraft.world.level.levelgen.DensityFunctions$Ap2",
                "bff0000000000000","3ff0000000000000",
            )))
            for point in range(32):
                i=seed_idx*32+point
                mapped,holder,_=anchor[i]
                lines.append("|".join((
                    inner.VALUE,str(i),mapped,mapped,mapped,
                    "0000000000000000",holder,
                    "3ff0000000000000",holder,
                )))
            lines.append("|".join((inner.END,str(seed_idx),"32")))
        return "\n".join(lines)+"\n"

    @staticmethod
    def methods()->dict:
        records={}
        for name in ("ap2_compute","holder_holder_compute"):
            owner,signature,body,normalized=inner.root.frozen_final.METHODS[name]
            records[name]=dict(
                owner=owner,signature=signature,
                body_sha256=body,normalized_sha256=normalized,reviewed=False,
            )
        records["mapped_delegate_compute"]={
            "owner":inner.root.PURE_TRANSFORMER,
            "signature":"compute(final DensityFunction . FunctionContext context)",
            "body_sha256":inner.root.PURE_COMPUTE_SHA256,
            "normalized_sha256":"ffe3db23debf52e4fabf8c146b01fa7ce9f91f9d8a0b896196b3ad0ae428e8d0",
            "reviewed":False,
        }
        return records

    def report(self)->dict:
        shapes,values=inner.parse_output(self.stdout())
        return {
            "schema":1,"kind":inner.KIND,
            "minecraft":"26.2","protocol":776,"data_version":4903,
            "source_archive_sha256":inner.final.frozen.SOURCE_SHA256,
            "official_server_sha256":inner.final.frozen.SERVER_SHA256,
            "prior_first_level_operand_sha256":inner.observed.FIXTURE_SHA256,
            "prior_original_first_level_report_sha256":inner.observed.ORIGINAL_JSON_SHA256,
            "source_methods":self.methods(),"world_seeds":list(inner.final.SEEDS),
            "point_count_per_seed":32,
            "sample_context":"DensityFunction$SinglePointContext",
            "original_stock_registry_used":True,
            "new_marker_range_branch_bits_observed":True,
            "shapes":shapes,"vectors":values,
            **{gate:False for gate in inner.GATES},
        }

    def test_all_128_inner_points_bind_old_source_free_operand_fixture(self):
        shapes,values=inner.parse_output(self.stdout())
        self.assertEqual(len(shapes),4)
        self.assertEqual(len(values),128)
        self.assertEqual(shapes[0]["marker_kind"],"CacheAllInCell")
        self.assertEqual(values[0]["mapped_bits"],
                         "0x"+inner.observed.read_words()[0][0])
        self.assertEqual(values[21]["holder_bits"],
                         "0x"+inner.observed.read_words()[21][1])
        inner.validate(self.report())

    def test_exact_marker_type_accepts_realistic_java_enum_name_shapes(self):
        # These are synthetic transport fixtures, not a claim that any
        # particular enum value is present at the actual pinned Overworld root.
        baseline=self.stdout()
        for name in ("CacheAllInCell","Cache2D","Interpolated","CACHE_ALL_IN_CELL"):
            modified=baseline.replace("|CacheAllInCell|","|"+name+"|")
            with self.subTest(name=name):
                shapes,vectors=inner.parse_output(modified)
                self.assertEqual([shape["marker_kind"] for shape in shapes],[name]*4)
                self.assertEqual(len(vectors),128)

    def test_rejects_invalid_enum_identifiers_and_changed_declaring_classes(self):
        original=self.stdout()
        for name in ("cache-all-in-cell","2DCache","Name With Spaces","x"*81):
            modified=original.replace("|CacheAllInCell|","|"+name+"|")
            with self.subTest(name=name),self.assertRaisesRegex(
                inner.InnerFrontierError,"Marker enum identifier"
            ):
                inner.parse_output(modified)
        modified=original.replace(
            "DensityFunctions$Marker$Type",
            "DensityFunctions$Unrelated$Type",
        )
        with self.assertRaisesRegex(inner.InnerFrontierError,"declaring class"):
            inner.parse_output(modified)

    def test_no_false_scope_admission(self):
        base=self.report()
        for gate in inner.GATES:
            mutated=copy.deepcopy(base)
            mutated[gate]=True
            with self.subTest(gate=gate),self.assertRaises(inner.InnerFrontierError):
                inner.validate(mutated)
        for field in ("source_archive_sha256","official_server_sha256",
                      "prior_first_level_operand_sha256","prior_original_first_level_report_sha256"):
            mutated=copy.deepcopy(base)
            mutated[field]="0"*64
            with self.subTest(field=field),self.assertRaises(inner.InnerFrontierError):
                inner.validate(mutated)

    def test_strict_stock_frame_and_identity_mutations(self):
        baseline=self.stdout().splitlines()
        variants=(
            lambda x:x.pop(1),
            lambda x:x.append(x[-1]),
            lambda x:x.__setitem__(1,x[1].replace("CacheAllInCell","BOGUS-TYPE")),
            lambda x:x.__setitem__(1,x[1].replace("DensityFunctions$Marker$Type","SomethingElse")),
            lambda x:x.__setitem__(
                2,"|".join([*x[2].split("|")[:4],"0000000000000000",*x[2].split("|")[5:]])
            ),
            lambda x:x.__setitem__(2,x[2][:-16]+"7ff8000000000000"),
            lambda x:x.__setitem__(2,x[2].replace("|0|","|8|",1)),
            lambda x:x.__setitem__(1,x[1].replace(inner.final.SEEDS[0],inner.final.SEEDS[1])),
        )
        for i,change in enumerate(variants):
            mutated=baseline.copy()
            change(mutated)
            with self.subTest(i=i),self.assertRaises(inner.InnerFrontierError):
                inner.parse_output("\n".join(mutated))
        bogus=self.report()
        bogus["vectors"][0]["marker_bits"]="0xwat"
        with self.assertRaises(inner.InnerFrontierError):
            inner.validate(bogus)

    def test_provenance_source_fingerprints_are_pinned(self):
        base=self.report()
        for path,value in (
            ("ap2_compute","reviewed"),
            ("mapped_delegate_compute","body_sha256"),
            ("holder_holder_compute","owner"),
        ):
            bad=copy.deepcopy(base)
            bad["source_methods"][path][value]="a"*64
            with self.subTest(method=path),self.assertRaises(inner.InnerFrontierError):
                inner.validate(bad)

    def test_missing_real_source_cannot_forge_evidence(self):
        with tempfile.TemporaryDirectory() as td:
            target=Path(td)/"not-published.json"
            stderr=io.StringIO()
            with contextlib.redirect_stderr(stderr):
                rc=inner.main([
                    "--source",str(Path(td)/"missing.zip"),
                    "--db",str(Path(td)/"missing.sqlite"),
                    "--lock",str(Path(td)/"missing.toml"),
                    "--server-jar",str(Path(td)/"missing.jar"),
                    "--output",str(target),
                ])
            self.assertEqual(rc,2)
            self.assertFalse(target.exists())
            self.assertIn("FINAL INNER REVIEW OPEN",stderr.getvalue())

    @unittest.skipUnless(shutil.which("javac"),"JDK compiler required")
    def test_reflection_bridge_compiles_without_minecraft_classpath(self):
        sources=(inner.final.roots.BASE_BRIDGE,inner.final.JAVA_SOURCE,
                 inner.root.JAVA_SOURCE,inner.JAVA_SOURCE)
        with tempfile.TemporaryDirectory() as td:
            result=subprocess.run(
                ["javac","-encoding","UTF-8","-d",td,*(str(s) for s in sources)],
                capture_output=True,text=True,timeout=60,check=False,
            )
            self.assertEqual(result.returncode,0,result.stderr)


if __name__=="__main__":
    unittest.main()
