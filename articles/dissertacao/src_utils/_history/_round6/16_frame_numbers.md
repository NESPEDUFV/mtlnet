# 15_frame_numbers.md — the frame chapters' numbers and scopes, plus two approved additions

**Round 6, 2026-07-28.** Track: Ch.1, Ch.2, Ch.6 and the appendices (the author's own prose, no
errata cost, new prose marked `[NEEDS SIGN-OFF]`). Six items. **Commit `456eaa72`.**

One sentence of orientation before the findings: **the item the brief ranked first needed no edit,
and the item nobody flagged as a falsehood was one.** NUM-3 was already correct at every locus;
Appendix C asserted that the dissertation "passed an eighteen-reviewer panel" that its own
consolidated report records as having failed it at two gates.

---

## 0 · Build, measured in an isolated tree, and why

The shared worktree at `870f882c` is **dirty with another track's work**: `4_courb.tex`,
`apx_b_errata.tex` (both modified) and a new untracked `apx_b_static_scope.tex`. Building there
gives 106/101 pp, and attributing those pages to my edits would have been exactly the class of
unchecked self-claim this round exists to stop. So both measurements below were taken in
`/tmp/r6t3_scratch`, a `git archive` of `870f882c` containing **only** my three files as changes
(verified file-by-file with md5 against `git show`; `0_main.tex` and every table byte-identical).

| | DEFENSE | FINAL | tex_errors | overfull hbox | overfull vbox | undef_cite | undef_ref | bibtex | oversized floats |
|---|---|---|---|---|---|---|---|---|---|
| baseline, clean `870f882c` | 105 | 100 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| **with my three files** | **108** | **103** | **0** | **0** | **0** | **0** | **0** | **0** | **0** |

`make defense && make final` exit 0 (the `-halt-on-error` signal), zero `^!` lines in the log.
**No gate regressed.** Three pages of growth, all in Ch.2 and Appendix A, from the added content.

**Chapter 2 span, measured on the render:** pp. 19-27 carry a Chapter 2 running head, so 10 pages
including its unheaded title page. Inside the 8-12 page target for a thin chapter.

**Two new low-text pages appeared (defense pp. 27 and 92) and both are benign.** I looked at them
rather than assuming: p. 27 carries 116 words, the tail of §2.5, and p. 92 carries 93 words, the
two closing qualifications of the new Appendix A section. Ordinary chapter-terminal pages, not
near-blanks like the 21-word p. 4 that `ANCHORS.md` §2 records.

**`make check` fails, at baseline too.** It reports 10 stale page-count claims in `CLAUDE.md`,
`PLAN.md`, `src_utils/PENDENCIAS.md` and `src_utils/codex_reviewer.md` (they record 104/99).
I ran the same check against the *baseline* documents and it fails identically, so this is
inherited, not caused. Those four are durable law/tracking documents belonging to other remits,
and `sync_page_counts.py --write` would rewrite them while three tracks are mid-round with page
counts still moving. **Left for whoever closes the round.** Everything else in `make check` passes:
word-count claims reconcile, 0 torn sentences, 0 trapped-prose suspects, 10/10 fixtures.

---

## 1 · ITEM 1 (NUM-3) — the region-task count. **No edit needed, and that is the finding.**

The brief states Ch.6 says "three of the six". **It does not, anywhere.** A sweep for
`three of (the )?six`, `três dos seis` and their variants over every `.tex` in `src/` returns
**nothing** (exit 1), and the same sweep over the text layer of both rendered PDFs returns nothing.
`ANCHORS.md` §3 already recorded this as corrected in an earlier round; I confirmed it rather than
trusting the row.

I enumerated **every** rendering locus that states a count for this result, comment lines excluded,
by parsing all eleven chapter files plus `0_main.tex` plus the six `\input` tables (27 count-claims
of any kind; the region-count subset is below):

| Locus | Line (2026-07-28) | What it says | Verdict |
|---|---|---|---|
| `0_main.tex` Resumo | 241 | "supera em **quatro dos seis** conjuntos" | correct |
| `0_main.tex` Abstract | 330 | "outperforms at **four of six** datasets" | correct |
| `1_introduction.tex` | 132 | "on the region task at **four of six**" | correct |
| `2_fundamentals.tex` | 600 | "on the next region at **four of six** datasets" | correct |
| `5_mobiwac.tex` preface | 28 | "the dedicated region model at **four of the six**" | correct |
| `5_mobiwac.tex` §5.1 | 67 | "it outperforms at **four of the six** datasets" | correct |
| `5_mobiwac.tex` §5.7 | 834 | "on **four of the six** datasets" | correct |
| `6_conclusion.tex` opening | 21 | "on the region task at **four of the six**" | correct |
| `6_conclusion.tex` §6.1 | 75 | "on the region task at **four of six**" + names the four | correct |

