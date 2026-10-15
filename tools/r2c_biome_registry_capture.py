#!/usr/bin/env python3
"""Extract a *candidate* 26.2 biome ID order from the pinned R1B Configuration witness.

Unlike official datagen's resource inventory, this observes the ordered entries
of the actual Configuration registry-data packet. The result is NOT admitted
as production registry IDs until the independent loaded-registry/source-order
cross-check in #285 is complete. No captured packet is shipped to Helve.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import tomllib
from pathlib import Path
from typing import Any, Sequence

import r1b_join_capture_image as witness

BIOME_REGISTRY = "minecraft:worldgen/biome"
REGISTRY_PACKET_ID = 7
MAX_ENTRIES = 65_536
MAX_IDENTIFIER_BYTES = 32_767
IDENTIFIER = re.compile(r"[a-z0-9_.-]+:[a-z0-9_./-]+\Z", flags=re.ASCII)
EXPECTED_REGISTRY_PACKETS = 29


class BiomeCaptureError(ValueError):
    """Malformed, incompatible, or unverified selected-profile witness."""


def _varint(data: bytes, offset: int) -> tuple[int, int]:
    """Decode a canonical nonnegative 32-bit Minecraft VarInt."""
    start = offset
    value = 0
    for index in range(5):
        if offset >= len(data):
            raise BiomeCaptureError("truncated VarInt")
        byte = data[offset]
        offset += 1
        if index == 4 and byte > 15:
            raise BiomeCaptureError("VarInt exceeds unsigned 32-bit range")
        value |= (byte & 0x7F) << (index * 7)
        if not byte & 0x80:
            encoded = []
            rest = value
            while rest >= 128:
                encoded.append((rest & 127) | 128)
                rest >>= 7
            encoded.append(rest)
            if data[start:offset] != bytes(encoded):
                raise BiomeCaptureError("noncanonical VarInt")
            return value, offset
    raise BiomeCaptureError("VarInt exceeds five bytes")


def _identifier(data: bytes, offset: int) -> tuple[str, int]:
    size, offset = _varint(data, offset)
    if size == 0 or size > MAX_IDENTIFIER_BYTES or size > len(data) - offset:
        raise BiomeCaptureError("invalid identifier byte length")
    raw = data[offset:offset + size]
    try:
        name = raw.decode("utf-8")
    except UnicodeDecodeError as error:
        raise BiomeCaptureError("identifier is not UTF-8") from error
    if IDENTIFIER.fullmatch(name) is None:
        raise BiomeCaptureError(f"noncanonical resource identifier: {name!r}")
    return name, offset + size


def registry_packet_name(body: bytes) -> tuple[str, int]:
    """Read only the admitted packet ID and registry identifier envelope."""
    packet_id, offset = _varint(body, 0)
    if packet_id != REGISTRY_PACKET_ID:
        raise BiomeCaptureError(f"expected registry-data packet ID 7, got {packet_id}")
    return _identifier(body, offset)


def decode_biome_packet(body: bytes) -> tuple[str, ...]:
    """Decode every ordered entry of a known-pack-backed biome packet.

    Inline NBT is deliberately unsupported by this narrowly selected 26.2
    profile. Rather than skipping unknown structured bytes, fail closed.
    """
    registry, offset = registry_packet_name(body)
    if registry != BIOME_REGISTRY:
        raise BiomeCaptureError(f"not the biome registry: {registry}")
    count, offset = _varint(body, offset)
    if not 0 < count <= MAX_ENTRIES:
        raise BiomeCaptureError("invalid biome registry count")
    result: list[str] = []
    seen: set[str] = set()
    for index in range(count):
        name, offset = _identifier(body, offset)
        if name in seen:
            raise BiomeCaptureError(f"duplicate biome at ordinal {index}: {name}")
        seen.add(name)
        if offset >= len(body):
            raise BiomeCaptureError("missing optional-entry-data flag")
        has_data = body[offset]
        offset += 1
        if has_data != 0:
            raise BiomeCaptureError(
                f"biome {name}: expected absent NBT under selected known-pack profile"
            )
        result.append(name)
    if offset != len(body):
        raise BiomeCaptureError("trailing bytes in biome registry-data packet")
    return tuple(result)


def _verified_bodies(image: dict[str, Any]) -> list[bytes]:
    target = image.get("target")
    if not isinstance(target, dict) or target != {
        "minecraft": "26.2",
        "protocol": 776,
        "source_archive_sha256": witness.EXPECTED_SOURCE_SHA256,
        "capture_sha256": witness.EXPECTED_CAPTURE_SHA256,
    }:
        raise BiomeCaptureError("image target/capture/source identity differs from pinned witness")
    if image.get("schema") != 1 or image.get("kind") != witness.KIND:
        raise BiomeCaptureError("not the selected R1B capture-image format")
    config = image.get("configuration")
    if not isinstance(config, dict):
        raise BiomeCaptureError("missing Configuration image")
    raw_bodies = config.get("server_bodies")
    if not isinstance(raw_bodies, list) or len(raw_bodies) != 34:
        raise BiomeCaptureError("expected exactly 34 Configuration clientbound bodies")
    bodies: list[bytes] = []
    for index, record in enumerate(raw_bodies):
        if not isinstance(record, dict) or record.get("ordinal") != index + 1:
            raise BiomeCaptureError(f"invalid Configuration body ordinal {index}")
        raw = record.get("body_hex")
        if not isinstance(raw, str):
            raise BiomeCaptureError(f"missing body hex at {index}")
        try:
            data = bytes.fromhex(raw)
        except ValueError as error:
            raise BiomeCaptureError(f"invalid packet hex at {index}") from error
        if len(data) != record.get("body_bytes"):
            raise BiomeCaptureError(f"body size mismatch at {index}")
        if hashlib.sha256(data).hexdigest() != record.get("body_sha256"):
            raise BiomeCaptureError(f"body hash mismatch at {index}")
        bodies.append(data)
    combined = b"".join(bodies)
    if (len(combined) != witness.EXPECTED_CONFIG_BODY_BYTES
        or hashlib.sha256(combined).hexdigest() != witness.EXPECTED_CONFIG_BODY_SHA256
        or config.get("body_bytes") != len(combined)
        or config.get("body_concat_sha256") != witness.EXPECTED_CONFIG_BODY_SHA256):
        raise BiomeCaptureError("Configuration bytes differ from pinned independent witness")
    ids = [_varint(body, 0)[0] for body in bodies]
    if (ids[:3] != [1, 12, 14]
        or ids[3:32] != [REGISTRY_PACKET_ID] * EXPECTED_REGISTRY_PACKETS
        or ids[32:] != [13, 3]):
        raise BiomeCaptureError("Configuration packet sequence differs from admitted profile")
    return bodies[3:32]


def _inventory(path: Path) -> tuple[str, ...]:
    if path.is_symlink() or not path.is_file():
        raise BiomeCaptureError("inventory must be a regular non-symlink file")
    raw = path.read_bytes()
    if not raw.endswith(b"\n") or b"\r" in raw:
        raise BiomeCaptureError("inventory must have LF-terminated records")
    try:
        names = tuple(raw.decode("utf-8").splitlines())
    except UnicodeDecodeError as error:
        raise BiomeCaptureError("inventory is not UTF-8") from error
    if (len(names) != 66 or len(set(names)) != 66
        or any(IDENTIFIER.fullmatch(name) is None for name in names)):
        raise BiomeCaptureError("expected 66 unique canonical official biome resource keys")
    if hashlib.sha256(raw).hexdigest() != (
        "97cba53b1bfd18870a345a42cea14e665e0a59f559dba939bec95cdf6fa5373d"
    ):
        raise BiomeCaptureError("official biome inventory digest differs from frozen source")
    return names


def extract(image: dict[str, Any], inventory: tuple[str, ...], lock: dict[str, Any]) -> dict[str, Any]:
    """Return a source-free CANDIDATE only, never a production-registry ID map."""
    if (lock.get("minecraft") != "26.2" or lock.get("protocol") != 776
        or lock.get("data_version") != 4903
        or lock.get("source", {}).get("archive_sha256") != witness.EXPECTED_SOURCE_SHA256):
        raise BiomeCaptureError("official version/source lock differs from capture")
    server_sha = lock.get("runtime", {}).get("server_sha256")
    if (not isinstance(server_sha, str) or
        re.fullmatch(r"[0-9a-f]{64}", server_sha) is None):
        raise BiomeCaptureError("missing locked official-server SHA-256")
    registry_packets = _verified_bodies(image)
    ordered_registries: set[str] = set()
    biome_entries: tuple[str, ...] | None = None
    for body in registry_packets:
        registry, _ = registry_packet_name(body)
        if registry in ordered_registries:
            raise BiomeCaptureError(f"duplicate Configuration registry: {registry}")
        ordered_registries.add(registry)
        if registry == BIOME_REGISTRY:
            biome_entries = decode_biome_packet(body)
    if biome_entries is None:
        raise BiomeCaptureError("pinned Configuration did not publish a biome registry")
    if len(biome_entries) != len(inventory) or set(biome_entries) != set(inventory):
        raise BiomeCaptureError("biome entries do not equal the complete pinned official inventory")
    ordered = "\n".join(biome_entries) + "\n"
    return {
        "schema": 1,
        "target": {"minecraft": "26.2", "protocol": 776, "data_version": 4903},
        "registry": BIOME_REGISTRY,
        "source": "pinned-r1b-configuration-registry-data-witness-v1",
        "source_archive_sha256": witness.EXPECTED_SOURCE_SHA256,
        "official_server_sha256_from_lock": server_sha,
        "capture_sha256": witness.EXPECTED_CAPTURE_SHA256,
        "network_entry_count": len(biome_entries),
        "candidate_order_sha256": hashlib.sha256(ordered.encode("utf-8")).hexdigest(),
        "candidate_names_by_network_ordinal": list(biome_entries),
        "numeric_id_authority": "UNQUALIFIED_CAPTURE_CANDIDATE",
        "required_independent_check": "loaded 26.2 server registry ordinals and source-backed client assignment",
    }


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("capture_image", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--inventory", type=Path, default=Path(
        "vanilla/fixtures/world/26.2-official-biome-resource-keys.txt"
    ))
    parser.add_argument("--lock", type=Path, default=Path("vanilla/vanilla.lock.toml"))
    args = parser.parse_args(argv)
    try:
        if args.capture_image.is_symlink() or not args.capture_image.is_file():
            raise BiomeCaptureError("capture image must be a regular non-symlink file")
        image = json.loads(args.capture_image.read_text(encoding="utf-8"))
        if not isinstance(image, dict):
            raise BiomeCaptureError("capture image must contain an object")
        with args.lock.open("rb") as source:
            lock = tomllib.load(source)
        result = extract(image, _inventory(args.inventory), lock)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    except (BiomeCaptureError, OSError, ValueError, KeyError, TypeError) as error:
        print(f"R2C candidate registry extraction failed: {error}", file=sys.stderr)
        return 2
    print(
        f"captured {result['network_entry_count']} source-inventory-checked biome keys; "
        "numeric ID authority remains UNQUALIFIED pending independent check"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
