# Stock 26.2 finalDensity: successful second-layer JVM receipt and bounded Rust implementation

**21 October 2026** · Minecraft Java **26.2** · Protocol **776** · DataVersion **4903**

**Source-owning original JVM:** user-provided, source-free successful second-layer receipt after CI-green merged PR #484.

- **Merged main before this work:** `ce4347f8bc63a21d5b96c2101363183775a0a970`.
- **Original private source-free JSON:** 66,003 bytes, SHA-256 `e12d01ccc9defc0c7d8a8a162bc7c7c890af7df6eb12e13656c59277f5eae9d9`; **not committed**.
- **New immutable compact public fixture:** `crates/world/helve-world-gen/tests/data/stock_finaldensity_second_layer_new_128_rawbits.tsv`; 8,704 bytes, SHA-256 `e684407be3e3d8ef5435c7518a0d4f5adbccae134684a730b216a11212874f4a`.
- **Source archive/JAR/Atlas:** still pinned by the original strict reporter. The report's prior immutable 128-inner SHA is `967c9203950f0e22a8b69f73dfe5e1bd1438ef1224fcc4346b8d578409c45170`.
- **Only four genuinely new words per fixed XYZ point:** `mul_input_bits`, `selector_input_bits`, `outer_left_bits`, `outer_right_bits`. The earlier `mul_output_bits`, `selector_output_bits`, `outer_output_bits` are revalidated against the old inner source-free fixture, **not recaptured as a replacement**.

## Actual graph, not an imagined 26.2 formula

All four Overworld seeds have the **same** original runtime class/operation/argument identities:

```text
RandomState.router.finalDensity() : Ap2 MIN
├── Mapped SQUEEZE
│   └── Marker Interpolated
│       └── MulOrAdd specificType=MUL argument=0x3fe47ae147ae147b (0.64)
│           └── DensityFunctions$Marker                   ← unknown inner graph
└── HolderHolder -> Holder$Direct -> RangeChoice
    ├── input: Marker Interpolated
    │   └── DensityFunctions$RangeChoice                  ← unknown nested choice
    ├── minInclusive: -1000000.0
    ├── maxExclusive: +0.0
    ├── whenInRange: Constant(64.0)
    └── whenOutOfRange: Ap2 ADD
        ├── DensityFunctions$Marker                       ← unknown inner graph
        └── DensityFunctions$MulOrAdd                     ← unknown inner graph
```

The original recorded enum declaring types are `DensityFunctions$MulOrAdd$Type`, `DensityFunctions$Marker$Type`, and `DensityFunctions$TwoArgumentSimpleFunction$Type`. The three Markers cannot be assumed interchangeable; no `NoiseChunk` timeline is established.

## Numerical evidence and limits

For the **128 fixed original JVM SinglePointContexts** only:

- `MulOrAdd MUL` computes all 128 outputs exactly as the actual upstream input multiplied by the literal binary64 `0x3fe47ae147ae147b`. The existing fused Rust operator can now be instantiated with the **actual** parameter rather than an arbitrary stock mixed-delegate parameter.
- `Ap2 ADD` computes all 128 out-of-range branch outputs exactly as the newly observed left plus right inputs, bit-for-bit. This is a numeric law on finite samples, not yet an all-input source-law proof.
- `Marker(type=Interpolated)` delegates to the wrapped selector's nested RangeChoice exactly on these 128 SinglePointContexts.
- Previously established immutable witnesses remain valid: SQUEEZE 128/128, RangeChoice 47 in / 81 out, MIN root 124 left / 4 right. No need to re-run 128-root, 128-inner, 512-cell, 768-NoiseChunk or 1,152 stock mixed delegates.

**Rust implementation:** `StockDensityNode262::ExplicitAp2Add` is a caller-explicit, typed finite ADD candidate in the same validated, immutable, at-most-32-node bounded DAG. It uses existing caller-owned scratch, cold backwards-edge and reachability checks, and eager IEEE evaluation when demanded. The 128-row Rust test `stock_finaldensity_second_layer_262.rs` composes MulOrAdd, SQUEEZE, out-Ap2 ADD, RangeChoice and MIN in **one** ten-node graph, testing the new operations independently to avoid inactive branch masking. The four remaining actual child inputs are supplied as **JVM-origin leaf values**, not secretly derived from Rust world-seeded noise or invented constants.

**Validator:** `tools/worldgen_26_2_stock_finaldensity_second_layer_fixture.py` pins exact fixture bytes and the private user JSON's length/SHA, checks old raw-bit anchors and identity/shape gates through the existing `second.validate`, and provides optional private receipt validation:

