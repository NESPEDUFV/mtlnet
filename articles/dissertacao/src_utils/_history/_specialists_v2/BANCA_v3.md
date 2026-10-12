# BANCA_v3 — simulated arguição on the 2026-07-27 defense build

> 🛑 **GERACAO SUPERADA — nenhum numero deste ficheiro pode ser citado.**
>
> Isto e a simulacao de banca v3, corrido em 27 de julho de 2026, **antes** de a geracao v18 fechar o vazamento de rotulo
> no grafo de visitas consecutivas (fechado em 2026-08-13). As celulas de macro-F1 de categoria
> medidas aqui vem da geracao com vazamento e **nao sao as do documento entregue**.
>
> **Como reconhecer uma celula morta sem a copiar daqui:** a categoria entregue vive na casa dos
> **30 a 38**. Qualquer valor de categoria muito acima disso neste ficheiro e da geracao anterior.
>
> **O que este ficheiro ainda vale:** o registo de que estas questoes foram levantadas, por quem,
> e o que se decidiu. O raciocinio e o processo continuam legiveis. So os **valores medidos**
> e que caducaram.
>
> Antes de agir sobre qualquer coisa aqui, ler `VEREDITOS.md` na raiz da pasta: as questoes ja
> encerradas estao la com a prova, e este ficheiro nao e fonte de nenhuma delas.


**Persona:** 12 · Banca simulator (`reviewers/12_banca_simulator.md`), examiner (doutor, ML / urban
computing) on a UFV/PPGCC master's defense of a *coletânea de artigos*.
**Build under review:** `src/dissertacao.pdf`, **102 pages**, rebuilt 2026-07-27 after the correction round.
**Companion build checked:** `src/build/main_final.pdf`, **97 pages** — the two blockers below are present in
both, at the loci given.
**Method:** full pre-read with annotation list built first, then scoring, then the arguição from the
annotations. Read-only; no file in the dissertation was edited. In the defense build the printed page
number equals the PDF page from p. 13 onward, and page numbers below are printed pages.
**Numbers:** every figure I quote was re-traced this session to the source of truth named in
`reviewers/README.md §Sources of truth`. Where I could not trace something, the finding says so.
**BANCA_v2 was read first** (as instructed) and §1 states which of its concerns are closed. Findings were
re-derived independently; v2 was consulted for closure accounting, not for what to look for.

---

## 0 · Verdict

> ### APROVADO COM CORREÇÕES MENORES
> *(with the two **obrigatórias** of §4 filed and verified in the corrected version before deposit)*

Same verdict as v2, reached on a materially better document and for a different reason. The v2 verdict was
held down by four broken citations in the fundamentals chapter. Those are gone — the bibliography now
resolves 98 of 99 entries with a clean `.blg`, and the fundamentals chapter reads through without a single
rendering defect. That matters more than it sounds, because my first impression forms at the end of
Chapter 2, and this time Chapter 2 earned goodwill instead of spending it.

The corrections round also closed the one question I said the committee would certainly ask and the
document could not answer at all: **Appendix E answers it, and answers it better than I expected.** More on
that in §2.

Two things keep this from *sem ressalvas*, and both are the same class of defect as the one v2 caught:

**A word is missing from the Conclusão Geral.** Page 77, the sentence that introduces the
capacity-matched control — the single strongest piece of frame-level evidence in the dissertation — begins
mid-clause with a lowercase letter, because the word "Second," was pulled into a LaTeX comment. The
reader meets "…we do not offer the ablation as evidence that the trunk contributes nothing. a
capacity-matched dedicated baseline, run after the Chapter 5 manuscript was submitted…". This is the
**ninth** occurrence of this exact bug in this document, and the repository's own checker for it reports
zero suspects, because its threshold is two words and this tear is one word long. The defect is four
characters of missing text in the paragraph that carries the dissertation's mechanism claim.

**Chapter 5 and Appendix D contradict each other on a leakage-audit fact.** Page 66 states that *every*
encoder screened lies above the label-history benchmark; page 99 names the encoder that does not, at
0.3328 against 0.3617. Appendix D is right and Chapter 5 is wrong, the author's own source comment records
the contradiction as known and unfixed, and this sits inside the leak-audit paragraph — the one place in
the document where a committee reads every word twice.

Neither obrigatória requires an experiment, a re-run, or a restructuring: one is a missing word, the other
is a quantifier. That is what keeps this *menores*, and I applied that line rather than a feeling about
volume.

**On the removed Appendix A.2 (the deliberate structural change):** the removal is defensible, and I would
not file a correction demanding it back. But it is not free, and §2 says exactly what it costs and what
the candidate must now be able to say aloud that the text no longer says for him.

**What the correction round bought, stated plainly so it is not undone:** the artifact's credibility. v2's
verdict came with a counterfactual — that an undisclosed version of this document would have been
*correções substanciais*. That counterfactual is now spent; this build discloses. What it has instead is a
class of defect that survives every gate the repository runs, and that is the thing to fix before the
banca reads it, because a committee that finds a torn sentence on page 77 will re-read pages 1 to 76 in a
different register. I did.

---

## 1 · BANCA_v2 concerns: what is closed

Audited against the current build, not against a commit message.

| v2 finding | Status now | Evidence |
|---|---|---|
| **BLOCKER-1** — four citations render `(??)` (pp. 21, 45, 49, 50) | ✅ **CLOSED** | Zero `(??)` anywhere in 102 pages. `build/main.blg` carries **0 warnings** and no `Warning--I didn't find` line; `references.bib` holds 99 entries, `main.bbl` 98 items — the one absentee is the deliberately uncited `liu2014geographical`, declared in Appendix B (Table 15, p. 96). The `@misc`-inside-a-comment root cause is fixed at `references.bib:830-831`, which now spells the entry type out in words. |
| **BLOCKER-2** — Appendix A opens with a destroyed sentence | ✅ **CLOSED** | p. 88 now reads whole: "It is organized as a registry-driven experimental framework rather than a collection of one-off scripts: name-keyed registries expose interchangeable implementations across each axis the dissertation studies." |
| **MAJOR-4** — no privacy / consent / licensing / re-identification statement in the document | ✅ **CLOSED** (and see §2.2) | Appendix E, pp. 101–102, ~790 words: provenance and licence per corpus with the depositor caveat named, the pseudonymity-is-not-anonymity sentence, the no-de-identification concession, and the human-subjects position. |
| **NIT-1** — keep Table 9's 26.56/26.56 coincidence footnote | ✅ **KEPT** | p. 70, footnote intact. |
| **MODERATE-3** — `[VERIFY]` on the swept "Cat F1" averaging convention | ⚠️ **STILL OPEN** | `2_fundamentals.tex:174` still carries the flag; p. 20 still prints "rose monotonically from 0.74 to 0.82". Non-rendering, so not reader-facing — but still an open fact-gate item on a number that ships. |
| **MAJOR-1** — Appendix C's "passed an eighteen-reviewer panel" | ⚠️ **STILL OPEN, but now nearly true** | p. 97, sentence unchanged. With BLOCKER-1 and BLOCKER-2 fixed, the claim is far more defensible than it was; the two obrigatórias below are what still undercut it. See §4 SUG-1. |
| **MAJOR-2** — B.4 reconciles Florida only; TX and CA also disagree | ❌ **NOT ADDRESSED** | Table 5 (p. 53) and Table 8 (p. 65) still disagree on Texas (3,355,419 → 4,089,892 check-ins; 135,570 → 160,938 POIs) and California (2,535,573 → 3,171,380; 148,314 → 169,145). B.4 (pp. 93–94) still names Florida alone — the words "Texas" and "California" do not appear in it. |
| **MAJOR-3** — Ch.3/4 static category task is evaluated on inputs containing the target's own category | ❌ **NOT ADDRESSED** | p. 32 still states the node features are "category one-hot encoding of each POI"; no sentence anywhere in 102 pages scopes what Tables 2 and 6 therefore measure. I re-ran the search across the whole build. This remains the question with zero written cover (Q6 below). |
| **MODERATE-1** — Gowalla vintage differs between chapters | ❌ **NOT ADDRESSED** | Ch. 4, p. 57: "February 2009 and October 2010". Ch. 6, p. 78: "2009 and 2011". Unreconciled. |
| **MODERATE-2** — AZ ceiling's pending 2-seed top-up is undisclosed | ❌ **NOT ADDRESSED, and now a decision rather than an oversight** | The abstract's upper endpoint "9.4" still rests on AZ's +9.35. `CEILINGS_N20_FINAL.md:11-12` still records the two n=10 screens at 57.04 / 56.93 "pending a 2-seed top-up". `5_mobiwac.tex:634-639` now records that the top-up was **dropped** on 2026-07-08 and, in the same comment, states the reason for not printing the sensitivity as "author policy: hide caveats, provide on request". That is a defensible editorial choice about a rule-clean pre-registered estimator — but it is now a policy, and §4 SUG-4 says why I would still print one clause. |
| **MINOR-1** — "two encodersthat" | ❌ **NOT FIXED** | p. 49, `4_courb.tex:141`. |
| **MINOR-2** — Appendix A platform scope unsettled | ➖ **UNCHANGED** | p. 88 still scopes to "the experiments of Chapters 3 and 5". Now partly answered *elsewhere*: the same appendix states that the Chapter 4 study "ran in a separate repository", which is the disclosure v2 asked for. Q3 still lands, but the text now helps. |

