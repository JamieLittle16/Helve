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
            ],
        )
        self.assertEqual(len({name for _, roots in groups for name in roots}), 6)
        with tempfile.TemporaryDirectory() as tmp:
            candidate = json.loads(frontier.DEFAULT_PLAN.read_text())
            candidate["status"] = "ADMITTED"
            path = Path(tmp) / "forged-review.json"
            path.write_text(json.dumps(candidate))
            with self.assertRaises(frontier.BiomeIdSourceError):
                frontier.load_plan(path)
            candidate["status"] = "DISCOVERY_NOT_ADMISSION"
            candidate["groups"][1]["types"].append("net.minecraft.core.MappedRegistry")
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
