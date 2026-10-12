"""closing_data C1 (confirm-on-G) — aggregate route_task_best JSONs into the
G0.2 gate verdict.

Per (state, seed, fold) the routing JSON gives, for each of the 3 snapshots:
reg Acc@10 (top10_acc) and cat F1. The deploy panel routes EACH task to its own
best snapshot vs the single shipped joint (geom_simple) checkpoint:

    Δreg = reg_best.reg_top10_acc - joint.reg_top10_acc   (route reg to reg-best)
    Δcat = cat_best.cat_f1        - joint.cat_f1           (route cat to cat-best)

Gate (G0.2): PROMOTE iff mean Δreg >= +0.3 pp AND cat not hurt (mean Δcat >= 0),
multi-seed, paired-Wilcoxon-supported. Else NULL (recovery already captured by
C25-fix + dual-tower + geom_simple).

Usage:
    python scripts/closing_data/c1_aggregate.py 'results/check2hgi_design_k_resln_mae_l0_1/*/mtlnet_*ep50_*/c1_route/route_fold*.json'
    # or pass explicit files / dirs
"""
from __future__ import annotations

import glob
import json
import sys
from pathlib import Path

try:
    from scipy.stats import wilcoxon
except Exception:  # pragma: no cover
    wilcoxon = None

GATE_PP = 0.30  # promote threshold on reg, in percentage points


def _collect(args: list[str]) -> list[Path]:
    files: list[Path] = []
    for a in args:
        p = Path(a)
        if p.is_dir():
            files += [Path(x) for x in glob.glob(str(p / "**" / "route_fold*.json"), recursive=True)]
        elif any(ch in a for ch in "*?["):
            files += [Path(x) for x in glob.glob(a, recursive=True)]
        elif p.is_file():
            files.append(p)
    return sorted(set(files))


def _seed_from_path(p: Path) -> str:
    # seed is encoded in a path component: either "...seed<N>..." (rundir) or
    # the "c1_route_s<N>" / "c1_snap_s<N>" dir this driver writes — best effort.
    for part in p.parts:
        for marker in ("seed", "_s"):
            if marker in part:
                frag = part.split(marker)[-1]
                num = "".join(c for c in frag if c.isdigit())
                if num:
                    return num
    return "?"


def main(argv: list[str]) -> None:
    if not argv:
        print(__doc__)
        sys.exit(2)
    files = _collect(argv)
    if not files:
        print("no route_fold*.json found for:", argv, file=sys.stderr)
        sys.exit(2)

    rows = []  # (state, seed, fold, dreg_pp, dcat_pp)
    for f in files:
        d = json.loads(f.read_text())
        s = d.get("summary", {})
        state = d.get("state", "?")
        seed = _seed_from_path(f)
        fold = d.get("fold", "?")
        dreg = (s["reg_routed_top10_acc"] - s["joint_reg_top10_acc"]) * 100.0
        dcat = (s["cat_routed_f1"] - s["joint_cat_f1"]) * 100.0
        rows.append((state, seed, fold, dreg, dcat))

    by_state: dict[str, list] = {}
    for r in rows:
        by_state.setdefault(r[0], []).append(r)

    print(f"\nC1 confirm-on-G — per-task-best routing vs single geom_simple checkpoint")
    print(f"gate: PROMOTE iff mean Δreg >= +{GATE_PP:.2f} pp AND mean Δcat >= 0\n")

    overall_dreg, overall_dcat = [], []
    for state, rs in sorted(by_state.items()):
        rs.sort(key=lambda x: (x[1], x[2]))
        print(f"=== {state} (n={len(rs)} fold×seed) ===")
        print(f"  {'seed':>5} {'fold':>5} {'Δreg pp':>9} {'Δcat pp':>9}")
        for (_, seed, fold, dreg, dcat) in rs:
            print(f"  {seed:>5} {str(fold):>5} {dreg:>9.3f} {dcat:>9.3f}")
        dregs = [r[3] for r in rs]
        dcats = [r[4] for r in rs]
        overall_dreg += dregs
        overall_dcat += dcats
        mreg = sum(dregs) / len(dregs)
        mcat = sum(dcats) / len(dcats)
        line = f"  MEAN  Δreg={mreg:+.3f} pp  Δcat={mcat:+.3f} pp"
        if wilcoxon is not None and len(dregs) >= 5 and any(abs(x) > 1e-9 for x in dregs):
            try:
                wr = wilcoxon(dregs)
                wc = wilcoxon(dcats) if any(abs(x) > 1e-9 for x in dcats) else None
                line += f"  | Wilcoxon reg p={wr.pvalue:.4f}"
                if wc is not None:
                    line += f", cat p={wc.pvalue:.4f}"
            except Exception as e:
                line += f"  (wilcoxon failed: {e})"
        print(line)
        verdict = "PROMOTE" if (mreg >= GATE_PP and mcat >= 0) else "NULL"
        print(f"  >>> {state}: {verdict}\n")

    if len(by_state) > 1:
        mreg = sum(overall_dreg) / len(overall_dreg)
        mcat = sum(overall_dcat) / len(overall_dcat)
        print(f"=== POOLED (n={len(overall_dreg)}) ===")
        print(f"  MEAN  Δreg={mreg:+.3f} pp  Δcat={mcat:+.3f} pp")
        verdict = "PROMOTE" if (mreg >= GATE_PP and mcat >= 0) else "NULL"
        print(f"  >>> POOLED: {verdict}")


if __name__ == "__main__":
    main(sys.argv[1:])
