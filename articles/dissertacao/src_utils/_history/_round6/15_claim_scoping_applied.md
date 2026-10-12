# 15 · Claim scoping and attribution: six items applied

> 🛑 **GERACAO SUPERADA — nenhum numero medido deste ficheiro pode ser citado.**
>
> Isto e o registo do escopo de alegacoes aplicado na ronda 6, corrido **antes** de a geracao v18 fechar o vazamento de rotulo no grafo de
> visitas consecutivas (fechado em 2026-08-13). As celulas de macro-F1 medidas aqui vem da
> geracao com vazamento e **nao sao as do documento entregue**.
>
> **Como reconhecer uma celula morta sem a copiar daqui:** a categoria entregue vive na casa dos
> **30 a 38**. Qualquer valor de categoria muito acima disso neste ficheiro e da geracao anterior.
>
> **O que este ficheiro ainda vale:** o registo de que estas questoes foram levantadas, por quem,
> e o que se decidiu. O raciocinio e o processo continuam legiveis. So os **valores medidos**
> e que caducaram.
>
> Antes de agir sobre qualquer coisa aqui, ler `VEREDITOS.md` na raiz da pasta.


**Written 2026-07-28.** This track applies the author-approved edits drafted in
[`10_protocol_recovery.md`](10_protocol_recovery.md) and [`11_citation_claims.md`](11_citation_claims.md).
Both were read in full before any edit. The job was to APPLY, verifying each drafted sentence against
the law and against the source it cites before it landed, and one drafted sentence did not survive that
check unchanged (§3, ITEM 3) while a second drafted verdict was overturned (§6, ITEM 6).

**Commit:** `519de348`. **Build, from the staged tree rather than the working tree:** defense **109 pp**,
final **105 pp**, `tex_errors=0`, `overfull_hbox=0`, `overfull_vbox=0`, `undef_cite=0`, `undef_ref=0`,
`bibtex_problems=0`, `oversized_floats=0`. **Paper:** 9 pp, `tex_errors=0`, 0 overfull, 0 undefined,
built in an isolated copy.

---

## 0 · Three things to read before the item list

**The inherited build number was wrong, and not by my hand.** The brief states 105/100 at `870f882c`.
A pristine `git archive` of that tree builds **106/101** here, twice, converged. Every page number below
is measured, and the attribution of my own contribution is measured separately in §8 rather than inferred
from a difference of totals: with only this track's six files reverted to `HEAD` and everything else left
as it stands, the build is **108/104** against the current 109/105, so **this track costs about one page
per variant**. The rest of the distance from 106/101 belongs to other work landing in this tree in
parallel. An earlier version of a comment I wrote into `tables/cbic/errata.tex` claimed the whole
106 → 109 growth for this round; that was wrong and is corrected in the committed file.

**A render defect was found at one of my own edit sites, and no source-level review could have caught
it.** At the ITEM 4 site the two cross-references were written `\\ref{...}` with a doubled backslash,
introduced in `877b2109`. In LaTeX that is a line break followed by the literal text `ref{...}`, so the
defense PDF printed `reftab:mobiwac:results; Figure reffig:mobiwac:deltas)` on p.75, in the opening
sentence of the Discussion, with two spurious line breaks. It raised no warning and did not appear in any
`undef_ref` count, because there was no `\ref` command left to be undefined. Read out of the PDF text
layer, not inferred. This is the second time in this repository that a defect hid behind a green gate,
and the shape is the same as the round-5 brace: the checker was looking for a failure mode the defect did
not have.

**Every claim about the document's own state below was measured.** All 22 edited or removed sentences
were verified in the **PDF text layer** of the built defense PDF, not assumed from source: each new
sentence present at its page, each superseded wording absent except where a footnote or an errata row
quotes it as the defect being corrected. Three of my first-pass checks reported failures that turned out
to be artifacts of my own matcher (a running header injected mid-sentence at a page break, a curly
apostrophe, and a footnote legitimately quoting the published wording); they are recorded here rather
than silently re-run, because the next checker will hit them too.

---

## 1 · ITEM 1 — COD-007, the protocol cells for Chapters 3 and 4

### What landed

**`3_cbic.tex`, "Evaluation protocol"**, four sentences appended after "using a 5-fold cross-validation
methodology.": the folds are stratified over samples rather than users, so one user's check-ins may
appear in both training and validation, with Chapter 5 named as the stricter protocol; the category
task's sample unit is the place, so no place spans two folds; the code of record pins a single random
seed, so five folds are one repetition and the reported spreads are across those folds at that seed;
training runs the full configured epochs without early stopping, each task read at the epoch of its own
highest validation macro-F1 on the fold the score is reported on.

