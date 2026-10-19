# R2C — Remaining independent source-review handoff (26.2)

**Status:** Local reviewer preparation, **not source admission**. The previously admitted 58-method world-state gate (PR #268) remains valid and must **not** be repeated.

## Scope

After the real-client 25-source visual demonstration, three independent source obligations still block the ordinary product's uninhabited `R2cSourceAdmission`:

- **Receiving-client biome numeric IDs and selected known-pack ordering:** The pinned server-side registry/Configuration and common ordered-registration declarations have a source-free frontier; the actual stock-client callback/bootstrap/control path must be independently reviewed and bound to the source admission.
- **Per-state heightmap flag semantics:** The complete 32,366-entry official runtime table and digest are already reproducible. The exact predicate delegates—particularly `blocksMotion` / cached collision solidity—still need source review and independent VAR/SEM.
- **Outer chunk/light Play lifecycle:** Packet envelope, block-entity empty-list law, initial light, batch/pacing and source-admitted publication ordering must be independently reviewed. The finite 25-source TCP and client visual tests do not establish source/VAR/SEM admission.

These are **three existing independent tools**, not three new parsers. The orchestration script `tools/r2c_remaining_source_review_bundle.py` runs the existing `r2c_biome_id_source_frontier.py`, `r2c_chunk_wire_source_frontier.py` and `r2c_heightmap_predicate_source_review.py` with one pinned Atlas/source/lock input. Each original tool keeps its own content and identity checks.

## Run on the machine containing the pinned official source ZIP

From the Helve repository root, with Minecraft closed and the pinned Atlas database already prepared:

```bash
cd /home/Jamie/Crucible
git pull --ff-only

STAMP="$(date +%s)"
python3 tools/r2c_remaining_source_review_bundle.py \
  --source "$HOME/Documents/mc-source/mc-src.zip" \
  --db ".crucible/vanilla/atlas.sqlite" \
  --lock "vanilla/vanilla.lock.toml" \
  --source-free-dir "/tmp/helve-r2c-source-free-$STAMP" \
  --private-dir "$HOME/helve-r2c-source-review-PRIVATE-$STAMP"
```

Both directories must be **fresh, distinct, outside the repository**, with real, existing parent directories. They are created mode `0700`, never reused, and the source-free index is created mode `0600`. If an original source tool rejects the archive/Atlas/plan, or any output shape/flag drifts, **no successful final index is emitted**; partial files must not be misrepresented as a completed review.

### Source-free directory — safe review metadata only

- `biome-id-declarations.json`: the original fingerprinted groups and targeted ordered-sequence delegate; its review/production flags remain false.
- `chunk-wire-declarations.json`: the original four typed packet/publication roots, declaration fingerprints, hazards, questions and false authority flags.
- `source-free-review-index.json`: hashes and lengths for both fingerprints, source-archive identity, private review digest/size **but not its path or bytes**, and explicit remaining review obligations and false production-admission fields.

### Private directory — source-rich; never upload or commit

- `heightmap-source-PRIVATE-DO-NOT-SHARE.json`: the original exact pinned four Java predicate source texts. This file **contains Mojang source**. Keep it local and do not share it with GitHub, an issue, a PR or a source-free evidence upload. The index contains no source bodies. Do not upload the whole private directory or combine the two directories.

## Verified source-free operator evidence (18 October 2026)

The first locally generated source-free bundle was inspected by digest
without importing private Mojang source text. Its uploaded archive SHA-256
was `eb078a895641f818ec416ac34c41a1232029c1b85f0c221bde7d526b16cebb52`.
The archive contained exactly the three permitted JSON reports, whose
lengths and SHA-256 values matched its own index:

| Source-free inventory | Bytes | SHA-256 |
| --- | ---: | --- |
| Biome ID declarations | 52,911 | `652ce178d27449cf894ea72e3de79d3fc90062fca5ef4c096a75287c1bc43c47` |
| Chunk/light/Play declarations | 19,694 | `f02742fd0238c60417aab736dd2f9a729fdf149a537fc2881bfaedacdbafede3` |

The biome inventory has **127 methods across eight type roots**, plus
one separately targeted `net.minecraft.util.Util.sequence` overload
(fingerprint `34d09271fc8193617f0d7f9e22b67bd4f79784fa039d1662e19ae3d259cc3901`).
The wire inventory has **44 methods across four type roots**. This is
finite *declaration discovery*, not reviewed Java method semantics.

### Important Atlas no-body classification correction

The first report marked every biome method `declaration_only=false`
because it checked only for a **null** body hash. In fact **23**
declarations had the **SHA-256 of the empty token body**
(`e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`):
22 in `net.minecraft.core.Registry` and one
`RegistryLoadTask.load`. An empty-body digest proves no executable
implementation and **must not count as source-reviewed implementation
evidence**. These declarations still have useful source identity, but
must be followed to their concrete delegates.

The inspector now conservatively sets `declaration_only=true` for
both null and empty-body SHA-256, retaining the original digest.
The bundle verifier rejects an older source-free report that labels
such a declaration as executable. **Regenerate this inexpensive local
source-free bundle after the fix before constructing any later source
review handoff.** The original SHA fingerprints are deliberately
not rewritten or promoted; this historical report remains evidence
of the classification bug and successful source-file identity only.

### Focused review order (do not source-review all 171 methods blindly)

1. **Biome registration/order:** Review concrete
   `MappedRegistry.register/getId/byId`, the network overload of
   `RegistryDataLoader.load`,
   `SynchronizeRegistriesTask.sendRegistries/handleResponse`,
   `PalettedContainerFactory.createForBiomes`,
   `NetworkRegistryLoadTask.load`,
   `RegistryLoadTask.registerElements`, and the separately pinned
   `Util.sequence`. Prove registration order, exception/duplicate
   behavior, selected known packs and actual receiving-client callbacks.
   Declarations from the `Registry` interface are **not** substitutes
   for `MappedRegistry` bodies.
2. **Chunk body and light wire:** Review
   `ClientboundLevelChunkWithLightPacket.write`,
   `ClientboundLevelChunkPacketData.write/getBlockEntitiesTags`,
   and `ClientboundLightUpdatePacketData.write/prepareSectionData`
   plus reached constructors/codecs and the exact zero block-entity
   profile. Reuse the already source-admitted world-state inner
   block/biome/height/light laws; do not redo their 58-method gate.
3. **Send/ACK lifecycle:** Review
   `PlayerChunkSender.sendNextChunks/sendChunk/collectChunksToSend/
   onChunkBatchReceivedByClient` with error cases, rate/window
   semantics, and packet timing relative to the R2B entry boundary.
4. **Heightmap delegate source:** Privately review the four pinned
   local heightmap sources and all reached `blocksMotion`,
   solidity-cache, fluid-state and leaves-type delegates. The exact
   runtime 32,366-state oracle is still *candidate data*, not
   independently reviewed predicate SEM.

The archive and its digests do **not** establish method execution,
branch reachability, actual receiving-client behavior or an independent
gate result. Never construct production `R2cSourceAdmission` from this
document or any of the above inventory hashes.

## Verified post-#401 source-free review (18 October 2026)

The operator reran the three existing source inspectors after #401 and
provided `helve-r2c-post401.tar.gz`. We verified that the archive contains
**exactly** the three expected source-free JSON members, that both inventory
byte lengths and SHA-256 values match `source-free-review-index.json`,
and that the index binds the pinned source archive SHA-256
`1e9bca3dff83cd83e7905f8810f1ec9899361fa2dc83fe893bb48beeb04df750`.
No source-rich Java file was included.

| Audit identity | Verified result |
| --- | --- |
| Uploaded source-free tar.gz SHA-256 | `0954be9b19a499cb20f41402cdc39e7160b9d0150121f1a90e95e40c5f47f045` |
| Biome declaration inventory | 52,888 bytes; `1f463c0ff1144e605053e4e0362bdfb85b08935600fbeebf78622978b588ba03` |
| Chunk wire inventory | 19,694 bytes; `f02742fd0238c60417aab736dd2f9a729fdf149a537fc2881bfaedacdbafede3` |
| Biome source methods | 127 across eight root types; **23** `declaration_only=true`, all SHA256(empty): 22 `Registry` and one `RegistryLoadTask.load` |
| Biome targeted method | One nonempty `net.minecraft.util.Util.sequence(List<CompletableFuture<...>>)` overload; hazard `CONCURRENCY` |
| Outer chunk/light/Play methods | 44 across four root types; zero declaration-only |
| Heightmap local four-file artifact | Reported privately generated, 76,644 bytes, SHA-256 `b4d63be3fd59748b83277a8b3dfd77755f84661e6d6974f71ade1c85d08c552f` (source **not** inspected here) |
| All new source/VAR/SEM and production authority flags | **false**; the old #268 admitted world-state gate remains true |

The previous SHA-256/length pair (52,911 bytes for biome) described the
**pre-#401** classification and remains historical evidence only.
The corrected **52,888-byte** biome report closes the inventory labelling
bug, **not** semantic review. Neither SHA nor a hazard label proves an
execution branch, exception behavior or exact delegate semantics.

### Exact method-scope disposition for the next review

To avoid a second broad 171-method trawl, inspect these *body-fingerprint-
bound* primary roots, and only expand to reached delegates. Digests below
are the first 16 hex characters of the SHA-256 recorded **in the verified
post-#401 inventory**; any future VAR/SEM must bind the **full** digest,
qualified owner, exact overload signature, source lock and hazards.

| Track | Pinned concrete root(s) — body SHA-256 prefix | Required semantic proof, not yet established |
| --- | --- | --- |
| Biome ID allocation | `MappedRegistry.register` `db84c1d045aa4053`; `getId` `0e7e3fa87f368763`; `byId` `6834b6aa6df88167` | Dense ID allocation and duplicate/invalid registration behavior; never substitute the 22 abstract `Registry` interface declarations |
| Selected known packs and Configuration | `SynchronizeRegistriesTask.sendRegistries` `37c0f1be0c2c9a78`; `handleResponse` `4b2cef65c9d1b60f`; `ClientboundRegistryDataPacket.<clinit>` `8a4ff8201f2a585f` | Chosen pack negotiation, insertion/packet list order, codec/dispatch and full error branches; expand to actual serialization delegate |
| Registry-to-palette binding | `RegistryDataLoader.load(Map,...)` `ebfb8faf885bd3f8`; `PalettedContainerFactory.create(RegistryAccess)` `fae7ad93397fd5e6` | Verify same loaded biome registry/order is used by chunk quart-biome palette |
| Client decode and ordered registration | `NetworkRegistryLoadTask.load` `ff9aab1016f44e66`; `RegistryLoadTask.registerElements` `47b4a6fdb2b7989`; `Util.sequence` `34d09271fc819361` | Ordered futures for empty/single/multiple/error cases, no mutation races, actual client listener and lambda callback, duplicate/error outcome. Reuse already-pinned actual **client** bytecode/BootstrapMethods and JDK oracle |
| Chunk packet envelope | `ClientboundLevelChunkWithLightPacket.<clinit>` `1b44c24dfefe344f`; `write` `301b54bda0182b88` | Target 26.2 packet registration/ID, constructor/serializer/decoder field order |
| Chunk payload and empty block entities | `ClientboundLevelChunkPacketData.write` `4aef2d360efc79fc`; `extractChunkData` `ed3c3a556dc02ec3`; `getBlockEntitiesTags` `3b91b0ba4af8e1fa` | Source-qualified selected empty-tag count, map/section payload framing and nonempty-block-entity rejection |
| Initial light | `ClientboundLightUpdatePacketData.write` `c985bb5295297713`; `prepareSectionData` `81b84d2c2f709f2f` | Four mask order, section data counts, selected source-light and decoding behavior; reuse existing admitted inner light SEM |
| Pacing and ACK | `PlayerChunkSender.sendNextChunks` `9d3c4a2790bad34d`; `sendChunk` `e068870637f26c7a`; `collectChunksToSend` `843b1a2817ef75f5`; `onChunkBatchReceivedByClient` `7f168dfb63b21f43` | Exact transaction/window/rate ordering and errors. 25-source TCP backpressure tests provide independent behavior confirmation, **not** source admission |
| Dense state predicates | Private `Heightmap.java`, `BlockBehaviour.java`, `FluidState.java`, `LeavesBlock.java` (existing file digests) | Review the four local source texts and *all reached* solidity/collision-shape delegates; reconcile with the pinned 32,366-entry official runtime candidate; do not infer per-state flags from mutation bits |

**Finish line:** independently source-reviewed full-fingerprint VARs, explicit
SEM decisions, complete reachable error/delegate closure, independent
Atlas/source gate and then a *separate* product change to inhabit
`R2cSourceAdmission`. Do not convert this shortlist or any source-free
inventory into production admission.

## Scoped outer-wire second-pass checkpoint (19 October 2026)

The 19-method source-rich review bundle has now been read a second time
for **five** already extracted packet envelope/receiver methods. Their
complete source-free fingerprints and direct-order observations are in
`vanilla/reviews/network/r2c-outer-envelope-second-pass-source-findings.json`.
The only additional Rust behavioral assertion needed was exact signed
network-endian X/Z and contiguous chunk-data/empty-BE/light spans;
existing tests already covered source receipts, atomic rollback, batch
envelopes and client-visible 25-column integration. The new Python
test rejects source-fingerprint drift, erased delegate obligations,
accidental official source inclusion or premature source admission.

**Still required:** exact signed primitive writer/reader delegates,
outer packet read constructor, selected empty-entity semantics and
actual client packet/ACK lifecycle. This *reduces the field-order
ambiguity* but does **not** close the entire outer packet,
client biome-ID/known-pack or dense state-fact obligations. Do not
reinterpret this checkpoint as independent VAR/SEM gate approval.

## Required next human and independent gate work

Review the private heightmap predicates and reached delegates using the pinned source, together with the **source-free** inventory of biome/packet declarations. Record exact method/delegate source VARs, human-authored semantic rules and explicit hazard closure, including actual receiving-client ordering and error branches—not only identical runtime ordinals or a stock-client screenshot. Then run Helve's independent pinned Atlas/source admission gate. Only **after** that independent gate passes can a separate reviewed product change construct production source admission, enable the existing publisher and repeat the stock-client product test.

The source review bundle intentionally states `operator_semantic_source_review_complete=false`, `independent_source_var_sem_admitted=false`, and `production_chunk_publication_admitted=false`. Never treat generating it as progress on the *semantic* approval itself; it establishes only input identity and review handoff. The 58-method previously admitted world-state material remains independently authoritative.

See [R2C Current State](../execution/R2C_CURRENT_STATE.md), [biome numeric-ID source frontier](R2C_BIOME_ID_SOURCE_FRONTIER.md), [heightmap exact-source closure](R2C_HEIGHTMAP_PINNED_SOURCE_CLOSURE.md), [chunk wire source frontier](R2C_CHUNK_WIRE_SOURCE_FRONTIER.md), and [client registration ordering frontier](R2C_CLIENT_ORDER_SEMANTIC_FRONTIER.md).
