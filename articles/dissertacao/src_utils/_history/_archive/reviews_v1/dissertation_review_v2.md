# Dissertation Review, version 2

**Supersedes** `dissertation_review.md` (Codex first pass, 24 July 2026, plus the Claude second
opinion of the same date). The v1 document is kept intact; nothing in it was edited or deleted.

**Review date:** 26 July 2026
**Documents reviewed:** `src/dissertacao.pdf` (defense build, 94 pages) and
`src/build/main_final.pdf` (final AcademicoPG build, 89 pages), both rebuilt this session from the
corrected source.
**Scope:** a re-audit of all 39 findings (29 REV + 10 NEW) against the working tree as it stands
today rather than as it stood on 24 July; the corrections this round applied; and a fresh
independent review of the corrected document by nine reviewer personas, the fact gate, and the
committee simulator.
**Overall disposition:** **not yet ready for submission, and the reason has changed.** The v1 gate
blocked on three scientific-validity findings requiring reruns. On the evidence, none of them does.
What now stands between this document and a defensible submission is a short list of external facts
the author alone holds, two scope disclosures, and an ethics statement that has never been written.

---

## 1. Executive summary

The v1 review's central judgment was that the empirical result might not survive scrutiny, and it
gated submission on rebuilding the representation, re-deciding the Chapter 3 and 4 estimand, and
introducing nested cross-validation. Re-audited against the code and the committed record, that
gate does not hold up:

- **REV-001** (future-label leakage in the check-in-level representation) describes a real channel,
  and the repository had already found it, named it, instrumented it, and used it to disqualify two
  encoders. The deployed encoder family measures at the clean autocorrelation ceiling. The defect
  was never the leak; it was that the dissertation asserted the negative and never showed the
  measurement. **Chapter 5 now shows it, with its three limits stated.**
- **REV-002** must be split. Its Chapter 3 half is refuted by code the reviewer did not open. Its
  Chapter 4 half is real, and this round measured it, with an unfavourable answer for the author's
  hypothesis (Section 3.1 below).
- **REV-003** (checkpoint selection on the reporting fold) is confirmed, was already disclosed
  twice in the text, and needed one sentence naming the consequence. It has it now.

Of the 39 findings, **26 are closed in the source this round**, 3 were already closed before it, 6
require an external fact or a decision only the author can make, and 4 are deliberately deferred.
The corrected document builds clean in both variants: **zero overfull boxes** (two measurable
margin violations eliminated), **zero undefined citations**, **zero undefined references**, **zero
BibTeX errors**, no floats-only page, and the repository lint at exit 0.

The independent re-review of the corrected build returned: fact gate **PASS with corrections** after
its one blocker was cleared; nine personas at **2 blockers, 16 majors**, both blockers now fixed;
committee simulator **aprovado com correções menores**, which is the modal defense outcome, with its
own note that without this round's disclosures the verdict would have been *correções
substanciais*.

**The two things that most threaten the defense are no longer methodological.** They are the absent
data-ethics statement, which a committee will ask about and which cannot be written without three
facts the author holds, and the unscoped Chapter 4 static task. Both are in `PENDENCIAS.md`.

### Verification failures in this round, disclosed

Four defects in my own checking, all found by review rather than by me, and all corrected. They are
recorded here because the v1 review's weakest passages came from trusting a check instead of
running one, and the same failure mode caught me.

1. **The undefined-citation check was blind.** It reported "0 undefined citations" while four
   citations rendered as `(??)` in both delivered PDFs. The check matched line-anchored patterns;
   LaTeX wraps warnings across lines, so every wrapped warning was invisible. Three independent
   reviewers caught what I had certified as clean. The checker now flattens the log before matching
   and reads the BibTeX log as well, where the decisive error actually lived.
2. **The floats-only-page check was insensitive.** It relied on the log line "Text page N contains
   only floats", which LaTeX does not emit for every such page. It reported "none" for a build whose
   page 71 was in fact floats-only. Floats-only pages are now measured from the PDF text layer, not
   inferred from the log.
3. **A commit message recorded "no floats-only page" as verified when it was not.** That commit is
   `2f1cd5b3`. The claim came from the insensitive check above, and page 71 was floats-only at the
   time it was written; the condition was genuinely fixed in the next commit, `e84b37c0`. The
   commit record is left as written, since rewriting history would hide the error, and the
   correction is recorded here instead.
