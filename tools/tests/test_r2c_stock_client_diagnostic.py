"""Local-only R2C diagnostic launcher preflight: no real client/network needed."""
from __future__ import annotations

import hashlib
import struct
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import r2c_stock_client_diagnostic as diagnostic


class LauncherTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.world = self.root / "world"
        (self.world / "dimensions/minecraft/overworld/region").mkdir(parents=True)
        (self.world / "level.dat").write_bytes(b"validated by Rust, not launcher")
        self.r2b = self.root / "playtest.bin"
        self.r2b.write_bytes(b"CRR2B001" + struct.pack("<I", 776) + b"test image payload")
        self.facts = self.root / "facts.bin"
        self.state_bytes = bytes([1]) * diagnostic.CANDIDATE_BYTES
        self.facts.write_bytes(self.state_bytes)
        self.checksum = hashlib.sha256(self.state_bytes).hexdigest()

    def arguments(self, *extra: str):
        return diagnostic.build_parser().parse_args([
            "--world", str(self.world),
            "--r2b-image", str(self.r2b),
            "--heightmap-bin", str(self.facts),
            *extra,
        ])

    def test_stage_existing_vanilla_regions_without_changing_any_source_bytes(self) -> None:
        vanilla = self.root / "vanilla-save"
        (vanilla / "region").mkdir(parents=True)
        level = b"preserve vanilla saved world metadata"
        (vanilla / "level.dat").write_bytes(level)
        originals = {}
        for i, name in enumerate(diagnostic.FIRST_VIEW_REGIONS):
            body = b"original anvil region " + bytes([i]) * (i + 1)
            (vanilla / "region" / name).write_bytes(body)
            originals[name] = body

        staging = self.root / "disposable"
        staged = diagnostic.stage_vanilla_overworld(vanilla, staging)
        self.assertNotEqual(staged, vanilla)
        self.assertEqual((staged / "level.dat").read_bytes(), level)
        for name, body in originals.items():
            copied = staged / "dimensions/minecraft/overworld/region" / name
            self.assertEqual(copied.read_bytes(), body)
            self.assertNotEqual(copied.stat().st_ino, (vanilla / "region" / name).stat().st_ino)
            self.assertEqual((vanilla / "region" / name).read_bytes(), body)

    def test_missing_required_region_or_symlink_never_creates_fake_chunks(self) -> None:
        vanilla = self.root / "vanilla-save"
        (vanilla / "region").mkdir(parents=True)
        (vanilla / "level.dat").write_bytes(b"untouched level")
        for name in diagnostic.FIRST_VIEW_REGIONS[1:]:
            (vanilla / "region" / name).write_bytes(b"source")
        with self.assertRaisesRegex(diagnostic.DiagnosticError, "required initial-view region"):
            diagnostic.stage_vanilla_overworld(vanilla, self.root / "attempt")
        self.assertFalse((self.root / "attempt").exists())
        missing = diagnostic.FIRST_VIEW_REGIONS[0]
        (vanilla / "region" / missing).symlink_to(vanilla / "region" / diagnostic.FIRST_VIEW_REGIONS[1])
        with self.assertRaisesRegex(diagnostic.DiagnosticError, "non-symlink"):
            diagnostic.stage_vanilla_overworld(vanilla, self.root / "attempt")

    def test_existing_namespaced_overworld_rejects_redundant_vanilla_staging(self) -> None:
        with self.assertRaisesRegex(diagnostic.DiagnosticError, "already has a namespaced Overworld"):
            diagnostic.stage_vanilla_overworld(self.world, self.root / "unused")

    def test_frozen_heightmap_identity_preflight(self) -> None:
        args = self.arguments("--preflight-only")
        with patch.object(diagnostic, "EXPECTED_DENSE_SHA256", self.checksum):
            self.assertEqual(diagnostic.prepare(args, self.root), (self.world, self.r2b, self.facts))
        with self.assertRaisesRegex(diagnostic.DiagnosticError, "pinned official runtime"):
            diagnostic.selected_heightmap(self.facts)

    def test_bad_region_layout_or_symlink_fails_before_launch(self) -> None:
        (self.world / "dimensions/minecraft/overworld/region").rmdir()
        with self.assertRaisesRegex(diagnostic.DiagnosticError, "region directory"):
            diagnostic.selected_world_root(self.world)
        (self.world / "dimensions/minecraft/overworld/region").symlink_to(self.root, target_is_directory=True)
        with self.assertRaisesRegex(diagnostic.DiagnosticError, "region directory"):
            diagnostic.selected_world_root(self.world)

    def test_bad_r2b_magic_or_protocol_fails(self) -> None:
        self.r2b.write_bytes(b"WRONGMAG" + struct.pack("<I", 776))
        with self.assertRaisesRegex(diagnostic.DiagnosticError, "wrong magic"):
            diagnostic.selected_r2b_image(self.r2b)
        self.r2b.write_bytes(b"CRR2B001" + struct.pack("<I", 775))
        with self.assertRaisesRegex(diagnostic.DiagnosticError, "wrong magic"):
            diagnostic.selected_r2b_image(self.r2b)

    def test_bad_table_length_and_symlink_fails(self) -> None:
        self.facts.write_bytes(b"\x00" * 100)
        with self.assertRaisesRegex(diagnostic.DiagnosticError, "32366"):
            diagnostic.selected_heightmap(self.facts)
        self.facts.unlink()
        self.facts.symlink_to(self.r2b)
        with self.assertRaisesRegex(diagnostic.DiagnosticError, "non-symlink"):
            diagnostic.selected_heightmap(self.facts)

    def test_diagnostic_port_range_rejected(self) -> None:
        for value in (0, -1, 65_536):
            with self.subTest(port=value):
                with self.assertRaisesRegex(diagnostic.DiagnosticError, "port"):
                    diagnostic.prepare(self.arguments("--port", str(value)), self.root)

    def test_only_the_ignored_explicit_test_receives_positive_environment(self) -> None:
        calls = []

        def fake_run(command, *, cwd, env, check):
            calls.append((command, env.copy()))
            return SimpleNamespace(returncode=0)

        with patch.object(diagnostic, "EXPECTED_DENSE_SHA256", self.checksum), \
                patch.object(diagnostic.shutil, "which", return_value="/mock/cargo"), \
                patch.object(diagnostic.subprocess, "run", side_effect=fake_run):
            self.assertEqual(diagnostic.main([
                "--world", str(self.world), "--r2b-image", str(self.r2b),
                "--heightmap-bin", str(self.facts), "--port", "25566",
            ]), 0)
        self.assertEqual(len(calls), 2)
        self.assertEqual(calls[0][0], diagnostic.rust_test_command(diagnostic.REHEARSAL, ignored=False))
        self.assertEqual(calls[1][0], diagnostic.rust_test_command(diagnostic.TEST, ignored=True))
        self.assertEqual(calls[1][1]["HELVE_R2C_DIAGNOSTIC_CONFIRM"], "UNADMITTED_LOCAL_ONLY")
        self.assertEqual(calls[1][1]["HELVE_R2C_DIAGNOSTIC_PORT"], "25566")
        self.assertEqual(calls[1][1]["HELVE_R2C_DIAGNOSTIC_EPOCH"], diagnostic.CAPTURE_EPOCH)

    def test_preflight_only_never_launches_a_test(self) -> None:
        with patch.object(diagnostic, "EXPECTED_DENSE_SHA256", self.checksum), \
                patch.object(diagnostic.subprocess, "run") as runner:
            self.assertEqual(diagnostic.main([
                "--world", str(self.world), "--r2b-image", str(self.r2b),
                "--heightmap-bin", str(self.facts), "--preflight-only",
            ]), 0)
        runner.assert_not_called()

    def test_a_failed_rehearsal_never_runs_the_live_test(self) -> None:
        calls = []

        def fake_run(command, *, cwd, env, check):
            calls.append(command)
            return SimpleNamespace(returncode=1)

        with patch.object(diagnostic, "EXPECTED_DENSE_SHA256", self.checksum), \
                patch.object(diagnostic.shutil, "which", return_value="/mock/cargo"), \
                patch.object(diagnostic.subprocess, "run", side_effect=fake_run):
            self.assertEqual(diagnostic.main([
                "--world", str(self.world), "--r2b-image", str(self.r2b),
                "--heightmap-bin", str(self.facts),
            ]), 2)
        self.assertEqual(len(calls), 1)
        self.assertEqual(calls[0], diagnostic.rust_test_command(diagnostic.REHEARSAL, ignored=False))

    def test_r1b_pack_is_delegated_to_the_existing_qualified_packer(self) -> None:
        r1b = self.root / "qualified-r1b.json"
        r1b.write_text("{}")
        args = diagnostic.build_parser().parse_args([
            "--world", str(self.world), "--r1b-image", str(r1b),
            "--heightmap-bin", str(self.facts),
        ])

        def fake_pack(source: Path, destination: Path):
            self.assertEqual(source, r1b)
            destination.write_bytes(self.r2b.read_bytes())
            return 34, 1024

        with patch.object(diagnostic, "EXPECTED_DENSE_SHA256", self.checksum), \
                patch.object(diagnostic.r2b, "pack", side_effect=fake_pack) as pack:
            world, image, facts = diagnostic.prepare(args, self.root)
        pack.assert_called_once()
        self.assertEqual(world, self.world)
        self.assertEqual(image.name, "helve-r2b-playtest.bin")
        self.assertEqual(facts, self.facts)


if __name__ == "__main__":
    unittest.main()
