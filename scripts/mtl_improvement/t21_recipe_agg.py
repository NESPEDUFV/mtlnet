#!/usr/bin/env python
"""Assemble the recipe×state matrix for the baseline head (next_getnext_hard).

Cells (reg@10 disjoint / cat-F1 deploy), seed42 5f×50ep unless noted:
  onecycle: AL/AZ/FL = base_a (ladder/harden manifests); CA/TX = rmatrix 'onecyc'
  B9:       AL/AZ/CA/TX = rmatrix 'b9';  FL = LANDED multi-seed (61.28/70.26)
  H3-alt:   FL = rmatrix 'h3alt';  AL/AZ = LANDED multi-seed (47.23/38.27 ; 46.78/48.75)

  PYTHONPATH=src .venv/bin/python scripts/mtl_improvement/t21_recipe_agg.py
"""
import json, re
from pathlib import Path

STATES = ["alabama", "arizona", "florida", "california", "texas"]
LANDED = {  # (a) multi-seed {0,1,7,100}: reg_disj, cat_disj
    ("H3ALT", "alabama"): (47.23, 46.78), ("H3ALT", "arizona"): (38.27, 48.75),
    ("B9", "florida"): (61.28, 70.26),
}


def _m(rd):
    s = json.load(open(Path(rd) / "summary" / "full_summary.json"))
    return (round(s["per_metric_best"]["next_region"]["top10_acc_indist"]["mean"] * 100, 2),
            round(s["next_category"]["f1"]["mean"] * 100, 2))


def _load(mf):
    out = {}
    p = Path("scripts/mtl_improvement") / mf
    if not p.exists():
        return out
    for line in p.read_text().splitlines():
        parts = line.split("\t")
        if len(parts) < 3:
            continue
        tag, rd = parts[1], parts[2]
        st = re.search(r"/(alabama|arizona|florida|california|texas)/", rd)
        if not st:
            continue
        try:
            out[(tag, st.group(1))] = _m(rd)
        except Exception:
            pass
    return out


def main():
    rm = _load("t21_rmatrix_manifest.tsv")
    # onecycle@AL/AZ/FL = base_a from ladder/harden
    base = {}
    for mf in ["t21_ladder_manifest.tsv", "t21_harden_manifest.tsv"]:
        for k, v in _load(mf).items():
            if k[0] == "base_a":
                base[k[1]] = v

    cell = {}  # (recipe, state) -> (reg, cat, source)
    for st in STATES:
        # onecycle
        if st in ("alabama", "arizona", "florida") and st in base:
            cell[("ONECYCLE", st)] = (*base[st], "base_a")
        if ("onecyc", st) in rm:
            cell[("ONECYCLE", st)] = (*rm[("onecyc", st)], "rmatrix")
        # B9
        if ("b9", st) in rm:
            cell[("B9", st)] = (*rm[("b9", st)], "rmatrix")
        elif ("B9", st) in LANDED:
            cell[("B9", st)] = (*LANDED[("B9", st)], "landed-ms")
        # H3-alt
        if ("h3alt", st) in rm:
            cell[("H3ALT", st)] = (*rm[("h3alt", st)], "rmatrix")
        elif ("H3ALT", st) in LANDED:
            cell[("H3ALT", st)] = (*LANDED[("H3ALT", st)], "landed-ms")

    print("\n=== RECIPE × STATE MATRIX — baseline head reg@10 disjoint (cat-F1) ===")
    print(f"  {'recipe':<10}" + "".join(f"{s[:2].upper():>16}" for s in STATES))
    for rec in ["H3ALT", "ONECYCLE", "B9"]:
        row = f"  {rec:<10}"
        for st in STATES:
            c = cell.get((rec, st))
            row += (f"{c[0]:>7.2f}({c[1]:>5.2f})" if c else f"{'—':>16}")
        print(row)
    print("\n  source per cell:")
    for rec in ["H3ALT", "ONECYCLE", "B9"]:
        for st in STATES:
            c = cell.get((rec, st))
            if c:
                print(f"    {rec:<9} {st:<11} reg={c[0]:6.2f} cat={c[1]:6.2f}  [{c[2]}]")


if __name__ == "__main__":
    main()
