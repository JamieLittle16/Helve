#!/usr/bin/env python3
"""Prioritize exact source-review roots from the existing R2C inventory handoff.

Only a nonauthoritative, source-free first-pass queue is produced. This is NOT
exhaustive delegate closure, independently inspected source, VAR/SEM, or
production admission. Reuses the canonical parallel runner's receipt and
previously admitted world-state VAR checks, not another source parser.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

import r2c_parallel_source_frontiers as existing

# Narrow *starting* roots, not a claim that these methods close the proof.
# The actual method signatures and body hashes come from the pinned Atlas.
BIOME = (
    ("net.minecraft.core.MappedRegistry", "register(final ResourceKey < T >"),
    ("net.minecraft.core.MappedRegistry", "byId(final int"),
    ("net.minecraft.core.MappedRegistry", "getId(final @ Nullable"),
    ("net.minecraft.resources.RegistryDataLoader", "load(final Map < ResourceKey"),
    ("net.minecraft.server.network.config.SynchronizeRegistriesTask", "sendRegistries("),
    ("net.minecraft.network.protocol.configuration.ClientboundRegistryDataPacket", "<clinit>()"),
    ("net.minecraft.world.level.chunk.PalettedContainerFactory", "createForBiomes()"),
    ("net.minecraft.resources.NetworkRegistryLoadTask", "load(final RegistryOps"),
    ("net.minecraft.resources.RegistryLoadTask", "registerElements("),
    ("net.minecraft.util.Util", "sequence(final List <"),
)
WIRE = (
    ("net.minecraft.network.protocol.game.ClientboundLevelChunkWithLightPacket", "<clinit>()"),
    ("net.minecraft.network.protocol.game.ClientboundLevelChunkWithLightPacket", "ClientboundLevelChunkWithLightPacket(final LevelChunk"),
    ("net.minecraft.network.protocol.game.ClientboundLevelChunkWithLightPacket", "write(final RegistryFriendlyByteBuf"),
    ("net.minecraft.network.protocol.game.ClientboundLevelChunkPacketData", "ClientboundLevelChunkPacketData(final RegistryFriendlyByteBuf"),
    ("net.minecraft.network.protocol.game.ClientboundLevelChunkPacketData", "getBlockEntitiesTags(final "),
    ("net.minecraft.network.protocol.game.ClientboundLightUpdatePacketData", "ClientboundLightUpdatePacketData(final FriendlyByteBuf"),
    ("net.minecraft.server.network.PlayerChunkSender", "sendNextChunks("),
    ("net.minecraft.server.network.PlayerChunkSender", "sendChunk("),
    ("net.minecraft.server.network.PlayerChunkSender", "onChunkBatchReceivedByClient("),
)
NONADMITTED_FLAGS = (
    "chunk_wire_admitted", "client_biome_ids_admitted",
    "heightmap_per_state_source_semantics_admitted", "independent_atlas_gate_passed",
    "independent_human_source_review_complete", "live_world_publication_admitted",
    "outer_packet_semantics_reused_or_admitted",
)


class FocusError(ValueError):
    """Inputs cannot yield the expected narrowly bounded first-pass review."""


def _focus(index: dict, targets: tuple[tuple[str, str], ...], reused: set[str]) -> list[dict]:
    output: list[dict] = []
    for owner, prefix in targets:
        rows = index.get(owner)
        if not isinstance(rows, list):
            raise FocusError("missing planned exact Atlas owner: " + owner)
        matches = [row for row in rows if isinstance(row, dict)
                   and isinstance(row.get("signature"), str)
                   and row["signature"].startswith(prefix)]
        if len(matches) != 1:
            raise FocusError("missing or ambiguous Atlas declaration: " + owner + "#" + prefix)
        row = matches[0]
        identity = owner + "#" + row["signature"]
        if identity in reused:
            raise FocusError("already source-admitted inner-wire method selected again")
        if (row.get("declaration_only") is not False
                or not all(isinstance(row.get(key), str) and len(row[key]) == 64
                           for key in ("body_sha256", "normalized_sha256"))
                or not isinstance(row.get("hazard_leads"), list)):
            raise FocusError("incomplete Atlas method body fingerprint: " + identity)
        output.append({
            "source": identity,
            "normalized_sha256": row["normalized_sha256"],
            "body_sha256": row["body_sha256"],
            "hazard_leads": row["hazard_leads"],
            "source_inspected": False,
            "semantics_admitted": False,
        })
    if len(set(row["source"] for row in output)) != len(output):
        raise FocusError("repeated first-pass method")
    return output


def build(manifest: dict, biome: dict, wire: dict, admitted: dict) -> dict:
    if (manifest.get("schema") != 1
            or manifest.get("kind") != "r2c-26_2-parallel-source-frontier-handoff-v1"
            or manifest.get("target") != existing.TARGET
            or manifest.get("source_archive_sha256") != existing.EXPECTED_SHA
            or any(manifest.get(flag) is not False for flag in NONADMITTED_FLAGS)):
        raise FocusError("pinned source handoff identity or nonadmission flags drifted")
    if (biome.get("kind") != "r2c-biome-id-source-declaration-inventory-v1"
            or wire.get("kind") != "r2c-chunk-wire-source-declarations-unadmitted-v1"):
        raise FocusError("inventories differ from the exact R2C source frontiers")
    for label, item in (("biome_client_ids", biome), ("chunk_wire", wire)):
        if (item.get("target") != existing.TARGET
                or item.get("source_archive_sha256") != existing.EXPECTED_SHA
                or item.get("source_inspected") is not False
                or item.get("production_admitted") is not False):
            raise FocusError("inventory source/admission identity drift: " + label)
    reused = existing.exact_admitted_world_state_reuse(wire, admitted)
    if manifest.get("reused_independently_admitted_inner_wire_methods") != reused:
        raise FocusError("source-admitted seven-method reuse differs from independent gate")
    if manifest.get("reused_world_state_gate_id") != existing.WORLD_STATE_GATE_ID:
        raise FocusError("wrong prior world-state source gate")
    roots: dict[str, list] = {}
    for group in biome["groups"]:
        for owner in group["roots"]:
            if owner["type"] in roots:
                raise FocusError("duplicate biome Atlas owner")
            roots[owner["type"]] = owner["methods"]
    targeted = biome.get("targeted_methods")
    if (not isinstance(targeted, list) or len(targeted) != 1
            or targeted[0].get("type") != "net.minecraft.util.Util"
            or targeted[0].get("method") != "sequence"):
        raise FocusError("missing exact ordered-futures delegate")
    roots["net.minecraft.util.Util"] = targeted[0]["overloads"]
    wire_roots: dict[str, list] = {}
    for group in wire["groups"]:
        if group["type"] in wire_roots:
            raise FocusError("duplicate chunk-wire Atlas owner")
        wire_roots[group["type"]] = group["declarations"]
    reused_names = {row["source"] for row in reused}
    return {
        "schema": 1,
        "kind": "r2c-26_2-first-pass-source-review-focus-v1",
        "target": existing.TARGET,
        "source_archive_sha256": existing.EXPECTED_SHA,
        "first_pass_only": True,
        "delegate_closure_proven": False,
        "client_biome_ids_admitted": False,
        "heightmap_predicates_admitted": False,
        "outer_wire_admitted": False,
        "production_admitted": False,
        "already_admitted_inner_wire_methods": len(reused),
        "biome_priority": _focus(roots, BIOME, reused_names),
        "outer_wire_priority": _focus(wire_roots, WIRE, reused_names),
    }


def run(manifest_path: Path, biome_path: Path, wire_path: Path, output: Path) -> dict:
    if (output.exists() or output.is_symlink()
            or output.resolve(strict=False).is_relative_to(existing.ROOT.resolve())):
        raise FocusError("review handoff output must be a fresh path outside the repository")
    inputs = {
        "manifest": manifest_path.read_bytes(),
        "biome_client_ids": biome_path.read_bytes(),
        "chunk_wire": wire_path.read_bytes(),
    }
    docs = {name: json.loads(raw) for name, raw in inputs.items()}
    for label in ("biome_client_ids", "chunk_wire"):
        actual = existing.check_one(label, biome_path if label == "biome_client_ids" else wire_path)
        if docs["manifest"].get("inventories", {}).get(label) != actual:
            raise FocusError("inventory SHA-256 receipt or contents mismatch: " + label)
    prior = json.loads(existing.ADMITTED_WORLD_STATE.read_text(encoding="utf-8"))
    report = build(docs["manifest"], docs["biome_client_ids"], docs["chunk_wire"], prior)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("x", encoding="utf-8") as stream:
        json.dump(report, stream, indent=2, sort_keys=True)
        stream.write("\n")
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--biome", type=Path, required=True)
    parser.add_argument("--wire", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    try:
        result = run(args.manifest, args.biome, args.wire, args.output)
    except (OSError, KeyError, TypeError, ValueError, json.JSONDecodeError) as error:
        print(f"R2C first-pass source review rejected: {error}", file=sys.stderr)
        return 2
    print(f"Focused {len(result['biome_priority'])} biome + "
          f"{len(result['outer_wire_priority'])} new outer-wire methods; "
          "seven admitted inner-wire VAR methods reused; NO new admission")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
