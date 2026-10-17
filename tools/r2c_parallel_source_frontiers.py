#!/usr/bin/env python3
"""Run the two remaining pinned official-source frontier inventories in parallel.

This produces source-free *review inputs only*. Running a source inventory,
even twice, never grants VAR/SEM, client numeric IDs or chunk publication.
Only separately inspected human decisions and an independent Atlas gate can
establish admission. The 32,366-state heightmap runtime oracle runs in its
existing separate official Java workflow.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXPECTED_SHA = "1e9bca3dff83cd83e7905f8810f1ec9899361fa2dc83fe893bb48beeb04df750"
TARGET = {"minecraft": "26.2", "protocol": 776, "data_version": 4903}
ADMITTED_WORLD_STATE = ROOT / (
    "vanilla/reports/r2c-world-state-source-admission-26.2.json"
)
WORLD_STATE_GATE_ID = "GATE-NET-R2C-WORLD-STATE-26_2-001"
# These two wire roots overlap the *already admitted* inner world-state
# semantics. Reuse only exact declaration/body fingerprints, NEVER the
# broader outer packet ID, bootstrap, empty-entity or ACK claims.
REUSABLE_WIRE_ROOTS = frozenset({
    "net.minecraft.network.protocol.game.ClientboundLevelChunkPacketData",
    "net.minecraft.network.protocol.game.ClientboundLightUpdatePacketData",
})

JOBS = {
    "biome_client_ids": (
        "r2c_biome_id_source_frontier.py",
        "biome-client-id-source-inventory.json",
    ),
    "chunk_wire": (
        "r2c_chunk_wire_source_frontier.py",
        "chunk-wire-source-inventory.json",
    ),
}


def sha256(path: Path) -> str:
    checksum = hashlib.sha256()
    with path.open("rb") as data:
        while block := data.read(1 << 20):
            checksum.update(block)
    return checksum.hexdigest()


def check_one(label: str, path: Path) -> dict:
    if path.is_symlink() or not path.is_file():
        raise ValueError(f"{label}: report missing or symlinked")
    raw = path.read_bytes()
    if not 0 < len(raw) < 5_000_000:
        raise ValueError(f"{label}: report byte count outside finite bound")
    obj = json.loads(raw)
    if not isinstance(obj, dict) or obj.get("schema") != 1:
        raise ValueError(f"{label}: unsupported report schema")
    if obj.get("target") != TARGET or obj.get("source_archive_sha256") != EXPECTED_SHA:
        raise ValueError(f"{label}: report source/target does not match 26.2 pin")
    if obj.get("source_inspected") is not False or obj.get("production_admitted") is not False:
        raise ValueError(f"{label}: source discovery cannot claim source admission")
    if label == "biome_client_ids":
        if (obj.get("client_assignment_proven") is not False
            or not isinstance(obj.get("groups"), list)
            or len(obj["groups"]) != 4):
            raise ValueError("biome numeric ID candidate boundaries drifted")
    if label == "chunk_wire":
        if (obj.get("packet_wire_law_proven") is not False
            or obj.get("block_entity_semantics_proven") is not False
            or obj.get("chunk_publication_order_proven") is not False
            or not isinstance(obj.get("groups"), list)
            or len(obj["groups"]) != 4):
            raise ValueError("outer chunk wire candidate boundaries drifted")
    return {"filename": path.name, "bytes": len(raw),
            "sha256": hashlib.sha256(raw).hexdigest(),
            "method_group_count": len(obj["groups"]),
            "source_inspected": False, "production_admitted": False}


def exact_admitted_world_state_reuse(
    wire_inventory: dict, admitted_report: dict,
) -> list[dict[str, object]]:
    """Carry forward *only* independently gated exact inner-wire methods.

    An identical method fingerprint may support reuse of the previously
    reviewed semantic claims; it does not automatically admit the packet
    envelope, first Play ordering, block entities or publication pacing.
    """
    source = admitted_report.get("source")
    if (
        admitted_report.get("schema") != 1
        or admitted_report.get("admitted") is not True
        or admitted_report.get("source_free_bundle_bound") is not True
        or admitted_report.get("failures") != []
        or admitted_report.get("gate_id") != WORLD_STATE_GATE_ID
        or not isinstance(source, dict)
        or source.get("archive_sha256") != EXPECTED_SHA
        or source.get("minecraft_version") != "26.2"
        or source.get("protocol_version") != "776"
        or source.get("world_version") != "4903"
        or source.get("fingerprint_algorithm") != "java-token-v2-literal-sensitive"
        or wire_inventory.get("source_archive_sha256") != EXPECTED_SHA
        or wire_inventory.get("source_inspected") is not False
        or wire_inventory.get("production_admitted") is not False
    ):
        raise ValueError("previous independent world-state source gate invalid or drifted")

    required = admitted_report.get("required_methods")
    groups = wire_inventory.get("groups")
    if not isinstance(required, list) or len(required) != 58 or not isinstance(groups, list):
        raise ValueError("source admission method set or wire inventory missing")

    by_source: dict[str, dict] = {}
    for record in required:
        if not isinstance(record, dict):
            raise ValueError("malformed existing independent VAR record")
        name = record.get("source")
        if (
            not isinstance(name, str) or not name
            or record.get("status") != "VAR_REVIEWED"
            or not isinstance(record.get("var_id"), str)
            or not isinstance(record.get("semantic_rules"), list)
            or not record["semantic_rules"]
            or not all(isinstance(record.get(key), str)
                       and len(record[key]) == 64
                       for key in ("normalized_sha256", "body_sha256"))
            or name in by_source
        ):
            raise ValueError("unusable, duplicated or unreviewed prior source record")
        by_source[name] = record

    reused: list[dict[str, object]] = []
    for group in groups:
        if not isinstance(group, dict):
            raise ValueError("malformed chunk-wire declaration group")
        owner = group.get("type")
        if owner not in REUSABLE_WIRE_ROOTS:
            continue
        methods = group.get("declarations")
        if not isinstance(methods, list):
            raise ValueError("missing inner wire declarations")
        for method in methods:
            if not isinstance(method, dict) or not isinstance(method.get("signature"), str):
                raise ValueError("invalid exact wire method signature")
            name = f"{owner}#{method['signature']}"
            record = by_source.get(name)
            if record is None:
                continue
            if (
                method.get("declaration_only") is not False
                or method.get("normalized_sha256") != record["normalized_sha256"]
                or method.get("body_sha256") != record["body_sha256"]
            ):
                raise ValueError(f"admitted source declaration fingerprint drift: {name}")
            reused.append({
                "source": name,
                "var_id": record["var_id"],
                "admitted_semantic_rules": record["semantic_rules"],
                "normalized_sha256": record["normalized_sha256"],
                "body_sha256": record["body_sha256"],
                "authority": "PRIOR_INDEPENDENT_WORLD_STATE_VAR_ONLY",
                "outer_chunk_wire_admitted": False,
            })
    if len(reused) != 7 or len({r["source"] for r in reused}) != 7:
        raise ValueError("expected seven exact previously admitted inner-wire declarations")
    return sorted(reused, key=lambda item: str(item["source"]))


# Only committed public declaration names and fixed error categories may cross
# the parallel subprocess boundary. The official source, its local paths, raw
# child tracebacks and arbitrary JVM/Atlas output must never be forwarded.
BIOME_REVIEW_TYPES = frozenset({
    "net.minecraft.core.MappedRegistry",
    "net.minecraft.core.Registry",
    "net.minecraft.resources.RegistryDataLoader",
    "net.minecraft.server.network.config.SynchronizeRegistriesTask",
    "net.minecraft.network.protocol.configuration.ClientboundRegistryDataPacket",
    "net.minecraft.world.level.chunk.PalettedContainerFactory",
    "net.minecraft.resources.NetworkRegistryLoadTask",
    "net.minecraft.resources.RegistryLoadTask",
})
NAMED_ORDER_DELEGATE = "net.minecraft.util.Util#sequence"


def safe_source_failure(label: str, stderr: str) -> str:
    """Surface actionable, source-free child errors, not raw subprocess text."""
    if label == "biome_client_ids":
        prefix = "R2C biome ID source discovery failed: "
        for line in stderr.splitlines():
            if not line.startswith(prefix):
                continue
            message = line[len(prefix):]
            missing = re.fullmatch(
                r"missing, ambiguous or excessive official type: (net\.minecraft\.[A-Za-z0-9_.$]+):.*",
                message,
            )
            if missing is not None and missing.group(1) in BIOME_REVIEW_TYPES:
                return (
                    "exact Atlas type lookup failed for " + missing.group(1)
                    + "; run the biome source probe directly to distinguish"
                    " absent/ambiguous/over-cap declarations"
                )
            if message == "named delegate owner must resolve once: net.minecraft.util.Util":
                return (
                    "pinned Atlas did not resolve the planned exact "
                    "net.minecraft.util.Util owner; compare the source ZIP's actual "
                    "Util.java package and the frozen review plan"
                )
            if message == "named delegate missing or too broad: " + NAMED_ORDER_DELEGATE:
                return "pinned Atlas has no bounded exact " + NAMED_ORDER_DELEGATE
            if message.startswith("Atlas/source lock mismatch:"):
                return "official source and Atlas metadata disagree with vanilla.lock.toml"
            if message.startswith("source archive SHA-256 does not match vanilla lock:"):
                return "official source archive does not match vanilla.lock.toml SHA-256"
            if message.startswith("source plan "):
                return "frozen biome source review plan rejected (identity or schema)"
            if message.startswith("named delegate Atlas lookup failed:"):
                return "bounded named-delegate Atlas query failed"
    elif label == "chunk_wire":
        prefix = "R2C chunk-wire source inventory rejected: "
        for line in stderr.splitlines():
            if line.startswith(prefix):
                message = line[len(prefix):]
                if message.startswith("missing/ambiguous/excessive pinned source class "):
                    return "exact chunk-wire Atlas class resolution failed (see direct probe)"
                if message.startswith("source archive SHA-256 does not match vanilla lock:"):
                    return "official source archive identity does not match vanilla.lock.toml"
                if message.startswith("Atlas/source lock mismatch:"):
                    return "official source and Atlas metadata disagree with vanilla.lock.toml"
    return (
        "diagnostic not safe to forward; run "
        + ("tools/r2c_biome_id_source_frontier.py" if label == "biome_client_ids"
           else "tools/r2c_chunk_wire_source_frontier.py")
        + " directly with the same --source/--db and a fresh --output"
    )


def run_one(label: str, script: str, path: Path, source: Path,
            db: Path, lock: Path) -> None:
    result = subprocess.run(
        [sys.executable, str(ROOT / "tools" / script),
         "--source", str(source), "--db", str(db),
         "--lock", str(lock), "--output", str(path)],
        capture_output=True, text=True, check=False, timeout=180,
    )
    if result.returncode:
        # Never forward arbitrary subprocess output derived from a local
        # proprietary official-source scan. Preserve only the failing label.
        raise ValueError(
            f"{label}: pinned source inventory failed closed "
            f"(exit {result.returncode}): "
            f"{safe_source_failure(label, result.stderr)}"
        )


def prepare(source: Path, db: Path, lock: Path, output_dir: Path) -> dict:
    if not source.is_file() or source.is_symlink() or sha256(source) != EXPECTED_SHA:
        raise ValueError("official source archive identity mismatch")
    if not db.is_file() or db.is_symlink() or not lock.is_file() or lock.is_symlink():
        raise ValueError("pinned local Atlas/lock must be real files")
    if output_dir.exists() or output_dir.is_symlink():
        raise ValueError("source-free output directory must not exist")
    if output_dir.resolve(strict=False).is_relative_to(ROOT.resolve()):
        raise ValueError("source review reports must stay outside the repository")
    parent = output_dir.parent
    if not parent.is_dir() or parent.is_symlink():
        raise ValueError("source report parent must be an existing non-symlink directory")
    with tempfile.TemporaryDirectory(prefix="helve-r2c-both-frontiers-", dir=parent) as scratch:
        staging = Path(scratch)
        with ThreadPoolExecutor(max_workers=2) as pool:
            work = [
                pool.submit(run_one, label, script, staging / filename,
                            source, db, lock)
                for label, (script, filename) in JOBS.items()
            ]
            for future in work:
                future.result()
        reports = {
            label: check_one(label, staging / filename)
            for label, (_, filename) in JOBS.items()
        }
        # This is a source-free intersection of the *already* independently
        # admitted 58-method report with freshly inventoried declaration and
        # method-body SHA-256 identities. Never infer a new semantic claim.
        prior = json.loads(ADMITTED_WORLD_STATE.read_text(encoding="utf-8"))
        wire = json.loads(
            (staging / JOBS["chunk_wire"][1]).read_text(encoding="utf-8")
        )
        reuse = exact_admitted_world_state_reuse(wire, prior)
        report = {
            "schema": 1,
            "kind": "r2c-26_2-parallel-source-frontier-handoff-v1",
            "target": TARGET, "source_archive_sha256": EXPECTED_SHA,
            "inventories": reports, "completed_in_parallel": True,
            "reused_independently_admitted_inner_wire_methods": reuse,
            "reused_world_state_gate_id": WORLD_STATE_GATE_ID,
            "outer_packet_semantics_reused_or_admitted": False,
            "independent_human_source_review_complete": False,
            "independent_atlas_gate_passed": False,
            "heightmap_per_state_source_semantics_admitted": False,
            "client_biome_ids_admitted": False,
            "chunk_wire_admitted": False,
            "live_world_publication_admitted": False,
        }
        (staging / "review-frontier-manifest.json").write_text(
            json.dumps(report, indent=2, sort_keys=True) + "\n"
        )
        staging.rename(output_dir)
        return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--db", type=Path, required=True)
    parser.add_argument("--lock", type=Path, default=ROOT / "vanilla/vanilla.lock.toml")
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    try:
        result = prepare(args.source, args.db, args.lock, args.output_dir)
    except (ValueError, OSError, TypeError, json.JSONDecodeError,
            subprocess.TimeoutExpired) as error:
        print(f"R2C parallel source review preparation blocked: {error}", file=sys.stderr)
        return 2
    print(f"Two source-free R2C frontier inventories: {args.output_dir}")
    print("Source review, VAR/SEM, independent Atlas gate, production admission: ALL STILL REQUIRED")
    assert result["live_world_publication_admitted"] is False
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
