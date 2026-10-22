"""Ninth source-owned one-new-word original Java fixture and adversarial guards."""
from __future__ import annotations

import contextlib
import io
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import worldgen_26_2_stock_finaldensity_ninth_layer_fixture as ninth  # noqa: E402


class GenuineNinthJVMFixtureTests(unittest.TestCase):
    def test_ninth_new_128_words_and_independent_eighth_parents(self):
        rows=ninth.load()
        self.assertEqual(len(rows),128)
        self.assertEqual(rows[0],"3fd36cd350602ed8")
        self.assertEqual(rows[-1],"3fd44719e77631df")
        self.assertEqual(ninth.gradient(255),"3fb0000000000000")
        self.assertEqual(ninth.gradient(320),"0000000000000000")
        self.assertEqual(ninth.main([]),0)

    def test_corrupt_raw_inputs_are_rejected(self):
        raw=ninth.FIXTURE.read_bytes()
        self.assertEqual(len(raw),2176)
        changed=[
            raw[:-1],
            raw.replace(b"\n",b"\r",1),
            raw.replace(b"3fd36cd350602ed8",b"3fd36cd350602ed9",1),
            raw.replace(b"3fd36cd350602ed8",b"7ff0000000000000",1),
            b"".join(reversed(raw.splitlines(keepends=True))),
        ]
        with tempfile.TemporaryDirectory() as td:
            path=Path(td)/"mutated.tsv"
            for i,data in enumerate(changed):
                with self.subTest(case=i),self.assertRaises(ninth.NinthFixtureError):
                    path.write_bytes(data)
                    ninth.load(path)
            path.write_bytes(changed[2])
            with self.assertRaisesRegex(ninth.NinthFixtureError,"ADD child"):
                ninth.load(path,require_sha=False)

    def test_untrusted_private_report_not_promoted(self):
        self.assertEqual(ninth.REPORT_BYTES,42445)
        self.assertEqual(ninth.SHAPE["left_from_y"],240)
        self.assertEqual(ninth.SHAPE["right_op"],"ADD")
        with tempfile.TemporaryDirectory() as td:
            path=Path(td)/"fabricated.json"
            path.write_text('{"production_worldgen_enabled":true}',encoding="ascii")
            with self.assertRaisesRegex(ninth.NinthFixtureError,"report bytes/SHA"):
                ninth.validate_original(path)
            err=io.StringIO()
            with contextlib.redirect_stderr(err):
                rc=ninth.main(["--capture",str(path)])
            self.assertEqual(rc,2)
            self.assertIn("NINTH FIXTURE OPEN",err.getvalue())


if __name__=="__main__":
    unittest.main()
