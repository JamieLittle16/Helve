"""Source-review orchestration reuses existing inspectors and never admits R2C."""
from __future__ import annotations

import json
import os
import stat
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import r2c_remaining_source_review_bundle as bundle


class SourceReviewBundleTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory(prefix="helve-r2c-source-review-")
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.source = self.root / "mc-src.zip"
        self.source.write_bytes(b"synthetic source stub: inspectors are mocked")
        self.db = self.root / "atlas.sqlite"
        self.lock = self.root / "lock.toml"
        self.public = self.root / "source-free"
        self.private = self.root / "private"

    @staticmethod
    def fake_biome(argv: list[str]) -> int:
        target = Path(argv[argv.index("--output") + 1])
        target.write_text(json.dumps({
            "schema": 1, "kind": bundle.biome.KIND,
            "target": bundle.TARGET,
            "source_archive_sha256": bundle.biome.SOURCE_SHA256,
            "groups": [{}, {}, {}, {}],
            "source_inspected": False,
            "client_assignment_proven": False,
            "production_admitted": False,
        }))
        return 0

    @staticmethod
    def fake_wire(argv: list[str]) -> int:
        target = Path(argv[argv.index("--output") + 1])
        target.write_text(json.dumps({
            "schema": 1, "kind": bundle.wire.KIND,
            "target": bundle.TARGET,
            "source_archive_sha256": bundle.biome.SOURCE_SHA256,
            "groups": [{}, {}, {}, {}],
            "source_inspected": False,
            "packet_wire_law_proven": False,
            "block_entity_semantics_proven": False,
            "chunk_publication_order_proven": False,
            "production_admitted": False,
        }))
        return 0

    @staticmethod
    def fake_heightmap(*, output: Path, **_: object) -> dict:
        output.write_text(json.dumps({
            "schema": 1, "kind": bundle.heightmap.KIND,
            "target": bundle.TARGET,
            "source_archive_sha256": bundle.biome.SOURCE_SHA256,
            "contains_official_source_text": True,
            "production_admitted": False,
            "independent_source_var_sem_admitted": False,
            "source_inspected": False,
            "delegate_closure_proven": False,
            "files": [
                {"source_text": "SYNTHETIC PRIVATE SOURCE ONLY",
                 "source_inspected": False} for _ in range(4)
            ],
        }))
        return {"production_admitted": False}

    def generate(self) -> dict:
        return bundle.generate(
            source=self.source, db=self.db, lock=self.lock,
            source_free_dir=self.public, private_dir=self.private,
        )

    def test_three_existing_frontiers_and_privacy_boundary(self) -> None:
        with patch.object(bundle.biome, "main", side_effect=self.fake_biome) as biome, \
                patch.object(bundle.wire, "main", side_effect=self.fake_wire) as wire, \
                patch.object(bundle.heightmap, "run",
                             side_effect=self.fake_heightmap) as rich:
            record = self.generate()
        self.assertEqual(biome.call_count, 1)
        self.assertEqual(wire.call_count, 1)
        self.assertEqual(rich.call_count, 1)
        self.assertEqual(record["kind"], bundle.KIND)
        self.assertEqual(len(record["source_free_files"]), 2)
        self.assertFalse(record["source_rich_review_included"])
        self.assertFalse(record["independent_source_var_sem_admitted"])
        self.assertFalse(record["production_chunk_publication_admitted"])
        self.assertFalse(record["client_registry_numeric_id_proven"])
        self.assertFalse(record["heightmap_per_state_source_predicates_proven"])
        self.assertEqual(stat.S_IMODE(self.public.stat().st_mode), 0o700)
        self.assertEqual(stat.S_IMODE(self.private.stat().st_mode), 0o700)
        for summary in record["source_free_files"]:
            f = self.public / summary["file"]
            self.assertEqual(summary["bytes"], f.stat().st_size)
            self.assertEqual(summary["sha256"], bundle._sha(f))
        index = self.public / "source-free-review-index.json"
        self.assertEqual(stat.S_IMODE(index.stat().st_mode), 0o600)
        self.assertEqual(json.loads(index.read_text()), record)
        self.assertNotIn("SYNTHETIC PRIVATE SOURCE ONLY",
                         "\n".join(path.read_text() for path in self.public.iterdir()))
        self.assertNotIn(str(self.private), index.read_text())
        self.assertEqual(len(list(self.private.iterdir())), 1)
        self.assertIn("SYNTHETIC PRIVATE SOURCE ONLY",
                      next(self.private.iterdir()).read_text())

    def test_no_reuse_no_inside_repository_and_no_nested_review_roots(self) -> None:
        already = self.root / "existing"
        already.mkdir()
        with self.assertRaisesRegex(bundle.BundleError, "new"):
            bundle._outside_fresh_directory(already)
        with self.assertRaisesRegex(bundle.BundleError, "outside"):
            bundle._outside_fresh_directory(bundle.REPO / "review-danger")
        with self.assertRaisesRegex(bundle.BundleError, "disjoint"):
            bundle.generate(source=self.source, db=self.db, lock=self.lock,
                            source_free_dir=self.public,
                            private_dir=self.public / "secret")
        link = self.root / "linked-parent"
        link.symlink_to(self.root, target_is_directory=True)
        with self.assertRaisesRegex(bundle.BundleError, "non-symlink"):
            bundle._outside_fresh_directory(link / "new")

    def test_source_free_claims_never_silently_upgrade(self) -> None:
        path = self.root / "unadmitted.json"
        self.fake_biome(["--output", str(path)])
        good = json.loads(path.read_text())
        self.assertEqual(bundle._inventory(
            path, kind=bundle.biome.KIND,
            required_false=("source_inspected", "production_admitted"),
        )["sha256"], bundle._sha(path))
        for mutation in (
            {"source_inspected": True},
            {"production_admitted": True},
            {"source_archive_sha256": "f" * 64},
            {"source_text": "SHOULD NEVER EXPORT"},
            {"groups": [{}]},
        ):
            candidate = {**good, **mutation}
            path.write_text(json.dumps(candidate))
            with self.assertRaises(bundle.BundleError):
                bundle._inventory(
                    path, kind=bundle.biome.KIND,
                    required_false=("source_inspected", "production_admitted"),
                )
        private = self.root / "private-rich.json"
        self.fake_heightmap(output=private)
        rich = json.loads(private.read_text())
        rich["independent_source_var_sem_admitted"] = True
        private.write_text(json.dumps(rich))
        with self.assertRaises(bundle.BundleError):
            bundle._private_source(private)

    def test_empty_body_sha_can_never_be_false_concrete_implementation(self) -> None:
        path = self.root / "old-biome-review.json"
        self.fake_biome(["--output", str(path)])
        data = json.loads(path.read_text())
        abstract = {
            "signature": "getId(T value)",
            "body_sha256": bundle.biome.EMPTY_BODY_SHA256,
            "declaration_only": False,
        }
        data["groups"][0] = {"roots": [{"methods": [abstract]}]}
        path.write_text(json.dumps(data))
        with self.assertRaisesRegex(bundle.BundleError, "empty Atlas body"):
            bundle._inventory(
                path, kind=bundle.biome.KIND,
                required_false=("source_inspected", "production_admitted"),
            )
        abstract["declaration_only"] = True
        path.write_text(json.dumps(data))
        summary = bundle._inventory(
            path, kind=bundle.biome.KIND,
            required_false=("source_inspected", "production_admitted"),
        )
        self.assertEqual(summary["empty_body_sha256_declarations"], 1)
        self.assertEqual(summary["declaration_only_methods"], 1)

    def test_failed_inspector_never_produces_success_manifest(self) -> None:
        with patch.object(bundle.biome, "main", side_effect=self.fake_biome), \
                patch.object(bundle.wire, "main", return_value=2), \
                patch.object(bundle.heightmap, "run") as never:
            with self.assertRaisesRegex(bundle.BundleError, "wire"):
                self.generate()
        never.assert_not_called()
        self.assertFalse((self.public / "source-free-review-index.json").exists())
        self.assertFalse(any(self.private.iterdir()))

    def test_private_source_is_not_accepted_as_source_free(self) -> None:
        path = self.root / "source-rich.json"
        self.fake_heightmap(output=path)
        with self.assertRaises(bundle.BundleError):
            bundle._inventory(path, kind=bundle.biome.KIND,
                              required_false=("production_admitted",))


if __name__ == "__main__":
    unittest.main()
