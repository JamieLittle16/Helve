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
