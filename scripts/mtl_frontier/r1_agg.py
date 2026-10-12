#!/usr/bin/env python3
"""Aggregate the R1 screen: log_C co-location KD INCREMENTAL over G + log_T-KD.

Metric (matched bar, R0 method): reg-full = top10_acc_indist · (1 − ood_fraction)
at the indist-best epoch, per fold → mean. cat = diagnostic-best macro-F1. The
gate is R1 − base ≥ 0.3 pp reg (with no material cat regression), seed 0 AL+FL.
"""
import csv, glob, json, statistics as st
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]


def reg_full_cat(rd):
    rd = REPO / rd
    folds = []
    for f in sorted(glob.glob(str(rd / "metrics/fold*_next_region_val.csv"))):
        rows = list(csv.DictReader(open(f)))
        b = max(rows, key=lambda r: float(r["top10_acc_indist"]))
        folds.append(float(b["top10_acc_indist"]) * (1 - float(b["ood_fraction"])) * 100)
    d = json.load(open(rd / "summary/full_summary.json"))
    cat = d["diagnostic_task_best"]["next_category"]["f1"]["mean"] * 100
    reg_diag = d["diagnostic_task_best"]["next_region"]["top10_acc_indist"]["mean"] * 100
    return (
        round(st.mean(folds), 3) if folds else None,
        round(st.pstdev(folds), 3) if len(folds) > 1 else 0.0,
        round(cat, 3), round(reg_diag, 3),
    )


man = {}
for line in (REPO / "scripts/mtl_frontier/r1_screen_manifest.tsv").read_text().splitlines():
    p = line.split("\t")
    if len(p) >= 3:
        man[p[0]] = (p[1], p[2])

rows = {}
for tag, (state, rd) in man.items():
    reg, sd, cat, regdiag = reg_full_cat(rd)
    rows[tag] = {"state": state, "reg_full": reg, "reg_full_std": sd,
                 "cat_f1": cat, "reg_diag_indist": regdiag, "rundir": rd}

out = {"runs": rows, "gate": {}}
for state in ("alabama", "florida"):
    base = rows.get(f"base_{state}")
    r1 = rows.get(f"r1_{state}")
    if base and r1 and base["reg_full"] is not None and r1["reg_full"] is not None:
        dreg = round(r1["reg_full"] - base["reg_full"], 3)
        dcat = round(r1["cat_f1"] - base["cat_f1"], 3)
        out["gate"][state] = {
            "base_reg_full": base["reg_full"], "r1_reg_full": r1["reg_full"],
            "delta_reg": dreg,
            "base_cat": base["cat_f1"], "r1_cat": r1["cat_f1"], "delta_cat": dcat,
            "promote_reg_>=0.3": dreg >= 0.3,
        }

outp = REPO / "docs/results/mtl_frontier/r1_screen_results.json"
outp.parent.mkdir(parents=True, exist_ok=True)
outp.write_text(json.dumps(out, indent=2) + "\n")
print(json.dumps(out, indent=2))
# Verdict summary
print("\n=== R1 GATE (≥0.3pp reg over G+log_T-KD, seed0) ===")
for state, g in out["gate"].items():
    verdict = "PROMOTE→multiseed" if g["promote_reg_>=0.3"] else "null"
    print(f"  {state:8} Δreg {g['delta_reg']:+.3f}  Δcat {g['delta_cat']:+.3f}  → {verdict}")
print(f"\nWROTE {outp}")
