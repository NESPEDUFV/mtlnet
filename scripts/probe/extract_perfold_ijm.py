"""Extract per-fold metrics for Designs I/J/M from results/ + P1 JSONs.

Cat: results/check2hgi_design_<x>/<state>/<run>/folds/foldN_next_report.json
     → phase1_perfold/{AL,AZ}_design_<x>_cat_gru_5f50ep.json

Reg: docs/.../P1/region_head_<state>_..._design_<x>_reg...json (heads.next_getnext_hard.per_fold)
     → phase1_perfold/{AL,AZ}_design_<x>_reg_gethard_pf_5f50ep.json
"""
from __future__ import annotations
import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
RESULTS = REPO / "results"
P1 = REPO / "docs/results/P1"
PERFOLD = REPO / "docs/results/phase1_perfold"

import argparse

DESIGNS = ["b", "i", "j", "m"]
STATES = [("alabama", "AL"), ("arizona", "AZ"), ("florida", "FL")]


def latest_run(state_dir: Path) -> Path | None:
    runs = sorted([p for p in state_dir.iterdir() if p.is_dir()])
    return runs[-1] if runs else None


def extract_cat(design: str, state: str, code: str):
    state_dir = RESULTS / f"check2hgi_design_{design}" / state
    if not state_dir.exists():
        print(f"  [{code}/{design}/cat] no run dir"); return None
    run = latest_run(state_dir)
    if run is None:
        print(f"  [{code}/{design}/cat] no run dir (cat skipped)"); return None
    out = {}
    for i in range(1, 6):
        rpt = run / "folds" / f"fold{i}_next_report.json"
        if not rpt.exists():
            print(f"  [{code}/{design}/cat] missing fold{i}"); return None
        d = json.load(rpt.open())
        out[f"fold_{i-1}"] = {"f1": d["macro avg"]["f1-score"]}
    dest = PERFOLD / f"{code}_design_{design}_cat_gru_5f50ep.json"
    dest.write_text(json.dumps(out, indent=2))
    print(f"  [{code}/{design}/cat] wrote {dest.name}")
    return dest


def extract_reg(design: str, state: str, code: str):
    upper = state.upper()
    src = P1 / f"region_head_{state}_region_5f_50ep_STL_{upper}_design_{design}_reg_gethard_pf_5f50ep.json"
    if not src.exists():
        print(f"  [{code}/{design}/reg] missing P1 {src.name}"); return None
    d = json.load(src.open())
    pf = d["heads"]["next_getnext_hard"]["per_fold"]
    out = {}
    for i, f in enumerate(pf):
        out[f"fold_{i}"] = {
            "f1": f.get("f1"),
            "acc1": f.get("accuracy"),
            "acc5": f.get("top5_acc"),
            "acc10": f.get("top10_acc"),
            "mrr": f.get("mrr"),
        }
    dest = PERFOLD / f"{code}_design_{design}_reg_gethard_pf_5f50ep.json"
    dest.write_text(json.dumps(out, indent=2))
    print(f"  [{code}/{design}/reg] wrote {dest.name}")
    return dest


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--designs", nargs="+", default=DESIGNS)
    ap.add_argument("--states", nargs="+", default=[s[0] for s in STATES])
    args = ap.parse_args()
    code_of = {s: c for s, c in STATES}
    for design in args.designs:
        print(f"\n=== Design {design.upper()} ===")
        for state in args.states:
            code = code_of[state]
            extract_cat(design, state, code)
            extract_reg(design, state, code)


if __name__ == "__main__":
    main()
