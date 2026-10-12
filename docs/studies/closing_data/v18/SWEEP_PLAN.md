# v18 — re-tuning sweep: test register and execution order

> **Why this exists.** The v18 category recipe was inherited from the **leaked** substrate. Both arms
> peak early and the baseline is not a ceiling by the study's own standard. This file is the running
> register of every sweep arm, its order, and its status, so the work is not lost between sessions
> and so we can return to the evaluation waves afterwards.
>
> Status legend: ⬜ queued · 🔄 running · ✅ done · ❌ failed · ⏭ skipped
>
> **All arms fp32 on both models** (user decision 2026-08-07), `--compile --tf32`, 5 folds,
> engine `check2hgi_v18`, per-command `env` (never a bare `export` — see
> [`PRECISION_CAVEAT.md`](PRECISION_CAVEAT.md)).

## Why the sweep is split by state size

Measured on v18 seed 0 — the failure mode **inverts** with data size, so one recipe cannot serve both:

| state | windows | peak−final | **train−val gap @ep50** | diagnosis |
|---|---:|---:|---:|---|
| alabama | 96 k | +4.08 | **+42.45** | severe overfit |
| arizona | 201 k | +4.29 | **+41.15** | severe overfit |
| istanbul | 272 k | +3.68 | +7.09 | mild overfit |
| florida | 1.27 M | +1.59 | +3.48 | mild |
| california | 2.93 M | +0.61 | **+0.52** | **no overfit** |
| texas | 3.83 M | +1.20 | **+0.25** | **no overfit** |

Small states memorize (AL train F1 66.4 vs val 24.0). Large states show **no train–val gap at all** —
they are capacity-limited, not overfitting. So the small-state grid goes **down** in LR and the
large-state grid goes **up**. This matches v17's own conclusion that the cat optimum is
state-size-dependent (it already tiered bs2048/bs8192 by size).

## The class-weight asymmetry (verified 2026-08-07)

| arm | class-weighted CE? | set where |
|---|---|---|
| **dedicated** (`--task next`) | **YES** | `default_next` sets `use_class_weights=True`; read at `next_cv.py:140` |
| **MTL** (`--task mtl`) | **NO** | C25 (2026-06-05): `default_mtl` sets `use_class_weights_cat=False`, `use_class_weights_reg=False` |

**`--no-cat-class-weights` is INERT on `--task next`** — it sets `use_class_weights_cat`, which only
`mtl_cv.py:497` reads. The working flag for the dedicated arm is **`--no-class-weights`**
(`train.py:499-504`, `dest=use_class_weights`).

C25's own record: *"cat: EMPIRICALLY unweighted also wins macro-F1 (+5.1 pp AL: 48.37→53.51) — the
'balancing helps macro-F1' assumption was FALSE."* That was measured on the **MTL** cat head, on the
leaked substrate. If it transfers to the dedicated arm on v18, our ceiling is **under-estimated** and
every Δcat is **too positive** — i.e. the bias runs *against* the "MTL matches" reading, not for it.

## Execution order

Sequential on the single A40 unless a row says otherwise. GPU is compute-saturated at ~98 % by one
small-state job, so 2-wide buys only ~1.18× and is used solely where a row says so.
**CPU execution is excluded**: CUDA and CPU kernels give different floating-point results, so CPU
arms would not be comparable to GPU arms — the same class of error as the fp16/fp32 leak.

## EXECUTION ORDER — confirmed 2026-08-08

**3 → 7 → 4 → 10 → 5 → 6 → 3b → 9**, then the post-hoc rows **A–C → 11 → 12 → 10b → 13**.
All of 3/7/4/10/5/6/3b and A/B/C/11/12/10b are **✅ done**; row 13 is **🔄 running**; row 9 is the
only ⬜ left. Rows 3 and 7 ran together per state (AL ✅, AZ ✅, IST ✅).
**Row 8 is postponed and is NOT in this order.**

Chained unattended: `run_queue2.sh` (rows 3+7 at AZ/IST, then row 4) → `run_queue3.sh` (row 10) →
`run_queue4.sh` (rows 5, 6 at TX 1-fold; row 3b at FL 1-fold). Row 9 needs a winner fixed first.

