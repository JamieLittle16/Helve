"""R2C chunk-with-light source inspection is bounded and never production admission."""

from __future__ import annotations

import json
import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path

TOOLS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOLS))
import r2c_chunk_wire_source_frontier as frontier


def mock_atlas() -> sqlite3.Connection:
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    conn.executescript("""
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
        INSERT INTO source_files VALUES (1, 'src/Packet.java');
        INSERT INTO types VALUES (
          1, 'net.minecraft.network.protocol.game.ClientboundLevelChunkWithLightPacket', 1
        );
        INSERT INTO methods VALUES (
          1, 1, 'write', 'write(final FriendlyByteBuf output)', 1, 10, 15,
          'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa',
          'bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb'
        );
    """)
    return conn


class ChunkWireSourceFrontierTests(unittest.TestCase):
    def test_exact_profile_only_no_source_authority(self) -> None:
        roots = frontier.load_plan(frontier.PLAN)
        self.assertEqual(
            [(x["group"], x["type"]) for x in roots], list(frontier.ROOTS)
        )
        self.assertEqual(len(roots), 4)
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "plan.json"
            source = json.loads(frontier.PLAN.read_text())
            for key, value in (
                ("status", "PRODUCTION_ADMITTED"),
                ("source_archive_sha256", "f" * 64),
                ("max_methods_per_type", 4096),
            ):
                forged = json.loads(json.dumps(source))
                forged[key] = value
                path.write_text(json.dumps(forged), encoding="utf-8")
                with self.assertRaises(frontier.ChunkWireSourceError):
                    frontier.load_plan(path)

            forged = json.loads(json.dumps(source))
            forged["roots"][1]["type"] = forged["roots"][0]["type"]
            path.write_text(json.dumps(forged), encoding="utf-8")
            with self.assertRaises(frontier.ChunkWireSourceError):
                frontier.load_plan(path)
            forged = json.loads(json.dumps(source))
            forged["roots"][0]["must_review"] = []
            path.write_text(json.dumps(forged), encoding="utf-8")
            with self.assertRaises(frontier.ChunkWireSourceError):
                frontier.load_plan(path)

    def test_fingerprints_and_report_never_promote_packet(self) -> None:
        conn = mock_atlas()
        try:
            methods = frontier.exact_declarations(conn, frontier.ROOTS[0][1])
            self.assertEqual(len(methods), 1)
            self.assertEqual(methods[0]["signature"], "write(final FriendlyByteBuf output)")
            self.assertEqual(methods[0]["normalized_sha256"], "a" * 64)
            self.assertEqual(methods[0]["body_sha256"], "b" * 64)
            roots = frontier.load_plan(frontier.PLAN)
            # The inventory must be made complete, not silently pretend that
            # this deliberately one-type mock Atlas covered all four roots.
            with self.assertRaises(frontier.ChunkWireSourceError):
                frontier.source_free_inventory(
                    conn, roots,
                    source_sha256=frontier.SOURCE_SHA256,
                    plan_sha256="c" * 64,
                )
            with self.assertRaises(frontier.ChunkWireSourceError):
                frontier.source_free_inventory(
                    conn, roots[:1],
                    source_sha256="f" * 64, plan_sha256="c" * 64,
                )
            inventory = frontier.source_free_inventory(
                conn, roots[:1],
                source_sha256=frontier.SOURCE_SHA256, plan_sha256="c" * 64,
            )
            self.assertEqual(inventory["kind"], frontier.KIND)
            self.assertFalse(inventory["source_inspected"])
            self.assertFalse(inventory["packet_wire_law_proven"])
            self.assertFalse(inventory["block_entity_semantics_proven"])
            self.assertFalse(inventory["chunk_publication_order_proven"])
            self.assertFalse(inventory["production_admitted"])
            self.assertEqual(inventory["groups"][0]["declarations"][0]["body_sha256"], "b" * 64)
            self.assertNotIn("source_text", json.dumps(inventory))
        finally:
            conn.close()

    def test_empty_atlas_body_hash_is_not_implementation_evidence(self) -> None:
        conn = mock_atlas()
        try:
            conn.execute(
                "UPDATE methods SET body_sha256=? WHERE id=1",
                (frontier.EMPTY_BODY_SHA256,),
            )
            [method] = frontier.exact_declarations(conn, frontier.ROOTS[0][1])
            self.assertEqual(method["body_sha256"], frontier.EMPTY_BODY_SHA256)
            self.assertTrue(method["declaration_only"])
        finally:
            conn.close()

    def test_abstract_declaration_is_not_a_body_proof(self) -> None:
        conn = mock_atlas()
        try:
            conn.execute("UPDATE methods SET body_sha256=NULL WHERE id=1")
            [method] = frontier.exact_declarations(conn, frontier.ROOTS[0][1])
            self.assertTrue(method["declaration_only"])
            self.assertIsNone(method["body_sha256"])
        finally:
            conn.close()

    def test_missing_and_ambiguous_roots_are_rejected(self) -> None:
        conn = mock_atlas()
        try:
            with self.assertRaises(frontier.ChunkWireSourceError):
                frontier.exact_declarations(conn, "net.minecraft.game.NoSuchPacket")
            conn.execute(
                "INSERT INTO types VALUES (2, ?, 1)", (frontier.ROOTS[0][1],)
            )
            with self.assertRaises(frontier.ChunkWireSourceError):
                frontier.exact_declarations(conn, frontier.ROOTS[0][1])
            conn.execute("DELETE FROM types WHERE id=2")
            conn.execute("DELETE FROM methods")
            with self.assertRaises(frontier.ChunkWireSourceError):
                frontier.exact_declarations(conn, frontier.ROOTS[0][1])
        finally:
            conn.close()

    def test_external_output_is_fresh_and_never_symlink(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "new-report.json"
            frontier.validate_output(path)
            path.write_text("{}", encoding="utf-8")
            with self.assertRaises(frontier.ChunkWireSourceError):
                frontier.validate_output(path)
            link = Path(tmp) / "link.json"
            link.symlink_to(path)
            with self.assertRaises(frontier.ChunkWireSourceError):
                frontier.validate_output(link)
        with self.assertRaises(frontier.ChunkWireSourceError):
            frontier.validate_output(frontier.REPO_ROOT / "unwritten-source-report.json")


if __name__ == "__main__":
    unittest.main()
