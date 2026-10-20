#!/usr/bin/env python3
"""Fail-closed, source-free frozen official 26.2 world-seed noise bit oracle.

The official JVM (not a Rust port) produced these bits from stock registries,
world-seeded RandomState and DensityFunctions$Noise.compute. Freezing the
answers is NOT claiming that a Rust RandomState implementation exists or has
passed parity, nor that independent VAR/SEM or production gates are admitted.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

import worldgen_26_2_world_seed_density_capture as capture

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "vanilla/reports/worldgen-26_2-stock-worldseed-noise-bits-01.txt"
FIXTURE_SHA256 = "79bf0251f2cf8bb7f4bfb226be0ba7912a7a574c6aaf8e8f5a9560dd2edfe414"
ORIGINAL_JSON_SHA256 = "ee2135a89e196e482ea13eb374423cf14fb73a2c7f3e1e175dda1fbf785dced4"
SOURCE_SHA256 = "1e9bca3dff83cd83e7905f8810f1ec9899361fa2dc83fe893bb48beeb04df750"
SERVER_SHA256 = "cdacdfb25898de5e4b4b0e5ddcc2722f77067e46605709c2d886c000ebb63ec5"
VANILLA_STOCK_LOOKUP_SHA256 = "63167b8b8e1f8ffd687a6577e61ab06c9e87ecb16457b9a65c67a8d8f07bf16d"
HEX16 = re.compile(r"[0-9a-f]{16}\Z")


class FixtureError(ValueError):
    """The frozen source-free reference evidence has changed or is invalid."""


def load_bits(path: Path = FIXTURE) -> tuple[str, ...]:
    raw = path.read_bytes()
    if len(raw) != 1440 * 17 or hashlib.sha256(raw).hexdigest() != FIXTURE_SHA256:
        raise FixtureError("source-free stock world-seed fixture size or SHA-256 changed")
    try:
        lines = raw.decode("ascii").splitlines(keepends=True)
    except UnicodeDecodeError as exc:
        raise FixtureError("non-ASCII world-seed raw-bits fixture") from exc
    if len(lines) != 1440:
        raise FixtureError("expected exactly 1440 stock-seeded reference vectors")
    bits = []
    for index, line in enumerate(lines):
        if len(line) != 17 or line[-1] != "\n" or HEX16.fullmatch(line[:-1]) is None:
            raise FixtureError(f"bad hexadecimal IEEE-754 record at index {index}")
        value = int(line[:-1], 16)
        if ((value >> 52) & 0x7ff) == 0x7ff:
            raise FixtureError(f"nonfinite stock noise output at index {index}")
        bits.append(line[:-1])
    return tuple(bits)


def validate_manifest(manifest: dict, bits: tuple[str, ...]) -> None:
    """Check source-free manifest, exact row order, identities and closed gates.

    This is an inspection of official output, NOT a replay in Rust. Callers
    establishing authentic acquisition must additionally pin the original
    uploaded JSON SHA-256 (see validate_original_capture).
    """
    fixed = {
        "schema": 1,
        "kind": capture.KIND,
        "stage": capture.STAGE,
        "minecraft": "26.2",
        "protocol": 776,
        "data_version": 4903,
        "source_archive_sha256": SOURCE_SHA256,
        "official_server_sha256": SERVER_SHA256,
        "frontier_sha256": capture.FRONTIER_SHA256,
        "profiles": capture.PROFILES,
        "world_seeds": list(capture.SEEDS),
        "noise_keys": list(capture.NOISE_KEYS),
        "stock_registry_used": True,
        "world_seed_random_state_observed": True,
        "world_seed_random_state_bound": False,
        "source_text_included": False,
        "independent_var_sem_admitted": False,
        "production_worldgen_enabled": False,
    }
    if not isinstance(manifest, dict) or set(manifest) != set(fixed) | {"source_methods", "vectors"}:
        raise FixtureError("wrong world-seed source-free manifest schema")
    for key, expected in fixed.items():
        if type(manifest.get(key)) is not type(expected) or manifest[key] != expected:
            raise FixtureError("incorrect official target, profile, seed or closed gate: " + key)
    methods = manifest["source_methods"]
    if not isinstance(methods, dict) or set(methods) != set(capture.SOURCE_PINS) | {"stock_vanilla_lookup"}:
        raise FixtureError("wrong stock source-method inventory")
    for label, (owner, _, _, digest) in capture.SOURCE_PINS.items():
        row = methods[label]
        if not isinstance(row, dict) or set(row) != {"owner", "signature", "body_sha256", "normalized_sha256"} \
            or row["owner"] != owner or row["body_sha256"] != digest \
            or not isinstance(row["signature"], str) or not isinstance(row["normalized_sha256"], str) \
            or re.fullmatch(r"[0-9a-f]{64}", row["normalized_sha256"]) is None:
            raise FixtureError("wrong pinned method identity: " + label)
    stock = methods["stock_vanilla_lookup"]
    if not isinstance(stock, dict) or stock.get("owner") != capture.VANILLA_REGISTRIES \
        or stock.get("signature") != "createLookup()" \
        or stock.get("body_sha256") != VANILLA_STOCK_LOOKUP_SHA256 \
        or set(stock) != {"owner", "signature", "body_sha256", "normalized_sha256"} \
        or not isinstance(stock["normalized_sha256"], str) \
        or re.fullmatch(r"[0-9a-f]{64}", stock["normalized_sha256"]) is None:
        raise FixtureError("stock registry source identity changed")

    vectors = manifest["vectors"]
    expected = capture.input_rows()
    if not isinstance(vectors, list) or len(vectors) != 1440 or len(bits) != 1440:
        raise FixtureError("incomplete stock world-seed vector grid")
    for index, (actual, row, value) in enumerate(zip(vectors, expected, bits, strict=True)):
        if type(actual) is not dict or actual != dict(row, value_bits="0x" + value):
            raise FixtureError(f"wrong source-free stock vector / order / raw bits at {index}")


def validate_original_capture(path: Path) -> None:
    raw = path.read_bytes()
    if len(raw) > 400_000 or hashlib.sha256(raw).hexdigest() != ORIGINAL_JSON_SHA256:
        raise FixtureError("original official JVM world-seed capture SHA-256 changed")
    try:
        manifest = json.loads(raw)
    except (ValueError, UnicodeError) as exc:
        raise FixtureError("invalid original official JVM source-free JSON") from exc
    validate_manifest(manifest, load_bits())


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--capture", type=Path,
                        help="optional original, exact-SHA-pinned official JVM JSON")
    args = parser.parse_args(argv)
    try:
        bits = load_bits()
        if args.capture is not None:
            validate_original_capture(args.capture)
    except (FixtureError, OSError) as exc:
        print("STOCK 26.2 WORLDSEED REFERENCE NOT VERIFIED: " + str(exc), file=sys.stderr)
        return 2
    print(json.dumps({
        "vectors": len(bits),
        "fixture_sha256": FIXTURE_SHA256,
        "original_capture_sha256": ORIGINAL_JSON_SHA256,
        "stock_world_seed_observed": True,
        "rust_world_seed_parity_verified": False,
        "independent_var_sem_admitted": False,
        "production_worldgen_enabled": False,
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
