# R2C — verified four-file heightmap predicate review (26.2)

**Date:** 17 October 2026  
**Target:** Minecraft Java 26.2 / protocol 776 / data version 4903  
**Status:** first-pass source inspected; **not** closed delegates, independent
VAR/SEM admission, or permission to activate the live source gate.

## Identity and actual review

The 17 October local operator export contained four whole original-source
texts, each independently checked here by recomputing the SHA-256 of the
uploaded UTF-8 contents against the exporter receipt and the already pinned
source-file hash. No text, bytecode or binary was committed. All four file
hashes and exact source line anchors are in the *source-free* companion:
`vanilla/reviews/network/r2c-heightmap-four-file-source-findings.json`.

Full archive SHA-256:
`1e9bca3dff83cd83e7905f8810f1ec9899361fa2dc83fe893bb48beeb04df750`.

The source supports the following semantics of the exact three `CLIENT`
heightmap types (the two worldgen types and ocean-floor live type are **not**
client heightmap members):

| Sent map | 26.2 ID | Predicate |
| --- | --- | --- |
| WORLD_SURFACE | 1 | State is not air |
| MOTION_BLOCKING | 4 | State blocks motion, **or** state fluid is not empty |
| MOTION_BLOCKING_NO_LEAVES | 5 | Motion condition above, **and** concrete block is not a LeavesBlock |

These are precisely the existing Rust `HeightmapStateProperties` matching
laws and the official runtime oracle's four-bit column state semantics.
The source's column index is `x + z*16` (256 columns); its first-available
height is one above the highest matching block, stored relative to chunk
minimum Y. Helve's descending scan already implements this reference.

## Why solidity cannot be inferred from section counters

The actual `BlockBehaviour.BlockStateBase` implementation establishes
the following dependency path:

1. `initCache` obtains the *block-derived* fluid state, creates the
   collision cache only for a block not marked dynamic shape, then
   computes and stores `legacySolid`.
2. The computed solidity is true if `forceSolidOn` is set. Otherwise
   `forceSolidOff` forces false. With neither override, missing cache
   or empty collision shape gives false. Otherwise the cached shape's
   AABB passes if its size is at least `0.7291666666666666` **or**
   vertical extent is at least `1.0`.
3. `blocksMotion` reads `legacySolid`, but always excludes the
   **COBWEB** and **BAMBOO_SAPLING** block identities first.

The exact AABB size and collision-shape methods are delegate obligations,
not independently reviewed by this four-file source export. Their official
runtime-computed values **already exist** in the SHA-pinned 32,366-byte
candidate. Do not reimplement block-specific geometry in the COLD
projector or infer motion from the existing non-air mutation flag.

## Fluids and leaves

`BlockStateBase.getFluidState` returns a state cached by `initCache`;
the default block behavior returns the empty fluid. The `FluidState`
`isEmpty` method dispatches to its concrete fluid type's `isEmpty`;
this class alone does not establish the concrete implementation.

`LeavesBlock` specifically returns the water source when the leaf state
is `WATERLOGGED`. The non-leaves heightmap excludes *all*
`LeavesBlock` instances even where those blocks have nonempty fluid.
Consequently a waterlogged leaf can contribute to MOTION_BLOCKING but
**cannot** contribute to MOTION_BLOCKING_NO_LEAVES.

To guard this independently of the entire 32,366-byte table, the pure
Rust heightmap predicate now tests **all 16** possible four-bit inputs
with a source-transcribed truth table. This tests combinations not emitted
by the stock registry, so it detects Boolean precedence and leaves
exclusion regressions. Existing official-runtime packet tests continue
to establish that the frozen table reaches correct chunk heightmap words.

## Remaining exact source boundary (do not skip)

The source-free JSON lists the still-delegated proof leads explicitly:
`Fluid.isEmpty` and concrete empty/water implementations;
`VoxelShape.bounds`, `AABB.getSize`, `AABB.getYsize`;
`Block.hasDynamicShape`, block-specific collision-shape calculation
and default property registration; the source-canonical `Blocks`
special-case identities; and block-state `initCache` call/bootstrapping
order. The correct result is to bind those delegates and the official
runtime ID table to independently reviewed VAR/SEM evidence **once**,
not to reverse-engineer 32,366 individual block definitions or duplicate
the original official runtime probe.

