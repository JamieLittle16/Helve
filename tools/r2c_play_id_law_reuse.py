#!/usr/bin/env python3
"""Compose *existing* R0 reviewed packet-ID law with two exact R2C client witnesses.

No source parser, runtime registry, new wire implementation, or production gate
is created here. The independent R0 VAR/SEM gate remains authoritative for the
generic append -> ID law; this COLD consistency check cannot admit the R2C
Play lifecycle, selected Configuration or heightmap source semantics.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TARGET = {"minecraft": "26.2", "protocol": 776, "data_version": 4903}
SOURCE = "1e9bca3dff83cd83e7905f8810f1ec9899361fa2dc83fe893bb48beeb04df750"
NUMBERS = {
    "CLIENTBOUND_CHUNK_BATCH_FINISHED": 11,
    "CLIENTBOUND_CHUNK_BATCH_START": 12,
    "CLIENTBOUND_LEVEL_CHUNK_WITH_LIGHT": 45,
    "CLIENTBOUND_SET_CHUNK_CACHE_CENTER": 94,
    "SERVERBOUND_CHUNK_BATCH_RECEIVED": 11,
}
PACKET_METHODS = {
    "lambda$static$2": (429, "83b3c511b46a3575a4fbf0779ee145b01519404f5516ac83cb2aefdd13a81b21", 141),
    "lambda$static$1": (211, "e317857a535331f9aa6a6827ed55d67fa2b723103400d45d9ad48dc60b54122a", 13),
}
# Required, already reviewed and independently gate-bound generic source
# contracts; none is an invented new R2C VAR or SEM decision.
REUSE = {
    "VAR-NET-R0-PROTOCOL-BUILDER-ADD-001": "SEM-NET-R0-014",
    "VAR-NET-R0-PROTOCOL-BUILDER-CODEC-001": "SEM-NET-R0-014",
    "VAR-NET-R0-PROTOCOL-BUILDER-ENTRY-001": "SEM-NET-R0-014",
    "VAR-NET-R0-PROTOCOL-CODEC-ADD-001": "SEM-NET-R0-015",
    "VAR-NET-R0-PROTOCOL-CODEC-BUILD-001": "SEM-NET-R0-015",
    "VAR-NET-R0-ID-DISPATCH-BUILDER-ADD-001": "SEM-NET-R0-015",
    "VAR-NET-R0-ID-DISPATCH-BUILDER-BUILD-001": "SEM-NET-R0-015",
    "VAR-NET-R0-ID-DISPATCH-DECODE-001": "SEM-NET-R0-015",
    "VAR-NET-R0-ID-DISPATCH-ENCODE-001": "SEM-NET-R0-015",
}
BUILDER_METHODS = {
    ("net.minecraft.network.protocol.ProtocolInfoBuilder", "withBundlePacket"):
        ("01a8b43ca46c5e92a17c40aaff795558fe63820bbf55750a862723d52caf41fe", 24),
    ("net.minecraft.network.protocol.ProtocolInfoBuilder", "buildPacketCodec"):
        ("39caa1a45b1bb0212ef922b1700fad0a92661e5cb130baf8fdd59f56e50bfeb4", 25),
    ("net.minecraft.network.protocol.ProtocolInfoBuilder$CodecEntry", "addToBuilder"):
        ("69488d19803f37955aac584fbbfd236631b05a10b17b9188efb375ca0d982593", 25),
    ("net.minecraft.network.protocol.ProtocolCodecBuilder", "add"):
        ("ede86bfae070b2bac3b2ac53a8885648d44a995cd3c2c68fcec91afb1e3014ff", 23),
    ("net.minecraft.network.codec.IdDispatchCodec$Builder", "add"):
        ("ee260d95f5e0bbe233fa4875ef4c40c8d91a20dfa007474a08e0158237308c83", 11),
    ("net.minecraft.network.codec.IdDispatchCodec$Builder", "build"):
        ("e20ada392294df45f305e29cef91f8a4f143cee33f7f05631f92817df0852fbc", 49),
    ("net.minecraft.network.codec.IdDispatchCodec", "decode"):
        ("8749bdfc2418e725da921046cda9b5a50bf8486a9621bcd934e05882e9986938", 42),
    ("net.minecraft.network.codec.IdDispatchCodec", "encode"):
        ("efe32a2a267cf7eb1cd25737f35534f4ae9cc2026a121e35d0a243ef88f4a8ea", 54),
}
BUILDER_CLASSES = {
    "net.minecraft.network.protocol.ProtocolInfoBuilder":
        "7af68e5a84feaa5c7b4f2c6bff09e8ee2b8f679256624419428c774cf88e8bde",
    "net.minecraft.network.protocol.ProtocolCodecBuilder":
        "bd344893e334305216765d20497912600db813229cb4adadc90f549e374c7cd3",
    "net.minecraft.network.codec.IdDispatchCodec$Builder":
        "fc0a71b133aea8f0e7e0abc7a263b049158de2dab4cf09f0ca76c0d0e41d608a",
    "net.minecraft.network.codec.IdDispatchCodec":
        "0055112127f7f55a79601906ed1267569ec6fe8c511a409ee57c3cd5b35c4f74",
}
SHA256 = re.compile(r"[0-9a-f]{64}\Z")


def require(predicate: bool, reason: str) -> None:
    if not predicate:
        raise ValueError(reason)


def bind(play: dict, builder: dict, root: Path = ROOT) -> dict:
    """Check identity and consistency only. Fresh Atlas source gate is separate."""
    with (root / "vanilla/vanilla.lock.toml").open("rb") as stream:
        lock = tomllib.load(stream)
    require(
        (lock.get("minecraft"), lock.get("protocol"), lock.get("data_version")) ==
        ("26.2", 776, 4903) and lock["source"]["archive_sha256"] == SOURCE,
        "official source/target lock drift",
    )
    for name, report in (("Play", play), ("builder", builder)):
        require(report.get("schema") == 1 and report.get("target") == TARGET,
                f"{name} target drift")
        require(report.get("official_client_sha1") == play.get("official_client_sha1")
                and report.get("official_client_sha256") == play.get("official_client_sha256")
                and SHA256.fullmatch(str(report.get("official_client_sha256"))) is not None,
                f"{name} official client identity disagrees")
        source_field = ("source_archive_sha256" if name == "Play"
                        else "pinned_source_archive_sha256")
        require(report.get(source_field) == SOURCE, f"{name} source corpus mismatch")
        require(report.get("production_admitted") is False,
                f"{name} cannot claim production admission")

    pg = play["protocol_registration_candidate"]
    require(pg.get("owner") == "net.minecraft.network.protocol.game.GameProtocols"
            and pg.get("complete_builder_argument_order_for_five_types_candidate") == NUMBERS
            and pg.get("numeric_packet_ids_admitted") is False
            and pg.get("play_bundle_and_direction_law_admitted") is False,
            "Play register probe is missing/unadmitted or has divergent IDs")
    methods = {m["method_name"]: m for m in pg["selected_registration_methods"]}
    require(set(methods) == set(PACKET_METHODS),
            "Play packet registration method set drift")
    for name, (count, digest, registrations) in PACKET_METHODS.items():
        item = methods[name]
        require((item["instruction_count"], item["all_instructions_sha256"],
                 item["candidate_complete_add_packet_registrations"]) ==
                (count, digest, registrations),
                f"pinned Play registration method drift: {name}: "
                f"observed={(item['instruction_count'], item['all_instructions_sha256'], item['candidate_complete_add_packet_registrations'])!r}")
        require(item["no_conditional_builder_registration_observed"] is True,
                f"conditional Play builder: {name}")
    # The clientbound bundle is a *counted* packet at ordinal zero,
    # not an offset subtracted after numeric assignment.
    first = methods["lambda$static$2"].get("first_registration_candidate")
    require(first is not None and first.get("field") == "CLIENTBOUND_BUNDLE"
            and first.get("candidate_ordinal") == 0
            and first.get("bundle_registration") is True,
            "clientbound bundle must be registered at ordinal zero")
    first_serverbound = methods["lambda$static$1"].get("first_registration_candidate")
    require(first_serverbound is not None
            and first_serverbound.get("bundle_registration") is False,
            "serverbound dispatch cannot inherit clientbound bundle")

    require(builder.get("independent_source_var_sem_admitted") is False
            and builder.get("builder_append_to_numeric_id_law_proven") is False,
            "builder probe has invented admission authority")
    class_hashes = {
        cls["class_name"]: cls["classfile_sha256"]
        for cls in builder["builder_class_candidates"]
    }
    for class_name, digest in BUILDER_CLASSES.items():
        require(class_hashes.get(class_name) == digest,
                f"official client builder class identity drift: {class_name}")
    observed = {}
    for cls in builder["builder_class_candidates"]:
        for method in cls["selected_methods"]:
            key = cls["class_name"], method["method_name"]
            observed.setdefault(key, set()).add(
                (method["instruction_shape_sha256"], method["instruction_count"])
            )
    for method, fingerprint in BUILDER_METHODS.items():
        require(fingerprint in observed.get(method, set()),
                f"downstream client append/dispatch law drift: {method}")
    # Do not silently adopt some extra / missing R0 source record. Verify
    # both its explicit independent gate membership and its SEM link.
    gate = json.loads((root / "vanilla/gates/network/GATE-NET-STATUS-26_2-001.json").read_text())
    require(gate.get("frontier") == "r0-status"
            and gate.get("minimum_status") == "VAR_REVIEWED"
            and gate.get("require_semantic_rules") is True
            and gate.get("require_hazards_reviewed") is True,
            "reviewed R0 source-gate requirements drift")
    declared = {item["var_id"]: item["query"] for item in gate["methods"]}
    semantics = (root / "vanilla/semantics/network/R0_STATUS_SEMANTICS.md").read_text()
    for record_id, sem in REUSE.items():
        require(record_id in declared and sem in semantics,
                f"missing exact reviewed R0 packet source law: {record_id}")
        record = json.loads(
            (root / f"vanilla/records/network/r0/{record_id}.json").read_text()
        )
        source = record["source"]
        require(record.get("schema") == 1 and record.get("id") == record_id
                and record.get("status") == "VAR_REVIEWED"
                and source.get("fingerprint_algorithm") == "java-token-v2-literal-sensitive"
                and all(SHA256.fullmatch(str(source.get(f))) for f in
                        ("body_sha256", "normalized_sha256"))
                and sem in record.get("semantic_rules", [])
                and declared[record_id] == source["type"] + "#" + source["signature"],
                f"reviewed R0 VAR / gate / SEM disagreement: {record_id}")

    return {
        "schema": 1,
        "kind": "r2c-26_2-client-play-packet-id-reviewed-law-reuse-v1",
        "target": TARGET,
        "source_archive_sha256": SOURCE,
        "official_client_sha1": play["official_client_sha1"],
        "official_client_sha256": play["official_client_sha256"],
        "packet_numbers_candidate": NUMBERS,
        "reviewed_r0_var_records_reused": sorted(REUSE),
        "source_bound_packet_id_composition_consistent": True,
        "clientbound_bundle_counted_at_zero": True,
        "independent_r2c_atlas_source_gate_passed": False,
        "r2c_play_lifecycle_var_sem_admitted": False,
        "r2c_biome_var_sem_admitted": False,
        "r2c_heightmap_var_sem_admitted": False,
        "production_admitted": False,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--play", type=Path, required=True)
    ap.add_argument("--builder", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()
    try:
        if args.output.exists() or args.output.is_symlink():
            raise ValueError("source-binding output must be a new path")
        if args.output.resolve(strict=False).is_relative_to(ROOT):
            raise ValueError("source-binding evidence must stay outside repository")
        result = bind(json.loads(args.play.read_text()),
                      json.loads(args.builder.read_text()))
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, sort_keys=True, indent=2) + "\n")
    except (OSError, ValueError, KeyError, TypeError, tomllib.TOMLDecodeError) as exc:
        print(f"R2C Play reviewed-law source composition rejected: {exc}",
              file=sys.stderr)
        return 2
    print("Five exact Play packet positions agree with reviewed R0 ID law; "
          "R2C source/SEM and production admission remain FALSE")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
