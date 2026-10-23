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

## Twelfth genuine original-JVM out-left Ap2(MIN) and staged native parity (22 October 2026)

**Original owner has run; DO NOT run it again.** The genuine completed
26.2 source-only report is **39,658 bytes**, SHA-256
**041eadc4a4174b4bace6eed2270c129cad6c65fe06cdbd7396268216bf26ab26**.
It was captured by the merged original twelfth owner from #508 at the
unchanged 4 world seeds × 32 SinglePointContext XYZ, against the pinned
original 26.2 source ZIP/JAR and indexed Java method-body checksum
inventory. No source text, private trace or registry dump was exported.

**Actual new original source record:** the eleventh out-of-range
Ap2(MAX) **left** operand is genuinely **Ap2(MIN)**, with two independent
class-observed DensityFunctions$Ap2 children. Its enum owner is
DensityFunctions$TwoArgumentSimpleFunction$Type, and all four seeded
record shapes agree. No operator or class was inferred from a numeric
coincidence. Both actual child IEEE words are finite at all 128 original
contexts, without any observed signed-zero/tie sample.

Direct numerical MIN on each pair of genuine original child words
reproduces the independently frozen old eleventh out-left parent rawbits
**128/128**. The actual child selection is **125 left, 3 right**;
the three rare genuine right winners are at **rows 21, 97, 106**.
The source-only original report records zero direct arithmetic candidate
mismatches, but retains source_law_admitted=false and every other
original source, NoiseChunk, VAR/SEM, fully seeded and production gate
**FALSE**.

New immutable **twelfth-new-only** fixture:
crates/world/helve-world-gen/tests/data/stock_finaldensity_twelfth_outleft_ap2_children_128_rawbits.tsv.
Exactly **128 × 2 = 256 NEW original IEEE words**, columns
(ap2_left_bits, ap2_right_bits), **4,352 bytes**, SHA-256
**c51d0c1686a5a7160abb2f03c6db5e377b6a2f6fee23cc18bca7a493439b552f**.
It contains NO old parent, previous tenth branch/selector or original
root words; all parent comparisons load the previously merged and
SHA-pinned eleventh new-only fixture separately. No earlier capture,
fixture or test oracle is rewritten.

Source-only fail-closed verifier:
tools/worldgen_26_2_stock_finaldensity_twelfth_layer_fixture.py,
with adversarial mutation tests at
tools/tests/test_worldgen_26_2_stock_finaldensity_twelfth_layer_fixture.py.
The optional --capture verifies the **already generated** private JSON's
exact complete SHA, length, original owner provenance/method record and
all-false gates; this command does NOT rerun original Java:

    python3 tools/worldgen_26_2_stock_finaldensity_twelfth_layer_fixture.py \
      --capture /tmp/helve-26_2-final-twelfth-layer-128.json

The existing test-only Rust stock_finaldensity_eighth_layer_262.rs now
adds separately cold-validated **3-node explicit Ap2(MIN)** arithmetic
fed by the genuinely new child words, validating the old eleventh
MAX-left parent 128/128 and all three right-winning witnesses.
That output feeds the existing eleventh 3-node MAX (plus the
independent eleventh 3-node MIN), tenth 4-node RangeChoice,
and ninth **32-node fixed** original root graph. The previously frozen
stock Java finalDensity MIN root remains **128/128 raw-bit parity**.
Per-stage scratch ceilings are **3, 3, 3, 4, 32**, maximum **32**;
no new HOT allocations, production scheduler or worldgen authority.

**Critical unqualified boundary:** only the original finite
4×32 SinglePointContext candidates are parity tested. The two
actual twelfth Ap2 children are STILL numerically supplied by the
original JVM. This does NOT prove all-input Java Ap2 NaN or signed-zero
semantics, general marker/Holder/NoiseChunk lifecycle, native seeded
noise sources, VAR/SEM, full graph worldgen, or production admission.

**Potential next narrow source-owned frontier:** independently observe
the actual operation and immediate children of the two twelfth Ap2
nodes, prioritized by which contributes to the root's selected path.
Do not guess their operators, expand HOT scratch, repeat any previous
source capture (layers one through twelve), or silently admit source
laws from finite agreement.

## Thirteenth original source-owner frontier — selected twelfth MIN-left Ap2 (22 October 2026, JVM execution PENDING)

