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

  // A strictly bounded, read-only shape probe. It follows ONLY immediate
  // record components whose declared type implements DensityFunction.
  // Holder, spline, settings, marker enums and cached values remain opaque.
  // Object identity is used solely to describe sharing, never to evaluate.
  static final int GRAPH_LIMIT = 384;
  static final int GRAPH_DEPTH = 4;
  static final String GRAPH_HEAD = "HELVE26_2_ROUTER_GRAPH_HEAD|";
  static final String GRAPH_ROOT = "HELVE26_2_ROUTER_GRAPH_ROOT|";
  static final String GRAPH_NODE = "HELVE26_2_ROUTER_GRAPH_NODE|";
  static final String GRAPH_EDGE = "HELVE26_2_ROUTER_GRAPH_EDGE|";
  static final String GRAPH_OPAQUE = "HELVE26_2_ROUTER_GRAPH_OPAQUE|";
  static final String GRAPH_END = "HELVE26_2_ROUTER_GRAPH_END|";
  static final String HOLDER = "HELVE26_2_ROUTER_HOLDER|";
  static final String HOLDER_END = "HELVE26_2_ROUTER_HOLDER_END|";
  static final String HOLDER_HOLDER = ROOT+"DensityFunctions$HolderHolder";

  static int registerGraph(Object node, int depth,
                           IdentityHashMap<Object,Integer> identities,
                           ArrayList<Object> nodes, ArrayList<Integer> depths)
      throws Exception {
    Integer existing=identities.get(node);
    if (existing!=null) return existing;
    if (nodes.size()>=GRAPH_LIMIT)
      throw new IllegalStateException("stock graph object count exceeds 384");
    int id=nodes.size();
    identities.put(node,id);
    nodes.add(node);
    depths.add(depth);
    return id;
  }

  static void inspectGraph(int seedIndex, Class<?> routerType, Class<?> density,
                           Class<?> context, Object router, boolean holders) throws Exception {
    if (!routerType.isRecord() || !routerType.isInstance(router))
      throw new IllegalStateException("expected stock NoiseRouter record instance");
    RecordComponent[] roots=routerType.getRecordComponents();
    if (roots==null || roots.length!=FIELD_COUNT)
      throw new IllegalStateException("expected 15 bound stock NoiseRouter roots");
    IdentityHashMap<Object,Integer> identities=new IdentityHashMap<>();
    ArrayList<Object> nodes=new ArrayList<>();
    ArrayList<Integer> depths=new ArrayList<>();
    OUT.println(GRAPH_HEAD+seedIndex+"|"+FIELD_COUNT+"|"+name(routerType));
    for (int i=0;i<roots.length;i++) {
      RecordComponent root=roots[i];
      phase="graph-root-"+seedIndex+"-"+i;
      if (root.getType()!=density ||
          !root.getName().matches("[a-zA-Z_$][a-zA-Z0-9_$]{0,100}"))
        throw new IllegalStateException("unexpected stock router root declaration");
      Method accessor=root.getAccessor();
      if (!accessor.canAccess(router) && !accessor.trySetAccessible())
        throw new IllegalStateException("stock router root inaccessible");
      Object value=accessor.invoke(router);
      if (value==null || !density.isInstance(value))
        throw new IllegalStateException("stock router root not a density function");
      int node=registerGraph(value,0,identities,nodes,depths);
      OUT.println(GRAPH_ROOT+seedIndex+"|"+i+"|"+root.getName()+"|"+node);
    }
    int edges=0,opaques=0,holderRows=0;
    for (int id=0;id<nodes.size();id++) {
      phase="graph-node-"+seedIndex+"-"+id;
      Object value=nodes.get(id);
      int depth=depths.get(id);
      Class<?> type=value.getClass();
      if (!density.isInstance(value) ||
          !name(type).startsWith(ROOT+"DensityFunctions$"))
        throw new IllegalStateException("unknown stock router density implementation");
      Method compute=type.getMethod("compute",context);
      if (compute.getReturnType()!=double.class)
        throw new IllegalStateException("stock router compute contract changed");
      boolean expanded=depth<GRAPH_DEPTH;
      // This optional probe resolves only the *public Holder.value() binding*
      // of the exact, already observed HolderHolder implementation. It does
      // not follow that function recursively or infer how it is evaluated.
      if (holders && name(type).equals(HOLDER_HOLDER)) {
        phase="holder-bound-"+seedIndex+"-"+id;
        RecordComponent[] components=type.getRecordComponents();
        Class<?> holderInterface=Class.forName("net.minecraft.core.Holder");
        if (components==null || components.length!=1 ||
            !components[0].getName().equals("function") ||
            components[0].getType()!=holderInterface)
          throw new IllegalStateException("unexpected stock HolderHolder component contract");
        Method accessor=components[0].getAccessor();
        if (!accessor.canAccess(value) && !accessor.trySetAccessible())
          throw new IllegalStateException("HolderHolder.function accessor inaccessible");
        Object holder=accessor.invoke(value);
        if (holder==null || !holderInterface.isInstance(holder))
          throw new IllegalStateException("missing real stock Holder object");
        Method holderValue=holderInterface.getMethod("value");
        if (holderValue.getParameterCount()!=0 || holderValue.getReturnType().isPrimitive() ||
            !holderValue.canAccess(holder) && !holderValue.trySetAccessible())
          throw new IllegalStateException("unqualified public Holder.value contract");
        Object bound=holderValue.invoke(holder);
        if (bound==null || !density.isInstance(bound))
          throw new IllegalStateException("stock holder does not resolve to DensityFunction");
        Class<?> boundType=bound.getClass();
        Method boundCompute=boundType.getMethod("compute",context);
        if (boundCompute.getReturnType()!=double.class)
          throw new IllegalStateException("bound stock holder's compute signature changed");
        OUT.println(HOLDER+seedIndex+"|"+id+"|"+depth+"|"+
            name(holder.getClass())+"|"+name(boundType)+"|"+
            name(boundCompute.getDeclaringClass()));
        if (++holderRows>64) throw new IllegalStateException("too many held density bindings");
      }
      ArrayList<String> childRows=new ArrayList<>(),opaqueRows=new ArrayList<>();
      if (expanded && type.isRecord()) {
        RecordComponent[] slots=type.getRecordComponents();
        if (slots==null || slots.length>32)
          throw new IllegalStateException("unbounded stock density record component count");
        for (int slotIndex=0;slotIndex<slots.length;slotIndex++) {
          RecordComponent slot=slots[slotIndex];
          String field=slot.getName();
          if (!field.matches("[a-zA-Z_$][a-zA-Z0-9_$]{0,100}"))
            throw new IllegalStateException("invalid density record child name");
          if (density.isAssignableFrom(slot.getType())) {
            Method accessor=slot.getAccessor();
            if (!accessor.canAccess(value) && !accessor.trySetAccessible())
              throw new IllegalStateException("stock density child accessor inaccessible");
            Object nested=accessor.invoke(value);
            if (nested==null || !density.isInstance(nested))
              throw new IllegalStateException("null typed density child");
            int childId=registerGraph(nested,depth+1,identities,nodes,depths);
            childRows.add(GRAPH_EDGE+seedIndex+"|"+id+"|"+slotIndex+"|"+field+"|"+childId);
          } else {
            // Do not even INVOKE non-density accessors: holders, spline
            // instances, noise parameters, constants and enums are opaque.
            opaqueRows.add(GRAPH_OPAQUE+seedIndex+"|"+id+"|"+slotIndex+"|"+
                field+"|"+name(slot.getType()));
          }
        }
      }
      OUT.println(GRAPH_NODE+seedIndex+"|"+id+"|"+depth+"|"+
          name(type)+"|"+name(compute.getDeclaringClass())+"|"+
          (expanded?"1":"0")+"|"+childRows.size()+"|"+opaqueRows.size());
      for (String row:childRows) OUT.println(row);
      for (String row:opaqueRows) OUT.println(row);
      edges+=childRows.size();
      opaques+=opaqueRows.size();
      if (edges>4096 || opaques>4096)
        throw new IllegalStateException("unbounded graph edge/opaque declarations");
    }
    OUT.println(GRAPH_END+seedIndex+"|"+nodes.size()+"|"+edges+"|"+opaques);
    if (holders) OUT.println(HOLDER_END+seedIndex+"|"+holderRows+"|"+nodes.size());
  }

  public static void main(String[] args) {
    try {
      if (args.length!=1 ||
          (!args[0].equals("--router-roots-4") &&
           !args[0].equals("--router-graph-4") &&
           !args[0].equals("--router-holder-4")))
        throw new IllegalArgumentException("expected --router-roots-4, --router-graph-4 or --router-holder-4");
      run(args[0]);
    } catch (Throwable t) {
      fail(t);
      System.exit(2);
    }
  }

  static void run(String mode) throws Exception {
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
      if (mode.equals("--router-roots-4")) inspect(i,routerType,density,context,router);
      else inspectGraph(i,routerType,density,context,router,
                        mode.equals("--router-holder-4"));
    }
    if (reader.readLine()!=null)
      throw new IllegalStateException("unexpected fifth world seed");
  }
}
