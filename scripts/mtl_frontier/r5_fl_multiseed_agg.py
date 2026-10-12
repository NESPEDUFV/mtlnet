#!/usr/bin/env python3
"""R-CC+ FL multi-seed gate — promoted configs vs MATCHED same-batch champion G
at FL {0,1,7,100}. Per-(seed,fold) reg pairing (n=20, Wilcoxon greater) + per-seed
cat (n=4). Gate ≥0.3 either head on the 4-seed mean. Baselines are the in-batch
`base` rows (not reused) → no code-drift / cross-manifest risk.
"""
import csv, glob, json, statistics as st
from pathlib import Path
from scipy.stats import wilcoxon

REPO = Path(__file__).resolve().parents[2]
SEEDS = [0, 1, 7, 100]


def pf_reg(rd):
    out = []
    for f in sorted(glob.glob(str(REPO / rd / "metrics/fold*_next_region_val.csv"))):
        rows = list(csv.DictReader(open(f)))
        b = max(rows, key=lambda r: float(r["top10_acc_indist"]))
        out.append(float(b["top10_acc_indist"]) * (1 - float(b["ood_fraction"])) * 100)
    return out


def cat(rd):
    return json.load(open(REPO / rd / "summary/full_summary.json"))[
        "diagnostic_task_best"]["next_category"]["f1"]["mean"] * 100


# manifest: tag \t state \t seed \t rundir
man = {}  # tag -> {seed: rundir}
for line in (REPO / "scripts/mtl_frontier/r5_fl_multiseed_manifest.tsv").read_text().splitlines():
    p = line.split("\t")
    if len(p) >= 4:
        man.setdefault(p[0], {})[int(p[2])] = p[3]

base = man.get("base", {})
configs = [t for t in man if t != "base"]
out = {"comparand": "matched same-batch GLOBAL log_T-KD W=0.2 (gate=none), FL", "configs": {}}
for cfg in sorted(configs):
    pb, pc, dreg_s, dcat_s = [], [], [], []
    for s in SEEDS:
        b, c = base.get(s), man[cfg].get(s)
        if not b or not c:
            continue
        fb, fc = pf_reg(b), pf_reg(c)
        if len(fb) != len(fc):
            continue
        pb += fb; pc += fc
        dreg_s.append(st.mean(fc) - st.mean(fb)); dcat_s.append(cat(c) - cat(b))
    if not dreg_s:
        continue
    try:
        _, preg = wilcoxon(pc, pb, alternative="greater"); preg = round(float(preg), 5)
        _, pcat = wilcoxon(dcat_s, [0] * len(dcat_s), alternative="greater"); pcat = round(float(pcat), 5)
    except Exception:
        preg = pcat = None
    mdr, mdc = round(st.mean(dreg_s), 3), round(st.mean(dcat_s), 3)
    out["configs"][cfg] = {
        "n_seeds": len(dreg_s), "mean_delta_reg": mdr, "std_delta_reg": round(st.pstdev(dreg_s), 3),
        "mean_delta_cat": mdc, "std_delta_cat": round(st.pstdev(dcat_s), 3),
        "per_seed_delta_cat": [round(x, 3) for x in dcat_s],
        "per_seed_delta_reg": [round(x, 3) for x in dreg_s],
        "wilcoxon_reg_p_n20": preg, "wilcoxon_cat_p_n4": pcat,
        "gate_either_>=0.3": (mdr >= 0.3) or (mdc >= 0.3),
    }

outp = REPO / "docs/results/mtl_frontier/r5_fl_multiseed_results.json"
outp.write_text(json.dumps(out, indent=2) + "\n")
print("=== R-CC+ FL MULTI-SEED GATE (≥0.3 either head, 4-seed, matched G) ===")
for cfg, v in out["configs"].items():
    flag = " ★PROMOTE" if v["gate_either_>=0.3"] else ""
    print(f"  {cfg:10} Δreg {v['mean_delta_reg']:+.3f}±{v['std_delta_reg']} (p={v['wilcoxon_reg_p_n20']})  "
          f"Δcat {v['mean_delta_cat']:+.3f}±{v['std_delta_cat']} (p={v['wilcoxon_cat_p_n4']}){flag}")
    print(f"             per-seed Δcat: {v['per_seed_delta_cat']}  Δreg: {v['per_seed_delta_reg']}")
print(f"WROTE {outp}")
