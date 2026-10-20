"""Exact 128-vector stock 26.2 finalDensity SinglePointContext receipt tests."""
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
import worldgen_26_2_stock_final_density_singlepoint_capture as final  # noqa: E402


class OriginalStockFinalDensityTests(unittest.TestCase):
    def source_methods(self):
        return {
            "router_map_all":{
                "owner":final.roots.ROUTER,"signature":"mapAll(Visitor)",
                "body_sha256":final.roots.ROUTER_MAP_ALL_SHA256,
                "normalized_sha256":"a"*64,"reviewed":False,
            },
            "random_state_router":{
                "owner":final.roots.STATE,"signature":"router()",
                "body_sha256":"b"*64,"normalized_sha256":"c"*64,
                "reviewed":False,
            },
            "holder_holder_compute":{
                "owner":final.holder.OWNER,"signature":"compute(FunctionContext)",
                "body_sha256":"d"*64,"normalized_sha256":"e"*64,
                "reviewed":False,
            },
            "ap2_compute":{
                "owner":final.FINAL,"signature":"compute(FunctionContext)",
                "body_sha256":"f"*64,"normalized_sha256":"0"*64,
                "reviewed":False,
            },
        }

    def original_manifest(self):
        return {
            "schema":1,"kind":final.KIND,"minecraft":"26.2",
            "protocol":776,"data_version":4903,
            "source_archive_sha256":final.frozen.SOURCE_SHA256,
            "official_server_sha256":final.frozen.SERVER_SHA256,
            "original_router_roots_sha256":final.graph.ORIGINAL_ROOT_SHA256,
            "original_router_graph_sha256":final.holder.ORIGINAL_GRAPH_SHA256,
            "original_holder_bindings_sha256":final.ORIGINAL_HOLDER_SHA256,
            "source_methods":self.source_methods(),
            "world_seeds":list(final.SEEDS),
            "points":[list(p) for p in final.POINTS],
            "sample_context":"DensityFunction$SinglePointContext",
            "stock_registry_used":True,
            "stock_bound_final_density_singlepoint_observed":True,
            "stock_noisechunk_interpolation_observed":False,
            "world_seed_random_state_bound":False,
            "router_numeric_parity_qualified":False,
            "full_router_graph_qualified":False,
            "source_text_included":False,
            "independent_var_sem_admitted":False,
            "production_worldgen_enabled":False,
        }

    def bits(self):
        return ["0x"+struct.pack(">d",float(row["block_x"]+
                                             row["block_y"]+2)).hex()
                for row in final.input_rows()]

    def output(self):
        values=self.bits()
        lines=["minecraft stock bootstrap stdout text"]
        for seed_index,seed in enumerate(final.SEEDS):
            lines.append(
                final.HEAD+f"|{seed_index}|{seed}|{final.FINAL}|"
                f"{final.MAPPED}|{final.HOLDER}|32"
            )
            for point in range(32):
                idx=seed_index*32+point
                lines.append(final.BITS+f"|{idx}|{values[idx][2:]}")
            lines.append(final.END+f"|{seed_index}|32")
        return "\n".join(lines)

    def test_exact_128_heldout_sample_coordinate_grid(self):
        self.assertEqual(len(final.POINTS),32)
        self.assertEqual(len(final.input_rows()),128)
        self.assertEqual(len(set(final.POINTS)),32)
        self.assertEqual([v["world_seed_bits"] for v in final.input_rows()[0:32]],
                         [final.SEEDS[0]]*32)
        self.assertEqual(final.parse_output(self.output()),self.bits())

    def test_missing_duplicate_reordered_nonfinite_and_false_class_tag_rejected(self):
        rows=self.output().splitlines()
        bit_index=next(i for i,line in enumerate(rows)
                       if line.startswith(final.BITS+"|1|"))
        for case,corrupted in enumerate((
            rows[:bit_index]+rows[bit_index+1:],
            rows[:bit_index]+[rows[bit_index]]+rows[bit_index:],
            rows[:-1],
            rows+[rows[-1]],
            [line.replace("|1|","|9|",1) if i==bit_index else line
             for i,line in enumerate(rows)],
            [line.replace("DensityFunctions$Ap2","DensityFunctions$Noise")
             if line.startswith(final.HEAD+"|0|") else line for line in rows],
            [line.replace("|0x","|") if i==bit_index else line
             for i,line in enumerate(rows)],
            [final.BITS+"|1|7ff8000000000000" if i==bit_index else line
             for i,line in enumerate(rows)],
        )):
            with self.subTest(case=case):
                self.assertNotEqual(corrupted,rows)
                with self.assertRaises(final.FinalDensityError):
                    final.parse_output("\n".join(corrupted))
        with self.assertRaisesRegex(final.FinalDensityError,"JVM PHASE"):
            final.parse_output(final.FAIL+
                "|real-finalDensity-SinglePointContext-0-7|"
                "java.lang.IllegalStateException|"
                "java.lang.reflect.InvocationTargetException|bad original context")

    def test_manifest_rejects_any_qualification_or_source_or_output_mutation(self):
        methods=self.source_methods()
        manifest=dict(self.original_manifest(),vectors=[
            dict(row,value_bits=value) for row,value
            in zip(final.input_rows(),self.bits(),strict=True)
        ])
        final.validate(manifest,methods)
        for key in ("world_seed_random_state_bound","router_numeric_parity_qualified",
                    "full_router_graph_qualified","stock_noisechunk_interpolation_observed",
                    "source_text_included","independent_var_sem_admitted",
                    "production_worldgen_enabled"):
            broken=copy.deepcopy(manifest);broken[key]=True
            with self.subTest(flag=key),self.assertRaises(final.FinalDensityError):
                final.validate(broken,methods)
        for mutate in (
            lambda data:data["vectors"].pop(),
            lambda data:data["vectors"].reverse(),
            lambda data:data["vectors"][3].__setitem__("block_x",99),
            lambda data:data["vectors"][3].__setitem__("value_bits","0x7ff0000000000000"),
            lambda data:data.__setitem__("original_holder_bindings_sha256","0"*64),
            lambda data:data.__setitem__("sample_context","NoiseChunk"),
            lambda data:data.__setitem__("source_methods",{}),
        ):
            data=copy.deepcopy(manifest);mutate(data)
            with self.assertRaises(final.FinalDensityError):
                final.validate(data,methods)

    def test_byte_pinned_actual_32_holder_receipt(self):
        with tempfile.TemporaryDirectory() as folder:
            p=Path(folder)/"not-the-received-real-stock-holders.json"
            p.write_text(json.dumps({"holder_bindings":[]}))
            with self.assertRaisesRegex(final.FinalDensityError,"SHA"):
                final.load_holder_evidence(p,{})

    def test_original_source_ap2_compute_remains_indexed_but_unreviewed(self):
        conn=sqlite3.connect(":memory:")
        conn.row_factory=sqlite3.Row
        conn.executescript("""
            CREATE TABLE types(id INTEGER PRIMARY KEY,qualified_name TEXT);
            CREATE TABLE methods(id INTEGER PRIMARY KEY,type_id INTEGER,
                name TEXT,signature TEXT,param_count INTEGER,
                body_sha256 TEXT,normalized_sha256 TEXT);
            INSERT INTO types VALUES(1,'net.minecraft.world.level.levelgen.DensityFunctions$Ap2');
            INSERT INTO methods VALUES(1,1,'compute','compute(FunctionContext)',1,
                'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa',
                'bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb');
        """)
        method=final.source_ap2_compute(conn)
        self.assertEqual(method["body_sha256"],"a"*64)
        self.assertFalse(method["reviewed"])
        conn.execute("DELETE FROM methods")
        with self.assertRaises(final.FinalDensityError):
            final.source_ap2_compute(conn)
        conn.close()

    @unittest.skipUnless(shutil.which("java") and shutil.which("javac"),
                         "real Java toolchain required for source-free JVM bridge test")
    def test_actual_compiled_java_bridge_uses_bound_overworld_final_density(self):
        with tempfile.TemporaryDirectory(prefix="helve-final-density-toy-") as directory:
            workspace=Path(directory)
            source=workspace/"java"
            def write_java(package,name,body):
                path=source/package.replace(".","/")/(name+".java")
                path.parent.mkdir(parents=True,exist_ok=True)
                path.write_text("package "+package+";\n"+body+"\n")
            write_java("net.minecraft","SharedConstants",
                       "public class SharedConstants {"
                       "public static void tryDetectVersion(){} }")
            write_java("net.minecraft.server","Bootstrap",
                       "public class Bootstrap { public static void bootStrap()"
                       "{System.setOut(new java.io.PrintStream("
                       "new java.io.ByteArrayOutputStream()));}}")
            write_java("net.minecraft.resources","ResourceKey",
                       "public record ResourceKey(String name) {}")
            write_java("net.minecraft.core","HolderGetter",
                       "public interface HolderGetter { interface Provider {} }")
            write_java("net.minecraft.core","HolderLookup",
                       "public interface HolderLookup {interface Provider extends "
                       "net.minecraft.core.HolderGetter.Provider {}}")
            write_java("net.minecraft.core","Holder",
                       "public interface Holder<T> { T value(); "
                       "record Direct<T>(T value) implements Holder<T> {} }")
            write_java("net.minecraft.data.registries","VanillaRegistries",
                       "public class VanillaRegistries {public static "
                       "net.minecraft.core.HolderLookup.Provider createLookup(){"
                       "return new net.minecraft.core.HolderLookup.Provider(){};}}")
            level="net.minecraft.world.level.levelgen"
            write_java(level,"NoiseGeneratorSettings",
                       "public class NoiseGeneratorSettings {"
                       "public static final net.minecraft.resources.ResourceKey "
                       "OVERWORLD=new net.minecraft.resources.ResourceKey(\"overworld\");}")
            write_java(level,"DensityFunction",
                       "public interface DensityFunction {double compute(FunctionContext c);"
                       "interface FunctionContext {}"
                       "record SinglePointContext(int blockX,int blockY,int blockZ)"
                       "implements FunctionContext {} }")
            write_java(level,"DensityFunctions",
                       "public class DensityFunctions {"
                       "public record Constant(double value) implements DensityFunction {"
                       "public double compute(DensityFunction.FunctionContext c){return value;}}"
                       "public record SampleXY() implements DensityFunction {"
                       "public double compute(DensityFunction.FunctionContext c){"
                       "var p=(DensityFunction.SinglePointContext)c;"
                       "return (double)p.blockX()+p.blockY();}}"
                       "public record Mapped(DensityFunction input) implements DensityFunction {"
                       "public double compute(DensityFunction.FunctionContext c){"
                       "return input.compute(c);}}"
                       "record HolderHolder(net.minecraft.core.Holder<DensityFunction> function)"
                       "implements DensityFunction {"
                       "public double compute(DensityFunction.FunctionContext c){"
                       "return function.value().compute(c);}}"
                       "public record Ap2(String type,DensityFunction argument1,"
                       "DensityFunction argument2,double minValue,double maxValue)"
                       "implements DensityFunction {"
                       "public double compute(DensityFunction.FunctionContext c){"
                       "return argument1.compute(c)+argument2.compute(c);}}}")
            fields=", ".join("DensityFunction root%02d"%i for i in range(15))
            constructors=", ".join(
                "new DensityFunctions.Ap2(\"ADD\","
                "new DensityFunctions.Mapped(new DensityFunctions.SampleXY()),"
                "new DensityFunctions.HolderHolder("
                "new net.minecraft.core.Holder.Direct<DensityFunction>("
                "new DensityFunctions.Constant(2.0))),-1.0,1.0)"
                if i==11 else "new DensityFunctions.Constant(0.0)"
                for i in range(15)
            )
            write_java(level,"NoiseRouter",
                       f"public record NoiseRouter({fields}) {{}}")
            write_java(level,"RandomState",
                       "public class RandomState {"
                       "public static RandomState create("
                       "net.minecraft.core.HolderGetter.Provider provider,"
                       "net.minecraft.resources.ResourceKey settings,long seed)"
                       "{return new RandomState();}"
                       f"public NoiseRouter router(){{return new NoiseRouter({constructors});}}"
                       "}")
            classes=workspace/"classes"
            javac=subprocess.run(
                ["javac","-encoding","UTF-8","-d",str(classes),
                 *[str(p) for p in source.rglob("*.java")]],
                capture_output=True,text=True,check=False,timeout=45,
            )
            self.assertEqual(javac.returncode,0,javac.stderr)
            with mock.patch.object(final.official,"extract_classpath",return_value=[classes]):
                self.assertEqual(final.observe(workspace/"toy.jar",timeout=90),self.bits())


if __name__=="__main__":
    unittest.main()
