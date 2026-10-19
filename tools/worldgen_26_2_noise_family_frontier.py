#!/usr/bin/env python3
"""Source-free, non-admitting local 26.2 Perlin/Normal/density source frontier.

Requires the exact pinned private ZIP *and* matching disposable Vanilla Atlas.
Emits method identities/hashes/call-site diagnostics, never Java source text
or code snippets. A source index is NOT a reviewed source or parity proof.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sqlite3
import sys
import tomllib
from pathlib import Path

import r1b_configuration_source_probe as source_probe
import r2c_world_projection_source_review as projection
import vanilla_atlas
from worldgen_26_2_improved_noise_capture import external_output

ROOT = Path(__file__).resolve().parents[1]
OWNERS = {
    "perlin_noise": "net.minecraft.world.level.levelgen.synth.PerlinNoise",
    "normal_noise": "net.minecraft.world.level.levelgen.synth.NormalNoise",
    "density_functions": "net.minecraft.world.level.levelgen.DensityFunctions",
    "noise_router": "net.minecraft.world.level.levelgen.NoiseRouter",
}
SHA256 = re.compile(r"[0-9a-f]{64}\Z")
MAX_METHODS = 128


class FrontierError(ValueError):
    """Missing, excessive or misleading Atlas source-review evidence."""


def _hash_or_none(value: object) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str) or SHA256.fullmatch(value) is None:
        raise FrontierError("Atlas returned an invalid exact SHA-256 method fingerprint")
    return value


def inventory(conn: sqlite3.Connection) -> dict[str, object]:
    """Read only bounded method metadata for the four explicitly selected roots."""
    roots: dict[str, object] = {}
    for label, owner in OWNERS.items():
        rows = projection._exact_type_methods(conn, owner, MAX_METHODS)
        if not rows:
            raise FrontierError(f"selected noise/density type has no indexed declarations: {owner}")
        items: list[dict[str, object]] = []
        observed = set()
        for index, row in enumerate(rows):
            method_id = int(row["id"])
            signature = str(row["signature"])
            if not signature or signature in observed:
                raise FrontierError(f"ambiguous or empty declaration in {owner}")
            observed.add(signature)
            candidate_id = f"INDEX-WORLDGEN-26_2-{label.upper()}-{index + 1:03d}"
            template = source_probe.record_template(conn, row, candidate_id)
            source = template["source"]
            if not isinstance(source, dict) or source.get("type") != owner:
                raise FrontierError("Atlas method identity disagrees with the selected owner")
            if source.get("signature") != signature:
                raise FrontierError("Atlas method signature disagrees with the selected row")
            calls = projection._call_inventory(conn, method_id)
            items.append({
                "candidate_id": candidate_id,
                "signature": signature,
                "body_sha256": _hash_or_none(source.get("body_sha256")),
                "normalized_sha256": _hash_or_none(source.get("normalized_sha256")),
                "call_sites": calls["call_sites"],
                "resolved_targets": calls["resolved_targets"],
                "unresolved_call_sites": calls["unresolved_call_sites"],
                "top_unresolved_callees": calls["top_unresolved_callees"],
                "atlas_observed_hazards": template.get("atlas_observed_hazards", []),
                "declaration_only": source.get("body_sha256") is None,
            })
        roots[label] = {
            "owner": owner,
            "method_count": len(items),
            "methods": items,
        }
    return roots


def capture(*, source: Path, db: Path, lock: Path, output: Path) -> dict[str, object]:
    destination = external_output(output)
    with lock.open("rb") as reader:
        locked = tomllib.load(reader)
    if (locked.get("minecraft") != "26.2" or locked.get("protocol") != 776
        or locked.get("data_version") != 4903):
        raise FrontierError("source lock is not the pinned Minecraft Java 26.2 profile")

    conn = vanilla_atlas.connect_db(db)
    try:
        source_hash = source_probe.require_pinned_source(conn, source, lock)
        roots = inventory(conn)
    finally:
        conn.close()

    report = {
        "schema": 1,
        "kind": "worldgen_26_2_source_method_index_not_sem_admitted",
        "minecraft": "26.2",
        "protocol": 776,
        "data_version": 4903,
        "source_archive_sha256": source_hash,
        "official_server_sha256": locked["runtime"]["server_sha256"],
        "source_text_included": False,
        "independent_var_sem_admitted": False,
        "production_worldgen_enabled": False,
        "note": "Method identities and call-site diagnostics only; no source semantics, verified constructor recipes, or output vectors",
        "roots": roots,
    }
    payload = (json.dumps(report, indent=2, sort_keys=True) + "\n").encode("utf-8")
    destination.parent.mkdir(parents=True, exist_ok=True)
    # Exclusive creation: never overwrite earlier official-source evidence.
    with destination.open("xb") as stream:
        stream.write(payload)
    return {
        "output": str(destination),
        "source_index_sha256": hashlib.sha256(payload).hexdigest(),
        "root_types": len(roots),
        "method_declarations": sum(group["method_count"] for group in roots.values()),
        "independent_var_sem_admitted": False,
        "production_worldgen_enabled": False,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=Path.home() / "Documents/mc-source/mc-src.zip")
    parser.add_argument("--db", type=Path, default=ROOT / ".crucible/vanilla/atlas.sqlite")
    parser.add_argument("--lock", type=Path, default=ROOT / "vanilla/vanilla.lock.toml")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        result = capture(source=args.source, db=args.db, lock=args.lock, output=args.output)
    except (FrontierError, source_probe.ProbeError, projection.DiscoveryError,
            OSError, KeyError, ValueError, sqlite3.Error, TypeError) as error:
        print(f"26.2 noise-family source frontier NOT QUALIFIED: {error}", file=sys.stderr)
        return 1
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