4. **Two build reports presented an un-rebuilt variant as fresh.** The build script printed a line
   for every log file present, including the final-build log, even when only the defense build had
   been run, so two commit messages quoted final-build numbers that a later genuine build happened
   to reproduce but that had not been measured at the time. The script now reports only the variants
   the invocation actually built.

A fifth, smaller overstatement: the numeral audit said "all Chapter 6 numerals trace to the
committed README or summary JSON" after probing eight of the ten new numerals. The two unprobed
values were `64` and `192`, the width-asymmetry figures; both have since been traced to
`4_courb.tex:221` (which prints the concatenated representation as an element of R^192) and `:119`
(the monolithic 64-dimensional baseline).

---

## 2. Disposition of every finding

Legend: **CLOSED** the source now handles it; **AUTHOR** blocked on a fact or decision only the
author holds; **DEFERRED** deliberately postponed with a reason.

| ID | v1 severity | Disposition | What actually happened |
|---|---|---|---|
| REV-001 | Critical | **CLOSED, and the reference level rebuilt** | Mechanism confirmed. The audit existed and was never cited; Ch.5 now reports it with its three limits. This round also rebuilt the label-only ceiling the audit reads against, which found the chapter's absolute claim overstated and replaced it with the relative one it can support (Section 5.6 below, new Appendix D). |
| REV-002 | Critical | **Ch.3 REFUTED; Ch.4 AUTHOR** | Ch.3 is spatial homophily, not leakage. Ch.4 is confirmed and now measured (Section 3.1). |
| REV-003 | Critical | **CLOSED** | Confirmed, already disclosed twice; the missing consequence sentence is now the second of three limits, without claiming exact cancellation. |
| REV-004 | Major | **CLOSED before this round** | The text already says the opposite of the alleged overclaim. |
| REV-005 | Major | **CLOSED per the author's ruling; one conflict escalated** | The Ch.3 pointer fix the author asked for is applied. The author's "no Ch.3 caveat" ruling conflicts with a standing NORTH_STAR instruction for Ch.4; escalated rather than silently resolved. |
| REV-006 | Major | **CLOSED** | The strongest finding in v1. Three loci corrected: Appendix A's universal-protocol sentence (three separate falsehoods), and two in Ch.2. Both halves fixed, split axis and significance testing. |
| REV-007 | Major | **CLOSED in source** | Resolved by the prior round's uncommitted edits, now committed. Two repository-hygiene residuals carried to `PENDENCIAS.md`. |
| REV-008 | Major | **CLOSED** | The absolute "passes no usable information" is replaced by four bounded channels, and the forward-edge audit is cited for the first time. |
| REV-009 | Major | **CLOSED** | The 64-to-192 width asymmetry now reaches the reader in Ch.6, pointing at Ch.4's own missing-control sentence. Ch.4 untouched, as the author directed. |
| REV-010 | Major | **CLOSED** | One footnote; published sentence preserved. The alleged truncation was a display artifact, disproved by byte comparison against the published source. |
| REV-011 | Major | **CLOSED per the author's wording; one recommendation open** | "At their default configurations" applied. The qualifier does not cover PCGrad, whose exclusion is a wiring result; recommendation recorded, name kept pending the author's ruling. |
| REV-012 | Major | **CLOSED** | Ch.4's single seed recovered from the released code of record and declared. Ch.3's run logs are genuinely lost and are stated as such. |
| REV-013 | Major | **CLOSED** | The artifacts were committed on 24 July; this round replaced the now-false partial-California sentence with the completed run and scoped the parameter-count claim. |
| REV-014 | Major | **CLOSED** | Six loci plus the GLOSSARY, which contradicted itself and was fixed first. The 20 fitted models stay visible; the inferential n = 4 is named. |
| REV-015 | Major | **CLOSED** | The single unqualified sentence is qualified. Arizona is never upgraded, at any of six sites. |
| REV-016 | Major | **CLOSED** | Reader-facing note on the two Gowalla extractions added, with the category-mapping-drift mechanism quoted. |
| REV-017 | Major | **CLOSED, bounded** | Bounded to non-parsing sentences, the task-noun reconciliation, and the inferential verbs, per the author. No general style normalization: it would trip the variance-compression failure mode. |
| REV-018 | Moderate | **DEFERRED** | No UFV word or page limit exists; verified against the manual. The author's instruction is to do this last. |
| REV-019 | Moderate | **CLOSED** | The reviewer's premise was wrong. The real residual, the repurposing of the POI-level output, is now named, together with the retuned cross-region weight, which works in the author's favour. |
| REV-020 | Moderate | **CLOSED (4 of 5); 1 correctly refused** | Kohavi DOI dropped, Rußwurm re-typed to ICLR 2024, orphan row rephrased, Nash claim corrected. The Pedregosa item is a recorded author ruling and was not reopened. |
| REV-021 | Major | **CLOSED and measured** | Both overfull boxes eliminated. The Ch.2 lineage table was redesigned as `tabularx`, not scaled. |
| REV-022 | Moderate | **PART CLOSED; AUTHOR for the rest** | Axis label corrected and figure regenerated. The Portuguese labels in the Ch.4 figure are blocked on missing source art. |
| REV-023 | Major | **PART CLOSED; AUTHOR for the rest** | "Three published studies" corrected; page counts synchronized; the approval-sheet macro that hardcoded a prior student's name defused. Committee, date, and cover remain the author's. |
| REV-024 | Major | **AUTHOR** | A real deviation with a same-advisor precedent that passed. The edit is one deletion; the consequence is roughly two pages, which interacts with pagination. |
| REV-025 | Major | **AUTHOR RULED** | The author ruled Appendix C stays as written. The 27 sign-off markers are inventoried in `PENDENCIAS.md`. |
| REV-026 | Moderate | **AUTHOR, and it is the most exposed open item** | Zero rendered sentences on ethics, privacy, licensing, or consent. The licence research is done; the missing inputs are three facts. |
| REV-027 | Major | **CLOSED for Ch.3; refuted for Ch.4** | Four substitutions where the word attaches to this study's own comparisons. The hypothesis and cited-work uses were deliberately left. Ch.4 has zero occurrences. |
| REV-028 | Moderate | **CLOSED** | The ledger was complete; the reader-facing record was not. Counts corrected, B4 reclassified, omissions disclosed. |
| REV-029 | Major | **CLOSED, in two passes** | Seven floats relaxed; three declarations moved. A second pass was needed after the first left one floats-only page. |
| NEW-1 | Blocker | **CLOSED before this round** | Artifacts committed 24 July. |
| NEW-2 | Major | **CLOSED** | The freeze control is now stated against the basis it was measured on, with its single-seed footing disclosed. |
| NEW-3 | Major | **CLOSED in source** | Ch.2 and Ch.5 now agree on which test licenses which verb. |
| NEW-4 | Moderate | **CLOSED** | The pointer names Chapter 5. Verified that Chapter 4 does train with Nash-MTL, so the correction was necessary. |
| NEW-5 | Trap | **CLOSED** | The approval macro no longer carries a prior student's name. |
| NEW-6 | Minor | **CLOSED** | The errata row names the work instead of printing an orphaned key. |
| NEW-7 | Moderate | **CLOSED and measured** | The results table was split at its own rule rather than scaled harder. It renders at full body size; all 78 cells and every marker verified identical. |
| NEW-8 | Moderate | **CLOSED** | The inaccurate provenance sentence is corrected. |
| NEW-9 | Moderate | **CLOSED** | Ch.4's undercount was worse than reported (eight, not three). Ch.3 and Ch.5 checked for the same pattern. |
| NEW-10 | Minor | **CLOSED** | Page counts corrected everywhere, with the measurement dated and the review-suite staleness noted. |

