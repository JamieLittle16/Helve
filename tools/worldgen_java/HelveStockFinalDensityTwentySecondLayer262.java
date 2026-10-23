// Genuine original Minecraft Java 26.2 twenty-second SOURCE-OWNED Noise leaf
// structure observation. The true twentieth nested MulOrAdd(MUL) child is
// an actual DensityFunctions$Noise, NOT another arithmetic wrapper.
// Reflect its real bound NoiseHolder, resource key and xz/y scales.
// Emit the OLD twenty-first Noise output as a strict source-free anchor to the
// sealed 128-word receipt; ZERO new numerical leaf samples/fixtures.
// No Java source, holder objects, random state, registry bytes, methods,
// noise parameters, cache law, or production authority is exported.

import java.io.*;
import java.lang.reflect.*;
import java.nio.charset.StandardCharsets;
import java.util.*;

public final class HelveStockFinalDensityTwentySecondLayer262 {
  static final String LV="net.minecraft.world.level.levelgen.";
  static final String HEAD="HELVE26_2_TWENTY_SECOND_SHAPE|";
  static final String VALUE="HELVE26_2_TWENTY_SECOND_VALUE|";
  static final String END="HELVE26_2_TWENTY_SECOND_END|";
  static final String FAIL="HELVE26_2_TWENTY_SECOND_FAILURE|";
  static final PrintStream OUT=new PrintStream(
      new FileOutputStream(FileDescriptor.out),true,StandardCharsets.US_ASCII);
  static String phase="bootstrap";

