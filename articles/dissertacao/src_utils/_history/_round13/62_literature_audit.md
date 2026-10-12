# 62_literature_audit.md — the grounded-citation track: author items 7 (first half), 13, 27

**Track:** AUDIT, grounded-citation lane. **Written:** 2026-08-04.
**Author items covered:** §4 item 7 (first half only, the comparative-literature leg), item 13
(Contributions), item 27 (Pareto).
**Governing law obeyed:** `AGENT_GUARDRAILS.md` §1 R1/R2/R3/R5, §2 N1/N2/N3/N5, §3 C1/C2, §4b
V1/V2/V4/V13/V17. `WRITING_LAW.md` §3 (verbs bound to tests). `GLOSSARY.md` fail-closed registry.
**Nothing in this report edits any `.tex` file, and nothing was added to `references.bib`.**

## 0 · Tree state this was measured against (V1, and a correction to the briefing)

**The briefing's baseline is stale, and this is the first finding.** It said `HEAD=82080ce4`. Measured:

```
cd /Users/vitor/Desktop/mestrado/ingred
git log --oneline -1
  -> aa75a05b docs(tracker): §5 removed from PENDENCIAS after re-verification, archived with its closing state
git merge-base --is-ancestor 82080ce4 HEAD && git log --oneline 82080ce4..HEAD
  -> YES; one commit ahead: aa75a05b
```

**I measured every source claim below against the WORKING TREE** (uncommitted `1_introduction.tex`,
`2_fundamentals.tex`, `GLOSSARY.md`, `6_conclusion.tex`, `apx_f_cosine.tex`), not against any build.

**The second briefing premise is also no longer true.** It said `src/build/main.pdf` (mtime
2026-08-03 20:19:18) is stale for chapter 2 by 14 minutes. Measured:

```
stat -f '%Sm' -t '%Y-%m-%d %H:%M:%S' articles/dissertacao/src/chapters/2_fundamentals.tex
  -> 2026-08-03 21:03:40
stat -f '%Sm' -t '%Y-%m-%d %H:%M:%S' articles/dissertacao/src/build/main.pdf
  -> 2026-08-03 21:13:26
```

The PDF now POSTDATES the chapter-2 source by about ten minutes. That is a statement about mtimes
only: I did not open the PDF and I do not claim its chapter 2 matches the source. **No claim in this
report rests on the PDF.**

---

## 1 · SOURCE LEDGER

One row per reference touched. Columns: identifier -> where I opened it THIS SESSION -> the specific
claim -> whether the claim was LOCATED in the source text. A row is admissible for prose only when
all three of `AGENT_GUARDRAILS` §1 R1(a)(b)(c) hold. **Attributes are copied from Crossref (the source
of record), never retyped from another bibliography** (R2).

### 1.1 · Sources opened and LOCATED (admissible)

