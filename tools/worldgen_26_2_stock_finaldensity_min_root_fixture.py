#!/usr/bin/env python3
"""Freeze the real stock 26.2 Ap2 MIN root combination only.

The 128 source-free MIN operands were independently observed as Mapped SQUEEZE
(Marker) and HolderHolder(RangeChoice). This fixture is *not* an independent
Rust evaluation of those children, not a source review of Java's MIN branches,
not a NoiseChunk-context oracle, and grants no production admission.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import struct
import sys
from pathlib import Path

import worldgen_26_2_stock_final_density_root_semantics as root
import worldgen_26_2_stock_final_density_singlepoint_fixture as frozen

ROOT=Path(__file__).resolve().parents[1]
FIXTURE=ROOT/"crates/world/helve-world-gen/tests/data/stock_finaldensity_min_root_128_rawbits.tsv"
FIXTURE_SHA256="5693d6d923ccd3fd29847350c825556349ba1f5eb1a5a7671537d8328ac485fd"
ORIGINAL_JSON_SHA256="2c8094e2c561f13aff9a392081bf0f7c3fa41b94f1c8d3d922c308269db78e8d"
ORIGINAL_JSON_BYTES=38630
LINE=re.compile(r"([0-9a-f]{16})\t([0-9a-f]{16})\t([0-9a-f]{16})\n\Z")
HOLDER_WINS=(21,66,67,87)


class MinRootFixtureError(ValueError):
    """Source-free observed Ap2 MIN operand evidence changed."""


def read_words(path:Path=FIXTURE,*,enforce_sha:bool=True)->tuple[tuple[str,str,str],...]:
    raw=path.read_bytes()
    if len(raw)!=128*51 or (enforce_sha and
        hashlib.sha256(raw).hexdigest()!=FIXTURE_SHA256):
        raise MinRootFixtureError("original JVM MIN operand fixture byte length/SHA differs")
    try:
        lines=raw.decode("ascii").splitlines(keepends=True)
    except UnicodeDecodeError as exc:
        raise MinRootFixtureError("non-ASCII JVM MIN root operand fixture") from exc
    if len(lines)!=128:
        raise MinRootFixtureError("expected 128 original JVM root rows")
    root_bits=frozen.load_bits()
    hits=[]
    triples=[]
    for i,line in enumerate(lines):
        m=LINE.fullmatch(line)
        if m is None:
            raise MinRootFixtureError("malformed stock MIN root row "+str(i))
        a,b,final=m.groups()
        # The actual original JVM observation covers finite non-zero inputs,
        # not source-law reviewed NaN or signed-zero MIN handling.
        va,vb,vr=(struct.unpack(">d",bytes.fromhex(word))[0]
                  for word in (a,b,final))
        if not all(map(lambda x: x==x and abs(x)!=float("inf") and x!=0.0,(va,vb,vr))):
            raise MinRootFixtureError("outside observed finite nonzero domain")
        winner=a if va<=vb else b
        if winner!=final or final!=root_bits[i]:
            raise MinRootFixtureError("stock root MIN child/output mismatch "+str(i))
        if va>vb:
            hits.append(i)
        triples.append((a,b,final))
    if tuple(hits)!=HOLDER_WINS:
        raise MinRootFixtureError("actual stock MIN holder-winner positions changed")
    return tuple(triples)


def validate_original(path:Path)->None:
    raw=path.read_bytes()
    if len(raw)!=ORIGINAL_JSON_BYTES or hashlib.sha256(raw).hexdigest()!=ORIGINAL_JSON_SHA256:
        raise MinRootFixtureError("exact original user-owned 26.2 root JSON SHA differs")
    try:
        capture=json.loads(raw)
        root.validate(capture)
    except (ValueError,KeyError,TypeError) as exc:
        raise MinRootFixtureError("original source-free root reviewer report unqualified") from exc
    expected=read_words()
    for index,(row,want) in enumerate(zip(capture["vectors"],expected,strict=True)):
        got=tuple(row[key][2:] for key in
                  ("mapped_bits","holder_bits","final_density_bits"))
        if got!=want:
            raise MinRootFixtureError("original stock root child mismatch "+str(index))
    if any(s["ap2_operator"]!="MIN" or
           s["mapped_transform"]!="SQUEEZE" or
           not s["mapped_input_class"].endswith("$Marker") or
           not s["holder_target_class"].endswith("$RangeChoice")
           for s in capture["shapes"]):
        raise MinRootFixtureError("original root has different operation or children")


def main(argv:list[str]|None=None)->int:
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--capture",type=Path,
                   help="Optional EXACT original user-provided 38,630-byte JSON; no private Java source")
    args=p.parse_args(argv)
    try:
        words=read_words()
        if args.capture is not None:
            validate_original(args.capture)
    except (MinRootFixtureError,OSError) as exc:
        print("STOCK 26.2 MIN ROOT OPERANDS UNQUALIFIED: "+str(exc),file=sys.stderr)
        return 2
    print(json.dumps({
        "observed_min_root_operand_pairs":len(words),
        "java_root_operator":"MIN","mapped_transform":"SQUEEZE",
        "mapped_input":"Marker","holder_target":"RangeChoice",
        "holder_wins":len(HOLDER_WINS),
        "fixture_sha256":FIXTURE_SHA256,"original_source_free_report_sha256":ORIGINAL_JSON_SHA256,
        "full_final_density_rust_parity_qualified":False,
        "independent_var_sem_admitted":False,"production_worldgen_enabled":False,
    },sort_keys=True))
    return 0


if __name__=="__main__":
    raise SystemExit(main())
