"""Fail-closed real 26.2 finalDensity operator/map/holder child diagnosis."""
from __future__ import annotations

import contextlib
import copy
import io
import json
import shutil
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import worldgen_26_2_stock_final_density_root_semantics as r  # noqa: E402


class RealRootSemanticsTests(unittest.TestCase):
    @staticmethod
    def stdout()->str:
        bits=r.frozen_final.load_bits()
        lines=["original Minecraft startup lines are not diagnostic tags"]
        for seed_index,seed in enumerate(r.final.SEEDS):
            lines.append("|".join((
                r.HEAD,str(seed_index),seed,
                "net.minecraft.world.level.levelgen.DensityFunctions$Ap2$Type","ADD",
                "net.minecraft.world.level.levelgen.DensityFunctions$Mapped$Type","SQUEEZE",
                "net.minecraft.world.level.levelgen.DensityFunctions$Marker",
                "net.minecraft.world.level.levelgen.DensityFunctions$RangeChoice",
                "bff0000000000000","3ff0000000000000",
            )))
            for point in range(32):
                idx=seed_index*32+point
                lines.append("|".join((
                    r.VALUE,str(idx),"0000000000000000",
                    "3ff0000000000000",bits[idx],
                )))
            lines.append("|".join((r.END,str(seed_index),"32")))
        return "\n".join(lines)+"\n"

    @staticmethod
    def methods():
        identities={}
        for name,pin in (
            ("ap2_compute",r.frozen_final.METHODS["ap2_compute"]),
            ("holder_holder_compute",r.frozen_final.METHODS["holder_holder_compute"]),
        ):
            identities[name]=dict(zip(
                ("owner","signature","body_sha256","normalized_sha256"),pin,
                strict=True,
            ),reviewed=False)
        identities["mapped_compute"]={
            "owner":r.final.MAPPED,
            "signature":"compute(final DensityFunction . FunctionContext context)",
            "body_sha256":"a"*64,"normalized_sha256":"b"*64,"reviewed":False,
        }
        return identities

    def manifest(self):
        shapes,vectors=r.parse_output(self.stdout())
        return {
            "schema":1,"kind":r.KIND,"minecraft":"26.2","protocol":776,
            "data_version":4903,
            "source_archive_sha256":r.final.frozen.SOURCE_SHA256,
            "official_server_sha256":r.final.frozen.SERVER_SHA256,
            "original_final_density_fixture_sha256":r.frozen_final.FIXTURE_SHA256,
            "original_final_density_json_sha256":r.frozen_final.ORIGINAL_JSON_SHA256,
            "source_methods":self.methods(),"world_seeds":list(r.final.SEEDS),
            "point_count_per_seed":32,
            "sample_context":"DensityFunction$SinglePointContext",
            "original_stock_registry_used":True,
            "operator_class_identity_observed":True,"first_child_values_observed":True,
            "shapes":shapes,"vectors":vectors,
            **{gate:False for gate in r.GATES},
        }

    def test_exact_four_root_shapes_and_independent_128_output_words(self):
        shapes,vectors=r.parse_output(self.stdout())
        self.assertEqual(len(shapes),4)
        self.assertEqual(len(vectors),128)
        self.assertEqual(shapes[0]["ap2_operator"],"ADD")
        self.assertEqual(shapes[0]["mapped_transform"],"SQUEEZE")
        self.assertEqual(shapes[0]["holder_target_class"].split("$")[-1],"RangeChoice")
        self.assertEqual(
            [row["final_density_bits"][2:] for row in vectors],
            list(r.frozen_final.load_bits()),
        )
        r.validate(self.manifest())

    def test_cannot_silent_accept_mismatched_official_root_or_noise_context(self):
        lines=self.stdout().splitlines()
        mutations=(
            lambda x:x.pop(1),
            lambda x:x.append(x[-1]),
            lambda x:x.__setitem__(1,x[1].replace("|ADD|","|BAD-TYPE|")),
            lambda x:x.__setitem__(1,x[1].replace("|ADD|","|BOGUS|")),
            lambda x:x.__setitem__(1,x[1].replace("|SQUEEZE|","|WUT|")),
            lambda x:x.__setitem__(2,x[2].replace("|0000000000000000|","|zzz|")),
            lambda x:x.__setitem__(2,x[2].replace("0000000000000000","7ff8000000000000")),
            lambda x:x.__setitem__(2,x[2][:-16]+"7ff0000000000000"),
            lambda x:x.__setitem__(2,x[2].replace("|0|","|9|",1)),
            lambda x:x.__setitem__(1,x[1].replace("RangeChoice","HolderHolder")),
            lambda x:x.__setitem__(1,x[1].replace(r.final.SEEDS[0],r.final.SEEDS[1])),
        )
        for i,mutate in enumerate(mutations):
            altered=lines.copy()
            mutate(altered)
            with self.subTest(i=i),self.assertRaises(r.RootSemanticError):
                r.parse_output("\n".join(altered))

    def test_report_flags_source_methods_and_coordinate_mutations_fail(self):
        original=self.manifest()
        for flag in r.GATES:
            altered=copy.deepcopy(original)
            altered[flag]=True
            with self.subTest(flag=flag),self.assertRaises(r.RootSemanticError):
                r.validate(altered)
        cases=(
            lambda x:x["source_methods"]["ap2_compute"].__setitem__("reviewed",True),
            lambda x:x["source_methods"]["mapped_compute"].__setitem__(
                "normalized_sha256","invalid"),
            lambda x:x["source_methods"]["holder_holder_compute"].__setitem__(
                "body_sha256","0"*64),
            lambda x:x["vectors"][0].__setitem__("block_y",2026),
            lambda x:x["vectors"][0].__setitem__("final_density_bits","0x0000000000000000"),
            lambda x:x["shapes"][2].__setitem__("mapped_transform","HALF_NEGATIVE"),
            lambda x:x["shapes"][3].__setitem__("holder_target_class",
                "net.minecraft.world.level.levelgen.DensityFunctions$Marker"),
        )
        for i,mutate in enumerate(cases):
            wrong=copy.deepcopy(original)
            mutate(wrong)
            with self.subTest(case=i),self.assertRaises(r.RootSemanticError):
                r.validate(wrong)

    def test_source_mapped_identity_requires_unique_exact_method(self):
        conn=sqlite3.connect(":memory:")
        conn.row_factory=sqlite3.Row
        conn.executescript("""
            CREATE TABLE types(id INTEGER PRIMARY KEY,qualified_name TEXT);
            CREATE TABLE methods(id INTEGER PRIMARY KEY,type_id INTEGER,name TEXT,
                signature TEXT,param_count INTEGER,body_sha256 TEXT,normalized_sha256 TEXT);
        """)
        for i,(_,owner) in enumerate(
            (("ap2",r.final.FINAL),("mapped",r.final.MAPPED),
             ("holder",r.final.HOLDER)),start=1
        ):
            conn.execute("INSERT INTO types VALUES(?,?)",(i,owner))
            conn.execute(
                "INSERT INTO methods VALUES(?,?,?,?,?,?,?)",
                (i,i,"compute","compute(FunctionContext)",1,"a"*64,"b"*64),
            )
        ids=r.source_methods(conn)
        self.assertEqual(set(ids),set(self.methods()))
        self.assertFalse(ids["mapped_compute"]["reviewed"])
        conn.execute("DELETE FROM methods WHERE id=2")
        with self.assertRaises(r.RootSemanticError):
            r.source_methods(conn)
        conn.close()

    def test_no_private_source_cannot_produce_forged_original_packet(self):
        with tempfile.TemporaryDirectory() as td:
            base=Path(td)
            err=io.StringIO()
            with contextlib.redirect_stderr(err):
                rc=r.main([
                    "--source",str(base/"missing.zip"),
                    "--db",str(base/"missing.sqlite"),
                    "--lock",str(base/"missing.toml"),
                    "--server-jar",str(base/"missing.jar"),
                    "--output",str(base/"packet.json"),
                ])
            self.assertEqual(rc,2)
            self.assertFalse((base/"packet.json").exists())
            self.assertIn("FINAL ROOT SEMANTIC REVIEW OPEN",err.getvalue())

    @unittest.skipUnless(shutil.which("javac"),"JDK required")
    def test_pinned_bounded_root_reflection_bridge_compiles_without_minecraft_code(self):
        with tempfile.TemporaryDirectory() as td:
            sources=(r.final.roots.BASE_BRIDGE,r.final.JAVA_SOURCE,r.JAVA_SOURCE)
            result=subprocess.run(
                ["javac","-encoding","UTF-8","-d",td,*(str(x) for x in sources)],
                capture_output=True,text=True,timeout=50,check=False,
            )
            self.assertEqual(result.returncode,0,result.stderr)


if __name__=="__main__":
    unittest.main()