Even though exact top-level predicate formulas are now inspected,
these **four file hashes are not Atlas method VAR records** and cannot
be inserted as independent source admission. The client registry numeric
ID/profile gate and outer packet/stock-client lifecycle gate also remain
independent requirements for the first visible R2C world.

**Production `R2cSourceAdmission` stays uninhabited. No HOT path, chunk
writer, network owner, or worldgen architecture is changed by this review.**

## Exact method-level follow-up, not another four-file dump

A narrower official-source/Vanilla Atlas tool,
`tools/r2c_heightmap_delegate_exact_review.py`, now selects the
**directly observed** remaining `Fluid.isEmpty`,
`VoxelShape.bounds`, and `AABB.getSize/getYsize` call sites by exact
qualified owner, method name and arity. It also explicitly attempts
`EmptyFluid.isEmpty`, fluid default-state and state/bootstrap/shape
helpers as **optional** exploratory leads, reporting their absence
instead of guessing a different owner or silently treating an absent
override as semantically identical.

From the repository root, on the machine holding the original official
ZIP and pinned Atlas, run:

```bash
git pull
python3 tools/r2c_heightmap_delegate_exact_review.py \
  --source "$HOME/Documents/mc-source/mc-src.zip" \
  --db .crucible/vanilla/atlas.sqlite \
  --lock vanilla/vanilla.lock.toml \
  --output "/tmp/helve-r2c-heightmap-delegates-$(date +%s).json"
```

The output is **local source-rich** and must not be committed.
Its method records carry the exact Atlas declaration/signature, body and
normalized SHA-256, source line range, bounded body excerpt, hazard
metadata, and resolved/unresolved call inventory. A missing **required**
method, duplicate owner/arity, duplicate ZIP member, changed official
ZIP/Atlas pin or source bound is rejected before output. Each method is
COLD/qualification-only and its admission flags remain false.

An optional method being absent means further exact type/dispatch
investigation is needed. This tool is intentionally *not* a Java type
checker and cannot prove full virtual dispatch to every block-specific
collision shape from names or static call-site metadata. The official
32,366-state runtime oracle supplies the concrete target identity and
value witness; the reviewed source path and independent VAR/SEM
certification remain the separate logical obligations.

The stock-client biome numeric ID/known-pack proof is a separate gate;
do not activate R2C publication based on this heightmap-only report.

## Verified second pass: eleven exact delegates (17 October 2026)

The operator's pinned follow-up extracted **all eleven** exact methods
(four required, seven exploratory; none missing). Every local method
excerpt was independently byte-hashed and matched its receipt. The
local source-rich JSON SHA-256 is
`538f146a9f354c2a4f46fbafa88ac251fb19dedb00553847ff3d25636f355434`.
The source-free reviewed identities, excerpt hashes and **false**
admission flags are retained in
`vanilla/reviews/network/r2c-heightmap-eleven-delegate-first-pass.json`.

The newly resolved *source-visible* laws are:

- `Fluid.isEmpty` returns false in the base implementation;
  `EmptyFluid.isEmpty` returns true. `FluidState.isEmpty()` (from
  the first pass) dispatches to its owner's override. This establishes
  the two named methods, **not** an exhaustive proof that no other
  concrete fluid overrides the method.
- `VoxelShape.bounds` first rejects the empty case; otherwise it
  constructs an AABB from three axis minima and maxima. The actual
  `VoxelShape.isEmpty/min/max` implementations and shape type
  dispatch remain outside these eleven excerpts.
- `AABB.getSize` computes the **arithmetic mean** of the three
  side lengths: `(getXsize()+getYsize()+getZsize())/3.0`.
  It is **not** volume, surface area, maximum span, or a full-block
  predicate. `AABB.getYsize` is `maxY - minY`. Therefore the
  already-inspected vanilla `calculateSolid` threshold depends
  on this mean **or** a separately sufficient vertical span of
  at least 1.0. `getXsize`, `getZsize` and AABB construction
  are the narrow remaining arithmetic delegates.
- `Block.hasDynamicShape` returns its stored flag;
  `Block.registerDefaultState` stores a state; and
  `StateDefinition.getPossibleStates` returns its stored list.
  These getters/setters alone do **not** establish the complete
  cache-initialization epoch or global state-ID registration.
