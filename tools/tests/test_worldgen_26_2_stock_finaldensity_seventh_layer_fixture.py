"""Fail-closed exact seventh-layer original 26.2 stock Java fixture tests."""
from __future__ import annotations

import contextlib
import io
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import worldgen_26_2_stock_finaldensity_seventh_layer_fixture as seventh  # noqa: E402


class SeventhOriginalFixtureTests(unittest.TestCase):
    def test_real_original_seven_new_words_and_parent_parity(self):
        rows=seventh.load()
        self.assertEqual(len(rows),128)
        self.assertEqual(rows[0],(
            "3fd86cd350602ed8","c050000000000000",
            "3fb1706ac678551e","0000000000000000",
            "c050000000000000","3fc97cd23503f6f8",
            "0000000000000000",
        ))
        self.assertEqual(rows[-1],(
            "3fd94719e77631df","c050400000000000",
            "3fdb2b715a1f27c1","0000000000000000",
            "c050400000000000","3fbdbc43b6a8b768",
            "0000000000000000",
        ))
        self.assertEqual(seventh.main([]),0)

    def test_mutation_wrong_order_and_source_shape_rejected(self):
        raw=seventh.FIXTURE.read_bytes()
        self.assertEqual(len(raw),15232)
        changes=[
            raw[:-1],
            raw.replace(b"\t",b" ",1),
            raw.replace(b"3fd86cd350602ed8",b"3fd86cd350602ed9",1),
            raw.replace(b"c050000000000000",b"c04f800000000000",1),
            raw.replace(b"3fb1706ac678551e",b"3fb1706ac678551f",1),
            raw.replace(b"0000000000000000",b"3ff0000000000000",1),
            raw.replace(b"3fc97cd23503f6f8",b"3fc97cd23503f6f9",1),
            raw.replace(b"3fd86cd350602ed8",b"7ff0000000000000",1),
            b"\n".join(reversed(raw.splitlines()))+b"\n",
        ]
        with tempfile.TemporaryDirectory() as td:
            path=Path(td)/"altered.tsv"
            for i,payload in enumerate(changes):
                path.write_bytes(payload)
                with self.subTest(i=i),self.assertRaises(seventh.SeventhLayerFixtureError):
                    seventh.load(path)
            path.write_bytes(changes[2])
            with self.assertRaisesRegex(seventh.SeventhLayerFixtureError,"ADD"):
                seventh.load(path,require_sha=False)
            path.write_bytes(changes[3])
            with self.assertRaisesRegex(seventh.SeventhLayerFixtureError,"selector"):
                seventh.load(path,require_sha=False)
            path.write_bytes(changes[5])
            with self.assertRaisesRegex(seventh.SeventhLayerFixtureError,"Constant"):
                seventh.load(path,require_sha=False)

    def test_original_owner_SHA_and_source_exclusion(self):
        self.assertEqual(seventh.REPORT_BYTES,87635)
        self.assertEqual(seventh.EXPECTED_SHAPE["left_deep_op"],"ADD")
        self.assertEqual(seventh.EXPECTED_SHAPE["left_choice_in_class"],
                         seventh.CLASS+"Noise")
        self.assertEqual(seventh.EXPECTED_SHAPE["right_choice_in_class"],
                         seventh.CLASS+"Noise")
        with tempfile.TemporaryDirectory() as td:
            path=Path(td)/"wrong-owner.json"
            path.write_text('{"production_worldgen_enabled":true}',encoding="ascii")
            with self.assertRaisesRegex(seventh.SeventhLayerFixtureError,"identity|SHA"):
                seventh.validate_original(path)
            err=io.StringIO()
            with contextlib.redirect_stderr(err):
                status=seventh.main(["--capture",str(path)])
            self.assertEqual(status,2)
            self.assertIn("UNQUALIFIED",err.getvalue())


if __name__=="__main__":
    unittest.main()
