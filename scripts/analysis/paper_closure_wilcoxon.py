"""Paper-closure paired Wilcoxon analysis — MTL B9 vs STL ceiling per state.

Mirrors `f51_multiseed_analysis.py` extraction methodology (per-fold max
top10_acc_indist for reg, f1 for cat, epoch >= 5). Pools across seeds
where multi-seed data is available.

Usage:
    PYTHONPATH=src python scripts/analysis/paper_closure_wilcoxon.py

Outputs:
    docs/findings/PAPER_CLOSURE_WILCOXON.json

Reads:
    - MTL run dirs:   results/check2hgi/<state>/mtlnet_..._ep50_20260501_*
    - STL reg JSONs:  docs/results/P1/region_head_*paper_close*.json
                      + region_head_florida_region_5f_50ep_c4_clean.json (FL seed=42)
    - STL cat dirs:   results/check2hgi/<state>/next_..._ep50_20260501_*  (CA, TX paper-closure)
                      + docs/results/phase1_perfold/{AL,AZ}_check2hgi_cat_gru_5f50ep.json
"""
import json, statistics
from pathlib import Path
import pandas as pd
import numpy as np
from scipy.stats import wilcoxon

REG_METRIC = "top10_acc_indist"
CAT_METRIC = "f1"
MIN_EPOCH = 5

# Hardcoded mapping of paper-closure run dirs to (state, seed).
MTL_DIRS = {
    ("alabama", 0):   "results/check2hgi/alabama/mtlnet_lr1.0e-04_bs2048_ep50_20260501_014904_411673",
    ("alabama", 1):   "results/check2hgi/alabama/mtlnet_lr1.0e-04_bs2048_ep50_20260501_014904_411676",
    ("alabama", 7):   "results/check2hgi/alabama/mtlnet_lr1.0e-04_bs2048_ep50_20260501_014904_411691",
    ("alabama", 100): "results/check2hgi/alabama/mtlnet_lr1.0e-04_bs2048_ep50_20260501_014904_411706",
    ("arizona", 0):   "results/check2hgi/arizona/mtlnet_lr1.0e-04_bs2048_ep50_20260501_015206_412194",
    ("arizona", 1):   "results/check2hgi/arizona/mtlnet_lr1.0e-04_bs2048_ep50_20260501_015208_412291",
    ("arizona", 7):   "results/check2hgi/arizona/mtlnet_lr1.0e-04_bs2048_ep50_20260501_015209_412306",
    ("arizona", 100): "results/check2hgi/arizona/mtlnet_lr1.0e-04_bs2048_ep50_20260501_015209_412356",
    ("california", 42): "results/check2hgi/california/mtlnet_lr1.0e-04_bs2048_ep50_20260501_015857_412969",
    ("texas", 42):    "results/check2hgi/texas/mtlnet_lr1.0e-04_bs2048_ep50_20260501_023224_413998",
    # Florida B9 reference (single available pre-paper-closure run; seed=42 baseline)
    ("florida", 42):  "results/check2hgi/florida/mtlnet_lr1.0e-04_bs2048_ep50_20260430_0110",
}

# STL cat at CA/TX = paper-closure runs; STL cat at AL/AZ/FL = phase1 / F37 (single-seed at present)
STL_CAT_DIRS_FROM_RUN = {
    "california": "results/check2hgi/california/next_lr1.0e-04_bs2048_ep50_20260501_011357_409058",
    "texas":      "results/check2hgi/texas/next_lr1.0e-04_bs2048_ep50_20260501_012451_409450",
}
STL_CAT_PHASE1 = {  # F37 / phase1 per-fold JSONs (assumed seed=42)
    "alabama": "docs/results/phase1_perfold/AL_check2hgi_cat_gru_5f50ep.json",
    "arizona": "docs/results/phase1_perfold/AZ_check2hgi_cat_gru_5f50ep.json",
}
# FL STL reg seed=42 (c4_clean), used for FL paired Wilcoxon since F51 multi-seed
# B9 per-fold not locally archived.
STL_REG_FL_SEED42 = "docs/results/P1/region_head_florida_region_5f_50ep_c4_clean.json"


def per_fold_best(run_dir: Path, task_filename: str, metric: str, min_epoch: int = MIN_EPOCH):
    out = []
    for fold in (1, 2, 3, 4, 5):
        csv = run_dir / "metrics" / f"fold{fold}_{task_filename}_val.csv"
        if not csv.exists(): return []
        df = pd.read_csv(csv)
        if metric not in df.columns: return []
        masked = df[df["epoch"] >= min_epoch]
        if masked.empty: return []
        out.append(float(masked[metric].max()))
    return out


