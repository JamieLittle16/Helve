# R2C — Loaded 26.2 biome ordinal observation

**Status: runtime-observed candidate only. No production numeric-ID authority.**

Issue #285 cannot be closed using alphabetical resource keys, world-save palettes,
or the official datagen static-registry report. This bounded Python harness
launches the SHA-locked official Java 26.2 server with a disposable vanilla
world and reads the *loaded* `minecraft:worldgen/biome` registry through the
actual online Configuration `registry_data` publication. The test process
acts only as a minimal offline-login protocol observer; it does not replay
world packets, modify the server runtime or create Helve world-generation code.

The observer performs the exact 776 Handshake and offline/uncompressed Login,
acknowledges the Login boundary, accepts only the selected default
`minecraft:core@26.2` known packs, observes 29 unique registry-data
packets and the terminating update-tags packet, then extracts all 66 biome
names in network order. Input is bounded by frame length, packet count, UTF-8
limits and timeouts. It checks the official server SHA-256 from
`vanilla/vanilla.lock.toml` and compares the complete observed biome
key *set* with the independently frozen Mojang datagen resource inventory.
It **never** sorts the observed order.

Running the dedicated CI workflow emits a *source-free* JSON candidate
under `/tmp` and the ordinal-to-key mapping in the job log. The output
explicitly says `RUNTIME_OBSERVED_SOURCE_ADMISSION_PENDING`. This is not
the independently reviewed loaded-registry ID oracle, does not establish
protocol wire-law/source/SEM admission, and must not be fed to
`OrderedBiomeRegistry` for production publication yet. In particular,
a single live Configuration capture cannot substitute for an independent
loaded-registry enumeration under the exact matching datapack profile.

Next: verify the independently loaded runtime registry numeric IDs against
this ordered Configuration observation; bind the source declaration and
client registry assignment semantics to reviewed VAR/SEM records, freeze
reproducible digest and only then enable 26.2 biome ordinals for R2C.
