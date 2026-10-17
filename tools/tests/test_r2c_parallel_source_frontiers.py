"""Independent fail-closed client biome/wire source review preparation tests."""
from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import r2c_parallel_source_frontiers as gate


def fixture(label: str) -> dict:
    base = {
        "schema": 1, "target": gate.TARGET,
        "source_archive_sha256": gate.EXPECTED_SHA,
        "source_inspected": False,
        "production_admitted": False,
        "groups": [{} for _ in range(4)],
    }
    if label == "biome_client_ids":
        base["client_assignment_proven"] = False
    else:
        base.update(packet_wire_law_proven=False,
                    block_entity_semantics_proven=False,
                    chunk_publication_order_proven=False)
    return base


class ParallelSourceFrontierTests(unittest.TestCase):
    def test_pin_complete_nonadmission_both_groups(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            for name in ("source.zip", "atlas.sqlite", "lock.toml"):
                (root/name).write_bytes(b"synthetic fixture")
            def fake_runner(label, script, out, source, db, lock):
                self.assertIn(script, [i[0] for i in gate.JOBS.values()])
                self.assertTrue(source.is_file())
                self.assertTrue(db.is_file())
                self.assertTrue(lock.is_file())
                out.write_text(json.dumps(fixture(label)))
            with patch.object(gate, "sha256", return_value=gate.EXPECTED_SHA), \
                 patch.object(gate, "run_one", side_effect=fake_runner):
                manifest = gate.prepare(
                    root/"source.zip", root/"atlas.sqlite", root/"lock.toml",
                    root/"review-packet"
                )
            self.assertTrue(manifest["completed_in_parallel"])
            self.assertEqual(sorted(manifest["inventories"]),
                             ["biome_client_ids","chunk_wire"])
            self.assertFalse(manifest["client_biome_ids_admitted"])
            self.assertFalse(manifest["chunk_wire_admitted"])
            self.assertFalse(manifest["heightmap_per_state_source_semantics_admitted"])
            self.assertFalse(manifest["independent_atlas_gate_passed"])
            self.assertFalse(manifest["live_world_publication_admitted"])
            self.assertTrue((root/"review-packet"/"review-frontier-manifest.json").is_file())
            with patch.object(gate, "sha256", return_value=gate.EXPECTED_SHA):
                with self.assertRaisesRegex(ValueError,"must not exist"):
                    gate.prepare(root/"source.zip",root/"atlas.sqlite",root/"lock.toml",
                                 root/"review-packet")

    def test_drift_and_bad_authority_never_prepare_a_review_packet(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            p=Path(temp)/"candidate.json"
            for label in gate.JOBS:
                doc=fixture(label)
                p.write_text(json.dumps(doc))
                self.assertEqual(gate.check_one(label,p)["source_inspected"],False)
                for key in ("source_inspected","production_admitted"):
                    bad=fixture(label)
                    bad[key]=True
                    p.write_text(json.dumps(bad))
                    with self.assertRaisesRegex(ValueError,"cannot claim source admission"):
                        gate.check_one(label,p)
                bad=fixture(label)
                bad["source_archive_sha256"]="0"*64
                p.write_text(json.dumps(bad))
                with self.assertRaisesRegex(ValueError,"source/target"):
                    gate.check_one(label,p)
                bad=fixture(label)
                bad["groups"]=[]
                p.write_text(json.dumps(bad))
                with self.assertRaisesRegex(ValueError,"boundaries drifted"):
                    gate.check_one(label,p)
                bad=fixture(label)
                if label=="biome_client_ids":
                    bad["client_assignment_proven"]=True
                else:
                    bad["packet_wire_law_proven"]=True
                p.write_text(json.dumps(bad))
                with self.assertRaisesRegex(ValueError,"boundaries drifted"):
                    gate.check_one(label,p)

    def test_wrong_source_absent_db_and_subprocess_failure_reject(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp)
            for name in ("source.zip", "atlas.sqlite", "lock.toml"):
                (root/name).write_bytes(b"source-free test")
            with self.assertRaisesRegex(ValueError,"identity mismatch"):
                gate.prepare(root/"source.zip",root/"atlas.sqlite",
                             root/"lock.toml",root/"out")
            with patch.object(gate,"sha256",return_value=gate.EXPECTED_SHA):
                with self.assertRaisesRegex(ValueError,"Atlas/lock"):
                    gate.prepare(root/"source.zip",root/"missing",
                                 root/"lock.toml",root/"out")
                with patch.object(gate,"run_one",side_effect=ValueError("one failed")):
                    with self.assertRaisesRegex(ValueError,"one failed"):
                        gate.prepare(root/"source.zip",root/"atlas.sqlite",
                                     root/"lock.toml",root/"out")
                self.assertFalse((root/"out").exists())


if __name__=="__main__":
    unittest.main()
