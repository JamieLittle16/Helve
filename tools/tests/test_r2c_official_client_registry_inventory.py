"""Official unobfuscated 26.2 client remains unadmitted until source review."""

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
import r2c_official_client_registry_inventory as probe

CLIENT_CLASS = "net/minecraft/client/multiplayer/ClientConfigurationPacketListenerImpl.class"
BYTECODE = b"\xca\xfe\xba\xbe" + b"synthetic-jvm-test-class"
JAVAP = """public class net.minecraft.client.multiplayer.ClientConfigurationPacketListenerImpl {
  public void handleRegistryData(net.minecraft.network.protocol.configuration.ClientboundRegistryDataPacket);
  public void handleUpdateTags(net.minecraft.network.protocol.configuration.ClientboundUpdateTagsPacket);
  public void close();
}
"""


def jar_bytes(entries: dict[str, bytes]) -> bytes:
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as archive:
        for name, content in entries.items():
            archive.writestr(name, content)
    return buffer.getvalue()


def meta() -> dict:
    return {
        "id": "26.2",
        "downloads": {
            "client": {"url": "https://example.invalid/client.jar",
                       "sha1": "a" * 40, "size": 123},
        },
    }


class OfficialClientSourceFrontierTests(unittest.TestCase):
    def test_unobfuscated_client_class_names_are_bounded_and_unadmitted(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            jar = Path(tmp) / "client.jar"
            jar.write_bytes(jar_bytes({CLIENT_CLASS: BYTECODE}))
            process = subprocess.CompletedProcess([], 0, JAVAP, "")
            with patch.object(probe.subprocess, "run", return_value=process):
                [candidate] = probe.receiver_candidates(jar)
            self.assertEqual(
                candidate["class_name"],
                "net.minecraft.client.multiplayer.ClientConfigurationPacketListenerImpl",
            )
            self.assertEqual(candidate["classfile_sha256_candidate"],
                             hashlib.sha256(BYTECODE).hexdigest())
            self.assertEqual(candidate["registry_related_method_names"],
                             ["handleRegistryData", "handleUpdateTags"])
            jar.write_bytes(jar_bytes({"net/minecraft/server/ServerListener.class": BYTECODE}))
            with self.assertRaisesRegex(ValueError, "no bounded"):
                probe.receiver_candidates(jar)
            jar.write_bytes(jar_bytes({CLIENT_CLASS: BYTECODE}))
            missing = subprocess.CompletedProcess([], 0, "public void handleTags();", "")
            with patch.object(probe.subprocess, "run", return_value=missing):
                with self.assertRaisesRegex(ValueError, "no registry method"):
                    probe.receiver_candidates(jar)

    def test_unobfuscated_metadata_has_exact_official_identity_fields(self) -> None:
        self.assertEqual(probe.required_client(meta())["size"], 123)
        for invalid in [
            {"url": "http://example.invalid/x", "sha1": "a" * 40, "size": 12},
            {"url": "https://example.invalid/x", "sha1": "short", "size": 12},
            {"url": "https://example.invalid/x", "sha1": "a" * 40, "size": 0},
            {"url": "https://example.invalid/x", "sha1": "a" * 40, "size": True},
            {"url": "https://example.invalid/x", "sha1": "a" * 40},
        ]:
            data = meta()
            data["downloads"]["client"] = invalid
            with self.subTest(invalid=invalid), self.assertRaises(ValueError):
                probe.required_client(data)
        old = meta()
        old["downloads"]["client_mappings"] = {
            "url": "https://example.invalid/mappings.txt",
            "sha1": "b" * 40, "size": 16
        }
        with self.assertRaisesRegex(ValueError, "unobfuscated"):
            probe.required_client(old)

    def test_lock_rejects_version_and_source_drift(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            lock = Path(d) / "lock.toml"
            lock.write_text(
                'minecraft = "26.2"\nprotocol = 776\ndata_version = 4903\n'
                '[source]\narchive_sha256 = "' + probe.SOURCE_SHA256 + '"\n'
            )
            probe.identity_lock(lock)
            lock.write_text(lock.read_text().replace("776", "777"))
            with self.assertRaises(ValueError):
                probe.identity_lock(lock)

    def test_discovery_emits_no_jar_or_bytecode_and_cannot_self_admit(self) -> None:
        blob = jar_bytes({CLIENT_CLASS: BYTECODE})

        def fake_download(url: str, output: Path, sha1: str, size: int) -> None:
            del url, sha1, size
            output.write_bytes(blob)

        process = subprocess.CompletedProcess([], 0, JAVAP, "")
        with tempfile.TemporaryDirectory() as tmp:
            with patch.object(probe.official, "download", side_effect=fake_download):
                with patch.object(probe.subprocess, "run", return_value=process):
                    result = probe.discover(meta(), Path(tmp))
        self.assertEqual(result["target"]["protocol"], 776)
        self.assertEqual(result["client_artifact"]["observed_sha256_candidate"],
                         hashlib.sha256(blob).hexdigest())
        self.assertTrue(result["official_executable_unobfuscated"])
        self.assertFalse(result["source_inspected"])
        self.assertFalse(result["client_handler_invocation_proven"])
        self.assertFalse(result["client_numeric_id_assignment_proven"])
        self.assertFalse(result["production_admitted"])
        self.assertEqual(len(result["client_configuration_listener_candidates"]), 1)
        self.assertNotIn("synthetic-jvm-test-class", json.dumps(result))
        self.assertNotIn("public void", json.dumps(result))


if __name__ == "__main__":
    unittest.main()
