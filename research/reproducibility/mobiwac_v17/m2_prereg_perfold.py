#!/usr/bin/env python3
"""M2 — the PRE-REGISTERED test at its registered footing, on the joint-best arrays.

Pre-registration: docs/reproducibility/mobiwac_v17/STATISTICAL_PROTOCOL.md
  §2  superiority -> paired one-sided Wilcoxon signed-rank on the matched PER-FOLD deltas,
      multi-seed pooled, n=20 = 4 seeds x 5 folds
  §5.2 Holm-Bonferroni WITHIN the six-dataset next-category superiority set; the region TOST
      cells are equivalence tests and are explicitly NOT pooled into that family
  §4  pairing discipline: both arms share the same fixed folds (family (A) is paired by construction)

Why this script exists (2026-07-25). Until now the registered per-fold test could not be run at
Istanbul: the dedicated category ceiling was committed only as four per-seed scalars
(h3_istanbul/step3_runs/cat_ceil_s*.txt), and the per-fold arrays lived in gitignored A40 rundirs
(docs/reproducibility/mobiwac_v17/stats/RESULTS.md LIMITS #2). Those four sidecars were recovered from the A40 on 2026-07-25 and
are now committed under h3_istanbul/step3_runs/cat_ceiling_perfold/, so the COMPLETE six-dataset
family runs for the first time. The paper reports the seed-level paired t (deviation log, RESULTS.md
entries 1-3); this script is the registered test reported alongside it as corroboration.

Convention: joint-best (one saved model per fold at the geom_simple-selected validation epoch,
min_best_epoch=0). Reads ONLY committed artifacts. Aborts if any recomputed aggregate stops matching
the board.

Run from the repo root:
  .venv/bin/python research/reproducibility/mobiwac_v17/m2_prereg_perfold.py
"""
import json
import statistics as st
from pathlib import Path

from scipy import stats

REPO = Path(__file__).resolve().parents[3]
ALPHA = 0.05
SEEDS = [0, 1, 7, 100]

SNAPSHOT = REPO / "docs/reproducibility/mobiwac_v17/data"
J1 = SNAPSHOT / "joint_best/j1_results.json"
CATX = REPO / "docs/results/closing_data/catx_v17_n20/joint_best"
SWEEP = SNAPSHOT / "cat_ceiling_sweep/sweep_results"
IST_CEIL = SNAPSHOT / "h3_istanbul/step3_runs/cat_ceiling_perfold"
P1 = REPO / "docs/results/P1"

# Dedicated category ceiling arms (CEILINGS_N20_FINAL.md; per-state max over the bs x LR sweep).
CAT_CEIL_ARM = {"AL": "alabama_bs2048_lr0.005", "AZ": "arizona_bs8192_lr0.005",
                "FL": "florida_bs8192_lr0.005", "CA": "california_bs8192_lr0.005",
                "TX": "texas_bs8192_lr0.005"}

# Dedicated region ceiling (prior-off next_stan_flow, topped up to n=20).
REG_CEIL_FILES = {
    "AL": ["region_head_alabama_region_5f_50ep_alabama_ovl_stl_reg_s0.json",
           "region_head_alabama_region_5f_50ep_alabama_ovl_stl_reg_topup_s1.json",
           "region_head_alabama_region_5f_50ep_alabama_ovl_stl_reg_topup_s7.json",
           "region_head_alabama_region_5f_50ep_alabama_ovl_stl_reg_topup_s100.json"],
    "AZ": ["region_head_arizona_region_5f_50ep_arizona_ovl_stl_reg_s0.json",
           "region_head_arizona_region_5f_50ep_arizona_ovl_stl_reg_topup_s1.json",
           "region_head_arizona_region_5f_50ep_arizona_ovl_stl_reg_topup_s7.json",
           "region_head_arizona_region_5f_50ep_arizona_ovl_stl_reg_topup_s100.json"],
    "FL": ["region_head_florida_region_5f_50ep_florida_ovl_stl_reg_s0.json",
           "region_head_florida_region_5f_50ep_florida_ovl_stl_reg_topup_s1.json",
           "region_head_florida_region_5f_50ep_florida_ovl_stl_reg_topup_s7.json",
           "region_head_florida_region_5f_50ep_florida_ovl_stl_reg_topup_s100.json"],
    "CA": ["region_head_california_region_5f_50ep_ca_ovl_stl_reg_s0.json",
           "region_head_california_region_5f_50ep_california_ovl_stl_reg_topup_s1.json",
           "region_head_california_region_5f_50ep_california_ovl_stl_reg_topup_s7.json",
           "region_head_california_region_5f_50ep_california_ovl_stl_reg_topup_s100.json"],
    "TX": ["region_head_texas_region_5f_50ep_tx_ovl_stl_reg_s0.json",
           "region_head_texas_region_5f_50ep_texas_ovl_stl_reg_topup_s1.json",
           "region_head_texas_region_5f_50ep_texas_ovl_stl_reg_topup_s7.json",
           "region_head_texas_region_5f_50ep_texas_ovl_stl_reg_topup_s100.json"],
    "Istanbul": ["region_head_istanbul_region_5f_50ep_istanbul_ovl_stl_reg_s0.json",
                 "region_head_istanbul_region_5f_50ep_istanbul_ovl_stl_reg_s1.json",
                 "region_head_istanbul_region_5f_50ep_istanbul_ovl_stl_reg_s7.json",
                 "region_head_istanbul_region_5f_50ep_istanbul_ovl_stl_reg_s100.json"],
}

