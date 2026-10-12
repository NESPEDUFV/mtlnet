"""tier_resln Design-J branch analysis — ResLN+Design J vs HGI / ResLN+Design B.

Pure re-analysis (no GPU). Mirrors analyze_resln.py extraction conventions so the
new ResLN+Design J numbers are directly comparable to ResLN+Design B.

STL reg (Acc@10 %): RAW per-fold top10_acc at each fold's OWN best epoch
  (per_metric_best.top10_acc.top10_acc). References (all leak-free P1, pf):
    - HGI            : region_head_<st>_..._hgi_reg_gethard_pf_5f50ep.json
    - canonical J    : region_head_<st>_..._design_j_reg_gethard_pf_5f50ep.json
    - ResLN+Design B : tier_resln/stl_reg/resln_design_b/<st>/seed42/*.json
    - ResLN+Design J : tier_resln/stl_reg/resln_design_j/<st>/seed42/*.json (new)
  Wilcoxon: RAW per-fold, paired by fold, one-sided (J family > / < ref).

STL cat (F1 %): RAW per-fold next_gru f1.
    - ResLN+Design J vs ResLN+Design B (both per-fold, paired Wilcoxon)
    - HGI cat: aggregate-only ref (P1_5b ..._hgi_5f_50ep_fair.json, AL/AZ only)

MTL (two fronts) vs canonical_noresln baseline: disjoint (own-best) + joint
  (geom_simple). Same per-fold val-CSV parse as analyze_resln.py.

Usage: .venv/bin/python scripts/substrate_protocol_cleanup/analyze_reslndj.py
"""
from __future__ import annotations

import json
import math
from pathlib import Path

import pandas as pd
from scipy.stats import wilcoxon

REPO = Path(__file__).resolve().parents[2]
TIER = REPO / "docs/results/substrate_protocol_cleanup/tier_resln"
P1 = REPO / "docs/results/P1"
P15B = REPO / "docs/results/P1_5b"
STATES = ("alabama", "arizona", "florida")
ST_UP = {"alabama": "ALABAMA", "arizona": "ARIZONA", "florida": "FLORIDA"}


def _mean(xs):
    return sum(xs) / len(xs) if xs else float("nan")


def _wilcox(a, b, alt="greater"):
    """One-sided paired Wilcoxon on per-fold deltas (a-b)."""
    deltas = [a[i] - b[i] for i in range(min(len(a), len(b)))]
    try:
        w = wilcoxon(deltas, alternative=alt)
        W, p = float(w.statistic), float(w.pvalue)
    except ValueError:
        W, p = float("nan"), float("nan")
    return deltas, _mean(deltas), W, p


# ---------------- STL reg ----------------

def _reg_pf_from_json(path: Path, head: str = "next_getnext_hard") -> list[float] | None:
    if path is None or not path.exists():
        return None
    j = json.loads(path.read_text())
    h = j["heads"].get(head) or next(iter(j["heads"].values()))
    out = []
    for pf in h["per_fold"]:
        out.append(float(pf["per_metric_best"]["top10_acc"]["top10_acc"]) * 100)
    return out


def _stl_reg_cell(variant: str, state: str) -> list[float] | None:
    cell = TIER / "stl_reg" / variant / state / "seed42"
    if not cell.exists():
        return None
    js = sorted(cell.glob("*.json"))
    return _reg_pf_from_json(js[0]) if js else None


def _p1_reg_ref(state: str, key: str) -> list[float] | None:
    fn = f"region_head_{state}_region_5f_50ep_STL_{ST_UP[state]}_{key}_reg_gethard_pf_5f50ep.json"
    return _reg_pf_from_json(P1 / fn)


# ---------------- STL cat ----------------

def _cat_pf_from_cell(variant: str, state: str) -> list[float] | None:
    cell = TIER / "stl_cat" / variant / state / "seed42"
    if not cell.exists():
        return None
    js = sorted(cell.glob("*.json"))
    if not js:
        return None
    j = json.loads(js[0].read_text())
    h = j["heads"].get("next_gru") or next(iter(j["heads"].values()))
    return [float(pf["f1"]) * 100 for pf in h["per_fold"]]


def _hgi_cat_agg(state: str) -> float | None:
    fn = P15B / f"next_category_{state}_hgi_5f_50ep_fair.json"
    if not fn.exists():
        return None
    return float(json.loads(fn.read_text())["next"]["f1"]["mean"]) * 100


# ---------------- MTL ----------------

def _mtl_run_dir(tag: str, state: str) -> Path | None:
    cell = TIER / tag / state / "seed42"
    if not cell.exists():
        return None
    cands = sorted(cell.glob("mtlnet_*"), key=lambda p: p.stat().st_mtime, reverse=True)
    return cands[0] if cands else None