**Established independently from the results table**, not from the prose that agrees with it. I
parsed `tables/mobiwac/results.tex` for its own marks (and corrected my first parser, which
silently dropped the Istanbul row because it follows `\midrule` — the kind of off-by-one that
would have produced a confident "three"):

- region block: **4** `$^{\uparrow}$` marks = Istanbul, FL, TX, CA (the caption defines the mark as
  "a statistically supported improvement over the dedicated model")
- region block: **2** `$^{\approx}$` marks = AL, AZ ("a non-inferior match (TOST, $\pm2$ pp)")
- category block: **6** bold cells = all six datasets

Corroborated in the significance record, `v17_completion/stats_n20/RESULTS.md`: the region TOST
table (:87-90) gives all four of AL/AZ/FL/Istanbul the verdict **matches (TOST)**, with FL and
Istanbul additionally CI-positive, and :139/:141 give CA and TX region point estimates above the
2-pp margin. **The four are Istanbul, FL, TX, CA and the two matches are AL and AZ**, exactly as
the document says. AZ is never upgraded anywhere (its 90% CI lower bound is +0.001, and :197 says
so explicitly).

**Two loci differ because they scope something narrower, and I left both alone:**

1. `6_conclusion.tex:177` — "four Gowalla states, **three of which are among the five we report**".
   This is the *gradient-cosine* measurement, whose pool is four states including Georgia, which is
   not one of the dissertation's six datasets. Different quantity, correctly scoped, and the
   comment at :183 records the correction. Flattening this to "four of six" would have created a
   falsehood while "fixing" a non-defect.
2. `6_conclusion.tex:220` — "**two of the six** datasets" for the capacity-matched control. A
   different control with its own scope, quoted from its README.

**Nothing was changed in `0_main.tex`.** The count there was already right, so the coordination the
brief asked for with the Resumo/Abstract track cost zero touches. That file is untouched in my
commit.

---

## 2 · ITEM 2 (NUM-4) — the HGI sweep number. **Corrected, and the convention added.**

Re-anchored by phrase: "rose monotonically from 0.74 to 0.82" (`2_fundamentals.tex:172` before the
edit). The clause carried **two means with no spread, no swept range, and no epoch budget**.

**The trace, and the defect it exposed.** 0.74 and 0.82 are quoted from
`research/embeddings/hgi/CLAUDE.md:117`, a Gotchas bullet. But that bullet **itself rounds** the
sweep table it points at. So the page was quoting a rounded restatement of the source of record,
which puts a computed step between the document and its evidence, and drops the spreads that
`AGENT_GUARDRAILS` N-5 and `WRITING_LAW` §3 both require of a reported mean.

**The source of record**, `research/embeddings/hgi/README.md`:544 (header) and :548-551 (rows):

| `w_r` | Cat F1 | source line |
|---|---|---|
| 0.4 (published) | 0.7388 ± 0.0205 | :548 |
| 0.5 | 0.7678 ± 0.0211 | :549 |
| 0.6 | 0.7944 ± 0.0186 | :550 |
| **0.7 (adopted)** | **0.8186 ± 0.0123** | :551 |

Convention, quoted from the table's own header: **5 folds × 50 epochs**, Alabama, four settings.
The sentence now names the swept range, the fold count, the epoch budget, both endpoint means with
their spreads, the zero-to-one scale, and what the spread is taken across. Monotonicity is the
source's own word (`CLAUDE.md:117`, `preprocess.py:38`) and is readable off the four rows without
computing anything. The adopted 0.7 is the shipped default (`preprocess.py:23`).

**Verified firsthand at the publisher's own text**, not from another paper's bibliography: the HGI
PDF in the repository, p. 4, Eq. 2 — the paper's factor differentiates intra-region and
cross-region edges, at 0.4 for the cross-region case. So "set to 0.4 for the dense Chinese cities
they study" is the paper's own value and the retuning to 0.7 is a real departure, correctly
disclosed.

