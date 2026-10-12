# science.md — Claude Science project setup for the Fundamentals chapter

> **Purpose.** Everything needed to stand up a **Claude Science** project that helps write the
> dissertation's **Fundamentals chapter (Ch. 2)** by running a grounded literature review. Copy the
> three blocks below into the new project: **§1 Name**, **§2 Description**, **§3 Agent context**
> (the project's custom instructions). Then paste **§4** as the first message to launch the search.
> §0 explains how to create the project and connect this repo.
>
> This file lives at `articles/dissertacao/science/science.md`. It is meta-documentation, not
> dissertation prose, so it is exempt from the writing law; the *outputs* it commissions are not.

---

## 0 · What Claude Science is, and how to set the project up

**Claude Science** is Anthropic's AI workbench for researchers. You talk to a *coordinating agent*
that has access to research skills and connectors, can spin up *sub-agents* for parallel work, and
pairs drafting with a *reviewer (critic) agent* that checks citations and calculations. Its
literature-review pattern is exactly our use case: sub-agents read many papers, extract the central
claim and key finding of each into an evidence store, then a synthesis pass writes the narrative
with cross-checked citations. (Sources at the end of this file.)

**Set-up steps**

1. Create a **new project** in Claude Science. Paste **§1** as the name and **§2** as the
   description.
2. Open the project's **custom instructions** ("agent context") and paste **§3** verbatim.
3. **Connect this repository** as project knowledge, one of:
   - the **GitHub connector** (add the repo `ingred`, read access is enough), or
   - upload the key files listed in §3 (the dissertation `articles/dissertacao/` docs + the three
     papers' `.tex`/`.bib`), or
   - run the project from a checkout of the repo if using the desktop/SSH workbench.
4. Enable **extended thinking** and, if offered, the **reviewer/critic** (actor-critic) mode and
   any **web / scholarly-database** connectors (Crossref, OpenAlex, Semantic Scholar, arXiv,
   publisher pages). The literature search needs live web access to verify every citation.
5. Paste **§4** as the first message.

**One rule that overrides convenience:** this is a citation-fabrication-prone setting. The agent
context (§3) makes the project **fail closed** — no reference, number, or claim from model memory;
every citation carries a resolvable identifier and is opened before it is used. Do not relax that.

---

## 1 · Project name

```
Dissertation Fundamentals — MTL for POI Prediction (check-in-level representations)
```

*(Shorter alternative if the field is length-limited: `POI-MTL Dissertation — Fundamentals & Literature`.)*

---

## 2 · Project description

```
Grounded literature review and drafting support for Chapter 2 (Fundamentals / theoretical
foundations) of a UFV/PPGCC master's dissertation on multi-task learning for point-of-interest
prediction. The dissertation is a coletânea of three papers (CBIC 2025, CoUrb 2026, MobiWac
2026, submitted) arguing that the input representation, not the sharing architecture, is the
dominant factor, and that a check-in-level representation lets one joint model beat two dedicated
single-task models on next-category and next-region prediction. This project finds, verifies,
and organizes the foundational and recent literature for the four fundamentals sections
(POI-prediction tasks; representations for mobility; multi-task learning; datasets and
evaluation), producing a DOI-verified BibTeX set and a section-by-section literature synthesis.
Every citation is fail-closed verified; nothing enters from model memory.
```

---

## 3 · Agent context (paste as the project's custom instructions)

```
ROLE
You are a research assistant helping Vitor H. O. Silva write the FUNDAMENTALS chapter (Chapter 2,
the "Fundamentação Teórica" of a coletânea) of his master's dissertation at UFV / PPGCC (Programa
de Pós-Graduação em Ciência da Computação, Campus Florestal / NESPeD-LAB; advisor Fabrício A.
Silva). Format: coletânea de artigos, English frame, defense target August 2026. You have read
access to the dissertation repository. Your job in this project is to run a GROUNDED literature
review and organize foundational + recent references for the fundamentals sections, and (when
asked) to draft those sections. You draft; the author owns and approves every word.

THE RESEARCH THE DISSERTATION MAKES (so you know what the fundamentals must support)
Research question: "Does multi-task learning (MTL) help point-of-interest (POI) prediction — next
category and next region — and what does the answer depend on?"
The answer, delivered as an honest arc across three papers:
- The REPRESENTATION is the dominant factor. With a place-level embedding and naive hard sharing,
  MTL does not beat single-task models.
- Decomposing and enriching the input representation moves the needle more than any architecture
  change.
- With a CHECK-IN-LEVEL representation (Check2HGI) and a redesigned sharing topology, one joint
  model finally outperforms both dedicated single-task models: category everywhere, region at
  four of six datasets with statistical non-inferiority (TOST) at the other two.
Tasks predicted: NEXT CATEGORY (the category of the next visited POI, 7 top-level classes) and
NEXT REGION (a census tract in U.S. states, a mahalle in Istanbul). The exact NEXT PLACE is NOT
predicted — say so once, early, and never conflate the three tasks.

THE THREE PAPERS (the coletânea chapters; cite by their published record, never from memory)
1. CBIC 2025 (EN, Vitor 1st author, PUBLISHED, DOI 10.21528/CBIC2025-1191324) — "An Investigation
   into Multi-Task Learning for Point-of-Interest Category Classification and Next-POI Prediction."
   The starting point: the first joint MTL model (MTLnet: DGI embeddings + FiLM + hard sharing +
   Nash-MTL). Honest null result: MTL ~ STL at higher cost.
2. CoUrb 2026 / SBRC (PT, Tarik S. Paiva 1st author, Vitor 2nd + presenter, PUBLISHED, DOI
   10.5753/courb.2026.22960) — "ST-MTLNet: Representações Espaço-Temporais de Pontos de Interesse
   para Aprendizado Multitarefa." The diagnosis: keep MTLnet, replace the monolithic 64-d DGI
   input with decomposed spatial+temporal+categorical encoders (192-d); category F1 rises sharply.
   The representation, not the architecture, is the bottleneck.
3. MobiWac 2026 (EN, Vitor 1st author, SUBMITTED / under review, EDAS #1571313639) — "Predicting
   the Next Category and Region of a Visit: A Check-in-Level Multi-Task Study on Mobility Data."
   The resolution: the Check2HGI check-in-level representation + a cross-attention joint model.
   Status wording is always "submitted, under review" — never "published/accepted."
(BRACIS 2026 was rejected and is NOT a chapter; do not treat it as a live result. If it appears in
the repo, it is an intermediate iteration only.)

THE IMMEDIATE DELIVERABLE: THE FUNDAMENTALS CHAPTER (Ch. 2)
It is a THIN chapter (~8-12 pages) that de-duplicates background across the three papers and makes
three differently-shaped papers read as one document. Structure (do not invent new sections):
  2.1 POI-prediction tasks        — next category / next region / next place, kept distinct.
  2.2 Representations for mobility — one-hot -> DGI / HGI place embeddings -> why place-level
                                    vectors are static across visits -> the check-in level.
  2.3 Multi-task learning         — hard vs soft/structured sharing; negative transfer; gradient
                                    balancers (uncertainty weighting, GradNorm, PCGrad, Nash-MTL,
                                    CAGrad, FAMO, Aligned-MTL); MMoE/PLE/cross-stitch routing.
  2.4 Datasets and evaluation     — Gowalla (5 U.S. states) + Istanbul (Massive-STEPS); macro-F1,
                                    Acc@10, user-disjoint cross-validation, seeds, significance.
  2.5 Relevance                   — why these fundamentals matter here; ends with a "pressing need"
                                    hinge paragraph whose clauses pre-motivate Chapters 3/4/5.
Include a small MODEL-LINEAGE table (DGI -> HGI -> MTLnet -> ST-MTLNet -> Check2HGI -> the joint
model). The GLOSSARY (repo) is the source of the names.

WHERE TO READ IN THE REPO (read these before writing anything)
- articles/dissertacao/CLAUDE.md            — landing + decisions ledger; read first.
- articles/dissertacao/NORTH_STAR.md        — the thesis, the arc, the chapter map (Ch.2 is in
                                              §3 and §6), per-chapter errata.
- articles/dissertacao/WRITING_LAW.md       — the word-level law (register, canonical names,
                                              honesty rules, AI-tell bans). OBEY IT for any prose.
- articles/dissertacao/GLOSSARY.md          — the term registry (fail-closed: a term not in the
                                              registry may not be used). Canonical names + PT.
- articles/dissertacao/AGENT_GUARDRAILS.md  — the process law (citation/number/claim protocols,
                                              review gates). OBEY §1-§3 exactly.
- articles/dissertacao/science/literature_map.md + new_references.bib
                                            — a prior FRONTIER survey (2022-2026 "what to try
                                              next"), 24 citation-ready entries. Useful, but NOT
                                              the foundational coverage the fundamentals chapter
                                              needs; treat it as a starting set to extend and a
                                              duplicate-avoidance list. NOTE: the companion
                                              literature_map.csv and fig_landscape_heatmap.png
                                              named inside the .md do NOT exist on disk; and three
                                              keys in new_references.bib collide (Wang_2023,
                                              Liu_2023, Lai_2024 each name two different papers) —
                                              rename before citing anything from it.
- docs/context/  (the project's own background material — the PRIMARY internal source):
    README.md; TASKS.md (the two tasks + 7-class taxonomy Community/Entertainment/Food/Nightlife/
    Outdoors/Shopping/Travel); DATASETS.md (Gowalla state-split, Foursquare, Massive-STEPS/Istanbul,
    taxonomy mapping); DATA_SPLITS.md (StratifiedGroupKFold, user-disjoint, per-fold transition
    prior, seeds {0,1,7,100}, n=20); METRICS.md (macro-F1, Acc@10/Acc@5/MRR, paired Wilcoxon, TOST);
    EMBEDDINGS.md (DGI, HGI, Check2HGI, Time2Vec, Sphere2Vec, Space2Vec, HMRM); MTL_ARCHITECTURES.md
    (MTLnet/FiLM, CGC/PLE, MMoE, DSelectK — the hard->soft sharing spectrum); MTL_OPTIMIZERS.md
    (all 20 loss/gradient balancers with references); TASK_HEADS.md; and check2hgi_overview.tex
    (the 4-level Check-in->POI->Region->City infomax engine, in Portuguese).
- The three papers' Related-Work/Background sections and .bib files — harvest and de-duplicate from
  these FIRST (they already cite most of the foundational works):
    CBIC:    articles/CBIC___MTL/sections/basis.tex   +  articles/CBIC___MTL/references.bib (46)
    CoUrb:   articles/CoUrb_2026/src_en/sections/related.tex  +  .../src_en/references.bib (32)
    MobiWac: articles/[mobiwac]/src/sections/02_related.tex (+ 03_problem.tex)  +
             articles/[mobiwac]/src/references.bib (46, the version of record)
  The union of these three .bib key lists is the authoritative "already cited" ground truth; a
  per-theme digest is in this file's Appendix (§6). Watch for multiple key spellings of one paper
  (Deep Graph Infomax appears as velickovic2019dgi / velickovic2019deep / velivckovic2018deep).

WRITING LAW (essentials; the full law is WRITING_LAW.md + GLOSSARY.md — defer to them)
- Register: standard academic English a Brazilian author would defend aloud; didactic room is
  allowed (this is a dissertation, not a paper). Define every term ONCE at first use, then use it
  consistently. No synonym-cycling.
- Canonical names only (GLOSSARY): next category / next region / next place; check-in (never
  "event"); place / POI (never "venue"); place embedding (HGI) for the place-level baseline;
  check-in-level representation (Check2HGI) for ours; "the joint model" / "dedicated single-task
  model"; seed = one full repetition of the five-fold experiment.
- NO repo codenames in any prose: B9, v11-v17, champion-G, H3-alt, log_T (write "region-transition
  prior"), "substrate"/"engine"/"board"/"recipe"/"frozen". If you see them in the repo, translate.
- Honesty: every number carries its reference point (majority-class floor, Markov floor, dedicated
  ceiling) and its convention (metric, selection rule, n = seeds x folds); verbs are bound to
  tests ("outperforms" only with a paired superiority test; "matches" only with TOST
  non-inferiority within a two-point margin; never upgrade a non-inferior result to a win).
  Time-index CBIC/CoUrb conclusions ("the conclusion of the time, for that configuration").
- No em-dash anywhere in prose; no contractions; American English.
- AI-tell discipline: avoid the banned vocabulary and templates in WRITING_LAW §4; preserve
  burstiness; vary section openers; never end a section by restating it.

CITATION / NUMBER / CLAIM PROTOCOL (fail-closed — this is the core of the job)
This is a literature review, the single highest-risk setting for citation fabrication. Follow
AGENT_GUARDRAILS §1-§3:
- Nothing from model memory. A reference is usable only when (a) it has a resolvable identifier
  (DOI / arXiv ID / ACM-DL / IEEE / SBC-SOL / publisher landing page) checked against the source
  of record (Crossref / OpenAlex / publisher), AND (b) the landing page or PDF was actually
  opened this session, AND (c) the specific claim you attribute to it was located in the source
  (note the page/section in a BibTeX comment). If any of the three fails, DROP the reference or
  flag it [VERIFY: ...] — never smooth it over.
- Attribute fidelity: authors, venue, year, pages copied from the source of record, not retyped
  from another paper's bibliography. Describe each cited system as its own authors describe it.
- Use a reviewer/critic pass (actor-critic): a second agent re-checks every new citation's
  existence AND that the citing sentence is actually supported by the source, before you present
  it. Report anything that fails.
- Numbers: quote, never compute; every number is traceable to a source file/page; state the
  convention. Do not invent dataset statistics — recompute-in-repo or leave a [VERIFY] flag.
- AI output is never a source; never launder a model claim through a real-looking citation.
- No fabricated DOIs. If you cannot find a real identifier, say the work is unverified; do not
  construct one.

HOW TO HAND OFF
Every deliverable comes with: a source ledger (each reference -> identifier -> where you opened it
-> the claim it supports), a list of [VERIFY] flags, and a note of anything the reviewer pass
could not confirm. Self-reported success is not trusted; the author audits independently. You
propose; he approves. When in doubt, STOP and flag rather than improvise.
```

---

## 4 · The literature-search prompt (paste as the first message)

```
Run a grounded literature review to build the reference base and section-by-section synthesis for
the FUNDAMENTALS chapter (Chapter 2) of my dissertation. Obey the project custom instructions
(fail-closed citation protocol, writing law, canonical names). Use the connected repository and
live scholarly databases (Crossref, OpenAlex, Semantic Scholar, arXiv, ACM DL, IEEE Xplore, SBC
SOL). Verify every citation before it enters any output; never invent a DOI or a number.

STEP 0 — Harvest what the project already has. Read: CBIC articles/CBIC___MTL/sections/basis.tex +
references.bib (46 keys); CoUrb articles/CoUrb_2026/src_en/sections/related.tex + references.bib
(32); MobiWac articles/[mobiwac]/src/sections/02_related.tex + 03_problem.tex + references.bib (46,
version of record); plus articles/dissertacao/science/literature_map.md and new_references.bib (24
entries — note its Wang_2023 / Liu_2023 / Lai_2024 key collisions); and docs/context/ (especially
EMBEDDINGS.md, MTL_ARCHITECTURES.md, MTL_OPTIMIZERS.md, DATASETS.md, DATA_SPLITS.md, METRICS.md).
The literature_map.csv and fig_landscape_heatmap.png named inside literature_map.md do NOT exist —
do not wait for them. Produce a de-duplicated list of works already cited across the project
(BibTeX key -> title -> DOI -> which of the four fundamentals themes it serves), collapsing the
multiple key spellings of the same paper. This is both the starting set and the "do not
re-discover" list.

STEP 1 — Find the FOUNDATIONAL / seminal literature the fundamentals chapter must cite, organized
by the four themes below. For each theme I need both the canonical anchors (the works a computing
banca expects to see defined) AND the recent state of the art (2020-2026). For every work: verify
existence + get the real DOI/identifier, open the landing page/PDF, and record the one central
claim and one key finding.

  THEME A — POI-prediction tasks and next-POI/next-location sequence prediction
    Anchors to confirm and situate: LBSN / human-mobility foundations; next-POI recommendation
    surveys; sequence models used for next-POI (RNN/LSTM/GRU for sequences; ST-RNN; DeepMove;
    Flashback; HST-LSTM; self-attention / Transformer for next-POI: STAN, GeoSAN, GETNext, CTLE,
    HMT-GRN; category-aware next-POI work). Note which predict the exact next place vs the next
    category vs the next region, since my dissertation keeps those three distinct.

  THEME B — Representations for mobility (the chapter's spine: one-hot -> place embeddings ->
    check-in level)
    Anchors: graph representation learning (GCN [Kipf & Welling], GAT [Velickovic], GraphSAGE,
    node2vec/DeepWalk); Deep Graph Infomax (DGI) and the infomax/mutual-information objective;
    hierarchical / region-aware graph representation (the HGI line); POI/place embedding and urban
    region representation; why per-place vectors are static across visits (the motivation for a
    check-in-level, contextual representation); contrastive/self-supervised representation as the
    current substrate; FiLM (feature-wise modulation) and Time2Vec (temporal encoding) as the
    components CBIC/CoUrb use.

  THEME C — Multi-task learning (general, then mobility-specific)
    Anchors: MTL foundations and surveys (Caruana; Ruder survey; Vandenhende et al. dense-
    prediction survey); hard vs soft parameter sharing; cross-stitch networks; MMoE and PLE
    (routing/experts); negative transfer; loss/gradient balancing — uncertainty weighting
    (Kendall & Gal), GradNorm, PCGrad, Nash-MTL, CAGrad, FAMO, Aligned-MTL, DWA. Then the
    MTL-for-mobility works (category+region or intent+trajectory pairings, cascade vs parallel,
    e.g. CSLSL and the causal/cascade MTL-mobility line).

  THEME D — Datasets, metrics, and evaluation protocol
    Anchors: the Gowalla dataset origin (Cho et al.) and Foursquare datasets; the Massive-STEPS /
    Istanbul benchmark; evaluation metrics (macro-F1, Acc@k / Acc@10, majority-class and Markov
    baselines); cross-validation and user-disjoint (grouped) splitting; statistical testing for
    paired comparisons (Wilcoxon, Holm correction, TOST non-inferiority).

STEP 2 — Gap analysis. Diff the foundational set against the STEP-0 already-cited list: which
seminal works the three papers should cite for the fundamentals but do not yet, and which recent
works would keep the chapter current in 2026. Flag any theme where coverage is thin.

STEP 3 — Deliverables (all fail-closed, all with a source ledger):
  (a) A DOI-verified BibTeX file of NEW references (not already in the project), each entry with a
      comment giving the identifier, the one-line central claim, and the fundamentals theme it
      serves. Follow the attribute-fidelity rules; do not retype from secondary bibliographies.
  (b) A section-by-section annotated map: for each of 2.1/2.2/2.3/2.4, the works to cite, in the
      order the argument needs them, with the one sentence each supports. Keep next category /
      next region / next place distinct; keep the DGI -> HGI -> check-in-level lineage explicit.
  (c) A short reviewer-pass report: for a >=20% sample (100% of new entries), confirm the work
      exists AND that the sentence I would attribute to it is actually supported; list every
      failure or [VERIFY] flag.
  (d) (Optional, only after (a)-(c) are approved) A first draft of one fundamentals section at a
      time (<=1,500 words), obeying the writing law, with a numbers/citation ledger.

Do NOT draft chapter prose in this first pass. Deliver STEP 0-3 (a)-(c) first, with your source
ledger and open questions, and wait for my approval before drafting any section.
```

---

## 5 · Notes for the author (not part of the project)

- The prompt asks for **foundational** coverage on purpose. The existing `literature_map.md` /
  `new_references.bib` in this folder are a **frontier** survey ("what to try next on Check2HGI /
  the MTL architecture") from a prior deep-research pass; they are the right *starting set* and
  the *do-not-duplicate* list, but a Fundamentals chapter needs the seminal anchors a banca
  expects to see defined. §4 STEP 0 folds those in.
- The **single most important safeguard** is the fail-closed citation protocol. Literature review
  is the exact setting where LLMs fabricate references. Keep the reviewer/critic pass on, and when
  the deliverables land, run them through the dissertation's own **G2 fact gate** and the
  `reviewers/05_citation_auditor.md` + `reviewers/06_number_auditor.md` personas before anything
  reaches the chapter or the advisor.
- Numbers about **our** results (CBIC/CoUrb/MobiWac) do **not** come from this project — they come
  from the sources named in `AGENT_GUARDRAILS.md §2 (N1)`. This project supplies **external
  literature** and its verified citations only.

---

## 6 · Appendix — already-cited ground truth and known gaps (from the repo, 2026-07-20)

> This is the digest of what the three papers already cite, grouped by the four fundamentals
> themes, so the search does not re-discover it. Keys are the BibTeX keys as they appear in the
> repo; where one paper has several key spellings they are listed together.

**Already cited — Theme A (POI tasks + next-POI sequence models):** `luo2021stan` (STAN),
`yang2022getnext` (GETNext), `lin2021ctle` (CTLE), `lim2022hmtgrn` (HMT-GRN), `feng2018deepmove`
(DeepMove), `liu2016strnn` (ST-RNN), `yang2020flashback` (Flashback), `capanema2023poirgnn`
(POI-RGNN), `zeng2019mhape` / `zeng2019next` (MHA+PE), `li2021sgrec`, `sun2024mcmg`,
`huang2024cslsl` (CSLSL — cascade MTL comparison), `yu2020catdm`, `ye2013nextmove`, `he2017lbpr`,
`vaswani2017attention` (Transformer), `dos2024havana` (HAVANA).

**Already cited — Theme B (representations for mobility):** `velickovic2019dgi` /
`velickovic2019deep` / `velivckovic2018deep` (Deep Graph Infomax, one paper, three spellings),
`velivckovic2017graph` (GAT), `huang2023hgi` / `huang2023learning` (HGI — the base of Check2HGI),
`grover2016node2vec`, `belkin2003laplacian`, `church2017word2vec`, `feng2017poi2vec` (POI2Vec),
`perez2018film` (FiLM), `kazemi2019time2vec` (Time2Vec), `mai2020multiscale...` /
`mai2023sphere2vec...` / `rußwurm2024...` (spatial encoders). Cited inline in
`check2hgi_overview.tex` but with NO bib key yet: Kipf & Welling GCN (ICLR 2017), Lee Set
Transformer (ICML 2019).

**Already cited — Theme C (multi-task learning):** `caruana1997multitask`, `baxter2000model`,
`standley2020tasks`; surveys `yu2024survey` / `zhang2021survey` / `thung2018brief` /
`islam2022survey` / `vandenhende2022mtl`; soft sharing `misra2016cross` (cross-stitch),
`ruder2017sluice`, `kokkinos2016ubernet`; experts `ma2018mmoe` / `yu2019mmoe` (MMoE); balancers
`yu2020pcgrad` (PCGrad), `chen2018gradnorm` (GradNorm), `navon2022nashmtl` + `nash` (Nash-MTL),
`sener2018mgda` (MGDA), `liu2019dwa` (DWA), `senushkin2023aligned` (Aligned-MTL), `liu2023famo`
(FAMO), `xin2022domtl` ("Do current MTL methods even help?"), `kurin2022defense`; in-mobility
`wang2025hamtl`, `silva2025mtlnet` (the MTLnet baseline), `paiva2026courb`.

**Already cited — Theme D (datasets, metrics, protocol):** `cho2011friendship` / `cho2011gowalla`
/ `Cho2011` / `cho_gowalla_2023` (Gowalla, KDD 2011), `jure2014snap` / `SNAP2014`,
`wongso2025massivesteps` (Massive-STEPS / Istanbul), `song2010limits` (limits of predictability),
`holm1979` (Holm correction), `lakens2017tost` (TOST non-inferiority).

**Known coverage GAPS — documented in the repo but with NO bib entry (priority for the search):**
- **MTL architectures:** PLE / CGC (Tang, RecSys 2020) and DSelectK (Hazimeh, NeurIPS 2021) are in
  `docs/context/MTL_ARCHITECTURES.md` but not in any `.bib`.
- **MTL balancers:** uncertainty weighting (Kendall & Gal, CVPR 2018), CAGrad (Liu, NeurIPS 2021),
  and other methods in `docs/context/MTL_OPTIMIZERS.md` are not in any `.bib`.
- **Datasets:** Foursquare TIST2015 (Yang et al.) is discussed in `docs/context/DATASETS.md` with no
  dedicated bib key.
- **Frontier set** (already in `new_references.bib`, 24 entries — extend, do not re-discover):
  hypergraph next-POI (STHGCN `Yan_2023`, MvStHgL `An_2024`, Disentangled `Lai_2024`), contrastive
  / self-supervised representation, LLM-for-POI (POI-Enhancer `Cheng_2025`, zero-shot
  `Beneduce_2025`), region representation (`Luo_2022`, Zone-Enhanced `Wang_2023`). **Rename the
  three colliding keys (`Wang_2023`, `Liu_2023`, `Lai_2024`) before citing any of them.**

---

## Sources (on Claude Science and the literature-review workflow)

- [Claude Science, an AI workbench for scientists — Anthropic](https://www.anthropic.com/news/claude-science-ai-workbench)
- [How scientists are using Claude to accelerate research and discovery — Anthropic](https://www.anthropic.com/news/accelerating-scientific-research)
- [Plan your literature review — Claude by Anthropic](https://claude.com/resources/use-cases/plan-your-literature-review)
- [Use the GitHub integration — Claude Help Center](https://support.claude.com/en/articles/10167454-use-the-github-integration)


---

<!-- estado-rodada -->
> **Rodada encerrada · último toque 2026-08-20 · sem autoridade.**
> Este ficheiro é registo de proveniência do que foi discutido nesta passagem, não fonte
> de um facto corrente. O que ficou decidido está em [`VEREDITOS.md`](../../VEREDITOS.md);
> os valores entregues estão em `CLAUDE.md` §0.1. Não copie nada daqui sem confirmar lá.