Prior **twelfth** original JVM evidence and staged native parity are already
merged (#509) and **MUST NOT be recaptured or duplicated**. The original
twelfth report remains exactly 39,658 bytes, SHA-256
**041eadc4a4174b4bace6eed2270c129cad6c65fe06cdbd7396268216bf26ab26**.
The immutable genuine twelfth-only two-child TSV remains 4,352 bytes,
SHA-256 **c51d0c1686a5a7160abb2f03c6db5e377b6a2f6fee23cc18bca7a493439b552f**.
Existing eleventh/tenth/ninth stock captures and fixture hashes remain untouched.

**Control-flow priority audit against independently frozen Java fixtures:** the
twelfth out-left Ap2(MIN) picks its left immediate Ap2 result 125/128 and its
right Ap2 result 3/128 (right-wins original rows **21, 97, 106**).
The selected tenth branch is in-range 68/128 and out-of-range 60/128;
out-of-range MAX takes that twelfth MIN in all 60 out-of-range sample
results. However, original stock finalDensity root MIN selects its *left*
result only at 124/128. On the actual original selected ROOT path, the
twelfth Ap2(MIN) **left** child therefore contributes at **55/128**
samples; the twelfth MIN **right** child contributes at **2/128**
(rows **97, 106**). The third local right-wins row **21** is masked by
root MIN's other side on that sample.

These intersections are **only finite evidence of selection**; they
do not prove call execution (stock Java may evaluate operands even
when ultimately masked), computational sensitivity, dead branches on
arbitrary coordinates, object identity, or admissible optimizations
to source-observed graph topology.

**Therefore** the thirteenth observer descends into **ONLY the actual
twelfth Ap2(MIN) left child**. Both twelfth siblings were original-JVM
class-observed as Ap2, but their internal enum operations and immediate
child classes are **not yet known**. The new source-only Java bridge
`tools/worldgen_java/HelveStockFinalDensityThirteenthLayer262.java`
records its actual original Java TwoArgumentSimpleFunction Type enum,
actual ADD/MUL/MIN/MAX operation, two immediate child runtime classes,
and **two new original IEEE child words** per same fixed four seeds ×
32 SinglePointContext XYZ. It recomputes the original twelfth MIN-left
parent **only** to compare 128/128 exact raw words against **column one**
of the immutable twelfth TSV, NOT to write a duplicated parent fixture.

The new bounded source-free observer is
`tools/worldgen_26_2_stock_final_density_thirteenth_layer.py`
and its adversarial regression tests are in
`tools/tests/test_worldgen_26_2_stock_final_density_thirteenth_layer.py`.
It strictly preserves original 26.2 source ZIP/JAR and three indexed
Java method-body owner pins, frozen prior twelfth report/fixture SHAs,
4 identical original seeded records, no source text/trace/registry
export, exactly 128 finite ordered original child pairs with 128
independent old-parent anchors, and **all** previous source-law,
NoiseChunk, seeded worldgen, VAR/SEM, and production flags **FALSE**.
Synthetic transport/Java compilation CI is NOT genuine original
runtime evidence and may never auto-admit an operator law.

**Original thirteenth JVM probe has NOT YET RUN.** Only after the
observer PR's required checks are green and merged should the
private source owner run this **ONE NEW** thirteenth capture:

    cd ~/Crucible
    git switch main
    git pull --ff-only
    python3 tools/worldgen_26_2_stock_final_density_thirteenth_layer.py \
      --source "$HOME/Documents/mc-source/mc-src.zip" \
      --db .crucible/vanilla/atlas.sqlite \
      --lock vanilla/vanilla.lock.toml \
      --output /tmp/helve-26_2-final-thirteenth-layer-128.json

Upload the NEW source-free thirteenth JSON or bounded
`HELVE26_2_THIRTEENTH_FAILURE|phase|ExceptionClass` marker.
Do not repeat captures 1–12. After genuine thirteenth report validation,
freeze only **128×2 new** original child rawbit words, SHA-pin the
private thirteenth report and fixture, and add one test-only source-
observed native operator stage feeding the twelfth MIN, eleventh MAX,
tenth RangeChoice, and ninth fixed 32-node root parity.

**Constraints remain absolute:** each stage cold-validated separately,
HOT scratch ≤32 nodes, no HOT allocations, new performance claims,
Java all-input operator / signed-zero / NaN semantics admission,
stock NoiseChunk lifecycle qualification, native fully seeded worldgen,
source VAR/SEM gates or production publication authority.

## Thirteenth actual original-JVM MIN fixture and native bounded parity (22 October 2026)

**The original thirteenth JVM observer (#510) HAS NOW RUN. Do not recapture
it or any prior layers 1–12.** The original source-free thirteenth
JSON has exactly **41,610 bytes**, SHA-256
**e50e4ef14a7d3716613e0bb77982a5693c0395ac1f32e24325930dbf0c8d79db**.
The four seed records independently identify the twelfth MIN-left
child as an actual original Minecraft 26.2
`DensityFunctions$Ap2(MIN)` whose two direct classes are a LEFT
`DensityFunctions$Ap2` and RIGHT
`DensityFunctions$HolderHolder` (enum owner
`DensityFunctions$TwoArgumentSimpleFunction$Type`).
The unchanged original 26.2 source-method hashes/source ZIP and
official server SHA remain pinned in the capture. No source text,
stack trace, original Java jar, old fixture values or private indexed
database has been committed.

Exactly **128×2 genuine new** raw IEEE-754 operands were emitted
over the *same* fixed original 4×32 SinglePointContext coordinates.
Original Java's two operands agree with the independently pinned
**twelfth LEFT operand** at **128/128 bit-exact** values when the
direct MIN candidate is selected. No NaN, nonfinite, signed-zero
tie, or arithmetic candidate mismatch was observed. True thirteenth
MIN selection is **12 left** and **116 right**. The exact sampled left
winners are **[0, 1, 9, 10, 11, 12, 31, 32, 41, 53, 62, 117]**.
Intersecting with original independent Java tenth RangeChoice,
eleventh MAX, twelfth MIN and final root MIN results, only
**12 left** and **43 right** thirteenth child values lie on the
selected original root path (55 total). The observed right
`HolderHolder` is thus the higher-impact FOURTEENTH review target,
not a reason to presume it forwards without a real source record.

Immutable genuine new-only source-free fixture:
`crates/world/helve-world-gen/tests/data/stock_finaldensity_thirteenth_selected_left_ap2_children_128_rawbits.tsv`.
It contains EXACTLY **128×2 = 256 new original IEEE words**,
only (`left_ap2_left_bits`, `left_ap2_right_bits`), in this order.
The fixture is **4,352 bytes**, SHA-256
**cd8ba322bea4575aba70a28223940162af7feed926806a96c217d7a4b04eee4a**.
NO prior twelfth parent values, old tenth RangeChoice / eleventh
MAX inputs, ninth graph parent or old final root are copied into it.
The old twelfth child pair fixture remains untouched at 4,352
bytes, SHA-256
**c51d0c1686a5a7160abb2f03c6db5e377b6a2f6fee23cc18bca7a493439b552f**.

Strict fail-closed fixture/provenance validator:
`tools/worldgen_26_2_stock_finaldensity_thirteenth_layer_fixture.py`,
with adversarial SHA, structure, ordering, source-provenance,
branch witness, old-parent bit, NaN and signed-zero/tie mutation
tests in `tools/tests/test_worldgen_26_2_stock_finaldensity_thirteenth_layer_fixture.py`.
It requires the exact original private report full length and SHA,
actual four seed class/operation records and original Java
unadmitted telemetry, and the full prior source-method inventory.
The original report is not part of git. To verify an existing local
original report **without re-running any source capture**:

    python3 tools/worldgen_26_2_stock_finaldensity_thirteenth_layer_fixture.py \
      --capture /tmp/helve-26_2-final-thirteenth-layer-128.json

The existing test-only
`crates/world/helve-world-gen/tests/stock_finaldensity_eighth_layer_262.rs`
adds a separately cold-validated three-node
`ExplicitAp2Min` sample stage with the **two NEW original JVM
thirteenth child bits**, verifying 128/128 original twelfth MIN-left
parents. Its computed value, not the old twelfth parent fixture,
feeds twelfth Ap2(MIN), eleventh Ap2(MAX) plus in-range MIN,
tenth RangeChoice and ninth fixed 32-node final-density MIN graph.
The independent original stock MIN-root results remain **128/128
IEEE rawbit parity** after full composition.

The distinct test-only stage scratch bounds remain
**3 + 3 + 3 + 3 + 4 + 32, with per-stage HOT maximum 32 nodes**.
Do not replace separate cold-validated stages with an unbounded
production DAG or allocate on the HOT sampling path.

**Limits: all observed results are only finite sample-level
SinglePointContext parity.** No arbitrary-input Java operation law,
NaN/signed-zero/short-circuit behaviour, `HolderHolder` target
forwarding, marker cache semantics, NoiseChunk lifecycle,
seeded native noise ownership, independent VAR/SEM, full router
qualification or production worldgen is newly admitted. Every
source-law and production admission flag in the authentic report
was **FALSE** and must remain false in the fixture and tests.

**Next only if source-weighted:** inspect the original right
`HolderHolder` record beneath the thirteenth MIN (43 selected
root paths), obtaining its underlying original target type and
finite values without assuming identity/alias or doing a redundant
prior JVM capture. Prioritize review of actual target source
identity and lifecycle before calling any holder numerical
coincidence a native source law.


## Fourteenth genuine MIN-right Holder target frontier — source-only owner prepared (22 October 2026)

**Prior original captures 1–13 are finished. Do not re-run any previous capture.**
PR #511 merged the original thirteenth **Ap2(MIN)** evidence (original private
report **41,610 bytes**, SHA-256
**e50e4ef14a7d3716613e0bb77982a5693c0395ac1f32e24325930dbf0c8d79db**).
The immutable 128×2 **thirteenth-new-only** fixture is 4,352 bytes,
SHA-256 **cd8ba322bea4575aba70a28223940162af7feed926806a96c217d7a4b04eee4a**.
It must not be rewritten or its old parent duplicated. The thirteenth
MIN's RIGHT original child is an independently class-observed
`DensityFunctions$HolderHolder`, selected by its local MIN **116/128**
times and contributing to **43/128** final-root selected paths. The
LEFT local child is an actual distinct `DensityFunctions$Ap2`,
selected 12 times, contributing 12 final-root selected paths.
This is a source-weighted investigative priority, **not** proof of
dead branches, call-path execution, Holder forwarding or Java all-input law.

The **fourteenth only** original-JVM frontier is the previously unseen
target of that exact right `HolderHolder` child of the actual
thirteenth `Ap2(MIN)`, itself the LEFT child of the twelfth
`Ap2(MIN)` under the eleventh outside `Ap2(MAX)`.
New Java:
`tools/worldgen_java/HelveStockFinalDensityFourteenthLayer262.java`.
It strictly retraces real runtime record edges and verifies both known
twelfth and thirteenth MIN enums and the genuine thirteenth immediate
children's actual classes; it then calls the existing source-reflective
`HelveStockFinalDensityRootSemantics262.holderTarget()` helper.
That helper explicitly requires the original `function` record
component to contain a `net.minecraft.core.Holder$Direct`, reads
its **actual** `value()` and requires a real
`DensityFunction` delegate. The diagnostic records *without
guessing* each original seed's actual Holder wrapper, Direct container,
and resolved delegate runtime class. A different real container or
graph aborts with a bounded source-only failure phase rather than
attempting to infer an equivalent numeric replacement.

Each of the SAME unchanged four world seeds × 32
`DensityFunction$SinglePointContext` XYZ yields **only ONE new
resolved target original-JVM rawbit word**, plus the original direct
Holder output solely to independently compare against **column two**
(`left_ap2_right_bits`) of the immutable thirteenth fixture.
The old Holder bits are NOT a new fixture and should never be
copied into any fourteenth-new-only TSV. Record validation requires
four seed-invariant genuine shape records, 128 finite ordered IEEE
pairs, strict original source ZIP/JAR/Atlas method provenance,
the exact prior thirteenth report/fixture checksums, and every
old/all-input/NoiseChunk/VAR-SEM/production source-law gate **FALSE**.

Source-free Python driver:
`tools/worldgen_26_2_stock_final_density_fourteenth_layer.py`;
adversarial transport/provenance/class/old-parent tests:
`tools/tests/test_worldgen_26_2_stock_final_density_fourteenth_layer.py`.
The synthetic JDK build merely establishes source-free Java compilation.
New `holder_forward_candidate_telemetry` records disagreement between
actual delegate and old Holder finite words, **without filtering genuine
Java observations** or turning equality into a forwarding source law.
Neither original Java source text, private registry values, JVM bytecode
nor original stack traces are exported. No Rust production code or HOT
scratch bound is changed in the observer PR.

**Real original fourteenth JVM has NOT RUN.** Only after green CI and
merging the observer PR should the local original-source owner run
ONE NEW source-only capture:

    cd ~/Crucible
    git switch main
    git pull --ff-only
    python3 tools/worldgen_26_2_stock_final_density_fourteenth_layer.py \
      --source "$HOME/Documents/mc-source/mc-src.zip" \
      --db .crucible/vanilla/atlas.sqlite \
      --lock vanilla/vanilla.lock.toml \
      --output /tmp/helve-26_2-final-fourteenth-layer-128.json

Upload only the NEW source-free JSON, or the bounded
`HELVE26_2_FOURTEENTH_FAILURE|phase|ExceptionClass` failure marker.
Never repeat captures 1–13. On genuine validated evidence, freeze
only any **genuinely new** direct target words if justified; if the
target equals the old Holder for every point, preserve the equality
receipt without duplicating prior words or claiming all-input
delegation. Use actual target class and source-record semantics
before planning a native primitive or subsequent original JVM probe.

**All source-law, all-input Holder forwarding, NaN/signed-zero,
cache/marker/NoiseChunk traversal, VAR/SEM, fully seeded native
worldgen, and production publication gates remain FALSE.**
The existing original 128/128 bounded finalDensity root parity
from the test-only native stages and immutable 32-node maximum
HOT scratch remain unchanged.


## Fourteenth original Marker receipt and fifteenth source-owner frontier (22 October 2026)

**The original fourteenth JVM capture is complete. DO NOT rerun layers 1–14.**
Original source-free fourteenth JSON is **36,371 bytes**, exact SHA-256
**8d258327bb24a5b8f6d6a3a64ad6ab751fd5dea7706b80ca88e42ca6a2b43492**.
The four independent world-seed records show exactly
`DensityFunctions$HolderHolder` → `net.minecraft.core.Holder$Direct` →
`DensityFunctions$Marker`, not a presumed gradient, noise, or other
delegate. Original provenance remains Minecraft Java **26.2**, protocol
776, DataVersion 4903, original ZIP SHA
**1e9bca3dff83cd83e7905f8810f1ec9899361fa2dc83fe893bb48beeb04df750**,
official server SHA **cdacdfb25898de5e4b4b0e5ddcc2722f77067e46605709c2d886c000ebb63ec5**,
and already pinned indexed Java method owners.

The original Holder's direct target value matches the original Holder
itself **128/128 exact raw IEEE words**, and BOTH match **column two**
of the independently frozen thirteenth fixture (4,352 bytes,
SHA-256 **cd8ba322bea4575aba70a28223940162af7feed926806a96c217d7a4b04eee4a**).
The original report's candidate telemetry is zero mismatches with
`source_law_admitted=false`. The fourteenth therefore contributes
**zero genuinely novel numerical words**. Do **NOT** create a
fourteenth TSV by repeating 128 existing thirteenth-right values.
The actual added evidence is the real original `Marker` source class,
a known genuine `Holder$Direct` container and bounded finite
numeric agreement; all-input Holder forwarding, Marker caching,
NoiseChunk lifecycle and production admission remain FALSE.

`tools/worldgen_26_2_stock_finaldensity_fourteenth_layer_receipt.py`
pins the **exact full private original report length/SHA**, all four
actual original runtime shape records, 128 independent thirteenth
old-parent comparisons, zero-mismatch telemetry and every all-false
qualification gate. It does **not** commit the original private JSON
or produce duplicate original numerical fixture values. Verify the
**existing**, already-completed original local report, without
re-running the Java observer:

    python3 tools/worldgen_26_2_stock_finaldensity_fourteenth_layer_receipt.py \
      --capture /tmp/helve-26_2-final-fourteenth-layer-128.json

The next bounded **FIFTEENTH** source-owning question is the real
`DensityFunctions$Marker` beneath this exact thirteenth-right
`HolderHolder`, with its actual original `DensityFunctions$Marker$Type`
enum and its **sole real immediate wrapped DensityFunction child**.
No operation or cached input may be guessed from older Marker nodes:
these are different source runtime objects. The new Java
`tools/worldgen_java/HelveStockFinalDensityFifteenthLayer262.java`
re-traces the established original twelfth MIN → thirteenth MIN →
right `HolderHolder` → `Holder$Direct` → fourteenth `Marker`
ancestry and checks the exact JVM enum class, enum value, and actual
child density runtime class. At the SAME original four world seeds
× 32 fixed `SinglePointContext` XYZ, it computes only **one NEW
original wrapped-child raw IEEE word**. The original Marker target
output and the old original Holder output are computed **only as
independent consistency anchors**; each MUST equal column two of
the frozen thirteenth TSV, previously independently validated by
the authentic fourteenth receipt. No old parent/target/root IEEE
values may enter a new permanent fifteenth-new-only fixture.

The source-free bounded Python observer is
`tools/worldgen_26_2_stock_final_density_fifteenth_layer.py`;
its source-free JDK build, adversarial frames/shape/methods/gates tests,
and fourteenth SHA/no-duplicate receipt tests live in
`tools/tests/test_worldgen_26_2_stock_final_density_fifteenth_layer.py`.
Record `marker_wrapped_candidate_telemetry` only as **finite numeric
evidence**, never a Java Marker cache/forwarding law. Original
method-body SHA/source ZIP, official server, original 4×32 XYZ,
thirteenth report/fixture, and fourteenth full report SHA remain
pinned. Synthetic tests are NOT genuine new original JVM evidence.

**FIFTEENTH original JVM has NOT RUN.** Only after the observer PR
passes all required green CI and merges, perform just this one new
original capture on the original-source local machine:

    cd ~/Crucible
    git switch main
    git pull --ff-only
    python3 tools/worldgen_26_2_stock_final_density_fifteenth_layer.py \
      --source "$HOME/Documents/mc-source/mc-src.zip" \
      --db .crucible/vanilla/atlas.sqlite \
      --lock vanilla/vanilla.lock.toml \
      --output /tmp/helve-26_2-final-fifteenth-layer-128.json

Upload only the NEW fifteenth source-free JSON or bounded
`HELVE26_2_FIFTEENTH_FAILURE|phase|ExceptionClass` marker.
**Do not repeat any of the first fourteen captures.**
After authentic evidence, compare the genuine Marker-wrapped values
to the frozen Holder parent; if they duplicate old values, preserve
the topology/verified equality receipt **without** a new TSV. If
distinct, freeze only genuinely NEW original child IEEE words.
No rust production source, HOT scratch, or earlier fixture changes
are included in the observer. Existing bounded original finalDensity
root parity 128/128 and max HOT 32-node budget remain unchanged,
as do all NoiseChunk, VAR/SEM, all-input and production gates **FALSE**.

## Fifteenth genuine CacheOnce/Ap2 receipt and sixteenth original-JVM frontier (22 October 2026)

**Fifteenth original capture COMPLETE. DO NOT repeat any original 1–15 captures.**
Actual original Minecraft Java 26.2 source-only JSON is **43,502 bytes**,
SHA-256 **bc1df68c3245c55735df84c4c2e36bc35b4d349d4a5c9623db24ac9630cbe0f0**.
Four independent seeded original runtime shapes identify the actual
'DensityFunctions$Marker$Type = CacheOnce' whose sole original wrapped
child is a real 'DensityFunctions$Ap2'. The direct source-owned path is:
thirteenth Ap2(MIN) RIGHT -> HolderHolder -> Holder$Direct ->
Marker(CacheOnce) -> Ap2. This contributes to **43 original root-selected
sample paths** out of the frozen 128. Do not infer all-input branch
selection or wrapper source semantics from these observations.

At the unchanged 4 seeds × 32 original SinglePointContext XYZ, the
direct actual Ap2 wrapped child, original Marker output, and original
Holder output agree **128/128 exact IEEE bits** with EACH OTHER and with
column TWO (RIGHT) of the independently frozen original thirteenth
2-column fixture, 4,352 bytes, SHA-256
**cd8ba322bea4575aba70a28223940162af7feed926806a96c217d7a4b04eee4a**.
The original report contains zero candidate mismatches and explicit
'source_law_admitted=false', and retains exact previous fourteenth
report SHA **8d258327bb24a5b8f6d6a3a64ad6ab751fd5dea7706b80ca88e42ca6a2b43492**,
the original thirteenth report SHA and original stock source ZIP/JAR
method-body identity pins. Fifteenth contributes exactly **zero
genuinely distinct numerical IEEE words**. There is deliberately
**NO fifteenth numerical TSV**; repeating old values would violate
new-only immutable fixture discipline.

New source-free receipt verifier:
'tools/worldgen_26_2_stock_finaldensity_fifteenth_layer_receipt.py'.
It checks the complete original private report length/SHA, all four
genuine CacheOnce -> Ap2 source-record shapes and 128 independent
old thirteenth-right equalities, preserving all false gates. To
check the already-created private report (WITHOUT rerunning Java):

    python3 tools/worldgen_26_2_stock_finaldensity_fifteenth_layer_receipt.py \
      --capture /tmp/helve-26_2-final-fifteenth-layer-128.json

**SIXTEENTH original-JVM owner is prepared but NOT RUN.** Follow ONLY
the actual fifteenth CacheOnce-wrapped Ap2 and inspect this Ap2's real
'TwoArgumentSimpleFunction$Type' enum and **two actual density children**.
Do not assume its operation (ADD/MUL/MIN/MAX) or class from other Ap2 nodes.
The Java bridge
'tools/worldgen_java/HelveStockFinalDensitySixteenthLayer262.java'
reflects actual original ancestry and emits exactly **TWO genuinely
new direct child IEEE words per point**, plus only ONE old Ap2 output
checked against the independently immutable thirteenth RIGHT column.
The source-only Python
'tools/worldgen_26_2_stock_final_density_sixteenth_layer.py'
pins exact stock source ZIP, official server JAR, indexed Java method
body identities, three prior original reports, thirteenth fixture,
all 4×32 XYZ records and all-false source-law/VAR-SEM/NoiseChunk/production
gates. Finite sample-only arithmetic candidate telemetry is not an
all-input Java source-law admission; observed mismatches are never
filtered. No old parent outputs are committed as a new numerical fixture.
Tests live at
'tools/tests/test_worldgen_26_2_stock_final_density_sixteenth_layer.py';
they cover source-free javac, fake records, prior immutable source
pins and admission flips.

The existing test-only full finalDensity original root parity is
**128/128 exact IEEE bits**. Separated cold-validated stages keep the
HOT scratch budget **at most 32 nodes**, without extra HOT allocations,
production chunk publication or NoiseChunk cache/lifecycle assumptions.

**After SIXTEENTH observer PR green CI and merge only**, run exactly
ONE new original source-owner diagnostic; do not repeat previous captures:

    cd ~/Crucible
    git switch main
    git pull --ff-only
    python3 tools/worldgen_26_2_stock_final_density_sixteenth_layer.py \
      --source "$HOME/Documents/mc-source/mc-src.zip" \
      --db .crucible/vanilla/atlas.sqlite \
      --lock vanilla/vanilla.lock.toml \
      --output /tmp/helve-26_2-final-sixteenth-layer-128.json

Upload the new source-free JSON or the bounded
'HELVE26_2_SIXTEENTH_FAILURE|phase|ExceptionClass' marker. Source review
and genuine operand bits must precede any test-only native lowering.
All-input and production admission flags remain FALSE.

## Sixteenth genuine CacheOnce-wrapped Ap2(MIN) new-only fixture and seventeenth frontier (22 October 2026)

**Original SIXTEENTH source-owned capture COMPLETE. DO NOT repeat original captures
1–16.** The authentic original Minecraft Java 26.2 stock registry and
4×32 SinglePointContext report is 41,479 bytes, exact SHA-256
**648f5636c00f88c964c5b847abc57227157c2d53955cee971af05519126dcb5e**.
Original source ZIP SHA-256:
**1e9bca3dff83cd83e7905f8810f1ec9899361fa2dc83fe893bb48beeb04df750**;
official server SHA-256:
**cdacdfb25898de5e4b4b0e5ddcc2722f77067e46605709c2d886c000ebb63ec5**.
The original sixteenth owner binds exact thirteenth/fourteenth/fifteenth
source-report SHA identities and original indexed source method digests.

All four original seeded runtime shapes are identical:
sixteenth genuine 'DensityFunctions$Ap2' enum 'MIN'; LEFT child actual
'DensityFunctions$Ap2'; RIGHT child actual 'DensityFunctions$Ap2'.
Ancestry: selected original thirteenth MIN RIGHT 'HolderHolder' ->
actual Holder$Direct -> actual 'Marker(CacheOnce)' -> actual sixteenth
'Ap2(MIN)' -> two actual Ap2 children. These are real original-JVM
class observations, not guessed from their finite sampled outputs.

**128/128 exact raw IEEE parent matches**: independent arithmetic MIN of the
actual two source-owned children reproduces the already immutable old
thirteenth RIGHT operand (source-observed Holder/CacheOnce/Ap2 parent)
at all 128 original points. Exact observed local winners:
LEFT **57/128**, RIGHT **71/128**, ties **0**; arithmetic candidate
mismatch count **0**, source-law admitted **FALSE**. Both operands have
distinct source identities and MUST both be preserved; do not confuse
these 57/71 local branch selections with final root-path coverage.
All-input operation laws, cache reuse, NoiseChunk lifecycle and seeded
production publication are NOT admitted.

Exactly **2 newly observed original child IEEE rawbit words/point (256 words)**
are frozen separately in the immutable new-only TSV
'crates/world/helve-world-gen/tests/data/stock_finaldensity_sixteenth_cacheonce_ap2_children_128_rawbits.tsv'.
Bytes **4,352**; exact SHA-256
**bd56e08412141819e938a0370b5375c458ff131d2cda12882826108b196b99d9**.
The **old** original parent is independently sourced ONLY from column TWO
(RIGHT) of the immutable thirteenth 128×2 new-only TSV
(SHA **cd8ba322bea4575aba70a28223940162af7feed926806a96c217d7a4b04eee4a**).
No older numerical values are committed again. The strict fixture validator
'tools/worldgen_26_2_stock_finaldensity_sixteenth_layer_fixture.py'
pins full original report SHA/bytes, 4 genuine seed-invariant runtime shapes,
original methods/seed/XYZ provenance, exact new-only fixture SHA and 128
independent original-right MIN output/equality checks. Strict synthetic
tests include wrong parent with checksum bypass, nonfinite, signed-zero tie,
fixture reorder and wrong source/provenance/gate mutations at
'tools/tests/test_worldgen_26_2_stock_finaldensity_sixteenth_layer_fixture.py'.
To verify the already-existing PRIVATE original sixteenth report, NO
original-JVM recapture required:

    python3 tools/worldgen_26_2_stock_finaldensity_sixteenth_layer_fixture.py \
      --capture /tmp/helve-26_2-final-sixteenth-layer-128.json

**Test-only native Rust parity now extends from the genuine source-owned
sixteenth MIN all the way to 128/128 original stock finalDensity roots.**
'crates/world/helve-world-gen/tests/stock_finaldensity_eighth_layer_262.rs'
adds an independent 3-node explicit MIN consuming actual sixteenth 2-word
operand fixture; asserts genuine sixteenth left/right MIN winner coverage
57/71 and independently old thirteenth RIGHT outputs 128/128. A separate
staged parity check composes actual newly CALCULATED sixteenth RIGHT into
the existing 13th MIN, 12th MIN, 11th MAX/MIN, 10th RangeChoice and 9th
root through to original 128 finalDensity stock roots; previously frozen
roots/parents and native stages stay independently owned. No enormous
monolithic graph, no runtime allocation, no change to max 32 HOT nodes,
no production worldgen and no all-input Marker/source law admission.

**Next original frontier: SEVENTEENTH, not run yet.** The genuine sixteenth
MIN RIGHT child is an actual 'DensityFunctions$Ap2', selected in 71 of 128
fixed sixteenth samples (more frequent than the 57 local left selections).
The source-only observer
'tools/worldgen_java/HelveStockFinalDensitySeventeenthLayer262.java'
retraces exact original ancestry, checks the sixteenth 'MIN' and Ap2/Ap2
class records, then reflects that actual RIGHT Ap2's OWN original enum
and its TWO immediate actual density child classes. It computes exactly
TWO NEW original child IEEE rawbit words per original 4×32 point, plus
ONE OLD right-Ap2 parent sample used ONLY for validation against column
TWO of the immutable sixteenth new-only TSV; no old words are refrozen.
'tools/worldgen_26_2_stock_final_density_seventeenth_layer.py' requires
the original thirteenth/fourteenth/fifteenth/sixteenth report and fixture
SHA pins, exact original source ZIP/JAR/methods and bounded seed/XYZ/finite
frames. Adversarial source-free transport/JDK compilation:
'tools/tests/test_worldgen_26_2_stock_final_density_seventeenth_layer.py'.
Sample arithmetic candidate telemetry does NOT admit all-input source
laws or filter true original JVM mismatches.

Only AFTER all required CI checks are green and this observer PR is
merged into main, run this SINGLE NEW original stock capture:

    cd ~/Crucible
    git switch main
    git pull --ff-only
    python3 tools/worldgen_26_2_stock_final_density_seventeenth_layer.py \
      --source "$HOME/Documents/mc-source/mc-src.zip" \
      --db .crucible/vanilla/atlas.sqlite \
      --lock vanilla/vanilla.lock.toml \
      --output /tmp/helve-26_2-final-seventeenth-layer-128.json

Upload only the source-free seventeenth JSON or bounded phase/error
marker. Original captures 1–16 do not need repeating. No stock
NoiseChunk interpolation, caching, other VAR/SEM admission or production
worldgen gates have been switched on.

## Seventeenth genuine ADD HolderHolder+Clamp and eighteenth source-owned Clamp frontier (22 October 2026)

**Original SEVENTEENTH completed. DO NOT recapture layers 1–17.**
Actual source-free original stock Minecraft Java **26.2**, protocol 776,
DataVersion 4903, four world seeds × 32 original SinglePointContext XYZ
JSON: **43,284 bytes**, exact SHA-256
**1c9fd95824aef71b68aaeb9c9528cb1adca174d6a258bc002989c3eb2fcac3c1**.
The original four original-JVM source runtime shapes agree:
sixteenth genuine Ap2(MIN) RIGHT child is an actual **Ap2(ADD)**,
LEFT actual **DensityFunctions$HolderHolder**, RIGHT actual
**DensityFunctions$Clamp**. This is not inferred from outputs or
assumed from another MIN/ADD. This local sixteenth MIN RIGHT branch won
**71/128** original MIN samples; the seventeenth ADD operand comparison
is **124 LEFT smaller, 4 RIGHT smaller, 0 equal** but **ADD does not
select either operand**, so 124/4 is NOT a MIN/branch win count.

Original source owner computes two immediate child IEEE words and one
OLD right-Ap2 output. Exact IEEE-754 ADD of the genuine HolderHolder
and Clamp original words reproduces **128/128** frozen sixteenth RIGHT
operand words, with **zero arithmetic candidate mismatches**. The
old parent is column TWO of the already immutable sixteenth 128x2 TSV
(SHA **bd56e08412141819e938a0370b5375c458ff131d2cda12882826108b196b99d9**).
The original report retains all independently pinned original thirteenth,
fourteenth, fifteenth and sixteenth reports, Java source ZIP/JAR/indexed
method SHA, genuine XYZ/world seeds and every all-input/cache/NoiseChunk/
VAR/SEM/production qualification gate **FALSE**. No source-law is
established from the 128 arithmetic matches.

Exactly **256 NEW original source-owned operand IEEE words** (128×2)
are frozen in the independent 4,352-byte fixture
'crates/world/helve-world-gen/tests/data/stock_finaldensity_seventeenth_minright_add_children_128_rawbits.tsv',
SHA-256 **ef9a7e19fc793ce4d33592756faa73a80d86ad59941ae171820b3ed8eb4263a5**.
There is no duplicate sixteenth old-parent column. New strict validator
'tools/worldgen_26_2_stock_finaldensity_seventeenth_layer_fixture.py'
verifies 17th original private report SHA/length, actual four source
class/enum shapes, full owner validator, all 128 new-only words against
the immutable seventeenth TSV, exact binary ADD against old sixteenth
RIGHT, and all original unadmitted gates. Adversarial checksum-bypass,
nonfinite, IEEE overflow, source gate, wrong parent and reorder tests
are at 'tools/tests/test_worldgen_26_2_stock_finaldensity_seventeenth_layer_fixture.py'.
Verify the ALREADY completed private JSON, no Java replay:

    python3 tools/worldgen_26_2_stock_finaldensity_seventeenth_layer_fixture.py \
      --capture /tmp/helve-26_2-final-seventeenth-layer-128.json

**Native test-only genuine source parity extended to seventeenth ADD.**
'crates/world/helve-world-gen/tests/stock_finaldensity_eighth_layer_262.rs'
loads the immutable seventeenth 2-word original operand receipt,
cold-validates a separate three-node HOT ExplicitAp2Add, asserts 128
IEEE rawbit parent matches, then FEEDS the newly computed ADD as the
sixteenth MIN RIGHT child into the already source-owned 16th/13th/12th/
11th/10th/9th stages to verify **128 original stock finalDensity roots**.
Earlier fixture hashes/production code and max **32 HOT node scratch**
remain unchanged. No cache law, original arbitrary-XYZ generated terrain,
or production chunk publication authority is admitted.

**Next, EIGHTEENTH original capture NOT run:** the actual seventeenth
ADD RIGHT is genuine 'DensityFunctions$Clamp' (not another imagined
source operator). Source-owned Java
'tools/worldgen_java/HelveStockFinalDensityEighteenthLayer262.java'
retraces full original real ancestry, verifies original sixteenth
MIN/Ap2+Ap2 and seventeenth ADD HolderHolder+Clamp, then reflects the
actual Clamp's source-owned min/max double bounds and its sole actual
DensityFunction child runtime class. At the SAME 4×32 XYZ it observes
just **one NEW original Clamp-wrapped child IEEE raw word**, plus **one
OLD original Clamp output** independently anchored to immutable
seventeenth RIGHT column. Source-only Python owner
'tools/worldgen_26_2_stock_final_density_eighteenth_layer.py'
pins all prior fixture/report/source ZIP/JAR/indexed-method identities,
actual class/bounds-shape and original coordinates; clamp candidate
telemetry reports below/inside/above positions and candidate mismatches
WITHOUT admitting all-input Clamp clipping or NoiseChunk cache semantics.
'tools/tests/test_worldgen_26_2_stock_final_density_eighteenth_layer.py'
validates bounded source-only frame adversarial cases and full source-free
JDK bridge compilation. Production and source gates remain FALSE.

**Only after all CI checks green and observer PR merge**, run JUST:

    cd ~/Crucible
    git switch main
    git pull --ff-only
    python3 tools/worldgen_26_2_stock_final_density_eighteenth_layer.py \
      --source "$HOME/Documents/mc-source/mc-src.zip" \
      --db .crucible/vanilla/atlas.sqlite \
      --lock vanilla/vanilla.lock.toml \
      --output /tmp/helve-26_2-final-eighteenth-layer-128.json

Upload only the new original source-free eighteenth JSON or a bounded
HELVE26_2_EIGHTEENTH_FAILURE|phase|ExceptionClass marker. Original JVM
captures 1–17 must not be repeated; source-law/all-input/production
admission requires independent review beyond finite originals.

## Eighteenth genuine Clamp[-1,+1] two-original-overrides receipt and nineteenth source frontier (23 October 2026)

**Eighteenth actual original-JVM capture COMPLETE. DO NOT repeat source
captures 1–18.** Original stock Minecraft Java 26.2 4-seed × 32
'DensityFunction$SinglePointContext' source-only JSON:
**36,555 bytes**, SHA-256
**4e8279f53b06a6de9154f18df073b742ad091acfe6b156611bc916dbbf8781ae**.
All four original Java runtime shapes identify actual seventeenth
'Ap2(ADD)' RIGHT child 'DensityFunctions$Clamp', with sole original
wrapped child runtime type **'DensityFunctions$Ap2'** and authentic
bound double bits MIN **bff0000000000000 = -1.0** and MAX
**3ff0000000000000 = +1.0**.

Original sampled Clamp candidate produces **128/128 bit-exact original
seventeenth RIGHT Clamp output**. Branch coverage:
**126 within [-1,+1]**, **2 strictly above +1**, **0 below -1**,
zero candidate mismatches. There are EXACTLY TWO original source
inner IEEE values genuinely different from the old sealed seventeenth
right Clamp column: index **18**, inner
**3ff5c1c9c20d14a4** (genuine XYZ=(128,128,128),
seed 0123456789abcdef) and index **28**, inner
**3ff219c5d9c551b1** (XYZ=(-33554431,-63,33554431),
same original seed). In both cases the old original Clamp output
is **3ff0000000000000**, +1.0. Remaining **126 original exact rawbits
are identical** to previously frozen seventeenth new-only RIGHT operand.
Finite bounded original tests support this exact sample-only candidate,
NOT general Clamp source law, cache lifecycle, NoiseChunk interpolation
or production world-generation admission.

**Critical no-duplicate-original-words policy:** new original fixture
'crates/world/helve-world-gen/tests/data/stock_finaldensity_eighteenth_clamp_true_new_two_overrides_128.tsv'
has ONLY the two authentic index/new-word override records, **40 bytes**,
SHA-256 **e1b4da2ef965a0e92ad2bb56931de16dce95318f3aadabd4e78be2721a5b2811**.
No 128-word sixteenth/seventeenth value duplicate is made.
The authentic eighteenth original full-report receipt
'tools/worldgen_26_2_stock_finaldensity_eighteenth_layer_receipt.py'
pins entire private original SHA/length, actual original four shapes,
source ZIP/JAR and method provenance via eighteenth owner, previous
seventeenth fixture SHA **ef9a7e19fc793ce4d33592756faa73a80d86ad59941ae171820b3ed8eb4263a5**,
the two newly distinct original IEEE override words and exact locations,
126 old-word equalities, all 128 independently anchored Clamp parents,
and every original source/prod gate **FALSE**. Negative fixture mutation
tests, source SHA and zero/overflow bounds tests:
'tools/tests/test_worldgen_26_2_stock_finaldensity_eighteenth_layer_receipt.py'.
To verify PRIVATE original report without recapture:

    python3 tools/worldgen_26_2_stock_finaldensity_eighteenth_layer_receipt.py \
      --capture /tmp/helve-26_2-final-eighteenth-layer-128.json

**Native test-only original sampled Clamp composition extended to roots.**
'crates/world/helve-world-gen/tests/stock_finaldensity_eighth_layer_262.rs'
reconstructs the original 128 raw inner Ap2 words from the original
seventeenth RIGHT parent old words with two truly new overrides,
uses separate **5-node COLD-validated Max(-1) then Min(+1)** native
staged composition, verifies genuine Clamp **128/128**, genuine 2
upper clipping events; feeds CALCULATED Clamp parent into existing
17th ADD, 16th MIN, 13th MIN, 12th MIN, 11th MAX/MIN,
10th RangeChoice, ninth root and checks **128 genuine JVM finalDensity
outputs**. The largest separate HOT stage remains bounded at 32
nodes. No production Rust changes or extra HOT runtime allocation.

**Next original source frontier: NINETEENTH (NOT RUN).** The actual
eighteenth 'Clamp[-1,+1]' wraps a real 'DensityFunctions$Ap2'.
'tools/worldgen_java/HelveStockFinalDensityNineteenthLayer262.java'
follows the precise stock original rooted ancestry, checks this
specific Clamp and bounds and authentic wrapped Ap2, then reflects
that actual Ap2's **own genuine operation** and two immediate actual
DensityFunction runtime children. Captures precisely **TWO NEW child
IEEE words/sample**, plus ONE OLD raw Ap2 parent independently
reconstructed with the source-proven eighteenth two-new-only override
receipt, not re-frozen as a nineteenth numerical fixture. The strict
Python owner 'tools/worldgen_26_2_stock_final_density_nineteenth_layer.py'
pins previous thirteenth-through-eighteenth original source-report
SHAs, immutable thirteenth/sixteenth/seventeenth fixture SHAs,
exact eighteenth 40-byte new-only fixture, official source ZIP/JAR
and indexed method body IDs, original four seeds/XYZ, all-false
source/cache/VAR-SEM/NoiseChunk/production gates. Full source-free
JDK javac and adversarial genuine-old-parent/fake-source frames:
'tools/tests/test_worldgen_26_2_stock_final_density_nineteenth_layer.py'.
Finite candidate arithmetic telemetry does NOT admit Java all-input
operation law and does not censor original mismatches.

**Only AFTER green checks and merge of nineteenth source owner PR**
run the SINGLE new original stock capture below, no 1–18 replay:

    cd ~/Crucible
    git switch main
    git pull --ff-only
    python3 tools/worldgen_26_2_stock_final_density_nineteenth_layer.py \
      --source "$HOME/Documents/mc-source/mc-src.zip" \
      --db .crucible/vanilla/atlas.sqlite \
      --lock vanilla/vanilla.lock.toml \
      --output /tmp/helve-26_2-final-nineteenth-layer-128.json

Upload only new nineteenth source-free JSON (or bounded
HELVE26_2_NINETEENTH_FAILURE|phase|ExceptionClass). The real source
operation/children may NOT be guessed from the eighteenth Ap2 class.


## Nineteenth actual Clamp-wrapped Ap2(ADD) original report and strict receipt (23 October 2026)

**NINETEENTH ORIGINAL JVM CAPTURE COMPLETE. Never recapture layers 1–19.**
The source-free original 26.2 stock RandomState report was received as
`helve-26_2-final-nineteenth-layer-128.json`: **43,278 bytes**,
SHA-256 **a79b4d191a42f3f264d5e44757aa75c56cdf5077258d36c967207b058695e1f1**.
Four original seeds × 32 immutable coordinates, 128 original
`DensityFunction$SinglePointContext` frames. The independent old parent
is the original eighteenth **unclamped** Ap2-inner output reconstructed
from seventeenth immutable RIGHT Clamp words and the two eighteenth
genuinely new overshoot overrides (indices 18, 28).

All four original JVM source-reflected concrete runtime shapes agree:
eighteenth `Clamp[-1,+1]` wrapped child is
`DensityFunctions$Ap2(ADD)`, whose **genuine immediate LEFT child**
is `DensityFunctions$Ap2` and whose **genuine immediate RIGHT child**
is `DensityFunctions$MulOrAdd`. No source topology was inferred from
numeric equalities. The actual 256 **new** child IEEE-754 raw words
(128 LEFT, 128 RIGHT) yield bit-exact floating-point ADD to the frozen
old eighteenth raw parent in **128/128** original samples,
mismatches **0**. RIGHT operand is strictly less than LEFT for
**128/128**, ties **0**. The old parent exceeds +1 in the same two
previously pinned eighteenth samples; no new clamp-parent numbers
are duplicated. This is *bounded sample agreement only*.

The two-new-child-only fixture is
`crates/world/helve-world-gen/tests/data/stock_finaldensity_nineteenth_clamp_ap2_add_children_128_rawbits.tsv`,
**4,352 bytes**, SHA-256
**77b5729bf8895a5b71b256b662643e87b2afa8fe0cc06caf7848787433fb48c4**.
It contains ONLY `left_rawbits<TAB>right_rawbits`, with no copied
old parent, XYZ, seed or source text. Strict accompanying Python owner:
`tools/worldgen_26_2_stock_finaldensity_nineteenth_layer_fixture.py`;
negative SHA/malformed/floating-point/old-parent mutation tests:
`tools/tests/test_worldgen_26_2_stock_finaldensity_nineteenth_layer_fixture.py`.
This module validates original private full-report SHA and byte count,
the entire existing nineteenth source-owner provenance (previous reports,
fixture identities, official ZIP/JAR and indexed method hashes),
exact original concrete four shapes, all original bit anchors, arithmetic
telemetry, and unmodified **FALSE** qualification and production gates.

To verify the **already supplied** private nineteenth report (never
recapture stock original layers 1–19):

    python3 tools/worldgen_26_2_stock_finaldensity_nineteenth_layer_fixture.py \
      --capture /tmp/helve-26_2-final-nineteenth-layer-128.json

The native **test-only** `stock_finaldensity_eighth_layer_262.rs` stages
a separate cold-validated 3-node `ExplicitAp2Add` on the two genuine
nineteenth words; verifies 128 original eighteenth raw parents; computes
genuine 18th Clamp (including both original +1 overshoots); and passes
CALCULATED results through previously frozen genuine 17th ADD, 16th MIN,
13th/12th MIN, eleventh MAX/MIN, tenth RangeChoice and ninth-layer
partial root to the **128 original stock JVM finalDensity roots**. The
largest separate hot stage remains 32 nodes. No runtime or production
router graph has been introduced.

**Still OPEN:** independent original Java method source review and
VAR/SEM admission; general `Ap2.compute` law; `MulOrAdd` runtime and
its actual child semantics; cache/Marker/NoiseChunk lifecycle; full
router and seeded worldgen numeric parity; ordinary server chunk
publication and production worldgen. All corresponding flags remain FALSE.

**Next genuine source frontier is TWENTIETH, not recapture of
nineteenth.** Follow only the genuine nineteenth `Ap2(ADD)` RIGHT
`MulOrAdd` child first: reflect its actual runtime operation enum,
constant parameter and immediate wrapped DensityFunction class from
the original stock JVM, and capture its ONE genuine new wrapped-child
IEEE word at each of the same original 4x32 coordinates. The old
nineteenth RIGHT operand must be independently anchored to the new
nineteenth two-column fixture; do not duplicate it. Preserve fail-closed
source archive/official JAR/indexed-method provenance, fixed response
size, exact source class/op assertions, malformed fake-source tests, all
FALSE admission gates, and a distinct execution command only after the
twentieth observer passes CI. Do not guess `MulOrAdd` variant or scalar
from the previous negative numeric values.


### Twentieth actual nineteenth-RIGHT MulOrAdd source observer, pre-capture (23 October 2026)

The next *source-only* observer is now staged, **NOT captured or
qualified**. `tools/worldgen_java/HelveStockFinalDensityTwentiethLayer262.java`
reconstructs the existing original stock `RandomState` router, strictly
retraces the actual seventeenth ADD Holder/Clamp, eighteenth Clamp[-1,+1],
nineteenth `Ap2(ADD)` with actual LEFT `Ap2` and RIGHT `MulOrAdd`.
It then reflects **that exact right MulOrAdd node**, reads genuine
`specificType` enum and `argument` raw IEEE scalar, and gets its
single real wrapped DensityFunction child runtime class. It exports
exactly ONE new child IEEE value and ONE OLD right-parent word in each
of the original 4 × 32 fixed `SinglePointContext` samples. It does
not presume whether the actual operator is ADD or MUL, what scalar it
uses, or its wrapped child's concrete class.

Strict source-free transport and provenance:
`tools/worldgen_26_2_stock_final_density_twentieth_layer.py`,
negative tests and javac source bridge:
`tools/tests/test_worldgen_26_2_stock_final_density_twentieth_layer.py`.
Old twentieth-parent words are independently bit-anchored to the
nineteenth immutable RIGHT-column fixture SHA
**77b5729bf8895a5b71b256b662643e87b2afa8fe0cc06caf7848787433fb48c4**;
the original nineteenth private report is separately pinned by SHA
**a79b4d191a42f3f264d5e44757aa75c56cdf5077258d36c967207b058695e1f1**.
No older original captures are re-run. No source text is exported.
Arithmetic comparison is diagnostic only, never filters real captures;
previous gates and `twentieth_actual_muloradd_child_qualified` and
`twentieth_all_input_muloradd_law_admitted` are all FALSE.

**Only after this twentieth-observer PR CI is green and it merges**,
run the SINGLE new twentieth original JVM capture (no 1–19 replay):

    cd ~/Crucible
    git switch main
    git pull --ff-only
    python3 tools/worldgen_26_2_stock_final_density_twentieth_layer.py \
      --source "$HOME/Documents/mc-source/mc-src.zip" \
      --db .crucible/vanilla/atlas.sqlite \
      --lock vanilla/vanilla.lock.toml \
      --output /tmp/helve-26_2-final-twentieth-layer-128.json

Upload ONLY the new source-free twentieth JSON or the bounded
`HELVE26_2_TWENTIETH_FAILURE|phase|ExceptionClass` diagnostic marker.
All preceding original stock 4×32 captures are complete and must
not be repeated. The observed scalar/operation/class must be reviewed
*from this actual source probe*, not guessed before it executes.

## 2026-10-23 — original twentieth RIGHT MulOrAdd child (one new word per point)

**Original stock Java 26.2 evidence received**: 4 actual RandomState seeds × 32
original SinglePointContext XYZ = 128 points. Private source-free original
capture length **37,509 bytes**; SHA-256
`859e7f78594bb2ddca090627ea6e04503b220f6b619fe3df46bab8b25394bbd8`.
The indexed source and server SHA pins have **not** changed.

The nineteenth original Clamp-wrapped Ap2(ADD) RIGHT child was observed as
`DensityFunctions$MulOrAdd`, with its own original source-reflected enum
`ADD`, constant argument raw IEEE `bfb395810624dd2f` = -0.0765, and
genuine wrapped-child runtime class `DensityFunctions$MulOrAdd`.
All four seeds observed the identical concrete operator, scalar and class.
Exactly 128 new original wrapped-child IEEE words were captured; another 128
nineteenth RIGHT MulOrAdd parent bits served **only as independent anchors**
to the sealed nineteenth original two-new-word receipt.

The original 128 finite ADD candidates `twentieth_inner + (-0.0765)` exactly
bit-match their **old frozen nineteenth RIGHT** parents, with 0 mismatches.
No generalized Java numeric / source-method / cache / NoiseChunk / production
claim follows from finite bounded samples.

Only 128 genuinely NEW IEEE words are stored in
`crates/world/helve-world-gen/tests/data/stock_finaldensity_twentieth_muloradd_nested_child_128_rawbits.tsv`:
2,176 bytes, SHA-256
`cfefd23fb5cb60a0d8da2ec0a12990c58ef6b94bd2faff2639e1660148482d6c`.
No old parent copies, old seed rows, private original report, Java source archive
or unsourced inferred operand values enter the fixture.
`tools/worldgen_26_2_stock_finaldensity_twentieth_layer_fixture.py`
seals the original report and fixture size/SHA, observed enum/constant/child
shape, fixed seed identities, source index, every false gate, and reconstructs
each old parent from the already-frozen nineteenth original RIGHT bits.

The test-only Rust cold-validated 3-node ADD with original scalar then enters
the true nineteenth ADD, eighteenth Clamp[-1,+1] (2 genuine clips),
seventeenth ADD, sixteenth MIN, thirteenth/twelfth/eleventh/tenth/ninth
stages and all 128 genuine stock finalDensity root anchor words.
No existing HOT-stage allocation or production world generation is enabled.

### Single new twenty-first original JVM frontier

The genuine 20th wrapped child was observed to be another
`DensityFunctions$MulOrAdd`. The next bounded original-JVM observer therefore
retraces source-owned ancestry and reflects **that nested node's actual**
`specificType` enum, constant `argument` bits and wrapped child class, then
samples only its ONE new original child IEEE word per original point. The 20th
wrapped-child old parent is independently anchored to the new-only sealed 128
20th fixture. No next operation, scalar or inner-child runtime type is
assumed ahead of the actual JVM capture. This is **not** a request to recapture
earlier layers.

Only after this PR is CI-green and merged:

```bash
cd ~/Crucible
git switch main
git pull --ff-only
python3 tools/worldgen_26_2_stock_final_density_twenty_first_layer.py \
  --source "$HOME/Documents/mc-source/mc-src.zip" \
  --db .crucible/vanilla/atlas.sqlite \
  --lock vanilla/vanilla.lock.toml \
  --server-jar .crucible/vanilla/downloads/26.2-server.bin \
  --output /tmp/helve-26_2-final-twenty-first-layer-128.json
```

The `--server-jar` argument avoids an otherwise unconditional online version
manifest request from `official_state_data.resolve()`; the runtime is still
independently SHA-256 checked against the original stock lock.

**All source/VAR-SEM/all-input/cache/NoiseChunk/router/production admission
gates remain FALSE.** Passing finite source-observed witnesses cannot promote
them. Earlier original stock captures 1–20 are already complete and must not
be repeated.

## 2026-10-23 — twenty-first genuine nested MUL terminates at real Noise leaf

PRIVATE original stock 26.2 **37,461-byte** source-free JVM receipt (SHA-256
`a14316f209553322029b2df7a37ddc757d5f52ae53005f404427111a00f58fec`).
Exactly **4 independent actual RandomState world seeds × 32 existing XYZ**.
Original actual twentieth wrapped child is `DensityFunctions$MulOrAdd`:
concrete operator **MUL**, scalar IEEE `bf878d4fdf3b6458` (approximately
−0.0115), concrete wrapped child `DensityFunctions$Noise`. No assumed
source class, operator, or scalar from numerical coincidence. All 128 new
stock Noise outputs exactly reproduce the independently frozen twentieth
child parent under IEEE multiplication (**128/128**; 0 mismatches).
Original Java source archive and server SHA pins are unchanged.

Only **128 genuinely new Noise leaf IEEE words** enter
`stock_finaldensity_twenty_first_actual_noise_leaf_128_rawbits.tsv`,
2,176 bytes, SHA-256 `7519acc761730ba6aac2f1ac03d4b625d529127e258e23a8945dee7d25e193ed`.
`tools/worldgen_26_2_stock_finaldensity_twenty_first_layer_fixture.py`
pins the original report bytes/SHA, exact original operator/argument/child
class, prior twentieth fixture and source history, all false admission gates,
and independently verifies all 128 frozen twentieth parents. **No copy of old
parent bits, original stock source text, archive, registry or seed dataset** is
stored in this receipt. Rust adds only test-only cold 3-node MUL candidate,
then traverses each existing cold 20→9 stage to 128/128 genuine original
finalDensity root anchors; no production changes.

### Next frontier: source-owned Noise leaf STRUCTURE, not a nonexistent 22nd numeric child

The original twenty-first actual child is a `DensityFunctions$Noise` leaf.
There is **no deeper density-function child to recurse into**. Accordingly,
`HelveStockFinalDensityTwentySecondLayer262.java` retraces the original
RandomState noise router graph and observes the **genuine source-owned**
`Noise` node xz/y scales, actual `DensityFunction$NoiseHolder` binding
and concrete NormalNoise runtime, original `Holder` storage class and its
unwrapped resource-key identity (possibly explicitly `unkeyed`).
The 128 numeric old Noise words are **independently checked against the
previous sealed one-new-word fixture**; the 22nd evidence adds **zero**
new numeric words. No presumed noise key, scale or registry holder is
manufactured, and no all-input NoiseHolder seed/random/cache law is admitted.

Only after this PR is merged with all CI/workgen qualifications green, run:

```bash
cd ~/Crucible
git switch main
git pull --ff-only
python3 tools/worldgen_26_2_stock_final_density_twenty_second_layer.py \
  --source "$HOME/Documents/mc-source/mc-src.zip" \
  --db .crucible/vanilla/atlas.sqlite \
  --lock vanilla/vanilla.lock.toml \
  --server-jar .crucible/vanilla/downloads/26.2-server.bin \
  --output /tmp/helve-26_2-final-twenty-second-layer-128.json
```

This explicitly bypasses the otherwise unconditional online manifest
lookup but **does not** bypass the stock server SHA-256 pinned in
`vanilla/vanilla.lock.toml`. Earlier original original probes 1–21 must
not be repeated. All source/VAR/SEM/full router/NoiseChunk/cache/production
gate flags remain **false**. The 22nd result is noise-**structure**
evidence only.

### Twenty-second source-owned `Holder` key reflection repair (23 October)

The first original stock runtime execution of the terminal-Noise structure
observer reached `twenty-first-layer-0-0-original-22nd-holder-resource-key`
but stopped with `java.lang.NoSuchMethodException`. This occurred after the
real nested `DensityFunctions$Noise` and NoiseHolder type had been reflected;
it did **not** indicate a new mismatch in any of the 128 original arithmetic
or Noise leaf fixtures.

The observer's previous use of `Holder.class.getMethod("unwrapKey")`
incorrectly presumed a public method on the pinned runtime. The replacement
reads exactly one non-static, `ResourceKey`-typed instance field from the
actual `Holder$Reference` storage, requiring unique identity, accessibility
and a non-null typed value. The already supported `Holder$Direct` is explicitly
`unkeyed`. Neither branch constructs a key or guesses a registry value.
The `ResourceKey.location()` boundary has its own failure phase to isolate a
potential additional original runtime API mismatch without weakening the
source/provenance checks. The original Java source body, source SHA, server
SHA and all production/VAR/SEM/cache/all-input admission gates remain pinned,
unchanged and **false**.

Existing original stock data 1–21 remains fully reusable. The only retry
is the same twenty-second source-owned Noise structure command above, after
this repair passes CI and merges.
