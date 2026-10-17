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
