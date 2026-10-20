#!/usr/bin/env python3
"""Source-locked, *direct-seeded* official 26.2 Noise density JVM oracle.

This is a deliberately bounded next frontier. It constructs an official
NormalNoise from RandomSource.create(seed) and places that noise inside the
actual DensityFunction.NoiseHolder / DensityFunctions.Noise runtime records.
It uses Minecraft's own Noise.compute on integer block XYZ coordinates.

This is NOT RandomState seed binding, NoiseRouter, biome/surface parity, a
source-reviewed delegate or a production-admitted generator. Constructor
shapes are runtime-checked and fail closed if they differ in the pinned jar.
No original Minecraft code, jar, archive or private source is redistributed.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sqlite3
import subprocess
import sys
import tempfile
import tomllib
import urllib.error
from pathlib import Path

import official_state_data as official
import r1b_configuration_source_probe as source_probe
import r2c_world_projection_source_review as projection
import vanilla_atlas
import worldgen_26_2_density_primitive_capture as primitive
import worldgen_26_2_improved_noise_capture as improved
import worldgen_26_2_perlin_normal_capture as family

KIND = "official_26_2_direct_seeded_noise_density_candidate"
STAGE = "direct_seeded_noise_density_not_random_state"
PREFIX = "HELVE26_2_DIRECT_NOISE_DENSITY|"
ROOT = "net.minecraft.world.level.levelgen."
NOISE_OWNER = ROOT + "DensityFunctions$Noise"
NOISE_FACTORY = ROOT + "DensityFunctions"
NORMAL_OWNER = ROOT + "synth.NormalNoise"
SOURCE_LOCKED_METHODS = {
    "density_noise_compute": (NOISE_OWNER, "compute(final DensityFunction . FunctionContext context)",
        "bbef25d12896f0895c6fbec4523095fe3c1f42a3ece3229dfebdad793adbe9fe"),
    "density_noise_factory": (NOISE_FACTORY,
        "noise(final Holder < NormalNoise . NoiseParameters > noiseData , final double xzScale , final double yScale)",
        "410456eefd7a1364a89705b96c7b31fd0f044c4b017eb521264370d2bdd424f9"),
    "normal_create": family.EXPECTED["normal_noise"]["create"],
    "normal_get_value": family.EXPECTED["normal_noise"]["get_value_3"],
}
PROFILES = {
    "unit": ["0x3ff0000000000000", "0x3ff0000000000000"],
    "quarter_xz": ["0x3fd0000000000000", "0x3ff0000000000000"],
    "quarter_xz_half_y": ["0x3fd0000000000000", "0x3fe0000000000000"],
}
SEEDS = primitive.SEEDS
N_COORDS = 32
N_RECORDS = len(PROFILES) * len(SEEDS) * N_COORDS
HASH = re.compile(r"[0-9a-f]{64}\Z")
BITS = re.compile(r"0x[0-9a-f]{16}\Z")


class DirectNoiseCaptureError(ValueError):
    """Requested direct noise path is not evidenced by the pinned 26.2 JVM."""


def inputs() -> list[dict[str, object]]:
    base = primitive.inputs()[:N_COORDS]
    return [
        {"profile": profile, "seed_bits": seed, "block_x": point["block_x"],
         "block_y": point["block_y"], "block_z": point["block_z"]}
        for profile in PROFILES for seed in SEEDS for point in base
    ]


def source_methods(conn: sqlite3.Connection) -> dict[str, dict[str, str]]:
    rows_cache: dict[str, dict[str, sqlite3.Row]] = {}
    result: dict[str, dict[str, str]] = {}
    for label, (owner, signature, fingerprint) in SOURCE_LOCKED_METHODS.items():
        if owner not in rows_cache:
            indexed = projection._exact_type_methods(conn, owner, 128)
            names = [str(r["signature"]) for r in indexed]
            if len(names) != len(set(names)):
                raise DirectNoiseCaptureError("duplicate Atlas source methods on " + owner)
            rows_cache[owner] = {str(r["signature"]): r for r in indexed}
        row = rows_cache[owner].get(signature)
        if row is None:
            raise DirectNoiseCaptureError(f"exact 26.2 source method absent: {label}")
        meta = source_probe.record_template(conn, row, "INDEX-WORLDGEN-262-NOISE-" + label.upper())
        source = meta["source"]
        if source["type"] != owner or source["signature"] != signature:
            raise DirectNoiseCaptureError("Atlas source identity disagreement")
        if source["body_sha256"] != fingerprint or not HASH.fullmatch(source["normalized_sha256"]):
            raise DirectNoiseCaptureError(f"pinned source fingerprint changed: {label}")
        result[label] = {"owner": owner, "signature": signature, "body_sha256": fingerprint,
                         "normalized_sha256": source["normalized_sha256"]}
    return result


JAVA_PROBE = r"""import java.io.*;
import java.lang.reflect.*;
import java.nio.charset.StandardCharsets;
import java.util.*;
public final class HelveDirectSeededNoiseDensityBits {
  private static final PrintStream RESULT = new PrintStream(
      new FileOutputStream(FileDescriptor.out), true, StandardCharsets.US_ASCII);
  static long parseBits(String raw) {
    if (!raw.matches("0x[0-9a-f]{16}")) throw new IllegalArgumentException("not raw long bits");
    return Long.parseUnsignedLong(raw.substring(2), 16);
  }
  static double decode(String raw) { return Double.longBitsToDouble(parseBits(raw)); }
  static Method staticMethod(Class<?> owner, String name, Class<?> result, Class<?>... args)
      throws Exception {
    Method m=owner.getMethod(name,args);
    if (!Modifier.isStatic(m.getModifiers()) || m.getReturnType()!=result)
      throw new IllegalStateException("unexpected official 26.2 static declaration "+name);
    return m;
  }
  static void startup() throws Exception {
    Class<?> constants=Class.forName("net.minecraft.SharedConstants");
    Method version=constants.getMethod("tryDetectVersion");
    if (!Modifier.isStatic(version.getModifiers())) throw new IllegalStateException("version method");
    version.invoke(null);
    Class<?> boot=Class.forName("net.minecraft.server.Bootstrap");
    Method method=boot.getMethod("bootStrap");
    if (!Modifier.isStatic(method.getModifiers())) throw new IllegalStateException("bootstrap");
    method.invoke(null);
  }
  public static void main(String[] ignored) throws Exception {
    startup();
    Class<?> random=Class.forName("net.minecraft.util.RandomSource");
    Class<?> normal=Class.forName("net.minecraft.world.level.levelgen.synth.NormalNoise");
    Class<?> noiseParameters=Class.forName(
        "net.minecraft.world.level.levelgen.synth.NormalNoise$NoiseParameters");
    Class<?> doubleList=Class.forName("it.unimi.dsi.fastutil.doubles.DoubleList");
    Class<?> doubleArray=Class.forName("it.unimi.dsi.fastutil.doubles.DoubleArrayList");
    Class<?> holder=Class.forName("net.minecraft.core.Holder");
    Class<?> noiseHolder=Class.forName(
        "net.minecraft.world.level.levelgen.DensityFunction$NoiseHolder");
    Class<?> density=Class.forName("net.minecraft.world.level.levelgen.DensityFunction");
    Class<?> context=Class.forName(
        "net.minecraft.world.level.levelgen.DensityFunction$FunctionContext");
    Class<?> point=Class.forName(
        "net.minecraft.world.level.levelgen.DensityFunction$SinglePointContext");
    Class<?> noiseNode=Class.forName(
        "net.minecraft.world.level.levelgen.DensityFunctions$Noise");

    Method createRandom=staticMethod(random,"create",random,long.class);
    Method createNormal=staticMethod(normal,"create",normal,random,int.class,double[].class);
    Method wrap=doubleArray.getMethod("wrap",double[].class);
    Method direct=holder.getMethod("direct",Object.class);
    Constructor<?> parametersCtor=noiseParameters.getDeclaredConstructor(int.class,doubleList);
    Constructor<?> noiseHolderCtor=noiseHolder.getDeclaredConstructor(holder,normal);
    Constructor<?> nodeCtor=noiseNode.getDeclaredConstructor(noiseHolder,double.class,double.class);
    Constructor<?> pointCtor=point.getDeclaredConstructor(int.class,int.class,int.class);
    Method compute=noiseNode.getMethod("compute",context);
    if (!Modifier.isStatic(wrap.getModifiers()) || !Modifier.isStatic(direct.getModifiers())
        || compute.getReturnType()!=double.class
        || !density.isAssignableFrom(noiseNode)) {
      throw new IllegalStateException("26.2 runtime signature mismatch in direct noise");
    }
    for (Constructor<?> c:new Constructor<?>[]{parametersCtor,noiseHolderCtor,nodeCtor,pointCtor})
      c.setAccessible(true);
    // The official family oracle already verifies the same -3/4-amplitude
    // direct RandomSource -> NormalNoise construction independently.
    double[] amplitudes=new double[]{1.0,0.0,0.5,1.0};
    Object list=wrap.invoke(null,(Object)amplitudes);
    Object parameters=parametersCtor.newInstance(-3,list);
    Object parameterHolder=direct.invoke(null,parameters);
    Map<String,Object> nodes=new HashMap<>();
    BufferedReader reader=new BufferedReader(
        new InputStreamReader(System.in,StandardCharsets.US_ASCII));
    String line;
    int count=0;
    while ((line=reader.readLine())!=null) {
      String[] v=line.split("\t",-1);
      if (v.length!=5 || ++count>480) throw new IllegalStateException("invalid row count/shape");
      double xzScale,yScale;
      switch(v[0]) {
        case "unit": xzScale=1.0; yScale=1.0; break;
        case "quarter_xz": xzScale=0.25; yScale=1.0; break;
        case "quarter_xz_half_y": xzScale=0.25; yScale=0.5; break;
        default: throw new IllegalStateException("unknown direct noise scale profile");
      }
      String key=v[0]+"/"+v[1];
      Object densityNode=nodes.get(key);
      if (densityNode==null) {
        Object rng=createRandom.invoke(null,parseBits(v[1]));
        Object officialNoise=createNormal.invoke(null,rng,-3,(Object)amplitudes);
        Object held=noiseHolderCtor.newInstance(parameterHolder,officialNoise);
        densityNode=nodeCtor.newInstance(held,xzScale,yScale);
        nodes.put(key,densityNode);
      }
      Object at=pointCtor.newInstance(
          Integer.parseInt(v[2]),Integer.parseInt(v[3]),Integer.parseInt(v[4]));
      double value=(Double)compute.invoke(densityNode,at);
      RESULT.println("HELVE26_2_DIRECT_NOISE_DENSITY|"+(count-1)+"|"+
          String.format(Locale.ROOT,"%016x",Double.doubleToRawLongBits(value)));
    }
    if (count!=480) throw new IllegalStateException("incomplete direct noise probe");
  }
}
"""


def parse_output(output: str, *, count: int = N_RECORDS) -> list[str]:
    if len(output) > 300_000 or len(output.splitlines()) > 1024:
        raise DirectNoiseCaptureError("unbounded official JVM output")
    tagged = [line for line in output.splitlines() if line.startswith(PREFIX)]
    if len(tagged) != count:
        raise DirectNoiseCaptureError(f"official JVM emitted {len(tagged)} tagged values, expected {count}")
    bits: list[str] = []
    for i, line in enumerate(tagged):
        parts = line.split("|")
        if len(parts) != 3 or parts[0] != PREFIX[:-1] or parts[1] != str(i) \
            or re.fullmatch(r"[0-9a-f]{16}", parts[2]) is None:
            raise DirectNoiseCaptureError(f"changed exact official raw-bit row at {i}")
        bits.append("0x" + parts[2])
    return bits


def runtime_bits(server: Path, rows: list[dict[str, object]], *, timeout: int = 120) -> list[str]:
    if len(rows) != N_RECORDS:
        raise DirectNoiseCaptureError("incorrect requested direct noise row count")
    with tempfile.TemporaryDirectory(prefix="helve-direct-noise-density-262-") as folder:
        work = Path(folder)
        classpath = official.extract_classpath(server, work / "classpath")
        java=work/"HelveDirectSeededNoiseDensityBits.java"
        java.write_text(JAVA_PROBE, encoding="utf-8")
        compiled=subprocess.run(["javac","-encoding","UTF-8","-d",str(work),str(java)],
                                text=True,capture_output=True,check=False,timeout=timeout)
        if compiled.returncode:
            raise DirectNoiseCaptureError("JVM direct noise probe failed to compile: "+compiled.stderr[:1400])
        request="\n".join(
            f"{v['profile']}\t{v['seed_bits']}\t{v['block_x']}\t{v['block_y']}\t{v['block_z']}"
            for v in rows
        )+"\n"
        run=subprocess.run(
            ["java","-Xmx512m","-cp",os.pathsep.join([str(work),*(str(p) for p in classpath)]),
             "HelveDirectSeededNoiseDensityBits"],
            input=request,text=True,capture_output=True,check=False,timeout=timeout,
        )
        if run.returncode:
            raise DirectNoiseCaptureError("official 26.2 direct seeded density path is NOT confirmed: "+
                                         run.stderr[:1500])
        return parse_output(run.stdout)


def validate(manifest: dict, lock: dict) -> None:
    expected_fields={
        "schema","kind","stage","minecraft","protocol","data_version",
        "source_archive_sha256","official_server_sha256","source_methods",
        "runtime_startup_sequence","profiles","seeds","rng_construction",
        "noise_construction","world_seed_random_state_bound","vectors",
        "source_text_included","independent_var_sem_admitted","production_worldgen_enabled",
    }
    if not isinstance(manifest,dict) or set(manifest)!=expected_fields:
        raise DirectNoiseCaptureError("invalid direct noise manifest schema")
    fixed={
        "schema":1,"kind":KIND,"stage":STAGE,"minecraft":"26.2","protocol":776,
        "data_version":4903,
        "source_archive_sha256":lock["source"]["archive_sha256"],
        "official_server_sha256":lock["runtime"]["server_sha256"],
        "runtime_startup_sequence":primitive.STARTUP_SEQUENCE,
        "profiles":PROFILES,"seeds":list(SEEDS),
        "rng_construction":"RandomSource.create(long) direct; NOT world RandomState",
        "noise_construction":"NormalNoise.create(RandomSource,-3,[1,0,0.5,1]) to NoiseHolder/Noise constructor",
        "world_seed_random_state_bound":False,
        "source_text_included":False,"independent_var_sem_admitted":False,
        "production_worldgen_enabled":False,
    }
    for key,want in fixed.items():
        if type(manifest.get(key)) is not type(want) or manifest[key]!=want:
            raise DirectNoiseCaptureError(f"invalid source or admission field: {key}")
    methods=manifest["source_methods"]
    if not isinstance(methods,dict) or set(methods)!=set(SOURCE_LOCKED_METHODS):
        raise DirectNoiseCaptureError("wrong pinned delegate methods")
    for label,(owner,signature,fingerprint) in SOURCE_LOCKED_METHODS.items():
        v=methods[label]
        if not isinstance(v,dict) or set(v)!={"owner","signature","body_sha256","normalized_sha256"} \
            or v["owner"]!=owner or v["signature"]!=signature or v["body_sha256"]!=fingerprint \
            or not isinstance(v["normalized_sha256"],str) or HASH.fullmatch(v["normalized_sha256"]) is None:
            raise DirectNoiseCaptureError(f"unbound source method identity: {label}")
    records=manifest["vectors"]
    wanted=inputs()
    if not isinstance(records,list) or len(records)!=len(wanted):
        raise DirectNoiseCaptureError("incomplete direct noise vectors")
    for index,(actual,req) in enumerate(zip(records,wanted,strict=True)):
        if not isinstance(actual,dict) or set(actual)!={*req,"value_bits"} \
            or any(type(actual[k]) is not type(x) or actual[k]!=x for k,x in req.items()) \
            or not isinstance(actual["value_bits"],str) or BITS.fullmatch(actual["value_bits"]) is None:
            raise DirectNoiseCaptureError(f"bad exact raw bit vector {index}")


def capture(*, source: Path, db: Path, lock: Path, server: Path, output: Path) -> dict:
    target=improved.external_output(output)
    with lock.open("rb") as stream:
        pin=tomllib.load(stream)
    if (pin.get("minecraft"),pin.get("protocol"),pin.get("data_version"))!=("26.2",776,4903):
        raise DirectNoiseCaptureError("not the locked 26.2 server target")
    conn=vanilla_atlas.connect_db(db)
    try:
        source_sha=source_probe.require_pinned_source(conn,source,lock)
        methods=source_methods(conn)
    finally:
        conn.close()
    runtime_sha=official.sha256_file(server)
    if runtime_sha!=pin["runtime"]["server_sha256"]:
        raise DirectNoiseCaptureError("unrecognised official 26.2 server jar")
    requested=inputs()
    observed=runtime_bits(server,requested)
    manifest={
        "schema":1,"kind":KIND,"stage":STAGE,"minecraft":"26.2",
        "protocol":776,"data_version":4903,"source_archive_sha256":source_sha,
        "official_server_sha256":runtime_sha,"source_methods":methods,
        "runtime_startup_sequence":primitive.STARTUP_SEQUENCE,
        "profiles":PROFILES,"seeds":list(SEEDS),
        "rng_construction":"RandomSource.create(long) direct; NOT world RandomState",
        "noise_construction":"NormalNoise.create(RandomSource,-3,[1,0,0.5,1]) to NoiseHolder/Noise constructor",
        "world_seed_random_state_bound":False,
        "source_text_included":False,"independent_var_sem_admitted":False,
        "production_worldgen_enabled":False,
        "vectors":[dict(r,value_bits=b) for r,b in zip(requested,observed,strict=True)],
    }
    validate(manifest,pin)
    payload=(json.dumps(manifest,sort_keys=True,indent=2)+"\n").encode()
    target.parent.mkdir(parents=True,exist_ok=True)
    fd=os.open(target,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
    with os.fdopen(fd,"wb") as writer:
        writer.write(payload)
    return {"output":str(target),"rows":N_RECORDS,"source_free_sha256":hashlib.sha256(payload).hexdigest(),
            "world_seed_random_state_bound":False,"production_worldgen_enabled":False}


def main(argv: list[str] | None = None) -> int:
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--source",type=Path,default=primitive.SOURCE)
    p.add_argument("--db",type=Path,default=primitive.DB)
    p.add_argument("--lock",type=Path,default=primitive.LOCK)
    p.add_argument("--cache",type=Path,default=primitive.CACHE)
    p.add_argument("--server-jar",type=Path)
    p.add_argument("--output",type=Path,required=True)
    args=p.parse_args(argv)
    try:
        server=args.server_jar
        if server is None:
            resolved,_=official.resolve("26.2",args.cache)
            server=resolved["server"][0]
        print(json.dumps(capture(source=args.source,db=args.db,lock=args.lock,
                                 server=server,output=args.output),sort_keys=True))
    except (DirectNoiseCaptureError, OSError, ValueError, TypeError, KeyError, sqlite3.Error,
            projection.DiscoveryError,source_probe.ProbeError,
            subprocess.TimeoutExpired,urllib.error.URLError) as exc:
        print(f"OFFICIAL 26.2 DIRECT-SEEDED NOISE DENSITY NOT CAPTURED: {exc}",file=sys.stderr)
        return 2
    return 0


if __name__=="__main__":
    raise SystemExit(main())
