# TEMPLATE.md — LaTeX base decision + adaptation checklist

> Decision record from the 2026-07-18 template survey (GitHub/CTAN/Overleaf/official pages, all
> API/HTTP-verified). Bottom line: **do not use the template the author found first**
> (ViniciusBRodrigues/TeseUFVLatex — abandoned 2018/2019, non-compliant with the current manual);
> use its 2024 derivative — OR, since 2026-07-20, the in-lab proven tree below.

## 0 · NEW OPTION (2026-07-20): the Germano tree — an in-lab, defended precedent with source

The author added [`exemples/germano/`](exemples/germano/): the **full working LaTeX source** of
Germano Barcelos dos Santos's dissertation (*Urban Region Representation Learning*, PPGCC
Florestal **2024, same advisor, English body, defended**) — built on UFVMastersTemplate2021
(abnTeX2 + `abntex2-UFV.sty`), paper-per-chapter shaped, with the UFV front matter
(assinaturas/ficha placeholders) already solved.

**Revised recommendation: start the skeleton from the Germano tree** — proof of acceptance at
the exact program with the exact advisor outweighs LucasBraganca's simplicity. Required deltas
(all verified against `0_main.tex`):
1. Font: `lmodern` → Times (`newtxtext,newtxmath`; abnTeX2/memoir tolerates it) — manual §8.
2. Citations: it uses `abntex2cite [alf]` (author–year ABNT) — **switch to the settled
   Viegas-style numeric global scheme** (abntex2cite `[num]` variant, or drop to natbib
   numeric); verify the References heading tweaks in its babel block survive.
3. Margins / page-number position / numbering start: **measure against UFV_COMPLIANCE §2**
   (the 2014-lineage `abntex2-UFV.sty` may carry pre-manual geometry — fix in the .sty if so).
4. The two-build toggle (§3 of this file / checklist item 4) still must be added — abnTeX2's
   front matter becomes the defense build; the AcademicoPG build strips it.
5. Strip Germano's content/macros (`\modelname`, his colors), keep the machinery.

LucasBraganca (§1 below) remains the **fallback** if abnTeX2 fights the two-build split or the
numeric-citation swap — its checklist is unchanged. Decide within the Day-1 skeleton half-day:
timebox the Germano route to ~2 hours of compliance checks before committing.

## 1 · Verdict (2026-07-18 survey — now the fallback path)

