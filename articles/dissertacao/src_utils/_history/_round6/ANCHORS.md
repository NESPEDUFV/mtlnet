# ANCHORS.md — every audit coordinate re-resolved against the live build (round 6)

**Written 2026-07-28**, against `src/build/main.pdf` (**104 pp**) and `src/build/main_final.pdf`
(**99 pp**). *Both moved to 105/100 later the same day when the two Chapter 5 diagrams were scaled
to `\textwidth`; the page numbers in the tables below were taken at 104/99 and the three figure
pages (48, 62, 65) were re-confirmed unmoved after the rescale.*, both rebuilt after `ba90aa6d` restored the brace that had stopped `make` from producing
anything since `6d780b58`. `tex_errors=0` on both.

## Why this file exists

`CODEX_AUDIT.md` was written against a 97/92-page pair, re-anchored once to 102/97, and annotated
against 103/98 and 104/99 at different times. `PENDENCIAS.md` cites coordinates from all of those.
**Of the 79 resolvable `file:line` coordinates those two documents cite, 25 now land on a comment
line, a blank line, or past the end of the file.** The findings survive; the coordinates do not.

This file re-resolves the load-bearing ones **by content**, which is the only stable key. Line
numbers below were measured on 2026-07-28 and will drift again; the phrase will not.

## 1 · Sites this round edits

