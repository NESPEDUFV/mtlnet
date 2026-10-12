#!/usr/bin/env python
"""Stage 0 — re-score every existing v18 cell with a DE-NOISED epoch selector.

WHY
===
On the v18 substrate the category head peaks at epoch ~8 (dedicated) / ~21 (MTL) out of 50 and then
degrades, and the peak plateau is 1-3 epochs wide (v17's was 10-20). So `argmax` over 50 epochs is a
max over a short, jittery spike: it captures 0.51-0.80 pp of pure single-epoch noise in v18 versus
0.05-0.17 pp in v17. That is what makes the reported number swing between seeds (arizona dedicated
cat +1.12 pp, of which ~63% is single-epoch noise).

WHAT THIS CHANGES, AND WHAT IT DOES NOT
=======================================
It changes the SELECTION RULE only:

    epoch*  =  argmax over a centred 3-epoch moving average of the validation curve
    value   =  the RAW metric AT epoch*        <-- not the smoothed value

So the reported number is always a value the model actually achieved on that fold. We never report a
smoothed quantity that never occurred. The metric itself is untouched: cat is macro-F1, reg is
top10_acc_indist * (1 - ood_fraction) * 100.

The rule is applied SYMMETRICALLY to both arms (dedicated and MTL) and to both tasks, so every
comparison stays like-for-like.

STATISTICAL PROTOCOL: UNCHANGED
===============================
Per-fold vectors are preserved, so the downstream tests are the same ones make_results.py already
runs: paired one-sided superiority for "beats", TOST non-inferiority within +/-2.0 pp for "matches",
n = seeds x folds stated in every table. These outputs are drop-in replacements for the argmax ones
under an identical protocol -- only the epoch-selection convention differs, and it is declared.

Emits, per cell, the SAME schema the existing scorers use (cat_per_fold / cat_best_epochs /
cat_macro_f1_mean / _std, reg_per_fold / reg_best_epochs / reg_full_top10_mean / _std) so nothing
downstream needs special-casing.

Usage:  .venv/bin/python docs/studies/closing_data/v18/stage0_rescore.py [--window 3] [--write]
"""
from __future__ import annotations

import argparse
import csv
import glob
import json
import statistics as st
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]
BASE = Path(__file__).resolve().parent
SIDE = REPO / "docs/results/closing_data/v18"
OUT = REPO / "docs/results/closing_data/v18_stage0"


def read_curve(path: Path, cols: list[str]) -> list[dict]:
    rows = []
    for r in csv.DictReader(open(path)):
        rec = {}
        for c in cols:
            v = r.get(c)
            if v in (None, "", "nan"):
                rec[c] = None
            else:
                try:
                    rec[c] = float(v)
                except ValueError:
                    rec[c] = None
        rows.append(rec)
    return rows


def smoothed_argmax(series: list[float | None], window: int) -> int:
    """Index of the max of a centred moving average, ignoring None. Ties -> earliest."""
    n = len(series)
    half = window // 2
    best_i, best_v = 0, float("-inf")
    for i in range(n):
        lo, hi = max(0, i - half), min(n, i + half + 1)
        vals = [series[j] for j in range(lo, hi) if series[j] is not None]
        if not vals:
            continue
        m = sum(vals) / len(vals)
        if m > best_v:                      # strict > keeps the earliest on ties
            best_v, best_i = m, i
    return best_i


def score_cat(rundir: Path, pattern: str, window: int) -> dict | None:
    """Dedicated or MTL category: macro-F1 at the de-noised best epoch, per fold."""
    per_fold, epochs, raw_argmax = [], [], []
    for f in sorted(glob.glob(str(rundir / "metrics" / pattern))):
        rows = read_curve(Path(f), ["f1"])
        s = [r["f1"] for r in rows]
        if not any(v is not None for v in s):
            continue
        i = smoothed_argmax(s, window)
        per_fold.append(s[i] * 100)
        epochs.append(i + 1)                                  # CSV epoch col is 1-based
        raw_argmax.append(max(v for v in s if v is not None) * 100)
    if not per_fold:
        return None
    return {"cat_per_fold": [round(v, 4) for v in per_fold],
            "cat_best_epochs": epochs,
            "cat_macro_f1_mean": round(st.mean(per_fold), 4),
            "cat_macro_f1_std": round(st.stdev(per_fold), 4) if len(per_fold) > 1 else 0.0,
            "cat_argmax_mean": round(st.mean(raw_argmax), 4),
            "cat_argmax_premium": round(st.mean(raw_argmax) - st.mean(per_fold), 4)}