---

## 3. Author take against Claude take: the reconciliation

Where the two agreed, the agreed action was applied and needs no discussion here. Five divergences
mattered.

### 3.1 REV-002, Chapter 4: the author's hypothesis is refuted by measurement

The author wrote: *"if I am not wrong it used the fclass and not the category ... let's eval how
huge is this problem, cause the numbers were very near with the DGI."*

The premise is correct. It does not help, and this round measured why. On
`data/checkins_by_state/Alabama.parquet` (113,846 rows), the corpus carries **275 distinct `fclass`
values** (the fine-grained spot category: Airport, Coffee Shop, Seafood) against the **7 top-level
categories** that are the prediction target. Every one of the 275 maps to **exactly one** category.
**Zero** map to more than one.

The chain, each link verified in code:

1. `research/embeddings/hgi/poi2vec.py:486-487` sets
   `poi_embeddings[valid] = fclass_embeddings[fclass_values[valid]]`, so the place vector is a pure
   function of `fclass`.
2. `fclass` determines `category` deterministically, as measured above.
3. By composition, the place embedding determines the target category exactly.

Using `fclass` rather than `category` therefore makes the input *more* informative about the target,
not less. For the **static** task this has an analytic answer: the input is a deterministic function
of the label, so the score measures how well the model inverts a lookup table, not inductive
category inference. The observation that the numbers "were very near the DGI" is consistent with
this rather than reassuring against it, since DGI's input is neighbour-averaged one-hots of the same
taxonomy.