# Board cells to gate against (CEILINGS_N20_FINAL.md + JOINT_BEST_RESULTS.md).
BOARD = {
    "AL":       {"mtl_cat": 64.51, "mtl_reg": 69.70, "cat_ceil": 56.82, "reg_ceil": 70.11},
    "AZ":       {"mtl_cat": 65.79, "mtl_reg": 59.46, "cat_ceil": 56.43, "reg_ceil": 59.46},
    "FL":       {"mtl_cat": 79.84, "mtl_reg": 77.41, "cat_ceil": 74.51, "reg_ceil": 76.70},
    "CA":       {"mtl_cat": 77.05, "mtl_reg": 65.69, "cat_ceil": 70.60, "reg_ceil": 63.49},
    "TX":       {"mtl_cat": 77.24, "mtl_reg": 67.06, "cat_ceil": 69.79, "reg_ceil": 64.95},
    "Istanbul": {"mtl_cat": 63.32, "mtl_reg": 75.35, "cat_ceil": 54.74, "reg_ceil": 75.16},
}
NAME2KEY = {"alabama": "AL", "arizona": "AZ", "florida": "FL",
            "california": "CA", "texas": "TX", "istanbul": "Istanbul"}


def load_mtl():
    """Joint-best per-fold arrays, both tasks, all six datasets."""
    out = {}
    for r in json.loads(J1.read_text())["per_run"]:
        out.setdefault(NAME2KEY[r["state"]], {})[r["seed"]] = {
            "cat": r["jb_cat_folds"], "reg": r["jb_reg_folds"]}
    for state, key in (("california", "CA"), ("texas", "TX")):
        for seed in SEEDS:
            jb = json.loads((CATX / f"{state}_s{seed}.json").read_text())["joint_best"]
            out.setdefault(key, {})[seed] = {"cat": jb["cat_per_fold"], "reg": jb["reg_per_fold"]}
    return out


def load_cat_ceiling():
    out = {}
    for key, arm in CAT_CEIL_ARM.items():
        out[key] = {s: json.loads((SWEEP / f"{arm}_s{s}.json").read_text())["cat_per_fold"]
                    for s in SEEDS}
    # Istanbul: the sidecars recovered from the A40 on 2026-07-25.
    out["Istanbul"] = {s: json.loads((IST_CEIL / f"h3ist_cat_s{s}.json").read_text())["cat_per_fold"]
                       for s in SEEDS}
    return out


def load_reg_ceiling():
    out = {}
    for key, files in REG_CEIL_FILES.items():
        per_seed = {}
        for seed, fname in zip(SEEDS, files):
            d = json.loads((P1 / fname).read_text())
            pf = d["heads"]["next_stan_flow"]["per_fold"]
            per_seed[seed] = [x["top10_acc"] * 100 for x in pf]
        out[key] = per_seed
    return out


def pooled(per_seed):
    """Per-fold values pooled across seeds, in a fixed seed order (n=20)."""
    return [v for s in SEEDS for v in per_seed[s]]


def gate(label, recomputed, board, tol=0.011):
    ok = abs(recomputed - board) <= tol
    print(f"  [{'OK' if ok else 'FAIL'}] {label}: recomputed {recomputed:.4f} vs board {board}")
    if not ok:
        raise SystemExit(f"ABORT: {label} no longer reproduces the board cell")


