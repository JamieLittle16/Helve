"""Fail-closed original 26.2 fourth-layer immutable source-free receipt tests."""
from __future__ import annotations

import contextlib
import io
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import worldgen_26_2_stock_finaldensity_fourth_layer_fixture as fixture  # noqa: E402


class ActualFourthLayerFixtureTests(unittest.TestCase):
    def test_original_128_by_seven_and_immutable_prior_third_anchors(self):
        rows=fixture.load()
        self.assertEqual(len(rows),128)
        self.assertEqual(rows[0],(
            "0000000000000000","c050000000000000","c050000000000000",
            "bfb1ce838b39457f","0000000000000000",
            "0000000000000000","0000000000000000",
        ))
        self.assertEqual(rows[-1],(
            "0000000000000000","c050400000000000","c050400000000000",
            "bfb51aa5f984f33d","0000000000000000",
            "0000000000000000","0000000000000000",
        ))
        self.assertEqual(fixture.main([]),0)

    def test_mutations_never_silently_admit_original_evidence(self):
        raw=fixture.FIXTURE.read_bytes()
        self.assertEqual(len(raw),15232)
        mutations=[
            raw[:-1],
            raw.replace(b"\t",b" ",1),
            raw.replace(b"3fd01a874a693da1",b"3ff0000000000000",1),
            raw.replace(b"bfb1ce838b39457f",b"bfb1ce838b39457e",1),
            raw.replace(b"0000000000000000",b"7ff0000000000000",1),
            b"\n".join(reversed(raw.splitlines()))+b"\n",
        ]
        with tempfile.TemporaryDirectory() as td:
            path=Path(td)/"mutated.tsv"
            for i,data in enumerate(mutations):
                path.write_bytes(data)
                with self.subTest(i=i),self.assertRaises(fixture.FourthLayerFixtureError):
                    fixture.load(path)
            path.write_bytes(mutations[2])
            with self.assertRaisesRegex(fixture.FourthLayerFixtureError,"ADD"):
                fixture.load(path,require_sha=False)

    def test_untrusted_private_capture_cannot_replace_original_owner(self):
        with tempfile.TemporaryDirectory() as td:
            path=Path(td)/"untrusted.json"
            path.write_text('{"production_worldgen_enabled":true}',encoding="ascii")
            with self.assertRaisesRegex(fixture.FourthLayerFixtureError,"identity"):
                fixture.validate_original(path)
            err=io.StringIO()
            with contextlib.redirect_stderr(err):
                rc=fixture.main(["--capture",str(path)])
            self.assertEqual(rc,2)
            self.assertIn("UNQUALIFIED",err.getvalue())


if __name__=="__main__":
    unittest.main()
