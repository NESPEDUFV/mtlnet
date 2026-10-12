# 06 + 07 · Number auditor and claim/honesty auditor — round 6 delta pass (G2, N1–N5 + C1–C4)

> 🛑 **GERACAO SUPERADA — nenhum numero medido deste ficheiro pode ser citado.**
>
> Isto e a auditoria de numeros e de honestidade de alegacoes da ronda 6, corrido **antes** de a geracao v18 fechar o vazamento de rotulo no grafo de
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


**Written 2026-07-28**, read-only, fresh eyes. Personas 06 and 07 run as one pass because they share
the extraction work and jointly constitute gate G2.

**State reviewed.** Source at `4e84cf7a` (the per-section chapter split). I rebuilt all three targets
myself rather than trusting the recorded state:

```
make defense -> build/main.pdf       108 pp
make final   -> build/main_final.pdf 105 pp
make ppgc    -> build/main_ppgc.pdf  109 pp
tex_errors=0, overfull_hbox=0, overfull_vbox=0, undef_cite=0, undef_ref=0,
oversized_floats=0  (all three logs, matched by Python with errors='replace')
```

**Coordinates.** Every line number below was measured **2026-07-28 against the post-split tree** and
each finding names the phrase it is anchored on. `5_mobiwac.tex` line numbers from earlier records are
all stale; the prose now lives in `chapters/5_mobiwac/*.tex`.

**Independent check of the split itself.** Before auditing content I verified the split is mechanical,
because every finding's coordinate depends on it. Reconstructing each wrapper plus its `\input`
subfiles and stripping comments gives prose **byte-identical** to the pre-split blobs
(`9dc3036a`, `495711c8`, `f7f78ffd`): 3_cbic 40,871 chars, 4_courb 39,410, 5_mobiwac 52,372. The
split is confirmed clean; the render claim holds.

---

## VERDICT: **GATE FAIL**

One BLOCKER (a number that contradicts its own source of record, in two files), plus one MAJOR
self-contradiction created by this round's own edits. Everything else this round touched verifies.

The fail is narrow and both items are cheap to close. Nothing in the round's *new* content is
fabricated: of 27 numerals I traced, 25 reproduce exactly from their sources, and I recomputed the
balancer-screen and pre-registered-test cells from the JSONs rather than accepting any prose.

---

## 1 · MISMATCH LIST

### N-1 · **BLOCKER** · The gradient-cosine per-dataset bound contradicts the source it now cites

