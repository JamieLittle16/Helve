#!/usr/bin/env python3
"""Strict source-owned eleventh 26.2 direct-child fixture, finite samples only.

Freeze exactly five original-JVM child IEEE words per seeded point. The old
Marker and both original Ap2 parents are independently loaded from the tenth
fixture, never recopied into the eleventh fixture. CacheOnce lifecycle, all-input
Ap2 laws, stock NoiseChunk and production worldgen remain unadmitted.
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

import worldgen_26_2_stock_final_density_eleventh_layer as eleventh
import worldgen_26_2_stock_finaldensity_tenth_layer_fixture as prior

FIXTURE = Path(__file__).resolve().parents[1] / (
    "crates/world/helve-world-gen/tests/data/"
    "stock_finaldensity_eleventh_layer_new_128_rawbits.tsv"
)
SHA256 = "f2d4b9084f30aa5f277053f9513c7529c321648d491b21b77e12bfd24b960e99"
REPORT_SHA256 = "a9d39854865d84bc8bdc2cf061ff715a589101af57c842dc159c2754cc71c6cc"
REPORT_BYTES = 71499
LINE = re.compile(rb"(?:[0-9a-f]{16}\t){4}[0-9a-f]{16}\n\Z")
CLASS = eleventh.tenth.ninth.eighth.CLASS
SHAPE = {
    "marker_enum_class": CLASS + "Marker$Type",
    "marker_type": "CacheOnce",
    "marker_child_class": CLASS + "HolderHolder",
    "in_enum_class": CLASS + "TwoArgumentSimpleFunction$Type",
    "in_op": "MIN",
    "in_left_class": CLASS + "Marker",
    "in_right_class": CLASS + "MulOrAdd",
    "out_enum_class": CLASS + "TwoArgumentSimpleFunction$Type",
    "out_op": "MAX",
    "out_left_class": CLASS + "Ap2",
    "out_right_class": CLASS + "RangeChoice",
}
MARKER_TELEMETRY = {
    "original_bounded_points": 128,
    "marker_delegate_mismatches": 0,
    "marker_delegate_first_mismatch_index": -1,
    "source_law_admitted": False,
}


class EleventhFixtureError(ValueError):
    """Eleventh source-owning finite evidence drift or inadmissible fixture."""


def number(word: str) -> float:
    return struct.unpack(">d", bytes.fromhex(word))[0]


def candidate_bits(left: str, right: str, *, minimum: bool) -> str:
    """A finite-sample branch candidate, not a generalized Java compute law."""
    a, b = number(left), number(right)
    if not math.isfinite(a) or not math.isfinite(b):
        raise EleventhFixtureError("nonfinite actual eleventh child")
    if a == b and left != right:
        raise EleventhFixtureError("unreviewed signed-zero MIN/MAX tie")
    return left if (a <= b if minimum else a >= b) else right


def load(
    path: Path = FIXTURE, *, require_sha: bool = True
) -> tuple[tuple[str, str, str, str, str], ...]:
    raw = path.read_bytes()
    if len(raw) != 128 * 85 or (
        require_sha and hashlib.sha256(raw).hexdigest() != SHA256
    ):
        raise EleventhFixtureError("genuine eleventh new-only fixture bytes/SHA changed")
    old = prior.load()
    rows = raw.splitlines(keepends=True)
    if len(rows) != 128 or len(old) != 128:
        raise EleventhFixtureError("original eleventh 4x32 bounded sample count moved")
    result = []
    min_left = min_right = max_left = max_right = nonconstant_out = 0
    for i, row in enumerate(rows):
        if not LINE.fullmatch(row):
            raise EleventhFixtureError(f"eleventh actual rawbit row malformed: {i}")
        words = tuple(w.decode("ascii") for w in row[:-1].split(b"\t"))
        marker, in_left, in_right, out_left, out_right = words
        if any(not math.isfinite(number(w)) for w in words):
            raise EleventhFixtureError(f"eleventh source child nonfinite: {i}")
        parent_marker, parent_in, parent_out = old[i]
        if marker != parent_marker:
            raise EleventhFixtureError(f"CacheOnce SinglePoint candidate parent drift: {i}")
        actual_min = candidate_bits(in_left, in_right, minimum=True)
        actual_max = candidate_bits(out_left, out_right, minimum=False)
        if actual_min != parent_in or actual_max != parent_out:
            raise EleventhFixtureError(f"original tenth Ap2 parent bits disagree: {i}")
        min_left += actual_min == in_left
        min_right += actual_min == in_right and in_right != in_left
        max_left += actual_max == out_left
        max_right += actual_max == out_right and out_right != out_left
        nonconstant_out += out_right != "c12e848000000000"
        if i == 110 and not (actual_max == out_right and out_right != out_left):
            raise EleventhFixtureError("rare original MAX right-wins witness lost")
        result.append(words)
    if (min_left, min_right, max_left, max_right, nonconstant_out) != (
        68, 60, 127, 1, 3
    ):
        raise EleventhFixtureError("genuine eleventh sampled operation coverage drift")
    for i in (19, 109, 110):
        if result[i][4] == "c12e848000000000":
            raise EleventhFixtureError(f"real nonconstant out-right witness moved: {i}")
    return tuple(result)


def validate_original(path: Path) -> None:
    raw = path.read_bytes()
    if len(raw) != REPORT_BYTES or hashlib.sha256(raw).hexdigest() != REPORT_SHA256:
        raise EleventhFixtureError("authentic eleventh original owner bytes/SHA moved")
    try:
        report = json.loads(raw)
        eleventh.validate(report)
    except (ValueError, TypeError, KeyError, IndexError) as exc:
        raise EleventhFixtureError("eleventh source/provenance/admission rejected") from exc
    if any(
        {k: v for k, v in shape.items() if k != "world_seed_bits"} != SHAPE
        for shape in report["shapes"]
    ):
        raise EleventhFixtureError("genuine eleventh Marker/Ap2 shape changed")
    if report["marker_candidate_telemetry"] != MARKER_TELEMETRY:
        raise EleventhFixtureError("original unadmitted Marker telemetry changed")
    new = load()
    old = prior.load()
    for i, (vector, row) in enumerate(zip(report["vectors"], new, strict=True)):
        if any(
            vector[key] != "0x" + word
            for key, word in zip(eleventh.NEW_FIELDS, row, strict=True)
        ):
            raise EleventhFixtureError(f"real eleventh child changed: {i}")
        if any(
            vector[key] != "0x" + word
            for key, word in zip(eleventh.OLD_FIELDS, old[i], strict=True)
        ):
            raise EleventhFixtureError(f"independent tenth parent changed: {i}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--capture", type=Path, help="completed private original JVM eleventh JSON"
    )
    args = parser.parse_args(argv)
    try:
        rows = load()
        if args.capture is not None:
            validate_original(args.capture)
    except (EleventhFixtureError, OSError) as exc:
        print("STOCK 26.2 ELEVENTH FIXTURE OPEN: " + str(exc), file=sys.stderr)
        return 2
    print(json.dumps({
        "kind": "original_26_2_eleventh_finite_direct_child_only",
        "new_child_rows": len(rows),
        "genuinely_new_child_words": len(rows) * 5,
        "old_tenth_parent_words_anchored": len(rows) * 3,
        "single_point_marker_candidate_matches": 128,
        "min_parent_candidate_matches": 128,
        "max_parent_candidate_matches": 128,
        "max_right_wins_witness_index": 110,
        "original_eleventh_report_sha256": REPORT_SHA256,
        "new_only_fixture_sha256": SHA256,
        **{gate: False for gate in eleventh.GATES},
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
