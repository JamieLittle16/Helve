#!/usr/bin/env python3
"""Discover the exact unobfuscated *client-side* 26.2 registry receiver frontier.

Java 26.2 is shipped unobfuscated and has no client_mappings download. Fetch
only the official client JAR from the Mojang launcher manifest, check official
SHA-1/size, and emit SHA-256 class/artifact fingerprints plus bounded method
names from javap. No JAR, bytecode listing or original source is emitted.
This is discovery, NOT reviewed client invocation or numeric-ID admission.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
import tempfile
import tomllib
import zipfile
from pathlib import Path

import official_state_data as official

VERSION = "26.2"
PROTOCOL = 776
DATA_VERSION = 4903
SOURCE_SHA256 = "1e9bca3dff83cd83e7905f8810f1ec9899361fa2dc83fe893bb48beeb04df750"
REPO = Path(__file__).resolve().parents[1]
LOCK = REPO / "vanilla/vanilla.lock.toml"
KIND = "r2c-official-unobfuscated-client-receiver-artifact-discovery-v1"
MAX_CANDIDATES = 16
MAX_METHODS_PER_CANDIDATE = 64
MAX_CLASS_BYTES = 1_048_576


def required_client(meta: dict) -> dict:
    """Require exact Mojang client identity; mapping absence is version law."""
    downloads = meta.get("downloads")
    if not isinstance(downloads, dict) or "client_mappings" in downloads:
        raise ValueError("official 26.2 downloads must be unobfuscated and unmapped")
    asset = downloads.get("client")
    if not isinstance(asset, dict):
        raise ValueError("official 26.2 metadata has no client")
    if (not {"url", "sha1", "size"}.issubset(asset)
        or not isinstance(asset["url"], str)
        or not asset["url"].startswith("https://")
        or not isinstance(asset["sha1"], str)
        or re.fullmatch(r"[0-9a-f]{40}", asset["sha1"]) is None
        or type(asset["size"]) is not int
        or not 0 < asset["size"] < 512 * 1024 * 1024):
        raise ValueError("invalid official client metadata identity")
    return asset


def receiver_candidates(client: Path) -> list[dict]:
    """Read only bounded class identities and method names; no class execution."""
    with zipfile.ZipFile(client) as archive:
        names = sorted(name for name in archive.namelist()
                       if name.startswith("net/minecraft/client/")
                       and "Configuration" in name
                       and "Listener" in name
                       and name.endswith(".class")
                       and "$" not in name)
        if not 1 <= len(names) <= MAX_CANDIDATES:
            raise ValueError("no bounded unobfuscated client Configuration listener frontier")
        candidates: list[dict] = []
        for name in names:
            bytecode = archive.read(name)
            if not 4 <= len(bytecode) <= MAX_CLASS_BYTES or bytecode[:4] != b"\xca\xfe\xba\xbe":
                raise ValueError(f"invalid or oversized official client class {name}")
            class_name = name[:-6].replace("/", ".")
            result = subprocess.run(
                ["javap", "-p", "-classpath", str(client), class_name],
                capture_output=True, text=True, timeout=30, check=False,
            )
            if result.returncode:
                raise ValueError(f"javap could not inspect {class_name}: {result.stderr[:400]}")
            relevant: set[str] = set()
            for line in result.stdout.splitlines():
                names_on_line = re.findall(r"([A-Za-z_$][A-Za-z0-9_$]*)\s*\(", line)
                if not names_on_line:
                    continue
                method = names_on_line[-1]
                if any(word in method.lower()
                       for word in ("registry", "pack", "tag", "configuration")):
                    relevant.add(method)
            if len(relevant) > MAX_METHODS_PER_CANDIDATE:
                raise ValueError(f"unbounded client receiver methods: {class_name}")
            candidates.append({
                "class_name": class_name,
                "classfile_sha256_candidate": hashlib.sha256(bytecode).hexdigest(),
                "registry_related_method_names": sorted(relevant),
            })
        if not any(any("registry" in method.lower()
                       for method in candidate["registry_related_method_names"])
                   for candidate in candidates):
            raise ValueError("actual client Configuration listener has no registry method")
        return candidates


def identity_lock(path: Path) -> None:
    with path.open("rb") as stream:
        lock = tomllib.load(stream)
    if (lock.get("minecraft") != VERSION
        or lock.get("protocol") != PROTOCOL
        or lock.get("data_version") != DATA_VERSION
        or lock.get("source", {}).get("archive_sha256") != SOURCE_SHA256):
        raise ValueError("exact pinned 26.2 source/protocol identity drifted")


def official_version_metadata() -> dict:
    manifest = official.fetch_json(official.MANIFEST_URL)
    versions = manifest.get("versions")
    if not isinstance(versions, list):
        raise ValueError("official version manifest has no entries")
    entries = [entry for entry in versions
               if isinstance(entry, dict) and entry.get("id") == VERSION]
    if len(entries) != 1 or not isinstance(entries[0].get("url"), str):
        raise ValueError("official version manifest cannot uniquely resolve 26.2")
    metadata = official.fetch_json(entries[0]["url"])
    if metadata.get("id") != VERSION:
        raise ValueError("resolved official client metadata is for another version")
    return metadata


def discover(metadata: dict, cache: Path) -> dict:
    asset = required_client(metadata)
    local = cache / f"{VERSION}-client.jar"
    official.download(asset["url"], local, asset["sha1"], asset["size"])
    return {
        "schema": 1,
        "kind": KIND,
        "target": {"minecraft": VERSION, "protocol": PROTOCOL, "data_version": DATA_VERSION},
        "server_source_archive_sha256": SOURCE_SHA256,
        "official_executable_unobfuscated": True,
        "client_artifact": {
            "official_sha1": asset["sha1"],
            "observed_sha256_candidate": official.sha256_file(local),
            "official_size_bytes": asset["size"],
        },
        "client_configuration_listener_candidates": receiver_candidates(local),
        "source_inspected": False,
        "client_handler_invocation_proven": False,
        "client_numeric_id_assignment_proven": False,
        "production_admitted": False,
        "next_gate": (
            "Pin full client SHA-256 and classfile fingerprints; review exact "
            "stock client Configuration handler/delegates with javap -c or source; "
            "independently review registration order/errors and known-pack VAR/SEM"
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--lock", type=Path, default=LOCK)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    try:
        if args.output.exists() or args.output.is_symlink():
            raise ValueError("output must be a fresh file")
        if args.output.resolve(strict=False).is_relative_to(REPO.resolve(strict=True)):
            raise ValueError("discovery output cannot be written into repository")
        identity_lock(args.lock)
        with tempfile.TemporaryDirectory(prefix="helve-262-client-review-") as tmp:
            result = discover(official_version_metadata(), Path(tmp))
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, sort_keys=True, indent=2) + "\n",
                               encoding="utf-8")
    except (OSError, ValueError, KeyError, TypeError, zipfile.BadZipFile,
            subprocess.TimeoutExpired) as error:
        print(f"R2C official client discovery failed closed: {error}", file=sys.stderr)
        return 2
    print("Official unobfuscated client artifact and receiver class candidates found; "
          "client source review and VAR/SEM admission STILL REQUIRED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
