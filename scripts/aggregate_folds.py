#!/usr/bin/env python3
"""Aggregate the per-fold artifacts of ONE (possibly fanned-out) rundir.

The multi-fold companion to ``scripts/train.py --only-folds k --run-id NAME``: when
the 5 folds of one execution are run as separate processes (each writing its own
``fold{k}_*`` artifacts into the SAME ``--run-id`` rundir, by real fold id), this
reads them all back and writes a single clean aggregate — so "the 5 folds point to
one execution and the aggregation is clear".

It reproduces the canonical per-task **diagnostic-best, fold-mean** method (the same
one ``scripts/closing_data/a40_score_matched.py`` uses), reading
``metrics/fold*_<task>_val.csv``:

  * category : macro-F1 (``f1`` column) at the f1-best epoch
  * region   : FULL top10 = ``top10_acc_indist`` * (1 - ``ood_fraction``) at the
               indist-best epoch  (+ raw Acc@1/5/10, MRR for context)

Output: ``<rundir>/fold_aggregate.json`` + a printed table. It also validates that
the expected fold set is present (``--expect 0,1,2,3,4``) and flags any missing
fold, so a half-finished fan-out can't masquerade as a complete run.

Usage:
  PYTHONPATH=src python scripts/aggregate_folds.py <rundir> [--expect 0,1,2,3,4] [--tag T]
"""
from __future__ import annotations

import argparse
import csv
import glob
import json
import re
import statistics as st
from pathlib import Path
from typing import Dict, List, Optional, Tuple

_FOLD_RE = re.compile(r"fold(\d+)_(.+)_val\.csv$")


def _discover(rundir: Path) -> Dict[str, Dict[int, Path]]:
    """Map task -> {real_fold_id (1-indexed on disk) -> val csv path}."""
    out: Dict[str, Dict[int, Path]] = {}
    for f in sorted(glob.glob(str(rundir / "metrics" / "fold*_*_val.csv"))):
        m = _FOLD_RE.search(Path(f).name)
        if not m:
            continue
        fold_1idx, task = int(m.group(1)), m.group(2)
        out.setdefault(task, {})[fold_1idx] = Path(f)
    return out


def _best_row(rows: List[dict], metric: str) -> Optional[dict]:
    rows = [r for r in rows if metric in r and r[metric] not in ("", None)]
    if not rows:
        return None
    return max(rows, key=lambda r: float(r[metric]))


def _fold_value(csv_path: Path, task: str) -> Optional[Tuple[Dict[str, float], int]]:
    rows = list(csv.DictReader(open(csv_path)))
    if not rows:
        return None
    cols = set(rows[0].keys())
    is_region = "top10_acc_indist" in cols
    sel = "top10_acc_indist" if is_region else ("f1" if "f1" in cols else None)
    if sel is None:
        return None
    best = _best_row(rows, sel)
    if best is None:
        return None
    epoch = int(float(best.get("epoch", -1)))
    vals: Dict[str, float] = {}
    if is_region:
        ood = float(best.get("ood_fraction", 0.0))
        vals["top10_full"] = float(best["top10_acc_indist"]) * (1.0 - ood) * 100.0
        for k in ("accuracy", "top3_acc", "top5_acc", "top10_acc", "mrr"):
            if k in best and best[k] not in ("", None):
                vals[k] = float(best[k]) * 100.0
    else:
        vals["macro_f1"] = float(best["f1"]) * 100.0
        for k in ("accuracy", "top3_acc"):
            if k in best and best[k] not in ("", None):
                vals[k] = float(best[k]) * 100.0
    return vals, epoch


def _ms(x: List[float]) -> Tuple[float, float, int]:
    if not x:
        return float("nan"), 0.0, 0
    return st.mean(x), (st.pstdev(x) if len(x) > 1 else 0.0), len(x)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("rundir")
    ap.add_argument("--expect", default=None,
                    help="comma-separated 0-indexed canonical fold ids that MUST be present (e.g. 0,1,2,3,4)")
    ap.add_argument("--tag", default=None)
    args = ap.parse_args()

    rundir = Path(args.rundir).resolve()
    if not rundir.exists():
        raise SystemExit(f"rundir not found: {rundir}")

    discovered = _discover(rundir)
    if not discovered:
        raise SystemExit(f"no per-fold val CSVs under {rundir}/metrics/ — nothing to aggregate.")

    expect_1idx = None
    if args.expect:
        expect_1idx = sorted({int(x) + 1 for x in args.expect.split(",") if x.strip() != ""})

    report: Dict[str, dict] = {}
    missing_any = False
    for task, fold_map in sorted(discovered.items()):
        present = sorted(fold_map)
        missing = [k for k in (expect_1idx or []) if k not in fold_map]
        if missing:
            missing_any = True
        per_fold: Dict[int, dict] = {}
        per_metric: Dict[str, List[float]] = {}
        epochs: Dict[int, int] = {}
        for k in present:
            res = _fold_value(fold_map[k], task)
            if res is None:
                continue
            vals, epoch = res
            per_fold[k - 1] = vals  # back to 0-indexed fold id for the report
            epochs[k - 1] = epoch
            for mk, mv in vals.items():
                per_metric.setdefault(mk, []).append(mv)
        agg = {}
        for mk, xs in per_metric.items():
            mean, std, n = _ms(xs)
            agg[mk] = {"mean": round(mean, 4), "std": round(std, 4), "n": n}
        report[task] = {
            "folds_present": [k - 1 for k in present],
            "folds_missing": [k - 1 for k in missing],
            "best_epochs": epochs,
            "aggregate": agg,
            "per_fold": per_fold,
        }

    out = {
        "rundir": rundir.name,
        "tag": args.tag,
        "run_id_leaf": rundir.name,
        "complete": not missing_any,
        "tasks": report,
        "method": "per-task diagnostic-best, fold-mean (region FULL top10 = indist*(1-ood) at indist-best ep; "
                  "category macro-F1 at f1-best ep) — matches a40_score_matched.py",
    }
    sidecar = rundir / "fold_aggregate.json"
    sidecar.write_text(json.dumps(out, indent=2))

    print(f"=== fold aggregate: {rundir.name} ===")
    for task, r in report.items():
        head = "region" if any("top10" in m for m in r["aggregate"]) else "category"
        print(f"  [{task}] folds={r['folds_present']}"
              + (f"  MISSING={r['folds_missing']}" if r["folds_missing"] else ""))
        for mk, s in r["aggregate"].items():
            star = " *" if (head == "region" and mk == "top10_full") or (head != "region" and mk == "macro_f1") else ""
            print(f"      {mk:<12} = {s['mean']:.4f} ± {s['std']:.4f}  (n={s['n']}){star}")
    if missing_any:
        print("  ⚠ INCOMPLETE: some expected folds are missing — do NOT cite this aggregate as a full run.")
    print(f"  wrote {sidecar}")


if __name__ == "__main__":
    main()
