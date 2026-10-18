# R2C — exact 26.2 client invokedynamic bootstrap-method frontier

**Status: official-client method-handle discovery only.** The runtime biome
ordinal table is NOT source-admitted, VAR/SEM-approved, or available to live
world/chunk publication.

## Why this probe exists

The previous client-side source-free inventories established the exact
receiver-reached route:

1. `ClientConfigurationPacketListenerImpl.handleRegistryData` retrieves
   packet registry key and entry list, then calls
   `RegistryDataCollector.appendContents`.
2. The inner contents collector calls `Map.computeIfAbsent` and
   `List.addAll`.
3. Configuration completion leads to `RegistryDataLoader.load`; the
   loader schedules `RegistryLoadTask` futures and waits for them.
4. `NetworkRegistryLoadTask.load` walks packed entries, schedules per-entry
   decode futures in a list, then invokes
   `net.minecraft.util.Util.sequence` and `thenAcceptAsync`.
5. A candidate network lambda invokes `registerElements(Stream)`.
   `MappedRegistry.register` contains dense-ID list/index writes.

The remaining connection must not be guessed by sorting method names:
`invokedynamic` indices refer to a per-class `BootstrapMethods` table,
and that table names the JVM method handle implementing the actual lambda
or method reference. A callback appearing as `lambda$load$2` in a class
does not establish that the `thenAcceptAsync` call site uses it.

## Exact bounded review

`tools/r2c_client_bootstrap_frontier.py` downloads the SHA-1/size-verified
official unobfuscated **26.2 client** JAR only to disposable scratch.
It pins its SHA-256 and three exact classfile SHA-256 candidates:

- `net.minecraft.resources.NetworkRegistryLoadTask`:
  `load` and `lambda$load$2`;
- `net.minecraft.util.Util`: `sequence` and
  `lambda$sequence$0`;
- `net.minecraft.resources.RegistryDataLoader`: the
  `load(LoaderFactory,List,List,Executor)` overload and
  `lambda$load$0`.

For each named method the probe selects **one exact declaration**,
fingerprints its signature, reads only `javap -v -p -c` symbol metadata,
and maps every candidate `invokedynamic` bytecode offset through its
`BootstrapMethods` index to a unique `LambdaMetafactory` implementation
handle. The output contains bounded symbolic call shapes, handle kinds and
full handle SHA-256; no original source, classfile, JAR, disassembly or
generated compiled code is retained in Git.

The dedicated GitHub Actions workflow exercises hermetic negative tests
and real Mojang client metadata; its downloadable JSON is ephemeral and
all product authority flags are **forced false**.

## Independently observed exact call-site-to-handle edges

The dedicated official Java 25 client workflow for Minecraft 26.2
successfully resolved these bytecode offsets via the classfile
`BootstrapMethods` table, not by method-name association:

| Root method | Offset | Actual LambdaMetafactory implementation |
| --- | ---: | --- |
| `NetworkRegistryLoadTask.load` | 194 | `REF_invokeVirtual NetworkRegistryLoadTask.lambda$load$2` |
| `Util.sequence` | 63 | `REF_invokeStatic Util.lambda$sequence$0` |
| `Util.lambda$sequence$0` | 6 | `REF_invokeVirtual CompletableFuture.join` |
| `RegistryDataLoader.load(LoaderFactory,...)` | 4 | `REF_invokeStatic RegistryDataLoader.lambda$load$0` |
| `RegistryDataLoader.lambda$load$0` | 113 | `REF_invokeStatic RegistryDataLoader.lambda$load$2` |

The CI script asserts these exact resolved edges fail-closed, rather
than merely printing candidate handles. This verifies the callback
linkage structural fact for the official client artifact, but **does
not authorize** the downstream semantic law: we still need bytecode
branch/exception review and independent source admission.

## Official-client registration success/error consumer chain

After independently resolving the network completion callback, the
stock 26.2 client was probed at the exact downstream
`RegistryLoadTask.registerElements(Stream)` method. The classfile
`BootstrapMethods` confirms:

| Method | Bytecode offset | Confirmed JVM edge |
| --- | ---: | --- |
| `RegistryLoadTask.registerElements` | 9 | `REF_invokeVirtual RegistryLoadTask.lambda$registerElements$0` |
| `RegistryLoadTask.lambda$registerElements$0` | 6 | `REF_invokeVirtual RegistryLoadTask.lambda$registerElements$1` |
| `RegistryLoadTask.lambda$registerElements$0` | 16 | `REF_invokeVirtual RegistryLoadTask.lambda$registerElements$2` |

The precise selected callback call sites, recorded separately from
bootstrap linkage, are:

- `lambda$registerElements$0`: invokedynamic at offsets 6 and
  16, `Either.ifLeft` at offset 11, `Either.ifRight` at offset 21.
- `lambda$registerElements$1`: interface invocation
  `WritableRegistry.register(ResourceKey, Object, RegistrationInfo)`
  at offset 13.
