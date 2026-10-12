"""F51 Tier 2 capacity-smoke analyzer.

Each Tier 2 smoke runs 5f×30ep at FL with one capacity knob altered. This
script reads `logs/f51_t2_<knob>.log` to find each smoke's run dir, then
computes paired Wilcoxon vs the B9 seed=42 reference (capped at ≤ep30 to
match the smoke window).

Decision rule (from F50_NORTH_STAR_DEEP_EXPLORATION_PROMPT.md §4):
  Promote a knob to 5×50ep paper-grade only if smoke shifts reg-best
  epoch < 1 ep AND peak shifts < 0.5 pp → don't promote.

i.e. promote iff Δ(reg-best epoch) ≥ 1 OR Δ(reg @≥ep5) ≥ 0.5 pp.

Usage:
    python scripts/analysis/f51_tier2_analysis.py
"""
from __future__ import annotations

import json
import re
from pathlib import Path

import numpy as np
import pandas as pd

try:
    from scipy.stats import wilcoxon
    HAS_SCIPY = True
except ImportError:
    HAS_SCIPY = False


REPO = Path("/workspace/PoiMtlNet")
LOGS = REPO / "logs"
RESULTS = REPO / "results" / "check2hgi" / "florida"
REF_RUN = RESULTS / "mtlnet_lr1.0e-04_bs2048_ep50_20260430_0522"  # B9 seed=42 env-B

EPOCH_CAP = 30  # smokes use 30 ep; cap reference to same window
MIN_EPOCH = 5   # min-best-epoch selector

# Decision thresholds
THRESHOLD_DELTA_REG_PP = 0.5
THRESHOLD_DELTA_BEST_EP = 1


def per_fold_best(run_dir: Path, task: str, metric: str,
                   min_epoch: int = MIN_EPOCH,
                   max_epoch: int = EPOCH_CAP) -> tuple[list[float], list[int]]:
    """Return (per-fold-best values, per-fold-best epochs)."""
    out_v: list[float] = []
    out_e: list[int] = []
    for fold in (1, 2, 3, 4, 5):
        csv = run_dir / "metrics" / f"fold{fold}_{task}_val.csv"
        if not csv.exists():
            return [], []
        df = pd.read_csv(csv)
        masked = df[(df["epoch"] >= min_epoch) & (df["epoch"] <= max_epoch)]
        if masked.empty:
            return [], []
        idx = masked[metric].idxmax()
        out_v.append(float(masked.loc[idx, metric]))
        out_e.append(int(masked.loc[idx, "epoch"]))
    return out_v, out_e


def _log_start_mtime(log_path: Path) -> float | None:
    """Return the first INFO line's timestamp from a smoke log (epoch
    seconds). This is the wall time at which the smoke launched."""
    try:
        with log_path.open() as f:
            for line in f:
                # Match: 2026-04-30 12:32:48,800 - INFO - ...
                m = re.match(r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})", line)
                if m:
                    import datetime as dt
                    return dt.datetime.strptime(
                        m.group(1), "%Y-%m-%d %H:%M:%S"
                    ).replace(tzinfo=dt.timezone.utc).timestamp()
    except FileNotFoundError:
        return None
    return None


def find_run_dir_for_smoke(knob_tag: str) -> Path | None:
    """Map a smoke tag to its run dir via log-start timestamp.

    The run dir is created seconds AFTER the smoke's first log line. We
    match by finding the ep30 run dir whose earliest metric-file mtime is
    just after (within a few minutes of) the log's first timestamp.
    """
    log_path = LOGS / f"f51_t2_{knob_tag}.log"
    if not log_path.exists():
        return None
    log_start = _log_start_mtime(log_path)
    if log_start is None:
        # Fall back to file mtime (works if smoke is mid-flight)
        log_start = log_path.stat().st_mtime
    candidates = []
    for d in RESULTS.iterdir():
        if not d.is_dir() or "ep30" not in d.name:
            continue
        try:
            first_metric = min(
                (m.stat().st_mtime for m in (d / "metrics").iterdir()),
                default=None,
            )
        except FileNotFoundError:
            continue
        if first_metric is None:
            continue
        # Run dir's first metric must be AFTER the log's first line, but
        # within ~15 min (a typical smoke is ~10 min).
        if 0 <= first_metric - log_start <= 900:
            candidates.append((first_metric, d))
    if not candidates:
        return None
    # Earliest run dir whose first metric is after the log start = this smoke's dir
    candidates.sort(key=lambda x: x[0])
    return candidates[0][1]


