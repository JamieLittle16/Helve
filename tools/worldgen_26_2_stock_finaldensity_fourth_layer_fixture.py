#!/usr/bin/env python3
"""Pin only seven NEW original stock 26.2 finalDensity fourth-layer words.

Four seeds, 128 genuine SinglePointContexts, four earlier independently
frozen third-layer outputs used ONLY as equality anchors. The graph's
unexpanded original children are not native, source-admitted or production.
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

import worldgen_26_2_stock_final_density_fourth_layer as fourth

ROOT=Path(__file__).resolve().parents[1]
FIXTURE=ROOT/"crates/world/helve-world-gen/tests/data/stock_finaldensity_fourth_layer_new_128_rawbits.tsv"
SHA256="149ebe4d87dbbf2ebc1d40bc5149656b5e50ae16db16bf9d9210f3510b37543c"
REPORT_SHA256="fb4d7207276311b6853e6bb25d407137417111432d1b3a937c623a5ab866d19f"
REPORT_BYTES=97865
WIDTH=7*16+6+1
LINE=re.compile(r"[0-9a-f]{16}(?:\t[0-9a-f]{16}){6}\n\Z")
NEW_FIELDS=fourth.NEW_FIELDS
CLASS=fourth.DENSITY
PARAM="3fbe000000000000"
BOUNDS=("c04e000000000000","4074100000000000")
EXPECTED_SHAPE={
    "left_mul_enum_class":CLASS+"MulOrAdd$Type",
    "left_mul_op":"ADD",
    "left_mul_argument_bits":"0x"+PARAM,
    "left_mul_input_class":CLASS+"Ap2",
    "nested_holder_target_class":CLASS+"YClampedGradient",
    "outside_range_selector_class":CLASS+"HolderHolder",
    "outside_range_in_class":CLASS+"MulOrAdd",
    "outside_range_out_class":CLASS+"Constant",
    "outside_range_min_bits":"0x"+BOUNDS[0],
    "outside_range_max_bits":"0x"+BOUNDS[1],
    "right_ap2_enum_class":CLASS+"TwoArgumentSimpleFunction$Type",
    "right_ap2_op":"MAX",
    "right_ap2_left_class":CLASS+"Mapped",
    "right_ap2_right_class":CLASS+"Mapped",
}


class FourthLayerFixtureError(ValueError):
    """Cannot admit original fourth-layer source-free evidence."""


def number(word:str)->float:
    return struct.unpack(">d",bytes.fromhex(word))[0]


def bits(value:float)->str:
    return struct.pack(">d",value).hex()


def load(path:Path=FIXTURE,*,require_sha:bool=True)->tuple[tuple[str,...],...]:
    raw=path.read_bytes()
    if len(raw)!=128*WIDTH or (require_sha and
            hashlib.sha256(raw).hexdigest()!=SHA256):
        raise FourthLayerFixtureError("fourth-layer source-free fixture bytes/SHA changed")
    try:
        lines=raw.decode("ascii").splitlines(keepends=True)
    except UnicodeError as exc:
        raise FourthLayerFixtureError("non-ASCII original fixture") from exc
    previous=fourth.prior.load()
    result=[]
    in_count=out_count=left=right=tie=0
    for index,line in enumerate(lines):
        if not LINE.fullmatch(line):
            raise FourthLayerFixtureError("invalid seven-word original row "+str(index))
        a,y,selector,in_value,out_value,max_left,max_right=line[:-1].split("\t")
        if not all(math.isfinite(number(v)) for v in
                (a,y,selector,in_value,out_value,max_left,max_right)):
            raise FourthLayerFixtureError("nonfinite original fourth-layer word")
        old=previous[index]
        # Exact old owner outputs: left wrapped MulOrAdd, nested HolderHolder
        # and outside Interpolated RangeChoice, and the right Ap2 result.
        if bits(number(a)+number(PARAM))!=old[0]:
            raise FourthLayerFixtureError("original ADD(0.1171875) output changed: "+str(index))
        if y!=old[1]:
            raise FourthLayerFixtureError("nested HolderHolder forwarding changed: "+str(index))
        selected=in_value if number(BOUNDS[0])<=number(selector)<number(BOUNDS[1]) else out_value
        if selected!=old[4]:
            raise FourthLayerFixtureError("outside original RangeChoice changed: "+str(index))
        in_count+=int(selected==in_value and number(BOUNDS[0])<=number(selector)<number(BOUNDS[1]))
        out_count+=int(not number(BOUNDS[0])<=number(selector)<number(BOUNDS[1]))
        if out_value!=bits(0.0):
            raise FourthLayerFixtureError("outside Constant(+0) changed: "+str(index))
        mx=max(number(max_left),number(max_right))
        if bits(mx)!=old[5]:
            raise FourthLayerFixtureError("right Ap2 MAX raw bits differ: "+str(index))
        left+=int(number(max_left)>number(max_right))
        right+=int(number(max_left)<number(max_right))
        tie+=int(number(max_left)==number(max_right))
        result.append((a,y,selector,in_value,out_value,max_left,max_right))
    if len(result)!=128 or (in_count,out_count,left,right,tie)!=(108,20,44,64,20):
        raise FourthLayerFixtureError("fourth-layer observed branch distribution moved")
    return tuple(result)


def validate_original(path:Path)->None:
    raw=path.read_bytes()
    if len(raw)!=REPORT_BYTES or hashlib.sha256(raw).hexdigest()!=REPORT_SHA256:
        raise FourthLayerFixtureError("original private fourth-layer owner report identity changed")
    try:
        report=json.loads(raw)
        fourth.validate(report)
    except (ValueError,KeyError,TypeError,IndexError) as exc:
        raise FourthLayerFixtureError("original fourth-layer owner validator rejected") from exc
    if any({k:v for k,v in shape.items() if k!="world_seed_bits"}!=EXPECTED_SHAPE
           for shape in report["shapes"]):
        raise FourthLayerFixtureError("original seed-invariant fourth-layer shape moved")
    rows=load()
    for i,(vector,words) in enumerate(zip(report["vectors"],rows,strict=True)):
        if tuple(vector[k][2:] for k in NEW_FIELDS)!=words:
            raise FourthLayerFixtureError("new source-free fourth-layer input moved: "+str(i))


def main(argv:list[str]|None=None)->int:
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--capture",type=Path,
                   help="Optional original fourth-layer private source-free JSON")
    args=p.parse_args(argv)
    try:
        rows=load()
        if args.capture is not None:
            validate_original(args.capture)
    except (FourthLayerFixtureError,OSError) as exc:
        print("STOCK 26.2 FOURTH-LAYER FIXTURE UNQUALIFIED: "+str(exc),file=sys.stderr)
        return 2
    print(json.dumps({
        "kind":"original_26_2_finaldensity_fourth_layer_128_singlepoint_only",
        "new_child_input_rows":len(rows),
        "new_child_input_words":len(rows)*len(NEW_FIELDS),
        "left_mul_or_add":"ADD",
        "left_add_argument_bits":"0x"+PARAM,
        "nested_holder_target_type":"YClampedGradient",
        "outside_range_min_inclusive":-60,
        "outside_range_max_exclusive":321,
        "outside_range_in":108,"outside_range_out":20,
        "right_ap2_operation":"MAX",
        "right_max_left_wins":44,"right_max_right_wins":64,"right_max_ties":20,
        "raw_bit_parity":128,
        "source_free_fixture_sha256":SHA256,
        "original_owner_report_sha256":REPORT_SHA256,
        "full_final_density_qualified":False,
        **{gate:False for gate in fourth.GATES},
    },sort_keys=True))
    return 0


if __name__=="__main__":
    raise SystemExit(main())