- `Block.isShapeFullBlock` uses a separate cached shape-fullness
  lookup; **do not substitute** it for `calculateSolid()`.
  `Shapes.block` returns a preexisting static shape, without
  proving how that shape was instantiated.
- `Fluid.defaultFluidState` returns an already stored field;
  its initialization and fluid subtype dispatch are not yet proven.

### Next bounded exact-method export

The existing `tools/r2c_heightmap_delegate_exact_review.py` was
**extended**, not duplicated, to append five required direct callees:
`AABB.getXsize`, `AABB.getZsize`, `VoxelShape.isEmpty`,
`VoxelShape.min(Axis)`, `VoxelShape.max(Axis)`; plus two optional
concrete-constructor/override leads. The old eleven selectors retain
their original order and identity. An absent required method fails
closed; an optional missing/ambiguous method remains explicitly open.

Run on the pinned operator machine after updating `main`:

```bash
git pull
python3 tools/r2c_heightmap_delegate_exact_review.py \
  --source "$HOME/Documents/mc-source/mc-src.zip" \
  --db .crucible/vanilla/atlas.sqlite \
  --lock vanilla/vanilla.lock.toml \
  --output "/tmp/helve-r2c-heightmap-delegates-$(date +%s).json"
```

The output is new-only, private, and **source-rich LOCAL ONLY**.
Neither the first-pass review nor this follow-up authorizes
independent VAR/SEM promotion or production chunk publication.
Still needed: complete fluid subtype/registry and shape dispatch,
cache bootstrap/state identity, receiving-client biome IDs,
and independent source admission.

## Verified third pass: 17 exact methods (17 October 2026)

The next operator-local report contains **17 exact source methods**:
the original eleven, five previously reached direct callees, and
the six-argument AABB constructor. All 17 reported excerpt SHA-256
digests independently match the actual received UTF-8 excerpt bytes.
The complete **local-only** report has SHA-256
`e6cf968b6072ce5f9ee814247a829c78e4f77a24a8492dacfd6a7c050aeb1701`
and unchanged official archive pin. A minimal source-free record for
the **six newly reviewed methods**, with per-method body/excerpt hashes,
is retained in `vanilla/reviews/network/r2c-heightmap-seventeen-delegate-review.json`.
The first eleven are reused by reference rather than copied again.

Exact third-pass source laws:

- `AABB.getXsize()` is `maxX - minX`, while `getZsize()`
  is `maxZ - minZ`. Together with the previously reviewed
  Y span and `getSize`, the size is the arithmetic mean of
  all three coordinate differences. This is **not** volume.
- The six-coordinate `AABB` constructor normalizes each axis
  using `Math.min/Math.max`. It does not assume ordered input.
- `VoxelShape.isEmpty()` delegates to its
  `DiscreteVoxelShape.isEmpty()` member, retaining a concrete
  discrete-shape dependency.
- `VoxelShape.min(axis)` uses `firstFull(axis)` and
  `getSize(axis)`; beyond the occupied range it returns positive
  infinity, otherwise the coordinate at `get(axis, i)`.
  `VoxelShape.max(axis)` uses `lastFull(axis)`, returning
  negative infinity when no positive upper occupied position
  is present, otherwise the coordinate at `get(axis, i)`.
  The discrete shape and coordinate helper remain unreviewed.
- `FlowingFluid.isEmpty()/0` was **not** declared in that
  concrete owner in the pinned Atlas. It is an *optional missing
  method*, not a source or extraction failure; the absence of
  that declaration is not a class-hierarchy/override-completeness proof.

### Next: only five new direct delegates

The existing exact-method exporter has been extended with the next
five **required** method identities:
`DiscreteVoxelShape.isEmpty()`,
`DiscreteVoxelShape.firstFull(Axis)`,
`DiscreteVoxelShape.lastFull(Axis)`,
`DiscreteVoxelShape.getSize(Axis)`, and
`VoxelShape.get(Axis,int)`.

To avoid repeatedly exporting the **same seventeen** already
reviewed bodies, select the new subset with `--pending-only`:

