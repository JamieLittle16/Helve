# R2C — Saved block-entity presence gate

**Status:** COLD source-presence evidence only. Non-empty block-entity
publication and the enclosing 26.2 chunk-with-light packet remain unadmitted.

## What the import boundary actually guarantees

The selected light-bearing Anvil import now observes `block_entities`
inside the **same** schema-directed, bounded NBT traversal as block
sections, biomes and persisted light. It does not allocate a second
source tree, repeat a chunk decode or retain unqualified NBT as packets.

The resulting `StoredBlockEntityEvidence` has three explicit states:

- `Absent`: no field found; cannot be promoted to empty under an
  unreviewed missing-tag law.
- `ExplicitlyEmpty`: one source list of exactly zero entries.
- `UnhandledEntries { count }`: the saved list contains entries.
  The original payload is bounded-skipped and must not be dropped by
  future packet publication.

The `require_explicitly_empty` guard rejects both missing and
nonempty states. This can be used by a future **selected, proven
empty-block-entity-only** R2C publication profile, once its outer
packet ordering and missing-field semantics are reviewed.

Any malformed or repeated list, wrong non-empty list element type,
nested invalid NBT, or NBT resource-limit failure remains an explicit
import error. A non-empty list also fails **before semantic resident
installation** with an explicit `UnadmittedBlockEntities` error, so
Helve cannot inadvertently represent such a chunk as if its stored
block entities had never existed. The state is carried through the light-enabled
`ImportedChunkWithBiomeLight`, `ImportedChunkWithLight` and
`ImportedStoredChunkWithBiomeLight` transaction results, so COLD
callers need not reparse NBT.

## Explicit limits

This is *not* a block-entity codec, canonical NBT serializer, or a
proof that all chunks in the official representative world are empty.
No live packet ID, block-entity type registry ID, NBT payload, new
resident owner, cached packet graph or R2D worldgen is introduced.

The distinct R2C block-entity VAR/SEM source gate remains open:
review which saved block entities become initial chunk publication
entries, how their position/type/NBT is encoded, and any legitimate
absence or empty default semantics. Until that review, nonempty
entries **must fail closed** at the publication boundary. This
presence mechanism alone confers no Play packet authority.

## Residency-bound source-publication receipt

The complete persisted-biome installation route now has
`install_source_biome_chunk_with_receipt`: it mints
`SourceChunkPublicationReceipt` **only when** the existing single
authoritative directory admits the imported chunk. The legacy installer
delegates to this identical path and returns its original result, so
no second installation mechanism exists.

The small caller-owned receipt retains the exact Anvil header,
three-state block-entity evidence, and the real
dimension/position/generation handle. It is not installed into the
resident world and has no independent revision or cache.

Before projecting the strictly empty-block-entity body, the server
now uses `append_receipt_bound_empty_chunk_body_candidate`.
It resolves the handle through the existing resident directory
(exact dimension + position + generation), rejects a changed semantic
revision, requires explicit-empty source evidence, and derives the
initial snapshot **while holding the verified immutable chunk borrow**.
Stale, unloaded, wrong-dimension, mutated, or absent-list receipts
therefore cannot produce even one candidate byte. A same-position
reload receives a different generation and cannot reuse the old receipt.

Import/world-load regressions cover rejection on mutation, unload,
reincarnation, foreign dimension and missing saved list. Server
regressions exercise genuine imported residency, exact buffered
candidate composition, and the failed-after-mutation path.

This closes the **evidence-to-incarnation linkage** only. The receipt
does not establish the client numeric biome registry, exact 26.2 outer
packet byte contract, source admission of the empty block-entity
list representation, or valid publication timing. There is no live
Play send route. The separate source gates remain mandatory.
