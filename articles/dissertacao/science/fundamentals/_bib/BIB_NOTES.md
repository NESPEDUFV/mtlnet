# BIB_NOTES — bibliography integrity, errata, and scope routing

## A. New references for Ch. 2
`new_references_ch2.bib` — 26 entries, DOI/identifier-verified, each with identifier + one-line claim + theme.
Global collision check against the union of CBIC + CoUrb + MobiWac + frontier (128 keys): **0 key, 0 DOI collisions**.

## B. Errata in the EXISTING project bibs (R4) — AUTHOR to apply to the dissertation bib
These are inherited-and-known-wrong entries. I do not silently rewrite the papers' .bib files; the author applies
them to the single dissertation bib (NORTH_STAR errata policy #7 = "fix + note").

| Entry | Problem | Fix |
|---|---|---|
| POI-RGNN (CBIC) | cites the wrong paper | use `capanema2023poirgnn` |
| HMRM | author names wrong | correct from source of record |
| GAT | should cite the ICLR version | replace with the ICLR 2018 record |
| `silva2025mtlnet` | venue name wrong ("Brazilian Conference on Intelligent Systems (CBIC)"); "Submetido" stale | correct venue; update status |
| `misra2016cross` | DOI resolves to a different paper | -> **10.1109/CVPR.2016.433** |
| `zhang2021survey` | listed DOI does not resolve | -> **10.1109/TKDE.2021.3070203** |
| `church2017word2vec` | resolves to a commentary, not skip-gram | cite `mikolov2013word2vec` for the method |
| `yu2019mmoe` | no distinct resolvable 2019 work; likely dup of `ma2018mmoe` | **confirm or drop** |
| DGI triple-key | velickovic2019deep / velickovic2019dgi / velivckovic2018deep | **consolidate to one key** |
| Nash-MTL double-key | one variant contains a slash | **consolidate; remove slash** |

## C. Frontier set — scope routing (Fundamentals ≠ frontier)
`new_references_frontier_decollided.bib` — the 24-entry frontier set with the 6 collisions disambiguated:

| Old key | New key | Paper |
|---|---|---|
| Lai_2024 | `lai2024disentangled` | Disentangled Contrastive Hypergraph (SIGIR 2024) |
| Lai_2024 | `lai2024adaptive` | Adaptive Spatial-Temporal Hypergraph Fusion (ICASSP 2024) |
| Wang_2023 | `wang2023context` | Context-and-category-aware double self-attention (Appl. Intell.) |
| Wang_2023 | `wang2023zone` | Zone-Enhanced Spatio-Temporal (TKDE) |
| Liu_2023 | `liu2023ship` | ship trajectory + collision MTL (Ocean Eng.) |
| Liu_2023 | `liu2023mandari` | Mandari MMTKG (ICME) |

**Routing rule (UPDATED 2026-07-21, author ruling "add the frontier, this can be seen with good look for the
dissertacao"):** the frontier set is **INCLUDED** in the dissertation and merged into the global bib. It is used
**sparingly and in the right places**, so Ch.2 stays thin: at most **one forward-looking clause per theme** in
2.1-2.4 (citing 1-2 frontier works as "current directions"), with the bulk of the frontier weight in **2.5
Relevance** (the live-context sentences that make the "pressing need" current in 2026) and in the **paper chapters'
related-work / future-work**. The full per-work routing is in `../FRONTIER_INTEGRATION.md` (six clusters:
hypergraph next-POI, LLM-for-POI, contrastive/SSL, urban-region embedding, attention/KG next-POI, MTL-for-mobility
beyond POI). All 24 frontier DOIs verified this session (24/24 resolve on OpenAlex). The Massive-STEPS
graph-transformer/hypergraph baselines (STHGCN, TGAT, ROTAN, MobGT) still stay in related-work; Massive-STEPS
itself is cited in 2.4 as the Istanbul benchmark of record (`wongso2025massivesteps`).

## D. Per-theme anchor budget (keep Ch.2 thin, ~8-12pp)
≈10-20 anchor works per theme. Prefer the canonical anchor + the one or two recent works that keep the theme
current; push the rest to related-work. Do not let verified-but-peripheral works pad the chapter.
