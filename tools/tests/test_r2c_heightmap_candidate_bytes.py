"""Hermetic identity/corruption tests of non-admitted 26.2 heightmap bytes."""
from __future__ import annotations

import copy
import hashlib
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import official_r2c_heightmap_facts as official
import r2c_heightmap_candidate_bytes as candidate


LOCK = {
    "runtime": {"server_sha256": "test-pinned-server"},
    "source": {"archive_sha256": official.SOURCE_ARCHIVE_SHA256},
}


def document() -> dict:
    return {
        "schema": 1,
        "target": candidate.EXPECTED_TARGET.copy(),
        "server_sha256": LOCK["runtime"]["server_sha256"],
        "source_archive_sha256": official.SOURCE_ARCHIVE_SHA256,
        "source_file_sha256": official.SOURCE_FILE_SHA256.copy(),
        "bit_layout": candidate.EXPECTED_BITS.copy(),
        "heightmap_laws": candidate.EXPECTED_LAWS.copy(),
        "source_admitted": False,
        "production_admitted": False,
        "gate": "R2C-HEIGHTMAP-STATE-PREDICATES source fingerprint and independent SEM admission",
        "state_count": official.EXPECTED_STATE_COUNT,
        "flags_by_vanilla_state_id": [0, 3, 5, 11] +
            [1] * (official.EXPECTED_STATE_COUNT - 4),
    }


class CandidateBytesTests(unittest.TestCase):
    def test_exact_four_bit_byte_image_and_source_identity(self) -> None:
        data = document()
        packed = candidate.validate_candidate(data, LOCK)
        self.assertEqual(len(packed), 32_366)
        self.assertEqual(packed[:4], bytes([0, 3, 5, 11]))
        self.assertEqual(packed[-1], 1)
        self.assertEqual(len(packed), len(data["flags_by_vanilla_state_id"]))

    def test_exact_frozen_official_digest_precedes_materialization(self) -> None:
        packed = candidate.validate_candidate(document(), LOCK)
        # A correctly shaped candidate is not necessarily the independently
        # reproduced target-specific byte image. Reject it before output.
        with self.assertRaisesRegex(ValueError, "dense digest mismatch"):
            candidate.require_frozen_official_bytes(packed)

        # Exercise the success branch with a synthetic test-only identity.
        # Never weaken the real frozen official digest in production.
        digest = hashlib.sha256(packed).hexdigest()
        with patch.object(candidate, "EXPECTED_DENSE_SHA256", digest):
            candidate.require_frozen_official_bytes(packed)
            corrupted = bytearray(packed)
            corrupted[1234] ^= 2
            with self.assertRaisesRegex(ValueError, "dense digest mismatch"):
                candidate.require_frozen_official_bytes(bytes(corrupted))

    def test_source_and_runtime_pins_are_mandatory(self) -> None:
        for key, value in (
            ("server_sha256", "wrong"),
            ("source_archive_sha256", "wrong"),
            ("source_file_sha256", {"Heightmap.java": "wrong"}),
        ):
            data = document()
            data[key] = value
            with self.subTest(key=key), self.assertRaises(ValueError):
                candidate.validate_candidate(data, LOCK)

    def test_cannot_promote_a_candidate_by_changing_admission_flags(self) -> None:
        for key in ("source_admitted", "production_admitted"):
            data = document()
            data[key] = True
            with self.subTest(key=key), self.assertRaisesRegex(ValueError, "unadmitted"):
                candidate.validate_candidate(data, LOCK)

    def test_any_changed_target_law_bits_or_gate_fails(self) -> None:
        for key in ("target", "bit_layout", "heightmap_laws", "gate"):
            data = document()
            data[key] = None
            with self.subTest(key=key), self.assertRaises(ValueError):
                candidate.validate_candidate(data, LOCK)

    def test_non_exact_state_values_and_short_universe_fail_closed(self) -> None:
        for wrong in (16, -1, "7", True):
            data = document()
            data["flags_by_vanilla_state_id"][10] = wrong
            with self.subTest(wrong=wrong), self.assertRaisesRegex(ValueError, "4-bit"):
                candidate.validate_candidate(data, LOCK)
        data = document()
        data["flags_by_vanilla_state_id"].pop()
        with self.assertRaisesRegex(ValueError, "truncated"):
            candidate.validate_candidate(data, LOCK)
        data = document()
        data["flags_by_vanilla_state_id"][0] = 8
        with self.assertRaisesRegex(ValueError, "inconsistency"):
            candidate.validate_candidate(data, LOCK)


if __name__ == "__main__":
    unittest.main()