**If the author is unavailable when the queues finish:** decide row 9 per the pre-registered rules
below, have the choice reviewed by an independent (Fable-5) reviewer, record the decision and its
reviewer verdict here, then work out which wave cells the new recipe invalidates and restart the
waves. Authorised 2026-08-08.

> 📊 **Full results with paired tests, per-arm tables and the two corrections:
> [`SWEEP_FINDINGS.md`](SWEEP_FINDINGS.md).** Read that for the audit; this file is the register.

## STATUS AT A GLANCE (updated 2026-08-08)

| question | answer |
|---|---|
| Dedicated (STL) sweep settled at AL/AZ/IST? | **YES — 30/30 arms done** (rows 1+2). Winner per state below. |
| Dedicated row 4 (`--no-class-weights`)? | ✅ **done** — removing them **HURTS** ~1 pp (−1.20 @0.005, −1.00 @0.0025). Author hypothesis not supported on the dedicated side. |
| MTL cat-LR grid {5e-4,1e-3,2e-3} + 25-ep arm (row 3)? | ✅ **done at AL, AZ, IST** — result: **null** (span ≤0.28 sm3 across 4× the LR range) |
| MTL cat-class-weights {on,off} × category-weight {0.75,0.5} (row 7)? | ✅ **done at AL, AZ, IST** — class weights are **alabama-only** (+1.12 p=0.004; AZ +0.23 p=0.64; IST −0.14 p=0.68) |
| P1 capacity control (after T2)? | ❌ **NOT run — deliberately HELD** by author decision 2026-08-07 → [`POSTPONED.md`](POSTPONED.md) P1 |
| CA/TX sweep (rows 5, 6, 8)? | ❌ **NOT run — POSTPONED for time** 2026-08-08 → [`POSTPONED.md`](POSTPONED.md) P6 |

### Dedicated (STL) winners — rows 1+2 complete, seed 0, fp32, sm3 selector

| state | current recipe | sm3 | **retuned winner** | sm3 | gain | med best-epoch |
|---|---|---:|---|---:|---:|---:|
| alabama | bs2048 @ 0.005 | 27.122 | **bs8192 @ 0.0025** | 27.610 | **+0.49** | 8 → 13 |
| arizona | bs8192 @ 0.005 | 31.103 | **bs8192 @ 0.0005** | 31.668 | **+0.57** | 10 → 17 |
| istanbul | bs2048 @ 0.005 | 30.998 | **bs2048 @ 0.0005** | 32.077 | **+1.08** | 6 → 16 |

Lower LR wins at all three, and the median best epoch moves from 6–10 into 13–23 — the signature v17's
76-arm sweep identified (early-peaking arms were never ceilings, 0/27). On *argmax* istanbul's old
recipe still looks best (32.722); its sm3 is the **worst** (30.998), which is the argmax-noise effect
this sweep exists to remove.

### MTL winner so far — alabama only (AZ/IST in flight)

| arm | cat sm3 | reg |
|---|---:|---:|
| cw0.75, class-weights **OFF** (current recipe) | 26.153 | 69.683 |
| **cw0.75, class-weights ON** | **27.276** | 69.696 |
| cw0.50, class-weights ON | 27.003 | 69.709 |
| cw0.50, class-weights OFF | 26.915 | 69.687 |

> **TIE-BREAK, pre-registered 2026-08-08 (author).** When the two class-weights-ON arms are
> statistically indistinguishable (they are: p=0.62 cat, p=0.90 reg), **break the tie on REGION**,
> which selects **`cw0.50 / class-weights ON`**. Rationale: region is the axis on which MTL has a
> defensible claim, so a tie on category should not decide it. Recorded before AZ/IST reported.

**The finding is the ON/OFF axis, not the loss split.** Paired per-fold at n=5:

| contrast | cat sm3 | p | reg | p |
|---|---:|---:|---:|---:|
| class-weights **ON vs OFF** (@cw0.75) | **+1.123** | **0.004** | +0.013 | 0.90 |
| cw0.50/ON vs cw0.75/ON | −0.273 | 0.62 | +0.014 | 0.90 |

