# SEARCH_PROVENANCE — how the review was conducted (feeds the AI-use disclosure appendix)

<!-- GAP_STATUS gap #8. Lighter than PRISMA (this is a coletânea fundamentals chapter), but enough to reproduce
     the search and to populate the mandatory AI-use disclosure (AGENT_GUARDRAILS §6). Dates: this session. -->

## Databases and tools
- **OpenAlex** (works + venue metadata) — primary discovery + attribute confirmation.
- **arXiv** (batch metadata) — preprint identifiers and author/date confirmation.
- **Crossref / publisher landing pages** — source-of-record for final attributes (DOIs, pages, venue).
- **Author-provided PDFs** (articles/dissertacao/science/articles/) — firsthand claim location for 6 works.
- **Repo internal docs** (docs/context/*) — the project's own conventions and counts (quoted, not recomputed).

## Inclusion rule
A work enters Ch.2 only if it is (a) a canonical anchor a computing banca expects for that theme, OR (b) a
directly-used component/method, AND it passes fail-closed verification (resolvable identifier + opened record +
located claim). Frontier / state-of-the-art-beyond-fundamentals works are EXCLUDED from Ch.2 and routed to the
paper chapters' related-work / future-work.

## Per-theme provenance (STEP 1)
| Theme | Verified works | New (not already cited) | Notes |
|---|---|---|---|
| A — POI-prediction tasks + sequence models | 31 | 3 (+2 optional) | Task formulations (next category/region/place, category classification) kept distinct; sequence lineage framed as next-place background. |
| B — Representations for mobility | 24 | 6 | General encoders (Time2Vec/SIREN/Space2Vec/Sphere2Vec/FiLM) cited at their own origin, per author instruction. HGI claim closed firsthand. |
| C — Multi-task learning | 38 | 7 | Balancer family fully verified; caught 2 wrong DOIs in existing bib; "no prior next-region-as-end-target" gap confirmed. |
| D — Datasets, metrics, evaluation | 17 | 8 (+2 this round) | Added Δm (Maninis 2019) + focal-loss option this round; floors/OOD/selector given defensive definitions. |

## Totals
- Already-cited distinct works (STEP 0): **92** (A40 / B18 / C26 / D8). CoUrb count reconciled to **32** entries.
- New verified references for Ch.2: **26** (24 first round + Maninis + focal).
- Frontier set (routed OUT of Ch.2): **24**, key-collisions disambiguated.
- Global key/DOI collision check against all four existing bibs: **0 / 0**.

## Reproducibility caveats
- OpenAlex abstracts are license-gated for some works; where unreadable, the claim was marked [VERIFY] class B, not
  fabricated. Six such were closed this round from author PDFs.
- Numbers from repo docs (e.g. Food class share ≈32-34%) are quoted from docs/context/TASKS.md, not recomputed.
