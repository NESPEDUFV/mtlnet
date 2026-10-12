# Majority-class floor, per state — closing the "5.7 to 7.3" range

> **Status: derived, not trained.** This is a closed-form calculation from an already-published
> table, not a new v18 run. No sidecar, no rundir, no GPU. Written to answer a defense-prep
> question: the dissertation states the majority-class floor spans **5.7 to 7.3 macro-F1** across
> the six Ch. 5 datasets and names only the minimum's dataset (Florida). Which dataset gives the
> maximum was never printed anywhere in the delivered material — this note derives it.

## 1 · Where "5.7 to 7.3" comes from, and what's missing

`src/chapters/5_mobiwac/06_results.tex` (p. 80 of `banca.pdf`):

> "always predicting the most common category reaches between 5.7 and 7.3 macro-F1 depending on
> the dataset (the majority-class floor, lowest at Florida, whose category mix is the most even)"

Checked and confirmed absent from the delivered material:
- `tables/mobiwac/results.tex` (Table 10) has no majority-floor row — its category-block reference
  columns are Markov-K and POI-RGNN only.
- No draft of the MobiWac paper (`articles/[mobiwac]/src/`, `src_fix/`, `src_v1/`) tabulates the
  floor per dataset either; `src_v1` only ever states a single aggregate "~7%".
- No file under `docs/results/` is named for this quantity.

So the maximum's dataset was never disclosed in writing. It is derived below.

## 2 · Closed-form macro-F1 of a constant "always predict Food" classifier

Food is the majority class in all six Ch. 5 datasets (`5_mobiwac/05_setup.tex:30`,
`tables/mobiwac/datasets.tex` caption). For a classifier that always predicts the majority class
`m` on a test set where `m` occurs with frequency `p`, over `C = 7` categories:

- `Recall_m = 1` — every true instance of `m` is among the predictions (all predictions are `m`).
- `Precision_m = p` — of all predictions (100% of the test set), the fraction actually equal to `m`
  is `p`.
- `F1_m = 2·p / (1 + p)`.
- Every other class `c ≠ m`: `Recall_c = 0` (never predicted), so `F1_c = 0` regardless of
  precision convention.
- `macro-F1 = (1/C) · F1_m = 2p / (C·(1 + p))`, with `C = 7`.

This is exact (no approximation) for any fold whose majority-class frequency is `p`; it is the same
computation `sklearn.metrics.f1_score(average='macro', zero_division=0)` would return for a
constant predictor.

Per `AGENT_GUARDRAILS.md` N2 ("agents quote; they do not compute" — derived quantities come from a
script committed to the repo, then are quoted), this formula is implemented in
[`majority_class_floor.py`](majority_class_floor.py), not evaluated in prose. §4 quotes that
script's output verbatim.

## 3 · Input: the published per-state majority share (Table 8)

`src/tables/mobiwac/datasets.tex:30-35`, column **Majority (%)** — "share of next-visit labels in
the most common category (Food in every dataset)," computed on the same next-visit target labels
the category task trains and evaluates on:

| Dataset | Majority (%) — `p` |
|---|---|
| FL | 24.7 |
| TX | 31.0 |
| CA | 32.7 |
| Istanbul | 33.4 |
| AZ | 34.0 |
| AL | 34.2 |

The table's hidden provenance comment (`datasets.tex:9-12`) adds two precision notes worth
carrying forward: the Gowalla values match an independent windowing to ≤0.5 pp (AL measured 34.18
there, which rounds to the printed 34.2); and the Istanbul 33.4 comes from an earlier windowing of
the same visits, with a note that exact recomputation on the current `dk_ovl` substrate was left
for "the next A40 session" — i.e., Istanbul's third-decimal precision is not guaranteed the way the
five Gowalla states' is. This does not change the ranking below, only its precision at Istanbul.

## 4 · Result: per-state majority-class-floor macro-F1

Output of `python3 majority_class_floor.py`, quoted verbatim (2026-08-25):

```
Dataset     Majority (%)   Majority-floor macro-F1 (%)
FL                  24.7                          5.66
TX                  31.0                          6.76
CA                  32.7                          7.04
Istanbul            33.4                          7.15
AZ                  34.0                          7.25
AL                  34.2                          7.28
```

Rounded to one decimal (the dissertation's own precision for this range): FL 5.7, TX 6.8, CA 7.0,
Istanbul 7.2, AZ 7.2, AL 7.3.

**The maximum is Alabama, 7.3 — not Texas.** (Texas, despite being one of the two largest datasets,
sits mid-range at 6.8; dataset size does not drive this number — only how lopsided the category mix
is. Larger states here happen to have a *more even* Food share, not less.)

## 5 · Self-check: this reproduces both published bounds

Neither endpoint was fit to the published range — both fall out of the formula applied to the
already-printed Table 8 column:

- **Minimum:** 5.66 rounds to **5.7**, matching the dissertation's stated minimum, at the
  dissertation's stated dataset (Florida). ✓
- **Maximum:** 7.28 rounds to **7.3**, matching the dissertation's stated maximum. ✓ (its dataset
  was the one unstated fact this note recovers: Alabama.)

Both endpoints reproducing exactly is strong internal evidence the closed-form is the same
computation behind the printed "5.7 to 7.3," not a coincidentally similar one.

## 6 · Caveat

This uses the **whole-dataset** majority share printed in Table 8, not a fresh per-fold
recomputation from the actual v18 stratified test folds. Because the Ch. 5 splits are stratified by
the next-category label (`5_mobiwac/05_setup.tex:30`), each fold's local majority share should
track the whole-dataset share closely — the Gowalla cross-check above bounds that drift at ≤0.5 pp,
which moves a macro-F1 value by a few hundredths of a point at most, not enough to change the
ranking or the rounded values in §4. Istanbul carries the extra, unresolved precision caveat from
§3. If a per-fold, v18-exact recomputation is wanted before the defense (e.g., to quote more than
one decimal place), it would need `CATEGORY_DISTRIBUTION.md`'s per-fold counts or a fresh pass over
the v18 fold assignments — not done here.

## 7 · Provenance

- Range "5.7 to 7.3", Florida named as minimum: `src/chapters/5_mobiwac/06_results.tex:54-56`
  (`banca.pdf` p. 80); identical text in `articles/[mobiwac]/src_fix/sections/06_results.tex:54-55`.
- Majority-class-floor definition: `src/chapters/5_mobiwac/05_setup.tex:111` (`banca.pdf` p. 76).
- Majority (%) column: `src/tables/mobiwac/datasets.tex:30-35` (Table 8, `banca.pdf` p. 8), hidden
  provenance comment at lines 9-12.
- Formula: standard macro-F1 definition (`src/chapters/2_fundamentals.tex:1626-1641`) specialized to
  a constant classifier; not separately cited in the dissertation.
