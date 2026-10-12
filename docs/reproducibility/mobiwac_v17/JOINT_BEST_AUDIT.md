# AUDIT — independent verification of the J1 joint-best re-score

> Four independent verifier agents, each reading the A40 rundirs directly, all returned **CONFIRMED** with
> **no material discrepancies**. This is on top of the three self-audits built into the scorer
> (`JOINT_BEST_RESULTS.md §Audit`: diag-best parity 18/18, joint-epoch fidelity 90/90, paper parity 6/6).
> Workflow: `wf_8392161a-943` (5 agents, 0 errors, 315k subagent tokens).

## 1 · Independent re-derivation (no scorer, no `scoring.py`) — CONFIRMED
A verifier re-implemented joint-best from scratch (stdlib-only python, own argmax over
`sqrt(f1·top10_acc_indist)`, ties→earliest) for AL s0, AL s1, Istanbul s0, TX s0, FL s0. **Every per-fold cat
and reg matched the sidecar bit-identically to 4 dp**, every picked `e*` equalled the sidecar `epochs[]`, and the
AL s0 fold-1 cross-check held (`primary_checkpoint.epoch` 35 +1 = 36 = e\*). The independent `selector_per_fold`
reproduced the sidecar exactly → confirms the selector uses `top10_acc_indist` (in-distribution), not full-top10.
→ **The scorer's logic is independently reproduced; not trusting a single implementation.**

## 2 · AL region tail-risk (the runbook's flagged risk) — CONFIRMED, risk did NOT materialize
The J1 runbook warned AL region could approach the −2 pp TOST bound (a legacy smoke run once saw −1.16 pp).
Actual v17 board result over the 4 AL seeds:
- n=20 joint-best AL reg = **69.695** (cross-seed sd 0.10); diag-best 69.80. **Joint selector penalty = −0.105 pp.**
- Δ vs ceiling 70.11: **−0.415** (joint) vs −0.310 (diag). **1.585 pp of margin remaining** to the −2 pp bound.
- **No fold collapse:** all 20 joint epochs 34–49 (min 34); diag reg-best epochs 27–48 (min 27); none ≤ 5.
- **Worst single-fold joint−diag reg drop = −0.29 pp** (s1 f4) — nowhere near the −1.16 legacy fear.
→ **AL stays a comfortable within-2-pp match under joint-best.**

## 3 · Istanbul / FL region "beats" sensitivity — CONFIRMED, direction preserved (and per-fold robust)
The joint-best point estimate is lower, so the up-arrow cells were stress-tested:
- Istanbul n=20 joint-best reg **75.352** vs ceiling 75.16 → **Δ +0.192** (diag +0.28; thins ~31% relative but **positive**).
- FL n=20 joint-best reg **77.410** vs ceiling 76.70 → **Δ +0.710** (diag +0.72; essentially unchanged).
- **Per-fold paired evidence (the strong result):** joint-best MTL reg beats the STL reg ceiling in **20/20 folds**
  at BOTH states — Istanbul paired diff mean +0.194 (min +0.074, sd 0.082); FL mean +0.712 (min +0.560). A formal
  Wilcoxon/90%-CI would still reject strongly. **Flip risk LOW even at the thinned Istanbul margin.**
- Ceilings independently re-derived from the per-fold JSONs: 75.158 / 76.697 (match 75.16 / 76.70).
- **Metric-definition note for the camera-ready stat (T7):** the MTL side reports FULL top10 = `top10_indist·(1−ood)`
  while the STL ceiling per-fold JSONs report plain `top10_acc` (ood=None). The board's diag headline already pairs
  them this way, and MTL beats in 20/20 folds even under the *conservative* FULL metric — but the formal test should
  confirm both sides use an identical top10 definition. Ceiling per-fold data:
  `docs/results/P1/region_head_{istanbul,florida}_region_5f_50ep_*_ovl_stl_reg_s{0,1,7,100}.json` (FL {1,7,100}
  carry a `_topup_` infix); MTL side = `<rundir>/joint_best_score.json → joint_best.reg_per_fold`.

## 4 · Completeness critic — CONFIRMED, scope correct
- All 6 "Joint (ours)" cells map to the correct v17/`dk_ovl` rundirs (AL/AZ/FL/Istanbul n=20; CA/TX seed-0 5f);
  all 18 rundirs complete (5 folds, paired CSVs), each now carrying both `a40_matched_score.json` and the new sidecar.
- **FL uses the `new` bs8192 per-head runs** (diag cat 79.848 = paper 79.85), not the bs2048 `base`.
- **Recipe verified v17** from `model_params.json`: bs 8192, OneCycle per-head max_lr cat 1e-3 / reg 3e-3 / shared
  3e-3 (per-head LR APPLIED, not uniform), static_weight 0.75/0.25, AdamW wd 0.05.
- **CA/TX A1 (n=20) genuinely incomplete on disk *at audit time*:** only a dead CA seed-1 attempt (rundir 742357,
  4/5 folds, no sidecar) existed; no CA s7/s100, no TX seeds. `a1_DRIVER.log` showed A1 launched only CA s1
  (2026-07-08 19:14) then stopped. → CA/TX correctly stayed **seed-0 5f provisional** for this joint-best re-score.
  **UPDATE: A1 has since completed 2026-07-11 on the A40** (CA/TX v17 MTL n=20, `docs/results/closing_data/catx_v17_n20/`);
  the n=20 diag-best confirms the seed-0 values within <0.13 pp. The *joint-best* n=20 re-score (task T6) is now
  unblocked (CPU-only) but not yet run, so the seed-0 joint-best cells above stand until it is.
- **STL "Dedicated" ceilings need no joint-best re-score** — a single-task checkpoint is picked on that task's own
  metric = its diag-best (joint-best == diag-best by construction; `score_joint_best.py` can't even run on an STL
  rundir, it requires paired cat+reg CSVs).
- Two non-cell CA rundirs correctly excluded from the CA cell: `1342525` (1-fold audit), `742357` (dead A1 s1).

## Forward-looking notes (not defects — for camera-ready / response-letter)
1. **The §6.2 hidden response-letter note is now STALE.** `articles/[mobiwac]/src/sections/06_results.tex`
   (lines ~88–93) says the joint-checkpoint numbers "were not re-scored for the paper … do NOT claim they match."
   J1 has now re-scored them: they land 0.00–0.11 pp below the diag-best cells. When the response letter lands,
   update the note to cite the actual joint-best numbers (they *confirm* the reported cells, within 0.1 pp).
2. **If joint-best is ever RENDERED in place of a diag-best cell**, re-verify TOST/CI on the three thin reg cells
   only (AL −0.42, Istanbul +0.19, AZ −0.00); every cat beat and the FL/TX/CA reg ↑ are safe (task T7).
3. **CA/TX at n=20** (task T6) is the only genuinely open item. The A1 GPU top-up it depended on is **done
   (2026-07-11, A40)** — so T6 is now a CPU-only re-score (re-run T2 `score_joint_best.py` on the CA/TX n=20 rundirs),
   no longer GPU-blocked. The n=20 diag-best already confirms the seed-0 cells within <0.13 pp.
