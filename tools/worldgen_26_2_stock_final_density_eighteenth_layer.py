#!/usr/bin/env python3
"""Actual eighteenth Clamp child/source bounds below seventeenth right Ap2 ADD.

Reflect only genuine original JVM Clamp right operand below source-observed
ADD(HolderHolder, Clamp). Record real 4x32 original Clamp bounds, actual
wrapped DensityFunction runtime class, ONE new inner IEEE word, and one
OLD Clamp parent independently pinned to immutable seventeenth RIGHT
column. No source law, cache lifecycle or production gate is admitted.
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
import worldgen_26_2_stock_final_density_seventeenth_layer as seventeenth
import worldgen_26_2_stock_finaldensity_seventeenth_layer_fixture as prior
import worldgen_26_2_stock_finaldensity_sixteenth_layer_fixture as sixteenth_fixture

JAVA_SOURCE = Path(__file__).resolve().parent / (
    "worldgen_java/HelveStockFinalDensityEighteenthLayer262.java"
)
KIND = "original_26_2_finaldensity_eighteenth_actual_right_clamp_input_unadmitted"
HEAD = "HELVE26_2_EIGHTEENTH_SHAPE"
VALUE = "HELVE26_2_EIGHTEENTH_VALUE"
END = "HELVE26_2_EIGHTEENTH_END"
FAIL = "HELVE26_2_EIGHTEENTH_FAILURE"
SHAPE_FIELDS = ("clamp_class", "clamp_input_class", "clamp_min_bits", "clamp_max_bits")
NEW_FIELDS = ("clamp_inner_bits",)
OLD_FIELDS = ("old_seventeenth_clamp_bits",)
WORDS = NEW_FIELDS + OLD_FIELDS
GATES = tuple(seventeenth.GATES) + (
    "eighteenth_actual_clamp_input_and_bounds_qualified",
    "eighteenth_all_input_clamp_law_admitted",
)
CLASS = seventeenth.CLASS
FINAL = seventeenth.FINAL
ROOT = seventeenth.ROOT


class EighteenthLayerError(ValueError):
    """The original eighteenth 26.2 JVM source-owner evidence cannot be admitted."""


def finite_bits(word: str) -> bool:
    return seventeenth.finite_bits(word)


def value(word: str) -> float:
    return struct.unpack(">d", bytes.fromhex(word[2:]))[0]


def bits(number: float) -> str:
    return "0x" + struct.pack(">d", number).hex()


def validate_shape(s: dict) -> None:
    if not isinstance(s, dict) or set(s) != set(SHAPE_FIELDS) | {"world_seed_bits"}:
        raise EighteenthLayerError("original eighteenth Clamp shape fields moved")
    if s["clamp_class"] != CLASS + "Clamp":
        raise EighteenthLayerError("actual source-owned Clamp class moved")
    try:
        seventeenth.sixteenth.fifteenth.fourteenth.thirteenth.twelfth.eleventh.tenth.ninth.eighth.seventh.sixth.fifth.fourth.third.second.require_class(
            s["clamp_input_class"]
        )
    except (ValueError, TypeError) as exc:
        raise EighteenthLayerError("genuine Clamp sole wrapped DensityFunction class moved") from exc
    for k in ("clamp_min_bits", "clamp_max_bits"):
        if not finite_bits("0x" + s[k]):
            raise EighteenthLayerError("original Clamp min/max raw IEEE is malformed/nonfinite")
    if not value("0x" + s["clamp_min_bits"]) < value("0x" + s["clamp_max_bits"]):
        raise EighteenthLayerError("actual original Clamp bounds not ordered")


def candidate_telemetry(shapes: list[dict], vectors: list[dict]) -> dict:
    """Pure bounded candidate: DOES NOT prove all-input Java Clamp semantics."""
    mismatches = []
    below = within = above = 0
    for i, v in enumerate(vectors):
        shape = shapes[i // 32]
        raw = value(v["clamp_inner_bits"])
        low = value("0x" + shape["clamp_min_bits"])
        high = value("0x" + shape["clamp_max_bits"])
        if raw < low:
            below += 1
        elif raw > high:
            above += 1
        else:
            within += 1
        guess = min(max(raw, low), high)
        if bits(guess) != v["old_seventeenth_clamp_bits"]:
            mismatches.append(i)
    return {
        "original_bounded_points": len(vectors),
        "clamp_candidate_mismatches": len(mismatches),
        "clamp_candidate_first_mismatch_index": mismatches[0] if mismatches else -1,
        "observed_below_min": below,
        "observed_within_inclusive_bounds": within,
        "observed_above_max": above,
        "source_law_admitted": False,
    }


def parse_output(stdout: str) -> tuple[list[dict], list[dict]]:
    if not isinstance(stdout, str) or len(stdout) > 100000:
        raise EighteenthLayerError("unbounded eighteenth original JVM output")
    frames = [parts for line in stdout.splitlines()
              if (parts := line.split("|"))[0] in (HEAD, VALUE, END, FAIL)]
    if any(frame[0] == FAIL for frame in frames):
        raise EighteenthLayerError("original bounded seventeenth JVM source reflection failed")
    old = prior.load()
    points = FINAL.input_rows()
    shapes: list[dict] = []
    vectors: list[dict] = []
    cursor = 0
    for group, seed in enumerate(FINAL.SEEDS):
        if cursor >= len(frames):
            raise EighteenthLayerError("missing bounded source-owner eighteenth seed shape")
        header = frames[cursor]
        cursor += 1
        if len(header) != 3 + len(SHAPE_FIELDS) or header[:3] != [HEAD, str(group), seed]:
            raise EighteenthLayerError("actual original eighteenth seed shape header drift")
        shape = dict(zip(SHAPE_FIELDS, header[3:], strict=True))
        shape["world_seed_bits"] = seed
        validate_shape(shape)
        shapes.append(shape)
        for j in range(32):
            index = group * 32 + j
            if cursor >= len(frames):
                raise EighteenthLayerError("missing eighteenth original fixed XYZ point")
            record = frames[cursor]
            cursor += 1
            if (len(record) != 2 + len(WORDS)
                    or record[:2] != [VALUE, str(index)]
                    or not all(finite_bits(word) for word in record[2:])):
                raise EighteenthLayerError("seventeenth genuine finite IEEE point frame invalid")
            actual = dict(zip(WORDS, ("0x" + w for w in record[2:]), strict=True))
            if actual["old_seventeenth_clamp_bits"][2:] != old[index][1]:
                raise EighteenthLayerError(
                    "independently frozen seventeenth RIGHT Clamp parent drift at: "
                    + str(index)
                )
            vectors.append({**points[index], **actual})
        if cursor >= len(frames) or frames[cursor] != [END, str(group), "32"]:
            raise EighteenthLayerError("actual original eighteenth 32-point seed terminator moved")
        cursor += 1
    if cursor != len(frames):
        raise EighteenthLayerError("eighteenth original JVM emitted extra record frames")
    if any(
        {k: v for k, v in s.items() if k != "world_seed_bits"}
        != {k: v for k, v in shapes[0].items() if k != "world_seed_bits"}
        for s in shapes[1:]
    ):
        raise EighteenthLayerError("original actual seventeenth RIGHT Ap2 op/classes changed across four seeds")
    return shapes, vectors


def validate(report: dict) -> None:
    if not isinstance(report, dict):
        raise EighteenthLayerError("original eighteenth report must be JSON object")
    pins = {
        "schema": 1, "kind": KIND, "minecraft": "26.2",
        "protocol": 776, "data_version": 4903,
        "source_archive_sha256": FINAL.frozen.SOURCE_SHA256,
        "official_server_sha256": FINAL.frozen.SERVER_SHA256,
        "prior_thirteenth_fixture_sha256": sixteenth_fixture.prior.SHA256,
        "prior_sixteenth_fixture_sha256": sixteenth_fixture.SHA256,
        "prior_seventeenth_fixture_sha256": prior.SHA256,
        "prior_fourteenth_report_sha256": sixteenth_fixture.receipt.owner.previous.REPORT_SHA256,
        "prior_fifteenth_report_sha256": sixteenth_fixture.receipt.REPORT_SHA256,
        "prior_sixteenth_report_sha256": sixteenth_fixture.REPORT_SHA256,
        "prior_seventeenth_report_sha256": prior.REPORT_SHA256,
        "prior_thirteenth_report_sha256": sixteenth_fixture.prior.REPORT_SHA256,
        "source_methods": report.get("source_methods"),
        "world_seeds": list(FINAL.SEEDS),
        "point_count_per_seed": 32,
        "sample_context": "DensityFunction$SinglePointContext",
        "original_stock_registry_used": True,
        "new_eighteenth_actual_clamp_input_observed": True,
        "source_text_included": False,
        "clamp_candidate_telemetry": report.get("clamp_candidate_telemetry"),
        **{gate: False for gate in GATES},
    }
    if set(report) != set(pins) | {"shapes", "vectors"} or any(
        type(report.get(k)) is not type(v) or report[k] != v
        for k, v in pins.items()
    ):
        raise EighteenthLayerError("original eighteenth provenance/source/admission drift")
    methods = report["source_methods"]
    if not isinstance(methods, dict) or set(methods) != {
        "ap2_compute", "holder_holder_compute", "mapped_delegate_compute"
    }:
        raise EighteenthLayerError("eighteenth original source method inventory changed")
    for name in ("ap2_compute", "holder_holder_compute"):
        owner = methods[name]
        if (not isinstance(owner, dict)
                or owner.get("reviewed") is not False
                or tuple(owner.get(k) for k in (
                    "owner", "signature", "body_sha256", "normalized_sha256"
                )) != ROOT.frozen_final.METHODS[name]):
            raise EighteenthLayerError("original indexed Java source method SHA moved")
    mapped = methods["mapped_delegate_compute"]
    if (not isinstance(mapped, dict)
            or mapped.get("reviewed") is not False
            or mapped.get("owner") != ROOT.PURE_TRANSFORMER
            or mapped.get("body_sha256") != ROOT.PURE_COMPUTE_SHA256):
        raise EighteenthLayerError("actual mapped delegate source provenance moved")
    shapes, vectors = report.get("shapes"), report.get("vectors")
    if (not isinstance(shapes, list) or len(shapes) != 4
            or not isinstance(vectors, list) or len(vectors) != 128):
        raise EighteenthLayerError("eighteenth actual 4x32 finite capture size moved")
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
                raise EighteenthLayerError("eighteenth original XYZ/seed or field set altered")
            replay.append("|".join((VALUE, str(i), *(v[k][2:] for k in WORDS))))
        replay.append("|".join((END, str(group), "32")))
    candidate = candidate_telemetry(shapes, vectors)
    if (type(report["clamp_candidate_telemetry"]) is not dict
            or report["clamp_candidate_telemetry"] != candidate):
        raise EighteenthLayerError("eighteenth sample-only candidate telemetry tampered")
    if parse_output("\n".join(replay)) != (shapes, vectors):
        raise EighteenthLayerError("eighteenth source-free real record round-trip failed")


def observe(server: Path, timeout: int = 240) -> tuple[list[dict], list[dict]]:
    with tempfile.TemporaryDirectory(prefix="helve-26_2-eighteenth-layer-") as td:
        work = Path(td)
        jars = official.extract_classpath(server, work / "classpath")
        f = seventeenth.sixteenth.fifteenth.fourteenth.thirteenth.twelfth.eleventh.tenth.ninth.eighth.seventh.sixth.fifth
        sources = (
            f.fourth.third.second.final.roots.BASE_BRIDGE,
            f.fourth.third.second.final.JAVA_SOURCE,
            f.fourth.third.second.root.JAVA_SOURCE,
            f.fourth.third.second.inner.JAVA_SOURCE,
            f.fourth.third.second.JAVA_SOURCE,
            f.fourth.third.JAVA_SOURCE,
            f.fourth.JAVA_SOURCE,
            f.JAVA_SOURCE,
            seventeenth.sixteenth.fifteenth.fourteenth.thirteenth.twelfth.eleventh.tenth.ninth.eighth.seventh.sixth.JAVA_SOURCE,
            seventeenth.sixteenth.fifteenth.fourteenth.thirteenth.twelfth.eleventh.tenth.ninth.eighth.seventh.JAVA_SOURCE,
            seventeenth.sixteenth.fifteenth.fourteenth.thirteenth.twelfth.eleventh.tenth.ninth.eighth.JAVA_SOURCE,
            seventeenth.sixteenth.fifteenth.fourteenth.thirteenth.twelfth.eleventh.tenth.ninth.JAVA_SOURCE,
            seventeenth.sixteenth.fifteenth.fourteenth.thirteenth.twelfth.eleventh.tenth.JAVA_SOURCE,
            seventeenth.sixteenth.fifteenth.fourteenth.thirteenth.twelfth.eleventh.JAVA_SOURCE,
            seventeenth.sixteenth.fifteenth.fourteenth.thirteenth.twelfth.JAVA_SOURCE,
            seventeenth.sixteenth.fifteenth.fourteenth.thirteenth.JAVA_SOURCE,
            seventeenth.sixteenth.fifteenth.fourteenth.JAVA_SOURCE,
            seventeenth.sixteenth.fifteenth.JAVA_SOURCE,
            seventeenth.sixteenth.JAVA_SOURCE,
            seventeenth.JAVA_SOURCE,
            JAVA_SOURCE,
        )
        if any(not path.is_file() for path in sources):
            raise EighteenthLayerError("missing original source-free eighteenth bridge")
        build = subprocess.run(
            ["javac", "-encoding", "UTF-8", "-d", str(work),
             *(str(path) for path in sources)],
            capture_output=True, text=True, timeout=timeout, check=False
        )
        if build.returncode:
            raise EighteenthLayerError("eighteenth bounded javac failed: " + build.stderr[:480])
        proc = subprocess.run(
            ["java", "-Xmx768m", "-cp",
             os.pathsep.join((str(work), *(str(jar) for jar in jars))),
             "HelveStockFinalDensityEighteenthLayer262", "--eighteenth-layer-128"],
            input="\n".join(
                f"{p['world_seed_bits']}\t{p['block_x']}\t{p['block_y']}\t{p['block_z']}"
                for p in FINAL.input_rows()
            ) + "\n",
            capture_output=True, text=True, timeout=timeout, check=False,
        )
        if proc.returncode:
            reason = next(
                (line for line in proc.stdout.splitlines() if line.startswith(FAIL)),
                "no bounded original eighteenth failure tag"
            )
            raise EighteenthLayerError("real original eighteenth JVM failure: " + reason[:160])
        return parse_output(proc.stdout)


def capture(*, source: Path, db: Path, lock: Path,
            server: Path, output: Path) -> dict:
    dest = FINAL.improved.external_output(output)
    source_sha, server_sha, methods = (
        seventeenth.sixteenth.fifteenth.fourteenth.thirteenth.twelfth.eleventh.tenth.ninth.eighth.seventh.sixth.fifth.fourth.third.second.inner
        .source_provenance(source, db, lock, server)
    )
    shapes, vectors = observe(server)
    report = {
        "schema": 1, "kind": KIND, "minecraft": "26.2",
        "protocol": 776, "data_version": 4903,
        "source_archive_sha256": source_sha,
        "official_server_sha256": server_sha,
        "prior_thirteenth_fixture_sha256": sixteenth_fixture.prior.SHA256,
        "prior_sixteenth_fixture_sha256": sixteenth_fixture.SHA256,
        "prior_seventeenth_fixture_sha256": prior.SHA256,
        "prior_fourteenth_report_sha256": sixteenth_fixture.receipt.owner.previous.REPORT_SHA256,
        "prior_fifteenth_report_sha256": sixteenth_fixture.receipt.REPORT_SHA256,
        "prior_sixteenth_report_sha256": sixteenth_fixture.REPORT_SHA256,
        "prior_seventeenth_report_sha256": prior.REPORT_SHA256,
        "prior_thirteenth_report_sha256": sixteenth_fixture.prior.REPORT_SHA256,
        "source_methods": methods,
        "world_seeds": list(FINAL.SEEDS),
        "point_count_per_seed": 32,
        "sample_context": "DensityFunction$SinglePointContext",
        "original_stock_registry_used": True,
        "new_eighteenth_actual_clamp_input_observed": True,
        "source_text_included": False,
        "shapes": shapes, "vectors": vectors,
        "clamp_candidate_telemetry": candidate_telemetry(shapes, vectors),
        **{gate: False for gate in GATES},
    }
    validate(report)
    payload = (json.dumps(report, indent=2, sort_keys=True) + "\n").encode("ascii")
    if len(payload) > 115000:
        raise EighteenthLayerError("unbounded eighteenth source-free report payload")
    dest.parent.mkdir(parents=True, exist_ok=True)
    with os.fdopen(os.open(dest, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600), "wb") as fp:
        fp.write(payload)
    return {
        "output": str(dest),
        "sha256": hashlib.sha256(payload).hexdigest(),
        "genuinely_new_eighteenth_ieee_words": len(vectors) * len(NEW_FIELDS),
        "independent_old_seventeenth_clamp_parent_words": len(vectors),
        "original_clamp_class": shapes[0]["clamp_class"],
        "original_clamp_inner_class": shapes[0]["clamp_input_class"],
        "original_clamp_min_bits": shapes[0]["clamp_min_bits"],
        "original_clamp_max_bits": shapes[0]["clamp_max_bits"],
        "clamp_candidate_telemetry": candidate_telemetry(shapes, vectors),
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
        EighteenthLayerError, ValueError, TypeError, KeyError, IndexError, OSError,
        sqlite3.Error, subprocess.TimeoutExpired, urllib.error.URLError
    ) as exc:
        print("STOCK 26.2 EIGHTEENTH LAYER OPEN: " + str(exc), file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
