"""SHOULD-FIX: TOST equivalence + power for small-state region 'matches'.

Pre-registered (docs/studies/closing_data/v17_completion/STATISTICAL_PROTOCOL.md §3.2-3.3): δ_reg = 2 pp, paired,
report TOST p + 90% CI (1-2α, α=.05) on mean Δ; verdict = CI within (-2,+2).
Plus power to detect a true 2-pp gap given the board's variance.

Δ defined as MTL champion reg Acc@10 − STL dedicated reg ceiling, per fold (paired).
"""
import json, statistics as st
from scipy import stats

DELTA = 2.0   # pp equivalence margin
ALPHA = 0.05

def ceiling_perfold(path):
    d = json.load(open(path))
    pf = d['heads']['next_stan_flow']['per_fold']
    return [x['top10_acc'] * 100 for x in pf]

AL_ceil = ceiling_perfold('docs/results/P1/region_head_alabama_region_5f_50ep_alabama_ovl_stl_reg_s0.json')
AZ_ceil = ceiling_perfold('docs/results/P1/region_head_arizona_region_5f_50ep_arizona_ovl_stl_reg_s0.json')
IST_ceil = ceiling_perfold('docs/results/P1/region_head_istanbul_region_5f_50ep_istanbul_stride1_stl_reg_s0.json')

AL_mtl = json.load(open('docs/results/closing_data/h100/alabama_s0_mtl_fp32_matched_score.json'))['reg_per_fold']
AZ_mtl = json.load(open('docs/results/closing_data/h100/arizona_s0_mtl_fp32_matched_score.json'))['reg_per_fold']
IST_mtl = json.load(open('docs/results/second_dataset/istanbul/istanbul_stride1_s0_mtl_fp32_matched_score.json'))['reg_per_fold']


def tost_paired(mtl, ceil, label, delta=DELTA, alpha=ALPHA):
    d = [m - c for m, c in zip(mtl, ceil)]
    n = len(d)
    mean_d = st.mean(d)
    sd_d = st.stdev(d)
    se = sd_d / n ** 0.5
    df = n - 1
    # TOST: H0a: mu <= -delta (reject -> not worse by >delta);  H0b: mu >= +delta
    t_lower = (mean_d - (-delta)) / se
    p_lower = stats.t.sf(t_lower, df)            # P(T > t_lower) under boundary mu=-delta
    t_upper = (mean_d - (+delta)) / se
    p_upper = stats.t.cdf(t_upper, df)           # P(T < t_upper) under boundary mu=+delta
    p_tost = max(p_lower, p_upper)
    # 90% CI (1-2alpha)
    tcrit = stats.t.ppf(1 - alpha, df)
    ci_lo, ci_hi = mean_d - tcrit * se, mean_d + tcrit * se
    equivalent = (ci_lo > -delta) and (ci_hi < delta)
    # Power via seeded Monte Carlo at the board's variance (sigma = observed sd_d), n fixed.
    import numpy as np
    rng = np.random.default_rng(12345)
    N = 200000
    t_a = stats.t.ppf(1 - alpha, df)
    def equiv_rate(mu):
        x = rng.normal(mu, sd_d, size=(N, n))
        xbar = x.mean(1); s = x.std(1, ddof=1); se_h = s / n ** 0.5
        t_lo = (xbar + delta) / se_h
        t_hi = (xbar - delta) / se_h
        return float(np.mean((t_lo > t_a) & (t_hi < -t_a)))
    power_mu0 = equiv_rate(0.0)            # power to CONCLUDE equivalence if truly equal
    power_detect = 1 - equiv_rate(-delta)  # power to REJECT a true 2-pp deficit (not call it equiv)
    return dict(label=label, n=n, d=[round(x,3) for x in d], mean_d=round(mean_d,4),
                sd_d=round(sd_d,4), se=round(se,4),
                p_lower_noninf=round(p_lower,5), p_tost=round(p_tost,5),
                ci90=(round(ci_lo,3), round(ci_hi,3)),
                equivalent=equivalent, power_mu0=round(power_mu0,4),
                power_detect_2pp=round(power_detect,4))


for mtl, ceil, lab in [(AL_mtl, AL_ceil, 'AL'), (AZ_mtl, AZ_ceil, 'AZ'), (IST_mtl, IST_ceil, 'Istanbul(s0)')]:
    r = tost_paired(mtl, ceil, lab)
    print(r)

# board-variance reference: pooled per-fold sd of the paired diffs
print('\n--- pooled paired-diff SD (board variance) ---')
alld = [m-c for m,c in zip(AL_mtl,AL_ceil)]+[m-c for m,c in zip(AZ_mtl,AZ_ceil)]+[m-c for m,c in zip(IST_mtl,IST_ceil)]
print('pooled n=%d mean=%.3f sd=%.3f' % (len(alld), st.mean(alld), st.stdev(alld)))
