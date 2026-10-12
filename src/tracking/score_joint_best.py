#!/usr/bin/env python3
"""Post-hoc JOINT-BEST scorer for ONE MTL rundir (companion to a40_score_matched.py).

a40_score_matched.py scores the per-task DIAGNOSTIC-BEST convention (cat and reg each
at their OWN best epoch — the submitted MobiWac Table-3 numbers, disclosed in the paper
§6.2). This script recovers the SINGLE-CHECKPOINT (joint-best) numbers post-hoc from the
SAME per-epoch CSVs, reproducing the epoch the training-time joint-checkpoint gate
actually saved (mtl_cv._compute_joint_selectors + `joint_eligible = epoch_idx >=
joint_min_epoch`):

  e*  = argmax_e selector(e)   over epochs with 0-based index >= --min-best-epoch
        (ties -> earliest epoch, matching training's strict `>` improvement)
  selector(e) [geom_simple, default] = sqrt(cat_f1(e) * reg_top10_acc_indist(e))
  report: cat macro-F1(e*)  and  reg FULL top10 = top10_acc_indist(e*) * (1 - ood_fraction(e*))

DEFAULT --min-best-epoch 0 matches the v17 board: the v16/v17 canon bundles
(src/configs/canon.py _V16) and the board drivers (--canon none + explicit v17 recipe)
do NOT pin --min-best-epoch, so training ran with the ExperimentConfig default 0.
⚠ v11/v12/v15 (B9-recipe) runs pinned --min-best-epoch 5 — pass `--min-best-epoch 5`
when scoring those.

Selection logic is imported from src/tracking/scoring.py (the single source of truth;
loaded file-directly to stay torch-free). When the rundir carries the standardized
metrics/fold{N}_standard_scores.json artifacts (written by every post-fix run) with a
matching selector + min-best-epoch, those are read instead of re-deriving from CSVs.

Prints both conventions to 4dp (percent, like a40) and writes a committable JSON
sidecar `joint_best_score.json` into the rundir (C28: commit result JSONs).
Frozen result record: docs/reproducibility/mobiwac_v17/JOINT_BEST_RESULTS.md.

Usage: .venv/bin/python src/tracking/score_joint_best.py <rundir> \
           [--seed N] [--tag T] [--min-best-epoch 0] [--selector geom_simple] \
           [--cat-task next_category] [--reg-task next_region]
"""
import argparse
import csv
import glob
import importlib.util
import json
import re
import statistics as st
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]


