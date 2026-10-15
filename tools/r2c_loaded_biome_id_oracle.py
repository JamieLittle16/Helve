#!/usr/bin/env python3
"""Independent loaded biome numeric-ID oracle for pinned Minecraft Java 26.2.

A temporary, source-free Java agent reads the *in-memory* loaded Registry<Biome>
by byId/getId/getKey. Simultaneously, a separate socket observer reads the
Configuration registry_data stream from the same official server process.
All IDs must agree without sorting or inferring IDs from datagen paths.

This is runtime evidence only: reviewed source/VAR/SEM/client assignment and
selected-pack parity remain gates before Helve production consumption.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
import tomllib
from pathlib import Path

import official_state_data
import r2c_biome_registry_capture as capture
import r2c_live_biome_registry as live

EXPECTED_ID_COUNT = 66
AGENT_CLASS = "R2cBiomeIdAgent"
AGENT_SOURCE = Path(__file__).resolve().parent / "java/R2cBiomeIdAgent.java"
NAME_SYMBOLS = {
    "SERVER_CLASS": "net.minecraft.server.MinecraftServer",
    "REGISTRIES_CLASS": "net.minecraft.core.registries.Registries",
    "REGISTRY_CLASS": "net.minecraft.core.Registry",
}
PROGUARD_IDENT = re.compile(r"[A-Za-z_$][A-Za-z0-9_$]*\Z", re.ASCII)


class LoadedIdOracleError(ValueError):
    """A source/official runtime identity or numeric-id invariant was not established."""


def symbols(mapping_text: str | None) -> dict[str, str]:
    if mapping_text is None:
        # The official 26.2 launcher does not distribute a separate
        # server_mappings artifact. As in official_state_data.py's sealed
        # state-ID oracle, use readable runtime symbols and require every
        # reflected class/method/field to exist. Do not invent obfuscated IDs.
        return {
            **NAME_SYMBOLS,
            "BIOME_FIELD": "BIOME",
            "SERVER_ACCESS": "registryAccess",
            "BY_ID": "byId",
            "GET_ID": "getId",
            "GET_KEY": "getKey",
        }
    classes, fields, methods = official_state_data.parse_mappings(mapping_text)
    resolved: dict[str, str] = {}
    for token, class_name in NAME_SYMBOLS.items():
        if class_name not in classes:
            raise LoadedIdOracleError(f"official mappings lack {class_name}")
        resolved[token] = classes[class_name]
    field = fields.get(("net.minecraft.core.registries.Registries", "BIOME"))
    if field is None or PROGUARD_IDENT.fullmatch(field) is None:
        raise LoadedIdOracleError("official mapping does not declare Registries.BIOME")
    resolved["BIOME_FIELD"] = field
    for token, owner, name in (
        ("SERVER_ACCESS", "net.minecraft.server.MinecraftServer", "registryAccess"),
        ("BY_ID", "net.minecraft.core.IdMap", "byId"),
        ("GET_ID", "net.minecraft.core.IdMap", "getId"),
        ("GET_KEY", "net.minecraft.core.Registry", "getKey"),
    ):
        try:
            mapping = official_state_data.unique_method(methods, owner, name)
        except ValueError as error:
            raise LoadedIdOracleError(
                f"official mapping lacks unique {owner}#{name}"
            ) from error
        if PROGUARD_IDENT.fullmatch(mapping) is None:
            raise LoadedIdOracleError(f"invalid obfuscated method name for {owner}#{name}")
        resolved[token] = mapping
    return resolved


def build_agent(java_root: Path, mapping_text: str | None) -> Path:
    if java_root.exists() or java_root.is_symlink():
        raise LoadedIdOracleError("Java agent build directory must be fresh")
    java_root.mkdir(parents=True)
    substitutions = symbols(mapping_text)
    source = AGENT_SOURCE.read_text(encoding="utf-8")
    for key, value in substitutions.items():
        placeholder = f"@{key}@"
        if source.count(placeholder) != 1:
            raise LoadedIdOracleError(f"agent template must contain exactly one {placeholder}")
        source = source.replace(placeholder, value)
    if re.search(r"@[A-Z_]+@", source) is not None:
        raise LoadedIdOracleError("agent template contains unresolved mapping placeholders")
    target = java_root / f"{AGENT_CLASS}.java"
    target.write_text(source, encoding="utf-8")
    manifest = java_root / "MANIFEST.MF"
    manifest.write_text(
        "Manifest-Version: 1.0\n"
        f"Premain-Class: {AGENT_CLASS}\n"
        "\n",
        encoding="ascii",
    )
    compile_result = subprocess.run(
        ["javac", "-encoding", "UTF-8", "-d", str(java_root), str(target)],
        capture_output=True, text=True, timeout=60, check=False,
    )
    if compile_result.returncode != 0:
        raise LoadedIdOracleError(
            "official loaded-registry observer failed to compile:\n"
            + compile_result.stderr[-4000:]
        )
    jar = java_root / "r2c-biome-oracle-agent.jar"
    bundle = subprocess.run(
        ["jar", "cfm", str(jar), str(manifest), "-C", str(java_root),
         f"{AGENT_CLASS}.class"],
        capture_output=True, text=True, timeout=30, check=False,
    )
    if bundle.returncode != 0 or not jar.is_file():
        raise LoadedIdOracleError(
            "could not package runtime-loaded registry observer: "
            + bundle.stderr[-2000:]
        )
    return jar


def parse_direct_id_report(raw: bytes) -> tuple[str, ...]:
    """Parse explicit dense (numeric-id, resource-key) pairs; never assign IDs."""
    if not raw or len(raw) > 16_384 or not raw.endswith(b"\n") or b"\r" in raw:
        raise LoadedIdOracleError("invalid or oversized loaded-registry ID report")
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as error:
        raise LoadedIdOracleError("ID report must be UTF-8") from error
    lines = text.splitlines()
    if len(lines) != EXPECTED_ID_COUNT:
        raise LoadedIdOracleError("runtime loaded biome registry cardinality mismatch")
    names: list[str] = []
    for expected_id, line in enumerate(lines):
        fields = line.split("\t")
        if len(fields) != 2 or fields[0] != str(expected_id):
            raise LoadedIdOracleError(
                f"non-dense, missing or noncanonical numeric ID at {expected_id}"
            )
        name = fields[1]
        if capture.IDENTIFIER.fullmatch(name) is None or name in names:
            raise LoadedIdOracleError(f"invalid or duplicate loaded biome ID {expected_id}")
        names.append(name)
    return tuple(names)


def compare_authorities(
    direct_ids: tuple[str, ...],
    network_ids: tuple[str, ...],
    inventory: tuple[str, ...],
    server_sha256: str,
    lock: dict[str, object],
) -> dict[str, object]:
    if not (
        len(direct_ids) == len(network_ids) == len(inventory) == EXPECTED_ID_COUNT
        and len(set(direct_ids)) == EXPECTED_ID_COUNT
        and set(direct_ids) == set(inventory)
        and direct_ids == network_ids
    ):
        raise LoadedIdOracleError(
            "direct loaded-registry byId/getId/key disagree with network ordinals or inventory"
        )
    if server_sha256 != lock.get("runtime", {}).get("server_sha256"):
        raise LoadedIdOracleError("official server identity mismatch")
    digest = hashlib.sha256(("\n".join(direct_ids) + "\n").encode("utf-8")).hexdigest()
    return {
        "schema": 1,
        "target": {"minecraft": "26.2", "protocol": 776, "data_version": 4903},
        "registry": capture.BIOME_REGISTRY,
        "source": "independent-official-loaded-registry-and-live-configuration-v1",
        "server_sha256": server_sha256,
        "source_archive_sha256": lock["source"]["archive_sha256"],
        "known_packs": ["minecraft:core@26.2"],
        "count": len(direct_ids),
        "independent_numeric_id_order_sha256": digest,
        "configuration_network_order_sha256": digest,
        "names_by_verified_runtime_id_candidate": list(direct_ids),
        "numeric_id_authority": "RUNTIME_CROSSCHECK_PASSED_SOURCE_SEM_ADMISSION_PENDING",
        "required_source_gate": "R2C-BIOMES and client registry ID-assignment VAR/SEM",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cache", type=Path, default=Path("/tmp/helve-vanilla-downloads"))
    parser.add_argument("--work-dir", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--lock", type=Path, default=Path("vanilla/vanilla.lock.toml"))
    parser.add_argument("--inventory", type=Path, default=Path(
        "vanilla/fixtures/world/26.2-official-biome-resource-keys.txt"
    ))
    args = parser.parse_args()
    try:
        if args.work_dir.exists() or args.work_dir.is_symlink():
            raise LoadedIdOracleError("work directory must be fresh")
        with args.lock.open("rb") as handle:
            lock = tomllib.load(handle)
        if (lock.get("minecraft"), lock.get("protocol"), lock.get("data_version")) != (
            "26.2", 776, 4903
        ):
            raise LoadedIdOracleError("version lock does not select 26.2/776/4903")
        resolved, _ = official_state_data.resolve("26.2", args.cache)
        server, _ = resolved["server"]
        mapping_entry = resolved.get("server_mappings")
        mappings = mapping_entry[0] if mapping_entry is not None else None
        server_sha = official_state_data.sha256_file(server)
        if server_sha != lock.get("runtime", {}).get("server_sha256"):
            raise LoadedIdOracleError("official-server SHA-256 differs from pinned runtime")
        args.work_dir.mkdir(parents=True)
        jar = build_agent(
            args.work_dir / "agent",
            mappings.read_text(encoding="utf-8") if mappings is not None else None,
        )
        agent_output = args.work_dir / "loaded-registry-by-id.txt"
        network_ids = live.observe_official_server(
            server,
            args.work_dir / "world",
            agent_jar=jar,
            oracle_output=agent_output,
        )
        direct_ids = parse_direct_id_report(agent_output.read_bytes())
        inventory = capture._inventory(args.inventory)
        result = compare_authorities(direct_ids, network_ids, inventory, server_sha, lock)
        if args.output.exists() or args.output.is_symlink():
            raise LoadedIdOracleError("output destination must be fresh")
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(
            json.dumps(result, sort_keys=True, indent=2) + "\n", encoding="utf-8"
        )
    except (LoadedIdOracleError, live.LiveBiomeProbeError, capture.BiomeCaptureError,
            KeyError, OSError, ValueError, subprocess.SubprocessError) as error:
        print(f"independent loaded-biome ID observation failed: {error}", file=sys.stderr)
        return 2
    print(
        f"Loaded 26.2 direct byId/getId/resource-key IDs match independent "
        f"Configuration ordinals ({result['count']} biomes); "
        f"SHA-256 {result['independent_numeric_id_order_sha256']}. "
        "R2C source/SEM admission still pending."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
