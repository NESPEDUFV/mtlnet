#!/usr/bin/env python
"""Regenerate docs/studies/closing_data/v18/data/v18_results.json from the rundirs.

This is the reproducer. It reads the scorer-written artifacts inside each rundir -- never a cached
summary -- so re-running it after any re-score picks the new values up. The per-cell sidecars in
docs/results/closing_data/v18/ supply only the (state, seed, family) -> rundir mapping; every number
below is read back out of the rundir itself.

Schema mirrors joint_best/data/j1_results.json (per_run / cells / order) with v18-specific fields
added rather than existing ones repurposed.

Conventions, never mixed (see ../JOINT_BEST_SCORING.md):
  db_*  diag-best   per-task diagnostic-best epochs -- the Table-3 convention
  jb_*  joint-best  the single served checkpoint, geom_simple selector, min_best_epoch 0

Usage:  .venv/bin/python docs/studies/closing_data/v18/score_all.py [--write]
"""
from __future__ import annotations

import argparse
import json
import statistics as stats
import subprocess
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]
SIDE = REPO / "docs/results/closing_data/v18"
BASE = REPO / "docs/studies/closing_data/v18"
STATES = ["istanbul", "alabama", "arizona", "florida", "texas", "california"]
SEEDS = [0, 1, 7, 100]

# v17 published values, n=20 (v17_completion/CEILINGS_N20_FINAL.md). Deltas are computed against
# these; they are a DIFFERENT substrate, so every delta carries that label in the markdown.
V17 = {
    "alabama":    {"mtl_cat": 64.54, "mtl_reg": 69.80, "stl_cat": 56.82, "stl_reg": 70.11},
    "arizona":    {"mtl_cat": 65.83, "mtl_reg": 59.56, "stl_cat": 56.43, "stl_reg": 59.46},
    "florida":    {"mtl_cat": 79.85, "mtl_reg": 77.42, "stl_cat": 74.51, "stl_reg": 76.70},
    "california": {"mtl_cat": 77.05, "mtl_reg": 65.69, "stl_cat": 70.60, "stl_reg": 63.49},
    "texas":      {"mtl_cat": 77.24, "mtl_reg": 67.06, "stl_cat": 69.79, "stl_reg": 64.95},
    "istanbul":   {"mtl_cat": 63.33, "mtl_reg": 75.44, "stl_cat": 54.74, "stl_reg": 75.16},
}


def sha() -> str:
    try:
        return subprocess.run(["git", "-C", str(REPO), "rev-parse", "HEAD"],
                              capture_output=True, text=True, timeout=15).stdout.strip()
    except Exception:
        return "unknown"


def jload(p: Path):
    try:
        return json.loads(Path(p).read_text())
    except Exception:
        return None


def sidecar(state: str, seed: int, family: str):
    return jload(SIDE / f"{state}_s{seed}_{family}.json")


def resolve(p: str | None) -> Path | None:
    if not p:
        return None
    q = Path(p)
    return q if q.is_absolute() else REPO / q


