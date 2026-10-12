# Codex Re-review of the Revised Dissertation

**Review date:** 26 July 2026  
**Repository state reviewed:** `70d3888d` (`main`)  
**Defense artifact:** `src/build/main.pdf`, 97 A4 pages  
**Final/AcademicoPG artifact:** `src/build/main_final.pdf`, 92 A4 pages  
**Scope:** Current source, rendered artifacts, author responses in `_history/_archive/reviews_v1/dissertation_review_v1.md`,
the v2 re-review, project laws and ledgers, documentation, result artifacts, relevant
implementations, and one fresh independent pass for each of the 18 reviewer definitions.
No dissertation source, result, numerical value, citation, or claim was changed in this pass.

---

> ## AUDIT AND DISPOSITION, 2026-07-27
>
> This document was audited finding by finding against the source before any of it was acted on,
> at the author's instruction. Each finding below carries an **AUDIT VERDICT** line, and the ones
> that were acted on carry a **What was done** line naming the commit.
>
> **Two things to know before reading it.**
>
> First, this review read a 97/92-page pair. The builds on disk are **119/114 pages** (117/114 when that review was written; the round-14 standalone edits to the article bodies shortened each by one page). Every
> `file:line` in this document has drifted, and the audit re-pinned each locus by content. The
> findings mostly survive; the coordinates do not.
>
> Second, the audit is in two companion files, and they carry the evidence this summary compresses:
> [`_history/_archive/CODEX_AUDIT.md`](_history/_archive/CODEX_AUDIT.md) has the per-finding verdicts with file:line
> proof (archived 2026-07-29; anything of it still needing the author is `_history/_archive/PENDENCIAS_RESOLVIDOS.md`), and
> [`CODEX_VS_PERSONAS.md`](_history/CODEX_VS_PERSONAS.md) maps this review against the nine-persona suite,
> the fact gate and the committee simulation, naming what is duplicate, what is contested, and what
> only this review found.
>
> **Tally:** 5 RESOLVED, 1 REFUTED as stated, 1 CONFIRMED and fixed, the rest PARTLY, with the
> live residue named in each case. Four claims do not hold on the evidence, including a citation
> demand that runs against a recorded author ruling, and a chapter attribution that reads a MobiWac
> appendix sentence as a Chapter 4 claim.
>
> **The four highest-value findings were ones no other reviewer caught**, and all four are fixed:
> the capacity-control miscount (three arms of twenty, sixty fits, and 56.16 is a mean not a
> maximum), the wrong Mikolov paper for negative sampling, a Chapter 5 sentence that reasserted an
> attribution the same chapter refuses, and a Chapter 3 sentence describing a node feature the
> released code does not build. A nine-persona suite, the fact gate and the committee simulator all
> read past every one of them.
>
> **What still needs the author** is listed in [`PENDENCIAS.md`](PENDENCIAS.md), not here.

---

## Executive Summary

The revision is a substantial improvement over the first reviewed version. The central Chapter 5
result is numerically coherent: the joint-versus-dedicated result board, task-specific metrics,
four-seed inferential unit, Arizona non-inferiority language, and most of the reported deltas trace
to repository artifacts. Both PDF variants are A4, use the intended margins and page-number
placement, contain no unresolved references or citations, and have no measured overfull boxes.
The negative-to-positive research arc, the time-capsule chapter prefaces, and the unusually candid
reporting of inconvenient results remain important strengths.

The dissertation is nevertheless **not ready for advisor handoff, defense circulation, or
submission in its current form**. The reason is not that the headline Chapter 5 score board has
been disproved. The current gate fails for four different reasons:

1. Three sentences in the delivered PDF are grammatically broken because live prose was
   accidentally placed after `%` inside audit comments.
2. The dissertation-level scientific interpretation remains stronger than the controls permit.
   In particular, the Chapter 4 static task deterministically exposes the target through `fclass`,
   and Chapter 5 demonstrates operational success of one joint artifact but not region-to-category
   transfer or a shared-trunk mechanism.
3. The exact Check2HGI lineage used for the headline results has not received the nonlinear,
   future-edge test needed to close the known bidirectional category-information channel.
4. Submission prerequisites remain open: privacy/ethics text, cover and approval sheet, committee
   and date, author sign-offs, bibliography font size, exact institutional font acceptance, and
   several secretariat/advisor decisions.

The current committee simulation is **“aprovado com correções substanciais”**, with a realistic
path to “correções menores” if the scientific framing, exact-lineage leakage decision, ethics
statement, and production blockers are resolved before circulation.

## Overall Assessment

| Dimension | Current assessment | Submission consequence |
|---|---|---|
| Core Chapter 5 result board | Substantially verified | Preserve; repair interpretation and protocol wording |
| Dissertation-wide causal claim | Overstated and internally inconsistent | Major revision |
| Chapter 4 static-category evidence | Confirmed target-derived shortcut | Cannot carry the thesis-level diagnosis |
| Chapter 5 leakage evidence | Honest but does not test the shipped lineage | Author/advisor decision or new audit |
| Statistics | Mostly reproducible; inference is conditional on one fixed partition and development-as-reporting folds | Reframe; do not imply population-wide certainty |
| Citations | All keys resolve; several load-bearing claim/source mismatches remain | Targeted citation repair |
| Coletânea integration | Strong structure; provenance/errata ledgers lag the current text | Synchronize records |
| Prose | Strong macro-argument; three broken sentences and local high-burden passages | Mandatory line/readability pass |
| Visual production | Generally polished and unclipped | Targeted visual/typographic pass |
| UFV readiness | Non-compliant in both current artifacts | Administrative/format gate fails |

### What the recent revision accomplished

- It corrected the inferential unit from twenty fits to four per-seed means in the main Chapter 5
  reporting.
- It preserved the distinction between category superiority, region superiority, and
  non-inferiority; Arizona is correctly reported as a match.
- It added useful disclosures about fixed-fold uncertainty, no independent test split,
  representation transductivity, width asymmetry, task-pair change, and the limited reach of the
  freeze control.
- It added a label-history analysis and a capacity-matched follow-up, both of which are valuable
  once their claims and counts are stated precisely.
- It fixed the previous margin overflows and floats-only page and retained a clean reference/citation
  build.
- It materially improved bibliography identities and the historical correction trail.

### What the revision did not close

- It measured the Chapter 4 static shortcut but did not disclose the result in the dissertation or
  remove that task from the thesis-level diagnosis.
- It narrowed the shared-trunk claim in one place but left the contrary attribution in the Chapter
  5 discussion.
- It disclosed that the Check2HGI probe is limited but still allows global wording that reads as
  though the shipped representation were leakage-cleared.
- It called a maximum over four selected label-only models a “ceiling,” which is not an upper bound.
- It retained unsupported or false claims about PCGrad, Nash-MTL, preregistration timing,
  post-hoc power, and identical checkpoint selection.
- The correction batch introduced three new comment-swallow regressions that the new checker misses.

## Major Issues

### COD-001 — Three rendered sentences are broken by comment-swallowed prose

> **AUDIT VERDICT (2026-07-27): RESOLVED.** All three render: "Nash-MTL treats" p23, "a capacity-matched dedicated baseline" p77, "The emphasis convention" p89; four more of the class were found and fixed; the checker now passes 10 fixtures before its own result is trusted
>
> **What was done:** Fixed 2026-07-27 (f62e33f8). All three sentences verified rendering. Four MORE of the same class were then found and fixed. The detector was rebuilt around a render test, carries 10 regression fixtures, and check.sh runs the fixtures before trusting it.

- **Severity:** Critical
- **Status:** Open
- **Files:** `src/chapters/2_fundamentals.tex:356-368`;
  `src/chapters/6_conclusion.tex:99-106`;
  `src/chapters/apx_b_errata.tex:184-191`
- **Sections:** Gradient-balancing overview; consolidated answer; Appendix B
- **Reported by:** Reviewers 01, 02, 03, 04, 12, 14, and 15
- **Classification:** Confirmed error

**Finding**

Three pieces of live prose occur after `%` and therefore do not render:

- “Nash-MTL treats” is missing on PDF pp. 22–23.
- “a capacity-matched dedicated baseline, run after the” is missing on PDF p. 77.
- “The emphasis convention of the published category table, which” is missing on PDF pp. 88–89.

The affected passages are not cosmetic. The conclusion defect breaks one of the two controls used
to support the consolidated answer, while the Appendix B defect undermines the document intended
to prove correction discipline.

**Why it matters**

These are immediate handoff blockers and show that the new trapped-prose check is not a valid
release gate. A reader encounters malformed scientific statements in the delivered PDF.

**Recommended action**

Restore the three complete sentences outside comment blocks, add each case as a regression fixture
for `check_trapped_prose.py`, rebuild both variants, and visually inspect the repaired pages.

**Author response**

> _Write response here._

**Resolution notes**

> _Record the commit, rebuilt page checks, and checker regression test here._

### COD-002 — Chapter 4 static category result is target-derived but still drives the thesis arc

> **AUDIT VERDICT (2026-07-27): PARTLY.** `spot`→`category` purity is 1.0 at all five states (measured); no rendered page states it; but Ch.4 is only one of two supports for the diagnosis and the width confound is now disclosed in Ch.6

- **Severity:** Critical
- **Status:** Needs author input
- **Files:** `src/chapters/4_courb.tex:121-125,169-175,203-218,313,412-414`;
  `src/chapters/1_introduction.tex:110-116`;
  `src/chapters/6_conclusion.tex:43-55`
