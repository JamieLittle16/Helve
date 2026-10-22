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


## Seventh actual original JVM report — parity closure (22 October 2026)

The original private 26.2 seventh-layer capture **completed successfully** after #494. Source-owner JSON is **87,635 bytes**, SHA-256 **9b7adeb5d9fdec39e78668e5cd89d14e8134d31cd38ae8109444d23e72f16f4a**, pinned earlier sixth fixture **b41f262fe145d82fa5d7f05d586663918c4ad900654a7e0906559405cca1d68e** and parent owner JSON **597287a4fde98d3fd2f984f6c4b9de20016782e8fd45532092fd797d5697aa35**. Four seed-invariant real Java shapes, 128 distinct pinned SinglePointContext observations; original source/archive, JAR and unreviewed method-body SHA pins unchanged, all production/source/VAR-SEM/NoiseChunk/whole-router admissions FALSE. **Do not rerun this capture**.

New precise graph discoveries:

1. Real seventh left deeper \`MulOrAdd\` is \`ADD\` with bit coefficient \`bfb4000000000000\` (-0.078125), child class actual \`DensityFunctions$Ap2\`. Its 128 new children reproduce the six-layer independently frozen left parent output bit-for-bit.
2. The **two distinct** \`Interpolated Marker -> RangeChoice\` subgraphs are *both* original Java \`RangeChoice(-60,321)\` with \`HolderHolder\` selector, *different actual* \`Noise\` when-in inputs and \`Constant(+0)\` when-out inputs. Each selects Noise **108/128**, zero **20/128**, exact raw bits. Different in-range Noise words prohibit incorrectly aliasing the two RangeChoice graphs.
3. Both real HolderHolder selector outputs match one another and the previously separately observed native \`YClampedGradient(-4064,4062,-4064,4062)\` output **128/128**, including original Y=-4096 yielding -4064. This is precisely a **bounded sample-value observation, not a source law or proof of Java object identity**.
4. The old sixth originals \`left_mul_child_bits\`, \`left_marker_child_bits\`, \`right_marker_child_bits\` remain **384/384 exact independently frozen parent anchors**. The new fixture has only **seven genuinely new child raw words** per XYZ (896 new IEEE raw words), **15,232 bytes** and SHA-256 **f749b5a0d6519de971a8a715d02e306111f04a697d7c4c3068aefc0f54c6bd92**. It does not duplicate old root, previous output words, original source or private registries.
5. The reconstructed **30-node**, cold-validated, backwards-only native Rust partial \`finalDensity\` graph fits the existing hard **32-node** bound by reusing the independently 128/128-equal selector output and common constant(+0) *for this finite parity test only*. It contains real left deep ADD and two real RangeChoice operations with **distinct JVM-fed Noise leaves**; it does **not** claim seeded native Noise, Marker interpolation in NoiseChunk, or an all-input sharing law. Independent tests check the newly explicit operators even if the parent MIN would short-circuit.
6. Original private receipt checks are explicit and fail closed: original full-report bytes/SHA, all four real runtime shapes, exact fixture SHA, all seven new IEEE input columns, three old independent sixth-layer parents, actual operator/choice arithmetic and original source-method hashes and every false gate. Run the already-owned exact seventh private receipt check (no Java execution) with:

       python3 tools/worldgen_26_2_stock_finaldensity_seventh_layer_fixture.py \
         --capture /tmp/helve-26_2-final-seventh-layer-128.json

**Next true eighth-layer frontier:** descend into the genuine left deeper \`Ap2\` (operation enum, its two children and independent 128-point child outputs) and read the two separate \`HolderHolder\` selector **targets and actual record fields**, to determine whether all-input source-honest selector-sharing is warranted. Separately bind the now-three-or-more outstanding actual \`Noise\` inputs only by reviewing original 26.2 named-noise holders/seeded settings and immutable native noise constructor/registry laws; original \`SinglePointContext\` observations alone do not justify that. Avoid private registry exports or recapturing any root/second/third/fourth/fifth/sixth/seventh, 512-cell, 768-NoiseChunk oracle. Existing 32-node cap/hot-path no-allocation requirement remains strict; if the new native topology grows beyond 32 distinct reachable nodes, first seek source-grounded sharing or bounded compositional evaluator stages, never simply raise scratch.


## Eighth original JVM source-only frontier — prepared, not executed (22 October 2026)

After all **eight** required checks green, **PR #495 merged** the exact seventh 30-node finite raw-bit parity into \`main\` as **e0bc616913e960f6cc0442295052cd08fae73e20**. Original seventh report **87,635 bytes SHA 9b7adeb5d9fdec39e78668e5cd89d14e8134d31cd38ae8109444d23e72f16f4a**, seventh new-operand fixture **15,232 bytes SHA f749b5a0d6519de971a8a715d02e306111f04a697d7c4c3068aefc0f54c6bd92**. The old seventh and all earlier evidence are **frozen** and must never be recaptured.

The next only **source-owning eighth-layer** program is \`tools/worldgen_26_2_stock_final_density_eighth_layer.py\` with Java diagnostic \`tools/worldgen_java/HelveStockFinalDensityEighthLayer262.java\`. It observes the actual two inputs/enum/child classes of the real deeper left \`Ap2\` that was revealed by the seventh JVM, and separately unwraps **both** \`HolderHolder\` selectors of the two Marker RangeChoice branches. It inspects each target's actual density runtime class and Y-gradient record parameters. The original stock *numeric* target and holder output are compared independently; matching sampled outputs do not establish Holder source semantics or all-input aliasing. Only **two genuinely new Ap2 operand IEEE words per point** are intended for the next permanent fixture (the prior Ap2 result and two older selector outputs are immutable consistency anchors, not recaptured oracle data). The two target output observations are source-law evidence only and should not be recopied into the final fixture if identical.

This diagnostic keeps pinned source/JAR/Atlas and method hashes, exact four-seed/32 XYZ finite bounds, explicit source-text exclusion and every production/VAR-SEM/whole-router/NoiseChunk/actual all-input admission flag FALSE. No old root/inner/second/third/fourth/fifth/sixth/seventh/512-cell/768-NoiseChunk recaptures. The original JVM owner alone runs the program; CI's Java compilation and synthetic frames are **not proof of its original runtime reflection**.

**Once the eighth diagnostic PR is green and merged, run on private original-source owner:**

    cd ~/Crucible
    git switch main
    git pull --ff-only
    python3 tools/worldgen_26_2_stock_final_density_eighth_layer.py \
      --source "$HOME/Documents/mc-source/mc-src.zip" \
      --db .crucible/vanilla/atlas.sqlite \
      --lock vanilla/vanilla.lock.toml \
      --output /tmp/helve-26_2-final-eighth-layer-128.json

Upload only the bounded source-free JSON, or paste the exact \`HELVE26_2_EIGHTH_FAILURE|<phase>|<exception-class>\` marker if original reflection differs. Do not infer full native seeded router, real noise or Marker lifecycle parity from this diagnostic. Preserve 32-node hot-path scratch cap and immutable no-allocation DAG; all further nodes require source-grounded sharing or bounded composition before promotion.

## Eighth original-JVM arithmetic-observation erratum — 22 October 2026

The **first original eighth-layer run** on verified `main` `addd947850ab0983f6b5792fa7bf6a739741d9ed` stopped in the Python transport parser with the exact message `STOCK 26.2 EIGHTH LAYER OPEN: original eighth Ap2 real arithmetic changed`. The original Java program had already emitted finite eighth-layer frames successfully: this **was not** a javac, JVM bootstrap, registry, shape or old parent-anchor failure. No eighth JSON was written or admitted. **Do not run any earlier frozen capture again**.

Cause of the parser rejection: the eighth consumer assumed that a real source-owned `Ap2` record with operator `ADD` or `MUL` must equal Python's unconditional `a+b` or `a*b` for every original IEEE raw-bit pair. This is **not an independently reviewed all-input Java source law**. Earlier native `ExplicitAp2Multiply` already has an explicit positive-zero early-return candidate; IEEE multiplication of +0 by a negative operand would instead yield -0. This is one **possible** cause, **not** a diagnosis of the original eighth operand that failed, because the old error suppressed its operator and sample index. We must not guess that the observed difference is exclusively signed-zero.

The revised eighth source-only consumer therefore **keeps every strict provenance, four-seed graph shape, pinned XYZ, finite original operand, independent old seventh source-frame anchor, two exact `HolderHolder` target-forwarding, source-free/no-registry condition and all false source/VAR-SEM/NoiseChunk/production gates**, but does not discard a genuine original frame solely because an unadmitted Python arithmetic shortcut disagrees. It computes and includes a small **non-authoritative candidate comparison receipt**, with mismatch counts and first row indices for both unconditional IEEE arithmetic and the independently known **positive-zero-only Ap2 multiplication candidate**. The explicit `source_law_admitted=false` field is mandatory and exact-recomputed during JSON validation. This permits precise offline review of the actual finite original eighth operands **once**, without rerunning the entire upstream probe chain or laundering observed disagreement into parity qualification.

The owner command in the preceding section is unchanged; once this erratum PR passes required CI and merges, run it once at the same `/tmp/helve-26_2-final-eighth-layer-128.json` destination, then upload only the new bounded eighth JSON. If either candidate still has mismatches, leave native eighth arithmetic source-law and production admission CLOSED until independently reviewed. All old captures remain frozen.


## Authentic eighth-layer original JVM receipt: zero-shortcut resolved, finite parity closed (22 October 2026)

The **corrected eighth-only** original-stock 26.2 capture completed after green #497. The prior failure was a Python-only unsafe unconditional IEEE-754 multiplication assumption, not a JVM/registry/Java compilation failure. Genuine owner report **67,230 bytes**, SHA-256 **3fae6fa522856983894335830a7f54689bf2534e66c446f6f73f3a3ed1548b58**. Source archive **1e9bca3dff83cd83e7905f8810f1ec9899361fa2dc83fe893bb48beeb04df750**, original official 26.2 JAR **cdacdfb25898de5e4b4b0e5ddcc2722f77067e46605709c2d886c000ebb63ec5**, original Ap2 method SHA **54d44e99cae188665438eda580ab0a76204c0c486b80edb603f32fa4375b3e48**, seventh parent original fixture **f749b5a0d6519de971a8a715d02e306111f04a697d7c4c3068aefc0f54c6bd92**. Original report has four seed-invariant runtime graph shapes, 4 × 32 finite SinglePointContext observations and explicit source_text_included=false. All production, VAR/SEM, all-input, NoiseChunk lifecycle and router parity admission booleans remain **false**.

**Observed structure:** seventh deep-left child is genuine DensityFunctions$Ap2(type=MUL), with left **YClampedGradient** child and right **MulOrAdd** child. Neither child was synthesized from the parent's value. Two real HolderHolder selector targets were separately inspected. They are both **YClampedGradient records** with fromY=-4064, toY=4062, fromValue=-4064, toValue=4062; each direct target's raw bits match its Holder output on **all 128 original samples**. These exact record observations strengthen *sample-only* selector reuse. Three seventh old output anchors per point independently match the frozen seventh fixture (**384/384**); their output columns are not duplicated in the new fixture.

**Original Java Ap2 signed-zero witness:** for precisely original indices **8, 40, 72, 104** (one per seed, XYZ=(0,320,0)), left actual Y-gradient sample is IEEE **+0.0**, the right actual MulOrAdd is a *negative finite value*, naive IEEE multiplication returns **-0.0**, while the original stock Ap2.compute returns **+0.0**. All remaining 124 naive operations match the original bits. Helve's already-existing **ExplicitAp2Multiply positive-zero short-circuit candidate** matches **128/128** real eighth results. This observation is **not** an all-input Java source law or arbitrary instance admission.

The only new permanent fixture contains **two original child raw IEEE words per point**: 128 × 2 = **256** genuinely new values, source-free TSV **4,352 bytes**, SHA-256 **4fc059ebcfb74cf3e0b155460fca8b144c975aaafc653f6da51a913c68fc2c6e**. Its fail-closed validation compares old seventh Ap2 results, the witnessed signed-zero short-circuit, observed finite gradient sampling categories, original source/JAR SHA, shapes, and strict false gates. Optional private owner JSON verification checks exact original byte identity and full metadata:

    python3 tools/worldgen_26_2_stock_finaldensity_eighth_layer_fixture.py \
      --capture /tmp/helve-26_2-final-eighth-layer-128.json

**Native Rust parity:** the new test-only bounded finalDensity candidate contains **exactly 32 immutable, backward-only, cold-validated nodes**. It replaces the previously injected deep Ap2 *output* with two separately JVM-injected actual *children*, combined with native ExplicitAp2Multiply. Independently compare all 128 actual Ap2 results and frozen final MIN-root results. Previous seventh 30-node reconstruction and its independent operator tests remain regressions. The existing 32-node ceiling, stack scratch and allocation-free hot path stay intact; all production world-publishing authority remains disabled. Future expansion must use source-grounded sharing or composition rather than increase the scratch cap.

**Next genuine ninth source-only frontier (not executed):** inspect the original deep-left YClampedGradient's fromY/toY/fromValue/toValue record (eighth observed class only), and deep-right MulOrAdd actual enum, IEEE argument and single wrapped child class/value. Native seeded Noise holder/key/seed settings and true NoiseChunk marker/interpolation traversal are independent, unqualified obligations. **Do not rerun** any root/inner/second/third/fourth/fifth/sixth/seventh/eighth or existing NoiseChunk source captures.


## Ninth-layer source-owner diagnostic staged (22 October 2026; not original-JVM executed)

**PR #498 merged GREEN (all eight CI checks)** at **9dc1355fe168ef1c80b5f659e6a8723b3e6ac56c**. The authentic original eighth 67,230-byte private JSON **SHA 3fae6fa522856983894335830a7f54689bf2534e66c446f6f73f3a3ed1548b58**, and **4,352-byte two-only-new-child fixture SHA 4fc059ebcfb74cf3e0b155460fca8b144c975aaafc653f6da51a913c68fc2c6e**, are fully frozen. The existing no-allocation, cold-validated 32-node test-only Rust candidate matches 128/128 original frozen Java MIN-root words; previous 30-node and all original NoiseChunk evidence remain unchanged.

The next actual source-owning frontier has ONLY TWO unresolved immediate source types:
1. The real deep-left **YClampedGradient** was class-identified and numerically sampled by the eighth Java but its original actual fromY/toY/fromValue/toValue record was not inspected. The ninth bridge reads that record without guessing endpoints from the 1, 1/16, 0 observed output categories.
2. The real deep-right **MulOrAdd** was class-identified and sampled by the eighth Java but its actual specificType enum, IEEE coefficient and sole density child runtime class were not inspected. The ninth bridge reads the exact record and observes **one genuinely new direct child IEEE-754 word per XYZ**. Do not assume its operation is ordinary IEEE arithmetic at signed zero without independent proof. Any direct arithmetic mismatch is recorded as unadmitted candidate telemetry, never suppressed or discarded.

The staged program pair is **tools/worldgen_java/HelveStockFinalDensityNinthLayer262.java** + **tools/worldgen_26_2_stock_final_density_ninth_layer.py**. It verifies the two separately frozen previous eighth original JVM child values as **256 independent old equality anchors**, without repeating old entries in a new fixture. It requires four seed-invariant original 26.2 graph shapes × 32 pinned finite SinglePointContext coordinates, unchanged exact previous eighth fixture/report/source/official JAR/method-body SHA provenance, an explicit source_text_included=false, fixed bounded output and ALL existing production, VAR/SEM, full-router, NoiseChunk marker/cache, arbitrary source-law and ninth admission gates **FALSE**. CI synthetic frames and Java compilation tests do NOT count as original-JVM evidence.

**After the ninth PR passes CI and merges**, run only the one remaining private-source original 26.2 probe (never rerun eighth or any earlier capture):

    cd ~/Crucible
    git switch main
    git pull --ff-only
    python3 tools/worldgen_26_2_stock_final_density_ninth_layer.py \
      --source "$HOME/Documents/mc-source/mc-src.zip" \
      --db .crucible/vanilla/atlas.sqlite \
      --lock vanilla/vanilla.lock.toml \
      --output /tmp/helve-26_2-final-ninth-layer-128.json

Upload the new source-free ninth JSON, or paste its bounded HELVE26_2_NINTH_FAILURE|phase|ExceptionClass if original source reflects differently. On successful genuine ninth evidence, next task is **source-grounded native compositional evaluation**: the current flat finalDensity candidate already uses all 32 allowed nodes. Confirm actual same-record semantics and registry/noise seeding before attempting to lower another Java child; split into bounded cold-validated subgraphs or prove a real graph sharing law rather than increase per-worker hot-path scratch. Nothing so far proves stock NoiseChunk interpolation/cache traversal or production worldgen.


## Actual original ninth Java source-owner capture — verified, native 32-node finite parity (22 October 2026)

**Authentic completed ninth capture**, previously staged by green PR #499: source-free JSON **42,445 bytes**, SHA-256 **66716c9d06ac1eb72f10c2648c9ccc56f68b1d21ceb9bba346de5c15e1bf88d1**. The original 26.2 server JAR/source SHA, first through eighth independent frozen fixtures and actual method-owner/body SHA all remain unchanged; prior eighth original JSON SHA **3fae6fa522856983894335830a7f54689bf2534e66c446f6f73f3a3ed1548b58** and two-word eighth fixture SHA **4fc059ebcfb74cf3e0b155460fca8b144c975aaafc653f6da51a913c68fc2c6e** are independently anchored **256/256**. Four real seed-invariant Java graph shapes, exactly 128 original SinglePointContext XYZ samples, finite IEEE raw bits, source_text_included=false, all qualification/VAR-SEM/NoiseChunk/production flags **FALSE**. No recapture of any preceding oracle.

The genuine deep-left record is **YClampedGradient(fromY=240, toY=256, fromValue=1.0, toValue=+0.0)**, directly observed with exact record fields. It produces original finite 128 left-child raw words: 112 times +1.0, 12 times 1/16 and 4 times positive zero at the pinned Y values. The deep-right record is genuine **MulOrAdd(specificType=ADD, argument=+0.078125, child=RangeChoice)**. This is an actual original Java operator/argument/child runtime class, not a guessed algebraic rewrite. The sole newly descended RangeChoice child is evaluated by the original JVM at every one of 128 points. Python unconditional binary64 ADD on those original child bits independently agrees **128/128** with the earlier eighth real right MulOrAdd output. The ninth JSON's naive MulOrAdd mismatch telemetry is **0** with source_law_admitted=false; the positive-zero early-return Ap2 evidence from eighth remains unchanged.

**New permanent compact fixture:** only **128** genuinely new original Java RangeChoice child IEEE words (one/point) in a **2,176-byte** strict lowercase source-free TSV, SHA-256 **1cb8c4ddd35fec84d5a44adfaf4281dcbe3caf9fd30cbe00eb3e8f0a7844ae9d**. No seventh/eighth prior parent or root raw-bit words are recopied. The fail-closed ninth compact fixture checker verifies exact byte count/SHA, 128 finite source-child rawbit words, **128/128 native gradient** samples and **128/128 native right ADD** outputs against separately frozen eighth parents; optional exact full ninth owner JSON byte SHA/length, original ninth validated provenance/method pins, shapes, true source-text exclusion, still-false production gates and immutable new child words.

    python3 tools/worldgen_26_2_stock_finaldensity_ninth_layer_fixture.py \
      --capture /tmp/helve-26_2-final-ninth-layer-128.json

**Native bounded graph topology:** the previous eighth test-only 32-node complete partial finalDensity graph had two numerically identical YClampedGradient nodes for two *distinct* HolderHolder selector wrappers (formerly slots 10 and 14). Their two original target records are independently measured and precisely identical (-4064, 4062, -4064, 4062), and previous seventh/eighth observations confirmed each wrapper matches its own target **128/128**. The revised *finite-test-only* ninth graph shares **one numerical gradient evaluation node**, without asserting Java Holder object identity, all-input Holder forwarding or all-input source-law admissibility. That frees exactly one node, allowing the real deep-left gradient as a native Primitive, one actual JVM-fed RangeChoice child and real native MulOrAdd ADD before existing ExplicitAp2Multiply — **32 backward-only, cold-validated nodes**, within the unchanged maximum. The independently frozen stock Java MIN root is compared 128/128 with this entire candidate; earlier eighth 32-node, seventh 30-node and all lower regressions continue to run. The production HOT evaluator, cache and world-publisher are *untouched*.

**Next genuine tenth original-JVM frontier (not executed):** descend into only the actual deep-right **RangeChoice** discovered here and inspect its independent selector and two branches, exact range bounds and their independently original values at the 128 existing pinned XYZ contexts. Do not alias any old RangeChoice by sampled output or class similarity without source-grounded identity. At 32 nodes, any further native extension requires another genuinely source-grounded common subexpression or fixed-cap, allocation-free compositional stages. Original named Noise constructor/registry seeding and NoiseChunk actual Marker/cell interpolation/lifecycle and production/VAR-SEM are separate outstanding obligations. All previous root through ninth, 512-cell and 768-NoiseChunk oracles remain frozen.


## Tenth source-owner right-hand RangeChoice frontier staged, not executed (22 October 2026)

**PR #500 merged, all eight CI checks green:** main SHA **dcb725813902ef1b3bb40f51e7d567f82259321b**. Authentic ninth source-owner report **42,445 bytes SHA 66716c9d06ac1eb72f10c2648c9ccc56f68b1d21ceb9bba346de5c15e1bf88d1** and one-word-per-XYZ source-free fixture **2,176 bytes SHA 1cb8c4ddd35fec84d5a44adfaf4281dcbe3caf9fd30cbe00eb3e8f0a7844ae9d** are frozen. All ninth actual Java records and 128 frozen MIN-root results remain independently tested. The fully native partial ninth graph still fits **32** immutable backwards-only nodes without increasing hot-path scratch, using *finite-sample justified numerical* sharing of the two original same-record Holder selector gradients. No all-input/NoiseChunk/full-router/VAR-SEM or production admission.

The next **only genuine source-owning tenth** diagnostics are **tools/worldgen_java/HelveStockFinalDensityTenthLayer262.java**, **tools/worldgen_26_2_stock_final_density_tenth_layer.py** and their synthetic CI regression. They descend *only* into the actual original Java **RangeChoice** already established as the right-child of the real deep-right MulOrAdd ADD(+0.078125) node. Reflect its actual minInclusive/maxExclusive floating-point rawbit words, the actual runtime class of its selector and each of its separate in/out branch children; then sample **only those three new independently genuine JVM-fetched child IEEE words per point** at the same four seeded groups × 32 pinned SinglePointContext XYZ. Re-observe the original RangeChoice output only as an exact old parent equality anchor against the committed ninth fixture, never freeze that value again. Standard >=min and <max branch choice is recorded only as a **candidate mismatch telemetry**, never as an all-input source-law admission or reason to discard genuine original raw data.

The source-only Python bridge requires the exact previously frozen ninth report/fixture SHA, source archive and official Java server JAR hashes, three prior indexed source-owner method hashes, finite 4×32 frames, four seed-invariant actual graph shapes, strict old parent parity 128/128, no source text or registry exports, and every existing source-law, native seeded Noise, NoiseChunk marker/interpolation, VAR/SEM, full router and production admission flag FALSE. JDK compilation plus synthetic CI frames do NOT count as original stock runtime evidence.

**After tenth PR passes CI and merges, execute exactly this one NEW original-JVM probe on the private source owner:**

    cd ~/Crucible
    git switch main
    git pull --ff-only

    python3 tools/worldgen_26_2_stock_final_density_tenth_layer.py \
      --source "$HOME/Documents/mc-source/mc-src.zip" \
      --db .crucible/vanilla/atlas.sqlite \
      --lock vanilla/vanilla.lock.toml \
      --output /tmp/helve-26_2-final-tenth-layer-128.json

Provide only the bounded source-free tenth report or the exact HELVE26_2_TENTH_FAILURE|phase|ExceptionClass marker. No eighth/ninth or earlier owner capture needs replay. At the current strict 32-node budget, source-grounded graph sharing or separately cold-validated finite stages are necessary before any further native lowering; do NOT expand scratch and do NOT infer real NoiseChunk traversal from SinglePoint samples.


## Authentic tenth original-JVM RangeChoice receipt and composed parity (22 October 2026)

The tenth source-owner probe staged by green PR #501 was **actually executed against the original Minecraft Java 26.2 JVM**, with four stock seed-owned graph shapes × 32 independently pinned XYZ. Its source-free JSON is **45,434 bytes**, SHA-256 **b5bed75d54e2704718af4795407614ebd591330cb714263e61e6d7a21e8c3e8e**. Independently committed prior ninth source-only fixture SHA **1cb8c4ddd35fec84d5a44adfaf4281dcbe3caf9fd30cbe00eb3e8f0a7844ae9d** and original ninth report SHA **66716c9d06ac1eb72f10c2648c9ccc56f68b1d21ceb9bba346de5c15e1bf88d1** remain unchanged, 128/128 old ninth RangeChoice outputs exactly anchored. Immutable original archive, 26.2 official JAR, real indexed method SHAs, source-free policy and all false qualification flags are verified. No earlier root, NoiseChunk, seventh/eighth/ninth, or other original JVM oracle was regenerated.

**Genuine tenth runtime shape**, identical for all four seeds:
- The real deep-right RangeChoice has **minInclusive=-1_000_000.0** (bits c12e848000000000), **maxExclusive=+1.5625** (bits 3ff9000000000000).
- Its actual selector is runtime class **DensityFunctions$Marker**.
- Its **whenInRange** and **whenOutOfRange** branches are two separately inspected **DensityFunctions$Ap2** objects. Their Ap2 operator, independently wrapped children, actual Java object identity and source bodies are NOT yet inspected or admitted.
- Original finite branch choice min <= selector < max reproduces the prior ninth Java RangeChoice output **128/128 raw IEEE words**, 68 on the in-range branch, 60 on out-of-range, 0 telemetry mismatches with source_law_admitted=false. The in-range Ap2 result equals the selector numerically in 67 of 68 in-range samples, but **differs in one real original-JVM sample**. Selector aliasing without real source evidence would be invalid. Marker/stock NoiseChunk cache or interpolation semantics remain unqualified.

**New permanent source-free tenth fixture:** ONLY the three genuinely new original-JVM values per point (selector, in-range Ap2, out-of-range Ap2) are frozen: **128 × 3 = 384** new finite IEEE words, TSV **6,528 bytes**, SHA **5786ee42753215750163ec740220082b941e9d34adb76d145bfd43c21f9656f1**. The old ninth parent and original root values are NOT recopied. Exact SHA/length, source word syntax/finiteness, 68/60 arm counts and all independent previous ninth parent result bits are validated. Optional complete original owner JSON checks exact original byte SHA/length, provenance, four original shapes, source exclusion, false gates and all 384 actual new values:

    python3 tools/worldgen_26_2_stock_finaldensity_tenth_layer_fixture.py \
      --capture /tmp/helve-26_2-final-tenth-layer-128.json

**Composed native finite parity with UNCHANGED 32-node scratch cap:** the existing source-observed **32-node ninth partial finalDensity** Rust test graph is preserved, along with all seventh/eighth/ninth and lower regressions. Instead of adding three source-unresolved children plus the RangeChoice operation above 32, a separate **four-node cold-validated local test stage** evaluates the original tenth Marker selector and both independently original Java Ap2 child values; the three child raw words are still JVM-fed. Its computed IEEE output is the single input to the unchanged ninth 32-node native test graph. Tests independently assert 128/128 tenth stage -> frozen ninth result, 68 in/60 out, the non-alias witness and 128/128 exact final MIN-root parity through the **4+32 two-stage composition**. This does not create a production scheduler, increase any stage's HOT scratch, make a throughput claim, source-admit either Ap2 or establish Marker lifecycle semantics.

**Next genuine eleventh source frontier, NOT executed:** inspect the two actual in/out Ap2 branch operator types, each of their two independent child class records and sampled values, and separately the Marker enum and its true wrapped child. Only real source-grounded sharing or bounded composition can justify further native lowering. Entire seeded Noise constructor/router, actual NoiseChunk marker/cache/interpolator lifecycle, VAR/SEM and production world-publishing gates remain false despite finite-sample parity.


## Eleventh source-only Marker/Ap2 operator-record probe staged (22 October 2026; genuine JVM execution pending)

**PR #502 has merged all eight checks GREEN**, squash SHA **8c0456782c6c2fc60ad3cf2e54bd7c86e91fbf52**. Authentic completed tenth original-stock 26.2 report **45,434 bytes**, SHA **b5bed75d54e2704718af4795407614ebd591330cb714263e61e6d7a21e8c3e8e**; new-only committed three-child original IEEE fixture **6,528 bytes**, SHA **5786ee42753215750163ec740220082b941e9d34adb76d145bfd43c21f9656f1**. Previous root through ninth, 128 frozen tenth branch samples, all 512-cell/NoiseChunk data are immutable and are NOT to be recaptured. Two-stage candidate **4-node tenth RangeChoice + 32-node ninth partial finalDensity** matches all 128 source-owned stock MIN outputs while retaining existing per-stage scratch limit. This is only independently frozen finite SinglePointContext parity, not genuine seeded NoiseChunk source admission.

The eleventh Java bridge prepares ONLY the narrow frontier exposed by the actual tenth original JVM shape: source-owned **DensityFunctions$Marker** selector and TWO separate original **DensityFunctions$Ap2** in/out branches, not presumed identical to each other or other known Ap2. The first bounded 32-coordinate seed record reflects:
- Original Marker enum declaring class, exact enum constant (actual marker lifecycle name), and runtime class of its sole actual density child.
- Exact in-range Ap2 enum declaring class and operation plus independently reflected original runtime classes of argument1/argument2.
- Exact out-of-range Ap2 enum declaring class and operation plus independently reflected original runtime classes of argument1/argument2.
- Five genuinely NEW numeric observations per original XYZ: Marker wrapped child's finite raw IEEE value and four separate in/out Ap2 actual child operands. The three **old** original tenth values — Marker selector, in-range Ap2 result and out-of-range Ap2 result — are independently recomputed ONLY as SHA-pinned 128×3 prior-boundary checks, never copied to any new permanent fixture.

Source-only transport tools: **tools/worldgen_java/HelveStockFinalDensityEleventhLayer262.java**, **tools/worldgen_26_2_stock_final_density_eleventh_layer.py**, with bounded four-seed synthetic frame/JDK compilation and fail-closed mutation tests. The original archive, official 26.2 JAR, prior tenth report/fixture SHA and actual indexed source-method hashes must agree; output is source-free and finite, has exact four seed-invariant 32-row graph shapes and unchanged strict no-source/VAR-SEM/production/NoiseChunk/all-input admission gates. Candidate Marker-child numeric equality on SinglePointContext is diagnostic telemetry ONLY; there is no unconditional source-law or actual NoiseChunk cache/interpolator qualification, and the two Ap2 operation semantics remain separately unadmitted.

**After the eleventh diagnostic PR is GREEN and merged, run ONLY this new original private owner capture**:

    cd ~/Crucible
    git switch main
    git pull --ff-only

    python3 tools/worldgen_26_2_stock_final_density_eleventh_layer.py \
      --source "$HOME/Documents/mc-source/mc-src.zip" \
      --db .crucible/vanilla/atlas.sqlite \
      --lock vanilla/vanilla.lock.toml \
      --output /tmp/helve-26_2-final-eleventh-layer-128.json

Upload source-free eleventh JSON or exact bounded HELVE26_2_ELEVENTH_FAILURE|phase|ExceptionClass. Do not execute any prior eighth, ninth, tenth or older original oracle. Upon successful true-source evidence, explore independent fixed-cap composed Rust stages with exact signed-zero-aware Ap2 operators; do not fabricate node sharing or exceed fixed per-stage HOT scratch.

## ACTUAL eleventh original-JVM source receipt — completed and reviewed (22 October 2026)

**This update supersedes the earlier section that described the eleventh owner capture as still pending.** PR #503 https://github.com/JamieLittle16/Helve/pull/503 is **MERGED**, three required CI checks green. Verified main head before this docs PR: **770d3497cb295484fa47e4feeeccaaf37c1303df**. The original Java 26.2 private source-owner eleventh observer has ALREADY RUN and its source-free JSON was uploaded: **71,499 bytes, SHA-256 a9d39854865d84bc8bdc2cf061ff715a589101af57c842dc159c2754cc71c6cc**. DO NOT re-run eleventh or any earlier original JVM capture.

Genuine seed-invariant source shape, four seed groups × 32 fixed pinned XYZ in DensityFunction$SinglePointContext:

- Selector Marker(enum class DensityFunctions$Marker$Type, type **CacheOnce**) wraps an actual **HolderHolder** density child.
- In-range Ap2 (enum class DensityFunctions$TwoArgumentSimpleFunction$Type, actual operation **MIN**) has children **Marker** and **MulOrAdd**, independently original-JVM evaluated.
- Out-of-range Ap2 (same enum declaring class, operation **MAX**) has children **Ap2** and **RangeChoice**, independently original-JVM evaluated.
- Five NEW genuine IEEE-754 sample words per point: marker_child_bits, in_left_bits, in_right_bits, out_left_bits, out_right_bits. Three OLD parent anchors per point: old_marker_bits, old_when_in_bits, old_when_out_bits; **never recopy these old parents into the new fixture**.
- Exactly **128/128** rawbit equality between CacheOnce Marker and its wrapped Holder child at these finite SinglePointContext samples. In-branch MIN reproduces original in parent **128/128**, selecting left **68** samples and right **60**. Out-branch MAX reproduces original out parent **128/128**, selecting left **127** times and right **once**. These finite telemetry checks do NOT source-admit CacheOnce caching/lifecycle or arbitrary-input MIN/MAX.
- Rare out-right-branch winner at **global row 110**, last seed 0xf0e1d2c3b4a59687, XYZ **(-17, 65, -17)**: real MAX left bits **3fde51afdb79aeec**, right bits **3fdf83606ba08263**, original selected MAX result **3fdf83606ba08263**. Out-right input is -1_000_000.0 in **125/128**, but has three nonconstant original JVM values at **rows 19, 109, 110**. Never simplify this RangeChoice child to a literal -1 million or alias MAX output to the left input.
- Marker candidate telemetry reports zero discrepancies and **source_law_admitted=false**. Every other actual source-law, NoiseChunk lifecycle, VAR/SEM, full router and production worldgen qualification/admission flag remains **FALSE**.

**Crucial independently verified old-oracle identity:** Reassemble all **384** previous tenth parent IEEE raw words from this new eleventh JSON in the exact order old_marker_bits, old_when_in_bits, old_when_out_bits; lowercase 16 hex digits each, three tab-separated words then LF, 128 lines. Byte size **6,528** and SHA-256 **5786ee42753215750163ec740220082b941e9d34adb76d145bfd43c21f9656f1**, exactly matching the previously merged immutable tenth fixture; no old capture needs repeating. Prior genuine tenth source-owner report SHA **b5bed75d54e2704718af4795407614ebd591330cb714263e61e6d7a21e8c3e8e**. Original ZIP/JAR/method/body pins and all four seed-original shapes in the JSON are unchanged; no source text included.

**Next concrete PR work, NOT YET COMPLETED:** freeze ONLY the 5 NEW eleventh rawbit words per point in crates/world/helve-world-gen/tests/data/stock_finaldensity_eleventh_layer_new_128_rawbits.tsv, exact **128×5 words, 10,880 bytes**, precomputed SHA-256 **f2d4b9084f30aa5f277053f9513c7529c321648d491b21b77e12bfd24b960e99**. Add Python strict fixture/provenance/optional original JSON receipt verifier and adversarial mutation tests. Extend the existing test-only Rust ninth 32-node plus tenth 4-node staged composition with native **explicit MIN and MAX** fixed-cap stages fed from new source-owned Java child outputs, verifying old tenth parent rawbits 128/128 each and original stock finalDensity MIN root 128/128; guard rare MAX right-win at row 110 and previously frozen tenth in-range selector≠branch witness. Do not increase per-stage HOT scratch, allocate on HOT path, claim unconditional Java source equivalence, infer real NoiseChunk marker cache/interpolator semantics or admit native production.

**After the above exact source-honest PR passes CI green and merges**, plan only ONE narrow real twelfth original owner frontier, chosen among still-unresolved in-right MulOrAdd, out-left Ap2, out-right RangeChoice, and independent Marker/Holder ownership. No shotgun source probing. The next fresh context should use the uploaded eleventh report and the 22 October handoff, and should start with **fixture freeze / native eleventh finite parity**, NOT another original-JVM capture.


## Eleventh compact original-JVM fixture and bounded source-observed native parity (22 October 2026)

This section supersedes the preceding *fixture still pending* paragraph. The already
completed **original 26.2 eleventh source-owner report is reused, NOT recaptured**:
**71,499 bytes, SHA-256 a9d39854865d84bc8bdc2cf061ff715a589101af57c842dc159c2754cc71c6cc**.
The prior independently committed tenth fixture is unchanged: **6,528 bytes,
SHA-256 5786ee42753215750163ec740220082b941e9d34adb76d145bfd43c21f9656f1**.
Exactly **384/384 old tenth parent words** reconstructed from the genuine eleventh
report match that earlier three-column tenth fixture.

New source-free immutable *eleventh-only* fixture:
`crates/world/helve-world-gen/tests/data/stock_finaldensity_eleventh_layer_new_128_rawbits.tsv`.
It contains exactly **128 × 5 = 640 new original JVM IEEE-754 direct-child words**
(`marker_child_bits`, `in_left_bits`, `in_right_bits`, `out_left_bits`,
`out_right_bits`), **10,880 bytes**, SHA-256
**f2d4b9084f30aa5f277053f9513c7529c321648d491b21b77e12bfd24b960e99**.
It contains no duplicated old selector, Ap2 parent, ninth choice or original root
result words, private source text, raw registry contents, or JVM stack traces.

The fail-closed source-only fixture checker is
`tools/worldgen_26_2_stock_finaldensity_eleventh_layer_fixture.py`.
Its exact-size/SHA/type/finite/4×32/shape/parent checks use the immutable prior
tenth TSV, and the optional `--capture` checks the completed private JSON's
original exact byte SHA, source/JAR/method owner pins, fixed coordinates/seeds,
all-false source and production gates, source text exclusion, original shape
and candidate telemetry, and all 640+384 rawbit words. Tampering with a selected
MIN parent, with the genuine rare MAX right winner, or the source owner fails
closed. Run only against an **already captured** original JSON (do not recapture):

    python3 tools/worldgen_26_2_stock_finaldensity_eleventh_layer_fixture.py \
      --capture /tmp/helve-26_2-final-eleventh-layer-128.json

The test-only Rust staged candidate retains the pre-existing **32-node**
backward-only ninth graph and the **4-node** tenth `RangeChoice` stage unchanged.
Two additional separately cold-validated **3-node** actual `ExplicitAp2Min` and
`ExplicitAp2Max` local stages consume four original-JVM eleventh child operands;
the genuine `CacheOnce` `Marker→HolderHolder` child is tested as a *bounded
finite numerical forwarding observation* only, never simulated as a
`NoiseChunk` cache lifecycle law. Independent old tenth Marker, MIN and MAX
parents are asserted bitwise **128/128 each**; the existing 68/60 tenth range
choice and genuine selector-not-in-branch witness are retained. The actual
MIN picks left/right **68/60**, actual MAX picks left/right **127/1** and the
right-hand real `RangeChoice` takes a nonconstant value at rows **19,109,110**.
Row **110** is an explicit right-wins regression. This feeds existing tenth
choice and ninth graph against the *independently frozen original stock Java*
`finalDensity` MIN root **128/128**. The per-stage HOT scratch ceiling
**remains 32 nodes**; no production HOT executor or orchestration is modified.

**Critical scope:** finite original `SinglePointContext` arithmetic and
candidate parity ONLY, not all-input Java `Ap2` semantics, exact signed-zero
proofs for new inputs, general `CacheOnce` identity/lifecycle, stock
`NoiseChunk` interpolation, seeded native full graph generation, VAR/SEM or
production admission. Existing source-fidelity and throughput obligations
remain OPEN and all reported qualification booleans stay FALSE. The next
narrow source-owned frontier, only if necessary, is the actual in-right
`MulOrAdd`, out-left `Ap2`, out-right `RangeChoice` and independent
Marker/Holder ownership. Original captures through layer eleven are complete
and **must not be replayed**.

## Selected-path accounting and twelfth narrow original Ap2 frontier (22 October 2026; JVM execution PENDING)

After #506 merged green, the existing authentic eleventh original-JVM report was
analysed **without recapture** for *two successive branch selectors*. The naive
"MIN chooses right 60 of 128" statistic is **not the selected parent contribution**:
the outer tenth `RangeChoice` chooses in-range MIN on 68/128 points and
out-of-range MAX on 60/128. For the **actual selected path**, the exact
intersection with independently observed eleventh child comparisons is:

| Actual frozen tenth choice and eleventh selected child | Samples |
| --- | ---: |
| tenth in-range, eleventh MIN left `Marker` | 67 |
| tenth in-range, eleventh MIN right `MulOrAdd` | 1 |
| tenth out-of-range, eleventh MAX left `Ap2` | **60** |
| tenth out-of-range, eleventh MAX right `RangeChoice` | 0 |

**Second independent final-root boundary:** comparing the frozen **three-column
original stock MIN-root** TSV, root MIN chooses its left result **124/128**
and its right result **4/128**, without ties. Intersecting that with the
above true tenth-choice and eleventh MIN/MAX choices leaves the actual
out-left `Ap2` on **57** selected root-left paths, while the
in-right `MulOrAdd` occurs on **zero** selected root-left paths.
The remaining three of 60 selected out-left results are masked by the
root MIN right side in these samples. These are observed control-flow
intersections, not proof of nonzero numerical sensitivity or arbitrary-
coordinate dead code. A separate source-free Python regression now anchors
all counts to BOTH the immutable eleventh/tenth fixtures and the original
root MIN fixture.

The authentic isolated MAX right-wins witness at original row 110 remains
**real and important for branch fidelity**, but the *tenth outer selector
chooses in-range* at row 110, so it is not an executed right MAX branch in
these 128 original `SinglePointContext` points. This is finite source
evidence, NOT Java-wide dead-code elimination, object sharing, general lazy
evaluation qualification or authorization to remove any branch.

**Therefore the next highest-leverage source-owned edge is out-of-range
MAX's actual left `DensityFunctions$Ap2`**, not the in-range MIN's right
`MulOrAdd`. The briefly opened in-right twelfth proposal #507 was
**closed unmerged without an original JVM capture**, precisely to avoid a
low-yield probe; do not rerun or reintroduce it unless later evidence gives
an independent reason.

**Twelfth bounded source-only observer (staged, NOT original-JVM executed):**
`tools/worldgen_java/HelveStockFinalDensityTwelfthLayer262.java`,
`tools/worldgen_26_2_stock_final_density_twelfth_layer.py`, and
`tools/tests/test_worldgen_26_2_stock_final_density_twelfth_layer.py`.
Only the *actual eleventh out-left Ap2* is descended:

- Reflect the original `TwoArgumentSimpleFunction$Type` declaring class
  and actual `ADD`/`MUL`/`MIN`/`MAX` enum, with **two independently
  original runtime child classes**.
- For exactly four existing seeds × 32 existing XYZ, observe **two genuinely
  new IEEE-754 operand words each**. The old original eleventh
  `out_left_bits` (column four of the previously frozen five-field eleventh
  TSV) is observed only as a **128/128 independent bitwise parent anchor**
  and must never be recopied into a permanent twelfth fixture.
- Require four seed-invariant source shape records, source ZIP and stock
  JAR SHA, existing indexed source method body hashes, the immutable
  original eleventh report SHA
  `a9d39854865d84bc8bdc2cf061ff715a589101af57c842dc159c2754cc71c6cc`,
  and eleventh new-only fixture SHA
  `f2d4b9084f30aa5f277053f9513c7529c321648d491b21b77e12bfd24b960e99`.
  Only bounded, source-free, exact pinned `SinglePointContext` IEEE
  frames are allowed; all source-law, cache/interpolator, fully native,
  VAR/SEM and production flags remain **FALSE**.
- Arithmetic comparison from actual operands against original Ap2 parent
  bits is a **diagnostic candidate only**. Preserve any mismatch, signed
  zero or special Java `Ap2` early-exit; neither a guessed operation nor
  finite numbers can justify source-law admission or changing JVM evidence.
- Native ninth 32-node scratch, staged eleventh 3+3+4+32 finite parity and
  all prior oracle fixtures remain **untouched**. Synthetic tests and JDK
  compilation qualify this *source-free observer*, not the original Java
  result or seeded worldgen.

After this twelfth observer passes all CI checks and merges, run **ONLY this
one new original-JVM capture**, against the same private pinned original
source owner. Do NOT repeat captures one through eleven:

    cd ~/Crucible
    git switch main
    git pull --ff-only
    python3 tools/worldgen_26_2_stock_final_density_twelfth_layer.py \
      --source "$HOME/Documents/mc-source/mc-src.zip" \
      --db .crucible/vanilla/atlas.sqlite \
      --lock vanilla/vanilla.lock.toml \
      --output /tmp/helve-26_2-final-twelfth-layer-128.json

Upload only the NEW source-free JSON or bounded
`HELVE26_2_TWELFTH_FAILURE|phase|ExceptionClass` marker.
Once authentic twelfth evidence exists, freeze **only 128×2 new operand
rawbit words**, SHA-pin the original report and parent fixture, and compose
a test-only native explicit Ap2 local stage into the existing MAX,
tenth `RangeChoice`, ninth 32-node original MIN-root parity. Maintain
per-stage ≤32-node scratch, no new HOT allocations, no production
worldgen or stock `NoiseChunk` lifecycle claim.
