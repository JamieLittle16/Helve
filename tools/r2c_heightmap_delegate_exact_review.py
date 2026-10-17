#!/usr/bin/env python3
"""Extract narrowly selected 26.2 heightmap delegate methods from pinned Atlas.

The four top-level heightmap source files are already reviewed. This is the
next *local-only* source-rich inspection for the concrete fluid, AABB, voxel
shape and state-cache delegates they actually invoke. Missing optional
methods are reported, never silently inferred. No method is SEM-admitted.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sqlite3
import sys
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

import official_r2c_heightmap_facts as oracle
import r1b_configuration_source_probe as source_probe
import r2c_world_state_delegate_closure_source_review as closure
import vanilla_atlas

MAX_METHOD_LINES = 420
MAX_MEMBER_BYTES = 4 * 1024 * 1024
MAX_EXCERPT_BYTES = 256 * 1024
KIND = "r2c-26_2-heightmap-predicate-delegate-source-excerpts-v1"


@dataclass(frozen=True)
class Root:
    owner: str
    method: str
    parameters: int
    required: bool
    purpose: str


# Exact owner/name/arity, not textual name searches across the source tree.
# Required roots are direct callees in the already inspected four source
# files. Optional roots expose further concrete implementations/bootstraps;
# a missing optional entry is explicitly recorded as a review gap.
ROOTS = (
    Root("net.minecraft.world.level.material.Fluid", "isEmpty", 0, True, "FluidState.isEmpty owner implementation"),
    Root("net.minecraft.world.phys.shapes.VoxelShape", "bounds", 0, True, "shape bounds for calculateSolid"),
    Root("net.minecraft.world.phys.AABB", "getSize", 0, True, "collision AABB size threshold"),
    Root("net.minecraft.world.phys.AABB", "getYsize", 0, True, "collision AABB vertical threshold"),
    Root("net.minecraft.world.level.material.EmptyFluid", "isEmpty", 0, False, "concrete empty-fluid override"),
    Root("net.minecraft.world.level.material.Fluid", "defaultFluidState", 0, False, "default fluid state identity"),
    Root("net.minecraft.world.level.block.Block", "hasDynamicShape", 0, False, "shape cache eligibility"),
    Root("net.minecraft.world.level.block.Block", "isShapeFullBlock", 1, False, "full shape helper"),
    Root("net.minecraft.world.level.block.Block", "registerDefaultState", 1, False, "block default-state bootstrap"),
    Root("net.minecraft.world.level.block.state.StateDefinition", "getPossibleStates", 0, False, "state enumeration and initCache reachability"),
    Root("net.minecraft.world.phys.shapes.Shapes", "block", 0, False, "default block shape identity"),
    # Narrow follow-up from the independently inspected 11-method report.
    # The first five are named direct callees in that exact official source.
    Root("net.minecraft.world.phys.AABB", "getXsize", 0, True, "getSize arithmetic mean X side"),
    Root("net.minecraft.world.phys.AABB", "getZsize", 0, True, "getSize arithmetic mean Z side"),
    Root("net.minecraft.world.phys.shapes.VoxelShape", "isEmpty", 0, True, "bounds empty-shape guard"),
    Root("net.minecraft.world.phys.shapes.VoxelShape", "min", 1, True, "bounds minimum axis"),
    Root("net.minecraft.world.phys.shapes.VoxelShape", "max", 1, True, "bounds maximum axis"),
    Root("net.minecraft.world.phys.AABB", "AABB", 6, False, "bounds six-scalar constructor"),
    Root("net.minecraft.world.level.material.FlowingFluid", "isEmpty", 0, False, "possible concrete fluid override"),
    # The five direct dispatch edges reached by the 17-method pinned pass.
    # These methods are reviewed once, not recursively guessed via class names.
    Root("net.minecraft.world.phys.shapes.DiscreteVoxelShape", "isEmpty", 0, True, "VoxelShape.isEmpty concrete discrete-shape predicate"),
    Root("net.minecraft.world.phys.shapes.DiscreteVoxelShape", "firstFull", 1, True, "VoxelShape.min occupied lower index"),
    Root("net.minecraft.world.phys.shapes.DiscreteVoxelShape", "lastFull", 1, True, "VoxelShape.max upper occupied index"),
    Root("net.minecraft.world.phys.shapes.DiscreteVoxelShape", "getSize", 1, True, "VoxelShape.min axis discrete size"),
    Root("net.minecraft.world.phys.shapes.VoxelShape", "get", 2, True, "VoxelShape.min/max coordinate lookup"),


)

# Qualify only the newly reached methods when earlier pinned excerpts are already reviewed.
PENDING_DISCRETE_ROOTS = ROOTS[-5:]


class ReviewError(ValueError):
    """A required pinned source/Atlas fact is missing or ambiguous."""


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def resolve_roots(conn: sqlite3.Connection, roots: Sequence[Root] = ROOTS):
    selected: list[tuple[Root, sqlite3.Row]] = []
    missing: list[dict[str, str | int]] = []
    seen: set[str] = set()
    for root in roots:
        key = f"{root.owner}#{root.method}/{root.parameters}"
        if key in seen:
            raise ReviewError(f"duplicate method selector: {key}")
        seen.add(key)
        rows = conn.execute(
            closure._ROW_SELECT
            + " WHERE t.qualified_name=? AND m.name=? AND m.param_count=? ORDER BY m.id",
            (root.owner, root.method, root.parameters),
        ).fetchall()
        if len(rows) > 1:
            raise ReviewError(f"ambiguous Java method overload: {key}")
        if not rows:
            if root.required:
                raise ReviewError(f"required official delegate missing: {key}")
            missing.append({
                "owner": root.owner,
                "method": root.method,
                "parameters": root.parameters,
                "purpose": root.purpose,
            })
            continue
        selected.append((root, rows[0]))
    return selected, missing


def extract(
    conn: sqlite3.Connection,
    archive: zipfile.ZipFile,
    roots: Sequence[Root] = ROOTS,
) -> tuple[list[dict], list[dict]]:
    selected, missing = resolve_roots(conn, roots)
    cache: dict[str, list[str]] = {}
    members = archive.namelist()
    total = 0
    reviewed: list[dict] = []
    for i, (root, row) in enumerate(selected, 1):
        source = source_probe.record_template(conn, row, f"DISC-NET-R2C-HEIGHTMAP-DELEGATE-{i:03d}")
        evidence = source["source"]
        if (evidence["type"] != root.owner
                or evidence["signature"] != row["signature"]
                or evidence["fingerprint_algorithm"] != vanilla_atlas.FINGERPRINT_ALGORITHM
                or not isinstance(evidence["normalized_sha256"], str)
                or len(evidence["normalized_sha256"]) != 64
                or (evidence["body_sha256"] is not None
                    and (not isinstance(evidence["body_sha256"], str)
                         or len(evidence["body_sha256"]) != 64))):
            raise ReviewError(f"Atlas declaration/fingerprint invalid: {root.owner}#{root.method}")
        path = closure._safe_member(row["path"])
        if members.count(path) != 1:
            raise ReviewError(f"missing or duplicate Java archive member: {path}")
        info = archive.getinfo(path)
        if not 0 < info.file_size <= MAX_MEMBER_BYTES:
            raise ReviewError(f"Java source member outside byte bound: {path}")
        excerpt = closure._source_excerpt(archive, row, max_lines=MAX_METHOD_LINES, cache=cache)
        total += len(excerpt)
        if total > MAX_EXCERPT_BYTES:
            raise ReviewError("heightmap delegate excerpts exceed frozen size cap")
        reviewed.append({
            "owner": root.owner,
            "method": root.method,
            "parameters": root.parameters,
            "purpose": root.purpose,
            "source_identity": f"{root.owner}#{row['signature']}",
            "normalized_sha256": evidence["normalized_sha256"],
            "body_sha256": evidence["body_sha256"],
            "has_source_body": evidence["body_sha256"] is not None,
            "atlas_hazards": source["atlas_observed_hazards"],
            "source_path": path,
            "start_line": int(row["start_line"]),
            "end_line": int(row["end_line"]),
            "excerpt": excerpt.decode("utf-8", errors="strict"),
            "excerpt_sha256": digest(excerpt),
            "calls": closure._call_inventory(conn, int(row["id"])),
            "source_inspected": False,
            "delegate_semantics_admitted": False,
        })
    return reviewed, missing


def run(*, source_zip: Path, db: Path, lock: Path, output: Path,
        roots: Sequence[Root] = ROOTS) -> dict:
    external = closure._external_output(output)
    conn = vanilla_atlas.connect_db(db)
    try:
        identity = source_probe.require_pinned_source(conn, source_zip, lock)
        if identity != oracle.SOURCE_ARCHIVE_SHA256:
            raise ReviewError("wrong official 26.2 source identity")
        with zipfile.ZipFile(source_zip) as archive:
            reviewed, missing = extract(conn, archive, roots)
    finally:
        conn.close()
    if not reviewed:
        raise ReviewError("no heightmap delegates extracted")
    result = {
        "schema": 1,
        "kind": KIND,
        "source_archive_sha256": identity,
        "commit_policy": "PRIVATE_EPHEMERAL_SOURCE_RICH_DO_NOT_COMMIT",
        "contains_official_source_text": True,
        "review_methods": reviewed,
        "missing_optional_methods": missing,
        "method_count": len(reviewed),
        "selection_scope": "pending-discrete" if tuple(roots) == PENDING_DISCRETE_ROOTS else "all",
        "selected_root_count": len(roots),
        "all_delegate_calls_reviewed": False,
        "source_inspected": False,
        "heightmap_predicates_source_admitted": False,
        "independent_atlas_gate_passed": False,
        "production_admitted": False,
    }
    data = (json.dumps(result, sort_keys=True, indent=2, ensure_ascii=False) + "\n").encode()
    external.parent.mkdir(parents=True, exist_ok=True)
    fd = os.open(external, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    with os.fdopen(fd, "wb") as writer:
        writer.write(data)
    return {
        "output": str(external), "review_methods": len(reviewed),
        "missing_optional_methods": len(missing),
        "source_admitted": False,
    }


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=closure.DEFAULT_SOURCE)
    parser.add_argument("--db", type=Path, default=closure.DEFAULT_DB)
    parser.add_argument("--lock", type=Path, default=closure.DEFAULT_LOCK)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument(
        "--pending-only", action="store_true",
        help="export only five newly reached DiscreteVoxelShape/VoxelShape methods",
    )
    args = parser.parse_args(argv)
    try:
        report = run(source_zip=args.source, db=args.db, lock=args.lock, output=args.output,
                     roots=PENDING_DISCRETE_ROOTS if args.pending_only else ROOTS)
    except (ReviewError, closure.ClosureError, ValueError, TypeError, OSError,
            sqlite3.Error, zipfile.BadZipFile) as error:
        print(f"R2C heightmap delegate review rejected: {error}", file=sys.stderr)
        return 2
    print(json.dumps(report, sort_keys=True))
    print("Source excerpts are local-only and have not passed independent VAR/SEM")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
