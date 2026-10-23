#!/usr/bin/env python3
"""Immutable stock Java 26.2 twentieth original nested MulOrAdd one-new-word receipt.

Freeze only the 128 genuinely new wrapped-child IEEE words. The old parent
nineteenth RIGHT MulOrAdd is reconstructed from its separately frozen child
fixture and the original twentieth source-observed ADD scalar (-0.0765).
This is *bounded numerical evidence*, never an all-input/VAR/SEM/cache law.
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

import worldgen_26_2_stock_final_density_twentieth_layer as owner
import worldgen_26_2_stock_finaldensity_nineteenth_layer_fixture as previous

FIXTURE = Path(__file__).resolve().parents[1] / (
    "crates/world/helve-world-gen/tests/data/"
    "stock_finaldensity_twentieth_muloradd_nested_child_128_rawbits.tsv"
)
FIXTURE_BYTES = 2176
SHA256 = "cfefd23fb5cb60a0d8da2ec0a12990c58ef6b94bd2faff2639e1660148482d6c"
REPORT_BYTES = 37509
REPORT_SHA256 = "859e7f78594bb2ddca090627ea6e04503b220f6b619fe3df46bab8b25394bbd8"
ARGUMENT_BITS = "bfb395810624dd2f"
SHAPE = {
    "muloradd_enum_class": owner.CLASS + "MulOrAdd$Type",
    "muloradd_op": "ADD",
    "muloradd_argument_bits": ARGUMENT_BITS,
    "muloradd_child_class": owner.CLASS + "MulOrAdd",
}
TELEMETRY = {
    "original_bounded_points": 128,
    "muloradd_candidate_mismatches": 0,
    "muloradd_candidate_first_mismatch_index": -1,
    "observed_add_points": 128,
    "observed_mul_points": 0,
    "source_law_admitted": False,
}
LINE = re.compile(rb"[0-9a-f]{16}\n\Z")


class TwentiethFixtureError(ValueError):
    """Original twentieth source provenance, immutable words or gate drift."""


def ieee(number: float) -> str:
    if not math.isfinite(number):
        raise TwentiethFixtureError("nonfinite original twentieth native candidate")
    return struct.pack(">d", number).hex()


def from_ieee(word: str) -> float:
    return struct.unpack(">d", bytes.fromhex(word))[0]


def load(path: Path = FIXTURE, *, require_sha: bool = True) -> tuple[str, ...]:
    raw = path.read_bytes()
    if len(raw) != FIXTURE_BYTES or (
        require_sha and hashlib.sha256(raw).hexdigest() != SHA256
    ):
        raise TwentiethFixtureError("original twentieth one-new fixture bytes/SHA changed")
    records = raw.splitlines(keepends=True)
    older = previous.load()
    if len(records) != 128 or len(older) != 128:
        raise TwentiethFixtureError("original twentieth strict 4x32 dimensions changed")
    scalar = from_ieee(ARGUMENT_BITS)
    words: list[str] = []
    for i, line in enumerate(records):
        if not LINE.fullmatch(line):
            raise TwentiethFixtureError(f"original twentieth raw IEEE malformed at {i}")
        word = line[:-1].decode("ascii")
        child = from_ieee(word)
        if not math.isfinite(child) or ieee(child + scalar) != older[i][1]:
            raise TwentiethFixtureError(
                f"genuine twentieth one-new child vs frozen nineteenth RIGHT drift at {i}"
            )
        words.append(word)
    return tuple(words)


def validate_original(path: Path) -> None:
    raw = path.read_bytes()
    if len(raw) != REPORT_BYTES or hashlib.sha256(raw).hexdigest() != REPORT_SHA256:
        raise TwentiethFixtureError("original twentieth report bytes/SHA moved")
    try:
        report = json.loads(raw)
        owner.validate(report)
        if len(report["shapes"]) != 4 or any(
            set(shape) != set(SHAPE) | {"world_seed_bits"}
            or {k: shape[k] for k in SHAPE} != SHAPE
            or shape["world_seed_bits"] != owner.FINAL.SEEDS[i]
            for i, shape in enumerate(report["shapes"])
        ):
            raise TwentiethFixtureError("twentieth real source scalar/enum/nesting changed")
        if report["muloradd_candidate_telemetry"] != TELEMETRY:
            raise TwentiethFixtureError("original twentieth finite telemetry drift")
        rows = load()
        old = previous.load()
        for i, (actual, new, older) in enumerate(
            zip(report["vectors"], rows, old, strict=True)
        ):
            if actual["muloradd_inner_bits"] != "0x" + new:
                raise TwentiethFixtureError(f"new twentieth original IEEE drift at {i}")
            if actual["old_nineteenth_right_bits"] != "0x" + older[1]:
                raise TwentiethFixtureError(f"old nineteenth original parent drift at {i}")
        if any(report[gate] is not False for gate in owner.GATES):
            raise TwentiethFixtureError("original source law/production gates promoted")
    except (KeyError, IndexError, TypeError, ValueError) as exc:
        raise TwentiethFixtureError("original twentieth source-authentic report rejected") from exc


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--capture", type=Path, help="existing PRIVATE original JSON; never recapture")
    args = parser.parse_args(argv)
    try:
        rows = load()
        if args.capture is not None:
            validate_original(args.capture)
    except (TwentiethFixtureError, OSError) as exc:
        print("STOCK 26.2 TWENTIETH FIXTURE OPEN: " + str(exc), file=sys.stderr)
        return 2
    print(json.dumps({
        "kind": "original_26_2_twentieth_nested_muloradd_one_new_child_unadmitted",
        "original_report_sha256": REPORT_SHA256,
        "one_new_fixture_sha256": SHA256,
        "original_points": len(rows),
        "truly_new_ieee_words": len(rows),
        "previous_parent_words_reused": len(rows),
        "bounded_native_add_parent_matches": len(rows),
        "source_law_admitted": False,
        **{gate: False for gate in owner.GATES},
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
