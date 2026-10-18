#!/usr/bin/env python3
"""Gather existing pinned R2C source-review frontiers without admitting them.

Two *source-free* inventories are kept separately from a private source-rich
heightmap review. No alternate Atlas/Java parser, VAR/SEM approval, automatic
source interpretation or production publication authority is introduced.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from pathlib import Path
from typing import Sequence

import r2c_biome_id_source_frontier as biome
import r2c_chunk_wire_source_frontier as wire
import r2c_heightmap_predicate_source_review as heightmap

REPO = Path(__file__).resolve().parents[1]
KIND = "r2c-26_2-remaining-source-review-bundle-v1"
TARGET = {"minecraft": "26.2", "protocol": 776, "data_version": 4903}


class BundleError(ValueError):
    """A pinned review input, output boundary or readiness claim failed."""


def _outside_fresh_directory(path: Path) -> Path:
    path = path.expanduser().absolute()
    if path.exists() or path.is_symlink():
        raise BundleError("review output directory must be new; no overwrites")
    parent = path.parent
    if not parent.is_dir() or any(part.is_symlink() for part in (parent, *parent.parents)):
        raise BundleError("review output parent must be a real existing non-symlink directory")
    if path.resolve(strict=False).is_relative_to(REPO.resolve()):
        raise BundleError("review output must stay outside the repository")
    return path


def _sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for piece in iter(lambda: stream.read(128 * 1024), b""):
            h.update(piece)
    return h.hexdigest()


def _inventory(path: Path, *, kind: str, required_false: tuple[str, ...]) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or data.get("schema") != 1:
        raise BundleError("source-free inventory schema drifted")
    if data.get("kind") != kind or data.get("target") != TARGET:
        raise BundleError("source-free inventory kind/target drifted")
    if data.get("source_archive_sha256") != biome.SOURCE_SHA256:
        raise BundleError("source-free inventory pinned source drifted")
    if any(data.get(name) is not False for name in required_false):
        raise BundleError("source-free inventory must not claim reviewed/admitted semantics")
    if not isinstance(data.get("groups"), list) or len(data["groups"]) != 4:
        raise BundleError("source-free inventory must include all four review groups")
    encoded = json.dumps(data, ensure_ascii=True)
    if '"source_text"' in encoded or '"contains_official_source_text": true' in encoded:
        raise BundleError("source-free inventory unexpectedly contains official source")
    return {"file": path.name, "bytes": path.stat().st_size, "sha256": _sha(path)}


def _private_source(path: Path) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    if (not isinstance(data, dict) or data.get("schema") != 1
        or data.get("kind") != heightmap.KIND
        or data.get("target") != TARGET
        or data.get("source_archive_sha256") != biome.SOURCE_SHA256
        or data.get("contains_official_source_text") is not True
        or data.get("production_admitted") is not False
        or data.get("independent_source_var_sem_admitted") is not False
        or data.get("source_inspected") is not False
        or data.get("delegate_closure_proven") is not False
        or not isinstance(data.get("files"), list) or len(data["files"]) != 4):
        raise BundleError("private pinned heightmap review shape/status drifted")
    for entry in data["files"]:
        if (not isinstance(entry, dict)
            or not isinstance(entry.get("source_text"), str)
            or not entry["source_text"]
            or entry.get("source_inspected") is not False):
            raise BundleError("private heightmap review text/flags incomplete")
    return {"source_rich_file_created_privately": True,
            "source_rich_bytes": path.stat().st_size,
            "source_rich_sha256": _sha(path),
            "source_text_in_source_free_bundle": False}


def generate(*, source: Path, db: Path, lock: Path,
             source_free_dir: Path, private_dir: Path) -> dict:
    """Run the *existing* 3 pinned inspections, then write a nonadmitted index."""
    public = source_free_dir.expanduser().absolute()
    private = private_dir.expanduser().absolute()
    public_resolved = public.resolve(strict=False)
    private_resolved = private.resolve(strict=False)
    if (public_resolved.is_relative_to(private_resolved)
        or private_resolved.is_relative_to(public_resolved)):
        raise BundleError("source-free and private review roots must be disjoint")
    public = _outside_fresh_directory(public)
    private = _outside_fresh_directory(private)
    public.mkdir(mode=0o700)
    private.mkdir(mode=0o700)
    common = ["--source", str(source), "--db", str(db), "--lock", str(lock)]
    biome_path = public / "biome-id-declarations.json"
    wire_path = public / "chunk-wire-declarations.json"
    heightmap_path = private / "heightmap-source-PRIVATE-DO-NOT-SHARE.json"

    if biome.main([*common, "--output", str(biome_path)]) != 0:
        raise BundleError("existing biome-ID source frontier rejected")
    if wire.main([*common, "--output", str(wire_path)]) != 0:
        raise BundleError("existing chunk-wire source frontier rejected")
    heightmap.run(source_archive=source, atlas=db, lock=lock, output=heightmap_path)

    summaries = [
        _inventory(biome_path, kind=biome.KIND,
                   required_false=("source_inspected", "client_assignment_proven",
                                   "production_admitted")),
        _inventory(wire_path, kind=wire.KIND,
                   required_false=("source_inspected", "packet_wire_law_proven",
                                   "block_entity_semantics_proven",
                                   "chunk_publication_order_proven", "production_admitted")),
    ]
    private_summary = _private_source(heightmap_path)
    report = {
        "schema": 1, "kind": KIND, "target": TARGET,
        "source_archive_sha256": biome.SOURCE_SHA256,
        "source_free_files": summaries,
        "private_source_review": private_summary,
        "operator_semantic_source_review_complete": False,
        "independent_source_var_sem_admitted": False,
        "production_chunk_publication_admitted": False,
        "client_registry_numeric_id_proven": False,
        "heightmap_per_state_source_predicates_proven": False,
        "outer_chunk_play_lifecycle_source_proven": False,
        "remaining_review": [
            "review exact ordered client Configuration registry registration and error paths",
            "close heightmap blocksMotion collision-cache delegate and exact state predicates",
            "review outer chunk/light packet and PlayerChunkSender/ACK lifecycle VAR/SEM",
            "independently source-gate all selected profile/known-pack/registry decisions",
        ],
        "source_rich_review_included": False,
        "previous_world_state_58_method_admission_unchanged": True,
    }
    manifest = public / "source-free-review-index.json"
    payload = (json.dumps(report, indent=2, sort_keys=True) + "\n").encode()
    fd = os.open(manifest, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, "wb") as stream:
        stream.write(payload)
    return report


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--db", type=Path, required=True)
    parser.add_argument("--lock", type=Path, default=REPO / "vanilla/vanilla.lock.toml")
    parser.add_argument("--source-free-dir", type=Path, required=True)
    parser.add_argument("--private-dir", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        generate(source=args.source, db=args.db, lock=args.lock,
                 source_free_dir=args.source_free_dir, private_dir=args.private_dir)
    except (BundleError, ValueError, OSError, TypeError, json.JSONDecodeError,
            heightmap.HeightmapReviewError) as error:
        print(f"R2C remaining-source review FAILED CLOSED: {error}", file=sys.stderr)
        return 2
    print("R2C bounded source review frontiers prepared separately; "
          "human VAR/SEM, client and production source admission remain OPEN")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
