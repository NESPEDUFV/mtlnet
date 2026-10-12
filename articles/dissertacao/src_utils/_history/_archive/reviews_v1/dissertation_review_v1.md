# Comprehensive Dissertation Review

> 🛑 **GERACAO SUPERADA — nenhum numero medido deste ficheiro pode ser citado.**
>
> Isto e a revisao abrangente da dissertacao v1, corrido **antes** de a geracao v18 fechar o vazamento de rotulo no grafo de
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


**Document reviewed:** `articles/dissertacao/src/build/main.pdf` (defense build, 89 pages) and
`articles/dissertacao/src/build/main_final.pdf` (final build, 84 pages)  
**Review date:** 24 July 2026  
**Scope:** first-pass review only; no dissertation claims, results, citations, or source text were changed  
**Overall disposition:** **Not ready for submission in the present form**

## 1. Executive Summary

This is an unusually coherent article-based dissertation with a clear null-result → diagnosis → correction arc. The
framing chapters, time-capsule prefaces, explicit article status labels, negative controls, and discussion of
limitations are stronger than in many dissertations of comparable length. The 89-page defense build is also within the
range of the five local reference dissertations (68–108 pages), and its chapter organization is consistent with their
strongest patterns.

The current obstacle is not the dissertation's topic, contribution, or amount of work. It is the validity and scope of
the central empirical claims. Three issues require resolution before the reported improvements can support the present
conclusions:

1. Check2HGI constructs bidirectional consecutive-visit graph edges while every check-in node contains its category. A
   two-layer graph encoder can therefore propagate the target visit's category into the representation of the last
   history visit. The canonical downstream design reuses those full-graph embeddings. This is a concrete future-label
   leakage path that the current A4 audit does not test.
2. Chapters 3 and 4 use category-derived information in the representation and then evaluate prediction of the same
   category. Unless the intended task is explicitly reconstruction rather than unknown-category prediction, these static
   experiments contain target leakage.
3. Chapter 5 selects a checkpoint on the held-out fold and reports performance on that same fold. The text itself states
   that there is no third split. This produces selection bias and invalidates the current confirmatory interpretation
   unless an inner validation split, nested cross-validation, or a locked selection rule is used.

Two further claim-scope problems are major. The encoder-freezing control shows that the category improvement survives
with the region stream disabled, so it supports an architectural cross-attention/shared-encoder advantage, not evidence
of region-to-category multi-task transfer. In addition, the Nash-MTL solver silently fell back to fixed weights because
its configured solver was unavailable; the older Nash conclusions must be retracted or qualified.

The document also needs a protocol reconciliation, a clean inferential artifact trail, a substantially more candid
AI/provenance statement, repair of Chapter 3 prose and task definitions, front-matter completion, and several layout
fixes. These are addressable, but the three validity issues above should be resolved before extensive polishing.

## 2. Overall Assessment

### Current readiness

| Dimension                                   | Assessment                                                  |
|---------------------------------------------|-------------------------------------------------------------|
| Research problem and motivation             | Strong                                                      |
| Originality and dissertation-level unity    | Strong, conditional on validation                           |
| Organization and contribution narrative     | Strong                                                      |
| Methodological validity of headline result  | Not yet established                                         |
| Statistical support                         | Major revisions required                                    |
| Reproducibility and artifact traceability   | Mixed                                                       |
| Writing quality                             | Strong in Chapters 1, 2, 5, and 6; weak in Chapters 3 and 4 |
| Citation integrity                          | Generally sound; several corrections required               |
| UFV formatting and administrative readiness | Not ready                                                   |
| Overall submission readiness                | **Not ready**                                               |

### Comparison with the reference dissertations

The dissertation already adopts several effective patterns visible in the Canesche, Passe, Lapsus, Viegas, and Germano
examples: an explicit coletânea structure, a foundations chapter, article-status prefaces, a general synthesis, and a
single bibliography. Its length and chapter balance are normal. The time-capsule framing and explicit reporting of
failed approaches are distinctive strengths that should be preserved.

Relative to the strongest examples, this dissertation needs a cleaner front matter, more stable terminology in the
article chapters, a compact cross-study protocol/evidence matrix, and a conclusion whose claims match the exact estimand
and controls. More prose or a longer literature review is not the priority. Validity, claim calibration, and
traceability are.

### Review basis

All 18 reviewer definitions were considered. Seventeen produced substantive independent reviews. Reviewer 14 is a
pre-application change gate and correctly returned “not applicable” because this pass proposed no source-edit batch for
approval. The review also cross-checked LaTeX sources, rendered pages, repository experiment records, statistical
protocols, and relevant implementation code. A clean LaTeX build is not evidence that the scientific issues below are
resolved.

**Repository-answer follow-up (24 July 2026).** Every question originally left in an “Author response” field was
re-audited against the dissertation text, project documentation, article packages, experiment records, and
implementation. Recovered answers are now written directly under their findings. Section 13 distinguishes questions
answered by committed evidence from the small set that still requires an external artifact, author decision,
advisor/Comissão approval, or institutional determination.

---

## 2-bis. Second-opinion pass (Claude, 24 July 2026) — triage

Every one of the 29 findings was independently re-audited against the LaTeX source, the rendered PDFs, the build logs,
the `docs/` science tree, the article packages, and the implementation code. Each finding now carries a **Claude take**
block stating what the files actually say. Verdicts were verified firsthand, not taken on report.

**Marker legend on each heading**

| Marker | Meaning                                                                                     |
|--------|---------------------------------------------------------------------------------------------|
| ✅     | **Closed.** The finding is refuted or already handled in the current text. No action.       |
| 🔧     | **Mechanical.** The fix is determined and needs no judgment from the author, only approval. |
| ⚠️     | **Needs the author.** A decision, an external fact, or an advisor/institutional call.       |

**Triage**

| ✅ Closed (2)    | 🔧 Mechanical (14)                                                                                                           | ⚠️ Needs the author (13)                                                                                            |
|------------------|------------------------------------------------------------------------------------------------------------------------------|---------------------------------------------------------------------------------------------------------------------|
| REV-004, REV-015 | REV-003, REV-006, REV-008, REV-009, REV-010, REV-011, REV-014, REV-016, REV-019, REV-020, REV-021, REV-027, REV-028, REV-029 | REV-001, REV-002, REV-005, REV-007, REV-012, REV-013, REV-017, REV-018, REV-022, REV-023, REV-024, REV-025, REV-026 |

**Severity corrections to the review's own disposition**

- **REV-001 down from Critical to Major.** The leakage *mechanism* is confirmed, but the repository already discovered
  this exact channel on 2026-06-01, instrumented it (`scripts/embedding_eval/leak_sniff.py`), and disqualified two
  encoders for it. The deployed encoder family measures at the clean autocorrelation ceiling. The recommended
  "rebuild causally and recompute everything" is not warranted; three named, cheap residuals are. See the take under
  REV-001.
