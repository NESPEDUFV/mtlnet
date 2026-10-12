#!/usr/bin/env python3
"""R9 BayesAgg-MTL champion-recipe screen — bayesagg_mtl vs matched champion G
(static_weight 0.75), AL+FL seed0. Question: does the repo bayesagg_mtl (gradient
MAGNITUDE-variance weighting, not the faithful ICML'24 direction-posterior) crater at
the CHAMPION recipe too (→ impl pathology) or recover (→ the 19-arm crater was a
defaults artifact)? Matched bar: reg=top10_acc_indist·(1-ood)@indist-best, cat=diag-best f1.
"""
import csv, glob, json, statistics as st
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
STATES = ["alabama", "florida"]


def rc(rd):
    rd = REPO / rd
    folds = []
    for f in sorted(glob.glob(str(rd / "metrics/fold*_next_region_val.csv"))):
        rows = list(csv.DictReader(open(f)))
        b = max(rows, key=lambda r: float(r["top10_acc_indist"]))
        folds.append(float(b["top10_acc_indist"]) * (1 - float(b["ood_fraction"])) * 100)
    d = json.load(open(rd / "summary/full_summary.json"))
    cat = d["diagnostic_task_best"]["next_category"]["f1"]["mean"] * 100
    return (round(st.mean(folds), 3) if folds else None, round(cat, 3))


man = {}
for line in (REPO / "scripts/mtl_frontier/r9_screen_manifest.tsv").read_text().splitlines():
    p = line.split("\t")
    if len(p) >= 3:
        man[p[0]] = p[2]

out = {"comparand": "champion G (static_weight 0.75, KD-off), seed0",
       "note": "repo bayesagg_mtl = gradient-magnitude-variance weighting (Kendall-style), "
               "NOT the faithful ICML'24 posterior gradient-direction uncertainty.",
       "by_state": {}}
for state in STATES:
    bt, vt = f"base_{state}", f"bayesagg_{state}"
    if bt not in man or vt not in man:
        continue
    br, bc = rc(man[bt])
    vr, vc = rc(man[vt])
    out["by_state"][state] = {
        "champion_reg": br, "champion_cat": bc,
        "bayesagg_reg": vr, "bayesagg_cat": vc,
        "delta_reg": round(vr - br, 3) if (vr is not None and br is not None) else None,
        "delta_cat": round(vc - bc, 3),
        "cratered_cat": (vc is not None and bc is not None and vc < bc - 5.0),
    }

outp = REPO / "docs/results/mtl_frontier/r9_screen_results.json"
outp.write_text(json.dumps(out, indent=2) + "\n")
print("=== R9 BayesAgg-MTL champion-recipe screen (vs champion G static_weight 0.75, seed0) ===")
for state in STATES:
    s = out["by_state"].get(state)
    if not s:
        continue
    print(f"\n{state}: champion cat {s['champion_cat']} / reg {s['champion_reg']}")
    print(f"    bayesagg cat {s['bayesagg_cat']} ({s['delta_cat']:+.3f})  reg {s['bayesagg_reg']} ({s['delta_reg']:+.3f})"
          f"{'   ← CAT CRATER' if s['cratered_cat'] else ''}")
print(f"\nWROTE {outp}")