```bash
python3 tools/worldgen_26_2_stock_finaldensity_second_layer_fixture.py \
  --capture /tmp/helve-26_2-final-second-layer-post484.json
```

No original Java source, source method body, registry snapshot or binary is committed.

## Next new frontier: true children, not new root captures

A further **source-owning** bounded traversal must descend only into these **four observed children**:

1. `MulOrAdd(MUL 0.64).input = Marker`: determine that Marker type, its exact wrapped child class and 128 genuine wrapped values.
2. The existing selector `Marker Interpolated` wraps another `RangeChoice`: identify its actual input, threshold words, two branch classes, and new wrapped values; do not shortcut a nested selector to a single noise.
3. The outside `Ap2 ADD.argument1 = Marker`: determine Marker kind/wrapped class and 128 real wrapped values.
4. The outside `Ap2 ADD.argument2 = MulOrAdd`: determine its real `specificType`, argument bits, wrapped density class and 128 real upstream bits.

Write a narrow source-free original JVM observer that reuses the same **fixed seed/XYZ list as query coordinates** while outputting only **previously unseen upstream values and class/operation declarations**. New upper-node values may appear only as equality checks to the existing old/new fixtures. Keep the original class/record/enum guards; fail closed with exact fixed phase tags on mismatches; no fake source law or Java-body emission. Follow children recursively until the registered noise/splines are truly source-bound to existing seeded Rust primitives. After entire SinglePointContext graph succeeds, implement separate genuine `NoiseChunk` lifecycle / interpolation and use the existing 768 adjacent and 512-cell immutable oracles.

**All quality and product gates remain false:** mapped SQUEEZE and RangeChoice source-law reviewed, marker NoiseChunk lifecycle reviewed, full router graph qualified, router numeric parity qualified, independent VAR/SEM admitted, production worldgen enabled. A fixed **single** semantic world owner and no per-block allocation, graph-rewriting or extra registry lookup remain required.


## Next original-JVM diagnostic implemented: four real third-layer children

After CI-green merged PR #485 (`main=a78e6c480732f5d90b36c6953e312aec0d856b4a`), the source-free, *not yet source-owner-executed* next frontier is implemented in:

- `tools/worldgen_26_2_stock_final_density_third_layer.py`
- `tools/worldgen_java/HelveStockFinalDensityThirdLayer262.java`
- `tools/tests/test_worldgen_26_2_stock_final_density_third_layer.py`

The real rooted traversal follows **only** the four new classes established in the second-layer original-JVM receipt. It probes the left MulOrAdd's wrapped Marker, the selector Marker's nested RangeChoice selector/branches/thresholds, the outside ADD left Marker's child, and the outside ADD right MulOrAdd's actual `specificType`/argument/child. Its fixed 4 × 32 samples introduce **six new original upstream IEEE words per coordinate**; four previous second-layer values are *comparison-only bit anchors* against the immutable 8,704-byte fixture. All source archive/server/Atlas/method pins, Java enum declaring classes, arity, finite values, branch selection and configured constant arithmetic fail closed, with narrow `third-layer-<seed>-<point>-<step>` failure tags. No source text, exception message, registry state, or full original JSON is committed.

**Run after all required CI is green and this branch merges**, on the private source-owning machine. This does not repeat a root, inner, second-layer or NoiseChunk capture:

```bash
cd ~/Crucible
git switch main
git pull --ff-only
python3 tools/worldgen_26_2_stock_final_density_third_layer.py \
  --source "$HOME/Documents/mc-source/mc-src.zip" \
  --db .crucible/vanilla/atlas.sqlite \
  --lock vanilla/vanilla.lock.toml \
  --output /tmp/helve-26_2-final-third-layer-128.json
```

Upload **only** the resulting bounded source-free JSON or the exact bounded failure tag. The next Rust lowering must use the actual reported Marker kinds, nested RangeChoice bounds/branches, and second MulOrAdd parameter rather than assuming a general vanilla law. The previous root/inner/second/512/768/mixed fixtures are frozen. All source-law, marker/NoiseChunk, VAR/SEM, full-router and production flags remain false.


## Third-layer original-JVM result and partial Rust lowering (21 October 2026)