Class weights ON is solid; **the 0.75-vs-0.50 choice is a coin flip at this n** and is left for AZ/IST
to break. Which of the two ON arms "wins" is selector-dependent — `cw0.50/ON` takes cat-argmax, reg
and geom_simple-argmax; `cw0.75/ON` takes cat-sm3 and geom_simple-sm3 (author observation 2026-08-08,
correcting an earlier read that looked only at category):

| arm | cat argmax | cat sm3 | reg | geom argmax | geom sm3 |
|---|---:|---:|---:|---:|---:|
| cw0.75 / OFF (current) | 27.3836 | 26.1532 | 69.6831 | 43.68 | 42.69 |
| cw0.75 / ON | 27.8604 | **27.2760** | 69.6956 | 44.07 | **43.60** |
| cw0.50 / OFF | 27.6771 | 26.9152 | 69.6873 | 43.92 | 43.31 |
| cw0.50 / ON | **27.9534** | 27.0034 | **69.7091** | **44.14** | 43.39 |

cat-LR is near-null across 4× its range (26.15–26.37 sm3). The 25-epoch arm gains cat +0.64 but costs
reg −0.79 — rejected.

Net at alabama, both arms fairly tuned and both fp32: **Δcat −0.97 → −0.33**.

### §12 note — category_weight 0.50 vs 0.75 under logit adjustment is a TRADE, not a free win

Re-measured at τ=0.5, 5 folds (`mla_*` arms). Δ is **(0.50 − 0.75)**:

| state | cat Δ | p | reg Δ | p |
|---|---:|---:|---:|---:|
| alabama | **+0.336** | **0.024** | −0.060 | 0.520 |
| arizona | +0.125 | 0.139 | **−0.188** | **0.010** |
| istanbul | −0.022 | 0.603 | **−0.180** | **0.007** |
| **mean** | **+0.146** | | **−0.143** | |

**cw0.50 does help category** — significantly at alabama, directionally at arizona. That reading is
correct. But it costs region **significantly at two of three states**, and the two effects are the
same size, so pooled it is close to a wash that moves ~0.15 pp from region into category.

**SWEEP_PLAN decision rule 3 pre-registers that ties break on region.** Under that rule the winner is
**cw0.75**. Adopting 0.50 means overriding the author's own pre-registration — allowed, but it must
be recorded as a deliberate override, not reported as "0.50 was better".

### §13 — corrections and decisions from the Fable review (2026-08-09)

**⚠ CORRECTION — bs16384 is NOT an improvement at large states.** The measured TX numbers are a
**monotone decline**: bs8192 → 16384 → 32768 gives sm3 35.1696 → 35.0585 → 34.6175 (−0.111, −0.552),
with **no wall-clock saving whatsoever** (1116 / 1119 / 1117 s).

The likely source of the opposite impression is the **argmax** column, where bs16384 *does* look
better — 35.1696 → 35.3995 (**+0.23**). That inversion is exactly the artifact `sm3` exists to
remove: the `argmax − sm3` gap grows 0.000 → 0.341 → 0.538 with batch size, because fewer optimizer
steps make the validation curve spikier and its single best epoch less trustworthy. Reading argmax
picks the tallest spike; reading sm3 picks the highest sustained region. **On the selector this study
committed to, bs8192 wins.**

It was also tested at a **small** state: row 10 and its post-calibration re-run 10b (AL, MTL). bs16k
is worse on both heads; bs32k buys +0.156 cat for **−2.05 reg**. So bs8192 is confirmed at both ends
of the size range and is kept everywhere.

**Row 13 (running)** validates logit adjustment where it has never been measured. It runs at
**bs8192, not bs16384** — the "faster" rationale is void per the walls above, and running the
validation off-recipe would confound it.

**Region + logit adjustment (author request, in row 13).** It *is* wired for the dedicated region
head (`p1_region_head_ablation.py:652-662`, train-split counts only). The prior expectation is that
it **hurts**: logit adjustment is Bayes-consistent for **balanced error** (macro-F1), whereas region
is reported by **Acc@10**, a frequency-weighted metric whose Bayes-optimal predictor is the
*unadjusted* posterior. `mtl_cv.py:477-479` already records that class-balancing hurts this head, and
turns it off by default for exactly this reason. Cheap enough (189 s/arm) to settle empirically.

