"""Fail-closed real 26.2 NoiseChunk cell numerical transport tests."""
from __future__ import annotations

import copy
import json
import shutil
import sqlite3
import struct
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import worldgen_26_2_stock_noisechunk_cell_capture as cell  # noqa: E402
import worldgen_26_2_stock_noisechunk_complete_cell_capture as grid  # noqa: E402


class StockNoiseChunkCellTests(unittest.TestCase):
    def methods(self):
        return {
            label:{
                "owner":owner,"signature":name+"("+str(arity)+")",
                "body_sha256":"a"*64,"normalized_sha256":"b"*64,
                "reviewed":False,
            }
            for label,owner,name,arity in cell.METHODS
        }

    def manifest(self,values,classes):
        return {
            "schema":1,"kind":cell.KIND,"minecraft":"26.2","protocol":776,
            "data_version":4903,
            "source_archive_sha256":cell.frozen.SOURCE_SHA256,
            "official_server_sha256":cell.frozen.SERVER_SHA256,
            "original_singlepoint_oracle_sha256":
                cell.scalar_fixture.ORIGINAL_JSON_SHA256,
            "source_methods":self.methods(),"world_seeds":list(cell.SEEDS),
            "points":[list(p) for p in cell.POINTS],
            "cell_geometry":{"width":4,"height":8,"min_y":-64,
                             "world_height":384,"cell_x":0,"cell_y":16,"cell_z":0},
            "sample_context":"NoiseChunk","stock_registry_used":True,
            "stock_noisechunk_cell_observed":True,
            "stock_noisechunk_full_lifecycle_qualified":False,
            "world_seed_random_state_bound":False,
            "full_router_graph_qualified":False,
            "router_numeric_parity_qualified":False,
            "independent_var_sem_admitted":False,
            "source_text_included":False,
            "production_worldgen_enabled":False,
            "wrapped_classes":classes,
            "vectors":[dict(row,value_bits=bit)
                       for row,bit in zip(cell.input_rows(),values,strict=True)],
        }

    def frame(self):
        lines=["stock boot stdout"]
        for i,seed in enumerate(cell.SEEDS):
            lines.append(cell.TAG_HEAD+f"|{i}|{seed}|4|8|-64|384|"
                         "net.minecraft.world.level.levelgen.DensityFunctions$Ap2|4")
            for j,(x,y,z) in enumerate(cell.POINTS):
                value=(float(x+y+z))
                bits=struct.pack(">d",value).hex()
                lines.append(cell.TAG_BITS+f"|{4*i+j}|{bits}")
            lines.append(cell.TAG_END+f"|{i}|4")
        return lines

    def test_frames_and_shapes_and_all_16_raw_results(self):
        values,classes=cell.parse_output("\n".join(self.frame()))
        self.assertEqual(len(values),16)
        self.assertEqual(len(classes),4)
        self.assertEqual(values[0],"0x4050000000000000")
        self.assertEqual(values[3],"0x4052400000000000")
        cell.validate(self.manifest(values,classes),self.methods())

    def test_fail_closed_for_missing_duplicate_reordered_nonfinite_and_false_shape(self):
        lines=self.frame()
        first=next(i for i,l in enumerate(lines) if l.startswith(cell.TAG_BITS+"|0|"))
        attacks=(
            lines[:first]+lines[first+1:],
            lines[:first]+[lines[first]]+lines[first:],
            lines[:-1],
            lines+[lines[-1]],
            [s.replace("|0|","|40|",1) if i==first else s
             for i,s in enumerate(lines)],
            [s.replace("|4|8|-64|384|","|4|16|-64|384|")
             if s.startswith(cell.TAG_HEAD) else s for s in lines],
            [s.replace("DensityFunctions$Ap2","java.lang.Object")
             if s.startswith(cell.TAG_HEAD) else s for s in lines],
            [cell.TAG_BITS+"|0|7ff8000000000000" if i==first else s
             for i,s in enumerate(lines)],
        )
        for i,attempt in enumerate(attacks):
            with self.subTest(i=i):
                self.assertNotEqual(attempt,lines)
                with self.assertRaises(cell.NoiseChunkCellError):
                    cell.parse_output("\n".join(attempt))
        with self.assertRaisesRegex(cell.NoiseChunkCellError,"JVM PHASE"):
            cell.parse_output(cell.TAG_FAILURE+
                              "|original-NoiseChunk-interpolate-0-2|"
                              "java.lang.IllegalStateException|"
                              "java.lang.reflect.InvocationTargetException|wrong cell order")

    def test_rejects_all_admission_flags_and_mutated_coordinates(self):
        values,classes=cell.parse_output("\n".join(self.frame()))
        m=self.manifest(values,classes)
        for flag in (
            "stock_noisechunk_full_lifecycle_qualified",
            "world_seed_random_state_bound","full_router_graph_qualified",
            "router_numeric_parity_qualified","independent_var_sem_admitted",
            "source_text_included","production_worldgen_enabled",
        ):
            bad=copy.deepcopy(m);bad[flag]=True
            with self.subTest(flag=flag),self.assertRaises(cell.NoiseChunkCellError):
                cell.validate(bad,self.methods())
        for changed in (
            lambda x:x["vectors"][7].__setitem__("block_x",19),
            lambda x:x["vectors"][7].__setitem__("value_bits","0x7ff0000000000000"),
            lambda x:x["vectors"].reverse(),
            lambda x:x["source_methods"].clear(),
            lambda x:x["wrapped_classes"].append("net.minecraft.Fake"),
            lambda x:x.__setitem__("sample_context","DensityFunction$SinglePointContext"),
            lambda x:x.__setitem__("original_singlepoint_oracle_sha256","0"*64),
        ):
            bad=copy.deepcopy(m);changed(bad)
            with self.assertRaises(cell.NoiseChunkCellError):
                cell.validate(bad,self.methods())

    def test_indexed_source_methods_not_claimed_as_reviewed(self):
        conn=sqlite3.connect(":memory:")
        conn.row_factory=sqlite3.Row
        conn.executescript("""
            CREATE TABLE types(id INTEGER PRIMARY KEY,qualified_name TEXT);
            CREATE TABLE methods(id INTEGER PRIMARY KEY,type_id INTEGER,
                name TEXT,signature TEXT,param_count INTEGER,
                body_sha256 TEXT,normalized_sha256 TEXT);
        """)
        for i,(label,owner,name,arity) in enumerate(cell.METHODS,1):
            conn.execute("INSERT INTO types VALUES(?,?)",(i,owner))
            conn.execute("INSERT INTO methods VALUES(?,?,?,?,?,?,?)",
                         (i,i,name,name+"()",arity,"a"*64,"b"*64))
        report=cell.source_methods(conn)
        self.assertEqual(len(report),len(cell.METHODS))
        self.assertFalse(any(v["reviewed"] for v in report.values()))
        conn.execute("UPDATE methods SET body_sha256='bad' WHERE id=1")
        with self.assertRaises(cell.NoiseChunkCellError):
            cell.source_methods(conn)
        conn.close()

    @unittest.skipUnless(shutil.which("javac") and shutil.which("java"),
                         "JDK needed for source-free stock contract transport")
    def test_original_bridge_uses_noisechunk_not_singlepoint_in_compiled_toy(self):
        with tempfile.TemporaryDirectory(prefix="helve-noisechunk-toy-") as td:
            work=Path(td);src=work/"java"
            def java(package,name,body):
                p=src/package.replace(".","/")/(name+".java")
                p.parent.mkdir(parents=True,exist_ok=True)
                p.write_text("package "+package+";\n"+body+"\n")
            java("net.minecraft","SharedConstants",
                 "public class SharedConstants{"
                 "public static void tryDetectVersion(){} }")
            java("net.minecraft.server","Bootstrap",
                 "public class Bootstrap{public static void bootStrap(){"
                 "System.setOut(new java.io.PrintStream("
                 "new java.io.ByteArrayOutputStream()));}}")
            java("net.minecraft.resources","ResourceKey",
                 "public record ResourceKey(String name) {}")
            java("net.minecraft.core","HolderGetter",
                 "public interface HolderGetter{interface Provider{"
                 "default HolderGetter lookupOrThrow("
                 "net.minecraft.resources.ResourceKey k){return new HolderGetter(){};}}"
                 "default Holder getOrThrow(net.minecraft.resources.ResourceKey k){"
                 "return new Holder.Direct(new net.minecraft.world.level.levelgen."
                 "NoiseGeneratorSettings(new net.minecraft.world.level.levelgen."
                 "NoiseSettings(-64,384,4,8)));}}")
            java("net.minecraft.core","HolderLookup",
                 "public interface HolderLookup{interface Provider extends "
                 "net.minecraft.core.HolderGetter.Provider{}}")
            java("net.minecraft.core","Holder",
                 "public interface Holder<T>{T value();"
                 "record Direct<T>(T value) implements Holder<T>{}}")
            java("net.minecraft.core.registries","Registries",
                 "public class Registries{public static final "
                 "net.minecraft.resources.ResourceKey NOISE_SETTINGS="
                 "new net.minecraft.resources.ResourceKey(\"NOISE_SETTINGS\");}")
            java("net.minecraft.data.registries","VanillaRegistries",
                 "public class VanillaRegistries{public static "
                 "net.minecraft.core.HolderLookup.Provider createLookup(){"
                 "return new net.minecraft.core.HolderLookup.Provider(){};}}")
            level="net.minecraft.world.level.levelgen"
            java(level,"NoiseSettings",
                 "public record NoiseSettings(int minY,int height,"
                 "int noiseSizeHorizontal,int noiseSizeVertical){"
                 "public int getCellWidth(){return noiseSizeHorizontal;}"
                 "public int getCellHeight(){return noiseSizeVertical;}}")
            java(level,"NoiseGeneratorSettings",
                 "public record NoiseGeneratorSettings(NoiseSettings noiseSettings){"
                 "public static final net.minecraft.resources.ResourceKey OVERWORLD="
                 "new net.minecraft.resources.ResourceKey(\"OVERWORLD\");}")
            java(level,"DensityFunction",
                 "public interface DensityFunction{"
                 "double compute(FunctionContext c);"
                 "interface FunctionContext{int blockX();int blockY();int blockZ();}}")
            java(level,"DensityFunctions",
                 "public class DensityFunctions{"
                 "public interface BeardifierOrMarker{}"
                 # Match official stock 26.2: package-private nested enum,
                 # although its generated INSTANCE field is public.
                 "enum BeardifierMarker implements BeardifierOrMarker{INSTANCE;}"
                 "public record Ap2() implements DensityFunction{"
                 "public double compute(DensityFunction.FunctionContext c){"
                 "return c.blockX()+c.blockY()+c.blockZ();}}}")
            java(level,"Aquifer",
                 "public interface Aquifer{interface FluidPicker{}}")
            java(level,"NoiseBasedChunkGenerator",
                 "public class NoiseBasedChunkGenerator{"
                 "private static Aquifer.FluidPicker createFluidPicker("
                 "NoiseGeneratorSettings s){return new Aquifer.FluidPicker(){};}}")
            java(level+".blending","Blender",
                 "public class Blender{public static Blender empty(){"
                 "return new Blender();}}")
            java(level,"NoiseRouter",
                 "public record NoiseRouter(DensityFunction finalDensity){}")
            java(level,"RandomState",
                 "public class RandomState{public static RandomState create("
                 "net.minecraft.core.HolderGetter.Provider p,"
                 "net.minecraft.resources.ResourceKey k,long seed){"
                 "return new RandomState();}"
                 "public NoiseRouter router(){return new NoiseRouter("
                 "new DensityFunctions.Ap2());}}")
            java(level,"NoiseChunk",
                 "public class NoiseChunk implements DensityFunction.FunctionContext{"
                 "private int x,y,z;private boolean started,advanced,selected;"
                 "public NoiseChunk(int count,RandomState state,int startX,int startZ,"
                 "NoiseSettings noise,DensityFunctions.BeardifierOrMarker beard,"
                 "NoiseGeneratorSettings settings,Aquifer.FluidPicker picker,"
                 "net.minecraft.world.level.levelgen.blending.Blender b){"
                 "if(count!=4||startX!=0||startZ!=0)throw new RuntimeException();}"
                 "protected DensityFunction wrap(DensityFunction d){return d;}"
                 "public void initializeForFirstCellX(){started=true;}"
                 "public void advanceCellX(int i){if(!started||i!=0)"
                 "throw new IllegalStateException();advanced=true;}"
                 "public void selectCellYZ(int i,int j){"
                 "if(!advanced||i!=16||j!=0)throw new IllegalStateException();"
                 "selected=true;}"
                 "public void updateForY(int v,double frac){"
                 "if(!selected)throw new IllegalStateException();y=v;}"
                 "public void updateForX(int v,double frac){x=v;}"
                 "public void updateForZ(int v,double frac){z=v;}"
                 "public void stopInterpolation(){}"
                 "public int blockX(){return x;}"
                 "public int blockY(){return y;}"
                 "public int blockZ(){return z;}}")
            output=work/"classes"
            compiled=subprocess.run(
                ["javac","-encoding","UTF-8","-d",str(output),
                 *[str(p) for p in src.rglob("*.java")]],
                capture_output=True,text=True,check=False,timeout=45,
            )
            self.assertEqual(compiled.returncode,0,compiled.stderr)
            with mock.patch.object(cell.official,"extract_classpath",
                                   return_value=[output]):
                values,wrappers=cell.observe(work/"toy.jar",timeout=90)
                complete=grid.observe(work/"toy.jar",timeout=90)
            self.assertEqual(values,cell.parse_output("\n".join(self.frame()))[0])
            self.assertEqual(wrappers,[level+".DensityFunctions$Ap2"]*4)
            self.assertEqual(len(complete),512)
            self.assertEqual(complete[0],"0x"+struct.pack(">d",64.0).hex())
            self.assertEqual(complete[127],"0x"+struct.pack(">d",77.0).hex())
            self.assertEqual(complete[128],complete[0])
            self.assertEqual(complete[511],complete[127])


if __name__=="__main__":
    unittest.main()
