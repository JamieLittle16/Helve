#!/usr/bin/env python3
"""Immutable original 26.2 twenty-sixth IntervalSelect declaration receipt.

This stage observed ZERO new XYZ IEEE words. Both old numeric streams live
only in the sealed twenty-fifth fixture. The uploaded private 26th JSON
stays local; this script pins its exact bytes and observed class fields.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

import worldgen_26_2_stock_final_density_twenty_sixth_layer as source
import worldgen_26_2_stock_finaldensity_twenty_fifth_layer_fixture as old

REPORT_BYTES = 39040
REPORT_SHA256 = "ada7937510777d744d612de17486981a485c1714863cffb2e98096dc069cfb44"
DECLARED_FIELDS = (
    "functions~java.util.List;"
    "input~net.minecraft.world.level.levelgen.DensityFunction;"
    "thresholds~it.unimi.dsi.fastutil.doubles.DoubleList"
)
TELEMETRY = {
    "new_numeric_ieee_words": 0,
    "old_twenty_fifth_interval_anchors_matched": 256,
    "original_bounded_points": 128,
    "original_interval_declaration_shapes_observed": 4,
    "source_law_admitted": False,
}


class OriginalTwentySixthReceiptError(ValueError):
    """Original 26th provenance, type or inherited numeric evidence drift."""


def validate_original(path: Path) -> dict:
    raw = path.read_bytes()
    if len(raw) != REPORT_BYTES or hashlib.sha256(raw).hexdigest() != REPORT_SHA256:
        raise OriginalTwentySixthReceiptError("original private 26th report bytes/SHA moved")
    try:
        report = json.loads(raw)
        source.validate(report)
        if (
            len(report["shapes"]) != 4
            or any(
                shape != {
                    "first_interval_declared_fields": DECLARED_FIELDS,
                    "second_interval_declared_fields": DECLARED_FIELDS,
                    "world_seed_bits": source.FINAL.SEEDS[i],
                }
                for i, shape in enumerate(report["shapes"])
            )
            or report["interval_declarations_candidate_telemetry"] != TELEMETRY
        ):
            raise OriginalTwentySixthReceiptError("genuine 26th IntervalSelect fields drift")
        old_words = old.load()
        if len(report["vectors"]) != len(old_words):
            raise OriginalTwentySixthReceiptError("real old 4x32 numeric anchors moved")
        for i, record in enumerate(report["vectors"]):
            if tuple(record[k][2:] for k in source.OLD_FIELDS) != old_words[i]:
                raise OriginalTwentySixthReceiptError(f"old interval numeric anchor moved {i}")
        if any(report[g] is not False for g in source.GATES):
            raise OriginalTwentySixthReceiptError("unadmitted 26th source gate opened")
    except (ValueError, KeyError, TypeError, IndexError) as exc:
        raise OriginalTwentySixthReceiptError("original 26th report rejected") from exc
    return {
        "original_report_sha256": REPORT_SHA256,
        "real_interval_declared_fields": DECLARED_FIELDS,
        "original_4x32_points": 128,
        "new_numeric_ieee_words": 0,
        "reused_old_interval_ieee_words": 256,
        "source_law_admitted": False,
        "production_worldgen_enabled": False,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--capture", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        print(json.dumps(validate_original(args.capture), sort_keys=True))
        return 0
    except (OriginalTwentySixthReceiptError, OSError) as exc:
        print("STOCK 26.2 ORIGINAL 26TH DECLARATION RECEIPT OPEN: " + str(exc),
              file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