## Row register

| # | stage | arm | states | grid | arms | status |
|---|---|---|---|---|---|---|
| 1 | small-state dedicated | dedicated | AL, AZ, IST | bs {2048, 8192} × max_lr {0.0005, 0.001, 0.0025, 0.005} | 24 | ✅ done |
| 2 | schedule shape | dedicated | AL, AZ, IST | epochs {15, 25} @ anchor | 6 | ✅ done |
| 3 | MTL cat-LR | MTL | AL, AZ, IST | cat-lr {5e-4, 1e-3, 2e-3} + 25-ep arm | 12 | ✅ done — null |
| 4 | dedicated class weights | dedicated | AL | `--no-class-weights` × max_lr {0.005, 0.0025} | 2 | ✅ done — removing hurts ~1 pp |
| 5 | large-state dedicated | dedicated | **TX, 1 fold** | max_lr {0.005, 0.0075, 0.01} × epochs {50, 75} | 5 | ✅ done — **FLAT** (all within 0.25 sm3); keep 0.005 @ 50 ep |
| 6 | dedicated class weights @ large | dedicated | **TX, 1 fold** | `--no-class-weights` | 1 | ✅ done — **OFF wins +1.18** @ 75 ep (opposite sign to alabama!) — **superseded by step B**: +1.556 over 3 folds @ 50 ep, p=0.030 |
| 7 | MTL knobs | MTL | AL, AZ, IST | class-weights {on,off} × cw {0.75, 0.5} | 9 | ✅ done — see SWEEP_FINDINGS §3 |
| 3b | MTL cat-LR @ large | MTL | **FL, 1 fold** | cat-lr {5e-4, 1e-3, 2e-3} + 25-ep | 4 | ✅ done — **null** (span 0.263 sm3); nominal best 2e-3 by +0.047 on ONE fold ⇒ keep 1e-3 |
| 8 | MTL @ large | MTL | TX/CA | carried from #7 | 2 | ⏸ **POSTPONED** (P6) |
| 10 | **MTL batch size** | MTL | AL | per-head LR ×{1.67, 2.5, 3.33} × bs {16384, 32768} | 6 | ✅ done — **keep bs8192** (larger batches cost ~1.3 reg) |
| 10b | MTL batch size **re-run post-calibration** | MTL | AL | bs {16384, 32768} × per-head LR ×{1.67, 2.5, 3.33} | 6 | ✅ done — **bs8192 still wins**: bs16k is worse on cat *and* reg; bs32k buys +0.156 cat for **−2.05 reg** |
| 12 | MTL logit-adjust × category_weight | MTL | AL, AZ, IST, 5 folds | cw {0.50, 0.75} @ τ=0.5 | 6 | ✅ done — a **genuine trade**, see §12 note below |
| **13** | **large-state logit-adjust validation** | both | **TX f0, CA f0, AL region 5f** | τ=0.5 vs baseline | 5 | 🔄 **running** (launched 2026-08-09) |
| 9 | confirm | both | winners | best dedicated + best MTL | — | ⬜ **the only row still outstanding** |

**Row 8 is NOT in the execution order** — it is postponed (P6) and will not run in this pass.

### Follow-ups added 2026-08-08 (`run_next2.sh`) — triggered by the row-6 sign flip

