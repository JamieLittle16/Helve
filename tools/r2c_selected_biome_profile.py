#!/usr/bin/env python3
"""COLD R1X Configuration vs independently observed 26.2 runtime biome IDs.

Check the *actual selected immutable Configuration bodies* against the frozen
source-free, direct byId/getId + live-wire 66-ordinal candidate. No sorting,
no generation of IDs, no source/VAR/SEM admission. This is a pack-time guard.
"""
from __future__ import annotations

import hashlib
import json
import tomllib
from pathlib import Path
from typing import Sequence

try:
    from . import r2c_biome_registry_capture as capture
except ImportError:
    import r2c_biome_registry_capture as capture

ROOT = Path(__file__).resolve().parents[1]
FROZEN = ROOT / "vanilla/fixtures/world/26.2-runtime-crosschecked-biome-ordinal-candidate.json"
LOCK = ROOT / "vanilla/vanilla.lock.toml"
SELECTED_NETWORK_SHA256 = "97cba53b1bfd18870a345a42cea14e665e0a59f559dba939bec95cdf6fa5373d"
EXPECTED_SOURCE_SHA256 = "1e9bca3dff83cd83e7905f8810f1ec9899361fa2dc83fe893bb48beeb04df750"
EXPECTED_REGISTRY_COUNT = 29
EXPECTED_CLIENTBOUND_COUNT = 34
EXPECTED_REGISTRY = "minecraft:worldgen/biome"
EXPECTED_AUTHORITY = "RUNTIME_CROSSCHECK_PASSED_SOURCE_SEM_ADMISSION_PENDING"
EXPECTED_SOURCE = "independent-official-loaded-registry-and-live-configuration-v1"
EXPECTED_GATE = "R2C-BIOMES and client registry ID-assignment VAR/SEM"


class ProfileMismatch(ValueError):
    """Selected outbound Configuration does not match official runtime candidate."""


def _frozen_profile(*, fixture: Path = FROZEN, lockfile: Path = LOCK) -> tuple[str, ...]:
    if fixture.is_symlink() or not fixture.is_file():
        raise ProfileMismatch("runtime-verified candidate fixture must be a regular file")
    if lockfile.is_symlink() or not lockfile.is_file():
        raise ProfileMismatch("version lock must be a regular file")
    try:
        observed = json.loads(fixture.read_text(encoding="utf-8"))
        with lockfile.open("rb") as handle:
            lock = tomllib.load(handle)
    except (OSError, ValueError) as error:
        raise ProfileMismatch(f"cannot read pinned biome profile: {error}") from error
    if not isinstance(observed, dict):
        raise ProfileMismatch("runtime candidate is not an object")
    if (lock.get("minecraft"), lock.get("protocol"), lock.get("data_version")) != (
        "26.2", 776, 4903
    ) or lock.get("source", {}).get("archive_sha256") != EXPECTED_SOURCE_SHA256:
        raise ProfileMismatch("unsupported version/source lock")
    if (
        observed.get("schema") != 1
        or observed.get("target") != {"minecraft": "26.2", "protocol": 776, "data_version": 4903}
        or observed.get("source") != EXPECTED_SOURCE
        or observed.get("source_archive_sha256") != EXPECTED_SOURCE_SHA256
        or observed.get("server_sha256") != lock.get("runtime", {}).get("server_sha256")
        or observed.get("registry") != EXPECTED_REGISTRY
        or observed.get("known_packs") != ["minecraft:core@26.2"]
        or observed.get("count") != 66
        or observed.get("numeric_id_authority") != EXPECTED_AUTHORITY
        or observed.get("required_source_gate") != EXPECTED_GATE
        or observed.get("independent_numeric_id_order_sha256") != SELECTED_NETWORK_SHA256
        or observed.get("configuration_network_order_sha256") != SELECTED_NETWORK_SHA256
    ):
        raise ProfileMismatch("frozen runtime biome source/known-pack contract drift")
    names = observed.get("names_by_verified_runtime_id_candidate")
    if (not isinstance(names, list) or len(names) != 66
            or not all(isinstance(name, str) and capture.IDENTIFIER.fullmatch(name)
                       for name in names)
            or len(set(names)) != 66):
        raise ProfileMismatch("runtime biome candidate has invalid dense ID order")
    digest = hashlib.sha256(("\n".join(names) + "\n").encode("utf-8")).hexdigest()
    if digest != SELECTED_NETWORK_SHA256:
        raise ProfileMismatch("frozen runtime biome ID order SHA-256 changed")
    return tuple(names)


def verify_selected_biome_profile(
    configuration_bodies: Sequence[bytes],
    *,
    fixture: Path = FROZEN,
    lockfile: Path = LOCK,
) -> None:
    """Fail-closed pack preflight; comparison is *ordinal exact*, never sorted.

    The selected R1X packer independently verifies the entire captured image,
    immutable body hashes and source/capture commitments before this call.
    This binds that actual 34-body image to a prior direct official-runtime
    byId/getId/network agreement under the selected core known-pack candidate,
    NOT to complete stock-client receiving registry semantics.
    """
    if len(configuration_bodies) != EXPECTED_CLIENTBOUND_COUNT:
        raise ProfileMismatch("expected 34 exact selected Configuration bodies")
    try:
        ids = [capture._varint(body, 0)[0] for body in configuration_bodies]
        if (ids[:3] != [1, 12, 14]
                or ids[3:32] != [capture.REGISTRY_PACKET_ID] * EXPECTED_REGISTRY_COUNT
                or ids[32:] != [13, 3]):
            raise ProfileMismatch("selected Configuration packet order differs from 26.2 profile")
        registries = [capture.registry_packet_name(body)[0]
                      for body in configuration_bodies[3:32]]
        if len(set(registries)) != EXPECTED_REGISTRY_COUNT:
            raise ProfileMismatch("duplicate Configuration registry-data publication")
        selected = [body for body, name in zip(configuration_bodies[3:32],
                                               registries, strict=True)
                    if name == EXPECTED_REGISTRY]
        if len(selected) != 1:
            raise ProfileMismatch("expected exactly one selected biome registry packet")
        network_names = capture.decode_biome_packet(selected[0])
    except capture.BiomeCaptureError as error:
        raise ProfileMismatch(f"invalid selected registry wire body: {error}") from error
    expected_names = _frozen_profile(fixture=fixture, lockfile=lockfile)
    if len(network_names) != len(expected_names):
        raise ProfileMismatch("selected biome count and frozen runtime ID universe disagree")
    for ordinal, (actual, expected) in enumerate(zip(network_names, expected_names, strict=True)):
        if actual != expected:
            raise ProfileMismatch(f"selected biome ordinal {ordinal} differs from direct runtime ID")
