"""Source-free, fail-closed official 26.2 client invokedynamic frontier tests."""

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
import r2c_client_bootstrap_frontier as probe

BYTECODE = b"\xca\xfe\xba\xbe" + b"synthetic-class"
HANDLES = {
    "net.minecraft.resources.NetworkRegistryLoadTask": (
        "load", "lambda$load$2",
        "net/minecraft/resources/NetworkRegistryLoadTask.lambda$load$2:"
    ),
    "net.minecraft.util.Util": (
        "sequence", "lambda$sequence$0", "net/minecraft/util/Util.lambda$sequence$0:"
    ),
    "net.minecraft.resources.RegistryDataLoader": (
        "load", "lambda$load$0", "net/minecraft/resources/RegistryDataLoader.lambda$load$0:"
    ),
}


def verbose_fixture(class_name: str) -> str:
    main, helper, handle = HANDLES[class_name]
    if class_name == "net.minecraft.resources.RegistryDataLoader":
        declaration = (
            "  public static java.util.concurrent.CompletableFuture load("
            "net.minecraft.resources.RegistryDataLoader$LoaderFactory, "
            "java.util.List, java.util.List, java.util.concurrent.Executor);"
        )
    else:
        declaration = f"  public static java.util.concurrent.CompletableFuture {main}(java.util.List);"
    return (
        f"public class {class_name} {{\n"
        f"{declaration}\n"
        "    descriptor: (Ljava/util/List;)Ljava/util/concurrent/CompletableFuture;\n"
        "    flags: (0x0009) ACC_PUBLIC, ACC_STATIC\n"
        "    Code:\n"
        "       0: aload_0\n"
        "       1: invokedynamic #101,  0 // InvokeDynamic #0:apply:()Ljava/util/function/Function;\n"
        "       6: areturn\n"
        f"  private static java.lang.Object {helper}(java.lang.Object);\n"
        "    descriptor: (Ljava/lang/Object;)Ljava/lang/Object;\n"
        "    Code:\n"
        "       0: aload_0\n"
        "       1: invokedynamic #102,  0 // InvokeDynamic #1:apply:()Ljava/util/function/Function;\n"
        "       6: areturn\n"
        "  public static void irrelevant();\n"
        "    Code:\n"
        "       0: invokestatic #300 // Method net/minecraft/core/MappedRegistry.wrong:()V\n"
        "}\n"
        "BootstrapMethods:\n"
        "  0: #120 REF_invokeStatic java/lang/invoke/LambdaMetafactory.metafactory:(...)\n"
        "    Method arguments:\n"
        "      #128 (Ljava/lang/Object;)Ljava/lang/Object;\n"
        f"      #129 REF_invokeStatic {handle}(Ljava/lang/Object;)Ljava/lang/Object;\n"
        "      #130 (Ljava/lang/Object;)Ljava/lang/Object;\n"
        "  1: #120 REF_invokeStatic java/lang/invoke/LambdaMetafactory.metafactory:(...)\n"
        "    Method arguments:\n"
        "      #128 (Ljava/lang/Object;)Ljava/lang/Object;\n"
        "      #129 REF_invokeVirtual java/util/concurrent/CompletableFuture.join:()Ljava/lang/Object;\n"
        "      #130 (Ljava/lang/Object;)Ljava/lang/Object;\n"
        "InnerClasses:\n"
        "  public static final #200= #201 of #202;\n"
    )



