# v18 — METHODOLOGY

> What v18 is, why each piece is in it, and what was deliberately excluded. Charter:
> [`V18_AGENT_PROMPT.md`](V18_AGENT_PROMPT.md). Run started from commit `f281a709`.

## 1 · Definition

**v18 = the frozen v17 recipe, with the consecutive-visit leak fixed, plus elapsed-time node features.**

| component | what it is |
|---|---|
| **v17 recipe, unchanged** | same model, heads, optimizer, learning rates, epoch counts, selector, scorers. v18 is **not** an architecture change. |
| **forward-only check-in graph** | the canonical preprocessor emits *both* directions of every consecutive-visit edge. v18 keeps only `src < tgt`, in **training and at readout**. |
| **elapsed-time node columns** | 4 columns appended to the canonical 11 → `in_channels = 15`: log time since previous visit, log time since the user's first visit, same-day gap clipped at 24 h, first-visit indicator. All measured **up to the visit itself**. |

Built by `scripts/integrity_v2/build_study_repr.py --forward-only --add-continuous-time`, read out
by `infer_checkins.py --readout prefix_forward_only`, materialized into a normal engine directory
by `materialize_engine.py`. Representation seed **42**, 500 epochs, `resln` encoder, dim 64,
2 layers — one engine per state, shared by all four downstream seeds.

## 2 · Why forward-only

Under v17 a visit's vector is convolved over a neighbourhood that includes the visit **after** it, so
the category head sees a feature of the target it is being asked to predict. Measured at Alabama on
the reported dedicated model: withholding the target visit costs **28.63 macro-F1 points**
(56.86 → 28.23). The audit reproduced the published dedicated column (55.87 published seed-0 vs
56.86 in the audit), so the gap is a property of the substrate, not of a divergent harness.

**Expect the category numbers to fall a long way.** At Alabama the honest forward-only arm scores
about 28.3 where v17 reported about 56.9. That is the result, not a bug. A v18 category number
landing near its v17 value means the forward-only path is broken and must be investigated, not
reported (§6.6 of the charter; enforced automatically by `run_wave.sh`).

**Expect region to be essentially unchanged.** The region tower consumes region embeddings indexed
by historical places, which are per-region dataset constants, so the leak cannot reach it. At
Alabama the joint region result moved by +0.01 points under the strict readout. A region move
greater than 2 pp is also a signal to investigate.

## 3 · Why elapsed time, and what was excluded

Measured at Alabama on the dedicated protocol against the forward-only baseline of **27.5127**:

| variant | macro-F1 | vs forward-only |
|---|---:|---:|
| **elapsed time** (the only gain) | **28.3461** | **+0.83** |
| region, standardized, projected to 8 | 26.9601 | −0.55 |
| place, standardized, projected to 8 (best place arm) | 27.1047 | −0.41 |
| place, standardized, full 64 | 25.7683 | −1.74 |
| place, raw 64 (worst) | 25.6506 | −1.86 |

**Mechanism.** A spatial block the graph can already anticipate from a node's neighbourhood becomes
a shortcut for the pretext discriminator, whose negatives are row-permuted node features — so
"real or shuffled?" becomes answerable from that block alone. The pretext loss collapses
(0.2112 → 0.064 with region, → 0.088 with raw place) while downstream accuracy falls. Elapsed time
is the one tested feature barely above chance in neighbourhood predictability, which is the working
explanation for why it is the only one that helps.

**One honest caveat, recorded as unexplained:** that account does not explain why region collapses
the objective *harder* than place, since place has the higher predictability lift.

**Also excluded — settled, re-running them is waste:** encoder width sweeps at 32/64/128 and depth
sweeps at 1/2/3/4 found 64 and 2 at or near optimum, with one layer equal to three within 0.014
points. Output width 64 is a hard constant in three places (the encoder, the Delaunay place-table
anchor's fixed 64-d distillation target, and the downstream head's configured embedding dimension).

## 4 · The experiment matrix

6 datasets × 4 seeds `{0, 1, 7, 100}` × 5 folds = **n = 20 per cell**, three families per cell.

| family | command | scorer | metric |
|---|---|---|---|
| **(a) dedicated cat** | `train.py --task next --model next_gru --embedding-dim 64` | `score_stl_cat_ceiling.py` | macro-F1 at the f1-best epoch, fold-mean |
| **(b) dedicated reg** | `p1_region_head_ablation.py --heads next_stan_flow --input-type region` | the P1 JSON | `top10_acc_mean × 100` |
| **(c) joint (v17 MTL)** | `train.py --task mtl --canon none` | `a40_score_matched.py` + `score_joint_best.py` | cat macro-F1 at f1-best; reg `top10_acc_indist × (1 − ood_fraction) × 100` at indist-best — **Acc@10** |

Per-state dedicated-category recipe (`CEILINGS_N20_FINAL.md`; Istanbul per `h3_istanbul/run_step3_n20.sh:43`):

