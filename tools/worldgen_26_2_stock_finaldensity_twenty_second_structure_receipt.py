#!/usr/bin/env python3
"""Seal actual 26.2 finalDensity Noise leaf ID, scales and 128 old anchors.

The twenty-second original stock JVM report contains zero genuinely new
numeric leaf words. Never re-store the old 128 Noise samples in another
fixture, guess the registry parameters or admit production/VAR/SEM.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

import worldgen_26_2_stock_final_density_twenty_second_layer as owner

REPORT_BYTES = 32822
REPORT_SHA256 = "8c2a9b2a2f5383899c7ade9931971ce9ea6757b3bcd1967aac9038df8fe5834c"
STRUCTURE = {
    "noise_node_class": "net.minecraft.world.level.levelgen.DensityFunctions$Noise",
    "noise_holder_class": "net.minecraft.world.level.levelgen.DensityFunction$NoiseHolder",
    "noise_data_holder_class": "net.minecraft.core.Holder$Reference",
    "noise_parameters_key": "minecraft:spaghetti_3d_thickness",
    "noise_runtime_class": "net.minecraft.world.level.levelgen.synth.NormalNoise",
    "noise_xz_scale_bits": "3ff0000000000000",
    "noise_y_scale_bits": "3ff0000000000000",
}
TELEMETRY = {
    "genuinely_new_ieee_words": 0,
    "old_twenty_first_noise_anchors_matched": 128,
    "original_bounded_points": 128,
    "original_noise_shapes_observed": 4,
    "source_law_admitted": False,
}


class TwentySecondReceiptError(ValueError):
    """Source-owned twenty-second report identity or Noise leaf drift."""


def validate_original(path: Path) -> dict:
    raw = path.read_bytes()
    if len(raw) != REPORT_BYTES or hashlib.sha256(raw).hexdigest() != REPORT_SHA256:
        raise TwentySecondReceiptError("original private 22nd report bytes/SHA drift")
    try:
        report = json.loads(raw)
        owner.validate(report)
        if (report["noise_structure_candidate_telemetry"] != TELEMETRY
                or len(report["shapes"]) != 4 or len(report["vectors"]) != 128):
            raise TwentySecondReceiptError("real Noise 4x32 bounded structure drift")
        seeds = owner.FINAL.SEEDS
        for i, shape in enumerate(report["shapes"]):
            if shape != {**STRUCTURE, "world_seed_bits": seeds[i]}:
                raise TwentySecondReceiptError(
                    f"actual spaghetti Noise source-owned shape drift: seed {i}"
                )
        frozen = owner.prior_leaf.load()
        for i, row in enumerate(report["vectors"]):
            if row["old_twenty_first_noise_bits"] != "0x" + frozen[i]:
                raise TwentySecondReceiptError(
                    f"old genuine twenty-first Noise anchor moved: {i}"
                )
        if any(report.get(gate) is not False for gate in owner.GATES):
            raise TwentySecondReceiptError("all-input/source/production gate promoted")
    except (KeyError, TypeError, IndexError, ValueError) as exc:
        raise TwentySecondReceiptError("private twenty-second stock report rejected") from exc
    return {
        "kind": "original_26_2_22nd_real_spaghetti_noise_structure_zero_new_words_unadmitted",
        "original_report_sha256": REPORT_SHA256,
        "original_report_bytes": REPORT_BYTES,
        "source_key": STRUCTURE["noise_parameters_key"],
        "source_xz_scale_bits": STRUCTURE["noise_xz_scale_bits"],
        "source_y_scale_bits": STRUCTURE["noise_y_scale_bits"],
        "reused_old_noise_anchors": len(frozen),
        "new_noise_sample_ieee_words": 0,
        "independent_var_sem_admitted": False,
        "production_worldgen_enabled": False,
        **{gate: False for gate in owner.GATES},
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--capture", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        report = validate_original(args.capture)
    except (TwentySecondReceiptError, OSError) as exc:
        print("STOCK 26.2 TWENTY-SECOND RECEIPT OPEN: " + str(exc), file=sys.stderr)
        return 2
    print(json.dumps(report, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
