# Exemplar-baseline calibration — assembled v1 vs. three Locus dissertations (2026-07-24)

> **What this note is now.** It began as a lightweight Phase-8 re-check; it is rewritten here into
> a real exemplar-baseline analysis. The three renowned/relevant UFV PPGCC dissertations the
> Phase-0b survey (`locus_calibration_2026-07-23.md`) had only *indexed* were **downloaded and read
> this session**; every claim below about an exemplar is something seen in its PDF this session,
> with page numbers. The PDFs and their PROVENANCE.md files live under `exemples/{canesche, passe,
> lapsusvgi}/`. This note is the deposit the survey pointed to when it said "the Locus record
> resolves it."
>
> **Scope guard.** The settled decisions in `CLAUDE.md §2` / `NORTH_STAR §5` (numeric bib,
> coletânea layout, Germano tree as base, EN frame, CoUrb full EN chapter) are NOT reopened here.
> Improvements below are ledger-compatible polish; anything that would touch a settled decision is
> flagged **AUTHOR DECISION — not folded**. No `src/` file was edited by this analysis.

## The three exemplars (verified this session)

| Exemplar | Identity (page-verified) | Format | Citations |
|---|---|---|---|
| **Canesche 2021** (`canesche/canesche_2021.pdf`, 2.69 MB, 108 pp) | Michael Canesche, *Algoritmos de Posicionamento e Roteamento… (CGRA)*, UFV PPGCC, adv. Ricardo dos Santos Ferreira, defended 19 Feb 2021 (p.1, p.3, p.7) | Coletânea, declared §1.6 (p.20) | ABNT author-year (p.32, p.97) |
| **Passe 2020** (`passe/passe.pdf`, 2.43 MB, 68 pp) | Fernando Ferreira Passe, *Ferramentas de Ensino com Grafos de Fluxo de Dados…*, UFV PPGCC, adv. Ricardo dos Santos Ferreira, defended 23 Jul 2020 (p.1, p.3, p.7) | "Modelo de artigos", declared §1.3 (p.18) | ABNT author-year (p.60) |
| **"LapsusVGI" = Dorigueto** (`lapsusvgi/lapsusvgi.pdf`, 3.48 MB, 77 pp) | Lucas Fouraux Dorigueto, *Um framework para… gerenciamento de informações de desastres… deslizamento de terra*, UFV, adv. Jugurta Lisboa Filho. **Date inconsistent in source**: approval p.3 "14 de maio de 2020"; ficha p.2 and Resumo p.6 both "2021" (likely defense 2020 / deposit 2021) | Coletânea, declared §1.2 (p.14); explicit "2 ARTIGOS CIENTÍFICOS" TOC part (p.10) | ABNT author-year |

> ⚠ **Identity flag (also in `exemples/lapsusvgi/PROVENANCE.md`).** The task brief and the survey
> both attached the label "LapsusVGI / award-winning / English title / SBGames CTD 2020" to the
> bitstream `9c313234-…`. The file at that URL is **Dorigueto's landslide-VGI framework
> dissertation** (PT title, adv. Jugurta Lisboa Filho, GeoInfo) — it matches survey entry **#3**
> (the "ARTIGOS CIENTÍFICOS" precedent), **not** survey entry **#4** (Rubens Moraes Filho,
> *Asymmetric Action Abstractions…*, the English-title SBGames award-winner). The download is
> correct for the URL; the two survey rows were conflated. If the author wants the true
> English-title / SBGames award exemplar, that PDF still needs its Locus bitstream located.

## What each exemplar does right

### Canesche 2021 — the award-grade skeleton match
- **Front matter, complete and in order** (verified pages): folha de rosto (p.1) → ficha
  catalográfica (p.2) → **folha de aprovação** with `APROVADA: 19 de fevereiro de 2021` +
  `Assentimento:` + author and advisor signature lines (p.3) → Resumo (p.7) → Abstract (p.8) →
  Lista de Figuras (p.9) → Lista de Tabelas (p.12) → Sumário (p.13).
- **Catalog-header Resumo/Abstract**: `CANESCHE, Michael, M.Sc., Universidade Federal de Viçosa,
  fevereiro de 2021. <título>. Orientador: …` verbatim (p.7), mirrored in English on p.8. Keywords
  are **period-separated**: `Palavras-chave: Arquiteturas Reconfiguráveis. CGRAs. Posicionamento.
  Roteamento.` (p.7); `Keywords: Reconfigurable architecture. CGRAs. Placement. Routing.` (p.8).
