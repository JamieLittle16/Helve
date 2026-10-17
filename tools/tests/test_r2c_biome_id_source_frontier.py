"""The R2C biome-ID source frontier must discover, never self-admit."""

from __future__ import annotations

import json
import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path

TOOLS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOLS))
import r2c_biome_id_source_frontier as frontier


def mock_atlas() -> sqlite3.Connection:
    connection = sqlite3.connect(":memory:")
    connection.row_factory = sqlite3.Row
    connection.executescript("""
        CREATE TABLE source_files(id INTEGER PRIMARY KEY, path TEXT);
        CREATE TABLE types(id INTEGER PRIMARY KEY, qualified_name TEXT, file_id INTEGER);
        CREATE TABLE methods(
            id INTEGER PRIMARY KEY, type_id INTEGER, name TEXT, signature TEXT,
            param_count INTEGER, start_line INTEGER, end_line INTEGER,
            normalized_sha256 TEXT, body_sha256 TEXT
        );
        CREATE TABLE meta(key TEXT PRIMARY KEY, value TEXT);
        CREATE TABLE hazards(method_id INTEGER, kind TEXT);
        CREATE TABLE classifications(method_id INTEGER, label TEXT, source TEXT);
        INSERT INTO meta VALUES ('fingerprint_algorithm','java-token-v2-literal-sensitive');
        INSERT INTO source_files VALUES (1, 'src/Test.java');
        INSERT INTO types VALUES (1, 'net.minecraft.core.MappedRegistry', 1);
        INSERT INTO methods VALUES (
          1, 1, 'byId', 'byId(final int ordinal)', 1, 10, 15,
          'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa',
          'bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb'
        );
        INSERT INTO types VALUES (3, 'net.minecraft.util.Util', 1);
        INSERT INTO methods VALUES (
          3, 3, 'sequence', 'sequence(List futures)', 1, 20, 28,
          'cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc',
          'dddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddd'
        );
    """)
    return connection


