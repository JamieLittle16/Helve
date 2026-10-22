#!/usr/bin/env python3
"""Authenticate seven NEW original Java 26.2 seventh-layer input words.

The sixth-layer old parents, older original root, source and actual report
stay independently immutable. Two real RangeChoice selectors happen to equal
the already admitted gradient on 128 points; never assert Java identity,
all-input equivalence or NoiseChunk caching/interpolation.
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

import worldgen_26_2_stock_final_density_seventh_layer as seventh

ROOT=Path(__file__).resolve().parents[1]
FIXTURE=ROOT/"crates/world/helve-world-gen/tests/data/stock_finaldensity_seventh_layer_new_128_rawbits.tsv"
SHA256="f749b5a0d6519de971a8a715d02e306111f04a697d7c4c3068aefc0f54c6bd92"
REPORT_SHA256="9b7adeb5d9fdec39e78668e5cd89d14e8134d31cd38ae8109444d23e72f16f4a"
REPORT_BYTES=87635
LINE=re.compile(r"[0-9a-f]{16}(?:\t[0-9a-f]{16}){6}\n\Z")
WIDTH=7*16+6+1
NEW_FIELDS=seventh.NEW_FIELDS
CLASS=seventh.CLASS
MIN="c04e000000000000"
MAX="4074100000000000"
ARG="bfb4000000000000"
ZERO="0000000000000000"
EXPECTED_SHAPE={
    "left_deep_enum_class":CLASS+"MulOrAdd$Type",
    "left_deep_op":"ADD",
    "left_deep_arg_bits":"0x"+ARG,
    "left_deep_child_class":CLASS+"Ap2",
    "left_choice_min_bits":"0x"+MIN,
    "left_choice_max_bits":"0x"+MAX,
    "left_choice_selector_class":CLASS+"HolderHolder",
    "left_choice_in_class":CLASS+"Noise",
    "left_choice_out_class":CLASS+"Constant",
    "right_choice_min_bits":"0x"+MIN,
    "right_choice_max_bits":"0x"+MAX,
    "right_choice_selector_class":CLASS+"HolderHolder",
    "right_choice_in_class":CLASS+"Noise",
    "right_choice_out_class":CLASS+"Constant",
}


class SeventhLayerFixtureError(ValueError):
    """Reject source owner evidence if *any* independent old anchor changes."""


def value(word:str)->float:
    return struct.unpack(">d",bytes.fromhex(word))[0]


def bits(number:float)->str:
    return struct.pack(">d",number).hex()


def known_selector(y:int)->str:
    # Original two HolderHolder selectors match this recorded gradient at
    # 128 finite samples only; no structural or all-input source claim.
    return bits(float(max(-4064,min(4062,y))))


def load(path:Path=FIXTURE,*,require_sha:bool=True)->tuple[tuple[str,...],...]:
    raw=path.read_bytes()
    if len(raw)!=128*WIDTH or (require_sha and
            hashlib.sha256(raw).hexdigest()!=SHA256):
        raise SeventhLayerFixtureError("original seventh-layer seven-word bytes/SHA changed")
    try:
        lines=raw.decode("ascii").splitlines(keepends=True)
    except UnicodeError as exc:
        raise SeventhLayerFixtureError("non-ASCII original seventh-layer fixture") from exc
    old=seventh.prior.load()
    points=seventh.sixth.fifth.fourth.third.second.final.input_rows()
    result=[]
    for i,line in enumerate(lines):
        if not LINE.fullmatch(line):
            raise SeventhLayerFixtureError("invalid new seventh-layer IEEE row "+str(i))
        child,ls,li,lo,rs,ri,ro=line[:-1].split("\t")
        if not all(math.isfinite(value(w)) for w in (child,ls,li,lo,rs,ri,ro)):
            raise SeventhLayerFixtureError("nonfinite original seventh-layer input "+str(i))
        parent=old[i]
        if bits(value(child)+value(ARG))!=parent[0]:
            raise SeventhLayerFixtureError("left deep ADD actual rawbits changed: "+str(i))
        selector=known_selector(points[i]["block_y"])
        if ls!=selector or rs!=selector or ls!=rs:
            raise SeventhLayerFixtureError("two independent selector outputs changed: "+str(i))
        if lo!=ZERO or ro!=ZERO:
            raise SeventhLayerFixtureError("actual zero Constant output changed: "+str(i))
        sel=value(ls)
        for actual_in,actual_out,expected in ((li,lo,parent[2]),(ri,ro,parent[3])):
            measured=actual_in if -60.0<=sel<321.0 else actual_out
            if measured!=expected:
                raise SeventhLayerFixtureError("original seventh RangeChoice branch changed: "+str(i))
        result.append((child,ls,li,lo,rs,ri,ro))
    if len(result)!=128:
        raise SeventhLayerFixtureError("seventh-layer original point count changed")
    return tuple(result)


def validate_original(path:Path)->None:
    raw=path.read_bytes()
    if len(raw)!=REPORT_BYTES or hashlib.sha256(raw).hexdigest()!=REPORT_SHA256:
        raise SeventhLayerFixtureError("private original seventh owner report SHA/bytes changed")
    try:
        report=json.loads(raw)
        seventh.validate(report)
    except (ValueError,TypeError,KeyError,IndexError) as exc:
        raise SeventhLayerFixtureError("actual seventh original owner report unqualified") from exc
    if report.get("source_text_included") is not False:
        raise SeventhLayerFixtureError("original source-free exclusion changed")
    if any({k:v for k,v in shape.items() if k!="world_seed_bits"}!=EXPECTED_SHAPE
           for shape in report["shapes"]):
        raise SeventhLayerFixtureError("actual seed-invariant seventh graph shape changed")
    for index,(v,new) in enumerate(zip(report["vectors"],load(),strict=True)):
        if tuple(v[k][2:] for k in NEW_FIELDS)!=new:
            raise SeventhLayerFixtureError("private seventh real input changed: "+str(index))


def main(argv:list[str]|None=None)->int:
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--capture",type=Path,help="optional exact 87635-byte original seventh JVM report")
    args=p.parse_args(argv)
    try:
        rows=load()
        if args.capture:
            validate_original(args.capture)
    except (SeventhLayerFixtureError,OSError) as exc:
        print("STOCK 26.2 SEVENTH-LAYER FIXTURE UNQUALIFIED: "+str(exc),file=sys.stderr)
        return 2
    print(json.dumps({
        "kind":"original_26_2_finaldensity_seventh_layer_128_singlepoint_only",
        "new_input_rows":len(rows),
        "new_input_words":len(rows)*len(NEW_FIELDS),
        "left_deep_add_rawbit_matches":128,
        "two_choice_branch_rawbit_matches":256,
        "two_holder_selector_sampled_gradient_matches":256,
        "two_constant_zero_output_matches":256,
        "two_actual_rangechoice_bounds_bits":["0x"+MIN,"0x"+MAX],
        "source_free_fixture_sha256":SHA256,
        "original_owner_report_sha256":REPORT_SHA256,
        **{gate:False for gate in seventh.GATES},
    },sort_keys=True))
    return 0


if __name__=="__main__":
    raise SystemExit(main())
