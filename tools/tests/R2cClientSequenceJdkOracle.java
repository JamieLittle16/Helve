import java.util.ArrayList;
import java.util.List;
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

    public static void main(String[] args) {
        for (int size : new int[]{0, 1, 2, 3, 4, 66}) {
            checkOutOfOrderCompletion(size);
            for (int failedAt = 0; failedAt < size; failedAt++) {
                checkExceptionalCompletion(size, failedAt);
            }
        }
        System.out.println("JDK 25 ordered-future and exceptional-completion semantics verified; "
                + "client source/VAR/SEM admission still pending");
    }
}
