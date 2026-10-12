#!/usr/bin/env python
"""Figure 3 (MobiWac 2026): category embedding-quality panel.

Plots two category-separability metrics, each computed on the ground-truth
seven next-category labels (NOT on discovered k-means clusters), on which the
check-in-level Check2HGI representation scores far higher than the place-level
HGI embedding:

  * cosine silhouette on the next-category labels
        (check2hgi_v18 ~0.51  vs  hgi ~0.00)
  * leave-one-out kNN (k=10) classification purity on those same labels
        (check2hgi_v18 ~0.98  vs  hgi ~0.78)

Both bars are metrics evaluated against the ground-truth category labels; no
clustering / k-means is run, and neither bar is a model "accuracy" result.

Region geometry is deliberately NOT shown: on region both engines are at the
floor and HGI scores spuriously higher, which would mislead. The story here is
strictly that the check-in-level substrate separates by category; its
region-neutral behavior is carried in the caption, not in this panel.

Source: docs/results/closing_data/v18/geometry/metrics_long.csv (committed
198eb2e8; engine check2hgi_v18 vs hgi, metrics silhouette + knn10_acc), mean and
SD (ddof=1) over the 25 state-folds of the five Gowalla states of the study.
[2026-09-30] Re-measured on the DELIVERED representation (check2hgi_v18). Until
this date the constants came from the earlier design_k build
(check2hgi_design_k_resln_mae_l0_1, 0.5668 / 0.9827), which the chapter's prose
had to scope as "an earlier build"; the author ruled that the text describes the
delivered method, so the figure now plots the delivered build.

Run:
  /Users/vitor/Desktop/mestrado/ingred/.venv/bin/python fig3_embquality_diss.py
Writes: fig3_embquality.pdf  (this directory)
"""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

# ---------------------------------------------------------------------------
# Authoritative numbers: docs/results/closing_data/v18/geometry/metrics_long.csv,
# engine check2hgi_v18 vs hgi, mean +/- SD (ddof=1) over the 25 state-fold values
# of the five Gowalla states. CATEGORY metrics only; region omitted.
# ---------------------------------------------------------------------------
METRICS = ["Silhouette\n(by category)", "kNN purity\n(by category, k=10)"]

CHECK2HGI = {"mean": [0.5140, 0.9804], "sd": [0.0533, 0.0065]}
HGI = {"mean": [0.0003, 0.7750], "sd": [0.0046, 0.0311]}

# Colors: a saturated accent for the contributed substrate, a muted gray for
# the place-embedding baseline so the contrast reads at IEEE column size.
C_CHECK2HGI = "#1f4e79"  # deep blue  -- Check2HGI (ours)
C_HGI = "#b0b0b0"        # neutral gray -- HGI (place embedding)


def main() -> None:
    plt.rcParams.update(
        {
            "font.size": 10,
            "font.family": "serif",
            "axes.linewidth": 0.6,
            "xtick.major.width": 0.6,
            "ytick.major.width": 0.6,
            "pdf.fonttype": 42,  # embed TrueType (no Type-3) for IEEE
            "ps.fonttype": 42,
        }
    )

    x = np.arange(len(METRICS))
    width = 0.36

    # ~3.3 in wide single-column IEEE figure.
    fig, ax = plt.subplots(figsize=(5.2, 2.4))

    b1 = ax.bar(
        x - width / 2,
        CHECK2HGI["mean"],
        width,
        yerr=CHECK2HGI["sd"],
        capsize=2.5,
        color=C_CHECK2HGI,
        edgecolor="black",
        linewidth=0.5,
        error_kw={"elinewidth": 0.7, "capthick": 0.7},
        label="Check2HGI (check-in level)",
    )
    b2 = ax.bar(
        x + width / 2,
        HGI["mean"],
        width,
        yerr=HGI["sd"],
        capsize=2.5,
        color=C_HGI,
        edgecolor="black",
        linewidth=0.5,
        error_kw={"elinewidth": 0.7, "capthick": 0.7},
        label="HGI (place embedding)",
    )

    # Numeric labels above each bar.
    def annotate(bars, means, sds):
        for rect, m, s in zip(bars, means, sds):
            ax.text(
                rect.get_x() + rect.get_width() / 2.0,
                m + s + 0.025,
                f"{m:.2f}",
                ha="center",
                va="bottom",
                fontsize=8.5,
            )

    annotate(b1, CHECK2HGI["mean"], CHECK2HGI["sd"])
    annotate(b2, HGI["mean"], HGI["sd"])

    ax.set_ylim(0, 1.14)
    ax.set_yticks([0.0, 0.5, 1.0])
    # REV-022 (2026-07-26): was "Score (0–1)". The left bar group is a cosine silhouette, which is
    # defined on [-1, 1], not [0, 1] (the chapter's own prose says so at section 5.6.1). The
    # plotted values are all non-negative, so nothing was misdrawn, but the label asserted a range
    # that is wrong for one of the two metrics. Each metric's own range is stated in the caption
    # and in the prose, so the axis carries the bare quantity name.
    ax.set_ylabel("Score")
    ax.set_xticks(x)
    ax.set_xticklabels(METRICS)
    ax.tick_params(axis="x", length=0)
    ax.axhline(0, color="black", linewidth=0.6)

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.yaxis.grid(True, linewidth=0.4, color="0.85", zorder=0)
    ax.set_axisbelow(True)

    ax.legend(
        loc="upper center",
        bbox_to_anchor=(0.5, 1.18),
        ncol=2,
        frameon=False,
        fontsize=8.5,
        handlelength=1.2,
        columnspacing=1.0,
        handletextpad=0.5,
    )

    fig.tight_layout(pad=0.4)
    out = Path(__file__).resolve().parent / "fig3_embquality.pdf"
    fig.savefig(out, bbox_inches="tight", pad_inches=0.02)
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
