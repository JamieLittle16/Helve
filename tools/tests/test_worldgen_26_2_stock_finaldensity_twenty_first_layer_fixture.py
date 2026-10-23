"""Fail-closed source-authentic twenty-first original Noise-only receipt tests."""
from __future__ import annotations

import hashlib
import struct
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import worldgen_26_2_stock_final_density_twenty_first_layer as owner  # noqa: E402
import worldgen_26_2_stock_finaldensity_twenty_first_layer_fixture as receipt  # noqa: E402
import worldgen_26_2_stock_finaldensity_twentieth_layer_fixture as prior  # noqa: E402


class TwentyFirstOriginalNoiseFixtureTests(unittest.TestCase):
    def test_noise_one_new_word_128_exact_mul_to_independent_old_parent(self):
        noise = receipt.load()
        older = prior.load()
        self.assertEqual(len(noise), 128)
        self.assertEqual(len(older), 128)
        self.assertEqual(receipt.FIXTURE_BYTES, 2176)
        self.assertEqual(receipt.REPORT_BYTES, 37461)
        self.assertEqual(receipt.SCALAR_BITS, "bf878d4fdf3b6458")
        self.assertEqual(set(k["muloradd_op"] for k in [receipt.SHAPE]), {"MUL"})
        scalar = receipt.from_ieee(receipt.SCALAR_BITS)
        for i, (raw, frozen) in enumerate(zip(noise, older, strict=True)):
            with self.subTest(i=i):
                self.assertEqual(receipt.ieee(receipt.from_ieee(raw) * scalar), frozen)

    def test_fixture_bytes_sha_and_parent_tampering_all_fail_closed(self):
        frozen = receipt.FIXTURE.read_bytes()
        self.assertEqual(hashlib.sha256(frozen).hexdigest(), receipt.SHA256)
        for tampered in (
            frozen[:-1], frozen + b"\n", b"!" + frozen[1:],
            frozen.replace(b"\n", b"\r\n", 1),
            frozen[:2] + b"0" + frozen[3:],
        ):
            with tempfile.TemporaryDirectory() as td:
                dest = Path(td) / "wrong.tsv"
                dest.write_bytes(tampered)
                with self.assertRaises(receipt.TwentyFirstFixtureError):
                    receipt.load(dest)
        with patch.object(receipt.previous, "load", return_value=("0" * 16,) * 128):
            with self.assertRaises(receipt.TwentyFirstFixtureError):
                receipt.load()

    def test_original_report_sha_and_source_provenance_sealed(self):
        self.assertEqual(receipt.REPORT_SHA256,
                         "a14316f209553322029b2df7a37ddc757d5f52ae53005f404427111a00f58fec")
        self.assertEqual(receipt.SHA256,
                         "7519acc761730ba6aac2f1ac03d4b625d529127e258e23a8945dee7d25e193ed")
        with tempfile.TemporaryDirectory() as td:
            forged = Path(td) / "forged.json"
            forged.write_text("{}")
            with self.assertRaises(receipt.TwentyFirstFixtureError):
                receipt.validate_original(forged)
        self.assertEqual(receipt.TELEMETRY["muloradd_candidate_mismatches"], 0)
        self.assertFalse(receipt.TELEMETRY["source_law_admitted"])
        self.assertIn("production_worldgen_enabled", owner.GATES)
        self.assertFalse(receipt.SHAPE["muloradd_op"] == "ADD")


if __name__ == "__main__":
    unittest.main()