def collect_run(state: str, seed: int) -> dict | None:
    """One object per (state, seed): all three families, read back from the rundirs."""
    entry: dict = {
        "state": state, "seed": seed,
        "forward_only": True, "in_channels": 15,
        "v18_config": {"engine": "check2hgi_v18", "repr_seed": 42, "repr_epochs": 500,
                       "encoder": "resln", "dim": 64, "num_layers": 2,
                       "node_layout": ["canonical_11", "continuous_time_4"],
                       "readout": "prefix_forward_only"},
        "protocol": {"precision": "fp32", "compile": True, "tf32": True,
                     "folds": 5, "epochs": 50, "selector": "geom_simple",
                     "min_best_epoch": 0},
        "warnings": [],
    }
    found = False

    # ---- (a) dedicated next-category ------------------------------------------------------
    sc = sidecar(state, seed, "cat")
    if sc:
        rd = resolve(sc.get("rundir"))
        d = jload(rd / "stl_cat_ceiling_score.json") if rd else None
        if d:
            found = True
            entry["cat_rundir"] = str(rd)
            entry["cat_pid"] = str(rd.name).rsplit("_", 1)[-1]
            entry["stl_cat"] = d.get("cat_macro_f1_mean")
            entry["stl_cat_std"] = d.get("cat_macro_f1_std")
            entry["stl_cat_folds"] = d.get("cat_per_fold")
            entry["stl_cat_epochs"] = d.get("cat_best_epochs")
            entry["cat_wall_seconds"] = sc.get("wall_seconds")
        else:
            entry["warnings"].append("cat sidecar present but stl_cat_ceiling_score.json unreadable")

    # ---- (b) dedicated next-region --------------------------------------------------------
    sr = sidecar(state, seed, "reg")
    if sr:
        rj = resolve(sr.get("rundir"))
        d = jload(rj) if rj else None
        if d:
            found = True
            head = d.get("heads", {}).get("next_stan_flow", {})
            agg = head.get("aggregate", {})
            entry["reg_result_json"] = str(rj)
            entry["stl_reg"] = round(agg.get("top10_acc_mean", 0) * 100, 4) or None
            # per-fold lives under heads.<head>.per_fold as a list of dicts, one per fold;
            # top10_acc there is the same quantity the aggregate means over.
            pf = head.get("per_fold")
            if isinstance(pf, list) and pf:
                folds = [f.get("top10_acc") for f in pf if f.get("top10_acc") is not None]
                if folds:
                    entry["stl_reg_folds"] = [round(x * 100, 4) for x in folds]
            entry["reg_wall_seconds"] = sr.get("wall_seconds")
        else:
            entry["warnings"].append("reg sidecar present but P1 result json unreadable")

    # ---- (c) joint v17 MTL ----------------------------------------------------------------
    sj = sidecar(state, seed, "joint")
    if sj:
        rd = resolve(sj.get("rundir"))
        if rd:
            found = True
            entry["rundir"] = str(rd)
            entry["pid"] = str(rd.name).rsplit("_", 1)[-1]
            entry["joint_wall_seconds"] = sj.get("wall_seconds")
            a = jload(rd / "a40_matched_score.json")
            if a:
                entry.update(
                    db_cat=a.get("cat_macro_f1_mean"), db_cat_std=a.get("cat_macro_f1_std"),
                    db_cat_folds=a.get("cat_per_fold"), db_cat_epochs=a.get("cat_best_epochs"),
                    db_reg=a.get("reg_full_top10_mean"), db_reg_std=a.get("reg_full_top10_std"),
                    db_reg_folds=a.get("reg_per_fold"), db_reg_epochs=a.get("reg_best_epochs"),
                )
            else:
                entry["warnings"].append("joint rundir has no a40_matched_score.json")
            b = jload(rd / "joint_best_score.json")
            if b:
                entry.update(
                    jb_cat=b.get("cat_macro_f1_mean") or b.get("jb_cat"),
                    jb_reg=b.get("reg_full_top10_mean") or b.get("jb_reg"),
                    jb_cat_folds=b.get("cat_per_fold") or b.get("jb_cat_folds"),
                    jb_reg_folds=b.get("reg_per_fold") or b.get("jb_reg_folds"),
                    jb_epochs=b.get("joint_epochs") or b.get("jb_epochs"),
                )
            else:
                entry["warnings"].append("joint rundir has no joint_best_score.json")

            # §6.6 sanity, recorded rather than asserted -- the markdown must surface it
            v17 = V17.get(state, {})
            if entry.get("db_cat") is not None and v17.get("mtl_cat") is not None:
                if abs(entry["db_cat"] - v17["mtl_cat"]) < 5:
                    entry["warnings"].append(
                        f"VERIFY: joint cat {entry['db_cat']:.2f} within 5 pp of v17 "
                        f"{v17['mtl_cat']:.2f} -- forward-only path suspect")
            if entry.get("db_reg") is not None and v17.get("mtl_reg") is not None:
                if abs(entry["db_reg"] - v17["mtl_reg"]) > 2:
                    entry["warnings"].append(
                        f"VERIFY: joint reg moved {entry['db_reg'] - v17['mtl_reg']:+.2f} pp "
                        f"vs v17 {v17['mtl_reg']:.2f}")
    return entry if found else None