**`4_courb.tex`**, the last of those four appended verbatim to the existing protocol sentence. The
repetition is deliberate: the two studies run the *same checkpoint code*, and WRITING_LAW's
one-name-per-concept rule argues for one phrasing rather than two paraphrases of one mechanism.

**Appendix B** gains its **first Article 1 additions paragraph**, in the register of the existing CoUrb
one, covering the preface, the convergence lead sentence and the four protocol facts. The **Article 2
count moves 8 → 9**, and the paragraph's own arithmetic still reconciles (3 frame devices + 3 protocol
facts + 3 lead sentences).

### Why these are additions and not errata

Per NORTH_STAR §4 these are **additions of protocol detail to published chapters**, not corrections of
any published claim: the published papers state a fold count and nothing else about the protocol, so
nothing published is contradicted. That is why they go in an additions paragraph rather than an errata
row, which is what the task instructed and what the evidence supports.

### Verified firsthand, not taken from the drafted report

I re-derived every cell from the code rather than trusting `10_protocol_recovery.md`, because the report
itself is a secondary source. At `9b06053f` (message `VERSION PUBLISHED`):

| Cell | What I ran | What it shows |
|---|---|---|
| Split axis | read `src/data/create_fold.py:217,:220`; grepped all five fold builders for `groups=` and `GroupKFold` | both splitters are plain `StratifiedKFold`; **zero** occurrences of `groups=` or `GroupKFold` anywhere; `:194` drops `userid` from the features |
| Sample unit | `:205`, `:209` | `placeid` is unique and becomes the index, so the category task has one row per place |
| Seed | `:159` default `random_state: int = 42`; `next_head_trainer.py:46`; `category_head_trainer.py:46`; both head configs | 42 at every commit spanning the three published run dates |
| Checkpoint | `mtl_train.py:206`, `:214-229`; `ml_history/metrics.py:107,:119-122`; `validation.py:18,:29` | one `state_dict()`, two `add_val` calls with `best_metric='val_f1'`, `>=` comparison, `deepcopy` on improvement, then two reload passes, one per task |
| The metric is macro | `engine/evaluate.py:58,:61`; single-task `trainer.py:93` | `report['macro avg']['f1-score']` and `f1_score(..., average='macro')` |
| No early stopping | `mtl_train.py:240-249,:251-254`; `configs/model.py:6,9,10` | the only two breaks are a target-F1 cutoff and a wall-clock timeout, both guarded `is not None`, and all three config values are `None`; the two target values sit commented out at `:7-8`, which is how the convergence experiment was run |

**Chapter 4 is the same code, diffed rather than assumed.** The checkpoint block in
`tarik-new/PoiMtlNet_Novo/src/train/mtlnet/mtl_train.py:226-249` is character-identical to the CBIC-era
block; `ml_history/metrics.py` differs by **five import lines and nothing else**; `validation.py:18,:29`
reload per task unchanged; the epoch loop's only breaks are `:260-269` and `:272-274` with the same three
`None` config values; `evaluate.py:58,:61` read the same macro field. The one `patience` hit in that file
is a learning-rate scheduler at `:328`, and the early-stopping variant at `:346` is commented out.

### Three things I deliberately did not write, and one caution

- **No configuration count.** The tuning budget is NOT RECOVERABLE: `git ls-tree -r 9b06053f` returns no
  sweep, tune, grid, optuna or hparam file, no search library appears in the requirements, and
  `.gitignore` was `/results/*`, so the losing configurations were never committed. The task said no
  sentence may assert a configuration count and none does. What the additions paragraph asserts instead
  is a statement about the **record**: that the number is not recoverable from the released material.
  The optional clause the drafted report offered ("No systematic hyperparameter search was performed")
  is a claim about the study's *conduct*, so I left it out and flagged it for the author.
- **No epoch count and no literal seed value.** The committed config and the committed run record
  disagree on batch size for the joint model's published run, so a config-sourced integer is not a
  witness for what a run used. The literal 42 stays out of prose, following the Chapter 4 precedent.
- **No claim that these files produced the published runs.** "The code of record" mirrors the Chapter 4
  wording the audit already accepted as correctly scoped.