def registration_consumer_fixture() -> str:
    return """public class net.minecraft.resources.RegistryLoadTask {
  public void registerElements(java.util.stream.Stream);
    descriptor: (Ljava/util/stream/Stream;)V
    Code:
       0: aload_1
       1: invokedynamic #101,  0 // InvokeDynamic #0:accept:(Lnet/minecraft/resources/RegistryLoadTask;)Ljava/util/function/Consumer;
       6: invokeinterface #102,  2 // InterfaceMethod java/util/stream/Stream.forEach:(Ljava/util/function/Consumer;)V
      11: return
  private void lambda$registerElements$0(net.minecraft.resources.RegistryLoadTask$PendingRegistration);
    descriptor: (Lnet/minecraft/resources/RegistryLoadTask$PendingRegistration;)V
    Code:
       0: aload_1
       1: getfield #200 // Field net/minecraft/resources/RegistryLoadTask$PendingRegistration.value:Lcom/mojang/datafixers/util/Either;
       4: aload_0
       5: aload_1
       6: invokedynamic #111,  0 // InvokeDynamic #1:accept:(Lnet/minecraft/resources/RegistryLoadTask;Lnet/minecraft/resources/RegistryLoadTask$PendingRegistration;)Ljava/util/function/Consumer;
      11: invokevirtual #103 // Method com/mojang/datafixers/util/Either.ifLeft:(Ljava/util/function/Consumer;)Lcom/mojang/datafixers/util/Either;
      14: aload_0
      15: aload_1
      16: invokedynamic #112,  0 // InvokeDynamic #2:accept:(Lnet/minecraft/resources/RegistryLoadTask;Lnet/minecraft/resources/RegistryLoadTask$PendingRegistration;)Ljava/util/function/Consumer;
      21: invokevirtual #106 // Method com/mojang/datafixers/util/Either.ifRight:(Ljava/util/function/Consumer;)Lcom/mojang/datafixers/util/Either;
      24: pop
      25: return
  private void lambda$registerElements$1(net.minecraft.resources.RegistryLoadTask$PendingRegistration, java.lang.Object);
    descriptor: (Lnet/minecraft/resources/RegistryLoadTask$PendingRegistration;Ljava/lang/Object;)V
    Code:
       0: aload_0
       1: getfield #201 // Field registry:Lnet/minecraft/core/WritableRegistry;
       4: aload_1
       5: getfield #202 // Field net/minecraft/resources/RegistryLoadTask$PendingRegistration.key:Lnet/minecraft/resources/ResourceKey;
       8: aload_2
       9: aload_1
      10: getfield #203 // Field net/minecraft/resources/RegistryLoadTask$PendingRegistration.registrationInfo:Lnet/minecraft/core/RegistrationInfo;
      13: invokeinterface #104,  4 // InterfaceMethod net/minecraft/core/WritableRegistry.register:(Lnet/minecraft/resources/ResourceKey;Ljava/lang/Object;Lnet/minecraft/core/RegistrationInfo;)Lnet/minecraft/core/Holder$Reference;
      18: pop
      19: return
  private void lambda$registerElements$2(net.minecraft.resources.RegistryLoadTask$PendingRegistration, java.lang.Exception);
    descriptor: (Lnet/minecraft/resources/RegistryLoadTask$PendingRegistration;Ljava/lang/Exception;)V
    Code:
       0: aload_0
       1: getfield #204 // Field loadingErrors:Ljava/util/Map;
       4: aload_1
       5: getfield #205 // Field net/minecraft/resources/RegistryLoadTask$PendingRegistration.key:Lnet/minecraft/resources/ResourceKey;
       8: aload_2
       9: invokeinterface #105,  3 // InterfaceMethod java/util/Map.put:(Ljava/lang/Object;Ljava/lang/Object;)Ljava/lang/Object;
      14: pop
      15: return
}
BootstrapMethods:
  0: #120 REF_invokeStatic java/lang/invoke/LambdaMetafactory.metafactory:(...)
    Method arguments:
      #128 (Ljava/lang/Object;)V
      #129 REF_invokeVirtual net/minecraft/resources/RegistryLoadTask.lambda$registerElements$0:(Lnet/minecraft/resources/RegistryLoadTask$PendingRegistration;)V
      #130 (Ljava/lang/Object;)V
  1: #120 REF_invokeStatic java/lang/invoke/LambdaMetafactory.metafactory:(...)
    Method arguments:
      #128 (Ljava/lang/Object;)V
      #129 REF_invokeVirtual net/minecraft/resources/RegistryLoadTask.lambda$registerElements$1:(Lnet/minecraft/resources/RegistryLoadTask$PendingRegistration;Ljava/lang/Object;)V
      #130 (Ljava/lang/Object;)V
  2: #120 REF_invokeStatic java/lang/invoke/LambdaMetafactory.metafactory:(...)
    Method arguments:
      #128 (Ljava/lang/Object;)V
      #129 REF_invokeVirtual net/minecraft/resources/RegistryLoadTask.lambda$registerElements$2:(Lnet/minecraft/resources/RegistryLoadTask$PendingRegistration;Ljava/lang/Exception;)V
      #130 (Ljava/lang/Object;)V
InnerClasses:
  public static final #200= #201 of #202;
"""


