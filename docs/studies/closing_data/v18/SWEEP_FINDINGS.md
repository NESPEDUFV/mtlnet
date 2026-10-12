# v18 re-tuning sweep — findings, in full, for audit

> **Written for auditing, not for reading.** Every number below is a 5-fold seed-0 mean on the v18
> engine, fp32, `--compile --tf32`. Paired tests are per-fold across the same 5 folds (n=5), so they
> are matched but underpowered — read p-values as *"is the sign stable across folds"*, not as proof.
> Raw sidecars: `docs/results/closing_data/v18_sweep/*.json` (each carries `*_per_fold`).
>
> Selector conventions: **argmax** = the board's diag-best; **sm3** = raw metric at the 3-epoch
> smoothed argmax ([`stage0_rescore.py`](stage0_rescore.py)). The pre-registered rule picks on
> **sm3**. Both are shown so a reader can check the choice is not selector-shopping.
>
> Status 2026-08-08: rows 1, 2, 3, 4, 7 complete. Row 10 running. Rows 5, 6, 3b queued. Row 8
> postponed. Row 9 pending a recipe decision.

---

## 1 · Headline: what survives three states, and what does not

| finding | states | verdict |
|---|---|---|
| **Logit adjustment τ=0.5 on BOTH arms** | AL, AZ, IST | ✅ **LARGEST EFFECT IN THE SWEEP** — dedicated +2.86, MTL +3.18, all p ≤ 0.0014. Δcat preserved (−0.363 → −0.105). See §9 |
| **Dedicated ceiling was mistuned; lower LR wins** | AL, AZ, IST | ✅ **ROBUST** — wins at all three, +0.49 / +0.57 / +1.08 sm3 |
| **Shared trunk is inert** | AL, FL (5-fold) | ✅ robust where measured; **not** established at CA/TX |
| MTL cat-LR matters | AL, AZ, IST | ❌ **null** — spans 0.22 / 0.21 / 0.28 sm3 across 4× the LR range |
| MTL 25-epoch schedule | AL, AZ, IST | ❌ **rejected** — trades cat for reg |
| **MTL class weights ON helps** | AL only | ⚠️ **DOES NOT REPLICATE** — see §3 |
| Removing class weights from the dedicated arm | AL (5f) | ❌ **hurts** ~1 pp — see §4 |
| **…but at TEXAS it HELPS ~1.2 pp** | TX (1f) | ⚠️ **sign flips with data size** — see §7.2. AZ/IST queued to map it |
| TX dedicated LR / schedule grid | TX (1f) | ❌ **flat** — no change warranted; recipe tiers by size — see §7.1 |
| MTL batch size (16k / 32k) | AL | ❌ **keep bs8192** — larger batches cost ~1.3 reg — see §7.3 |
| cw 0.75 vs 0.50 | AL, AZ, IST | ⚠️ **tie-break reversed** — see §3.2 |

**The one-sentence summary: BOTH arms were mis-calibrated — logit adjustment τ=0.5 lifts each by
~3 pp and leaves Δcat where it was (≈0, "matches") — and separately the dedicated baseline's LR was
mistuned and is now fixed. No MTL-specific knob survives three states.**

---

## 2 · Dedicated (STL) re-tune — rows 1 + 2, 30 arms, COMPLETE

Full per-state tables are in [`SWEEP_PLAN.md`](SWEEP_PLAN.md). Winners on sm3:

| state | current recipe | sm3 | **retuned winner** | sm3 | gain | median best epoch |
|---|---|---:|---|---:|---:|---|
| alabama | bs2048 @ 0.005 | 27.122 | **bs8192 @ 0.0025** | 27.610 | **+0.49** | 8 → 13 |
| arizona | bs8192 @ 0.005 | 31.103 | **bs8192 @ 0.0005** | 31.668 | **+0.57** | 10 → 17 |
| istanbul | bs2048 @ 0.005 | 30.998 | **bs2048 @ 0.0005** | 32.077 | **+1.08** | 6 → 16 |

**Why this is the most trustworthy result in the sweep:**
1. It reproduces at **all three** states, in the **same direction**, with the same mechanism.
2. The median best epoch moves out of the early-peak zone (6–10) into 13–23 — the exact signature
   v17's own 76-arm sweep used to identify a mis-tuned arm (**0 of 27** early-peaking arms was ever a
   ceiling; they averaged −2.59 pp below).
