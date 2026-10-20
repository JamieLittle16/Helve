"""Strict transport, provenance and closed-gate tests for 26.2 adjacent cells."""
from __future__ import annotations

import copy
import sqlite3
import struct
import sys
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import worldgen_26_2_stock_noisechunk_adjacent_capture as adjacent  # noqa: E402
import worldgen_26_2_stock_noisechunk_cell_capture as cell  # noqa: E402
import worldgen_26_2_stock_noisechunk_cell_fixture as previous  # noqa: E402


class AdjacentStockNoiseChunkTests(unittest.TestCase):
    @staticmethod
    def frames():
        rows=["vanilla startup output"]
        for si,seed in enumerate(adjacent.SEEDS):
            for chunk_index,origin in enumerate(adjacent.CHUNK_ORIGINS):
                rows.append(
                    f"{adjacent.HEAD}|{si}|{seed}|{chunk_index}|{origin}|{origin}|"
                    f"4|8|-64|384|{adjacent.AP2}|96"
                )
                for pi,(x,y,z) in enumerate(adjacent.points(chunk_index)):
                    index=si*192+chunk_index*96+pi
                    value=struct.pack(">d",float(x+y+z)).hex()
                    rows.append(f"{adjacent.BIT}|{index}|{x}|{y}|{z}|{value}")
                rows.append(f"{adjacent.END}|{si}|{chunk_index}|96")
        return rows

    @staticmethod
    def methods():
        m={
            label:{
                "owner":owner,"signature":name+"()",
                "body_sha256":"a"*64,"normalized_sha256":"b"*64,
                "reviewed":False,
            }
            for label,owner,name,arity in cell.METHODS
        }
        for label,owner,name in adjacent.EXTRA_METHODS:
            m[label]={
                "owner":owner,"signature":name+"()",
                "body_sha256":"c"*64,"normalized_sha256":"d"*64,
                "reviewed":False,
            }
        return m

    def manifest(self,bits):
        return {
            "schema":1,"kind":adjacent.KIND,"minecraft":"26.2",
            "protocol":776,"data_version":4903,
            "source_archive_sha256":cell.frozen.SOURCE_SHA256,
            "official_server_sha256":cell.frozen.SERVER_SHA256,
            "previous_original_complete_cell_sha256":
                adjacent.complete.ORIGINAL_JSON_SHA256,
            "source_methods":self.methods(),
            "world_seeds":list(adjacent.SEEDS),
            "chunk_origins":list(adjacent.CHUNK_ORIGINS),
            "sample_context":"NoiseChunk",
            "traversal":
                "EXPERIMENTAL_xcell_zcell_ycell_desc_yblock_desc_xblock_zblock",
            "stock_registry_used":True,
            "stock_noisechunk_adjacent_cells_observed":True,
            "stock_noisechunk_canonical_traversal_qualified":False,
            "stock_noisechunk_full_lifecycle_qualified":False,
            "world_seed_random_state_bound":False,
            "full_router_graph_qualified":False,
            "router_numeric_parity_qualified":False,
            "independent_var_sem_admitted":False,
            "source_text_included":False,
            "production_worldgen_enabled":False,
            "vectors":[dict(row,value_bits=word)
                       for row,word in zip(
                           adjacent.input_rows(),bits,strict=True)],
        }

    def test_two_chunk_origins_have_proper_adjacent_cells(self):
        self.assertEqual(len(adjacent.points(0)),96)
        self.assertEqual(len(adjacent.points(1)),96)
        self.assertEqual(adjacent.points(0)[0],(0,79,0))
        self.assertEqual(adjacent.points(0)[-1],(7,56,7))
        self.assertEqual(adjacent.points(1)[0],(-16,79,-16))
        self.assertEqual(adjacent.points(1)[-1],(-9,56,-9))
        self.assertEqual(len(adjacent.input_rows()),768)
        self.assertEqual(set((y+64)//8 for _,y,_ in adjacent.points(0)),{15,16,17})
        self.assertEqual(set(x//4 for x,_,_ in adjacent.points(1)),{-4,-3})
        self.assertEqual(set(z//4 for _,_,z in adjacent.points(1)),{-4,-3})

    def test_parse_synthetic_original_frame_contract(self):
        output="\n".join(self.frames())
        bits=adjacent.parse_output(output)
        self.assertEqual(len(bits),768)
        self.assertEqual(bits[0],"0x"+struct.pack(">d",79.0).hex())
        adjacent.validate(self.manifest(bits),self.methods())

    def test_missing_duplicate_reordered_nonfinite_and_wrong_frame_fail(self):
        frames=self.frames()
        i=next(n for n,row in enumerate(frames)
               if row.startswith(adjacent.BIT+"|3|"))
        row=frames[i]
        corruption=(
            frames[:i]+frames[i+1:],
            frames[:i]+[row]+frames[i:],
            frames[:-1],
            frames+[frames[-1]],
            frames[:i]+[row.replace("|3|","|30|",1)]+frames[i+1:],
            frames[:i]+[row.rsplit("|",1)[0]+"|7ff0000000000000"]+frames[i+1:],
            frames[:i]+[row.replace("|0|","|100|",1)]+frames[i+1:],
            [f.replace("|96","|128") if f.startswith(adjacent.HEAD)
             else f for f in frames],
            [f.replace(adjacent.AP2,"java.lang.Object")
             if f.startswith(adjacent.HEAD) else f for f in frames],
            [f.replace("|-16|-16|","|-12|-12|")
             if f.startswith(adjacent.HEAD) else f for f in frames],
        )
        for j,invalid in enumerate(corruption):
            with self.subTest(j=j),self.assertRaises(adjacent.AdjacentError):
                adjacent.parse_output("\n".join(invalid))
        with self.assertRaisesRegex(adjacent.AdjacentError,"JVM PHASE"):
            adjacent.parse_output(
                cell.TAG_FAILURE+
                "|adjacent-swapSlices-0-0-0|java.lang.IllegalStateException|"
                "java.lang.reflect.InvocationTargetException|unexpected stock state"
            )

    def test_source_and_qualification_gates_cannot_be_promoted(self):
        m=self.manifest(adjacent.parse_output("\n".join(self.frames())))
        for gate in (
            "stock_noisechunk_canonical_traversal_qualified",
            "stock_noisechunk_full_lifecycle_qualified",
            "world_seed_random_state_bound","full_router_graph_qualified",
            "router_numeric_parity_qualified","independent_var_sem_admitted",
            "production_worldgen_enabled","source_text_included",
        ):
            altered=copy.deepcopy(m);altered[gate]=True
            with self.subTest(gate=gate),self.assertRaises(adjacent.AdjacentError):
                adjacent.validate(altered,self.methods())
        attacks=(
            lambda d:d["vectors"].pop(),
            lambda d:d["vectors"].reverse(),
            lambda d:d["vectors"][95].__setitem__("block_x",15),
            lambda d:d["vectors"][95].__setitem__(
                "value_bits","0x7ff8000000000000"),
            lambda d:d["source_methods"]["chunk_swap"].__setitem__(
                "reviewed",True),
            lambda d:d.__setitem__("previous_original_complete_cell_sha256","0"*64),
            lambda d:d.__setitem__("traversal","canonical"),
            lambda d:d.__setitem__("chunk_origins",[0,16]),
        )
        for j,mutation in enumerate(attacks):
            altered=copy.deepcopy(m);mutation(altered)
            with self.subTest(attack=j),self.assertRaises(adjacent.AdjacentError):
                adjacent.validate(altered,self.methods())

    def test_new_source_method_identities_are_unique_unreviewed_and_pinned(self):
        db=sqlite3.connect(":memory:")
        db.row_factory=sqlite3.Row
        db.executescript("""
            CREATE TABLE types(id INTEGER PRIMARY KEY,qualified_name TEXT);
            CREATE TABLE methods(id INTEGER PRIMARY KEY,type_id INTEGER,
              name TEXT,signature TEXT,param_count INTEGER,
              body_sha256 TEXT,normalized_sha256 TEXT);
        """)
        for i,(_,owner,name) in enumerate(adjacent.EXTRA_METHODS,1):
            db.execute("INSERT INTO types VALUES(?,?)",(i,owner))
            db.execute("INSERT INTO methods VALUES(?,?,?,?,?,?,?)",(
                i,i,name,name+"()",0 if name=="swapSlices" else 4,
                "c"*64,"d"*64,
            ))
        old={k:v for k,v in self.methods().items()
             if k not in {x[0] for x in adjacent.EXTRA_METHODS}}
        with mock.patch.object(cell,"source_methods",return_value=old),\
             mock.patch.object(previous,"source_methods",return_value=old):
            methods=adjacent.source_methods(db)
            self.assertEqual(methods,self.methods())
            self.assertFalse(any(v["reviewed"] for v in methods.values()))
            db.execute("UPDATE methods SET normalized_sha256='invalid' WHERE id=1")
            with self.assertRaises(adjacent.AdjacentError):
                adjacent.source_methods(db)
        db.close()

    def test_isolated_new_mode_and_legacy_dispatch_are_present(self):
        java=cell.JAVA_SOURCE.read_text()
        self.assertIn("--stock-noisechunk-cell-16",java)
        self.assertIn("--stock-noisechunk-complete-cell-512",java)
        self.assertIn(adjacent.MODE,java)
        self.assertIn("swap.invoke(chunk)",java)
        self.assertIn("run(complete,false)",java)


if __name__=="__main__":
    unittest.main()
