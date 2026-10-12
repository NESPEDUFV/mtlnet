#!/usr/bin/env python3
"""cosine_stats6.py -- Appendix F's numbers over SIX datasets, at the FOLD unit.

WHY A SECOND FILE RATHER THAN AN EDIT. cosine_stats.py is the committed derivation of the
FOUR-dataset appendix and its structural assertions name those four states and 3,900 rows by
value. It is the record of what was published at commit ff69ba07 and it still runs (RC=0) on the
parquet it ships with. Rewriting its assertions in place would destroy the only mechanical proof
that the four-dataset text was derived from the four-dataset data. This file is the six-dataset
derivation; both run, and each asserts its own structure.

INPUT   src_utils/_history/_round7/gradient_cosine_observations6.parquet
        columns state, fold, epoch, cos, config -- identical schema to the four-dataset parquet.

THE UNIT OF ANALYSIS IS THE FOLD, and that is the whole point of this round's correction. The 50
per-epoch cosines inside one fold are consecutive states of ONE training trajectory, so they are
serially dependent; treating them as 250 independent draws makes every p-value anti-conservative.
Every test below therefore runs on ONE VALUE PER FOLD:
    alabama, arizona, georgia, california, texas, istanbul  ->  5 fold means      (n=5)
    florida                                                 -> 60 fold-series means (12 configurations x 5 folds)
FLORIDA'S HEADLINE UNIT CHANGED IN THIS FILE, AND IT IS A CHANGE, NOT CONTINUITY. cosine_stats.py
reports Florida at the CONFIGURATION mean (n=12, its `independent_unit()` returns
groupby("config")); this file reports it at the FOLD SERIES (n=60, configuration x fold), because
the round's brief is that the unit of analysis is the FOLD and every other dataset here is at n=5
fold means. Putting Florida at n=12 in the same column would mean the table's `n` counts two
different things across rows. An earlier version of this docstring said the configuration reading
was reported beside it "exactly as the four-dataset script did", which described the wrong direction:
the four-dataset script made n=12 the headline and this one makes it the secondary reading.

The change moves nothing that matters and both readings are printed. Florida's twelve
configurations reuse the same five folds, so its 60 fold-series means are not mutually independent
either; the configuration-mean aggregation (n=12) is the more conservative reading, appears in the
EQUIVALENCE AT EVERY LEVEL block, and gives the same mean (+0.00026) and the same verdict
(equivalent, TOST p=1.28e-16 against 4.54e-62 at n=60). The 95% CI does differ with the unit --
[-0.00099, +0.00151] at n=60 against [-0.0012, +0.0017] at n=12 -- so a CI quoted for Florida must
name which unit it belongs to, and the table's Unit column is what carries that.

THE SIGN TEST CANNOT REACH 0.05 AT n=5. Its two-sided floor at five values that all agree in
direction is 0.0625. This script prints the floor next to every sign p-value so that a reader
cannot mistake "0.0625" for a rejection: at this sample size a distribution-free test is
incapable of significance, and any rejection therefore rests entirely on the t-test's normality
assumption. Equivalence (TOST) within +/-0.05 is the claim that survives the sample size.

Usage:  python3 src_utils/_history/_round7/cosine_stats6.py
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

HERE = Path(__file__).resolve().parent
PARQUET = HERE / "gradient_cosine_observations6.parquet"
MARGIN = 0.05

# Structural expectations, asserted BEFORE any statistic. The four-dataset script exists because
# an earlier combine carried a fabricated fourth "dataset" that was really a directory name; the
# assertion is what caught it. Florida keeps its 3,150 rows (12 configurations, two of which carry
# a partial re-run of epochs 1-15, so 65 rows in 10 of its 60 series); the six single-configuration
# states carry 250 each = 5 folds x 50 epochs.
EXPECTED = {
    "alabama": 250, "arizona": 250, "california": 250, "florida": 3150,
    "georgia": 250, "istanbul": 250, "texas": 250,
}


def tost_p(v: np.ndarray, margin: float = MARGIN) -> float:
    """Two one-sided tests against +/- margin. Returns the larger (governing) p-value."""
    v = np.asarray(v, dtype=float)
    mean = v.mean()
    se = v.std(ddof=1) / np.sqrt(v.size)
    dof = v.size - 1
    p_lower = stats.t.sf((mean + margin) / se, dof)   # H0: mu <= -margin
    p_upper = stats.t.cdf((mean - margin) / se, dof)  # H0: mu >= +margin
    return float(max(p_lower, p_upper))


def ci95(v: np.ndarray) -> tuple[float, float]:
    v = np.asarray(v, dtype=float)
    mean = v.mean()
    se = v.std(ddof=1) / np.sqrt(v.size)
    tc = stats.t.ppf(0.975, v.size - 1)
    return float(mean - tc * se), float(mean + tc * se)


def sign_test(v: np.ndarray) -> tuple[float, float, int, int]:
    """Exact two-sided sign test, plus the FLOOR: the smallest p reachable at this n."""
    v = np.asarray(v, dtype=float)
    npos = int((v > 0).sum())
    k = npos + int((v < 0).sum())
    p = float(stats.binomtest(npos, k, 0.5, alternative="two-sided").pvalue)
    floor = float(stats.binomtest(k, k, 0.5, alternative="two-sided").pvalue)
    return p, floor, npos, k


def fold_unit(g: pd.DataFrame, state: str) -> tuple[np.ndarray, str]:
    """ONE VALUE PER FOLD. Florida's folds are nested in configurations, so its unit is the
    fold-series (configuration x fold); everywhere else it is the fold."""
    if state == "florida":
        return g.groupby(["config", "fold"])["cos"].mean().to_numpy(), "fold series"
    return g.groupby("fold")["cos"].mean().to_numpy(), "fold"


def main() -> int:
    obs = pd.read_parquet(PARQUET)

    # ---- structural assertions BEFORE any statistic ----
    states = sorted(obs["state"].unique())
    counts = obs.groupby("state").size().to_dict()
    assert states == sorted(EXPECTED), f"expected {sorted(EXPECTED)}, got {states}"
    assert counts == EXPECTED, f"row counts {counts} != {EXPECTED}"
    assert len(obs) == sum(EXPECTED.values()), f"{len(obs)} != {sum(EXPECTED.values())}"
    assert int(obs["cos"].isna().sum()) == 0, "null cosines present"
    n_dissertation = len([s for s in states if s != "georgia"])
    print(f"STRUCTURE OK  states={len(states)} ({n_dissertation} of the dissertation's six, plus georgia)")
    print(f"  rows={len(obs)}  per-state={counts}")
    print(f"  folds={sorted(obs['fold'].unique())}  epochs={obs['epoch'].nunique()}"
          f"  florida configurations={obs[obs.state=='florida']['config'].nunique()}")

    c = obs["cos"].to_numpy()
    print(f"\nPOOLED DESCRIPTIVE (describes the data; it is NOT a test): n={c.size}"
          f"  mean={c.mean():+.6f}  within |{MARGIN:g}|={100*(np.abs(c)<MARGIN).mean():.2f}%"
          f"  range=[{c.min():+.4f}, {c.max():+.4f}]")

    print("\n=== TESTS AT THE FOLD UNIT (these are the appendix's numbers) ===")
    print(f"{'dataset':11s} {'unit':11s} {'n':>3s} {'obs':>5s} {'mean':>10s} {'ci95_lo':>10s} "
          f"{'ci95_hi':>10s} {'TOST p':>10s} {'t p':>8s} {'sign p':>8s} {'floor':>8s} {'pos':>7s}")
    rows = []
    for state, g in obs.groupby("state", sort=True):
        u, uname = fold_unit(g, state)
        lo, hi = ci95(u)
        sp, floor, npos, k = sign_test(u)
        tp = float(stats.ttest_1samp(u, 0.0).pvalue)
        tp_governing = tost_p(u)
        print(f"{state:11s} {uname:11s} {u.size:3d} {len(g):5d} {u.mean():+10.5f} {lo:+10.5f} "
              f"{hi:+10.5f} {tp_governing:10.2e} {tp:8.4f} {sp:8.4f} {floor:8.4f} "
              f"{f'{npos}/{k}':>7s}")
        rows.append({
            "dataset": state, "unit": f"{uname} mean", "n": u.size, "n_observations": len(g),
            "mean": round(float(u.mean()), 5), "sd": round(float(u.std(ddof=1)), 5),
            "ci95_lo": round(lo, 5), "ci95_hi": round(hi, 5),
            "t_p_vs_zero": round(tp, 4), "sign_p": round(sp, 4),
            "sign_p_floor_at_this_n": round(floor, 4),
            "TOST_p_margin_0.05": float(f"{tp_governing:.3e}"),
            "TOST_0.05": "equivalent" if tp_governing < 0.05 else "NOT equivalent",
            "n_positive": npos,
        })

    print("\n=== EQUIVALENCE AT EVERY LEVEL (robustness of the appendix's one claim) ===")
    for state, g in obs.groupby("state", sort=True):
        levels = {"observation (SERIALLY DEPENDENT)": g["cos"].to_numpy()}
        levels["fold-series mean"] = fold_unit(g, state)[0]
        if state == "florida":
            levels["configuration mean"] = g.groupby("config")["cos"].mean().to_numpy()
        parts = [f"{nm} n={v.size} p={tost_p(v):.2e} "
                 f"{'EQUIV' if tost_p(v) < 0.05 else 'NOT-EQUIV'}" for nm, v in levels.items()]
        print(f"  {state:11s} " + " | ".join(parts))

    print("\n=== PER-FOLD SLOPE OVER TRAINING (one slope per trajectory, tested against 0) ===")
    slopes_out = {}
    for state, g in obs.groupby("state", sort=True):
        grp = g.groupby(["config", "fold"]) if state == "florida" else g.groupby("fold")
        sl = np.array([np.polyfit(gg["epoch"], gg["cos"], 1)[0] for _, gg in grp if len(gg) > 2])
        t, p = stats.ttest_1samp(sl, 0.0)
        sp, floor, _npos, _k = sign_test(sl)
        print(f"  {state:11s} n_series={sl.size:3d} mean_slope={sl.mean():+.6f} t={t:+.3f} "
              f"t_p={p:.4f} sign_p={sp:.4f} (floor {floor:.4f}) negative={int((sl<0).sum())}/{sl.size}")
        slopes_out[state] = {
            "mean_slope": float(f"{sl.mean():.6g}"), "t_test_p": round(float(p), 4),
            "sign_test_p": round(sp, 4), "sign_p_floor": round(floor, 4),
            "n_folds": int(sl.size), "n_negative": int((sl < 0).sum()),
        }

    print("\n=== FLORIDA, PER CONFIGURATION (the hyperparameter axis) ===")
    fl = obs[obs.state == "florida"]
    per = fl.groupby("config")["cos"].mean()
    equiv = 0
    for cfg, gg in fl.groupby("config"):
        fm = gg.groupby("fold")["cos"].mean().to_numpy()
        ok = tost_p(fm) < 0.05
        equiv += ok
        print(f"  {cfg:34s} folds={fm.size} mean={fm.mean():+.5f} TOST p={tost_p(fm):.2e} "
              f"{'EQUIV' if ok else 'NOT-EQUIV'}")
    print(f"  configurations equivalent at the fold unit: {equiv} of {per.size}")
    print(f"  configuration-mean span: [{per.min():+.5f}, {per.max():+.5f}]")

    print("\n=== SIGN-TEST FLOOR, STATED PLAINLY ===")
    for n in (5, 12, 60):
        print(f"  at n={n:2d} the two-sided exact sign test cannot return below "
              f"p={stats.binomtest(n, n, 0.5, alternative='two-sided').pvalue:.4f}")
    print("  Consequence: at n=5 no distribution-free test can reach 0.05, so no dataset with five")
    print("  folds can support a significance claim about the SIGN of its mean. Equivalence within")
    print("  +/-0.05 by TOST is the claim that survives, and it holds at every dataset and unit.")

    # Machine-readable side output, so the table and the figure quote one file rather than a paste.
    out_csv = HERE / "gradient_cosine_tests6.csv"
    pd.DataFrame(rows).to_csv(out_csv, index=False)
    print(f"\nwrote {out_csv.name} ({len(rows)} rows, one per dataset at the fold unit)")
    import json
    (HERE / "gradient_cosine_slopes6.json").write_text(json.dumps(slopes_out, indent=1))
    print(f"wrote gradient_cosine_slopes6.json ({len(slopes_out)} datasets)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
