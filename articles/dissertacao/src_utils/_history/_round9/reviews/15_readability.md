# 15 · Readability editor — round 9

**Persona:** `reviewers/15_readability_editor.md` (professional academic editor; ten lenses; craft, not law enforcement).
**Build commit:** `901a0408`
**Date:** 2026-07-30, 08:41–09:14 local (wall-clock checkpoint hit; see UNFINISHED).
**Scope as assigned:** frame chapters only — Ch. 1, Ch. 2, Ch. 6. Chapters 3–5 not read (reproductions).

**What I actually read**
- `src/build/main.pdf`, pages 12–28 and 78–85, extracted to text and read in full. Page 28 (Ch. 3 preface + §3.1 ¶1) and pages 82–85 (references) were inside the extracted range and are used only where cited below.
- Sources, read in full: `src/chapters/1_introduction.tex` (all 304 lines, including comments), `src/chapters/6_conclusion.tex` (all 348 lines).
- Source, read in the regions cited: `src/chapters/2_fundamentals.tex` lines 9–45, 160–185, 228–250, 383–470, 615–640, 700–790, 842–898, plus targeted greps across all 909 lines.
- Law files read first, in the required order: `AGENT_GUARDRAILS.md` §0–§4 (lines 1–140), `WRITING_LAW.md` (all 193 lines), `reviewers/15_readability_editor.md`. **`GLOSSARY.md` and `NORTH_STAR.md` were NOT read** — see UNFINISHED. No finding below rests on either.

**Exact commands run** (no build, no gate, per instruction)
```
date; git log -1 --format='%H %ai %s'
ls; ls reviewers/; ls -la src_utils/_history/_round9/reviews/
wc -l AGENT_GUARDRAILS.md WRITING_LAW.md GLOSSARY.md NORTH_STAR.md reviewers/15_readability_editor.md
find src -name '*.tex' | sort ; ls -la src/build/*.pdf
git status --porcelain | head -30 ; stat -f '%N %Sm' src/build/main.pdf
wc -l src/chapters/1_introduction.tex src/chapters/2_fundamentals.tex src/chapters/6_conclusion.tex
cat -n src/chapters/1_introduction.tex
sed -n '1,180p' src/chapters/6_conclusion.tex | cat -n
sed -n '180,348p' src/chapters/6_conclusion.tex | cat -n
awk 'NR>=N1 && NR<=N2 && $0 !~ /^%/ {printf "%d| %s\n", NR, $0}' src/chapters/2_fundamentals.tex     # for the line ranges listed above
grep -n <patterns listed inline in the findings> src/chapters/{1_introduction,2_fundamentals,6_conclusion}.tex
python: pypdfium2 → per-page get_text_range() over src/build/main.pdf; pages 12-29 + 78-86 written to handoff/frame_pages.txt; em-dash and contraction counts computed on that slice only
```
Severity vocabulary: the parent's (blocker / should-fix / nit). My persona's own labels (Critical / Major / Minor / Strength) are given in brackets so the mapping is visible.

---

## Blockers

**None.** I found no passage in Chapters 1, 2, or 6 that defeats comprehension. Every sentence I read parses, and every argument I followed arrived. This is an honest empty section, not a courtesy: the frame prose is above the bar where a reader gives up. The nearest thing to a blocker is SF-1, and a reader still gets the list.

---

## Should-fix

### SF-1 [Major] — The chapter list on p. 15 has no stem sentence; the reader falls into the bullets
**WHERE:** PDF p. 15 (rendered); `src/chapters/1_introduction.tex:207-227`
**WHAT:** rendered text, verbatim, across the break:
> "...and any correction applied afterward is listed in the errata appendix of the supplementary volume of this dissertation rather than silently edited.
> • Chapter 2 consolidates the background the three articles share:..."

The stem exists but is commented out, at `1_introduction.tex:225`:
> `% The collection is organized as follows:`

