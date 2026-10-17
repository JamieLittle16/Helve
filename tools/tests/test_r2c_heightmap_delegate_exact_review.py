"""Exact official 26.2 heightmap delegate source reader fail-closed tests."""
from __future__ import annotations

import io
import json
import sqlite3
import sys
import tempfile
import unittest
import warnings
import zipfile
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import r2c_heightmap_delegate_exact_review as review
from test_r2c_local_final_source_excerpts import fake_atlas

TEST_ROOT = review.Root(
    "net.minecraft.core.MappedRegistry", "register", 2, True, "synthetic fake Atlas",
)
MISSING_ROOT = review.Root(
    "net.minecraft.core.MappedRegistry", "doesNotExist", 0, False, "optional missing",
)


def source_zip(*, missing: bool = False, duplicate: bool = False) -> bytes:
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as archive:
        if not missing:
            archive.writestr(
                "src/net/minecraft/Test.java",
                "class Test {\n  void register() {}\n}\n",
            )
            if duplicate:
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore", UserWarning)
                    archive.writestr("src/net/minecraft/Test.java", "class Test {}\n")
    return buffer.getvalue()


class DelegateSourceReviewTests(unittest.TestCase):
    def test_exact_method_and_missing_optional(self) -> None:
        conn = fake_atlas()
        try:
            found, missing = review.resolve_roots(conn, (TEST_ROOT, MISSING_ROOT))
            self.assertEqual(len(found), 1)
            self.assertEqual(found[0][1]["name"], "register")
            self.assertEqual([x["method"] for x in missing], ["doesNotExist"])
            with zipfile.ZipFile(io.BytesIO(source_zip())) as archive:
                rows, misses = review.extract(conn, archive, (TEST_ROOT, MISSING_ROOT))
            self.assertEqual(len(rows), 1)
            self.assertEqual(len(misses), 1)
            item = rows[0]
            self.assertIn("void register", item["excerpt"])
            self.assertIn("#register(", item["source_identity"])
            self.assertEqual(len(item["body_sha256"]), 64)
            self.assertEqual(len(item["normalized_sha256"]), 64)
            self.assertFalse(item["delegate_semantics_admitted"])
            self.assertFalse(item["source_inspected"])
        finally:
            conn.close()

    def test_absent_required_ambiguous_overload_duplicate_selector_fail(self) -> None:
        conn = fake_atlas()
        try:
            with self.assertRaisesRegex(review.ReviewError, "required official delegate missing"):
                review.resolve_roots(conn, (
                    review.Root(TEST_ROOT.owner, "doesNotExist", 0, True, "absent"),
                ))
            with self.assertRaisesRegex(review.ReviewError, "duplicate method selector"):
                review.resolve_roots(conn, (TEST_ROOT, TEST_ROOT))
            conn.execute(
                "INSERT INTO methods SELECT 2,type_id,name,signature,param_count,"
                "start_line,end_line,normalized_sha256,body_sha256 FROM methods WHERE id=1"
            )
            with self.assertRaisesRegex(review.ReviewError, "ambiguous Java method overload"):
                review.resolve_roots(conn, (TEST_ROOT,))
        finally:
            conn.close()

    def test_abstract_declaration_recognized_with_atlas_empty_body_hash(self) -> None:
        # Actual Atlas schema stores SHA-256(empty), NOT null, for
        # abstract Java method declarations. A digest alone is not body
        # evidence. Mirror the five-method operator receipt.
        import hashlib

        conn = fake_atlas()
        try:
            conn.execute(
                "UPDATE methods SET body_sha256=? WHERE id=1",
                (hashlib.sha256(b"").hexdigest(),),
            )
            java = b"public abstract int register(final int x);\n"
            buf = io.BytesIO()
            with zipfile.ZipFile(buf, "w") as archive:
                archive.writestr("src/net/minecraft/Test.java", java)
            with zipfile.ZipFile(io.BytesIO(buf.getvalue())) as archive:
                rows, missing = review.extract(conn, archive, (TEST_ROOT,))
            self.assertEqual(missing, [])
            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0]["body_sha256"], hashlib.sha256(b"").hexdigest())
            self.assertIs(rows[0]["has_source_body"], False)
            self.assertEqual(rows[0]["declaration_kind"], "abstract")
            self.assertIs(rows[0]["delegate_semantics_admitted"], False)
        finally:
            conn.close()

    def test_empty_executable_body_and_inconsistent_declarations_fail_closed(self) -> None:
        empty = review.EMPTY_BODY_SHA256
        self.assertTrue(review.has_executable_body(b"void f() {}", empty))
        self.assertFalse(
            review.has_executable_body(b"public abstract int f();", empty)
        )
        with self.assertRaisesRegex(review.ReviewError, "missing Atlas body hash"):
            review.has_executable_body(b"void f() {}", None)
        with self.assertRaisesRegex(review.ReviewError, "without an executable brace"):
            review.has_executable_body(b"public int f();", empty)

    def test_missing_duplicate_zip_members_rejected(self) -> None:
        for scenario in ("missing", "duplicate"):
            with self.subTest(scenario=scenario):
                conn = fake_atlas()
                try:
                    with zipfile.ZipFile(io.BytesIO(source_zip(
                        missing=scenario == "missing", duplicate=scenario == "duplicate"
                    ))) as archive:
                        with self.assertRaisesRegex(review.ReviewError, "archive member"):
                            review.extract(conn, archive, (TEST_ROOT,))
                finally:
                    conn.close()

    def test_run_only_writes_private_nonadmitted_external_file(self) -> None:
        with tempfile.TemporaryDirectory(prefix="helve-r2c-delegate-") as directory:
            root = Path(directory)
            source = root / "official.zip"
            source.write_bytes(source_zip())
            out = root / "review.json"
            with (patch.object(review.vanilla_atlas, "connect_db",
                               side_effect=lambda _: fake_atlas()),
                  patch.object(review.source_probe, "require_pinned_source",
                               return_value=review.oracle.SOURCE_ARCHIVE_SHA256)):
                receipt = review.run(
                    source_zip=source, db=root / "atlas.sqlite",
                    lock=root / "vanilla.lock.toml", output=out,
                    roots=(TEST_ROOT, MISSING_ROOT),
                )
                self.assertEqual(receipt["review_methods"], 1)
                self.assertEqual(receipt["missing_optional_methods"], 1)
                self.assertIs(receipt["source_admitted"], False)
                self.assertEqual(out.stat().st_mode & 0o777, 0o600)
                document = json.loads(out.read_text())
                for flag in (
                    "all_delegate_calls_reviewed", "source_inspected",
                    "heightmap_predicates_source_admitted",
                    "independent_atlas_gate_passed", "production_admitted",
                ):
                    self.assertIs(document[flag], False)
                with self.assertRaises(review.closure.ClosureError):
                    review.run(
                        source_zip=source, db=root / "atlas.sqlite",
                        lock=root / "vanilla.lock.toml", output=out,
                        roots=(TEST_ROOT, MISSING_ROOT),
                    )
                with self.assertRaises(review.closure.ClosureError):
                    review.run(
                        source_zip=source, db=root / "atlas.sqlite",
                        lock=root / "vanilla.lock.toml",
                        output=Path(__file__).parents[1] / "review.json",
                        roots=(TEST_ROOT, MISSING_ROOT),
                    )


if __name__ == "__main__":
    unittest.main()
