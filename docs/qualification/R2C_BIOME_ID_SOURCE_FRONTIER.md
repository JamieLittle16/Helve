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

## Independent actual-client artifact acquisition (candidate only)

The pinned server-source ZIP does **not** contain the actual stock 26.2
client Configuration listener. To remove that *discovery* blocker without
committing Minecraft binaries, use the separately bounded official launcher
manifest / unobfuscated-class inventory:

```bash
python3 -m unittest discover -s tools/tests -p 'test_r2c_official_client_registry_inventory.py' -v
python3 tools/r2c_official_client_registry_inventory.py \
  --output /tmp/r2c-26.2-client-registry-discovery.json
```

Minecraft 26.2 has **unobfuscated** official client classes and does not
publish a separate `client_mappings` artifact. The disposable downloader
checks the official client JAR's SHA-1/size, records the full SHA-256
**candidate**, and uses Java 25 `javap -p` to enumerate a bounded set of
readable Configuration listener class/method names. The source-free report
also fingerprints the inspected raw classfiles. No client JAR, bytecode
listing or Mojang source is committed or uploaded; the dedicated Actions
workflow uploads only the JSON discovery report. See Mojang's
[removal-of-obfuscation announcement](https://www.minecraft.net/en-us/article/removing-obfuscation-in-java-edition).

This establishes where the **actual receiving-client** method review should
begin. It does **not** inspect the implementation, prove ordered registration,
bind a complete artifact hash into the canonical lock, or authorize the 66 ID
candidate. Complete client-handler bytecode/source inspection, independently
reviewed VAR/SEM and an exact client+known-pack gate remain required.

### Stock-client method-call frontier from unobfuscated bytecode (unadmitted)

The next independent official-client probe inspects **only** the actual
`ClientConfigurationPacketListenerImpl` method bodies for
`handleRegistryData`, `handleConfigurationFinished` and
`handleSelectKnownPacks` via local `javap -c -p`. It records bounded
symbolic invoke targets, opcodes and bytecode offsets (no disassembly,
JAR or source text). Only calls found inside the **named method** qualify
as discovery; unrelated methods and lambdas cannot satisfy the probe.
Missing/duplicate handler declarations, absent symbolic invoke targets or
excessive call sites fail closed.

These are bytecode *call-site candidates* for manual review, not
proof that the delegated code preserves entry order, nor proof that
the client actually assigns the loaded registry IDs. The exact method
descriptors, call-site order, relevant branch/error paths and reached
network-registry registration delegates must be reviewed and admitted
independently before issue #285 can close.

### Receiver-reached client collector (unadmitted)

The observed stock-client `handleRegistryData` implementation passes the
received `packet.registry()` key and `packet.entries()` list directly to
`net.minecraft.client.multiplayer.RegistryDataCollector.appendContents`.
The next independent probe fingerprints the actual official client
`RegistryDataCollector.class` and enumerates a **bounded** set of
collector/content/registry/load methods' invoke sites. This is a fixed
receiver-reached class, not a broad search for calls that happen to
mention registries elsewhere.

The probe is still source-free bytecode *discovery*. A later review must
prove whether the collector preserves the ordered list, how and when the
final builder invokes network loading, any pending known-pack interaction,
and how errors or duplicates are handled; no production ID assignment is
asserted without complete VAR/SEM and independent gate.

### Actual client inner contents collector (unadmitted)

After the verified receiving handler and outer collector call sites, the
exact next delegate is `RegistryDataCollector$ContentsCollector.append`.
The official 26.2 client source-free probe now independently hashes that
nested classfile, verifies its named append method, and records its
bounded symbolic invoke sites. The referenced
`net.minecraft.resources.RegistryDataLoader` classfile is fingerprinted
separately, closing another exact *discovery* identity requirement.

Whether list insertion is lossless/in-order, whether duplicate registries
are rejected or replaced, and how `RegistryDataLoader.load` ultimately
registers the entries **remain independent source-review obligations**.
The probe must never change client-ID or production-admission flags.

### Stock-client selected RegistryDataLoader.load overload (unadmitted)

The observed client `RegistryDataCollector.loadNewElementsAndTags` invokes
`RegistryDataLoader.load(Map, ResourceProvider, List, List, Executor)`.
The source-free official client probe now selects **that exact five-argument
overload**, fingerprinting its signature separately and enumerating only
its symbolic JVM invoke sites. Official bytecode shows it delegates to
a **distinct four-argument loader-factory overload**; the probe now
independently selects that exact overload and inventories its calls too.
Unrelated overloads of `load` and unrelated class methods must not be
used as evidence of the selected path.

This remains discovery of code structure, not review of branches,
exceptions, asynchronous completion, actual list insertion or numeric ID
assignment. Complete VAR/SEM and source gate remain mandatory.