The **sequential** task in both chapters is clean (`3_cbic.tex:161-167`, `4_courb.tex:125`) and is
unaffected. The v1 reviewer did not draw that distinction, and it matters a great deal: it is the
difference between a scoping sentence and a retraction.

Because Chapter 4 is a co-authored published paper with Tarik as first author, the preface sentence
is drafted and queued for courtesy notice rather than applied unilaterally. The author's own
suggestion, an appendix carrying the measurement, is the right home for it.

### 3.2 REV-005: the author's ruling conflicts with a standing instruction

The author ruled: no Chapter 3 caveat, no Chapter 3 errata, fix only the pointer. That is applied
exactly. But `NORTH_STAR.md:146` lists "Nash-MTL caveat as in Ch.3" as a Chapter 4 honesty item,
written and never executed. A later author ruling now sits against a standing written instruction.

That conflict is the author's to resolve, so it is escalated rather than settled in either
direction. Note the scope this preserves: only the optimizer-preference claim is affected. Chapter
3's headline does not depend on which balancer was live, and Chapter 5 does not use Nash at all.

### 3.3 REV-014: errata is the wrong instrument

The author leaned toward leaving the text and adding an errata acknowledgment. Appendix B exists to
declare departures from *published* text; all six loci are the author's own frame prose plus the
GLOSSARY. An errata row there would declare a departure from nothing.

The author's substantive point is preserved: twenty fitted models remain twenty fitted models, and
the corrected phrasing states both numbers, so the reader sees the full effort and the honest
inferential unit in the same clause. One part was not discretionary: `GLOSSARY.md` contradicted
itself, and it is fail-closed law for the whole document, so it was fixed first.

### 3.4 REV-001 and REV-008: extrapolation across datasets is not available

The author asked whether the Florida result can be extrapolated to the other states. It cannot, and
the repository's own record is what forbids it:

1. **The gate is per-encoder and it already disqualified two encoders.** A test whose function is to
   separate encoders cannot be assumed to transfer across the things it separates.
2. **The probe is linear, and it is documented to have missed a nonlinear leak.** `RESCREEN.md:94`
   records one encoder passing the per-step gate and leaking under a sequence model.
3. **The shipped lineage was never sniffed.** Only an ancestor build was measured.

Extrapolating would be exactly the move the claim registry forbids. The defensible position, and the
one now in the text, is to cite the audit, scope the claim to the channels it bounds, and name the
coverage. What the additional runs would and would not close is scoped in `PENDENCIAS.md`.

### 3.5 REV-017: the author's conservatism is adopted as the rule

The author asked for restraint, worrying that many changes would read badly. That instinct is right,
and for a second reason he does not state: a broad style normalization would trip the
variance-compression failure mode named in `AGENT_GUARDRAILS.md:190` and `WRITING_LAW.md §4.3`.

This is now measured rather than asserted. The style auditor found that the **most-edited chapters
carry the highest sentence-length dispersion** (Ch.6 CV 0.640, Ch.5 0.497) against the barely-edited
paper chapters (0.414, 0.424). Had the edit pass homogenized the prose, those numbers would run the
other way.

---

## 4. What the v1 review got wrong

Recorded so this version does not re-inherit it. Each was verified firsthand.

