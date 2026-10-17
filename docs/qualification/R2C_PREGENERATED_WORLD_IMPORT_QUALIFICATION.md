# R2C Pregenerated World Import Qualification

Status: **R2C.3 block-state import qualified through genuine official 26.2 save differential; resident install and whole-import performance decision pending**  
Target: **Minecraft: Java Edition 26.2 / DataVersion 4903**  
Architecture: `../architecture/R2C_WORLD_PROJECTION_IMPLEMENTATION.md`  
Execution plan: `../execution/R2C_EXECUTION_PLAN.md`

## Purpose

R2C needs a real Helve-owned semantic world before chunk/light projection can be meaningful. The first
world source is a pinned pregenerated Minecraft 26.2 world; world generation is deliberately not a
prerequisite.

This qualification prevents the cold persistence path from becoming a second live world model or a
permissive generic deserializer. The selected architecture is:

```text
bounded region / separately bounded external bytes
        ↓
validated Anvil framing
        ↓
static ChunkPayloadDecoder boundary
        ↓
bounded schema-directed NBT cursor
        ↓
exact 26.2 block-state semantics
        ↓
static final-section builder
        ↓
(uncommitted imported chunk)
        ↓
future DimensionInstance residency transaction
```

The production path must not become:

```text
bytes -> generic NBT object tree -> Mojang-shaped object graph
      -> second intermediate world model -> live Helve chunk
```

Persisted palette packing, live section storage and network palette encoding are three separate
mechanisms. They must not be collapsed into one representation merely because Mojang uses related
concepts for each.

## Independent oracle

`tools/vanilla_section_extractor.py` remains the independent transparent cold qualification oracle for
pinned vanilla saves. It validates important 26.2 persisted semantics including:

- 4096-byte region sectors and the two-sector Anvil header;
- location-table bounds and overlap rejection;
- inline/external chunk framing;
- gzip, zlib and uncompressed oracle payloads;
- exact `DataVersion == 4903`;
- stored `xPos` / `zPos` agreement with the region slot;
- `sections` as a list of compounds;
- duplicate section-Y rejection;
- block-state palette identity and non-spanning packed-long decoding;
- normalized dense target state IDs.

The Python oracle deliberately uses a generic NBT value representation because transparency matters
more than allocation cost in qualification tooling. Production Rust does **not** share that parser
shape. The permanent differential gate compares normalized semantics rather than parser internals.

The Python extractor currently rejects LZ4-compressed chunks rather than guessing. Rust Anvil framing
recognizes compression ID 4 as metadata, but that recognition is not an admission of LZ4.

## R2C.3A — bounded Anvil and NBT framing

`RegionView`:

- receives already bounded bytes and re-enforces the configured region limit;
- rejects short or non-sector-aligned region images;
- validates all 1024 location entries before exposing chunks;
- rejects header-sector, zero-sector, out-of-file and overlapping allocations;
- uses checked signed region-to-absolute chunk coordinate arithmetic;
- validates stored record length against sector allocation;
- separates the external-payload flag from compression identity;
- never aliases external-record sector padding as payload;
- enforces an explicit inline compressed-payload limit;
- rejects unknown compression identities;
- performs location-table validation without heap allocation;
- contains no input-dependent `expect`/panic path in production framing.

External `.mcc` I/O remains outside `RegionView`. An external record exposes no borrowed bytes from its
allocated region sectors.

`NbtReader` is a zero-copy schema cursor over one already decompressed payload. It:

- rejects truncation and unknown tag IDs;
- validates UTF-8 names/strings;
- rejects negative list/array lengths;
- enforces explicit string/list/array bounds;
- enforces a hard recursion ceiling plus the selected import depth;
- rejects non-empty `TAG_End` lists;
- uses checked length arithmetic;
- exposes borrowed strings and byte arrays;
- bounded-skips irrelevant fields without constructing a generic object tree;
- detects trailing bytes after the admitted root is complete.

## R2C.3B — exact semantic block-state decode

`decode_chunk_block_sections` consumes decompressed NBT in one schema-directed pass. It validates:

- `DataVersion : TAG_Int == 4903`;
- `xPos` / `zPos` against the Anvil-derived expected position;
- `sections : TAG_List<TAG_Compound>`;
- required signed section `Y` and duplicate section-Y rejection;
- `block_states : TAG_Compound` when present;
- non-empty compound block-state palettes;
- a first writer-compatible palette bound of at most 4096 entries;
- palette entry `Name : TAG_String`;
- optional `Properties : TAG_Compound` with string values;
- duplicate property rejection;
- deterministic lexicographic property ordering before semantic resolution;
- fail-closed unknown state identities through the injected `BlockStateResolver`;
- minimum local palette width `max(4, ceil(log2(palette_len)))`;
- 26.2 non-spanning packed-long cell layout;
- exact packed-word count for 4096 cells;
- packed indices remaining inside the resolved palette.

The decoded 4096-cell order is already Helve's frozen observable YZX section order, so no transpose or
layout-conversion pass is required.

The decoder deliberately does **not** select live section storage. `ImportedBlockSectionBuilder` is a
static construction boundary:

- uniform sections can construct directly from one semantic state without allocating 4096 transient
  cells;
- non-uniform sections reuse one caller-owned 4096-cell semantic scratch buffer;
- palette and packed-word scratch capacities are also retained and reused between sections;
- the final/reference section object is constructed before return, not represented as a Mojang-shaped
  intermediate section.

Sections without `block_states` remain represented in the validated stored-section count but emit no
block-bearing section object.

## R2C.3C — complete stored-block transaction

`StoredBlockImporter` binds one cold loading session's:

- payload limits;
- NBT limits;
- statically selected `ChunkPayloadDecoder`;
- semantic `BlockStateResolver`;
- final-section builder;
- reusable section decode scratch.

Per-chunk calls then perform:

```text
RegionView slot
 -> choose inline bytes or separately bounded external .mcc bytes
 -> enforce external compressed-byte bound
 -> static decoder
 -> bounded NBT + exact target semantic decode
 -> final block-section objects
 -> return uninstalled ImportedStoredChunk
```

The returned source timestamp/compression/external flag are diagnostic metadata only; they do not
become live world authority.

The transaction remains atomic with respect to resident state: no `DimensionInstance` mutation occurs
inside this crate, so a late schema/state failure cannot leave a partially installed chunk.

`UncompressedChunkPayloadDecoder` remains the zero-copy reference mechanism for compression ID 3.
The qualified `DeflateChunkPayloadDecoder` candidate admits uncompressed, zlib and gzip through the
same static transaction boundary; LZ4 remains fail-closed. Its compressed path owns one fallibly
allocated reusable output buffer sized to the caller-selected decompressed bound and reuses one
allocation-free DEFLATE state between chunks. Once that buffer is initialized, a chunk decode performs
no codec-side allocation or runtime decoder construction.

Synthetic qualification covers external uncompressed records plus complete inline zlib and gzip
region -> decompression -> NBT -> semantic-section transactions. The same decoder instance is reused
across both compressed wrappers without changing semantic output. Existing static decoder tests prove
that mechanism selection does not alter the transaction shape.

## Compressed-codec admission and hermeticity

Gzip/zlib now have a qualified first production candidate without weakening Helve's hermetic build
boundary. The exact reviewed dependency surface is:

- `miniz_oxide 0.8.9`, `default-features = false`;
- `adler2 2.0.1` as its checksum dependency;
- repository-owned Cargo vendor sources selected through `.cargo/config.toml`;
- exact versions/checksums frozen by `Cargo.lock` and the dependency allowlist;
- no git dependency, SIMD checksum feature or codec-side allocator feature.

The production wrapper calls the safe allocation-free `DecompressorOxide` core directly instead of
miniz's vector or generic streaming convenience APIs. This avoids a per-loader streaming dictionary
and writes decompressed bytes directly into one Helve-owned reusable output slice. The current
single-pass candidate sizes that initialized slice to the caller-selected decompressed bound. An
adaptive smaller retained scratch policy is a future mechanism candidate and must win on whole-import
CPU + memory evidence before replacing this simpler baseline.

Zlib admission requires exact stream consumption and the wrapper's Adler-32 check. Helve owns gzip
framing and validates magic, DEFLATE method, reserved flags, bounded optional extra/name/comment
fields, optional header CRC16, exact raw-DEFLATE consumption, CRC32 and ISIZE. Concatenated members or
hidden trailing compressed bytes are not silently admitted. Output exhaustion fails as a hard
`max_decompressed_bytes` violation, providing a decompression-bomb boundary before NBT parsing.

