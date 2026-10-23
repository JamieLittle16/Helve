#!/usr/bin/env python3
"""TwentySecond bounded original JVM source-owned RIGHT MulOrAdd child probe.

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
import re
import os
import sqlite3
import struct
import subprocess
import sys
import tempfile
import urllib.error
from pathlib import Path

import official_state_data as official
import worldgen_26_2_stock_final_density_twentieth_layer as twentieth
import worldgen_26_2_stock_final_density_nineteenth_layer as nineteenth
import worldgen_26_2_stock_finaldensity_nineteenth_layer_fixture as prior_nineteenth
import worldgen_26_2_stock_finaldensity_twentieth_layer_fixture as prior
import worldgen_26_2_stock_final_density_twenty_first_layer as predecessor
import worldgen_26_2_stock_finaldensity_twenty_first_layer_fixture as prior_leaf

JAVA_SOURCE = Path(__file__).resolve().parent / (
    "worldgen_java/HelveStockFinalDensityTwentySecondLayer262.java"
)
KIND = "original_26_2_finaldensity_twenty_second_real_noise_leaf_structure_unadmitted"
HEAD = "HELVE26_2_TWENTY_SECOND_SHAPE"
VALUE = "HELVE26_2_TWENTY_SECOND_VALUE"
END = "HELVE26_2_TWENTY_SECOND_END"
FAIL = "HELVE26_2_TWENTY_SECOND_FAILURE"
SHAPE_FIELDS = (
    "noise_node_class", "noise_xz_scale_bits", "noise_y_scale_bits",
    "noise_holder_class", "noise_data_holder_class", "noise_parameters_key",
    "noise_runtime_class",
)
NEW_FIELDS = ()  # terminal stock Noise node: no next child numeric values
OLD_FIELDS = ("old_twenty_first_noise_bits",)
WORDS = OLD_FIELDS
GATES = tuple(predecessor.GATES) + (
    "twenty_second_original_noise_leaf_structure_qualified",
    "twenty_second_all_input_noise_holder_binding_law_admitted",
)
CLASS = twentieth.CLASS
FINAL = twentieth.FINAL
ROOT = twentieth.ROOT


class TwentySecondLayerError(ValueError):
    """Actual original twenty_second source shape, ancestry or frame drift."""


def finite_bits(word: str) -> bool:
    return nineteenth.finite_bits(word)


def value(word: str) -> float:
    return struct.unpack(">d", bytes.fromhex(word[2:]))[0]


def bits(number: float) -> str:
    return "0x" + struct.pack(">d", number).hex()


def validate_shape(shape: dict) -> None:
    if not isinstance(shape, dict) or set(shape) != set(SHAPE_FIELDS) | {"world_seed_bits"}:
        raise TwentySecondLayerError("original Noise node structure fields moved")
    if shape["noise_node_class"] != CLASS + "Noise":
        raise TwentySecondLayerError("real original Noise runtime class drift")
    if shape["noise_holder_class"] != "net.minecraft.world.level.levelgen.DensityFunction$NoiseHolder":
        raise TwentySecondLayerError("genuine NoiseHolder concrete source class drift")
    if shape["noise_runtime_class"] != "net.minecraft.world.level.levelgen.synth.NormalNoise":
        raise TwentySecondLayerError("genuine bound NormalNoise source class drift")
    if shape["noise_data_holder_class"] not in (
        "net.minecraft.core.Holder$Reference", "net.minecraft.core.Holder$Direct"
    ):
        raise TwentySecondLayerError("original Noise holder storage class drift")
    if not isinstance(shape["noise_parameters_key"], str) or not re.fullmatch(
        r"(?:minecraft:[a-z0-9_./-]+|unkeyed)", shape["noise_parameters_key"]
    ):
        raise TwentySecondLayerError("original Noise resource identity malformed")
    for k in ("noise_xz_scale_bits", "noise_y_scale_bits"):
        word = shape[k]
        if not isinstance(word, str) or len(word) != 16 or not finite_bits(word):
            raise TwentySecondLayerError("original Noise axis-scale IEEE malformed")


def candidate_telemetry(shapes: list[dict], vectors: list[dict]) -> dict:
    """All old original Noise leaf words are independently anchored."""
    return {
        "original_bounded_points": len(vectors),
        "old_twenty_first_noise_anchors_matched": len(vectors),
        "genuinely_new_ieee_words": 0,
        "original_noise_shapes_observed": len(shapes),
        "source_law_admitted": False,
    }


def parse_output(stdout: str) -> tuple[list[dict], list[dict]]:
    if not isinstance(stdout, str) or len(stdout) > 100000:
        raise TwentySecondLayerError("unbounded original twenty_second JVM frame output")
    frames = [parts for line in stdout.splitlines()
              if (parts := line.split("|"))[0] in (HEAD, VALUE, END, FAIL)]
    if any(frame[0] == FAIL for frame in frames):
        raise TwentySecondLayerError("bounded genuine twenty_second JVM reflection failure")
    old = prior_leaf.load()
    points = FINAL.input_rows()
    shapes = []
    vectors = []
    cursor = 0
    for group, seed in enumerate(FINAL.SEEDS):
        if cursor >= len(frames):
            raise TwentySecondLayerError("missing twenty_second original seed shape")
        header = frames[cursor]
        cursor += 1
        if len(header) != 3 + len(SHAPE_FIELDS) or header[:3] != [HEAD, str(group), seed]:
            raise TwentySecondLayerError("actual twenty_second original seed header drift")
        shape = dict(zip(SHAPE_FIELDS, header[3:], strict=True))
        shape["world_seed_bits"] = seed
        validate_shape(shape)
        shapes.append(shape)
        for j in range(32):
            i = group * 32 + j
            if cursor >= len(frames):
                raise TwentySecondLayerError("missing source-owned twenty_second point")
            record = frames[cursor]
            cursor += 1
            if (len(record) != 2 + len(WORDS)
                    or record[:2] != [VALUE, str(i)]
                    or not all(finite_bits(word) for word in record[2:])):
                raise TwentySecondLayerError("malformed original twenty_second finite IEEE frame")
            actual = dict(zip(WORDS, ("0x" + word for word in record[2:]), strict=True))
            if actual["old_twenty_first_noise_bits"][2:] != old[i]:
                raise TwentySecondLayerError(
                    f"independently frozen twenty-first real Noise leaf drift at {i}"
                )
            vectors.append({**points[i], **actual})
        if cursor >= len(frames) or frames[cursor] != [END, str(group), "32"]:
            raise TwentySecondLayerError("twenty_second original 32-point seed terminator moved")
        cursor += 1
    if cursor != len(frames):
        raise TwentySecondLayerError("twenty_second JVM emitted unexpected frames")
    if any(
        {k: v for k, v in shape.items() if k != "world_seed_bits"}
        != {k: v for k, v in shapes[0].items() if k != "world_seed_bits"}
        for shape in shapes[1:]
    ):
        raise TwentySecondLayerError("original MulOrAdd source enum/parameter/child changed across seeds")
    return shapes, vectors


def validate(report: dict) -> None:
    if not isinstance(report, dict):
        raise TwentySecondLayerError("original twenty_second report must be JSON object")
    fixture = twentieth.nineteenth.seventeenth_fixture
    pins = {
        "schema": 1, "kind": KIND, "minecraft": "26.2",
        "protocol": 776, "data_version": 4903,
        "source_archive_sha256": FINAL.frozen.SOURCE_SHA256,
        "official_server_sha256": FINAL.frozen.SERVER_SHA256,
        "prior_thirteenth_fixture_sha256": fixture.prior.prior.SHA256,
        "prior_sixteenth_fixture_sha256": fixture.prior.SHA256,
        "prior_seventeenth_fixture_sha256": fixture.SHA256,
        "prior_eighteenth_override_fixture_sha256": prior_nineteenth.prior.SHA256,
        "prior_nineteenth_fixture_sha256": prior_nineteenth.SHA256,
        "prior_twentieth_fixture_sha256": prior.SHA256,
        "prior_twenty_first_fixture_sha256": prior_leaf.SHA256,
        "prior_thirteenth_report_sha256": fixture.prior.prior.REPORT_SHA256,
        "prior_fourteenth_report_sha256": fixture.prior.receipt.owner.previous.REPORT_SHA256,
        "prior_fifteenth_report_sha256": fixture.prior.receipt.REPORT_SHA256,
        "prior_sixteenth_report_sha256": fixture.prior.REPORT_SHA256,
        "prior_seventeenth_report_sha256": fixture.REPORT_SHA256,
        "prior_eighteenth_report_sha256": prior_nineteenth.prior.REPORT_SHA256,
        "prior_nineteenth_report_sha256": prior_nineteenth.REPORT_SHA256,
        "prior_twentieth_report_sha256": prior.REPORT_SHA256,
        "prior_twenty_first_report_sha256": prior_leaf.REPORT_SHA256,
        "source_methods": report.get("source_methods"),
        "world_seeds": list(FINAL.SEEDS),
        "point_count_per_seed": 32,
        "sample_context": "DensityFunction$SinglePointContext",
        "original_stock_registry_used": True,
        "original_twenty_second_real_noise_leaf_structure_observed": True,
        "source_text_included": False,
        "noise_structure_candidate_telemetry": report.get("noise_structure_candidate_telemetry"),
        **{gate: False for gate in GATES},
    }
    if set(report) != set(pins) | {"shapes", "vectors"} or any(
        type(report.get(k)) is not type(v) or report[k] != v for k, v in pins.items()
    ):
        raise TwentySecondLayerError("original twenty_second source provenance/gate report drift")
    methods = report["source_methods"]
    if not isinstance(methods, dict) or set(methods) != {
        "ap2_compute", "holder_holder_compute", "mapped_delegate_compute"
    }:
        raise TwentySecondLayerError("original twenty_second source method inventory changed")
    for name in ("ap2_compute", "holder_holder_compute"):
        method = methods[name]
        if (not isinstance(method, dict) or method.get("reviewed") is not False
                or tuple(method.get(k) for k in (
                    "owner", "signature", "body_sha256", "normalized_sha256"
                )) != ROOT.frozen_final.METHODS[name]):
            raise TwentySecondLayerError("source-indexed Java method SHA drift")
    mapped = methods["mapped_delegate_compute"]
    if (not isinstance(mapped, dict)
            or mapped.get("reviewed") is not False
            or mapped.get("owner") != ROOT.PURE_TRANSFORMER
            or mapped.get("body_sha256") != ROOT.PURE_COMPUTE_SHA256):
        raise TwentySecondLayerError("original mapped delegate method SHA drift")
    shapes, vectors = report.get("shapes"), report.get("vectors")
    if (not isinstance(shapes, list) or len(shapes) != 4
            or not isinstance(vectors, list) or len(vectors) != 128):
        raise TwentySecondLayerError("twenty_second original 4x32 shape/count drift")
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
                raise TwentySecondLayerError("twenty_second original seed/XYZ or field identity changed")
            replay.append("|".join((VALUE, str(i), *(row[k][2:] for k in WORDS))))
        replay.append("|".join((END, str(group), "32")))
    candidate = candidate_telemetry(shapes, vectors)
    if (type(report["noise_structure_candidate_telemetry"]) is not dict
            or report["noise_structure_candidate_telemetry"] != candidate):
        raise TwentySecondLayerError("twenty_second source-free finite arithmetic telemetry drift")
    if parse_output("\n".join(replay)) != (shapes, vectors):
        raise TwentySecondLayerError("original twenty_second source-free record replay failed")


def observe(server: Path, timeout: int = 240) -> tuple[list[dict], list[dict]]:
    with tempfile.TemporaryDirectory(prefix="helve-26_2-twenty_second-layer-") as td:
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
            twentieth.JAVA_SOURCE,
            predecessor.JAVA_SOURCE,
            JAVA_SOURCE,
        )
        if any(not path.is_file() for path in sources):
            raise TwentySecondLayerError("source-free twenty_second original JVM bridge missing")
        build = subprocess.run(
            ["javac", "-encoding", "UTF-8", "-d", str(work),
             *(str(path) for path in sources)],
            capture_output=True, text=True, timeout=timeout, check=False
        )
        if build.returncode:
            raise TwentySecondLayerError("twenty_second javac failed: " + build.stderr[:480])
        process = subprocess.run(
            ["java", "-Xmx768m", "-cp",
             os.pathsep.join((str(work), *(str(jar) for jar in jars))),
             "HelveStockFinalDensityTwentySecondLayer262", "--twenty-second-layer-128"],
            input="\n".join(
                f"{point['world_seed_bits']}\t{point['block_x']}\t{point['block_y']}\t{point['block_z']}"
                for point in FINAL.input_rows()
            ) + "\n",
            capture_output=True, text=True, timeout=timeout, check=False,
        )
        if process.returncode:
            marker = next((line for line in process.stdout.splitlines()
                           if line.startswith(FAIL)), "no bounded twenty_second failure marker")
            raise TwentySecondLayerError("original twenty_second JVM failure: " + marker[:160])
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
        "prior_thirteenth_fixture_sha256": twentieth.nineteenth.seventeenth_fixture.prior.prior.SHA256,
        "prior_sixteenth_fixture_sha256": twentieth.nineteenth.seventeenth_fixture.prior.SHA256,
        "prior_seventeenth_fixture_sha256": twentieth.nineteenth.seventeenth_fixture.SHA256,
        "prior_eighteenth_override_fixture_sha256": prior_nineteenth.prior.SHA256,
        "prior_nineteenth_fixture_sha256": prior_nineteenth.SHA256,
        "prior_twentieth_fixture_sha256": prior.SHA256,
        "prior_twenty_first_fixture_sha256": prior_leaf.SHA256,
        "prior_thirteenth_report_sha256": twentieth.nineteenth.seventeenth_fixture.prior.prior.REPORT_SHA256,
        "prior_fourteenth_report_sha256": twentieth.nineteenth.seventeenth_fixture.prior.receipt.owner.previous.REPORT_SHA256,
        "prior_fifteenth_report_sha256": twentieth.nineteenth.seventeenth_fixture.prior.receipt.REPORT_SHA256,
        "prior_sixteenth_report_sha256": twentieth.nineteenth.seventeenth_fixture.prior.REPORT_SHA256,
        "prior_seventeenth_report_sha256": twentieth.nineteenth.seventeenth_fixture.REPORT_SHA256,
        "prior_eighteenth_report_sha256": prior_nineteenth.prior.REPORT_SHA256,
        "prior_nineteenth_report_sha256": prior_nineteenth.REPORT_SHA256,
        "prior_twentieth_report_sha256": prior.REPORT_SHA256,
        "prior_twenty_first_report_sha256": prior_leaf.REPORT_SHA256,
        "source_methods": methods,
        "world_seeds": list(FINAL.SEEDS),
        "point_count_per_seed": 32,
        "sample_context": "DensityFunction$SinglePointContext",
        "original_stock_registry_used": True,
        "original_twenty_second_real_noise_leaf_structure_observed": True,
        "source_text_included": False,
        "shapes": shapes, "vectors": vectors,
        "noise_structure_candidate_telemetry": candidate_telemetry(shapes, vectors),
        **{gate: False for gate in GATES},
    }
    validate(report)
    payload = (json.dumps(report, indent=2, sort_keys=True) + "\n").encode("ascii")
    if len(payload) > 115000:
        raise TwentySecondLayerError("unbounded twenty_second source-free report bytes")
    dest.parent.mkdir(parents=True, exist_ok=True)
    with os.fdopen(os.open(dest, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600), "wb") as fp:
        fp.write(payload)
    return {
        "output": str(dest),
        "sha256": hashlib.sha256(payload).hexdigest(),
        "genuinely_new_ieee_words": 0,
        "independent_old_twenty_first_noise_ieee_anchors": len(vectors),
        "noise_node_class": shapes[0]["noise_node_class"],
        "noise_xz_scale_bits": shapes[0]["noise_xz_scale_bits"],
        "noise_y_scale_bits": shapes[0]["noise_y_scale_bits"],
        "noise_data_holder_class": shapes[0]["noise_data_holder_class"],
        "noise_parameters_key": shapes[0]["noise_parameters_key"],
        "noise_runtime_class": shapes[0]["noise_runtime_class"],
        "noise_structure_candidate_telemetry": candidate_telemetry(shapes, vectors),
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
        TwentySecondLayerError, ValueError, TypeError, KeyError, IndexError, OSError,
        sqlite3.Error, subprocess.TimeoutExpired, urllib.error.URLError
    ) as exc:
        print("STOCK 26.2 TWENTY_SECOND LAYER OPEN: " + str(exc), file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
