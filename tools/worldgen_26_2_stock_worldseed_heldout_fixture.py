#!/usr/bin/env python3
"""SHA-pinned source-free held-out stock 26.2 registered-noise reference.

The 576 exact JVM outputs are *independently acquired* numeric evidence.
Loading or validating the oracle does NOT perform Rust parity, independently
review source/delegate laws or authorize any production world generation.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

import worldgen_26_2_stock_worldseed_fixture as frozen
import worldgen_26_2_stock_worldseed_heldout_capture as capture
import worldgen_26_2_world_seed_density_capture as original

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "crates/world/helve-world-gen/tests/data/stock_worldseed_heldout_576_rawbits.txt"
FIXTURE_SHA256 = "0a0ae74712c31ea735f293c54264b80ecdc00e667b82d84eded003bf0660dab4"
ORIGINAL_JSON_SHA256 = "59c510f78edd2f70351c377ea8d13017f52370cfa20bc480a73cddcfb59b19f5"
HEX16 = re.compile(r"[0-9a-f]{16}\Z")


class HeldoutFixtureError(ValueError):
    """Source-free independently acquired held-out corpus is not qualified."""


def read_fixture(path: Path = FIXTURE) -> tuple[str, ...]:
    raw = path.read_bytes()
    if len(raw) != 576 * 17 or hashlib.sha256(raw).hexdigest() != FIXTURE_SHA256:
        raise HeldoutFixtureError("held-out fixture size or SHA-256 differs")
    try:
        lines = raw.decode("ascii").splitlines(keepends=True)
    except UnicodeDecodeError as exc:
        raise HeldoutFixtureError("non-ASCII held-out raw-bit oracle") from exc
    if len(lines) != 576:
        raise HeldoutFixtureError("incomplete 576-vector held-out oracle")
    for index, row in enumerate(lines):
        if len(row) != 17 or row[-1] != "\n" or HEX16.fullmatch(row[:-1]) is None:
            raise HeldoutFixtureError("held-out noncanonical IEEE word at " + str(index))
        bits = int(row[:-1], 16)
        if ((bits >> 52) & 0x7ff) == 0x7ff:
            raise HeldoutFixtureError("held-out nonfinite sample at " + str(index))
    if (lines[0], lines[287], lines[575]) != (
        "bfded41016e4261a\n",
        "bfa078eb58200b97\n",
        "3fbe82b27db6a527\n",
    ):
        raise HeldoutFixtureError("held-out anchor words differ")
    return tuple(row[:-1] for row in lines)


def validate_original_capture(path: Path) -> None:
    raw = path.read_bytes()
    if len(raw) > 250_000 or hashlib.sha256(raw).hexdigest() != ORIGINAL_JSON_SHA256:
        raise HeldoutFixtureError("independently captured original 576-row JSON SHA changed")
    try:
        manifest = json.loads(raw)
    except (UnicodeError, ValueError) as exc:
        raise HeldoutFixtureError("malformed original held-out capture") from exc
    if not isinstance(manifest, dict) or not isinstance(manifest.get("source_methods"), dict):
        raise HeldoutFixtureError("missing actual stock source method identities")
    methods = manifest["source_methods"]
    if set(methods) != set(original.SOURCE_PINS) | {"stock_vanilla_lookup"}:
        raise HeldoutFixtureError("changed source method identity set")
    for label, (owner, _, _, sha) in original.SOURCE_PINS.items():
        method = methods[label]
        if method.get("owner") != owner or method.get("body_sha256") != sha:
            raise HeldoutFixtureError("source method changed: " + label)
    lookup = methods["stock_vanilla_lookup"]
    if (lookup.get("owner") != original.VANILLA_REGISTRIES
        or lookup.get("body_sha256") != frozen.VANILLA_STOCK_LOOKUP_SHA256
        or lookup.get("signature") != "createLookup()"):
        raise HeldoutFixtureError("changed stock registry implementation identity")
    try:
        capture.validate(
            manifest,
            source_sha=frozen.SOURCE_SHA256,
            server_sha=frozen.SERVER_SHA256,
            methods=methods,
        )
    except capture.HeldoutNoiseError as exc:
        raise HeldoutFixtureError("wrong held-out source, order or gate: " + str(exc)) from exc
    expected = read_fixture()
    for index, (row, bits) in enumerate(zip(manifest["vectors"], expected, strict=True)):
        if row["value_bits"] != "0x" + bits:
            raise HeldoutFixtureError("JVM held-out capture/fixture differs at " + str(index))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--original-json", type=Path, default=None,
                        help="optional original source-free locally captured JVM JSON")
    options = parser.parse_args(argv)
    try:
        lines = read_fixture()
        if options.original_json is not None:
            validate_original_capture(options.original_json)
        print("PINNED independent official stock 26.2 held-out oracle:",
              len(lines), "raw IEEE-754 words; Rust parity and VAR/SEM are separate")
    except (HeldoutFixtureError, OSError, KeyError, TypeError) as exc:
        print("UNQUALIFIED 26.2 HELD-OUT FIXTURE: " + str(exc), file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
