# 42 · Excellence assessment, round 9b — the Pareto block and Appendix F at seven datasets

> **Persona:** `reviewers/17_excellence_assessor.md` (distance-from-the-top, not a defect list).
> **Scope:** the four files changed in `c94d1f19..HEAD` and nothing else —
> `src/chapters/2_fundamentals.tex` (+106), `src/chapters/apx_f_cosine.tex` (+205/−92),
> `src/chapters/1_introduction.tex` (+37/−14), `src/tables/frame/cosine.tex` (+74/−33).
> **Read as an examiner:** every page number and every quote below is from the RENDERED
> defense PDF (`make defense` → `pages=102 tex_errors=0`, exit code read directly), never
> from source. Comment stripping uses `live_text` imported from
> `src_utils/check_audit_claims.py`, so nothing a reader cannot see is judged as prose.
> **Severity scale (this persona):** REQUIRED = would cost the document at a banca or is a
> law violation; RECOMMENDED = the move from good to outstanding; OPTIONAL = polish.

---

## 0 · Verdict, and the sign-off you asked me for

**The changed prose is defensible as it stands, with two exceptions I would fix before the
advisor sees it.** The measurement work is excellent and the Pareto block is the single
best-argued passage in Chapter 2. Two sentences overreach the evidence that now supports
them, and both are in the appendix's mechanism section — the part carrying the
`[NEEDS SIGN-OFF]`.

**On the mechanism claim, my answer is: approve it with one clause deleted.** The claim as
stated is *"That is why hard sharing costs nothing in this
architecture, and why Chapter 5 finds no balancer improving on a fixed loss weighting: the
measurement explains the finding"* (p. 101). Half of that sentence is earned and half is
not, and the seven datasets do not change which half.

- **Earned.** The balancer half. Orthogonality is measured on the model Chapter 5 reports,
  the balancer screen is reported in the same chapter (p. 62–63), and the mechanism is the
  standard one. This is the reframing the dissertation should be making, and I would defend
  it aloud.
- **Not earned.** *"hard sharing costs nothing in this architecture."* The architecture
  measured here has no hard sharing in it. Chapter 5's model shares by cross-attention
  between per-task streams, and the chapter says so in the same words: *"The tasks therefore
  share by exchanging information between per-task streams, not by owning hidden layers in
  common"* (p. 65). Measured: Chapter 5 (pp. 59–77) mentions hard sharing **zero times**,
  with the same regex returning three hits in Chapter 3 as its positive control. No
  experiment anywhere in the document runs hard sharing on the check-in-level
  representation, so the appendix asserts the cost of a configuration it never measured.
- **The cut, precisely.** Delete "hard sharing costs nothing in this architecture, and why";
  the sentence then claims only what was measured, that the two tasks give a balancer nothing
  to act on in the model where the cosine was taken. What hard sharing would cost on the
  check-in-level representation is an experiment nobody ran, and it belongs in future work
  beside Chapter 6's limitation 6, not in an appendix as a consequence.

**What I would ask at the defense, in this order.** (1) "Your appendix says hard sharing
costs nothing in this architecture — which of your models is that, and where is the
hard-sharing arm of the comparison?" (2) "Your first study concluded the sharing scheme
might be the limit; Appendix F says replacing it changed little. Which experiment replaced
it?" (3) "Alabama has the largest mean in your table and is one of your two smallest
datasets. You then write that the largest datasets behave like the smallest. How do those
two sentences sit together?" (4) "The appendix measures one architecture family at one
random initialization per dataset. Your protocol elsewhere is four seeds. Why the
difference, and does the equivalence survive a second initialization?" Question 4 is the
one I would not be able to answer from the document, and it is the cheapest to close.

---

## 1 · Scorecard, changed material only

| # | Dimension | Verdict | Evidence line |
|---|---|---|---|
| 1 | Problem framing | GOOD (unchanged) | Not touched by this diff beyond FAB wording. |
| 2 | Contribution clarity & unity | **OUTSTANDING** | The new cosine paragraph (p. 23) is the frame's first mechanical bridge between §2.3 and the arc: it defines the quantity, points at where it was measured, and hedges the arc claim to *"part of the reason"*. |
| 3 | Command & critical use of literature | **OUTSTANDING** | The Pareto block reads five papers' guarantees and reports that they differ. *"Not every method claims even that much"* (p. 23) is a position, not coverage. |
| 4 | Methodological rigor | GOOD | Appendix F's unit-of-independence argument and its refusal to accept a *t*-test at n=5 for one claim while rejecting it for another are examiner-grade. One seed per dataset is the gap (finding EX-4). |
| 5 | Statistical & empirical rigor | **OUTSTANDING** | I re-derived all 63 cells of Table 11 from `gradient_cosine_observations6.parquet`; every one reproduces. The equivalence-vs-null paragraph (p. 98) is the best statistical paragraph in the document. |
| 6 | Originality & insight | **OUTSTANDING** | *"Orthogonality is not a conflict resolved but a conflict absent"* (p. 23) is a genuine reframing and it is delivered as one. |
| 7 | Critical self-assessment | GOOD → nearly OUTSTANDING | §F.4 names the untested axis and prescribes the experiment. Two sentences (EX-1, EX-2) undercut it by claiming past the boundary the same section draws. |
| 8 | Reproducibility | GOOD | Sources of record named in comments; the reader-facing text carries no artifact pointer for the cosine data (EX-7, OPTIONAL). |
| 9 | Writing, structure, voice | GOOD | Law-clean on the mechanical rules (0 em-dashes, 0 contractions, 0 banned vocabulary, -ly at 0.61%). Two register items: the F.4 paragraph break lost in the render (EX-5) and the chapter's carry-budget overrun (EX-6). |
| 10 | External validation | Not in scope of this diff. |

