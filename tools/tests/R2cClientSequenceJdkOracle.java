import java.util.ArrayList;
import java.util.List;
import java.util.LinkedHashMap;
import java.util.Map;
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.CompletionException;
import java.util.concurrent.atomic.AtomicInteger;

/**
 * JDK 25 semantics oracle, NOT an executable copy of Mojang's client.
 *
 * The official 26.2 client bytecode has separately pinned:
 * - Util.sequence: empty/singleton paths and allOf(...).thenApply(...)
 * - Util.lambda$sequence$0: List.stream, map(CompletableFuture::join), toList
 * - the network loader's thenAcceptAsync consumer and registerElements(stream)
 *
 * Here we verify the JDK ordering/error properties of these operations.
 * This does not prove the client executes the exact model on every input:
 * source-bound control flow and known-pack ID binding still require review.
 */
public final class R2cClientSequenceJdkOracle {
    private R2cClientSequenceJdkOracle() {}

    private static <T> CompletableFuture<List<T>> sequence(List<CompletableFuture<T>> inputs) {
        if (inputs.isEmpty()) {
            return CompletableFuture.completedFuture(List.of());
        }
        if (inputs.size() == 1) {
            return inputs.getFirst().thenApply(List::of);
        }
        return CompletableFuture.allOf(inputs.toArray(CompletableFuture[]::new))
                .thenApply(ignored -> inputs.stream().map(CompletableFuture::join).toList());
    }

    private static void check(boolean condition, String detail) {
        if (!condition) throw new AssertionError(detail);
    }

    private static void checkOutOfOrderCompletion(int size) {
        List<CompletableFuture<Integer>> futures = new ArrayList<>();
        for (int i = 0; i < size; i++) futures.add(new CompletableFuture<>());
        CompletableFuture<List<Integer>> completed = sequence(futures);
        for (int i = size - 1; i >= 0; i--) {
            futures.get(i).complete(i);
        }
        List<Integer> results = completed.join();
        check(results.size() == size, "wrong result length " + size);
        List<Integer> published = new ArrayList<>();
        // The client's callback is independently proven to call
        // registerElements(stream); Stream.forEach is the registered method.
        results.stream().forEach(published::add);
        for (int i = 0; i < size; i++) {
            check(results.get(i) == i, "out-of-order sequence at index " + i);
            check(published.get(i) == i, "out-of-order sequential register " + i);
        }
    }

    private static void checkExceptionalCompletion(int size, int failedAt) {
        List<CompletableFuture<Integer>> futures = new ArrayList<>();
        for (int i = 0; i < size; i++) futures.add(new CompletableFuture<>());
        AtomicInteger callbackCalls = new AtomicInteger();
        CompletableFuture<List<Integer>> completed = sequence(futures)
                .thenApply(results -> {
                    callbackCalls.incrementAndGet();
                    return results;
                });
        for (int i = size - 1; i >= 0; i--) {
            if (i == failedAt) futures.get(i).completeExceptionally(new IllegalStateException("invalid"));
            else futures.get(i).complete(i);
        }
        boolean failed = false;
        try {
            completed.join();
        } catch (CompletionException exception) {
            failed = exception.getCause() instanceof IllegalStateException;
        }
        check(failed, "exception must propagate, size=" + size);
        check(callbackCalls.get() == 0, "no successful registration callback on error");
    }

    /**
     * JDK Stream.forEach is not a transaction.  This model mirrors the
     * separately pinned success-side WritableRegistry.register invocation,
     * but intentionally does not instantiate Minecraft or infer its state.
     */
    private static void checkPartialRegistrationOnThrownError(int size, int failedAt) {
        List<Integer> source = new ArrayList<>();
        for (int i = 0; i < size; i++) source.add(i);
        List<Integer> committed = new ArrayList<>();
        IllegalStateException marker = new IllegalStateException("registration failure");
        RuntimeException observed = null;
        try {
            source.stream().forEach(id -> {
                if (id == failedAt) throw marker;
                committed.add(id);
            });
        } catch (RuntimeException exception) {
            observed = exception;
        }
        check(observed == marker, "forEach must propagate the original thrown error");
        check(committed.size() == failedAt,
                "forEach must retain prefix before thrown error at " + failedAt);
        for (int i = 0; i < failedAt; i++) {
            check(committed.get(i) == i, "partial registration prefix reordered");
        }
        // This observable retained prefix is the reason we cannot claim
        // registry rollback from JVM monitorenter/monitorexit alone.
    }

    /**
     * Synthetic *per-entry reported error* model, not a recreation of
     * Mojang's Either type or registration dataflow. The actual client
     * independently pins Either.ifLeft -> WritableRegistry.register and
     * Either.ifRight -> Map.put; source review must still bind their values.
     */
    private static void checkReportedEntryError(int size, int failedAt) {
        List<Integer> source = new ArrayList<>();
        for (int i = 0; i < size; i++) source.add(i);
        List<Integer> committed = new ArrayList<>();
        Map<Integer, Integer> assignedOrdinals = new LinkedHashMap<>();
        Map<Integer, String> reportedErrors = new LinkedHashMap<>();
        source.stream().forEach(id -> {
            if (id == failedAt) {
                reportedErrors.put(id, "decode-error");
            } else {
                assignedOrdinals.put(id, committed.size());
                committed.add(id);
            }
        });
        check(reportedErrors.size() == 1, "per-entry error must be reported once");
        check("decode-error".equals(reportedErrors.get(failedAt)),
              "wrong per-entry error identity");
        check(committed.size() == size - 1, "reported error must not register an entry");
        int position = 0;
        for (int i = 0; i < size; i++) {
            if (i == failedAt) continue;
            check(committed.get(position) == i,
                    "surviving registration order changed");
            check(assignedOrdinals.get(i) == position,
                    "survivor ordinal not dense after reported error");
            check(position == (i < failedAt ? i : i - 1),
                    "a reported missing element must shift later dense IDs");
            position++;
        }
        // Unlike a thrown exception, a reported error does not stop
        // this *modelled* stream; actual Minecraft error-map finalization
        // and whether any registry can be published remain unproven.
    }

    public static void main(String[] args) {
        for (int size : new int[]{0, 1, 2, 3, 4, 66}) {
            checkOutOfOrderCompletion(size);
            for (int failedAt = 0; failedAt < size; failedAt++) {
                checkExceptionalCompletion(size, failedAt);
                checkPartialRegistrationOnThrownError(size, failedAt);
                checkReportedEntryError(size, failedAt);
            }
        }
        System.out.println("JDK 25 future order, thrown registration prefix, "
                + "and reported-entry-error models verified; actual client "
                + "error handling and source/VAR/SEM admission still pending");
    }
}
