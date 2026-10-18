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

## Required next human and independent gate work

Review the private heightmap predicates and reached delegates using the pinned source, together with the **source-free** inventory of biome/packet declarations. Record exact method/delegate source VARs, human-authored semantic rules and explicit hazard closure, including actual receiving-client ordering and error branches—not only identical runtime ordinals or a stock-client screenshot. Then run Helve's independent pinned Atlas/source admission gate. Only **after** that independent gate passes can a separate reviewed product change construct production source admission, enable the existing publisher and repeat the stock-client product test.

The source review bundle intentionally states `operator_semantic_source_review_complete=false`, `independent_source_var_sem_admitted=false`, and `production_chunk_publication_admitted=false`. Never treat generating it as progress on the *semantic* approval itself; it establishes only input identity and review handoff. The 58-method previously admitted world-state material remains independently authoritative.

See [R2C Current State](../execution/R2C_CURRENT_STATE.md), [biome numeric-ID source frontier](R2C_BIOME_ID_SOURCE_FRONTIER.md), [heightmap exact-source closure](R2C_HEIGHTMAP_PINNED_SOURCE_CLOSURE.md), [chunk wire source frontier](R2C_CHUNK_WIRE_SOURCE_FRONTIER.md), and [client registration ordering frontier](R2C_CLIENT_ORDER_SEMANTIC_FRONTIER.md).
