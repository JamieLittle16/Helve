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
  static final String ADJ_HEAD="HELVE26_2_NOISECHUNK_ADJACENT_HEAD|";
  static final String ADJ_BIT="HELVE26_2_NOISECHUNK_ADJACENT_BITS|";
  static final String ADJ_END="HELVE26_2_NOISECHUNK_ADJACENT_END|";
  static final PrintStream OUT=new PrintStream(
      new FileOutputStream(FileDescriptor.out),true,StandardCharsets.US_ASCII);
  static final int[][] POINTS={{0,64,0},{1,65,1},{2,66,2},{3,67,3}};
  // Separate, explicitly row-major Y/X/Z traversal of all positions in the
  // SAME bounded original 4x8x4 cell. No neighbouring-cell or slice claim.
  static final int[][] CELL_GRID=completeCellGrid();
  static int[][] completeCellGrid() {
    int[][] grid=new int[128][3];
    int i=0;
    for(int y=64;y<72;y++)
      for(int x=0;x<4;x++)
        for(int z=0;z<4;z++)
          grid[i++]=new int[]{x,y,z};
    if(i!=128)throw new IllegalStateException("wrong bounded cell sampling grid");
    return grid;
  }
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
      if(args.length!=1)throw new IllegalArgumentException("expected exactly one mode");
      if(args[0].equals("--stock-noisechunk-cell-16"))run(false);
      else if(args[0].equals("--stock-noisechunk-complete-cell-512"))run(true);
      else if(args[0].equals("--stock-noisechunk-adjacent-cells"))run(false,true);
      else throw new IllegalArgumentException("unapproved 26.2 NoiseChunk cell probe mode");
    } catch(Throwable t){fail(t);System.exit(2);}
  }
  static void run(boolean complete) throws Exception {run(complete,false);}
  static void run(boolean complete,boolean adjacent) throws Exception {
    final int[][] samples=complete?CELL_GRID:POINTS;
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
    // Only the NEW cross-cell mode needs this exact original lifecycle method.
    // The existing 16 and 512 modes must remain byte-for-byte identical.
    Method swap=adjacent?noiseChunk.getMethod("swapSlices"):null;
    if(adjacent && (swap.getReturnType()!=void.class || swap.getParameterCount()!=0))
      throw new IllegalStateException("original 26.2 swapSlices contract changed");
    if(compute.getReturnType()!=double.class||
        initialize.getReturnType()!=void.class||advance.getReturnType()!=void.class||
        select.getReturnType()!=void.class||updateX.getReturnType()!=void.class||
        updateY.getReturnType()!=void.class||updateZ.getReturnType()!=void.class||
        stop.getReturnType()!=void.class)
      throw new IllegalStateException("wrong 26.2 density-cell evaluation signatures");
    // Stock DensityFunctions$BeardifierMarker is a package-private nested
    // enum. A public INSTANCE field on a nonpublic declaring class is NOT
    // reflectively readable without opening that exact Field, even though
    // getField("INSTANCE") succeeds. Do not change the shared stock bridge,
    // widen access globally, or substitute a synthetic Beardifier marker.
    phase="stock-BeardifierMarker-INSTANCE";
    Field beardifierInstance=markerEnum.getField("INSTANCE");
    if (!markerEnum.isEnum() ||
        !Modifier.isStatic(beardifierInstance.getModifiers()) ||
        !Modifier.isPublic(beardifierInstance.getModifiers()) ||
        beardifierInstance.getDeclaringClass()!=markerEnum ||
        beardifierInstance.getType()!=markerEnum)
      throw new IllegalStateException("original stock BeardifierMarker.INSTANCE contract changed");
    if (!beardifierInstance.canAccess(null) &&
        !beardifierInstance.trySetAccessible())
      throw new IllegalAccessException("stock BeardifierMarker.INSTANCE inaccessible");
    Object noBeard=beardifierInstance.get(null);
    if (noBeard==null || !markerInterface.isInstance(noBeard))
      throw new IllegalStateException("stock BeardifierMarker.INSTANCE is not the typed marker");
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
      if(adjacent){
        runAdjacentForSeed(si,seed,state,finalNode,ctor,wrap,compute,
            initialize,advance,select,updateY,updateX,updateZ,swap,stop,
            shape,noBeard,settings,stockPicker,noBlending);
        continue;
      }
      phase="construct-original-NoiseChunk-"+si;
      Object chunk=ctor.newInstance(16/cellW,state,0,0,shape,
           noBeard,settings,stockPicker,noBlending);
      Object wrapped=wrap.invoke(chunk,finalNode);
      if(!density.isInstance(wrapped))
        throw new IllegalStateException("stock NoiseChunk.wrap is not DensityFunction");
      OUT.println(HEAD+si+"|"+seed+"|"+cellW+"|"+cellH+"|"+yStart+"|"+worldH+"|"+
          wrapped.getClass().getName()+"|"+samples.length);
      phase="original-NoiseChunk-initialize-"+si;
      initialize.invoke(chunk);
      advance.invoke(chunk,0);
      select.invoke(chunk,(64-yStart)/cellH,0);
      for(int pi=0;pi<samples.length;pi++){
        int x=samples[pi][0],y=samples[pi][1],z=samples[pi][2];
        phase="original-NoiseChunk-interpolate-"+si+"-"+pi;
        updateY.invoke(chunk,y,(double)Math.floorMod(y-yStart,cellH)/cellH);
        updateX.invoke(chunk,x,(double)Math.floorMod(x,cellW)/cellW);
        updateZ.invoke(chunk,z,(double)Math.floorMod(z,cellW)/cellW);
        double value=(Double)compute.invoke(wrapped,chunk);
        if(!Double.isFinite(value))
          throw new IllegalStateException("nonfinite original NoiseChunk density");
        OUT.println(BIT+(si*samples.length+pi)+"|"+
          String.format(Locale.ROOT,"%016x",Double.doubleToRawLongBits(value)));
      }
      stop.invoke(chunk);
      OUT.println(END+si+"|"+samples.length);
    }
    if(reader.readLine()!=null)
      throw new IllegalStateException("unexpected extra stock world-seed input");
  }

  // EXPERIMENTAL cross-cell traversal. Full production order, marker cache
  // semantics and slice reuse remain UNREVIEWED until original 26.2 source
  // inspection; this MUST NOT grant any production/worldgen qualification.
  // Each chunk visits two X cells, two Z cells and three descending Y cells.
  // Every voxel update/compute is executed; only bounded corner positions
  // are emitted. The second X column explicitly follows a slice swap.
  // Two independent chunk origins test both positive and negative coordinates.
  static void runAdjacentForSeed(int si,String seed,Object state,Object finalNode,
      Constructor<?> ctor,Method wrap,Method compute,Method initialize,
      Method advance,Method select,Method updateY,Method updateX,Method updateZ,
      Method swap,Method stop,Object shape,Object noBeard,Object settings,
      Object stockPicker,Object noBlending) throws Exception {
    for(int chunkIndex=0;chunkIndex<2;chunkIndex++){
      int origin=chunkIndex==0?0:-16;
      int firstCell=Math.floorDiv(origin,4);
      phase="adjacent-construct-"+si+"-"+chunkIndex;
      Object chunk=ctor.newInstance(4,state,origin,origin,shape,
          noBeard,settings,stockPicker,noBlending);
      Object wrapped=wrap.invoke(chunk,finalNode);
      if(wrapped==null || !wrapped.getClass().getName().equals(
          ROOT+"DensityFunctions$Ap2"))
        throw new IllegalStateException("different stock adjacent finalDensity wrapper");
      OUT.println(ADJ_HEAD+si+"|"+seed+"|"+chunkIndex+"|"+origin+"|"+origin+
          "|4|8|-64|384|"+wrapped.getClass().getName()+"|96");
      initialize.invoke(chunk);
      int emitted=0;
      for(int cellXOffset=0;cellXOffset<2;cellXOffset++){
        phase="adjacent-advance-"+si+"-"+chunkIndex+"-"+cellXOffset;
        advance.invoke(chunk,firstCell+cellXOffset);
        for(int cellZOffset=0;cellZOffset<2;cellZOffset++){
          for(int cellY=17;cellY>=15;cellY--){
            phase="adjacent-select-"+si+"-"+chunkIndex+"-"+cellXOffset+
                "-"+cellZOffset+"-"+cellY;
            select.invoke(chunk,cellY,firstCell+cellZOffset);
            for(int localY=7;localY>=0;localY--){
              int y=cellY*8+localY;
              updateY.invoke(chunk,y,(double)localY/8.0);
              for(int localX=0;localX<4;localX++){
                int x=origin+cellXOffset*4+localX;
                updateX.invoke(chunk,x,(double)localX/4.0);
                for(int localZ=0;localZ<4;localZ++){
                  int z=origin+cellZOffset*4+localZ;
                  phase="adjacent-compute-"+si+"-"+chunkIndex+"-"+cellXOffset+
                      "-"+cellZOffset+"-"+cellY+"-"+localY+"-"+localX+"-"+localZ;
                  updateZ.invoke(chunk,z,(double)localZ/4.0);
                  double value=(Double)compute.invoke(wrapped,chunk);
                  if(!Double.isFinite(value))
                    throw new IllegalStateException("nonfinite stock adjacent density");
                  if((localY==0 || localY==7) && (localX==0 || localX==3) &&
                      (localZ==0 || localZ==3)){
                    int absoluteIndex=si*192+chunkIndex*96+emitted++;
                    OUT.println(ADJ_BIT+absoluteIndex+"|"+x+"|"+y+"|"+z+"|"+
                        String.format(Locale.ROOT,"%016x",
                            Double.doubleToRawLongBits(value)));
                  }
                }
              }
            }
          }
        }
        phase="adjacent-swapSlices-"+si+"-"+chunkIndex+"-"+cellXOffset;
        swap.invoke(chunk);
      }
      phase="adjacent-stop-"+si+"-"+chunkIndex;
      stop.invoke(chunk);
      if(emitted!=96)throw new IllegalStateException("adjacent output count drift");
      OUT.println(ADJ_END+si+"|"+chunkIndex+"|"+emitted);
    }
  }
}
