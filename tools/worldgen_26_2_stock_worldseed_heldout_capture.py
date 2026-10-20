#!/usr/bin/env python3
"""Single bounded 576-vector *held-out* Minecraft Java 26.2 stock noise probe.

Reuses the already source-pinned VanillaRegistries.createLookup ->
RandomState.create -> getOrCreateNoise -> DensityFunctions.Noise bridge,
without repeating any of the original 1,440 oracle seed identities.
This probe does NOT admit source laws, Rust constructor generality, a terrain
generator, or production publication. The local result is source-free and
private until individually reviewed, fingerprinted and pinned.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sqlite3
import subprocess
import sys
import tempfile
import tomllib
import urllib.error
from pathlib import Path

import official_state_data as official
import r1b_configuration_source_probe as source_probe
import r2c_world_projection_source_review as projection
import vanilla_atlas
import worldgen_26_2_improved_noise_capture as improved
import worldgen_26_2_stock_worldseed_fixture as frozen
import worldgen_26_2_world_seed_density_capture as stock

KIND = "official_26_2_stock_worldseed_noise_heldout_576"
SEEDS = (
    "0x0123456789abcdef",
    "0x7fffffffffffffff",
    "0x8000000000000001",
    "0xf0e1d2c3b4a59687",
)
# New block-coordinate requests, including wrap +/-2^25 and signed i32 extremes.
# Entire collection is independent of the original fixed five seeds.
POINTS = (
    (0, 0, 0),
    (-1, -64, 1),
    (1, 319, -1),
    (33_554_431, -63, -33_554_432),
    (-33_554_431, 320, 33_554_431),
    (2_147_483_600, 255, -2_147_483_600),
    (-2_147_483_600, -4096, 2_147_483_600),
    (105, -65, -417),
    (-1_000_000, 2048, 1_000_000),
    (123_456, -128, -654_321),
    (-16, 0, 16),
    (15, 256, -15),
    (33_554_433, 321, -33_554_433),
    (-33_554_433, -31, 33_554_433),
    (2048, 63, -2048),
    (-2049, 64, 2049),
)
TOTAL = len(stock.PROFILES) * len(SEEDS) * len(stock.NOISE_KEYS) * len(POINTS)
assert TOTAL == 576


class HeldoutNoiseError(ValueError):
    """The independent held-out JVM capture is absent, malformed or unpinned."""


def input_rows() -> list[dict]:
    return [
        {
            "profile": profile, "world_seed_bits": seed, "noise_key": key,
            "block_x": x, "block_y": y, "block_z": z,
        }
        for profile in stock.PROFILES
        for seed in SEEDS for key in stock.NOISE_KEYS for (x, y, z) in POINTS
    ]


def observe(server: Path, rows: list[dict], *, timeout: int = 180) -> list[str]:
    if rows != input_rows() or len(rows) != 576:
        raise HeldoutNoiseError("held-out request count, order or identities changed")
    if not stock.JAVA_SOURCE.is_file():
        raise HeldoutNoiseError("original stock JVM reflection bridge is absent")
    with tempfile.TemporaryDirectory(prefix="helve-262-worldseed-heldout-") as scratch:
        work = Path(scratch)
        cp = official.extract_classpath(server, work / "classpath")
        built = subprocess.run(
            ["javac", "-encoding", "UTF-8", "-d", str(work), str(stock.JAVA_SOURCE)],
            capture_output=True, text=True, check=False, timeout=timeout)
        if built.returncode:
            raise HeldoutNoiseError("original stock JVM bridge javac failed: " + built.stderr[:1500])
        request = "\n".join(
            f"{r['profile']}\t{r['world_seed_bits']}\t{r['noise_key']}\t"
            f"{r['block_x']}\t{r['block_y']}\t{r['block_z']}"
            for r in rows
        ) + "\n"
        run = subprocess.run(
            [
                "java", "-Xmx768m", "-cp",
                os.pathsep.join([str(work), *(str(jar) for jar in cp)]),
                "HelveWorldSeededDensity262", "--heldout-576",
            ],
            input=request, capture_output=True, text=True,
            check=False, timeout=timeout,
        )
        problem = stock.java_probe_failure(run.stdout)
        if problem is not None:
            raise HeldoutNoiseError("original stock bridge rejected held-out probe: " + problem)
        if run.returncode:
            raise HeldoutNoiseError("official stock held-out JVM failed: "
                                    + stock.java_failure_detail(run.stderr))
        return stock.parse_bits(run.stdout, expected=576)


def validate(manifest: dict, *, source_sha: str, server_sha: str, methods: dict) -> None:
    expected = {
        "schema": 1, "kind": KIND, "minecraft": "26.2", "protocol": 776,
        "data_version": 4903, "source_archive_sha256": source_sha,
        "official_server_sha256": server_sha,
        "frontier_sha256": stock.FRONTIER_SHA256,
        "reference_fixture_sha256": frozen.FIXTURE_SHA256,
        "source_methods": methods, "profiles": stock.PROFILES,
        "world_seeds": list(SEEDS), "noise_keys": list(stock.NOISE_KEYS),
        "points": [list(point) for point in POINTS],
        "stock_registry_used": True, "world_seed_random_state_observed": True,
        "world_seed_random_state_bound": False, "source_text_included": False,
        "independent_var_sem_admitted": False, "production_worldgen_enabled": False,
    }
    if not isinstance(manifest, dict) or set(manifest) != set(expected) | {"vectors"}:
        raise HeldoutNoiseError("unsupported held-out oracle schema")
    for key, value in expected.items():
        if type(manifest.get(key)) is not type(value) or manifest[key] != value:
            raise HeldoutNoiseError("held-out target, order, source or gate differs: " + key)
    received = manifest["vectors"]
    required_rows = input_rows()
    if not isinstance(received, list) or len(received) != 576:
        raise HeldoutNoiseError("exactly 576 new official vectors required")
    for index, (want, row) in enumerate(zip(required_rows, received, strict=True)):
        if not isinstance(row, dict) or set(row) != set(want) | {"value_bits"} \
           or any(type(row.get(k)) is not type(v) or row.get(k) != v
                  for k, v in want.items()) \
           or not isinstance(row.get("value_bits"), str) \
           or stock.BITS.fullmatch(row["value_bits"]) is None:
            raise HeldoutNoiseError("invalid independent JVM row at index " + str(index))


def capture(*, source: Path, db: Path, lock: Path, server: Path,
            frontier: Path, output: Path) -> dict:
    destination = improved.external_output(output)
    with lock.open("rb") as reader:
        pin = tomllib.load(reader)
    if (pin.get("minecraft"), pin.get("protocol"), pin.get("data_version")) != ("26.2", 776, 4903):
        raise HeldoutNoiseError("not the locked 26.2 official runtime")
    reference = stock.reference_frontier(frontier, pin)
    connection = vanilla_atlas.connect_db(db)
    try:
        source_sha = source_probe.require_pinned_source(connection, source, lock)
        methods = stock.source_methods(reference, connection)
    finally:
        connection.close()
    server_sha = official.sha256_file(server)
    if source_sha != frozen.SOURCE_SHA256 or server_sha != frozen.SERVER_SHA256 \
       or server_sha != pin["runtime"]["server_sha256"] \
       or methods["stock_vanilla_lookup"]["body_sha256"] != frozen.VANILLA_STOCK_LOOKUP_SHA256:
        raise HeldoutNoiseError("original official stock source / JVM fingerprints changed")

    rows = input_rows()
    values = observe(server, rows)
    result = {
        "schema": 1, "kind": KIND, "minecraft": "26.2", "protocol": 776,
        "data_version": 4903, "source_archive_sha256": source_sha,
        "official_server_sha256": server_sha,
        "frontier_sha256": stock.FRONTIER_SHA256,
        "reference_fixture_sha256": frozen.FIXTURE_SHA256,
        "source_methods": methods, "profiles": stock.PROFILES,
        "world_seeds": list(SEEDS), "noise_keys": list(stock.NOISE_KEYS),
        "points": [list(point) for point in POINTS],
        "stock_registry_used": True, "world_seed_random_state_observed": True,
        "world_seed_random_state_bound": False, "source_text_included": False,
        "independent_var_sem_admitted": False, "production_worldgen_enabled": False,
        "vectors": [dict(row, value_bits=bits) for row, bits in zip(rows, values, strict=True)],
    }
    validate(result, source_sha=source_sha, server_sha=server_sha, methods=methods)
    payload = (json.dumps(result, indent=2, sort_keys=True) + "\n").encode()
    destination.parent.mkdir(parents=True, exist_ok=True)
    with os.fdopen(os.open(destination, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600),
                   "wb") as file:
        file.write(payload)
    return {
        "output": str(destination),
        "vectors": 576,
        "sha256": hashlib.sha256(payload).hexdigest(),
        "independent_heldout_jvm_observed": True,
        "rust_heldout_parity_verified": False,
        "world_seed_random_state_bound": False,
        "production_worldgen_enabled": False,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=stock.primitive.SOURCE)
    parser.add_argument("--db", type=Path, default=stock.primitive.DB)
    parser.add_argument("--lock", type=Path, default=stock.primitive.LOCK)
    parser.add_argument("--cache", type=Path, default=stock.primitive.CACHE)
    parser.add_argument("--server-jar", type=Path)
    parser.add_argument("--frontier", type=Path, default=stock.FRONTIER)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        server = args.server_jar
        if server is None:
            found, _ = official.resolve("26.2", args.cache)
            server = found["server"][0]
        print(json.dumps(capture(
            source=args.source, db=args.db, lock=args.lock, server=server,
            frontier=args.frontier, output=args.output), sort_keys=True))
    except (HeldoutNoiseError, stock.WorldSeedNoiseError, ValueError, OSError,
            KeyError, TypeError, sqlite3.Error, source_probe.ProbeError,
            projection.DiscoveryError, subprocess.TimeoutExpired,
            urllib.error.URLError) as exc:
        print("OFFICIAL STOCK 26.2 HELD-OUT WORLDSEED NOISE NOT QUALIFIED: "
              + str(exc), file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
