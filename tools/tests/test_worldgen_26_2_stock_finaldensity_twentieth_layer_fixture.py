"""Fail-closed original twentieth MulOrAdd source-only receipt tests."""
from __future__ import annotations

import copy
import hashlib
import json
import struct
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import worldgen_26_2_stock_finaldensity_twentieth_layer_fixture as sealed  # noqa: E402
import worldgen_26_2_stock_finaldensity_nineteenth_layer_fixture as prior  # noqa: E402
import worldgen_26_2_stock_final_density_twentieth_layer as source  # noqa: E402


class OriginalTwentiethFixtureTests(unittest.TestCase):
    def test_128_truly_new_ieee_words_old_original_parent_independent(self):
        actual = sealed.load()
        older = prior.load()
        self.assertEqual(len(actual), 128)
        self.assertEqual(len(older), 128)
        self.assertEqual(sealed.FIXTURE_BYTES, 2176)
        self.assertEqual(sealed.REPORT_BYTES, 37509)
        self.assertEqual(sealed.ARGUMENT_BITS, "bfb395810624dd2f")
        scalar = sealed.from_ieee(sealed.ARGUMENT_BITS)
        self.assertEqual(scalar, -0.0765)
        for i, (new, pair) in enumerate(zip(actual, older, strict=True)):
            with self.subTest(i=i):
                self.assertEqual(
                    sealed.ieee(sealed.from_ieee(new) + scalar),
                    pair[1],
                )

    def test_wrong_fixture_bytes_sha_and_independent_nineteenth_anchor_fail(self):
        original = sealed.FIXTURE.read_bytes()
        self.assertEqual(hashlib.sha256(original).hexdigest(), sealed.SHA256)
        for mutated in (
            original[:-1],
            b"!" + original[1:],
            original.replace(b"\n", b"\r\n", 1),
            original[:4] + b"0" + original[5:],
        ):
            with tempfile.TemporaryDirectory() as td:
                path = Path(td) / "changed.tsv"
                path.write_bytes(mutated)
                with self.assertRaises(sealed.TwentiethFixtureError):
                    sealed.load(path)
        with patch.object(sealed.previous, "load", return_value=(("0"*16, "0"*16),)*128):
            with self.assertRaises(sealed.TwentiethFixtureError):
                sealed.load()

    def test_old_stock_full_report_hash_is_immutable(self):
        self.assertEqual(sealed.REPORT_SHA256,
                         "859e7f78594bb2ddca090627ea6e04503b220f6b619fe3df46bab8b25394bbd8")
        self.assertEqual(sealed.REPORT_BYTES, 37509)
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "not-the-original.json"
            p.write_text("{}")
            with self.assertRaises(sealed.TwentiethFixtureError):
                sealed.validate_original(p)

    def test_original_report_validation_does_not_promote_source_gates(self):
        self.assertTrue(all(key for key in source.GATES))
        self.assertIn("twentieth_all_input_muloradd_law_admitted", source.GATES)
        self.assertIn("production_worldgen_enabled", source.GATES)
        self.assertFalse(source.candidate_telemetry([
            {"muloradd_argument_bits": sealed.ARGUMENT_BITS,
             "muloradd_op": "ADD"}
        ], [{
            "muloradd_inner_bits": "0x" + sealed.load()[0],
            "old_nineteenth_right_bits": "0x" + prior.load()[0][1],
        }])["source_law_admitted"])

    def test_original_capture_if_present_is_verified_by_full_sha_and_schema(self):
        # Original user JVM capture is private and must not be distributed in the repo.
        self.assertNotIn("source_text", sealed.FIXTURE.read_text())
        self.assertEqual(len(sealed.load()), 128)


if __name__ == "__main__":
    unittest.main()
