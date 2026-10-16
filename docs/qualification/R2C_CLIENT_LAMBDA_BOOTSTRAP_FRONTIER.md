# R2C — exact 26.2 client invokedynamic bootstrap-method frontier

**Status: official-client method-handle discovery only.** The runtime biome
ordinal table is NOT source-admitted, VAR/SEM-approved, or available to live
world/chunk publication.

## Why this probe exists

The previous client-side source-free inventories established the exact
receiver-reached route:

1. \`ClientConfigurationPacketListenerImpl.handleRegistryData\` retrieves
   packet registry key and entry list, then calls
   \`RegistryDataCollector.appendContents\`.
2. The inner contents collector calls \`Map.computeIfAbsent\` and
   \`List.addAll\`.
3. Configuration completion leads to \`RegistryDataLoader.load\`; the
   loader schedules \`RegistryLoadTask\` futures and waits for them.
4. \`NetworkRegistryLoadTask.load\` walks packed entries, schedules per-entry
   decode futures in a list, then invokes
   \`net.minecraft.util.Util.sequence\` and \`thenAcceptAsync\`.
5. A candidate network lambda invokes \`registerElements(Stream)\`.
   \`MappedRegistry.register\` contains dense-ID list/index writes.

The remaining connection must not be guessed by sorting method names:
\`invokedynamic\` indices refer to a per-class \`BootstrapMethods\` table,
and that table names the JVM method handle implementing the actual lambda
or method reference. A callback appearing as \`lambda$load$2\` in a class
does not establish that the \`thenAcceptAsync\` call site uses it.

## Exact bounded review

\`tools/r2c_client_bootstrap_frontier.py\` downloads the SHA-1/size-verified
official unobfuscated **26.2 client** JAR only to disposable scratch.
It pins its SHA-256 and three exact classfile SHA-256 candidates:

- \`net.minecraft.resources.NetworkRegistryLoadTask\`:
  \`load\` and \`lambda$load$2\`;
- \`net.minecraft.util.Util\`: \`sequence\` and
  \`lambda$sequence$0\`;
- \`net.minecraft.resources.RegistryDataLoader\`: the
  \`load(LoaderFactory,List,List,Executor)\` overload and
  \`lambda$load$0\`.

For each named method the probe selects **one exact declaration**,
fingerprints its signature, reads only \`javap -v -p -c\` symbol metadata,
and maps every candidate \`invokedynamic\` bytecode offset through its
\`BootstrapMethods\` index to a unique \`LambdaMetafactory\` implementation
handle. The output contains bounded symbolic call shapes, handle kinds and
full handle SHA-256; no original source, classfile, JAR, disassembly or
generated compiled code is retained in Git.

The dedicated GitHub Actions workflow exercises hermetic negative tests
and real Mojang client metadata; its downloadable JSON is ephemeral and
all product authority flags are **forced false**.

## What this still cannot certify

Even a fully resolved lambda bootstrap does not itself prove:

- that \`Util.sequence\` preserves input-list order, including zero and
  singleton cases and exceptional completion;
- that per-entry decoding produces a one-to-one ordered list and
  that the registration callback receives this exact list;
- that \`registerElements\` inserts in that order without parallel mutation,
  including duplicate-key/value/error cases and registration rollback;
- that this receiving-client registry is precisely the one whose IDs
  the Play biome palette uses, under the actual selected known-packs;
- the independently pinned VAR/SEM source review of the exact client and
  shared server source roots.

The server-source Atlas plan also names a distinct
\`net.minecraft.Util\` declaration; the observed official client invokes
\`net.minecraft.util.Util\`. These must not be silently equated.

**Never promote** \`client_numeric_id_assignment_proven\` or
\`production_admitted\` based on discovery-only output. The heightmap
facts/static generation and outer chunk/light/Play wire admission are
separate R2C publication gates.
