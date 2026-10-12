"""G1 per-state aggregation: TO vs FULL (category macro-F1 at f1-best epoch; region per_fold[0].top10_acc).
usage: g1_aggregate.py <state> <printed_cat_folds_csv> <printed_reg_folds_csv>"""
import sys, json, glob
import numpy as np, pandas as pd
from scipy import stats
st = sys.argv[1]; P_cat = [float(x) for x in sys.argv[2].split(",")]; P_reg = [float(x) for x in sys.argv[3].split(",")]
def cat(F, arm):
    f = glob.glob(f"results/g1_cat_f{F}/{arm}/*/{st}/*/metrics/fold1_next_val.csv"); assert len(f) == 1, (F, arm, f)
    d = pd.read_csv(f[0]); i = d.f1.idxmax()
    rep = json.load(open(glob.glob(f[0].replace("metrics/fold1_next_val.csv", "folds/fold1_next_report.json"))[0]))
    sup = int(rep["macro avg"]["support"]) if "macro avg" in rep else None
    n_val = json.load(open(f"results/g1/splits/{st}_split_seed0_fold{F}.json"))["n_val_rows"]
    assert sup == n_val, f"support {sup} != n_val {n_val} ({F},{arm})"
    return d.f1[i] * 100, int(d.epoch[i]) if "epoch" in d else int(i)
def reg(F, tag):
    pf = json.load(open(f"docs/results/P1/region_head_{st}_region_5f_50ep_g1_reg_{tag}_{st}_f{F}.json"))["heads"]["next_stan_flow"]["per_fold"]
    assert len(pf) == 1; return pf[0]["top10_acc"] * 100, pf[0]["best_epoch"]
rows = []
for F in range(5):
    r = dict(fold=F)
    r["cat_to"], r["cat_to_ep"] = cat(F, "to"); r["cat_full"], r["cat_full_ep"] = cat(F, "full_cpu")
    r["reg_to"], r["reg_to_ep"] = reg(F, "to"); r["reg_full"], r["reg_full_ep"] = reg(F, "fullcpu_s0")
    r["cat_print"] = P_cat[F]; r["reg_print"] = P_reg[F]; rows.append(r)
d = pd.DataFrame(rows); d["cat_TOmFULL"] = d.cat_to - d.cat_full; d["reg_TOmFULL"] = d.reg_to - d.reg_full
d["cat_FULLmPRINT"] = d.cat_full - d.cat_print; d["reg_FULLmPRINT"] = d.reg_full - d.reg_print
pd.set_option("display.width", 250); print(d.round(4).to_string(index=False))
out = {}
for k in ("cat_TOmFULL", "reg_TOmFULL", "cat_FULLmPRINT", "reg_FULLmPRINT"):
    x = d[k].values; out[k] = dict(mean=float(x.mean()), sd=float(x.std(ddof=1)), t_p=float(stats.ttest_1samp(x, 0).pvalue),
                                   wil_p=float(stats.wilcoxon(x).pvalue) if np.any(x != 0) else 1.0, n_pos=int((x > 0).sum()))
    print(f"{k:15s} mean {x.mean():+.4f} sd {x.std(ddof=1):.4f} t p={out[k]['t_p']:.3f} wilcoxon p={out[k]['wil_p']:.4f} positives {out[k]['n_pos']}/5")
print("means:", {c: round(float(d[c].mean()), 4) for c in ("cat_to", "cat_full", "cat_print", "reg_to", "reg_full", "reg_print")})
d.to_csv(f"g1_logs/G1_{st.upper()[:2]}_5fold.csv", index=False); json.dump(out, open(f"g1_logs/G1_{st.upper()[:2]}_5fold_stats.json", "w"), indent=1)
