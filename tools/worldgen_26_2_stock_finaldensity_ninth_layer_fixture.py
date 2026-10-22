#!/usr/bin/env python3
"""Authentic ninth-layer stock JVM: ONE new RangeChoice child IEEE word/point.

Original 26.2 source owner and the two independently frozen eighth parents
are checked without copying previous root, parent, noise, or source oracles.
These finite SinglePointContext checks NEVER admit a full source law.
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

import worldgen_26_2_stock_final_density_ninth_layer as ninth

FIXTURE=Path(__file__).resolve().parents[1]/(
    "crates/world/helve-world-gen/tests/data/"
    "stock_finaldensity_ninth_layer_new_128_rawbits.tsv")
SHA256="1cb8c4ddd35fec84d5a44adfaf4281dcbe3caf9fd30cbe00eb3e8f0a7844ae9d"
REPORT_SHA256="66716c9d06ac1eb72f10c2648c9ccc56f68b1d21ceb9bba346de5c15e1bf88d1"
REPORT_BYTES=42445
WORD_LINE=re.compile(rb"[0-9a-f]{16}\n\Z")
CLASS=ninth.CLASS
SHAPE={
    "left_from_y":240,
    "left_to_y":256,
    "left_from_value_bits":"0x3ff0000000000000",
    "left_to_value_bits":"0x0000000000000000",
    "right_enum_class":CLASS+"MulOrAdd$Type",
    "right_op":"ADD",
    "right_arg_bits":"0x3fb4000000000000",
    "right_child_class":CLASS+"RangeChoice",
}

class NinthFixtureError(ValueError):
    """Bounded ninth source owner/finite native candidate not qualified."""


def ieee(value:float)->str:
    return struct.pack(">d",value).hex()


def number(word:str)->float:
    return struct.unpack(">d",bytes.fromhex(word))[0]


def gradient(y:int)->str:
    if y<=240:
        return ieee(1.0)
    if y>=256:
        return ieee(0.0)
    return ieee(1.0-(y-240)/16.0)


def load(path:Path=FIXTURE,*,require_sha:bool=True)->tuple[str,...]:
    raw=path.read_bytes()
    if len(raw)!=128*17 or (require_sha and
            hashlib.sha256(raw).hexdigest()!=SHA256):
        raise NinthFixtureError("original ninth source-free new words length/SHA changed")
    rows=raw.splitlines(keepends=True)
    old=ninth.prior.load()
    points=ninth.eighth.seventh.sixth.fifth.fourth.third.second.final.input_rows()
    if len(rows)!=128 or len(old)!=128 or len(points)!=128:
        raise NinthFixtureError("source-bounded ninth old/new point count moved")
    result=[]
    for i,row in enumerate(rows):
        if WORD_LINE.fullmatch(row) is None:
            raise NinthFixtureError("new ninth raw IEEE syntax changed: "+str(i))
        child=row[:-1].decode("ascii")
        v=number(child)
        if not math.isfinite(v):
            raise NinthFixtureError("new ninth source-owned child not finite")
        left,right=old[i]
        if gradient(points[i]["block_y"])!=left:
            raise NinthFixtureError("real ninth sampled Y-gradient changed: "+str(i))
        if ieee(v+0.078125)!=right:
            raise NinthFixtureError("actual ninth MulOrAdd ADD child/parent mismatch: "+str(i))
        result.append(child)
    return tuple(result)


def validate_original(path:Path)->None:
    raw=path.read_bytes()
    if len(raw)!=REPORT_BYTES or hashlib.sha256(raw).hexdigest()!=REPORT_SHA256:
        raise NinthFixtureError("authentic ninth original-JVM report bytes/SHA changed")
    try:
        report=json.loads(raw)
        ninth.validate(report)
    except (ValueError,TypeError,KeyError,IndexError) as exc:
        raise NinthFixtureError("ninth source-owner report/provenance unqualified") from exc
    if any({k:v for k,v in s.items() if k!="world_seed_bits"}!=SHAPE
           for s in report["shapes"]):
        raise NinthFixtureError("actual ninth original graph record moved")
    if report["muloradd_candidate_telemetry"]!={
            "naive_muloradd_first_mismatch_index":-1,
            "naive_muloradd_mismatch_count":0,
            "old_parent_anchored_points":128,
            "source_law_admitted":False}:
        raise NinthFixtureError("source-owned ninth naive arithmetic report changed")
    for i,(v,child) in enumerate(zip(report["vectors"],load(),strict=True)):
        if v["new_right_child_bits"]!="0x"+child:
            raise NinthFixtureError("source-owned ninth NEW child bit changed: "+str(i))
        if v["old_left_gradient_bits"]!="0x"+ninth.prior.load()[i][0] or (
                v["old_right_muloradd_bits"]!="0x"+ninth.prior.load()[i][1]):
            raise NinthFixtureError("independently frozen eighth parent mismatch")


def main(argv:list[str]|None=None)->int:
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--capture",type=Path,help="optional private authentic ninth source-free JSON receipt")
    args=p.parse_args(argv)
    try:
        rows=load()
        if args.capture is not None:
            validate_original(args.capture)
    except (NinthFixtureError,OSError) as exc:
        print("STOCK 26.2 NINTH FIXTURE OPEN: "+str(exc),file=sys.stderr)
        return 2
    print(json.dumps({
        "kind":"original_26_2_ninth_singlepoint_candidate_only",
        "new_child_rawbit_words":len(rows),
        "real_gradient_and_add_source_numeric_matches":128,
        "real_eighth_parent_anchor_matches":256,
        "original_ninth_report_sha256":REPORT_SHA256,
        "new_source_free_fixture_sha256":SHA256,
        **{gate:False for gate in ninth.GATES},
    },sort_keys=True))
    return 0


if __name__=="__main__":
    raise SystemExit(main())
