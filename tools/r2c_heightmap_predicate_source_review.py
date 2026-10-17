#!/usr/bin/env python3
"""Read the four *exact* pinned official 26.2 heightmap predicate source files locally.

This creates only a private external, source-RICH review artifact, not a VAR/SEM
decision, independent source gate, generated fact table or production authority.
In particular this does not infer blocksMotion from non-air/mutation flags.
Reuse the existing locked Vanilla Atlas source preflight and the established
official heightmap source-file SHA commitments; do not parse Java again.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sqlite3
import sys
import zipfile
from pathlib import Path
from typing import Mapping, Sequence

import official_r2c_heightmap_facts as oracle
import r1b_configuration_source_probe as source_probe
import r2c_world_state_delegate_closure_source_review as existing
import vanilla_atlas

KIND = "r2c-26_2-heightmap-source-four-file-local-review-v1"
MAX_SINGLE_JAVA_BYTES = 512 * 1024
MAX_TOTAL_JAVA_BYTES = 1024 * 1024
SOURCE_ROOT = "src/net/minecraft/"
# Narrow four-file source surface, not the entire official server source.
# The official oracle already retains these *original-file* SHA-256 values,
# which are independent of Atlas normalized token/method fingerprints.
SOURCES = {
    "Heightmap.java": "world/level/levelgen/Heightmap.java",
    "BlockBehaviour.java": "world/level/block/state/BlockBehaviour.java",
    "FluidState.java": "world/level/material/FluidState.java",
    "LeavesBlock.java": "world/level/block/LeavesBlock.java",
}


class HeightmapReviewError(ValueError):
    """Official source identity, file bound or source separation rejected."""


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_predicate_sources(
    archive: zipfile.ZipFile,
    *,
    expected_raw_sha: Mapping[str, str] | None = None,
) -> list[dict[str, object]]:
    """Fail atomically on any missing/duplicate/drifted exact source member."""
    expected = oracle.SOURCE_FILE_SHA256 if expected_raw_sha is None else expected_raw_sha
    if set(expected) != set(SOURCES):
        raise HeightmapReviewError("heightmap review surface does not match four pinned files")
    members = archive.namelist()
    selected: list[dict[str, object]] = []
    total_bytes = 0
    for file_name, suffix in SOURCES.items():
        path = SOURCE_ROOT + suffix
        if members.count(path) != 1:
            raise HeightmapReviewError(f"missing/ambiguous pinned heightmap member: {path}")
        info = archive.getinfo(path)
        if not 0 < info.file_size <= MAX_SINGLE_JAVA_BYTES:
            raise HeightmapReviewError(f"invalid official Java file size: {path}")
        total_bytes += info.file_size
        if total_bytes > MAX_TOTAL_JAVA_BYTES:
            raise HeightmapReviewError("four-file official source review exceeds global byte cap")
        body = archive.read(info)
        if len(body) != info.file_size:
            raise HeightmapReviewError(f"source ZIP member truncated: {path}")
        actual = sha256_bytes(body)
        if actual != expected[file_name]:
            raise HeightmapReviewError(f"official source file SHA-256 drift: {path}")
        try:
            text = body.decode("utf-8", errors="strict")
        except UnicodeDecodeError as error:
            raise HeightmapReviewError(f"official Java file not UTF-8: {path}") from error
        selected.append({
            "file": file_name,
            "path": path,
            "raw_sha256": actual,
            "raw_bytes": len(body),
            "source_text": text,
            "source_inspected": False,
            "semantic_predicates_admitted": False,
        })
    return selected


def run(
    *,
    source_archive: Path,
    atlas: Path,
    lock: Path,
    output: Path,
) -> dict[str, object]:
    # Existing helper forbids placing official-source bytes in the repo,
    # and requires a fresh output path outside its tree.
    external = existing._external_output(output)
    conn = vanilla_atlas.connect_db(atlas)
    try:
        source_sha = source_probe.require_pinned_source(conn, source_archive, lock)
        if source_sha != oracle.SOURCE_ARCHIVE_SHA256:
            raise HeightmapReviewError("official 26.2 source identity drift")
        with zipfile.ZipFile(source_archive) as archive:
            sources = read_predicate_sources(archive)
    finally:
        conn.close()

    result = {
        "schema": 1,
        "kind": KIND,
        "source_archive_sha256": source_sha,
        "target": {"minecraft": "26.2", "protocol": 776, "data_version": 4903},
        "commit_policy": "SOURCE_RICH_LOCAL_REVIEW_DO_NOT_COMMIT",
        "contains_official_source_text": True,
        "source_inspected": False,
        "delegate_closure_proven": False,
        "independent_source_var_sem_admitted": False,
        "heightmap_per_state_semantics_admitted": False,
        "production_admitted": False,
        "official_runtime_state_count": oracle.EXPECTED_STATE_COUNT,
        "files": sources,
    }
    data = (json.dumps(result, indent=2, sort_keys=True, ensure_ascii=False) + "\n").encode("utf-8")
    external.parent.mkdir(parents=True, exist_ok=True)
    fd = os.open(external, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, "wb") as stream:
        stream.write(data)
    return {
        "output": str(external),
        "files": len(sources),
        "java_source_bytes": sum(int(item["raw_bytes"]) for item in sources),
        "output_sha256": sha256_bytes(data),
        "production_admitted": False,
    }


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=existing.DEFAULT_SOURCE)
    parser.add_argument("--db", type=Path, default=existing.DEFAULT_DB)
    parser.add_argument("--lock", type=Path, default=existing.DEFAULT_LOCK)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        summary = run(
            source_archive=args.source, atlas=args.db, lock=args.lock, output=args.output
        )
    except (HeightmapReviewError, existing.ClosureError, ValueError, TypeError,
            OSError, sqlite3.Error, zipfile.BadZipFile) as error:
        print(f"R2C heightmap pinned-source review rejected: {error}", file=sys.stderr)
        return 2
    print(json.dumps(summary, sort_keys=True))
    print("Source text LOCAL ONLY; predicate delegates / VAR/SEM remain unadmitted")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
