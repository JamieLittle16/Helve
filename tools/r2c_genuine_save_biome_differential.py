#!/usr/bin/env python3
"""Independently compare every saved quart-biome cell with the production Rust 26.2 importer.

This is a persisted-save **name/cell** differential, NOT target biome registry-ID
qualification. A catalog built from names present in the official save is used only to
exercise the Rust name resolver; numeric IDs in that catalog are not claimed to be
vanilla registry IDs. Real target-ID order needs a separate source-bound registry gate.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import subprocess
import sys
from pathlib import Path

import vanilla_section_extractor as oracle

BIOME_CELLS = 64
TARGET = "26.2"
DIMENSION = "minecraft:overworld"
OVERWORLD_REGIONS = Path("dimensions/minecraft/overworld/region")
MAX_REGION_BYTES = 256 * 1024 * 1024


class BiomeDifferentialError(ValueError):
    """A saved-biome law, source identity, or cross-language differential failed."""


def decode_biome_cells(container: object) -> tuple[str, ...]:
    """Independent target-format saved quart-biome oracle with 64-cell YZX indexing."""
    compound = oracle._require_compound(container, "biomes")
    names = oracle._require_list(
        compound.get("palette"), "biomes.palette", element_type=8
    )
    if not 1 <= len(names) <= BIOME_CELLS:
        raise BiomeDifferentialError(f"saved biome palette size outside 1..64: {len(names)}")
    palette = [oracle._require_str(name, "biome resource key") for name in names]
    data = compound.get("data")
    if len(palette) == 1:
        if data is not None and (
            not isinstance(data, oracle.NbtLongArray) or data.values
        ):
            raise BiomeDifferentialError("uniform biome palette has nonempty or wrong-type data")
        return (palette[0],) * BIOME_CELLS
    if not isinstance(data, oracle.NbtLongArray):
        raise BiomeDifferentialError("nonuniform biome palette requires packed long array")
    bits = (len(palette) - 1).bit_length()
    per_word = 64 // bits
    expected_words = math.ceil(BIOME_CELLS / per_word)
    if len(data.values) != expected_words:
        raise BiomeDifferentialError(
            f"saved biome data words={len(data.values)}, expected={expected_words} for bits={bits}"
        )
    mask = (1 << bits) - 1
    result = []
    for index in range(BIOME_CELLS):
        word = data.values[index // per_word] & 0xFFFF_FFFF_FFFF_FFFF
        local_index = (word >> ((index % per_word) * bits)) & mask
        if local_index >= len(palette):
            raise BiomeDifferentialError(
                f"saved biome cell={index} references palette index={local_index} "
                f"outside cardinality={len(palette)}"
            )
        result.append(palette[local_index])
    return tuple(result)


def expected_region(
    path: Path, dimension: str
) -> tuple[list[str], set[str]]:
    """Parse region framing and NBT separately from Helve's Rust implementation."""
    rx, rz = oracle._region_coordinates(path)
    raw = path.read_bytes()
    if len(raw) < oracle.REGION_HEADER_BYTES or len(raw) > MAX_REGION_BYTES:
        raise BiomeDifferentialError(f"invalid bounded region length: {path}")
    if len(raw) % oracle.SECTOR_BYTES:
        raise BiomeDifferentialError(f"unaligned Anvil region: {path}")
    rows: list[str] = []
    biome_names: set[str] = set()
    for slot, (offset, count) in enumerate(oracle._region_locations(raw, path)):
        if offset == 0:
            continue
        x, z = rx * 32 + slot % 32, rz * 32 + slot // 32
        chunk = oracle.parse_nbt(oracle._chunk_payload(path, raw, x, z, offset, count))
        version = oracle._require_int(chunk.get("DataVersion"), "DataVersion")
        if version != oracle.TARGET_DATA_VERSION:
            raise BiomeDifferentialError(f"unexpected chunk DataVersion {version}")
        if (
            oracle._require_int(chunk.get("xPos"), "xPos"),
            oracle._require_int(chunk.get("zPos"), "zPos"),
        ) != (x, z):
            raise BiomeDifferentialError(f"region/chunk x-z mismatch at {x},{z}")
        sections = oracle._require_list(chunk.get("sections"), "sections", element_type=10)
        seen_y: set[int] = set()
        for raw_section in sections:
            section = oracle._require_compound(raw_section, "section")
            y = oracle._require_int(section.get("Y"), "section.Y")
            if y in seen_y:
                raise BiomeDifferentialError(f"duplicate section Y {y} at chunk {x},{z}")
            seen_y.add(y)
            if "biomes" not in section:
                continue
            cells = decode_biome_cells(section["biomes"])
            biome_names.update(cells)
            rows.append(f"BIOME|{dimension}|{x}|{z}|{y}|{','.join(cells)}")
    return sorted(rows), biome_names


