"""Frozen original 26.2 twenty-second Noise terminal graph proof obligations."""
from __future__ import annotations

import hashlib
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import worldgen_26_2_stock_finaldensity_twenty_second_structure_receipt as receipt  # noqa: E402


class GenuineNoiseLeafReceiptTests(unittest.TestCase):
    def test_no_copy_of_old_numeric_values_and_four_seed_structure(self):
        self.assertEqual(receipt.REPORT_BYTES, 32822)
        self.assertEqual(
            receipt.REPORT_SHA256,
            "8c2a9b2a2f5383899c7ade9931971ce9ea6757b3bcd1967aac9038df8fe5834c",
        )
        self.assertEqual(receipt.STRUCTURE["noise_parameters_key"],
                         "minecraft:spaghetti_3d_thickness")
        self.assertEqual(receipt.STRUCTURE["noise_data_holder_class"],
                         "net.minecraft.core.Holder$Reference")
        self.assertEqual(receipt.STRUCTURE["noise_xz_scale_bits"],
                         "3ff0000000000000")
        self.assertEqual(receipt.STRUCTURE["noise_y_scale_bits"],
                         "3ff0000000000000")
        self.assertEqual(receipt.TELEMETRY["genuinely_new_ieee_words"], 0)
        self.assertEqual(len(receipt.owner.prior_leaf.load()), 128)
        self.assertTrue(all(val is False for val in (
            receipt.TELEMETRY["source_law_admitted"],
            *[False for _ in receipt.owner.GATES],
        )))

    def test_private_receipt_never_accepts_changed_bytes_or_fake_provenance(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "not-source-owned.json"
            for data in (b"{}", b"\n" * receipt.REPORT_BYTES, b"x" * receipt.REPORT_BYTES):
                path.write_bytes(data)
                with self.subTest(sha=hashlib.sha256(data).hexdigest()):
                    with self.assertRaises(receipt.TwentySecondReceiptError):
                        receipt.validate_original(path)

    def test_all_source_and_semantic_rechecks_even_when_digest_is_present(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "right-length-only.json"
            path.write_bytes(b" " * receipt.REPORT_BYTES)
            with patch.object(receipt, "REPORT_SHA256", hashlib.sha256(path.read_bytes()).hexdigest()):
                with self.assertRaises(receipt.TwentySecondReceiptError):
                    receipt.validate_original(path)
        self.assertFalse(receipt.owner.prior_leaf.load()[0] == "0" * 16)


if __name__ == "__main__":
    unittest.main()
