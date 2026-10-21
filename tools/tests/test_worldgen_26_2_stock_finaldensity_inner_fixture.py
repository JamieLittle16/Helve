"""Fail-closed 128 real stock 26.2 inner Marker/SQUEEZE/RangeChoice bits."""
from __future__ import annotations

import contextlib
import io
import tempfile
import unittest
from pathlib import Path
import sys

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import worldgen_26_2_stock_finaldensity_inner_fixture as fixture  # noqa: E402


class StockInnerFixtureTests(unittest.TestCase):
    def test_authentic_source_free_inner_fixture_and_existing_root_anchor(self):
        rows=fixture.load()
        self.assertEqual(len(rows),128)
        self.assertEqual(rows[0],(
            "3fb3333333333333","3fb3333333333333","3fa330e560418937",
            "bff0000000000000","4050000000000000","0000000000000000",
            "4050000000000000",
        ))
        self.assertEqual(rows[-1],rows[0])
        self.assertEqual(fixture.main([]),0)

    def test_input_output_swaps_and_bit_mutations_fail_closed(self):
        original=fixture.FIXTURE.read_bytes()
        changes=[
            original[:-1],
            original.replace(b"\t",b" ",1),
            original.replace(b"3fb3333333333333",b"3fb3333333333334",1),
            original.replace(b"3fa330e560418937",b"3fa330e560418936",1),
            original.replace(b"4050000000000000",b"4050000000000001",1),
            original.replace(b"bff0000000000000",b"3ff0000000000000",1),
            b"\n".join(original.splitlines()[::-1])+b"\n",
        ]
        with tempfile.TemporaryDirectory() as td:
            path=Path(td)/"altered.tsv"
            for i,data in enumerate(changes):
                path.write_bytes(data)
                with self.subTest(case=i),self.assertRaises(fixture.InnerFixtureError):
                    fixture.load(path)

    def test_unselected_branch_changes_must_fail_byte_pin_even_when_output_unchanged(self):
        raw=fixture.FIXTURE.read_bytes()
        # The row-zero selector chooses the in-range branch; changing its
        # out-of-range operand does not change the calculated root. The
        # source-free bit identity pin must still reject this mutation.
        altered=raw.replace(
            b"\t0000000000000000\t4050000000000000\n",
            b"\t3ff0000000000000\t4050000000000000\n",1,
        )
        self.assertNotEqual(raw,altered)
        with tempfile.TemporaryDirectory() as td:
            path=Path(td)/"altered.tsv"
            path.write_bytes(altered)
            with self.assertRaises(fixture.InnerFixtureError):
                fixture.load(path)
            self.assertEqual(len(fixture.load(path,require_sha=False)),128)

    def test_no_untrusted_forged_private_json(self):
        with tempfile.TemporaryDirectory() as td:
            file=Path(td)/"unqualified.json"
            file.write_text('{"source_text_included":true}')
            with self.assertRaisesRegex(fixture.InnerFixtureError,"identity"):
                fixture.validate_original(file)
            stderr=io.StringIO()
            with contextlib.redirect_stderr(stderr):
                rc=fixture.main(["--capture",str(file)])
            self.assertEqual(rc,2)
            self.assertIn("UNQUALIFIED",stderr.getvalue())


if __name__=="__main__":
    unittest.main()
