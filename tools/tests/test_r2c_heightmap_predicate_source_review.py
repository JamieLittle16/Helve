"""Exact local heightmap source review must match all four official file digests."""
from __future__ import annotations

import hashlib
import io
import json
import os
import sqlite3
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import r2c_heightmap_predicate_source_review as review


def fixture() -> tuple[bytes, dict[str, str], dict[str, bytes]]:
    # Intentionally synthetic; NEVER embed/commit any Mojang Java source.
    members = {
        name: (f"/* synthetic {name} */\nclass Test {{}}\n").encode()
        for name in review.SOURCES
    }
    digests = {name: hashlib.sha256(raw).hexdigest()
               for name, raw in members.items()}
    stream = io.BytesIO()
    with zipfile.ZipFile(stream, "w") as archive:
        for name, raw in members.items():
            archive.writestr(review.SOURCE_ROOT + review.SOURCES[name], raw)
    return stream.getvalue(), digests, members


class PinnedPredicateReviewTests(unittest.TestCase):
    def test_exact_four_files_and_source_free_nonadmission(self) -> None:
        raw, digests, original = fixture()
        with zipfile.ZipFile(io.BytesIO(raw)) as archive:
            result = review.read_predicate_sources(archive, expected_raw_sha=digests)
        self.assertEqual([item["file"] for item in result], list(review.SOURCES))
        self.assertEqual(len(result), 4)
        for item in result:
            self.assertEqual(
                item["source_text"],
                original[item["file"]].decode("utf-8"),
            )
            self.assertFalse(item["source_inspected"])
            self.assertFalse(item["semantic_predicates_admitted"])

    def test_fingerprint_drift_and_wrong_surface_fail_closed(self) -> None:
        raw, digests, _ = fixture()
        with zipfile.ZipFile(io.BytesIO(raw)) as archive:
            changed = digests | {"Heightmap.java": "0" * 64}
            with self.assertRaisesRegex(review.HeightmapReviewError, "SHA-256 drift"):
                review.read_predicate_sources(archive, expected_raw_sha=changed)
            with self.assertRaisesRegex(review.HeightmapReviewError, "four pinned files"):
                review.read_predicate_sources(
                    archive, expected_raw_sha={"Heightmap.java": "0" * 64}
                )

    def test_missing_ambiguous_and_invalid_utf8_fail_closed(self) -> None:
        _, digests, source = fixture()
        for scenario in ("missing", "ambiguous", "non_utf8"):
            with self.subTest(scenario=scenario):
                output = io.BytesIO()
                with zipfile.ZipFile(output, "w") as archive:
                    for name, raw in source.items():
                        if scenario == "missing" and name == "FluidState.java":
                            continue
                        if scenario == "non_utf8" and name == "FluidState.java":
                            raw = b"\xff\xfe"
                        member = review.SOURCE_ROOT + review.SOURCES[name]
                        archive.writestr(member, raw)
                        if scenario == "ambiguous" and name == "Heightmap.java":
                            # ZIP permits duplicates, which must not be resolved silently.
                            import warnings
                            with warnings.catch_warnings():
                                warnings.simplefilter("ignore", UserWarning)
                                archive.writestr(member, raw)
                output.seek(0)
                with zipfile.ZipFile(output) as archive:
                    fingerprints = digests
                    if scenario == "non_utf8":
                        fingerprints = digests | {
                            "FluidState.java": hashlib.sha256(b"\xff\xfe").hexdigest()
                        }
                    with self.assertRaises(review.HeightmapReviewError):
                        review.read_predicate_sources(
                            archive, expected_raw_sha=fingerprints
                        )

    def test_bounded_complete_external_private_output(self) -> None:
        raw, digests, _ = fixture()
        with tempfile.TemporaryDirectory(prefix="helve-r2c-heightmap-review-") as temp:
            root = Path(temp)
            source = root / "official.zip"
            source.write_bytes(raw)
            output = root / "private-review.json"
            with (patch.object(review.vanilla_atlas, "connect_db",
                               side_effect=lambda _: sqlite3.connect(":memory:")),
                  patch.object(review.source_probe, "require_pinned_source",
                               return_value=review.oracle.SOURCE_ARCHIVE_SHA256),
                  patch.object(review.oracle, "SOURCE_FILE_SHA256", digests)):
                summary = review.run(
                    source_archive=source, atlas=root / "atlas.sqlite",
                    lock=root / "lock.toml", output=output,
                )
                self.assertEqual(summary["files"], 4)
                self.assertFalse(summary["production_admitted"])
                result = json.loads(output.read_text(encoding="utf-8"))
                self.assertEqual(result["kind"], review.KIND)
                self.assertTrue(result["contains_official_source_text"])
                self.assertEqual(result["official_runtime_state_count"], 32_366)
                for flag in (
                    "source_inspected",
                    "delegate_closure_proven",
                    "independent_source_var_sem_admitted",
                    "heightmap_per_state_semantics_admitted",
                    "production_admitted",
                ):
                    self.assertIs(result[flag], False)
                self.assertEqual(output.stat().st_mode & 0o777, 0o600)
                with self.assertRaises(review.existing.ClosureError):
                    review.run(
                        source_archive=source, atlas=root / "atlas.sqlite",
                        lock=root / "lock.toml", output=Path(__file__).parent / "source.json",
                    )
                with self.assertRaises(review.HeightmapReviewError):
                    # File present must be rejected before source reads.
                    review.run(
                        source_archive=source, atlas=root / "atlas.sqlite",
                        lock=root / "lock.toml", output=output,
                    )


if __name__ == "__main__":
    unittest.main()
