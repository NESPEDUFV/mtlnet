# 04 · Concordance checker — cross-chapter consistency audit (Round 9)

**Persona:** `reviewers/04_concordance_checker.md` (Gate G3 + guardrails L3/L4). Fresh eyes: I wrote
none of the text under audit and did not participate in the Round 9 edits.

**Build commit:** `03b53d16` (full: `03b53d16e42de7c5cb21edc1d9e26ec34b9bf019`, committed
2026-07-30 04:49:23 -0300; read from `git log -1` in the repo root).

**Volume read:** `src/build/main.pdf`, 102 pages (defense build). Page numbers in findings are
**PDF page indices** of that file, extracted from its text layer. Source line numbers are from the
working tree at this commit. I did not open `main_academico.pdf` (99 pp), `main_ppgc.pdf` (103 pp),
or `main_extra.pdf` (20 pp); the supplementary volume is referenced only where the defense volume
points into it.

**Date:** 2026-07-30.

**Verdict: seams need work.** The document agrees with itself on the load-bearing claims. The
region wording law, the six-dataset scoping, the `5.3`/`9.4` category range, the `+0.001` cosine
number and its scope clauses, the `n = 20` / `n = 4` arithmetic, and the Abstract/Resumo pair are
concordant everywhere I checked them. The cross-reference graph is clean. What needs work is a
small set of frame-to-chapter seams where the frame states a chapter's result or scope in terms
the chapter itself does not use: one metric name is never bridged, one balancer-screen claim
loses its scope in two frame-side restatements, one cost claim reads as a general result when its
own chapter restricts it to wall time, and the CBIC candidate-cause list is renumbered between
Chapter 1 and Chapter 6. None is a factual error inside a chapter; each is a place where two
parts of the document say the same thing differently.

**Exact commands run** (no build, no `make check`, no `make selftest`; read-only except this file):

```
git log -1 --format='%H %ci'
ls -la ; ls -la reviewers/ ; ls -la src_utils/_history/_round9/ ; ls -la src/build/*.pdf
wc -l AGENT_GUARDRAILS.md WRITING_LAW.md GLOSSARY.md NORTH_STAR.md CLAUDE.md reviewers/*.md
sed -n '59,116p;304,415p' NORTH_STAR.md
sed -n '125,145p;459,482p' AGENT_GUARDRAILS.md
python3 -c "pypdfium2 ... get_text_bounded() over src/build/main.pdf -> /tmp/conc/main_txt.txt"   # 102 pages
wc -l src/chapters/*.tex src/chapters/*/*.tex ; cat src/content.tex
grep -n 'MTLNet|MTL-Net|MtlNet' <all chapter+table .tex>
grep -nio '\bvenues\?\b' ... ; grep -ni 'sigmoid|label-only|autocorrelation ceiling' ...
grep -no 'champion-G|dk_ovl|log_T|B9|v1[1-7]|mtlnet_crossattn_dualtower|fclass|substrate' ...
grep -c '—' ... ; grep -no "don't|doesn't|isn't|can't|won't|it's|we're|didn't" ...
python3 (label/ref lint, comment-stripped: 113 labels, 269 refs, dup/dangling check, cross-chapter pair table)
python3 (comment-stripped prose corpus -> /tmp/conc/prose.txt, 2976 lines)
python3 (9-gram cross-chapter duplication sweep over the prose corpus)
grep -n 'four of six|six datasets|seven datasets|0\.001|5\.3|9\.4|nineteen|twenty|Pareto|Nash|
         Average F1|macro-F1|cost more|MFLOP|Next-POI|no balanc' /tmp/conc/prose.txt
sed -n <targeted ranges> src/chapters/{1_introduction,2_fundamentals,6_conclusion}.tex
sed -n <targeted ranges> src/chapters/{3_cbic,4_courb,5_mobiwac}/*.tex src/chapters/apx_*.tex
grep -v '^\s*%' src/tables/frame/lineage.tex src/tables/{courb,cbic,mobiwac}/*.tex
python3 (page-locate each quoted string in the PDF text layer)
```

---

## BLOCKERS

None. I found no cross-chapter contradiction that makes the document state two incompatible things
about the same quantity or claim, and no wrong-target cross-reference.

---

## SHOULD-FIX

