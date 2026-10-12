"""HGI FL MTL TWO-FRONT analysis vs canonical c2hgi baseline (Tier B FL).

Reuses analyze_tier_b_fl._per_fold / _compare (byte-identical methodology):
  reg = top10_acc_indist, cat = f1; disjoint = per-head best-val epoch;
  joint = epoch maximising sqrt(cat_f1 * reg_top10_indist) over shared epochs.
  Wilcoxon one-sided HGI>canonical on RAW per-fold values.

Compares mtl_hgi vs mtl_canonical, and prints the three-way (canon / B / J / L / HGI)
disjoint+joint reg means for the cross-reference table.

Usage: .venv/bin/python scripts/substrate_protocol_cleanup/analyze_hgi_mtl_fl.py
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "scripts" / "substrate_protocol_cleanup"))
from analyze_tier_b_fl import _per_fold, _run_dir, _compare, _mean  # noqa: E402


def main():
    hgi_pf = _per_fold(_run_dir("mtl_hgi"))
    base_pf = _per_fold(_run_dir("mtl_canonical"))
    cmp = _compare(hgi_pf, base_pf)

    out = {
        "hgi_per_fold": hgi_pf,
        "canonical_per_fold": base_pf,
        "hgi_vs_canonical": cmp,
        "three_way_reg": {},
    }

    # three-way reg means (disjoint + joint) for cross-reference table
    cells = {
        "canonical": "mtl_canonical",
        "design_b": "mtl_design_b",
        "design_j": "mtl_design_j",
        "design_l": "mtl_design_l",
        "hgi": "mtl_hgi",
    }
    for name, tag in cells.items():
        try:
            pf = _per_fold(_run_dir(tag))
            out["three_way_reg"][name] = {
                "disjoint_reg_mean": _mean(pf["disjoint_reg"]),
                "joint_reg_mean": _mean(pf["joint_reg"]),
                "disjoint_cat_mean": _mean(pf["disjoint_cat"]),
                "joint_cat_mean": _mean(pf["joint_cat"]),
                "disjoint_reg_perfold": pf["disjoint_reg"],
                "joint_reg_perfold": pf["joint_reg"],
            }
        except FileNotFoundError:
            out["three_way_reg"][name] = {"status": "MISSING"}

    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
