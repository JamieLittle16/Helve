#!/usr/bin/env python3
"""Pin only genuinely new finalDensity second-layer original 26.2 JVM words.

Four seeds x 32 SinglePointContexts; no recapture of root, inner or cell
oracles. The older 128 inner values remain independent bit-equality anchors.
Numerical evidence does NOT admit marker lifecycle or production worldgen.
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

import worldgen_26_2_stock_final_density_second_layer as second
import worldgen_26_2_stock_finaldensity_inner_fixture as prior

ROOT=Path(__file__).resolve().parents[1]
FIXTURE=ROOT/"crates/world/helve-world-gen/tests/data/stock_finaldensity_second_layer_new_128_rawbits.tsv"
SHA256="e684407be3e3d8ef5435c7518a0d4f5adbccae134684a730b216a11212874f4a"
ORIGINAL_JSON_SHA256="e12d01ccc9defc0c7d8a8a162bc7c7c890af7df6eb12e13656c59277f5eae9d9"
ORIGINAL_JSON_BYTES=66003
FIELDS=("mul_input_bits","selector_input_bits","outer_left_bits","outer_right_bits")
WIDTH=4*16+3+1
LINE=re.compile(r"[0-9a-f]{16}(?:\t[0-9a-f]{16}){3}\n\Z")
ARGUMENT_BITS="3fe47ae147ae147b"
ARGUMENT=struct.unpack(">d",bytes.fromhex(ARGUMENT_BITS))[0]
CLASS="net.minecraft.world.level.levelgen.DensityFunctions$"
EXPECTED_SHAPE={
    "mul_op_enum_class":CLASS+"MulOrAdd$Type",
    "mul_op":"MUL",
    "mul_argument_bits":"0x"+ARGUMENT_BITS,
    "mul_input_class":CLASS+"Marker",
    "selector_marker_enum_class":CLASS+"Marker$Type",
    "selector_marker_kind":"Interpolated",
    "selector_input_class":CLASS+"RangeChoice",
    "outside_ap2_enum_class":CLASS+"TwoArgumentSimpleFunction$Type",
    "outside_ap2_op":"ADD",
    "outside_left_class":CLASS+"Marker",
    "outside_right_class":CLASS+"MulOrAdd",
}


class SecondLayerFixtureError(ValueError):
    """The bound original 26.2 second-layer packet has changed."""


def value(word:str)->float:
    return struct.unpack(">d",bytes.fromhex(word))[0]


def bits(v:float)->str:
    return struct.pack(">d",v).hex()


def load(path:Path=FIXTURE,*,require_sha:bool=True)->tuple[tuple[str,...],...]:
    data=path.read_bytes()
    if len(data)!=128*WIDTH or (require_sha and
            hashlib.sha256(data).hexdigest()!=SHA256):
        raise SecondLayerFixtureError("second-layer fixture length/SHA changed")
    try:
        lines=data.decode("ascii").splitlines(keepends=True)
    except UnicodeError as exc:
        raise SecondLayerFixtureError("non-ASCII second-layer fixture") from exc
    old=prior.load()
    rows=[]
    for i,line in enumerate(lines):
        if not LINE.fullmatch(line):
            raise SecondLayerFixtureError("invalid source-free second-layer row: "+str(i))
        a,selector,left,right=line[:-1].split("\t")
        operands=(a,selector,left,right)
        if any(not math.isfinite(value(w)) for w in operands):
            raise SecondLayerFixtureError("nonfinite original second-layer input")
        if bits(value(a)*ARGUMENT)!=old[i][1]:
            raise SecondLayerFixtureError("MulOrAdd candidate JVM bits changed: "+str(i))
        if selector!=old[i][3]:
            raise SecondLayerFixtureError("Interpolated selector delegation changed: "+str(i))
        if bits(value(left)+value(right))!=old[i][5]:
            raise SecondLayerFixtureError("outside Ap2 ADD candidate bits changed: "+str(i))
        rows.append(operands)
    if len(rows)!=128:
        raise SecondLayerFixtureError("second-layer row count changed")
    return tuple(rows)


def validate_original(path:Path)->None:
    raw=path.read_bytes()
    if (len(raw)!=ORIGINAL_JSON_BYTES or
            hashlib.sha256(raw).hexdigest()!=ORIGINAL_JSON_SHA256):
        raise SecondLayerFixtureError("original owner second-layer JSON identity changed")
    try:
        report=json.loads(raw)
        second.validate(report)
    except (ValueError,TypeError,KeyError,IndexError) as exc:
        raise SecondLayerFixtureError("original owner report rejected by source validator") from exc
    for shape in report["shapes"]:
        if {k:v for k,v in shape.items() if k!="world_seed_bits"}!=EXPECTED_SHAPE:
            raise SecondLayerFixtureError("seed-invariant original 26.2 second-layer shape changed")
    rows=load()
    for i,(vector,expected) in enumerate(zip(report["vectors"],rows,strict=True)):
        if tuple(vector[k][2:] for k in FIELDS)!=expected:
            raise SecondLayerFixtureError("owner second-layer new operand mismatch: "+str(i))


def main(argv:list[str]|None=None)->int:
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--capture",type=Path,
                   help="Optional exact 66,003-byte original source-free owner receipt")
    args=p.parse_args(argv)
    try:
        rows=load()
        if args.capture is not None:
            validate_original(args.capture)
    except (SecondLayerFixtureError,OSError) as exc:
        print("STOCK 26.2 SECOND LAYER FIXTURE UNQUALIFIED: "+str(exc),file=sys.stderr)
        return 2
    print(json.dumps({
        "kind":"observed_26_2_finaldensity_second_layer_128_singlepoint_only",
        "new_operand_rows":len(rows),"new_operand_words":len(rows)*len(FIELDS),
        "muloradd_operation":"MUL","muloradd_argument_bits":"0x"+ARGUMENT_BITS,
        "outside_ap2_operation":"ADD",
        "muloradd_rawbit_parity":128,"outside_ap2_rawbit_parity":128,
        "selector_interpolated_delegation_rawbit_parity":128,
        "compact_source_free_fixture_sha256":SHA256,
        "original_owner_report_sha256":ORIGINAL_JSON_SHA256,
        **{gate:False for gate in second.GATES},
        "end_to_end_final_density_qualified":False,
    },sort_keys=True))
    return 0


if __name__=="__main__":
    raise SystemExit(main())