Hermeticity is permanent qualification, not a one-shot setup fact. The dedicated import workflow
creates a fresh empty `CARGO_HOME` and performs `cargo check` plus `cargo test` with
`--offline --locked`; therefore a missing vendor source or accidental registry dependency fails before
normal cached qualification can mask it. The repository guard and dependency allowlist also remain
active. Existing Helve Cargo aliases are preserved alongside the vendor source replacement.

Codec qualification currently establishes:

- maximum compressed-size enforcement in Anvil/external framing;
- hard decompressed-size enforcement in the decoder;
- exact EOF/trailing-data policy;
- zlib Adler-32 and gzip header/CRC32/ISIZE policy;
- reusable output-state behaviour;
- malformed/truncated/checksum/unsupported-wrapper regressions;
- end-to-end zlib/gzip semantic import on deterministic 26.2 NBT fixtures.

LZ4 remains explicitly unadmitted. Gzip/zlib semantic correctness is additionally exercised by the
genuine official-save differential below. Whole-import target-hardware cost still remains before the
codec/scratch policy is considered production-selected for performance.

## Target block-state resolver

The exact Minecraft Java 26.2 persisted-state resolver is qualified. It is generated from the same
source/runtime-qualified state dataset that defines Helve's dense vanilla-identity `BlockStateId`
universe and therefore does not invent a second numbering scheme.

The generated cold index covers all 32,366 admitted states in 416,665 bytes. Lookup hashes the already
canonicalized saved name/properties without constructing a canonical key string, maps to one generated
candidate, and then performs exact structured name/property verification before returning the existing
`BlockStateId`. Hash equality is indexing only and never semantic authority on hostile input.

The committed table is reproducible from regenerated official 26.2 runtime identities bound to the
frozen source qualification. The dedicated lookup workflow regenerates and byte-verifies the exact
artifact before Rust qualification. Keep this cold index separate from HOT mutation/state-fact tables
so persisted-world compatibility adds no ordinary block-access tax.

## Differential qualification

The permanent differential boundary is documented in `R2C_IMPORT_DIFFERENTIAL.md`.

The synthetic gate compares independent Python and production Rust implementations over sector-aligned
fixtures covering positive/negative coordinates, gzip/zlib/uncompressed records, an external payload,
uniform sections and both four-bit and forced five-bit non-spanning packed palettes. It compares all
4096 cells in every block-bearing section.

The genuine gate then generates an actual overworld with the pinned official Minecraft Java 26.2
server and fixed seed `6842363988700132471`. The same raw `.mca` files are independently decoded by the
Python oracle and the production Rust importer. `Section Corpus Probe` run 373 qualified:

- `4` actual overworld region files;
- `12,696` block-bearing sections;
- `52,002,816` exact semantic cells;
- `81` distinct dense state IDs observed;
- semantic SHA-256 `2b012ebf055e7eecec15ee503aba6103a456bb78fe199a9fe57dac8bc4d7163f`;
- normalized corpus SHA-256 `934b4d641fe016dcd51bebd6cf0dc05566719f6d26275fc3eae3b9e1e213b883` for that generated-save evidence run.

The workflow validates every actual region, including regions with zero oracle block-bearing sections,
so Rust-only extra output cannot hide. It also proves the official runtime state universe still binds
to the committed source-qualified state data and that every compared section/cell belongs to the same
corpus identity.

This closes the block-state real-save differential for the admitted R2C.3 profile. Biome, height/light
and selected block-entity semantics remain later admission work and are not implied by this result.

## Hostile-input qualification

Current deterministic tests cover malformed region allocations, chunk lengths, NBT truncation/lengths,
depth limits, duplicate semantic fields, packed-word counts, out-of-range palette indices, unknown
states, external payload bounds and unadmitted compression.

Before arbitrary external worlds become a supported product feature, add a persistent fuzz/property
corpus for at least:

- region location/length framing;
- NBT skip/length/depth logic;
- decompression boundary;
- block-state palette/packed-data decoding;
- chunk schema state machine;
- generated target state resolver.

Every discovered panic, excessive-resource case or semantic disagreement becomes a minimized permanent
regression fixture.

## Performance qualification

There is deliberately no standalone framing/NBT/palette microbenchmark. The first decision-grade
benchmark begins when this complete transaction exists:

```text
bounded stored chunk
 -> admitted decompression
 -> schema + semantic block-state decode
 -> final selected/reference section construction
 -> LiveChunkCore construction
 -> DimensionInstance installation
```

Measure at minimum:

- chunks/second and whole-chunk service latency;
- p50/p95/p99 and slowest-tail behaviour;
- compressed bytes read and decompressed bytes produced;
- retained bytes per imported chunk;
- allocation count/bytes where measurable;
- bytes copied between stages;
- decoder/section scratch high-water marks;
- multi-region RSS/process effects;
- independent-process direction stability on controlled target hardware.

Hosted timings remain diagnostic. An optimization is accepted only with unchanged semantic digests and
an improved whole transaction without adding architecture tax to resident HOT access.

## Evidence classes

| Evidence | Establishes | Does not establish |
| --- | --- | --- |
| synthetic Rust unit tests | parser/transaction bounds and local schema invariants | real-save parity |
| Python oracle tests | independent persisted-format interpretation | production Rust correctness by itself |
| synthetic cross-language differential | independent agreement on selected real-format packing/compression shapes | naturally emitted writer coverage |
| genuine official-save cross-language differential | normalized block-state semantic agreement on actual 26.2 writer output | biome/light/height/block-entity parity or production throughput |
| hosted whole-import benchmark | harness health / diagnostic direction | target-hardware winner |
| controlled target-hardware run set | reproducible load-cost distribution | automatic mechanism selection |
| decision record | selected production import/decompression mechanism | future validity after a trigger changes |

## Requalification triggers

Re-run affected evidence when any of these changes materially:

- Minecraft target/DataVersion or admitted persisted schema;
- region/NBT/transaction/decompression parser logic;
- source-backed state-ID mapping or generation digest;
- generated persisted-state resolver;
- selected section-construction policy;
- import limits or unsupported-input policy;
- codec source/version/build mechanism;
- differential corpus/generator identity;
- whole-import benchmark workload/harness;
- target hardware/toolchain for a numerical baseline.

## R2C Anvil-to-authoritative-source-receipt composition

The `helve-world-load::import_and_install_anvil_source` COLD
entrypoint now composes existing source-reviewed mechanisms without
creating a second world representation:

1. borrow one already validated `RegionView` and (if required)
   separately bounded external `.mcc` bytes;
2. decode the exact target 4903 blocks, saved quart-biomes and initial
   light in **one** `StoredBlockImporter` transaction using the
   caller's statically selected decoder/section builder and biome
   resolver;
3. require an **explicitly present and empty** saved block-entity
   list for this narrow first-visibility profile, before mutating
   residency;
4. move the decoded sections straight into the authoritative
   `SemanticDimensionInstance` using the existing transactional
   `install_source_biome_chunk_with_receipt`, returning its genuine
   `SourceChunkPublicationReceipt`.

This connection introduces no second NBT pass, retained duplicate
section copy, world directory, target packet dependency or extra
HOT mutation bookkeeping. Incomplete saved evidence and unsupported
block entities never authorize an empty packet entity list.

Hermetic integration tests build actual serialized Anvil sector,
location and chunk-record bytes with schema-correct 4903 NBT and
source-resolved `minecraft:stone`/`minecraft:plains` identities.
They verify a pristine installed source receipt and unchanged
residency after absent empty-entity evidence, a wrong `DataVersion`,
or duplicate chunk admission.

**This is not yet a production world-file traversal or an unmodified
client demo.** These hermetic bytes are not a captured natural Anvil
world. Source-admitted client biome numeric IDs, exact heightmap
predicates, outer chunk publication and the product runtime's region
file enumeration remain separate explicit obligations.

## Bounded selected-region file ingress

`helve-world-load::visit_pregenerated_region` now offers the
production-compiled **COLD filesystem boundary** for an already-selected
finite group of chunks in one pregenerated Anvil region:

- caller supplies the semantic centre/view's selected absolute chunk
  positions, explicit maximum region/inline/external file sizes and
  exact region coordinates; duplicate or foreign positions fail
  before any filesystem access;
- only `world/region/r.<x>.<z>.mca` is opened, read under its explicit
  byte cap and validated once by the established `RegionView` source
  contract; no arbitrary recursive world traversal or guessed chunks;