- **REV-002(a) is refuted by code.** The DGI encoder consumes neighbour-averaged one-hots with self
  excluded (`research/embeddings/dgi/preprocess.py:115-130`). Chapter 3's static task is spatial
  homophily, which is what the chapter motivates.
- **REV-004 and REV-015 are refuted by the text.** Both already say what the review asks them to say.
- **REV-019's premise is wrong.** `hgi.py` exports POI-level and region-level embeddings, and the
  cited paper names POIs in its title.
- **REV-020(b) is refuted and was already ruled on.** Citing the library paper for a library feature
  is standard.
- **REV-021's second box is not an equation** but a prose paragraph with unbreakable inline math,
  which changes the fix.
- **REV-027 is refuted for Chapter 4**, which contains zero occurrences of "significant".
- **REV-010's three contradictions are one**, and the preface the reviewer read as the defect is the
  fix.
- **The gate itself was wrong.** Blocking readiness on REV-001 to REV-003 pending reruns was not
  warranted by the evidence. The binding items are administrative and disclosural.

A pattern worth naming: the v1 review read the LaTeX and the documentation but not the
implementation, and its file-level assertions should be treated as leads rather than findings. Its
strongest work (REV-006, REV-021, REV-023, REV-029) is where it read the rendered artifact.

---

## 5. The independent re-review of the corrected build

Eleven of the eighteen personas ran, plus the fact gate and the committee simulator, all fresh-eyes
and read-only on the rebuilt document. Reports in `src_utils/_history/_review_v2/` and
`src_utils/_history/_specialists_v2/`.

**Coverage: fourteen of the eighteen personas ran, plus both specialists.** Nine text/fact/domain
personas and the two specialists ran first (01, 03, 04, 05, 06, 07, 09, 15, 18, the fact gate, and 12
the committee simulator). The three that the first pass identified as real gaps were then run on the
author's instruction, and they turned out to be the highest-yield of the round: **08 (translation
fidelity)**, mandatory under the suite's own L5 rule and never previously run; **10 (MTL expert)**;
and **11 (POI/mobility expert)**. Between them they returned four blockers, every one of which was a
real defect in the delivered document, and each is now fixed (Section 5.7).

Four personas did not run, and none is a gap: 02 (line editor) is subsumed by 15 on the same text;
14 (adversarial advisor) gates proposed edit batches before application, and this round applied its
edits under the author's standing rulings rather than proposing a batch; 16 (AI-credibility) runs
after 03 passes, which happened only at the end of the round; and 13 (UFV compliance) is a
pre-submission gate whose two inputs, the committee facts and the bibliography font call, are author
decisions still pending.

### 5.1 Verdicts

| Reviewer | Verdict | Blockers |
|---|---|---|
| Fact gate (G2) | FAIL, then PASS once the blocker cleared | 1, fixed |
| 04 concordance | Coherent, two seams | 0 |
| 05 citations | GATE FAIL | 1, fixed |
| 06 numbers | GATE PASS | 0 |
| 07 claim honesty | GATE PASS | 0 |
| 09 stats and leakage | Survives with corrections | 0 |
| 03 style | GATE PASS | 0 |
| 15 readability | 7.5 / 10 | 0 |
| 18 visual | Needs a visual pass | 1 |
| 01 cold reader | Followable, no reader checked out | 0 |
| Committee simulator | **Aprovado com correções menores** | 2, both fixed |

### 5.2 The blockers they found, and what they were

**A cited reference was missing from the printed bibliography.** Four citations rendered as `(??)`
on defense pages 21, 45, 49 and 50. Two independent causes, both now fixed: `references.bib` carried
a bare at-sign inside a comment, which BibTeX reads as an entry start and which made it skip the
entry that followed; and stale 25 July `chapters/*.aux` and `main.aux` files were **committed at the
source root**, where BibTeX resolves them ahead of `build/`, feeding it a pre-rename citation key.
The residue is removed, gitignored, and the reason recorded in the ignore file so it cannot recur.

**Appendix A rendered a broken sentence.** A line of real prose had been swallowed onto a comment
line, so the appendix read "released with the code. collection of one-off scripts". Fixed, and the
whole document swept for the same failure class.

**A floats-only page.** The first float pass left page 71 carrying only floats and split the
Section 5.6.2 argument across three pages. A second pass moved Figure 7 one paragraph later; the
page now carries 360 word-tokens of prose against 263, and the argument reads continuously.