**Net:** three of v2's four obrigatórias are closed, including the two rendering blockers and the ethics
gap. The one that survives (MAJOR-3) survives untouched. Two new blockers appeared, both introduced by
this round's own edits.

---

## 2 · The two structural changes, judged

### 2.1 The removal of Appendix A.2 — how a committee actually reads it

The question put to me is whether a banca would read the removal as concealment, and whether anything left
in the document depends on the disclosure that is gone. Two separate questions, and they have different
answers.

**Does anything now dangle?** No, and I checked rather than assuming. I swept the full build for every
construction that could point at the deleted section: "earlier iteration", "earlier manuscript",
"unpublished", "rejected", "was corrected", "older protocol", "precision artifact", "cost on region". The
only surviving "was corrected" passages are at p. 27 (CBIC typographical errata), p. 93 (the MobiWac
misattribution about Chapter 3, which names its own antecedent) and p. 95 (bibliography). None points at
the removed section. `Appendix A` is referenced in exactly two places, the TOC (p. 12) and its own title
page (p. 88). The acronym BRACIS appears **nowhere** in the 102 pages, and the List of Abbreviations
(p. 9) no longer carries it — the orphan NORTH_STAR §5.11 flagged has been cleaned up. **The removal is
mechanically complete.** That is the part most likely to have gone wrong, and it did not.

**Would a committee read it as concealment?** No — and I want to be precise about why, because the
author's reasoning as recorded is *almost* right and the part that is off matters for the defense.

The author's grounds are that the error trail is not constructive for the reader, and that reworking a
manuscript after a rejection is normal practice. The second half is simply correct, and no examiner in
this area would think otherwise; unpublished intermediate submissions are not part of a dissertation's
evidence base and there is no norm requiring their disclosure. UFV Normas §2.3/§2.6 ask for articles
published, accepted or submitted that are pertinent to the research. A rejected, superseded manuscript is
none of those. **A banca will not ask about a paper it has no way to know exists, and would not object if
told.** I would not file a correction demanding its return.

Where the reasoning is off is the *first* half, and only in one direction. The removal did not just cut an
error trail — it cut the document's only volunteered answer to question bank Q24, "what failed attempts
were left out, and why should I trust that the exclusion was not convenient?" In v2 that question was a
**pass**, and I recorded it as such: the text named a rejection, named the date, and then declared that
its own later work had refuted the rejected paper's headline claim. Declaring a result you later
overturned is the strongest possible answer to a question about selective reporting, and the document made
it unprompted.

It no longer makes it. So the honest accounting is not "concealment versus disclosure" — it is that the
dissertation **traded a volunteered credibility signal for a shorter read**, and that trade is the
author's to make. What changes is where the answer now has to come from: the candidate's mouth, in the
sala, unrehearsed. Q11 below is that question, and it is now one of the two or three where improvisation
would cost real ground.

One residual, and it is small but genuine. Appendix B.3 (p. 93) records that the submitted MobiWac
manuscript wrongly described Chapter 3 as having studied the region task and observed negative transfer,
and that this was corrected. A reader who wonders *how* a submitted manuscript came to contain that
particular error has no answer available; with A.2 present, the lineage of the region-task framing was
visible. I do not think a committee follows that thread — B.3 names CBIC as the antecedent and stands on
its own. But if one does, the answer is Q11's second half, and it must be ready.

**Verdict on the change: sound, mechanically clean, and it costs the candidate one written answer that he
must now be able to give aloud.** Not a correction. A defense-preparation item, and I have written it as
one.

### 2.2 Appendix E — does it answer the question I would have asked?

Yes, and on the specific point I said a committee would press, it goes further than the answer I sketched
in v2. Judged against the four things I would have wanted:

1. **Provenance of each corpus, named as an artifact rather than a citation.** Delivered, and with the
   distinction that matters: the Gowalla data actually consumed is the Figshare deposit
   (DOI 10.6084/m9.figshare.22126586.v2, CC0), and the SNAP release cited as the collection reference is
   named as "a different artifact" that "carries no place categories, and its page states no license"
   (p. 101). That is the correct disentanglement and most dissertations get it wrong.
2. **The licence caveat, not just the licence.** Delivered, unprompted, and in the form that costs the
   author something: "The dedication was applied by the depositor of this copy, identified there by a
   single name, and not by the party that collected the data… What is supportable is therefore a statement
   about the copy in hand… that Gowalla data as such is in the public domain is a broader claim, and
   nothing that could be opened supports it." I traced this to
   `src_utils/evidence/DATASET_LICENSING_FINDINGS.md §1.2–1.3` and it reproduces faithfully, including the
   unreachable upstream. The one outstanding check the record names — that the Foursquare product terms
   were not read — **is printed to the reader** (p. 101). An appendix that names its own unfinished check
   is doing the job.
3. **What the work does to the data, concretely.** Delivered, and this is the section I did not expect.
   The appendix states that the work adds *no* de-identification, that no coordinate is perturbed or
   masked, and gives the reason (the Chapter 5 target is spatial, so coarsening would change the measured
   quantity). It then names what limits exposure instead: the deposit's social-graph and user-profile files
   are never read, identifiers are carried as opaque integers, nothing links a user across collections, and
   no check-in data is redistributed because the data directory is out of version control. Those are
   checkable claims about the pipeline rather than reassurances, which is the difference between an ethics
   statement and an ethics gesture.
4. **The human-subjects position, stated as a position.** Delivered, and correctly framed: secondary
   analysis of already-public collections, no participant recruited or contacted, therefore in the
   author's judgment no committee review required — and then, crucially, "It records no approval and no
   exemption, because none was sought and none is claimed." That sentence is what stops this from being
   an implied clearance.

**The precedent paragraph is the one place I pushed, and it holds.** E.3 claims that a comparable
dissertation defended in this program in 2024, under the same advisor, on LBSN data, carries a location-
privacy statement, says which fields were left unmasked, and contains no mention of an ethics committee.
I opened that dissertation (`exemples/germano/`, 96 pages) and searched it: it carries a §2.6 "Ethical
Statement" which states that the study used "Gowalla anonymized user identifier information, but we
maintained the location without masking the latitude and longitude", and recommends mix-zones or CATS for
real-world deployment. A search of all 96 pages returns **zero** occurrences of "comitê"/"comite" and no
ethics-committee, approval-number, or submission mention. **Every clause of the precedent claim checks
out**, including the disclaimer the appendix attaches to it: "That is how a close precedent handled the
question, not a determination of the rule."

