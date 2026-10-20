# Worldgen — actual stock 26.2 mixed noise/primitive density parity

**20 October 2026**, Minecraft Java **26.2**, protocol **776**,
DataVersion **4903**.

## Official independent evidence (not an inferred arithmetic contract)

PR #455 built a reflection-only, source-pinned probe which created actual stock
`VanillaRegistries.createLookup` → `RandomState.create` →
`RandomState.getOrCreateNoise` registered noise leaves and then called the
actual `DensityFunctions.add/mul` factories. The user independently ran
it against the official 26.2 JVM. **All 1,920 exact raw IEEE-754 values** and
the concrete computation classes were captured with closed admission flags.

**Original 483,143-byte source-free JSON SHA-256:**
`4e998fc577236b50fa8b9b31188eef19e56aa35210fe889498016bac038ed305`.

**Frozen 1,920-word source-free fixture:**
`crates/world/helve-world-gen/tests/data/stock_mixed_density_1920_rawbits.txt`
(32,640 bytes, one lowercase 16-digit hex word per line), SHA-256
`13d279c3ad4d1d79e991846deedd532d096fa2eb20df2d428ff1640b9fce8062`.

The uploaded JSON retained the already-pinned official source archive,
JAR, original 1,440 stock noise and independent held-out 576 noise fixture
identities, plus **all twelve** original code method-body fingerprints:
six world-seeded noise, four primitive and both composition factory methods.
`world_seed_random_state_bound=false`,
`independent_var_sem_admitted=false` and
`production_worldgen_enabled=false` remain unchanged.

## The precise observed vanilla distinction

The 1,920 records span ten profiles × four previously unseen signed world
seeds × three stock noise keys × sixteen XYZ points, using exact quarter
horizontal / half vertical scaling. Each profile has 192 outputs.

| Mixed profile family | Actual returned object class | Reached compute declaration |
| --- | --- | --- |
| Noise + gradient, gradient + noise, noise × gradient, gradient × noise | `DensityFunctions$Ap2` | `DensityFunctions$Ap2` |
| Noise ± negative-zero constant, noise × negative-zero constant, noise × 0.5 constant | `DensityFunctions$MulOrAdd` | `DensityFunctions$PureTransformer` |

Numerical analysis of all 1,920 outputs found **exactly seven** differences
from strict eager left-to-right IEEE arithmetic. All seven occur for
`mul_gradient_noise` at **Y=128**, where the *first* varying gradient
returns raw `+0` and the *second* stock noise is negative. Eager IEEE
`(+0)×(negative)` produces `-0` (`0x8000000000000000`);
the actual 26.2 JVM `Ap2` output is `+0`
(`0x0000000000000000`). The other **1,913** records match ordered eager
arithmetic exactly, including both noise/gradient addition orders, all
constant-factor profiles and signed negative zeros.

These observations agree with the earlier genuine **1,280** two-primitive
capture's five gradient×gradient +0 exceptions. However, a capture does
not prove how `Ap2` behaves for all possible nonfinite or dynamic -0
operands, nor that it evaluated/skipped a particular subfunction.
Those cases remain subject to independent delegate source-law review.

## Helve implementation and fast path

`stock_vanilla_mixed_density_262.rs` is a **separate typed layer**, not a
change to the existing eager `StockDensityProgram262` DAG:

- It borrows the previously source-free JVM-bit-qualified registered noise
  leaf and copies a previously qualified Y-only primitive. The caller selects
  `Add` or `Multiply`, and exactly which input is first.
- At COLD construction, it selects a constant `MulOrAdd` vs dynamic
  `Ap2` candidate. For dynamic multiply, a **positive-zero first operand**
  returns +0 before any multiplication. For constant multiplication, it
  preserves the ordinary IEEE multiplication and negative-zero sign.
- The scalar path can skip evaluating noise for a +0 gradient-first multiply.
  The bit-exact 16×16 horizontal plane path can similarly fill +0 with no
  noise sampling, after validating coordinates. The 16³ path reuses the
  existing coherent batched noise sampler and computes exactly 16 Y-only
  primitive values; it matches *output values*, not necessarily the JVM
  delegate's evaluation trace.
- 100% of the new 1,920 independent official raw-bit values must match in
  **both debug and release**. Every 16×16/16³ element is also checked
  against the scalar semantics across Y=128, plus corruption/overflow
  atomicity and one explicit seven-disagreement eager-IEEE regression.
- The Python source-free fixture validator pins the original JSON SHA,
  every method body hash and ten concrete delegates and provides an optional
  `--original-json` revalidation mode. CI tests mutations and the exact
  fixture SHA without shipping the original 483-kB JSON.

This preserves Helve's architecture: no new chunk/world/cache owner, no
per-block heap allocations or registry lookups, and the only specialized
hot path is one for which we now have independent actual JVM outputs.

## Still to prove before terrain is enabled

The mixed parity qualifies **these ten observed shapes only**; it does not
independently prove the full reached `Ap2`/`MulOrAdd` delegate laws or
permit arbitrary nested density graphs. Independent source/VAR/SEM work
still needs to cover the complete stock density `NoiseRouter` dependencies,
caches, interpolation, splines, aquifers, biome selection, surfaces, sections
and actual chunk publication. The PR introduces **no production admission**.

The next highest-leverage target is the exact **stock router density DAG
root/argument and data-binding inventory**, then a bounded stock
`NoiseRouter` output capture and its pure Rust parity gate.