### 5.3 What the reviewers confirmed about this round

Measured, not taken on report: both overfull boxes gone; all three Chapter 5 tables now render at
**11.96 pt**, full body size, against the 8.13 and 8.00 pt the v1 review measured; no table renders
before its introducing heading; the Wilcoxon-versus-*t* sentence that persona 09 had called the
single weakest methodological sentence in the experimental chapters is fixed, with the registered
per-fold test now actually run at all six datasets; all four grounds of the representation-integrity
paragraph trace to source, including the leak-sniff values to four decimals; the inferential unit is
identical at every site; and Arizona is never upgraded.

### 5.4 Disagreements, recorded not resolved

The reviewers were asked to surface conflicts rather than silently pick a side.

1. **The four-grounds paragraph.** Persona 09 calls it the round's strongest work and warns against
   editing its defenses away; personas 15 and 01 call its 546 unbroken words the document's worst
   readability failure. Both are right, and they are compatible: the fix is break-insertion with no
   words changed. A careless application of the readability finding would damage what 09 protects.
2. **Chapter 6's opening sentence.** The scope qualification that persona 07 records as necessary
   produced what 15 and 01 call the hardest sentence in the document, at 110 words. The correction
   and its readability cost arrived in the same edit.
3. **Chapter 3's adverb density**, at 1.69 percent, is double the band. Persona 03 measures it and
   declines to recommend a fix, because it is reproduced published prose. Recorded so that a later
   pass does not "fix" it on the number alone.

### 5.5 What the committee simulator says

**Aprovado com correções menores**, the modal outcome, with four *obrigatórias*. Its own calibration
note is worth quoting to the author: without this round's disclosures, the verdict would have been
*correções substanciais*.

Its two hardest questions land where this review agrees the document is thinnest: the Chapter 3 and
4 static task, whose input is derived from the label, and the total absence of a data-ethics
statement. Its most useful observation for defense preparation is that the leakage answer needs a
symmetry argument the text does not yet make, that the channel is shared by both arms and therefore
threatens absolute scores rather than the joint-versus-dedicated difference, together with the
exception the author should volunteer rather than concede: the place-level against check-in-level
comparison does not get that protection.

---

## 5.6 The autocorrelation ceiling, rebuilt

Requested by the author after the first pass of this review recommended against running the probe
extension. Reconstructing the reference level turned out to be the more valuable half of that work,
and it changed a claim in Chapter 5.

**The conflation.** The internal record uses "autocorrelation ceiling" for two different
quantities. `RESCREEN.md:57` applies it to a level of about 0.45; `RESCREEN.md:87` applies it to the
clean control at about 0.41. They are not the same thing:

- the **clean reference encoder** is what `leak_sniff.py` compares against in code
  (`:63`, `:87`: flag when `perstep > control + margin`, margin 0.03). At Florida, 0.4090.
- the **label-only ceiling** is what the genuine category history permits on its own. It is a
  property of the label sequence, not of any encoder, and it had never been measured.

Chapter 5 inherited the conflation, stating that a clean reference encoder "sets" the ceiling at
about 0.41.

**The measurement.** `scripts/embedding_eval/autocorrelation_ceiling.py` reads no embeddings. It
derives the last-visited category by the same rule the training inputs use
(`src/data/inputs/next_region.py:132-146`) and evaluates four label-only predictors under the
probe's own protocol, five folds grouped by user, macro-F1 averaged over folds. The ceiling is the
best of the four:

| Dataset | Label-only ceiling | Majority floor |
|---|---|---|
| Alabama | 0.2800 | 0.0727 |
| Arizona | 0.3232 | 0.0725 |
| Florida | 0.3617 | 0.0566 |
| California | 0.3242 | 0.0704 |
| Istanbul | 0.3016 | 0.0715 |

**Two readings, pointing in different directions.** The screen's own verdicts are unaffected,
because they were always relative: the disqualified attention encoder clears the reference by 8.9
points against a three-point margin, so the decision does not depend on where the ceiling sits. The
absolute reading is weaker than the chapter claimed: every encoder screened at Florida, the clean
references included, scores four to six points above the label-only ceiling. That is not evidence of
a leak, since a per-visit vector legitimately carries the place, its neighborhood, and the hour of
the visit, any of which predicts the next category without information flowing backward in time.
What it means is that the screen bounds encoders against each other and not against an absolute
standard.

