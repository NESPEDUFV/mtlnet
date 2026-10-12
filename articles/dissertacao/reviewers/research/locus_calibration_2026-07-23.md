# Locus calibration survey — UFV PPGCC master's dissertations (2026-07-23, pre-skeleton)

> Phase-0b deliverable of the v1 assembly plan (author-requested reordering: survey BEFORE the
> skeleton so the Germano-machinery copy is informed by the wider precedent set). Timeboxed web
> survey; every item below was seen in a live source this session (URLs given). This note feeds
> the Phase-1 skeleton decisions and is re-checked in Phase 8 against the assembled v1.

## What was surveyed

Targets: UFV institutional repository Locus (locus.ufv.br) + the PPGCC pages (ppgcc.ufv.br),
prioritizing renowned dissertations (SBC CTD award-listed) and coletânea-format ones. The two
local exemplars (Viegas 2026, Germano 2024) are held in `exemples/` and were NOT re-surveyed.

## Findings (verified this session)

| # | Dissertation | Evidence seen | Relevance |
|---|---|---|---|
| 1 | **Michael Canesche**, "Algoritmos de Posicionamento e Roteamento baseados em Travessia de Grafo para Arquiteturas Reconfiguráveis de Grão Grosso (CGRA)", UFV PPGCC 2021, advisor Ricardo Ferreira | PPGCC awards page: top-10 CTD-SBC 2022 + WSCAD-CTD 2022 prize (ppgcc.ufv.br/publicacoes/). Full PDF on Locus (locus.ufv.br bitstream 4e3ceb9d-...): chapters with per-chapter contributions, closing "conclusão geral e trabalhos futuros" chapter; Resumo carries the UFV catalog header ("CANESCHE, Michael, M.Sc., Universidade Federal de Viçosa, fevereiro de 2021. ... Orientador: ..."); citations are ABNT author-year ("Chin et al., 2017a"). | The award-grade calibration point: chapter-per-contribution shape + Conclusão Geral matches our planned skeleton. Its author-year citations show numeric is NOT the only accepted scheme; our numeric decision (ledger #5, Viegas precedent) stands. |
| 2 | **Fernando Ferreira Passe**, "Ferramentas de Ensino com Grafos de Fluxo de Dados em Três Níveis de Abstração", UFV PPGCC (#202 in the program list), advisor Ricardo Ferreira | Full PDF on Locus (bitstream f5f5d30d-...): states verbatim "Esta dissertação está organizada no modelo de artigos"; TOC has "Estrutura da Dissertação". | A coletânea (modelo de artigos) precedent ON Locus for this exact program — the format is established practice, not an exception. |
| 3 | **LapsusVGI dissertation** (UFV PPGCC; DINF; author name not captured in the surveyed excerpt) | Locus PDF (bitstream 9c313234-...): TOC block "ARTIGOS CIENTÍFICOS ..." after the introduction chapter; §1.2 "Organização da Dissertação". | Second coletânea precedent on Locus: a visible "ARTIGOS CIENTÍFICOS" part between Introdução and Conclusão. |
| 4 | **Rubens Moraes Filho**, "Asymmetric Action Abstractions for Real-Time Planning in Extensive-Form Games" | PPGCC news: 1st place, 12º CTD SBGames 2020 (ppgcc.ufv.br/informativo/...). | An award-winning PPGCC dissertation with an ENGLISH title: English-language work has award-grade precedent in the program (supports the settled EN-frame decision, pending advisor sign-off). |

## Consequences for the Phase-1 skeleton (fold-in decisions)

1. **Keep the Germano tree as the base** (TEMPLATE.md §0 decision confirmed): the award-listed
   precedents share its shape (chapters, Conclusão Geral, UFV catalog-header Resumo); nothing
   surveyed suggests a different machinery.
2. **Coletânea layout is standard practice**: two Locus precedents organize as
   Introdução (Geral) -> artigos -> Conclusão Geral, exactly the NORTH_STAR §3 map. No change.
3. **Resumo/Abstract catalog header** (AUTHOR, M.Sc., Universidade Federal de Viçosa, month
   year. Title. Orientador:) is consistent across the surveyed PDFs and the Germano source —
   the Phase-5 front matter must render it exactly.
4. **Citation scheme variance exists** (Canesche = ABNT author-year; Viegas = numeric). The
   settled decision (#5: single global numeric, Viegas-style) does NOT conflict with program
   practice; both schemes have accepted precedent. No reopening.
5. **"Estrutura/Organização da Dissertação" section** at the end of the Introduction is a
   constant across all surveyed works — already planned (Ch.1 §1.5). No change.

## What was NOT found (timebox honored)

- No UFV PPGCC coletânea located with an English FRAME + translated chapter combination; the
  Germano tree (same advisor, EN body, defended 2024) remains the closest precedent for that.
- The LapsusVGI author attribution was not captured before the timebox; the structural evidence
  (TOC) was. If the author needs the name, the Locus record resolves it.
- Locus full-text search UI was not crawled exhaustively; the survey relied on indexed search.

## Sources

- https://ppgcc.ufv.br/publicacoes/ (awards list, seen 2026-07-23)
- https://ppgcc.ufv.br/informativo/dissertacao-de-mestrado-do-ppgcc-e-premiada-em-primeiro-lugar-no-12-concurso-de-teses-e-dissertacoes-do-sbgames-2020/
- https://locus.ufv.br/server/api/core/bitstreams/4e3ceb9d-6762-4e5c-ba44-c61d3f6c80ea/content (Canesche PDF)
- https://locus.ufv.br/server/api/core/bitstreams/f5f5d30d-5fde-4147-b97e-66d75fcbe164/content (Passe PDF)
- https://locus.ufv.br/server/api/core/bitstreams/9c313234-82cf-44b0-b645-ee2659470be8/content (LapsusVGI PDF)
- https://ppgcc.ufv.br/dissertacoesteses/ (program dissertation list)
