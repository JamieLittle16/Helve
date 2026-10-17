#!/usr/bin/env python3
"""Extract exactly the 19 pending R2C method bodies for local human review.

Reuse Vanilla Atlas declaration fingerprints and the existing source-range
reader, not another Java parser or registry discovery system. Source-RICH
output is local-only and must NEVER be committed to the repository. This
does not review delegates or issue VAR/SEM/source admission.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sqlite3
import sys
import zipfile
from pathlib import Path
from typing import Mapping, Sequence

import r1b_configuration_source_probe as source_probe
import r2c_final_review_focus as focus
import r2c_world_state_delegate_closure_source_review as closure
import vanilla_atlas

MAX_EXCERPT_LINES = 512
MAX_SOURCE_MEMBER_BYTES = 4 * 1024 * 1024
MAX_TOTAL_EXCERPT_BYTES = 512 * 1024
ACCEPTED_FOCUS_KINDS = frozenset({
    "r2c-26_2-first-pass-source-review-focus-v1",
    "r2c-inventory-first-pass-review-focus-v1",
})


class LocalReviewError(ValueError):
    """The exact 26.2 source-review boundary cannot be established."""


def _sha256(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def select_review_entries(document: Mapping[str, object]) -> list[tuple[str, dict]]:
    """Check the complete first-pass selection without treating it as admission."""
    if (document.get("schema") != 1
            or document.get("kind") not in ACCEPTED_FOCUS_KINDS
            or document.get("source_archive_sha256") != focus.existing.EXPECTED_SHA
            or document.get("first_pass_only") is not True
            or document.get("biome_client_ids_admitted") is not False
            or document.get("heightmap_predicates_admitted") is not False
            or document.get("live_world_publication_admitted", False) is not False
            or document.get("production_admitted", False) is not False):
        raise LocalReviewError("source focus pin, scope or nonadmission flags drifted")
    if (document.get("delegate_closure_proven", False) is not False
            or document.get("exhaustive_delegate_closure_claimed", False) is not False
            or document.get("outer_wire_admitted", False) is not False
            or document.get("chunk_wire_admitted", False) is not False):
        raise LocalReviewError("review focus must not claim admission or delegate closure")

    entries: list[tuple[str, dict]] = []
    identities: set[str] = set()
    for key, planned in (("biome_priority", focus.BIOME), ("outer_wire_priority", focus.WIRE)):
        group = document.get(key)
        if not isinstance(group, list) or len(group) != len(planned):
            raise LocalReviewError(f"{key} must contain its exact frozen review roots")
        for candidate, (owner, signature_prefix) in zip(group, planned, strict=True):
            if not isinstance(candidate, dict):
                raise LocalReviewError("method selection is not an object")
            identity = candidate.get("source")
            if (not isinstance(identity, str)
                    or not identity.startswith(owner + "#" + signature_prefix)
                    or identity in identities
                    or candidate.get("source_inspected") is not False
                    or candidate.get("semantics_admitted") is not False
                    or not isinstance(candidate.get("hazard_leads"), list)
                    or not all(isinstance(candidate.get(field), str)
                               and len(candidate[field]) == 64
                               for field in ("normalized_sha256", "body_sha256"))):
                raise LocalReviewError("selected method is not the exact unreviewed Atlas root")
            identities.add(identity)
            entries.append((key, candidate))
    return entries


def read_exact_source(
    conn: sqlite3.Connection,
    source_zip: zipfile.ZipFile,
    entries: Sequence[tuple[str, Mapping[str, object]]],
) -> list[dict]:
    """Match each entire declaration and body fingerprint before reading source."""
    cache: dict[str, list[str]] = {}
    extracted: list[dict] = []
    total_bytes = 0
    for index, (group, item) in enumerate(entries, 1):
        identity = str(item["source"])
        owner, signature = identity.split("#", 1)
        rows = conn.execute(
            closure._ROW_SELECT
            + " WHERE t.qualified_name=? AND m.signature=? ORDER BY m.id",
            (owner, signature),
        ).fetchall()
        if len(rows) != 1:
            raise LocalReviewError(f"source owner/signature missing or ambiguous: {identity}")
        row = rows[0]
        source_record = source_probe.record_template(
            conn, row, f"DISC-NET-R2C-FIRST-PASS-{index:03d}"
        )
        source = source_record["source"]
        if (source["type"] != owner
                or source["signature"] != signature
                or source["fingerprint_algorithm"] != "java-token-v2-literal-sensitive"
                or source["normalized_sha256"] != item["normalized_sha256"]
                or source["body_sha256"] != item["body_sha256"]
                or source_record["atlas_observed_hazards"] != item["hazard_leads"]):
            raise LocalReviewError(f"source method/hazard fingerprint drift: {identity}")
        member = closure._safe_member(row["path"])
        try:
            info = source_zip.getinfo(member)
        except KeyError as error:
            raise LocalReviewError(f"pinned source path absent: {identity}") from error
        if info.file_size > MAX_SOURCE_MEMBER_BYTES:
            raise LocalReviewError(f"source Java member too large for review: {identity}")
        excerpt = closure._source_excerpt(
            source_zip, row, max_lines=MAX_EXCERPT_LINES, cache=cache
        )
        total_bytes += len(excerpt)
        if total_bytes > MAX_TOTAL_EXCERPT_BYTES:
            raise LocalReviewError("local source excerpts exceed the frozen total size bound")
        extracted.append({
            "review_index": index,
            "group": group,
            "source": identity,
            "normalized_sha256": source["normalized_sha256"],
            "body_sha256": source["body_sha256"],
            "atlas_observed_hazards": source_record["atlas_observed_hazards"],
            "source_path": member,
            "source_start_line": row["start_line"],
            "source_end_line": row["end_line"],
            "source_excerpt": excerpt.decode("utf-8"),
            "source_excerpt_sha256": _sha256(excerpt),
            "calls": closure._call_inventory(conn, int(row["id"])),
            "source_inspected": False,
            "semantics_admitted": False,
        })
    return extracted


def run(
    *,
    review_focus: Path,
    source_archive: Path,
    db: Path,
    lock: Path,
    output: Path,
) -> dict:
    if output.exists() or output.is_symlink():
        raise LocalReviewError("local source-rich output must not already exist")
    if output.resolve(strict=False).is_relative_to(focus.existing.ROOT.resolve(strict=True)):
        raise LocalReviewError("local source-rich review must remain outside the repository")
    if review_focus.is_symlink() or not review_focus.is_file():
        raise LocalReviewError("focus document must be an existing regular file")
    raw = review_focus.read_bytes()
    if not 0 < len(raw) <= 100_000:
        raise LocalReviewError("source-free focus report byte count is not bounded")
    document = json.loads(raw)
    if not isinstance(document, dict):
        raise LocalReviewError("review focus is not an object")
    selected = select_review_entries(document)

    conn = vanilla_atlas.connect_db(db)
    try:
        source_sha = source_probe.require_pinned_source(conn, source_archive, lock)
        if source_sha != focus.existing.EXPECTED_SHA:
            raise LocalReviewError("local official source identity does not match R2C")
        with zipfile.ZipFile(source_archive) as source_zip:
            records = read_exact_source(conn, source_zip, selected)
    finally:
        conn.close()

    report = {
        "schema": 1,
        "kind": "r2c-26_2-local-first-pass-source-excerpts-v1",
        "source_archive_sha256": source_sha,
        "focus_sha256": _sha256(raw),
        "commit_policy": "EPHEMERAL_SOURCE_RICH_DO_NOT_COMMIT",
        "contains_official_source_text": True,
        "first_pass_only": True,
        "human_source_review_complete": False,
        "delegate_closure_proven": False,
        "client_biome_ids_admitted": False,
        "heightmap_predicates_admitted": False,
        "chunk_wire_admitted": False,
        "production_admitted": False,
        "method_count": len(records),
        "review_methods": records,
    }
    data = (json.dumps(report, indent=2, ensure_ascii=False, sort_keys=True) + "\n").encode("utf-8")
    output.parent.mkdir(parents=True, exist_ok=True)
    # A private local file, created only after all 19 method records pass.
    fd = os.open(output, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    with os.fdopen(fd, "wb") as stream:
        stream.write(data)
    return {"source_method_count": len(records), "local_review_bytes": len(data),
            "output": str(output), "source_admitted": False}


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--focus", type=Path, required=True)
    parser.add_argument("--source", type=Path, default=closure.DEFAULT_SOURCE)
    parser.add_argument("--db", type=Path, default=closure.DEFAULT_DB)
    parser.add_argument("--lock", type=Path, default=closure.DEFAULT_LOCK)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        summary = run(
            review_focus=args.focus,
            source_archive=args.source,
            db=args.db,
            lock=args.lock,
            output=args.output,
        )
    except (LocalReviewError, source_probe.ProbeError, closure.ClosureError,
            sqlite3.Error, OSError, ValueError, TypeError, KeyError,
            json.JSONDecodeError, zipfile.BadZipFile) as error:
        print(f"R2C exact source-review extraction failed closed: {error}", file=sys.stderr)
        return 2
    print(json.dumps(summary, sort_keys=True))
    print("Official-source excerpts remain LOCAL-ONLY; review needed; no VAR/SEM promotion")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
