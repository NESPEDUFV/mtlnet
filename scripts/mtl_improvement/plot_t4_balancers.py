#!/usr/bin/env python3
"""Two T4 companion figures:
  (A) balancer scatter — cat-F1 vs reg-Acc@10 (matched) per balancer at FL; they all
      cluster at the equal-weight point and NONE Pareto-beats tuned static_weight (G).
  (B) normalized reg loss-weight trajectories — shows which balancers actually engage
      (static fixed; nash adapts; gradnorm/dwa frozen at ~equal; cagrad collapses).
"""
import csv, glob, json
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

V14 = "results/check2hgi_design_k_resln_mae_l0_1"
MAN = {}
for l in open("scripts/mtl_improvement/t4_full_manifest.tsv"):
    p = l.rstrip().split("\t")
    if len(p) >= 3:
        MAN[p[0]] = (p[1], p[2])

CEIL = {"florida": (73.27, 69.96)}  # (c) reg ceiling, cat ceiling (full / multiseed)


def rf_cat(rd):
    folds = []
    for f in sorted(glob.glob(rd + "/metrics/fold*_next_region_val.csv")):
        rows = list(csv.DictReader(open(f)))
        b = max(rows, key=lambda r: float(r["top10_acc_indist"]))
        folds.append(float(b["top10_acc_indist"]) * (1 - float(b["ood_fraction"])) * 100)
    d = json.load(open(rd + "/summary/full_summary.json"))
    return float(np.mean(folds)), d["diagnostic_task_best"]["next_category"]["f1"]["mean"] * 100


# ---------- Figure A: scatter (FL) ----------
state = "florida"
pts = {}
for key, (arm, rd) in MAN.items():
    if not key.endswith("|" + state):
        continue
    try:
        pts[arm] = rf_cat(rd)
    except Exception:
        pass
# exclude the catastrophically-broken scale_norm (reg 35) so the cluster is legible
pts.pop("scale_norm", None)

fig, ax = plt.subplots(figsize=(8.4, 6.0))
creg, ccat = CEIL[state]
for arm, (reg, cat) in pts.items():
    if arm == "static_weight":
        ax.scatter(cat, reg, s=160, c="#d62728", marker="*", zorder=5,
                   edgecolor="black", linewidth=0.6, label="static_weight 0.75/0.25 (champion G)")
        ax.annotate("G (static)", (cat, reg), textcoords="offset points", xytext=(8, 4),
                    fontsize=9, fontweight="bold", color="#d62728")
    elif arm == "equal_weight":
        ax.scatter(cat, reg, s=110, c="#2ca02c", marker="D", zorder=4,
                   edgecolor="black", linewidth=0.5, label="equal_weight (1/1)")
        ax.annotate("equal", (cat, reg), textcoords="offset points", xytext=(6, -10), fontsize=8, color="#2ca02c")
    else:
        ax.scatter(cat, reg, s=55, c="#1f77b4", alpha=0.75, zorder=3)
        ax.annotate(arm, (cat, reg), textcoords="offset points", xytext=(4, 3), fontsize=6.5, color="#33558c")
# ceiling reference lines
ax.axhline(creg, color="grey", ls=":", lw=1.0); ax.text(ax.get_xlim()[0], creg, " STL reg ceiling", va="bottom", ha="left", fontsize=7.5, color="grey")
ax.set_xlabel("next-category   macro-F1  (%)", fontsize=11)
ax.set_ylabel("next-region   Acc@10 (matched, %)", fontsize=11)
ax.set_title("Every MTL balancer clusters near equal-weighting;\n"
             "none Pareto-beats tuned static_weight (Florida, seed 0)",
             fontsize=12.5, fontweight="bold")
ax.annotate("advanced balancers trade ~1.3 pp cat for ~0.1 pp reg →\n"
            "static keeps the best cat; no Pareto gain",
            xy=(0.02, 0.02), xycoords="axes fraction", fontsize=8.5, color="#444",
            va="bottom", ha="left")
ax.legend(loc="lower right", fontsize=8.5, framealpha=0.9)
ax.grid(True, alpha=0.25)
fig.tight_layout()
outA = "docs/studies/mtl_improvement/figs/t4_balancer_scatter_FL.png"
fig.savefig(outA, dpi=200, bbox_inches="tight"); print("wrote", outA)


# ---------- Figure B: normalized reg loss-weight trajectories (FL fold1) ----------
def reg_weight_traj(arm):
    key = arm + "|florida"
    if key not in MAN:
        return None
    rd = MAN[key][1]
    f = rd + "/diagnostics/fold1_diagnostics.csv"
    eps, wn = [], []
    for r in csv.DictReader(open(f)):
        wr = r.get("loss_weight_next_region"); wc = r.get("loss_weight_next_category")
        if wr in (None, "", "nan") or wc in (None, "", "nan"):
            continue
        wr, wc = float(wr), float(wc)
        s = wr + wc
        if s <= 0:
            continue
        eps.append(int(float(r["epoch"]))); wn.append(wr / s)  # normalized reg share
    return np.array(eps), np.array(wn)

fig2, ax2 = plt.subplots(figsize=(9, 5.2))
SHOW = [("static_weight", "#d62728", "-", "static_weight (fixed 0.25)"),
        ("nash_mtl", "#1f77b4", "-", "Nash-MTL (adapts)"),
        ("cagrad", "#9467bd", "-", "CAGrad (collapses → 0)"),
        ("gradnorm", "#2ca02c", "--", "GradNorm (frozen ≈ 0.5)"),
        ("dwa", "#8c564b", "--", "DWA (pinned ≈ 0.5)"),
        ("uncertainty_weighting", "#ff7f0e", "-", "Uncertainty-W. (adapts)")]
for arm, color, ls, lab in SHOW:
    t = reg_weight_traj(arm)
    if t is None or len(t[0]) == 0:
        continue
    ax2.plot(t[0], t[1], color=color, ls=ls, lw=1.9, label=lab)
ax2.axhline(0.5, color="black", lw=0.8, ls=":", alpha=0.6)
ax2.text(ax2.get_xlim()[1], 0.5, " equal", va="bottom", ha="right", fontsize=8, color="black")
ax2.set_xlabel("Training epoch", fontsize=11)
ax2.set_ylabel("normalized reg loss-weight\n$w_{\\mathrm{reg}}/(w_{\\mathrm{reg}}+w_{\\mathrm{cat}})$", fontsize=11)
ax2.set_ylim(-0.02, 1.02)
ax2.set_title("Why the balancers cluster: most don't actually move off equal-weighting\n"
             "(GradNorm/DWA frozen; CAGrad collapses; only Nash/UW adapt) — Florida fold 1",
             fontsize=12, fontweight="bold")
ax2.legend(loc="center right", fontsize=8.5, framealpha=0.9)
ax2.grid(True, alpha=0.25)
fig2.tight_layout()
outB = "docs/studies/mtl_improvement/figs/t4_loss_weight_trajectories_FL.png"
fig2.savefig(outB, dpi=200, bbox_inches="tight"); print("wrote", outB)