3. It is **selector-honest**: at istanbul the *old* recipe still wins on argmax (32.722 vs 32.424)
   while losing badly on sm3 (30.998 vs 32.077). That is argmax reading a 1–3-epoch spike. If we had
   judged on argmax alone we would have kept the worse recipe.

⚠️ **Not validated at a large state.** Rows 5/6 (TX, 1 fold) are queued. The failure mode inverts
with data size — AL/AZ overfit (train−val +42 pp) while CA/TX show **no train−val gap** (+0.25 /
+0.52) — so a lower LR may *hurt* the large states. See [`POSTPONED.md`](POSTPONED.md) P6.

---

## 3 · MTL knobs — rows 3 + 7, 21 arms across three states, COMPLETE

### 3.1 Full table (5-fold seed-0 means)

| state | arm | cat sm3 | cat argmax | reg | wall |
|---|---|---:|---:|---:|---:|
| alabama | cat-lr 5e-4 | 26.3148 | 27.1045 | 69.7579 | 583 s |
| alabama | cat-lr 1e-3 *(anchor)* | 26.1532 | 27.3836 | 69.6831 | 552 s |
| alabama | cat-lr 2e-3 | 26.3657 | 27.5131 | 69.6592 | 552 s |
| alabama | cat-lr 1e-3 @25 ep | 26.7901 | 27.6177 | **68.8910** | 290 s |
| alabama | **cw0.75 ON** | **27.2760** | 27.8604 | 69.6956 | 552 s |
| alabama | cw0.50 OFF | 26.9152 | 27.6771 | 69.6873 | 552 s |
| alabama | cw0.50 ON | 27.0034 | **27.9534** | **69.7091** | 552 s |
| arizona | cat-lr 5e-4 | 30.8518 | 31.5924 | 59.5326 | 1155 s |
| arizona | cat-lr 1e-3 *(anchor)* | 30.7987 | 31.6874 | 59.5411 | 1133 s |
| arizona | cat-lr 2e-3 | **31.0127** | 31.7250 | 59.5002 | 1134 s |
| arizona | cat-lr 1e-3 @25 ep | 30.9994 | 31.6297 | 59.2638 | 582 s |
| arizona | **cw0.75 ON** | 31.0282 | 31.6232 | **59.6212** | 1133 s |
| arizona | cw0.50 OFF | 30.8695 | **31.7298** | 59.3295 | 1131 s |
| arizona | cw0.50 ON | 30.9327 | 31.6155 | 59.5097 | 1131 s |
| istanbul | cat-lr 5e-4 | 32.0349 | 32.5243 | 75.4018 | 1539 s |
| istanbul | cat-lr 1e-3 *(anchor)* | 31.9130 | 32.6985 | 75.3631 | 1507 s |
| istanbul | cat-lr 2e-3 | 31.7531 | 32.7514 | 75.3422 | 1508 s |
| istanbul | cat-lr 1e-3 @25 ep | **32.2227** | 32.4091 | 75.2983 | 769 s |
| istanbul | cw0.75 ON | 31.7716 | 32.3552 | **75.4320** | 1507 s |
| istanbul | **cw0.50 OFF** | 32.0695 | **32.6726** | 75.2531 | 1506 s |
| istanbul | cw0.50 ON | 31.8189 | 32.3861 | 75.2623 | 1506 s |

**cat-LR is null.** Across a 4× range the sm3 span is 0.22 (AL), 0.21 (AZ), 0.28 (IST) — smaller than
the fold-σ. The argmax winner and the sm3 winner disagree at every state, which is what a null looks
like under a noisy selector.

**The 25-epoch arm is rejected.** It gains cat at AL (+0.64) and IST (+0.31) but costs reg
**−0.79** (AL) / −0.27 (AZ) / −0.06 (IST). Halving the schedule halves the wall time, which is its
only real attraction.

### 3.2 ⚠️ Class weights: an Alabama-only effect

**This corrects an earlier claim in this study.** After Alabama alone, the sweep reported
"class weights ON is the lever: +1.12 sm3". With arizona and istanbul measured, it does not hold.

Paired per-fold, class-weights **ON vs OFF** at cw0.75 (n=5):

