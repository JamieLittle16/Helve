#!/usr/bin/env python3
"""Discover the exact unobfuscated *client-side* 26.2 registry receiver frontier.

Java 26.2 is shipped unobfuscated and has no client_mappings download. Fetch
only the official client JAR from the Mojang launcher manifest, check official
SHA-1/size, and emit SHA-256 class/artifact fingerprints plus bounded method
names and symbolic invoke-site metadata from javap. No JAR, bytecode
listing or original source is emitted.
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
MAX_INVOKES_PER_HANDLER = 96
MAX_COLLECTOR_METHODS = 32
MAX_COLLECTOR_INVOKES = 256
MAX_LOADER_LAMBDAS = 16
MAX_LOADER_LAMBDA_INVOKES = 256
MAX_REGISTRY_ROOT_OVERLOADS = 16
MAX_REGISTRY_ROOT_TOTAL_INVOKES = 256
REGISTRY_TASK_ROOTS = (
    ("net.minecraft.resources.RegistryLoadTask", ("load", "registerElements")),
    ("net.minecraft.resources.NetworkRegistryLoadTask", ("load",)),
    ("net.minecraft.core.MappedRegistry", ("register",)),
)

COLLECTOR_CLASS = "net.minecraft.client.multiplayer.RegistryDataCollector"
CONTENTS_CLASS = "net.minecraft.client.multiplayer.RegistryDataCollector$ContentsCollector"
LOADER_CLASS = "net.minecraft.resources.RegistryDataLoader"
HANDLER_NAMES = ("handleRegistryData", "handleConfigurationFinished", "handleSelectKnownPacks")


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



def handler_invocations(
    disassembly: str,
    *,
    method_names: tuple[str, ...] = HANDLER_NAMES,
    required_method: str | None = "handleRegistryData",
) -> list[dict]:
    """Summarize exact javap call *sites*, not source/bytecode or call proof.

    Method boundaries are taken from javap declarations, not a substring
    search across the whole class: an unrelated lambda cannot masquerade as
    handleRegistryData. Keep bytecode indexes and opcode for human review of
    dispatch and error paths, but never persist instruction listings.
    """
    found: dict[str, list[dict]] = {}
    current: str | None = None
    in_code = False
    for line in disassembly.splitlines():
        declaration = re.fullmatch(
            r"  (?:[^;{}]+ )?([\w$<>]+)\([^;]*\)(?: throws [^;]+)?;", line
        )
        if line == "  static {};" or line == "}":
            current = None
            in_code = False
            continue
        if declaration:
            name = declaration.group(1)
            current = name if name in method_names else None
            if current is not None:
                if current in found:
                    raise ValueError(f"ambiguous client handler overload: {current}")
                found[current] = []
            in_code = False
            continue
        if line.strip() == "Code:":
            in_code = current is not None
            continue
        if not in_code:
            continue
        insn = re.match(
            r"^\s*(\d+):\s+(invokevirtual|invokestatic|invokeinterface|invokespecial|invokedynamic)\s+#\d+",
            line,
        )
        if insn is None:
            continue
        if "// " not in line:
            raise ValueError("javap invocation without symbolic constant-pool target")
        target = line.split("// ", 1)[1].strip()
        if not target or len(target) > 8192:
            raise ValueError("empty or implausibly large symbolic invoke target")
        calls = found[current]
        calls.append({
            "bytecode_offset": int(insn.group(1)),
            "opcode": insn.group(2),
            "symbolic_target": target[:512],
            "symbolic_target_sha256": hashlib.sha256(target.encode("utf-8")).hexdigest(),
            "target_truncated": len(target) > 512,
        })
        if len(calls) > MAX_INVOKES_PER_HANDLER:
            raise ValueError("client registry handler exceeds bounded call-site limit")
    if required_method is not None and (
        required_method not in found or not found[required_method]
    ):
        raise ValueError(
            f"actual client handler has no inspectable {required_method} invokes"
        )
    return [{"handler": name, "invocations": found[name]}
            for name in method_names if name in found]


def inspect_handler_invocations(client: Path, class_name: str) -> list[dict]:
    """Disassemble one pinned official class, emitting *only* bounded invoke edges."""
    result = subprocess.run(
        ["javap", "-c", "-p", "-classpath", str(client), class_name],
        capture_output=True, text=True, timeout=30, check=False,
    )
    if result.returncode:
        raise ValueError(f"javap invocation inspection failed for {class_name}: "
                         f"{result.stderr[:400]}")
    if len(result.stdout) > 2_000_000:
        raise ValueError("client receiver disassembly exceeds bounded review")
    return handler_invocations(result.stdout)


def collector_candidate(client: Path) -> dict:
    """Trace only receiver-reached RegistryDataCollector, not an invented loader."""
    path = COLLECTOR_CLASS.replace(".", "/") + ".class"
    with zipfile.ZipFile(client) as archive:
        try:
            raw = archive.read(path)
        except KeyError as error:
            raise ValueError("official client is missing the exact registry collector") from error
    if not 4 <= len(raw) <= MAX_CLASS_BYTES or raw[:4] != b"\xca\xfe\xba\xbe":
        raise ValueError("invalid official registry collector classfile")
    result = subprocess.run(
        ["javap", "-c", "-p", "-classpath", str(client), COLLECTOR_CLASS],
        capture_output=True, text=True, timeout=30, check=False,
    )
    if result.returncode or len(result.stdout) > 2_000_000:
        raise ValueError("unbounded or uninspectable official client registry collector")
    methods: set[str] = set()
    for line in result.stdout.splitlines():
        declaration = re.fullmatch(
            r"  (?:[^;{}]+ )?([\w$<>]+)\([^;]*\)(?: throws [^;]+)?;", line
        )
        if declaration is not None:
            name = declaration.group(1)
            if name == "appendContents" or any(
                token in name.lower()
                for token in ("collect", "registr", "build", "load", "tag", "resource", "contents")
            ):
                methods.add(name)
    if "appendContents" not in methods or len(methods) > MAX_COLLECTOR_METHODS:
        raise ValueError("client collector review lacks bounded appendContents delegate")
    ordered = ("appendContents", *sorted(methods - {"appendContents"}))
    edges = handler_invocations(
        result.stdout, method_names=ordered, required_method="appendContents"
    )
    if sum(len(method["invocations"]) for method in edges) > MAX_COLLECTOR_INVOKES:
        raise ValueError("client collector method-call frontier exceeds total bound")
    return {
        "class_name": COLLECTOR_CLASS,
        "classfile_sha256_candidate": hashlib.sha256(raw).hexdigest(),
        "method_call_sites_candidate": edges,
    }



def inner_contents_candidate(client: Path) -> dict:
    """Follow the exact ContentsCollector.append delegate and fingerprint loader.

    Named class identities come from the preceding official-client call-site
    inventory, not a broad arbitrary jar scan. Store only symbolic invocation
    candidates; branch/field semantics still require manual source review.
    """
    paths = tuple(name.replace(".", "/") + ".class"
                  for name in (CONTENTS_CLASS, LOADER_CLASS))
    with zipfile.ZipFile(client) as archive:
        contents: list[bytes] = []
        for path in paths:
            if archive.namelist().count(path) != 1:
                raise ValueError(f"missing or duplicated exact client delegate: {path}")
            raw = archive.read(path)
            if not 4 <= len(raw) <= MAX_CLASS_BYTES or raw[:4] != b"\xca\xfe\xba\xbe":
                raise ValueError(f"invalid client delegate classfile: {path}")
            contents.append(raw)
    result = subprocess.run(
        ["javap", "-c", "-p", "-classpath", str(client), CONTENTS_CLASS],
        capture_output=True, text=True, timeout=30, check=False,
    )
    if result.returncode or len(result.stdout) > 2_000_000:
        raise ValueError("client inner contents appendix cannot be inspected")
    calls = handler_invocations(
        result.stdout, method_names=("append",), required_method="append"
    )
    return {
        "class_name": CONTENTS_CLASS,
        "classfile_sha256_candidate": hashlib.sha256(contents[0]).hexdigest(),
        "append_invoke_sites_candidate": calls,
        "registry_loader_class_name": LOADER_CLASS,
        "registry_loader_classfile_sha256_candidate": hashlib.sha256(contents[1]).hexdigest(),
    }




def loader_async_lambda_candidates(disassembly: str) -> list[dict]:
    """Bound compiler-generated loader lambdas, without asserting bootstrap links.

    Method-name matching alone cannot prove which Supplier or thenCompose
    callback is installed by invokedynamic. This is finite discovery for
    subsequent exact bootstrap resolution, not a source-admission decision.
    """
    declarations: dict[str, str] = {}
    for line in disassembly.splitlines():
        header = re.fullmatch(
            r"  (?:[^;{}]+ )?(lambda\$load\$[0-9]+)\([^;]*\)(?: throws [^;]+)?;",
            line,
        )
        if header is None:
            continue
        name = header.group(1)
        if name in declarations:
            raise ValueError(f"ambiguous loader lambda declaration: {name}")
        declarations[name] = line
        if len(declarations) > MAX_LOADER_LAMBDAS:
            raise ValueError("client loader async lambda count exceeds cap")
    if not declarations:
        raise ValueError("client async loader has no generated load lambdas")
    method_names = tuple(sorted(declarations))
    sites = handler_invocations(
        disassembly, method_names=method_names, required_method=None
    )
    if len(sites) != len(method_names):
        raise ValueError("loader lambda method bodies are missing")
    if sum(len(method["invocations"]) for method in sites) > MAX_LOADER_LAMBDA_INVOKES:
        raise ValueError("loader lambda invocation count exceeds cap")
    return [
        {
            "method_name": method["handler"],
            "declaration_sha256": hashlib.sha256(
                declarations[method["handler"]].encode("utf-8")
            ).hexdigest(),
            "invoke_sites_candidate": method["invocations"],
            "bootstrap_linkage_proven": False,
        }
        for method in sites
    ]


def registry_loader_overload_candidate(client: Path) -> dict:
    """Resolve *one* five-argument loader actually invoked by the collector.

    Check method-signature identity before inspecting body: the same class can
    contain other methods named load, whose calls do not establish the selected
    receiving-client route. This is a source-free invocation inventory only.
    """
    result = subprocess.run(
        ["javap", "-c", "-p", "-classpath", str(client), LOADER_CLASS],
        capture_output=True, text=True, timeout=30, check=False,
    )
    if result.returncode or len(result.stdout) > 2_000_000:
        raise ValueError("official registry loader disassembly is unavailable or unbounded")
    lines = result.stdout.splitlines()
    headers = [
        i for i, line in enumerate(lines)
        if re.fullmatch(
            r"  (?:[^;{}]+ )?([\w$<>]+)\([^;]*\)(?: throws [^;]+)?;",
            line,
        ) is not None
    ]
    selected = [
        (i, lines[i]) for i in headers
        if " load(" in lines[i]
        and "java.util.Map" in lines[i]
        and "net.minecraft.server.packs.resources.ResourceProvider" in lines[i]
        and lines[i].count("java.util.List") >= 2
        and "java.util.concurrent.Executor" in lines[i]
    ]
    if len(selected) != 1:
        raise ValueError("actual client collector loader overload must resolve exactly once")
    start, signature = selected[0]
    end = next((i for i in headers if i > start), len(lines))
    method = "\n".join(lines[start:end])
    [sites] = handler_invocations(
        method, method_names=("load",), required_method="load"
    )
    factory_overloads = [
        (i, lines[i]) for i in headers
        if " load(" in lines[i]
        and "net.minecraft.resources.RegistryDataLoader$LoaderFactory" in lines[i]
        and lines[i].count("java.util.List") >= 2
        and "java.util.concurrent.Executor" in lines[i]
        and "net.minecraft.server.packs.resources.ResourceProvider" not in lines[i]
    ]
    if len(factory_overloads) != 1:
        raise ValueError("receiver-reached loader factory overload must resolve exactly once")
    factory_start, factory_signature = factory_overloads[0]
    factory_end = next((i for i in headers if i > factory_start), len(lines))
    [factory_sites] = handler_invocations(
        "\n".join(lines[factory_start:factory_end]),
        method_names=("load",),
        required_method="load",
    )
    path = LOADER_CLASS.replace(".", "/") + ".class"
    with zipfile.ZipFile(client) as archive:
        if archive.namelist().count(path) != 1:
            raise ValueError("official RegistryDataLoader class is missing or duplicated")
        raw = archive.read(path)
    if not 4 <= len(raw) <= MAX_CLASS_BYTES or raw[:4] != b"\xca\xfe\xba\xbe":
        raise ValueError("official RegistryDataLoader classfile is malformed")
    lambda_candidates = loader_async_lambda_candidates(result.stdout)
    return {
        "class_name": LOADER_CLASS,
        "classfile_sha256_candidate": hashlib.sha256(raw).hexdigest(),
        "selected_overload_signature_sha256": hashlib.sha256(
            signature.encode("utf-8")
        ).hexdigest(),
        "selected_overload_invoke_sites_candidate": sites,
        "factory_overload_signature_sha256": hashlib.sha256(
            factory_signature.encode("utf-8")
        ).hexdigest(),
        "factory_overload_invoke_sites_candidate": factory_sites,
        "async_lambda_candidates": lambda_candidates,
        "source_inspected": False,
        "client_registration_order_admitted": False,
    }



def exact_registry_task_candidates(client: Path) -> list[dict]:
    """Pin selected source-reached registry task and ID-map class methods.

    A class being present does NOT prove it is used by the selected load,
    and a method named register does NOT prove insertion-order semantics.
    Preserve exact per-overload signatures, raw classfile fingerprints, and
    bounded symbolic call edges; source/VAR/SEM review must close that chain.
    """
    candidates: list[dict] = []
    with zipfile.ZipFile(client) as archive:
        for qualified_name, method_names in REGISTRY_TASK_ROOTS:
            path = qualified_name.replace(".", "/") + ".class"
            if archive.namelist().count(path) != 1:
                raise ValueError(f"registry task root must exist once: {qualified_name}")
            raw = archive.read(path)
            if not 4 <= len(raw) <= MAX_CLASS_BYTES or raw[:4] != b"\xca\xfe\xba\xbe":
                raise ValueError(f"invalid registry task classfile: {qualified_name}")
            result = subprocess.run(
                ["javap", "-c", "-p", "-classpath", str(client), qualified_name],
                capture_output=True, text=True, timeout=30, check=False,
            )
            if result.returncode or len(result.stdout) > 2_000_000:
                raise ValueError(f"uninspectable registry task root: {qualified_name}")
            lines = result.stdout.splitlines()
            headers: list[tuple[int, str, str]] = []
            for line_index, line in enumerate(lines):
                found = re.fullmatch(
                    r"  (?:[^;{}]+ )?([\w$<>]+)\([^;]*\)(?: throws [^;]+)?;",
                    line,
                )
                if found:
                    headers.append((line_index, found.group(1), line))
            selected = [
                (start, name, declaration)
                for start, name, declaration in headers
                if name in method_names
            ]
            if not 1 <= len(selected) <= MAX_REGISTRY_ROOT_OVERLOADS:
                raise ValueError(f"unbounded root methods: {qualified_name}")
            if set(method_names) - {name for _, name, _ in selected}:
                raise ValueError(f"required registry methods missing: {qualified_name}")
            members: list[dict] = []
            for start, name, declaration in selected:
                end = next((i for i, _, _ in headers if i > start), len(lines))
                [parsed] = handler_invocations(
                    "\n".join(lines[start:end]),
                    method_names=(name,),
                    required_method=None,
                )
                members.append({
                    "method_name": name,
                    "declaration_sha256": hashlib.sha256(
                        declaration.encode("utf-8")
                    ).hexdigest(),
                    "invoke_sites_candidate": parsed["invocations"],
                })
            if sum(len(m["invoke_sites_candidate"]) for m in members) > MAX_REGISTRY_ROOT_TOTAL_INVOKES:
                raise ValueError(f"registry task root invoke cap exceeded: {qualified_name}")
            candidates.append({
                "class_name": qualified_name,
                "classfile_sha256_candidate": hashlib.sha256(raw).hexdigest(),
                "method_candidates": members,
                "source_reviewed": False,
                "insertion_order_proven": False,
            })
    return candidates


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
                "client_handler_invoke_sites_candidate": (
                    inspect_handler_invocations(client, class_name)
                    if class_name.endswith(".ClientConfigurationPacketListenerImpl")
                    else []
                ),
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
        "client_registry_collector_candidate": collector_candidate(local),
        "client_inner_contents_candidate": inner_contents_candidate(local),
        "client_registry_loader_overload_candidate": registry_loader_overload_candidate(local),
        "registry_task_root_candidates": exact_registry_task_candidates(local),
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