**The actual source-owning third-layer diagnostic succeeded without recapturing previous fixtures.** The original private source-free receipt (do not commit) is 92,321 bytes, SHA-256 7379c8e0282f642b4780be40810d2dcd871d06a2f5bacdcffaba3b264248dd81. It contains 128 genuine SinglePointContext observations across four seeds. The four actual graph shapes are seed-invariant; all arithmetic checks pass 128/128; recomputing all four columns of the previously frozen second-layer fixture from this report reproduces SHA-256 e684407be3e3d8ef5435c7518a0d4f5adbccae134684a730b216a11212874f4a exactly.

### Actual newly discovered graph

- MIN's left side: Mapped SQUEEZE(Interpolated Marker(MulOrAdd MUL 0.64 (BlendDensity Marker (MulOrAdd [unexpanded])))).
- MIN's right side: HolderHolder to RangeChoice [-1_000_000, 0). Its selector is an Interpolated Marker of another real RangeChoice [-60, 321), with HolderHolder selector [unexpanded], in-range Noise [unexpanded], and out-of-range Constant(-1).
- Outer in-range is Constant(64). Outer out-of-range is Ap2 ADD(Interpolated Marker(RangeChoice [unexpanded]), MulOrAdd MUL 1.5 (Ap2 [unexpanded])).
- Nested choice selects 108 in / 20 out. The nested out operand is -1 for all 128. Both newly discovered Marker delegations match 128/128 only in SinglePointContext; BlendDensity must not be conflated with Interpolated in real NoiseChunk.
- Nested HolderHolder output equals block Y in 124 rows but at Y=-4096 returns -4064 for each of the four seeds. This **suggests** a clamped/offset vertical primitive but is NOT a verified all-input law; investigate its actual holder target.
- Actual left and outside constant arguments are binary64 0x3fe47ae147ae147b (0.64) and 0x3ff8000000000000 (1.5). The nested bounds are 0xc04e000000000000 (-60) and 0x4074100000000000 (321).

### Frozen new evidence and implementation

Only six genuinely new IEEE f64 input words per XYZ are committed in crates/world/helve-world-gen/tests/data/stock_finaldensity_third_layer_new_128_rawbits.tsv: exactly 13,056 bytes, SHA-256 bacf33b5d8274083ad3e5ff5a557d66dc9c999c07d9f358b0e06e1978fe79181. It has strict old bit-anchor verification, original receipt length/SHA admission, actual class/parameter/branch verification and mutation tests in tools/worldgen_26_2_stock_finaldensity_third_layer_fixture.py and tools/tests/test_worldgen_26_2_stock_finaldensity_third_layer_fixture.py.

For private original receipt validation only (no new JVM capture): python3 tools/worldgen_26_2_stock_finaldensity_third_layer_fixture.py --capture /tmp/helve-26_2-final-third-layer-128.json

The new Rust test crates/world/helve-world-gen/tests/stock_finaldensity_third_layer_262.rs independently verifies nested RangeChoice and MUL(1.5) even when lazy branches skip them, then assembles a single 14-node COLD-validated backwards-only graph using the true previously captured constants and previous root oracle. Four still-unexpanded graph leaf operands remain original-JVM injected. No production graph authority or NoiseChunk lifecycle is claimed.

### Next genuinely unknown fourth layer

Inspect only: (1) the BlendDensity Marker's wrapped MulOrAdd operation, coefficient, child; (2) nested selector HolderHolder target; (3) outside Interpolated Marker's wrapped RangeChoice selector, thresholds and two branch types; (4) outside MUL 1.5's wrapped Ap2 operator and both children. The newly seen nested Noise additionally needs actual noise registry-key/scale binding. Strictly no repeat of old root, inner, second, third, 512 cell, 768 NoiseChunk or 1152 delegate captures. All source-law, NoiseChunk marker-lifecycle, full-router, independent VAR/SEM and production admission gates stay false.


## Fourth-layer source-owning observer prepared after green merged #487

The actual third-layer owner receipt has been independently frozen and merged: PR #487, main commit 1d843bc2b5c8dfbb29387c822586ec2bb12dbd46. The fourth-layer instrument is implemented in tools/worldgen_java/HelveStockFinalDensityFourthLayer262.java and tools/worldgen_26_2_stock_final_density_fourth_layer.py with synthetic failure and JDK compilation tests in tools/tests/test_worldgen_26_2_stock_final_density_fourth_layer.py.

