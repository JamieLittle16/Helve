#!/usr/bin/env python3
"""Freeze exact stock Java 26.2 NoiseChunk 4x8x4 complete-cell rawbit oracle.

Four original world seeds by 128 voxel points, one original NoiseChunk cell,
experimental Y/X/Z traversal (NOT certified stock chunk emplacement order).
This certifies genuine *reference values*, not a Rust implementation, complete
chunk production, neighbouring-cell interpolation or VAR/SEM admission.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

import worldgen_26_2_stock_noisechunk_complete_cell_capture as complete
import worldgen_26_2_stock_noisechunk_cell_fixture as previous

ROOT=Path(__file__).resolve().parents[1]
FIXTURE=ROOT/"vanilla/reports/worldgen-26_2-stock-noisechunk-complete-cell-512-bits.txt"
FIXTURE_BYTES=512*17
FIXTURE_SHA256="71da8201d571fbd2856848066a18b5f844a83533742937e2b0dcefcae55049eb"
ORIGINAL_JSON_BYTES=122792
ORIGINAL_JSON_SHA256="1ce45d95a09eae9d5f95754e4ef582244fa707ca08598223eeb52930d7c65fb9"
HEX16=re.compile(r"[0-9a-f]{16}\Z")
POINT_INDEX={point:i for i,point in enumerate(complete.POINTS)}
assert len(POINT_INDEX)==128


class FrozenCompleteCellError(ValueError):
    """Actual 26.2 complete-cell stock reference integrity not established."""


def load_bits(path:Path=FIXTURE)->tuple[str,...]:
    raw=path.read_bytes()
    if len(raw)!=FIXTURE_BYTES or hashlib.sha256(raw).hexdigest()!=FIXTURE_SHA256:
        raise FrozenCompleteCellError("exact real stock complete-cell bit fixture bytes/SHA changed")
    try:
        lines=raw.decode("ascii").splitlines(keepends=True)
    except UnicodeDecodeError as exc:
        raise FrozenCompleteCellError("non-ASCII actual stock full-cell reference") from exc
    if len(lines)!=512:
        raise FrozenCompleteCellError("not 512 complete original stock cell words")
    bits=[]
    for i,line in enumerate(lines):
        if len(line)!=17 or not line.endswith("\n") or \
           not HEX16.fullmatch(line[:-1]) or \
           (int(line[:-1],16)>>52)&0x7ff==0x7ff:
            raise FrozenCompleteCellError("nonfinite/invalid full-cell bitword "+str(i))
        bits.append(line[:-1])
    return tuple(bits)


def validate_manifest(manifest:dict,bits:tuple[str,...])->None:
    methods=previous.source_methods()
    try:
        complete.validate(manifest,methods)
    except (complete.CompleteCellError,ValueError,KeyError,TypeError) as exc:
        raise FrozenCompleteCellError(
            "original complete-cell source identity, coordinate order or gate changed"
        ) from exc
    if len(bits)!=512 or len(manifest["vectors"])!=512:
        raise FrozenCompleteCellError("not 512 exact stock original cell observations")
    for i,(row,word) in enumerate(zip(manifest["vectors"],bits,strict=True)):
        if row["value_bits"]!="0x"+word:
            raise FrozenCompleteCellError("stock original complete-cell rawbit mismatch: "+str(i))
    # Frozen earlier 16 official values are independent first-pass observations.
    # Preserve ALL overlaps, not just (0,64,0). The Y/X/Z traversal still
    # differs from canonical Minecraft chunk block population order.
    first16=previous.load_bits()
    for seed_index in range(4):
        for old_index,point in enumerate(complete.cell.POINTS):
            new_index=seed_index*128+POINT_INDEX[point]
            old_bit=first16[seed_index*4+old_index]
            if bits[new_index]!=old_bit:
                raise FrozenCompleteCellError(
                    "stock original 16/512 cell coordinate overlap changed: "+
                    str(seed_index)+"/"+str(old_index)
                )


def validate_original_capture(path:Path)->None:
    raw=path.read_bytes()
    if len(raw)!=ORIGINAL_JSON_BYTES or \
       hashlib.sha256(raw).hexdigest()!=ORIGINAL_JSON_SHA256:
        raise FrozenCompleteCellError(
            "original complete-cell stock JVM 122792-byte JSON bytes/SHA changed"
        )
    try:
        manifest=json.loads(raw)
    except (ValueError,UnicodeError) as exc:
        raise FrozenCompleteCellError("invalid exact real stock complete-cell JSON") from exc
    validate_manifest(manifest,load_bits())


def main(argv:list[str]|None=None)->int:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--capture",type=Path,help=(
        "Optionally verify exact 122792-byte original stock JVM JSON against the immutable 512-bit reference"
    ))
    args=parser.parse_args(argv)
    try:
        words=load_bits()
        # Validate overlap even if original receipt remains private.
        old=previous.load_bits()
        for seed_index in range(4):
            for old_index,p in enumerate(complete.cell.POINTS):
                if words[seed_index*128+POINT_INDEX[p]]!=old[seed_index*4+old_index]:
                    raise FrozenCompleteCellError("frozen 16/512 real stock overlap differs")
        if args.capture is not None:
            validate_original_capture(args.capture)
    except (OSError,FrozenCompleteCellError,previous.FrozenNoiseChunkError) as exc:
        print("STOCK 26.2 COMPLETE CELL REFERENCE UNQUALIFIED: "+str(exc),file=sys.stderr)
        return 2
    print(json.dumps({
        "reference":"original_26_2_stock_NoiseChunk_complete_single_4x8x4_cell",
        "vectors":512,"seeds":4,"original_overlap_bitwise_matches":16,
        "stock_noisechunk_complete_cell_reference_frozen":True,
        "bit_fixture_sha256":FIXTURE_SHA256,
        "original_official_capture_sha256":ORIGINAL_JSON_SHA256,
        "stock_noisechunk_canonical_traversal_qualified":False,
        "stock_noisechunk_full_lifecycle_qualified":False,
        "rust_router_numeric_parity_qualified":False,
        "independent_var_sem_admitted":False,
        "production_worldgen_enabled":False,
    },sort_keys=True))
    return 0


if __name__=="__main__":
    raise SystemExit(main())