**`[VERIFY]` left open (pre-existing, and I did not close it):** no source names the *averaging*
convention of "Cat F1" (macro or weighted). This is why the sentence says "category F1" and not
"macro-F1", and the author should either confirm the convention or drop the two values and keep the
clause qualitative. Closing this by assuming macro would have been the smoothing this round bans.

---

## 3 · ITEM 3 (COD-013) — the joint model's descent from MTLnet. **Named, in the frame.**

Before: the descent was carried **only by row order** in `tables/frame/lineage.tex`. No sentence in
the document said the joint model is a descendant of MTLnet.

**Established from the code, read this session** (every line number re-checked after drafting,
which caught two of my own citations being off — `_build_shared_backbone` is at :362, not :364-368,
and the private-path comment at :86-90, not :90-93; both corrected in the file):

```
mtlnet_crossattn_dualtower/model.py:42   class MTLnetCrossAttnDualTower(MTLnetCrossAttn)
mtlnet_crossattn/model.py:207            class MTLnetCrossAttn(MTLnet)
mtlnet/model.py:39                       class MTLnet(nn.Module)
```

So the chain is base → cross-attention variant → dual-tower, two specializations deep. What the
subclass overrides is **one component**: `_build_shared_backbone` (:362), whose docstring (:368)
reads "Override MTLnet's FiLM + shared\_layers with cross-attention blocks", and whose body
registers the cross-attention blocks and two LayerNorms and nothing else. The FiLM + residual stack
it displaces is `mtlnet/model.py:193-197`. Encoders, heads and the parameter partition are
inherited (:208-214 class docstring; accessors at :554, :563, :578). Each block lets one stream
read the other while each keeps its own feed-forward weights (:55-66, and :63 "Separate FFNs per
task, no parameter sharing"). The second specialization hands the region output the raw region
sequence (module docstring :1-9, and :86-90).

**Where it landed, and why — decided on the science.** Ch.2's lineage discussion, immediately after
`Table~\ref{tab:fund:lineage}`. The fact is about the **relation between two chapters' artifacts**,
which is the frame's own subject, and it is what licenses reading Ch.3's null against Ch.5's
positive result at all. Within the MobiWac paper the joint model stands alone and needs no
ancestor, so putting the sentence in Ch.5 would have bought a two-file change to a manuscript under
review for a fact that chapter does not use. **Free in the frame, costly in Ch.5, and better placed
in the frame on the merits.**

The registry id `mtlnet_crossattn_dualtower` does **not** appear in the prose (`WRITING_LAW` §2
names it explicitly as a banned repo codename); it appears only in the LaTeX comment that carries
the provenance, which is where the author and an auditor need it.

---

## 4 · ITEM 4 (COD-015) — the Check2HGI loss equation. **Added to Ch.2, not Ch.5.**

Measured first, since the brief's figure invited a check: **§5.4.1 has 244 rendering words, zero
equations, zero figure floats.** (The brief says 228 words; the difference is a counting convention
on LaTeX markup, and the substance — no equation anywhere — is identical.)

**Transcribed from `docs/context/check2hgi_overview.tex`, section "Função de Perda"**, whose three
display equations are the three now in the document, in the source's own notation:

1. `L = 0.4 L_c2p + 0.3 L_p2r + 0.3 L_r2c` (the total objective, one term per hierarchy boundary)
2. `D(e_1,e_2) = σ(e_1^T W e_2)` (the bilinear discriminator)
3. `L_* = -log D(e^+,e^+) - log(1 - D(e^+,e^-))` (the per-boundary term)

Kept from the source: `\mathcal{L}`, `\mathcal{D}`, the c2p/p2r/r2c subscripts, `e^+`/`e^-`, `W`,
`σ`, the star on `L_*`, and all three weights. Dropped: its `\underbrace` annotations (their content
is now in the prose) and its Portuguese labels. **No notation was invented.** Every symbol is
defined at first use in the sentence following its equation.

**Confirmed in the running code**, because a documentation .tex is not by itself evidence the
objective is the shipped one: `Check2HGIModule.py:51-53` (`alpha_c2p=0.4, alpha_p2r=0.3,
alpha_r2c=0.3`), assembled at :1192-1195; the per-boundary term at :1159/:1184/:1189 in exactly the
source's `-log(pos) - log(1-neg)` form; the discriminator at :1003-1018 (matmul, elementwise
product summed, sigmoid) and :246 "Bilinear transformation weights for discrimination at each
boundary". Same three weights in the pipeline config, `check2hgi.pipe.py:43-45`.

