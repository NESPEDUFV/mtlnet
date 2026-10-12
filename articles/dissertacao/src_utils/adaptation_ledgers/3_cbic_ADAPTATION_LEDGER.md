# ADAPTATION LEDGER — Chapter 3 (CBIC 2025 re-typeset)

> Source of record: `articles/CBIC___MTL/` (main.tex + sections/{intro,basis,method,results,
> conclusion}.tex + tables/ + imgs/), published at CBIC 2025, DOI 10.21528/CBIC2025-1191324.
> Target: `articles/dissertacao/src/chapters/3_cbic.tex`.
> Every departure from the published text is listed here (feeds Appendix B; reconciliation
> gate: fixes applied == fixes listed). Citation errata #1–#9 in `articles/CBIC___MTL/ERRATA.md`
> are Phase-4 bibliography work and are NOT applied here; all \cite keys kept as-is.

## A. Structural re-typeset changes (format only, no content change)

| # | Change | Where |
|---|---|---|
| A1 | Abstract and IEEEkeywords dropped (coletânea chapters carry no abstract; NORTH_STAR §3). The Acknowledgment section is also not carried (see A10). **Round 4 (REV-028):** the omission was recorded but never told to the reader; Appendix B's opening now states it for all three chapters at once. Verified 2026-07-26 in `articles/CBIC___MTL/main.tex`: abstract :43-45, IEEEkeywords :47-49, `\section*{Acknowledgment}` :77-78. | whole chapter |
| A2 | Paper `\section` levels became `\section` under the `\chapter`; labels renumbered to the chapter-prefixed scheme: `sec:related → sec:cbic:related`, `sec:methodology → sec:cbic:methodology`, `sec:mtl → sec:cbic:mtl`, `sec:method:mtl → sec:cbic:mtlarch`, `sec:nash_mtl → sec:cbic:nash`, `sec:experiments → sec:cbic:experiments`, `sec:conclusion → sec:cbic:conclusion`, `fig:arch → fig:cbic:arch`, `eq:loss → eq:cbic:loss`, `eq:nbs_objective → eq:cbic:nbs`, `table:cat → tab:cbic:category`, `table:next → tab:cbic:next`, `table:convergence_comparison → tab:cbic:convergence`. | whole chapter |
| A3 | "this paper" → "this chapter" (4 instances: §Intro "In this work, we investigate" → "In this chapter"; "contributions of this paper" → "of this chapter"; "The rest of this paper is organized" → "of this chapter"; §Method "This work computes" → "This chapter computes"; §Conclusion "In this paper, we introduced" → "In this chapter"). | intro, method, conclusion |
| A4 | Italic time-capsule preface added before §3.1 (`chapterpreface` environment): venue in full, DOI, first author, of-the-time framing, pointer to Chapters 4–5, one clause on the later Nash-MTL implementation finding (sanctioned by NORTH_STAR §4 Ch.3 claim-discipline note). Not part of the published text. | chapter opening |
| A5 | `IEEEeqnarray` (2-col line-broken DGI loss) reflowed to a single-line `equation` for 1-col; content identical. `\argmax` (paper-preamble macro) → `\operatorname*{arg\,max}` inline. `\resizebox` wrapper around the parameter-partition display removed (not needed at 1-col); the Θ_specific set line-broken for width. | method |
| A6 | Tables converted from vertical-ruled `tabular` + `\resizebox` to booktabs (no vertical rules), captions moved ABOVE tables (WRITING_LAW §5), captions rewritten as self-contained descriptions naming metric, spread convention, and bolding convention (original captions: "Table comparing the results of ..."). Cell values, bolding, and underlining copied verbatim from the published tables (see B7 for the one bolding-convention note). `{\ul ...}` (ulem) → `\underline{...}`. | results tables |
| A7 | Lead takeaway sentence added before the convergence table ("The convergence measurements show a clear wall-time disadvantage...") per WRITING_LAW §5 (tables introduced by a lead sentence); the two results tables were already introduced by the paper's own discussion paragraphs. | results |
| A8 | Figure: `figure*` (2-col span) → `figure`; `imgs/mtlnet_poi.drawio.png` copied to `figures/cbic_mtlnet_arch.png`; placed at `\textwidth` (the paper's figure* also spanned the full page width, so this is not a stretch; bitmap is 1200 px wide, ~200 dpi at text width — acceptable for a diagram, but flag: a TikZ/drawio re-export at higher resolution would be better; sources `mtlnet_poi_horizontal.drawio` / `_vertical.drawio` exist in `articles/CBIC___MTL/imgs/`). | method figure |
| A9 | Em-dashes and free-standing en-dashes removed per WRITING_LAW §1: challenge-list separators ("Negative Transfer — Unrelated..." etc.) → colons; parenthetical en-dashes in intro ("POIs – specific physical locations ... –") → commas; "Nash–MTL" heading → "Nash-MTL"; "$p_1$–$p_9$" → "$p_1$--$p_9$" (range en-dash kept in TeX form). | intro, basis, method |
| A10 | Commented-out draft blocks (old intro draft, section to-do notes in PT, commented citations) not carried over. Acknowledgment section not carried (frame-level matter). | whole chapter |

## B. Errata applied silently in the text (ERRATA.md non-citation set; each also lands in Appendix B)

| # | Erratum | Applied fix |
|---|---|---|
| B1 | Unfilled dataset placeholders `N_users`, `N_poi`, `N_checkins` in results.tex. | NOT invented. Rendered as visible placeholders "[$N_{\text{users}}$; VERIFY: recompute per ERRATA.md]" (same for poi/checkins) + a % comment block naming the sanctioned path (repo-committed recompute script over the CBIC-era Florida pipeline, author-approved; CoUrb FL row is cross-check only). **AUTHOR ACTION REQUIRED before handoff.** |
| B2 | Prose "almost four times more wall time" contradicts table (80.88 s vs 34.97 s = 2.3×). | Reconciled to the table: "required 80.88 s of wall time, about 2.3 times the cumulative 34.97 s of the individual single-task models." Values 80.88/16.26/18.71 from the published table; 34.97 and 2.3× quoted from ERRATA.md (not agent-computed). |
| B3 | Prose MFLOPs "roughly double" contradicts the table (MTL 0.234 vs Category 2.315 + Next 0.012). | Reconciled to the table: prose now states the table does not show a higher MFLOPs cost for MTL and quotes the three cell values verbatim. Follow-on edits for consistency: "incurred a significantly higher overhead in both time and computational resources" → "in wall time"; "where convergence speed and computational efficiency are critical factors" → "where convergence speed is a critical factor"; "a more convenient and resource-efficient strategy" → "a more convenient strategy"; §Conclusion "higher computational demands in terms of convergence time and MFLOPs" → "in terms of convergence wall time". |
| B4 | Broken cross-ref: `\label{sec:method:single_task_heads}` sat on the Dataset subsection, and method.tex pointed to it as if it described the task heads. | Dataset subsection relabeled `sec:cbic:dataset`; the dangling pointer sentence in §Method ("as detailed in Section~\ref{sec:method:single_task_heads}") dropped: "passed to dedicated, unshared task-specific heads. These heads generate...". No section describing single-task heads exists in the published paper, so no target could be substituted. |
| B5 | Typo "spatio-tegm\nmporal" in basis.tex. | → "spatio-temporal". |
| B6 | Nash-MTL claim discipline (NORTH_STAR §4). | The paper's own §Method sentence ("Nash-MTL consistently yielded a better overall performance") is preserved verbatim as published text; NOT amplified anywhere; the preface carries the one-clause of-the-time caution. |
| B7 | (Noted, not an ERRATA.md item) The published category table bolds the better of MTL/Single per row and never bolds HMRM, even where HMRM is numerically highest (Recall/Nightlife: HMRM 42.13 > Single 36.77 bold). Emphasis preserved exactly as published; the new caption states the convention explicitly so the bolding is not misread as "best per row". | tab:cbic:category |
| B8 | **NEW round 4 (REV-020a).** Factual correction in §3.3.4 Nash-MTL Optimizer, "Practical Aspects" paragraph (3_cbic.tex:237). Published (`sections/method.tex`): "Its reliance on gradient signs rather than scales inherently balances heterogeneous tasks without manual re-weighting." Nash-MTL does not read gradient signs; it is scale-invariant, which the SAME subsection states earlier at :224 ("scale-invariant to arbitrary loss re-weightings"), so the published text contradicted itself. | Chapter: "Its invariance to the scale of the individual task gradients, the second of the axioms listed above, balances heterogeneous tasks without manual re-weighting." Claim strength REDUCED (a mechanism claim is replaced by the property the source proves). Verified three ways 2026-07-26: (a) Navon et al., *Multi-Task Learning as a Bargaining Game*, arXiv:2202.01017 (PDF opened this session): Axiom 2.4 "Invariance to affine transformation" and the Fig. 1 discussion ("Our method, Nash-MTL, is invariant to changes in loss scale"); the token "sign" occurs in that paper **only** inside a bibliography entry for an unrelated method (gradient sign dropout, Chen et al. 2020). (b) `/Users/vitor/Desktop/mestrado/temp/tarik-new/PoiMtlNet_Novo/src/criterion/nash_mtl.py`: **zero** occurrences of `sign`/`abs`; `get_weighted_loss` (:176-232) stacks per-task gradients into G, forms `GTG = torch.mm(G, G.t())` (:222), divides by the Frobenius norm (:224-227) and solves for alpha (:228). (c) This repo's `src/losses/nash_mtl/loss.py`: same structure at :291-299, also **zero** `sign`. Declared as row 6 of Appendix B Table B.1 |
| B9 | **NEW 2026-09-02 (B-13).** Scope defect in §3.4.2.1, the sentence at `3_cbic/results.tex:125`. Published (`sections/results.tex:29`): “both our MTL and Single models significantly outperform HMRM across all POI categories in terms of F1-score, precision, and recall.” The table the sentence cites holds 21 cells and HMRM is the highest in one of them — **Recall / Nightlife: HMRM 42.13 ± 3.28 vs Single 36.77 ± 5.86 and MTL 25.80 ± 3.54**, **Corrected 2026-09-02 before the commit landed in the deposit:** an earlier draft of this entry, of the Table B.1 row and of `CBIC___MTL/ERRATA.md` claimed the gap was "wider than the standard deviations". False. 42.13 - 36.77 = 5.36 against the single-task model's sd of 5.86, so it sits inside it; only the gap over the joint model (16.33 vs sd 3.54) clears its own. It was also an inferential claim inside a chapter that runs no inferential test, which contradicts the B.2 row on "significantly". The defect stands without it: the prose says HMRM is never highest, the table prints it highest once. ⚠ **The cell was already on record and the consequence was not**: B7 above logs this exact comparison in round 4, while fixing how the caption explains the table's bolding, and nobody carried it back to the prose fifteen lines earlier. Surfaced again because a banca reader highlighted the sentence on the delivered PDF (`wrapup/REVISAO_BANCA_PDF.md`, B-13, 26/08 10:16, no written comment); author-confirmed 2026-09-02 after checking the cell himself. | Chapter: “outperform HMRM \cite{chen2020modeling} in every POI category in terms of F1-score and precision, and in every category except Nightlife in terms of recall.” Claim strength REDUCED, in the baseline's favor — same discipline as B2/B3 (reconcile the prose **to** the table). The rest of the paragraph is untouched and checks out: the Shopping 62.51/46.69 and Food 57.43/28.44 examples are both F1 cells. Verified four ways 2026-09-02: (a) `src/tables/cbic/category.tex:30`; (b) the published `CBIC___MTL/tables/category_result.tex:25`, identical values and identical column order MTL│Single│HMRM, so the chapter reproduces the published table faithfully and the defect is the article's; (c) `banca.pdf` as rendered, p.48; (d) a mechanical parse of all 21 cells — 20 confirm the claim, HMRM is lowest in all 14 F1 and precision cells. **SECOND EDIT TO ONE PUBLISHED SENTENCE**: Table B.2 already carries it for dropping “significantly” and “across all” → “in every”; that row's right column was re-quoted in the same commit so the appendix stops describing chapter text that no longer exists. Declared as row 11 of Appendix B Table B.1 (`src/tables/cbic/errata.tex`), with `apx_b_errata.tex` counts B.1 10→11 and Total 55→56, both measured by `count_errata_rows.py` before being written. Also logged in the article's own `CBIC___MTL/ERRATA.md`. |

## C. Writing-law substitutions in preserved prose (minimal, lint-gate-driven; WRITING_LAW §4 banned words)

| # | Original (published) | Chapter text |
|---|---|---|
| C1 | "By leveraging shared information, MTL can potentially mitigate..." (intro) | "By using shared information, ..." |
| C2 | "solutions that leverage shared representations across related POI tasks" (basis) | "solutions that use shared representations..." |
| C3 | "by leveraging shared information across correlated tasks" (basis §MTL-in-POI) | "by sharing information across correlated tasks" |
| C4 | "Moreover, we utilize a Deep Graph Infomax..." / "Moreover, $\mathcal{D}$ is a discriminator..." (method) | "In addition, ..." (both) |
| C5 | "These findings underscore that..." (conclusion) | "These findings indicate that..." |
| C6 | "Furthermore, investigating advanced multi-task optimizers..." (conclusion) | "In addition, investigating..." |
| C7 | "Furthermore, the computational cost ... was roughly double" (results) | superseded by erratum B3 rewrite |
| C8 | "where different sequential patterns might be leveraged" (results) | "might be exploited" |
| C9 | **NEW round 4 (REV-027).** "the MTL framework does not deliver the consistent, significant gains often expected" (intro, 3_cbic.tex:62) | "does not deliver the consistent gains often expected" |
| C10 | **NEW round 4 (REV-027).** "both our MTL and Single models significantly outperform HMRM ... across all POI categories" (results, :302) | "both our MTL and Single models outperform HMRM ... in every POI category" |
| C11 | **NEW round 4 (REV-027).** "significantly surpassing MHA+PE in these categories" (results, :340) | "surpassing MHA+PE in these two categories" |
| C12 | **NEW round 4 (REV-027).** "suggesting that, statistically, the performance of the MTL and Single models is largely comparable, without a clear, consistent, and significant advantage" (results, :377) | "suggesting that the performance of the MTL and Single models is largely comparable, without a clear or consistent advantage" |
| C13 | **NEW round 4 (REV-010).** "Next-POI Prediction, in contrast, aims to predict which specific location a user is likely to visit next, given their past movement history." (related work, :81; published `sections/basis.tex`:23) | Sentence reproduced VERBATIM; a footnote was appended: "This states the general formulation of the task as the literature poses it. The variant studied in this chapter predicts the *category* of the next visited place rather than the place itself, as defined in Section 3.1 and in the chapter preface." |
| C14 | "MTL allows the learning of complementary objectives simultaneously, allowing for more accuracy." | "MTL allows complementary objectives to be learned simultaneously, which can improve accuracy." |
| C15 | "Some Models such as TME ... but treat prediction and classification separately." | "Some models, such as TME, ... but treat prediction and classification separately." |
| C16 | "jointly performs POI category prediction and next-POI classification" | "jointly performs POI category classification and next-category prediction" (the published sentence had the two task operations reversed). |
| C17 | "enabling more robust predictions even in data-sparse environments" | Removed because the study did not evaluate robustness as a function of data sparsity. |
| C18 | "We hypothesize three primary factors contributed to this outcome" | "We hypothesize that three primary factors contributed to this outcome." |

**REV-027 scope note (round 4).** The chapter uses "significant/significantly" twelve times and
reports no inferential test anywhere: a grep for `p-value|p value|Wilcoxon|t-test|Holm|TOST|
confidence interval|statistical` over `3_cbic.tex` returned only :62 and :377, both of which
appealed to the word without naming a test and both of which are now corrected. Four uses were
substituted (C9-C12), all attaching significance to THIS study's own measured comparisons.
Untouched, with reasons: :90 and :209 attribute claims to cited work (Xu/Lim et al.; Caruana);
:60 states the study's own *hypothesis* ("will face significant limitations"), which is a
prediction about the outcome rather than a claim that a measured difference was tested, so
lowering it would misreport what the paper hypothesized; :68 makes a claim about task
dissimilarity, not about a measured comparison; :237 states a property of Nash-MTL attributed to
`\cite{nash}`; :395 names a chosen target F1 level ("a comparable and significant level of
predictive performance"), not a comparison. Two further uses are borderline and were LEFT AS
PUBLISHED pending the author's call, since neither was in the approved set of four: :414 ("a
significantly higher overhead in wall time", a magnitude reading of the chapter's own 80.88 s
against 34.97 s) and :423 ("the lack of significant improvement", restating the null result).
**Chapter 4 contains ZERO occurrences of "signific*" (confirmed 2026-07-26) and needed nothing.**

**Preface pointer fix (round 4, NEW-4).** 3_cbic.tex:25-27 said the chapter's preference for
Nash-MTL is "a conclusion of the time ... and the following chapters do not rely on it". False
for Chapter 4, which trains with the Nash-MTL balancer (`4_courb.tex`:115, and :84 for the
MTLnet baseline). Corrected to name Chapter 5, which reports a fixed loss weighting and states
that no balancer, Nash-MTL included, improved on it (`5_mobiwac.tex`:180-186). This sentence is
dissertation-authored preface prose (ledger row A4), NOT reproduced published text, so it takes
**no** Appendix B errata row. Per the author's ruling this round, no Nash caveat was added to
Chapter 3 or Chapter 4 beyond this pointer fix.

## D. [VERIFY] / [NEEDS SIGN-OFF] items

1. **[VERIFY — blocks handoff]** B1 dataset statistics: `N_users`, `N_poi`, `N_checkins` must be
   recomputed by the sanctioned repo script and author-approved before the placeholders are
   replaced. Visible in the rendered PDF by design.
2. **[NEEDS SIGN-OFF]** B4: the dangling task-heads cross-reference was resolved by deletion
   (no valid target exists in the published paper). Alternative: point to §3.3.2 (the MTL
   architecture's task-heads paragraph) if the author prefers a pointer over deletion.
3. **[NEEDS SIGN-OFF]** Preface wording, in particular the Nash-MTL clause ("weakened by a
   later finding about the optimizer implementation") — the solver-bug detail (repo memory
   2026-04-10) is deliberately not spelled out; confirm the level of specificity wanted.
4. **[FLAG]** A8: `cbic_mtlnet_arch.png` is a 1200×336 px bitmap (~200 dpi at text width).
   Legible, but a higher-resolution re-export from the .drawio sources would be better for the
   final build.
5. **[RECOMMENDATION, round 4 — author's call, NOT applied]** The same sentence corrected in B8
   also claims Nash-MTL "requires only two matrix-vector products per iteration" (3_cbic.tex:237).
   The phrase does not occur in Navon et al. (arXiv:2202.01017, full text searched this session),
   and the claim understates the per-step cost: both implementations run an iterative
   concave-convex procedure with `optim_niter = 20` by default, each pass a cvxpy/ECOS solve
   (`temp/tarik-new/PoiMtlNet_Novo/src/criterion/nash_mtl.py`:99 and :126-141; this repo's
   `src/losses/nash_mtl/loss.py`:105 and :158-200). The paper itself reports that raising the CCP
   sequence to 20 iterations lifts the share of optimal solutions from 91.5% to 93.5%, and it
   devotes §3.3 ("Practical Speedup") to the cost of the step. Whether to correct a published
   cost claim is a judgment call, so it was left as published and raised in the handoff instead.
6. **[BIBLIOGRAPHY-ADJACENT FINDING, round 4 — reported, not acted on; references.bib is another
   track's file]** 3_cbic.tex:108 cites `\cite{nash,standley2020tasks}` for the "Data
   Heterogeneity" challenge ("Variations in modality, label granularity, and dataset size
   complicate sampling strategies and minibatch construction"). Navon et al. do **not** establish
   that: the tokens "modalit", "minibatch", "heterogen", "dataset size", "label granular", and
   "sampling" return **zero** hits in the full text of arXiv:2202.01017 (checked this session).
   That paper is about gradient conflict and the bargaining solution, not about data
   heterogeneity. The co-cite `standley2020tasks` (*Which Tasks Should Be Learned Together in
   Multi-Task Learning?*) is the plausible support for a task-grouping claim, though it was not
   opened this session. Recommendation for the references track: either drop `nash` from this
   particular co-cite, or re-source the sentence. No bib entry was added or changed here.
7. **[NOTE]** Citation errata #1–#9 (ERRATA.md) untouched here; keys `velivckovic2017graph`,
   `velivckovic2018deep`, `nash`, `yu2019mmoe`, `chen2020modeling`, `misra2016cross`,
   `zhang2021survey` etc. appear in this chapter exactly as in the paper and await the Phase-4
   global bib merge.

## E. Numbers ledger (every numeral in the chapter → source)

All performance numbers (per-category F1/precision/recall means ± std, both tables) and all
convergence cells (16.26 / 18.71 / 80.88 s; 3.8 / 3.2 / 3.2 epochs; 2.315 / 0.012 / 0.234
MFLOPs) are copied verbatim from `articles/CBIC___MTL/tables/{category_result,next_result,
converge_result}.tex`. In-prose numbers (62.51±0.94, 46.69±0.81, 57.43±1.46, 28.44±0.42,
53.11±0.58, 47.75±0.89, 43.47±0.50, 43.53±1.66, 64.61±1.11, 22.07±0.52, 26.06±1.01,
22.45±0.81, targets 47 and 32.2) are verbatim from `sections/results.tex`. 34.97 s and 2.3×
are quoted from `articles/CBIC___MTL/ERRATA.md` (sanctioned reconciliation), not computed by
the agent. Method constants (64-d, L_h=9, 9×64=576, seven categories, 5-fold, <5 visits)
verbatim from `sections/method.tex` and `sections/results.tex`. Hardware/software footnote
verbatim from `sections/results.tex`. Dataset counts: placeholders only (B1).
