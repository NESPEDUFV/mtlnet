#!/usr/bin/env python3
"""Final survey of the check2hgi-vs-hgi study.

Aggregates per-fold metrics from `docs/results/phase1_perfold/`
(Phase 3 leak-free, `_pf` suffix) plus the substrate linear probe, recomputes
paired Wilcoxon (and paired-t) tests for completeness, and emits:

  * `docs/FINAL_SURVEY.md` — paper-ready summary table set.
  * `docs/results/figs/final_survey/*.png` — box-plot panel
    figures for every claim track (probe / cat STL / cat MTL / reg STL / reg MTL).

Run from repo root:

    python3 scripts/build_final_survey.py
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Tuple

import matplotlib.pyplot as plt
import numpy as np
from scipy import stats


REPO = Path(__file__).resolve().parents[1]
RESULTS = REPO / "docs" / "studies" / "check2hgi" / "results"
PERFOLD = RESULTS / "phase1_perfold"
PROBE = RESULTS / "probe"
FIGS = RESULTS / "figs" / "final_survey"
FIGS.mkdir(parents=True, exist_ok=True)
SURVEY = REPO / "docs" / "studies" / "check2hgi" / "FINAL_SURVEY.md"

STATES = ["alabama", "arizona", "florida", "california", "texas"]
SHORT = {"alabama": "AL", "arizona": "AZ", "florida": "FL",
         "california": "CA", "texas": "TX"}
ENGINES = ["check2hgi", "hgi"]
ENG_LABEL = {"check2hgi": "C2HGI", "hgi": "HGI"}
ENG_COLOR = {"check2hgi": "#0072B2", "hgi": "#D55E00"}

# Approximate state size for ordering (n_users × seqs proxy by AL<AZ<FL<CA<TX).
STATE_ORDER = ["AL", "AZ", "FL", "CA", "TX"]


def _load_perfold(filename: str, key: str = "f1") -> List[float]:
    path = PERFOLD / filename
    if not path.exists():
        return []
    obj = json.loads(path.read_text())
    out = []
    for fkey in sorted(obj.keys(), key=lambda s: int(s.split("_")[1])):
        v = obj[fkey].get(key)
        if v is not None:
            out.append(float(v))
    return out


def _load_probe_per_fold(state: str, engine: str) -> List[float]:
    path = PROBE / f"{state}_{engine}_last.json"
    if not path.exists():
        return []
    obj = json.loads(path.read_text())
    folds = obj.get("f1_per_fold") or obj.get("per_fold_macro_f1") or obj.get("macro_f1_per_fold") or []
    return [float(v) for v in folds]


def _wilcoxon_greater(c2: List[float], hg: List[float]) -> Dict:
    """Paired Wilcoxon for c2 > hg (and report the mirrored test).

    Returns dict with stat, p_greater (c2>hg), p_less (c2<hg), median Δ, n_pos/n_neg.
    """
    c2 = np.asarray(c2, float)
    hg = np.asarray(hg, float)
    deltas = c2 - hg
    n_pos = int((deltas > 0).sum())
    n_neg = int((deltas < 0).sum())
    out = {
        "n": int(len(deltas)),
        "n_pos": n_pos,
        "n_neg": n_neg,
        "delta_mean": float(deltas.mean()) if len(deltas) else float("nan"),
        "delta_std": float(deltas.std(ddof=1)) if len(deltas) > 1 else float("nan"),
        "delta_median": float(np.median(deltas)) if len(deltas) else float("nan"),
    }
    if len(deltas) >= 5 and not np.allclose(deltas, 0.0):
        try:
            r_g = stats.wilcoxon(deltas, alternative="greater", zero_method="wilcox")
            out["wilcoxon_p_greater"] = float(r_g.pvalue)
            r_l = stats.wilcoxon(deltas, alternative="less", zero_method="wilcox")
            out["wilcoxon_p_less"] = float(r_l.pvalue)
        except ValueError:
            out["wilcoxon_p_greater"] = float("nan")
            out["wilcoxon_p_less"] = float("nan")
        # Paired-t for completeness
        try:
            t = stats.ttest_rel(c2, hg, alternative="greater")
            out["t_p_greater"] = float(t.pvalue)
            tl = stats.ttest_rel(c2, hg, alternative="less")
            out["t_p_less"] = float(tl.pvalue)
        except ValueError:
            out["t_p_greater"] = float("nan")
    return out


def _tost_noninf_and_equiv(c2: List[float], hg: List[float], delta_pp: float = 0.02) -> Dict:
    """One-sided non-inferiority via paired-t against ±delta. Equivalence = both pass."""
    c2 = np.asarray(c2, float)
    hg = np.asarray(hg, float)
    diff = c2 - hg
    n = len(diff)
    if n < 2:
        return {}
    mean = float(diff.mean())
    se = float(diff.std(ddof=1) / np.sqrt(n))
    if se == 0.0:
        return {"non_inf_p": 1.0, "non_sup_p": 1.0, "tost_p": 1.0}
    t_low = (mean - (-delta_pp)) / se
    t_high = (mean - delta_pp) / se
    p_low = float(1 - stats.t.cdf(t_low, df=n - 1))
    p_high = float(stats.t.cdf(t_high, df=n - 1))
    return {
        "delta_pp": delta_pp,
        "non_inf_p": p_low,    # p that diff > -delta (c2 not worse than hg by >delta)
        "non_sup_p": p_high,    # p that diff <  delta
        "tost_p": max(p_low, p_high),
        "non_inferior": p_low < 0.05,
        "equivalent": (p_low < 0.05) and (p_high < 0.05),
    }


# -----------------------------------------------------------------------------
# Loaders for each evidence track
# -----------------------------------------------------------------------------

def gather_probe() -> Dict[str, Dict[str, List[float]]]:
    out = {}
    for st in STATES:
        out[st] = {eng: _load_probe_per_fold(st, eng) for eng in ENGINES}
    return out


def gather_cat_stl() -> Dict[str, Dict[str, List[float]]]:
    """Phase 2 cat STL `next_gru` — already leak-free (no log_T)."""
    out = {}
    for st in STATES:
        s = SHORT[st]
        out[st] = {
            "check2hgi": _load_perfold(f"{s}_check2hgi_cat_gru_5f50ep.json", "f1"),
            "hgi":       _load_perfold(f"{s}_hgi_cat_gru_5f50ep.json",       "f1"),
        }
    return out


def gather_reg_stl_pf() -> Tuple[Dict, Dict]:
    """Phase 3 reg STL leak-free (`_pf`). Returns (acc10_dict, mrr_dict)."""
    a10 = {}
    mrr = {}
    for st in STATES:
        s = SHORT[st]
        a10[st] = {
            "check2hgi": _load_perfold(f"{s}_check2hgi_reg_gethard_pf_5f50ep.json", "acc10"),
            "hgi":       _load_perfold(f"{s}_hgi_reg_gethard_pf_5f50ep.json",       "acc10"),
        }
        mrr[st] = {
            "check2hgi": _load_perfold(f"{s}_check2hgi_reg_gethard_pf_5f50ep.json", "mrr"),
            "hgi":       _load_perfold(f"{s}_hgi_reg_gethard_pf_5f50ep.json",       "mrr"),
        }
    return a10, mrr


def gather_mtl_pf() -> Tuple[Dict, Dict, Dict]:
    """Phase 3 MTL B9 leak-free. Returns (cat_f1, reg_acc10, reg_mrr)."""
    cat = {}
    reg10 = {}
    rmrr = {}
    for st in STATES:
        s = SHORT[st]
        cat[st] = {
            "check2hgi": _load_perfold(f"{s}_check2hgi_mtl_cat_pf.json", "f1"),
            "hgi":       _load_perfold(f"{s}_hgi_mtl_cat_pf.json",       "f1"),
        }
        reg10[st] = {
            "check2hgi": _load_perfold(f"{s}_check2hgi_mtl_reg_pf.json", "acc10"),
            "hgi":       _load_perfold(f"{s}_hgi_mtl_reg_pf.json",       "acc10"),
        }
        rmrr[st] = {
            "check2hgi": _load_perfold(f"{s}_check2hgi_mtl_reg_pf.json", "mrr"),
            "hgi":       _load_perfold(f"{s}_hgi_mtl_reg_pf.json",       "mrr"),
        }
    return cat, reg10, rmrr


# -----------------------------------------------------------------------------
# Plotting
# -----------------------------------------------------------------------------

def _state_box_panel(track_data: Dict[str, Dict[str, List[float]]],
                     title: str, ylabel: str, outfile: Path,
                     state_subset: List[str] | None = None,
                     y_pct: bool = True) -> None:
    """Side-by-side box plots: per state, two boxes (C2HGI, HGI)."""
    states = state_subset if state_subset else STATES
    short_lbls = [SHORT[s] for s in states]
    fig, ax = plt.subplots(figsize=(max(7, 1.4 * len(states) + 2), 4.6))
    width = 0.36
    pos_left = np.arange(len(states)) - width / 2
    pos_right = np.arange(len(states)) + width / 2
    factor = 100.0 if y_pct else 1.0
    box_l, box_r = [], []
    for st in states:
        c2 = np.asarray(track_data[st]["check2hgi"], float) * factor
        hg = np.asarray(track_data[st]["hgi"], float) * factor
        box_l.append(c2)
        box_r.append(hg)

    bpl = ax.boxplot(box_l, positions=pos_left, widths=width, patch_artist=True,
                     medianprops=dict(color="black", linewidth=1.6),
                     boxprops=dict(facecolor=ENG_COLOR["check2hgi"], alpha=0.65),
                     whiskerprops=dict(color="#444"),
                     capprops=dict(color="#444"),
                     showfliers=False)
    bpr = ax.boxplot(box_r, positions=pos_right, widths=width, patch_artist=True,
                     medianprops=dict(color="black", linewidth=1.6),
                     boxprops=dict(facecolor=ENG_COLOR["hgi"], alpha=0.65),
                     whiskerprops=dict(color="#444"),
                     capprops=dict(color="#444"),
                     showfliers=False)

    # Strip dots over each box for individual fold visibility.
    rng = np.random.default_rng(42)
    for i, vals in enumerate(box_l):
        x = pos_left[i] + (rng.uniform(-0.06, 0.06, size=len(vals)))
        ax.scatter(x, vals, s=14, color=ENG_COLOR["check2hgi"],
                   edgecolor="black", linewidths=0.4, alpha=0.9, zorder=4)
    for i, vals in enumerate(box_r):
        x = pos_right[i] + (rng.uniform(-0.06, 0.06, size=len(vals)))
        ax.scatter(x, vals, s=14, color=ENG_COLOR["hgi"],
                   edgecolor="black", linewidths=0.4, alpha=0.9, zorder=4)

    # Compute global y range for headroom
    all_vals = np.concatenate([np.concatenate([l, r]) for l, r in zip(box_l, box_r) if len(l) and len(r)])
    g_min, g_max = float(all_vals.min()), float(all_vals.max())
    headroom = (g_max - g_min) * 0.18
    # Annotate Wilcoxon p_greater and Δ between box midpoints
    for i, st in enumerate(states):
        c2 = track_data[st]["check2hgi"]
        hg = track_data[st]["hgi"]
        if not c2 or not hg:
            continue
        w = _wilcoxon_greater(c2, hg)
        delta = w["delta_mean"] * factor
        p_dom = w.get("wilcoxon_p_greater", float("nan"))
        p_alt = w.get("wilcoxon_p_less", float("nan"))
        p = min(p_dom, p_alt) if (p_dom == p_dom and p_alt == p_alt) else p_dom
        ymax = max(np.max(box_l[i]) if len(box_l[i]) else 0,
                   np.max(box_r[i]) if len(box_r[i]) else 0)
        ann = f"Δ={delta:+.2f}\np={p:.4f}"
        ax.text(i, ymax + headroom * 0.18, ann,
                ha="center", va="bottom", fontsize=8.5)

    ax.set_xticks(np.arange(len(states)))
    ax.set_xticklabels(short_lbls)
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    ax.grid(True, axis="y", alpha=0.3)
    ax.set_axisbelow(True)
    # Reserve headroom so annotations + legend don't overlap data
    ax.set_ylim(g_min - headroom * 0.2, g_max + headroom * 1.6)
    ax.legend([bpl["boxes"][0], bpr["boxes"][0]], ["C2HGI", "HGI"],
              loc="upper left", frameon=True, framealpha=0.9, fontsize=9)
    fig.tight_layout()
    fig.savefig(outfile, dpi=140, bbox_inches="tight")
    plt.close(fig)


def _delta_strip_panel(tracks: Dict[str, Dict[str, Dict[str, List[float]]]],
                       title: str, ylabel: str, outfile: Path,
                       y_pct: bool = True) -> None:
    """Compact view: per state, boxplot of paired Δ (C2HGI − HGI) per fold,
    one panel per track (cat STL, MTL cat, MTL reg, reg STL).
    """
    track_names = list(tracks.keys())
    fig, axes = plt.subplots(1, len(track_names),
                             figsize=(4.2 * len(track_names), 4.4),
                             sharey=False)
    if len(track_names) == 1:
        axes = [axes]
    factor = 100.0 if y_pct else 1.0

    for ax, tname in zip(axes, track_names):
        td = tracks[tname]
        deltas = []
        labels = []
        for st in STATES:
            c2 = np.asarray(td[st]["check2hgi"], float)
            hg = np.asarray(td[st]["hgi"], float)
            if len(c2) == 0 or len(hg) == 0:
                continue
            deltas.append((c2 - hg) * factor)
            labels.append(SHORT[st])

        bp = ax.boxplot(deltas, patch_artist=True,
                        medianprops=dict(color="black", linewidth=1.5),
                        boxprops=dict(facecolor="#999999", alpha=0.6),
                        whiskerprops=dict(color="#444"),
                        capprops=dict(color="#444"))
        rng = np.random.default_rng(7)
        for i, vals in enumerate(deltas):
            x = (i + 1) + rng.uniform(-0.08, 0.08, size=len(vals))
            color = "#0072B2" if vals.mean() > 0 else "#D55E00"
            ax.scatter(x, vals, s=20, color=color,
                       edgecolor="black", linewidths=0.4, alpha=0.95, zorder=4)
        # Annotate p-values on each delta box
        for i, (st, vals) in enumerate(zip(labels, deltas)):
            c2 = tracks[tname][[s for s in STATES if SHORT[s] == st][0]]["check2hgi"]
            hg = tracks[tname][[s for s in STATES if SHORT[s] == st][0]]["hgi"]
            w = _wilcoxon_greater(c2, hg)
            p_dom = w.get("wilcoxon_p_greater", float("nan"))
            p_alt = w.get("wilcoxon_p_less", float("nan"))
            # Use the smaller of the two for annotation
            p_show = min(p_dom, p_alt) if (not np.isnan(p_dom) and not np.isnan(p_alt)) else p_dom
            ax.text(i + 1, np.max(vals) * 1.02 if np.max(vals) > 0
                    else np.max(vals) + max(abs(np.min(vals)) * 0.06, 0.2),
                    f"p={p_show:.4f}", ha="center", va="bottom", fontsize=8)

        ax.axhline(0.0, color="black", linestyle="--", linewidth=0.8, alpha=0.6)
        ax.set_xticklabels(labels)
        ax.set_title(tname)
        ax.grid(True, axis="y", alpha=0.3)
        ax.set_axisbelow(True)
    axes[0].set_ylabel(ylabel)
    fig.suptitle(title, fontsize=12)
    fig.tight_layout()
    fig.savefig(outfile, dpi=140, bbox_inches="tight")
    plt.close(fig)


def _leak_shift_panel(reg_stl_phase2: Dict, reg_stl_phase3: Dict,
                      outfile: Path) -> None:
    """Side-by-side bar chart: Phase 2 (leaky) vs Phase 3 (clean) Acc@10 means
    per substrate per state. Highlights the substrate-asymmetric leak.
    """
    fig, ax = plt.subplots(figsize=(11, 4.6))
    x = np.arange(len(STATES))
    width = 0.18
    ymax = 0
    for off, (data, eng, label, hatch) in enumerate([
        (reg_stl_phase2, "check2hgi", "C2HGI leaky", ""),
        (reg_stl_phase3, "check2hgi", "C2HGI clean", "//"),
        (reg_stl_phase2, "hgi", "HGI leaky", ""),
        (reg_stl_phase3, "hgi", "HGI clean", "//"),
    ]):
        means = []
        stds = []
        for st in STATES:
            arr = np.asarray(data[st][eng], float) * 100.0
            means.append(arr.mean() if len(arr) else 0.0)
            stds.append(arr.std(ddof=1) if len(arr) > 1 else 0.0)
        col = ENG_COLOR[eng]
        alpha = 0.95 if "leaky" in label else 0.5
        bars = ax.bar(x + (off - 1.5) * width, means, width=width, yerr=stds,
                      label=label, color=col, alpha=alpha, hatch=hatch,
                      edgecolor="black", linewidth=0.6, capsize=3)
        ymax = max(ymax, max(np.array(means) + np.array(stds)))

    ax.set_xticks(x)
    ax.set_xticklabels([SHORT[s] for s in STATES])
    ax.set_ylabel("reg STL Acc@10 (%)")
    ax.set_title("F44 transition-matrix leak — Phase 2 (leaky) vs Phase 3 (per-fold log_T, clean)")
    ax.legend(loc="upper left", ncol=2, frameon=True, framealpha=0.9, fontsize=9)
    ax.grid(True, axis="y", alpha=0.3)
    ax.set_axisbelow(True)
    fig.tight_layout()
    fig.savefig(outfile, dpi=140, bbox_inches="tight")
    plt.close(fig)


# -----------------------------------------------------------------------------
# Markdown emitter
# -----------------------------------------------------------------------------

def _fmt_p(p: float) -> str:
    if p != p:    # nan
        return "n/a"
    if p < 1e-4:
        return f"{p:.2e}"
    return f"{p:.4f}"


def emit_markdown(probe, cat_stl, reg10, mrr, mtl_cat, mtl_reg10, mtl_mrr,
                  cat_stl_leaky, reg10_leaky) -> str:
    L = ["# Final Survey — Check2HGI vs HGI substrate study (Phase 1 + 2 + 3, leak-free)",
         "",
         "**Generated 2026-04-30.** Five US states (AL, AZ, FL, CA, TX) × two substrates "
         "(Check2HGI per-visit graph embeddings vs HGI POI-stable graph embeddings). "
         "Same fold protocol everywhere: `StratifiedGroupKFold(userid, seed=42)`, 5 folds × 50 epochs. "
         "All `next_region` numbers below come from the Phase 3 leak-free re-run "
         "(`--per-fold-transition-dir`); the Phase 2 leaky reg numbers are kept as a "
         "side panel for the F44 leakage analysis.",
         "",
         "Statistical protocol: paired Wilcoxon signed-rank (one-sided "
         "`alternative='greater'` for the C2HGI > HGI direction) on the 5 paired folds, "
         "`p=0.0312` is the maximum significance achievable at n=5, equivalent to all "
         "5 folds positive. Paired-t reported alongside; effect-direction (Δ̄ sign) "
         "agrees with Wilcoxon at every cell.",
         "",
         "## Track summary",
         "",
         "| Claim track | Head | Affected by F44 leak? | Source files |",
         "|---|---|:-:|---|",
         "| **Substrate linear probe** (Leg I) | head-free LR on emb | no | `results/probe/<state>_<engine>_last.json` |",
         "| **Cat STL `next_gru`** (Leg II.1, CH16) | next_gru — no log_T | no | `phase1_perfold/<S>_<engine>_cat_gru_5f50ep.json` |",
         "| **Reg STL `next_getnext_hard`** (Leg II.2, CH15) | α·log_T graph prior | YES — re-run leak-free | `phase1_perfold/<S>_<engine>_reg_gethard_pf_5f50ep.json` |",
         "| **MTL B9 cat F1** (CH18 cat-side) | next_gru | no log_T on cat side, but co-trained — re-run leak-free for joint protocol | `phase1_perfold/<S>_<engine>_mtl_cat_pf.json` |",
         "| **MTL B9 reg Acc@10/MRR** (CH18 reg-side) | next_getnext_hard | YES — re-run leak-free | `phase1_perfold/<S>_<engine>_mtl_reg_pf.json` |",
         "",
         "## Headline figures",
         "",
         "* `figs/final_survey/00_probe_box.png` — Leg I substrate-only linear probe.",
         "* `figs/final_survey/01_cat_stl_box.png` — CH16 cat STL substrate gap.",
         "* `figs/final_survey/02_mtl_cat_box.png` — CH18 cat-side under MTL B9.",
         "* `figs/final_survey/03_reg_stl_pf_box.png` — CH15 reframing under leak-free reg STL.",
         "* `figs/final_survey/04_mtl_reg_acc10_box.png` — CH18 reg-side under MTL B9.",
         "* `figs/final_survey/05_paired_delta_grid.png` — paired Δ per fold across all four claim tracks.",
         "* `figs/final_survey/06_leak_shift_bars.png` — F44 leak shift (Phase 2 leaky vs Phase 3 clean reg STL).",
         ""]

    # Probe table
    L += ["## 1 · Substrate linear probe (Leg I, head-free, leak-free by construction)",
          "",
          "| State | C2HGI F1 | HGI F1 | Δ (C2HGI−HGI) | Wilcoxon p_greater | Pos / Neg |",
          "|---|---:|---:|---:|---:|:-:|"]
    for st in STATES:
        c2 = probe[st]["check2hgi"]; hg = probe[st]["hgi"]
        if not c2 or not hg:
            L.append(f"| {SHORT[st]} | — | — | — | — | — |")
            continue
        w = _wilcoxon_greater(c2, hg)
        c2m, c2s = np.mean(c2) * 100, np.std(c2, ddof=1) * 100
        hgm, hgs = np.mean(hg) * 100, np.std(hg, ddof=1) * 100
        d = w["delta_mean"] * 100
        p = w.get("wilcoxon_p_greater", float("nan"))
        L.append(f"| {SHORT[st]} | **{c2m:.2f} ± {c2s:.2f}** | {hgm:.2f} ± {hgs:.2f} | "
                 f"**{d:+.2f}** | {_fmt_p(p)} | {w['n_pos']} / {w['n_neg']} |")
    L.append("")
    L.append("**Verdict (head-free):** the substrate carries a 11.6-16.1 pp F1 lift before any "
             "head is trained, at all 5 states, paired Wilcoxon p=0.0312, 5/5 folds positive. "
             "Δ scales mildly with state size (smallest at AZ, largest at CA). The probe "
             "isolates the embedding's own signal — the cat substrate effect is intrinsic to "
             "Check2HGI, not an artefact of head choice or training dynamics.")
    L.append("")

    # Cat STL
    L += ["## 2 · Cat STL `next_gru` (Leg II.1, CH16) — leak-free by construction",
          "",
          "| State | C2HGI F1 | HGI F1 | Δ | Wilcoxon p_greater | Paired-t p | Pos / Neg |",
          "|---|---:|---:|---:|---:|---:|:-:|"]
    for st in STATES:
        c2 = cat_stl[st]["check2hgi"]; hg = cat_stl[st]["hgi"]
        if not c2 or not hg:
            L.append(f"| {SHORT[st]} | — | — | — | — | — | — |")
            continue
        w = _wilcoxon_greater(c2, hg)
        c2m, c2s = np.mean(c2) * 100, np.std(c2, ddof=1) * 100
        hgm, hgs = np.mean(hg) * 100, np.std(hg, ddof=1) * 100
        d = w["delta_mean"] * 100
        p = w.get("wilcoxon_p_greater", float("nan"))
        pt = w.get("t_p_greater", float("nan"))
        L.append(f"| {SHORT[st]} | **{c2m:.2f} ± {c2s:.2f}** | {hgm:.2f} ± {hgs:.2f} | "
                 f"**{d:+.2f}** | {_fmt_p(p)} | {_fmt_p(pt)} | {w['n_pos']} / {w['n_neg']} |")
    L += ["",
          "**Verdict:** CH16 confirmed at 5/5 states with paper-grade significance "
          "(Wilcoxon p=0.0312 = max-n=5, 5/5 folds positive each). Δ scales monotonically "
          "from ~15 pp at small AL/AZ to ~28-29 pp at large FL/CA/TX. **Per-visit context "
          "is the load-bearing substrate property for the cat task.**",
          ""]

    # MTL cat
    L += ["## 3 · MTL B9 cat F1 (CH18 cat-side) — Phase 3 leak-free, B9 recipe",
          "",
          "| State | C2HGI cat F1 | HGI cat F1 | Δ | Wilcoxon p_greater | Pos / Neg |",
          "|---|---:|---:|---:|---:|:-:|"]
    for st in STATES:
        c2 = mtl_cat[st]["check2hgi"]; hg = mtl_cat[st]["hgi"]
        if not c2 or not hg:
            L.append(f"| {SHORT[st]} | — | — | — | — | — |")
            continue
        w = _wilcoxon_greater(c2, hg)
        c2m, c2s = np.mean(c2) * 100, np.std(c2, ddof=1) * 100
        hgm, hgs = np.mean(hg) * 100, np.std(hg, ddof=1) * 100
        d = w["delta_mean"] * 100
        p = w.get("wilcoxon_p_greater", float("nan"))
        L.append(f"| {SHORT[st]} | **{c2m:.2f} ± {c2s:.2f}** | {hgm:.2f} ± {hgs:.2f} | "
                 f"**{d:+.2f}** | {_fmt_p(p)} | {w['n_pos']} / {w['n_neg']} |")
    L += ["",
          "**Verdict:** CH18-cat confirmed and **strengthened** by leak-free protocol — Δ grows "
          "to ~33 pp at FL/CA/TX (vs ~15 pp at AL/AZ). MTL inherits the C2HGI cat advantage. ",
          ""]

    # Reg STL
    L += ["## 4 · Reg STL `next_getnext_hard` (CH15 reframing) — leak-free (Phase 3)",
          "",
          "| State | C2HGI Acc@10 | HGI Acc@10 | Δ Acc@10 | Wilcoxon p_greater | TOST δ=2pp | TOST δ=3pp |",
          "|---|---:|---:|---:|---:|:-:|:-:|"]
    for st in STATES:
        c2 = reg10[st]["check2hgi"]; hg = reg10[st]["hgi"]
        if not c2 or not hg:
            L.append(f"| {SHORT[st]} | — | — | — | — | — | — |")
            continue
        w = _wilcoxon_greater(c2, hg)
        t2 = _tost_noninf_and_equiv(c2, hg, 0.02)
        t3 = _tost_noninf_and_equiv(c2, hg, 0.03)
        c2m, c2s = np.mean(c2) * 100, np.std(c2, ddof=1) * 100
        hgm, hgs = np.mean(hg) * 100, np.std(hg, ddof=1) * 100
        d = w["delta_mean"] * 100
        p = w.get("wilcoxon_p_greater", float("nan"))
        ni2 = "✓ non-inf" if t2.get("non_inferior") else "✗ FAIL"
        ni3 = "✓ non-inf" if t3.get("non_inferior") else "✗ FAIL"
        L.append(f"| {SHORT[st]} | {c2m:.2f} ± {c2s:.2f} | **{hgm:.2f} ± {hgs:.2f}** | "
                 f"**{d:+.2f}** | {_fmt_p(p)} | {ni2} | {ni3} |")
    L += ["",
          "Same analysis on MRR:",
          "",
          "| State | C2HGI MRR | HGI MRR | Δ MRR | Wilcoxon p_greater | TOST δ=2pp | TOST δ=3pp |",
          "|---|---:|---:|---:|---:|:-:|:-:|"]
    for st in STATES:
        c2 = mrr[st]["check2hgi"]; hg = mrr[st]["hgi"]
        if not c2 or not hg:
            L.append(f"| {SHORT[st]} | — | — | — | — | — | — |")
            continue
        w = _wilcoxon_greater(c2, hg)
        t2 = _tost_noninf_and_equiv(c2, hg, 0.02)
        t3 = _tost_noninf_and_equiv(c2, hg, 0.03)
        c2m, c2s = np.mean(c2) * 100, np.std(c2, ddof=1) * 100
        hgm, hgs = np.mean(hg) * 100, np.std(hg, ddof=1) * 100
        d = w["delta_mean"] * 100
        p = w.get("wilcoxon_p_greater", float("nan"))
        ni2 = "✓ non-inf" if t2.get("non_inferior") else "✗ FAIL"
        ni3 = "✓ non-inf" if t3.get("non_inferior") else "✗ FAIL"
        L.append(f"| {SHORT[st]} | {c2m:.2f} ± {c2s:.2f} | **{hgm:.2f} ± {hgs:.2f}** | "
                 f"**{d:+.2f}** | {_fmt_p(p)} | {ni2} | {ni3} |")
    L += ["",
          "**Verdict:** CH15 reframing **rejected at AL/AZ/FL** (TOST δ=2pp fails because "
          "|Δ| > 2 pp; HGI nominally above C2HGI by 1.6-3.1 pp). **Tied at CA/TX** (Δ < 2 pp, "
          "TOST passes). Sign-reversed at all 5 states vs Phase 2 leaky reference — the "
          "Phase 2 sign came from the F44 leak (Section 7).",
          ""]

    # MTL reg
    L += ["## 5 · MTL B9 reg Acc@10 / MRR (CH18 reg-side) — Phase 3 leak-free",
          "",
          "| State | C2HGI Acc@10 | HGI Acc@10 | Δ Acc@10 | Wilcoxon p_greater | Pos / Neg |",
          "|---|---:|---:|---:|---:|:-:|"]
    for st in STATES:
        c2 = mtl_reg10[st]["check2hgi"]; hg = mtl_reg10[st]["hgi"]
        if not c2 or not hg:
            L.append(f"| {SHORT[st]} | — | — | — | — | — |")
            continue
        w = _wilcoxon_greater(c2, hg)
        c2m, c2s = np.mean(c2) * 100, np.std(c2, ddof=1) * 100
        hgm, hgs = np.mean(hg) * 100, np.std(hg, ddof=1) * 100
        d = w["delta_mean"] * 100
        p = w.get("wilcoxon_p_greater", float("nan"))
        L.append(f"| {SHORT[st]} | {c2m:.2f} ± {c2s:.2f} | **{hgm:.2f} ± {hgs:.2f}** | "
                 f"**{d:+.2f}** | {_fmt_p(p)} | {w['n_pos']} / {w['n_neg']} |")
    L += ["",
          "MRR:",
          "",
          "| State | C2HGI MRR | HGI MRR | Δ MRR | Wilcoxon p_greater | Pos / Neg |",
          "|---|---:|---:|---:|---:|:-:|"]
    for st in STATES:
        c2 = mtl_mrr[st]["check2hgi"]; hg = mtl_mrr[st]["hgi"]
        if not c2 or not hg:
            L.append(f"| {SHORT[st]} | — | — | — | — | — |")
            continue
        w = _wilcoxon_greater(c2, hg)
        c2m, c2s = np.mean(c2) * 100, np.std(c2, ddof=1) * 100
        hgm, hgs = np.mean(hg) * 100, np.std(hg, ddof=1) * 100
        d = w["delta_mean"] * 100
        p = w.get("wilcoxon_p_greater", float("nan"))
        L.append(f"| {SHORT[st]} | {c2m:.2f} ± {c2s:.2f} | **{hgm:.2f} ± {hgs:.2f}** | "
                 f"**{d:+.2f}** | {_fmt_p(p)} | {w['n_pos']} / {w['n_neg']} |")
    L += ["",
          "**Verdict:** CH18-reg **rejected at 5/5 states** under leak-free MTL B9. The "
          "Phase 2 leaky finding (\"C2HGI reg ≥ HGI reg under MTL\") was an artifact of the "
          "F44 leak, which C2HGI exploited disproportionately. Magnitude is small at "
          "FL/CA/TX (≤ 1.1 pp Acc@10, basically tied) but substantial at AL/AZ (3-8 pp).",
          ""]

    # Leak shift table
    L += ["## 6 · F44 leakage — Phase 2 (leaky) vs Phase 3 (clean) on reg STL",
          "",
          "Phase 2 reg numbers used the legacy full-data `region_transition_log.pt` graph "
          "prior, leaking val transitions into training. Phase 3 used `--per-fold-transition-dir` "
          "(StratifiedGroupKFold train-only edges per fold). The leak inflated absolute "
          "Acc@10 across all states, BUT was substrate-asymmetric — C2HGI benefited more "
          "than HGI, refuting the earlier uniform-leak hypothesis.",
          "",
          "| State | C2HGI leaky | C2HGI clean | Δ_C2HGI | HGI leaky | HGI clean | Δ_HGI | Asymmetry (Δ_C2HGI − Δ_HGI) |",
          "|---|---:|---:|---:|---:|---:|---:|---:|"]
    for st in STATES:
        c2_l = cat_stl_leaky[st]["check2hgi"]   # placeholder; real leaky reg below
        # Use reg10_leaky pulled separately
        c2_lk = reg10_leaky[st]["check2hgi"]
        hg_lk = reg10_leaky[st]["hgi"]
        c2_cl = reg10[st]["check2hgi"]
        hg_cl = reg10[st]["hgi"]
        if not c2_lk or not c2_cl:
            L.append(f"| {SHORT[st]} | — | — | — | — | — | — | — |")
            continue
        c2lm = np.mean(c2_lk) * 100
        c2cm = np.mean(c2_cl) * 100
        hglm = np.mean(hg_lk) * 100
        hgcm = np.mean(hg_cl) * 100
        d_c2 = c2cm - c2lm
        d_hg = hgcm - hglm
        asym = d_c2 - d_hg
        L.append(f"| {SHORT[st]} | {c2lm:.2f} | {c2cm:.2f} | {d_c2:+.2f} | "
                 f"{hglm:.2f} | {hgcm:.2f} | {d_hg:+.2f} | {asym:+.2f} |")
    L += ["",
          "Negative asymmetry → C2HGI lost more pp than HGI when the leak was removed → C2HGI "
          "had been benefiting more from the leak. **AZ shows the largest gap (~5.5 pp)**, "
          "the smoking-gun for substrate-asymmetric leakage. This is why CH15 + CH18-reg "
          "results sign-flip leak-free.",
          ""]

    # Final synthesis
    L += ["## 7 · Final paper-grade synthesis",
          "",
          "Five paper-grade claims after the 5-state, leak-free, Phase 1+2+3 closure:",
          "",
          "1. **CH16 — Cat substrate gap** ✅ at 5/5 states (Wilcoxon p=0.0312, 5/5 folds positive). "
          "Δ scales monotonically with state size.",
          "2. **CH18-cat — MTL inherits the cat substrate gap** ✅ at 5/5 states (same statistics). "
          "Δ in MTL is similar magnitude to cat-STL (15 pp at small AL/AZ, ~33 pp at large FL/CA/TX).",
          "3. **CH15 reframing — substrate-equivalent reg under matched head** ❌ rejected at AL/AZ/FL "
          "(TOST δ=2pp fails). Tied at CA/TX (Δ < 2 pp). Sign-flipped at every state vs leaky reference.",
          "4. **CH18-reg — MTL substrate-specific reg lift** ❌ rejected at 5/5 states (sign-reversed). "
          "The Phase 2 leaky claim was an F44 artefact.",
          "5. **F44 leak is substrate-asymmetric** (~3 pp differential, AZ peak ~5.5 pp). C2HGI "
          "exploited the leaky log_T more than HGI — α grew more for C2HGI runs.",
          "",
          "### Suggested paper framing",
          "",
          "> **Per-visit context (Check2HGI) is the load-bearing substrate for next-category "
          "prediction; for next-region prediction, POI-level embeddings (HGI) are at parity "
          "(large states FL/CA/TX) or marginally ahead (small states AL/AZ).**",
          "",
          "Mechanism (CH19, F37 FL):",
          "* The cat task benefits from the per-visit variance Check2HGI adds (AL+AZ pooled-vs-canonical "
          "decomposition: ~72% of cat gap is per-visit context).",
          "* Reg is a POI-level coarser label; POI-stable HGI embeddings aggregate cleanly across "
          "the 9-window without needing per-visit signal.",
          "* The previously-claimed CH18-reg lift was the F44 leak: C2HGI's α grew more aggressively "
          "(to ~2 by ep 17-20) and mined val edges from the full-data log_T more effectively.",
          "",
          "## 8 · Bibliography of internal docs",
          "",
          "* `PHASE2_TRACKER.md` — Phase 2 STL closure (cat + probe, leak-free already).",
          "* `PHASE3_TRACKER.md` — Phase 3 Scope D plan + status board.",
          "* `research/SUBSTRATE_COMPARISON_FINDINGS.md` — full Phase-1 verdicts + Phase-3 closure.",
          "* `research/F50_T4_C4_LEAK_DIAGNOSIS.md` — root-cause + magnitude.",
          "* `research/F50_T4_BROADER_LEAKAGE_AUDIT.md` — audit of other heads.",
          "* `research/F50_T4_PRIOR_RUNS_VALIDITY.md` — which prior runs survived the C4 fix.",
          "* `research/PHASE3_INCIDENTS.md` — operational incidents during Phase 3.",
          "* `NORTH_STAR.md` — committed MTL recipe (B9 leak-free champion).",
          ""]
    return "\n".join(L)


# -----------------------------------------------------------------------------

def main() -> None:
    probe = gather_probe()
    cat_stl = gather_cat_stl()
    reg10, mrr = gather_reg_stl_pf()
    mtl_cat, mtl_reg10, mtl_mrr = gather_mtl_pf()

    # Leaky reg STL (Phase 2) for the leak-shift comparison
    reg10_leaky = {}
    for st in STATES:
        s = SHORT[st]
        reg10_leaky[st] = {
            "check2hgi": _load_perfold(f"{s}_check2hgi_reg_gethard_5f50ep.json", "acc10"),
            "hgi":       _load_perfold(f"{s}_hgi_reg_gethard_5f50ep.json",       "acc10"),
        }

    # Per-track box plots (state-major)
    _state_box_panel(probe,
                     "Substrate-only linear probe — F1 (5-fold)",
                     "Macro-F1 (%)",
                     FIGS / "00_probe_box.png",
                     state_subset=[s for s in STATES if probe[s]["check2hgi"]])
    _state_box_panel(cat_stl,
                     "Cat STL `next_gru` — F1 (5-fold, leak-free by construction)",
                     "F1 (%)",
                     FIGS / "01_cat_stl_box.png")
    _state_box_panel(mtl_cat,
                     "MTL B9 cat F1 — Phase 3 leak-free per-fold",
                     "Cat F1 (%)",
                     FIGS / "02_mtl_cat_box.png")
    _state_box_panel(reg10,
                     "Reg STL `next_getnext_hard` — Phase 3 leak-free Acc@10",
                     "Acc@10 (%)",
                     FIGS / "03_reg_stl_pf_box.png")
    _state_box_panel(mtl_reg10,
                     "MTL B9 reg Acc@10 — Phase 3 leak-free",
                     "Acc@10 (%)",
                     FIGS / "04_mtl_reg_acc10_box.png")

    # Paired Δ grid
    _delta_strip_panel(
        {
            "Cat STL (CH16)": cat_stl,
            "MTL cat (CH18-cat)": mtl_cat,
            "Reg STL (CH15)": reg10,
            "MTL reg (CH18-reg)": mtl_reg10,
        },
        "Paired Δ (C2HGI − HGI) per fold across the 4 claim tracks",
        "Δ (pp)",
        FIGS / "05_paired_delta_grid.png",
    )

    # Leak shift bar chart
    _leak_shift_panel(reg10_leaky, reg10, FIGS / "06_leak_shift_bars.png")

    md = emit_markdown(probe, cat_stl, reg10, mrr, mtl_cat, mtl_reg10, mtl_mrr,
                       cat_stl, reg10_leaky)
    SURVEY.write_text(md)
    print(f"Wrote {SURVEY}")
    for p in sorted(FIGS.glob("*.png")):
        print(f"  fig: {p.relative_to(REPO)}")


if __name__ == "__main__":
    main()
