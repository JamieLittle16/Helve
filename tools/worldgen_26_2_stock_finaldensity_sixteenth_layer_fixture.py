#!/usr/bin/env python3
"""Immutable genuine stock 26.2 16th CacheOnce-wrapped Ap2(MIN) child fixture.

Only TWO new original JVM child IEEE-754 words per 4x32 fixed sample are
frozen. Prior genuine thirteenth RIGHT column independently owns the
old Ap2/CacheOnce/Holder parent. Source law and production gates remain false.
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

import worldgen_26_2_stock_final_density_sixteenth_layer as owner
import worldgen_26_2_stock_finaldensity_thirteenth_layer_fixture as prior
import worldgen_26_2_stock_finaldensity_fifteenth_layer_receipt as receipt

FIXTURE = Path(__file__).resolve().parents[1] / (
    "crates/world/helve-world-gen/tests/data/"
    "stock_finaldensity_sixteenth_cacheonce_ap2_children_128_rawbits.tsv"
)
SHA256 = "bd56e08412141819e938a0370b5375c458ff131d2cda12882826108b196b99d9"
REPORT_SHA256 = "648f5636c00f88c964c5b847abc57227157c2d53955cee971af05519126dcb5e"
REPORT_BYTES = 41479
LINE = re.compile(rb"[0-9a-f]{16}\t[0-9a-f]{16}\n\Z")
SHAPE = {
    "ap2_enum_class": owner.CLASS + "TwoArgumentSimpleFunction$Type",
    "ap2_op": "MIN",
    "ap2_left_class": owner.CLASS + "Ap2",
    "ap2_right_class": owner.CLASS + "Ap2",
}
TELEMETRY = {
    "arithmetic_candidate_first_mismatch_index": -1,
    "arithmetic_candidate_mismatches": 0,
    "observed_equal_operands": 0,
    "observed_left_strictly_less": 57,
    "observed_right_strictly_less": 71,
    "original_bounded_points": 128,
    "source_law_admitted": False,
}


class SixteenthFixtureError(ValueError):
    """Genuine exact frozen sixteenth Ap2(MIN) evidence rejected."""


def number(raw: str) -> float:
    return struct.unpack(">d", bytes.fromhex(raw))[0]


def native_sample_min(left: str, right: str) -> str:
    a, b = number(left), number(right)
    if not (math.isfinite(a) and math.isfinite(b)):
        raise SixteenthFixtureError("original sixteenth IEEE operands nonfinite")
    if a == b:
        raise SixteenthFixtureError("unreviewed sixteenth MIN operand tie/signed zero")
    return left if a < b else right


def load(path: Path = FIXTURE, *, require_sha: bool = True) -> tuple[tuple[str, str], ...]:
    raw = path.read_bytes()
    if len(raw) != 4352 or (require_sha and hashlib.sha256(raw).hexdigest() != SHA256):
        raise SixteenthFixtureError("original new-only sixteenth fixture bytes/SHA moved")
    lines = raw.splitlines(keepends=True)
    old = prior.load()
    if len(lines) != 128 or len(old) != 128:
        raise SixteenthFixtureError("genuine sixteenth 4x32 corpus size drift")
    result = []
    left_count = 0
    right_count = 0
    for i, line in enumerate(lines):
        if not LINE.fullmatch(line):
            raise SixteenthFixtureError(f"original sixteenth strict TSV shape moved: {i}")
        left, right = (raw_word.decode("ascii") for raw_word in line[:-1].split(b"\t"))
        selected = native_sample_min(left, right)
        # The OLD parent is the thirteenth RIGHT operand, not its MIN output.
        if selected != old[i][1]:
            raise SixteenthFixtureError(f"original thirteenth RIGHT parent anchor drift: {i}")
        if selected == left:
            left_count += 1
        else:
            right_count += 1
        result.append((left, right))
    if (left_count, right_count) != (57, 71):
        raise SixteenthFixtureError("genuine sixteenth MIN winner coverage moved")
    return tuple(result)


def validate_original(path: Path) -> None:
    raw = path.read_bytes()
    if len(raw) != REPORT_BYTES or hashlib.sha256(raw).hexdigest() != REPORT_SHA256:
        raise SixteenthFixtureError("original sixteenth JVM report length/SHA drift")
    try:
        report = json.loads(raw)
        owner.validate(report)
    except (ValueError, TypeError, KeyError, IndexError) as exc:
        raise SixteenthFixtureError("actual sixteenth original source/provenance rejected") from exc
    if len(report["shapes"]) != 4 or any(
        {k: v for k, v in row.items() if k != "world_seed_bits"} != SHAPE
        or row["world_seed_bits"] != owner.FINAL.SEEDS[i]
        for i, row in enumerate(report["shapes"])
    ):
        raise SixteenthFixtureError("actual original MIN/Ap2/Ap2 classes changed")
    if report["ap2_arithmetic_candidate_telemetry"] != TELEMETRY:
        raise SixteenthFixtureError("original sixteenth finite MIN telemetry/source gate drift")
    if report["prior_fifteenth_report_sha256"] != receipt.REPORT_SHA256:
        raise SixteenthFixtureError("original fifteenth source report SHA drift")
    actual, old = load(), prior.load()
    if len(report["vectors"]) != 128:
        raise SixteenthFixtureError("original sixteenth fixed sample count moved")
    for i, (v, pair) in enumerate(zip(report["vectors"], actual, strict=True)):
        if any(v[k] != "0x" + word for k, word in zip(owner.NEW_FIELDS, pair, strict=True)):
            raise SixteenthFixtureError(f"genuine original new Ap2 operand words altered {i}")
        if v["old_thirteenth_right_bits"] != "0x" + old[i][1]:
            raise SixteenthFixtureError(f"independent original thirteenth parent altered {i}")
    if any(report.get(gate) is not False for gate in owner.GATES):
        raise SixteenthFixtureError("sixteenth production/source law gate promoted")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--capture", type=Path, help="already-created PRIVATE original JVM JSON")
    args = parser.parse_args(argv)
    try:
        rows = load()
        if args.capture is not None:
            validate_original(args.capture)
    except (SixteenthFixtureError, OSError) as exc:
        print("STOCK 26.2 SIXTEENTH FIXTURE OPEN: " + str(exc), file=sys.stderr)
        return 2
    print(json.dumps({
        "kind": "original_26_2_sixteenth_actual_cacheonce_ap2_min_2_new_children",
        "original_report_sha256": REPORT_SHA256,
        "new_only_fixture_sha256": SHA256,
        "original_points": len(rows),
        "new_original_ieee_words": len(rows) * 2,
        "old_thirteenth_right_parent_bits_independently_anchored": len(rows),
        "sample_min_left_wins": 57,
        "sample_min_right_wins": 71,
        "sample_min_ties": 0,
        "java_ap2_source_law_admitted": False,
        "marker_cache_lifecycle_admitted": False,
        **{gate: False for gate in owner.GATES},
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
