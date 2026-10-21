"""Fail-closed original fifth-layer source-free SHA and old-result regression tests."""
from __future__ import annotations

import contextlib
import io
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import worldgen_26_2_stock_finaldensity_fifth_layer_fixture as fixture  # noqa: E402


class OriginalFifthLayerFixtureTests(unittest.TestCase):
    def test_exact_six_new_words_128_rows_and_frozen_fourth_anchors(self):
        rows=fixture.load()
        self.assertEqual(len(rows),128)
        self.assertEqual(rows[0],(
            "0000000000000000","3fc7d9a6a0c05db0","c050000000000000",
            "3f764afa7f9edb4d","0000000000000000","0000000000000000",
        ))
        self.assertEqual(rows[-1],(
            "0000000000000000","3fc98e33ceec63be","c050400000000000",
            "bf7e772c651c008a","0000000000000000","0000000000000000",
        ))
        self.assertEqual(fixture.main([]),0)

    def test_both_word_tampering_and_reordering_fail_closed(self):
        raw=fixture.FIXTURE.read_bytes()
        self.assertEqual(len(raw),13056)
        mutations=[
            raw[:-1],
            raw.replace(b"\t",b" ",1),
            raw.replace(b"0000000000000000",b"7ff0000000000000",1),
            raw.replace(b"3fd01a874a693da1",b"3fd01a874a693da2",1),
            raw.replace(b"3f764afa7f9edb4d",b"3f764afa7f9edb4e",1),
            b"\n".join(reversed(raw.splitlines()))+b"\n",
        ]
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/"mutated.tsv"
            for i,data in enumerate(mutations):
                p.write_bytes(data)
                with self.subTest(i=i),self.assertRaises(fixture.FifthLayerFixtureError):
                    fixture.load(p)
            p.write_bytes(mutations[3])
            with self.assertRaisesRegex(fixture.FifthLayerFixtureError,"MUL"):
                fixture.load(p,require_sha=False)

    def test_no_replacement_of_original_owner_report_by_fake_json(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/"untrusted.json"
            p.write_text('{"production_worldgen_enabled":true}',encoding="ascii")
            with self.assertRaisesRegex(fixture.FifthLayerFixtureError,"identity"):
                fixture.validate_original(p)
            err=io.StringIO()
            with contextlib.redirect_stderr(err):
                rc=fixture.main(["--capture",str(p)])
            self.assertEqual(rc,2)
            self.assertIn("UNQUALIFIED",err.getvalue())


if __name__=="__main__":
    unittest.main()
