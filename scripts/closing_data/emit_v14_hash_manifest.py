"""Emit / update the canonical v14 substrate hash manifest (HANDOFF_A40_PREFREEZE Lane 3).

The frozen v14 substrate is the comparability anchor for the whole board. It was
materialized several non-identical ways across studies with no identity assert
(FREEZE_READINESS §2 BLOCKER). This emits a sha256 manifest of each state's
substrate-DEFINING artifacts so:
  - CA/TX/GE builds can be checked for identity against ONE anchor, and
  - the C1/A2/A4 study substrates can be diffed against the board substrate.

What is hashed = substrate identity (windowing-INDEPENDENT):
  embeddings.parquet, poi_embeddings.parquet, region_embeddings.parquet,
  input/{next,next_region,category}*.parquet (if present).
What is NOT hashed = windowing-DEPENDENT (rebuilds post-freeze): the per-fold
  seeded log_T (region_transition_log_*.pt), region_colocation_log_*, temp/.

Usage:
    python scripts/closing_data/emit_v14_hash_manifest.py                 # all states found on disk
    python scripts/closing_data/emit_v14_hash_manifest.py --states california texas
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
ENGINE = "check2hgi_design_k_resln_mae_l0_1"
SUB_ROOT = ROOT / "output" / ENGINE
OUT_JSON = ROOT / "docs" / "studies" / "closing_data" / "V14_HASH_MANIFEST.json"

# substrate-identity artifacts (windowing-independent), in canonical order
TOP_ARTIFACTS = ["embeddings.parquet", "poi_embeddings.parquet", "region_embeddings.parquet"]
INPUT_ARTIFACTS = ["next.parquet", "next_region.parquet", "category.parquet"]


def sha256_file(p: Path, chunk: int = 1 << 20) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for blk in iter(lambda: f.read(chunk), b""):
            h.update(blk)
    return h.hexdigest()


def manifest_for_state(state: str) -> dict | None:
    d = SUB_ROOT / state
    if not d.is_dir():
        return None
    files = {}
    for name in TOP_ARTIFACTS:
        p = d / name
        if p.exists():
            files[name] = {"sha256": sha256_file(p), "bytes": p.stat().st_size}
    indir = d / "input"
    if indir.is_dir():
        for name in INPUT_ARTIFACTS:
            p = indir / name
            if p.exists():
                files[f"input/{name}"] = {"sha256": sha256_file(p), "bytes": p.stat().st_size}
    # region cardinality (board comparability metadatum) — read row count from
    # parquet metadata, not the full payload.
    n_regions = None
    rp = d / "region_embeddings.parquet"
    if rp.exists():
        try:
            import pyarrow.parquet as _pq
            n_regions = int(_pq.ParquetFile(rp).metadata.num_rows)
        except Exception:
            try:
                n_regions = int(len(pd.read_parquet(rp, columns=[])))
            except Exception:
                n_regions = None
    return {
        "engine": ENGINE,
        "n_regions": n_regions,
        "hashed_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "files": files,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--states", nargs="*", default=None,
                    help="states to (re)hash; default = all dirs found under the engine")
    args = ap.parse_args()

    states = args.states or sorted(p.name for p in SUB_ROOT.iterdir() if p.is_dir())

    # merge with any existing manifest so a partial re-run only updates named states
    manifest = {}
    if OUT_JSON.exists():
        manifest = json.loads(OUT_JSON.read_text())
    manifest.setdefault("engine", ENGINE)
    manifest.setdefault("states", {})
    # last_run_utc = when THIS invocation ran; each state carries its own hashed_utc
    # (a partial --states re-run no longer restamps untouched states).
    manifest["last_run_utc"] = datetime.now(timezone.utc).isoformat(timespec="seconds")

    for st in states:
        m = manifest_for_state(st)
        if m is None:
            print(f"[skip] {st}: no substrate dir")
            continue
        manifest["states"][st] = m
        print(f"[ok]   {st}: n_regions={m['n_regions']} files={len(m['files'])}")
        for fn, meta in m["files"].items():
            print(f"         {meta['sha256'][:16]}…  {fn}  ({meta['bytes']:,} B)")

    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(manifest, indent=2, sort_keys=True))
    print(f"\nwrote {OUT_JSON.relative_to(ROOT)} ({len(manifest['states'])} states total)")


if __name__ == "__main__":
    main()
