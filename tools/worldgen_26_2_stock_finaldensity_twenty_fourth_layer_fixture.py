#!/usr/bin/env python3
"""Freeze original 26.2 24th nineteenth-left MAX(Mapped, Mapped).

Only the TWO genuinely NEW child IEEE words per 4x32 stock point are
committed. The 128 OLD parent words are read afresh from the SHA-pinned
nineteenth fixture, not duplicated in this new-only TSV. No full
source/VAR/SEM/cache/NoiseChunk/production admission.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import struct
import sys
from pathlib import Path

import worldgen_26_2_stock_final_density_twenty_fourth_layer as owner
import worldgen_26_2_stock_finaldensity_nineteenth_layer_fixture as original_parent

FIXTURE = Path(__file__).resolve().parents[1] / (
    "crates/world/helve-world-gen/tests/data/"
    "stock_finaldensity_twenty_fourth_left_max_mapped_children_128_rawbits.tsv"
)
FIXTURE_BYTES = 4352
FIXTURE_SHA256 = "dc44a67d9ce942d5591cdf02cef388dedabedbe4b85e5c9d27f729e4e42fe343"
REPORT_BYTES = 45989
REPORT_SHA256 = "3c92faf8f74d8d6f4f45fa39e6d07a5dbfe9dc6ba9e7406a8e78e0e3afbe545f"
SHAPE = {
    "left_ap2_enum_class": owner.CLASS + "TwoArgumentSimpleFunction$Type",
    "left_ap2_op": "MAX",
    "left_ap2_left_class": owner.CLASS + "Mapped",
    "left_ap2_right_class": owner.CLASS + "Mapped",
}
TELEMETRY = {
    "arithmetic_candidate_first_mismatch_index": -1,
    "arithmetic_candidate_mismatches": 0,
    "observed_equal_operands": 0,
    "observed_left_strictly_less": 75,
    "observed_right_strictly_less": 53,
    "original_bounded_points": 128,
    "source_law_admitted": False,
}
LINE = re.compile(rb"[0-9a-f]{16}\t[0-9a-f]{16}\n")


class TwentyFourthFixtureError(ValueError):
    """Pinned actual original JVM source-owned 24th children drift."""


def load(path: Path = FIXTURE, *, require_sha: bool = True) -> tuple[tuple[str, str], ...]:
    raw = path.read_bytes()
    if len(raw) != FIXTURE_BYTES or (
        require_sha and hashlib.sha256(raw).hexdigest() != FIXTURE_SHA256
    ):
        raise TwentyFourthFixtureError("24th original two-new-only fixture digest drift")
    frames = raw.splitlines(keepends=True)
    previous = original_parent.load()
    if len(frames) != 128 or len(previous) != 128:
        raise TwentyFourthFixtureError("original 4x32 mapped MAX dimensions moved")
    result = []
    left_less = right_less = ties = 0
    for i, frame in enumerate(frames):
        if not LINE.fullmatch(frame):
            raise TwentyFourthFixtureError(f"source new-only raw IEEE frame malformed {i}")
        first, second = (word.decode("ascii") for word in frame[:-1].split(b"\t"))
        a = struct.unpack(">d", bytes.fromhex(first))[0]
        b = struct.unpack(">d", bytes.fromhex(second))[0]
        if not (a == a and b == b and abs(a) != float("inf") and abs(b) != float("inf")):
            raise TwentyFourthFixtureError("nonfinite original Mapped child")
        left_less += a < b
        right_less += a > b
        ties += a == b
        expected = first if a > b else second
        if expected != previous[i][0]:
            raise TwentyFourthFixtureError(f"24th native MAX to 19th original LEFT mismatch {i}")
        result.append((first, second))
    if (left_less, right_less, ties) != (75, 53, 0):
        raise TwentyFourthFixtureError("real MAX branch coverage changed")
    return tuple(result)


def validate_original(path: Path) -> dict:
    content = path.read_bytes()
    if len(content) != REPORT_BYTES or hashlib.sha256(content).hexdigest() != REPORT_SHA256:
        raise TwentyFourthFixtureError("original private stock JVM report bytes/SHA mismatch")
    try:
        report = json.loads(content)
        owner.validate(report)
        if (
            len(report["shapes"]) != 4
            or any(
                shape != {**SHAPE, "world_seed_bits": owner.FINAL.SEEDS[i]}
                for i, shape in enumerate(report["shapes"])
            )
            or report["left_ap2_arithmetic_candidate_telemetry"] != TELEMETRY
        ):
            raise TwentyFourthFixtureError("real 24th MAX/Mapped operation or coverage drift")
        rows = load()
        old = original_parent.load()
        if len(report["vectors"]) != 128:
            raise TwentyFourthFixtureError("real 4x32 vector count changed")
        for i, row in enumerate(report["vectors"]):
            if tuple(row[field][2:] for field in owner.NEW_FIELDS) != rows[i]:
                raise TwentyFourthFixtureError(f"new-only 24th stock source value drift {i}")
            if row["old_nineteenth_left_bits"][2:] != old[i][0]:
                raise TwentyFourthFixtureError(f"old 19th source parent changed {i}")
        if any(report[gate] is not False for gate in owner.GATES):
            raise TwentyFourthFixtureError("unqualified stock source gate opened")
    except (KeyError, TypeError, IndexError, ValueError) as exc:
        raise TwentyFourthFixtureError("real 24th source-owned report rejected") from exc
    return {
        "original_stock_report_sha256": REPORT_SHA256,
        "new_only_fixture_sha256": FIXTURE_SHA256,
        "original_4x32_points": 128,
        "genuinely_new_ieee_words": 256,
        "reused_old_nineteenth_left_parent_words": 128,
        "max_left_wins": 53,
        "max_right_wins": 75,
        "independent_var_sem_admitted": False,
        "production_worldgen_enabled": False,
        **{gate: False for gate in owner.GATES},
    }


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--capture", type=Path, help="PRIVATE 24th original report (optional)")
    args = p.parse_args(argv)
    try:
        rows = load()
        result = validate_original(args.capture) if args.capture else {
            "original_stock_report_sha256": REPORT_SHA256,
            "new_only_fixture_sha256": FIXTURE_SHA256,
            "genuinely_new_ieee_words": len(rows) * 2,
            "reused_old_nineteenth_left_parent_words": len(rows),
            "source_law_admitted": False,
            "production_worldgen_enabled": False,
            **{gate: False for gate in owner.GATES},
        }
    except (TwentyFourthFixtureError, OSError) as exc:
        print("STOCK 26.2 ORIGINAL TWENTY-FOURTH FIXTURE OPEN: "+str(exc),
              file=sys.stderr)
        return 2
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
