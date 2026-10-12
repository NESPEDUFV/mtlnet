#!/usr/bin/env python
"""Aggregate the T1.4 tuned-ceiling sweep into a per-state ranked table.

reg = next_stan_flow Acc@10 (top10_acc_mean) from docs/results/P1/region_head_*.json,
      including the T1.3 baselines R0 (default, with-prior) and R1 (alpha=0, prior-off).
cat = next_gru macro-F1 (full_summary['next']['f1']['mean']) from the rundirs recorded
      in /tmp/t14/manifest_cat_<state>.tsv.

Usage: PYTHONPATH=src .venv/bin/python scripts/mtl_improvement/t14_agg.py [state ...]
       (default states: alabama florida)
"""
import json
import sys
from pathlib import Path

P1 = Path("docs/results/P1")
MAN = Path("/tmp/t14")

# T1.3 reg baselines already on disk (the floor to beat).
REG_BASE = {
    "R0_default_prioron": "t13_cfg1_raw_v14_s42",
    "R1_alpha0_prioroff": "t13po_cfg1_raw_v14_s42",
}


def reg_acc10(state: str, tag: str):
    f = P1 / f"region_head_{state}_region_5f_50ep_{tag}.json"
    if not f.exists():
        return None
    d = json.load(open(f))
    h = next(iter(d["heads"].values()))
    a = h.get("aggregate", {})
    return (a.get("top10_acc_mean", 0.0) * 100, a.get("top10_acc_std", 0.0) * 100)


def cat_f1(rundir: str):
    f = Path(rundir) / "summary" / "full_summary.json"
    if not f.exists():
        return None
    d = json.load(open(f))
    nx = d.get("next", {}).get("f1", {})
    return (nx.get("mean", 0.0) * 100, nx.get("std", 0.0) * 100)


def reg_table(state: str):
    rows = []
    for label, tag in REG_BASE.items():
        v = reg_acc10(state, tag)
        if v:
            rows.append((label, *v))
    for f in sorted(P1.glob(f"region_head_{state}_region_5f_50ep_r_*.json")):
        if f.name.endswith(".checkpoint.json"):
            continue  # skip mid-run checkpoint files
        tag = f.stem.replace(f"region_head_{state}_region_5f_50ep_", "")
        v = reg_acc10(state, tag)
        if v:
            rows.append((tag, *v))
    return rows


def cat_table(state: str):
    man = MAN / f"manifest_cat_{state}.tsv"
    rows = []
    if man.exists():
        for line in man.read_text().splitlines():
            parts = line.split("\t")
            if len(parts) >= 4 and parts[0] == "cat" and parts[3] == "ok":
                tag, rd = parts[1], parts[2]
                v = cat_f1(rd)
                if v:
                    rows.append((tag, *v))
    return rows


def show(title, rows, unit):
    print(f"\n=== {title} ===")
    if not rows:
        print("  (no results yet)")
        return
    rows = sorted(rows, key=lambda r: r[1], reverse=True)
    best = rows[0][1]
    for tag, m, s in rows:
        star = "  <== BEST" if m == best else ""
        print(f"  {tag:<26} {m:6.2f} ± {s:4.2f} {unit}{star}")


def main():
    states = sys.argv[1:] or ["alabama", "florida"]
    for st in states:
        print(f"\n########## {st.upper()} ##########")
        show(f"reg next_stan_flow Acc@10 — {st}", reg_table(st), "%")
        show(f"cat next_gru macro-F1 — {st}", cat_table(st), "%")


if __name__ == "__main__":
    main()