| state | Δ cat sm3 | p | Δ reg | p |
|---|---:|---:|---:|---:|
| **alabama** | **+1.123** | **0.004** | +0.013 | 0.90 |
| arizona | +0.229 | 0.64 | +0.080 | 0.42 |
| istanbul | **−0.141** | 0.68 | +0.069 | 0.08 |

One significant state, one null, one null-and-negative. The three-state mean (+0.40) is carried
entirely by alabama. **Do not report "class weights help MTL" as a finding.** The defensible
statement is: *class weighting the MTL category head helps at alabama and is null at arizona and
istanbul.*

Region is unmoved everywhere (+0.013 / +0.080 / +0.069), so the knob is category-only regardless.

### 3.3 ⚠️ The tie-break reversed: region now prefers cw0.75

The pre-registered rule was: *when the two class-weights-ON arms are statistically indistinguishable,
break the tie on **region***. That rule was fixed on alabama-only data, where region gave
`cw0.50` a **+0.014 (p=0.90)** edge — i.e. a null.

With arizona and istanbul measured, `cw0.50/ON` vs `cw0.75/ON`:

| state | Δ cat sm3 | p | **Δ reg** | **p** |
|---|---:|---:|---:|---:|
| alabama | −0.273 | 0.62 | +0.014 | 0.90 |
| **arizona** | −0.095 | 0.56 | **−0.111** | **0.037** |
| **istanbul** | +0.047 | 0.69 | **−0.170** | **0.006** |

Category is a null at all three (p = 0.62 / 0.56 / 0.69), so the tie-break condition genuinely
applies. On region, **cw0.50 is significantly worse at two of three states** and null at the third.

**Applying the pre-registered rule to the full data selects `cw0.75 / class-weights ON`, not
`cw0.50`.** The rule was fixed before these numbers existed and is being applied unchanged; it is the
data that moved. Recorded here rather than silently re-deciding. **Awaiting the author's
confirmation before the adopted recipe changes.**

---

## 4 · Row 4 — removing class weights from the DEDICATED arm hurts

Hypothesis under test (author): class weights should be off on **all** arms, dedicated included.
C25's record showed unweighted cat CE winning macro-F1 by +5.1 pp — but that was measured on the
**MTL head, on the leaked substrate**.

Alabama, dedicated, bs8192, 5 folds (`--no-class-weights`; note `--no-cat-class-weights` is **inert**
on `--task next`):

| max_lr | weights ON (default) | weights OFF | Δ sm3 | p | med epoch ON → OFF |
|---|---:|---:|---:|---:|---|
| 0.005 | 27.4230 | 26.2195 | **−1.203** | 0.19 | 10 → 15 |
| 0.0025 | 27.6098 | 26.6145 | **−0.995** | 0.23 | 13 → 14 |

**Removing class weights costs ~1 pp on the dedicated arm**, consistently at both LRs. p ≈ 0.2 at
n=5, so this is directional rather than proven — but the sign is the same at both settings and the
magnitude is large relative to the retune gains it would erase.

**Consequence:** C25's unweighted-wins result does **not** transfer from the MTL head on the leaked
substrate to the dedicated arm on v18. The dedicated ceiling keeps its class weights, so the retuned
ceiling from §2 stands and Δcat is **not** pushed back down.

---

## 5 · How this changes Δcat at alabama

All fp32, both arms, sm3 selector:

| configuration | dedicated | MTL | **Δcat** |
|---|---:|---:|---:|
| both as-inherited | 27.122 | 26.153 | **−0.968** |
| both retuned (MTL = cw0.75/ON) | 27.610 | 27.276 | **−0.334** |

Fair tuning of both arms moves Δcat from −0.97 to −0.33 at alabama. This is **one state and one
seed**; it is not the pooled headline. The pooled Stage-0 result across six states remains
**Δcat +0.010, 95% CI [−0.424, +0.445], "matches" (TOST ±2 pp)**.


---

## 7 · Large states — rows 5, 6 (TX, 1 fold) and row 10 (MTL batch size, AL)

### 7.1 Row 5 — TX dedicated LR/schedule grid: FLAT

Grid went **up** (0.005 → 0.01) because TX shows no train−val gap. It found nothing.

| max_lr | epochs | argmax | sm3 | best epoch |
|---:|---:|---:|---:|---:|
| **0.005** | 50 | 34.107 | 33.613 | 16 |
| 0.0075 | 50 | 34.007 | 33.058 | 9 |
| 0.01 | 50 | 34.012 | 33.607 | **2** |
| 0.005 | 75 | 33.997 | **33.848** | 9 |
| 0.0075 | 75 | 34.077 | 33.602 | 9 |

