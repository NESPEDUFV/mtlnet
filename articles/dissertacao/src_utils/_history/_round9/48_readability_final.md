# 48 · Readability editor (persona 15), round 9 final — first-read comprehension over everything this round changed

**Reviewer:** persona 15, `reviewers/15_readability_editor.md` as rewritten by the author at commit `89b7eca1`
("docs: enforce first-read comprehension").
**Method:** the file's own review method. One uninterrupted reading of each unit with no backtracking,
recording every passage whose meaning or logical connection was not clear after that single reading; then the
analytical pass over the eleven lenses.
**Judged on:** the rendered PDFs, `build/main.pdf` (101 pp) and `build/main_extra.pdf` (22 pp), both rebuilt at
the head of this round (`make defense` rc=0, `make extra` rc=0, read directly).
**Scope:** the diff `89b7eca1..HEAD` over `src/`. That range reproduces the diffstat in the brief exactly
(`apx_f_cosine.tex` 219+/63-, `6_conclusion.tex` 53+/13-, `4_courb/methodology.tex` 74+/27-,
`apx_b_errata.tex` 41+/13-), so the baseline is confirmed rather than assumed.
**Instrument:** prose read through `check_audit_claims.live_text` (comments stripped, lines joined), so every
sweep below crosses line wraps. Provenance comments in this tree quote the sentences under review; an
unfiltered grep over-reports here (V4).

**The bar is the author's, not a general one.** He found British English and phrasing that "don't seems like
nothing that a non native writer would write" in prose that had already passed five persona reviews. So the two
questions asked of every sentence were his: would a Brazilian non-native writer of academic English produce it,
and can a non-native reader take it in on one reading.

---

## 1 · First-read log

One pass per unit, no backtracking. Sentence counts are live prose in the built PDF (comment-stripped,
math and citation macros removed, fragments under four words dropped), counted per unit rather than estimated.

| # | Unit | Sentences read | First-read verdict |
|---|---|--:|---|
| 1 | `chapters/apx_f_cosine.tex` — Appendix D, pp. 97–101 | 71 | **NEEDS REVISION** — two passages |
| 2 | `chapters/6_conclusion.tex` — Ch. 6, pp. 78–81 | 58 | **NEEDS REVISION** — two passages |
| 3 | `chapters/4_courb/methodology.tex` — §4.3, pp. 48–53 | 75 | PASS |
| 4 | `chapters/apx_b_errata.tex` — Appendix B, extra pp. 5–13 | 69 | **NEEDS REVISION** — one passage |
| 5 | `content.tex` — Resumo and Abstract, pp. 2–3 | 23 | **NEEDS REVISION** — one passage (both languages) |
| 6 | `chapters/2_fundamentals.tex` — Ch. 2, pp. 17–27 | 197 | PASS |
| 7 | `chapters/5_mobiwac/02_related.tex` — §5.2, pp. 61–63 | 44 | PASS |
| 8 | `chapters/5_mobiwac/06_results.tex` — §5.6, pp. 70–75 | 75 | PASS |
| 9 | `chapters/4_courb/{intro,related,results}.tex` — pp. 44–47, 54–57 | 86 | PASS |
| 10 | `chapters/3_cbic/{basis,method}.tex` — pp. 30–37 | 112 | PASS |
| 11 | `main_extra.tex` — "About this volume", extra p. 3 | 14 | **NEEDS REVISION** — one passage |
| 12 | changed tables under `src/tables/` (five files) | 49 | PASS |
| | **Total** | **873** | |

**Overall first-read verdict: NEEDS REVISION.** Seven passages did not survive one reading. They are R15-01
through R15-07 below. Everything else in 873 sentences did.

### What stopped the reading, in the order it happened

1. **Appendix D, second sentence, p. 97.** "if the update next-region asks for points against the update
   next-category asks for" — I parsed "asks for points" as verb plus object, reached "against", and had to
   go back. Two omitted relative pronouns and two stranded prepositions in one clause. This is the entry
   point of the appendix the author sent back fifteen points on, and it is the first sentence in the document
   that carries an idea. (R15-04)
2. **Appendix D §D.4, p. 101.** "The second axis is the data. It now covers every dataset Chapter 5 reports
   on" — "It" sits two words from "axis" and three from "the data", and "now" asks the reader to compare
   against a version of the appendix that is not in front of them. (R15-06)
