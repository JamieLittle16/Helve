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
