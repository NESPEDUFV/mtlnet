#!/usr/bin/env python3
"""Conditional coupling screen — cc_e2e / cc_detach vs champion G (cond=none, KD-off).
Gate ≥0.3 pp either head, AL+FL seed0 → multi-seed if positive.
"""
import csv, glob, json, statistics as st
from pathlib import Path
REPO = Path(__file__).resolve().parents[2]


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


base = {}
for line in (REPO / "scripts/mtl_frontier/r2_aftb_manifest.tsv").read_text().splitlines():
    p = line.split("\t")
    if len(p) >= 4 and p[0] in ("base_alabama", "base_florida"):
        base[p[1]] = p[3]
cc = {}
for line in (REPO / "scripts/mtl_frontier/cc_manifest.tsv").read_text().splitlines():
    p = line.split("\t")
    if len(p) >= 3:
        cc[p[0]] = p[2]

out = {"comparand": "champion G (cond=none, KD-off)", "by_state": {}}
promoted = []
for state in ("alabama", "florida"):
    if state not in base:
        continue
    br, bc = rc(base[state])
    out["by_state"][state] = {"base_reg": br, "base_cat": bc, "configs": {}}
    for cfg in ("cc_e2e", "cc_detach"):
        tag = f"{cfg}_{state}"
        if tag not in cc:
            continue
        rr, rcat = rc(cc[tag])
        dreg = round(rr - br, 3) if rr is not None else None
        dcat = round(rcat - bc, 3)
        hit = (dreg is not None and dreg >= 0.3) or (dcat >= 0.3)
        out["by_state"][state]["configs"][cfg] = {"reg": rr, "cat": rcat,
            "delta_reg": dreg, "delta_cat": dcat, "gate_either_>=0.3": hit}
        if hit:
            promoted.append((state, cfg, dreg, dcat))

out["promote_candidates"] = [{"state": s, "config": c, "delta_reg": dr, "delta_cat": dc} for s, c, dr, dc in promoted]
outp = REPO / "docs/results/mtl_frontier/cc_screen_results.json"
outp.write_text(json.dumps(out, indent=2) + "\n")
print(json.dumps(out["by_state"], indent=2))
print("\n=== CONDITIONAL COUPLING GATE (≥0.3pp either head over champion G, seed0) ===")
for state in ("alabama", "florida"):
    s = out["by_state"].get(state, {})
    print(f"  {state}: base reg {s.get('base_reg')} / cat {s.get('base_cat')}")
    for cfg, c in s.get("configs", {}).items():
        flag = " ★PROMOTE" if c["gate_either_>=0.3"] else ""
        print(f"    {cfg:10} Δreg {c['delta_reg']:+.3f}  Δcat {c['delta_cat']:+.3f}{flag}")
print(f"\n  promote candidates: {[(s,c) for s,c,_,_ in promoted] or 'NONE → conditional coupling null'}")
print(f"WROTE {outp}")
