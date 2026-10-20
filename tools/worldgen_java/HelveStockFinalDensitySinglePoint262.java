// Stock Minecraft Java 26.2: 128 SinglePointContext FINAL DENSITY bit outputs.
// The actual official VanillaRegistries + Overworld RandomState owns the
// density router and all its registered bound functions. This bridge copies
// NO Minecraft code and does NOT claim the NoiseChunk interpolation context.
// No fake registry, synthetic density node, source implementation, or math.
import java.io.*;
import java.lang.reflect.*;
import java.nio.charset.StandardCharsets;
import java.util.*;

public final class HelveStockFinalDensitySinglePoint262 {
  static final String ROOT="net.minecraft.world.level.levelgen.";
  static final String HEAD="HELVE26_2_FINAL_SINGLE_HEAD|";
  static final String BITS="HELVE26_2_FINAL_SINGLE_BITS|";
  static final String END="HELVE26_2_FINAL_SINGLE_END|";
  static final String FAILURE="HELVE26_2_FINAL_SINGLE_FAILURE|";
  static final int SEED_COUNT=4;
  static final int POINT_COUNT=32;
  static final String FINAL_FIELD="finalDensity";
  static final String FINAL_CLASS=ROOT+"DensityFunctions$Ap2";
  static final String LEFT_CLASS=ROOT+"DensityFunctions$Mapped";
  static final String RIGHT_CLASS=ROOT+"DensityFunctions$HolderHolder";
  static String phase="bootstrap";
  static final PrintStream OUT=new PrintStream(
      new FileOutputStream(FileDescriptor.out),true,StandardCharsets.US_ASCII);