**Where it landed, and why — decided on the science, as the brief asked.** Ch.2, in the
representation section. That is the point where the dissertation builds the infomax line, DGI's
local-global objective and then HGI's hierarchical one, so the fourth boundary reads as *a term
added to an objective the reader has just met three paragraphs earlier*. Ch.5 states the same
construction in words for a paper audience under a page limit, and an equation there is a two-file
change to a submitted manuscript for something that chapter's argument does not require. Placing it
in the frame also puts it **before both chapters that use the representation**, which is what a
fundamentals chapter is for. The convenience and the science point the same way here, and I would
have chosen Ch.2 even if Ch.5 had been free.

**Two faithfulness notes recorded in the file, both of which limit the claim:**

1. `e^-` is described as "substituted from elsewhere in the batch", which is the source's
   **optimized** path (its "Corrupção de Embeddings" section: negatives come from permuting
   already-computed embeddings, not from re-running the encoder on shuffled features). That is the
   code's default. The equations are indifferent to how `e^-` is produced, so nothing in them
   depends on this.
2. The **two auxiliary terms Ch.5 mentions** (a masked reconstruction and an anchor, weights 0.3
   and 0.1, `5_mobiwac.tex:290`) are **not** in this objective. The source document does not carry
   them and their code defaults are `0.0` (`Check2HGIModule.py:68`, `:178`), enabled per run. So
   the passage presents the three-boundary objective as the source states it and **does not claim
   to be the complete training loss of every run reported in Ch.5.**

**Verified in the RENDER, not the source only** (the failure mode `AGENT_BRIEF` §3 names): all
three equations set correctly on defense p. 21, numbered 2.1-2.3, with the bold vectors, the
transpose, `σ` and the `\mathcal` script rendering as intended. Page image inspected.

### `[VERIFY]` / **blocking** — the GLOSSARY is fail-closed and I could not close this myself

This passage uses **two terms the registry does not hold**: *bilinear discriminator* and *logistic
function* (`grep` on `GLOSSARY.md`: 0 hits each). The maintenance rule is that the entry lands
**before** the term does, and `GLOSSARY.md` is not in my editable set. So:

> **Proposed entries, for the author to approve before this paragraph is final:**
>
> - **bilinear discriminator** — A scoring function `D(e_1,e_2) = σ(e_1^T W e_2)` that maps a pair
>   of embeddings to a compatibility score in (0,1) through a learned matrix `W`. Used in the
>   Check2HGI objective at each hierarchy boundary. PT: *discriminador bilinear*.
> - **logistic function** — The function `σ(x) = 1/(1+e^{-x})`, which maps a real score to (0,1).
>   Named at first use as the `σ` of the discriminator. PT: *função logística*.
>
> Precedent for the narrower word: **"discriminator" is already in published Ch.3 prose**
> (`3_cbic.tex:166`), so only the modifier "bilinear" and the name of `σ` are new to the document.

This is recorded in the file itself as a blocking dependency, not merely as a sign-off note.

---

## 5 · ITEM 5 — the AI disclosure. **Trimmed 374 → 303 words; one cut removed a false claim.**

Four cuts. The first is not padding, it is a factual defect.

**Cut 1, FALSE CLAIM REMOVED.** The appendix read: *"The complete first version passed an
eighteen-reviewer panel, each reviewer a separate agent (Claude Opus family) confined to one
role..."* The **count is right** (18 numbered reports in `src_utils/_history/_review_v1/`). **"Passed" is
not.** That panel's own consolidated verdict table (`_history/_review_v1/CONSOLIDATED_REVIEW_REPORT.md`:13-22)
records:

- persona 03, Style auditor: **GATE FAIL (document)**
- persona 06, Number auditor: **GATE FAIL (conditional)**
- BLOCKER-class findings at personas 01, 03, 06, 09 and 10

A document does not pass a panel two of whose gates failed it. This is the standing failure mode
named in `AGENT_BRIEF` §2, in the one appendix whose whole job is to be credible about process, and
it would have been read by a banca. The replacement says what the passes **did** — checked
citations, numbers, claims, cross-references and style; each pass run by an agent that did not
write the text; findings offered as corrections for the author to accept or reject, **not
approvals** — all of which the reports evidence.