def parse_knob_levels(_script_path: Path) -> list[tuple[str, str, str]]:
    """Discover Tier 2 smokes via log filenames.

    Each smoke writes `logs/f51_t2_<tag>.log`. Tag is `<knob>_<value>` —
    last underscore splits name from value. Glob is the most reliable
    discovery path (the bash runner uses `for v in 128 384 512` loops
    that aren't parseable from the script source).
    """
    rows = []
    seen = set()
    for log in sorted(LOGS.glob("f51_t2_*.log")):
        tag = log.stem.replace("f51_t2_", "")
        if tag in seen:
            continue
        seen.add(tag)
        split_idx = tag.rfind("_")
        if split_idx > 0:
            rows.append((tag, tag[:split_idx], tag[split_idx + 1:]))
    return rows


def paired(arm_vals: list[float], ref_vals: list[float]) -> dict:
    if not arm_vals or len(arm_vals) != len(ref_vals):
        return {"valid": False}
    a = np.array(arm_vals); r = np.array(ref_vals)
    diffs = a - r
    out = {
        "valid": True,
        "n": len(a),
        "mean_arm_pp": float(a.mean() * 100),
        "std_arm_pp": float(a.std(ddof=1) * 100) if len(a) > 1 else 0.0,
        "mean_ref_pp": float(r.mean() * 100),
        "std_ref_pp": float(r.std(ddof=1) * 100) if len(r) > 1 else 0.0,
        "delta_pp": float((a.mean() - r.mean()) * 100),
        "n_pos": int((diffs > 0).sum()),
        "n_neg": int((diffs < 0).sum()),
        "p_value": None,
    }
    if HAS_SCIPY and len(a) >= 4 and not np.allclose(diffs, 0):
        try:
            stat = wilcoxon(diffs, zero_method="wilcox", alternative="greater")
            out["p_value"] = float(stat.pvalue)
        except ValueError:
            pass
    return out