  static void stage(int seed,int point,String step) {
    phase="twenty-first-layer-"+seed+"-"+point+"-"+step;
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
      throw new IllegalStateException("nonfinite original eighteenth Clamp probe value");
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
      throw new IllegalStateException("original thirteenth-layer rooted node class changed");
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
      if(args.length!=1 || !args[0].equals("--twenty-second-layer-128"))
        throw new IllegalArgumentException("one bounded thirteenth-layer mode only");
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
      throw new IllegalStateException("stock thirteenth-layer context inaccessible");

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
      Object leftMulChild=null,outsideInnerMulChild=null;
      Object leftMarkerWrapped=null,rightMarkerWrapped=null;
      Object leftDeepGrandchild=null;
      Object choiceLeftInput=null,choiceLeftIn=null,choiceLeftOut=null;
      Object choiceRightInput=null,choiceRightIn=null,choiceRightOut=null;
      Object eighthAp2Left=null,eighthAp2Right=null;
      Object eighthLeftTarget=null,eighthRightTarget=null;
      Object ninthRightChild=null;
      Object tenthSelector=null,tenthWhenIn=null,tenthWhenOut=null;
      Object eleventhMarkerInput=null,eleventhInLeft=null,eleventhInRight=null,eleventhOutLeft=null,eleventhOutRight=null;
       Object twelfthOutLeftAp2First=null,twelfthOutLeftAp2Second=null;
       Object thirteenthLeftChild1=null,thirteenthLeftChild2=null;
       Object fourteenthHolderTarget=null;
       Object fifteenthMarkerWrapped=null;
       Object sixteenthAp2Left=null,sixteenthAp2Right=null;
       Object seventeenthRightLeft=null,seventeenthRightRight=null;
       Object eighteenthClampInput=null;
       Object nineteenthLeft=null,nineteenthRight=null;
       Object twentiethInner=null;
       Object twentyFirstInner=null;
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
              throw new IllegalStateException("thirteenth-layer wrapped child not DensityFunction");
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

          stage(seedIndex,pointIndex,"sixth-real-left-ap2");
          if(!enumName(deeperLeftInput,"type").equals("MUL"))
            throw new IllegalStateException("sixth real left Ap2 changed");
          leftAp2Left=member(deeperLeftInput,"argument1");
          leftAp2Right=member(deeperLeftInput,"argument2");
          expect(leftAp2Left,"YClampedGradient");
          expect(leftAp2Right,"MulOrAdd");
          if(!enumName(leftAp2Right,"specificType").equals("ADD") ||
             !bits((Double)member(leftAp2Right,"argument")).equals("bfbe000000000000"))
            throw new IllegalStateException("sixth real left inner ADD moved");
          leftMulChild=child(leftAp2Right,density);
          expect(leftMulChild,"MulOrAdd");

          stage(seedIndex,pointIndex,"sixth-real-outside-noise");
          outsideMulChild=child(outsideRangeIn,density);
          expect(outsideMulChild,"MulOrAdd");
          if(!enumName(outsideMulChild,"specificType").equals("MUL") ||
             !bits((Double)member(outsideMulChild,"argument")).equals("bf9999999999999a"))
            throw new IllegalStateException("sixth outside inner MUL moved");
          outsideInnerMulChild=child(outsideMulChild,density);
          expect(outsideInnerMulChild,"Noise");

          stage(seedIndex,pointIndex,"sixth-two-interpolated-markers");
          mappedLeftInput=HelveStockFinalDensityRootSemantics262.mappedInput(
              rightAp2Left,density);
          mappedRightInput=HelveStockFinalDensityRootSemantics262.mappedInput(
              rightAp2Right,density);
          expect(mappedLeftInput,"Marker");
          expect(mappedRightInput,"Marker");
          if(!enumName(mappedLeftInput,"type").equals("Interpolated") ||
             !enumName(mappedRightInput,"type").equals("Interpolated"))
            throw new IllegalStateException("sixth Interpolated markers moved");
          leftMarkerWrapped=child(mappedLeftInput,density);
          rightMarkerWrapped=child(mappedRightInput,density);
          expect(leftMarkerWrapped,"RangeChoice");
          expect(rightMarkerWrapped,"RangeChoice");

          stage(seedIndex,pointIndex,"left-deep-muloradd-record");
          String deepEnum=enumClass(leftMulChild,"specificType");
          String deepOp=enumName(leftMulChild,"specificType");
          double deepArg=(Double)member(leftMulChild,"argument");
          leftDeepGrandchild=child(leftMulChild,density);
          if(!deepEnum.equals(LV+"DensityFunctions$MulOrAdd$Type") ||
             !(deepOp.equals("ADD") || deepOp.equals("MUL")) ||
             !Double.isFinite(deepArg))
            throw new IllegalStateException("unqualified eighth real MulOrAdd");

          stage(seedIndex,pointIndex,"first-real-interpolated-range-choice");
          double firstMin=(Double)member(leftMarkerWrapped,"minInclusive");
          double firstMax=(Double)member(leftMarkerWrapped,"maxExclusive");
          choiceLeftInput=member(leftMarkerWrapped,"input");
          choiceLeftIn=member(leftMarkerWrapped,"whenInRange");
          choiceLeftOut=member(leftMarkerWrapped,"whenOutOfRange");

          stage(seedIndex,pointIndex,"second-real-interpolated-range-choice");
          double secondMin=(Double)member(rightMarkerWrapped,"minInclusive");
          double secondMax=(Double)member(rightMarkerWrapped,"maxExclusive");
          choiceRightInput=member(rightMarkerWrapped,"input");
          choiceRightIn=member(rightMarkerWrapped,"whenInRange");
          choiceRightOut=member(rightMarkerWrapped,"whenOutOfRange");
          if(!Double.isFinite(firstMin) || !Double.isFinite(firstMax) ||
             !Double.isFinite(secondMin) || !Double.isFinite(secondMax) ||
             firstMin>=firstMax || secondMin>=secondMax)
            throw new IllegalStateException("unqualified eighth actual RangeChoice bounds");
          for(Object node:new Object[]{leftDeepGrandchild,
                                       choiceLeftInput,choiceLeftIn,choiceLeftOut,
                                       choiceRightInput,choiceRightIn,choiceRightOut})
            if(!density.isInstance(node))
              throw new IllegalStateException("eighth original child not density");

          stage(seedIndex,pointIndex,"actual-left-deeper-ap2");
          expect(leftDeepGrandchild,"Ap2");
          String ap2Enum=enumClass(leftDeepGrandchild,"type");
          String ap2Op=enumName(leftDeepGrandchild,"type");
          eighthAp2Left=member(leftDeepGrandchild,"argument1");
          eighthAp2Right=member(leftDeepGrandchild,"argument2");
          if(!ap2Enum.equals(LV+"DensityFunctions$TwoArgumentSimpleFunction$Type") ||
             !(ap2Op.equals("ADD") || ap2Op.equals("MUL") ||
               ap2Op.equals("MIN") || ap2Op.equals("MAX")) ||
             !density.isInstance(eighthAp2Left) ||
             !density.isInstance(eighthAp2Right))
            throw new IllegalStateException("actual eighth Ap2 source class changed");

          stage(seedIndex,pointIndex,"actual-first-selector-holder-target");
          expect(choiceLeftInput,"HolderHolder");
          eighthLeftTarget=HelveStockFinalDensityRootSemantics262.holderTarget(
              choiceLeftInput,density);
          expect(eighthLeftTarget,"YClampedGradient");
          int lFrom=(Integer)member(eighthLeftTarget,"fromY");
          int lTo=(Integer)member(eighthLeftTarget,"toY");
          double lVFrom=(Double)member(eighthLeftTarget,"fromValue");
          double lVTo=(Double)member(eighthLeftTarget,"toValue");

          stage(seedIndex,pointIndex,"actual-second-selector-holder-target");
          expect(choiceRightInput,"HolderHolder");
          eighthRightTarget=HelveStockFinalDensityRootSemantics262.holderTarget(
              choiceRightInput,density);
          expect(eighthRightTarget,"YClampedGradient");
          int rFrom=(Integer)member(eighthRightTarget,"fromY");
          int rTo=(Integer)member(eighthRightTarget,"toY");
          double rVFrom=(Double)member(eighthRightTarget,"fromValue");
          double rVTo=(Double)member(eighthRightTarget,"toValue");
          if(lFrom>=lTo || rFrom>=rTo)
            throw new IllegalStateException("invalid original eighth gradient endpoints");

          stage(seedIndex,pointIndex,"real-deep-left-gradient-record");
          expect(eighthAp2Left,"YClampedGradient");
          int deepFrom=(Integer)member(eighthAp2Left,"fromY");
          int deepTo=(Integer)member(eighthAp2Left,"toY");
          double deepVFrom=(Double)member(eighthAp2Left,"fromValue");
          double deepVTo=(Double)member(eighthAp2Left,"toValue");
          if(deepFrom>=deepTo)
            throw new IllegalStateException("invalid actual deep gradient bounds");

          stage(seedIndex,pointIndex,"real-deep-right-muloradd-record");
          expect(eighthAp2Right,"MulOrAdd");
          String rightChildEnum=enumClass(eighthAp2Right,"specificType");
          String rightChildOp=enumName(eighthAp2Right,"specificType");
          double rightChildArg=(Double)member(eighthAp2Right,"argument");
          ninthRightChild=child(eighthAp2Right,density);
          if(!rightChildEnum.equals(LV+"DensityFunctions$MulOrAdd$Type") ||
             !(rightChildOp.equals("ADD") || rightChildOp.equals("MUL")) ||
             !Double.isFinite(rightChildArg) ||
             !density.isInstance(ninthRightChild))
            throw new IllegalStateException("real deep MulOrAdd source operator changed");

          stage(seedIndex,pointIndex,"actual-tenth-deep-right-rangechoice");
          expect(ninthRightChild,"RangeChoice");
          tenthSelector=member(ninthRightChild,"input");
          tenthWhenIn=member(ninthRightChild,"whenInRange");
          tenthWhenOut=member(ninthRightChild,"whenOutOfRange");
          double tenthMin=(Double)member(ninthRightChild,"minInclusive");
          double tenthMax=(Double)member(ninthRightChild,"maxExclusive");
          if(!Double.isFinite(tenthMin) || !Double.isFinite(tenthMax) ||
             tenthMin>=tenthMax ||
             !density.isInstance(tenthSelector) ||
             !density.isInstance(tenthWhenIn) ||
             !density.isInstance(tenthWhenOut))
            throw new IllegalStateException("original tenth RangeChoice class/record changed");
          stage(seedIndex,pointIndex,"actual-eleventh-marker-record");
          expect(tenthSelector,"Marker");
          String markerEnum=enumClass(tenthSelector,"type");
          String markerType=enumName(tenthSelector,"type");
          eleventhMarkerInput=child(tenthSelector,density);

          stage(seedIndex,pointIndex,"actual-eleventh-in-ap2-record");
          expect(tenthWhenIn,"Ap2");
          String inEnum=enumClass(tenthWhenIn,"type");
          String inOp=enumName(tenthWhenIn,"type");
          eleventhInLeft=member(tenthWhenIn,"argument1");
          eleventhInRight=member(tenthWhenIn,"argument2");

          stage(seedIndex,pointIndex,"actual-eleventh-out-ap2-record");
          expect(tenthWhenOut,"Ap2");
          String eleventhOutEnum=enumClass(tenthWhenOut,"type");
          String eleventhOutOp=enumName(tenthWhenOut,"type");
          eleventhOutLeft=member(tenthWhenOut,"argument1");
          eleventhOutRight=member(tenthWhenOut,"argument2");

          if(!density.isInstance(eleventhMarkerInput) ||
             !density.isInstance(eleventhInLeft) ||
             !density.isInstance(eleventhInRight) ||
             !density.isInstance(eleventhOutLeft) ||
             !density.isInstance(eleventhOutRight))
            throw new IllegalStateException("original eleventh density child type mismatch");
          // Only the eleventh out-of-range MAX left Ap2 edge. In the
          // independently frozen 128 samples it supplies all 60 *selected*
          // outer out-of-range results. Never infer Java object identity or
          // child operator class from numerical equality at these points.
          stage(seedIndex,pointIndex,"actual-twelfth-out-left-ap2");
          expect(eleventhOutLeft,"Ap2");
          String twelfthAp2Enum=enumClass(eleventhOutLeft,"type");
          String twelfthAp2Op=enumName(eleventhOutLeft,"type");
          twelfthOutLeftAp2First=member(eleventhOutLeft,"argument1");
          twelfthOutLeftAp2Second=member(eleventhOutLeft,"argument2");
          if(!twelfthAp2Enum.equals(LV+"DensityFunctions$TwoArgumentSimpleFunction$Type") ||
             !(twelfthAp2Op.equals("ADD") || twelfthAp2Op.equals("MUL") ||
               twelfthAp2Op.equals("MIN") || twelfthAp2Op.equals("MAX")) ||
             !density.isInstance(twelfthOutLeftAp2First) ||
             !density.isInstance(twelfthOutLeftAp2Second))
            throw new IllegalStateException("actual twelfth Ap2 record changed");
          // Descend ONLY the actual LEFT Ap2 child of the genuine twelfth
          // Ap2(MIN). Of 128 pinned samples, this value participates in
          // 55 final MIN-root selected paths after both outer choices.
          // Never infer Java op/child classes from numeric coincidences.
          stage(seedIndex,pointIndex,"actual-thirteenth-twelfth-left-ap2");
          expect(twelfthOutLeftAp2First,"Ap2");
          String thirteenthAp2Enum=enumClass(twelfthOutLeftAp2First,"type");
          String thirteenthAp2Op=enumName(twelfthOutLeftAp2First,"type");
          thirteenthLeftChild1=member(twelfthOutLeftAp2First,"argument1");
          thirteenthLeftChild2=member(twelfthOutLeftAp2First,"argument2");
          if(!thirteenthAp2Enum.equals(LV+"DensityFunctions$TwoArgumentSimpleFunction$Type") ||
             !(thirteenthAp2Op.equals("ADD") || thirteenthAp2Op.equals("MUL") ||
               thirteenthAp2Op.equals("MIN") || thirteenthAp2Op.equals("MAX")) ||
             !density.isInstance(thirteenthLeftChild1) ||
             !density.isInstance(thirteenthLeftChild2))
            throw new IllegalStateException("actual thirteenth left Ap2 record changed");
          if(!twelfthAp2Op.equals("MIN") ||
             !thirteenthAp2Op.equals("MIN") ||
             !type(thirteenthLeftChild1).equals(LV+"DensityFunctions$Ap2") ||
             !type(thirteenthLeftChild2).equals(LV+"DensityFunctions$HolderHolder"))
            throw new IllegalStateException("actual frozen twelfth/thirteenth MIN ancestry drift");
          stage(seedIndex,pointIndex,"actual-fourteenth-right-holder-target");
          expect(thirteenthLeftChild2,"HolderHolder");
          Object directHolder=member(thirteenthLeftChild2,"function");
          if(!type(directHolder).equals("net.minecraft.core.Holder$Direct"))
            throw new IllegalStateException("genuine fourteenth Holder target container moved");
          fourteenthHolderTarget=
              HelveStockFinalDensityRootSemantics262.holderTarget(thirteenthLeftChild2,density);
          if(!density.isInstance(fourteenthHolderTarget))
            throw new IllegalStateException("genuine fourteenth delegate not a DensityFunction");
          stage(seedIndex,pointIndex,"actual-fifteenth-marker-record");
          expect(fourteenthHolderTarget,"Marker");
          String fifteenthMarkerEnum=enumClass(fourteenthHolderTarget,"type");
          String fifteenthMarkerType=enumName(fourteenthHolderTarget,"type");
          fifteenthMarkerWrapped=child(fourteenthHolderTarget,density);
          if(!fifteenthMarkerEnum.equals(LV+"DensityFunctions$Marker$Type") ||
             !density.isInstance(fifteenthMarkerWrapped))
            throw new IllegalStateException("real fifteenth Marker enum/wrapped child changed");
          if(!fifteenthMarkerType.equals("CacheOnce") ||
             !type(fifteenthMarkerWrapped).equals(LV+"DensityFunctions$Ap2"))
            throw new IllegalStateException("pinned fifteenth CacheOnce -> Ap2 ancestry drift");
          stage(seedIndex,pointIndex,"actual-sixteenth-cacheonce-wrapped-ap2");
          expect(fifteenthMarkerWrapped,"Ap2");
          String sixteenthEnum=enumClass(fifteenthMarkerWrapped,"type");
          String sixteenthOp=enumName(fifteenthMarkerWrapped,"type");
          sixteenthAp2Left=member(fifteenthMarkerWrapped,"argument1");
          sixteenthAp2Right=member(fifteenthMarkerWrapped,"argument2");
          if(!sixteenthEnum.equals(LV+"DensityFunctions$TwoArgumentSimpleFunction$Type") ||
             !(sixteenthOp.equals("ADD") || sixteenthOp.equals("MUL") ||
               sixteenthOp.equals("MIN") || sixteenthOp.equals("MAX")) ||
             !density.isInstance(sixteenthAp2Left) ||
             !density.isInstance(sixteenthAp2Right))
            throw new IllegalStateException("actual sixteenth Ap2 operation/child types moved");
          if(!sixteenthOp.equals("MIN") ||
             !type(sixteenthAp2Left).equals(LV+"DensityFunctions$Ap2") ||
             !type(sixteenthAp2Right).equals(LV+"DensityFunctions$Ap2"))
            throw new IllegalStateException("independent original sixteenth MIN Ap2/Ap2 ancestry drift");
          stage(seedIndex,pointIndex,"actual-seventeenth-sixteenth-min-right-ap2");
          expect(sixteenthAp2Right,"Ap2");
          String seventeenthEnum=enumClass(sixteenthAp2Right,"type");
          String seventeenthOp=enumName(sixteenthAp2Right,"type");
          seventeenthRightLeft=member(sixteenthAp2Right,"argument1");
          seventeenthRightRight=member(sixteenthAp2Right,"argument2");
          if(!seventeenthEnum.equals(LV+"DensityFunctions$TwoArgumentSimpleFunction$Type") ||
             !(seventeenthOp.equals("ADD") || seventeenthOp.equals("MUL") ||
               seventeenthOp.equals("MIN") || seventeenthOp.equals("MAX")) ||
             !density.isInstance(seventeenthRightLeft) ||
             !density.isInstance(seventeenthRightRight))
            throw new IllegalStateException("genuine seventeenth right Ap2 record drift");
          if(!seventeenthOp.equals("ADD") ||
             !type(seventeenthRightLeft).equals(LV+"DensityFunctions$HolderHolder") ||
             !type(seventeenthRightRight).equals(LV+"DensityFunctions$Clamp"))
            throw new IllegalStateException("original seventeenth ADD Holder/Clamp source ancestry drift");
          stage(seedIndex,pointIndex,"eighteenth-original-clamp-source-structure");
          expect(seventeenthRightRight,"Clamp");
          eighteenthClampInput=child(seventeenthRightRight,density);
          Object boundMin=member(seventeenthRightRight,"minValue");
          Object boundMax=member(seventeenthRightRight,"maxValue");
          if(!(boundMin instanceof Double) || !(boundMax instanceof Double))
            throw new IllegalStateException("original Clamp bound type changed");
          double clampMin=((Double)boundMin).doubleValue();
          double clampMax=((Double)boundMax).doubleValue();
          if(!Double.isFinite(clampMin) || !Double.isFinite(clampMax) ||
             !(clampMin < clampMax) || !density.isInstance(eighteenthClampInput))
            throw new IllegalStateException("real original Clamp bounds/child malformed");
          if(!type(eighteenthClampInput).equals(LV+"DensityFunctions$Ap2") ||
             bits(clampMin).equals("bff0000000000000")==false ||
             bits(clampMax).equals("3ff0000000000000")==false)
            throw new IllegalStateException("actual eighteenth Clamp[-1,+1] Ap2 source ancestry moved");
          stage(seedIndex,pointIndex,"genuine-nineteenth-clamp-wrapped-ap2");
          expect(eighteenthClampInput,"Ap2");
          String nineteenthEnum=enumClass(eighteenthClampInput,"type");
          String nineteenthOp=enumName(eighteenthClampInput,"type");
          nineteenthLeft=member(eighteenthClampInput,"argument1");
          nineteenthRight=member(eighteenthClampInput,"argument2");
          if(!nineteenthEnum.equals(LV+"DensityFunctions$TwoArgumentSimpleFunction$Type") ||
             !(nineteenthOp.equals("ADD") || nineteenthOp.equals("MUL") ||
               nineteenthOp.equals("MIN") || nineteenthOp.equals("MAX")) ||
             !density.isInstance(nineteenthLeft) ||
             !density.isInstance(nineteenthRight))
            throw new IllegalStateException("actual nineteenth wrapped Ap2 op/child identities changed");
          if(!nineteenthOp.equals("ADD") ||
             !type(nineteenthLeft).equals(LV+"DensityFunctions$Ap2") ||
             !type(nineteenthRight).equals(LV+"DensityFunctions$MulOrAdd"))
            throw new IllegalStateException("original nineteenth ADD(Ap2,MulOrAdd) ancestry drift");
          stage(seedIndex,pointIndex,"genuine-twentieth-nineteenth-right-muloradd");
          expect(nineteenthRight,"MulOrAdd");
          String twentiethEnum=enumClass(nineteenthRight,"specificType");
          String twentiethOp=enumName(nineteenthRight,"specificType");
          Object argument=member(nineteenthRight,"argument");
          if(!(argument instanceof Double))
            throw new IllegalStateException("real twentieth MulOrAdd argument type drift");
          double twentiethArgument=((Double)argument).doubleValue();
          twentiethInner=child(nineteenthRight,density);
          if(!twentiethEnum.equals(LV+"DensityFunctions$MulOrAdd$Type") ||
             !(twentiethOp.equals("ADD") || twentiethOp.equals("MUL")) ||
             !Double.isFinite(twentiethArgument) ||
             !density.isInstance(twentiethInner))
            throw new IllegalStateException("original twentieth MulOrAdd source enum/child drift");
          if(!twentiethOp.equals("ADD") ||
             !bits(twentiethArgument).equals("bfb395810624dd2f") ||
             !type(twentiethInner).equals(LV+"DensityFunctions$MulOrAdd"))
            throw new IllegalStateException("twentieth original nested ADD scalar/child drift");
          stage(seedIndex,pointIndex,"source-observe-actual-twenty-first-nested-muloradd");
          expect(twentiethInner,"MulOrAdd");
          String twentyFirstEnum=enumClass(twentiethInner,"specificType");
          String twentyFirstOp=enumName(twentiethInner,"specificType");
          Object twentyFirstArgumentObject=member(twentiethInner,"argument");
          if(!(twentyFirstArgumentObject instanceof Double))
            throw new IllegalStateException("twenty-first genuine MulOrAdd argument class drift");
          double twentyFirstArgument=((Double)twentyFirstArgumentObject).doubleValue();
          twentyFirstInner=child(twentiethInner,density);
          if(!twentyFirstEnum.equals(LV+"DensityFunctions$MulOrAdd$Type") ||
             !(twentyFirstOp.equals("ADD") || twentyFirstOp.equals("MUL")) ||
             !Double.isFinite(twentyFirstArgument) ||
             !density.isInstance(twentyFirstInner))
            throw new IllegalStateException("original twenty-first MulOrAdd enum/scalar/child drift");
          if(!twentyFirstOp.equals("MUL") ||
             !bits(twentyFirstArgument).equals("bf878d4fdf3b6458") ||
             !type(twentyFirstInner).equals(LV+"DensityFunctions$Noise"))
            throw new IllegalStateException("original 21st MUL -> Noise source ancestry drift");
          stage(seedIndex,pointIndex,"original-22nd-real-noise-node");
          expect(twentyFirstInner,"Noise");
          Object xzObj=member(twentyFirstInner,"xzScale");
          Object yObj=member(twentyFirstInner,"yScale");
          if(!(xzObj instanceof Double) || !(yObj instanceof Double))
            throw new IllegalStateException("genuine Noise scale component type drift");
          double xzScale=((Double)xzObj).doubleValue();
          double yScale=((Double)yObj).doubleValue();
          if(!Double.isFinite(xzScale) || !Double.isFinite(yScale))
            throw new IllegalStateException("original Noise scale nonfinite");
          Object heldNoise=member(twentyFirstInner,"noise");
          if(!type(heldNoise).equals(LV+"DensityFunction$NoiseHolder"))
            throw new IllegalStateException("genuine Noise holder node source class drift");
          Object noiseData=member(heldNoise,"noiseData");
          Object normalNoise=member(heldNoise,"noise");
          Class<?> holderType=Class.forName("net.minecraft.core.Holder");
          if(!holderType.isInstance(noiseData) || normalNoise==null ||
             !type(normalNoise).equals(LV+"synth.NormalNoise"))
            throw new IllegalStateException("genuine NoiseHolder stock binding unqualified");
          stage(seedIndex,pointIndex,"original-22nd-holder-resource-key");
          Method unwrap=holderType.getMethod("unwrapKey");
          Object optional=unwrap.invoke(noiseData);
          if(!(optional instanceof Optional<?>))
            throw new IllegalStateException("real holder unwrapKey Optional class drift");
          String keyName="unkeyed";
          if(((Optional<?>)optional).isPresent()) {
            Object keyObject=((Optional<?>)optional).get();
            Class<?> resourceKey=Class.forName("net.minecraft.resources.ResourceKey");
            if(!resourceKey.isInstance(keyObject))
              throw new IllegalStateException("original resource key owner drift");
            Object location=resourceKey.getMethod("location").invoke(keyObject);
            keyName=String.valueOf(location);
          }
          if(!keyName.matches("(minecraft:[a-z0-9_.\\/\\-]+|unkeyed)"))
            throw new IllegalStateException("original Noise key identity is not bounded");
          stage(seedIndex,pointIndex,"emit-original-22nd-leaf-structure");
          OUT.println(HEAD+seedIndex+"|"+seed+"|"+
              type(twentyFirstInner)+"|"+bits(xzScale)+"|"+bits(yScale)+"|"+
              type(heldNoise)+"|"+type(noiseData)+"|"+keyName+"|"+
              type(normalNoise));
        } else if(!seed.equals(row[0])) {
          throw new IllegalStateException("seed changed within seventeenth-layer 32-point group");
        }
        stage(seedIndex,pointIndex,"decode-xyz");
        int x=Integer.parseInt(row[1]),y=Integer.parseInt(row[2]),z=Integer.parseInt(row[3]);
        stage(seedIndex,pointIndex,"point-context");
        Object at=pointCtor.newInstance(x,y,z);
        stage(seedIndex,pointIndex,"only-OLD-sealed-twenty-first-original-noise-value");
        double oldNoise=finite(twentyFirstInner,compute,at);
        stage(seedIndex,pointIndex,"emit-one-independent-old-anchor-no-new-values");
        OUT.println(VALUE+captured+"|"+bits(oldNoise));
        captured++;
      }
      OUT.println(END+seedIndex+"|32");
    }
    if(captured!=128 || input.readLine()!=null)
      throw new IllegalStateException("seventeenth-layer 128 original frames exceeded");
  }
}
