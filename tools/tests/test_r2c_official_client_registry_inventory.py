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
COLLECTOR_CLASS = "net/minecraft/client/multiplayer/RegistryDataCollector.class"
CONTENTS_CLASS = "net/minecraft/client/multiplayer/RegistryDataCollector$ContentsCollector.class"
LOADER_CLASS = "net/minecraft/resources/RegistryDataLoader.class"
BYTECODE = b"\xca\xfe\xba\xbe" + b"synthetic-jvm-test-class"
JAVAP = """public class net.minecraft.client.multiplayer.ClientConfigurationPacketListenerImpl {
  public void handleRegistryData(net.minecraft.network.protocol.configuration.ClientboundRegistryDataPacket);
  public void handleUpdateTags(net.minecraft.network.protocol.configuration.ClientboundUpdateTagsPacket);
  public void close();
}
"""


JAVAP_CODE = """public class net.minecraft.client.multiplayer.ClientConfigurationPacketListenerImpl {
  public void handleRegistryData(net.minecraft.network.protocol.configuration.ClientboundRegistryDataPacket);
    Code:
       0: aload_0
       1: invokevirtual #11 // Method net/minecraft/client/multiplayer/ClientConfigurationPacketListenerImpl.getData:()Ljava/lang/Object;
       4: aload_1
       5: invokeinterface #12,  2 // InterfaceMethod net/minecraft/resources/RegistryDataCollector.append:(Ljava/lang/Object;)V
      10: return

  public void close();
    Code:
       0: invokestatic #99 // Method net/minecraft/core/MappedRegistry.fake:()V

  public void handleSelectKnownPacks(net.minecraft.network.protocol.configuration.ClientboundSelectKnownPacks);
    Code:
       0: invokestatic #13 // Method net/minecraft/resources/KnownPacks.choose:()V
}
"""


JAVAP_COLLECTOR = """public class net.minecraft.client.multiplayer.RegistryDataCollector {
  public void appendContents(net.minecraft.resources.ResourceKey key, java.util.List entries);
    Code:
       0: aload_0
       1: invokevirtual #12 // Method java/util/HashMap.computeIfAbsent:(Ljava/lang/Object;Ljava/util/function/Function;)Ljava/lang/Object;
       4: return

  public void collectGameRegistries();
    Code:
       0: invokestatic #15 // Method net/minecraft/resources/NetworkRegistryLoadTask.load:()V
       3: return

  public void unrelated();
    Code:
       0: invokestatic #99 // Method net/minecraft/core/MappedRegistry.fake:()V
}
"""


JAVAP_CONTENTS = """public class net.minecraft.client.multiplayer.RegistryDataCollector$ContentsCollector {
  public void append(net.minecraft.resources.ResourceKey key, java.util.List entries);
    Code:
       0: aload_0
       1: getfield #13 // Field contents:Ljava/util/Map;
       4: aload_1
       5: aload_2
       6: invokeinterface #14,  3 // InterfaceMethod java/util/Map.put:(Ljava/lang/Object;Ljava/lang/Object;)Ljava/lang/Object;
      11: return

  public void unrelated();
    Code:
       0: invokestatic #99 // Method net/minecraft/core/MappedRegistry.fake:()V
}
"""