**Base: [LucasBraganca/ModeloLatexTeseUFV](https://github.com/LucasBraganca/ModeloLatexTeseUFV)**
(last push 2024-04-09; README: "atualizado de acordo com o novo manual de trabalhos acadêmicos da
UFV (BBT)"; Overleaf-tested). Out of the box it already satisfies 4 of the 6 mandatory 2025/2026
rules: A4 + margins `left=3cm, top=3cm, right=2cm, bottom=2cm`; 12 pt `report` class; page number
**top-right** via fancyhdr; body in `onehalfspacing`. Remaining work: font swap
(Palatino→Times), front-matter restructuring for the two builds, and the coletânea chapter
layout. Estimated effort: **~1 day + one AcademicoPG draft iteration**.

Why not the alternatives:

| Option | State | Blockers |
|---|---|---|
| ViniciusBRodrigues/**TeseUFVLatex** (= CTAN `ecothesis` v1.2, 2018) | Abandoned (content frozen 2019-07-01) | Old print-era margins (4/3/2.8/2.5 cm), page numbers in the FOOTER, pagination restarts at 1 after the abstract, Palatino. Its one asset: working `chapterbib` per-chapter bibliography wiring — usable as a donor if per-chapter bibs are chosen. |
| marcelodmmenezes/**UFVMastersTemplate2021** (abnTeX2 + UFV .sty) | 2021 | Heavier machinery whose main deliverable (ABNT capa/folha de rosto) the AcademicoPG system now generates; per-chapter bibs awkward under abntex2cite; font swap still needed. Second choice only if ABNT author-date citations are demanded. |
| Official PPGCC templates | Word .docx only (PT/EN) | No official LaTeX template exists; the .docx is the layout reference of record — keep it side-by-side when in doubt. |
| Overleaf gallery | TCC templates only | Nothing for UFV dissertations. |
| Minimal custom `report`-class preamble (~40 lines) | — | Equivalent effort; choose only if zero inherited cruft is preferred. |

## 2 · Adaptation checklist (ordered; tick as done)

1. [ ] Clone/import the base; commit pristine upstream first (clean diff trail).
2. [ ] **Font:** remove `mathpazo` + `\linespread{1.5}`; add `\usepackage{newtxtext,newtxmath}`
       (Times-equivalent, pdfLaTeX-safe). Literal Arial only if the secretariat demands it
       (then XeLaTeX + fontspec).
3. [ ] **Spacing:** `\usepackage{setspace}\onehalfspacing` globally; drop redundant wrappers.
4. [ ] **Two build modes** (one source, a boolean toggle, e.g. `\newif\ifdefensebuild`):
       - *Defense build*: cover page, approval-sheet placeholder, Resumo/Abstract pages (PPG
         model format), lists, sumário, body — the banca's PDF (Viegas shape).
       - *Final build*: front matter suppressed; PDF starts at the lists → sumário → body
         (UFV_COMPLIANCE §1); `\thispagestyle{empty}` on every pre-body page;
         `\setcounter{page}{K}` at the introduction, K tuned against the system's RASCUNHO PDF.
5. [ ] **Coletânea structure:** chapters = Introduction (Introdução Geral) / Fundamentals /
       Article 1..3 / Conclusion (Conclusão Geral); `\include` per chapter; chapter-preface
       environment (italic, one paragraph: venue, status, contribution note — NORTH_STAR §3).
6. [ ] **Bibliography — SETTLED (decision #5): single global, Viegas-style** (natbib numeric,
       one consolidated list, blue hyperlinked cites). No chapterbib. Create `references.bib`
       now, seeded from the MobiWac verified entries (AGENT_GUARDRAILS R1); add the two
       dissertation-composing DOIs (CBIC `10.21528/CBIC2025-1191324`, CoUrb
       `10.5753/courb.2026.22960`).
7. [ ] **Floats:** table captions ABOVE, figure captions BELOW (fix the Viegas inconsistency);
       booktabs everywhere; subcaption for (a)/(b) pairs; algorithm2e if pseudocode is used.
8. [ ] **Hyperref:** colorlinks (blue cites/refs like Viegas), pdf metadata (title/author),
       `\listoffigures`, `\listoftables`, abbreviations list (include our coinages: MTLnet,
       ST-MTLNet, Check2HGI, HGI, DGI, MTL, STL, POI, LBSN, TOST, …).
9. [ ] **Language plumbing:** `babel` english main + brazilian for PT surfaces (and the CoUrb
       chapter if it stays PT — `\selectlanguage` per chapter).
10. [ ] **Lint hooks:** a `make check` that greps for em-dashes, "this paper" in chapters,
        unresolved `\ref`/`\cite`, banned words (WRITING_LAW §4) — the cheap half of
        AGENT_GUARDRAILS gate G2/G3.
11. [ ] Verify margins with a ruler after the font swap (headheight shifts); keep
        `\setlength{\headheight}{14.5pt}`.
12. [ ] Compare one rendered chapter against the official PPGCC Word EN model + the pre-textual
        checklist; confirm coletânea per-article style questions with the secretariat
        (ppgcc@ufv.br) if per-chapter formats are kept.

## 3 · Figure/asset pipeline

- Reuse the papers' figure sources: MobiWac `src/figs/*.py` (regenerate at dissertation column
  width — the 2-col sizes will not survive re-typesetting), TikZ figures re-compiled inline;
  CBIC/CoUrb figures re-rendered from their sources where available, redrawn (with "adapted
  from" credit) where not.
- Bold the champion/winning row in results tables (Viegas bolds best values); mean ± std via a
  `\sd{}` macro as in the MobiWac sources.
- Any number that appears in LaTeX comes from the sources named in AGENT_GUARDRAILS §2 N1 —
  prefer generating table rows by script into `tables/*.tex` (the MobiWac pattern) over
  hand-typing.


---

<!-- estado-rodada -->
> **Rodada encerrada · último toque 2026-08-20 · sem autoridade.**
> Este ficheiro é registo de proveniência do que foi discutido nesta passagem, não fonte
> de um facto corrente. O que ficou decidido está em [`VEREDITOS.md`](../VEREDITOS.md);
> os valores entregues estão em `CLAUDE.md` §0.1. Não copie nada daqui sem confirmar lá.
