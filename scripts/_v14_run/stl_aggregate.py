#!/usr/bin/env python
"""Aggregate the STL verification sweep (next-cat macro-F1, next-reg Acc@10) for v11/v14/HGI at FL."""
import json, csv
from pathlib import Path
from statistics import mean, pstdev

REPO = Path("/home/vitor.oliveira/PoiMtlNet")
MAN = REPO / "scripts/_v14_run/stl_manifest.tsv"
NAMES = {"check2hgi": "v11 (canonical)", "check2hgi_design_k_resln_mae_l0_1": "v14", "hgi": "HGI"}
# prior-study targets
TGT_CAT = {"check2hgi": 67.32, "check2hgi_design_k_resln_mae_l0_1": 67.36, "hgi": 34.29}
TGT_REG = {"check2hgi": 0.6943, "check2hgi_design_k_resln_mae_l0_1": 0.7024, "hgi": 0.7060}

cat, reg = {}, {}
if MAN.exists():
    for row in csv.reader(open(MAN), delimiter="\t"):
        if len(row) < 4 or not row[3]:
            continue
        task, eng, seed, art = row
        try:
            if task == "cat":
                j = json.load(open(Path(art) / "summary" / "full_summary.json"))
                cat.setdefault(eng, []).append(j["next"]["f1"]["mean"] * 100)
            elif task == "reg":
                # p1 writes to docs/results/P1/region_head_<state>_region_5f_50ep_<eng>_s<seed>.json
                jp = REPO / f"docs/results/P1/region_head_florida_region_5f_50ep_{eng}_s{seed}.json"
                j = json.load(open(jp))
                v = j["heads"]["next_stan_flow"]["aggregate"]["top10_acc_mean"]
                reg.setdefault(eng, []).append(v * 100)
        except Exception as e:
            print(f"  ! skip {task} {eng} s{seed}: {e}")

def line(d, eng, tgt, pct=False):
    xs = d.get(eng, [])
    if not xs:
        return "pending"
    m, s = mean(xs), (pstdev(xs) if len(xs) > 1 else 0.0)
    t = tgt[eng] * (100 if pct else 1)
    return f"{m:.2f}±{s:.2f}  (n={len(xs)}; prior {t:.2f}; Δ {m-t:+.2f})"

print("\n=== STL verification @ FL, seeds {0,1,7,100} ===")
print("\n-- next-cat macro-F1 --")
for e in ["check2hgi", "check2hgi_design_k_resln_mae_l0_1", "hgi"]:
    print(f"  {NAMES[e]:16}: {line(cat, e, TGT_CAT)}")
print("\n-- next-reg Acc@10 (%) --")
for e in ["check2hgi", "check2hgi_design_k_resln_mae_l0_1", "hgi"]:
    print(f"  {NAMES[e]:16}: {line(reg, e, TGT_REG, pct=True)}")
print()