| tier | states | recipe |
|---|---|---|
| small | alabama, **istanbul** | `--batch-size 2048 --max-lr 0.005` |
| large | arizona, florida, california, texas | `--batch-size 8192 --max-lr 0.005` |

The region family runs with the prior **OFF** (`freeze_alpha=True alpha_init=0.0`), so `log_T` is
inert and `--per-fold-transition-dir` is omitted — parity validated at Alabama (no-dir 70.00 vs
board 69.99).

Both epoch-selection conventions are reported: **diag-best** (the Table-3 convention) and
**joint-best** (`geom_simple`, `min_best_epoch=0` — the single served checkpoint). Never compare one
against the other without flagging it; see [`../JOINT_BEST_SCORING.md`](../JOINT_BEST_SCORING.md).

## 5 · Deliberate deviations from the charter's abbreviated command

The charter's §3 joint command omits two things that **every published v17 comparand used**
(`a1_catx/run_a1_catx_n20.sh`, `h3_istanbul/run_step3_n20.sh`, `perhead_lr_n20.md`). Both are
restored here, because differencing v18 against v17 across a protocol boundary would violate the
charter's own §10 rule:

1. **fp32** — `MTL_DISABLE_AMP=1`. Not optional on this A40: bf16 backward grad-NaNs at CA/TX class
   counts (C ≈ 6.5–8.5 k) and fp16 overflows at large reg logits. The whole v17 board is fp32.
2. **`--compile --tf32`** plus `MTL_CHUNK_VAL_METRIC=1 MTL_STRICT=1 MTL_COMPILE_DYNAMIC=1`. Confirmed
   by the author 2026-08-06: match the published MobiWac results.

   ⚠ **Corrected 2026-08-11.** This paragraph used to inherit `CLAUDE.md`'s general warning that
   compiled numbers are "within-fold-std but **not** bit-reproducible". **That does not hold for
   v18 on this box, and it was measured, not assumed:** eight same-recipe / different-inductor-cache
   pairs reproduce **exactly** — four alabama joint pairs (`mtlAL_r3_*` vs `mtl_alabama_*`,
   identical means, per-fold arrays *and* best-epoch indices), the alabama `mla_*` vs board joint
   pair, the alabama s1 cat parity check, and the istanbul region parity run. The one non-zero
   observation (arizona region, +0.004478) was traced to a **code change**, commit `aab23985`
   (`MTL_SKIP_INERT_PRIOR`, default ON): with the skip off, a fresh session reproduces the 08-06
   banked cell bit-for-bit on all five folds — see [`inert_prior_ab/`](inert_prior_ab/).

   So on v18 the compile session is **not** a source of variation worth reasoning about. The real
   limiter is **seed variance** (0.02–0.12 pp on Δcat), which is 4–25× larger. `CLAUDE.md`'s warning
   was written for a different recipe and substrate (the v16 champion at AL) and still stands there;
   it should not be carried into v18 claims. Full record in [`log.md`](log.md) under the retraction
   entry.

Two further scheduling deviations, which change wall-clock only and no measured value:

3. **Large states run 1-wide**, not 2-wide. `catx_v17_seed0_5f/RESULTS.md` records 2-wide as
   infeasible for CA/TX: each MTL dataset build peaks ~66 GB **host** RAM on this shared 125 GB box.
   (The charter's ~21 GB figure is GPU-side and correct.) Small states run 2-wide.
4. **The v18 engine is materialized from the one-shot full-graph export**, not from the per-window
   `prefix_forward_only` npz. On a forward-only graph the two are the same to float32 round-off
   (verified over *every* window at three states: max 2.4–3.1e-06 on embeddings of scale ~1.05,
   with slot 8 — the truncation boundary — no worse than slot 0), because messages flow strictly
   past → future and a visit's vector cannot depend on anything after it. This cuts FL/CA/TX Phase 0
   from ~17 h of single-threaded CPU to seconds, and changes no downstream number. Full evidence and
   the reproduction commands: [`READOUT_EQUIVALENCE.md`](READOUT_EQUIVALENCE.md). The shortcut is
   **invalid for bidirectional arms** and `materialize_from_insample.py` hard-fails on them.
5. **Alabama's representation was not rebuilt.** Study cell `E2` is bit-for-bit this definition
   (`--forward-only --add-continuous-time`, seed 42, 500 ep, resln, dim 64, 2 layers, all users,
   `self_test: true`); the v18 engine was materialized from its existing npz. Provenance in
   [`PROVENANCE.md`](PROVENANCE.md).

## 6 · Honesty rules in force

- Every number carries its convention: metric, selector, and `n = seeds × folds`.
- Never compare across protocols. If a baseline is needed, it is measured on the same protocol.
- "Outperforms" requires a paired superiority test; "matches" requires TOST non-inferiority within
  the stated margin. A non-inferior result is never upgraded to a win.
- Report what was measured, not what was expected. If v18 is worse than v17 on category, that **is**
  the result, and it is the honest one.