"(Claude Opus family)" went with the sentence that carried it. This also **closes the `ANCHORS.md`
COD-013 row for this file** ("name the model"): the tool is already named in the opening paragraph,
and the file's own header records that **no version string is derivable** from the drafting commits,
so the parenthesis was claiming a precision it could not source. The model cannot honestly be named
more precisely than it already is.

**Cut 2, ceremony.** "This appendix discloses the scope of that use and the verification process
applied, in line with..." announced what the appendix would do before doing it. Now one clause,
which also **fixes a conflation**: CNPq Portaria 2.664/2026 **mandates** declaration while UFV/DPE
03/2026 **recommends** it (`AGENT_GUARDRAILS.md:169-171`; `UFV_COMPLIANCE.md:103-104`). The old
sentence put both under "recommendations".

**Cut 3, ceremony.** "The record below is reconstructed from the version-control history... rather
than from recollection." A statement about how *this appendix* was drafted, not about the AI use it
discloses. The provenance stays in the file's comment header where an auditor can use it.

**Cut 4, padding.** "Every AI-drafted passage passed a fail-closed verification pipeline before
reaching the advisor:" plus a five-clause semicolon chain naming an outline, a fact gate, a style
gate and the author's approval. It read as apparatus, and `WRITING_LAW` §4 bans semicolon braids.
The three rules the chain amounted to are now three short sentences, plus the fail-closed rule
itself (flag, do not smooth), which was the one substantive item and was buried in it. "No content
entered the document from model memory" was dropped as an unverifiable process claim; what replaced
it is the rule that produces it.

**Substance kept in full:** the tool and its role, the policy basis, all four scope items with the
drafting-versus-re-typesetting split, the CoUrb translation fidelity check (which is real: the L5
gate report records 63/63, 63/63 and 9/9 cell-identical), and the author's responsibility for every
word. **Nothing was added.**

One correction to my own work, recorded because self-reported numbers are not trusted: my first
draft of the comment claimed "469 → 340 words", a figure I had not measured. Measured properly
(comments stripped, escaped percent signs preserved) it is **374 → 303**, and the comment now says
so and says that it was corrected.

---

## 6 · ITEM 6 — reproducibility content for Appendix A. **Added, following Appendix D's pattern.**

New `\section{Reproducing the reported numbers}`, six entries, each naming the code that implements
one element and the file its output lives in. **Every path was checked to exist on disk**; every
protocol statement is quoted from a source document and then confirmed in the implementation, not
retyped from the brief (which the brief explicitly forbade).

| Element | Named in the text | Source read | Confirmed in code |
|---|---|---|---|
| Fold partition | `src/data/folds.py` | `DATA_SPLITS.md` "Configuration" | `folds.py:1159`, `:1247` (`StratifiedGroupKFold`, `shuffle=True`, `random_state=self.seed`); seed default `:1061` = 42; `n_splits` `:1059` = 5 |
| Paired MTL folds | same routine | `DATA_SPLITS.md` "MTL fold pairing" steps 1-4 | `folds.py:1204-1208`, `:1453-1455` |
| Seeds | 0, 1, 7, 100 over one fixed partition | `DATA_SPLITS.md` "Multi-seed pooling"; `STATISTICAL_PROTOCOL.md` | — |
| Region-transition prior | `scripts/build_phase3_per_fold_transitions.sh` | `DATA_SPLITS.md` "Per-fold log_T" | path exists |
| Joint-best reading | `scripts/closing_data/score_joint_best.py` → `joint_best/JOINT_BEST_RESULTS.md` | `GLOSSARY.md` "joint-best convention"; script header `:2-6` | both exist |
| Significance tests | `superiority_wilcoxon.py`, `region_match_tost.py`, `m1_stats_n20.py`, `m2_prereg_perfold.py` + both output logs | `stats_n20/RESULTS.md:44-46` | all six paths exist |
| Label-history benchmark | pointer to Appendix D, which already names the script | `apx_d_ceiling.tex` | not duplicated |

**Two structural fixes the addition forced**, both measured on the render:

