#!/usr/bin/env python3
"""Run the two remaining pinned official-source frontier inventories in parallel.

This produces source-free *review inputs only*. Running a source inventory,
even twice, never grants VAR/SEM, client numeric IDs or chunk publication.
Only separately inspected human decisions and an independent Atlas gate can
establish admission. The 32,366-state heightmap runtime oracle runs in its
existing separate official Java workflow.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXPECTED_SHA = "1e9bca3dff83cd83e7905f8810f1ec9899361fa2dc83fe893bb48beeb04df750"
TARGET = {"minecraft": "26.2", "protocol": 776, "data_version": 4903}
JOBS = {
    "biome_client_ids": (
        "r2c_biome_id_source_frontier.py",
        "biome-client-id-source-inventory.json",
    ),
    "chunk_wire": (
        "r2c_chunk_wire_source_frontier.py",
        "chunk-wire-source-inventory.json",
    ),
}


def sha256(path: Path) -> str:
    checksum = hashlib.sha256()
    with path.open("rb") as data:
        while block := data.read(1 << 20):
            checksum.update(block)
    return checksum.hexdigest()


def check_one(label: str, path: Path) -> dict:
    if path.is_symlink() or not path.is_file():
        raise ValueError(f"{label}: report missing or symlinked")
    raw = path.read_bytes()
    if not 0 < len(raw) < 5_000_000:
        raise ValueError(f"{label}: report byte count outside finite bound")
    obj = json.loads(raw)
    if not isinstance(obj, dict) or obj.get("schema") != 1:
        raise ValueError(f"{label}: unsupported report schema")
    if obj.get("target") != TARGET or obj.get("source_archive_sha256") != EXPECTED_SHA:
        raise ValueError(f"{label}: report source/target does not match 26.2 pin")
    if obj.get("source_inspected") is not False or obj.get("production_admitted") is not False:
        raise ValueError(f"{label}: source discovery cannot claim source admission")
    if label == "biome_client_ids":
        if (obj.get("client_assignment_proven") is not False
            or not isinstance(obj.get("groups"), list)
            or len(obj["groups"]) != 4):
            raise ValueError("biome numeric ID candidate boundaries drifted")
    if label == "chunk_wire":
        if (obj.get("packet_wire_law_proven") is not False
            or obj.get("block_entity_semantics_proven") is not False
            or obj.get("chunk_publication_order_proven") is not False
            or not isinstance(obj.get("groups"), list)
            or len(obj["groups"]) != 4):
            raise ValueError("outer chunk wire candidate boundaries drifted")
    return {"filename": path.name, "bytes": len(raw),
            "sha256": hashlib.sha256(raw).hexdigest(),
            "method_group_count": len(obj["groups"]),
            "source_inspected": False, "production_admitted": False}


def run_one(label: str, script: str, path: Path, source: Path,
            db: Path, lock: Path) -> None:
    result = subprocess.run(
        [sys.executable, str(ROOT / "tools" / script),
         "--source", str(source), "--db", str(db),
         "--lock", str(lock), "--output", str(path)],
        capture_output=True, text=True, check=False, timeout=180,
    )
    if result.returncode:
        # Never forward arbitrary subprocess output derived from a local
        # proprietary official-source scan. Preserve only the failing label.
        raise ValueError(f"{label}: pinned source inventory failed closed "
                         f"(exit {result.returncode})")


def prepare(source: Path, db: Path, lock: Path, output_dir: Path) -> dict:
    if not source.is_file() or source.is_symlink() or sha256(source) != EXPECTED_SHA:
        raise ValueError("official source archive identity mismatch")
    if not db.is_file() or db.is_symlink() or not lock.is_file() or lock.is_symlink():
        raise ValueError("pinned local Atlas/lock must be real files")
    if output_dir.exists() or output_dir.is_symlink():
        raise ValueError("source-free output directory must not exist")
    if output_dir.resolve(strict=False).is_relative_to(ROOT.resolve()):
        raise ValueError("source review reports must stay outside the repository")
    parent = output_dir.parent
    if not parent.is_dir() or parent.is_symlink():
        raise ValueError("source report parent must be an existing non-symlink directory")
    with tempfile.TemporaryDirectory(prefix="helve-r2c-both-frontiers-", dir=parent) as scratch:
        staging = Path(scratch)
        with ThreadPoolExecutor(max_workers=2) as pool:
            work = [
                pool.submit(run_one, label, script, staging / filename,
                            source, db, lock)
                for label, (script, filename) in JOBS.items()
            ]
            for future in work:
                future.result()
        reports = {
            label: check_one(label, staging / filename)
            for label, (_, filename) in JOBS.items()
        }
        report = {
            "schema": 1,
            "kind": "r2c-26_2-parallel-source-frontier-handoff-v1",
            "target": TARGET, "source_archive_sha256": EXPECTED_SHA,
            "inventories": reports, "completed_in_parallel": True,
            "independent_human_source_review_complete": False,
            "independent_atlas_gate_passed": False,
            "heightmap_per_state_source_semantics_admitted": False,
            "client_biome_ids_admitted": False,
            "chunk_wire_admitted": False,
            "live_world_publication_admitted": False,
        }
        (staging / "review-frontier-manifest.json").write_text(
            json.dumps(report, indent=2, sort_keys=True) + "\n"
        )
        staging.rename(output_dir)
        return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--db", type=Path, required=True)
    parser.add_argument("--lock", type=Path, default=ROOT / "vanilla/vanilla.lock.toml")
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    try:
        result = prepare(args.source, args.db, args.lock, args.output_dir)
    except (ValueError, OSError, TypeError, json.JSONDecodeError,
            subprocess.TimeoutExpired) as error:
        print(f"R2C parallel source review preparation blocked: {error}", file=sys.stderr)
        return 2
    print(f"Two source-free R2C frontier inventories: {args.output_dir}")
    print("Source review, VAR/SEM, independent Atlas gate, production admission: ALL STILL REQUIRED")
    assert result["live_world_publication_admitted"] is False
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
