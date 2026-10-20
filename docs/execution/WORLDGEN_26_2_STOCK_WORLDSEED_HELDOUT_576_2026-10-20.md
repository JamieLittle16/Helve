# Helve — truly independent stock world-seed noise held-out, 576 requests

**Date:** 20 October 2026. **Minecraft:** Java 26.2 / protocol 776 / DataVersion 4903.
**Purpose:** independently check the already implemented seed-derived Rust Xoroshiro/positional
noise constructor against *different world seeds and block coordinates*, not recapture the
original 1,440 JVM samples.

## Already achieved

- PR #449: complete 15-state prepared stock JVM observation and source-free replay.
- PR #450: independently seed-derived Rust stock registered noise states; all 15 **full
  numeric states** exactly matched; all 1,440 existing JVM output bits matched in
  debug/release. These are not independently held-out new seeds.
- PR #451: one-root seed-owned three-key immutable sampler, 16×16 coherent planes
  and 16³ integer-block cells. Bitwise equivalence to scalar; allocation-free sampling.
  No production publication or source VAR/SEM upgrade.

## New bounded original-JVM check

The only new mode is `--heldout-576` on the **same original** reflection-only
`HelveWorldSeededDensity262.java`, not a second stock registry bridge. The
default mode still requires **exactly 1,440 original lines** and has no other
behavioral change. In held-out mode, exactly 576 lines are demanded:

- Three existing scale pairs: `unit`, `quarter_xz`,
  `quarter_xz_half_y` (in original semantic order).
- Four genuinely different 64-bit world seeds:
  `0x0123456789abcdef`, `0x7fffffffffffffff`,
  `0x8000000000000001`, `0xf0e1d2c3b4a59687`.
- Exact same three built-in registered stock noise keys, in original order:
  TEMPERATURE, CONTINENTALNESS, EROSION.
- Sixteen new integer XYZ requests per seed/key/profile, including
  signed Y extremes, ±2^25 wrapping, near-signed-i32 extrema,
  and conventional block/chunk boundaries.
- Ordering remains profile → seed → key → point. Every response contains
  one strict sequential index and an **original raw IEEE-754 f64 bit word**.
  The parser does not admit bad length, duplicate row, NaN text, changed
  stock origin, changed method/lock hashes or a non-official-runtime JVM.

The bounded Python collector `tools/worldgen_26_2_stock_worldseed_heldout_capture.py`
reuses the **same** pinned source archive and Atlas, original official server
and verified `VanillaRegistries.createLookup` provider; no fake holders,
source code, raw JAR or private Atlas database is transported. Output is
source-free JSON, stored externally through exclusive file creation (0600).
The helper deliberately reports `rust_heldout_parity_verified=false`.

## Exactly one source-owning local run

From the checked-out GitHub Helve repo (local directory may still be
`~/Crucible`), after pulling this merged PR:

```bash
python3 tools/worldgen_26_2_stock_worldseed_heldout_capture.py \
  --frontier /tmp/helve-26_2-random-state-binding-frontier-01.json \
  --source "$HOME/Documents/mc-source/mc-src.zip" \
  --db .crucible/vanilla/atlas.sqlite \
  --lock vanilla/vanilla.lock.toml \
  --output /tmp/helve-26_2-stock-worldseed-heldout-576.json
```

The output path **must not already exist**. Upload **only** the
source-free `/tmp/helve-26_2-stock-worldseed-heldout-576.json` and the
printed capture SHA-256. Do not upload the original source archive, server
JAR, Atlas DB, or any decompiled body.

## After receiving the held-out receipt

1. Confirm actual 576-line completeness and all origin/source pins, fingerprint
   the JSON and compare every row to the pure seed-derived **Rust**
   `StockWorldSeededNoiseSet262` density evaluator (do not inject the received
   numeric answer into the Rust constructor).
2. Pin independent output bytes in a small source-free Rust integration fixture
   and test **576/576 raw bits** in both debug and release. Diagnose the
   first differing `(scale, seed, key, XYZ)` tuple on any mismatch.
3. Independently review the pinned 26.2 RandomState/Noises/Xoroshiro source
   delegates, including constructor choice, MD5 positional naming,
   absent octave slots and exact `nextInt` rejection semantics.
4. Only the resulting precise held-out parity claim can be promoted. Neither
   an official reference acquisition alone nor numeric parity silently
   switches on production terrain, full NoiseRouter or R2C publication.

**Always closed until independently admitted:** `world_seed_random_state_bound=false`,
`independent_var_sem_admitted=false`, `production_worldgen_enabled=false`.

## Actual independent JVM receipt received — 20 October 2026

The originally requested **source-free** 576-record JSON was received from the
source-owning machine. It had the exact 26.2 official runtime SHA, original
source and method-fingerprint chain, original 1,440-vector reference identity,
and closed source/production gates. Every record had the expected
profile → seed → key → point position and a finite raw `f64` word.

**Pinned original capture SHA-256**:
`59c510f78edd2f70351c377ea8d13017f52370cfa20bc480a73cddcfb59b19f5`.

**Small derived source-free oracle**:
`crates/world/helve-world-gen/tests/data/stock_worldseed_heldout_576_rawbits.txt`,
exactly 576 lines of 16 lowercase hexadecimal digits and newline
(9,792 bytes), SHA-256
`0a0ae74712c31ea735f293c54264b80ecdc00e667b82d84eded003bf0660dab4`.

**Verification tools**:

- `tools/worldgen_26_2_stock_worldseed_heldout_fixture.py` verifies fixture
  size, SHA-256 and finite IEEE words. With
  `--original-json /path/to/helve-26_2-stock-worldseed-heldout-576.json`
  it also verifies the original upload SHA, all method/source keys and
  record-by-record correspondence with the small fixture. The original
  141-kB JSON itself remains uncommitted.
- `tests/stock_worldseed_heldout_262_official.rs` executes all 576
  independent outputs against the unchanged
  `StockWorldSeededNoiseSet262::new_candidate` and
  `RegisteredNoiseDensityObserved262::sample_block`. It constructs its
  permutations and octave states from the *unseen seeds*, not the JVM
  output or captured tables. On a mismatch it reports the exact raw bit
  pair, scale, signed seed bits, noise key and XYZ tuple.
- CI runs Rust integration tests in **both debug and optimised release** and
  adds strict frozen-fixture mutation/format tests. Only successful CI proves
  576/576 Rust held-out parity.

This increases stock JVM coverage to **2,016 verified output cases only if the
new Rust assertions pass**: the original 1,440 and these *independent* 576.
No claim of complete 26.2 biome registry, arbitrary datapack noise,
final density routing, chunk generation or source VAR/SEM admission follows.
