"""Fail-closed synthetic tests for the source-free official-noise comparison format.

Fixtures are deliberately NOT official Minecraft outputs. They verify that
the comparison cannot convert floats, ignore signed zeros or declare authority.
"""
import copy
import struct
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import worldgen_noise_oracle as oracle  # noqa: E402

LOCK = {
    "minecraft": "26.2",
    "protocol": 776,
    "data_version": 4903,
    "source": {"archive_sha256": "a" * 64},
    "runtime": {"server_sha256": "b" * 64},
}


def bits(value: float) -> str:
    return "0x" + struct.pack(">d", value).hex()


def manifest(kind: str) -> dict:
    values = [-0.0, 0.0, -31.5, 31.5, -16.0, 16.0, 1.125, -1.125]
    records = []
    for i in range(24):
        records.append({
            "seed_bits": f"0x{i % 3:016x}",
            "x_bits": bits(values[i % len(values)]),
            "y_bits": bits(float(i - 12)),
            "z_bits": bits(float(i + 32)),
            "value_bits": f"0x{(i * 0x102030405060708) & ((1 << 64) - 1):016x}",
        })
    return {
        "schema": 1,
        "kind": kind,
        "minecraft": "26.2",
        "protocol": 776,
        "data_version": 4903,
        "source_archive_sha256": "a" * 64,
        "official_server_sha256": "b" * 64,
        "stage": "normal_noise",
        "method_body_sha256": "c" * 64,
        "source_text_included": False,
        "independent_var_sem_admitted": False,
        "production_worldgen_enabled": False,
        "vectors": records,
    }


class NoiseOracleTests(unittest.TestCase):
    def setUp(self):
        self.ref = manifest("official_26_2_noise_oracle_candidate")
        self.candidate = manifest("helve_noise_candidate")

    def test_equal_raw_vectors_remain_unadmitted(self):
        result = oracle.compare(self.ref, self.candidate, LOCK)
        self.assertTrue(result["bit_pattern_match"])
        self.assertEqual(result["matched_raw_bit_patterns"], 24)
        self.assertFalse(result["official_source_review_admitted"])
        self.assertFalse(result["production_worldgen_enabled"])

    def test_minus_zero_output_is_not_plus_zero(self):
        self.ref["vectors"][0]["value_bits"] = "0x8000000000000000"
        self.candidate["vectors"][0]["value_bits"] = "0x0000000000000000"
        with self.assertRaisesRegex(oracle.OracleError, "bit-pattern mismatches"):
            oracle.compare(self.ref, self.candidate, LOCK)

    def test_distinct_nan_payloads_are_not_equal(self):
        self.ref["vectors"][1]["value_bits"] = "0x7ff8000000000001"
        self.candidate["vectors"][1]["value_bits"] = "0x7ff8000000000002"
        with self.assertRaisesRegex(oracle.OracleError, "bit-pattern mismatches"):
            oracle.compare(self.ref, self.candidate, LOCK)

    def test_extra_or_missing_input_is_rejected(self):
        self.candidate["vectors"][0]["x_bits"] = bits(-30.0)
        with self.assertRaisesRegex(oracle.OracleError, "coverage mismatch"):
            oracle.compare(self.ref, self.candidate, LOCK)

    def test_drifted_archive_and_method_do_not_pass(self):
        self.ref["source_archive_sha256"] = "f" * 64
        with self.assertRaisesRegex(oracle.OracleError, "source lock"):
            oracle.compare(self.ref, self.candidate, LOCK)
        self.ref["source_archive_sha256"] = "a" * 64
        self.candidate["method_body_sha256"] = "d" * 64
        with self.assertRaisesRegex(oracle.OracleError, "stage/method mismatch"):
            oracle.compare(self.ref, self.candidate, LOCK)

    def test_fake_production_or_var_sem_authority_fails(self):
        for name in ("production_worldgen_enabled", "independent_var_sem_admitted"):
            changed = copy.deepcopy(self.candidate)
            changed[name] = True
            with self.subTest(flag=name), self.assertRaisesRegex(oracle.OracleError, name):
                oracle.compare(self.ref, changed, LOCK)

    def test_missing_negative_zero_and_few_seeds_fail(self):
        for vector in self.ref["vectors"]:
            if vector["x_bits"] == bits(-0.0):
                vector["x_bits"] = bits(2.0)
        with self.assertRaisesRegex(oracle.OracleError, "missing -0.0"):
            oracle.compare(self.ref, self.candidate, LOCK)
        self.ref = manifest("official_26_2_noise_oracle_candidate")
        for vector in self.ref["vectors"]:
            vector["seed_bits"] = "0x0000000000000000"
        with self.assertRaises(oracle.OracleError):
            oracle.compare(self.ref, self.candidate, LOCK)

    def test_duplicate_vectors_and_unreviewed_stage_rejected(self):
        self.ref["vectors"][1] = self.ref["vectors"][0].copy()
        with self.assertRaisesRegex(oracle.OracleError, "duplicate"):
            oracle.compare(self.ref, self.candidate, LOCK)
        self.ref = manifest("official_26_2_noise_oracle_candidate")
        self.ref["stage"] = "vanilla_26_2_parity_admitted"
        with self.assertRaisesRegex(oracle.OracleError, "invalid or unreviewed"):
            oracle.compare(self.ref, self.candidate, LOCK)


if __name__ == "__main__":
    unittest.main()
