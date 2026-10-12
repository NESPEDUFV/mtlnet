#!/usr/bin/env python
"""T2.1 sharing dose-response — merge ladder + harden manifests into one table.

reg@10 disjoint (capacity) + cat-F1 per arm per state, Δ vs the matched base_a
zero-point, vs the (c) STL ceiling. Shows the monotonic sharing→reg relationship.

  PYTHONPATH=src .venv/bin/python scripts/mtl_improvement/t21_doseresp.py
"""
import json, re
from pathlib import Path

C = {"alabama": 62.88, "arizona": 55.11, "florida": 73.31}
MANIFESTS = ["t21_ladder_manifest.tsv", "t21_harden_manifest.tsv"]
ORDER = ["t22_crossstitch", "base_a", "t20_hardshare", "dt_gated_on", "dt_priv_on", "dt_priv_off"]
LBL = {
    "t22_crossstitch": "T2.2 CrossStitch (cross-talk)",
    "base_a": "base_a (cross-attn, most-shared)",
    "t20_hardshare": "T2.0 hard-share (mtlnet trunk)",
    "dt_gated_on": "T2.1 dual-tower gated",
    "dt_priv_on": "T2.1 dual private-only",
    "dt_priv_off": "T2.1 dual private-only prior-OFF",
}


def _metrics(rd):
    s = json.load(open(Path(rd) / "summary" / "full_summary.json"))
    return (round(s["per_metric_best"]["next_region"]["top10_acc_indist"]["mean"] * 100, 2),
            round(s["next_category"]["f1"]["mean"] * 100, 2))


def main():
    rows = {}
    for mf in MANIFESTS:
        p = Path("scripts/mtl_improvement") / mf
        if not p.exists():
            continue
        for line in p.read_text().splitlines():
            parts = line.split("\t")
            if len(parts) < 3:
                continue
            tag, rd = parts[1], parts[2]
            # only seed42 single-seed arms (skip multi-seed onecyc_val / s!=42)
            if "|s" in parts[0] and not parts[0].endswith("|s42"):
                continue
            m = re.search(r"/(alabama|arizona|florida)/", rd)
            if not m:
                continue
            try:
                rows.setdefault(m.group(1), {})[tag] = _metrics(rd)
            except Exception:
                pass
    for st in ["alabama", "arizona", "florida"]:
        print(f"\n### {st.upper()}   (c) STL reg ceiling = {C[st]}")
        r = rows.get(st, {})
        base = r.get("base_a", (None,))[0]
        print(f"  {'arm':<36}{'reg@10 disj':>12}{'cat-F1':>9}{'Δreg vs base':>14}{'vs (c)':>9}")
        for tag in ORDER:
            if tag in r:
                d, c = r[tag]
                dv = f"{d-base:+.2f}" if base else "?"
                print(f"  {LBL[tag]:<36}{d:>12.2f}{c:>9.2f}{dv:>14}{d-C[st]:>+9.2f}")


if __name__ == "__main__":
    main()
