"""Paired one-sided Wilcoxon signed-rank on the 20 matched fold differences, computed on
the v18 / joint-best (served-checkpoint) arrays the paper reports, alongside the paired
one-sided t-test on the 4 per-seed means that is the statistic actually printed in the
paper's text.

WHY THIS SCRIPT EXISTS
-----------------------
The registered analysis plan (`analysis_protocol/STATISTICAL_PROTOCOL.md` §2, §5.2 of this
release) names a paired one-sided Wilcoxon signed-rank on the matched per-fold deltas,
n = 20 = 4 seeds x 5 folds, as the primary superiority test for next-category. At four
seed-pairs the exact one-sided Wilcoxon p cannot fall below 0.0625, which is why the paper
reports the t-statistic on per-seed means instead (see
`analysis_protocol/DEVIATION_LOG.md`, D-1/D-2) while still computing the Wilcoxon
alongside it, at its registered footing, for agreement.

WHAT CARRIES WHAT STANDING
---------------------------
- CATEGORY, all six datasets: superiority, joint > dedicated. Pre-registered (protocol §2
  for the test, §5.2 for the Holm family within the six-dataset category-superiority set).
- REGION: the protocol pins next-region to non-inferiority only (TOST at a 2-pp margin,
  protocol §3.2 -- not this script). No region-superiority family is pre-registered; the
  region Wilcoxon/t computed here are a sensitivity reading, and any region "outperforms"
  claim in the paper carries its own post-hoc Holm family, not the one applied below.

FOOTING
-------
Paired per (seed, fold) on the same partition: for a given seed both arms read the same
StratifiedGroupKFold split, so fold k of seed s is matched across arms. Pairing across
seeds is not valid (each seed draws its own partition) -- the Wilcoxon here operates on
the pooled set of 20 matched differences (the registered footing), while the t-test
operates on the 4 per-seed means (the reported footing); both are printed side by side.

Known limitation: the five folds inside one seed share the majority of their training
data, so the 20 differences are not 20 independent replicates. The registered Wilcoxon
uses this footing anyway (as pre-registered); the seed-level t (n = 4, more conservative)
is the statistic the paper's text reports.

INPUTS (both committed to this release)
-----------------------------------------
  joint:      docs/results/closing_data/v18/joint_best_perfold.json
              cells['<state>_s<seed>_joint'].folds['1'..'5'].joint_best
              cat = cat_f1 (fraction), reg = top10_full (fraction)
  dedicated:  docs/studies/closing_data/v18/data/v18_results.json
              per_run[] matched on (state, seed) -> stl_cat_folds, stl_reg_folds (percent)

The raw per-run artifacts (rundirs/logs) the two files above were aggregated from are not
part of this release -- only the two finished aggregates. See the top-level README.

The script refuses to report any test until it has reproduced the paper's own per-cell
means from these arrays to within a small tolerance -- a parse that silently returns the
wrong mean would otherwise be indistinguishable from a real result.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

from scipy import stats

REPO = Path(__file__).resolve().parents[3]
JOINT = REPO / "docs/results/closing_data/v18/joint_best_perfold.json"
DED = REPO / "docs/studies/closing_data/v18/data/v18_results.json"

SEEDS = [0, 1, 7, 100]
STATES = ["istanbul", "alabama", "arizona", "florida", "texas", "california"]

# Delivered cell means, recomputed from the same arrays (mean of 5 folds inside a seed,
# then mean of the 4 seeds). Used as the instrument check, not as an input.
EXPECTED = {
    "istanbul": (35.4228, 75.0804),
    "alabama": (30.5868, 69.2430),
    "arizona": (34.5702, 59.0440),
    "florida": (37.5484, 76.5376),
    "texas": (36.1941, 66.1503),
    "california": (35.6287, 64.5362),
}
TOL = 0.005


def load():
    joint = json.loads(JOINT.read_text())["cells"]
    ded_runs = json.loads(DED.read_text())["per_run"]
    ded = {(r["state"], r["seed"]): r for r in ded_runs}
    return joint, ded


def series(joint, ded, state):
    """Return (cat_pairs, reg_pairs) as lists of (joint, dedicated) in percent,
    ordered seed-major then fold, 20 entries each."""
    cat, reg = [], []
    for seed in SEEDS:
        cell = joint[f"{state}_s{seed}_joint"]["folds"]
        run = ded[(state, seed)]
        for k in range(1, 6):
            jb = cell[str(k)]["joint_best"]
            cat.append((jb["cat_f1"] * 100.0, run["stl_cat_folds"][k - 1]))
            reg.append((jb["top10_full"] * 100.0, run["stl_reg_folds"][k - 1]))
    return cat, reg


def seed_means(pairs):
    """Mean of each arm within each seed -> 4 pairs."""
    out = []
    for i in range(0, 20, 5):
        blk = pairs[i : i + 5]
        out.append((sum(a for a, _ in blk) / 5.0, sum(b for _, b in blk) / 5.0))
    return out


def holm(pvals):
    """Holm-Bonferroni step-down. Returns adjusted p in the input order."""
    order = sorted(range(len(pvals)), key=lambda i: pvals[i])
    m = len(pvals)
    adj = [0.0] * m
    running = 0.0
    for rank, i in enumerate(order):
        running = max(running, (m - rank) * pvals[i])
        adj[i] = min(1.0, running)
    return adj


def check_instrument(joint, ded):
    print("INSTRUMENT CHECK -- reproduce the delivered cell means before testing")
    ok = True
    for st in STATES:
        cat, reg = series(joint, ded, st)
        cm = sum(a for a, _ in seed_means(cat)) / 4.0
        rm = sum(a for a, _ in seed_means(reg)) / 4.0
        ec, er = EXPECTED[st]
        good = abs(cm - ec) < TOL and abs(rm - er) < TOL
        ok &= good
        print(f"  {st:<11} cat {cm:8.4f} (expected {ec:8.4f})   "
              f"reg {rm:8.4f} (expected {er:8.4f})   {'ok' if good else 'FAIL'}")
    if not ok:
        sys.exit("instrument check failed -- not reporting any test")
    print()


def run_axis(joint, ded, axis, idx, family_note):
    print(f"{'=' * 78}\n{axis}\n{family_note}\n{'=' * 78}")
    rows, praw = [], []
    for st in STATES:
        pairs = series(joint, ded, st)[idx]
        d20 = [a - b for a, b in pairs]
        pos = sum(1 for x in d20 if x > 0)
        # one-sided: joint greater than dedicated
        w = stats.wilcoxon(d20, alternative="greater", method="exact")
        sm = seed_means(pairs)
        d4 = [a - b for a, b in sm]
        t = stats.ttest_rel([a for a, _ in sm], [b for _, b in sm], alternative="greater")
        rows.append((st, sum(d20) / 20.0, pos, w.pvalue, sum(d4) / 4.0, t.pvalue))
        praw.append(w.pvalue)
    adj = holm(praw)
    print(f"  {'dataset':<12}{'delta20':>9}{'folds+':>8}{'W exato p':>12}"
          f"{'Holm':>10}   |{'delta4':>9}{'t p':>11}")
    for (st, d20m, pos, pw, d4m, pt), pa in zip(rows, adj):
        print(f"  {st:<12}{d20m:>9.4f}{pos:>5}/20{pw:>12.2e}{pa:>10.4f}   |"
              f"{d4m:>9.4f}{pt:>11.2e}")
    print()
    return rows, adj


def main():
    joint, ded = load()
    check_instrument(joint, ded)
    run_axis(joint, ded, "NEXT CATEGORY -- superiority (joint > dedicated), macro-F1",
             0, "PRE-REGISTERED test, protocol §2. Holm within the six-state family (m=6).")
    run_axis(joint, ded, "NEXT REGION -- superiority (joint > dedicated), Acc@10",
             1, "NOT pre-registered as superiority. Protocol pins region to TOST "
                "non-inferiority.\nReported here as a sensitivity reading; any region "
                "'outperforms' claim in the paper carries\nits own post-hoc Holm family, "
                "not the one applied here.")
    print("delta20 = mean of the 20 matched fold differences; delta4 = mean of the 4 "
          "per-seed differences.\n't p' is the one-sided paired t on the four per-seed "
          "means (df=3) -- the statistic the\npaper's text reports. Holm here is applied "
          "to the Wilcoxon p only, within its own family.")


if __name__ == "__main__":
    main()