**WHY:** Lens 2 (coherence) and lens 10 (reader experience). §1.5's one and only job is to hand the reader the map of the document, and its list arrives with no grammatical or rhetorical lead-in. The preceding sentence is about errata practice, so the first bullet reads for a half-second as a continuation of the errata sentence. This is the highest-traffic navigational moment in the volume after the abstract. The source comment at `:216-224` shows the defect was found in round 7 and deliberately left, on the ground that the pass had to leave the PDF byte-identical; that reason has expired now that this round is editing prose.
**FIX:** Move the sentence at `:225` out of the comment block, above `\begin{itemize}`. Author's call on whether the page-count re-measure is wanted in this round.

### SF-2 [Major] — One load-bearing concept, five names across the frame
**WHERE:** `1_introduction.tex:126`; `2_fundamentals.tex:226`, `:856`, `:886`; `6_conclusion.tex:59`, `:219`
**WHAT:** the same claim, named differently each time:
> `1_introduction.tex:125-126`: "the input representation, not the sharing architecture, was the **bottleneck**."
> `2_fundamentals.tex:226`: "it is this change to the representation, rather than any change to the architecture, that **moves the results**."
> `2_fundamentals.tex:856`: "Here the representation is **the lever**."
> `2_fundamentals.tex:886`: "whether the representation, rather than the architecture, is **the lever**"
> `6_conclusion.tex:58-59`: "the input representation, not the sharing scheme, was the **binding constraint** at that stage of the research."
> `6_conclusion.tex:219`: "one worked path between those poles, with the **decisive variable** named and tested."

**WHY:** Lens 3 (clarity) and lens 6 (consistency of voice). This is the single most important assertion in the dissertation, and a reader cannot tell from the wording whether "the bottleneck", "the lever", "the binding constraint" and "the decisive variable" are one claim restated or four related claims of different strength. "Bottleneck" and "binding constraint" carry a causal commitment; "the lever" is an instrument; "moves the results" is an observation. A committee member who reads Ch. 1 and Ch. 6 back to back will ask which one the author means. `WRITING_LAW.md` §2 independently requires one name per concept for the whole document; I raise it here as craft, not as ban-list enforcement (persona 03 owns that).
**FIX:** Pick one noun phrase and use it at all six loci. "The binding constraint" is the most defensible aloud and is already the one Ch. 6 uses at the diagnosis. Author's call on which.

### SF-3 [Major] — §6.2's two-controls paragraph is an eleven-sentence block; "Second," arrives after a four-sentence digression the text then disowns
**WHERE:** PDF pp. 79–80; `6_conclusion.tex:110-192`
**WHAT:** the paragraph opens
> "Two controls separate this claim from wishful attribution. First, the freeze control reported in Chapter 5:..."

and then, before "Second," ever appears, inserts:
> "The control does not say which part. A development ablation at Florida removed the cross-attention stack alone and moved next-category macro-F1 by −0.04 ± 0.13, but that measurement was taken on an earlier configuration whose region head was driven by a transition prior the models reported here do not use, and its own record reads the null as a compensation effect rather than an absence of contribution. We therefore do not name the shared trunk as the source, and we do not offer the ablation as evidence that the trunk contributes nothing."

**WHY:** Lens 8 (paragraph quality: one main idea) and lens 1 (no re-reading). The paragraph runs from p. 79 well into p. 80 and holds four distinct items: the freeze control, a disowned ablation, the Alabama capacity-matched baseline, and the California run. The 60-word ablation sentence carries three subordinate clauses and ends by withdrawing its own evidential value, so the reader spends effort on a measurement that is then set aside — and by the time "Second," arrives, "First," is two hundred words back. The content is careful and should stay; the container is wrong.
**FIX:** Three paragraphs: (i) the freeze control and what it does not locate, ending at "The control does not say which part."; (ii) the disowned ablation, or push it to a footnote since its only function is to forestall an objection; (iii) "Second, a capacity-matched dedicated baseline..." through the California run. No sentence needs rewriting for this.

### SF-4 [Major] — "each method named in the next paragraph" points at the wrong paragraph
**WHERE:** `2_fundamentals.tex:424-426`; PDF pp. 22–23
**WHAT:**
> "over $K$ tasks at shared parameters $\boldsymbol{\theta}$, and each method named in the **next paragraph** is a different answer to how the weights $w_k$, or the update direction they imply, should be set."

