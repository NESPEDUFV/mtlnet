# Nomenclature — the words this project uses for its experimental design

> **Enforcing document.** Every agent and developer touching folds, seeds, statistics or results
> uses these words with these meanings. Where our historical name differs from the literature's, the
> literature wins and the old name is listed as deprecated.
>
> This exists because a wrong name is not a cosmetic problem here: it decides what a number is a
> sample *of*, and therefore what may be claimed from it. The project already published the phrase
> "paired Wilcoxon over n=20" for 20 cells that were not 20 independent anything.

## 1 · The finding that motivated this document

`splits.build(..., seed=s)` feeds `StratifiedGroupKFold(shuffle=True, random_state=s)`, and the same
`s` also seeds weight initialisation and batch order. Measured directly — four seeds, four **distinct
user partitions**:

```
seed   0: partition 162efc6b2b4a
seed   1: partition 8757b9120c96
seed   7: partition e721b25fe486
seed 100: partition 179e105519b2
```

So what this project has been calling a **seed** is, in the literature's terms, a **repetition** of
k-fold cross-validation — a fresh partition of the users — and it *simultaneously* changes the
training randomness. **One knob, two experimental factors.** They cannot be separated in anything
run to date, and no analysis of existing results can attribute variance to one or the other.

That is a real limitation, not just a naming slip, and it must be stated wherever those numbers are
reported.

## 2 · The vocabulary

| Term | Meaning here | Literature | Our old name |
|---|---|---|---|
| **fold** | one of the K user-disjoint blocks of a single partition; k = 1..K | fold | fold ✓ |
| **partition** | one complete division of users into K folds | partition / split | *(unnamed)* |
| **repetition** | one complete K-fold pass under a NEW partition; r = 1..R | repetition, repeat (repeated k-fold CV) | **seed** ✗ |
| **replicate** | a refit with new training randomness on a **fixed** partition | random restart, initialisation seed | **seed** ✗ |
| **split_seed** | the integer that determines the partition | — | conflated into `seed` |
| **model_seed** | the integer that determines init and batch order | — | conflated into `seed` |
| **repr_seed** | the integer that determines a substrate build | — | `repr_seed` ✓ |
| **arm** | one configuration being compared (a model version, a schedule, a family) | arm, condition, treatment | `arm` ✓ |
| **cell** | one (arm, dataset, repetition) run — the unit that produces a result directory | run, configuration | `cell` ✓ |
| **lane** | which convention a reported number follows (e.g. per-task diagnostic best) | — | `lane` ✓ |
| **state / dataset** | one geographic corpus (alabama, …) | dataset | both, interchangeably |

### The three that are most often confused

**repetition ≠ replicate.** A repetition re-partitions the data; a replicate re-runs training on the
same partition. They estimate different variances: repetition includes data-partition variability,
replicate does not. Reporting one while meaning the other misstates what the interval covers.

**fold ≠ repetition.** Folds within one partition are *complementary pieces of one dataset* whose
training sets overlap ~75–80 %. They are not replicates of anything. `repetition × fold` cells are
not independent observations, and the count of them is not an inferential `n`.

**cell ≠ observation.** A cell is a unit of *execution* (it gets a directory, a result, an index
entry). Inferential `n` is a separate question answered in §4.

## 3 · What our current design actually is

**Repeated K-fold cross-validation**, R = 4 repetitions × K = 5 folds, with repetition and replicate
confounded. Not "4 seeds × 5 folds = 20 samples".

Write it as: *four repetitions of five-fold user-disjoint cross-validation (20 fits), where each
repetition also re-randomises initialisation.*

## 4 · The inferential unit — the rule that keeps being broken

| Quantity | Correct `n` | Why |
|---|---|---|
| spread of an arm's score | **R = 4** repetitions | folds are not replicates |
| paired difference between two arms | **R = 4** | one delta per repetition, folds averaged within it |
| uncertainty over USERS | number of users (thousands) | via user-cluster bootstrap on pooled out-of-fold predictions |
| "does it hold across datasets" | **6** datasets | and this is heterogeneity, not pooling |

**Never** `R × K`. **Never** `datasets × R × K`.

The paired band in `train/stats.py` follows this: `stderr` is the standard deviation of the
**per-repetition** deltas divided by √R, and it is NaN at R = 1 — the criterion refuses to answer
rather than inventing precision.

## 5 · Measured variance, so the words attach to numbers

| Source | Magnitude | What varies |
|---|---:|---|
| between folds, one arm | ~1,2 pp | which users are held out |
| between repetitions, one arm | 0,02–0,07 pp | partition + initialisation (confounded) |
| same config, two compiled runs | 0,02–0,05 pp | CUDA reduction order |
| **paired delta, band over repetitions** | **0,05–0,15 pp** | what a comparison actually fights |
| substrate rebuild | ~0,18 pp | the representation itself |

The fold term is 20–50× the repetition term **and is common to both arms**, so pairing removes it.
That is the whole reason a paired analysis detects effects an unpaired one cannot, and the reason
"no test ever finds anything" was a property of the analysis rather than of the models.

## 6 · Rules

1. **Say repetition, not seed**, when the partition changes. Say replicate when it does not.
2. **Never report `R × K` as a sample size**, in text, table, or code comment.
3. **A new design must name its factors** — `split_seed`, `model_seed`, `repr_seed` — even when one
   integer currently drives several. Recording them separately is what makes the confound visible;
   recording one `seed` is what hid it.
4. **State which quantity an interval covers**: users, repetitions, or datasets. An interval without
   its unit is not a result.
5. **`cell` is execution, never inference.**
6. When adding a factor, add it here first.

## 7 · Deprecated

| Old | Use instead | Note |
|---|---|---|
| "seed" meaning a repetition | **repetition** | `--seed` stays as the CLI flag; the *word* in prose and docs changes |
| "n=20", "20 folds", "20 runs" as an inferential n | R = 4 repetitions | the count of fits is not the count of observations |
| "fold-level standard error" | paired band over repetitions | folds are correlated by construction |
| "independent runs" for our 4 seeds | repetitions, confounded with replicates | they are not independent of the data |

## 8 · Open — a limitation to state, not to hide

Because one integer drives both the partition and the initialisation, **no result produced so far can
separate data-partition variance from optimisation variance.** Anything reported as "seed variance"
is really "partition + initialisation variance". Splitting `split_seed` from `model_seed` is a
prerequisite for ever making that decomposition, and it is tracked in
[`../studies/porting_validation/BACKLOG.md`](../studies/porting_validation/BACKLOG.md) alongside the
evaluation-protocol work.
