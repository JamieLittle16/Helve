"""Verify both independently captured 26.2 family oracles stay frozen bit-for-bit.

The 320 values are source-free output observations, not invented formulas and
not independently source/VAR/SEM-admitted. Reconstruct all 160 five-field rows
per family without ever converting IEEE-754 values to Python floats.
"""
from __future__ import annotations

import copy
import json
import sys
import tomllib
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FIXTURE = ROOT / "vanilla/reports/worldgen-26_2-family-raw-bit-oracle-01.json"
LOCK = ROOT / "vanilla/vanilla.lock.toml"
sys.path.insert(0, str(ROOT / "tools"))
import worldgen_26_2_improved_noise_capture as improved  # noqa: E402
import worldgen_26_2_perlin_normal_capture as family  # noqa: E402
import worldgen_noise_oracle as raw  # noqa: E402

EXPECTED_ORIGINAL_SHA = {
    "perlin_noise": "82eb2e74d16c80420b46fae1c59a0cd15afa453e85b7b3ca681e385008bafdda",
    "normal_noise": "d4b8b5ced031550be9ba4161779d09c9c0231a92435b7752c6bdeff70af7e6fb",
}


def expand(stage: str, evidence: dict) -> dict:
    """Reproduce exactly the original 160 candidate rows from frozen bits."""
    observed = evidence["stages"][stage]
    vectors = []
    for seed, row in zip(evidence["seeds"], observed["values"], strict=True):
        for xyz, answer in zip(evidence["coordinates_xyz_bits"], row, strict=True):
            vectors.append(dict(
                seed_bits=seed, x_bits=xyz[0], y_bits=xyz[1],
                z_bits=xyz[2], value_bits=answer,
            ))
    return {
        "schema": 1, "kind": family.KIND, "minecraft": evidence["minecraft"],
        "protocol": evidence["protocol"], "data_version": evidence["data_version"],
        "source_archive_sha256": evidence["source_archive_sha256"],
        "official_server_sha256": evidence["official_server_sha256"],
        "stage": stage,
        "method_body_sha256": observed["method_body_sha256"],
        "source_text_included": evidence["source_text_included"],
        "independent_var_sem_admitted": evidence["independent_var_sem_admitted"],
        "production_worldgen_enabled": evidence["production_worldgen_enabled"],
        "profile": evidence["profile"],
        "source_methods": observed["source_methods"],
        "vectors": vectors,
    }


class FrozenFamilyVectorsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.evidence = json.loads(FIXTURE.read_text(encoding="utf-8"))
        with LOCK.open("rb") as reader:
            cls.lock = tomllib.load(reader)

    def test_exact_target_source_free_schema_and_official_file_hashes(self):
        p = self.evidence
        self.assertEqual(p["schema"], 1)
        self.assertEqual(p["kind"], "official_26_2_noise_family_bit_fixture_not_sem_admitted")
        self.assertEqual(p["minecraft"], "26.2")
        self.assertEqual(p["protocol"], 776)
        self.assertEqual(p["data_version"], 4903)
        self.assertEqual(p["source_archive_sha256"], self.lock["source"]["archive_sha256"])
        self.assertEqual(p["official_server_sha256"], self.lock["runtime"]["server_sha256"])
        self.assertEqual(p["original_manifest_sha256"], EXPECTED_ORIGINAL_SHA)
        self.assertEqual(p["profile"], family.PROFILE)
        self.assertFalse(p["source_text_included"])
        self.assertFalse(p["independent_var_sem_admitted"])
        self.assertFalse(p["production_worldgen_enabled"])
        self.assertEqual(set(p["stages"]), set(family.STAGES))
        self.assertEqual(len(p["seeds"]), 5)
        self.assertEqual(len(p["coordinates_xyz_bits"]), 32)

    def test_320_raw_bit_fixtures_roundtrip_to_strict_26_2_oracle(self):
        expected_inputs = improved.probes()
        self.assertEqual(len(expected_inputs), 160)
        for stage in family.STAGES:
            with self.subTest(stage=stage):
                manifest = expand(stage, self.evidence)
                result = family.validate_family(manifest, self.lock)
                self.assertEqual(len(result), 160)
                for actual, expected in zip(manifest["vectors"], expected_inputs, strict=True):
                    self.assertEqual({key: actual[key] for key in raw.INPUT_FIELDS}, expected)
                self.assertEqual(
                    manifest["method_body_sha256"], family.EXPECTED[stage]["get_value_3"][2]
                )
                self.assertEqual(
                    set(manifest["source_methods"]), set(family.EXPECTED[stage])
                )

    def test_mutating_one_raw_value_one_constructor_hash_or_one_profile_fails(self):
        for stage in family.STAGES:
            with self.subTest(stage=stage):
                manifest = expand(stage, self.evidence)
                manifest["vectors"][0]["value_bits"] = "not-raw-bits"
                with self.assertRaises(raw.OracleError):
                    family.validate_family(manifest, self.lock)
                manifest = expand(stage, self.evidence)
                manifest["source_methods"]["get_value_3"]["body_sha256"] = "0" * 64
                with self.assertRaises(family.CaptureError):
                    family.validate_family(manifest, self.lock)
                manifest = expand(stage, self.evidence)
                manifest["profile"] = copy.deepcopy(manifest["profile"])
                manifest["profile"]["amplitudes_bits"][2] = "0x3ff0000000000000"
                with self.assertRaises(family.CaptureError):
                    family.validate_family(manifest, self.lock)

    def test_distinct_perlin_and_normal_outputs_are_not_conflated(self):
        perlin = expand("perlin_noise", self.evidence)["vectors"]
        normal = expand("normal_noise", self.evidence)["vectors"]
        self.assertEqual(
            [tuple(v[k] for k in raw.INPUT_FIELDS) for v in perlin],
            [tuple(v[k] for k in raw.INPUT_FIELDS) for v in normal],
        )
        self.assertTrue(all(a["value_bits"] != b["value_bits"] for a, b in zip(perlin, normal)))


if __name__ == "__main__":
    unittest.main()
