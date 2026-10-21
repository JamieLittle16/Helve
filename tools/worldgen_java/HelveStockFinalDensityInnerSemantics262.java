// Read-only stock 26.2 finalDensity *inner* edge review.
// Capture new Marker -> Mapped and RangeChoice selector/branch observations.
// Exact old first-level operand bitwords are independently pinned in Python.
// No Minecraft code or registry is serialized, no published worldgen authority.
import java.io.*;
import java.lang.reflect.*;
import java.nio.charset.StandardCharsets;
import java.util.*;

public final class HelveStockFinalDensityInnerSemantics262 {
  static final String PREFIX="HELVE26_2_FINAL_INNER_";
  static final String SHAPE=PREFIX+"SHAPE|";
  static final String VALUE=PREFIX+"VALUE|";
  static final String END=PREFIX+"END|";
  static final String FAIL=PREFIX+"FAILURE|";
  static final String LEVEL="net.minecraft.world.level.levelgen.";
  static final PrintStream OUT=new PrintStream(
      new FileOutputStream(FileDescriptor.out),true,StandardCharsets.US_ASCII);
  static String phase="bootstrap";

  static String safe(String name) {
    if(name==null || name.length()>180 || !name.matches("[A-Za-z0-9_.$-]+"))
      throw new IllegalStateException("unqualified original class/phase name");
    return name;
  }
  static String bits(double value) {
    return String.format(Locale.ROOT,"%016x",Double.doubleToRawLongBits(value));
  }
  static Object member(Object node,String key) throws Exception {
    return HelveStockFinalDensityRootSemantics262.member(node,key);
  }
  static String type(Object node) {
    return safe(node.getClass().getName());
  }
  static Object soleDensityChild(Object node,Class<?> density) throws Exception {
    if(!node.getClass().isRecord())
      throw new IllegalStateException("stock input wrapper not record");
    Object found=null;
    int n=0;
    for(RecordComponent c:node.getClass().getRecordComponents()) {
      if(c.getType()==density) {
        found=HelveStockFinalDensitySinglePoint262.checkedAccessor(c,node);
        n++;
      }
    }
    if(n!=1 || found==null || !density.isInstance(found))
      throw new IllegalStateException("stock marker must have one typed child");
    return found;
  }
  static double finite(Object densityNode,Method compute,Object context) throws Exception {
    double value=(Double)compute.invoke(densityNode,context);
    if(!Double.isFinite(value))
      throw new IllegalStateException("nonfinite inner stock 26.2 observation");
    return value;
  }
  static void fail(Throwable throwable) {
    Throwable cause=throwable;
    for(int i=0;i<16 && cause.getCause()!=null && cause.getCause()!=cause;i++)
      cause=cause.getCause();
    OUT.println(FAIL+safe(phase)+"|"+safe(cause.getClass().getName()));
  }
  public static void main(String[] args) {
    try {
      if(args.length!=1 || !args[0].equals("--inner-128"))
        throw new IllegalArgumentException("bounded 128-point inner review only");
      run();
    } catch(Throwable t) {
      fail(t);
      System.exit(2);
    }
  }
  static void run() throws Exception {
    phase="bootstrap";
    HelveWorldSeededDensity262.bootstrap();
    phase="stock-contracts";
    Class<?> vanilla=Class.forName("net.minecraft.data.registries.VanillaRegistries");
    Class<?> lookup=Class.forName("net.minecraft.core.HolderLookup$Provider");
    Class<?> getterProvider=Class.forName("net.minecraft.core.HolderGetter$Provider");
    Class<?> key=Class.forName("net.minecraft.resources.ResourceKey");
    Class<?> settings=Class.forName(LEVEL+"NoiseGeneratorSettings");
    Class<?> stateType=Class.forName(LEVEL+"RandomState");
    Class<?> routerType=Class.forName(LEVEL+"NoiseRouter");
    Class<?> density=Class.forName(LEVEL+"DensityFunction");
    Class<?> context=Class.forName(LEVEL+"DensityFunction$FunctionContext");
    Class<?> point=Class.forName(LEVEL+"DensityFunction$SinglePointContext");
    Method makeState=HelveWorldSeededDensity262.checkedStatic(
        stateType,"create",stateType,getterProvider,key,long.class);
    Method router=stateType.getMethod("router");
    Method compute=density.getMethod("compute",context);
    Constructor<?> pointCtor=point.getDeclaredConstructor(int.class,int.class,int.class);
    if(!pointCtor.canAccess(null) && !pointCtor.trySetAccessible())
      throw new IllegalStateException("official SinglePointContext ctor inaccessible");
    phase="stock-registry";
    Object provider=HelveWorldSeededDensity262.checkedStatic(
        vanilla,"createLookup",lookup).invoke(null);
    if(provider==null || !getterProvider.isInstance(provider))
      throw new IllegalStateException("original 26.2 lookup provider mismatch");
    Object overworld=HelveWorldSeededDensity262.field(settings,"OVERWORLD",key);
    BufferedReader reader=new BufferedReader(
        new InputStreamReader(System.in,StandardCharsets.US_ASCII));
    int total=0;
    for(int seedIndex=0;seedIndex<4;seedIndex++) {
      Object mapped=null,marker=null,wrapped=null,holder=null,choice=null;
      Object selector=null,inner=null,outer=null;
      String seed=null;
      for(int pointIndex=0;pointIndex<32;pointIndex++) {
        phase="stock-inner-"+seedIndex+"-"+pointIndex;
        String row=reader.readLine();
        if(row==null) throw new IllegalStateException("missing fixed 128-point context");
        String[] fields=row.split("\\t",-1);
        if(fields.length!=4 || !fields[0].matches("0x[0-9a-f]{16}"))
          throw new IllegalStateException("unqualified input frame");
        if(pointIndex==0) {
          seed=fields[0];
          Object state=makeState.invoke(null,provider,overworld,
              HelveWorldSeededDensity262.bits(seed));
          Object root=HelveStockFinalDensitySinglePoint262.finalDensity(
              router.invoke(state),routerType,density);
          if(!type(root).equals(LEVEL+"DensityFunctions$Ap2") ||
             !HelveStockFinalDensityRootSemantics262.enumName(root,"type").equals("MIN"))
            throw new IllegalStateException("original Ap2 MIN root changed");
          mapped=member(root,"argument1");
          holder=member(root,"argument2");
          if(!type(mapped).equals(LEVEL+"DensityFunctions$Mapped") ||
             !type(holder).equals(LEVEL+"DensityFunctions$HolderHolder") ||
             !HelveStockFinalDensityRootSemantics262.enumName(mapped,"type").equals("SQUEEZE"))
            throw new IllegalStateException("original SQUEEZE/HolderHolder paths changed");
          marker=HelveStockFinalDensityRootSemantics262.mappedInput(mapped,density);
          if(!type(marker).equals(LEVEL+"DensityFunctions$Marker"))
            throw new IllegalStateException("original marker wrapper changed");
          wrapped=soleDensityChild(marker,density);
          choice=HelveStockFinalDensityRootSemantics262.holderTarget(holder,density);
          if(!type(choice).equals(LEVEL+"DensityFunctions$RangeChoice") ||
             !choice.getClass().isRecord() ||
             choice.getClass().getRecordComponents().length!=5)
            throw new IllegalStateException("bound original RangeChoice record changed");
          selector=member(choice,"input");
          inner=member(choice,"whenInRange");
          outer=member(choice,"whenOutOfRange");
          if(!density.isInstance(selector) ||
             !density.isInstance(inner) || !density.isInstance(outer))
            throw new IllegalStateException("range branch components not stock density types");
          double low=(Double)member(choice,"minInclusive");
          double high=(Double)member(choice,"maxExclusive");
          if(!Double.isFinite(low) || !Double.isFinite(high) || !(low<high))
            throw new IllegalStateException("invalid original RangeChoice thresholds");
          OUT.println(SHAPE+seedIndex+"|"+seed+"|"+
              HelveStockFinalDensityRootSemantics262.enumClass(marker,"type")+"|"+
              HelveStockFinalDensityRootSemantics262.enumName(marker,"type")+"|"+
              type(wrapped)+"|"+type(selector)+"|"+type(inner)+"|"+
              type(outer)+"|"+bits(low)+"|"+bits(high));
        } else if(!seed.equals(fields[0])) {
          throw new IllegalStateException("root world seed changed");
        }
        int x=Integer.parseInt(fields[1]);
        int y=Integer.parseInt(fields[2]);
        int z=Integer.parseInt(fields[3]);
        Object at=pointCtor.newInstance(x,y,z);
        double markerValue=finite(marker,compute,at);
        double wrappedValue=finite(wrapped,compute,at);
        double mappedValue=finite(mapped,compute,at);
        double selectorValue=finite(selector,compute,at);
        double whenInValue=finite(inner,compute,at);
        double whenOutValue=finite(outer,compute,at);
        double holderValue=finite(holder,compute,at);
        OUT.println(VALUE+total+"|"+bits(markerValue)+"|"+
            bits(wrappedValue)+"|"+bits(mappedValue)+"|"+
            bits(selectorValue)+"|"+bits(whenInValue)+"|"+
            bits(whenOutValue)+"|"+bits(holderValue));
        total++;
      }
      OUT.println(END+seedIndex+"|32");
    }
    if(total!=128 || reader.readLine()!=null)
      throw new IllegalStateException("additional stock context rows");
  }
}
