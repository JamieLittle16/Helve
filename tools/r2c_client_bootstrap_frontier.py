#!/usr/bin/env python3
"""Bound exact Java 26.2 receiving-client invokedynamic/bootstrap relationships.

Read only the SHA/size-checked, disposable Mojang unobfuscated client JAR.
Resolve *specific* listener-reached registry loader/sequence method bodies
to their LambdaMetafactory implementation handles using javap -v. Export only
source-free class/signature hashes and invoke-site -> bootstrap -> method-handle
metadata, never disassembly, binary or decompiled source.

Bootstrap call-site linkage is evidence, NOT a review of ordering, exception
handling, parallel execution, known-pack behavior or biome ID source admission.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

import r2c_official_client_registry_inventory as client_probe

KIND = "r2c-26_2-receiver-client-lambda-bootstrap-candidates-v1"
MAX_CLASS_BYTES = 1_048_576
MAX_VERBOSE_CHARS = 6_000_000
MAX_BOOTSTRAPS = 256
MAX_LAMBDA_LINKS_PER_CLASS = 32
MAX_SOURCE_METHODS = 4
# Precisely rooted in the official-client listener -> collector -> network task
# -> sequence and client loader-factory path. Do not discover by broad wildcard.
ROOTS = (
    ("net.minecraft.resources.NetworkRegistryLoadTask",
     ("load", "lambda$load$2")),
    ("net.minecraft.util.Util",
     ("sequence", "lambda$sequence$0")),
    ("net.minecraft.resources.RegistryDataLoader",
     ("load", "lambda$load$0")),
    ("net.minecraft.resources.RegistryLoadTask",
     ("registerElements", "lambda$registerElements$0")),
)
DECLARATION = re.compile(
    r"  (?:[^;{}]+ )?([\w$<>]+)\([^;]*\)(?: throws [^;]+)?;"
)
BOOTSTRAP_HEADER = re.compile(r"^  (\d+): #\d+ REF_\w+ (.+)$")
BOOTSTRAP_IMPL = re.compile(r"^\s+#\d+ (REF_invoke\w+) (.+)$")
CALLSITE = re.compile(
    r"^\s*(\d+):\s+invokedynamic\s+#\d+.*// InvokeDynamic #(\d+):([^\s]+)"
)


def extract_bootstraps(verbose: str) -> dict[int, dict]:
    """Read javap's named BootstrapMethods section, never constant-pool guesses."""
    begin = verbose.find("\nBootstrapMethods:\n")
    if begin < 0:
        raise ValueError("verbose client class lacks BootstrapMethods")
    seen: dict[int, dict] = {}
    current: int | None = None
    for line in verbose[begin + len("\nBootstrapMethods:\n"):].splitlines():
        if line and not line.startswith((" ", "\t")):
            break
        found = BOOTSTRAP_HEADER.fullmatch(line)
        if found:
            number = int(found.group(1))
            if number in seen or number > MAX_BOOTSTRAPS:
                raise ValueError("duplicate or unbounded bootstrap index")
            seen[number] = {"factory": found.group(2), "handles": []}
            current = number
            continue
        if current is None:
            continue
        handle = BOOTSTRAP_IMPL.fullmatch(line)
        if handle and not line.lstrip().startswith("#0 "):
            seen[current]["handles"].append({
                "kind": handle.group(1),
                "target": handle.group(2),
            })
            if len(seen[current]["handles"]) > 16:
                raise ValueError("excessive bootstrap method-handle arguments")
    if not seen:
        raise ValueError("client bootstrap section has no records")
    return seen


def select_methods(verbose: str, class_name: str) -> list[dict]:
    lines = verbose.splitlines()
    headers: list[tuple[int, str, str]] = []
    for i, line in enumerate(lines):
        found = DECLARATION.fullmatch(line)
        if found:
            headers.append((i, found.group(1), line))
    selected: list[dict] = []
    required = dict(ROOTS)[class_name]
    for name in required:
        matches = [(index, header) for index, method, header in headers
                   if method == name]
        if name == "load" and class_name == "net.minecraft.resources.RegistryDataLoader":
            matches = [(index, header) for index, header in matches
                       if "net.minecraft.resources.RegistryDataLoader$LoaderFactory" in header
                       and header.count("java.util.List") >= 2
                       and "java.util.concurrent.Executor" in header]
        if len(matches) != 1:
            raise ValueError(f"missing/ambiguous rooted method {class_name}#{name}")
        start, signature = matches[0]
        end = next((i for i, _, _ in headers if i > start), len(lines))
        method_lines = lines[start:end]
        # No extraction of field/branch semantics; only exact indy offsets.
        calls: list[tuple[int, int, str]] = []
        for line in method_lines:
            found = CALLSITE.match(line)
            if found:
                calls.append((int(found.group(1)), int(found.group(2)), found.group(3)))
        selected.append({
            "method_name": name,
            "declaration_sha256": hashlib.sha256(signature.encode()).hexdigest(),
            "indy_candidates": calls,
        })
    if len(selected) > MAX_SOURCE_METHODS:
        raise ValueError("unbounded rooted client method inventory")
    return selected


