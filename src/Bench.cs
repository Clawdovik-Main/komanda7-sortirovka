using System;
using System.Diagnostics;
using System.IO;

class Item : IComparable {
    public int Value;
    public int Id;
    public int CompareTo(object other) {
        return Value.CompareTo(((Item)other).Value);
    }
}

class Bench {
    static int[] ReadBin(string file) {
        using (var stream = new FileStream(file, FileMode.Open, FileAccess.Read))
        using (var reader = new BinaryReader(stream)) {
            int n = reader.ReadInt32();
            int[] values = new int[n];
            for (int i = 0; i < n; i++) values[i] = reader.ReadInt32();
            return values;
        }
    }

    static double Median(double[] samples) {
        Array.Sort(samples);
        return samples[(samples.Length - 1) / 2];
    }

    static double TimeSort(int[] values) {
        double[] times = new double[5];
        int[] work = new int[values.Length];
        var clock = new Stopwatch();
        for (int attempt = 0; attempt < 6; attempt++) {
            Array.Copy(values, work, values.Length);
            clock.Restart();
            Array.Sort(work);
            clock.Stop();
            if (attempt > 0) times[attempt - 1] = clock.Elapsed.TotalMilliseconds;
        }
        for (int i = 1; i < work.Length; i++) {
            if (work[i] < work[i - 1]) throw new Exception("csharp sort failed");
        }
        return Median(times);
    }

    static bool StableOk() {
        Item[] items = new Item[400];
        for (int i = 0; i < items.Length; i++) {
            items[i] = new Item();
            items[i].Value = i % 5;
            items[i].Id = i;
        }
        Array.Sort(items);
        for (int i = 1; i < items.Length; i++) {
            if (items[i].Value == items[i - 1].Value && items[i].Id < items[i - 1].Id) return false;
        }
        return true;
    }

    static void Main(string[] args) {
        foreach (string line in File.ReadAllLines(args[0])) {
            if (line.Trim().Length == 0) continue;
            string[] parts = line.Split(new char[] { ' ', '\t' }, StringSplitOptions.RemoveEmptyEntries);
            int[] values = ReadBin(parts[2]);
            double ms = TimeSort(values);
            Console.WriteLine("TIME\tcsharp\t" + parts[0] + "\t" + parts[1] + "\t" + ms.ToString("F4", System.Globalization.CultureInfo.InvariantCulture));
        }
        Console.WriteLine("STABLE\tcsharp\t" + (StableOk() ? "yes" : "no"));
    }
}