**Anchor phrase:** `per-dataset means within $\pm0.003$`
**Files (today's lines):** `src/chapters/5_mobiwac/02_related.tex:161` **and**
`articles/[mobiwac]/src/sections/02_related.tex:99`. Both texts carry the clause verbatim; I confirmed
the full sentence is identical in the two files apart from the sanctioned
"this dissertation" / "this study" substitution.

**The sentence, as it stands:**

> "the cosine similarity between the next-category and next-region updates on the shared trunk
> averages $+0.001$ across training (four seeds each on four Gowalla states: Alabama, Arizona and
> Florida … and Georgia … **per-dataset means within $\pm0.003$**)."

**What I measured.** This round rescoped the pool from "three of our six datasets" to the four states
of the widened, 16-run measurement. That widening moved the per-state means, and the bound was carried
across unchanged. The authoritative post-widening per-state figures
(`docs/studies/archive/mtl_improvement/WHY_ORTHOGONAL_AND_NO_MODERN_OPTIMIZERS.md:30`, restated at
`docs/results/mtl_improvement/T4_audit_and_verdict.md:48`):

| state | per-state cosine mean | within ±0.003? |
|---|---:|:--:|
| FL | +0.0007 | yes |
| **AL** | **+0.0032** | **no** |
| AZ | −0.0005 | yes |
| GE | −0.0004 | yes |

`|+0.0032| > 0.003`. The bound is **false for Alabama**, the very state the sentence names first.

**Why it survived.** The ±0.003 bound is correct against the *superseded* two-run, seed-0 figures
(FL +0.0007 / AL +0.0026), which are what the clause was originally written against and which still
circulate in `docs/CLAIMS_AND_HYPOTHESES.md:19`, `PAPER_UPDATE.md:40`, `log.md:2172` and
`CHANGELOG.md:62`. `HANDOFF_AUDIT.md` H1 widened the pool from 2 runs to 16 on 2026-06-12 and AL moved
+0.0026 → +0.0032. The round's own ledger records the mechanism precisely:
`SOURCE_LEDGER.md:154` marks this number **`INHERITED` — "I did not re-derive the cosine"**. The
scope was fixed and the bound that depends on the scope was not re-checked.

**Note the direction.** The pooled `+0.001` is *correct* (source pooled mean +0.0008 rounds to
+0.001), and the finding does not touch the orthogonality conclusion — +0.0032 is still ≈ 0. This is a
false bound, not a false conclusion.

**Closes when:** the clause states a bound the source supports — e.g. `within $\pm0.004$`, or
"per-dataset means between $-0.001$ and $+0.004$" — quoted from
`WHY_ORTHOGONAL_AND_NO_MODERN_OPTIMIZERS.md:30`, applied in **both** files, with the errata line in
`articles/[mobiwac]/ERRATA.md` that the Ch.5 parity regime requires. Because the four per-state values
are published in the source, the honest alternative is to name them.

---

### N-2 · **MAJOR** · Ch.2 says Chapter 3 does not identify its split axis; Chapter 3 now does

**Anchor phrase:** `reports five-fold cross-validation without identifying the split`
**File (today's line):** `src/chapters/2_fundamentals.tex:601-602`

**Current text:**

> "it strengthened from one study to the next: Chapter~\ref{ch:cbic} reports five-fold
> cross-validation **without identifying the split axis**, Chapter~\ref{ch:courb} states that its
> split is stratified by sample rather than by user …"

**What I measured.** This round added the split axis to Chapter 3.
`src/chapters/3_cbic/results.tex:30` now reads: "The folds are formed by a stratified splitter over
the samples rather than over the users, so the check-ins of one user may appear in both training and
validation". So the frame asserts an absence that the chapter it describes no longer has.

This was **predicted in writing and then not applied**. The protocol-recovery pass flagged it as a
consequential edit (`_history/_round6/10_protocol_recovery.md`, §"The consequential edit in Chapter 2, outside
my remit", and again as item 3 of its §8 handover checklist), and the Ch.3 source comment repeats the
warning at `3_cbic/results.tex` ("That clause is FALSE the moment this addition lands"). Items 1, 2, 4,
5 and 6 of that checklist all landed; item 3 did not. I verified each: Ch.3 protocol added, Ch.4
checkpoint sentence added at `4_courb/results.tex:14`, balancer scope added, Nash narrowed at
`4_courb/methodology.tex:36`, Standley corrected.

**Closes when:** the clause is replaced with the repair the recovery pass already drafted and the
author has the wording for — "Chapters 3 and 4 both stratify by sample rather than by user … and only
Chapter 5 splits by user" — or with any wording that does not assert the absence. One sentence, no
number changes.

---

### N-3 · **MINOR** · Ch.2 calls the three-boundary sum "the total objective"; Ch.5 adds two more terms

**Anchor phrases:** `the total objective is a fixed-weight sum of one term per boundary`
(`src/chapters/2_fundamentals.tex:243`) against `Two small label-free auxiliary terms are added
(weights 0.3 and 0.1)` (`src/chapters/5_mobiwac/04_method.tex:18`).

**What I measured.** Equation 2.1 is transcribed faithfully and the source
(`docs/context/check2hgi_overview.tex:213`) does call it "A perda total" — so Ch.2 is faithful to its
source. But the two chapters, read together, describe different objectives: three terms
(0.4/0.3/0.3) in Ch.2, five in Ch.5. Both are correct as decompositions of different things; the word
"total" is what collides.

I established which configuration the reported results use, since that decides whether this is
cosmetic. The board's engine is `check2hgi_dk_ovl`, a re-windowing of
`check2hgi_design_k_resln_mae_l0_1` (`src/configs/paths.py:59`), and that engine's builder
(`scripts/probe/build_design_k_delaunay.py:4-5, :367, :387-389`) sets `anchor-lambda 0.1` and
`mae-poi-lambda 0.3` as **v14 defaults**. So the two auxiliary terms are **on** in the runs Ch.5
reports, while the module-level defaults are 0.0 (`Check2HGIModule.py:68, :178`) and the source
explainer document describes the canonical engine only (it names no mae/anchor/Delaunay anywhere).
The chapter comment's own `[VERIFY]` flag on exactly this question is therefore live and correctly
raised — and answerable from the build script.

**Closes when:** Ch.2 says "the objective across the hierarchy's three boundaries" (or equivalent)
rather than "the total objective", or adds a half-sentence pointing at Ch.5's two auxiliary terms.
The equation itself needs no change. This also closes the chapter's own `[VERIFY]`.

---

### N-4 · **MINOR** · `make check` exits non-zero: a gate fires on Appendix B

**Anchor phrase:** `This article differs from the other two in a way that changes what this section has to record.`
**File (today's line):** `src/chapters/apx_b_errata.tex:307`

**What I measured.** `bash src_utils/check.sh` exits **1**. Every named gate prints OK except the
"this paper / this article" sweep, which reports the line above. The brief states `make check` all
gates pass; measured today, it does not.

**This is a consequence of the gate-coverage fix, not a new defect in the prose.** The line predates
this round (introduced at `d1911c0a`) and is a legitimate use — Appendix B is describing one of the
three articles, not calling the dissertation "this article". At `1ef83867` the gate globbed
`chapters/*.tex`, which *does* match `apx_b_errata.tex`, so I checked whether it failed there too: it
did. The gate has been firing on this line since `d1911c0a`; the round-6 brief's "all gates pass" is
inherited from a record, not from a run.

Two smaller observations from the same run, both benign: the verdict-verb sweep prints four hits
(`3_cbic/basis.tex:44,54`, `3_cbic/method.tex:201`, `4_courb/methodology.tex:36`) but is
non-fatal by construction (`|| echo OK`, no `FAIL=1`), and all four are the mathematical term
"Pareto", not result verbs — correct behavior. And `make check` reports
"src/build/main.log has no page count -- the build did not finish" when run immediately after
`make defense && make final && make ppgc`, because `make ppgc` overwrites nothing but the
last-written log is `main_ppgc.log`; running `make defense` last makes the gate pass. Worth knowing
before anyone reads that message as a broken build.

**Closes when:** either the Appendix B sentence is reworded ("The third article differs…"), or the
gate exempts `apx_b_errata` for this sweep as it already does for the banned-word sweep. Author's
call which; the gate is currently correct-but-noisy and its non-zero exit masks future real hits.

---

### C-1 · **MINOR** · `_check_pair_parity.py` defaults to the pre-cut page numbers

**File:** `src_utils/_history/_round6/_check_pair_parity.py:35` (`PT_PAGE=3`, `EN_PAGE=4`)

**What I measured.** Run with its defaults against today's build, the checker reports **19/19 floor
claims FAILING** and "EN 400 words / 16 sentences". Run with `PT_PAGE=2 EN_PAGE=3` — the pages the
pair actually occupies in the current 108-page build — it reports **0 failures, 19/19 present in both
languages, PT 310 / EN 271**. The Resumo moved from p.3 to p.2 when the approval sheet became
`main_ppgc`-only (`7a91b720`).

The script's docstring anticipates staleness and says a zero-word EN block means "you are pointing it
at a PDF that does not match the source". That is the right instinct but the wrong diagnosis here:
the PDF is fresh and the page numbers are stale, and the failure mode is 19 loud false failures
rather than a divide-by-zero. A gate whose default invocation cries wolf is one nobody will run.

**Closes when:** the defaults become 2/3, or the script locates the blocks by searching for the
`Resumo`/`Abstract` headings instead of taking page numbers.

---

## 2 · ALL-CLEAR LIST — what I verified, grouped

### Priority 1 · The three Check2HGI equations (Ch.2) — **CLEAN**

- **Transcription, not invention.** I extracted all three display equations from
  `docs/context/check2hgi_overview.tex` §"Função de Perda" (:214, :219, :226) and normalized both
  sides. After removing the source's `\underbrace` annotations, which the chapter comment declares
  dropped, **all three match exactly**: `L = 0.4L_c2p + 0.3L_p2r + 0.3L_r2c`,
  `D(e_1,e_2) = σ(e_1^T W e_2)`, `L_* = −log D(e^+,e^+) − log(1 − D(e^+,e^-))`. Symbols, weights,
  subscripts and the star on `L_*` are the source's own, as the comment claims.
- **Every symbol defined at first use**, mechanically confirmed in the surrounding prose:
  `L_c2p`/`L_p2r`/`L_r2c` ("the check-in-to-place term", etc.), `e_1`/`e_2` ("the two embeddings being
  compared"), `W` ("a learned weight matrix"), `σ` ("the logistic function"), the score range
  ("lies between 0 and 1"), `e^+` ("an embedding from a true pair"), `e^-` ("substituted from
  elsewhere in the batch").
- **The render says what the source says.** Verified on the built PDF, not the source: the passage
  renders on **p. 19**, equations numbered **(2.1), (2.2), (2.3)**, all three complete and correctly
  typeset in the text layer.
- **Code agrees with the equations.** `Check2HGIModule.py:51-53` (alpha_c2p=0.4, alpha_p2r=0.3,
  alpha_r2c=0.3), assembled at `:1192-1195`; the per-boundary form `-log(pos) - log(1-neg)` at
  `:1159`, `:1184`, `:1189`; the bilinear discriminator at `:1003-1018`
  (`matmul` → elementwise product → `torch.sigmoid`). Same three weights in
  `pipelines/embedding/check2hgi.pipe.py:43-45`.
- Scope caveat correctly stated: "No target label appears in any of the three equations" is true of
  all three as typeset. See N-3 for the one word I would change.
- One process note, not a number defect: the chapter comment records that "bilinear discriminator"
  and "logistic function" are **not** in `GLOSSARY.md` and flags the paragraph as blocked on the
  fail-closed registry rule (L2). I confirmed both terms are absent from the registry. That is
  persona 05/author territory; I record it so it is not lost.

### Priority 2 · Ch.5 balancer screen and gradient cosine — **numbers CLEAN, parity CLEAN, one bound wrong (N-1)**

Recomputed from `T4_full_screen.json` directly, not read from prose:

- **"nineteen loss and gradient balancers"** — exactly 19 keys under each of the two top-level keys.
  Both top-level keys are `alabama` and `florida`, confirming "two datasets, Alabama and Florida"
  from the artifact rather than from the `AL+FL` abbreviation.
- **Nash-MTL "+0.68"** — 54.2465 − 53.5660 (equal_weight) = **+0.6805**. Correct.
- **scale normalization "+0.19"** — 53.7591 − 53.5660 = **+0.1931**. Correct.
- **"none improved … across both tasks and both datasets"** — I tested every arm against both
  equal_weight and static_weight on both tasks at both datasets: **the winner set is empty in both
  cases**. The claim holds as stated.
- **"neither holds that position elsewhere"** — Nash-MTL FL cat 71.61 vs equal 71.79 (loses);
  scale_norm FL cat 72.12 (gains) with FL reg 35.47 vs 73.05 (collapses, −37.59). Both halves hold.
- **Scope sentence** ("at their default configurations at a single seed on two datasets, Alabama and
  Florida") matches `T4_audit_and_verdict.md:8-10` ("registry DEFAULTS, seed 0, AL+FL") and its
  restatement at `:111-112`. The "seed 0 stays out of the prose" decision follows
  `articles/[mobiwac]/GLOSSARY.md:113`.
- **Parity with the submitted paper: verified mechanically, not assumed.** Normalizing only the
  sanctioned substitutions (dissertation/study, `\ref` targets, the `nash`/`navon2022nashmtl` key),
  the balancer paragraph, the cosine sentence, the analysis-plan paragraph, the Holm-scope sentence
  and the registered-Wilcoxon sentence are **identical** in `chapters/5_mobiwac/*` and
  `articles/[mobiwac]/src/sections/*`. The only divergence in the cosine passage is the
  dissertation's figure block, which is expected.

### Priority 2b · The reconciled gradient-cosine scope — **scope CLEAN**

`R0_matched_metric_bar.json` has exactly four keys under `states` — `alabama`, `arizona`, `georgia`,
`florida` — each with `g_rundirs` for seeds `[0, 1, 7, 100]`, and
`scripts/mtl_improvement/plot_grad_cosine.py:19-24` names the same four. So "four Gowalla states … at
four seeds each" and "Georgia, which this dissertation does not otherwise use" are both correct, and
the round's parity fix carried the right wording into the paper. The pooled `+0.001` is +0.0008
rounded. Only the ±0.003 bound is wrong (N-1).
*Cannot verify independently:* the per-epoch `grad_cosine_shared` CSVs live under
`results/check2hgi_design_k_resln_mae_l0_1/...`, which is not on this machine, so I verified the
per-state means against the two records that publish them rather than recomputing. Flagged in §4.

### Priority 2c · The new statistical sentences — **CLEAN, and they run**

Every value in the two new Ch.5/paper sentences reproduces from
`stats_n20/m2_prereg_output.txt`, whose own 24/24 artifact→board gates all pass:

- "each gain is significant after a Holm correction across the six datasets (paired t, corrected
  p<0.001)" — worst Holm-adj = **5.7220e-06**.
- "the four next-region gains hold under their own Holm correction as well (corrected p<0.001)" —
  reg family m=4, Holm-adj **3.8147e-06**.
- "The registered Wilcoxon test on the individual fold differences agrees at every dataset, with all
  20 folds favoring the joint model" — **20/20 folds positive at all six**, exact p 9.5367e-07 = the
  n=20 one-sided floor.
- The analysis-plan paragraph's claims all check: the exact one-sided Wilcoxon floor at n=4 **is**
  0.0625; the plan registered non-inferiority for region *per task* and no region-superiority family,
  so labeling the four region gains "secondary results outside it" is the honest form; the Holm scope
  sentence now names both families instead of the previous "across the comparisons".
- **The trap the brief named: cleared correctly.** "At all six" is anchored on the **rev 4
  (2026-07-13) header table** of `stats_n20/RESULTS.md` (lines 1-22), where all six datasets reject at
  Holm-adj ≤ 8.9e-07. The `(superseded)` heading at `:26` and the "provisional" CA/TX material in
  §1b sit *below* it. I read the revision header before using the number; the withdrawn flag was
  correctly withdrawn.
- **Two hedges correctly removed, not lost.** `06_results.tex` dropped "so no claim depends on this
  choice" and "both models average four seeds over five folds" — the first because the sentence
  already gives the bound, the second because `05_setup.tex:76` now states the seeds and pairing for
  all datasets. No measurement was weakened (evidence-guard, C7/C8): the 0.06/0.11 bound itself
  survives verbatim.

### Priority 3 · Resumo / Abstract pair — **CLEAN, 19/19 floor claims in both languages**

Measured on the **rendered pages** of today's build (p. 2 PT, p. 3 EN), using the track's own
instrument `_measure_abs.py` under its stated convention, reproduce-first per README §10:

| block | words | sentences | mean | recorded |
|---|---:|---:|---:|---|
| Resumo | **310** | 11 | 28.2 | 310 / 11 / 28.2 ✓ |
| Abstract | **271** | 11 | 24.6 | 271 / 11 / 24.6 ✓ |

- **Sentence-for-sentence parity is real.** I extracted both blocks from source independently of the
  track's tooling and aligned them: **11 sentences each, one-to-one, in the same order**, same claims,
  same hedges. Printed in full during the audit.
- **Same numbers, same hedging, both languages.** PT `5,3`/`9,4`/`Acc@10`/`dois pontos` against EN
  `5.3`/`9.4`/`Acc@10`/`two-point`. Verbs bound to tests in both: `supera`/`outperforms` for the six
  category cells and the four region cells, `equipara-se estatisticamente … (TOST)`/`statistically
  matches … (TOST)` for the other two. **Arizona is never upgraded** in either block.
- **Every number traced.** `5.3 to 9.4` = FL +5.34 (low) and AZ +9.40 (high) from
  `stats_n20/RESULTS.md` rev-4 §1 — I confirmed AL +7.73, Istanbul +8.59, CA +6.45, TX +7.45 all lie
  inside. "at all six" and "four of them" per Priority 2c and `tables/mobiwac/results.tex`.
  `twenty fitted models` / `vinte modelos ajustados`, `four random initializations over five fixed
  folds` — consistent with `DATA_SPLITS.md` seeds {0,1,7,100} × 5 folds and with Appendix A.
- **Conventions named in both** (N5): metric (macro-F1, Acc@10), selection rule (joint-best /
  `seleção joint-best`), inferential unit (paired tests on the four initialization means), margin and
  test (two-point Acc@10, TOST).
- **Floor check reproduced**: 19/19 present in both languages, 0 failures, when the checker is
  pointed at the right pages (see C-1).
- One genuine one-word difference from the record, and it is the *instrument*, not the text: the
  Abstract measures **272** words when the page's text layer is read raw, because pdfium emits a
  soft-hyphen inside `multi-task` at a justified line break, splitting one compound into two tokens.
  With the hyphenation normalization the report documents, it is 271. The prose is unchanged since
  the cut — the only commit touching `0_main.tex` since (`7a91b720`) moved the approval sheet.
  This is exactly the "text layer is not the page" class the round-5 figure finding established.
- [VERIFY] carried forward, correctly self-reported by the track and not smoothed: the pair remains
  above the exemplar envelope (310 vs 282; 271 vs 250). Author's ruling, not a gate failure.

### Priority 4 · Ch.3 / Ch.4 protocol detail — **CLEAN, and the code citations verify firsthand**

The Ch.3 comment cites the CBIC-era codebase at commit `9b06053f` ("VERSION PUBLISHED"). Earlier
records had closed this as unrecoverable; `a7ab2eaa` claims the code is in this repository. **It is**,
and I read it rather than trusting either record:

- **Split axis** — `git show 9b06053f:src/data/create_fold.py`: `:217` and `:220` are plain
  `StratifiedKFold(n_splits=k_splits, shuffle=True, random_state=random_state)`; the two `.split(x, y)`
  calls at `:231-233` carry **no `groups=` argument**; `:194` drops `userid` from the features. So
  "stratified over the samples rather than over the users" is exactly right, and the chapter's
  "check-ins of one user may appear in both training and validation" follows.
- **Sample unit** — `:205` `places_ids = df_category['placeid'].unique()`, `:209`
  `set_index('placeid')`, so "for the category task the sample unit is the place, so no place spans
  two folds" holds, and it is correctly presented as a property of the unit and **not** as a leakage
  guard.
- **Seed** — `:159` `random_state: int = 42` as the `create_folds` default. The prose says "pins a
  single random seed" and keeps the literal 42 out, matching the Ch.4 precedent.
- **Checkpoint rule** — the sentence is word-for-word identical in the two chapters
  (`3_cbic/results.tex:30`, `4_courb/results.tex:14`), which is the deliberate one-name-per-concept
  choice the comments record. Verified as identical.
- **Honesty of scope, credited.** The comment declines to claim the files produced the published runs
  ("the code of record"), declines a tuning budget as unrecoverable, and declines an epoch count
  because the committed config and run record disagree on batch size. It also scopes "without early
  stopping" away from the Convergence subsection, which deliberately stops at a target. Each of these
  is the fail-closed behavior the guardrails ask for, and I found no claim in the prose that outruns
  the evidence. The one consequence it flagged in Ch.2 was not applied — that is N-2.
- **Ch.4 Nash narrowing (`4_courb/methodology.tex:36`)** — the published "ensures that the update is
  beneficial for all tasks simultaneously" is now conditioned on being away from a Pareto-stationary
  point and on the linear-independence assumption. The correction **narrows without weakening below
  the source**: "is a descent direction for every task" is the authors' own property, not an
  aspiration, and the retained "avoiding the dominance of one task over the other" is independently
  supported. Correctly listed as a correction in the Ch.4 errata table.

### Priority 5 · The HGI sweep number (Ch.2) — **CLEAN**

**Anchor:** `the category F1 rose monotonically … from $0.7388 \pm 0.0205$ … to $0.8186 \pm 0.0123$`
(`src/chapters/2_fundamentals.tex:173-177`). Traced to the table itself,
`research/embeddings/hgi/README.md:544-551`: header "5 folds × 50 epochs"; rows 0.4 → 0.7388 ± 0.0205,
0.5 → 0.7678 ± 0.0211, 0.6 → 0.7944 ± 0.0186, **0.7 → 0.8186 ± 0.0123**. Monotonicity is readable off
the four rows without computing. The re-anchoring is a real improvement: the previous "0.74 to 0.82"
was quoted from `hgi/CLAUDE.md:117`, which *rounds* the table — a computed step between page and
source. The adopted 0.7 is the shipped default (`preprocess.py:23`), and the published 0.4 is
confirmed in the HGI paper's Eq. 2. The clause now carries spread, swept range, epoch budget and
scale. The surviving `[VERIFY]` (whether "Cat F1" is macro or weighted) is correctly raised — the
sources do not say — and the prose correctly says "category F1", not "macro-F1".

### Priority 6 · Appendix A reproducibility — **CLEAN, every path resolves**

The section's contract is "names, for each part of the protocol, the code that implements it and the
file its output lives in". I extracted all **13** `\path{}` targets from the prose and checked each on
disk: **13/13 exist**, including the four resolved relative to `stats_n20/` (`m1_stats_n20.py`,
`m2_prereg_perfold.py`, `m1_full_output.txt`, `m2_prereg_output.txt`). Fold partition
(`src/data/folds.py`, StratifiedGroupKFold, five splits, seed 42, grouped by user), seeds
(0/1/7/100 over one fixed partition = twenty fitted models), region-transition prior
(`build_phase3_per_fold_transitions.sh`, per fold, training partition only, consumed only by the
external baseline), joint-best scorer, the significance scripts, and the label-history benchmark all
name both script and output. The section correctly scopes itself to Ch.5's protocol and repeats the
fixed-folds limitation. No number appears here that is not already sourced elsewhere in the document.

### Cross-cutting checks

- **Never-cite sweep (N5/C3).** `STAN v4-collapse`, `fp16`, `bf16`: **zero** prose hits.
  `ReHDM` appears three times but as the **published-protocol reference**
  (`5_mobiwac/05_setup.tex:80`: "A ReHDM reference is reported under its own published protocol"),
  which is the permitted use — the never-cite item is the *v2 row*, and I found no v2 row in the
  prose. `56.16` at `6_conclusion.tex:118` is the capacity-matched control, which I reproduced from
  `capacity_matched_stl_cat/capacity_matched_summary.json`: `bs2048_lr0.0025` n=20 **mean 56.1611,
  std 1.885**; the round-5 correction to "three configurations, twenty each, sixty total, the
  strongest configuration averages … standard deviation 1.89" is accurate, including that 56.16 is a
  **mean**, not a maximum. `20.2` at `6_conclusion.tex:46` carries its width-matching caveat in the
  next sentence.
- **Appendix B static-scope addition (new this round) — numbers CLEAN.** "the fine class takes
  between 284 and 365 distinct values per state, every one of them maps to exactly one of the seven
  top-level categories, and none maps to more than one" traces to
  `docs/archive/fusion-study/results/P0/leakage_ablation/fclass_purity.json`, which I loaded: AL 284,
  AZ 305, CA 333, FL 324, TX 365 (Georgia 313 is in the file but correctly excluded — the claim is
  scoped to "the five Gowalla state subsets the collection uses"). Min 284, max 365 over exactly
  those five. `purity_macro = purity_weighted = 1.0` and `pairs == fclasses` at every row, which is
  precisely "each maps to exactly one, none to more than one". The section's three qualifications are
  correctly framed as qualifications and not softenings, and the "the sequential task is unaffected"
  claim is the right scope. **The one gap:** no `%`-comment ledger line names
  `fclass_purity.json` at the point of use, unlike every other addition this round. Not a number
  defect; a traceability one (N3). Worth one comment line.
- **Appendix C.** The false self-claim is gone: "passed an eighteen-reviewer panel" appears **only
  inside a `%` comment** documenting its own removal, with the reason (two personas recorded gate
  FAILs). Zero prose hits. Correct — and this is the class of self-claim the round exists to catch.
- **BRACIS containment (C4).** Zero prose hits for BRACIS anywhere in `src/`.
- **Ch.2 MTLnet-descent paragraph (new this round, `2_fundamentals.tex:323`).** Claim-shaped and
  carries no numbers; it asserts the joint model is "a specialization of the MTLnet class" that
  "overrides exactly one component, the shared middle". Architectural, so persona 10 territory, but I
  note it is scoped as an implementation fact ("In the released implementation") rather than as a
  design claim, and it is what licenses reading Ch.3's null against Ch.5's win — a frame claim
  correctly marked `[NEEDS SIGN-OFF]`.
- **Gate coverage after the split — verified in both directions.** `check.sh:12` now globs
  `chapters/*.tex chapters/*/*.tex`, and the three Python checkers carry matching globs with the
  reason in comments. Measured: 12 wrapper/frame files + **18 subfiles**; the subfiles hold
  **56.9%** of the non-comment prose, so the pre-fix blind spot was real and the "55 percent" figure
  in the commit message is right. The doubled-macro checker reports **49 files** where it reported 31.
  This is the "gate that has never fired" bias caught in the act; the fix is sound.

---

## 3 · CLAIM / HONESTY LEDGER (persona 07)

**Verbs bound to tests — intact everywhere I checked.** Category "outperforms at all six" rests on the
rev-4 six-dataset Holm family (all reject); region "outperforms at four" rests on the m=4 secondary
family with its scope stated as secondary; AL/AZ are "matches / statistically non-inferior within a
two-point Acc@10 margin (TOST)" and **Arizona is never upgraded** in the Resumo, the Abstract, Ch.5 or
Ch.6. No "beats", "wins", "ties" or "Pareto" as a result verb anywhere in prose (the four "Pareto"
hits are the mathematical term). No bare "everywhere". The scaling claim stays scoped to the five
U.S. states.

**Time-indexing intact.** CBIC's null reads as a conclusion of its time and configuration; the Ch.5
preface names the corrections; the new Ch.2 descent paragraph is what makes the two readable against
each other, and it says so.

**Honesty devices I verified present after this round's edits** (so future editors know they are
load-bearing):

1. The next-place exclusion, in both Resumo and Abstract ("mas não o ponto de interesse exato" /
   "though not the exact next place").
2. The joint-best selection convention, named in both blocks and defined in Ch.5.
3. The 0.06/0.11 checkpoint-convention bound in `06_results.tex` — the hedge around it was cut, the
   measurement was not.
4. The analysis-plan disclosure, now *stronger* than before: it states the plan did not cover
   region superiority and labels those four gains secondary, and it discloses the registered-Wilcoxon
   → paired-t departure with the reason (0.0625 floor at n=4).
5. The four leakage-hygiene grounds in `5_mobiwac/06_results.tex:398` and the "bounds this channel
   rather than closing it" limitation at `:413`, both intact.
6. Ch.3's declined claims (no tuning budget, no epoch count, "code of record" not "the published
   runs").
7. Appendix C's corrected self-description.
8. Ch.4's contribution note and the Ch.5 "submitted, under review" status wording — I found no
   "published"/"accepted" for MobiWac anywhere.

**Negative-result care.** The CBIC null is written with the same care as the wins, and this round's
Ch.2 addition strengthens rather than softens it.

**NEW-CLAIM items already marked, for author sign-off** (I add none): the Check2HGI loss paragraph
(COD-015), the MTLnet-descent paragraph (COD-013), "nineteen"/"+0.68"/"+0.19" in Ch.5, the Resumo and
Abstract cuts, the Appendix A reproducibility section, the Appendix B static-scope section, and the
Appendix B additions paragraph for Article 1.

---

## 4 · COULD NOT VERIFY (fail-closed)

1. **The per-epoch gradient-cosine CSVs.** The run directories `plot_grad_cosine.py` reads
   (`results/check2hgi_design_k_resln_mae_l0_1/<state>/mtlnet_...`) are **not present on this
   machine**; I confirmed all sixteen paths are absent. So the per-state means in N-1 are taken from
   the two records that publish them (`WHY_ORTHOGONAL…:30`, `T4_audit_and_verdict.md:48`), which agree
   with each other, rather than recomputed. If a three-state recomputation excluding Georgia was ever
   made, it is not in the repository and is not what the cited records report. **N-1 stands on the
   sources the sentence itself relies on**, but a recompute would settle the exact bound.
2. **Whether Ch.5's two auxiliary terms belong in Ch.2's equation** (N-3). I established that they
   are v14 build-script defaults and therefore active in the reported runs, but I did not find a
   per-run configuration record for the shipped representation that states the five weights together.
   The chapter's own `[VERIFY]` names this correctly.
3. **The published CBIC run provenance.** The comment states three of four published columns
   reproduce from committed artifacts and the joint model's next-category column does not. I did not
   re-derive those columns; outside this round's delta and explicitly declined in the prose.
4. **Whether the `[NEEDS SIGN-OFF]` items have been approved.** I audit their content, not their
   approval state. `ANCHORS.md` §2 item 4 counts 32; I did not recount after the split.
5. **`GLOSSARY.md` registration** of "bilinear discriminator" and "logistic function". Confirmed
   absent from the registry; whether the author accepts them is his call, and the fail-closed rule
   says the entry lands before the term does.

---

## 5 · WHAT HOLDS (do not touch)

The equation block in Ch.2 is the strongest addition of the round: faithful to its source,
symbol-complete, correctly placed before both chapters that use the representation, and it renders
cleanly. The balancer-screen scope sentence and the pre-registered-test sentences are now among the
best-sourced claims in the document — every cell reproduces from a gated artifact, and the
dissertation/paper parity is exact. The Ch.3 protocol addition is a model of scoped recovery: it
states what the code shows, names what it declines to claim, and dates the facts to the runs rather
than to the tag. Appendix A's path list is complete and correct. The Resumo/Abstract pair is a genuine
claim-parity pair, eleven sentences to eleven, with no floor claim lost.

---

## 6 · IF YOU FIX ONLY TWO THINGS

1. **N-1** — the `\pm0.003` bound, in both files, plus the errata line. It is a number that
   contradicts its own source of record, in a sentence a reviewer of an MTL paper will read closely.
2. **N-2** — one sentence in Ch.2, already drafted by the pass that predicted the problem.

Neither changes a result. Both are cases of a true statement becoming false because something *else*
was corrected, which is the failure mode this round's own history keeps producing.


---

<!-- estado-rodada -->
> **Rodada encerrada · último toque 2026-07-28 · sem autoridade.**
> Este ficheiro é registo de proveniência do que foi discutido nesta passagem, não fonte
> de um facto corrente. O que ficou decidido está em [`VEREDITOS.md`](../../../VEREDITOS.md);
> os valores entregues estão em `CLAUDE.md` §0.1. Não copie nada daqui sem confirmar lá.
