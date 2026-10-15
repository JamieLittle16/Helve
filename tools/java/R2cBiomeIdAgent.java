// Temporary, out-of-process Java 25 instrumentation of a SHA-pinned official server.
// This probe never changes Minecraft classes or Helve's live world representation.
// All target symbol strings are substituted from pinned official server mappings.
import java.lang.instrument.Instrumentation;
import java.lang.reflect.*;
import java.nio.charset.StandardCharsets;
import java.nio.file.*;
import java.util.*;

public final class R2cBiomeIdAgent {
    private static final String SERVER_CLASS = "@SERVER_CLASS@";
    private static final String REGISTRIES_CLASS = "@REGISTRIES_CLASS@";
    private static final String BIOME_FIELD = "@BIOME_FIELD@";
    private static final String REGISTRY_CLASS = "@REGISTRY_CLASS@";
    private static final String SERVER_ACCESS = "@SERVER_ACCESS@";
    private static final String BY_ID = "@BY_ID@";
    private static final String GET_ID = "@GET_ID@";
    private static final String GET_KEY = "@GET_KEY@";
    private static final int EXPECTED_BIOMES = 66;
    private static final int MAX_BIOMES = 65536;

    private R2cBiomeIdAgent() {}

    public static void premain(String output, Instrumentation instrumentation) {
        if (output == null || output.isBlank()) {
            throw new IllegalArgumentException("explicit fresh oracle output path required");
        }
        System.err.println("HELVE_BIOME_ID_ORACLE_START");
        Thread observer = new Thread(() -> run(output), "Helve biome-ID observation");
        observer.setDaemon(true);
        observer.start();
    }

    private static void run(String destination) {
        try {
            // The official MinecraftServer is the Runnable held by the vanilla
            // server thread. This is JDK introspection, independent of the
            // Configuration registry_data packet path.
            Field holder = Thread.class.getDeclaredField("holder");
            holder.setAccessible(true);
            Field runnable = holder.getType().getDeclaredField("task");
            runnable.setAccessible(true);
            long deadline = System.nanoTime() + 45_000_000_000L;
            boolean reportedTask = false;
            boolean reportedNullRegistry = false;
            while (System.nanoTime() < deadline) {
                for (Thread thread : Thread.getAllStackTraces().keySet()) {
                    if (!thread.getName().equals("Server thread") || !thread.isAlive()) {
                        continue;
                    }
                    Object task = runnable.get(holder.get(thread));
                    if (task == null) {
                        if (!reportedTask) {
                            System.err.println("HELVE_BIOME_ID_ORACLE_TASK|null");
                            reportedTask = true;
                        }
                        continue;
                    }
                    if (!reportedTask) {
                        System.err.println("HELVE_BIOME_ID_ORACLE_TASK|" + task.getClass().getName()
                            + "|synthetic=" + task.getClass().isSynthetic());
                        for (Field captured : task.getClass().getDeclaredFields()) {
                            if (!Modifier.isStatic(captured.getModifiers())) {
                                captured.setAccessible(true);
                                Object value = captured.get(task);
                                System.err.println("HELVE_BIOME_ID_ORACLE_CAPTURE|"
                                    + captured.getName() + "|"
                                    + (value == null ? "null" : value.getClass().getName()));
                            }
                        }
                        reportedTask = true;
                    }
                    ClassLoader loader = task.getClass().getClassLoader();
                    Class<?> serverClass = Class.forName(SERVER_CLASS, false, loader);
                    Object server = findCapturedServer(task, serverClass, 3);
                    if (server == null) {
                        continue;
                    }
                    try {
                        String report = inspect(server, loader);
                        if (report == null && !reportedNullRegistry) {
                            System.err.println("HELVE_BIOME_ID_ORACLE_PENDING|registry lookup returned null");
                            reportedNullRegistry = true;
                        }
                        if (report != null) {
                            // Never overwrite or update an existing evidence file.
                            Files.writeString(
                                Path.of(destination), report, StandardCharsets.UTF_8,
                                StandardOpenOption.CREATE_NEW, StandardOpenOption.WRITE
                            );
                            System.err.println("HELVE_BIOME_ID_ORACLE_OK|" + EXPECTED_BIOMES);
                            return;
                        }
                    } catch (InvocationTargetException ex) {
                        // Registry may not be ready while the official server
                        // performs asynchronous world initialization.
                        Throwable cause = ex.getCause();
                        if (!(cause instanceof IllegalStateException)) {
                            throw ex;
                        }
                    }
                }
                Thread.sleep(200);
            }
            System.err.println("HELVE_BIOME_ID_ORACLE_ERROR|runtime registry unavailable before deadline");
        } catch (Throwable error) {
            System.err.println("HELVE_BIOME_ID_ORACLE_ERROR|" + error);
            error.printStackTrace(System.err);
        }
    }

