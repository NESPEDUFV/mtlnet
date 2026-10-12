#!/usr/bin/env python
"""Validate the onecycle reg-recipe lever — onecycle multi-seed {0,1,7,100} vs
the landed (a) baseline (H3-alt@AL/AZ, B9@FL, the v14_mtl_vs_canonical numbers).

Reads onecyc_val arms from t21_harden_manifest.tsv (mtlnet_crossattn +
next_getnext_hard @ onecycle), aggregates mean±std over seeds per state, and
shows Δ vs landed (a) on disjoint reg, deploy reg, and cat.

  PYTHONPATH=src .venv/bin/python scripts/mtl_improvement/t21_onecyc_val.py
"""
import json, re, statistics
from pathlib import Path

# Landed (a) v14-MTL multi-seed {0,1,7,100} — v14_mtl_vs_canonical.md.
LANDED = {
    "alabama":  {"reg_disj": 47.23, "cat_disj": 46.78, "reg_dep": 50.14, "cat_dep": 46.50, "recipe": "H3-alt"},
    "arizona":  {"reg_disj": 38.27, "cat_disj": 48.75, "reg_dep": 37.78, "cat_dep": 48.52, "recipe": "H3-alt"},
    "florida":  {"reg_disj": 61.28, "cat_disj": 70.26, "reg_dep": 61.21, "cat_dep": 66.73, "recipe": "B9"},
}
MAN = Path("scripts/mtl_improvement/t21_harden_manifest.tsv")


def _m(rd):
    s = json.load(open(Path(rd) / "summary" / "full_summary.json"))
    return {
        "reg_disj": s["per_metric_best"]["next_region"]["top10_acc_indist"]["mean"] * 100,
        "reg_dep": s["next_region"]["top10_acc_indist"]["mean"] * 100,
        "cat_dep": s["next_category"]["f1"]["mean"] * 100,
        "cat_disj": s["diagnostic_task_best"]["next_category"]["f1"]["mean"] * 100,
    }


def main():
    by_state = {}
    for line in MAN.read_text().splitlines():
        p = line.split("\t")
        if len(p) < 3 or p[1] != "onecyc_val":
            continue
        st = re.search(r"/(alabama|arizona|florida)/", p[2])
        if not st:
            continue
        try:
            by_state.setdefault(st.group(1), []).append(_m(p[2]))
        except Exception:
            pass
    for st in ["alabama", "arizona", "florida"]:
        runs = by_state.get(st, [])
        if not runs:
            print(f"\n### {st.upper()}: (no onecyc_val runs yet)")
            continue
        L = LANDED[st]
        def agg(k):
            vs = [r[k] for r in runs]
            return statistics.mean(vs), (statistics.stdev(vs) if len(vs) > 1 else 0.0)
        print(f"\n### {st.upper()}  (n={len(runs)} seeds; landed (a) recipe={L['recipe']})")
        for axis, lk in [("reg_disj", "reg_disj"), ("reg_dep", "reg_dep"),
                         ("cat_disj", "cat_disj"), ("cat_dep", "cat_dep")]:
            m, sd = agg(axis)
            d = m - L[lk]
            print(f"  {axis:<9} onecycle={m:6.2f}±{sd:4.2f}  landed(a)={L[lk]:6.2f}  Δ={d:+6.2f}")


if __name__ == "__main__":
    main()
