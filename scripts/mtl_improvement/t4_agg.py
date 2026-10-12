#!/usr/bin/env python3
"""Aggregate the T4 full balancer screen (matched-metric, R0 method).

Reads scripts/mtl_improvement/t4_full_manifest.tsv (<arm|state>\t<arm>\t<rundir>),
computes reg-full = indist*(1-ood) at the indist-best epoch + cat F1 (diag-best) per
arm/state, and ranks Δ vs the G control (static_weight) and vs the R0 matched ceiling.
"""
import csv, glob, json, statistics as st, sys
from pathlib import Path
REPO = Path(__file__).resolve().parents[2]

# R0 matched (c) reg ceilings (full top10_acc, multi-seed) + cat ceilings
CEIL = {"alabama": (62.67, 50.35), "florida": (73.27, 69.96),
        "georgia": (58.44, 57.50), "arizona": (54.80, 50.39)}


def reg_full_cat(rd):
    folds = []
    for f in sorted(glob.glob(str(REPO / rd / "metrics/fold*_next_region_val.csv"))):
        rows = list(csv.DictReader(open(f)))
        b = max(rows, key=lambda r: float(r["top10_acc_indist"]))
        folds.append(float(b["top10_acc_indist"]) * (1 - float(b["ood_fraction"])) * 100)
    d = json.load(open(REPO / rd / "summary/full_summary.json"))
    cat = d["diagnostic_task_best"]["next_category"]["f1"]["mean"] * 100
    return (st.mean(folds) if folds else float("nan")), cat


def main():
    man = {}
    mp = REPO / "scripts/mtl_improvement/t4_full_manifest.tsv"
    for l in mp.read_text().splitlines():
        p = l.split("\t")
        if len(p) >= 3:
            man[p[0]] = (p[1], p[2])
    states = ["alabama", "florida"]
    rows = {}  # arm -> {state: (reg,cat)}
    for key, (arm, rd) in man.items():
        arm_, state = key.split("|")
        try:
            rows.setdefault(arm, {})[state] = reg_full_cat(rd)
        except Exception as e:
            rows.setdefault(arm, {})[state] = (float("nan"), float("nan"))
    for state in states:
        ctrl = rows.get("static_weight", {}).get(state)
        creg, ccat = CEIL[state]
        print(f"\n=== {state} (seed0) — G control static_weight={ctrl}; "
              f"(c) ceil reg {creg} / cat {ccat} ===")
        print(f"{'arm':24}{'reg-full':>10}{'ΔvsG':>8}{'Δvsceil':>9}{'cat':>9}{'Δcat_vsG':>10}")
        items = []
        for arm, sd in rows.items():
            if state in sd:
                items.append((arm, sd[state]))
        # sort by reg desc
        items.sort(key=lambda x: (-(x[1][0] if x[1][0] == x[1][0] else -1)))
        for arm, (reg, cat) in items:
            dvg = reg - ctrl[0] if ctrl else float("nan")
            dvc = reg - creg
            dcat = cat - ctrl[1] if ctrl else float("nan")
            star = " ★" if (dvg > 0.3 and dcat > -0.5) else ""
            print(f"{arm:24}{reg:10.2f}{dvg:+8.2f}{dvc:+9.2f}{cat:9.2f}{dcat:+10.2f}{star}")
    # dump JSON
    out = {state: {arm: {"reg_full": rows[arm][state][0], "cat": rows[arm][state][1]}
                   for arm in rows if state in rows[arm]} for state in states}
    (REPO / "docs/results/mtl_improvement/T4_full_screen.json").write_text(json.dumps(out, indent=2))
    print("\nwrote docs/results/mtl_improvement/T4_full_screen.json")


if __name__ == "__main__":
    main()
