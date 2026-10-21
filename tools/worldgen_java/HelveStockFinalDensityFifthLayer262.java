// Fifth-layer genuinely new children of observed stock Java 26.2 finalDensity.
// This original-JVM diagnostic never exports Java source, bytes, holder
// registries, stack traces, or private exception messages. Old output words
// are cross-check anchors ONLY; Python emits no new old-root fixtures.
import java.io.*;
import java.lang.reflect.*;
import java.nio.charset.StandardCharsets;
import java.util.*;

public final class HelveStockFinalDensityFifthLayer262 {
  static final String LV="net.minecraft.world.level.levelgen.";
  static final String HEAD="HELVE26_2_FIFTH_SHAPE|";
  static final String VALUE="HELVE26_2_FIFTH_VALUE|";
  static final String END="HELVE26_2_FIFTH_END|";
  static final String FAIL="HELVE26_2_FIFTH_FAILURE|";
  static final PrintStream OUT=new PrintStream(
      new FileOutputStream(FileDescriptor.out),true,StandardCharsets.US_ASCII);
  static String phase="bootstrap";

  static void stage(int seed,int point,String step) {
    phase="fifth-layer-"+seed+"-"+point+"-"+step;
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
      throw new IllegalStateException("nonfinite bounded new fifth-layer value");
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
      throw new IllegalStateException("original fifth-layer rooted node class changed");
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
      if(args.length!=1 || !args[0].equals("--fifth-layer-128"))
        throw new IllegalArgumentException("one bounded fifth-layer mode only");
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
      throw new IllegalStateException("stock fifth-layer context inaccessible");

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
      Object leftAp2Left=null,leftAp2Right=null;
      Object outsideHolderTarget=null,outsideMulChild=null;
      Object mappedLeftInput=null,mappedRightInput=null;
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
              throw new IllegalStateException("fifth-layer wrapped child not DensityFunction");
          }
          stage(seedIndex,pointIndex,"assert-original-fourth-graph");
          expect(leftWrapped,"MulOrAdd");
          if(!enumName(leftWrapped,"specificType").equals("ADD") ||
             !bits((Double)member(leftWrapped,"argument")).equals("3fbe000000000000"))
            throw new IllegalStateException("frozen left ADD changed");
          deeperLeftInput=child(leftWrapped,density);
          expect(deeperLeftInput,"Ap2");
          nestedHolderTarget=HelveStockFinalDensityRootSemantics262.holderTarget(
              nestedSelector,density);
          expect(nestedHolderTarget,"YClampedGradient");
          expect(outsideWrapped,"RangeChoice");
          outsideRangeSelector=member(outsideWrapped,"input");
          expect(outsideRangeSelector,"HolderHolder");
          outsideRangeIn=member(outsideWrapped,"whenInRange");
          expect(outsideRangeIn,"MulOrAdd");
          outsideRangeOut=member(outsideWrapped,"whenOutOfRange");
          expect(outsideRangeOut,"Constant");
          if(!bits((Double)member(outsideWrapped,"minInclusive")).equals("c04e000000000000") ||
             !bits((Double)member(outsideWrapped,"maxExclusive")).equals("4074100000000000"))
            throw new IllegalStateException("outside [-60,321) moved");
          expect(outsideMulWrapped,"Ap2");
          if(!enumName(outsideMulWrapped,"type").equals("MAX"))
            throw new IllegalStateException("actual fourth-layer right MAX moved");
          rightAp2Left=member(outsideMulWrapped,"argument1");
          rightAp2Right=member(outsideMulWrapped,"argument2");
          expect(rightAp2Left,"Mapped");
          expect(rightAp2Right,"Mapped");

          stage(seedIndex,pointIndex,"left-ap2-type-and-children");
          String leftAp2Enum=enumClass(deeperLeftInput,"type");
          String leftAp2Op=enumName(deeperLeftInput,"type");
          if(!leftAp2Enum.equals(LV+"DensityFunctions$TwoArgumentSimpleFunction$Type"))
            throw new IllegalStateException("real left Ap2 type unexpected");
          leftAp2Left=member(deeperLeftInput,"argument1");
          leftAp2Right=member(deeperLeftInput,"argument2");

          stage(seedIndex,pointIndex,"gradient-real-record-fields");
          int fromY=(Integer)member(nestedHolderTarget,"fromY");
          int toY=(Integer)member(nestedHolderTarget,"toY");
          double fromValue=(Double)member(nestedHolderTarget,"fromValue");
          double toValue=(Double)member(nestedHolderTarget,"toValue");
          if(fromY>=toY || !Double.isFinite(fromValue) || !Double.isFinite(toValue))
            throw new IllegalStateException("actual fifth-layer YGradient malformed");

          stage(seedIndex,pointIndex,"outside-holder-target");
          outsideHolderTarget=HelveStockFinalDensityRootSemantics262.holderTarget(
              outsideRangeSelector,density);

