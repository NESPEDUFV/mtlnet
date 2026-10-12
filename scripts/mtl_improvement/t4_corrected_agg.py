#!/usr/bin/env python3
"""H2 (HANDOFF_AUDIT 2026-06-12) — commit the Tier-4 CORRECTED re-run + T4.0a
scale-norm cw-grid as a JSON artefact (they previously existed only as markdown
tables in T4_audit_and_verdict.md §4/§5 + remote rundir pointers, unlike the full
screen which has T4_full_screen.json).

Reuses the t4_agg.py reg_full_cat pattern: reg-full = indist*(1-ood) at the
indist-best epoch (R0 matched metric), cat = diagnostic-best macro-F1. Δ vs the
G control (static_weight cw=0.75) and vs the R0 matched (c) ceilings.

Sources:
  scripts/mtl_improvement/t4_corrected_manifest.tsv  (§4: static cw-sweep + gradnorm lr=0.05 + nash mn=2.2)
  scripts/mtl_improvement/t40a_wgrid_manifest.tsv    (§5: scale-norm cw 0.10/0.20/0.35, AL+FL)
  scripts/mtl_improvement/t4_full_manifest.tsv       (G control: static_weight)
"""
import csv, glob, json, statistics as st
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]

# R0 matched (c) ceilings (full top10_acc / cat F1, multi-seed) — same as t4_agg.py.
CEIL = {"alabama": (62.67, 50.35), "florida": (73.27, 69.96)}


def reg_full_cat(rd):
    folds = []
    for f in sorted(glob.glob(str(REPO / rd / "metrics/fold*_next_region_val.csv"))):
        rows = list(csv.DictReader(open(f)))
        b = max(rows, key=lambda r: float(r["top10_acc_indist"]))
        folds.append(float(b["top10_acc_indist"]) * (1 - float(b["ood_fraction"])) * 100)
    d = json.load(open(REPO / rd / "summary/full_summary.json"))
    cat = d["diagnostic_task_best"]["next_category"]["f1"]["mean"] * 100
    return (round(st.mean(folds), 2) if folds else None), round(cat, 2)


def load_manifest(name):
    out = {}
    for line in (REPO / "scripts/mtl_improvement" / name).read_text().splitlines():
        p = line.split("\t")
        if len(p) >= 3:
            out[p[0]] = (p[1], p[2])
    return out


# Build per-state arm tables.
manifests = {
    "corrected_rerun": "t4_corrected_manifest.tsv",   # §4
    "scalenorm_wgrid": "t40a_wgrid_manifest.tsv",      # §5
}
# G control from the full screen.
full = load_manifest("t4_full_manifest.tsv")
control = {k.split("|")[1]: v[1] for k, v in full.items() if k.startswith("static_weight|")}

result = {
    "_note": "H2 — Tier-4 corrected re-run (§4) + scale-norm cw-grid (§5) raw aggregation, "
             "committed 2026-06-12 (HANDOFF_AUDIT). Metric: reg-full = indist*(1-ood) @ indist-best "
             "epoch (R0 matched); cat = diagnostic-best macro-F1. seed0, AL+FL.",
    "ceilings_R0_matched": {s: {"reg_full": c[0], "cat_f1": c[1]} for s, c in CEIL.items()},
    "g_control_static_weight_cw0.75": {},
    "corrected_rerun": {},
    "scalenorm_wgrid": {},
}

for state, rd in control.items():
    reg, cat = reg_full_cat(rd)
    result["g_control_static_weight_cw0.75"][state] = {"reg_full": reg, "cat_f1": cat, "rundir": rd}


def fill(section, manifest_name):
    man = load_manifest(manifest_name)
    for key, (arm, rd) in man.items():
        arm_, state = key.split("|")
        reg, cat = reg_full_cat(rd)
        ctrl = result["g_control_static_weight_cw0.75"].get(state, {})
        creg, ccat = CEIL[state]
        result[section].setdefault(arm, {})[state] = {
            "reg_full": reg, "cat_f1": cat,
            "d_reg_vs_G": round(reg - ctrl["reg_full"], 2) if reg is not None and ctrl else None,
            "d_cat_vs_G": round(cat - ctrl["cat_f1"], 2) if ctrl else None,
            "d_reg_vs_ceil": round(reg - creg, 2) if reg is not None else None,
            "rundir": rd,
        }


fill("corrected_rerun", "t4_corrected_manifest.tsv")
fill("scalenorm_wgrid", "t40a_wgrid_manifest.tsv")

outp = REPO / "docs/results/mtl_improvement/T4_corrected_rerun.json"
outp.write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps(result, indent=2))
print(f"\nWROTE {outp}")