3. **Chapter 6 §6.2, p. 79.** "whose region head was driven by a transition prior the models reported here do
   not use" — the missing relative pronoun made "the models" read momentarily as a second object of "driven
   by". (R15-03)
4. **Chapter 6 §6.2, p. 80.** "three of which are among the five we report, directional conflict only, a
   finding for this pair of tasks" — a bare noun phrase between commas, attached to nothing. I could not tell
   what it modified. (R15-05)
5. **Abstract, p. 3.** Forty-seven words, of which the 24 before the subject are protocol conditions. I reached
   "that joint model" having already lost the thread of what the conditions attached to. The Resumo's
   counterpart is fifty-seven words. (R15-07)
6. **Supplementary volume, "About this volume", extra p. 3.** The dissertation is named by a title that is not
   its title. I stopped to check whether I was holding the right document. (R15-02)
7. **Appendix B §B.3, extra p. 11.** "one cites Appendix ??." The third item of a three-item list has no
   referent at all. (R15-01)

### What read well, and should be protected

- **§2.3, pp. 22–24 (multi-task learning).** The Pareto passage does something difficult very well: it defines
  dominance, optimality and stationarity in three consecutive sentences, each one short, and then uses the
  distinction immediately to say what each method does and does not claim. A reader learns a formal hierarchy
  without a formal apparatus. The closing move ("This dissertation therefore claims no Pareto property of any
  kind for its models") lands because the ground was laid.
- **§4.3, pp. 48–53 (CoUrb methodology), the largest changed unit at 101 lines.** Seventy-five sentences, no
  first-read stumble. The translated prose now reads as one voice with the frame chapters, and the passage
  that gave the most trouble in earlier rounds, the Nash-MTL guarantee, is now stated with its condition
  inline ("Away from a Pareto-stationary point, meaning a point at which some convex combination of the task
  gradients is zero") and is clear on one pass.
- **Appendix D §D.2, p. 98, the equivalence-versus-null paragraph.** "A test that merely failed to reject zero
  would license one statement... An equivalence test licenses the positive claim instead." This is the single
  hardest idea in the appendix and it is the easiest paragraph in it to read. Do not touch it.
- **§5.6.2, pp. 74–75, the floor-above-the-baselines discussion.** Names the awkward fact, gives the two
  reasons, declines to pick one, and says what the reader should take from it. Model of honest exposition.
- **Chapter 6 close, p. 81.** "The negative result was not an obstacle on the way to the contribution; worked
  through, it was the contribution's first half." Earns its place.

### Chapter-seam verdict

**The seam holds.** Reading pp. 44–57 (CoUrb, translated) directly against pp. 17–27 (frame) and pp. 78–81
(frame), the register is one author's. The reproduced chapters keep their own sentence rhythm, which is
correct and should not be smoothed, but vocabulary, hedging and verb-to-test binding are consistent across
the seam. The two places the seam is visible are both defensible: the CBIC chapter's first-person plural
against the frame's third person, and the CoUrb chapter's longer noun phrases. Neither cost a re-read.

---

## 2 · Findings, ranked

REQUIRED means it breaks a written rule or genuinely obstructs first-read comprehension. Every quote below was
confirmed verbatim in the comment-stripped source AND located in the rendered PDF before it was written down;
every proposed replacement was run against `check_register.py`'s four shapes and spelling families,
`check_process_narration.py`'s five rules, and the em-dash, contraction, American-English and glossary
constraints. All ten came back clean.

---

### R15-01 · REQUIRED · undefined cross-reference renders as "Appendix ??"

**File:** `src/chapters/apx_b_errata.tex:396` · **Page:** `main_extra.pdf` p. 11, §B.3

> one cites the benchmark of Appendix~\ref{apx:ceiling}, one cites this chapter's own results table, and one
> cites Appendix~\ref{apx:cosine}.

**Renders as:** "one cites the benchmark of Appendix D, one cites this chapter's own results table, and one
cites **Appendix ??**."

**Breaks:** first-read comprehension at its strongest (lens 2, lens 4); WRITING_LAW §5 anti-patterns
("unresolved \ref/\cite"); §7 consistency checklist, last line.

**Why it fails on one reading.** The sentence names three items and the third has no referent at all. The
label `apx:cosine` belongs to `chapters/apx_f_cosine.tex`, which `content.tex` includes and `main_extra.tex`
does not, so the reference cannot resolve in this volume. The build says so: `Reference 'apx:cosine' on page 11
undefined on input line 396`. Confirmed in the render itself, not only in the text layer. The sentence was
added this round. Note that every other cross-volume pointer in this document already uses a hard-coded letter
plus `\extravolume` — twelve uses across eight files, e.g. "Appendix~B of \extravolume" at
`chapters/3_cbic/method.tex` — precisely because `\ref` cannot cross the volume boundary. This one line
departs from the convention the rest of the document follows.

**Proposal.** Use the house convention. Because the errata appendix is in the supplementary volume and the
cosine appendix is in the dissertation, the pointer runs the other way:

> one cites the benchmark of Appendix~\ref{apx:ceiling}, one cites this chapter's own results table, and one
> cites Appendix~D of the dissertation.

If the author would rather not print a bare letter that also names an appendix of the volume the reader is
holding, "the gradient-cosine appendix of the dissertation" is unambiguous and needs no letter.

---

### R15-02 · REQUIRED · the supplementary volume names the dissertation by a title that is not its title

**File:** `src/main_extra.tex:206` · **Page:** `main_extra.pdf` p. 3, "About this volume"

> This volume holds two appendices that were written for the dissertation ``From Representations to a Single
> Joint Model: Multi-Task Learning for Point-of-Interest Category and Region Prediction'' and that are
> published beside it rather than inside it.

**Breaks:** lens 4 (clarity: nothing interpretable two ways), lens 7 (consistency of conventions across the
document).

**Why it fails on one reading.** That is not the title of the dissertation. The cover of this same volume, its
own `\titulo` field one hundred lines above this paragraph, and the folha de rosto, Resumo and Abstract of the
main document all read **"Multi-Task Learning for Point-of-Interest Classification and Prediction Tasks: The
Role of the Check-in-Level Representation"**. A reader holding both volumes meets two different titles for one
work within three pages, on the page whose entire job is to say what this volume belongs to, and has no way to
tell which is current. The paragraph two lines below was rewritten this round and the stale title survived the
edit.

**Proposal.** Quote the title of record, the same string this file's own `\titulo` already carries:

> This volume holds two appendices that were written for the dissertation ``Multi-Task Learning for
> Point-of-Interest Classification and Prediction Tasks: The Role of the Check-in-Level Representation'' and
> that are published beside it rather than inside it.

Stronger still, drop the quoted title: "written for the dissertation named on the cover of this volume" cannot
go stale a second time.

---

### R15-03 · REQUIRED · unregistered term "region head", plus an omitted relative pronoun, in one clause

**File:** `src/chapters/6_conclusion.tex:143` · **Page:** `main.pdf` p. 79, §6.2

> that measurement was taken on an earlier configuration whose **region head** was driven by a transition
> prior **the models** reported here do not use

**Breaks:** GLOSSARY fail-closed rule §1 and MobiWac GLOSSARY §4 (jargon list); WRITING_LAW §1 (write relative
pronouns); lens 7 (consistency of terminology across the document).

**Why it fails.** Two defects in one clause.

*"region head".* The MobiWac GLOSSARY §4 lists "head" among the internal research words that are jargon in
prose and prescribes "output", exempting the word only "when describing OTHER systems (HMT-GRN's next-place
head, CSLSL's shared trunk)". This clause describes **our own** earlier configuration, so the exemption does
not apply. This exact wording was already caught and corrected once, at `5_mobiwac/06_results.tex`, whose
provenance comment records the change to "region output"; `AGENT_GUARDRAILS` §4b V13 seventh instance records
the same sentence as the case where a reviewer read the evidence and classified it wrongly. Measured across
all 59 live `.tex` files: **"region output" 7 occurrences, "region head" 1** — this one. So the term is both
unregistered and inconsistent with the rest of the document.

*The omitted pronoun.* "a transition prior the models reported here do not use" drops the relative pronoun
that WRITING_LAW §1 requires be written. On first reading "the models" attaches to "driven by" before the
sentence forces a re-parse.

**Proposal.**

> that measurement was taken on an earlier configuration whose **region output** was driven by a transition
> prior **that** the models reported here do not use

The parallel sentence at `5_mobiwac/06_results.tex` reads "a region-transition prior the models reported here
do not use"; if the author wants the two to match exactly, the pronoun should go into both.

---

### R15-04 · REQUIRED · the appendix's opening idea cannot be parsed on one reading

**File:** `src/chapters/apx_f_cosine.tex:79` · **Page:** `main.pdf` p. 97, Appendix D opening paragraph

> The usual reason is a disagreement, and it shows up in the gradients: if the update next-region asks for
> points against the update next-category asks for, one task improves at the other's expense.

**Breaks:** WRITING_LAW §1 (write relative pronouns; no phrasing a non-native reader must read twice); lens 1,
lens 2, lens 10.

**Why it fails on one reading.** This is the second sentence of the appendix and the first that carries an
idea. It stacks two reduced relative clauses with the pronoun omitted ("the update next-region asks for", "the
update next-category asks for"), both ending on a stranded preposition, and then puts the two stranded
prepositions in one clause with "points against" between them. The reader parses "asks for points" as a
verb-object pair, hits "against", and has to unwind. The clause is grammatical and it is not one of the four
gated shapes, which is exactly the class the author says survives the sweeps.

The appendix was reworked to fifteen author points this round and this sentence was not among them; it is
unchanged from the version he read.

**Proposal.** Name the two updates and let them act. The technical content is identical:

> The usual reason is a disagreement, and it shows up in the gradients: when the two tasks ask for opposite
> updates, one task improves at the other's expense.

If the two tasks must be named in the clause, "when the update the next-region task asks for opposes the
update the next-category task asks for" keeps them, but it is still two reduced clauses; the shorter form is
the one a non-native reader takes in first.

---

### R15-05 · RECOMMENDED · an appositive with no grammatical attachment, using an unregistered term

**File:** `src/chapters/6_conclusion.tex:159` · **Page:** `main.pdf` p. 80, §6.2

> the cosine similarity between the two tasks' gradients averaged $+0.001$ over four seeds on four Gowalla
> states, three of which are among the five we report, **directional conflict only**, a finding for this pair
> of tasks rather than a general rule.

**Breaks:** lens 4 (ambiguous reference), lens 10 (awkward though grammatical); GLOSSARY §1 fail-closed
("gradient conflict" is the registered term; "directional conflict" is not registered).

**Why it fails on one reading.** "directional conflict only" is a bare noun phrase dropped between two commas
with no verb and no attachment. It arrives after a relative clause about which states are reported, so the
reader must decide whether it qualifies the average, the states, or the measurement. None of the three is
stated. The sentence delivers its number and then stalls.

**Proposal.** Split the appositive into its own sentence and use the registered term:

> the cosine similarity between the two tasks' gradients averaged $+0.001$ over four seeds on four Gowalla
> states, three of which are among the five we report. The cosine measures gradient conflict in direction
> alone, and this is a finding for this pair of tasks rather than a general rule.

---

### R15-06 · RECOMMENDED · "It now covers" dates the document against a version the reader never saw

**File:** `src/chapters/apx_f_cosine.tex` · **Page:** `main.pdf` p. 101, §D.4

> The second axis is the data. **It now covers** every dataset Chapter~\ref{ch:mobiwac} reports on:

**Breaks:** WRITING_LAW §1 (process narration, the document's own version history), lens 4 (ambiguous
pronoun).

**Why it fails.** Two problems in seven words, and the first is the class the author has complained about by
name. "now" is true only by contrast with an earlier state of this appendix that covered fewer datasets. That
is the version-history sub-class the law bans outright, and it is the same appendix that carried the deleted
sentence "California, Texas, and Istanbul were absent from an earlier version of this appendix". A banca
member reading the deposited document has no earlier version to contrast with, so "now" is not merely
redundant, it is unreadable. Second, "It" sits two words from "axis" and three from "the data"; a reader who
resolves it to "the data" gets "the data covers every dataset", which is circular.

The gate is silent here, correctly — its version-history pattern is built from the deleted sentence's shape
and cannot express a bare "now" (see §4).

**Proposal.** Name the subject, drop the time-word:

> The second axis is the data. The seven datasets cover every dataset Chapter~\ref{ch:mobiwac} reports on:

The count of seven is already stated in §D.1 and in the figure caption, so nothing is lost, and the sentence
stops depending on a version the reader never had.

---

### R15-07 · RECOMMENDED · the Abstract's headline sentence stacks 24 words of protocol ahead of its subject

**File:** `src/content.tex` · **Pages:** `main.pdf` p. 3 (Abstract) and p. 2 (Resumo)

> Under user-disjoint cross-validation, with twenty fitted models per configuration, four random
> initializations over five fixed folds, and paired tests on the four initialization means, that joint model
> outperforms the dedicated models on next category at all six, by 5.3 to 9.4 macro-F1 points under a
> joint-best selection.

**Breaks:** lens 2, lens 6 (conciseness), lens 11 (reader experience); WRITING_LAW §1 ("reduce clause load...
or split it").

**Why it fails on one reading.** Forty-seven words, of which the first 24 are protocol conditions held ahead
of the subject "that joint model" (counted: `s.split()` gives 47 tokens, the subject at index 24). The reader carries four unattached prepositional phrases before learning what the
sentence is about, and this is the headline result on the most-read page of the document. Its Resumo counterpart is worse at fifty-seven words with 32 ahead of its subject. Every other sentence on both pages runs between five and
thirty-nine words, so this one breaks the rhythm of the page as well.

**Proposal.** Lead with the result, let the protocol follow. Every number, hedge and convention is preserved:

> Under user-disjoint cross-validation, that joint model outperforms the dedicated models on next category at
> all six, by 5.3 to 9.4 macro-F1 points under a joint-best selection. The protocol uses twenty fitted models
> per configuration, four random initializations over five fixed folds, and paired tests on the four
> initialization means.

Apply the same split to the Resumo so the claim-parity audit (WRITING_LAW §6) still passes on the pair.

---

### R15-08 · RECOMMENDED · a comma between subject and verb reads as a false list-start

**File:** `src/chapters/apx_b_errata.tex` · **Page:** `main_extra.pdf` p. 9, §B.2

> \emph{ST-MTLNet}**,** is a different name and keeps its published form throughout, and the public repository
> address printed in Chapters~\ref{ch:cbic} and~\ref{ch:mobiwac} keeps its own casing, since it is a literal
> address rather than the model name.

**Breaks:** lens 10 (sentence-level craft), lens 4.

**Why it fails.** The comma stands between the subject and its verb, so the sentence opens as though a list is
starting and then does not. It sits mid-paragraph in the one passage whose whole subject is a naming
distinction the reader is holding in mind (MTLnet against ST-MTLNet), which is exactly where a false
list-start costs a re-read. Not introduced this round, but it is inside a changed unit and the fix is one
character.

**Proposal.** Delete the comma: "\emph{ST-MTLNet} is a different name and keeps its published form
throughout, and the public repository address...".

---

### R15-09 · OPTIONAL · the replacement for the author's flagged sentence keeps its shape

**File:** `src/chapters/apx_f_cosine.tex` · **Page:** `main.pdf` p. 99, §D.2

> Two patterns stand out in the data.

**Why raised.** This round replaced "Two departures from that flat picture appear" — the sentence the author
called "pure A.I, we can be more simple" — with this one. The replacement is a real improvement and the gate
is silent on it. But it keeps the shape he objected to: a numeral-led abstract subject with a verb of
appearance at the end of the clause. "stand out" is also a phrasal verb, which WRITING_LAW §4's idiom rule
treats as a class to avoid. It did not cost me a re-read, so this is preference, not defect.

**Proposal.** "The figure shows two patterns." — which is close to the remedy the register gate itself prints
for this shape — or "Two patterns recur across the datasets."

---

### R15-10 · OPTIONAL · "Settling that needs" collides with the banned need+gerund shape

**File:** `src/chapters/apx_f_cosine.tex` · **Page:** `main.pdf` p. 101, §D.4, last sentence of the appendix

> **Settling that needs** the same diagnostic and nothing else changed: the per-epoch cosine on the
> candidate's shared parameters, under a fixed loss weighting, across one dataset's folds, with the fold means
> tested for equivalence against a margin chosen in advance.

**Why raised.** A gerund subject immediately followed by "needs" reads for one beat as the British
need+gerund construction the register law now bans by name — the author's own instance, "feature needs saying
plainly", came from this appendix. It is **not** that construction and the gate is right to stay silent. But
the collision is unfortunate on the page where he found the original, and the sentence is the appendix's last,
running thirty-eight words across four appositives.

**Proposal.**

> Answering that question needs the same diagnostic and nothing else changed: the per-epoch cosine on the
> candidate's shared parameters, under a fixed loss weighting, across one dataset's folds. The fold means are
> then tested for equivalence against a margin chosen in advance.

---

## 3 · Scores

| Dimension | Score | Justification |
|---|--:|---|
| First-read comprehension | 7/10 | Seven passages in 873 sentences needed a second reading; two of the seven (R15-01, R15-02) are reference defects rather than prose. |
| Readability | 8/10 | Sentences are direct and the technical density is well managed; the outliers are two long stacked-condition sentences and two reduced-relative clauses. |
| Flow | 9/10 | Paragraphs transition without jolts; §2.3 and §D.2 are exemplary; §D.4's "It now covers" is the only weak junction. |
| Clarity | 7/10 | Three ambiguous references (R15-01 an absent one, R15-05 an unattached appositive, R15-06 a pronoun with two candidates). |
| Conciseness | 8/10 | Little filler anywhere; the Abstract and Resumo headline sentences are the two genuine offenders. |
| Consistency | 8/10 | One unregistered term against seven registered uses of its replacement, one stale document title, otherwise steady. |
| Overall writing quality | 8/10 | Above the bar for a defended dissertation; the seven passages above are specific and cheap to fix. |

---

## 4 · The gates, and where they cannot see

### Do the two gates agree with me?

Both are green and **both are correct on what they measure.**

```
python3 src_utils/check_register.py            -> rc=0
python3 src_utils/check_process_narration.py   -> rc=0
```

`check_register.py`: "no British spellings or constructions and no gated hard-phrasing shape in 54 .tex files;
references.bib 5 authored field types checked, 0 hit(s); 1 hit(s) held open by name" — the open hit is
`chapters/3_cbic/conclusion.tex` "biased towards the features required", verbatim published CBIC prose held
for the author as an errata decision. That register is doing its job. The gate's own output says a green
result "is NOT a first-read PASS", which is precisely the finding of this report.

`check_process_narration.py`: "no process narration in 51 files (3 exempt); self-test passed in both
directions."

**Agreement:** the gates and I agree on everything the gates express. Of my ten findings, **none** is a gate
false negative on a shape the gate claims to cover. Four are in classes no gate expresses at all. I verified
this by running the gates' own patterns against my findings rather than assuming:

| Sentence | Gate verdict | Correct? |
|---|---|---|
| "Two departures from that flat picture appear" (the author's, now deleted) | FIRES: delayed subject | yes — the gate can see its target |
| "if the update next-region asks for points against..." (R15-04) | SILENT | yes — not one of the four shapes |
| "It now covers every dataset..." (R15-06) | SILENT (both gates) | yes — not one of the five narration patterns |
| "a transition prior the models reported here do not use" (R15-03) | SILENT | yes — no rule expresses it |
| "...directional conflict only, a finding..." (R15-05) | SILENT | yes — no rule expresses it |
| "Two patterns stand out in the data" (R15-09) | SILENT | yes — "stand out" is not in `_APPEAR` |

### Gap 1 — the omitted relative pronoun, and this is the one worth closing

WRITING_LAW §1 requires relative pronouns be written ("the head **that** we do not predict") and **no gate
enforces it**. It is the mechanism behind two of my four REQUIRED findings (R15-03, R15-04) and it is exactly
the author's class: grammatical, native-sounding, and a re-read for a non-native reader.

The general shape is hard to express, but its worst sub-case is not: a reduced relative clause that **ends on
a stranded preposition**, which is where the reader's parse actually breaks. That is expressible.

```python
# Reduced relative clause ending on a stranded preposition:
#   <det> <noun> ... <verb> <prep> [,.;:]
# The wh-lookbehinds spare the legal cases: an interrogative or a written relative pronoun
# already tells the reader a clause is coming ("what the answer depends on").
P_STRANDED = re.compile(
    r"(?<!\bwhat )(?<!\bwhich )(?<!\bthat )(?<!\bwhom )(?<!\bwhere )"
    r"\b(?:the|a|an|its|their|this|that|one|two|each|every|no)\s+"
    r"[a-z][a-z-]{2,}\s+"
    r"(?:[a-z][a-z-]*\s+){0,3}?"
    r"(?:asks?|needs?|uses?|reads?|reports?|gives?|wants?|carries|covers?|leaves?|"
    r"makes?|takes?|looks?|points?|accounts?|calls?|works?|aims?|relies|depends?)\s+"
    r"(?:for|to|of|on|at|with|from|about|against|into|by|upon)\s*(?=[,.;:]|$)", re.I)
```

**Validated in both directions before proposing it (V3, V17).** It fires on the R15-04 clause; it stays silent
on "what the answer depends on", which is legal and appears four times in Chapters 1 and 6. Run over the
comment-stripped text of all 59 live `.tex` files it returns **three hits, and I read all three**:

1. `chapters/apx_f_cosine.tex` — "the update next-category asks for," — **the real defect (R15-04).**
2. `chapters/2_fundamentals.tex` — "the metrics and reference points each result is read against," — same
   shape, milder; inside a four-item list where the reader has more support. Worth the author's eye.
3. `main_extra.tex` — "the reference level one screening argument in the dissertation is read against." —
   same shape, and this one is genuinely hard: three nouns stacked before the reduced clause.

Three hits, no false positives, and the one it exists to catch is a REQUIRED finding. That is a gate worth
adding, and it closes the class rather than the sentence.

(The 59 files are the 54 authored sources `check_register.py` sweeps plus the five generated copies under
`build/fmt/`. None of the three hits falls in a generated copy, so the count is a count of authored prose.)

### Gap 2 — the bare temporal "now" as version narration

`check_process_narration.py`'s version-history rule was written from the deleted sentence's shape:
`an earlier version of this (appendix|chapter|section)`, `originally reported`, and so on. Every pattern names
the earlier version explicitly. A bare "now" performs the same comparison **without naming what it compares
to**, which is what makes it harder to read, not easier, and it is invisible to all five rules (verified).

This one should not be a hard gate — "now" is legitimate in some constructions — but a **warn-level** pattern
would surface it:

```python
# Warn, not fail: a bare "now" whose comparison target is not on the page.
r"\b(?:it|this|the \w+) (?:now|already|no longer) (?:covers|includes|contains|reports|holds|reads|stands)\b"
```

**Measured, and the measurement corrected my first draft of this paragraph.** Over the same 59 files the
pattern returns **two** hits, not one, and I read both:

1. `chapters/apx_f_cosine.tex` — "It now covers" — the R15-06 defect.
2. `chapters/apx_b_static_scope.tex` — "a lookup **it already holds**" — a **false positive**. There "already"
   is not a comparison against an earlier document state; it says the model is handed a mapping it possesses.
   The sentence is correct and must not change.

One true hit against one false positive is why this belongs at warn level and not as a hard gate, and the
false positive shows where a tighter version would go: drop `already` from the alternation, or require the
verb to take the document itself as subject. I also read **all ten** occurrences of "now" in live prose
(1_introduction, 5_mobiwac/02_related, 5_mobiwac/04_method, apx_b_errata, apx_b_static_scope, apx_e_ethics,
apx_f_cosine, tables/cbic/errata, tables/frame/bib_errata ×2). Nine name their comparison or refer to the
world rather than to the document ("Such records now exist at large scale", "the chapter now states", "that
address now redirects"), and are legitimate. Exactly one, `apx_f_cosine.tex`, compares the document against a
version of itself.

### Gap 3 — no gate reads a `\ref` against the volume that builds it

R15-01 is a two-volume defect: the label exists, the file that defines it is not included in the volume that
cites it, and LaTeX reports it as a warning the build's exit code does not carry. `make extra` returned 0 with
`Reference 'apx:cosine' on page 11 undefined` in its log. A check that fails on any `undefined on input line`
in either build log would have caught this before it reached a reader, and would cost one grep.

### What no gate can do

R15-02 — a stale title inside a quotation — is a content-comparison defect. Nothing pattern-based finds it;
only a reader comparing the quoted string against the `\titulo` field forty lines above. A cheap probe exists
though: assert that any quoted string in `main_extra.tex` beginning "the dissertation ``" is a substring of
the `\titulo` argument in `preamble.tex`. Narrow, but it would have held.

---

## 5 · Hard limits observed

Read-only. No `.tex` file was edited. No ban-list enforcement (persona 03's), no sentence-by-sentence stumble
log (persona 01's), no grammar list (persona 02's), no judgment on any number, citation or scientific claim.
Suggested rewrites stay at phrase and sentence scale; where a passage needs restructuring (R15-07) the
restructure is described and the split is shown, not drafted at length.


---

<!-- estado-rodada -->
> **Rodada encerrada · último toque 2026-08-02 · sem autoridade.**
> Este ficheiro é registo de proveniência do que foi discutido nesta passagem, não fonte
> de um facto corrente. O que ficou decidido está em [`VEREDITOS.md`](../../../VEREDITOS.md);
> os valores entregues estão em `CLAUDE.md` §0.1. Não copie nada daqui sem confirmar lá.