- a fixed 1024-bit stack bitset preflights duplicate slot positions
  with no hash table or heap allocation;
- one region byte allocation is reused across the entire selected
  group; external `c.<x>.<z>.mcc` bytes are fetched only for
  source records explicitly marked external, under separate bounds,
  and released after each synchronous visitor;
- the callback receives only `SelectedAnvilSource`, the **same**
  caller-borrowed handle accepted by
  `import_and_install_anvil_source` from PR #319;
- malformed headers, missing selected slots, symlinks, oversized
  files and callback failures remain explicit errors. Per-chunk
  semantic admission is transactional; a group of multiple valid
  chunks is **not** claimed to install atomically.

Hermetic filesystem tests cover requested-order callbacks, no region
file re-read, separate external payloads, missing/truncated regions,
unresolved chunk positions, duplicate/foreign requests, and refusal
of linked region files.

The actual live R2B `WorldProjectionReady` route still does
**not** invoke this reader. Its integration with source-bound
Configuration biomes, actual generated heightmap facts and
Play publisher remains gated on independent client-ID and world-wire
VAR/SEM admission. The absence of a second chunk/image owner
and any HOT world cost is deliberate.

## COLD multi-region source selection

`helve-world-load::visit_selected_pregenerated_world` now groups a
caller-owned finite list of absolute chunk positions across signed
Anvil region coordinates. It sorts that source selection **in place**
once by region and chunk coordinates, rejects duplicates before any
filesystem I/O, and calls the existing bounded one-region visitor
once per region group. No hashmap, second source-image owner or
per-tick world scan is added.

This closes the initial-file-selection composition for a pregenerated
spawn view that crosses `r.-1.0.mca`, `r.0.0.mca`, `r.1.0.mca`
or other region boundaries. The COLD import callback remains
responsible for minting authentic source receipts; the separately
implemented `prepare_initial_source_view` then sorts **those**
receipts by client-view distance, before packet publication. File
iteration order is not presumed to equal client publication order.

Unit tests verify signed-region grouping, deterministic ordering,
duplicate preflight before callbacks, and explicit failure for a
missing later region without pretending earlier committed chunks were
rolled back. No implicit world generation or fallback biome IDs are
introduced.

This does **not** select world identity, a player spawn or a
production-loaded biome registry. Source VAR/SEM admission and the
real R2B `WorldProjectionReady` handoff remain separate.

## Gated server first-view import and batch composition

The dormant `helve-server::r2c_disk_first_view` coordinator now
connects the exact 26.2 two-chunk-buffered rounded view law to the
single **canonical** multi-region loader
`helve-world-load::visit_selected_pregenerated_world` introduced
above. No second region-grouping or filesystem reader is installed.

The caller supplies an explicit view centre, admitted view distance
(2 through 32), finite requested positions and separate receipt
storage. `plan_first_view_positions` can construct a nearest-first
candidate request with a caller-selected cap of 1..4096; the request
does not claim the saved chunks exist. The composition preflights
view membership and an empty receipt destination before any I/O;
the established loader rejects duplicates, sorts by signed region
in place, and reads each selected region exactly once.

For every source chunk, the existing `import_and_install_anvil_source`
performs its bounded single-pass block/biome/light decode and
authoritative resident install. Only real current source receipts
enter the caller's collection. After a complete successful import,
`prepare_initial_source_view` independently validates these
receipts, sorts them nearest-first, and returns the ACK-aware batch
state, which sends the source-selected cache centre first.

A hermetic cross-region integration test writes two valid target-4903
Anvil files at `r.-1.0.mca` and `r.0.0.mca`, imports their
neighbouring stored chunks into **one** authoritative dimension,
and proves both source receipts are current and ordered for batching.
Malformed or absent source evidence is never silently manufactured.
If a later region fails after earlier chunks were installed, the
attempt has no batch controller or queued Play bytes; earlier
authoritative resident chunks may remain. This is **not** a
multi-region atomic transaction.

This coordination is still source-gated and not invoked by the live
R2B `WorldProjectionReady` transport. Client registry numeric IDs,
heightmap semantics and complete outgoing world packet admission
remain separate requirements for a stock-client R2C exit.

## Official oracle: disk-backed two-region first-view packet test

