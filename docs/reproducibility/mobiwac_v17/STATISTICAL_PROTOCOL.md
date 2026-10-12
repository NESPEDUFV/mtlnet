# ../v17_completion/STATISTICAL_PROTOCOL.md — pre-registered analysis plan for the closing_data board

> **STATUS: PRE-REGISTERED. Commit this BEFORE the board unblinds.** This is the analysis plan for the
> regenerated base (the `closing_data` board): which test runs on which cell, which margins are pinned, and
> how the family is corrected — fixed *before* any cell number is read. The point is anti-p-hacking: once the
> board runs all cells once (PLAN §P3/P4), every cell is analysed by the rule written here, not by a rule
> chosen after seeing the Δ. If a cell's analysis deviates from this doc, the deviation must be logged in
> `log.md` with a reason, not silently applied.
>
> **Grounding (read these; this doc extends, it does not replace them):**
> - [`articles/[BRACIS]_Beyond_Cross_Task/STATISTICAL_AUDIT.md §0`](../../../articles/[BRACIS]_Beyond_Cross_Task/STATISTICAL_AUDIT.md) — the existing statistical machinery (the three power regimes; the n=5 ceiling; the DO/DON'T wording contract). This protocol inherits §0 verbatim and adds the per-axis margin pinning that §0 left implicit.
> - [`RUN_MATRIX.md`](RUN_MATRIX.md) §0 (frozen recipe / n=20 per cell), §1 (BRACIS-suite cells), §2 (baseline block).
> - [`../baseline_gap/TRIAGE.md`](../baseline_gap/TRIAGE.md) — B1–B5 comparability classes (SC vs E2E).
> - [`../pre_freeze_gates/BOARD_ADOPTION_DECISION.md`](../pre_freeze_gates/BOARD_ADOPTION_DECISION.md) — gated-overlap adoption; the reg-side "write as TOST non-inferiority from the start" instruction; the FL 2-seed ~−1.2 pp matched reg gap.
> - [`../pre_freeze_gates/LANE2_OVERLAP_VALIDATION.md`](../pre_freeze_gates/LANE2_OVERLAP_VALIDATION.md) — the overlap-vs-non-overlap **unpaired-across-seed** rule (different fold partitions per arm).
>
> **The task.** Joint POI **next-category** (macro-F1) + **next-region** (Acc@10) MTL. The board freezes a base
> (champion G / v16 on the v14 substrate, RUN_MATRIX §0) then runs all cells once at **n=20/cell** (6 states ×
> seeds {0,1,7,100} × 5 folds; FL auxiliary axes may reach n=25 with seed 42 added). Tests below operate on the
> matched-scorer per-fold outputs (cat macro-F1; reg FULL fp32 `top10_acc` on BOTH MTL and STL sides — the
> B-A2 correction, RUN_MATRIX §0).

---

## 0 · The one paragraph that pins what §0 left open (READ FIRST)

`STATISTICAL_AUDIT §0.3` pre-registered TOST non-inferiority at **δ ∈ {2 pp, 3 pp}** for the **SUBSTRATE
axis** — the Check2HGI-vs-HGI "ties" on CA/TX (the CH15 reframing). **That margin was scoped to the substrate
axis and MUST NOT be silently reused for the MTL-vs-STL reg-parity claim.** The two claims live on different
axes, different comparisons, different noise scales; reusing a substrate-axis margin for an MTL-axis claim is
exactly the kind of post-hoc convenience this pre-registration exists to forbid. This protocol therefore pins
a **separate, axis-specific** margin **δ_reg** for the MTL-vs-STL reg-parity claim (§3.2) and flags it as a
**user-confirm parameter**. Under the adopted gated-overlap board the matched MTL-vs-STL reg gap is
~**−1.2 pp** (FL, 2 seeds — `BOARD_ADOPTION_DECISION.md`), so the equivalence margin is load-bearing: the
claim's verdict ("non-inferior" vs "fails non-inferiority") depends on which δ_reg we committed to *before*
looking. We commit it here.

---

## 1 · The two comparison families

| Family | Comparison | Headline? | Direction | Primary test |
|---|---|---|---|---|
| **(A) MTL-vs-STL** | champion-G MTL vs our STL ceiling, **same substrate, same folds** | **YES — the headline** | cat: superiority (MTL > STL); reg: **non-inferiority** (MTL not worse than STL by more than δ_reg) | cat → paired Wilcoxon (§2); reg → **TOST** (§3) |
| **(B) baselines-vs-ours** | each external/substrate baseline vs our STL ceiling AND vs our MTL champion | supporting | superiority (we beat baseline X) | paired Wilcoxon (§2), with Holm correction across the grid (§5) |

Family (A) is the paper's thesis: *one joint model, one forward, N tasks* — beats category, non-inferior on
region. Family (B) situates that model against the SOTA-equivalent literature and the substrate floor. They
are analysed under the same test toolkit but reported and corrected separately (§5 corrects the baseline grid;
the headline MTL-vs-STL cells are a small fixed family, §5.2).

---

## 2 · Superiority / directional claims → paired Wilcoxon signed-rank

**Use for:** "MTL cat > STL cat" (family A); "we beat baseline X" on either task (family B); any claim with a
sign.

**Test.** Paired Wilcoxon signed-rank on the matched per-fold Δs, **multi-seed pooled** (n=20 = 4 seeds × 5
folds; FL auxiliary axes n=25 = 5 seeds × 5 folds). One-sided in the pre-registered direction; report fold/pair
positivity alongside p.

**Pairing requirement.** Only valid when the two arms share the **same folds** (same engine slot, same fold
construction, same windowing) — see §4. Where pairing fails, drop to unpaired across-seed (§4).

**The single-seed ceiling (inherited from `STATISTICAL_AUDIT §0`, state it once in the paper):** single-seed
n=5 paired Wilcoxon has a maximum achievable significance of **p = 0.0312 one-sided / 0.0625 two-sided**
(5/5 folds in the claimed direction). A "p = 0.0312, 5/5 positive" cell is *at-ceiling for n=5*, not
"barely significant." The board runs at n=20 by default, which breaks this ceiling and reaches sub-1e-4
p-values where the effect is real; the ceiling note is retained only for any cell that ends up single-seed
(e.g. a deferred baseline run at one seed).

**Reporting (per cell, §6):** Δ (pp), n_pairs, "paired Wilcoxon", one-sided p + direction, fold/pair
positivity (e.g. 19/20 positive), effect size relative to multi-seed σ.

---

## 3 · Equivalence / "matches" claims → TOST non-inferiority (margin pinned PER AXIS)

**Use for:** any "matches" / "ties" / "non-inferior" / "Pareto-non-inferior" claim. A non-significant Wilcoxon
is **NOT** evidence of equivalence — absence of a detected difference is not the same as a demonstrated
bound. Equivalence claims require **TOST** (two one-sided tests) against an explicit margin δ, reporting the
TOST p **and** the confidence interval versus δ.

**The per-axis margin rule (the core of this pre-registration).** Every equivalence claim names the axis it is
on and uses that axis's own pre-registered δ. Two axes are in play:

| Axis | Claim | Pre-registered margin | Provenance | Status |
|---|---|---|---|---|
| **Substrate** (Check2HGI vs HGI, CA/TX "ties") | substrate-equivalence | **δ ∈ {2 pp, 3 pp}** | `STATISTICAL_AUDIT §0.3` (CH15 reframing) | inherited as-is; **do not re-derive** |
| **MTL-vs-STL reg-parity** (champion-G MTL vs STL reg ceiling) | "joint model is non-inferior on region" | **δ_reg = 2 pp** *(recommended; user-confirm)* | **THIS doc §3.2** — pinned fresh for THIS axis | **USER-CONFIRM at P2 freeze** |

These two δ's happen to share a numeric value at the recommended setting, but they are **separately
pre-registered for separately-justified reasons.** The substrate δ travels untouched from §0.3; δ_reg is
justified below on its own terms. They are not the same parameter and a change to one does not move the other.

### 3.2 δ_reg for the MTL-vs-STL reg-parity claim (the user-confirm parameter)

**Recommended: δ_reg = 2 pp on next-region Acc@10**, justified on THIS axis (not inherited):

1. **Practical negligibility.** Acc@10 is top-10 accuracy over the region label space (≈1.1k regions at AL up
   to ≈8.5k at CA). A 2 pp shift in top-10 hit-rate over thousands of candidate regions is practically
   negligible for a downstream next-region recommender — it is well inside the noise a deployment would
   tolerate.
2. **~2× the multi-seed σ.** The multi-seed standard deviation on reg Acc@10 at the board's n=20 footing is
   on the order of ~1 pp; δ_reg = 2 pp is ≈2σ — a margin tight enough to be meaningful, wide enough that
   passing it is a genuine non-inferiority result rather than an artefact of a loose bound. **Confirm the
   actual σ from the board's own STL-reg-ceiling cells before locking** (it is computed from the same n=20
   per-fold outputs); if σ materially exceeds ~1 pp at the large states, re-confirm δ_reg with the user
   rather than silently widening it.
