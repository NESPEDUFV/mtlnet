# 15 · Readability editor — professional-editor quality review

> **THIS REPORT SUPERSEDES the 15_readability_editor_report.md dated 2026-07-26**, which was
> written against the 94-page build and is now stale by a full day of edits. That build did not
> contain the rewritten Appendix D, did not contain Appendix E at all, still contained Appendix A.2,
> and had not yet received the MTLnet standardization, the cross-attention rescoping, the
> Markov-floor rewrite, or the 12 pt bibliography. Where a finding from the prior report still
> stands, it is re-verified here against the current source and re-numbered; the prior numbering
> (R-01 … R-07) is mapped in §7 so nothing is silently dropped.

**Read:** `src/dissertacao.pdf` (102 pp, rebuilt 2026-07-27) for the reading experience;
`src/chapters/*.tex` for quoting; `src/0_main.tex` for include order.
**Date:** 2026-07-27. **Persona:** `reviewers/15_readability_editor.md`. **Read-only** — this file
is the only file I wrote.
Science, numbers, and citations assumed correct (personas 05/06/07/09/10/11 own them). I judge the
writing as writing, including what is technically legal but reads poorly.

**The author's charge this round.** The author raised this persona himself, writing of recent
additions that *"da forma como ele tá escrito hoje está confuso; se alguém pega para ler só o
appendix D, ele por si só está bem confuso de ler e difícil de acompanhar."* Appendix D has since
been rewritten. My charge: judge whether the rewrite fixed the two diagnosed defects, and find the
same two shapes elsewhere. The two shapes are (i) **concept collision** — two similar names
alternated for two quantities a passage exists to hold apart, and (ii) **external dependency** — a
term used before, or without, its definition. Sentence length was already ruled out as the cause
and I did not re-litigate it.

---

## 1 · Verdict on Appendix D: the rewrite works, and it left three seams

**The rewrite fixed the defect it was aimed at.** Judged against the two diagnosed shapes:

| Diagnosed defect | Pre-rewrite | Now | Verdict |
|---|---|---|---|
| Concept collision: "ceiling" | 8 uses in 508 words | **2 uses in 928 words**, and both are *meta-mentions* (naming the word as retired), not uses of it as a name | **FIXED** |
| Concept collision: "reference" | 5 uses, unattached to either quantity | 7 uses, of which 6 are inside the registered compound "clean reference encoder" | **FIXED in kind** — see D-2 for the residue |
| External dependency: "screen" | 9 uses, defined only in Chapter 5 | 12 uses, and **the appendix now defines the procedure itself** at `apx_d_ceiling.tex:22-27`, p. 98, in its second paragraph | **FIXED** |

The structural move that did the work is the `description` list at `:31-40` (p. 98): the two
quantities are named side by side, each in one sentence, each told what it is *not*. That is the
right instrument for a concept collision and it is well executed. The two-readings split at `:85`
("Two readings follow from the table, and they point in different directions") is also good
craft: it tells the reader in advance that the next two paragraphs disagree, which is exactly what
a reader of a disambiguation appendix needs.

**A reader picking up Appendix D alone can now follow it.** I tested that directly by reading
pp. 98–100 cold, without Chapter 5 in view. The procedure, the two quantities, the table, and the
two limits all land. That is a genuine improvement and the author's original complaint is answered.

Three seams survive, and one of them is the collision shape reappearing in miniature.

### D-1 (Major) · The appendix opens by invoking the retired word before either quantity exists

`src/chapters/apx_d_ceiling.tex:16-20`, rendered **p. 98**, first paragraph, third sentence:

> "The answer fixes how strong a screening argument in Chapter~\ref{ch:mobiwac} can honestly be,
> because two different quantities have both served as that argument's reference level and have
> both been called the ceiling."

**Why it affects the reader.** This is the third sentence of the appendix and it asks the reader to
hold four unknowns at once: which screening argument, which two quantities, whose reference level,
and who called them the ceiling. None of the four has been introduced. The word *the ceiling*
arrives with a definite article and no referent, and the reader does not learn whose word it was
until `:117` (p. 100), ninety percent of the way through: "Calling it a ceiling, as the internal
screening record does." A reader who stops at the opening paragraph concludes the appendix is about
a naming dispute rather than a measurement.

The irony is precise: the appendix exists to retire a colliding word, and it opens by using that
word as the hook. The rewrite retired *the name* thoroughly and kept *the confession* in the
opening slot.

