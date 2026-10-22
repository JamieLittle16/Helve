#!/usr/bin/env python3
"""Bounded original JVM 26.2 sixteenth: actual CacheOnce-wrapped Ap2 operands.

Genuine fifteenth Marker(CacheOnce) wraps actual DensityFunctions$Ap2.
Reflect its real enum and two immediate classes; export exactly TWO NEW
actual child IEEE words per original 4x32 SinglePointContext, with one OLD
Ap2 output checked against immutable thirteenth RIGHT operand. A complete
fifteenth original source-report SHA pins prior Holder/Marker equality.
Original stock NoiseChunk/cache law and production authority stay disabled.
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
import worldgen_26_2_stock_final_density_fifteenth_layer as fifteenth
import worldgen_26_2_stock_finaldensity_fifteenth_layer_receipt as previous
import worldgen_26_2_stock_finaldensity_thirteenth_layer_fixture as prior

JAVA_SOURCE = Path(__file__).resolve().parent / (
    "worldgen_java/HelveStockFinalDensitySixteenthLayer262.java"
)
KIND = "original_26_2_finaldensity_sixteenth_cacheonce_ap2_children_unadmitted"
HEAD = "HELVE26_2_SIXTEENTH_SHAPE"
VALUE = "HELVE26_2_SIXTEENTH_VALUE"
END = "HELVE26_2_SIXTEENTH_END"
FAIL = "HELVE26_2_SIXTEENTH_FAILURE"
SHAPE_FIELDS = ("ap2_enum_class", "ap2_op", "ap2_left_class", "ap2_right_class")
NEW_FIELDS = ("ap2_left_bits", "ap2_right_bits")
OLD_FIELDS = ("old_thirteenth_right_bits",)
WORDS = NEW_FIELDS + OLD_FIELDS
GATES = tuple(fifteenth.GATES) + (
    "sixteenth_actual_cacheonce_ap2_children_qualified",
    "sixteenth_all_input_ap2_law_admitted",
)
CLASS = fifteenth.CLASS
FINAL = fifteenth.FINAL
ROOT = fifteenth.ROOT


class SixteenthLayerError(ValueError):
    """The original sixteenth 26.2 JVM source-owner evidence cannot be admitted."""


def finite_bits(word: str) -> bool:
    return fifteenth.finite_bits(word)


def value(word: str) -> float:
    return struct.unpack(">d", bytes.fromhex(word[2:]))[0]


def bits(number: float) -> str:
    return "0x" + struct.pack(">d", number).hex()


def validate_shape(s: dict) -> None:
    if not isinstance(s, dict) or set(s) != set(SHAPE_FIELDS) | {"world_seed_bits"}:
        raise SixteenthLayerError("source-owned sixteenth Ap2 record shape changed")
    if s["ap2_enum_class"] != CLASS + "TwoArgumentSimpleFunction$Type":
        raise SixteenthLayerError("original sixteenth Ap2 enum owner changed")
    if s["ap2_op"] not in ("ADD", "MUL", "MIN", "MAX"):
        raise SixteenthLayerError("original sixteenth Ap2 operation changed")
    for k in ("ap2_left_class", "ap2_right_class"):
        try:
            fifteenth.fourteenth.thirteenth.twelfth.eleventh.tenth.ninth.eighth.seventh.sixth.fifth.fourth.third.second.require_class(
                s[k]
            )
        except (ValueError, TypeError) as exc:
            raise SixteenthLayerError("genuine sixteenth density child class malformed") from exc


def candidate_telemetry(shapes: list[dict], vectors: list[dict]) -> dict:
    """FINITE arithmetic candidate only. Preserve genuine mismatches unfiltered."""
    mismatches = []
    left = right = ties = 0
    for i, v in enumerate(vectors):
        a = value(v["ap2_left_bits"])
        b = value(v["ap2_right_bits"])
        op = shapes[i // 32]["ap2_op"]
        if a == b:
            ties += 1
        if a < b:
            left += 1
        elif a > b:
            right += 1
        try:
            if op == "ADD":
                guess = a + b
            elif op == "MUL":
                guess = a * b
            elif op == "MIN":
                guess = min(a, b)
            else:
                guess = max(a, b)
            exact = math.isfinite(guess) and bits(guess) == v["old_thirteenth_right_bits"]
        except (OverflowError, ValueError):
            exact = False
        if not exact:
            mismatches.append(i)
    return {
        "original_bounded_points": len(vectors),
        "arithmetic_candidate_mismatches": len(mismatches),
        "arithmetic_candidate_first_mismatch_index": mismatches[0] if mismatches else -1,
        "observed_left_strictly_less": left,
        "observed_right_strictly_less": right,
        "observed_equal_operands": ties,
        "source_law_admitted": False,
    }


def parse_output(stdout: str) -> tuple[list[dict], list[dict]]:
    if not isinstance(stdout, str) or len(stdout) > 100000:
        raise SixteenthLayerError("unbounded sixteenth original JVM output")
    frames = [parts for line in stdout.splitlines()
              if (parts := line.split("|"))[0] in (HEAD, VALUE, END, FAIL)]
    if any(frame[0] == FAIL for frame in frames):
        raise SixteenthLayerError("original bounded fifteenth JVM source reflection failed")
    old = prior.load()
    points = FINAL.input_rows()
    shapes: list[dict] = []
    vectors: list[dict] = []
    cursor = 0
    for group, seed in enumerate(FINAL.SEEDS):
        if cursor >= len(frames):
            raise SixteenthLayerError("missing bounded source-owner sixteenth seed shape")
        header = frames[cursor]
        cursor += 1
        if len(header) != 3 + len(SHAPE_FIELDS) or header[:3] != [HEAD, str(group), seed]:
            raise SixteenthLayerError("actual original sixteenth seed shape header drift")
        shape = dict(zip(SHAPE_FIELDS, header[3:], strict=True))
        shape["world_seed_bits"] = seed
        validate_shape(shape)
        shapes.append(shape)
        for j in range(32):
            index = group * 32 + j
            if cursor >= len(frames):
                raise SixteenthLayerError("missing sixteenth original fixed XYZ point")
            record = frames[cursor]
            cursor += 1
            if (len(record) != 2 + len(WORDS)
                    or record[:2] != [VALUE, str(index)]
                    or not all(finite_bits(word) for word in record[2:])):
                raise SixteenthLayerError("sixteenth genuine finite IEEE point frame invalid")
            actual = dict(zip(WORDS, ("0x" + w for w in record[2:]), strict=True))
            if actual["old_thirteenth_right_bits"][2:] != old[index][1]:
                raise SixteenthLayerError(
                    "independently frozen thirteenth RIGHT Ap2 parent changed at: "
                    + str(index)
                )
            vectors.append({**points[index], **actual})
        if cursor >= len(frames) or frames[cursor] != [END, str(group), "32"]:
            raise SixteenthLayerError("actual original sixteenth 32-point seed terminator moved")
        cursor += 1
    if cursor != len(frames):
        raise SixteenthLayerError("sixteenth original JVM emitted extra record frames")
    if any(
        {k: v for k, v in s.items() if k != "world_seed_bits"}
        != {k: v for k, v in shapes[0].items() if k != "world_seed_bits"}
        for s in shapes[1:]
    ):
        raise SixteenthLayerError("original actual sixteenth Ap2 op/classes changed across four seeds")
    return shapes, vectors


def validate(report: dict) -> None:
    if not isinstance(report, dict):
        raise SixteenthLayerError("original sixteenth report must be JSON object")
    pins = {
        "schema": 1, "kind": KIND, "minecraft": "26.2",
        "protocol": 776, "data_version": 4903,
        "source_archive_sha256": FINAL.frozen.SOURCE_SHA256,
        "official_server_sha256": FINAL.frozen.SERVER_SHA256,
        "prior_thirteenth_fixture_sha256": prior.SHA256,
        "prior_fourteenth_report_sha256": previous.owner.previous.REPORT_SHA256,
        "prior_fifteenth_report_sha256": previous.REPORT_SHA256,
        "prior_thirteenth_report_sha256": prior.REPORT_SHA256,
        "source_methods": report.get("source_methods"),
        "world_seeds": list(FINAL.SEEDS),
        "point_count_per_seed": 32,
        "sample_context": "DensityFunction$SinglePointContext",
        "original_stock_registry_used": True,
        "new_sixteenth_cacheonce_ap2_children_observed": True,
        "source_text_included": False,
        "ap2_arithmetic_candidate_telemetry": report.get("ap2_arithmetic_candidate_telemetry"),
        **{gate: False for gate in GATES},
    }
    if set(report) != set(pins) | {"shapes", "vectors"} or any(
        type(report.get(k)) is not type(v) or report[k] != v
        for k, v in pins.items()
    ):
        raise SixteenthLayerError("original sixteenth provenance/source/admission drift")
    methods = report["source_methods"]
    if not isinstance(methods, dict) or set(methods) != {
        "ap2_compute", "holder_holder_compute", "mapped_delegate_compute"
    }:
        raise SixteenthLayerError("fifteenth original source method inventory changed")
    for name in ("ap2_compute", "holder_holder_compute"):
        owner = methods[name]
        if (not isinstance(owner, dict)
                or owner.get("reviewed") is not False
                or tuple(owner.get(k) for k in (
                    "owner", "signature", "body_sha256", "normalized_sha256"
                )) != ROOT.frozen_final.METHODS[name]):
            raise SixteenthLayerError("original indexed Java source method SHA moved")
    mapped = methods["mapped_delegate_compute"]
    if (not isinstance(mapped, dict)
            or mapped.get("reviewed") is not False
            or mapped.get("owner") != ROOT.PURE_TRANSFORMER
            or mapped.get("body_sha256") != ROOT.PURE_COMPUTE_SHA256):
        raise SixteenthLayerError("actual mapped delegate source provenance moved")
    shapes, vectors = report.get("shapes"), report.get("vectors")
    if (not isinstance(shapes, list) or len(shapes) != 4
            or not isinstance(vectors, list) or len(vectors) != 128):
        raise SixteenthLayerError("sixteenth actual 4x32 finite capture size moved")
    points = FINAL.input_rows()
    replay = []
    for group, shape in enumerate(shapes):
        validate_shape(shape)
        replay.append("|".join((
            HEAD, str(group), shape["world_seed_bits"],
            *(str(shape[k]) for k in SHAPE_FIELDS)
        )))
        for j in range(32):
            i = group * 32 + j
            v = vectors[i]
            if (not isinstance(v, dict)
                    or set(v) != set(points[i]) | set(WORDS)
                    or any(v.get(k) != p for k, p in points[i].items())):
                raise SixteenthLayerError("sixteenth original XYZ/seed or field set altered")
            replay.append("|".join((VALUE, str(i), *(v[k][2:] for k in WORDS))))
        replay.append("|".join((END, str(group), "32")))
    candidate = candidate_telemetry(shapes, vectors)
    if (type(report["ap2_arithmetic_candidate_telemetry"]) is not dict
            or report["ap2_arithmetic_candidate_telemetry"] != candidate):
        raise SixteenthLayerError("sixteenth sample-only candidate telemetry tampered")
    if parse_output("\n".join(replay)) != (shapes, vectors):
        raise SixteenthLayerError("sixteenth source-free real record round-trip failed")


def observe(server: Path, timeout: int = 240) -> tuple[list[dict], list[dict]]:
    with tempfile.TemporaryDirectory(prefix="helve-26_2-sixteenth-layer-") as td:
        work = Path(td)
        jars = official.extract_classpath(server, work / "classpath")
        f = fifteenth.fourteenth.thirteenth.twelfth.eleventh.tenth.ninth.eighth.seventh.sixth.fifth
        sources = (
            f.fourth.third.second.final.roots.BASE_BRIDGE,
            f.fourth.third.second.final.JAVA_SOURCE,
            f.fourth.third.second.root.JAVA_SOURCE,
            f.fourth.third.second.inner.JAVA_SOURCE,
            f.fourth.third.second.JAVA_SOURCE,
            f.fourth.third.JAVA_SOURCE,
            f.fourth.JAVA_SOURCE,
            f.JAVA_SOURCE,
            fifteenth.fourteenth.thirteenth.twelfth.eleventh.tenth.ninth.eighth.seventh.sixth.JAVA_SOURCE,
            fifteenth.fourteenth.thirteenth.twelfth.eleventh.tenth.ninth.eighth.seventh.JAVA_SOURCE,
            fifteenth.fourteenth.thirteenth.twelfth.eleventh.tenth.ninth.eighth.JAVA_SOURCE,
            fifteenth.fourteenth.thirteenth.twelfth.eleventh.tenth.ninth.JAVA_SOURCE,
            fifteenth.fourteenth.thirteenth.twelfth.eleventh.tenth.JAVA_SOURCE,
            fifteenth.fourteenth.thirteenth.twelfth.eleventh.JAVA_SOURCE,
            fifteenth.fourteenth.thirteenth.twelfth.JAVA_SOURCE,
            fifteenth.fourteenth.thirteenth.JAVA_SOURCE,
            fifteenth.fourteenth.JAVA_SOURCE,
            fifteenth.JAVA_SOURCE,
            JAVA_SOURCE,
        )
        if any(not path.is_file() for path in sources):
            raise SixteenthLayerError("missing original source-free sixteenth bridge")
        build = subprocess.run(
            ["javac", "-encoding", "UTF-8", "-d", str(work),
             *(str(path) for path in sources)],
            capture_output=True, text=True, timeout=timeout, check=False
        )
        if build.returncode:
            raise SixteenthLayerError("sixteenth bounded javac failed: " + build.stderr[:480])
        proc = subprocess.run(
            ["java", "-Xmx768m", "-cp",
             os.pathsep.join((str(work), *(str(jar) for jar in jars))),
             "HelveStockFinalDensitySixteenthLayer262", "--sixteenth-layer-128"],
            input="\n".join(
                f"{p['world_seed_bits']}\t{p['block_x']}\t{p['block_y']}\t{p['block_z']}"
                for p in FINAL.input_rows()
            ) + "\n",
            capture_output=True, text=True, timeout=timeout, check=False,
        )
        if proc.returncode:
            reason = next(
                (line for line in proc.stdout.splitlines() if line.startswith(FAIL)),
                "no bounded original fifteenth failure tag"
            )
            raise SixteenthLayerError("real original fifteenth JVM failure: " + reason[:160])
        return parse_output(proc.stdout)


def capture(*, source: Path, db: Path, lock: Path,
            server: Path, output: Path) -> dict:
    dest = FINAL.improved.external_output(output)
    source_sha, server_sha, methods = (
        fifteenth.fourteenth.thirteenth.twelfth.eleventh.tenth.ninth.eighth.seventh.sixth.fifth.fourth.third.second.inner
        .source_provenance(source, db, lock, server)
    )
    shapes, vectors = observe(server)
    report = {
        "schema": 1, "kind": KIND, "minecraft": "26.2",
        "protocol": 776, "data_version": 4903,
        "source_archive_sha256": source_sha,
        "official_server_sha256": server_sha,
        "prior_thirteenth_fixture_sha256": prior.SHA256,
        "prior_fourteenth_report_sha256": previous.owner.previous.REPORT_SHA256,
        "prior_fifteenth_report_sha256": previous.REPORT_SHA256,
        "prior_thirteenth_report_sha256": prior.REPORT_SHA256,
        "source_methods": methods,
        "world_seeds": list(FINAL.SEEDS),
        "point_count_per_seed": 32,
        "sample_context": "DensityFunction$SinglePointContext",
        "original_stock_registry_used": True,
        "new_sixteenth_cacheonce_ap2_children_observed": True,
        "source_text_included": False,
        "shapes": shapes, "vectors": vectors,
        "ap2_arithmetic_candidate_telemetry": candidate_telemetry(shapes, vectors),
        **{gate: False for gate in GATES},
    }
    validate(report)
    payload = (json.dumps(report, indent=2, sort_keys=True) + "\n").encode("ascii")
    if len(payload) > 115000:
        raise SixteenthLayerError("unbounded sixteenth source-free report payload")
    dest.parent.mkdir(parents=True, exist_ok=True)
    with os.fdopen(os.open(dest, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600), "wb") as fp:
        fp.write(payload)
    return {
        "output": str(dest),
        "sha256": hashlib.sha256(payload).hexdigest(),
        "genuinely_new_sixteenth_ieee_words": len(vectors) * len(NEW_FIELDS),
        "independent_old_thirteenth_right_parent_words": len(vectors),
        "original_ap2_enum_class": shapes[0]["ap2_enum_class"],
        "original_ap2_op": shapes[0]["ap2_op"],
        "original_ap2_left_class": shapes[0]["ap2_left_class"],
        "original_ap2_right_class": shapes[0]["ap2_right_class"],
        "ap2_arithmetic_candidate_telemetry": candidate_telemetry(shapes, vectors),
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
        SixteenthLayerError, ValueError, TypeError, KeyError, IndexError, OSError,
        sqlite3.Error, subprocess.TimeoutExpired, urllib.error.URLError
    ) as exc:
        print("STOCK 26.2 SIXTEENTH LAYER OPEN: " + str(exc), file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
