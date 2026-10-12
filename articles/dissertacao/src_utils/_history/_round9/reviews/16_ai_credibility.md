# Review 16 · AI-credibility (external-perception simulation) — round 9

**Persona:** `reviewers/16_ai_credibility.md` (screener channel + suspicious-expert channel)
**Build commit:** `901a0408`
**Date:** 2026-07-30 (session start 08:41 -03, checkpoint honored)
**Read this session (sources, opened and quoted from):**
`AGENT_GUARDRAILS.md` §0–§4 (lines 1–140), `WRITING_LAW.md` (full, 193 lines), `GLOSSARY.md`
(fail-closed rule L9–13; §4 Pareto rows L99–104; §6 PT rows L146–149; L156–176),
`reviewers/16_ai_credibility.md` (full), `src/chapters/2_fundamentals.tex` L383–617 (all of §2.3,
including the 106 lines added today by `beebd33b`), `src/chapters/apx_f_cosine.tex` L60–86 and
L230–359, `src/chapters/1_introduction.tex` L24–40 + sweep over L1–304,
`src/chapters/6_conclusion.tex` L1–60, L113–122, L330–348 + sweep over L1–348,
`src/chapters/3_cbic.tex` L27–90 and `src/chapters/3_cbic/{method,conclusion}.tex` (to test one
claim about study 1), `src/chapters/apx_c_ai_disclosure.tex` L93–126.
**Rendered pages extracted from `src/build/main.pdf` (102 pp, not rebuilt):** pp. 22, 23, 24, 97, 101.

