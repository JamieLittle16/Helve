#!/usr/bin/env python3
"""Twentieth bounded original JVM source-owned RIGHT MulOrAdd child probe.

Follow the actual nineteenth Clamp-wrapped Ap2(ADD) RIGHT MulOrAdd.
Reflect the genuine MulOrAdd enum, scalar and wrapped child runtime class.
Observe ONE new wrapped-child IEEE value per fixed 4x32 stock point;
the OLD RIGHT MulOrAdd parent is pinned to the immutable nineteenth
two-new-child fixture. Do not admit all-input/cache/NoiseChunk/production law.
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
import worldgen_26_2_stock_final_density_nineteenth_layer as nineteenth
import worldgen_26_2_stock_finaldensity_nineteenth_layer_fixture as prior

JAVA_SOURCE = Path(__file__).resolve().parent / (
    "worldgen_java/HelveStockFinalDensityTwentiethLayer262.java"
)
KIND = "original_26_2_finaldensity_twentieth_actual_nineteenth_right_muloradd_child_unadmitted"
HEAD = "HELVE26_2_TWENTIETH_SHAPE"
VALUE = "HELVE26_2_TWENTIETH_VALUE"
END = "HELVE26_2_TWENTIETH_END"
FAIL = "HELVE26_2_TWENTIETH_FAILURE"
SHAPE_FIELDS = (
    "muloradd_enum_class", "muloradd_op",
    "muloradd_argument_bits", "muloradd_child_class",
)
NEW_FIELDS = ("muloradd_inner_bits",)
OLD_FIELDS = ("old_nineteenth_right_bits",)
WORDS = NEW_FIELDS + OLD_FIELDS
GATES = tuple(nineteenth.GATES) + (
    "twentieth_actual_muloradd_child_qualified",
    "twentieth_all_input_muloradd_law_admitted",
)
CLASS = nineteenth.CLASS
FINAL = nineteenth.FINAL
ROOT = nineteenth.ROOT


class TwentiethLayerError(ValueError):
    """Actual original twentieth source shape, ancestry or frame drift."""


def finite_bits(word: str) -> bool:
    return nineteenth.finite_bits(word)


def value(word: str) -> float:
    return struct.unpack(">d", bytes.fromhex(word[2:]))[0]


def bits(number: float) -> str:
    return "0x" + struct.pack(">d", number).hex()


def validate_shape(shape: dict) -> None:
    if not isinstance(shape, dict) or set(shape) != set(SHAPE_FIELDS) | {"world_seed_bits"}:
        raise TwentiethLayerError("source-owned twentieth MulOrAdd shape fields moved")
    if shape["muloradd_enum_class"] != CLASS + "MulOrAdd$Type":
        raise TwentiethLayerError("real twentieth MulOrAdd enum class moved")
    if shape["muloradd_op"] not in ("ADD", "MUL"):
        raise TwentiethLayerError("source-owned twentieth MulOrAdd op malformed")
    raw = shape["muloradd_argument_bits"]
    if not isinstance(raw, str) or len(raw) != 16 or not finite_bits("0x" + raw):
        raise TwentiethLayerError("twentieth actual MulOrAdd scalar IEEE nonfinite/malformed")
    try:
        nineteenth.eighteenth.seventeenth.sixteenth.fifteenth.fourteenth.thirteenth.twelfth.eleventh.tenth.ninth.eighth.seventh.sixth.fifth.fourth.third.second.require_class(
            shape["muloradd_child_class"]
        )
    except (ValueError, TypeError) as exc:
        raise TwentiethLayerError("twentieth wrapped original density class moved") from exc


def candidate_telemetry(shapes: list[dict], vectors: list[dict]) -> dict:
    """Finite bounded original candidates; never source all-input-law admission."""
    mismatches = []
    add_count = mul_count = 0
    for i, v in enumerate(vectors):
        shape = shapes[i // 32]
        scalar = value("0x" + shape["muloradd_argument_bits"])
        inner = value(v["muloradd_inner_bits"])
        if shape["muloradd_op"] == "ADD":
            add_count += 1
            guess = inner + scalar
        else:
            mul_count += 1
            guess = inner * scalar
        if not math.isfinite(guess) or bits(guess) != v["old_nineteenth_right_bits"]:
            mismatches.append(i)
    return {
        "original_bounded_points": len(vectors),
        "muloradd_candidate_mismatches": len(mismatches),
        "muloradd_candidate_first_mismatch_index": mismatches[0] if mismatches else -1,
        "observed_add_points": add_count,
        "observed_mul_points": mul_count,
        "source_law_admitted": False,
    }


def parse_output(stdout: str) -> tuple[list[dict], list[dict]]:
    if not isinstance(stdout, str) or len(stdout) > 100000:
        raise TwentiethLayerError("unbounded original twentieth JVM frame output")
    frames = [parts for line in stdout.splitlines()
              if (parts := line.split("|"))[0] in (HEAD, VALUE, END, FAIL)]
    if any(frame[0] == FAIL for frame in frames):
        raise TwentiethLayerError("bounded genuine twentieth JVM reflection failure")
    old = prior.load()
    points = FINAL.input_rows()
    shapes = []
    vectors = []
    cursor = 0
    for group, seed in enumerate(FINAL.SEEDS):
        if cursor >= len(frames):
            raise TwentiethLayerError("missing twentieth original seed shape")
        header = frames[cursor]
        cursor += 1
        if len(header) != 3 + len(SHAPE_FIELDS) or header[:3] != [HEAD, str(group), seed]:
            raise TwentiethLayerError("actual twentieth original seed header drift")
        shape = dict(zip(SHAPE_FIELDS, header[3:], strict=True))
        shape["world_seed_bits"] = seed
        validate_shape(shape)
        shapes.append(shape)
        for j in range(32):
            i = group * 32 + j
            if cursor >= len(frames):
                raise TwentiethLayerError("missing source-owned twentieth point")
            record = frames[cursor]
            cursor += 1
            if (len(record) != 2 + len(WORDS)
                    or record[:2] != [VALUE, str(i)]
                    or not all(finite_bits(word) for word in record[2:])):
                raise TwentiethLayerError("malformed original twentieth finite IEEE frame")
            actual = dict(zip(WORDS, ("0x" + word for word in record[2:]), strict=True))
            if actual["old_nineteenth_right_bits"][2:] != old[i][1]:
                raise TwentiethLayerError(
                    f"independently frozen nineteenth RIGHT original parent drift at {i}"
                )
            vectors.append({**points[i], **actual})
        if cursor >= len(frames) or frames[cursor] != [END, str(group), "32"]:
            raise TwentiethLayerError("twentieth original 32-point seed terminator moved")
        cursor += 1
    if cursor != len(frames):
        raise TwentiethLayerError("twentieth JVM emitted unexpected frames")
    if any(
        {k: v for k, v in shape.items() if k != "world_seed_bits"}
        != {k: v for k, v in shapes[0].items() if k != "world_seed_bits"}
        for shape in shapes[1:]
    ):
        raise TwentiethLayerError("original MulOrAdd source enum/parameter/child changed across seeds")
    return shapes, vectors


def validate(report: dict) -> None:
    if not isinstance(report, dict):
        raise TwentiethLayerError("original twentieth report must be JSON object")
    fixture = nineteenth.seventeenth_fixture
    pins = {
        "schema": 1, "kind": KIND, "minecraft": "26.2",
        "protocol": 776, "data_version": 4903,
        "source_archive_sha256": FINAL.frozen.SOURCE_SHA256,
        "official_server_sha256": FINAL.frozen.SERVER_SHA256,
        "prior_thirteenth_fixture_sha256": fixture.prior.prior.SHA256,
        "prior_sixteenth_fixture_sha256": fixture.prior.SHA256,
        "prior_seventeenth_fixture_sha256": fixture.SHA256,
        "prior_eighteenth_override_fixture_sha256": prior.prior.SHA256,
        "prior_nineteenth_fixture_sha256": prior.SHA256,
        "prior_thirteenth_report_sha256": fixture.prior.prior.REPORT_SHA256,
        "prior_fourteenth_report_sha256": fixture.prior.receipt.owner.previous.REPORT_SHA256,
        "prior_fifteenth_report_sha256": fixture.prior.receipt.REPORT_SHA256,
        "prior_sixteenth_report_sha256": fixture.prior.REPORT_SHA256,
        "prior_seventeenth_report_sha256": fixture.REPORT_SHA256,
        "prior_eighteenth_report_sha256": prior.prior.REPORT_SHA256,
        "prior_nineteenth_report_sha256": prior.REPORT_SHA256,
        "source_methods": report.get("source_methods"),
        "world_seeds": list(FINAL.SEEDS),
        "point_count_per_seed": 32,
        "sample_context": "DensityFunction$SinglePointContext",
        "original_stock_registry_used": True,
        "new_twentieth_actual_muloradd_child_observed": True,
        "source_text_included": False,
        "muloradd_candidate_telemetry": report.get("muloradd_candidate_telemetry"),
        **{gate: False for gate in GATES},
    }
    if set(report) != set(pins) | {"shapes", "vectors"} or any(
        type(report.get(k)) is not type(v) or report[k] != v for k, v in pins.items()
    ):
        raise TwentiethLayerError("original twentieth source provenance/gate report drift")
    methods = report["source_methods"]
    if not isinstance(methods, dict) or set(methods) != {
        "ap2_compute", "holder_holder_compute", "mapped_delegate_compute"
    }:
        raise TwentiethLayerError("original twentieth source method inventory changed")
    for name in ("ap2_compute", "holder_holder_compute"):
        method = methods[name]
        if (not isinstance(method, dict) or method.get("reviewed") is not False
                or tuple(method.get(k) for k in (
                    "owner", "signature", "body_sha256", "normalized_sha256"
                )) != ROOT.frozen_final.METHODS[name]):
            raise TwentiethLayerError("source-indexed Java method SHA drift")
    mapped = methods["mapped_delegate_compute"]
    if (not isinstance(mapped, dict)
            or mapped.get("reviewed") is not False
            or mapped.get("owner") != ROOT.PURE_TRANSFORMER
            or mapped.get("body_sha256") != ROOT.PURE_COMPUTE_SHA256):
        raise TwentiethLayerError("original mapped delegate method SHA drift")
    shapes, vectors = report.get("shapes"), report.get("vectors")
    if (not isinstance(shapes, list) or len(shapes) != 4
            or not isinstance(vectors, list) or len(vectors) != 128):
        raise TwentiethLayerError("twentieth original 4x32 shape/count drift")
    points = FINAL.input_rows()
    replay = []
    for group, shape in enumerate(shapes):
        validate_shape(shape)
        replay.append("|".join((HEAD, str(group), shape["world_seed_bits"],
                                *(str(shape[k]) for k in SHAPE_FIELDS))))
        for j in range(32):
            i = group * 32 + j
            row = vectors[i]
            if (not isinstance(row, dict)
                    or set(row) != set(points[i]) | set(WORDS)
                    or any(row.get(k) != val for k, val in points[i].items())):
                raise TwentiethLayerError("twentieth original seed/XYZ or field identity changed")
            replay.append("|".join((VALUE, str(i), *(row[k][2:] for k in WORDS))))
        replay.append("|".join((END, str(group), "32")))
    candidate = candidate_telemetry(shapes, vectors)
    if (type(report["muloradd_candidate_telemetry"]) is not dict
            or report["muloradd_candidate_telemetry"] != candidate):
        raise TwentiethLayerError("twentieth source-free finite arithmetic telemetry drift")
    if parse_output("\n".join(replay)) != (shapes, vectors):
        raise TwentiethLayerError("original twentieth source-free record replay failed")


def observe(server: Path, timeout: int = 240) -> tuple[list[dict], list[dict]]:
    with tempfile.TemporaryDirectory(prefix="helve-26_2-twentieth-layer-") as td:
        work = Path(td)
        jars = official.extract_classpath(server, work / "classpath")
        f = nineteenth.eighteenth.seventeenth.sixteenth.fifteenth.fourteenth.thirteenth.twelfth.eleventh.tenth.ninth.eighth.seventh.sixth.fifth
        sources = (
            f.fourth.third.second.final.roots.BASE_BRIDGE,
            f.fourth.third.second.final.JAVA_SOURCE,
            f.fourth.third.second.root.JAVA_SOURCE,
            f.fourth.third.second.inner.JAVA_SOURCE,
            f.fourth.third.second.JAVA_SOURCE,
            f.fourth.third.JAVA_SOURCE,
            f.fourth.JAVA_SOURCE,
            f.JAVA_SOURCE,
            nineteenth.eighteenth.seventeenth.sixteenth.fifteenth.fourteenth.thirteenth.twelfth.eleventh.tenth.ninth.eighth.seventh.sixth.JAVA_SOURCE,
            nineteenth.eighteenth.seventeenth.sixteenth.fifteenth.fourteenth.thirteenth.twelfth.eleventh.tenth.ninth.eighth.seventh.JAVA_SOURCE,
            nineteenth.eighteenth.seventeenth.sixteenth.fifteenth.fourteenth.thirteenth.twelfth.eleventh.tenth.ninth.eighth.JAVA_SOURCE,
            nineteenth.eighteenth.seventeenth.sixteenth.fifteenth.fourteenth.thirteenth.twelfth.eleventh.tenth.ninth.JAVA_SOURCE,
            nineteenth.eighteenth.seventeenth.sixteenth.fifteenth.fourteenth.thirteenth.twelfth.eleventh.tenth.JAVA_SOURCE,
            nineteenth.eighteenth.seventeenth.sixteenth.fifteenth.fourteenth.thirteenth.twelfth.eleventh.JAVA_SOURCE,
            nineteenth.eighteenth.seventeenth.sixteenth.fifteenth.fourteenth.thirteenth.twelfth.JAVA_SOURCE,
            nineteenth.eighteenth.seventeenth.sixteenth.fifteenth.fourteenth.thirteenth.JAVA_SOURCE,
            nineteenth.eighteenth.seventeenth.sixteenth.fifteenth.fourteenth.JAVA_SOURCE,
            nineteenth.eighteenth.seventeenth.sixteenth.fifteenth.JAVA_SOURCE,
            nineteenth.eighteenth.seventeenth.sixteenth.JAVA_SOURCE,
            nineteenth.eighteenth.seventeenth.JAVA_SOURCE,
            nineteenth.eighteenth.JAVA_SOURCE,
            nineteenth.JAVA_SOURCE,
            JAVA_SOURCE,
        )
        if any(not path.is_file() for path in sources):
            raise TwentiethLayerError("source-free twentieth original JVM bridge missing")
        build = subprocess.run(
            ["javac", "-encoding", "UTF-8", "-d", str(work),
             *(str(path) for path in sources)],
            capture_output=True, text=True, timeout=timeout, check=False
        )
        if build.returncode:
            raise TwentiethLayerError("twentieth javac failed: " + build.stderr[:480])
        process = subprocess.run(
            ["java", "-Xmx768m", "-cp",
             os.pathsep.join((str(work), *(str(jar) for jar in jars))),
             "HelveStockFinalDensityTwentiethLayer262", "--twentieth-layer-128"],
            input="\n".join(
                f"{point['world_seed_bits']}\t{point['block_x']}\t{point['block_y']}\t{point['block_z']}"
                for point in FINAL.input_rows()
            ) + "\n",
            capture_output=True, text=True, timeout=timeout, check=False,
        )
        if process.returncode:
            marker = next((line for line in process.stdout.splitlines()
                           if line.startswith(FAIL)), "no bounded twentieth failure marker")
            raise TwentiethLayerError("original twentieth JVM failure: " + marker[:160])
        return parse_output(process.stdout)


def capture(*, source: Path, db: Path, lock: Path,
            server: Path, output: Path) -> dict:
    dest = FINAL.improved.external_output(output)
    source_sha, server_sha, methods = (
        nineteenth.eighteenth.seventeenth.sixteenth.fifteenth.fourteenth.thirteenth.twelfth.eleventh.tenth.ninth.eighth.seventh.sixth.fifth.fourth.third.second.inner
        .source_provenance(source, db, lock, server)
    )
    shapes, vectors = observe(server)
    report = {
        "schema": 1, "kind": KIND, "minecraft": "26.2",
        "protocol": 776, "data_version": 4903,
        "source_archive_sha256": source_sha,
        "official_server_sha256": server_sha,
        "prior_thirteenth_fixture_sha256": nineteenth.seventeenth_fixture.prior.prior.SHA256,
        "prior_sixteenth_fixture_sha256": nineteenth.seventeenth_fixture.prior.SHA256,
        "prior_seventeenth_fixture_sha256": nineteenth.seventeenth_fixture.SHA256,
        "prior_eighteenth_override_fixture_sha256": prior.prior.SHA256,
        "prior_nineteenth_fixture_sha256": prior.SHA256,
        "prior_thirteenth_report_sha256": nineteenth.seventeenth_fixture.prior.prior.REPORT_SHA256,
        "prior_fourteenth_report_sha256": nineteenth.seventeenth_fixture.prior.receipt.owner.previous.REPORT_SHA256,
        "prior_fifteenth_report_sha256": nineteenth.seventeenth_fixture.prior.receipt.REPORT_SHA256,
        "prior_sixteenth_report_sha256": nineteenth.seventeenth_fixture.prior.REPORT_SHA256,
        "prior_seventeenth_report_sha256": nineteenth.seventeenth_fixture.REPORT_SHA256,
        "prior_eighteenth_report_sha256": prior.prior.REPORT_SHA256,
        "prior_nineteenth_report_sha256": prior.REPORT_SHA256,
        "source_methods": methods,
        "world_seeds": list(FINAL.SEEDS),
        "point_count_per_seed": 32,
        "sample_context": "DensityFunction$SinglePointContext",
        "original_stock_registry_used": True,
        "new_twentieth_actual_muloradd_child_observed": True,
        "source_text_included": False,
        "shapes": shapes, "vectors": vectors,
        "muloradd_candidate_telemetry": candidate_telemetry(shapes, vectors),
        **{gate: False for gate in GATES},
    }
    validate(report)
    payload = (json.dumps(report, indent=2, sort_keys=True) + "\n").encode("ascii")
    if len(payload) > 115000:
        raise TwentiethLayerError("unbounded twentieth source-free report bytes")
    dest.parent.mkdir(parents=True, exist_ok=True)
    with os.fdopen(os.open(dest, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600), "wb") as fp:
        fp.write(payload)
    return {
        "output": str(dest),
        "sha256": hashlib.sha256(payload).hexdigest(),
        "new_twentieth_original_ieee_words": len(vectors),
        "independent_old_nineteenth_right_ieee_words": len(vectors),
        "real_muloradd_enum_class": shapes[0]["muloradd_enum_class"],
        "real_muloradd_op": shapes[0]["muloradd_op"],
        "real_muloradd_argument_bits": shapes[0]["muloradd_argument_bits"],
        "real_muloradd_child_class": shapes[0]["muloradd_child_class"],
        "muloradd_candidate_telemetry": candidate_telemetry(shapes, vectors),
        **{gate: False for gate in GATES},
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=FINAL.primitive.SOURCE)
    parser.add_argument("--db", type=Path, default=FINAL.primitive.DB)
    parser.add_argument("--lock", type=Path, default=FINAL.primitive.LOCK)
    parser.add_argument("--cache", type=Path, default=FINAL.primitive.CACHE)
    parser.add_argument("--server-jar", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        server = args.server_jar
        if server is None:
            metadata, _ = official.resolve("26.2", args.cache)
            server = metadata["server"][0]
        print(json.dumps(capture(
            source=args.source, db=args.db, lock=args.lock,
            server=server, output=args.output
        ), sort_keys=True))
    except (
        TwentiethLayerError, ValueError, TypeError, KeyError, IndexError, OSError,
        sqlite3.Error, subprocess.TimeoutExpired, urllib.error.URLError
    ) as exc:
        print("STOCK 26.2 TWENTIETH LAYER OPEN: " + str(exc), file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
