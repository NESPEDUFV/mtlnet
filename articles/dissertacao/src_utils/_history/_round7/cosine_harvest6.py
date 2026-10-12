#!/usr/bin/env python3
"""cosine_harvest6.py -- build the six-dataset parquet, with the fold-distinctness gate FIRST.

WHY THIS GATE EXISTS, measured on this project. Earlier this round two per-fold jobs on the GPU
host both resolved their output directory by RECENCY (`find ... -newer sentinel | head -1`), which
races under concurrent jobs, and `--only-fold k` names its output `fold1_diagnostics.csv` for every
k -- so the filename carries no fold identity. Two jobs harvested the SAME run directory and
produced BYTE-IDENTICAL files claiming to be different folds (md5 2afa6aebfb2a2c2145a104c3a54f50f6
for both california_f2 and california_f3). Those files are still on the host and this script would
accept them without the checks below. The data was discarded rather than reported.

THE GATE, and every leg is a hard assertion rather than a warning:
  (1) every per-fold CSV's md5 is distinct -- two identical files across folds is a harvest fault,
      not a result, no matter how well-formed they are;
  (2) each file's own fold column equals the fold it is filed under -- a filename is a claim, the
      column is evidence. (The runner writes fold identity into the PATH, not into a column, so the
      check is: the file came from <rundir>/diagnostics/fold<k>_diagnostics.csv of a run directory
      resolved by the training process's own pid, and its epoch column is a complete 1..50 series.)
  (3) the cosine column carries numbers -- exit status, row count and header shape are ALL satisfied
      by an all-NaN column, which is exactly what three earlier runs produced (the diagnostic is
      opt-in and defaults off).
A fold failing any leg is DISCARDED and named in the output, never silently dropped.

Usage:  python3 src_utils/_history/_round7/cosine_harvest6.py <newdata_dir> [out.parquet]
        where <newdata_dir> holds <state>_fold<k>_diagnostics.csv files harvested from the host.

THE SECOND ARGUMENT IS NOT A CONVENIENCE. Validating this gate needs a synthetic clean case (three
states, five distinct folds each) to prove the gate PASSES data it should pass -- and the first run
of that validation wrote a 4,650-row parquet to the production path, of which the 750 NEW rows were
`numpy.random.default_rng(0)` output (the other 3,900 were the real four-dataset parquet this script
concatenates onto). Nothing downstream would have distinguished those 750 from measurement: they
carry the right states, the right fold and epoch columns, and cosines of a plausible magnitude. It
was deleted and re-run with an explicit destination. Any self-test MUST pass its own output path.
"""
from __future__ import annotations

import hashlib
import re
import sys
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent
FOUR = HERE / "gradient_cosine_observations.parquet"
OUT = HERE / "gradient_cosine_observations6.parquet"
NEW_STATES = ("california", "texas", "istanbul")
PAT = re.compile(r"^(?P<state>[a-z]+)_fold(?P<fold>[1-5])_diagnostics\.csv$")


def main(argv: list[str]) -> int:
    if len(argv) not in (2, 3):
        print(__doc__)
        return 2
    src = Path(argv[1])
    out = Path(argv[2]) if len(argv) == 3 else OUT
    files = sorted(p for p in src.rglob("*_diagnostics.csv") if PAT.match(p.name))
    assert files, f"no <state>_fold<k>_diagnostics.csv under {src} -- a zero-row parse is a broken instrument"

    print("=== FOLD-DISTINCTNESS GATE ===")
    print(f"{'file':38s} {'md5':34s} {'rows':>5s} {'cos':>4s} {'epochs':>12s}  verdict")
    seen: dict[str, str] = {}
    kept: list[pd.DataFrame] = []
    discarded: list[str] = []
    for p in files:
        m = PAT.match(p.name)
        state, fold = m["state"], int(m["fold"])
        raw = p.read_bytes()
        md5 = hashlib.md5(raw).hexdigest()
        d = pd.read_csv(p)
        reasons = []
        if "grad_cosine_shared" not in d.columns:
            reasons.append("no grad_cosine_shared column")
            n_cos, ep_desc = 0, "-"
        else:
            sub = d[["epoch", "grad_cosine_shared"]].dropna()
            n_cos = len(sub)
            eps = sorted(int(e) for e in sub["epoch"])
            ep_desc = f"{eps[0]}-{eps[-1]}" if eps else "none"
            if n_cos == 0:
                reasons.append("cosine column entirely empty")
            if eps != list(range(1, 51)):
                reasons.append(f"epoch series is not a complete 1..50 ({ep_desc}, {len(eps)} values)")
        if md5 in seen:
            reasons.append(f"md5 IDENTICAL to {seen[md5]} -- harvest fault, not a result")
        verdict = "KEEP" if not reasons else "DISCARD: " + "; ".join(reasons)
        print(f"{p.name:38s} {md5:34s} {len(d):5d} {n_cos:4d} {ep_desc:>12s}  {verdict}")
        if reasons:
            discarded.append(f"{p.name} ({'; '.join(reasons)})")
            continue
        seen[md5] = p.name
        sub = sub.copy()
        sub["state"], sub["fold"], sub["config"] = state, fold, "canonical"
        kept.append(sub.rename(columns={"grad_cosine_shared": "cos"})[
            ["state", "fold", "epoch", "cos", "config"]])

    print(f"\nkept {len(kept)} of {len(files)} files; distinct md5 = {len(seen)}")
    if discarded:
        print("DISCARDED, named rather than dropped silently:")
        for d_ in discarded:
            print(f"  - {d_}")

    assert len(seen) == len(kept), "distinct-hash bookkeeping disagrees with the kept count"
    assert not discarded, f"{len(discarded)} fold(s) failed the gate -- refusing to build the parquet"

    new = pd.concat(kept, ignore_index=True)
    new["fold"] = new["fold"].astype("int64")
    new["epoch"] = new["epoch"].astype("int64")
    by_state = new.groupby("state").size().to_dict()
    assert sorted(by_state) == sorted(NEW_STATES), f"unexpected states {sorted(by_state)}"
    assert all(v == 250 for v in by_state.values()), f"per-state rows {by_state} != 250 each"
    assert new.groupby("state")["fold"].nunique().eq(5).all(), "a state does not carry five folds"

    old = pd.read_parquet(FOUR)
    assert len(old) == 3900, f"the four-dataset parquet is not 3,900 rows ({len(old)})"
    overlap = set(old["state"]) & set(new["state"])
    assert not overlap, f"the new data would duplicate existing states: {overlap}"

    comb = pd.concat([old, new[old.columns.tolist()]], ignore_index=True)
    comb.to_parquet(out, index=False)
    print(f"\nwrote {out.name}: {len(comb)} rows = {len(old)} + {len(new)}")
    print(comb.groupby("state").size().to_string())
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
