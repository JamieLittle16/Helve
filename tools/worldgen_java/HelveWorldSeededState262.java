// Original reflection-only receipt of stock Minecraft Java 26.2 registered
// noise parameters and prepared numeric sampler state. No game source copied.
// Never use this diagnostic transport as production generation authority.
import java.io.*;
import java.lang.reflect.*;
import java.nio.charset.StandardCharsets;
import java.util.*;

public final class HelveWorldSeededState262 {
  private static final String TAG = "HELVE26_2_REGISTERED_STATE|";
  private static final String FAILURE = "HELVE26_2_REGISTERED_STATE_FAILURE|";
  private static final PrintStream OUT = new PrintStream(
      new FileOutputStream(FileDescriptor.out), true, StandardCharsets.US_ASCII);
  private static String phase = "bootstrap";
  private static final String ROOT = "net.minecraft.world.level.levelgen.";
  private static final String[] KEYS = {"TEMPERATURE", "CONTINENTALNESS", "EROSION"};
  private static final int MAX_SLOTS = 64;
  private static int seedIndex, keyIndex;

  private static String clean(String input) {
    if (input == null) return "-";
    StringBuilder result = new StringBuilder();
    for (int i = 0; i < input.length() && i < 256; i++) {
      char c = input.charAt(i);
      result.append(c >= 32 && c <= 126 && c != '|' ? c : '_');
    }
    return result.toString();
  }
  private static void emit(String kind, String path, String name, String value) {
    if (!kind.matches("[IDAPLZE]") || !path.matches("[A-Za-z0-9_/\\[\\].-]{1,120}")
        || !name.matches("[A-Za-z0-9_]{1,80}")
        || !value.matches("[0-9a-f-]{1,512}"))
      throw new IllegalStateException("non-numeric/unbounded reflection receipt");
    OUT.println(TAG + seedIndex + "|" + keyIndex + "|" + kind + "|" + path
        + "|" + name + "|" + value);
  }
  private static String bits(double value) {
    return String.format(Locale.ROOT, "%016x", Double.doubleToRawLongBits(value));
  }
  private static Field[] fields(Class<?> type) {
    Field[] result = type.getDeclaredFields();
    Arrays.sort(result, Comparator.comparing(Field::getName));
    return result;
  }
  private static void improved(Object source, Class<?> improved, String path)
      throws Exception {
    int doubles = 0, permutations = 0;
    for (Field f : fields(improved)) {
      if (Modifier.isStatic(f.getModifiers())) continue;
      f.setAccessible(true);
      if (f.getType() == double.class) {
        emit("D", path, f.getName(), bits(f.getDouble(source)));
        doubles++;
      } else if (f.getType().isArray() &&
          (f.getType().getComponentType() == byte.class ||
           f.getType().getComponentType() == int.class)) {
        Object array = f.get(source);
        if (Array.getLength(array) != 256)
          throw new IllegalStateException("permutation length changed");
        StringBuilder bytes = new StringBuilder(512);
        boolean[] seen = new boolean[256];
        for (int j = 0; j < 256; j++) {
          int n = ((Number)Array.get(array,j)).intValue() & 255;
          if (seen[n]) throw new IllegalStateException("duplicate permutation entry");
          seen[n] = true;
          bytes.append(String.format(Locale.ROOT,"%02x",n));
        }
        emit("P", path, f.getName(), bytes.toString());
        permutations++;
      }
    }
    if (doubles != 3 || permutations != 1)
      throw new IllegalStateException("unexpected ImprovedNoise numeric layout");
  }
  private static void perlin(Object source, Class<?> perlin, Class<?> improved,
                             Class<?> doubleList, String path) throws Exception {
    int lists = 0, arrays = 0, octaveInts = 0;
    for (Field f : fields(perlin)) {
      if (Modifier.isStatic(f.getModifiers())) continue;
      f.setAccessible(true);
      Class<?> type = f.getType();
      Object value = f.get(source);
      if (type == int.class) {
        emit("I",path,f.getName(),Integer.toString(f.getInt(source)));
        octaveInts++;
      } else if (type == double.class) {
        emit("D",path,f.getName(),bits(f.getDouble(source)));
      } else if (doubleList.isAssignableFrom(type)) {
        lists++;
        int count = ((Number)doubleList.getMethod("size").invoke(value)).intValue();
        if (count < 1 || count > MAX_SLOTS) throw new IllegalStateException("amplitude span");
        emit("L",path,f.getName(),Integer.toString(count));
        Method get = doubleList.getMethod("getDouble",int.class);
        for (int i=0; i<count; i++)
          emit("A",path,f.getName()+"_"+i,
              bits(((Number)get.invoke(value,i)).doubleValue()));
      } else if (type.isArray() && type.getComponentType() == improved) {
        arrays++;
        int count = Array.getLength(value);
        if (count < 1 || count > MAX_SLOTS) throw new IllegalStateException("octave span");
        emit("L",path,f.getName(),Integer.toString(count));
        for (int i=0; i<count; i++) {
          String member = path+"/"+f.getName()+"["+i+"]";
          Object octave = Array.get(value,i);
          if (octave == null) emit("Z",member,"absent","0");
          else improved(octave,improved,member);
        }
      }
    }
    if (lists != 1 || arrays != 1 || octaveInts != 1)
      throw new IllegalStateException("unexpected PerlinNoise numeric layout");
  }
  private static void parameters(Object value, Class<?> type, Class<?> doubleList)
      throws Exception {
    int ints=0, lists=0;
    for (Field f : fields(type)) {
      if (Modifier.isStatic(f.getModifiers())) continue;
      f.setAccessible(true);
      if (f.getType() == int.class) {
        emit("I","parameters",f.getName(),Integer.toString(f.getInt(value)));
        ints++;
      } else if (doubleList.isAssignableFrom(f.getType())) {
        lists++;
        Object amps = f.get(value);
        int count = ((Number)doubleList.getMethod("size").invoke(amps)).intValue();
        if (count < 1 || count > MAX_SLOTS) throw new IllegalStateException("parameter span");
        emit("L","parameters",f.getName(),Integer.toString(count));
        Method get = doubleList.getMethod("getDouble",int.class);
        for (int i=0; i<count; i++)
          emit("A","parameters",f.getName()+"_"+i,
              bits(((Number)get.invoke(amps,i)).doubleValue()));
      }
    }
    if (ints != 1 || lists != 1)
      throw new IllegalStateException("unexpected official NoiseParameters layout");
  }
  private static void normal(Object source, Class<?> normal, Class<?> perlin,
                             Class<?> improved, Class<?> doubleList) throws Exception {
    int branches = 0;
    for (Field f : fields(normal)) {
      if (Modifier.isStatic(f.getModifiers())) continue;
      f.setAccessible(true);
      if (f.getType() == double.class)
        emit("D","normal",f.getName(),bits(f.getDouble(source)));
      else if (f.getType() == perlin) {
        branches++;
        perlin(f.get(source),perlin,improved,doubleList,"normal/"+f.getName());
      }
    }
    if (branches != 2) throw new IllegalStateException("not two Perlin branches");
  }
  private static void run() throws Exception {
    phase = "bootstrap";
    HelveWorldSeededDensity262.bootstrap();
    phase = "stock-runtime-classes";
    Class<?> lookup = Class.forName("net.minecraft.core.HolderLookup$Provider");
    Class<?> provider = Class.forName("net.minecraft.core.HolderGetter$Provider");
    Class<?> getter = Class.forName("net.minecraft.core.HolderGetter");
    Class<?> registryKey = Class.forName("net.minecraft.resources.ResourceKey");
    Class<?> holder = Class.forName("net.minecraft.core.Holder");
    Class<?> vanilla = Class.forName("net.minecraft.data.registries.VanillaRegistries");
    Class<?> registries = Class.forName("net.minecraft.core.registries.Registries");
    Class<?> settings = Class.forName(ROOT+"NoiseGeneratorSettings");
    Class<?> stateClass = Class.forName(ROOT+"RandomState");
    Class<?> noises = Class.forName(ROOT+"Noises");
    Class<?> normal = Class.forName(ROOT+"synth.NormalNoise");
    Class<?> parameters = Class.forName(ROOT+"synth.NormalNoise$NoiseParameters");
    Class<?> perlin = Class.forName(ROOT+"synth.PerlinNoise");
    Class<?> improved = Class.forName(ROOT+"synth.ImprovedNoise");
    Class<?> doubles = Class.forName("it.unimi.dsi.fastutil.doubles.DoubleList");

    phase = "stock-registry-createLookup";
    Object stock = HelveWorldSeededDensity262.checkedStatic(
        vanilla,"createLookup",lookup).invoke(null);
    if (!provider.isAssignableFrom(lookup) || stock == null || !provider.isInstance(stock))
      throw new IllegalStateException("not the same official stock provider");
    phase = "stock-registered-holder";
    Method lookupNoise = HelveWorldSeededDensity262.getNoiseRegistry(
        provider,registryKey,getter);
    Object noiseGetter = lookupNoise.invoke(stock,
        HelveWorldSeededDensity262.field(registries,"NOISE",registryKey));
    Method getRef = getter.getMethod("getOrThrow",registryKey);
    Method holderValue = holder.getMethod("value");
    if (!parameters.isAssignableFrom(holderValue.getReturnType()) &&
        holderValue.getReturnType() != Object.class)
      throw new IllegalStateException("holder value shape changed");
    Method create = HelveWorldSeededDensity262.checkedStatic(
        stateClass,"create",stateClass,provider,registryKey,long.class);
    Method getNoise = stateClass.getMethod("getOrCreateNoise",registryKey);
    if (getNoise.getReturnType() != normal)
      throw new IllegalStateException("noise type changed");
    Object overworld = HelveWorldSeededDensity262.field(settings,"OVERWORLD",registryKey);

    BufferedReader input = new BufferedReader(new InputStreamReader(
        System.in,StandardCharsets.US_ASCII));
    for (seedIndex = 0; seedIndex < 5; seedIndex++) {
      String line = input.readLine();
      if (line == null) throw new IllegalStateException("missing signed worldseed");
      long seed = HelveWorldSeededDensity262.bits(line);
      phase = "stock-randomstate";
      Object state = create.invoke(null,stock,overworld,seed);
      for (keyIndex=0; keyIndex<KEYS.length; keyIndex++) {
        Object key = HelveWorldSeededDensity262.field(noises,KEYS[keyIndex],registryKey);
        Object resolved = getRef.invoke(noiseGetter,key);
        if (resolved == null || !holder.isInstance(resolved))
          throw new IllegalStateException("not a stock registered holder");
        Object params = holderValue.invoke(resolved);
        if (!parameters.isInstance(params)) throw new IllegalStateException("wrong registry value");
        phase = "registered-parameters";
        parameters(params,parameters,doubles);
        phase = "randomstate-prepared-noise";
        Object prepared = getNoise.invoke(state,key);
        if (prepared == null || !normal.isInstance(prepared))
          throw new IllegalStateException("missing prepared normal sampler");
        normal(prepared,normal,perlin,improved,doubles);
        emit("E","sample","complete","1");
      }
    }
    if (input.readLine() != null)
      throw new IllegalStateException("unexpected extra worldseed request");
  }
  public static void main(String[] args) {
    try {
      if (args.length != 0) throw new IllegalArgumentException("no command arguments");
      run();
    } catch (Throwable failure) {
      Throwable root = failure;
      for (int i=0; i<16 && root.getCause()!=null && root.getCause()!=root; i++)
        root=root.getCause();
      OUT.println(FAILURE+clean(phase)+"|"+clean(root.getClass().getName())+"|"+
                  clean(root.getMessage()));
      OUT.flush();
      System.exit(2);
    }
  }
}