```bash
git pull
python3 tools/r2c_heightmap_delegate_exact_review.py \
  --pending-only \
  --source "$HOME/Documents/mc-source/mc-src.zip" \
  --db .crucible/vanilla/atlas.sqlite \
  --lock vanilla/vanilla.lock.toml \
  --output "/tmp/helve-r2c-discrete-delegates-$(date +%s).json"
```

The source/Atlas pin, duplicate and bounds checks still apply.
The selected scope is recorded in the private output and cannot
be confused with an exhaustive extraction. The default mode
continues to extract the full selector set for deliberate
re-verification.

**This is deliberately the last planned arithmetic/voxel helper
review pass for the initial COLD nine-chunk R2C window.** The next
substantive milestone work should concentrate on independent
source-semantic admission of the observed 32,366-state predicate
table, the actual client's biome registry order and the final
world publication/stock-client observation. A chain of helper
reviews must not be treated as an infinite prerequisite for
demonstrating a correctly gated bounded runtime witness; the
remaining global dispatch/bootstrap claims must be stated
explicitly rather than guessed.

No official source text is committed, and no source admission,
Play runtime, HOT path or publisher capability is changed.

## Fourth pass: five discrete-shape source roots, two abstract (17 October 2026)

The operator ran the **five-method `--pending-only`** export against
the same official 26.2 source archive and Atlas. All five exact UTF-8
source excerpts independently matched their SHA-256 receipts. The
private source-rich JSON SHA-256 is
`03dea24f6ae5e56fa89c0cb4873280c13b4cc2e49abe614ff01e27276204caca`.
The complete source-free method identities, body/excerpt hashes and
carefully bounded findings are in
`vanilla/reviews/network/r2c-discrete-shape-five-source-free-findings.json`.
No Java body text is committed.

The inspected code establishes:

- `DiscreteVoxelShape.isEmpty` returns true when the interval is
  empty on **any** axis (`firstFull(axis) >= lastFull(axis)`);
  otherwise it returns false. The first/last methods dispatch into
  implementations, not into code defined in the abstract class.
- `DiscreteVoxelShape.firstFull(Axis)` and `lastFull(Axis)`
  are **abstract declarations**, not executable source bodies.
  Their body fingerprints are both SHA-256(empty). The original
  extractor wrongly emitted `has_source_body=true` because Atlas
  stores that digest rather than NULL; it did **not** demonstrate
  the concrete override bodies. This PR repairs the distinction
  and tests it using the same Atlas empty-body fingerprint.
- `DiscreteVoxelShape.getSize(Axis)` selects the stored
  `xSize/ySize/zSize` using `Direction.Axis.choose`.
  This source alone does not establish the `choose` implementation
  or where those dimensions originate.
- `VoxelShape.get(Axis,int)` retrieves the coordinate from
  `getCoords(axis).getDouble(i)`. Subtype-specific coordinate
  lists and `getCoords` are still unresolved.

These five reviewed *declarations* complete the **bounded top-level
arithmetic-source review**, **not** full polymorphic
shape-dispatch, cache initialization, client-world state equivalence,
or independent VAR/SEM admission.

### Decision: stop recursive arithmetic review and qualify the demo

We already hold an exact twice-reproduced official runtime oracle
for all **32,366** registered states, source-reviewed top-level
heightmap predicates, all three heightmap Boolean laws and
integration evidence for chunk heightmap packing. Completing every
Java collision-shape helper and every block-specific override is
not a prerequisite to *attempt* independent source/semantic
admission of the **bounded official runtime-produced dense state fact
table**. The gate must still qualify the concrete registry ID epoch,
source/probe identity, matching source-law predicates and
state-table completeness and fail closed on any uncertainty.

Next work should prioritize the existing independent gates:

1. Define and independently validate the exact runtime-probe/source
   equivalence contract for the three heightmap predicate bits and
   dense 32,366-state canonical IDs, without guessing dynamic
   dispatch for uninspected blocks.
2. Complete the official **receiving-client** numeric biome
   registry/selected-known-pack VAR/SEM review against the already
   recorded source-free Java 25 branch and lambda-bootstrap evidence.
3. Confirm the outer Play sender/batch/client lifecycle and run
   the real stock-client nine-chunk world demo through the
   *existing* COLD publisher after gates permit it.

**Production publication remains blocked.** There is no source
admission by extrapolation from these abstract declarations.