The instrument follows only the four **actually established** runtime types and discovers (1) BlendDensity's wrapped MulOrAdd specificType, argument and density input; (2) nested HolderHolder's real delegate target; (3) outside Interpolated RangeChoice selector, in/out child classes and exact inclusive/exclusive bounds; (4) the second MulOrAdd's wrapped Ap2 actual type and both children. It emits exactly **seven new input words per original fixed XYZ**. It also calculates **four old third-layer values only as strict equality anchors**, checking them against the frozen third-layer TSV SHA bacf33b5d8274083ad3e5ff5a557d66dc9c999c07d9f358b0e06e1978fe79181. It does not export old oracles again, holder registry data, Java source/binary, source methods or original exception messages.

The previously unknown Ap2 operation must be read before any source-faithful Rust arithmetic lowering. The transport **does not guess** an Ap2 formula. It checks strict original enum identities, all new argument classes, finite IEEE operands, real constant MulOrAdd output bits, HolderHolder single-point forwarding and outer RangeChoice selected input. Any mismatch fails with a bounded original-JVM phase tag and leaves no approved capture. Source-law, NoiseChunk lifecycle, independent VAR/SEM, full-router and production remain false.

**After this fourth-layer PR is green and merged**, run only the new diagnostic on the private source-owning machine, no repeats:

    cd ~/Crucible
    git switch main
    git pull --ff-only
    python3 tools/worldgen_26_2_stock_final_density_fourth_layer.py \
      --source "$HOME/Documents/mc-source/mc-src.zip" \
      --db .crucible/vanilla/atlas.sqlite \
      --lock vanilla/vanilla.lock.toml \
      --output /tmp/helve-26_2-final-fourth-layer-128.json

Only upload the resulting bounded source-free JSON (or the exact bounded failure stage/class). The next lowering must use its actual first MulOrAdd argument, nested Holder target, outside choice bounds and Ap2 type—not historical Minecraft guesses.


## Fourth-layer original-JVM receipt succeeded and frozen (22 October 2026)

**Do not repeat the fourth-layer or earlier captures.** The original 26.2 fourth-layer source-free JSON is 97,865 bytes, SHA-256 fb4d7207276311b6853e6bb25d407137417111432d1b3a937c623a5ab866d19f (the original private JSON stays off GitHub). It declares the same actual graph for all four world seeds and 128 finite SinglePointContexts. Every one of the four *previously frozen third-layer outputs* per point matches the new report bit-for-bit: 512/512 independent anchors. Third-layer original fixture SHA bacf33b5d8274083ad3e5ff5a557d66dc9c999c07d9f358b0e06e1978fe79181 unchanged.

Actual source-observed fourth children:
- BlendDensity Marker's inner MulOrAdd is **ADD (0x3fbe000000000000 = 0.1171875)** applied to an actual **Ap2**. It matches 128/128 ordinary finite raw binary64 additions.
- Nested RangeChoice's HolderHolder target is **YClampedGradient**. The earlier Y=-4096 observation of -4064 is no longer cause to guess identity with block Y; the actual target's lower/upper heights and values must be separately observed and source-reviewed. HolderHolder forwards the delegate's 128 original outputs bit-for-bit.
- Outside Interpolated Marker wraps a **RangeChoice [-60,321)** whose input is another **HolderHolder**, in-range child is **MulOrAdd**, and out-of-range is **Constant(+0)** on all 128 observed points. Branches select 108 in / 20 out with 128/128 raw-bit parity.
- Outside MUL(1.5)'s child is **Ap2 MAX(Mapped, Mapped)**, with 44 left wins, 64 right wins and 20 ties (128/128 finite raw-bit matches). The two Mapped subgraphs and the Ap2 MAX NaN/signed-zero corner behavior remain source-law unreviewed.

The permanent fourth-layer fixture is crates/world/helve-world-gen/tests/data/stock_finaldensity_fourth_layer_new_128_rawbits.tsv: 128 x 7 **new** input words, exactly 15,232 bytes, SHA-256 149ebe4d87dbbf2ebc1d40bc5149656b5e50ae16db16bf9d9210f3510b37543c. Earlier values are used ONLY as old separate TSV output anchors; no new old-root fixtures. Run strict read-only optional private original receipt verification with:

    python3 tools/worldgen_26_2_stock_finaldensity_fourth_layer_fixture.py \
      --capture /tmp/helve-26_2-final-fourth-layer-128.json

