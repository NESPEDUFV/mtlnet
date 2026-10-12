#!/usr/bin/env python3
"""R-CC+ screen aggregator — the conditional-coupling family vs FRESH matched
champion G (cond off, KD-off), AL+FL seed0.

Matched bar (same as cc_agg / all mtl_frontier levers):
  reg = mean_folds[ top10_acc_indist · (1 - ood_fraction) ] at the indist-best
        epoch, ×100  (diagnostic-best, read straight from the per-epoch CSVs —
        NOT the joint-selected full_summary reg, ref_mtl_metric_field)
  cat = diagnostic_task_best.next_category.f1.mean ×100  (from full_summary.json)
Gate ≥0.3 pp either head. Any FL seed0 positive → multi-seed FL {0,1,7,100}.
"""
import csv, glob, json, statistics as st
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
CONFIGS = ["cc_e2e", "cc_calib", "cc_argmax", "cc_topk", "cc_film", "cc_concat", "cc_logitp"]
STATES = ["alabama", "florida"]


def rc(rd):
    """(matched-reg, diagnostic-best-cat) for a rundir."""
    rd = REPO / rd
    folds = []
    for f in sorted(glob.glob(str(rd / "metrics/fold*_next_region_val.csv"))):
        rows = list(csv.DictReader(open(f)))
        b = max(rows, key=lambda r: float(r["top10_acc_indist"]))
        folds.append(float(b["top10_acc_indist"]) * (1 - float(b["ood_fraction"])) * 100)
    d = json.load(open(rd / "summary/full_summary.json"))
    cat = d["diagnostic_task_best"]["next_category"]["f1"]["mean"] * 100
    return (round(st.mean(folds), 3) if folds else None, round(cat, 3))


man = {}
for line in (REPO / "scripts/mtl_frontier/ccplus_manifest.tsv").read_text().splitlines():
    p = line.split("\t")
    if len(p) >= 3:
        man[p[0]] = p[2]

out = {"comparand": "fresh matched champion G (cond=none, KD-off), seed0", "by_state": {}}
promoted = []
for state in STATES:
    btag = f"base_{state}"
    if btag not in man:
        print(f"!! missing {btag} in manifest — run ccplus_screen.sh")
        continue
    br, bc = rc(man[btag])
    out["by_state"][state] = {"base_reg": br, "base_cat": bc, "configs": {}}
    for cfg in CONFIGS:
        tag = f"{cfg}_{state}"
        if tag not in man:
            continue
        rr, rcat = rc(man[tag])
        dreg = round(rr - br, 3) if (rr is not None and br is not None) else None
        dcat = round(rcat - bc, 3)
        hit = (dreg is not None and dreg >= 0.3) or (dcat >= 0.3)
        out["by_state"][state]["configs"][cfg] = {
            "reg": rr, "cat": rcat, "delta_reg": dreg, "delta_cat": dcat,
            "gate_either_>=0.3": hit,
        }
        if hit:
            promoted.append((state, cfg, dreg, dcat))

out["promote_candidates"] = [
    {"state": s, "config": c, "delta_reg": dr, "delta_cat": dc} for s, c, dr, dc in promoted
]
fl_positives = sorted({c for s, c, _, _ in promoted if s == "florida"})
out["fl_multiseed_next"] = fl_positives

outp = REPO / "docs/results/mtl_frontier/ccplus_screen_results.json"
outp.write_text(json.dumps(out, indent=2) + "\n")

print("=== R-CC+ SCREEN (≥0.3pp either head over fresh matched champion G, seed0) ===")
for state in STATES:
    s = out["by_state"].get(state, {})
    print(f"\n{state}: base reg {s.get('base_reg')} / cat {s.get('base_cat')}")
    for cfg in CONFIGS:
        c = s.get("configs", {}).get(cfg)
        if not c:
            continue
        flag = " ★" if c["gate_either_>=0.3"] else ""
        dr = f"{c['delta_reg']:+.3f}" if c["delta_reg"] is not None else "  n/a"
        print(f"    {cfg:10} reg {str(c['reg']):>7} ({dr})   cat {c['cat']:>7} ({c['delta_cat']:+.3f}){flag}")
print(f"\n  FL seed0 positives → multi-seed: {fl_positives or 'NONE'}")
print(f"  all promote candidates: {[(s,c) for s,c,_,_ in promoted] or 'NONE'}")
print(f"WROTE {outp}")
