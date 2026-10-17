"""Fail-closed fixtures for stock 26.2 packet numeric-ID builder inspection."""
from __future__ import annotations

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
import r2c_client_packet_builder_frontier as probe


CLASS_BYTES = b"\xca\xfe\xba\xbefake_builder"


def fake_class(name: str) -> str:
    return f"""public interface {name} {{
  public abstract net.minecraft.network.protocol.ProtocolInfoBuilder addPacket(java.lang.Object);
  public static net.minecraft.network.protocol.ProtocolInfoBuilder build();
    Code:
       0: new #10 // class net/minecraft/network/protocol/ProtocolInfoBuilder$Builder
       3: dup
       4: invokespecial #11 // Method java/lang/Object."<init>":()V
       7: areturn
  private void selected();
    Code:
       0: getstatic #12 // Field foo:Ljava/lang/Object;
       3: return
}}
"""


def fake_nested(name: str) -> str:
    return f"""class {name} {{
  public net.minecraft.network.protocol.ProtocolInfoBuilder addPacket(java.lang.Object);
    Code:
       0: aload_0
       1: getfield #21 // Field entries:Ljava/util/List;
       4: invokeinterface #22,  2 // InterfaceMethod java/util/List.add:(Ljava/lang/Object;)Z
       9: areturn
}}
"""


def make_jar(missing=False, duplicates=False):
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as jar:
        if not missing:
            jar.writestr(probe.ROOT + ".class", CLASS_BYTES)
            if duplicates:
                jar.writestr(probe.ROOT + ".class", CLASS_BYTES)
        jar.writestr(probe.ROOT + "$Builder.class", CLASS_BYTES)
    return buf.getvalue()


def fake_javap(args, **kwargs):
    del kwargs
    cls = args[-1]
    return subprocess.CompletedProcess(
        args, 0, fake_nested(cls) if cls.endswith("$Builder") else fake_class(cls), ""
    )


class ClientBuilderFrontierTests(unittest.TestCase):
    def test_method_boundaries_and_abstract_declaration_are_explicit(self):
        root = probe.inspect(fake_class(probe.OWNER), probe.OWNER)
        self.assertEqual([m["method_name"] for m in root["selected_methods"]],
                         ["addPacket", "build"])
        [decl, builder] = root["selected_methods"]
        self.assertTrue(decl["abstract_or_native_no_bytecode"])
        self.assertEqual(decl["instruction_count"], 0)
        self.assertFalse(builder["abstract_or_native_no_bytecode"])
        self.assertEqual(builder["instruction_count"], 4)
        self.assertEqual(builder["symbolic_edges_candidate"][0]["opcode"], "new")
        self.assertNotIn("Field foo:", json.dumps(root))
        self.assertFalse(root["builder_numeric_id_assignment_proven"])

    def test_bounded_fail_closed_code_and_symbol_inputs(self):
        cls = probe.OWNER
        with self.assertRaisesRegex(ValueError, "unbounded"):
            probe.inspect("x" * (probe.MAX_JAVAP_BYTES + 1), cls)
        with self.assertRaisesRegex(ValueError, "missing or excessive"):
            probe.inspect("no method here", cls)
        wrong = fake_nested(cls).replace("9: areturn", "0: areturn")
        with self.assertRaisesRegex(ValueError, "nonincreasing"):
            probe.inspect(wrong, cls)
        wrong = fake_nested(cls).replace("// InterfaceMethod", "InterfaceMethod")
        with self.assertRaisesRegex(ValueError, "unsymbolized"):
            probe.inspect(wrong, cls)

    def test_real_jar_roots_and_nested_class_are_distinct(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "client.jar"
            p.write_bytes(make_jar())
            with zipfile.ZipFile(p) as jar:
                roots = probe.builder_roots(jar)
            self.assertEqual(
                roots,
                [(probe.ROOT + ".class", probe.OWNER),
                 (probe.ROOT + "$Builder.class", probe.OWNER + "$Builder")]
            )
            with patch.object(probe.subprocess, "run", side_effect=fake_javap):
                classes = probe.inspect_client(p)
            self.assertEqual(len(classes), 2)
            [nested] = [item for item in classes if item["class_name"].endswith("$Builder")]
            self.assertEqual(
                nested["selected_methods"][0]["symbolic_edges_candidate"][1]["opcode"],
                "invokeinterface"
            )
            p.write_bytes(make_jar(missing=True))
            with zipfile.ZipFile(p) as jar:
                with self.assertRaisesRegex(ValueError, "missing or duplicate"):
                    probe.builder_roots(jar)
            p.write_bytes(make_jar(duplicates=True))
            with zipfile.ZipFile(p) as jar:
                with self.assertRaisesRegex(ValueError, "missing or duplicate"):
                    probe.builder_roots(jar)

    def test_candidate_report_cannot_claim_numeric_admission(self):
        raw = make_jar()
        meta = {"downloads": {"client": {"url": "https://example.invalid/test",
                                         "sha1": "f" * 40, "size": len(raw)}}}
        with tempfile.TemporaryDirectory() as tmp:
            def download(url, path, sha1, size):
                del url, sha1, size
                path.write_bytes(raw)
            with patch.object(probe.official_client.official, "download",
                              side_effect=download), patch.object(
                                  probe.subprocess, "run", side_effect=fake_javap):
                report = probe.discover(meta, Path(tmp))
        self.assertEqual(report["target"]["protocol"], 776)
        self.assertEqual(len(report["builder_class_candidates"]), 2)
        for key in ("builder_append_to_numeric_id_law_proven",
                    "bundle_numeric_id_effect_proven",
                    "serverbound_clientbound_direction_law_proven",
                    "independent_source_var_sem_admitted", "production_admitted"):
            self.assertFalse(report[key])
        self.assertNotIn("fake_builder", json.dumps(report))


if __name__ == "__main__":
    unittest.main()
