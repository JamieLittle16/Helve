"""Source-free callsite inventory must not silently promote review status."""
from __future__ import annotations

import sqlite3
import sys
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import worldgen_26_2_noisechunk_lifecycle_review_packet as review  # noqa: E402
import worldgen_26_2_stock_noisechunk_adjacent_capture as adjacent  # noqa: E402


class NoiseChunkLifecyclePacketTests(unittest.TestCase):
    def test_extracts_bounded_syntactic_call_order_not_canonical_proof(self):
        db=sqlite3.connect(":memory:")
        db.row_factory=sqlite3.Row
        db.executescript("""
          CREATE TABLE types(id INTEGER PRIMARY KEY,qualified_name TEXT);
          CREATE TABLE methods(id INTEGER PRIMARY KEY,type_id INTEGER,
              name TEXT,signature TEXT,param_count INTEGER,
              start_line INTEGER,end_line INTEGER);
          CREATE TABLE method_calls(id INTEGER PRIMARY KEY,
              caller_method_id INTEGER,callee_name TEXT,
              arg_count INTEGER,line INTEGER,resolution TEXT);
        """)
        fake={}
        for idx,(label,owner,name,arity) in enumerate(
                (*((a,b,c,d) for a,b,c,d in adjacent.cell.METHODS),
                 *((a,b,c,0) for a,b,c in adjacent.EXTRA_METHODS)),1):
            sig=f"{name}({arity})"
            fake[label]={
                "owner":owner,"signature":sig,"body_sha256":"a"*64,
                "normalized_sha256":"b"*64,"reviewed":False,
            }
            db.execute("INSERT INTO types VALUES(?,?)",(idx,owner))
            db.execute("INSERT INTO methods VALUES(?,?,?,?,?,?,?)",(
                idx,idx,name,sig,arity,100,200,
            ))
        for i,(name,line) in enumerate(
            [("advanceCellX",105),("otherCall",109),("swapSlices",110)],1
        ):
            db.execute("INSERT INTO method_calls VALUES(?,?,?,?,?,?)",(
                i,1,name,1,line,"syntactic",
            ))
        with mock.patch.object(adjacent,"source_methods",return_value=fake):
            packet=review.extract(db)
            self.assertEqual(len(packet["method_inventory"]),12)
            self.assertFalse(packet["canonical_control_flow_source_reviewed"])
            self.assertFalse(packet["source_text_included"])
            self.assertFalse(packet["production_worldgen_enabled"])
            first=next(x for x in packet["method_inventory"]
                       if x["signature"]==list(fake.values())[0]["signature"])
            self.assertEqual(
                [x["name"] for x in first["selected_syntactic_calls"]],
                ["advanceCellX","swapSlices"],
            )
            db.execute("UPDATE method_calls SET line=99 WHERE id=1")
            with self.assertRaises(review.ReviewPacketError):
                review.extract(db)
        db.close()


if __name__=="__main__":
    unittest.main()
