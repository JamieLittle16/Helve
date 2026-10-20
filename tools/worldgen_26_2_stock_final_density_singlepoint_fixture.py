#!/usr/bin/env python3
"""Immutable source-free 128-bit stock 26.2 Overworld finalDensity reference.

The stock JVM computed these exact 128 values via true RandomState.router()
and DensityFunction.compute(SinglePointContext). This verifies the ORIGINAL
numeric receipt and provenance; it does not implement, run, or qualify a Rust
NoiseRouter, a stock NoiseChunk, interpolation or production terrain.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

import worldgen_26_2_stock_final_density_singlepoint_capture as capture

ROOT=Path(__file__).resolve().parents[1]
FIXTURE=ROOT/"vanilla/reports/worldgen-26_2-stock-final-density-singlepoint-128-bits.txt"
FIXTURE_SHA256="058846dd4c755802ffe43f829b109884331962712ac7556f4d5cb4320a597e4f"
ORIGINAL_JSON_SHA256="0c294020fb2ad882f6ed88e5759e032c6955d48be3cfef1a19a089f561bb059d"
ORIGINAL_JSON_BYTES=25704
HEX16=re.compile(r"[0-9a-f]{16}\Z")
METHODS={
    "ap2_compute":(
        capture.FINAL,"compute(final DensityFunction . FunctionContext context)",
        "54d44e99cae188665438eda580ab0a76204c0c486b80edb603f32fa4375b3e48",
        "5f5a5777d74971ea81d88a9da9d437f73d7934bae27d0dcb5b73acba9bc14e1b",
    ),
    "holder_holder_compute":(
        capture.HOLDER,"compute(final DensityFunction . FunctionContext context)",
        "766c33ffa1e2b33e38704aff1091b8abcf90e88365d12fbd274edfb70f1082aa",
        "c43831a20cf75a130a0b711f7ab9bc005c3ca95a3747aa7c8868dd838e06e1fe",
    ),
    "random_state_router":(
        capture.roots.STATE,"router()",
        "02377bf15b6627b0b8c54730f3a517fe1409ae3e3dc0bf96741b8c7099f1f90b",
        "0b5f28d48f161e0785859e590b54692ab3c433e2793027188bfa3e6a1c923b4e",
    ),
    "router_map_all":(
        capture.roots.ROUTER,
        "mapAll(final DensityFunction . Visitor visitor)",
        "61ea5c6e319640ee561342ceeb9833aaf9c832ce3aa296e27a2bc1f965a9897c",
        "f1b633f1d879a2f1fecf50e94301bb9508d360d6ed998d2096bd02fb41a48298",
    ),
}


class FrozenFinalDensityError(ValueError):
    """The original stock final-density numeric reference is unqualified."""


def load_bits(path:Path=FIXTURE) -> tuple[str,...]:
    raw=path.read_bytes()
    if len(raw)!=128*17 or hashlib.sha256(raw).hexdigest()!=FIXTURE_SHA256:
        raise FrozenFinalDensityError("real finalDensity bit fixture bytes/SHA changed")
    try:
        lines=raw.decode("ascii").splitlines(keepends=True)
    except UnicodeDecodeError as exc:
        raise FrozenFinalDensityError("non-ASCII official raw-bits fixture") from exc
    if len(lines)!=128:
        raise FrozenFinalDensityError("expected 128 official finalDensity raw-bit words")
    result=[]
    for idx,line in enumerate(lines):
        if len(line)!=17 or line[-1]!="\n" or not HEX16.fullmatch(line[:-1]) or \
           (int(line[:-1],16)>>52)&0x7ff==0x7ff:
            raise FrozenFinalDensityError("unqualified official raw-bit record "+str(idx))
        result.append(line[:-1])
    return tuple(result)


def validate_manifest(manifest:dict,bits:tuple[str,...]) -> None:
    if not isinstance(manifest,dict):
        raise FrozenFinalDensityError("expected source-free official stock manifest")
    methods=manifest.get("source_methods")
    if not isinstance(methods,dict) or set(methods)!=set(METHODS):
        raise FrozenFinalDensityError("source method inventory not original/pinned")
    for name,(owner,signature,body,normalized) in METHODS.items():
        if methods[name]!={
            "owner":owner,"signature":signature,
            "body_sha256":body,"normalized_sha256":normalized,
            "reviewed":False,
        }:
            raise FrozenFinalDensityError("actual source method fingerprint changed: "+name)
    try:
        capture.validate(manifest,methods)
    except (capture.FinalDensityError,ValueError,KeyError,TypeError) as exc:
        raise FrozenFinalDensityError("source-free official manifest is unqualified") from exc
    rows=manifest["vectors"]
    if len(rows)!=len(bits):
        raise FrozenFinalDensityError("official reference/fixture count differs")
    for idx,(row,bit) in enumerate(zip(rows,bits,strict=True)):
        if row["value_bits"]!="0x"+bit:
            raise FrozenFinalDensityError("real stock finalDensity bit mismatch at "+str(idx))


def validate_original_capture(path:Path) -> None:
    raw=path.read_bytes()
    if len(raw)!=ORIGINAL_JSON_BYTES or \
       hashlib.sha256(raw).hexdigest()!=ORIGINAL_JSON_SHA256:
        raise FrozenFinalDensityError("original captured JVM JSON bytes/SHA changed")
    try:
        original=json.loads(raw)
    except (UnicodeError,ValueError) as exc:
        raise FrozenFinalDensityError("invalid original stock JVM final-density receipt") from exc
    validate_manifest(original,load_bits())


def main(argv:list[str]|None=None) -> int:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--capture",type=Path,
                        help="Optional exact original 25,704-byte source-free JVM JSON")
    args=parser.parse_args(argv)
    try:
        words=load_bits()
        if args.capture is not None:
            validate_original_capture(args.capture)
    except (FrozenFinalDensityError,OSError) as exc:
        print("STOCK 26.2 FINAL DENSITY REFERENCE UNQUALIFIED: "+str(exc),file=sys.stderr)
        return 2
    print(json.dumps({
        "vectors":len(words),"source":"stock_overworld_finalDensity_SinglePointContext",
        "fixture_sha256":FIXTURE_SHA256,
        "original_capture_sha256":ORIGINAL_JSON_SHA256,
        "stock_singlepoint_reference_verified":True,
        "rust_final_density_parity_verified":False,
        "stock_noisechunk_interpolation_observed":False,
        "independent_var_sem_admitted":False,
        "production_worldgen_enabled":False,
    },sort_keys=True))
    return 0


if __name__=="__main__":
    raise SystemExit(main())
