"""Immutable source-free sixth-layer original 26.2 JVM parity fixture tests."""
from __future__ import annotations

import contextlib
import io
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import worldgen_26_2_stock_finaldensity_sixth_layer_fixture as sixth  # noqa: E402


class SixthOriginalFixtureTests(unittest.TestCase):
    def test_sixth_true_original_128_rows_and_fifth_rawbit_parent_parity(self):
        rows=sixth.load()
        self.assertEqual(len(rows),128)
        self.assertEqual(rows[0],(
            "3fd36cd350602ed8","bfcbddb91f869220",
            "0000000000000000","0000000000000000",
        ))
        self.assertEqual(rows[-1],(
            "3fd44719e77631df","3fd30a7bbf318056",
            "0000000000000000","0000000000000000",
        ))
        self.assertEqual(sixth.main([]),0)

    def test_mutation_reordering_and_old_result_bit_differences_are_rejected(self):
        raw=sixth.FIXTURE.read_bytes()
        self.assertEqual(len(raw),8704)
        changed=[
            raw[:-1],
            raw.replace(b"\t",b" ",1),
            raw.replace(b"3fd36cd350602ed8",b"3fd36cd350602ed9",1),
            raw.replace(b"bfcbddb91f869220",b"bfcbddb91f869221",1),
            raw.replace(b"0000000000000000",b"3ff0000000000000",1),
            raw.replace(b"3fd36cd350602ed8",b"7ff0000000000000",1),
            b"\n".join(reversed(raw.splitlines()))+b"\n",
        ]
        with tempfile.TemporaryDirectory() as td:
            path=Path(td)/"tampered.tsv"
            for i,payload in enumerate(changed):
                path.write_bytes(payload)
                with self.subTest(i=i),self.assertRaises(sixth.SixthLayerFixtureError):
                    sixth.load(path)
            path.write_bytes(changed[2])
            with self.assertRaisesRegex(sixth.SixthLayerFixtureError,"ADD"):
                sixth.load(path,require_sha=False)

    def test_original_owner_identity_source_exclusion_and_all_admissions(self):
        self.assertEqual(sixth.REPORT_BYTES,93302)
        self.assertEqual(sixth.EXPECTED_SHAPE["left_marker_kind"],"Interpolated")
        self.assertEqual(sixth.EXPECTED_SHAPE["right_marker_kind"],"Interpolated")
        self.assertEqual(
            sixth.EXPECTED_SHAPE["outside_mul_child_class"],sixth.CLASS+"Noise"
        )
        with tempfile.TemporaryDirectory() as td:
            path=Path(td)/"false-owner.json"
            path.write_text('{"production_worldgen_enabled": true}',encoding="ascii")
            with self.assertRaisesRegex(sixth.SixthLayerFixtureError,"identity"):
                sixth.validate_original(path)
            stderr=io.StringIO()
            with contextlib.redirect_stderr(stderr):
                code=sixth.main(["--capture",str(path)])
            self.assertEqual(code,2)
            self.assertIn("UNQUALIFIED",stderr.getvalue())


if __name__=="__main__":
    unittest.main()
