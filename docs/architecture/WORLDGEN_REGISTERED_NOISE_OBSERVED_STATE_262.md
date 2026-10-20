# Minecraft Java 26.2 — bounded observed-state registered-noise sampler

**20 October 2026 · Rust numeric replay substrate, not stock world-seed derivation**

`crates/world/helve-world-gen/src/registered_noise_state_262.rs` introduces
an immutable COLD-owned Perlin/Normal sampler with **1–64** arbitrary octave
slots, including absent octaves. Unlike the earlier four-slot
`from_direct_seed_observed_profile`, it never fabricates an amplitude set,
normalisation factor or positional random seed for
TEMPERATURE / CONTINENTALNESS / EROSION. It requires all numeric state to be
supplied explicitly from reviewed, source-free runtime evidence.

The constructor checks octave and amplitude counts, signed Java octave-index
overflow and finite factor values, and retains each of the two Perlin
branches independently in boxed immutable slices. State equality compares
IEEE-754 raw bits and complete ImprovedNoise state. No allocation, RNG,
mutable cache, registry dispatch, per-block conversion of source records or
secondary world owner occurs inside its scalar sample path.

The `sample_perlin_parts` scalar evaluator is shared with the existing
direct-seeded four-slot sampler to preserve Java numerical operation order;
its previously qualified fast 16×16 plane/cell paths remain unchanged. The
new generic observed-state density leaf reuses the three exact integer-block
scale profiles and borrows prepared state. It deliberately has no authority
to install or publish chunks.

**Regression evidence:** the new module reconstructs the already qualified
*direct-seeded* four-octave example from observed numeric parameters and the
existing legacy positional RNG, then compares exactly **480/480** separate
official raw-bit density outputs in debug/release tests. This establishes
that the larger observed-state container does not lose or reorder these
numbers. It is **not** a claim of even one real *stock registered world-seed*
Rust match, nor a proof that the legacy direct-seeded constructor is the
world-seed positional factory.

Next steps:
1. Run the bounded official 15-state inspector merged via PR #447 on the
   private source-owning machine. Pin the source-free output and distinguish
   the actual registered key parameters, full octave layouts and RNG state.
2. Independently read the exact 26.2 `RandomState.create`, seed/fork,
   `Noises.instantiate`, `NormalNoise`, `PerlinNoise`, `ImprovedNoise`
   and reached RNG delegates. Bind source hashes and prove positional factory
   family, key-naming, signed arithmetic, cache order and absent-octave skips.
3. Only then add immutable world-seed-to-registered-sampler construction,
   pin independent held-out official samples, and run a dedicated Rust
   **1,440/1,440** raw-bit fixture comparison. Both fresh and frozen parity
   tests must pass in debug and release before any parity flag changes.

Independent VAR/SEM, NoiseRouter/terrain and production publication
permissions remain CLOSED. R2D visible pregenerated-world work is separate.
