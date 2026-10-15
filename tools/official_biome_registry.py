#!/usr/bin/env python3
"""Produce a source-pinned 26.2 dynamic-biome *resource inventory* from Mojang datagen.

The official reports/registries.json is a STATIC-registry report and deliberately
does not contain minecraft:worldgen/biome. Instead this cold probe extracts all
built-in biome JSON resource keys from the pinned official server's datagen output.

The returned candidate sequence is NOT an admitted protocol-id map. Dynamic
registry integer assignments require an independent exact 26.2 RegistryDataLoader
source proof and/or runtime registry-ID oracle before promotion.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
import tomllib
from pathlib import Path

import official_state_data

REGISTRY = "minecraft:worldgen/biome"
TARGET_VERSION = "26.2"
MAX_REGISTRY = 65_536


class RegistryExtractionError(ValueError):
    """Pinned official server report or registry data violated our source contract."""


def canonical_keys(data: object) -> tuple[str, ...]:
    """Normalize explicit report protocol IDs only; never infer order from key iteration."""
    if not isinstance(data, dict):
        raise RegistryExtractionError("reports/registries.json root is not an object")
    raw = data.get(REGISTRY)
    if not isinstance(raw, dict):
        available = sorted(data)
        raise RegistryExtractionError(
            f"official reports do not contain {REGISTRY}; "
            f"available registry keys ({len(available)}): {available[:160]}"
        )
    entries = raw.get("entries")
    if not isinstance(entries, dict) or not entries:
        raise RegistryExtractionError("official biome report has no entries")
    if len(entries) > MAX_REGISTRY:
        raise RegistryExtractionError("official biome registry exceeds compact ID capacity")
    ordered: list[str | None] = [None] * len(entries)
    for key, properties in entries.items():
        if (
            not isinstance(key, str)
            or not key.startswith("minecraft:")
            or not isinstance(properties, dict)
        ):
            raise RegistryExtractionError("invalid official biome name or report descriptor")
        protocol_id = properties.get("protocol_id")
        if isinstance(protocol_id, bool) or not isinstance(protocol_id, int):
            raise RegistryExtractionError(f"biome {key}: missing integer protocol_id")
        if not 0 <= protocol_id < len(ordered):
            raise RegistryExtractionError(
                f"biome {key}: non-dense or invalid protocol ID {protocol_id}"
            )
        if ordered[protocol_id] is not None:
            raise RegistryExtractionError(
                f"duplicate protocol ID {protocol_id}: {ordered[protocol_id]} and {key}"
            )
        ordered[protocol_id] = key
    if any(value is None for value in ordered):
        raise RegistryExtractionError("official biome protocol IDs contain a gap")
    return tuple(key for key in ordered if key is not None)


def payload(
    version: str, server_sha256: str, report_data: dict[str, object]
) -> dict[str, object]:
    if version != TARGET_VERSION:
        raise RegistryExtractionError("only the locked 26.2 protocol is admitted")
    keys = canonical_keys(report_data)
    canonical = "\n".join(keys) + "\n"
    return {
        "schema": 1,
        "target": {
            "minecraft_version": TARGET_VERSION,
            "protocol_version": 776,
            "data_version": 4903,
        },
        "registry": REGISTRY,
        "source": "pinned-official-server-datagen-registry-report-v1",
        "server_sha256": server_sha256,
        "registry_count": len(keys),
        "source_order_sha256": hashlib.sha256(canonical.encode("utf-8")).hexdigest(),
        "names_by_protocol_id": keys,
    }


def source_biome_inventory(data_root: Path) -> tuple[str, ...]:
    """Inventory built-in worldgen biome JSON keys without assigning protocol IDs."""
    root = data_root / "data" / "minecraft" / "worldgen" / "biome"
    if not root.is_dir():
        candidates = sorted(
            p.relative_to(data_root).as_posix()
            for p in data_root.rglob("*")
            if p.is_file() and "biome" in p.parts
        )
        raise RegistryExtractionError(
            f"official datagen produced no data/minecraft/worldgen/biome directory; "
            f"related files: {candidates[:40]}"
        )
    names: list[str] = []
    paths = sorted(root.rglob("*.json"))
    if not paths or len(paths) > MAX_REGISTRY:
        raise RegistryExtractionError(
            f"unexpected official biome resource count: {len(paths)}"
        )
    for path in paths:
        relative = path.relative_to(root)
        if not path.is_file():
            raise RegistryExtractionError("invalid generated biome file")
        source_name = relative.with_suffix("").as_posix()
        if not source_name or any(
            part in ("", ".", "..") for part in relative.parts
        ):
            raise RegistryExtractionError("invalid generated biome resource path")
        name = "minecraft:" + source_name
        if name in names:
            raise RegistryExtractionError(f"duplicate generated biome key: {name}")
        try:
            contents = json.loads(path.read_text(encoding="utf-8"))
        except (UnicodeError, json.JSONDecodeError) as error:
            raise RegistryExtractionError(
                f"official biome data is invalid JSON: {relative}"
            ) from error
        if not isinstance(contents, dict) or not contents:
            raise RegistryExtractionError(f"empty biome definition: {relative}")
        names.append(name)
    return tuple(names)


def candidate_payload(
    version: str, server_hash: str, biome_names: tuple[str, ...],
) -> dict[str, object]:
    """Record content identity but never claim sorted names are network ordinals."""
    if version != TARGET_VERSION or not biome_names:
        raise RegistryExtractionError("unsupported target or missing biome resource inventory")
    if len(biome_names) > MAX_REGISTRY or len(set(biome_names)) != len(biome_names):
        raise RegistryExtractionError("invalid source biome cardinality/uniqueness")
    source_text = "\n".join(biome_names) + "\n"
    return {
        "schema": 1,
        "target": {
            "minecraft_version": TARGET_VERSION,
            "protocol_version": 776,
            "data_version": 4903,
        },
        "registry": REGISTRY,
        "source": "digest-pinned-official-server-datagen-worldgen-biome-v1",
        "server_sha256": server_hash,
        "biome_resource_count": len(biome_names),
        "biome_resource_keys_sha256": hashlib.sha256(
            source_text.encode("utf-8")
        ).hexdigest(),
        "biome_resource_keys": biome_names,
        "protocol_id_authority": "NOT_QUALIFIED",
        "order_kind": "generated-resource-path-order-not-network-id-order",
    }


def extract(
    version: str,
    output: Path,
    cache: Path,
    work_dir: Path,
    lock_path: Path,
) -> dict[str, object]:
    with lock_path.open("rb") as f:
        lock = tomllib.load(f)
    if lock.get("minecraft") != version or lock.get("protocol") != 776:
        raise RegistryExtractionError("target version/protocol differs from source lock")
    pinned_sha = lock.get("runtime", {}).get("server_sha256")
    if not isinstance(pinned_sha, str) or len(pinned_sha) != 64:
        raise RegistryExtractionError("missing pinned official server digest")

    resolved, _ = official_state_data.resolve(version, cache)
    server, _metadata = resolved["server"]
    server_hash = official_state_data.sha256_file(server)
    if server_hash != pinned_sha:
        raise RegistryExtractionError(
            f"official launcher server differs from lock: got {server_hash}"
        )
    if work_dir.exists() and any(work_dir.iterdir()):
        raise RegistryExtractionError("report work directory must be initially empty")
    work_dir.mkdir(parents=True, exist_ok=True)
    data_root = work_dir / "out"
    log_path = work_dir / "generator.log"

    # The official server datagen provides dynamic biome *resources*, not their IDs.
    # Fail closed if the intended generated resource files are missing.
    command = [
        "java",
        "-DbundlerMainClass=net.minecraft.data.Main",
        "-jar",
        str(server.resolve()),
        "--all",
        "--output",
        str(data_root.resolve()),
    ]
    try:
        completed = subprocess.run(
            command, cwd=work_dir, capture_output=True, text=True, timeout=360,
            check=False,
        )
    except subprocess.TimeoutExpired as error:
        raise RegistryExtractionError("official datagen exceeded 360-second bound") from error
    log_path.write_text(completed.stdout + "\n" + completed.stderr, encoding="utf-8")
    if completed.returncode != 0:
        raise RegistryExtractionError(
            f"official --all exited {completed.returncode}; log at {log_path}"
        )
    keys = source_biome_inventory(data_root)
    result = candidate_payload(version, server_hash, keys)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--version", default=TARGET_VERSION)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--cache", type=Path, default=Path("/tmp/helve-vanilla-downloads"))
    parser.add_argument("--work-dir", type=Path, required=True)
    parser.add_argument("--lock", type=Path, default=Path("vanilla/vanilla.lock.toml"))
    parser.add_argument("--print-ids", action="store_true")
    args = parser.parse_args()
    try:
        result = extract(
            args.version, args.output, args.cache, args.work_dir, args.lock
        )
    except (
        RegistryExtractionError, OSError, KeyError, ValueError,
        subprocess.CalledProcessError,
    ) as error:
        print(f"official biome registry extraction error: {error}", file=sys.stderr)
        return 2
    print(
        f"official {TARGET_VERSION} {REGISTRY}: "
        f"{result['biome_resource_count']} generated resource keys, "
        f"resource SHA256={result['biome_resource_keys_sha256']}; "
        "numeric protocol IDs NOT qualified"
    )
    if args.print_ids:
        for key in result["biome_resource_keys"]:
            print(f"BIOME_RESOURCE_KEY|{key}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
