"""Real 18th Clamp source owned SHA, ONLY two true-new IEEE words."""
from __future__ import annotations

import contextlib
import io
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import worldgen_26_2_stock_finaldensity_eighteenth_layer_receipt as receipt  # noqa: E402


class EighteenthRealClampReceipt(unittest.TestCase):
    def test_full_original_sha_and_real_clipping_coverage(self):
        inner = receipt.load()
        self.assertEqual(len(inner), 128)
        self.assertEqual(inner[18], "3ff5c1c9c20d14a4")
        self.assertEqual(inner[28], "3ff219c5d9c551b1")
        self.assertEqual(inner[0], "3fd9b41908f49e76")
        self.assertEqual(inner[-1], "3fd40092294f1588")
        self.assertEqual(receipt.REPORT_BYTES, 36555)
        self.assertEqual(receipt.REPORT_SHA256,
                         "4e8279f53b06a6de9154f18df073b742ad091acfe6b156611bc916dbbf8781ae")
        self.assertEqual(receipt.SHA256,
                         "e1b4da2ef965a0e92ad2bb56931de16dce95318f3aadabd4e78be2721a5b2811")
        self.assertEqual(receipt.FIXTURE_BYTES, 40)
        self.assertEqual(receipt.TELEMETRY["observed_above_max"], 2)
        self.assertEqual(receipt.TELEMETRY["observed_within_inclusive_bounds"], 126)
        self.assertEqual(receipt.TELEMETRY["observed_below_min"], 0)
        self.assertEqual(receipt.TELEMETRY["clamp_candidate_mismatches"], 0)
        self.assertFalse(receipt.TELEMETRY["source_law_admitted"])
        self.assertEqual(receipt.main([]), 0)

    def test_fail_closed_override_mutations_even_without_sha(self):
        raw = receipt.FIXTURE.read_bytes()
        self.assertEqual(len(raw), 40)
        fake = [
            raw[:-1],
            raw.replace(b"\t", b" ", 1),
            raw.replace(b"18\t", b"28\t", 1),
            raw.replace(b"3ff5c1c9c20d14a4", b"3ff5c1c9c20d14a5", 1),
            raw.replace(b"3ff219c5d9c551b1", b"7ff0000000000000", 1),
            raw[::-1],
        ]
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "fake.txt"
            for i, item in enumerate(fake):
                path.write_bytes(item)
                with self.subTest(index=i), self.assertRaises(receipt.EighteenthReceiptError):
                    receipt.load(path)
            path.write_bytes(raw.replace(b"3ff219c5d9c551b1", b"3ff219c5d9c551b2", 1))
            with self.assertRaises(receipt.EighteenthReceiptError):
                receipt.load(path, require_sha=False)
            with self.assertRaises(receipt.EighteenthReceiptError):
                receipt.minmax("7ff0000000000000")

    def test_private_original_report_unforgeable_with_only_2_new_words(self):
        self.assertEqual(receipt.SHAPE["clamp_input_class"], receipt.owner.CLASS + "Ap2")
        self.assertEqual(receipt.SHAPE["clamp_min_bits"], "bff0000000000000")
        self.assertEqual(receipt.SHAPE["clamp_max_bits"], "3ff0000000000000")
        self.assertEqual(receipt.OVERRIDES, {18: "3ff5c1c9c20d14a4", 28: "3ff219c5d9c551b1"})
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "fake-original.json"
            path.write_text('{"production_worldgen_enabled":true}', encoding="ascii")
            with self.assertRaisesRegex(receipt.EighteenthReceiptError, "report SHA/bytes"):
                receipt.validate_original(path)
            errors = io.StringIO()
            with contextlib.redirect_stderr(errors):
                self.assertEqual(receipt.main(["--capture", str(path)]), 2)
            self.assertIn("EIGHTEENTH RECEIPT OPEN", errors.getvalue())


if __name__ == "__main__":
    unittest.main()
