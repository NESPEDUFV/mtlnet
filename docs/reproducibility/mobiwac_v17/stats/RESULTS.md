# M1-FULL — v17 pre-registered stats vs the n=20 best-vs-best ceilings (rev 4, 2026-07-13)

> ✅ **M1-FULL (rev 4, 2026-07-13) — A1 landed CA/TX v17 MTL n=20 (2026-07-11); the pre-registered
> 6-dataset family Holm now runs.** Re-run `m1_stats_n20.py` (§5 appended; full log `m1_full_output.txt`).
> All artifact→board reproduction gates pass, incl. the new CA/TX n=20 (CA cat 77.052/reg 65.693,
> TX cat 77.239/reg 67.062). **Result — the 6-dataset cat-superiority family Holm ALL REJECT @ α=0.05:**
>
> | dataset | Δcat (pp) | paired t(3) p | Holm-adj (m=6) | reject |
> |---|---:|---:|---:|:--:|
> | AL | +7.73 | 4.5e-07 | 8.9e-07 | ✅ |
> | AZ | +9.40 | 2.1e-07 | 8.9e-07 | ✅ |
> | FL | +5.34 | 4.2e-09 | 2.5e-08 | ✅ |
> | Istanbul | +8.59 | 1.8e-07 | 8.9e-07 | ✅ |
> | **CA** | **+6.45** (4/4) | 3.8e-07 | 8.9e-07 | ✅ |
> | **TX** | **+7.45** (4/4) | 2.5e-07 | 8.9e-07 | ✅ |
>
> **MTL beats the dedicated category ceiling at every dataset** (Holm-adj ≤ 8.9e-07). Reg (per-axis δ=2 pp):
> matches at AL/AZ, **beats** at FL/CA/TX/Istanbul — CA reg Δ+2.20 (90% CI +2.193…+2.215, entirely above +δ;
> superiority t(3) p=1.0e-08), TX reg Δ+2.11 (superiority t(3) p=1.4e-07). The n=20 **CONFIRMS** the seed-0
> provisional verdicts (§3) — **no verdict changed.** The seed-level test is n=4-paired (per protocol §8's
> powered-t deviation; the exact-Wilcoxon floor is 0.0625 at n=4). The PROVISIONAL/M1-PARTIAL material below is
> retained for the record.

---

## (superseded) M1-PARTIAL — rev 3, 2026-07-08

> ⚠ **This is M1-PARTIAL.** The fully-n=20 family covers **AL, AZ, FL, Istanbul** (ceilings per
> [`../CEILINGS_N20_FINAL.md`](../CEILINGS_N20_FINAL.md), **AZ ceiling = 56.43, the corrected
> bs8192@0.005 arm**). **CA/TX MTL n=20 is pending A1** (A40); rev 3 adds CA/TX **PROVISIONAL**
> verdicts at the per-fold **seed-0 (n=5)** footing (§1b) — their **STL ceilings ARE n=20**; only
> the MTL side is seed-0. The paper's headline family is 6 datasets (protocol §5.2) — **the full
> 6-dataset family Holm re-runs after A1**; everything here is the pre-registered analysis of the
> committed artifacts, not the final family verdict.
>
> **rev 2 (2026-07-08):** A0 (`c51b1183`) committed the AL/AZ/FL v17 MTL per-seed values
> (`train_perf_multifold/n20_perhead_runs/summary.tsv`) → the AL/AZ/FL cells flip from PENDING to
> tested at the **seed-level (n=4)** footing, same as Istanbul. All four datasets now carry verdicts.
> **rev 3 (2026-07-08):** CA/TX added as **PROVISIONAL n=5** (seed-0, per-fold paired; exact
> Wilcoxon floor 0.0312) — both sides have committed per-fold seed-0 vectors. Superseded by A1's
> n=20; NOT folded into the m=4 Holm family (§1b).
>
> Pre-registration: [`../STATISTICAL_PROTOCOL.md`](../STATISTICAL_PROTOCOL.md) (§2 cat
> superiority → paired one-sided Wilcoxon; §3 reg → TOST non-inferiority at **δ_reg = 2 pp**;
> §4 pairing discipline; §5.2 Holm on the cat family only; §8 deviation log). Test conventions
> mirror `research/reproducibility/mobiwac_v17/superiority_wilcoxon.py` + `region_match_tost.py`.
>
> Reproduce: `.venv/bin/python research/reproducibility/mobiwac_v17/m1_stats_n20.py`
> (reads ONLY committed artifacts; aborts if any recomputed aggregate stops matching the board).