The new typed Rust ExplicitAp2Max node is bounded and source-unadmitted. crates/world/helve-world-gen/tests/stock_finaldensity_fourth_layer_262.rs individually checks original ADD, outside RangeChoice and MAX even when higher branches skip their computation, then assembles one cold-validated **20-node** partial true graph against the **original frozen finalDensity MIN root for 128 points**. It retains the actual Y-gradient, left Ap2, both MAX Mapped leaves, outside MulOrAdd leaf and original inner Noise as **JVM-injected** operands; there is still no fully native world-seed density router. This adds no production hot-path work and admits no factory rewrite or lifecycle assumptions.

### Next fifth-layer source-owning frontier

Only descend newly unresolved actual branches: (1) left ADD's child Ap2 enum and two real child types; (2) the YClampedGradient actual gradient endpoints (bounds and densities) and whether the two HolderHolder targets are source-identical, without assuming so from equal single-point samples; (3) outside RangeChoice's HolderHolder target class and exact delegation; (4) outside in-range MulOrAdd operation, finite argument and child type; (5) both MAX Mapped nodes' mapping enum and wrapped child classes. Separately source-review the existing nested Noise registry key/scales for coherent native qualification. Keep captures bounded and use **only new leaf words** with fourth-layer old anchors; no previous capture reruns. Independently qualify source-law, NoiseChunk cache/interpolation and production admission before ever connecting generated terrain to live publication. All previously false admission flags stay false.


## Fifth-layer bounded source-owning observer prepared after fourth-layer #489

PR #489 merged completely green; verified main immediately after its merge: 13186f2aa5491562f9f4abdd3f0037d76cebdb3e. Fourth-layer private owner report is already completed; **never repeat it**. Its six old outputs are not reproduced as new permanent fixtures. The fifth-layer code is tools/worldgen_java/HelveStockFinalDensityFifthLayer262.java and tools/worldgen_26_2_stock_final_density_fifth_layer.py, with strict mock transport, false-admission, source-pin, no-owner and Java compilation tests in tools/tests/test_worldgen_26_2_stock_final_density_fifth_layer.py.

The original JVM must identify the actual left Ap2 enum, two child classes and per-sample operands; the YClampedGradient record's real from/to heights and density endpoints; the outside HolderHolder target; the outside in-range MulOrAdd operation, argument and child; and both MAX Mapped enum kinds, child classes and input values. Precisely **six new source-owning scalar child values per original XYZ**; five fourth-layer values are checked bit-for-bit against the independently frozen fourth-layer seven-word fixture SHA 149ebe4d87dbbf2ebc1d40bc5149656b5e50ae16db16bf9d9210f3510b37543c, and are not exported again as permanent fixtures. This is a fixed-size original-26.2-SinglePointContext graph exploration, not a NoiseChunk lifecyle or source-law admission.

When the fifth observer's own PR passes CI and has merged, run **only** the next bounded diagnostic locally on the private source owner (no root/inner/second/third/fourth/512-cell/768-NoiseChunk recapture):

    cd ~/Crucible
    git switch main
    git pull --ff-only
    python3 tools/worldgen_26_2_stock_final_density_fifth_layer.py \
      --source "$HOME/Documents/mc-source/mc-src.zip" \
      --db .crucible/vanilla/atlas.sqlite \
      --lock vanilla/vanilla.lock.toml \
      --output /tmp/helve-26_2-final-fifth-layer-128.json

Upload only the source-free bounded fifth-layer JSON or exact source-free `HELVE26_2_FIFTH_FAILURE` phase and exception class. YClampedGradient field reflection is guarded: a shape or record-component change must fail closed, never trigger a guess or alternate semantics. All source-law, registered noise binding, marker interpolation, VAR/SEM and production publishing gates stay false.


## Actual fifth-layer original-JVM receipt and Rust parity (22 October 2026)

**The fifth-layer owner execution succeeded; it must not be rerun.** Uploaded original stock Java 26.2 source-free JSON is exactly **103,398 bytes** with SHA-256 **0116b9cc0d7ed21edc19a93b37a99207f37726fa781affbd7901dc814b390bbd**. It records four seed-invariant runtime shapes and 128 finite `DensityFunction$SinglePointContext` observations. The parent fourth-layer fixture remains 15,232 bytes, SHA-256 149ebe4d87dbbf2ebc1d40bc5149656b5e50ae16db16bf9d9210f3510b37543c. Five independent original-fourth output words per point remain frozen equality anchors (**640 comparisons**); no previous root, inner, second, third, fourth, cell or NoiseChunk captures are repeated.

Actual new graph nodes, *not* historical guesses:

