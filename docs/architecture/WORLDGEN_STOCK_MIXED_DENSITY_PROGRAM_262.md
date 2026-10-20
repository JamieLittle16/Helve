# Helve — bounded mixed-density program over seed-derived stock noise (26.2)

**Date:** 20 October 2026. **Minecraft:** Java 26.2, protocol 776, DataVersion 4903.

## Scope, evidence and authority

The individual numerical leaves were already implemented and independently
observed against the *real* stock JVM:

- PRs #449–#450: complete first 15 official prepared registered noise states,
  original 1,440 stock JVM outputs, and seed-derived Rust constructor parity.
- PR #451: immutable, one-root keyed noise set and bitwise-equivalent coherent
  16×16 planes / 16³ cells with no hot-path allocations.
- PRs #452–#453: **four genuinely unseen signed world seeds**, sixteen new
  coordinates, all three noise keys and three scaling pairs. All **576**
  independent raw IEEE-754 bits matched the unchanged seed-derived Rust
  construction, in debug and release (2,016/2,016 stock output cases total).
- `density_primitives_262.rs` has an independent official 26.2 capture for
  constant/Y-clamped-gradient leaves; `density_composition_262.rs` has official
  JVM evidence for its **two-primitive** add/multiply shapes only.

This PR creates a **mixed expression substrate** over those independently
qualified leaves. It is *not* independently qualified as
`DensityFunctions.add`, `mul`, a final `NoiseRouter` or terrain. The
existing 26.2 source-observed `Ap2` rule may short-circuit a dynamic
left operand that evaluates to **positive zero**. Thus the new mixed graph
uses **explicit eager IEEE arithmetic** and makes no vanilla-composition
claim. Do not silently route a Minecraft density function through it.

## Design

`StockDensityProgram262<'a, N>` owns an immutable, bounded and validated
straight-line DAG (maximum 32 nodes). A node is a copied integer-block-Y
primitive, a **borrowed** immutable `RegisteredNoiseDensityObserved262`
leaf, or strict ordered `Add`/`Multiply` of already-computed child indices.

Validation is **COLD**, before sampling:

- Empty/oversized programs, cycles, forward dependencies or invalid node
  indices are rejected.
- A reverse reachability walk rejects every disconnected node. Each scalar
  evaluation overwrites fixed `[f64; N]` worker scratch in dependency order
  before reading it. Repeated child references reuse a result *within the
  same coordinate*, never across coordinates without source-validated cache
  semantics.
- The output is the final node. No heap memory, map lookup, source registry,
  dynamic dispatch, RNG mutation, chunk or world ownership is introduced on
  the hot path.
- Plane/cell integer block-coordinate overflow is fully checked **before**
  any output mutation.

The construction preselects single-primitive, single-noise and three-node
noise-plus-primitive arithmetic plans. The fast path delegates directly to
the already bit-qualified batched noise kernel and applies one Y-invariant
primitive value per plane, preserving exact **left/right IEEE operand order**
and signed zeros. For the 16³ mixed cell, this reuses the noise kernel's
one-time X/Z axis preparation and 16 Y-only primitive evaluations rather than
4096 Y-gradient computations. Arbitrary graphs are evaluated through a
fixed-size scalar scratch fallback; no algebraic FMA/reassociation occurs.

## Qualification

- **576/576** independent held-out official JVM bits must pass with a
  *single-noise-node program*, proving the bridge does not change its qualified
  seed-derived noise leaf.
- Mixed noise/Y-gradient 16² and 16³ outputs must compare every `f64::to_bits()`
  against strict ordered scalar arithmetic, including left/right operand
  order, negative seeds, wrapping coordinates and signed zero.
- Multi-noise general expression graphs must reuse dependencies and match
  their explicitly defined eager arithmetic reference (not a stock-JVM
  mixed-composition oracle).
- Malformed DAGs and coordinate overflow must reject without sampling or
  partially mutating output.
- Strict Rust worldgen debug/release CI remains mandatory.

## Next independent semantic frontier

Acquire from stock JVM a **bounded independent mixed-density oracle** for
`DensityFunctions.add` and `mul` on actual
`RandomState.getOrCreateNoise` registered-noise leaves combined with
Y-clamped gradients and constants, including signed zero and dynamic
positive-zero cases. Record actual delegate class and method-body identity,
source fingerprints and evaluation order. Only then implement an
**explicitly named vanilla operation plan** distinct from the eager
substrate where semantics differ.

**Closed gates**:
`world_seed_random_state_bound=false`,
`independent_var_sem_admitted=false`,
`production_worldgen_enabled=false`. No source/JAR/private Atlas data
is included.
