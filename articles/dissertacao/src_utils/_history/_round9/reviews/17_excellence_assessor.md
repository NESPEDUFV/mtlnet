# Review — 17 · Excellence assessor (gap-to-outstanding)

- **Persona:** `reviewers/17_excellence_assessor.md` (strategy persona; scores against the
  positive descriptors of `reviewers/research/dissertation_excellence_2026-07-20.md` §ACTIONABLE_RUBRIC
  and screens §ANTI_PATTERNS).
- **Build commit:** `901a0408`
- **Date:** 2026-07-30 (started 11:41 UTC, report written at the 30-minute checkpoint).
- **Scope given:** the whole 102-page defense build at the level of ARGUMENT AND ARC, not
  line-level prose. Frame chapters closely; paper chapters for claims and conclusions only.
- **What I actually read** (nothing in this report comes from memory):
  - `src/build/main.pdf` — pages **3, 4, 5, 6, 7, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22,
    23, 24, 25, 26, 27, 28, 43, 44, 58, 59, 70, 71, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 86,
    87, 88, 90, 91, 92, 101** (text extracted, not skimmed on screen).
  - Source, comment-stripped where quoted: `src/chapters/1_introduction.tex`,
    `src/chapters/6_conclusion.tex`, `src/chapters/2_fundamentals.tex`,
    `src/chapters/3_cbic.tex`, `src/chapters/apx_f_cosine.tex`,
    `src/chapters/apx_a_contributions.tex`, `src/chapters/apx_b_static_scope.tex`,
    `src/chapters/apx_d_ceiling.tex`, `src/chapters/5_mobiwac/07_discussion.tex`,
    `src/content.tex`, `src/main_extra.tex`.
  - Law/rubric: `AGENT_GUARDRAILS.md` §0–§4b, `WRITING_LAW.md` §1–§3 (headers of §4–§7),
    `GLOSSARY.md` §1–§4, `NORTH_STAR.md` §1–§6, `reviewers/README.md`,
    `reviewers/research/dissertation_excellence_2026-07-20.md` §ACTIONABLE_RUBRIC + §ANTI_PATTERNS.
- **Exact commands run** (working directory `/Users/vitor/Desktop/mestrado/ingred/articles/dissertacao`):
  ```
  git log -1 --format="%H %ad %s"
  python3 -c "import pypdfium2 as pdfium; pdf=pdfium.PdfDocument('src/build/main.pdf'); ..."   # per-page text -> r9x/pages.json
  wc -l src/chapters/*.tex src/content.tex
  sed -n '84,116p' reviewers/research/dissertation_excellence_2026-07-20.md
  sed -n '/^## 3/,/^## 4/p' WRITING_LAW.md
  grep -in "deploy" GLOSSARY.md
  grep -vn '^[[:space:]]*%' src/chapters/6_conclusion.tex | grep -nE '[0-9]+\.[0-9]'
  grep -vn '^[[:space:]]*%' src/chapters/apx_f_cosine.tex | sed -n '<F.3..F.4 window>'
  grep -n "deployable" src/chapters/*.tex src/content.tex
  grep -n "three candidate explanations\|task dissimilarity" src/chapters/6_conclusion.tex
  grep -n "supplied on request" src/chapters/apx_a_contributions.tex
  grep -n "caption" src/chapters/{1_introduction,2_fundamentals,6_conclusion}.tex   # rc=1, NO output
  grep -vn '^[[:space:]]*%' src/chapters/{1_introduction,2_fundamentals,6_conclusion}.tex | grep -n 'input{tables'
  ls src/chapters/tables/frame/
  ```
  No build, no `make check`, no `make selftest` (instructed; another agent holds this checkout).
  Greps over `.tex` strip comment lines first (AGENT_GUARDRAILS V4).

  **Disclosure:** I edited no source, tracker, or gate. But I did not write *only* this report: the
  PDF-extraction step above wrote scratch text dumps to an untracked `articles/dissertacao/r9x/`
  (`pages.json` and four page-range extracts). I requested their deletion at the end of the session;
  if `r9x/` is still present, it is mine and safe to remove. Nothing tracked was modified — verified
  with `git status --porcelain`, whose only entry under `articles/dissertacao/src_utils/_history/_round9/`
  attributable to me is this report file.