def inspect_verbose(verbose: str, class_name: str) -> list[dict]:
    """Resolve exact invokedynamic constants to LambdaMetafactory handles."""
    if not 0 < len(verbose) <= MAX_VERBOSE_CHARS:
        raise ValueError("unbounded client verbose class output")
    if class_name not in dict(ROOTS):
        raise ValueError("not an approved receiver-reached class")
    bootstraps = extract_bootstraps(verbose)
    output: list[dict] = []
    for selected in select_methods(verbose, class_name):
        candidates: list[dict] = []
        for offset, bsm_index, description in selected["indy_candidates"]:
            bsm = bootstraps.get(bsm_index)
            if bsm is None:
                raise ValueError(f"invokedynamic refers to absent bootstrap #{bsm_index}")
            # These specific rooted methods use dynamic lambdas. Other
            # invokedynamic forms such as string concat cannot be accepted
            # as an inferred registration callback.
            if "java/lang/invoke/LambdaMetafactory." not in bsm["factory"]:
                raise ValueError(f"non-lambda bootstrap on rooted method #{bsm_index}")
            handles = bsm["handles"]
            if len(handles) != 1:
                raise ValueError("lambda bootstrap lacks unique implementation handle")
            target = handles[0]["target"]
            if not 0 < len(target) <= 8192:
                raise ValueError("unbounded lambda implementation target")
            candidates.append({
                "bytecode_offset": offset,
                "bootstrap_index": bsm_index,
                "callsite_shape": description[:192],
                "bootstrap_factory": bsm["factory"].split(":")[0][:160],
                "impl_handle_kind": handles[0]["kind"],
                "impl_handle_target_candidate": target[:384],
                "impl_handle_sha256": hashlib.sha256(target.encode()).hexdigest(),
                "impl_handle_truncated": len(target) > 384,
            })
            if len(candidates) > MAX_LAMBDA_LINKS_PER_CLASS:
                raise ValueError("too many rooted client lambda links")
        output.append({
            "method_name": selected["method_name"],
            "declaration_sha256": selected["declaration_sha256"],
            "bootstrap_method_handle_links_candidate": candidates,
        })
    if not any(m["bootstrap_method_handle_links_candidate"] for m in output):
        raise ValueError("no invokedynamic bootstrap links in targeted methods")
    return output


def inspect_client(client: Path) -> list[dict]:
    records: list[dict] = []
    with zipfile.ZipFile(client) as archive:
        names = archive.namelist()
        for class_name, _ in ROOTS:
            path = class_name.replace(".", "/") + ".class"
            if names.count(path) != 1:
                raise ValueError(f"missing exact client class: {class_name}")
            raw = archive.read(path)
            if not 4 <= len(raw) <= MAX_CLASS_BYTES or raw[:4] != b"\xca\xfe\xba\xbe":
                raise ValueError(f"invalid exact client class: {class_name}")
            process = subprocess.run(
                ["javap", "-v", "-p", "-c", "-classpath", str(client), class_name],
                capture_output=True, text=True, timeout=35, check=False,
            )
            if process.returncode or len(process.stdout) > MAX_VERBOSE_CHARS:
                raise ValueError(f"could not bound official client verbose class: {class_name}")
            item = {
                "class_name": class_name,
                "classfile_sha256_candidate": hashlib.sha256(raw).hexdigest(),
                "selected_methods": inspect_verbose(process.stdout, class_name),
            }
            if class_name == "net.minecraft.resources.RegistryLoadTask":
                [callback] = client_probe.handler_invocations(
                    process.stdout,
                    method_names=("lambda$registerElements$0",),
                    required_method="lambda$registerElements$0",
                )
                item["register_consumer_callback_invocations_candidate"] = callback
            records.append(item)
    return records


def discover(metadata: dict, cache: Path) -> dict:
    asset = client_probe.required_client(metadata)
    local = cache / "26.2-client.jar"
    client_probe.official.download(asset["url"], local, asset["sha1"], asset["size"])
    return {
        "schema": 1,
        "kind": KIND,
        "target": {"minecraft": "26.2", "protocol": 776, "data_version": 4903},
        "official_client_sha1": asset["sha1"],
        "official_client_sha256_candidate": client_probe.official.sha256_file(local),
        "official_client_size_bytes": asset["size"],
        "rooted_class_bootstraps": inspect_client(local),
        "invokedynamic_bootstrap_resolution_inspected": True,
        "full_branch_and_error_semantics_reviewed": False,
        "client_numeric_id_assignment_proven": False,
        "source_var_sem_admitted": False,
        "production_admitted": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    try:
        if args.output.exists() or args.output.is_symlink():
            raise ValueError("bootstrap candidate output must be fresh")
        if args.output.resolve(strict=False).is_relative_to(client_probe.REPO.resolve()):
            raise ValueError("discovery output cannot be stored in the repository")
        client_probe.identity_lock(client_probe.LOCK)
        with tempfile.TemporaryDirectory(prefix="helve-r2c-indy-") as scratch:
            result = discover(client_probe.official_version_metadata(), Path(scratch))
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, sort_keys=True, indent=2) + "\n")
    except (OSError, ValueError, KeyError, TypeError, subprocess.TimeoutExpired,
            zipfile.BadZipFile) as error:
        print(f"Official client bootstrap discovery failed closed: {error}", file=sys.stderr)
        return 2
    print("Official client lambda bootstrap call-site candidates resolved; "
          "branch/error/ordering semantics and VAR/SEM NOT ADMITTED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
