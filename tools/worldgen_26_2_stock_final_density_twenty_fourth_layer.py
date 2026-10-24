#!/usr/bin/env python3
"""24th original JVM side frontier: left operand of genuine nineteenth ADD.

Read the actual 19th ADD(Ap2,MulOrAdd) left Ap2's operation,
child classes, two new IEEE words and independent old-left parent
from sealed 19th source fixture. All admission gates stay false.
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
import worldgen_26_2_stock_final_density_eighteenth_layer as eighteenth
import worldgen_26_2_stock_finaldensity_eighteenth_layer_receipt as prior
import worldgen_26_2_stock_finaldensity_seventeenth_layer_fixture as seventeenth_fixture
import worldgen_26_2_stock_final_density_nineteenth_layer as nineteenth
import worldgen_26_2_stock_finaldensity_nineteenth_layer_fixture as old_nineteenth
import worldgen_26_2_stock_finaldensity_twenty_third_parameters_receipt as previous_parameters

JAVA_SOURCE = Path(__file__).resolve().parent / (
    "worldgen_java/HelveStockFinalDensityTwentyFourthLayer262.java"
)
KIND = "original_26_2_finaldensity_twenty_fourth_nineteenth_left_ap2_children_unadmitted"
HEAD = "HELVE26_2_TWENTY_FOURTH_SHAPE"
VALUE = "HELVE26_2_TWENTY_FOURTH_VALUE"
END = "HELVE26_2_TWENTY_FOURTH_END"
FAIL = "HELVE26_2_TWENTY_FOURTH_FAILURE"
SHAPE_FIELDS = ("left_ap2_enum_class", "left_ap2_op", "left_ap2_left_class", "left_ap2_right_class")
NEW_FIELDS = ("left_ap2_first_child_bits", "left_ap2_second_child_bits")
OLD_FIELDS = ("old_nineteenth_left_bits",)
WORDS = NEW_FIELDS + OLD_FIELDS
GATES = tuple(nineteenth.GATES) + (
    "twenty_fourth_nineteenth_left_ap2_children_qualified",
    "twenty_fourth_all_input_left_ap2_law_admitted",
)
CLASS = eighteenth.CLASS
FINAL = eighteenth.FINAL
ROOT = eighteenth.ROOT


class TwentyFourthLayerError(ValueError):
    """The original nineteenth 26.2 JVM source-owner evidence cannot be admitted."""


def finite_bits(word: str) -> bool:
    return eighteenth.finite_bits(word)


def value(word: str) -> float:
    return struct.unpack(">d", bytes.fromhex(word[2:]))[0]


def bits(number: float) -> str:
    return "0x" + struct.pack(">d", number).hex()


def validate_shape(s: dict) -> None:
    if not isinstance(s, dict) or set(s) != set(SHAPE_FIELDS) | {"world_seed_bits"}:
        raise TwentyFourthLayerError("original nineteenth real Ap2 record fields moved")
    if s["left_ap2_enum_class"] != CLASS + "TwoArgumentSimpleFunction$Type":
        raise TwentyFourthLayerError("actual nineteenth Ap2 enum class drift")
    if s["left_ap2_op"] not in ("ADD", "MUL", "MIN", "MAX"):
        raise TwentyFourthLayerError("real original nineteenth Ap2 op unknown")
    for field in ("left_ap2_left_class", "left_ap2_right_class"):
        try:
            eighteenth.seventeenth.sixteenth.fifteenth.fourteenth.thirteenth.twelfth.eleventh.tenth.ninth.eighth.seventh.sixth.fifth.fourth.third.second.require_class(s[field])
        except (ValueError, TypeError) as exc:
            raise TwentyFourthLayerError("actual 19th Ap2 child class malformed") from exc


def candidate_telemetry(shapes: list[dict], vectors: list[dict]) -> dict:
    """FINITE sample candidate; never promotes all-input original-JVM law."""
    mismatch = []
    smaller_left = smaller_right = ties = 0
    for i, v in enumerate(vectors):
        a = value(v["left_ap2_first_child_bits"])
        b = value(v["left_ap2_second_child_bits"])
        op = shapes[i // 32]["left_ap2_op"]
        smaller_left += a < b
        smaller_right += a > b
        ties += a == b
        try:
            if op == "ADD":
                result = a + b
            elif op == "MUL":
                result = a * b
            elif op == "MIN":
                result = min(a, b)
            else:
                result = max(a, b)
            equal = math.isfinite(result) and bits(result) == v["old_nineteenth_left_bits"]
        except (OverflowError, ValueError):
            equal = False
        if not equal:
            mismatch.append(i)
    return {
        "original_bounded_points": len(vectors),
        "arithmetic_candidate_mismatches": len(mismatch),
        "arithmetic_candidate_first_mismatch_index": mismatch[0] if mismatch else -1,
        "observed_left_strictly_less": smaller_left,
        "observed_right_strictly_less": smaller_right,
        "observed_equal_operands": ties,
        "source_law_admitted": False,
    }


def parse_output(stdout: str) -> tuple[list[dict], list[dict]]:
    if not isinstance(stdout, str) or len(stdout) > 100000:
        raise TwentyFourthLayerError("unbounded nineteenth original JVM output")
    frames = [parts for line in stdout.splitlines()
              if (parts := line.split("|"))[0] in (HEAD, VALUE, END, FAIL)]
    if any(frame[0] == FAIL for frame in frames):
        raise TwentyFourthLayerError("original bounded seventeenth JVM source reflection failed")
    old = old_nineteenth.load()
    points = FINAL.input_rows()
    shapes: list[dict] = []
    vectors: list[dict] = []
    cursor = 0
    for group, seed in enumerate(FINAL.SEEDS):
        if cursor >= len(frames):
            raise TwentyFourthLayerError("missing bounded source-owner nineteenth seed shape")
        header = frames[cursor]
        cursor += 1
        if len(header) != 3 + len(SHAPE_FIELDS) or header[:3] != [HEAD, str(group), seed]:
            raise TwentyFourthLayerError("actual original nineteenth seed shape header drift")
        shape = dict(zip(SHAPE_FIELDS, header[3:], strict=True))
        shape["world_seed_bits"] = seed
        validate_shape(shape)
        shapes.append(shape)
        for j in range(32):
            index = group * 32 + j
            if cursor >= len(frames):
                raise TwentyFourthLayerError("missing nineteenth original fixed XYZ point")
            record = frames[cursor]
            cursor += 1
            if (len(record) != 2 + len(WORDS)
                    or record[:2] != [VALUE, str(index)]
                    or not all(finite_bits(word) for word in record[2:])):
                raise TwentyFourthLayerError("seventeenth genuine finite IEEE point frame invalid")
            actual = dict(zip(WORDS, ("0x" + w for w in record[2:]), strict=True))
            if actual["old_nineteenth_left_bits"][2:] != old[index][0]:
                raise TwentyFourthLayerError(
                    "independently reconstructed genuine eighteenth raw Ap2 inner parent drift at: "
                    + str(index)
                )
            vectors.append({**points[index], **actual})
        if cursor >= len(frames) or frames[cursor] != [END, str(group), "32"]:
            raise TwentyFourthLayerError("actual original nineteenth 32-point seed terminator moved")
        cursor += 1
    if cursor != len(frames):
        raise TwentyFourthLayerError("nineteenth original JVM emitted extra record frames")
    if any(
        {k: v for k, v in s.items() if k != "world_seed_bits"}
        != {k: v for k, v in shapes[0].items() if k != "world_seed_bits"}
        for s in shapes[1:]
    ):
        raise TwentyFourthLayerError("original actual seventeenth RIGHT Ap2 op/classes changed across four seeds")
    return shapes, vectors


def validate(report: dict) -> None:
    if not isinstance(report, dict):
        raise TwentyFourthLayerError("original nineteenth report must be JSON object")
    pins = {
        "schema": 1, "kind": KIND, "minecraft": "26.2",
        "protocol": 776, "data_version": 4903,
        "source_archive_sha256": FINAL.frozen.SOURCE_SHA256,
        "official_server_sha256": FINAL.frozen.SERVER_SHA256,
        "prior_thirteenth_fixture_sha256": seventeenth_fixture.prior.prior.SHA256,
        "prior_sixteenth_fixture_sha256": seventeenth_fixture.prior.SHA256,
        "prior_seventeenth_fixture_sha256": seventeenth_fixture.SHA256,
        "prior_eighteenth_override_fixture_sha256": prior.SHA256,
        "prior_nineteenth_two_new_fixture_sha256": old_nineteenth.SHA256,
        "prior_nineteenth_report_sha256": old_nineteenth.REPORT_SHA256,
        "prior_twenty_third_report_sha256": previous_parameters.REPORT_SHA256,
        "prior_fourteenth_report_sha256": seventeenth_fixture.prior.receipt.owner.previous.REPORT_SHA256,
        "prior_fifteenth_report_sha256": seventeenth_fixture.prior.receipt.REPORT_SHA256,
        "prior_sixteenth_report_sha256": seventeenth_fixture.prior.REPORT_SHA256,
        "prior_seventeenth_report_sha256": seventeenth_fixture.REPORT_SHA256,
        "prior_eighteenth_report_sha256": prior.REPORT_SHA256,
        "prior_thirteenth_report_sha256": seventeenth_fixture.prior.prior.REPORT_SHA256,
        "source_methods": report.get("source_methods"),
        "world_seeds": list(FINAL.SEEDS),
        "point_count_per_seed": 32,
        "sample_context": "DensityFunction$SinglePointContext",
        "original_stock_registry_used": True,
        "new_twenty_fourth_nineteenth_left_ap2_children_observed": True,
        "source_text_included": False,
        "left_ap2_arithmetic_candidate_telemetry": report.get("left_ap2_arithmetic_candidate_telemetry"),
        **{gate: False for gate in GATES},
    }
    if set(report) != set(pins) | {"shapes", "vectors"} or any(
        type(report.get(k)) is not type(v) or report[k] != v
        for k, v in pins.items()
    ):
        raise TwentyFourthLayerError("original nineteenth provenance/source/admission drift")
    methods = report["source_methods"]
    if not isinstance(methods, dict) or set(methods) != {
        "ap2_compute", "holder_holder_compute", "mapped_delegate_compute"
    }:
        raise TwentyFourthLayerError("nineteenth original source method inventory changed")
    for name in ("ap2_compute", "holder_holder_compute"):
        owner = methods[name]
        if (not isinstance(owner, dict)
                or owner.get("reviewed") is not False
                or tuple(owner.get(k) for k in (
                    "owner", "signature", "body_sha256", "normalized_sha256"
                )) != ROOT.frozen_final.METHODS[name]):
            raise TwentyFourthLayerError("original indexed Java source method SHA moved")
    mapped = methods["mapped_delegate_compute"]
    if (not isinstance(mapped, dict)
            or mapped.get("reviewed") is not False
            or mapped.get("owner") != ROOT.PURE_TRANSFORMER
            or mapped.get("body_sha256") != ROOT.PURE_COMPUTE_SHA256):
        raise TwentyFourthLayerError("actual mapped delegate source provenance moved")
    shapes, vectors = report.get("shapes"), report.get("vectors")
    if (not isinstance(shapes, list) or len(shapes) != 4
            or not isinstance(vectors, list) or len(vectors) != 128):
        raise TwentyFourthLayerError("nineteenth actual 4x32 finite capture size moved")
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
                raise TwentyFourthLayerError("nineteenth original XYZ/seed or field set altered")
            replay.append("|".join((VALUE, str(i), *(v[k][2:] for k in WORDS))))
        replay.append("|".join((END, str(group), "32")))
    candidate = candidate_telemetry(shapes, vectors)
    if (type(report["left_ap2_arithmetic_candidate_telemetry"]) is not dict
            or report["left_ap2_arithmetic_candidate_telemetry"] != candidate):
        raise TwentyFourthLayerError("nineteenth sample-only candidate telemetry tampered")
    if parse_output("\n".join(replay)) != (shapes, vectors):
        raise TwentyFourthLayerError("nineteenth source-free real record round-trip failed")


def observe(server: Path, timeout: int = 240) -> tuple[list[dict], list[dict]]:
    with tempfile.TemporaryDirectory(prefix="helve-26_2-twenty-fourth-layer-") as td:
        work = Path(td)
        jars = official.extract_classpath(server, work / "classpath")
        f = eighteenth.seventeenth.sixteenth.fifteenth.fourteenth.thirteenth.twelfth.eleventh.tenth.ninth.eighth.seventh.sixth.fifth
        sources = (
            f.fourth.third.second.final.roots.BASE_BRIDGE,
            f.fourth.third.second.final.JAVA_SOURCE,
            f.fourth.third.second.root.JAVA_SOURCE,
            f.fourth.third.second.inner.JAVA_SOURCE,
            f.fourth.third.second.JAVA_SOURCE,
            f.fourth.third.JAVA_SOURCE,
            f.fourth.JAVA_SOURCE,
            f.JAVA_SOURCE,
            eighteenth.seventeenth.sixteenth.fifteenth.fourteenth.thirteenth.twelfth.eleventh.tenth.ninth.eighth.seventh.sixth.JAVA_SOURCE,
            eighteenth.seventeenth.sixteenth.fifteenth.fourteenth.thirteenth.twelfth.eleventh.tenth.ninth.eighth.seventh.JAVA_SOURCE,
            eighteenth.seventeenth.sixteenth.fifteenth.fourteenth.thirteenth.twelfth.eleventh.tenth.ninth.eighth.JAVA_SOURCE,
            eighteenth.seventeenth.sixteenth.fifteenth.fourteenth.thirteenth.twelfth.eleventh.tenth.ninth.JAVA_SOURCE,
            eighteenth.seventeenth.sixteenth.fifteenth.fourteenth.thirteenth.twelfth.eleventh.tenth.JAVA_SOURCE,
            eighteenth.seventeenth.sixteenth.fifteenth.fourteenth.thirteenth.twelfth.eleventh.JAVA_SOURCE,
            eighteenth.seventeenth.sixteenth.fifteenth.fourteenth.thirteenth.twelfth.JAVA_SOURCE,
            eighteenth.seventeenth.sixteenth.fifteenth.fourteenth.thirteenth.JAVA_SOURCE,
            eighteenth.seventeenth.sixteenth.fifteenth.fourteenth.JAVA_SOURCE,
            eighteenth.seventeenth.sixteenth.fifteenth.JAVA_SOURCE,
            eighteenth.seventeenth.sixteenth.JAVA_SOURCE,
            eighteenth.seventeenth.JAVA_SOURCE,
            eighteenth.JAVA_SOURCE,
            JAVA_SOURCE,
        )
        if any(not path.is_file() for path in sources):
            raise TwentyFourthLayerError("missing original source-free nineteenth bridge")
        build = subprocess.run(
            ["javac", "-encoding", "UTF-8", "-d", str(work),
             *(str(path) for path in sources)],
            capture_output=True, text=True, timeout=timeout, check=False
        )
        if build.returncode:
            raise TwentyFourthLayerError("nineteenth bounded javac failed: " + build.stderr[:480])
        proc = subprocess.run(
            ["java", "-Xmx768m", "-cp",
             os.pathsep.join((str(work), *(str(jar) for jar in jars))),
             "HelveStockFinalDensityTwentyFourthLayer262", "--twenty-fourth-layer-128"],
            input="\n".join(
                f"{p['world_seed_bits']}\t{p['block_x']}\t{p['block_y']}\t{p['block_z']}"
                for p in FINAL.input_rows()
            ) + "\n",
            capture_output=True, text=True, timeout=timeout, check=False,
        )
        if proc.returncode:
            reason = next(
                (line for line in proc.stdout.splitlines() if line.startswith(FAIL)),
                "no bounded original nineteenth failure tag"
            )
            raise TwentyFourthLayerError("real original nineteenth JVM failure: " + reason[:160])
        return parse_output(proc.stdout)


def capture(*, source: Path, db: Path, lock: Path,
            server: Path, output: Path) -> dict:
    dest = FINAL.improved.external_output(output)
    source_sha, server_sha, methods = (
        eighteenth.seventeenth.sixteenth.fifteenth.fourteenth.thirteenth.twelfth.eleventh.tenth.ninth.eighth.seventh.sixth.fifth.fourth.third.second.inner
        .source_provenance(source, db, lock, server)
    )
    shapes, vectors = observe(server)
    report = {
        "schema": 1, "kind": KIND, "minecraft": "26.2",
        "protocol": 776, "data_version": 4903,
        "source_archive_sha256": source_sha,
        "official_server_sha256": server_sha,
        "prior_thirteenth_fixture_sha256": seventeenth_fixture.prior.prior.SHA256,
        "prior_sixteenth_fixture_sha256": seventeenth_fixture.prior.SHA256,
        "prior_seventeenth_fixture_sha256": seventeenth_fixture.SHA256,
        "prior_eighteenth_override_fixture_sha256": prior.SHA256,
        "prior_nineteenth_two_new_fixture_sha256": old_nineteenth.SHA256,
        "prior_nineteenth_report_sha256": old_nineteenth.REPORT_SHA256,
        "prior_twenty_third_report_sha256": previous_parameters.REPORT_SHA256,
        "prior_fourteenth_report_sha256": seventeenth_fixture.prior.receipt.owner.previous.REPORT_SHA256,
        "prior_fifteenth_report_sha256": seventeenth_fixture.prior.receipt.REPORT_SHA256,
        "prior_sixteenth_report_sha256": seventeenth_fixture.prior.REPORT_SHA256,
        "prior_seventeenth_report_sha256": seventeenth_fixture.REPORT_SHA256,
        "prior_eighteenth_report_sha256": prior.REPORT_SHA256,
        "prior_thirteenth_report_sha256": seventeenth_fixture.prior.prior.REPORT_SHA256,
        "source_methods": methods,
        "world_seeds": list(FINAL.SEEDS),
        "point_count_per_seed": 32,
        "sample_context": "DensityFunction$SinglePointContext",
        "original_stock_registry_used": True,
        "new_twenty_fourth_nineteenth_left_ap2_children_observed": True,
        "source_text_included": False,
        "shapes": shapes, "vectors": vectors,
        "left_ap2_arithmetic_candidate_telemetry": candidate_telemetry(shapes, vectors),
        **{gate: False for gate in GATES},
    }
    validate(report)
    payload = (json.dumps(report, indent=2, sort_keys=True) + "\n").encode("ascii")
    if len(payload) > 115000:
        raise TwentyFourthLayerError("unbounded nineteenth source-free report payload")
    dest.parent.mkdir(parents=True, exist_ok=True)
    with os.fdopen(os.open(dest, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600), "wb") as fp:
        fp.write(payload)
    return {
        "output": str(dest),
        "sha256": hashlib.sha256(payload).hexdigest(),
        "genuinely_new_twenty_fourth_ieee_words": len(vectors) * len(NEW_FIELDS),
        "independent_old_nineteenth_left_parent_words": len(vectors),
        "original_left_ap2_enum_class": shapes[0]["left_ap2_enum_class"],
        "original_left_ap2_op": shapes[0]["left_ap2_op"],
        "original_left_ap2_left_class": shapes[0]["left_ap2_left_class"],
        "original_left_ap2_right_class": shapes[0]["left_ap2_right_class"],
        "left_ap2_arithmetic_candidate_telemetry": candidate_telemetry(shapes, vectors),
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
        TwentyFourthLayerError, ValueError, TypeError, KeyError, IndexError, OSError,
        sqlite3.Error, subprocess.TimeoutExpired, urllib.error.URLError
    ) as exc:
        print("STOCK 26.2 TWENTY FOURTH LAYER OPEN: " + str(exc), file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