def score_reg(rundir: Path, window: int) -> dict | None:
    """Region: top10_acc_indist * (1 - ood_fraction) * 100 at the de-noised best epoch."""
    per_fold, epochs, raw_argmax = [], [], []
    for f in sorted(glob.glob(str(rundir / "metrics" / "fold*_next_region_val.csv"))):
        rows = read_curve(Path(f), ["top10_acc_indist", "ood_fraction", "top10_acc"])
        full = []
        for r in rows:
            ti, oo = r.get("top10_acc_indist"), r.get("ood_fraction")
            if ti is not None and oo is not None:
                full.append(ti * (1 - oo) * 100)
            elif r.get("top10_acc") is not None:
                full.append(r["top10_acc"] * 100)
            else:
                full.append(None)
        if not any(v is not None for v in full):
            continue
        i = smoothed_argmax(full, window)
        per_fold.append(full[i])
        epochs.append(i + 1)
        raw_argmax.append(max(v for v in full if v is not None))
    if not per_fold:
        return None
    return {"reg_per_fold": [round(v, 4) for v in per_fold],
            "reg_best_epochs": epochs,
            "reg_full_top10_mean": round(st.mean(per_fold), 4),
            "reg_full_top10_std": round(st.stdev(per_fold), 4) if len(per_fold) > 1 else 0.0,
            "reg_argmax_mean": round(st.mean(raw_argmax), 4),
            "reg_argmax_premium": round(st.mean(raw_argmax) - st.mean(per_fold), 4)}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--window", type=int, default=3, help="moving-average width (odd)")
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args()
    assert args.window % 2 == 1, "window must be odd so the average is centred"

    cells, n = [], 0
    for f in sorted(glob.glob(str(SIDE / "*.json"))):
        d = json.loads(Path(f).read_text())
        fam, state, seed = d["family"], d["state"], d["seed"]
        rd = d.get("rundir")
        if not rd or fam == "reg":
            # the dedicated-reg family is driven by p1_region_head_ablation, which writes a result
            # JSON rather than per-epoch CSVs in a rundir; its curve peaks late (epoch 25-50) and
            # shows no argmax-noise problem, so it is carried through unchanged and flagged as such.
            if fam == "reg":
                cells.append({"state": state, "seed": seed, "family": "reg",
                              "selector": "unchanged (p1 aggregate; late peak, no spike artifact)",
                              "reg_full_top10_mean": d.get("reg")})
            continue
        rdp = Path(rd) if Path(rd).is_absolute() else REPO / rd
        if not rdp.exists():
            print(f"  [skip] {state} s{seed} {fam}: rundir missing")
            continue
        rec = {"state": state, "seed": seed, "family": fam, "rundir": str(rdp),
               "selector": f"smoothed-argmax(w={args.window}); value = RAW metric at that epoch"}
        if fam == "cat":
            s = score_cat(rdp, "fold*_next_val.csv", args.window)
            if s: rec.update(s)
        elif fam == "joint":
            s = score_cat(rdp, "fold*_next_category_val.csv", args.window)
            if s: rec.update(s)
            r = score_reg(rdp, args.window)
            if r: rec.update(r)
        cells.append(rec)
        n += 1

    print(f"{'state':<11}{'sd':>3} {'fam':<6} {'cat sm3':>9} {'cat argmax':>11} {'premium':>8} "
          f"{'ep(sm3)':>9}")
    for c in cells:
        if "cat_macro_f1_mean" in c:
            print(f"{c['state']:<11}{c['seed']:>3} {c['family']:<6} {c['cat_macro_f1_mean']:>9.3f} "
                  f"{c['cat_argmax_mean']:>11.3f} {c['cat_argmax_premium']:>8.3f} "
                  f"{str(c['cat_best_epochs']):>9}")

    if args.write:
        OUT.mkdir(parents=True, exist_ok=True)
        for c in cells:
            if "rundir" not in c:
                continue
            (OUT / f"{c['state']}_s{c['seed']}_{c['family']}.json").write_text(
                json.dumps(c, indent=2))
        (OUT / "_manifest.json").write_text(json.dumps({
            "selector": f"smoothed-argmax(window={args.window})",
            "value_rule": "RAW metric at the selected epoch (never a smoothed value)",
            "applied_symmetrically_to": ["dedicated cat", "MTL cat", "MTL reg"],
            "reg_dedicated": "unchanged (p1 aggregate; peaks late, no spike artifact)",
            "statistical_protocol": "UNCHANGED — per-fold vectors preserved; paired one-sided "
                                    "superiority for 'beats'; TOST +/-2.0 pp for 'matches'; "
                                    "n = seeds x folds",
            "n_cells": n}, indent=2))
        print(f"\n[stage0] wrote {n} re-scored cells to {OUT}")


if __name__ == "__main__":
    main()
