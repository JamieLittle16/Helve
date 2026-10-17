"""Hermetic fail-closed tests for double-official-run heightmap fingerprints."""
from __future__ import annotations

import copy
import hashlib
import sys
import unittest
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import r2c_heightmap_reproducibility as repeat
import r2c_heightmap_candidate_bytes as candidate

LOCK={
    "runtime":{"server_sha256":"d"*64},
    "source":{"archive_sha256":candidate.official.SOURCE_ARCHIVE_SHA256},
}


def report() -> dict:
    facts=[1]*repeat.STATE_COUNT
    facts[0]=0
    facts[1]=3
    facts[2]=5
    facts[3]=11
    facts[4]=3
    return {
        "schema":1,
        "target":candidate.EXPECTED_TARGET,
        "server_sha256":"d"*64,
        "source_archive_sha256":candidate.official.SOURCE_ARCHIVE_SHA256,
        "source_file_sha256":candidate.official.SOURCE_FILE_SHA256,
        "state_count":repeat.STATE_COUNT,
        "flags_by_vanilla_state_id":facts,
        "bit_layout":candidate.EXPECTED_BITS,
        "heightmap_laws":candidate.EXPECTED_LAWS,
        "source_admitted":False,
        "production_admitted":False,
        "gate":"R2C-HEIGHTMAP-STATE-PREDICATES source fingerprint and independent SEM admission",
    }


class HeightmapReproducibilityTests(unittest.TestCase):
    def test_full_universe_reproduces_exactly_and_keeps_authority_false(self) -> None:
        first=report()
        result=repeat.compare(first,copy.deepcopy(first),LOCK)
        self.assertEqual(result["state_count"],32366)
        self.assertEqual(result["reproduced_dense_state_fact_sha256"],
                         hashlib.sha256(bytes(first["flags_by_vanilla_state_id"])).hexdigest())
        self.assertEqual(sum(result["four_bit_histogram"]),32366)
        self.assertEqual(result["official_independent_probe_runs"],2)
        self.assertFalse(result["independent_semantic_source_review"])
        self.assertFalse(result["source_var_sem_admitted"])
        self.assertFalse(result["production_admitted"])
        self.assertGreater(result["client_heightmap_state_predicate_counts"]["leaves"],0)

    def test_changed_single_state_fails_even_if_metadata_is_equal(self) -> None:
        first=report()
        second=copy.deepcopy(first)
        second["flags_by_vanilla_state_id"][200]=3
        with self.assertRaisesRegex(ValueError,"not reproducible at ID 200"):
            repeat.compare(first,second,LOCK)

    def test_unauthorized_admission_changed_hash_or_truncated_table_rejected(self) -> None:
        first=report()
        for key in ("source_admitted","production_admitted"):
            invalid=copy.deepcopy(first)
            invalid[key]=True
            with self.subTest(key=key),self.assertRaisesRegex(ValueError,"unadmitted"):
                repeat.compare(first,invalid,LOCK)
        invalid=copy.deepcopy(first)
        invalid["server_sha256"]="c"*64
        with self.assertRaisesRegex(ValueError,"pin mismatch"):
            repeat.compare(first,invalid,LOCK)
        invalid=copy.deepcopy(first)
        invalid["flags_by_vanilla_state_id"].pop()
        with self.assertRaisesRegex(ValueError,"truncated"):
            repeat.compare(first,invalid,LOCK)

    def test_all_air_or_all_nonmotion_rejected_as_broken_probe(self) -> None:
        first=report()
        first["flags_by_vanilla_state_id"]=[0]*repeat.STATE_COUNT
        with self.assertRaisesRegex(ValueError,"diversity"):
            repeat.compare(first,copy.deepcopy(first),LOCK)

if __name__=="__main__":
    unittest.main()
