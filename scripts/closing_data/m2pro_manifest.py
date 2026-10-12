#!/usr/bin/env python3
"""Emit a committable MANIFEST of the M2 Pro lane's built baseline embeddings.

The embeddings.parquet files live under gitignored output/ (multi-GB), so this
records the durable RESULT provenance instead: per built cell, the embeddings
row-count + byte-size + windowing provenance + leak-marker presence. Re-runnable
and deterministic (sorted) so it produces clean incremental diffs as cells land.

Cheap by design: parquet row-count is a footer read (not a full-file read),
size is stat() — no heavy I/O on the flaky external SSD. (sha256 is intentionally
NOT computed here; add it later on a stable disk if byte-level regen-verification
is needed.)

Usage:  PYTHONPATH=src .venv/bin/python scripts/closing_data/m2pro_manifest.py
Writes: docs/studies/closing_data/M2PRO_MANIFEST.md  (+ .json)
"""
from __future__ import annotations

import json
import os
from pathlib import Path

import pyarrow.parquet as pq

REPO = Path(__file__).resolve().parent.parent.parent
# Scan root is overridable so a git WORKTREE (whose own output/ is empty) can point at
# the MAIN repo's output where the deliverables actually live (e.g. the A40 lane runs the
# worktree's script against /home/.../PoiMtlNet/output via MANIFEST_OUTPUT_ROOT).
OUT = Path(os.environ.get("MANIFEST_OUTPUT_ROOT", str(REPO / "output")))
DOCS = REPO / "docs" / "studies" / "closing_data"


def rows(p: Path) -> int:
    try:
        return pq.ParquetFile(p).metadata.num_rows
    except Exception as e:
        return -1


def prov(cell_dir: Path) -> dict:
    j = cell_dir / "next_build_provenance.json"
    out = {}
    if j.exists():
        try:
            d = json.loads(j.read_text())
            out["stride"] = d.get("stride")
            out["min_seq"] = d.get("min_sequence_length")
            out["emit_tail"] = d.get("emit_tail")
        except Exception:
            pass
    out["leak_marker"] = (cell_dir / "LEAK_MARKER.txt").exists()
    return out


def collect():
    cells = []
    # B2c — per-state (fold-independent), under its own engine dir.
    for emb in sorted((OUT / "baseline_b2c_onehot64").glob("*/embeddings.parquet")):
        st = emb.parent.name
        cells.append({"baseline": "b2c_onehot64", "state": st, "seed": "-", "fold": "-",
                      "rows": rows(emb), "size_mb": round(emb.stat().st_size / 1e6, 1),
                      **prov(emb.parent / "input")})
    # b2b / ctle / poi2vec — per (state, seed, fold) under board_baselines.
    for emb in sorted((OUT / "board_baselines").glob("*/*/s*_f*/embeddings.parquet")):
        cell = emb.parent
        baseline = cell.parent.parent.name
        state = cell.parent.name
        sf = cell.name  # s<seed>_f<fold>
        seed = sf.split("_")[0][1:]
        fold = sf.split("_")[1][1:]
        cells.append({"baseline": baseline, "state": state, "seed": seed, "fold": fold,
                      "rows": rows(emb), "size_mb": round(emb.stat().st_size / 1e6, 1),
                      **prov(cell)})
    return cells


def main():
    cells = collect()
    # MERGE with the committed manifest so cells built on ANOTHER box are preserved
    # (the Mac lane's parquets aren't present on the A40 box and vice-versa). The local
    # scan is authoritative for cells present locally; remote-only cells are carried over.
    def key(c):
        return (c["baseline"], c["state"], str(c["seed"]), str(c["fold"]))
    local_keys = {key(c) for c in cells}
    existing = DOCS / "M2PRO_MANIFEST.json"
    if existing.exists():
        try:
            for c in json.loads(existing.read_text()):
                if key(c) not in local_keys:
                    cells.append(c)
        except Exception:
            pass
    cells.sort(key=key)
    # counts per (baseline, state)
    counts = {}
    for c in cells:
        counts.setdefault((c["baseline"], c["state"]), 0)
        counts[(c["baseline"], c["state"])] += 1

    (DOCS / "M2PRO_MANIFEST.json").write_text(json.dumps(cells, indent=1, sort_keys=True))

    lines = ["# M2 Pro lane — BUILT-ARTIFACT MANIFEST (auto-generated)",
             "",
             "> Durable record of built baseline embeddings (the parquets are gitignored under",
             "> `output/`). Regenerate with `scripts/closing_data/m2pro_manifest.py`. All cells are",
             "> stride-1 gated-overlap, train-only per fold (leak-marker asserted by the builder).",
             "",
             f"**Total built cells: {len(cells)}**", "",
             "## Counts (built / expected)", "",
             "| baseline | AL | AZ | GA | FL | CA | TX |",
             "|---|---|---|---|---|---|---|"]
    abbr = {"alabama": "AL", "arizona": "AZ", "georgia": "GA", "florida": "FL",
            "california": "CA", "texas": "TX"}
    states = ["alabama", "arizona", "georgia", "florida", "california", "texas"]
    for b in ["b2c_onehot64", "b2b", "ctle", "poi2vec"]:
        exp = 1 if b == "b2c_onehot64" else 20
        row = [b]
        for st in states:
            n = counts.get((b, st), 0)
            row.append(f"{n}/{exp}" if n else "—")
        lines.append("| " + " | ".join(row) + " |")
    lines += ["", "## Cells", "",
              "| baseline | state | seed | fold | rows | size_MB | stride | min_seq | leak |",
              "|---|---|---|---|---|---|---|---|---|"]
    for c in cells:
        lines.append(f"| {c['baseline']} | {c['state']} | {c['seed']} | {c['fold']} | "
                     f"{c['rows']:,} | {c['size_mb']} | {c.get('stride')} | "
                     f"{c.get('min_seq')} | {'✓' if c.get('leak_marker') else '—'} |")
    (DOCS / "M2PRO_MANIFEST.md").write_text("\n".join(lines) + "\n")
    print(f"manifest: {len(cells)} cells -> {DOCS/'M2PRO_MANIFEST.md'}")
    for (b, st), n in sorted(counts.items()):
        print(f"  {b:14s} {st:11s} {n}")


if __name__ == "__main__":
    main()