- `lambda$registerElements$2`: `Map.put` at offset 9; no
  `WritableRegistry.register` call site in this method.

These **actual verified Java client call sites** are asserted against
hard-coded offsets, exact opcode kinds and receiver owner names in a
dedicated CI path. A future changed success/error dispatch or a
registration invocation in the error callback fails closed instead of
being treated as compatible. The success method calls the
`WritableRegistry` interface, *not* `MappedRegistry` directly:
concrete receiver/type reachability and its ID allocation still
require separate semantic review. This avoids a false source claim.

This is a necessary success-vs-error dispatch witness, **not** proof
that the `Either` branches always execute without exceptional
interleavings, or that a nonempty error map aborts the final registry,
nor VAR/SEM admission. No source, JAR or disassembly is checked in.

## Callback operand-path candidate and partial-failure model

The already rooted `RegistryLoadTask.lambda$registerElements$0/$1/$2`
methods now have an additional **bounded local operand-construction
witness**, using this same `javap -v -p -c` pass. For each method the
inspector records at most 48 opcode/offset pairs, exact reached
`getfield` identities and the complete method-instruction SHA-256,
without exporting original source, raw instruction operands, method
bodies or disassembly. The official-client workflow independently pins
the three full fingerprints:

| Client callback | Exact official method SHA-256 |
| --- | --- |
| `lambda$registerElements$0` | `428ca10f04d28d66ea7ada23b67f72c7ee819ff87842554e83ef798333cdba55` |
| `lambda$registerElements$1` | `3ceaf249ecfe9c115211442c7a8ce1a18d9f5842a76f3bf2aba3e7b0dda6342e` |
| `lambda$registerElements$2` | `7a8e087f0a776b2f2db35b4622a7e1fbcd2685a074059fefe782475fec5f27d2` |

This closes a bounded **JVM operand provenance** gap. The exact
`$0` instruction sequence loads `PendingRegistration.value:Either`,
creates the left-side `Consumer` and calls `Either.ifLeft`.
Its returned `Either` remains the operand-stack receiver while a
right-side `Consumer` is constructed and `Either.ifRight` is called;
the result is popped. The `$1` success lambda loads
`RegistryLoadTask.registry:WritableRegistry`,
`PendingRegistration.key`, the decoded value (`aload_2`)
and `PendingRegistration.registrationInfo`, then invokes the
`WritableRegistry.register` interface. The `$2` error lambda
loads `RegistryLoadTask.loadingErrors:Map`, the same entry key and
the exception (`aload_2`), then invokes `Map.put`.

These are actual official-client *local* operand constructions and
distinct capture destinations, not a transcribed source-code guess.
They still do **not** independently prove the library's actual
`Either.ifLeft/ifRight` behavior, the concrete `WritableRegistry`
receiver's runtime implementation, order/error effects of entire
registry loading, or that a partially successful registry is refused
at finalization. In particular, method shapes do not prove that
`WritableRegistry.register` dispatches to the separately reviewed
`MappedRegistry` for every relevant client execution.

A separate **JDK 25 conditional failure oracle** in
`tools/tests/R2cClientSequenceJdkOracle.java` now tests two
distinct scenarios at all nonempty lengths 1, 2, 3, 4 and 66
and every possible failing position:

- A sequential `Stream.forEach` callback **throw** leaves the
  previously committed model prefix intact, propagates the error, and
  stops before the suffix. A JVM monitor is not a rollback mechanism.
- A **reported** per-entry error routed to a model map while
  other callbacks continue leaves a dense ordinal table of successful
  entries; every entry *after* the skipped error shifts down by one.
  The model cannot establish whether the actual client permits such
  a registry to finalize.

The latter is a deliberately adversarial **conditional model**:
the actual stock client `Either` values, callback dataflow, error
map processing, and registry finalization remain pending independent
source/SEM review. Neither oracle results nor method-opcode metadata
may inhabit R2C production authority.

## What this still cannot certify

Even a fully resolved lambda bootstrap does not itself prove:

- that `Util.sequence` preserves input-list order, including zero and
  singleton cases and exceptional completion;
- that per-entry decoding produces a one-to-one ordered list and
  that the registration callback receives this exact list;
- that `registerElements` inserts in that order without parallel mutation,
  including duplicate-key/value/error cases and registration rollback;
- that this receiving-client registry is precisely the one whose IDs
  the Play biome palette uses, under the actual selected known-packs;
- the independently pinned VAR/SEM source review of the exact client and
  shared server source roots.

The **old, superseded** Atlas plan named
`net.minecraft.Util`; the current bounded server-source plan and the
official 26.2 client both name `net.minecraft.util.Util`.
This identity correction does **not** establish that the source
declaration is the exact client code path or prove its exceptional,
ordered-completion semantics. Keep actual receiving-client
BootstrapMethods/bytecode verification independent.

**Never promote** `client_numeric_id_assignment_proven` or
`production_admitted` based on discovery-only output. The heightmap
facts/static generation and outer chunk/light/Play wire admission are
separate R2C publication gates.