- The left `Ap2` is real `MUL(YClampedGradient, MulOrAdd)`; 128/128 exact finite binary64 products. Its left gradient's **own source record parameters have not been collected**, so that operand remains an original-JVM leaf.
- The nested selector's `HolderHolder` target is a real `YClampedGradient` with record `fromY=-4064, toY=4062, fromValue=-4064, toValue=4062`. The already-existing Rust gradient primitive matches the original nested selector at all 128 fixed Y positions (including the four Y=-4096 clamps), but all-input source law is NOT admitted.
- The *outside* selector's `HolderHolder` target class is also `YClampedGradient`; its **own record bounds are NOT exposed**. Its observed outputs match the same clamp for 128 points, but **DO NOT alias** this target to the nested gradient or assert identical source parameters.
- The outside in-range `MulOrAdd` is `ADD` of exact IEEE coefficient `0xbfb3333333333334` (approximately −0.075) and another `MulOrAdd` child. 128/128 finite word matches.
- Both MAX children are `Mapped ABS(Marker)`, each 128/128 original input-to-output word matches (**256/256**). The two Markers still have genuine NoiseChunk cache/interpolation obligations.
- The original first/second/.../fifth `finalDensity` partial graph is now assembled as one **25-node** cold-validated backwards-only bounded Rust candidate; only genuinely unknown child operands are injected, and the existing gradient primitive is used at real fixed block Y. Existing production hot paths are unchanged.

**New evidence fixture only:** `crates/world/helve-world-gen/tests/data/stock_finaldensity_fifth_layer_new_128_rawbits.tsv` contains 128 × 6 *new* IEEE-754 child inputs, exactly **13,056 bytes**, SHA-256 **1f0c3cf5e9c7fda8a8c348d68d431a99f4c3871611dacd48a97a442ed95a9433**. `tools/worldgen_26_2_stock_finaldensity_fifth_layer_fixture.py` verifies exact private owner report bytes/SHA (optional), stock source/JAR/Atlas/registry/method pin transport, seed-invariant exact runtime shape and all previous parent output bit anchors; mutation tests are in `tools/tests/test_worldgen_26_2_stock_finaldensity_fifth_layer_fixture.py`. The new `CandidateAbs` finite operator is implemented in both standard and demand Rust paths; `crates/world/helve-world-gen/tests/stock_finaldensity_fifth_layer_262.rs` separately checks every newly observed operator even when lazy parents mask it, and the original older MIN root across 128 sample points.

Read-only original JSON authentication (if needed, no recapture):

    python3 tools/worldgen_26_2_stock_finaldensity_fifth_layer_fixture.py \
      --capture /tmp/helve-26_2-final-fifth-layer-128.json

### Next sixth-layer frontier: advance genuine source leaves, not old oracles

The real graph is now narrower. A new bounded original-JVM source-owner descent, if needed, must inspect only: (1) *left* `Ap2` Y-gradient **own** record bounds and its right `MulOrAdd` actual operation/argument/child; (2) the **outside** `YClampedGradient` own record bounds, permitting an independent exact structural equality test against the nested one; (3) outside in-range `MulOrAdd` child's operation/argument/child; and (4) the actual child types beneath the **two ABS Markers** (with distinct marker kinds). Separately review the existing nested `Noise` registry key, scales and noise-seeding binding, and qualify the full canonical `NoiseChunk` lifecycle before production. Preserve the existing performance, reusable seeded-noise stack, bounded allocation-free scratch and true source-gated publication architecture. All source-law, NoiseChunk, full-router, VAR/SEM and production gates remain FALSE.


## Sixth-layer next source-owning four-child diagnostic (after green merged #491)

PR #491 has merged with all eight checks green. Original private fifth-layer source-free JSON 103,398 bytes, SHA-256 0116b9cc0d7ed21edc19a93b37a99207f37726fa781affbd7901dc814b390bbd and its exact six-column fixture 13,056 bytes, SHA-256 1f0c3cf5e9c7fda8a8c348d68d431a99f4c3871611dacd48a97a442ed95a9433, are completed **do-not-recapture** evidence. Current fifth-layer observed finite graph has a 25-node Rust candidate tested against the frozen MIN root on 128 original points. Production remains forbidden.

The bounded **sixth-layer** original-26.2-JVM bridge is staged in tools/worldgen_java/HelveStockFinalDensitySixthLayer262.java with transport and source-pin validator tools/worldgen_26_2_stock_final_density_sixth_layer.py and synthetic plus JDK tests tools/tests/test_worldgen_26_2_stock_final_density_sixth_layer.py.

