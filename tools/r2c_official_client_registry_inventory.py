#!/usr/bin/env python3
"""Discover the exact *client-side* 26.2 biome receiver source-review frontier.

The pinned server source ZIP does not include the stock client's
Configuration listener. Download official client + official mappings only
from the Mojang 26.2 launcher metadata, check their SHA-1/size, and emit a
small source-free class/method inventory and SHA-256 candidates for later
independent source/bytecode review. No client JAR or mapping text is emitted.
This is *not* proof of the actual receiver path, ID assignment or admission.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import tempfile
import tomllib
from pathlib import Path

import official_state_data as official

VERSION = "26.2"
PROTOCOL = 776
DATA_VERSION = 4903
SOURCE_SHA256 = "1e9bca3dff83cd83e7905f8810f1ec9899361fa2dc83fe893bb48beeb04df750"
REPO = Path(__file__).resolve().parents[1]
LOCK = REPO / "vanilla/vanilla.lock.toml"
KIND = "r2c-official-client-receiver-artifact-discovery-v1"
MAX_CANDIDATES = 16
MAX_METHODS_PER_CANDIDATE = 64


def required_asset(meta: dict, key: str) -> dict:
    """Reject malformed or missing *official metadata* before any download."""
    asset = meta.get("downloads", {}).get(key)
    if not isinstance(asset, dict):
        raise ValueError(f"official 26.2 metadata has no {key}")
    if (set(asset) < {"url", "sha1", "size"}
        or not isinstance(asset["url"], str)
        or not asset["url"].startswith("https://")
        or not isinstance(asset["sha1"], str)
        or re.fullmatch(r"[0-9a-f]{40}", asset["sha1"]) is None
        or type(asset["size"]) is not int
        or not 0 < asset["size"] < 512 * 1024 * 1024):
        raise ValueError(f"invalid official metadata identity for {key}")
    return asset


def receiver_candidates(mappings: str) -> list[dict]:
    """Bound exact mapped class/method names; never assume call semantics."""
    classes, _, methods = official.parse_mappings(mappings)
    names = sorted(name for name in classes
                   if name.startswith("net.minecraft.client.")
                   and "Configuration" in name
                   and "Listener" in name)
    if not 1 <= len(names) <= MAX_CANDIDATES:
        raise ValueError("no unique bounded client Configuration listener frontier")
    candidates: list[dict] = []
    for name in names:
        relevant = sorted({method for owner, method in methods
                           if owner == name
                           and any(word in method.lower()
                                   for word in ("registry", "pack", "tag", "configuration"))})
        if len(relevant) > MAX_METHODS_PER_CANDIDATE:
            raise ValueError(f"unbounded mapped client methods in {name}")
        candidates.append({
            "mapped_class": name,
            "official_obfuscated_class": classes[name],
            "registry_related_method_names": relevant,
        })
    if not any(any("registry" in method.lower()
                   for method in candidate["registry_related_method_names"])
               for candidate in candidates):
        raise ValueError("mapped client Configuration frontier has no registry method")
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
    artifacts = {}
    for key in ("client", "client_mappings"):
        asset = required_asset(metadata, key)
        local = cache / f"{VERSION}-{key}.bin"
        official.download(asset["url"], local, asset["sha1"], asset["size"])
        artifacts[key] = {
            "official_sha1": asset["sha1"],
            "observed_sha256_candidate": official.sha256_file(local),
            "official_size_bytes": asset["size"],
        }
    mapped = (cache / f"{VERSION}-client_mappings.bin").read_text(encoding="utf-8")
    return {
        "schema": 1,
        "kind": KIND,
        "target": {"minecraft": VERSION, "protocol": PROTOCOL, "data_version": DATA_VERSION},
        "server_source_archive_sha256": SOURCE_SHA256,
        "artifacts": artifacts,
        "client_configuration_listener_candidates": receiver_candidates(mapped),
        "source_inspected": False,
        "client_handler_invocation_proven": False,
        "client_numeric_id_assignment_proven": False,
        "production_admitted": False,
        "next_gate": (
            "Pin complete client/mapping SHA-256; inspect exact stock-client Configuration "
            "handler bytecode/source and resolved network-registry delegates; independently "
            "review ordering, failures, VAR/SEM and known-pack identity before promotion"
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
    except (OSError, ValueError, KeyError, TypeError) as error:
        print(f"R2C official client discovery failed closed: {error}", file=sys.stderr)
        return 2
    print("Official client artifact identity and mapped receiver candidates discovered; "
          "client bytecode/source review and VAR/SEM admission STILL REQUIRED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
