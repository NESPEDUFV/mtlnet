#!/usr/bin/env python3
"""Aggregate the X-series runs (HANDOFF_AUDIT 2026-06-12) and apply the promote gates.

Metric: reg-full = indist*(1-ood) @ indist-best epoch (R0 matched); cat = diag-best macro-F1.
Comparisons:
  X2 G-unchanged : A (FL KD-off, post-fix) vs R0 seed0 FL G  → should match (gate fix inert)
  X2 KD-on FL    : C (FL KD0.2) vs A           → gate: ≥+0.3pp reg ⇒ promote (multi-seed)
  X2 KD-on AL    : D (AL KD0.2) vs R0 seed0 AL G→ gate: ≥+0.3pp reg ⇒ promote
  X4 fp32 eval   : B (FL KD-off fp32 eval) vs A (fp16) → Δreg; |Δ|≳0.1pp ⇒ re-score R0 FL row
  X1 roll probe  : E (FL KD-off, task-b rolled) cat-F1 vs A cat-F1 → Δcat≈0 ⇒ mixing dead
"""
import csv, glob, json, statistics as st
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
R0 = json.load(open(REPO / "docs/results/mtl_improvement/R0_matched_metric_bar.json"))


def reg_full_cat(rd):
    folds = []
    for f in sorted(glob.glob(str(REPO / rd / "metrics/fold*_next_region_val.csv"))):
        rows = list(csv.DictReader(open(f)))
        b = max(rows, key=lambda r: float(r["top10_acc_indist"]))
        folds.append(float(b["top10_acc_indist"]) * (1 - float(b["ood_fraction"])) * 100)
    d = json.load(open(REPO / rd / "summary/full_summary.json"))
    cat = d["diagnostic_task_best"]["next_category"]["f1"]["mean"] * 100
    return (round(st.mean(folds), 3) if folds else None), round(cat, 3)


man = {}
for line in (REPO / "scripts/mtl_improvement/x_series_manifest.tsv").read_text().splitlines():
    p = line.split("\t")
    if len(p) >= 3:
        man[p[0]] = (p[1], p[2])

runs = {}
for tag, (state, rd) in man.items():
    reg, cat = reg_full_cat(rd)
    runs[tag] = {"state": state, "rundir": rd, "reg_full": reg, "cat_f1": cat}

# R0 seed0 references (per_seed index 0 == seed 0).
r0_fl = R0["states"]["florida"]
r0_al = R0["states"]["alabama"]
r0_fl_g_reg0 = r0_fl["g_reg_full_per_seed"][0]
r0_al_g_reg0 = r0_al["g_reg_full_per_seed"][0]

A = runs.get("A_fl_kdoff_ckpt", {})
B = runs.get("B_fl_kdoff_fp32", {})
C = runs.get("C_fl_kd02", {})
D = runs.get("D_al_kd02", {})
E = runs.get("E_fl_rollprobe", {})


def d(a, b):
    return round(a - b, 3) if (a is not None and b is not None) else None

verdicts = {
    "X2_G_unchanged_FL": {
        "A_reg": A.get("reg_full"), "A_cat": A.get("cat_f1"),
        "R0_seed0_FL_G_reg": r0_fl_g_reg0,
        "delta_reg_vs_R0": d(A.get("reg_full"), r0_fl_g_reg0),
        "note": "post-fix KD-off G should match R0 seed0 G (aux-gate fix inert on G)",
    },
    "X2_KDon_FL": {
        "C_reg": C.get("reg_full"), "A_reg": A.get("reg_full"),
        "delta_reg": d(C.get("reg_full"), A.get("reg_full")),
        "C_cat": C.get("cat_f1"), "delta_cat": d(C.get("cat_f1"), A.get("cat_f1")),
        "promote": (d(C.get("reg_full"), A.get("reg_full")) or -9) >= 0.3,
    },
    "X2_KDon_AL": {
        "D_reg": D.get("reg_full"), "R0_seed0_AL_G_reg": r0_al_g_reg0,
        "delta_reg": d(D.get("reg_full"), r0_al_g_reg0),
        "promote": (d(D.get("reg_full"), r0_al_g_reg0) or -9) >= 0.3,
    },
    "X4_fp32_eval_FL": {
        "A_reg_fp16": A.get("reg_full"), "B_reg_fp32": B.get("reg_full"),
        "delta_reg_fp32_minus_fp16": d(B.get("reg_full"), A.get("reg_full")),
        "material": abs(d(B.get("reg_full"), A.get("reg_full")) or 0) >= 0.1,
    },
    "X1_roll_probe_FL": {
        "A_cat_aligned": A.get("cat_f1"), "E_cat_rolled": E.get("cat_f1"),
        "delta_cat": d(E.get("cat_f1"), A.get("cat_f1")),
        "mixing_dead": abs(d(E.get("cat_f1"), A.get("cat_f1")) or 9) < 0.3,
        "note": "reg under roll is meaningless by construction — read cat-F1 only",
    },
}

out = {"runs": runs, "verdicts": verdicts}
outp = REPO / "docs/results/mtl_improvement/x_series_results.json"
outp.write_text(json.dumps(out, indent=2) + "\n")
print(json.dumps(out, indent=2))
print(f"\nWROTE {outp}")
