"""Fail-closed Play packet-number evidence reuse; no R2C source admission."""
from __future__ import annotations

import copy
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import r2c_play_id_law_reuse as binding


def reports() -> tuple[dict, dict]:
    client_sha1 = "b" * 40
    client_sha256 = "c" * 64
    methods = []
    for name, (count, digest, registered) in binding.PACKET_METHODS.items():
        is_clientbound = name == "lambda$static$2"
        methods.append({
            "method_name": name,
            "instruction_count": count,
            "all_instructions_sha256": digest,
            "candidate_complete_add_packet_registrations": registered,
            "no_conditional_builder_registration_observed": True,
            "first_registration_candidate": {
                "field": "CLIENTBOUND_BUNDLE" if is_clientbound
                         else "SERVERBOUND_TEST_0",
                "candidate_ordinal": 0,
                "bundle_registration": is_clientbound,
            },
        })
    play = {
        "schema": 1,
        "target": binding.TARGET.copy(),
        "source_archive_sha256": binding.SOURCE,
        "official_client_sha1": client_sha1,
        "official_client_sha256": client_sha256,
        "production_admitted": False,
        "protocol_registration_candidate": {
            "owner": "net.minecraft.network.protocol.game.GameProtocols",
            "complete_builder_argument_order_for_five_types_candidate":
                binding.NUMBERS.copy(),
            "numeric_packet_ids_admitted": False,
            "play_bundle_and_direction_law_admitted": False,
            "selected_registration_methods": methods,
        },
    }
    classes = []
    for class_name, digest in binding.BUILDER_CLASSES.items():
        classes.append({
            "class_name": class_name,
            "classfile_sha256": digest,
            "selected_methods": [
                {
                    "method_name": method,
                    "instruction_shape_sha256": fingerprint[0],
                    "instruction_count": fingerprint[1],
                }
                for (owner, method), fingerprint in binding.BUILDER_METHODS.items()
                if owner == class_name
            ],
        })
    # There really are overloaded decode/encode methods on the client.
    # Their presence must not overwrite the 42/54-instruction wire codec.
    classes[-1]["selected_methods"].extend([
        {
            "method_name": "decode",
            "instruction_shape_sha256": "f" * 64,
            "instruction_count": 5,
        },
        {
            "method_name": "encode",
            "instruction_shape_sha256": "e" * 64,
            "instruction_count": 6,
        },
    ])
    builder = {
        "schema": 1,
        "target": binding.TARGET.copy(),
        "pinned_source_archive_sha256": binding.SOURCE,
        "official_client_sha1": client_sha1,
        "official_client_sha256": client_sha256,
        "production_admitted": False,
        "independent_source_var_sem_admitted": False,
        "builder_append_to_numeric_id_law_proven": False,
        "builder_class_candidates": classes,
    }
    return play, builder


class ReviewedLawReuseTests(unittest.TestCase):
    def test_exact_consistent_client_and_reviewed_r0_id_law(self) -> None:
        play, builder = reports()
        item = binding.bind(play, builder)
        self.assertEqual(item["packet_numbers_candidate"], binding.NUMBERS)
        self.assertEqual(len(item["reviewed_r0_var_records_reused"]), 9)
        self.assertTrue(item["source_bound_packet_id_composition_consistent"])
        self.assertTrue(item["clientbound_bundle_counted_at_zero"])
        for name, value in item.items():
            if name.endswith("_admitted") or name.endswith("_passed"):
                self.assertIs(value, False, name)

    def test_stock_client_identity_order_bundle_and_dispatch_drift_reject(self) -> None:
        play, builder = reports()
        damaged = copy.deepcopy(play)
        damaged["official_client_sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "identity disagrees"):
            binding.bind(damaged, builder)
        damaged = copy.deepcopy(play)
        damaged["protocol_registration_candidate"][
            "complete_builder_argument_order_for_five_types_candidate"
        ]["SERVERBOUND_CHUNK_BATCH_RECEIVED"] = 12
        with self.assertRaisesRegex(ValueError, "divergent IDs"):
            binding.bind(damaged, builder)
        damaged = copy.deepcopy(play)
        damaged["protocol_registration_candidate"]["selected_registration_methods"][0][
            "first_registration_candidate"
        ]["bundle_registration"] = False
        with self.assertRaisesRegex(ValueError, "bundle must be registered"):
            binding.bind(damaged, builder)
        damaged = copy.deepcopy(play)
        damaged["protocol_registration_candidate"]["selected_registration_methods"][1][
            "first_registration_candidate"
        ]["bundle_registration"] = True
        with self.assertRaisesRegex(ValueError, "serverbound dispatch"):
            binding.bind(damaged, builder)
        damaged = copy.deepcopy(builder)
        damaged["builder_class_candidates"][0]["classfile_sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "class identity drift"):
            binding.bind(play, damaged)
        damaged = copy.deepcopy(builder)
        damaged["builder_class_candidates"][3]["selected_methods"][0][
            "instruction_shape_sha256"
        ] = "0" * 64
        with self.assertRaisesRegex(ValueError, "dispatch law drift"):
            binding.bind(play, damaged)

    def test_reused_var_sem_gate_is_not_merely_a_text_label(self) -> None:
        play, builder = reports()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            copies = [
                "vanilla/vanilla.lock.toml",
                "vanilla/gates/network/GATE-NET-STATUS-26_2-001.json",
                "vanilla/semantics/network/R0_STATUS_SEMANTICS.md",
                *[f"vanilla/records/network/r0/{record}.json"
                  for record in binding.REUSE],
            ]
            for name in copies:
                target = root / name
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(binding.ROOT / name, target)
            self.assertTrue(
                binding.bind(play, builder, root)[
                    "source_bound_packet_id_composition_consistent"
                ]
            )
            record = next(iter(binding.REUSE))
            path = root / f"vanilla/records/network/r0/{record}.json"
            content = json.loads(path.read_text())
            content["status"] = "UNREVIEWED"
            path.write_text(json.dumps(content))
            with self.assertRaisesRegex(ValueError, "VAR / gate / SEM"):
                binding.bind(play, builder, root)
            shutil.copyfile(binding.ROOT / f"vanilla/records/network/r0/{record}.json", path)
            gate_file = root / "vanilla/gates/network/GATE-NET-STATUS-26_2-001.json"
            gate = json.loads(gate_file.read_text())
            gate["methods"] = [m for m in gate["methods"] if m["var_id"] != record]
            gate_file.write_text(json.dumps(gate))
            with self.assertRaisesRegex(ValueError, "missing exact reviewed"):
                binding.bind(play, builder, root)


if __name__ == "__main__":
    unittest.main()
