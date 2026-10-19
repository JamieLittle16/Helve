# R2C 26.2 — 19-method pinned-source first-pass findings

**Evidence status:** source text personally inspected from the 17 October 2026 local
review bundle. This is a **first pass**, not a complete delegation closure,
independent human review, independent Atlas gate, VAR/SEM source admission or
authorization for live Play chunk publication. The later 18 October stock-client
test-only 25-source-chunk visual demonstration **did** render the central 3x3;
the first-pass findings below remain *historical, unadmitted source
evidence* rather than the current runtime status.

**19 October second pass:** a narrow source-free artifact
`vanilla/reviews/network/r2c-outer-envelope-second-pass-source-findings.json`
now confirms the exact direct packet-constructor/write and receiving-field
order for five of these 19 pinned methods. See
`R2C_CHUNK_WIRE_SOURCE_FRONTIER.md` for its explicit reached-delegate
and exception/packet-identity exclusions. Neither first nor second
pass grants independent source VAR/SEM authority.

## Exact provenance and safe retention

The operator generated a local source-rich review artifact from the locked
Minecraft 26.2 source archive using
`tools/r2c_local_final_source_excerpts.py`. The tool matched 10 biome/order
and nine outer-wire/pacing methods against Atlas qualified declarations and
both body and normalized fingerprints before extracting bounded bodies.

* Official archive SHA-256:
  `1e9bca3dff83cd83e7905f8810f1ec9899361fa2dc83fe893bb48beeb04df750`.
* Exact source-free focus JSON SHA-256:
  `68881bbb15f77cefea774551d7f32735ba50dcaa4727960f2245689b751b3ee6`.
* Temporary 19-method source-rich JSON SHA-256:
  `dfb70d1dea37f52bfd41037b7a5d078ff71194ae74198ff4db05a82018a26d9c`.
* Each local excerpt SHA-256 was independently recomputed and matched its
  reported `source_excerpt_sha256`; the focus hash also matched the upload.
* Exact body hashes, local excerpt hashes, index order, numbered observations
  and pending obligations are retained **without Java code** in
  `vanilla/reviews/network/r2c-first-pass-source-free-observations.json`.

The corresponding local JSON is **not committed**. A body hash or local excerpt
digest is an identification anchor; it is not an automatic semantic proof.

## Registry ordering — what the source actually demonstrates

The registry's `register` method rejects duplicate keys/values and appends
each successfully registered holder to `byId`, assigning its position as
the new numeric ID. `byId` reads from this dense list (returning null
out of bounds); `getId` retrieves the reverse index.

The server's registry synchronization sends registry records constructed
by the delegated `RegistrySynchronization.packRegistries`, then network
tags. The Configuration packet codec carries a registry key and a list of
packed entries. The inspected server source **does not alone certify the
entire pack-list order, known-pack content semantics or client receiver**.

For loading, `NetworkRegistryLoadTask.load` walks the received entry list
in order, enqueues independent decode futures in that order, then uses
`Util.sequence` before registering. `Util.sequence` waits for the
futures and collects their results **from the original list sequence**,
rather than by completion order. `RegistryLoadTask.registerElements`
serially walks that stream under a write lock, registering each successfully
decoded entry in order. Invalid entries are collected as loading errors.

Thus the specific ordered registration chain is supported by these excerpts,
including the asynchronous case. It is a sound reason for Helve to retain
the **Configuration-on-the-wire candidate order**, instead of assigning
biome IDs from alphabetical save names. However the actual selected
`minecraft:core@26.2` 66-entry profile and the receiving stock client's
complete numeric-ID/lifecycle law remain **unadmitted**. The 66 keys are a
separate Configuration-image observation, not a source-proved universal
constant. `PalettedContainerFactory.createForBiomes` delegates to its
biome strategy; its global holder-ID behavior is covered by previously
admitted *world-state* rules, not newly asserted here.

## Chunk envelope and incoming decode — first-pass observation

The chunk-with-light packet constructor takes the loaded chunk's X/Z,
constructs inner chunk data and light data (optionally filtered), and the
write method emits two signed, 32-bit coordinates followed by chunk data
and light data in precisely that order. Inner writers have a **separate,
previously admitted seven-method reuse boundary**; the outer packet is
not automatically admitted by that reuse.

The inspected chunk-data *decoder* reads heightmap data, a VarInt section
byte count (rejecting values above 2,097,152), then exactly that many
section bytes, then block-entity records. It is not evidence that every
candidate heightmap value is true or that arbitrary large payloads should
be accepted by Helve's chosen 65,535-byte initial-window policy.

The block-entity decode reconstitutes world X/Z from packed high/low nibbles
and signed chunk coordinates; the initial demo deliberately requires an
empty block-entity list in the selected world. The light decoder reads
four bitsets in the order sky-data, block-data, sky-empty, block-empty,
then sky-layer and block-layer arrays. The exact inner light-writer
laws are checked through the *existing* admitted inner-wire source gate.

## Sender lifecycle and acknowledgement — first-pass observation

`PlayerChunkSender.sendNextChunks` gates sending on the outstanding-window
limit and its rate/quota. A nonempty ready selection produces one batch
start, the selected chunks, and a finished packet containing the count.
`sendChunk` builds the chunk-with-light packet with null light filters.
The source-delegated `collectChunksToSend` selection/readiness semantics
still require review for general worlds.

On acknowledgement the outstanding counter decreases and floors at zero;
the desired-per-tick rate is clamped to 0.01–64, treating NaN as 0.01;
when no batches remain outstanding the quota resets to 1 and the
permitted outstanding maximum becomes 10. These laws match the current
dormant `R2cChunkBatchState` algorithm for the bounded first-window
candidate. Wire packet identities remain separately pinned via the
Play registration order; the *serverbound* batch ACK is **ID 11**, not 12
(the latter is the *clientbound* batch-start ID).

## What must happen before R2C is declared complete

1. Close the actual selected client receiving registry/known-pack numeric
   assignment law, not merely the successful server-source registration
   chain, with the appropriate independent VAR/SEM evidence.
2. Close delegated registry packet packing and any newly reached entry
   materialization; reuse admitted inner chunk/light writers by exact
   fingerprint, not by name alone.
3. Source-qualify the generated 32,366-element per-state heightmap
   predicates and identify the precise three-map input contract.
4. Qualify the outer Play envelope, stock-client chunk-batch lifecycle,
   COLD world source and selected Configuration profile. Exercise the
   independent Atlas gate with all necessary semantic decisions.
5. Only after the checks permit it, construct the `R2cSourceAdmission`
   production capability and connect the already-built publisher to the
   continuing R2B Play session. Prove a nine-chunk pregenerated-world
   demo in an unmodified 26.2 client. R2D worldgen remains separate.

**No official source text has been placed in this document or in the
source-free review report.** Do not mark the unresolved obligations as
admitted merely because the 19 excerpts were hash-validated and read.