def agg(vals: list[float]) -> dict:
    vals = [v for v in vals if v is not None]
    if not vals:
        return {"mean": None, "sd": None, "n_seeds": 0, "n": 0}
    return {"mean": round(stats.mean(vals), 4),
            "sd": round(stats.stdev(vals), 4) if len(vals) > 1 else 0.0,
            "n_seeds": len(vals), "n": len(vals) * 5}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true", help="write data/v18_results.json")
    args = ap.parse_args()

    per_run, order = [], []
    for st in STATES:
        for sd in SEEDS:
            e = collect_run(st, sd)
            if e:
                per_run.append(e)
                order.append(f"{st}_s{sd}")

    cells = {}
    for st in STATES:
        runs = [e for e in per_run if e["state"] == st]
        if not runs:
            continue
        c = {
            "stl_cat":  agg([e.get("stl_cat") for e in runs]),
            "stl_reg":  agg([e.get("stl_reg") for e in runs]),
            "joint_cat_diag_best": agg([e.get("db_cat") for e in runs]),
            "joint_reg_diag_best": agg([e.get("db_reg") for e in runs]),
            "joint_cat_joint_best": agg([e.get("jb_cat") for e in runs]),
            "joint_reg_joint_best": agg([e.get("jb_reg") for e in runs]),
            "v17_published": V17.get(st),
        }
        # PAIRED ceiling means (audit fix 2026-08-10). "stl_cat" above averages EVERY seed with a
        # dedicated cell; "joint_cat_diag_best" averages the seeds with a JOINT cell. Those sets
        # diverge as soon as a cheap cell runs ahead of its joint cell -- which is exactly what the
        # rented lane is for (alabama s100 cat+reg landed while s100 joint had not). Differencing
        # the unpaired means gave a Δ over one seed set sitting next to an n and a p-value computed
        # over another. Restrict the ceiling to the seeds that also have a joint result, so the
        # contrast compares like with like. Identical to the old behaviour when the sets coincide.
        # SYMMETRIC pairing. Restricting only the dedicated side was half the fix: a seed with a
        # JOINT result and no dedicated cell (what a joint-only rented purchase produces) would
        # land in the joint mean while being excluded from the dedicated mean — the same
        # mismatch, mirrored. Build the subset that has BOTH arms and average each side over it.
        _pc = [e for e in runs if e.get("stl_cat") is not None and e.get("db_cat") is not None]
        _pr = [e for e in runs if e.get("stl_reg") is not None and e.get("db_reg") is not None]
        c["stl_cat_paired"]   = agg([e["stl_cat"] for e in _pc])
        c["joint_cat_paired"] = agg([e["db_cat"]  for e in _pc])
        c["stl_reg_paired"]   = agg([e["stl_reg"] for e in _pr])
        c["joint_reg_paired"] = agg([e["db_reg"]  for e in _pr])
        # Deltas WITHIN v18 (same protocol, so these are the citable contrasts)
        if c["joint_cat_paired"]["mean"] is not None and c["stl_cat_paired"]["mean"] is not None:
            c["delta_cat_vs_own_ceiling"] = round(
                c["joint_cat_paired"]["mean"] - c["stl_cat_paired"]["mean"], 4)
        if c["joint_reg_paired"]["mean"] is not None and c["stl_reg_paired"]["mean"] is not None:
            c["delta_reg_vs_own_ceiling"] = round(
                c["joint_reg_paired"]["mean"] - c["stl_reg_paired"]["mean"], 4)
        # Deltas vs v17 -- ACROSS SUBSTRATES, descriptive only, never a superiority claim
        v = V17.get(st, {})
        if c["joint_cat_diag_best"]["mean"] is not None:
            c["delta_cat_vs_v17_cross_substrate"] = round(
                c["joint_cat_diag_best"]["mean"] - v["mtl_cat"], 4)
        if c["joint_reg_diag_best"]["mean"] is not None:
            c["delta_reg_vs_v17_cross_substrate"] = round(
                c["joint_reg_diag_best"]["mean"] - v["mtl_reg"], 4)
        cells[st] = c

    out = {
        "meta": {
            "study": "v18",
            "generated_utc": datetime.now(timezone.utc).isoformat(),
            "commit_sha": sha(),
            "definition": "v17 recipe on a forward-only check-in graph with 4 elapsed-time node "
                          "columns (in_channels 15)",
            "forward_only": True,
            "in_channels": 15,
            "seeds": SEEDS,
            "folds": 5,
            "n_per_full_cell": 20,
            "conventions": {
                "db_*": "diag-best: cat macro-F1 at f1-best epoch; reg top10_acc_indist*(1-ood)*100 "
                        "at indist-best epoch (Table-3 convention)",
                "jb_*": "joint-best: both heads at the single geom_simple-selected epoch, "
                        "min_best_epoch 0",
                "delta_*_vs_own_ceiling": "within-v18, same protocol -- the citable contrast",
                "delta_*_vs_v17_cross_substrate": "DESCRIPTIVE ONLY: different substrate, so this "
                                                  "is not a superiority test",
            },
        },
        "per_run": per_run,
        "cells": cells,
        "order": order,
    }

    txt = json.dumps(out, indent=1)
    if args.write:
        (BASE / "data").mkdir(parents=True, exist_ok=True)
        (BASE / "data/v18_results.json").write_text(txt)
        print(f"[score_all] wrote data/v18_results.json  "
              f"({len(per_run)} runs, {len(cells)} states)")
    else:
        print(txt[:4000])
        print(f"\n[score_all] {len(per_run)} runs, {len(cells)} states (use --write to persist)")


if __name__ == "__main__":
    main()
