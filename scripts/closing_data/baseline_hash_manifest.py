#!/usr/bin/env python3
"""Board baseline-embedding HASH manifest generator (mirrors V14_HASH_MANIFEST.json /
HGI_HASH_MANIFEST.json: per-artifact bytes + sha256 so every consumer machine can verify
the canonical bytes before use).

Walks an output root and hashes the deliverable `embeddings.parquet` of every board
baseline cell:
  - board_baselines/<baseline>/<state>/s<seed>_f<fold>/embeddings.parquet   (b2b, ctle, poi2vec)
  - baseline_b2c_onehot64/<state>/embeddings.parquet                         (b2c, fold-independent)

Two modes:
  gen   : hash a local root            -> JSON keyed by cell id, tagged with --source
  merge : union several gen JSONs      -> one combined manifest (A40 + Mac lanes)

Cell id scheme:  "<baseline>/<state>/s<seed>_f<fold>"   and  "b2c/<state>".
"""
from __future__ import annotations
import argparse, hashlib, json, os, sys
from pathlib import Path


def sha256_of(path: Path) -> tuple[int, str]:
    h = hashlib.sha256()
    n = 0
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8 << 20), b""):
            h.update(chunk)
            n += len(chunk)
    return n, h.hexdigest()


def gen(root: Path, source: str) -> dict:
    cells: dict[str, dict] = {}
    bb = root / "board_baselines"
    for baseline in ("b2b", "ctle", "poi2vec"):
        bdir = bb / baseline
        if not bdir.is_dir():
            continue
        for state_dir in sorted(p for p in bdir.iterdir() if p.is_dir()):
            for cell in sorted(state_dir.glob("s*_f*")):
                emb = cell / "embeddings.parquet"
                if not emb.exists():
                    continue
                nbytes, digest = sha256_of(emb)
                cid = f"{baseline}/{state_dir.name}/{cell.name}"
                cells[cid] = {"bytes": nbytes, "sha256": digest, "source": source}
    b2c = root / "baseline_b2c_onehot64"
    if b2c.is_dir():
        for state_dir in sorted(p for p in b2c.iterdir() if p.is_dir()):
            emb = state_dir / "embeddings.parquet"
            if not emb.exists():
                continue
            nbytes, digest = sha256_of(emb)
            cells[f"b2c/{state_dir.name}"] = {"bytes": nbytes, "sha256": digest, "source": source}
    return cells


def main() -> int:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    g = sub.add_parser("gen")
    g.add_argument("--root", required=True)
    g.add_argument("--source", required=True, help="machine label, e.g. m2pro-ssd / a40")
    g.add_argument("--out", required=True)
    m = sub.add_parser("merge")
    m.add_argument("--inputs", nargs="+", required=True)
    m.add_argument("--out", required=True)
    a = ap.parse_args()

    if a.cmd == "gen":
        cells = gen(Path(a.root), a.source)
        doc = {"engine": "board_baselines", "kind": "hash_manifest",
               "source": a.source, "n_cells": len(cells), "cells": cells}
        Path(a.out).write_text(json.dumps(doc, indent=2, sort_keys=True))
        print(f"[gen] {a.source}: {len(cells)} cells -> {a.out}")
        return 0

    if a.cmd == "merge":
        merged: dict[str, dict] = {}
        conflicts = []
        for p in a.inputs:
            d = json.loads(Path(p).read_text())
            for cid, rec in d["cells"].items():
                if cid in merged and merged[cid]["sha256"] != rec["sha256"]:
                    conflicts.append(cid)
                merged[cid] = rec
        by_baseline: dict[str, int] = {}
        for cid in merged:
            by_baseline[cid.split("/")[0]] = by_baseline.get(cid.split("/")[0], 0) + 1
        doc = {"engine": "board_baselines", "kind": "hash_manifest",
               "n_cells": len(merged), "counts_by_baseline": by_baseline,
               "conflicts": conflicts, "cells": merged}
        Path(a.out).write_text(json.dumps(doc, indent=2, sort_keys=True))
        print(f"[merge] {len(merged)} cells -> {a.out}  counts={by_baseline}  conflicts={conflicts}")
        return 1 if conflicts else 0


if __name__ == "__main__":
    sys.exit(main())
