// Independent mixed-noise/gradient/constant 26.2 capture; Minecraft's own
// stock registries, RandomState and DensityFunctions factories evaluate ALL
// numerical results. This is ONLY reflection, never reimplemented Mojang math.
// Reuse existing pinned HelveWorldSeededDensity262 typed reflection helpers.
import java.io.*;
import java.lang.reflect.*;
import java.nio.charset.StandardCharsets;
import java.util.*;

public final class HelveStockMixedDensity262 {
  static final String ROOT = "net.minecraft.world.level.levelgen.";
  static final String BITS = "HELVE26_2_STOCK_MIXED_BITS|";
  static final String DELEGATE = "HELVE26_2_STOCK_MIXED_DELEGATE|";
  static final String FAILURE = "HELVE26_2_STOCK_MIXED_FAILURE|";
  static final String[] KEYS = {"TEMPERATURE", "CONTINENTALNESS", "EROSION"};
  static final String[] PROFILES = {
      "add_noise_gradient", "add_gradient_noise",
      "mul_noise_gradient", "mul_gradient_noise",
      "add_noise_negative_zero", "add_negative_zero_noise",
      "mul_noise_negative_zero", "mul_negative_zero_noise",
      "mul_noise_half", "mul_half_noise"
  };
  static final PrintStream RESULT = new PrintStream(
      new FileOutputStream(FileDescriptor.out), true, StandardCharsets.US_ASCII);
  static String phase = "bootstrap";

  static String clean(String raw) {
    if (raw == null) return "-";
    StringBuilder out = new StringBuilder();
    for (int i=0; i<raw.length() && out.length()<500; i++) {
      char c=raw.charAt(i);
      out.append(c>=32 && c<=126 && c!='|' ? c : '_');
    }
    return out.toString();
  }
  static void fail(Throwable problem) {
    Throwable deepest=problem;
    for (int i=0; i<16; i++) {
      if (deepest.getCause()==null || deepest.getCause()==deepest) break;
      deepest=deepest.getCause();
    }
    RESULT.println(FAILURE + clean(phase) + "|" + clean(deepest.getClass().getName()) +
        "|" + clean(problem.getClass().getName()) + "|" + clean(deepest.getMessage()));
    RESULT.flush();
  }
  static String className(Class<?> cls) {return cls==null ? "-" : cls.getName();}
  static void emitDelegate(String profile, Object expression, Class<?> context) throws Exception {
    Class<?> type=expression.getClass();
    Method compute=type.getMethod("compute", context);
    RESULT.println(DELEGATE + profile + "|" + className(type) + "|" +
        className(compute.getDeclaringClass()) + "|" + className(type.getSuperclass()));
  }
  static boolean profileIsApproved(String profile) {
    for (String known: PROFILES) if (known.equals(profile)) return true;
    return false;
  }
  static boolean keyIsApproved(String key) {
    for (String known: KEYS) if (known.equals(key)) return true;
    return false;
  }
  static Object composed(String profile, Object noise, Object gradient,
                         Object negativeZero, Object half, Method add, Method multiply)
      throws Exception {
    Object first, second;
    if (profile.equals("add_noise_gradient") || profile.equals("mul_noise_gradient")) {
      first=noise; second=gradient;
    } else if (profile.equals("add_gradient_noise") || profile.equals("mul_gradient_noise")) {
      first=gradient; second=noise;
    } else if (profile.equals("add_noise_negative_zero") || profile.equals("mul_noise_negative_zero")) {
      first=noise; second=negativeZero;
    } else if (profile.equals("add_negative_zero_noise") || profile.equals("mul_negative_zero_noise")) {
      first=negativeZero; second=noise;
    } else if (profile.equals("mul_noise_half")) {
      first=noise; second=half;
    } else if (profile.equals("mul_half_noise")) {
      first=half; second=noise;
    } else throw new IllegalArgumentException("not a pinned mixed composition profile");
    return profile.startsWith("add_")
        ? add.invoke(null, first, second) : multiply.invoke(null, first, second);
  }

  public static void main(String[] args) {
    try {
      if (args.length!=1 || !args[0].equals("--mixed-1920"))
        throw new IllegalArgumentException("expected ONLY --mixed-1920");
      run();
    } catch (Throwable problem) {
      fail(problem);
      System.exit(2);
    }
  }

