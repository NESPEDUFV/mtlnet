#!/usr/bin/env python3
"""AUDIT re-eval: conditional coupling (cc_e2e) at FL vs FRESH MATCHED replicated
champion-G baselines (gmatched_manifest), with the run-to-run non-determinism floor.

For each FL seed: G_a, G_b = two fresh champion-G replicates → G_mean (stable matched
baseline) and |G_a−G_b| (noise floor). cc_e2e − G_mean = the matched effect. Compare
the effect to the noise floor and to the OLD reused-baseline delta.
"""
import csv, glob, json, statistics as st
from pathlib import Path
REPO = Path(__file__).resolve().parents[2]


def rc(rd):
    folds = []
    for f in sorted(glob.glob(str(REPO / rd / "metrics/fold*_next_region_val.csv"))):
        rows = list(csv.DictReader(open(f)))
        b = max(rows, key=lambda r: float(r["top10_acc_indist"]))
        folds.append(float(b["top10_acc_indist"]) * (1 - float(b["ood_fraction"])) * 100)
    d = json.load(open(REPO / rd / "summary/full_summary.json"))
    cat = d["diagnostic_task_best"]["next_category"]["f1"]["mean"] * 100
    return (round(st.mean(folds), 3) if folds else None, round(cat, 3))


# fresh matched G replicates (FL)
gm = {}  # seed -> {rep: rundir}
for line in (REPO / "scripts/mtl_frontier/gmatched_manifest.tsv").read_text().splitlines():
    p = line.split("\t")  # tag seed rep rundir
    if len(p) >= 4:
        gm.setdefault(int(p[1]), {})[p[2]] = p[3]
# cc_e2e FL
cce = {}
for line in (REPO / "scripts/mtl_frontier/cc_manifest.tsv").read_text().splitlines():
    p = line.split("\t")
    if len(p) >= 3 and p[0] == "cc_e2e_florida":
        cce[0] = p[2]
for line in (REPO / "scripts/mtl_frontier/cc_e2e_multiseed_manifest.tsv").read_text().splitlines():
    p = line.split("\t")
    if len(p) >= 4 and p[1] == "florida":
        cce[int(p[2])] = p[3]

SEEDS = [0, 1, 7, 100]
rows, eff_cat, eff_reg, noise_cat, noise_reg = [], [], [], [], []
for s in SEEDS:
    if s not in gm or "a" not in gm[s] or "b" not in gm[s] or s not in cce:
        continue
    ga_r, ga_c = rc(gm[s]["a"]); gb_r, gb_c = rc(gm[s]["b"])
    gmean_r, gmean_c = (ga_r + gb_r) / 2, (ga_c + gb_c) / 2
    cc_r, cc_c = rc(cce[s])
    dcat = cc_c - gmean_c; dreg = cc_r - gmean_r
    eff_cat.append(dcat); eff_reg.append(dreg)
    noise_cat.append(abs(ga_c - gb_c)); noise_reg.append(abs(ga_r - gb_r))
    rows.append({"seed": s, "G_a_cat": ga_c, "G_b_cat": gb_c, "G_mean_cat": round(gmean_c, 3),
                 "cc_cat": cc_c, "delta_cat_matched": round(dcat, 3), "G_noise_cat": round(abs(ga_c - gb_c), 3),
                 "delta_reg_matched": round(dreg, 3), "G_noise_reg": round(abs(ga_r - gb_r), 3)})

out = {"state": "florida", "comparand": "FRESH matched champion-G (2 replicates/seed)",
       "per_seed": rows,
       "mean_delta_cat_matched": round(st.mean(eff_cat), 3) if eff_cat else None,
       "std_delta_cat_matched": round(st.pstdev(eff_cat), 3) if len(eff_cat) > 1 else 0.0,
       "mean_delta_reg_matched": round(st.mean(eff_reg), 3) if eff_reg else None,
       "mean_G_noise_cat": round(st.mean(noise_cat), 3) if noise_cat else None,
       "mean_G_noise_reg": round(st.mean(noise_reg), 3) if noise_reg else None}
outp = REPO / "docs/results/mtl_frontier/cc_rematched_results.json"
outp.write_text(json.dumps(out, indent=2) + "\n")
print(json.dumps(out, indent=2))
print("\n=== cc_e2e FL vs FRESH MATCHED G (audit re-eval) ===")
for r in rows:
    print(f"  seed{r['seed']:<3}: G_mean cat {r['G_mean_cat']} (noise ±{r['G_noise_cat']})  cc {r['cc_cat']}  Δcat_matched {r['delta_cat_matched']:+.3f}")
print(f"  → matched Δcat = {out['mean_delta_cat_matched']}±{out['std_delta_cat_matched']} "
      f"vs G-noise-floor {out['mean_G_noise_cat']}  | matched Δreg = {out['mean_delta_reg_matched']} (noise {out['mean_G_noise_reg']})")
print(f"WROTE {outp}")