**Suggested direction.** Move the confession to where its referent already exists. The opening
paragraph needs only its own first two sentences, which are excellent and self-sufficient ("This
appendix answers one question. How much of the next category can be predicted from the category
history of the input window alone, without reading any representation at all?"). The clause about
two quantities having shared a name belongs immediately before or inside the `description` list at
`:29-40`, where both quantities are on the page and the collision becomes concrete rather than
cryptic. No wording need change; only the placement.

### D-2 (Major) · The registered singular becomes an unregistered plural, and its second value arrives cold

The `description` item at `:36-39` (p. 98) defines the quantity in the **singular**, with one pair
of values:

> "**The clean reference encoder.** The encoder that a screened candidate is actually compared
> against … At Florida it is a graph encoder from the same lineage as the representation of
> Chapter~\ref{ch:mobiwac}, at $0.4090$ macro-F1 on standardized features and $0.4074$ on raw ones."

Fifty-five words later, `:93-94` (p. 99) uses the **plural** and introduces a value the appendix
never defined:

> "At Florida the two clean reference encoders score above the benchmark, $0.4090$ and $0.4197$
> against $0.3617$ …"

I verified the numeric set: Appendix D's body contains `0.4074`, `0.4090`, `0.4142`, `0.4197`.
`0.4090`/`0.4074` are introduced in the `description` item; `0.4142` is introduced with the
relation-typed encoder at `:97`; **`0.4197` appears exactly once, at `:94`, with no introduction.**
Its introduction lives in Chapter 5 (`5_mobiwac.tex:376`, p. 66: "the residual variant that the
encoder we ship descends from sits at the same level, $0.4197$ and $0.4182$").

**Why it affects the reader.** This is both diagnosed shapes at once, inside the appendix built to
cure them. A reader who has just been promised "Each is given one name here and keeps it" (`:29`)
meets that name pluralized, with a second member whose identity and value are external. The reader
must either accept `0.4197` on faith or go to Chapter 5 — which is the standalone-readability
failure the rewrite was commissioned to remove. It also silently converts a *definition* into a
*category*: is "the clean reference encoder" one encoder, or a class with two members?

**Suggested direction.** Two clean options, author's choice. Either make the `description` item
plural from the start and name both members there with both values, so the plural at `:93` has a
referent; or keep the item singular and let `:93` compare the single defined reference against the
benchmark, moving the residual variant into the coverage-limits paragraph. The first is probably
truer to the measurement.

### D-3 (Minor) · Two scales alternate inside single sentences

The table and the definitions are on a zero-to-one scale (caption: "All values are macro-F1 on a
zero-to-one scale"). The two verdict paragraphs report differences in **points**: "the screening
margin of three points" (`:88`), "clears the clean reference encoder by $8.9$ points" (`:90`), "a
gap of four to six points" (`:94`). I checked the arithmetic and it is internally consistent
(0.4976 − 0.4090 = 8.9 points; 0.4090 − 0.3617 = 4.7 and 0.4197 − 0.3617 = 5.8, hence "four to
six"), so this is not a number defect. It is a reading defect: within one sentence at `:93-94` the
reader is handed `0.4090` and "four to six points" and must supply the ×100 conversion mentally to
see that they agree.

**Suggested direction.** One sentence early in the appendix, next to the scale statement, saying
that differences are quoted in points, one point being 0.01 on that scale. Cheaper than converting
either set of figures.

---

## 2 · The same two shapes elsewhere: what the sweep found

I swept every chapter and appendix for both shapes. The results, ranked.

### X-1 (BLOCKER, reader-facing) · Chapter 6's "Second," was swallowed into a comment; the sentence renders headless

`src/chapters/6_conclusion.tex:110-111`, rendered **p. 77**.

The comment block at `:104-110` ends with the words `[NEEDS SIGN-OFF: AUTHOR] Second,` — the
enumerator is **inside the comment line**, so LaTeX discards it. Prose resumes at `:111` with a
lowercase fragment. The rendered page reads:

> "… and we do not offer the ablation as evidence that the trunk contributes nothing. **a
> capacity-matched dedicated baseline, run after the Chapter 5 manuscript was submitted** …"

**Why it affects the reader.** The paragraph promises "**Two** controls separate this claim from
wishful attribution. **First,** the freeze control …" and then never delivers the second
enumerator. A sentence begins mid-clause with a lowercase letter after a full stop. This is on the
consolidated-answer page, the single page a busy examiner is most likely to read closely, and it is
the paragraph carrying the dissertation's central attribution claim. A reader who notices it
concludes the document was assembled mechanically; a reader who does not notice it loses the
first/second scaffold and reads the capacity-matched control as a continuation of the ablation
discussion, which inverts its rhetorical role from *supporting* to *qualifying*.

I verified this is a real rendering defect and not an extraction artifact: the source line ends the
comment with `Second,` and the PDF text at p. 77 reads "…contributes nothing. a capacity-matched
dedicated baseline…". This defect was **created this round** — it is at the join between the new
cross-attention rescoping (`:104-110`) and the pre-existing capacity-matched passage.

**Suggested direction.** Move `Second,` out of the comment onto the prose line at `:111` and
capitalize. One-word fix; no content changes. This is the only instance in the document — I swept
all eleven chapter/appendix files for comment lines ending in a sentence-starter immediately
followed by prose and this is the sole hit, so it is a one-line correction and not a class.

### X-2 (BLOCKER, reader-facing) · `\\pm` in inline math renders as a line break plus literal "pm" on p. 73

`src/chapters/5_mobiwac.tex:704`, rendered **p. 73**, first two lines:

Source: `$-0.04 \\pm 0.13$` — two backslashes before `pm` where `\pm` needs one. (Verified on the
raw bytes: `5_mobiwac.tex:704` has `0x5c 0x5c 0x70 0x6d`; `6_conclusion.tex:98` has `0x5c 0x70
0x6d`.) Rendered:

> "moved next-category macro-F1 by −0.04
> 𝑝𝑚0.13, which a paired test cannot separate from zero."

The ± symbol is gone; the reader gets a forced line break inside the math, then the italic letters
*pm* set against the number. The identical clause in Chapter 6 (`6_conclusion.tex:98`, p. 77) is
correct — `$-0.04 \pm 0.13$` renders "−0.04 ± 0.13" — so the two loci of the same rescoped value
now disagree in appearance.

**Why it affects the reader.** A reader who reaches p. 73 sees a typographic failure in the middle
of a hedged claim about an ablation, and the number becomes unreadable: "−0.04" then a break then
"pm0.13" does not parse as a mean and a standard deviation. It reads as a build error, which
undermines the very passage that is being careful. Sweeping the whole source, this is the only
`\\pm` in any chapter, so again a single-site fix.

**Suggested direction.** Delete one backslash at `5_mobiwac.tex:704`, so `\\pm` becomes `\pm`.
Nothing else changes.

Both X-1 and X-2 are in **passages this round created or rescoped**, which is where the round's own
claims most needed auditing. Neither is caught by "0 errors, 0 undefined refs, 0 overfull boxes" —
both compile cleanly and both are visible to any reader.

### X-3 (Major) · Chapter 5's four-grounds paragraph is now 591 words, up from 546

`src/chapters/5_mobiwac.tex:376`, rendered **pp. 66–67**. Re-measured on the same basis the prior
report used (LaTeX stripped, citations and math removed): **591 words in a single unbroken
paragraph**, against 546 in the 07-26 build. The prior report's R-01 recommended breaking it at the
four ground boundaries. Not applied, and the paragraph **grew by 45 words** — the label-history
benchmark material was inserted into it rather than after it.

I am re-raising it rather than restating it, because the growth changed its character. The
paragraph now carries, in one block: four grounds, three coverage limits, two named reference
quantities (the clean reference encoder and the label-history benchmark), five numeric pairs, a
cross-reference to Appendix D, a disclaimer that the benchmark is not an upper bound, and a closing
sentence about what the screen does not establish. The two quantities Appendix D exists to hold
apart are now **introduced in the same 591-word block**, 120 words apart, with "reference" doing
duty for both ("that reference", "clear of the reference", "A second reference", "the clean
reference", "the clean references"). That is the concept-collision shape, at its highest local
density in the document, in the passage an examiner is most likely to interrogate line by line.

**Suggested direction.** Unchanged from the prior round for the first four grounds: break at the
ground boundaries, so the First/Second/Third/Fourth markers become paragraph openers, which is what
they are already trying to be. Additionally, the fourth ground has grown long enough to deserve its
own break at "A second reference can be computed directly from the category sequence" — that is
where the passage stops describing the screen and starts describing the benchmark. No words need
changing; five or six breaks.

### X-4 (Major) · A 16-word paragraph is stranded between two long ones, and it echoes the word it follows

`src/chapters/5_mobiwac.tex:718-719`, rendered **p. 73**:

> "Either way the gain requires no second model at serving time (one model, one forward pass)."

It stands alone as a paragraph. The preceding paragraph (`:686-710`, 386 words) ends: "…and we do
not present the ablation as evidence against it **either**." So the reader meets "either" as the
last word of one paragraph and "Either way" as the first two words of the next.

**Why it affects the reader.** "Either way" is a discourse connective that needs its two ways in
view; as a standalone paragraph it reads as an orphan, and the reader pauses to work out which two
readings are being closed over (the answer is the two limits from the previous paragraph, six lines
up). The word echo makes the pause longer. The sentence itself is a good one and it is doing real
work — it is the serving-cost argument — but it is architecturally homeless.

This paragraph is a residue of this round's rescoping: the rescoped clause (`:702-710`, 130 words)
was inserted *between* the freeze-control discussion and this sentence, so what used to be a
paragraph-final clause is now a paragraph of its own with its antecedent pushed out of reach.

**Suggested direction.** Attach it to the end of the preceding paragraph, or open it with a
concrete subject instead of "Either way" ("The gain requires no second model at serving time,
whichever component supplies it"). Do not delete it.

### X-5 (Major) · "the freeze control" is named in Chapter 6 and never named in Chapter 5

`6_conclusion.tex:92`, p. 77: "First, **the freeze control** reported in Chapter~\ref{ch:mobiwac}".
Chapter 5 describes the experiment at `:687-701` (p. 72) but never calls it that. Its own wording
is "a control shows otherwise", then "We fix the region pathway at its initial values", then "the
control", then "freezing the region stream". The noun phrase *the freeze control* appears **once in
the document, in the chapter that is pointing back at the other one.**

**Why it affects the reader.** This is the external-dependency shape with the arrow reversed: the
frame chapter coins a name for something the source chapter left unnamed, and points at the source
chapter for it. A reader following the pointer to Chapter 5 searches for "freeze control", does not
find it, and has to reconstruct the identification from "we fix the region pathway at its initial
values". A reader who does not follow the pointer may take the freeze control to be a *different*
experiment from the one on p. 72.

Note also `WRITING_LAW.md §2`, which lists "frozen" among the repo words to translate ("write
'fixed', except frozen weights, glossed"). Chapter 5 obeys that rule ("we fix the region pathway");
Chapter 6 does not ("with the region pathway frozen", "the freeze control"). I flag the readability
consequence and hand the law question to persona 03 — the two chapters currently disagree, and
whichever way it resolves, one name should serve both.

**Suggested direction.** Pick one name and use it in both places. If "the freeze control" is the
name the author wants, Chapter 5 should coin it at first use on p. 72 and Chapter 6 can then point
at it; if the law's "fixed" wins, Chapter 6 should say "the control that fixed the region pathway".

### X-6 (Minor) · Three of Chapter 6's contribution paragraphs open with the identical frame

`6_conclusion.tex:32`, `:43`, `:68`, rendered **pp. 76–77**: "Chapter~\ref{ch:cbic} contributed
MTLnet…", "Chapter~\ref{ch:courb} contributed the controlled test…", "Chapter~\ref{ch:mobiwac}
contributed the resolution…". Three consecutive paragraphs, same opener, same verb, same slot.

This is `WRITING_LAW §4.4`'s discourse-skeleton shape rather than a comprehension problem, and in a
"contributions by chapter" section a parallel frame is partly defensible — the parallelism *is* the
information. I rank it Minor for that reason. But three is where a parallel frame stops reading as
deliberate and starts reading as a template, and this is the reader's first section after the
opening summary.

**Suggested direction.** Vary the second or third: lead with the contribution and name the chapter
second ("The controlled test of the representation explanation came from Chapter 4, which held…").
One variation is enough to reset the pattern.

### X-7 (Minor) · Chapter 2's longest paragraphs are unchanged, and one term still collides there

Re-measured, unchanged from the prior round: Chapter 2 runs **26 paragraphs, mean 154.9 words, 10
of them over 150 words, longest 324** (`2_fundamentals.tex:494-521`, the validation-protocol
paragraph, rendered p. 24). The prior report's R-03 recommended breaking it at "The statistical
treatment is scoped the same way"; not applied. I re-verify rather than re-argue.

The collision shape worth adding: **"floor" carries two unrelated senses within twenty-five lines**
of that paragraph. At `:483-485` (p. 24) it is a *reference level* ("the majority-class floor …
is the level a learned category model must clear"; "the corresponding non-learned floor"). At
`:510-511` (p. 25) it is a *numerical limit of a statistic* ("Its exact one-sided $p$ has a floor
set by the number of pairs"). Both are standard usage in their own field and neither is wrong. But
this is the chapter that teaches the vocabulary, and a reader learning that "floor" means
"reference point a model must clear" meets it one page later meaning "smallest attainable p-value".

**Suggested direction.** At `:510` write "a lower bound set by the number of pairs" and reserve
"floor" for reference levels throughout. One word.

### X-8 (Minor) · The 12 pt bibliography reads well; noting it since it changed this round

`src/0_main.tex:393-396`; **pp. 80–86**. The `\footnotesize` wrapper is gone and the 99 entries set
at body size across seven pages. I read all seven: the entries are scannable, the numeric labels
sit clear of the text block, and multi-line entries no longer crowd. This is a straight improvement
in reading experience and I would not revert it. Recorded so the author knows the change was
audited from the reader's side, not just the compliance side.

---

## 3 · Appendix E (new, never reviewed): verdict and findings

**Verdict: the best-organized new prose in the document, with one voice anomaly and two reader
gaps.** Its three sections answer three questions in the order a reader asks them (where did the
data come from, what does it do to real people, was ethics review needed), each section opens with
a purpose-carrying sentence rather than a throat-clear, and its paragraphs are the most consistently
sized in the document (mean 78.9 words, **zero over 150**, longest 142). The honesty pattern that
makes Chapter 5 strong is reproduced faithfully here: every claim is followed by its own limit
("One check is outstanding: the Foursquare product terms were not read, only the license tag on the
distribution"; "That is how a close precedent handled the question, not a determination of the
rule"). Read cold, pp. 101–102 are clear start to finish. No concept collision: I checked the
license/dedication/deposit/record/copy cluster and each term keeps one job.

### E-1 (Major) · The passive rate is roughly triple the frame's, and it obscures who acted

Measured across the eleven files, Appendix E has the **highest passive density in the document**:
20 of its 35 sentences (57 percent) contain at least one passive construction, against 13 per 100
sentences in Chapter 5 and 5 per 100 in Chapter 6. Consecutive examples from `:58-70` (p. 102):

> "this work adds no de-identification of its own. No coordinate **is perturbed, rounded,
> generalized, or masked**, and no formal privacy mechanism **is applied**. Latitude and longitude
> **are used** at the precision the sources publish … User identifiers **are carried** as opaque
> integers … a non-numeric identifier **is replaced** by a position index that **is not kept**."

**Why it affects the reader.** This is the appendix where agency is the subject matter. The reader
wants to know what *the author's pipeline* does and what *the depositor* did, and the passive voice
systematically removes the actor from exactly those sentences. The effect is compounded by the
appendix's own choice to write "the author" in the third person (three times) while every
neighbouring chapter writes "we" (Chapter 5: 104 first-person forms). So the reader gets an
appendix that both distances the author and deletes the agent, in a passage whose credibility rests
on the author taking responsibility. It reads as institutional prose dropped into a dissertation
that elsewhere speaks in the first person.

The contrast within the appendix itself proves the point: the active sentences are its best ones.
"Pseudonymity is not anonymity" (`:51-52`) and "No check-in data is redistributed" (`:72`) land
because they name a state of affairs plainly.

**Suggested direction.** Convert the pipeline sentences to active with a named actor: "The pipeline
perturbs, rounds, generalizes, and masks no coordinate, and applies no formal privacy mechanism."
Leave the provenance sentences passive where the actor is genuinely unknown ("the dedication was
applied by the depositor of this copy" is correct — the actor is named and the passive puts the
dedication in topic position). And decide the person question deliberately: third-person "the
author" is defensible for the human-subjects section, where a formal register is appropriate, but
the pipeline sections should match the chapters. Persona 03 owns whether the law prefers one; I
report that the seam is audible.

### E-2 (Major) · Nothing in the document points to Appendix E

I swept all `.tex` sources: `\label{apx:ethics}` is defined at `apx_e_ethics.tex:8` and
**referenced nowhere**. No chapter, no appendix, and no front-matter passage mentions data ethics,
governance, or licensing with a pointer to it. The word "ethic" appears in exactly one non-comment
line in the whole source tree: the `\include` in `0_main.tex:404`.

**Why it affects the reader.** An appendix nobody points at is read by nobody except a reader
paging to the end. The natural entry points exist and are unused: Chapter 5 §5.5.1 Data (p. 65)
introduces both collections; Chapter 6 §6.3 Limitations (p. 78) discusses the Gowalla vintage and
the transductive constraint; Chapter 1 §1.4 Scope and assumptions (p. 16) states design-time
assumptions. Any one of those would give the appendix a reader. Appendix D, by contrast, is reached
from `5_mobiwac.tex:376` and is therefore discoverable.

There is a second-order effect. Appendix E's licensing account is *finer* than the body's: it
distinguishes the Figshare category-annotated deposit (CC0, the copy actually used) from the older
Stanford release cited as `cho2011gowalla,jure2014snap` (no categories, no stated license). Chapters
3, 4, and 5 all cite the Stanford pair when naming the dataset. Only the footnote at
`5_mobiwac.tex:55` mentions Figshare. So a reader who reads the body learns the dataset is "the
Gowalla dataset [Stanford]", and a reader who finds Appendix E learns that is a different artifact
from the one measured on. The distinction is correct and carefully drawn; it is simply unreachable
from where it matters.

**Suggested direction.** One sentence at the end of Chapter 5 §5.5.1 pointing to Appendix E for
provenance, licensing, and the handling of personal data. Whether the provenance distinction itself
needs to reach the chapters is a citation-integrity question, not mine — handed to persona 05
below.

### E-3 (Minor) · The 2024 precedent cannot be followed

`:84-91` (p. 102): "A comparable dissertation defended in this program in 2024, on location-based
social network data and under the same advisor, was consulted on the point." No citation, no
author, no title. I checked `src/references.bib` (99 entries): there is no `mastersthesis` or
`phdthesis` entry, and no entry matching a UFV dissertation.

**Why it affects the reader.** The paragraph is doing evidentiary work — it is the only external
support for the human-subjects position — and the reader cannot verify it or read it. The
description is specific enough (same program, same advisor, 2024, LBSN data) that the reader knows
a particular document is meant, which makes its absence more conspicuous than a vague appeal would
be. The closing hedge ("That is how a close precedent handled the question, not a determination of
the rule") is exactly right and I would keep it verbatim.

**Suggested direction.** Cite it, or drop the specificity. Persona 05 should rule on whether an
uncited precedent may carry this weight; from the reader's side, either a citation or a plainer
formulation would work.

### E-4 (Minor) · "that label" points backward past a footnote and a four-item list

`:28` (p. 101): "Two qualifications belong with **that label**, and both come from the record
itself." The antecedent is "the Creative Commons CC0 public-domain dedication" at `:20-21`, seven
lines earlier, and between them sit a footnote marker, the four pipeline files, and two sentences
about the category taxonomy. The paragraph is also the appendix's longest (142 words).

**Why it affects the reader.** By the time "that label" arrives the reader has moved on to
taxonomy mechanics, and the referent has to be retrieved. "Label" is also not the word used for it
earlier — it was called a "dedication", and is called a "dedication" again in the very next
sentence. Small, but it is the concept-collision shape in miniature: one thing, two names, four
lines apart.

**Suggested direction.** "Two qualifications belong with that dedication" — matching the word
already in use, which also gives the pronoun a lexical anchor.

---

## 4 · Scores (1–10)

| Dimension | Score | Δ vs 07-26 | One-line justification |
|---|:--:|:--:|---|
| **Readability** | **7** | = | Sentences remain clear individually; Appendix D now readable standalone, but two rendering defects (X-1, X-2) stop a reader mid-claim on pp. 73 and 77 |
| **Coherence and flow** | **7.5** | −0.5 | The arc still reads; this round's insertions left an orphan paragraph (X-4) and a headless sentence (X-1) at the joins |
| **Clarity** | **8** | = | Appendix D's disambiguation is a real gain; offset by the singular/plural reference-encoder slip (D-2) and the unnamed freeze control (X-5) |
| **Conciseness** | **6** | = | Still the weakest dimension: Ch.2 mean 154.9 words/paragraph unchanged, and Ch.5's four-grounds paragraph grew 546 → 591 |
| **Consistency of voice** | **6.5** | −0.5 | Appendix E's 57 percent passive rate and third-person "the author" are the widest voice gap in the frame material |
| **Overall writing quality** | **7.5** | = | Two new appendices of genuinely good prose, two mechanical defects in the changed passages, and the prior round's paragraph-length findings still open |

**On the burstiness question** (`WRITING_LAW §4.3`, which the prior round tested): re-measured, no
compression. Sentence-length coefficient of variation by chapter — Ch.6 0.636, Ch.2 0.560,
Ch.5 0.548, Ch.1 0.543, Ch.4 0.423, Ch.3 0.424 — and the new appendices sit inside the frame's
band (D 0.575, E 0.501), not below it. The most-edited material is still the burstiest. This
round did not smooth.

---

## 5 · What holds — protect these

1. **Appendix D's `description` list** (`:31-40`, p. 98). The instrument that fixed the author's
   complaint. Two quantities, two names, one sentence each, each told what it is not. Do not merge
   these back into running prose.
2. **Appendix D's two-readings split** (`:85-102`, p. 99). "Two readings follow from the table, and
   they point in different directions", then one paragraph per reading, the stronger first, each
   labelled by its own strength ("The screening comparison is unaffected" / "The absolute reading
   is the weaker one"). This is how to write a passage that has to concede something.
3. **Appendix D's two refusals** (`:111-118`, p. 100). "The gap is not by itself evidence of a
   leak." "The benchmark is also not an upper bound." Short, flat, each pre-empting the objection a
   skeptical reader is forming at exactly that moment. Same craft the prior report praised in
   Chapter 5, now in the appendix.
4. **Appendix E's section titles.** "Where the data came from", "Real people, and how the traces
   are handled", "The human-subjects question". Plain, question-shaped, and they tell a reader
   scanning the TOC exactly what is inside. They read better than most of the body's section
   titles.
5. **Appendix E's closing paragraph** (`:78-91`, p. 102). It states a position, states its basis,
   states what it does *not* claim ("It records no approval and no exemption, because none was
   sought and none is claimed"), then names the condition under which it would have to change. That
   is how to write a defensible institutional claim without overclaiming, and it is the paragraph a
   banca member is most likely to probe.
6. **The Chapter 5 Markov-floor rewrite** (`:778-796`, p. 73). The rewrite replaced one causal
   explanation with a two-fact protocol asymmetry and then explicitly declined to resolve it
   ("Neither fact establishes why the floor lies above the three systems, and we do not claim a
   single explanation"). Structurally this is now the clearest passage in the results section: the
   comparison, then fact one, then fact two, then what follows and what does not. The clause "and
   the comparison deserves a direct word rather than being left for the reader to assemble" is the
   author telling the reader he saw the problem, which buys real credit.
7. **The Chapter 3 and Chapter 4 prefaces**, and **Chapter 1's funnel** — re-verified unchanged and
   still the strongest orientation devices in the document.
8. **The 12 pt bibliography** (pp. 80–86). See X-8.

---

## 6 · Chapter-seam verdict: do the papers and the frame read as one voice?

**Unchanged from the prior round for Chapters 1–6, with a new seam inside the back matter.**

- **Chapters 1, 2, 5, 6 still read as one author.** Re-measured: -ly adverb density 0.68 / 0.94 /
  0.61 / 0.66 percent, passive rate 10.6 / 19.7 / 13.0 / 5.3 per 100 sentences. Tight band, same
  habits, same preference for a limit immediately after a claim.
- **Chapters 3 and 4 remain audibly different** and remain correctly flagged as reproductions
  (Ch.3 -ly 1.38 percent, Ch.4 passive 28.7 per 100 sentences — both roughly double the frame).
  The prefaces still absorb it. My judgment is unchanged: nothing to fix.
- **New: the appendices no longer speak with one voice.** Appendices A, B, and D read in the frame
  voice. **Appendix C and Appendix E do not** — both drop "we" for "the author" (C: 4 instances in
  385 words; E: 3 in 821), and Appendix E's passive rate (62.9 per 100 sentences) is nearly five
  times Chapter 5's. Appendix C's register is defensible: a disclosure statement is a formal
  instrument. Appendix E's is a mixture: its human-subjects section reads like a compliance
  document, which suits it, and its pipeline sections read like one too, which does not — those
  describe things the author's own code does or does not do, and the chapters describe such things
  in the first person.

  **Verdict:** the body reads as one document. The back matter now reads as two registers, and the
  boundary falls inside Appendix E rather than between appendices. Worth one deliberate decision
  from the author rather than a rewrite.

---

## 7 · Disposition of the prior report's findings

Audited against the current source rather than accepted as fixed.

| Prior | Locus | Then | Now | Status |
|---|---|---|---|---|
| R-01 | `5_mobiwac.tex:376`, pp. 66–67 | 546-word paragraph | **591 words**, +45 | **OPEN, worse** → re-raised as X-3 |
| R-02 | `6_conclusion.tex:14-22`, p. 76 | 110-word opening sentence | **110 words**, unchanged | **OPEN** — still the first sentence an examiner reads; prior suggestion (split after "three studies") stands |
| R-03 | `2_fundamentals.tex`, pp. 20–26 | mean 154, 10 over 150, longest 324 | **mean 154.9, 10 over 150, longest 324** | **OPEN**, unchanged → re-raised with an addition as X-7 |
| R-04 | `5_mobiwac.tex:414`, p. 67 | 315-word statistics paragraph | **310 words** | **OPEN**, materially unchanged |
| R-05 | `5_mobiwac.tex:411` | Table 9 vs Table 10 column confusion | text unchanged | **OPEN** (Minor; persona 04 also holds it) |
| R-06 | `5_mobiwac.tex:60`, p. 59 | forward-referenced floats | unchanged | **OPEN** (recorded friction, not a defect) |
| R-07 | `5_mobiwac.tex:398`, `:400` | two long baseline sentences | unchanged | **OPEN** (lowest priority) |

None of the prior round's seven findings were applied. That is a legitimate outcome — the author
gates each finding and the round's effort went to fact-level corrections — but it means the
paragraph-architecture findings are now one round older, and R-01 has grown. Note that R-01 to R-04
are all **break-insertions, not rewrites**: no words change. Open question 1 from the prior report
(whether re-paragraphing reproduced Chapter 5 prose counts as an errata-listable departure) is still
unanswered and still blocks the cheapest four fixes in this report.

---

## 8 · Reader-experience map (102-page build)

| Where | Experience |
|---|---|
| pp. 13–17 (Ch.1) | **Effortless.** The funnel works |
| pp. 18–26 (Ch.2) | **Dense but navigable.** Section purpose statements save it; the 154-word mean paragraph slows it; the "floor" double sense on pp. 24–25 costs one stop |
| pp. 27–42 (Ch.3) | **Different voice, clearly flagged.** Readable |
| pp. 43–57 (Ch.4) | **Translation register.** Occasionally effortful, never unclear |
| pp. 58–65 (Ch.5 setup) | **Strong** |
| pp. 66–67 | **The hard patch.** The 591-word four-grounds paragraph; two reference quantities introduced 120 words apart |
| pp. 69–72 (Ch.5 results) | **Strong.** The freeze-control passage is careful and readable |
| **p. 73** | **Stops the reader twice**: the broken ± (X-2) in line 2, then the orphan "Either way" paragraph (X-4). The Markov-floor rewrite below them is the page's best writing |
| pp. 74–75 (Ch.5 close) | **Clear** |
| pp. 76–79 (Ch.6) | **Strong after the 110-word opening**, until **p. 77**, where the headless "a capacity-matched dedicated baseline" (X-1) lands on the central attribution claim |
| pp. 80–86 (bibliography) | **Improved.** 12 pt is the right call |
| pp. 88–97 (Apx A–C) | **Clear.** Appendix B remains unusually readable for an errata document; A now reads as one unsectioned statement, which is fine |
| **pp. 98–100 (Apx D)** | **Readable standalone — the rewrite worked.** Costs: a cryptic third sentence (D-1) and one uninitialized value (D-2) |
| **pp. 101–102 (Apx E)** | **Clear and well organized**, in a noticeably more impersonal voice than everything before it |

**Where a reader would get confused, ranked:** (1) p. 77, the headless sentence; (2) p. 73, the
broken ±; (3) pp. 66–67, the four grounds and the two reference quantities; (4) p. 98, "have both
been called the ceiling" with no referent; (5) p. 99, "the two clean reference encoders" after a
singular definition; (6) pp. 72 → 77, the freeze control under two names.

---

## 9 · Open questions only the author can answer

1. **Is break-insertion inside reproduced Chapter 5 prose within the errata policy?** Carried over
   from the prior round, still unanswered, and it gates X-3 and prior R-04. Chapter 5 is a submitted
   paper; if re-paragraphing is a listable departure, Appendix B needs an entry, and if it is not,
   four findings close for free.
2. **Which name for the freeze control** (X-5), given that `WRITING_LAW §2` asks for "fixed" rather
   than "frozen" outside glossed frozen weights?
3. **Should Appendix E speak as "we" or as "the author"** (E-1), and should that answer differ
   between its pipeline sections and its human-subjects section?
4. **Where should Appendix E be pointed at from** (E-2)? My reading says Chapter 5 §5.5.1; Chapter 1
   §1.4 and Chapter 6 §6.3 are also plausible.
5. **Is "the clean reference encoder" one encoder or two** (D-2)? The answer decides which of the
   two suggested fixes applies.

---

## 10 · Out-of-scope handoffs

- **Persona 03 (style gate):** X-1 and X-2 are rendering defects in changed passages, not caught by
  the build's zero-error state; "frozen"/"the freeze control" in Ch.6 against `WRITING_LAW §2`;
  Appendix E's person and passive register.
- **Persona 04 (concordance):** the freeze control under two names (X-5); the two-conventions
  Table 9 / Table 10 seam (prior R-05, still open); `0.4197` used in Appendix D and defined only in
  Chapter 5 (D-2).
- **Persona 05 (citations):** the uncited 2024 UFV dissertation carrying the human-subjects
  argument (E-3); whether the Figshare-versus-Stanford provenance distinction drawn in Appendix E
  must also reach Chapters 3, 4, and 5, which cite `cho2011gowalla,jure2014snap` when naming the
  dataset (noted under E-2).
- **Persona 06 (numbers):** the zero-to-one versus points scale alternation in Appendix D (D-3) — I
  verified the arithmetic is consistent and raise it only as a reading matter.
- **Persona 07 (claims):** Appendix D's comment at `:107-108` records that `5_mobiwac.tex:376`
  "still asserts 'Every encoder screened … sits above'" and was reported for narrowing, not edited.
  Two files now describe the same measurement at different strengths; that is a claim question, not
  a readability one.
- **Persona 13 (UFV compliance):** Appendix E makes institutional claims about ethics review and is
  marked `[NEEDS SIGN-OFF: AUTHOR]` in its source header.
- **Persona 18 (visual):** the forced line break inside the math on p. 73 (X-2) is also a
  typographic defect; Appendix D's table sets at `\footnotesize` while its body is 12 pt.

**Not checked, and I am saying so rather than implying coverage:** I did not re-read Chapters 3 and
4 line by line this round (unchanged apart from the MTLnet spelling, which I verified separately:
28 correct `MTLnet` against 2 residual `MTLNet` in Ch.4, both of which are the *expansion* "Spatial-
Temporal MTLNet" inside the registered name `ST-MTLNet` at `:38` and `:248`, so they are correct per
`GLOSSARY §2` and not misses). I did not evaluate figures, tables, or float placement beyond the
reading breaks they cause. I did not verify any number, citation, or scientific claim.


---

<!-- estado-rodada -->
> **Rodada encerrada · último toque 2026-07-27 · sem autoridade.**
> Este ficheiro é registo de proveniência do que foi discutido nesta passagem, não fonte
> de um facto corrente. O que ficou decidido está em [`VEREDITOS.md`](../../../VEREDITOS.md);
> os valores entregues estão em `CLAUDE.md` §0.1. Não copie nada daqui sem confirmar lá.