| step | what | scope | why | cost | status |
|---|---|---|---|---:|---|
| **A** | AZ + IST dedicated `--no-class-weights` | 5 folds, at the retuned winner LR **and** at 0.005 | AL (96 k) says weights ON, TX (3.8 M) says OFF. AZ (201 k) / IST (272 k) sit between → is the flip **size-graded** or a texas peculiarity? | ~37 min | ✅ done — AZ **−0.535** (both LRs agree); IST **sign-flips** between LRs ⇒ null. Both weak. |
| **B** | TX class weights, folds 0/1/2, same seed, **50 ep** | 6 runs | one fold can be biased. Fold 0 is re-run at 50 ep for **both** arms so the 3-fold mean does not mix schedules with row 6's 75 ep | ~1.6 h | ✅ done — **OFF wins +1.556**, sd 0.478, t=+5.64, **p=0.0301**, 3/3 folds positive |
| **C** | TX dedicated bs {16384, 32768} | 1 fold, class-weight flag taken from **B's 3-fold mean** | batch size at a state that is *not* step-starved (unlike AL row 10) | ~40 min | ✅ done — **bs8192 wins**: 16k −0.111, 32k −0.552, and **no wall saving** (1116/1119/1117 s) |
| **D** | FL MTL bs {16384, 32768} | 1 fold, at the best row-3b cat-lr | AL's batch sweep was confounded by step starvation; FL has ~13× the windows | ~50 min | ⏭ **NOT RUN** — dropped when row 10b re-confirmed bs8192 at AL post-calibration and step C confirmed it at TX. Two states, both ends of the size range, agree; a third batch sweep was not worth ~50 min. |
| **11** | **logit adjustment** `--logit-adjust-tau {0.5, 1.0}` | AL, AZ, IST, 5 folds, at each state's **retuned winner LR** | row 4 removed class weights with **no replacement** and lost ~1 pp. Logit adjustment is the Bayes-consistent substitute and targets macro-F1 directly. **This is the cell row 4 never tested.** | ~49 min | ✅ done — **τ=0.5 wins big**: dedicated **+2.86**, MTL **+3.18**, all p≤0.0014. τ=1.0 a flat null. Only AL/AZ/IST ⇒ **row 13** validates it at scale. |

**A runs first, deliberately.** Two contradictory data points (AL ON, TX OFF) are not a finding; a
size-graded transition would be. The large-state recipe decision waits on it.

⚠️ **D may OOM at bs32768.** FL MTL at bs8192 uses **15.2 GB of 46 GB**; ~4× the activations likely
exceeds the card. The driver catches OOM, logs it distinctly and continues — a failure there is
information, not a crash.

**Epochs pinned at 50 for TX** (author 2026-08-08): row 5 showed 50 vs 75 inside the margin of error.

#### Row 11 — logit adjustment (author request 2026-08-08)

**Verified mechanism, not assumed.** `next_cv.py:123-141` — when `config.loss_calibration` is
non-empty it builds `CalibratedLoss`, and the class-weighted `CrossEntropyLoss` is the **`else`**
branch. So `--logit-adjust-tau` **replaces class weighting automatically**. Do **not** also pass
`--no-class-weights` or `--tail-loss balanced`: stacking logit adjustment on balanced weights
cratered in T1.4 (AL 30.15 vs 49.97).

**Leak-safe, verified:** class counts come from `train_loader.dataset.targets` — the TRAIN fold only
(`next_cv.py:127`) — and the offset is applied inside the criterion. `shared_evaluate` takes no
criterion, so evaluation logits are unadjusted.

**Prior evidence:** the mtl_improvement T1.4 re-pin tuned this exact head and found **τ=0.5 beat
`--tail-loss balanced` at all four states**. ⚠ Caveat: T1.4 ran on the **stride-9** substrate
(AL 12,709 windows); v18 is **stride-1** (96,326). Transfer is not guaranteed.

Run at each state's retuned winner LR (AL bs8192@0.0025, AZ bs8192@0.0005, IST bs2048@0.0005) so the
result composes with the adopted recipe rather than a superseded one.
| P1 | capacity-matched region control | dedicated reg | AL, CA | `d_model` 480 / 352 | 2 | ⬜ after sweep |

### 1-fold screens — scope decision 2026-08-08, and its limits

Rows 5, 6 and 3b run **one fold** to buy large-state evidence cheaply: rows 5+6 drop from ~9.6 h to
**~1.9 h**, row 3b from ~6.5 h to **~1.6 h**. This directly reduces the transfer risk recorded in
[`POSTPONED.md`](POSTPONED.md) P6 — some large-state evidence beats none.

**What one fold can and cannot do.** The effects measured at the small states were +0.49…+1.08 sm3;
TX dedicated fold-σ is ~0.30. One fold gives no dispersion, no paired test and no interval, so it can
pick a **direction** but cannot certify a winner — the same rule the region triage driver states. Arms
are compared **on the same fold**, so the contrast stays paired and fair even if fold 0 is not
representative in absolute level.

