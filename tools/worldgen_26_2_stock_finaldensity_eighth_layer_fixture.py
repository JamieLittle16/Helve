#!/usr/bin/env python3
"""Exact 26.2 original JVM eighth-layer operands, no repeated old oracle words.

The original Java Ap2 MUL returned +0 instead of IEEE -0 on four negative
right operands at Y=320. The specific positive-zero shortcut candidate fits
128/128 raw words, but the general source body and stock NoiseChunk are NOT
admitted by this finite SinglePointContext fixture.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import struct
import sys
from collections import Counter
from pathlib import Path

import worldgen_26_2_stock_final_density_eighth_layer as eighth

ROOT=Path(__file__).resolve().parents[1]
FIXTURE=ROOT/"crates/world/helve-world-gen/tests/data/stock_finaldensity_eighth_layer_new_128_rawbits.tsv"
SHA256="4fc059ebcfb74cf3e0b155460fca8b144c975aaafc653f6da51a913c68fc2c6e"
REPORT_SHA256="3fae6fa522856983894335830a7f54689bf2534e66c446f6f73f3a3ed1548b58"
REPORT_BYTES=67230
LINE=re.compile(r"[0-9a-f]{16}\t[0-9a-f]{16}\n\Z")
ZERO="0000000000000000"
SIGNED_ZERO="8000000000000000"
ONE="3ff0000000000000"
ONE_SIXTEENTH="3fb0000000000000"
CLASS=eighth.CLASS
EXPECTED_SHAPE={
    "deep_ap2_enum_class":CLASS+"TwoArgumentSimpleFunction$Type",
    "deep_ap2_op":"MUL",
    "deep_ap2_left_class":CLASS+"YClampedGradient",
    "deep_ap2_right_class":CLASS+"MulOrAdd",
    "left_target_class":CLASS+"YClampedGradient",
    "left_from_y":-4064,
    "left_to_y":4062,
    "left_from_value_bits":"0xc0afc00000000000",
    "left_to_value_bits":"0x40afbc0000000000",
    "right_target_class":CLASS+"YClampedGradient",
    "right_from_y":-4064,
    "right_to_y":4062,
    "right_from_value_bits":"0xc0afc00000000000",
    "right_to_value_bits":"0x40afbc0000000000",
}


class EighthFixtureError(ValueError):
    """Real original-JVM raw-bit parity cannot be silently promoted."""


def number(word:str)->float:
    return struct.unpack(">d",bytes.fromhex(word))[0]


def word(value:float)->str:
    return struct.pack(">d",value).hex()


def load(path:Path=FIXTURE,*,require_sha:bool=True)->tuple[tuple[str,str],...]:
    data=path.read_bytes()
    if len(data)!=128*34 or (require_sha and
            hashlib.sha256(data).hexdigest()!=SHA256):
        raise EighthFixtureError("authentic eighth two-new-word fixture bytes/SHA moved")
    try:
        lines=data.decode("ascii").splitlines(keepends=True)
    except UnicodeError as exc:
        raise EighthFixtureError("non-ASCII original IEEE fixture") from exc
    old=eighth.prior.load()
    points=eighth.seventh.sixth.fifth.fourth.third.second.final.input_rows()
    result=[]
    zeros=[]
    naive_mismatches=[]
    left_distribution=Counter()
    for i,line in enumerate(lines):
        if not LINE.fullmatch(line):
            raise EighthFixtureError("original eighth actual operands malformed: "+str(i))
        left,right=line[:-1].split("\t")
        a,b=number(left),number(right)
        if not math.isfinite(a) or not math.isfinite(b):
            raise EighthFixtureError("nonfinite eighth original child: "+str(i))
        left_distribution[left]+=1
        expected=old[i][0]
        naive=word(a*b)
        actual=ZERO if left==ZERO else naive
        if actual!=expected:
            raise EighthFixtureError("original source-owned Ap2 +zero candidate mismatch: "+str(i))
        if naive!=expected:
            naive_mismatches.append(i)
            if left!=ZERO or naive!=SIGNED_ZERO or expected!=ZERO or not b<0:
                raise EighthFixtureError("non-positive-zero original Ap2 discrepancy: "+str(i))
            zeros.append(i)
        # This is precisely a 128-row observation, NOT a source law for all Y.
        y=points[i]["block_y"]
        sample_left=ZERO if y==320 else ONE_SIXTEENTH if y==255 else ONE
        if left!=sample_left:
            raise EighthFixtureError("original sampled Y-gradient child changed: "+str(i))
        result.append((left,right))
    if len(result)!=128 or zeros!=[8,40,72,104] or left_distribution!={
            ONE:112,ONE_SIXTEENTH:12,ZERO:4}:
        raise EighthFixtureError("bounded exact original Ap2 positive-zero witnesses changed")
    return tuple(result)


def validate_original(path:Path)->None:
    raw=path.read_bytes()
    if len(raw)!=REPORT_BYTES or hashlib.sha256(raw).hexdigest()!=REPORT_SHA256:
        raise EighthFixtureError("authentic eighth source-owned report SHA/bytes moved")
    try:
        report=json.loads(raw)
        eighth.validate(report)
    except (ValueError,TypeError,KeyError,IndexError) as exc:
        raise EighthFixtureError("real eighth source-owning provenance rejected") from exc
    if report.get("source_text_included") is not False:
        raise EighthFixtureError("original eighth source-free exclusion changed")
    if any({k:v for k,v in shape.items() if k!="world_seed_bits"}!=EXPECTED_SHAPE
           for shape in report["shapes"]):
        raise EighthFixtureError("original eighth independent runtime record shape changed")
    observation=report["ap2_candidate_observation"]
    expected={
        "candidate_operand_pairs_checked":128,
        "raw_ieee_mismatch_count":4,
        "raw_ieee_first_mismatch_index":8,
        "positive_zero_shortcircuit_mismatch_count":0,
        "positive_zero_shortcircuit_first_mismatch_index":-1,
        "source_law_admitted":False,
    }
    if observation!=expected:
        raise EighthFixtureError("original actual signed-zero candidate telemetry changed")
    for i,(v,inputs) in enumerate(zip(report["vectors"],load(),strict=True)):
        if tuple(v[k][2:] for k in eighth.NEW_FIELDS)!=inputs:
            raise EighthFixtureError("actual eighth new operand changed: "+str(i))
        if v["left_target_bits"]!=v["left_selector_old_bits"] or (
                v["right_target_bits"]!=v["right_selector_old_bits"]):
            raise EighthFixtureError("independent original Holder target forwarding changed")


def main(argv:list[str]|None=None)->int:
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--capture",type=Path,help="optional private eighth original-JVM source-free receipt")
    args=p.parse_args(argv)
    try:
        inputs=load()
        if args.capture:
            validate_original(args.capture)
    except (EighthFixtureError,OSError) as exc:
        print("STOCK 26.2 EIGHTH FIXTURE UNQUALIFIED: "+str(exc),file=sys.stderr)
        return 2
    print(json.dumps({
        "kind":"original_26_2_finaldensity_eighth_layer_128_singlepoint_only",
        "new_input_rows":len(inputs),"new_input_words":256,
        "ap2_mul_positive_zero_candidate_matches":128,
        "naive_ieee_signed_zero_mismatches":4,
        "two_original_holder_target_forwarding_matches":256,
        "original_owner_report_sha256":REPORT_SHA256,
        "source_free_fixture_sha256":SHA256,
        **{gate:False for gate in eighth.GATES},
    },sort_keys=True))
    return 0


if __name__=="__main__":
    raise SystemExit(main())
