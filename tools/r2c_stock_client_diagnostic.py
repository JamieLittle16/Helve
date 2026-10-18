#!/usr/bin/env python3
"""Prepare and run the *test-only* R2C stock-client TCP diagnostic.

COLD developer orchestration only. All packet bodies, server-side source
receipts, session state and live socket ownership remain in the existing
Rust test harness. This script grants NO production source/VAR/SEM admission.
"""
from __future__ import annotations

import argparse
import hashlib
import os
import shutil
import struct
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Sequence

import r2b_pack_playtest as r2b
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


def stage_vanilla_overworld(source: Path, scratch: Path) -> Path:
    """Copy only the four *original* Anvil regions into test-only layout.

    The actual Rust bounded visitor and world metadata checker still own
    all semantic qualification. Never rewrite source NBT or remove entities.
    """
    source = source.expanduser().absolute()
    if source.is_symlink() or not source.is_dir():
        raise DiagnosticError(f"vanilla save must be a real non-symlink directory: {source}")
    region_dir = source / "region"
    if region_dir.is_symlink() or not region_dir.is_dir():
        raise DiagnosticError(f"expected a vanilla Overworld region/ directory: {region_dir}")
    if (source / "dimensions" / "minecraft" / "overworld").exists():
        raise DiagnosticError("save already has a namespaced Overworld; omit --stage-vanilla-overworld")
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
    parser.add_argument("--port", type=int, default=25565, help="loopback port (default: 25565)")
    parser.add_argument("--preflight-only", action="store_true", help="validate inputs without building or opening any listener")
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
        with tempfile.TemporaryDirectory(prefix="helve-r2c-diagnostic-") as directory:
            world, image, candidate = prepare(args, Path(directory))
            print("R2C local test-only preflight PASSED", flush=True)
            print(f"  world: {world}", flush=True)
            print(f"  R2B image: {image} (full commitments revalidated by Rust)", flush=True)
            print(f"  heightmap candidate: {candidate} (NOT source-admitted)", flush=True)
            if args.preflight_only:
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
            if not args.skip_rehearsal:
                print("R2C: running existing nine-chunk source-receipt + real TCP/ACK rehearsal", flush=True)
                outcome = subprocess.run(rust_test_command(REHEARSAL, ignored=False),
                                         cwd=REPO_ROOT, env=env, check=False)
                if outcome.returncode != 0:
                    raise DiagnosticError("nine-chunk TCP rehearsal failed; live client test withheld")
            print(f"Connect UNMODIFIED Minecraft Java 26.2 to localhost:{args.port}", flush=True)
            print("Keep the connection open through a keep-alive, then disconnect to end the test.", flush=True)
            print("WARNING: this is UNADMITTED, TEST-ONLY. Console success does NOT prove visible pixels.", flush=True)
            outcome = subprocess.run(rust_test_command(TEST, ignored=True),
                                     cwd=REPO_ROOT, env=env, check=False)
            if outcome.returncode != 0:
                raise DiagnosticError(f"R2C live client diagnostic exited with code {outcome.returncode}")
            print("R2C diagnostic socket/teleport/keep-alive passed. Visual rendering remains a MANUAL observation.", flush=True)
            print("Production R2C source admission remains unavailable.", flush=True)
            return 0
    except (DiagnosticError, OSError) as error:
        print(f"R2C diagnostic NO-GO: {error}", file=sys.stderr, flush=True)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