Everything sits within **0.25 sm3 / 0.11 argmax** — smaller than the *gain* the small-state retune
produced (+0.49…+1.08). At one fold with no dispersion that is a null: the screen picks no direction.
Raising the LR does **not** help, so the "large states are capacity-limited, go up" reasoning is
**not** supported either. Both directions are flat.

The `lr 0.01` arm peaks at **epoch 2** — the pathological end of the early-peak signature; its argmax
is read off essentially a first-epoch spike and only the smoothing rescues it.

**Consequence:** the blind-transfer risk in [`POSTPONED.md`](POSTPONED.md) P6 resolves the safest
way — there is no reason to change the large-state LR at all. **Recipe tiers by state size**, exactly
as v17 did: small states take the retuned lower LR, large states keep `bs8192 @ 0.005`.
**Epochs pinned at 50** (author, 2026-08-08): 50 vs 75 is inside the margin of error.

### 7.2 Row 6 — TX class weights: the sign FLIPS versus alabama ⚠️

| state | data | train−val gap | folds | **Δ sm3 (OFF − ON)** |
|---|---|---:|---:|---:|
| **alabama** | 96 k windows | **+42 pp** (memorizing) | 5 | **−1.203** → weights **ON** better |
| **texas** | 3.83 M windows | **+0.25** (no overfit) | **1** | **+1.176** → weights **OFF** better |

Same knob, opposite sign, and the split falls exactly on the overfit/capacity divide measured in
§ *Why the sweep is split by state size*. Mechanistically coherent: macro-F1 rewards rare classes, so
where the model memorizes (AL) class weighting is a useful rebalancer, and where there is enough data
to fit rare classes anyway (TX) it distorts away from the frequency-weighted optimum.

**This partially vindicates the author's hypothesis** that class weights should be off — true at
large states, false at small ones. C25's "unweighted wins" evidently transfers at scale, not at small
data.

⚠️ **It is load-bearing and under-evidenced.** TX's Δcat was **+0.96**, the only "beats" verdict in
the category column. If the TX dedicated ceiling rises ~1.18, that becomes ≈ **−0.2** and the last
category "beats" disappears. But this is **1 fold** against alabama's 5. In its favour: +1.18 is ~4×
TX's dedicated fold-σ (~0.30). Against it: one fold has no dispersion, and row 6 ran at 75 epochs
while everything else uses 50.

### 7.3 Row 10 — MTL batch size at alabama: keep bs8192

All arms on cw0.50 + class-weights ON. Per-head LRs scaled ×1.67/2.5/3.33 (the `--max-lr` flag is
inert under `MTL_ONECYCLE_PER_HEAD_LR=1`).

| bs | lr× | cat sm3 | reg | geom |
|---:|---:|---:|---:|---:|
| **8192 (reference)** | 1.00 | 27.003 | **69.709** | **43.386** |
| 16384 | 1.67 | 26.691 | 69.570 | 43.091 |
| 16384 | 2.50 | 27.115 | 69.182 | 43.311 |
| 16384 | 3.33 | 26.477 | 69.483 | 42.892 |
| 32768 | 1.67 | **27.234** | 68.374 | 43.152 |
| 32768 | 2.50 | 26.649 | 68.470 | 42.716 |
| 32768 | 3.33 | 27.171 | 68.564 | 43.162 |

**bs8192 wins on region and on the joint selector; every larger-batch arm is worse on `geom`.** The
best category arm (bs32k ×1.67, +0.23 cat) costs **−1.34 reg**. Category is scattered with no LR
trend (noise); **region is the informative axis** and loses ~1.3 pp at bs32k across all three LRs.

Read this as **"too few optimizer steps hurts region"**, not "large batches hurt": bs32768 gives only
~118 steps over 50 epochs at alabama, and the region head peaks late (epochs 25–50), so it is exactly
what a shortened step budget damages. The two are confounded at alabama — as flagged *before* the run.

---

## 8 · Follow-ups A–D as planned (results are in §11)