def collect_stl_reg():
    """Returns {(state, seed): [per-fold top10_acc]}."""
    out = {}
    for jf in Path("docs/results/P1").glob("region_head_*paper_close*.json"):
        d = json.load(jf.open())
        state = d['state']; seed = d['seed']
        out[(state, seed)] = [x['top10_acc'] for x in d['heads']['next_getnext_hard']['per_fold']]
    # FL seed=42 via c4_clean
    if Path(STL_REG_FL_SEED42).exists():
        d = json.load(open(STL_REG_FL_SEED42))
        out[("florida", 42)] = [x['top10_acc'] for x in d['heads']['next_getnext_hard']['per_fold']]
    return out


def collect_stl_cat():
    """Returns {(state, seed): [per-fold f1]} (seed=42 for AL/AZ/FL, paper-closure seed for CA/TX)."""
    out = {}
    # Run-dir based (CA, TX paper-closure)
    for state, d in STL_CAT_DIRS_FROM_RUN.items():
        f1 = per_fold_best(Path(d), "next", CAT_METRIC)
        if f1: out[(state, 42)] = f1
    # Phase1/F37 (AL, AZ)
    for state, jf in STL_CAT_PHASE1.items():
        if Path(jf).exists():
            d = json.load(open(jf))
            out[(state, 42)] = [d[f"fold_{i}"]["f1"] for i in range(5)]
    return out


def main():
    stl_reg = collect_stl_reg()
    stl_cat = collect_stl_cat()
    results = {}
    for state in ["alabama", "arizona", "florida", "california", "texas"]:
        rseeds = sorted({s for (st, s) in MTL_DIRS if st == state})
        if not rseeds: continue
        out = {"state": state, "tasks": {}}
        for task, mtl_csv_name, mtl_metric, stl_dict in [
            ("reg", "next_region",   REG_METRIC, stl_reg),
            ("cat", "next_category", CAT_METRIC, stl_cat),
        ]:
            all_diffs = []
            per_seed = []
            for seed in rseeds:
                mdir = MTL_DIRS.get((state, seed))
                if not mdir: continue
                # MTL-side filename differs at FL: the FL ref run has both cat+reg files (full MTL); same for others.
                mtl_fb = per_fold_best(Path(mdir), mtl_csv_name, mtl_metric)
                stl_fb = stl_dict.get((state, seed)) or stl_dict.get((state, 42))
                if not mtl_fb or not stl_fb: continue
                m, s = np.array(mtl_fb), np.array(stl_fb)
                diffs = m - s
                try:
                    wstat = wilcoxon(diffs, zero_method="wilcox", alternative="two-sided")
                    pv = float(wstat.pvalue)
                except ValueError:
                    pv = float("nan")
                per_seed.append({
                    "seed": seed,
                    "mtl_mean_pp": float(m.mean()*100),
                    "stl_mean_pp": float(s.mean()*100),
                    "delta_pp": float(diffs.mean()*100),
                    "per_fold_diff_pp": [round(float(x*100),3) for x in diffs],
                    "n_pos": int((diffs>0).sum()),
                    "n_neg": int((diffs<0).sum()),
                    "p_value_two_sided": pv,
                })
                all_diffs.extend(diffs.tolist())
            if not per_seed: continue
            arr = np.array(all_diffs)
            try:
                pooled = wilcoxon(arr, zero_method="wilcox", alternative="two-sided")
                pp = float(pooled.pvalue)
            except ValueError:
                pp = float("nan")
            out["tasks"][task] = {
                "n_seeds": len(per_seed),
                "per_seed": per_seed,
                "pooled": {
                    "n_pairs": int(arr.size),
                    "delta_mean_pp": float(arr.mean()*100),
                    "delta_std_pp": float(arr.std(ddof=1)*100) if arr.size > 1 else 0,
                    "n_pos": int((arr>0).sum()),
                    "n_neg": int((arr<0).sum()),
                    "p_value_two_sided": pp,
                },
            }
            sign = "+" if arr.mean() > 0 else ""
            print(f"  {state:<11} {task:>3}: n={int(arr.size):2d}  Δ={sign}{arr.mean()*100:+6.2f} pp  p={pp:.2e}  ({(arr>0).sum()}/{int(arr.size)} MTL>STL)")
        results[state] = out

    out_path = Path("docs/findings/PAPER_CLOSURE_WILCOXON.json")
    out_path.write_text(json.dumps(results, indent=2))
    print(f"\nSaved: {out_path}")


if __name__ == "__main__":
    main()
