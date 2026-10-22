"""Exact source-owned eighth 26.2 Ap2 signed-zero and prior-parent fixture checks."""
from __future__ import annotations

import contextlib
import io
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import worldgen_26_2_stock_finaldensity_eighth_layer_fixture as eighth  # noqa: E402


class ActualEighthOriginalFixtureTests(unittest.TestCase):
    def test_128_new_eighth_operands_and_four_positive_zero_source_witnesses(self):
        rows=eighth.load()
        self.assertEqual(len(rows),128)
        self.assertEqual(rows[0],("3ff0000000000000","3fd86cd350602ed8"))
        self.assertEqual(rows[-1],("3ff0000000000000","3fd94719e77631df"))
        self.assertEqual([i for i,(left,_) in enumerate(rows) if left==eighth.ZERO],
                         [8,40,72,104])
        self.assertEqual(eighth.main([]),0)

    def test_original_new_word_mutations_cannot_be_admitted(self):
        raw=eighth.FIXTURE.read_bytes()
        self.assertEqual(len(raw),4352)
        lines=raw.splitlines(keepends=True)
        changed=[
            raw[:-1],
            raw.replace(b"\t",b" ",1),
            raw.replace(b"3fd86cd350602ed8",b"3fd86cd350602ed9",1),
            raw.replace(b"3ff0000000000000",b"0000000000000000",1),
            b"".join(reversed(lines)),
        ]
        zero_changed=lines.copy()
        zero_changed[8]=zero_changed[8].replace(
            b"0000000000000000",b"8000000000000000",1)
        changed.append(b"".join(zero_changed))
        with tempfile.TemporaryDirectory() as td:
            path=Path(td)/"changed.tsv"
            for i,blob in enumerate(changed):
                path.write_bytes(blob)
                with self.subTest(i=i),self.assertRaises(eighth.EighthFixtureError):
                    eighth.load(path)
            path.write_bytes(changed[2])
            with self.assertRaisesRegex(eighth.EighthFixtureError,"Ap2"):
                eighth.load(path,require_sha=False)
            path.write_bytes(changed[5])
            with self.assertRaisesRegex(eighth.EighthFixtureError,"Ap2|gradient"):
                eighth.load(path,require_sha=False)

    def test_source_owner_sha_and_false_admission(self):
        self.assertEqual(eighth.REPORT_BYTES,67230)
        self.assertEqual(eighth.EXPECTED_SHAPE["deep_ap2_op"],"MUL")
        self.assertEqual(eighth.EXPECTED_SHAPE["deep_ap2_left_class"],
                         eighth.CLASS+"YClampedGradient")
        self.assertEqual(eighth.EXPECTED_SHAPE["deep_ap2_right_class"],
                         eighth.CLASS+"MulOrAdd")
        with tempfile.TemporaryDirectory() as td:
            path=Path(td)/"fake-eighth-owner.json"
            path.write_text('{"production_worldgen_enabled":true}',encoding="ascii")
            with self.assertRaisesRegex(eighth.EighthFixtureError,"source-owned report"):
                eighth.validate_original(path)
            err=io.StringIO()
            with contextlib.redirect_stderr(err):
                code=eighth.main(["--capture",str(path)])
            self.assertEqual(code,2)
            self.assertIn("UNQUALIFIED",err.getvalue())


if __name__=="__main__":
    unittest.main()
