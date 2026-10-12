#!/usr/bin/env python3
"""R2 multi-state confirm — aftb_late (none,ab+ba) vs base (champion G).
AZ/GE seed0 + FL multi-seed {0,1,7,100}. Plus AL (from the AL multi-seed) for
reference. Decision: does the AL cat lift generalize? ≥0.3 cat at scale (FL) or
across small states → v17 candidate; AL-only → scale-conditional null.
"""
import csv, glob, json, statistics as st
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
V14 = "check2hgi_design_k_resln_mae_l0_1"


def reg_cat(rd):
    rd = REPO / rd
    folds = []
    for f in sorted(glob.glob(str(rd / "metrics/fold*_next_region_val.csv"))):
        rows = list(csv.DictReader(open(f)))
        b = max(rows, key=lambda r: float(r["top10_acc_indist"]))
        folds.append(float(b["top10_acc_indist"]) * (1 - float(b["ood_fraction"])) * 100)
    d = json.load(open(rd / "summary/full_summary.json"))
    cat = d["diagnostic_task_best"]["next_category"]["f1"]["mean"] * 100
    return (st.mean(folds) if folds else None, cat)


# Multi-state manifest (AZ/GE seed0 + FL {1,7,100}) + FL seed0 from the sweep manifest.
ms = {}
for line in (REPO / "scripts/mtl_frontier/r2_multistate_manifest.tsv").read_text().splitlines():
    p = line.split("\t")
    if len(p) >= 5:
        ms[(p[1], int(p[2]), "late" if p[3] else "base")] = p[4]
# FL seed0 base + aftb_late from the original sweep
for line in (REPO / "scripts/mtl_frontier/r2_aftb_manifest.tsv").read_text().splitlines():
    p = line.split("\t")
    if len(p) >= 4 and p[1] == "florida" and p[0] in ("base_florida", "aftb_late_florida"):
        ms[("florida", 0, "late" if p[0].startswith("aftb_late") else "base")] = p[3]

out = {"config": "aftb_late (none,ab+ba)", "comparand": "base = champion G (KD-off)", "states": {}}

# AZ, GE: seed0 single
for stt in ("arizona", "georgia"):
    rb, rl = ms.get((stt, 0, "base")), ms.get((stt, 0, "late"))
    if rb and rl:
        br, bc = reg_cat(rb); lr, lc = reg_cat(rl)
        out["states"][stt] = {"seeds": [0], "delta_reg": round(lr - br, 3),
                              "delta_cat": round(lc - bc, 3),
                              "base_cat": round(bc, 3), "late_cat": round(lc, 3)}

# FL: multi-seed {0,1,7,100}
fl_dreg, fl_dcat = [], []
for s in (0, 1, 7, 100):
    rb, rl = ms.get(("florida", s, "base")), ms.get(("florida", s, "late"))
    if rb and rl:
        br, bc = reg_cat(rb); lr, lc = reg_cat(rl)
        fl_dreg.append(lr - br); fl_dcat.append(lc - bc)
if fl_dreg:
    out["states"]["florida"] = {
        "seeds": [0, 1, 7, 100][:len(fl_dreg)],
        "delta_reg": round(st.mean(fl_dreg), 3), "std_reg": round(st.pstdev(fl_dreg), 3) if len(fl_dreg) > 1 else 0.0,
        "delta_cat": round(st.mean(fl_dcat), 3), "std_cat": round(st.pstdev(fl_dcat), 3) if len(fl_dcat) > 1 else 0.0,
        "per_seed_cat": [round(x, 3) for x in fl_dcat],
    }

# AL reference (from the AL multi-seed results JSON, if present)
alp = REPO / "docs/results/mtl_frontier/r2_al_multiseed_results.json"
if alp.exists():
    al = json.load(open(alp))["configs"].get("aftb_late", {})
    out["states"]["alabama"] = {"seeds": [0, 1, 7, 100], "delta_reg": al.get("mean_delta_reg"),
                                "delta_cat": al.get("mean_delta_cat"), "_ref": "AL multi-seed"}

# Decision
cat_hits = {s: v for s, v in out["states"].items() if (v.get("delta_cat") or 0) >= 0.3}
out["generalizes"] = {"states_with_cat>=0.3": list(cat_hits.keys()),
                      "FL_cat_delta": out["states"].get("florida", {}).get("delta_cat")}
outp = REPO / "docs/results/mtl_frontier/r2_multistate_results.json"
outp.write_text(json.dumps(out, indent=2) + "\n")
print(json.dumps(out, indent=2))
print("\n=== R2 aftb_late multi-state (Δcat ≥0.3 = generalizes) ===")
for s, v in out["states"].items():
    print(f"  {s:9} Δreg {v.get('delta_reg'):+.3f}  Δcat {v.get('delta_cat'):+.3f}  "
          f"{'★cat≥0.3' if (v.get('delta_cat') or 0) >= 0.3 else ''}")
print(f"\n  states with Δcat≥0.3: {list(cat_hits.keys())}  | FL Δcat = {out['generalizes']['FL_cat_delta']}")
print(f"WROTE {outp}")
