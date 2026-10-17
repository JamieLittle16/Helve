#!/usr/bin/env python3
"""Inspect the finite, still-unadmitted 26.2 biome numeric-ID source frontier.

This is a SOURCE-FREE declaration/fingerprint inventory, never an admission.
A pinned local official source zip and its disposable Atlas database are
mandatory, but no Mojang source text is copied into the emitted JSON.
Reviewers must inspect each selected declaration and its delegates locally,
author source-bound VAR/SEM and pass an independent source gate separately.

This is intentionally separate from the previously admitted R2C biome
palette/storage source group. ById values + Configuration ordinals matching
does not, by itself, certify the client registry-assignment law.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sqlite3
import sys
from pathlib import Path
from typing import Mapping, Sequence

import r1b_configuration_source_probe as source_probe
import r2c_world_projection_source_review as projection
import vanilla_atlas

KIND = "r2c-biome-id-source-declaration-inventory-v1"
SOURCE_SHA256 = "1e9bca3dff83cd83e7905f8810f1ec9899361fa2dc83fe893bb48beeb04df750"
PLAN_ID = "REVIEW-NET-R2C-BIOME-IDS-26_2-001"
TARGET = {"minecraft": "26.2", "protocol": 776, "data_version": 4903}
REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PLAN = REPO_ROOT / "vanilla/reviews/network/r2c-biome-id-source-frontier.json"


class BiomeIdSourceError(ValueError):
    """The bounded pinned-source inventory cannot be established."""


def load_plan(path: Path) -> tuple[tuple[str, tuple[str, ...]], ...]:
    if path.is_symlink() or not path.is_file():
        raise BiomeIdSourceError("source review plan must be an existing regular file")
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or set(data) != {
        "schema", "id", "target", "source_archive_sha256",
        "status", "groups", "max_methods_per_type", "targeted_methods",
    }:
        raise BiomeIdSourceError("source plan keys differ from frozen schema")
    if (data["schema"] != 1 or data["id"] != PLAN_ID
        or data["target"] != TARGET or data["source_archive_sha256"] != SOURCE_SHA256
        or data["status"] != "DISCOVERY_NOT_ADMISSION"
        or data["max_methods_per_type"] != 256):
        raise BiomeIdSourceError("source plan identity, bounds or admission status drifted")
    # Util contains many unrelated helpers; only inspect the exact ordered
    # future-sequencing delegate rather than broadening the 256-method cap.
    if data["targeted_methods"] != [{
        "type": "net.minecraft.util.Util",
        "method": "sequence",
        "max_overloads": 16,
        "review_focus": (
            "Prove ordered completion of the network registry List<CompletableFuture> "
            "in Util.sequence, including exceptional completion and non-reordering; "
            "independent proof of actual stock 26.2 client Configuration handler "
            "invocation remains outstanding."
        ),
    }]:
        raise BiomeIdSourceError("bounded Util.sequence source review target drifted")
    groups = data["groups"]
    if not isinstance(groups, list) or len(groups) != 4:
        raise BiomeIdSourceError("four finite lifecycle groups are required")
    expected = (
        "LOADED-REGISTRY-ID-ALLOCATION",
        "CONFIGURATION-BIOME-ENTRY-PUBLICATION",
        "BIOME-CONTAINER-ID-BINDING",
        "NETWORK-REGISTRY-RECEIVE-AND-ORDERED-REGISTRATION",
    )
    seen: set[str] = set()
    result: list[tuple[str, tuple[str, ...]]] = []
    for i, group in enumerate(groups):
        if not isinstance(group, dict) or set(group) != {"id", "types", "review_focus"}:
            raise BiomeIdSourceError(f"group {i} has unreviewed metadata")
        key = group["id"]
        types = group["types"]
        if (key != expected[i] or not isinstance(group["review_focus"], str)
            or not group["review_focus"] or not isinstance(types, list)
            or not types or any(not isinstance(t, str)
            or not t.startswith("net.minecraft.") for t in types)
            or len(set(types)) != len(types)):
            raise BiomeIdSourceError(f"group {i} is malformed")
        for name in types:
            if name in seen:
                raise BiomeIdSourceError(f"duplicate declaration root {name}")
            seen.add(name)
        result.append((key, tuple(types)))
    return tuple(result)


def exact_type_declarations(
    conn: sqlite3.Connection, qualified_name: str,
    *,
    method_cap: int = 256,
) -> list[dict[str, object]]:
    if not 1 <= method_cap <= 256:
        raise BiomeIdSourceError("method cap exceeds frozen review bounds")
    try:
        rows = projection._exact_type_methods(conn, qualified_name, method_cap)
    except (projection.DiscoveryError, sqlite3.Error) as error:
        raise BiomeIdSourceError(
            f"missing, ambiguous or excessive official type: {qualified_name}: {error}"
        ) from error
    if not rows:
        raise BiomeIdSourceError(f"official root has no methods: {qualified_name}")
    results: list[dict[str, object]] = []
    for i, row in enumerate(rows):
        template = source_probe.record_template(
            conn, row, f"INDEX-NET-R2C-BIOME-ID-{i + 1:03d}"
        )
        source = template.get("source")
        if not isinstance(source, dict) or source.get("type") != qualified_name:
            raise BiomeIdSourceError("Atlas declaration fingerprint/source owner drifted")
        if not all(
            isinstance(source.get(key), str) and source[key]
            for key in ("signature", "fingerprint_algorithm", "normalized_sha256")
        ):
            raise BiomeIdSourceError("Atlas returned incomplete declaration fingerprints")
        body_sha = source.get("body_sha256")
        if body_sha is not None and not isinstance(body_sha, str):
            raise BiomeIdSourceError("Atlas returned a malformed method body fingerprint")
        # Interfaces and abstract declarations can carry a source signature
        # without a method body. Their source-bound declaration hash remains
        # useful discovery evidence; they cannot be elevated to a reviewed
        # *implementation* without following the concrete delegate.
        results.append({
            "signature": source["signature"],
            "normalized_sha256": source["normalized_sha256"],
            "body_sha256": body_sha,
            "declaration_only": body_sha is None,
            "hazard_leads": template["atlas_observed_hazards"],
        })
    return results



def exact_named_declarations(
    conn: sqlite3.Connection,
    qualified_name: str,
    method_name: str,
    *,
    overload_cap: int = 16,
) -> list[dict[str, object]]:
    """Find a bounded concrete delegate without scanning every Util method."""
    if not (1 <= overload_cap <= 16):
        raise BiomeIdSourceError("named delegate overload cap exceeds review bounds")
    if qualified_name != "net.minecraft.util.Util" or method_name != "sequence":
        raise BiomeIdSourceError("unplanned named delegate")
    try:
        type_rows = conn.execute(projection._TYPE_SELECT, (qualified_name,)).fetchall()
        if len(type_rows) != 1:
            raise BiomeIdSourceError(
                f"named delegate owner must resolve once: {qualified_name}"
            )
        rows = conn.execute(
            """SELECT m.id,t.qualified_name,m.name,m.signature,m.param_count,
                      m.start_line,m.end_line,f.path
               FROM methods m
               JOIN types t ON t.id=m.type_id
               JOIN source_files f ON f.id=t.file_id
               WHERE t.qualified_name=? AND m.name=?
               ORDER BY m.start_line,m.id""",
            (qualified_name, method_name),
        ).fetchall()
        if not rows or len(rows) > overload_cap:
            raise BiomeIdSourceError(
                f"named delegate missing or too broad: {qualified_name}#{method_name}"
            )
        result: list[dict[str, object]] = []
        for index, row in enumerate(rows):
            template = source_probe.record_template(
                conn, row, f"INDEX-NET-R2C-BIOME-ID-ORDER-{index + 1:03d}"
            )
            source = template.get("source")
            if (not isinstance(source, dict)
                or source.get("type") != qualified_name
                or not all(isinstance(source.get(field), str) and source[field]
                           for field in ("signature", "normalized_sha256"))):
                raise BiomeIdSourceError("incomplete named delegate fingerprint")
            body_sha = source.get("body_sha256")
            if body_sha is not None and not isinstance(body_sha, str):
                raise BiomeIdSourceError("malformed named delegate body fingerprint")
            result.append({
                "signature": source["signature"],
                "normalized_sha256": source["normalized_sha256"],
                "body_sha256": body_sha,
                "declaration_only": body_sha is None,
                "hazard_leads": template["atlas_observed_hazards"],
            })
        return result
    except sqlite3.Error as error:
        raise BiomeIdSourceError(f"named delegate Atlas lookup failed: {error}") from error


def inventory(
    conn: sqlite3.Connection,
    groups: tuple[tuple[str, tuple[str, ...]], ...],
    *,
    source_sha256: str,
    plan_sha256: str,
    include_ordered_sequence: bool = False,
) -> dict[str, object]:
    if source_sha256 != SOURCE_SHA256:
        raise BiomeIdSourceError("pinned source identity mismatch")
    rows: list[dict[str, object]] = []
    for group, types in groups:
        roots = [
            {"type": name, "methods": exact_type_declarations(conn, name)}
            for name in types
        ]
        rows.append({"group": group, "roots": roots})
    return {
        "schema": 1,
        "kind": KIND,
        "target": TARGET,
        "source_archive_sha256": source_sha256,
        "source_review_plan_sha256": plan_sha256,
        "groups": rows,
        "targeted_methods": ([{
            "type": "net.minecraft.util.Util",
            "method": "sequence",
            "overloads": exact_named_declarations(conn, "net.minecraft.util.Util", "sequence"),
        }] if include_ordered_sequence else []),
        "source_inspected": False,
        "client_assignment_proven": False,
        "production_admitted": False,
        "remaining_gate": "exact registry allocation, network packing, common receive-registration ordering and actual client Configuration invocation VAR/SEM",
    }


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=projection.DEFAULT_SOURCE)
    parser.add_argument("--db", type=Path, default=projection.DEFAULT_DB)
    parser.add_argument("--lock", type=Path, default=projection.DEFAULT_LOCK)
    parser.add_argument("--plan", type=Path, default=DEFAULT_PLAN)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        groups = load_plan(args.plan)
        if args.output.exists() or args.output.is_symlink():
            raise BiomeIdSourceError("output must be a fresh file")
        resolved = args.output.resolve(strict=False)
        if resolved.is_relative_to(REPO_ROOT.resolve(strict=True)):
            raise BiomeIdSourceError("local source-review inventory must stay outside repository")
        conn = vanilla_atlas.connect_db(args.db)
        try:
            source_sha = source_probe.require_pinned_source(
                conn, args.source, args.lock
            )
            bundle = inventory(
                conn, groups,
                source_sha256=source_sha,
                plan_sha256=hashlib.sha256(args.plan.read_bytes()).hexdigest(),
                include_ordered_sequence=True,
            )
        finally:
            conn.close()
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(
            json.dumps(bundle, sort_keys=True, indent=2) + "\n", encoding="utf-8"
        )
    except (BiomeIdSourceError, source_probe.ProbeError, OSError,
            ValueError, sqlite3.Error, json.JSONDecodeError) as error:
        print(f"R2C biome ID source discovery failed: {error}", file=sys.stderr)
        return 2
    print("Source-free loaded-biome-ID declaration inventory prepared; "
          "human source review, client registry assignment and gate STILL REQUIRED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
