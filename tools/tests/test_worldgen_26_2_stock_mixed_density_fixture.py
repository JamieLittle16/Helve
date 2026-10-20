"""Strict immutable independently acquired stock 26.2 mixed-density oracle."""
from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import worldgen_26_2_stock_mixed_density_fixture as target  # noqa: E402


class StockMixedFixtureTests(unittest.TestCase):
    def test_original_reference_is_complete_canonical_and_sha_pinned(self):
        values = target.read_bits()
        self.assertEqual(len(values), 1920)
        self.assertEqual(values[0], "bfda6cdb9e1f1c66")
        self.assertEqual(values[384], "8000000000000000")
        self.assertEqual(values[576], "0000000000000000")
        self.assertEqual(values[1919], "3fae82b27db6a527")
        self.assertEqual(len(target.METHODS["composition_factories"]), 2)
        self.assertEqual(len(target.METHODS["density_primitives"]), 4)
        self.assertEqual(len(target.METHODS["worldseed_noise"]), 6)
        self.assertEqual(len(target.DELEGATES), 10)

    def test_truncation_padding_mutation_bad_hex_and_changed_signed_zero_reject(self):
        pristine = target.FIXTURE.read_bytes()
        with tempfile.TemporaryDirectory() as root:
            candidate = Path(root) / "heldout.txt"
            for wrong in (
                pristine[:-1], pristine + b"\n",
                pristine[:-17], pristine[:16] + b"0" + pristine[17:],
                b"z" + pristine[1:],
                pristine.replace(b"8000000000000000\n", b"0000000000000000\n", 1),
                pristine.replace(b"0000000000000000\n", b"8000000000000000\n", 1),
            ):
                with self.subTest(length=len(wrong), prefix=wrong[:17]):
                    candidate.write_bytes(wrong)
                    with self.assertRaises(target.StockMixedFixtureError):
                        target.read_bits(candidate)

    def test_fake_source_free_json_cannot_impersonate_exact_original_receipt(self):
        with tempfile.TemporaryDirectory() as root:
            source = Path(root) / "fake-capture.json"
            source.write_text('{"vectors": []}\n')
            with self.assertRaises(target.StockMixedFixtureError):
                target.validate_original(source)

    def test_real_runtime_delegate_pin_distinguishes_dynamic_and_constant_nodes(self):
        for index, profile in enumerate(target.source.PROFILES):
            actual = target.DELEGATES[profile]
            if index < 4:
                self.assertTrue(actual["implementation_class"].endswith("$Ap2"))
                self.assertTrue(actual["compute_declaring_class"].endswith("$Ap2"))
            else:
                self.assertTrue(actual["implementation_class"].endswith("$MulOrAdd"))
                self.assertTrue(actual["compute_declaring_class"].endswith("$PureTransformer"))


if __name__ == "__main__":
    unittest.main()