| # | Work / key | Identifier | Where opened THIS session | Claim it supports | LOCATED? |
|---|---|---|---|---|---|
| L1 | Wang, Chen, Liu, Zhang, Wu, Cui, Hu — *Hierarchy aware-based multi-task learning for user location prediction* (`wang2025hamtl`) | DOI 10.1007/s11227-025-07643-7 | **The PDF already in this repository**, `articles/dissertacao/science/articles/wang2025hamtl.pdf` (1,865,663 bytes, 28 pages, 67,091 chars extracted). Attributes cross-checked at Crossref `api.crossref.org/works/10.1007/s11227-025-07643-7` this session. | HAMTL's location target is the exact place, its category head is the AUXILIARY task, and it names **no region-like spatial unit anywhere**. | **YES** — p2: *"Our framework consists of two tasks: location prediction as the main task and category prediction as the auxiliary task."* p3 (contributions bullet): *"which employs category prediction as an auxiliary task to enhance the primary task of location prediction."* p14: *"It first predicts the category for the next destination (e.g., restaurant). This category prediction inherently restricts the potential search space for the subsequent fine-grained location prediction."* |
| L2 | same, HAMTL — the ABSENCE half | as above | same PDF | HAMTL names no region/grid/district/coarse spatial unit, and reports **no category metric**. | **YES, and measured** (see §2.3 for the commands and the instrument validation). `region` -> 1 occurrence, in a 1970 Tobler reference title on p27. `grid` -> 0. `district` -> 0. `coarse` -> 0. Metrics, p18: *"we implemented two evaluation metrics: top-k accuracy (Acc@k) and mean reciprocal rank (MRR). Acc@k determines how often the actual next **location** appears within the top-k predictions."* Loss, p15: *"two multiclassification tasks: predicting locations and their categories. We use cross-entropy as the loss function for both tasks, assigning equal weight to each."* |
| L3 | Luca, Barlacchi, Lepri, Pappalardo — *A Survey on Deep Learning for Human Mobility* (`luca2021mobilitysurvey`, already cited) | DOI 10.1145/3485125; ACM Comput. Surv. 55(1):1-44, issued 2021-11-23 (Crossref) | `fetch_article_fulltext` -> Unpaywall green OA PDF (arXiv 2012.02825 route), 42 pages, opened and searched this session | The survey's taxonomy of mobility tasks **contains no next-category and no next-region task**, and it explicitly EXCLUDES semantic enrichment from scope. | **YES** — p2: *"we focus on DL solutions to predict or generate human movements and exclude other approaches solving other problems, such as semantic enrichment of mobility data (e.g., predicting the purpose of movement)... we discuss two predictive tasks, namely next-location prediction and crowd flow prediction, and two generative tasks, namely trajectory generation and flow generation."* Fig. 1 caption p3: *"A taxonomy of the mobility tasks we discuss in this survey."* |
| L4 | Zhu, Cao, Lu, Liu, Liu, Li, Luo, Xiong — *Predicting a Person's Next Activity Region with a Dynamic Region-Relation-Aware Graph Neural Network* (`zhu2022drrgnn`, already cited) | DOI 10.1145/3529091; ACM TKDD 16(6):1-23, issued 2022-07-30 (Crossref, 8 authors) | OpenAlex `works/doi:10.1145/3529091` abstract, this session. Full text NOT opened (`oa_status=closed`; doi_resolve 403). | Next activity region IS an end target in one published system, jointly with a mobility-intention label — the strongest near-miss to the priority claim. | **YES, in the abstract** — *"we aim at developing models that can answer three questions: (1) Which regions are the ARs? (2) Which region will be the next AR, and (3) Why do people make this regional mobility?"* and *"significantly improve accuracy for both the next AR prediction and mobility intention prediction."* **Regions are discovered per person** — *"we first propose a method to find out people's ARs"* — which is what keeps it distinct from a fixed citywide partition. |
| L5 | Tang, He, Zhao — *Activity-Aware Human Mobility Prediction With Hierarchical Graph Attention Recurrent Network* (Hgarn) | DOI 10.1109/tits.2024.3513695; IEEE T-ITS 26(2):1604-1616 | OpenAlex abstract, this session | A 2024 system that jointly predicts next activity and next location, with **activity explicitly auxiliary** — a near-miss NOT currently cited anywhere in `src/references.bib`. | **YES, in the abstract** — *"a Temporal Module, which employs recurrent structures to jointly predict users' next activities and their associated locations, with the former used as an auxiliary task to enhance the latter prediction."* |
| L6 | Liu, Song, Xu, Rafique, Zhang, Shen, Khosravi, Qi — *Bidirectional GRU networks-based next POI category prediction for healthcare* (ABG_poic) | DOI 10.1002/int.22710; Int. J. Intell. Syst. 37(7):4020-4040, issued 2021-10-11 (Crossref, 8 authors) | OpenAlex abstract, this session | Next-POI-**category** is an end target in its own right in published work, argued as more informative than the POI itself. | **YES, in the abstract** — *"we propose an attention-based bidirectional gated recurrent unit (GRU) model for POI category prediction (ABG_poic). We regard the user's POI category as the user's interest preference because the fuzzy POI category is easier to reflect the user's interest than the POI."* |
| L7 | Liu, Pei, Wang, Yang, Zhang, Wang, Dai, Qi, Ma — *An attention-based category-aware GRU model for the next POI recommendation* (ATCA-GRU) | DOI 10.1002/int.22412; Int. J. Intell. Syst. 36(7):3174-3189, issued 2021-03-25 (Crossref, 9 authors) | OpenAlex abstract, this session | Same lineage: an end-target next-POI-category model. | **YES, in the abstract** — *"we develop an attention-based category-aware GRU (ATCA-GRU) model for the next POI category recommendation."* |
| L8 | Capanema, de Oliveira, Silva, Silva, Loureiro — *Combining recurrent and Graph Neural Networks to predict the next place's category* (`capanema2023poirgnn`, already cited, Ch.5 baseline) | DOI 10.1016/j.adhoc.2022.103016; Ad Hoc Networks 138:103016, issued 2023-01 (Crossref) | Crossref record this session; **abstract NOT available in OpenAlex** (empty) and full text not opened. | Next-place-**category** as an end target, in the advisor's own group. | **TITLE ONLY.** Admissible for existence and for the target named in its title; NOT admissible for any characterization beyond the title. |

### 1.2 · Sources opened, claim NOT located (inadmissible for that claim)

| # | Work | Identifier | Where opened | Claim sought | Status |
|---|---|---|---|---|---|
| N1 | Chekol & Fufa — *A survey on next location prediction techniques, applications, and challenges* | DOI 10.1186/s13638-022-02114-6 | OpenAlex abstract, this session | a survey that RANKS or COUNTS task popularity, so item 7's comparative claim could be anchored | **NOT LOCATED.** The abstract describes an extensive review of next-location approaches; it makes no comparative statement about the standing of next-category or next-region versus static POI classification. Full text not opened. |
| N2 | Sánchez & Bellogín — *POI Recommender Systems Based on LBSNs: A Survey from an Experimental Perspective* | DOI 10.1145/3510409 | OpenAlex abstract, this session | same | **NOT LOCATED.** Abstract is about algorithms, information sources and reproducibility; no task-popularity ranking. Full text not opened. |
| N3 | Chen, Zhu, Xu, Liu, Yu, Yin — *Embedding Hierarchical Structures for Venue Category Representation* | DOI 10.1145/3478285 | OpenAlex abstract, this session | evidence that static POI-category work is treated as representation/enrichment rather than an end target | **NOT LOCATED as a comparative claim.** The abstract is about a category embedding model; it does not rank tasks. |
| N4 | Senefonte, Silva, Lüders, Delgado — *Classifying Venue Categories of Unlabeled Check-ins Using Mobility Patterns* | DOI 10.1109/dcoss.2019.00105 | OpenAlex abstract, this session | same | **NOT LOCATED as a comparative claim.** It is a static category-classification paper; it does not compare the standing of the tasks. |

### 1.3 · Sources NOT opened (named so the absence is on the record)