    private static Object findCapturedServer(Object candidate, Class<?> serverClass, int depth)
            throws ReflectiveOperationException {
        if (candidate == null) {
            return null;
        }
        if (serverClass.isInstance(candidate)) {
            return candidate;
        }
        if (depth == 0) {
            return null;
        }
        // MinecraftServer.spin captures a java.util.concurrent.AtomicReference
        // in the Runnable handed to "Server thread". Its get() gives the
        // same actual server object without mutation or heap inspection.
        if (candidate instanceof java.util.concurrent.atomic.AtomicReference<?> reference) {
            return findCapturedServer(reference.get(), serverClass, depth - 1);
        }
        // The 26.2 runtime's Server thread uses a captured Runnable lambda.
        // Inspect *only* its bounded, non-static captured fields and stop at
        // the first actual MinecraftServer instance. Do not enumerate heaps,
        // install runtime patches or retain the object outside this probe.
        // Hidden lambda classes are not guaranteed to carry the Java
        // synthetic flag. Restrict traversal by the exact official server
        // classloader instead, and keep a hard recursion cap.
        if (candidate.getClass().getClassLoader() != serverClass.getClassLoader()) {
            return null;
        }
        for (Field field : candidate.getClass().getDeclaredFields()) {
            if (Modifier.isStatic(field.getModifiers())) {
                continue;
            }
            field.setAccessible(true);
            Object nested = field.get(candidate);
            Object server = findCapturedServer(nested, serverClass, depth - 1);
            if (server != null) {
                return server;
            }
        }
        return null;
    }

    private static Method method(Object owner, String name, Class<?> parameter)
            throws ReflectiveOperationException {
        for (Method candidate : owner.getClass().getMethods()) {
            if (!candidate.getName().equals(name)) {
                continue;
            }
            if (parameter == null && candidate.getParameterCount() == 0) {
                return candidate;
            }
            if (parameter != null && candidate.getParameterCount() == 1
                    && (candidate.getParameterTypes()[0].isAssignableFrom(parameter))) {
                return candidate;
            }
        }
        throw new NoSuchMethodException(owner.getClass().getName() + "." + name);
    }

    private static Object lookupRegistry(Object registryAccess, Object key, Class<?> registryClass)
            throws ReflectiveOperationException {
        Object match = null;
        for (Method candidate : registryAccess.getClass().getMethods()) {
            if (candidate.getParameterCount() != 1
                    || !candidate.getParameterTypes()[0].isInstance(key)) {
                continue;
            }
            // Do not rely on a guessed source-level lookup method identity:
            // structurally require that exactly one method yields the expected
            // Registry<T>, not some unrelated resource or holder lookup.
            Object result;
            try {
                result = candidate.invoke(registryAccess, key);
            } catch (InvocationTargetException | IllegalArgumentException error) {
                continue;
            }
            if (result instanceof Optional<?> optional) {
                result = optional.orElse(null);
            }
            if (result == null || !registryClass.isInstance(result)) {
                continue;
            }
            if (match != null && match != result) {
                throw new IllegalStateException("ambiguous loaded biome registry lookup");
            }
            match = result;
        }
        return match;
    }

    private static String inspect(Object server, ClassLoader loader)
            throws ReflectiveOperationException {
        Class<?> registries = Class.forName(REGISTRIES_CLASS, false, loader);
        Field field = registries.getField(BIOME_FIELD);
        Object key = field.get(null);
        if (key == null) {
            return null;
        }
        Object access = method(server, SERVER_ACCESS, null).invoke(server);
        if (access == null) {
            return null;
        }
        Class<?> registryClass = Class.forName(REGISTRY_CLASS, false, loader);
        Object registry = lookupRegistry(access, key, registryClass);
        if (registry == null) {
            return null;
        }
        Method byId = method(registry, BY_ID, int.class);

        StringBuilder buffer = new StringBuilder(2560);
        Set<String> seen = new HashSet<>();
        for (int id = 0; id <= EXPECTED_BIOMES; id++) {
            Object biome = byId.invoke(registry, id);
            if (id == EXPECTED_BIOMES) {
                if (biome != null) {
                    throw new IllegalStateException("loaded registry has extra ordinal 66");
                }
                break;
            }
            if (biome == null || id >= MAX_BIOMES) {
                throw new IllegalStateException("missing loaded biome at ordinal " + id);
            }
            Method getId = method(registry, GET_ID, biome.getClass());
            Method getKey = method(registry, GET_KEY, biome.getClass());
            int reverse = ((Number) getId.invoke(registry, biome)).intValue();
            if (reverse != id) {
                throw new IllegalStateException("registry getId/byId disagreement at " + id);
            }
            Object resourceKey = getKey.invoke(registry, biome);
            if (resourceKey == null || !seen.add(resourceKey.toString())) {
                throw new IllegalStateException("missing or duplicate biome resource key " + id);
            }
            buffer.append(id).append('\t').append(resourceKey).append('\n');
        }
        if (seen.size() != EXPECTED_BIOMES) {
            throw new IllegalStateException("loaded biome registry cardinality mismatch");
        }
        return buffer.toString();
    }
}