**Does it invite a harder follow-up?** One, and it is the one I would ask. The appendix is thorough about
the *training data* and silent about the *model*. The exposure a committee will reach for is not the
public check-in file — it is that a deployed artifact which ranks ten census tracts for a user's next visit
is itself an inference surface, and the user-disjoint protocol is precisely the claim that it generalizes
to users the model never saw. E.2 gestures at this by citing the mobility survey on models absorbing
information, but it never states the consequence in its own voice, and §6.3's limitations do not carry an
ethics or deployment-risk item either. That is Q12 below. It is a *better* question than the one v2 asked,
which is the correct outcome for a new appendix: it moves the conversation from "why is there nothing" to
"what about this specific thing", and the second is a conversation the candidate can win.

Two smaller notes. E.1's statement that four deposit files enter the pipeline and that the seven-category
taxonomy "arrives with the deposit" is a good, checkable disclosure — it forecloses the reading that the
author invented the taxonomy. And the appendix's closing sentence ("Should the program require a formal
determination for secondary analysis of public data, it belongs on file before deposit, and this appendix
should then name it") is an action item addressed to the author, printed in the document. I would ask
whether the secretariat has been asked. That is Q12's tail.

**Verdict on the change: it answers the question I asked in v2, at a level well above the field norm for
a master's dissertation in this area, and the follow-up it invites is answerable.**

---

## 3 · Dimension scores

| # | Dimension | v2 | **v3** | Evidence line |
|---|---|:-:|:-:|---|
| 1 | Problem clarity and delimitation | 5 | **5** | The question is bold inline (p. 14); the three targets are held apart in §2.1 (p. 18), excluded in §1.4 ("The exact next place is not predicted anywhere in this work", p. 15), and re-stated as limitation 4 (p. 78). Chapter 2 adds the fourth task (static category classification) explicitly and §1.1 (p. 13) names why it was replaced. Four load-bearing places, no drift. |
| 2 | Command of the state of the art | 4 | **5** | §2.3 takes positions rather than cataloguing: "a fixed-weight baseline is a serious competitor, and a balancer earns its place only by outperforming it" (p. 23), grounded on three independent results. §2.1 separates ends from means precisely ("Both treat the category or the region as an intermediate signal on the way to a place", p. 19). The four broken citations that held this at 4 are gone, and the "to our knowledge" novelty claim (p. 61) is now scoped by two named near-exceptions. |
| 3 | Methodological coherence | 4 | **4** | Alternatives are tested, not asserted: cascade rewired inside the model and reported as a tie (p. 74), balancers tried and reported as no help (p. 61). Held below 5 by the cascade running "under the configuration tuned for the parallel model" (p. 74, disclosed) and by limitation 6's task-pair confound (p. 78). |
| 4 | Rigor and honesty of results | 4 | **4** | Verbs bound to tests; an analysis plan "fixed during development and before any result was read" with its own departure disclosed (p. 67); floors named; Holm applied; the four next-region gains explicitly labelled "secondary results outside" the plan (p. 67). Held below 5 by the n=4 inferential unit over one fixed partition, by epoch selection reading the scored fold, and by the Ch.5/Appendix D contradiction of BLK-2. |
| 5 | Contribution | 4 | **4** | A nameable delta well above the master's bar: the check-in-level representation (+27.63 to +39.62 macro-F1 over the place embedding, Table 9, p. 70) plus a joint model that beats both dedicated models. Held below 5 because the candidate's own freeze control locates the category half in the architecture, not in cross-task transfer (p. 72) — which the text now states even more carefully than v2 saw. |
| 6 | Recognition of limitations | 4 | **5** | Six numbered limitations each tied 1:1 to a future-work item (pp. 78–79), three more inside Ch.5 §5.7, plus the volunteered fixed-partition caveat in §1.6 (p. 17) and the epoch-selection disclosure with its direction (p. 75). The absent class that held this at 4 — privacy, licensing, governance — is now Appendix E. |
| 7 | Candidate ownership | 4 | **4** | The CoUrb contribution is stated in three independent places (§1.5 p. 16; Ch.4 preface p. 43; Appendix C p. 97) and is specific: second author, presenter, first author of the baseline MTLnet. Appendix A now also discloses that the Chapter 4 study "ran in a separate repository". Held below 5 because the platform-scope sentence (p. 88) still reads "Chapters 3 and 5" while the appendix's own next paragraph implies the boundary — a reader has to assemble it. |
| 8 | Text quality | 2 | **4** | The four `(??)` are gone, the Appendix A sentence is whole, the MTLnet spelling is uniform in Ch.4's prose, and the bibliography now sets at body size (measured: 12 pt, matching Ch.2's body text) instead of the inherited `\footnotesize`. Against that: the Conclusão Geral's torn sentence (BLK-1, p. 77) and "encodersthat" (p. 49). **Not 5, and not 2** — one missing word in the conclusion is a serious defect, but it is one defect, in a document that fixed five. |
| 9 | Coletânea unity | 4 | **4** | Still the document's strongest dimension as a *coletânea*: the arc is written as a correction trail (p. 14), each preface time-indexes its own conclusions (pp. 27, 43, 58), Ch.5 §5.2.1 recaps both predecessors by name, and Appendix B is a genuine errata. Held below 5 by MAJOR-2's unreconciled TX/CA counts and by two Appendix B self-accounting errors I found this round (NEW-1, NEW-2) — the errata is the one place where being approximately right is not enough. |
| 10 | Defense-readiness of the text | 3 | **4** | The text pre-answers leakage, capacity, cascade choice, balancer choice, selection bias, cost, and — new this round — data governance. It still does not pre-answer the static-task circularity of Ch.3/4 (MAJOR-3), the "is this multi-task learning at all" reading its own freeze control invites, or the failed-attempts question that A.2 used to answer. |

**Mean 4.3, up from 3.8.** Dimensions 2, 6 and 8 moved on real changes. Dimension 8 is the one to watch:
it moved from 2 to 4 and would be a 5 the day BLK-1 is fixed.

---

## 4 · Corrections list the banca would file

### Obrigatórias

**BLOCKER-1 · The Conclusão Geral's attribution sentence is torn; a word is trapped in a comment.**

> p. 77: "…and we do not offer the ablation as evidence that the trunk contributes nothing. **a
> capacity-matched dedicated baseline, run after the Chapter 5 manuscript was submitted and reported here
> as a frame-level analysis:** a dedicated category model widened to the joint model's parameter budget…"

Locus: `src/chapters/6_conclusion.tex:110`. The line is a `%` comment ending
`…rests on the freeze control and the capacity-matched control. [NEEDS SIGN-OFF: AUTHOR] Second,` — the
word **"Second,"** sits after the bracket, inside the comment, so it never renders. The paragraph opens
"Two controls separate this claim from wishful attribution. First, the freeze control…" and the second
control now arrives with no "Second," and a lowercase "a". Present in the final build too, at p. 75.

This is not cosmetic. The sentence introduces the capacity-matched control, which is the frame-level
evidence that closes the "the joint model just has more parameters" explanation — the single strongest
argument that this collection is a dissertation rather than three papers (it was my Q5 pass in v2). Its
topic sentence is broken.

*Direction (not applied):* move `Second,` onto the following body line and terminate the comment block on
its own line.

