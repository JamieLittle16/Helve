#!/usr/bin/env python3
"""Authenticate only six NEW original 26.2 fifth-layer finalDensity operands.

Exactly 128 stock SinglePointContext observations and immutable old fourth-layer
output anchors. No original source, JAR, Atlas, old oracle duplication, broader
source-law claim, NoiseChunk lifecycle or production authority.
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

import worldgen_26_2_stock_final_density_fifth_layer as fifth

ROOT=Path(__file__).resolve().parents[1]
FIXTURE=ROOT/"crates/world/helve-world-gen/tests/data/stock_finaldensity_fifth_layer_new_128_rawbits.tsv"
SHA256="1f0c3cf5e9c7fda8a8c348d68d431a99f4c3871611dacd48a97a442ed95a9433"
REPORT_SHA256="0116b9cc0d7ed21edc19a93b37a99207f37726fa781affbd7901dc814b390bbd"
REPORT_BYTES=103398
LINE=re.compile(r"[0-9a-f]{16}(?:\t[0-9a-f]{16}){5}\n\Z")
WIDTH=6*16+5+1
NEW_FIELDS=fifth.NEW_FIELDS
CLASS=fifth.CLASS
ARG="bfb3333333333334"
GRADIENT_FROM_Y=-4064
GRADIENT_TO_Y=4062
EXPECTED_SHAPE={
    "left_ap2_enum_class":CLASS+"TwoArgumentSimpleFunction$Type",
    "left_ap2_op":"MUL",
    "left_ap2_left_class":CLASS+"YClampedGradient",
    "left_ap2_right_class":CLASS+"MulOrAdd",
    "gradient_from_y":GRADIENT_FROM_Y,
    "gradient_to_y":GRADIENT_TO_Y,
    "gradient_from_value_bits":"0xc0afc00000000000",
    "gradient_to_value_bits":"0x40afbc0000000000",
    "outside_holder_target_class":CLASS+"YClampedGradient",
    "outside_in_enum_class":CLASS+"MulOrAdd$Type",
    "outside_in_op":"ADD",
    "outside_in_argument_bits":"0x"+ARG,
    "outside_in_child_class":CLASS+"MulOrAdd",
    "max_left_mapped_enum_class":CLASS+"Mapped$Type",
    "max_left_mapped_kind":"ABS",
    "max_left_mapped_child_class":CLASS+"Marker",
    "max_right_mapped_enum_class":CLASS+"Mapped$Type",
    "max_right_mapped_kind":"ABS",
    "max_right_mapped_child_class":CLASS+"Marker",
}


class FifthLayerFixtureError(ValueError):
    """Fifth-layer original JVM receipt cannot be admitted."""


def value(word:str)->float:
    return struct.unpack(">d",bytes.fromhex(word))[0]


def bits(number:float)->str:
    return struct.pack(">d",number).hex()


def gradient(y:int)->float:
    # This is a finite-sample comparison with the original observed
    # record fields. It is NOT a stock 26.2 source-law admission.
    span=GRADIENT_TO_Y-GRADIENT_FROM_Y
    t=max(0.0,min(1.0,(float(y)-GRADIENT_FROM_Y)/span))
    return float(GRADIENT_FROM_Y)+t*span


def load(path:Path=FIXTURE,*,require_sha:bool=True)->tuple[tuple[str,...],...]:
    data=path.read_bytes()
    if len(data)!=128*WIDTH or (require_sha and
            hashlib.sha256(data).hexdigest()!=SHA256):
        raise FifthLayerFixtureError("original fifth-layer six-word fixture bytes/SHA changed")
    try:
        lines=data.decode("ascii").splitlines(keepends=True)
    except UnicodeError as exc:
        raise FifthLayerFixtureError("non-ASCII original fifth-layer evidence") from exc
    old=fifth.prior.load()
    points=fifth.fourth.third.second.final.input_rows()
    result=[]
    for index,line in enumerate(lines):
        if not LINE.fullmatch(line):
            raise FifthLayerFixtureError("invalid original fifth-layer IEEE row "+str(index))
        left,right,holder,inner,absolute_left,absolute_right=line[:-1].split("\t")
        if not all(math.isfinite(value(x)) for x in
                (left,right,holder,inner,absolute_left,absolute_right)):
            raise FifthLayerFixtureError("fifth-layer original child nonfinite")
        p=old[index]
        if bits(value(left)*value(right))!=p[0]:
            raise FifthLayerFixtureError("left Ap2 original MUL bit result changed: "+str(index))
        if holder!=p[2]:
            raise FifthLayerFixtureError("real outside Holder target forwarding changed: "+str(index))
        if bits(value(inner)+value(ARG))!=p[3]:
            raise FifthLayerFixtureError("outside in-range original ADD bits changed: "+str(index))
        if bits(abs(value(absolute_left)))!=p[5] or (
                bits(abs(value(absolute_right)))!=p[6]):
            raise FifthLayerFixtureError("original two ABS Mapped outputs changed: "+str(index))
        # Nested Y-gradient is the one whose endpoints were reflected.
        # Outside holder's target class is also YClampedGradient but its
        # actual *parameters* have NOT been inspected; never alias them.
        if bits(gradient(points[index]["block_y"]))!=p[1]:
            raise FifthLayerFixtureError("nested original Y-gradient words changed: "+str(index))
        result.append((left,right,holder,inner,absolute_left,absolute_right))
    if len(result)!=128:
        raise FifthLayerFixtureError("fifth-layer expected 128 samples")
    return tuple(result)


def validate_original(path:Path)->None:
    raw=path.read_bytes()
    if len(raw)!=REPORT_BYTES or hashlib.sha256(raw).hexdigest()!=REPORT_SHA256:
        raise FifthLayerFixtureError("original fifth-layer private owner report identity changed")
    try:
        report=json.loads(raw)
        fifth.validate(report)
    except (ValueError,KeyError,TypeError,IndexError) as exc:
        raise FifthLayerFixtureError("original fifth-layer owner validator rejected") from exc
    for s in report["shapes"]:
        if {k:v for k,v in s.items() if k!="world_seed_bits"}!=EXPECTED_SHAPE:
            raise FifthLayerFixtureError("fifth-layer actual seed-invariant shape changed")
    for index,(v,new) in enumerate(zip(report["vectors"],load(),strict=True)):
        if tuple(v[k][2:] for k in NEW_FIELDS)!=new:
            raise FifthLayerFixtureError("original fifth-layer new input changed: "+str(index))


def main(argv:list[str]|None=None)->int:
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--capture",type=Path,
                   help="Optional exact original 103398-byte fifth-layer owner JSON")
    args=p.parse_args(argv)
    try:
        rows=load()
        if args.capture:
            validate_original(args.capture)
    except (FifthLayerFixtureError,OSError) as exc:
        print("STOCK 26.2 FIFTH-LAYER FIXTURE UNQUALIFIED: "+str(exc),file=sys.stderr)
        return 2
    print(json.dumps({
        "kind":"original_26_2_finaldensity_fifth_layer_128_singlepoint_only",
        "new_input_rows":len(rows),"new_input_words":len(rows)*len(NEW_FIELDS),
        "left_ap2_operation":"MUL",
        "nested_gradient_from_y":GRADIENT_FROM_Y,
        "nested_gradient_to_y":GRADIENT_TO_Y,
        "outside_holder_target_class":"YClampedGradient",
        "outside_in_operation":"ADD",
        "outside_in_argument_bits":"0x"+ARG,
        "max_left_mapped_operation":"ABS",
        "max_right_mapped_operation":"ABS",
        "left_ap2_mul_rawbit_matches":128,
        "outside_add_rawbit_matches":128,
        "mapped_abs_rawbit_matches":256,
        "holder_forwarding_rawbit_matches":128,
        "nested_y_gradient_sample_matches":128,
        "source_free_fixture_sha256":SHA256,
        "original_owner_report_sha256":REPORT_SHA256,
        "native_end_to_end_finaldensity_qualified":False,
        **{gate:False for gate in fifth.GATES},
    },sort_keys=True))
    return 0


if __name__=="__main__":
    raise SystemExit(main())
