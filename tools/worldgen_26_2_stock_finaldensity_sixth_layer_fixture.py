#!/usr/bin/env python3
"""Immutable genuine sixth-layer 26.2 original-JVM child-value fixture.

Only four newly exposed IEEE words/point; all six old fifth-layer words
remain strictly independent SHA-pinned equality anchors. Exact original
private JSON is optional for offline source-owner receipt authentication.
This is NOT a stock NoiseChunk or full-router qualification.
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

import worldgen_26_2_stock_final_density_sixth_layer as sixth

ROOT=Path(__file__).resolve().parents[1]
FIXTURE=ROOT/"crates/world/helve-world-gen/tests/data/stock_finaldensity_sixth_layer_new_128_rawbits.tsv"
SHA256="b41f262fe145d82fa5d7f05d586663918c4ad900654a7e0906559405cca1d68e"
REPORT_SHA256="597287a4fde98d3fd2f984f6c4b9de20016782e8fd45532092fd797d5697aa35"
REPORT_BYTES=93302
LINE=re.compile(r"[0-9a-f]{16}(?:\t[0-9a-f]{16}){3}\n\Z")
WIDTH=4*16+3+1
NEW_FIELDS=sixth.NEW_FIELDS
CLASS=sixth.CLASS
EXPECTED_SHAPE={
    "left_gradient_from_y":-64,
    "left_gradient_to_y":-40,
    "left_gradient_from_value_bits":"0x0000000000000000",
    "left_gradient_to_value_bits":"0x3ff0000000000000",
    "outside_gradient_from_y":-4064,
    "outside_gradient_to_y":4062,
    "outside_gradient_from_value_bits":"0xc0afc00000000000",
    "outside_gradient_to_value_bits":"0x40afbc0000000000",
    "left_mul_enum_class":CLASS+"MulOrAdd$Type",
    "left_mul_op":"ADD",
    "left_mul_arg_bits":"0xbfbe000000000000",
    "left_mul_child_class":CLASS+"MulOrAdd",
    "outside_mul_enum_class":CLASS+"MulOrAdd$Type",
    "outside_mul_op":"MUL",
    "outside_mul_arg_bits":"0xbf9999999999999a",
    "outside_mul_child_class":CLASS+"Noise",
    "left_marker_enum_class":CLASS+"Marker$Type",
    "left_marker_kind":"Interpolated",
    "left_marker_child_class":CLASS+"RangeChoice",
    "right_marker_enum_class":CLASS+"Marker$Type",
    "right_marker_kind":"Interpolated",
    "right_marker_child_class":CLASS+"RangeChoice",
}


class SixthLayerFixtureError(ValueError):
    """Source-owning evidence must not be silently qualified."""


def value(word:str)->float:
    return struct.unpack(">d",bytes.fromhex(word))[0]


def bits(number:float)->str:
    return struct.pack(">d",number).hex()


def gradient(y:int,fy:int,ty:int,fv:float,tv:float)->float:
    alpha=max(0.0,min(1.0,(float(y)-float(fy))/(float(ty)-float(fy))))
    return fv+alpha*(tv-fv)


def load(path:Path=FIXTURE,*,require_sha:bool=True)->tuple[tuple[str,...],...]:
    raw=path.read_bytes()
    if len(raw)!=128*WIDTH or (require_sha and
            hashlib.sha256(raw).hexdigest()!=SHA256):
        raise SixthLayerFixtureError("original sixth-layer 4-word fixture SHA/bytes changed")
    try:
        lines=raw.decode("ascii").splitlines(keepends=True)
    except UnicodeError as exc:
        raise SixthLayerFixtureError("non-ASCII sixth-layer fixture") from exc
    parent=sixth.prior.load()
    points=sixth.fifth.fourth.third.second.final.input_rows()
    output=[]
    for i,line in enumerate(lines):
        if not LINE.fullmatch(line):
            raise SixthLayerFixtureError("fifth-to-sixth new rawbits schema changed: "+str(i))
        l,o,ml,mr=line[:-1].split("\t")
        if not all(math.isfinite(value(w)) for w in (l,o,ml,mr)):
            raise SixthLayerFixtureError("nonfinite original-JVM sixth layer")
        f=parent[i]
        y=points[i]["block_y"]
        if bits(gradient(y,-64,-40,0.0,1.0))!=f[0]:
            raise SixthLayerFixtureError("left gradient old rawbits changed: "+str(i))
        if bits(gradient(y,-4064,4062,-4064.0,4062.0))!=f[2]:
            raise SixthLayerFixtureError("outside gradient old rawbits changed: "+str(i))
        if bits(value(l)+value("bfbe000000000000"))!=f[1]:
            raise SixthLayerFixtureError("left inner original ADD rawbits changed: "+str(i))
        if bits(value(o)*value("bf9999999999999a"))!=f[3]:
            raise SixthLayerFixtureError("outside inner original MUL rawbits changed: "+str(i))
        if ml!=f[4] or mr!=f[5]:
            raise SixthLayerFixtureError("two interpolated Marker old rawbits changed: "+str(i))
        output.append((l,o,ml,mr))
    if len(output)!=128:
        raise SixthLayerFixtureError("original six-layer samples missing")
    return tuple(output)


def validate_original(path:Path)->None:
    raw=path.read_bytes()
    if len(raw)!=REPORT_BYTES or hashlib.sha256(raw).hexdigest()!=REPORT_SHA256:
        raise SixthLayerFixtureError("private original sixth report identity changed")
    try:
        report=json.loads(raw)
        sixth.validate(report)
    except (ValueError,KeyError,TypeError,IndexError) as exc:
        raise SixthLayerFixtureError("original sixth-layer provenance validator rejected") from exc
    if report.get("source_text_included") is not False:
        raise SixthLayerFixtureError("original sixth-layer source-free exclusion changed")
    if any({k:v for k,v in s.items() if k!="world_seed_bits"}!=EXPECTED_SHAPE
           for s in report["shapes"]):
        raise SixthLayerFixtureError("real original 26.2 sixth graph shape changed")
    for i,(v,new) in enumerate(zip(report["vectors"],load(),strict=True)):
        if tuple(v[k][2:] for k in NEW_FIELDS)!=new:
            raise SixthLayerFixtureError("new original-JVM sixth input changed: "+str(i))


def main(argv:list[str]|None=None)->int:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--capture",type=Path,help="optional exact 93302-byte original-JVM owner JSON")
    args=parser.parse_args(argv)
    try:
        rows=load()
        if args.capture:
            validate_original(args.capture)
    except (SixthLayerFixtureError,OSError) as exc:
        print("STOCK 26.2 SIXTH-LAYER FIXTURE UNQUALIFIED: "+str(exc),file=sys.stderr)
        return 2
    print(json.dumps({
        "kind":"original_26_2_finaldensity_sixth_layer_128_singlepoint_only",
        "new_input_rows":len(rows),"new_input_words":len(rows)*len(NEW_FIELDS),
        "left_mul_operation":"ADD","left_mul_arg_bits":EXPECTED_SHAPE["left_mul_arg_bits"],
        "outside_mul_operation":"MUL","outside_mul_arg_bits":EXPECTED_SHAPE["outside_mul_arg_bits"],
        "two_marker_kinds":"Interpolated",
        "left_gradient_rawbit_matches":128,"outside_gradient_rawbit_matches":128,
        "left_add_rawbit_matches":128,"outside_multiply_rawbit_matches":128,
        "two_marker_forwarding_matches":256,
        "source_free_fixture_sha256":SHA256,
        "original_owner_report_sha256":REPORT_SHA256,
        **{gate:False for gate in sixth.GATES},
    },sort_keys=True))
    return 0


if __name__=="__main__":
    raise SystemExit(main())