| step | what | scope | why | cost |
|---|---|---|---|---:|
| **A** | AZ + IST dedicated `--no-class-weights` | 5 folds, at the retuned winner LR **and** at 0.005 | AL (96 k) says ON, TX (3.8 M) says OFF. AZ (201 k) and IST (272 k) sit between, so they show whether the flip is **size-graded** or a texas peculiarity | ~37 min |
| **B** | TX class weights, folds 0/1/2, same seed, **50 ep** | 6 runs | one fold can be biased; fold 0 is re-run at 50 ep for both arms so the 3-fold mean does not mix schedules | ~1.6 h |
| **C** | TX dedicated bs {16384, 32768} | 1 fold, class-weight flag taken from **B's 3-fold mean** | batch size at a state that is not step-starved | ~40 min |
| **D** | FL MTL bs {16384, 32768} | 1 fold, at the best row-3b cat-lr | the AL batch sweep was confounded by step starvation; FL has ~4× the windows | ~50 min |

⚠️ **D may OOM at bs32768.** FL MTL at bs8192 uses **15.2 GB of 46 GB**; 4× the activations likely
exceeds the card. The driver catches OOM, logs it distinctly and continues — a failure there is
information, not a crash.

### 8.1 Row 11 — logit adjustment (queued after A–C)

`--logit-adjust-tau {0.5, 1.0}` at AL/AZ/IST, 5 folds, at each state's retuned winner LR (~49 min).

**Why this is not a repeat of row 4.** Row 4 removed class weights with **no replacement** and lost
~1 pp at alabama. Logit adjustment is the Bayes-consistent *substitute*: it shifts logits by
`τ·log(prior)` instead of reweighting the loss, and it targets macro-F1 directly. `next_cv.py:123-141`
makes the class-weighted CE the `else` branch, so passing the flag replaces class weighting on its
own — the untested cell.

Prior: T1.4 found **τ=0.5 beat balanced weighting at all four states** — but on the **stride-9**
substrate (AL 12,709 windows) versus v18's **stride-1** (96,326), so transfer is not guaranteed.

This is also the intervention the overfitting diagnosis ranked #2 of 3, and the only one of the three
expected to move the reported metric rather than merely stabilise training.

**A is deliberately first.** Two contradictory data points (AL ON, TX OFF) are not a finding; a
size-graded transition would be. The recipe decision for the large states should wait for it.


---

## 9 · Rows 11 + 12 — logit adjustment: the largest effect in the sweep, on BOTH arms

### 9.1 What it is, and why it is not a leak