def _mtl_per_fold(run_dir: Path) -> dict:
    out = {"disjoint_reg": [], "disjoint_cat": [], "joint_reg": [], "joint_cat": []}
    for fold in range(1, 6):
        cat_p = run_dir / "metrics" / f"fold{fold}_next_category_val.csv"
        reg_p = run_dir / "metrics" / f"fold{fold}_next_region_val.csv"
        if not cat_p.exists() or not reg_p.exists():
            return {}
        cat_df = pd.read_csv(cat_p)
        reg_df = pd.read_csv(reg_p)
        cat_by = {int(r.epoch): r for _, r in cat_df.iterrows()}
        reg_by = {int(r.epoch): r for _, r in reg_df.iterrows()}
        cb = max(cat_by, key=lambda e: cat_by[e]["f1"])
        rb = max(reg_by, key=lambda e: reg_by[e]["top10_acc_indist"])
        out["disjoint_cat"].append(float(cat_by[cb]["f1"]) * 100)
        out["disjoint_reg"].append(float(reg_by[rb]["top10_acc_indist"]) * 100)
        shared = sorted(set(cat_by) & set(reg_by))

        def geom(ep):
            c = float(cat_by[ep]["f1"]); r = float(reg_by[ep]["top10_acc_indist"])
            return math.sqrt(c * r) if c > 0 and r > 0 else 0.0

        ge = max(shared, key=geom)
        out["joint_cat"].append(float(cat_by[ge]["f1"]) * 100)
        out["joint_reg"].append(float(reg_by[ge]["top10_acc_indist"]) * 100)
    return out


def main():
    result = {"stl_reg": {}, "stl_cat": {}, "mtl": {}}

    for state in STATES:
        dj = _stl_reg_cell("resln_design_j", state)
        db = _stl_reg_cell("resln_design_b", state)
        hgi = _p1_reg_ref(state, "hgi")
        canon_j = _p1_reg_ref(state, "design_j")
        entry = {
            "resln_design_j_pf": dj, "resln_design_j_mean": _mean(dj) if dj else None,
            "resln_design_b_pf": db, "resln_design_b_mean": _mean(db) if db else None,
            "hgi_pf": hgi, "hgi_mean": _mean(hgi) if hgi else None,
            "canonical_design_j_pf": canon_j,
            "canonical_design_j_mean": _mean(canon_j) if canon_j else None,
        }
        if dj and hgi:
            d, m, W, p_gt = _wilcox(dj, hgi, "greater")
            _, _, _, p_lt = _wilcox(dj, hgi, "less")
            entry["vs_hgi"] = {"delta_mean": m, "deltas": d, "W": W,
                               "p_beat": p_gt, "p_below": p_lt}
        if dj and db:
            d, m, W, p_gt = _wilcox(dj, db, "greater")
            entry["vs_resln_design_b"] = {"delta_mean": m, "deltas": d, "W": W, "p_gt": p_gt}
        if dj and canon_j:
            d, m, W, p_gt = _wilcox(dj, canon_j, "greater")
            entry["vs_canonical_design_j"] = {"delta_mean": m, "deltas": d, "W": W, "p_gt": p_gt}
        result["stl_reg"][state] = entry

    for state in STATES:
        dj = _cat_pf_from_cell("resln_design_j", state)
        db = _cat_pf_from_cell("resln_design_b", state)
        canon = _cat_pf_from_cell("canonical", state)
        entry = {
            "resln_design_j_pf": dj, "resln_design_j_mean": _mean(dj) if dj else None,
            "resln_design_b_pf": db, "resln_design_b_mean": _mean(db) if db else None,
            "canonical_pf": canon, "canonical_mean": _mean(canon) if canon else None,
            "hgi_cat_agg_mean": _hgi_cat_agg(state),
        }
        if dj and db:
            d, m, W, p_gt = _wilcox(dj, db, "greater")
            entry["vs_resln_design_b"] = {"delta_mean": m, "deltas": d, "W": W, "p_gt": p_gt}
        if dj and canon:
            d, m, W, p_gt = _wilcox(dj, canon, "greater")
            entry["vs_canonical"] = {"delta_mean": m, "deltas": d, "W": W, "p_gt": p_gt}
        result["stl_cat"][state] = entry

    for state in STATES:
        base_dir = _mtl_run_dir("canonical_noresln", state)
        v_dir = _mtl_run_dir("resln_design_j", state)
        if base_dir is None or v_dir is None:
            result["mtl"][state] = {"base": base_dir is not None, "variant": v_dir is not None}
            continue
        base_pf = _mtl_per_fold(base_dir)
        v_pf = _mtl_per_fold(v_dir)
        if not base_pf or not v_pf:
            result["mtl"][state] = {"base_pf": bool(base_pf), "variant_pf": bool(v_pf)}
            continue
        cmp = {}
        for front, rk, ck in [("disjoint", "disjoint_reg", "disjoint_cat"),
                              ("joint", "joint_reg", "joint_cat")]:
            dr, mr, Wr, pr = _wilcox(v_pf[rk], base_pf[rk], "greater")
            dc, mc, Wc, pc = _wilcox(v_pf[ck], base_pf[ck], "greater")
            cmp[front] = {
                "reg_v_mean": _mean(v_pf[rk]), "reg_base_mean": _mean(base_pf[rk]),
                "reg_delta_mean": mr, "reg_deltas": dr, "reg_W": Wr, "reg_p_gt": pr,
                "cat_v_mean": _mean(v_pf[ck]), "cat_base_mean": _mean(base_pf[ck]),
                "cat_delta_mean": mc, "cat_deltas": dc, "cat_W": Wc, "cat_p_gt": pc,
            }
        result["mtl"][state] = {"per_fold": v_pf, "base_per_fold": base_pf, "compare": cmp}

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
