#!/usr/bin/env python3
"""R0 / T6.0 — multi-state matched-metric G-ceiling bar (FREE, zero retrain).

The reg "beats the ceiling" verb was matched-metric-verified at FL ONLY (B-A2):
G's reported reg was ``top10_acc_indist`` while the (c) p1 ceiling is the FULL
``top10_acc``. This re-scores the EXISTING G runs onto the FULL metric so every
reopened Tier-3/4/5 probe can be measured against a real bar at AL/AZ/GE too.

Method (validated vs B-A2's independent route_task_best at FL: 72.95 vs 72.93):
  full_top10 = indist_top10 * (1 - ood_fraction)            [per fold]
OOD samples (target never seen in train) almost never land in the full-metric top-10
(an OOD class index CAN be hit by chance, but B-A2 confirmed the OOD-hit rate ≈ 0 at
FL: 72.95 converted vs 72.93 independent, ~0.02pp). So the relation is empirically
near-exact, VALIDATED AT FL; at AL/AZ/GE it is validated-by-analogy (any residual
OOD-hit would make true G-full HIGHER, shrinking the deficit → "matches" is robust to
it, error is in G's favour). ``ood_fraction`` is split-
determined and epoch-invariant per fold, so G's full-best epoch == its
indist-best epoch -> G-full at the indist-best epoch IS G-full-best. The (c)
ceiling (p1 JSON) is already the FULL top10_acc at its own top10-best epoch.

Reads rundirs from the committed manifests; nothing is retrained.
"""
import csv
import glob
import json
import statistics as st
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
V14 = "check2hgi_design_k_resln_mae_l0_1"
SEEDS = [0, 1, 7, 100]
STATES = ["alabama", "arizona", "georgia", "florida"]


def read_manifest(name):
    """key -> rundir from a <key>\t<label>\t<rundir> manifest."""
    out = {}
    p = REPO / "scripts/mtl_improvement" / name
    if not p.exists():
        return out
    for line in p.read_text().splitlines():
        parts = line.split("\t")
        if len(parts) >= 3:
            out[parts[0]] = parts[2]
    return out


# ---- assemble the G rundir map: {state: {seed: rundir}} -------------------
def g_rundirs():
    ms = read_manifest("c25_g_multistate_manifest.tsv")   # AL/AZ/GE s1/s7/s100
    gv2 = read_manifest("c25_gv2_manifest.tsv")           # AL/AZ/GE s0
    promote = read_manifest("c25_combos_promote_manifest.tsv")  # FL s1/s7/s100
    screen = read_manifest("c25_combos_screen_manifest.tsv")    # FL s0
    abbr = {"alabama": "AL", "arizona": "AZ", "georgia": "GE"}
    m = {s: {} for s in STATES}
    for stf in ("alabama", "arizona", "georgia"):
        m[stf][0] = gv2[f"g_{abbr[stf]}|s0"]
        for sd in (1, 7, 100):
            m[stf][sd] = ms[f"g_{stf}|s{sd}"]
    m["florida"][0] = screen["dual_aux_off|s0"]
    for sd in (1, 7, 100):
        m["florida"][sd] = promote[f"dual_aux_off|s{sd}"]
    return m


def g_reg_full_per_fold(rundir):
    """Per-fold G-full top10 at the indist-best epoch."""
    folds = []
    for f in sorted(glob.glob(str(REPO / rundir / "metrics/fold*_next_region_val.csv"))):
        rows = list(csv.DictReader(open(f)))
        best = max(rows, key=lambda r: float(r["top10_acc_indist"]))
        ind = float(best["top10_acc_indist"])
        ood = float(best["ood_fraction"])
        folds.append(ind * (1 - ood) * 100)
    return folds


def g_reg_indist_per_fold(rundir):
    folds = []
    for f in sorted(glob.glob(str(REPO / rundir / "metrics/fold*_next_region_val.csv"))):
        rows = list(csv.DictReader(open(f)))
        best = max(rows, key=lambda r: float(r["top10_acc_indist"]))
        folds.append(float(best["top10_acc_indist"]) * 100)
    return folds


def g_cat_f1(rundir):
    d = json.load(open(REPO / rundir / "summary/full_summary.json"))
    return d["diagnostic_task_best"]["next_category"]["f1"]["mean"] * 100


# ---- ceilings from the T2V.1 manifest ------------------------------------
def ceil_reg(engine, state, seed):
    """(c)/(d) reg ceiling = full top10_acc at top10-best epoch (p1 JSON)."""
    cm = read_manifest("t2v1_ceilings_manifest.tsv")
    key = f"creg|{engine}|{state}|s{seed}"
    if key not in cm:
        return None
    d = json.load(open(REPO / cm[key]))
    head = next(iter(d["heads"].values()))
    return head["aggregate"]["top10_acc_mean"] * 100


