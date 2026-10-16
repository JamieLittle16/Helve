# R2C — Loaded biome ID source closure frontier

**Status:** finite declaration discovery only; not a source review or production admission.

Official runtime evidence (#294 and #295) established that the loaded Minecraft
Java 26.2 server's `Registry<Biome>` ordinal table and its Configuration
`registry_data` publication agree exactly on all 66 default known-pack
biomes. The full candidate was frozen in #296. That evidence remains
`RUNTIME_CROSSCHECK_PASSED_SOURCE_SEM_ADMISSION_PENDING`.

The already admitted `GATE-NET-R2C-WORLD-STATE-26_2-001` proves the
biome *container* / palette binding, not **how loaded dynamic biome
numeric IDs are assigned**, nor how the receiving 26.2 client associates
each ordered Configuration key with an ID. Do not extend its status by
implication.

## Focused official-source review

A separate, bounded plan at
`vanilla/reviews/network/r2c-biome-id-source-frontier.json`
contains four distinct non-overlapping proof obligations:

1. Loaded registry insertion and `byId`/`getId` ID allocation;
2. Selected default known-packs branch and ordered Configuration emission;
3. Bound biome paletted-container identity from the loaded registry;
4. Shared network registry reception and ordered registration of the
   serialized entry list, *without* claiming that the actual 26.2
   client Configuration handler is already source-qualified.

### Newly identified common network-receive law (unadmitted)

The pinned official Java 26.2 server-source archive (SHA-256
`1e9bca3dff83cd83e7905f8810f1ec9899361fa2dc83fe893bb48beeb04df750`)
contains shared registry-loading implementations **in addition to**
the server's registry packet emitter:

- `src/net/minecraft/resources/NetworkRegistryLoadTask.java`:
  SHA-256 `dc9d281b179da141bb2faaa3707a58e3a213ce8a837703ee7e6557a6c1b49404`;
- `src/net/minecraft/resources/RegistryLoadTask.java`:
  SHA-256 `64803b037a94786e138723ff9fd9eed7bbfe1313b7fc2499700eb65931e650c2`;
- `src/net/minecraft/core/MappedRegistry.java`:
  SHA-256 `d5351583e7fe0eadb7587ec1ccbb1b0340662dc62cada04a37d6303239d3e86f`;
- `src/net/minecraft/network/protocol/configuration/ClientboundRegistryDataPacket.java`:
  SHA-256 `5fcce02e360a61fefdb057f39067185876030e311804210c23dad3bec7d37409`.

These are raw-file review anchors, **not** verified Atlas
declaration fingerprints or admitted VAR/SEM.

The packet codec serializes an ordered list of packed entries.
`NetworkRegistryLoadTask.load` iterates that list and schedules
per-entry value decoding, then calls `Util.sequence` and
`registerElements`; `RegistryLoadTask.registerElements` registers
the resulting stream sequentially, and `MappedRegistry.register`
assigns each value its current `byId.size()` before insertion.
That suggests a direct network-entry-order → numeric-ordinal law
**conditional on** complete in-order resolution and invocation by
the receiving client.

The review inventory now includes an **exact-name, maximum 16-overload**
Atlas lookup for `net.minecraft.Util#sequence` (a method-scoped
`targeted_methods` entry in the review plan). This avoids inventorying
hundreds of unrelated `Util` methods or weakening the existing
256-method-per-root cap. Its signatures/body fingerprints and hazard leads
are only declaration metadata. A missing, ambiguous or excessive delegate
fails the local review inventory rather than silently dropping this
essential in-order-future-completion proof obligation.

The review must explicitly close `Util.sequence`'s ordering
semantics, any registry rejection/duplicate-error branches, the
packet listener's preparation of the networked registry data and,
critically, the *actual stock client Configuration handler* invoking
this shared loader. The last handler is **not supplied** by this
server-source archive. None of those missing links can be filled by
assuming that server-side classes imply client-side execution.

This expanded discovery directly narrows issue #285, but the status
remains `DISCOVERY_NOT_ADMISSION` and client numeric ID authority
remains **unqualified**.

To prepare source-free declaration fingerprints from the pinned local source
archive and disposable Atlas database, run:

```bash
python3 tools/r2c_biome_id_source_frontier.py \
  --source ~/Documents/mc-source/mc-src.zip \
  --db .crucible/vanilla/atlas.sqlite \
  --lock vanilla/vanilla.lock.toml \
  --output /tmp/helve-r2c-biome-id-source-frontier.json
```

The tool must resolve every named source class exactly once, verify
the official source SHA-256 and Atlas lock, and freeze declaration
signatures and fingerprints with observed hazard leads. The cap is
256 methods per root type, and missing/ambiguous declarations fail.
No official source body/excerpt is emitted or committed.

The inventory's separate `targeted_methods` section identifies only
the exact `Util.sequence` candidate signatures for focused local source
inspection. It does **not** establish that the actual unmodified 26.2
client invokes the common receiver; the server archive cannot close that
last link.

The output always says `source_inspected: false`,
`client_assignment_proven: false` and
`production_admitted: false`. **Atlas metadata is not review.**
The source ZIP itself must remain local.

After the bounded source review, explicitly select the narrow declarations
actually relied upon, close reachable delegates and hazards, produce
reviewed VAR/SEM records, and pass an independent fingerprint-pinned
source gate with provenance. The initial server-only source corpus is
not proof of the client's registry assignment behavior; that requires
separate exact client code/source or equally authoritative evidence.

**Do not** wire the frozen biome fixture into the runtime
`OrderedBiomeRegistry` or 26.2 Play chunk publication until that last
qualification is complete. The first R2C demo continues to rely on
pregenerated world import, not R2D world generation.