- **Sections:** CoUrb representation, results, dissertation diagnosis
- **Reported by:** Reviewers 09, 11, and 12
- **Classification:** Confirmed method/claim mismatch

**Finding**

The Chapter 4 static task pairs the HGI-derived representation with the POI category target.
The implementation maps each POI to an embedding indexed by its `fclass`. Across the five committed
state corpora, each observed `fclass` maps to exactly one of the seven target categories. The
repository's own Alabama shuffle control collapses static macro-F1 from 0.7855 to 0.1437, while the
sequential task moves far less, from 0.2383 to 0.1988.

The current PDF does not render that result. Instead, the 20.2–22.0-point static gain is still used
in Chapters 1 and 6 to argue that representation rather than sharing architecture was the
bottleneck.

**Why it matters**

The static result does not estimate target-blind inductive category prediction and cannot carry the
dissertation's central “controlled diagnosis.” The sequential CoUrb evidence remains usable and
should be preserved, but it is heterogeneous rather than universal.

**Recommended action**

Obtain the co-author/advisor decision recorded in `PENDENCIAS.md`. In the dissertation-authored
frame, disclose the deterministic mapping and shuffle control, withdraw the static result as
evidence of predictive representation quality, retain the sequential conclusion, and rebuild the
Introduction and Conclusion around evidence that survives. If a target-masked rerun is performed,
report it as new evidence rather than silently replacing the published record.

**Author response**

> _State whether the result will be rerun, withdrawn from the thesis-level diagnosis, or retained
> under an advisor-approved alternative estimand._

**Resolution notes**

> _Record the co-author/advisor decision and the exact reader-facing disclosure here._

### COD-003 — The exact reported Check2HGI lineage has not closed the future-edge channel

> **AUDIT VERDICT (2026-07-27): PARTLY.** Ch.5 :391 states the linear form, the Florida-only single-seed scope, the ancestor-build lineage, and the failed screen; the one global word left is "leakage-guarded" at `1_introduction.tex:158`

- **Severity:** Major
- **Status:** Needs author input
- **Files:** `src/chapters/5_mobiwac.tex:259-263,370-396,839-845`;
  `research/embeddings/check2hgi/preprocess.py:172-209,616-639`
- **Section:** Chapter 5 representation integrity and limitations
- **Reported by:** Reviewers 01, 07, 09, 11, and 12
- **Classification:** Confirmed information channel; exploitation by the shipped artifact is unverified

**Finding**

Check-ins contain category features, consecutive check-ins are connected in both directions, and
the encoder uses multiple message-passing layers. This creates a path by which the next check-in's
category can reach a context representation. The dissertation commendably says that its linear
probe was Florida-only, one seed, and run on ancestor encoders, and admits that another encoder
passed the linear probe but leaked under a downstream sequence model. It does not test the exact
artifact lineage that produced the reported board, and the audit population also differs from the
stride-1 result-window population.

**Why it matters**

The existence of a channel does not prove that the reported artifact exploited it, so the result
must not be labelled invalid without a test. Conversely, an ancestor-build linear probe cannot
clear the shipped lineage. The current evidential state is **unverified**, not “clean” and not
“proven leaked.”

**Recommended action**

Choose explicitly between:

1. running a nonlinear, sequence-level forward-edge test and preferably a causal/future-masked
   ablation on the exact reported artifact lineage; or
2. retaining the result as conditional evidence while removing any global “leakage-guarded” or
   closure wording and stating the unresolved channel adjacent to the headline.

The earlier author response says the causal rerun may be run on `nespedgpu`; that work was not
undertaken here because this pass is review-only.

**Author response**

> _Choose the evidence path and identify the exact artifact/checkpoint to be audited._

**Resolution notes**

> _Record the run manifest and result, or the approved conditional wording._

### COD-004 — Operational joint-model success is conflated with MTL transfer and a trunk mechanism

> **AUDIT VERDICT (2026-07-27): PARTLY.** The withholding is stated twice (Ch.5 :713, Ch.6 :101) and the ablation is disclosed as unusable; the contrary attribution survives verbatim at `5_mobiwac.tex:872` (p74)
>
> **What was done:** Applied (06b64cab). Attribution downgraded in Ch.5 and Ch.6; the supporting ablation was audited and found measured on a different configuration, and that is disclosed. A residual reassertion at 5_mobiwac.tex:872 was then found by the cross-check and fixed (877b2109).

- **Severity:** Major
- **Status:** Open
- **Files:** `src/chapters/5_mobiwac.tex:695-716,829-840`;
  `src/chapters/6_conclusion.tex:82-100,148-161`;
  `src/chapters/3_cbic.tex:23-27`
- **Sections:** Chapter 5 mechanism; consolidated answer
- **Reported by:** Reviewers 01, 04, 07, 10, 11, and 12
- **Classification:** Confirmed internal contradiction/overclaim

**Finding**

The freeze control shows that region-task training does not cause the category gain, and the
Florida cross-attention removal changes category macro-F1 by only \(-0.04\pm0.13\). Chapter 5
therefore correctly says it cannot name the shared trunk as the source. The discussion later says
that “the shared trunk carries the semantic context that lifts” category. Chapter 6 answers that
MTL helps while also saying the gain is not cross-task transfer.

The clean conclusion is operational: one artifact with one forward pass produces both outputs and
beats or matches the selected dedicated comparators. The current controls do not show that
region-task learning causes the category improvement, that the trunk is the responsible component,
or that the two tasks teach each other.

**Why it matters**

This is the main claim the committee will test. The score board can be correct while its causal
interpretation is wrong.

**Recommended action**

Separate four propositions throughout the frame:

- category comparator result;
- region comparator result;
- one-artifact/deployment result;
- cross-task transfer/mechanism result.

Retain the first three at their measured scope and state that the fourth was not demonstrated.
Replace architecture-excluding language such as “representation, not architecture” with “the
largest observed lever in this experimental sequence” or an equally conditional statement.

**Author response**

> _Write response here._

**Resolution notes**

> _Record the synchronized Chapter 1, Chapter 5, Chapter 6, Appendix B, and registry edits._

### COD-005 — PCGrad and Nash-MTL evidence is still misstated

> **AUDIT VERDICT (2026-07-27): PARTLY.** Wiring defect and unsupported cost claim CONFIRMED at source; the author has ruled on PCGrad and Nash separately; the screen's seed/state scope is still absent from prose

- **Severity:** Major
- **Status:** Open
- **Files:** `src/chapters/5_mobiwac.tex:182-210`;
  `src/chapters/3_cbic.tex:205-237,271,423`;
  `src/chapters/4_courb.tex:84,115`;
  `src/chapters/apx_b_errata.tex:160-169`
- **Sections:** MTL optimization and historical correction trail
- **Reported by:** Reviewers 05, 07, and 10
- **Classification:** Confirmed error and unsupported attribution

**Finding**

Chapter 5 says none of the named balancers, PCGrad and Nash-MTL, improved on fixed weighting. The
repository audit says PCGrad was never validly tested individually in the dual tower because its
update did not reach most of the private region pathway. “At default configurations” does not fix a
wiring defect, and the screen scope—seed 0 at Alabama and Florida—is absent.

The historical Nash-MTL implementation collapsed to equal weights, yet Chapters 3 and 4 still
attribute optimizer preference and a guarantee that every loss improves. The claim that Nash-MTL
requires only two matrix-vector products is known to be unsupported while remaining live in the
chapter.

**Why it matters**

These statements turn invalid or conditional implementation evidence into optimizer conclusions.
They also obscure which parts of the historical result survive the implementation finding.

**Recommended action**

Remove PCGrad from the empirical confirmation; state the valid screen's datasets, seed, and
configuration scope; describe the Nash equal-weight collapse plainly in the historical prefaces;
make Nash guarantees conditional on their assumptions; and correct the computational-cost
statement in the main chapter while retaining an Appendix B record.

**Author response**

> _Write response here._

**Resolution notes**

> _Record the final optimizer inventory and the historical-result interpretation._

### COD-006 — Statistical wording exceeds the design

> **AUDIT VERDICT (2026-07-27): PARTLY.** "before any result was read" and "well powered" are CONFIRMED overstatements; "identically" is REFUTED as reported (the sentence names the asymmetry itself); n=4 and the fixed partition are already stated

- **Severity:** Major
- **Status:** Open
- **Files:** `src/chapters/2_fundamentals.tex:493-516`;
  `src/chapters/5_mobiwac.tex:416-423,525-533,657-674,839-845`
- **Sections:** Validation, tests, and reporting
- **Reported by:** Reviewers 04, 06, 07, 09, 10, 11, and 12
- **Classification:** Confirmed interpretation problem

**Finding**

The current design provides four seed-level observations conditional on one fixed five-fold user
partition. The fold-level Wilcoxon pool reuses the same folds across seeds and should not be read as
twenty independent population draws.

