// Read-only stock Minecraft Java 26.2 finalDensity root semantic diagnostic.
// REAL VanillaRegistries -> RandomState -> NoiseRouter.finalDensity.
// Never implements Minecraft math, never publishes Java source/bytecode.
import java.io.*;
import java.lang.reflect.*;
import java.nio.charset.StandardCharsets;
import java.util.*;

public final class HelveStockFinalDensityRootSemantics262 {
  static final String LEVEL="net.minecraft.world.level.levelgen.";
  static final String HEAD="HELVE26_2_FINAL_ROOT_SHAPE|";
  static final String VALUE="HELVE26_2_FINAL_ROOT_VALUE|";
  static final String END="HELVE26_2_FINAL_ROOT_END|";
  static final String FAIL="HELVE26_2_FINAL_ROOT_FAILURE|";
  static final PrintStream OUT=new PrintStream(
      new FileOutputStream(FileDescriptor.out),true,StandardCharsets.US_ASCII);
  static String phase="bootstrap";

  static String safe(String raw) {
    if(raw==null || raw.length()>180 || !raw.matches("[A-Za-z0-9_.$-]+"))
      throw new IllegalStateException("unqualified original runtime name");
    return raw;
  }
  static String bits(double v) {
    return String.format(Locale.ROOT,"%016x",Double.doubleToRawLongBits(v));
  }
  static void fail(Throwable throwable) {
    Throwable cause=throwable;
    for(int i=0;i<16 && cause.getCause()!=null && cause.getCause()!=cause;i++)
      cause=cause.getCause();
    OUT.println(FAIL+safe(phase)+"|"+safe(cause.getClass().getName()));
  }
  static Object member(Object node,String name) throws Exception {
    Class<?> type=node.getClass();
    if(!type.isRecord()) throw new IllegalStateException("expected original record node");
    RecordComponent found=null;
    for(RecordComponent part:type.getRecordComponents()) {
      if(part.getName().equals(name)) {
        if(found!=null) throw new IllegalStateException("duplicated stock record component");
        found=part;
      }
    }
    if(found==null) throw new IllegalStateException("missing observed record component");
    return HelveStockFinalDensitySinglePoint262.checkedAccessor(found,node);
  }
  static String enumName(Object node,String name) throws Exception {
    Object type=member(node,name);
    if(!(type instanceof Enum<?>))
      throw new IllegalStateException("expected typed runtime enum");
    return safe(((Enum<?>)type).name());
  }
  static String enumClass(Object node,String name) throws Exception {
    return safe(member(node,name).getClass().getName());
  }
  static Object mappedInput(Object mapped,Class<?> density) throws Exception {
    if(!mapped.getClass().isRecord())
      throw new IllegalStateException("Mapped not record");
    Object input=null;
    int count=0;
    for(RecordComponent c:mapped.getClass().getRecordComponents()) {
      if(c.getType()==density) {
        input=HelveStockFinalDensitySinglePoint262.checkedAccessor(c,mapped);
        count++;
      }
    }
    if(count!=1 || input==null || !density.isInstance(input))
      throw new IllegalStateException("Mapped must have exactly one DensityFunction input");
    return input;
  }
  static Object holderTarget(Object holderNode,Class<?> density) throws Exception {
    Object holder=member(holderNode,"function");
    if(!holder.getClass().getName().equals("net.minecraft.core.Holder$Direct"))
      throw new IllegalStateException("stock finalDensity holder not Direct");
    Method value=holder.getClass().getMethod("value");
    if(!value.canAccess(holder) && !value.trySetAccessible())
      throw new IllegalStateException("stock holder accessor not visible");
    Object target=value.invoke(holder);
    if(target==null || !density.isInstance(target))
      throw new IllegalStateException("bound Holder value not DensityFunction");
    return target;
  }
  static String shape(Object root,Class<?> density) throws Exception {
    if(root==null || !root.getClass().getName().equals(LEVEL+"DensityFunctions$Ap2"))
      throw new IllegalStateException("root no longer observed Ap2");
    if(!root.getClass().isRecord() || root.getClass().getRecordComponents().length!=5)
      throw new IllegalStateException("unexpected actual Ap2 record arity");
    Object left=member(root,"argument1");
    Object right=member(root,"argument2");
    if(!left.getClass().getName().equals(LEVEL+"DensityFunctions$Mapped") ||
       !right.getClass().getName().equals(LEVEL+"DensityFunctions$HolderHolder"))
      throw new IllegalStateException("actual finalDensity first-level children changed");
    Object mappedChild=mappedInput(left,density);
    Object holderChild=holderTarget(right,density);
    if(!left.getClass().isRecord() || !right.getClass().isRecord() ||
       right.getClass().getRecordComponents().length!=1)
      throw new IllegalStateException("unexpected mapped/holder first-level record");
    return enumClass(root,"type")+"|"+enumName(root,"type")+"|"+
           enumClass(left,"type")+"|"+enumName(left,"type")+"|"+
           safe(mappedChild.getClass().getName())+"|"+
           safe(holderChild.getClass().getName())+"|"+
           bits((Double)member(root,"minValue"))+"|"+
           bits((Double)member(root,"maxValue"));
  }
  public static void main(String[] args) {
    try {
      if(args.length!=1 || !args[0].equals("--final-root-children-128"))
        throw new IllegalArgumentException("expected one bounded diagnostic mode");
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
      throw new IllegalStateException("actual stock context ctor inaccessible");
    phase="stock-registry";
    Object provider=HelveWorldSeededDensity262.checkedStatic(
        vanilla,"createLookup",lookup).invoke(null);
    if(provider==null || !getterProvider.isInstance(provider))
      throw new IllegalStateException("not the original lookup provider");
    Object overworld=HelveWorldSeededDensity262.field(settings,"OVERWORLD",key);
    BufferedReader reader=new BufferedReader(
        new InputStreamReader(System.in,StandardCharsets.US_ASCII));
    int total=0;
    for(int seedIndex=0;seedIndex<4;seedIndex++) {
      Object root=null,left=null,right=null;
      String expectedSeed=null;
      for(int pointIndex=0;pointIndex<32;pointIndex++) {
        phase="stock-point-"+seedIndex+"-"+pointIndex;
        String line=reader.readLine();
        if(line==null) throw new IllegalStateException("missing frozen stock request");
        String[] row=line.split("\t",-1);
        if(row.length!=4 || !row[0].matches("0x[0-9a-f]{16}"))
          throw new IllegalStateException("wrong frozen coordinate frame");
        if(pointIndex==0) {
          expectedSeed=row[0];
          Object state=makeState.invoke(
              null,provider,overworld,HelveWorldSeededDensity262.bits(expectedSeed));
          root=HelveStockFinalDensitySinglePoint262.finalDensity(
              router.invoke(state),routerType,density);
          left=member(root,"argument1");
          right=member(root,"argument2");
          OUT.println(HEAD+seedIndex+"|"+expectedSeed+"|"+shape(root,density));
        } else if(!expectedSeed.equals(row[0])) {
          throw new IllegalStateException("seed changed mid frame");
        }
        int x=Integer.parseInt(row[1]);
        int y=Integer.parseInt(row[2]);
        int z=Integer.parseInt(row[3]);
        Object at=pointCtor.newInstance(x,y,z);
        double a=(Double)compute.invoke(left,at);
        double b=(Double)compute.invoke(right,at);
        double result=(Double)compute.invoke(root,at);
        if(!Double.isFinite(a) || !Double.isFinite(b) || !Double.isFinite(result))
          throw new IllegalStateException("nonfinite original density child/output");
        OUT.println(VALUE+total+"|"+bits(a)+"|"+bits(b)+"|"+bits(result));
        total++;
      }
      OUT.println(END+seedIndex+"|32");
    }
    if(total!=128 || reader.readLine()!=null)
      throw new IllegalStateException("not exactly 128 original contexts");
  }
}
