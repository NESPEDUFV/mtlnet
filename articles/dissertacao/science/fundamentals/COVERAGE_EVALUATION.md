# COVERAGE_EVALUATION — does Ch.2 cover the fundamentals the three articles rely on?

<!-- Method: extracted every \cite key from the three articles' related-work/background sections
     (CBIC basis.tex, CoUrb related.tex, MobiWac 02_related.tex + 03_problem.tex), normalized
     variant spellings, and diffed against the keys threaded in the 2.1-2.4 section maps. Then
     classified each uncovered key as (A) a fundamental Ch.2 should define, (B) a peripheral
     competitor system that belongs in a paper chapter's related-work, or (C) already covered by an
     equivalent. NORTH_STAR Ch.2 spec: 2.1 tasks (category/region/place distinct) -> 2.2
     representations (one-hot -> DGI/HGI -> check-in level) -> 2.3 MTL (hard/soft sharing, negative
     transfer, balancers) -> 2.4 datasets+metrics+protocol -> 2.5 relevance hinge + lineage table. -->

## Headline
The section maps already cover the **fundamentals** a computing banca expects for all five sections.
Of 19 article-cited keys not literally present in the maps, **most are peripheral competitor systems** correctly
routed to the paper chapters' related-work, not Ch.2. **Five are genuine fundamentals that were already cited in the
project but not yet threaded into the maps**; all five now are (using their existing keys, no new bib entry, claims
located firsthand). No theme is left thin.

## Coverage matrix (NORTH_STAR Ch.2 spec vs section maps)

| Section | Required beats (NORTH_STAR) | Covered? | Anchors in the map |
|---|---|---|---|
| 2.1 | category / region / place kept distinct; LBSN + mobility foundation; sequence models | **YES** | task formulations distinct; luca2021mobilitysurvey, song2010limits, DeepMove/STAN/GETNext/Flashback/CTLE/HST-LSTM/GeoSAN, category-aware line |
| 2.2 | one-hot -> DGI/HGI place embeddings -> static-across-visits -> check-in level; general encoders | **YES** | word2vec/DeepWalk/node2vec, GCN/GAT/GraphSAGE, DGI+infomax(MINE/DIM), HGI, CTLE (static->contextual), Time2Vec/SIREN/Space2Vec/Sphere2Vec/FiLM |
| 2.3 | hard/soft sharing, negative transfer, balancers, routing | **YES (+5 to add)** | Caruana, cross-stitch, MMoE/PLE/DSelectK, uncertainty/GradNorm/PCGrad/NashMTL/CAGrad/FAMO/Aligned/DWA/RLW; MTL-mobility (MCARNN/iMTL/CSLSL/CatDM) |
| 2.4 | Gowalla states + Istanbul; macro-F1, Acc@10, user-disjoint CV, seeds, significance; Δm, floors | **YES** | Gowalla(Cho), Foursquare(yang2015tsmc), Massive-STEPS; Sokolova macro-F1, Acc@k, Kohavi CV, sklearn splitter, Wilcoxon/Holm/TOST, Δm(Maninis), Markov(Gambs), predictability(Song 93%) |
| 2.5 | relevance synthesis + pressing-need hinge + lineage table | **YES** | 2.5_relevance_plan.md (argument-only, 3-clause hinge); model_lineage_table.md |

## The 19 uncovered keys, classified

### (A) THREAD into Ch.2 — fundamentals ALREADY CITED in the project (5, claims located firsthand this session)
> IMPORTANT: all five are already keys in the existing project bibs, so they get **no new bib entry** (that would
> duplicate a key in the single global dissertation bib and break compilation). They are threaded into the section
> maps using their **existing keys**. Done 2026-07-21.

| Existing key | What it is | Threaded into | Where it already lives / identifier |
|---|---|---|---|
| `sener2018mgda` | MTL as Multi-Objective Optimization (MGDA) — canonical: a weighted linear loss sum is valid only when tasks do not compete, motivating gradient balancing toward Pareto-optimality. | 2.3 (row 24) | CBIC bib; arXiv:1810.04650 (NeurIPS 2018) |
| `standley2020tasks` | "Which Tasks Should Be Learned Together?" — joint training hurts when objectives compete; the negative-transfer / task-grouping anchor. | 2.3 (row 25) | CBIC bib; arXiv:1905.07553 (ICML 2020) |
| `yu2024survey` | Recent comprehensive MTL survey (2024) — keeps 2.3 current alongside Ruder/Vandenhende/Zhang. | 2.3 (row 26) | CBIC bib; arXiv:2404.18961 |
| `silva2019urbancomputing` | Urban-computing-over-LBSN survey — the LBSN/mobility-data foundation; MobiWac's own motivation cite. | 2.1 (row 17) | MobiWac bib; DOI 10.1145/3301284 (ACM CSUR 2019) |
| `rußwurm2024geographiclocationencodingspherical` | General geographic location encoding (spherical harmonics + sinusoidal rep. networks) — "spatial encoders not only in mobility." | 2.2 (row 19) | CoUrb bib; arXiv:2310.06743 (ICLR 2024). Use this OR TorchSpatial, one example. |

### (B) KEEP in paper related-work — peripheral competitor systems (12)
`Halder2021`/`Halder2022` (queuing-time next-POI), `Xia2020` (MTPR — already named in the lineage as a prior
MTL-POI system; cited, not a fundamental to define), `dos2024havana` (HAVANA venue graph), `rahmani2019category`
(category-aware location embedding — a specific system; the CONCEPT is covered by CTLE/POI2Vec), `sun2020go`
(long/short-term next-POI), `sun2024mcmg`/`sun2024transtarec`/`sun2025kgtb` (specific next-POI recommenders),
`sun2024mcmg`, `wang2025hamtl` (hierarchy-aware MTL user-location — the ONE prior work closest to next-region;
belongs in Ch.5 related-work, flagged in STEP-2), `moura2025mobilityaware` (tourist mobility system — MobiWac
motivation), `ye2013nextmove` (early activity prediction — the cascade lineage root; already NAMED in 2.1/2.3
cascade discussion even if the key was not in the grep).
- **Rationale:** Ch.2 is thin and de-duplicates; these are system-level related-work, not concepts a banca expects
  *defined* in fundamentals. They stay in the paper chapters where they already live.

### (C) Already covered by an equivalent (2)
`ruder2017sluice` (Sluice/"Latent Multi-Task Architecture Learning") — soft-sharing IS covered in 2.3 (cross-stitch
+ the hard/soft spectrum); this specific system can be added as a one-cite example if desired (also on the errata
list for rename to the AAAI 2019 record). `wu2024torchspatial`/`rußwurm2024spherical` overlap — pick ONE for 2.2.

## Verdict
The 5 (A) fundamentals are threaded into the section maps using their existing keys (2.3 rows 24-26, 2.1 row 17,
2.2 row 19); no new bib entries (they were already cited). The rest stay in the paper related-work. Ch.2 now covers
every required beat for 2.1-2.5 with no thin theme. **This closes the coverage evaluation.**
