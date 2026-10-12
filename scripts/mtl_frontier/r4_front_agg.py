#!/usr/bin/env python3
"""R4 scalarization Pareto front — frozen champion G, --category-weight sweep.

For each weight produces TWO (cat-F1, reg-Acc@10) points:
  - diagnostic-best  : per-task ceiling (best cat epoch, best reg epoch — the study's
                       lever metric; an optimistic envelope, epochs differ).
  - geom_simple      : the single DEPLOYABLE epoch, selected by argmax_e
                       sqrt(meanfold catf1_e · meanfold regmatched_e) — the C21 selector.
The geom_simple points across weights = the achievable deployable front (Pareto subset).
Also extracts the champion's (cw=0.75) per-EPOCH trajectory front (within-run cat↔reg
tension) + its geom_simple-selected epoch.

Verdict: cat-range & reg-range across the deployable front. Collapse (both small) =
tasks decoupled = publishable regime datum; spread = a real front (→ consider PaLoRA).
"""
import csv, glob, json, math, statistics as st
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
COLLAPSE_PP = 0.5  # if BOTH cat and reg span < this (pp) across the front → "collapsed"


def per_epoch(rd):
    """Return (cat_f1[e], reg_matched[e]) mean-over-folds arrays (×100), aligned by epoch."""
    rd = REPO / rd
    cat_by_fold, reg_by_fold = [], []
    for f in sorted(glob.glob(str(rd / "metrics/fold*_next_category_val.csv"))):
        rows = list(csv.DictReader(open(f)))
        cat_by_fold.append([float(r["f1"]) * 100 for r in rows])
    for f in sorted(glob.glob(str(rd / "metrics/fold*_next_region_val.csv"))):
        rows = list(csv.DictReader(open(f)))
        reg_by_fold.append([float(r["top10_acc_indist"]) * (1 - float(r["ood_fraction"])) * 100 for r in rows])
    n = min(min(len(x) for x in cat_by_fold), min(len(x) for x in reg_by_fold))
    cat = [st.mean(fold[e] for fold in cat_by_fold) for e in range(n)]
    reg = [st.mean(fold[e] for fold in reg_by_fold) for e in range(n)]
    return cat, reg


def points(rd):
    cat, reg = per_epoch(rd)
    cat_db = max(cat); reg_db = max(reg)                       # diagnostic-best (per-task ceiling)
    e = max(range(len(cat)), key=lambda i: math.sqrt(max(cat[i], 0) * max(reg[i], 0)))  # geom_simple
    return {"cat_diagbest": round(cat_db, 3), "reg_diagbest": round(reg_db, 3),
            "cat_geomsimple": round(cat[e], 3), "reg_geomsimple": round(reg[e], 3),
            "geomsimple_epoch": e + 1, "epoch_cat": cat, "epoch_reg": reg}


def pareto(pts):
    """Indices of non-dominated points (maximize both)."""
    keep = []
    for i, (ci, ri) in enumerate(pts):
        if not any((cj >= ci and rj >= ri) and (cj > ci or rj > ri) for j, (cj, rj) in enumerate(pts) if j != i):
            keep.append(i)
    return keep


man = []
for line in (REPO / "scripts/mtl_frontier/r4_scalar_front_manifest.tsv").read_text().splitlines():
    p = line.split("\t")
    if len(p) >= 4:
        man.append((float(p[2]), p[1], p[3]))  # (category_weight, state, rundir)
man.sort()

front, champ = [], None
for cw, state, rd in man:
    pt = points(rd)
    row = {"category_weight": cw, **{k: v for k, v in pt.items() if not k.startswith("epoch_")}}
    front.append(row)
    if abs(cw - 0.75) < 1e-9:
        champ = (rd, pt)

# deployable (geom_simple) front + Pareto subset
gs_pts = [(r["cat_geomsimple"], r["reg_geomsimple"]) for r in front]
par_idx = pareto(gs_pts)
cat_span = round(max(c for c, _ in gs_pts) - min(c for c, _ in gs_pts), 3)
reg_span = round(max(r for _, r in gs_pts) - min(r for _, r in gs_pts), 3)
collapsed = (cat_span < COLLAPSE_PP) and (reg_span < COLLAPSE_PP)

# champion epoch-trajectory Pareto front (within-run)
champ_epoch_front = None
if champ:
    cat, reg = champ[1]["epoch_cat"], champ[1]["epoch_reg"]
    epts = list(zip(cat, reg))
    ei = pareto(epts)
    champ_epoch_front = {"geomsimple_epoch": champ[1]["geomsimple_epoch"],
                         "geomsimple_point": [champ[1]["cat_geomsimple"], champ[1]["reg_geomsimple"]],
                         "pareto_epochs": [i + 1 for i in sorted(ei)],
                         "n_pareto_epochs": len(ei),
                         "cat_range": round(max(cat) - min(cat), 3),
                         "reg_range": round(max(reg) - min(reg), 3)}

out = {"comparand": "frozen champion G, --category-weight scalarization sweep (FL seed0)",
       "deployable_front_geomsimple": front,
       "pareto_optimal_weights": [front[i]["category_weight"] for i in sorted(par_idx)],
       "deployable_cat_span_pp": cat_span, "deployable_reg_span_pp": reg_span,
       "collapse_threshold_pp": COLLAPSE_PP, "front_collapsed_to_point": collapsed,
       "champion_epoch_front": champ_epoch_front}

outp = REPO / "docs/results/mtl_frontier/r4_scalar_front_results.json"
outp.write_text(json.dumps(out, indent=2) + "\n")

print("=== R4 SCALARIZATION FRONT (frozen champion G, --category-weight sweep, FL seed0) ===")
print(f"{'cw':>5} | {'cat_diagbest':>12} {'reg_diagbest':>12} | {'cat_deploy':>10} {'reg_deploy':>10} {'gs_ep':>5}")
for r in front:
    print(f"{r['category_weight']:>5} | {r['cat_diagbest']:>12} {r['reg_diagbest']:>12} | "
          f"{r['cat_geomsimple']:>10} {r['reg_geomsimple']:>10} {r['geomsimple_epoch']:>5}")
print(f"\n  deployable front spread:  cat {cat_span} pp,  reg {reg_span} pp")
print(f"  Pareto-optimal weights:   {out['pareto_optimal_weights']}")
print(f"  FRONT COLLAPSED TO POINT (both spans < {COLLAPSE_PP}pp): {collapsed}"
      f"  → {'tasks DECOUPLED (regime datum)' if collapsed else 'real front (consider PaLoRA)'}")
if champ_epoch_front:
    print(f"\n  champion (cw=0.75) epoch-trajectory front: {champ_epoch_front['n_pareto_epochs']} Pareto epochs "
          f"{champ_epoch_front['pareto_epochs']}; geom_simple picks ep{champ_epoch_front['geomsimple_epoch']} "
          f"@ {champ_epoch_front['geomsimple_point']}")
    print(f"  within-run epoch ranges: cat {champ_epoch_front['cat_range']}pp, reg {champ_epoch_front['reg_range']}pp")
print(f"WROTE {outp}")