1. I first wrote `footnote~\ref{fn:mobiwac:code}` to point at the repository URL. That would print
   a **chapter-local footnote number** read from an appendix, which is a cross-reference the reader
   cannot resolve. Replaced with prose ("which Chapter 5 footnotes at first mention"), so there is
   still exactly **one URL of record per repository** in the document.
2. The file header records that the lone `A.1` heading was dropped when the former A.2 was removed,
   leaving one unsectioned statement. A second topic makes that asymmetric, so I added
   `\section{The experimental platform}` over the existing opening. **The opening prose itself is
   unchanged.**

**`METRICS.md` was deliberately NOT restated, and this is a judgment the author should check.** It
is an internal document whose conventions differ in places from what the chapters report: it makes
**MRR primary** for the joint scoreboard, and it describes an "F51 canonical extraction" of
per-fold **max over epochs ≥ 5**, which is **not** the joint-best convention Ch.5 reports (one
validation-selected checkpoint per fold). Restating it would have imported a superseded convention
into a reproducibility appendix. The section points at the chapters, which state the conventions
actually used, and I recorded the reasoning in the file.

**`[VERIFY]` flags left rather than guessed:**

- A **package-version manifest** for the released code, if one exists, belongs in this section. I
  did not establish one. Hardware and per-model training configurations are likewise not named;
  Ch.5 says the full training configuration is in the released code.
- Whether the author wants `METRICS.md`'s Δm variants and the F51 extraction rule disclosed
  **anywhere** in the document. I could not establish that either belongs to the reported
  configuration, so neither is named.

---

## 7 · Writing-law sweep on my own added prose

Measured on the 116 rendering lines (1,104 words) my diff adds, comments stripped:

| Check | Count |
|---|---|
| em-dash | **0** |
| contractions | **0** (9 apostrophes, all possessives: `author's`, `boundary's`, `other's`, `chapter's`, `fold's`, `scikit-learn's`, `user's`, `task's` ×2) |
| banned words (§4 list + Claude-family tics) | **0** |
| banned templates | **0** |
| repo codenames (incl. the registry id, "substrate", "engine", "board", "recipe", "frozen") | **0** |
| phrasal-metaphor idioms | **0** |
| banned verdict verbs (beats / wins / ties / Pareto) | **0** |
| two `-ly` adverbs in one sentence | **0** |

No new number is written without its reference point and convention. No new citation was added to
`references.bib`, so the citation-integrity surface is unchanged by this track.

---

## 8 · Source ledger

**Numbers** (value → source file → field → convention):

| Value | Source | Convention |
|---|---|---|
| 0.7388 ± 0.0205 | `research/embeddings/hgi/README.md:548` | Cat F1, Alabama, `w_r`=0.4, 5 folds × 50 epochs, 0-1 scale, spread across folds |
| 0.8186 ± 0.0123 | same, `:551` | same, `w_r`=0.7 (the adopted default, `preprocess.py:23`) |
| sweep {0.4, 0.5, 0.6, 0.7} | same, `:548-551` | four settings, one per row |
| `w_r` = 0.4 published | HGI PDF p. 4, Eq. 2, **read firsthand** | the paper's cross-region factor for Xiamen/Shenzhen |
| 0.4 / 0.3 / 0.3 loss weights | `check2hgi_overview.tex` §"Função de Perda"; `Check2HGIModule.py:51-53`, `:1192-1195`; `check2hgi.pipe.py:43-45` | fixed weights, one per hierarchy boundary |
| 4 supported / 2 TOST (region) | `tables/mobiwac/results.tex` region block marks; `stats_n20/RESULTS.md:87-90`, `:139`, `:141` | Acc@10, 4 seeds × 5 folds, paired t on per-seed means (n=4), Holm; TOST δ=2 pp |
| 6 bold (category) | same, category block | macro-F1, same footing |
| seeds {0,1,7,100}, n=20 | `DATA_SPLITS.md` "Multi-seed pooling"; `STATISTICAL_PROTOCOL.md` | 4 initializations × 5 folds over ONE fixed partition |
| `StratifiedGroupKFold`, 5 splits, seed 42 | `DATA_SPLITS.md` "Configuration"; `folds.py:1159`, `:1247`, `:1059`, `:1061` | grouped by userid, stratified on task label |
| 18 reviewer reports | `src_utils/_history/_review_v1/`, counted | 18 numbered `.md` files |
| 2 GATE FAILs, 5 BLOCKERs | `_history/_review_v1/CONSOLIDATED_REVIEW_REPORT.md:13-22` | the panel's own verdict table |
| 374 → 303 words | measured on `apx_c_ai_disclosure.tex` | comments stripped, escaped `%` preserved |
| 244 words / 0 eq / 0 fig in §5.4.1 | measured on `5_mobiwac.tex:284-295` | comment lines excluded |
| 105/100 → 108/103 pp | `build.sh` in `/tmp/r6t3_scratch` | isolated tree at `870f882c` + my three files only |

