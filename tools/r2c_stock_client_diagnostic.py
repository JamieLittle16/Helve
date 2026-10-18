#!/usr/bin/env python3
"""Prepare and run the *test-only* R2C stock-client TCP diagnostic.

COLD developer orchestration only. All packet bodies, server-side source
receipts, session state and live socket ownership remain in the existing
Rust test harness. This script grants NO production source/VAR/SEM admission.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import stat
import shutil
import struct
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Sequence

import r2b_pack_playtest as r2b
import r2c_first_view_block_entities as saved_entities
from r2c_heightmap_candidate_bytes import EXPECTED_DENSE_SHA256

REPO_ROOT = Path(__file__).resolve().parents[1]
CONFIRM = "UNADMITTED_LOCAL_ONLY"
CAPTURE_EPOCH = "4d7f604f196a43b08987f0b2a27c2663"
TEST = "r2b_playtest::r2c_stock_client_diagnostic::manual_stock_client_receives_real_anvil_chunks"
REHEARSAL = "r2c_disk_first_view::tests::nine_disk_chunks_cross_four_regions_and_reach_one_receipted_batch"
CANDIDATE_BYTES = 32_366
# R2B's pinned teleport (10.39, 84, -5.815) selects a 3x3 first view
# spanning the four signed Anvil regions adjacent to world origin.
# These are *existing bytes* from the user's vanilla save, never
# fabricated chunks or an altered block-entity list.
FIRST_VIEW_REGIONS = (
    "r.-1.-1.mca", "r.-1.0.mca", "r.0.-1.mca", "r.0.0.mca",
)
REGION_BYTES_LIMIT = 64 * 1024 * 1024


class DiagnosticError(ValueError):
    """Fail-closed local diagnostic prerequisite or command error."""


def existing_file(path: Path, description: str, *, maximum: int | None = None) -> Path:
    """Reject symlinks and non-regular/missing files without reading large input."""
    path = path.expanduser().absolute()
    if path.is_symlink() or not path.is_file():
        raise DiagnosticError(f"{description} must be an existing regular non-symlink file: {path}")
    if maximum is not None and path.stat().st_size > maximum:
        raise DiagnosticError(f"{description} exceeds its maximum size of {maximum} bytes: {path}")
    return path


def selected_world_root(world: Path) -> Path:
    """Check the exact directory shape already consumed by R2cColdWorldPlan."""
    world = world.expanduser().absolute()
    root = world
    for part in ("dimensions", "minecraft", "overworld", "region"):
        if root.is_symlink() or not root.is_dir():
            raise DiagnosticError(f"26.2 world root has missing/symlinked directory: {root}")
        root = root / part
    if root.is_symlink() or not root.is_dir():
        raise DiagnosticError(f"26.2 Overworld region directory missing/symlinked: {root}")
    existing_file(world / "level.dat", "26.2 saved-world level.dat", maximum=4 * 1024 * 1024)
    # DataVersion/NBT and each requested Anvil region are checked again by the
    # exact existing Rust loader: do not create another NBT parser here.
    return world


def preflight_render_halo(world: Path) -> None:
    """COLD-only full source check, before Java generation or any listener.

    Same existing Anvil/NBT inspection oracle as the manual first-view
    diagnostic; no mutation and no authority to source-admit packets.
    The real Rust importer still independently checks each source receipt.
    """
    try:
        reports = saved_entities.audit_world(world, saved_entities.RENDER_HALO_CHUNKS)
    except (OSError, saved_entities.SourceAuditError) as error:
        raise DiagnosticError(f"25-chunk source preflight rejected: {error}") from error
    if not saved_entities.print_report(reports):
        raise DiagnosticError(
            "25-chunk render halo has unsupported saved block entities or "
            "missing explicitly-empty evidence; no heightmap generated and "
            "no socket opened"
        )
    print("R2C COLD 25-source-chunk block-entity preflight PASSED", flush=True)


def stage_vanilla_overworld(source: Path, scratch: Path) -> Path:
    """Copy only the four *original* Anvil regions into test-only layout.

    The actual Rust bounded visitor and world metadata checker still own
    all semantic qualification. Never rewrite source NBT or remove entities.
    """
    source = source.expanduser().absolute()
    if source.is_symlink() or not source.is_dir():
        raise DiagnosticError(f"vanilla save must be a real non-symlink directory: {source}")
    if (source / "dimensions" / "minecraft" / "overworld").exists():
        raise DiagnosticError("save already has a namespaced Overworld; omit --stage-vanilla-overworld")
    region_dir = source / "region"
    if region_dir.is_symlink() or not region_dir.is_dir():
        raise DiagnosticError(f"expected a vanilla Overworld region/ directory: {region_dir}")
    level = existing_file(
        source / "level.dat", "vanilla level.dat", maximum=4 * 1024 * 1024,
    )
    regions = tuple(
        existing_file(region_dir / name, f"required initial-view region {name}",
                      maximum=REGION_BYTES_LIMIT)
        for name in FIRST_VIEW_REGIONS
    )
    destination = scratch / "original-vanilla-overworld"
    target_regions = destination / "dimensions" / "minecraft" / "overworld" / "region"
    target_regions.mkdir(parents=True, exist_ok=False)
    # A copy, not symlinks or hardlinks: Minecraft cannot modify the source
    # after the snapshot, and R2C cannot modify the original save.
    shutil.copyfile(level, destination / "level.dat")
    for region in regions:
        shutil.copyfile(region, target_regions / region.name)
    print(
        "R2C COLD staging: copied original vanilla level.dat and "
        f"{len(regions)} signed Anvil regions to a disposable test-only view; "
        "no block entities removed or rewritten",
        flush=True,
    )
    return selected_world_root(destination)


def selected_r2b_image(image: Path) -> Path:
    image = existing_file(image, "R2B playtest image", maximum=300_000)
    with image.open("rb") as stream:
        header = stream.read(12)
    if len(header) != 12 or header[:8] != r2b.MAGIC or struct.unpack("<I", header[8:])[0] != 776:
        raise DiagnosticError("R2B image has wrong magic or protocol; use tools/r2b_pack_playtest.py")
    # The actual R2B Rust image loader authenticates source/capture and all
    # Configuration/body commitments before contacting the client.
    return image


def selected_heightmap(candidate: Path) -> Path:
    candidate = existing_file(candidate, "heightmap state candidate", maximum=CANDIDATE_BYTES)
    data = candidate.read_bytes()
    if len(data) != CANDIDATE_BYTES:
        raise DiagnosticError(f"heightmap candidate requires {CANDIDATE_BYTES} exact state bytes")
    if hashlib.sha256(data).hexdigest() != EXPECTED_DENSE_SHA256:
        raise DiagnosticError("heightmap candidate bytes do not match the pinned official runtime oracle")
    return candidate



def evidence_destination(path: Path) -> Path:
    """Require one fresh local file outside the repository, never overwrite."""
    path = path.expanduser().absolute()
    if path.exists() or path.is_symlink():
        raise DiagnosticError("R2C evidence output must be a new file; never overwrite a prior run")
    if path.parent.is_symlink() or not path.parent.is_dir():
        raise DiagnosticError("R2C evidence output parent must be an existing real directory")
    if path.resolve(strict=False).is_relative_to(REPO_ROOT.resolve()):
        raise DiagnosticError("R2C local source evidence must remain outside the repository")
    return path


def evidence_file(path: Path, relative: str, limit: int) -> dict:
    """Snapshot bounded file identity and digest without exposing local paths.

    Open without following symlinks; reject source changes during hashing.
    This is reproducible input identity, not NBT or semantic qualification.
    """
    existing_file(path, relative, maximum=limit)
    fd = os.open(path, os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0))
    with os.fdopen(fd, "rb") as stream:
        before = os.fstat(stream.fileno())
        if not stat.S_ISREG(before.st_mode) or before.st_size > limit:
            raise DiagnosticError(f"evidence source not a bounded regular file: {relative}")
        digest = hashlib.sha256()
        total = 0
        while block := stream.read(128 * 1024):
            total += len(block)
            if total > limit:
                raise DiagnosticError(f"evidence source exceeds bounded limit: {relative}")
            digest.update(block)
        after = os.fstat(stream.fileno())
    path_now = path.lstat()
    if (before.st_ino, before.st_dev, before.st_size, before.st_mtime_ns) != (
        after.st_ino, after.st_dev, after.st_size, after.st_mtime_ns
    ) or (after.st_ino, after.st_dev, after.st_size, after.st_mtime_ns) != (
        path_now.st_ino, path_now.st_dev, path_now.st_size, path_now.st_mtime_ns
    ) or total != after.st_size or not stat.S_ISREG(path_now.st_mode):
        raise DiagnosticError(f"evidence source changed while being read: {relative}")
    return {"relative_path": relative, "bytes": total, "sha256": digest.hexdigest()}


def evidence_snapshot(args: argparse.Namespace, world: Path, image: Path, candidate: Path) -> dict:
    """Freeze the exact preselected source inputs, using the existing view law."""
    count = saved_entities.RENDER_HALO_CHUNKS if args.render_halo else saved_entities.INITIAL_CHUNKS
    positions = saved_entities.first_view_positions(count)
    regions = sorted({
        f"r.{x // 32}.{z // 32}.mca" for x, z in positions
    })
    def source_files(root: Path, *, staged: bool) -> list[dict]:
        prefix = ("region/" if staged else "dimensions/minecraft/overworld/region/")
        files = [evidence_file(root / "level.dat", "level.dat", 4 * 1024 * 1024)]
        files.extend(
            evidence_file(root / prefix / name, prefix + name, REGION_BYTES_LIMIT)
            for name in regions
        )
        return files

    selected_files = source_files(world, staged=False)
    original_files = (
        source_files(args.world.expanduser().absolute(), staged=True)
        if args.stage_vanilla_overworld else None
    )
    if original_files is not None and [
        (item["bytes"], item["sha256"]) for item in original_files
    ] != [
        (item["bytes"], item["sha256"]) for item in selected_files
    ]:
        raise DiagnosticError("disposable staging differs from original vanilla save bytes")
    return {
        "world_files": selected_files,
        "original_vanilla_files": original_files,
        "r2b_image": evidence_file(image, "r2b-playtest-image", 300_000),
        "heightmap_candidate": evidence_file(candidate, "heightmap-state-candidate", CANDIDATE_BYTES),
        "selected_chunks": [[x, z] for x, z in positions],
    }


def write_evidence(path: Path, snapshot: dict, *, preflight_only: bool) -> None:
    """Persist a source-free, operator-owned *diagnostic*, never an admission."""
    destination = evidence_destination(path)
    report = {
        "schema": 1,
        "kind": "r2c-26_2-local-stock-client-input-evidence-v1",
        "target": {"minecraft": "26.2", "protocol": 776, "data_version": 4903},
        "outcome": (
            "PREFLIGHT_ONLY_NO_CLIENT"
            if preflight_only else "TEST_ONLY_TRANSPORT_COMPLETED_VISUAL_MANUAL"
        ),
        "input_files_unchanged": True,
        "inputs": snapshot,
        "source_var_sem_admitted": False,
        "production_chunk_publication_admitted": False,
        "stock_client_pixels_independently_verified": False,
        "client_logs_and_screenshot": "RETAIN_AND_REVIEW_SEPARATELY",
        "operator_repository_commit": "RECORD_SEPARATELY",
    }
    payload = json.dumps(report, indent=2, sort_keys=True) + "\n"
    fd = os.open(
        destination,
        os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0),
        0o600,
    )
    with os.fdopen(fd, "w", encoding="utf-8") as stream:
        stream.write(payload)


def rust_test_command(name: str, *, ignored: bool) -> list[str]:
    arguments = ["cargo", "test", "--locked", "-p", "helve-server", "--lib", name, "--", "--exact"]
    if ignored:
        arguments.extend(("--ignored", "--nocapture", "--test-threads=1"))
    return arguments


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run the ignored local Minecraft Java 26.2 R2C diagnostic. NEVER production/source-admitted."
    )
    parser.add_argument("--world", type=Path, required=True, help="26.2 save root with level.dat and dimensions/minecraft/overworld/region/")
    image = parser.add_mutually_exclusive_group(required=True)
    image.add_argument("--r2b-image", type=Path, help="already prepared CRR2B001 playtest image")
    image.add_argument("--r1b-image", type=Path, help="qualified R1B JSON; pack with existing validated tool")
    heightmap = parser.add_mutually_exclusive_group(required=True)
    heightmap.add_argument("--heightmap-bin", type=Path, help="verified 32,366-byte official candidate from existing CI")
    heightmap.add_argument("--generate-heightmap", action="store_true", help="run the existing pinned Java 25 oracle and candidate converter")
    parser.add_argument(
        "--stage-vanilla-overworld", action="store_true",
        help="COLD-copy the four unchanged first-view regions from an ordinary "
             "vanilla save root containing region/ (no block-entity edits)",
    )
    parser.add_argument(
        "--render-halo", action="store_true",
        help="COLD test-only: publish 25 actual source chunks (5x5) so the interior "
             "3x3 has loaded rendering neighbors; default remains 9 chunks",
    )
    parser.add_argument("--port", type=int, default=25565, help="loopback port (default: 25565)")
    parser.add_argument("--preflight-only", action="store_true", help="validate inputs without building or opening any listener")
    parser.add_argument(
        "--evidence-json", type=Path,
        help="write one new, private, source-free input digest report outside the repo "
             "after preflight or successful test; never source admission",
    )
    parser.add_argument("--skip-rehearsal", action="store_true", help="skip the existing nine-chunk test (e.g. after green CI)")
    return parser


def prepare(args: argparse.Namespace, scratch: Path) -> tuple[Path, Path, Path]:
    if not 1 <= args.port <= 65_535:
        raise DiagnosticError("port must be in the range 1..65535")
    world = (
        stage_vanilla_overworld(args.world, scratch)
        if args.stage_vanilla_overworld
        else selected_world_root(args.world)
    )
    if args.render_halo:
        preflight_render_halo(world)

    if args.r2b_image is not None:
        image = selected_r2b_image(args.r2b_image)
    else:
        # The existing source-free R1B validation and selected R2B packer
        # alone own this transformation; no captured Play-world packets enter.
        input_path = existing_file(args.r1b_image, "qualified R1B capture JSON")
        image_path = scratch / "helve-r2b-playtest.bin"
        try:
            r2b.pack(input_path, image_path)
        except (OSError, ValueError) as error:
            raise DiagnosticError(f"R1B source/capture-qualified packing rejected: {error}") from error
        image = selected_r2b_image(image_path)

    if args.heightmap_bin is not None:
        candidate = selected_heightmap(args.heightmap_bin)
    else:
        if shutil.which("java") is None or shutil.which("javac") is None:
            raise DiagnosticError("official runtime heightmap generation requires Java 25 (java and javac)")
        candidate_json = scratch / "26.2-heightmap-oracle.json"
        candidate_bin = scratch / "26.2-heightmap-oracle.bin"
        commands = (
            [sys.executable, str(REPO_ROOT / "tools/official_r2c_heightmap_facts.py"),
             "--output", str(candidate_json)],
            [sys.executable, str(REPO_ROOT / "tools/r2c_heightmap_candidate_bytes.py"),
             "--input", str(candidate_json), "--output", str(candidate_bin)],
        )
        for command in commands:
            if subprocess.run(command, cwd=REPO_ROOT, check=False).returncode != 0:
                raise DiagnosticError("pinned official runtime candidate generation failed; see preceding output")
        candidate = selected_heightmap(candidate_bin)
    return world, image, candidate


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        evidence_path = (
            evidence_destination(args.evidence_json)
            if args.evidence_json is not None else None
        )
        with tempfile.TemporaryDirectory(prefix="helve-r2c-diagnostic-") as directory:
            world, image, candidate = prepare(args, Path(directory))
            snapshot = (
                evidence_snapshot(args, world, image, candidate)
                if evidence_path is not None else None
            )
            print("R2C local test-only preflight PASSED", flush=True)
            print(f"  world: {world}", flush=True)
            print(f"  R2B image: {image} (full commitments revalidated by Rust)", flush=True)
            print(f"  heightmap candidate: {candidate} (NOT source-admitted)", flush=True)
            if args.preflight_only:
                if evidence_path is not None and snapshot is not None:
                    if evidence_snapshot(args, world, image, candidate) != snapshot:
                        raise DiagnosticError("R2C preflight evidence inputs changed")
                    write_evidence(evidence_path, snapshot, preflight_only=True)
                print("No TCP listener opened. This is NOT a visible-world result.", flush=True)
                return 0
            if shutil.which("cargo") is None:
                raise DiagnosticError("cargo is required to compile the isolated Rust test harness")
            env = os.environ.copy()
            env.update({
                "HELVE_R2C_DIAGNOSTIC_CONFIRM": CONFIRM,
                "HELVE_R2C_DIAGNOSTIC_EPOCH": CAPTURE_EPOCH,
                "HELVE_R2C_DIAGNOSTIC_R2B_IMAGE": str(image),
                "HELVE_R2C_DIAGNOSTIC_WORLD": str(world),
                "HELVE_R2C_HEIGHTMAP_CANDIDATE": str(candidate),
                "HELVE_R2C_DIAGNOSTIC_PORT": str(args.port),
            })
            # Never inherit a positive test-only halo gate from an unrelated
            # shell environment; only this explicit launcher option may set it.
            env.pop("HELVE_R2C_DIAGNOSTIC_RENDER_HALO", None)
            if args.render_halo:
                env["HELVE_R2C_DIAGNOSTIC_RENDER_HALO"] = "1"
            if not args.skip_rehearsal:
                print("R2C: running existing nine-chunk source-receipt + real TCP/ACK rehearsal", flush=True)
                outcome = subprocess.run(rust_test_command(REHEARSAL, ignored=False),
                                         cwd=REPO_ROOT, env=env, check=False)
                if outcome.returncode != 0:
                    raise DiagnosticError("nine-chunk TCP rehearsal failed; live client test withheld")
            if args.render_halo:
                print(
                    "R2C TEST-ONLY renderer halo: 25 genuine source chunks (5x5); "
                    "interior 3x3 can meet the eight-neighbor mesh requirement",
                    flush=True,
                )
            print(f"Connect UNMODIFIED Minecraft Java 26.2 to localhost:{args.port}", flush=True)
            print("Keep the connection open through a keep-alive, then disconnect to end the test.", flush=True)
            print("WARNING: this is UNADMITTED, TEST-ONLY. Console success does NOT prove visible pixels.", flush=True)
            outcome = subprocess.run(rust_test_command(TEST, ignored=True),
                                     cwd=REPO_ROOT, env=env, check=False)
            if outcome.returncode != 0:
                raise DiagnosticError(f"R2C live client diagnostic exited with code {outcome.returncode}")
            if evidence_path is not None and snapshot is not None:
                if evidence_snapshot(args, world, image, candidate) != snapshot:
                    raise DiagnosticError(
                        "R2C source/image/heightmap inputs changed during diagnostic; "
                        "evidence file withheld"
                    )
                write_evidence(evidence_path, snapshot, preflight_only=False)
                print(f"R2C source-free local evidence written: {evidence_path}", flush=True)
            print("R2C diagnostic socket/teleport/keep-alive passed. Visual rendering remains a MANUAL observation.", flush=True)
            print("Production R2C source admission remains unavailable.", flush=True)
            return 0
    except (DiagnosticError, OSError) as error:
        print(f"R2C diagnostic NO-GO: {error}", file=sys.stderr, flush=True)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
