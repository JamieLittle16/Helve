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
