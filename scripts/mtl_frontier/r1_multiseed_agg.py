#!/usr/bin/env python3
"""R1 AL multi-seed gate: paired (base=G+log_T-KD) vs (R1=+log_C-KD) at {0,1,7,100}.

Per-fold matched reg = top10_acc_indist·(1−ood) at the indist-best epoch. Pairing is
per (seed, fold) — n=20 — exactly how log_T-KD's n=20 promotion was structured. Reports:
the 4-seed mean Δreg ± std, per-seed Δ, paired Wilcoxon (n=20 fold-seed pairs, one-sided
greater), and the cat Δ (no-regression check). Gate: 4-seed mean Δreg ≥ 0.3 pp.
"""
import csv, glob, json, statistics as st
from pathlib import Path
from scipy.stats import wilcoxon

REPO = Path(__file__).resolve().parents[2]
ST = "alabama"


def per_fold_reg(rd):
    rd = REPO / rd
    out = []
    for f in sorted(glob.glob(str(rd / "metrics/fold*_next_region_val.csv"))):
        rows = list(csv.DictReader(open(f)))
        b = max(rows, key=lambda r: float(r["top10_acc_indist"]))
        out.append(float(b["top10_acc_indist"]) * (1 - float(b["ood_fraction"])) * 100)
    return out  # length 5, fold-ordered


def cat_f1(rd):
    d = json.load(open(REPO / rd / "summary/full_summary.json"))
    return d["diagnostic_task_best"]["next_category"]["f1"]["mean"] * 100


# Collect rundirs: seed0 from the screen manifest, seeds 1/7/100 from the AL multi-seed.
runs = {}  # (seed, arm) -> rundir
for line in (REPO / "scripts/mtl_frontier/r1_screen_manifest.tsv").read_text().splitlines():
    p = line.split("\t")
    if len(p) >= 3 and p[1] == ST:
        arm = "r1" if p[0].startswith("r1") else "base"
        runs[(0, arm)] = p[2]
ms = REPO / "scripts/mtl_frontier/r1_al_multiseed_manifest.tsv"
for line in ms.read_text().splitlines():
    p = line.split("\t")
    if len(p) >= 4:
        seed = int(p[2]); arm = "r1" if p[0].startswith("r1") else "base"
        runs[(seed, arm)] = p[3]

SEEDS = [0, 1, 7, 100]
paired_base, paired_r1 = [], []   # per (seed,fold), n=20
per_seed = {}
for s in SEEDS:
    rb, rr = runs.get((s, "base")), runs.get((s, "r1"))
    if not rb or not rr:
        print(f"WARN missing seed {s}: base={rb} r1={rr}")
        continue
    fb, fr = per_fold_reg(rb), per_fold_reg(rr)
    paired_base += fb; paired_r1 += fr
    per_seed[s] = {
        "base_reg": round(st.mean(fb), 3), "r1_reg": round(st.mean(fr), 3),
        "delta_reg": round(st.mean(fr) - st.mean(fb), 3),
        "base_cat": round(cat_f1(rb), 3), "r1_cat": round(cat_f1(rr), 3),
        "delta_cat": round(cat_f1(rr) - cat_f1(rb), 3),
    }

seed_dregs = [v["delta_reg"] for v in per_seed.values()]
seed_dcats = [v["delta_cat"] for v in per_seed.values()]
mean_dreg = round(st.mean(seed_dregs), 3)
std_dreg = round(st.pstdev(seed_dregs), 3) if len(seed_dregs) > 1 else 0.0
mean_dcat = round(st.mean(seed_dcats), 3)

# Paired Wilcoxon over the 20 fold-seed pairs (one-sided: R1 > base).
deltas = [r - b for r, b in zip(paired_r1, paired_base)]
try:
    w_stat, w_p = wilcoxon(paired_r1, paired_base, alternative="greater")
    w_p = float(w_p)
except Exception as e:
    w_stat, w_p = None, None

out = {
    "state": ST, "metric": "reg-full = top10_acc_indist*(1-ood) @ indist-best epoch",
    "comparand": "base = G + log_T-KD 0.2 ; R1 = base + log_C-KD 0.2",
    "per_seed": per_seed,
    "mean_delta_reg": mean_dreg, "std_delta_reg": std_dreg,
    "mean_delta_cat": mean_dcat,
    "wilcoxon_n": len(deltas), "wilcoxon_p_onesided_greater": w_p,
    "n_pairs_positive": sum(1 for d in deltas if d > 0),
    "gate_mean_reg_>=0.3": mean_dreg >= 0.3,
}
outp = REPO / "docs/results/mtl_frontier/r1_al_multiseed_results.json"
outp.parent.mkdir(parents=True, exist_ok=True)
outp.write_text(json.dumps(out, indent=2) + "\n")
print(json.dumps(out, indent=2))
print(f"\n=== R1 AL MULTI-SEED GATE ===")
print(f"  mean Δreg = {mean_dreg:+.3f} ± {std_dreg}  (gate ≥0.3 → {'PASS' if out['gate_mean_reg_>=0.3'] else 'FAIL'})")
print(f"  mean Δcat = {mean_dcat:+.3f}")
print(f"  per-seed Δreg: {seed_dregs}")
print(f"  Wilcoxon n={out['wilcoxon_n']} p(1-sided)={w_p}  ({out['n_pairs_positive']}/{len(deltas)} pairs positive)")
print(f"\nWROTE {outp}")
