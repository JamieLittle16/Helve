"""Fail-closed method-shape evidence for the official Minecraft 26.2 client."""

from __future__ import annotations

import hashlib
import io
import json
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import r2c_client_order_semantic_frontier as probe

BYTECODE = b"\xca\xfe\xba\xbe" + b"synthetic-branch-fixture"


def fixture(class_name: str) -> str:
    out = [f"public class {class_name} {{"]
    for root, method in probe.METHODS:
        if root != class_name:
            continue
        out.extend([f"  public void {method}();", "    Code:",
                    "       0: aload_0", "       1: ifnonnull     4"])
        for i, target in enumerate(probe.REQUIRED_CALLS[(root, method)]):
            out.append(f"       {4+i}: invokestatic  #14 // Method exact/{target}()V")
        out.append(f"       {4+len(probe.REQUIRED_CALLS[(root, method)])}: return")
    out.extend(["  public void unrelated();", "    Code:",
                "       0: invokestatic #99 // Method fake/MappedRegistry.register:()V",
                "       3: return", "}"])
    return "\n".join(out) + "\n"


def jar_bytes(missing: str | None = None) -> bytes:
    content = io.BytesIO()
    with zipfile.ZipFile(content, "w") as jar:
        for cls, _ in probe.METHODS:
            if cls == missing:
                continue
            path = cls.replace(".", "/") + ".class"
            if path not in jar.namelist():
                jar.writestr(path, BYTECODE)
    return content.getvalue()


def mock_javap(args: list[str], **kwargs: object) -> subprocess.CompletedProcess:
    del kwargs
    return subprocess.CompletedProcess(args, 0, fixture(args[-1]), "")


class OfficialClientOrderSemanticFrontierTests(unittest.TestCase):
    def test_target_methods_only_and_ordered_checkpoints(self) -> None:
        for cls, method in probe.METHODS:
            with self.subTest(cls=cls, method=method):
                record = probe.bounded_method_shape(fixture(cls), cls, method)
                self.assertTrue(record["ordered_callsite_witness_matches"])
                self.assertEqual(len(record["conditional_branch_edges"]), 1)
                self.assertEqual(record["conditional_branch_edges"][0]["to"], 4)
                self.assertEqual(len(record["required_ordered_invoke_checkpoints"]),
                                 len(probe.REQUIRED_CALLS[(cls, method)]))
                self.assertFalse(record["all_control_flow_paths_reviewed"])
                self.assertFalse(record["exception_and_duplicate_semantics_proven"])
                self.assertNotIn("fake/MappedRegistry", json.dumps(record))
                self.assertNotIn("synthetic-branch-fixture", json.dumps(record))

    def test_reordering_drops_and_spoofed_neighbors_fail_closed(self) -> None:
        cls, method = probe.METHODS[0]
        original = fixture(cls)
        calls = probe.REQUIRED_CALLS[(cls, method)]
        reordered = original.replace(
            f"exact/{calls[0]}()V", "exact/swapped.first:()V"
        ).replace(
            f"exact/{calls[1]}()V", f"exact/{calls[0]}()V"
        ).replace(
            "exact/swapped.first:()V", f"exact/{calls[1]}()V"
        )
        with self.assertRaisesRegex(ValueError, "missing or reordered"):
            probe.bounded_method_shape(reordered, cls, method)
        deleted = original.replace(f"exact/{calls[1]}()V", "exact/missing:()V")
        with self.assertRaisesRegex(ValueError, "missing or reordered"):
            probe.bounded_method_shape(deleted, cls, method)
        duplicate = original.replace("  public void unrelated();",
                                     f"  public void {method}();")
        with self.assertRaisesRegex(ValueError, "ambiguous"):
            probe.bounded_method_shape(duplicate, cls, method)
        no_body = original.replace("    Code:", "    Missing:", 1)
        with self.assertRaisesRegex(ValueError, "no executable Code"):
            probe.bounded_method_shape(no_body, cls, method)

    def test_malformed_control_flow_and_uncertain_calls_fail_closed(self) -> None:
        cls, method = probe.METHODS[3]
        source = fixture(cls)
        with self.assertRaisesRegex(ValueError, "jumps outside parsed"):
            probe.bounded_method_shape(
                source.replace("ifnonnull     4", "ifnonnull     999"),
                cls, method,
            )
        with self.assertRaisesRegex(ValueError, "missing explicit JVM target"):
            probe.bounded_method_shape(
                source.replace("ifnonnull     4", "ifnonnull     unclear"),
                cls, method,
            )
        with self.assertRaisesRegex(ValueError, "symbolic invoke"):
            probe.bounded_method_shape(source.replace("// Method", "; Method"),
                                       cls, method)
        with self.assertRaisesRegex(ValueError, "oversized"):
            probe.bounded_method_shape("!" * (probe.MAX_DISASSEMBLY_CHARS + 1),
                                       cls, method)

    def test_full_26_2_client_pipeline_does_not_self_admit(self) -> None:
        raw = jar_bytes()
        meta = {"downloads": {"client": {
            "url": "https://example.invalid/26.2-client.jar",
            "sha1": "a" * 40,
            "size": len(raw),
        }}}
        with tempfile.TemporaryDirectory() as tmp:
            jar = Path(tmp) / "client.jar"
            jar.write_bytes(raw)
            with patch.object(probe.subprocess, "run", side_effect=mock_javap):
                results = probe.inspect_client(jar)
            self.assertEqual(len(results), 7)
            jar.write_bytes(jar_bytes(probe.METHODS[-1][0]))
            with patch.object(probe.subprocess, "run", side_effect=mock_javap):
                with self.assertRaisesRegex(ValueError, "missing/duplicate official"):
                    probe.inspect_client(jar)
            def fake_download(url: str, path: Path, sha1: str, size: int) -> None:
                del url, sha1, size
                path.write_bytes(raw)
            with patch.object(probe.receiver.official, "download",
                              side_effect=fake_download):
                with patch.object(probe.subprocess, "run", side_effect=mock_javap):
                    evidence = probe.discover(meta, Path(tmp))
        self.assertEqual(len(evidence["review_method_shapes"]), 7)
        self.assertEqual(evidence["official_client_sha256_candidate"],
                         hashlib.sha256(raw).hexdigest())
        self.assertFalse(evidence["complete_semantic_review"])
        self.assertFalse(evidence["client_numeric_id_assignment_proven"])
        self.assertFalse(evidence["source_var_sem_admitted"])
        self.assertFalse(evidence["production_admitted"])


if __name__ == "__main__":
    unittest.main()
