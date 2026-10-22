"""Exact original JVM tenth selector and independent Ap2 child SHA tests."""
from __future__ import annotations

import contextlib
import io
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import worldgen_26_2_stock_finaldensity_tenth_layer_fixture as tenth  # noqa: E402


class TenthActualSourceFixtureTests(unittest.TestCase):
    def test_all_real_new_words_and_selected_original_ninth_parents(self):
        rows=tenth.load()
        self.assertEqual(len(rows),128)
        self.assertEqual(
            rows[0],
            ("402ec6c8407d1d3d","400084be7e4c37c8","3fd36cd350602ed8"))
        self.assertEqual(
            rows[-1],
            ("402b486e660f3a02","3ff958e06153be57","3fd44719e77631df"))
        self.assertEqual(tenth.main([]),0)

    def test_new_rawbit_mutations_fail_closed_and_no_alias_shortcuts(self):
        raw=tenth.FIXTURE.read_bytes()
        self.assertEqual(len(raw),6528)
        changes=[
            raw[:-1],
            raw.replace(b"\t",b" ",1),
            raw.replace(b"402ec6c8407d1d3d",b"402ec6c8407d1d3e",1),
            raw.replace(b"402ec6c8407d1d3d",b"7ff0000000000000",1),
            b"".join(reversed(raw.splitlines(keepends=True))),
        ]
        with tempfile.TemporaryDirectory() as td:
            path=Path(td)/"changed.tsv"
            for i,changed in enumerate(changes):
                with self.subTest(i=i),self.assertRaises(tenth.TenthFixtureError):
                    path.write_bytes(changed)
                    tenth.load(path)
            path.write_bytes(changes[2])
            # Either the selected parent or the branch coverage must disagree.
            with self.assertRaises(tenth.TenthFixtureError):
                tenth.load(path,require_sha=False)

    def test_fabricated_original_report_is_not_source_admission(self):
        self.assertEqual(tenth.REPORT_BYTES,45434)
        self.assertEqual(tenth.SHAPE["selector_class"],tenth.CLASS+"Marker")
        self.assertEqual(tenth.SHAPE["when_in_class"],tenth.CLASS+"Ap2")
        self.assertEqual(tenth.SHAPE["when_out_class"],tenth.CLASS+"Ap2")
        with tempfile.TemporaryDirectory() as td:
            path=Path(td)/"wrong-owner.json"
            path.write_text('{"production_worldgen_enabled":true}',encoding="ascii")
            with self.assertRaisesRegex(tenth.TenthFixtureError,"owner bytes/SHA"):
                tenth.validate_original(path)
            err=io.StringIO()
            with contextlib.redirect_stderr(err):
                rc=tenth.main(["--capture",str(path)])
            self.assertEqual(rc,2)
            self.assertIn("TENTH FIXTURE OPEN",err.getvalue())


if __name__=="__main__":
    unittest.main()
