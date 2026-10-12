#!/usr/bin/env python
"""Aggregate v14 + matched-canonical MTL sweeps on TWO bases:
  - DIAG  = per-task diagnostic-best epoch (region's own best / category's own best) — the §0.1 convention.
  - JOINT = the single joint_score-selected checkpoint (one deployed model serving both tasks).
Primary comparison = matched canonical (same harness/recipe/seeds). §0.1 v11 shown for reference."""
import json, csv, glob, statistics as st
from pathlib import Path
from statistics import mean, pstdev

REPO = Path("/home/vitor.oliveira/PoiMtlNet")
RUN = REPO / "scripts/_v14_run"
S01 = {"alabama": (50.17, 40.57), "arizona": (40.78, 45.10), "florida": (63.27, 68.56)}
STATES = ["florida", "alabama", "arizona"]

import csv as _csv
def _read_val_csv(path):
    rows = list(_csv.DictReader(open(path)))
    return rows

def _min_epoch_for(rd):
    # B9 (FL) used --min-best-epoch 5; H3-alt (AL/AZ) used 0. Detect by state in path.
    return 5 if "/florida/" in rd else 0

def metrics(rd):
    """Three bases, all % averaged over folds:
      diag_*   : per-task own-best epoch (selector-independent; §0.1 convention).
      joint_*  : v11 LEGACY selector (joint_score=0.5*(cat_f1+reg_f1)) — what primary_checkpoint used.
      jgeom_*  : CORRECTED selector (joint_geom_lift = sqrt(reg_lift*cat_lift); 2026-05-24 C21 fix).
                 argmax over epochs of (acc1_reg * acc1_cat) since per-fold majority baselines are
                 constants and don't change the argmax; min_best_epoch floor applied (FL=5, AL/AZ=0).
    """
    fis = sorted(glob.glob(str(Path(rd) / "folds" / "fold*_info.json")))
    dreg, dcat = [], []
    jgreg, jgcat = [], []
    me = _min_epoch_for(rd)
    for fi in fis:
        j = json.load(open(fi))
        db = j["diagnostic_best_epochs"]
        dreg.append(db["next_region"]["metrics"].get("top10_acc_indist", 0.0))
        dcat.append(db["next_category"]["metrics"].get("f1", 0.0))
        # corrected joint: recompute selected epoch from per-epoch val CSVs
        fold = fi.split("fold")[-1].split("_")[0]
        rcsv = _read_val_csv(Path(rd) / "metrics" / f"fold{fold}_next_region_val.csv")
        ccsv = _read_val_csv(Path(rd) / "metrics" / f"fold{fold}_next_category_val.csv")
        best_e, best_score = None, -1.0
        for rr, cc in zip(rcsv, ccsv):
            ep = int(rr["epoch"])            # CSV epoch is 1-indexed; 0-indexed = ep-1
            if (ep - 1) < me:
                continue
            # C21 geom_simple selector: argmax( cat_macroF1 * reg_Acc@10 )
            sc = float(cc["f1"]) * float(rr["top10_acc_indist"])
            if sc > best_score:
                best_score, best_e = sc, (rr, cc)
        if best_e is not None:
            jgreg.append(float(best_e[0]["top10_acc_indist"]))
            jgcat.append(float(best_e[1]["f1"]))
    # legacy joint (what shipped) — from summary aggregate of primary_checkpoint
    s = json.load(open(Path(rd) / "summary" / "full_summary.json"))
    out = {"diag_reg": st.mean(dreg)*100, "diag_cat": st.mean(dcat)*100,
           "joint_reg": s["next_region"]["top10_acc_indist"]["mean"]*100,
           "joint_cat": s["next_category"]["f1"]["mean"]*100}
    if jgreg:
        out["jgeom_reg"] = st.mean(jgreg)*100
        out["jgeom_cat"] = st.mean(jgcat)*100
    return out

def load(man):
    out = {}
    if not Path(man).exists(): return out
    for row in csv.reader(open(man), delimiter="\t"):
        if len(row) < 3 or not row[2]: continue
        st_, seed, rd = row
        try: m = metrics(rd)
        except Exception: continue
        d = out.setdefault(st_, {})
        for k in m: d.setdefault(k, []).append(m[k])
        d.setdefault("seeds", []).append(seed)
    return out

v14 = load(RUN / "manifest.tsv")
can = load(RUN / "canon_manifest.tsv")

def agg(d, st_, key):
    xs = d.get(st_, {}).get(key, [])
    if not xs: return None
    return mean(xs), (pstdev(xs) if len(xs) > 1 else 0.0)

def cell(d, st_, key):
    a = agg(d, st_, key)
    return f"{a[0]:5.2f}±{a[1]:4.2f}" if a else "   pending "

def delta(v, c, st_, key):
    av, ac = agg(v, st_, key), agg(c, st_, key)
    return f"{av[0]-ac[0]:+6.2f}" if (av and ac) else "  n/a "

for basis, rk, ck in [("DIAGNOSTIC-BEST (per-task own best epoch — §0.1 convention)", "diag_reg", "diag_cat"),
                      ("JOINT-GEOM-SIMPLE ✅ CORRECTED selector = sqrt(cat_F1 * reg_Acc@10), C21 — now CODE DEFAULT", "jgeom_reg", "jgeom_cat"),
                      ("JOINT-LEGACY ⚠ v11 broken selector (0.5*(cat_f1+reg_f1)) — what shipped", "joint_reg", "joint_cat")]:
    print("\n" + "=" * 110)
    print(f"v14 vs MATCHED canonical — {basis}  | KD OFF, seeds {{0,1,7,100}}")
    print("=" * 110)
    h = (f"{'state':9} {'n':>2} | {'v14 reg@10':>11} {'canon reg':>11} {'Δreg':>7} || "
         f"{'v14 catF1':>11} {'canon catF1':>11} {'Δcat':>7} | {'§0.1(reg/cat)':>14}")
    print(h); print("-" * len(h))
    for s in STATES:
        n = len(v14.get(s, {}).get("seeds", []))
        if n == 0: print(f"{s:9} {'-':>2} | (v14 pending)"); continue
        ref = f"{S01[s][0]:.1f}/{S01[s][1]:.1f}"
        print(f"{s:9} {n:>2} | {cell(v14,s,rk):>11} {cell(can,s,rk):>11} {delta(v14,can,s,rk):>7} || "
              f"{cell(v14,s,ck):>11} {cell(can,s,ck):>11} {delta(v14,can,s,ck):>7} | {ref:>14}")
print("=" * 110)
print("Reg=top10_acc_indist, Cat=macro-F1. Δ>0 ⇒ v14 beats matched canonical.")
print("DIAG = each task at its own best epoch (optimistic ceiling, what §0.1 reports).")
print("JOINT = one checkpoint chosen by joint_score (realistic single deployed model; reg sits below its peak).\n")