| Item | File | Line (2026-07-28) | Anchor phrase | State |
|---|---|---|---|---|
| COD-003 | `1_introduction.tex` | 158 | "a leakage-guarded statistical protocol" | **open** |
| COD-002 | `1_introduction.tex` | 114 | "Category performance rose sharply" | open (author: no text change; LEFT_OUT.md) |
| NUM-4 | `2_fundamentals.tex` | 172 | "rose monotonically from 0.74 to 0.82" | **open** (spreads dropped) |
| COD-015 (d) | `2_fundamentals.tex` | 437 | "mean reciprocal rank" | **open** (promise unused) |
| COD-015 (d) | `2_fundamentals.tex` | 442 | "the relative multi-task performance change" | **open** (promise unused) |
| COD-007 | `2_fundamentals.tex` | 468 | "stratified by sample rather than by" | present, discloses the gap |
| COD-015 (a) | `3_cbic.tex` | 24 | "revise that verdict by changing the input representation" | **open** |
| COD-008 | `3_cbic.tex` | 214 | `standley2020tasks` at "hard parameter sharing frequently matches" | **open** |
| COD-016 | `3_cbic.tex` | 317 | "unbalanced result for the MTL and single" | **open** |
| COD-005 | `3_cbic.tex` | 242 | "matrix-vector products per iteration" | **already corrected in prose**, see §3 |
| COD-007 | `3_cbic.tex` | 303 | "a 5-fold cross-validation" | **open** (no split axis, seed, budget, checkpoint) |
| COD-008 | `4_courb.tex` | 208 | "negative sampling" | fixed (`mikolov2013negsampling` cited) |
| COD-005 | `4_courb.tex` | 120 | "ensures that the update is beneficial" | **open** (unconditional) |
| COD-009 | `4_courb.tex` | 257 | "pins a single random seed" | scoped correctly |
| COD-015 (c) | `4_courb.tex` | 345 | "February 2009 and October 2010" | published prose, the correct range |
| NUM-7 | `4_courb.tex` | 40, 306, 325, 339 | "better of the two spatial encoders" | disclosed at all Ch.4 sites |
| COD-004 | `5_mobiwac.tex` | 772 | "One model serves both tasks: the joint architecture lifts" | **already softened**, see §3 |
| COD-004 | `5_mobiwac.tex` | 593, 601 | "attribute the gain to the joint architecture", "do not name the shared trunk" | present |
| COD-006 | `5_mobiwac.tex` | 388 | "before any result was read" / "well powered" | **open** (author approved only the second) |
| COD-016 | `5_mobiwac.tex` | 361 | "bounds this channel rather than closing it" | **open** (needs breaks, zero words changed) |
| COD-005 | `5_mobiwac.tex` | 186, 211 | balancer screen | **already scoped**, see §3 |
| COD-009 | `5_mobiwac.tex` | 33 | "No result, claim, or conclusion was altered" | author: leave as is |
| NUM-3 | `6_conclusion.tex` | 177 | "four Gowalla states, three of which are among the five we report" | **already corrected**, see §3 |
| COD-010 | `6_conclusion.tex` | 118 | "56.16" | corrected (three configurations, twenty each, sixty total, SD 1.89) |
| COD-015 (c) | `6_conclusion.tex` | 200 | "collected between 2009 and 2011" | **open** (contradicts Ch.4's published range) |
| NUM-7 | `6_conclusion.tex` | 46 | "20.2" | **open** (per-cell clause absent in the frame) |
| COD-018 | `apx_a_contributions.tex` | 75 | "stratified its folds by sample" | roles still absent |
| COD-013 | `apx_c_ai_disclosure.tex` | 39 | "each reviewer a separate agent (Claude Opus family)" | **open** (name the model) |
| COD-017 | `tables/frame/bib_errata.tex` | 113 | `\end{longtable}` | float warning **gone**, see §2 |

## 2 · Four audit statements that the live build no longer supports

1. **The Appendix B oversized float is gone.** Both logs report **zero**
   `Float too large for page` warnings. The audit measured 21.55853 pt; that measurement was taken
   from a build of the source *before* the longtable conversion, and the conversion fixed it. The
   author's instruction to fix it now is therefore already satisfied; what remains is only to
   re-check after the Resumo rewrite moves pagination.
   > **A different defect appeared in that same table during this round** and is not the float
   > warning: an added bibliography-errata row prints a 52-character `\texttt` key that cannot be
   > broken, giving an `Overfull \hbox` of **113.58371 pt** at `tables/frame/bib_errata.tex:112`.
   > Caught by the figure pass, which had to revert it in an isolated tree to measure its own work.
   > Fixed in this round; the row now names the work rather than printing the key, matching the row
   > above it.
2. **The Ch.5 diagram labels are confirmed, and one page number moved.** Measured font sizes, not
   glyph bounding boxes: body is **11.96 pt**; the two diagrams carry **6.97 and 7.27 pt**, that is
   58 percent of body size, on **pp. 62 and 65**. The audit said pp. 62 and 64. Page 65 is the
   correct second page in this build.
   > **Two corrections to this row, both from the figure pass** (`12_figures.md`). First, my glyph
   > counts of "449 and 427 below 9 pt" include spaces and newlines; excluding them gives **350 and
   > 312** with the same instrument on the same pages. Neither number is wrong, but they are not
   > interchangeable, and the exclusion is the more meaningful count. Second, and more important:
   > **`FPDFText_GetFontSize` reports the size declared inside the embedded XObject and is blind to
   > the `\includegraphics` scale.** It still returns 6.97 pt after the figures were rescaled. The
   > true on-page size has to come from glyph geometry calibrated against the body font on the same
   > page. Measured that way after the fix: `fig2_model` 6.84 → **11.15 pt** (93.2 percent of body),
   > `fig1_dataflow` 6.84 → **7.93 pt** (66.3 percent). So this row's original instrument would have
   > reported no improvement at all.
3. **The near-blank p. 4 is confirmed, precisely.** It carries the `Palavras-chave:` heading and five
   keyword lines, **21 words in total**, and nothing else.
4. **The `[NEEDS SIGN-OFF]` count is 32, not 31.** Measured across `src/`: `0_main.tex` 6,
   `5_mobiwac.tex` 6, `6_conclusion.tex` 6, `apx_a_contributions.tex` 4, `apx_b_errata.tex` 3,
   `1_introduction.tex` 2, `2_fundamentals.tex` 2, and one each in Appendices C, D and E. The audit's
   31 was correct when written; `5_mobiwac.tex` has gained one since.

## 3 · Five items the audit lists as fixable that are already done

Recorded so nobody spends the round redoing them. Each was verified by reading the live prose line.

| Audit item | Evidence it is done |
|---|---|
| §6 item 2, NUM-3 Ch.6 gradient scope | `6_conclusion.tex:177` reads "four Gowalla states, three of which are among the five we report". The "three of the six datasets" wording is gone. |
| §6 item 11, COD-004 trunk attribution | `5_mobiwac.tex:772` reads "the joint architecture lifts the next-category task". The component attribution is gone, and the comment at :775-778 records the change. |
| §6 item 14, COD-005 balancer screen scope | **NOT done, and my first reading of this row was wrong.** I recorded `:186` as naming "the two datasets" by reading "including the two named above" as Alabama and Florida. The Protocol-recovery pass measured it: **neither state is named before `:186`** (the first "Alabama" in the file is `:188`, the first "Florida" is `:210`), and what is named immediately above at `:183` is the two *balancers*, PCGrad and Nash-MTL. So the sentence identifies neither the seed nor the datasets, and the residue is larger than this table first said. See `10_protocol_recovery.md` §2.2. |
| COD-010 capacity sentence | `6_conclusion.tex:118` carries the corrected count, the mean and the SD. |
| COD-005 Nash cost claim | `3_cbic.tex:242` now reads "That cost claim is corrected here rather than reproduced", so the claim is corrected in the chapter, not merely reported in Appendix B. |

## 4 · One orphan the author asked to close

`\label{apx:ethics}` is declared at `apx_e_ethics.tex:8` and referenced **nowhere**. The author asked
for a short pointer from Chapter 1, near the data description.

## 5 · How to cite a coordinate from here on

Cite the **phrase**, and give the line number as of a stated date. A bare `file:line` in a durable
record is a claim with a shelf life of about one commit.


---

<!-- estado-rodada -->
> **Rodada encerrada · último toque 2026-07-28 · sem autoridade.**
> Este ficheiro é registo de proveniência do que foi discutido nesta passagem, não fonte
> de um facto corrente. O que ficou decidido está em [`VEREDITOS.md`](../../../VEREDITOS.md);
> os valores entregues estão em `CLAUDE.md` §0.1. Não copie nada daqui sem confirmar lá.
