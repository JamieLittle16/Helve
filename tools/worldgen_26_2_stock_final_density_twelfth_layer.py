#!/usr/bin/env python3
"""Bounded original JVM 26.2 twelfth: one actual in-right MulOrAdd child.

Real eleventh Ap2(MIN) right operand was class-observed as MulOrAdd.
Read its original specificType, IEEE argument, one wrapped child's runtime
class and exactly ONE new original stock JVM IEEE child word per fixed point.
The old in-right parent is independently anchored to the immutable eleventh
five-only-new TSV. No original prior capture is replayed, and no source,
all-input operator law, NoiseChunk lifecycle, VAR/SEM or production admission.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import sqlite3
import struct
import subprocess
import sys
import tempfile
import urllib.error
from pathlib import Path

import official_state_data as official
import worldgen_26_2_stock_final_density_eleventh_layer as eleventh
import worldgen_26_2_stock_finaldensity_eleventh_layer_fixture as prior

JAVA_SOURCE = Path(__file__).resolve().parent / (
    "worldgen_java/HelveStockFinalDensityTwelfthLayer262.java"
)
KIND = "original_26_2_finaldensity_twelfth_inright_muloradd_child_unadmitted"
HEAD = "HELVE26_2_TWELFTH_SHAPE"
VALUE = "HELVE26_2_TWELFTH_VALUE"
END = "HELVE26_2_TWELFTH_END"
FAIL = "HELVE26_2_TWELFTH_FAILURE"
SHAPE_FIELDS = ("mul_enum_class", "mul_op", "mul_argument_bits", "mul_child_class")
NEW_FIELDS = ("mul_child_bits",)
OLD_FIELDS = ("old_in_right_bits",)
WORDS = NEW_FIELDS + OLD_FIELDS
GATES = tuple(eleventh.GATES) + (
    "twelfth_actual_inright_muloradd_record_qualified",
    "twelfth_all_input_muloradd_law_admitted",
)
CLASS = eleventh.tenth.ninth.eighth.CLASS
FINAL = eleventh.tenth.ninth.eighth.seventh.sixth.fifth.fourth.third.second.final
ROOT = eleventh.tenth.ninth.eighth.seventh.sixth.fifth.fourth.third.second.root


class TwelfthLayerError(ValueError):
    """The original twelfth 26.2 JVM source-owner evidence cannot be admitted."""


def finite_bits(word: str) -> bool:
    return eleventh.finite_bits(word)


def value(word: str) -> float:
    return struct.unpack(">d", bytes.fromhex(word[2:]))[0]


def bits(number: float) -> str:
    return "0x" + struct.pack(">d", number).hex()


def validate_shape(s: dict) -> None:
    if not isinstance(s, dict) or set(s) != set(SHAPE_FIELDS) | {"world_seed_bits"}:
        raise TwelfthLayerError("actual twelfth MulOrAdd source-owned record shape moved")
    if s["mul_enum_class"] != CLASS + "MulOrAdd$Type":
        raise TwelfthLayerError("actual original MulOrAdd enum declaring class moved")
    if s["mul_op"] not in ("ADD", "MUL"):
        raise TwelfthLayerError("actual original MulOrAdd operation moved")
    argument = s["mul_argument_bits"]
    if (not isinstance(argument, str) or not argument.startswith("0x")
            or not finite_bits(argument[2:])):
        raise TwelfthLayerError("real source coefficient is not finite IEEE")
    eleventh.tenth.ninth.eighth.seventh.sixth.fifth.fourth.third.second.require_class(
        s["mul_child_class"]
    )


def candidate_telemetry(shapes: list[dict], vectors: list[dict]) -> dict:
    """Only arithmetic candidate evidence; mismatches do NOT censor JVM data."""
    mismatches = []
    for i, vector in enumerate(vectors):
        shape = shapes[i // 32]
        x = value(vector["mul_child_bits"])
        c = value(shape["mul_argument_bits"])
        try:
            guess = x + c if shape["mul_op"] == "ADD" else x * c
            same = math.isfinite(guess) and bits(guess) == vector["old_in_right_bits"]
        except (OverflowError, ValueError):
            same = False
        if not same:
            mismatches.append(i)
    return {
        "original_bounded_points": len(vectors),
        "direct_arithmetic_candidate_mismatches": len(mismatches),
        "direct_arithmetic_first_mismatch_index": mismatches[0] if mismatches else -1,
        "source_law_admitted": False,
    }


def parse_output(stdout: str) -> tuple[list[dict], list[dict]]:
    if not isinstance(stdout, str) or len(stdout) > 100000:
        raise TwelfthLayerError("unbounded twelfth original JVM output")
    frames = [parts for line in stdout.splitlines()
              if (parts := line.split("|"))[0] in (HEAD, VALUE, END, FAIL)]
    if any(frame[0] == FAIL for frame in frames):
        raise TwelfthLayerError("original bounded twelfth JVM source reflection failed")
    old = prior.load()
    points = FINAL.input_rows()
    shapes: list[dict] = []
    vectors: list[dict] = []
    cursor = 0
    for group, seed in enumerate(FINAL.SEEDS):
        if cursor >= len(frames):
            raise TwelfthLayerError("missing bounded source-owner twelfth seed shape")
        header = frames[cursor]
        cursor += 1
        if len(header) != 3 + len(SHAPE_FIELDS) or header[:3] != [HEAD, str(group), seed]:
            raise TwelfthLayerError("actual original twelfth seed shape header drift")
        shape = dict(zip(SHAPE_FIELDS, header[3:], strict=True))
        shape["mul_argument_bits"] = "0x" + shape["mul_argument_bits"]
        shape["world_seed_bits"] = seed
        validate_shape(shape)
        shapes.append(shape)
        for j in range(32):
            index = group * 32 + j
            if cursor >= len(frames):
                raise TwelfthLayerError("missing twelfth original fixed XYZ point")
            record = frames[cursor]
            cursor += 1
            if (len(record) != 2 + len(WORDS)
                    or record[:2] != [VALUE, str(index)]
                    or not all(finite_bits(word) for word in record[2:])):
                raise TwelfthLayerError("twelfth genuine finite IEEE point frame invalid")
            actual = dict(zip(WORDS, ("0x" + w for w in record[2:]), strict=True))
            if actual["old_in_right_bits"][2:] != old[index][2]:
                raise TwelfthLayerError(
                    "immutable independently frozen eleventh in-right parent drift: "
                    + str(index)
                )
            vectors.append({**points[index], **actual})
        if cursor >= len(frames) or frames[cursor] != [END, str(group), "32"]:
            raise TwelfthLayerError("actual original twelfth 32-point seed terminator moved")
        cursor += 1
    if cursor != len(frames):
        raise TwelfthLayerError("twelfth original JVM emitted extra record frames")
    if any(
        {k: v for k, v in s.items() if k != "world_seed_bits"}
        != {k: v for k, v in shapes[0].items() if k != "world_seed_bits"}
        for s in shapes[1:]
    ):
        raise TwelfthLayerError("real MulOrAdd record changed across four seeds")
    return shapes, vectors


def validate(report: dict) -> None:
    if not isinstance(report, dict):
        raise TwelfthLayerError("original twelfth report must be JSON object")
    pins = {
        "schema": 1, "kind": KIND, "minecraft": "26.2",
        "protocol": 776, "data_version": 4903,
        "source_archive_sha256": FINAL.frozen.SOURCE_SHA256,
        "official_server_sha256": FINAL.frozen.SERVER_SHA256,
        "prior_eleventh_fixture_sha256": prior.SHA256,
        "prior_eleventh_report_sha256": prior.REPORT_SHA256,
        "source_methods": report.get("source_methods"),
        "world_seeds": list(FINAL.SEEDS),
        "point_count_per_seed": 32,
        "sample_context": "DensityFunction$SinglePointContext",
        "original_stock_registry_used": True,
        "new_twelfth_inright_direct_child_observed": True,
        "source_text_included": False,
        "arithmetic_candidate_telemetry": report.get("arithmetic_candidate_telemetry"),
        **{gate: False for gate in GATES},
    }
    if set(report) != set(pins) | {"shapes", "vectors"} or any(
        type(report.get(k)) is not type(v) or report[k] != v
        for k, v in pins.items()
    ):
        raise TwelfthLayerError("original twelfth provenance/source/admission drift")
    methods = report["source_methods"]
    if not isinstance(methods, dict) or set(methods) != {
        "ap2_compute", "holder_holder_compute", "mapped_delegate_compute"
    }:
        raise TwelfthLayerError("twelfth original source method inventory changed")
    for name in ("ap2_compute", "holder_holder_compute"):
        owner = methods[name]
        if (not isinstance(owner, dict)
                or owner.get("reviewed") is not False
                or tuple(owner.get(k) for k in (
                    "owner", "signature", "body_sha256", "normalized_sha256"
                )) != ROOT.frozen_final.METHODS[name]):
            raise TwelfthLayerError("original indexed Java source method SHA moved")
    mapped = methods["mapped_delegate_compute"]
    if (not isinstance(mapped, dict)
            or mapped.get("reviewed") is not False
            or mapped.get("owner") != ROOT.PURE_TRANSFORMER
            or mapped.get("body_sha256") != ROOT.PURE_COMPUTE_SHA256):
        raise TwelfthLayerError("actual mapped delegate source provenance moved")
    shapes, vectors = report.get("shapes"), report.get("vectors")
    if (not isinstance(shapes, list) or len(shapes) != 4
            or not isinstance(vectors, list) or len(vectors) != 128):
        raise TwelfthLayerError("twelfth actual 4x32 finite capture size moved")
    points = FINAL.input_rows()
    replay = []
    for group, shape in enumerate(shapes):
        validate_shape(shape)
        replay.append("|".join((
            HEAD, str(group), shape["world_seed_bits"],
            *(shape[k][2:] if k == "mul_argument_bits" else str(shape[k])
              for k in SHAPE_FIELDS)
        )))
        for j in range(32):
            i = group * 32 + j
            v = vectors[i]
            if (not isinstance(v, dict)
                    or set(v) != set(points[i]) | set(WORDS)
                    or any(v.get(k) != p for k, p in points[i].items())):
                raise TwelfthLayerError("twelfth original XYZ/seed or field set altered")
            replay.append("|".join((VALUE, str(i), *(v[k][2:] for k in WORDS))))
        replay.append("|".join((END, str(group), "32")))
    candidate = candidate_telemetry(shapes, vectors)
    if (type(report["arithmetic_candidate_telemetry"]) is not dict
            or report["arithmetic_candidate_telemetry"] != candidate):
        raise TwelfthLayerError("twelfth sample-only candidate telemetry tampered")
    if parse_output("\n".join(replay)) != (shapes, vectors):
        raise TwelfthLayerError("twelfth source-free real record round-trip failed")


def observe(server: Path, timeout: int = 240) -> tuple[list[dict], list[dict]]:
    with tempfile.TemporaryDirectory(prefix="helve-26_2-twelfth-layer-") as td:
        work = Path(td)
        jars = official.extract_classpath(server, work / "classpath")
        f = eleventh.tenth.ninth.eighth.seventh.sixth.fifth
        sources = (
            f.fourth.third.second.final.roots.BASE_BRIDGE,
            f.fourth.third.second.final.JAVA_SOURCE,
            f.fourth.third.second.root.JAVA_SOURCE,
            f.fourth.third.second.inner.JAVA_SOURCE,
            f.fourth.third.second.JAVA_SOURCE,
            f.fourth.third.JAVA_SOURCE,
            f.fourth.JAVA_SOURCE,
            f.JAVA_SOURCE,
            eleventh.tenth.ninth.eighth.seventh.sixth.JAVA_SOURCE,
            eleventh.tenth.ninth.eighth.seventh.JAVA_SOURCE,
            eleventh.tenth.ninth.eighth.JAVA_SOURCE,
            eleventh.tenth.ninth.JAVA_SOURCE,
            eleventh.tenth.JAVA_SOURCE,
            eleventh.JAVA_SOURCE,
            JAVA_SOURCE,
        )
        if any(not path.is_file() for path in sources):
            raise TwelfthLayerError("missing original source-free twelfth bridge")
        build = subprocess.run(
            ["javac", "-encoding", "UTF-8", "-d", str(work),
             *(str(path) for path in sources)],
            capture_output=True, text=True, timeout=timeout, check=False
        )
        if build.returncode:
            raise TwelfthLayerError("twelfth bounded javac failed: " + build.stderr[:480])
        proc = subprocess.run(
            ["java", "-Xmx768m", "-cp",
             os.pathsep.join((str(work), *(str(jar) for jar in jars))),
             "HelveStockFinalDensityTwelfthLayer262", "--twelfth-layer-128"],
            input="\n".join(
                f"{p['world_seed_bits']}\t{p['block_x']}\t{p['block_y']}\t{p['block_z']}"
                for p in FINAL.input_rows()
            ) + "\n",
            capture_output=True, text=True, timeout=timeout, check=False,
        )
        if proc.returncode:
            reason = next(
                (line for line in proc.stdout.splitlines() if line.startswith(FAIL)),
                "no bounded original twelfth failure tag"
            )
            raise TwelfthLayerError("real original twelfth JVM failure: " + reason[:160])
        return parse_output(proc.stdout)


def capture(*, source: Path, db: Path, lock: Path,
            server: Path, output: Path) -> dict:
    dest = FINAL.improved.external_output(output)
    source_sha, server_sha, methods = (
        eleventh.tenth.ninth.eighth.seventh.sixth.fifth.fourth.third.second.inner
        .source_provenance(source, db, lock, server)
    )
    shapes, vectors = observe(server)
    report = {
        "schema": 1, "kind": KIND, "minecraft": "26.2",
        "protocol": 776, "data_version": 4903,
        "source_archive_sha256": source_sha,
        "official_server_sha256": server_sha,
        "prior_eleventh_fixture_sha256": prior.SHA256,
        "prior_eleventh_report_sha256": prior.REPORT_SHA256,
        "source_methods": methods,
        "world_seeds": list(FINAL.SEEDS),
        "point_count_per_seed": 32,
        "sample_context": "DensityFunction$SinglePointContext",
        "original_stock_registry_used": True,
        "new_twelfth_inright_direct_child_observed": True,
        "source_text_included": False,
        "shapes": shapes, "vectors": vectors,
        "arithmetic_candidate_telemetry": candidate_telemetry(shapes, vectors),
        **{gate: False for gate in GATES},
    }
    validate(report)
    payload = (json.dumps(report, indent=2, sort_keys=True) + "\n").encode("ascii")
    if len(payload) > 115000:
        raise TwelfthLayerError("unbounded twelfth source-free report payload")
    dest.parent.mkdir(parents=True, exist_ok=True)
    with os.fdopen(os.open(dest, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600), "wb") as fp:
        fp.write(payload)
    return {
        "output": str(dest),
        "sha256": hashlib.sha256(payload).hexdigest(),
        "genuinely_new_twelfth_ieee_words": len(vectors),
        "old_eleventh_inright_parent_words_anchored": len(vectors),
        "original_muloradd_op": shapes[0]["mul_op"],
        "original_muloradd_arg_bits": shapes[0]["mul_argument_bits"],
        "original_child_class": shapes[0]["mul_child_class"],
        "arithmetic_candidate_telemetry": candidate_telemetry(shapes, vectors),
        **{gate: False for gate in GATES},
    }


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--source", type=Path, default=FINAL.primitive.SOURCE)
    p.add_argument("--db", type=Path, default=FINAL.primitive.DB)
    p.add_argument("--lock", type=Path, default=FINAL.primitive.LOCK)
    p.add_argument("--cache", type=Path, default=FINAL.primitive.CACHE)
    p.add_argument("--server-jar", type=Path)
    p.add_argument("--output", type=Path, required=True)
    args = p.parse_args(argv)
    try:
        server = args.server_jar
        if server is None:
            meta, _ = official.resolve("26.2", args.cache)
            server = meta["server"][0]
        print(json.dumps(capture(
            source=args.source, db=args.db, lock=args.lock,
            server=server, output=args.output
        ), sort_keys=True))
    except (
        TwelfthLayerError, ValueError, TypeError, KeyError, IndexError, OSError,
        sqlite3.Error, subprocess.TimeoutExpired, urllib.error.URLError
    ) as exc:
        print("STOCK 26.2 TWELFTH LAYER OPEN: " + str(exc), file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