def digest(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def run(
    world: Path, rust_emitter: Path, work_dir: Path, dimension: str, evidence: Path
) -> dict[str, object]:
    if dimension != DIMENSION:
        raise BiomeDifferentialError(f"unqualified biome differential dimension {dimension}")
    oracle.validate_level_dat(world)
    region_root = world / OVERWORLD_REGIONS
    regions = sorted(region_root.glob("r.*.*.mca"))
    if not regions:
        raise BiomeDifferentialError("official 26.2 save has no overworld region files")

    expected: dict[Path, list[str]] = {}
    region_digest: dict[str, str] = {}
    keys: set[str] = set()
    for region in regions:
        rows, observed = expected_region(region, dimension)
        expected[region] = rows
        keys.update(observed)
        region_digest[region.name] = digest(region.read_bytes())

    if not keys or not any(expected.values()):
        raise BiomeDifferentialError("official save has no persisted quart-biome cells")
    if len(keys) > 65_536:
        raise BiomeDifferentialError("saved biome name catalog exceeds compact ID bound")
    work_dir.mkdir(parents=True, exist_ok=True)
    catalog = "\n".join(sorted(keys)) + "\n"
    catalog_path = work_dir / "observed-save-keys.txt"
    catalog_path.write_text(catalog, encoding="utf-8")

    expected_rows: list[str] = []
    actual_rows: list[str] = []
    for index, region in enumerate(regions):
        output = work_dir / f"region-{index:04d}.rust-biomes.txt"
        subprocess.run(
            [str(rust_emitter.resolve()), dimension, str(region.resolve()),
             str(catalog_path.resolve()), str(output.resolve())],
            check=True,
            capture_output=True,
            text=True,
        )
        actual = sorted(output.read_text(encoding="utf-8").splitlines())
        if actual != expected[region]:
            for line_index, (left, right) in enumerate(
                zip(expected[region], actual, strict=False)
            ):
                if left != right:
                    raise BiomeDifferentialError(
                        f"region {region.name} mismatch at row {line_index}: "
                        f"expected={left[:220]} actual={right[:220]}"
                    )
            raise BiomeDifferentialError(
                f"region {region.name} count mismatch "
                f"oracle={len(expected[region])} production={len(actual)}"
            )
        expected_rows.extend(expected[region])
        actual_rows.extend(actual)

    expected_text = "\n".join(sorted(expected_rows)) + "\n"
    actual_text = "\n".join(sorted(actual_rows)) + "\n"
    if expected_text != actual_text:
        raise BiomeDifferentialError("aggregate saved-biome differential failed")
    result: dict[str, object] = {
        "schema": 1,
        "target": {"minecraft": TARGET, "data_version": oracle.TARGET_DATA_VERSION},
        "policy": "official-save-biome-names-and-quart-cells-v1",
        "source": "official-26.2-pregenerated-save",
        "region_sha256": region_digest,
        "biome_section_count": len(expected_rows),
        "biome_cell_count": len(expected_rows) * BIOME_CELLS,
        "distinct_observed_biome_names": len(keys),
        "observed_catalog_sha256": digest(catalog.encode("utf-8")),
        "oracle_semantic_sha256": digest(expected_text.encode("utf-8")),
        "production_semantic_sha256": digest(actual_text.encode("utf-8")),
        "registry_id_authority": "NOT_QUALIFIED_observed_names_only",
    }
    evidence.parent.mkdir(parents=True, exist_ok=True)
    evidence.write_text(json.dumps(result, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--world", type=Path, required=True)
    parser.add_argument("--rust-emitter", type=Path, required=True)
    parser.add_argument("--work-dir", type=Path, required=True)
    parser.add_argument("--dimension", default=DIMENSION)
    parser.add_argument("--evidence", type=Path, required=True)
    args = parser.parse_args()
    try:
        result = run(
            args.world, args.rust_emitter, args.work_dir, args.dimension, args.evidence
        )
    except (BiomeDifferentialError, oracle.ExtractorError, OSError,
            subprocess.CalledProcessError) as error:
        print(f"biome differential error: {error}", file=sys.stderr)
        return 2
    print(
        f"PASS: {result['biome_section_count']} exact saved biome sections, "
        f"{result['biome_cell_count']} quart cells, "
        f"{result['distinct_observed_biome_names']} distinct observed names; "
        "registry numeric IDs NOT qualified"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
