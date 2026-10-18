# R2C — bind Play packet numbers to the already-reviewed R0 dispatch law

**Target:** Minecraft Java 26.2, protocol 776, DataVersion 4903.  
**Status:** source-bound **numeric-ID consistency** candidate; **no new
R2C VAR/SEM admission, independent R2C Atlas gate, or live publication**.

## Evidence reuse, not a second packet implementation

This qualification explicitly composes *three existing* proofs:

1. The actual receiving client's **full** `GameProtocols` clientbound
   429-instruction and serverbound 211-instruction registration methods.
   The pinned JVM fingerprints and a branch-free, complete
   `addPacket`/bundle registration count establish the exact order of
   all entries, not merely the five interesting packet fields.
2. The source/bytecode reviewed generic target packet-ID law already
   documented in `SEM-NET-R0-014` and `SEM-NET-R0-015`, with **nine
   previously reviewed R0 VAR records** located through
   `GATE-NET-STATUS-26_2-001`: append to the ordered builder list,
   ordered codec construction, `IdDispatchCodec.Builder` insertion and
   zero-based map-size assignment, VarInt encode/decode, and duplicate
   rejection. These are source statements about generic **protocol
   machinery**, not R0-only assumptions about packet values.
3. The exact SHA/size-checked receiving client's
   `ProtocolInfoBuilder`, `ProtocolCodecBuilder`,
   `IdDispatchCodec` classes and delegates, observed by the existing
   `r2c_client_packet_builder_frontier.py` inspector. All selected
   class and whole-method fingerprints are required to match the
   independently pinned implementation.

`tools/r2c_play_id_law_reuse.py` is a **COLD, read-only composition
checker**, not another Java decompiler or parser. Its two inputs are the
source-free outputs of the already existing Play registration and
builder probes. The `R2C Official Client Play Packet Registry Frontier`
workflow runs both pinned 26.2 client probes and this checker under
Java 25, verifies the nine reviewed VAR identifiers against the actual
version-controlled R0 gate and SEM links, and runs negative tests for
altered registration order, packet direction, bundle position, changed
client method/class fingerprints and stale/missing VAR review records.

## Exact finite packet positions

| Direction | Field | Zero-based position |
| --- | --- | ---: |
| Clientbound Play | CHUNK_BATCH_FINISHED | 11 |
| Clientbound Play | CHUNK_BATCH_START | 12 |
| Clientbound Play | LEVEL_CHUNK_WITH_LIGHT | 45 |
| Clientbound Play | SET_CHUNK_CACHE_CENTER | 94 |
| Serverbound Play | CHUNK_BATCH_RECEIVED | 11 |

The clientbound builder's **bundle delimiter is the actual first
registered codec entry, at position zero**. The serverbound builder
has its own independent ordinal space and **no bundle entry**. No
post hoc minus-one adjustment is permissible. This distinction is
necessary for the source-bound mapping above; the serverbound ACK is
11 and is **not** the clientbound batch-start packet 12.

## Admission boundary

A passing composition check can establish agreement of these **five
candidate numeric IDs** with the reviewed generic packet-ID source
law. It does not independently source-admit the complete *Play*
protocol: no new R2C-specific Atlas VAR record, source gate result,
or selected-client lifecycle SEM is generated. In particular,
this check does **not** establish Configuration known-pack acceptance,
receiving-client biome numeric identities, heightmap predicate
equivalence, initial chunk/light publication ordering, batch
acknowledgement lifecycle, or a rendered stock-client world.

The output explicitly marks
`independent_r2c_atlas_source_gate_passed=false`,
`r2c_play_lifecycle_var_sem_admitted=false`,
`r2c_biome_var_sem_admitted=false`,
`r2c_heightmap_var_sem_admitted=false` and
`production_admitted=false`. All are checked in CI.

A future R2C independent reviewer should **reuse** this nine-method
R0 source gate and the fixed `GameProtocols` evidence instead of
reindexing or reimplementing the packet-numbering system. The new
R2C review obligations are its actual first-Play sender/client
lifecycle and reached delegates, rather than the already-admitted
generic ID codec implementation.

There is no modified production packet constant, hot-path dispatch,
Minecraft source text in Git, new world owner or new network codec.
The production `R2cSourceAdmission` remains uninhabited.
