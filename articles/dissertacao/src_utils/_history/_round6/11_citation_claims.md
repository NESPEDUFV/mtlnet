# 11_citation_claims.md — the per-chapter citation claim-support audit, consolidated

**Round 6, 2026-07-28.** Written against the live source tree; PDFs rebuilt after the two
bibliography edits of ITEM 2 (`tex_errors=0`, 0 overfull boxes, 105/100 pp; see section 7).

This report covers the three items of the task: the per-chapter claim-support pass the author
asked for by name under COD-008 (ITEM 1), the two preprint-to-version-of-record bibliography
upgrades (ITEM 2), and the Standley citation audited against its own commit history (ITEM 3).

---

## 0 · How this was run, and one deviation to declare

**Deviation.** The task specifies dispatching one sub-agent per chapter with `host.delegate`.
`host.delegate` is **not available in this frame** — it is root-only and this frame is a leaf, so
the call raises rather than dispatching. I ran every unit myself instead, unit by unit, over the
whole citation surface rather than a sample. The per-chapter reports the task names were still
written, one per unit, and each carries its own counts, verdict table and source ledger. What is
lost by not fanning out is the independence of a fresh-eyes reader per chapter (AGENT_GUARDRAILS
L6); what is kept is that no unit was sampled and every verdict traces to a source I opened.
**The author should treat this report as one auditor's pass, not seven.**

**Method, in the order it ran.**

1. **Measured the surface.** Parsed all eleven chapter files plus `0_main.tex` and the six
   `\input` table files, stripping `%` comments so only rendering sites count. Matched
   `\cite`, `\citep`, `\citet`, `\textcite`, `\parencite` and `\onlinecite`.
2. **Resolved every bibliography entry at its source of record.** 100 entries: Crossref REST
   for every DOI, the arXiv API for every arXiv identifier, OpenAlex (with the configured API
   key, never anonymously and never with a `mailto` parameter) for entries carrying neither, and
   Semantic Scholar for the abstracts Crossref does not deposit. Six references were read as
   full PDFs: five already in the repository at `science/articles/`, plus Caruana 1997 fetched
   open-access from Springer, plus Standley 2020 fetched from arXiv for ITEM 3.
3. **Screened every citing sentence** against the retrieved record and abstract. This screen is
   a triage instrument only; per AGENT_GUARDRAILS R5, AI output is not a source.
   **Two evidence strings fed to that screen were defective, and both are recorded in section 11.**
   For `wilcoxon1945` the string was JSTOR front-matter boilerplate rather than paper content, and
   for `huang2023hgi` it was empty (my text slice looked for a spaced `A B S T R A C T` header that
   the PDF does not use). Neither changed a verdict — the screen returned UNVERIFIABLE for all nine
   affected sites, naming the missing evidence, and the manual pass then read the actual PDF for HGI
   and closed Wilcoxon at record level — but the stored data was wrong and has been corrected.
4. **Verified by hand every site the screen did not clear**, plus every site whose verdict
   depended on a detail an abstract cannot carry. 38 sites were adjudicated against the sources
   directly; 15 more were closed by reading a paper body or a repository document. Six of the
   screen's flags were **overturned as false positives** and are recorded as such, because a
   later pass would otherwise re-raise them.
5. **Traced provenance** of every failure: whether the citing sentence is the author's own frame
   prose or verbatim reproduced article prose, by exact-string matching against
   `articles/CBIC___MTL/sections/`, `articles/CoUrb_2026/src_en/sections/` (and the PT source of
   record) and `articles/[mobiwac]/src/sections/`. This decides the errata regime for each row.

## 1 · Counts (measured, not sampled)

| Unit | `\cite` commands | Source lines carrying them | Key instances (audited) | Distinct keys | SUPPORTED | PARTIAL | NOT-SUPPORTED | UNVERIFIABLE |
|---|---|---|---|---|---|---|---|---|
| `1_introduction` | 8 | 8 | 9 | 9 | 8 | 1 | 0 | 0 |
| `2_fundamentals` | 69 | 69 | 70 | 67 | 70 | 0 | 0 | 0 |
| `3_cbic` | 57 | 37 | 64 | 31 | 49 | 8 | 6 | 1 |
| `4_courb` | 50 | 32 | 53 | 28 | 47 | 4 | 2 | 0 |
| `5_mobiwac` | 56 | 43 | 60 | 33 | 57 | 3 | 0 | 0 |
| `6_conclusion` | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| `appendices` | 7 | 7 | 9 | 9 | 9 | 0 | 0 | 0 |
| **total** | **247** | **196** | **265** | **100** | **240** | **16** | **8** | **1** |

**On the task's figure of 334 citation instances.** I measure **247 rendering `\cite` commands**
and **265 key instances** across the eleven units. The gap is accounted for and is not a
discrepancy in the document: raw `grep` over the same files finds 255 `\cite` commands and 273
comma-expanded keys, of which the difference is inside `%` comments (audit-trail notes that do
not render), plus 3 keys in `tables/frame/lineage.tex` (counted here under Chapter 2, which
`\input`s it) and one `\citebrackets` command in `0_main.tex` that is a style declaration, not a
citation. 334 does not correspond to any count I can reproduce over `src/`; the author should
treat 247/265 as the measured figure and this paragraph as the audit trail for it.

**Bibliography integrity, measured while resolving.** 100 entries, 100 distinct keys, **zero**
duplicate keys, **zero** cited-but-missing keys, **zero** uncited entries. 99 of the 100 resolve
at an external source of record; the one that does not is `santos2024urban`, a UFV master's
dissertation with no DOI, which I verified against the document itself (see section 4).

## 2 · The consolidated failure table, ranked by how load-bearing the claim is

Ranking is by what the claim carries in the document, not by verdict severity. A NOT-SUPPORTED
citation on a background bullet costs less than a PARTIAL on a sentence that motivates a design
choice. "Load" is my judgment and the author may re-rank it; the evidence for each row is in the
per-chapter report and the reasoning is in section 3.

| # | Load | Verdict | Site | Key | Regime | Recommended disposition |
|---|---|---|---|---|---|---|
| 1 | high | NOT-SUPPORTED | `3_cbic.tex:213` | `ruder2017sluice` | PUBLISHED, Appendix B row required | CHANGE THE CITATION. Swap to `baxter2000model`, which is already in the bibliography and is cited for exactly this claim at `4_courb.tex:116`. Appendix B row (published prose). |
| 2 | high | NOT-SUPPORTED | `3_cbic.tex:214` | `standley2020tasks` | PUBLISHED, Appendix B row required | NARROW THE PROSE. Draft sentence and Appendix B row in section 5 of this report. NEEDS-AUTHOR: it is a claim, not a typo. |
| 3 | high | NOT-SUPPORTED | `4_courb.tex:161` | `sun2020go` | PUBLISHED, Appendix B row required | NARROW THE PROSE. Drop the semantics half, or keep it and cite a source for it. `cho2011gowalla` supports temporal and spatial periodicity of visits; nothing in the bibliography supports temporal cycles revealing place FUNCTION. Appendix B row. |
| 4 | high | NOT-SUPPORTED | `4_courb.tex:219` | `belkin2003laplacian` | PUBLISHED, Appendix B row required | CHANGE THE CITATION. `Xu2023` (TME) regularizes category relatedness with a predefined category hierarchy, which is what this term does; it is already in the bibliography and cited in the same chapter. Or drop the citation and present the term as the implementation's own. Appendix B row. |
| 5 | high | PARTIAL | `5_mobiwac.tex:44` | `caruana1997multitask` | UNDER REVIEW, two-file change + article errata | ADD A SECOND CITATION. `standley2020tasks` states "this often leads to inferior overall performance as task objectives can compete", which is the mechanism the sentence describes; it is already in the bibliography and cited for this at `2_fundamentals.tex:310`. Two-file change (dissertation + `articles/[mobiwac]/src/`), then that article's errata record. |
| 6 | medium | NOT-SUPPORTED | `3_cbic.tex:97` | `zhang2021survey` | PUBLISHED, Appendix B row required | NARROW THE ATTRIBUTION. The five dimensions listed are `yu2024survey`'s five areas, renamed. Keep the list on `yu2024survey`; cite `zhang2021survey` for the survey framing only, or drop it here (it is cited three more times in the chapter). Appendix B row. |
| 7 | medium | NOT-SUPPORTED | `3_cbic.tex:114` | `nash` | PUBLISHED, Appendix B row required | NARROW THE PROSE or MOVE THE KEYS. Both keys are mis-slotted: they belong to the gradient-conflict bullet immediately above, where both are already cited. Either narrow the data-heterogeneity bullet to what these works support, or cite a survey that does treat heterogeneity. Appendix B row. |
| 8 | medium | NOT-SUPPORTED | `3_cbic.tex:114` | `standley2020tasks` | PUBLISHED, Appendix B row required | As the row above: same bullet, same disposition. |
| 9 | medium | PARTIAL | `3_cbic.tex:244` | `nash` | PUBLISHED, Appendix B row required | LEAVE AND RECORD as a `[VERIFY]`. The clause needs a page or section from arXiv:2202.01017; the same subsection has already had two other cost claims corrected against this paper, so the paper has been read here before. |
| 10 | medium | PARTIAL | `3_cbic.tex:306` | `chen2020modeling` | PUBLISHED, Appendix B row required | NARROW THE PROSE. "is designed for POI category classification" -> "is applied here to POI category classification". One clause, no result affected. Appendix B row. |
| 11 | medium | PARTIAL | `4_courb.tex:134` | `russwurm2024geographiclocationencodingspherical` | PUBLISHED, Appendix B row required | ADD ONE CLAUSE. State that the encoder used is the sinusoidal-representation-network component of that work; the paper itself reports the two components as separable and each competitive alone. Same fix serves `:153`. Appendix B row. |
| 12 | medium | PARTIAL | `4_courb.tex:153` | `russwurm2024geographiclocationencodingspherical` | PUBLISHED, Appendix B row required | As `:134`, one shared clause covers both. |
| 13 | medium | PARTIAL | `5_mobiwac.tex:153` | `Lim2022` | UNDER REVIEW, two-file change + article errata | LEAVE. The two sentences following the citation already draw the distinction the finding is about. If tightened: say the coarse target is trained but subordinate. |
| 14 | low | NOT-SUPPORTED | `3_cbic.tex:123` | `Zhang2020` | PUBLISHED, Appendix B row required | NARROW THE PROSE. Restate as its authors do: an interactive multi-task framework whose temporal-aware activity encoder handles uncertain check-ins. Appendix B row (wording table). |
| 15 | low | PARTIAL | `1_introduction.tex:50` | `wu2024torchspatial` | frame, no erratum; [NEEDS SIGN-OFF] | NARROW ONE WORD. "first validated" -> "validated". True of both co-cited works under the weaker verb. Frame chapter, so no erratum; `[NEEDS SIGN-OFF]`-class. NOTE: the published CoUrb introduction carries the same "originally validated" attribution to the same key, so the two should take the same disposition. |
| 16 | low | PARTIAL | `3_cbic.tex:102` | `caruana1997multitask` | PUBLISHED, Appendix B row required | LEAVE AND RECORD. The regularization half is supported; the popularity half is a bibliometric claim a 1997 paper cannot carry. Low exposure. |
| 17 | low | PARTIAL | `3_cbic.tex:115` | `zhang2021survey` | PUBLISHED, Appendix B row required | LEAVE AND RECORD. The surveys treat cost growth with task count; "super-linearly" is a shape claim neither abstract states. Challenge-list bullet, no result depends on it. |
| 18 | low | PARTIAL | `3_cbic.tex:115` | `yu2024survey` | PUBLISHED, Appendix B row required | As the row above. |
| 19 | low | PARTIAL | `3_cbic.tex:123` | `Liao2018` | PUBLISHED, Appendix B row required | NARROW THE PROSE. "temporal attention mechanisms" -> "context-aware recurrent units", which is what MCARNN's authors describe. Appendix B wording row. |
| 20 | low | PARTIAL | `3_cbic.tex:125` | `Xia2020` | PUBLISHED, Appendix B row required | NARROW THE PROSE. Drop "LSTMs and", or verify against the paper body. The sentence also needs a grammatical repair ("improve multi-task POI recommendation both location and temporal context"), which is a wording row regardless. |
| 21 | low | PARTIAL | `3_cbic.tex:127` | `Xu2023` | PUBLISHED, Appendix B row required | NARROW THE PROSE. "graph-based encoders" -> "a tree-guided multi-task embedding". Appendix B wording row. |
| 22 | low | PARTIAL | `4_courb.tex:60` | `rahmani2019category` | PUBLISHED, Appendix B row required | LEAVE AND RECORD as a narrow `[VERIFY]` on the sequential clause. Crossref returns a truncated abstract for this paper. |
| 23 | low | PARTIAL | `4_courb.tex:82` | `Xia2020` | PUBLISHED, Appendix B row required | Same work and same defect as `3_cbic.tex:125`. Fix both or neither, so the two chapters do not describe one system two ways. |
| 24 | low | PARTIAL | `5_mobiwac.tex:181` | `caruana1997multitask` | UNDER REVIEW, two-file change + article errata | LEAVE, or move the fixed-weighting clause onto `kurin2022scalarization` / `xin2022domtl`, both cited two lines later and both of which do establish a fixed or uniform weighting as the baseline to beat. |
| 25 | low | UNVERIFIABLE | `3_cbic.tex:145` | `huang2022estimating` | PUBLISHED, Appendix B row required | RECORD as a `[VERIFY]` with a named check: locate the edge-weight formula in the cited paper, or restate it as this work's own construction. |

**Shape of the result.** 25 rows out of 265 key instances: 8 NOT-SUPPORTED, 16 PARTIAL, 1
UNVERIFIABLE. **Twenty-one of the 25 are in reproduced article prose** (15 in Chapter 3, 6 in
Chapter 4), so they are errata-policy decisions rather than free edits. The frame chapters the
author wrote himself carry **one** PARTIAL between them (`1_introduction.tex:50`) and Chapter 2,
the most heavily cited unit at 70 key instances, carries **none**. That asymmetry is the finding
worth naming: the citation risk in this document is concentrated in the inherited related-work
sections of the two published papers, not in the new writing.

**Five rows share two underlying defects.** `Xia2020` is described with LSTMs at both
`3_cbic.tex:125` and `4_courb.tex:82`; `russwurm2024...spherical` is described as SIREN-only at
both `4_courb.tex:134` and `:153`; and the "originally validated" attribution to
`wu2024torchspatial` appears both at `1_introduction.tex:50` and in the published CoUrb
introduction. Fixing each pair together costs one decision instead of two and prevents the
document describing one system two ways.

## 3 · Why each NOT-SUPPORTED is a failure (the four highest-load rows)

The full reasoning for all 25 rows is in the per-chapter reports. The four that carry the most
are set out here, since these are the ones the author will have to rule on.

### `3_cbic.tex:213` — `ruder2017sluice` cited for hard-sharing regularization

The bullet reads: "By constraining the hypothesis space, hard sharing acts as a regularizer, often
leading to more generalizable models, especially when tasks are related." The cited work's title
of record at arXiv is **"Latent Multi-task Architecture Learning"** (arXiv:1705.08142; the bib
entry carries the earlier "Sluice Networks" title, which is an attribute defect in its own right).
Its stated contribution is learning **what and how much to share**, and it reports that this
"consistently outperforms previous approaches to learning latent architectures". It is a
soft-sharing method presented as an improvement on fixed sharing: evidence against the bullet it
is attached to. **`baxter2000model` is the right citation and is already in the bibliography**,
cited for precisely this claim at `4_courb.tex:116`; its abstract states that "the learner can
search for a hypothesis space that contains good solutions to many of the problems", which is the
hypothesis-space-constraint argument the bullet makes.

### `4_courb.tex:161` — `sun2020go` cited for temporal cycles revealing place function

The sentence claims that cyclical regularities such as meal times and weekly movements "carry
discriminative information about the functional nature of the visited POIs". The cited paper is
LSTPM (AAAI 2020), which models long- and short-term **user preference** for next-POI
recommendation with a nonlocal network and a geo-dilated RNN. It makes no claim about temporal
signal predicting place semantics. The temporal-regularity half is common ground in the field and
`cho2011gowalla` supports it directly ("periodic behavior explains 50% to 70%"); the semantics
half has no support anywhere in this bibliography, which I checked by re-reading the abstracts of
`kazemi2019time2vec` and `Xu2023`, the two other candidates in the chapter.

### `4_courb.tex:219` — `belkin2003laplacian` cited for a hierarchical embedding regularizer

The cited object is an L2 penalty pulling a subcategory embedding toward its parent category
embedding over a known label tree. Laplacian eigenmaps is a nonlinear **dimensionality-reduction**
method for data on a low-dimensional manifold. The link is thematic at best (graph-Laplacian
smoothness) and the sentence attributes the term itself to the paper. `Xu2023` (TME), already in
this chapter's citation list, "utilizes the predefined category hierarchy to regularize the
relatedness among categories" — the same construction the term implements.

### `5_mobiwac.tex:44` — `caruana1997multitask` cited for the compromise mechanism

This one is PARTIAL rather than NOT-SUPPORTED but ranks high because it opens Chapter 5 and sets
up the whole study. The sentence says shared parameters "can converge to a compromise optimal for
neither task, helping one while hurting the other". Caruana 1997 is the origin of the shared
representation and argues the **positive** direction: MTL "improves generalization by using the
domain information contained in the training signals of related tasks as an inductive bias".
`standley2020tasks` states the negative direction in as many words — "this often leads to inferior
overall performance as task objectives can compete" — and is already in the bibliography, cited
for exactly this at `2_fundamentals.tex:310`. Adding it beside Caruana closes the gap without
removing the historically correct citation. Chapter 5 is under review, so the change is a
two-file change and goes in that article's errata record, not Appendix B.

## 4 · Six false positives the screen produced, overturned here

Recorded because each would otherwise be re-raised by the next checker, and because two of them
are systematic classes rather than one-offs.

| Site | Key | Screen said | Actual verdict | Why the screen was wrong |
|---|---|---|---|---|
| `5_mobiwac.tex:96` | `silva2025mtlnet` | NOT-SUPPORTED ("architecture described in reverse") | **SUPPORTED** | The CBIC **abstract** compresses the architecture ("shares lower-level embeddings and sequence encoders while maintaining task-specific heads"); the CBIC **method section** of record states the chapter's version verbatim: inputs "are first processed by separate, task-specific encoders", then FiLM conditioning, then shared residual layers, then task-specific heads, with Nash-MTL aggregating gradients. Abstract-only checking inverts this. |
| `apx_b_errata.tex:220` | `silva2025mtlnet` | NOT-SUPPORTED | **SUPPORTED** | An errata row necessarily cites the source that contradicts the text being corrected. The row says the *submitted MobiWac manuscript* mis-described the CBIC work; the cited abstract is the evidence for the erratum, not the claim under audit. Systematic class for errata registers. |
| `2_fundamentals.tex:57` | `Xu2023` | PARTIAL ("TME uses check-in context, not static features") | **SUPPORTED** | The sentence attributes the **task** (labeling a POI with its category, which TME's abstract states as its problem), not a feature set. "from static features rather than from a sequence" is the dissertation's contrast between task types. |
| `2_fundamentals.tex:420` | `wongso2025massivesteps` | PARTIAL ("15 cities, not Istanbul") | **SUPPORTED** | The chapter says the benchmark *supplies* Istanbul check-ins, not that it is Istanbul-only, and the over-reliance claim is verbatim in the abstract ("the over-reliance on older datasets from 2012-2013"). |
| `3_cbic.tex:108` and `2_fundamentals.tex:320` | `liu2019dwa` | PARTIAL / UNVERIFIABLE | **SUPPORTED** | The paper ("End-To-End Multi-Task Learning With Attention", CVPR 2019) introduces both MTAN and Dynamic Weight Averaging. Its abstract leads with the architecture, so an abstract-only check underreads the DWA attribution, which is correct. |
| `appendices apx_d_ceiling.tex:55` | `kohavi1995crossval` | PARTIAL ("recommends ten folds, not five") | **SUPPORTED** | The citation supports cross-validation as the estimation protocol; the fold count and the user grouping are the dissertation's own choices, stated in the same sentence. Same construction as the scikit-learn site the author already ruled on. |

## 5 · ITEM 3 — the Standley citation at `3_cbic.tex:214`

The author asked for four things here: what the paper does and does not support, a commit-history
check for an earlier reference at that site, whether a reference that DOES support the claim exists,
and a drafted narrowed sentence with its Appendix B row. **`3_cbic.tex` was not edited.**

### 5.1 · What the paper supports, read at the source

Resolved as arXiv:1905.07553 (arXiv API: submitted 2019-05-18, last revised 2020-09-03, six
authors, no `journal_ref` and no DOI on the preprint record) and as the ICML 2020 version at
OpenAlex (venue "International Conference on Machine Learning", pp. 9120-9132, PMLR v119). I then
downloaded and read the full paper (13 pages, arXiv v3). The bibliography entry's ICML venue is
correct and the dropped page range is the fail-closed behaviour Appendix B already records.

The citing bullet claims two things. **Both fail, in different ways.**

*First half, "hard parameter sharing frequently matches or exceeds the performance of more complex
architectures on many benchmarks".* The paper argues the opposite direction as its motivating
premise: multi-task learning "often leads to inferior overall performance as task objectives can
compete", and in the body, "multi-task performance can suffer so much that smaller independent
networks are often superior". Its own contribution is a framework for **assigning** tasks across
several networks so that cooperating tasks share one and competing tasks do not. On the specific
comparison the bullet makes, the paper reports its groupings beating a single traditional
multi-task network at every budget above 1.5 SNT: "solutions that utilize multiple networks
outperform this traditional strategy for every budget > 1.5". The one result that leans the
bullet's way is narrower and budget-conditional: "when the single-task networks are shrunk so that
they fit within the same total budget as the multi-task network, multi-task networks with 3, 4, or
5 tasks outperform the single-task networks on average. Nevertheless, two-task networks still do
not compare favorably." **This chapter's model has exactly two tasks**, so the sentence the paper
does support is the one that excludes this chapter's own case.

*Second half, "while offering faster training and inference".* The string "faster training" does
not occur in the paper. It does support the inference half: multi-task learning "can save
computation at inference time as only a single network needs to be evaluated", and the paper's
framework "offers a time-accuracy trade-off". On training the paper says the opposite of a benefit
in the passage nearest the claim: UberNet's authors, using hard sharing, "focus on reducing the
computational cost of training for hard parameter sharing, but experience a rapid degradation in
performance as more tasks are added". Training cost is also the axis on which this chapter's own
result went the other way, which Appendix B already records.

So the site is not a mis-citation of the wrong paper. It is a **correctly identified paper cited
for the reverse of its finding**, which is the class AGENT_GUARDRAILS §1 calls claim-not-supported
and which existence checking cannot catch. Note that the same key is cited four times in Chapter
3, and three of those four are sound: `:118` (task clustering), `:191` (mitigating negative
transfer, alongside `perez2018film`) and `2_fundamentals.tex:310` (joint training can hurt as
easily as it helps) are all SUPPORTED. Only `:214` and `:114` fail.

### 5.2 · The commit history: was a different reference ever used at that site?

**No. The answer is negative and I can date it.** Run through the shell over both paths the author
named:

```
git log --oneline -S"standley2020tasks"    -- articles/CBIC___MTL/sections/ articles/dissertacao/src/chapters/3_cbic.tex
git log --oneline -S"matches or exceeds"   -- (same two paths)
git log --oneline -S"Empirical Performance"-- (same two paths)
```

All three return the **same two commits**, and only those two:

| Commit | Date | What it is |
|---|---|---|
| `223f5df7` | 2025-10-21 12:22 | first import of the CBIC article tree (`CBIC___MTL/` at the repo root) |
| `643c686e` | 2025-10-21 12:23 | the same content one minute later, after the `articles/` reorganization |
| `1a29b545` | 2026-07-23 | the dissertation re-typeset that copied the sentence into `3_cbic.tex` |

`articles/CBIC___MTL/sections/method.tex` has been touched by **exactly one commit in its entire
history** (`643c686e`). The bullet is present in the very first committed version of that file, at
line 85, with `\cite{standley2020tasks}` already attached and the wording byte-identical to today:

> \item \textbf{Empirical Performance:} In practice, hard parameter sharing frequently matches or
> exceeds the performance of more complex architectures on many benchmarks, while offering faster
> training and inference \cite{standley2020tasks}.

I then checked the dissertation side the other way, printing the `Empirical Performance` line from
**every one of the 14 commits** that has ever touched `3_cbic.tex`: the line is byte-identical in
all 13 versions in which it exists, and absent only from `a735b8f3` (the skeleton commit, before
the chapter had content). I also ran `-S` for seven plausible alternative keys
(`vandenhende2022mtl`, `crawshaw2020multi`, `ruder2017overview`, `zhang2021survey`,
`kokkinos2016ubernet`, `caruana1997multitask`, `baxter2000model`) against the CBIC method file:
only `caruana1997multitask` and `baxter2000model` appear at all, each in the single import commit,
and neither has ever stood at this bullet.

**Conclusion.** No earlier or different reference ever stood at that site. The mis-support is
original to the article as first written, not introduced by the dissertation's re-typeset or by any
later repair. That is worth recording precisely because the neighbouring Mikolov site *was* a
repair-introduced defect (`church2017word2vec` -> `mikolov2013word2vec` fixed an existence error and
left a support error); this one has a different history and no repair to blame.

One further fact from the history, offered because it bears on how the site should be fixed: the
same key is cited in the CBIC architecture sentence (`method.tex`, now `3_cbic.tex:191`) for
"modulating task interactions and mitigating negative transfer", alongside `perez2018film`. That
use is **sound** and is what the paper is actually about. The author's own instinct in citing
Standley was right; only this one bullet's direction is wrong.

### 5.3 · Does a reference in the bibliography support the claim as stated?

**Not as stated, and I would not add one that appeared to.** I checked the three candidates whose
stated findings are closest, all already in `references.bib` and all read at their sources this
session:

| Candidate | Identifier | What it actually supports | Verdict as a replacement |
|---|---|---|---|
| `kurin2022scalarization` | arXiv:2201.04122 (OpenAlex) | "unitary scalarization, coupled with standard regularization and stabilization techniques ... matches or improves upon the performance of complex multi-task optimizers" | Supports "matches or improves" about **optimizers**, not about architectures. Closest in wording, wrong object. |
| `xin2022domtl` | arXiv:2209.11379 (arXiv API) | "MTO methods do not yield any performance improvements beyond what is achievable via traditional optimization approaches" | Same: optimizers, not architectures. |
| `vandenhende2022mtl` | DOI 10.1109/TPAMI.2021.3054719 (Crossref) | an architecture-plus-optimization survey with "an extensive experimental evaluation across a variety of dense prediction benchmarks to examine the pros and cons of the different methods" | The only candidate whose object is architectures and which compares them on benchmarks. It does not state the bullet's direction in its abstract, so citing it for "frequently matches or exceeds" would repeat the present defect one step removed. |

The honest reading is that the bullet's first half, as written, is **not a claim the MTL literature
supports in general** — which is precisely what this dissertation's own arc goes on to find. So the
repair is to narrow the sentence to what is supported, not to hunt for a citation that licenses the
original. Two things *are* supported and are worth keeping:

- **the inference-time saving**, by Standley directly ("can save computation at inference time as
  only a single network needs to be evaluated");
- **the fixed-weight-baseline result**, by `kurin2022scalarization` and `xin2022domtl`, which is the
  defensible version of "the simple thing is hard to beat" and which Chapter 2 already states at
  `2_fundamentals.tex:331-340`.

### 5.4 · The drafted narrowed sentence (for the author to approve; NOT applied)

The bullet lives in an itemized list of three under "Rationale for Hard Parameter Sharing". The
draft keeps the list structure, keeps the bullet's role in the argument (why this chapter chose hard
sharing), and reduces the claim to what the cited work supports. Claim strength goes **down**, never
up, which is the direction the writing law requires for a substitution.

**Published wording** (`articles/CBIC___MTL/sections/method.tex`, reproduced at `3_cbic.tex:214`):

> \item \textbf{Empirical Performance:} In practice, hard parameter sharing frequently matches or
> exceeds the performance of more complex architectures on many benchmarks, while offering faster
> training and inference \cite{standley2020tasks}.

**Draft replacement** (option A, the conservative one — narrows to the inference claim the paper
makes and drops the comparative claim it does not):

```latex
    \item \textbf{Inference Cost:} A single shared network is evaluated once at inference time
    rather than once per task, which is where the joint model's computational advantage lies
    \cite{standley2020tasks}.\footnote{The published sentence read ``In practice, hard parameter
    sharing frequently matches or exceeds the performance of more complex architectures on many
    benchmarks, while offering faster training and inference''. Neither half is supported by the
    cited work, which argues that joint training ``often leads to inferior overall performance as
    task objectives can compete'' and reports its own task groupings outperforming a single
    multi-task network at every inference budget it tests. The claim is corrected here rather than
    reproduced. See Table~\ref{tab:apx:cbic-errata}.}
```

**Draft replacement** (option B, if the author prefers to keep a performance claim in the bullet —
it then has to be the one the literature supports, and the citation changes):

```latex
    \item \textbf{Empirical Performance:} A simple shared architecture trained with fixed loss
    weights is a strong baseline: controlled comparisons report that specialized multi-task
    optimizers do not consistently improve on it \cite{kurin2022scalarization,xin2022domtl}. The
    inference cost is also lower, since a single network is evaluated once rather than once per
    task \cite{standley2020tasks}.
```

I recommend **option A**. It is the smaller change, it keeps the bullet's function, and it does not
import a claim about optimizers into a paragraph about architectures. Option B is defensible but it
adds two citations to published prose and shifts the bullet's subject.

Two consequential notes on the surrounding text if option A is taken. The bullet's `\textbf{}` label
changes from "Empirical Performance" to "Inference Cost", which is a heading change inside published
prose and needs the same sign-off as the sentence. And the paragraph's lead-in at `:210` says the
choice "is motivated by its efficiency and regularization benefits" — after this change the list's
three bullets are efficiency, regularization and inference cost, so the lead-in still reads
correctly, but the first and third bullets both now concern cost. The author may prefer to merge
them; that is a structural edit and I have not drafted it.

### 5.5 · The Appendix B row (drafted, NOT applied)

This goes in `src/tables/cbic/errata.tex`, the content-errata table for the CBIC chapter, whose
existing rows I read and matched for voice (defect stated flatly in the left cell, correction with
its evidence and its direction in the right cell; the Nash rows are the closest models). It is a
content correction, not a wording substitution, so it belongs in `errata.tex` and not in
`errata_wording.tex`.

```latex
\addlinespace
The rationale for hard parameter sharing states that the approach ``frequently matches or exceeds
the performance of more complex architectures on many benchmarks, while offering faster training
and inference''. The cited work argues the opposite direction: joint training ``often leads to
inferior overall performance as task objectives can compete'', and its own contribution is a
framework for splitting tasks across several networks, which it reports outperforming a single
multi-task network at every inference budget it tests. The phrase ``faster training'' does not
occur in it. &
Narrowed to the claim the cited work supports, that a single shared network is evaluated once at
inference time rather than once per task, with the correction recorded in a footnote. The one
result in that work which favors joint training is conditioned on a matched parameter budget and
on three or more tasks, and it excludes the two-task case this chapter studies. The correction
removes a claim in the chapter's own favor, so it runs against the chapter's interest. \\
```

The reconciliation header at the top of `apx_b_errata.tex` counts itemized rows ("6 + 13 + 3 + 14 =
36"); adding this row makes the CBIC content table 7 and the total 37. **That header comment must be
updated in the same commit as the row**, or the appendix will misstate its own count — the defect
class the file's own history records at the "11 rows" line. I have not made either change: applying
chapter prose edits is a later pass, and I did not want a half-applied erratum in the tree.

## 6 · ITEM 2 — the two bibliography records, re-verified and applied

I re-verified both at Crossref in this session rather than trusting the audit's values. Both came
back exactly as the audit reported, with one typographic difference worth recording.

### 6.1 · `kokkinos2016ubernet`

**Before** (`references.bib:395-400`): `@article` with
`journal = {arXiv preprint arXiv:1609.02132}`, year 2016, no DOI.

**Crossref, DOI 10.1109/cvpr.2017.579**, fetched this session:

| Field | Value returned |
|---|---|
| title | UberNet: Training a Universal Convolutional Neural Network for Low-, Mid-, and High-Level Vision Using Diverse Datasets and Limited Memory |
| container-title | 2017 IEEE Conference on Computer Vision and Pattern Recognition (CVPR) |
| type / publisher | proceedings-article / IEEE |
| issued | 2017-07 |
| page | 5454-5463 |
| author | Iasonas Kokkinos (single) |

Cross-checked at the arXiv API for 1609.02132: same single author, same title, submitted
2016-09-07, and **no `journal_ref` and no DOI on the preprint record**, which is why the conference
version does not resolve from the preprint alone. Every value the audit reported is confirmed:
CVPR 2017, DOI 10.1109/cvpr.2017.579, pp. 5454-5463.

**One difference from Crossref I did not adopt.** Crossref renders the title without the quotation
marks around *Universal* that the author's own preprint title carries (\`Universal'). I kept the
author's typography, since R2 asks that a work be described as its authors describe it, and
recorded the difference in the entry's provenance comment.

**After** (`references.bib:394-412`): re-typed to `@inproceedings` with the CVPR booktitle, pages
`5454--5463`, `doi = {10.1109/CVPR.2017.579}`, and `note = {arXiv:1609.02132}` keeping the preprint
identifier. **The key is unchanged, so no citing site moves.** The single citing site is
`1_introduction.tex:72`, which cites it for "single networks that handle many vision tasks at once";
the abstract supports that and the site is SUPPORTED in the Chapter 1 report.

### 6.2 · `mai2023sphere2vecgeneralpurposelocationrepresentation`

**Before** (`references.bib:640-648`): `@misc` with `eprint = {2306.17624}`, `archivePrefix`,
`primaryClass`, `url`, year 2023, no venue at all.

**Crossref, DOI 10.1016/j.isprsjprs.2023.06.016**, fetched this session:

| Field | Value returned |
|---|---|
| title | Sphere2Vec: A general-purpose location representation learning over a spherical surface for large-scale geospatial predictions |
| container-title | ISPRS Journal of Photogrammetry and Remote Sensing |
| type / publisher | journal-article / Elsevier BV |
| issued | 2023-08 |
| volume / page | 202 / 439-462 |
| ISSN | 0924-2716 |
| authors | Gengchen Mai; Yao Xuan; Wenyun Zuo; Yutong He; Jiaming Song; Stefano Ermon; Krzysztof Janowicz; Ni Lao (8) |

Cross-checked at the arXiv API for 2306.17624: the record's `journal_ref` field reads **"ISPRS
Journal of Photogrammetry and Remote Sensing, 2023"**, and the author list and title match. Every
value the audit reported is confirmed: ISPRS J. Photogramm. Remote Sens. 202:439-462, DOI
10.1016/j.isprsjprs.2023.06.016.

**After** (`references.bib:639-657`): re-typed to `@article` with the journal abbreviated exactly as
the sibling entry `huang2023hgi` abbreviates the same journal (`ISPRS J. Photogramm. Remote Sens.`),
volume 202, pages `439--462`, the DOI, and `note = {arXiv:2306.17624}`. **The key is unchanged, so
none of the five citing sites moves.**

### 6.3 · The two errata rows, and the overfull box they caused

Both rows were added to `src/tables/frame/bib_errata.tex` immediately before the CoUrb-Gowalla row,
matching the existing rows' voice (defect in the donor list on the left, correction with its
verification source on the right, the phrase "arXiv identifier kept as a note" reused from the GAT
and Rußwurm rows).