- `zhu2022drrgnn` full text: closed access, `doi_resolve` 403. Only the abstract is admissible.
- Any Springer-gated text beyond the HAMTL PDF already in the repository. The configured Springer key
  was NOT re-tested this session; it did not need to be, because the PDF was already on disk.

---

## 2 · ITEM 7 (first half) — is the comparative literature claim supportable?

### 2.1 · The live sentence and the author's proposal

Live prose, `src/chapters/1_introduction.tex` (working tree, uncommitted), in §1.2 *Research question*:

> "Under a check-in level representation, static category classification is a less natural companion
> task than a second sequential target, so the final task pair becomes next category and next region."

The author says the reason is thin and proposes a second, stronger one: in the literature, next
category and next region carry more weight than POI classification.

### 2.2 · Verdict: the comparative form is NOT supportable from an opened source. **Take the sanctioned fallback.**

`NORTH_STAR` §6 Ch.1 beat 4(b) already anticipates this: leg 2's *"comparative form stays [VERIFY]
until an opened anchor supports it"*, with the fallback *"both are established end targets, and next
region feeds a broader family of downstream problems."* **This audit closes that [VERIFY] in the
negative.** No source I opened states, in any form, that next-category or next-region prediction is
more established, more studied, or carries more weight than static POI category classification.

What I DID establish, per item, with the evidence beside it:

**(a) Both of the author's two tasks ARE established end targets in published work — separately.**
This half of the fallback wording is now backed by opened sources.
- Next category as an end target: L6 (ABG_poic, *"a model for POI category prediction... the fuzzy POI
  category is easier to reflect the user's interest than the POI"*), L7 (ATCA-GRU, *"the next POI
  category recommendation"*), and L8 by title (`capanema2023poirgnn`, already cited).
- Next region as an end target: L4 (DRRGNN, *"Which region will be the next AR"*), already cited at
  `5_mobiwac/02_related.tex:91`.

**(b) There is NO opened source that ranks the tasks against each other.** Four candidate surveys were
opened at abstract level (N1-N4) and none makes a comparative statement. The one survey I opened in
FULL TEXT (L3, Luca et al., 42-page PDF) is evidence in the *opposite* direction of a simple ranking:
its taxonomy contains **neither** of the author's two tasks. Its four tasks are next-location
prediction, crowd flow prediction, trajectory generation and flow generation, and it explicitly puts
semantic work outside scope (*"exclude other approaches solving other problems, such as semantic
enrichment of mobility data (e.g., predicting the purpose of movement)"*, p2). A survey that excludes
the semantic axis cannot be cited to say the semantic axis outranks anything.

**(c) A counting argument is available but it is WEAK EVIDENCE and I do not recommend citing it.**
OpenAlex title-and-abstract counts, run this session:

| query (OpenAlex `title_and_abstract.search`) | count |
|---|---:|
| `"next POI recommendation" OR "next location prediction" OR "next POI prediction"` | 676 |
| `("POI category" OR "venue category" OR "place category") AND (classification OR annotation OR inference OR labeling)` | 128 |
| `"next POI category" OR "next place category" OR "next category prediction" OR "next activity type"` | 16 |
| `"next region prediction" OR "next activity region" OR ("region prediction" AND "check-in")` | 14 |

These counts point the **opposite way from the author's premise**: static POI-category work
(128) is roughly four times as large a literature as next-category (16) and next-region (14) combined.
A keyword count is a measurement of a query, not of a field (V17: the phrasing bounds what it can
find), so I would not put it in prose in either direction — but it is enough to say the comparative
claim is not merely unsupported, it may be **backwards**.

**Sycophancy check (AGENT_GUARDRAILS §7).** The author's premise as written — that these two tasks
"possuem mais forças que a classificação de poi" in the literature — is not supported, and one
reading of the evidence contradicts it. I am reporting that rather than finding a way to agree.

### 2.3 · What IS defensible, and the exact wording

The genuinely supportable comparative statement is narrower and sharper, and the repository already
knows it: the mainstream treats category and region as **auxiliary to next place**, not as competitors
of static classification. That is documented in `docs/baselines/RELATED_WORK_TRIAGE.md` §4 over 14
primary sources, and it is confirmed independently by two sources I opened this session:
HAMTL (L1/L2, *"category prediction as the auxiliary task"*) and Hgarn (L5, *"the former used as an
auxiliary task to enhance the latter"*).

**Recommended replacement for leg 2 — the fallback, unchanged from NORTH_STAR:**

> both are established end targets, and next region feeds a broader family of downstream problems

If the author wants the *literature* framing he asked for, the defensible version is not comparative
between his tasks and POI classification, it is about the auxiliary/end-target axis:

> where prior joint models treat category and region as auxiliary signals for an exact-place target,
> this study takes both as end targets

That sentence is supportable today from L1, L4, L5, and the already-cited `Lim2022`/`sun2024mcmg`.
**It is not the sentence the author asked for.** His comparative form must be dropped or flagged.

### 2.4 · Second half of item 7, out of my scope but flagged

Item 7 also raises category leakage from the check-in-level embedding into the next-category target.
That is a different track and I did not audit it. It is not vacuous: `5_mobiwac/05_setup.tex:70`
already describes a screening audit built for exactly this channel. **Whoever takes it should start
there, not from scratch.**

### 2.5 · The measurement commands (V1), and the instrument validations (V13/V17)

All OpenAlex calls used `api.openalex.org` with the stored API key, from the Python kernel this
session. Every count above is reproducible with:

```python
# from the python tool, key from OPENALEX_API_KEY
oa("works", filter=f"title_and_abstract.search:{QUERY}", per_page=1)["meta"]["count"]
```

**The boolean instrument was validated in both directions before any zero was believed** (V13: a parse
returning zero is a broken instrument until proven otherwise):

| validation | expected | got |
|---|---|---|
| `"hierarchical multi-task graph recurrent"` (a paper known present) | ≥1 | **2**, incl. `Lim2022` |
| `("activity region" AND "graph")` (DRRGNN known present) | ≥1 | **2**, incl. DRRGNN |
| `("multi-task" AND "POI")` | large | **89** |
| `"activity region"` alone (proves the phrase is indexable) | large | **568** |

Only after those did I treat these zeros as absences: `("next category" AND "next region")` -> **0**;
`("activity region" AND "multi-task")` -> **0**; `("multi-task" AND "next location" AND (region OR
area OR grid))` -> **0**; `(category AND region AND multi-task AND ("end target" OR "co-equal" OR
"equal standing"))` -> **0**.

The HAMTL PDF greps were validated the same way before their zeros were used:

```
# python, pypdfium2 text extraction over all 28 pages of
# articles/dissertacao/science/articles/wang2025hamtl.pdf
'multi-task' -> 14 hits   'location' -> 145   'category' -> 64      # instrument sees the text
'region' -> 1 (a 1970 reference title, p27)   'grid' -> 0   'district' -> 0   'coarse' -> 0
```

**Exclusions declared (V2):** no `continue`, `skip`, or filter dropped any record in the counts above.
Two OpenAlex `search=` calls returned HTTP 504 and were not retried; both were superseded by the
`title_and_abstract.search` probes, which are the ones reported. Nothing else was excluded.

---

## 3 · ITEM 13 — the Contributions section and the author's four candidates

### 3.1 · The live section, measured

`src/chapters/1_introduction.tex:294-331` (working tree). Four `\item[...]` groups: **Theoretical**,
**Software**, **Empirical**, **Practical** — which matches the `NORTH_STAR` §6 Ch.1 beat-8 taxonomy
exactly, so the SHAPE is correct and only the CONTENT is at issue.

### 3.2 · (a) Check2HGI as a reusable check-in-level representation — **SUPPORTABLE, and currently understated**

The live Software bullet names Check2HGI, but only as a delivered artifact alongside MTLnet. The
author's point is that the *level of the representation* is the advance and that it is reusable. That
claim is inside the whitelist: `articles/[mobiwac]/PAPER_PLAN.md` §3 CAN-say carries the measured
margin over the place-level embedding (+29.31 / +27.63 / +39.62 / +37.95 / +37.47 macro-F1 at
AL/AZ/FL/CA/TX, paired Wilcoxon p = 0.031, 5/5 folds each) and the caveat that on next-region the two
representations are within about 1.6 to 3.1 points with HGI slightly ahead. **A contributions sentence
must carry that second half**, or it overstates the representation as a general win when it is
measured as category-specific.

The word "reusable" is a forward-looking claim about future work, not a measured result. It is fine in
a Contributions section **if it is stated as availability, not as demonstrated transfer** — nothing in
this document tests Check2HGI on a task outside these two.

**Disposition: YOU_APPLY**, with the region caveat mandatory in the same sentence.

### 3.3 · (b) The joint model as modular / extensible — **PARTLY SUPPORTABLE, weakest of the four**

"Can be used for joint training of the tasks" is simply what Chapter 5 demonstrates and is already in
the Practical bullet. "Can be extended to other tasks given its modularity" is **not measured
anywhere**. The document's own boundary statement points the other way: Appendix F
(`apx_f_cosine.tex`, §`apx:cosine:extension`) states that every run measured uses one architecture
family and that *"Nothing here says the gradients stay orthogonal in a model that shares more of its
depth, couples the tasks in a cascade, or shares an output layer."*

An extensibility claim in Chapter 1 that the appendix disclaims in Chapter D is a claims-evidence
mismatch a banca member finds in one pass. **Either drop the extensibility clause or write it as a
design property with no performance implication** (the model has per-task streams and a shared trunk,
so a third stream is architecturally admissible — not that it would help).

**Disposition: I_DECIDE.** The honest version is thin enough that the author should choose whether it
is worth a line.

### 3.4 · (c) "The tasks appear not to be conflicting" — **the author's own caution is correct, and it is the harder of the two dangerous items**

He wrote "(Esse tem que tomar bastante cuidado)". He is right, and here is exactly what the evidence
licenses.

**What the two measurements are** (they are different runs and must never be merged):

| | Ch.5 related-work measurement | Appendix F (prints as Appendix D) |
|---|---|---|
| source | `5_mobiwac/02_related.tex:163-174` | `apx_f_cosine.tex` |
| when | during development, on an **earlier data preparation** | on the shipped preparation |
| coverage | four Gowalla states (AL, AZ, FL + **Georgia**, which is not one of the six) | **seven** datasets: the six of Ch.5 plus Georgia |
| unit | four seeds | 5 folds × 50 epochs, ONE random initialization per dataset |
| headline | pooled cosine **+0.001**, largest per-dataset mean **+0.0032** | 4,650 epoch-level cosines; every dataset equivalent to zero |

**What Appendix F licenses (this is stronger than the author's phrasing):** not "no conflict was
detected" but a positive equivalence statement. Its own prose: *"An equivalence test supports the
positive claim instead: the mean alignment lies inside a margin fixed in advance, so whatever
alignment is there is too small to matter."* The margin is ±0.05, two one-sided tests, `lakens2017tost`.
The unit of independence is the **fold**, and the appendix says so: *"The unit of independence is the
fold, and every test below runs on folds."*

**What it does NOT license, and every one of these is a trap the appendix itself flags:**
1. **Not "the tasks are not conflicting" as a general property.** Seven datasets, ONE architecture
   family. The appendix draws that boundary explicitly.
2. **Not a carry-back to Chapters 3 and 4.** Different task pair (static category classification +
   next category) and different architecture (hard parameter sharing). The appendix cut a paragraph
   for exactly this reason at the author's own instruction.
3. **Nothing may be called "significant".** At five folds the exact sign test floors at 0.0625; the
   appendix's standing instruction is *"Never write 'significantly positive' here."*
4. **Not "the tasks share nothing".** Appendix F: *"Orthogonal gradients also do not mean that the
   tasks share no knowledge: the two streams still exchange information through the cross-attention
   trunk, a sharing mechanism this measurement does not read."*
5. **Not from the +0.001 alone.** `GER-11` (the advisor, via the author's paraphrase) is right that a
   single mean over four seeds cannot distinguish consistent orthogonality from large conflicts that
   cancel. **Appendix F is what answers GER-11** — it has per-fold spread, confidence intervals and an
   equivalence test where the +0.001 had none. A contributions bullet must be founded on the appendix,
   never on the +0.001.

**The defensible wording, bounded:**

> On this task pair and this architecture, the two tasks' gradients on the shared trunk are
> statistically equivalent to zero (TOST, ±0.05 margin) at every dataset measured, so a gradient
> balancer has no conflict to resolve.

**GLOSSARY compliance:** `gradient conflict` is registered (§4) and its row already bans the phrasing
the author reached for — *"Never call a near-zero cosine 'no conflict detected' where the appendix's
equivalence test supports the positive statement."* The author's own sentence, "as tarefas parecem não
serem conflitantes", is the banned weaker form. **Registered terms exist for this bullet; the wording
he proposed is the one the registry rules out.**

**Disposition: I_DECIDE.** The claim is real and it is Appendix-F-grade, but only in the bounded form,
and the author must choose whether a bullet this hedged earns a place in Chapter 1.

### 3.5 · (d) THE PRIORITY CLAIM — "our papers are pioneering in using MTL for these two tasks"

This is the sentence the task named as the most dangerous in the audit. I ran a search designed to
**refute** it, not to support it (V13: a claim whose function is to justify what you want to say is
the one to check hardest).

**What is already in the document.** The live prose is already narrower than the author's phrasing,
in two places, and both were probed:

- `2_fundamentals.tex` (live prose, comments stripped): *"Among the works reviewed here, none treats
  next category and next region as co-equal end targets of one joint model."* — scoped to the works
  reviewed. Probe `R10-novelty`.
- `5_mobiwac/02_related.tex:87-89`: *"To our knowledge, fine-grained region as an end target of equal
  standing, rather than an auxiliary coarse grid cell, is underexplored."* — "underexplored", not
  "first". Probe present via `R10-hamtl` on the neighbouring HAMTL description.
- `5_mobiwac/01_introduction.tex:36` is the strongest live form: *"to our knowledge, the first work to
  treat fine-grained region as an end target of equal standing"*. **This is in a chapter under review
  and I did not touch it.**

**The refutation sweep.** Eight boolean probes over OpenAlex title-and-abstract, plus five keyword
searches, plus direct record pulls on every candidate. Instrument validated first (§2.5). Results:

| probe | count | anything that refutes? |
|---|---:|---|
| `("next category" AND "next region")` | 0 | no |
| `("multi-task" AND category AND region AND ("check-in" OR POI))` | 4 | no — POI recommenders and two theses |
| `("region prediction" AND "multi-task")` | 7 | no — none in mobility (antibody LM, remote sensing, traffic demand) |
| `("activity region" AND "multi-task")` | 0 | no |
| `("multi-task" AND "next location" AND (region OR area OR grid))` | 0 | no |
| `("multi-task" AND geohash)` | 1 | no — spatial crowdsourcing allocation |
| `("semantic" AND "spatial" AND "multi-task" AND "next location")` | 1 | `wang2024iemtlf`, already cited |
| `(category AND region AND multi-task AND ("end target" OR "co-equal" OR "equal standing"))` | 0 | no |

**Every near-miss found, with its identifier and why it does not refute:**

| near-miss | identifier | why it does not refute |
|---|---|---|
| **HAMTL** | 10.1007/s11227-025-07643-7 | **PDF opened this session.** Location is the main task, category is auxiliary and named as such twice; the location target is the exact place; the word "region" appears once, in a 1970 reference title. No region-like unit, and no category metric reported. **The blocker on FAB-28 is now cleared by direct reading, not by the bibliography's recorded note.** |
| **DRRGNN** | 10.1145/3529091 | Next activity region IS an end target, jointly with mobility intention. **But** the regions are *discovered per person* (*"we first propose a method to find out people's ARs"*), not a fixed citywide administrative partition, and the co-target is an intention label, not a category. Already cited at `02_related.tex:91` with exactly this distinction. **This is the closest published work and it is correctly positioned.** |
| **Hgarn** | 10.1109/tits.2024.3513695 | Jointly predicts next activity and next location, *"the former used as an auxiliary task to enhance the latter"* — the auxiliary pattern again, and the spatial target is a location, not a region. **NOT currently in `references.bib`** (checked against all 100 entries). |
| **HMT-GRN** | 10.1145/3477495.3531989 (+ journal ext. 10.1145/3610584) | Multi-task over region granularities, but *"predict the next POI"* is the goal and regions serve a beam search. Already cited (`Lim2022`). |
| **MCMG** | 10.1145/3592789 | Region and category are *channels* densifying a next-POI objective. Already cited (`sun2024mcmg`). |
| **CSLSL** | 10.1140/epjds/s13688-024-00460-7 | Cascade when->what->where, location primary. Already cited. |
| **MCARNN** | 10.24963/ijcai.2018/477 | Jointly predicts activity and location; spatial target is a location. Already cited (`Liao2018`). |
| **DPMTM** | 10.1145/3625234 | Multi-task over next check-in time, POI, and POI functional semantics — POI identity is in the target set. Not a region task. Not cited. |
| **MSAN** | 10.3390/ijgi12070297 | Visiting-intention prediction as *"the auxiliary task of the next POI recommendation task"*. Not cited. |
| **IntTravel** | arXiv 2602.11664 (2026) | Multi-task travel recommendation (when/how/where/what); "where" is a POI. Not a region task. Not cited. |
| **ABG_poic / ATCA-GRU** | 10.1002/int.22710 / 10.1002/int.22412 | Next-POI-category as an end target — but **single-task**, no region, no MTL pairing. They weaken "pioneering in these tasks"; they do not touch the *pair* claim. |

**Verdict on (d): the author's phrasing must be dropped; the claim survives only in the narrowed form
already in the text.** "Pioneiros na utilização de MTL para essas duas tarefas" is refutable on its
face — MTL involving a category target is a populated literature (L1, L5, `Liao2018`, `Zhang2020`,
`Halder2021/2022`, `Xu2023`, `huang2024cslsl`, `Lim2022`, `sun2024mcmg`), and next-category as a
standalone target predates this work (L6, L7, L8). What no source I found does is treat **next
category and next region as co-equal end targets of one joint model with no next-place target**.

**The exact narrowest defensible wording** (and it is already the text's own):

> Among the works reviewed here, none treats next category and next region as co-equal end targets of
> one joint model.

If the author wants a Contributions bullet, that sentence with "to our knowledge" is the ceiling:

> To our knowledge, no prior joint model treats next category and next region as co-equal end targets,
> without an exact-place target behind them.

**Do not write "pioneering", "the first", or "unprecedented" in Chapter 1.** The strongest live form
("the first work to treat fine-grained region as an end target of equal standing") lives in Chapter 5,
which is a submitted manuscript; the frame should not exceed it.

**Disposition: I_DECIDE**, because the wording is a claim under §3 C2 and only the author can approve
it — but the recommendation is unambiguous: narrow it or drop it.

### 3.6 · What is MISSING from Contributions that the work actually earned

Measured against the live block (`1_introduction.tex:294-331`) and `NORTH_STAR` §6 beat 8:

**1. Chapter 4 is absent from the section entirely.** Measured (V1):

```
cd articles/dissertacao/src/chapters
awk '!/^[[:space:]]*%/{print FNR": "$0}' 1_introduction.tex | awk '/section\{Contributions\}/,0' \
  | grep -cE 'ch:cbic'            -> 2
  ... | grep -cE 'ch:courb|ST-MTLNet|courb'  -> 0
```

Chapter 3 is referenced twice, Chapter 5 twice, **Chapter 4 zero times**. Yet the diagnosis that the
representation is the bottleneck is the arc's hinge, the Theoretical bullet asserts exactly that
finding, and `ST-MTLNet` is a registered artifact in `GLOSSARY.md` §2. The Software bullet lists
MTLnet and Check2HGI and omits ST-MTLNet. **This is the single largest gap and it is mechanical.**

**2. The balancer screen is not claimed anywhere in Contributions.** `5_mobiwac/02_related.tex:118-124`
reports nineteen loss and gradient balancers screened at default configurations, one seed, two
datasets (Alabama and Florida), with none improving on tuned fixed weighting across both tasks and
both datasets. That is a real empirical contribution with a stated scope. Its bounded form belongs in
the Empirical bullet, **with its scope attached** (default configurations, single seed, two datasets)
— an unscoped version would overclaim badly.

**3. The gradient-orthogonality measurement is not claimed.** Item 13(c). Appendix F over seven
datasets is a Theoretical/Empirical contribution and appears in no bullet.

**4. The region-native baseline adaptations are not claimed.** `5_mobiwac/05_setup.tex:154` describes
HMT-GRN adapted to a region-native form and STAN re-implemented with a region output layer, both on
our folds. Building comparable baselines for a task the field does not evaluate is Software+Empirical
work, and Chapter 5 leans on it.

**5. The Empirical bullet omits the external-baseline result.** It names the joint-vs-dedicated
comparison and the protocol but not `08_conclusion.tex:14`'s measured margins over the external
references (at least 4 Acc@10 points over the strongest region reference; at least 33 macro-F1 points
over POI-RGNN).

**What I checked and found NOT missing:** the taxonomy itself (all four beat-8 groups present); the
n=20 arithmetic and its fixed-partition caveat (present and correct, matching the `GLOSSARY` §4 row);
the region verdict partition (present, four of six plus TOST at the other two, matching
`PAPER_PLAN.md` §3 and `JOINT_BEST_RESULTS.md`).

---

## 4 · ITEM 27 — is any Pareto-flavored property empirically supported?

### 4.1 · What the document currently says, and it is not silent

`GLOSSARY.md` §4 registers **Pareto dominance**, **Pareto optimality** and **Pareto-stationary point**,
and states that Pareto optimality is not claimed. `2_fundamentals.tex` carries all three in live prose
plus the disclaimer, guarded by four probes (`R9-pareto`, `R9-pareto2`, `R9-pareto3`, and `R9-conflict`
for the neighbouring definition). Live prose:

> "This dissertation therefore claims no Pareto property for its models. It judges each task against
> its dedicated single-task model under the tests defined in Section~\ref{sec:fund:eval}."

The registered definition of dominance, quoted from `2_fundamentals.tex` live prose:

> "One parameter setting exhibits Pareto dominance over another when it is no worse on every task loss
> and better on at least one."

### 4.2 · (a) The per-dataset evidence, QUOTED from the source of record (N2: quote, never compute)

From `articles/[mobiwac]/PAPER_PLAN.md` §3 (the claim whitelist) and
`docs/studies/closing_data/joint_best/JOINT_BEST_RESULTS.md` (the joint-best lane the paper reports).
Convention: joint-best, one saved model per fold, n=20 = 4 seeds × 5 folds, inferential unit n=4.

| dataset | Δcategory (macro-F1, pp) | category verdict | Δregion (Acc@10, pp) | region verdict |
|---|---:|---|---:|---|
| Istanbul | +8.58 | beats | **+0.19** (90% CI +0.15..+0.23, 20/20 folds) | beats |
| AL | +7.69 | beats | **−0.41** (90% CI −0.63..−0.20) | **matches (TOST, δ=2 pp)** |
| AZ | +9.35 | beats | **−0.00** (90% CI −0.08..+0.07) | **matches (TOST, δ=2 pp)** |
| FL | +5.33 | beats | +0.71 (CI +0.67..+0.76) | beats |
| TX | +7.45 | beats | +2.11 (CI +2.10..+2.13) | beats |
| CA | +6.45 | beats | +2.20 (CI +2.19..+2.21) | beats |

Category superiority family: per-cell Holm m=6, all reject, worst adjusted p = 1.0e-06.

### 4.3 · (b) The answer: **a bounded dominance statement holds at FOUR datasets and is BLOCKED at two**

Apply the document's own registered definition — no worse on every task, better on at least one:

- **Istanbul, FL, TX, CA: the joint model Pareto-dominates the pair of dedicated models on the two
  reported metrics.** Both deltas are positive and both carry a superiority test. This is not a
  reinterpretation of the numbers; it is the definition read against them.
- **AL and AZ: dominance is BLOCKED, and this is the honest answer to item 27.** AL region is −0.41 and
  AZ region is −0.00. Both are non-inferior by TOST within two points, and non-inferiority is **not**
  "no worse". `WRITING_LAW` §3 forbids upgrading a TOST match to a win, and `PAPER_PLAN.md` §3 puts it
  on the must-NOT-say list by name: *"beats region everywhere" or "Pareto-dominates everywhere"*. AZ is
  additionally called out — *"NEVER upgrade AZ (its CI straddles zero)"*.

**So a global dominance claim is refuted by the document's own source of record.** A per-dataset one is
supported at four of six.

**Two further reasons the framing needs care even where it holds.** First, Pareto dominance is defined
in the multi-objective literature (`liu2021cagrad` Def. 3.1, `sener2018mgda` Def. 1(a)) over **task
losses at parameter settings of one model**; here it would be applied to **two evaluation metrics of
one model versus two separately trained models**. Same logical shape, different objects. Second,
dominance over the dedicated models says nothing about Pareto **optimality** — nothing here is a claim
about a front, and the fundamentals chapter's disclaimer must survive intact whatever is decided.

### 4.4 · The exact bounded wording, if the author wants the claim

Two options, both defensible; neither may go in without the disclaimer in §2.3 staying put.

**Option A — per-dataset, the strongest honest form:**

> At four of the six datasets the joint model is better than the dedicated single-task models on both
> tasks at once. At the other two it is better on category and statistically non-inferior on region
> within a two-point margin (TOST), so no dominance claim is made there.

**Option B — name the concept, in Appendix F, which is where the author suggested it could live:**

> Where the joint model improves both tasks at once, at Istanbul, Florida, Texas and California, the
> outcome has the shape of Pareto dominance over the pair of dedicated models. At Alabama and Arizona
> the region result is non-inferior rather than better, so the relation does not hold and none is
> claimed. Nothing here is a claim of Pareto optimality.

**My recommendation is Option A without the word "Pareto".** It says the same thing, needs no
multi-objective vocabulary in a results context, and cannot be misread as a front claim. Option B is
admissible if the author wants the vocabulary explicitly connected — and note **Appendix F is the wrong
home** for it: that appendix measures gradient cosines, not task outcomes, and its own text warns that
its ±0.05 margin *"measures a different quantity on a different scale"* from Chapter 5's two-point
margin. If the claim lands anywhere, it lands in Chapter 6.

### 4.5 · (c) Is this the same decision as AUT-01?

**No. They are distinct, and item 27 is the newer and narrower one.**

- **AUT-01** asks whether the MTL *fundamentals* need a Pareto treatment at all. Its own block records
  it as largely SATISFIED by a concurrent edit: `2_fundamentals.tex` now has the total-loss equation,
  the dominance and optimality definitions, the Pareto-stationary distinction, the per-method guarantee
  levels, and the disclaimer; `GLOSSARY.md` gained the four rows. What remains open under AUT-01 is the
  author's approval of three PT renderings.
- **Item 27** asks whether the *empirical results of Chapter 5* support a Pareto-flavored claim. That is
  a claim-registry question under §3 C2, about results, not about §2.3's exposition.

They interact in one place and it must not be missed: **if item 27 is answered yes in any form, the
sentence "This dissertation therefore claims no Pareto property for its models" becomes false as
written** and needs narrowing to optimality (which is what it actually means). Four probes guard that
sentence, so an edit to it will fire `R9-pareto` and must be re-pointed deliberately, with the claim
re-verified in the new text.

---

## 5 · [VERIFY] LIST

1. **[VERIFY] Item 7's comparative claim has no opened anchor and the count evidence points the other
   way.** `NORTH_STAR` §6 Ch.1 beat 4(b)'s [VERIFY] is hereby closed **in the negative**. Take the
   sanctioned fallback wording. Four candidate surveys (N1-N4) were opened at abstract level only; if
   the author wants one more attempt, the full texts of `10.1186/s13638-022-02114-6` and
   `10.1145/3510409` are the two unexhausted leads, and I did not open them.
2. **[VERIFY] `capanema2023poirgnn` (L8) has no abstract in OpenAlex and its full text was not opened
   this session.** Admissible for its title's target (next place's category) and nothing more. It is
   already cited as a Ch.5 baseline, so this affects only any NEW characterization of it.
3. **[VERIFY] `zhu2022drrgnn` (L4) full text not opened** — closed access, `doi_resolve` 403. The
   per-person-region distinction is quoted from the abstract, which is enough for the sentence already
   in `02_related.tex`, but a stronger claim about its region construction would need the paper.
4. **[VERIFY] Hgarn (L5, 10.1109/tits.2024.3513695) is NOT in `references.bib`** (checked against all
   100 entries) and its abstract only was opened. It is a 2024 near-miss in the auxiliary-task pattern.
   Adding it would strengthen the novelty paragraph's coverage against FAB-28's "only two papers"
   objection — **but it must not be added on this report's authority**: R1(b) requires the landing page
   or PDF, and I opened only the OpenAlex abstract.
5. **[VERIFY] The OpenAlex counts in §2.2(c) are keyword measurements, not field measurements.** They
   are reported to show the author's premise may be backwards; they are not citable evidence in either
   direction and should not enter prose.
6. **[VERIFY] Two OpenAlex `search=` calls returned HTTP 504 and were not retried.** Both queries were
   re-run in the `title_and_abstract.search` form, which is what §3.5's table reports, so no probe is
   missing — but the raw-`search` coverage of those two phrasings is incomplete.
7. **[VERIFY] I did not audit item 7's second half** (category leakage from the check-in-level
   embedding into the next-category target). `5_mobiwac/05_setup.tex:70` is where the existing screening
   audit lives; a separate track should start there.
8. **[VERIFY] `src/build/main.pdf` was not opened.** Its mtime postdates `2_fundamentals.tex` by about
   ten minutes, which contradicts the briefing's staleness premise, but mtime ordering is not evidence
   about content. Every claim here is from source files in the working tree.

## 6 · FINDING FOR FAB-28 AND GER-11 (requested by the task)

**FAB-28 can be UNBLOCKED.** Its block was recorded as: the `wang2025hamtl` abstract could not be
opened, and the novelty claim turns on whether that paper treats a region-like unit as an end target.
**The full 28-page PDF has been in this repository the whole time**, at
`articles/dissertacao/science/articles/wang2025hamtl.pdf`, and I read it this session. Its own text
settles the question three times over: category is the auxiliary task, location is the main task and
is venue-level, the word "region" occurs once in a 1970 reference title, and no category metric is
reported. **The novelty sentence at `2_fundamentals.tex` is not threatened by HAMTL, established by
direct reading rather than by the bibliography's recorded note.**

The residual half of FAB-28 — Fabrício's actual request, a fuller account of MTL-for-POI work than two
papers — is **not** settled by this, and no single paper settles it. But the premise behind FAB-28's
quote may itself have been overtaken by a later edit: the paragraph it objects to now carries **eight
citation keys naming seven systems** (MCARNN, CSLSL, iMTL, Halder et al. with two references, TME,
HAMTL, IeMTLF), not two. Measured (V1), from `articles/dissertacao`:

```
awk '!/^[[:space:]]*%/' src/chapters/2_fundamentals.tex \
  | sed -n '/In mobility, MTL has been used almost entirely/,/none treats next category/p' \
  | grep -o '\cite{[^}]*}' | sed 's/\\cite{//;s/}//' | tr ',' '\n' | sort -u | wc -l
  -> 8
```

Whether eight keys satisfies the advisor is his call, not a measurement, and it belongs to whoever
owns FAB-28.

**GER-11 is answered by Appendix F, and the answer should be recorded.** GER-11's objection is that a
single mean over four seeds cannot distinguish consistent orthogonality from cancelling conflicts.
Appendix F is precisely the missing evidence: per-fold spread, confidence intervals, an equivalence
test against a pre-set margin, seven datasets. The item's disposition should move from "strengthen it
or downgrade the sentence" to "strengthened; the surviving question is only how much of it Chapter 1
and Chapter 6 should carry", which is §3.4 above.


---

<!-- estado-rodada -->
> **Rodada encerrada · último toque 2026-08-04 · sem autoridade.**
> Este ficheiro é registo de proveniência do que foi discutido nesta passagem, não fonte
> de um facto corrente. O que ficou decidido está em [`VEREDITOS.md`](../../../VEREDITOS.md);
> os valores entregues estão em `CLAUDE.md` §0.1. Não copie nada daqui sem confirmar lá.
