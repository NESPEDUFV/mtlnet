#!/usr/bin/env python3
"""R10 GRM-gated read screen — G+GRM vs champion G (reused R2 base rows).
Gate: ≥0.3 pp EITHER head, AL+FL seed0. Falsifier: GRM ≡ G within noise (citable null).
"""
import csv, glob, json, statistics as st
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]


def reg_cat(rd):
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
grm = {}
for line in (REPO / "scripts/mtl_frontier/r10_screen_manifest.tsv").read_text().splitlines():
    p = line.split("\t")
    if len(p) >= 3:
        grm[p[1]] = p[2]

out = {"comparand": "base = champion G (v16, KD-off; reused R2 base)", "by_state": {}}
promoted = []
for state in ("alabama", "florida"):
    if state not in base or state not in grm:
        continue
    br, bc = reg_cat(base[state]); gr, gc = reg_cat(grm[state])
    dreg = round(gr - br, 3); dcat = round(gc - bc, 3)
    hit = dreg >= 0.3 or dcat >= 0.3
    out["by_state"][state] = {"base_reg": br, "base_cat": bc, "grm_reg": gr, "grm_cat": gc,
                              "delta_reg": dreg, "delta_cat": dcat, "gate_either_>=0.3": hit}
    if hit:
        promoted.append((state, dreg, dcat))

out["promote"] = [{"state": s, "delta_reg": dr, "delta_cat": dc} for s, dr, dc in promoted]
outp = REPO / "docs/results/mtl_frontier/r10_screen_results.json"
outp.parent.mkdir(parents=True, exist_ok=True)
outp.write_text(json.dumps(out, indent=2) + "\n")
print(json.dumps(out, indent=2))
print("\n=== R10 GRM GATE (≥0.3pp EITHER head over champion G, seed0) ===")
for state, c in out["by_state"].items():
    flag = " ★PROMOTE" if c["gate_either_>=0.3"] else ""
    print(f"  {state}: Δreg {c['delta_reg']:+.3f}  Δcat {c['delta_cat']:+.3f}{flag}")
print(f"\n  promote: {[s for s,_,_ in promoted] or 'NONE → R10 null (GRM ≡ G — citable)'}")
print(f"WROTE {outp}")