**Root cause, and why this one is worse than the eight before it.** `src_utils/check_trapped_prose.py`
exists specifically to catch this bug and documents eight prior instances, three of them from the previous
round. It reports **0 suspects** on this build, and `make check` passes. I reproduced why: line 64 sets
`MIN_TAIL_WORDS = 2`, with the comment "`, Nash-MTL treats` is three; do not raise this". The tail here is
one word. Re-running the checker's own logic with the threshold at 1 surfaces this defect immediately,
along with six benign ledger remarks it correctly discriminates on the render test. **A gate that returns
clean on the defect it was written to catch is worse than no gate**, because this round's handoff cites
"repo lint exit 0" as evidence of a clean document. *Direction:* lower `MIN_TAIL_WORDS` to 1 and add this
case to `test_trapped_prose.py` as fixture ten. I am naming this as part of the obrigatória because the
fix to the sentence without the fix to the checker leaves instance ten free to ship.

**BLOCKER-2 · Chapter 5 and Appendix D state contradictory facts about the leak screen.**

> p. 66 (Ch. 5, §5.5.2): "**Every encoder screened, including the clean references, therefore lies above
> the label-history benchmark**, by four to six points at Florida."
>
> p. 99 (Appendix D): "**One candidate falls below the benchmark on the standardized run**, a relation-typed
> graph encoder at 0.3328 that rises to 0.4142 on the raw one."

Both cannot be true, and Appendix D is the correct one. I traced both to
`docs/results/embedding_eval/rescreen_cat/leak_sniff_fl.csv`: the `check2hgi_rgcn` row reads
`perstep = 0.3328098…`, which is **2.89 points below** the Florida benchmark of 0.3617, while its raw run
is 0.4142, above. Seven of the eight screened encoders clear the benchmark on both runs; that one clears
it on one run only. Chapter 5's "every" is false as written.

The author knows. `src/chapters/apx_d_ceiling.tex:107-108` carries: "5_mobiwac.tex:376 still asserts
'Every encoder screened … sits above'; reported for narrowing, not edited here (not my file)." The
finding was raised and left.

Two reasons this is a blocker rather than a nit. First, the locus: this is the leak-audit paragraph, the
one place a methodologically hostile examiner reads twice, and the contradicting appendix is the document
the paragraph itself points at. Finding a false universal quantifier there, three pages apart, is how a
committee decides to check everything else. Second, the fix runs *toward* the document's interest, not
away: Chapter 5's own argument is that the screen is relative rather than absolute, and the rgcn
exception is a clean illustration — it is the very encoder that "passed this screen and then leaked under
a downstream sequence model", which Chapter 5 cites two sentences later as the reason the linear form is a
screen and not a proof. The correct sentence is *stronger* than the false one.

*Direction (not applied):* narrow the quantifier in `5_mobiwac.tex:376` — e.g. every encoder screened lies
above the benchmark on the raw run, and all but one on the standardized run, with the exception pointing
at Appendix D. No number changes; no claim weakens.

### Sugestões (strongly recommended, not blocking)

**SUG-1 · Appendix C's "passed" is still ahead of the artifact (v2 MAJOR-1).**
> p. 97: "The complete first version **passed** an eighteen-reviewer panel…"

Much closer to true than it was. Fix the two obrigatórias and it becomes defensible; ship it alongside a
torn sentence in the conclusion and it invites the same inference it did in v2. *Direction:* keep the
sentence after BLK-1 and BLK-2 are closed, or soften "passed" to "was reviewed by".

**SUG-2 · Appendix B's MTLnet site count is wrong (NEW).**
> p. 92: "The reproduced text of Chapter 4 was normalized to the second form at all **24** places where
> the name appears in the printed chapter: **21 in prose, one in a figure caption, and two in table
> headings**."