- **A caution recorded at the Chapter 4 site:** `git status` in `tarik-new` reports `create_fold.py`,
  `src/configs/model.py` and `pipelines/mtlnet_trainer.py` as modified relative to `58fd219b`. The
  modifications do not touch the seed, the splitters or the checkpoint block, but the working tree is
  not the commit, and a future citation should say which.

### One consequential edit owed in a file outside this remit

`2_fundamentals.tex` says Chapter 3 "reports five-fold cross-validation **without identifying the split
axis**". That clause became **false** the moment the Chapter 3 addition landed. It is a frame chapter and
not mine to edit; the minimal repair is drafted in the comment at the Chapter 3 site and reported in §9.

---

## 2 · ITEM 2 — COD-005 residue, the balancer screen's scope, plus a parity divergence

### The scope clause

`5_mobiwac.tex` and `articles/[mobiwac]/src/sections/02_related.tex` now read "screened at their default
configurations **at a single seed** on two datasets, **Alabama and Florida**, including the two
**methods** named above".

**Two defects, not one.** The drafted report identified the missing seed and datasets. Reading the site
showed a second one: **"including the two named above" resolved to the two BALANCERS**, PCGrad and
Nash-MTL in the preceding sentence, not to a pair of datasets. Measured: neither state was named anywhere
earlier in the file. So the phrase was not merely incomplete, it pointed at the wrong antecedent, and
"the two **methods** named above" is now explicit. An earlier anchor table had recorded this site as
already naming the two datasets; that reading was wrong and the correction is recorded at the site.

**Source, opened this session.** `T4_audit_and_verdict.md:8-10`, the evidence-strength banner: the full
screen ran at registry defaults, seed 0, AL+FL. Restated at `:111-112` under "Caveats / scope". The AL+FL
expansion is not inferred from the abbreviation: `T4_full_screen.json` has exactly **two** top-level keys,
`alabama` and `florida`, each holding exactly **19** arms, which I enumerated from the JSON.

**Literal "seed 0" stays out of prose**, per `articles/[mobiwac]/GLOSSARY.md:113`, which gives "a single
seed" as the phrasing and bans the compound "single-seed states". Nine words added; no number, count or
verb changed.

### The parity divergence, established rather than assumed

The task asked me to determine which text was right. **The dissertation was.** I read the artifact
myself: `R0_matched_metric_bar.json` has exactly four keys under `states` (`alabama`, `arizona`,
`georgia`, `florida`) and `"seeds": [0, 1, 7, 100]`, and `scripts/mtl_improvement/plot_grad_cosine.py`
reads its per-state run directories out of that same JSON with a `STATE_STYLE` map naming the same four.
So: **four Gowalla states at four seeds each**, of which three are among the five U.S. datasets the
document reports. The paper's "three of our six datasets" both undercounted the pool and implied every
state in it is one the study reports. The dissertation's wording was carried into the paper, with "this
dissertation" rendered as "this study". The correction runs in the study's favor: the finding replicates
on a state the paper never reports.

---

## 3 · ITEM 3 — COD-005 sub-claim 4, the Nash-MTL guarantee

### Where I departed from the drafted sentence

The drafted clause read "at points that are not Pareto stationary, and under the method's assumption that
the task gradients there are linearly independent". I applied a **glossed** version instead:

> Away from a Pareto-stationary point, meaning a point at which some convex combination of the task
> gradients is zero, and under the method's assumption that the gradients are linearly independent there,
> that direction is a descent direction for every task, avoiding the dominance of one task over the other.

**Why.** "Pareto stationary" is **not in GLOSSARY.md**, and the registry is fail-closed. WRITING_LAW §1
also requires every term to be defined once at first use. The document's first use is in Chapter 3's
published formal formulation, which carries "Pareto-stationary point" with no gloss; expanding a published
sentence for no reader gain would be a further edit to a published article, so the gloss is placed at the
use that carries a claim. The plain reading is the source's own (arXiv:2202.01017 p.2, restated p.6). The
hyphenated spelling matches Chapter 3's, so the two chapters name one concept one way. **The registry
entry is proposed, not registered** — see §9.

### The guarantee, verified at source

PDF of arXiv:2202.01017 downloaded and read (19 pp.), arXiv comment field "ICML 2022". Every quotation
re-checked against the extracted text by exact substring match: **5 of 5 verbatim**.