          stage(seedIndex,pointIndex,"outside-in-muloradd");
          String outsideInEnum=enumClass(outsideRangeIn,"specificType");
          String outsideInOp=enumName(outsideRangeIn,"specificType");
          if(!outsideInEnum.equals(LV+"DensityFunctions$MulOrAdd$Type") ||
             !(outsideInOp.equals("MUL") || outsideInOp.equals("ADD")))
            throw new IllegalStateException("actual outside MulOrAdd enum changed");
          double outsideInArg=(Double)member(outsideRangeIn,"argument");
          if(!Double.isFinite(outsideInArg))
            throw new IllegalStateException("actual fifth-layer outside finite MulOrAdd failed");
          outsideMulChild=child(outsideRangeIn,density);

          stage(seedIndex,pointIndex,"max-mapped-child-types");
          String leftMapEnum=enumClass(rightAp2Left,"type");
          String leftMapKind=enumName(rightAp2Left,"type");
          String rightMapEnum=enumClass(rightAp2Right,"type");
          String rightMapKind=enumName(rightAp2Right,"type");
          if(!leftMapEnum.equals(LV+"DensityFunctions$Mapped$Type") ||
             !rightMapEnum.equals(LV+"DensityFunctions$Mapped$Type"))
            throw new IllegalStateException("real fifth-layer Mapped type unexpected");
          mappedLeftInput=HelveStockFinalDensityRootSemantics262.mappedInput(
              rightAp2Left,density);
          mappedRightInput=HelveStockFinalDensityRootSemantics262.mappedInput(
              rightAp2Right,density);
          for(Object node:new Object[]{leftAp2Left,leftAp2Right,outsideHolderTarget,
                                       outsideMulChild,mappedLeftInput,mappedRightInput})
            if(!density.isInstance(node))
              throw new IllegalStateException("actual fifth-layer child not density");

          stage(seedIndex,pointIndex,"emit-fifth-shape");
          OUT.println(HEAD+seedIndex+"|"+seed+"|"+
              leftAp2Enum+"|"+leftAp2Op+"|"+
              type(leftAp2Left)+"|"+type(leftAp2Right)+"|"+
              fromY+"|"+toY+"|"+bits(fromValue)+"|"+bits(toValue)+"|"+
              type(outsideHolderTarget)+"|"+
              outsideInEnum+"|"+outsideInOp+"|"+bits(outsideInArg)+"|"+
              type(outsideMulChild)+"|"+
              leftMapEnum+"|"+leftMapKind+"|"+type(mappedLeftInput)+"|"+
              rightMapEnum+"|"+rightMapKind+"|"+type(mappedRightInput));
        } else if(!seed.equals(row[0])) {
          throw new IllegalStateException("seed changed within fifth-layer 32-point group");
        }
        stage(seedIndex,pointIndex,"decode-xyz");
        int x=Integer.parseInt(row[1]),y=Integer.parseInt(row[2]),z=Integer.parseInt(row[3]);
        stage(seedIndex,pointIndex,"point-context");
        Object at=pointCtor.newInstance(x,y,z);
        stage(seedIndex,pointIndex,"left-ap2-new-children");
        double al=finite(leftAp2Left,compute,at);
        double ar=finite(leftAp2Right,compute,at);
        stage(seedIndex,pointIndex,"left-ap2-frozen-output-anchor");
        double ao=finite(deeperLeftInput,compute,at);

        stage(seedIndex,pointIndex,"outside-holder-new-target");
        double h=finite(outsideHolderTarget,compute,at);
        stage(seedIndex,pointIndex,"outside-holder-frozen-anchor");
        double ho=finite(outsideRangeSelector,compute,at);

        stage(seedIndex,pointIndex,"outside-mul-new-child");
        double im=finite(outsideMulChild,compute,at);
        stage(seedIndex,pointIndex,"outside-mul-frozen-anchor");
        double imo=finite(outsideRangeIn,compute,at);

        stage(seedIndex,pointIndex,"both-max-mapped-new-children");
        double ml=finite(mappedLeftInput,compute,at);
        double mr=finite(mappedRightInput,compute,at);
        stage(seedIndex,pointIndex,"both-max-mapped-frozen-anchors");
        double mlo=finite(rightAp2Left,compute,at);
        double mro=finite(rightAp2Right,compute,at);

        stage(seedIndex,pointIndex,"emit-six-new-inputs-five-old-anchors");
        OUT.println(VALUE+captured+"|"+
            bits(al)+"|"+bits(ar)+"|"+bits(ao)+"|"+
            bits(h)+"|"+bits(ho)+"|"+
            bits(im)+"|"+bits(imo)+"|"+
            bits(ml)+"|"+bits(mlo)+"|"+bits(mr)+"|"+bits(mro));
        captured++;
      }
      OUT.println(END+seedIndex+"|32");
    }
    if(captured!=128 || input.readLine()!=null)
      throw new IllegalStateException("fifth-layer 128 original frames exceeded");
  }
}
