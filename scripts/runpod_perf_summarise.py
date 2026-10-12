"""Read tagged FL H3-alt run dirs and emit a comparison vs NORTH_STAR.

Locates run dirs whose `.runpod_tag` matches a known variant
(baseline/tf32/compile) and writes a markdown table with cat F1 +
reg Acc@10_indist, plus per-variant deltas vs the published
NORTH_STAR FL H3-alt numbers.

The published reference is fixed inline because it lives in
`docs/NORTH_STAR.md` as prose, not a parseable file:
    cat F1                 = 67.92 +/- 0.72
    reg Acc@10_indist      = 71.96 +/- 0.68
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

# F48-H3-alt FL 5f x 50ep, seed 42 — from NORTH_STAR.md (post-F37, 2026-04-28)
NORTH_STAR_FL = {
    "cat_f1":             {"mean": 67.92, "std": 0.72, "source": "NORTH_STAR.md"},
    "reg_top10_indist":   {"mean": 71.96, "std": 0.68, "source": "NORTH_STAR.md"},
}

VARIANT_ORDER = ["baseline", "tf32", "compile", "bs2048"]


def find_tagged_runs(results_dir: Path) -> dict[str, Path]:
    """Return {tag -> latest tagged run dir} for known tags."""
    out: dict[str, Path] = {}
    candidates = sorted(results_dir.glob("mtlnet_lr*_bs*_ep*_*"), reverse=True)
    for run_dir in candidates:
        tag_file = run_dir / ".runpod_tag"
        if not tag_file.exists():
            continue
        tag = tag_file.read_text().strip()
        if tag in VARIANT_ORDER and tag not in out:
            out[tag] = run_dir
    return out


def load_summary(run_dir: Path) -> dict | None:
    f = run_dir / "summary" / "full_summary.json"
    if not f.exists():
        return None
    return json.loads(f.read_text())


def fmt_pct(mean: float | None, std: float | None) -> str:
    if mean is None:
        return "—"
    if std is None or std == 0:
        return f"{mean*100:.2f}"
    return f"{mean*100:.2f} ± {std*100:.2f}"


def fmt_delta(variant_mean: float | None, ref: dict) -> str:
    if variant_mean is None:
        return "—"
    delta_pp = variant_mean * 100 - ref["mean"]
    sigma = ref["std"]
    z = abs(delta_pp) / sigma if sigma > 0 else 0
    sign = "+" if delta_pp >= 0 else ""
    marker = "✓" if z <= 1 else ("~" if z <= 2 else "✗")
    return f"{sign}{delta_pp:.2f} pp ({z:.2f}σ) {marker}"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--results-dir", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()

    found = find_tagged_runs(args.results_dir)
    if not found:
        print(f"no tagged runs found under {args.results_dir}")
        return 1

    rows = []
    for tag in VARIANT_ORDER:
        run_dir = found.get(tag)
        if run_dir is None:
            rows.append({"tag": tag, "missing": True})
            continue
        summary = load_summary(run_dir)
        if summary is None:
            rows.append({"tag": tag, "run_dir": run_dir, "missing": True})
            continue
        cat = summary.get("next_category", {})
        reg = summary.get("next_region", {})
        rows.append({
            "tag": tag,
            "run_dir": run_dir,
            "cat_f1_mean": cat.get("f1", {}).get("mean"),
            "cat_f1_std":  cat.get("f1", {}).get("std"),
            "reg_top10_mean": reg.get("top10_acc_indist", {}).get("mean"),
            "reg_top10_std":  reg.get("top10_acc_indist", {}).get("std"),
        })

    lines = [
        "# FL H3-alt — perf-variant comparison",
        "",
        f"_Generated from `{args.results_dir}`_",
        "",
        "Reference: F48-H3-alt FL 5f × 50ep, seed 42, "
        f"cat F1 {NORTH_STAR_FL['cat_f1']['mean']:.2f} ± "
        f"{NORTH_STAR_FL['cat_f1']['std']:.2f}, "
        f"reg Acc@10_indist {NORTH_STAR_FL['reg_top10_indist']['mean']:.2f} ± "
        f"{NORTH_STAR_FL['reg_top10_indist']['std']:.2f} "
        "(from `docs/NORTH_STAR.md`).",
        "",
        "Equivalence marker: ✓ ≤ 1σ from NORTH_STAR mean | ~ ≤ 2σ | ✗ > 2σ.",
        "",
        "| Variant | Cat F1 (5f) | Δ vs NORTH_STAR | Reg Acc@10 indist (5f) | Δ vs NORTH_STAR | Run dir |",
        "|---|---:|---:|---:|---:|---|",
    ]
    for row in rows:
        if row.get("missing"):
            lines.append(f"| **{row['tag']}** | — | — | — | — | _missing_ |")
            continue
        cat_f1 = fmt_pct(row.get("cat_f1_mean"), row.get("cat_f1_std"))
        reg_top10 = fmt_pct(row.get("reg_top10_mean"), row.get("reg_top10_std"))
        cat_delta = fmt_delta(row.get("cat_f1_mean"), NORTH_STAR_FL["cat_f1"])
        reg_delta = fmt_delta(row.get("reg_top10_mean"), NORTH_STAR_FL["reg_top10_indist"])
        run_dir_short = row["run_dir"].name
        lines.append(
            f"| **{row['tag']}** | {cat_f1} | {cat_delta} | {reg_top10} | {reg_delta} | `{run_dir_short}` |"
        )

    lines += [
        "",
        "## Verdict template",
        "",
        "Both perf variants count as a publishable \"preview mode\" iff Δ ≤ 1σ on "
        "BOTH metrics for that variant. If a variant lands in 1–2σ band, it is "
        "exploratory only. > 2σ → quality is hurt; do not use.",
        "",
    ]
    args.output.write_text("\n".join(lines))
    print(args.output.read_text())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
