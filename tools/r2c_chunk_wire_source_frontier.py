#!/usr/bin/env python3
"""Inspect the finite, still-unadmitted Minecraft 26.2 chunk-with-light wire frontier.

Binds a reviewer-owned pinned official source ZIP and disposable Vanilla Atlas
database to the canonical lock, then emits source-free declaration fingerprints
for exactly four existing R2C wire/publication roots.  No output implies that
the packet identity, byte order, saved block-entity law, pacing, or client biome
IDs have been admitted. Those require inspected, closed VAR/SEM source records.

All source-review output MUST stay outside the repository; official Java source
text is never reproduced, copied, or committed by this tool.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sqlite3
import sys
from pathlib import Path
from typing import Any, Sequence

import r1b_configuration_source_probe as source_probe
import r2c_world_projection_source_review as projection
import vanilla_atlas

REPO_ROOT = Path(__file__).resolve().parents[1]
PLAN = REPO_ROOT / "vanilla/reviews/network/r2c-chunk-wire-source-frontier.json"
KIND = "r2c-chunk-wire-source-declarations-unadmitted-v1"
PLAN_ID = "REVIEW-NET-R2C-CHUNK-WIRE-26_2-001"
SOURCE_SHA256 = "1e9bca3dff83cd83e7905f8810f1ec9899361fa2dc83fe893bb48beeb04df750"
# An Atlas SHA-256 of zero body bytes is a declaration anchor, not executable
# implementation evidence (seen on abstract Registry interface methods).
EMPTY_BODY_SHA256 = hashlib.sha256(b"").hexdigest()
TARGET = {"minecraft": "26.2", "protocol": 776, "data_version": 4903}
ROOTS = (
    ("CHUNK-PACKET-ENVELOPE", "net.minecraft.network.protocol.game.ClientboundLevelChunkWithLightPacket"),
    ("CHUNK-DATA-AND-EMPTY-ENTITIES", "net.minecraft.network.protocol.game.ClientboundLevelChunkPacketData"),
    ("INITIAL-LIGHT-FIELDS", "net.minecraft.network.protocol.game.ClientboundLightUpdatePacketData"),
    ("INITIAL-CHUNK-PUBLICATION", "net.minecraft.server.network.PlayerChunkSender"),
)
MAX_METHODS = 256


class ChunkWireSourceError(ValueError):
    """The selected chunk-wire source inventory cannot be established safely."""


def load_plan(path: Path) -> tuple[dict[str, object], ...]:
    """Require the exact pinned review roots, obligations and status."""
    if path.is_symlink() or not path.is_file():
        raise ChunkWireSourceError("review plan must be a regular file, not a link")
    try:
        doc = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ChunkWireSourceError(f"cannot load review plan: {error}") from error
    if not isinstance(doc, dict) or set(doc) != {
        "schema", "id", "target", "source_archive_sha256", "status",
        "max_methods_per_type", "roots",
    }:
        raise ChunkWireSourceError("review plan fields are not the frozen schema")
    if (
        type(doc["schema"]) is not int or doc["schema"] != 1
        or doc["id"] != PLAN_ID or doc["target"] != TARGET
        or doc["source_archive_sha256"] != SOURCE_SHA256
        or doc["status"] != "DISCOVERY_NOT_ADMISSION"
        or type(doc["max_methods_per_type"]) is not int
        or doc["max_methods_per_type"] != MAX_METHODS
    ):
        raise ChunkWireSourceError("pinned source target/ID/bounds/admission status drifted")
    roots = doc["roots"]
    if not isinstance(roots, list) or len(roots) != len(ROOTS):
        raise ChunkWireSourceError("four exact chunk-wire source roots are mandatory")
    for i, (actual, (expected_group, expected_type)) in enumerate(zip(roots, ROOTS)):
        if not isinstance(actual, dict) or set(actual) != {
            "group", "type", "must_review",
        }:
            raise ChunkWireSourceError(f"root {i} has unreviewed fields")
        obligations = actual["must_review"]
        if (actual["group"] != expected_group or actual["type"] != expected_type
            or not isinstance(obligations, list) or len(obligations) < 2
            or len(obligations) > 5 or len(set(map(str, obligations))) != len(obligations)
            or any(not isinstance(q, str) or not 16 <= len(q) <= 240 for q in obligations)):
            raise ChunkWireSourceError(f"root {i} identity or review obligations drifted")
    return tuple(roots)


def exact_declarations(conn: sqlite3.Connection, name: str) -> list[dict[str, object]]:
    """Produce source-free declaration identities, including abstract-only status."""
    try:
        rows = projection._exact_type_methods(conn, name, MAX_METHODS)
    except (projection.DiscoveryError, sqlite3.Error) as error:
        raise ChunkWireSourceError(
            f"missing/ambiguous/excessive pinned source class {name}: {error}"
        ) from error
    if not rows:
        raise ChunkWireSourceError(f"no pinned method declarations for {name}")
    result: list[dict[str, object]] = []
    for index, row in enumerate(rows):
        template = source_probe.record_template(
            conn, row, f"INDEX-NET-R2C-CHUNK-WIRE-{index + 1:03d}"
        )
        source = template.get("source")
        if not isinstance(source, dict) or source.get("type") != name:
            raise ChunkWireSourceError("Atlas source owner drift")
        if not all(isinstance(source.get(f), str) and source[f]
                   for f in ("signature", "normalized_sha256", "fingerprint_algorithm")):
            raise ChunkWireSourceError("missing declaration signature/hash")
        body = source.get("body_sha256")
        if body is not None and not isinstance(body, str):
            raise ChunkWireSourceError("invalid method-body fingerprint")
        result.append({
            "signature": source["signature"],
            "normalized_sha256": source["normalized_sha256"],
            "body_sha256": body,
            "declaration_only": body is None or body == EMPTY_BODY_SHA256,
            "hazard_leads": template["atlas_observed_hazards"],
        })
    return result


def source_free_inventory(
    conn: sqlite3.Connection,
    roots: tuple[dict[str, object], ...],
    *,
    source_sha256: str,
    plan_sha256: str,
) -> dict[str, object]:
    """Inventory names, hashes and source-review questions, NEVER approval."""
    if source_sha256 != SOURCE_SHA256:
        raise ChunkWireSourceError("source archive is not the pinned official 26.2 ZIP")
    groups = []
    for root in roots:
        name = root["type"]
        if not isinstance(name, str):
            raise ChunkWireSourceError("invalid exact root type")
        groups.append({
            "group": root["group"],
            "type": name,
            "questions_not_yet_answered": root["must_review"],
            "declarations": exact_declarations(conn, name),
        })
    return {
        "schema": 1,
        "kind": KIND,
        "target": TARGET,
        "source_archive_sha256": source_sha256,
        "review_plan_sha256": plan_sha256,
        "groups": groups,
        "source_inspected": False,
        "packet_wire_law_proven": False,
        "block_entity_semantics_proven": False,
        "chunk_publication_order_proven": False,
        "production_admitted": False,
        "remaining_gates": [
            "source-inspected exact packet registration and payload VAR/SEM",
            "source-inspected block entity absent/empty and nonempty inclusion VAR/SEM",
            "source-inspected chunk publication/pacing VAR/SEM",
            "separate numeric biome registry client-assignment gate #285",
        ],
    }


def validate_output(path: Path) -> None:
    """Never overwrite a local report or place source-review output in this repository."""
    if path.exists() or path.is_symlink():
        raise ChunkWireSourceError("source inventory output must be a fresh nonexisting path")
    if path.resolve(strict=False).is_relative_to(REPO_ROOT.resolve(strict=True)):
        raise ChunkWireSourceError("source inventory must be written outside the repository")


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=projection.DEFAULT_SOURCE)
    parser.add_argument("--db", type=Path, default=projection.DEFAULT_DB)
    parser.add_argument("--lock", type=Path, default=projection.DEFAULT_LOCK)
    parser.add_argument("--plan", type=Path, default=PLAN)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        roots = load_plan(args.plan)
        validate_output(args.output)
        conn = vanilla_atlas.connect_db(args.db)
        try:
            source_sha = source_probe.require_pinned_source(conn, args.source, args.lock)
            report = source_free_inventory(
                conn, roots, source_sha256=source_sha,
                plan_sha256=hashlib.sha256(args.plan.read_bytes()).hexdigest(),
            )
        finally:
            conn.close()
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(report, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    except (OSError, ChunkWireSourceError, source_probe.ProbeError,
            sqlite3.Error, ValueError) as error:
        print(f"R2C chunk-wire source inventory rejected: {error}", file=sys.stderr)
        return 2
    print("Prepared source-free packet source inventory; NO packet, registry, or Play admission")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
