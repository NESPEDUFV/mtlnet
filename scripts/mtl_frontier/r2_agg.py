#!/usr/bin/env python3
"""Aggregate the R2 STEM-AFTB sweep vs champion G (KD-off). Gate: ≥0.3 pp EITHER
head over G, AL+FL seed0 → a positive promotes to multi-seed.

Metric: reg-full = top10_acc_indist·(1−ood) @ indist-best epoch; cat = diag-best macro-F1.
"""
import csv, glob, json, statistics as st
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
ORDER = ["base", "aftb_all", "aftb_late", "aftb_early", "reg_protect", "cat_protect"]


def reg_full_cat(rd):
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
for line in (REPO / "scripts/mtl_frontier/r2_aftb_manifest.tsv").read_text().splitlines():
    p = line.split("\t")
    if len(p) >= 4:
        man[p[0]] = (p[1], p[2], p[3])   # tag -> (state, spec, rundir)

rows = {}
for tag, (state, spec, rd) in man.items():
    reg, cat = reg_full_cat(rd)
    rows[tag] = {"state": state, "spec": spec or "(G baseline)", "reg_full": reg, "cat_f1": cat}

out = {"runs": rows, "by_state": {}}
promoted = []
for state in ("alabama", "florida"):
    base = rows.get(f"base_{state}")
    if not base:
        continue
    out["by_state"][state] = {"base_reg": base["reg_full"], "base_cat": base["cat_f1"], "configs": {}}
    for cfg in ORDER[1:]:
        r = rows.get(f"{cfg}_{state}")
        if not r:
            continue
        dreg = round(r["reg_full"] - base["reg_full"], 3) if r["reg_full"] is not None else None
        dcat = round(r["cat_f1"] - base["cat_f1"], 3)
        hit = (dreg is not None and dreg >= 0.3) or (dcat >= 0.3)
        out["by_state"][state]["configs"][cfg] = {
            "spec": r["spec"], "reg": r["reg_full"], "cat": r["cat_f1"],
            "delta_reg": dreg, "delta_cat": dcat, "gate_either_>=0.3": hit,
        }
        if hit:
            promoted.append((state, cfg, dreg, dcat))

out["promote_candidates"] = [
    {"state": s, "config": c, "delta_reg": dr, "delta_cat": dc} for s, c, dr, dc in promoted
]
outp = REPO / "docs/results/mtl_frontier/r2_aftb_results.json"
outp.parent.mkdir(parents=True, exist_ok=True)
outp.write_text(json.dumps(out, indent=2) + "\n")
print(json.dumps(out["by_state"], indent=2))
print("\n=== R2 AFTB GATE (≥0.3pp EITHER head over G, seed0) ===")
for state in ("alabama", "florida"):
    s = out["by_state"].get(state, {})
    print(f"  {state}: base reg {s.get('base_reg')} / cat {s.get('base_cat')}")
    for cfg, c in s.get("configs", {}).items():
        flag = " ★PROMOTE" if c["gate_either_>=0.3"] else ""
        print(f"    {cfg:12} ({c['spec']:12}) Δreg {c['delta_reg']:+.3f}  Δcat {c['delta_cat']:+.3f}{flag}")
print(f"\n  promote candidates (seed0): {[(s,c) for s,c,_,_ in promoted] or 'NONE → R2 null'}")
print(f"\nWROTE {outp}")
