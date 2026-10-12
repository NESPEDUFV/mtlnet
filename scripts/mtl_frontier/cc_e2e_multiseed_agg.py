#!/usr/bin/env python3
"""cc_e2e multi-seed gate vs champion G at AL+FL {0,1,7,100}.
Baselines reused: AL = r2 base_alabama(s0) + r2_al_multiseed base_s*; FL = r2 base_florida(s0)
+ r10_fl_multiseed base_s* (grm=0). cc_e2e: s0 from cc_manifest, s{1,7,100} from cc_e2e_multiseed.
Per-(seed,fold) reg pairing (n=20); cat over 4 seeds. Gate: 4-seed mean ≥0.3 either head.
"""
import csv, glob, json, statistics as st
from pathlib import Path
from scipy.stats import wilcoxon
REPO = Path(__file__).resolve().parents[2]


def pf_reg(rd):
    out = []
    for f in sorted(glob.glob(str(REPO / rd / "metrics/fold*_next_region_val.csv"))):
        rows = list(csv.DictReader(open(f)))
        b = max(rows, key=lambda r: float(r["top10_acc_indist"]))
        out.append(float(b["top10_acc_indist"]) * (1 - float(b["ood_fraction"])) * 100)
    return out


def cat(rd):
    return json.load(open(REPO / rd / "summary/full_summary.json"))["diagnostic_task_best"]["next_category"]["f1"]["mean"] * 100


# baselines
base = {"alabama": {}, "florida": {}}
for line in (REPO / "scripts/mtl_frontier/r2_aftb_manifest.tsv").read_text().splitlines():
    p = line.split("\t")
    if len(p) >= 4 and p[0] == "base_alabama": base["alabama"][0] = p[3]
    if len(p) >= 4 and p[0] == "base_florida": base["florida"][0] = p[3]
for line in (REPO / "scripts/mtl_frontier/r2_al_multiseed_manifest.tsv").read_text().splitlines():
    p = line.split("\t")  # tag \t seed \t spec(empty) \t rundir
    if len(p) >= 4 and p[0].startswith("base_s") and p[1].strip().isdigit():
        base["alabama"][int(p[1])] = p[3]
for line in (REPO / "scripts/mtl_frontier/r10_fl_multiseed_manifest.tsv").read_text().splitlines():
    p = line.split("\t")  # tag seed grm rundir
    if len(p) >= 4 and p[0].startswith("base_s") and p[2] == "0":
        base["florida"][int(p[1])] = p[3]
# cc_e2e
cce = {"alabama": {}, "florida": {}}
for line in (REPO / "scripts/mtl_frontier/cc_manifest.tsv").read_text().splitlines():
    p = line.split("\t")
    if len(p) >= 3 and p[0] == "cc_e2e_alabama": cce["alabama"][0] = p[2]
    if len(p) >= 3 and p[0] == "cc_e2e_florida": cce["florida"][0] = p[2]
for line in (REPO / "scripts/mtl_frontier/cc_e2e_multiseed_manifest.tsv").read_text().splitlines():
    p = line.split("\t")  # tag state seed rundir
    if len(p) >= 4:
        cce[p[1]][int(p[2])] = p[3]

SEEDS = [0, 1, 7, 100]
out = {"config": "cc_e2e (cond_coupling=posterior, end-to-end)", "comparand": "champion G (KD-off)", "states": {}}
for stt in ("alabama", "florida"):
    pb, pc, dreg_s, dcat_s = [], [], [], []
    for s in SEEDS:
        b, c = base[stt].get(s), cce[stt].get(s)
        if not b or not c:
            continue
        fb, fc = pf_reg(b), pf_reg(c)
        pb += fb; pc += fc
        dreg_s.append(st.mean(fc) - st.mean(fb)); dcat_s.append(cat(c) - cat(b))
    if not dreg_s:
        continue
    try:
        _, preg = wilcoxon(pc, pb, alternative="greater"); preg = round(float(preg), 5)
        _, pcat = wilcoxon(dcat_s, [0]*len(dcat_s), alternative="greater"); pcat = round(float(pcat), 5)
    except Exception:
        preg = pcat = None
    mdr, mdc = round(st.mean(dreg_s), 3), round(st.mean(dcat_s), 3)
    out["states"][stt] = {"n_seeds": len(dreg_s), "mean_delta_reg": mdr, "std_delta_reg": round(st.pstdev(dreg_s), 3),
        "mean_delta_cat": mdc, "std_delta_cat": round(st.pstdev(dcat_s), 3),
        "per_seed_delta_cat": [round(x, 3) for x in dcat_s], "per_seed_delta_reg": [round(x, 3) for x in dreg_s],
        "wilcoxon_reg_p_n20": preg, "wilcoxon_cat_p_n4": pcat,
        "gate_either_>=0.3": (mdr >= 0.3) or (mdc >= 0.3)}

outp = REPO / "docs/results/mtl_frontier/cc_e2e_multiseed_results.json"
outp.write_text(json.dumps(out, indent=2) + "\n")
print(json.dumps(out, indent=2))
print("\n=== cc_e2e MULTI-SEED GATE (≥0.3 either head, 4-seed) ===")
for stt, v in out["states"].items():
    flag = " ★PROMOTE" if v["gate_either_>=0.3"] else ""
    print(f"  {stt:8} Δreg {v['mean_delta_reg']:+.3f}±{v['std_delta_reg']} (p={v['wilcoxon_reg_p_n20']})  "
          f"Δcat {v['mean_delta_cat']:+.3f}±{v['std_delta_cat']} (p={v['wilcoxon_cat_p_n4']}){flag}")
    print(f"           per-seed Δcat: {v['per_seed_delta_cat']}")
print(f"WROTE {outp}")
