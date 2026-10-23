#!/usr/bin/env python3
"""Source-authentic stock 26.2 twenty-first Noise-leaf new-only JVM receipt.

Actual twentieth wrapped MulOrAdd(MUL) descends into DensityFunctions$Noise.
Freeze ONE genuinely new Noise leaf output at each of four seeds x 32 XYZ.
The OLD twentieth wrapped child is only reconstructed from the previous
immutable 128-word receipt. Neither NoiseHolder/registry binding nor source
execution/caching/generalised parity is admitted by these finite observations.
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

import worldgen_26_2_stock_final_density_twenty_first_layer as owner
import worldgen_26_2_stock_finaldensity_twentieth_layer_fixture as previous

FIXTURE = Path(__file__).resolve().parents[1] / (
    "crates/world/helve-world-gen/tests/data/"
    "stock_finaldensity_twenty_first_actual_noise_leaf_128_rawbits.tsv"
)
FIXTURE_BYTES = 2176
SHA256 = "7519acc761730ba6aac2f1ac03d4b625d529127e258e23a8945dee7d25e193ed"
REPORT_BYTES = 37461
REPORT_SHA256 = "a14316f209553322029b2df7a37ddc757d5f52ae53005f404427111a00f58fec"
SCALAR_BITS = "bf878d4fdf3b6458"
SHAPE = {
    "muloradd_enum_class": owner.CLASS + "MulOrAdd$Type",
    "muloradd_op": "MUL",
    "muloradd_argument_bits": SCALAR_BITS,
    "muloradd_child_class": owner.CLASS + "Noise",
}
TELEMETRY = {
    "original_bounded_points": 128,
    "muloradd_candidate_mismatches": 0,
    "muloradd_candidate_first_mismatch_index": -1,
    "observed_add_points": 0,
    "observed_mul_points": 128,
    "source_law_admitted": False,
}
LINE = re.compile(rb"[0-9a-f]{16}\n\Z")


class TwentyFirstFixtureError(ValueError):
    """Original Noise sample, source provenance, immutable ancestry or gate drift."""


def from_ieee(word: str) -> float:
    return struct.unpack(">d", bytes.fromhex(word))[0]


def ieee(number: float) -> str:
    if not math.isfinite(number):
        raise TwentyFirstFixtureError("nonfinite actual stock Noise-leaf candidate")
    return struct.pack(">d", number).hex()


def load(path: Path = FIXTURE, *, require_sha: bool = True) -> tuple[str, ...]:
    raw = path.read_bytes()
    if len(raw) != FIXTURE_BYTES or (
        require_sha and hashlib.sha256(raw).hexdigest() != SHA256
    ):
        raise TwentyFirstFixtureError("genuine Noise-leaf fixture size/SHA mismatch")
    lines = raw.splitlines(keepends=True)
    old = previous.load()
    if len(lines) != 128 or len(old) != 128:
        raise TwentyFirstFixtureError("Noise-leaf 4x32 original point count moved")
    scalar = from_ieee(SCALAR_BITS)
    words = []
    for i, line in enumerate(lines):
        if not LINE.fullmatch(line):
            raise TwentyFirstFixtureError(f"new Noise-leaf raw IEEE frame drift {i}")
        word = line[:-1].decode("ascii")
        number = from_ieee(word)
        if not math.isfinite(number) or ieee(number * scalar) != old[i]:
            raise TwentyFirstFixtureError(
                f"actual twenty-first Noise-leaf multiply vs old twentieth parent {i}"
            )
        words.append(word)
    return tuple(words)


def validate_original(path: Path) -> None:
    raw = path.read_bytes()
    if len(raw) != REPORT_BYTES or hashlib.sha256(raw).hexdigest() != REPORT_SHA256:
        raise TwentyFirstFixtureError("original private twenty-first JVM report bytes/SHA drift")
    try:
        report = json.loads(raw)
        owner.validate(report)
        if len(report["shapes"]) != 4 or any(
            set(shape) != set(SHAPE) | {"world_seed_bits"}
            or {key: shape[key] for key in SHAPE} != SHAPE
            or shape["world_seed_bits"] != owner.FINAL.SEEDS[i]
            for i, shape in enumerate(report["shapes"])
        ):
            raise TwentyFirstFixtureError("original MUL -> Noise source shape moved")
        if report["muloradd_candidate_telemetry"] != TELEMETRY:
            raise TwentyFirstFixtureError("genuine Noise leaf bounded parity drift")
        words, prior = load(), previous.load()
        for i, (row, rawbits, old) in enumerate(zip(
            report["vectors"], words, prior, strict=True
        )):
            if row["nested_inner_bits"] != "0x" + rawbits:
                raise TwentyFirstFixtureError(f"one truly new original Noise IEEE drift {i}")
            if row["old_twentieth_child_bits"] != "0x" + old:
                raise TwentyFirstFixtureError(f"old twentieth parent anchor drift {i}")
        if any(report.get(gate) is not False for gate in owner.GATES):
            raise TwentyFirstFixtureError("source/all-input/cache/production gate promoted")
    except (KeyError, IndexError, TypeError, ValueError) as exc:
        raise TwentyFirstFixtureError("genuine original twenty-first report rejected") from exc


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--capture", type=Path, help="existing private original JVM JSON, never recapture")
    args = parser.parse_args(argv)
    try:
        rows = load()
        if args.capture is not None:
            validate_original(args.capture)
    except (TwentyFirstFixtureError, OSError) as exc:
        print("STOCK 26.2 TWENTY-FIRST NOISE FIXTURE OPEN: " + str(exc), file=sys.stderr)
        return 2
    print(json.dumps({
        "kind": "original_26_2_twenty_first_true_noise_leaf_one_new_word_unadmitted",
        "report_sha256": REPORT_SHA256,
        "new_only_fixture_sha256": SHA256,
        "original_seed_groups": 4,
        "new_noise_leaf_ieee_words": len(rows),
        "previous_twentieth_parent_words_reused": len(rows),
        "bounded_original_mul_parent_matches": len(rows),
        "noise_holder_source_law_admitted": False,
        **{gate: False for gate in owner.GATES},
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