### SF-1 · The CoUrb chapter's metric is never bridged to the frame's `macro-F1`, and the frame silently renames it

**WHERE:** `src/chapters/4_courb/results.tex:14` and `:101`; `src/tables/courb/category.tex:5`;
`src/tables/courb/next.tex:5` (PDF pp. 54, 56, 57, and the List of Tables on p. 6) against
`src/chapters/6_conclusion.tex:46` (PDF p. 78).

**WHAT:** Chapter 4 names its metric, in prose and in both table captions:

> "The performance of the models is evaluated using the Average F1-Score per category, reported as
> mean and standard deviation over 5 \textit{folds} with a stratified split"

> "\caption{Average F1-Score (\%) per model and state for the POI Category Classification task.}"

Chapter 6 reports the same result under a different name:

> "raised category macro-F1 by 20.2 to 22.0 percentage points across the three states tested"

**WHY:** WRITING_LAW §2 ("One name per concept for the whole document") and GLOSSARY §4, which
registers **macro-F1** as "the category metric everywhere". `Average F1-Score per category` is not
in the registry, so under the GLOSSARY §1 fail-closed rule it may not appear in prose; and the
frame chapter attributing a number to `macro-F1` that its own chapter labels `Average F1-Score` is
exactly the L3/L4 drift a coletânea is exposed to. Note the asymmetry that makes this a
concordance finding rather than a style nit: Chapter 4's *protocol* sentence at
`4_courb/results.tex:14` already uses "macro-F1" for the epoch-selection rule in the same
sentence in which it calls the reported metric "Average F1-Score per category", so the two names
sit side by side within one sentence with nothing saying they denote the same quantity. Chapter 3
handles the same problem correctly at `3_cbic/results.tex:30` ("we report precision, recall, and
$F_{1}$-score, and utilize the macro-average of these metrics"), which is a bridge; Chapter 4 has
none. I checked `chapters/apx_b_errata.tex` and `tables/courb/errata.tex` for a metric-name
erratum row: there is none (`grep 'Average F1'` over both returns nothing).

**FIX:** Author's call between two options, both cheap. (a) Add one bridging clause to
`4_courb/results.tex:14`, in the pattern the preface already uses for the task-name bridge:
"the Average F1-Score per category, which is the macro-averaged F1 (macro-F1) of the frame's
Section 2.4". This keeps the published wording and the published captions untouched. (b) Declare
the rename in Appendix B and normalize the chapter to `macro-F1`, as was done for
`MTLNet` → `MTLnet`. Option (a) is the smaller departure from the published text and is my
recommendation; option (b) is more consistent with how the MTLnet spelling was settled. Either
way the frame's `macro-F1` at `6_conclusion.tex:46` then has a named referent.

### SF-2 · Chapter 2 and Appendix F state the balancer finding without the scope Chapter 5 gives it

**WHERE:** `src/chapters/2_fundamentals.tex:501-502` (PDF p. 23) and
`src/chapters/apx_f_cosine.tex:291-292` (PDF p. 101), against
`src/chapters/5_mobiwac/02_related.tex:111-117` (PDF p. 63).

**WHAT:** Chapter 5 states the finding with its measurement scope attached:

> "of nineteen loss and gradient balancers screened at their default configurations at a single
> seed on two datasets, Alabama and Florida, including the two methods named above, none improved
> on a tuned fixed task weighting across both tasks and both datasets. Two exceed equal weighting
> on next-category at Alabama, Nash-MTL by $0.68$ points and scale normalization by $0.19$"

Chapter 2 restates it with no scope:

> "it reads that result as the reason no balancing method improved on a fixed weighting in this work"

Appendix F likewise:

> "and why Chapter~\ref{ch:mobiwac} finds no balancer improving on a fixed loss weighting"

**WHY:** WRITING_LAW §3, "Every number carries its reference point ... and its convention (which
metric, which selection rule, n = how many)" and "Scope every universal". Chapter 5's claim is
"none improved **across both tasks and both datasets**, at default configurations, at a single
seed, on Alabama and Florida" and it explicitly records two per-cell exceedances. "No balancing
method improved on a fixed weighting" drops the conjunction, the two datasets, the single seed,
and the default-configuration caveat, so a reader of §2.3 or of Appendix F carries away a
stronger claim than the chapter supports, and one that the same chapter's next two sentences
partially contradict. This is the concordance failure mode the persona file item 3 names: the
frame announcing more than the section it cites.