def jar_bytes(missing: str | None = None) -> bytes:
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as archive:
        for class_name, _ in probe.ROOTS:
            if class_name == missing:
                continue
            archive.writestr(class_name.replace(".", "/") + ".class", BYTECODE)
    return buffer.getvalue()


def fake_javap(args: list[str], **kwargs: object) -> subprocess.CompletedProcess:
    del kwargs
    if args[-1] == "net.minecraft.resources.RegistryLoadTask":
        return subprocess.CompletedProcess(args, 0, registration_consumer_fixture(), "")
    return subprocess.CompletedProcess(args, 0, verbose_fixture(args[-1]), "")


class ClientLambdaBootstrapFrontierTests(unittest.TestCase):
    def test_each_exact_method_links_to_its_bootstrap_method_handle(self) -> None:
        for class_name, _ in probe.ROOTS:
            if class_name == "net.minecraft.resources.RegistryLoadTask":
                with self.subTest(class_name=class_name):
                    [consumer, callback] = probe.inspect_verbose(
                        registration_consumer_fixture(), class_name
                    )
                    self.assertEqual(consumer["method_name"], "registerElements")
                    self.assertEqual(callback["method_name"], "lambda$registerElements$0")
                    self.assertEqual(
                        [e["impl_handle_target_candidate"].split(":")[0].split(".")[-1]
                         for e in callback["bootstrap_method_handle_links_candidate"]],
                        ["lambda$registerElements$1", "lambda$registerElements$2"],
                    )
                    [edge] = consumer["bootstrap_method_handle_links_candidate"]
                    self.assertEqual(edge["bootstrap_index"], 0)
                    self.assertEqual(edge["bytecode_offset"], 1)
                    self.assertIn("RegistryLoadTask.lambda$registerElements$0:",
                                  edge["impl_handle_target_candidate"])
                continue
            with self.subTest(class_name=class_name):
                result = probe.inspect_verbose(verbose_fixture(class_name), class_name)
                self.assertEqual(len(result), 2)
                self.assertEqual(result[0]["method_name"], HANDLES[class_name][0])
                [link] = result[0]["bootstrap_method_handle_links_candidate"]
                self.assertEqual(link["bytecode_offset"], 1)
                self.assertEqual(link["bootstrap_index"], 0)
                self.assertEqual(link["impl_handle_kind"], "REF_invokeStatic")
                self.assertEqual(link["impl_handle_sha256"],
                                 hashlib.sha256(
                                     (HANDLES[class_name][2] +
                                      "(Ljava/lang/Object;)Ljava/lang/Object;").encode()
                                 ).hexdigest())
                [secondary] = result[1]["bootstrap_method_handle_links_candidate"]
                self.assertEqual(secondary["impl_handle_kind"], "REF_invokeVirtual")
                self.assertIn("CompletableFuture.join",
                              secondary["impl_handle_target_candidate"])

    def test_register_delegate_opcode_skeletons_are_bounded_and_exact(self) -> None:
        src = registration_consumer_fixture()
        rows = probe.bounded_registration_callback_opcodes(src)
        self.assertEqual([r["handler"] for r in rows], [
            "lambda$registerElements$0",
            "lambda$registerElements$1",
            "lambda$registerElements$2",
        ])
        self.assertEqual(
            [[x["offset"] for x in r["source_free_opcode_offsets"]] for r in rows],
            [[0, 1, 4, 5, 6, 11, 14, 15, 16, 21, 24, 25],
             [0, 1, 4, 5, 8, 9, 10, 13, 18, 19],
             [0, 1, 4, 5, 8, 9, 14, 15]],
        )
        self.assertEqual([r["bounded_instruction_count"] for r in rows], [12, 10, 8])
        probe.require_registration_callback_operands(rows)
        self.assertEqual(
            [len(r["bounded_field_refs"]) for r in rows], [1, 3, 2]
        )
        from copy import deepcopy
        wrong_receiver = deepcopy(rows)
        wrong_receiver[1]["bounded_field_refs"][0]["field"] = "errors:Ljava/util/Map;"
        with self.assertRaisesRegex(ValueError, "captured field identity"):
            probe.require_registration_callback_operands(wrong_receiver)
        different_source = deepcopy(rows)
        different_source[0]["source_free_opcode_offsets"][0]["opcode"] = "aload_0"
        with self.assertRaisesRegex(ValueError, "operand opcode path"):
            probe.require_registration_callback_operands(different_source)
        wrong_name = src.replace("lambda$registerElements$2(", "wrongCallback(", 1)
        with self.assertRaisesRegex(ValueError, "ambiguous registration callback"):
            probe.bounded_registration_callback_opcodes(wrong_name)
        malformed = src.replace("13: invokeinterface", "0: invokeinterface")
        with self.assertRaisesRegex(ValueError, "strictly increasing"):
            probe.bounded_registration_callback_opcodes(malformed)
        no_return = src.replace("25: return", "25: nop")
        with self.assertRaisesRegex(ValueError, "trailing return"):
            probe.bounded_registration_callback_opcodes(no_return)

    def test_register_delegate_requires_success_and_error_separation(self) -> None:
        from copy import deepcopy
        with tempfile.TemporaryDirectory() as tmp:
            jar = Path(tmp) / "client.jar"
            jar.write_bytes(jar_bytes())
            with patch.object(probe.subprocess, "run", side_effect=fake_javap):
                [item] = [x for x in probe.inspect_client(jar)
                          if x["class_name"] == "net.minecraft.resources.RegistryLoadTask"]
        callbacks = item["register_consumer_delegate_invocations_candidate"]
        for index in (0, 1, 2):
            modified = deepcopy(callbacks)
            modified[index]["invocations"][0]["bytecode_offset"] += 1
            with self.subTest(index=index), self.assertRaisesRegex(ValueError, "call changed"):
                probe.require_registration_delegate_sites(modified)
        wrong_side = deepcopy(callbacks)
        wrong_side[2]["invocations"][0]["symbolic_target"] = (
            "InterfaceMethod net/minecraft/core/WritableRegistry.register:()V"
        )
        with self.assertRaisesRegex(ValueError, "call changed"):
            probe.require_registration_delegate_sites(wrong_side)
        extra_registration = deepcopy(callbacks)
        extra_registration[2]["invocations"].append(
            extra_registration[1]["invocations"][0]
        )
        with self.assertRaisesRegex(ValueError, "call count drifted"):
            probe.require_registration_delegate_sites(extra_registration)

    def test_fail_closed_on_missing_bootstrap_or_non_lambda(self) -> None:
        name = "net.minecraft.util.Util"
        sample = verbose_fixture(name)
        with self.assertRaisesRegex(ValueError, "BootstrapMethods"):
            probe.inspect_verbose(sample.replace("BootstrapMethods:", "NotBootstrapMethods:"), name)
        with self.assertRaisesRegex(ValueError, "absent bootstrap"):
            probe.inspect_verbose(
                sample.replace("InvokeDynamic #0:apply:", "InvokeDynamic #20:apply:"), name
            )
        with self.assertRaisesRegex(ValueError, "non-lambda bootstrap"):
            probe.inspect_verbose(
                sample.replace("java/lang/invoke/LambdaMetafactory.metafactory",
                               "java/lang/invoke/StringConcatFactory.makeConcat"), name
            )
        with self.assertRaisesRegex(ValueError, "unique implementation handle"):
            probe.inspect_verbose(
                sample.replace("      #130 (Ljava/lang/Object;)Ljava/lang/Object;",
                               "      #130 REF_invokeStatic net/minecraft/util/Util.extra:()V", 1),
                name,
            )
        with self.assertRaisesRegex(ValueError, "missing/ambiguous rooted method"):
            probe.inspect_verbose(sample.replace(" sequence(", " replaced("), name)
        self.assertRaisesRegex(ValueError, "not an approved", probe.inspect_verbose, sample,
                               "net.minecraft.core.Unrelated")

    def test_exact_loader_factory_overload_selection(self) -> None:
        name = "net.minecraft.resources.RegistryDataLoader"
        data = verbose_fixture(name)
        unrelated = (
            "  public static void load(java.lang.String other);\n"
            "    Code:\n"
            "       0: invokedynamic #111,  0 // InvokeDynamic #0:apply:()Ljava/util/function/Function;\n"
        )
        result = probe.inspect_verbose(data.replace("  public static void irrelevant();",
                                                    unrelated + "  public static void irrelevant();"),
                                       name)
        self.assertEqual(result[0]["method_name"], "load")
        self.assertEqual(len(result[0]["bootstrap_method_handle_links_candidate"]), 1)
        with self.assertRaisesRegex(ValueError, "missing/ambiguous rooted method"):
            probe.inspect_verbose(
                data.replace("  public static void irrelevant();",
                             data.splitlines()[1] + "\n  public static void irrelevant();"), name
            )

    def test_full_archive_probe_makes_no_authority_claims(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            jar = Path(tmp) / "client.jar"
            jar.write_bytes(jar_bytes())
            with patch.object(probe.subprocess, "run", side_effect=fake_javap):
                records = probe.inspect_client(jar)
            self.assertEqual(len(records), 4)
            [consumer] = [r for r in records if
                          r["class_name"] == "net.minecraft.resources.RegistryLoadTask"]
            callbacks = consumer["register_consumer_delegate_invocations_candidate"]
            self.assertEqual(
                [callback["handler"] for callback in callbacks],
                ["lambda$registerElements$0", "lambda$registerElements$1",
                 "lambda$registerElements$2"],
            )
            self.assertEqual([len(callback["invocations"]) for callback in callbacks],
                             [4, 1, 1])
            self.assertTrue(consumer["success_error_dispatch_callsite_shapes_pinned"])
            self.assertFalse(consumer["full_register_or_error_semantics_proven"])
            self.assertNotIn("synthetic-class", json.dumps(records))
            self.assertNotIn("MappedRegistry.wrong", json.dumps(records))
            jar.write_bytes(jar_bytes("net.minecraft.util.Util"))
            with patch.object(probe.subprocess, "run", side_effect=fake_javap):
                with self.assertRaisesRegex(ValueError, "missing exact client class"):
                    probe.inspect_client(jar)
            jar.write_bytes(jar_bytes())
            client_meta = {"downloads": {"client": {
                "url": "https://example.invalid/client.jar",
                "sha1": "a" * 40, "size": len(jar_bytes())
            }}}
            def fake_download(url: str, path: Path, sha1: str, size: int) -> None:
                del url, sha1, size
                path.write_bytes(jar_bytes())
            with patch.object(probe.client_probe.official, "download",
                              side_effect=fake_download):
                with patch.object(probe.subprocess, "run", side_effect=fake_javap):
                    evidence = probe.discover(client_meta, Path(tmp))
            self.assertTrue(evidence["invokedynamic_bootstrap_resolution_inspected"])
            self.assertFalse(evidence["full_branch_and_error_semantics_reviewed"])
            self.assertFalse(evidence["client_numeric_id_assignment_proven"])
            self.assertFalse(evidence["source_var_sem_admitted"])
            self.assertFalse(evidence["production_admitted"])


if __name__ == "__main__":
    unittest.main()
