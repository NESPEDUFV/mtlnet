# 09 · Stats & leakage skeptic — methods kill-shot hunt

**Build audited:** `src/dissertacao.pdf` (94 pp) + `src/chapters/*.tex` at 2026-07-25 23:43.
**Date:** 2026-07-26. **Persona:** `reviewers/09_stats_leakage_skeptic.md`. Read-only.
Reproduce-first observed: every number below was read from its committed artifact before being
compared to the page; nothing was recomputed to replace a recorded value.

**Evidence consulted:** `docs/studies/closing_data/v17_completion/STATISTICAL_PROTOCOL.md` (§1–§5, §8);
`.../stats_n20/RESULTS.md` + `m2_prereg_output.txt`; `.../joint_best/JOINT_BEST_RESULTS.md`;
`.../CEILINGS_N20_FINAL.md`; `docs/studies/pre_freeze_gates/A4_RESULTS.md`;
`docs/results/embedding_eval/rescreen_cat/RESCREEN.md` + `leak_sniff_fl.csv` + `leak_sniff_resln_fl.csv`;
`docs/studies/closing_data/archive/findings/W6_ENCODER_ISOLATION.md`;
`docs/results/closing_data/capacity_matched_stl_cat/README.md`; `articles/dissertacao/GLOSSARY.md` §4.

## Verdict

**SURVIVES A HOSTILE EXAMINER, WITH CORRECTIONS.**

This is a materially stronger methodological chapter than the one I reviewed before. The specific
sentence I previously called the single weakest in the experimental chapters — the
Wilcoxon-versus-*t* substitution — **is fixed**, and fixed properly: not smoothed, but explained,
with the floor stated numerically and the registered test now actually run and reported alongside.
That is the correct repair and it closes the finding.

### The prior finding, re-checked

The current text reads:

> "The plan registered a paired Wilcoxon signed-rank test; at four seeds its exact one-sided $p$
> cannot fall below $0.0625$, so we report a paired $t$ on the per-seed means, with the 90\%
> confidence interval of the paired difference, and the registered test alongside it. Both, and this
> departure, are released with the code."
> — `src/chapters/5_mobiwac.tex:394` (rendered p. 67)

and the registered test's result is reported at `:643-645` (rendered p. 72):

> "The registered Wilcoxon test on the individual fold / differences agrees at every dataset, with
> all 20 folds favoring the joint model / (corrected $p<0.001$)."

I verified this against `m2_prereg_output.txt`: the per-fold n = 20 Wilcoxon runs at all six
datasets, 20/20 folds positive at every one, exact p = 9.5367e-07, Holm-adjusted (m = 6) 5.7220e-06,
all reject. The claim "agrees at every dataset, with all 20 folds favoring the joint model" is
exact. The prior version of this text reported only the *t* and characterized the Wilcoxon as
under-powered without running it at its registered footing; the round both ran it and disclosed the
departure. **Finding closed.**

The single weakest methodological sentence in the current chapters is now a different and much
smaller one (S-01 below).

**Severity summary:** 0 BLOCKER, 2 MAJOR, 4 MODERATE, 3 MINOR.

## The single weakest methodological sentence

> "The equivalence is well powered: the paired difference's standard deviation is 0.01 to 0.18 points
> across the datasets, and the intervals pass a margin as small as one point at Alabama and Arizona
> (Section~\ref{sec:mobiwac:results-part2})."
> — `src/chapters/5_mobiwac.tex:394`, rendered p. 67

See S-01.

---

## Ranked findings

### S-01 · MAJOR · "Well powered" is a post-hoc precision argument wearing a design-power label

**The attack.** An examiner who works on equivalence testing will stop here. "Well powered" is a
statement about the probability of rejecting the null under an assumed effect, fixed *before* data.
What the sentence supplies is the *observed* standard deviation of the paired difference and the
*observed* interval width — quantities that exist only after unblinding. This is precisely the
"post-hoc power dressed as design power" pattern. Nothing in `STATISTICAL_PROTOCOL.md` §3 pins a
target power or an assumed effect size; §3.2 pins the margin (δ_reg = 2 pp) as a user-confirm
parameter and nothing else. So the label has no pre-registered referent.

The underlying argument is *sound* — an interval of ±0.08 pp against a 2 pp margin is overwhelming
evidence of equivalence, and it is honest to say so. The chapter simply names it wrong.