This instrument explores only the remaining four genuine unknown child values: (1) left-MUL's child MulOrAdd input; (2) outside-ADD's child MulOrAdd input; (3) first right-side ABS Marker child; (4) second right-side ABS Marker child. It also inspects **each separate real YClampedGradient record** (left Ap2 and outside Holder) to test whether either equals the already-known nested selector, without guessing. It reads **six old fifth-layer output words ONLY as independent immutable equality anchors** and does NOT promote them to new fixtures; strict exact enum record components, gradient finite bounds, operation bit parity, Marker SinglePointContext forwarding, source archive/server/Atlas/method pins, fixed four seeds and all prior false admission gates fail closed. No code paths report Java source text, original registries, JAR bytes, private stack traces or exception messages.

After this sixth PR passes all CI and is merged, run exactly the next new diagnostic on the private original source-owner machine; DO NOT repeat old captures:

    cd ~/Crucible
    git switch main
    git pull --ff-only
    python3 tools/worldgen_26_2_stock_final_density_sixth_layer.py \
      --source "$HOME/Documents/mc-source/mc-src.zip" \
      --db .crucible/vanilla/atlas.sqlite \
      --lock vanilla/vanilla.lock.toml \
      --output /tmp/helve-26_2-final-sixth-layer-128.json

Upload only the bounded source-free sixth-layer JSON, or paste the precise original `HELVE26_2_SIXTH_FAILURE` tag with failure phase/class. Deeper native lowering must wait for the observed operators and Marker child types, while independent source-law, NoiseChunk marker lifetimes, all-input density router, VAR/SEM and production-worldgen admission remain false.


## Original sixth-layer 26.2 receipt — completed (22 October 2026)

The owner's **authentic original-JVM sixth-layer** JSON was uploaded and verified against the original fifth-layer owner receipt; **do not recapture this or any of the earlier root/inner/second/third/fourth/fifth/512-cell/768-NoiseChunk oracles**.

