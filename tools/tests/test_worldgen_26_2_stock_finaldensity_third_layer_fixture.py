"""Fail-closed third original-JVM receipt, not a rewritten older oracle."""
from __future__ import annotations

import contextlib
import io
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import worldgen_26_2_stock_finaldensity_third_layer_fixture as fixture  # noqa: E402


class StockThirdLayerFixtureTests(unittest.TestCase):
    def test_exact_six_new_fields_128_rows_and_second_layer_sha_anchors(self):
        rows=fixture.load()
        self.assertEqual(len(rows),128)
        self.assertEqual(rows[0],(
            "3fbe000000000000","c050000000000000","3fe795fda3baf6a4",
            "bff0000000000000","0000000000000000","0000000000000000",
        ))
        self.assertEqual(rows[-1],(
            "3fbe000000000000","c050400000000000","bfcf55c9830dd135",
            "bff0000000000000","0000000000000000","0000000000000000",
        ))
        self.assertEqual(fixture.main([]),0)

    def test_corrupt_branches_and_parameters_are_not_admitted(self):
        raw=fixture.FIXTURE.read_bytes()
        self.assertEqual(len(raw),13056)
        changes=[
            raw[:-1],
            raw.replace(b"\t",b" ",1),
            raw.replace(b"3fbe000000000000",b"3fbe000000000001",1),
            raw.replace(b"c050000000000000",b"4050000000000000",1),
            raw.replace(b"3fe795fda3baf6a4",b"3fe795fda3baf6a5",1),
            raw.replace(b"bff0000000000000",b"3ff0000000000000",1),
            raw.replace(b"0000000000000000",b"0000000000000001",1),
            b"\n".join(reversed(raw.splitlines()))+b"\n",
        ]
        with tempfile.TemporaryDirectory() as td:
            path=Path(td)/"changed.tsv"
            for i,blob in enumerate(changes):
                path.write_bytes(blob)
                with self.subTest(i=i),self.assertRaises(fixture.ThirdLayerFixtureError):
                    fixture.load(path)
            path.write_bytes(changes[2])
            with self.assertRaisesRegex(fixture.ThirdLayerFixtureError,"Marker"):
                fixture.load(path,require_sha=False)

    def test_untrusted_json_cannot_replace_original_owner_receipt(self):
        with tempfile.TemporaryDirectory() as td:
            path=Path(td)/"not-original.json"
            path.write_text('{"production_worldgen_enabled":true}',encoding="ascii")
            with self.assertRaisesRegex(fixture.ThirdLayerFixtureError,"identity"):
                fixture.validate_original(path)
            err=io.StringIO()
            with contextlib.redirect_stderr(err):
                rc=fixture.main(["--capture",str(path)])
            self.assertEqual(rc,2)
            self.assertIn("UNQUALIFIED",err.getvalue())


if __name__=="__main__":
    unittest.main()
