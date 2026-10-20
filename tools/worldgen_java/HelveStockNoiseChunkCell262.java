// Actual 26.2 Overworld bound finalDensity inside a stock NoiseChunk cell.
// Read-only original Minecraft evaluation. Does not rebuild density math,
// invent a registry, substitute SinglePointContext, or execute a Rust kernel.
// Abort if the exact version-specific constructor or lifecycle differs.
import java.io.*;
import java.lang.reflect.*;
import java.nio.charset.StandardCharsets;
import java.util.*;

public final class HelveStockNoiseChunkCell262 {
  static final String ROOT="net.minecraft.world.level.levelgen.";
  static final String HEAD="HELVE26_2_NOISECHUNK_CELL_HEAD|";
  static final String BIT="HELVE26_2_NOISECHUNK_CELL_BITS|";
  static final String END="HELVE26_2_NOISECHUNK_CELL_END|";
  static final String FAIL="HELVE26_2_NOISECHUNK_CELL_FAILURE|";
  static final PrintStream OUT=new PrintStream(
      new FileOutputStream(FileDescriptor.out),true,StandardCharsets.US_ASCII);
  static final int[][] POINTS={{0,64,0},{1,65,1},{2,66,2},{3,67,3}};
  static String phase="bootstrap";

  static String clean(String s) {
    if(s==null||s.isEmpty())return "-";
    StringBuilder b=new StringBuilder();
    for(int i=0;i<s.length()&&b.length()<400;i++){
      char c=s.charAt(i);b.append(c>=32&&c<=126&&c!='|'?c:'_');
    }
    return b.toString();
  }
  static void fail(Throwable t) {
    Throwable inner=t;
    for(int i=0;i<16&&inner.getCause()!=null&&inner.getCause()!=inner;i++)
      inner=inner.getCause();
    OUT.println(FAIL+clean(phase)+"|"+clean(inner.getClass().getName())+
       "|"+clean(t.getClass().getName())+"|"+clean(inner.getMessage()));
  }
  static Method openMethod(Class<?> owner,String name,Class<?> returns,Class<?>...params)
      throws Exception {
    Method m=owner.getDeclaredMethod(name,params);
    if(m.getReturnType()!=returns||!m.trySetAccessible())
      throw new IllegalStateException("unqualified original method: "+owner.getName()+"."+name);
    return m;
  }
  static Object accessor(Class<?> type,Object owner,String field) throws Exception {
    if(!type.isRecord())throw new IllegalStateException("stock record changed: "+type);
    for(RecordComponent c:type.getRecordComponents()) {
      if(c.getName().equals(field)){
        Method m=c.getAccessor();
        if(!m.canAccess(owner)&&!m.trySetAccessible())
          throw new IllegalAccessException("inaccessible stock record accessor: "+field);
        return m.invoke(owner);
      }
    }
    throw new IllegalStateException("missing stock record field: "+field);
  }
  public static void main(String[] args) {
    try {
      if(args.length!=1||!args[0].equals("--stock-noisechunk-cell-16"))
        throw new IllegalArgumentException("only --stock-noisechunk-cell-16");
      run();
    } catch(Throwable t){fail(t);System.exit(2);}
  }
  static void run() throws Exception {
    phase="bootstrap";HelveWorldSeededDensity262.bootstrap();
    phase="stock-version-class-contract";
    Class<?> vanilla=Class.forName("net.minecraft.data.registries.VanillaRegistries");
    Class<?> lookup=Class.forName("net.minecraft.core.HolderLookup$Provider");
    Class<?> getterProvider=Class.forName("net.minecraft.core.HolderGetter$Provider");
    Class<?> getter=Class.forName("net.minecraft.core.HolderGetter");
    Class<?> key=Class.forName("net.minecraft.resources.ResourceKey");
    Class<?> holder=Class.forName("net.minecraft.core.Holder");
    Class<?> registries=Class.forName("net.minecraft.core.registries.Registries");
    Class<?> generatorSettings=Class.forName(ROOT+"NoiseGeneratorSettings");
    Class<?> noiseSettingsClass=Class.forName(ROOT+"NoiseSettings");
    Class<?> stateType=Class.forName(ROOT+"RandomState");
    Class<?> routerClass=Class.forName(ROOT+"NoiseRouter");
    Class<?> density=Class.forName(ROOT+"DensityFunction");
    Class<?> context=Class.forName(ROOT+"DensityFunction$FunctionContext");
    Class<?> noiseChunk=Class.forName(ROOT+"NoiseChunk");
    Class<?> markerInterface=Class.forName(ROOT+"DensityFunctions$BeardifierOrMarker");
    Class<?> markerEnum=Class.forName(ROOT+"DensityFunctions$BeardifierMarker");
    Class<?> fluidPicker=Class.forName(ROOT+"Aquifer$FluidPicker");
    Class<?> blender=Class.forName(ROOT+"blending.Blender");
    Class<?> chunkGen=Class.forName(ROOT+"NoiseBasedChunkGenerator");
    if(!context.isAssignableFrom(noiseChunk)||!markerInterface.isAssignableFrom(markerEnum)
        || !getterProvider.isAssignableFrom(lookup))
      throw new IllegalStateException("26.2 stock chunk-context subtype changed");

    Method createState=HelveWorldSeededDensity262.checkedStatic(
        stateType,"create",stateType,getterProvider,key,long.class);
    Method getRouter=stateType.getMethod("router");
    Method compute=density.getMethod("compute",context);
    Method getRegistry=HelveWorldSeededDensity262.getNoiseRegistry(
        getterProvider,key,getter);
    Method getHolder=getter.getMethod("getOrThrow",key);
    Method getValue=holder.getMethod("value");
    Method empty=HelveWorldSeededDensity262.checkedStatic(blender,"empty",blender);
    Method noiseWidth=noiseSettingsClass.getMethod("getCellWidth");
    Method noiseHeight=noiseSettingsClass.getMethod("getCellHeight");
    Method minY=noiseSettingsClass.getMethod("minY");
    Method height=noiseSettingsClass.getMethod("height");
    if(noiseWidth.getReturnType()!=int.class||noiseHeight.getReturnType()!=int.class
        ||minY.getReturnType()!=int.class||height.getReturnType()!=int.class
        ||getValue.getParameterCount()!=0)
      throw new IllegalStateException("wrong actual 26.2 chunk sampling settings API");
    Constructor<?> ctor=noiseChunk.getDeclaredConstructor(
        int.class,stateType,int.class,int.class,noiseSettingsClass,
        markerInterface,generatorSettings,fluidPicker,blender);
    if(!ctor.canAccess(null)&&!ctor.trySetAccessible())
      throw new IllegalAccessException("stock NoiseChunk constructor inaccessible");
    Method picker=openMethod(chunkGen,"createFluidPicker",fluidPicker,generatorSettings);
    if(!Modifier.isStatic(picker.getModifiers()))
      throw new IllegalStateException("stock fluid picker factory no longer static");
    Method wrap=openMethod(noiseChunk,"wrap",density,density);
    Method initialize=noiseChunk.getMethod("initializeForFirstCellX");
    Method advance=noiseChunk.getMethod("advanceCellX",int.class);
    Method select=noiseChunk.getMethod("selectCellYZ",int.class,int.class);
    Method updateY=noiseChunk.getMethod("updateForY",int.class,double.class);
    Method updateX=noiseChunk.getMethod("updateForX",int.class,double.class);
    Method updateZ=noiseChunk.getMethod("updateForZ",int.class,double.class);
    Method stop=noiseChunk.getMethod("stopInterpolation");
    if(compute.getReturnType()!=double.class||
        initialize.getReturnType()!=void.class||advance.getReturnType()!=void.class||
        select.getReturnType()!=void.class||updateX.getReturnType()!=void.class||
        updateY.getReturnType()!=void.class||updateZ.getReturnType()!=void.class||
        stop.getReturnType()!=void.class)
      throw new IllegalStateException("wrong 26.2 density-cell evaluation signatures");
    Object noBeard=HelveWorldSeededDensity262.field(markerEnum,"INSTANCE",markerEnum);
    Object noBlending=empty.invoke(null);
    if(!blender.isInstance(noBlending))
      throw new IllegalStateException("no official no-blending instance");
    phase="stock-VanillaRegistries-createLookup";
    Object provider=HelveWorldSeededDensity262.checkedStatic(
        vanilla,"createLookup",lookup).invoke(null);
    if(!getterProvider.isInstance(provider))
      throw new IllegalStateException("actual source registry type changed");
    Object registryKey=HelveWorldSeededDensity262.field(registries,"NOISE_SETTINGS",key);
    Object noiseGetter=getRegistry.invoke(provider,registryKey);
    Object overworldKey=HelveWorldSeededDensity262.field(generatorSettings,"OVERWORLD",key);
    Object heldSettings=getHolder.invoke(noiseGetter,overworldKey);
    Object settings=getValue.invoke(heldSettings);
    if(!generatorSettings.isInstance(settings))
      throw new IllegalStateException("real stock Overworld settings absent");
    Object shape=accessor(generatorSettings,settings,"noiseSettings");
    if(!noiseSettingsClass.isInstance(shape))
      throw new IllegalStateException("not original NoiseSettings");
    int cellW=(Integer)noiseWidth.invoke(shape),cellH=(Integer)noiseHeight.invoke(shape),
        yStart=(Integer)minY.invoke(shape),worldH=(Integer)height.invoke(shape);
    if(cellW!=4||cellH!=8||yStart!=-64||worldH!=384||16%cellW!=0)
      throw new IllegalStateException("actual Overworld noise cell geometry changed");
    Object stockPicker=picker.invoke(null,settings);
    if(!fluidPicker.isInstance(stockPicker))
      throw new IllegalStateException("original fluid picker type changed");
    BufferedReader reader=new BufferedReader(
        new InputStreamReader(System.in,StandardCharsets.US_ASCII));
    for(int si=0;si<4;si++){
      phase="stock-seed-"+si;
      String seed=reader.readLine();
      if(seed==null)throw new IllegalStateException("missing world-seed bits");
      long signed=HelveWorldSeededDensity262.bits(seed);
      Object state=createState.invoke(null,provider,overworldKey,signed);
      Object router=getRouter.invoke(state);
      if(!routerClass.isInstance(router)||!routerClass.isRecord())
        throw new IllegalStateException("stock RandomState router type changed");
      Object finalNode=accessor(routerClass,router,"finalDensity");
      if(finalNode==null||!finalNode.getClass().getName().equals(
         ROOT+"DensityFunctions$Ap2"))
        throw new IllegalStateException("stock finalDensity bound root changed");
      phase="construct-original-NoiseChunk-"+si;
      Object chunk=ctor.newInstance(16/cellW,state,0,0,shape,
           noBeard,settings,stockPicker,noBlending);
      Object wrapped=wrap.invoke(chunk,finalNode);
      if(!density.isInstance(wrapped))
        throw new IllegalStateException("stock NoiseChunk.wrap is not DensityFunction");
      OUT.println(HEAD+si+"|"+seed+"|"+cellW+"|"+cellH+"|"+yStart+"|"+worldH+"|"+
          wrapped.getClass().getName()+"|4");
      phase="original-NoiseChunk-initialize-"+si;
      initialize.invoke(chunk);
      advance.invoke(chunk,0);
      select.invoke(chunk,(64-yStart)/cellH,0);
      for(int pi=0;pi<POINTS.length;pi++){
        int x=POINTS[pi][0],y=POINTS[pi][1],z=POINTS[pi][2];
        phase="original-NoiseChunk-interpolate-"+si+"-"+pi;
        updateY.invoke(chunk,y,(double)Math.floorMod(y-yStart,cellH)/cellH);
        updateX.invoke(chunk,x,(double)Math.floorMod(x,cellW)/cellW);
        updateZ.invoke(chunk,z,(double)Math.floorMod(z,cellW)/cellW);
        double value=(Double)compute.invoke(wrapped,chunk);
        if(!Double.isFinite(value))
          throw new IllegalStateException("nonfinite original NoiseChunk density");
        OUT.println(BIT+(si*POINTS.length+pi)+"|"+
          String.format(Locale.ROOT,"%016x",Double.doubleToRawLongBits(value)));
      }
      stop.invoke(chunk);
      OUT.println(END+si+"|4");
    }
    if(reader.readLine()!=null)
      throw new IllegalStateException("unexpected extra stock world-seed input");
  }
}