The next paragraph (`:433-450`) is about Pareto stationarity and guarantee strength. The paragraph after that (`:494-503`) is about the gradient-cosine measure. The methods that are "a different answer to how the weights should be set" — uncertainty weighting, GradNorm, dynamic weight averaging, PCGrad, CAGrad, Nash-MTL, Aligned-MTL, FAMO — are named three paragraphs later, at `:525` ff. (PDF p. 23), beginning "A family of methods tries to manage the conflict at the level of the gradients or the losses."
**WHY:** Lens 3 (clarity: no reference interpretable two ways) and lens 2. A reader who follows the pointer literally lands on a paragraph about convergence guarantees and has to decide whether the author meant it. Nash-MTL, CAGrad, Aligned-MTL and PCGrad *are* named in the immediately following paragraph, which is exactly what makes the pointer ambiguous rather than plainly wrong.
**FIX:** "and each of the balancing methods below is a different answer to..." — a pointer that does not commit to a distance. Alternatively move Eq. 2.4 down to head the balancer paragraph.

### SF-5 [Major] — MTL is defined twice in adjacent chapters, six pages apart, with different capitalization
**WHERE:** PDF p. 22 (`2_fundamentals.tex:386-388`) and PDF p. 28 (Ch. 3 §3.1 ¶1)
**WHAT:**
> Ch. 2: "**Multi-task learning** (MTL) trains one model on several related tasks at once, in the expectation that a representation shared among them generalizes better than one learned for a single task in isolation [7]."
> Ch. 3: "**Multi-Task Learning** (MTL) is a machine learning paradigm where multiple related tasks are learned jointly, sharing representations and inductive biases to improve generalization performance [7]."