⚠ **Use `--only-fold 0`, never `--folds 1`** — because `--folds N` overrides `k_folds` to
`max(2,N)`, so `--folds 1` silently trains on a **2-fold split**, a different partition from the
canonical 5-split, making the screen incomparable to the 5-fold cells. `--only-fold` runs exactly
fold 0 *of* the canonical 5-split.

**Correction 2026-08-08 (author, repeatedly).** An earlier version of this note justified the same
flag by a `log_T` leak. **That does not apply here: this recipe never loads `log_T` at all.**
`_log_t_is_inert` (`mtl_cv.py:552`) is true when `freeze_alpha=True` + `alpha_init=0.0` + every KD
route off — exactly our config — and `MTL_SKIP_INERT_LOGT` defaults to on, so the load **and its
leak-guards** are skipped. Every fold logs `[log_T-inert skip] … Output byte-identical`.
`--per-fold-transition-dir` is passed only to match the board driver; it is inert. The `log_T` leak
warning applies solely to configs with a **live** α-prior (learnable α, α_init ≠ 0, or any KD
weight > 0) — not to champion-G or to v18.

### Inserted 2026-08-07 — trunk arms at alabama, BEFORE the MTL sweep rows

Ordering is deliberate (user decision): the trunk result can change what the MTL sweep should test,
so it runs **before** rows 3 / 7 / 8. Row 3 (MTL cat-LR grid) is deferred until these report.

| # | stage | arm | state | flag | seeds | cost | status |
|---|---|---|---|---|---|---|---|
| T1 | trunk | **A** no sharing | alabama | `--model-param disable_cross_attn=True` | 0 | 359 s | ✅ Δcat **−0.015**, Δreg **−0.138** |
| T2 | trunk | **A′** no mixing, same depth | alabama | `--model-param identity_cross_attn=True` | 0 | 414 s | ✅ Δcat **−0.154**, Δreg **−0.004** |
| T3 | trunk | **A** no sharing | florida | `--model-param disable_cross_attn=True` | 0 | 4525 s | ✅ **DONE** Δcat **+0.002**, Δreg **+0.026** |
| T4 | trunk | **A′** | florida | `identity_cross_attn=True` | 0 | — | ⏭ **dropped** — nothing for A′ to decompose after T3's null |

**T1/T2 result: at ALABAMA the trunk is inert, not harmful.** The "trunk adds capacity that feeds
memorization" hypothesis is falsified *at alabama* — severing it neither helps nor hurts (|Δ| ≤ 0.154
on either head, against fold-σ ~1.7 cat / ~3.0 reg).

⚠ **SCOPE — do not generalise this.** This is a 5-fold measurement at ONE small state. The CA/TX/FL/
IST evidence is a **1-fold screen** which, by its own driver's rule, has power only for a
several-point effect: it refutes "the trunk carries the +2 pp" and licenses **nothing smaller**. A
5-fold trunk ablation at CA/TX does **not** exist ([`POSTPONED.md`](POSTPONED.md) P4, deferred by
decision 2026-08-07). Statements of the form "the trunk is inert at every scale" are **not
supported**; the supported statement is "inert at alabama (5-fold), and not the source of the CA/TX
advantage (1-fold screen)".

The compute observation (champion-G 1094 s vs T1 359 s at alabama) is likewise **alabama-scoped** and
is not a basis for changing the architecture until CA/TX are measured at 5 folds.

**Hypothesis under test at alabama is the OPPOSITE of the one at CA/TX.** There the question was
"does severing cost the +2 pp?" (answer: no — see
[`region_1fold_triage/FINDING.md`](region_1fold_triage/FINDING.md)). Here the question is **does
severing HELP?** At alabama the joint model is *worse* than dedicated on both heads (Δcat −0.65 /
−1.04, Δreg −0.31 / −0.33) while the dedicated arm overfits badly (train macro-F1 66.4 vs val 24.0).
If the trunk is adding capacity that feeds memorization, A and A′ should **beat** champion-G.

