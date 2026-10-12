#!/usr/bin/env python
"""Aggregate O2/O3 multi-seed cat macro-F1 into a per-(head,state) table.

cat macro-F1 = full_summary['next']['f1']['mean'] (5-fold mean) per seed, then
averaged across seeds {0,1,7,100}. Compares vs the frozen (c)-cat next_gru floor.

Usage: PYTHONPATH=src .venv/bin/python scripts/mtl_improvement/o2o3_agg.py
"""
import json
import statistics as st
from pathlib import Path

MAN = Path("/tmp/o2o3")
# Frozen (c)-cat next_gru ceiling (seed42) — the floor a challenger must clear.
FLOOR = {"alabama": 49.97, "arizona": 51.01, "georgia": 58.12, "florida": 69.97}
# FL MTL diagnostic-best cat (multi-seed {0,1,7,100}) — the number (c) must bound (O3).
MTL_DIAG_FL = 70.26


def cat_f1(rundir: str):
    f = Path(rundir) / "summary" / "full_summary.json"
    if not f.exists():
        return None
    d = json.load(open(f))
    return d.get("next", {}).get("f1", {}).get("mean", 0.0) * 100


def load(arm: str):
    man = MAN / f"manifest_{arm}.tsv"
    rows = {}
    if not man.exists():
        return rows
    for line in man.read_text().splitlines():
        p = line.split("\t")
        if len(p) >= 5 and p[4] == "ok":
            h, state, seed, rd = p[0], p[1], p[2], p[3]
            v = cat_f1(rd)
            if v is not None:
                rows.setdefault((h, state), {})[seed] = v
    return rows


def show(arm, rows):
    print(f"\n{'='*78}\n{arm.upper()} — multi-seed cat macro-F1 (mean over seeds vs frozen (c) floor)\n{'='*78}")
    print(f"{'head':<16}{'state':<10}{'seeds':<22}{'mean±sd':>12}{'floor':>8}{'Δ':>8}  verdict")
    for (h, state), sd in sorted(rows.items()):
        vals = [sd[k] for k in sorted(sd)]
        m = st.mean(vals)
        s = st.stdev(vals) if len(vals) > 1 else 0.0
        floor = FLOOR.get(state, float("nan"))
        d = m - floor
        seedstr = ",".join(f"{v:.1f}" for v in vals)
        if arm == "o3":
            verdict = (f"vs MTL-diag {MTL_DIAG_FL}: Δ={m-MTL_DIAG_FL:+.2f} -> "
                       + ("ceiling OK (≥MTL)" if m >= MTL_DIAG_FL else "still below (confound)"))
        else:
            verdict = "PROMOTE (≥+0.5)" if d >= 0.5 else ("tie" if d > -0.5 else "loses")
        print(f"{h:<16}{state:<10}{seedstr:<22}{m:>8.2f}±{s:.2f}{floor:>8.2f}{d:>+8.2f}  {verdict}")


def main():
    for arm in ("o2", "o3"):
        rows = load(arm)
        if rows:
            show(arm, rows)
        else:
            print(f"\n{arm.upper()}: no results yet ({MAN}/manifest_{arm}.tsv missing/empty)")


if __name__ == "__main__":
    main()