def mock_javap(args: list[str], **kwargs: object) -> subprocess.CompletedProcess:
    del kwargs
    if "-c" in args and probe.COLLECTOR_CLASS in args:
        return subprocess.CompletedProcess(args, 0, JAVAP_COLLECTOR, "")
    if "-c" in args and probe.CONTENTS_CLASS in args:
        return subprocess.CompletedProcess(args, 0, JAVAP_CONTENTS, "")
    return subprocess.CompletedProcess(
        args, 0, JAVAP_CODE if "-c" in args else JAVAP, ""
    )


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
            with patch.object(probe.subprocess, "run", side_effect=mock_javap):
                [candidate] = probe.receiver_candidates(jar)
            self.assertEqual(
                candidate["class_name"],
                "net.minecraft.client.multiplayer.ClientConfigurationPacketListenerImpl",
            )
            self.assertEqual(candidate["classfile_sha256_candidate"],
                             hashlib.sha256(BYTECODE).hexdigest())
            self.assertEqual(candidate["registry_related_method_names"],
                             ["handleRegistryData", "handleUpdateTags"])
            [receiver, known_packs] = candidate["client_handler_invoke_sites_candidate"]
            self.assertEqual(receiver["handler"], "handleRegistryData")
            self.assertEqual([edge["bytecode_offset"] for edge in receiver["invocations"]],
                             [1, 5])
            self.assertIn("RegistryDataCollector.append",
                          receiver["invocations"][1]["symbolic_target"])
            self.assertEqual(known_packs["handler"], "handleSelectKnownPacks")
            self.assertEqual(known_packs["invocations"][0]["opcode"], "invokestatic")
            jar.write_bytes(jar_bytes({"net/minecraft/server/ServerListener.class": BYTECODE}))
            with self.assertRaisesRegex(ValueError, "no bounded"):
                probe.receiver_candidates(jar)
            jar.write_bytes(jar_bytes({CLIENT_CLASS: BYTECODE}))
            missing = subprocess.CompletedProcess([], 0, "public void handleTags();", "")
            with patch.object(probe.subprocess, "run", return_value=missing):
                with self.assertRaisesRegex(ValueError, "no inspectable handleRegistryData"):
                    probe.receiver_candidates(jar)

    def test_inspection_is_per_handler_bounded_and_not_whole_class_search(self) -> None:
        self.assertEqual(len(probe.handler_invocations(JAVAP_CODE)), 2)
        bad = JAVAP_CODE.replace(
            "public void handleRegistryData(net.minecraft.network.protocol.configuration.ClientboundRegistryDataPacket);",
            "public void unrelated(net.minecraft.network.protocol.configuration.ClientboundRegistryDataPacket);",
        )
        with self.assertRaisesRegex(ValueError, "no inspectable handleRegistryData"):
            probe.handler_invocations(bad)
        duplicate = JAVAP_CODE.replace(
            "  public void close();",
            "  public void handleRegistryData(int ordinal);"
        )
        with self.assertRaisesRegex(ValueError, "ambiguous"):
            probe.handler_invocations(duplicate)
        no_symbol = JAVAP_CODE.replace(
            "// InterfaceMethod net/minecraft/resources/RegistryDataCollector.append:(Ljava/lang/Object;)V",
            ""
        )
        with self.assertRaisesRegex(ValueError, "symbolic constant-pool target"):
            probe.handler_invocations(no_symbol)
        long_name = "net/minecraft/BigDelegate." + ("x" * 600)
        long_javap = JAVAP_CODE.replace(
            "net/minecraft/resources/RegistryDataCollector.append:(Ljava/lang/Object;)V",
            long_name,
        )
        [receiver, _] = probe.handler_invocations(long_javap)
        edge = receiver["invocations"][1]
        self.assertTrue(edge["target_truncated"])
        self.assertEqual(len(edge["symbolic_target"]), 512)
        self.assertEqual(edge["symbolic_target_sha256"],
                         hashlib.sha256(("InterfaceMethod " + long_name).encode()).hexdigest())
        too_large = JAVAP_CODE.replace(
            "net/minecraft/resources/RegistryDataCollector.append:(Ljava/lang/Object;)V",
            "net/minecraft/BigDelegate." + ("x" * 8200),
        )
        with self.assertRaisesRegex(ValueError, "implausibly large"):
            probe.handler_invocations(too_large)
        flooding = JAVAP_CODE.replace(
            "      10: return",
            "      10: return\n" + "\n".join(
                "      11: invokestatic #11 // Method net/minecraft/Util.x:()V"
                for _ in range(probe.MAX_INVOKES_PER_HANDLER)
            ),
        )
        with self.assertRaisesRegex(ValueError, "bounded call-site"):
            probe.handler_invocations(flooding)


    def test_collector_is_exact_class_only_and_cannot_reach_unrelated_methods(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            jar = Path(tmp) / "client.jar"
            jar.write_bytes(jar_bytes({COLLECTOR_CLASS: BYTECODE}))
            with patch.object(probe.subprocess, "run", side_effect=mock_javap):
                collector = probe.collector_candidate(jar)
            self.assertEqual(len(collector["method_call_sites_candidate"]), 2)
            self.assertNotIn("MappedRegistry.fake", json.dumps(collector))
            jar.write_bytes(jar_bytes({CLIENT_CLASS: BYTECODE}))
            with self.assertRaisesRegex(ValueError, "missing the exact registry collector"):
                probe.collector_candidate(jar)
            jar.write_bytes(jar_bytes({COLLECTOR_CLASS: BYTECODE}))
            no_append = JAVAP_COLLECTOR.replace("appendContents(", "different(")
            with patch.object(
                probe.subprocess, "run",
                return_value=subprocess.CompletedProcess([], 0, no_append, ""),
            ), self.assertRaisesRegex(ValueError, "bounded appendContents"):
                probe.collector_candidate(jar)
            empty_body = JAVAP_COLLECTOR.replace(
                "       1: invokevirtual #12 // Method java/util/HashMap.computeIfAbsent:(Ljava/lang/Object;Ljava/util/function/Function;)Ljava/lang/Object;",
                "       1: nop",
            )
            with patch.object(
                probe.subprocess, "run",
                return_value=subprocess.CompletedProcess([], 0, empty_body, ""),
            ), self.assertRaisesRegex(ValueError, "no inspectable appendContents"):
                probe.collector_candidate(jar)


    def test_exact_nested_append_and_loader_classes_are_both_required(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            jar = Path(tmp) / "client.jar"
            jar.write_bytes(jar_bytes({CONTENTS_CLASS: BYTECODE, LOADER_CLASS: BYTECODE}))
            with patch.object(probe.subprocess, "run", side_effect=mock_javap):
                observed = probe.inner_contents_candidate(jar)
            self.assertEqual(observed["classfile_sha256_candidate"],
                             hashlib.sha256(BYTECODE).hexdigest())
            self.assertNotIn("MappedRegistry.fake", json.dumps(observed))
            jar.write_bytes(jar_bytes({CONTENTS_CLASS: BYTECODE}))
            with self.assertRaisesRegex(ValueError, "missing or duplicated"):
                probe.inner_contents_candidate(jar)
            jar.write_bytes(jar_bytes({CONTENTS_CLASS: b"wrong", LOADER_CLASS: BYTECODE}))
            with self.assertRaisesRegex(ValueError, "invalid client delegate"):
                probe.inner_contents_candidate(jar)
            jar.write_bytes(jar_bytes({CONTENTS_CLASS: BYTECODE, LOADER_CLASS: BYTECODE}))
            wrong = JAVAP_CONTENTS.replace("public void append(", "public void other(")
            with patch.object(
                probe.subprocess, "run",
                return_value=subprocess.CompletedProcess([], 0, wrong, ""),
            ), self.assertRaisesRegex(ValueError, "no inspectable append"):
                probe.inner_contents_candidate(jar)

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
        blob = jar_bytes({CLIENT_CLASS: BYTECODE, COLLECTOR_CLASS: BYTECODE,
                         CONTENTS_CLASS: BYTECODE, LOADER_CLASS: BYTECODE})

        def fake_download(url: str, output: Path, sha1: str, size: int) -> None:
            del url, sha1, size
            output.write_bytes(blob)

        with tempfile.TemporaryDirectory() as tmp:
            with patch.object(probe.official, "download", side_effect=fake_download):
                with patch.object(probe.subprocess, "run", side_effect=mock_javap):
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
        collector = result["client_registry_collector_candidate"]
        self.assertEqual(collector["class_name"], probe.COLLECTOR_CLASS)
        self.assertEqual(
            [method["handler"] for method in collector["method_call_sites_candidate"]],
            ["appendContents", "collectGameRegistries"],
        )
        self.assertIn("HashMap.computeIfAbsent",
                      collector["method_call_sites_candidate"][0]["invocations"][0]
                      ["symbolic_target"])
        inner = result["client_inner_contents_candidate"]
        self.assertEqual(inner["class_name"], probe.CONTENTS_CLASS)
        self.assertEqual(inner["registry_loader_class_name"], probe.LOADER_CLASS)
        self.assertEqual(len(inner["append_invoke_sites_candidate"]), 1)
        self.assertIn("Map.put", inner["append_invoke_sites_candidate"][0]["invocations"][0]
                      ["symbolic_target"])
        self.assertNotIn("synthetic-jvm-test-class", json.dumps(result))
        self.assertNotIn("public void", json.dumps(result))


if __name__ == "__main__":
    unittest.main()