## 0 · Artifact → board reproduction gate (16/16 PASS)

Every board number used below was recomputed from the committed artifacts before testing:
STL cat ceilings AL 56.815 / AZ 56.435 / FL 74.509 (`../data/cat_ceiling_sweep/sweep_results/` per-fold
JSONs, 4 seeds × 5 folds); STL reg ceilings AL 70.111 / AZ 59.459 / FL 76.697 / Istanbul 75.158
(`docs/results/P1/region_head_*_ovl_stl_reg_{s0,topup_s{1,7,100}}.json` per-fold arrays); **v17 MTL
AL 64.540/69.801, AZ 65.835/59.563, FL 79.848/77.421 (the A0 `summary.tsv` per-seed rows, `recipe=new`
= the bs8192 + per-head cat-lr 1e-3 v17 arm — the FL `recipe=base` bs2048 anchor rows are excluded)**;
Istanbul MTL 63.329/75.440 + cat ceiling 54.738 (`../data/h3_istanbul/step3_runs/*.txt`). All match
`CEILINGS_N20_FINAL.md` / `perhead_lr_n20.md` to rounding.

## 1 · Per-dataset results — the fully-n=20 family (AL/AZ/FL/Istanbul)

Δ orientation = **MTL − STL ceiling** (positive = MTL better). δ_reg = 2 pp (pre-registered, §3.2).
**Pairing level for every cell in THIS section: SEED-LEVEL paired, n=4** — each observation is a
per-seed 5-fold mean, paired by seed {0,1,7,100} across arms sharing the frozen fold construction
(§4). Per-fold (n=20) pairing is not yet possible from the committed tree (LIMITS #2). CA/TX are in
§1b (different footing — keep them separate).

### Category — superiority (MTL > dedicated STL cat ceiling)

| Dataset | Δcat (pp) | pairs+ | Wilcoxon p (exact, 1-sided) | paired t(3) p (1-sided) | Holm-adj p (m=4, on t) | Verdict |
|---|---:|---|---|---|---|---|
| **AL** | **+7.73 ± 0.12** | 4/4 | 0.0625 (= n=4 floor) | 4.5e-07 (≈67 σ_d) | **5.3e-07** ✓ | **outperforms** |
| **AZ** | **+9.40 ± 0.11** | 4/4 | 0.0625 (= n=4 floor) | 2.1e-07 (≈87 σ_d) | **5.3e-07** ✓ | **outperforms** |
| **FL** | **+5.34 ± 0.02** | 4/4 | 0.0625 (= n=4 floor) | 4.2e-09 (≈320 σ_d) | **1.7e-08** ✓ | **outperforms** |
| **Istanbul** | **+8.59 ± 0.09** | 4/4 | 0.0625 (= n=4 floor) | 1.8e-07 (≈92 σ_d) | **5.3e-07** ✓ | **outperforms** |

All four survive Holm at α = 0.05 on the paired-t footing (see deviation log — at n=4 the exact
Wilcoxon is floor-limited at 0.0625 for **any** effect size, so the pre-registered Wilcoxon itself
cannot clear α until the per-fold n=20 vectors land).

### Region — TOST non-inferiority (δ_reg = 2 pp; equivalence cells, NOT in the cat Holm family per §5.2)

| Dataset | Δreg (pp) | TOST p | 90 % CI (pp) | Verdict |
|---|---:|---|---|---|
| **AL** | **−0.31 ± 0.15** | 8.8e-05 | (−0.482, −0.139) ⊂ ±2 | **matches (TOST)** |
| **AZ** | **+0.10 ± 0.09** | 1.3e-05 | (+0.001, +0.206) ⊂ ±2 | **matches (TOST)** (CI ≥ 0 but grazes it — do NOT upgrade to "beats"; supplementary superiority t p = 0.049, marginal) |
| **FL** | **+0.72 ± 0.04** | 5.8e-06 | (+0.671, +0.776) ⊂ ±2 | **matches (TOST)** — CI entirely > 0, descriptively **beats** (suppl. t p = 3.2e-05) |
| **Istanbul** | **+0.28 ± 0.04** | 1.2e-06 | (+0.240, +0.323) ⊂ ±2 | **matches (TOST)** — CI entirely > 0, descriptively **beats** (suppl. t p = 2.7e-04) |

**Per-seed Δs (seeds 0/1/7/100)** — cat: AL [+7.73, +7.88, +7.60, +7.69], AZ [+9.40, +9.41, +9.26,
+9.53], FL [+5.32, +5.34, +5.33, +5.36], Istanbul [+8.61, +8.47, +8.59, +8.70]; reg: AL [−0.13,
−0.46, −0.39, −0.26], AZ [+0.23, +0.03, +0.05, +0.11], FL [+0.68, +0.71, +0.72, +0.78], Istanbul
[+0.25, +0.31, +0.25, +0.32].

### Deviation log (protocol §8)

1. **Seed-level pairing (n=4) instead of the pre-registered per-fold n=20.** The committed MTL sides
   are per-seed 5-fold means (A0 `summary.tsv`; Istanbul step3 txts) — the per-fold matched-score
   sidecars remain A40-only (LIMITS #2). Seed-level pairing is valid (§4: same frozen folds, same
   seed set); no per-fold values were fabricated, nothing pooled unpaired.
2. **Paired t reported alongside the pre-registered Wilcoxon.** At n=4 the exact one-sided Wilcoxon's
   minimum attainable p is 1/2⁴ = **0.0625 > α** — a power ceiling (the n=4 analogue of §2's n=5
   note): all four cat cells sit exactly at the floor with 4/4 positive. The paired t (df=3) is the
   powered seed-level test; with effects of 67–320 σ_d the verdicts do not hinge on distributional
   fine print. The per-fold n=20 Wilcoxon (the pre-registered test proper) runs when the sidecars
   are pulled.
3. **Holm applied to the paired-t family** (m=4: AL/AZ/FL/Istanbul cat superiority) — on the Wilcoxon
   footing the whole family is floor-locked (best possible Holm-adj = 4 × 0.0625 = 0.25), so the
   correction is reported on the t p-values; all four reject at FWER 0.05 (smallest margin: adj
   p = 5.3e-07).

## 1b · CA / TX — seed-0 paired analysis (✅ **A1 n=20 now COMPLETE — supersede via M1-full re-run**)

> ✅ **A1 DONE 2026-07-11** — CA/TX v17 MTL is now **n=20** (`docs/results/closing_data/catx_v17_n20/`; means
> CA cat 77.052 ±0.006 / reg 65.693 ±0.017, TX cat 77.239 ±0.014 / reg 67.062 ±0.007). The n=20 **confirms** the
> provisional seed-0 verdicts below with tight cross-seed variance (all four cells still beat their n=20 ceilings:
> CA +6.45/+2.20, TX +7.45/+2.11). **The seed-0 paired tests below are retained as the provisional footing; the
> M1-FULL step is to re-run `m1_stats_n20.py` on the CA/TX n=20 per-fold vectors** (now extractable from the A1
> rundirs) so the 6-dataset family Holm runs at full n=20 and the PROVISIONAL/M1-PARTIAL banners lift. The verdicts
> are not expected to move (the n=20 means match seed-0 to <0.13 pp).

**Footing (state it precisely):** the **cited ceiling means stay the n=20 values** (CA cat 70.60 /
reg 63.49; TX cat 69.79 / reg 64.95 — `CEILINGS_N20_FINAL.md`); the **paired tests below use the
seed-0 fold vectors of those same ceiling runs** (cat: `../data/cat_ceiling_sweep/sweep_results/
{california,texas}_bs8192_lr0.005_s0.json`; reg: `docs/results/P1/region_head_{california…ca,texas…tx}
_ovl_stl_reg_s0.json`), fold-k paired with fold-k at seed 0 (same frozen fold construction, §4).
MTL side = `../data/catx_v17_seed0_5f/` — the matched-scorer per-fold arrays are **parsed from that
RESULTS.md** (the only committed carrier: `summary.tsv` has fold-means only, and `profile.json`'s
`quality.next_region` is a different, non-ood-corrected capture; its `quality.next_category` DOES
reproduce the cat arrays exactly and is used as an in-script cross-check). Exact one-sided Wilcoxon
floor at n=5 = **0.0312** (5/5 positive = at-ceiling, per §2's single-seed note). **These two cells
are NOT in the §1 Holm family** — the pre-registered 6-dataset family Holm runs after A1.

| Dataset | Cell | Δ (pp, seed-0 footing) | folds+ | Wilcoxon p (exact) | paired t(4) p | Verdict (PROVISIONAL) |
|---|---|---:|---|---|---|---|
| **CA** | cat | **+6.31 ± 0.17** | 5/5 | 0.0312 (= n=5 floor) | 5.9e-08 | **outperforms** (provisional) |
| **CA** | reg | **+2.21 ± 0.07** | 5/5 | 0.0312 (= n=5 floor) | 1.5e-07 | **beats** (provisional) — 90 % CI (+2.14, +2.28) entirely ABOVE +δ: exceeds the 2-pp margin in the favorable direction; TOST non-inferiority trivially holds (p = 1.1e-08); two-sided equivalence n/a (better than the margin) |
| **TX** | cat | **+7.31 ± 0.40** | 5/5 | 0.0312 (= n=5 floor) | 1.0e-06 | **outperforms** (provisional) |
| **TX** | reg | **+2.11 ± 0.07** | 5/5 | 0.0312 (= n=5 floor) | 1.4e-07 | **beats** (provisional) — 90 % CI (+2.04, +2.18) entirely ABOVE +δ; TOST non-inferiority trivially holds (p = 9.6e-09); two-sided equivalence n/a |

Per-fold Δs (seed 0, folds 0–4) — CA cat [+6.48, +6.46, +6.24, +6.31, +6.08], CA reg [+2.15, +2.11,
+2.27, +2.24, +2.26]; TX cat [+7.31, +7.50, +6.63, +7.59, +7.52], TX reg [+2.14, +2.18, +2.13,
+2.00, +2.10]. **Correction (2026-07-27, claim-neutral).** This paragraph previously said the reg
cells "land in the pre-registered reg-**superiority** family (`superiority_wilcoxon.py` pins FL/CA/TX
as 'the beats')" and inferred that superiority was "the apt primary there". **No such family is
pre-registered.** The protocol pins next-region to non-inferiority only: §1's family-(A) row reads
"reg: **non-inferiority** (MTL not worse than STL by more than δ_reg)" with "reg → **TOST** (§3)",
and §5.2 fixes the headline family as "{6 states} × {cat superiority, reg non-inferiority}" with the
TOST cells "not pooled into the cat Holm family". `superiority_wilcoxon.py` is a script, not the
registration — and it was first committed (`1e3449e6`, 2026-06-25) **after** the FL/CA (2026-06-22)
and TX (2026-06-24) region ceilings were readable. **The registered primary test for every reg cell,
CA/TX included, is TOST non-inferiority at δ_reg = 2 pp.** The reg superiority statistics in the
table above are **post-hoc** and reported as such (deviation of record:
[`../DEVIATIONS.md`](../DEVIATIONS.md) entry **D-4**, 2026-07-25 — they now carry their own Holm family, m=4,
and are labeled secondary results in the paper and in dissertation Ch.5). Both tests stay reported
here; what changes is which one is registered. **No number in this file moved.** The seed-0-footing
Δcat (+6.31/+7.31)
differs from the board Δ (+6.44/+7.44) exactly because the board Δ subtracts the **n=20** ceiling
mean while the paired vectors are seed-0 (seed-0 ceiling ≈ +0.12/+0.13 above the n=20 mean).

## 2 · LIMITS (honest gaps — read before citing)

1. **CA/TX MTL n=20 is now DONE (A1, 2026-07-11)** — the provisional risk that sat on the seed-0 MTL
   side is resolved: n=20 means confirm seed-0 to <0.13 pp (CA cat 77.052/reg 65.693, TX cat 77.239/
   reg 67.062). ⏳ **Remaining (M1-full compute, not a doc edit):** re-run `m1_stats_n20.py` on the CA/TX
   n=20 per-fold vectors (extract from the A1 rundirs) → the 6-dataset family Holm at full n=20, which
   **lifts the M1-PARTIAL banner + the §1b PROVISIONAL labels**. Verdicts not expected to move.
2. **All §1 cells are seed-level (n=4), not per-fold (n=20).** Still missing from the committed tree
   (A40 gitignored rundirs):
   - AL/AZ/FL: the per-PID `a40_score_matched.py` sidecar JSONs (tags `n20ph_{state}_{recipe}_s{seed}`,
     `cat_per_fold`/`reg_per_fold` arrays) inside
     `results/check2hgi_dk_ovl/{state}/mtlnet_*bs8192_ep50_*_{pid}/`;
   - Istanbul: the `h3ist_mtl_s{S}` sidecars + the cat-ceiling `stl_cat_ceiling_score.json` per rundir.
   Pulling those upgrades every cell to the pre-registered per-fold n=20 Wilcoxon/TOST (which breaks
   the Wilcoxon floor, §2). ~~Prior gap: AL/AZ/FL per-seed values not committed~~ — **closed by A0
   (`c51b1183`,** `n20_perhead_runs/summary.tsv`**)**.
   ✅ **CLOSED 2026-07-25 on the joint-best convention.** The MTL per-fold arrays are committed for all six
   datasets (`joint_best/data/j1_results.json` `per_run[].jb_{cat,reg}_folds`; CA/TX at
   `docs/results/closing_data/catx_v17_n20/joint_best/`), and the last dedicated-side gap, **Istanbul's
   per-fold category ceiling**, was recovered from the A40 and committed at
   [`../data/h3_istanbul/step3_runs/cat_ceiling_perfold/`](../data/h3_istanbul/step3_runs/cat_ceiling_perfold/)
   (tags `h3ist_cat_s{0,1,7,100}`; per-seed means reproduce `cat_ceil_s*.txt` exactly, so the board cell
   54.74 is unchanged and no retraining was needed). **The pre-registered per-fold n=20 Wilcoxon now runs at
   all six datasets** — see [`m2_prereg_perfold.py`](m2_prereg_perfold.py) /
   [`m2_prereg_output.txt`](m2_prereg_output.txt): the six-dataset cat family Holm (m=6) **ALL REJECT**,
   worst adjusted p = 5.72e-06, every cell at the exact n=20 floor 9.54e-07 with 20/20 folds positive; the
   four reg-superiority cells reject in their own m=4 family (adjusted 3.81e-06). **No verdict changed and
   no reported estimate moved.** The seed-level (n=4) tests below remain the paper's reported footing (the
   region CIs are computed on it); the registered test is now reported alongside them.
