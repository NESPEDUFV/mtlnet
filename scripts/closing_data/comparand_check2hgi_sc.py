#!/usr/bin/env python3
"""Check2HGI-SC comparand for the closing_data board (§0/§2).

Runs OUR matched STL heads (cat next_gru + reg next_stan_flow) on the
check2hgi_dk_ovl board base — the SAME recipe mac_baseline_compare.py runs on the
baseline substrate — to produce the Check2HGI-SC reference the CTLE-SC / SC
baselines are compared against. Crucially the reg head runs at --input-type
CHECKIN (the C-2 modality fix): the baselines have no region embedding, so the
matched comparand must be checkin-modality too (the old region-modality 69.73 is a
Check2HGI-only ceiling, NOT a matched Δ).

Prerequisite: the dk_ovl base + per-fold seeded log_T must already be built
(build_overlap_probe_engine.py <state> 1 ; compute_region_transition.py --engine
check2hgi_dk_ovl --per-fold --seed 0 --n-splits 5). This script does NOT stage —
it reuses run_cat/run_reg against the dk_ovl engine dir directly.

Usage:
  PYTHONPATH=src .venv/bin/python scripts/closing_data/comparand_check2hgi_sc.py \
      --state alabama --folds 5 --heads cat reg
  -> docs/results/closing_data/baseline_compare/<state>_check2hgi_sc.json
"""
from __future__ import annotations
import argparse
import json
import statistics as st
import sys
from pathlib import Path

_root = Path(__file__).resolve().parents[2]
for p in (str(_root), str(_root / "src")):
    if p not in sys.path:
        sys.path.insert(0, p)

from scripts.closing_data.mac_baseline_compare import run_cat, run_reg, REPO  # noqa: E402

ENGINE = "check2hgi_dk_ovl"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--state", required=True)
    ap.add_argument("--folds", type=int, default=5)
    ap.add_argument("--heads", nargs="+", default=["cat", "reg"], choices=["cat", "reg"])
    a = ap.parse_args()

    out = {"state": a.state, "baseline": "check2hgi_sc", "engine": ENGINE,
           "note": "Check2HGI-SC comparand: matched STL heads on dk_ovl board base; "
                   "reg is CHECKIN-modality (C-2 matched Δ).", "per_fold": []}
    for f in range(a.folds):
        rec = {"fold": f}
        if "cat" in a.heads:
            rec.update(run_cat(ENGINE, a.state, f))
        if "reg" in a.heads:
            rec.update(run_reg(ENGINE, a.state, f))
        out["per_fold"].append(rec)
        print(f"[comparand] {a.state} fold {f}: {rec}", flush=True)

    for k in ("macro_f1", "top10_acc", "mrr"):
        vals = [r[k] for r in out["per_fold"] if k in r]
        if vals:
            out[f"{k}_mean"] = round(st.mean(vals), 3)
            out[f"{k}_std"] = round(st.stdev(vals), 3) if len(vals) > 1 else 0.0

    outdir = REPO / "docs/results/closing_data/baseline_compare"
    outdir.mkdir(parents=True, exist_ok=True)
    p = outdir / f"{a.state}_check2hgi_sc.json"
    p.write_text(json.dumps(out, indent=2))
    print(f"[comparand] DONE -> {p}", flush=True)
    print(f"[comparand]   cat macro-F1={out.get('macro_f1_mean')} "
          f"reg Acc@10={out.get('top10_acc_mean')}", flush=True)


if __name__ == "__main__":
    main()