**No reference was added to the bibliography**, so there is no citation ledger for this track. The
one external document I opened firsthand is the HGI paper PDF already in the repository
(`science/articles/Learning urban region representations...pdf`), for Eq. 2 and the paper's stated
region-representation goal.

---

## 9 · What I could not confirm

1. **The averaging convention of the HGI sweep's "Cat F1"** (macro or weighted). No source names
   it. `[VERIFY]` left in place; the prose says "category F1" rather than "macro-F1" for this
   reason.
2. **Whether Ch.5's two auxiliary loss terms belong in the Ch.2 equation.** Their code defaults are
   0.0 and the source document omits them, so I presented the three-boundary objective as the
   source states it and said so in the file. Settling this needs the run configuration of the
   shipped representation, which I did not establish.
3. **A package-version manifest** for the released code. Not found; not asserted.
4. **Whether `METRICS.md`'s MRR-primary and F51 extraction conventions should be disclosed
   anywhere.** They differ from what Ch.5 reports and I could not establish that either belongs to
   the reported configuration.
5. **The two GLOSSARY entries are proposed, not landed.** The registry is fail-closed and not my
   file; until the author approves them the Check2HGI paragraph is formally blocked, not merely
   awaiting wording sign-off.
6. **`make check`'s 10 stale page-count claims** are inherited (they fail at baseline too) and live
   in four documents belonging to other remits. Not fixed, and `sync_page_counts.py --write` should
   run once at the end of the round, not now while three tracks are still moving pages.

## 10 · Reported across remits, not fixed by me

- **The shared worktree is dirty** with another track's `4_courb.tex`, `apx_b_errata.tex` and a new
  untracked `apx_b_static_scope.tex`. It builds 106/101 pp there. Anyone measuring in the live tree
  right now is measuring three tracks at once.
- **`ANCHORS.md` line numbers for `2_fundamentals.tex` have all shifted** below line 171 (the file
  grew from 617 to 751 lines). Measured, so the next reader does not re-derive them: the COD-015(d)
  anchors the table lists at `:437` ("mean reciprocal rank") and `:442` ("the relative multi-task
  performance change") are now at **`:571`** and **`:576`**, and the COD-007 anchor at `:468`
  ("stratified by sample rather than by") is now at **`:602`**. The NUM-4 row's own anchor phrase
  ("rose monotonically") is at **`:173`**. Anchor by phrase, as that file itself instructs.
- **`5_mobiwac.tex` §5.4.1 still has zero figures and no equation**, which is now a deliberate
  choice rather than an oversight: the equation is in Ch.2 and cross-referable. If the author wants
  it in Ch.5 as well, that is the two-file change, and it is the Claim-scoping track's file.
- **`14_comments_measured.md:40` overstates what its own seven blocks are**, and since two of those
  seven sit in a file I could check, I verified it rather than passing the report along. It says
  "The remaining 7 fact-free blocks are `[NEEDS SIGN-OFF]` markers ... the author's own decision
  queue and must stay until he clears them." Two of the seven it enumerates, `3_cbic.tex:152` and
  `:165`, are **bare one-character `%` lines** (confirmed by reading both). They are not a decision
  queue and nothing is waiting on them. That report's recommendation (no compression pass) is
  unaffected; the description of two of its lines is wrong, and it wrongly protects them. Not my
  file, so not fixed. Flagged for the comment-volume track.


---

<!-- estado-rodada -->
> **Rodada encerrada · último toque 2026-07-28 · sem autoridade.**
> Este ficheiro é registo de proveniência do que foi discutido nesta passagem, não fonte
> de um facto corrente. O que ficou decidido está em [`VEREDITOS.md`](../../../VEREDITOS.md);
> os valores entregues estão em `CLAUDE.md` §0.1. Não copie nada daqui sem confirmar lá.