3. **It is the margin under which the headline claim survives gated overlap.** The adopted gated-overlap
   board widened the matched reg gap from ~−0.31 pp (non-overlap, "visibly ties") to ~−1.2 pp (FL, 2 seeds).
   A −1.2 pp gap with σ~1.0 **passes** TOST non-inferiority at δ_reg = 2 pp. So the claim *"a single joint
   model is non-inferior on region (within 2 pp) and beats category by +3"* survives overlap — what is lost
   is rhetorical comfort margin, not the claim (`BOARD_ADOPTION_DECISION.md §"framing correction"`).

**This is a user-confirm parameter, NOT inherited from the substrate axis.** It is pinned here so the verdict
is decided before the numbers are read. If the user prefers a different δ_reg, change it HERE and re-commit
before unblind; do not negotiate it after seeing a cell.

**De-risk dependency (carried from `BOARD_ADOPTION_DECISION.md` Condition 1):** the FL 2-seed evidence is the
basis; the mechanism warns the gap could be worse at the large states (CA/TX, 4703+ regions). The one
large-state (TX or CA) gated-overlap reg de-risk cell is the gate: |Δreg| ≤ ~1.5 pp → comfortably inside
δ_reg = 2 pp; > 2 pp → the non-inferiority claim does not hold at that state and the board reverts to the
non-overlap base. δ_reg = 2 pp is the bar that de-risk cell is checked against.