> **PREMISE PARTLY REFUTED, 2026-08-04. Recorded here rather than rewritten: revising a reviewer's
> verdict is the reviewer's call, not mine.** The two sentences above assume the four seeds share one
> partition. They do not: `src/data/folds.py` passes the run's seed into
> `StratifiedGroupKFold(random_state=...)`, so each seed draws its own user partition. Full evidence,
> code path and a measured control: `../science/fold_partition_and_seeds.md`.
>
> **What this does to the finding.** Nothing, for the two clauses it flagged as overstatements: neither
> depends on the partition premise, and each keeps the disposition the author already gave it. Stated
> exactly, because I got this wrong once and a live ledger is the wrong place for it:
> **"well powered" was REMOVED** — probe `COD-006a` in `check_audit_claims.py:65-66` is ABSENT-type on
> that phrase, and the sentence now reads "The precision of the equivalence test is measured across
> these four partitions". **"before any result was read" was KEPT, deliberately, and it is ACCURATE.**
> The author's decision was explicitly narrow, quoted in that file at `:67-72`: *"Let's change only the
> second point about the: 'The equivalence is well powered'."* Probe `COD-006b` at `:73-74` is
> PRESENT-type on the phrase and its header states the reason in terms that apply directly to what I
> nearly did: it "is kept, inverted, so that a later agent 'tidying up' the other half of the audit
> finding is caught by the gate instead of silently overriding an author decision." My first version of
> this annotation asserted that clause was "still false on the repository record" and that both clauses
> "were fixed" — both statements were wrong, and the gate would have caught the edit while the prose
> asserting it would not have been. What
> changes is the *reason* offered here for distrusting the pool. The pool should still not be read as
> twenty independent draws, but the correct reason is that the five folds within a seed are not
> independent of each other (they partition one dataset), not that the partition is shared across
> seeds. The reported tests pair the four per-seed means, so they never claimed the twenty.
>
> **The recommended remedy in the table at the end of this file ("Condition intervals on the fixed
> partition") is no longer the right instruction** and is annotated there. The plan was frozen before the final board, but repository
records show that pilot results informed the two-point margin and protocol choices. “Before any
result was read” is therefore false. “The equivalence is well powered” relies on observed variance
and is post-hoc precision, not prospective power.

The dissertation also says selection is applied identically to both arms, while dedicated models
use task-best epochs and the joint model uses a geometric-mean joint selector. Absolute scores are
optimistic and the paired deltas are only partly protected.

**Why it matters**

The numerical results remain informative, but the current language can make conditional
initialization variability sound like broad sampling uncertainty and exploratory design sound
confirmatory.

**Recommended action**

- Say the protocol was frozen before the final board after pilot-informed development.
- Lead with effect estimates, confidence intervals, and the \(n=4\) seed-level analysis.
- Treat the fold-level Wilcoxon as supporting/sensitivity evidence, not an independent \(n=20\)
  footing.
- Replace “well powered” with the observed interval precision, conditional on the fixed split.
- Remove “identically” from the checkpoint discussion and state each selector exactly.
- Ensure only the paired seed-level test licenses “outperforms,” consistent with the glossary.

**Author response**

> _Write response here._

**Resolution notes**

> _Record whether inference is reframed or an independent split/rerun is introduced._

### COD-007 — Historical Chapters 3–4 remain descriptively useful but methodologically under-specified

> **AUDIT VERDICT (2026-07-27): PARTLY / NEEDS-AUTHOR.** The missing Ch.3 records and unspecified Ch.4 checkpoint rule are CONFIRMED; the "significant/outperforms survives" half is largely REFUTED (Appendix B documents four removals and accounts for all six surviving uses)

- **Severity:** Major
- **Status:** Needs author input
- **Files:** `src/chapters/2_fundamentals.tex:499-506`;
  `src/chapters/3_cbic.tex:50-62,131-295,414-423`;
  `src/chapters/4_courb.tex:245-252,313,412-414`
- **Sections:** CBIC and CoUrb protocols/results
- **Reported by:** Reviewers 01, 06, 09, 10, 11, and 12
- **Classification:** Confirmed missing record plus unsupported inferential language

**Finding**

Chapter 3 does not recover the split axis, seed count, fold-built embedding boundary, tuning budget,
or checkpoint rule. Chapter 4 discloses a sample-level—not user-level—split and a single-seed
footing, but its checkpoint selection is still not specified. Neither chapter runs the significance
tests later defined in Chapter 2, yet “significant,” “statistical,” “outperforms,” and “consistently”
language survives in places. CoUrb's 20.2–22.0-point value additionally selects the better spatial
encoder separately per cell and is an oracle upper envelope unless labelled as such.

**Why it matters**

These chapters can support a historical, configuration-specific research narrative, but not the
same inferential or generalization claims as Chapter 5.

**Recommended action**

Recover the original records if possible. Otherwise explicitly mark Chapter 3 as historical
descriptive evidence, replace untested inferential verbs with mean-comparison language, identify
CoUrb's sample-level estimand, and label the per-cell best-encoder summary as an oracle envelope.

**Author response**

> _State which original CBIC/CoUrb records can be recovered and whether article prose may be
> corrected under the adopted errata policy._

**Resolution notes**

> _Record recovered manifests or the final historical-scope wording._

### COD-008 — Several load-bearing citations do not support the claims attached to them

> **AUDIT VERDICT (2026-07-27): PARTLY.** Mikolov negative-sampling mismatch CONFIRMED (1301.3781 has no negative sampling); Standley overreach CONFIRMED; UberNet/Sphere2Vec preprints CONFIRMED (versions of record exist); the scikit-learn claim is REFUTED as a support failure
>
> **What was done:** Mikolov half fixed (47ca2bd5): mikolov2013negsampling added and both cited, with an errata row recording that the earlier erratum installed the defect.

- **Severity:** Major
- **Status:** Open
- **Files:** `src/chapters/2_fundamentals.tex:493-498`;
  `src/chapters/4_courb.tex:203`;
  `src/chapters/3_cbic.tex:205-210`;
  `src/references.bib:395-401,647-656,967-973`
- **Sections:** Validation method, embedding method, MTL background, bibliography
- **Reported by:** Reviewer 05
- **Classification:** Confirmed citation-support/metadata errors

**Finding**

- The 2011 scikit-learn paper cannot support `StratifiedGroupKFold`, which was added in
  scikit-learn 1.0 in 2021.
- The earlier Word2Vec paper cited at the CoUrb site describes skip-gram with hierarchical softmax,
  not negative sampling.
- Standley et al. do not establish the broad claim that hard sharing generally matches or exceeds
  more complex architectures while training and inferring faster.
- UberNet and Sphere2Vec still cite preprint records despite available versions of record; the
  Standley entry lacks its PMLR volume/pages.

**Why it matters**

The first three are claim-support failures, not style preferences. The grouped split is
load-bearing to Chapter 5's leakage defense.

**Recommended action**

Permit a versioned official scikit-learn citation, cite the later Mikolov negative-sampling work or
remove that phrase, narrow the Standley sentence, and update the three bibliographic records to
their versions of record. Preserve the successful R4 repairs to the other sampled entries.

**Author response**

> _Confirm whether versioned software documentation is acceptable under the bibliography policy._

**Resolution notes**

> _Record the corrected keys/claims and a fresh citation-support audit._

### COD-009 — CoUrb translation and adaptation records lag the actual dissertation

> **AUDIT VERDICT (2026-07-27): PARTLY.** The single-seed sentence is already scoped to the released code (verified firsthand in `create_fold.py`); the stale inventory, English-donor source-of-record, and the "no claim altered" tension are CONFIRMED

- **Severity:** Major
- **Status:** Open
- **Files:** `src/chapters/4_courb.tex:245-252,313,356,412-414`;
  `src_utils/adaptation_ledgers/4_courb_ADAPTATION_LEDGER.md`;
  `src/chapters/apx_b_errata.tex`
- **Section:** Chapter 4 reproduction and provenance
- **Reported by:** Reviewers 04, 08, 11, and 12
- **Classification:** Confirmed provenance/ledger drift

**Finding**

The Portuguese paper reports mean and standard deviation over five folds; the dissertation says the
released code pins a single seed and that the reported standard deviations are fold spreads at
that seed. The code supports the execution convention, but the ledger admits it cannot prove that
the published run used that exact file. A new count-based baseline retaining six values is not
fully recorded. The adaptation inventory/count is stale, and the ledger incorrectly treats the
English donor as the source of record rather than the published Portuguese article.

The chapter also says no result, claim, or conclusion was altered while Appendix B lists claim-scope
corrections.

**Why it matters**

For a translated published chapter, provenance discipline is part of scientific trust. A plausible
code inference must not be presented as a fact about the published execution without evidence.

**Recommended action**

Scope the single-seed statement to the released implementation unless the published execution is
proved; update the ledger and Appendix B for every current departure; name the Portuguese
publication as the source of record; reconcile the universal “no claim altered” statement.

**Author response**

> _Write response here._

**Resolution notes**

> _Record the completed source-to-dissertation inventory._

### COD-010 — Capacity-matched control is useful but miscounted and over-compressed

> **AUDIT VERDICT (2026-07-27): CONFIRMED.** "across three training configurations and all twenty fitted models" still renders on p77; the artifact is 20 per arm, 60 total, and 56.16 is the best arm's mean (SD 1.89)
>
> **What was done:** Fixed (47ca2bd5). Verified in capacity_matched_summary.json: three arms at n=20 each, sixty fits, and 56.16 is the best arm's mean with sd 1.89. Both now stated.

- **Severity:** Moderate
- **Status:** Open
- **File:** `src/chapters/6_conclusion.tex:105-148`
- **Section:** Consolidated answer, capacity-matched control
- **Reported by:** Reviewers 02, 06, 07, 10, and 15
- **Classification:** Confirmed numerical/prose error

**Finding**

The conclusion says “across three training configurations and all twenty fitted models.” The
artifacts contain twenty fits per arm, or sixty across the three arms. The stated 56.16 is the best
arm's mean (with SD 1.89), not the maximum of twenty individual fitted models. The same paragraph is
currently broken by COD-001.

**Why it matters**

The control strengthens the dissertation, but the current wording misstates both the sample count
and the statistic.

**Recommended action**

Restore the sentence, say “twenty fits per configuration (sixty total),” identify 56.16 as the
best configuration's mean with dispersion, and retain the narrower search/one-width limitations.

**Author response**

> _Write response here._

**Resolution notes**

> _Record the corrected count/statistic and artifact path._

### COD-011 — Privacy, ethics, licensing, and data governance are absent from the PDF

> **AUDIT VERDICT (2026-07-27): RESOLVED.** Appendix E "Data Ethics and Governance" is in the build (pp. 101–102), with licences re-verified at source and the CEP/IRB position recorded as a position, not an approval
>
> **What was done:** Resolved (9e2b5157). Appendix E, Data Ethics and Governance, is in the build. Every licence re-verified at its source of record; two claims later corrected on the fact gate's findings (6f97bf60).

- **Severity:** Major
- **Status:** Needs author input
- **Files:** Dissertation-wide; `src_utils/evidence/DATASET_LICENSING_FINDINGS.md`
- **Section:** Missing reader-facing ethics/governance statement
- **Reported by:** Reviewers 01, 07, 12, and 13
- **Classification:** Confirmed omission; institutional facts required

**Finding**

The rendered dissertation contains no substantive discussion of privacy, consent,
re-identification, anonymization, licensing, data retention/security, LGPD, or CEP/IRB
applicability, despite analyzing individual mobility trajectories. Repository licensing research
exists but is not integrated into the dissertation.

**Why it matters**

This is a predictable committee question and a responsible-research requirement independent of
whether the source datasets are public.

**Recommended action**

Add a concise data-ethics and governance subsection stating dataset provenance and licence,
identifier handling, residual re-identification risk, access/retention safeguards, limits on
individual deployment, and the actual CEP/IRB determination. Do not invent the latter.

**Author response**

> _Provide the CEP/IRB determination, Massive-STEPS terms, Chapters 3–4 Gowalla terms, and the
> safeguards actually used._

**Resolution notes**

> _Record the approved statement and supporting institutional/source evidence._

### COD-012 — Both artifacts fail the current UFV submission gate

> **AUDIT VERDICT (2026-07-27): PARTLY.** Bibliography now measures 11.96 pt, body size (measured p81), so that half is RESOLVED; cover, approval sheet, committee, date, font ruling and process documents remain NEEDS-AUTHOR
>
> **What was done:** Bibliography half resolved (9e2b5157): the footnotesize wrapper is gone and the bibliography sets at body size. Campus set, and flagged as inert until a cover exists. Cover, approval sheet, committee and date remain yours.

- **Severity:** Critical
- **Status:** Needs author input
- **Files:** `src/0_main.tex:35-41,122-168,388-389`; both PDFs; institutional records
- **Section:** Front matter, typography, and process prerequisites
- **Reported by:** Reviewer 13
- **Classification:** Confirmed production failures plus external decisions

**Finding**

The defense PDF begins with the title page rather than a cover and contains literal approval-sheet
placeholder text. Committee and date remain placeholders. The bibliography is explicitly set in
`\footnotesize` and measures about 10 pt despite the documented 12 pt requirement. The body uses
TeX Gyre Termes, a Times-compatible face, while the current rule as recorded names Times New Roman
or Arial; repository evidence does not establish acceptance of a substitute.

The Article 21 proof, anti-plagiarism certificate, assent/library items, defense date, and operative
quality-resolution interpretation are also pending. The final-build first-body-page offset remains
provisional until the AcademicoPG preview is inspected.

**Why it matters**

These are independent submission blockers even if every scientific issue is resolved.

**Recommended action**

Add the real cover and approval sheet; fill date/committee; remove the bibliography size override;
either use a named permitted font or obtain written acceptance of TeX Gyre Termes; complete the
listed process documents; and verify the final page offset against the portal-generated preview.

**Author response**

> _Provide the booked date, committee, secretariat rulings, font decision, and completion status of
> each mandatory document._

**Resolution notes**

> _Record the final defense and AcademicoPG compliance checks._

### COD-013 — AI disclosure is ahead of the recorded author-approval state

> **AUDIT VERDICT (2026-07-27): CONFIRMED.** Appendix C claims the author "takes responsibility for every word" while 31 `[NEEDS SIGN-OFF]` markers remain in `src/`, not 27

- **Severity:** Major
- **Status:** Needs author input
- **Files:** `src/chapters/apx_c_ai_disclosure.tex:11-12,50-57`;
  `src_utils/PENDENCIAS.md`
- **Section:** Appendix C and author sign-off
- **Reported by:** Reviewers 03, 12, and 13
- **Classification:** Confirmed repository/disclosure inconsistency

**Finding**

Appendix C says the author reviewed and accepts responsibility for every word, while 27
`[NEEDS SIGN-OFF]` markers remain in the source, including central Chapters 5–6 claims and the
disclosure itself. The appendix uses a family-level model name even though the repository records
the exact reviewer model for at least one major pass. The detailed disclosure appears only on
PDF p. 95, with no short front-matter pointer. The commit history contains many explicit AI-draft
labels but only one explicit author-edit label before most current changes, so it does not yet
support the stronger claim of chapter-level author approval.

**Why it matters**

The disclosure is a credibility shield only if it is precise and true at the time of circulation.

**Recommended action**

Complete and record the 27 sign-offs before circulation or revise the statement to the actual
current state. Name exact models/versions where independently verifiable and distinguish
generation, translation, editing, analysis, and reviewer roles. Add a short, institutionally
acceptable front-matter disclosure pointing to Appendix C, and preserve real pre-AI, post-AI, and
final checkpoints rather than creating retrospective author-approval commits.

**Author response**

> _Confirm completion of the reading/sign-off and the exact tool/model facts that can be verified._

**Resolution notes**

> _Record the signed disclosure text and approval evidence._

### COD-014 — New “ceiling” and Markov-floor explanations claim more than the analyses show

> **AUDIT VERDICT (2026-07-27): RESOLVED.** "label-history benchmark" throughout with "not an upper bound" stated; the Markov paragraph now states protocol asymmetry system by system and disclaims a single cause
>
> **What was done:** Resolved (ff96dcaf). 'label-history benchmark' throughout, stated as not an upper bound; the Markov paragraph states a protocol asymmetry with no causal claim. A wrong-quantity number in that same paragraph was then found by the fact gate and fixed (9a861200).

- **Severity:** Moderate
- **Status:** Open
- **Files:** `src/chapters/apx_d_ceiling.tex`;
  `src/chapters/5_mobiwac.tex:376-396,778-784`;
  `GLOSSARY.md`
- **Sections:** Appendix D, representation audit, external baselines
- **Reported by:** Reviewers 06, 11, and 14
- **Classification:** Confirmed conceptual overstatement

**Finding**

The maximum held-out score among four chosen label-history predictors is called a “ceiling” and
“what the past itself allows.” It is an empirical benchmark, not an upper bound; a different model
could do better using the same history. It therefore cannot establish that an encoder contains
information beyond category history.

The new Markov paragraph says all three external systems predict places and are read at region
level, although Chapter 5 describes HMT-GRN as region-native and STAN as adapted to rank regions.
The protocol differences do not identify a single causal reason why the Markov floor is higher.

**Why it matters**

Both additions are valuable honesty devices, but false labels turn them into stronger conclusions
than their evidence licenses.

**Recommended action**

Rename “label-only ceiling” to “label-history benchmark” throughout and explicitly say it is not an
upper bound. Preserve the observed Markov comparisons but remove the common causal explanation;
state the protocol asymmetry and treat external rows as contextual comparisons.

**Author response**

> _Write response here._

**Resolution notes**

> _Record glossary, appendix, Chapter 5, registry, and Appendix B synchronization._

### COD-015 — Cross-chapter task, data, and reference-point seams remain

> **AUDIT VERDICT (2026-07-27): PARTLY.** Four of six sub-claims hold: Ch.6 still says "three of the six datasets" where the measurement pools four Gowalla states, the MRR and relative-multi-task promises are still unused, the frame and Ch.4 disagree on the Gowalla vintage, and the Ch.3 preface clause understates Ch.5's changes; the next-POI bridge and the cross-reference targets are REFUTED

- **Severity:** Moderate
- **Status:** Open
- **Files:** `src/chapters/3_cbic.tex:23-25,50-84`;
  `src/chapters/4_courb.tex:250-252`;
  `src/chapters/5_mobiwac.tex:519-523,839-840`;
  `src/chapters/6_conclusion.tex:154-161`
- **Sections:** Task definitions, dataset provenance, cross-references
- **Reported by:** Reviewers 01, 04, 06, and 11
- **Classification:** Confirmed coherence defects

**Finding**

- The Chapter 3 preface says Chapters 4–5 revise the design through representation rather than
  architecture, although Chapter 5 changes topology and task pair.
- “Next-POI” is defined as exact-place prediction in a chapter that actually predicts next
  category.
- Gowalla vintage is variously described as 2009–2010 and 2009–2011 without consistently naming
  the distinct extraction bases.
- Chapter 2 promises MRR and relative multi-task performance change, neither of which appears in
  the result chapters.
- The random-region reference and checkpoint-selection cross-references do not point to sections
  that define those claims.
- Gradient scope is four Gowalla states, not “three of six datasets.”

**Why it matters**

The dissertation's strength is its explicit evolution. These seams make that evolution look less
controlled than it is.

**Recommended action**

Repair the preface and task bridge; add one extraction-specific date/provenance convention; remove
unused metric promises or report them; correct the semantic references; synchronize the four-state
gradient scope.

**Author response**

> _Write response here._

**Resolution notes**

> _Record the terminology/provenance sweep._

### COD-016 — A targeted professional language and readability pass remains mandatory

> **AUDIT VERDICT (2026-07-27): PARTLY.** The 114-word abstract result sentence and the 546-word integrity block are CONFIRMED burdens; the `3_cbic.tex:340` "unrecoverable" sentence is REFUTED (the quoted words are published prose and their meaning is recoverable)

- **Severity:** Moderate
- **Status:** Open
- **Files:** Dissertation-wide, concentrated in Chapters 3–5 and Appendix B
- **Sections:** Local prose and paragraph architecture
- **Reported by:** Reviewers 01, 02, 03, and 15
- **Classification:** Confirmed editing need; some house-style flags are subjective

**Finding**

Beyond COD-001, Chapter 3 still contains sentences whose meaning is not recoverable without author
clarification, including “unbalanced result … lead to the worse of other results”
(`3_cbic.tex:340`). The Chapter 5 integrity paragraph on PDF pp. 66–67 carries four audit channels,
many values, a failed probe, and its epistemic limit in one block. The control paragraph on
pp. 72–73 mixes its intended comparator, historical comparator, current table, exclusion, and
Florida ablation. The abstract compresses most of the design and result into one long sentence.

The current internal style audit also fails its own density/ban rules, especially in Chapters 3–4.
Some hits are exact titles, quotations, or otherwise legitimate and should not be changed
mechanically.

**Why it matters**

The macro-level story is strong, but high reader burden and inherited article prose reduce defense
reliability. A blanket homogenization would also erase useful authorial/historical differences.

**Recommended action**

Repair confirmed grammar first; split the four-channel integrity passage into a numbered paragraph
sequence; reorder the mechanism control paragraph; clarify or delete the unrecoverable Chapter 3
sentence; then perform a bounded line edit that preserves published-text provenance and voice.

**Author response**

> _Clarify the intended meaning of `3_cbic.tex:340` and confirm the permitted scope of edits to
> reproduced article prose._

**Resolution notes**

> _Record the bounded language-pass scope and author sign-off._

### COD-017 — Visual and typographic inconsistencies need a final production pass

> **AUDIT VERDICT (2026-07-27): PARTLY.** The oversized Appendix B float (21.55853 pt) and 6.97/7.27 pt diagram labels on pp. 62 and 64 are CONFIRMED by measurement; the Portuguese figure labels are RESOLVED; the "nearly blank p.4 with orphaned keywords" is CONFIRMED

- **Severity:** Moderate
- **Status:** Open
- **Files:** Both PDFs and figure/table sources
- **Sections:** Front matter, Chapter 4 figures, bibliography, dense audit pages
- **Reported by:** Reviewers 01, 13, and 18
- **Classification:** Confirmed visual issues; see reviewer 18 matrix below

**Finding**

The current artifacts are generally clean, but the defense PDF contains the literal approval
placeholder on p. 2 and a nearly blank p. 4 with orphaned Resumo keywords. Both logs report
`Float too large for page by 21.55853pt` for the Appendix B bibliography-errata table (defense
p. 94; final p. 89), which reaches the lower page boundary. Architecture/process diagrams on
defense pp. 35, 48, 62, and 64 use labels substantially below body size; Chapter 4's spatial panels
on p. 53 are too small for comfortable print reading. Appendix B tables visibly switch to a
cramped, ruled paper style. Chapter 4's inherited visuals most clearly look like a different paper.

**Why it matters**

These issues do not invalidate results, but they separate a functional PDF from a polished
dissertation and interact with the UFV font-size violation.

**Recommended action**

Replace the approval page; keep the complete keyword block together; split the Appendix B float
into a continued table or reduce row padding; convert the errata tables to a readable multi-page
booktabs style; and regenerate the small diagrams/panels at full text width with approximately
9–10 pt labels. Enlarge the Chapter 5 delta chart and add grayscale-safe hatch or direct labels.
Do not perform discretionary float reflow before the scientific prose stabilizes, because
pagination will move.

**Author response**

> _Write response here._

**Resolution notes**

> _Record the final page-by-page visual inspection._

### COD-018 — Governance files and automated gates no longer describe the artifact reliably

> **AUDIT VERDICT (2026-07-27): PARTLY.** Page counts in `CLAUDE.md`, `PLAN.md`, `_history/_archive/handoffs/HANDOFF_v1.md` are stale (89/84 against 102/97) and Appendix A lacks per-role CoUrb credit; the checker and `pypdfium2` sub-claims are RESOLVED
>
> **What was done:** Page counts synced to the measured 103/98 in CLAUDE.md, PLAN.md and _history/_archive/handoffs/HANDOFF_v1.md. The check.sh undefined-citation gate was found to pass silently under UTF-8 locales and was rebuilt (877b2109). [Superseded 2026-07-27: the build is now 104/99 after the Table 15 longtable conversion; that sync was correct when made.]

- **Severity:** Moderate
- **Status:** Open
- **Files:** `CLAUDE.md`, `PLAN.md`, `src_utils/_history/_archive/handoffs/HANDOFF_v1.md`,
  `src_utils/PENDENCIAS.md`, adaptation ledgers, `src_utils/check.sh`,
  `src_utils/check_trapped_prose.py`
- **Section:** Project governance and release checks
- **Reported by:** Reviewers 04, 08, 14, and root verification
- **Classification:** Confirmed repository drift

**Finding**

Several governance files retain obsolete page counts (89/84, 94/89, or 96/91) while the current
build is 97/92, and Appendix D is absent from some inventories. The Chapter 5 adaptation ledger says
every departure is recorded while omitting multiple recent additions. The trapped-prose checker
returns success despite the three live COD-001 failures. In the ordinary project environment,
`make check` also fails because `pypdfium2` is undeclared; the log-flattening check is locale-fragile.

**Why it matters**

The correction record is part of this dissertation's trust model. A green check that misses the
exact regression it was introduced to catch is worse than a clearly labelled heuristic.

**Recommended action**

Synchronize page/build inventories and ledgers after source fixes; add the three failures as test
fixtures; declare the PDF dependency; make log scanning locale-safe; and call the detector a
heuristic until it passes those fixtures.

**Author response**

> _Write response here._

**Resolution notes**

> _Record the governance synchronization and clean check command/environment._

## Chapter-by-Chapter Review

### Front matter and main build

The title page, abstracts, lists, contents, numbering, and body sequence render coherently, but the
defense build lacks a cover and a real approval sheet. The Portuguese keywords spill onto a nearly
empty page. The title remains recorded as provisional. These are production issues, not reasons to
disturb the working two-build mechanism.

### Chapter 1 — Introduction

**Strong:** The research question is clear, the three-study progression is memorable, and the
chapter does real synthesis rather than merely listing included papers.

**Revise:** The representation-versus-architecture diagnosis depends on the compromised Chapter 4
static result and excludes architecture more strongly than the controlled evidence permits.
Rewrite the diagnosis around the surviving sequential evidence and the operational Chapter 5
result. Make the task-pair and topology changes part of the thesis claim rather than only a later
limitation.

### Chapter 2 — Fundamentals

**Strong:** It usefully distinguishes next place, next category, and next region; presents fixed
weighting as a serious MTL baseline; and connects protocol choices to mobility-specific leakage
risks.

**Revise:** Repair the broken optimizer sentence, citation support, statistical-test licensing, and
the universal metric/reference-point promises. The grouped-stratified split requires an appropriate
versioned source. The HGI retuning paragraph should state that the static criterion is compromised
and that sequential F1 was effectively flat across the sweep. A short evaluation-validity
positioning paragraph would be more useful than broad citation expansion.

### Chapter 3 — CBIC

**Strong:** The negative result is valuable, historically honest, and essential to the
dissertation's evolution. The current preface helps prevent later findings from being projected
backward.

**Revise:** Treat the experiment as historical descriptive evidence unless the missing split,
seed, preprocessing, tuning, and checkpoint records are recovered. Direct self-label lookup is not
confirmed: the inspected DGI preprocessing replaces a node's own one-hot with neighbor-category
averages. However, the graph remains transductive and label-derived, so the estimand should be
described as spatial homophily/label propagation rather than ordinary inductive category
classification. Remove untested “significant” language, resolve the task naming, and clarify or
delete opaque inherited sentences.

### Chapter 4 — CoUrb

**Strong:** The translated chapter is largely faithful; tables and main numerical patterns are
preserved; the width asymmetry and sample-level split are now visible; and the sequential evidence
remains scientifically informative.

**Revise:** The static target shortcut must reach the reader, and that result must stop carrying the
thesis-level diagnosis. Label the per-cell best-encoder summary as an oracle envelope. Scope the
single-seed/fold-spread statement to what the released implementation proves. Complete the
adaptation inventory, source-of-record convention, new baseline row, and errata trail.

### Chapter 5 — MobiWac

**Strong:** This is the dissertation's strongest chapter. The task definitions, user-disjoint
folds, joint-best checkpoint convention, one-artifact reporting, parameter asymmetry, transition
prior correction, Markov floors, four-seed board, task-specific inference, Arizona language,
capacity follow-up, and negative mechanism findings make the work unusually auditable.

**Revise:** Separate operational success from MTL transfer; remove the trunk attribution and invalid
PCGrad claim; narrow gradient-cosine interpretation; fix preregistration/power/selector language;
state that the category audit is a POI-level in-coverage proxy; make bidirectional edges and exact
lineage status explicit; correct external-baseline replication/protocol facts; state that metrics
are window-weighted rather than user-averaged; and replace “ceiling” with “benchmark.”

### Chapter 6 — Conclusion

**Strong:** The chapter synthesizes the three studies, identifies limitations, and closes with a
clear correction-trail narrative. The task-pair confound and capacity asymmetry are unusually
candid.

**Revise:** Repair the swallowed capacity-control subject and its counts. State separately what is
established about category, region, deployment, representation, topology, task pair, and transfer.
Synchronize the four-state gradient scope and remove causal language not supported by gradient
norms or component ablations.

### Appendices

- **Appendix A:** The contribution structure is useful, but CoUrb ownership needs concrete roles in
  conceptualization, software, experiments, analysis, visualization, and writing.
- **Appendix B:** The errata mechanism is valuable but currently undermined by a broken sentence,
  stale inventories, preserved known-false wording, and universal claims that the listed
  corrections contradict.
- **Appendix C:** Keep the disclosure, but make it exact and true only after author sign-off.
- **Appendix D:** Keep the empirical analysis; rename it a label-history benchmark and remove
  upper-bound interpretations.

## Methodology and Experimental Validation

### Evidence that currently holds

- The Chapter 5 downstream folds are user-disjoint; overlapping windows do not cross those folds.
- The transition prior is built per fold in the corrected experiment, and the previous inflation is
  disclosed.
- Category and region are reported separately; no blended score hides a sacrificed task.
- One joint checkpoint is selected per fold and both heads are read from that artifact.
- The joint model's parameter advantage over dedicated models is disclosed, and the later
  capacity-matched category controls are useful at their limited scope.
- The headline board uses four seeds over five folds, and the primary inferential unit is stated as
  \(n=4\).
- Region superiority and non-inferiority are separated, with Arizona not upgraded to a gain.
- The task-pair, width, transductivity, fixed-partition, and no-third-split limitations are at least
  partly visible.

### Evidence that does not yet hold

- Chapter 4 static category performance as target-blind prediction.
- Cross-task transfer as the cause of Chapter 5's category gain.
- The shared trunk as the source of that gain.
- Absence of future-category exploitation in the exact shipped Check2HGI lineage.
- Population-level uncertainty across resampled users/splits.
- A genuinely result-blind preregistration.
- A common protocol or common causal explanation for all external region baselines.
- Complete historical reproducibility for Chapters 3–4.

### Experimental decisions still required

| Decision | Minimum defensible path | Stronger path |
|---|---|---|
| Chapter 4 static shortcut | Withdraw from thesis diagnosis and disclose shuffle result | Target-masked, fold-built rerun |
| Check2HGI future-edge channel | Mark exact lineage unverified and scope claims | Nonlinear exact-lineage audit plus causal-edge ablation |
| Selection/reporting reuse | Treat as development-protocol evidence | Nested/inner validation or untouched outer test |
| Fixed-fold uncertainty | ~~Condition intervals on the fixed partition~~ **superseded 2026-08-04: there is no fixed partition. Each seed draws its own (`science/fold_partition_and_seeds.md`), so the intervals already sample split variability at four draws; the honest limit is that four draws sample it rather than characterize it** | Repeated independent grouped splits/hierarchical analysis (still the stronger design; four draws is a sample, not a characterization) |
| CoUrb capacity/encoder attribution | Keep width confound and oracle label | Width-matched and encoder-wise ablations |
| Ethics/governance | Add factually supported statement | Institutional determination plus documented data-management record |

## Results, Statistics, and Claim Verification

### Main verified result package

The current repository supports the following bounded statement:

> Under the reported Chapter 5 development/evaluation protocol, one joint artifact outperforms the
> selected dedicated next-category comparator on all six datasets and outperforms or is
> non-inferior to the selected dedicated next-region comparator, depending on dataset. The evidence
> is conditional on four random initializations, one fixed user-grouped fold partition,
> validation-selected checkpoints read on those same folds, the reported representation lineage,
> and the stated baseline adaptations.

This statement does **not** by itself establish cross-task transfer, a shared-trunk mechanism,
inductive generalization of the representation to unseen places, or population-wide uncertainty
over alternative user samples.

### Numerical corrections required

| Item | Current issue | Required correction |
|---|---|---|
| Capacity-matched control | “Three configurations and all twenty fitted models” | Twenty per arm; sixty total |
| Capacity 56.16 | Reads like best individual fit | Best arm mean; include SD 1.89 |
| Gradient scope | “Three of six datasets” | Four Gowalla states, including Georgia |
| HGI example | 0.74→0.82 basis not fully specified in text | Confirm averaging convention and spreads or keep qualitative |
| Arizona rounding | Table/raw precision differs by 0.01 in one trace | State rounding basis consistently |
| Label-history analysis | Called a ceiling | Empirical maximum among four specified predictors |
| CoUrb 20.2–22.0 | Reads as deployable fixed encoder | Oracle per-cell best of two encoders |
| Wilcoxon \(n=20\) | Can read as independent observations | Supporting clustered fold evidence, not primary independent footing |

### Claim-verification dispositions

- **Confirmed:** Chapter 5 main table arrays, reported category deltas, four region wins, Alabama
  deficit, Arizona match, transition-prior correction, parameter asymmetry, capacity-control
  existence, and the Florida cross-attention null.
- **Confirmed error:** Chapter 4 deterministic `fclass` shortcut; PCGrad validity claim; shared-trunk
  attribution; three swallowed phrases; capacity fit count; “ceiling” terminology; several
  citation-support claims.
- **Unverified:** exact shipped-lineage future-edge exploitation; original CBIC split/selection
  record; published CoUrb execution seed; seed 0's complete development/reporting separation;
  >99% HMT-GRN denominator coverage; institutional acceptance of TeX Gyre Termes.
- **Subjective recommendation:** adding broader MTL/evaluation canon, compressing the abstract,
  and visual restyling beyond compliance.

## Structure, Coherence, and Readability

The dissertation is structurally coherent. It is not “three stapled papers”: the null result,
representation diagnosis, revised system, and general conclusion form a real intellectual
sequence. The time-capsule prefaces and conclusion are the main devices that make this work and
should be preserved.

The sequence currently overstates how controlled its middle transition is. Chapter 4 changes input
width and contains the static shortcut; Chapter 5 changes representation, topology, and task pair.
The correct thesis-level contribution is a documented experimental evolution with bounded
evidence, not a one-variable causal proof.

The prose is strongest in Chapters 1, 2, 5, and 6. Chapter 3 retains opaque inherited English;
Chapter 4 retains translated repetition and donor-paper visual/prose habits. The answer is a
bounded professional pass, not uniform rewriting. Highest-yield repairs are:

1. repair all non-parsing sentences;
2. split the four-channel integrity block on PDF pp. 66–67;
3. reorder the freeze-control/mechanism paragraph;
4. simplify the abstract result sentence;
5. fix the next-place/next-category bridge;
6. remove repeated Chapter 4 method explanations;
7. obtain author clarification for sentences whose meaning cannot be inferred.

## Terminology, Notation, and Consistency

| Term/notation | Current issue | Decision |
|---|---|---|
| Next-POI / next place / next category | Chapter 3 locally changes the task referent | Preserve title; make body distinction explicit |
| Static category classification | Reads as ordinary predictive task | Name transductive/label-derived estimand and shortcut |
| MTL “helps” | Mixes operational and causal meanings | Define operational one-artifact result separately from transfer |
| Shared trunk | Named as source in one passage, rejected in another | Do not name a component |
| Equivalence / non-inferiority | TOST is used for a non-inferiority margin in places | Use one canonical term per claim |
| Seed / repetition / fold | Mostly improved | Keep \(n=4\) and fixed-partition scope adjacent |
| Label-only ceiling | Not a theoretical ceiling | Use label-history benchmark |
| Gowalla dates | Extraction-specific vintages differ | Name extraction and date basis together |
| “Significant” / “outperforms” | Used in Chapters 3–4 without tests | Descriptive language only |
| “Used throughout” | Protocol applies only to Chapter 5 | Scope every protocol statement by chapter |

## Figures, Tables, Equations, and References

### Tables and equations

The earlier measurable margin violations are resolved, the large Chapter 5 result table is
legible, and no current log reports an overfull box. Both logs do, however, report an oversized
Appendix B float by 21.55853 pt. Table captions are generally placed correctly and the
joint/dedicated reporting conventions are clearer than before.

Remaining content issues include the CoUrb per-cell emphasis/oracle convention, the inherited HMRM
bolding explanation, and incomplete equation-level readability in the densest Chapter 3 method
passages. These should be corrected without reintroducing scaled-down tables.

### Figures

Chapter 5's result figures are among the strongest visuals and should set the style bar. Chapter 4
contains the most visible cross-paper drift: small labels, Portuguese text, and a different diagram
vocabulary. Any redraw must preserve “adapted from” attribution and the published-content
relationship.

| Part | Figure style | Table style | Caption style |
|---|---|---|---|
| Front matter | N/A | Lists consistent; Resumo keywords break | N/A |
| Chapters 1–2 | Consistent | Consistent, slightly small | Consistent |
| Chapter 3 | Tiny architecture diagram | Booktabs consistent | Consistent |
| Chapter 4 | Tiny diagram and spatial panels | Consistent but compressed | Consistent |
| Chapter 5 | Strong results; some tiny diagrams/charts | Consistent but dense | Consistent |
| Chapter 6 | Consistent | N/A | N/A |
| Appendices | N/A | Strong drift; cramped errata tables and oversized float | Consistent |

The strongest current page groups are the Introduction opening (defense pp. 13–17), chapter
openings on pp. 27, 43, and 58, the p. 70 result composition, and the Conclusion on pp. 76–79.

### References

All live citation keys resolve and the current PDFs contain no `(??)` markers. Most of the prior R4
bibliography cleanup survives. Resolve COD-008, then rerun a claim-site audit rather than only a
key-resolution check. Remove or justify the uncited `liu2014geographical` entry.

## Formatting and Submission Readiness

### Verified compliant/working elements

- A4 page size.
- Approximately 3 cm left/top and 2 cm right/bottom margins.
- One-and-a-half body spacing.
- Top-right Arabic numbering in the body.
- Correct stripping of defense-only front matter from the final upload variant.
- Article sequence and status wording.
- No duplicated funding acknowledgement in the final upload PDF.
- No unresolved citations/references or visible margin overflow.

### Blocking or externally unverified elements

- Missing defense cover.
- Placeholder approval sheet, committee, and date.
- Oversized Appendix B float warning in both builds.
- Bibliography at approximately 10 pt rather than 12 pt.
- TeX Gyre Termes not explicitly authorized by the recorded “Times New Roman or Arial” rule.
- English frame, translated CoUrb inclusion, standalone Fundamentals chapter, title, and errata
  policy still need the recorded advisor/Comissão bundle.
- Article 21 proof, operative quality threshold, anti-plagiarism certificate, and signature/library
  process remain pending.
- Final-build first-body-page value 11 must be checked against the AcademicoPG preview.
- Portal fields and post-defense deposit cannot yet be verified.

**Readiness conclusion:** The document is not ready for defense circulation or portal upload.
Scientific framing and malformed prose should be repaired before final pagination and
institutional production work.

## Reviewer Agreements and Disagreements

### Strong agreements

The independent reviewers converged on the following:

1. The Chapter 5 score board is the dissertation's strongest evidence and is not overturned by the
   present review.
2. Chapter 4's static task exposes the category through `fclass`; the result cannot support the
   current dissertation-level representation diagnosis.
3. The freeze and cross-attention controls do not identify region-to-category transfer or a shared
   trunk as the source of the category gain.
4. The exact Check2HGI lineage remains unverified against the future-edge channel.
5. The current statistical language is more confirmatory and general than the fixed-partition,
   development-as-reporting design permits.
6. The three comment-swallowed phrases are release blockers.
7. Privacy/ethics text and institutional front matter are mandatory before submission.
8. The correction trail, negative-result reporting, time-capsule prefaces, and one-artifact
   reporting are unusually strong and should be preserved.

### Reconciled disagreements

#### Is Chapter 3 direct target leakage?

Reviewers 09 and 12 treated Chapter 3 as target leakage because category-derived graph features
support category prediction. The code inspection shows a material distinction from Chapter 4:
Chapter 3 replaces a node's own one-hot with averages of its neighbors' categories before the GAT.
Therefore, direct self-label lookup is **not confirmed**. The task is still transductive,
label-derived spatial homophily/label propagation, and its split/embedding-fit boundaries are
unverified. The consolidated disposition is **major scope/method uncertainty**, not the confirmed
deterministic lookup established in Chapter 4.

#### Does the future-edge channel invalidate Chapter 5?

Some reviewers called the headline result exposed; others accepted the existing audit. The
repository proves that the channel exists and proves that the current probe is not lineage-matched.
It does not prove that the shipped encoder exploited the channel. The correct status is
**unverified**. The author may close it experimentally or retain a visibly conditional claim, but
may not describe it as proven clean.

#### Does “MTL help”?

Yes in an operational sense: one jointly trained artifact produces both outputs and reaches the
reported comparator results. No causal category-transfer conclusion follows: freezing the region
path preserves the category gain, and cross-attention removal is null at Florida. The dissertation
must define which sense it claims.

#### Does selection bias cancel in paired differences?

Shared folds and a wider dedicated-model search provide some protection and can make the comparison
conservative in some directions. Different epoch selectors and use of the reporting fold for
selection prevent a proof of exact cancellation. Report the deltas as conditional on the
development protocol.

#### Is the new label-only analysis a ceiling?

No. It is the best observed result among four specified history-only predictors. Reviewers agree
the analysis is useful; the adversarial change gate correctly rejects the upper-bound terminology.

#### Are TeX Gyre Termes and the standalone Fundamentals chapter acceptable?

They may be accepted in practice or by precedent, but the repository's current institutional
evidence does not establish that acceptance. These are external advisor/Comissão/secretariat
decisions, not facts to infer.

### Reviewer panel outcomes

| Reviewer | Independent verdict | Main contribution to this report |
|---:|---|---|
| 01 Cold reader | Not submission-ready | Mechanism contradiction, Appendix B breakage, reader burden |
| 02 Line editor | Heavy mechanical pass required | Three swallowed phrases and sentence-level repairs |
| 03 Style auditor | Internal-law gate fail | Chapter 3–4 density/templates; bounded rather than mechanical cleanup |
| 04 Concordance checker | Cross-chapter seams remain | Scope, dates, tests, references, tracking drift |
| 05 Citation auditor | Gate fail | Splitter, negative sampling, Standley, Nash support |
| 06 Number auditor | Gate fail; main board sound | Capacity counts, derived-number provenance, gradient scope |
| 07 Claim-honesty auditor | Gate fail | Mechanism, PCGrad, ledgers, HGI, inferential verbs |
| 08 Translation fidelity | L5 fail | CoUrb seed/provenance, adaptation inventory/source of record |
| 09 Statistics/leakage skeptic | Exposed | Ch.4 shortcut, future-edge channel, preregistration and dependence |
| 10 MTL expert | At risk | Invalid PCGrad, trunk contradiction, cosine over-interpretation |
| 11 POI/mobility expert | At risk | Static shortcut, audit-window mismatch, baseline/metric estimands |
| 12 Banca simulator | Aprovado com correções substanciais | Defense kill-shots, ownership, ethics, mandatory corrections |
| 13 UFV compliance | Both builds non-compliant | Cover/approval, bibliography/font, process prerequisites |
| 14 Adversarial advisor | Hold/fail-closed | Applied-batch regressions, false ceiling, Markov explanation |
| 15 Readability editor | Major revision | Broken sentences and high-burden protocol passages |
| 16 AI credibility | Conditional fail; medium/medium risk | Disclosure truthfulness and provenance shield |
| 17 Excellence assessor | Very good; not submission-ready | Outstanding unity/insight/self-critique; visible regressions prevent excellence |
| 18 Visual presentation | Not presentable | Approval placeholder, Resumo break, oversized Appendix B float, small inherited visuals |

## Prior Review Resolution Audit

The v2 review correctly identifies many real improvements, but its “closed” count is too
optimistic for the current artifact. Later corrections reopened or exposed several items.

| Prior finding group | Current disposition | Reason |
|---|---|---|
| REV-001 future-edge channel | **Needs author input / reopened** | Channel bounded but exact shipped lineage untested |
| REV-002 static target issue | **Ch.3 narrowed; Ch.4 open** | Ch.3 is not direct lookup; Ch.4 shortcut confirmed and undisclosed |
| REV-003 selection/reporting reuse | **Partially resolved** | Optimism disclosed; “identically” and confirmatory language remain |
| REV-004 transfer attribution | **Reopened** | Discussion still names trunk; causal/operational senses conflict |
| REV-005/011 balancers | **Reopened** | PCGrad remains counted despite invalid wiring |
| REV-006 protocol scope | **Mostly resolved** | Chapter-specific split/test scope now visible |
| REV-007 statistical artifact sync | **Partially resolved** | Main arrays sync; governance/interpretation drift remains |
| REV-008 audit scope | **Partially resolved** | Limits stated, but A4 proxy and exact-lineage scope not fully rendered |
| REV-009 capacity/representation confound | **Mostly resolved** | Width caveat visible; mechanism language still too strong |
| REV-010 task reversal | **Resolved, with terminology residue** | Published task distinction preserved via frame, local naming still burdensome |
| REV-012 historical reproducibility | **Partially resolved** | Missing records disclosed, not recovered |
| REV-013 capacity control | **Reopened in wording** | Completed artifacts exist; count/statistic sentence is wrong |
| REV-014 inferential unit | **Partially resolved** | \(n=4\) visible; fold-Wilcoxon dependence and capacity count remain |
| REV-015 external-baseline/result scope | **Mostly resolved** | Arizona and protocol asymmetry improved; baseline provenance remains |
| REV-016 dataset counts/vintage | **Partially resolved** | Separate ETLs acknowledged; date conventions still drift |
| REV-017/018 language and abstracts | **Open/deferred** | Confirmed broken prose and abstract spill/length |
| REV-019 HGI adaptation | **Partially resolved** | Repurposing disclosed; compromised tuning criterion needs context |
| REV-020 citations | **Reopened** | New claim-site support audit found three material failures |
| REV-021 margins/tables | **Resolved** | No current measurable overflow |
| REV-022 visuals | **Partially resolved** | Axis fix holds; inherited visual drift remains |
| REV-023/024 UFV production | **Open** | Front matter, 12 pt bibliography, font ruling, portal preview |
| REV-025 AI disclosure | **Open** | 27 sign-offs conflict with completion/approval wording |
| REV-026 ethics | **Open** | Zero substantive rendered coverage |
| REV-027 inferential verbs | **Partially resolved** | Untested claims remain in Chapters 3–4 |
| REV-028 translation ledger | **Reopened** | Inventory/source-of-record/provenance drift |
| REV-029 float placement | **Resolved** | No floats-only page; new defects are comment swallowing, not floats |
| NEW-1 artifacts | **Resolved** | Key result artifacts are committed |
| NEW-2 freeze control | **Mostly resolved** | Correct negative inference; later trunk sentence contradicts it |
| NEW-3 test licensing | **Reopened** | Fundamentals says either test licenses “outperforms” |
| NEW-4 pointer | **Resolved** | Correct chapter target |
| NEW-5 approval macro trap | **Resolved** | Prior student's name removed; real sheet still pending |
| NEW-6 orphan label | **Resolved** | Current orphan is a bibliography entry, a different minor issue |
| NEW-7 results-table layout | **Resolved** | Full-size split table renders |
| NEW-8 provenance sentence | **Partially resolved** | Further CoUrb execution-provenance overreach remains |
| NEW-9 omission counts | **Partially resolved** | Current ledger/count drift persists |
| NEW-10 page counts | **Reopened in governance docs** | Current PDFs are 97/92; several records remain stale |

## Prioritized Action Plan

### Phase 0 — Restore a trustworthy artifact

1. Fix the three comment-swallowed sentences.
2. Add them as checker regression fixtures and declare the PDF-check dependency.
3. Rebuild both variants and inspect the affected pages directly.
4. Do not send the current PDF to the advisor before this phase is complete.

### Phase 1 — Correct the thesis-level scientific answer

1. Remove Chapter 4 static results from the representation diagnosis or report a valid target-masked
   rerun.
2. Rewrite “MTL helps” into separate operational and causal propositions.
3. Remove shared-trunk attribution and synchronize Chapters 1, 5, 6, Appendix B, `NORTH_STAR.md`,
   and the Chapter 5 adaptation/claim ledgers.
4. Remove invalid PCGrad evidence and state the Nash implementation consequences.
5. Rename the label-history “ceiling” and remove the false common Markov-baseline explanation.

### Phase 2 — Decide the remaining methodological evidence

1. Decide whether to run the exact-lineage future-edge audit/causal ablation on `nespedgpu`.
2. Decide whether Chapter 4 receives a target-masked rerun or a scope-only correction.
3. Recover Chapter 3/4 split, seed, checkpoint, and tuning records where possible.
4. Document whether seed 0 influenced any final recipe or inference decision.
5. Reframe preregistration, post-hoc precision, fold dependence, and selector asymmetry.

### Phase 3 — Repair evidence support and provenance

1. Correct the grouped-splitter, negative-sampling, Standley, Nash, UberNet, Sphere2Vec, and
   PMLR citation records/claims.
2. Complete the CoUrb and MobiWac adaptation/errata inventories.
3. Correct capacity counts/statistics and gradient scope.
4. Add external-baseline replication, output-domain, coverage, and window-weighted-estimand facts.
5. Synchronize page counts, inventories, governance files, and sign-off registers.

### Phase 4 — Add author/institutional facts

1. Write the ethics/data-governance statement from verified facts.
2. Record the candidate's concrete CoUrb contribution roles.
3. Complete all 27 author sign-offs and make Appendix C exact.
4. Obtain the advisor/Comissão bundle: title, English frame, translated CoUrb, Fundamentals,
   errata policy, font, and bibliography-size decision.
5. Supply cover, committee, date, approval sheet, Article 21 proof, anti-plagiarism certificate,
   and other process documents.

### Phase 5 — Editorial and production finish

1. Run the bounded language/readability pass.
2. Apply the page-specific visual pass after prose stabilizes.
3. Rebuild defense/final artifacts and verify the AcademicoPG preview offset.
4. Rerun all 18 reviewers only on the final candidate, concentrating on previously failed gates.
5. Conduct a final mock defense on the static shortcut, MTL causality, leakage, inference, ethics,
   and candidate ownership.

## Questions for the Author

The repository already answers the main result counts, current Chapter 5 board status, task
definitions, code locations, and the existence of the capacity and shuffle controls. The remaining
questions require an author, co-author, advisor, or institutional decision:

1. Will Chapter 4's static result be withdrawn from the thesis diagnosis, rerun with target masking,
   or defended under a different explicitly named estimand?
2. Should I run the exact reported Check2HGI lineage through a nonlinear future-edge/causal audit on
   `nespedgpu` in a separate implementation pass?
3. Did seed 0 influence any recipe, architecture, margin, baseline, or reporting decision?
4. Can the original Chapter 3 split/preprocessing/tuning/checkpoint record and the published CoUrb
   execution seed be recovered?
5. What exact research roles did the candidate perform for CoUrb beyond supplying MTLnet and
   presenting the paper?
6. What is the institutional CEP/IRB determination, what licences govern the Chapter 3–4 Gowalla
   snapshot and Massive-STEPS, and what privacy/security safeguards were actually used?
7. What are the booked defense date and committee, and which current secretariat ruling controls
   Article 21 quality, font substitution, Fundamentals placement, and the final portal offset?
8. May official versioned software documentation be cited for `StratifiedGroupKFold`?
9. Has the author read and approved the current 97-page artifact? Which exact AI model versions can
   be independently verified?
10. May reproduced article prose be corrected for confirmed factual/grammatical defects when every
    departure is recorded in Appendix B?

## Author Responses and Resolution Tracking

| ID | Owner | Target date | Status | Evidence/commit/artifact |
|---|---|---|---|---|
| COD-001 |  |  | Open |  |
| COD-002 |  |  | Needs author input |  |
| COD-003 |  |  | Needs author input |  |
| COD-004 |  |  | Open |  |
| COD-005 |  |  | Open |  |
| COD-006 |  |  | Open |  |
| COD-007 |  |  | Needs author input |  |
| COD-008 |  |  | Open |  |
| COD-009 |  |  | Open |  |
| COD-010 |  |  | Open |  |
| COD-011 |  |  | Needs author input |  |
| COD-012 |  |  | Needs author input |  |
| COD-013 |  |  | Needs author input |  |
| COD-014 |  |  | Open |  |
| COD-015 |  |  | Open |  |
| COD-016 |  |  | Open |  |
| COD-017 |  |  | Open |  |
| COD-018 |  |  | Open |  |

### Submission gate

Do not change the overall status to “ready” until COD-001–COD-006, COD-008, COD-011–COD-014, and
the institutional parts of COD-012 are resolved or explicitly accepted by the appropriate
decision-maker. A final reviewer pass should verify the rendered artifact, not only source diffs
and logs.

## Strengths of the Dissertation

- The dissertation has a real intellectual arc: a null result motivates a diagnosis, revised
  representations, and a stronger final system.
- The Chapter 5 result board is unusually transparent about task-specific outcomes, negative
  cases, parameter asymmetry, checkpoint convention, and inferential unit.
- The work reports inconvenient evidence instead of hiding it: transition-prior inflation,
  Alabama's deficit, Arizona's zero-centered interval, fixed-fold uncertainty, no independent test
  split, a failed leakage screen, a null cross-attention ablation, and capacity limitations.
- The time-capsule prefaces make the evolution of conclusions legible without pretending that
  earlier papers knew later results.
- User-disjoint splitting, per-fold priors, out-of-vocabulary handling, and one-artifact reporting
  are strong mobility-evaluation choices.
- The distinction among next place, next category, and next region is substantially better than in
  the first reviewed version.
- The capacity-matched controls, label-history benchmark, and Markov floors are valuable additions
  once their scope is corrected.
- The current PDFs are generally clean, readable, and free of clipping or unresolved references.
- The project maintains an unusually rich provenance trail. Its current drift is fixable and worth
  repairing rather than discarding.
- The final reflective conclusion—that the negative result was the first half of the
  contribution—is memorable and should be preserved.

### Excellence trajectory

The excellence assessor rated contribution clarity/unity, originality/insight, and critical
self-assessment as already **outstanding-grade**. The remaining dimensions were predominantly
good; only current writing/production fell below the bar because of visible regressions and front
matter. Two optional, high-return enhancements after the required corrections are:

1. a one-page cross-study synthesis matrix mapping chapter, task pair, representation, topology,
   protocol, controlled result, inference, and publication/product status; and
2. a one-page reproducibility/products inventory with pinned revisions, datasets, environments,
   commands, seeds, and result locations.

These would improve examiner navigation and artifact visibility without strengthening any
scientific claim.

## Final Readiness Statement

**Current state:** scientifically promising and substantially improved, but not yet safe for
advisor handoff or submission.

**Most important issues:** repair the malformed PDF; remove the Chapter 4 static shortcut from the
thesis diagnosis; distinguish operational joint-model success from cross-task transfer; decide the
exact-lineage leakage audit; correct statistical/citation/provenance overclaims; and complete
ethics plus UFV prerequisites.

**Recommended revision order:** artifact integrity → scientific claim scope → methodological
evidence decisions → citation/provenance synchronization → author/institutional facts →
language/visual production → final reviewer and mock-defense pass.


---

<!-- estado-rodada -->
> **Rodada encerrada · último toque 2026-08-20 · sem autoridade.**
> Este ficheiro é registo de proveniência do que foi discutido nesta passagem, não fonte
> de um facto corrente. O que ficou decidido está em [`VEREDITOS.md`](../VEREDITOS.md);
> os valores entregues estão em `CLAUDE.md` §0.1. Não copie nada daqui sem confirmar lá.
