# Helve — stock 26.2 `finalDensity` second-layer failure and next implementation handoff

**Date:** 21 October 2026  
**Repository:** [JamieLittle16/Helve](https://github.com/JamieLittle16/Helve)  
**Last verified merged `main` at the handoff start:** `37649da70537ac7993f5edd12f6b6b7be4b23deb`  
**Latest completed feature:** [PR #482](https://github.com/JamieLittle16/Helve/pull/482) (merged at that head; all eight required premerge checks successful).  
**Handoff repair branch:** `worldgen/262-second-layer-phase-handoff-20261021` (adds diagnostic *phase precision* and this handoff; merge only after CI green).  
**Target:** vanilla-faithful Minecraft **Java 26.2**, protocol **776**, DataVersion **4903**.

## Post-#483 correction: original MulOrAdd operation is `specificType` (21 October)

Merged [PR #483](https://github.com/JamieLittle16/Helve/pull/483) and the owner's next source-owning run were verified on `main=c9fdd3c92da817a88d8a993d7bd8bb242794b236`. The precise real original JVM failure was:

```text
HELVE26_2_SECOND_FAILURE|second-layer-0-0-muloradd-operation-record|java.lang.IllegalStateException
```

**Isolation:** This stage occurs only *after* the rooted MulOrAdd class, sole typed child, real `argument`, RangeChoice's selector/outer Ap2 and their typed children have been traversed. The broken bridge used `member(mul,"type")`: that reads **record components**, whereas the Minecraft **26.2** MulOrAdd five-component record declares `specificType` and implements a separate inherited `type()` interface method. The 26.2 NeoForge class-use Javadoc exposes the exact signature
`MulOrAdd(MulOrAdd.Type specificType, DensityFunction input, double minValue, double maxValue, double argument)`. This corroborates the phase failure; the *actual configured enum value and argument* still need a successful owner-private JVM witness.

The branch `worldgen/262-muloradd-specifictype-20261021` replaces only this incorrect reflection assumption. It checks runtime `DensityFunctions$MulOrAdd$Type` with `ADD` or `MUL`, retains the strict five-record-component contract and emits the existing unchanged 14-field second-layer SHAPE frame. Its Python parser additionally requires the runtime declaring enum class and independently verifies all 128 new MulOrAdd operand/parameter results against the **already frozen first-inner MulOrAdd output IEEE words**. This is numerical candidate parity only, **not** source-law, NoiseChunk cache, world-bound or production admission.

**Owner's next action only after CI-green merge:** rerun *only* `tools/worldgen_26_2_stock_final_density_second_layer.py` using the same pinned source, Atlas DB, lock and fresh output path. It should reveal the actual `specificType` operation, parameter, input class and words, selector child, and out-of-range Ap2 children. If it still fails, preserve the **new exact phase or source-free parser error**; do not speculate about unseen graph edges. Then freeze only genuinely new words with SHA-pinned fixtures and recursively compile the demonstrated noise/spline dependencies into the existing bounded Rust density DAG. Existing 128-root, 128-inner, 512-cell, 768-NoiseChunk and 1,152 mixed delegates **stay frozen**, and all review/VAR/SEM/production gates remain false.

Source context (not a substitute for the owner's pinned JVM): [NeoForge 26.2 class-use constructor inventory](https://aldak.netlify.app/javadoc/26.2.x/net/minecraft/world/level/levelgen/class-use/densityfunction).

## Immediate blocker: real stock source-owning second-layer JVM probe rejected

On 21 October, with user checkout successfully fast-forwarded to the **above merged main**, the user ran:

```bash
cd ~/Crucible
git switch main
git pull --ff-only
python3 tools/worldgen_26_2_stock_final_density_second_layer.py \
  --source "$HOME/Documents/mc-source/mc-src.zip" \
  --db .crucible/vanilla/atlas.sqlite \
  --lock vanilla/vanilla.lock.toml \
  --output /tmp/helve-26_2-final-second-layer-128.json
```

The exact source-free failure was:

```text
STOCK 26.2 FINAL SECOND LAYER OPEN: original 26.2 JVM second-layer rejected: HELVE26_2_SECOND_FAILURE|second-layer-0-0|java.lang.IllegalStateException
```

**What this does and does not establish:** The Python wrapper reached the original Java diagnostic and obtained its fail-closed JVM error. It happened on **seed index 0, point index 0**, before a validated second-layer JSON was published. It does **not** identify the failed record member, prove that any particular shape has changed, or undermine earlier validated JVM bit fixtures. The original bridge groups multiple reflection assertions under this undifferentiated phase; the failure could reflect a guessed record layout, field name, operation enum or another checked contract. Do **not** guess an implementation law or delete the guard.

Potential unverified checkpoints worth isolating:
- `HelveStockFinalDensityInnerSemantics262.soleDensityChild(mul, density)` demands that the real `MulOrAdd` is a Java **record** with exactly one component whose declared type is the `DensityFunction` interface. That shape was **not established** by the first-level numeric receipt.
- `member(mul, "argument")` and `enumClass(mul, "type")` assume particular **record component names and types** not yet verified for the actual upstream `MulOrAdd`.
- `RangeChoice`'s selector `Marker` record and the out-of-range `Ap2` children are independently plausible but must still be checked on original stock Java.
- The failure phase alone cannot determine which assertion failed. Avoid writing a speculative Rust implementation.

## Current structure — preserve established evidence

The stock Overworld root graph has been **observed**, not reconstructed from outdated versions:

```text
Overworld RandomState.router().finalDensity
└── DensityFunctions$Ap2(type=MIN)
    ├── DensityFunctions$Mapped(type=SQUEEZE)
    │   └── DensityFunctions$Marker(type=Interpolated)
    │       └── DensityFunctions$MulOrAdd     <- ACTUAL NEXT UNKNOWN INPUT/ARGUMENT
    └── DensityFunctions$HolderHolder
        └── Holder$Direct -> DensityFunctions$RangeChoice
            ├── input: DensityFunctions$Marker  <- ACTUAL SELECTOR CHILD UNKNOWN
            ├── minInclusive: -1000000.0
            ├── maxExclusive: 0.0
            ├── whenInRange: DensityFunctions$Constant(64.0)
            └── whenOutOfRange: DensityFunctions$Ap2
                ├── argument1 unknown           <- NEXT
                └── argument2 unknown           <- NEXT
```

Immutable independently captured original JVM evidence **already used and frozen**:
- 128 stock four-seed × 32 `SinglePointContext finalDensity` root raw-bit outputs (prior pinned 128 oracle).
- 128 genuine first-level `Mapped` and `HolderHolder` operands; actual `Ap2 MIN` wins **124 left / 4 right**.
- 128 genuine second-input `Marker`/SQUEEZE/RangeChoice tuples in
  `crates/world/helve-world-gen/tests/data/stock_finaldensity_inner_128_rawbits.tsv`;
  **15,232 bytes**, SHA-256
  `967c9203950f0e22a8b69f73dfe5e1bd1438ef1224fcc4346b8d578409c45170`.
  Original private user's matching source-free JSON: **67,785 bytes**, SHA-256
  `22c8473fa1cc409f9833731306a1d35cb633808c6571ea75fbb84a45150c56b1`.
- `CandidateSqueeze` computes original JVM `Mapped` output bits for **128/128** real stock inputs; Interpolated `Marker` delegates to wrapped `MulOrAdd` on all 128 **single-point** contexts.
- `CandidateRangeChoice` reproduces **128/128** original selector/branch choices for `[-1000000, 0)`: 47 in-range (constant 64), 81 out-of-range (an `Ap2`).
- `CandidateMulOrAdd` has **1,152** *different*, independent stock noise/constant mixed-delegate raw-bit comparisons from the frozen 1,920-word fixture; **this is NOT yet evidence for the configured `finalDensity` MulOrAdd instance**.
- Historical pinned **512-cell** and **768 adjacent `NoiseChunk`** output fixtures; an observed NoiseChunk final-density sample is **not** plain trilinear interpolation of only the final output's corners.

**Never recapture these already completed original datasets.** The failed new second-layer run did **not** complete; retrying that one specifically with improved diagnostics is appropriate.

## Existing executable Rust architecture

Most relevant files:
- `crates/world/helve-world-gen/src/stock_density_program_262.rs`
- `crates/world/helve-world-gen/src/density_composition_262.rs`
- `crates/world/helve-world-gen/src/stock_vanilla_mixed_density_262.rs`
- `crates/world/helve-world-gen/src/registered_noise_state_262.rs`
- `crates/world/helve-world-gen/tests/stock_finaldensity_inner_262.rs`
- `crates/world/helve-world-gen/tests/stock_muloradd_fused_262_official.rs`
- `tools/worldgen_26_2_stock_finaldensity_inner_fixture.py`

Preserve the **single immutable bounded at-most-32-node DAG**, cold constructor validation, backwards-only indices, at most 32-node stack/scratch, caller-owned batch buffers, lazy `Ap2` multiplication and `RangeChoice` right/selected branch evaluation, no per-sample heap allocations or extra world owners. Do not repurpose eager `Multiply` for stock `Ap2`: the original dynamic `+0` early-return differs from IEEE signed-zero multiplication. The fused `MulOrAdd` candidate is ordinary IEEE constant multiplication; its **actual finalDensity parameter/type is still unknown**.

The R2C imported-world demo remains an independent achievement; production worldgen and complete native terrain generation are **not** yet qualified.

## Exact next steps (do these in order)

1. **Finish narrow failure discrimination, merge CI green.** This handoff's branch changes only
   `tools/worldgen_java/HelveStockFinalDensitySecondLayer262.java`
   to assign precise, fixed-format, source-free `second-layer-<seed>-<point>-<step>` phase labels *before* each original reflection or numeric step. Its Java bridge must still compile via
   `tools/tests/test_worldgen_26_2_stock_final_density_second_layer.py` and all CI must pass before merge. Do not print private original Java source, method bodies, proprietary registry, stack traces, exception messages or JAR bytes.
2. **Run the failed new diagnostic once more on merged main.** Use **exactly the command above**. If it fails, paste the *new bounded phase tag*, for example a suffix naming `muloradd-child-record`, `muloradd-argument-record` or `muloradd-operation-record`. These are examples of instrumentation, **not predictions of the failed step**. The output file is only written after 128 valid samples and all checks pass. If the path already exists, select a fresh output name; never overwrite proof receipts.
3. **Correct only the original-source-backed structural assumption.** If the real Java `MulOrAdd` is not a record with a single typed `DensityFunction` component, do not call the generic record-only helper: inspect its **actual** source/Atlas-locked constructor/components/declared density child on the user's source-owning machine, or introduce a very narrow read-only source-free shape report (bounded field **names/types only**). Similarly verify actual operation/argument locations rather than guessing `"type"` or `"argument"`. Keep data traversal explicitly rooted and source-locked.
4. **Once the probe succeeds**, freeze **only its genuinely new** `MulOrAdd` upstream input words, selector-wrapped inputs, actual out-`Ap2` operands and four seed-invariant operation/argument/type declarations as a compact SHA-pinned source-free fixture. Bind three earlier outputs *bit-for-bit* to `stock_finaldensity_inner_128_rawbits.tsv`. Use the existing `tools/worldgen_26_2_stock_final_density_second_layer.py` fail-closed validator. Zero admission booleans must stay false.
5. **Implement next true nested Rust graph dependencies**, not only supplied JVM child constants. Use `CandidateMulOrAdd` only if the *actual* original operation/input/constant is independently verified; implement selector `Marker` wrapped graph and out-`Ap2` with correct operation order and lazy semantics; rerun 128-root, 128-inner and source-free new second-layer exact word comparisons.
6. **Then** extend to original `NoiseChunk` interpolation and marker/cache lifecycle (including advance/swap/slice and boundary placement) and test 768 adjacent original values and 512 cell; no production publication until all structural source-law, VAR/SEM, world-bound and numerical gates pass.

## Qualification and honesty checklist

- Original source archive/JAR/Atlas version locked at Minecraft Java 26.2, Protocol 776, DataVersion 4903; no generalized older Minecraft law assumed.
- Operation implementations must keep original floating-point ordering, handle IEEE signed zero/short-circuit distinctions, and avoid silent NaN/boundary admissions.
- Existing source-free fixture SHA pins and **all original frozen oracle data stay unchanged**.
- `mapped_squeeze_source_law_reviewed`,
  `range_choice_source_law_reviewed`,
  `marker_noisechunk_lifecycle_reviewed`,
  `full_router_graph_qualified`,
  `router_numeric_parity_qualified`,
  `independent_var_sem_admitted`,
  `production_worldgen_enabled`: **all remain false**.
- Numeric parity at `SinglePointContext` is not evidence of stateful `NoiseChunk` interpolation or production admission.
- Always inspect and retain new CI failures instead of repeatedly cycling superficial fixes; do not merge failing PRs.

## Prompt for the fresh context

> Continue Helve worldgen from the verified 21 October second-layer handoff in
> `docs/execution/HANDOFF_2026-10-21_HELVE_SECOND_LAYER_FAILURE.md`.
> Pull and verify latest main/PRs first. PR #482 merged at
> `37649da70537ac7993f5edd12f6b6b7be4b23deb`; the original 26.2
> second-layer JVM probe failed at `HELVE26_2_SECOND_FAILURE|second-layer-0-0|java.lang.IllegalStateException`.
> Finish/merge the narrow diagnostic phase instrumentation if it is not
> already merged, obtain just the **new** bounded failure phase, correct the
> real source-backed `MulOrAdd`/selector/`Ap2` reflection shape, then use
> a single successful second-layer 128-input packet to bind the actual
> nested Rust density graph. Do NOT redo frozen root/inner/512/768
> captures, invent source laws, or open any production/VAR/SEM gates.