- Original **93,302-byte** private JSON, SHA-256 **597287a4fde98d3fd2f984f6c4b9de20016782e8fd45532092fd797d5697aa35**. Four seed-invariant authentic runtime shapes, 4 × 32 finite SinglePointContext XYZ, real pinned Java source/JAR and exact recorded source-method SHA metadata. Six old output words per row match the immutable fifth-layer fixture (**768/768 exact parent anchors**).
- Only **four genuinely new IEEE-754 operands per point**, compact **8,704-byte** TSV, SHA-256 **b41f262fe145d82fa5d7f05d586663918c4ad900654a7e0906559405cca1d68e**; no repeated old output words are copied into the new fixture. The permanent validator verifies exact SHA/length, the old pinned fifth-layer parents and independent child arithmetic; optional original JSON checking verifies exact byte identity, original provenance and source-free schema.
- The observed **left Ap2 gradient** really is \`YClampedGradient(-64,-40,0.0,1.0)\`: its original output matches the existing primitive at all 128 sampled Y values, including -63 and -4096.
- The observed **outside HolderHolder gradient** is **independently** \`YClampedGradient(-4064,4062,-4064,4062)\`; exactly the same **record fields** as the nested selector's earlier observed gradient. This does not by itself establish they are the same object, but they do not need source aliasing to use two cold-created immutable primitive nodes.
- The left inner \`MulOrAdd\` is actual **ADD argument 0xbfbe000000000000 (-0.1171875)**, child class itself \`MulOrAdd\`. The outside inner \`MulOrAdd\` is actual **MUL argument 0xbf9999999999999a (-0.025)**, child class **\`Noise\`**. Each independently agrees on **128/128 exact finite operations**, not just an accidentally lazy outer root.
- **Both MAX-side \`Mapped ABS\` Marker children** are actual \`Marker(type=Interpolated, child=RangeChoice)\`. Their original original-JVM single-point forwarding is exact **256/256**, but neither NoiseChunk interpolation/cache lifecycle nor either child RangeChoice graph is yet known.
- The source-free owner report explicitly contains \`"source_text_included": false\`. The initially merged sixth transport expected an older report schema lacking the field; this changes **only the strict negative provenance field**, not arithmetic, Java source identity or graph evidence. The corrected source-owner validator explicitly requires **false** and emits **false** in future sixth-layer transport. Never silently discard or ignore this transport field.
- The Rust partial \`finalDensity\` now uses **27 immutable, statically bounded, backward-only nodes**, including both native Y-gradient records, both real inner MulOrAdd operations, existing outer arithmetic, ABS, nested choices and the final MIN; only genuinely unresolved inner \`MulOrAdd\`, \`Noise\` and two \`RangeChoice\` values remain stock-JVM injected. The independent old original-JVM root fixture is the only final equality oracle for the same 128 coordinates.

**Next genuine seventh-layer source-owning frontier:** inspect the **left inner MulOrAdd** operation/constant/dependency; inspect **both distinct Marker-wrapped RangeChoice** min/max and selector, when-in, when-out *runtime classes and numeric values*; inspect whether the known real outside \`Noise\` can already bind to the existing source-locked keyed registry/noise-seed Rust implementation. Do not ask the original JVM to recapture old parent values except fixed equality anchors; do not assume cache markers match SinglePointContext outside the observed context. Check whether the two RangeChoice subgraphs share source structure before collapsing anything, but no alias guesses. Independent source-law, stock NoiseChunk cache/interpolation lifecycle, complete native seeded router, VAR/SEM and **production admission remain FALSE**.

Verification of an already available original private JSON (does not execute JVM):

    python3 tools/worldgen_26_2_stock_finaldensity_sixth_layer_fixture.py \
      --capture /tmp/helve-26_2-final-sixth-layer-128.json

No original-owner JSON/source/JAR/private Atlas content is committed.


## Seventh-layer source-owner probe prepared (22 October 2026; **NOT EXECUTED**)

After the original sixth-layer receipt, PR #493 merged with all eight CI checks green; \`main\` advanced to **90601a31aac7fa8b8b5e0283c50d1c01e174085a**. The exact **93,302-byte original private sixth-layer JSON** (SHA-256 **597287a4fde98d3fd2f984f6c4b9de20016782e8fd45532092fd797d5697aa35**) and exact **8,704-byte sixth-layer four-column source-free fixture** (SHA-256 **b41f262fe145d82fa5d7f05d586663918c4ad900654a7e0906559405cca1d68e**) are **FROZEN; do not recapture**.

The 27-node bounded partial native Rust \`StockDensityProgram262\` exercises both actual gradients and the two nested arithmetic operators with original root 128-point parity. It is a **candidate**; it does NOT implement the remaining seeded \`Noise\`, marker-interpolated choices or stock \`NoiseChunk\` sampling.

The new \`tools/worldgen_26_2_stock_final_density_seventh_layer.py\` + \`tools/worldgen_java/HelveStockFinalDensitySeventhLayer262.java\` is the only next original-JVM diagnostic. It explores **three actual unresolved nodes only**, with the previously observed original stock 26.2 graph as its exact source shape anchor:
(1) left deeper \`MulOrAdd\` actual enum operation/IEEE coefficient and one child class/value;
(2–3) both separate \`Interpolated Marker -> RangeChoice\` genuine numeric bounds, selector/in/out classes, and selector/in/out finite words.
The two nested choices must be independently evaluated even if a parent MIN/RangeChoice would skip them. **Seven NEW IEEE words/point** are emitted; just three sixth-layer words/point are read and compared **as old immutable anchors only**. This preserves old root/inner/second/third/fourth/fifth/sixth, 512-cell and 768-NoiseChunk captures.

The source-owner transport is finite, strict-seed/XYZ, source/JAR/Atlas/method SHA-locked, two-branch runtime shape locked, no extracted Java source, private exception messages or registries. All previous false admission flags stay false, including all-input density law, stock NoiseChunk interpolation, VAR/SEM, seeded full-router and production.

**After the seventh-layer PR merges green, run on the private original-source owner only:**

    cd ~/Crucible
    git switch main
    git pull --ff-only
    python3 tools/worldgen_26_2_stock_final_density_seventh_layer.py \
      --source "$HOME/Documents/mc-source/mc-src.zip" \
      --db .crucible/vanilla/atlas.sqlite \
      --lock vanilla/vanilla.lock.toml \
      --output /tmp/helve-26_2-final-seventh-layer-128.json

Upload that source-free seventh JSON, or paste the \`HELVE26_2_SEVENTH_FAILURE|<phase>|<exception-class>\` original-JVM failure tag; **do not rerun any previously frozen capture**.

**Architecture note:** the 27-node graph currently retains Helve's existing 32-node limit. Native expansion of two distinct RangeChoice subgraphs may not fit one flat 32-node program; compare original graph sharing and use separately cold-validated smaller subgraphs/composition if necessary. Do **NOT** silently increase hot-path scratch or heap allocations merely to fit more layers, and do not guess structural aliasing between distinct source nodes.