- **Coletânea declared explicitly** (§1.6, p.20): "Esta dissertação está estruturada conforme o
  formato de coletânea de artigos científicos normalizado pelo Conselho Técnico de Pós-Graduação
  da Universidade Federal de Viçosa… introdução geral… capítulos provindos de artigos… conclusão
  geral."
- **A dedicated Background chapter** (Ch.2 "Background" / "referencial teórico", heading on viewer
  p.22) — a direct precedent for a shared Fundamentals chapter inside a coletânea.
- **Per-article contributions as bullet lists inside the introduction** (§1.6, p.21): each
  article chapter is previewed with its headline result and a "As contribuições desse artigo
  foram:" bullet list (e.g. "10x… mais rápida", "83.4x e 19.4x mais rápida").
- **A general Conclusão** chapter (Ch.6, heading on viewer p.94) closing the collection, followed
  by one global "Referências Bibliográficas" (viewer p.97).
- **Mixed-language coletânea**: PT frame, PT background, but the article chapters (Ch.4, Ch.5) run
  in English (Sumário, p.13–14: "Experimental Results", "You Only Look Twice…").

### Passe 2020 — the coletânea-without-general-conclusion counterexample
- Same UFV front-matter spine (folha de rosto p.1; folha de aprovação `APROVADA: 23 de julho de
  2020` + signatures p.3; catalog-header Resumo p.7; period-separated keywords p.7).
- **"Modelo de artigos" declared** in §1.3 (p.18): "Esta dissertação está organizada no modelo de
  artigos."
- **Names each article's publication venue inline** as it introduces the chapter (§1.3, p.18):
  IJCAE; "XXI Simpósio em Sistemas Computacionais de Alto Desempenho"; "Mind the Gap".
- **No general-conclusion chapter**: the collection ends at the last article (Ch.4) + Referências
  (p.59); each article chapter carries its own close ("2.5 Considerações Finais", "3.5
  Conclusion"). This is the useful contrast — a Conclusão Geral is *common* (Canesche, Viegas,
  Germano) but not universal in the program.
