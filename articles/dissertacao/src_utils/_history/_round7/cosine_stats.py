#!/usr/bin/env python3
"""cosine_stats.py -- derive every number in Appendix F from the observations.

AGENT_GUARDRAILS §2 N2 ("agents quote; they do not compute"): this script is the committed
derivation, and the appendix quotes its output. Nothing in
src/chapters/apx_f_cosine.tex or src/tables/frame/cosine.tex is computed by hand or copied
from a summary file.

INPUT   src_utils/_history/_round7/gradient_cosine_observations.parquet
        3,900 rows; columns state, fold, epoch, cos, config.

NOT EVERY SERIES CARRIES FIFTY VALUES, and the appendix now says so. Two of Florida's twelve
configurations (T6_4_two_pass, T6_4_infonce_tau0_5) hold 65 rows per fold rather than 50: their
epochs 1 to 15 each appear twice, with different cosines, which is a partial re-run harvested on
top of the original series. 10 of the 75 series are affected, 150 of the 3,900 rows. It does not
touch the appendix's claim (equivalence holds either way, and both configurations stay equivalent
to zero), but it does move those two configuration means, so the reported Florida span is computed
over the rows as they stand. Measured with:
    df.groupby(['state','config','fold']).size().value_counts()   ->  50: 65 series, 65: 10 series

THE UNIT OF INDEPENDENCE, which is the whole methodological point.
The 50 per-epoch cosines inside one fold are consecutive states of ONE training trajectory, so
they are not independent draws. Treating them as 250 or 3,150 independent observations makes
every p-value anti-conservative. This script therefore aggregates first:
    Alabama, Arizona   -> fold means           (n=5)
    Florida            -> configuration means  (n=12; its 12 configurations reuse the 5 folds)
and computes every test on the aggregate. Observation-level tests are printed too, labelled as
anti-conservative, only to show that the equivalence conclusion does not depend on the choice.

THE SIGN-TEST FLOOR is printed for each dataset because at n=5 the exact two-sided sign test
cannot return below 0.0625 even when all five values agree in direction. Any "significant"
claim at n=5 therefore rests entirely on the t-test's normality assumption, and the appendix
words it as a tendency rather than an effect. Printing the floor beside the p-value is what
makes that visible instead of inferable.

STRUCTURAL ASSERTIONS run before any statistic, and they exist because an earlier combine of
this data carried a fourth "dataset" that was really the directory name of Florida's shipped
configuration arm. A fabricated dataset in a dissertation appendix is the failure this guards:
    exactly 4 states, named alabama/arizona/florida/georgia
    3,900 rows = 3,150 + 250 + 250 + 250
    no nulls in cos

Usage:  python3 src_utils/_history/_round7/cosine_stats.py
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

HERE = Path(__file__).resolve().parent
PARQUET = HERE / "gradient_cosine_observations.parquet"
MARGIN = 0.05
FLORIDA_UNIT = "config"          # Florida aggregates to configuration means
EXPECTED = {"alabama": 250, "arizona": 250, "florida": 3150, "georgia": 250}
# [round7, 2026-07-29] GEORGIA ADDED. This dict and the three assertions below still named THREE
# states after georgia landed (commit ff69ba07), so the script asserted its way to a crash on the
# parquet it ships with, and the appendix pointed at a derivation that could not run:
#   AssertionError: expected ['alabama','arizona','florida'], got ['alabama','arizona','florida','georgia']
# The row total moves 3,650 -> 3,900 for the same reason. That is AGENT_GUARDRAILS 4b V6: the count
# was corrected in the parquet and in the appendix, and this file kept the superseded value.


def tost_p(v: np.ndarray, margin: float = MARGIN) -> float:
    """Two one-sided tests against +/- margin. Returns the larger (governing) p-value."""
    v = np.asarray(v, dtype=float)
    n = v.size
    mean = v.mean()
    se = v.std(ddof=1) / np.sqrt(n)
    dof = n - 1
    p_lower = stats.t.sf((mean + margin) / se, dof)   # H0: mu <= -margin
    p_upper = stats.t.cdf((mean - margin) / se, dof)  # H0: mu >= +margin
    return float(max(p_lower, p_upper))


def ci95(v: np.ndarray) -> tuple[float, float]:
    v = np.asarray(v, dtype=float)
    n = v.size
    mean = v.mean()
    se = v.std(ddof=1) / np.sqrt(n)
    tc = stats.t.ppf(0.975, n - 1)
    return float(mean - tc * se), float(mean + tc * se)


def sign_test(v: np.ndarray) -> tuple[float, float, int, int]:
    """Exact two-sided sign test, plus the FLOOR: the smallest p reachable at this n."""
    v = np.asarray(v, dtype=float)
    npos = int((v > 0).sum())
    nneg = int((v < 0).sum())
    k = npos + nneg
    p = float(stats.binomtest(npos, k, 0.5, alternative="two-sided").pvalue)
    floor = float(stats.binomtest(k, k, 0.5, alternative="two-sided").pvalue)
    return p, floor, npos, k


def series_groups(g: pd.DataFrame, state: str):
    """One group per training trajectory (fold within configuration)."""
    return g.groupby([FLORIDA_UNIT, "fold"]) if state == "florida" else g.groupby("fold")


def independent_unit(g: pd.DataFrame, state: str) -> tuple[np.ndarray, str]:
    if state == "florida":
        return g.groupby(FLORIDA_UNIT)["cos"].mean().to_numpy(), "configuration mean"
    return g.groupby("fold")["cos"].mean().to_numpy(), "fold mean"


def main() -> int:
    obs = pd.read_parquet(PARQUET)

    # ---- structural assertions BEFORE any statistic ----
    states = sorted(obs["state"].unique())
    counts = obs.groupby("state").size().to_dict()
    assert states == sorted(EXPECTED), f"expected {sorted(EXPECTED)}, got {states}"
    assert counts == EXPECTED, f"row counts {counts} != {EXPECTED}"
    assert len(obs) == sum(EXPECTED.values()) == 3900, len(obs)
    assert int(obs["cos"].isna().sum()) == 0, "null cosines present"
    print(f"STRUCTURE OK  states={states}  rows={len(obs)}  per-state={counts}")
    print(f"folds={sorted(obs['fold'].unique())}  epochs={obs['epoch'].nunique()}"
          f"  florida configurations={obs[obs.state=='florida'][FLORIDA_UNIT].nunique()}")

    c = obs["cos"].to_numpy()
    print(f"\nPOOLED DESCRIPTIVE (data, not a test): n={c.size}  mean={c.mean():+.6f}"
          f"  within |{MARGIN:g}|={100*(np.abs(c)<MARGIN).mean():.2f}%"
          f"  range=[{c.min():+.4f}, {c.max():+.4f}]")

    print("\n=== TESTS ON THE INDEPENDENT UNIT (these are the appendix's numbers) ===")
    hdr = (f"{'dataset':9s} {'unit':20s} {'n':>3s} {'obs':>5s} {'mean':>10s} "
           f"{'ci95_lo':>10s} {'ci95_hi':>10s} {'TOST p':>10s} {'t p':>8s} "
           f"{'sign p':>8s} {'floor':>8s} {'pos':>6s}")
    print(hdr)
    for state, g in obs.groupby("state", sort=True):
        u, uname = independent_unit(g, state)
        lo, hi = ci95(u)
        sp, floor, npos, k = sign_test(u)
        print(f"{state:9s} {uname:20s} {u.size:3d} {len(g):5d} {u.mean():+10.5f} "
              f"{lo:+10.5f} {hi:+10.5f} {tost_p(u):10.2e} "
              f"{stats.ttest_1samp(u, 0.0).pvalue:8.4f} {sp:8.4f} {floor:8.4f} "
              f"{f'{npos}/{k}':>6s}")

    print("\n=== EQUIVALENCE AT EVERY LEVEL (robustness of the appendix's one claim) ===")
    for state, g in obs.groupby("state", sort=True):
        levels: dict[str, np.ndarray] = {"observation (anti-conservative)": g["cos"].to_numpy()}
        levels["fold series mean"] = (
            g.groupby([FLORIDA_UNIT, "fold"])["cos"].mean().to_numpy() if state == "florida"
            else g.groupby("fold")["cos"].mean().to_numpy())
        if state == "florida":
            levels["configuration mean"] = g.groupby(FLORIDA_UNIT)["cos"].mean().to_numpy()
        parts = [f"{name} n={v.size} p={tost_p(v):.2e} "
                 f"{'EQUIV' if tost_p(v) < 0.05 else 'NOT-EQUIV'}"
                 for name, v in levels.items()]
        print(f"  {state:9s} " + " | ".join(parts))

    print("\n=== PER-FOLD SLOPE OVER TRAINING (one slope per trajectory, tested against 0) ===")
    for state, g in obs.groupby("state", sort=True):
        slopes = np.array([np.polyfit(gg["epoch"], gg["cos"], 1)[0]
                           for _, gg in series_groups(g, state) if len(gg) > 2])
        t, p = stats.ttest_1samp(slopes, 0.0)
        print(f"  {state:9s} n_series={slopes.size:3d} mean_slope={slopes.mean():+.6f} "
              f"t={t:+.3f} p={p:.4f} negative={int((slopes < 0).sum())}/{slopes.size}")

    print("\n=== FLORIDA, PER CONFIGURATION (the hyperparameter axis) ===")
    fl = obs[obs.state == "florida"]
    per = fl.groupby(FLORIDA_UNIT)["cos"].mean()
    equiv = 0
    for cfg, gg in fl.groupby(FLORIDA_UNIT):
        fm = gg.groupby("fold")["cos"].mean().to_numpy()
        ok = tost_p(fm) < 0.05
        equiv += ok
        print(f"  {cfg:34s} folds={fm.size} mean={fm.mean():+.5f} TOST p={tost_p(fm):.2e} "
              f"{'EQUIV' if ok else 'NOT-EQUIV'}")
    print(f"  configurations equivalent at the fold unit: {equiv} of {per.size}")
    print(f"  configuration-mean span: [{per.min():+.5f}, {per.max():+.5f}]")

    print("\n=== ALABAMA, EPOCH BLOCKS (the decline reported in the appendix) ===")
    al = obs[obs.state == "alabama"]
    for lo_e, hi_e in [(1, 5), (6, 10), (11, 20), (21, 30), (31, 40), (41, 50)]:
        s = al[(al.epoch >= lo_e) & (al.epoch <= hi_e)]["cos"]
        print(f"  epochs {lo_e:2d}-{hi_e:2d}: n={len(s):3d} mean={s.mean():+.5f} "
              f"median={s.median():+.5f}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