The dedicated `R2C Official Heightmap Facts` workflow now runs
`r2c_disk_first_view::tests::source_chunks_from_two_disk_regions_feed_one_nearest_first_batch`
with **actual official 26.2 runtime heightmap facts** for all 32,366
vanilla block states, cross-checked against Helve's independent
generated state-data table.

This extends the earlier structured import-to-packet test across
real, temporary on-disk `r.-1.0.mca` and `r.0.0.mca` files.
`import_disk_first_view` loads the two source-backed saved columns,
sorts receipts nearest-first from the centre, then passes them to the
continuing R2B `ConnectionDriver` with no duplicate egress owner.
The test verifies each emitted framed chunk's signed X/Z, exact
three-map packed heightmap words (16 blocks of stone in every
column), initial cache centre, batch start, batch finish and the
transactional serverbound chunk-batch ACK.

No copied serialized chunk image is kept; the scratch allocation
and original R2B read-scratch pointer remain stable across the
batch. The test asserts that the source-resolved `minecraft:stone`
ID has the expected official non-air/motion/non-leaf/non-fluid facts.
Ordinary hermetic Rust CI still validates the disk/import half
without accepting synthetic heightmap bytes as official.

**This remains a candidate-level integration test**, not stock
client visual proof: the NBT data is serialized by the test rather
than copied from a naturally generated world, the candidate biome
registry count is not an independently client-admitted ordinal
mapping, and world-wire/heightmap VAR/SEM promotion has not occurred.
Live `WorldProjectionReady` publication remains disabled.

## Nine-chunk, four-region retained-driver source qualification

The existing Rust integration fixture now also covers the actual fixed-size
**nine-chunk first view** (not another chunk importer or packet codec).
`nine_disk_chunks_cross_four_regions_and_reach_one_receipted_batch`
creates one valid on-disk 26.2 DataVersion-4903 chunk at each of the nearest
nine positions around the pending R2B teleport at the origin. The positions
cross four signed Anvil region files, including negative X and negative Z.
The fixture shares one bounded region writer with the original two-region
test; source import still goes through
`import_pending_teleport_disk_first_view` and the sole
`SemanticDimensionInstance`. Every minted receipt is resolved against that
same authoritative world before publication tests.

Ordinary hermetic CI checks the nine-file-backed chunk selection, ordered
receipts and zero driver egress before admission. The dedicated Java 25
`R2C Official Heightmap Facts` workflow additionally executes the same
test with the exact official 32,366-state runtime-produced four-bit table.
The test-only `R2cSourceAdmission` then permits the *existing*, already
written publisher to admit a single bounded nine-chunk batch through the
original driver. Its test decoder checks the complete **12-frame** sequence:
signed cache centre, batch start, nine receipt-bound chunk-with-light
bodies in nearest-first order, and batch finish with count nine. It verifies
all three independently encoded source-heightmap maps and a real serverbound
float32 ACK, using the existing transactional ingress handler.

This is end-to-end **Rust source import → original driver** evidence
and does not establish that the official client renders the packets. It
uses explicitly serialized test chunks, not a stock-client-generated
pregenerated save or an official client connection. The production
`R2cSourceAdmission` remains uninhabited. Receiving-client biome
ordinals/known-pack semantics, complete 26.2 per-state heightmap
VAR/SEM, outer Play/batching admission and nine-chunk visual observation
remain independent required gates. This does not qualify a section-storage
production winner or R2D world generation.

## Explicit non-claims at the current R2C.3 boundary

A green current R2C.3 block-state boundary means Helve has:

- bounded Anvil/NBT framing;
- qualified gzip/zlib and zero-copy uncompressed decoding;
- exact generated 26.2 persisted-name/property -> `BlockStateId` resolution;
- direct schema-directed decode toward final/reference section construction;
- synthetic and genuine official-save Python/Rust semantic differential coverage through all imported
  block cells;
- no Mojang-shaped live object graph and no networking dependency in the importer.

It does **not** yet mean a complete arbitrary 26.2 world can be loaded or played.

Still pending:

- final selected/reference section construction wired atomically into `LiveChunkCore` / `DimensionInstance`;
- transactional resident install and load/unload/reload qualification;
- biome import;
- heightmap/light import or recomputation policy;
- block entities;
- whole-import performance baseline and decompression scratch-policy decision;
- arbitrary-world compatibility claim;
- chunk/light network projection.
