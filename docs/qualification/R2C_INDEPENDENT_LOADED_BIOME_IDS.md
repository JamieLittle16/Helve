# R2C — Independent direct loaded biome numeric ID oracle

**Status:** source-free runtime cross-check candidate; source/SEM admission remains pending.

This probe is separate from the original live network observation (#294).
A disposable Java 25 agent uses JDK reflection to find the running,
SHA-pinned official 26.2 MinecraftServer and its loaded biome registry.
It enumerates **by numeric byId** and verifies the inverse getId and
the resource getKey at every ordinal. No sorted resource list is used to
assign IDs. The class/field/method names are resolved through official Mojang mappings
when distributed. The pinned official 26.2 launcher has **no**
server_mappings entry, so the observer uses the readable official runtime
symbols, the same policy as the existing sealed block-state runtime oracle.
Every class, field and method must independently resolve at runtime; a
missing symbol aborts the probe instead of guessing obfuscated names.

**Independent within one process:** an unrelated minimal offline client
socket simultaneously observes the ordered Configuration registry-data
publication under exactly minecraft:core@26.2. The report is emitted only
if the direct in-memory byId/getId/key table and network ordinals agree in
all 66 positions, match the same frozen resource *set*, and the official
server SHA-256 matches vanilla.lock.toml. Runtime introspection and
packet parsing have distinct code paths, while sharing the same registry
instance, datapack profile and server runtime identity.

The probe's JVM instrumentation is temporary, running only in the CI
oracle subprocess; it does not transform official classes, enter
Helve production, persist any world packet bytes or touch HOT world
code. It deliberately fails closed on reflective identity differences or
mismatched IDs. A source-free JSON result is written under /tmp, and
its authority is still labeled
RUNTIME_CROSSCHECK_PASSED_SOURCE_SEM_ADMISSION_PENDING.

**Remaining admission:** fingerprint-pinned exact 26.2 source evidence for
loaded registry ID allocation, full R1B Configuration entry publication
and client assignment semantics; independent reviewed R2C-BIOMES VAR/SEM
gate; bound runtime pack-profile equivalence. A successful direct runtime
cross-check alone must not close issue #285 or publish a biome numeric ID
table to Helve clients.