class BiomeSourceFrontierTests(unittest.TestCase):
    def test_frozen_plan_keeps_independent_client_assignment_gap(self) -> None:
        groups = frontier.load_plan(frontier.DEFAULT_PLAN)
        self.assertEqual(
            [g[0] for g in groups],
            [
                "LOADED-REGISTRY-ID-ALLOCATION",
                "CONFIGURATION-BIOME-ENTRY-PUBLICATION",
                "BIOME-CONTAINER-ID-BINDING",
                "NETWORK-REGISTRY-RECEIVE-AND-ORDERED-REGISTRATION",
            ],
        )
        self.assertEqual(len({name for _, roots in groups for name in roots}), 8)
        plan = json.loads(frontier.DEFAULT_PLAN.read_text())
        self.assertEqual(plan["targeted_methods"][0]["type"], "net.minecraft.util.Util")
        self.assertEqual(plan["targeted_methods"][0]["method"], "sequence")
        self.assertEqual(
            groups[3][1],
            (
                "net.minecraft.resources.NetworkRegistryLoadTask",
                "net.minecraft.resources.RegistryLoadTask",
            ),
        )
        with tempfile.TemporaryDirectory() as tmp:
            candidate = json.loads(frontier.DEFAULT_PLAN.read_text())
            candidate["status"] = "ADMITTED"
            path = Path(tmp) / "forged-review.json"
            path.write_text(json.dumps(candidate))
            with self.assertRaises(frontier.BiomeIdSourceError):
                frontier.load_plan(path)
            candidate["status"] = "DISCOVERY_NOT_ADMISSION"
            candidate["targeted_methods"][0]["method"] = "sequenceAsync"
            path.write_text(json.dumps(candidate))
            with self.assertRaises(frontier.BiomeIdSourceError):
                frontier.load_plan(path)
            candidate["targeted_methods"][0]["method"] = "sequence"
            # The legacy owner was never in the pinned Atlas: reject stale
            # plans instead of silently falling back to a guessed class.
            candidate["targeted_methods"][0]["type"] = "net.minecraft.Util"
            path.write_text(json.dumps(candidate))
            with self.assertRaisesRegex(frontier.BiomeIdSourceError, "bounded Util.sequence"):
                frontier.load_plan(path)
            candidate["targeted_methods"][0]["type"] = "net.minecraft.util.Util"
            candidate["groups"][1]["types"].append("net.minecraft.core.MappedRegistry")
            path.write_text(json.dumps(candidate))
            with self.assertRaises(frontier.BiomeIdSourceError):
                frontier.load_plan(path)
            candidate["groups"][1]["types"].pop()
            candidate["groups"].pop()
            path.write_text(json.dumps(candidate))
            with self.assertRaisesRegex(frontier.BiomeIdSourceError, "four finite"):
                frontier.load_plan(path)
            candidate["groups"].append({
                "id": "NETWORK-REGISTRY-RECEIVE-AND-ORDERED-REGISTRATION",
                "review_focus": "unreviewed",
                "types": ["net.minecraft.core.MappedRegistry"],
            })
            path.write_text(json.dumps(candidate))
            with self.assertRaises(frontier.BiomeIdSourceError):
                frontier.load_plan(path)

    def test_inventory_contains_exact_atlas_fingerprints_only(self) -> None:
        db = mock_atlas()
        try:
            candidates = frontier.exact_type_declarations(
                db, "net.minecraft.core.MappedRegistry"
            )
            self.assertEqual(len(candidates), 1)
            self.assertEqual(candidates[0]["signature"], "byId(final int ordinal)")
            self.assertEqual(candidates[0]["normalized_sha256"], "a" * 64)
            self.assertEqual(candidates[0]["body_sha256"], "b" * 64)
            result = frontier.inventory(
                db,
                (("LOADED-REGISTRY-ID-ALLOCATION",
                  ("net.minecraft.core.MappedRegistry",)),),
                source_sha256=frontier.SOURCE_SHA256,
                plan_sha256="c" * 64,
            )
            self.assertFalse(result["source_inspected"])
            self.assertFalse(result["client_assignment_proven"])
            self.assertFalse(result["production_admitted"])
            self.assertEqual(
                result["groups"][0]["roots"][0]["methods"][0]["signature"],
                "byId(final int ordinal)",
            )
            with self.assertRaises(frontier.BiomeIdSourceError):
                frontier.inventory(
                    db,
                    (("LOADED-REGISTRY-ID-ALLOCATION",
                      ("net.minecraft.core.MappedRegistry",)),),
                    source_sha256="0" * 64,
                    plan_sha256="c" * 64,
                )
        finally:
            db.close()

    def test_abstract_interface_method_is_not_a_verified_implementation(self) -> None:
        db = mock_atlas()
        try:
            db.execute("UPDATE methods SET body_sha256=NULL WHERE id=1")
            [candidate] = frontier.exact_type_declarations(
                db, "net.minecraft.core.MappedRegistry"
            )
            self.assertIsNone(candidate["body_sha256"])
            self.assertTrue(candidate["declaration_only"])
            self.assertEqual(candidate["normalized_sha256"], "a" * 64)
        finally:
            db.close()


    def test_util_sequence_named_delegate_is_bounded_and_unadmitted(self) -> None:
        db = mock_atlas()
        try:
            [method] = frontier.exact_named_declarations(
                db, "net.minecraft.util.Util", "sequence"
            )
            self.assertEqual(method["signature"], "sequence(List futures)")
            self.assertEqual(method["normalized_sha256"], "c" * 64)
            self.assertEqual(method["body_sha256"], "d" * 64)
            self.assertFalse(method["declaration_only"])
            result = frontier.inventory(
                db,
                (("LOADED-REGISTRY-ID-ALLOCATION",
                  ("net.minecraft.core.MappedRegistry",)),),
                source_sha256=frontier.SOURCE_SHA256,
                plan_sha256="e" * 64,
                include_ordered_sequence=True,
            )
            self.assertEqual(result["targeted_methods"][0]["overloads"], [method])
            self.assertFalse(result["source_inspected"])
            self.assertFalse(result["client_assignment_proven"])
            self.assertFalse(result["production_admitted"])
            # The historical pre-26.2 owner is not accepted, even if
            # someone adds a synthetic alias to the Atlas.
            with self.assertRaisesRegex(frontier.BiomeIdSourceError, "unplanned named delegate"):
                frontier.exact_named_declarations(db, "net.minecraft.Util", "sequence")
            with self.assertRaises(frontier.BiomeIdSourceError):
                frontier.exact_named_declarations(db, "net.minecraft.util.Util", "other")
            with self.assertRaises(frontier.BiomeIdSourceError):
                frontier.exact_named_declarations(
                    db, "net.minecraft.util.Util", "sequence", overload_cap=17
                )
            db.execute("UPDATE methods SET body_sha256=NULL WHERE id=3")
            [abstract] = frontier.exact_named_declarations(
                db, "net.minecraft.util.Util", "sequence"
            )
            self.assertTrue(abstract["declaration_only"])
            # Multiple owner identities are as unsafe as no identity.
            db.execute("INSERT INTO types VALUES (4, 'net.minecraft.util.Util', 1)")
            with self.assertRaisesRegex(frontier.BiomeIdSourceError, "resolve once"):
                frontier.exact_named_declarations(db, "net.minecraft.util.Util", "sequence")
            db.execute("DELETE FROM types WHERE id=4")
            db.execute("DELETE FROM methods WHERE id=3")
            with self.assertRaises(frontier.BiomeIdSourceError):
                frontier.exact_named_declarations(db, "net.minecraft.util.Util", "sequence")
        finally:
            db.close()

    def test_missing_ambiguous_and_excessive_declarations_fail_closed(self) -> None:
        db = mock_atlas()
        try:
            with self.assertRaises(frontier.BiomeIdSourceError):
                frontier.exact_type_declarations(
                    db, "net.minecraft.core.DoesNotExist"
                )
            db.execute(
                "INSERT INTO types VALUES (2, 'net.minecraft.core.MappedRegistry', 1)"
            )
            with self.assertRaises(frontier.BiomeIdSourceError):
                frontier.exact_type_declarations(
                    db, "net.minecraft.core.MappedRegistry"
                )
            db.execute("DELETE FROM types WHERE id=2")
            with self.assertRaises(frontier.BiomeIdSourceError):
                frontier.exact_type_declarations(
                    db, "net.minecraft.core.MappedRegistry", method_cap=257
                )
            db.execute("DELETE FROM methods")
            with self.assertRaises(frontier.BiomeIdSourceError):
                frontier.exact_type_declarations(
                    db, "net.minecraft.core.MappedRegistry"
                )
        finally:
            db.close()


if __name__ == "__main__":
    unittest.main()
