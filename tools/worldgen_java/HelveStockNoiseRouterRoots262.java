// Stock Minecraft 26.2 NoiseRouter ROOTS only. The original JVM owns
// all registry, RandomState, density graph and binding objects. This tool
// reads typed record components and first-level density-child class names;
// it never computes a guessed router value or interprets an original method.
import java.io.*;
import java.lang.reflect.*;
import java.nio.charset.StandardCharsets;
import java.util.*;

public final class HelveStockNoiseRouterRoots262 {
  static final String ROOT = "net.minecraft.world.level.levelgen.";
  static final String HEADER = "HELVE26_2_ROUTER_HEADER|";
  static final String FIELD = "HELVE26_2_ROUTER_FIELD|";
  static final String CHILD = "HELVE26_2_ROUTER_CHILD|";
  static final String FAILURE = "HELVE26_2_ROUTER_FAILURE|";
  static final int SEED_COUNT = 4;
  static final int FIELD_COUNT = 15;
  static String phase = "bootstrap";
  static final PrintStream OUT = new PrintStream(
      new FileOutputStream(FileDescriptor.out), true, StandardCharsets.US_ASCII);

  static void fail(Throwable t) {
    Throwable root = t;
    for (int i = 0; i < 16 && root.getCause() != null
         && root.getCause() != root; i++) root = root.getCause();
    OUT.println(FAILURE + safe(phase) + "|" + safe(root.getClass().getName())
        + "|" + safe(t.getClass().getName()) + "|" + safe(root.getMessage()));
    OUT.flush();
  }

  static String safe(String s) {
    if (s == null || s.isEmpty()) return "-";
    StringBuilder clean = new StringBuilder();
    for (int i=0; i<s.length() && clean.length()<480; i++) {
      char c=s.charAt(i);
      clean.append(c>=32 && c<=126 && c!='|' ? c : '_');
    }
    return clean.toString();
  }

  static String name(Class<?> c) { return c.getName(); }

  static void inspect(int seedIndex, Class<?> routerType, Class<?> density,
                      Class<?> context, Object router) throws Exception {
    if (!routerType.isInstance(router) || !routerType.isRecord())
      throw new IllegalStateException("real stock NoiseRouter is not the expected record");
    RecordComponent[] components = routerType.getRecordComponents();
    if (components == null || components.length != FIELD_COUNT)
      throw new IllegalStateException("stock router must expose 15 record fields");
    OUT.println(HEADER + seedIndex + "|" + components.length + "|" + name(routerType));
    for (int fieldIndex=0; fieldIndex<components.length; fieldIndex++) {
      RecordComponent component=components[fieldIndex];
      phase="router-field-" + seedIndex + "-" + fieldIndex;
      if (component.getType()!=density
          || !component.getName().matches("[a-zA-Z_$][a-zA-Z0-9_$]{0,100}"))
        throw new IllegalStateException("unqualified stock router field type or name");
      Method rootAccessor=component.getAccessor();
      if (!rootAccessor.canAccess(router) && !rootAccessor.trySetAccessible())
        throw new IllegalStateException("stock router record accessor not accessible");
      Object node=rootAccessor.invoke(router);
      if (node==null || !density.isInstance(node))
        throw new IllegalStateException("stock router field is not a density node");
      Class<?> actual=node.getClass();
      Method compute=actual.getMethod("compute",context);
      if (compute.getReturnType()!=double.class)
        throw new IllegalStateException("stock router density compute signature changed");
      List<String[]> children=new ArrayList<>();
      RecordComponent[] slots=actual.getRecordComponents();
      if (slots!=null) {
        for (RecordComponent slot:slots) {
          // Depth ONE only. This is a partial, non-semantic field inventory.
          // Do not traverse or unbox spline/holder/cache internals.
          if (!density.isAssignableFrom(slot.getType())) continue;
          // A public generated accessor can belong to a package-private
          // Minecraft nested record (e.g. DensityFunctions$FindTopSurface).
          // Reflection from this standalone, unnamed-package probe cannot
          // invoke it until access is enabled on this exact typed accessor.
          // Never change global module openness or walk opaque child fields.
          Method childAccessor=slot.getAccessor();
          if (!childAccessor.canAccess(node) && !childAccessor.trySetAccessible())
            throw new IllegalStateException("stock density record child accessor not accessible");
          Object nested=childAccessor.invoke(node);
          if (nested==null || !density.isInstance(nested))
            throw new IllegalStateException("record's typed density child is null");
          children.add(new String[]{slot.getName(),name(nested.getClass())});
          if (children.size()>32)
            throw new IllegalStateException("unbounded first-level density children");
        }
      }
      OUT.println(FIELD+seedIndex+"|"+fieldIndex+"|"+component.getName()+"|"
          +name(actual)+"|"+name(compute.getDeclaringClass())+"|"+children.size());
      for (int i=0; i<children.size(); i++) {
        String[] child=children.get(i);
        OUT.println(CHILD+seedIndex+"|"+fieldIndex+"|"+i+"|"
            +child[0]+"|"+child[1]);
      }
    }
  }