def ceil_cat(state, seed):
    cm = read_manifest("t2v1_ceilings_manifest.tsv")
    key = f"ccat|{state}|s{seed}"
    if key not in cm:
        return None
    rd = cm[key]
    d = json.load(open(REPO / rd / "summary/full_summary.json"))
    # STL `next` run: cat F1 at f1-best epoch (per_metric_best.next)
    nc = d["per_metric_best"]["next"]
    return nc["f1"]["mean"] * 100


def agg(per_seed):
    """mean and std over per-seed means (matches how G was reported)."""
    return st.mean(per_seed), (st.pstdev(per_seed) if len(per_seed) > 1 else 0.0)


def main():
    gm = g_rundirs()
    out = {"method": "full=indist*(1-ood_frac); validated vs B-A2 FL 72.93",
           "seeds": SEEDS, "states": {}}
    print(f"{'state':9} | {'G-full reg':>16} | {'(c) reg ceil':>14} | "
          f"{'Δreg matched':>13} | {'G-indist(xref)':>14} | {'G cat':>11} | "
          f"{'(c) cat':>9} | {'Δcat':>7}")
    print("-" * 120)
    for stf in STATES:
        gfull_seed, gind_seed, gcat_seed = [], [], []
        creg_seed, ccat_seed = [], []
        per_fold_dump = {}
        for sd in SEEDS:
            rd = gm[stf][sd]
            ff = g_reg_full_per_fold(rd)
            gfull_seed.append(st.mean(ff))
            gind_seed.append(st.mean(g_reg_indist_per_fold(rd)))
            gcat_seed.append(g_cat_f1(rd))
            per_fold_dump[sd] = {"g_full_folds": [round(x, 3) for x in ff]}
            cr = ceil_reg(V14, stf, sd)
            if cr is not None:
                creg_seed.append(cr)
            cc = ceil_cat(stf, sd)
            if cc is not None:
                ccat_seed.append(cc)
        gfull_m, gfull_s = agg(gfull_seed)
        gind_m, _ = agg(gind_seed)
        gcat_m, gcat_s = agg(gcat_seed)
        creg_m, creg_s = agg(creg_seed) if creg_seed else (float("nan"), 0)
        ccat_m, ccat_s = agg(ccat_seed) if ccat_seed else (float("nan"), 0)
        dreg = gfull_m - creg_m
        dcat = gcat_m - ccat_m
        print(f"{stf:9} | {gfull_m:7.2f} ± {gfull_s:4.2f} | "
              f"{creg_m:6.2f} ± {creg_s:4.2f} | {dreg:+12.2f} | "
              f"{gind_m:14.2f} | {gcat_m:6.2f}±{gcat_s:4.2f} | "
              f"{ccat_m:8.2f} | {dcat:+6.2f}")
        out["states"][stf] = {
            "g_reg_full_mean": round(gfull_m, 3), "g_reg_full_std": round(gfull_s, 3),
            "g_reg_full_per_seed": [round(x, 3) for x in gfull_seed],
            "g_reg_indist_mean": round(gind_m, 3),
            "c_reg_ceiling_full_mean": round(creg_m, 3), "c_reg_ceiling_full_std": round(creg_s, 3),
            "c_reg_ceiling_per_seed": [round(x, 3) for x in creg_seed],
            "delta_reg_matched": round(dreg, 3),
            "g_cat_f1_mean": round(gcat_m, 3), "g_cat_f1_std": round(gcat_s, 3),
            "c_cat_ceiling_mean": round(ccat_m, 3),
            "delta_cat": round(dcat, 3),
            "per_fold": per_fold_dump,
            "g_rundirs": {sd: gm[stf][sd] for sd in SEEDS},
        }
    # (d) FL composite (HGI-alpha0) for the FL "ties/beats composite" framing
    dcomp = []
    for sd in SEEDS:
        v = ceil_reg("hgi", "florida", sd)
        if v is not None:
            dcomp.append(v)
    if dcomp:
        dm, ds = agg(dcomp)
        out["states"]["florida"]["d_composite_reg_full_mean"] = round(dm, 3)
        out["states"]["florida"]["delta_reg_vs_composite"] = round(
            out["states"]["florida"]["g_reg_full_mean"] - dm, 3)
        print(f"\n(d) FL composite reg full = {dm:.2f} ± {ds:.2f}  | "
              f"G-full − composite = {out['states']['florida']['g_reg_full_mean'] - dm:+.2f}")

    outp = REPO / "docs/results/mtl_improvement/R0_matched_metric_bar.json"
    outp.write_text(json.dumps(out, indent=2))
    print(f"\nwrote {outp}")


if __name__ == "__main__":
    main()