**First attempt introduced a defect, which the rebuild caught.** Printing
`\texttt{mai2023sphere2vecgeneralpurposelocationrepresentation}` (52 characters) in the
`p{0.42\textwidth}` left column produced `Overfull \hbox (113.58371pt too wide)` at
`bib_errata.tex:112-113` — a `\texttt` key does not line-break. It was the only overfull box in
either build. The fix follows the precedent already in the table: the Rußwurm row **names the work**
instead of printing the key, and so does this row now ("The Sphere2Vec location encoder of Mai et
al. was typed as an arXiv preprint, with no venue recorded at all"). The constraint is recorded in a
comment at the top of the file so the next editor does not re-introduce a long key in a cell.

**The braces are intact.** The `{\small ...}` group whose lost opening brace broke every build from
`6d780b58` to `a880632b` is untouched: I verified the balance mechanically on the comment-stripped
file (44 open, 44 close, delta 0), confirmed line 15 is still `{\small` and the file still ends
`\end{longtable}` then `}`, and rebuilt.

**Both rows render.** Read out of the PDF text layer, not assumed: the two rows are on **p. 95** of
the defense build and **p. 90** of the final build, carrying "kokkinos2016ubernet: typed as an arXiv
preprint", "DOI 10.1109/CVPR.2017.579, pages 5454-5463", "The Sphere2Vec location encoder of Mai et
al." and "DOI 10.1016/j.isprsjprs.2023.06.016". The two upgraded entries also render in the printed
bibliography on **p. 81**: `[8] KOKKINOS, I. Ubernet: ... In: Proceedings of the IEEE Conference on
Computer Vision and Pattern Recognition (CVPR). 2017. p. 5454-5463. ArXiv:1609.02132.` and `[5]
MAI, G. et al. Sphere2vec: ... ISPRS J. Photogramm. Remote Sens., v. 202, p. 439-462, 2023.
ArXiv:2306.17624.`

## 7 · Build result

Run after the two `src/` edits, from `src/`, with `src_utils/texenv.sh` sourced:

```
make defense   ->  build/main.pdf        105 pages
make final     ->  build/main_final.pdf  100 pages
bash ../src_utils/build.sh . both
  DEFENSE: pages=['105'] tex_errors=0 overfull_hbox=0 overfull_vbox=0 undef_cite=0 undef_ref=0
           bibtex_problems=0 oversized_floats=0
  FINAL:   pages=['100'] tex_errors=0 overfull_hbox=0 overfull_vbox=0 undef_cite=0 undef_ref=0
           bibtex_problems=0 oversized_floats=0
```

**The gate was validated in both directions before I trusted it**, per AGENT_GUARDRAILS §7 ("a check
that has never fired is not a check"). I copied `src/` to a scratch tree and re-injected the exact
historical defect, removing the opening brace of the `{\small` group in `bib_errata.tex`. On that
tree `build.sh` reports `tex_errors=1` with `! Extra }, or forgotten \endgroup`, prints its own
warning that the recovered PDF "is not the document", and **exits 1**; `make defense` produces no PDF
at all and exits 2. On the real tree `build.sh` reports `tex_errors=0` and **exits 0**. So the zero
above is an observation the checker is capable of contradicting.

`tex_errors=0` on both, which is the part of the claim that matters after `ba90aa6d`. Zero overfull
boxes after the long-key fix described in 6.3. Both builds are converged: I ran each twice and the
byte size and page count stopped moving, and the `Label(s) may have changed` warning is gone from
the final pass.

**On the page count, stated carefully because ANCHORS.md records 104/99 and this build reports
105/100.** The delta is **not** mine. Other agents are working in this same tree and have
uncommitted edits in it, including `src/chapters/5_mobiwac.tex` (19 lines) and a replaced CoUrb
figure. I measured the attribution rather than assuming it: I copied `src/` to a scratch tree,
reverted **only my two files** to their `HEAD` versions, and rebuilt. That tree also produces **105
pages**. So the document had already grown to 105/100 from another agent's work before my edits, and
my two errata rows cost **zero pages** — they fit in the existing longtable overflow on p. 95. The
committed `dissertacao.pdf` at `HEAD` is 104 pages, which is what ANCHORS.md measured.

`make check` **fails**, on one gate, and it is not mine:

```
== recorded page counts vs the measured build ==
src/build/main.log has no page count -- the build did not finish
  -> run: python3 src_utils/sync_page_counts.py --write
```

Two things to note about that gate. First, its message is **wrong about the cause**: the build did
finish and `build/main.log` does contain `Output written on build/main.pdf (105 pages, ...)`. The
check reads `main.log` before the final `pdflatex` pass has rewritten it, or reads it while `make`
is mid-run; either way the failure is a stale-read in the checker, not a build failure. Second, the
recorded page counts in the governance files are now stale by one page for a reason that is not my
change. **I did not run `sync_page_counts.py --write`**: it edits `CLAUDE.md`, `PLAN.md` and other
files outside my remit, and the page count is still moving while other agents work. That is a
hand-off, recorded here rather than acted on. Every other `make check` gate passes: banned words,
codenames, unresolved refs and cites, bibtex, sweep-guard self-tests, word-count reconciliation,
torn sentences (0), trapped prose (0/10 fixtures failing).

## 8 · Edits applied

| File | Lines | Change |
|---|---|---|
| `src/references.bib` | 394-412 | `kokkinos2016ubernet` re-typed `@article` -> `@inproceedings`, CVPR 2017 booktitle, pp. 5454--5463, `doi = {10.1109/CVPR.2017.579}`, `note = {arXiv:1609.02132}`, with a 10-line provenance comment naming what was verified where. Key unchanged. |
| `src/references.bib` | 650-670 | `mai2023sphere2vecgeneralpurposelocationrepresentation` re-typed `@misc` -> `@article`, ISPRS J. Photogramm. Remote Sens. v.202 pp. 439--462, `doi = {10.1016/j.isprsjprs.2023.06.016}`, `note = {arXiv:2306.17624}`, with a 9-line provenance comment. Key unchanged. |
| `src/tables/frame/bib_errata.tex` | 15-22 | Comment recording the two new rows and the long-key overflow constraint, so it is not re-introduced. |
| `src/tables/frame/bib_errata.tex` | 114-124 | The two errata rows, in the existing rows' voice, placed before the CoUrb-Gowalla row. |

Nothing else in `src/` was touched. `3_cbic.tex` was **not** edited (ITEM 3 is a hand-off);
`apx_b_errata.tex` was **not** edited (its reconciliation header needs the Standley row and the
count update in the same commit as the prose change, which is the later pass).

## 9 · Source ledger

Every one of the 100 bibliography entries, the identifier it resolved by, and where I opened it this
session. Channels: **Crossref REST** (`api.crossref.org/works/{doi}`), **arXiv API**
(`export.arxiv.org/api/query?id_list=`), **OpenAlex** (`api.openalex.org`, with the configured API
key on every request; never anonymous, never with a `mailto` parameter), **Semantic Scholar**
(`api.semanticscholar.org/graph/v1`) for abstracts Crossref does not deposit, and **PDF** where a
full text was read.

| Key | Identifier | Opened at | Record as returned |
|---|---|---|---|
| `bastug2014edge` | DOI 10.1109/MCOM.2014.6871674 | Crossref REST; OpenAlex API | Living on the edge: The role of proactive caching in 5G wireless networks \| IEEE Communications Magazine \| 2014 \| type journal-article |
| `baxter2000model` | DOI 10.1613/jair.731 | Crossref REST; OpenAlex API | A Model of Inductive Bias Learning \| Journal of Artificial Intelligence Research \| 2000 \| type journal-article |
| `belghazi2018mine` | arXiv:1801.04062 | arXiv API; OpenAlex API | MINE: Mutual Information Neural Estimation \| ICML 2018 \| 2018 \| type posted-content |
| `belkin2003laplacian` | DOI 10.1162/089976603321780317 | Crossref REST; OpenAlex API | Laplacian Eigenmaps for Dimensionality Reduction and Data Representation \| Neural Computation \| 2003 \| type journal-article |
| `capanema2023poirgnn` | DOI 10.1016/j.adhoc.2022.103016 | Crossref REST; OpenAlex API | Combining recurrent and Graph Neural Networks to predict the next place’s category \| Ad Hoc Networks \| 2023 \| type journal-article |
| `caruana1997multitask` | DOI 10.1023/A:1007379606734 | Crossref REST; OpenAlex API; PDF in repo: 10.1023_A_1007379606734.pdf | Multitask Learning \| Machine Learning \| 1997 \| type journal-article |
| `chen2018gradnorm` | no identifier in the bib entry | arXiv API; OpenAlex API | GradNorm: Gradient Normalization for Adaptive Loss Balancing in Deep Multitask Networks \| Proceedings of the 35th International Conference on Machine |
| `chen2020modeling` | DOI 10.1109/TKDE.2020.3001025 | Crossref REST; OpenAlex API | Modeling Spatial Trajectories With Attribute Representation Learning \| IEEE Transactions on Knowledge and Data Engineering \| 2022 \| type journal-ar |
| `cho2011gowalla` | DOI 10.1145/2020408.2020579 | Crossref REST; OpenAlex API | Friendship and mobility \| Proceedings of the 17th ACM SIGKDD international conference on Knowledge discovery and data mining \| 2011 \| type proceedi |
| `du2019beyond` | DOI 10.1109/ICDM.2019.00026 | Crossref REST; OpenAlex API | Beyond Geo-First Law: Learning Spatial Representations via Integrated Autocorrelations and Complementarity \| 2019 IEEE International Conference on Da |
| `feng2017poi2vec` | DOI 10.1609/aaai.v31i1.10500 | Crossref REST; OpenAlex API | POI2Vec: Geographical Latent Representation for Predicting Future Visitors \| Proceedings of the AAAI Conference on Artificial Intelligence \| 2017 \| |
| `feng2018deepmove` | DOI 10.1145/3178876.3186058 | Crossref REST; OpenAlex API | DeepMove \| Proceedings of the 2018 World Wide Web Conference on World Wide Web - WWW '18 \| 2018 \| type proceedings-article |
| `gambs2012mmc` | DOI 10.1145/2181196.2181199 | Crossref REST; OpenAlex API | Next place prediction using mobility Markov chains \| Proceedings of the First Workshop on Measurement, Privacy, and Mobility \| 2012 \| type proceedi |
| `grover2016node2vec` | DOI 10.1145/2939672.2939754 | Crossref REST; OpenAlex API | node2vec \| Proceedings of the 22nd ACM SIGKDD International Conference on Knowledge Discovery and Data Mining \| 2016 \| type proceedings-article |
| `Halder2021` | DOI 10.1007/978-3-030-75765-6_41 | Crossref REST; OpenAlex API; Semantic Scholar API | Transformer-Based Multi-task Learning for Queuing Time Aware Next POI Recommendation \| Lecture Notes in Computer Science \| 2021 \| type book-chapter |
| `Halder2022` | DOI 10.1007/s10618-022-00865-w | Crossref REST; OpenAlex API | POI recommendation with queuing time and user interest awareness \| Data Mining and Knowledge Discovery \| 2022 \| type journal-article |
| `hamilton2017graphsage` | arXiv:1706.02216 | arXiv API; OpenAlex API | Inductive Representation Learning on Large Graphs \| arXiv preprint \| 2017 \| type posted-content |
| `hazimeh2021dselectk` | arXiv:2106.03760 | arXiv API; OpenAlex API | DSelect-k: Differentiable Selection in the Mixture of Experts with Applications to Multi-Task Learning \| arXiv preprint \| 2021 \| type posted-conten |
| `hjelm2019dim` | arXiv:1808.06670 | arXiv API; OpenAlex API | Learning deep representations by mutual information estimation and maximization \| arXiv preprint \| 2018 \| type posted-content |
| `holm1979` | no identifier in the bib entry | OpenAlex API | A Simple Sequentially Rejective Multiple Test Procedure \| Scandinavian Journal of Statistics \| 1979 \| type article |
| `huang2022estimating` | DOI 10.1080/13658816.2022.2040510 | Crossref REST; OpenAlex API | Estimating urban functional distributions with semantics preserved POI embedding \| International Journal of Geographical Information Science \| 2022  |
| `huang2023hgi` | DOI 10.1016/j.isprsjprs.2022.11.021 | Crossref REST; OpenAlex API; Semantic Scholar API; PDF in repo: Learning urban region representations with POIs and hierarchical graph infomax.pdf | Learning urban region representations with POIs and hierarchical graph infomax \| ISPRS Journal of Photogrammetry and Remote Sensing \| 2023 \| type j |
| `huang2024cslsl` | DOI 10.1140/epjds/s13688-024-00460-7 | Crossref REST; OpenAlex API | Human mobility prediction with causal and spatial-constrained multi-task network \| EPJ Data Science \| 2024 \| type journal-article |
| `jure2014snap` | no identifier in the bib entry | OpenAlex API | {SNAP Datasets}: {Stanford} Large Network Dataset Collection \| (no venue in record) \| 2014 \| type article |
| `kazemi2019time2vec` | arXiv:1907.05321 | arXiv API; OpenAlex API | Time2Vec: Learning a Vector Representation of Time \| arXiv preprint \| 2019 \| type posted-content |
| `kendall2018uncertainty` | DOI 10.1109/CVPR.2018.00781 | Crossref REST; OpenAlex API | Multi-task Learning Using Uncertainty to Weigh Losses for Scene Geometry and Semantics \| 2018 IEEE/CVF Conference on Computer Vision and Pattern Reco |
| `kipf2017gcn` | arXiv:1609.02907 | arXiv API; OpenAlex API | Semi-Supervised Classification with Graph Convolutional Networks \| arXiv preprint \| 2016 \| type posted-content |
| `kohavi1995crossval` | no identifier in the bib entry | OpenAlex API | A Study of Cross-Validation and Bootstrap for Accuracy Estimation and Model Selection \| (no venue in record) \| 1995 \| type article |
| `kokkinos2016ubernet` | arXiv:1609.02132 | arXiv API; OpenAlex API | UberNet: Training a `Universal' Convolutional Neural Network for Low-, Mid-, and High-Level Vision using Diverse Datasets and Limited Memory \| arXiv  |
| `kong2018hstlstm` | DOI 10.24963/ijcai.2018/324 | Crossref REST; OpenAlex API | HST-LSTM: A Hierarchical Spatial-Temporal Long-Short Term Memory Network for Location Prediction \| Proceedings of the Twenty-Seventh International Jo |
| `kurin2022scalarization` | no identifier in the bib entry | arXiv API; OpenAlex API | In Defense of the Unitary Scalarization for Deep Multi-Task Learning \| arXiv preprint \| 2022 \| type posted-content |
| `lakens2017tost` | DOI 10.1177/1948550617697177 | Crossref REST; OpenAlex API | Equivalence Tests \| Social Psychological and Personality Science \| 2017 \| type journal-article |
| `li2025rehdm` | DOI 10.24963/ijcai.2025/343 | Crossref REST; OpenAlex API | Beyond Individual and Point: Next POI Recommendation via Region-aware Dynamic Hypergraph with Dual-level Modeling \| Proceedings of the Thirty-Fourth  |
| `lian2020geosan` | DOI 10.1145/3394486.3403252 | Crossref REST; OpenAlex API | Geography-Aware Sequential Location Recommendation \| Proceedings of the 26th ACM SIGKDD International Conference on Knowledge Discovery &amp; Data Mi |
| `Liao2018` | DOI 10.24963/ijcai.2018/477 | Crossref REST; OpenAlex API | Predicting Activity and Location with Multi-task Context Aware Recurrent Neural Network \| Proceedings of the Twenty-Seventh International Joint Confe |
| `Lim2022` | DOI 10.1145/3477495.3531989 | Crossref REST; OpenAlex API | Hierarchical Multi-Task Graph Recurrent Network for Next POI Recommendation \| Proceedings of the 45th International ACM SIGIR Conference on Research  |
| `lin2021ctle` | DOI 10.1609/aaai.v35i5.16548 | Crossref REST; OpenAlex API | Pre-training Context and Time Aware Location Embeddings from Spatial-Temporal Trajectories for User Next Location Prediction \| Proceedings of the AAA |
| `lin2022rlw` | arXiv:2111.10603 | arXiv API; OpenAlex API | Reasonable Effectiveness of Random Weighting: A Litmus Test for Multi-Task Learning \| arXiv preprint \| 2021 \| type posted-content |
| `lipton2015learning` | arXiv:1511.03677 | arXiv API; OpenAlex API | Learning to Diagnose with LSTM Recurrent Neural Networks \| arXiv preprint \| 2015 \| type posted-content |
| `liu2016strnn` | DOI 10.1609/aaai.v30i1.9971 | Crossref REST; OpenAlex API | Predicting the Next Location: A Recurrent Model with Spatial and Temporal Contexts \| Proceedings of the AAAI Conference on Artificial Intelligence \| |
| `liu2019dwa` | DOI 10.1109/CVPR.2019.00197 | Crossref REST; OpenAlex API | End-To-End Multi-Task Learning With Attention \| 2019 IEEE/CVF Conference on Computer Vision and Pattern Recognition (CVPR) \| 2019 \| type proceeding |
| `liu2021cagrad` | arXiv:2110.14048 | arXiv API; OpenAlex API | Conflict-Averse Gradient Descent for Multi-task Learning \| arXiv preprint \| 2021 \| type posted-content |
| `liu2023famo` | no identifier in the bib entry | arXiv API; OpenAlex API | FAMO: Fast Adaptive Multitask Optimization \| arXiv preprint \| 2023 \| type posted-content |
| `luca2021mobilitysurvey` | DOI 10.1145/3485125 | Crossref REST; OpenAlex API | A Survey on Deep Learning for Human Mobility \| ACM Computing Surveys \| 2021 \| type journal-article |
| `luo2021stan` | DOI 10.1145/3442381.3449998 | Crossref REST; OpenAlex API | STAN: Spatio-Temporal Attention Network for Next Location Recommendation \| Proceedings of the Web Conference 2021 \| 2021 \| type proceedings-article |
| `ma2018mmoe` | DOI 10.1145/3219819.3220007 | Crossref REST; OpenAlex API | Modeling Task Relationships in Multi-task Learning with Multi-gate Mixture-of-Experts \| Proceedings of the 24th ACM SIGKDD International Conference o |
| `mai2020multiscalerepresentationlearningspatial` | arXiv:2003.00824 | arXiv API; OpenAlex API | Multi-Scale Representation Learning for Spatial Feature Distributions using Grid Cells \| ICLR 2020, Apr. 26 - 30, 2020, Addis Ababa, ETHIOPIA \| 2020 |
| `mai2023sphere2vecgeneralpurposelocationrepresentation` | arXiv:2306.17624 | arXiv API; OpenAlex API | Sphere2Vec: A General-Purpose Location Representation Learning over a Spherical Surface for Large-Scale Geospatial Predictions \| ISPRS Journal of Pho |
| `maninis2019attentive` | DOI 10.1109/CVPR.2019.00195 | Crossref REST; OpenAlex API | Attentive Single-Tasking of Multiple Tasks \| 2019 IEEE/CVF Conference on Computer Vision and Pattern Recognition (CVPR) \| 2019 \| type proceedings-a |
| `mikolov2013negsampling` | arXiv:1310.4546 | arXiv API; OpenAlex API | Distributed Representations of Words and Phrases and their Compositionality \| arXiv preprint \| 2013 \| type posted-content |
| `mikolov2013word2vec` | arXiv:1301.3781 | arXiv API; OpenAlex API | Efficient Estimation of Word Representations in Vector Space \| arXiv preprint \| 2013 \| type posted-content |
| `misra2016cross` | DOI 10.1109/CVPR.2016.433 | Crossref REST; OpenAlex API | Cross-Stitch Networks for Multi-task Learning \| 2016 IEEE Conference on Computer Vision and Pattern Recognition (CVPR) \| 2016 \| type proceedings-ar |
| `moura2025mobilityaware` | DOI 10.1109/MSWiM67937.2025.11308734 | Crossref REST; OpenAlex API | On the Design of Mobility-Aware Systems: A Tourist’s Perspective \| 2025 International Conference on Modeling, Analysis and Simulation of Wireless and |
| `nash` | no identifier in the bib entry | arXiv API; OpenAlex API | Multi-Task Learning as a Bargaining Game \| arXiv preprint \| 2022 \| type posted-content |
| `paiva2026stmtlnet` | DOI 10.5753/courb.2026.22960 | Crossref REST; OpenAlex API | ST-MTLNet: Representações Espaço-Temporais de Pontos de Interesse para Aprendizado Multitarefa \| Anais do X Workshop de Computação Urbana (CoUrb 2026 |
| `pedregosa2011sklearn` | no identifier in the bib entry | arXiv API; OpenAlex API; PDF in repo: Pedregosa2011_ScikitLearn.pdf | Scikit-learn: Machine Learning in Python \| Journal of Machine Learning Research (2011) \| 2012 \| type posted-content |
| `perez2018film` | DOI 10.1609/aaai.v32i1.11671 | Crossref REST; OpenAlex API | FiLM: Visual Reasoning with a General Conditioning Layer \| Proceedings of the AAAI Conference on Artificial Intelligence \| 2018 \| type journal-arti |
| `perozzi2014deepwalk` | DOI 10.1145/2623330.2623732 | Crossref REST; OpenAlex API | DeepWalk \| Proceedings of the 20th ACM SIGKDD international conference on Knowledge discovery and data mining \| 2014 \| type proceedings-article |
| `rahmani2019category` | DOI 10.1145/3341981.3344240 | Crossref REST; OpenAlex API | Category-Aware Location Embedding for Point-of-Interest Recommendation \| Proceedings of the 2019 ACM SIGIR International Conference on Theory of Info |
| `ruder2017mtloverview` | arXiv:1706.05098 | arXiv API; OpenAlex API | An Overview of Multi-Task Learning in Deep Neural Networks \| arXiv preprint \| 2017 \| type posted-content |
| `ruder2017sluice` | arXiv:1705.08142 | arXiv API | Latent Multi-task Architecture Learning \| arXiv preprint \| 2017 \| type posted-content |
| `russwurm2024geographiclocationencodingspherical` | arXiv:2310.06743 | arXiv API; OpenAlex API | Geographic Location Encoding with Spherical Harmonics and Sinusoidal Representation Networks \| Published as a conference paper at ICLR 2024 \| 2023 \ |
| `santos2024urban` | no identifier in the bib entry | NOT RESOLVED at any source of record | None \| (no venue in record) \| None \| type None |
| `sener2018mgda` | arXiv:1810.04650 | arXiv API; OpenAlex API | Multi-Task Learning as Multi-Objective Optimization \| arXiv preprint \| 2018 \| type posted-content |
| `senushkin2023aligned` | no identifier in the bib entry | Crossref REST; OpenAlex API | Independent Component Alignment for Multi-Task Learning \| 2023 IEEE/CVF Conference on Computer Vision and Pattern Recognition (CVPR) \| 2023 \| type  |
| `silva2019urbancomputing` | DOI 10.1145/3301284 | Crossref REST; OpenAlex API | Urban Computing Leveraging Location-Based Social Network Data \| ACM Computing Surveys \| 2019 \| type journal-article |
| `silva2025mtlnet` | DOI 10.21528/CBIC2025-1191324 | Crossref REST; OpenAlex API | An Investigation into Multi-Task Learning for Point-of-Interest Category Classification and Next-POI Prediction \| Anais do XVII Congresso Brasileiro  |
| `sitzmann2020implicit` | arXiv:2006.09661 | arXiv API; OpenAlex API | Implicit Neural Representations with Periodic Activation Functions \| arXiv preprint \| 2020 \| type posted-content |
| `sokolova2009measures` | DOI 10.1016/j.ipm.2009.03.002 | Crossref REST; OpenAlex API; PDF in repo: sokolova2009.pdf | A systematic analysis of performance measures for classification tasks \| Information Processing &amp; Management \| 2009 \| type journal-article |
| `song2010limits` | DOI 10.1126/science.1177170 | Crossref REST; OpenAlex API; PDF in repo: 201002-19_Science-Predictability.pdf | Limits of Predictability in Human Mobility \| Science \| 2010 \| type journal-article |
| `standley2020tasks` | arXiv:1905.07553 | arXiv API; OpenAlex API | Which Tasks Should Be Learned Together in Multi-task Learning? \| arXiv preprint \| 2019 \| type posted-content |
| `sun2020go` | DOI 10.1609/aaai.v34i01.5353 | Crossref REST; OpenAlex API | Where to Go Next: Modeling Long- and Short-Term User Preferences for Point-of-Interest Recommendation \| Proceedings of the AAAI Conference on Artific |
| `sun2024mcmg` | DOI 10.1145/3592789 | Crossref REST; OpenAlex API | A Multi-channel Next POI Recommendation Framework with Multi-granularity Check-in Signals \| ACM Transactions on Information Systems \| 2023 \| type j |
| `sun2024transtarec` | DOI 10.1109/ICCEA62105.2024.10603711 | Crossref REST; OpenAlex API | TransTARec: Time-Adaptive Translating Embedding Model for Next POI Recommendation \| 2024 5th International Conference on Computer Engineering and App |
| `sun2025kgtb` | DOI 10.48550/arXiv.2509.12350 | arXiv API; OpenAlex API | Knowledge Graph Tokenization for Behavior-Aware Generative Next POI Recommendation \| arXiv preprint \| 2025 \| type posted-content |
| `tang2020ple` | DOI 10.1145/3383313.3412236 | Crossref REST; OpenAlex API | Progressive Layered Extraction (PLE): A Novel Multi-Task Learning (MTL) Model for Personalized Recommendations \| Fourteenth ACM Conference on Recomme |
| `vandenhende2022mtl` | DOI 10.1109/TPAMI.2021.3054719 | Crossref REST; OpenAlex API | Multi-Task Learning for Dense Prediction Tasks: A Survey \| IEEE Transactions on Pattern Analysis and Machine Intelligence \| 2021 \| type journal-art |
| `vaswani2017attention` | arXiv:1706.03762 | arXiv API | Attention Is All You Need \| arXiv preprint \| 2017 \| type posted-content |
| `velickovic2019deep` | no identifier in the bib entry | OpenAlex API | Deep Graph Infomax \| Apollo (University of Cambridge) \| 2018 \| type conference-paper |
| `velivckovic2017graph` | arXiv:1710.10903 | arXiv API | Graph Attention Networks \| arXiv preprint \| 2017 \| type posted-content |
| `vielhaus2022handover` | DOI 10.1145/3551660.3560913 | Crossref REST; OpenAlex API | Handover Predictions as an Enabler for Anticipatory Service Adaptations in Next-Generation Cellular Networks \| Proceedings of the 20th ACM Internatio |
| `wang2025hamtl` | DOI 10.1007/s11227-025-07643-7 | Crossref REST; OpenAlex API | Hierarchy aware-based multi-task learning for user location prediction \| The Journal of Supercomputing \| 2025 \| type journal-article |
| `wei2022finetuned` | URL https://openreview.net/forum?id=gEZrGCozdqR | arXiv API; OpenAlex API | Finetuned Language Models Are Zero-Shot Learners \| arXiv preprint \| 2021 \| type posted-content |
| `wilcoxon1945` | DOI 10.2307/3001968 | Crossref REST; OpenAlex API; PDF in repo: wilcoxon1945.pdf | Individual Comparisons by Ranking Methods \| Biometrics Bulletin \| 1945 \| type journal-article |
| `wongso2025massivesteps` | no identifier in the bib entry | arXiv API; OpenAlex API | Massive-STEPS: Massive Semantic Trajectories for Understanding POI Check-ins -- Dataset and Benchmarks \| arXiv preprint \| 2025 \| type posted-conten |
| `wu2024torchspatial` | arXiv:2406.15658 | arXiv API; OpenAlex API | TorchSpatial: A Location Encoding Framework and Benchmark for Spatial Representation Learning \| arXiv preprint \| 2024 \| type posted-content |
| `Xia2020` | DOI 10.3390/app10196664 | Crossref REST; OpenAlex API | MTPR: A Multi-Task Learning Based POI Recommendation Considering Temporal Check-Ins and Geographical Locations \| Applied Sciences \| 2020 \| type jou |
| `xin2022domtl` | no identifier in the bib entry | arXiv API; OpenAlex API | Do Current Multi-Task Optimization Methods in Deep Learning Even Help? \| arXiv preprint \| 2022 \| type posted-content |
| `Xu2023` | DOI 10.1145/3582553 | Crossref REST; OpenAlex API | TME: Tree-guided Multi-task Embedding Learning towards Semantic Venue Annotation \| ACM Transactions on Information Systems \| 2023 \| type journal-ar |
| `yang2015tsmc` | DOI 10.1109/TSMC.2014.2327053 | Crossref REST; OpenAlex API | Modeling User Activity Preference by Leveraging User Spatial Temporal Characteristics in LBSNs \| IEEE Transactions on Systems, Man, and Cybernetics:  |
| `yang2020flashback` | DOI 10.24963/ijcai.2020/302 | Crossref REST; OpenAlex API | Location Prediction over Sparse User Mobility Traces Using RNNs: Flashback in Hidden States! \| Proceedings of the Twenty-Ninth International Joint Co |
| `yang2022getnext` | DOI 10.1145/3477495.3531983 | Crossref REST; OpenAlex API | GETNext \| Proceedings of the 45th International ACM SIGIR Conference on Research and Development in Information Retrieval \| 2022 \| type proceedings |
| `ye2013nextmove` | DOI 10.1137/1.9781611972832.19 | Crossref REST; OpenAlex API | What's Your Next Move: User Activity Prediction in Location-based Social Networks \| Proceedings of the 2013 SIAM International Conference on Data Min |
| `yu2020catdm` | DOI 10.1145/3366423.3380202 | Crossref REST; OpenAlex API | A Category-Aware Deep Model for Successive POI Recommendation on Sparse Check-in Data \| Proceedings of The Web Conference 2020 \| 2020 \| type procee |
| `yu2020pcgrad` | no identifier in the bib entry | arXiv API; OpenAlex API | Gradient Surgery for Multi-Task Learning \| arXiv preprint \| 2020 \| type posted-content |
| `yu2024survey` | arXiv:2404.18961 | arXiv API; OpenAlex API | Unleashing the Power of Multi-Task Learning: A Comprehensive Survey Spanning Traditional, Deep, and Pretrained Foundation Model Eras \| arXiv preprint |
| `zeng2019next` | DOI 10.1007/978-3-030-30146-0_21 | Crossref REST; OpenAlex API; Semantic Scholar API | A Next Location Predicting Approach Based on a Recurrent Neural Network and Self-attention \| Lecture Notes of the Institute for Computer Sciences, So |
| `Zhang2020` | DOI 10.24963/ijcai.2020/491 | Crossref REST; OpenAlex API | An Interactive Multi-Task Learning Framework for Next POI Recommendation with Uncertain Check-ins \| Proceedings of the Twenty-Ninth International Joi |
| `zhang2021survey` | DOI 10.1109/TKDE.2021.3070203 | Crossref REST; OpenAlex API | A Survey on Multi-Task Learning \| IEEE Transactions on Knowledge and Data Engineering \| 2022 \| type journal-article |
| `zhu2022drrgnn` | DOI 10.1145/3529091 | Crossref REST; OpenAlex API | Predicting a Person’s Next Activity Region with a Dynamic Region-Relation-Aware Graph Neural Network \| ACM Transactions on Knowledge Discovery from D |

**Six references read as full PDFs**, not only as records:

| Key | PDF | Why the full text was needed |
|---|---|---|
| `standley2020tasks` | arXiv 1905.07553v3, downloaded this session | ITEM 3: the abstract alone cannot establish what the paper does and does not support |
| `caruana1997multitask` | fetched open-access, DOI 10.1023/A:1007379606734 | cited 13 times, the most-cited key in the document |
| `huang2023hgi` | `science/articles/Learning urban region representations ... .pdf` | 8 citing sites, all needing the POI-region-city hierarchy and the corruption mechanism |
| `song2010limits` | `science/articles/201002-19_Science-Predictability.pdf` | the 93 percent figure in Chapter 1 is a quoted number |
| `pedregosa2011sklearn` | `science/articles/Pedregosa2011_ScikitLearn.pdf` | the twice-ruled site at `2_fundamentals.tex:465` |
| `sokolova2009measures` | `science/articles/sokolova2009.pdf` | the macro-F1 weighting claim in Appendix D |

Also read from the repository, not from a publisher: `moura2025mobilityaware`
(`articles/[mobiwac]/mobility/On_the_Design_of_Mobility-Aware_Systems_A_Tourists_Perspective.pdf`,
for the machine-learning-as-future-work claim at `5_mobiwac.tex:810`) and `santos2024urban`
(`articles/dissertacao/exemples/germano/Dissertação_Mestrado___Germano.pdf`, the only entry with no
external source of record).

**Numbers quoted in this report, and where each comes from.** No number here was computed by me;
counts were produced by a script over the source and are reported as it printed them.

| Number | Source | Convention |
|---|---|---|
| 247 sites / 265 key instances | parse of the eleven chapter files plus `tables/frame/lineage.tex`, `%` comments stripped | a multi-key `\cite` counts once per key; comment-only sites excluded |
| 255 raw `\cite` / 273 raw keys | `grep` over the same files **including** comments | given only to account for the difference |
| 100 bib entries, 0 duplicate keys, 0 dangling cites, 0 uncited | parse of `src/references.bib` against the union of used keys | |
| 105 / 100 pages | `Output written on` in `build/main.log` and `build/main_final.log` | after my edits, both builds converged |
| 104 pages at HEAD | `git show HEAD:articles/dissertacao/src/dissertacao.pdf`, page count read from the PDF | the committed artifact ANCHORS.md measured |
| `Overfull \hbox (113.58371pt too wide)` | `build/main.log`, first attempt at the Sphere2Vec errata row | pt too wide, as pdflatex reports it |
| 44 open / 44 close braces | brace count over the comment-stripped `bib_errata.tex` | delta 0, the `{\small}` group intact |
| 244,987 characters | extracted text of the Germano dissertation PDF | the corpus searched for ethics-committee terms |

## 10 · `[VERIFY]` flags

Four, all narrow and each with a named check that would close it:

1. **`[VERIFY: 3_cbic.tex:244, nash]`** — "task weights can be updated less frequently,
   significantly reducing runtime while maintaining performance". Not in the abstract of
   arXiv:2202.01017. Check: locate the passage in the paper body. This same subsection has already
   had two other cost claims corrected against this paper, so it has been read here before.
2. **`[VERIFY: 3_cbic.tex:145, huang2022estimating]`** — the edge-weight formula
   `w_ij = log((1+D^1.5)/(1+d_ij^1.5))` is attributed to the cited work. Check: locate the formula
   in the paper, or restate it as this work's own construction.
3. **`[VERIFY: 4_courb.tex:60, rahmani2019category]`** — Crossref returns a truncated four-sentence
   abstract for this ICTIR paper. The categorical half of the citing sentence is supported; the
   sequential half is not visible in the record. Check: the paper body.
4. **`[VERIFY: 5_mobiwac.tex:750, huang2024cslsl]`** — the sentence cites CSLSL's own ablation (its
   chain against a shared-trunk parallel variant). An abstract does not carry ablations. Check: the
   paper's results section.

A fifth, narrower still and recorded rather than flagged: `5_mobiwac.tex:409` asserts that CTLE's
training never sees the category vocabulary. That is consistent with the abstract, which names only
locations and temporal information as inputs, but an abstract cannot prove an absence.

## 11 · What I could not confirm

Stated plainly, since a smoothed-over gap is the defect this repository keeps catching.

0. **Two of my own evidence strings were defective and I did not catch them until a review pass
   pointed at one.** The `abstract` field I stored for `wilcoxon1945` held the JSTOR terms-of-use
   notice, labelled as though it were paper content; the field for `huang2023hgi` was a single space,
   because my extraction looked for a spaced `A B S T R A C T` header this PDF does not use. Both are
   fixed in `_sor_snapshot.json`: HGI now carries 1,674 characters read from the paper, and Wilcoxon
   carries an empty abstract with an explicit note that no abstract or body text is obtainable. I then
   swept the whole snapshot for the same class: **zero** remaining boilerplate-contaminated abstracts,
   and six entries with an honestly empty one (`Halder2021`, `capanema2023poirgnn`, `santos2024urban`,
   `wang2025hamtl`, `wilcoxon1945`, `zeng2019next`). No verdict in this report rested on either bad
   string: the screen returned UNVERIFIABLE at all nine affected sites and said why, and the manual
   pass read the HGI paper directly. What this cost is not accuracy but a clean audit trail, and it is
   the reason the screen's output is never presented here as a verdict.

1. **The fan-out the task specified did not happen.** `host.delegate` is unavailable in this frame
   (root-only; this frame is a leaf). I ran all seven units myself. The per-chapter reports exist and
   nothing was sampled, but the **independence** of seven fresh readers does not. AGENT_GUARDRAILS L6
   asks for fresh eyes; this is one pair. Treat it accordingly.
2. **Four entries return no abstract at any source of record I can reach**, so for those the check
   ran on the record and title only: `capanema2023poirgnn` (Elsevier), `wang2025hamtl` (Springer),
   `zeng2019next` (Springer chapter), and `Halder2021` (Springer, cited once at `3_cbic.tex:125`).
   Their publisher landing pages are outside the network allowlist; Crossref deposits no abstract and
   Semantic Scholar returns the records with empty abstract fields. Every citing site for these keys
   is an identity-of-baseline or pattern-continuation pointer that the resolved record supports; no
   mechanism claim rests on any of them. But I did not read those four papers.
3. **The comparative results claims at `5_mobiwac.tex:664-666` were not audited.** What a citation
   must support there is each baseline's identity, and each record does. Whether the joint model is
   in fact above every external baseline on both tasks across all six datasets is a **number** claim
   under AGENT_GUARDRAILS §2, whose single source of truth for Chapter 5 is `RESULTS_BOARD.md`. That
   is a different audit and I did not perform it. The same applies to every reported figure in
   Chapters 3 and 4 that sits beside a citation.
4. **The `[VERIFY]` flags in section 10 are open**, four of them, each needing a page from a paper
   body I did not obtain.
5. **`santos2024urban` has no external identifier and never will**, being a UFV master's
   dissertation. I verified it against the document in the repository, which is the best available
   evidence and is not a source of record in the Crossref sense. The entry should carry a bib comment
   saying so, or a future existence-checker will read the absence as a defect. I did not add that
   comment: it is a bib edit outside ITEM 2's remit.
6. **The `make check` page-count gate fails and I did not fix it.** Its own message misdiagnoses the
   cause (`main.log` does carry the page count). Running `sync_page_counts.py --write` would edit
   `CLAUDE.md`, `PLAN.md` and other files outside my remit while the count is still moving under
   other agents' work. Hand-off, not a fix.
7. **I did not verify the load-bearing ranking in section 2 against the author's own sense of the
   argument.** It is my reading of what each claim carries. The dispositions follow the ranking, so if
   the ranking is wrong the priorities are wrong; the evidence per row does not depend on it.

## 12 · Recommended order of work for the author

1. **Rule on the Standley site** (section 5.4, option A recommended). It is the one row the author
   asked for by name, it is a claim rather than a typo, and the drafted sentence and Appendix B row
   are ready to apply.
2. **Take the four other high-load rows together**, since three of the four are one-key swaps to
   references already in the bibliography: `ruder2017sluice` -> `baxter2000model` at `3_cbic.tex:213`,
   `belkin2003laplacian` -> `Xu2023` at `4_courb.tex:219`, and adding `standley2020tasks` beside
   Caruana at `5_mobiwac.tex:44`. Only `4_courb.tex:161` needs a prose decision rather than a key.
3. **Fix the three paired defects as pairs** (`Xia2020` at two sites, the Rußwurm encoder at two
   sites, the TorchSpatial "first validated" attribution at a frame site and in the published CoUrb
   introduction), so the document does not describe one system two ways.
4. **Batch the remaining low-load Chapter 3 wording rows** into one Appendix B wording-table pass:
   `:102`, `:115`, `:123` (both keys), `:125`, `:127`. Each is one clause.
5. **Close or accept the four `[VERIFY]` flags.**
6. **Re-run `sync_page_counts.py --write`** once the other agents' edits have landed and the page
   count has stopped moving.

---

**Companion reports** (one per unit, each with its own counts, full verdict table and source ledger):
`11_claims_1_introduction.md`, `11_claims_2_fundamentals.md`, `11_claims_3_cbic.md`,
`11_claims_4_courb.md`, `11_claims_5_mobiwac.md`, `11_claims_6_conclusion.md`,
`11_claims_appendices.md`. The machine-readable verdict set is `_final_verdicts.json` in this folder,
with the intermediate resolution and screening data alongside it.


---

# Anexo · Os veredictos por unidade, linha a linha

> **Consolidado em 2026-08-28.** Estas sete tabelas estavam em sete ficheiros irmaos
> (`11_claims_*.md`) da mesma corrida, mesmo auditor, mesma data. Eram um relatorio em sete
> ficheiros, nao sete relatorios. O conteudo esta VERBATIM; so os cabecalhos `##` sao novos.


---

## `11_claims_1_introduction.md`

# 11_claims_1_introduction.md — citation claim-support audit, Chapter 1, Introduction

**Unit:** `src/chapters/1_introduction.tex`  
**Run:** 2026-07-28, round 6, as the per-chapter pass the author asked for by name (COD-008 decision).  
**Errata regime for this unit:** frame chapter: author's own text, no errata mechanism; claim changes are [NEEDS SIGN-OFF]-class.

## 1 · Counts (every citation in the unit, not a sample)

- `\cite` commands in the unit: **8**, on **8** source lines, carrying **9** key instances (a multi-key `\cite` counts once per key). Every one was audited.
- Distinct bibliography keys used: **9**.
- Verdicts: **SUPPORTED** 8, **PARTIAL** 1.

Comments were stripped before counting, so a key that appears only inside a `%` comment is not counted; every counted site renders.

## 2 · Every citation, with its verdict

Verdict scale: SUPPORTED, the citing sentence's attribution is present in or a fair paraphrase of the
source; PARTIAL, part is supported and part is not, or the sentence is stronger than the source;
NOT-SUPPORTED, the attribution is absent from or contradicted by the source; UNVERIFIABLE, the source
of record does not carry enough to decide and the attribution is not implausible.

| # | Site (file:line) | Key | Verdict | Evidence quoted from the source (under 20 words) |
|---|---|---|---|---|
| 1 | `1_introduction.tex:38` | `song2010limits` | SUPPORTED | "there was 93% predictability across the whole user base" |
| 2 | `1_introduction.tex:45` | `luca2021mobilitysurvey` | SUPPORTED | "its impact on several aspects of our society, such as disease spreading, urban planning, well-being, pollution" |
| 3 | `1_introduction.tex:46` | `Xu2023` | SUPPORTED | "categories (e.g., Bar and Museum ) are vital to the task, as they often serve as excellent semantic characterization of the venues" |
| 4 | `1_introduction.tex:50` | `mai2023sphere2vecgeneralpurposelocationrepresentation` | SUPPORTED | "fine-grained species recognition, Flickr image recognition, and remote sensing image classification" |
| 5 | `1_introduction.tex:50` | `wu2024torchspatial` | PARTIAL | "a learning framework and benchmark for location (point) encoding" |
| 6 | `1_introduction.tex:70` | `caruana1997multitask` | SUPPORTED | "improves generalization by using the domain information contained in the training signals of related tasks" |
| 7 | `1_introduction.tex:72` | `kokkinos2016ubernet` | SUPPORTED | "jointly handles low-, mid-, and high-level vision tasks in a unified architecture" |
| 8 | `1_introduction.tex:73` | `lipton2015learning` | SUPPORTED | "multilabel classification of diagnoses, training a model to classify 128 diagnoses given 13 frequently but irregularly sampled clinical measurements" |
| 9 | `1_introduction.tex:75` | `wei2022finetuned` | SUPPORTED | "finetuning language models on a collection of tasks described via instructions" |
## 3 · Failures and partials in this unit, in detail

### `1_introduction.tex:50` — `wu2024torchspatial` — **PARTIAL**

**Citing sentence.** The field also imports its tools: part of the representation machinery used in this research, the spatial location encoders of the second study, was first validated on geospatial tasks such as species recognition and remote sensing classification~\cite{mai2023sphere2vecgeneralpurposelocationrepresentation,wu2024torchspatial}.

**Reference resolved.** arXiv:2406.15658. Source of record: arXiv API; OpenAlex API. Record reads: TorchSpatial: A Location Encoding Framework and Benchmark for Spatial Representation Learning | arXiv preprint | 2024 | type posted-content.

**Located passage.** "a learning framework and benchmark for location (point) encoding"

**Why.** TorchSpatial is a framework and benchmark that consolidates 15 existing location encoders and supplies LocBench (7 geo-aware image classification and 10 regression datasets). It is where the encoders are benchmarked on geospatial tasks, not where they were "first validated". Sphere2Vec, the co-cited entry, does carry the original validation.

**Recommended disposition.** Narrow "first validated" to "validated": the clause is true of both works under the weaker verb, and Sphere2Vec alone supports the stronger one.

## 4 · Source ledger for this unit

Every distinct key cited in this unit, the identifier it resolved by, and where I opened it this session.

| Key | Identifier | Opened at | Record as returned |
|---|---|---|---|
| `Xu2023` | DOI 10.1145/3582553 | Crossref REST; OpenAlex API | TME: Tree-guided Multi-task Embedding Learning towards Semantic Venue Annotation \| ACM Transactions on Information Systems \| 2023 \| type journal-article |
| `caruana1997multitask` | DOI 10.1023/A:1007379606734 | Crossref REST; OpenAlex API; PDF in repo: 10.1023_A_1007379606734.pdf | Multitask Learning \| Machine Learning \| 1997 \| type journal-article |
| `kokkinos2016ubernet` | arXiv:1609.02132 | arXiv API; OpenAlex API | UberNet: Training a `Universal' Convolutional Neural Network for Low-, Mid-, and High-Level Vision using Diverse Datasets and Limited Memory \| arXiv preprint \| 2016 \|  |
| `lipton2015learning` | arXiv:1511.03677 | arXiv API; OpenAlex API | Learning to Diagnose with LSTM Recurrent Neural Networks \| arXiv preprint \| 2015 \| type posted-content |
| `luca2021mobilitysurvey` | DOI 10.1145/3485125 | Crossref REST; OpenAlex API | A Survey on Deep Learning for Human Mobility \| ACM Computing Surveys \| 2021 \| type journal-article |
| `mai2023sphere2vecgeneralpurposelocationrepresentation` | arXiv:2306.17624 | arXiv API; OpenAlex API | Sphere2Vec: A General-Purpose Location Representation Learning over a Spherical Surface for Large-Scale Geospatial Predictions \| ISPRS Journal of Photogrammetry and Remo |
| `song2010limits` | DOI 10.1126/science.1177170 | Crossref REST; OpenAlex API; PDF in repo: 201002-19_Science-Predictability.pdf | Limits of Predictability in Human Mobility \| Science \| 2010 \| type journal-article |
| `wei2022finetuned` | URL https://openreview.net/forum?id=gEZrGCozdqR | arXiv API; OpenAlex API | Finetuned Language Models Are Zero-Shot Learners \| arXiv preprint \| 2021 \| type posted-content |
| `wu2024torchspatial` | arXiv:2406.15658 | arXiv API; OpenAlex API | TorchSpatial: A Location Encoding Framework and Benchmark for Spatial Representation Learning \| arXiv preprint \| 2024 \| type posted-content |

## 5 · What I could not confirm in this chapter

Nothing outstanding beyond the single PARTIAL above. The `song2010limits` figure at `:38` was
checked against the paper itself and not only its abstract: `science/articles/201002-19_Science-
Predictability.pdf` states "a potential 93% average predictability in user mobility" in its summary
and gives Pmax approximately 0.93 in the body, which is what the chapter's "about 93 percent"
reports, with the chapter's own hedge ("potential predictability") matching the source's.

---

## `11_claims_2_fundamentals.md`

# 11_claims_2_fundamentals.md — citation claim-support audit, Chapter 2, Fundamentals

**Unit:** `src/chapters/2_fundamentals.tex`  
**Run:** 2026-07-28, round 6, as the per-chapter pass the author asked for by name (COD-008 decision).  
**Errata regime for this unit:** frame chapter: author's own text, no errata mechanism; claim changes are [NEEDS SIGN-OFF]-class.

## 1 · Counts (every citation in the unit, not a sample)

- `\cite` commands in the unit: **69**, on **69** source lines, carrying **70** key instances (a multi-key `\cite` counts once per key). Every one was audited.
- Distinct bibliography keys used: **67**.
- Verdicts: **SUPPORTED** 70.

Comments were stripped before counting, so a key that appears only inside a `%` comment is not counted; every counted site renders.

## 2 · Every citation, with its verdict

Verdict scale: SUPPORTED, the citing sentence's attribution is present in or a fair paraphrase of the
source; PARTIAL, part is supported and part is not, or the sentence is stronger than the source;
NOT-SUPPORTED, the attribution is absent from or contradicted by the source; UNVERIFIABLE, the source
of record does not carry enough to decide and the attribution is not implausible.

| # | Site (file:line) | Key | Verdict | Evidence quoted from the source (under 20 words) |
|---|---|---|---|---|
| 1 | `2_fundamentals.tex:31` | `silva2019urbancomputing` | SUPPORTED | "offers unprecedented geographic and temporal resolutions" |
| 2 | `2_fundamentals.tex:33` | `cho2011gowalla` | SUPPORTED | "Short-ranged travel is periodic both spatially and temporally...while long-distance travel is more influenced by social network ties" |
| 3 | `2_fundamentals.tex:35` | `song2010limits` | SUPPORTED | "there was 93% predictability across the whole user base" |
| 4 | `2_fundamentals.tex:47` | `luca2021mobilitysurvey` | SUPPORTED | "leading deep learning solutions to next-location prediction, crowd flow prediction, trajectory generation, and flow generation" |
| 5 | `2_fundamentals.tex:57` | `Xu2023` | SUPPORTED | "we address the problem of semantic venue annotation, i.e., labeling the venue with a semantic category" |
| 6 | `2_fundamentals.tex:68` | `liu2016strnn` | SUPPORTED | "time-specific transition matrices for different time intervals and distance-specific transition matrices for different geographical distances" |
| 7 | `2_fundamentals.tex:70` | `feng2018deepmove` | SUPPORTED | "historical attention model with two mechanisms to capture the multi-level periodicity" |
| 8 | `2_fundamentals.tex:71` | `kong2018hstlstm` | SUPPORTED | "hierarchical extension of the proposed ST-LSTM (HST-LSTM)...naturally combines spatial-temporal influence into LSTM" |
| 9 | `2_fundamentals.tex:73` | `yang2020flashback` | SUPPORTED | "explicitly uses spatiotemporal contexts to search past hidden states with high predictive power" |
| 10 | `2_fundamentals.tex:75` | `luo2021stan` | SUPPORTED | "point-to-point interaction between non-adjacent locations and non-consecutive check-ins with explicit spatio-temporal effect" |
| 11 | `2_fundamentals.tex:77` | `lian2020geosan` | SUPPORTED | "GeoSAN represents the hierarchical gridding of each GPS point with a self-attention based geography encoder" |
| 12 | `2_fundamentals.tex:79` | `yang2022getnext` | SUPPORTED | "propose a user-agnostic global trajectory flow map and a novel Graph Enhanced Transformer model (GETNext) to better exploit the extensive collaborativ" |
| 13 | `2_fundamentals.tex:85` | `lin2021ctle` | SUPPORTED | "calculates a location's representation vector with consideration of its specific contextual neighbors in trajectories" |
| 14 | `2_fundamentals.tex:90` | `Lim2022` | SUPPORTED | "perform a Hierarchical Beam Search (HBS) on the different region and POI distributions to hierarchically reduce the search space" |
| 15 | `2_fundamentals.tex:91` | `yu2020catdm` | SUPPORTED | "incorporates POI category and geographical influence to reduce search space to overcome data sparsity" |
| 16 | `2_fundamentals.tex:94` | `zhu2022drrgnn` | SUPPORTED | "predicting the next activity region (AR)... studies... individual-level inter-regional mobility behavior" |
| 17 | `2_fundamentals.tex:95` | `capanema2023poirgnn` | SUPPORTED | "Combining recurrent and Graph Neural Networks to predict the next place's category" |
| 18 | `2_fundamentals.tex:139` | `mikolov2013word2vec` | SUPPORTED | "continuous vector representations of words from very large data sets" |
| 19 | `2_fundamentals.tex:141` | `perozzi2014deepwalk` | SUPPORTED | "generalizes recent advancements in language modeling ... from sequences of words to graphs" |
| 20 | `2_fundamentals.tex:143` | `grover2016node2vec` | SUPPORTED | "design a biased random walk procedure, which efficiently explores diverse neighborhoods... generalizes prior work which is based on rigid notions" |
| 21 | `2_fundamentals.tex:145` | `kipf2017gcn` | SUPPORTED | "localized first-order approximation of spectral graph convolutions" |
| 22 | `2_fundamentals.tex:147` | `velivckovic2017graph` | SUPPORTED | "enable (implicitly) specifying different weights to different nodes in a neighborhood, without requiring any kind of costly matrix operation" |
| 23 | `2_fundamentals.tex:149` | `hamilton2017graphsage` | SUPPORTED | "we learn a function that generates embeddings by sampling and aggregating features from a node's local neighborhood" |
| 24 | `2_fundamentals.tex:154` | `belghazi2018mine` | SUPPORTED | "estimation of mutual information between high dimensional continuous random variables can be achieved by gradient descent" |
| 25 | `2_fundamentals.tex:156` | `hjelm2019dim` | SUPPORTED | "maximizing mutual information between an input and the output of a deep neural network encoder... incorporating knowledge about locality" |
| 26 | `2_fundamentals.tex:159` | `velickovic2019deep` | SUPPORTED | "DGI relies on maximizing mutual information between patch representations and corresponding high-level summaries of graphs" |
| 27 | `2_fundamentals.tex:163` | `huang2023hgi` | SUPPORTED | "the mutual information among the POI - region - city hierarchy is leveraged as the objective" |
| 28 | `2_fundamentals.tex:192` | `lin2021ctle` | SUPPORTED | "calculates a location's representation vector with consideration of its specific contextual neighbors in trajectories" |
| 29 | `2_fundamentals.tex:201` | `kazemi2019time2vec` | SUPPORTED | "model-agnostic vector representation for time, called Time2Vec, that can be easily imported into many existing" |
| 30 | `2_fundamentals.tex:204` | `sitzmann2020implicit` | SUPPORTED | "demonstrate that these networks, dubbed sinusoidal representation networks or Sirens, are ideally suited for representing complex natural signals and " |
| 31 | `2_fundamentals.tex:205` | `mai2020multiscalerepresentationlearningspatial` | SUPPORTED | "propose a representation learning model called Space2Vec to encode the absolute positions and spatial relationships of places" |
| 32 | `2_fundamentals.tex:208` | `mai2023sphere2vecgeneralpurposelocationrepresentation` | SUPPORTED | "propose a multi-scale location encoder called Sphere2Vec which can preserve spherical distances when encoding point coordinates on a spherical surface" |
| 33 | `2_fundamentals.tex:211` | `russwurm2024geographiclocationencodingspherical` | SUPPORTED | "combines spherical harmonic basis functions, natively defined on spherical surfaces, with sinusoidal representation networks" |
| 34 | `2_fundamentals.tex:213` | `perez2018film` | SUPPORTED | "FiLM layers influence neural network computation via a simple, feature-wise affine transformation based on conditioning information" |
| 35 | `2_fundamentals.tex:284` | `caruana1997multitask` | SUPPORTED | "improves generalization by using the domain information contained in the training signals of related tasks... learning tasks in parallel while using a" |
| 36 | `2_fundamentals.tex:293` | `ruder2017mtloverview` | SUPPORTED | "introduces the two most common methods for MTL in Deep Learning" |
| 37 | `2_fundamentals.tex:296` | `misra2016cross` | SUPPORTED | "These units combine the activations from multiple networks and can be trained end-to-end" |
| 38 | `2_fundamentals.tex:298` | `ma2018mmoe` | SUPPORTED | "Modeling Task Relationships in Multi-task Learning with Multi-gate Mixture-of-Experts" |
| 39 | `2_fundamentals.tex:300` | `tang2020ple` | SUPPORTED | "PLE separates shared components and task-specific components explicitly and adopts a progressive routing mechanism" |
| 40 | `2_fundamentals.tex:301` | `hazimeh2021dselectk` | SUPPORTED | "a continuously differentiable and sparse gate for MoE, based on a novel binary encoding formulation" |
| 41 | `2_fundamentals.tex:310` | `standley2020tasks` | SUPPORTED | "this often leads to inferior overall performance as task objectives can compete, which consequently poses the question: which tasks should and should " |
| 42 | `2_fundamentals.tex:313` | `sener2018mgda` | SUPPORTED | "this workaround is only valid when the tasks do not compete, which is rarely the case" |
| 43 | `2_fundamentals.tex:317` | `kendall2018uncertainty` | SUPPORTED | "weighs multiple loss functions by considering the homoscedastic uncertainty of each task" |
| 44 | `2_fundamentals.tex:319` | `chen2018gradnorm` | SUPPORTED | "gradient normalization (GradNorm) algorithm that automatically balances training in deep multitask models by dynamically tuning gradient magnitudes" |
| 45 | `2_fundamentals.tex:320` | `liu2019dwa` | SUPPORTED | "less sensitive to various weighting schemes in the multi-task loss function" |
| 46 | `2_fundamentals.tex:322` | `yu2020pcgrad` | SUPPORTED | "projects a task's gradient onto the normal plane of the gradient of any other task that has a conflicting gradient" |
| 47 | `2_fundamentals.tex:324` | `liu2021cagrad` | SUPPORTED | "leveraging the worst local improvement of individual tasks to regularize the algorithm trajectory. CAGrad ... provably converges to a minimum" |
| 48 | `2_fundamentals.tex:327` | `nash` | SUPPORTED | "viewing the gradients combination step as a bargaining game... known as the Nash Bargaining Solution" |
| 49 | `2_fundamentals.tex:329` | `senushkin2023aligned` | SUPPORTED | "aligning the orthogonal components of the linear system of gradients... condition number as a stability criterion" |
| 50 | `2_fundamentals.tex:331` | `liu2023famo` | SUPPORTED | "decreases task losses in a balanced way using $\mathcal{O}(1)$ space and time" |
| 51 | `2_fundamentals.tex:332` | `lin2022rlw` | SUPPORTED | "RW methods can achieve comparable performance with state-of-the-art baselines" |
| 52 | `2_fundamentals.tex:334` | `xin2022domtl` | SUPPORTED | "MTO methods do not yield any performance improvements beyond what is achievable via traditional optimization approaches" |
| 53 | `2_fundamentals.tex:336` | `kurin2022scalarization` | SUPPORTED | "unitary scalarization, coupled with standard regularization and stabilization techniques...matches or improves upon the performance of complex multi-t" |
| 54 | `2_fundamentals.tex:338` | `vandenhende2022mtl` | SUPPORTED | "we consider MTL from a network architecture point-of-view... we examine various optimization methods to tackle the joint learning" |
| 55 | `2_fundamentals.tex:338` | `yu2024survey` | SUPPORTED | "categorizes MTL techniques into five key areas: regularization, relationship learning, feature propagation, optimization, and pre-training" |
| 56 | `2_fundamentals.tex:352` | `Liao2018` | SUPPORTED | "novel Context Aware Recurrent Unit is designed to integrate the sequential dependency and temporal regularity" |
| 57 | `2_fundamentals.tex:354` | `huang2024cslsl` | SUPPORTED | "explicitly model the “ when → what → where ”, a.k.a. “ time → activity → location ” decision logic" |
| 58 | `2_fundamentals.tex:362` | `silva2025mtlnet` | SUPPORTED | "did not consistently yield substantial improvements over the single-task baselines across both tasks" |
| 59 | `2_fundamentals.tex:417` | `cho2011gowalla` | SUPPORTED | "humans experience a combination of periodic movement that is geographically limited and seemingly random jumps correlated with their social networks" |
| 60 | `2_fundamentals.tex:420` | `wongso2025massivesteps` | SUPPORTED | "the over-reliance on older datasets from 2012-2013" |
| 61 | `2_fundamentals.tex:422` | `yang2015tsmc` | SUPPORTED | "real-world datasets collected from New York and Tokyo" |
| 62 | `2_fundamentals.tex:431` | `sokolova2009measures` | SUPPORTED | "systematic analysis of twenty four performance measures used in the complete spectrum of Machine Learning classification tasks" |
| 63 | `2_fundamentals.tex:444` | `maninis2019attentive` | SUPPORTED | "a smooth trade-off between computation and multi-task accuracy" |
| 64 | `2_fundamentals.tex:451` | `gambs2012mmc` | SUPPORTED | "extend a mobility model called Mobility Markov Chain (MMC)" |
| 65 | `2_fundamentals.tex:454` | `song2010limits` | SUPPORTED | "there was 93% predictability across the whole user base" |
| 66 | `2_fundamentals.tex:462` | `kohavi1995crossval` | SUPPORTED | "the best method to use for model selection is ten-fold strati ed cross validation" |
| 67 | `2_fundamentals.tex:465` | `pedregosa2011sklearn` | SUPPORTED | "Scikit-learn is a Python module integrating a wide range of state-of-the-art machine learning algorithms" |
| 68 | `2_fundamentals.tex:476` | `wilcoxon1945` | SUPPORTED | "Individual Comparisons by Ranking Methods" |
| 69 | `2_fundamentals.tex:481` | `holm1979` | SUPPORTED | "widely applicable multiple test procedure of the sequentially rejective type" |
| 70 | `2_fundamentals.tex:484` | `lakens2017tost` | SUPPORTED | "the two one-sided tests (TOST) procedure discussed in this article, an upper and lower equivalence bound is specified" |
## 3 · Failures and partials in this unit, in detail

None. Every citation in this unit is SUPPORTED.

## 4 · Source ledger for this unit

Every distinct key cited in this unit, the identifier it resolved by, and where I opened it this session.

| Key | Identifier | Opened at | Record as returned |
|---|---|---|---|
| `Liao2018` | DOI 10.24963/ijcai.2018/477 | Crossref REST; OpenAlex API | Predicting Activity and Location with Multi-task Context Aware Recurrent Neural Network \| Proceedings of the Twenty-Seventh International Joint Conference on Artificial  |
| `Lim2022` | DOI 10.1145/3477495.3531989 | Crossref REST; OpenAlex API | Hierarchical Multi-Task Graph Recurrent Network for Next POI Recommendation \| Proceedings of the 45th International ACM SIGIR Conference on Research and Development in I |
| `Xu2023` | DOI 10.1145/3582553 | Crossref REST; OpenAlex API | TME: Tree-guided Multi-task Embedding Learning towards Semantic Venue Annotation \| ACM Transactions on Information Systems \| 2023 \| type journal-article |
| `belghazi2018mine` | arXiv:1801.04062 | arXiv API; OpenAlex API | MINE: Mutual Information Neural Estimation \| ICML 2018 \| 2018 \| type posted-content |
| `capanema2023poirgnn` | DOI 10.1016/j.adhoc.2022.103016 | Crossref REST; OpenAlex API | Combining recurrent and Graph Neural Networks to predict the next place’s category \| Ad Hoc Networks \| 2023 \| type journal-article |
| `caruana1997multitask` | DOI 10.1023/A:1007379606734 | Crossref REST; OpenAlex API; PDF in repo: 10.1023_A_1007379606734.pdf | Multitask Learning \| Machine Learning \| 1997 \| type journal-article |
| `chen2018gradnorm` | no identifier in the bib entry | arXiv API; OpenAlex API | GradNorm: Gradient Normalization for Adaptive Loss Balancing in Deep Multitask Networks \| Proceedings of the 35th International Conference on Machine Learning (2018), 79 |
| `cho2011gowalla` | DOI 10.1145/2020408.2020579 | Crossref REST; OpenAlex API | Friendship and mobility \| Proceedings of the 17th ACM SIGKDD international conference on Knowledge discovery and data mining \| 2011 \| type proceedings-article |
| `feng2018deepmove` | DOI 10.1145/3178876.3186058 | Crossref REST; OpenAlex API | DeepMove \| Proceedings of the 2018 World Wide Web Conference on World Wide Web - WWW '18 \| 2018 \| type proceedings-article |
| `gambs2012mmc` | DOI 10.1145/2181196.2181199 | Crossref REST; OpenAlex API | Next place prediction using mobility Markov chains \| Proceedings of the First Workshop on Measurement, Privacy, and Mobility \| 2012 \| type proceedings-article |
| `grover2016node2vec` | DOI 10.1145/2939672.2939754 | Crossref REST; OpenAlex API | node2vec \| Proceedings of the 22nd ACM SIGKDD International Conference on Knowledge Discovery and Data Mining \| 2016 \| type proceedings-article |
| `hamilton2017graphsage` | arXiv:1706.02216 | arXiv API; OpenAlex API | Inductive Representation Learning on Large Graphs \| arXiv preprint \| 2017 \| type posted-content |
| `hazimeh2021dselectk` | arXiv:2106.03760 | arXiv API; OpenAlex API | DSelect-k: Differentiable Selection in the Mixture of Experts with Applications to Multi-Task Learning \| arXiv preprint \| 2021 \| type posted-content |
| `hjelm2019dim` | arXiv:1808.06670 | arXiv API; OpenAlex API | Learning deep representations by mutual information estimation and maximization \| arXiv preprint \| 2018 \| type posted-content |
| `holm1979` | no identifier in the bib entry | OpenAlex API | A Simple Sequentially Rejective Multiple Test Procedure \| Scandinavian Journal of Statistics \| 1979 \| type article |
| `huang2023hgi` | DOI 10.1016/j.isprsjprs.2022.11.021 | Crossref REST; OpenAlex API; Semantic Scholar API; PDF in repo: Learning urban region representations with POIs and hierarchical graph infomax.pdf | Learning urban region representations with POIs and hierarchical graph infomax \| ISPRS Journal of Photogrammetry and Remote Sensing \| 2023 \| type journal-article |
| `huang2024cslsl` | DOI 10.1140/epjds/s13688-024-00460-7 | Crossref REST; OpenAlex API | Human mobility prediction with causal and spatial-constrained multi-task network \| EPJ Data Science \| 2024 \| type journal-article |
| `kazemi2019time2vec` | arXiv:1907.05321 | arXiv API; OpenAlex API | Time2Vec: Learning a Vector Representation of Time \| arXiv preprint \| 2019 \| type posted-content |
| `kendall2018uncertainty` | DOI 10.1109/CVPR.2018.00781 | Crossref REST; OpenAlex API | Multi-task Learning Using Uncertainty to Weigh Losses for Scene Geometry and Semantics \| 2018 IEEE/CVF Conference on Computer Vision and Pattern Recognition \| 2018 \| t |
| `kipf2017gcn` | arXiv:1609.02907 | arXiv API; OpenAlex API | Semi-Supervised Classification with Graph Convolutional Networks \| arXiv preprint \| 2016 \| type posted-content |
| `kohavi1995crossval` | no identifier in the bib entry | OpenAlex API | A Study of Cross-Validation and Bootstrap for Accuracy Estimation and Model Selection \| (no venue in record) \| 1995 \| type article |
| `kong2018hstlstm` | DOI 10.24963/ijcai.2018/324 | Crossref REST; OpenAlex API | HST-LSTM: A Hierarchical Spatial-Temporal Long-Short Term Memory Network for Location Prediction \| Proceedings of the Twenty-Seventh International Joint Conference on Ar |
| `kurin2022scalarization` | no identifier in the bib entry | arXiv API; OpenAlex API | In Defense of the Unitary Scalarization for Deep Multi-Task Learning \| arXiv preprint \| 2022 \| type posted-content |
| `lakens2017tost` | DOI 10.1177/1948550617697177 | Crossref REST; OpenAlex API | Equivalence Tests \| Social Psychological and Personality Science \| 2017 \| type journal-article |
| `lian2020geosan` | DOI 10.1145/3394486.3403252 | Crossref REST; OpenAlex API | Geography-Aware Sequential Location Recommendation \| Proceedings of the 26th ACM SIGKDD International Conference on Knowledge Discovery &amp; Data Mining \| 2020 \| type |
| `lin2021ctle` | DOI 10.1609/aaai.v35i5.16548 | Crossref REST; OpenAlex API | Pre-training Context and Time Aware Location Embeddings from Spatial-Temporal Trajectories for User Next Location Prediction \| Proceedings of the AAAI Conference on Arti |
| `lin2022rlw` | arXiv:2111.10603 | arXiv API; OpenAlex API | Reasonable Effectiveness of Random Weighting: A Litmus Test for Multi-Task Learning \| arXiv preprint \| 2021 \| type posted-content |
| `liu2016strnn` | DOI 10.1609/aaai.v30i1.9971 | Crossref REST; OpenAlex API | Predicting the Next Location: A Recurrent Model with Spatial and Temporal Contexts \| Proceedings of the AAAI Conference on Artificial Intelligence \| 2016 \| type journa |
| `liu2019dwa` | DOI 10.1109/CVPR.2019.00197 | Crossref REST; OpenAlex API | End-To-End Multi-Task Learning With Attention \| 2019 IEEE/CVF Conference on Computer Vision and Pattern Recognition (CVPR) \| 2019 \| type proceedings-article |
| `liu2021cagrad` | arXiv:2110.14048 | arXiv API; OpenAlex API | Conflict-Averse Gradient Descent for Multi-task Learning \| arXiv preprint \| 2021 \| type posted-content |
| `liu2023famo` | no identifier in the bib entry | arXiv API; OpenAlex API | FAMO: Fast Adaptive Multitask Optimization \| arXiv preprint \| 2023 \| type posted-content |
| `luca2021mobilitysurvey` | DOI 10.1145/3485125 | Crossref REST; OpenAlex API | A Survey on Deep Learning for Human Mobility \| ACM Computing Surveys \| 2021 \| type journal-article |
| `luo2021stan` | DOI 10.1145/3442381.3449998 | Crossref REST; OpenAlex API | STAN: Spatio-Temporal Attention Network for Next Location Recommendation \| Proceedings of the Web Conference 2021 \| 2021 \| type proceedings-article |
| `ma2018mmoe` | DOI 10.1145/3219819.3220007 | Crossref REST; OpenAlex API | Modeling Task Relationships in Multi-task Learning with Multi-gate Mixture-of-Experts \| Proceedings of the 24th ACM SIGKDD International Conference on Knowledge Discover |
| `mai2020multiscalerepresentationlearningspatial` | arXiv:2003.00824 | arXiv API; OpenAlex API | Multi-Scale Representation Learning for Spatial Feature Distributions using Grid Cells \| ICLR 2020, Apr. 26 - 30, 2020, Addis Ababa, ETHIOPIA \| 2020 \| type posted-cont |
| `mai2023sphere2vecgeneralpurposelocationrepresentation` | arXiv:2306.17624 | arXiv API; OpenAlex API | Sphere2Vec: A General-Purpose Location Representation Learning over a Spherical Surface for Large-Scale Geospatial Predictions \| ISPRS Journal of Photogrammetry and Remo |
| `maninis2019attentive` | DOI 10.1109/CVPR.2019.00195 | Crossref REST; OpenAlex API | Attentive Single-Tasking of Multiple Tasks \| 2019 IEEE/CVF Conference on Computer Vision and Pattern Recognition (CVPR) \| 2019 \| type proceedings-article |
| `mikolov2013word2vec` | arXiv:1301.3781 | arXiv API; OpenAlex API | Efficient Estimation of Word Representations in Vector Space \| arXiv preprint \| 2013 \| type posted-content |
| `misra2016cross` | DOI 10.1109/CVPR.2016.433 | Crossref REST; OpenAlex API | Cross-Stitch Networks for Multi-task Learning \| 2016 IEEE Conference on Computer Vision and Pattern Recognition (CVPR) \| 2016 \| type proceedings-article |
| `nash` | no identifier in the bib entry | arXiv API; OpenAlex API | Multi-Task Learning as a Bargaining Game \| arXiv preprint \| 2022 \| type posted-content |
| `pedregosa2011sklearn` | no identifier in the bib entry | arXiv API; OpenAlex API; PDF in repo: Pedregosa2011_ScikitLearn.pdf | Scikit-learn: Machine Learning in Python \| Journal of Machine Learning Research (2011) \| 2012 \| type posted-content |
| `perez2018film` | DOI 10.1609/aaai.v32i1.11671 | Crossref REST; OpenAlex API | FiLM: Visual Reasoning with a General Conditioning Layer \| Proceedings of the AAAI Conference on Artificial Intelligence \| 2018 \| type journal-article |
| `perozzi2014deepwalk` | DOI 10.1145/2623330.2623732 | Crossref REST; OpenAlex API | DeepWalk \| Proceedings of the 20th ACM SIGKDD international conference on Knowledge discovery and data mining \| 2014 \| type proceedings-article |
| `ruder2017mtloverview` | arXiv:1706.05098 | arXiv API; OpenAlex API | An Overview of Multi-Task Learning in Deep Neural Networks \| arXiv preprint \| 2017 \| type posted-content |
| `russwurm2024geographiclocationencodingspherical` | arXiv:2310.06743 | arXiv API; OpenAlex API | Geographic Location Encoding with Spherical Harmonics and Sinusoidal Representation Networks \| Published as a conference paper at ICLR 2024 \| 2023 \| type posted-conten |
| `sener2018mgda` | arXiv:1810.04650 | arXiv API; OpenAlex API | Multi-Task Learning as Multi-Objective Optimization \| arXiv preprint \| 2018 \| type posted-content |
| `senushkin2023aligned` | no identifier in the bib entry | Crossref REST; OpenAlex API | Independent Component Alignment for Multi-Task Learning \| 2023 IEEE/CVF Conference on Computer Vision and Pattern Recognition (CVPR) \| 2023 \| type proceedings-article |
| `silva2019urbancomputing` | DOI 10.1145/3301284 | Crossref REST; OpenAlex API | Urban Computing Leveraging Location-Based Social Network Data \| ACM Computing Surveys \| 2019 \| type journal-article |
| `silva2025mtlnet` | DOI 10.21528/CBIC2025-1191324 | Crossref REST; OpenAlex API | An Investigation into Multi-Task Learning for Point-of-Interest Category Classification and Next-POI Prediction \| Anais do XVII Congresso Brasileiro de Inteligência Comp |
| `sitzmann2020implicit` | arXiv:2006.09661 | arXiv API; OpenAlex API | Implicit Neural Representations with Periodic Activation Functions \| arXiv preprint \| 2020 \| type posted-content |
| `sokolova2009measures` | DOI 10.1016/j.ipm.2009.03.002 | Crossref REST; OpenAlex API; PDF in repo: sokolova2009.pdf | A systematic analysis of performance measures for classification tasks \| Information Processing &amp; Management \| 2009 \| type journal-article |
| `song2010limits` | DOI 10.1126/science.1177170 | Crossref REST; OpenAlex API; PDF in repo: 201002-19_Science-Predictability.pdf | Limits of Predictability in Human Mobility \| Science \| 2010 \| type journal-article |
| `standley2020tasks` | arXiv:1905.07553 | arXiv API; OpenAlex API | Which Tasks Should Be Learned Together in Multi-task Learning? \| arXiv preprint \| 2019 \| type posted-content |
| `tang2020ple` | DOI 10.1145/3383313.3412236 | Crossref REST; OpenAlex API | Progressive Layered Extraction (PLE): A Novel Multi-Task Learning (MTL) Model for Personalized Recommendations \| Fourteenth ACM Conference on Recommender Systems \| 2020 |
| `vandenhende2022mtl` | DOI 10.1109/TPAMI.2021.3054719 | Crossref REST; OpenAlex API | Multi-Task Learning for Dense Prediction Tasks: A Survey \| IEEE Transactions on Pattern Analysis and Machine Intelligence \| 2021 \| type journal-article |
| `velickovic2019deep` | no identifier in the bib entry | OpenAlex API | Deep Graph Infomax \| Apollo (University of Cambridge) \| 2018 \| type conference-paper |
| `velivckovic2017graph` | arXiv:1710.10903 | arXiv API | Graph Attention Networks \| arXiv preprint \| 2017 \| type posted-content |
| `wilcoxon1945` | DOI 10.2307/3001968 | Crossref REST; OpenAlex API; PDF in repo: wilcoxon1945.pdf | Individual Comparisons by Ranking Methods \| Biometrics Bulletin \| 1945 \| type journal-article |
| `wongso2025massivesteps` | no identifier in the bib entry | arXiv API; OpenAlex API | Massive-STEPS: Massive Semantic Trajectories for Understanding POI Check-ins -- Dataset and Benchmarks \| arXiv preprint \| 2025 \| type posted-content |
| `xin2022domtl` | no identifier in the bib entry | arXiv API; OpenAlex API | Do Current Multi-Task Optimization Methods in Deep Learning Even Help? \| arXiv preprint \| 2022 \| type posted-content |
| `yang2015tsmc` | DOI 10.1109/TSMC.2014.2327053 | Crossref REST; OpenAlex API | Modeling User Activity Preference by Leveraging User Spatial Temporal Characteristics in LBSNs \| IEEE Transactions on Systems, Man, and Cybernetics: Systems \| 2015 \| t |
| `yang2020flashback` | DOI 10.24963/ijcai.2020/302 | Crossref REST; OpenAlex API | Location Prediction over Sparse User Mobility Traces Using RNNs: Flashback in Hidden States! \| Proceedings of the Twenty-Ninth International Joint Conference on Artifici |
| `yang2022getnext` | DOI 10.1145/3477495.3531983 | Crossref REST; OpenAlex API | GETNext \| Proceedings of the 45th International ACM SIGIR Conference on Research and Development in Information Retrieval \| 2022 \| type proceedings-article |
| `yu2020catdm` | DOI 10.1145/3366423.3380202 | Crossref REST; OpenAlex API | A Category-Aware Deep Model for Successive POI Recommendation on Sparse Check-in Data \| Proceedings of The Web Conference 2020 \| 2020 \| type proceedings-article |
| `yu2020pcgrad` | no identifier in the bib entry | arXiv API; OpenAlex API | Gradient Surgery for Multi-Task Learning \| arXiv preprint \| 2020 \| type posted-content |
| `yu2024survey` | arXiv:2404.18961 | arXiv API; OpenAlex API | Unleashing the Power of Multi-Task Learning: A Comprehensive Survey Spanning Traditional, Deep, and Pretrained Foundation Model Eras \| arXiv preprint \| 2024 \| type pos |
| `zhu2022drrgnn` | DOI 10.1145/3529091 | Crossref REST; OpenAlex API | Predicting a Person’s Next Activity Region with a Dynamic Region-Relation-Aware Graph Neural Network \| ACM Transactions on Knowledge Discovery from Data \| 2022 \| type  |

## 5 · Two sites in this chapter that a naive check flags and that are NOT defects

Recorded so a later pass does not re-open them.

**`2_fundamentals.tex:465`, `pedregosa2011sklearn`.** The chapter states the grouped, stratified
splitting protocol in prose and cites the library. `StratifiedGroupKFold` is a scikit-learn v1.0
(2021) feature and the cited paper is from 2011, which is why an existence-only check flags it. The
author has ruled on this twice: it is a citation-style preference, not a support failure, and the
ruling is recorded in the chapter's own ledger comment. Confirmed again here against the paper
(read in `science/articles/Pedregosa2011_ScikitLearn.pdf`): the paper is the software citation and
the sentence attributes no splitter behaviour to it. **Leave.**

**`2_fundamentals.tex:476`, `wilcoxon1945`.** The PDF in the repository carries only a JSTOR cover
page in its text layer; pages 2 to 5 extract zero characters, so the paper body could not be read
from it and no full text is reachable at any allowlisted source. The citation is a method-origin
pointer and the record (Crossref, Biometrics Bulletin 1(6):80-83, 1945) supports it at that level.
Recorded as a limit of the check, not a finding.

**A defect in my own handling of that entry, recorded.** An earlier pass of this audit stored that
JSTOR boilerplate in the entry's `abstract` field, labelled as though it were paper content, and fed
it to the screen. The screen returned UNVERIFIABLE for the site and named the boilerplate explicitly,
so no verdict rested on the bad string, and the verdict above was set at record level. The stored
field is now empty with a note that no abstract or body text is obtainable. I swept the whole snapshot
for the same class afterwards and found no other contaminated abstract. See section 11 item 0 of
`11_citation_claims.md`.

## 6 · What I could not confirm in this chapter

Nothing outstanding. All 70 key instances are SUPPORTED. The two entries above are closed at the
level their sources support, and the limit is stated rather than smoothed over.

---

## `11_claims_3_cbic.md`

# 11_claims_3_cbic.md — citation claim-support audit, Chapter 3, CBIC 2025

**Unit:** `src/chapters/3_cbic.tex`  
**Run:** 2026-07-28, round 6, as the per-chapter pass the author asked for by name (COD-008 decision).  
**Errata regime for this unit:** PUBLISHED: a correction to reproduced prose is applied in the dissertation and listed in Appendix B; the published article record is not edited.

## 1 · Counts (every citation in the unit, not a sample)

- `\cite` commands in the unit: **57**, on **37** source lines, carrying **64** key instances (a multi-key `\cite` counts once per key). Every one was audited.
- Distinct bibliography keys used: **31**.
- Verdicts: **SUPPORTED** 49, **PARTIAL** 8, **NOT-SUPPORTED** 6, **UNVERIFIABLE** 1.

Comments were stripped before counting, so a key that appears only inside a `%` comment is not counted; every counted site renders.

## 2 · Every citation, with its verdict

Verdict scale: SUPPORTED, the citing sentence's attribution is present in or a fair paraphrase of the
source; PARTIAL, part is supported and part is not, or the sentence is stronger than the source;
NOT-SUPPORTED, the attribution is absent from or contradicted by the source; UNVERIFIABLE, the source
of record does not carry enough to decide and the attribution is not implausible.

| # | Site (file:line) | Key | Verdict | Evidence quoted from the source (under 20 words) |
|---|---|---|---|---|
| 1 | `3_cbic.tex:48` | `Zhang2020` | SUPPORTED | "novel interactive multi-task learning (iMTL) framework to better exploit the interplay between activity and location preference" |
| 2 | `3_cbic.tex:48` | `caruana1997multitask` | SUPPORTED | "improves generalization by using the domain information contained in the training signals of related tasks as an inductive bias" |
| 3 | `3_cbic.tex:48` | `kokkinos2016ubernet` | SUPPORTED | "jointly handles low-, mid-, and high-level vision tasks in a unified architecture that is trained end-to-end" |
| 4 | `3_cbic.tex:48` | `wei2022finetuned` | SUPPORTED | "instruction tuning -- finetuning language models on a collection of tasks described via instructions -- substantially improves zero-shot performance" |
| 5 | `3_cbic.tex:62` | `chen2020modeling` | SUPPORTED | "propose a holistic approach named Human Mobility Representation Model (HMRM) to simultaneously produce the vector representations" |
| 6 | `3_cbic.tex:62` | `cho2011gowalla` | SUPPORTED | "data from two online location-based social networks" |
| 7 | `3_cbic.tex:62` | `jure2014snap` | SUPPORTED | "A collection of more than 50 large network datasets" |
| 8 | `3_cbic.tex:62` | `zeng2019next` | SUPPORTED | "A Next Location Predicting Approach Based on a Recurrent Neural Network and Self-Attention" |
| 9 | `3_cbic.tex:86` | `Xu2023` | SUPPORTED | "devise a Tree-guided Multi-task Embedding model (TME for short) to learn effective representations of venues and categories" |
| 10 | `3_cbic.tex:88` | `Lim2022` | SUPPORTED | "learning different User-Region matrices of lower sparsities in a multi-task setting" |
| 11 | `3_cbic.tex:95` | `caruana1997multitask` | SUPPORTED | "improves generalization by using the domain information contained in the training signals of related tasks" |
| 12 | `3_cbic.tex:97` | `yu2024survey` | SUPPORTED | "categorizes MTL techniques into five key areas: regularization, relationship learning, feature propagation, optimization, and pre-training" |
| 13 | `3_cbic.tex:97` | `zhang2021survey` | NOT-SUPPORTED | "five categories, including feature learning approach, low-rank approach, task clustering approach, task relation learning approach and decomposition a" |
| 14 | `3_cbic.tex:102` | `caruana1997multitask` | PARTIAL | "improves generalization by using the domain information contained in the training signals of related tasks as an inductive bias" |
| 15 | `3_cbic.tex:104` | `misra2016cross` | SUPPORTED | "we propose a new sharing unit: "cross-stitch" unit. These units combine the activations from multiple networks" |
| 16 | `3_cbic.tex:104` | `ruder2017sluice` | SUPPORTED | "learns a latent multi-task architecture that jointly addresses (a)--(c)" |
| 17 | `3_cbic.tex:106` | `ma2018mmoe` | SUPPORTED | "successfully used in many real-world large-scale applications such as recommendation systems" |
| 18 | `3_cbic.tex:108` | `chen2018gradnorm` | SUPPORTED | "gradient normalization (GradNorm) algorithm that automatically balances training in deep multitask models by dynamically tuning gradient magnitudes" |
| 19 | `3_cbic.tex:108` | `liu2019dwa` | SUPPORTED | "less sensitive to various weighting schemes in the multi-task loss function" |
| 20 | `3_cbic.tex:108` | `sener2018mgda` | SUPPORTED | "we explicitly cast multi-task learning as multi-objective optimization, with the overall objective of finding a Pareto optimal solution" |
| 21 | `3_cbic.tex:108` | `yu2020pcgrad` | SUPPORTED | "projects a task's gradient onto the normal plane of the gradient of any other task that has a conflicting gradient" |
| 22 | `3_cbic.tex:112` | `ruder2017sluice` | SUPPORTED | "MTL involves searching an enormous space of possible parameter sharing architectures to find (a) the layers or subspaces that benefit from sharing" |
| 23 | `3_cbic.tex:112` | `zhang2021survey` | SUPPORTED | "leverage useful information contained in multiple related tasks to help improve the generalization performance of all the tasks" |
| 24 | `3_cbic.tex:113` | `sener2018mgda` | SUPPORTED | "different tasks may conflict, necessitating a trade-off" |
| 25 | `3_cbic.tex:113` | `yu2020pcgrad` | SUPPORTED | "detrimental gradient interference, and develop a simple yet general approach for avoiding such interference between task gradients" |
| 26 | `3_cbic.tex:114` | `nash` | NOT-SUPPORTED | "since the gradients of these different tasks may conflict, training a joint model for MTL often yields lower performance" |
| 27 | `3_cbic.tex:114` | `standley2020tasks` | NOT-SUPPORTED | "which tasks should and should not be learned together in one network when employing multi-task learning" |
| 28 | `3_cbic.tex:115` | `yu2024survey` | PARTIAL | "MTL's key advantages encompass streamlined model architecture, performance enhancement, and cross-domain generalizability" |
| 29 | `3_cbic.tex:115` | `zhang2021survey` | PARTIAL | "When the number of tasks is large or the data dimensionality is high, we review online, parallel and distributed MTL models as well as dimensionality " |
| 30 | `3_cbic.tex:118` | `standley2020tasks` | SUPPORTED | "propose a framework for assigning tasks to a few neural networks such that cooperating tasks are computed by the same neural network" |
| 31 | `3_cbic.tex:118` | `yu2024survey` | SUPPORTED | "categorizes MTL techniques into five key areas: regularization, relationship learning, feature propagation, optimization, and pre-training" |
| 32 | `3_cbic.tex:123` | `Liao2018` | PARTIAL | "a novel Context Aware Recurrent Unit is designed to integrate the sequential dependency and temporal regularity" |
| 33 | `3_cbic.tex:123` | `Zhang2020` | NOT-SUPPORTED | "temporal-aware activity encoder equipped with fuzzy characterization over uncertain check-ins" |
| 34 | `3_cbic.tex:125` | `Halder2021` | SUPPORTED | "Transformer-Based Multi-task Learning for Queuing Time Aware Next POI Recommendation" |
| 35 | `3_cbic.tex:125` | `Xia2020` | PARTIAL | "exploits a structure of generative adversarial networks (GAN) simultaneously considering temporal check-ins and geographical locations" |
| 36 | `3_cbic.tex:127` | `Xu2023` | PARTIAL | "we devise a Tree-guided Multi-task Embedding model (TME for short) to learn effective representations of venues and categories" |
| 37 | `3_cbic.tex:143` | `du2019beyond` | SUPPORTED | "spatial complementarity refers to the effect that the role of a spatial entity can be complemented and augmented by other different yet compatible spa" |
| 38 | `3_cbic.tex:145` | `huang2022estimating` | UNVERIFIABLE | "(no single decisive passage; see the ledger)" |
| 39 | `3_cbic.tex:151` | `velickovic2019deep` | SUPPORTED | "maximizing mutual information between patch representations and corresponding high-level summaries of graphs" |
| 40 | `3_cbic.tex:151` | `velivckovic2017graph` | SUPPORTED | "novel neural network architectures that operate on graph-structured data, leveraging masked self-attentional layers" |
| 41 | `3_cbic.tex:191` | `perez2018film` | SUPPORTED | "FiLM layers influence neural network computation via a simple, feature-wise affine transformation based on conditioning information" |
| 42 | `3_cbic.tex:191` | `standley2020tasks` | SUPPORTED | "which tasks should and should not be learned together in one network when employing multi-task learning" |
| 43 | `3_cbic.tex:197` | `perez2018film` | SUPPORTED | "FiLM layers influence neural network computation via a simple, feature-wise affine transformation based on conditioning information" |
| 44 | `3_cbic.tex:204` | `baxter2000model` | SUPPORTED | "the learner can search for a hypothesis space that contains good solutions to many of the problems" |
| 45 | `3_cbic.tex:213` | `caruana1997multitask` | SUPPORTED | "improves generalization by using the domain information contained in the training signals of related tasks as an inductive bias" |
| 46 | `3_cbic.tex:213` | `ruder2017sluice` | NOT-SUPPORTED | "we present an approach that learns a latent multi-task architecture" |
| 47 | `3_cbic.tex:214` | `standley2020tasks` | NOT-SUPPORTED | "this often leads to inferior overall performance as task objectives can compete" |
| 48 | `3_cbic.tex:228` | `nash` | SUPPORTED | "viewing the gradients combination step as a bargaining game, where tasks negotiate to reach an agreement" |
| 49 | `3_cbic.tex:228` | `nash` | SUPPORTED | "proposed viewing the gradients combination step as a bargaining game... Nash Bargaining Solution" |
| 50 | `3_cbic.tex:231` | `nash` | SUPPORTED | "viewing the gradients combination step as a bargaining game, where tasks negotiate to reach an agreement on a joint direction" |
| 51 | `3_cbic.tex:231` | `nash` | SUPPORTED | "tasks negotiate to reach an agreement on a joint direction of parameter update" |
| 52 | `3_cbic.tex:238` | `nash` | SUPPORTED | "we propose viewing the gradients combination step as a bargaining game" |
| 53 | `3_cbic.tex:238` | `nash` | SUPPORTED | "Nash Bargaining Solution, which we propose to use as a principled approach to multi-task learning" |
| 54 | `3_cbic.tex:238` | `nash` | SUPPORTED | "derive theoretical guarantees for its convergence" |
| 55 | `3_cbic.tex:244` | `nash` | PARTIAL | "Empirically, we show that Nash-MTL achieves state-of-the-art results on multiple MTL benchmarks" |
| 56 | `3_cbic.tex:280` | `yu2020pcgrad` | SUPPORTED | "gradient surgery that projects a task's gradient onto the normal plane of the gradient of any other task" |
| 57 | `3_cbic.tex:288` | `cho2011gowalla` | SUPPORTED | "data from two online location-based social networks, we aim to understand what basic laws govern human motion" |
| 58 | `3_cbic.tex:306` | `chen2020modeling` | PARTIAL | "We apply HMRM to both unsupervised and supervised tasks including two activity evaluation tasks and two embedding evaluation tasks" |
| 59 | `3_cbic.tex:308` | `vaswani2017attention` | SUPPORTED | "new simple network architecture, the Transformer, based solely on attention mechanisms" |
| 60 | `3_cbic.tex:308` | `zeng2019next` | SUPPORTED | "A Next Location Predicting Approach Based on a Recurrent Neural Network and Self-Attention" |
| 61 | `3_cbic.tex:311` | `chen2020modeling` | SUPPORTED | "We apply HMRM to both unsupervised and supervised tasks including two activity evaluation tasks and two embedding evaluation tasks" |
| 62 | `3_cbic.tex:317` | `zeng2019next` | SUPPORTED | "A Next Location Predicting Approach Based on a Recurrent Neural Network and Self-Attention" |
| 63 | `3_cbic.tex:322` | `chen2020modeling` | SUPPORTED | "we propose a holistic approach named Human Mobility Representation Model (HMRM)" |
| 64 | `3_cbic.tex:322` | `zeng2019next` | SUPPORTED | "A Next Location Predicting Approach Based on a Recurrent Neural Network and Self-Attention" |
## 3 · Failures and partials in this unit, in detail

### `3_cbic.tex:97` — `zhang2021survey` — **NOT-SUPPORTED**

**Citing sentence.** Recent surveys \cite{yu2024survey,zhang2021survey} organize contemporary MTL research along five methodological dimensions: (i) \textit{parameter sharing} (hard vs.\ soft); (ii) \textit{relationship learning} (discovering task affinity or hierarchy); (iii) \textit{feature routing} (e.g., cross-stitch, sluice networks, attention gating); (iv) \textit{optimization} (conflict-aware gradient techniques); and (v) \textit{pre-training and instruction tuning}.

**Reference resolved.** DOI 10.1109/TKDE.2021.3070203. Source of record: Crossref REST; OpenAlex API. Record reads: A Survey on Multi-Task Learning | IEEE Transactions on Knowledge and Data Engineering | 2022 | type journal-article.

**Located passage.** "five categories, including feature learning approach, low-rank approach, task clustering approach, task relation learning approach and decomposition approach"

**Why.** The sentence says "Recent surveys [yu2024survey,zhang2021survey] organize contemporary MTL research along five methodological dimensions" and then lists parameter sharing / relationship learning / feature routing / optimization / pre-training and instruction tuning. That list is yu2024survey's five areas (regularization, relationship learning, feature propagation, optimization, pre-training), loosely renamed. zhang2021survey also gives five, but a DIFFERENT five, none of which is parameter sharing or pre-training. The plural "surveys" makes a taxonomy claim of both.

**Recommended disposition.** Published CBIC prose. Narrow the attribution: keep the list on yu2024survey and cite zhang2021survey for the survey framing only, or drop it from this sentence (it is cited three more times in the chapter). Appendix B row if the prose changes.

### `3_cbic.tex:114` — `nash` — **NOT-SUPPORTED**

**Citing sentence.** \textbf{Data Heterogeneity}: Variations in modality, label granularity, and dataset size complicate sampling strategies and minibatch construction \cite{nash,standley2020tasks}.

**Reference resolved.** no identifier in the bib entry. Source of record: arXiv API; OpenAlex API. Record reads: Multi-Task Learning as a Bargaining Game | arXiv preprint | 2022 | type posted-content.

**Located passage.** "since the gradients of these different tasks may conflict, training a joint model for MTL often yields lower performance"

**Why.** The bullet is "Data Heterogeneity: variations in modality, label granularity, and dataset size complicate sampling strategies and minibatch construction". Nash-MTL is a gradient-aggregation method; it addresses gradient conflict, which is the PRECEDING bullet in the same list, and says nothing about modality, label granularity, dataset size, sampling or minibatch construction.

**Recommended disposition.** Published CBIC prose. The two keys are mis-slotted across adjacent bullets. Either cite a survey that does treat data heterogeneity, or narrow the bullet to what these two works support.

### `3_cbic.tex:114` — `standley2020tasks` — **NOT-SUPPORTED**

**Citing sentence.** \textbf{Data Heterogeneity}: Variations in modality, label granularity, and dataset size complicate sampling strategies and minibatch construction \cite{nash,standley2020tasks}.

**Reference resolved.** arXiv:1905.07553. Source of record: arXiv API; OpenAlex API. Record reads: Which Tasks Should Be Learned Together in Multi-task Learning? | arXiv preprint | 2019 | type posted-content.

**Located passage.** "which tasks should and should not be learned together in one network when employing multi-task learning"

**Why.** Same bullet. The paper studies task cooperation and competition and proposes a task-grouping framework. It does not treat modality, label granularity or dataset-size heterogeneity, nor sampling or minibatch construction.

**Recommended disposition.** As above.

### `3_cbic.tex:123` — `Zhang2020` — **NOT-SUPPORTED**

**Citing sentence.** Similarly, the iMTL framework~\cite{Zhang2020} uses an LSTM architecture to model next-activity prediction, incorporating temporal dynamics in user behavior modeling.

**Reference resolved.** DOI 10.24963/ijcai.2020/491. Source of record: Crossref REST; OpenAlex API. Record reads: An Interactive Multi-Task Learning Framework for Next POI Recommendation with Uncertain Check-ins | Proceedings of the Twenty-Ninth International Joint Conference on Artificial Intelligence | 2020 | type proceedings-article.

**Located passage.** "temporal-aware activity encoder equipped with fuzzy characterization over uncertain check-ins"

**Why.** iMTL is an interactive multi-task framework for next-POI recommendation with uncertain check-ins; its encoders are a temporal-aware activity encoder and a spatial-aware location preference encoder, with a task-specific decoder. The abstract does not name LSTM, and "next-activity prediction" is one of two interacting tasks, not the model's object.

**Recommended disposition.** Published CBIC prose. Restate as its authors do: an interactive multi-task framework whose temporal-aware activity encoder handles uncertain check-ins. Appendix B row.

### `3_cbic.tex:213` — `ruder2017sluice` — **NOT-SUPPORTED**

**Citing sentence.** \textbf{Implicit Regularization:} By constraining the hypothesis space, hard sharing acts as a regularizer, often leading to more generalizable models, especially when tasks are related \cite{ruder2017sluice}.

**Reference resolved.** arXiv:1705.08142. Source of record: arXiv API. Record reads: Latent Multi-task Architecture Learning | arXiv preprint | 2017 | type posted-content.

**Located passage.** "we present an approach that learns a latent multi-task architecture"

**Why.** The bullet claims hard sharing acts as a regularizer. The cited work (arXiv:1705.08142, whose arXiv title of record is "Latent Multi-task Architecture Learning") proposes LEARNING what and how much to share, that is a soft-sharing alternative to hard sharing, and reports it outperforming standard MTL. It is evidence against the bullet it is attached to, not for it.

**Recommended disposition.** Published CBIC prose. baxter2000model, already in the bibliography and cited for exactly this at 4_courb.tex:116, does support a shared-hypothesis-space regularization claim. Swap the key. Appendix B row.

### `3_cbic.tex:214` — `standley2020tasks` — **NOT-SUPPORTED**

**Citing sentence.** \textbf{Empirical Performance:} In practice, hard parameter sharing frequently matches or exceeds the performance of more complex architectures on many benchmarks, while offering faster training and inference \cite{standley2020tasks}.

**Reference resolved.** arXiv:1905.07553. Source of record: arXiv API; OpenAlex API. Record reads: Which Tasks Should Be Learned Together in Multi-task Learning? | arXiv preprint | 2019 | type posted-content.

**Located passage.** "this often leads to inferior overall performance as task objectives can compete"

**Why.** ITEM 3. See the dedicated section of this report.

**Recommended disposition.** ITEM 3 draft: narrowed sentence + Appendix B row, handed over, not applied.

### `3_cbic.tex:102` — `caruana1997multitask` — **PARTIAL**

**Citing sentence.** This remains the simplest and most popular baseline, providing effective regularization \cite{caruana1997multitask}.

**Reference resolved.** DOI 10.1023/A:1007379606734. Source of record: Crossref REST; OpenAlex API; PDF in repo: 10.1023_A_1007379606734.pdf. Record reads: Multitask Learning | Machine Learning | 1997 | type journal-article.

**Located passage.** "improves generalization by using the domain information contained in the training signals of related tasks as an inductive bias"

**Why.** The regularization half is squarely supported. "the simplest and most popular baseline" is a bibliometric claim about the field in 2025 that a 1997 paper cannot carry.

**Recommended disposition.** Published CBIC prose, low exposure. Leave and record, or attribute the popularity clause to a survey (vandenhende2022mtl / zhang2021survey are both in the bibliography).

### `3_cbic.tex:115` — `zhang2021survey` — **PARTIAL**

**Citing sentence.** \textbf{Scalability}: Routing complexity, memory footprint, and evaluation costs often grow super-linearly as the number of tasks increases \cite{zhang2021survey,yu2024survey}.

**Reference resolved.** DOI 10.1109/TKDE.2021.3070203. Source of record: Crossref REST; OpenAlex API. Record reads: A Survey on Multi-Task Learning | IEEE Transactions on Knowledge and Data Engineering | 2022 | type journal-article.

**Located passage.** "When the number of tasks is large or the data dimensionality is high, we review online, parallel and distributed MTL models as well as dimensionality reduction and featur"

**Why.** The survey does treat cost growth with the number of tasks, and names computational and storage concerns. The specific word "super-linearly" is a quantitative shape claim that the abstract does not state, and neither does yu2024survey's.

### `3_cbic.tex:115` — `yu2024survey` — **PARTIAL**

**Citing sentence.** \textbf{Scalability}: Routing complexity, memory footprint, and evaluation costs often grow super-linearly as the number of tasks increases \cite{zhang2021survey,yu2024survey}.

**Reference resolved.** arXiv:2404.18961. Source of record: arXiv API; OpenAlex API. Record reads: Unleashing the Power of Multi-Task Learning: A Comprehensive Survey Spanning Traditional, Deep, and Pretrained Foundation Model Eras | arXiv preprint | 2024 | type posted-content.

**Located passage.** "MTL's key advantages encompass streamlined model architecture, performance enhancement, and cross-domain generalizability"

**Why.** Same bullet. The survey addresses architectures and efficiency but the abstract makes no super-linear growth claim. Published CBIC prose, low exposure: the bullet is a challenge list, not a result.

### `3_cbic.tex:123` — `Liao2018` — **PARTIAL**

**Citing sentence.** Early MTL-based approaches such as MCARNN~\cite{Liao2018} employ recurrent neural networks with temporal attention mechanisms to jointly predict user activities and future visited locations.

**Reference resolved.** DOI 10.24963/ijcai.2018/477. Source of record: Crossref REST; OpenAlex API. Record reads: Predicting Activity and Location with Multi-task Context Aware Recurrent Neural Network | Proceedings of the Twenty-Seventh International Joint Conference on Artificial Intelligence | 2018 | type proceedings-article.

**Located passage.** "a novel Context Aware Recurrent Unit is designed to integrate the sequential dependency and temporal regularity"

**Why.** MCARNN does jointly predict activity and location with a recurrent model, which is the load-bearing part. "temporal attention mechanisms" is not what the paper describes: its mechanism is a Context Aware Recurrent Unit over spatial-activity topics.

**Recommended disposition.** Published CBIC prose. Substitute "context-aware recurrent units" for "temporal attention mechanisms" (describe the system as its authors do, AGENT_GUARDRAILS R2), with an Appendix B row.

### `3_cbic.tex:125` — `Xia2020` — **PARTIAL**

**Citing sentence.** MTPR~\cite{Xia2020} combines LSTMs and adversarial learning to address uncertainty in check-ins and improve multi-task POI recommendation both location and temporal context with a generative component.

**Reference resolved.** DOI 10.3390/app10196664. Source of record: Crossref REST; OpenAlex API. Record reads: MTPR: A Multi-Task Learning Based POI Recommendation Considering Temporal Check-Ins and Geographical Locations | Applied Sciences | 2020 | type journal-article.

**Located passage.** "exploits a structure of generative adversarial networks (GAN) simultaneously considering temporal check-ins and geographical locations"

**Why.** The multi-task, adversarial and temporal-geographic halves are supported verbatim. "combines LSTMs" is not in the abstract. The citing sentence is also ungrammatical in the published text ("improve multi-task POI recommendation both location and temporal context").

**Recommended disposition.** Published CBIC prose. Drop "LSTMs and" or verify against the paper body; the sentence needs a grammatical repair regardless, which is a wording row.

### `3_cbic.tex:127` — `Xu2023` — **PARTIAL**

**Citing sentence.** Some Models such as TME~\cite{Xu2023} address category annotation using graph-based encoders, but treat prediction and classification separately.

**Reference resolved.** DOI 10.1145/3582553. Source of record: Crossref REST; OpenAlex API. Record reads: TME: Tree-guided Multi-task Embedding Learning towards Semantic Venue Annotation | ACM Transactions on Information Systems | 2023 | type journal-article.

**Located passage.** "we devise a Tree-guided Multi-task Embedding model (TME for short) to learn effective representations of venues and categories"

**Why.** The load-bearing half is supported: TME addresses category annotation and does not pair it with next-POI prediction. "using graph-based encoders" is not TME's described mechanism, which is multi-context embedding regularized by a predefined category hierarchy.

**Recommended disposition.** Published CBIC prose. Replace "graph-based encoders" with "a tree-guided multi-task embedding". Appendix B row.

### `3_cbic.tex:145` — `huang2022estimating` — **UNVERIFIABLE**

**Citing sentence.** Besides that, following \cite{huang2022estimating} the weight of an edge $e_{ij}$ is defined as $w_{ij} = \log((1+D^{1.5}/1+d_{ij}^{1.5}))$, where D is the diagonal length of bounding box that encloses the coordinates of POIs, and $d_{ij}$ is the geodesic distance between $p_{i}$ and $p_{j}$.

**Reference resolved.** DOI 10.1080/13658816.2022.2040510. Source of record: Crossref REST; OpenAlex API. Record reads: Estimating urban functional distributions with semantics preserved POI embedding | International Journal of Geographical Information Science | 2022 | type journal-article.

**Why.** The citing sentence reproduces a specific edge-weight formula, w_ij = log((1+D^1.5)/(1+d_ij^1.5)), and says it follows the cited work. That is a formula-level attribution; the abstract of record cannot confirm or refute it, and I did not obtain the paper body. Open as [VERIFY] with a named check: locate the formula in the cited paper, or restate it as this work's own construction.

### `3_cbic.tex:244` — `nash` — **PARTIAL**

**Citing sentence.** For efficiency, task weights can be updated less frequently, significantly reducing runtime while maintaining performance~\cite{nash}.

**Reference resolved.** no identifier in the bib entry. Source of record: arXiv API; OpenAlex API. Record reads: Multi-Task Learning as a Bargaining Game | arXiv preprint | 2022 | type posted-content.

**Located passage.** "Empirically, we show that Nash-MTL achieves state-of-the-art results on multiple MTL benchmarks"

**Why.** The abstract does not carry the less-frequent-update claim. I could not locate it from the abstract alone, and I did not read the paper body for this clause, so I cannot certify it either way. The chapter has already corrected two other cost claims in this same subsection against this same paper.

**Recommended disposition.** Open as [VERIFY]. The clause needs a page or section from arXiv:2202.01017 before it stands; the neighbouring corrections show the paper has been read for cost claims before.

### `3_cbic.tex:306` — `chen2020modeling` — **PARTIAL**

**Citing sentence.** The Human Mobility Representation Model (HMRM), introduced by Chen et al. (2020) \cite{chen2020modeling}, is designed for POI category classification.

**Reference resolved.** DOI 10.1109/TKDE.2020.3001025. Source of record: Crossref REST; OpenAlex API. Record reads: Modeling Spatial Trajectories With Attribute Representation Learning | IEEE Transactions on Knowledge and Data Engineering | 2022 | type journal-article.

**Located passage.** "We apply HMRM to both unsupervised and supervised tasks including two activity evaluation tasks and two embedding evaluation tasks"

**Why.** HMRM is a general trajectory-attribute representation model, not a model "designed for POI category classification". The rest of the passage (PMI, matrix factorization, SVM on the embeddings) describes how THIS chapter used it as a baseline, which is a legitimate use.

**Recommended disposition.** Published CBIC prose. Narrow to "used here for POI category classification" or "a representation model that this chapter applies to POI category classification".

## 4 · Source ledger for this unit

Every distinct key cited in this unit, the identifier it resolved by, and where I opened it this session.

| Key | Identifier | Opened at | Record as returned |
|---|---|---|---|
| `Halder2021` | DOI 10.1007/978-3-030-75765-6_41 | Crossref REST; OpenAlex API; Semantic Scholar API | Transformer-Based Multi-task Learning for Queuing Time Aware Next POI Recommendation \| Lecture Notes in Computer Science \| 2021 \| type book-chapter |
| `Liao2018` | DOI 10.24963/ijcai.2018/477 | Crossref REST; OpenAlex API | Predicting Activity and Location with Multi-task Context Aware Recurrent Neural Network \| Proceedings of the Twenty-Seventh International Joint Conference on Artificial  |
| `Lim2022` | DOI 10.1145/3477495.3531989 | Crossref REST; OpenAlex API | Hierarchical Multi-Task Graph Recurrent Network for Next POI Recommendation \| Proceedings of the 45th International ACM SIGIR Conference on Research and Development in I |
| `Xia2020` | DOI 10.3390/app10196664 | Crossref REST; OpenAlex API | MTPR: A Multi-Task Learning Based POI Recommendation Considering Temporal Check-Ins and Geographical Locations \| Applied Sciences \| 2020 \| type journal-article |
| `Xu2023` | DOI 10.1145/3582553 | Crossref REST; OpenAlex API | TME: Tree-guided Multi-task Embedding Learning towards Semantic Venue Annotation \| ACM Transactions on Information Systems \| 2023 \| type journal-article |
| `Zhang2020` | DOI 10.24963/ijcai.2020/491 | Crossref REST; OpenAlex API | An Interactive Multi-Task Learning Framework for Next POI Recommendation with Uncertain Check-ins \| Proceedings of the Twenty-Ninth International Joint Conference on Art |
| `baxter2000model` | DOI 10.1613/jair.731 | Crossref REST; OpenAlex API | A Model of Inductive Bias Learning \| Journal of Artificial Intelligence Research \| 2000 \| type journal-article |
| `caruana1997multitask` | DOI 10.1023/A:1007379606734 | Crossref REST; OpenAlex API; PDF in repo: 10.1023_A_1007379606734.pdf | Multitask Learning \| Machine Learning \| 1997 \| type journal-article |
| `chen2018gradnorm` | no identifier in the bib entry | arXiv API; OpenAlex API | GradNorm: Gradient Normalization for Adaptive Loss Balancing in Deep Multitask Networks \| Proceedings of the 35th International Conference on Machine Learning (2018), 79 |
| `chen2020modeling` | DOI 10.1109/TKDE.2020.3001025 | Crossref REST; OpenAlex API | Modeling Spatial Trajectories With Attribute Representation Learning \| IEEE Transactions on Knowledge and Data Engineering \| 2022 \| type journal-article |
| `cho2011gowalla` | DOI 10.1145/2020408.2020579 | Crossref REST; OpenAlex API | Friendship and mobility \| Proceedings of the 17th ACM SIGKDD international conference on Knowledge discovery and data mining \| 2011 \| type proceedings-article |
| `du2019beyond` | DOI 10.1109/ICDM.2019.00026 | Crossref REST; OpenAlex API | Beyond Geo-First Law: Learning Spatial Representations via Integrated Autocorrelations and Complementarity \| 2019 IEEE International Conference on Data Mining (ICDM) \|  |
| `huang2022estimating` | DOI 10.1080/13658816.2022.2040510 | Crossref REST; OpenAlex API | Estimating urban functional distributions with semantics preserved POI embedding \| International Journal of Geographical Information Science \| 2022 \| type journal-arti |
| `jure2014snap` | no identifier in the bib entry | OpenAlex API | {SNAP Datasets}: {Stanford} Large Network Dataset Collection \| (no venue in record) \| 2014 \| type article |
| `kokkinos2016ubernet` | arXiv:1609.02132 | arXiv API; OpenAlex API | UberNet: Training a `Universal' Convolutional Neural Network for Low-, Mid-, and High-Level Vision using Diverse Datasets and Limited Memory \| arXiv preprint \| 2016 \|  |
| `liu2019dwa` | DOI 10.1109/CVPR.2019.00197 | Crossref REST; OpenAlex API | End-To-End Multi-Task Learning With Attention \| 2019 IEEE/CVF Conference on Computer Vision and Pattern Recognition (CVPR) \| 2019 \| type proceedings-article |
| `ma2018mmoe` | DOI 10.1145/3219819.3220007 | Crossref REST; OpenAlex API | Modeling Task Relationships in Multi-task Learning with Multi-gate Mixture-of-Experts \| Proceedings of the 24th ACM SIGKDD International Conference on Knowledge Discover |
| `misra2016cross` | DOI 10.1109/CVPR.2016.433 | Crossref REST; OpenAlex API | Cross-Stitch Networks for Multi-task Learning \| 2016 IEEE Conference on Computer Vision and Pattern Recognition (CVPR) \| 2016 \| type proceedings-article |
| `nash` | no identifier in the bib entry | arXiv API; OpenAlex API | Multi-Task Learning as a Bargaining Game \| arXiv preprint \| 2022 \| type posted-content |
| `perez2018film` | DOI 10.1609/aaai.v32i1.11671 | Crossref REST; OpenAlex API | FiLM: Visual Reasoning with a General Conditioning Layer \| Proceedings of the AAAI Conference on Artificial Intelligence \| 2018 \| type journal-article |
| `ruder2017sluice` | arXiv:1705.08142 | arXiv API | Latent Multi-task Architecture Learning \| arXiv preprint \| 2017 \| type posted-content |
| `sener2018mgda` | arXiv:1810.04650 | arXiv API; OpenAlex API | Multi-Task Learning as Multi-Objective Optimization \| arXiv preprint \| 2018 \| type posted-content |
| `standley2020tasks` | arXiv:1905.07553 | arXiv API; OpenAlex API | Which Tasks Should Be Learned Together in Multi-task Learning? \| arXiv preprint \| 2019 \| type posted-content |
| `vaswani2017attention` | arXiv:1706.03762 | arXiv API | Attention Is All You Need \| arXiv preprint \| 2017 \| type posted-content |
| `velickovic2019deep` | no identifier in the bib entry | OpenAlex API | Deep Graph Infomax \| Apollo (University of Cambridge) \| 2018 \| type conference-paper |
| `velivckovic2017graph` | arXiv:1710.10903 | arXiv API | Graph Attention Networks \| arXiv preprint \| 2017 \| type posted-content |
| `wei2022finetuned` | URL https://openreview.net/forum?id=gEZrGCozdqR | arXiv API; OpenAlex API | Finetuned Language Models Are Zero-Shot Learners \| arXiv preprint \| 2021 \| type posted-content |
| `yu2020pcgrad` | no identifier in the bib entry | arXiv API; OpenAlex API | Gradient Surgery for Multi-Task Learning \| arXiv preprint \| 2020 \| type posted-content |
| `yu2024survey` | arXiv:2404.18961 | arXiv API; OpenAlex API | Unleashing the Power of Multi-Task Learning: A Comprehensive Survey Spanning Traditional, Deep, and Pretrained Foundation Model Eras \| arXiv preprint \| 2024 \| type pos |
| `zeng2019next` | DOI 10.1007/978-3-030-30146-0_21 | Crossref REST; OpenAlex API; Semantic Scholar API | A Next Location Predicting Approach Based on a Recurrent Neural Network and Self-attention \| Lecture Notes of the Institute for Computer Sciences, Social Informatics and |
| `zhang2021survey` | DOI 10.1109/TKDE.2021.3070203 | Crossref REST; OpenAlex API | A Survey on Multi-Task Learning \| IEEE Transactions on Knowledge and Data Engineering \| 2022 \| type journal-article |

## 5 · Provenance of every failure in this chapter

**All fifteen non-SUPPORTED sites in this chapter are verbatim published CBIC 2025 prose.** I did
not take this on trust. Each citing sentence was matched, as an exact string prefix, against the
article source of record in this repository:

| Site | Found verbatim in |
|---|---|
| `:97` five survey dimensions | `articles/CBIC___MTL/sections/basis.tex` |
| `:102` hard-sharing baseline | `articles/CBIC___MTL/sections/basis.tex` |
| `:108` DWA | `articles/CBIC___MTL/sections/basis.tex` |
| `:114` data heterogeneity | `articles/CBIC___MTL/sections/basis.tex` |
| `:123` MCARNN and iMTL | `articles/CBIC___MTL/sections/basis.tex` |
| `:125` MTPR | `articles/CBIC___MTL/sections/basis.tex` |
| `:127` TME | `articles/CBIC___MTL/sections/basis.tex` |
| `:213` regularization and Caruana | `articles/CBIC___MTL/sections/method.tex` |
| `:214` empirical performance | `articles/CBIC___MTL/sections/method.tex` |
| `:244` Nash update frequency | `articles/CBIC___MTL/sections/method.tex` |
| `:306` HMRM | `articles/CBIC___MTL/sections/results.tex` |

So every disposition in this chapter is an errata-policy decision, not a typo fix: the correction is
applied in the dissertation and listed in Appendix B, and the published record is not edited. That
is also why the load-bearing ranking matters more here than elsewhere: each row costs an Appendix B
line.

## 6 · The Standley site

`3_cbic.tex:214` is treated separately and at length in `11_citation_claims.md` section 5, per the
author's instruction: a deeper evaluation of the effect on the text, a commit-history check for an
earlier reference at that site, a replacement candidate, and a drafted narrowed sentence with its
Appendix B row. **No edit to `3_cbic.tex` was made in this task.**

## 7 · What I could not confirm in this chapter

- `:145`, `huang2022estimating`: the edge-weight formula is attributed to the cited work and I could
  not locate the formula. Open as `[VERIFY]`.
- `:244`, `nash`: the less-frequent-update efficiency clause is not in the abstract of record and I
  did not read the paper body for it. Open as `[VERIFY]`.
- `zeng2019next` (four sites) returns no abstract at Crossref, OpenAlex or Semantic Scholar, and the
  Springer chapter is outside the network allowlist. All four sites are identity-of-baseline
  attributions that the record's title supports; no mechanism claim is made at any of them.

---

## `11_claims_4_courb.md`

# 11_claims_4_courb.md — citation claim-support audit, Chapter 4, CoUrb 2026

**Unit:** `src/chapters/4_courb.tex`  
**Run:** 2026-07-28, round 6, as the per-chapter pass the author asked for by name (COD-008 decision).  
**Errata regime for this unit:** PUBLISHED: a correction to reproduced prose is applied in the dissertation and listed in Appendix B; the published article record is not edited.

## 1 · Counts (every citation in the unit, not a sample)

- `\cite` commands in the unit: **50**, on **32** source lines, carrying **53** key instances (a multi-key `\cite` counts once per key). Every one was audited.
- Distinct bibliography keys used: **28**.
- Verdicts: **SUPPORTED** 47, **PARTIAL** 4, **NOT-SUPPORTED** 2.

Comments were stripped before counting, so a key that appears only inside a `%` comment is not counted; every counted site renders.

## 2 · Every citation, with its verdict

Verdict scale: SUPPORTED, the citing sentence's attribution is present in or a fair paraphrase of the
source; PARTIAL, part is supported and part is not, or the sentence is stronger than the source;
NOT-SUPPORTED, the attribution is absent from or contradicted by the source; UNVERIFIABLE, the source
of record does not carry enough to decide and the attribution is not implausible.

| # | Site (file:line) | Key | Verdict | Evidence quoted from the source (under 20 words) |
|---|---|---|---|---|
| 1 | `4_courb.tex:18` | `paiva2026stmtlnet` | SUPPORTED | "title=ST-MTLNet: Representações Espaço-Temporais de Pontos de Interesse para Aprendizado Multitarefa; venue=Anais do X Workshop de Computação Urbana (" |
| 2 | `4_courb.tex:25` | `cho2011gowalla` | SUPPORTED | "data from two online location-based social networks" |
| 3 | `4_courb.tex:25` | `jure2014snap` | SUPPORTED | "A collection of more than 50 large network datasets" |
| 4 | `4_courb.tex:32` | `caruana1997multitask` | SUPPORTED | "improves generalization by using the domain information contained in the training signals of related tasks" |
| 5 | `4_courb.tex:34` | `silva2025mtlnet` | SUPPORTED | "shares lower-level embeddings and sequence encoders while maintaining task-specific heads" |
| 6 | `4_courb.tex:38` | `wu2024torchspatial` | SUPPORTED | "a unified location encoding framework that consolidates 15 commonly recognized location encoders" |
| 7 | `4_courb.tex:40` | `jure2014snap` | SUPPORTED | "A collection of more than 50 large network datasets" |
| 8 | `4_courb.tex:60` | `feng2017poi2vec` | SUPPORTED | "we propose a new latent representation model POI2Vec that is able to incorporate the geographical influence" |
| 9 | `4_courb.tex:60` | `rahmani2019category` | PARTIAL | "previous studies fail to capture crucial information about POIs such as categorical information" |
| 10 | `4_courb.tex:62` | `huang2023hgi` | SUPPORTED | "aggregate POI embeddings and generate region raw embeddings" |
| 11 | `4_courb.tex:62` | `velickovic2019deep` | SUPPORTED | "DGI relies on maximizing mutual information between patch representations and corresponding high-level summaries of graphs" |
| 12 | `4_courb.tex:68` | `wu2024torchspatial` | SUPPORTED | "a unified location encoding framework that consolidates 15 commonly recognized location encoders, ensuring scalability and reproducibility" |
| 13 | `4_courb.tex:70` | `mai2023sphere2vecgeneralpurposelocationrepresentation` | SUPPORTED | "propose a multi-scale location encoder called Sphere2Vec which can preserve spherical distances when encoding point coordinates on a spherical surface" |
| 14 | `4_courb.tex:70` | `russwurm2024geographiclocationencodingspherical` | SUPPORTED | "combines spherical harmonic basis functions... with sinusoidal representation networks (SirenNets)... for globally distributed geographic data" |
| 15 | `4_courb.tex:70` | `sitzmann2020implicit` | SUPPORTED | "leverage periodic activation functions for implicit neural representations...ideally suited for representing complex natural signals" |
| 16 | `4_courb.tex:76` | `sun2020go` | SUPPORTED | "a nonlocal network for long-term preference modeling and a geo-dilated RNN for short-term preference learning" |
| 17 | `4_courb.tex:76` | `sun2024transtarec` | SUPPORTED | "fuse user preference and temporal influence... unification with user preference and sequential dynamics" |
| 18 | `4_courb.tex:78` | `kazemi2019time2vec` | SUPPORTED | "model-agnostic vector representation for time, called Time2Vec" |
| 19 | `4_courb.tex:82` | `Halder2022` | SUPPORTED | "propose a multi-task, multi-head attention transformer model...recommends the next POIs...and predicts queuing time...simultaneously" |
| 20 | `4_courb.tex:82` | `Liao2018` | SUPPORTED | "integrate the sequential dependency and temporal regularity of spatial activity topics" |
| 21 | `4_courb.tex:82` | `Xia2020` | PARTIAL | "exploits a structure of generative adversarial networks (GAN) simultaneously considering temporal check-ins and geographical locations" |
| 22 | `4_courb.tex:82` | `caruana1997multitask` | SUPPORTED | "Multitask Learning is an approach to inductive transfer that improves generalization by using the domain information" |
| 23 | `4_courb.tex:84` | `Lim2022` | SUPPORTED | "learning different User-Region matrices of lower sparsities in a multi-task setting" |
| 24 | `4_courb.tex:84` | `Xu2023` | SUPPORTED | "utilizes the predefined category hierarchy to regularize the relatedness among categories" |
| 25 | `4_courb.tex:89` | `silva2025mtlnet` | SUPPORTED | "We propose a joint MTL architecture that shares lower-level embeddings and sequence encoders while maintaining task-specific heads" |
| 26 | `4_courb.tex:96` | `kazemi2019time2vec` | SUPPORTED | "model-agnostic vector representation for time, called Time2Vec, that can be easily imported into many existing and future architectures" |
| 27 | `4_courb.tex:96` | `silva2025mtlnet` | SUPPORTED | "a joint MTL architecture that shares lower-level embeddings and sequence encoders" |
| 28 | `4_courb.tex:96` | `wu2024torchspatial` | SUPPORTED | "a learning framework and benchmark for location (point) encoding, which is one of the most fundamental data types" |
| 29 | `4_courb.tex:105` | `silva2025mtlnet` | SUPPORTED | "We propose a joint MTL architecture that shares lower-level embeddings and sequence encoders while maintaining task-specific heads" |
| 30 | `4_courb.tex:109` | `caruana1997multitask` | SUPPORTED | "learning tasks in parallel while using a shared representation" |
| 31 | `4_courb.tex:109` | `perez2018film` | SUPPORTED | "FiLM layers influence neural network computation via a simple, feature-wise affine transformation based on conditioning information" |
| 32 | `4_courb.tex:109` | `silva2025mtlnet` | SUPPORTED | "We propose a joint MTL architecture that shares lower-level embeddings and sequence encoders while maintaining task-specific heads" |
| 33 | `4_courb.tex:116` | `baxter2000model` | SUPPORTED | "the learner can search for a hypothesis space that contains good solutions to many of the problems" |
| 34 | `4_courb.tex:120` | `nash` | SUPPORTED | "viewing the gradients combination step as a bargaining game, where tasks negotiate to reach an agreement on a joint direction" |
| 35 | `4_courb.tex:124` | `silva2025mtlnet` | SUPPORTED | "We propose a joint MTL architecture that shares lower-level embeddings and sequence encoders while maintaining task-specific heads" |
| 36 | `4_courb.tex:124` | `silva2025mtlnet` | SUPPORTED | "a joint MTL architecture that shares lower-level embeddings and sequence encoders" |
| 37 | `4_courb.tex:124` | `velickovic2019deep` | SUPPORTED | "learning node representations within graph-structured data in an unsupervised manner" |
| 38 | `4_courb.tex:134` | `mai2023sphere2vecgeneralpurposelocationrepresentation` | SUPPORTED | "propose a multi-scale location encoder called Sphere2Vec which can preserve spherical distances when encoding point coordinates on a spherical surface" |
| 39 | `4_courb.tex:134` | `russwurm2024geographiclocationencodingspherical` | PARTIAL | "both spherical harmonics and sinusoidal representation networks are competitive on their own but set state-of-the-art performances when combined" |
| 40 | `4_courb.tex:134` | `wu2024torchspatial` | SUPPORTED | "TorchSpatial contains three key components: 1) a unified location encoding framework that consolidates 15 commonly recognized location encoders" |
| 41 | `4_courb.tex:153` | `russwurm2024geographiclocationencodingspherical` | PARTIAL | "sinusoidal representation networks (SirenNets) that can be interpreted as learned Double Fourier Sphere embedding" |
| 42 | `4_courb.tex:157` | `mai2023sphere2vecgeneralpurposelocationrepresentation` | SUPPORTED | "we propose a multi-scale location encoder called Sphere2Vec which can preserve spherical distances when encoding point coordinates on a spherical surf" |
| 43 | `4_courb.tex:161` | `sun2020go` | NOT-SUPPORTED | "a nonlocal network for long-term preference modeling and a geo-dilated RNN for short-term preference learning" |
| 44 | `4_courb.tex:163` | `kazemi2019time2vec` | SUPPORTED | "model-agnostic vector representation for time, called Time2Vec, that can be easily imported into many existing" |
| 45 | `4_courb.tex:176` | `huang2023hgi` | SUPPORTED | "the mutual information among the POI - region - city hierarchy is leveraged as the objective" |
| 46 | `4_courb.tex:208` | `grover2016node2vec` | SUPPORTED | "design a biased random walk procedure, which efficiently explores diverse neighborhoods" |
| 47 | `4_courb.tex:208` | `mikolov2013negsampling` | SUPPORTED | "a simple alternative to the hierarchical softmax called negative sampling" |
| 48 | `4_courb.tex:208` | `mikolov2013word2vec` | SUPPORTED | "two novel model architectures for computing continuous vector representations of words" |
| 49 | `4_courb.tex:219` | `belkin2003laplacian` | NOT-SUPPORTED | "a geometrically motivated algorithm for representing the high-dimensional data ... nonlinear dimensionality reduction" |
| 50 | `4_courb.tex:223` | `huang2023hgi` | SUPPORTED | "Learning urban region representations with POIs and hierarchical graph infomax" |
| 51 | `4_courb.tex:248` | `silva2025mtlnet` | SUPPORTED | "a joint MTL architecture that shares lower-level embeddings and sequence encoders" |
| 52 | `4_courb.tex:277` | `cho2011gowalla` | SUPPORTED | "data from two online location-based social networks" |
| 53 | `4_courb.tex:277` | `jure2014snap` | SUPPORTED | "A collection of more than 50 large network datasets" |
## 3 · Failures and partials in this unit, in detail

### `4_courb.tex:161` — `sun2020go` — **NOT-SUPPORTED**

**Citing sentence.** Human mobility patterns exhibit cyclical regularities, such as meal times and weekly movements, which carry discriminative information about the functional nature of the visited POIs \cite{sun2020go}.

**Reference resolved.** DOI 10.1609/aaai.v34i01.5353. Source of record: Crossref REST; OpenAlex API. Record reads: Where to Go Next: Modeling Long- and Short-Term User Preferences for Point-of-Interest Recommendation | Proceedings of the AAAI Conference on Artificial Intelligence | 2020 | type journal-article.

**Located passage.** "a nonlocal network for long-term preference modeling and a geo-dilated RNN for short-term preference learning"

**Why.** LSTPM (AAAI 2020) models long- and short-term user preference for next-POI recommendation. The citing sentence claims that cyclical regularities such as meal times and weekly movements carry discriminative information about the FUNCTIONAL NATURE of visited POIs. That is a claim about temporal signal predicting place semantics, which this paper does not make.

**Recommended disposition.** Published CoUrb prose. The chapter cites kazemi2019time2vec and Xu2023 elsewhere; neither states this either. Either narrow the sentence to the temporal regularity of visits (which sun2020go and cho2011gowalla both support) or find a source for the semantics half.

### `4_courb.tex:219` — `belkin2003laplacian` — **NOT-SUPPORTED**

**Citing sentence.** The implementation incorporates a hierarchical regularization term \cite{belkin2003laplacian} between category and \textit{fclass}: $\mathcal{L}_{\text{hier}} = \sum_{(c,s) \in \mathcal{H}} \left\| \mathbf{e}_s - \mathbf{e}_c \right\|_2^2$, in which $\mathcal{H}$ contains the (category, \textit{fclass}) pairs.

**Reference resolved.** DOI 10.1162/089976603321780317. Source of record: Crossref REST; OpenAlex API. Record reads: Laplacian Eigenmaps for Dimensionality Reduction and Data Representation | Neural Computation | 2003 | type journal-article.

**Located passage.** "a geometrically motivated algorithm for representing the high-dimensional data ... nonlinear dimensionality reduction"

**Why.** Laplacian eigenmaps is a manifold dimensionality-reduction method. The cited object is an L2 penalty pulling a subcategory embedding toward its parent category embedding, that is, a hierarchical regularizer over a known label tree. The connection is at best thematic (graph Laplacian smoothness) and the sentence attributes the term itself.

**Recommended disposition.** Published CoUrb prose. Xu2023, already in the bibliography, regularizes category relatedness with a predefined category hierarchy, which is what this term does. Swap the key, or drop the citation and present the term as the implementation's own.

### `4_courb.tex:60` — `rahmani2019category` — **PARTIAL**

**Citing sentence.** CATAPE (\textit{Category-Aware Location Embedding}) \cite{rahmani2019category} extends this idea by incorporating categorical and sequential information, capturing the geographic influence between POIs based on the temporal sequence of user visits.

**Reference resolved.** DOI 10.1145/3341981.3344240. Source of record: Crossref REST; OpenAlex API. Record reads: Category-Aware Location Embedding for Point-of-Interest Recommendation | Proceedings of the 2019 ACM SIGIR International Conference on Theory of Information Retrieval | 2019 | type proceedings-article.

**Located passage.** "previous studies fail to capture crucial information about POIs such as categorical information"

**Why.** Crossref returns a truncated abstract for this SIGIR ICTIR paper (four sentences). The categorical half is supported. The sequential/temporal-visit-order half is not visible in what the source of record returns.

**Recommended disposition.** Open as [VERIFY] on the sequential clause only. Published CoUrb prose, low exposure.

### `4_courb.tex:82` — `Xia2020` — **PARTIAL**

**Citing sentence.** MTPR \cite{Xia2020} jointly models location and temporal context through geographic LSTMs and adversarial learning.

**Reference resolved.** DOI 10.3390/app10196664. Source of record: Crossref REST; OpenAlex API. Record reads: MTPR: A Multi-Task Learning Based POI Recommendation Considering Temporal Check-Ins and Geographical Locations | Applied Sciences | 2020 | type journal-article.

**Located passage.** "exploits a structure of generative adversarial networks (GAN) simultaneously considering temporal check-ins and geographical locations"

**Why.** Same work, same defect class as 3_cbic.tex:125: adversarial learning and joint temporal-geographic modeling are supported; "geographic LSTMs" is not in the abstract.

**Recommended disposition.** Published CoUrb prose. Same disposition as the Ch.3 site; fix both or neither, so the chapters do not describe one system two ways.

### `4_courb.tex:134` — `russwurm2024geographiclocationencodingspherical` — **PARTIAL**

**Citing sentence.** This chapter selects two \textit{encoders} that represent distinct spatial encoding paradigms: SIREN \cite{russwurm2024geographiclocationencodingspherical}, which models continuous functions through sinusoidal activations with controllable frequencies, and Sphere2Vec-M \cite{mai2023sphere2vecgeneralpurposelocationrepresentation}, which operates directly on spherical coordinates preserving geodesic distance properties.

**Reference resolved.** arXiv:2310.06743. Source of record: arXiv API; OpenAlex API. Record reads: Geographic Location Encoding with Spherical Harmonics and Sinusoidal Representation Networks | Published as a conference paper at ICLR 2024 | 2023 | type posted-content.

**Located passage.** "both spherical harmonics and sinusoidal representation networks are competitive on their own but set state-of-the-art performances when combined"

**Why.** The paper proposes spherical harmonics COMBINED with SirenNets. The chapter uses the name SIREN for the sinusoidal-network half and describes only that half. By the paper's own words the halves are separable and each is competitive alone, so naming one is defensible, but the chapter never says which component of the cited work it instantiated.

**Recommended disposition.** Published CoUrb prose. One clause would close it: state that the encoder used is the sinusoidal-representation-network component of that work. This also affects 4_courb.tex:153.

### `4_courb.tex:153` — `russwurm2024geographiclocationencodingspherical` — **PARTIAL**

**Citing sentence.** The SIREN model (\textit{Sinusoidal Representation Networks}) \cite{russwurm2024geographiclocationencodingspherical} models a continuous function $f_\theta : \mathbb{R}^2 \rightarrow \mathbb{R}^{64}$ that directly maps normalized geographic coordinates into a vector \textit{embedding}.

**Reference resolved.** arXiv:2310.06743. Source of record: arXiv API; OpenAlex API. Record reads: Geographic Location Encoding with Spherical Harmonics and Sinusoidal Representation Networks | Published as a conference paper at ICLR 2024 | 2023 | type posted-content.

**Located passage.** "sinusoidal representation networks (SirenNets) that can be interpreted as learned Double Fourier Sphere embedding"

**Why.** Same issue as :134. The R^2 -> R^64 map and the 64-dimensional output are this chapter's own configuration, not the paper's claim.

**Recommended disposition.** As :134.

## 4 · Source ledger for this unit

Every distinct key cited in this unit, the identifier it resolved by, and where I opened it this session.

| Key | Identifier | Opened at | Record as returned |
|---|---|---|---|
| `Halder2022` | DOI 10.1007/s10618-022-00865-w | Crossref REST; OpenAlex API | POI recommendation with queuing time and user interest awareness \| Data Mining and Knowledge Discovery \| 2022 \| type journal-article |
| `Liao2018` | DOI 10.24963/ijcai.2018/477 | Crossref REST; OpenAlex API | Predicting Activity and Location with Multi-task Context Aware Recurrent Neural Network \| Proceedings of the Twenty-Seventh International Joint Conference on Artificial  |
| `Lim2022` | DOI 10.1145/3477495.3531989 | Crossref REST; OpenAlex API | Hierarchical Multi-Task Graph Recurrent Network for Next POI Recommendation \| Proceedings of the 45th International ACM SIGIR Conference on Research and Development in I |
| `Xia2020` | DOI 10.3390/app10196664 | Crossref REST; OpenAlex API | MTPR: A Multi-Task Learning Based POI Recommendation Considering Temporal Check-Ins and Geographical Locations \| Applied Sciences \| 2020 \| type journal-article |
| `Xu2023` | DOI 10.1145/3582553 | Crossref REST; OpenAlex API | TME: Tree-guided Multi-task Embedding Learning towards Semantic Venue Annotation \| ACM Transactions on Information Systems \| 2023 \| type journal-article |
| `baxter2000model` | DOI 10.1613/jair.731 | Crossref REST; OpenAlex API | A Model of Inductive Bias Learning \| Journal of Artificial Intelligence Research \| 2000 \| type journal-article |
| `belkin2003laplacian` | DOI 10.1162/089976603321780317 | Crossref REST; OpenAlex API | Laplacian Eigenmaps for Dimensionality Reduction and Data Representation \| Neural Computation \| 2003 \| type journal-article |
| `caruana1997multitask` | DOI 10.1023/A:1007379606734 | Crossref REST; OpenAlex API; PDF in repo: 10.1023_A_1007379606734.pdf | Multitask Learning \| Machine Learning \| 1997 \| type journal-article |
| `cho2011gowalla` | DOI 10.1145/2020408.2020579 | Crossref REST; OpenAlex API | Friendship and mobility \| Proceedings of the 17th ACM SIGKDD international conference on Knowledge discovery and data mining \| 2011 \| type proceedings-article |
| `feng2017poi2vec` | DOI 10.1609/aaai.v31i1.10500 | Crossref REST; OpenAlex API | POI2Vec: Geographical Latent Representation for Predicting Future Visitors \| Proceedings of the AAAI Conference on Artificial Intelligence \| 2017 \| type journal-articl |
| `grover2016node2vec` | DOI 10.1145/2939672.2939754 | Crossref REST; OpenAlex API | node2vec \| Proceedings of the 22nd ACM SIGKDD International Conference on Knowledge Discovery and Data Mining \| 2016 \| type proceedings-article |
| `huang2023hgi` | DOI 10.1016/j.isprsjprs.2022.11.021 | Crossref REST; OpenAlex API; Semantic Scholar API; PDF in repo: Learning urban region representations with POIs and hierarchical graph infomax.pdf | Learning urban region representations with POIs and hierarchical graph infomax \| ISPRS Journal of Photogrammetry and Remote Sensing \| 2023 \| type journal-article |
| `jure2014snap` | no identifier in the bib entry | OpenAlex API | {SNAP Datasets}: {Stanford} Large Network Dataset Collection \| (no venue in record) \| 2014 \| type article |
| `kazemi2019time2vec` | arXiv:1907.05321 | arXiv API; OpenAlex API | Time2Vec: Learning a Vector Representation of Time \| arXiv preprint \| 2019 \| type posted-content |
| `mai2023sphere2vecgeneralpurposelocationrepresentation` | arXiv:2306.17624 | arXiv API; OpenAlex API | Sphere2Vec: A General-Purpose Location Representation Learning over a Spherical Surface for Large-Scale Geospatial Predictions \| ISPRS Journal of Photogrammetry and Remo |
| `mikolov2013negsampling` | arXiv:1310.4546 | arXiv API; OpenAlex API | Distributed Representations of Words and Phrases and their Compositionality \| arXiv preprint \| 2013 \| type posted-content |
| `mikolov2013word2vec` | arXiv:1301.3781 | arXiv API; OpenAlex API | Efficient Estimation of Word Representations in Vector Space \| arXiv preprint \| 2013 \| type posted-content |
| `nash` | no identifier in the bib entry | arXiv API; OpenAlex API | Multi-Task Learning as a Bargaining Game \| arXiv preprint \| 2022 \| type posted-content |
| `paiva2026stmtlnet` | DOI 10.5753/courb.2026.22960 | Crossref REST; OpenAlex API | ST-MTLNet: Representações Espaço-Temporais de Pontos de Interesse para Aprendizado Multitarefa \| Anais do X Workshop de Computação Urbana (CoUrb 2026) \| 2026 \| type pr |
| `perez2018film` | DOI 10.1609/aaai.v32i1.11671 | Crossref REST; OpenAlex API | FiLM: Visual Reasoning with a General Conditioning Layer \| Proceedings of the AAAI Conference on Artificial Intelligence \| 2018 \| type journal-article |
| `rahmani2019category` | DOI 10.1145/3341981.3344240 | Crossref REST; OpenAlex API | Category-Aware Location Embedding for Point-of-Interest Recommendation \| Proceedings of the 2019 ACM SIGIR International Conference on Theory of Information Retrieval \| |
| `russwurm2024geographiclocationencodingspherical` | arXiv:2310.06743 | arXiv API; OpenAlex API | Geographic Location Encoding with Spherical Harmonics and Sinusoidal Representation Networks \| Published as a conference paper at ICLR 2024 \| 2023 \| type posted-conten |
| `silva2025mtlnet` | DOI 10.21528/CBIC2025-1191324 | Crossref REST; OpenAlex API | An Investigation into Multi-Task Learning for Point-of-Interest Category Classification and Next-POI Prediction \| Anais do XVII Congresso Brasileiro de Inteligência Comp |
| `sitzmann2020implicit` | arXiv:2006.09661 | arXiv API; OpenAlex API | Implicit Neural Representations with Periodic Activation Functions \| arXiv preprint \| 2020 \| type posted-content |
| `sun2020go` | DOI 10.1609/aaai.v34i01.5353 | Crossref REST; OpenAlex API | Where to Go Next: Modeling Long- and Short-Term User Preferences for Point-of-Interest Recommendation \| Proceedings of the AAAI Conference on Artificial Intelligence \|  |
| `sun2024transtarec` | DOI 10.1109/ICCEA62105.2024.10603711 | Crossref REST; OpenAlex API | TransTARec: Time-Adaptive Translating Embedding Model for Next POI Recommendation \| 2024 5th International Conference on Computer Engineering and Application (ICCEA) \|  |
| `velickovic2019deep` | no identifier in the bib entry | OpenAlex API | Deep Graph Infomax \| Apollo (University of Cambridge) \| 2018 \| type conference-paper |
| `wu2024torchspatial` | arXiv:2406.15658 | arXiv API; OpenAlex API | TorchSpatial: A Location Encoding Framework and Benchmark for Spatial Representation Learning \| arXiv preprint \| 2024 \| type posted-content |

## 5 · Provenance of every failure in this chapter

All six non-SUPPORTED sites are the English donor text of the published CoUrb 2026 article, matched
as exact string prefixes against `articles/CoUrb_2026/src_en/sections/related.tex` and
`.../metodology.tex`. The version of record is the Portuguese text; I spot-checked the PT source at
`articles/CoUrb_2026/src/sections/related.tex` for the POI2Vec and CATAPE sentences and the claims
map one to one ("adapta a arquitetura Word2Vec ... por meio de uma estrutura de arvore binaria
geografica"; "estende essa ideia incorporando informacoes categoricas e sequenciais"), so the
findings are properties of the published article and not of the translation.

One point worth the author's attention: the PT introduction at `articles/CoUrb_2026/src/sections/
intro.tex` says the two spatial encoders were "originalmente validadas em tarefas geoespaciais de
sensoriamento remoto e ecologia \cite{wu2024torchspatial}" — the same "originally validated"
attribution to TorchSpatial that Chapter 1 carries at `1_introduction.tex:50` and that is flagged
PARTIAL there. The two sites are the same claim and should take the same disposition.

## 6 · What I could not confirm in this chapter

- `:60`, `rahmani2019category`: Crossref returns a truncated abstract (four sentences) for this
  ICTIR paper. The categorical half of the citing sentence is supported; the sequential half is not
  visible in what the source of record returns. Open as `[VERIFY]` on that clause only.
- `:60`, `feng2017poi2vec`: the Word2Vec lineage and the geographic binary tree are POI2Vec's
  construction but are not in the abstract. The load-bearing half (geographic influence in the
  embedding) is verbatim.

---

## `11_claims_5_mobiwac.md`

# 11_claims_5_mobiwac.md — citation claim-support audit, Chapter 5, MobiWac 2026

**Unit:** `src/chapters/5_mobiwac.tex`  
**Run:** 2026-07-28, round 6, as the per-chapter pass the author asked for by name (COD-008 decision).  
**Errata regime for this unit:** UNDER REVIEW: a correction is applied to the dissertation AND to articles/[mobiwac]/src/ so the two texts stay identical, then named in that article's own errata record rather than in Appendix B (author instruction, 2026-07-27).

## 1 · Counts (every citation in the unit, not a sample)

- `\cite` commands in the unit: **56**, on **43** source lines, carrying **60** key instances (a multi-key `\cite` counts once per key). Every one was audited.
- Distinct bibliography keys used: **33**.
- Verdicts: **SUPPORTED** 57, **PARTIAL** 3.

Comments were stripped before counting, so a key that appears only inside a `%` comment is not counted; every counted site renders.

## 2 · Every citation, with its verdict

Verdict scale: SUPPORTED, the citing sentence's attribution is present in or a fair paraphrase of the
source; PARTIAL, part is supported and part is not, or the sentence is stronger than the source;
NOT-SUPPORTED, the attribution is absent from or contradicted by the source; UNVERIFIABLE, the source
of record does not carry enough to decide and the attribution is not implausible.

| # | Site (file:line) | Key | Verdict | Evidence quoted from the source (under 20 words) |
|---|---|---|---|---|
| 1 | `5_mobiwac.tex:40` | `bastug2014edge` | SUPPORTED | "peak traffic demands can be substantially reduced by proactively serving predictable user demands via caching at base stations" |
| 2 | `5_mobiwac.tex:40` | `cho2011gowalla` | SUPPORTED | "data from two online location-based social networks, we aim to understand what basic laws govern human motion" |
| 3 | `5_mobiwac.tex:40` | `moura2025mobilityaware` | SUPPORTED | "leverage a large dataset of Foursquare check-ins... Mobility-aware systems play a crucial role in leveraging such insights to design adaptive, data-dr" |
| 4 | `5_mobiwac.tex:40` | `song2010limits` | SUPPORTED | "there was 93% predictability across the whole user base" |
| 5 | `5_mobiwac.tex:40` | `vielhaus2022handover` | SUPPORTED | "Predicting handovers in high mobility scenarios enables networks and applications to adapt ahead of time to improve the Quality of Service" |
| 6 | `5_mobiwac.tex:44` | `caruana1997multitask` | PARTIAL | "what is learned for each task can help other tasks be learned better" |
| 7 | `5_mobiwac.tex:45` | `silva2025mtlnet` | SUPPORTED | "the multi-task learning approach did not consistently yield substantial improvements over the single-task baselines" |
| 8 | `5_mobiwac.tex:53` | `huang2023hgi` | SUPPORTED | "the mutual information among the POI - region - city hierarchy is leveraged as the objective" |
| 9 | `5_mobiwac.tex:53` | `velickovic2019deep` | SUPPORTED | "DGI relies on maximizing mutual information between patch representations and corresponding high-level summaries of graphs" |
| 10 | `5_mobiwac.tex:55` | `wongso2025massivesteps` | SUPPORTED | "a large-scale, publicly available benchmark dataset built upon the Semantic Trails dataset" |
| 11 | `5_mobiwac.tex:96` | `silva2025mtlnet` | SUPPORTED | "a joint MTL architecture that shares lower-level embeddings and sequence encoders while maintaining task-specific heads" |
| 12 | `5_mobiwac.tex:103` | `paiva2026stmtlnet` | SUPPORTED | "supera o baseline em todas as 21 combinações de categoria e estado para classificação" |
| 13 | `5_mobiwac.tex:112` | `velickovic2019deep` | SUPPORTED | "maximizing mutual information between patch representations and corresponding high-level summaries of graphs" |
| 14 | `5_mobiwac.tex:116` | `huang2023hgi` | SUPPORTED | "the mutual information among the POI - region - city hierarchy is leveraged as the objective" |
| 15 | `5_mobiwac.tex:120` | `lin2021ctle` | SUPPORTED | "calculates a location's representation vector with consideration of its specific contextual neighbors in trajectories" |
| 16 | `5_mobiwac.tex:138` | `feng2018deepmove` | SUPPORTED | "DeepMove, an attentional recurrent network for mobility prediction from lengthy and sparse trajectories" |
| 17 | `5_mobiwac.tex:139` | `luo2021stan` | SUPPORTED | "Spatio-Temporal Attention Network for Next Location Recommendation" |
| 18 | `5_mobiwac.tex:139` | `yang2022getnext` | SUPPORTED | "GETNext incorporates the global transition patterns, user's general preference, spatio-temporal context ... into a transformer model" |
| 19 | `5_mobiwac.tex:144` | `luca2021mobilitysurvey` | SUPPORTED | "guide to the leading deep learning solutions to next-location prediction, crowd flow prediction, trajectory generation, and flow generation" |
| 20 | `5_mobiwac.tex:146` | `silva2025mtlnet` | SUPPORTED | "the multi-task learning approach did not consistently yield substantial improvements over the single-task baselines across both tasks" |
| 21 | `5_mobiwac.tex:153` | `Lim2022` | PARTIAL | "learning different User-Region matrices of lower sparsities in a multi-task setting" |
| 22 | `5_mobiwac.tex:153` | `sun2024mcmg` | SUPPORTED | "local multi-channel (i.e., region, category, and POI channels) encoder" |
| 23 | `5_mobiwac.tex:158` | `zhu2022drrgnn` | SUPPORTED | "developing models that can answer... (2) Which region will be the next AR, and (3) Why do people make this regional mobility" |
| 24 | `5_mobiwac.tex:160` | `sun2025kgtb` | SUPPORTED | "introduces multiple behavior-specific prediction tasks for LLM fine-tuning, e.g., POI, category, and region visit behaviors" |
| 25 | `5_mobiwac.tex:166` | `Liao2018` | SUPPORTED | "Multi-task Context Aware Recurrent Neural Network to leverage the spatial activity topic for activity and location prediction" |
| 26 | `5_mobiwac.tex:168` | `wang2025hamtl` | SUPPORTED | "Hierarchy Aware-based Multi-task Learning for User Location Prediction" |
| 27 | `5_mobiwac.tex:171` | `ye2013nextmove` | SUPPORTED | "predict the category of user activity at the next step and then predict the most likely location given the estimated category distribution" |
| 28 | `5_mobiwac.tex:172` | `huang2024cslsl` | SUPPORTED | "explicitly model the "when → what → where", a.k.a. "time → activity → location" decision logic" |
| 29 | `5_mobiwac.tex:174` | `yu2020catdm` | SUPPORTED | "incorporates POI category and geographical influence to reduce search space" |
| 30 | `5_mobiwac.tex:181` | `caruana1997multitask` | PARTIAL | "learning tasks in parallel while using a shared representation" |
| 31 | `5_mobiwac.tex:183` | `nash` | SUPPORTED | "combine per-task gradients into a joint update direction using a particular heuristic" |
| 32 | `5_mobiwac.tex:183` | `yu2020pcgrad` | SUPPORTED | "propose a form of gradient surgery that projects a task's gradient onto the normal plane" |
| 33 | `5_mobiwac.tex:184` | `xin2022domtl` | SUPPORTED | "MTO methods do not yield any performance improvements beyond what is achievable via traditional optimization approaches" |
| 34 | `5_mobiwac.tex:258` | `silva2019urbancomputing` | SUPPORTED | "a survey of recent urban computing studies that make use of LBSN data" |
| 35 | `5_mobiwac.tex:260` | `moura2025mobilityaware` | SUPPORTED | "Key points of interest (especially transportation hubs and cultural landmarks) serve as essential connectors shaping network flow" |
| 36 | `5_mobiwac.tex:280` | `huang2023hgi` | SUPPORTED | "row-wise shuffling of the POI graph's feature matrix Xp ... to form a corrupted graph" |
| 37 | `5_mobiwac.tex:280` | `velickovic2019deep` | SUPPORTED | "maximizing mutual information between patch representations and corresponding high-level summaries" |
| 38 | `5_mobiwac.tex:300` | `caruana1997multitask` | SUPPORTED | "learning tasks in parallel while using a shared representation; what is learned for each task can help other tasks" |
| 39 | `5_mobiwac.tex:327` | `cho2011gowalla` | SUPPORTED | "data from two online location-based social networks" |
| 40 | `5_mobiwac.tex:328` | `wongso2025massivesteps` | SUPPORTED | "Massive-STEPS spans 15 geographically and culturally diverse cities" |
| 41 | `5_mobiwac.tex:388` | `holm1979` | SUPPORTED | "a simple and widely applicable multiple test procedure of the sequentially rejective type" |
| 42 | `5_mobiwac.tex:388` | `lakens2017tost` | SUPPORTED | "an upper and lower equivalence bound is specified based on the smallest effect size of interest" |
| 43 | `5_mobiwac.tex:392` | `Lim2022` | SUPPORTED | "Hierarchical Multi-Task Graph Recurrent Network (HMT-GRN) approach" |
| 44 | `5_mobiwac.tex:392` | `capanema2023poirgnn` | SUPPORTED | "Combining recurrent and Graph Neural Networks to predict the next place's category" |
| 45 | `5_mobiwac.tex:392` | `li2025rehdm` | SUPPORTED | "ReHDM utilizes regional encoding to mine the potential spatial relationships among POIs with coarse-grained geographical information" |
| 46 | `5_mobiwac.tex:392` | `luo2021stan` | SUPPORTED | "STAN explicitly exploits relative spatiotemporal information of all the check-ins with self-attention layers along the trajectory" |
| 47 | `5_mobiwac.tex:394` | `lin2021ctle` | SUPPORTED | "calculates a location's representation vector with consideration of its specific contextual neighbors in trajectories" |
| 48 | `5_mobiwac.tex:396` | `huang2023hgi` | SUPPORTED | "aggregate POI embeddings and generate region raw embeddings" |
| 49 | `5_mobiwac.tex:396` | `huang2024cslsl` | SUPPORTED | "explicitly model the “ when → what → where ”, a.k.a. “ time → activity → location ” decision logic" |
| 50 | `5_mobiwac.tex:396` | `ye2013nextmove` | SUPPORTED | "predict the category of user activity at the next step and then predict the most likely location given the estimated category distribution" |
| 51 | `5_mobiwac.tex:396` | `yu2020catdm` | SUPPORTED | "incorporates POI category and geographical influence to reduce search space" |
| 52 | `5_mobiwac.tex:404` | `huang2023hgi` | SUPPORTED | "aggregate POI embeddings and generate region raw embeddings" |
| 53 | `5_mobiwac.tex:409` | `lin2021ctle` | SUPPORTED | "calculates a location's representation vector with consideration of its specific contextual neighbors in trajectories" |
| 54 | `5_mobiwac.tex:578` | `caruana1997multitask` | SUPPORTED | "improves generalization by using the domain information contained in the training signals of related tasks" |
| 55 | `5_mobiwac.tex:664` | `Lim2022` | SUPPORTED | "learning different User-Region matrices of lower sparsities in a multi-task setting" |
| 56 | `5_mobiwac.tex:664` | `luo2021stan` | SUPPORTED | "STAN explicitly exploits relative spatiotemporal information of all the check-ins with self-attention layers" |
| 57 | `5_mobiwac.tex:665` | `li2025rehdm` | SUPPORTED | "ReHDM utilizes regional encoding to mine the potential spatial relationships among POIs" |
| 58 | `5_mobiwac.tex:666` | `capanema2023poirgnn` | SUPPORTED | "Combining recurrent and Graph Neural Networks to predict the next place's category" |
| 59 | `5_mobiwac.tex:750` | `huang2024cslsl` | SUPPORTED | "utilizes a causal structure based on multi-task learning to explicitly model the "when -> what -> where" ... decision logic" |
| 60 | `5_mobiwac.tex:810` | `moura2025mobilityaware` | SUPPORTED | "One potential research direction is the integration of the analyzed metrics with machine learning algorithms" |
## 3 · Failures and partials in this unit, in detail

### `5_mobiwac.tex:44` — `caruana1997multitask` — **PARTIAL**

**Citing sentence.** Sharing one representation across tasks has a cost: in multi-task learning (MTL), one model does several jobs at once by sharing most of its parts, so the shared parameters can converge to a compromise optimal for neither task, helping one while hurting the other~\cite{caruana1997multitask}.

**Reference resolved.** DOI 10.1023/A:1007379606734. Source of record: Crossref REST; OpenAlex API; PDF in repo: 10.1023_A_1007379606734.pdf. Record reads: Multitask Learning | Machine Learning | 1997 | type journal-article.

**Located passage.** "what is learned for each task can help other tasks be learned better"

**Why.** The compromise-optimal-for-neither mechanism is the negative-transfer reading of shared representations. Caruana 1997 is the origin of the shared-representation idea and the paper does discuss when MTL helps, but the abstract states the positive direction. The chapter itself corrected an adjacent claim in the same passage in round 4 (comment at :46-50).

**Recommended disposition.** Under review, so a change propagates to articles/[mobiwac]/src/ and to that article's errata rather than Appendix B. Lowest-cost repair: cite a work whose stated finding is negative transfer. standley2020tasks says "often leads to inferior overall performance as task objectives can compete" and is already in the bibliography, cited for exactly this at 2_fundamentals.tex:310.

### `5_mobiwac.tex:153` — `Lim2022` — **PARTIAL**

**Citing sentence.** The field increasingly models several granularities at once; in those systems, category and region are auxiliary signals that help a primary next-place task (MCMG \cite{sun2024mcmg}, HMT-GRN \cite{Lim2022}).

**Reference resolved.** DOI 10.1145/3477495.3531989. Source of record: Crossref REST; OpenAlex API. Record reads: Hierarchical Multi-Task Graph Recurrent Network for Next POI Recommendation | Proceedings of the 45th International ACM SIGIR Conference on Research and Development in Information Retrieval | 2022 | type proceedings-article.

**Located passage.** "learning different User-Region matrices of lower sparsities in a multi-task setting"

**Why.** In HMT-GRN region IS a multi-task target, used to alleviate User-POI sparsity and then searched hierarchically toward the next POI. So "auxiliary signals that help a primary next-place task" is right about the ROLE (next POI is the end target) and understates that region is a trained target. The chapter's own next sentences make exactly this distinction, so the paragraph as a whole is accurate.

**Recommended disposition.** Leave; the following sentences carry the distinction. If tightened, say the coarse target is trained but subordinate.

### `5_mobiwac.tex:181` — `caruana1997multitask` — **PARTIAL**

**Citing sentence.** On optimization, we are conservative by design: joint training with a fixed loss weighting is standard practice \cite{caruana1997multitask}, not itself our contribution.

**Reference resolved.** DOI 10.1023/A:1007379606734. Source of record: Crossref REST; OpenAlex API; PDF in repo: 10.1023_A_1007379606734.pdf. Record reads: Multitask Learning | Machine Learning | 1997 | type journal-article.

**Located passage.** "learning tasks in parallel while using a shared representation"

**Why.** Joint training with a shared representation is supported. "with a fixed loss weighting is standard practice" is a claim about current practice; the sentence's own next clause cites xin2022domtl and kurin2022scalarization, which do establish that a fixed or uniform weighting is the baseline to beat.

**Recommended disposition.** Leave, or move the fixed-weighting clause onto kurin2022scalarization / xin2022domtl, which are cited two lines later.

## 4 · Source ledger for this unit

Every distinct key cited in this unit, the identifier it resolved by, and where I opened it this session.

| Key | Identifier | Opened at | Record as returned |
|---|---|---|---|
| `Liao2018` | DOI 10.24963/ijcai.2018/477 | Crossref REST; OpenAlex API | Predicting Activity and Location with Multi-task Context Aware Recurrent Neural Network \| Proceedings of the Twenty-Seventh International Joint Conference on Artificial  |
| `Lim2022` | DOI 10.1145/3477495.3531989 | Crossref REST; OpenAlex API | Hierarchical Multi-Task Graph Recurrent Network for Next POI Recommendation \| Proceedings of the 45th International ACM SIGIR Conference on Research and Development in I |
| `bastug2014edge` | DOI 10.1109/MCOM.2014.6871674 | Crossref REST; OpenAlex API | Living on the edge: The role of proactive caching in 5G wireless networks \| IEEE Communications Magazine \| 2014 \| type journal-article |
| `capanema2023poirgnn` | DOI 10.1016/j.adhoc.2022.103016 | Crossref REST; OpenAlex API | Combining recurrent and Graph Neural Networks to predict the next place’s category \| Ad Hoc Networks \| 2023 \| type journal-article |
| `caruana1997multitask` | DOI 10.1023/A:1007379606734 | Crossref REST; OpenAlex API; PDF in repo: 10.1023_A_1007379606734.pdf | Multitask Learning \| Machine Learning \| 1997 \| type journal-article |
| `cho2011gowalla` | DOI 10.1145/2020408.2020579 | Crossref REST; OpenAlex API | Friendship and mobility \| Proceedings of the 17th ACM SIGKDD international conference on Knowledge discovery and data mining \| 2011 \| type proceedings-article |
| `feng2018deepmove` | DOI 10.1145/3178876.3186058 | Crossref REST; OpenAlex API | DeepMove \| Proceedings of the 2018 World Wide Web Conference on World Wide Web - WWW '18 \| 2018 \| type proceedings-article |
| `holm1979` | no identifier in the bib entry | OpenAlex API | A Simple Sequentially Rejective Multiple Test Procedure \| Scandinavian Journal of Statistics \| 1979 \| type article |
| `huang2023hgi` | DOI 10.1016/j.isprsjprs.2022.11.021 | Crossref REST; OpenAlex API; Semantic Scholar API; PDF in repo: Learning urban region representations with POIs and hierarchical graph infomax.pdf | Learning urban region representations with POIs and hierarchical graph infomax \| ISPRS Journal of Photogrammetry and Remote Sensing \| 2023 \| type journal-article |
| `huang2024cslsl` | DOI 10.1140/epjds/s13688-024-00460-7 | Crossref REST; OpenAlex API | Human mobility prediction with causal and spatial-constrained multi-task network \| EPJ Data Science \| 2024 \| type journal-article |
| `lakens2017tost` | DOI 10.1177/1948550617697177 | Crossref REST; OpenAlex API | Equivalence Tests \| Social Psychological and Personality Science \| 2017 \| type journal-article |
| `li2025rehdm` | DOI 10.24963/ijcai.2025/343 | Crossref REST; OpenAlex API | Beyond Individual and Point: Next POI Recommendation via Region-aware Dynamic Hypergraph with Dual-level Modeling \| Proceedings of the Thirty-Fourth International Joint  |
| `lin2021ctle` | DOI 10.1609/aaai.v35i5.16548 | Crossref REST; OpenAlex API | Pre-training Context and Time Aware Location Embeddings from Spatial-Temporal Trajectories for User Next Location Prediction \| Proceedings of the AAAI Conference on Arti |
| `luca2021mobilitysurvey` | DOI 10.1145/3485125 | Crossref REST; OpenAlex API | A Survey on Deep Learning for Human Mobility \| ACM Computing Surveys \| 2021 \| type journal-article |
| `luo2021stan` | DOI 10.1145/3442381.3449998 | Crossref REST; OpenAlex API | STAN: Spatio-Temporal Attention Network for Next Location Recommendation \| Proceedings of the Web Conference 2021 \| 2021 \| type proceedings-article |
| `moura2025mobilityaware` | DOI 10.1109/MSWiM67937.2025.11308734 | Crossref REST; OpenAlex API | On the Design of Mobility-Aware Systems: A Tourist’s Perspective \| 2025 International Conference on Modeling, Analysis and Simulation of Wireless and Mobile Systems (MSW |
| `nash` | no identifier in the bib entry | arXiv API; OpenAlex API | Multi-Task Learning as a Bargaining Game \| arXiv preprint \| 2022 \| type posted-content |
| `paiva2026stmtlnet` | DOI 10.5753/courb.2026.22960 | Crossref REST; OpenAlex API | ST-MTLNet: Representações Espaço-Temporais de Pontos de Interesse para Aprendizado Multitarefa \| Anais do X Workshop de Computação Urbana (CoUrb 2026) \| 2026 \| type pr |
| `silva2019urbancomputing` | DOI 10.1145/3301284 | Crossref REST; OpenAlex API | Urban Computing Leveraging Location-Based Social Network Data \| ACM Computing Surveys \| 2019 \| type journal-article |
| `silva2025mtlnet` | DOI 10.21528/CBIC2025-1191324 | Crossref REST; OpenAlex API | An Investigation into Multi-Task Learning for Point-of-Interest Category Classification and Next-POI Prediction \| Anais do XVII Congresso Brasileiro de Inteligência Comp |
| `song2010limits` | DOI 10.1126/science.1177170 | Crossref REST; OpenAlex API; PDF in repo: 201002-19_Science-Predictability.pdf | Limits of Predictability in Human Mobility \| Science \| 2010 \| type journal-article |
| `sun2024mcmg` | DOI 10.1145/3592789 | Crossref REST; OpenAlex API | A Multi-channel Next POI Recommendation Framework with Multi-granularity Check-in Signals \| ACM Transactions on Information Systems \| 2023 \| type journal-article |
| `sun2025kgtb` | DOI 10.48550/arXiv.2509.12350 | arXiv API; OpenAlex API | Knowledge Graph Tokenization for Behavior-Aware Generative Next POI Recommendation \| arXiv preprint \| 2025 \| type posted-content |
| `velickovic2019deep` | no identifier in the bib entry | OpenAlex API | Deep Graph Infomax \| Apollo (University of Cambridge) \| 2018 \| type conference-paper |
| `vielhaus2022handover` | DOI 10.1145/3551660.3560913 | Crossref REST; OpenAlex API | Handover Predictions as an Enabler for Anticipatory Service Adaptations in Next-Generation Cellular Networks \| Proceedings of the 20th ACM International Symposium on Mob |
| `wang2025hamtl` | DOI 10.1007/s11227-025-07643-7 | Crossref REST; OpenAlex API | Hierarchy aware-based multi-task learning for user location prediction \| The Journal of Supercomputing \| 2025 \| type journal-article |
| `wongso2025massivesteps` | no identifier in the bib entry | arXiv API; OpenAlex API | Massive-STEPS: Massive Semantic Trajectories for Understanding POI Check-ins -- Dataset and Benchmarks \| arXiv preprint \| 2025 \| type posted-content |
| `xin2022domtl` | no identifier in the bib entry | arXiv API; OpenAlex API | Do Current Multi-Task Optimization Methods in Deep Learning Even Help? \| arXiv preprint \| 2022 \| type posted-content |
| `yang2022getnext` | DOI 10.1145/3477495.3531983 | Crossref REST; OpenAlex API | GETNext \| Proceedings of the 45th International ACM SIGIR Conference on Research and Development in Information Retrieval \| 2022 \| type proceedings-article |
| `ye2013nextmove` | DOI 10.1137/1.9781611972832.19 | Crossref REST; OpenAlex API | What's Your Next Move: User Activity Prediction in Location-based Social Networks \| Proceedings of the 2013 SIAM International Conference on Data Mining \| 2013 \| type  |
| `yu2020catdm` | DOI 10.1145/3366423.3380202 | Crossref REST; OpenAlex API | A Category-Aware Deep Model for Successive POI Recommendation on Sparse Check-in Data \| Proceedings of The Web Conference 2020 \| 2020 \| type proceedings-article |
| `yu2020pcgrad` | no identifier in the bib entry | arXiv API; OpenAlex API | Gradient Surgery for Multi-Task Learning \| arXiv preprint \| 2020 \| type posted-content |
| `zhu2022drrgnn` | DOI 10.1145/3529091 | Crossref REST; OpenAlex API | Predicting a Person’s Next Activity Region with a Dynamic Region-Relation-Aware Graph Neural Network \| ACM Transactions on Knowledge Discovery from Data \| 2022 \| type  |

## 5 · Errata regime for anything changed here

Chapter 5 is **under review**. Per the author's instruction of 2026-07-27, a correction here is
applied to the dissertation AND to the submitted source at `articles/[mobiwac]/src/` so the two
texts stay identical, then named in that article's own errata record rather than in Appendix B. All
three PARTIAL sites below were matched against the submitted source
(`articles/[mobiwac]/src/sections/01_introduction.tex` and `02_related.tex`) and are present there
verbatim, so any change is a two-file change.

## 6 · Two sites a naive check inverts

**`5_mobiwac.tex:96`, `silva2025mtlnet`.** An abstract-only check reports this as reversed: the CBIC
abstract says the model "shares lower-level embeddings and sequence encoders while maintaining
task-specific heads", while the chapter says "task-specific encoders feed shared layers". Both are
true of the same architecture, and the chapter's version is the one the CBIC **method section** of
record states: inputs "are first processed by separate, task-specific encoders", then FiLM
conditioning on a learnable task embedding, then shared residual layers, then task-specific heads,
with Nash-MTL aggregating gradients (`articles/CBIC___MTL/sections/method.tex`). **SUPPORTED.**

**`apx_b_errata.tex:220`** (in the appendices unit) is the same class of false positive in the other
direction: an errata row cites the source that contradicts the text being corrected. Recorded there.

## 7 · One correction to my own evidence handling

The eight `huang2023hgi` sites in this chapter and Chapters 2 and 4 were screened against an **empty**
evidence string: my text slice of the local PDF looked for a spaced `A B S T R A C T` header that this
paper does not use, so the field held one space. The screen correctly returned UNVERIFIABLE for all of
them and said the abstract text was missing. The manual pass then read the paper itself (12 pages,
ISPRS 196:134-145, in `science/articles/`) and closed all eight against its abstract and its section 3,
which is where the quoted passages in this report come from. The stored field now carries 1,674
characters read from the paper. Recorded because the trail matters even when the verdict does not change.

## 8 · What I could not confirm in this chapter

- `capanema2023poirgnn` and `wang2025hamtl` return no abstract at Crossref, OpenAlex or Semantic
  Scholar, and their Elsevier and Springer landing pages are outside the network allowlist. Both are
  used as identity-of-baseline or pattern-continuation pointers that the resolved record and title
  support; no mechanism claim rests on either.
- `:409`, `lin2021ctle`: the negative clause ("the category vocabulary never enters its training") is
  consistent with the abstract, which names only locations and temporal information as inputs, but an
  abstract cannot prove an absence. Narrow `[VERIFY]`.
- `:750`, `huang2024cslsl`: the cited internal comparison (the chain against a shared-trunk parallel
  variant on CSLSL's own benchmarks) is an ablation that the abstract does not carry. Narrow
  `[VERIFY]`; the sentence attributes it to the paper explicitly, so it needs a page.
- The comparative results claims at `:664-666` were **not** audited here. What a citation must
  support at those sites is the baseline's identity, which each record does. The comparison itself
  is a number claim under AGENT_GUARDRAILS section 2, whose single source of truth for this chapter
  is `RESULTS_BOARD.md`. That is a numbers audit, not this one, and I did not perform it.

---

## `11_claims_6_conclusion.md`

# 11_claims_6_conclusion.md — citation claim-support audit, Chapter 6, Conclusion

**Unit:** `src/chapters/6_conclusion.tex`  
**Run:** 2026-07-28, round 6, as the per-chapter pass the author asked for by name (COD-008 decision).  
**Errata regime for this unit:** frame chapter: author's own text.

## 1 · Counts (every citation in the unit, not a sample)

- `\cite` commands in the unit: **0**, on **0** source lines, carrying **0** key instances (a multi-key `\cite` counts once per key). Every one was audited.
- Distinct bibliography keys used: **0**.
- Verdicts: .

Comments were stripped before counting, so a key that appears only inside a `%` comment is not counted; every counted site renders.

This unit carries **no citations at all**. Verified by scanning the comment-stripped source for
`\cite`, `\citep`, `\citet`, `\textcite`, `\parencite` and `\onlinecite`: zero matches. The one
`cite` string in the file is inside a `%` comment. Nothing to audit.
## 3 · What I could not confirm

Nothing: the unit has no citations. The absence itself was measured, not assumed.

---

## `11_claims_appendices.md`

# 11_claims_appendices.md — citation claim-support audit, Appendices A to E

**Unit:** `src/chapters/apx_a..apx_e`  
**Run:** 2026-07-28, round 6, as the per-chapter pass the author asked for by name (COD-008 decision).  
**Errata regime for this unit:** author's own text; Appendix B is the errata register itself.

## 1 · Counts (every citation in the unit, not a sample)

- `\cite` commands in the unit: **7**, on **7** source lines, carrying **9** key instances (a multi-key `\cite` counts once per key). Every one was audited.
- Distinct bibliography keys used: **9**.
- Verdicts: **SUPPORTED** 9.

Comments were stripped before counting, so a key that appears only inside a `%` comment is not counted; every counted site renders.

## 2 · Every citation, with its verdict

Verdict scale: SUPPORTED, the citing sentence's attribution is present in or a fair paraphrase of the
source; PARTIAL, part is supported and part is not, or the sentence is stronger than the source;
NOT-SUPPORTED, the attribution is absent from or contradicted by the source; UNVERIFIABLE, the source
of record does not carry enough to decide and the attribution is not implausible.

| # | Site (file:line) | Key | Verdict | Evidence quoted from the source (under 20 words) |
|---|---|---|---|---|
| 1 | `apx_b_errata.tex:220` | `silva2025mtlnet` | SUPPORTED | "focusing on two complementary tasks: POI Category Classification and Next-POI Prediction" |
| 2 | `apx_d_ceiling.tex:55` | `kohavi1995crossval` | SUPPORTED | "the best method to use for model selection is ten-fold stratified cross validation" |
| 3 | `apx_d_ceiling.tex:55` | `pedregosa2011sklearn` | SUPPORTED | "Scikit-learn is a Python module integrating a wide range of state-of-the-art machine learning algorithms" |
| 4 | `apx_d_ceiling.tex:56` | `sokolova2009measures` | SUPPORTED | "the measure invariance taxonomy with respect to all relevant label distribution changes" |
| 5 | `apx_e_ethics.tex:36` | `cho2011gowalla` | SUPPORTED | "data from two online location-based social networks" |
| 6 | `apx_e_ethics.tex:36` | `jure2014snap` | SUPPORTED | "A collection of more than 50 large network datasets" |
| 7 | `apx_e_ethics.tex:40` | `wongso2025massivesteps` | SUPPORTED | "large-scale, publicly available benchmark dataset ... spans 15 geographically and culturally diverse cities" |
| 8 | `apx_e_ethics.tex:61` | `luca2021mobilitysurvey` | SUPPORTED | "deep learning ... human mobility" |
| 9 | `apx_e_ethics.tex:91` | `santos2024urban` | SUPPORTED | "it is fundamental to anonymize the locations with an appropriate method" |
## 3 · Failures and partials in this unit, in detail

None. Every citation in this unit is SUPPORTED.

## 4 · Source ledger for this unit

Every distinct key cited in this unit, the identifier it resolved by, and where I opened it this session.

| Key | Identifier | Opened at | Record as returned |
|---|---|---|---|
| `cho2011gowalla` | DOI 10.1145/2020408.2020579 | Crossref REST; OpenAlex API | Friendship and mobility \| Proceedings of the 17th ACM SIGKDD international conference on Knowledge discovery and data mining \| 2011 \| type proceedings-article |
| `jure2014snap` | no identifier in the bib entry | OpenAlex API | {SNAP Datasets}: {Stanford} Large Network Dataset Collection \| (no venue in record) \| 2014 \| type article |
| `kohavi1995crossval` | no identifier in the bib entry | OpenAlex API | A Study of Cross-Validation and Bootstrap for Accuracy Estimation and Model Selection \| (no venue in record) \| 1995 \| type article |
| `luca2021mobilitysurvey` | DOI 10.1145/3485125 | Crossref REST; OpenAlex API | A Survey on Deep Learning for Human Mobility \| ACM Computing Surveys \| 2021 \| type journal-article |
| `pedregosa2011sklearn` | no identifier in the bib entry | arXiv API; OpenAlex API; PDF in repo: Pedregosa2011_ScikitLearn.pdf | Scikit-learn: Machine Learning in Python \| Journal of Machine Learning Research (2011) \| 2012 \| type posted-content |
| `santos2024urban` | no identifier in the bib entry | NOT RESOLVED at any source of record | None \| (no venue in record) \| None \| type None |
| `silva2025mtlnet` | DOI 10.21528/CBIC2025-1191324 | Crossref REST; OpenAlex API | An Investigation into Multi-Task Learning for Point-of-Interest Category Classification and Next-POI Prediction \| Anais do XVII Congresso Brasileiro de Inteligência Comp |
| `sokolova2009measures` | DOI 10.1016/j.ipm.2009.03.002 | Crossref REST; OpenAlex API; PDF in repo: sokolova2009.pdf | A systematic analysis of performance measures for classification tasks \| Information Processing &amp; Management \| 2009 \| type journal-article |
| `wongso2025massivesteps` | no identifier in the bib entry | arXiv API; OpenAlex API | Massive-STEPS: Massive Semantic Trajectories for Understanding POI Check-ins -- Dataset and Benchmarks \| arXiv preprint \| 2025 \| type posted-content |

## 5 · The one site a naive check inverts

**`apx_b_errata.tex:220`, `silva2025mtlnet`.** A checker reading this sentence as the dissertation's
own claim about the CBIC work reports NOT-SUPPORTED, because the CBIC abstract says the work studied
"POI Category Classification and Next-POI Prediction" while the sentence says next-category and
next-region with negative transfer between them. That is the point of the row: it records that the
**submitted MobiWac manuscript** described the CBIC work that way, that the description was
inaccurate, and that it was corrected. The cited abstract is the evidence FOR the erratum. This is a
systematic false-positive class for errata registers and is recorded here so it is not re-raised.

## 6 · The one entry with no external source of record

**`santos2024urban`** resolves at no external source: no DOI, absent from Crossref, arXiv and
OpenAlex (title search returns unrelated works). It is a UFV master's dissertation. I verified it
against the document itself, which is in the repository at
`articles/dissertacao/exemples/germano/Dissertação_Mestrado___Germano.pdf`:

- Title page: "GERMANO BARCELOS DOS SANTOS", "URBAN REGION REPRESENTATION LEARNING: A POSITIONAL AND
  STRUCTURAL GRAPH APPROACH", Federal University of Viçosa, "Orientador: Fabrício Aguiar Silva",
  2024. Every bib field checks.
- Section 2.6, "Ethical Statement", states the location-privacy position and says which fields were
  left unmasked: the study "used Gowalla anonymized user identifier information, but we maintained
  the location without masking the latitude and longitude of a collected GPS point".
- Searched the full extracted text (244,987 characters) for "research ethics", "Comitê", "CEP",
  "CAAE", "institutional review" and "IRB": **zero occurrences of each**, which is the negative half
  of the citing sentence at `apx_e_ethics.tex:91`.

Every clause of that sentence checks, including the negative one. The entry should keep a bib comment
recording that it has no external identifier by nature, so a future existence-checker does not read
the absence as a defect.

## 7 · What I could not confirm in this unit

Nothing outstanding. All nine key instances are SUPPORTED.
