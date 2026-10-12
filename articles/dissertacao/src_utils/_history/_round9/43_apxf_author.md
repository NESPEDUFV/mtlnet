# 43 — Appendix F reworked against the author's fifteen points, and relettered D

Round 9c, 2026-07-30. Track owner of `src/chapters/apx_f_cosine.tex` and
`src/tables/frame/cosine.tex`. The author's rulings are the `> **AUTHOR:**` block of
PENDENCIAS 2.22 (fifteen numbered points, 0-14, plus the sign-off approval). Every point below
carries his words, what was done, and the rendered evidence, read from `build/main.pdf` after the
final rebuild (101 pages, `tex_errors=0`, RC=0 read directly).

One edit in this track went OUTSIDE its two owned files, and it is declared here rather than
discovered later: `src/content.tex` (the appendix block, where the lettering lives) and one
paragraph of `src/main_extra.tex` (whose lettering sentence the rename made false). Point 0 cannot
be done inside the appendix file: the letter comes from the chapter counter in `content.tex`.
The `main_extra.tex` paragraph sits under that file's own `[NEEDS SIGN-OFF]`, so the author
reviews it with that volume.

## Point 0 — the rename to D, and the sign-off marker

**His words.** *"I approve the appedix F you can remove the `[NEEDS SIGN-OFF]`"* and *"You must
rename all the appendix, so the letters respect the correct order in the current version of the
text. In this case this appendix would be the letter D."*

**What was done.** The two `\setcounter{chapter}{N}` lines in `content.tex`'s appendix block were
removed, so the four main-volume appendices letter sequentially: A (contributions), B (AI
disclosure), C (ethics), D (this appendix). File names are unchanged; the letter comes from the
counter, not the file name. Both `[NEEDS SIGN-OFF]` markers inside `apx_f_cosine.tex` (the
whole-appendix one from round 7 and the PENDENCIAS-2.9 clause one from round 8) were converted to
`[SIGNED OFF 2026-07-30 ...]` records; no other file's markers were touched. This was done LAST,
after the other fourteen points.

**Rendered evidence (build/main.pdf).** Appendix headers print A (p. 90), B (p. 93), C (p. 94),
D (p. 97): `APPENDIX D – Why the Two Tasks Do Not Compete on the Shared Trunk`. The table of
contents lists APPENDIX A/B/C/D with the same titles. Every `\ref` prints the right letter:
"Appendix D measures the cosine" (p. 23, Ch. 2), "Appendix D reports the same quantity" (p. 80,
Ch. 6). The supplementary volume still letters its two appendices B and D (its own `\setcounter`
lines untouched; `make extra` evidence below).

**What the author should know (a consequence, not a defect).** The main volume now ALSO has an
Appendix B and an Appendix D, so a bare "Appendix B" is ambiguous across the two volumes. Measured
before deciding this is acceptable: all 10 live-prose pointers at the supplementary volume's
appendices say "Appendix~B/D of \extravolume" (rendered: "of the supplementary volume of this
dissertation"), so no reader-facing sentence is ambiguous. The `main_extra.tex` "About this
volume" paragraph, which claimed "a reference to Appendix B means the same thing in both volumes"
and "the letters A, C and E belong to appendices that stayed", became false with the rename and
was corrected (it now says the letters should be read together with the volume they belong to).
GLOSSARY.md lines 41/51/73 still say "Appendix B"/"Appendix D" about the supplementary volume's
appendices; those references remain correct because that is where the errata and the label-history
benchmark still live.

## Point 1 — the negative-transfer citation

**His words.** *"On the `an end up worse at both than two dedicated models are at one each.` we
shoud add a reference to it."*

**What was done.** `\cite{standley2020tasks}` added at the sentence. The key was already in
`references.bib` and is what Chapter 2's negative-transfer paragraph and Chapter 3's method
section cite for the same phenomenon, so no new bib entry was created. VERIFIED AT SOURCE THIS
SESSION per AGENT_GUARDRAILS §1 R1: arXiv:1905.07553 (Standley, Zamir, Chen, Guibas, Malik,
Savarese, ICML 2020), PDF downloaded and opened; p. 1 names negative transfer and states
"multi-task performance can suffer so much that smaller independent networks are often superior",
which is exactly this sentence's claim. Author list checked against the arXiv API record.

**Rendered evidence.** p. 97: "can end up worse at both than two dedicated models are at one each
[45]." Bibliography entry [45] is Standley et al., ICML 2020 (read from the rendered
bibliography, not the source).

## Point 2 — "stranger result"

**His words.** *"Don't say `stranger result` without cite some ref, but my main take is not to
say this, is your jugdment and can cause questions in the reviewer."*

