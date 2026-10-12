#!/usr/bin/env python3
"""Plot task-gradient cosine cos(∇L_cat, ∇L_reg) on the shared trunk over training.
The finding: cosine ≈ 0 → the two tasks' gradients are orthogonal → there is no
gradient conflict for MTL balancers (PCGrad/CAGrad/Nash/GradNorm/...) to resolve,
which is why tuned static scalarization is on the Pareto front (T4 audit, 2026-06-08).

2026-06-12 (HANDOFF_AUDIT H1): widened from 2 static_weight-screen runs (seed 0) to
the FULL champion-G evidence base — the 16 R0-bar G rundirs (4 states × 4 seeds),
read straight from R0_matched_metric_bar.json → g_rundirs. Each state line is the
mean over its 4 seeds; the title carries the pooled mean and the total epoch-fold n.
"""
import csv, glob, json
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

R0 = json.load(open("docs/results/mtl_improvement/R0_matched_metric_bar.json"))
STATE_STYLE = {
    "florida": ("Florida (large · ~4,700 regions)", "#1f77b4"),
    "alabama": ("Alabama (small · ~1,100 regions)", "#d62728"),
    "arizona": ("Arizona", "#2ca02c"),
    "georgia": ("Georgia", "#9467bd"),
}


def load_state(rundirs):
    """Mean/std of grad_cosine_shared per epoch, pooled over all (seed, fold) CSVs
    of one state. Returns (epochs, mean, std, all_values)."""
    per_ep = {}
    allv = []
    for rd in rundirs.values():
        for f in sorted(glob.glob(rd + "/diagnostics/fold*_diagnostics.csv")):
            for r in csv.DictReader(open(f)):
                v = r.get("grad_cosine_shared")
                if v in (None, "", "nan"):
                    continue
                try:
                    ep = int(float(r["epoch"])); val = float(v)
                except (ValueError, KeyError):
                    continue
                per_ep.setdefault(ep, []).append(val)
                allv.append(val)
    eps = sorted(per_ep)
    mean = np.array([np.mean(per_ep[e]) for e in eps])
    std = np.array([np.std(per_ep[e]) for e in eps])
    return np.array(eps), mean, std, np.array(allv)


fig, ax = plt.subplots(figsize=(9, 5.2))
pooled = []
n_total = 0
n_runs = 0
for state, (label, color) in STATE_STYLE.items():
    g = R0["states"].get(state, {}).get("g_rundirs", {})
    if not g:
        continue
    n_runs += len(g)
    eps, mean, std, allv = load_state(g)
    if allv.size == 0:
        continue
    pooled.append(allv)
    n_total += allv.size
    ax.plot(eps, mean, color=color, lw=2.0,
            label=f"{label}   (mean = {allv.mean():+.3f}, {len(g)} seeds)")
    ax.fill_between(eps, mean - std, mean + std, color=color, alpha=0.12)

pooled = np.concatenate(pooled)
pooled_mean = pooled.mean()

ax.axhline(0.0, color="black", lw=1.0, ls="--", alpha=0.7)
ax.axhspan(-0.05, 0.05, color="grey", alpha=0.10)
ax.text(0.99, 0.05, "orthogonal band  (|cos| < 0.05)", transform=ax.get_yaxis_transform(),
        ha="right", va="bottom", fontsize=8, color="grey")

ax.set_xlabel("Training epoch", fontsize=11)
ax.set_ylabel(r"cosine$\,(\nabla \mathcal{L}_{\mathrm{cat}},\ \nabla \mathcal{L}_{\mathrm{reg}})$"
              "\non shared parameters", fontsize=11)
ax.set_title("Next-category vs. next-region gradients are orthogonal\n"
             f"→ no task conflict for MTL gradient-balancers to resolve  "
             f"(pooled mean = {pooled_mean:+.4f})",
             fontsize=12.5, fontweight="bold")
ax.set_ylim(-0.35, 0.35)
ax.legend(loc="upper right", fontsize=9, framealpha=0.9)
ax.grid(True, alpha=0.25)
fig.text(0.5, -0.02,
         f"Champion-G recipe (static_weight) · {n_runs} runs = 4 states × 4 seeds · "
         f"per-state mean ± 1 s.d. over (seed,fold,epoch) · n={n_total} epoch-fold points · "
         "PoiMTLnet / Check2HGI",
         ha="center", fontsize=8, color="#444")
fig.tight_layout()
out = "docs/studies/mtl_improvement/figs/grad_cosine_tasks.png"
fig.savefig(out, dpi=200, bbox_inches="tight")
print("wrote", out)
print(f"pooled mean cosine = {pooled_mean:+.4f}  over n={n_total} epoch-fold points "
      f"({n_runs} runs, 4 states × 4 seeds)")