  static void run() throws Exception {
    phase="bootstrap";
    HelveWorldSeededDensity262.bootstrap();
    phase="resolve-official-contracts";
    Class<?> vanilla=Class.forName("net.minecraft.data.registries.VanillaRegistries");
    Class<?> lookup=Class.forName("net.minecraft.core.HolderLookup$Provider");
    Class<?> getterProvider=Class.forName("net.minecraft.core.HolderGetter$Provider");
    Class<?> getter=Class.forName("net.minecraft.core.HolderGetter");
    Class<?> holder=Class.forName("net.minecraft.core.Holder");
    Class<?> resourceKey=Class.forName("net.minecraft.resources.ResourceKey");
    Class<?> registries=Class.forName("net.minecraft.core.registries.Registries");
    Class<?> settings=Class.forName(ROOT+"NoiseGeneratorSettings");
    Class<?> stateClass=Class.forName(ROOT+"RandomState");
    Class<?> noises=Class.forName(ROOT+"Noises");
    Class<?> normal=Class.forName(ROOT+"synth.NormalNoise");
    Class<?> noiseHolder=Class.forName(ROOT+"DensityFunction$NoiseHolder");
    Class<?> noiseNode=Class.forName(ROOT+"DensityFunctions$Noise");
    Class<?> density=Class.forName(ROOT+"DensityFunction");
    Class<?> context=Class.forName(ROOT+"DensityFunction$FunctionContext");
    Class<?> point=Class.forName(ROOT+"DensityFunction$SinglePointContext");
    Class<?> funcs=Class.forName(ROOT+"DensityFunctions");

    Method makeState=HelveWorldSeededDensity262.checkedStatic(
        stateClass,"create",stateClass,getterProvider,resourceKey,long.class);
    Method getNoise=stateClass.getMethod("getOrCreateNoise",resourceKey);
    if (getNoise.getReturnType()!=normal || !density.isAssignableFrom(noiseNode))
      throw new IllegalStateException("26.2 stock RandomState/noise DensityFunction contract changed");
    Method add=HelveWorldSeededDensity262.checkedStatic(
        funcs,"add",density,density,density);
    Method mul=HelveWorldSeededDensity262.checkedStatic(
        funcs,"mul",density,density,density);
    Method constant=HelveWorldSeededDensity262.checkedStatic(
        funcs,"constant",density,double.class);
    Method gradientMethod=HelveWorldSeededDensity262.checkedStatic(
        funcs,"yClampedGradient",density,int.class,int.class,double.class,double.class);
    Method compute=density.getMethod("compute",context);
    if (compute.getReturnType()!=double.class)
      throw new IllegalStateException("26.2 DensityFunction.compute return type changed");
    Constructor<?> heldCtor=noiseHolder.getDeclaredConstructor(holder,normal);
    Constructor<?> noiseCtor=noiseNode.getDeclaredConstructor(noiseHolder,double.class,double.class);
    Constructor<?> pointCtor=point.getDeclaredConstructor(int.class,int.class,int.class);
    for (Constructor<?> c:new Constructor<?>[]{heldCtor,noiseCtor,pointCtor}) c.setAccessible(true);

    // Source-grounded parameter bits from the independently observed
    // 26.2 YClampedGradient and Constant primitive captures.
    Object gradient=gradientMethod.invoke(null,-64,320,-1.0,1.0);
    Object negativeZero=constant.invoke(null,Double.longBitsToDouble(0x8000000000000000L));
    Object half=constant.invoke(null,0.5);

    phase="stock-registry-createLookup";
    Object stock=HelveWorldSeededDensity262.checkedStatic(vanilla,"createLookup",lookup)
        .invoke(null);
    phase="stock-registry-provider-subtype";
    if (!getterProvider.isAssignableFrom(lookup) || !getterProvider.isInstance(stock))
      throw new IllegalStateException("26.2 real stock registry provider contract changed");
    phase="stock-noise-registry-lookup";
    Method noiseRegistry=HelveWorldSeededDensity262.getNoiseRegistry(
        getterProvider,resourceKey,getter);
    Object noiseGetter=noiseRegistry.invoke(
        stock,HelveWorldSeededDensity262.field(registries,"NOISE",resourceKey));
    Method getRef=getter.getMethod("getOrThrow",resourceKey);
    if (!holder.isAssignableFrom(getRef.getReturnType()))
      throw new IllegalStateException("26.2 stock registry no longer returns a holder");
    Object settingsKey=HelveWorldSeededDensity262.field(settings,"OVERWORLD",resourceKey);

    Map<String,Object> states=new HashMap<>();
    Map<String,Object> expressions=new HashMap<>();
    Set<String> delegateEmitted=new HashSet<>();
    BufferedReader input=new BufferedReader(
        new InputStreamReader(System.in,StandardCharsets.US_ASCII));
    int index=0;
    for (String line; (line=input.readLine())!=null;) {
      String[] row=line.split("\t",-1);
      if (row.length!=6 || index>=1920)
        throw new IllegalStateException("exactly 1920 six-column mixed requests required");
      String profile=row[0], seed=row[1], keyName=row[2];
      if (!profileIsApproved(profile) || !keyIsApproved(keyName))
        throw new IllegalArgumentException("unapproved composition profile or noise key");
      long seedBits=HelveWorldSeededDensity262.bits(seed);
      Object state=states.get(seed);
      if (state==null) {
        phase="stock-randomstate-create";
        state=makeState.invoke(null,stock,settingsKey,seedBits);
        states.put(seed,state);
      }
      String cacheKey=profile+"/"+seed+"/"+keyName;
      Object expression=expressions.get(cacheKey);
      if (expression==null) {
        Object key=HelveWorldSeededDensity262.field(noises,keyName,resourceKey);
        phase="stock-noise-holder";
        Object registered=getRef.invoke(noiseGetter,key);
        if (!holder.isInstance(registered))
          throw new IllegalStateException("stock noise registry has no holder");
        phase="seeded-noise-instantiation";
        Object sampled=getNoise.invoke(state,key);
        if (!normal.isInstance(sampled))
          throw new IllegalStateException("RandomState did not instantiate stock NormalNoise");
        Object bound=noiseCtor.newInstance(
            heldCtor.newInstance(registered,sampled),0.25,0.5);
        phase="official-mixed-factory";
        expression=composed(profile,bound,gradient,negativeZero,half,add,mul);
        if (!density.isInstance(expression))
          throw new IllegalStateException("stock mixed density factory returned wrong type");
        expressions.put(cacheKey,expression);
        if (delegateEmitted.add(profile)) emitDelegate(profile,expression,context);
      }
      phase="official-mixed-compute";
      Object at=pointCtor.newInstance(Integer.parseInt(row[3]),
          Integer.parseInt(row[4]),Integer.parseInt(row[5]));
      double observed=(Double)compute.invoke(expression,at);
      RESULT.println(BITS+index+"|"+
          String.format(Locale.ROOT,"%016x",Double.doubleToRawLongBits(observed)));
      index++;
    }
    if (index!=1920 || delegateEmitted.size()!=PROFILES.length)
      throw new IllegalStateException("incomplete official stock mixed-density sample or delegate inventory");
  }
}
