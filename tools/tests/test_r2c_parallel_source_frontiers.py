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
        # Reuse the already checked-in independent source-admission report,
        # not a freshly invented source or a second semantic review.
        admitted = json.loads(gate.ADMITTED_WORLD_STATE.read_text())
        classes = list(sorted(gate.REUSABLE_WIRE_ROOTS))
        groups = [{"type": "unrelated", "declarations": []} for _ in range(2)]
        for owner in classes:
            methods = []
            for row in admitted["required_methods"]:
                if not row["source"].startswith(owner + "#"):
                    continue
                methods.append({
                    "signature": row["source"].split("#", 1)[1],
                    "normalized_sha256": row["normalized_sha256"],
                    "body_sha256": row["body_sha256"],
                    "declaration_only": False,
                })
            groups.append({"type": owner, "declarations": methods})
        base["groups"] = groups
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
            self.assertFalse(manifest["outer_packet_semantics_reused_or_admitted"])
            self.assertEqual(len(manifest["reused_independently_admitted_inner_wire_methods"]), 7)
            self.assertTrue(all(
                not entry["outer_chunk_wire_admitted"]
                for entry in manifest["reused_independently_admitted_inner_wire_methods"]
            ))
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

    def test_only_exact_previously_reviewed_fingerprints_can_be_reused(self) -> None:
        prior = json.loads(gate.ADMITTED_WORLD_STATE.read_text())
        valid = fixture("chunk_wire")
        reused = gate.exact_admitted_world_state_reuse(valid, prior)
        self.assertEqual(len(reused), 7)
        self.assertEqual(len({entry["source"] for entry in reused}), 7)
        self.assertTrue(all(entry["authority"] ==
                            "PRIOR_INDEPENDENT_WORLD_STATE_VAR_ONLY"
                            for entry in reused))

        import copy
        changed = copy.deepcopy(valid)
        changed["groups"][2]["declarations"][0]["body_sha256"] = "f" * 64
        with self.assertRaisesRegex(ValueError, "fingerprint drift"):
            gate.exact_admitted_world_state_reuse(changed, prior)

        lost = copy.deepcopy(valid)
        lost["groups"][2]["declarations"].pop()
        with self.assertRaisesRegex(ValueError, "seven exact"):
            gate.exact_admitted_world_state_reuse(lost, prior)

        forged = copy.deepcopy(prior)
        forged["admitted"] = False
        with self.assertRaisesRegex(ValueError, "source gate invalid"):
            gate.exact_admitted_world_state_reuse(valid, forged)

        forged = copy.deepcopy(prior)
        forged["source"]["archive_sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "source gate invalid"):
            gate.exact_admitted_world_state_reuse(valid, forged)

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
