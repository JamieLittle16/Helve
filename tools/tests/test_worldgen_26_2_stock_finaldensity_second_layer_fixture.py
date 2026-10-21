"""Source-free tests for actual original stock 26.2 finalDensity second layer."""
from __future__ import annotations

import contextlib
import io
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import worldgen_26_2_stock_finaldensity_second_layer_fixture as fixture  # noqa: E402


class StockSecondLayerFixtureTests(unittest.TestCase):
    def test_exact_new_128_rows_and_frozen_inner_bit_anchors(self):
        rows=fixture.load()
        self.assertEqual(len(rows),128)
        self.assertEqual(rows[0],(
            "3fbe000000000000","bff0000000000000",
            "0000000000000000","0000000000000000",
        ))
        self.assertEqual(rows[-1],rows[0])
        self.assertEqual(fixture.ARGUMENT_BITS,"3fe47ae147ae147b")
        self.assertEqual(fixture.main([]),0)

    def test_mutations_and_reorders_fail_closed(self):
        original=fixture.FIXTURE.read_bytes()
        self.assertEqual(len(original),8704)
        a=original.splitlines()
        self.assertEqual(len(a),128)
        variants=[
            original[:-1],
            original.replace(b"\t",b" ",1),
            original.replace(b"3fbe000000000000",b"3fbe000000000001",1),
            original.replace(b"bff0000000000000",b"bff0000000000001",1),
            original.replace(b"0000000000000000",b"0000000000000001",1),
            b"\n".join([a[1],a[0],*a[2:]])+b"\n",
            b"\n".join(reversed(a))+b"\n",
        ]
        with tempfile.TemporaryDirectory() as td:
            changed=Path(td)/"changed.tsv"
            for index,blob in enumerate(variants):
                changed.write_bytes(blob)
                with self.subTest(index=index),self.assertRaises(fixture.SecondLayerFixtureError):
                    fixture.load(changed)
        with tempfile.TemporaryDirectory() as td:
            changed=Path(td)/"untrusted.tsv"
            changed.write_bytes(variants[2])
            with self.assertRaisesRegex(fixture.SecondLayerFixtureError,"MulOrAdd"):
                fixture.load(changed,require_sha=False)

    def test_fake_owner_receipts_not_admitted(self):
        with tempfile.TemporaryDirectory() as td:
            path=Path(td)/"untrusted.json"
            path.write_text('{"source_text_included":true}',encoding="ascii")
            with self.assertRaisesRegex(fixture.SecondLayerFixtureError,"identity"):
                fixture.validate_original(path)
            err=io.StringIO()
            with contextlib.redirect_stderr(err):
                result=fixture.main(["--capture",str(path)])
            self.assertEqual(result,2)
            self.assertIn("UNQUALIFIED",err.getvalue())


if __name__=="__main__":
    unittest.main()
