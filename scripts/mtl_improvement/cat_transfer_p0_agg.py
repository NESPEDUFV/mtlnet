#!/usr/bin/env python3
"""P0 (HANDOFF_AUDIT 2026-06-12) — re-aggregate the FL cat-transfer decomposition
from FOUR DISTINCT seed runs after fixing the triple-counted-rundir manifest flaw.

cat+trunk (reg-OFF) FL = clean seed0 base + reseeded {1,7,100}.
Comparands (trusted, 4 distinct rundirs each) come from R0_matched_metric_bar.json:
  FL G cat f1 mean   = 73.164  (region co-training ON)
  FL STL cat ceiling = 69.963  (next_gru, no trunk)
Decomposition:  architecture = cat+trunk − STL ;  region-transfer = G − cat+trunk.

AL side is unchanged (its 4 rundirs were already distinct) and re-aggregated here
only as a self-consistency cross-check.
"""
import json, statistics as st
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
V14 = "check2hgi_design_k_resln_mae_l0_1"

# Trusted comparands from R0 bar (clean, distinct rundirs).
R0 = json.load(open(REPO / "docs/results/mtl_improvement/R0_matched_metric_bar.json"))
FL_G_CAT   = R0["states"]["florida"]["g_cat_f1_mean"]        # 73.164
FL_STL_CAT = R0["states"]["florida"]["c_cat_ceiling_mean"]   # 69.963
AL_G_CAT   = R0["states"]["alabama"]["g_cat_f1_mean"]
AL_STL_CAT = R0["states"]["alabama"]["c_cat_ceiling_mean"]


def cat_f1(rundir: str) -> float:
    """Per-task diagnostic-best macro-F1 (ref_mtl_metric_field), as a percentage."""
    p = REPO / rundir / "summary" / "full_summary.json"
    d = json.load(open(p))
    return round(d["diagnostic_task_best"]["next_category"]["f1"]["mean"] * 100, 3)


# --- FL cat+trunk (reg-OFF): seed0 base + reseeded {1,7,100} ---
FL_RUNDIRS = {
    0:   f"results/{V14}/florida/mtlnet_lr1.0e-04_bs2048_ep50_20260608_185334_3061119",
}
# pull reseed rundirs from the reseed manifest
reseed_man = REPO / "scripts/mtl_improvement/cat_transfer_reseed_manifest.tsv"
for line in reseed_man.read_text().splitlines():
    if not line.strip():
        continue
    key, _kind, rd = line.split("\t")
    seed = int(key.split("_s")[1].split("|")[0])
    FL_RUNDIRS[seed] = rd

# --- AL cat+trunk (already-clean, cross-check) ---
AL_RUNDIRS = {
    0:   f"results/{V14}/alabama/mtlnet_lr1.0e-04_bs2048_ep50_20260608_185331_3061125",
    1:   f"results/{V14}/alabama/mtlnet_lr1.0e-04_bs2048_ep50_20260610_031508_3671027",
    7:   f"results/{V14}/alabama/mtlnet_lr1.0e-04_bs2048_ep50_20260610_031907_3671875",
    100: f"results/{V14}/alabama/mtlnet_lr1.0e-04_bs2048_ep50_20260610_032306_3672588",
}


def summarise(name, rundirs, g_cat, stl_cat):
    per_seed = {s: cat_f1(rd) for s, rd in sorted(rundirs.items())}
    vals = list(per_seed.values())
    mean = round(st.mean(vals), 3)
    sd = round(st.pstdev(vals), 3) if len(vals) > 1 else 0.0
    arch = round(mean - stl_cat, 3)
    transfer = round(g_cat - mean, 3)
    return {
        "cat_trunk_regOFF_per_seed": per_seed,
        "cat_trunk_regOFF_mean": mean,
        "cat_trunk_regOFF_std": sd,
        "n_seeds": len(vals),
        "stl_cat_ceiling": stl_cat,
        "g_cat_regON": g_cat,
        "architecture": arch,
        "region_transfer": transfer,
        "total": round(g_cat - stl_cat, 3),
        "rundirs": {str(s): rd for s, rd in sorted(rundirs.items())},
    }


out = {
    "_note": "P0 re-aggregation after manifest triple-count fix (HANDOFF_AUDIT 2026-06-12). "
             "FL cat+trunk is now 4 DISTINCT seeds {0,1,7,100}; supersedes the prior 72.09 "
             "(=seed0 + one run counted 3x). Comparands g_cat/stl from R0_matched_metric_bar.json.",
    "metric": "diagnostic_task_best.next_category.f1.mean (macro-F1, %)",
    "florida": summarise("florida", FL_RUNDIRS, FL_G_CAT, FL_STL_CAT),
    "alabama": summarise("alabama", AL_RUNDIRS, AL_G_CAT, AL_STL_CAT),
}

outp = REPO / "docs/results/mtl_improvement/cat_transfer_decomposition_4seed.json"
outp.write_text(json.dumps(out, indent=2) + "\n")
print(json.dumps(out, indent=2))
print(f"\nWROTE {outp}")