def _load_scoring():
    """Load src/tracking/scoring.py file-directly (stdlib-pure), bypassing the
    tracking package __init__ (which imports torch)."""
    path = _REPO_ROOT / "src" / "tracking" / "scoring.py"
    spec = importlib.util.spec_from_file_location("_standard_scoring", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


scoring = _load_scoring()


def _fold_ids(rundir: Path, task: str):
    """REAL fold ids present for `task`, from metrics/fold{N}_{task}_val.csv."""
    ids = []
    for f in glob.glob(str(rundir / f"metrics/fold*_{task}_val.csv")):
        m = re.match(rf"fold(\d+)_{re.escape(task)}_val\.csv$", Path(f).name)
        if m:
            ids.append(int(m.group(1)))
    return sorted(ids)


def _read_series(csv_path: Path, warnings):
    """Read a fold val CSV into {column: [values]} ordered by the epoch column.

    Guards: rows sorted by epoch value; non-contiguous / non-1-based epoch columns
    are warned about (positional alignment index i == epoch i+1 is then approximate).
    """
    with open(csv_path) as fh:
        rows = list(csv.DictReader(fh))
    rows.sort(key=lambda r: float(r["epoch"]))
    epochs = [int(float(r["epoch"])) for r in rows]
    if epochs and epochs != list(range(1, len(epochs) + 1)):
        warnings.append(f"{csv_path.name}: epoch column is not contiguous 1..N ({epochs[:3]}...)")
    out = {}
    for key in rows[0].keys() if rows else []:
        if key == "epoch":
            continue
        try:
            out[key] = [float(r[key]) for r in rows]
        except (TypeError, ValueError):
            continue  # non-numeric column
    return out


def _from_artifact(rundir: Path, fold_id: int, selector: str, min_best_epoch: int):
    """Return the fold's standard_scores payload iff a matching artifact exists."""
    p = rundir / "metrics" / f"fold{fold_id}_standard_scores.json"
    if not p.exists():
        return None
    try:
        d = json.loads(p.read_text())
    except (json.JSONDecodeError, OSError):
        return None
    if d.get("selector_name") != selector or int(d.get("min_best_epoch", -1)) != min_best_epoch:
        return None
    return d


def _ms(x):
    return (st.mean(x), (st.pstdev(x) if len(x) > 1 else 0.0), len(x)) if x else (float("nan"), 0.0, 0)


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("rundir")
    ap.add_argument("--seed", type=int, default=None)
    ap.add_argument("--tag", type=str, default=None)
    ap.add_argument("--min-best-epoch", type=int, default=0,
                    help="0-based joint gate; 0 = v17 board default. B9/v11/v12/v15 runs: pass 5.")
    ap.add_argument("--selector", type=str, default="geom_simple",
                    choices=list(scoring.RECOMPUTABLE_SELECTORS),
                    help="joint checkpoint selector (training --checkpoint-selector).")
    ap.add_argument("--cat-task", type=str, default="next_category")
    ap.add_argument("--reg-task", type=str, default="next_region")
    args = ap.parse_args()

    rundir = Path(args.rundir).resolve()
    if not rundir.exists():
        raise SystemExit(f"rundir not found: {rundir}")

    cat_ids = _fold_ids(rundir, args.cat_task)
    reg_ids = _fold_ids(rundir, args.reg_task)
    fold_ids = sorted(set(cat_ids) & set(reg_ids))
    warnings = []
    if set(cat_ids) != set(reg_ids):
        warnings.append(f"fold-id mismatch: cat={cat_ids} reg={reg_ids}; scoring the intersection")
    if not fold_ids:
        raise SystemExit(f"no paired fold CSVs for tasks ({args.cat_task}, {args.reg_task}) under {rundir}/metrics/")

    per_fold = []       # (fold_id, scores_dict, source)
    for fid in fold_ids:
        art = _from_artifact(rundir, fid, args.selector, args.min_best_epoch)
        if art is not None:
            per_fold.append((fid, art, "standard_scores.json"))
            continue
        fold_warn = []
        cat_series = _read_series(rundir / "metrics" / f"fold{fid}_{args.cat_task}_val.csv", fold_warn)
        reg_series = _read_series(rundir / "metrics" / f"fold{fid}_{args.reg_task}_val.csv", fold_warn)
        scores = scoring.compute_standard_scores(
            cat_series, reg_series,
            selector_name=args.selector,
            min_best_epoch=args.min_best_epoch,
        )
        if scores is None:
            warnings.append(f"fold{fid}: missing f1 series; skipped")
            continue
        scores["warnings"] = fold_warn + scores["warnings"]
        per_fold.append((fid, scores, "csv"))

    # Collect the two conventions (percent, like a40_score_matched.py).
    jb_cat, jb_reg, jb_eps, jb_sel = [], [], [], []
    db_cat, db_reg, db_cat_eps, db_reg_eps = [], [], [], []
    per_fold_out = []
    skipped_joint = []
    for fid, s, source in per_fold:
        for w in s.get("warnings", []):
            warnings.append(f"fold{fid}: {w}")
        cd, rd, jb = s["cat_diag_best"], s["reg_diag_best"], s["joint_best"]
        db_cat.append(cd["f1"] * 100.0); db_cat_eps.append(cd["epoch"])
        db_reg.append(rd["top10_full"] * 100.0); db_reg_eps.append(rd["epoch"])
        row = {
            "fold": fid, "source": source,
            "diag_best": {"cat_f1": round(cd["f1"] * 100.0, 4), "cat_epoch": cd["epoch"],
                          "reg_full_top10": round(rd["top10_full"] * 100.0, 4), "reg_epoch": rd["epoch"]},
        }
        if jb is not None:
            jb_cat.append(jb["cat_f1"] * 100.0)
            jb_reg.append(jb["top10_full"] * 100.0)
            jb_eps.append(jb["epoch"]); jb_sel.append(jb["selector"])
            row["joint_best"] = {"epoch": jb["epoch"], "selector": round(jb["selector"], 6),
                                 "cat_f1": round(jb["cat_f1"] * 100.0, 4),
                                 "reg_full_top10": round(jb["top10_full"] * 100.0, 4)}
        else:
            skipped_joint.append(fid)
            row["joint_best"] = None
        per_fold_out.append(row)
    if skipped_joint:
        warnings.append(f"folds {skipped_joint}: no joint-eligible epoch (min_best_epoch gate)")

    jcm, jcs, jn = _ms(jb_cat)
    jrm, jrs, _ = _ms(jb_reg)
    dcm, dcs, dn = _ms(db_cat)
    drm, drs, _ = _ms(db_reg)

    print(f"=== joint-best score: {rundir.name} ===")
    if args.seed is not None or args.tag is not None:
        print(f"  seed={args.seed}  tag={args.tag}")
    print(f"  selector={args.selector}  min_best_epoch={args.min_best_epoch}  "
          f"sources={{{', '.join(sorted(set(src for _, _, src in per_fold)))}}}")
    print(f"  JOINT-BEST (single checkpoint, epoch e* = argmax selector):")
    print(f"    cat macro-F1       = {jcm:.4f} ± {jcs:.4f}  (n={jn})  per-fold={[round(x, 4) for x in jb_cat]}  epochs={jb_eps}")
    print(f"    reg FULL top10_acc = {jrm:.4f} ± {jrs:.4f}  (n={jn})  per-fold={[round(x, 4) for x in jb_reg]}  epochs={jb_eps}")
    print(f"  DIAG-BEST (per-task best epochs — the a40_score_matched / paper-Table-3 convention):")
    print(f"    cat macro-F1       = {dcm:.4f} ± {dcs:.4f}  (n={dn})  epochs={db_cat_eps}")
    print(f"    reg FULL top10_acc = {drm:.4f} ± {drs:.4f}  (n={dn})  epochs={db_reg_eps}")
    print(f"  Δ (joint − diag)     : cat {jcm - dcm:+.4f}  reg {jrm - drm:+.4f}")
    for w in warnings:
        print(f"  WARN: {w}")

    out = {
        "rundir": str(rundir.relative_to(_REPO_ROOT)) if str(rundir).startswith(str(_REPO_ROOT)) else str(rundir),
        "seed": args.seed,
        "tag": args.tag,
        "method": (
            "joint-best: e* = argmax_e selector(e) over epochs with 0-based index >= min_best_epoch "
            "(ties -> earliest; selector geom_simple = sqrt(cat_f1 * reg_top10_acc_indist), the "
            "mtl_cv joint-checkpoint gate); report cat macro-f1(e*) and reg full top10 = "
            "top10_acc_indist(e*)*(1-ood_fraction(e*)). diag-best: per-task best epochs, ungated "
            "(a40_score_matched.py convention). Values are percent; fold-mean ± pstdev. "
            "Selection logic: src/tracking/scoring.py."
        ),
        "selector_name": args.selector,
        "min_best_epoch": args.min_best_epoch,
        "cat_task": args.cat_task,
        "reg_task": args.reg_task,
        "joint_best": {
            "cat_macro_f1_mean": round(jcm, 4), "cat_macro_f1_std": round(jcs, 4),
            "reg_full_top10_mean": round(jrm, 4), "reg_full_top10_std": round(jrs, 4),
            "cat_per_fold": [round(x, 4) for x in jb_cat],
            "reg_per_fold": [round(x, 4) for x in jb_reg],
            "epochs": jb_eps,
            "selector_per_fold": [round(x, 6) for x in jb_sel],
            "n_folds": jn,
        },
        "diag_best": {
            "cat_macro_f1_mean": round(dcm, 4), "cat_macro_f1_std": round(dcs, 4),
            "reg_full_top10_mean": round(drm, 4), "reg_full_top10_std": round(drs, 4),
            "cat_per_fold": [round(x, 4) for x in db_cat],
            "reg_per_fold": [round(x, 4) for x in db_reg],
            "cat_best_epochs": db_cat_eps,
            "reg_best_epochs": db_reg_eps,
            "n_folds": dn,
        },
        "delta_joint_minus_diag": {"cat": round(jcm - dcm, 4), "reg": round(jrm - drm, 4)},
        "per_fold": per_fold_out,
        "warnings": warnings,
    }
    sidecar = rundir / "joint_best_score.json"
    sidecar.write_text(json.dumps(out, indent=2))
    print(f"  wrote {sidecar}")


if __name__ == "__main__":
    main()
