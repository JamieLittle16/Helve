// Original source-free Java 26.2 bridge: inspect a real stock registry and
// evaluate a real world-seed RandomState-bound DensityFunctions$Noise node.
// No Mojang implementation code is reproduced or generated here.
import java.io.*;
import java.lang.reflect.*;
import java.nio.charset.StandardCharsets;
import java.util.*;

public final class HelveWorldSeededDensity262 {
  private static final String PREFIX = "HELVE26_2_WORLD_SEED_DENSITY|";
  private static final String FAILURE = "HELVE26_2_WORLD_SEED_FAILURE|";
  // Original source-free debugging phases; no Minecraft source is serialized.
  private static String phase = "bootstrap";
  private static final PrintStream RESULT = new PrintStream(
      new FileOutputStream(FileDescriptor.out), true, StandardCharsets.US_ASCII);
  private static final String ROOT = "net.minecraft.world.level.levelgen.";
  private static final String[] KEYS = {"TEMPERATURE", "CONTINENTALNESS", "EROSION"};

  static long bits(String raw) {
    if (!raw.matches("0x[0-9a-f]{16}"))
      throw new IllegalArgumentException("world-seed bits not 16-digit lowercase hex");
    return Long.parseUnsignedLong(raw.substring(2), 16);
  }
  static double scale(String profile, boolean vertical) {
    if (profile.equals("unit")) return 1.0;
    if (profile.equals("quarter_xz")) return vertical ? 1.0 : 0.25;
    if (profile.equals("quarter_xz_half_y")) return vertical ? 0.5 : 0.25;
    throw new IllegalArgumentException("unknown scaling profile");
  }
  static Method checkedStatic(Class<?> owner, String name,
                              Class<?> returns, Class<?>... params) throws Exception {
    Method method=owner.getMethod(name, params);
    if (!Modifier.isStatic(method.getModifiers()) || method.getReturnType()!=returns)
      throw new IllegalStateException("official JVM static method contract changed: "+name);
    return method;
  }
  static Object field(Class<?> owner, String name, Class<?> type) throws Exception {
    Field value=owner.getField(name);
    if (!Modifier.isStatic(value.getModifiers()) || value.getType()!=type)
      throw new IllegalStateException("official registry field shape changed: "+name);
    return value.get(null);
  }
  static Method getNoiseRegistry(Class<?> owner, Class<?> key,
                                 Class<?> getter) throws Exception {
    Method selected=null;
    for (String name : new String[]{"lookupOrThrow","getOrThrow"}) {
      try {
        Method method=owner.getMethod(name,key);
        if (!getter.isAssignableFrom(method.getReturnType())) continue;
        if (selected != null)
          throw new IllegalStateException("ambiguous official registry getter API");
        selected=method;
      } catch (NoSuchMethodException absent) { /* try the other exact spelling */ }
    }
    if (selected==null) throw new IllegalStateException("no typed stock NOISE registry accessor");
    return selected;
  }
  static void bootstrap() throws Exception {
    Class<?> constants=Class.forName("net.minecraft.SharedConstants");
    checkedStatic(constants,"tryDetectVersion",void.class).invoke(null);
    Class<?> boot=Class.forName("net.minecraft.server.Bootstrap");
    checkedStatic(boot,"bootStrap",void.class).invoke(null);
  }

  private static String clean(String value) {
    if (value == null || value.isEmpty()) return "-";
    StringBuilder text = new StringBuilder();
    for (int i=0; i<value.length() && text.length()<700; i++) {
      char c=value.charAt(i);
      text.append(c>=32 && c<=126 && c!='|' ? c : '_');
    }
    return text.toString();
  }

  static void reportFailure(Throwable problem) {
    Throwable deepest=problem;
    for (int depth=0; depth<16; depth++) {
      Throwable next=deepest.getCause();
      if (next==null || next==deepest) break;
      deepest=next;
    }
    // Direct FileDescriptor.out avoids both Minecraft's redirected System.out
    // AND an uncaught exception handler which may intercept System.err.
    RESULT.println(FAILURE + clean(phase) + "|" +
        clean(deepest.getClass().getName()) + "|" +
        clean(problem.getClass().getName()) + "|" + clean(deepest.getMessage()));
    RESULT.flush();
  }

  public static void main(String[] args) {
    try {
      int expected;
      if (args.length==0) expected=1440; // Original frozen full corpus, unchanged.
      else if (args.length==1 && args[0].equals("--heldout-576")) expected=576;
      else throw new IllegalArgumentException("unapproved bounded JVM capture mode");
      run(expected);
    } catch (Throwable failure) {
      reportFailure(failure);
      System.exit(2);
    }
  }

