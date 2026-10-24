"""Immutable original stock 23rd key/parameters SHA and ancestry gates."""
from __future__ import annotations

import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import worldgen_26_2_stock_finaldensity_twenty_third_parameters_receipt as receipt  # noqa: E402
import test_worldgen_26_2_stock_final_density_twenty_third_layer as probe  # noqa: E402


class OriginalTwentyThirdParametersReceiptTests(unittest.TestCase):
    def synth(self) -> dict:
        # Synthetic transport only: actual source-owned bytes are not in CI.
        r = probe.OriginalTwentyThirdSpaghettiParametersTests().report()
        for shape in r["shapes"]:
            shape["noise_first_octave"] = receipt.FIRST_OCTAVE
            shape["noise_amplitudes_rawbits"] = receipt.AMPLITUDES
        return r

    def fake_file(self, path: Path, report: dict) -> tuple[int, str]:
        raw = (json.dumps(report, indent=2, sort_keys=True) + "\n").encode("ascii")
        path.write_bytes(raw)
        return len(raw), hashlib.sha256(raw).hexdigest()

    def test_original_receipt_pins_actual_source_parameters_no_new_xyz_values(self):
        self.assertEqual(receipt.REPORT_BYTES, 33486)
        self.assertEqual(receipt.REPORT_SHA256,
                         "e3dde9db3a83e7cd16c126536475943728e73c11a4ddd44820a2cad4f35ffc05")
        self.assertEqual(receipt.PARAMETERS["noise_parameters_key"],
                         "minecraft:spaghetti_3d_thickness")
        self.assertEqual(receipt.FIRST_OCTAVE, "-8")
        self.assertEqual(receipt.AMPLITUDES, "3ff0000000000000")
        self.assertEqual(receipt.TELEMETRY["genuinely_new_sample_ieee_words"], 0)
        self.assertEqual(len(receipt.owner.prior_leaf.load()), 128)

    def test_synthetic_good_transport_all_fields_are_revalidated(self):
        with tempfile.TemporaryDirectory() as directory:
            p = Path(directory) / "synthetic-only.json"
            report = self.synth()
            size, sha = self.fake_file(p, report)
            with patch.object(receipt, "REPORT_BYTES", size), patch.object(
                receipt, "REPORT_SHA256", sha
            ):
                result = receipt.validate_original(p)
                self.assertEqual(result["first_octave"], -8)
                self.assertEqual(result["old_noise_values_anchored"], 128)
                self.assertFalse(result["production_worldgen_enabled"])

    def test_modified_real_signature_or_anchors_fail_even_under_modified_sha(self):
        for mutate in (
            lambda x: x["shapes"][0].__setitem__("noise_first_octave", "-7"),
            lambda x: x["shapes"][1].__setitem__(
                "noise_amplitudes_rawbits", "0000000000000000"
            ),
            lambda x: x["vectors"][127].__setitem__(
                "old_twenty_first_noise_bits", "0x0000000000000000"
            ),
            lambda x: x.__setitem__("production_worldgen_enabled", True),
            lambda x: x.__setitem__("twenty_third_real_spaghetti_parameters_qualified", True),
        ):
            with self.subTest(mutation=str(mutate)), tempfile.TemporaryDirectory() as directory:
                path = Path(directory) / "tampered-but-pinned.json"
                report = self.synth()
                mutate(report)
                size, digest = self.fake_file(path, report)
                with patch.object(receipt, "REPORT_BYTES", size), patch.object(
                    receipt, "REPORT_SHA256", digest
                ):
                    with self.assertRaises(receipt.TwentyThirdReceiptError):
                        receipt.validate_original(path)

    def test_unpinned_capture_rejected_before_parsing(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "fake.json"
            self.fake_file(path, self.synth())
            with self.assertRaises(receipt.TwentyThirdReceiptError):
                receipt.validate_original(path)


if __name__ == "__main__":
    unittest.main()