### 3.3 TOST procedure and reporting

- Run TOST as two one-sided paired tests (the matched-fold Δs from §4) against the null that |true Δ| ≥ δ.
- **Report the TOST p AND the (1−2α) CI on the mean Δ, placed against δ.** The verdict is read off the CI: if
  the CI lies entirely within (−δ, +δ) → non-inferior (here, one-sided: CI upper bound below +δ on the
  "STL minus MTL" orientation, i.e. MTL not worse by more than δ). Quote both the p and the CI-vs-δ.
- **Never report a non-significant Wilcoxon as equivalence.** If only a Wilcoxon was run on an equivalence
  cell, the cell is **unresolved** until TOST is run — flag it, do not write "tied."

**Reporting (per cell, §6):** Δ (pp), n_pairs, "TOST non-inferiority, δ = {value}", TOST p, the CI vs δ, and
the verdict (non-inferior / fails non-inferiority / unresolved).

### 3.4 Computed results — small-state region "matches" (2026-06-25, no new runs)

Paired per-fold TOST at **δ_reg = 2 pp**, Δ = MTL champion-G reg Acc@10 − STL dedicated reg ceiling, seed 0 ×
5 folds (same frozen overlap folds → paired, §4). 90% CI = (1−2α), α = 0.05. Sources: champion =
`docs/results/closing_data/h100/{alabama,arizona}_s0_mtl_fp32_matched_score.json` (`reg_per_fold`) +
`docs/results/second_dataset/istanbul/istanbul_stride1_s0_mtl_fp32_matched_score.json`; STL ceiling =
`docs/results/P1/region_head_{alabama,arizona}_region_5f_50ep_*_ovl_stl_reg_s0.json` +
`region_head_istanbul_region_5f_50ep_istanbul_stride1_stl_reg_s0.json` (`heads.next_stan_flow.per_fold[].top10_acc`).
The per-fold Δ-means reproduce the board (AL −0.18, AZ −0.06, Istanbul −0.50) exactly. Recompute:
`research/reproducibility/mobiwac_v17/region_match_tost.py`.

