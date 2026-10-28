"use strict";
const fs = require("fs");

function readBin(file) {
  const buf = fs.readFileSync(file);
  const n = buf.readInt32LE(0);
  const values = new Array(n);
  for (let i = 0; i < n; i++) values[i] = buf.readInt32LE(4 + i * 4);
  return values;
}

function median(samples) {
  const copy = samples.slice().sort((a, b) => a - b);
  return copy[(copy.length - 1) >> 1];
}

function timeSort(values) {
  const times = [];
  let last = null;
  for (let attempt = 0; attempt < 6; attempt++) {
    const work = values.slice();
    const started = process.hrtime.bigint();
    work.sort((a, b) => a - b);
    const elapsed = Number(process.hrtime.bigint() - started) / 1e6;
    if (attempt) times.push(elapsed);
    last = work;
  }
  for (let i = 1; i < last.length; i++) {
    if (last[i] < last[i - 1]) throw new Error("js sort failed");
  }
  return median(times);
}

function stableOk() {
  const pairs = [];
  for (let i = 0; i < 400; i++) pairs.push({ v: i % 5, id: i });
  pairs.sort((a, b) => a.v - b.v);
  for (let i = 1; i < pairs.length; i++) {
    if (pairs[i].v === pairs[i - 1].v && pairs[i].id < pairs[i - 1].id) return false;
  }
  return true;
}

const rows = fs.readFileSync(process.argv[2], "utf8").trim().split(/\r?\n/);
for (const line of rows) {
  const [pattern, size, file] = line.split(/\s+/);
  const ms = timeSort(readBin(file));
  console.log(`TIME\tjavascript\t${pattern}\t${size}\t${ms.toFixed(4)}`);
}
console.log("STABLE\tjavascript\t" + (stableOk() ? "yes" : "no"));
