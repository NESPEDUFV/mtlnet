# _review_v2 — persona review of the corrected build

**Build under review:** `src/dissertacao.pdf` (94 pp) and `src/build/main_final.pdf` (89 pp), both
written 2026-07-25 23:42–23:43, against `src/chapters/*.tex` and `src/references.bib` at the same
timestamp. **Review date:** 2026-07-26.

Nine personas from [`reviewers/`](../../../reviewers/), each run as its own pass with its own report,
under the Common protocol (read-only, fail-closed, fresh eyes, evidence or it did not happen).

## Index

| # | Report | Verdict | BLOCKER | MAJOR | Other |
|---|---|---|:--:|:--:|:--:|
| 04 | [Concordance checker](04_concordance_checker_report.md) | **coherent, two seams need work** | 0 | 2 | 7 |
| 05 | [Citation auditor](05_citation_auditor_report.md) | **GATE FAIL** | **1** | 1 | 2 |
| 06 | [Number auditor](06_number_auditor_report.md) | **GATE PASS** (one MAJOR to rule on) | 0 | 1 | 2 |
| 07 | [Claim & honesty auditor](07_claim_honesty_auditor_report.md) | **GATE PASS** | 0 | 1 | 7 |
| 09 | [Stats & leakage skeptic](09_stats_leakage_skeptic_report.md) | **survives with corrections** | 0 | 2 | 7 |
| 03 | [Style auditor](03_style_auditor_report.md) | **GATE PASS** | 0 | 0 | 7 |
| 15 | [Readability editor](15_readability_editor_report.md) | **7.5 / 10 overall** | 0 | 3 (1 Critical) | 4 |
| 18 | [Visual & presentation](18_visual_presentation_report.md) | **needs a visual pass** | **1** | 3 | 7 |
| 01 | [Cold reader](01_cold_reader_report.md) | **followable; no reader checked out** | 0 | 3 (top-3) | 6 |

**Total: 2 BLOCKER, 16 MAJOR.**

## The two blockers

1. **A cited reference is missing from the bibliography** (05, cross-reported by 18 and 04).
   `russwurm2024geographiclocationencodingspherical` is cited four times and absent from the
   rendered reference list; it renders as `(??)` on defense pp. 21, 45, 49, 50 (final build
   pp. 16, 40, 44, 45). Cause: a bare `@misc` inside the LaTeX comment at `references.bib:831` is
   parsed by BibTeX as an entry start, so the real entry at `:849` is skipped
   (`build/main.blg`: "I was expecting a `{' or a `('---line 831"). The entry's content is correct
   and independently verified against arXiv and OpenReview; only the neighbouring comment breaks
   the build. Arithmetic confirms a single dropped entry: 98 cite keys, 97 `\bibitem`s.

2. **Figure 2 is labeled in Portuguese in the English-frame chapter** (18). Page 48:
   `Encoder Espacial`, `Encoder Temporal`, `Encoder Categórico`, `Coordenadas (lat, lon)`,
   `Timestamps (hora, dia)`, `Categorias (POI graph)` — under an English caption, in a chapter whose
   preface declares it a translated reproduction.

## Correction round: what the audit confirms

| Claim | Status |
|---|---|
| Two overfull boxes gone | **CONFIRMED** — 0 overfull hboxes in the current logs (the 2 in the stale root `main.log` predate the round) |
| Two shrunken Ch.5 tables now legible | **CONFIRMED by measurement** — Tables 8, 9 and 10 all render at **11.96 pt**, full body size (previously 8.13 and 8.00 pt) |
| No table renders before its introducing heading | **CONFIRMED** — all 22 floats mapped to render page vs first reference |
| Wilcoxon-vs-*t* sentence fixed | **CONFIRMED** (09) — the floor is stated numerically, the departure declared, and the registered per-fold n = 20 Wilcoxon now actually run and reported (20/20 folds at all six datasets) |
| Representation-integrity paragraph honest | **CONFIRMED** (07, 09) — all four grounds trace exactly to source, including leak-sniff values to four decimals; the paragraph volunteers its own counter-evidence |
| Freeze-control restatement honest | **CONFIRMED** (09) — comparand named, time-indexed, single-seed footing stated in Ch.5 |
| Inferential unit (n = 4 / 20 fitted models) propagated | **CONFIRMED** (04, 06) — identical at all four sites |
| Conclusão Geral verdict qualified | **CONFIRMED** (07) — Arizona never upgraded at any of six sites |
| No floats-only page | **FAILS** (18) — page 71 is floats only |
| No float splits a sentence | **FAILS** (18, 01, 15) — Table 10 + Figure 7 split the §5.6.2 argument across pp. 70→72 |
| Edit pass did not compress variance (WRITING_LAW §4.3) | **CONFIRMED by measurement** (03, 15) — the most-edited chapters have the *highest* sentence-length dispersion (Ch.6 CV 0.640, Ch.5 0.497) against the barely-edited paper chapters (0.414, 0.424) |

## Note on the stated build state

