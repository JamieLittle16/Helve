#!/usr/bin/env python3
"""Read-only diagnosis of R2C's nine source chunks and saved block entities.

Cold developer inspection, NOT source admission: reuses the existing Python
qualification Anvil/NBT reader. Does not edit the save, mint receipts, bypass
the Rust explicit-empty block-entity gate, or put anything on the Play wire.
"""
from __future__ import annotations

import argparse
import hashlib
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

import vanilla_section_extractor as oracle

# Source: retained selected R2B teleport x=10.390952..., z=-5.815159...
# floor(x/16), floor(z/16) -> (0,-1). R2C first view: sort by squared
# horizontal distance, then chunk X and Z, take the nearest nine.
# Never use this COLD inspection constant to authorize product publication.
PINNED_FIRST_VIEW_CENTER = (0, -1)
INITIAL_CHUNKS = 9
REGION_SIZE_LIMIT = 64 * 1024 * 1024
CHUNK_DECOMPRESSED_LIMIT = 16 * 1024 * 1024


class SourceAuditError(ValueError):
    """A real source could not be read or safely inspected."""


@dataclass(frozen=True)
class ChunkBlockEntityReport:
    x: int
    z: int
    evidence: str
    entries: tuple[tuple[str, object, object, object], ...]
    region_sha256: str


def first_view_positions() -> tuple[tuple[int, int], ...]:
    cx, cz = PINNED_FIRST_VIEW_CENTER
    # Equivalent first nine selected source positions (all radius <= 2).
    positions = [
        (cx + dx, cz + dz)
        for dx in range(-2, 3)
        for dz in range(-2, 3)
    ]
    positions.sort(key=lambda pos: (
        (pos[0] - cx) ** 2 + (pos[1] - cz) ** 2,
        pos[0],
        pos[1],
    ))
    return tuple(positions[:INITIAL_CHUNKS])


def _regular(path: Path, *, maximum: int | None = None) -> Path:
    if path.is_symlink() or not path.is_file():
        raise SourceAuditError(f"required regular, non-symlink source file: {path}")
    if maximum is not None and path.stat().st_size > maximum:
        raise SourceAuditError(f"source file exceeds {maximum} byte cap: {path}")
    return path


def _region_source(world: Path, x: int, z: int) -> Path:
    return world / "dimensions/minecraft/overworld/region" / f"r.{x // 32}.{z // 32}.mca"


def _read_one(
    path: Path,
    region_bytes: bytes,
    locations: list[tuple[int, int]],
    digest: str,
    x: int,
    z: int,
) -> ChunkBlockEntityReport:
    slot = (x % 32) + 32 * (z % 32)
    offset, sectors = locations[slot]
    if offset == 0:
        raise SourceAuditError(f"selected source chunk ({x},{z}) absent in {path}")
    try:
        raw_nbt = oracle._chunk_payload(path, region_bytes, x, z, offset, sectors)
        if len(raw_nbt) > CHUNK_DECOMPRESSED_LIMIT:
            raise SourceAuditError(f"chunk ({x},{z}) exceeds decompressed audit cap")
        root = oracle.parse_nbt(raw_nbt)
        version = oracle._require_int(root.get("DataVersion"), "chunk DataVersion")
        saved_x = oracle._require_int(root.get("xPos"), "chunk xPos")
        saved_z = oracle._require_int(root.get("zPos"), "chunk zPos")
    except oracle.ExtractorError as error:
        raise SourceAuditError(f"source chunk ({x},{z}) invalid: {error}") from error
    if version != oracle.TARGET_DATA_VERSION or (saved_x, saved_z) != (x, z):
        raise SourceAuditError(
            f"chunk ({x},{z}) wrong version/coordinates: DataVersion={version},"
            f" saved=({saved_x},{saved_z}); expected 4903/({x},{z})"
        )
    if "block_entities" not in root:
        return ChunkBlockEntityReport(x, z, "ABSENT (not admitted as empty)", (), digest)
    saved_list = root["block_entities"]
    if not isinstance(saved_list, oracle.NbtListValue):
        raise SourceAuditError(f"chunk ({x},{z}) block_entities is not an NBT list")
    if saved_list.values and saved_list.element_type != 10:
        raise SourceAuditError(f"chunk ({x},{z}) block_entities nonempty list is not compound")
    if not saved_list.values:
        return ChunkBlockEntityReport(x, z, "EXPLICITLY_EMPTY", (), digest)
    entries: list[tuple[str, object, object, object]] = []
    for entity in saved_list.values:
        if not isinstance(entity, dict):
            raise SourceAuditError(f"chunk ({x},{z}) block entity is not a compound")
        # Human-readable evidence only. No client type-ID or NBT serialization
        # is inferred from these strings or source coordinates.
        entries.append((
            str(entity.get("id", "<missing id>")),
            entity.get("x", "<missing x>"),
            entity.get("y", "<missing y>"),
            entity.get("z", "<missing z>"),
        ))
    return ChunkBlockEntityReport(x, z, "NONEMPTY (unsupported)", tuple(entries), digest)


