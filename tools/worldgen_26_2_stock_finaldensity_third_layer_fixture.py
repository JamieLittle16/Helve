#!/usr/bin/env python3
"""Pin only NEW source-owning original 26.2 third-layer finalDensity inputs.

128 JVM SinglePointContexts, four seeds, and six genuinely new child words.
Earlier 128 second-layer words are independent immutable output anchors.
This is finite-sample evidence, NOT source-law/NoiseChunk/production admission.
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

import worldgen_26_2_stock_final_density_third_layer as third

ROOT=Path(__file__).resolve().parents[1]
FIXTURE=ROOT/"crates/world/helve-world-gen/tests/data/stock_finaldensity_third_layer_new_128_rawbits.tsv"
SHA256="bacf33b5d8274083ad3e5ff5a557d66dc9c999c07d9f358b0e06e1978fe79181"
ORIGINAL_JSON_SHA256="7379c8e0282f642b4780be40810d2dcd871d06a2f5bacdcffaba3b264248dd81"
ORIGINAL_JSON_BYTES=92321
FIELDS=third.NEW_FIELDS
WIDTH=6*16+5+1
LINE=re.compile(r"[0-9a-f]{16}(?:\t[0-9a-f]{16}){5}\n\Z")
LOW=-60.0
HIGH=321.0
ARGUMENT_BITS="3ff8000000000000"
ARGUMENT=struct.unpack(">d",bytes.fromhex(ARGUMENT_BITS))[0]
CLASS=third.DENSITY
EXPECTED_SHAPE={
    "left_marker_enum_class":CLASS+"Marker$Type",
    "left_marker_kind":"BlendDensity",
    "left_marker_wrapped_class":CLASS+"MulOrAdd",
    "nested_selector_class":CLASS+"HolderHolder",
    "nested_in_class":CLASS+"Noise",
    "nested_out_class":CLASS+"Constant",
    "nested_min_inclusive_bits":"0xc04e000000000000",
    "nested_max_exclusive_bits":"0x4074100000000000",
    "outside_marker_enum_class":CLASS+"Marker$Type",
    "outside_marker_kind":"Interpolated",
    "outside_marker_wrapped_class":CLASS+"RangeChoice",
    "outside_mul_enum_class":CLASS+"MulOrAdd$Type",
    "outside_mul_op":"MUL",
    "outside_mul_argument_bits":"0x"+ARGUMENT_BITS,
    "outside_mul_wrapped_class":CLASS+"Ap2",
}


class ThirdLayerFixtureError(ValueError):
    """Actual original 26.2 third-layer fixture cannot be admitted."""


def value(word:str)->float:
    return struct.unpack(">d",bytes.fromhex(word))[0]


def bits(v:float)->str:
    return struct.pack(">d",v).hex()


def load(path:Path=FIXTURE,*,require_sha:bool=True)->tuple[tuple[str,...],...]:
    data=path.read_bytes()
    if len(data)!=128*WIDTH or (require_sha and
            hashlib.sha256(data).hexdigest()!=SHA256):
        raise ThirdLayerFixtureError("third-layer original fixture bytes/SHA changed")
    try:
        lines=data.decode("ascii").splitlines(keepends=True)
    except UnicodeError as exc:
        raise ThirdLayerFixtureError("non-ASCII third-layer original fixture") from exc
    previous=third.prior.load()
    rows=[]
    inside=outside=0
    for i,line in enumerate(lines):
        if not LINE.fullmatch(line):
            raise ThirdLayerFixtureError("invalid six-word third-layer row: "+str(i))
        first,selector,noise,constant,marker,mul=line[:-1].split("\t")
        if any(not math.isfinite(value(w)) for w in
               (first,selector,noise,constant,marker,mul)):
            raise ThirdLayerFixtureError("nonfinite original third-layer input")
        if (first,marker)!= (previous[i][0],previous[i][2]):
            raise ThirdLayerFixtureError("original third-layer Marker delegation moved: "+str(i))
        if constant!=bits(-1.0):
            raise ThirdLayerFixtureError("nested out-of-range -1 witness changed: "+str(i))
        winner=noise if LOW<=value(selector)<HIGH else constant
        if winner!=previous[i][1]:
            raise ThirdLayerFixtureError("third-layer nested RangeChoice bytes changed: "+str(i))
        inside+=int(LOW<=value(selector)<HIGH)
        outside+=int(not LOW<=value(selector)<HIGH)
        if bits(value(mul)*ARGUMENT)!=previous[i][3]:
            raise ThirdLayerFixtureError("original third-layer MUL 1.5 bits changed: "+str(i))
        rows.append((first,selector,noise,constant,marker,mul))
    if len(rows)!=128 or (inside,outside)!=(108,20):
        raise ThirdLayerFixtureError("original third-layer branch distribution changed")
    return tuple(rows)


def validate_original(path:Path)->None:
    raw=path.read_bytes()
    if (len(raw)!=ORIGINAL_JSON_BYTES or
            hashlib.sha256(raw).hexdigest()!=ORIGINAL_JSON_SHA256):
        raise ThirdLayerFixtureError("private original third-layer JSON identity changed")
    try:
        report=json.loads(raw)
        third.validate(report)
    except (ValueError,KeyError,IndexError,TypeError) as exc:
        raise ThirdLayerFixtureError("original third-layer owner validator rejected") from exc
    for s in report["shapes"]:
        if {k:v for k,v in s.items() if k!="world_seed_bits"}!=EXPECTED_SHAPE:
            raise ThirdLayerFixtureError("actual original seed-invariant third-layer shape changed")
    rows=load()
    for i,(v,words) in enumerate(zip(report["vectors"],rows,strict=True)):
        if tuple(v[k][2:] for k in FIELDS)!=words:
            raise ThirdLayerFixtureError("third-layer original new input changed: "+str(i))


def main(argv:list[str]|None=None)->int:
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--capture",type=Path,
                   help="Optional private 92,321-byte original source-free third-layer JSON")
    args=p.parse_args(argv)
    try:
        rows=load()
        if args.capture is not None:
            validate_original(args.capture)
    except (ThirdLayerFixtureError,OSError) as exc:
        print("STOCK 26.2 THIRD-LAYER FIXTURE UNQUALIFIED: "+str(exc),file=sys.stderr)
        return 2
    print(json.dumps({
        "kind":"original_26_2_finaldensity_third_layer_128_singlepoint_only",
        "new_child_input_rows":len(rows),"new_child_input_words":len(rows)*len(FIELDS),
        "left_marker_kind":"BlendDensity",
        "outside_marker_kind":"Interpolated",
        "nested_range_min_inclusive":LOW,
        "nested_range_max_exclusive":HIGH,
        "nested_range_in_count":108,"nested_range_out_count":20,
        "outside_muloradd_operation":"MUL",
        "outside_muloradd_argument_bits":"0x"+ARGUMENT_BITS,
        "nested_rangechoice_rawbit_parity":128,
        "outside_muloradd_rawbit_parity":128,
        "two_marker_delegations_rawbit_parity":128,
        "source_free_fixture_sha256":SHA256,
        "original_owner_report_sha256":ORIGINAL_JSON_SHA256,
        **{gate:False for gate in third.GATES},
        "end_to_end_final_density_qualified":False,
    },sort_keys=True))
    return 0


if __name__=="__main__":
    raise SystemExit(main())
