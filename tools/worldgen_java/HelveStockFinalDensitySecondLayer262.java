// Original Minecraft Java 26.2 stock finalDensity next *unseen* inner edges.
// Source-owning JVM only: no generated terrain, registry data, Minecraft source,
// compiled classes or intermediate private Java snippets are transmitted.
// Previously frozen inner output words are equality anchors, not new captures.
import java.io.*;
import java.lang.reflect.*;
import java.nio.charset.StandardCharsets;
import java.util.*;

public final class HelveStockFinalDensitySecondLayer262 {
  static final String LV="net.minecraft.world.level.levelgen.";
  static final String SHAPE="HELVE26_2_SECOND_SHAPE|";
  static final String VALUE="HELVE26_2_SECOND_VALUE|";
  static final String END="HELVE26_2_SECOND_END|";
  static final String FAIL="HELVE26_2_SECOND_FAILURE|";
  static final PrintStream OUT=new PrintStream(
      new FileOutputStream(FileDescriptor.out),true,StandardCharsets.US_ASCII);
  static String phase="bootstrap";
  // Narrow, source-free failure stages. Only fixed identifiers, never
  // reflection exception messages, private class contents, or source text.
  static void stage(int seed, int point, String step) {
    phase="second-layer-"+seed+"-"+point+"-"+step;
  }
  static String bits(double value) {
    if(!Double.isFinite(value))
      throw new IllegalStateException("nonfinite stock second-layer density");
    return HelveStockFinalDensityInnerSemantics262.bits(value);
  }
  static String type(Object value) {
    return HelveStockFinalDensityInnerSemantics262.type(value);
  }
  static Object member(Object value,String field) throws Exception {
    return HelveStockFinalDensityInnerSemantics262.member(value,field);
  }
  static Object child(Object value,Class<?> density) throws Exception {
    return HelveStockFinalDensityInnerSemantics262.soleDensityChild(value,density);
  }
  static void failure(Throwable t) {
    Throwable reason=t;
    for(int i=0;i<16 && reason.getCause()!=null && reason.getCause()!=reason;i++)
      reason=reason.getCause();
    OUT.println(FAIL+
        HelveStockFinalDensityInnerSemantics262.safe(phase)+"|"+
        HelveStockFinalDensityInnerSemantics262.safe(reason.getClass().getName()));
  }
  public static void main(String[] args) {
    try {
      if(args.length!=1 || !args[0].equals("--second-layer-128"))
        throw new IllegalArgumentException("must request fixed second-layer 128 frames");
      run();
    } catch(Throwable t) {
      failure(t);
      System.exit(2);
    }
  }
  static void run() throws Exception {
    phase="bootstrap";
    HelveWorldSeededDensity262.bootstrap();
    Class<?> vanilla=Class.forName("net.minecraft.data.registries.VanillaRegistries");
    Class<?> lookup=Class.forName("net.minecraft.core.HolderLookup$Provider");
    Class<?> getterProvider=Class.forName("net.minecraft.core.HolderGetter$Provider");
    Class<?> key=Class.forName("net.minecraft.resources.ResourceKey");
    Class<?> settings=Class.forName(LV+"NoiseGeneratorSettings");
    Class<?> stateClass=Class.forName(LV+"RandomState");
    Class<?> routerClass=Class.forName(LV+"NoiseRouter");
    Class<?> density=Class.forName(LV+"DensityFunction");
    Class<?> context=Class.forName(LV+"DensityFunction$FunctionContext");
    Class<?> point=Class.forName(LV+"DensityFunction$SinglePointContext");
    Method create=HelveWorldSeededDensity262.checkedStatic(
        stateClass,"create",stateClass,getterProvider,key,long.class);
    Method router=stateClass.getMethod("router");
    Method compute=density.getMethod("compute",context);
    Constructor<?> pointCtor=point.getDeclaredConstructor(int.class,int.class,int.class);
    if(!pointCtor.canAccess(null) && !pointCtor.trySetAccessible())
      throw new IllegalStateException("point constructor access changed");

    phase="stock-lookup";
    Object provider=HelveWorldSeededDensity262.checkedStatic(
        vanilla,"createLookup",lookup).invoke(null);
    if(provider==null || !getterProvider.isInstance(provider))
      throw new IllegalStateException("original vanilla lookup provider changed");
    Object overworld=HelveWorldSeededDensity262.field(settings,"OVERWORLD",key);
    BufferedReader input=new BufferedReader(
        new InputStreamReader(System.in,StandardCharsets.US_ASCII));
    int captured=0;
    for(int seedIndex=0;seedIndex<4;seedIndex++) {
      Object mul=null,mulChild=null,selector=null,selectorChild=null;
      Object outer=null,outLeft=null,outRight=null;
      String seed=null;
      for(int pointIndex=0;pointIndex<32;pointIndex++) {
        stage(seedIndex,pointIndex,"input-frame");
        String line=input.readLine();
        if(line==null) throw new IllegalStateException("missing frozen frame");
        String[] f=line.split("\\t",-1);
        if(f.length!=4 || !f[0].matches("0x[0-9a-f]{16}"))
          throw new IllegalStateException("unqualified bounded XYZ seed frame");
        if(pointIndex==0) {
          seed=f[0];
          stage(seedIndex,pointIndex,"create-random-state");
          Object state=create.invoke(null,provider,overworld,
              HelveWorldSeededDensity262.bits(seed));
          stage(seedIndex,pointIndex,"resolve-root");
          Object root=HelveStockFinalDensitySinglePoint262.finalDensity(
              router.invoke(state),routerClass,density);
          stage(seedIndex,pointIndex,"check-min-root");
          if(!type(root).equals(LV+"DensityFunctions$Ap2") ||
             !HelveStockFinalDensityRootSemantics262.enumName(root,"type").equals("MIN"))
            throw new IllegalStateException("original rooted MIN changed");
          stage(seedIndex,pointIndex,"root-left-child");
          Object mapped=member(root,"argument1");
          stage(seedIndex,pointIndex,"root-right-child");
          Object holder=member(root,"argument2");
          stage(seedIndex,pointIndex,"check-first-level-types");
          if(!type(mapped).equals(LV+"DensityFunctions$Mapped") ||
             !type(holder).equals(LV+"DensityFunctions$HolderHolder") ||
             !HelveStockFinalDensityRootSemantics262.enumName(mapped,"type").equals("SQUEEZE"))
            throw new IllegalStateException("root first-layer graph changed");
          stage(seedIndex,pointIndex,"mapped-input");
          Object marked=HelveStockFinalDensityRootSemantics262.mappedInput(mapped,density);
          stage(seedIndex,pointIndex,"check-interpolated-marker");
          if(!type(marked).equals(LV+"DensityFunctions$Marker") ||
             !HelveStockFinalDensityRootSemantics262.enumName(marked,"type").equals("Interpolated"))
            throw new IllegalStateException("original left Marker changed");
          stage(seedIndex,pointIndex,"interpolated-wrapped-child");
          mul=child(marked,density);
          stage(seedIndex,pointIndex,"check-muloradd-class");
          if(!type(mul).equals(LV+"DensityFunctions$MulOrAdd"))
            throw new IllegalStateException("actual wrapped MulOrAdd changed");
          stage(seedIndex,pointIndex,"muloradd-child-record");
          mulChild=child(mul,density);
          stage(seedIndex,pointIndex,"resolve-holder-target");
          Object choice=HelveStockFinalDensityRootSemantics262.holderTarget(holder,density);
          stage(seedIndex,pointIndex,"check-rangechoice-class");
          if(!type(choice).equals(LV+"DensityFunctions$RangeChoice"))
            throw new IllegalStateException("actual HolderHolder target changed");
          stage(seedIndex,pointIndex,"range-selector-record");
          selector=member(choice,"input");
          stage(seedIndex,pointIndex,"range-outside-record");
          outer=member(choice,"whenOutOfRange");
          stage(seedIndex,pointIndex,"check-selector-and-ap2-class");
          if(!type(selector).equals(LV+"DensityFunctions$Marker") ||
             !type(outer).equals(LV+"DensityFunctions$Ap2"))
            throw new IllegalStateException("selector Marker or out Ap2 changed");
          stage(seedIndex,pointIndex,"selector-marker-child-record");
          selectorChild=child(selector,density);
          stage(seedIndex,pointIndex,"outside-ap2-left");
          outLeft=member(outer,"argument1");
          stage(seedIndex,pointIndex,"outside-ap2-right");
          outRight=member(outer,"argument2");
          stage(seedIndex,pointIndex,"check-all-density-inputs");
          if(!density.isInstance(mulChild) || !density.isInstance(selectorChild) ||
             !density.isInstance(outLeft) || !density.isInstance(outRight))
            throw new IllegalStateException("second-layer node children not densities");
          stage(seedIndex,pointIndex,"muloradd-argument-record");
          double arg=(Double)member(mul,"argument");
          stage(seedIndex,pointIndex,"muloradd-operation-record");
          String mulOpClass=HelveStockFinalDensityRootSemantics262.enumClass(mul,"type");
          String mulOpName=HelveStockFinalDensityRootSemantics262.enumName(mul,"type");
          stage(seedIndex,pointIndex,"selector-marker-type-record");
          String selectorClass=HelveStockFinalDensityRootSemantics262.enumClass(selector,"type");
          String selectorName=HelveStockFinalDensityRootSemantics262.enumName(selector,"type");
          stage(seedIndex,pointIndex,"outside-ap2-operation-record");
          String outsideClass=HelveStockFinalDensityRootSemantics262.enumClass(outer,"type");
          String outsideName=HelveStockFinalDensityRootSemantics262.enumName(outer,"type");
          stage(seedIndex,pointIndex,"emit-shape");
          OUT.println(SHAPE+seedIndex+"|"+seed+"|"+
              mulOpClass+"|"+mulOpName+"|"+
              bits(arg)+"|"+type(mulChild)+"|"+
              selectorClass+"|"+selectorName+"|"+
              type(selectorChild)+"|"+
              outsideClass+"|"+outsideName+"|"+
              type(outLeft)+"|"+type(outRight));
        } else if(!seed.equals(f[0])) {
          throw new IllegalStateException("original seed frame changed");
        }
        stage(seedIndex,pointIndex,"decode-xyz");
        int x=Integer.parseInt(f[1]),y=Integer.parseInt(f[2]),z=Integer.parseInt(f[3]);
        stage(seedIndex,pointIndex,"single-point-context");
        Object at=pointCtor.newInstance(x,y,z);
        stage(seedIndex,pointIndex,"muloradd-output");
        double m=HelveStockFinalDensityInnerSemantics262.finite(mul,compute,at);
        stage(seedIndex,pointIndex,"muloradd-input");
        double mc=HelveStockFinalDensityInnerSemantics262.finite(mulChild,compute,at);
        stage(seedIndex,pointIndex,"selector-output");
        double ss=HelveStockFinalDensityInnerSemantics262.finite(selector,compute,at);
        stage(seedIndex,pointIndex,"selector-wrapped-input");
        double sc=HelveStockFinalDensityInnerSemantics262.finite(selectorChild,compute,at);
        stage(seedIndex,pointIndex,"outside-ap2-left-value");
        double a=HelveStockFinalDensityInnerSemantics262.finite(outLeft,compute,at);
        stage(seedIndex,pointIndex,"outside-ap2-right-value");
        double b=HelveStockFinalDensityInnerSemantics262.finite(outRight,compute,at);
        stage(seedIndex,pointIndex,"outside-ap2-output");
        double o=HelveStockFinalDensityInnerSemantics262.finite(outer,compute,at);
        stage(seedIndex,pointIndex,"emit-bit-frame");
        OUT.println(VALUE+captured+"|"+bits(mc)+"|"+bits(m)+"|"+
            bits(sc)+"|"+bits(ss)+"|"+bits(a)+"|"+bits(b)+"|"+bits(o));
        captured++;
      }
      OUT.println(END+seedIndex+"|32");
    }
    if(captured!=128 || input.readLine()!=null)
      throw new IllegalStateException("bounded original stock frames exceeded");
  }
}