**Applied.** The four-grounds paragraph now makes the relative claim and cites the measured ceiling;
Appendix D carries the table and both readings; two terms entered the GLOSSARY specifically so they
cannot be swapped again. No encoder number changed, and every one still traces to
`leak_sniff_fl.csv` and `leak_sniff_resln_fl.csv`.

**Coverage limits, stated in the appendix.** Texas is absent because
`output/check2hgi/texas/temp/` retains no check-in graph or window file, only the design-engine
embeddings, so the ceiling there needs preprocessing re-run. For Istanbul, 196 of 29,816 places
carry more than one category across the record; the modal category is used, and dropping every
ambiguous place moves the result by less than a thousandth.

**What this does not close.** Two of the three limits Chapter 5 declares stand: the probe is linear,
and the record documents an encoder that passed the linear screen and leaked under a sequence model;
and it measures ancestor builds rather than the shipped lineage. Running the probe at the four
datasets that now have a ceiling became possible, and is offered to the author as a decision, but
the comparison that matters most needs the shipped lineage re-exported.

## 5.7 The three domain and fidelity passes, and what they caught

Run after the first pass flagged them as gaps. They found four blockers that fourteen other readings,
two build gates, and this review's own author had all missed. Each is fixed and committed.

**The L5 translation gate (persona 08) found published text missing from the document.** A round-4
overfull-box fix in Chapter 4 had appended the second half of a published sentence to the end of its
own comment line, so three method facts, that the POI graph is built by Delaunay triangulation over
geographic coordinates, that edges are weighted by logarithmic decay of the Haversine distance, and
that connections between distinct counties are penalized, silently did not render, and the chapter
printed a sentence ending mid-clause. Verified before repair: the words "Haversine" and "GEOIDs" each
occurred zero times in the delivered PDF. The gate otherwise reported zero number mismatches and zero
claim-strength drifts against the published Portuguese record, which it obtained rather than assuming
the repository copy was authoritative.

**The MTL expert (persona 10) found the central mechanism claim overstated.** Chapter 5 attributed
the category gain to "a stronger shared trunk" and foreclosed hedging with "we report this
attribution as a finding, not a hypothesis". The freeze control that backs it removes region
training, so it can establish that the gain is not cross-task transfer but cannot locate which part
of the joint architecture produces it. The repository holds an arm that tests the trunk directly and
disagrees: with the entire cross-attention stack removed at Florida, next-category macro-F1 moves by
$-0.04 \pm 0.13$, which a paired test cannot separate from zero. Asserting a named mechanism as
settled while holding a null result for that exact mechanism is the sharpest thing a referee can
find, and the released code makes it one flag away. The negative result is retained as a finding; the
positive attribution is downgraded to the joint architecture and the disconfirming ablation is now
disclosed in the chapter.

**The POI expert (persona 11) found the external comparison unreconciled with the study's own
floor.** Chapter 5 called the external systems the per-task state of the art on our data, and twenty
pages later printed a non-learned first-order Markov floor that is above HMT-GRN at all six datasets,
above the ReHDM reference at three, and above STAN at four. Both sets of numbers were correct and
traceable; nothing connected them. The chapter now states the comparison directly and explains it as
a property of the sliding-window protocol rather than a verdict on those systems, and treats the
floor as the reference the region task must clear.

The same reviewer also re-derived the category determinism at five states rather than the one this
review had measured, and found it holds everywhere: 284 to 365 distinct fine-grained values per
state, none of them mapping to more than one of the seven target classes. That strengthens the
finding in Section 3.1 and removes any question of it being a single-dataset artifact.

Three further findings were verified and applied: the gradient-cosine measurement is pooled over four
Gowalla states including Georgia, which the dissertation does not otherwise report, so the scope
sentence "three of our six datasets" was wrong in both directions; CAGrad was described as bounding
conflict when its objective is a maximin over worst per-task improvement; and the Nash-MTL cost claim
that the errata table left uncorrected beside a clause it did correct is now named in the appendix's
deliberately-preserved section rather than passed over in silence.


## 6. Build state