- **REV-002 must be split.** The Chapter 3 half is **refuted by code** the reviewer did not open (the DGI encoder
  consumes neighbour-averaged one-hots, never the POI's own). The Chapter 4 half is real and is the most
  defense-critical item in this review.
- **REV-003 remedy disproportionate.** The mechanism is confirmed and *already disclosed twice* in the text; the
  convention is symmetric across arms and the comparator holds the larger search space, so the residual bias is
  conservative for the headline delta. One sentence closes it, and that sentence is already drafted in
  `src_utils/_history/_review_v1/09_stats_leakage_skeptic_report.md:294-307`.
- **REV-004 and REV-015 refuted.** The text already says "a stronger shared trunk, not the region task teaching the
  category one" and already reports the 4-of-6 region split in four separate places.

**Consequence for the submission gate.** The review's gate reads "do not change the disposition to ready until
REV-001–REV-003 are resolved". On the evidence, none of the three requires a re-run. What they require is disclosure:
cite the leak audit you already have (REV-001), scope the Chapter 4 static task (REV-002), and name the selection-bias
consequence (REV-003). The binding blockers are instead **administrative** (REV-023, REV-025, REV-026) and one
**fact-gate failure** (NEW-1 below).

### New findings — defects not raised by the review

| #          | Finding                                                                                                                                                                                                                                                                                                                                                                                                                          | Where                                                                    | Severity    |
|------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|--------------------------------------------------------------------------|-------------|
| **NEW-1**  | `al_capmatch_summary.json` and the job `d38a1382` artifacts **do not exist anywhere in the repository** (`find` over the whole tree, hidden dirs included, returns nothing). The Alabama capacity numbers 56.16 / 55.74 / 55.61 printed at `6_conclusion.tex:78` trace only to prose. Under `AGENT_GUARDRAILS` N1/N3 this is a **fact-gate failure**, and it is the only load-bearing Chapter 6 number with no committed source. | `6_conclusion.tex:78`; `storyline/audit/capacity_baseline_experiment.md` | **Blocker** |
| **NEW-2**  | The freeze-control figure "within $0.3$ of the joint model" is measured against the **v16 diagnostic-best** comparand, while the chapter's own Table 3 prints **v17 joint-best** cells. Against Table 3 the gaps are **−1.01 (AL)** and **−2.12 (AZ)**, not ≤0.3. The verdict is unaffected, but the number does not match the table on the facing page. The control is also n=5, seed 0, undisclosed against an n=20 document.  | `5_mobiwac.tex:573`; `W6_ENCODER_ISOLATION.md:22-24,54`                  | Major       |
| **NEW-3**  | The dissertation names **two different tests for the same verb**. `2_fundamentals.tex:448-450`: the paired **Wilcoxon** "is the test that licenses the verb ``outperforms''". `5_mobiwac.tex:355`: "superiority is tested with a paired **$t$**". Nowhere does the document say a substitution occurred.                                                                                                                         | Ch.2 vs Ch.5                                                             | Major       |
| **NEW-4**  | `3_cbic.tex:26-27` says the Nash finding is one "the following chapters do not rely on" — but `4_courb.tex:115` trains with the Nash-MTL balancer. Should read "Chapter 5".                                                                                                                                                                                                                                                      | `3_cbic.tex:26-27`                                                       | Moderate    |
| **NEW-5**  | `abntex2-UFV.sty`'s `\imprimirfolhadeaprovacao` hardcodes a **prior student's name** (`\assinatura{\textbf{Gabriel Vita Silva Franco}}`). Currently unused, so nothing wrong ships today — but switching from the placeholder to the macro without editing it prints the wrong author on the approval sheet.                                                                                                                     | `abntex2-UFV.sty`                                                        | Trap        |
| **NEW-6**  | Bibliography: **99 entries, 98 `\bibitem`s**. `liu2014geographical` is orphaned, yet `apx_b_errata.tex:267` prints that key to the reader — pointing at an entry the printed bibliography silently drops.                                                                                                                                                                                                                        | `references.bib` / `build/main.bbl`                                      | Minor       |
| **NEW-7**  | Chapter 5's wide tables are scaled by `adjustbox`, not by a size command, to **8.13 pt (Table 8)** and **8.00 pt with 6.00 pt uncertainties (Table 10)** against 11.96 pt body text — i.e. below `\footnotesize`, nearer `\scriptsize`/`\tiny`.                                                                                                                                                                                  | `5_mobiwac.tex:315,478`                                                  | Moderate    |
| **NEW-8**  | `apx_b_errata.tex:81` says the Chapter 3 dataset figures were supplied "from the current data pipeline". The current pipeline yields the **Chapter 5** counts; 990,518 came from the CoUrb published table via an intermediate ETL. As written, the sentence invites the question it exists to close.                                                                                                                            | `apx_b_errata.tex:81`                                                    | Moderate    |
| **NEW-9**  | Appendix B declares "**three marked additions**" for Chapter 4 while at least **seven** non-published sentences exist (three table leads and a caption sentence are filed under "mechanical" in the ledger). Appendix B opens by claiming it lists "every content departure", so the undercount contradicts the appendix's own stated purpose. Worth checking whether the Ch.3 and Ch.5 ledgers share the pattern.               | `apx_b_errata.tex` §B.2; `4_courb_ADAPTATION_LEDGER.md:29`               | Moderate    |
| **NEW-10** | Actual builds are **89 and 84 pages** (`pdfinfo`), documented as 87/83 in 27+ places. Second-order consequence: all 18 reports in `src_utils/_history/_review_v1/` were run against the older 87 pp build, so their page references are off by up to two.                                                                                                                                                                                 | `CLAUDE.md:28-29`, `PLAN.md:17-18`, `HANDOFF_v1.md:68,127`               | Minor       |

### Where the review is strongest and weakest

**Strongest.** REV-006 (the Appendix A universal-protocol sentence is flatly contradicted twice by Chapter 4 inside the
same PDF, and is free frame prose to fix), REV-014, REV-021, REV-023, REV-025, REV-026, REV-029. These are correct,
well-scoped, and mostly cheap.

**Weakest.** The review read the LaTeX and the docs but did not open the implementation where it mattered most. REV-002
(a) is refuted by `research/embeddings/dgi/preprocess.py`; REV-001's consequence is largely measured in
`docs/results/embedding_eval/rescreen_cat/`; REV-019's premise about HGI's exports is contradicted by
`research/embeddings/hgi/hgi.py`; REV-010 cites the Chapter 3 preface as the source of a contradiction when it is the
fix; REV-027's Chapter 4 half is disproved by a grep. Treat its file-level assertions as leads.

**Notable.** A large share of these findings were **already identified inside this repository** before the external
review — `_history/_review_v1/09_stats_leakage_skeptic_report.md`
(B1, B3, B4), the MobiWac review panels, `_history/_review_v1/CONSOLIDATED_REVIEW_REPORT.md (sec. 18_visual_presentation_report.md)`
(M1, M2, M5, m7, m9), and `NORTH_STAR.md:146`. That independent reproduction raises confidence in the findings and
lowers the cost of remediation: replacement sentences for several of them are already drafted in this repo.

---

## 3. Major Issues

### REV-001 — Future-label leakage path in Check2HGI ⚠️

- **Severity:** Critical
- **Status:** Open
- **Classification:** Confirmed error
- **File:** `src/chapters/5_mobiwac.tex`; `research/embeddings/check2hgi/preprocess.py`;
  `research/embeddings/check2hgi/CheckinEncoder.py`; `src/data/inputs/core.py`;
  `research/embeddings/check2hgi/check2hgi.py`
- **Section:** Chapter 5, Check2HGI representation and leakage controls
- **Reported by:** Reviewers 09 and 11; independently code-verified in consolidation

**Finding**

The preprocessing code connects consecutive visits bidirectionally (`preprocess.py`, lines 187–199), and each check-in
node contains a category one-hot feature (lines 615–624). The two-layer graph encoder can therefore pass the immediately
following target visit's category to the final history visit in one hop, and later future visits in two hops. The
exported embeddings are computed on the full graph (`check2hgi.py`, lines 862–865), while the prediction target is the
visit immediately after the history (`core.py`, lines 257–268). The dissertation's statement that the representation
“never sees the next category” (`5_mobiwac.tex`, lines 235–239) is not supported by the implementation.

**Why it matters**

This creates a direct path from a future label into the input representation and can plausibly account for the unusually
high representation separability and large accuracy gain. User-disjoint folds do not prevent leakage along edges within
a user's trajectory. The A4 audit tests POI-level category proxies, not this contextual future-edge channel.

**Recommended action**

Rebuild and rerun Check2HGI using strictly causal adjacency or per-example future-edge masking, with embeddings
fitted/exported without access to target or later visits. Recompute all downstream models, controls, figures, and
statistics. Until then, remove or suspend the affected headline claims.

**Author response**
[claude science]
> So yes this is a problem, but since we already prove for florida we can extrapolated that to the other states no ?
> if not, or if we need more evidences let's run this executions in parallel in the nespegpu.

**Claude take (2026-07-24) — severity DOWN from Critical to Major; mechanism confirmed, consequence largely measured,
disclosure missing.**

The mechanism is real and I verified every link myself: bidirectional consecutive-visit edges
(`research/embeddings/check2hgi/preprocess.py:195-199`), a category one-hot in the node features
(`preprocess.py:615-624`), a **2-layer** GCN so node *t* aggregates *t*±2 (`model/CheckinEncoder.py:16,34-36`),
full-graph export (`check2hgi.py:862-865`), and a target at *t+1* which therefore sits inside the last history node's
receptive field (`src/data/inputs/core.py:257-268`).

**What the reviewer did not find.** This exact channel was independently discovered in this repository on 2026-06-01,
named precisely, instrumented, and used to disqualify two encoders.
`docs/results/embedding_eval/rescreen_cat/RESCREEN.md:56-57` calls it "a forward-temporal neighbor-category bleed" and
establishes the correct test: a per-step probe predicting the next category from the **single last window slot**,
against the ~0.41 last-visited-category autocorrelation ceiling. `scripts/embedding_eval/leak_sniff.py` implements it.
Committed results (`leak_sniff_fl.csv`, `leak_sniff_resln_fl.csv`, Florida, 5-fold, GroupKFold-by-user):

| encoder                                                         | per-step probe (std / raw) | verdict                                          |
|-----------------------------------------------------------------|----------------------------|--------------------------------------------------|
| GCN control (= the canonical Check2HGI lineage)                 | 0.4090 / 0.4074            | clean, at ceiling                                |
| ResLN (the v13/v14 encoder the MobiWac substrate descends from) | 0.4197 / 0.4182            | clean                                            |
| **GAT**                                                         | **0.4976 / 0.4863**        | **LEAK, disqualified**                           |
| R-GCN                                                           | 0.3328 / 0.4142            | clean per-step; leaked 0.754 at L2, disqualified |

So the leak channel exists, is known, is gated, and the deployed encoder family measurably does not exploit it linearly,
while two encoders that did were thrown out for it. "Can plausibly account for the large accuracy gain" is therefore not
supported as stated.

**Three residuals keep this open, and they are the real work:**

1. **Coverage.** Florida only, seed 0. Not measured at AL, AZ, TX, CA, or Istanbul.
2. **Probe power.** The per-step gate is *linear*, and `RESCREEN.md:94` proves it can miss a nonlinear leak (R-GCN
   passed per-step at 0.414 and leaked at 0.754 under the GRU). The authoritative L2 gate compares a candidate against
   the GCN control, so it is structurally blind to a leak the control itself carries.
3. **Lineage.** The deployed substrate is `check2hgi_dk_ovl` (design_k + mae + ResLN, stride-1). Only its ResLN ancestor
   was sniffed, not the substrate as shipped.

**Recommended action (replaces "rebuild causally and recompute everything", which is not achievable before an August
defense and is not warranted by the evidence):**

- Cite the leak-sniff audit in Chapter 5. Right now the dissertation asserts the negative and never shows the
  measurement that supports it. That is the actual defect.
- Run the existing `leak_sniff.py` at the remaining five datasets on the shipped `check2hgi_dk_ovl` embeddings. Cheap:
  existing parquet, a probe, no retraining.
- Add one **nonlinear** per-step probe (small MLP/GRU on the single last slot) to close the R-GCN-shaped blind spot.
- The one decisive control, if time allows: rebuild Check2HGI at **Alabama only** with backward-only (causal) edges, or
  with the category one-hot removed from node features, and compare L2 next-category. One small-state embedding build.
  If the lift survives, the leak explanation is dead and you can say so at the defense.

**Needs your decision:** whether to run the AL causal/ablated rebuild before v1 or defer it to the defense Q&A with the
leak-sniff evidence in hand.

### REV-002 — Static category target leakage in Chapters 3 and 4 ⚠️

- **Severity:** Critical
- **Status:** Open
- **Classification:** Confirmed mechanism; intended task requires clarification
- **File:** `src/chapters/3_cbic.tex`; `src/chapters/4_courb.tex`
- **Section:** Chapter 3 DGI features and category task; Chapter 4 category representation
- **Reported by:** Reviewers 09 and 11; confirmed in consolidation

**Finding**

Chapter 3 states that the DGI input contains a POI category one-hot vector (`3_cbic.tex`, lines 131–135) and later
evaluates prediction of that same POI category (lines 152–154). Chapter 4 learns an embedding per category and remaps it
to the POI (`4_courb.tex`, lines 169–188), then pairs the representation with category target \(c\) (lines 121–125).

**Why it matters**

If the intended task is to infer an unknown POI category, the target is already encoded in the input. The resulting
scores do not measure target-blind classification. If the intended task is representation reconstruction or downstream
utility with category metadata available, the current “category prediction” framing is misleading and not comparable to
unknown-label prediction.

**Recommended action**

Clarify the estimand. For unknown-category prediction, rerun with the target category removed from every representation
input and pretraining feature available to that POI. For reconstruction, rename and reframe the task, establish a
non-trivial baseline, and narrow all conclusions.

**Author response**

> So, about the leak in the ch. 4, I believe worth a better investigates in the hgi, cause if I am not wrong it used the
> fclass and not the category. But after eval it deeply, lets eval how huge is this problem, cause the numbers were very
> near with the dgi, and if necessary let's create a appendix for this topic and in the preface of the ch. 4 we point to
> it.

**Claude take (2026-07-24) — SPLIT THE FINDING. The Chapter 3 half is refuted by code; the Chapter 4 half is real and is
the most defense-critical item in this review.**

**Chapter 3: refuted.** The reviewer read only the .tex. `research/embeddings/dgi/preprocess.py:115-130` builds two
matrices: `embedding_array` (the POI's own category one-hot) and `embedding_array_test` (the **mean of its Delaunay
neighbours'** one-hots, self excluded, zeros for isolated nodes). `dgi.py:56` binds `x = embedding_array_test`, and
`DGIModule.py:69` encodes `data.x`. **The POI's own label never reaches the encoder.** That is spatial homophily, which
is exactly what `3_cbic.tex:131` motivates, not target leakage.

Two real residuals remain in its place, both smaller and different in kind:

- **Text/code mismatch.** `3_cbic.tex:133` (verbatim published) describes the *self* one-hot construction, i.e. the
  leaky one, not the one the released code trains on. A reader reaching the reviewer's conclusion is reading the paper
  correctly. This belongs in the errata table alongside the wall-time and MFLOPs rows already there.
- **Attenuated self-path.** `POIEncoder` is a single `GATConv` with PyG's default `add_self_loops=True`, so POI *i*'s
  own one-hot re-enters via its neighbours' means at roughly 1/deg weight. Non-zero, not clean.

**Chapter 4: confirmed, and it needs no code to establish.** `4_courb.tex:188` states in the chapter's own words that
the embedding is "generated **per category and remapped to each POI**", and `:123` then pairs that representation with
the same POI's category as the target. The repo's implementation of the same construction is explicit
(`research/embeddings/hgi/poi2vec.py:486-487`: `poi_embeddings[valid] = fclass_embeddings[fclass_values[valid]]`;
`research/embeddings/hgi/CLAUDE.md`: "Multiple POIs with same fclass share IDENTICAL embeddings"). The static-task input
is a deterministic function of the target label, regionally smoothed. The **sequential** task in both chapters is clean
(`3_cbic.tex:161-167`, `4_courb.tex:125`) — the reviewer did not make that distinction and it matters a great deal.

**Why this is defense-critical.** `apx_a_contributions.tex:91-93` tells the banca that a prior submission was attacked
for label leakage and that Chapter 5 answers it with a dedicated audit. A committee member who reads that, then reads
`4_courb.tex:188` and `:123`, will ask why Chapter 4 got no equivalent treatment. Chapter 4 already carries a protocol
caveat in its preface (`:13`) — the mechanism for adding one more sentence exists.

**Needs your decision:** (a) a preface scope sentence for Ch.4 saying the static-task figures should be read as
representation quality under label-derived features rather than as inductive category inference, with the
sequential-task figures unaffected — this is a new claim about a published, **co-authored** result (Tarik is first
author), so courtesy notice applies; (b) whether to open the two code-of-record repos
(`github.com/VitorHugoOli/PoiMtlNet`, `github.com/TarikSalles/Spatial_Embeddings`) before any errata row asserts what
the published implementations did. I audited this repo's same-lineage code, not the paper's.

**Resolution notes**

>

### REV-003 — Checkpoint selection and reporting use the same held-out fold 🔧

- **Severity:** Critical
- **Status:** Open
- **Classification:** Confirmed error
- **File:** `src/chapters/5_mobiwac.tex`; `src/training/runners/mtl_cv.py`
- **Section:** Chapter 5, experimental protocol and statistical analysis
- **Reported by:** Reviewers 01, 09, 10, 11, and 12

**Finding**

The dissertation explicitly states that the held-out fold is used as validation and that no third split exists
(`5_mobiwac.tex`, line 341). The validation-selected epoch is then the reported score (lines 518–527). The runner uses
the same held-out loader for checkpoint selection and evaluation.

**Why it matters**

Choosing the epoch, loss weight, or hyperparameters on the observations later used for performance reporting
optimistically biases the estimate. The bias does not necessarily cancel across models because search spaces and tuning
decisions differ.

**Recommended action**

Use an inner user-disjoint validation split within each training fold, nested cross-validation, or a selection rule
fixed without inspecting the reporting fold. Repeat all model comparisons under one common protocol and distinguish
exploratory tuning from confirmatory evaluation.

**Author response**
> Great point, we can address as the claude suggest, and I add one more point, we can change the lmitation in the
> mobiwac in the
> original text and in the dissertacao, since we cna still send a reviewd version for the conference.

**Claude take (2026-07-24) — mechanism CONFIRMED, already disclosed twice, remedy DISPROPORTIONATE. One sentence closes
it, and that sentence is already drafted.**

Code-confirmed: `src/data/folds.py:1466-1477` produces a two-way split only; `mtl_cv.py:930-932` selects on the val
loaders and `:2294-2300` reports from the same loaders at the selected checkpoint; `mtl_cv.py:200-213` computes the
selector scalar from val-epoch metrics.

But the text already says so, plainly, twice: `5_mobiwac.tex:341` ("The held-out fold is the validation data; we reserve
no third split") and `:521-527` ("every reported model is one saved artifact per fold, read at its validation-selected
epoch"), with a sensitivity check bounding the alternative convention at 0.06 / 0.11 points. The convention is applied
identically to the dedicated arms (`category_cv.py:97`, `next_cv.py:195`), so the word "Throughout" is literally
accurate.

The reviewer's "does not necessarily cancel" objection is weak **here** specifically: the search spaces differ in the
direction that *hurts* the paper. The dedicated comparator gets a per-dataset batch-size × learning-rate sweep at n=20
best-vs-best (`5_mobiwac.tex:520`), while the joint model runs one frozen recipe across all six datasets. The residual
non-cancelling bias therefore favours the comparator, making the reported Δ conservative. Against Δcat of +5.33…+9.35 pp
with cross-seed sd 0.01–0.10, no plausible residual moves a verdict.

Where it does bite: the region side at AL/AZ (Δ −0.41 / −0.00), and the **external** baselines, where the text never
states whether HMT-GRN/STAN were read under the same rule.

**What is actually missing** is one sentence naming the consequence. Your own persona-9 reviewer already drafted it
(`src_utils/_history/_review_v1/09_stats_leakage_skeptic_report.md:294-307`): "because epoch selection consults the evaluation
fold, the absolute scores are optimistic; the joint-vs-dedicated comparison is unaffected, as both models are selected
identically on the same folds and the bias cancels in the difference." The Limitations paragraph
(`5_mobiwac.tex:620-621`) currently names only two limits and does not include this one.

"Nested cross-validation, repeat all model comparisons" means regenerating 6 datasets × 4 seeds × 5 folds × (joint + 2
dedicated + baselines) weeks before the defense, for a chapter reproducing a paper under review at EDAS. That is not
proportionate.

**Needs from you:** approve the drafted sentence (Ch.5 is version-of-record, so it rides as an errata row), and decide
whether to state the external-baseline epoch-selection rule.

**Resolution notes**

> _Record the revised split diagram, selection rule, rerun IDs, and updated estimates here._

### REV-004 — Category gain is not demonstrated to be cross-task MTL transfer ✅

- **Severity:** Major
- **Status:** Open
- **Classification:** Confirmed claim overreach
- **File:** `src/chapters/5_mobiwac.tex`; `src/chapters/6_conclusion.tex`;
  `docs/studies/closing_data/archive/findings/W6_ENCODER_ISOLATION.md`
- **Section:** Chapter 5 encoder-isolation control; Chapter 6 answers to research questions
- **Reported by:** Reviewers 07, 09, 10, 11, 12, and 17

**Finding**

The encoder-isolation control reports that the full category gain remains when the region stream is frozen and region
loss is zero. The underlying finding explicitly says “architecture, not transfer.” The dissertation nevertheless uses
the gain to answer that multi-task learning helps category prediction.

**Why it matters**

The result supports the utility of the joint architecture—especially cross-attention/shared feature processing—but does
not show that learning the region task transfers useful supervision to category prediction. Reverse category-to-region
transfer is also not isolated.

**Recommended action**

Reframe the category result as an architectural gain unless a controlled transfer experiment is added. Separate three
claims throughout: operational performance of the joint artifact, cross-task supervision transfer, and parameter
sharing/cross-attention effects.

**Author response**

> Claude take!

**Claude take (2026-07-24) — REFUTED. The text already says the opposite of the overclaim.**

`5_mobiwac.tex:571-574`, verbatim: "a control shows otherwise. We freeze the region pathway at the start of training so
it can neither learn nor teach the category task, yet the full category gain survives … **We therefore attribute the
category gain to a stronger shared trunk, not to the region task teaching the category one** … We report this
attribution as a finding, not a hypothesis." `6_conclusion.tex:68-72` repeats it. This reproduces the source finding
(`W6_ENCODER_ISOLATION.md:3-8`) almost verbatim, and the single-model framing is preserved at
`1_introduction.tex:173-176`. No sentence in Chapters 1, 5, or 6 attributes the category gain to cross-task transfer.
Nothing to reframe.

**Two sub-defects surfaced that the reviewer did not raise — see NEW-2 in the summary.** The "within $0.3$ of the joint
model" figure at `5_mobiwac.tex:573` is measured against the **v16 diagnostic-best** comparand
(`W6_ENCODER_ISOLATION.md:22-24`), while the chapter's own Table 3 prints **v17 joint-best** cells; against Table 3 the
gaps are −1.01 (AL) and −2.12 (AZ), not ≤0.3. The qualitative verdict is unaffected (the probe still clears the
dedicated cells by +5.3…+7.2), but the number as printed does not match the table on the facing page, and a careful
examiner can compute that. The freeze control is also **n=5, seed 0 only** (`W6_ENCODER_ISOLATION.md:54`) while every
other number in the chapter is n=20, and neither chapter says so.

**Resolution notes**

> _Record the final claim wording and any added ablation here._

### REV-005 — Nash-MTL results are invalid because the solver silently fell back ⚠️

- **Severity:** Major
- **Status:** Open
- **Classification:** Confirmed error
- **File:** `src/chapters/3_cbic.tex`; `src/chapters/4_courb.tex`; `src/configs/experiment.py`; `requirements.txt`
- **Section:** Chapters 3 and 4, dynamic loss balancing
- **Reported by:** Reviewers 07 and 10

**Finding**

The configured ECOS solver is absent from the environment, and the implementation silently collapses to fixed weights
`[1,1]`. Chapter 3 nevertheless states that Nash consistently performs better and mitigates gradient conflicts; Chapter
4 describes Nash balancing as beneficial.

**Why it matters**

The experiments do not establish an empirical Nash-MTL effect. Silent fallback also weakens reproducibility and makes
the algorithm label inaccurate.

**Recommended action**

State the exact implementation failure in both article prefaces and the synthesis; retract empirical Nash
superiority/gradient-conflict claims. If Nash remains important, rerun with a verified solver, logged weight
trajectories, and failure-fast checks.

**Author response**

> Let's ignore this error, since in the final model is not even used. For the ch. 3 we don't add any caveat or errata.
> let's fix the real issue of the ch.3 that says that the follow chapeter uses nahs, when indeed just the ch. 4 does.

**Claude take (2026-07-24) — bug CONFIRMED and dated; "results invalid" OVERSTATED; one mandated caveat was simply never
written.**

The bug is real: commit `a76fb9cc` (2026-04-10), "NashMTL was silently degraded to fixed [1,1] task weights … because
cvxpy's ECOS solver was not installed … the upstream `solve_optimization` swallows every exception in a bare `except:`".
Now fixed (`src/losses/nash_mtl/loss.py` raises instead of swallowing; `requirements.txt:27-31` pins `cvxpy==1.6.4` +
`ecos==2.0.14`), and documented at `docs/context/MTL_OPTIMIZERS.md:123-126`.

**Scope it correctly.** Only the *optimizer-preference* claim dies: Ch.3's Nash-vs-alternatives comparison compared
three arms that were all effectively equal-weighting. Ch.3's headline (MTL ≈ single-task) does not depend on which
balancer was live. Ch.4's representation contrast is self-consistent, since baseline and variants shared the same
degraded optimizer. Ch.5 does not use Nash at all. So "retract empirical Nash superiority" is right; "the experiments
are invalid" is not.

**Ch.3 is already handled.** The preface (`3_cbic.tex:25-27`) carries the of-the-time caution and
`apx_b_errata.tex:87-91` records the deliberate non-correction.

**Two genuine gaps, both cheap and both in frame prose you own:**

1. **Ch.4 has no Nash caveat at all.** Its preface (`4_courb.tex:13`) covers the split protocol, authorship, and
   terminology, and says nothing about Nash — even though `NORTH_STAR.md:146` explicitly lists "Nash-MTL caveat as in
   Ch.3" under Ch.4 honesty items. That instruction was written and not executed.
2. **The Ch.3 preface is factually wrong about Ch.4.** It says "the following chapters do not rely on it", but
   `4_courb.tex:115` trains with the Nash-MTL balancer. Should read "Chapter 5 does not rely on it." (See NEW-4.)

Corroborating evidence the reviewer did not have: the author-provided CoUrb-era codebase at
`/Users/vitor/Desktop/mestrado/temp/tarik-new/PoiMtlNet_Novo/` still carries the **unfixed** bare-except
(`src/criterion/nash_mtl.py:135-138`) and a `requirements.txt` with no `ecos`. Circumstantial, not proof of the
execution environment, but it is the same failure signature.

**Resolution notes**

> _Record the corrected historical interpretation or rerun here._

### REV-006 — “Used throughout” protocol conflicts with Chapters 3 and 4 🔧

- **Severity:** Major
- **Status:** Open
- **Classification:** Confirmed inconsistency
- **File:** `src/chapters/2_fundamentals.tex`; `src/chapters/3_cbic.tex`; `src/chapters/4_courb.tex`;
  `src/chapters/apx_a_contributions.tex`
- **Section:** Evaluation protocol and contribution appendix
- **Reported by:** Reviewers 01, 04, 07, 09, 11, and 12

**Finding**

Chapter 2 presents user-disjoint evaluation as the protocol used throughout, and Appendix A says every Chapters 3–5
comparison uses a common user-disjoint protocol. Chapter 4 explicitly uses sample-stratified folds with user overlap.
Chapter 3 reports five folds but does not identify the split axis.

**Why it matters**

Protocol heterogeneity affects leakage risk and prevents direct cross-chapter comparisons. The current universal wording
is false.

**Recommended action**

Add a one-page cross-study protocol matrix covering unit of split, user overlap, fitting scope, model-selection data,
seeds, folds, and inferential unit. Replace universal statements with chapter-specific facts and state that the protocol
strengthened over time.

**Author response**

> Indeed in the COURB and CBIC the a different user-disjoint, the StratifiedKFold and the Mobiwac already used the
> StratifiedGroupKFold, but in the split we always pass the users ids as a group, so I am not sure if this is really a
> problem, you can eval reading the commits. But as claude take says we need to address it in the common text not in the
> erratas. Oh and a important part is that we just do statistical analysis for the mobiwac, not for other, if the text
> let the interpretation as this was done for all we also need to change.

**Claude take (2026-07-24) — CONFIRMED, and this is the single most defensible finding in the whole review. Free to fix,
no errata, no decision.**

`apx_a_contributions.tex:60-63`, verbatim: "The same codebase standardizes evaluation across the dissertation through a
user-disjoint cross-validation and significance protocol, so that **every** single-task-versus-multi-task comparison
reported in Chapters 3 to 5 rests on a common, leakage-controlled measurement procedure rather than on per-study ad hoc
splits."

Contradicted twice by Chapter 4's own text, in the same PDF. `4_courb.tex:226`: "The split is stratified **by sample,
not by user**, so the check-ins of one user may appear in both training and validation." `4_courb.tex:13` repeats it in
the preface. Code-verified independently: the CoUrb splitter imports only `StratifiedKFold` and passes no `groups=`
(`.../PoiMtlNet_Novo/src/etl/mtl/create_fold.py:12,226,229`).

Three separate falsehoods in that one sentence: not user-disjoint in Ch.3/4; **no** significance protocol in Ch.3/4
(neither runs Wilcoxon, Holm, or TOST — Ch.3 reasons from overlapping standard deviations at `:344`); and not "the same
codebase" (Ch.3 ran in `PoiMtlNet`, Ch.4 in `Spatial_Embeddings`, both external).

`2_fundamentals.tex:16-18` ("validation protocol **used throughout**") and `:442-448` (present tense, unqualified)
compound it.

All three loci are **dissertation-authored frame prose**, outside the errata regime. A banca reads a self-contradiction
inside one PDF as carelessness, and it is the cheapest thing in this review to eliminate. The honest version arguably
strengthens the arc — Ch.4's preface already makes the protocol tightening part of the story. Roughly three sentences.

**Resolution notes**

> _Record the matrix location and corrected universal claims here._

### REV-007 — Statistical protocol and artifact trail are not internally synchronized ⚠️

- **Severity:** Major
- **Status:** Open
- **Classification:** Confirmed inconsistency
- **File:** `src/chapters/2_fundamentals.tex`; `src/chapters/5_mobiwac.tex`;
  `docs/studies/closing_data/STATISTICAL_PROTOCOL.md`; `docs/studies/closing_data/v17_completion/stats_n20/RESULTS.md`;
  `docs/studies/closing_data/joint_best/`
- **Section:** Confirmatory inference and joint-best results
- **Reported by:** Reviewers 04, 06, 07, 09, 10, and 12

**Finding**

The dissertation describes a Wilcoxon-based protocol fixed in advance, but the final n=4 seed-level analysis uses paired
t-tests after noting that the minimum exact Wilcoxon p-value is 0.0625. This deviation is documented in a results note
but not candidly explained in the dissertation. Region superiority is also post-hoc relative to the registered
non-inferiority framing. Some older joint-best notes are stale, although the current authority chain now resolves the
earlier apparent disagreement.

**Why it matters**

The point estimates can be traced, but the confirmatory status, multiplicity family, and authoritative statistical
artifact cannot be reconstructed cleanly. “Fixed in advance” overstates the record.

**Recommended action**

Create one immutable analysis manifest that names the exact input files, seeds, fold aggregation, tests, multiplicity
families, deviations, and generated tables. Regenerate all reported intervals and p-values from that manifest. Label
deviations and post-hoc tests explicitly.

**Author response**

> So with the takes of the claude science we already solve good part, about what is missing: let's add the manifest and
> versioned it, and fix the docstrings.

**Claude take (2026-07-24) — CONFIRMED, with one defect worse than the reviewer states and one path correction.**

Path note: `docs/studies/closing_data/STATISTICAL_PROTOCOL.md` does not exist; the protocol is at
`docs/studies/closing_data/v17_completion/STATISTICAL_PROTOCOL.md`.

**(i) The Wilcoxon→t deviation is logged, in the wrong place.** Pre-registration is unambiguous
(`STATISTICAL_PROTOCOL.md:54-60`: paired Wilcoxon, n=20 pooled). The deviation is recorded at
`stats_n20/RESULTS.md:103-108` and correctly reasoned (at n=4 the exact one-sided Wilcoxon floor is 0.0625 > α). But
`RESULTS.md:20-21` cites it as "per protocol §8's powered-t deviation" and **§8 contains no such entry** — only the
2026-07-18 joint-best convention switch. The protocol's own §8 mandates that deviations be logged there. Dangling
forward reference.

**(ii) The dissertation contradicts itself across chapters — worse than "not candidly explained".**
`2_fundamentals.tex:448-450`: "The paired **Wilcoxon** signed-rank test … **is the test that licenses the verb ``
outperforms''**". `5_mobiwac.tex:355`: "superiority is tested with a paired **$t$** on the per-seed means". Same verb,
two different tests, two chapters, and nowhere does the document say a substitution occurred. Your own persona-9
reviewer called this "THE single weakest methodological sentence in the experimental chapters" (`_history/_review_v1/09:207`,
marked BLOCKER). See NEW-3.

**(iii) Region superiority is genuinely post-hoc.** The protocol pins region as **non-inferiority/TOST only** (`:44`,
`:261-264`); no region-superiority family is enumerated anywhere. The §8 entry recording it is dated 2026-07-18,
post-unblind. So `5_mobiwac.tex:355`'s "We fix the assignment in advance, before reading any results" overstates the
record for the region axis. Mitigation: the CIs are far from zero (TX +2.10…+2.13, CA +2.19…+2.21, FL +0.67…+0.76; only
Istanbul +0.15…+0.23 is thin), so correction would not move a verdict.

**(iv) No single manifest.** Three stale nodes confirmed: `joint_best/TASKS.md:76-79` shows T7 unchecked though
`STATISTICAL_PROTOCOL.md:286-291` records the joint-best reruns completed with the exact CIs the chapter prints;
`JOINT_BEST_RESULTS.md:72` and `:99-101` are superseded by the 2026-07-18 ruling.

**Proportionality.** "One immutable manifest, regenerate all intervals and p-values" is heavier than the defect. The
parity gates already prove artifact→table fidelity (18/18, 90/90, 6/6). A one-page `ANALYSIS_MANIFEST.md` naming inputs,
tests, families and deviations satisfies the substance.

**Needs from you:** (1) reconcile Ch.2 to Ch.5 on the test name — Ch.2 is your own frame prose, free to fix, and this is
the highest-value single edit in the statistics family; (2) whether to add a deviation clause to Ch.5 (errata); (3)
whether to label region superiority post-hoc-confirmed.

**Resolution notes**

> _Record the manifest, command, checksums/commit, and corrected wording here._

**[CLAUDE SCIENCE]Audit + remedy pass (2026-07-25, author-approved). RESOLVED in the source; two items remain open.**

Independent re-derivation of every claim in this entry against the committed tree, plus the paper and Chapter 5 edits it
called for. Full report: `articles/[mobiwac]/science/AUDIT_statistical_protocol.md`
(English, with the 19-claim reconciliation table) and its pt-BR summary
`RELATORIO_protocolo_estatistico_ptbr.md`.

**What the audit confirmed.** Items (i), (ii) and (iii) of the Claude take above all hold. The protocol registers
next-region as **non-inferiority only** (`STATISTICAL_PROTOCOL.md` §1 family table, §5.2 family enumeration), and the
original 2026-06-21 text (`git show c96c67e3:...`) is identical on both points, so this is not a later deletion. The
`RESULTS.md:20` forward reference to "protocol §8's powered-t deviation"
is dangling: §8 carries only the 2026-07-18 joint-best switch, and the location §8 itself mandates
(`docs/studies/closing_data/log.md`) never received the entry.

**Three findings this entry did not have.**

1. **A fourth defect, more serious than (i) to (iv): the released bundle did not contain the record.**
   The paper's footnote 1 points at `github.com/VitorHugoOli/PoiMtlNet/tree/mobiwac`. That branch shipped **zero files
   under `docs/`** — no protocol, no deviation log, no `joint_best/`. So "released with the code" was false as written,
   and the deviation was unreachable for any reviewer. Worse, the branch's
   `README.md` §6 announced the bundled `superiority_wilcoxon.py` as implementing "the pre-registered tests" including
   "region superiority (FL/CA/TX)", repeating the unregistered claim in the one artifact the reader could actually
   reach. **Fixed:** the protocol, the deviation log, the joint-best record and the new generator are now on the
   `mobiwac` branch, and the `README.md` line is corrected.

2. **Hard evidence that region superiority is post-hoc, stronger than the argument from silence.**
   `scripts/closing_data/superiority_wilcoxon.py`, which names FL/CA/TX as "the beats", was first committed
   `1e3449e6` on **2026-06-25**. The FL and CA dedicated region ceilings landed **2026-06-22** and TX **2026-06-24**.
   The dataset selection was therefore made after those cells were readable. The same unregistered assertion also
   appears in `m1_stats_n20.py:333` (reaching the committed output at
   `m1_full_output.txt:83,91`) and in `stats_n20/RESULTS.md` §1b, which treats the script as the registration authority.

3. **The reason recorded for the deviation is the power floor, not conservatism.** `RESULTS.md` entry #2 records that at
   n=4 the exact one-sided Wilcoxon cannot fall below 0.0625 for any effect size. The pseudo-replication argument (five
   folds are one fixed partition shared across seeds) is a defensible post-hoc justification and is worth making in a
   response letter, but it is not what the artifact records, and the chapters do not attribute it to the plan.

**REV-007's premise is now obsolete: the pre-registered test has been run, at full n=20, on all six datasets.** The
blocker was Istanbul's dedicated category ceiling, committed only as four per-seed scalars
(`h3_istanbul/step3_runs/cat_ceil_s*.txt`) with the per-fold arrays in gitignored A40 rundirs (`RESULTS.md` LIMITS #2).
Those four sidecars were **recovered from the A40 on 2026-07-25**; their per-seed means reproduce the committed scalars
exactly (54.7063 / 54.8632 / 54.7705 / 54.6101, tags
`h3ist_cat_s{0,1,7,100}`), so no retraining was needed. They are committed at
`h3_istanbul/step3_runs/cat_ceiling_perfold/`, and **LIMITS #2 is closed.**

The registered test, at its registered footing (per-fold n=20 paired one-sided Wilcoxon, protocol §2; Holm m=6 within
the six-dataset next-category set, protocol §5.2), on the joint-best arrays:

| Dataset  | Δcat (pp) | folds positive | exact one-sided p | Holm-adj (m=6) |
|----------|----------:|----------------|------------------:|---------------:|
| AL       |    +7.690 | 20/20          |          9.54e-07 |       5.72e-06 |
| AZ       |    +9.350 | 20/20          |          9.54e-07 |       5.72e-06 |
| FL       |    +5.332 | 20/20          |          9.54e-07 |       5.72e-06 |
| CA       |    +6.442 | 20/20          |          9.54e-07 |       5.72e-06 |
| TX       |    +7.446 | 20/20          |          9.54e-07 |       5.72e-06 |
| Istanbul |    +8.584 | 20/20          |          9.54e-07 |       5.72e-06 |

All six reject at α = 0.05; 9.54e-07 is the exact n=20 floor (1/2^20) and every cell sits at it. The four next-region
superiority cells reject in their own m=4 family (Holm-adjusted 3.81e-06 each, 20/20 folds). **No verdict changed, and
no reported estimate or interval changed.** Generator, with a 24/24 artifact-to-board reproduction gate:
`stats_n20/m2_prereg_perfold.py`; output `m2_prereg_output.txt`.

**Answers to the three "needs from you" items.**

1. **Ch.2 reconciled to Ch.5 (done).** `2_fundamentals.tex` no longer says the Wilcoxon alone licenses
   "outperforms". It now states that the exact one-sided p has a floor set by the number of pairs, that a superiority
   claim on four repetitions is reported with a paired t on the per-repetition means with the Wilcoxon alongside it on
   the individual folds, and that either test licenses the verb.
2. **Deviation clause added to Ch.5 (done).** §5.3's analysis-plan sentence now says what the plan actually fixed (per
   task, not per dataset), discloses the Wilcoxon-to-t departure with the 0.0625 reason in one clause, and states that
   the registered test is reported alongside.
3. **Region superiority labeled (done).** Ch.5 calls the four next-region gains "secondary results outside"
   the plan, and the Holm sentence now names both families explicitly instead of "across the comparisons", which had
   implied a coverage the analysis did not have.

**Proportionality.** The audit agrees with the Claude take that "one immutable manifest, regenerate everything" is
heavier than the defect: the parity gates already prove artifact-to-table fidelity (18/18, 90/90, 6/6) and
`m2_prereg_perfold.py` adds 24/24 on the joint-best arrays. A one-page `ANALYSIS_MANIFEST.md`
naming inputs, tests, families and deviations still satisfies the substance and is the remaining work item.

**Still open (2 items).**

- **No single manifest, and one generator is missing from the tree.** The §8 entry of 2026-07-18 prints the exact CIs
  the chapters carry, and all of them reproduce from the committed arrays, so the values are sound. But no committed
  script emits that entry: `m1_stats_n20.py` reads the diag-best sources and
  `score_joint_best.py` only scores cells. The generator of the joint-best statistics run is not in the tree.
  `m2_prereg_perfold.py` now covers the registered per-fold family; the seed-level joint-best generator and the one-page
  manifest are what remain.
- **Docstring corrections.** `superiority_wilcoxon.py` and `m1_stats_n20.py` still assert a registration the protocol
  does not contain, and `stats_n20/RESULTS.md` §1b repeats it. These are repository hygiene, claim-neutral, and were
  left for a separate pass rather than edited inside a results record.

### REV-008 — A4 audit is narrower than the “no usable information” claim 🔧

- **Severity:** Major
- **Status:** Open
- **Classification:** Confirmed claim overreach
- **File:** `src/chapters/5_mobiwac.tex`
- **Section:** Representation leakage audit
- **Reported by:** Reviewers 07, 09, and 11

**Finding**

The text says the representation passes “no usable information” about category. A4 evaluates a POI-level proxy on three
states and only for in-coverage POIs. It does not test contextual per-visit information, the future-edge path in
REV-001, out-of-coverage behavior, or every dataset.

**Why it matters**

A passed audit only excludes the leakage mechanisms it can observe. The absolute conclusion creates false assurance.

**Recommended action**

Describe A4 precisely: datasets, coverage, proxy target, randomization, and mechanisms tested. Replace the universal
claim with a scoped statement and add direct causal/future-edge tests.

**Author response**

> Ok let's go with the claude takes, as I said before if necessary we can also make changes in the mobiwac and improve
> it (in orignal text and here). About the A4 audit, beside has been done in only e datasets in one seed this is
> somthing
> that we can extrapolated for other state no ? Investigates it more and use the nespedgpu if needed.


**Claude take (2026-07-24) — PARTLY CONFIRMED. The reviewer's specific sub-claims are wrong; the topic sentence is the
real problem.**

The reviewer says the text does not state datasets, coverage, or proxy scope. It does, in the same sentence:
`5_mobiwac.tex:343` reports "region $-0.33$ to $+0.01$; category $0.00$ to $+0.29$, **at Alabama, Arizona, and Florida**
", then "This measurement covers the visits whose places appear in training (**67 to 87 percent**); visits to places
unseen in training are the one part it cannot reach." That is a more honest scoping than the review credits.

What is genuinely wrong is narrower and sharper: the **topic sentence** — "We verify that it passes **no usable
information** about the test visits" — is an absolute that the three grounds beneath it do not cover. Specifically:

- Ground one ("its training objective is label-free … never sees a next-category or next-region target") is true of the
  *objective* and says nothing about the *inputs*. Two sentences earlier the chapter states that each visit's category
  is a node input feature (`:235`). The juxtaposition is what makes it read as more than it claims.
- Ground two (A4) measures **transductivity** — whole-dataset versus train-users-only — not the temporal/forward-edge
  channel of REV-001. Different leak, different axis.
- Coverage is 3 of 6 datasets at seed 0.

**Fix, and it is small:** replace the absolute with a scoped statement ("we bound two specific channels"), name what
each ground does and does not cover, and — the high-value addition — cite the forward-edge leak-sniff audit
(`RESCREEN.md`, `leak_sniff.py`) as a fourth ground. You currently have that evidence and do not show it. See REV-001.

**Resolution notes**

> _Record the revised audit scope and any new tests here._

### REV-009 — CoUrb does not isolate semantics from capacity 🔧

- **Severity:** Major
- **Status:** Open
- **Classification:** Confirmed design limitation and claim overreach
- **File:** `src/chapters/4_courb.tex`
- **Section:** Representation comparison
- **Reported by:** Reviewers 07, 09, 10, 11, and 12

**Finding**

The comparison changes all representation components and increases dimensionality from 64 to 192. The chapter
acknowledges the missing dimension-matched control but still says the design “isolates” representation quality.

**Why it matters**

The intervention changes information content, dimension, and downstream projection parameter count. It identifies the
effect of a representation package under a fixed downstream topology, not semantic quality alone.

**Recommended action**

Replace “isolates” with the narrower estimand. Add dimension-matched, parameter-matched, and component ablations if a
causal semantics claim is required.

**Author response**

> We need to take care with this, but I belive that the claude takes is the way, we don't change nothign of the courb
> text and change in the claims made in the ch.1 and ch.6.


**Claude take (2026-07-24) — correct as physics, but Chapter 4 already concedes it verbatim, and the concession is the
published authors' own. The gap is in the frame chapters.**

`4_courb.tex:213-215` states the confound and the missing control unprompted: "the difference in input dimensionality
may influence part of the observed gains. For this reason, an additional experimental control equalizing the
dimensionality of the representations would allow validating more precisely whether the gains occur mainly from the
semantic specialization of the encoders, and not only from the increase in input dimensionality." I confirmed this is
**verbatim from the published paper** (`articles/CoUrb_2026/src_en/sections/metodology.tex:147,149`, and the PT original
at the same lines) — not something the dissertation added. `:144` and `:219` ("isolating the effect of the
representation strategy") are likewise verbatim. Only the preface sentence at `:13` is new, and it is the sanctioned
NORTH_STAR floor sentence recorded in the ledger.

So: do **not** touch Ch.4. Softening published text here would break reproduction fidelity for no evidentiary gain.

**The real gap is Chapters 1 and 6, which present CoUrb as a clean controlled test with no capacity caveat.**
`6_conclusion.tex:36-43`: "Holding the MTLnet architecture fixed and replacing only the input … **A change of input,
with no change of architecture, moved the needle farther than any architectural variation tried before it.**" Literally
true (architecture is fixed) but it is the sentence most exposed at a defense, because the input width tripled from 64
to 192. Grepping the two frame chapters for `dimension|192|capacity` returns only the "64-dimensional" descriptor — the
64→192 asymmetry never reaches the reader.

**Fix:** one clause in `6_conclusion.tex:40-42` noting the decomposed input is also three times wider and that the
equal-dimension control is future work, pointing at `4_courb.tex:215` which already says so.

**Resolution notes**

> _Record the revised estimand and any controls here._

### REV-010 — Chapter 3 reverses or conflates the two tasks 🔧

- **Severity:** Major
- **Status:** Open
- **Classification:** Confirmed error
- **File:** `src/chapters/3_cbic.tex`
- **Section:** Preface, problem definition, and tasks
- **Reported by:** Reviewers 01, 02, 04, 11, and 15

**Finding**

The preface defines Next-POI as next-category prediction; the body describes it as predicting a specific location;
another passage swaps the task labels. The chapter alternates among POI, category, and location.

**Why it matters**

The reader cannot determine the target variable, label space, or whether later claims compare the same task. This also
compounds REV-002.

**Recommended action**

Create a task-definition table with input, target, label cardinality, and metric, then mechanically reconcile every use
of “Next-POI,” “category,” and “location.” Preserve the historical article only where reproduction fidelity requires it,
and annotate errors in the preface.

**Author response**

> I agree in not create the task table. For me the best apporach and easy one is create a errata for the phrase in the
> courb paper, so we don't need to change it. what do you think ?

**Claude take (2026-07-24) — ONE substantive contradiction, not three, and it is 80 percent already mitigated by a
preface the reviewer appears to have mistaken for the defect.**

Full inventory of `3_cbic.tex` task naming shows the preface at `:27-31` is the **fix**, added deliberately (commit
`46d84462`, "next-POI terminology bridge added to Ch.3 + Ch.4 prefaces"): "the term ``Next-POI Prediction'' as used in
the reproduced article denotes the frame's *next category* task … the dissertation reserves *next place* for the
exact-POI task, which is not studied here." It implements the `GLOSSARY.md` §1 mapping exactly. `4_courb.tex:13` carries
the identical bridge.

**The one real contradiction is `3_cbic.tex:72`** — "Next-POI Prediction, in contrast, aims to predict which **specific
location** a user is likely to visit next" — verbatim from `articles/CBIC___MTL/sections/basis.tex:23`. In fairness it
sits in the *related-work* subsection defining the two research areas as the literature uses them, and the paper's own
instantiation is stated correctly at `:46`, `:157`, `:166`, `:170`. It is a conflation of the generic literature name
with the paper's own task, not a self-contradiction about what was run — but it is still the sentence most likely to
trip a reader.

The other two are harmless verb swaps, both verbatim published (`:117` ≡ `basis.tex:77`; `:347` ≡ `results.tex:40`) —
they exchange "prediction"/"classification" between tasks while keeping the referents unambiguous. Neither reverses
which task is which.

**Fix:** one qualifying clause at `:72` ("in the general formulation of the literature; the task studied here is the
category variant defined in Section 3.1"), or a footnote pointing back to the preface. Errata row in
`apx_b_errata.tex` + `articles/CBIC___MTL/ERRATA.md`. Not a chapter-level rework, and the task-definition table the
reviewer asks for already exists in `GLOSSARY.md`.

**Resolution notes**

> _Record the corrected terminology map here._

## 4. Chapter-by-Chapter Review

### Chapter 1 — Introduction

The motivation, research gap, objectives, and null → diagnosis → correction storyline are clear and persuasive. Preserve
the compact contribution arc. Required revisions are to narrow the research-question answers in anticipation of REV-004,
distinguish four seeds from 20 fold-level measurements (REV-014), and avoid describing a single protocol as universal
(REV-006).

### Chapter 2 — Fundamentals

The chapter effectively connects MTL, POI representation, leakage, and evaluation rather than acting as a generic
survey. Its cross-study protocol synthesis is useful but presently anachronistic: it projects the Chapter 5 standard
backward onto earlier studies. The claims about Wilcoxon licensing “outperforms” need alignment with the actual
analysis. The HGI description and several citations need correction (REV-016 and REV-017). A compact evidence matrix
would improve it more than additional literature.

### Chapter 3 — CBIC article

This is the least submission-ready chapter. It contains task-definition contradictions, target leakage, invalid Nash
interpretation, unsupported “significant” language, and several broken or difficult sentences. Examples include the
incomplete construction near line 113, the feature/formula explanation near line 133, and the nearly unintelligible
results sentence near line 307. Because this is a published time capsule, use a preface erratum plus a carefully
governed correction strategy rather than silently rewriting scientific history.

### Chapter 4 — CoUrb article

The English body is broadly faithful to the Portuguese source, and the numerical errata and figures are consistent. The
principal scientific problem is that the target category is built into the representation, followed by the
dimension/capacity confound and sample-stratified user overlap. Statistical language should remain descriptive because
no inferential test is reported. Several translated collocations need professional editing. Clarify that the chapter
reproduces the article body, not necessarily its abstract and acknowledgments, and update the adaptation ledger for
added analytical lead/caption text.

### Chapter 5 — MobiWac article

This is the strongest-written and most carefully audited empirical chapter, but its central result is currently blocked
by REV-001 and REV-003. The negative-result reporting, transition-prior leakage history, coverage-aware baselines,
external-baseline caveats, and cascade qualification are excellent and should remain. The balancer summary must
distinguish invalid/misconfigured screens from valid negative results, and the A4 claim must be scoped.

### Chapter 6 — Conclusion

The synthesis is strong but currently outruns the evidence. It says the joint model outperforms both dedicated models
even though region is superior in only four datasets and non-inferior in two. Representation “dominance” is too causal
given REV-002 and REV-009. The capacity-matched control is useful but narrower and less complete than the conclusion
implies. Rewrite this chapter only after the critical reruns determine which claims survive.

### Appendices and front matter

Appendix A incorrectly says three articles are published while MobiWac is under review. Appendix C claims every passage
has received human approval while the same repository contains unresolved `[NEEDS SIGN-OFF]` markers. The front matter
lacks a final cover/approval sheet in the defense build and retains placeholders. These are substantive
submission-readiness issues, not cosmetic cleanup.

## 5. Methodology and Experimental Validation

### REV-011 — Balancer screen is summarized more strongly than the valid evidence permits 🔧

- **Severity:** Major
- **Status:** Open
- **Classification:** Confirmed claim overreach
- **File:** `src/chapters/5_mobiwac.tex`; `docs/results/mtl_improvement/T4_audit_and_verdict.md`
- **Section:** Dynamic task balancing
- **Reported by:** Reviewers 07 and 10

**Finding**

Chapter 5 says none of PCGrad, Nash-MTL, and the other balancers improved the result. The audit records that only
GradNorm was retuned; Nash used defaults; PCGrad, CAGrad, and Aligned were invalid; and DWA/FairGrad were misconfigured.

**Why it matters**

An invalid or misconfigured run is not evidence that an algorithm fails.

**Recommended action**

State only that no **valid screened configuration** Pareto-dominated the tuned fixed-weight baseline. List invalid and
inconclusive methods separately.

**Author response**

> I belive that the best apporach is to use the "at their default configurations", so we can change this in the original
> text and in here.

**Claude take (2026-07-24) — PARTLY CONFIRMED. The chapter's hedges are already close to what the audit prescribes; one
two-word parenthetical is the whole defect.**

The current text (`5_mobiwac.tex:182-194`) does **not** say "none improved" in the blanket sense: "none of the balancers
**that we tried**, including the two named above, improved on a tuned fixed task weighting in our model" … "this is **a
finding for this pair of tasks, not a general rule**." That is already the convergent-evidence-negative framing the
audit banner asks for (`T4_audit_and_verdict.md:8-17`).

The real defect is narrower: **PCGrad is named**, and PCGrad is exactly one of the three gradient-surgery methods the
audit says "**don't count** as balancer tests" — under the dual tower the private reg tower trains at unit weight
regardless, so as wired they collapse to `equal_weight` (`T4:26-31`). Nash-MTL, the other named method, **was**
correctly wired (`T4:37-39`), so half the named evidence is sound.

Secondary, unstated: the screen is seed 0, two states (AL+FL). Though the claim sits in Related Work as a confirmation
of published literature, not as a headline result, which limits the exposure.

I also verified the supporting number: the +0.001 cosine similarity is `T4:47-49`'s pooled +0.0008 over 16 champion runs
(4 states × 4 seeds), and the chapter's "four seeds each on three of our six datasets" is an accurate and correctly
scoped restatement.

**Fix:** drop "including the two named above" (keeping Nash-MTL only), or append "at their default configurations". One
clause; version-of-record, so an errata row. "Summarized more strongly than evidence permits" overstates it.

**Resolution notes**

> _Record corrected scope or rerun results here._

### REV-012 — Chapters 3 and 4 lack reproducible selection details ⚠️

- **Severity:** Major
- **Status:** Open
- **Classification:** Confirmed omission
- **File:** `src/chapters/3_cbic.tex`; `src/chapters/4_courb.tex`
- **Section:** Experimental setup
- **Reported by:** Reviewers 06, 09, 10, 11, and 12

**Finding**

Chapter 3 omits the split axis, seed policy, tuning budget, checkpoint convention, and environment. Chapter 4 gives the
fold scheme but not the seed, selection/tuning policy, or software/hardware versions.

**Why it matters**

The studies cannot be independently reproduced or compared fairly, and hidden selection choices cannot be evaluated.

**Recommended action**

Recover these details from code/logs where possible. Otherwise state that they are unavailable in the historical
artifact. Add a study-level reproducibility table rather than implying uniform retrospective compliance.

**Author response**

> I agree witht eh claude takem, and am more lean to add this point as a errata. Also the reproduction can be achived by
> going back in the code base
> commits, and the codebase link is in all articles what make the point of the review even weaker.

**Claude take (2026-07-24) — CONFIRMED, but more is recoverable than "genuinely lost", and one recovery is already
done.**

Item by item: **split axis** absent in Ch.3 (`:261` says only "5-fold cross-validation methodology"), present in Ch.4
(`:226`). **Seed policy** absent in both (no occurrence of "seed" or "random state" in either file). **Tuning budget**
absent in both — Ch.4 says only "All models share the same hyperparameters" (`:219`) with no values. **Checkpoint
convention** absent in both; Ch.3's target-F1 thresholds at `:347` are a stopping criterion for the convergence
experiment only, not a selection rule for the reported tables. **Environment** present in Ch.3 (`:366` footnote: Apple
M2 Pro, macOS 15.5, Python 3.9.6, PyTorch 2.6.0.dev, CVXPY 1.5.2), absent in Ch.4.

Neither `articles/CBIC___MTL/` nor `articles/CoUrb_2026/` contains any run log, fold manifest, config, or results JSON —
both are LaTeX-only packages.

**But Chapter 4's missing facts are already recovered.** The author-provided CoUrb codebase copy pins them:
`.../PoiMtlNet_Novo/src/etl/mtl/create_fold.py:162` sets `random_state: int = 42`, applied at `:180-181` to
`torch.manual_seed`/`np.random.seed` and to both splitters at `:226,229`. So Ch.4 is **single seed 42, 5 folds,
sample-stratified** — fully recoverable and worth stating, since "one seed" is exactly what a banca will want to know
when comparing against Ch.5's four.

Genuinely lost: per-fold run logs, per-run configs, and the tuning history for both chapters. And note the tuning budget
for Ch.3 is doubly compromised — even if the logs existed, REV-005 shows the optimizer comparison they record was
measured against a degraded solver. One incidental catch: the Ch.3 environment footnote pins `CVXPY 1.5.2` with no
`ecos`, so it inadvertently documents the broken configuration.

**Needs from you:** whether to add the recoverable facts as declared additions in Appendix B, or put one reproducibility
note in the frame. Precedent favours the first and it already exists — `apx_b_errata.tex:169-173` records Ch.4's
split-axis sentence as exactly this kind of added protocol clarification. A banca will not demand run logs for a
conference paper; it will notice a dissertation that reports five-fold CV with no seed while Chapter 2 lectures on
protocol rigor.

**Resolution notes**

> _Record recovered details and irrecoverable gaps here._

### REV-013 — Capacity-matched control is useful but incomplete and overstated ⚠️

- **Severity:** Major
- **Status:** Open
- **Classification:** Confirmed scope problem
- **File:** `src/chapters/6_conclusion.tex`; `storyline/audit/capacity_baseline_experiment.md`
- **Section:** Capacity-matched follow-up
- **Reported by:** Reviewers 06, 07, 09, 10, and 12

**Finding**

The control covers three Alabama recipes at n=20, while one California arm is only 15/20. The raw
`al_capmatch_summary.json` artifact named in the narrative is not committed. The rendered conclusion now uses the 64.51
joint-best value, but the experiment record still compares against the 64.54 diagnostic-best convention. “Closes the
parameter explanation” and “yields nothing” remain stronger than the tested architecture and datasets support.

**Why it matters**

The negative control is evidence against a simple parameter-count explanation in the tested setting, not proof that
capacity never matters.

**Recommended action**

Commit or regenerate the raw summary, complete or explicitly label the partial arm, report spreads and model-selection
conventions, and narrow the conclusion to the tested architecture/datasets.

**Author response**

> I agree with the claude take. We can do all their suggestions, aslo about the execution of the california it's
> alreadyed over in the nespegpu, how was in charge of it was the session
> `#Dissertation Storytelling Review: CBIC→CoUrb→MobiWac`

**Claude take (2026-07-24) — every factual sub-claim CONFIRMED, and the reviewer missed the serious one.**

Verified: three Alabama arms at n=20 (`capacity_baseline_experiment.md:100-109`, best 56.16 ±1.88); California
explicitly partial at seeds {0,1,7} = 15/20, job `4cff4b00`, 68.35 ±0.53 (`:127-137`); the 64.51/64.54 convention
question live and already self-flagged as `[NEEDS SIGN-OFF]` at `6_conclusion.tex:79-84`.

**The finding the reviewer did not raise — and the one I would act on first.** `find` over the entire repository,
including hidden directories, returns **nothing** for `*capmatch*` or `*d38a1382*`. The AL n=20 numbers printed at
`6_conclusion.tex:78` trace only to prose in `storyline/audit/capacity_baseline_experiment.md`, which itself refers to a
session artifact that was never committed. Under your own number protocol (`AGENT_GUARDRAILS` N1 "single source of
truth", N3 "every numeral is traceable to its source file") this is a **fact-gate failure**, and it is the only
load-bearing number in Chapter 6 with no committed source. Either commit the JSONs from the A40 work directory or
regenerate them. See NEW-1.

**On the overreach.** "Parameter count alone … **yields nothing here**" (`:86`) is well-scoped — "here", plus the
correct causal attribution, and it matches the source verdict in force ("recovers none of the joint gain"). The phrase
that actually outruns the evidence is `6_conclusion.tex:132`: "**the capacity-matched baseline above closes the
parameter-count explanation**", stated unqualified inside a limitations list, when the experiment covers the category
task only, 2 of 6 datasets, one width point per dataset, width-scaling not depth, with CA still at n=15/20 on one arm.
The source itself says only that it "closes the last cheap alternative explanation".

Also unstated: the source's own instruction at `:122-125` — the dedicated ceiling was tuned best-vs-best over a wider
recipe grid while the wide arm got a 3-recipe sweep, and "**state this scope whenever the number is quoted**". The
chapter states the sweep but not the asymmetry.

**Needs from you:** commit or regenerate the AL artifacts; confirm 64.51 vs 64.54 (already queued); scope `:132`. Note
that suppression is not on the table — `capacity_baseline_experiment.md:47-54` records that the experiment's outcome
binds the §3.4 concession once run. Only prominence is your call.

**Resolution notes**

**Claude take, round 2 (2026-07-24) — the two mechanical halves are CLOSED; one claim is now *more* overstated than when
the reviewer wrote this, and the completed run refutes a sentence the chapter currently prints.**

*What changed.* The California sweep finished on the A40 (job `4cff4b00`, exit 0, 8/8 cells). All raw results —
California **and** the previously-uncommitted Alabama set recovered from the A40 work directories — are now committed at
`docs/results/closing_data/capacity_matched_stl_cat/` (23 files, commit `58232dd2`), with a README carrying the
protocol, the parameter audit, the reference points, and the scope. **No text was changed** in that commit.

| Dataset    | matched width                 | best arm        | n  | value           | own narrow optimum | joint (diag-best) |
|------------|-------------------------------|-----------------|----|-----------------|--------------------|-------------------|
| Alabama    | h=672 (~4.21M vs joint 4.20M) | bs2048 @ 0.0025 | 20 | **56.16 ±1.89** | 56.82 ±0.03        | 64.54             |
| California | h=752 (~5.25M vs joint 5.15M) | bs8192 @ 0.0025 | 20 | **69.88 ±0.26** | 70.60 ±0.07        | 77.05             |

*Sub-claims 1 and 2 (incompleteness, uncommitted artifact) — CLOSED.* Both datasets are at n=20 per arm; the fact-gate
failure (NEW-1) is resolved by committed raw JSONs plus a summary recomputed from those committed copies, not from
session memory.

*Sub-claim 3 (convention mismatch) — still the author's, unchanged.* The record now states both bases explicitly and the
README repeats the N5 prohibition: the verdict is identical at 64.51 and 64.54, but the two must never be mixed inside
one comparison.

**The new finding: the completed run refutes the chapter's California sentence.** `:86` currently reads "A partial
California run, fifteen of twenty repetitions at the time of writing, shows the same direction." That was written from
the *first arm only* (bs8192@0.005, seeds {0,1,7} = 68.35), and I characterized it in the experiment record as "the same
direction, **larger magnitude**". The second arm refutes the magnitude half: California's best arm is 69.88, a shortfall
of **−0.72**
against its own ceiling, essentially identical to Alabama's **−0.66**. The direction never changed; the size claim did.
The sentence must be replaced by the completed figure, and the interim
"larger magnitude" phrasing must not survive anywhere. I have recorded the correction in the committed README rather
than silently dropping it (`AGENT_GUARDRAILS` §7, silent correction).

**On the overstatement, sharpened.** I stand by the round-1 reading that `:86` ("yields nothing **here**") is adequately
scoped and `:132` ("the capacity-matched baseline above **closes** the parameter-count explanation") is not — and the
completed run does **not** license upgrading it. Two datasets instead of one-and-a-half is still two of six, category
only, one width point each, width scaling rather than depth. The defensible form is the source's own: it closes the
*cheap*
parameter-count explanation *in the tested setting*. Recommended edit at `:132`, verdict-neutral:
"…and the capacity-matched baseline above rules out a simple parameter-count explanation for the category task at the
two datasets tested, but the homogeneity of the final pair remains…".

**One point in the experiment's favour that the chapter does not currently claim, and could.** At *both* datasets the
widened arm's optimum sits at a **lower learning rate** than the narrow ceiling's winning recipe (0.0025 vs 0.005 at
each). So the sweep did not merely re-run the ceiling recipe at a larger width and let it underperform for want of
tuning: it found the wide model's own better setting, and the verdict holds *there*. That is a real strengthening of the
fairness argument and it is now in the README. It does **not** erase the asymmetry the source flagged (the ceiling was
tuned best-vs-best over a wider grid than these 3-recipe/2-recipe sweeps), which must still travel with the number.

**Needs from you (revised).** (a) Replace the partial-California sentence at `:86` with the completed figure — this is
now a factual correction, not a refresh. (b) Scope `:132` as above. (c) Confirm 64.51 vs 64.54 (already queued at
`:79-84`). (d) Optional: adopt the lower-learning-rate fairness point. Prominence of the paragraph remains your call;
suppression is not on the table (`capacity_baseline_experiment.md:47-54`). Sources for every number above:
`docs/results/closing_data/capacity_matched_stl_cat/README.md` and
`capacity_matched_summary.json`.

## 6. Results, Statistics, and Claim Verification

### REV-014 — “20 repetitions” misstates the inferential unit 🔧

- **Severity:** Major
- **Status:** Open
- **Classification:** Confirmed error
- **File:** `src/0_main.tex`; `src/chapters/1_introduction.tex`; `src/chapters/5_mobiwac.tex`;
  `src/chapters/6_conclusion.tex`
- **Section:** Abstract, protocol, results, and conclusion
- **Reported by:** Reviewers 04, 06, 07, and 09

**Finding**

The experiment uses four seed repetitions across five fixed folds, producing 20 fitted fold measurements. The
inferential analysis aggregates to four seed means. The dissertation repeatedly calls this “20 repetitions.”

**Why it matters**

Twenty folds are not 20 independent repeated experiments. The n=4 analysis captures initialization variability
conditional on one fixed fold partition, not uncertainty over resampled user splits.

**Recommended action**

Use “four seeds × five fixed folds (20 fits)” everywhere and name the inferential unit explicitly. Describe the
resulting uncertainty limitation.

**Author response**

> I am lean to stay as it is in the text, and create in the appendix an errata acknowledging that this is not the
> perfect
> world, and explain the problem. But the number of execution give us a security over the results. what do you think?
>

**Claude take (2026-07-24) — CONFIRMED. Six sentence edits, all in chapters you own outright, zero effect on any
number.**

Design is 4 seeds × 5 **fixed** folds = 20 fitted models; the executed analysis pairs the four per-seed fold means,
`t(3)`, so **inferential n = 4** (`stats_n20/RESULTS.md:65-67,72-77`). All four seeds reuse the same frozen fold
partition (`STATISTICAL_PROTOCOL.md:187-190`), so the interval captures initialization variance conditional on one
user-split, not resampling uncertainty over splits — exactly the reviewer's point.

**Chapter 5 is already correct and needs nothing** (`:355`, `:499-500`, `:554-555`, `:605` all say "four seeds × five
folds", "$n{=}4$"). The defect is confined to the frame:

| Location                 | Current                                                                          | Corrected                                                                                                                   |
|--------------------------|----------------------------------------------------------------------------------|-----------------------------------------------------------------------------------------------------------------------------|
| `0_main.tex:276-277`     | "twenty repetitions per configuration (four random initializations, five folds)" | "four random initializations over five fixed folds (20 fitted models), the tests pairing the four per-initialization means" |
| `1_introduction.tex:243` | "twenty repetitions per configuration (four seeds, five folds)"                  | "four seeds over five fixed folds (20 fitted models; inferential n = 4 seed means)"                                         |
| `6_conclusion.tex:49`    | "twenty repetitions per configuration" (no decomposition at all — worst case)    | "four seeds over five fixed folds (20 fitted models)"                                                                       |
| `6_conclusion.tex:77`    | "the full twenty repetitions"                                                    | "the full four seeds × five folds"                                                                                          |
| `6_conclusion.tex:85`    | "fifteen of twenty repetitions"                                                  | "three of the four seeds (15 of 20 fits)"                                                                                   |
| `GLOSSARY.md:76`         | "the n=20 paired repetitions"                                                    | "n = 4 paired per-seed means (20 fits)"                                                                                     |

Note the last one: `GLOSSARY.md` **contradicts itself** — `:63` defines a seed as "one complete repetition of the
five-fold experiment", under which there are four repetitions, not twenty. Since the glossary is fail-closed law for the
whole document, fix it first.

Optional and worth one clause: state that all seeds share one frozen fold partition, so the interval does not cover
uncertainty over resampled user splits.

**Resolution notes**

> _Record corrected wording and any repeated-split analysis here._

### REV-015 — Conclusion and external-baseline language exceeds the measured result ✅

- **Severity:** Major
- **Status:** Open
- **Classification:** Confirmed claim overreach
- **File:** `src/chapters/5_mobiwac.tex`; `src/chapters/6_conclusion.tex`
- **Section:** Main claims and baseline comparison
- **Reported by:** Reviewers 01, 07, 09, 11, 12, and 17

**Finding**

The conclusion says the joint model outperforms both dedicated models, but region is superior in four of six datasets
and non-inferior in two. Claims of being above every external baseline mix partial STAN folds, a ReHDM result under its
own protocol/single seed, and high-coverage HMT subsets.

**Why it matters**

The strongest defensible claim is task- and dataset-specific. Cross-protocol point estimates are contextual, not
confirmatory head-to-head evidence.

**Recommended action**

Report category superiority separately from region superiority/non-inferiority. Treat dedicated baselines under the
common protocol as primary; label external comparisons descriptive and coverage/protocol-dependent.

**Author response**

> **Repository answer (24 July 2026):** The dedicated single-task models evaluated
> under the same representation, windows, folds, and training protocol are the primary
> comparator. External methods are contextual references with explicit protocol or
> coverage qualifications. The final region claim in Chapter 5 is superiority at
> Istanbul, Florida, Texas, and California, and non-inferiority within ±2 Acc@10 points
> at Alabama and Arizona. Category superiority is reported at all six datasets.

**Claude take (2026-07-24) — REFUTED on the premise. The 4-of-6 split is reported in four separate places and the
external-baseline arithmetic checks out.**

The dissertation never claims blanket region superiority. `5_mobiwac.tex:26-30` (preface), `:66-69` (contribution 2),
`:631-633` (chapter conclusion) and `6_conclusion.tex:49-53` all state it explicitly, e.g.: "on the category task at all
six datasets, by 5.3 to 9.4 macro-F1 points, and on the region task **at four of six, Istanbul, Florida, California, and
Texas, while remaining statistically non-inferior within a two-point margin (TOST) at Alabama and Arizona**." The
never-upgrade-AZ discipline from the claim whitelist is visibly honoured at `:547-569` ("At Arizona, the interval is
centered on zero, **so we report a match, not a gain**").

External-baseline bounds verified against Table 3: tightest region margin AL 69.70 − ReHDM 65.38 = +4.32 ("at least 4"
✓); tightest category margin Istanbul 63.32 − POI-RGNN 30.12 = +33.20 ("at least 33" ✓). The caveats the reviewer asks
for are already present — the representation-advantage disclaimer at `:580-584`, the protocol disclaimer inside the
conclusion sentence itself, and the footnote markers for STAN partial folds (TX 4/5, CA 2/5) and ReHDM single seed.
`5_mobiwac.tex:359` also states outright that the HMT-GRN comparand is "not a reproduction of the complete published
system", and `:589-596` frames the cascade as "a defense of the parallel design, not a claim that we outperform the
cascade". Chapter 6 makes no external-baseline claim at all.

**Two optional polish items, neither blocking:** `6_conclusion.tex:19` is the single unqualified instance ("one joint
model finally outperforms both dedicated models"), though it is a chapter-opening summary and `:63-66` restates it
correctly 45 lines later; and the Ch.5 conclusion's "at least 4 Acc@10" bound is computed partly against partial-fold
and single-seed comparands whose markers live only in the table footnote.

**Resolution notes**

> _Record the revised headline and baseline hierarchy here._

### REV-016 — Corpus counts and date ranges need a provenance decision 🔧

- **Severity:** Major
- **Status:** Open
- **Classification:** Source-of-truth conflict
- **File:** `src/chapters/3_cbic.tex`; `src/chapters/4_courb.tex`; `src/chapters/5_mobiwac.tex`;
  `src/chapters/6_conclusion.tex`; `NORTH_STAR.md`
- **Section:** Dataset descriptions
- **Reported by:** Reviewers 04 and 06

**Finding**

Chapters 3/4 report Florida as 990,518 check-ins, 20,301 users, and 65,009 POIs; Chapter 5 reports 1,407,034, 21,052
users, and 76,544 POIs. Date ranges also differ. The 24 July author ruling now resolves which figures belong to each
study, but the reader-facing dissertation does not explain that Chapters 3/4 and Chapter 5 use distinct source
snapshots/ETL chains, and stale governance text remains elsewhere.

**Why it matters**

Different corpora or ETL snapshots are legitimate, but unexplained differences look like contradictions. The repository
now identifies the chains, but the dissertation reader does not see that provenance.

**Recommended action**

For every corpus, state raw source, acquisition window, snapshot/hash, preprocessing stage, and post-filter counts.
Synchronize or deprecate stale governance files after author confirmation.

**Author response**

> I agree with the claude take, and let's add a phrase explaining in the appendix B.

**Claude take (2026-07-24) — the *decision* is already made and applied; what remains is documentation debt plus one
inaccurate sentence.**

The counts are as reported: Ch.3 `:246` and Ch.4 `:238` give Florida 990,518 / 65,009 / 20,301; Ch.5 `:324` gives
1,407,034 / 21,052 / 76,544. The author ruling of 24 July (`src_utils/evidence/cbic_recompute_result.md:1-10`,
`DECISOES_PENDENTES_ptBR.md:59-60`) is recorded and applied, and the `[VERIFY]` on the dataset numbers is closed
(`3_cbic.tex:255` is a cleared marker inside a comment; the only open `[VERIFY]` in the LaTeX is `main.tex:32`, an
unrelated pagination parameter).

The mechanism is also documented: `cbic_recompute_result.md` §3 attributes the gap to **category-mapping drift** — the
mapping files were last modified 2026-04-14, ~11 months after the CBIC-era extraction, and stage_1 drops unmapped rows,
so the expanded mapping keeps ~418k more check-ins.

**Four residuals, all mechanical:**

1. **The reader is never told.** The only rendered reconciliation is `apx_b_errata.tex:76-82`, which reconciles Ch.3 to
   Ch.4 and says nothing about Ch.5 — the divergence a reader actually sees. Your own fact gate already flagged this
   (`_specialists_v1/FACT_GATE_v1_corrected.md:112`: "there is no reconciling note in rendered prose … An examiner may
   ask").
2. **`apx_b_errata.tex:81` is inaccurate.** It says the figures were supplied "from the current data pipeline" — but the
   current pipeline yields the Ch.5 counts, not 990,518. The 990,518 set came from the CoUrb published table, produced
   by an intermediate ETL state. As written, this sentence invites the very question it is meant to close. See NEW-8.
3. **`NORTH_STAR.md:117-121`** still asserts the superseded rule that the CoUrb row is "a cross-check only, not a
   source" — now contradicted by the shipped chapter.
4. **`HANDOFF_v1.md:179,183`** still asserts the abandoned figures (10,460 / 64,454 / 960,520) as current, two rulings
   out of date.

The date-range half is a non-issue: `5_mobiwac.tex:286-288` already carries a measured provenance comment distinguishing
the Figshare dump from the SNAP/cho2011 dump, and `4_courb.tex:351` states the Gowalla collection window as a
limitation.

**One sentence for the reader** (best home: the Ch.5 data subsection or the Appendix B CBIC row): Chapters 3–4 report
the corpus as extracted by the ETL of their time; Chapter 5 reports the current extraction after an expanded category
mapping.

**Resolution notes**

> _Record the authoritative dataset manifest and explanatory text here._

### REV-027 — Chapters 3 and 4 use inferential verbs without reported tests 🔧

- **Severity:** Major
- **Status:** Open
- **Classification:** Confirmed claim-evidence mismatch
- **File:** `src/chapters/3_cbic.tex`; `src/chapters/4_courb.tex`
- **Section:** Results and discussion
- **Reported by:** Reviewers 05, 06, 07, 09, and 17

**Finding**

Chapter 3 uses “significantly outperform” and related statistical language while reporting five-fold means/standard
deviations without an identified inferential test. Chapter 4 repeatedly selects and describes the best encoder per cell
but reports no test or multiplicity control.

**Why it matters**

Numerically higher means do not establish statistical significance. Selecting among many dataset/task/encoder cells
further increases the risk of overinterpreting chance variation.

**Recommended action**

If valid paired fold/seed artifacts exist, specify and run an appropriate analysis with multiplicity control and a
defensible sampling unit. Otherwise replace inferential verbs with descriptive language such as “had a higher mean in
this evaluation.”

**Author response**

> I agree with the claude take and let's make the changes in the ch. 3 and add this changes in the appendix errata.

**Claude take (2026-07-24) — CONFIRMED for Chapter 3; REFUTED as literally stated for Chapter 4. The fix mechanism
already exists.**

Chapter 3 uses "significant/significantly" **12 times**, and **11 of the 12 are verbatim published wording**. The only
one inside dissertation-rewritten prose is `:366` (errata B3 changed the surrounding clause and kept the adverb). No
inferential test is reported anywhere in either chapter — a grep for
`p-value|Wilcoxon|t-test|statistical test|confidence interval|Holm|TOST` across both files returns exactly one line,
`3_cbic.tex:344`, which appeals to "statistically" and reports no test.

Not all 12 are equal. `:197` and `:225` attribute claims to cited work; `:78` uses the ordinary-language sense (
"significant progress"). The load-bearing offenders are the four that attach the word to **this paper's own empirical
comparisons**: `:55`, `:269` ("both our MTL and Single models significantly outperform HMRM"), `:307`, `:344`.

**Chapter 4 contains zero occurrences of "significant".** Its comparative language is "consistently superior",
"substantial", "wide margin" — and the single most statistically careful sentence in the chapter is one the
**dissertation added** (`:297`, errata A1: "a technical tie … where the baseline mean exceeds the best variant by 0.02
percentage points, a gap within one standard deviation"). That cuts directly against the premise that the dissertation
layer made things worse. On the strict reading, Ch.4 needs nothing.

**The policy tension resolves itself.** `WRITING_LAW.md:184-185` makes "significant only with a test" a checklist item
and `:72` binds verbs to tests "wherever those results appear", while the errata policy protects reproduced prose.
`apx_b_errata.tex` Table B.2 already resolves exactly this class — eight wording substitutions in reproduced CBIC prose,
declared, "claim strength unchanged". Substituting "significantly outperform" → "outperform in every category" rides the
same mechanism and *reduces* claim strength rather than changing it.

**My recommendation:** four substitutions (`:55`, `:269`, `:307`, `:344`) as new Table B.2 rows, nothing in Ch.4, plus
one frame sentence noting that Chapters 3–4 report fold means and standard deviations without significance testing and
that tested claims are confined to Ch.5. `1_introduction.tex:244` already half-draws that contrast.

**Resolution notes**

> _Record the test/artifact or revised descriptive wording here._

## 7. Structure, Coherence, and Readability

### REV-017 — Chapter 3 and parts of Chapter 4 require a professional language pass ⚠️

- **Severity:** Major
- **Status:** Open
- **Classification:** Confirmed editorial problem
- **File:** `src/chapters/3_cbic.tex`; `src/chapters/4_courb.tex`
- **Section:** Throughout, especially Chapter 3 tasks/method/results/conclusion
- **Reported by:** Reviewers 01, 02, 03, 15, and 16

**Finding**

Chapter 3 contains broken constructions, inconsistent task labels, formula explanations that do not parse, and a results
sentence near line 307 whose logical relation is unclear. Chapter 4 retains several literal Portuguese-to-English
collocations. Repeated article roadmaps and three-part “causes/future work” templates also make the dissertation feel
mechanically assembled.

**Why it matters**

These passages obscure the scientific content and will attract committee questions before the stronger contribution is
reached.

**Recommended action**

After the scientific corrections, perform a line edit focused on subject–verb completeness, task nouns, logical
connectors, paragraph purpose, and idiomatic academic English. Preserve article fidelity through marked errata/preface
commentary rather than silently changing claims.

**Author response**

> I agree with in most part of the claude take, but in my opinion we should be carreful and just change the phrases and
> construction that really hurt the construction, or create inconsistance. We already doing many change in the text and
> I don't know how this can be seend for the review, maybe with bad eyes, so let's be more creterius and to focus on
> what is the main parts.

**Claude take (2026-07-24) — the finding is real; the scope needs your ruling, and the mechanism already exists.**

I did not re-audit every sentence flagged as broken, so I take the prose judgment at face value. What I can add is that
the *policy* question the review leaves open is already answered by precedent inside your own document:
`apx_b_errata.tex` Table B.2 ("Wording substitutions in the reproduced CBIC 2025 prose (writing-rule conformance; claim
strength unchanged)") already records eight substitutions — "leveraging"→"using", "Moreover"→"In addition",
"underscore"→"indicate", "leveraged"→"exploited". A professional language pass on Ch.3 is the **same class of edit under
the same declared mechanism**, one row per substitution, no new policy needed.

That resolves the tension the review flags between the errata policy and the writing law. The errata policy forbids
*silent* correction, not correction; Table B.2 is what non-silent looks like.

**What still needs your decision:** how far the pass goes. My recommendation is to bound it to (a) sentences that do not
parse, (b) the task-noun reconciliation from REV-010, and (c) the inferential verbs from REV-027 — and explicitly
**not** to a general style normalization, which would trip the variance-compression failure mode your own guardrails
name (`AGENT_GUARDRAILS.md:190`) and would produce a larger errata table than the scientific content justifies. Chapter
4's translated collocations are a separate, smaller job and should be judged against the L5 fidelity gate rather than
rewritten for fluency.

Advisor confirmation of the adopted errata policy is still the gating item, as the review's own author-response block
notes.

**Resolution notes**

> _Record editing scope and sign-off here._

### REV-018 — Abstracts are long and the Portuguese abstract spills to a second page ⚠️

- **Severity:** Moderate
- **Status:** Open
- **Classification:** Confirmed presentation issue; exact institutional limit requires verification
- **File:** `src/0_main.tex`
- **Section:** Resumo and Abstract
- **Reported by:** Reviewers 01, 13, 15, and 18

**Finding**

The Resumo and Abstract are approximately 428 words. In the defense build, the Resumo fills page 3 but strands only two
keywords on an otherwise nearly blank page 4; the Abstract then starts on page 5.

**Why it matters**

The spill weakens front-matter polish and may conflict with local expectations even if no hard word limit is stated in
the repository.

**Recommended action**

Compress both mirrored abstracts after the final results are known, preserving objectives, method, principal result,
limitation, and contribution. Verify the UFV/PPGCC word/page rule.

**Author response**

> We indeed need to focus on it and let's eval how long is the abstract of the exemples that we have and set the target
> cound word of this. And indeed as claude sugest we should do this in last so after settle all the text we back on it.

**Claude take (2026-07-24) — CONFIRMED, and the reviewer under-reported the Resumo. No norm is being violated.**

Measured directly: **Abstract 429 words** (`0_main.tex:251-286`), **Resumo 505 words** (`:182-222`). The spill is real
and precisely as described — page 4 of the defense build contains 61 characters total, namely the last two Portuguese
keywords ("previsão da próxima região", "representação em nível de check-in"), on an otherwise blank page. The Abstract
does **not** spill.

**No word or page limit exists in either compliance source.** `UFV_COMPLIANCE.md:39` specifies only the system-field
format; the Manual 04/2026 §5.4–5.5 imposes formatting rules only, and a grep of the whole manual for word-count
language returns nothing but the "uma palavra por linha" keyword rule. So this is presentational polish, not compliance
risk — the review's own severity of Moderate is right, and the "verify the UFV/PPGCC word/page rule" action can be
closed: I verified it, there is none.

**Why it still needs you.** Trimming 505 words changes claim wording, and the Resumo/Abstract are a declared
**claim-parity pair** — both carry `[NEEDS SIGN-OFF]` (`0_main.tex:177`, `:223`, `:247`, `:287`), and any cut must be
mirrored in both or the parity breaks. That is not delegable.

**A purely mechanical alternative exists** if you would rather not touch the text before the results settle: a
`\clearpage`/spacing adjustment so the keywords do not strand. It leaves a two-page Resumo but removes the near-blank
page, which is the part a reader notices.

**Resolution notes**

> _Record the applicable rule and final word count here._

## 8. Terminology, Notation, and Consistency

### REV-019 — HGI is described as a standard POI embedding without explaining the adaptation 🔧

- **Severity:** Moderate
- **Status:** Open
- **Classification:** Confirmed terminology/citation issue
- **File:** `src/chapters/2_fundamentals.tex`; `src/chapters/5_mobiwac.tex`; `src/configs/embedding_fusion.py`
- **Section:** HGI/Check2HGI description
- **Reported by:** Reviewers 05 and 11

**Finding**

The dissertation calls HGI a standard place/POI embedding. The cited published method outputs region embeddings. The
implementation does use an HGI-derived internal POI-node representation, but that adaptation is not explained.

**Why it matters**

The present wording attributes an implementation-specific adaptation to the published method and obscures what Check2HGI
actually contributes.

**Recommended action**

Use “HGI-derived POI-node representation” and explicitly distinguish the cited region-level output from the local
adaptation.

**Author response**

> I agree with the claude take.

**Claude take (2026-07-24) — the reviewer's premise is wrong; a smaller real improvement remains.**

The claim that "the cited published method outputs region embeddings" is not supported.
`research/embeddings/hgi/hgi.py:101-110` documents both exports and lines 176-199 write both: POI-level
`embeddings.parquet` keyed on `placeid`, region-level `region_embeddings.parquet` keyed on `region_id`. The POI vector
is not an afterthought — it is the encoder output the hierarchy is built from (`HGIModule.py:112` produces
`pos_poi_emb`, `:119` pools it into `region_emb`). Both exports are live downstream
(`src/data/inputs/region_sequence.py:34-40` consumes the region file). And the bib entry the dissertation itself carries
is titled "Learning Urban Region Representations with **POIs** and Hierarchical Graph Infomax" — POIs are named as an
input, not excluded as an output.

Nor is the dissertation's wording misleading. "Region-aware place embeddings" (`2_fundamentals.tex:160-165`) accurately
describes `pos_poi_emb`: a place-level vector trained under an objective tying it to its region and city.
`5_mobiwac.tex:116-118`'s load-bearing claim, "Both produce one vector per place", is simply true.

**The genuine residual is framing, and it is cheap.** Huang et al.'s stated goal is urban *region* representation for
region-level tasks; this work repurposes the POI-level intermediate as a place embedding for a sequential-prediction
task the source never addressed. That repurposing is never named, and a domain examiner who knows the paper will ask
about it.

Worth adding in the same clause, because it works in your favour: `research/embeddings/hgi/CLAUDE.md` records that the
cross-region edge weight was retuned from the paper's 0.4 to **0.7** ("on Alabama Cat F1 rises monotonically 0.74 →
0.82"). So the HGI baseline as run is a **tuned** HGI, not a handicapped one. Saying so pre-empts the "you under-tuned
the baseline" question at no cost.

One clause in `2_fundamentals.tex` (frame prose, freely editable). Leave Ch.5 alone.

**Resolution notes**

> _Record the corrected terminology here._

## 9. Figures, Tables, Equations, and References

### REV-020 — Citation support and bibliography metadata need targeted correction 🔧

- **Severity:** Moderate
- **Status:** Open
- **Classification:** Confirmed citation issues
- **File:** `src/references.bib`; `src/chapters/2_fundamentals.tex`; `src/chapters/3_cbic.tex`;
  `src/chapters/4_courb.tex`
- **Section:** Methods citations and bibliography
- **Reported by:** Reviewer 05

**Finding**

The bibliography resolves all 98 cited keys and contains no duplicate keys or undefined citations. However, the Nash
citations do not support all implementation-specific claims; Pedregosa et al. (2011) cannot support
`StratifiedGroupKFold`; the Kohavi DOI points to a 2026 Zenodo redeposit; the Rußwurm venue should identify ICLR 2024;
several survey/drift claims need direct support; and `liu2014geographical` appears orphaned.

**Why it matters**

These are visible citation-integrity defects despite an otherwise healthy bibliography.

**Recommended action**

Correct metadata, cite the official implementation/documentation or appropriate methodological source for grouped
stratification, narrow unsupported Nash and complexity claims, and remove unused entries.

**Author response**

> I agree with claude takes. About the `A`,We can eval the best approach but for now I am lean on add this in the
> appendix+_b as an errata, also we need to check if the implementation in the cbic was indeed relies on "**gradient
signs rather than scales**", besides not been the faithul one, if this case turns to be truth, we just need to address
> in the errata this change, and also eval if we have fix for the mobiwac.

**Claude take (2026-07-24) — 4 of 5 confirmed, 1 refuted and should not be reopened. One is sharper than the reviewer
states.**

- **(a) Nash citations — CONFIRMED, and worse than flagged.** `3_cbic.tex:225` says Nash-MTL relies on "**gradient signs
  rather than scales**". It does not; the method is *scale-invariant*, which the same chapter states correctly twelve
  lines earlier at `:212`. The chapter contradicts itself, independently of the citation question. "Only two
  matrix-vector products per iteration" also understates a method that runs an iterative concave program
  (`optim_niter=20`–30 cvxpy solves per update in your own implementation). Separately `3_cbic.tex:102` cites
  `\cite{nash}` for a claim about modality/minibatch heterogeneity that Navon et al. do not establish, and
  `4_courb.tex:115` calls it a "regularizer" when it is a gradient-balancing optimizer.
- **(b) Pedregosa for `StratifiedGroupKFold` — REFUTED, and already ruled on.** The prose at
  `2_fundamentals.tex:444-447` names **no class**; it describes the behaviour generically and cites the library.
  `references.bib:748-752` records the reasoning and the explicit instruction "Do not add a second URL/API-docs
  citation", and `:473` marks it "SINGLE cite (author ruling)". Citing the library paper for a library feature is
  standard. Do not reopen a recorded decision.
- **(c) Kohavi DOI — CONFIRMED**, and already `[VERIFY]`-flagged in the bib. A DOI on a 1995 IJCAI entry that resolves
  to a third-party Zenodo re-deposit misrepresents the record. Cheapest correct fix: drop the `doi` field; IJCAI-95
  genuinely predates DOIs.
- **(d) Rußwurm — CONFIRMED.** Typed `@misc`/arXiv though published at ICLR 2024, and `year={2024}` already being the
  conference year makes the preprint typing internally odd. Precedent exists: `apx_b_errata.tex:229-230` already
  re-cited GAT from arXiv to ICLR 2018. Also worth noting: the citation key contains a non-ASCII character
  (`rußwurm…`) — it compiles today, but it is fragile.
- **(e) `liu2014geographical` — CONFIRMED.** I verified it: 99 `@` entries in `references.bib`, 98 `\bibitem`s in
  `build/main.bbl`. The key appears exactly once in the LaTeX, as `\texttt{}` inside `apx_b_errata.tex:267` — not a
  `\cite`. So the errata table points the reader at a key the printed bibliography silently drops. Better fix than
  deleting the entry: rephrase the errata row to name the work rather than the key.

(c), (d), (e) are bibliography-only, need no decision, and belong in the existing bib-errata section. **(a) needs your
call** and, given `apx_b_errata.tex:87-91` already preserves one Nash sentence deliberately, preserve-plus-note is the
consistent choice — pair it with the REV-005 Ch.4 caveat.

**Resolution notes**

> _Record corrected keys/claims here._

### REV-021 — Rendered tables/equations exceed the required right margin 🔧

- **Severity:** Major
- **Status:** Open
- **Classification:** Confirmed formatting error
- **File:** `src/chapters/2_fundamentals.tex`; `src/chapters/4_courb.tex`
- **Section:** Chapter 2 lineage table; Chapter 4 equation block
- **Reported by:** Reviewers 13 and 18

**Finding**

The Chapter 2 lineage table reaches approximately 0.965 cm from the paper edge (defense page 21/final page 16), short of
the required 2 cm right margin. A Chapter 4 equation reaches approximately 1.488 cm (defense page 50/final page 45). The
LaTeX log reports a 29.764 pt overfull box in the Chapter 2 table and a 15.139 pt overfull box in Chapter 4.

**Why it matters**

These are measurable margin violations and will remain in the archival PDF.

**Recommended action**

Redesign the table rather than globally shrinking it; break or align the equation; rebuild both defense and final
variants; and rerun a page-geometry check.

**Author response**

> I agree with claude takes. But takes this oportunit to eval the other assets, an exemple is the fig 2 or 3 or mobiwac
> where some lables are over passing the margins is nothig huge, but is a care that can be good.

**Claude take (2026-07-24) — CONFIRMED, and this is the complete list: there are exactly two overfull boxes in the whole
document.**

Verified in `src/build/main.log`: line 1604, `Overfull \hbox (29.76408pt too wide) in paragraph at lines 220--238` (the
Ch.2 lineage `tabular`); line 1728, `Overfull \hbox (15.13911pt too wide) at lines 175--176`. Nothing else. The 30
overfull vboxes an earlier review reported were eliminated by the round-2 short chapter titles. The 12 underfull hboxes
that remain are all inside the Appendix B errata tables and are cosmetic.

Measured ink extents against A4 (595.28 pt = 21.00 cm) with the required 2 cm right margin (`UFV_COMPLIANCE.md:34`,
Manual §8):

| Page                    | max ink  | right margin | verdict   |
|-------------------------|----------|--------------|-----------|
| 21 (Ch.2 lineage table) | 20.03 cm | **0.97 cm**  | violation |
| 50 (Ch.4 paragraph)     | 19.51 cm | **1.49 cm**  | violation |
| 64, 68 (Ch.5 tables)    | 18.99 cm | 2.01 cm      | compliant |

One correction to the review: the second box is **not** an equation. It is a prose paragraph containing unbreakable
inline math (`4_courb.tex:175-176`, the sentence about $\mathbf{E}_{\text{POI\_category}} \in \mathbb{R}^{64}$); the
nearby display equation at `:179` is clean. That changes the fix from "break or align the equation" to "rephrase or add
a discretionary break".

Fully mechanical, no decision needed. Both were already known — Reviewer 18 logged them as M5/m7 and they sit as
`HANDOFF_v1.md` item 15, queued and unfixed.

**Resolution notes**

> _Record rebuilt page numbers and measured margins here._

### REV-022 — Visual language and accessibility are inconsistent ⚠️

- **Severity:** Moderate
- **Status:** Open
- **Classification:** Confirmed and potential presentation issues
- **File:** `src/chapters/4_courb.tex`; `src/chapters/5_mobiwac.tex`; associated figure assets
- **Section:** Architecture, distribution, and embedding-quality figures
- **Reported by:** Reviewers 01, 13, and 18

**Finding**

The Chapter 4 architecture figure (defense page 47) retains Portuguese labels inside an English chapter. The spatial
plot on page 52 relies on close red/orange hues without redundant markers, with extremely small axes and legend. Chapter
3 Figure 1 and Chapter 4 Figure 2 use raster diagrams with labels far below body-text size. Chapter 5 Tables 8 and 10
are reduced to footnote-scale; Table 10's eleven columns, uncertainty notation, superscripts, and notes are not
comfortably readable in print. A Chapter 5 embedding-quality axis is labelled “Score (0–1)” while silhouette is
described on \([-1,1]\). Plot fonts and emphasis rules also change visibly between article chapters, and full
multi-sentence captions make the front-matter figure/table lists unnecessarily dense.

**Why it matters**

These inconsistencies reduce professional unity and can make figures misleading or inaccessible.

**Recommended action**

Translate embedded labels; use colorblind-safe palettes plus patterns/markers; correct the axis range/label; regenerate
raster diagrams with larger vector text; split or rotate wide tables rather than shrinking them; standardize plot
typography and best/second-best emphasis; use optional short captions for list entries; and verify every visual at print
size and in grayscale.

**Author response**

> Let's fix what is in our control. About the figs that we don't have the source (I belive that may is in the commit you
> cna try to check), let's keep them as is for now and
> let's create a document od pendencies.md in the src_utils, and add this there.

**Claude take (2026-07-24) — four of five sub-claims verified; one is understated; one item is genuinely blocked on
external material.**

- **Portuguese labels in the Ch.4 figure — CONFIRMED.** Rendered p.47 carries "Encoder Espacial", "Encoder Temporal",
  "Encoder Categórico", "Coordenadas (lat, lon)", "Timestamps (hora, dia)", "Categorias (POI graph)" inside an English
  chapter whose inner boxes are already English.
- **Colour without redundant encoding — CONFIRMED for Ch.4 only.** `4_courb.tex:249` distinguishes "Food (red)" from
  "Shopping (orange)" by hue alone, same marker, legend encoding colour only. The Ch.5 figures are **fine** and the
  review should not be read as implicating them: `figures/mobiwac/fig4_deltas_diss.py:81-82` uses deep blue `#1f4e79` vs
  brick red `#c0392b` (high luminance contrast) and both figures annotate every bar with its numeric value.
- **Raster diagrams — CONFIRMED.** Figs 1 and 2 render at ~190 and ~174 effective dpi.
- **"Tables 8/10 at footnote scale" — UNDERSTATED, and the mechanism is different.** There is no `\footnotesize` on any
  Ch.5 table body; the two `\footnotesize` hits are table *notes*. The shrink comes from
  `\begin{adjustbox}{max width=\textwidth}` (`5_mobiwac.tex:315`, `:478`). Measured span sizes: body text 11.96 pt
  everywhere, **Table 8 at 8.13 pt, Table 10 at 8.00 pt with the fold-sd at 6.00 pt**. At a 12 pt base `\footnotesize`
  is 10 pt, so these are nearer `\scriptsize`/`\tiny`. See NEW-7.
- **"Score (0–1)" vs silhouette on [−1,1] — CONFIRMED.** The label is set in a committed generator,
  `src/figures/mobiwac/fig3_embquality_diss.py:119`, with `set_ylim(0, 1.14)` at `:117`, and the plot does show
  silhouette (0.5668 vs 0.0003). The chapter's own prose at §5.6.1 says the silhouette is "on a −1 to 1 scale". Nothing
  is misdrawn — the plotted values are non-negative — but the axis label is wrong for one of the two metrics.
  One-character-class fix: `"Score"`.

**What is blocked.** Figures 1, 2 and 3 exist only as flattened PNGs; no `.drawio`, `.svg` or `.py` source exists
anywhere under `articles/dissertacao/`. Fig 2 belongs to a co-authored published paper, so relabelling it in English is
a fidelity call, not a formatting one.

**Split the response:** the axis label and the two wide tables are mechanical and should just be done; the figure
redraws need you (source recovery from the CoUrb authors, or authorization to recreate).

**Resolution notes**

> _Record regenerated assets and accessibility checks here._

### REV-028 — CoUrb translation is broadly faithful, but the adaptation record is incomplete 🔧

- **Severity:** Moderate
- **Status:** Open
- **Classification:** Confirmed documentation gap
- **File:** `src/chapters/4_courb.tex`; `src/chapters/apx_b_errata.tex`; CoUrb source materials and adaptation ledger
- **Section:** Chapter 4 preface, captions, and translation provenance
- **Reported by:** Reviewer 08

**Finding**

The core English body, numerical errata, and figures are faithful to the Portuguese source. However, added analytical
lead/caption sentences are not fully represented in the adaptation ledger, while the chapter's reproduction wording does
not clearly say that the article abstract and acknowledgments were omitted.

**Why it matters**

The issue is transparency, not detected scientific distortion. An incomplete ledger makes it difficult to distinguish
translation, typesetting, correction, and new dissertation framing.

**Recommended action**

Describe the chapter as a translation/reproduction of the article body, enumerate omitted front/back matter, and ledger
every substantive added sentence. Do not rewrite the faithful core merely to reduce similarity.

**Author response**

> I agree with the claude take.

**Claude take (2026-07-24) — the *ledger* is complete; the *reader-facing* record is not. That inverts the review's
framing.**

`4_courb_ADAPTATION_LEDGER.md:29` (row B4) does record the added sentences, quoted in full — the three table lead
sentences, the expanded Figure 4.2 reading instruction — and `:32` (row B7) records that the paper's title, authors,
address, **abstract, resumo and Acknowledgments are not reproduced**. I confirmed all four added sentences exist in the
chapter (`4_courb.tex:249,255,256,297`) and are absent from the published source (grep over `articles/CoUrb_2026/`
including `src_en/` returns zero hits).

So the reviewer's "not fully represented in the adaptation ledger" is wrong. **The two real defects are classification
and disclosure:**

1. **Misfiled.** B4 sits under section B, "Re-typeset departures (**mechanical**)", not section C, "Additions required
   by the dissertation frame (not in the published paper)", where C1/C2/C3 live. A sentence that *interprets a table* is
   content, not typesetting.
2. **Appendix B therefore undercounts to the reader.** `apx_b_errata.tex` §B.2 declares "**three marked additions**" for
   Ch.4 — the preface, the MTLnet recap, and the protocol-clarification sentence. At least **seven** non-published
   sentences exist. Appendix B opens by claiming it lists "**every** content departure" (`:29-32`), so the undercount is
   a self-contradiction in the appendix whose entire purpose is completeness. See NEW-9.
3. **The omission statement never reaches the reader.** The Ch.4 preface (`:12-18`) states venue, DOI, pages,
   authorship, protocol caveat and terminology bridge — and does not say the abstract and acknowledgments were dropped.
   Neither does Appendix B (grep for `abstract|acknowledg|front matter` in `apx_b_errata.tex` returns nothing), nor §1.5
   Organization, which says only that chapter content "is faithful to the published text of each article".

Mostly mechanical: reclassify B4 into section C, correct the "three marked additions" count, add one omission sentence
to the preface or Appendix B. **One thing I did not check and you should:** whether `3_cbic_ADAPTATION_LEDGER.md` and
`5_mobiwac_ADAPTATION_LEDGER.md` have the same undercount pattern.

The review's "do not rewrite the faithful core merely to reduce similarity" is right and worth keeping.

**Resolution notes**

> _Record the completed ledger and final scope statement here._

### REV-029 — Chapter 5 floats interrupt sentences and precede their sections 🔧

- **Severity:** Major
- **Status:** Open
- **Classification:** Confirmed presentation issue
- **File:** `src/chapters/5_mobiwac.tex`
- **Section:** Architecture, experimental setup, and Section 5.6.2
- **Reported by:** Reviewers 15 and 18

**Finding**

In the defense PDF, Figure 4 separates “The reason is” on page 60 from “visible in the gradients” on page 61
(`5_mobiwac.tex`, lines 197–205). Figure 5 similarly interrupts a sentence across pages 62–63 (lines 266–274). Dataset
Table 8 appears above the Section 5.5/5.5.1 headings that introduce it. Page 68 is floats-only, and Table 10/Figure 7
appear before the rendered Section 5.6.2 heading and opening explanation.

**Why it matters**

Figures should never separate consecutive parts of a sentence, and results should not appear before their section
framing. The current placement creates visible reading failures at the dissertation's most important empirical moment.

**Recommended action**

Move float declarations to completed paragraph boundaries and constrain/reorder them so each heading and one framing
paragraph appear before its table/figure. Recheck downstream page balance after the change.

**Author response**

> Let's follow the claude takes and audit after complete.

**Claude take (2026-07-24) — CONFIRMED on all five sub-claims, and it is a one-line fix with a clear cause.**

Root cause: **every** float in Chapter 5 requests `[!t]` — the most aggressive top placement, where `!` discards LaTeX's
placement restrictions. I verified all seven: `5_mobiwac.tex:197, 266, 303, 398, 430, 471, 503`. For contrast, Ch.4's
floats use `[htbp]`. This came in from the two-column ACM original, where `[!t]` is idiomatic and harmless; in a
one-column 12 pt dissertation it is not.

**The source ordering is correct.** Every float is declared after its owning heading (`\section{Experimental Setup}` at
`:276` and `\subsection{Data}` at `:279` both precede Table 8 at `:303`). `[!t]` then hoists the float past the heading
in the output. So this is purely a placement defect, not a structural one — which is why the fix is cheap.

Rendered consequences, all verified: Figure 4 splits "The reason is" (p.60) from "visible in the gradients" (p.61);
Figure 5 splits "the region output" (p.62) from "also keeps a private spatial path" (p.63); Table 8 renders above the
§5.5/§5.5.1 headings that introduce it; page 68 is floats-only — LaTeX says so itself at `build/main.log:1807`, "Text
page 68 contains only floats"; and Table 10 lands on p.68 a full page before its §5.6.2 heading (`main.toc` puts §5.6.2
on p.69), with Figure 7 above that heading on p.69.

Relax the seven `[!t]` to `[tbp]` or `[htbp]`, and move the two mid-sentence declarations to a paragraph boundary. Zero
content effect, one rebuild to re-check downstream page balance. The review is right that this lands at the
dissertation's most important empirical moment — but the earlier internal review rated only the floats-only page and
called it low priority; the sentence-splitting and heading-precedence effects are new.

**Resolution notes**

> _Record the rebuilt page order here._

## 10. Formatting and Submission Readiness

### REV-023 — UFV front matter and administrative prerequisites are incomplete ⚠️

- **Severity:** Major
- **Status:** Needs author input
- **Classification:** Confirmed omission plus unresolved administrative facts
- **File:** `src/0_main.tex`; `src/chapters/apx_a_contributions.tex`; submission documentation under
  `articles/dissertacao`
- **Section:** Cover, approval page, status declarations, submission checklist
- **Reported by:** Reviewers 12 and 13

**Finding**

The defense build begins with the title/folha de rosto and has no completed cover; the approval page is a placeholder;
committee/date fields remain unresolved; Appendix A calls three papers published although MobiWac is under review.
Repository process records also leave publication proof filing, anti-plagiarism certificate, signatures, English-frame
approval, working-title approval, and final `AcademicoPG` pagination unverified. The documented page counts (87/83) are
stale relative to the current 89/84 builds.

**Why it matters**

Even a scientifically corrected manuscript cannot be submitted with unresolved mandatory front matter and filing
prerequisites.

**Recommended action**

Obtain the current UFV/PPGCC checklist and template, complete the defense metadata, correct publication statuses, verify
the minimum scheduling interval, and regenerate the final variant only after the portal draft determines pagination.

**Author response**

> I agree with the claude takes, and also let's eval the dissertation of exemple to eval if we are missing other points.

**Claude take (2026-07-24) — all five sub-claims CONFIRMED, plus a booby-trap the review did not find.**

- **No cover.** `abntex2-UFV.sty` defines `\imprimircapa`, but `0_main.tex` never calls it — the defense branch at
  `:154-160` calls only `\imprimirfolhaderosto`. Page 1 of the build is the folha de rosto. `\campus{}` is never set. No
  ficha catalográfica.
- **Placeholder approval page.** `0_main.tex:161-168` prints a literal bracketed placeholder; rendered p.2 contains that
  and nothing else.
- **⚠ NEW — the approval macro is contaminated.** `abntex2-UFV.sty`'s `\imprimirfolhadeaprovacao` hardcodes a prior
  student's name: `\assinatura{\textbf{Gabriel Vita Silva Franco} \\ Author}`. It is currently unused, so nothing wrong
  ships today — but anyone who switches from the placeholder to the macro without editing it will print the wrong author
  on the approval sheet. Fix it now, while it is harmless. See NEW-6.
- **Committee/date unresolved.** `0_main.tex:122-124` carries three bracketed placeholders.
- **"Three published studies".** `apx_a_contributions.tex:41` is the **only** place in the document making that claim;
  everywhere else is correct (`1_introduction.tex:118`, `2_fundamentals.tex:218`, `5_mobiwac.tex:23-24`,
  `6_conclusion.tex:73` all say submitted/under review). One-word fix.
- **Page counts.** I verified with `pdfinfo`: **89** and **84**, against 87/83 documented in 27+ places including
  `CLAUDE.md:28-29`, `PLAN.md:17-18`, `HANDOFF_v1.md:68,127`. Worth knowing for a second reason: all 18 reports in
  `src_utils/_history/_review_v1/` were run against the older 87 pp build, so their page references are off by up to two. See
  NEW-10.

Cover content, the real PPG signature page, banca names and the defense date are external facts and are yours. The
"three published studies" clause, the page counts and the contaminated macro are mechanical and should not wait.

**Resolution notes**

> _Record each completed prerequisite and evidence path here._

### REV-024 — Bibliography font is explicitly smaller than the documented requirement ⚠️

- **Severity:** Major
- **Status:** Open
- **Classification:** Confirmed formatting error
- **File:** `src/0_main.tex`
- **Section:** Bibliography
- **Reported by:** Reviewer 13

**Finding**

The bibliography is explicitly set in `\footnotesize` near lines 369–370, approximately 10 pt, while the local rule set
expects 12 pt body/reference text.

**Why it matters**

This is an intentional format deviation, not an incidental rendering issue.

**Recommended action**

Remove the bibliography font-size reduction unless an authoritative current rule expressly permits it, then rebuild and
verify page count and line wrapping.

**Author response**

> I agree with claude takes, let's try to fix what is possible, and for those parts that need extra input like the name
> of the banca, add in the pendencies.md file.

**Claude take (2026-07-24) — CONFIRMED as a deviation, but there is a direct same-advisor precedent that passed, so this
is an advisor question, not a compliance failure.**

Verified: `0_main.tex:369-370` wraps `\bibliography{references}` in `{\footnotesize …}`, and the reference pages measure
**9.96 pt** against **11.96 pt** body text. The rule is unambiguous — `UFV_COMPLIANCE.md:32` and Manual §8 both say
Arial or Times New Roman, size 12, with no bibliography exception anywhere in §8.

**What changes the picture.** The construct was inherited verbatim from the skeleton you built on:
`exemples/germano/.../0_main.tex:285-287` has the identical `{\footnotesize \bibliography{references}}`, and the Germano
PDF's reference pages measure 9.96 pt. Germano defended in 2024 under the same advisor. Viegas, by contrast, sets
references at 11.96 pt.

So the honest framing is: one exemplar did it and passed; one did not; the written rule says 12. Your own compliance doc
anticipates exactly this dilemma at `:32` — "Viegas used Palatino and passed, but that predates strict enforcement;
**comply, don't gamble**." By its own stated logic that argues for removing the wrapper.

The edit is one deletion. The reason it needs you is the consequence: the reference section grows by roughly two pages,
which interacts with the AcademicoPG pagination you cannot finalize until the portal draft exists. Worth raising in the
same advisor conversation as the title and the errata policy rather than deciding alone.

**Resolution notes**

> _Record the final reference font and rule here._

### REV-025 — AI/provenance disclosure claims approval that the repository does not show ⚠️

- **Severity:** Major
- **Status:** Needs author input
- **Classification:** Confirmed internal contradiction
- **File:** `src/chapters/apx_c_ai_disclosure.tex`; `AGENT_GUARDRAILS.md`; `src_utils/DECISOES_PENDENTES_ptBR.md`;
  `storyline/audit/`
- **Section:** AI-use disclosure and provenance
- **Reported by:** Reviewer 16

**Finding**

Appendix C states that every passage/word received the author's reading and approval recorded in version control, while
the same appendix and multiple frame passages remain marked `[NEEDS SIGN-OFF]`. Git history shows extensive `draft(ai):`
assembly but no clear dissertation-level final human-approval checkpoint. The disclosure names Claude but omits exact
model versions and does not fully distinguish editing, translation, and generation across articles.

**Why it matters**

An inaccurate transparency statement is more damaging than a precise disclosure of substantial AI assistance. Human
approval and responsibility cannot be inferred from draft history.

**Recommended action**

Do not claim completed approval until it occurs. Add a short front-matter pointer to a precise appendix naming
tools/models, tasks, scope, limitations, and author verification. Preserve genuine pre-AI Portuguese decision records;
do not manufacture retroactive checkpoints. Include the present Codex/OpenAI-assisted review if it materially informs
the final manuscript.

**Author response**

> I and to keep the AI section slim and direct as possible. Abou the missing [NEEDS SIGN-OFF], let's list them in the
> pendences.md. My take is to keep the ai section as it is.

**Claude take (2026-07-24) — CONFIRMED. The appendix asserting universal approval is itself flagged as unapproved.**

`apx_c_ai_disclosure.tex:50-57` states: "the author's own reading and approval, recorded in version control … **the
author reviewed and takes responsibility for every word of the final text**." Eleven lines earlier, in the same file,
`:11-12`:
`% [NEEDS SIGN-OFF: whole appendix -- the author must confirm scope, tool naming, and whether to name specific model versions he can source.]`

Full inventory in `src/`: **14 `[NEEDS SIGN-OFF]`** markers (`0_main.tex` ×4, `1_introduction.tex:79`,
`2_fundamentals.tex:40,512`, `5_mobiwac.tex:19,88,423`, `6_conclusion.tex:79`, and all three appendices flagged whole)
and **7 `[VERIFY]`** (three already marked resolved). All are LaTeX comments, so none render — the risk is a false
statement inside a document about research integrity, not visible litter in the PDF.

One point in your favour that the review does not make: the claim is **forward-looking** ("before reaching the
advisor"). It becomes true if you complete the sign-off before the build ships. So the choice is genuinely binary and
not embarrassing either way: sign off on the 14 items, or soften the sentence to describe the verification pipeline
without asserting a completed end-to-end read.

Two additions I would make regardless, because they are cheap and they are what a committee actually checks: name the
review-suite model you *can* source (`claude-opus-4-8`, already recorded in `CLAUDE.md` §1 with the reason — Fable
tokens exhausted mid-run), and state plainly that the drafting/translation model versions are not recoverable from the
commit record rather than inventing them. An honest gap reads far better than a smooth claim. The present
Codex/OpenAI-assisted review should be disclosed too, if it informs the final text — and on the evidence of this pass,
it will.

**Resolution notes**

> _Record the verified disclosure, human sign-off commit, and advisor decision here._

### REV-026 — Ethical/privacy considerations for individual mobility data are absent ⚠️

- **Severity:** Moderate
- **Status:** Needs author input
- **Classification:** Potential submission issue
- **File:** `src/chapters/1_introduction.tex`; `src/chapters/5_mobiwac.tex`; `src/chapters/6_conclusion.tex`
- **Section:** Dataset ethics and limitations
- **Reported by:** Reviewers 11 and 12

**Finding**

The dissertation analyzes public individual mobility traces but does not clearly discuss re-identification risk, terms
of use, ethical review/waiver status, aggregation safeguards, or misuse risk.

**Why it matters**

Public availability does not eliminate privacy risk. A committee may reasonably ask why individual trajectories were
ethically acceptable to process and publish.

**Recommended action**

Add a concise factual ethics/data-governance statement based on the actual source terms and institutional determination.
Do not invent an IRB/CEP approval or exemption.

**Author response**

> I agree with the claude take, mainly in the new section about governance and data ethics.

**Claude take (2026-07-24) — CONFIRMED, and the gap is total. It extends past the dissertation into the dataset
registry.**

A grep of all nine chapter files for `ethic|privacy|re-identif|anonym|consent|GDPR|LGPD|IRB|licen[cs]e|CC0|terms of use`
returns four hits, and **all four are the verb "license"** ("the test that licenses the verb outperforms"). There is not
one rendered sentence on ethics, privacy, re-identification, consent, or data licensing in a dissertation whose entire
object is per-user movement traces.

The one piece of provenance that exists is a **hidden LaTeX comment**, `5_mobiwac.tex:284`, recording the Figshare CC0
dump and the measured date range. That matters for a second reason the review does not raise: the chapter *cites*
`cho2011gowalla` (SNAP) while the ETL actually consumes the Figshare dump. The comment says so; the reader is never
told.

The supporting registry is thinner than the review assumed. `docs/context/DATASETS.md:187-199` records the Gowalla
source as SNAP and has **no `License` row at all** — the CC0 fact is nowhere under `docs/`. Massive-STEPS/Istanbul has
only `| License | Open-source; academic research |` (`:153`), which is a characterization, not an identified licence.
Neighbouring records do carry proper licence rows (Brightkite, Yelp), so this is a genuine omission in the science docs
too, not a house style.

**Why this is yours alone.** New prose asserting data provenance, licensing and privacy posture is precisely the class
of content your guardrails forbid an assistant from inventing, and the review is right that no CEP/IRB determination may
be fabricated. What I can say is that the missing inputs are small and concrete: the Figshare licence identifier, the
Massive-STEPS licence terms, and whether your institution requires a CEP determination for secondary analysis of public
de-identified traces. With those three facts a short, factual data-governance paragraph writes itself — and a banca is
far more likely to ask why it is absent than to challenge it once present.

**Resolution notes**

> _Record the verified ethical basis and safeguards here._

## 11. Reviewer Agreements and Disagreements

### Strong agreements

- Reviewers 09 and 11 independently identified the future-edge/category-feature leakage mechanism in Check2HGI; direct
  code tracing confirmed it.
- Reviewers across methods, MTL, mobility, cold-read, and committee perspectives agreed that same-fold checkpoint
  selection is not a clean confirmatory protocol.
- Reviewers 07, 09, 10, 11, and 12 agreed that the encoder-isolation result does not establish cross-task transfer.
- Multiple reviewers independently found the universal user-disjoint protocol statement false, Chapter 3 task
  terminology unstable, and the Chapter 3 prose below the rest of the dissertation.
- Compliance and visual reviewers agreed that front matter and measurable right-margin violations block final
  submission.

### Reconciled disagreements

- Reviewer 17 rated the dissertation close to outstanding on unity, originality, and narrative. That judgment is
  reasonable **conditional on the empirical result being valid**. REV-001–REV-003 prevent using the award-level
  assessment as the current readiness verdict.
- Reviewer 08 treated all deviations from the CoUrb source package as blockers. Consolidation downgrades omitted
  abstract/acknowledgment material and added analytical lead/caption text to Moderate, provided the dissertation says it
  reproduces the article body and the adaptation ledger is complete. The translated scientific body and numeric errata
  otherwise pass.
- Reviewer 06 treated the Chapter 3/4 dataset counts as an outright blocker. The 24 July author ruling and ETL audit
  resolve the values: Chapters 3/4 use the CoUrb figures of record, while Chapter 5 uses a distinct CC0 Figshare
  snapshot. Consolidation keeps the issue Open only because this difference is not explained to the reader and stale
  governance text remains.
- Reviewer 16 discussed external AI-detector risk. No detector score was available, and detector output would not
  establish authorship. Only its repository-verifiable findings—premature approval claims, incomplete tool/task
  disclosure, and missing human sign-off—are included as actionable issues.
- Reviewer 14 is intentionally not a manuscript reviewer; it evaluates proposed edit batches. With no edit batch in this
  first pass, “not applicable” is the correct independent outcome.

## 12. Prioritized Action Plan

### Phase 0 — Freeze claims and preserve evidence

1. Tag or archive the current PDF, code commit, configs, logs, and result files.
2. Do not polish headline claims until REV-001–REV-003 are resolved.
3. Create one authoritative experiment/result manifest; do not overwrite historical artifacts.

### Phase 1 — Resolve scientific validity

1. Rebuild Check2HGI causally and rerun the full Chapter 5 pipeline (REV-001).
2. Decide whether Chapters 3/4 are reconstruction or unknown-category tasks; rerun target-blind if the latter (REV-002).
3. Introduce untouched test evaluation or nested/inner validation and rerun comparisons (REV-003).
4. Verify/retract Nash and invalid balancer results (REV-005, REV-011).

### Phase 2 — Recompute inference and calibrate claims

1. Generate one synchronized statistical artifact and document deviations (REV-007).
2. Correct the inferential unit and repetition language (REV-014).
3. Reframe architectural gain versus cross-task transfer (REV-004).
4. Narrow CoUrb, A4, capacity, region, and external-baseline claims (REV-008, REV-009, REV-013, REV-015).

### Phase 3 — Repair coherence and reproducibility

1. Add the cross-study protocol matrix and dataset manifest (REV-006, REV-012, REV-016).
2. Correct Chapter 3 task definitions and annotate historical errors (REV-010).
3. Run a professional language edit on Chapters 3 and 4 (REV-017).
4. Correct HGI terminology and citation metadata (REV-019, REV-020).
5. Add the verified ethics statement (REV-026).

### Phase 4 — Submission production

1. Complete front matter and administrative prerequisites (REV-023).
2. Fix margins, reference font, figure language/accessibility, float placement, and abstract length (REV-018, REV-021,
   REV-022, REV-024, REV-029).
3. Replace the premature AI-approval claim with an exact, signed-off disclosure (REV-025).
4. Rebuild both variants, inspect every rendered page, rerun bibliography/reference checks, and obtain advisor sign-off.

## 13. Questions for the Author

### Repository answer audit of the original questions

| #  | Original question                                          | Repository determination                                                                                                                                                                                                                                                                                                                   |
|----|------------------------------------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 1  | Bidirectional edges and causal rerun                       | **Partly answered.** Bidirectional edges are implemented, but no rationale or causal/future-masked canonical rerun is committed. Earlier embedding audits already detected a forward-neighbour category channel and deferred its closure.                                                                                                  |
| 2  | Reconstruction/probing or unknown-category classification? | **Answered.** Chapters 3/4 intend target-blind unknown-category classification. The category-derived inputs conflict with that intended estimand.                                                                                                                                                                                          |
| 3  | Untouched test/checkpoint rule?                            | **Answered.** None is documented; Chapter 5 explicitly reserves no third split and reports validation-selected checkpoints on the held-out fold.                                                                                                                                                                                           |
| 4  | Is MobiWac final?                                          | **Answered with scope.** The v17 headline board is declared complete at n=20 for all six datasets. The Arizona ceiling top-up was deliberately dropped; joint-best CA/TX T6 is complete. Only the narrower T7 camera-ready joint-best inferential regeneration and non-verdict baseline/documentation chores remain.                       |
| 5  | Authoritative datasets/counts?                             | **Answered.** Chapters 3/4 use the CoUrb snapshot/ETL (Florida 990,518 check-ins, 20,301 users, 65,009 POIs). Chapter 5 intentionally uses a distinct CC0 Figshare Gowalla dump/ETL (Florida 1,407,034 check-ins, 21,052 users, 76,544 POIs). The 24 July ruling is recorded as final.                                                     |
| 6  | Advisor/program approvals?                                 | **Partly answered.** The author selected English, full CoUrb inclusion/translation, the article-status wording, and a working title. Advisor/Comissão confirmation remains pending for the English frame, CoUrb inclusion, final title, and adopted errata policy.                                                                         |
| 7  | Defense date, committee, checklist?                        | **Partly answered.** The current rule set is identified (Manual 04/2026, general rules 2019, PPGCC regulation 09 July 2026), but the stored defense/pre-textual checklists are from 2024. Date and committee remain placeholders; the August dates are planning estimates only.                                                            |
| 8  | Human approval and exact AI tools/models?                  | **Partly answered.** End-to-end human sign-off is not complete. Claude's task scope is documented; exact drafting/translation versions are unavailable. The first 18-persona review suite is exactly `claude-opus-4-8`; the present review used Codex/OpenAI. Advisor approval of the disclosure is absent.                                |
| 9  | Ethics/data-use determination?                             | **Partly answered.** Public-source provenance is known, including CC0 for Chapter 5 Gowalla, but no CEP/IRB determination is committed and the exact Massive-STEPS terms still need verification.                                                                                                                                          |
| 10 | Correction policy for published prose?                     | **Answered, pending advisor confirmation.** Apply sanctioned corrections in the re-typeset chapter/global bibliography, list every content departure in per-article ERRATA/Appendix B, and never edit the published record. Historical scientific reinterpretations are time-indexed in a preface/footnote rather than silently rewritten. |

### Inputs still required from the author or advisor

1. Does any uncommitted causal/future-masked Check2HGI result or written rationale for bidirectional temporal edges
   exist outside the repository? If not, decide whether to run the causal rebuild or withdraw/suspend the affected
   claims.
R: No, you cna try to run in the nespdgpu
2. Can the original Chapter 3 split manifest/logs and the missing Chapter 3/4 selection/tuning records be recovered from
   the linked external repositories, old machines, or collaborators?
R: Kind, but I already give any extra information in my above takes.
3. Can `al_capmatch_summary.json` and the unfinished California capacity job
   `4cff4b00` be recovered from the A40 work directory, or should California remain explicitly partial?
R: Yes, and we already make. but you have acess through the nespedgpu.
4. Please obtain one bundled advisor/Comissão decision on the English frame, full translated CoUrb chapter, final title,
   two-page Resumo, and ERRATA policy.
R: 
5. Provide the booked defense date and committee, and ask the secretariat which checklist/Article 21 interpretation is
   operative under the 09 July 2026 regulation.
R: 
6. Has the author now read and approved every rendered passage and the added CoUrb framing/caption text? Which exact AI
   model versions can the author independently verify for drafting, translation, and editing, and does the advisor
   approve the disclosure?
R: 
7. Obtain or record the institutional CEP/IRB determination, verify the source terms for Massive-STEPS and the Chapters
   3/4 Gowalla snapshot, and state the actual privacy safeguards.

## 14. Author Responses and Resolution Tracking

Use this table as the high-level gate; detailed responses belong under each finding.

| ID      | Owner | Target date | Status             | 2nd opinion (Claude) | Evidence / commit / artifact                                                               |
|---------|-------|-------------|--------------------|----------------------|--------------------------------------------------------------------------------------------|
| REV-001 |       |             | Open               | ⚠️ Author            |                                                                                            |
| REV-002 |       |             | Open               | ⚠️ Author            | Intended estimand recovered from Chapters 1, 3, and 4                                      |
| REV-003 |       |             | Open               | 🔧 Mechanical        |                                                                                            |
| REV-004 |       |             | Open               | ✅ Closed            |                                                                                            |
| REV-005 |       |             | Open               | ⚠️ Author            |                                                                                            |
| REV-006 |       |             | Open               | 🔧 Mechanical        |                                                                                            |
| REV-007 |       |             | Open               | ⚠️ Author            |                                                                                            |
| REV-008 |       |             | Open               | 🔧 Mechanical        |                                                                                            |
| REV-009 |       |             | Open               | 🔧 Mechanical        |                                                                                            |
| REV-010 |       |             | Open               | 🔧 Mechanical        |                                                                                            |
| REV-011 |       |             | Open               | 🔧 Mechanical        |                                                                                            |
| REV-012 |       |             | Open               | ⚠️ Author            |                                                                                            |
| REV-013 |       |             | Open               | ⚠️ Author            |                                                                                            |
| REV-014 |       |             | Open               | 🔧 Mechanical        |                                                                                            |
| REV-015 |       |             | Open               | ✅ Closed            |                                                                                            |
| REV-016 |       |             | Open               | 🔧 Mechanical        | 24 July author ruling + `cbic_recompute_result.md`; reader-facing explanation still needed |
| REV-017 |       |             | Open               | ⚠️ Author            |                                                                                            |
| REV-018 |       |             | Open               | ⚠️ Author            |                                                                                            |
| REV-019 |       |             | Open               | 🔧 Mechanical        |                                                                                            |
| REV-020 |       |             | Open               | 🔧 Mechanical        |                                                                                            |
| REV-021 |       |             | Open               | 🔧 Mechanical        |                                                                                            |
| REV-022 |       |             | Open               | ⚠️ Author            |                                                                                            |
| REV-023 |       |             | Needs author input | ⚠️ Author            |                                                                                            |
| REV-024 |       |             | Open               | ⚠️ Author            |                                                                                            |
| REV-025 |       |             | Needs author input | ⚠️ Author            |                                                                                            |
| REV-026 |       |             | Needs author input | ⚠️ Author            |                                                                                            |
| REV-027 |       |             | Open               | 🔧 Mechanical        |                                                                                            |
| REV-028 |       |             | Open               | 🔧 Mechanical        |                                                                                            |
| REV-029 |       |             | Open               | 🔧 Mechanical        |                                                                                            |

**Submission gate:** Do not change the overall disposition to “ready” until REV-001–REV-003 are resolved with auditable
evidence and the resulting claims/statistics are regenerated. Administrative readiness additionally requires REV-021,
REV-023, REV-024, and REV-025 to be resolved.

## 15. Strengths of the Dissertation

- The dissertation has a genuine intellectual arc rather than a loose bundle of papers: an initial null result motivates
  a representation diagnosis, followed by a stronger model and explicit follow-up controls.
- Negative and inconvenient results are reported unusually well: transition-prior leakage, CTLE epoch behavior,
  feature-concatenation controls, partial external baselines, the Alabama deficit, and the cascade qualification all
  increase credibility.
- Article-status prefaces and the time-capsule approach make the evolution of the research legible and should be
  preserved.
- Chapters 1, 2, 5, and 6 are generally clear, controlled, and appropriately technical.
- The joint system, coverage-aware baselines, representation audits, and capacity control show a serious attempt to
  separate performance from easy explanations, even though the remaining leakage and selection paths must now be
  addressed.
- The bibliography is structurally healthy: all cited keys resolve, no duplicate keys were found, and the needed
  citation repairs are targeted.
- The rendered dissertation has a consistent overall visual identity and a length/organization comparable to the strong
  local reference dissertations.
- The repository contains substantial decision records, experiment notes, and Portuguese reasoning artifacts. With one
  authoritative manifest and honest sign-off, these can become a strong reproducibility and provenance package.

The dissertation is therefore best described as **scientifically promising and structurally strong, but not yet
evidentially or administratively ready for submission**. The fastest route to a defensible final document is to validate
the representation and evaluation pipeline first, then rewrite the claims around the results that survive.


---

<!-- estado-rodada -->
> **Rodada encerrada · último toque 2026-08-28 · sem autoridade.**
> Este ficheiro é registo de proveniência do que foi discutido nesta passagem, não fonte
> de um facto corrente. O que ficou decidido está em [`VEREDITOS.md`](../../../../VEREDITOS.md);
> os valores entregues estão em `CLAUDE.md` §0.1. Não copie nada daqui sem confirmar lá.