**Chapter-2 test (does the frame establish authority by its end?): PASSES, and better than
before this diff.** A reader who finishes §2.3 now knows what an optimum would be, why the
balancers are argued in those terms, what conflict is measured as, and that this
dissertation claims no Pareto property. That last sentence — *"This dissertation therefore
claims no Pareto property of any kind for its models"* (p. 23) — is exactly the
authoritative, self-limiting voice the rubric calls outstanding.

**Intro-conclusion loop test: unaffected by this diff, but note EX-3.** Chapter 6 still
carries the old development-time cosine (+0.001, four seeds, four Gowalla states) and does
not point at Appendix F. Measured: `\ref{apx:cosine}` occurs in exactly one live file,
`2_fundamentals.tex`. The frame chapter now cites the appendix; the conclusion, whose
sentence the appendix supersedes in every respect, does not.

---

## 2 · Findings

### EX-1 · REQUIRED · the mechanism claim names a sharing scheme that is not in the measured model

**File:** `src/chapters/apx_f_cosine.tex` §F.3 · **PDF p. 101**

> "Orthogonality leaves them nothing to resolve. That is why hard sharing costs nothing in
> this architecture, and why Chapter 5 finds no balancer improving on a fixed loss
> weighting: the measurement explains the finding."

**Why.** "This architecture" is defined two sections earlier as *"the cross-attention joint
model of Chapter~\ref{ch:mobiwac}"* (p. 102), and Chapter 5 describes that model as sharing
*"by exchanging information between per-task streams, not by owning hidden layers in
common"* (p. 65). Chapter 2 defines hard parameter sharing as the opposite: *"the tasks use
a common trunk and split only at the output heads"* (p. 22). Measured over the rendered
PDF: Chapter 5, pp. 59–77, contains **zero** occurrences of "hard sharing" or "hard
parameter sharing" (instrument validated: the same pattern returns 3 in Chapter 3,
pp. 28–44); no hard-sharing control appears in Chapter 5's ablation set, which is the
cascade rewiring, the freeze control, the place-level control, and the capacity-matched
baseline. Against AGENT_GUARDRAILS §4b V13, a claim whose function is to justify the arc is
the one to verify first; against WRITING_LAW §3 ("every number carries its reference point
and its convention"), a cost claim with no measured arm has no reference point at all.

**Fix.** Delete the hard-sharing clause and keep the half that is measured:
"Orthogonality leaves them nothing to resolve. That is why Chapter~\ref{ch:mobiwac} finds
no balancer improving on a fixed loss weighting: the measurement explains the finding."
If the author wants the broader statement, it belongs in Chapter 6's future work as the
experiment that would test it (hard sharing on the check-in-level representation), not in
an appendix as a consequence.

---

### EX-2 · REQUIRED · "replacing the sharing scheme changed so little in the first study" describes an experiment the first study did not run

**File:** `src/chapters/apx_f_cosine.tex`, opening · **PDF p. 97**

> "That is why replacing the sharing scheme changed so little in the first study, and why
> changing the representation changed so much in the second and third."

**Why.** Chapter 3 never replaced its sharing scheme. What it varied was the optimizer:
*"In our evaluation, Nash-MTL was compared with different strategies, including PCGrad and
an approach with no optimizer"* (p. 38). Its own discussion lists architectural
restrictiveness as an **untested hypothesis**, and prescribes the experiment as future work:
*"We plan to explore alternative parameter-sharing mechanisms, such as soft sharing (e.g.,
Cross-Stitch Networks) or Mixture-of-Experts (MoE) models, to test the hypothesis that the
hard-sharing architecture was overly restrictive"* (p. 43). A sentence that reports a plan
as a completed comparison is the claims-evidence mismatch the rubric lists as anti-pattern 7,
and it is the kind a banca member who has read Chapter 3 will catch immediately.
(Provenance note, so the author can price the fix: this sentence predates the round-9 diff —
`git log -S` places it at `fcdf6ad4` — but the round widened the appendix's coverage and
re-stated its opening, and the sentence is inside the block under sign-off.)

