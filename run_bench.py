"""Готовит одинаковые массивы и запускает встроенные сортировки пяти языков.

Сборка идёт во временной папке с латинским путём: компилятор Java на этой
системе портит кириллицу в аргументах командной строки.
"""
import array
import random
import shutil
import struct
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
RESULTS = ROOT / "results"
WORK = Path(tempfile.gettempdir()) / "team7_ads"
SIZES = (10_000, 100_000, 1_000_000)
PATTERNS = ("random", "sorted", "reversed", "few_unique", "nearly_sorted")


def build_array(pattern, size, rng):
    if pattern == "random":
        return [rng.randrange(0, 1_000_000) for _ in range(size)]
    if pattern == "sorted":
        return list(range(size))
    if pattern == "reversed":
        return list(range(size - 1, -1, -1))
    if pattern == "few_unique":
        return [rng.randrange(0, 10) for _ in range(size)]
    values = list(range(size))
    for index in range(0, size - 1, 50):
        values[index], values[index + 1] = values[index + 1], values[index]
    return values


def write_bin(path, values):
    payload = array.array("i", values)
    with path.open("wb") as handle:
        handle.write(struct.pack("<i", len(values)))
        payload.tofile(handle)


def prepare(data_dir):
    data_dir.mkdir(parents=True, exist_ok=True)
    rng = random.Random(7)
    lines = []
    for size in SIZES:
        for pattern in PATTERNS:
            path = data_dir / f"{pattern}_{size}.bin"
            write_bin(path, build_array(pattern, size, rng))
            lines.append(f"{pattern} {size} {path}")
    manifest = data_dir / "manifest.txt"
    manifest.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return manifest


def compile_all(src, bin_dir):
    bin_dir.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        ["javac", "-encoding", "UTF-8", "-d", str(bin_dir), "Bench.java"],
        check=True,
        cwd=src,
    )
    csc = r"C:\Windows\Microsoft.NET\Framework64\v4.0.30319\csc.exe"
    subprocess.run(
        [csc, "/nologo", "/optimize", "/out:bench_cs.exe", "Bench.cs"],
        check=True,
        cwd=src,
    )
    built = src / "bench_cs.exe"
    shutil.move(str(built), str(bin_dir / "bench_cs.exe"))
    command = (
        'call "C:\\Program Files\\Microsoft Visual Studio\\2022\\Community\\VC\\Auxiliary\\Build\\vcvars64.bat" >nul'
        f' && cl /nologo /EHsc /O2 /std:c++17 /Fe:"{bin_dir / "bench_cpp.exe"}" bench.cpp'
    )
    subprocess.run(command, check=True, shell=True, cwd=src)
    obj = src / "bench.obj"
    if obj.exists():
        obj.unlink()


def run_one(label, command):
    print("RUN", label, flush=True)
    completed = subprocess.run(command, check=True, capture_output=True, text=True, encoding="utf-8")
    if completed.stderr.strip():
        print(completed.stderr, file=sys.stderr)
    return completed.stdout


def main():
    if WORK.exists():
        shutil.rmtree(WORK)
    src = WORK / "src"
    bin_dir = WORK / "bin"
    shutil.copytree(SRC, src)
    manifest = prepare(WORK / "data")
    compile_all(src, bin_dir)
    chunks = [
        run_one("python", [sys.executable, str(src / "bench.py"), str(manifest)]),
        run_one("javascript", ["node", str(src / "bench.js"), str(manifest)]),
        run_one("java", ["java", "-cp", str(bin_dir), "Bench", str(manifest)]),
        run_one("csharp", [str(bin_dir / "bench_cs.exe"), str(manifest)]),
        run_one("cpp", [str(bin_dir / "bench_cpp.exe"), str(manifest)]),
    ]
    text = "".join(chunks)
    RESULTS.mkdir(exist_ok=True)
    (RESULTS / "raw.txt").write_text(text, encoding="utf-8")
    deliver = ROOT / "bin"
    if deliver.exists():
        shutil.rmtree(deliver)
    shutil.copytree(bin_dir, deliver)
    print(text)


if __name__ == "__main__":
    main()
