#!/usr/bin/env python3
"""R2 AL multi-seed gate — each AFTB config vs base (champion G) at {0,1,7,100}.

Per-fold matched reg = top10_acc_indist·(1−ood) @ indist-best epoch; cat = diag-best
macro-F1. Per-config: 4-seed mean Δreg/Δcat ± std, paired Wilcoxon (reg over n=20
fold-seed pairs, cat over n=4 seeds). Gate: 4-seed mean ≥0.3 pp EITHER head.
"""
import csv, glob, json, statistics as st
from pathlib import Path
from scipy.stats import wilcoxon

REPO = Path(__file__).resolve().parents[2]
ST = "alabama"
ORDER = ["aftb_all", "aftb_late", "aftb_early", "reg_protect", "cat_protect"]


def per_fold_reg(rd):
    out = []
    for f in sorted(glob.glob(str(REPO / rd / "metrics/fold*_next_region_val.csv"))):
        rows = list(csv.DictReader(open(f)))
        b = max(rows, key=lambda r: float(r["top10_acc_indist"]))
        out.append(float(b["top10_acc_indist"]) * (1 - float(b["ood_fraction"])) * 100)
    return out


def cat_f1(rd):
    d = json.load(open(REPO / rd / "summary/full_summary.json"))
    return d["diagnostic_task_best"]["next_category"]["f1"]["mean"] * 100


# rundirs: seed0 from the screen manifest (AL rows), seeds {1,7,100} from multiseed.
runs = {}  # (seed, cfg) -> rundir
for line in (REPO / "scripts/mtl_frontier/r2_aftb_manifest.tsv").read_text().splitlines():
    p = line.split("\t")
    if len(p) >= 4 and p[1] == ST:
        cfg = p[0].rsplit("_" + ST, 1)[0]
        runs[(0, cfg)] = p[3]
for line in (REPO / "scripts/mtl_frontier/r2_al_multiseed_manifest.tsv").read_text().splitlines():
    p = line.split("\t")
    if len(p) >= 4:
        cfg = p[0].rsplit("_s", 1)[0]; seed = int(p[1])
        runs[(seed, cfg)] = p[3]

SEEDS = [0, 1, 7, 100]
out = {"state": ST, "comparand": "base = champion G (v16, KD-off)", "configs": {}}
promoted = []
for cfg in ORDER:
    pb, pr, scat_b, scat_r, sreg_d = [], [], [], [], []
    ok = True
    for s in SEEDS:
        rb, rr = runs.get((s, "base")), runs.get((s, cfg))
        if not rb or not rr:
            ok = False; continue
        fb, fr = per_fold_reg(rb), per_fold_reg(rr)
        pb += fb; pr += fr
        sreg_d.append(st.mean(fr) - st.mean(fb))
        scat_b.append(cat_f1(rb)); scat_r.append(cat_f1(rr))
    if not ok or not sreg_d:
        out["configs"][cfg] = {"error": "missing runs"}; continue
    dreg = round(st.mean(sreg_d), 3); dreg_sd = round(st.pstdev(sreg_d), 3)
    dcat = round(st.mean([r - b for r, b in zip(scat_r, scat_b)]), 3)
    dcat_sd = round(st.pstdev([r - b for r, b in zip(scat_r, scat_b)]), 3)
    try:
        _, preg = wilcoxon(pr, pb, alternative="greater"); preg = round(float(preg), 5)
    except Exception:
        preg = None
    hit = (dreg >= 0.3) or (dcat >= 0.3)
    out["configs"][cfg] = {
        "spec": {"aftb_all": "ab+ba,ab+ba", "aftb_late": "none,ab+ba",
                 "aftb_early": "ab+ba,none", "reg_protect": "ab,ab", "cat_protect": "ba,ba"}[cfg],
        "mean_delta_reg": dreg, "std_delta_reg": dreg_sd,
        "mean_delta_cat": dcat, "std_delta_cat": dcat_sd,
        "per_seed_delta_reg": [round(x, 3) for x in sreg_d],
        "wilcoxon_reg_p_n20": preg,
        "gate_either_>=0.3": hit,
    }
    if hit:
        promoted.append((cfg, dreg, dcat))

out["promote_candidates"] = [{"config": c, "mean_delta_reg": dr, "mean_delta_cat": dc}
                             for c, dr, dc in promoted]
outp = REPO / "docs/results/mtl_frontier/r2_al_multiseed_results.json"
outp.parent.mkdir(parents=True, exist_ok=True)
outp.write_text(json.dumps(out, indent=2) + "\n")
print(json.dumps(out, indent=2))
print("\n=== R2 AL MULTI-SEED GATE (≥0.3pp EITHER head, 4-seed mean) ===")
for cfg in ORDER:
    c = out["configs"].get(cfg, {})
    if "error" in c:
        print(f"  {cfg}: {c['error']}"); continue
    flag = " ★PROMOTE" if c["gate_either_>=0.3"] else ""
    print(f"  {cfg:12} ({c['spec']:12}) Δreg {c['mean_delta_reg']:+.3f}±{c['std_delta_reg']} "
          f"(p={c['wilcoxon_reg_p_n20']})  Δcat {c['mean_delta_cat']:+.3f}±{c['std_delta_cat']}{flag}")
print(f"\n  PROMOTE candidates: {[c for c,_,_ in promoted] or 'NONE → R2 null'}")
print(f"WROTE {outp}")