**FIX:** Add the scope clause at both sites, drawn verbatim from Chapter 5 rather than
paraphrased. Chapter 2: "the reason no balancer among the nineteen screened there improved on a
tuned fixed weighting on both tasks at both screened datasets". Appendix F: the same
substitution. No number needs to move.

### SF-3 · "It cost more to train" is stated unrestricted in Chapters 1 and 6, but its own chapter restricts the cost to wall time

**WHERE:** `src/chapters/1_introduction.tex:116` and `src/chapters/6_conclusion.tex:36`
(PDF pp. 13 and 78), against `src/chapters/3_cbic/results.tex:189` and
`src/chapters/3_cbic/conclusion.tex:14` (PDF pp. 42 and 42), and the errata row at
`src/tables/cbic/errata.tex:51-56`.

**WHAT:** Both frame chapters use the same unrestricted phrase:

> "The joint model did not consistently outperform the two dedicated single-task models, and it
> cost more to train." (Ch. 1)

> "the joint model did not consistently outperform the dedicated single-task models on the two
> category tasks, and it cost more to train." (Ch. 6)

Chapter 3, as corrected, restricts it:

> "In terms of MFLOPs, in contrast, the table does not show a higher cost for the MTL setup: the
> MTL model required 0.234 MFLOPs, against 2.315 MFLOPs for the Category model and 0.012 MFLOPs
> for the Next model."

and its conclusion says "exhibited higher computational demands in terms of convergence wall
time". The errata row records the reason: "four follow-on wording edits restrict the overhead
claim to wall time".

**WHY:** WRITING_LAW §3 (numbers and claims carry their convention) and the persona's item 3
(promises vs delivery: the frame claims nothing the body did not establish). The document went to
the trouble of correcting Chapter 3 away from an unrestricted cost claim, then restates the
unrestricted version twice in the frame. On the measured axis that Chapter 3 reports second, the
joint model is *cheaper* (0.234 against 2.315 + 0.012 MFLOPs), so "it cost more to train"
contradicts the corrected chapter on one of its two cost columns. This also touches the
NORTH_STAR §6 Ch.1 beat-2 F3 guard, which forbids promising lower compute cost in the frame; the
mirror-image obligation is not to over-claim higher cost either.

**FIX:** Restrict both frame sentences to the axis Chapter 3 measures: "and it took longer to
converge" or "and it cost more wall time to train". Two words each, no number enters the frame,
and the arc reads identically.

### SF-4 · Chapter 1 and Chapter 6 give different accounts of what CBIC's candidate explanations were

**WHERE:** `src/chapters/1_introduction.tex:116-118` (PDF p. 13) and
`src/chapters/6_conclusion.tex:36-39` (PDF p. 78), against
`src/chapters/3_cbic/conclusion.tex:8-12` (PDF p. 43).

**WHAT:** Chapter 6 enumerates them:

> "three candidate explanations, task dissimilarity, an input representation too poor for both
> tasks at once, and the restrictiveness of hard sharing, that the rest of the dissertation put to
> the test."

Chapter 3's own three are headed **"Subtle Negative Transfer due to Task Dissimilarity"**,
**"Task Difficulty and Representation Mismatch"**, and **"Architectural Restrictiveness"**. The
second one's body reads:

> "The performance gap between the two tasks (with category classification achieving higher
> F1-scores) suggests an imbalance in difficulty. The representation learned by the shared layers
> might have become biased towards the features required for the simpler, static classification
> task"

