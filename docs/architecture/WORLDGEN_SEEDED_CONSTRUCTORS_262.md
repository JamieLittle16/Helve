# Minecraft Java 26.2 — profile-bound direct-seed Perlin/Normal constructors

**Status (19 October 2026):** Candidate Rust constructor implementation, independently checked against full *numeric* official-runtime captures. **Not** independent source/VAR/SEM admission or general density generation. R2C production chunk publication and worldgen gates remain closed.

## Precisely qualified input profile

- Pinned official runtime: Minecraft Java 26.2, protocol 776, DataVersion 4903.
- Direct `RandomSource.create(long)` seed bits, **not** a world-generation seed translated through `RandomState`, positional routing or dimension settings.
- `firstOctave = -3`; four amplitudes with raw bits `[3ff0000000000000, 0000000000000000, 3fe0000000000000, 3ff0000000000000]` (1, 0, 0.5, 1).
- Exactly three live `ImprovedNoise` instances at indices 0, 2 and 3; index 1 remains absent.
- The separately retained observed-state path remains available; the new direct-seed path does not read the observed-state fixture.

## Reconstructed candidate construction

`LegacyBits::new(seed_bits)` initialises Java's 48-bit legacy LCG as `(seed ^ 0x5deece66d) & ((1<<48)-1)`. A `nextLong()` consumes **two** 32-bit draws and combines them by signed-Java-long shifting and addition, not by unsigned concatenation.

For each Perlin instance, consume precisely **one parent** `nextLong()` for a positional factory. For active octave index `i`, construct a separate legacy random stream from:

```text
octave_number = firstOctave + i
inner_seed_bits = positional_factory_seed XOR
    sign_extend_i64(JavaStringHashCode("octave_" + decimal(octave_number)))
ImprovedNoise262::new(inner_seed_bits)
```

The Java string hash uses signed wrapping 32-bit arithmetic and decimal sign/ordering. No allocated string or mutable RNG is retained in the final immutable sampler. The zero-amplitude slot does not create an improved sampler and does **not** consume parent random draws on this captured new-initialisation path. The four octave fields and numerical factors are reconstructed in the same ordered slots; normal has two **different** Perlin sub-instances from two successive parent forks. This algorithm must **not** be substituted for the *legacy-initialisation* `skipOctave`/sequential-draw branch, which is still unreviewed for this target version.

The pinned observed factors are stored as exact IEEE-754 bits: Perlin lowest input `3fc0000000000000`, Perlin lowest value `3fe1111111111111`, and Normal output `3ff5555555555555`. Sampling uses the existing PR #426 bitwise-qualified evaluators unchanged.

## Evidence and regression obligations

The source-free `perlin_normal_26_2_observed_state.tsv` contains five separate JVM captures (seeds `0`, `1`, `-1`, `i64::MIN`, `0x9e3779b97f4a7c15`), with full 256-byte permutations and raw-bit X/Y/Z offsets for **all six active improved samplers per seed** (30 permutations and 90 offset numbers), plus all amplitude/factor bits and null masks. The new test compares the entire derived state against the **independent reflection-captured state**, including Normal's second branch. It additionally demands **320/320** official-JVM scalar output bits *from the derived state*, not from the fixture-loaded evaluator. Tests cover signed `nextLong` forks, signed-octave Java name hashes including `i32::MIN`, and high-bit seed truncation. The pre-existing 320 state-backed output comparisons and coherent grid equality must also continue passing.

The seeds reproduce exact constructor states under the direct-seed pinned profile, but finite evidence alone does not establish arbitrary parameter/factory/source semantics. Independently review the actual pinned source constructor, `forkPositional`, `fromHashOf`, `skipOctave` and reached `RandomSource` methods before changing any VAR/SEM declarations; method fingerprints alone are **not** a proof of the delegate laws. Extend official state/output capture with other first-octaves, sparse masks, new/legacy initialisation, positive-octave paths, and independent arbitrary seeds *before* broadening APIs. Full density-function evaluation, world seed resolution, chunk terrain output and target-machine benchmarks remain separate gates.

**Architecture:** these are one-time immutable sampler construction helpers, never per-block or per-chunk seed work; no heap allocation on scalar/grid sampling, no dynamic dispatch or production join/publication dependency. Keep `from_observed_parts` as a separate source-free diagnostic path. No new handler, world authority, registry, chunk packet or publication switch is introduced.