I counted, in the uncommented source of `4_courb.tex` and again in the rendered pp. 43–57. The chapter
contains **28** occurrences of `MTLnet`; two are in the italic preface and four in the Chapter 3 recap
subsection, both of which are frame text the dissertation added rather than reproduced text it normalized.
That leaves **22** in the reproduced body: **18 in prose, one subsection heading ("Baseline: MTLnet with
DGI", p. 48), one figure caption (Figure 2, p. 48), and two table headings** (Tables 6 and 7, pp. 54–55).
The donor confirms the shape: `articles/CoUrb_2026/src_en/` carries 22 bare `MTLNet` sites in the same
distribution — 20 prose, one caption, one subsection heading — plus two table headings in
`resultados/tabela_comparativa_f1_{category,next}.tex`, which the counts above include.

So two things are off: the total (24 vs 22) and the breakdown, which omits the subsection heading
altogether and moves it into the prose tally. *(The figure of 26 that appears in this round's own handoff
brief is a third value and matches neither.)* No result depends on this. It matters because Appendix B is
the document's declaration of fidelity to a published article, and a wrong count there is the one kind of
error that invites a reader to recount everything else in the appendix. *Direction:* recount and state the
scope ("in the reproduced body, excluding the preface and the added recap subsection"), or drop the
enumeration and keep the qualitative statement.

**SUG-3 · Appendix B's "four further uses" accounting does not hold (NEW).**
> p. 91: "**Four further uses** of the word were left in place because they do not attribute significance
> to a measured comparison of this study: two report claims of cited work, one states the study's own
> hypothesis, and one names a chosen target level."

Chapter 3 contains exactly eight occurrences of *significant/significantly* (verified identical in source
and render), so the arithmetic of "four removed, four left" is right. The **classification** is not. Two
of the four survivors do attribute significance to this study's own untested comparisons:

> p. 40 (`3_cbic.tex:414`): "the MTL model, in this configuration, incurred a **significantly** higher
> overhead in wall time."
> p. 41 (`3_cbic.tex:423`): "The lack of **significant** improvement from the MTL model prompts an
> analysis of the potential underlying causes."

Both describe this chapter's own measurements, and the chapter runs no inferential test — which is the
exact rationale Appendix B gives for removing the word in the other four places. Meanwhile the four
categories the appendix names ("two report claims of cited work, one states the study's own hypothesis,
one names a chosen target level") match four *different* survivors: pp. 35, 36 (cited work), p. 28
(hypothesis), p. 40 (target level). That accounts for four; two more exist; the sentence says there are
four in total.

This is the finding I would raise with the least pleasure and the most effect, because Appendix B is where
the dissertation claims to have policed exactly this. *Direction:* either extend the substitution to the
two statements above (p. 40 "a higher overhead"; p. 41 "The absence of a consistent improvement"), which
is the same treatment already applied four times and reduces no claim's strength, or correct the appendix's
count and classification to name them as survivors with a stated reason. The first is cleaner.

**SUG-4 · The AZ ceiling sensitivity still reaches no reader (v2 MODERATE-2).**
The abstract's "5.3 to 9.4 macro-F1 points" (p. 5) has its upper endpoint at Arizona's +9.35, resting on
the AZ dedicated ceiling of 56.43. `CEILINGS_N20_FINAL.md:11-12` still records two n=10 screens at 57.04
and 56.93 that would move the AZ gain to about +8.8. This round's change is that
`5_mobiwac.tex:634-639` now records the top-up as **dropped** (2026-07-08) and states the non-disclosure
as policy ("author policy: hide caveats, provide on request").

I accept the estimator argument: 56.43 is the per-state maximum at the pre-registered n=20 and the
screens are n=10, so citing 56.43 is rule-clean and I would not call the number wrong. What I would still
change is one clause, for a reason that is about the defense rather than the estimator: **+9.35 is quoted
as the range endpoint in the abstract, and Arizona is named in Chapter 5 as the largest gain.** If an
examiner asks what happens to that endpoint under a fuller sweep of the comparator, the answer is "about
+8.8, and Istanbul's +8.58 becomes nearly the largest" — an answer whose absence from the text looks
worse than its presence. *Direction:* one footnote on the AZ row of Table 10 naming the screened arms and
the pre-registered rule that excludes them. It costs nothing, since the rule is on the author's side.

**SUG-5 · The Gowalla vintage still differs between chapters (v2 MODERATE-1).**
Ch. 4, p. 57: "collected between February 2009 and October 2010." Ch. 6, p. 78: "collected between 2009
and 2011." Both are defensible in isolation — Ch. 4 reproduces the published SNAP-era statement, and
Appendix E now establishes that the consumed artifact is a *different, larger* Figshare deposit whose
measured range is 2009-01-21 to 2011-08-16. Appendix E made this reconcilable for the first time, and it
is now a one-clause fix rather than an open question. *Direction:* a clause in B.4 or in limitation 1
noting that the two extractions draw on different dumps with different date coverage, pointing at
Appendix E.

**SUG-6 · B.4's reconciliation still covers one of three states (v2 MAJOR-2).**
Extend B.4's first sentence to Texas (3,355,419 → 4,089,892 check-ins) and California (2,535,573 →
3,171,380); the category-mapping mechanism it already gives covers both. A reader comparing Table 5 and
Table 8 today finds three discrepancies and one explanation.

**SUG-7 · The static-task scoping paragraph is still missing (v2 MAJOR-3).**
Unchanged from v2, and still my judgment that it is the most valuable single paragraph the author could
add. See Q6.

**MINOR-1 · p. 49: "two encodersthat represent".** Missing space, `4_courb.tex:141`.

**MINOR-2 · `[VERIFY]` still open on a rendered number.** `2_fundamentals.tex:174` against p. 20's "rose
monotonically from 0.74 to 0.82". Confirm the averaging convention or make the clause qualitative.

---

## 5 · Arguição transcript

Twelve questions, posed as I would pose them. Five are from the coletânea block (minimum four). Each
carries: what it tests, what a strong answer contains, and what the **text as it stands** supports —
because that is the part the candidate cannot improvise around. Questions the text already answers are
marked as passes and I would move through them quickly; the sala time goes to Q6, Q8 and Q11.

---

### Q1 — coletânea (bank Q19)
> *"Convença-me de que isto é uma dissertação e não três artigos grampeados. Qual é o fio condutor, em uma
> frase?"*

**Tests:** whether the collection has an argument or merely an order.
**A strong answer contains:** one sentence — the representation, together with the sharing topology built
on it, decides whether MTL helps — then the demonstration that each chapter is a *move* in that argument.
**What the text supports — fully.** p. 14 states the arc as "a negative result, its diagnosis, and its
resolution"; p. 77 closes it in the same words from the other end: "The representation, together with the
sharing topology built on it, is what the answer depends on." §1.2, §2.5 and §6.2 answer with the same
sentence in three registers, which is the test of a real fio condutor. **Pass; I would move on quickly.**

---

### Q2 — coletânea (bank Q20)
> *"O artigo 3 contradiz a conclusão do artigo 1. Em qual devo acreditar, e onde o texto me diz isso sem
> que eu tenha que descobrir sozinho?"*

**Tests:** whether inter-paper conflict is confronted or buried.
**A strong answer contains:** both conclusions are correct within their configurations; the later one
supersedes only under the stated change of representation and topology; and the reader is told at the
point of reading, not retroactively.
**What the text supports — fully, and with a device.** Every article chapter opens with an italic preface
that time-indexes it: p. 27, "Its conclusions are the conclusions of the time, for the configuration
studied here… Chapters 4 and 5 revise that verdict by changing the input representation rather than the
architecture." p. 78 refuses the easy synthesis: "The negative result of Chapter 3 and the positive
result of Chapter 5 do not contradict each other; read together, they bound the claim." **Pass.** I would
say aloud that this device is the best structural decision in the document.

---

### Q3 — coletânea (bank Q21)
> *"No artigo do CoUrb o senhor é segundo autor. O que exatamente foi contribuição sua — e de quem é o
> código que rodou aqueles experimentos?"*

**Tests:** individual contribution, the concern this format obliges a committee to raise.
**A strong answer contains:** the specific contribution, the norms basis, and a clean line between the
candidate's work and the first author's.
**What the text supports — well, in four places now.** p. 16 and p. 43: Tarik S. Paiva is first author;
the candidate is second author, contributed the MTLnet baseline the study builds on, and presented the
paper. That is specific and it is the right basis: the chapter's entire premise is a controlled
substitution into the candidate's own prior model. The code question, which v2 flagged as exposed, is now
partly answered in the document — Appendix A (p. 88) states that "The study of Chapter 4 stratified its
folds by sample rather than by user and ran in a separate repository". **Residual exposure:** the same
appendix's opening still scopes the platform to "the experiments of Chapters 3 and 5", so the reader must
join two paragraphs to get the answer. The honest answer aloud is "his code in his repository, my
baseline model, my presentation" — say it, do not let it be assembled.

---

### Q4 — coletânea (bank Q22)
> *"A Tabela 5 e a Tabela 8 dão números diferentes para a Flórida, o Texas e a Califórnia. O Apêndice B.4
> explica a Flórida. E os outros dois estados?"*

**Tests:** cross-chapter number discipline — the classic examiner trap, and what decides whether I trust
the other tables.
**A strong answer contains:** the mechanism (category-mapping widening between two extractions of the same
public dump), the fact that the earlier check-in set is a strict subset of the current one, and an
immediate concession that the appendix under-covers.
**What the text supports — partially; this is a live hit, unchanged from v2.** B.4 (pp. 93–94) gives an
excellent account for Florida including the controlled comparison ("each of its POIs, users, and
check-ins reappears in the current extraction"). The same mechanism plainly covers Texas and California,
but the appendix names neither. Concede the coverage gap in the first sentence and name the mechanism;
do not defend the omission. See SUG-6.

---

### Q5 — coletânea (bank Q23)
> *"A Conclusão Geral afirma algo que nenhum dos três artigos afirma sozinho? Ou é um resumo?"*

**Tests:** whether the frame argues at thesis level.
**A strong answer contains:** a claim that exists only at the collection level, and evidence generated
*for* the collection.
**What the text supports — fully, and this is the strongest move in the frame.** §6.2 (p. 77) reports a
capacity-matched dedicated baseline "run after the Chapter 5 manuscript was submitted and reported here as
a frame-level analysis": a dedicated category model widened to the joint model's parameter budget reaches
56.16 macro-F1 at Alabama against 56.82 at its own tuned width and 64.51 for the joint model, with
California repeating the pattern (69.88 ± 0.26 against 70.60 ± 0.07). I traced every figure to
`docs/results/closing_data/capacity_matched_stl_cat/capacity_matched_summary.json` and they reproduce
exactly, including the 101.9 percent parameter ratio at hidden dimension 752 and the 4,207,399-vs-644,359
parameter audit behind "about 4.2 million against 0.6 million". The Conclusão Geral therefore closes an
explanation — "the joint model just has more parameters" — that no individual paper closes. **That is what
a Conclusão Geral is for, and few coletâneas manage it.**
**One caution the candidate should know before standing up:** the sentence that introduces this control is
the one broken by BLOCKER-1. If I had read only page 77 and not the source, my first question about the
strongest evidence in the frame would have been "why does this sentence start mid-clause?".

---

### Q6 — the static-task circularity
> *"Nos Capítulos 3 e 4, a matriz de atributos dos nós é o one-hot da categoria do POI, e a tarefa
> estática prediz essa mesma categoria. O que exatamente está sendo medido nas Tabelas 2 e 6?"*

**Tests:** whether the candidate understands what his first two chapters measured. I ask this to find out
how well he knows work he did two years ago and did not do alone.
**A strong answer contains:** an immediate concession — for the *static* task the target's own category is
present, one-hot, in the input from which that POI is embedded, so those absolute values measure how much
of an injected label survives graph convolution rather than inductive category inference; then the correct
scoping — the chapters' *conclusions* compare an MTL arm against a single-task arm under an identical
representation, so the comparison stands while the absolute numbers do not travel; and finally the
observation that this is one more reason the arc moved to a sequential pair, where the target's features
lie outside the window.
**What the text supports — nothing.** p. 32 states the node features; p. 33 defines the static task as
pairs "(e, c), where c is the POI's ground-truth category to be predicted"; no sentence in 102 pages
connects them. Chapter 5 says the analogous sentence about its own representation — "That bounds the
training signal and not the inputs, since each visit's own category enters as a node feature" (p. 66) —
but the frame never carries it back to where the static task lives and where the exposure is largest.
Chapter 4's "average gains per state are 20.2 to 22.0 percentage points" (p. 54) are the largest numbers
in the document and sit on exactly this construction, unqualified.
**The candidate is fully exposed and must not improvise.** Published status does not immunize the
chapters; the Normas let this banca require changes in *forma, linguagem e conteúdo* even for published
articles. If the answer is "we never separated that", say it — an honest "isso a pesquisa não explorou"
costs far less than a constructed defence. See SUG-7.

---

### Q7 — the leakage kill-shot (bank Q8)
> *"O senhor escreve que a auditoria 'limita o canal em vez de fechá-lo'. Então diga-me o que ficou fora
> do limite. E por que devo aceitar uma sonda linear, rodada em um único estado, em uma inicialização,
> sobre versões anteriores da representação — quando o próprio parágrafo diz que uma sonda linear já
> deixou passar um vazamento?"*

**Tests:** the deepest exposure in the document, and whether the candidate can hold the line at the
boundary of his own evidence instead of retreating to "we audited it".
**A strong answer contains four parts.** (i) Name the unbounded channels: visits to places unseen in
training (the transductive measurement "covers the visits whose places appear in training (67 to 87
percent)", p. 66, so 13 to 33 percent is outside it); the nonlinear and multi-step forward-edge channel,
which the record shows the linear screen cannot see; and the five datasets other than Florida where the
forward-edge probe never ran. (ii) Why the linear screen was the right instrument anyway: it is a
*disqualifier*, and it disqualified — the attention-based encoder at 0.4976/0.4863 against a 0.4090
reference was thrown out on this evidence. (iii) The symmetry argument: if the channel is open it is open
identically for the joint and dedicated arms, which share the representation, so it inflates absolute
scores and not the MTL-versus-STL difference that carries every claim in the chapter. (iv) The concession
that cannot be argued: Table 9's place-level-versus-check-in-level comparison is *not* protected by that
symmetry, because the two arms use different representations with different exposure — the +27.63 to
+39.62 gap is the number most at risk, not the +5.33 to +9.35 one.
**What the text supports — (i) and (ii) well; (iii) and (iv) not at all.** p. 66–67 is unusually candid
and I traced its numbers: the four screen decimals reproduce to four places against
`leak_sniff_fl.csv` and `leak_sniff_resln_fl.csv`; the three limits (linear probe, Florida at one
initialization, ancestor builds) are printed; the region-transition prior's 13-to-27-point inflation is
disclosed along with the fact that it is built per fold and used only by the HMT-GRN baseline; and the
transductive figures (region −0.33 to +0.01, category 0.00 to +0.29) reproduce against
`docs/studies/pre_freeze_gates/A4_RESULTS.md §5.2`. But the chapter never argues the symmetry defence and
never distinguishes which of its two headline gaps the audit protects.
**This is the question I would spend longest on, and the candidate must be able to say (iii) and (iv)
aloud.** Two further things he should know and the text does not say: `A4_RESULTS.md` carries a
run-variance caveat the chapter does not — a 2026-06-26 Alabama re-run moved the category figure from
+0.29 to +0.88 pp, so the transductive decimals are one traceable draw and should not be defended as
exact (the sign/magnitude verdict holds across runs, and that is the defensible claim); and if I press on
"every encoder screened", the document contradicts itself — see Q8.

---

### Q8 — the contradiction between Chapter 5 and Appendix D
> *"A página 66 diz que TODO codificador avaliado fica acima do label-history benchmark. A página 99 nomeia
> um que não fica, com 0,3328 contra 0,3617. Qual das duas páginas devo acreditar, e por que as duas estão
> no mesmo documento?"*

**Tests:** whether the candidate knows his own audit, and how he behaves when caught in a contradiction he
did not choose to disclose.
**A strong answer contains:** the immediate concession that Appendix D is correct and Chapter 5's "every"
is too strong; the identification of the exception (a relation-typed graph encoder, 0.3328 standardized /
0.4142 raw); and then the recovery, which is genuinely available — that encoder is the one that passed the
linear screen and later leaked under a downstream sequence model, so it is the *illustration* of the
chapter's own point that the linear form is a screen and not a proof, not a counterexample to the audit;
and finally that the screen's verdicts are relative to the clean reference with a three-point margin, so
the benchmark enters no verdict's arithmetic and the disqualification of the attention encoder (8.9 points
clear of the reference) is unaffected.
**What the text supports — the recovery, in Appendix D, but not the concession.** Appendix D (p. 99) makes
the whole argument correctly and even labels the two readings, "The screening comparison is unaffected"
and "The absolute reading is the weaker one". Chapter 5 (p. 66) states the false universal. I verified the
exception against `leak_sniff_fl.csv` and confirmed seven of eight encoders clear the benchmark on both
runs while `check2hgi_rgcn` clears it on the raw run only.
**The right behaviour here is concession in the first sentence.** The candidate should not defend "every";
the sentence he wants is the one Appendix D already wrote for him. See BLOCKER-2.

---

### Q9 — statistics (bank Q10)
> *"Vinte modelos ajustados, mas o teste pareia quatro médias. Então o n é quatro, sobre uma única
> partição fixa. Isso sustenta 'supera' em seis conjuntos de dados com correção de Holm?"*

**Tests:** whether the candidate knows what his own inferential unit is, and can defend a
three-degrees-of-freedom test.
**A strong answer contains:** the arithmetic plainly (4 seeds × 5 folds = 20 fitted models; the test pairs
the four per-seed means, n=4, 3 df); why the paired *t* carries the verdict (at four seeds the exact
one-sided Wilcoxon floors at 0.0625 and cannot reach significance whatever the effect); that the
registered Wilcoxon is reported alongside and agrees, with all 20 folds favouring the joint model at every
dataset; the effect-size argument (gains of 5.33 to 9.35 macro-F1 against cross-seed standard deviations
of 0.01 to 0.10); and the honest limit, that one fixed partition means the intervals do not cover
uncertainty over resampled user splits.
**What the text supports — all of it, unprompted.** p. 67 states the departure from the registered test
and why, and volunteers that the plan "assigned the tests per task, not per dataset, and did not cover
next-region superiority, so the four next-region gains of Section 5.6.2 are secondary results outside
it" — a scope concession most authors would omit. p. 17 volunteers the fixed-partition limit. p. 71 gives
the fold-level agreement. I checked for the banned phrasing "twenty repetitions" and it appears nowhere;
"a seed is one complete repetition of the five-fold experiment" is stated at p. 67, matching
`GLOSSARY.md`. **Pass, and better than most published work in this area.** The residual concession to
offer rather than await: with a fixed partition, fold-composition luck is a systematic rather than a
sampled component of every reported interval.

---

### Q10 — the mechanism, and the withheld attribution (bank Q5, Q12)
> *"Com o caminho da região congelado, o ganho de categoria sobrevive inteiro — então não há transferência
> entre tarefas. E o senhor se recusa a nomear o tronco compartilhado como a fonte. Então em que sentido
> esta dissertação mostra que 'aprendizado multitarefa ajuda' — e por que a ablação que existe não serve?"*

**Tests:** whether the candidate's framing survives his own best control, and whether he can defend a
*refusal to attribute* — which is harder than defending an attribution.
**A strong answer contains:** no retreat. The distinction between *multi-task learning helps* and *task B
teaches task A* — the dissertation demonstrates the first and explicitly refutes the second for the
category half; only the first was ever the research question. Then the positive content: the region half
is genuine joint benefit (+2.10 to +2.20 Acc@10 at Texas and California, outside the two-point margin,
from a model whose category loss is co-trained), the capacity-matched control rules out parameters alone,
and the operational claim is unaffected by mechanism. Then the ablation answer, which is the new part:
the cross-attention ablation moved category macro-F1 by −0.04 ± 0.13, which a paired test cannot separate
from zero, but it does **not** license "the trunk contributes nothing", for two reasons the candidate must
be able to state — it ran on an earlier configuration whose region head was driven by a transition prior
the shipped models do not use, and the development record that produced it reads the null as a
compensation effect (the category stream absorbing what the shared stack would otherwise supply) rather
than as an absent contribution. Therefore: the gain is attributed to the joint architecture, and no named
component of it.
**What the text supports — all of it, and this is where the round improved most.** p. 72: "We therefore
report the negative result, that the gain is not cross-task transfer, as a finding, and we attribute the
gain to the joint architecture rather than to any named component of it", followed by the explicit list of
what freezing does not remove ("the category stream's own encoder, the per-stream feed-forward blocks, or
the added depth"). pp. 72–73 then state both limits on the ablation and conclude "we therefore do not name
the shared trunk as the source, and we do not present the ablation as evidence against it either."
§6.2 (p. 77) repeats it. I traced the freeze control to
`docs/studies/closing_data/archive/findings/W6_ENCODER_ISOLATION.md`: 63.50, 63.67 and 79.79 macro-F1
with deltas +7.63, +6.54 and +4.64 reproduce exactly, as does the single-initialization n=5 footing the
chapter discloses. I also read the ablation's own record,
`docs/findings/archive/F50/F50_T1_5_CROSSATTN_ABSORPTION.md`: it calls its own null "misleading" and a
"hidden compensation effect" at line 229, and confirms the different engine and batch size. **The
chapter's characterization of its own source record is accurate.** Refusing to bank an ablation that ran
in your favour, and saying why in the text, is the behaviour that most raises my confidence in the rest.
**Where I would still press:** the abstract and title read as a multi-task-learning result, and a reader
who stops at p. 5 will not learn that the larger half of the headline is an architecture effect. That is
not dishonest — §6.2 says it plainly — but the candidate should defend the framing deliberately rather
than discover the tension at the table. The defensible line: "helps" in the title's sense is carried by
the joint architecture; for the category task the mechanism is a stronger shared trunk, which is a weaker
and more interesting claim than transfer.

---

### Q11 — coletânea (bank Q24), and the removed appendix
> *"Que tentativas fracassadas ficaram de fora desta coletânea, e por que devo confiar que a exclusão não
> foi conveniente?"*

**Tests:** whether the negative record is complete or curated. In v2 the document answered this itself.
It no longer does, and this is the direct cost of removing Appendix A.2.
**A strong answer contains:** no defensiveness and no volunteering of things nobody asked about. The
frame: the dissertation's evidence base is three studies, two published and one submitted, and the
negative results *inside* that base are reported rather than dropped — a published null in Chapter 3, a
freeze control that refutes the tidiest reading of the headline in Chapter 5, an ablation that is declined
as evidence in both directions, a class-weighting variant that lowered both metrics, a set of gradient
balancers that did not beat a tuned fixed weighting, and a cascade rewiring reported as a tie rather than
a win. Then, if pressed on submissions rather than experiments: there was an intermediate manuscript that
was rejected and not included; it is not a published, accepted or submitted article, so it is not eligible
as a chapter; its material was absorbed into the Chapter 5 study; and — the part that must be said if the
subject is opened at all — its central claim about a multi-task cost on region prediction did not survive,
so no result of it is cited anywhere in this dissertation.
**What the text supports — the first half strongly, the second half not at all.** The in-base negative
record is genuinely there and I would credit it aloud: p. 61 (balancers did not help, with the gradient
cosine of +0.001 and its measurement scope named), p. 64 (class weighting lowered both), p. 72 (the freeze
control against the author's own interest), pp. 72–73 (the ablation declined in both directions), p. 74
(the cascade read as "a defense of the parallel design, not a claim that we outperform the cascade").
On the second half the document is now silent by design: no "earlier iteration", no "unpublished", no
rejection date, and the BRACIS acronym appears nowhere including the abbreviations list. I verified the
removal is complete and leaves nothing dangling (§2.1).
**My reading, for the candidate's calibration:** the silence is defensible and I would not attack it. But
the candidate no longer has a page to point at, so the answer has to be fluent, brief, and volunteered
without prompting *if and only if* the subject is raised. The failure mode to avoid is a hesitation that
looks like something is being withheld — the substance here is entirely benign, and a crisp two-sentence
answer closes it. Rehearse it.

---

### Q12 — data governance and the model as an exposure (bank Q18)
> *"O Apêndice E é sólido sobre os dados de treino. Mas o senhor não diz nada sobre o modelo. Um artefato
> que ordena dez setores censitários para a próxima visita de um usuário é, ele mesmo, uma superfície de
> inferência — e o protocolo user-disjoint existe justamente para afirmar que ele generaliza para usuários
> nunca vistos. Onde está essa consideração?"*

**Tests:** whether the ethics statement is a boundary or a beginning — and this is the harder follow-up
that the new appendix invites, which is the correct outcome for a good appendix.
**A strong answer contains:** the concession that Appendix E scopes to provenance, handling and the
human-subjects question, and does not treat the trained artifact; then the substance, in the candidate's
own voice — that the model's outputs are the forward-looking exposure, that the user-disjoint protocol is
precisely a claim about generalization to unseen users, that a top-ten region shortlist at
neighbourhood granularity is a meaningfully informative prediction (the shipped model reaches 65.69
percent at California over 8,501 regions, and §5.7 already notes the shortlist lies a median 3 to 8 km
from its centroid), and that this is a property of deployment rather than of the published measurements;
and then the mitigations that would belong in a deployment setting, named without overclaiming that this
work implemented them — aggregation before use, no per-user retention, and the coarsening the appendix
explains it deliberately did not apply because it would change the measured quantity.
**What the text supports — the ground, not the conclusion.** E.2 (p. 102) comes close: it cites the
mobility survey for the point that "models trained on mobility data raise privacy questions during
training as well as at prediction time, because the portions of information a model absorbs cannot be
controlled directly", and it states that public availability "settles who may hold the files, not what
can be inferred from them." Both sentences point at the model. Neither draws the consequence for *this*
model, and §6.3's six limitations carry no ethics or deployment-risk item. The candidate has the material
and must supply the last step himself.
**A second, smaller thing I would ask, and the text answers it honestly:** whether the program requires a
formal ethics determination for secondary analysis of public data. E.3 records the author's position, its
basis, that no approval or exemption is claimed, and that a determination "belongs on file before deposit"
if required. **Have the secretariat's answer before the defense**, because the appendix promises to name
it. That is an administrative item, not a scientific one, and it is exactly the kind of thing a banca
resolves in thirty seconds when the candidate has already asked.

---

## 6 · Questions the candidate must be able to answer aloud

These have no adequate answer in the document. Some are beyond a written text's scope; each will be asked.

1. **What do Tables 2 and 6 measure, given that the target's category is a node input feature?** (Q6.
   Nothing in 102 pages addresses this. The largest numbers in the document sit on it.)
2. **Does the leak channel, if open, threaten the MTL-versus-STL comparison or only the absolute scores —
   and does that protection extend to Table 9's place-level comparison?** (Q7 (iii)–(iv). The symmetry
   argument is the candidate's strongest defence and it is nowhere in the document; the Table 9 exception
   must be volunteered, not conceded under pressure.)
3. **Which page do I believe about the label-history benchmark, 66 or 99?** (Q8. Concede in the first
   sentence; the recovery is already written in Appendix D.)
4. **What failed attempts were left out of the collection, and why is the exclusion not convenient?**
   (Q11. Until this round the document answered this itself. Two sentences, rehearsed.)
5. **What are the privacy implications of the trained model, as opposed to the training data?** (Q12.
   Appendix E supplies every premise and none of the conclusion.)
6. **In what sense does the dissertation show that multi-task learning helps, given the freeze control —
   and why is the cross-attention ablation not evidence that the trunk is idle?** (Q10. §6.2 and pp. 72–73
   answer both in the text; the candidate needs the distinction between *joint training helps* and *task B
   teaches task A* at his fingertips, and the compensation-effect reading of the ablation's own record.)
7. **Whose code ran the Chapter 4 experiments, and does the Appendix A platform claim cover them?** (Q3.
   Now nearly answered on p. 88; say it in one sentence instead of letting it be assembled.)
8. **Why do Texas and California counts differ between chapters when B.4 discusses only Florida?** (Q4.)
9. **Is the Arizona category gain of +9.35 stable, given the screened arms at about 57.0?** (SUG-4. The
   abstract's upper endpoint depends on the answer; the estimator argument is on the author's side, so
   answer with the rule, not with a hedge.)
10. **Was the swept "category F1" of p. 20 macro-averaged or weighted?** (MINOR-2. A one-word answer, and
    the wrong one in front of a committee is expensive.)
11. **Has the program been asked whether a formal ethics determination is required?** (Q12 tail. Appendix E
    promises to name it if so.)
12. **By how much does epoch-on-the-scored-fold selection inflate the absolute numbers?** (p. 75 makes the
    argument and declines the magnitude. The honest answer is "unmeasured, and a held-out third split is
    the experiment that would measure it" — say the second half.)

---

## 7 · What impressed me (do not edit this away)

Recorded because a correction round is exactly when good things get flattened. Items carried over from v2
are marked; they survived this round intact and should survive the next one.

- **The withheld attribution, pp. 72–73 — new this round and the best single change in it.** The
  dissertation had an ablation that pointed its way, and it declines to use it: "we therefore do not name
  the shared trunk as the source, and we do not present the ablation as evidence against it either",
  with both reasons stated (a different configuration, and the source record's own reading of the null as
  a compensation effect). I read that record. It does call its own null "misleading" and a "hidden
  compensation effect", and the chapter represents it accurately. **Declining to bank a convenient null,
  in print, with the inconvenient reading of your own internal record quoted back, is the rarest thing in
  this document.** It is also exactly what makes Q10 a conversation rather than an interrogation.
- **Appendix E's refusal to overclaim its own licence.** "The dedication was applied by the depositor of
  this copy, identified there by a single name, and not by the party that collected the data… that Gowalla
  data as such is in the public domain is a broader claim, and nothing that could be opened supports it."
  An appendix that distinguishes the copy from the corpus, and prints the one check it did not complete,
  is doing more than compliance.
- **The label-history rename, and Appendix D's reason for it.** "Calling it a ceiling, as the internal
  screening record does, would assert more than the measurement supports" (p. 100). The document renamed a
  quantity *against its own rhetorical interest* — "ceiling" sounds stronger — and then explained why in
  one sentence. The word is now used only for the dedicated single-task model, which is a real trained
  model's score; I checked every remaining occurrence. Appendix D also states the coverage limits (Texas
  absent and why; Istanbul's 196 multi-category places with the strict variant's 0.3009 against the
  table's 0.3016), and every cell of Table 16 reproduces exactly against
  `autocorrelation_ceiling.json`.
- **The time-capsule prefaces** (carried from v2). pp. 27, 43, 58. Each names venue, status, and precisely
  which of its own conclusions later chapters revise. Chapter 4's now also carries the split-protocol
  weakness and the single-seed disclosure. Keep every word.
- **§6.2's capacity-matched control** (carried from v2). Frame-level evidence generated *for* the
  dissertation, closing an explanation no individual paper closes, reported with its own scope limits, and
  now with the interim-reading correction folded in (the partial California read that suggested a larger
  magnitude is superseded, and the text reports the completed sweep's smaller shortfall). Fix its topic
  sentence; do not touch its content.
- **The refusal sentences** (carried from v2, and there are more of them now). "It does not follow that the
  bias cancels exactly" (p. 75). "The measurement bounds this channel rather than closing it" (p. 67). "We
  read this as a defense of the parallel design, not a claim that we outperform the cascade" (p. 74). "This
  remains motivation, not a measured service result" (p. 74). "It is not an upper bound on what a model may
  score" (p. 66). "It records no approval and no exemption, because none was sought and none is claimed"
  (p. 102). Each declines a claim the reader would have granted.
- **The Markov-floor paragraph as rewritten, p. 73.** The chapter reports that its own protocol-matched
  floor sits above three published external systems, and instead of explaining that away it states two
  facts about how the numbers were produced (stride-1 windows make the last-visit region a strong
  predictor, with 22.4 percent of Alabama windows containing their own target region as a genuine revisit;
  and the three systems do not meet the floor on equal terms), then explicitly declines the causal step:
  "Neither fact establishes why the floor lies above the three systems, and we do not claim a single
  explanation." It then names the floor rather than the externals as the reference the region task must
  clear — the more conservative choice. I recomputed the floor's span from
  `MARKOV_FLOOR_STRIDE1.md`: the chapter's "51 to 72 Acc@10" and "exceeds it by 4.9 to 10.3 points" come
  out at 51.2–72.5 and 4.95–10.38. **A protocol asymmetry honestly stated beats a causal story cleanly
  told, and the change of register here is the right one.**
- **Every headline number traced, again.** Table 10's twelve joint and dedicated cells against
  `joint_best/JOINT_BEST_RESULTS.md` (including the joint-best convention and the ≤0.06/≤0.11 robustness
  figures); the ceilings against `CEILINGS_N20_FINAL.md`; the capacity control against
  `capacity_matched_summary.json`; the freeze control against `W6_ENCODER_ISOLATION.md`; the four screen
  decimals against `leak_sniff_fl.csv` / `leak_sniff_resln_fl.csv`; Table 16 against
  `autocorrelation_ceiling.json`; the transductive figures against `A4_RESULTS.md`; the Markov floor
  against `MARKOV_FLOOR_STRIDE1.md`. **Not one headline number failed its trace.** The two obrigatórias
  above are a missing word and a quantifier — not a number.

---

## 8 · Scope note

Per the persona's hard limits, this review does not judge UFV formatting minutiae (persona 13) and does not
copyedit (persona 02); MINOR-1 and MINOR-2 are listed only because v2 listed them and the author asked for
closure accounting.

Out-of-scope handoffs, one line each. **Persona 13** — the approval-sheet placeholder on p. 2 must be
replaced before deposit, and Appendix E's closing sentence implies an item for the secretariat (a formal
ethics determination, if the program requires one). **Persona 06** — SUG-2 and SUG-3 are number/count
defects inside Appendix B; MINOR-2's averaging convention is still an open number-gate item. **Persona 05**
— the bibliography now ships 98 of 99 entries with the single absentee declared, which closes v2's
citation-integrity handoff. **Persona 09** — Q7 (iii)–(iv) and the `A4_RESULTS.md` run-variance caveat are
statistics items the chapter does not carry. **Whoever owns `src_utils/check.sh`** — the trapped-prose
checker returns exit 0 on a document containing instance nine of the bug it was written to catch; the
threshold at `check_trapped_prose.py:64` is the cause, and the fix belongs with BLOCKER-1.

*Read-only review. No file in the dissertation was modified. Findings are proposals; the author rules.*


---

<!-- estado-rodada -->
> **Rodada encerrada · último toque 2026-07-27 · sem autoridade.**
> Este ficheiro é registo de proveniência do que foi discutido nesta passagem, não fonte
> de um facto corrente. O que ficou decidido está em [`VEREDITOS.md`](../../../VEREDITOS.md);
> os valores entregues estão em `CLAUDE.md` §0.1. Não copie nada daqui sem confirmar lá.