The task brief records "0 errors, 0 undefined refs/cites". The current logs do not support that:
`build/main.log` carries four `Citation ... undefined` warnings plus "There were undefined
references", and `build/main.blg` carries one error. Reported as measured, per fail-closed.

## Where the personas disagree

Recorded, not resolved — the author rules.

1. **The four-grounds paragraph (`5_mobiwac.tex:367`).** Persona 09 calls it the round's strongest
   work and warns against editing its defenses away. Personas 15 (Critical) and 01 (top-3) call it
   the document's worst readability failure at 546 unbroken words. **Both are right and they are
   not in conflict:** the recommendation from 15 is break-insertion with zero words changed, which
   09's concern does not touch. Flagged because a careless application of 15's finding could damage
   what 09 is protecting.

2. **Chapter 6's opening sentence.** Persona 07 records the scope qualification added there as a
   correct and necessary fix. Personas 15 (Major) and 01 (C-05) report the resulting 110-word
   sentence as the hardest sentence in the document. The correction and the readability cost came
   in the same edit.

3. **Chapter 2's semicolon lists.** Persona 03 counts five sentences crossing the braid threshold
   and proposes a law exemption for parallel clause lists; persona 15 does not flag them as reading
   problems. Disagreement is about whether the law's mechanical threshold is right, not about the
   text.

4. **Chapter 3's adverb density (1.69%, double the band).** Persona 03 measures it and explicitly
   declines to recommend a fix (reproduced published prose under the errata policy); persona 15
   registers Chapter 3's register as an audible seam but judges the prefaces adequate cover. Neither
   asks for a change; recorded so a later pass does not "fix" it on the number alone.

5. **TOST.** The cold readers report it as never expanded; verification shows it **is** in the List
   of Abbreviations (p. 9). Persona 01 reframed this as a distance problem (first use p. 3,
   mechanics p. 67) and rejected the original claim. Recorded as an example of a stumble that was
   real friction but a false defect.

## Cross-cutting findings (raised independently by three or more personas)

- **The `(??)` renders** — 05 (root cause), 18 (page defect), 04 (L4 failure), 01 ("stopped me hard").
- **Page 71 floats-only / the split argument** — 18 (measurement), 15 (reading break), 01 (lost thread).
- **The fixed-partition caveat is in Ch.1 but not Ch.5** — 09 (MAJOR, the statistical consequence),
  04 (MAJOR, the concordance seam).
- **Table 9's column ≠ Table 10's column** — 04 (seam), 15 (reader stop), 06 (verified both trace
  correctly; the distinction is real and stated once, 27 lines from where it is needed).

## What holds — do not edit these away

Consolidated from all nine reports:

- The honesty sentences of Ch.5 (`"We report this attribution as a finding, not a hypothesis."`;
  `"It does not follow that the bias cancels exactly."`; `"At Arizona, the interval is centered on
  zero, so we report a match, not a gain."`) — named as strengths by 07, 09 and 15.
- The self-undercutting evidence in the fourth ground (one encoder passed the linear screen and
  leaked under a sequence model) — 07, 09.
- The Alabama deficit stated plainly inside an equivalence claim — 07, 09.
- The Ch.3 preface's task-name bridge and the Ch.4 protocol declaration — 04, 15.
- Table 9's coincidence footnote — 04, 15.
- Chapter 6's consolidated-answer parallel structure and closing line — 01, 15.
- Zero em-dashes, zero contractions, zero repo codenames, zero registry violations — 03.

## Verification base

Numbers traced to `docs/studies/closing_data/` (RESULTS_BOARD, joint_best, v17_completion incl.
STATISTICAL_PROTOCOL and stats_n20), `docs/studies/pre_freeze_gates/A4_RESULTS.md`,
`docs/results/embedding_eval/rescreen_cat/` (incl. the leak-sniff CSVs),
`docs/studies/closing_data/archive/findings/W6_ENCODER_ISOLATION.md`, and
`docs/results/closing_data/capacity_matched_stl_cat/`. Citations checked against Crossref and the
arXiv API this session (38 of 99 entries, 100% of those the round touched). Font sizes and float
placement measured on the rendered PDF via pypdfium2, not eyeballed.

**Twelve DOI-less proceedings entries were not independently resolved** and are listed as
UNVERIFIED in report 05; five numerals could not be traced to a source file and are listed as
UNVERIFIED in report 06. Both are fail-closed disclosures, not clearances.

## Method deviation (report 01)

The cold-reader pass could not be run by this reviewer: the boot sequence required reading the
project's governing documents, which disqualifies the reader by that persona's own rule. The first
pass was delegated to seven uncontaminated readers given only the rendered page text, and every
quoted stumble was verified against the document before admission — three claimed stumbles were
rejected as reader error. Disclosed in full at the head of report 01.


---

<!-- estado-rodada -->
> **Rodada encerrada · último toque 2026-07-26 · sem autoridade.**
> Este ficheiro é registo de proveniência do que foi discutido nesta passagem, não fonte
> de um facto corrente. O que ficou decidido está em [`VEREDITOS.md`](../../../VEREDITOS.md);
> os valores entregues estão em `CLAUDE.md` §0.1. Não copie nada daqui sem confirmar lá.