  private static void run(int expected) throws Exception {
    phase="bootstrap";
    bootstrap();
    phase="resolve-runtime-classes";
    Class<?> vanilla=Class.forName("net.minecraft.data.registries.VanillaRegistries");
    Class<?> lookup=Class.forName("net.minecraft.core.HolderLookup$Provider");
    Class<?> getterProvider=Class.forName("net.minecraft.core.HolderGetter$Provider");
    Class<?> getter=Class.forName("net.minecraft.core.HolderGetter");
    Class<?> resourceKey=Class.forName("net.minecraft.resources.ResourceKey");
    Class<?> holder=Class.forName("net.minecraft.core.Holder");
    Class<?> normal=Class.forName(ROOT+"synth.NormalNoise");
    Class<?> settings=Class.forName(ROOT+"NoiseGeneratorSettings");
    Class<?> stateType=Class.forName(ROOT+"RandomState");
    Class<?> noises=Class.forName(ROOT+"Noises");
    Class<?> registries=Class.forName("net.minecraft.core.registries.Registries");
    Class<?> noiseHolder=Class.forName(ROOT+"DensityFunction$NoiseHolder");
    Class<?> densityNode=Class.forName(ROOT+"DensityFunctions$Noise");
    Class<?> context=Class.forName(ROOT+"DensityFunction$FunctionContext");
    Class<?> point=Class.forName(ROOT+"DensityFunction$SinglePointContext");

    // This is the actual stock registry builder. No synthetic HolderGetter,
    // manually invented parameters or Holder.direct(...) is used.
    phase="stock-registry-createLookup";
    Object stock=checkedStatic(vanilla,"createLookup",lookup).invoke(null);
    // In 26.2 HolderLookup.Provider already extends HolderGetter.Provider.
    // The legacy asGetterLookup() adapter does not exist. Verify the real
    // runtime subtype relation AND the actual stock instance before passing
    // it to RandomState: no fake getter, wrapper or registry is introduced.
    phase="stock-registry-provider-subtype";
    if (!getterProvider.isAssignableFrom(lookup))
      throw new IllegalStateException(
          "official HolderLookup.Provider is not a HolderGetter.Provider");
    if (stock==null || !getterProvider.isInstance(stock))
      throw new IllegalStateException(
          "official stock HolderLookup.Provider is not a HolderGetter.Provider instance");
    Object holders=stock;
    phase="noise-registry-resolve";
    Method noiseRegistry=getNoiseRegistry(getterProvider,resourceKey,getter);
    phase="noise-registry-lookup";
    Object noiseGetter=noiseRegistry.invoke(holders,field(registries,"NOISE",resourceKey));
    Method getRef=getter.getMethod("getOrThrow",resourceKey);
    if (!holder.isAssignableFrom(getRef.getReturnType()))
      throw new IllegalStateException("real registry cannot produce a holder reference");

    phase="world-settings-and-methods";
    Object settingsKey=field(settings,"OVERWORLD",resourceKey);
    Method makeState=checkedStatic(stateType,"create",stateType,
        getterProvider,resourceKey,long.class);
    Method getNoise=stateType.getMethod("getOrCreateNoise",resourceKey);
    if (getNoise.getReturnType()!=normal)
      throw new IllegalStateException("RandomState noise output class changed");
    Constructor<?> heldCtor=noiseHolder.getDeclaredConstructor(holder,normal);
    Constructor<?> densityCtor=densityNode.getDeclaredConstructor(noiseHolder,double.class,double.class);
    Constructor<?> pointCtor=point.getDeclaredConstructor(int.class,int.class,int.class);
    Method compute=densityNode.getMethod("compute",context);
    if (compute.getReturnType()!=double.class)
      throw new IllegalStateException("noise density compute output is not a double");
    for (Constructor<?> c:new Constructor<?>[]{heldCtor,densityCtor,pointCtor})
      c.setAccessible(true);

    phase="start-sampling";
    Map<String,Object> states=new HashMap<>();
    Map<String,Object> nodes=new HashMap<>();
    BufferedReader in=new BufferedReader(
        new InputStreamReader(System.in,StandardCharsets.US_ASCII));
    String line;
    int index=0;
    while ((line=in.readLine())!=null) {
      String[] v=line.split("\\t",-1);
      if (v.length!=6 || index>=expected)
        throw new IllegalStateException("invalid world-seed noise request framing");
      String profile=v[0], seed=v[1], keyName=v[2];
      if (!Arrays.asList(KEYS).contains(keyName))
        throw new IllegalStateException("unapproved built-in noise key");
      double xz=scale(profile,false), y=scale(profile,true);
      long worldSeed=bits(seed);
      Object state=states.get(seed);
      if (state==null) {
        phase="create-stock-worldseed-randomstate";
        state=makeState.invoke(null,holders,settingsKey,worldSeed);
        states.put(seed,state);
      }
      String cacheKey=profile+"/"+seed+"/"+keyName;
      Object density=nodes.get(cacheKey);
      if (density==null) {
        Object key=field(noises,keyName,resourceKey);
        phase="resolve-registered-noise-holder";
        Object registered=getRef.invoke(noiseGetter,key);
        if (registered==null || !holder.isInstance(registered))
          throw new IllegalStateException("official key is missing from stock registry");
        phase="randomstate-getOrCreateNoise";
        Object noise=getNoise.invoke(state,key);
        if (noise==null || !normal.isInstance(noise))
          throw new IllegalStateException("official RandomState returned no registered noise");
        phase="construct-noise-density-node";
        Object held=heldCtor.newInstance(registered,noise);
        density=densityCtor.newInstance(held,xz,y);
        nodes.put(cacheKey,density);
      }
      Object at=pointCtor.newInstance(Integer.parseInt(v[3]),
          Integer.parseInt(v[4]),Integer.parseInt(v[5]));
      phase="compute-noise-density-value";
      double value=(Double)compute.invoke(density,at);
      RESULT.println(PREFIX+index+"|"+
          String.format(Locale.ROOT,"%016x",Double.doubleToRawLongBits(value)));
      index++;
    }
    if (index!=expected) throw new IllegalStateException("incomplete bounded worldseed oracle");
  }
}
