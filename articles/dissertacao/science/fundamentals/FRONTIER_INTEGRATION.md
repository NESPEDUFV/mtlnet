# FRONTIER_INTEGRATION — routing the 24 frontier works into the dissertation

<!-- Author ruling (2026-07-21): INCLUDE the frontier set; "this can be seen with good look for the
     dissertacao." So the 24-entry frontier bib is no longer routed OUT of the document. It is used
     SPARINGLY and in the right places: Ch.2 stays thin (each theme gets at most a one-clause
     forward pointer), and the bulk of the frontier weight lands in 2.5 Relevance (as the live
     research context that motivates the "pressing need") and in the paper chapters' related-work /
     the dissertation's future-work. All 24 DOIs verified this session (24/24 resolve on OpenAlex). -->

## Placement rule
- **Ch.2 body (2.1-2.4):** at most ONE forward-looking clause per theme, citing 1-2 frontier works as
  "current directions", never a survey. The thin-chapter budget holds.
- **2.5 Relevance:** the frontier set appears here as the live-context sentence(s) that make the
  "pressing need" current in 2026 (still argument-led; a handful of cites, not a catalog).
- **Paper chapters' related-work / future-work:** the remainder, at full weight.

## The 24, grouped, with routing

### Cluster 1 — Hypergraph next-POI recommendation (next place)
`Yan_2023` (Spatio-Temporal Hypergraph Learning), `lai2024disentangled` (Disentangled Contrastive Hypergraph, SIGIR),
`Lai_2023` (Multi-view ST-Enhanced Hypergraph), `An_2024` (MvStHgL), `Zhang_2024` (Hyper-relational KG),
`Yangyang_2022` (Hypergraph Embedding + Logical MF), `lai2024adaptive` (Adaptive ST Hypergraph Fusion, ICASSP).
- **Route:** 2.2 forward clause ("beyond the check-in level, hypergraph representations are a current direction")
  cite ONE (e.g. `Yan_2023`); rest -> future-work / related-work. These target next **place**, not category/region.

### Cluster 2 — LLM / generative for next-location (next place)
`Feng_2024` (Zero-shot LLM next POI), `Beneduce_2025` (LLMs are Zero-Shot Next Location Predictors),
`Solatorio_2023` (GeoFormer, GPT), `Cheng_2025` (POI-Enhancer, LLM semantic enhancement).
- **Route:** 2.5 live-context clause (LLM-based prediction is the 2024-2026 frontier); cite 1-2. Rest -> future-work.

### Cluster 3 — Contrastive / self-supervised representation
`Liu_2022` (CSTRM trajectory SSL), `Wang_2025` (multi-modal contrastive urban space), `Chen_2025` (ST-KG contrastive + trajectory prompt).
- **Route:** 2.2 forward clause (contrastive/SSL as the current representation substrate), cite ONE
  (e.g. `Wang_2025`); rest -> future-work. Ties to the DGI->HGI->Check2HGI infomax lineage as "the next substrate".

### Cluster 4 — Urban-region representation (region-level embeddings)
`Huang_2022` (semantics-preserved POI embedding), `Luo_2022` (Urban Region Profiling multi-graph),
`Luo_2023` (Urban Functional Zone Classification).
- **Route:** 2.2 (region-embedding neighborhood of HGI) OR 2.1 next-region context; cite `Huang_2022` once. Rest -> related-work.

### Cluster 5 — Attention / knowledge-graph next-POI
`wang2023context` (context-and-category-aware double self-attention), `wang2023zone` (Zone-Enhanced ST),
`liu2023mandari` (Mandari MMTKG), `Chen_2025` (also KG, see cluster 3).
- **Route:** 2.1 sequence-model forward clause (self-attention/KG next-POI is the active recsys line); cite 1. Rest -> related-work.

### Cluster 6 — MTL for mobility BEYOND POI (breadth for 2.3)
`liu2023ship` (ship trajectory + collision MTL), `Wang_2022` (maritime trajectory + destination MTL),
`Meng_2023` (lane-changing trajectory MTL), `Sun_2024` (privacy-preserving category-aware POI recommendation).
- **Route:** 2.3 MTL-for-mobility clause — these show MTL trajectory/destination pairings in adjacent mobility
  domains (maritime, road), useful to show the pattern generalizes; cite 1-2. `Sun_2024` is category-aware POI
  (closest to the dissertation's category target) -> 2.1 or 2.3. Rest -> related-work.

## What does NOT change
- None of these predict next **region as an end target** (still the dissertation's novelty; STEP-2 finding holds).
- Ch.2 remains thin: the frontier earns at most one forward clause per theme; the weight is in 2.5 + related-work.
- All keys are the de-collided forms (`lai2024disentangled` etc.); merge `new_references_frontier_decollided.bib`
  into the global bib (0 key/DOI collisions confirmed against all four existing bibs).
