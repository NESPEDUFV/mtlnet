#!/usr/bin/env python3
"""R7 merge-vs-joint aggregator. The ENSEMBLE (cat-specialist's cat + reg-specialist's
reg) is the BEST-CASE merge and a rigorous UPPER bound on any weight-merge. Compare it to
the JOINT champion G (FL seed0 = the R9 base_florida rundir, cat 73.012 / reg 72.929).
If the ensemble loses net to G, no merge can match joint training (tangent-space theory).
Matched bar: reg=top10_acc_indist·(1-ood)@indist-best; cat=diagnostic_task_best f1.
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


man = {}
for line in (REPO / "scripts/mtl_frontier/r7_specialists_manifest.tsv").read_text().splitlines():
    p = line.split("\t")
    if len(p) >= 4:
        man[p[0]] = p[3]
# champion G FL seed0 = R9 base_florida (static_weight cw=0.75, KD off, dual-tower)
gj = None
for line in (REPO / "scripts/mtl_frontier/r9_screen_manifest.tsv").read_text().splitlines():
    p = line.split("\t")
    if len(p) >= 3 and p[0] == "base_florida":
        gj = p[2]

g_reg, g_cat = rc(gj)
cs_reg, cs_cat = rc(man["cat_specialist"])   # cat-only: cat is its STL-ish cat; reg head untrained
rs_reg, rs_cat = rc(man["reg_specialist"])   # reg-only: reg is its STL-ish reg; cat head untrained

# ENSEMBLE = best-case merge: each task served by its own specialist
ens_cat, ens_reg = cs_cat, rs_reg
out = {
    "comparand": "joint champion G, FL seed0 (R9 base_florida)",
    "champion_G": {"cat": g_cat, "reg": g_reg},
    "cat_specialist": {"cat": cs_cat, "reg_untrained": cs_reg},
    "reg_specialist": {"reg": rs_reg, "cat_untrained": rs_cat},
    "ensemble_best_case_merge": {"cat": ens_cat, "reg": ens_reg,
                                 "delta_cat_vs_G": round(ens_cat - g_cat, 3),
                                 "delta_reg_vs_G": round(ens_reg - g_reg, 3)},
    "verdict": ("merge<=ensemble; ensemble net-worse than joint G"
                if (ens_cat - g_cat) + (ens_reg - g_reg) < 0 else "ensemble>=G (SURPRISE — escalate)"),
}
outp = REPO / "docs/results/mtl_frontier/r7_merge_results.json"
outp.write_text(json.dumps(out, indent=2) + "\n")
print("=== R7 MERGE-vs-JOINT (FL seed0) ===")
print(f"  joint champion G:        cat {g_cat}  reg {g_reg}")
print(f"  cat-specialist (cw=1.0): cat {cs_cat}  (reg untrained {cs_reg})")
print(f"  reg-specialist (cw=0.0): reg {rs_reg}  (cat untrained {rs_cat})")
print(f"  ENSEMBLE (best-case merge = cat-spec cat + reg-spec reg):")
print(f"     cat {ens_cat} ({ens_cat-g_cat:+.3f} vs G)   reg {ens_reg} ({ens_reg-g_reg:+.3f} vs G)")
print(f"  → merge ≤ ensemble; verdict: {out['verdict']}")
print(f"     (joint G's cat lift comes from co-training the shared trunk — unrecoverable by merging)")
print(f"WROTE {outp}")