| State | n_pairs | Δ (pp) | σ_d (pp) | TOST p (δ=2) | 90% CI | verdict |
|---|---:|---:|---:|---:|---|---|
| **AL** | 5 | −0.18 | 0.28 | 7e-05 | (−0.46, +0.09) | **non-inferior** (CI ⊂ ±2) |
| **AZ** | 5 | −0.06 | 0.37 | 1.5e-04 | (−0.41, +0.29) | **non-inferior** (CI ⊂ ±2) |
| **Istanbul** (s0) | 5 | −0.50 | 0.16 | 2e-05 | (−0.65, −0.35) | **non-inferior** (CI ⊂ ±2) |

**Power.** The board's per-fold region variance is σ_d ≈ 0.16–0.37 pp — far below the §3.2 working assumption of
~1 pp, so δ_reg = 2 pp is ≥ 5σ_d. At n = 5 the equivalence test has power ≈ 1.0 to declare non-inferiority when
the tasks truly match (seeded MC, σ = observed), and the 90% CI half-width (~0.3 pp) is ~7× narrower than the
margin: a true ≥ 2 pp region deficit would have been detected with probability ≈ 1 (the valid TOST is level-α at
the exact 2-pp boundary → ≥ 95% power to avoid a false "matches"). **The small-state "matches" are now a tested
equivalence claim, not an assertion.** (Istanbul paired at s0 because the STL reg ceiling exists only at s0; the
4-seed champion mean 74.28 ≈ the s0 champion 74.30, so the n=20 verdict is identical and the CI only tightens.)

---

## 4 · Pairing discipline (CRITICAL — get this wrong and every p is contaminated)

**Pair ONLY when both arms share the same folds** — same engine slot, same fold construction, same windowing,
same seed set. The paired Δ is then a true per-fold matched difference and paired Wilcoxon / paired TOST apply.
When the fold partitions differ between arms, the Δs are **not matched** and you MUST drop to **unpaired
across-seed** statistics.

| Comparison | Same folds? | Test footing |
|---|---|---|
| **MTL-G vs STL ceiling**, same substrate, **same frozen overlap folds** (family A) | **YES** | **PAIRED** per-fold (Wilcoxon for cat; TOST for reg) |
| **Overlap vs non-overlap** (e.g. the overlap-adoption validation) | **NO** — folds generated on-the-fly per arm, different windowed rows, partitions not bit-identical (`LANE2_OVERLAP_VALIDATION.md`) | **UNPAIRED across-seed** — do NOT pair per-fold |
| **SC baseline (B1 CTLE, B2a/b/c, substrate probes, SC-cascade B4) vs STL/MTL** | **YES** — SC inherits the frozen base through the matched-head pipeline (same folds/seeds/windowing/labels, only the embedding slot swaps) | **PAIRED** per-fold vs both STL and MTL |
| **E2E baseline (B3 HMT-GRN-style, B5 Flashback, faithful STAN/ReHDM/POI-RGNN/MHA+PE) vs STL/MTL** | **CONDITIONAL** — E2E builds its own sequences; **paired by fold IF and only IF it ran on the SAME user-disjoint splits + same windowing as ours**; otherwise **UNPAIRED** | paired by fold when split-matched; unpaired across-seed otherwise |

**The non-negotiable preflight for any paired cell:** assert both arms used the **same fold partition** (and,
for overlap cells, both built on the **same windowing** — the B-A2/windowing-matched trap from
`BOARD_ADOPTION_DECISION.md` Condition 3). If you cannot assert identical partitions, the cell is unpaired.
Because the board freezes folds once (RUN_MATRIX §0), every SC cell and the family-(A) MTL-vs-STL cells are
paired by construction; the only places pairing can break are overlap-vs-non-overlap comparisons (always
unpaired) and any E2E baseline that, despite the run-spec, did not mirror our splits.

**Why this matters for the headline:** family (A) is paired because MTL-G and the STL ceiling are evaluated on
the **same frozen overlap folds** — this is what licenses the per-fold paired Wilcoxon (cat) and paired TOST
(reg) at n=20. If a future re-run regenerates folds for one arm, the headline silently becomes unpaired and
the n=20 ceiling-breaking power is lost.

---

## 5 · Multiple-comparison correction

### 5.1 Family (B) — the baseline grid → Holm-Bonferroni (family-wise)

