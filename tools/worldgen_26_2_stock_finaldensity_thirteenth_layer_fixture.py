#!/usr/bin/env python3
"""Exact genuine 26.2 thirteenth selected-left Ap2 child fixture; finite only.

Freeze only two new original-JVM immediate child IEEE words per fixed sample.
Independently import the twelfth new-only fixture for the old thirteenth
Ap2 parent. Do not infer all-input Java laws, caching, or production authority.
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

import worldgen_26_2_stock_final_density_thirteenth_layer as owner
import worldgen_26_2_stock_finaldensity_twelfth_layer_fixture as prior

FIXTURE = Path(__file__).resolve().parents[1] / (
    "crates/world/helve-world-gen/tests/data/"
    "stock_finaldensity_thirteenth_selected_left_ap2_children_128_rawbits.tsv"
)
SHA256 = "cd8ba322bea4575aba70a28223940162af7feed926806a96c217d7a4b04eee4a"
REPORT_SHA256 = "e50e4ef14a7d3716613e0bb77982a5693c0395ac1f32e24325930dbf0c8d79db"
REPORT_BYTES = 41610
LINE = re.compile(rb"[0-9a-f]{16}\t[0-9a-f]{16}\n\Z")
CLASS = owner.CLASS
SHAPE = {
    "ap2_enum_class": CLASS + "TwoArgumentSimpleFunction$Type",
    "ap2_op": "MIN",
    "ap2_left_class": CLASS + "Ap2",
    "ap2_right_class": CLASS + "HolderHolder",
}
TELEMETRY = {
    "direct_arithmetic_candidate_mismatches": 0,
    "direct_arithmetic_first_mismatch_index": -1,
    "original_bounded_points": 128,
    "source_law_admitted": False,
}
LEFT_WINS = (0, 1, 9, 10, 11, 12, 31, 32, 41, 53, 62, 117)
ROOT_SELECTED_LEFT = LEFT_WINS
ROOT_SELECTED_RIGHT_COUNT = 43


class ThirteenthFixtureError(ValueError):
    """Genuine original JVM thirteenth finite evidence absent or altered."""


def number(word: str) -> float:
    return struct.unpack(">d", bytes.fromhex(word))[0]


def selected_min(left: str, right: str) -> str:
    """Only finite unequal observed operands; fail closed on signed-zero ties."""
    a, b = number(left), number(right)
    if not math.isfinite(a) or not math.isfinite(b):
        raise ThirteenthFixtureError("original thirteenth child nonfinite")
    if a == b:
        raise ThirteenthFixtureError("unreviewed original thirteenth MIN tie")
    return left if a < b else right


def load(
    path: Path = FIXTURE, *, require_sha: bool = True
) -> tuple[tuple[str, str], ...]:
    raw = path.read_bytes()
    if len(raw) != 128 * 34 or (
        require_sha and hashlib.sha256(raw).hexdigest() != SHA256
    ):
        raise ThirteenthFixtureError("genuine thirteenth two-new-only fixture bytes/SHA drift")
    old = prior.load()
    lines = raw.splitlines(keepends=True)
    if len(lines) != 128 or len(old) != 128:
        raise ThirteenthFixtureError("original 4x32 sample count drift")
    result = []
    actual_left_wins = []
    for i, line in enumerate(lines):
        if not LINE.fullmatch(line):
            raise ThirteenthFixtureError(f"thirteenth original IEEE pair malformed: {i}")
        left, right = (part.decode("ascii") for part in line[:-1].split(b"\t"))
        picked = selected_min(left, right)
        # Old twelfth fixture: first field is actual twelfth MIN LEFT operand.
        # This is precisely the previous original JVM thirteenth Ap2 parent.
        if picked != old[i][0]:
            raise ThirteenthFixtureError(
                f"original twelfth left Ap2 independent old-parent drift: {i}"
            )
        if picked == left:
            actual_left_wins.append(i)
        result.append((left, right))
    if tuple(actual_left_wins) != LEFT_WINS:
        raise ThirteenthFixtureError("original thirteenth sampled child-win coverage drift")
    return tuple(result)


def validate_original(path: Path) -> None:
    raw = path.read_bytes()
    if len(raw) != REPORT_BYTES or hashlib.sha256(raw).hexdigest() != REPORT_SHA256:
        raise ThirteenthFixtureError("original thirteenth JVM report bytes/SHA drift")
    try:
        report = json.loads(raw)
        owner.validate(report)
    except (ValueError, TypeError, KeyError, IndexError) as exc:
        raise ThirteenthFixtureError("original thirteenth source/provenance rejected") from exc
    if any(
        {key: val for key, val in shape.items() if key != "world_seed_bits"} != SHAPE
        for shape in report["shapes"]
    ):
        raise ThirteenthFixtureError("actual thirteenth MIN child classes changed")
    if report["arithmetic_candidate_telemetry"] != TELEMETRY:
        raise ThirteenthFixtureError("unadmitted source-owned arithmetic telemetry changed")
    actual, old = load(), prior.load()
    for i, (vector, new) in enumerate(zip(report["vectors"], actual, strict=True)):
        if any(
            vector[key] != "0x" + word
            for key, word in zip(owner.NEW_FIELDS, new, strict=True)
        ):
            raise ThirteenthFixtureError(f"original JVM child bit changed at row {i}")
        if vector["old_twelfth_left_bits"] != "0x" + old[i][0]:
            raise ThirteenthFixtureError(f"independent twelfth parent bit drift at row {i}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--capture", type=Path, help="existing source-only private original JVM JSON"
    )
    args = parser.parse_args(argv)
    try:
        rows = load()
        if args.capture is not None:
            validate_original(args.capture)
    except (ThirteenthFixtureError, OSError) as exc:
        print("STOCK 26.2 THIRTEENTH FIXTURE OPEN: " + str(exc), file=sys.stderr)
        return 2
    print(json.dumps({
        "kind": "original_26_2_thirteenth_selected_left_ap2_min_finite_only",
        "new_only_operand_rows": len(rows),
        "genuinely_new_original_ieee_words": len(rows) * 2,
        "independently_anchored_old_twelfth_left_parent_words": len(rows),
        "bounded_parent_parity": len(rows),
        "min_left_wins": len(LEFT_WINS),
        "min_right_wins": len(rows) - len(LEFT_WINS),
        "original_min_left_win_indices": list(LEFT_WINS),
        "new_only_fixture_sha256": SHA256,
        "original_report_sha256": REPORT_SHA256,
        **{gate: False for gate in owner.GATES},
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