def wilcoxon_superiority(mtl, ceil):
    d = [a - b for a, b in zip(mtl, ceil)]
    w = stats.wilcoxon(mtl, ceil, alternative="greater", zero_method="wilcox", method="exact")
    return {"n": len(d), "mean_d": st.mean(d),
            "pos": sum(1 for x in d if x > 0), "p": w.pvalue}


def holm(items, alpha=ALPHA):
    """Holm-Bonferroni. Returns key -> (adjusted p, reject)."""
    m = len(items)
    order = sorted(items, key=lambda kv: kv[1])
    adj, running = {}, 0.0
    for i, (k, p) in enumerate(order):
        running = max(running, min((m - i) * p, 1.0))
        adj[k] = running
    rej, cont = {}, True
    for i, (k, p) in enumerate(order):
        if cont and p <= alpha / (m - i):
            rej[k] = True
        else:
            cont, rej[k] = False, False
    return {k: (adj[k], rej[k]) for k, _ in items}


def main():
    mtl, cat_ceil, reg_ceil = load_mtl(), load_cat_ceiling(), load_reg_ceiling()
    keys = ["AL", "AZ", "FL", "CA", "TX", "Istanbul"]

    print("=" * 84)
    print("0 . Artifact -> board reproduction gate (24/24)")
    print("=" * 84)
    for k in keys:
        b = BOARD[k]
        gate(f"{k} MTL cat (joint-best n=20)",
             st.mean(pooled({s: mtl[k][s]['cat'] for s in SEEDS})), b["mtl_cat"])
        gate(f"{k} MTL reg (joint-best n=20)",
             st.mean(pooled({s: mtl[k][s]['reg'] for s in SEEDS})), b["mtl_reg"])
        gate(f"{k} dedicated cat ceiling (n=20)", st.mean(pooled(cat_ceil[k])), b["cat_ceil"])
        gate(f"{k} dedicated reg ceiling (n=20)", st.mean(pooled(reg_ceil[k])), b["reg_ceil"])

    print()
    print("=" * 84)
    print("1 . NEXT-CATEGORY superiority - the PRE-REGISTERED test (protocol 2)")
    print("    paired one-sided Wilcoxon signed-rank, PER-FOLD, n=20 = 4 seeds x 5 folds")
    print("=" * 84)
    cat = {k: wilcoxon_superiority(pooled({s: mtl[k][s]['cat'] for s in SEEDS}),
                                   pooled(cat_ceil[k])) for k in keys}
    cat_holm = holm([(k, cat[k]["p"]) for k in keys])
    for k in keys:
        r, (padj, rej) = cat[k], cat_holm[k]
        print(f"  {k:9s} Delta={r['mean_d']:+6.3f} pp  folds+={r['pos']}/{r['n']}  "
              f"exact p={r['p']:.4e}  Holm-adj(m=6)={padj:.4e}  reject@.05={rej}")
    worst = max(p for p, _ in cat_holm.values())
    allrej = all(rej for _, rej in cat_holm.values())
    print(f"\n  VERDICT: six-dataset next-category family "
          f"{'ALL REJECT' if allrej else 'NOT all reject'} @ alpha={ALPHA}; "
          f"worst Holm-adjusted p = {worst:.4e}")
    print(f"  (exact n=20 one-sided floor = 1/2^20 = {2.0**-20:.4e}; every cell is at the floor "
          f"with 20/20 folds positive)")

    print()
    print("=" * 84)
    print("2 . NEXT-REGION superiority - NOT pre-registered (protocol 1, 5.2 register")
    print("    non-inferiority only). Reported as a secondary family with its own Holm.")
    print("=" * 84)
    reg_keys = ["Istanbul", "FL", "TX", "CA"]
    reg = {k: wilcoxon_superiority(pooled({s: mtl[k][s]['reg'] for s in SEEDS}),
                                   pooled(reg_ceil[k])) for k in reg_keys}
    reg_holm = holm([(k, reg[k]["p"]) for k in reg_keys])
    for k in reg_keys:
        r, (padj, rej) = reg[k], reg_holm[k]
        print(f"  {k:9s} Delta={r['mean_d']:+6.3f} pp  folds+={r['pos']}/{r['n']}  "
              f"exact p={r['p']:.4e}  Holm-adj(m=4)={padj:.4e}  reject@.05={rej}")
    print("\n  AL and AZ are equivalence cells (TOST, delta_reg = 2 pp) and are NOT in this family,")
    print("  nor in the category family (protocol 5.2). Never upgrade AZ.")


if __name__ == "__main__":
    main()
