"""Genuine original 26.2 17th right-Ap2 ADD immutable fixture audits."""
from __future__ import annotations

import contextlib
import io
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import worldgen_26_2_stock_finaldensity_seventeenth_layer_fixture as genuine  # noqa: E402


class GenuineSeventeenthAddFixture(unittest.TestCase):
    def test_original_exact_source_owned_add_children_and_old_parent(self):
        rows = genuine.load()
        self.assertEqual(len(rows), 128)
        self.assertEqual(rows[0], ("3f873c91bd775944", "3fd9b41908f49e76"))
        self.assertEqual(rows[-1], ("3f71a1ef89c715c1", "3fd40092294f1588"))
        self.assertEqual(genuine.REPORT_BYTES, 43284)
        self.assertEqual(genuine.REPORT_SHA256,
                         "1c9fd95824aef71b68aaeb9c9528cb1adca174d6a258bc002989c3eb2fcac3c1")
        self.assertEqual(genuine.SHA256,
                         "ef9a7e19fc793ce4d33592756faa73a80d86ad59941ae171820b3ed8eb4263a5")
        self.assertEqual(genuine.main([]), 0)

    def test_reject_sha_format_nonfinite_previous_parent_and_order(self):
        old = genuine.FIXTURE.read_bytes()
        self.assertEqual(len(old), 4352)
        mutants = [
            old[:-1],
            old.replace(b"\t", b" ", 1),
            old.replace(b"3f873c91bd775944", b"3f873c91bd775945", 1),
            old.replace(b"3fd9b41908f49e76", b"7ff0000000000000", 1),
            b"".join(reversed(old.splitlines(keepends=True))),
        ]
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "forged.tsv"
            for i, candidate in enumerate(mutants):
                path.write_bytes(candidate)
                with self.subTest(index=i), self.assertRaises(genuine.SeventeenthFixtureError):
                    genuine.load(path)
            path.write_bytes(old.replace(b"3f873c91bd775944", b"3ff0000000000000", 1))
            with self.assertRaises(genuine.SeventeenthFixtureError):
                genuine.load(path, require_sha=False)
            with self.assertRaises(genuine.SeventeenthFixtureError):
                genuine.add_bits("7ff0000000000000", "3ff0000000000000")
            with self.assertRaises(genuine.SeventeenthFixtureError):
                genuine.add_bits("7fefffffffffffff", "7fefffffffffffff")

    def test_original_provenance_true_classes_and_false_gates(self):
        self.assertEqual(genuine.SHAPE["ap2_op"], "ADD")
        self.assertEqual(genuine.SHAPE["ap2_left_class"], genuine.owner.CLASS + "HolderHolder")
        self.assertEqual(genuine.SHAPE["ap2_right_class"], genuine.owner.CLASS + "Clamp")
        self.assertEqual(genuine.TELEMETRY["arithmetic_candidate_mismatches"], 0)
        self.assertEqual(genuine.TELEMETRY["observed_left_strictly_less"], 124)
        self.assertEqual(genuine.TELEMETRY["observed_right_strictly_less"], 4)
        self.assertFalse(genuine.TELEMETRY["source_law_admitted"])
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "fake-private.json"
            path.write_text('{"production_worldgen_enabled":true}', encoding="ascii")
            with self.assertRaisesRegex(genuine.SeventeenthFixtureError, "bytes/SHA"):
                genuine.validate_original(path)
            errors = io.StringIO()
            with contextlib.redirect_stderr(errors):
                self.assertEqual(genuine.main(["--capture", str(path)]), 2)
            self.assertIn("SEVENTEENTH FIXTURE OPEN", errors.getvalue())


if __name__ == "__main__":
    unittest.main()
