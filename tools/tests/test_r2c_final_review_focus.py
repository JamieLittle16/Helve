"""Strict, source-free first-pass queue derived from the admitted R2C evidence."""
from __future__ import annotations

import copy
import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import r2c_final_review_focus as review
import r2c_parallel_source_frontiers as existing


def fixture() -> tuple[dict, dict, dict, dict]:
    prior = json.loads(existing.ADMITTED_WORLD_STATE.read_text(encoding="utf-8"))
    wire_owners = {owner for owner, _ in review.WIRE}
    wire_owners.update(existing.REUSABLE_WIRE_ROOTS)
    methods = {owner: [] for owner in wire_owners}
    for row in prior["required_methods"]:
        for owner in existing.REUSABLE_WIRE_ROOTS:
            if row["source"].startswith(owner + "#"):
                methods[owner].append({
                    "signature": row["source"].split("#", 1)[1],
                    "normalized_sha256": row["normalized_sha256"],
                    "body_sha256": row["body_sha256"],
                    "declaration_only": False,
                    "hazard_leads": [],
                })
    for owner, prefix in review.WIRE:
        methods[owner].append({
            "signature": prefix + (" end)" if "(" in prefix and not prefix.endswith(")") else ""),
            "normalized_sha256": "a" * 64,
            "body_sha256": "b" * 64,
            "declaration_only": False,
            "hazard_leads": ["CLIENT_OBSERVABLE"],
        })
    wire = {
        "schema": 1, "kind": "r2c-chunk-wire-source-declarations-unadmitted-v1",
        "target": existing.TARGET, "source_archive_sha256": existing.EXPECTED_SHA,
        "source_inspected": False, "production_admitted": False,
        "groups": [{"type": owner, "declarations": rows} for owner, rows in methods.items()],
    }
    roots = {}
    for owner, prefix in review.BIOME:
        roots.setdefault(owner, []).append({
            "signature": prefix + (" end)" if "(" in prefix and not prefix.endswith(")") else ""),
            "normalized_sha256": "a" * 64,
            "body_sha256": "b" * 64,
            "declaration_only": False,
            "hazard_leads": ["REGISTRY"],
        })
    util = roots.pop("net.minecraft.util.Util")
    biome = {
        "schema": 1, "kind": "r2c-biome-id-source-declaration-inventory-v1",
        "target": existing.TARGET, "source_archive_sha256": existing.EXPECTED_SHA,
        "source_inspected": False, "production_admitted": False,
        "groups": [{"roots": [{"type": owner, "methods": rows}
                              for owner, rows in roots.items()]}],
        "targeted_methods": [{
            "type": "net.minecraft.util.Util", "method": "sequence",
            "overloads": util,
        }],
    }
    manifest = {
        "schema": 1,
        "kind": "r2c-26_2-parallel-source-frontier-handoff-v1",
        "target": existing.TARGET, "source_archive_sha256": existing.EXPECTED_SHA,
        **{flag: False for flag in review.NONADMITTED_FLAGS},
        "reused_world_state_gate_id": existing.WORLD_STATE_GATE_ID,
        "reused_independently_admitted_inner_wire_methods":
            existing.exact_admitted_world_state_reuse(wire, prior),
    }
    return manifest, biome, wire, prior


class FinalReviewFocusTests(unittest.TestCase):
    def test_exact_methods_only_and_prior_var_reuse_excluded(self) -> None:
        manifest, biome, wire, prior = fixture()
        report = review.build(manifest, biome, wire, prior)
        self.assertEqual(len(report["biome_priority"]), 10)
        self.assertEqual(len(report["outer_wire_priority"]), 9)
        self.assertEqual(report["already_admitted_inner_wire_methods"], 7)
        self.assertFalse(report["delegate_closure_proven"])
        self.assertFalse(report["production_admitted"])
        reused = {row["source"] for row in
                  manifest["reused_independently_admitted_inner_wire_methods"]}
        self.assertTrue(all(item["source"] not in reused for item in
                            report["biome_priority"] + report["outer_wire_priority"]))
        self.assertTrue(all(not item["semantics_admitted"] and
                            not item["source_inspected"] for item in
                            report["biome_priority"] + report["outer_wire_priority"]))

    def test_missing_or_ambiguous_or_declaration_only_fails_closed(self) -> None:
        manifest, biome, wire, prior = fixture()
        changed = copy.deepcopy(biome)
        changed["groups"][0]["roots"][0]["methods"].pop(0)
        with self.assertRaisesRegex(review.FocusError, "missing or ambiguous"):
            review.build(manifest, changed, wire, prior)
        changed = copy.deepcopy(biome)
        changed["groups"][0]["roots"][0]["methods"].append(
            changed["groups"][0]["roots"][0]["methods"][0].copy()
        )
        with self.assertRaisesRegex(review.FocusError, "missing or ambiguous"):
            review.build(manifest, changed, wire, prior)
        changed = copy.deepcopy(biome)
        changed["groups"][0]["roots"][0]["methods"][0]["declaration_only"] = True
        with self.assertRaisesRegex(review.FocusError, "incomplete Atlas"):
            review.build(manifest, changed, wire, prior)

    def test_no_forged_source_admission_or_old_client_util_owner(self) -> None:
        manifest, biome, wire, prior = fixture()
        altered = copy.deepcopy(manifest)
        altered["client_biome_ids_admitted"] = True
        with self.assertRaisesRegex(review.FocusError, "nonadmission"):
            review.build(altered, biome, wire, prior)
        altered = copy.deepcopy(manifest)
        altered["reused_independently_admitted_inner_wire_methods"].pop()
        with self.assertRaisesRegex(review.FocusError, "seven-method reuse"):
            review.build(altered, biome, wire, prior)
        altered = copy.deepcopy(biome)
        altered["targeted_methods"][0]["type"] = "net.minecraft.Util"
        with self.assertRaisesRegex(review.FocusError, "ordered-futures"):
            review.build(manifest, altered, wire, prior)
        altered = copy.deepcopy(wire)
        for group in altered["groups"]:
            if group["type"] in existing.REUSABLE_WIRE_ROOTS:
                group["declarations"][0]["body_sha256"] = "0" * 64
                break
        with self.assertRaisesRegex(ValueError, "fingerprint drift"):
            review.build(manifest, biome, altered, prior)


if __name__ == "__main__":
    unittest.main()