**WHY:** Lens 4 (redundancy) and lens 6 (the stylistic seam between re-typeset papers and frame prose, which is this persona's assigned seam). Same citation, same content, two definitions and two capitalizations within six pages. Chapter 2's stated purpose is to de-duplicate exactly this. A reader arriving at p. 28 is told a second time what MTL is, in a different voice, which is the clearest signal in the frame that the document is three papers plus a wrapper.
**FIX:** Chapter 3 is a reproduction and its prose cannot be restyled, so the fix belongs on the frame side: either the Ch. 3 preface acknowledges that the article restates definitions Chapter 2 has already given, or Ch. 2 §2.3's opening sentence is reshaped so the two do not read as competing definitions. Author's call; this is the kind of cut persona 14 gates.

### SF-6 [Major] — the semicolon-chain roadmap survived in Ch. 2 after today's edit removed the parallel one from Ch. 1
**WHERE:** `2_fundamentals.tex:12-20` (PDF p. 17); compare `1_introduction.tex:57-58` (the recorded FAB-16 edit)
**WHAT:** Chapter 2's second sentence, one sentence, four semicolons, five clauses:
> "It defines the prediction tasks and keeps them distinct (Section 2.1); follows the line of representations for mobility from one-hot identifiers to the check-in level (Section 2.2); reviews multi-task learning and the conditions under which it helps or hurts (Section 2.3); states the datasets and metrics, and the validation protocol of the final study (Section 2.4); and closes by drawing these together into the question the following chapters answer (Section 2.5)."

The Ch. 1 comment at `1_introduction.tex:57-58` records the opposite decision, taken today:
> "The semicolon before "this dissertation does not address it" is gone: he read it as an AI tell, and WRITING_LAW §4 bans semicolon braids independently. Now two sentences."

The same construction also stands at `2_fundamentals.tex:879-882` ("...built for these targets; it has multi-task learning but almost no treatment of the next region as an end target; and it has...") and `:845` and `6_conclusion.tex:216`.
**WHY:** Lens 6 (consistency) and lens 9 (repeated sentence structures). This is a hand-edit seam of the kind I was asked to look for: the fix was applied at the reported locus and not to the same construction one chapter later, so the document is now internally inconsistent about a device the author has explicitly ruled against. The Ch. 2 instance is also the more exposed of the two, being the chapter's opening move.
**FIX:** Break the roadmap after Section 2.2 into a second sentence. The five-item chain is legible but monotone, which is the specific quality the author objected to in Ch. 1.

### SF-7 [Major] — the "Two <plural noun> <verb>" opener runs six times in the frame
**WHERE:** `2_fundamentals.tex:82`, `:164`, `:445`, `:624`; `6_conclusion.tex:48`, `:110`
**WHAT:**
> `2_fundamentals.tex:82`: "**Two observations** from that line matter downstream."
> `2_fundamentals.tex:164`: "**Two qualifications** belong with that use."
> `2_fundamentals.tex:445`: "**Two of these papers** state the residual limitation themselves:"
> `2_fundamentals.tex:624`: "**Two check-in datasets** serve as the ground."
> `6_conclusion.tex:48`: "**Two qualifications** bound what that number licenses."
> `6_conclusion.tex:110`: "**Two controls** separate this claim from wishful attribution."

Adjacent to the same skeleton: `1_introduction.tex:157` "Four specific objectives structure the work"; `6_conclusion.tex:224` "Six limitations bound the scope of these conclusions."
**WHY:** Lens 9 (repeated sentence structures, cadence) and lens 6. Twice is a habit; six times in two chapters is a template, and "Two qualifications" appears verbatim as a paragraph opener in both Ch. 2 and Ch. 6. Read aloud, the frame develops a tic: announce the count, then enumerate. `WRITING_LAW.md` §4.4 names discourse-skeleton reuse as the tell that shows most across a long document, which is corroboration rather than my basis.
**FIX:** Keep two or three, including the "Two controls" one where the count genuinely orients the reader, and let the others begin with their content ("Huang et al. present HGI as...", "Gowalla is the dataset of record..."). No claim is affected.

### SF-8 [Major] — the Wilcoxon/paired-*t* sentence in §2.4 asks a reader to hold four things at once
**WHERE:** `2_fundamentals.tex:773-778`; PDF p. 25
**WHAT:**
> "Its exact one-sided $p$ has a floor set by the number of pairs, so a superiority claim tested on four repetitions is reported with a paired $t$ on the per-repetition means and the Wilcoxon test alongside it, on the individual folds (Chapter 5); either test licenses the verb "outperforms", and the Holm step-down procedure controls the family-wise error when several datasets are tested at once [69]."

**WHY:** Lens 1 (no re-reading) and lens 5. One sentence, roughly seventy words, carrying: a property of the Wilcoxon *p*-value, the consequent choice of two tests, the two different units those tests run on (per-repetition means versus individual folds), a chapter pointer, a verb-licensing rule, and a multiple-comparison correction. This is the most consequential methodological sentence in the fundamentals chapter and the one most likely to be quoted at a defense; it should be the easiest to follow, and it is the hardest in the chapter. §2.4 elsewhere handles the same job well (the macro-F1 and Acc@10 definitions are models of the pattern).
**FIX:** Three sentences: the *p*-floor and its consequence; the two tests with their units; then Holm. The parenthetical "(Chapter 5)" can move to the end of the second sentence.

### SF-9 [Major] — first person appears three times, only in Ch. 6, in an otherwise impersonal document
**WHERE:** `6_conclusion.tex:119-120` and `:205`; PDF pp. 79–80
**WHAT:**
> `:119-120`: "**We** therefore do not name the shared trunk as the source, and **we** do not offer the ablation as evidence that the trunk contributes nothing."
> `:205`: "...over four seeds on four Gowalla states, three of which are among the five **we** report, directional conflict only..."

Chapters 1 and 2 contain no first-person pronoun in prose (verified by grep across both files, comments excluded); they use "this dissertation", "the work reported here", "this author".
**WHY:** Lens 6 (consistency of voice). The three occurrences cluster in the two most argumentative paragraphs of the conclusion, where the voice shifts to a defensive first person exactly as the text is withholding an attribution. The shift is legible but it marks those sentences as a different register from everything around them, and a reader notices the change before noticing what is being conceded.
**FIX:** "This dissertation therefore does not name the shared trunk as the source, and does not offer the ablation as..."; "three of which are among the five reported here". Neither substitution moves a claim. If the author wants the first person for the concession specifically, that is a defensible choice, but then it should be the deliberate exception and Ch. 1 and 2 should be checked for whether they want it too.

### SF-10 [Major] — §2.5 states the three-part gap three times
**WHERE:** `2_fundamentals.tex:845-849`, `:851-861`, `:867-877`, `:879-895`; PDF pp. 26–27
**WHAT:** the section's own purpose statement, then the argument, then the hinge, each covering the same three points. Third statement, verbatim:
> "That question presses because its parts have not been brought together. The field has a place-level representation but not a check-in-level one built for these targets; it has multi-task learning but almost no treatment of the next region as an end target; and it has strong evaluation practice that mobility studies do not always apply."

Its clause 1 restates `:857-861` ("...any place embedding assigns a place the same vector on every visit"); its clause 2 restates §2.3's own closing at PDF p. 24 ("no multi-task model among them predicts the next region as a co-equal end target alongside the next category"); its clause 3 restates `:872-875`.
**WHY:** Lens 4 (redundancy). Reading §2.5 straight through, the reader receives the same three-item gap statement in three consecutive paragraphs at increasing compression. Each paragraph is well made in isolation; together they are one argument delivered three times, and the section is the last thing before Chapter 3, where reader patience is thinnest.
**FIX:** I flag, I do not assume this is cuttable — the project's own chapter spec mandates the closing "pressing need" hinge, so the hinge paragraph at `:879-895` stays. The candidate for compression is the middle paragraph's recap of the representation argument (`:857-861`), which §2.2 already made twice. **Author's call**, and persona 14 gates any cut here.

### SF-11 [Major] — "A fourth task also appears" arrives immediately after the set of three is closed
**WHERE:** `1_introduction.tex:64-73`; PDF p. 12
**WHAT:**
> "...is a third and different problem, not addressed in this dissertation. Chapter 2 keeps the three tasks formally distinct.
> A fourth task also appears in this dissertation: the first two studies paired next category prediction with the static classification of a place's category, category classification, and Section 1.2 explains why the final study replaced it. Next category and next region were chosen for what a mobility-aware service can act on, and both are established end targets in the literature on the way to the harder next-place problem."

**WHY:** Lens 2 (coherence) and lens 8 (one idea per paragraph). The previous paragraph ends by sealing the inventory at three; the next opens by adding a fourth, so the paragraph reads as a correction of the sentence before it. The paragraph then changes subject in its second sentence, from the fourth task to the rationale for choosing the two main ones, which are different jobs. A reader finishes it unsure how many tasks the dissertation has.
**FIX:** Either fold the fourth task into the inventory paragraph before the "Chapter 2 keeps the three tasks formally distinct" seal, or reopen the paragraph so the addition is framed rather than announced: "The first two studies also predicted a non-sequential fourth target, the static classification of a place's category, and Section 1.2 explains why the final study replaced it." Then give the task-choice rationale its own paragraph or attach it to the inventory.

### SF-12 [Major] — the opening sentence changes referent across its own colon
**WHERE:** `1_introduction.tex:33-38`; PDF p. 12 (first sentence of the volume's body)
**WHAT:**
> "Location-based social networks let **a person** announce where **they** are: a check-in records that **users** visited a given place, a point of interest (POI), at a given time."

**WHY:** Lens 3 (clarity: no ambiguous references) and lens 10. This is the hand edit recorded at `:34-36` (FAB-12, today). The plural is right for the second half, but the sentence now travels from "a person / they" to "users" across the colon, and the second half reads as though it explicates the first when its subject has changed. The first sentence of the body is the one place where the reader has no context to absorb a wobble. The author's stated reason for the edit is sound; the seam it left is in the half he did not touch.
**FIX:** Make the halves agree: "Location-based social networks let people announce where they are: a check-in records that a user visited a given place, a point of interest (POI), at a given time." — or keep "users" and open with "let their users announce where they are". Either keeps the advisor's plural.

---

## Nits

### N-1 [Minor] — the FAB-13 sentence reads heavier than the one it replaced
**WHERE:** `1_introduction.tex:59-60`; PDF p. 12
**WHAT:** "The two properties above are the two prediction tasks that are the object of study of this dissertation."
**WHY:** Lens 5 (conciseness) and lens 9. "two ... two" in one clause, then a relative clause ("that are the object of study of") doing work a verb could do. It also equates properties with tasks, where the properties are what the tasks predict. The comment at `:55-56` records this as the author's own wording, chosen for precision about what the tasks are *to* the document, and that intent is legitimate.
**FIX:** "The two properties above define the two prediction tasks this dissertation studies." **Author's call** — he chose the current form deliberately, and my note is only that it now reads as the heaviest sentence in the paragraph.

### N-2 [Minor] — the HGI sweep sentence puts six numbers into a background section
**WHERE:** `2_fundamentals.tex:170-174`; PDF p. 19
**WHAT:** "The sweep that fixed that value ran on Alabama over four settings of the weight, 0.4, 0.5, 0.6, and 0.7, each measured over five folds with a budget of 50 epochs, and the category F1 rose monotonically across them, from $0.7388 \pm 0.0205$ at the published setting to $0.8186 \pm 0.0123$ at the adopted one, on a zero-to-one scale, with the spread taken across the five folds."
**WHY:** Lens 5 and lens 10. Roughly 65 words and six numeric values in a section whose job is to trace a line of representations. The *fact* that the baseline was retuned belongs here and is the honest thing to say; the sweep grid, the epoch budget and the scale note read as a methods appendix that has drifted forward, and they slow the one section a reader most needs to move through.
**FIX:** Keep the first clause and the two endpoint values in the body; move the grid, the epoch budget, and the scale/spread conventions to a footnote. No number changes.

### N-3 [Minor] — "Two check-in datasets serve as the ground."
**WHERE:** `2_fundamentals.tex:624`; PDF p. 24
**WHY:** Lens 9 (grammatical but unnatural). "Serve as the ground" leaves the reader to supply "the ground *for what*"; "the ground" is not idiomatic in this position without a complement.
**FIX:** "The dissertation evaluates on two check-in datasets." (also removes one instance of SF-7.)

### N-4 [Minor] — "That stance only pays off if..."
**WHERE:** `2_fundamentals.tex:855`; PDF p. 26
**WHY:** Lens 6 (register). A transactional metaphor inside the chapter's most formal argumentative paragraph; the surrounding sentences are plain and declarative, so this one lands in a different key. `WRITING_LAW.md` §4 covers money metaphors and persona 03 owns that list — I raise it only as the register seam I can hear.
**FIX:** "That stance is only tenable if the model can represent a visit well enough to serve both."

---

## Strengths (protect these)

1. **§2.2's central formulation.** PDF p. 21: "Where a place embedding answers "what is this place," a check-in-level representation answers "what is this visit," and Chapter 5 develops this representation and the joint model built on it." This is the clearest sentence in the frame; it does in one line what the surrounding two pages argue, and it is the sentence a committee will remember. Do not touch it.
2. **§2.3's Pareto-guarantee paragraph** (`2_fundamentals.tex:433-450`, PDF p. 23). Difficult material — necessity versus sufficiency, per-method guarantee strength, then an explicit renunciation — delivered in short declaratives with the concession last: "This dissertation therefore claims no Pareto property of any kind for its models." Rhythmically the best-built paragraph I read.
3. **§6.5 Final remarks** (PDF p. 81). Four sentences, no summary of the summary, and it closes on a claim rather than a restatement: "The negative result was not an obstacle on the way to the contribution; worked through, it was the contribution's first half."
4. **Table 1 and its lead-in** (`2_fundamentals.tex:298-311`, PDF p. 21). The paragraph explaining that the joint model is a specialization of the MTLnet class, overriding one component, does real work: it is what makes the Ch. 3 null and the Ch. 5 positive comparable, and it says so.
5. **§6.3's limitation-to-future-work mapping** (PDF p. 81). Six limitations, then a future-work paragraph that answers each by number. Unusually easy to audit as a reader.

---

## Scores (1–10)

| Lens | Score | One-line justification |
|---|---|---|
| Readability | 7 | Sentences are clear individually, but four passages (SF-3, SF-8, N-2, and §2.4's protocol block) exceed what a single sentence should carry. |
| Flow | 7 | The Ch. 2 spine is well ordered and each section opens with its purpose; SF-11's fourth task and SF-4's mis-pointer are local breaks, and SF-1 drops the reader into a list. |
| Clarity | 6 | Lowered by SF-2: the document's central claim has five names, so the reader cannot fix its strength. Otherwise references and antecedents resolve. |
| Conciseness | 7 | Little filler and no padding, but the frame repeats its own gap statement (SF-10) and re-defines MTL across the seam (SF-5). |
| Consistency | 6 | Three seams: first person only in Ch. 6 (SF-9), a device banned in Ch. 1 today and left in Ch. 2 (SF-6), and one skeleton reused six times (SF-7). |
| **Overall writing quality** | **7** | Prose a banca will respect: honest, controlled, with real sentences and no inflation. What holds it at 7 rather than 8 is that the seams are all in the connective tissue the frame exists to provide. |

## Chapter-seam verdict

**Partially.** I can only report on the seam I was given pages for: Ch. 2 → Ch. 3 at PDF pp. 27–28. Across it, the two voices are distinguishable within one paragraph. The frame writes short declaratives and defines a term once ("Multi-task learning (MTL) trains one model on several related tasks at once"); the reproduced article writes the longer nominal style of a conference introduction and defines the same term again in different words and capitalization ("Multi-Task Learning (MTL) is a machine learning paradigm where..."), and glosses POI a second time inline. The Ch. 3 preface is doing its job well and reads in the frame's voice, so the transition is managed rather than abrupt — but the answer to "do these read as one author?" at this seam is no, and SF-5 is the concrete instance. **I did not read the Ch. 4 → Ch. 5 → Ch. 6 seams and cannot report on them**; Chapters 3–5 were outside my assigned scope.

## Scope note

The narrowing was right for the clock and wrong for one deliverable: my persona's output contract requires a chapter-seam verdict, and that verdict needs both sides of at least two seams. I got one seam only because p. 28 happened to fall inside the extracted range. If this persona runs again, either grant the first page and last page of each paper chapter, or drop the seam verdict from its contract.

---

## COUNTS

**blockers 0 / should-fix 12 / nits 4** (plus 5 strengths, not counted)

## UNFINISHED

I hit the 30-minute checkpoint at finding SF-12 and stopped. Not reached:

1. **`GLOSSARY.md` and `NORTH_STAR.md` were not read.** The task ordered four law files; I read `AGENT_GUARDRAILS.md` §0–§4 and `WRITING_LAW.md` in full and spent the remaining budget on the text. No finding above depends on the glossary registry or the north star, and I made no terminology-legality judgment (that is persona 04's and 03's scope anyway) — but the omission is mine to declare, not to excuse.
2. **§2.1 and §2.3's literature paragraphs were read once, not re-read.** My persona's method is deliberate re-reading and comparison; PDF pp. 18 and 23–24 got one pass, so the "reads as one argument" judgment on the next-place lineage paragraph is thinner than the rest.
3. **No aloud-rhythm pass on §2.4** (PDF pp. 24–26), the densest prose in the chapter. `WRITING_LAW.md` §4.2 prescribes reading a page aloud to detect uniform sentence weight; I sampled sentences instead, so SF-8 may not be the only over-loaded sentence there.
4. **Only `main.pdf` was read.** `main_academico.pdf` (99 pp.), `main_ppgc.pdf` (103 pp.) and `main_extra.pdf` (20 pp.) were not opened, so I cannot say whether the frame chapters read the same in the deposit and supplementary builds. SF-1's missing stem in particular should be confirmed in `main_academico.pdf` before the fix is measured.
5. **Chapters 3, 4, 5 not read** — excluded by scope, which is why the seam verdict is partial.
6. **The 106 new lines in §2.3 flagged in my briefing were read as prose but not diffed against the prior commit.** SF-4 and SF-7 fall inside that block; I did not establish whether they were introduced by that edit or predate it, and I did not run `git diff` to find out.


---

<!-- estado-rodada -->
> **Rodada encerrada · último toque 2026-07-30 · sem autoridade.**
> Este ficheiro é registo de proveniência do que foi discutido nesta passagem, não fonte
> de um facto corrente. O que ficou decidido está em [`VEREDITOS.md`](../../../../VEREDITOS.md);
> os valores entregues estão em `CLAUDE.md` §0.1. Não copie nada daqui sem confirmar lá.
