#!/usr/bin/env python3
"""Bounded original JVM 26.2 thirteenth: selected twelfth MIN-left Ap2 children.

The twelfth MIN-left Ap2 participates in 55 selected stock final MIN-root
results across the frozen 128 points. Reflect ONLY that exact JVM Ap2,
its enum operation and two actual immediate children. Emit exactly two
NEW child IEEE values per source-owned point; check the independently
frozen twelfth left parent, not an original root or recopied prior fixture.
No original prior captures are replayed; no source-law or product admission.
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
import worldgen_26_2_stock_final_density_twelfth_layer as twelfth
import worldgen_26_2_stock_finaldensity_twelfth_layer_fixture as prior

JAVA_SOURCE = Path(__file__).resolve().parent / (
    "worldgen_java/HelveStockFinalDensityThirteenthLayer262.java"
)
KIND = "original_26_2_finaldensity_thirteenth_selected_left_ap2_children_unadmitted"
HEAD = "HELVE26_2_THIRTEENTH_SHAPE"
VALUE = "HELVE26_2_THIRTEENTH_VALUE"
END = "HELVE26_2_THIRTEENTH_END"
FAIL = "HELVE26_2_THIRTEENTH_FAILURE"
SHAPE_FIELDS = ("ap2_enum_class", "ap2_op", "ap2_left_class", "ap2_right_class")
NEW_FIELDS = ("left_ap2_left_bits", "left_ap2_right_bits")
OLD_FIELDS = ("old_twelfth_left_bits",)
WORDS = NEW_FIELDS + OLD_FIELDS
GATES = tuple(twelfth.GATES) + (
    "thirteenth_actual_left_ap2_children_qualified",
    "thirteenth_all_input_ap2_law_admitted",
)
CLASS = twelfth.CLASS
FINAL = twelfth.FINAL
ROOT = twelfth.ROOT


class ThirteenthLayerError(ValueError):
    """The original thirteenth 26.2 JVM source-owner evidence cannot be admitted."""


def finite_bits(word: str) -> bool:
    return twelfth.finite_bits(word)


def value(word: str) -> float:
    return struct.unpack(">d", bytes.fromhex(word[2:]))[0]


def bits(number: float) -> str:
    return "0x" + struct.pack(">d", number).hex()


def validate_shape(s: dict) -> None:
    if not isinstance(s, dict) or set(s) != set(SHAPE_FIELDS) | {"world_seed_bits"}:
        raise ThirteenthLayerError("actual thirteenth left-Ap2 source-owned record shape moved")
    if s["ap2_enum_class"] != CLASS + "TwoArgumentSimpleFunction$Type":
        raise ThirteenthLayerError("original selected twelfth left Ap2 enum declaring class moved")
    if s["ap2_op"] not in ("ADD", "MUL", "MIN", "MAX"):
        raise ThirteenthLayerError("actual original selected twelfth left Ap2 operation moved")
    for key in ("ap2_left_class", "ap2_right_class"):
        try:
            twelfth.eleventh.tenth.ninth.eighth.seventh.sixth.fifth.fourth.third.second.require_class(
                s[key]
            )
        except (ValueError, TypeError) as exc:
            raise ThirteenthLayerError("original out-left Ap2 child class invalid") from exc


def candidate_telemetry(shapes: list[dict], vectors: list[dict]) -> dict:
    """Independent arithmetic candidate only; mismatches do not censor JVM values."""
    mismatches = []
    for i, vector in enumerate(vectors):
        op = shapes[i // 32]["ap2_op"]
        x = value(vector["left_ap2_left_bits"])
        y = value(vector["left_ap2_right_bits"])
        try:
            if op == "ADD":
                guess = x + y
            elif op == "MUL":
                guess = x * y
            elif op == "MIN":
                guess = min(x, y)
            else:
                guess = max(x, y)
            same = math.isfinite(guess) and bits(guess) == vector["old_twelfth_left_bits"]
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
        raise ThirteenthLayerError("unbounded thirteenth original JVM output")
    frames = [parts for line in stdout.splitlines()
              if (parts := line.split("|"))[0] in (HEAD, VALUE, END, FAIL)]
    if any(frame[0] == FAIL for frame in frames):
        raise ThirteenthLayerError("original bounded thirteenth JVM source reflection failed")
    old = prior.load()
    points = FINAL.input_rows()
    shapes: list[dict] = []
    vectors: list[dict] = []
    cursor = 0
    for group, seed in enumerate(FINAL.SEEDS):
        if cursor >= len(frames):
            raise ThirteenthLayerError("missing bounded source-owner thirteenth seed shape")
        header = frames[cursor]
        cursor += 1
        if len(header) != 3 + len(SHAPE_FIELDS) or header[:3] != [HEAD, str(group), seed]:
            raise ThirteenthLayerError("actual original thirteenth seed shape header drift")
        shape = dict(zip(SHAPE_FIELDS, header[3:], strict=True))
        shape["world_seed_bits"] = seed
        validate_shape(shape)
        shapes.append(shape)
        for j in range(32):
            index = group * 32 + j
            if cursor >= len(frames):
                raise ThirteenthLayerError("missing thirteenth original fixed XYZ point")
            record = frames[cursor]
            cursor += 1
            if (len(record) != 2 + len(WORDS)
                    or record[:2] != [VALUE, str(index)]
                    or not all(finite_bits(word) for word in record[2:])):
                raise ThirteenthLayerError("thirteenth genuine finite IEEE point frame invalid")
            actual = dict(zip(WORDS, ("0x" + w for w in record[2:]), strict=True))
            if actual["old_twelfth_left_bits"][2:] != old[index][0]:
                raise ThirteenthLayerError(
                    "immutable independently frozen twelfth MIN-left parent drift: "
                    + str(index)
                )
            vectors.append({**points[index], **actual})
        if cursor >= len(frames) or frames[cursor] != [END, str(group), "32"]:
            raise ThirteenthLayerError("actual original thirteenth 32-point seed terminator moved")
        cursor += 1
    if cursor != len(frames):
        raise ThirteenthLayerError("thirteenth original JVM emitted extra record frames")
    if any(
        {k: v for k, v in s.items() if k != "world_seed_bits"}
        != {k: v for k, v in shapes[0].items() if k != "world_seed_bits"}
        for s in shapes[1:]
    ):
        raise ThirteenthLayerError("real out-left Ap2 record changed across four seeds")
    return shapes, vectors


def validate(report: dict) -> None:
    if not isinstance(report, dict):
        raise ThirteenthLayerError("original thirteenth report must be JSON object")
    pins = {
        "schema": 1, "kind": KIND, "minecraft": "26.2",
        "protocol": 776, "data_version": 4903,
        "source_archive_sha256": FINAL.frozen.SOURCE_SHA256,
        "official_server_sha256": FINAL.frozen.SERVER_SHA256,
        "prior_twelfth_fixture_sha256": prior.SHA256,
        "prior_twelfth_report_sha256": prior.REPORT_SHA256,
        "source_methods": report.get("source_methods"),
        "world_seeds": list(FINAL.SEEDS),
        "point_count_per_seed": 32,
        "sample_context": "DensityFunction$SinglePointContext",
        "original_stock_registry_used": True,
        "new_thirteenth_selected_left_ap2_children_observed": True,
        "source_text_included": False,
        "arithmetic_candidate_telemetry": report.get("arithmetic_candidate_telemetry"),
        **{gate: False for gate in GATES},
    }
    if set(report) != set(pins) | {"shapes", "vectors"} or any(
        type(report.get(k)) is not type(v) or report[k] != v
        for k, v in pins.items()
    ):
        raise ThirteenthLayerError("original twelfth provenance/source/admission drift")
    methods = report["source_methods"]
    if not isinstance(methods, dict) or set(methods) != {
        "ap2_compute", "holder_holder_compute", "mapped_delegate_compute"
    }:
        raise ThirteenthLayerError("twelfth original source method inventory changed")
    for name in ("ap2_compute", "holder_holder_compute"):
        owner = methods[name]
        if (not isinstance(owner, dict)
                or owner.get("reviewed") is not False
                or tuple(owner.get(k) for k in (
                    "owner", "signature", "body_sha256", "normalized_sha256"
                )) != ROOT.frozen_final.METHODS[name]):
            raise ThirteenthLayerError("original indexed Java source method SHA moved")
    mapped = methods["mapped_delegate_compute"]
    if (not isinstance(mapped, dict)
            or mapped.get("reviewed") is not False
            or mapped.get("owner") != ROOT.PURE_TRANSFORMER
            or mapped.get("body_sha256") != ROOT.PURE_COMPUTE_SHA256):
        raise ThirteenthLayerError("actual mapped delegate source provenance moved")
    shapes, vectors = report.get("shapes"), report.get("vectors")
    if (not isinstance(shapes, list) or len(shapes) != 4
            or not isinstance(vectors, list) or len(vectors) != 128):
        raise ThirteenthLayerError("thirteenth actual 4x32 finite capture size moved")
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
                raise ThirteenthLayerError("thirteenth original XYZ/seed or field set altered")
            replay.append("|".join((VALUE, str(i), *(v[k][2:] for k in WORDS))))
        replay.append("|".join((END, str(group), "32")))
    candidate = candidate_telemetry(shapes, vectors)
    if (type(report["arithmetic_candidate_telemetry"]) is not dict
            or report["arithmetic_candidate_telemetry"] != candidate):
        raise ThirteenthLayerError("thirteenth sample-only candidate telemetry tampered")
    if parse_output("\n".join(replay)) != (shapes, vectors):
        raise ThirteenthLayerError("thirteenth source-free real record round-trip failed")


def observe(server: Path, timeout: int = 240) -> tuple[list[dict], list[dict]]:
    with tempfile.TemporaryDirectory(prefix="helve-26_2-thirteenth-layer-") as td:
        work = Path(td)
        jars = official.extract_classpath(server, work / "classpath")
        f = twelfth.eleventh.tenth.ninth.eighth.seventh.sixth.fifth
        sources = (
            f.fourth.third.second.final.roots.BASE_BRIDGE,
            f.fourth.third.second.final.JAVA_SOURCE,
            f.fourth.third.second.root.JAVA_SOURCE,
            f.fourth.third.second.inner.JAVA_SOURCE,
            f.fourth.third.second.JAVA_SOURCE,
            f.fourth.third.JAVA_SOURCE,
            f.fourth.JAVA_SOURCE,
            f.JAVA_SOURCE,
            twelfth.eleventh.tenth.ninth.eighth.seventh.sixth.JAVA_SOURCE,
            twelfth.eleventh.tenth.ninth.eighth.seventh.JAVA_SOURCE,
            twelfth.eleventh.tenth.ninth.eighth.JAVA_SOURCE,
            twelfth.eleventh.tenth.ninth.JAVA_SOURCE,
            twelfth.eleventh.tenth.JAVA_SOURCE,
            twelfth.eleventh.JAVA_SOURCE,
            twelfth.JAVA_SOURCE,
            JAVA_SOURCE,
        )
        if any(not path.is_file() for path in sources):
            raise ThirteenthLayerError("missing original source-free thirteenth bridge")
        build = subprocess.run(
            ["javac", "-encoding", "UTF-8", "-d", str(work),
             *(str(path) for path in sources)],
            capture_output=True, text=True, timeout=timeout, check=False
        )
        if build.returncode:
            raise ThirteenthLayerError("thirteenth bounded javac failed: " + build.stderr[:480])
        proc = subprocess.run(
            ["java", "-Xmx768m", "-cp",
             os.pathsep.join((str(work), *(str(jar) for jar in jars))),
             "HelveStockFinalDensityThirteenthLayer262", "--thirteenth-layer-128"],
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
            raise ThirteenthLayerError("real original thirteenth JVM failure: " + reason[:160])
        return parse_output(proc.stdout)


def capture(*, source: Path, db: Path, lock: Path,
            server: Path, output: Path) -> dict:
    dest = FINAL.improved.external_output(output)
    source_sha, server_sha, methods = (
        twelfth.eleventh.tenth.ninth.eighth.seventh.sixth.fifth.fourth.third.second.inner
        .source_provenance(source, db, lock, server)
    )
    shapes, vectors = observe(server)
    report = {
        "schema": 1, "kind": KIND, "minecraft": "26.2",
        "protocol": 776, "data_version": 4903,
        "source_archive_sha256": source_sha,
        "official_server_sha256": server_sha,
        "prior_twelfth_fixture_sha256": prior.SHA256,
        "prior_twelfth_report_sha256": prior.REPORT_SHA256,
        "source_methods": methods,
        "world_seeds": list(FINAL.SEEDS),
        "point_count_per_seed": 32,
        "sample_context": "DensityFunction$SinglePointContext",
        "original_stock_registry_used": True,
        "new_thirteenth_selected_left_ap2_children_observed": True,
        "source_text_included": False,
        "shapes": shapes, "vectors": vectors,
        "arithmetic_candidate_telemetry": candidate_telemetry(shapes, vectors),
        **{gate: False for gate in GATES},
    }
    validate(report)
    payload = (json.dumps(report, indent=2, sort_keys=True) + "\n").encode("ascii")
    if len(payload) > 115000:
        raise ThirteenthLayerError("unbounded thirteenth source-free report payload")
    dest.parent.mkdir(parents=True, exist_ok=True)
    with os.fdopen(os.open(dest, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600), "wb") as fp:
        fp.write(payload)
    return {
        "output": str(dest),
        "sha256": hashlib.sha256(payload).hexdigest(),
        "genuinely_new_thirteenth_ieee_words": len(vectors) * len(NEW_FIELDS),
        "old_twelfth_left_parent_words_anchored": len(vectors),
        "original_left_ap2_operation": shapes[0]["ap2_op"],
        "original_left_ap2_left_child_class": shapes[0]["ap2_left_class"],
        "original_left_ap2_right_child_class": shapes[0]["ap2_right_class"],
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
        ThirteenthLayerError, ValueError, TypeError, KeyError, IndexError, OSError,
        sqlite3.Error, subprocess.TimeoutExpired, urllib.error.URLError
    ) as exc:
        print("STOCK 26.2 THIRTEENTH LAYER OPEN: " + str(exc), file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
