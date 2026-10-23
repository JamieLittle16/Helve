"""Nineteenth original 26.2 source-owned ADD children; immutable rawbits."""
from __future__ import annotations

import contextlib
import io
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import worldgen_26_2_stock_finaldensity_nineteenth_layer_fixture as genuine  # noqa: E402


class NineteenthOriginalAp2Fixture(unittest.TestCase):
    def test_real_two_new_child_words_and_old_parent(self):
        rows = genuine.load()
        self.assertEqual(len(rows), 128)
        self.assertEqual(rows[0], ("3fdf12863e491a55", "bfb579b4d551ef7b"))
        self.assertEqual(rows[-1], ("3fd862dfadf4792f", "bfb1893612958e9a"))
        self.assertEqual(genuine.FIXTURE_BYTES, 4352)
        self.assertEqual(genuine.SHA256,
                         "77b5729bf8895a5b71b256b662643e87b2afa8fe0cc06caf7848787433fb48c4")
        self.assertEqual(genuine.REPORT_BYTES, 43278)
        self.assertEqual(genuine.REPORT_SHA256,
                         "a79b4d191a42f3f264d5e44757aa75c56cdf5077258d36c967207b058695e1f1")
        self.assertEqual(genuine.main([]), 0)

    def test_mutations_fail_closed_with_and_without_sha(self):
        raw = genuine.FIXTURE.read_bytes()
        self.assertEqual(len(raw), genuine.FIXTURE_BYTES)
        mutants = [
            raw[:-1],
            raw.replace(b"\t", b" ", 1),
            raw.replace(b"3fdf12863e491a55", b"3fdf12863e491a56", 1),
            raw.replace(b"bfb579b4d551ef7b", b"7ff0000000000000", 1),
            b"".join(reversed(raw.splitlines(keepends=True))),
        ]
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "malformed.tsv"
            for i, mutant in enumerate(mutants):
                path.write_bytes(mutant)
                with self.subTest(case=i), self.assertRaises(genuine.NineteenthFixtureError):
                    genuine.load(path)
            path.write_bytes(raw.replace(b"3fdf12863e491a55", b"3fdf12863e491a56", 1))
            with self.assertRaises(genuine.NineteenthFixtureError):
                genuine.load(path, require_sha=False)
            with self.assertRaises(genuine.NineteenthFixtureError):
                genuine.add_bits("7ff0000000000000", "bfb579b4d551ef7b")

    def test_original_source_shape_candidate_and_private_report_sha(self):
        self.assertEqual(genuine.SHAPE["ap2_op"], "ADD")
        self.assertEqual(genuine.SHAPE["ap2_left_class"], genuine.owner.CLASS + "Ap2")
        self.assertEqual(genuine.SHAPE["ap2_right_class"], genuine.owner.CLASS + "MulOrAdd")
        self.assertEqual(genuine.TELEMETRY["arithmetic_candidate_mismatches"], 0)
        self.assertEqual(genuine.TELEMETRY["observed_right_strictly_less"], 128)
        self.assertEqual(genuine.TELEMETRY["observed_left_strictly_less"], 0)
        self.assertFalse(genuine.TELEMETRY["source_law_admitted"])
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "fake-private.json"
            path.write_text('{"production_worldgen_enabled":true}', encoding="ascii")
            with self.assertRaisesRegex(genuine.NineteenthFixtureError, "bytes/SHA"):
                genuine.validate_original(path)
            err = io.StringIO()
            with contextlib.redirect_stderr(err):
                self.assertEqual(genuine.main(["--capture", str(path)]), 2)
            self.assertIn("NINETEENTH FIXTURE OPEN", err.getvalue())


if __name__ == "__main__":
    unittest.main()
