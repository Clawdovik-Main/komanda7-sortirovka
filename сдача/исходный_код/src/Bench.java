import java.io.IOException;
import java.nio.ByteBuffer;
import java.nio.ByteOrder;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.Arrays;

public class Bench {
    static int[] readBin(String file) throws IOException {
        ByteBuffer buffer = ByteBuffer.wrap(Files.readAllBytes(Path.of(file))).order(ByteOrder.LITTLE_ENDIAN);
        int n = buffer.getInt();
        int[] values = new int[n];
        for (int i = 0; i < n; i++) values[i] = buffer.getInt();
        return values;
    }

    static double median(double[] samples) {
        double[] copy = samples.clone();
        Arrays.sort(copy);
        return copy[(copy.length - 1) / 2];
    }

    static double timeInts(int[] values) {
        double[] times = new double[5];
        int[] work = new int[values.length];
        for (int attempt = 0; attempt < 6; attempt++) {
            System.arraycopy(values, 0, work, 0, values.length);
            long started = System.nanoTime();
            Arrays.sort(work);
            double elapsed = (System.nanoTime() - started) / 1_000_000.0;
            if (attempt > 0) times[attempt - 1] = elapsed;
        }
        for (int i = 1; i < work.length; i++) {
            if (work[i] < work[i - 1]) throw new RuntimeException("java int sort failed");
        }
        return median(times);
    }

    static double timeObjects(int[] values) {
        double[] times = new double[5];
        Integer[] work = new Integer[values.length];
        for (int attempt = 0; attempt < 6; attempt++) {
            for (int i = 0; i < values.length; i++) work[i] = values[i];
            long started = System.nanoTime();
            Arrays.sort(work);
            double elapsed = (System.nanoTime() - started) / 1_000_000.0;
            if (attempt > 0) times[attempt - 1] = elapsed;
        }
        return median(times);
    }

    static boolean stableObjects() {
        final class Item implements Comparable<Item> {
            final int value;
            final int id;
            Item(int value, int id) { this.value = value; this.id = id; }
            public int compareTo(Item other) { return Integer.compare(value, other.value); }
        }
        Item[] items = new Item[400];
        for (int i = 0; i < items.length; i++) items[i] = new Item(i % 5, i);
        Arrays.sort(items);
        for (int i = 1; i < items.length; i++) {
            if (items[i].value == items[i - 1].value && items[i].id < items[i - 1].id) return false;
        }
        return true;
    }

    public static void main(String[] args) throws IOException {
        for (String line : Files.readAllLines(Path.of(args[0]))) {
            if (line.isBlank()) continue;
            String[] parts = line.split("\\s+");
            int[] values = readBin(parts[2]);
            System.out.printf("TIME\tjava_int\t%s\t%s\t%.4f%n", parts[0], parts[1], timeInts(values));
            System.out.printf("TIME\tjava_object\t%s\t%s\t%.4f%n", parts[0], parts[1], timeObjects(values));
        }
        System.out.println("STABLE\tjava_object\t" + (stableObjects() ? "yes" : "no"));
    }
}