**Fix, and the appendix supplies its own wording.** §F.3 already states this argument
correctly, twenty source lines later: *"The investigation opened on the hypothesis that the
sharing scheme limited joint training, and the first study's null result was read that way at
the time"* (p. 101). That is accurate — the hypothesis was held and the result was read through
it — and it makes no claim that the scheme was replaced. The defect is confined to the opening's
compression of the same point. Bring the opening into line with it: "That is why the first
study's null result, read at the time as a limit of the sharing scheme, moved so little, and why
changing the representation moved the second and third." Or, shorter and equally supported: "That
is why no change on the optimization side moved the first study's result, and why changing the
representation moved the second and third." (I found the p. 101 sentence while re-reading the ten
ordinal hits for the cleared check in §4 — it is the single cheapest fix available for this
finding, because the author's own correct phrasing is already in the file.)

---

### EX-3 · RECOMMENDED · the appendix supersedes Chapter 6's cosine sentence and nothing tells the reader

**Files:** `src/chapters/6_conclusion.tex` (unchanged this round) vs the new §2.3 and
Appendix F · **PDF pp. 80, 23, 97**

> p. 80: "During development, on an earlier preparation of the data, the cosine similarity
> between the two tasks' gradients averaged +0.001 over four seeds on four Gowalla states,
> three of which are among the five we report, directional conflict only, a finding for this
> pair of tasks rather than a general rule."

**Why.** This is now the weakest version of a result the document states three times. The
appendix reports the same quantity on the shipped preparation, over seven datasets including
Istanbul, with a per-dataset spread, confidence intervals, and an equivalence test. The
appendix is careful to say it *"supersedes nothing there"* (p. 97) — correct, because they
are different runs — but the reader meeting p. 80 first has no way to know a stronger
measurement exists 20 pages later. Measured: `\ref{apx:cosine}` occurs in **one** live file
(`2_fundamentals.tex`); Chapters 5 and 6 carry zero pointers. This is the rubric's
"missed connections" ceiling (anti-pattern 11) in its purest form: the synthesis exists, the
structure begs for the link, and the text does not run it. The advisor's own review item
(G10.1, recorded in `_history/_round9/30_considerations_prosa_original.md`) asked for exactly this
strengthening and the appendix delivered it; the conclusion has not been told.

**Fix.** One clause in Chapter 6, no new claim: after "...rather than a general rule", add
"Appendix~\ref{apx:cosine} reports the same quantity on the configuration these results use,
across the six datasets of Chapter~\ref{ch:mobiwac} and one further Gowalla state." The count
matters, so state it the way the rest of the document does: the appendix measures **seven**
datasets, which are the dissertation's six plus Georgia, and Table 11's own caption uses exactly
that construction ("over the six datasets of Chapter~\ref{ch:mobiwac} and Georgia"). A bare "all
six" in Chapter 6 would undercount the appendix; a bare "seven" would imply the dissertation has
seven datasets, which it does not. This closes G10.1's second half at zero compute cost and turns
three isolated statements into one thread.

---

### EX-4 · RECOMMENDED · the appendix's repetition unit is one initialization per dataset, and the document never says so

**File:** `src/chapters/apx_f_cosine.tex` §F.1 · **PDF p. 97**

> "Every run is five-fold user-disjoint cross-validation over fifty epochs, so one
> configuration on one dataset is five series of fifty values"

