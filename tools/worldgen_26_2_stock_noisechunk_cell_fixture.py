#!/usr/bin/env python3
"""Freeze first authentic 26.2 NoiseChunk-bound finalDensity single-cell bits.

Exact user-origin stock JVM capture: 16 samples, four original seeds × four
interpolated positions, one 4×8×4 stock NoiseChunk cell. This is original
numeric REFERENCE evidence, NOT Rust parity, full interpolation lifecycle,
every NoiseChunk cache mode or production worldgen.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

import worldgen_26_2_stock_noisechunk_cell_capture as cell
import worldgen_26_2_stock_final_density_singlepoint_fixture as scalar_fixture

ROOT=Path(__file__).resolve().parents[1]
FIXTURE=ROOT/"vanilla/reports/worldgen-26_2-stock-noisechunk-cell-16-bits.txt"
FIXTURE_SHA256="aa65bf127ecbf17864f35fbef177afbd4c6c0d90331566017427a0a053409289"
ORIGINAL_JSON_BYTES=8485
ORIGINAL_JSON_SHA256="3ea20f5ed1b1236f5e166a847e5405ca54169d39f98810e0c8bf7029e3e74169"
HEX16=re.compile(r"[0-9a-f]{16}\Z")
WRAPPED="net.minecraft.world.level.levelgen.DensityFunctions$Ap2"

# Exact original 26.2 private-source indexed fingerprints, recorded as
# reviewed:false. These SHA-256s are NOT evidence of manual semantic review.
# tuple = (exact method signature, source body hash, normalized source hash)
METHOD_PINS={
    "chunk_advance":(
        "advanceCellX(final int cellXIndex)",
        "4dc23b071c6146745b1ab8269a39b2b7801a79bfb10eb6153318c58650710b10",
        "156b50fa2ee57500b6476c31d38207928dfc0b0b9e6bacd0cc4d3548e84f46e6"),
    "chunk_initialize":(
        "initializeForFirstCellX()",
        "663c9298e098bacd2cc7f41faec9b150f566d12b8132613e73579d04eed26c62",
        "41e4aa5c2e25e23ba41413dad6e96cf96d0646823cd6bde3af86e8fdd9e1ecc3"),
    "chunk_select":(
        "selectCellYZ(final int cellYIndex , final int cellZIndex)",
        "5d3f42f21060e6b5369be4e19ee8378acb9091d10f73d029dc316ed611bc7882",
        "395f9547d38454a4a704f7ccc042ce669c4ae7fd80f4de6726ebe26900332fc1"),
    "chunk_stop":(
        "stopInterpolation()",
        "73cb8fdb828573f9fd19878773af0d659957d84a66510ffc559894ac2eab564f",
        "003a36114fa83fcaf63ad89cd2fb26c33b8545ac908847ba09b42e64e3534102"),
    "chunk_update_x":(
        "updateForX(final int posX , final double factorX)",
        "328a27b3e96826e07817ff95b906784ed330111b94bd80cc5a855a391883e258",
        "cf73e2ef05a65a1d4eb34bcc189c6e96ef1e6ab020763f3d66425b7feb0c0ba2"),
    "chunk_update_y":(
        "updateForY(final int posY , final double factorY)",
        "e62b92771d9c23c0a1d6d5c743b12ec561542b982da3359fb1e5aa344f1532e4",
        "31bb751e792b72281d89190e81bfa66a4a709ae947959c156fa6e3be3643ebc3"),
    "chunk_update_z":(
        "updateForZ(final int posZ , final double factorZ)",
        "aa31e0a974ae1b1cf897a4c715d9efb1bd5358cae830201ea292f0309d03b03a",
        "ee3d8ca309527fd43bf379ceaa1f2c0ec27f1bf8b8d617b7fb653c0e099689e0"),
    "chunk_wrap":(
        "wrap(final DensityFunction function)",
        "1bb3d2eda7872596df93f488ffedf00e9af6ed05407f005c4078eae3065264a4",
        "c8a7a19f6b2b112f0e3c5675b31025e00489affba6df1b5bd677001c62758527"),
    "global_fluid_picker":(
        "createFluidPicker(final NoiseGeneratorSettings settings)",
        "0d29f1c39b92672b86c16389fc7249e2c6f5e17a0c83965f269fd1b49718782e",
        "0c17c8271f46b707dab425200956a1ae609f038a1dd9abc25903b68ca856423d"),
}


class FrozenNoiseChunkError(ValueError):
    """Authentic bounded stock NoiseChunk reference cannot be certified."""


def load_bits(path:Path=FIXTURE)->tuple[str,...]:
    raw=path.read_bytes()
    if len(raw)!=16*17 or hashlib.sha256(raw).hexdigest()!=FIXTURE_SHA256:
        raise FrozenNoiseChunkError("real original NoiseChunk rawbit fixture size/SHA changed")
    try:
        lines=raw.decode("ascii").splitlines(keepends=True)
    except UnicodeDecodeError as exc:
        raise FrozenNoiseChunkError("non-ASCII stock NoiseChunk original fixture") from exc
    if len(lines)!=16:
        raise FrozenNoiseChunkError("expected exactly 16 genuine stock cell bit words")
    bits=[]
    for i,line in enumerate(lines):
        if len(line)!=17 or line[-1]!="\n" or not HEX16.fullmatch(line[:-1]) or \
           ((int(line[:-1],16)>>52)&0x7ff)==0x7ff:
            raise FrozenNoiseChunkError("invalid original NoiseChunk IEEE bitword at "+str(i))
        bits.append(line[:-1])
    return tuple(bits)


def source_methods()->dict:
    observed={}
    if {name for name,_,_,_ in cell.METHODS}!=set(METHOD_PINS):
        raise FrozenNoiseChunkError("actual original NoiseChunk source method inventory changed")
    for label,owner,method,arity in cell.METHODS:
        signature,body,normal=METHOD_PINS[label]
        observed[label]={
            "owner":owner,"signature":signature,"body_sha256":body,
            "normalized_sha256":normal,"reviewed":False,
        }
    return observed


def validate_manifest(manifest:dict,bits:tuple[str,...])->None:
    methods=source_methods()
    if not isinstance(manifest,dict) or manifest.get("source_methods")!=methods:
        raise FrozenNoiseChunkError("stock NoiseChunk source-owner/method fingerprint changed")
    try:
        cell.validate(manifest,methods)
    except (cell.NoiseChunkCellError,KeyError,ValueError,TypeError) as exc:
        raise FrozenNoiseChunkError("original source-free NoiseChunk manifest/closed gate changed") from exc
    if manifest.get("wrapped_classes")!=[WRAPPED]*4:
        raise FrozenNoiseChunkError("stock finalDensity NoiseChunk wrapped root identity changed")
    if len(bits)!=16 or len(manifest["vectors"])!=16:
        raise FrozenNoiseChunkError("expected four seeds by four original chunk points")
    for i,(row,bit) in enumerate(zip(manifest["vectors"],bits,strict=True)):
        if row["value_bits"]!="0x"+bit:
            raise FrozenNoiseChunkError("mismatched authentic NoiseChunk rawbits at "+str(i))
    # The only overlapping coordinate: (0,64,0) on all four seeds.
    # Comparison proves exact bits ONLY for that point, not general
    # equivalence between SinglePointContext and NoiseChunk.
    scalar=scalar_fixture.load_bits()
    for i in range(4):
        if bits[i*4]!=scalar[i*32+3]:
            raise FrozenNoiseChunkError("genuine stock context overlap mismatch for seed "+str(i))


def validate_original_capture(path:Path)->None:
    raw=path.read_bytes()
    if len(raw)!=ORIGINAL_JSON_BYTES or hashlib.sha256(raw).hexdigest()!=ORIGINAL_JSON_SHA256:
        raise FrozenNoiseChunkError("original 8,485-byte stock NoiseChunk JSON bytes/SHA changed")
    try:
        data=json.loads(raw)
    except (ValueError,UnicodeError) as exc:
        raise FrozenNoiseChunkError("invalid original stock NoiseChunk JSON receipt") from exc
    validate_manifest(data,load_bits())


def main(argv:list[str]|None=None)->int:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--capture",type=Path,
                        help="Authenticate exact uncommitted original stock 8485-byte JSON receipt")
    args=parser.parse_args(argv)
    try:
        bits=load_bits()
        if args.capture is not None:
            validate_original_capture(args.capture)
        scalar=scalar_fixture.load_bits()
        if any(bits[i*4]!=scalar[i*32+3] for i in range(4)):
            raise FrozenNoiseChunkError("stock context intersection no longer exact")
    except (FrozenNoiseChunkError,scalar_fixture.FrozenFinalDensityError,OSError) as exc:
        print("STOCK 26.2 NOISECHUNK FROZEN CELL UNQUALIFIED: "+str(exc),file=sys.stderr)
        return 2
    print(json.dumps({
        "reference":"original_26_2_stock_NoiseChunk_single_cell",
        "vectors":16,"seeds":4,"overlapping_singlepoint_exact_match":4,
        "bit_fixture_sha256":FIXTURE_SHA256,
        "original_official_capture_sha256":ORIGINAL_JSON_SHA256,
        "stock_noisechunk_cell_reference_frozen":True,
        "stock_noisechunk_full_lifecycle_qualified":False,
        "rust_router_numeric_parity_qualified":False,
        "independent_var_sem_admitted":False,
        "production_worldgen_enabled":False,
    },sort_keys=True))
    return 0


if __name__=="__main__":
    raise SystemExit(main())