  public static void main(String[] args) {
    try {
      if (args.length!=1 || !args[0].equals("--router-roots-4"))
        throw new IllegalArgumentException("expected --router-roots-4 only");
      run();
    } catch (Throwable t) {
      fail(t);
      System.exit(2);
    }
  }

  static void run() throws Exception {
    phase="bootstrap";
    HelveWorldSeededDensity262.bootstrap();
    phase="stock-class-contracts";
    Class<?> vanilla=Class.forName("net.minecraft.data.registries.VanillaRegistries");
    Class<?> lookup=Class.forName("net.minecraft.core.HolderLookup$Provider");
    Class<?> getterProvider=Class.forName("net.minecraft.core.HolderGetter$Provider");
    Class<?> resourceKey=Class.forName("net.minecraft.resources.ResourceKey");
    Class<?> settings=Class.forName(ROOT+"NoiseGeneratorSettings");
    Class<?> stateType=Class.forName(ROOT+"RandomState");
    Class<?> routerType=Class.forName(ROOT+"NoiseRouter");
    Class<?> density=Class.forName(ROOT+"DensityFunction");
    Class<?> context=Class.forName(ROOT+"DensityFunction$FunctionContext");

    Method makeState=HelveWorldSeededDensity262.checkedStatic(
        stateType,"create",stateType,getterProvider,resourceKey,long.class);
    Method routerMethod=stateType.getMethod("router");
    if (routerMethod.getReturnType()!=routerType
        || !getterProvider.isAssignableFrom(lookup))
      throw new IllegalStateException("original RandomState.router contract changed");
    phase="stock-createLookup";
    Object stock=HelveWorldSeededDensity262.checkedStatic(
        vanilla,"createLookup",lookup).invoke(null);
    if (!getterProvider.isInstance(stock))
      throw new IllegalStateException("not the stock Provider");
    Object overworld=HelveWorldSeededDensity262.field(settings,"OVERWORLD",resourceKey);

    BufferedReader reader=new BufferedReader(
        new InputStreamReader(System.in,StandardCharsets.US_ASCII));
    for (int i=0; i<SEED_COUNT; i++) {
      String seed=reader.readLine();
      if (seed==null) throw new IllegalStateException("missing one of four world seeds");
      long signed=HelveWorldSeededDensity262.bits(seed);
      phase="stock-create-RandomState-" + i;
      Object state=makeState.invoke(null,stock,overworld,signed);
      phase="stock-RandomState-router-" + i;
      Object router=routerMethod.invoke(state);
      phase="stock-record-components-" + i;
      inspect(i,routerType,density,context,router);
    }
    if (reader.readLine()!=null)
      throw new IllegalStateException("unexpected fifth world seed");
  }
}
