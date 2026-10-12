#!/usr/bin/env python3
"""R5 per-instance KD-gating screen — coverage_max / coverage_entropy vs GLOBAL
log_T-KD W=0.2 (gate=none), AL+FL seed0. Matched bar (same as all levers):
reg = top10_acc_indist·(1-ood) @ indist-best, cat = diagnostic_task_best f1.
Falsifier: gated ≤ global-W everywhere. Gate ≥0.3 either head → multi-seed.
"""
import csv, glob, json, statistics as st
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
STATES = ["alabama", "florida"]
VARIANTS = ["covmax", "coventr"]


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
for line in (REPO / "scripts/mtl_frontier/r5_screen_manifest.tsv").read_text().splitlines():
    p = line.split("\t")
    if len(p) >= 4:
        man[p[0]] = p[3]

out = {"comparand": "champion G + GLOBAL log_T-KD W=0.2 (gate=none), seed0", "by_state": {}}
promoted = []
for state in STATES:
    bt = f"base_{state}"
    if bt not in man:
        continue
    br, bc = rc(man[bt])
    out["by_state"][state] = {"base_reg": br, "base_cat": bc, "configs": {}}
    for v in VARIANTS:
        tag = f"{v}_{state}"
        if tag not in man:
            continue
        rr, rcat = rc(man[tag])
        dreg = round(rr - br, 3) if (rr is not None and br is not None) else None
        dcat = round(rcat - bc, 3)
        hit = (dreg is not None and dreg >= 0.3) or (dcat >= 0.3)
        out["by_state"][state]["configs"][v] = {"reg": rr, "cat": rcat,
            "delta_reg": dreg, "delta_cat": dcat, "gate_either_>=0.3": hit}
        if hit:
            promoted.append((state, v, dreg, dcat))

out["promote_candidates"] = [{"state": s, "config": c, "delta_reg": dr, "delta_cat": dc} for s, c, dr, dc in promoted]
out["fl_multiseed_next"] = sorted({c for s, c, _, _ in promoted if s == "florida"})
outp = REPO / "docs/results/mtl_frontier/r5_screen_results.json"
outp.write_text(json.dumps(out, indent=2) + "\n")
print("=== R5 PER-INSTANCE KD-GATING (vs GLOBAL log_T-KD W=0.2, seed0) ===")
for state in STATES:
    s = out["by_state"].get(state, {})
    print(f"\n{state}: global-W base reg {s.get('base_reg')} / cat {s.get('base_cat')}")
    for v in VARIANTS:
        c = s.get("configs", {}).get(v)
        if not c:
            continue
        flag = " ★" if c["gate_either_>=0.3"] else ""
        dr = f"{c['delta_reg']:+.3f}" if c["delta_reg"] is not None else " n/a"
        print(f"    {v:8} reg {str(c['reg']):>7} ({dr})  cat {c['cat']:>7} ({c['delta_cat']:+.3f}){flag}")
print(f"\n  FL positives → multi-seed: {out['fl_multiseed_next'] or 'NONE (falsifier: gated ≤ global-W)'}")
print(f"WROTE {outp}")