`--logit-adjust-tau τ` adds `τ · log P_train(y)` to the logits **inside the training loss only**
(Menon et al., ICLR'21). The model learns `f(x) ≈ log p(y|x) − τ·log p(y)`, so its raw argmax at
inference targets the **balanced** posterior — the Bayes-consistent estimator for balanced error, and
our reported metric (macro-F1) is a balanced metric. It is the correct loss for the objective, not a
trick.

**Leak audit (the author asked for this explicitly; all three routes closed):**

| risk | finding |
|---|---|
| priors from the full dataset? | **No** — per-fold from `train_loader.dataset.targets` (STL, `next_cv.py:127`) / `dataloader_category.train.y` (MTL, `mtl_cv.py:504`). Verified empirically: fold offsets differ from the global vector; `fold-0 == global` is **False**. |
| offset applied at evaluation? | **No** — `shared_evaluate.evaluate()` takes **no criterion**; it computes `logits = model(X)` then `argmax(1)`. The offset lives in `CalibratedLoss.forward()`, which eval never calls. |
| could the offset smuggle information? | **No** — it is a **length-7 constant vector**, the log of train label frequency. It cannot encode per-example or per-user information. |

Sanity: at τ=0 the criterion reduces to plain cross-entropy to 7 decimals (2.44361711 vs 2.44361687).

It also **replaces** class weighting rather than stacking with it — `next_cv.py:123-141` and
`mtl_cv.py:481-484` both make the weighted CE the `else` branch ("mutually exclusive with cat
class-weighting"). Stacking cratered in T1.4 (AL 30.15 vs 49.97), so neither driver passes both.

### 9.2 Row 11 — dedicated arm, τ=0.5 vs τ=1.0

| state | class-weighted | **τ=0.5** | Δ | p | τ=1.0 | Δ | p |
|---|---:|---:|---:|---:|---:|---:|---:|
| alabama | 27.6098 | **30.4082** | **+2.798** | 0.0142 | 27.4527 | −0.157 | 0.71 |
| arizona | 31.6675 | **34.3852** | **+2.718** | 0.0008 | 31.3062 | −0.361 | 0.31 |
| istanbul | 32.0772 | **35.1431** | **+3.066** | 0.0002 | 32.2704 | +0.193 | 0.59 |
| | | | **+2.861** | | | **−0.108** | |

**There is a sharp interior optimum.** τ=0.5 wins at all three states; τ=1.0 is a flat null at all
three. That shape is itself evidence the effect is mechanistically real — a leak or a metric artifact
would not peak and then reverse. It also reproduces T1.4's τ=0.5 choice on a **different substrate**
(stride-9 → stride-1, 7.6× the windows), which discharges much of the transfer caveat.

⚠ **τ matters more than the switch.** Anyone adopting logit adjustment at the textbook default of
1.0 would have measured nothing here.

### 9.3 Row 12 — the MTL arm gains just as much, so Δcat is preserved

Row 11 alone would have implied MTL had fallen ~3 pp behind. It had not — the joint model has the
same knob (`mtl_cv.py:481-504`) and exploits it at least as well:

| state | ΔMTL | p | ΔDED | Δcat before | **Δcat after** |
|---|---:|---:|---:|---:|---:|
| alabama | +2.741 | 0.0010 | +2.824 | −0.308 | −0.391 |
| arizona | +3.276 | 0.0001 | +2.882 | −0.475 | **−0.081** |
| istanbul | +3.528 | 0.0005 | +3.066 | −0.306 | **+0.156** |
| **mean** | | | | **−0.363** | **−0.105** |

**The +2.9 pp is a property of the LOSS, not of the architecture.** Both ceilings rise together and
Δcat moves by 0.26 pp — if anything *toward* MTL. Every category number at the small states was ~3 pp
too low; the **MTL-vs-dedicated verdict is unchanged** and now rests on two correctly-calibrated arms
instead of two mis-calibrated ones.

**Methodological note worth keeping:** reporting row 11 without row 12 would have produced a 3 pp
swing that was pure measurement asymmetry — the baseline handed a tool the joint model was never
offered. That is the failure mode `CEILINGS_N20_FINAL` calls baseline sabotage, pointed the other way.

### 9.4 Two honest loose ends

**Region is not quite untouched.** Logit adjustment is category-only by construction, and AL/AZ agree
(Δreg −0.043 p=0.65, −0.042 p=0.61). But **istanbul shows −0.081 at p=0.002**. The magnitude is
negligible; the consistency is not. Most likely shared-trunk coupling — changing the category loss
perturbs the shared gradients and hence the region head. Recorded rather than rounded away; it
changes no verdict.

**The loss split does NOT reverse — alabama was a one-state artefact. RESOLVED 2026-08-09.**

Alabama alone suggested calibration flipped the split (−0.273 null → **+0.445, p=0.024**). Measured at
all three states, it does not replicate:

| state | Δcat (cw0.50 − cw0.75) | p | Δreg | p |
|---|---:|---:|---:|---:|
| alabama | **+0.445** | **0.024** | −0.060 | 0.52 |
| arizona | +0.101 | 0.42 | **−0.188** | **0.010** |
| istanbul | **−0.308** | 0.17 | **−0.180** | **0.007** |
| **mean** | **+0.079** | | **−0.143** | |

Category is a **tie** (mean +0.079, significant at one state, *negative* at istanbul). Region prefers
**cw0.75 at all three**, significantly at two. The pre-registered rule — *"when category ties, break
on region"* — therefore selects **cw0.75**, unchanged. Region's preference for cw0.75 survives
calibration, exactly as it held before it.

⚠ **A process error worth recording.** The driver's automatic selector compared **category means
only** and so chose cw0.50, contradicting the pre-registered rule. The batch-size re-run started on
the wrong split and was killed ~90 s in, before any arm completed; no results were affected. The
selector has been replaced with the fixed pre-registered value and the reasoning written into the
script. This is the **second** time an automated shortcut silently substituted a simpler proxy for a
pre-registered rule (the first picked the row-7 winner on category alone) — both times the rule
existed precisely to prevent that.

---

## 10 · Row 10b — batch size re-measured on the adopted recipe

The original row 10 measured batch size on the **class-weighted** recipe that logit adjustment has
since superseded by ~3 pp, so it was re-run at cw0.75 + τ=0.5.

| bs | lr× | cat sm3 | reg | geom | Δcat | Δreg |
|---:|---:|---:|---:|---:|---:|---:|
| **8192** | 1.00 | 30.0168 | **69.6530** | 45.725 | — | — |
| 16384 | 1.67 | 30.2977 | 69.4952 | **45.886** | +0.281 | −0.158 |
| 16384 | 2.50 | 30.3568 | 68.8547 | 45.719 | +0.340 | −0.798 |
| 16384 | 3.33 | 30.2293 | 69.0395 | 45.684 | +0.212 | −0.614 |
| 32768 | 1.67 | 30.5590 | 68.4685 | 45.742 | +0.542 | −1.184 |
| 32768 | 2.50 | 30.5846 | 68.1934 | 45.669 | +0.568 | −1.460 |
| 32768 | 3.33 | **30.8543** | 67.5446 | 45.651 | **+0.837** | **−2.108** |

**Verdict unchanged: keep bs8192.** But calibration made the mechanism legible — it is now a clean
**monotone trade**: every increase in batch size or LR buys category and pays region in lockstep, and
the largest step (bs32k ×3.33) has both the biggest gain (+0.84 cat) and the biggest loss (−2.11 reg).

⚠ **A correction to the original row 10's reading.** On the class-weighted recipe the category column
was scattered with no LR trend, which was interpreted as noise from step starvation. Under
calibration the category side is orderly and monotone, so that scatter was substantially the
**mis-calibrated loss**, not the batch size. The *region* conclusion is unchanged either way.

Honest note: bs8192 (geom 45.725) and bs16384 ×1.67 (geom **45.886**) are effectively tied, and the
latter is ~45 s faster. Not adopted — n=5 at one state, and switching would force regenerating every
joint cell for a 0.16 geom difference.


---

## 11 · Follow-ups A–C and row 3b — results (these were run; §8 only listed them as queued)

### 11.1 Step A — dedicated class weights at AZ / IST (5 folds), mapping the size-dependence

| state | lr | ON sm3 | OFF sm3 | Δ (OFF−ON) | p |
|---|---:|---:|---:|---:|---:|
| arizona | 0.0005 | 31.6675 | 31.1194 | -0.548 | 0.362 |
| arizona | 0.005 | 31.1028 | 30.5804 | -0.522 | 0.598 |
| istanbul | 0.0005 | 32.0772 | 31.8098 | -0.267 | 0.310 |
| istanbul | 0.005 | 30.9978 | 31.1756 | +0.178 | 0.717 |

Both arizona LRs agree (−0.548 / −0.522), so the effect is a property of the state, not an
interaction with the schedule. Istanbul **flips sign between its two LRs** (−0.267 / +0.178), i.e.
indistinguishable from zero either way. Per-fold signs are split at both states, so these two
middle points are **weak**, not firm.

### 11.2 Step B — TX class weights, 3 folds, same seed, 50 epochs (the decisive large-state arm)

| fold | ON | OFF | Δ |
|---:|---:|---:|---:|
| 0 | 33.6127 | 35.1696 | **+1.557** |
| 1 | 33.6640 | 35.6980 | **+2.034** |
| 2 | 32.9860 | 34.0636 | **+1.078** |
| **mean** | **33.4209** | **34.9771** | **+1.556** |

**sd 0.478, paired t = +5.64, p = 0.0301** — all three folds positive.
Row 6's original single-fold +1.176 (at 75 ep) was the *conservative* estimate; at 50 ep it is +1.56.

**The size-graded class-weight picture** (Δ = OFF − ON, dedicated arm):

| state | windows | Δ | folds | p |
|---|---:|---:|---:|---:|
| alabama | 96 k | **−1.203** | 5 | **0.004** |
| arizona | 201 k | −0.535 | 5 | 0.36–0.60 |
| istanbul | 272 k | ≈ 0 (sign-unstable) | 5 | 0.31–0.72 |
| **texas** | **3,830 k** | **+1.556** | 3 | **0.0301** |

Monotone in data volume with **both endpoints significant and opposite in sign**; the two middle
states sit on the crossing as nulls. ⚠ **But see §12** — logit adjustment may supersede this rule
entirely, since it *replaces* class weighting.

### 11.3 Step C — TX dedicated batch size, 1 fold, class weights OFF

| bs | sm3 | argmax | argmax−sm3 | best ep | wall |
|---:|---:|---:|---:|---:|---:|
| **8192** | **35.1696** | 35.1696 | **0.000** | [6] | 1116 s |
| 16384 | 35.0585 | 35.3998 | 0.341 | [10] | 1119 s |
| 32768 | 34.6175 | 35.1556 | 0.538 | [11] | 1117 s |

Monotone decline (−0.11, −0.55) and **no wall-clock saving at all** (1116/1119/1117 s). The
`argmax−sm3` gap grows with batch size (0.000 → 0.341 → 0.538): fewer optimizer steps make the
validation curve spikier and the argmax less trustworthy. Same mechanism as row 10 at alabama, at
the opposite end of the size range — so bs8192 is **directionally consistent at a large state**.
⚠ Not "confirmed": this is **one fold**, so there is no dispersion, no paired test and no interval.
A clean monotone direction at n=1 is a screen. Only alabama (5 folds) actually confirms bs8192.

### 11.4 Row 3b — FL MTL cat-LR grid, 1 fold

| cat-lr | ep | cat sm3 | cat argmax | reg |
|---:|---:|---:|---:|---:|
| 0.0005 | 50 | 36.1213 | 36.4909 | 77.3470 |
| 0.001 | 50 | 36.3369 | 36.4161 | 77.3921 |
| 0.001 | 25 | 36.2987 | 36.3037 | 77.4729 |
| 0.002 | 50 | 36.3842 | 36.6709 | 77.3752 |

**sm3 span 0.263 across the 4× LR range** — essentially identical to AL (0.22), AZ (0.21), IST
(0.28). So **cat-LR is null at all four states tested** (AL/AZ/IST at 5 folds, FL at 1) — CA/TX
untested. Not "closed": FL contributes a single fold, and no large state has a 5-fold measurement.
One state-dependent detail: the 25-epoch arm behaves *oppositely* to alabama — at FL it **gains**
+0.08 reg (the best region number in the table) at half the wall time, where at AL it cost −0.79.

### 11.5 A free bit-reproducibility check

Stage 1's driver independently re-ran all four row-3 arms with a **separate inductor cache**.
Every one reproduced to **Δ = 0.0000** (four decimals):

| arm | run 1 | run 2 |
|---|---:|---:|
| catlr0.0005_ep50 | 27.1045 | 27.1045 |
| catlr0.001_ep50 | 27.3836 | 27.3836 |
| catlr0.002_ep50 | 27.5131 | 27.5131 |
| catlr0.001_ep25 | 27.6177 | 27.6177 |

An unplanned duplicate (a scoping slip) turned into evidence that this configuration is
bit-reproducible under `--compile`, which `CLAUDE.md` treats as not guaranteed.

### 11.6 ⚠ Open: does logit adjustment SUPERSEDE the class-weight rule?

`--logit-adjust-tau` **replaces** class weighting — `next_cv.py:123-141` and `mtl_cv.py:481-484`
both make the weighted CE the `else` branch. If logit adjustment is adopted board-wide, then the
size-tiered class-weight rule in §11.2 governs a configuration **we no longer ship**, and the
texas +1.556 becomes a background finding rather than a recipe rule. **This is unresolved and is
the first thing an auditor should check.** Logit adjustment has only been measured at AL/AZ/IST —
never at a large state — so it cannot yet simply replace the tiering at TX/CA.

---

## 6 · What an auditor should check hardest

1. **§3.2 and §3.3 are corrections**, not fresh findings. An earlier version of this study reported
   the class-weight effect as a lever and pre-registered a tie-break on alabama-only data. Both are
   restated here against three states. Check I have not quietly kept the flattering version.
2. **n = 5, one seed, everywhere in this sweep.** Every p-value is a 5-fold paired test. Nothing here
   is n=20 evidence.
3. **The dedicated retune is the only multi-state, same-direction result.** If you discount one
   thing, discount the MTL knobs, not this.
4. **Large states are untested** (rows 5/6/3b queued, 1 fold). The size-inverted failure mode means
   the small-state recipe may not transfer — [`POSTPONED.md`](POSTPONED.md) P6.
5. **Selector honesty**: istanbul's argmax-vs-sm3 disagreement in §2 is the clearest case where the
   two conventions pick different winners. Both are reported everywhere for that reason.