Measured this session on the corrected source, three-pass with two BibTeX runs, both variants:

| | Defense | Final |
|---|---|---|
| Pages | 97 | 92 |
| Overfull hboxes | 0 | 0 |
| Overfull vboxes | 0 | 0 |
| Undefined citations | 0 | 0 |
| Undefined references | 0 | 0 |
| BibTeX errors | 0 | 0 |
| Floats-only pages | none | none |
| Repository lint | exit 0 | exit 0 |

The page counts grew from 89 and 84 because the corrections add text, because two tables that had
been scaled down to 8 pt now render at body size, and because Appendix D was added. The v1 review's
documented 87 and 83 were stale by two pages before this round began.

---

## 7. Application order, and why it was this order

Recorded because the order was load-bearing and a later round should reuse it.

1. **The fail-closed registry first.** `GLOSSARY.md` contradicted itself on the inferential unit,
   and it is law for the whole document. Fixing chapter text first would have propagated the
   contradiction into six more places.
2. **Governance synchronization second**, so that stale assertions did not get cited as sources by
   the later tracks.
3. **Frame prose third.** It is freely editable, carries no errata cost, and it is where most of the
   claim-scope defects lived.
4. **Published chapters fourth**, under the errata regime, with Appendix B written last within that
   track so it recorded what had actually been done rather than what was planned.
5. **Layout last**, because every text edit moves the page breaks that layout fixes depend on.
6. **Build, then independent review.** The reviewers caught two blockers that the build check had
   certified as clean, which is the argument for keeping the review after the build rather than
   merging them.

---

## 8. What remains open

Six items need the author, four are deferred by decision. All are in `PENDENCIAS.md` with the exact
input required. Ranked by exposure at the defense:

1. **The data-ethics and governance statement (REV-026).** Zero rendered sentences on privacy,
   re-identification, licensing, or consent, in a dissertation whose object is per-user movement
   traces. The committee simulator asks about it directly. The licence research is done and sits in
   `src_utils/evidence/DATASET_LICENSING_FINDINGS.md`; three facts are missing and only the author can supply
   them.
2. **The Chapter 4 static-task scope (REV-002).** Measured, unfavourable, and needing a co-author
   courtesy notice before anything is written.
3. **Committee, date, cover, and the approval sheet (REV-023).** External facts, and a submission
   blocker independent of the science.
4. **The advisor bundle**: English frame, CoUrb inclusion, final title, errata policy, and the
   bibliography font question (REV-024).
5. **The 27 sign-off markers**, including the Resumo and Abstract parity pair, which cannot be
   signed off separately.
6. **The Nash instruction conflict (REV-005)** between the author's ruling and `NORTH_STAR.md:146`.

Deferred by decision: the abstract length (REV-018, do last, no norm violated), the Chapter 4 figure
relabelling (REV-022, blocked on source art), the broad language pass (REV-017, deliberately
bounded), and the optional leak-audit extension (REV-001, scoped in `PENDENCIAS.md`).

---

## 9. Strengths, restated

The v1 review's list holds and this round did not erode it. Three additions from the fresh reviewers:

- **The honesty sentences of Chapter 5** were named as strengths by three independent personas, in
  particular "we report this attribution as a finding, not a hypothesis", "it does not follow that
  the bias cancels exactly", and "at Arizona, the interval is centered on zero, so we report a
  match, not a gain."
- **The fourth ground of the integrity paragraph undercuts itself on purpose**, reporting that one
  encoder passed the linear screen and leaked under a sequence model. A committee reads that as
  confidence, not weakness.
- **The edit pass measurably did not compress the author's voice**, which is the specific failure
  mode the project's own guardrails predicted and the reason for the bounded scope.

The document is in materially better shape than v1 described, and the remaining distance to a
defensible submission is short, concrete, and mostly not technical.


---

<!-- estado-rodada -->
> **Rodada encerrada · último toque 2026-07-27 · sem autoridade.**
> Este ficheiro é registo de proveniência do que foi discutido nesta passagem, não fonte
> de um facto corrente. O que ficou decidido está em [`VEREDITOS.md`](../../../../VEREDITOS.md);
> os valores entregues estão em `CLAUDE.md` §0.1. Não copie nada daqui sem confirmar lá.