def main() -> int:
    runner = REPO / "scripts" / "run_f51_tier2_capacity_smoke.sh"
    knobs = parse_knob_levels(runner)
    if not knobs:
        print("WARNING: could not parse knobs from runner; falling back to log glob")
        knobs = [(p.stem.replace("f51_t2_", ""), "?", "?")
                  for p in sorted(LOGS.glob("f51_t2_*.log"))]

    # Reference (B9 seed=42 capped @≤ep30)
    ref_reg_v, ref_reg_e = per_fold_best(REF_RUN, "next_region", "top10_acc_indist")
    ref_cat_v, ref_cat_e = per_fold_best(REF_RUN, "next_category", "f1")
    if not ref_reg_v:
        raise SystemExit(f"Cannot read reference run {REF_RUN}")

    print("# F51 Tier 2 capacity-smoke analysis (FL 5f×30ep, leak-free per-fold log_T)\n")
    print(f"Reference: B9 seed=42 (run `{REF_RUN.name}`) capped at ≤ep{EPOCH_CAP}")
    print(f"  reg @≥ep{MIN_EPOCH} top10_acc_indist: "
          f"mean={np.mean(ref_reg_v)*100:.2f} ± {np.std(ref_reg_v, ddof=1)*100:.2f} pp")
    print(f"  reg-best epochs: {ref_reg_e}")
    print(f"  cat @≥ep{MIN_EPOCH} f1: "
          f"mean={np.mean(ref_cat_v)*100:.2f} ± {np.std(ref_cat_v, ddof=1)*100:.2f} pp\n")

    print(f"Decision rule: promote iff Δ(reg-best epoch) ≥ {THRESHOLD_DELTA_BEST_EP} "
          f"OR Δ(reg @≥ep{MIN_EPOCH}) ≥ {THRESHOLD_DELTA_REG_PP} pp.\n")

    print("| knob | reg ± σ | Δreg | reg-best ep mean | Δep | cat ± σ | Δcat | p_reg | n+/n | promote? |")
    print("|---|---:|---:|---:|---:|---:|---:|---|---|---|")

    rows = []
    for tag, name, val in knobs:
        run_dir = find_run_dir_for_smoke(tag)
        if run_dir is None:
            print(f"| {name}={val} | _missing_ | — | — | — | — | — | — | — | — |")
            continue
        arm_reg_v, arm_reg_e = per_fold_best(run_dir, "next_region", "top10_acc_indist")
        arm_cat_v, _ = per_fold_best(run_dir, "next_category", "f1")
        if not arm_reg_v or not arm_cat_v:
            print(f"| {name}={val} | _incomplete ({run_dir.name})_ | — | — | — | — | — | — | — | — |")
            continue
        d_reg = paired(arm_reg_v, ref_reg_v)
        d_cat = paired(arm_cat_v, ref_cat_v)
        d_best_ep = float(np.mean(arm_reg_e)) - float(np.mean(ref_reg_e))
        # Promote only on positive lifts (a knob that LOWERS reg by ≥0.5 pp
        # is a regression, not a promotion candidate). reg-best epoch
        # shift can also be negative (saturating earlier), but we still
        # flag it for inspection because it's a mechanism shift.
        promote = (
            d_best_ep >= THRESHOLD_DELTA_BEST_EP  # later best ep
            or d_reg["delta_pp"] >= THRESHOLD_DELTA_REG_PP  # higher reg
        )
        if d_reg["delta_pp"] <= -THRESHOLD_DELTA_REG_PP:
            verdict = "⚠ regression"
        elif promote:
            verdict = "✅ PROMOTE"
        else:
            verdict = "❌ tied"
        p_str = f"{d_reg['p_value']:.4f}" if d_reg["p_value"] is not None else "n/a"
        print(f"| {name}={val} | {d_reg['mean_arm_pp']:.2f} ± {d_reg['std_arm_pp']:.2f} | "
              f"{d_reg['delta_pp']:+.2f} | {np.mean(arm_reg_e):.1f} | "
              f"{d_best_ep:+.1f} | "
              f"{d_cat['mean_arm_pp']:.2f} ± {d_cat['std_arm_pp']:.2f} | "
              f"{d_cat['delta_pp']:+.2f} | {p_str} | {d_reg['n_pos']}/{d_reg['n']} | "
              f"{verdict} |")
        rows.append({
            "knob": name, "value": val, "tag": tag,
            "run_dir": str(run_dir),
            "reg_mean_pp": d_reg["mean_arm_pp"], "reg_std_pp": d_reg["std_arm_pp"],
            "reg_delta_pp": d_reg["delta_pp"], "reg_p_value": d_reg["p_value"],
            "reg_n_pos": d_reg["n_pos"], "reg_n": d_reg["n"],
            "reg_best_ep_mean": float(np.mean(arm_reg_e)),
            "reg_best_ep_delta": d_best_ep,
            "cat_mean_pp": d_cat["mean_arm_pp"], "cat_std_pp": d_cat["std_arm_pp"],
            "cat_delta_pp": d_cat["delta_pp"],
            "promote": promote,
            "arm_reg_folds": arm_reg_v,
            "ref_reg_folds": ref_reg_v,
            "arm_cat_folds": arm_cat_v,
            "ref_cat_folds": ref_cat_v,
            "arm_reg_best_ep": arm_reg_e,
            "ref_reg_best_ep": ref_reg_e,
        })

    # Summary
    print()
    print("## Summary")
    print(f"- Smokes analyzed: {len(rows)}")
    promote_n = sum(1 for r in rows if r["promote"])
    print(f"- Promote candidates (Δreg ≥ {THRESHOLD_DELTA_REG_PP} pp OR "
          f"Δep ≥ {THRESHOLD_DELTA_BEST_EP}): **{promote_n}**")

    out_path = REPO / "docs" / "studies" / "check2hgi" / "research" / "F51_tier2_results.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps({"rows": rows, "n_promote": promote_n}, indent=2))
    print(f"\nWrote {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