**Exact commands run:**

    date
    git log -1 --format='%H %h %ad %s'
    git log --since='2026-07-30 00:00' --oneline --stat -- src/chapters/2_fundamentals.tex src/chapters/apx_f_cosine.tex
    git show beebd33b --stat
    git log --oneline -3 -- WRITING_LAW.md ; git log --oneline -3 -- GLOSSARY.md
    wc -l AGENT_GUARDRAILS.md WRITING_LAW.md GLOSSARY.md NORTH_STAR.md reviewers/16_ai_credibility.md
    grep -nE '\\(chapter|section|subsection|subsubsection|paragraph)\{' 2_fundamentals.tex
    grep -n 'Pareto' WRITING_LAW.md ; grep -n -i 'pareto|gradient conflict|scalariz|...' GLOSSARY.md
    grep -n 'SIGN-OFF\|NEEDS SIGN' apx_f_cosine.tex
    grep -rn -i 'hard sharing\|soft sharing\|sharing scheme' 3_cbic/*.tex
    grep -n 'stronger and stranger\|replacing the sharing scheme\|hard sharing costs nothing\|deserves one statement\|obliges one to say\|Conflict has a standard measure\|serve as structure' apx_f_cosine.tex 2_fundamentals.tex 6_conclusion.tex
    python3  # banned-vocabulary sweep (WRITING_LAW §4 table + Claude-family tics), 4 files, comments stripped
    python3  # em-dash / semicolon / contraction / negative-parallelism sweep, 4 files
    python3  # sentence-length distribution per block (n, mean, sd, cv, min, max, short-sentence count)
    python3  # gestalt-tell density per block (meta-discourse, negation openers, copula avoidance, significance trailers)
    python3  # pypdfium2 text extraction of main.pdf, heading location, pages 22/23/24/97/101

**Not run:** `make check`, `make selftest`, any build (instructed). No local detector is installed
in this checkout, so the screener channel is estimated qualitatively (see verdicts). The persona's
web refresh mandate was not exercised (see UNFINISHED).

---

## Verdict per channel

**Screener risk: LOW.** The scoped text is neither low-perplexity nor vocabulary-flattened: the
new §2.3 block carries a sentence-length spread of cv = 0.58 (n = 13, min 7 words, max 66) against
0.42 and 0.62 in the untouched §2.3 paragraphs on either side of it, so the added passage did not
compress the chapter's variance. Appendix F L240–345 measures cv = 0.61 with 12 of 44 sentences
under 12 words. Any score a committee obtains on this document is a hybrid-text score and is
window-size-sensitive by measurement, so it is evidence about the window, not about authorship;
I report the distributional numbers instead and no score is claimed here.

**Expert-suspicion risk: MEDIUM, concentrated in two places, not diffuse.** The gestalt problem is
not word choice (the banned-vocabulary sweep returned one hit in four files, and em-dashes and
contractions are at zero) but two narrative moves: an appendix sentence that asserts an experiment
the record does not contain, and three consecutive paragraphs of today's §2.3 addition that open
with the same meta-discursive move. The measured fact this persona answers to is that
polish-without-substance now costs a manuscript more than plain prose does, so a sentence whose
confidence outruns the repository is the expensive defect here, and finding 1 is exactly that.

---

## Findings

### 1. BLOCKER — Appendix F states that study 1 replaced the sharing scheme; study 1 never did

**WHERE:** `src/chapters/apx_f_cosine.tex:83` (rendered: `src/build/main.pdf` p. 97, opening
section of Appendix F).

**WHAT (verbatim, L81–84):**

> orthogonal on every dataset measured, which is a stronger and stranger result than mere absence of
> conflict, and it carries a consequence for the whole investigation: a gradient balancer had nothing
> to balance. That is why replacing the sharing scheme changed so little in the first study, and why
> changing the representation changed so much in the second and third.

**WHY:** The first study is Chapter 3 (CBIC), and it did not replace the sharing scheme. Its own
method text says the architecture "is built upon a hard parameter-sharing scheme for the joint
training of POI Category Classification and Next-POI Prediction" (`3_cbic/method.tex:69`), and its
conclusion lists the replacement as work not done: "We plan to explore alternative parameter-sharing
mechanisms, such as \textbf{soft sharing (e.g., Cross-Stitch Networks) or Mixture-of-Experts (MoE)
models}" (`3_cbic/conclusion.tex:23`). One intervention, stated as future work in the published
chapter, is reported four pages later in the same volume as a completed comparison whose outcome is
known. The appendix also contradicts itself: its own mechanism section says "Had the tasks been in
conflict, a better sharing scheme or a better balancer would have been the remedy. They were not"
(`apx_f_cosine.tex:296-297`), which presupposes that no better sharing scheme was tried. This breaks
AGENT_GUARDRAILS §3 C2 (a connective claim about what the arc shows is a claim and needs the
record) and WRITING_LAW §3 (verbs bound to evidence; time-indexed CBIC conclusions). Both channels
are endangered, and the expert channel worse: an examiner who reads Chapter 3 and then Appendix F
finds a claimed experiment with no method, no table, and no number, which is the single most
recognizable signature of generated narrative smoothing.

Note that Chapter 2's version of the same argument is correctly bounded, which is how I am confident
the drift is local to the appendix: `2_fundamentals.tex:501-503` says only "it reads that result as
the reason no balancing method improved on a fixed weighting in this work", a claim about balancers,
not about sharing schemes.

**FIX:** Rewrite the clause to the claim the record supports, for example "That is why a gradient
balancer changed so little in the first study" if that is what Chapter 3 measured, or drop the
first-study clause and keep only the representation half. Which of the two is correct is a fact
about Chapter 3's experiments that I did not audit, so the choice is the author's; what cannot stand
is the present wording. The sentence sits inside the passage already carrying
`[NEEDS SIGN-OFF: raised round 7 | THE WHOLE APPENDIX]` at `apx_f_cosine.tex:65`, so the sign-off
gate is the right place to resolve it.

### 2. SHOULD-FIX — "stronger and stranger" both inflates and contradicts the Chapter 2 definition

**WHERE:** `src/chapters/apx_f_cosine.tex:81` (PDF p. 97) against `src/chapters/2_fundamentals.tex:497`
(PDF p. 23).

**WHAT:** Appendix F: "Their gradients are statistically indistinguishable from orthogonal on every
dataset measured, which is a stronger and stranger result than mere absence of conflict".
Chapter 2, defining the same quantity: "Orthogonality is not a conflict resolved but a conflict
absent, which puts a limit on what any of these methods can contribute."

**WHY:** Chapter 2 defines orthogonality *as* the absence of conflict; Appendix F ranks it above
"mere absence of conflict". One of the two is wrong about the same measured quantity, and the reader
meets the definition first. Independently, "stranger" is a significance-inflation trailer of the
kind this persona is asked to key on, and "mere" is a decorative intensifier under WRITING_LAW §4
(intensifier budget, one per claim); the equivalence test licenses "indistinguishable from
orthogonal", it does not license a judgment about how surprising that is.

**FIX:** Cut the evaluative clause and let the measurement carry the paragraph: "Their gradients are
statistically indistinguishable from orthogonal on every dataset measured, and that carries a
consequence for the whole investigation: a gradient balancer had nothing to balance." If the author
wants to keep the note of surprise, it belongs in the mechanism section with a reason attached, not
in the appendix's opening summary.

### 3. SHOULD-FIX — three consecutive paragraphs of today's §2.3 addition open with the same meta-discursive move

**WHERE:** `src/chapters/2_fundamentals.tex:419`, `:433-434`, `:494` (PDF pp. 22–23).

**WHAT (paragraph openers, verbatim):**

> Casting it that way obliges one to say what an optimum would be.
> Reaching that front is not what the balancing methods promise, and the distance between the promise
> and the front deserves one statement.
> Conflict has a standard measure, and it is the quantity the gradient methods act on: ...

**WHY:** Each opener is a sentence about what the text is about to do rather than about
multi-task learning, and the first two name their own rhetorical obligation ("obliges one to say",
"deserves one statement"). WRITING_LAW §4.4 bans discourse-skeleton reuse specifically because
identical opening moves across adjacent sections are glaring at document scale, and §4.2 warns about
uniformly impersonal register. Measured density in the added block: 4.0 meta-discourse markers per
1,000 words, against 0.0 in the §2.3 paragraphs that precede it (L386–418) and 0.0 in those that
follow it (L525–572). This is the residual after persona 03's word-level sweep, which the block
passes, and it is the kind of evenness the suspicious-expert channel reads as machine-shaped.

**FIX:** Vary one or two of the three openers so they lead with the content, for example open the
Pareto paragraph on the asymmetry itself ("A single loss orders any two parameter settings; several
losses do not.") and let the definitional sentences follow. Keep the third as it is; it is the one
that already opens on a fact.

### 4. SHOULD-FIX — the new §2.3 block is the one passage in scope that could have been written without access to the experiments

**WHERE:** `src/chapters/2_fundamentals.tex:419-450` (PDF pp. 22–23), the Pareto material added
today.

**WHAT:** Across those 32 lines the only sentence tied to this project is the closing pair, "This
dissertation therefore claims no Pareto property of any kind for its models. Its verdicts are
per-task scores measured against dedicated single-task models under the tests of
Section~\ref{sec:fund:eval}." Everything before it is definitional.

**WHY:** This persona's highest-yield check is ABSENCE: the tell is missing lived research detail,
and the fix is additive, never subtractive. The block is legal under every rule in WRITING_LAW and
still reads as textbook material because nothing in it could only have been written by someone who
ran the experiments. The dissertation's own record supplies the missing specificity: Appendix F
reports "4,650 epoch-level cosines from seven datasets" and Florida's twelve configurations
(PDF p. 97), and the twelve configuration means "span $[-0.00261, +0.00457]$" (PDF p. 101).

**FIX:** Additive only. One clause naming that the balancers were tried here and did not improve on
a fixed weighting, placed where the block hands off to the conflict paragraph, converts the passage
from survey to argument. Do not add a number in §2.3: `GLOSSARY.md:104` and CONSIDERATIONS work-list
item 28 require the quantity to be defined here and its value reported only where it was measured,
and the existing comment at `2_fundamentals.tex:491-492` records that constraint. Whether to make
the addition at all is the author's call, since the section is deliberately thin.

### 5. NIT — an appendix is given the agency of reading its own result

**WHERE:** `src/chapters/2_fundamentals.tex:501` (PDF p. 23).

**WHAT:** "it reads that result as the reason no balancing method improved on a fixed weighting in
this work".

**WHY:** Vague attribution, which the persona lists as a gestalt trigger. The attribution device is
doing honest work here (the comment at L512–518 shows it was chosen so the mechanism claim stays
the appendix's), so this is style, not integrity: the sentence attributes a reading to a document
rather than to the author or to the measurement.

**FIX:** "Appendix~\ref{apx:cosine} measures the cosine ... and argues that this is why no balancing
method improved on a fixed weighting in this work." Same hedge, an agent that can hold an opinion.

### 6. NIT — "rather than" is doing too much work in Chapter 6, and one instance is copula avoidance

**WHERE:** `src/chapters/6_conclusion.tex:332-333` (sentence spans L330–333), with the pattern at
`:119`, `:169`, `:207`, `:310`, `:36`.

**WHAT (verbatim, L332–333):** "suggest category and region predictions can serve / as structure
rather than competition (limitation~4)".

**WHY:** Six negative-parallelism or "rather than" constructions in the 1,764 words I swept (1.1
per 1,000 words for the not-X-but-Y shape alone), and this one pairs it with "serve as" for "be",
the copula avoidance the persona names explicitly. Individually each is defensible; the density is
what a reader notices in a closing chapter.

**FIX:** "can act as structure instead of competing" or "can structure the prediction rather than
compete with it" for :333, and leave the rest; the other five each carry a real contrast.

### 7. NIT — copula avoidance plus a metaphor in §2.4 (found by the sweep, outside my narrowed scope)

**WHERE:** `src/chapters/2_fundamentals.tex:624` (PDF p. 24).

**WHAT:** "Two check-in datasets serve as the ground."

**WHY:** Reported for completeness because it is the single hit my WRITING_LAW §4 vocabulary sweep
returned across all four files: "serve as" for "are", with "the ground" as an unglossed metaphor
(§8 idiom rule). §2.4 was not in my narrowed scope, so I did not read the surrounding paragraph as a
reviewer and I make no claim about its context.

**FIX:** "The dissertation uses two check-in datasets." Author's call, and it belongs to whoever
owns §2.4.

---

## What already reads credibly human, and should be protected

- `6_conclusion.tex:113-122` (PDF: Chapter 6 §6.2 region) — the paragraph that declines to use its
  own ablation: "A development ablation at Florida removed the cross-attention stack alone and moved
  next-category macro-F1 by $-0.04 \pm 0.13$, but that measurement was taken on an earlier
  configuration ... We therefore do not name the shared trunk as the source". Reflective, first
  person, and it argues against the author's own interest. No generator produces this from a thin
  prompt; do not smooth it, and do not shorten the reasoning to the conclusion.
- `apx_f_cosine.tex:259-269` — the refusal to accept a $t$-test result the same appendix rejects
  elsewhere ("this appendix will not accept for one claim a basis it rejects for another"), with
  California given as the counter-case. Same protection.
- The new §2.3 block's honest separation of what each method proves, including that PCGrad "makes no
  Pareto claim at all" (`2_fundamentals.tex:444-445`). Four of five methods would be misdescribed by
  a single blanket sentence, and the passage refuses the blanket. That is a credibility asset;
  keep the per-method granularity even if finding 3's openers are rewritten.
- Variance: not compressed anywhere I measured. The added block sits inside the range of its
  untouched neighbors (cv 0.58 against 0.42 and 0.62). No over-correction to sterile prose was found
  in the scoped text, so finding 6's fix should stay minimal.

## Provenance-shield status (process, not prose)

| Defense | Status | Where I checked |
|---|---|---|
| Generation disclosed as generation, not as editing | Present and task-precise | `apx_c_ai_disclosure.tex:103-107`: frame chapters "were drafted by the assistant from author-approved outlines" |
| Reviewer independence stated | Present | `apx_c_ai_disclosure.tex:112-116`: each pass "run by an agent that did not write the text under review" |
| Verification rules stated to the reader | Present | `apx_c_ai_disclosure.tex:120-126` (references, numbers, verdict verbs, flagging) |
| Sign-off gates on new claims | Present on both of today's passages | `apx_f_cosine.tex:65`, `2_fundamentals.tex:519-523` |
| Git author/AI commit discipline | Not audited this session | see UNFINISHED |

## COUNTS

**blockers: 1 · should-fix: 3 · nits: 3**

## UNFINISHED

- The persona's **web refresh mandate** (bounded search for new tells, detector changes, venue
  policy moves since the two evidence files' dates) was not run. No proposed law or evidence-file
  updates are offered this round; the two evidence files were not opened either.
- **No detector was run.** The screener verdict rests on the sentence-length distributions I
  measured, not on any score. Nothing here should be read as a detector result.
- **Chapters 3, 4, 5 not read** (excluded from scope), except `3_cbic/method.tex` and
  `3_cbic/conclusion.tex`, opened only to test finding 1.
- **Chapter 1 and Chapter 6 got sweeps, not a full gestalt read.** I ran the vocabulary, punctuation,
  rhythm, and gestalt-density passes over all 304 and 348 lines and read L24–40, L1–60, L113–122,
  L330–348 closely. Their section transitions and chapter-opener templates were not compared
  paragraph by paragraph, which is where §4.4 skeleton reuse would show.
- **Appendix F L87–229** (the setup section, the results section, and the figure caption block) was
  read only in the rendered p. 97 and p. 101 extractions, not line by line in source.
- **Scope comment:** the narrowing was right for the clock. The one thing I would add next time is
  Chapter 6's opening and Chapter 1's opening side by side, since that is the cheapest place for a
  cross-chapter template tell to hide and neither sweep can see it.


---

<!-- estado-rodada -->
> **Rodada encerrada · último toque 2026-07-30 · sem autoridade.**
> Este ficheiro é registo de proveniência do que foi discutido nesta passagem, não fonte
> de um facto corrente. O que ficou decidido está em [`VEREDITOS.md`](../../../../VEREDITOS.md);
> os valores entregues estão em `CLAUDE.md` §0.1. Não copie nada daqui sem confirmar lá.
