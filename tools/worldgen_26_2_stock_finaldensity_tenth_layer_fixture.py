#!/usr/bin/env python3
"""Strict genuine tenth 26.2 RangeChoice new-only fixture, finite samples.

Freeze exactly the real source-owning selector, in and out child raw bits.
Parent output is sourced independently from the immutable ninth TSV, never
copied into a new oracle. Ordinary range comparison is sample-only evidence,
not source-law or NoiseChunk/production qualification.
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

import worldgen_26_2_stock_final_density_tenth_layer as tenth

FIXTURE=Path(__file__).resolve().parents[1]/(
    "crates/world/helve-world-gen/tests/data/"
    "stock_finaldensity_tenth_layer_new_128_rawbits.tsv")
SHA256="5786ee42753215750163ec740220082b941e9d34adb76d145bfd43c21f9656f1"
REPORT_SHA256="b5bed75d54e2704718af4795407614ebd591330cb714263e61e6d7a21e8c3e8e"
REPORT_BYTES=45434
LINE=re.compile(rb"(?:[0-9a-f]{16}\t){2}[0-9a-f]{16}\n\Z")
CLASS=tenth.ninth.eighth.CLASS
SHAPE={
    "min_bits":"0xc12e848000000000",  # -1_000_000.0
    "max_bits":"0x3ff9000000000000",  # +1.5625
    "selector_class":CLASS+"Marker",
    "when_in_class":CLASS+"Ap2",
    "when_out_class":CLASS+"Ap2",
}


class TenthFixtureError(ValueError):
    """Genuine source-owned tenth finite fixture moved or unqualified."""


def number(word:str)->float:
    return struct.unpack(">d",bytes.fromhex(word))[0]


def load(path:Path=FIXTURE,*,require_sha:bool=True)->tuple[tuple[str,str,str],...]:
    raw=path.read_bytes()
    if len(raw)!=128*51 or (require_sha and
            hashlib.sha256(raw).hexdigest()!=SHA256):
        raise TenthFixtureError("true tenth new-only fixture bytes/SHA changed")
    old=tenth.prior.load()
    rows=raw.splitlines(keepends=True)
    if len(rows)!=128 or len(old)!=128:
        raise TenthFixtureError("tenth actual 4x32 observation count moved")
    result=[]
    arms={"in":0,"out":0}
    for i,row in enumerate(rows):
        if not LINE.fullmatch(row):
            raise TenthFixtureError("tenth real selector and Ap2 rawbits malformed")
        words=tuple(v.decode("ascii") for v in row[:-1].split(b"\t"))
        selector,when_in,when_out=words
        if any(not math.isfinite(number(w)) for w in words):
            raise TenthFixtureError("tenth actual child nonfinite: "+str(i))
        branch="in" if -1_000_000.0<=number(selector)<1.5625 else "out"
        expected=when_in if branch=="in" else when_out
        if expected!=old[i]:
            raise TenthFixtureError("original tenth real choice disagrees with frozen ninth: "+str(i))
        arms[branch]+=1
        result.append(words)
    if arms!={"in":68,"out":60}:
        raise TenthFixtureError("original tenth in/out actual branch coverage moved")
    return tuple(result)


def validate_original(path:Path)->None:
    raw=path.read_bytes()
    if len(raw)!=REPORT_BYTES or hashlib.sha256(raw).hexdigest()!=REPORT_SHA256:
        raise TenthFixtureError("authentic tenth original owner bytes/SHA moved")
    try:
        report=json.loads(raw)
        tenth.validate(report)
    except (ValueError,TypeError,KeyError,IndexError) as exc:
        raise TenthFixtureError("tenth source provenance/admission report rejected") from exc
    if any({k:v for k,v in s.items() if k!="world_seed_bits"}!=SHAPE
           for s in report["shapes"]):
        raise TenthFixtureError("real tenth Marker/Ap2 branch shapes moved")
    if report["rangechoice_candidate_telemetry"]!={
            "original_bounded_choice_samples":128,
            "naive_candidate_mismatches":0,
            "naive_candidate_first_mismatch_index":-1,
            "source_law_admitted":False}:
        raise TenthFixtureError("original tenth reported candidate coverage changed")
    new=load()
    old=tenth.prior.load()
    for i,(v,words) in enumerate(zip(report["vectors"],new,strict=True)):
        if any(v[k]!="0x"+w for k,w in zip(tenth.NEW_FIELDS,words,strict=True)):
            raise TenthFixtureError("original tenth actually new child rawbit moved: "+str(i))
        if v["old_rangechoice_bits"]!="0x"+old[i]:
            raise TenthFixtureError("original ninth previously frozen parent moved")


def main(argv:list[str]|None=None)->int:
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--capture",type=Path,
                   help="private completed tenth source-only original JVM JSON")
    args=p.parse_args(argv)
    try:
        rows=load()
        if args.capture is not None:
            validate_original(args.capture)
    except (TenthFixtureError,OSError) as exc:
        print("STOCK 26.2 TENTH FIXTURE OPEN: "+str(exc),file=sys.stderr)
        return 2
    print(json.dumps({
        "kind":"original_26_2_tenth_finite_source_owned_choice_only",
        "new_child_rows":len(rows),
        "genuinely_new_child_words":len(rows)*3,
        "original_in_range_samples":68,
        "original_out_of_range_samples":60,
        "source_owned_candidate_parity":128,
        "original_tenth_report_sha256":REPORT_SHA256,
        "new_only_fixture_sha256":SHA256,
        **{g:False for g in tenth.GATES},
    },sort_keys=True))
    return 0


if __name__=="__main__":
    raise SystemExit(main())
