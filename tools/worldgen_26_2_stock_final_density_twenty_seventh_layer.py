#!/usr/bin/env python3
"""Twenty-seventh original Minecraft 26.2 source-owned IntervalSelect input/list observation.

Use 26th exact original instance declarations, observe actual
threshold rawbits and concrete function classes without assuming how
the selector chooses. Sample only 2 NEW input words for each original
XYZ, anchor both OLD IntervalSelect outputs to 25th immutable fixture.
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
import worldgen_26_2_stock_final_density_twenty_fourth_layer as previous_24
import worldgen_26_2_stock_final_density_twenty_fifth_layer as previous
import worldgen_26_2_stock_finaldensity_twenty_fifth_layer_fixture as prior_25
import worldgen_26_2_stock_finaldensity_twenty_fourth_layer_fixture as prior_fixture
import worldgen_26_2_stock_final_density_twenty_sixth_layer as previous_26
import worldgen_26_2_stock_finaldensity_twenty_sixth_declarations_receipt as prior_26

JAVA_SOURCE = Path(__file__).resolve().parent / (
    "worldgen_java/HelveStockFinalDensityTwentySeventhLayer262.java"
)
KIND = "original_26_2_finaldensity_twenty_seventh_two_intervalselect_input_and_lists_unadmitted"
HEAD = "HELVE26_2_TWENTY_SEVENTH_SHAPE"
VALUE = "HELVE26_2_TWENTY_SEVENTH_VALUE"
END = "HELVE26_2_TWENTY_SEVENTH_END"
FAIL = "HELVE26_2_TWENTY_SEVENTH_FAILURE"
SHAPE_FIELDS = (
    "first_selector_input_class", "first_selector_threshold_bits", "first_selector_function_classes",
    "second_selector_input_class", "second_selector_threshold_bits", "second_selector_function_classes",
)
NEW_FIELDS = ("first_selector_input_bits", "second_selector_input_bits")
OLD_FIELDS = ("old_first_interval_bits", "old_second_interval_bits")
WORDS = NEW_FIELDS + OLD_FIELDS
GATES = tuple(previous_26.GATES) + (
    "twenty_seventh_actual_interval_lists_and_inputs_qualified",
    "twenty_seventh_all_input_interval_selection_admitted",
)
CLASS = eighteenth.CLASS
FINAL = eighteenth.FINAL
ROOT = eighteenth.ROOT


class TwentySeventhLayerError(ValueError):
    """The original nineteenth 26.2 JVM source-owner evidence cannot be admitted."""


def finite_bits(word: str) -> bool:
    return eighteenth.finite_bits(word)


def value(word: str) -> float:
    return struct.unpack(">d", bytes.fromhex(word[2:]))[0]


def bits(number: float) -> str:
    return "0x" + struct.pack(">d", number).hex()


def validate_shape(s: dict) -> None:
    if not isinstance(s, dict) or set(s) != set(SHAPE_FIELDS) | {"world_seed_bits"}:
        raise TwentySeventhLayerError("actual IntervalSelect source list shape fields drift")
    for side in ("first", "second"):
        klass = s[side + "_selector_input_class"]
        if not isinstance(klass, str) or not re.fullmatch(
            r"net\.minecraft\.world\.level\.levelgen\.[A-Za-z_$][A-Za-z_$0-9]{0,150}",
            klass,
        ):
            raise TwentySeventhLayerError("actual original selector input class malformed")
        thresholds = s[side + "_selector_threshold_bits"].split(",")
        funcs = s[side + "_selector_function_classes"].split(",")
        if not 1 <= len(thresholds) <= 16 or not 1 <= len(funcs) <= 16:
            raise TwentySeventhLayerError("original selector list exceeds bounded window")
        if not all(finite_bits(word) for word in thresholds):
            raise TwentySeventhLayerError("invalid original threshold IEEE word")
        if not all(isinstance(name, str) and re.fullmatch(
            r"net\.minecraft\.world\.level\.levelgen\.[A-Za-z_$][A-Za-z_$0-9]{0,150}",
            name,
        ) for name in funcs):
            raise TwentySeventhLayerError("actual original function class malformed")


def candidate_telemetry(shapes: list[dict], vectors: list[dict]) -> dict:
    return {
        "original_bounded_points": len(vectors),
        "genuinely_new_selector_ieee_words": len(vectors) * len(NEW_FIELDS),
        "old_twenty_fifth_interval_anchors_matched": len(vectors) * len(OLD_FIELDS),
        "original_two_interval_list_shapes_observed": len(shapes),
        "source_law_admitted": False,
    }


def parse_output(stdout: str) -> tuple[list[dict], list[dict]]:
    if not isinstance(stdout, str) or len(stdout) > 100000:
        raise TwentySeventhLayerError("unbounded nineteenth original JVM output")
    frames = [parts for line in stdout.splitlines()
              if (parts := line.split("|"))[0] in (HEAD, VALUE, END, FAIL)]
    if any(frame[0] == FAIL for frame in frames):
        raise TwentySeventhLayerError("original bounded seventeenth JVM source reflection failed")
    old = prior_25.load()
    points = FINAL.input_rows()
    shapes: list[dict] = []
    vectors: list[dict] = []
    cursor = 0
    for group, seed in enumerate(FINAL.SEEDS):
        if cursor >= len(frames):
            raise TwentySeventhLayerError("missing bounded source-owner nineteenth seed shape")
        header = frames[cursor]
        cursor += 1
        if len(header) != 3 + len(SHAPE_FIELDS) or header[:3] != [HEAD, str(group), seed]:
            raise TwentySeventhLayerError("actual original nineteenth seed shape header drift")
        shape = dict(zip(SHAPE_FIELDS, header[3:], strict=True))
        shape["world_seed_bits"] = seed
        validate_shape(shape)
        shapes.append(shape)
        for j in range(32):
            index = group * 32 + j
            if cursor >= len(frames):
                raise TwentySeventhLayerError("missing nineteenth original fixed XYZ point")
            record = frames[cursor]
            cursor += 1
            if (len(record) != 2 + len(WORDS)
                    or record[:2] != [VALUE, str(index)]
                    or not all(finite_bits(word) for word in record[2:])):
                raise TwentySeventhLayerError("seventeenth genuine finite IEEE point frame invalid")
            actual = dict(zip(WORDS, ("0x" + w for w in record[2:]), strict=True))
            if tuple(actual[k][2:] for k in OLD_FIELDS) != old[index]:
                raise TwentySeventhLayerError(
                    "previous original 24th Mapped outputs drift at " + str(index)
                )
            vectors.append({**points[index], **actual})
        if cursor >= len(frames) or frames[cursor] != [END, str(group), "32"]:
            raise TwentySeventhLayerError("actual original nineteenth 32-point seed terminator moved")
        cursor += 1
    if cursor != len(frames):
        raise TwentySeventhLayerError("nineteenth original JVM emitted extra record frames")
    if any(
        {k: v for k, v in s.items() if k != "world_seed_bits"}
        != {k: v for k, v in shapes[0].items() if k != "world_seed_bits"}
        for s in shapes[1:]
    ):
        raise TwentySeventhLayerError("original actual seventeenth RIGHT Ap2 op/classes changed across four seeds")
    return shapes, vectors


def validate(report: dict) -> None:
    if not isinstance(report, dict):
        raise TwentySeventhLayerError("original nineteenth report must be JSON object")
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
        "prior_twenty_fourth_fixture_sha256": prior_fixture.FIXTURE_SHA256,
        "prior_twenty_fourth_report_sha256": prior_fixture.REPORT_SHA256,
        "prior_twenty_fifth_fixture_sha256": prior_25.FIXTURE_SHA256,
        "prior_twenty_fifth_report_sha256": prior_25.REPORT_SHA256,
        "prior_twenty_sixth_report_sha256": prior_26.REPORT_SHA256,
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
        "new_twenty_seventh_two_interval_input_lists_observed": True,
        "source_text_included": False,
        "interval_input_lists_candidate_telemetry": report.get("interval_input_lists_candidate_telemetry"),
        **{gate: False for gate in GATES},
    }
    if set(report) != set(pins) | {"shapes", "vectors"} or any(
        type(report.get(k)) is not type(v) or report[k] != v
        for k, v in pins.items()
    ):
        raise TwentySeventhLayerError("original nineteenth provenance/source/admission drift")
    methods = report["source_methods"]
    if not isinstance(methods, dict) or set(methods) != {
        "ap2_compute", "holder_holder_compute", "mapped_delegate_compute"
    }:
        raise TwentySeventhLayerError("nineteenth original source method inventory changed")
    for name in ("ap2_compute", "holder_holder_compute"):
        owner = methods[name]
        if (not isinstance(owner, dict)
                or owner.get("reviewed") is not False
                or tuple(owner.get(k) for k in (
                    "owner", "signature", "body_sha256", "normalized_sha256"
                )) != ROOT.frozen_final.METHODS[name]):
            raise TwentySeventhLayerError("original indexed Java source method SHA moved")
    mapped = methods["mapped_delegate_compute"]
    if (not isinstance(mapped, dict)
            or mapped.get("reviewed") is not False
            or mapped.get("owner") != ROOT.PURE_TRANSFORMER
            or mapped.get("body_sha256") != ROOT.PURE_COMPUTE_SHA256):
        raise TwentySeventhLayerError("actual mapped delegate source provenance moved")
    shapes, vectors = report.get("shapes"), report.get("vectors")
    if (not isinstance(shapes, list) or len(shapes) != 4
            or not isinstance(vectors, list) or len(vectors) != 128):
        raise TwentySeventhLayerError("nineteenth actual 4x32 finite capture size moved")
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
                raise TwentySeventhLayerError("nineteenth original XYZ/seed or field set altered")
            replay.append("|".join((VALUE, str(i), *(v[k][2:] for k in WORDS))))
        replay.append("|".join((END, str(group), "32")))
    candidate = candidate_telemetry(shapes, vectors)
    if (type(report["interval_input_lists_candidate_telemetry"]) is not dict
            or report["interval_input_lists_candidate_telemetry"] != candidate):
        raise TwentySeventhLayerError("nineteenth sample-only candidate telemetry tampered")
    if parse_output("\n".join(replay)) != (shapes, vectors):
        raise TwentySeventhLayerError("nineteenth source-free real record round-trip failed")


def observe(server: Path, timeout: int = 240) -> tuple[list[dict], list[dict]]:
    with tempfile.TemporaryDirectory(prefix="helve-26_2-twenty-seventh-layer-") as td:
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
            previous_24.JAVA_SOURCE,
            previous.JAVA_SOURCE,
            previous_26.JAVA_SOURCE,
            JAVA_SOURCE,
        )
        if any(not path.is_file() for path in sources):
            raise TwentySeventhLayerError("missing original source-free nineteenth bridge")
        build = subprocess.run(
            ["javac", "-encoding", "UTF-8", "-d", str(work),
             *(str(path) for path in sources)],
            capture_output=True, text=True, timeout=timeout, check=False
        )
        if build.returncode:
            raise TwentySeventhLayerError("nineteenth bounded javac failed: " + build.stderr[:480])
        proc = subprocess.run(
            ["java", "-Xmx768m", "-cp",
             os.pathsep.join((str(work), *(str(jar) for jar in jars))),
             "HelveStockFinalDensityTwentySeventhLayer262", "--twenty-seventh-layer-128"],
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
            raise TwentySeventhLayerError("real original nineteenth JVM failure: " + reason[:160])
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
        "prior_twenty_fourth_fixture_sha256": prior_fixture.FIXTURE_SHA256,
        "prior_twenty_fourth_report_sha256": prior_fixture.REPORT_SHA256,
        "prior_twenty_fifth_fixture_sha256": prior_25.FIXTURE_SHA256,
        "prior_twenty_fifth_report_sha256": prior_25.REPORT_SHA256,
        "prior_twenty_sixth_report_sha256": prior_26.REPORT_SHA256,
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
        "new_twenty_seventh_two_interval_input_lists_observed": True,
        "source_text_included": False,
        "shapes": shapes, "vectors": vectors,
        "interval_input_lists_candidate_telemetry": candidate_telemetry(shapes, vectors),
        **{gate: False for gate in GATES},
    }
    validate(report)
    payload = (json.dumps(report, indent=2, sort_keys=True) + "\n").encode("ascii")
    if len(payload) > 115000:
        raise TwentySeventhLayerError("unbounded nineteenth source-free report payload")
    dest.parent.mkdir(parents=True, exist_ok=True)
    with os.fdopen(os.open(dest, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600), "wb") as fp:
        fp.write(payload)
    return {
        "output": str(dest),
        "sha256": hashlib.sha256(payload).hexdigest(),
        "new_real_selector_ieee_words": len(vectors) * len(NEW_FIELDS),
        "old_original_interval_output_words": len(vectors) * len(OLD_FIELDS),
        "first_selector_input_class": shapes[0]["first_selector_input_class"],
        "first_selector_threshold_bits": shapes[0]["first_selector_threshold_bits"],
        "first_selector_function_classes": shapes[0]["first_selector_function_classes"],
        "second_selector_input_class": shapes[0]["second_selector_input_class"],
        "second_selector_threshold_bits": shapes[0]["second_selector_threshold_bits"],
        "second_selector_function_classes": shapes[0]["second_selector_function_classes"],
        "interval_input_lists_candidate_telemetry": candidate_telemetry(shapes, vectors),
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
        TwentySeventhLayerError, ValueError, TypeError, KeyError, IndexError, OSError,
        sqlite3.Error, subprocess.TimeoutExpired, urllib.error.URLError
    ) as exc:
        print("STOCK 26.2 TWENTY SEVENTH LAYER OPEN: " + str(exc), file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
