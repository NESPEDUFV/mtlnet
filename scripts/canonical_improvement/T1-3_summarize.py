"""Summarize T1.3 α-sweep results into a Pareto table + ranking."""

import json
from pathlib import Path

import numpy as np

ROOT = Path("/home/vitor.oliveira/PoiMtlNet/docs/results/canonical_improvement")

# Canonical baseline (Stage B regen, B9full, same A40, seed 42)
CANONICAL = {
    "tag": "c04p03r03 (canonical)",
    "alpha": {"c2p": 0.4, "p2r": 0.3, "r2c": 0.3},
    "al": {"cat_f1_mean_pct": 40.22, "reg_top10_mean_pct": 50.04, "leak_probe": {"f1_mean_pct": 31.04}},
    "az": {"cat_f1_mean_pct": 45.80, "reg_top10_mean_pct": 40.98, "leak_probe": {"f1_mean_pct": 34.57}},
}


def main() -> None:
    rows = [CANONICAL]
    for p in sorted(ROOT.glob("T1-3_c*.json")):
        rows.append(json.loads(p.read_text()))

    # Header
    print(f"{'tag':<22} {'α (c,p,r)':<16} {'AL cat':>10} {'AL reg':>10} {'AL leak':>8}    {'AZ cat':>10} {'AZ reg':>10} {'AZ leak':>8}")
    print("-" * 110)
    for r in rows:
        a = r["alpha"]
        al = r["al"]
        az = r["az"]
        atxt = f"({a['c2p']:.1f},{a['p2r']:.1f},{a['r2c']:.1f})"
        al_leak = al.get("leak_probe", {}).get("f1_mean_pct", float("nan"))
        az_leak = az.get("leak_probe", {}).get("f1_mean_pct", float("nan"))
        print(f"{r['tag']:<22} {atxt:<16} "
              f"{al['cat_f1_mean_pct']:>10.2f} {al['reg_top10_mean_pct']:>10.2f} {al_leak:>8.2f}    "
              f"{az['cat_f1_mean_pct']:>10.2f} {az['reg_top10_mean_pct']:>10.2f} {az_leak:>8.2f}")

    # Pareto: dominates canonical iff cat ≥ + reg ≥ + (leak within +5pp) at BOTH states
    print()
    print("Pareto check vs canonical (must be ≥ on both heads at BOTH states, leak ≤ canonical+5pp):")
    can = CANONICAL
    for r in rows[1:]:
        winners = []
        for s in ("al", "az"):
            cat_d = r[s]["cat_f1_mean_pct"] - can[s]["cat_f1_mean_pct"]
            reg_d = r[s]["reg_top10_mean_pct"] - can[s]["reg_top10_mean_pct"]
            leak_d = r[s].get("leak_probe", {}).get("f1_mean_pct", float("nan")) - can[s]["leak_probe"]["f1_mean_pct"]
            winners.append((s, cat_d, reg_d, leak_d))
        ok_al = (winners[0][1] >= -0.5 and winners[0][2] >= -0.5 and winners[0][3] <= 5)
        ok_az = (winners[1][1] >= -0.5 and winners[1][2] >= -0.5 and winners[1][3] <= 5)
        strict_al = (winners[0][1] > 0 and winners[0][2] > 0)
        strict_az = (winners[1][1] > 0 and winners[1][2] > 0)
        verdict = "STRICT_DOM" if (strict_al and strict_az) else ("NON_INFERIOR" if (ok_al and ok_az) else "INFERIOR")
        print(f"  {r['tag']:<22} AL Δcat={winners[0][1]:+5.2f} Δreg={winners[0][2]:+5.2f} Δleak={winners[0][3]:+5.2f}    "
              f"AZ Δcat={winners[1][1]:+5.2f} Δreg={winners[1][2]:+5.2f} Δleak={winners[1][3]:+5.2f}    [{verdict}]")


if __name__ == "__main__":
    main()
