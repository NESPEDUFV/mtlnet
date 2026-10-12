"""G2 IST: CTLE category macro-F1 under the MATCHED split vs the June board cell."""
import json, glob, numpy as np, pandas as pd
from scipy import stats
G2 = "/Users/vitor/g2_scratch"; R = "/Users/vitor/Desktop/mestrado/ingred/docs/results/closing_data/baseline_compare"
june = {d["fold"]: d["macro_f1"] for d in json.load(open(f"{R}/istanbul_ctle.json"))["per_fold"]}
rows = []
for F in range(5):
    rep = glob.glob(f"{G2}/results/istanbul_f{F}/run/check2hgi_ctle/istanbul/*/folds/fold1_next_report.json"); assert len(rep) == 1, (F, rep)
    r = json.load(open(rep[0])); m = pd.read_csv(rep[0].replace("folds/fold1_next_report.json", "metrics/fold1_next_val.csv"))
    mk = open(f"{G2}/results/istanbul_f{F}/CTLE_FOLD.txt").read(); assert f"fold={F}" in mk and "split_engine=check2hgi_dk_ovl" in mk
    rows.append(dict(fold=F, matched=r["macro avg"]["f1-score"] * 100, f1best=m.f1.max() * 100, june=june[F], n_val=int(r["macro avg"]["support"])))
d = pd.DataFrame(rows); d["matched_minus_june"] = d.matched - d.june; assert (abs(d.matched - d.f1best) < 1e-4).all()
print(d.round(4).to_string(index=False)); x = d.matched_minus_june.values
print(f"istanbul: matched {d.matched.mean():.2f} ± {d.matched.std(ddof=1):.2f} vs June {d.june.mean():.2f}; delta {x.mean():+.2f} ± {x.std(ddof=1):.2f} (neg {int((x<0).sum())}/5, t p={stats.ttest_1samp(x,0).pvalue:.3f})")
d.to_csv(f"{G2}/G2_CTLE_matched_istanbul.csv", index=False)
