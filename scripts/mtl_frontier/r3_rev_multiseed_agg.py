#!/usr/bin/env python3
"""R3 reverse-arm AL multi-seed gate: r3_rev vs base (G + log_T-KD) at {0,1,7,100}.
Baseline reused from the R1 manifests (seed0 r1_screen base_alabama; seeds 1/7/100
r1_al_multiseed base_s*). r3_rev: seed0 from r3_screen, seeds 1/7/100 from r3_al_multiseed.
Per (seed,fold) reg pairing (n=20); cat over 4 seeds. Gate: 4-seed mean ≥0.3 either head.
"""
import csv, glob, json, statistics as st
from pathlib import Path
from scipy.stats import wilcoxon

REPO = Path(__file__).resolve().parents[2]
ST = "alabama"


def pf_reg(rd):
    out = []
    for f in sorted(glob.glob(str(REPO / rd / "metrics/fold*_next_region_val.csv"))):
        rows = list(csv.DictReader(open(f)))
        b = max(rows, key=lambda r: float(r["top10_acc_indist"]))
        out.append(float(b["top10_acc_indist"]) * (1 - float(b["ood_fraction"])) * 100)
    return out


def cat(rd):
    return json.load(open(REPO / rd / "summary/full_summary.json"))["diagnostic_task_best"]["next_category"]["f1"]["mean"] * 100


base, rev = {}, {}
for line in (REPO / "scripts/mtl_frontier/r1_screen_manifest.tsv").read_text().splitlines():
    p = line.split("\t")
    if len(p) >= 3 and p[0] == "base_alabama":
        base[0] = p[2]
for line in (REPO / "scripts/mtl_frontier/r1_al_multiseed_manifest.tsv").read_text().splitlines():
    p = line.split("\t")
    # format: tag \t state \t seed \t rundir
    if len(p) >= 4 and p[0].startswith("base_s"):
        base[int(p[2])] = p[3]
for line in (REPO / "scripts/mtl_frontier/r3_screen_manifest.tsv").read_text().splitlines():
    p = line.split("\t")
    if len(p) >= 3 and p[0] == "r3_rev_alabama":
        rev[0] = p[2]
for line in (REPO / "scripts/mtl_frontier/r3_al_multiseed_manifest.tsv").read_text().splitlines():
    p = line.split("\t")
    if len(p) >= 3:
        rev[int(p[1])] = p[2]

SEEDS = [0, 1, 7, 100]
pb, pr, dreg_s, dcat_s = [], [], [], []
for s in SEEDS:
    if s not in base or s not in rev:
        print(f"WARN missing seed {s}"); continue
    fb, fr = pf_reg(base[s]), pf_reg(rev[s])
    pb += fb; pr += fr
    dreg_s.append(st.mean(fr) - st.mean(fb))
    dcat_s.append(cat(rev[s]) - cat(base[s]))

mean_dreg = round(st.mean(dreg_s), 3); sd_dreg = round(st.pstdev(dreg_s), 3)
mean_dcat = round(st.mean(dcat_s), 3); sd_dcat = round(st.pstdev(dcat_s), 3)
try:
    _, p_reg = wilcoxon(pr, pb, alternative="greater"); p_reg = round(float(p_reg), 5)
    _, p_cat = wilcoxon(dcat_s, [0] * len(dcat_s), alternative="greater"); p_cat = round(float(p_cat), 5)
except Exception:
    p_reg = p_cat = None

out = {"config": "r3_rev (reverse reg→cat KD, warmup15 ec0.3)",
       "comparand": "base = G + log_T-KD 0.2",
       "mean_delta_reg": mean_dreg, "std_delta_reg": sd_dreg,
       "mean_delta_cat": mean_dcat, "std_delta_cat": sd_dcat,
       "per_seed_delta_reg": [round(x, 3) for x in dreg_s],
       "per_seed_delta_cat": [round(x, 3) for x in dcat_s],
       "wilcoxon_reg_p_n20": p_reg, "wilcoxon_cat_p_n4": p_cat,
       "gate_either_>=0.3": (mean_dreg >= 0.3) or (mean_dcat >= 0.3)}
outp = REPO / "docs/results/mtl_frontier/r3_rev_al_multiseed_results.json"
outp.write_text(json.dumps(out, indent=2) + "\n")
print(json.dumps(out, indent=2))
print(f"\n=== R3 r3_rev AL MULTI-SEED GATE ===")
print(f"  Δreg {mean_dreg:+.3f}±{sd_dreg} (p={p_reg})  Δcat {mean_dcat:+.3f}±{sd_dcat} (p={p_cat})")
print(f"  per-seed Δcat: {[round(x,3) for x in dcat_s]}")
print(f"  gate ≥0.3 either: {out['gate_either_>=0.3']}")
print(f"WROTE {outp}")
