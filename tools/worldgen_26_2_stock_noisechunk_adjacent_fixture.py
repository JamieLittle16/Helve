#!/usr/bin/env python3
"""Freeze 768 genuine stock 26.2 NoiseChunk experimental adjacent-cell bits.

This is a strictly source-free original-JVM reference across two chunk origins
and explicit swapSlices transitions, NOT source-reviewed canonical traversal,
not a compiled Rust numerical parity claim, and not production worldgen.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

import worldgen_26_2_stock_noisechunk_adjacent_capture as adjacent
import worldgen_26_2_stock_noisechunk_complete_cell_fixture as complete
import worldgen_26_2_stock_noisechunk_cell_fixture as previous

ROOT=Path(__file__).resolve().parents[1]
FIXTURE=ROOT/"vanilla/reports/worldgen-26_2-stock-noisechunk-adjacent-768-bits.txt"
FIXTURE_BYTES=768*17
FIXTURE_SHA256="906ef4684d025d633e7d04f8c963b62b41c725b800739ce37e3256d8f484c95f"
ORIGINAL_JSON_BYTES=150067
ORIGINAL_JSON_SHA256="86f33de3a4fe19a6bcc202badaaeb23bdef83bab29405e01534bd12c226bbcc1"
HEX16=re.compile(r"[0-9a-f]{16}\\Z")
# Only new method identities are added; the prior nine remain byte-locked
# by the existing source-free frozen 16/512 method registry.
NEW_METHODS={
    "chunk_swap":{
        "owner":"net.minecraft.world.level.levelgen.NoiseChunk",
        "signature":"swapSlices()",
        "body_sha256":"108ea4689ae3494e57a7ebc78d1c6d4a81ac1551df5884d94d03d8fe3fcedb81",
        "normalized_sha256":"1f2f46739ec1e9e9dacdbf01efb7c2f54e74a9271ac808c5b03e14e71f9b45d9",
        "reviewed":False,
    },
    "generator_fill":{
        "owner":"net.minecraft.world.level.levelgen.NoiseBasedChunkGenerator",
        "signature":"fillFromNoise(final Blender blender , final RandomState randomState , final StructureManager structureManager , final ChunkAccess centerChunk)",
        "body_sha256":"2450a83eaf8f8b14a1947b8b1da190fdf6bbfb170b8904ada94e48fd551b8a52",
        "normalized_sha256":"d5e60ae54a7adb89b7304bd3aa0545ed61653268f35ed7de43d9779888fb4b62",
        "reviewed":False,
    },
    "generator_do_fill":{
        "owner":"net.minecraft.world.level.levelgen.NoiseBasedChunkGenerator",
        "signature":"doFill(final Blender blender , final StructureManager structureManager , final RandomState randomState , final ChunkAccess centerChunk , final int cellMinY , final int cellCountY)",
        "body_sha256":"5f8ccb1a66c47fe7d45ba5df3f4423d7c5d8543ece5cb5f375aa33b1eeb44cb7",
        "normalized_sha256":"1aefbea4036ed0fb54d8eefa9998fa85b598d058be339bee8e06658117f5753e",
        "reviewed":False,
    },
}


class FrozenAdjacentError(ValueError):
    """Pinned original adjacent NoiseChunk reference is unqualified."""


def source_methods()->dict:
    result=dict(previous.source_methods())
    if set(result)&set(NEW_METHODS):
        raise FrozenAdjacentError("overlapping source method identity")
    return result|NEW_METHODS


def load_bits(path:Path=FIXTURE)->tuple[str,...]:
    raw=path.read_bytes()
    if len(raw)!=FIXTURE_BYTES or hashlib.sha256(raw).hexdigest()!=FIXTURE_SHA256:
        raise FrozenAdjacentError("768 original adjacent bit fixture bytes/SHA changed")
    try:
        lines=raw.decode("ascii").splitlines(keepends=True)
    except UnicodeDecodeError as exc:
        raise FrozenAdjacentError("non-ASCII 768 original adjacent bits") from exc
    if len(lines)!=768:
        raise FrozenAdjacentError("not exactly 768 adjacent bitwords")
    words=[]
    for i,line in enumerate(lines):
        if (len(line)!=17 or not line.endswith("\\n") or
            not HEX16.fullmatch(line[:-1]) or
            ((int(line[:-1],16)>>52)&0x7ff)==0x7ff):
            raise FrozenAdjacentError("invalid/nonfinite original adjacent bitword "+str(i))
        words.append(line[:-1])
    return tuple(words)


def overlapping_count(bits:tuple[str,...])->int:
    baseline=complete.load_bits()
    index=complete.POINT_INDEX
    matched=0
    for seed_i in range(len(adjacent.SEEDS)):
        # Earlier 512 values are only for the 0,0 chunk, Y=64..71.
        for point_i,point in enumerate(adjacent.points(0)):
            if point not in index:
                continue
            new_bit=bits[seed_i*192+point_i]
            old_bit=baseline[seed_i*128+index[point]]
            if new_bit!=old_bit:
                raise FrozenAdjacentError(
                    "genuine old 512/new 768 coordinate overlap changed: "+
                    str(seed_i)+"/"+str(point)
                )
            matched+=1
    if matched!=32:
        raise FrozenAdjacentError("not exactly 32 independent old 512/new 768 matches")
    return matched


def validate_manifest(manifest:dict,bits:tuple[str,...])->None:
    try:
        adjacent.validate(manifest,source_methods())
    except (adjacent.AdjacentError,ValueError,KeyError,TypeError) as exc:
        raise FrozenAdjacentError(
            "original adjacent source identity, coordinates or gates changed"
        ) from exc
    if len(bits)!=768 or len(manifest["vectors"])!=768:
        raise FrozenAdjacentError("not 768 adjacent original observations")
    for i,(row,word) in enumerate(zip(manifest["vectors"],bits,strict=True)):
        if row["value_bits"]!="0x"+word:
            raise FrozenAdjacentError("original adjacent raw-bit mismatch: "+str(i))
    overlapping_count(bits)


def validate_original_capture(path:Path)->None:
    raw=path.read_bytes()
    if len(raw)!=ORIGINAL_JSON_BYTES or hashlib.sha256(raw).hexdigest()!=ORIGINAL_JSON_SHA256:
        raise FrozenAdjacentError("original 150067-byte stock adjacent JSON bytes/SHA changed")
    try:
        manifest=json.loads(raw)
    except (UnicodeError,ValueError) as exc:
        raise FrozenAdjacentError("malformed original adjacent stock JSON") from exc
    validate_manifest(manifest,load_bits())


def main(argv:list[str]|None=None)->int:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--capture",type=Path,
                        help="Optional exact original 150067-byte adjacent JSON receipt")
    args=parser.parse_args(argv)
    try:
        bits=load_bits()
        matches=overlapping_count(bits)
        if args.capture is not None:
            validate_original_capture(args.capture)
    except (OSError,FrozenAdjacentError,complete.FrozenCompleteCellError,
            previous.FrozenNoiseChunkError) as exc:
        print("STOCK 26.2 ADJACENT REFERENCE UNQUALIFIED: "+str(exc),file=sys.stderr)
        return 2
    print(json.dumps({
        "reference":"original_26_2_stock_NoiseChunk_EXPERIMENTAL_adjacent_cells",
        "vectors":768,"seeds":4,"origins":2,
        "genuine_complete_cell_overlap_bitwise_matches":matches,
        "candidate_adjacent_reference_frozen":True,
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