Falsification: if A and A′ land within fold-σ of champion-G, the trunk is simply inert at small data
too, and no trunk-side change will fix the alabama deficit.

⚠ Caveat on A′ (from the Fable review): `identity_cross_attn` zeroes the attention *output* but keeps
the attention weights (~1.05 M params) present-but-unused, so it is a control for **per-stream FFN
depth**, not for attention capacity. A vs A′ decomposes mixing vs depth; neither controls the
2.5–5.9× dual-tower region pathway.

Rows 4 and 6 test the user's hypothesis that class weights should be off on **all** arms; row 6 is
included because the class-weight effect may itself be size-dependent (macro-F1 balancing matters
more where the model memorizes).

Row 8 is **conditional** to avoid spending ~2 h on a null: TX MTL cells are the most expensive in the
matrix.

## Cost (measured, not extrapolated)

Per 5-fold run at fp32: AL dedicated ~350 s · AZ ~310 s · IST ~800 s · TX dedicated ~5 700 s ·
AL MTL ~1 340 s · TX MTL ~22 500 s. Rows 1–3 ≈ 9 h; rows 4–8 ≈ 8 h; row 9 ≈ 2 h.

## Decision rules (pre-registered, so the choice is not made after seeing the numbers)

1. **Selector.** Every arm is scored under **both** conventions: `argmax` (the board's diag-best) and
   `sm3` (raw value at the 3-epoch-smoothed argmax; see [`stage0_rescore.py`](stage0_rescore.py)).
   The winner is chosen on **sm3**, because argmax is the high-variance statistic this sweep exists
   to fix. Both are reported.
2. **Winner = per-state max of the mean over seeds**, exactly as `cat_ceiling_sweep/aggregate.py`
   does. Median best-epoch > 15 is recorded as a **sanity flag, not a selector** — v17 evidence is
   that early-peaking arms are never ceilings (0/27), but late-peaking does not guarantee a ceiling
   either (v17's low-LR arms peaked late and sat 3.2 pp below).
3. **Both arms are re-tuned.** Re-tuning only the baseline would bias Δcat against MTL.
4. ~~A retuned recipe is adopted board-wide only if it wins at both a small and a large state~~
   **SUPERSEDED 2026-08-08 (author decision, time constraint).** The CA/TX sweep is postponed, so the
   winner from AL/AZ/IST is **replicated to the large states without large-state validation**.

   ⚠ **The evidence argues against this and the risk must travel with the numbers.** The failure mode
   *inverts* with data size (see the table at the top of this file): AL/AZ overfit catastrophically
   (train−val +42 pp) while CA/TX show **no train−val gap at all** (+0.25 / +0.52) and are
   capacity-limited. The small-state fix is **lower LR**, which is the opposite of what a
   capacity-limited model needs. Replicating it to CA/TX may *reduce* their category scores.

   Two consequences to state wherever a large-state category number is reported: (a) the CA/TX
   category recipe is **transferred, not validated**; (b) if a CA/TX category number drops relative to
   the current recipe, that is the expected direction of this risk and not a new finding. The
   alternative — keep CA/TX on their existing v17 large-state tier (bs8192 @ 0.005) and retune only
   the small states — is the tiered option v17 itself used, and remains available at zero cost.

## Returning to the waves

After the sweep the evaluation waves resume with the adopted recipe:

- `docs/results/closing_data/v18/` holds **29 completed cells** (seed 0 all six states × 3 families;
  seed 1 istanbul/alabama/arizona × 3 + florida cat/reg). They are **resume-safe**: `run_wave.sh`
  skips any cell whose sidecar exists.
- ⚠ Cells produced **before** the retune used the inherited recipe and the leaked-substrate
  schedule. If the retune changes the recipe, the **category** cells must be regenerated; the
  **region** cells are unaffected (region peaks late and shows no argmax artifact — noise ratio vs
  v17 is 0.98).
- The two **void** cells regardless of the retune: florida cross-seed cat, texas s0 Δcat
  (both precision-confounded — [`PRECISION_CAVEAT.md`](PRECISION_CAVEAT.md)).
- Remaining to finish the n=10 matrix: florida joint s1, texas ×3 s1, california ×3 s1.
