"""Local-only R2C diagnostic launcher preflight: no real client/network needed."""
from __future__ import annotations

import hashlib
import json
import struct
import sys
import stat
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

    def make_evidence_regions(self) -> None:
        regions = self.world / "dimensions/minecraft/overworld/region"
        for index, name in enumerate(diagnostic.FIRST_VIEW_REGIONS):
            (regions / name).write_bytes(
                b"existing source region content " + bytes([index]) * 36
            )

    def test_source_evidence_preflight_is_private_source_free_and_new_only(self) -> None:
        self.make_evidence_regions()
        destination = self.root / "evidence.json"
        with patch.object(diagnostic, "EXPECTED_DENSE_SHA256", self.checksum):
            self.assertEqual(diagnostic.main([
                "--world", str(self.world), "--r2b-image", str(self.r2b),
                "--heightmap-bin", str(self.facts), "--preflight-only",
                "--evidence-json", str(destination),
            ]), 0)
        record = json.loads(destination.read_text())
        self.assertEqual(record["kind"], "r2c-26_2-local-stock-client-input-evidence-v1")
        self.assertEqual(record["outcome"], "PREFLIGHT_ONLY_NO_CLIENT")
        self.assertFalse(record["source_var_sem_admitted"])
        self.assertFalse(record["production_chunk_publication_admitted"])
        self.assertFalse(record["stock_client_pixels_independently_verified"])
        self.assertTrue(record["input_files_unchanged"])
        self.assertEqual(len(record["inputs"]["world_files"]), 5)
        self.assertEqual(len(record["inputs"]["selected_chunks"]), 9)
        self.assertEqual(record["inputs"]["r2b_image"]["sha256"],
                         hashlib.sha256(self.r2b.read_bytes()).hexdigest())
        self.assertEqual(record["inputs"]["heightmap_candidate"]["sha256"], self.checksum)
        self.assertEqual(stat.S_IMODE(destination.stat().st_mode), 0o600)
        self.assertNotIn(str(self.root), destination.read_text())
        self.assertNotIn("validated by Rust", destination.read_text())
        with patch.object(diagnostic, "EXPECTED_DENSE_SHA256", self.checksum):
            self.assertEqual(diagnostic.main([
                "--world", str(self.world), "--r2b-image", str(self.r2b),
                "--heightmap-bin", str(self.facts), "--preflight-only",
                "--evidence-json", str(destination),
            ]), 2)
        self.assertEqual(json.loads(destination.read_text()), record)

    def test_source_manifest_rejects_missing_symlinked_and_changed_inputs(self) -> None:
        self.make_evidence_regions()
        args = self.arguments("--evidence-json", str(self.root / "frozen.json"))
        with patch.object(diagnostic, "EXPECTED_DENSE_SHA256", self.checksum):
            baseline = diagnostic.evidence_snapshot(args, self.world, self.r2b, self.facts)
            observed = diagnostic.evidence_snapshot(args, self.world, self.r2b, self.facts)
        self.assertEqual(baseline, observed)
        moved = self.world / "dimensions/minecraft/overworld/region" / diagnostic.FIRST_VIEW_REGIONS[0]
        content = moved.read_bytes()
        moved.write_bytes(content + b"changed after preflight")
        with patch.object(diagnostic, "EXPECTED_DENSE_SHA256", self.checksum):
            self.assertNotEqual(baseline, diagnostic.evidence_snapshot(
                args, self.world, self.r2b, self.facts,
            ))
        moved.unlink()
        moved.symlink_to(self.world / "level.dat")
        with self.assertRaisesRegex(diagnostic.DiagnosticError, "non-symlink"):
            diagnostic.evidence_snapshot(args, self.world, self.r2b, self.facts)

    def test_evidence_failure_after_diagnostic_does_not_emit_success_report(self) -> None:
        self.make_evidence_regions()
        output = self.root / "should-not-exist.json"
        calls = 0

        def mutate_on_launch(command, *, cwd, env, check):
            nonlocal calls
            del command, cwd, env, check
            calls += 1
            if calls == 2:
                (self.world / "level.dat").write_bytes(b"world changed during run")
            return SimpleNamespace(returncode=0)

        with patch.object(diagnostic, "EXPECTED_DENSE_SHA256", self.checksum), \
                patch.object(diagnostic.shutil, "which", return_value="/mock/cargo"), \
                patch.object(diagnostic.subprocess, "run", side_effect=mutate_on_launch):
            self.assertEqual(diagnostic.main([
                "--world", str(self.world), "--r2b-image", str(self.r2b),
                "--heightmap-bin", str(self.facts),
                "--evidence-json", str(output),
            ]), 2)
        self.assertEqual(calls, 2)
        self.assertFalse(output.exists())

    def test_staged_vanilla_source_evidence_checks_original_byte_identity(self) -> None:
        self.make_evidence_regions()
        vanilla = self.root / "vanilla-source"
        (vanilla / "region").mkdir(parents=True)
        (vanilla / "level.dat").write_bytes((self.world / "level.dat").read_bytes())
        for name in diagnostic.FIRST_VIEW_REGIONS:
            (vanilla / "region" / name).write_bytes(
                (self.world / "dimensions/minecraft/overworld/region" / name).read_bytes()
            )
        staged = self.root / "stage"
        selected = diagnostic.stage_vanilla_overworld(vanilla, staged)
        args = self.arguments("--stage-vanilla-overworld")
        args.world = vanilla
        first = diagnostic.evidence_snapshot(args, selected, self.r2b, self.facts)
        self.assertEqual(len(first["original_vanilla_files"]), 5)
        (vanilla / "level.dat").write_bytes(b"mutated origin")
        with self.assertRaisesRegex(diagnostic.DiagnosticError, "differs from original"):
            diagnostic.evidence_snapshot(args, selected, self.r2b, self.facts)

    def test_source_evidence_destination_rejects_repo_and_symlinks(self) -> None:
        with self.assertRaisesRegex(diagnostic.DiagnosticError, "outside the repository"):
            diagnostic.evidence_destination(diagnostic.REPO_ROOT / "bad-evidence.json")
        target = self.root / "existing.json"
        target.write_text("not replaceable")
        with self.assertRaisesRegex(diagnostic.DiagnosticError, "never overwrite"):
            diagnostic.evidence_destination(target)
        link = self.root / "link.json"
        link.symlink_to(target)
        with self.assertRaisesRegex(diagnostic.DiagnosticError, "never overwrite"):
            diagnostic.evidence_destination(link)

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
        self.assertNotIn("HELVE_R2C_DIAGNOSTIC_RENDER_HALO", calls[0][1])
        self.assertNotIn("HELVE_R2C_DIAGNOSTIC_RENDER_HALO", calls[1][1])

    def test_renderer_halo_never_changes_the_rehearsal_and_is_opt_in_only(self) -> None:
        calls = []

        def fake_run(command, *, cwd, env, check):
            calls.append((command, env.copy()))
            return SimpleNamespace(returncode=0)

        reports = tuple(
            SimpleNamespace(
                x=i, z=i, evidence="EXPLICITLY_EMPTY", entries=(),
                region_sha256="abcdef" * 10,
            )
            for i in range(25)
        )
        with patch.object(diagnostic, "EXPECTED_DENSE_SHA256", self.checksum), \
                patch.object(diagnostic.shutil, "which", return_value="/mock/cargo"), \
                patch.object(diagnostic.subprocess, "run", side_effect=fake_run), \
                patch.object(diagnostic.saved_entities, "audit_world", return_value=reports) as read, \
                patch.dict(diagnostic.os.environ, {"HELVE_R2C_DIAGNOSTIC_RENDER_HALO": "unsafe"}):
            self.assertEqual(diagnostic.main([
                "--world", str(self.world), "--r2b-image", str(self.r2b),
                "--heightmap-bin", str(self.facts), "--render-halo",
            ]), 0)
        read.assert_called_once_with(self.world, 25)
        self.assertEqual(len(calls), 2)
        self.assertEqual(calls[0][0], diagnostic.rust_test_command(diagnostic.REHEARSAL, ignored=False))
        self.assertEqual(calls[1][0], diagnostic.rust_test_command(diagnostic.TEST, ignored=True))
        self.assertEqual(calls[1][1]["HELVE_R2C_DIAGNOSTIC_RENDER_HALO"], "1")

    def test_nonempty_25_halo_is_rejected_before_heightmap_java_or_listener(self) -> None:
        reports = tuple(
            SimpleNamespace(
                x=i, z=i,
                evidence="NONEMPTY (unsupported)" if i == 12 else "EXPLICITLY_EMPTY",
                entries=(("minecraft:beehive", 20, 74, 21),) if i == 12 else (),
                region_sha256="abcdef" * 10,
            )
            for i in range(25)
        )
        with patch.object(diagnostic.saved_entities, "audit_world", return_value=reports) as read, \
                patch.object(diagnostic.subprocess, "run") as runner, \
                patch.object(diagnostic.r2b, "pack") as pack:
            status = diagnostic.main([
                "--world", str(self.world), "--r2b-image", str(self.r2b),
                "--generate-heightmap", "--render-halo",
            ])
        self.assertEqual(status, 2)
        read.assert_called_once_with(self.world, 25)
        runner.assert_not_called()
        pack.assert_not_called()

    def test_malformed_or_missing_halo_source_stops_before_expensive_work(self) -> None:
        with patch.object(diagnostic.subprocess, "run") as runner:
            status = diagnostic.main([
                "--world", str(self.world), "--r2b-image", str(self.r2b),
                "--generate-heightmap", "--render-halo",
            ])
        self.assertEqual(status, 2)
        runner.assert_not_called()

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