3. **The STL sides are fully committed at n=20 per-fold** (cat: sweep JSONs at AL/AZ/FL; reg: P1
   JSONs at all four) — but they are consumed here as per-seed means to match the MTL side's
   granularity (pairing must be at a common footing).
4. **Wilcoxon at n=4 is floor-limited** (min p = 0.0625) — reported per cell, with the paired t as
   the powered sensitivity test (deviation log #2). Resolved automatically once per-fold vectors land.
5. **AZ reg**: the 90 % CI lower bound is +0.001 — non-inferiority is comfortable, but any "beats"
   phrasing at AZ is unsupported (supplementary superiority p = 0.049, at the boundary). The board's
   "≈matches" wording is exactly right.

## 3 · Bottom line (M1-partial)

- **At all 4 fully-n=20 datasets, the v17 champion beats the dedicated category ceiling (Δcat
  +5.3…+9.4 pp; seed-level paired t, every cell Holm-corrected p < 1e-6 at FWER 0.05) and is TOST
  non-inferior on region at δ_reg = 2 pp (every 90 % CI within ±2; AL the only negative point
  estimate at −0.31, bounded above −0.5).** FL and Istanbul additionally beat the region ceiling
  descriptively (CIs entirely positive); AZ grazes zero — keep it "matches."
- **CA/TX (PROVISIONAL, seed-0 n=5): the same signature, stronger on reg** — cat outperforms
  (+6.31/+7.31, 5/5 folds, Wilcoxon at the n=5 ceiling 0.0312, t p ≤ 1e-06) and reg **beats by more
  than the 2-pp margin** (90 % CIs entirely above +2). Superseded by A1's n=20.
- **The pre-registered per-fold n=20 tests remain the citation-grade target** — pending the A40
  sidecar pull (LIMITS #2) and A1 for CA/TX; then the full 6-dataset Holm family replaces this
  partial.