The baseline comparisons form a **grid: {baseline} × {state} × {task}** (e.g. CTLE/POI2Vec/skip-gram/one-hot/
substrate-probes/STAN/ReHDM/POI-RGNN/MHA+PE/HMT-GRN-style/cascade/Flashback × {AL,AZ,FL,CA,TX,GE} ×
{next-category, next-region}). Each "we beat baseline X at state S on task T" is one hypothesis. Across this
grid we control the **family-wise error rate with Holm-Bonferroni**.

- **State the family explicitly** in the paper/supplement: which baselines × which states × which tasks are in
  the corrected family (cells deferred to camera-ready — ReHDM CA/TX, faithful CSLSL/CatDM, DeepMove — are NOT
  in the family and are footnoted as deferred, not corrected).
- **Report both raw p and Holm-corrected p** per cell. A claim "we beat X" is paper-grade only if it survives
  Holm correction at the chosen FWER (α = 0.05) AND is in the pre-registered direction.
- Holm is applied **within each comparison-vs-arm separately** (baselines-vs-STL and baselines-vs-MTL are two
  families) so a baseline that loses to STL but ties MTL is not double-penalised.

### 5.2 Family (A) — the headline MTL-vs-STL cells

The headline family is small and fixed: {6 states} × {cat superiority, reg non-inferiority}. Apply
Holm-Bonferroni **within the cat-superiority set** (6 states) and report the reg-non-inferiority TOST cells
with their own δ_reg verdict (TOST cells are equivalence tests, not superiority tests, and are not pooled into
the cat Holm family). State this split explicitly so a reviewer sees the cat side is corrected and the reg
side is a pre-registered equivalence test, not a fished null.

### 5.3 What is NOT corrected

Descriptive cells (T1 dataset stats, F2 scatter, Markov/majority floors reported as context not as a
hypothesis test) carry no p and enter no correction family. Effect-size / σ reporting is descriptive.

---

## 6 · Per-cell reporting template (every hypothesis-bearing cell emits this)

Each cell in the board's analysis output reports, in this order:

1. **Δ** — the paired (or unpaired, flagged) mean difference, in pp, with explicit orientation (e.g.
   "MTL − STL" or "ours − baseline").
2. **n_pairs** (or n per arm if unpaired) — and the seed × fold composition (e.g. "n=20 = 4 seeds × 5 folds").
3. **Test** — "paired Wilcoxon signed-rank" / "unpaired across-seed Wilcoxon" / "paired TOST non-inferiority,
   δ = {value} pp".
4. **p + direction** — one-sided p in the pre-registered direction (and two-sided if reported), plus the
   Holm-corrected p where the cell is in a corrected family (§5).
5. **Fold/pair positivity** — e.g. "19/20 fold-pairs positive".
6. **Effect size / σ** — the Δ relative to the multi-seed σ on that metric (e.g. "Δ = +1.4 pp ≈ 8σ").
7. **For equivalence cells only:** the **TOST verdict** (non-inferior / fails / unresolved) **and the CI vs
   δ** (e.g. "90% CI on Δreg = [−1.7, −0.7] pp, entirely above −δ_reg = −2 pp → non-inferior").

A cell missing items 1–6 (or 1–7 for equivalence) is not paper-grade and is flagged in `log.md`.

---

## 7 · What to write in the paper (superiority vs non-inferiority — DO / DON'T)

Echoing the `STATISTICAL_AUDIT` DO/DON'T contract. The headline is **two different statistical claims** and
must be written as such — never collapse them into one "MTL is as good or better."

**Category (superiority):**
- **DO WRITE:** *"With the substrate fixed, the joint cross-attention model lifts next-category macro-F1 over
  the single-task ceiling at {states}, paired Wilcoxon p = {…} across n=20 multi-seed fold-pairs ({k}/20
  positive), Holm-corrected across the 6-state family."* State the AL edge case honestly if it recurs (it was
  small-significantly negative under the BRACIS frozen recipe — re-check under the new base, do not assume).
- **DON'T WRITE:** *"MTL gains on category at every state"* unless every state's corrected one-sided p lands
  positive; *"p = 0.0312"* without flagging the n=5 ceiling (the board is n=20, so this should not appear on
  headline cells).

