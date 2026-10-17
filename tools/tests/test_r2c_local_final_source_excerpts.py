"""R2C official-source extraction: hash binding, exact method, no admission."""
from __future__ import annotations

import io
import sqlite3
import sys
import unittest
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import r2c_final_review_focus as focus
import r2c_local_final_source_excerpts as review
from test_r2c_final_review_focus import fixture as producer_fixture


def fake_focus(kind: str = "r2c-26_2-first-pass-source-review-focus-v1") -> dict:
    def sample(roots: tuple[tuple[str, str], ...]) -> list[dict]:
        return [{
            "source": owner + "#" + prefix + "tail",
            "normalized_sha256": "a" * 64,
            "body_sha256": "b" * 64,
            "hazard_leads": [],
            "source_inspected": False,
            "semantics_admitted": False,
        } for owner, prefix in roots]
    return {
        "schema": 1,
        "kind": kind,
        "source_archive_sha256": focus.existing.EXPECTED_SHA,
        "first_pass_only": True,
        "client_biome_ids_admitted": False,
        "heightmap_predicates_admitted": False,
        "outer_wire_admitted": False,
        "production_admitted": False,
        "delegate_closure_proven": False,
        "biome_priority": sample(focus.BIOME),
        "outer_wire_priority": sample(focus.WIRE),
    }


def fake_atlas() -> sqlite3.Connection:
    db = sqlite3.connect(":memory:")
    db.row_factory = sqlite3.Row
    db.executescript("""
        CREATE TABLE source_files(id INTEGER PRIMARY KEY,path TEXT);
        CREATE TABLE types(id INTEGER PRIMARY KEY,qualified_name TEXT,file_id INTEGER);
        CREATE TABLE methods(
            id INTEGER PRIMARY KEY,type_id INTEGER,name TEXT,signature TEXT,
            param_count INTEGER,start_line INTEGER,end_line INTEGER,
            normalized_sha256 TEXT,body_sha256 TEXT
        );
        CREATE TABLE meta(key TEXT PRIMARY KEY,value TEXT);
        CREATE TABLE hazards(method_id INTEGER,kind TEXT);
        CREATE TABLE classifications(method_id INTEGER,label TEXT,source TEXT);
        CREATE TABLE method_calls(
            id INTEGER PRIMARY KEY,caller_method_id INTEGER,
            owner_text TEXT,callee_name TEXT,arg_count INTEGER,
            line INTEGER,resolved_method_id INTEGER
        );
        INSERT INTO meta VALUES ('fingerprint_algorithm','java-token-v2-literal-sensitive');
        INSERT INTO source_files VALUES (1,'src/net/minecraft/Test.java');
        INSERT INTO types VALUES (1,'net.minecraft.core.MappedRegistry',1);
        INSERT INTO methods VALUES (
          1,1,'register','register(final ResourceKey < T > key , final T value)',
          2,1,3,
          'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa',
          'bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb'
        );
    """)
    return db


class LocalSourceReviewTests(unittest.TestCase):
    def test_complete_nonadmitted_19_method_selection(self) -> None:
        for kind in review.ACCEPTED_FOCUS_KINDS:
            with self.subTest(kind=kind):
                entries = review.select_review_entries(fake_focus(kind))
                self.assertEqual(len(entries), 19)
                self.assertEqual([group for group, _ in entries].count("biome_priority"), 10)
                self.assertEqual([group for group, _ in entries].count("outer_wire_priority"), 9)
        changed = fake_focus()
        changed["biome_priority"].pop()
        with self.assertRaisesRegex(review.LocalReviewError, "frozen review roots"):
            review.select_review_entries(changed)
        changed = fake_focus()
        changed["biome_priority"][0]["source"] = "net.minecraft.Old#register("
        with self.assertRaisesRegex(review.LocalReviewError, "unreviewed Atlas root"):
            review.select_review_entries(changed)

    def test_actual_producer_report_is_accepted_without_silent_aliases(self) -> None:
        report = focus.build(*producer_fixture())
        self.assertEqual(report["client_biome_ids_admitted"], False)
        self.assertNotIn("biome_client_ids_admitted", report)
        self.assertEqual(len(review.select_review_entries(report)), 19)

    def test_forged_admission_or_drift_is_rejected(self) -> None:
        for field, value in [
            ("client_biome_ids_admitted", True),
            ("production_admitted", True),
            ("outer_wire_admitted", True),
            ("delegate_closure_proven", True),
            ("source_archive_sha256", "0" * 64),
        ]:
            with self.subTest(field=field):
                changed = fake_focus()
                changed[field] = value
                with self.assertRaises(review.LocalReviewError):
                    review.select_review_entries(changed)
        changed = fake_focus()
        changed["biome_priority"][0]["semantics_admitted"] = True
        with self.assertRaises(review.LocalReviewError):
            review.select_review_entries(changed)
        changed = fake_focus()
        changed["biome_priority"][0]["body_sha256"] = "bad"
        with self.assertRaises(review.LocalReviewError):
            review.select_review_entries(changed)

    def test_exact_fingerprint_and_source_range_before_extraction(self) -> None:
        db = fake_atlas()
        archive_file = io.BytesIO()
        with zipfile.ZipFile(archive_file, "w") as archive:
            archive.writestr(
                "src/net/minecraft/Test.java",
                "class Test {\n  void register() {}\n}\n",
            )
        archive_file.seek(0)
        item = {
            "source": (
                "net.minecraft.core.MappedRegistry#"
                "register(final ResourceKey < T > key , final T value)"
            ),
            "normalized_sha256": "a" * 64,
            "body_sha256": "b" * 64,
            "hazard_leads": [],
        }
        try:
            with zipfile.ZipFile(archive_file) as archive:
                rows = review.read_exact_source(db, archive, [("biome_priority", item)])
                self.assertEqual(len(rows), 1)
                self.assertIn("void register()", rows[0]["source_excerpt"])
                self.assertEqual(rows[0]["source_path"], "src/net/minecraft/Test.java")
                self.assertFalse(rows[0]["source_inspected"])
                self.assertFalse(rows[0]["semantics_admitted"])
                wrong = item | {"body_sha256": "0" * 64}
                with self.assertRaisesRegex(review.LocalReviewError, "fingerprint drift"):
                    review.read_exact_source(db, archive, [("biome_priority", wrong)])
                wrong = item | {"hazard_leads": ["REGISTRY"]}
                with self.assertRaisesRegex(review.LocalReviewError, "fingerprint drift"):
                    review.read_exact_source(db, archive, [("biome_priority", wrong)])
                db.execute("UPDATE methods SET signature='not-the-declaration' WHERE id=1")
                with self.assertRaisesRegex(review.LocalReviewError, "missing or ambiguous"):
                    review.read_exact_source(db, archive, [("biome_priority", item)])
                db.execute("UPDATE methods SET signature=? WHERE id=1",
                           (item["source"].split("#", 1)[1],))
                db.execute(
                    "INSERT INTO methods SELECT 2,type_id,name,signature,param_count,"
                    "start_line,end_line,normalized_sha256,body_sha256 FROM methods WHERE id=1"
                )
                with self.assertRaisesRegex(review.LocalReviewError, "missing or ambiguous"):
                    review.read_exact_source(db, archive, [("biome_priority", item)])
        finally:
            db.close()


if __name__ == "__main__":
    unittest.main()