def audit_world(world: Path) -> tuple[ChunkBlockEntityReport, ...]:
    world = world.expanduser().absolute()
    if world.is_symlink() or not world.is_dir():
        raise SourceAuditError(f"not a real, non-symlink world directory: {world}")
    _regular(world / "level.dat", maximum=4 * 1024 * 1024)
    directory = world / "dimensions/minecraft/overworld/region"
    if directory.is_symlink() or not directory.is_dir():
        raise SourceAuditError(f"missing/linked 26.2 namespaced region directory: {directory}")

    cached: dict[Path, tuple[bytes, list[tuple[int, int]], str]] = {}
    reports = []
    for x, z in first_view_positions():
        path = _region_source(world, x, z)
        if path not in cached:
            _regular(path, maximum=REGION_SIZE_LIMIT)
            raw = path.read_bytes()
            if len(raw) < oracle.REGION_HEADER_BYTES or len(raw) % oracle.SECTOR_BYTES:
                raise SourceAuditError(f"region sector shape invalid: {path}")
            try:
                locations = oracle._region_locations(raw, path)
            except oracle.ExtractorError as error:
                raise SourceAuditError(f"invalid region {path}: {error}") from error
            cached[path] = (raw, locations, hashlib.sha256(raw).hexdigest())
        data, locations, digest = cached[path]
        reports.append(_read_one(path, data, locations, digest, x, z))
    return tuple(reports)


def print_report(reports: tuple[ChunkBlockEntityReport, ...]) -> bool:
    print(f"R2C COLD SOURCE AUDIT | nine nearest chunks to {PINNED_FIRST_VIEW_CENTER}")
    ready = True
    for record in reports:
        print(
            f"chunk=({record.x},{record.z}) "
            f"block_entities={record.evidence} count={len(record.entries)} "
            f"region_sha256={record.region_sha256[:16]}..."
        )
        if record.evidence != "EXPLICITLY_EMPTY":
            ready = False
        for kind, x, y, z in record.entries:
            print(f"    saved block entity: id={kind} x={x} y={y} z={z}")
    if ready:
        print("COLD BLOCK-ENTITY PROFILE PASS: nine explicitly empty source lists.")
        print("Other semantic/light/biome/packet admission still checked by the actual Rust path.")
    else:
        print("COLD BLOCK-ENTITY PROFILE NO-GO: do not discard/overwrite any saved entity.")
        print("Use a separate, real vanilla 26.2 save with no block entities in the selected view,")
        print("or implement and source-qualify nonempty block-entity publishing first.")
    print("This is read-only source diagnosis; not a live R2C/VAR/SEM admission.")
    return ready


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Inspect the exact nine 26.2 source chunks for block-entity presence without changing the save"
    )
    parser.add_argument("--world", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        return 0 if print_report(audit_world(args.world)) else 2
    except (OSError, SourceAuditError) as error:
        print(f"R2C COLD SOURCE AUDIT NO-GO: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
