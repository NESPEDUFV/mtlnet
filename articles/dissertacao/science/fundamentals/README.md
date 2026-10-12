# Fundamentals (Chapter 2) — consolidated reference base and section maps

> **2026-09-30:** os rascunhos `.tex` desta pasta sairam da arvore -- eram uma copia superada do texto entregue, com numeros de outra geracao. Os ledgers de citacao (`*_citations.md`) ficam. Tudo recuperavel na tag `dissertacao-pre-organizacao` do PoiMtlNet.

> **⏸ FROZEN 2026-07-24 — IMPORTED into `../../../../src`.** The five section files + the model-lineage
> table drafted here were inlined into the assembled v1 at `../../src/chapters/2_fundamentals.tex`
> (Phase 3). **`../../../../src` is now the single working copy** (single-source rule, CLAUDE.md §1). Do NOT
> edit the section files here to change the dissertation text — edit `src/chapters/2_fundamentals.tex`
> and rebuild. This folder is kept as the provenance record (reference base, section maps, gate
> reports, `_bib/new_references_ch2.bib`) of how Ch.2 was built.
>
> **ONE FILE WAS ADDED AFTER THE FREEZE, and the exception is deliberate: `DEFINITIONS.md`** (2026-08-03,
> at the author's instruction). It does not violate the single-source rule, because it is not chapter
> text: it is the consolidated design for the chapter's numbered Definitions, produced after the author
> found a forward dependency among them, and it is gated behind six decisions of his. The chapter itself
> is still edited only in `../../src/chapters/2_fundamentals.tex`. When the design is applied there, this
> file becomes provenance like the rest of the folder.

This folder consolidates the grounded, fail-closed literature review for Ch. 2. It is organized by the chapter's
own sections. Everything here is verification output and planning material; **no chapter prose is drafted yet**
(the author approves before any section is written).

## Layout
```
fundamentals/
├── README.md                         <- this file
├── DEFINITIONS.md                    <- the twelve (or thirteen) numbered Definitions, consolidated
│                                        and validated. ADDED 2026-08-03, after the freeze, on the
│                                        author's instruction. A DESIGN document: six decisions gate
│                                        its application and nothing in it is in `src/` yet.
├── GAP_STATUS.md                     <- verdict on the 8 structural gaps (start here)
├── model_lineage_table.md            <- DGI -> HGI -> MTLnet -> ST-MTLNet -> Check2HGI -> joint model
├── 2.1_poi_prediction_tasks/         <- 2.1_citations.md
├── 2.2_representations_for_mobility/ <- 2.2_citations.md  (the chapter's spine; static->contextual hinge)
├── 2.3_multi_task_learning/          <- 2.3_citations.md
├── 2.4_datasets_and_evaluation/      <- 2.4_citations.md + 2.4_metrics_addendum.md (Δm, floors, OOD, imbalance)
├── 2.5_relevance/                    <- 2.5_relevance_plan.md (synthesis; NO fresh citations)
├── _bib/                             <- new_references_ch2.bib, new_references_frontier_decollided.bib, BIB_NOTES.md
└── _verification/                    <- VERIFICATION_NOTES.md, SEARCH_PROVENANCE.md
```

## Reading order
1. **GAP_STATUS.md** — what was closed and what still needs the author.
2. The four **2.x_citations.md** — the works to cite per section, in argument order, each with the sentence it supports.
3. **2.4_metrics_addendum.md** — the project's real metrics (Δm etc.) with defensive definitions.
4. **2.5_relevance_plan.md** + **model_lineage_table.md** — the synthesis section and the lineage table.
5. **_bib/** and **_verification/** — the bibliography and the audit trail.

## Ground rules honored
- Fail-closed citation protocol (identifier + opened record + located claim, else [VERIFY]).
- Canonical task vocabulary kept distinct: next place / next category / next region / category classification.
- Fundamentals ≠ frontier: frontier material routed to related-work / future-work.
- Repo codenames translated to canonical prose; no numbers invented (repo counts quoted from docs/context).

## Open items for the author
See `OPEN_QUESTIONS.md` (companion file) and GAP_STATUS gap #5 (errata are author-applied).