**What was done.** His main take: the word went. "a stronger and stranger result than mere absence
of conflict" is now "a stronger statement than mere absence of conflict". "Stronger" survives
without a citation because the appendix derives it itself (the equivalence-versus-null paragraph
in D.2).

**Rendered evidence.** p. 97: "which is a stronger statement than mere absence of conflict".
"stranger" appears on no page of the document (probe validated: it matches the old sentence).

## Points 3 and 13 — the arc claims, measured and removed

**His words (3).** *"This phrase ... Have a huge erros in the first sutdy we use 2 diffents tasks,
than the last third study of mobiwac, also the arch of the MTLnet was different so we can relate
the results of this appendix to the first and secon study."* **(13.)** *"we need to take care
cause the first two studies was diferrent tasks that these ones that we are testing int eh
appendix F. Maybe remove this."*

**The measurement, from each chapter's live prose.** He is right, on both facts:
- Ch. 3 (`3_cbic/intro.tex`): tasks are POI Category Classification (static, no sequence) and
  Next-POI Prediction (the next category). Architecture (`3_cbic/method.tex`): "hard
  parameter-sharing scheme" with FiLM.
- Ch. 4 (`4_courb/methodology.tex`): same task pair; "the original MTLnet ... whose internal
  architecture is kept unchanged in this chapter". Only the input representation changes.
- Ch. 5 / this appendix: next category and next region, cross-attention trunk with no hidden
  layers in common (`5_mobiwac/04_method.tex`).
The appendix's measurement shares neither the task pair nor the architecture with studies one and
two, and its own extension section already says orthogonality measured on one architecture cannot
be carried to another ("Nothing here says the gradients stay orthogonal in a model that shares
more of its depth" — hard sharing shares its whole trunk). A sentence carrying this result back to
the first two studies is therefore unsupportable, and both sentences were REMOVED rather than
scoped: any scoped version ("had those studies' tasks also been orthogonal...") would be a
speculation the data cannot back.

**What was cut.** (3) The intro sentence "That is why varying the gradient balancer changed so
little in the first study, and why changing the representation changed so much in the second and
third."; the paragraph's consequence clause was re-scoped from "for the whole investigation" to
"for that model". (13) The whole F.3 paragraph "The second is about the arc of the three
studies..." (six sentences, previously p. 101); with it gone, the section opener "Two consequences
follow" was reshaped to announce only the balancer consequence.

**No unique fact was lost.** The balancer consequence stays (it is the measured one, scoped to
Chapter 5); Ch. 5's own development-time cosine stays in `5_mobiwac/02_related.tex`, untouched;
the conclusion's pointer (`6_conclusion.tex`, p. 80) already scopes the finding to "this pair of
tasks rather than a general rule" and needed no edit.

**Rendered evidence.** "changed so little in the first study" and "arc of the three studies"
appear on no page (both probes validated against the old sentences). p. 97: "it carries a direct
consequence for that model: a gradient balancer had nothing to balance." p. 100 (D.3): the section
runs from the balancer consequence directly to the extension section.

## Point 4 — the gradient-cosine approach citation

**His words.** *"On the `the cosine of the angle between the two resulting gradient vectors was
recorded` we should cite some article/studie/document that show this apporach."*

**What was done.** The sentence now ends ", the quantity the gradient-surgery literature uses to
define task conflict~\cite{yu2020pcgrad}". The key was already in `references.bib`; it is the
source Chapter 2's gradient-conflict definition cites, and GLOSSARY §4's "gradient conflict" row
pins it (Def. 1, arXiv:2001.06782). VERIFIED AT SOURCE THIS SESSION: arXiv:2001.06782 PDF opened;
p. 1: "We define two gradients to be conflicting if they point away from one another, i.e., have
a negative cosine similarity"; p. 4 (Definition 1 and the PCGrad procedure) computes the cosine
between task gradients; p. 9, Fig. 4, records the fraction of training iterations with
positive/negative gradient cosine — the same per-iteration measurement this appendix records per
epoch. Author list checked against the arXiv API record.

**Rendered evidence.** p. 97: "was recorded, the quantity the gradient-surgery literature uses to
define task conflict [50]." Bibliography [50] is Yu et al., NeurIPS 2020.

## Point 5 — the over-detailed series clause

**His words.** *"Exclude this: `so one configuration on one dataset is five series of fifty
values, and two of Florida's carry a partial re-run on top of theirs.`, is over detail."*

**What was done.** Cut; the sentence now ends at "fifty epochs". Fact check before deleting: the
series structure is restated by the unit-of-independence paragraph and the table's Unit/n columns;
the partial re-run's full disclosure (10 of 75 series carry duplicated epochs 1..15; moves no
verdict) lives in the round-7 source comment, which was re-headed to say it is now the fact's only
home. The extension section's "over the observations as recorded" hedge still covers the
duplicated epochs for the reader.

