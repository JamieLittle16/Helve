#!/usr/bin/env python3
"""Convert an exact pinned 26.2 runtime *candidate* to a dense COLD byte table.

This DOES NOT qualify source semantics or emit a production table. Only the
official probe's pinned identity, four-bit layout, count and fail-closed
candidate status are accepted. The Rust adapter independently checks the
generated mutation facts for all 32,366 state IDs.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys
import tomllib

import official_r2c_heightmap_facts as official

EXPECTED_TARGET = {"minecraft": "26.2", "protocol": 776, "data_version": 4903}
EXPECTED_BITS = {
    "non_air": 0,
    "blocks_motion": 1,
    "fluid_non_empty": 2,
    "leaves": 3,
}
EXPECTED_LAWS = {
    "WORLD_SURFACE": "non_air",
    "MOTION_BLOCKING": "blocks_motion || fluid_non_empty",
    "MOTION_BLOCKING_NO_LEAVES":
        "(blocks_motion || fluid_non_empty) && !leaves",
}

def validate_candidate(document: dict, lock: dict) -> bytes:
    if document.get("schema") != 1 or document.get("target") != EXPECTED_TARGET:
        raise ValueError("wrong R2C heightmap target/schema")
    if document.get("server_sha256") != lock["runtime"]["server_sha256"]:
        raise ValueError("official runtime pin mismatch")
    if document.get("source_archive_sha256") != lock["source"]["archive_sha256"]:
        raise ValueError("official source archive pin mismatch")
    if document.get("source_archive_sha256") != official.SOURCE_ARCHIVE_SHA256:
        raise ValueError("heightmap inspector and source lock disagree")
    if document.get("source_file_sha256") != official.SOURCE_FILE_SHA256:
        raise ValueError("heightmap source-review surface mismatch")
    if document.get("bit_layout") != EXPECTED_BITS:
        raise ValueError("unsupported heightmap candidate bit layout")
    if document.get("heightmap_laws") != EXPECTED_LAWS:
        raise ValueError("unsupported 26.2 heightmap predicate laws")
    if document.get("source_admitted") is not False:
        raise ValueError("candidate MUST remain independently source-unadmitted")
    if document.get("production_admitted") is not False:
        raise ValueError("candidate MUST remain production-unadmitted")
    if document.get("gate") != (
        "R2C-HEIGHTMAP-STATE-PREDICATES source fingerprint and independent SEM admission"
    ):
        raise ValueError("candidate source gate was bypassed or changed")
    if document.get("state_count") != official.EXPECTED_STATE_COUNT:
        raise ValueError("official runtime state count mismatch")

    records = document.get("flags_by_vanilla_state_id")
    if not isinstance(records, list) or len(records) != official.EXPECTED_STATE_COUNT:
        raise ValueError("candidate state table is absent or truncated")
    for index, flags in enumerate(records):
        if type(flags) is not int or not (0 <= flags < 16):
            raise ValueError(f"invalid 4-bit state fact at official ID {index}")
        if flags & 0b1001 and not flags & 1:
            raise ValueError(f"leaf/non-air inconsistency at official ID {index}")
        if flags & 0b0010 and not flags & 1:
            raise ValueError(f"motion/air inconsistency at official ID {index}")
    return bytes(records)

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--lock", default=Path("vanilla/vanilla.lock.toml"), type=Path)
    args = parser.parse_args()
    try:
        with args.lock.open("rb") as stream:
            lock = tomllib.load(stream)
        document = json.loads(args.input.read_text(encoding="utf-8"))
        flags = validate_candidate(document, lock)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_bytes(flags)
        print(
            f"R2C official *candidate* only: {len(flags)} bytes, "
            f"sha256={hashlib.sha256(flags).hexdigest()}; "
            "NO production source admission"
        )
        return 0
    except (OSError, KeyError, ValueError, json.JSONDecodeError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 2

if __name__ == "__main__":
    raise SystemExit(main())