**WHY:** Persona item 1 (terminology concordance) and item 3 (the frame states the body's claims
in the body's own terms). Chapter 3's second hypothesis is about **task-difficulty imbalance and
the representation the shared layers learn** — an internal, learned representation. Chapter 6
renders it as "an input representation too poor for both tasks at once", which is a claim about
the **input** representation, i.e. the DGI place embedding. Those are different objects, and the
difference is load-bearing for the arc: the whole dissertation turns on the input
representation, so attributing that diagnosis to CBIC's own hypothesis list makes CBIC look like
it named the answer. Chapter 1 is more careful and says only "three candidate explanations, one of
which pointed at the input representation", which is defensible as a reading but still stronger
than Chapter 3's text; and NORTH_STAR §6 beat 4(d) explicitly forbids the foresight framing
("NEVER 'CBIC's future work called for better representations', never foresight"). The two frame
chapters also disagree with each other in emphasis: Ch. 1 says one of the three pointed at the
input representation; Ch. 6 names the input representation as the whole of hypothesis two.

**FIX:** Author's call on how much to concede. Minimum consistent version: make Ch. 6's second
item match Chapter 3's own wording, e.g. "a difficulty imbalance under which the shared layers
learn a representation biased toward the static task", and let Ch. 1's "one of which pointed at
the input representation" stand only if the author judges it supported by that body text; if not,
soften it to "one of which concerned the representation the shared layers learn". Either way the
two frame sites should say the same thing.

### SF-5 · `Pareto` vocabulary: §2.3's registered spelling is not the spelling used at three chapter sites

**WHERE:** `src/chapters/2_fundamentals.tex:430-431, 434-441, 448` (PDF p. 23) against
`src/chapters/3_cbic/basis.tex:44` (PDF p. 31), `3_cbic/basis.tex:54` (PDF p. 32),
`src/tables/courb/errata.tex:39` (supplementary volume).

**WHAT:** §2.3 defines and uses the hyphenated form and the two nouns:

> "A point is Pareto-stationary when some convex combination of the task gradients is zero, which
> is necessary for Pareto optimality without being sufficient"

> "This dissertation therefore claims no Pareto property of any kind for its models."

Chapter 3 uses two further forms the frame never defines:

> "MGDA finds Pareto-optimal descent directions" (`basis.tex:44`)

> "theoretical guarantees of Pareto efficiency ... remain open research directions"
> (`basis.tex:54`)

**WHY:** GLOSSARY §4 registers exactly three Pareto terms (`Pareto dominance`, `Pareto
optimality`/`Pareto front`, `Pareto-stationary point`) and its §1 maintenance rule is fail-closed.
`Pareto-optimal` as a compound adjective is a legitimate inflection of a registered term and I do
not report it; **`Pareto efficiency` is a fourth term that is not registered and is not defined
anywhere in the volume**. Both sites are published CBIC prose, which the GLOSSARY's own
conflict rule protects ("the chapter keeps the paper's usage and the frame uses this registry"),
so this is not a demand to edit Chapter 3. It is a gap in the bridge: §2.3 is the one place that
defines this vocabulary for the volume, and it defines three of the four terms a reader will meet.

**FIX:** Author's call. Cheapest option that satisfies the registry: add `Pareto efficiency` to
GLOSSARY §4 as a Chapter 3 historical usage with a one-line note that the dissertation's own
sections use `Pareto optimality`, and leave both chapters untouched. Alternatively add three words
to §2.3 noting that the reproduced chapters also use "Pareto efficiency" for the same property.
Do not edit the published sentences.

---

## NITS

### N-1 · `venue` appears once in a live prose line of Chapter 2's source

**WHERE:** `src/chapters/2_fundamentals.tex:600`.

**WHAT:** `+ NeurIPS 2022 venue). Added per domain F4 (canonical scalarization-skeptic anchor). [new bib]`

**WHY:** WRITING_LAW §2 bans "venue" as a synonym for place. This instance is inside a LaTeX
comment block (the section's source ledger) and refers to a conference, not a POI, so it does not
print and does not break the rule as written. I record it only because a `grep`-based sweep of the
banned-word list will keep flagging it, and because the other 14 hits in the sweep are in the same
category (comments, the errata tables' quotations of published text, and the bibliography errata
table's field names). **Zero printed occurrences of `venue` meaning "place" exist in the defense
volume.** No action needed; this line documents the sweep result so the next auditor does not
re-derive it.

### N-2 · `sigmoid` appears once in printed prose, in a reproduced chapter

**WHERE:** `src/chapters/4_courb/methodology.tex:114` (PDF p. 51).

**WHAT:** "in which $\sigma$ denotes the sigmoid function, $\text{sim}(\cdot,\cdot)$ is the cosine
similarity"

**WHY:** GLOSSARY §3 (`logistic function`) rules: 'Say "logistic function", never "sigmoid", in
prose.' Chapter 2 obeys it and its source comment at `2_fundamentals.tex:290` records the ruling.
This is published CoUrb prose, and the GLOSSARY conflict rule lets the chapter keep the paper's
usage, so the ruling is not violated. Flagged only because Chapter 2 defines $\sigma$ as "the
logistic function" (p. 20, at the Check2HGI discriminator equation) and Chapter 4 defines the same
symbol as "the sigmoid function" on p. 51, which is a one-symbol, two-names seam. If the author wants it closed, the errata appendix is the
place; my recommendation is to leave it.

### N-3 · One contraction in an appendix source comment

**WHERE:** `src/chapters/apx_f_cosine.tex:6`.

**WHY:** WRITING_LAW §7 requires `contractions = 0`. This one is in a comment and does not print;
printed contractions in the defense volume: zero. Recorded so the sweep is reproducible.

### N-4 · Em-dash count is zero and repo codenames are comment-only

**WHERE:** all chapter and table sources.

**WHY:** WRITING_LAW §1 (no em-dash) and §2 (no repo codenames in prose). `grep -c '—'` over every
chapter and table `.tex` returns no file with a nonzero count. Every hit for `dk_ovl`, `log_T`,
`v17`, `substrate`, `fclass`, and `mtlnet_crossattn_dualtower` is inside a LaTeX comment; I
checked the two that looked riskiest (`2_fundamentals.tex:319,331` and `6_conclusion.tex:126`) and
both are provenance ledgers, with `2_fundamentals.tex:333` explicitly recording "Registry id
deliberately absent from prose per WRITING_LAW §2". **This is a pass, not a finding** — recorded
because the persona requires saying so when a check comes back clean.

---

## Cross-reference lint (L4) — PASS

Comment-stripped sweep over `src/chapters/**/*.tex`, `src/tables/**/*.tex`, `content.tex`,
`main.tex`, `preamble.tex`:

| Check | Result |
|---|---|
| `\label` definitions | 113 |
| `\ref`/`\autoref`/`\eqref`/`\nameref`/`\pageref` uses | 269 |
| Duplicate labels | **0** |
| Dangling refs (ref with no label) | **0** |
| `??` in the built PDF text layer | **0** |

The three duplicate labels and one dangling ref that a naive sweep reports are all inside LaTeX
comments (`2_fundamentals.tex:513,515` quoting Appendix F's label names; `tables/mobiwac/results.tex:15`
in the split-table provenance note; `5_mobiwac/07_discussion.tex:25` quoting the doubled-backslash
render defect that Round 6 fixed). Comment-stripped, all four vanish.

**Target sanity, spot-checked by hand rather than by compile:** I verified that every
cross-chapter pointer I read in the frame resolves to the chapter it names in prose —
`6_conclusion.tex:86,102,111,131,191,215` (`ch:mobiwac`/`ch:cbic`), `1_introduction.tex:111,120,128,192,197`
(`ch:cbic`/`ch:courb`/`ch:mobiwac`/`ch:fundamentals`/`ch:conclusion`), `2_fundamentals.tex:407,498,641,649,654,894`
(`ch:mobiwac`, `apx:cosine`), and the lineage table's two chapter pointers
(`tables/frame/lineage.tex`, `ch:courb` and `ch:mobiwac`). No wrong-target ref found. The 42
unreferenced labels are section and appendix anchors, which is expected and not a defect.

## Duplication sweep (L3) — PASS

9-gram near-duplicate sweep over the comment-stripped prose corpus (2,976 lines), restricted to
matches that cross a chapter boundary and involve at least one frame chapter. Six overlap clusters
surfaced; every one is sanctioned:

| Passage pair | Longest shared span | Verdict |
|---|---|---|
| `1_introduction.tex:156` ↔ `6_conclusion.tex:15` | "interest prediction for the next category and next region" | Sanctioned: the research question restated in the Conclusion, which NORTH_STAR §6 mandates. |
| `1_introduction.tex:103` ↔ `6_conclusion.tex:100` | "does multi task learning help point of interest prediction" | Sanctioned: same, verbatim question. |
| `2_fundamentals.tex:754` ↔ `3_cbic/results.tex:30` ↔ `4_courb/results.tex:14` | "one user may appear in both training and validation" | Sanctioned: the protocol-difference hygiene sentence, which the law requires at each leakage-sensitive site. |
| `2_fundamentals.tex:655` ↔ `5_mobiwac/06_results.tex:372` | "score the geometric mean of the two task metrics" | Sanctioned: the frame defining the checkpoint rule the chapter uses. |
| `5_mobiwac/02_related.tex:157` ↔ `6_conclusion.tex:203` | "on an earlier preparation of the data the cosine" | Sanctioned, and load-bearing: this is the `+0.001` scope clause traveling verbatim, exactly as NORTH_STAR §6 Ch.6 N3 requires. |
| `apx_b_errata.tex:352` ↔ `5_mobiwac/01_introduction.tex:17` | "no consistent multi task advantage for the paired category" | Sanctioned: the errata row quoting the chapter it corrects. |

No padding, no unsanctioned frame-repeats-the-papers passage at this n-gram length.

## Concordance checks that came back clean (recorded, per the persona's "an empty section is a result")

- **Region wording law.** "four of six" + TOST at the other two, with AZ never upgraded, is stated
  identically at `1_introduction.tex:141-143` (p. 14), `2_fundamentals.tex:891-894` (p. 30),
  `6_conclusion.tex:20-21` and `:93-95` (p. 77-78), `5_mobiwac.tex:33`, `5_mobiwac/01_introduction.tex:39`,
  `5_mobiwac/07_discussion.tex:13`, `5_mobiwac/08_conclusion.tex:14`, the Resumo
  (`content.tex:92-94`), and the Abstract (`content.tex:170-171`). Ten sites, one wording, correct
  verbs at each.
- **The category range.** `6_conclusion.tex:93` says "5.3 to 9.4 macro-F1 points"; the Abstract and
  Resumo say the same; `5_mobiwac/06_results.tex:135` gives "$+5.33$ to $+9.35$". Rounding of the
  same quantity, direction and endpoints preserved. Concordant.
- **The `+0.001` cosine.** `5_mobiwac/02_related.tex:159` and `6_conclusion.tex:204` both carry
  four seeds, four Gowalla states, "three of which are among the five we report", the earlier data
  preparation, and "a finding for this pair of tasks, not a general rule". Appendix F's separate
  per-epoch measurement (7 datasets, `tables/frame/cosine.tex`) states at `apx_f_cosine.tex:122-125`
  that the two sets of numbers "are not interchangeable and this appendix supersedes nothing
  there". This is the cleanest seam in the document.
- **Protocol arithmetic.** "twenty fitted models per configuration, four seeds over one fixed set
  of five folds, paired tests on the four per-seed means" appears in that form at
  `1_introduction.tex:284-289`, `6_conclusion.tex:90-91`, the Resumo, and the Abstract, and never
  as "n = 20 paired repetitions". Matches GLOSSARY §4.
- **Six-dataset scoping.** Every "all six" I checked is either immediately preceded by the
  enumeration or by "the six datasets studied, five states of the United States and Istanbul"
  (`1_introduction.tex:140`). Appendix F's seven is always disambiguated as six-plus-Georgia
  (`apx_f_cosine.tex:119-121`, `tables/frame/cosine.tex:39`).
- **Task-name bridging.** All three prefaces carry the "Next-POI Prediction" → next category
  mapping sentence (`3_cbic.tex:33-37`, `4_courb.tex:19`), Ch. 5 needs none, and §2.1
  (`2_fundamentals.tex:49-63`) states the three-way distinction plus "It does not predict the exact
  next place" once, early, as the law requires.
- **Model-lineage table** (`tables/frame/lineage.tex`) against GLOSSARY §2: six rows, DGI → HGI →
  MTLnet → ST-MTLNet → Check2HGI → joint model, spellings correct including the `MTLnet`/`ST-MTLNet`
  case split. Consistent with every chapter's usage I sampled.
- **Time-capsule integrity.** Each of the three prefaces names venue, status, and what later
  chapters revise; Ch. 4's carries the required "does not revisit the MTL-versus-single-task
  question" sentence; Ch. 5's status wording is "submitted ... under review at the time of
  writing" in the preface, the Introduction bullet (`1_introduction.tex:250-252`), and the lineage
  table caption. No site says accepted or published.
- **Objectives ↔ chapters 1:1** (`1_introduction.tex:160-172`): four objectives, mapped to Ch. 3,
  Ch. 4, Ch. 5, Ch. 6 respectively. **Limitations ↔ future work:** six limitations
  (`6_conclusion.tex`, PDF pp. 81-82), including the task-pair confound that NORTH_STAR §6 requires.
- **Abstract ↔ Resumo structural parity.** Sentence-for-sentence: same eleven moves in the same
  order, same numbers (5,3–9,4 / 5.3–9.4), same hedges ("não superou consistentemente" / "did not
  consistently outperform"), same keywords in both lists, same conditional closing. Structurally
  concordant; the value and claim halves are personas 06/07's to confirm.
- **No retired vocabulary.** Zero occurrences of `label-only ceiling`, `autocorrelation ceiling`,
  or `what the past itself allows` anywhere in the sources; `label-history benchmark` is used with
  its not-an-upper-bound caveat at `5_mobiwac/05_setup.tex:74`.

---

## COUNTS

**blockers: 0 · should-fix: 5 · nits: 4**

## UNFINISHED

The following were in scope for Gate G3 + L3/L4 and I did not reach them inside the 25-minute
checkpoint. Each is a real gap in coverage, not a pass:

1. **`main_academico.pdf` (99 pp) and `main_ppgc.pdf` (103 pp) were not opened.** The frame prose
   is shared, so my findings transfer, but the two builds differ by the pre-textual matter and the
   approval sheet, and any concordance defect confined to those parts is unaudited. `main_extra.pdf`
   (20 pp) was likewise not opened: I read the supplementary appendices from source
   (`apx_b_errata.tex`, `apx_d_ceiling.tex`) but did not verify how the defense volume's fourteen
   "Appendix B/D of the supplementary volume" pointers land in the built extra volume. The repo has
   `src_utils/check_extra_xrefs.py` for exactly this and it is reported green at this commit; I did
   not run it (build tools were out of scope for this run) and I did not verify it by hand.
2. **Notation concordance for mathematical symbols was only spot-checked.** I compared $\sigma$
   across Chapters 2 and 4 (finding N-2) and read the four equation environments in §2.2-§2.3, but
   did not systematically diff symbol usage ($\theta$, $w_k$, $g_k$, $L$, $\mathcal{D}$, $L_h$)
   across Chapters 2, 3, 4, and 5. Persona checklist item 2 is therefore only partly discharged.
3. **Duplication sweep ran at one granularity.** The 9-gram sweep catches verbatim and
   near-verbatim reuse. Paraphrased duplication (the same background explained twice in different
   words across §2.3 and `3_cbic/basis.tex` §Multi-Task Learning, or across §2.2 and
   `5_mobiwac/02_related.tex`) would not surface at n = 9 and I did not read those pairs side by
   side. Given that §2.3 and `3_cbic/basis.tex:28-54` both survey the same balancer family, this
   pair specifically deserves a human read for redundancy of *content*, not of wording.
4. **Figure and table numbers in prose were not checked against the floats.** Persona item 7's
   second clause. I verified that every `\ref` resolves to a label of the right kind, but I did not
   confirm that, e.g., "Table 6" in a List of Tables entry and the number LaTeX assigned to
   `tab:courb:category` agree in the rendered page, nor that every figure's prose description
   matches the figure printed there.
5. **Definitions-before-use ordering (persona item 4) was checked only for the terms I happened to
   trace** (macro-F1, Acc@10, Pareto vocabulary, seed, fold, gradient conflict, the three tasks).
   A full first-use ordering pass over the GLOSSARY's ~60 registered terms, confirming each is
   glossed at its first *printed* occurrence and not redefined later, was not run.
6. **I did not diff the paper chapters against their published sources.** Out of scope for this
   persona (that is L5 / persona 08's translation-fidelity gate), but it bounds SF-1 and N-2: I am
   asserting that `Average F1-Score per category` and `sigmoid` are published wording on the basis
   of the errata appendix's silence about them, not on a byte comparison with the CoUrb source.


---

<!-- estado-rodada -->
> **Rodada encerrada · último toque 2026-07-30 · sem autoridade.**
> Este ficheiro é registo de proveniência do que foi discutido nesta passagem, não fonte
> de um facto corrente. O que ficou decidido está em [`VEREDITOS.md`](../../../../VEREDITOS.md);
> os valores entregues estão em `CLAUDE.md` §0.1. Não copie nada daqui sem confirmar lá.
