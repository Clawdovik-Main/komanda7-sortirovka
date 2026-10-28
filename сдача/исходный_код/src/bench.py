"""Замер list.sort и проверка устойчивости. Python 3.11+ : Timsort с порядком слияния Powersort."""
import statistics
import struct
import sys
import time


def read_bin(path):
    with open(path, "rb") as handle:
        n = struct.unpack("<i", handle.read(4))[0]
        return list(struct.unpack("<" + "i" * n, handle.read(4 * n)))


def median_ms(values, sort_func):
    times = []
    last = None
    for attempt in range(6):
        work = values[:]
        started = time.perf_counter()
        sort_func(work)
        elapsed = (time.perf_counter() - started) * 1000
        if attempt:
            times.append(elapsed)
        last = work
    if last != sorted(values):
        raise SystemExit("python sort failed")
    return statistics.median(times)


def stable_ok():
    pairs = [{"v": i % 5, "id": i} for i in range(400)]
    pairs.sort(key=lambda item: item["v"])
    for index in range(1, len(pairs)):
        if pairs[index]["v"] == pairs[index - 1]["v"] and pairs[index]["id"] < pairs[index - 1]["id"]:
            return False
    return True


def main():
    manifest = sys.argv[1]
    with open(manifest, encoding="utf-8") as handle:
        rows = [line.split() for line in handle if line.strip()]
    for pattern, size, path in rows:
        values = read_bin(path)
        ms = median_ms(values, lambda work: work.sort())
        print(f"TIME\tpython\t{pattern}\t{size}\t{ms:.4f}", flush=True)
    print("STABLE\tpython\t" + ("yes" if stable_ok() else "no"), flush=True)


if __name__ == "__main__":
    main()