**What the text must say to survive it.** State the observed precision and let it speak: the paired
difference's sd is 0.01 to 0.18 points, and at Alabama and Arizona the 90% intervals sit inside a
one-point margin, an order of magnitude tighter than the two-point margin the claim needs. No power
word required. If the author wants a power claim, it needs a pre-registered target and an assumed
effect, and I found neither in the protocol.

### S-02 · MAJOR · The fixed-partition caveat is absent from the chapter that reports the intervals

**The attack.** All four seeds reuse one fold partition. The reported 90% confidence intervals
therefore describe uncertainty over random initialization *conditional on that partition* — they do
not cover the variance a different user split would produce. With n = 4 and a single partition, the
intervals at Alabama (−0.63 to −0.20) and Arizona (−0.08 to +0.07) are extremely tight; an examiner
will ask whether that tightness is a property of the estimator or of the fixed split, and the
chapter does not answer.

The document *knows* this. Chapter 1 says it:

> "All / four seeds reuse the same fold partition, so the reported intervals do not / cover
> uncertainty over resampled user splits."
> — `src/chapters/1_introduction.tex:245-247`

`STATISTICAL_PROTOCOL.md` §4 is explicit that the fixed-fold construction is what licenses the
pairing at all ("this is what licenses the per-fold paired Wilcoxon (cat) and paired TOST (reg) at
n=20"). I grepped Chapter 5 for every phrasing of the consequence — `do not capture`,
`split-to-split`, `another partition`, `different partition`, `reuse the same fold` — and found
**zero occurrences in prose**. The chapter states the pairing (`:394`) but not what the pairing
costs.

**What the text must say to survive it.** One clause at the interval list in §5.6.2 or in §5.5.3:
the four seeds share one fold partition, so these intervals quantify initialization variance at that
partition and not resampling variance over user splits. This is a *defense the work already has* —
the protocol's fixed-fold design is deliberate and correct — that the text fails to state. Per this
persona's hard limits, that distinction matters: the method is not flawed, the text is silent.

### S-03 · MODERATE · The freeze control's single-seed footing is stated in Ch.5 and lost in Ch.6

Chapter 5 handles this correctly and at some length:

> "The control predates the results of / Table~\ref{tab:mobiwac:results} and was measured at one
> random initialization / over five folds, so its second comparison is to the joint scores of the /
> development configuration current at the time ($63.56$, $63.39$, $79.82$), which / it matched to
> within $0.3$, and not to the joint cells reported here."
> — `5_mobiwac.tex:664-668`

I verified every number against `W6_ENCODER_ISOLATION.md` §2: probe cat AL 63.50 / AZ 63.67 /
FL 79.79; Δ vs ceiling +7.63 / +6.54 / +4.64; full-MTL comparand 63.56 / 63.39 / 79.82. All exact.
I also verified the deltas reconcile against the table the prose names (Table 9, the one-fixed-
configuration column): 63.50 − 55.87 = 7.63, 63.67 − 57.13 = 6.54, 79.79 − 75.15 = 4.64. Pointing
them at Table 9 rather than Table 10 is the right choice and the source comment (`:674-679`) shows
it was a deliberate one.

**Is the restatement now honest?** Yes. It names the comparand, time-indexes it, states the
measurement footing, and explicitly refuses the comparison to the reported cells. That is more
disclosure than the source document demanded.

**The residual attack** is Chapter 6, which repeats the mechanism claim with the dataset scope but
without the footing (`6_conclusion.tex:92-95`). An examiner reading the conclusion learns that a
control supports the trunk attribution and does not learn it was one seed against the chapter's
n = 20. *What it must say:* carry the "one random initialization over five folds" clause into Ch.6.

**One thing the record contains that no chapter states:** `W6_ENCODER_ISOLATION.md` §4 notes a
2026-07-01 finding that "dropout stayed active in the fixed stream", with W6 recording the
directional conclusions as standing. The Chapter 5 source comment (`:687-688`) says explicitly "Not
surfaced in prose." That is an author decision I am flagging, not overriding: a hostile examiner who
obtains the artifact record will find it, and the honest framing ("the fixed stream retained
dropout; the directional conclusion is unaffected") costs one clause.

### S-04 · MODERATE · The third limitation is a real improvement, and its last sentence is the load-bearing one

New this round (`5_mobiwac.tex:736`, rendered p. 73):

> "Second, epoch selection consults the fold that the score is then read on
> (Section~\ref{sec:mobiwac:setup-windows}), so every absolute score reported here is optimistic.
> The comparison between the joint model and the dedicated models is affected far less, for two
> reasons that we can state rather than assume: the selection rule is applied identically to both
> arms on the same folds, and the dedicated arm receives the wider search, a per-dataset sweep over
> batch size and learning rate against one configuration held fixed across all six datasets for the
> joint model. The residual therefore favors the comparator, which makes the reported difference
> conservative. It does not follow that the bias cancels exactly."

This answers the tuning-leakage attack (attack surface item 3) properly: it concedes the absolute
scores are optimistic, gives two *verifiable* reasons the delta is protected, and then refuses to
claim exact cancellation. The in-source comment (`:737-749`) records that this deliberately
**weakens** a drafted sentence which had claimed the bias "cancels in the difference" — the draft
came from my own predecessor's report, and the author's team correctly declined to adopt its
overclaim. That is the anti-dilution rule running in the right direction, and I want it on record
that the weaker sentence is the better one.

**Remaining attack.** "The residual therefore favors the comparator" is an argument, not a
measurement, and "therefore" carries more weight than the two facts strictly support: a wider search
for the dedicated arm makes the *dedicated* arm's absolute score more optimistic, which does make
the reported gain conservative — but only if the two arms' selection biases are of comparable
magnitude, which is not established. *What it must say:* "favors the comparator" → a hedge such as
"points in the direction of the comparator". The final sentence already does most of this work.

### S-05 · MODERATE · No third split, stated once, and its consequence stated once — but in different places

`5_mobiwac.tex:365`: "The held-out fold is the validation data; we reserve no third split."
`5_mobiwac.tex:736`: the optimism consequence, ~370 lines later.

The disclosure and its consequence are both present, which is more than most papers manage. The
attack is only that a reader meeting the first sentence in §5.5.2 gets no signal that it matters
until §5.7. A forward pointer at `:365` ("with the consequence for absolute scores stated in
Section~\ref{sec:mobiwac:discussion}") would close it. MODERATE because the material is all there.

### S-06 · MODERATE · Preprocessing symmetry is asserted for the joint/dedicated pair, and unevenly disclosed for the externals

The joint-vs-dedicated arms share folds, windowing, and selection rule — stated at `:736` and
verifiable in the protocol. Good.

The externals are disclosed at differing granularity in the Table 10 footnote (`:602-607`):
HMT-GRN "on our folds, scored on visits whose region appears in training, $>$99\% of test visits in
every dataset and fold"; STAN "our re-implementation" with "$^{\dagger}$STAN partial folds: TX 4/5,
CA 2/5 (seed 0)"; ReHDM "its own protocol" with "$^{\ddagger}$ReHDM at TX and CA: a single seed".
This is honest and the subset sizes are given, which is what attack-surface item 5 asks for. The
gap: STAN's partial-fold cells (TX 61.67, CA 58.52) and ReHDM's single-seed cells (48.81, 50.26) are
compared against four-seed joint cells in the Chapter 5 conclusion's "at least 4 Acc@10 points over
the strongest region reference" claim (`:761`) without the claim itself noting the asymmetry. The
footnote carries it; the claim does not.

I recomputed the floor from Table 10 to check whether the asymmetry could flip it: the strongest
external per dataset is HMT-GRN or ReHDM or STAN, and the minimum joint-minus-strongest gap is
**+4.32** (Alabama, where the strongest external is ReHDM at 65.38 on a full protocol). So the claim
does not rest on a partial-fold cell. **The claim is safe;** the disclosure could travel with it.

### S-07 · MINOR · Multiplicity: both families enumerated, and the unregistered one is labeled

`5_mobiwac.tex:394`: "with a Holm correction~\cite{holm1979} across the six next-category
comparisons and, separately, across the four next-region ones."

And, critically, the chapter discloses that the region-superiority family was **not** pre-registered:

> "It assigned the tests per task, not per dataset, and did not cover next-region superiority, so the
> four next-region gains of Section~\ref{sec:mobiwac:results-part2} are secondary results outside
> it."

This matches `STATISTICAL_PROTOCOL.md` §8 deviation D-4 verbatim in substance ("next-region
superiority was never registered here ... and is reported as a secondary family with its own Holm
correction, labeled as such in the paper and in dissertation Ch.5"). Both families are enumerated,
the correction is applied within each, and the equivalence cells are correctly excluded from both
(`m2_prereg_output.txt`: "AL and AZ are equivalence cells ... and are NOT in this family, nor in the
category family"). **This is textbook and needs no change.**

### S-08 · MINOR · Pre-registration honesty: the artifact exists and is named

> "A written analysis plan, fixed during development and before any result was read, assigned one
> test to each task, with the two-point margin pinned there"
> — `5_mobiwac.tex:394`

`STATISTICAL_PROTOCOL.md` header: "STATUS: PRE-REGISTERED. Commit this BEFORE the board unblinds."
§3.2 pins δ_reg as a per-axis, user-confirm parameter and §0 explicitly forbids reusing the
substrate-axis margin for the MTL axis. The chapter's margin justification is operational, not
statistical, and is given at `:394` ("a mobility-aware service acts on which region will be busy,
not on a single rank position ... so a two-point shift in Acc@10 is below the granularity at which
such a service would behave differently"). That is an a-priori operational argument, which is what
attack-surface item 7 requires. **Holds.**

### S-09 · MINOR · Development-seed contamination: partially addressed

"The weights were tuned once on validation during development and held fixed across all six
datasets" (`5_mobiwac.tex:269`) and the analysis plan was "fixed during development and before any
result was read" (`:394`). What is not stated is whether the four reporting seeds {0,1,7,100} were
disjoint from any development seed. The protocol uses the same seed set throughout, and W6 and the
A4 audit both ran at seed 0 — which is also a reporting seed. An examiner may ask whether recipe
decisions taken on seed-0 development runs contaminate the seed-0 reporting cell. The effect is
bounded (one of four seeds) and the deltas are 60–300 σ, so nothing turns on it. *What it must say,
if anything:* one clause noting the development and reporting seed sets overlap and that the effect
is bounded by 1/4 of the reporting mass.

---

## Leakage: attack surface worked systematically

| # | Channel | Text's defense | Verdict |
|---|---|---|---|
| 1 | Split axis and overlap×fold interaction | "We split by user with stratified five-fold cross-validation, so all of a user's windows fall in the same fold and overlap cannot leak: a test user's visits never appear in training" (`:365`) | **Closed.** The sanctioned defense is stated *as the reason* overlap cannot leak, which is exactly what the persona asks for |
| 2 | Transductive artifacts | four grounds at `:367`; scope stated (67–87% coverage), unseen-places residual named | **Bounded and honestly scoped** — see below |
| 3 | Tuning leakage (no third split) | `:365` discloses; `:736` states the consequence | **Closed**, modulo S-04/S-05 |
| 4 | Development-seed contamination | partial | see S-09 |
| 5 | Preprocessing symmetry | joint/dedicated identical; externals disclosed per-cell | see S-06 |

### The four grounds, verified against source

Every quantitative claim in `5_mobiwac.tex:367` traces:

- **Transductive audit:** "region $-0.33$ to $+0.01$; category $0.00$ to $+0.29$, at Alabama,
  Arizona, and Florida" — `A4_RESULTS.md`: reg AL −0.33 / AZ +0.01 / FL −0.12; cat AL +0.29 /
  AZ +0.27 / FL +0.00. Exact. Coverage "67 to 87 percent" — A4: AL 66.8%, AZ 71.9%, FL 86.9%.
  Exact, and rounded outward (67 not 66.8) in the *unfavorable* direction.
- **Forward-edge audit:** control "about $0.41$"; FL lineage "$0.4090$ ... $0.4074$"; residual
  variant "$0.4197$ and $0.4182$"; disqualified encoder "$0.4976$ and $0.4863$". Against
  `leak_sniff_fl.csv`: gcn_ctrl 0.4089797540123382 / 0.40744232906432776; gat 0.49761650037538024 /
  0.48631035868799294; `leak_sniff_resln_fl.csv`: resln 0.4196859144977155 / 0.41815720719390814.
  **Exact to four decimals, nothing re-rounded.**
- **Three stated limits:** linear probe / Florida at one initialization over five user-grouped folds
  / ancestor builds rather than the shipped representation. All three match the audit's own
  residuals in `RESCREEN.md`.

**Does the text claim more coverage than the audit has?** No — and this is the round's strongest
methodological improvement. The paragraph replaced an absolute ("no usable information") with four
bounded channels, and it explicitly says "The measurement bounds this channel rather than closing
it". It then volunteers the counter-evidence:

> "The same record shows why the linear form is a screen and not a proof, since one encoder that
> passed it leaked under a downstream sequence model."

That is the R-GCN case (`RESCREEN.md`: passed per-step at 0.414, leaked at 0.754 under the GRU at
L2), reported against the author's interest. A hostile examiner who reads the artifact record finds
the chapter got there first. **This paragraph now survives the leakage attack.**

---

## Questions an examiner will ask, with the answer the current text supports

| Question | Answer in the text? |
|---|---|
| "Your representation saw the test users. Why is that not leakage?" | **Answered** — four grounds, `:367`, with the transductive channel measured and the residual named |
| "n = 4 is tiny. How can your p be 1e-7?" | **Answered** — `:394` gives the pairing, and `:643-645` gives the registered per-fold n = 20 Wilcoxon agreeing at 20/20 folds |
| "Why a *t* when you registered a Wilcoxon?" | **Answered** — the floor is stated numerically (0.0625), the departure is declared, both tests are reported, and the plan is released |
| "Your intervals are ±0.08. Is that credible?" | **Partly** — the precision is real (S-01 mislabels it), but the fixed-partition conditionality is not stated in this chapter (S-02) |
| "You have no test set. Are your absolute numbers optimistic?" | **Answered** — `:736` concedes it outright |
| "Did the region task teach the category task, or is this just a bigger model?" | **Answered** — freeze control, `:658-668`, with comparand and footing named; W6 backs it |
| "Would a dedicated model with the same parameters close the gap?" | **Answered in Ch.6** — capacity-matched arm, 56.16 vs 56.82 at AL and 69.88 vs 70.60 at CA, recovering none of the gain |
| "Is the two-point margin convenient?" | **Answered** — pinned pre-registration, operational justification at `:394` |
| "Was the region-superiority family pre-registered?" | **Answered, and volunteered** — `:394` says it was not, and labels those results secondary |
| "Did dropout stay active in your frozen stream?" | **Unanswered** — in the record, not in the text (S-03) |
| "Do your development seeds overlap your reporting seeds?" | **Unanswered** (S-09) |

---

## What already holds — defenses present and correctly scoped

Do not edit these away. Each is a defense that took work to earn:

1. **The Wilcoxon floor sentence** (`:394`). The numeric floor (0.0625) is stated, not gestured at.
   This is the repaired sentence and it is now a model of how to disclose a deviation.
2. **The registered-test agreement** (`:643-645`). Running the pre-registered test at its registered
   footing and reporting 20/20 fold positivity removes the entire "you switched tests to get your
   p-value" line of attack.
3. **The non-cancellation sentence** (`:736`, final clause). Refusing an overclaim a draft offered.
4. **The screen-not-a-proof sentence** (`:367`). Self-undercutting evidence, volunteered.
5. **The Alabama deficit** (`:649-650`): "a small but / statistically significant deficit, still well
   within the two-point margin." Reporting a significant negative result inside an equivalence claim
   is the single most credibility-positive sentence in the chapter.
6. **The Arizona non-upgrade** (`:648`): "the interval is centered on zero, so we report a match, /
   not a gain."
7. **The region-transition prior disclosure** (`:367`), which quantifies the counterfactual leak
   (13 to 27 points) rather than merely asserting the prior is per-fold.
8. **The trend hedge** (`:624-625`): region count and corpus size co-vary, "so we read the trend
   across the points rather than / as a precise law."

## Author decisions required

- **S-02** is the one finding I would not ship without: it is a one-clause fix and it closes the
  most likely examiner question about the tightest intervals in the document. Nothing needs to be
  re-run.
- **S-03** (dropout in the fixed stream) is a disclosure judgment, not a statistics one. No new
  experiment is implied either way.
- No finding in this report requires a new experiment.

## Out-of-scope handoffs

- Persona 07: "well powered" (S-01) is also a claim-honesty finding; we agree on it independently.
- Persona 04: the fixed-partition caveat's Ch.1-only placement (S-02) is also a concordance finding.
- Persona 06: the "at least 4 Acc@10 points" floor rests on a table minimum, not a source file.


---

<!-- estado-rodada -->
> **Rodada encerrada · último toque 2026-07-26 · sem autoridade.**
> Este ficheiro é registo de proveniência do que foi discutido nesta passagem, não fonte
> de um facto corrente. O que ficou decidido está em [`VEREDITOS.md`](../../../VEREDITOS.md);
> os valores entregues estão em `CLAUDE.md` §0.1. Não copie nada daqui sem confirmar lá.
