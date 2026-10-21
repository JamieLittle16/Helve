// Third, genuinely unseen children of stock Java 26.2 finalDensity.
// This original-JVM diagnostic never exports Java source, bytes, holder
// registries, stack traces, or private exception messages. Old output words
// are cross-check anchors ONLY; Python emits no new old-root fixtures.
import java.io.*;
import java.lang.reflect.*;
import java.nio.charset.StandardCharsets;
import java.util.*;

public final class HelveStockFinalDensityFourthLayer262 {
  static final String LV="net.minecraft.world.level.levelgen.";
  static final String HEAD="HELVE26_2_FOURTH_SHAPE|";
  static final String VALUE="HELVE26_2_FOURTH_VALUE|";
  static final String END="HELVE26_2_FOURTH_END|";
  static final String FAIL="HELVE26_2_FOURTH_FAILURE|";
  static final PrintStream OUT=new PrintStream(
      new FileOutputStream(FileDescriptor.out),true,StandardCharsets.US_ASCII);
  static String phase="bootstrap";

  static void stage(int seed,int point,String step) {
    phase="fourth-layer-"+seed+"-"+point+"-"+step;
  }
  static String type(Object value) {
    return HelveStockFinalDensityInnerSemantics262.type(value);
  }
  static Object member(Object node,String name) throws Exception {
    return HelveStockFinalDensityRootSemantics262.member(node,name);
  }
  static Object child(Object node,Class<?> density) throws Exception {
    return HelveStockFinalDensityInnerSemantics262.soleDensityChild(node,density);
  }
  static String bits(double value) {
    if(!Double.isFinite(value))
      throw new IllegalStateException("nonfinite bounded new fourth-layer value");
    return HelveStockFinalDensityInnerSemantics262.bits(value);
  }
  static double finite(Object node,Method compute,Object ctx) throws Exception {
    return HelveStockFinalDensityInnerSemantics262.finite(node,compute,ctx);
  }
  static String enumName(Object node,String component) throws Exception {
    return HelveStockFinalDensityRootSemantics262.enumName(node,component);
  }
  static String enumClass(Object node,String component) throws Exception {
    return HelveStockFinalDensityRootSemantics262.enumClass(node,component);
  }
  static void expect(Object node,String name) {
    if(!type(node).equals(LV+"DensityFunctions$"+name))
      throw new IllegalStateException("original fourth-layer rooted node class changed");
  }
  static void failure(Throwable t) {
    Throwable reason=t;
    for(int i=0;i<16 && reason.getCause()!=null && reason.getCause()!=reason;i++)
      reason=reason.getCause();
    OUT.println(FAIL+HelveStockFinalDensityInnerSemantics262.safe(phase)+"|"+
                HelveStockFinalDensityInnerSemantics262.safe(reason.getClass().getName()));
  }
  public static void main(String[] args) {
    try {
      if(args.length!=1 || !args[0].equals("--fourth-layer-128"))
        throw new IllegalArgumentException("one bounded fourth-layer mode only");
      run();
    } catch(Throwable t) {
      failure(t);
      System.exit(2);
    }
  }
  static void run() throws Exception {
    phase="bootstrap";
    HelveWorldSeededDensity262.bootstrap();
    Class<?> vanilla=Class.forName("net.minecraft.data.registries.VanillaRegistries");
    Class<?> lookup=Class.forName("net.minecraft.core.HolderLookup$Provider");
    Class<?> getterProvider=Class.forName("net.minecraft.core.HolderGetter$Provider");
    Class<?> key=Class.forName("net.minecraft.resources.ResourceKey");
    Class<?> settings=Class.forName(LV+"NoiseGeneratorSettings");
    Class<?> stateClass=Class.forName(LV+"RandomState");
    Class<?> routerClass=Class.forName(LV+"NoiseRouter");
    Class<?> density=Class.forName(LV+"DensityFunction");
    Class<?> context=Class.forName(LV+"DensityFunction$FunctionContext");
    Class<?> point=Class.forName(LV+"DensityFunction$SinglePointContext");
    Method create=HelveWorldSeededDensity262.checkedStatic(
        stateClass,"create",stateClass,getterProvider,key,long.class);
    Method router=stateClass.getMethod("router");
    Method compute=density.getMethod("compute",context);
    Constructor<?> pointCtor=point.getDeclaredConstructor(int.class,int.class,int.class);
    if(!pointCtor.canAccess(null) && !pointCtor.trySetAccessible())
      throw new IllegalStateException("stock fourth-layer context inaccessible");

    phase="stock-lookup";
    Object provider=HelveWorldSeededDensity262.checkedStatic(
        vanilla,"createLookup",lookup).invoke(null);
    if(provider==null || !getterProvider.isInstance(provider))
      throw new IllegalStateException("original 26.2 lookup provider changed");
    Object overworld=HelveWorldSeededDensity262.field(settings,"OVERWORLD",key);
    BufferedReader input=new BufferedReader(
        new InputStreamReader(System.in,StandardCharsets.US_ASCII));
    int captured=0;
    for(int seedIndex=0;seedIndex<4;seedIndex++) {
      String seed=null;
      Object leftMarker=null,leftWrapped=null;
      Object nestedChoice=null,nestedSelector=null,nestedIn=null,nestedOut=null;
      Object outsideMarker=null,outsideWrapped=null;
      Object outsideMul=null,outsideMulWrapped=null;
      Object deeperLeftInput=null,nestedHolderTarget=null;
      Object outsideRangeSelector=null,outsideRangeIn=null,outsideRangeOut=null;
      Object rightAp2Left=null,rightAp2Right=null;
      for(int pointIndex=0;pointIndex<32;pointIndex++) {
        stage(seedIndex,pointIndex,"input-frame");
        String line=input.readLine();
        if(line==null) throw new IllegalStateException("missing original point");
        String[] row=line.split("\\t",-1);
        if(row.length!=4 || !row[0].matches("0x[0-9a-f]{16}"))
          throw new IllegalStateException("invalid fixed seed/XYZ frame");
        if(pointIndex==0) {
          seed=row[0];
          stage(seedIndex,pointIndex,"create-random-state");
          Object state=create.invoke(null,provider,overworld,
              HelveWorldSeededDensity262.bits(seed));
          stage(seedIndex,pointIndex,"root-final-density");
          Object root=HelveStockFinalDensitySinglePoint262.finalDensity(
              router.invoke(state),routerClass,density);
          stage(seedIndex,pointIndex,"root-expected-min");
          expect(root,"Ap2");
          if(!enumName(root,"type").equals("MIN"))
            throw new IllegalStateException("original root MIN changed");
          stage(seedIndex,pointIndex,"root-left-mapped");
          Object mapped=member(root,"argument1");
          expect(mapped,"Mapped");
          stage(seedIndex,pointIndex,"mapped-interpolated");
          Object interpolated=HelveStockFinalDensityRootSemantics262.mappedInput(
              mapped,density);
          expect(interpolated,"Marker");
          if(!enumName(interpolated,"type").equals("Interpolated"))
            throw new IllegalStateException("original Interpolated type changed");
          stage(seedIndex,pointIndex,"actual-first-muloradd");
          Object mul=child(interpolated,density);
          expect(mul,"MulOrAdd");
          if(!enumName(mul,"specificType").equals("MUL") ||
             bits((Double)member(mul,"argument")).equals("3fe47ae147ae147b")==false)
            throw new IllegalStateException("old source-bound MUL changed");
          stage(seedIndex,pointIndex,"first-mul-upstream-marker");
          leftMarker=child(mul,density);
          expect(leftMarker,"Marker");
          stage(seedIndex,pointIndex,"first-mul-marker-wrapped");
          leftWrapped=child(leftMarker,density);
          stage(seedIndex,pointIndex,"root-right-holder");
          Object holder=member(root,"argument2");
          expect(holder,"HolderHolder");
          stage(seedIndex,pointIndex,"outer-range-choice");
          Object choice=HelveStockFinalDensityRootSemantics262.holderTarget(
              holder,density);
          expect(choice,"RangeChoice");
          stage(seedIndex,pointIndex,"original-selector-marker");
          Object originalSelector=member(choice,"input");
          expect(originalSelector,"Marker");
          if(!enumName(originalSelector,"type").equals("Interpolated"))
            throw new IllegalStateException("stock outer selector Marker changed");
          stage(seedIndex,pointIndex,"nested-range-choice");
          nestedChoice=child(originalSelector,density);
          expect(nestedChoice,"RangeChoice");
          stage(seedIndex,pointIndex,"nested-selector");
          nestedSelector=member(nestedChoice,"input");
          stage(seedIndex,pointIndex,"nested-in");
          nestedIn=member(nestedChoice,"whenInRange");
          stage(seedIndex,pointIndex,"nested-out");
          nestedOut=member(nestedChoice,"whenOutOfRange");
          stage(seedIndex,pointIndex,"nested-bounds");
          double min=(Double)member(nestedChoice,"minInclusive");
          double max=(Double)member(nestedChoice,"maxExclusive");
          if(!Double.isFinite(min) || !Double.isFinite(max) || min>=max)
            throw new IllegalStateException("invalid original nested range");
          stage(seedIndex,pointIndex,"old-outside-ap2");
          Object outside=member(choice,"whenOutOfRange");
          expect(outside,"Ap2");
          if(!enumName(outside,"type").equals("ADD"))
            throw new IllegalStateException("original outside ADD changed");
          stage(seedIndex,pointIndex,"outside-marker");
          outsideMarker=member(outside,"argument1");
          expect(outsideMarker,"Marker");
          stage(seedIndex,pointIndex,"outside-marker-wrapped");
          outsideWrapped=child(outsideMarker,density);
          stage(seedIndex,pointIndex,"outside-muloradd");
          outsideMul=member(outside,"argument2");
          expect(outsideMul,"MulOrAdd");
          stage(seedIndex,pointIndex,"outside-muloradd-wrapped");
          outsideMulWrapped=child(outsideMul,density);
          stage(seedIndex,pointIndex,"outside-muloradd-specifictype");
          String outEnum=enumClass(outsideMul,"specificType");
          String outOp=enumName(outsideMul,"specificType");
          if(!outEnum.equals(LV+"DensityFunctions$MulOrAdd$Type") ||
             !(outOp.equals("MUL") || outOp.equals("ADD")))
            throw new IllegalStateException("original outside MulOrAdd operation changed");
          stage(seedIndex,pointIndex,"outside-muloradd-argument");
          double arg=(Double)member(outsideMul,"argument");
          if(!Double.isFinite(arg))
            throw new IllegalStateException("original outside MulOrAdd constant nonfinite");
          for(Object value:new Object[]{
              leftWrapped,nestedSelector,nestedIn,nestedOut,
              outsideWrapped,outsideMulWrapped}) {
            if(!density.isInstance(value))
              throw new IllegalStateException("fourth-layer wrapped child not DensityFunction");
          }
          stage(seedIndex,pointIndex,"observed-third-children");
          expect(leftWrapped,"MulOrAdd");
          expect(nestedSelector,"HolderHolder");
          expect(nestedIn,"Noise");
          expect(nestedOut,"Constant");
          expect(outsideWrapped,"RangeChoice");
          expect(outsideMulWrapped,"Ap2");
          stage(seedIndex,pointIndex,"left-mul-specifictype");
          String leftOp=enumName(leftWrapped,"specificType");
          String leftEnum=enumClass(leftWrapped,"specificType");
          if(!leftEnum.equals(LV+"DensityFunctions$MulOrAdd$Type") ||
             !(leftOp.equals("MUL") || leftOp.equals("ADD")))
            throw new IllegalStateException("unqualified fourth left MulOrAdd");
          double leftArg=(Double)member(leftWrapped,"argument");
          if(!Double.isFinite(leftArg))
            throw new IllegalStateException("unqualified fourth left coefficient");
          stage(seedIndex,pointIndex,"left-mul-input");
          deeperLeftInput=child(leftWrapped,density);
          stage(seedIndex,pointIndex,"nested-holder-target");
          nestedHolderTarget=HelveStockFinalDensityRootSemantics262.holderTarget(
              nestedSelector,density);
          stage(seedIndex,pointIndex,"outside-range-children");
          outsideRangeSelector=member(outsideWrapped,"input");
          outsideRangeIn=member(outsideWrapped,"whenInRange");
          outsideRangeOut=member(outsideWrapped,"whenOutOfRange");
          double outsideLow=(Double)member(outsideWrapped,"minInclusive");
          double outsideHigh=(Double)member(outsideWrapped,"maxExclusive");
          if(!Double.isFinite(outsideLow) || !Double.isFinite(outsideHigh) ||
             !(outsideLow<outsideHigh))
            throw new IllegalStateException("unqualified fourth outside range");
          stage(seedIndex,pointIndex,"right-ap2-operation");
          String rightEnum=enumClass(outsideMulWrapped,"type");
          String rightOp=enumName(outsideMulWrapped,"type");
          if(!rightEnum.equals(LV+"DensityFunctions$TwoArgumentSimpleFunction$Type"))
            throw new IllegalStateException("unqualified fourth Ap2 operation");
          stage(seedIndex,pointIndex,"right-ap2-arguments");
          rightAp2Left=member(outsideMulWrapped,"argument1");
          rightAp2Right=member(outsideMulWrapped,"argument2");
          for(Object node:new Object[]{
              deeperLeftInput,nestedHolderTarget,
              outsideRangeSelector,outsideRangeIn,outsideRangeOut,
              rightAp2Left,rightAp2Right}) {
            if(!density.isInstance(node))
              throw new IllegalStateException("unqualified fourth-layer child type");
          }
          stage(seedIndex,pointIndex,"emit-fourth-shape");
          OUT.println(HEAD+seedIndex+"|"+seed+"|"+
              leftEnum+"|"+leftOp+"|"+bits(leftArg)+"|"+
              type(deeperLeftInput)+"|"+type(nestedHolderTarget)+"|"+
              type(outsideRangeSelector)+"|"+type(outsideRangeIn)+"|"+
              type(outsideRangeOut)+"|"+bits(outsideLow)+"|"+bits(outsideHigh)+"|"+
              rightEnum+"|"+rightOp+"|"+type(rightAp2Left)+"|"+type(rightAp2Right));
        } else if(!seed.equals(row[0])) {
          throw new IllegalStateException("seed changed within fourth-layer 32-point group");
        }
        stage(seedIndex,pointIndex,"decode-xyz");
        int x=Integer.parseInt(row[1]),y=Integer.parseInt(row[2]),z=Integer.parseInt(row[3]);
        stage(seedIndex,pointIndex,"point-context");
        Object at=pointCtor.newInstance(x,y,z);
        stage(seedIndex,pointIndex,"left-mul-new-input");
        double l=finite(deeperLeftInput,compute,at);
        stage(seedIndex,pointIndex,"left-mul-prior-output-anchor");
        double lo=finite(leftWrapped,compute,at);
        stage(seedIndex,pointIndex,"nested-holder-new-target");
        double h=finite(nestedHolderTarget,compute,at);
        stage(seedIndex,pointIndex,"nested-holder-prior-output-anchor");
        double ho=finite(nestedSelector,compute,at);
        stage(seedIndex,pointIndex,"outside-range-new-selector");
        double s=finite(outsideRangeSelector,compute,at);
        stage(seedIndex,pointIndex,"outside-range-new-in");
        double i=finite(outsideRangeIn,compute,at);
        stage(seedIndex,pointIndex,"outside-range-new-out");
        double o=finite(outsideRangeOut,compute,at);
        stage(seedIndex,pointIndex,"outside-range-prior-output-anchor");
        double co=finite(outsideWrapped,compute,at);
        stage(seedIndex,pointIndex,"right-ap2-new-left");
        double a=finite(rightAp2Left,compute,at);
        stage(seedIndex,pointIndex,"right-ap2-new-right");
        double b=finite(rightAp2Right,compute,at);
        stage(seedIndex,pointIndex,"right-ap2-prior-output-anchor");
        double ao=finite(outsideMulWrapped,compute,at);
        stage(seedIndex,pointIndex,"emit-seven-new-words-four-old-anchors");
        OUT.println(VALUE+captured+"|"+bits(l)+"|"+bits(lo)+"|"+
            bits(h)+"|"+bits(ho)+"|"+
            bits(s)+"|"+bits(i)+"|"+bits(o)+"|"+bits(co)+"|"+
            bits(a)+"|"+bits(b)+"|"+bits(ao));
        captured++;
      }
      OUT.println(END+seedIndex+"|32");
    }
    if(captured!=128 || input.readLine()!=null)
      throw new IllegalStateException("fourth-layer 128 original frames exceeded");
  }
}
