# Helve 26.2 — next `finalDensity` source frontier: nineteenth ADD LEFT

**24 October 2026 · bounded original stock JVM · protocol 776 · DataVersion 4903**

## Current established state (do not repeat work)

- PRs #524 and #525 are **merged**, all seven required workflows green.
  The genuine stock `minecraft:spaghetti_3d_thickness` `NormalNoise`
  was independently identified, its original `firstOctave=-8` and
  `amplitudes=[1.0]` observed, and its immutable Rust prepared state
  derived from the world seed without injecting captured noise/state.
- Debug **and** release demonstrate exactly **128/128 raw f64 Noise matches**
  for four signed world seeds × 32 original XYZ, and the native-produced
  Noise passes through the staged original root reconstruction to all
  **128/128 original `finalDensity` roots**.
- This is a **partial** graph: other operands still come from explicitly
  frozen independent original JVM values. It proves neither a full
  input-free graph nor live `NoiseChunk` evaluation/production.
- Prior original JVM numeric and structure captures **1–23** remain sealed.
  Do not re-run them. The next target is a sibling, **not a 24th child
  below the terminal spaghetti Noise**.

## Why the actual nineteenth ADD left operand?

The source-owned nineteenth real Clamp[-1,+1] child was independently
observed to be **ADD(Ap2, MulOrAdd)**. The right `MulOrAdd` chain is the
now-native-seeded spaghetti branch. The **LEFT `Ap2`** is presently a
frozen nineteen-layer fixture value in the final staged root proof; its
immediate children and operation have NOT yet been separately observed.
Pretending it is a Noise, Constant, RangeChoice or a prequalified operator
would violate source-first graph ownership.

The original 19th two-new fixture
`stock_finaldensity_nineteenth_clamp_ap2_add_children_128_rawbits.tsv`
SHA-256 `77b5729bf8895a5b71b256b662643e87b2afa8fe0cc06caf7848787433fb48c4`
provides **128 authoritative left-parent words**; reusing them avoids
recapturing 19th parent outputs.

## New twenty-fourth *side* observer

- `tools/worldgen_java/HelveStockFinalDensityTwentyFourthLayer262.java`
  retraces genuine stock `VanillaRegistries` → `RandomState` →
  original `finalDensity` graph → 19th ADD(Ap2,MulOrAdd), and inspects
  only its genuine left `Ap2` enum and immediate two child classes.
- It captures two **new** exact raw IEEE words at each old source XYZ
  (up to 256 genuinely new operands), plus one **OLD** 19th left parent
  word, which is strictly checked against the sealed fixture.
- Python `tools/worldgen_26_2_stock_final_density_twenty_fourth_layer.py`
  pins original 26.2 source/JAR hashes, old 19th fixture and report SHA,
  previous 23rd parameter receipt SHA, all source-method signatures,
  the real 4×32 sample order, bounded frame widths and **false** gates.
- Adversarial source-free and complete Java bootstrap compilation tests:
  `tools/tests/test_worldgen_26_2_stock_final_density_twenty_fourth_layer.py`.
- No Java source archive, Atlas data, server JAR, resource registry
  object, private whole report or previously captured value is committed.

After CI passes and this observer merges, run **only**:

```bash
cd ~/Crucible
git switch main
git pull --ff-only

python3 tools/worldgen_26_2_stock_final_density_twenty_fourth_layer.py \
  --source "$HOME/Documents/mc-source/mc-src.zip" \
  --db .crucible/vanilla/atlas.sqlite \
  --lock vanilla/vanilla.lock.toml \
  --server-jar .crucible/vanilla/downloads/26.2-server.bin \
  --output /tmp/helve-26_2-final-twenty-fourth-layer-128.json
```

Inspect the **actual** left `Ap2` op and child classes before implementing
anything further. If the genuine observation yields trivial gradient or
single registered Noise inputs, connect their separately verified native
source laws; if the children are other wrappers, follow only that observed
ancestry. Freeze **new-only** IEEE words and reuse old 19th parent bits.
All full-router, source all-input, VAR/SEM, cache/NoiseChunk lifecycle,
native production worldgen and chunk-publication authority gates remain
**false** regardless of this bounded source capture.