| Where | What it establishes |
|---|---|
| p.1 abstract | "Under certain assumptions, the bargaining problem has a unique solution" — conditional in the authors' first sentence about it |
| p.6 | "Since our update rule is a descent direction for all tasks" — the property, in their words |
| p.3, Assumption 5.1 at p.6 | "if θ is not Pareto stationary then the gradients are linearly independent" |
| p.3, Claim 3.1 | scoped to the case where θ is not on the Pareto front |
| p.3, on Axiom 2.4 | "the solution can easily be dominated by a single direction" — independently supports the retained published clause about dominance, so that clause was **kept, not cut** |

**The correction does not go soft.** "Is a descent direction for every task" is the authors' own phrasing
and is stronger and more precise than the published "beneficial". "Aims to" or "seeks to make" would have
been *weaker than the source*, which is the other failure mode. The twenty-iteration concave-convex
approximation (p.4) is deliberately **not** imported into the sentence: it is an implementation fact, not
part of the stated guarantee, and it belongs in the errata row, where the neighbouring Nash cost
correction already discusses it.

### The errata trail

One row added to `tables/courb/errata.tex`. **And one clause widened** in Appendix B: the CoUrb section
banner said the corrections "replace the published numbers", which the new row is not. It now distinguishes
the first three number corrections from the fourth, a claim narrowing. Giving the CoUrb section a second
table was the alternative and is more structure than one row justifies.

---

## 4 · ITEM 4 — COD-004, the Chapter 5 trunk attribution

### What the site said, and what it says now

The prose already read "the joint architecture lifts the next-category task" after round 5. That is
weaker than the "shared trunk" version it replaced, but **it still asserts a locus**, one page after the
chapter refuses to name one: the freeze-control paragraph says "we attribute the gain to the joint
architecture rather than to any named component of it" and closes "we do not name the shared trunk as the
source, and we do not present the ablation as evidence against it either."

I read the 44-line comment block at that site, as instructed. It records the disconfirming arm with its
numbers, and those numbers are why the attribution cannot stand: at Florida, five folds by fifty epochs,
category macro-F1 **68.36 ± 0.74** with cross-attention on against **68.32 ± 0.67** off, a difference of
**−0.04 ± 0.13** that a paired Wilcoxon cannot separate from zero (W+ = 5, p = 0.6250), from
`F50_T1_5_CROSSATTN_ABSORPTION.md:19-20,:37`. Its own record calls that null "misleading" and a "hidden
compensation effect" (`:229`), so it is **not evidence against the trunk either**, and neither text
presents it as such.

The opening sentence of the Discussion now states the **result**, which the tests license, with the scope
clauses the author approved:

> One model serves both tasks. In one forward pass it outperforms the dedicated category model at all six
> datasets, and on region it outperforms the dedicated model at four of them and matches it within a
> two-point margin at the other two, with the region output keeping a private spatial path
> (Table 5.2; Figure 5.4). Which part of the joint architecture produces the category gain is not settled
> by the controls reported here (Section 5.6.2).

Each verb is bound to its test per WRITING_LAW §3, the region split is four "outperforms" and two TOST
matches, **Arizona is not upgraded**, and no number is added. The private spatial path claim is retained:
it is architectural, not an attribution of the gain.

### The paper side, and one divergence I am declaring

The submitted paper still carried the **original** wording in two places, so this round is the first time
the softening reaches the version of record at all:

- `07_discussion.tex:13` read "the shared trunk carries the semantic context that lifts the next-category
  task". Same replacement applied.
- `06_results.tex` asserted "we therefore attribute the category gain to a stronger shared trunk" and
  closed "We report this attribution as a finding, not a hypothesis." **Softening only the discussion
  would have left the paper contradicting itself two sections apart**, so this paragraph was softened
  too. The negative result is kept as a finding, since the control does establish it; only the component
  attribution is withdrawn.

**Declared divergence.** Chapter 5 states the disconfirming ablation with its numbers and its two limits,
because it has the room; the paper does not. The two texts are therefore **not word-identical at that
paragraph**. What is identical is the **strength** of the claim, which is the property the parity rule
exists to protect: neither text now names a component as the source. Recorded in the article's ERRATA.md
so the asymmetry is not later read as an oversight.

---

## 5 · ITEM 5 — the Standley citation

### The correction

The bullet keeps its position, its `\textbf{Empirical Performance:}` label (so no heading changes inside
published prose) and its role in the argument, and reduces to the claim the cited work supports:

> **Empirical Performance:** In practice, sharing one network across tasks reduces inference cost, since
> a single network is evaluated rather than one network per task [ref].

with a footnote reproducing the published sentence and stating the cited work's own position, and a row
in `tables/cbic/errata.tex`.

### The false earlier claim, checked as the task required

Commit `83d1d8c5` retracted an earlier draft's assertion that Standley "makes no claim about training
speed". **I verified the false version reached neither the applied footnote nor the applied errata row.**
I also re-ran the measurement myself on the session's own PDF copy: `faster training` occurs **0** times,
but `training time` occurs **7** times and `reduced training time` **once**, at p.1, inside a list the
paper explicitly hedges "in theory". The applied prose says exactly that: the work "names improved
accuracy and reduced training time among the benefits joint training may have ``in theory''". The
absence-of-a-string claim is nowhere in the applied text.

### Source verification

PDF of arXiv:1905.07553 downloaded and read (13 pp.), arXiv comment "Presented to ICML 2020". Quotations
re-checked by exact substring match: **7 of 7 verbatim**, after normalizing the extractor's hyphenation
artifacts (an early check reported 2 misses that were purely an artifact of a private-use hyphenation
glyph, which is recorded here because the next checker will hit it).

| Claim | Verdict at source |
|---|---|
| inference saving | **Supported**, p.1 abstract |
| "matches or exceeds ... more complex architectures" | **Contradicted**: p.1, "this often leads to inferior overall performance as task objectives can compete"; p.2, UberNet "experiences a rapid degradation in performance as more tasks are added"; p.2, "multi-task learning is often inferior to single task learning with multiple networks" |
| "faster training" | **Named only as a theoretical possibility** (p.1), while every other training-time passage concerns the cost of the paper's own grouping search (§5.3 p.6; the 45-versus-95-percent comparison p.7), and p.9 concedes the framework "can be costly at training time" |

**One result that would favor the bullet, recorded in the errata row rather than suppressed:** p.7 reports
that at a matched parameter budget, multi-task networks with 3, 4 or 5 tasks outperform single-task
networks on average, "Nevertheless, two-task networks still do not compare favorably." **This chapter's
model has exactly two tasks**, so the one result leaning the bullet's way excludes this chapter's own case.

### The commit-history question, with its limit stated

**The load-bearing negative, stated first because it is the part that does not move.** Walking
`git rev-list --all` and extracting this bullet from every tree that contains either path yields **1729
blobs carrying it and exactly one distinct bullet text**, with `\cite{standley2020tasks}` attached in all
of them; the earliest is `223f5df7` at `:85`. No commit count is needed for that, and none of it depends
on which probe string is used.

**A commit roster is the wrong instrument here, and I got it wrong twice before that became clear.**
`git log --all -S<string>` counts *occurrence changes*, so its output moves as this round's own commits
edit the bullet and its comment, and it moves **differently per probe**. Measured 2026-07-28, over both
the pre-reorganization path (`CBIC___MTL/sections/`), the current one
(`articles/CBIC___MTL/sections/`) and this chapter:

| Probe | Roster returned |
|---|---|
| `standley2020tasks` | `223f5df7`, `83e40091`, `689b0d6e`, `1a29b545`, **`232befd5`** |
| `matches or exceeds` | `223f5df7`, `83e40091`, `689b0d6e`, `1a29b545`, **`76d92f22`** — no `232befd5` |
| `Empirical Performance` | `223f5df7`, `83e40091`, `689b0d6e`, `1a29b545`, **`232befd5`, `76d92f22`** |

`232befd5` is absent from the second probe because **this round removed the "matches or exceeds" wording
from the bullet**, so that commit changes the occurrence count of one string and not the others; `76d92f22`
then entered two rosters when it rewrote this very comment. So reporting one merged five-commit list "for
all three probes", which the previous version of this section did, was **false for at least one probe no
matter which list was chosen** — the reviewer was right, and the defect is that a moving instrument was
quoted as a fixed one.

Those three rows were re-verified against the live command, set for set, at the time of writing. **They
will drift again**: any later commit touching one of the three strings enters that probe's roster and not
the others, and the row for a probe whose wording this round changed will keep diverging from the rest.
Read the table as a dated observation, not as a fact about the repository. The two claims below do not
drift, and they are the ones to cite.

**Exclude this round's own commits and the instability disappears.** All three probes then return the
**same four**, and this is the roster to cite:

| Commit | Date | What it is |
|---|---|---|
| `223f5df7` | 2025-10-21 | the import of the CBIC article tree |
| `83e40091` | 2026-05-01 | BRACIS release branch, article tree unchanged |
| `689b0d6e` | 2026-07-08 | MobiWac release branch, likewise |
| `1a29b545` | 2026-07-23 | the dissertation re-typeset |

Restricted to the article tree alone, all three probes return the same three, without the re-typeset.

**Two further corrections to the first version of this section.** It named `643c686e` in the roster:
that is the import commit on the *current* path and appears in the **file history**, not in any `-S`
result, and conflating the two was the error. And it said
`articles/CBIC___MTL/sections/method.tex` was touched by **exactly one commit**; across all refs the file
history shows **three** (`643c686e`, `689b0d6e`, `83e40091`), the two later ones release branches. The
same per-probe correction was applied to the comment at the citing site in `3_cbic.tex`.

**The limit, stated and not papered over:** the CBIC LaTeX entered version control on **2025-10-21, after
publication**. Pre-submission drafts of this bullet are not in this repository at all, so the question
cannot be answered from here in either direction. What is established is narrower: **no substitution
happened after the LaTeX entered version control.**

---

## 6 · ITEM 6 — COD-006, the word "identically"

**Verdict: it overstates, and I narrowed it.** This reverses an earlier audit round, which recorded the
word as REFUTED on the ground that the per-model selection objectives are disclosed elsewhere in the
chapter and the non-cancellation caveat is the next sentence. Both of those facts hold, and neither
disposes of the problem, because of **what the word modifies**.

**What it modifies.** It sits inside a *mitigation*, in the limitations paragraph, whose job is to bound
how far the optimistic-score bias reaches into the joint-versus-dedicated comparison. A word that makes a
mitigation sound stronger than it is **understates a limitation**, and WRITING_LAW §3 forbids that
direction as firmly as it forbids upgrading a result. The earlier round judged the word against the
question "is this a contradiction?" — it is not — rather than against the question "does this understate a
limitation?", which is the one that governs here.

**Measured, in this chapter.** The selection rule states "each dedicated model at its task's best epoch,
and the joint model at the epoch selected by its joint validation score (the geometric mean of the two
task metrics)". So the **procedure** is shared (one saved model per fold, epoch chosen on validation,
score read on that same fold) and the **objective differs by model**. "Identically" asserted both. Now:

> the selection rule is the same for both models on the same folds, an epoch chosen on validation and read
> on that fold, with each model selected on its own validation objective (Section 5.6.2), and the
> dedicated model receives the wider search ...

"On the same folds" is kept, since it is what makes the comparison paired; the following sentence
declining to claim exact cancellation is untouched. Two-file change, with the paper's own
`sec:results-part2` label on that side.

---

## 7 · One regression I caused, and the fix

Adding the Standley row made `tables/cbic/errata.tex` **taller than the text block**, and a float cannot
break across pages: `Float too large for page by 190.30908pt`, `oversized_floats=1` in both variants. This
is a regression against the inherited state and the brief forbids it.

**Fixed by the precedent already in the repository**: converted `table` → `longtable`, exactly as
`tables/frame/bib_errata.tex` was converted in round 5 for the same reason. All eight rows, the caption,
the label and `\small` preserved; the `{\small ...}` group's braces verified balanced (33/33 on the
comment-stripped file), since dropping that opening brace is what stopped every build for six commits in
round 5. `\centering` was dropped rather than lost: longtable centers through `\LTleft`/`\LTright`.

**The conversion costs zero pages, isolated rather than assumed.** In a scratch copy, this round's eight
rows put back into the original float container also build **109/105**, with the warning present in both
variants. So the conversion removes the warning and moves no page.

---

## 8 · Build, and what I measured how

| Quantity | Value | How |
|---|---|---|
| Defense pages | **109** | `make defense` + `build.sh` on the **staged tree**, extracted with `git write-tree` and `git archive`, so the number describes what was committed rather than a working tree holding other agents' edits |
| Final pages | **105** | same |
| `tex_errors` | **0** both | `build.sh`; `make` also exits 0, which is the honest signal |
| overfull hbox / vbox | **0 / 0** both | `build.sh` |
| `undef_cite` / `undef_ref` | **0 / 0** both | `build.sh` |
| `bibtex_problems` | **0** both | `build.sh` |
| `oversized_floats` | **0** both | `build.sh`, after §7 |
| Paper | **9 pp**, `tex_errors=0`, 0 overfull, 0 undefined | isolated copy of `articles/[mobiwac]/src`, three `pdflatex` passes with `bibtex` |
| HEAD baseline | **106/101** | pristine `git archive` of `870f882c`, built twice, converged |
| **This track's own cost** | **108 → 109 defense, 104 → 105 final** | second scratch copy with only this track's six files reverted to `HEAD`, everything else as it stands |
| Render verification | **22 of 22** | PDF text-layer search of the built defense PDF, with hyphenation, curly quotation marks and running headers normalized |

