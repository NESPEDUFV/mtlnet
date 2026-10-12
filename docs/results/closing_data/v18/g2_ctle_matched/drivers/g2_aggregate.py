"""G2: CTLE category macro-F1 under the MATCHED split vs the June (mismatched-split) board cells."""
import json, glob, numpy as np, pandas as pd
from scipy import stats
R = "/Users/vitor/Desktop/mestrado/ingred/docs/results/closing_data/baseline_compare"
rows = []
for st in ("alabama", "arizona"):
    june = {d["fold"]: d["macro_f1"] for d in json.load(open(f"{R}/{st}_ctle.json"))["per_fold"]}
    for F in range(5):
        rep = glob.glob(f"results/g2_ctle/{st}_f{F}/run/check2hgi_ctle/{st}/*/folds/fold1_next_report.json"); assert len(rep) == 1, (st, F, rep)
        r = json.load(open(rep[0])); m = pd.read_csv(rep[0].replace("folds/fold1_next_report.json", "metrics/fold1_next_val.csv"))
        n_val = int(r["macro avg"]["support"]); mk = open(f"results/g2_ctle/{st}_f{F}/CTLE_FOLD.txt").read()
        assert f"fold={F}" in mk and "split_engine=check2hgi_dk_ovl" in mk
        rows.append(dict(state=st, fold=F, matched=r["macro avg"]["f1-score"] * 100, f1best=m.f1.max() * 100, june=june[F], n_val=n_val))
d = pd.DataFrame(rows); d["matched_minus_june"] = d.matched - d.june
d["rep_minus_f1best"] = d.matched - d.f1best; assert (d.rep_minus_f1best.abs() < 1e-4).all(), "report != f1-best epoch"
pd.set_option("display.width", 200); print(d.round(4).to_string(index=False))
out = {}
for st, g in d.groupby("state"):
    x = g.matched_minus_june.values
    out[st] = dict(matched_mean=g.matched.mean(), matched_sd=g.matched.std(ddof=1), june_mean=g.june.mean(), delta_mean=x.mean(), delta_sd=x.std(ddof=1),
                   t_p=stats.ttest_1samp(x, 0).pvalue, n_neg=int((x < 0).sum()))
    print(f"{st}: matched {g.matched.mean():.2f} ± {g.matched.std(ddof=1):.2f} vs June {g.june.mean():.2f}; delta {x.mean():+.2f} ± {x.std(ddof=1):.2f} (neg {int((x<0).sum())}/5, t p={out[st]['t_p']:.3f})")
d.to_csv("g1_logs/G2_CTLE_matched.csv", index=False); json.dump({k: {kk: float(vv) for kk, vv in v.items()} for k, v in out.items()}, open("g1_logs/G2_CTLE_matched_stats.json", "w"), indent=1)
