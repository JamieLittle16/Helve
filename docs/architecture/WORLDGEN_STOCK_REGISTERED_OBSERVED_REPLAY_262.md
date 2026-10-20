# Minecraft Java 26.2 — exact stock-worldseed registered-noise **observed-state** replay

**Status:** independently observed official stock-registry numeric state, imported by immutable Rust samplers and compared to the **separately captured** 1,440-output stock JVM oracle. This qualifies a narrow numeric *evaluation* pathway when the dedicated Rust test passes; it does **not** reconstruct a normal-noise state from world seed, assert arbitrary-seed parity, admit source VAR/SEM, or authorise production generation.

## Do not reopen the existing noise foundations

The 26.2 `ImprovedNoise262`, `PerlinNoise262`, `NormalNoise262` and direct `DensityFunctions.Noise` candidates were separately built and exact-bit compared against the official *direct-seeded* family, including 480/480 direct noise density samples. PR #448 introduced `RegisteredPerlinObserved262`, `RegisteredNormalObserved262` and `RegisteredNoiseDensityObserved262` for arbitrary bounded octave spans and immutable COLD-owned stock-shaped observed state. Both existing kernels share the same bit-qualified scalar arithmetic. Neither is a stock world-seed constructor.

## New independent official source-free evidence

- Full original `helve-26_2-stock-registered-state-01.json` source-free receipt (15 stock JVM states): **260,830 bytes**, SHA-256 **`9a06ced3efbc005941ed3ffaf2e80039480bd180ac6a0054f5c87e98056bba12`**.
- Strict source/free source identity as independently captured: Minecraft Java **26.2**, protocol **776**, DataVersion **4903**; official server SHA-256 `cdacdfb25898de5e4b4b0e5ddcc2722f77067e46605709c2d886c000ebb63ec5`; source archive SHA-256 `1e9bca3dff83cd83e7905f8810f1ec9899361fa2dc83fe893bb48beeb04df750`; binding frontier SHA-256 `1ce8eec830e497ccae7cb814705fd820fa466fb7824c7c220b54313aabe5c2c7`.
- The separately captured stock-registry output fixture `vanilla/reports/worldgen-26_2-stock-worldseed-noise-bits-01.txt` remains immutable, SHA-256 **`79bf0251f2cf8bb7f4bfb226be0ba7912a7a574c6aaf8e8f5a9560dd2edfe414`**.
- The derived **91,244-byte**, source-free numeric fixture `crates/world/helve-world-gen/tests/data/stock_registered_observed_state_26_2.txt` has SHA-256 **`e3481e2885cbe44ecb93c19ecc9c06e62200b26b47883399f053de46676fe3ce`**. It carries the complete two-branch Perlin/Improved state, 150 256-byte permutation bijections, raw IEEE-754 offsets, the full amplitude arrays, absent-slot markers and scalar factors. It contains neither Mojang source text nor a server JAR.
- Independent receipt validation confirmed exactly five ordered signed world-seed bit patterns (0, 1, -1, signed 64-bit MIN, `0x9e3779b97f4a7c15`) and the three real registered keys, no reordered/dropped/malformed states and registered parameters constant across seeds. Each of 15 groups ended with a complete marker.

The official stock registered parameters are:

| Key | First octave | Amplitudes |
| --- | ---: | --- |
| TEMPERATURE | -10 | [1.5, 0, 1, 0, 0, 0] |
| CONTINENTALNESS | -9 | [1, 1, 2, 2, 2, 1, 1, 1, 1] |
| EROSION | -9 | [1, 1, 0, 1, 1] |

## Qualification test and claim boundary

`crates/world/helve-world-gen/tests/stock_registered_observed_262_official.rs` builds all 15 immutable observed normal samplers once from the **complete** compact fixture, then iterates the exact official **3 scale profiles x 5 signed seeds x 3 registered keys x 32 signed block-coordinate positions**, comparing all 1,440 raw `f64::to_bits()` outputs. It includes large coordinate-wrap cases, nontruncated nine-octave states and seed-specific distinctness tests. The run tests Rust arithmetic against independent JVM *outputs* — it does not invoke JVM from CI and does not use oracle results as inputs for the evaluator.

**Next:** use the same 15 observed numeric states as internal reference for an independently source-reviewed, actually seed-derived keyed positional RNG + Normal/Perlin/Improved cold constructor. Compare **entire prepared states**, then run the *same* 1,440 vectors from the seed-derived Rust constructor, followed by held-out official runtime seed/key/point vectors. No noise-router or chunk-publication shortcut.

**Gates remain:** `world_seed_random_state_bound=false`; `independent_var_sem_admitted=false`; `production_worldgen_enabled=false`. Never relabel observed-state replay as seed-constructor parity.
