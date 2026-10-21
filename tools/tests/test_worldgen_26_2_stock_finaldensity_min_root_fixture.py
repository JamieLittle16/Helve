"""Frozen original Java 26.2 finalDensity Ap2 MIN root operand receipt."""
from __future__ import annotations

import contextlib
import io
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import worldgen_26_2_stock_finaldensity_min_root_fixture as rootmin  # noqa: E402


class StockMinRootFixtureTests(unittest.TestCase):
    def test_all_original_128_min_children_match_frozen_root_bits(self):
        triples=rootmin.read_words()
        self.assertEqual(len(triples),128)
        self.assertEqual(rootmin.HOLDER_WINS,(21,66,67,87))
        self.assertEqual(triples[0],(
            "3fa330e560418937","4050000000000000","3fa330e560418937"
        ))
        self.assertEqual(triples[-1],triples[0])
        self.assertEqual(triples[21],(
            "3f9cf82e09003609","3f91a72ed469fbec","3f91a72ed469fbec"
        ))
        self.assertEqual(rootmin.main([]),0)

    def test_bit_mutations_reordering_and_format_are_rejected(self):
        raw=rootmin.FIXTURE.read_bytes()
        with tempfile.TemporaryDirectory() as folder:
            dest=Path(folder)/"mutated.tsv"
            for i,changed in enumerate((
                raw[:-1],
                raw.replace(b"\t",b" ",1),
                raw.replace(b"3fa330e560418937",b"3fa330e560418936",1),
                b"\n".join(raw.splitlines()[::-1])+b"\n",
                raw.replace(b"4050000000000000",b"7ff8000000000000",1),
                raw.replace(b"3fa330e560418937",b"8000000000000000",1),
                raw.replace(b"\t4050000000000000\t",b"\t3fa330e560418937\t",1),
            )):
                dest.write_bytes(changed)
                with self.subTest(case=i),self.assertRaises(rootmin.MinRootFixtureError):
                    rootmin.read_words(dest)
                if len(changed)==len(raw) and i!=6:
                    with self.subTest(case=i),self.assertRaises(rootmin.MinRootFixtureError):
                        rootmin.read_words(dest,enforce_sha=False)
                elif i==6:
                    # A non-winning Holder value may change without changing
                    # MIN output. Exact byte SHA is therefore indispensable.
                    self.assertEqual(len(rootmin.read_words(dest,enforce_sha=False)),128)

    def test_unverified_original_capture_does_not_pass(self):
        with tempfile.TemporaryDirectory() as folder:
            bad=Path(folder)/"stock.json"
            bad.write_text('{"schema":1,"production_worldgen_enabled":true}')
            with self.assertRaisesRegex(rootmin.MinRootFixtureError,"SHA"):
                rootmin.validate_original(bad)
            stderr=io.StringIO()
            with contextlib.redirect_stderr(stderr):
                rc=rootmin.main(["--capture",str(bad)])
            self.assertEqual(rc,2)
            self.assertIn("UNQUALIFIED",stderr.getvalue())


if __name__=="__main__":
    unittest.main()