- **Mixed-language coletânea**: PT frame + one English article chapter ("3 Mind the Gap: Bridging
  Verilog and Computer Architecture", Sumário).

### Dorigueto 2021 ("LapsusVGI") — the visible "ARTIGOS CIENTÍFICOS" part + PT/EN companion articles
- **An explicit part heading in the TOC** (p.10): `2 ARTIGOS CIENTÍFICOS`, holding `2.1 ARTIGO I`
  (Portuguese, GeoInfo 2020) and `2.2 ARTIGO II: A Framework for Landslide Information Management
  Systems Development` (English) — the second article is a same-content English companion of the
  first.
- **Coletânea declared** in §1.2 "Organização da Dissertação" (p.14): "Essa dissertação foi
  elaborada como uma coletânea de artigos produzidos durante a pesquisa."
- **Carries a Lista de Abreviaturas/Siglas** (p.9) — the only one of the three that does.
- Standard UFV front matter (ficha p.2; folha de aprovação `APROVADA: 14 de maio de 2020` +
  signatures p.3; catalog-header Resumo p.6).

## Comparison table — exemplar device → is v1 doing it? → improvement

| Device (where seen in exemplars) | In assembled v1? | Concrete note |
|---|---|---|
| Folha de rosto (all 3, p.1) | **Yes** — `\imprimirfolhaderosto`, defense build | Matches. |
| **Folha de aprovação** with `APROVADA:`/`Assentimento:`/signature lines (all 3, p.3) | **Partial** — a *bracketed text* placeholder (`0_main.tex` 161–168), no page model | **IMPROVEMENT #1 (see below).** The Germano tree already ships `pdfs/Modelo-pgs-de-assinaturas.pdf`; the base tree includes it via a commented `\includepdf`. |
| Ficha catalográfica (all 3, p.2) | **Absent by design** | Correct: BBT-generated post-deposit; UFV_COMPLIANCE §2 says it is "neither counted nor numbered" and the final upload omits it. Optional defense-build parity page available (`ficha-catalografica-branca.pdf`) — IMPROVEMENT #2, minor. |
| Catalog-header Resumo/Abstract (all 3, p.6–8) | **Yes** — verbatim in both, PT + EN | Matches; v1 renders both (exemplars each render one language's header per abstract). |
| Keywords **period-separated** in the deposited Resumo/Abstract (all 3 + Viegas) | **Diverges** — v1 uses **one-per-line** in both builds | **AUTHOR DECISION — not folded (see below).** |
| Coletânea/"modelo de artigos" declared in the intro (all 3: Canesche §1.6, Passe §1.3, Dorigueto §1.2) | **Yes** — §1.5 "Organization of this dissertation" (Viegas magic sentence) | Matches. |
| Article chapters named by article title (Passe, Dorigueto) | **Yes** — `\chapter[short]{full}` per article chapter | Matches, with short TOC forms. |
| Per-chapter venue/status statement (Passe §1.3 inline; Dorigueto §1.2) | **Yes, and exceeds** — every article chapter opens a `chapterpreface` giving venue + DOI + status + authorship **plus** a "conclusions of the time" caveat and pointers to which later chapters revise it | v1 is **ahead** of the exemplars here; no exemplar carries the honesty/revision caveat. |
| Per-article contributions previewed in the intro (Canesche §1.6 bullets) | **Yes, differently** — the §1.2 arc narrates each chapter's finding with headline numbers; §1.5 gives a four-group contributions taxonomy (Viegas device) | Covered; no need to duplicate Canesche's bullet form. |
| Dedicated Background/Fundamentals chapter inside the coletânea (Canesche Ch.2) | **Yes** — Ch.2 Fundamentals (5 sections, ~559 lines), closes with the "pressing need" hinge | Matches; Canesche is a second in-program precedent beyond Germano/Viegas. |
| General Conclusão chapter (Canesche Ch.6, Viegas, Germano; Passe has none) | **Yes** — Ch.6 Conclusion | Matches the majority pattern; Passe shows it is not strictly mandatory, but the award-grade Canesche keeps it. |
| One global bibliography, ABNT author-year (all 3) vs. numeric (Viegas) | **Numeric** — settled decision #5 | Author-year has program precedent (all 3 here) and numeric has program precedent (Viegas); **no conflict**, decision #5 stands. |
| Lista de Siglas/Abreviaturas (Dorigueto p.9; Canesche/Passe omit) | **Yes** — `\begin{siglas}` from GLOSSARY §5 | Matches; Dorigueto corroborates acceptance, the other two show optionality. |

## Ledger-compatible improvements to fold into the build

Only two, both **front-matter polish for the defense build**, both realizable with the Germano
tree's own assets, neither touching a settled decision:

1. **Replace the bracketed-text approval placeholder with the official PPG signature-page model.**
   v1 currently prints a `[Approval sheet placeholder …]` text block (`src/0_main.tex` 161–168).
   All three exemplars (and Germano) render a real folha de aprovação. The Germano tree already
   contains `exemples/germano/…/pdfs/Modelo-pgs-de-assinaturas.pdf` (the PPG model, 429 KB), and
   Germano's own `0_main.tex` includes it via a commented `\includepdf[pages=-]{pdfs/Modelo-pgs-de-assinaturas.pdf}`.
   Folding: copy that PDF into `src/` and swap the text placeholder for the `\includepdf`, guarded
   to the defense build. Effect: the defense PDF shows the real signature page the banca expects;
   the signed scan replaces it afterward. Uses the Germano machinery (settled base), changes no
   ledger decision. *(Recommendation only — not applied; `src/` edits are the author's.)*

2. **(Minor) Optional blank-ficha parity page in the defense build.** The Germano tree ships
   `pdfs/ficha-catalografica-branca.pdf` (99 KB). Including it (defense build only) makes the
   defense PDF visually match the deposited exemplars, which all carry a ficha on p.2. This is
   cosmetic parity, not a compliance need — the real ficha is BBT-generated post-deposit and the
   final AcademicoPG upload omits it. Fold only if the author wants the defense PDF to look like a
   finished deposit; otherwise leave as-is (current behavior is compliant).

## Flagged — AUTHOR DECISION, not folded (would diverge from an exemplar or a source rule)

- **Keyword punctuation in the defense-build Resumo/Abstract.** Every deposited exemplar
  (Canesche p.7–8, Passe p.7–8, Dorigueto p.6, and Viegas) prints keywords **period-separated on
  one line** (`A. B. C. D.`). v1 prints them **one per line** in *both* builds, citing
  UFV_COMPLIANCE §2. That §2 rule ("keywords one per line, lowercase except proper nouns, no
  punctuation") is explicitly the **AcademicoPG system-field** rule, not a rule for the defense
  PDF's typeset Resumo/Abstract page. So for the *defense* build there are two defensible choices:
  keep one-per-line (internal consistency with the final system fields) or switch to
  period-separated (visual match to every deposited program exemplar). This does not conflict with
  any settled ledger decision, but it is a formatting judgment the author should make; it is not
  folded. *(No conflict with settled decisions; purely the author's style call.)*

## Bottom line

The assembled v1 is at or above the exemplar baseline on every structural device checked. The
exemplars mostly **confirm** its settled choices (coletânea declaration, catalog-header
Resumo/Abstract, dedicated Fundamentals chapter, Conclusão Geral, global bibliography, Siglas
list) and add two program-specific precedents worth recording:

- **Mixed-language coletâneas pass at UFV PPGCC.** Both Passe (PT frame + one EN article chapter)
  and Dorigueto (PT ARTIGO I + EN ARTIGO II companion) are accepted mixed-language collections in
  this exact program. This strengthens the settled EN-frame + CoUrb-translation decision and
  corroborates UFV_COMPLIANCE's reading that mixed language is legal (§2.6.3): translating CoUrb is
  a style choice, not a compliance requirement.
- **A general Conclusão is common but not universal** (Passe has none), so v1's Ch.6 is a
  strengthening choice, not a mandate — worth knowing if space ever gets tight.

The only build-facing action items are the two front-matter polish items above (approval-page
model; optional ficha parity page). Everything else is corroboration.

## Source ledger (each exemplar → identifier → where opened → claim it supports)

| Exemplar | Identifier / URL | Opened this session | Claims it supports here |
|---|---|---|---|
| Canesche 2021 | Locus bitstream `4e3ceb9d-6762-4e5c-ba44-c61d3f6c80ea` → `exemples/canesche/canesche_2021.pdf` | Yes — viewer pp.1,2,3,7,8,9,12,13,14,20,21,22,32,94,97 read/rendered | folha de aprovação device (p.3); catalog-header + period keywords (p.7–8); coletânea declaration §1.6 (p.20); Background chapter Ch.2 heading (p.22); per-article contribution bullets (p.21); Conclusão Ch.6 heading (p.94); ABNT author-year (p.32,97); mixed-language chapters (Sumário p.13–14) |
| Passe 2020 | Locus bitstream `f5f5d30d-5fde-4147-b97e-66d75fcbe164` → `exemples/passe/passe.pdf` | Yes — pp.1,3,7,8,11,12,18,59,60 read/rendered | front-matter spine + folha de aprovação (p.3); catalog-header + keywords (p.7); "modelo de artigos" + inline venues §1.3 (p.18); no general conclusion (Sumário p.12, Referências p.59); EN article chapter |
| Dorigueto 2021 ("LapsusVGI") | Locus bitstream `9c313234-82cf-44b0-b645-ee2659470be8` → `exemples/lapsusvgi/lapsusvgi.pdf` | Yes — pp.1(cover, image),2,3,4,5,6,8,9,10,14 read/rendered | ficha (p.2); folha de aprovação (p.3); catalog-header Resumo (p.6); Siglas list (p.9); "ARTIGOS CIENTÍFICOS" TOC part + PT/EN companion articles (p.10); coletânea declaration §1.2 (p.14); **identity discrepancy vs. brief** |
| (baseline) v1 assembled | `src/0_main.tex`, `src/chapters/{1_introduction,2_fundamentals,3_cbic,4_courb,5_mobiwac}.tex` | Yes — front matter + intro + chapter prefaces read | every "in v1?" cell in the comparison table |

The Dorigueto bitstream URL is the survey's `9c313234-82cf-44b0-b645-ee2659470be8`; that is the
value downloaded and verified this session (77 pp, ficha names Dorigueto) — provenance in
`exemples/lapsusvgi/PROVENANCE.md`.

## [VERIFY] flags

- **[VERIFY — author]** The "LapsusVGI/SBGames/English-title/award" descriptors do **not** match
  the downloaded file; they belong to Rubens Moraes Filho's dissertation, whose Locus URL was
  never captured. Decide whether to locate that PDF or drop the descriptor.
- **[VERIFY — author]** Canesche's CTD-SBC top-10 + WSCAD-CTD prize status is from the Phase-0b
  web survey (PPGCC awards page), **not** re-verified from the PDF this session. The PDF is a
  genuine repository copy; the *award* claim rests on the earlier survey.
- **[VERIFY — author]** Dorigueto's date is inconsistent *inside its own PDF*: the folha de
  aprovação (p.3, re-rendered at 4x this session) says defended 14 May 2020, but the ficha (p.2)
  and Resumo header (p.6) say 2021. This is a defect in the source document, not a transcription
  error here; cite the relevant page and note the conflict. It has no bearing on any v1 decision
  (the exemplar's value is structural), but it is why the note stops calling the file "Dorigueto
  2021" flatly.
- No fabricated identifiers were introduced. All three PDFs opened, carry valid `%PDF` headers,
  and their page-1 / ficha identities were read this session (see each PROVENANCE.md).
