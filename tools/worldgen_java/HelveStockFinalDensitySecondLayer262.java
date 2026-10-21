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
        phase="second-layer-"+seedIndex+"-"+pointIndex;
        String line=input.readLine();
        if(line==null) throw new IllegalStateException("missing frozen frame");
        String[] f=line.split("\\t",-1);
        if(f.length!=4 || !f[0].matches("0x[0-9a-f]{16}"))
          throw new IllegalStateException("unqualified bounded XYZ seed frame");
        if(pointIndex==0) {
          seed=f[0];
          Object state=create.invoke(null,provider,overworld,
              HelveWorldSeededDensity262.bits(seed));
          Object root=HelveStockFinalDensitySinglePoint262.finalDensity(
              router.invoke(state),routerClass,density);
          if(!type(root).equals(LV+"DensityFunctions$Ap2") ||
             !HelveStockFinalDensityRootSemantics262.enumName(root,"type").equals("MIN"))
            throw new IllegalStateException("original rooted MIN changed");
          Object mapped=member(root,"argument1");
          Object holder=member(root,"argument2");
          if(!type(mapped).equals(LV+"DensityFunctions$Mapped") ||
             !type(holder).equals(LV+"DensityFunctions$HolderHolder") ||
             !HelveStockFinalDensityRootSemantics262.enumName(mapped,"type").equals("SQUEEZE"))
            throw new IllegalStateException("root first-layer graph changed");
          Object marked=HelveStockFinalDensityRootSemantics262.mappedInput(mapped,density);
          if(!type(marked).equals(LV+"DensityFunctions$Marker") ||
             !HelveStockFinalDensityRootSemantics262.enumName(marked,"type").equals("Interpolated"))
            throw new IllegalStateException("original left Marker changed");
          mul=child(marked,density);
          if(!type(mul).equals(LV+"DensityFunctions$MulOrAdd"))
            throw new IllegalStateException("actual wrapped MulOrAdd changed");
          mulChild=child(mul,density);
          Object choice=HelveStockFinalDensityRootSemantics262.holderTarget(holder,density);
          if(!type(choice).equals(LV+"DensityFunctions$RangeChoice"))
            throw new IllegalStateException("actual HolderHolder target changed");
          selector=member(choice,"input");
          outer=member(choice,"whenOutOfRange");
          if(!type(selector).equals(LV+"DensityFunctions$Marker") ||
             !type(outer).equals(LV+"DensityFunctions$Ap2"))
            throw new IllegalStateException("selector Marker or out Ap2 changed");
          selectorChild=child(selector,density);
          outLeft=member(outer,"argument1");
          outRight=member(outer,"argument2");
          if(!density.isInstance(mulChild) || !density.isInstance(selectorChild) ||
             !density.isInstance(outLeft) || !density.isInstance(outRight))
            throw new IllegalStateException("second-layer node children not densities");
          double arg=(Double)member(mul,"argument");
          OUT.println(SHAPE+seedIndex+"|"+seed+"|"+
              HelveStockFinalDensityRootSemantics262.enumClass(mul,"type")+"|"+
              HelveStockFinalDensityRootSemantics262.enumName(mul,"type")+"|"+
              bits(arg)+"|"+type(mulChild)+"|"+
              HelveStockFinalDensityRootSemantics262.enumClass(selector,"type")+"|"+
              HelveStockFinalDensityRootSemantics262.enumName(selector,"type")+"|"+
              type(selectorChild)+"|"+
              HelveStockFinalDensityRootSemantics262.enumClass(outer,"type")+"|"+
              HelveStockFinalDensityRootSemantics262.enumName(outer,"type")+"|"+
              type(outLeft)+"|"+type(outRight));
        } else if(!seed.equals(f[0])) {
          throw new IllegalStateException("original seed frame changed");
        }
        int x=Integer.parseInt(f[1]),y=Integer.parseInt(f[2]),z=Integer.parseInt(f[3]);
        Object at=pointCtor.newInstance(x,y,z);
        double m=HelveStockFinalDensityInnerSemantics262.finite(mul,compute,at);
        double mc=HelveStockFinalDensityInnerSemantics262.finite(mulChild,compute,at);
        double ss=HelveStockFinalDensityInnerSemantics262.finite(selector,compute,at);
        double sc=HelveStockFinalDensityInnerSemantics262.finite(selectorChild,compute,at);
        double a=HelveStockFinalDensityInnerSemantics262.finite(outLeft,compute,at);
        double b=HelveStockFinalDensityInnerSemantics262.finite(outRight,compute,at);
        double o=HelveStockFinalDensityInnerSemantics262.finite(outer,compute,at);
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