**Rendered evidence.** p. 97: "Every run is five-fold user-disjoint cross-validation over fifty
epochs. Six of the seven are..."; "five series of fifty" appears on no page.

## Point 6 — the development-time measurement sentence

**His words.** *"This is a implementation detail let's exclude also: `That chapter reaches the
same conclusion from a smaller development-time measurement, on an earlier data preparation and
over four seeds rather than per-epoch series, so the two sets of numbers are not interchangeable
and this appendix supersedes nothing there.`"*

**What was done.** The implementation detail went (which preparation, seeds versus epochs, who
supersedes whom); ONE plain sentence stays: "Chapter 5 also reports its own smaller measurement of
this quantity; that one comes from a different run, so the two sets of numbers are not
interchangeable." The fact could not go entirely: Ch. 5's related-work section reports this same
cosine at +0.001 pooled / +0.0032 largest per-dataset mean, while the appendix reports Alabama at
+0.0112. This sentence is the only live-prose site telling the reader the two are different runs
(measured; no other site in this file or Ch. 5 says it), and without it a comparing reader reads a
contradiction. The detail is preserved in the source comment.

**Rendered evidence.** p. 97: "Chapter 5 also reports its own smaller measurement of this
quantity; that one comes from a different run, so the two sets of numbers are not
interchangeable." The old wording appears on no page.

## Point 7 — the fold/Florida paragraph

**His words.** *"this part explain the how the experiments was runned is importante, but we can
simplify the details, don't need to do a lot of tech explanation, also about the florida I belive
explain it in much details can cause confusion, lets try to be more straight."*

**What was done.** The paragraph kept exactly what he asked to keep (the tests run on folds) and
lost the depth: the anti-conservatism explanation ("would report more confidence than the data
hold") is now carried by the plainer first sentence; Florida's twelve-configurations-not-
independent-either digression went to the source comment, and its fact (the n=12
configuration-mean reading, same +0.0003, TOST 1.3e-16) remains in the TABLE FOOTNOTE where the
reader meets the numbers. Down from four dense sentences to four short ones.

**Rendered evidence.** p. 97-98: "Those fifty values are not fifty independent measurements: they
are consecutive states of one training run. The unit of independence is the fold, and every test
below runs on folds: five fold means at each dataset, and at Florida its sixty fold series, five
folds for each of its twelve configurations. Each dataset is measured at a single random
initialization, so the variation the tests see is across folds, not across restarts. Where a count
of observations appears it describes the data, not a test's sample size."

## Point 8 — the British construction

**His words.** *"The phrase: `feature needs saying plainly` this is britisher english and this
boke on of the agents_guartrails. If this is not in the guardrails add this and eval in the rest
of the text if we have similar stuctures that are britisher."*

**What was done, in this file.** "one feature needs saying plainly" is now "one feature must be
stated plainly". Needs+gerund is the British construction; WRITING_LAW §1 requires American
English. Measured in this file before the fix: `needs [a-z]+ing` over live prose returned exactly
this one hit.

**Reported to the other track (the rule and the document-wide sweep are theirs).** The register
law and its gate (`check_register.py`, added this round by the parallel track) own the
document-wide rule; this track's finding for them: one needs+gerund instance existed in
`apx_f_cosine.tex` and is fixed; their gate should keep `needs\s+\w+ing` (or equivalent) in its
pattern set so the construction cannot return.

## Points 9 and 10 — the departures opener

**His words (9).** *"This phrase: `Two departures from that flat picture appear` is pure A.I, we
cna be more simple and direct."* **(10.)** *"`both are worth reporting rather than smoothing` we
don't need to say this, appears as we are try to hide somthing we just need to report."*

**What was done.** The opener is now "Two patterns stand out in the data." — both flagged clauses
gone in one edit. "Departure" was also retired from the rest of the section (see point 11) so the
vocabulary does not cycle.

**Rendered evidence.** p. 99: "Two patterns stand out in the data. The first is a positive
tendency that recurs on two datasets..." Neither old clause appears on any page.

## Point 11 — the t-test sentence and its paragraph

**His words.** *"you don't say which datasets, and this phrase is confusing and hard to read for
whom don't have a lot of knowhow. We can try to improve the rest of this paragraph."*

**What was done.** The sentence now names the datasets: "A t-test does reject at Alabama and at
Georgia, for the positive means and for the declines, but with five folds that rejection depends
on assuming the fold means are normally distributed, an assumption five values cannot check."
Checked against the source of record before writing (cosine_stats6.py output +
gradient_cosine_slopes6.json): positive-mean t-tests AL 0.0125 / GA 0.0093, slope t-tests AL
0.0058 / GA 0.047, and the sign tests sit at the 0.0625 floor in all four cases — so Alabama and
Georgia, both patterns, are exactly the rejections. The rhetorical "this appendix will not accept
for one claim a basis it rejects for another" went; the California and Florida sentences kept
their facts with lighter phrasing.

**Rendered evidence.** p. 100: "A t-test does reject at Alabama and at Georgia, for the positive
means and for the declines, but with five folds that rejection depends on assuming the fold means
are normally distributed, an assumption five values cannot check."

## Point 12 — the non-native-reader paragraph

**His words.** *"is well written, but is not natural for a non native writer in english, and force
a non native read more than once to understand."*

**What was done.** "Both point away from trouble in any case. A positive cosine is mild
cooperation, not conflict, and the decline stays inside the margin throughout while moving toward
zero rather than away from it." is now "Neither pattern suggests a conflict. A positive cosine
means the two tasks cooperate slightly, and the declining cosines stay inside the margin and move
toward zero, not away from it." Three facts, three plain clauses, no phrasal metaphor.

**Rendered evidence.** p. 100: the new text prints as written; the old appears on no page.

## Point 14 — the knowledge-sharing qualification

**His words.** *"Somthing that worths to mention, don't need fither explanation, in the F.3 is
that besides the gradients don't addup, this don't means that the tasks are not sharing their
knowladge since exstie otehr mechanims like the gate in the arch and so on..."*

**What was done.** One sentence, as instructed, at the end of the balancer paragraph in D.3:
"Orthogonal gradients also do not mean that the tasks share no knowledge: the two streams still
exchange information through the cross-attention trunk, a sharing mechanism this measurement does
not read."

**Why it names the cross-attention exchange and not the gate.** Grounded in what the model
actually contains before writing, as the brief required. The gate he names EXISTS in the code:
`src/models/next/next_stan_flow_dualtower/head.py` implements gated fusion as the PRIMARY fusion
mode of the region output (g = sigma(W.[priv; shared])). But Chapter 5's prose never describes it
(grep over `5_mobiwac/*.tex` live prose: zero occurrences of gate/gating/gated) and GLOSSARY.md
registers no "gate" term, so naming it in the appendix would introduce an unregistered term for a
component the dissertation never describes (the fail-closed glossary rule). The mechanism Ch. 5
DOES describe, in registered vocabulary, is the cross-attention exchange ("attention lets each
stream read the other's features"; "the tasks therefore share by exchanging information between
per-task streams"). The sentence names that as the example; the gate is covered by the sentence's
subject being the mechanisms the measurement does not read, without a second example ("no further
explanation", his instruction). If he wants the gate named explicitly, it needs a Ch. 5 prose
edit (now allowed per his 2.9 ruling) plus a GLOSSARY row first — flagged as his call.

## Builds and gates, exit codes read directly, runs postdating the last edit

- defense 101 pp, academico 98 pp, ppgc 102 pp, extra 20 pp; tex_errors=0 and RC=0 in all four.
  (Baseline was 102/99/103/20: the cuts cost one page in each main-volume variant.)
- `bash src_utils/check.sh` -> rc=0, 25 gates, torn-sentence suspects 0, trapped-prose suspects 0.
- `python3 src_utils/check_audit_claims.py` -> rc=0.
- Page-count records (CLAUDE.md, PLAN.md, codex_reviewer.md) synced by
  `sync_page_counts.py --write` (7 claims updated).
- One defect this round INTRODUCED and the gate CAUGHT before commit: the point-8 provenance
  comment swallowed the following prose line ("Of the 4,650 cosines, 92.4 percent...") — the
  trapped-prose defect this file has been bitten by before. Fixed, rebuilt, re-checked; the
  final render carries the sentence (p. 99).

## Commit

- `4eea637a` — all six files (the two owned, content.tex, main_extra.tex, and the three
  page-count records).



---

<!-- estado-rodada -->
> **Rodada encerrada · último toque 2026-07-30 · sem autoridade.**
> Este ficheiro é registo de proveniência do que foi discutido nesta passagem, não fonte
> de um facto corrente. O que ficou decidido está em [`VEREDITOS.md`](../../../VEREDITOS.md);
> os valores entregues estão em `CLAUDE.md` §0.1. Não copie nada daqui sem confirmar lá.