**Why.** Measured: across pp. 97–102, "seed" appears exactly **once**, and it refers to
Chapter 5's older measurement, not to this one. The parquet has no seed column (columns:
`state, fold, epoch, cos, config`); the six single-configuration datasets carry one config
named `canonical`. So the equivalence rests on five folds at one random initialization per
dataset, while the document's registered repetition unit is the seed — *"A seed is one
complete repetition of the five-fold experiment, over the same folds, with a different random
initialization"* (p. 69) — and every headline result elsewhere uses four of them. This is not
a false statement anywhere; it is an absent convention, and WRITING_LAW §3 requires that
every number carry its convention. An examiner who has read p. 69 will ask why the
diagnostic uses a different repetition regime, and the honest answer ("one initialization,
because the diagnostic is per-epoch and cheap") is a good answer that the text should give
rather than have extracted.

**Fix.** One sentence in §F.1, stating the property rather than the reason: "Each
single-configuration dataset is measured at one random initialization over the five fixed
folds; Florida's twelve configurations are its axis of repetition." And in §F.4, add
initialization to the untested axes alongside the architecture, since the section already
has the right shape for it.

---

### EX-5 · REQUIRED (typographic) — **ALREADY FIXED IN THE WORKING TREE, uncommitted** · a paragraph break is lost in the render, fusing two axes into one paragraph

> **Status when I finished.** I found this independently in the HEAD build I was given
> (`build/main.pdf`, 10:17, `c94d1f19..HEAD`). While I was writing, a parallel track fixed it:
> the uncommitted working tree adds `\medskip\noindent` plus a blank line at
> `apx_f_cosine.tex:316`, and the 11:20 rebuild breaks the line correctly. I am reporting it
> anyway, because the finding is against the commit range I was asked to review, and because
> the two of us reached it by different routes — which is the confirmation the author wants.
> No action needed beyond committing what is already there.

**File:** `src/chapters/apx_f_cosine.tex` §F.4 · **PDF p. 101**

> "...so it is not an artifact of one choice among them. The second axis is the data. It now
> covers every dataset Chapter 5 reports on..."

**Why.** The source has "The first axis is the tuning..." and "The second axis is the
data..." as separate paragraphs, but a six-line `%` comment block sits between them with no
blank line after it (source lines 311–316), so TeX continues the first paragraph. The
render fuses the two axes the section announces one sentence earlier as *"two axes, each
answering a different objection"*, and the reader loses the signposting. This is the
sibling of the trapped-prose defect class this file has already been bitten by
(`check_trapped_prose.py`'s docstring lists eight instances): not a swallowed sentence, but
a swallowed paragraph break, which the existing gate does not detect because no words are
lost. Under the rubric, this is dimension 9's "zero sloppiness" clause, and Mullins & Kiley's
finding that presentation slips flip an examiner's reading applies with full force in the
appendix a committee will read most closely.

**Fix.** Insert a blank line after the comment block at source line 316 (before "The second
axis"). Zero prose change. Worth adding to `check_trapped_prose.py` as a second leg:
a comment block whose following source line begins a sentence that the PDF renders
mid-paragraph.

---

### EX-6 · RECOMMENDED · "the two largest states behave like the two smallest" is the one sentence in the appendix its own table contradicts

**File:** `src/chapters/apx_f_cosine.tex` §F.4 · **PDF p. 101**

> "Equivalence holds at both ends. The result is not a quirk of Florida, and it is not an
> artifact of small data either: the two largest states behave like the two smallest."

**Why.** The first two clauses are true and measured (all seven TOST pass; I reproduced
them). The third invites a comparison the table loses. Ascending by check-ins the five
states run AL 113,846 · AZ 236,450 · FL 1,407,034 · CA 3,171,380 · TX 4,089,892, so "the two
smallest" are Alabama and Arizona — and Alabama carries the largest mean in the whole table,
+0.0112, which is 42x Texas's |mean| and 16x California's, with 5/5 positive folds and the
appendix's own flagged positive tendency. Texas and California sit at −0.0003 and +0.0007
with mixed folds. They are all equivalent to zero, which is the claim that matters; they do
not "behave like" each other in the sense a reader will check. Nothing in the law forbids the
sentence, but it is the one place in this appendix where a careful reader can put the prose
against the table and find them arguing, and it costs the appendix credibility it has
otherwise earned by being scrupulous.

**Fix.** Drop the comparison and keep the scope: "Equivalence holds at both ends: the result
is not a quirk of Florida, and it is not an artifact of small data." The two datasets with a
positive tendency are already reported two pages earlier, so nothing is hidden by the cut.

---

### EX-7 · OPTIONAL · the chapter's carry-metaphor budget is now exceeded

**File:** `src/chapters/2_fundamentals.tex` (and Appendix F) · **PDF pp. 17–27, 97–102**

**Why.** WRITING_LAW §4's idiom rule sets the "metaphor budget for `carry/carries` ≤3 per
chapter". Measured on comment-stripped live prose: Chapter 2 has **6**; Appendix F has 4, of
which two entered this round ("two of Florida's carry a partial re-run", "the reason the
table carries a sign-test column"). Both new ones are load-bearing and read well; the
overrun is in the chapter as a whole, not in the new block, which has zero. Flagging so the
count is on the record rather than discovered later.

**Fix.** No change to the new prose. On the next Chapter 2 pass, convert three of the six
older instances ("carries a consequence" → "has a consequence"; "traces carry geographic
detail" → "traces record geographic detail").

---

### EX-9 · RECOMMENDED · the "worth noting" family is four instances document-wide, all four in the two files under review

**Files:** `src/chapters/2_fundamentals.tex`, `src/chapters/apx_f_cosine.tex` · **PDF pp. 21, 23, 98, 99**

> p. 23 (new this round, inside the Pareto block): "Reaching that front is not what the
> balancing methods promise, and the distance between the promise and the front **deserves one
> statement**."
> p. 99 (sentence reworded this round): "Two departures from that flat picture appear, and both
> are **worth reporting** rather than smoothing."
> p. 98: "Figure 8 shows the distributions, and one feature **needs saying** plainly..."
> p. 21: "The training objective makes that extension concrete, and it is **worth stating** here
> because it is what the fourth level costs."

**Why.** GLOSSARY §7's banned-word table registers *"it is important / worth noting that"* with
the prescribed replacement *"Note that", or just state it*, and WRITING_LAW §4 inherits that
table verbatim. Measured across all 48 live `.tex` files: this family occurs **4 times, and all
4 are in the two files this round changed** — zero elsewhere in the document. "Note that", the
law's prescribed replacement, occurs **0 times**. §4.5's own calibration is the governing
clause: *"One decorative instance is noise; density convicts."* Four in one document is a
cluster, not noise, and its concentration in the newest prose is the signature §4.1 warns about.

**What I am not saying.** Two of the four are load-bearing and I would keep them. *"both are
worth reporting rather than smoothing"* commits the appendix to not hiding the two departures
from its own headline result, which is a disposition, not decoration; *"one feature needs saying
plainly"* introduces the mean-versus-observation caveat that the same paragraph then proves.
§4.6 is explicit that *"the offense is decoration and stacking"*, and those two are neither. The
one I would cut is the new one: *"deserves one statement"* announces a statement and then makes
it, and deleting the announcement loses nothing — the Pareto-stationary sentence that follows
stands alone and is stronger without a preamble. The p. 21 instance is outside my review range
(it entered at `456eaa72`, round 6) and is recorded only so the author sees the full count.

**Fix.** In §2.3, cut the announcement and let the claim open the sentence: "Reaching that front
is not what the balancing methods promise. A point is Pareto-stationary when some convex
combination of the task gradients is zero, which is necessary for Pareto optimality without
being sufficient." Leave the other three; if the author disagrees and wants the family at zero,
the p. 21 instance is the next one to go, not the appendix's two.

**Checked and cleared, so the author does not have to re-check it.** *"The distance between that
result and a null result is the point of this appendix"* (p. 98) is **not** a violation, and I
tested it rather than assuming. It sits 73 words after the §F.2 heading, so it is not a
section-opening purpose statement of the kind §1 mandates, but §1's fourth sub-class bans
self-reference *to the writing* — its three examples are "this appendix originally reported",
"as noted above", "the boundary the paragraph above draws", all of which refer to the prose's own
history or structure. This sentence refers to the appendix's scientific purpose, which is the
same move as "the contribution of this chapter is". It stays.

---

### EX-8 · OPTIONAL · an approved errata line has not landed

**File:** `src/tables/cbic/errata*.tex` · not in the PDF

**Why.** In `PENDENCIAS.md` 2.12 the author wrote: *"Otimo trabalho, pode adicionar essa
linha no appendix B, para termos conhecimento desse detalhe menor e não deixar passar
batido"*, approving an errata row for Chapter 3's *"MGDA finds Pareto-optimal descent
directions"* (p. 31) against what `sener2018mgda` actually derives. Measured: zero
occurrences of "Pareto" in `src/tables/cbic/errata.tex`, `errata_wording.tex`, or
`apx_b_errata.tex`. Out of my remit as a defect (it is a tracker item, not changed prose) and
recorded here only because the new §2.3 states the correct version two pages earlier — *"the
fixed points of CAGrad are Pareto-stationary"*, and no Pareto-optimality claim for any
balancer — so the document now contains both readings with nothing reconciling them.

**Fix.** Add the approved row. One line.

---

## 3 · What is good, and must not be diluted

1. **The Pareto block is the best-argued passage in Chapter 2** and it does the thing the
   rubric calls outstanding: it takes a position on the literature rather than surveying it.
   *"Guarantees in this family are stated at that weaker level"* followed by four
   method-specific clauses and then *"Not every method claims even that much"* (p. 23) is
   critical use, not coverage. Protect the asymmetry; do not let a later pass smooth the four
   clauses into one.
2. **"This dissertation therefore claims no Pareto property of any kind for its models. Its
   verdicts are per-task scores measured against dedicated single-task models under the tests
   of Section 2.4"** (p. 23). A self-limiting sentence placed exactly where the temptation to
   overclaim lives. This is dimension 7 delivered in two sentences.
3. **The equivalence-versus-null paragraph** (p. 98 in the reviewed build; p. 99 once the
   working tree's caption cut is committed): *"A test that merely failed to reject
   zero would license one statement, that no conflict was detected, which is equally
   consistent with a conflict too small to see at this sample size."* Most master's
   dissertations get this backwards. Protect it verbatim.
4. **The refusal to promote the *t*-test at n=5** (p. 100 in the reviewed build; p. 99 after
   the caption cut): *"this appendix will not accept
   for one claim a basis it rejects for another"*, with California given as the case that
   proves the sign column earns its space. That is a methods-section sentence a committee
   remembers.
5. **The new §2.3 defines the cosine and reports no value there.** Measured on the rendered
   paragraph (p. 23): after removing citation markers, the only number tokens are the
   cross-references "Chapter 5" and "Chapters 4 and 5" — no cosine, no metric, no dataset
   count. (My first measurement of this ran on source and counted digits inside citation keys;
   corrected before the verdict.) This is the frame/method boundary held under pressure, and
   it is what makes the appendix legible without duplicating it.
6. **Table 11 is fully reproducible.** All 63 cells re-derived from the parquet at printed
   precision. The unit column, the positive-fold column, and the sign-test floor footnote are
   each doing work no other column does. Do not compress this table.
7. **§F.4's closing boundary** (p. 102): the untested axis is named, the answer's dependence
   on it is stated, and the exact experiment that would settle it is prescribed. Keep the
   final clause *"Section F.3 applies only to models shaped like this one"* — it is what makes
   EX-1 a fixable sentence rather than a structural problem.
8. **The advisor's seven wording items in Chapter 1 all landed cleanly.** The semicolon braid
   before *"this dissertation does not address it"* is gone and now reads as two sentences
   (p. 12); the section heading is *"Research question"* (p. 13); the redundant chapter titles
   are out of the organization bullets (p. 15). One note, RECOMMENDED-to-ignore: the FAB-12
   plural now reads *"a check-in records that users visited a given place, a point of
   interest (POI), at a given time"* (p. 12), where the singular record has a plural subject;
   the registry defines a check-in as *"One visit record (user, POI, timestamp)"*, and §2.1's
   own definition keeps the singular (*"Each record is a check-in: a user, a point of
   interest (POI), and a timestamp"*, p. 17). The advisor asked for this wording, so it is
   his call, not a defect; "records that a user visited" would satisfy both.
9. **The deleted disk paragraph is gone from the render and the rule that replaced it is
   enforced.** I re-ran `check_process_narration.py` rather than trusting the commit: rc=0,
   51 files, self-test passing both directions. The appendix now states the limitation as a
   property of the evidence and puts the reason in a comment, which is exactly the disposition
   WRITING_LAW §1 prescribes.

---

## 4 · Award lens (CTD), on this diff only

The Pareto block and Appendix F together strengthen the two double-weighted CAPES axes.
Originality: the appendix is a *mechanism* result, not another benchmark table, and a
10-page CTD summary would lead with it. Relevance: it converts the arc from three sequential
findings into one explanation. Two things stand between the appendix and that use, and both
are EX-1 and EX-2: a committee reading the mechanism section will test the two sentences that
claim past the measurement, and a single unsupported cost claim in the appendix that carries
the mechanism is worth more damage than its length suggests. Fix those two and this appendix
is a CTD asset.

---

## 5 · Measured (the instruments, so the author can re-take every count)

```
BUILD — the artifact every page number refers to
  cd src && make defense
  -> "latexbuild main -> build/main.pdf  pages=102 tex_errors=0"   (exit 0, read directly)
  NOTE: 102 pages. PENDENCIAS_RESOLVIDOS 2.12 (arquivado 2026-08-02) and _history/_round9/31_pareto.md both say the §2.3 block renders
  "na p. 23 do build de defesa de 101 paginas". The page is right; the page COUNT is stale.

CONCURRENT-EDIT CHECK — because two of my four files were edited by another track while I read
  My build is 10:17 (clean HEAD). A parallel track then edited apx_f_cosine.tex (11:15) and
  tables/frame/cosine.tex (11:20) and rebuilt at 11:20; both edits are UNCOMMITTED.
  I re-extracted the 11:20 build and re-located all 14 anchor strings behind my quotes:
    12 of 14 unchanged, including every page cited in EX-1, EX-2, EX-3, EX-4 and EX-6.
    2 shifted, both from the Table 11 caption cut (197 words -> 64): the equivalence-vs-null
    paragraph and the "92.4 percent" sentence move p98 -> p99, and the t-test-refusal
    paragraph moves p100 -> p99. Those two appear only in my protect list (§3 items 3 and 4).
  So: page numbers in this report are correct for the reviewed commit range; after the
  working tree is committed, read protect-list items 3 and 4 on p99.

RENDERED TEXT — pypdfium2 over build/main.pdf, 102 pages. Every quote and page above comes
  from this extraction. Source was consulted only to locate paragraph breaks and comments.

COMMENT STRIPPING — from check_audit_claims import live_text, strip_text  (the (?<!\\)% rule)
  apx_f_cosine.tex: 469 lines -> 145 live non-empty lines (69% of the file is comment).

N-OF-N SWEEPS over the rendered PDF (each asserted len(hits)>0 before any verdict):
  Pareto*            15   pp. 22(2), 23(9), 31, 32, 37, 49
  hard (parameter) sharing  19   pp. 3,13,21,24,26(2),28(2),31,36(4),45,48(2),78(2),101
  seed(s)            30   15 pages; Appendix F (pp.97-102) carries exactly ONE, on p97
  shared trunk 15 | sharing topology 12 | Nash-MTL 21 | cascade 11 | equivalen* 13
  fixed weighting/fixed-weight 12 | indistinguishable 2 (pp.23,97) | MGDA 1 (p31 only)
  sharing scheme 6 (pp.31,35,78,97,101x2) | self-reference to the writing 3 (pp.18,22,24)
  Chapter 5 (pp.59-77) "hard shar*" = 0, with the SAME regex returning 3 in Ch.3 (pp.28-44)
    as its positive control. My first pass mis-attributed 2 hits to Ch.5; they are on p78,
    which is Chapter 6. Corrected before the verdict was written (V9: one match does not
    license the pair).

WORD-LEVEL LAW, new §2.3 block (494 words, comment-stripped):
  em/en dash 0 | contractions 0 | banned vocabulary 0 | true -ly adverbs 3 (0.61%, in band)
  semicolons 4, none a braid (<=1 per sentence) | carry/carries 0 in the block
  carry/carries: Chapter 2 = 6 against a per-chapter budget of 3; Appendix F = 4 (2 new)

TABLE 11 RE-DERIVED from src_utils/_history/_round7/gradient_cosine_observations6.parquet
  (4,650 rows x 5 cols; 7 states; 250 rows each except florida 3,150; folds 1..5)
  Independently recomputed n, obs, 95% CI, mean, TOST(+/-0.05), one-sample t, exact binomial
  sign test, positive-fold count for all seven rows: ALL 63 CELLS REPRODUCE at printed
  precision. (Two apparent sign-column mismatches were MY comparison using Python's
  banker's rounding on 0.0625; the table's 0.063 is the correct half-up value.)
  Also reproduced: within-margin 92.366% -> "92.4 percent"; range -0.3407/+0.5802 ->
  "-0.34 to +0.58"; negative-slope counts AL 5/5, GA 5/5, IST 2/5, CA 4/5, TX 3/5, AZ 3/5,
  FL 29/60 (prose exact); Florida config-mean span [-0.00261,+0.00457], TOST 1.28e-16;
  TOST passes on the RAW observations for all seven, supporting "equivalence holds at every
  other level of aggregation". Florida's 3,150 = 12x5x50 + 150 duplicated-epoch rows
  (50-length: 50 series; 65-length: 10), which the prose discloses.

DATASET SCALE (src/tables/mobiwac/datasets.tex, comments stripped)
  check-ins AL 113,846 ... TX 4,089,892 -> 35.92x ("thirty-six"); regions 520 ... 8,501 ->
  16.35x ("sixteen"). Both hold. Ascending by check-ins: AL, AZ, FL, CA, TX.

GATES — re-run, not trusted from a commit message
  python3 src_utils/check_process_narration.py -> rc=0, "no process narration in 51 files
  (3 exempt)", self-test passed in both directions.

CROSS-REFERENCES (per file, comments stripped)
  \ref{apx:cosine} in exactly ONE live file: chapters/2_fundamentals.tex. Chapters 5 and 6: 0.
  \ref{sec:intro:arc} occurs in exactly ONE live site across all of src/ (1_introduction.tex:70,
  the same file as its \label), not the "three other files" the round-9 comment at
  1_introduction.tex:96 asserts. Instrument validated on the same sweep: \ref{ch:mobiwac}
  returns hits in 8+ distinct files, so the method is not blind to cross-file references.
  RECOMMENDED: correct the comment; the \label decision it defends is still right, since
  keeping a stable label costs nothing.
  "Pareto" rows in Appendix B / CBIC errata tables: 0 (see EX-8).

SECTION PROPORTIONS (rendered Ch.2, chars between headings)
  2.1 14.6% | 2.2 31.1% | 2.3 24.9% | 2.4 17.4% | 2.5 10.1%
  New block = 38% of §2.3. Chapter 2 live words 4,495 -> 4,989 (+11%). §2.3 remains second
  to §2.2 in length, so the Pareto material has not unbalanced the chapter.

POST-DRAFT SWEEP (returned after the first submission; it changed the report)
  "worth noting"-family regex (worth noting/reporting/stating/saying/mentioning, needs saying/
  stating, deserves a statement, bears noting) over all 48 live .tex files, comments stripped:
    4 hits, ALL FOUR in the two files under review -- 2_fundamentals.tex x2, apx_f_cosine.tex
    x2; zero in the other 46. "Note that", the law's prescribed replacement: 0 occurrences.
    git log -S dates each: "deserves one statement" -> beebd33b (IN range); "are worth
    reporting" -> 56fdf622, sentence reworded in this round's diff (1 added, 1 removed line);
    "needs saying" -> 56fdf622; "it is worth stating" -> 456eaa72 (round 6, outside range).
    -> EX-9.
  "the point of this appendix": 73 words after the F.2 \section, so not a section-opening
    purpose statement -- but §1's ban is on self-reference to the WRITING, and this names the
    appendix's scientific purpose. Cleared, not a finding.

TWO INSTRUMENT FAILURES OF MY OWN, both caught and both recorded
  1. A subprocess git-diff run inside the analysis kernel returned an EMPTY string (cwd
     resolution) and briefly made all four "worth noting" phrases look absent from the diff.
     Caught by re-running in bash, where "deserves one statement" shows as an added line and
     the control ("Pareto dominance") returns 2. The zero was the instrument, not the data.
  2. The "The first/second" clearing verdict, corrected after review. The originating sweep
     flagged 10; my clearing verdict named three two-item pairs, which accounts for SIX, and
     presented the check as covering all ten. I had re-measured with a NARROWED regex,
     "The (first|second|third) (?:is|axis|departure)", which returns 6 -- so four of the ten
     were certified without being read. A COUNT FROM A DIFFERENT INSTRUMENT IS NOT A COUNT OF
     THE FLAGGED SET. Re-ran the originating pattern, asserted N == 10, printed all ten with
     170 characters of left context: 6 are the three real pairs, 4 are ordinal references to
     the three studies. Cleared on all ten. Reading the four also surfaced the p.101 sentence
     that now supplies EX-2's fix, so the un-inspected remainder was not inert; it held the
     cheapest repair in the file.
```

### Nothing found, stated explicitly

- **Method content migrating into the frame: NOT FOUND.** I tested this directly, because it
  is the question I was asked. The new block defines vocabulary, reports what published
  methods guarantee, and states what this dissertation does not claim. It reports **no
  measured value and no result of this work**: in the rendered §2.3 block, after removing
  citation markers, the only number tokens are the equation's task indices and the chapter
  cross-references. §2.3
  is 24.9% of the chapter, still shorter than §2.2, and the chapter grew 11%. Two of the
  three new paragraphs are pure literature; the third is a definition plus a `\ref`. This is
  fundamentals doing its job.
- **Fabricated or unverifiable citations in the new block: NOT FOUND.** Every clause is
  attributed to a specific paper, the five keys resolve in the bibliography, and the
  provenance comment records arXiv IDs with page numbers for each guarantee. I did not
  re-open the five PDFs (out of remit for this persona), so this is a coherence check, not a
  source verification; the citation persona owns that gate.
- **Numbers disagreeing between prose, table, caption and figure caption: NOT FOUND.** All
  four sites say seven datasets and 4,650 observations, and both counts reproduce.
- **Process narration in the changed prose: NOT FOUND**, in the render or by the gate.
- **Em-dashes, contractions, banned vocabulary, semicolon braids, restating-the-section
  endings in the changed prose: NOT FOUND** (counts above).
- **Firstly/Secondly scaffolds and rule-of-three cascades: NOT FOUND**, and this one cost me a
  correction, so the audit trail is here in full. A sweep flagged **ten** "The first / The
  second" items in Appendix F. My first clearing verdict named three two-item pairs, which
  accounts for **six** of the ten, and asserted the other four were covered; a reviewer caught
  it. That is precisely the failure the brief warns about, so I re-ran the **originating**
  regex, asserted N = 10, and read all ten in context. The classification:
  **six** are three genuine two-item pairs ("The first is a positive tendency... The second is
  a decline", p. 99; "The first is about gradient balancers... The second is about the arc",
  p. 101; "The first axis is the tuning... The second axis is the data", p. 101), each a pair
  because the appendix genuinely has two of that thing.
  **Four** are not enumeration at all: they are ordinal references to the three studies of the
  collection ("the first study" / "the second and third", p. 97; "the first study's null result"
  / "the second and third studies", p. 101). The document has three studies as a matter of
  fact, so naming them by position is reference, not a rhythm device.
  Measured alongside: zero `Firstly/Secondly/Thirdly/Finally`-ly forms in the three changed
  prose files. GLOSSARY §7 bans the Firstly/Secondly scaffold and rule-of-**three** cascades;
  neither reaches any of the ten. **Cleared, on all ten, read individually.** One byproduct of
  reading the four went into EX-2 below, where it changes the prescribed fix.
- **Repo codenames in the changed prose: NOT FOUND.** The twelve Florida configuration ids
  (`T6_4_two_pass`, `shipping_florida_mtl_ep50_seed42`, …) stay in the comments and the
  parquet; the prose says "twelve configurations that vary the loss weight, the weighting
  schedule, and the training procedure".

---

*Report by the excellence assessor track, round 9b, 2026-07-30. Read-only: no `.tex` file was
modified. Findings EX-1, EX-2 and EX-5 are the three I would hold the advisor handoff for;
EX-3 and EX-4 are the two that move dimensions 2 and 4 toward outstanding.*


---

<!-- estado-rodada -->
> **Rodada encerrada · último toque 2026-08-02 · sem autoridade.**
> Este ficheiro é registo de proveniência do que foi discutido nesta passagem, não fonte
> de um facto corrente. O que ficou decidido está em [`VEREDITOS.md`](../../../VEREDITOS.md);
> os valores entregues estão em `CLAUDE.md` §0.1. Não copie nada daqui sem confirmar lá.