---

## 1 · The scorecard

Ten rubric dimensions, scored BELOW / GOOD / OUTSTANDING against the positive descriptors
(not by counting defects — §ANTI_PATTERNS 12).

| # | Dimension | Score | Evidence line (location I opened) |
|---|---|---|---|
| 1 | Problem framing & significance | **GOOD** | One quotable question, bold and inline, PDF p.13 §1.2. Why-it-matters beyond the lab is one sentence, p.12: urban planning, disease spreading, pollution, cited to [3]. The concrete service argument exists but sits in Ch.5, p.76, hedged as "motivation, not a measured service result". |
| 2 | Contribution clarity & unity (coletânea-critical) | **GOOD, near OUTSTANDING** | The arc paragraph, p.13–14, states a claim no single paper makes; the Ch.3 preface, p.28, names exactly what each later chapter changes ("Chapter 4 keeps this architecture and replaces the input representation … Chapter 5 then changes the architecture as well"). What is missing is the artifact the rubric names: no table maps study -> configuration -> task pair -> protocol -> verdict. See finding 5. |
| 3 | Command & critical use of literature (the chapter-2 test) | **OUTSTANDING** | §2.3 takes positions rather than cataloguing: p.23 states the guarantee level of each balancer and then "This dissertation therefore claims no Pareto property of any kind for its models"; p.24 "a fixed-weight baseline is a serious competitor, and a balancer earns its place only by outperforming it". §2.1 p.18 ends a lineage paragraph with "every model named in this paragraph predicts the exact next place", and §2.2 p.19 discloses that HGI was repurposed and retuned rather than taken as published. Gaps map 1:1 onto the three questions, p.26–27. |
| 4 | Methodological rigor & justification | **GOOD** | Protocol justified before results (§2.4 p.25: user-disjoint splitting motivated by the leakage it prevents); the parallel-versus-cascade choice is defended against the published alternative and then actually tested, p.75. Against that: the frame's own diagnosis leg is not width-matched and says so, p.78. |
| 5 | Statistical & empirical rigor | **OUTSTANDING** | p.16 downgrades its own generality unprompted: "All four seeds reuse the same fold partition, so the reported intervals do not cover uncertainty over resampled user splits." p.76: "every absolute score reported here is optimistic … The residual therefore favors the comparator … It does not follow that the bias cancels exactly." Verbs bound to tests throughout (p.26). |
| 6 | Originality & insight | **GOOD** | The reframing exists and is named ("The representation, together with the sharing topology built on it, is what the answer depends on", p.79), but the document's single most reframing measurement — the controlled place-level versus check-in-level contrast, +27.63 to +39.62 macro-F1, Table 9 p.71 — never reaches the frame. The frame argues representation dominance with the CoUrb number instead, which its own paragraph then qualifies twice. See finding 2. |
| 7 | Critical self-assessment & honest negatives | **OUTSTANDING** | p.78 retracts, in the author's own disfavour, the evidentiary weight of the number the arc leans on. p.79 refuses an available attribution: "The control does not say which part … we do not offer the ablation as evidence that the trunk contributes nothing." Limitation 6, p.81, concedes a confound most candidates would leave unsaid. |
| 8 | Reproducibility & artifacts | **GOOD** | Appendix A §A.2, p.91, names files, the partition seed 42, the four initializations 0/1/7/100, and the scripts per protocol step — this is the shape the rubric asks for. One seam short of outstanding: p.91 "the statistical scripts and their output files … are supplied on request". |
| 9 | Writing, structure, voice | **OUTSTANDING** (at arc level; sentences are other personas' scope) | The spine is visible from the chapter openers alone (p.17 lists §2.1–§2.5 as a route, not a summary), and the register holds across a translated chapter and two re-typeset ones. |
| 10 | External validation & impact trail | **GOOD** | Venue/status/DOI per chapter, p.15, with the CoUrb ownership note spelled out ("this author is the second author, contributed the MTLnet baseline … and presented the paper") — this closes anti-pattern 2 cleanly. Products are real but scattered across p.15, p.16 and p.90; no consolidated list. |

### The two cross-cutting tests

**The chapter-2 test — PASSED, and it is the document's strongest chapter.** Authority is
established by p.23–24: a reader who knows this literature meets a chapter that states what each
method guarantees, at what strength, and then declines the claim it could have made. The negative
space is handled too (p.24: "no multi-task model among them predicts the next region as a co-equal
end target alongside the next category"), which is what turns coverage into a gap.

**The intro-conclusion loop test — PASSED with one loose end.** The four objectives of p.14 are
answered in order at p.78–79, and §6.2 answers the p.13 question in the p.13 words. The loose end:
p.78 announces that Chapter 3's *three* candidate explanations are what "the rest of the
dissertation put to the test", and the report closes two of them. Finding 3.

---

## 2 · Findings

### SHOULD-FIX — Appendix F §F.3 explains Chapter 3's null with a measurement §F.4 forbids transferring there

**WHERE:** `src/chapters/apx_f_cosine.tex:294-299` (rendered PDF **p.101**), read against
`src/chapters/apx_f_cosine.tex:329-338` (PDF p.101–102).

**WHAT:** §F.3, second consequence, verbatim:

> "The second is about the arc of the three studies. The investigation opened on the hypothesis that
> the sharing scheme limited joint training, and the first study's null result was read that way at
> the time. Had the tasks been in conflict, a better sharing scheme or a better balancer would have
> been the remedy. They were not, so the limit lay elsewhere, and the second and third studies
> located it in the input representation. There was little interference to fix, and therefore little
> for a change of architecture to recover."

§F.4, two paragraphs later, verbatim:

> "Every run measured here uses one architecture family, the cross-attention joint model of
> Chapter 5. … Nothing here says the gradients stay orthogonal in a model that shares more of its
> depth, couples the tasks in a cascade, or shares an output layer. … Equivalence there makes
> orthogonality the task pair's property; otherwise it belongs to this architecture, and
> Section F.3 applies only to models shaped like this one."

**WHY:** the two sections are in scope conflict, and the conflict runs the wrong way for the
argument. The cosine was measured on the Chapter 5 joint model and on the Chapter 5 task pair
(next category + next region). Chapter 3's null was produced by a different architecture (hard
parameter sharing on a place-level embedding, PDF p.28) *and* a different task pair (static
category classification + next category, PDF p.14, p.43). §F.3's "They were not [in conflict], so
the limit lay elsewhere" reads as a retrodiction about Chapter 3's model; §F.4 then names the
architecture as "the factor most likely to change the answer and the one this appendix did not
vary", and even attributes the orthogonality to *the task pair* — the pair Chapter 3 did not use.
This is a frame-level claim about what the arc shows, so AGENT_GUARDRAILS §3 C2 applies (such
claims need derivation from the registry plus sign-off), and WRITING_LAW §3's scope rule applies
("Scope every universal"). It also matters more than its page position suggests: §F.3 ¶2 is the
only place in 102 pages that offers a *mechanism* for the null result, so it is the paragraph a
committee will press.

**Why not a blocker:** no number is wrong, and the document contains its own correction — §F.4 is
present, honest, and two paragraphs away. The defect is that §F.3 states more than §F.4 permits.

**FIX:** rescope §F.3 ¶2 in place. Concretely: say that the measurement is taken on the final
configuration, that it therefore cannot speak directly to the Chapter 3 model, and offer it as
*consistent with* the arc's reading rather than as its explanation. The hedged version of exactly
this inference already exists at `src/chapters/2_fundamentals.tex:502` (PDF p.23: Appendix F "reads
that result as … **part of** the reason the argument moves to the input representation") — the
appendix should not be stronger than the chapter that summarizes it. Whether to keep the paragraph
at all is the author's call.

### SHOULD-FIX — the arc's middle leg is argued in the frame with the one number its own paragraph disqualifies, while the strongest representation evidence in the document stays inside Chapter 5

**WHERE:** `src/chapters/6_conclusion.tex:44-62` (PDF **p.78**); the unused evidence is Table 9,
PDF **p.71**.

**WHAT:** §6.1, Chapter 4 paragraph, verbatim:

> "…raised category macro-F1 by 20.2 to 22.0 percentage points across the three states tested. …
> Two qualifications bound what that number licenses. It is measured on the static task, which
> classifies a place from that place's own representation, and Appendix B of the supplementary
> volume … records that this task's input determines its target by construction, so the figure is
> not evidence about the sequential task. The comparison is also not width-matched … 192 dimensions
> against 64 … What carries that diagnosis is the direction and the size of the effect on the
> sequential task, where no such identity between input and target exists…"

**WHY:** this is honest and it is also self-defeating as delivered. The 20.2–22.0 figure is the
*only* number the frame gives for the diagnosis that the whole arc turns on; the same paragraph
then rules it out as evidence for the task the diagnosis is about, and hands the load to "the
direction and the size of the effect on the sequential task" — a magnitude the frame never quotes.
A reader who accepts both qualifications is left with the middle leg asserted and unquantified.
Meanwhile the document's most direct evidence for representation dominance is sitting in Chapter 5
and never surfaces above it: Table 9, p.71, next-category macro-F1 for the check-in-level
representation against the place embedding, "same single-task model, training configuration, and
folds", with gaps the text states as +27.63 (Arizona) to +39.62 (Florida) and Istanbul +28.09,
plus the two controls on p.70–71 that rule out contextualization alone and feature injection.
Rubric dimension 6 (a named finding that survives beyond the benchmark) and §ANTI_PATTERNS 11
(missed connections) both point here.

**FIX:** two quote-not-compute moves, no new experiment.
1. In §6.1's Chapter 4 paragraph, quote the *sequential*-task figure from that chapter's own
   results table (PDF p.57, "Average F1-Score (%) per model and state for the Next-POI Prediction
   task") with its convention, so the diagnosis carries a number that survives both
   qualifications. **I did not open that table cell-by-cell** (see UNFINISHED) — the values must be
   copied from it by whoever applies this, not from me.
2. In §6.2, name the Table 9 contrast as the arc's direct, controlled evidence for representation
   dominance, with its scope intact (one seed, fold sd, single-task model). Estimated cost 1–2
   hours; highest ratio of argument gained to pages added in this document.

### SHOULD-FIX — three candidate explanations are announced as the arc's agenda; the conclusion adjudicates two and never says the third is still open

**WHERE:** `src/chapters/6_conclusion.tex:37-39` (PDF **p.78**); the unclosed door is described at
PDF p.43; the near-miss is limitation 6, `src/chapters/6_conclusion.tex:301` (PDF p.81).

**WHAT:** §6.1, verbatim: "three candidate explanations, task dissimilarity, an input
representation too poor for both tasks at once, and the restrictiveness of hard sharing, that the
rest of the dissertation put to the test."

**WHY:** §6.2 then adjudicates the representation and the sharing topology. Task dissimilarity is
never adjudicated — and could not be, because the task pair *changed* rather than being held
constant and measured, which limitation 6 concedes for a different purpose ("the homogeneity of the
final pair remains a possible contributor to the size of the improvement"). The conclusion
therefore reports on two of the three things it said it would test, without telling the reader that
the third was overtaken by the design. This is precisely the intro-conclusion linkage examiners
check (§ANTI_PATTERNS 9: "not doing what one said one would do, or explaining how and why changes
were made"), and the fix converts an omission into a rubric-7 asset.

**FIX:** one sentence in §6.2 (or as a clause on limitation 6): name explanation 1 as untested by
design — the pair changed with the representation, so dissimilarity was never isolated — and point
to the fixed-pair ablation already listed in §6.4 as the experiment that would test it. About
15 minutes, and it is the cheapest single upgrade in this report.

### SHOULD-FIX — "one deployable model" is the frame's only inflation-shaped claim, it is unregistered vocabulary, and the document's own limitation 3 works against it

**WHERE:** `src/chapters/1_introduction.tex:295` (PDF **p.16**) and
`src/chapters/6_conclusion.tex:342` (PDF **p.81**).

**WHAT:** p.16: "Evidence that one **deployable** model can serve both prediction services at
once…". p.81: "The practical output of this dissertation is one **deployable** model whose single
forward pass answers two questions…".

**WHY:** three independent reasons, none of them about style.
1. Chapter 5 says the opposite about deployment evidence, p.76: "we do not build or evaluate a
   mobility-aware service; it is background motivation".
2. Limitation 3, p.80: "The check-in-level representation is trained on the check-in graph of each
   dataset; it does not embed unseen places or users without retraining." A representation that
   needs retraining for an unseen place is not deployable in the ordinary reading of the word, and
   §6.4 lists the inductive variant as future work precisely so that deployment becomes possible.
3. `GLOSSARY.md` has no `deployable` entry — I checked (`grep -in "deploy" GLOSSARY.md` returns
   nothing) — and the registry is fail-closed for prose.
   WRITING_LAW §3 (scope every universal; verbs bound to evidence) and §ANTI_PATTERNS 7
   (contribution inflation) close it.

**FIX:** use the operational claim the evidence actually licenses, which the document already
words well elsewhere (p.15 §1.4 single-model constraint; Figure 5 caption p.66 "One model, one
forward pass, two predictions"): "one trained model whose single forward pass returns both
predictions". Alternative, author's call: register `deployable` in the glossary with its scope
stated. My recommendation is the first — it costs two words and removes the only sentence in the
frame an examiner can call overselling.

### SHOULD-FIX (gap-report move, not a defect) — the coletânea's unifying artifact is missing: no consolidated cross-study evidence table

**WHERE:** absent. The nearest existing artifacts are Table 1 (lineage), PDF **p.21**, and the
prose arc at PDF p.13–14 and p.78–79.

*Instrument note (AGENT_GUARDRAILS V2/V3), because my first instrument was blind:* `grep -n
"caption" src/chapters/{1_introduction,2_fundamentals,6_conclusion}.tex` returns **rc=1, no output**
— not because the frame has no table, but because captions live in `\input`ed files, so that grep
could not have seen one. The claim below rests on two instruments that can: (a)
`grep -vn '^[[:space:]]*%' <the three frame chapters> | grep -n 'input{tables'` returns exactly one
line, `2_fundamentals.tex:336: \input{tables/frame/lineage}`; (b) the List of Tables, PDF **p.6**,
lists Table 1 as the lineage table and Table 2 at page 40, which is inside Chapter 3. Table 1 is
therefore the frame's only table.

**WHY:** rubric dimension 2's evidence line asks for "a contributions table mapping papers ->
thesis-level claims", and §ANTI_PATTERNS 1 (stapled compilation) is the most-cited failure mode of
this exact format. Everything a committee needs to see side by side is already in the document but
in five places: task pair per study (p.14), protocol strength per study (p.25 and p.90), what each
study changed (p.28 preface), and each verdict (p.78–79). A reader currently has to assemble the
comparison themselves — which is also the assembly a hostile examiner performs looking for
inconsistency.

**FIX:** one page in §6.1 or at the end of §2.5: rows = the three studies; columns = task pair /
input representation / sharing topology / split protocol / significance treatment / verdict, every
cell quoted from the locations above with its hedge. Nothing new is measured or claimed. Estimated
2–3 hours. This is my single highest-leverage remaining investment, because it simultaneously
serves dimensions 2, 5 and 10 and the CTD products test below.

### NIT — the reproducibility trail is one clause short of the rubric's outstanding bar

**WHERE:** `src/chapters/apx_a_contributions.tex:110` (PDF **p.91**).

**WHAT:** "the statistical scripts and their output files listed below are part of the working
repository and are supplied on request."

**WHY:** dimension 8 OUTSTANDING wants released code/configs/seeds/commands; §A.2 otherwise hits
that bar exactly (named scripts, partition seed 42, initializations 0/1/7/100, the file each output
lives in). "Supplied on request" gates the half of the trail that licenses the verbs. There is
already a `NEEDS SIGN-OFF` note on this at `apx_a_contributions.tex:146`, so the author has seen it.

**FIX:** author's call and possibly a release decision rather than a text decision. If the
statistical scripts can ship in the public snapshot, say so; if not, the current sentence is honest
and should stay as it is.

### NIT — objective 4 is an act of writing, not a research aim

**WHERE:** `src/chapters/1_introduction.tex:168-171` (PDF **p.14**).

**WHAT:** "Anchor the final answer to the research question in a user-disjoint statistical
protocol, the cross-validation with paired significance and non-inferiority testing of Chapter 5,
and consolidate the evidence of the three studies under it (Chapter 6)."

**WHY:** objectives 1–3 name investigations; objective 4 names the consolidation chapter. The 1:1
objectives-to-chapters mapping is the deliberate Viegas device (NORTH_STAR §6 Ch.1 beat 5), so this
is a defensible choice, not an error — but as worded it makes the fourth aim read as bookkeeping,
and a committee that reads the objectives as the contract will notice that one of the four is
satisfied by the existence of Chapter 6.

**FIX:** optional reframe to an evidentiary aim ("establish the standard of evidence under which
the answer to the research question may be stated, and state it"), or leave as is. Author's call.

---

## 3 · The award lens — could this compete at SBC CTD?

**Yes, with three named edits.** Judged as a quality instrument only; whether to submit is the
author's decision and out of scope.

(a) **Can the problem -> contributions -> impact story be told in ten pages?** Yes, and most of it
is already written: PDF p.13–14 tells the three-beat arc in roughly one page, p.16 gives the
four-way contribution taxonomy, p.78–79 gives the consolidated answer with its controls. A CTD
summary would be an extraction, not a new composition.

(b) **Is the products list where a committee finds it?** No. The products exist and are real —
two DOIs plus one submission at p.15, software at p.16 and Appendix A p.90 (a 192-module,
28,644-line platform, an ETL producing fifty-six state-level datasets, twenty-one balancing
methods, thirteen backbones, quoted from p.90), the six-dataset benchmark at p.16 — but a reader
must visit three places to assemble them. **Edit:** a short products subsection in Appendix A, or
the consolidated table of finding 5 extended with a products row.

(c) **Are originality and relevance (the double-weighted axes) argued explicitly or only implied?**
Originality: argued, at p.16 (Theoretical) and p.79 ("The representation, together with the
sharing topology built on it, is what the answer depends on"). Relevance beyond the lab: **only
implied.** The frame spends one sentence on societal stakes (p.12, cited to [3]), while the
document's one concrete service argument is buried at p.76 — ten regions out of 8,501 containing
the true next region 65.69 percent of the time at California, with the shortlist's geographic
spread quoted against random draws, hedged as "motivation, not a measured service result".
**Edit:** lift that framing, hedge intact, into §1.1 or §2.5. It is the paragraph that makes an
outsider care, and it is currently the last thing they would reach.

---

## 4 · The protect list (already outstanding-grade; do not let an edit pass dilute these)

1. **The Chapter 3 preface**, `3_cbic.tex:15-33` / PDF p.28. It names what each later chapter
   changes and why the change identifies the cause. This paragraph, more than any other, is what
   makes three papers one document.
2. **The two qualifications in §6.1's Chapter 4 paragraph**, PDF p.78. They weaken the author's own
   headline number. Keep them even though finding 2 asks for reinforcement beside them — the fix is
   to add evidence, never to remove the retraction.
3. **§6.2's refusals**, PDF p.79: "The control does not say which part" and "we do not offer the
   ablation as evidence that the trunk contributes nothing."
4. **Chapter 5 §5.7's epoch-selection admission**, PDF p.76, including "It does not follow that the
   bias cancels exactly."
5. **§2.3's Pareto paragraph ending**, PDF p.23: "This dissertation therefore claims no Pareto
   property of any kind for its models." A literature review that declines an available claim is
   the chapter-2 test passing out loud.
6. **Limitation 6**, PDF p.81, the task-pair confound.
7. **The last sentence of §6.5**, PDF p.81: "worked through, it was the contribution's first half."
   That is the sentence that makes the null result an asset rather than a liability, and it earns
   the position it holds.

---

## 5 · Verdict (one paragraph, in Lovitts' terms)

This is a strong **very good** dissertation with a live, cheap path into **outstanding**, and the
usual demotion mechanism is inverted here: the documented "very good" pattern is a weak frame
wrapped around strong papers, whereas this frame is the best-argued part of the volume and the
thinnest link is the middle study. The honest null result is unambiguously an **asset** as
presented — time-indexed at p.28, kept as a finding rather than an embarrassment at p.78, and
converted into method at p.81 — and the arc does answer its research question, conditionally and
with the condition named. What holds it below outstanding is not honesty, coverage, or rigor; it is
that two syntheses the structure begs for are left for the reader to run: the cross-study evidence
table (finding 5), and the promotion of the controlled representation contrast of Table 9 into the
frame where the representation-dominance claim is actually made (finding 2). The single
highest-leverage remaining investment is finding 5 plus finding 2's second move, roughly half a day
together, both assembled from material already inside the document and requiring no new experiment
and no new claim. Finding 1 should be fixed before the volume reaches the banca, because it is the
only place where the document's own two sections disagree about how far its mechanism argument
reaches, and it sits on the one paragraph a committee will press.

---

## COUNTS

**blockers: 0 / should-fix: 5 / nits: 2**

No blockers found at this severity, and I am saying so rather than promoting a should-fix to fill
the slot: nothing I read at the argument level makes the dissertation indefensible or states a
result the document cannot support. Findings 1 and 4 are the two I would fix first.

## OUT-OF-SCOPE HANDOFFS (one line each, not my gates)

- Persona 06 / 07: §6.2's capacity-matched paragraph, `6_conclusion.tex:130-167` (PDF p.79–80),
  carries results "run after the Chapter 5 manuscript was submitted and reported here as a
  frame-level analysis" — a frame chapter reporting numbers no chapter sources (AGENT_GUARDRAILS
  N1 limits the frame to numbers already sourced in a chapter). It reads as deliberate and it has
  a `NEEDS SIGN-OFF` marker at `6_conclusion.tex:128`; I did not audit its values.
- Persona 06: two different gradient-cosine measurements coexist — the development-time +0.001 on
  four Gowalla states (PDF p.79) and Appendix F's seven-dataset equivalence result (PDF p.99–101) —
  and §6.2 does not cross-reference Appendix F where a reader would expect it.

## UNFINISHED

Reached the 30-minute checkpoint and stopped, per instruction. Not reached:

1. **PDF pages I did not read at all:** 1, 2, 8, 9, 10, 29–42, 45–57, 60–69, 72–74, 85, 89,
   93–100, 102. In particular the Portuguese Resumo (p.2) was not read, so I did not run the
   intro-conclusion loop test against the Resumo/Abstract claim-parity pair, and Table 10
   (p.72, the main results table) and Table 8 (p.66, dataset statistics) were not opened
   cell-by-cell.
2. **Finding 2's fix names a table I did not open cell-by-cell** — Table 7, PDF p.57 (CoUrb's
   sequential-task results). Whoever applies that fix must copy the values from the table itself.
   I quote no number from it.
3. **No citation identifier was checked** against Crossref/OpenAlex/arXiv this session, so this
   report contains no citation-existence or attribute finding of any kind. Persona 05 owns that
   gate; treat my silence on citations as unexamined, not as clean.
4. **Chapters 3, 4 and 5 methods sections** were read only where a claim or conclusion sent me
   there (p.43, p.58, p.70–71, p.75–77). The scope excluded methods detail, but that also means I
   cannot speak to whether the paper chapters' internal arguments hold up under their own methods.
5. **The scope was right for the clock.** I do not think it should have been wider; if anything,
   scoring ten rubric dimensions on a 102-page build is the part that would benefit from being
   split across two passes (frame chapters, then the paper chapters' claims), because dimensions
   4 and 5 are the two I scored on the least evidence.


---

<!-- estado-rodada -->
> **Rodada encerrada · último toque 2026-07-30 · sem autoridade.**
> Este ficheiro é registo de proveniência do que foi discutido nesta passagem, não fonte
> de um facto corrente. O que ficou decidido está em [`VEREDITOS.md`](../../../../VEREDITOS.md);
> os valores entregues estão em `CLAUDE.md` §0.1. Não copie nada daqui sem confirmar lá.
