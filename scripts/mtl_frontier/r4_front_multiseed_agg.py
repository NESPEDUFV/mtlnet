#!/usr/bin/env python3
"""R4 weight-front, multi-seed {0,1,7,100} at the 3 core weights {0.55, 0.75, 0.85}.

Sources (champion is bit-deterministic → reuse is safe, audit-confirmed):
  cw 0.55/0.85 : seed0 from r4_scalar_front_manifest.tsv + seeds{1,7,100} from
                 r4_front_multiseed_manifest.tsv
  cw 0.75      : champion G = the `base` rows of ccplus_fl_multiseed_manifest.tsv {0,1,7,100}
Reports per-weight 4-seed diagnostic-best (cat-F1 ceiling, reg-Acc@10 ceiling) mean±std →
the near-corner test (is the reg ceiling flat as cw drops below 0.75 while cat falls?).
Plus the champion epoch-trajectory Pareto front at each seed → C21-locus stability.
"""
import csv, glob, json, math, statistics as st
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]


def per_epoch(rd):
    rd = REPO / rd
    cat_f, reg_f = [], []
    for f in sorted(glob.glob(str(rd / "metrics/fold*_next_category_val.csv"))):
        cat_f.append([float(r["f1"]) * 100 for r in csv.DictReader(open(f))])
    for f in sorted(glob.glob(str(rd / "metrics/fold*_next_region_val.csv"))):
        reg_f.append([float(r["top10_acc_indist"]) * (1 - float(r["ood_fraction"])) * 100
                      for r in csv.DictReader(open(f))])
    n = min(min(len(x) for x in cat_f), min(len(x) for x in reg_f))
    cat = [st.mean(fold[e] for fold in cat_f) for e in range(n)]
    reg = [st.mean(fold[e] for fold in reg_f) for e in range(n)]
    return cat, reg


def diagbest(rd):
    cat, reg = per_epoch(rd)
    return max(cat), max(reg)


def epoch_front(rd):
    cat, reg = per_epoch(rd)
    pts = list(zip(cat, reg))
    par = [i for i, (ci, ri) in enumerate(pts)
           if not any((cj >= ci and rj >= ri) and (cj > ci or rj > ri)
                      for j, (cj, rj) in enumerate(pts) if j != i)]
    e = max(range(len(cat)), key=lambda i: math.sqrt(max(cat[i], 0) * max(reg[i], 0)))
    return len(par), e + 1, round(cat[e], 3), round(reg[e], 3)


def read_man(name):
    rows = []
    for line in (REPO / "scripts/mtl_frontier" / name).read_text().splitlines():
        rows.append(line.split("\t"))
    return rows


# assemble {weight: {seed: rundir}}
W = {0.55: {}, 0.75: {}, 0.85: {}}
for p in read_man("r4_scalar_front_manifest.tsv"):       # tag state cw rd  (seed0)
    if len(p) >= 4 and float(p[2]) in W:
        W[float(p[2])][0] = p[3]
for p in read_man("r4_front_multiseed_manifest.tsv"):    # tag state seed rd
    if len(p) >= 4:
        cw = float(p[0].replace("cw", ""))
        if cw in W:
            W[cw][int(p[2])] = p[3]
for p in read_man("ccplus_fl_multiseed_manifest.tsv"):   # tag state seed rd  (base = champion cw0.75)
    if len(p) >= 4 and p[0] == "base":
        W[0.75][int(p[2])] = p[3]

SEEDS = [0, 1, 7, 100]
out = {"comparand": "frozen champion G weight-front, FL multi-seed {0,1,7,100}", "weights": {}}
for cw in sorted(W):
    cats, regs = [], []
    for s in SEEDS:
        rd = W[cw].get(s)
        if not rd:
            continue
        c, r = diagbest(rd)
        cats.append(c); regs.append(r)
    if not cats:
        continue
    out["weights"][cw] = {
        "n_seeds": len(cats),
        "cat_diagbest_mean": round(st.mean(cats), 3), "cat_diagbest_std": round(st.pstdev(cats), 3),
        "reg_diagbest_mean": round(st.mean(regs), 3), "reg_diagbest_std": round(st.pstdev(regs), 3),
    }

# near-corner test: reg ceiling change 0.55→0.75 vs cat ceiling change
ws = out["weights"]
verdict = {}
if 0.55 in ws and 0.75 in ws and 0.85 in ws:
    verdict["reg_gain_lowering_to_0.55"] = round(ws[0.55]["reg_diagbest_mean"] - ws[0.75]["reg_diagbest_mean"], 3)
    verdict["cat_cost_lowering_to_0.55"] = round(ws[0.55]["cat_diagbest_mean"] - ws[0.75]["cat_diagbest_mean"], 3)
    verdict["reg_change_raising_to_0.85"] = round(ws[0.85]["reg_diagbest_mean"] - ws[0.75]["reg_diagbest_mean"], 3)
    verdict["cat_change_raising_to_0.85"] = round(ws[0.85]["cat_diagbest_mean"] - ws[0.75]["cat_diagbest_mean"], 3)
    verdict["near_corner"] = abs(verdict["reg_gain_lowering_to_0.55"]) < 0.5  # reg ceiling ~flat below champion
out["near_corner_test"] = verdict

# champion epoch-front stability across seeds
champ_ef = {}
for s in SEEDS:
    rd = W[0.75].get(s)
    if rd:
        n_par, gs_ep, gc, gr = epoch_front(rd)
        champ_ef[s] = {"n_pareto_epochs": n_par, "geomsimple_epoch": gs_ep, "geomsimple_point": [gc, gr]}
out["champion_epoch_front_by_seed"] = champ_ef

outp = REPO / "docs/results/mtl_frontier/r4_front_multiseed_results.json"
outp.write_text(json.dumps(out, indent=2) + "\n")
print("=== R4 WEIGHT-FRONT, multi-seed {0,1,7,100} (diagnostic-best ceilings) ===")
print(f"{'cw':>5} | {'cat-F1 (mean±std)':>20} | {'reg-Acc@10 (mean±std)':>22} | n")
for cw in sorted(ws):
    v = ws[cw]
    print(f"{cw:>5} | {v['cat_diagbest_mean']:>8} ± {v['cat_diagbest_std']:<8} | "
          f"{v['reg_diagbest_mean']:>10} ± {v['reg_diagbest_std']:<8} | {v['n_seeds']}")
if verdict:
    print(f"\n  lowering cw 0.75→0.55:  reg {verdict['reg_gain_lowering_to_0.55']:+.3f}pp  "
          f"cat {verdict['cat_cost_lowering_to_0.55']:+.3f}pp")
    print(f"  raising cw 0.75→0.85:   reg {verdict['reg_change_raising_to_0.85']:+.3f}pp  "
          f"cat {verdict['cat_change_raising_to_0.85']:+.3f}pp")
    print(f"  NEAR-CORNER (reg ceiling flat below champion, |Δreg|<0.5): {verdict['near_corner']}")
print("\n  champion (cw=0.75) epoch-front by seed:")
for s, e in champ_ef.items():
    print(f"    seed{s}: {e['n_pareto_epochs']} Pareto epochs, geom_simple ep{e['geomsimple_epoch']} @ {e['geomsimple_point']}")
print(f"WROTE {outp}")