`make check` **fails on one gate that is not mine and that I did not fix**: the recorded page counts in
`CLAUDE.md`, `PLAN.md`, `PENDENCIAS.md` and `codex_reviewer.md` still say 104/99 against the measured
109/105. Running `sync_page_counts.py --write` would edit four governance files outside this remit while
the count is still moving under other agents' work. Every other gate passes: em-dashes 0, contractions 0,
banned words OK, codenames OK, unresolved refs and cites OK, bibtex OK, sweep-guard self-tests 4/4,
word-count reconciliation OK, torn sentences 0, trapped prose 0 with 10/10 fixtures.

The two "banned verdict verb" hits at the Nash sites are the sweep matching the word **Pareto**, in
`Pareto-optimal`, `Pareto efficiency` and `Pareto-stationary`; three of the four flagged lines are
pre-existing published prose. The one contraction-style hit in `apx_b_errata.tex:300` ("This article
differs...") is pre-existing and refers to the MobiWac article as an article, which is correct.

**Law compliance of my own new prose, measured** over the added non-comment lines (114 against the
working-tree diff at the time of the sweep; 108 against `870f882c`, the difference being lines another
agent's interleaved commit had already carried): 0 banned words,
0 banned templates, 0 repo codenames, 0 em-dashes or en-dashes, 0 contractions, 0 British spellings,
0 banned verdict verbs. The single "robust" hit is inside the published sentence I extended, and
WRITING_LAW §4.6 explicitly declines to ban it.

---

## 9 · Errata rows added, and every `[NEEDS SIGN-OFF]` left

### Errata rows and appendix prose

| Where | What |
|---|---|
| `tables/cbic/errata.tex` | **1 new row**: the Standley claim narrowing, naming the cited work's own position and the two-task exclusion, and recording that the correction runs against the chapter's interest. Table converted to `longtable` (§7). |
| `tables/courb/errata.tex` | **1 new row**: the Nash-MTL guarantee narrowed to what the method's paper derives. |
| `apx_b_errata.tex` | **New Article 1 additions paragraph** (did not exist). CoUrb additions count 8 → 9. CoUrb section banner widened to cover a claim narrowing. **Reconciliation header re-measured**: the previous "6 + 13 + 3 + 14 = 36" had two stale terms *before* this round; measured now, 8 + 13 + 4 + 18 = **43** itemized rows, with the MobiWac scope table's 2 counted separately. |
| `articles/[mobiwac]/ERRATA.md` | **New dated section with four entries**, one per Ch.5-side change, each with its source and the declared divergence of §4. |

**No erratum row was added for ITEM 1**, by design: those are additions of protocol detail, not
corrections of a published claim.

### `[NEEDS SIGN-OFF]` markers I left — six

Total in `src/` is now **43**, measured. Mine:

1. **`3_cbic.tex`, protocol addition** — four sentences of new protocol detail in a published chapter.
   Names the optional tuning-budget clause I did **not** add and asks whether he wants it.
2. **`3_cbic.tex`, Standley bullet** — a claim change in published co-authored prose that removes a stated
   advantage of the architecture the chapter adopts. Names the cheaper alternative (preserve and disclose)
   and why I did not choose it.
3. **`4_courb.tex`, checkpoint sentence** — one new protocol sentence in a published chapter.
4. **`4_courb.tex`, Nash narrowing** — a claim narrowing in published co-authored prose. Offers the
   footnote variant if he prefers the published sentence intact.
5. **`5_mobiwac.tex`, trunk attribution** — flags that the opener is now three sentences rather than one,
   and names which sentence to cut if he wants it shorter.
6. **`5_mobiwac.tex`, "identically"** — a limitations sentence, changed so the paragraph is slightly less
   favorable to the study.

Plus **one proposed GLOSSARY entry**, recorded at the Chapter 4 site and not treated as registered:

> **Pareto-stationary point** — a point at which some convex combination of the task gradients is zero; a
> necessary condition for Pareto optimality. Used in Chapters 3 and 4 in the Nash-MTL description.

---

## 10 · `[VERIFY]` flags

1. **[VERIFY: `2_fundamentals.tex` split-axis clause]** "Chapter 3 reports five-fold cross-validation
   without identifying the split axis" is **now false**. Frame chapter, outside this remit. Minimal repair
   drafted in the comment at the Chapter 3 site: "Chapters 3 and 4 both stratify by sample rather than by
   user, so the check-ins of one user may appear in both training and validation, and only Chapter 5
   splits by user."
2. **[VERIFY: `make check` page-count gate]** Four governance files record 104/99 against the measured
   109/105. Deliberately not fixed while the count moves under parallel work.
3. **[VERIFY: nash page range]** `references.bib` gives `pages = {16428--16446}` for the Nash-MTL entry.
   I confirmed the venue (ICML 2022, from the arXiv comment field) but **not** the page range; PMLR is
   outside the network allowlist. Inherited from `10_protocol_recovery.md` and still open. The precedent
   in this same bibliography was to drop an unverifiable page range.
4. **[VERIFY: the published joint-model next-category column]** Inherited and unclosed: no run artifact in
   this repository reproduces that column. No sentence I added claims reproducibility, and none should.
5. **[VERIFY: doubled-backslash class]** I fixed the one instance at my own site and swept `chapters/` and
   `tables/` for `\\ref{` and `\\cite{`. One hit remains and it is **inside my own comment** at that site,
   quoting the defect in order to describe it; there is no remaining instance in prose. But the defect is
   invisible to every existing gate: it produces no warning and cannot raise `undef_ref`, because no
   `\ref` command survives to be undefined. A checker for it is worth adding and I did not write one
   (outside this remit). The check itself is one line: a grep for `\\\\ref{` or `\\\\cite{` on
   comment-stripped source.

---

## 11 · What I could not confirm

- **Whether the CBIC paper's pre-submission drafts cited a different work at the Standley site.** The
  repository's earliest `.tex` postdates publication. Established instead: no substitution after the LaTeX
  entered version control (§5).
- **The number of configurations examined in either study.** Not recoverable from artifacts (§1).
- **Whether the epoch counts in the committed configs are the counts the published runs used.** The
  config and the run record disagree on batch size for one published run, which is enough to distrust the
  config as a witness. No sentence I added quotes an epoch count.
- **The Nash-MTL page range** (§10 flag 3).
- **Whether the drafted `load-bearing` ranking of `11_citation_claims.md` matches the author's sense of
  the argument.** I applied only the two rows this track was assigned; the other twenty-three remain that
  report's open items.
- **My own attribution of the page growth beyond this track.** I measured that this track costs about one
  page per variant and that a pristine HEAD builds 106/101, but I did not attribute the intervening
  108/104 to specific other work; another agent committed to these same files (`232befd5`) while this
  track was in progress, and the working tree still holds uncommitted edits by others in
  `06_results.tex`, `05_setup.tex` and four `src_utils` documents.
- **Anything about the two chapters' figures or the rest of the document.** I verified the render only at
  my own sites, plus the one defect that verification exposed.

---

## 12 · A note on the shared tree

`232befd5` ("Address dissertation review corrections") landed in these same ten files while this track was
being applied, so my working files were committed by another hand mid-flight; my own commit `519de348`
therefore carries only the final correction to `tables/cbic/errata.tex`. **Every edit of this track is in
`HEAD` and verified there**, re-checked string by string after the fact (19 of 19 present, 8 of 8
superseded wordings absent outside comments that quote them as defects).

Other agents' uncommitted work was **not** committed by me. `06_results.tex` in particular held another
agent's statistical-wording edits alongside my paragraph; I staged that file through a blob built from
`HEAD` plus my paragraph alone, leaving their eight lines in the working tree. Their edits in
`05_setup.tex`, `review/questions.md`, the two PDFs and the four `src_utils` documents are untouched.


---

<!-- estado-rodada -->
> **Rodada encerrada · último toque 2026-07-28 · sem autoridade.**
> Este ficheiro é registo de proveniência do que foi discutido nesta passagem, não fonte
> de um facto corrente. O que ficou decidido está em [`VEREDITOS.md`](../../../VEREDITOS.md);
> os valores entregues estão em `CLAUDE.md` §0.1. Não copie nada daqui sem confirmar lá.
