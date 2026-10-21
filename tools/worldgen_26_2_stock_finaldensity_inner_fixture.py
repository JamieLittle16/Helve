#!/usr/bin/env python3
"""Pin authentic stock 26.2 finalDensity Marker/SQUEEZE/RangeChoice input words.

This validation does not grant source-law, NoiseChunk cache/interpolation or
production authority. Its 128 rows are the *new* original JVM inner inputs,
not another root output capture. Verify both against previously frozen
first-level JVM operands and the exact source-free original owner report.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import struct
import sys
from pathlib import Path

import worldgen_26_2_stock_final_density_inner_semantics as inner
import worldgen_26_2_stock_finaldensity_min_root_fixture as root_fixture

ROOT=Path(__file__).resolve().parents[1]
FIXTURE=ROOT/"crates/world/helve-world-gen/tests/data/stock_finaldensity_inner_128_rawbits.tsv"
SHA256="967c9203950f0e22a8b69f73dfe5e1bd1438ef1224fcc4346b8d578409c45170"
ORIGINAL_JSON_SHA256="22c8473fa1cc409f9833731306a1d35cb633808c6571ea75fbb84a45150c56b1"
ORIGINAL_JSON_BYTES=67785
FIELDS=("marker_bits","marker_wrapped_bits","mapped_bits",
        "range_selector_bits","range_in_bits","range_out_bits","holder_bits")
WIDTH=7*16+6+1
LINE=re.compile(r"([0-9a-f]{16})(?:\t([0-9a-f]{16})){6}\n\Z")
MIN=-1_000_000.0
MAX=0.0
ALLOWED_GATES=inner.GATES


class InnerFixtureError(ValueError):
    """The original bound JVM 26.2 inner receipt is not qualified."""


def value(bits:str)->float:
    return struct.unpack(">d",bytes.fromhex(bits))[0]


def bits(value:float)->str:
    return struct.pack(">d",value).hex()


def squeeze_candidate(x:float)->float:
    clamped=min(1.0,max(-1.0,x))
    return clamped/2.0-clamped*clamped*clamped/24.0


def load(path:Path=FIXTURE,*,require_sha:bool=True)->tuple[tuple[str,...],...]:
    data=path.read_bytes()
    if len(data)!=128*WIDTH or (require_sha and
        hashlib.sha256(data).hexdigest()!=SHA256):
        raise InnerFixtureError("inner original JVM fixture length/SHA changed")
    try:
        text=data.decode("ascii")
    except UnicodeDecodeError as exc:
        raise InnerFixtureError("non-ASCII original inner JVM fixture") from exc
    rows=[]
    in_count=0
    out_count=0
    min_count=0
    old=root_fixture.read_words()
    for i,line in enumerate(text.splitlines(keepends=True)):
        if not LINE.fullmatch(line):
            raise InnerFixtureError("invalid bounded original JVM inner row "+str(i))
        fields=tuple(line.rstrip("\n").split("\t"))
        if len(fields)!=7 or any(len(field)!=16 for field in fields):
            raise InnerFixtureError("wrong original inner operand arity")
        marker,wrapped,mapped,selector,inside,outside,holder=fields
        vals=[value(x) for x in fields]
        if any(not math.isfinite(x) for x in vals):
            raise InnerFixtureError("nonfinite original JVM inner operand")
        if marker!=wrapped:
            raise InnerFixtureError("stock Interpolated Marker single-point delegation changed")
        if squeeze_candidate(vals[0])!=vals[2] or bits(squeeze_candidate(vals[0]))!=mapped:
            raise InnerFixtureError("stock Mapped SQUEEZE candidate bit parity changed: "+str(i))
        if inside!=bits(64.0):
            raise InnerFixtureError("stock in-range Constant(64) changed")
        branch_in=MIN<=vals[3]<MAX
        winner=inside if branch_in else outside
        if winner!=holder:
            raise InnerFixtureError("stock RangeChoice branch selection changed: "+str(i))
        in_count+=int(branch_in)
        out_count+=int(not branch_in)
        if (mapped,holder)!=old[i][:2]:
            raise InnerFixtureError("old frozen first-level stock JVM operands changed: "+str(i))
        root_min=mapped if vals[2]<=vals[6] else holder
        if root_min!=old[i][2]:
            raise InnerFixtureError("stock finalDensity MIN root regressed: "+str(i))
        min_count+=int(vals[6]<vals[2])
        rows.append(fields)
    if len(rows)!=128 or in_count!=47 or out_count!=81 or min_count!=4:
        raise InnerFixtureError("original stock 26.2 branch/winner coverage changed")
    return tuple(rows)


def validate_original(path:Path)->None:
    data=path.read_bytes()
    if len(data)!=ORIGINAL_JSON_BYTES or hashlib.sha256(data).hexdigest()!=ORIGINAL_JSON_SHA256:
        raise InnerFixtureError("source-free original inner owner JSON identity changed")
    try:
        report=json.loads(data)
        inner.validate(report)
    except (ValueError,KeyError,TypeError,IndexError) as exc:
        raise InnerFixtureError("original stock 26.2 source-free JSON failed validation") from exc
    if any(shape["marker_kind"]!="Interpolated" or
           shape["marker_wrapped_class"]!="net.minecraft.world.level.levelgen.DensityFunctions$MulOrAdd" or
           shape["range_selector_class"]!="net.minecraft.world.level.levelgen.DensityFunctions$Marker" or
           shape["range_in_class"]!="net.minecraft.world.level.levelgen.DensityFunctions$Constant" or
           shape["range_out_class"]!="net.minecraft.world.level.levelgen.DensityFunctions$Ap2" or
           shape["range_min_inclusive_bits"]!="0xc12e848000000000" or
           shape["range_max_exclusive_bits"]!="0x0000000000000000"
           for shape in report["shapes"]):
        raise InnerFixtureError("observed stock inner graph/type/bound shape changed")
    old=load()
    for i,(row,expected) in enumerate(zip(report["vectors"],old,strict=True)):
        if tuple(row[k][2:] for k in FIELDS)!=expected:
            raise InnerFixtureError("original owner inner input changed: "+str(i))


def main(argv:list[str]|None=None)->int:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--capture",type=Path,help="Optional exact 67,785-byte original source-free user report")
    args=parser.parse_args(argv)
    try:
        rows=load()
        if args.capture is not None:
            validate_original(args.capture)
    except (InnerFixtureError,OSError) as exc:
        print("STOCK 26.2 FINAL INNER FIXTURE UNQUALIFIED: "+str(exc),file=sys.stderr)
        return 2
    print(json.dumps({
        "kind":"observed_26_2_finaldensity_inner_128_singlepoint_only",
        "rows":len(rows),"four_seed_squeeze_rawbits_matched":128,
        "range_choice_in_count":47,"range_choice_out_count":81,
        "holder_wins_final_min":4,
        "marker_kind":"Interpolated",
        "range_min_inclusive":MIN,"range_max_exclusive":MAX,
        "source_free_fixture_sha256":SHA256,
        "original_inner_report_sha256":ORIGINAL_JSON_SHA256,
        **{k:False for k in ALLOWED_GATES},
        "end_to_end_final_density_qualified":False,
    },sort_keys=True))
    return 0


if __name__=="__main__":
    raise SystemExit(main())