  static String safe(String s) {
    if (s==null || s.isEmpty()) return "-";
    StringBuilder out=new StringBuilder();
    for (int i=0;i<s.length() && out.length()<480;i++) {
      char c=s.charAt(i);
      out.append(c>=32 && c<=126 && c!='|' ? c : '_');
    }
    return out.toString();
  }
  static void fail(Throwable t) {
    Throwable root=t;
    for (int i=0;i<16 && root.getCause()!=null && root.getCause()!=root;i++)
      root=root.getCause();
    OUT.println(FAILURE+safe(phase)+"|"+safe(root.getClass().getName())+"|"+
        safe(t.getClass().getName())+"|"+safe(root.getMessage()));
    OUT.flush();
  }
  static Object checkedAccessor(RecordComponent component,Object parent)
      throws ReflectiveOperationException {
    Method method=component.getAccessor();
    if (!method.canAccess(parent) && !method.trySetAccessible())
      throw new IllegalAccessException("typed stock record accessor inaccessible");
    return method.invoke(parent);
  }
  static Object finalDensity(Object router,Class<?> routerType,Class<?> density)
      throws Exception {
    if (!routerType.isRecord() || !routerType.isInstance(router))
      throw new IllegalStateException("actual RandomState.router is not the stock NoiseRouter");
    RecordComponent[] components=routerType.getRecordComponents();
    if (components==null || components.length!=15 ||
        !FINAL_FIELD.equals(components[11].getName()) ||
        components[11].getType()!=density)
      throw new IllegalStateException("actual stock router's 15 fields changed");
    Object finalNode=checkedAccessor(components[11],router);
    if (finalNode==null || !finalNode.getClass().getName().equals(FINAL_CLASS))
      throw new IllegalStateException("actual finalDensity root is not the observed Ap2");
    RecordComponent[] children=finalNode.getClass().getRecordComponents();
    if (children==null || children.length!=5 ||
        !children[1].getName().equals("argument1") ||
        !children[2].getName().equals("argument2") ||
        children[1].getType()!=density || children[2].getType()!=density)
      throw new IllegalStateException("actual finalDensity Ap2 component contract changed");
    Object left=checkedAccessor(children[1],finalNode);
    Object right=checkedAccessor(children[2],finalNode);
    if (left==null || right==null ||
        !left.getClass().getName().equals(LEFT_CLASS) ||
        !right.getClass().getName().equals(RIGHT_CLASS))
      throw new IllegalStateException("bound finalDensity first-level children changed");
    return finalNode;
  }
  public static void main(String[] args) {
    try {
      if (args.length!=1 || !args[0].equals("--final-singlepoint-128"))
        throw new IllegalArgumentException("expected --final-singlepoint-128 ONLY");
      run();
    } catch (Throwable t) {
      fail(t);
      System.exit(2);
    }
  }
  static void run() throws Exception {
    phase="bootstrap";
    HelveWorldSeededDensity262.bootstrap();
    phase="stock-reflection-contracts";
    Class<?> vanilla=Class.forName("net.minecraft.data.registries.VanillaRegistries");
    Class<?> lookup=Class.forName("net.minecraft.core.HolderLookup$Provider");
    Class<?> getterProvider=Class.forName("net.minecraft.core.HolderGetter$Provider");
    Class<?> key=Class.forName("net.minecraft.resources.ResourceKey");
    Class<?> settings=Class.forName(ROOT+"NoiseGeneratorSettings");
    Class<?> stateType=Class.forName(ROOT+"RandomState");
    Class<?> routerType=Class.forName(ROOT+"NoiseRouter");
    Class<?> density=Class.forName(ROOT+"DensityFunction");
    Class<?> context=Class.forName(ROOT+"DensityFunction$FunctionContext");
    Class<?> pointType=Class.forName(ROOT+"DensityFunction$SinglePointContext");

    Method makeState=HelveWorldSeededDensity262.checkedStatic(
        stateType,"create",stateType,getterProvider,key,long.class);
    Method getRouter=stateType.getMethod("router");
    Method compute=density.getMethod("compute",context);
    if (getRouter.getReturnType()!=routerType ||
        compute.getReturnType()!=double.class ||
        !getterProvider.isAssignableFrom(lookup))
      throw new IllegalStateException("actual stock factory/density compute contract changed");
    Constructor<?> pointCtor=pointType.getDeclaredConstructor(
        int.class,int.class,int.class);
    if (!pointCtor.canAccess(null) && !pointCtor.trySetAccessible())
      throw new IllegalStateException("stock SinglePointContext constructor inaccessible");
    phase="stock-createLookup";
    Object provider=HelveWorldSeededDensity262.checkedStatic(
        vanilla,"createLookup",lookup).invoke(null);
    if (provider==null || !getterProvider.isInstance(provider))
      throw new IllegalStateException("not the actual stock Registry Provider");
    Object overworld=HelveWorldSeededDensity262.field(settings,"OVERWORLD",key);

    BufferedReader reader=new BufferedReader(
        new InputStreamReader(System.in,StandardCharsets.US_ASCII));
    int index=0;
    for (int seedIndex=0;seedIndex<SEED_COUNT;seedIndex++) {
      phase="stock-seed-"+seedIndex;
      Object finalNode=null;
      String expectedSeed=null;
      for (int pointIndex=0;pointIndex<POINT_COUNT;pointIndex++) {
        String raw=reader.readLine();
        if (raw==null) throw new IllegalStateException("missing original JVM point request");
        String[] record=raw.split("\t",-1);
        if (record.length!=4)
          throw new IllegalStateException("expected precisely four input columns");
        String seed=record[0];
        long worldSeed=HelveWorldSeededDensity262.bits(seed);
        if (pointIndex==0) {
          expectedSeed=seed;
          phase="real-RandomState-create-"+seedIndex;
          Object state=makeState.invoke(null,provider,overworld,worldSeed);
          phase="real-RandomState-router-"+seedIndex;
          Object router=getRouter.invoke(state);
          phase="real-bound-finalDensity-"+seedIndex;
          finalNode=finalDensity(router,routerType,density);
          OUT.println(HEAD+seedIndex+"|"+seed+"|"+FINAL_CLASS+"|"+
              LEFT_CLASS+"|"+RIGHT_CLASS+"|"+POINT_COUNT);
        } else if (!expectedSeed.equals(seed)) {
          throw new IllegalStateException("world seed changed within stock point group");
        }
        int x=Integer.parseInt(record[1]),y=Integer.parseInt(record[2]),
            z=Integer.parseInt(record[3]);
        phase="real-finalDensity-SinglePointContext-"+seedIndex+"-"+pointIndex;
        Object at=pointCtor.newInstance(x,y,z);
        double result=(Double)compute.invoke(finalNode,at);
        if (!Double.isFinite(result))
          throw new IllegalStateException("nonfinite real final density");
        OUT.println(BITS+index+"|"+
            String.format(Locale.ROOT,"%016x",Double.doubleToRawLongBits(result)));
        index++;
      }
      OUT.println(END+seedIndex+"|"+POINT_COUNT);
    }
    if (index!=SEED_COUNT*POINT_COUNT || reader.readLine()!=null)
      throw new IllegalStateException("not exactly 128 pinned official point requests");
  }
}