**Region (non-inferiority):**
- **DO WRITE:** *"The joint model is non-inferior on next-region: TOST at δ_reg = 2 pp gives p = {…}, with the
  {1−2α} CI on Δreg = [{…}] lying within the ±2 pp margin, at every state where the de-risk cell confirmed the
  large-state gap stays inside the margin."* Write reg as **TOST non-inferiority from the start** — not as
  "ties" (`BOARD_ADOPTION_DECISION.md`).
- **DON'T WRITE:** *"MTL matches STL on region"* backed by a non-significant Wilcoxon (that is the forbidden
  inversion — non-significance ≠ equivalence); *"within 2 pp"* without naming δ_reg as a pre-registered
  per-axis margin distinct from the substrate-axis δ; the substrate-axis δ as if it justified the reg-parity
  claim.

**The one-sentence headline (pin the asymmetry):** *"A single joint model — one forward pass, two tasks —
**beats** single-task on next-category (superiority, paired Wilcoxon) and is **non-inferior** on next-region
(TOST, δ_reg = 2 pp), under the frozen champion-G recipe on the gated-overlap base."* Superiority and
non-inferiority are different tests with different evidence bars; the paper states both, never one.

---

## 8 · Deviation log

Any analysis that departs from this pre-registration (a different test, a different δ, a different pairing
decision, a cell promoted from descriptive to inferential) is logged in
[`DEVIATIONS.md`](DEVIATIONS.md) with: the cell, the pre-registered rule, the deviation, and the reason. Pre-registration
means the default is *this doc*; deviations are allowed but must be visible.

**2026-07-18 — paper reporting convention switched to joint-best (author ruling).** The MobiWac paper's
Table III joint cells now report the **joint-best** convention (one saved model per fold, the `geom_simple`
validation selector, both tasks read at that epoch) instead of the per-task diagnostic-best convention, per the
author ruling in `articles/[mobiwac]/review/considerations_v3.md` #10. All pre-registered tests were re-run on
the joint-best arrays before the switch: category superiority + Holm m=6 all reject (worst adjusted
p = 1.0e-06); region TOST passes at AL (Δ −0.41, 90% CI −0.63..−0.20) and AZ (0.00, CI −0.08..+0.07); region
superiority holds at Istanbul (+0.19, CI +0.15..+0.23, 20/20 folds), FL (+0.71, CI +0.67..+0.76), TX (+2.11,
CI +2.10..+2.13), and CA (+2.20, CI +2.19..+2.21). **No verdict changed.** Sources:
[`JOINT_BEST_RESULTS.md`](JOINT_BEST_RESULTS.md) + the joint-best score JSONs at
`docs/results/closing_data/catx_v17_n20/joint_best/`.

**2026-07-25 — the four executed deviations are now logged where this section mandates, and the registered
test has been run at its registered footing.** Two departures (seed-level n=4 pairing; paired t reported for
superiority) had been reasoned in [`stats/RESULTS.md`](stats/RESULTS.md) but never transcribed to
the study log. All four are frozen as **D-1 to D-4** in [`DEVIATIONS.md`](DEVIATIONS.md), including
**D-4: next-region superiority was never registered here** (§1 and §5.2 pin next-region to non-inferiority
only) and is reported as a secondary family with its own Holm correction, labeled as such in the paper and in
dissertation Ch.5. **D-3 records that the registered test now runs at all six datasets**: Istanbul's dedicated
per-fold category ceiling was recovered from the A40 and committed at
[`data/h3_istanbul/step3_runs/cat_ceiling_perfold/`](data/h3_istanbul/step3_runs/cat_ceiling_perfold/), closing
`RESULTS.md` LIMITS #2, so the §2 per-fold n=20 paired Wilcoxon with §5.2's m=6 Holm gives **ALL REJECT**,
worst adjusted p = 5.72e-06, every cell at the exact n=20 floor 9.54e-07 with 20/20 folds positive (the four
reg cells: own m=4 family, adjusted 3.81e-06). Reproduce:
[`m2_prereg_perfold.py`](../../../research/reproducibility/mobiwac_v17/m2_prereg_perfold.py) (24/24 artifact→board gate), output
[`outputs/m2_prereg_output.txt`](outputs/m2_prereg_output.txt). **No verdict changed; no reported estimate
or interval moved.** Audit of record: `articles/[mobiwac]/science/AUDIT_statistical_protocol.md`.
