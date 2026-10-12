#!/usr/bin/env python3
"""Aggregate the 3 follow-up screens. Gate ≥0.3 pp on the relevant head, vs the
correct reused baseline. Metric: reg-full=top10_acc_indist·(1−ood)@indist-best; cat=diag-best F1.
"""
import csv, glob, json, statistics as st
from pathlib import Path
REPO = Path(__file__).resolve().parents[2]


def rc(rd):
    rd = REPO / rd
    folds = []
    for f in sorted(glob.glob(str(rd / "metrics/fold*_next_region_val.csv"))):
        rows = list(csv.DictReader(open(f)))
        b = max(rows, key=lambda r: float(r["top10_acc_indist"]))
        folds.append(float(b["top10_acc_indist"]) * (1 - float(b["ood_fraction"])) * 100)
    d = json.load(open(rd / "summary/full_summary.json"))
    cat = d["diagnostic_task_best"]["next_category"]["f1"]["mean"] * 100
    return (round(st.mean(folds), 3) if folds else None, round(cat, 3))


def load(man, key_idx=0):
    out = {}
    for line in (REPO / man).read_text().splitlines():
        p = line.split("\t")
        if len(p) >= 4:
            out[p[0]] = p[3]
    return out

fu = load("scripts/mtl_frontier/followup_manifest.tsv")
# baselines (champion G KD-off)
r2 = {}
for line in (REPO / "scripts/mtl_frontier/r2_aftb_manifest.tsv").read_text().splitlines():
    p = line.split("\t")
    if len(p) >= 4 and p[0] in ("base_alabama", "base_florida"):
        r2[p[1]] = p[3]
r2ms = {}
for line in (REPO / "scripts/mtl_frontier/r2_multistate_manifest.tsv").read_text().splitlines():
    p = line.split("\t")
    if len(p) >= 5 and p[0] in ("base_arizona_s0", "base_georgia_s0"):
        r2ms[p[1]] = p[4]
r2al = {}
for line in (REPO / "scripts/mtl_frontier/r2_al_multiseed_manifest.tsv").read_text().splitlines():
    p = line.split("\t")
    # 2026-06-17 audit fix: seed is in p[1] (format: tag \t seed \t <blank> \t rundir),
    # NOT p[2] — the old p[2].isdigit() check captured 0 seeds, so the FU1 AL "4-seed"
    # number was silently SEED0-ONLY. With the fix r2al captures seeds {1,7,100}.
    if len(p) >= 4 and p[0].startswith("base_s") and p[1].strip().isdigit():
        r2al[int(p[1])] = p[3]
# G+log_T-KD baseline (R1 base)
r1 = {}
for line in (REPO / "scripts/mtl_frontier/r1_screen_manifest.tsv").read_text().splitlines():
    p = line.split("\t")
    if len(p) >= 3 and p[0].startswith("base_"):
        r1[p[1]] = p[2]
# GRM AL seed0 (from r10_screen)
grm_al_s0 = None
for line in (REPO / "scripts/mtl_frontier/r10_screen_manifest.tsv").read_text().splitlines():
    p = line.split("\t")
    if len(p) >= 3 and p[0] == "grm_alabama":
        grm_al_s0 = p[2]

out = {}

# ---- Idea 1: GRM at AZ/GE seed0 + AL multi-seed {0,1,7,100} ----
i1 = {"comparand": "champion G (KD-off)", "states": {}}
for stt in ("arizona", "georgia"):
    g = fu.get(f"i1_grm_{stt}_s0"); b = r2ms.get(stt)
    if g and b:
        gr, gc = rc(g); br, bc = rc(b)
        i1["states"][stt] = {"seeds": [0], "delta_reg": round(gr - br, 3), "delta_cat": round(gc - bc, 3)}
# AL 4-seed
al_dreg, al_dcat = [], []
base_al = {0: r2.get("alabama"), **r2al}
grm_al = {0: grm_al_s0, 1: fu.get("i1_grm_alabama_s1"), 7: fu.get("i1_grm_alabama_s7"), 100: fu.get("i1_grm_alabama_s100")}
for s in (0, 1, 7, 100):
    if base_al.get(s) and grm_al.get(s):
        gr, gc = rc(grm_al[s]); br, bc = rc(base_al[s])
        al_dreg.append(gr - br); al_dcat.append(gc - bc)
if al_dreg:
    i1["states"]["alabama"] = {"seeds": [0, 1, 7, 100][:len(al_dreg)],
                               "delta_reg": round(st.mean(al_dreg), 3), "std_reg": round(st.pstdev(al_dreg), 3),
                               "delta_cat": round(st.mean(al_dcat), 3), "std_cat": round(st.pstdev(al_dcat), 3),
                               "per_seed_cat": [round(x, 3) for x in al_dcat]}
out["idea1_R10_multistate"] = i1

# ---- Idea 2: aux_gated vs champion G (aux), AL+FL seed0 ----
i2 = {"comparand": "champion G (fusion=aux, KD-off)", "states": {}}
for stt in ("alabama", "florida"):
    g = fu.get(f"i2_auxgated_{stt}_s0"); b = r2.get(stt)
    if g and b:
        gr, gc = rc(g); br, bc = rc(b)
        i2["states"][stt] = {"delta_reg": round(gr - br, 3), "delta_cat": round(gc - bc, 3),
                             "gate_reg_>=0.3": (gr - br) >= 0.3, "gate_either_>=0.3": (gr - br) >= 0.3 or (gc - bc) >= 0.3}
out["idea2_aux_gated"] = i2

# ---- Idea 3: best-stack vs G+log_T-KD, AL+FL seed0 ----
i3 = {"comparand": "G + log_T-KD 0.2", "states": {}}
for stt in ("alabama", "florida"):
    g = fu.get(f"i3_stack_{stt}_s0"); b = r1.get(stt)
    if g and b:
        gr, gc = rc(g); br, bc = rc(b)
        i3["states"][stt] = {"delta_reg": round(gr - br, 3), "delta_cat": round(gc - bc, 3),
                             "gate_either_>=0.3": (gr - br) >= 0.3 or (gc - bc) >= 0.3}
out["idea3_stack"] = i3

outp = REPO / "docs/results/mtl_frontier/followup_results.json"
outp.write_text(json.dumps(out, indent=2) + "\n")
print(json.dumps(out, indent=2))
print("\n=== FOLLOW-UP SUMMARY (gate ≥0.3 either head) ===")
print("IDEA 1 (R10 GRM other states):")
for s, v in i1["states"].items():
    print(f"  {s:8} Δreg {v['delta_reg']:+.3f}  Δcat {v['delta_cat']:+.3f}")
print("IDEA 2 (aux_gated vs G):")
for s, v in i2["states"].items():
    print(f"  {s:8} Δreg {v['delta_reg']:+.3f}  Δcat {v['delta_cat']:+.3f}  {'★' if v['gate_either_>=0.3'] else ''}")
print("IDEA 3 (best-stack vs G+log_T-KD):")
for s, v in i3["states"].items():
    print(f"  {s:8} Δreg {v['delta_reg']:+.3f}  Δcat {v['delta_cat']:+.3f}  {'★' if v['gate_either_>=0.3'] else ''}")
print(f"\nWROTE {outp}")
