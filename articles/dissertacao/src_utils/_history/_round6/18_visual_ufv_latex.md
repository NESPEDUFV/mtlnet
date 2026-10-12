# 17_visual_ufv_latex.md — three fresh-eyes passes: rendered pages (18), UFV compliance (13), LaTeX source and build engineering (19)

**Written 2026-07-28.** Read-only on the document. Nothing below is taken from another record on
trust: every recorded measurement this round asked me to confirm was re-derived with a stated
instrument, and where my re-derivation disagrees with the record I say so and give both numbers.

**Trees measured.** The state I was asked to review was `01915ba7`. Mid-pass the three paper
chapters were split into per-section files at `4e84cf7a`. I measured **both**, in isolated
`git archive` exports under `/tmp/r6_iso` (01915ba7) and `/tmp/r6_new` (4e84cf7a), because the live
working tree was being mutated by a parallel agent while my first build was running (the split
landed 90 seconds into it) and a build over a tree in flight is not a measurement. All source
coordinates below are **post-split, as of 2026-07-28**, and each is given with its anchor phrase.

---

## 0 · Verdicts

| Persona | Scope | Verdict |
|---|---|---|
| **18** Visual and presentation | rendered pages of all three builds | **needs a visual pass** — in-figure type size is a defect class in all four diagrams and is worse in the two the record does not track, and every footnote mark in every build is a hyperlink to page 1 |
| **13** UFV compliance | defense, final, ppgc | **defense COMPLIANT · ppgc COMPLIANT · final NON-COMPLIANT** on one measurable rule (page-numbering offset) |
| **19** LaTeX source and build engineering | source, preamble, `.sty`, Makefile, three logs, the gates | **needs an engineering pass** — the three-target structure is sound; `make check` does not pass, and two gate-coverage facts are worth recording |

**Top three findings:** E-5 (every footnote mark in all three builds is a live hyperlink to page 1,
ten of them, and the fix is one line that changes no pixel), C-1 (the final build's first body page
prints 11 on physical page 8), V-1 (Ch.3 figure labels at 44 percent of body, smaller than either
figure the audit tracks, and not in `LEFT_OUT.md`). Then E-1: `make check` exits nonzero at both
commits, so "all gates pass" in the round's state description is not what the gate reports.

**One of these was nearly a miss, and the near-miss is worth reading.** I first filed E-5 as a MINOR
log-hygiene note on the grounds that the ten footnote destinations exist and resolve. They do. They
also all resolve to page 1, which is the question I had not asked. The instrument that says
"resolves" and the instrument that says "resolves to the right place" are different instruments, and
only the second one is a measurement.

---

## 1 · The build, measured

`cd /tmp/r6_new/articles/dissertacao && source src_utils/texenv.sh && cd src && make defense &&
make final && make ppgc`, three passes each, then the logs read mechanically (flattened before
matching, `errors='replace'`, `.blg` read separately).

| | defense | final | ppgc |
|---|---:|---:|---:|
| pages | **108** | **105** | **109** |
| `tex_errors` | 0 | 0 | 0 |
| fatal errors | 0 | 0 | 0 |
| `Overfull \hbox` | 0 | 0 | 0 |
| `Overfull \vbox` | 0 | 0 | 0 |
| **`Underfull \hbox`** | **17** | **16** | **17** |
| `Underfull \vbox` | 0 | 0 | 0 |
| undefined citations | 0 | 0 | 0 |
| undefined references | 0 | 0 | 0 |
| `Float too large for page` | 0 | 0 | 0 |
| missing characters | 0 | 0 | 0 |
| undefined font shapes | 0 | 0 | 0 |
| `Label(s) may have changed` | no | no | no |
| bibtex problems (`.blg`) | 0 | 0 | 0 |
| `pdfTeX warning (dest)` | 10 | 10 | 10 |

The page counts match the state I was given exactly (108 / 105 / 109). `make` passes
`-halt-on-error` and all three targets produced PDFs, so the source compiles for real and not
under `nonstopmode` recovery. **Two columns the round's state description does not carry are
nonzero**: 16 to 17 underfull horizontal boxes and 10 `dest` warnings per build. Both are
assessed in E-5, and the second one matters: those ten warnings are ten **live broken hyperlinks**,
one per footnote, every one of them jumping the reader to page 1.

### 1.1 The split's render-parity claim, verified independently

The split was described to me as mechanical with the render unchanged. I did not take that on
trust, and it holds, on three instruments:

1. **Source content**: concatenating each new master with its `\input` parts, stripping comments
   and collapsing whitespace, reproduces the pre-split file **character for character** — 40,871
   chars for Ch.3, 39,410 for Ch.4, 52,372 for Ch.5, all three `IDENTICAL=True`.
2. **Text layer**: full-document extraction, all pages joined, SHA-256 equal for all three
   builds (defense 277,927 chars, final 272,861, ppgc 278,057).
3. **Render**: every page of the defense build rasterized at 1.0 scale and compared pixel by
   pixel, pre-split against post-split — **`pages differing: NONE`** over 108 pages
   (`src_utils/_history/_round6/_pxdiff.py`).

The PDF file hashes do differ, and that is not a defect: the only differing bytes are
`/CreationDate` and the document `/ID`. Recording this because "byte-identical" was the claim, and
the PDFs are **not** byte-identical while the *document* is. Equal file **sizes** are not evidence
of byte identity either, and I make that mistake explicit because I made it in passing before the
hashes came back: the three post-split PDFs have exactly the pre-split byte counts (1339651 /
1333480 / 1340420), and all three hashes still differ. Size equality is what you would expect from
a timestamp-only delta; it does not establish it. The parity claim in this report rests on the
text-layer SHA and the pixel diff, not on either the sizes or the file hashes.

---

## 2 · Persona 18 — the rendered pages

### V-1 · BLOCKER-adjacent, filed MAJOR: the Ch.3 architecture figure's labels are the smallest in the document, and are not in the register

- **Anchor:** `\includegraphics[width=\textwidth]{figures/cbic_mtlnet_arch.png}`,
  `src/chapters/3_cbic/method.tex:183` (2026-07-28). Renders **p.34** of the defense build.
- **Measured.** This is a 1200 px wide raster placed at `width=\textwidth` = 455.00 pt, so
  0.37917 pt per source pixel. The nominal-size API cannot see it at all: p.34's text layer
  reports only 11.96, 9.96 and 8.77 pt, none of which belongs to the PNG, because **the PNG's
  labels are not in the text layer** — the same trap `12_figures.md` records for the CoUrb raster.
  So I measured the raster. Compositing the RGBA over white and thresholding at 100, the
  cap/ascender ink height of `ResidualBlock`, `Next POI Encoder` and `Next POI Input` is **10 px**
  each, and `Dropout` is 12 px. At Helvetica's 0.717 cap ratio that is 13.9 nominal px, i.e.
  **5.29 pt on the page, 44.2 percent of the 11.96 pt body**.
- **Conclusion.** All four diagram figures, on one convention:

  | figure | effective nominal | % of 11.96 pt body | instrument |
  |---|---:|---:|---|
  | Ch.5 `fig2_model` (vector, p.64) | 11.15 pt | **93.2** | glyph geometry, `o` box 5.227 pt x 2.1331 |
  | Ch.5 `fig1_dataflow` (vector, p.61) | 7.93 pt | **66.3** | glyph geometry, `o` box 3.718 pt x 2.1331 |
  | Ch.4 `arquitetura_modelo` (raster, p.47) | 5.37 pt | **44.9** | drawio `fontSize=13` px x 0.41289 pt/px |
  | **Ch.3 `cbic_mtlnet_arch` (raster, p.34)** | **5.29 pt** | **44.2** | cap ink 10 px / 0.717 x 0.37917 pt/px |

  The two figures COD-017 tracks are the two **largest** of the four. The two rasters are half
  body size, and the Ch.3 one is the smallest in the document. `LEFT_OUT.md` LO-6 registers the
  Ch.4 raster as a deliberate deferral; **the Ch.3 raster is registered nowhere**, so its absence
  from the text is currently indistinguishable from an oversight, which is exactly what that
  register exists to prevent.
- **Closes when** either the figure is re-exported at a larger label size (it is a published CBIC
  figure, so this is an errata-class change), or an `LO-9` entry is added naming the measurement,
  the decision and the decider, as LO-6 does for Ch.4.

### V-2 · MINOR (confirmed, both directions): `12_figures.md`'s two Ch.5 numbers are correct

- **Anchors:** `width=\textwidth]{figures/mobiwac/fig1_dataflow.pdf}`,
  `src/chapters/5_mobiwac/02_related.tex:217`; `width=\textwidth]{figures/mobiwac/fig2_model.pdf}`,
  `src/chapters/5_mobiwac/04_method.tex:56` (2026-07-28).
- **Measured**, on the instrument that record specifies and with its calibration re-derived
  independently on each page (body `o` char-box 5.607 pt at 11.96 pt nominal, giving 2.1331
  nominal-pt per box-pt): **fig2_model 11.15 pt = 93.2 percent** of body on p.64; **fig1_dataflow
  7.93 pt = 66.3 percent** on p.61. Both agree with `12_figures.md` to the second decimal.
  I also reproduced the blindness it warns about: `FPDFText_GetFontSize` still returns **6.97 pt**
  for both after the rescale, and the below-9-pt glyph counts on those pages are still 351 and 317
  — an audit trusting that instrument would report no improvement at all.
- **Conclusion.** Both figures **CONFIRMED**. fig1 remains below the WRITING_LAW section 5 bar and
  is correctly carried as LO-5.

### V-3 · resolved: the near-blank keyword page is gone, verified on the raster

- **Anchor:** the `Palavras-chave:` block, `src/0_main.tex` (the `minipage` at the foot of the
  Resumo).
- **Measured on the rasterized page, not the text layer** (the failure mode this round warned
  about). p.2 of the defense build carries the `Resumo` heading, the catalog header, the full
  310-word block and all five keyword lines, and the page has visible white space below them; the
  keyword block did not break to its own page. Physical page 3 is the `Abstract`, page 4 is the
  List of Figures. `ANCHORS.md` section 2 item 3 records a near-blank p.4 carrying 21 words; on
  this build **that page does not exist**. Confirmed on all three builds by first-page inventory:
  defense 1 folha de rosto / 2 Resumo / 3 Abstract / 4 LoF, ppgc 1 / 2 approval sheet / 3 Resumo /
  4 Abstract / 5 LoF, final 1 LoF.
- **Conclusion.** **RESOLVED.** The word counts on the render are 334 and 324 tokens for the two
  pages including their catalog headers, consistent with the 310/271-word bodies the round records.

### V-4 · MINOR: three equations set correctly, and the last one strands its own definitions

- **Anchors:** `fixed-weight sum of one term per boundary`, `2_fundamentals.tex:244`; `bilinear
  discriminator that scores`, `:250`; `rewards a high score on a true pair`, `:256`. All three
  render on **p.19**.
- **Measured.** All three set as numbered display equations, `(2.1)` `(2.2)` `(2.3)`, right-aligned
  tags at x_right 537.68 / 537.67 / 533.45 bp against a text-block right edge of 540.60 bp, so no
  tag encroaches the margin. Glyph sizes in the equation bands are 11.96 pt with 8.77 pt
  subscripts (fonts `NewTXMI`, `txsys`, `TeXGyreTermesX-Regular`) — the subscripts are 73 percent
  of body, normal for mathematical subscripts and legible at print size. No equation breaks
  across a line or a page. Lowest ink on p.19 sits 67.83 bp above the page bottom against a
  56.91 bp bottom margin, so nothing overruns. Verified on the raster as well as the text layer.
- **The one defect.** `(2.3)` is the **last object on p.19**, and the `where` clause that defines
  its two symbols opens p.20: p.19 ends `... − log 1 − D (e + , e − ) , (2.3)` and p.20 starts
  `Chapter 2. Fundamentals 20 where e + denotes an embedding from a true pair ...`. The reader
  meets `e^+` and `e^-` and must turn the page for their definitions.
- **Conclusion.** The equations are typographically **correct and legible**; the page break
  between `(2.3)` and its `where` clause is a presentation defect, not a correctness one.
- **Closes when** the three-equation block is kept with its following paragraph (a `\samepage`
  group around `(2.3)` and its `where` sentence, or letting the block start on p.20). Zero words
  change either way.

### V-5 · MINOR: float placement is good, with four floats two pages from their nearest reference

- **Measured** on the defense build, body pages only, caption page against every in-body textual
  reference to that float (the naive version of this measurement reads the List of Figures as the
  render page and reports every float as 30 to 90 pages away; that is an artifact, and the
  numbers below exclude pp. 1 to 10).

  | float | caption p. | referenced on pp. | nearest gap |
  |---|---:|---|---:|
  | Figure 5 | 64 | 58, 62 | **2** |
  | Table 6 | 54 | 52 | **2** |
  | Table 7 | 55 | 53 | **2** |
  | Table 13 | 96 | 94 | **2** |

  Every other float in the document (19 of 23) lands within one page of a reference. No float is
  unreferenced. `oversized_floats=0` on all three builds, so the Appendix B float
  `ANCHORS.md` section 2 item 1 records as fixed is **still clear at 108/105/109 pages**.
- **Conclusion.** Placement is sound; the four two-page gaps are worth a look but none strands a
  reader, and all four are tables or a diagram whose caption is self-contained.

### V-6 · what holds, and should not be touched

- **Table craft is clean throughout.** Zero vertical rules in any tabular preamble, zero
  `\hline` anywhere (booktabs rules only), and **every** caption is correctly placed: tables
  above, figures below, checked mechanically across all 47 source files. Every `\label` follows
  its `\caption` — no label-before-caption anywhere, so no cross-reference silently points at a
  section number.
- **Grayscale safety of the two matplotlib figures.** Figure 7's two series are RGB(31,78,121) and
  RGB(192,57,43), BT.601 luma **68.8** and **95.8** of 255 — a 27-point separation that survives
  a monochrome printer, with the neutral +/-2 pp band at luma 233 well clear of both. Figure 6's
  two series are luma 68.8 (Check2HGI) against a neutral 176 (HGI), a 107-point separation. Both
  also carry explicit text legends. The joint-model blue is the same RGB(31,78,121) in both
  figures, so the colour threading across Chapter 5 is consistent.
- **The two matplotlib figures' in-figure type is fine**, even though they are the only two
  `\includegraphics` calls in the document with no width option (see E-3): measured by geometry,
  Figure 6's tick and annotation type is 10.04 to 11.82 pt (84 to 99 percent of body) and
  Figure 7's is 9.12 to 11.71 pt (76 to 98 percent).
- **Best pages:** p.64 (Figure 5 at 93 percent label size above a clean booktabs Table 8, both
  self-contained), p.19 (three display equations set cleanly in a full page of prose), p.71
  (Figure 7's dual-encoded gains plot with its band legend).

---

## 3 · Persona 13 — UFV compliance

### 3.1 The measured geometry, re-derived rather than taken

`13_layout_measured.md` reports the margins and line spacing as exact. I did not read its
registers; I measured the **rendered pages** of all three builds, taking the extreme ink positions
of body pages and the modal nominal font size.

| Rule (Manual 04_2026 section 7 and 8) | Required | Measured on the render | Verdict |
|---|---|---|---|
| Paper | A4 | 595.28 x 841.89 bp = 21.00 x 29.70 cm | **exact** |
| Font | Arial or Times New Roman 12 | `TeXGyreTermesX-Regular` at nominal **11.96 pt** modal on every body page sampled (pp. 11, 12, 20, 45, 70 defense; 8, 9, 17, 42 final; 12, 13, 21 ppgc) | **compliant** (Times clone; 11.96 pt is `newtx`'s realization of 12 pt) |
| Line spacing | 1.5 | baseline-to-baseline **17.90 bp** on 11.96 pt type = **1.497x** on every page sampled | **compliant** |
| Left margin | 3 cm | leftmost ink 84.07 to 85.01 bp = **2.966 to 2.999 cm** | **compliant** (paragraph-initial ink; the block edge is 85.36 bp = 3.000 cm) |
| Right margin | 2 cm | right gap 55.27 to 57.01 bp = **1.950 to 2.011 cm** | **compliant** |
| Top margin | 3 cm | top ink gap 54.05 to 54.17 bp = **1.907 to 1.911 cm** | see 3.2 |
| Bottom margin | 2 cm | bottom ink gap 54.10 bp min = **1.908 cm** | **compliant** |
| Page numbers | top-right, arabic | rightmost digit edge x = **537.2 to 538.0 bp** against a 540.60 bp block edge, y_top 787.7 bp | **compliant** |

The margins are **confirmed**, independently of the record, and I am naming the one place my
instrument differs from that record so the two are not confused: `13_layout_measured.md` probes the
memoir length registers (what the preamble asks for); I measured ink on the page (what prints).
They agree.

### 3.2 A note on the top margin, not a finding

Top ink gap measures 1.91 cm, not 3 cm, on every body page — because the **running header** (the
chapter name and page number) sits in the head margin, which is where abnTeX2 and the UFV manual
both put the page number. The 3 cm rule governs the text block, whose top edge is at
85.36 bp = 3.000 cm; the header lives above it by design. Measured to be explicit that the
1.91 cm figure is the header, not a margin violation.

### C-1 · MAJOR: the final build's first body page prints 11 on physical page 8

- **Anchor:** `\newcommand{\finalbuildfirstpage}{11}`, `src/main.tex:53` (carries a live
  `[VERIFY]` flag).
- **Measured** on the render, by locating the first page whose header carries a digit and reading
  the printed number:

  | build | pre-textual pages (counted, unnumbered) | first body page | prints | UFV section 2 requires |
  |---|---:|---:|---:|---:|
  | defense | 10 | physical p.11 | **11** | 11 — **correct** |
  | ppgc | 11 | physical p.12 | **12** | 12 — **correct** |
  | **final** | **7** | physical p.8 | **11** | **8** |

  The manual's own worked example is explicit: 10 pre-textual pages means the first body page is
  numbered 11. The final build strips the folha de rosto, Resumo and Abstract, so it has 7
  pre-textual pages (LoF, LoT, LoT continuation, siglas, and three sumário pages), and its first
  body page should print **8**. It prints 11, because `\finalbuildfirstpage` is hardcoded to the
  defense build's offset. Every subsequent page inherits the three-page error: the printed numbers
  ran **11 to 108** across a 105-page PDF, where they should run 8 to 105, and the sumário's page
  references (Introduction 11, References 80, Appendix E 106) match the defense build's numbering
  rather than this PDF's own.
  > **Arithmetic corrected 2026-07-28 (finding cd079279).** This read "11 to 115", which is
  > incompatible with the same finding's own premise. With 7 pre-textual pages counted but not
  > numbered, the first body page is physical 8; printing 11 there puts 11 + (105 − 8) = **108** on
  > the last page. 115 would require 12 pre-textual pages. The defect and its size (three pages) are
  > unchanged; only the endpoint was wrong.
- **Conclusion.** The AcademicoPG deposit build is **NON-COMPLIANT** on the numbering rule. It is
  caught early and cheaply: it is one integer, and the `[VERIFY]` flag on it is the reason it has
  not shipped wrong. The compliance doc also says the system's RASCUNHO PDF is the authoritative
  numbering reference, so the final value must be tuned post-defense in any case — but 11 is
  wrong by construction today, and 8 is what the current front matter implies.
- **Closes when** `\finalbuildfirstpage` is derived from the build mode rather than fixed (or set
  to 8 with the `[VERIFY]` flag kept for the RASCUNHO reconciliation), and the sumário page
  numbers are re-read on the resulting PDF.

### C-2 · MINOR: page 87 of the defense build (84 final, 88 ppgc) carries no page number

- **Measured.** Sweeping every page from the first numbered one onward, exactly one page per build
  lacks a header number: **p.87 defense, p.84 final, p.88 ppgc**. All three are the same page —
  the `Appendix` part divider, which carries the single word `Appendix` centered on an otherwise
  blank page (verified on the raster). It is `\partapendices`, which abnTeX2 sets with an empty
  page style. No printed number is out of sequence anywhere in any build.
- **Conclusion.** The manual requires numbering from the first body page onward and does not carve
  out part dividers. This is a **one-page deviation** in a post-textual divider, and the Germano
  precedent (same program, same advisor, defended) uses the same `\partapendices` machinery.
  Reported as measured; the author may reasonably leave it.
- **Closes when** either the divider gets `\thispagestyle{abntheadings}` or the deviation is
  accepted on the Germano precedent and recorded.

### 3.3 Structure and front matter, audited element by element

**Coletânea structure (Normas section 2.3 / 2.6):** body is Introduction (ch.1) → Fundamentals
(ch.2) → three article chapters (3, 4, 5) → Conclusion (ch.6), then References and Appendices A-E.
Introdução Geral, artigos, Conclusão Geral, in order — **compliant**. Article statuses are
labeled in the chapter prefaces, with Ch.5 carried as under review.

**Defense build front matter, in render order:** folha de rosto (p.1) → Resumo (p.2) → Abstract
(p.3) → List of Figures (p.4) → List of Tables (pp.5-6) → List of abbreviations (p.7) → sumário
(pp.8-10) → body (p.11). Resumo and Abstract are both present and structurally mirror each other
(same catalog header shape, same five-line keyword block).

**One observation, not a violation:** there is **no capa and no ficha catalográfica page** in any
build. `\imprimircapa` is defined in `abntex2-UFV.sty:44` and called by neither build;
`\campus{Campus Florestal}` feeds only that macro, which is what `LEFT_OUT.md` LO-3 records. For
the **final** build this is correct — the system generates both. For the **defense** build,
UFV_COMPLIANCE section 1 describes a "conventional full PDF — cover page, approval sheet, lists,
sumário, body". The document opens on the folha de rosto instead. The two pages are cosmetically
near-identical and the banca is unlikely to object, but the defense PDF is currently missing the
cover the compliance doc names, and LO-3 registers the mechanism without registering that
consequence. **Flagged for the author, not filed as a violation**, because the pre-textual
checklist governs and I did not open it this session.

**The ppgc build's approval sheet is correctly placed and correctly scoped.** Verified on the
raster: physical p.2, immediately after the folha de rosto and before the Resumo, which is the
position the PPG signature-page model occupies. It is absent from the defense and final builds.
`main_ppgc.pdf` is otherwise the defense document (109 = 108 + 1 page).

**Keyword blocks (UFV section 2 system rules)** — audited on the render, both blocks: five lines
each, **one keyword per line**, all lowercase, **no trailing punctuation**, zero indented
paragraph starts in the abstract body above them. PT mirrors EN one for one. **Compliant.**

**References style:** single global numeric list, `[N]` labels in the list and `[N]` in the text,
matching the advisor's round-5 instruction and the settled `abntex2cite[num]` decision. Rendered
list checked on pp. 80-81. Bibliography sets at body size, per the round-5 removal of the
`\footnotesize` wrapper.

**Lists:** LoF (7 figures), LoT (16 tables), and a 12-entry abbreviations list, all present in all
three builds and reachable as PDF bookmarks. The siglas list is correctly case-insensitively
alphabetical (`CBIC, Check2HGI, CoUrb, DGI, FiLM, HGI, LBSN, MobiWac, MTL, POI, SBRC, TOST`), and
all 12 entries do appear in prose (`CoUrb` 46 times, `FiLM` 21, `MobiWac` 24 — an acronym sweep
that strips LaTeX macros misses these three, which is why I counted them separately).

**Sumário:** complete and correct. Every chapter, every section to the third level, References,
and all five appendices, with page numbers matching the render.

### C-3 · MINOR: 49 acronym-shaped tokens appear in prose without a siglas entry

- **Measured.** Comment-stripped prose, math and macro names removed, tokens matching two-plus
  capitals or a letter-digit form: **49** such tokens are absent from the 12-entry list. Most are
  model names introduced and defined at first use in related-work prose (CTLE, STAN, SIREN,
  Sphere2Vec, Time2Vec, HMT-GRN, MCARNN, CSLSL) or third-party names cited once in a
  reproducibility footnote (CVXPY, MPS, GPU, CPU, NVIDIA). Two are worth the author's eye because
  they are used repeatedly and are not model names: **F1** (55 occurrences) and **HMRM** (9).
- **Conclusion.** The list was built deliberately on an expand-at-first-use / minimal-count rule
  (documented in `0_main.tex`), and that rule is defensible: an ABNT lista de siglas is not
  required to enumerate every cited system. This is **not a violation**, and I am not recommending
  a 49-row list. Flagged so the choice is visible.

### 3.4 Process prerequisites (status reported, not verified in-session)

| Item | Status | Basis |
|---|---|---|
| Art. 21 section 1 publication proof | **substance covered, filing pending** | CBIC DOI `10.21528/CBIC2025-1191324`, `CLAUDE.md` section 1; the comprovante filing with the secretariat is an open action in that same record |
| Art. 22, text to secretariat ≥20 days pre-defense | **at risk / undetermined** | no defense date is set (`\databanca{[defense date --- pending]}`, `0_main.tex:146`). Calendar math cannot be done without it. For an Aug 18-29 defense the text must be filed Jul 29 to Aug 9 |
| Anti-plagiarism certificate | **UNVERIFIED** | not establishable from the repository |
| Termo de assentimento, BBT authorization (wet signatures) | **UNVERIFIED** | not establishable from the repository |
| AI-use disclosure at its settled placement | **present** | Appendix C, rendered p.102, in all three builds |
| Banca members | **pending** | `[Banca member 1 --- pending advisor conversation]`, `0_main.tex:144-145` |

---

## 4 · Persona 19 — source and build engineering

### 4.1 Is the three-target structure sound? Yes, and here is the test that says so

**It is sound.** `main.tex` is the defense root and defines both switches with the same
`\ifdefined` guard, so a command-line `\def` works without the nested-`\if` scanning problem;
`main_ppgc.tex` is 18 lines of which two are content (`\def\APPROVALSHEET{}` and
`\input{main.tex}`), so the ppgc PDF cannot drift from the defense PDF; `make final` sets
`\FINALBUILD` on the command line against the same root. Three targets, one body, two switches.

I exercised the combination none of the three targets covers — **the ppgc root under
`\FINALBUILD`** — because an untested switch path is how a two-build toggle ships the wrong PDF.
Two runs, because the first thing I reached for tested the wrong root and I am recording both:

```
A. pdflatex -halt-on-error -jobname=comboA "\def\FINALBUILD{}\input{main_ppgc.tex}"
     -> exit 0, 95 pages, approval placeholder ABSENT, Resumo ABSENT, opens on "List of Figures"
B. pdflatex -halt-on-error -jobname=combo  "\def\FINALBUILD{}\def\APPROVALSHEET{}\input{main.tex}"
     -> exit 0, 95 pages, 1293670 bytes -- identical, but this is the DEFENSE root with both
        switches set on the command line, NOT the ppgc entry file
```

Run **A** is the one that answers the question, and it behaves correctly: `\FINALBUILD` wins,
the approval sheet is suppressed along with the rest of the front matter, and the result is the
deposit body. Run **B** is the same output reached through the other root, which is worth having
because it confirms `main_ppgc.tex` contributes nothing but the switch — but on its own it would
have proved nothing about the ppgc root, and I initially labelled it as though it had. 95 rather
than 105 pages in both cases because the front matter and the approval sheet are both gone, as
intended. **The structure will not bite someone**; the one thing that will is C-1, and that is a
value, not a structure.

`\finalbuildfirstpage` **is still flagged**, not silently trusted (`main.tex:53` carries
`% [VERIFY: tune against the RASCUNHO PDF]`), which is what persona 19 asks. C-1 is that the
flagged value is also wrong today.

### E-1 · MAJOR: `make check` does not pass, at either commit

- **Anchor:** `This article differs from the other two in a way that changes what this section has
  to record.` — `src/chapters/apx_b_errata.tex:307` (2026-07-28, identical at both commits).
- **Measured.** The gate's `'this paper' / 'this article' inside chapters` check matches that line
  and sets `FAIL=1`. Exit codes, at the post-split commit: `make check` → **2**,
  `./src_utils/check.sh` → **1**, `../src_utils/check.sh` from `src/` → **1**. At `01915ba7`, the
  commit whose state says "`make check` all gates pass": **also 2**. `git log -S` puts the line
  in `d1911c0a`, so it predates this round. Every other sub-check passes.
- **Conclusion.** The sentence itself is **correct prose** — Appendix B is discussing the
  MobiWac article's status, and "this article" refers to that article, not to the dissertation.
  It is a false positive in a check whose purpose is to catch leftover paper-voice inside
  re-typeset chapters. But the consequence is real and is the more important half of this
  finding: **the gate reports failure, and the round's state description reports that it passes.**
  A gate whose nonzero exit is known-and-ignored has stopped being a gate, which is precisely the
  "trusting the tolerant tool" bias `AGENT_GUARDRAILS` section 7 names.
- **Closes when** either the sentence is reworded ("The MobiWac article differs from the other
  two ...", zero claim change), or `apx_b_errata.tex` is exempted from this specific check the way
  it is already exempted from the banned-words check one line above it (`check.sh:25` carries
  `grep -v '^chapters/apx_b_errata'`), with the exemption's reason in the comment. Either way the
  build claim must stop asserting a pass the gate does not give.

### E-2 · MAJOR: six chapter files have no `% !TeX root`, and four are the files a reader opens first

- **Measured.** Post-split, 24 of 30 chapter files carry a correct magic comment (18 of them the
  new per-section files, all pointing at `../../main.tex`, all correct). **Six do not:**
  `2_fundamentals.tex`, `3_cbic.tex`, `4_courb.tex`, `5_mobiwac.tex`, `apx_d_ceiling.tex`,
  `apx_e_ethics.tex`. The round repointed six files whose comments named a nonexistent
  `main_defense.tex`; these six never had one.
- **Conclusion.** The three paper-chapter masters are now the **entry points** to the split
  chapters, so they are the files an editor opens to navigate, and they are exactly the ones that
  will not compile from the editor. `2_fundamentals.tex` is the chapter under active work. Not a
  build defect; a maintainability one, in the dimension the split just made more important.
- **Closes when** `% !TeX root = ../main.tex` is added as line 1 of those six files.

### E-3 · MINOR: one stale root pointer survives, in the preamble

- **Anchor:** `%% Compile with pdflatex via main_defense.tex or main_final.tex, never this file.`
  — `src/0_main.tex:16`.
- **Measured.** Neither file exists. `main_defense.tex` is the same nonexistent name this round
  repointed in six `% !TeX root` comments; `main_final.tex` is a `-jobname`, not a source file
  (`Makefile:28`). Grep for both names across `src/` returns this line plus Makefile comments that
  correctly describe the jobname.
- **Conclusion.** The round fixed this defect class in the magic comments and missed it in the
  preamble header, where a first-time reader is most likely to act on it. One line.
- **Closes when** the line names `main.tex` (defense), `make final`, and `main_ppgc.tex`.

### E-4 · MINOR: two `\includegraphics` calls carry no width option

- **Anchors:** `\includegraphics{figures/mobiwac/fig3_embquality.pdf}`,
  `src/chapters/5_mobiwac/06_results.tex:58`; `\includegraphics{figures/mobiwac/fig4_deltas.pdf}`,
  `:182` (2026-07-28).
- **Measured.** Every other graphic in the document carries `width=\textwidth`; these two are
  placed at natural size. Their natural widths are **369.028 pt** and **360.390 pt** against a
  455.00 pt text block, so they occupy 81 and 79 percent of it. No hardcoded `pt`/`cm`/`in`
  dimension appears on any `\includegraphics` anywhere, so this is an omission, not a hardcode.
- **Conclusion.** Benign **today** — both are matplotlib PDFs generated at a size that happens to
  fit, and their in-figure type measures 76 to 99 percent of body (V-6), better than either
  diagram. But the placement depends on the figure's own bounding box rather than the text block:
  regenerate either script at a different `figsize` and the figure silently changes size on the
  page, and if it grows past 455 pt it overflows with no warning from these two calls.
- **Closes when** both carry an explicit relative width (`width=\textwidth`, or
  `width=0.81\textwidth` to preserve today's appearance exactly).

### E-5 · MAJOR: every footnote mark in all three builds is a hyperlink to page 1

**This finding replaces an earlier version of itself that got the verdict backwards, and the
correction is the point.** I first tested whether the ten `Hfootnote.N` destinations *exist and
resolve*, found that all ten do, and concluded from that the warnings were benign. That is the
wrong test: a destination can resolve and still resolve to the wrong page. Measuring **where** they
land inverts the conclusion.

- **Anchor:** `pdfTeX warning (dest): name{Hfootnote.N} has been referenced but does not exist`,
  10 occurrences in each of `build/main.log`, `build/main_final.log`, `build/main_ppgc.log`.
- **Measured** (`src_utils/_history/_round6/_fnlinks.py`, run on all three renders). All ten footnote
  destinations resolve to **physical page 1** in every build. The pages that actually carry
  footnote text are pp. 27, 28, 31, 34, 35, 40, 44, 50, 58, 70, 106 of the defense build. And the
  broken destinations are not inert: **10 live link annotations**, on body pages 27, 28, 31, 34,
  35, 40, 44, 58 and 106 (twice), point at page 1. Those are exactly the ten footnote marks the
  source inventory predicts (6 in Ch.3, 1 in Ch.4, 1 in Ch.5, 2 in Appendix E); pp. 50 and 70 are
  table notes set with `\footnotesize`, which correctly produce no link.
- **Instrument validated against controls on the same document**, so a page-index of 0 is not an
  artifact of how I read the dest: `chapter.5` resolves to p.57, `section.5.6` to p.68,
  `cite.silva2025mtlnet` to p.82. Real anchors land correctly; only the footnote anchors collapse
  to page 1.
- **Conclusion.** A reader who clicks any footnote mark in the banca PDF is thrown to the folha de
  rosto (the List of Figures, in the final build) and loses their place. The pdfTeX warning was
  telling the truth the whole time, and "the name exists in the name tree" is not an answer to it.
  Ten broken links in a document handed to a committee is a MAJOR presentation defect, not the
  MINOR log-hygiene note I first filed. The underfull boxes in the same log **are** benign, and
  are kept here with them: **17** defense, **16** final, **17** ppgc, worst badness 10000 reached
  7 times, almost all loose inter-word spacing inside `p{}` columns of the quoted-prose errata
  tables (`Replaced by the correct record`, `Consolidated to a single entry`, and the `\texttt`
  keys beside them) plus one long footnote; `Overfull` is 0 everywhere, so nothing bleeds into a
  margin.
- **Cause and remedy, both tested.** The document sets `hyperfootnotes` nowhere, and abnTeX2 loads
  `hyperref` itself, so the footnote-anchor machinery never gets initialized for this class's
  footnote handling. `\hypersetup{hyperfootnotes=false}` in the preamble **does not work** and I
  verified that rather than assuming: the log answers
  `Package hyperref Warning: Option 'hyperfootnotes' has already been used`, and all 10 warnings
  survive. The option is load-time only, so it has to precede the class:
  `\PassOptionsToPackage{hyperfootnotes=false}{hyperref}` on the line above `\documentclass`.
  Built with that one line added: **108 pages, tex_errors=0, dest warnings 0 (from 10), footnote
  destinations 0 (from 10), footnote links to page 1 zero**, the control anchors still resolve
  correctly, the full text layer is SHA-identical to the current build, every footnote's text is
  still on its page, and `_pxdiff.py` reports **`pages differing: NONE`** across all 108 pages.
  The alternative, if clickable footnotes are wanted rather than switched off, is loading
  `hyperref` explicitly before the class machinery so its footnote anchors initialize; that is a
  larger change to a preamble whose load order is deliberate, and it is not what I tested.
- **Closes when** either that one line is added (measured above: no render change, no page-count
  change, warnings and broken links both to zero), or the ten links are made to point at their
  footnotes. Re-check with `_fnlinks.py`, which fails on the current build and passes on the
  patched one.

### 4.2 The gate-coverage findings the split produced

**E-6 · confirmed fixed, and validated on the real files.** The split briefly hid 55 percent of
the document's prose from every sweep while all of them reported OK, because they globbed
`chapters/*.tex`. All four are now correct at `4e84cf7a`: `check.sh:12` sets
`CH="chapters/*.tex chapters/*/*.tex"`; `check_doubled_macro.py:84-85`, `check_torn_sentences.py:89-91`
and `check_trapped_prose.py:158-159` each add the `*/*.tex` arm, each with a comment naming the
split as the reason. The doubled-macro checker reports **49 files** where it reported 31 —
consistent with 18 new per-section files. Its self-test still passes in both directions before it
reports, and the trapped-prose detector's 10 fixtures all pass. This is the right shape: the
checkers were fixed in the same commit as the structural change, and each carries its reason.

**E-7 · MINOR, a residual coverage gap.** `check_doubled_macro.py`'s file list is
`*.tex + chapters/*.tex + chapters/*/*.tex + tables/*/*.tex`; `check_torn_sentences.py` and
`check.sh` cover the same shape. **None of them descends past one level** under `chapters/`, and
none covers a `figures/*.tex` (there is no such file today). That is correct for today's tree and
will silently under-cover the first time a per-section file is itself split, which is the second
time in one round that a directory change outran a glob. Worth one line of defense:
`chapters/**/*.tex` via `rglob`, so the next split needs no gate edit.

### 4.3 The best-practice scorecard

| Dimension | Score | Evidence |
|---|---|---|
| 1. Preamble hygiene | **GOOD** | Zero obsolete commands (no `\bf`/`\it`/`\rm`/`\sc`/`\tt`, no `epsfig`, no `a4wide`) — swept across all 47 files. Zero duplicate `\usepackage` lines. Settled font stack `newtxtext,newtxmath` confirmed, and the `amssymb` drop carries its `\Bbbk` clash reason. Load order correct. Every non-default choice carries a comment with its reason and often its measurement. **Three packages appear unused**: `multicol` (0 `multicols`), `mathtools` (0 of its distinctive macros), `bm` (0 `\bm{}`) — recommend dropping, cost zero, benefit one less thing to explain. `indentfirst` has no callable trace by construction (it patches `\@afterindentfalse`) and is correct to keep under ABNT. |
| 2. Build health | **AT-RISK** | 0 tex_errors, 0 overfull, 0 undefined refs/cites, 0 oversized floats, 0 bibtex problems, no rerun needed, on all three targets. But `make check` exits nonzero (E-1), and the 10 `dest` warnings per build are 10 live broken hyperlinks that ship to the reader (E-5) — a warning the log raised on every build and no build claim has ever reported. |
| 3. Bibliography integrity (mechanical) | **GOOD** | `bibtex` + `abntex2cite[num]` + `abntex2-num.bst`, consistent with the settled decision; no biber, no `[alf]` residue. **100 entries, 100 unique keys, zero duplicates** — the known Wang_2023 / Liu_2023 / Lai_2024 collision set is **not** in this file. **Zero dangling keys and zero uncited entries** across 47 scanned files. The DGI triple-key fragmentation is resolved: one `velickovic2019deep` (`velivckovic2017graph` is the separate GAT paper). Four same-author-same-year clusters checked by title and all are genuinely distinct works. `.blg` clean on all three builds. |
| 4. Cross-reference plumbing | **GOOD** | **Every** `\ref`-family call carries a non-breaking tie — zero untied hits across all files. Every `\label` follows its `\caption`. One `Equation 2` in prose is a reference to a *cited paper's* equation (`2_fundamentals.tex:170`), not an internal cross-reference, so it is correct. Label prefixes consistent (`fig:`/`tab:`/`sec:`/`eq:`/`ch:`/`apx:`). Zero doubled reference macros. |
| 5. Graphics and floats (source) | **GOOD** | All relative widths, zero hardcoded dimensions, zero `[H]` placements, all floats `[htbp]` or `[htb]`, no `svg`/`--shell-escape` dependency, no absolute paths. Only E-4 (two missing width options) against it. |
| 6. Two-build correctness | **GOOD** | Three targets verified to produce the right PDF; the untested fourth switch combination exercised and correct; `\finalbuildfirstpage` still flagged. |
| 7. Maintainability and reproducibility | **NEEDS-WORK** | Modular `\include` per chapter plus the new per-section `\input` layer; results tables live in script-generated `tables/*.tex`; the `\sd{}` macro used consistently; **zero** manual `\newpage`/`\clearpage`/`\pagebreak` in any chapter. Held back by E-2 (six missing `% !TeX root`) and E-3 (stale pointer). |
| 8. Portability | **GOOD** | pdfLaTeX only, no shell-escape, no external converters. **One declared dependency**: the abnTeX2 and newtx stack must be on `TEXMFHOME` with `TEXMFVAR` pointing at the usermode font map, which `src_utils/texenv.sh` sets and documents with both failure signatures. On Overleaf this resolves from the TeX Live distribution. |

### 4.4 Linter appendix

**`chktex` and `lacheck` are not installed on this machine.** `which chktex lacheck` returns
nothing, nothing under `/usr/local/texlive` matches either name, and `kpsewhich chktexrc` returns
nothing — this is TeX Live 2026 **basic**. Rather than report silence I implemented the
load-bearing subset of their warning classes directly (`src_utils/_history/_round6/_lint_subset.py`, **nine**
checks, comment-stripped) and ran it on the real source. **Two classes are deliberately NOT
implemented and are therefore not covered by a green run**: ChkTeX 11 (swallowed space after a text
macro) and nested-quote direction; the script's header says so, so a later reader cannot mistake
its silence for coverage.

| check (mapped warning) | hits | triage |
|---|---:|---|
| straight `"` instead of `` `` '' `` (ChkTeX 38) | **0** | clean |
| obsolete font commands (l2tabu) | **0** | clean |
| footnote before its punctuation | **0** | clean |
| unbalanced `$` per line | **0** | clean |
| `\label` before its `\caption` inside a float (lacheck) | **0** | clean — validated in both directions before the zero was trusted: the check fires on a synthetic label-before-caption table and figure, stays silent on the corrected form, and ignores a `\label` inside a comment |
| missing tie before a `\ref`-family macro (ChkTeX 13) | **0** | clean |
| hardcoded float/section number in prose | 1 | **noise** — it is another paper's `Equation 2` |
| missing tie before a `\cite` (ChkTeX 13) | 175 | **noise, by house style** — the citations are numeric `[N]` superscript-style labels; the document places them after a space throughout, consistently, and 2 of 175 fall at a line end |
| `$...$` rather than `\(...\)` (ChkTeX 1) | 1126 | **noise** — a valid style choice, applied consistently |
| bare `...` instead of `\dots` | 11 | **noise** — all 11 are inside `tables/cbic/errata_wording.tex`, quoting elided published prose, where a literal ellipsis in quoted text is correct |

Nothing load-bearing. The classes that would matter (untied refs, obsolete commands, quote
direction, unbalanced math) are all at zero.

### 4.5 What is already engineered well, and must not be undone

- **The `\checkandfixthelayout[fixed]` argument at `0_main.tex:34`** is load-bearing and
  commented as such: without `[fixed]`, memoir rounds the text block to whole lines and the bottom
  margin drifts to 1.5-1.6 cm, breaking compliance. My independent render measurement (bottom ink
  gap 1.908 cm minimum) confirms it is doing its job.
- **The `\@biblabel` hook at `0_main.tex:75-77`**, with its comment explaining why
  `\citenumstyle` is the wrong hook (it is a font switch, not a formatter, and redefining it
  renders `[0]`). This is the kind of comment that prevents a re-break.
- **`main_ppgc.tex` being two lines of content.** The temptation to add "just one thing" to it is
  the temptation that makes two entry points drift. Its own comment forbids it.
- **`src_utils/texenv.sh`**, which documents both failure signatures including the one that looks
  like a missing font and is actually a missing font map.
- **The gates' defect-history comments.** Every checker names the real defect that shipped once
  and validates itself in both directions before reporting. `check_doubled_macro.py` is a good
  addition on exactly this standard: it catches a class where pdflatex raises nothing and
  `undef_ref` stays truthfully at 0.
- **The `{\small ...}` asymmetry note** in `13_layout_measured.md`: `\small` sits *inside* four
  errata `table` floats but *outside* `bib_errata`'s `longtable`, because a longtable is not a
  float and has no group of its own. That asymmetry is what made the lost brace of `6d780b58`
  possible. Do not "normalize" it away.

---

## 5 · Source ledger

Every number below traces to a file on this machine, opened this session. No external citations
were needed and none were added.

### 5.1 Numbers → source → field → convention

| number | source | field | convention |
|---|---|---|---|
| 108 / 105 / 109 pages | `/tmp/r6_new/.../src/build/{main,main_final,main_ppgc}.log` | `Output written on ... (N pages` | third pass of each target |
| tex_errors, overfull, underfull, undef, float, missing-char, fontshape, rerun, dest counts | same three logs | regex on the raw log for per-line matches, on the flattened log for wrapped warnings, `errors='replace'` | LaTeX wraps at 79 columns; flattening is required or wrapped warnings are invisible |
| bibtex_problems = 0 | `build/{main,main_final,main_ppgc}.blg` | lines matching `error\|didn't find\|I was expecting` | the `.blg` is read separately because a BibTeX error never reaches the `.log` |
| 40,871 / 39,410 / 52,372 chars | `chapters/{3_cbic,4_courb,5_mobiwac}.tex` at both commits | comment-stripped, whitespace-collapsed length | pre-split file vs post-split master + its `\input` parts concatenated |
| text-layer SHA equal, 277,927 / 272,861 / 278,057 chars | the six PDFs | pypdfium2 text extraction, all pages joined on `\x00` | pre-split vs post-split |
| `pages differing: NONE` over 108 pages | `/tmp/iso_main.pdf` vs `/tmp/r6_new/.../main.pdf` | per-pixel grayscale inequality at render scale 1.0 | `src_utils/_history/_round6/_pxdiff.py` |
| body nominal 11.96 pt | rendered pages 11, 12, 20, 45, 70 (defense) and the matching final/ppgc pages | `FPDFText_GetFontSize`, modal value | nominal size of the embedded font |
| leading 17.90 bp = 1.497x | same pages | median baseline-to-baseline gap of x-height glyph bottoms | on 11.96 pt type |
| margins 2.966-2.999 / 1.950-2.011 / 1.907-1.911 / 1.908 cm | same pages | extreme ink positions from `FPDFText_GetCharBox` | ink, not the text block; block edges are 85.36 and 56.91 bp |
| page-number x_right 537.2-538.0 bp | all pages of all three builds | rightmost contiguous digit run with box top > pageheight − 70 bp | text-block right edge 540.60 bp |
| pre-textual 10 / 7 / 11; first body p.11 / 8 / 12; prints 11 / 11 / 12 | all three renders | first page carrying a header digit | UFV section 2: pre-textual counted, unnumbered; body numbering starts at pre-textual + 1 |
| unnumbered page 87 / 84 / 88 | all three renders | pages after the first numbered one with no header digit | verified on the raster as the `Appendix` part divider |
| fig1 7.93 pt (66.3%), fig2 11.15 pt (93.2%) | `/tmp/iso_main.pdf` pp. 61, 64 | median `o` char-box height x 2.1331 | geometry, calibrated on the body `o` (5.607 pt box at 11.96 pt nominal) on the same page |
| fig1/fig2 nominal still 6.97 pt; 351 / 317 glyphs below 9 pt | same pages | `FPDFText_GetFontSize` | **blind to `\includegraphics` scale** — recorded to reproduce the trap, not used for a verdict |
| Ch.4 label 5.37 pt (44.9%) | `figures/courb/arquitetura_modelo.png` + `4_courb/methodology.tex:20` | drawio `fontSize=13` px x (455.00 / 1102 px) | PNG exported at scale 1.0; mapping verified against the page raster (figure ink bbox 87.0-536.2 pt, 449.25 pt wide) |
| Ch.4 label ink 3.92-4.83 pt | `/tmp/iso_main.pdf` p.47 rasterized at 12 px/pt | ink height of the three encoder-title bands, PNG rows mapped to page px | cross-check on the nominal figure above |
| Ch.3 label 5.29 pt (44.2%) | `figures/cbic_mtlnet_arch.png` + `3_cbic/method.tex:183` | cap/ascender ink 10 px / 0.717 Helvetica cap ratio x (455.00 / 1200 px) | RGBA composited over white, threshold 100 |
| body mixed-line ink 10.83 pt | `/tmp/iso_main.pdf` p.47 rasterized at 12 px/pt | ascender-to-descender ink height of one prose line | the comparator for raster ink measurements |
| Figure 6 / 7 in-figure type 9.12-11.82 pt | pp. 69, 71 | median reference-glyph box x 2.1331 per nominal cluster | same geometry route |
| fig3 369.028 x 164.305 pt, fig4 360.390 x 153.828 pt | the two committed figure PDFs | page box via pypdfium2 | against `\textwidth` = 455.00 pt |
| luma 68.8 / 95.8 / 176 / 233 | pp. 69, 71 rasterized at 4x | BT.601 luma of the modal saturated and neutral fills | grayscale-print proxy |
| equation tag x_right 537.68 / 537.67 / 533.45 bp; lowest ink 67.83 bp | p.19 | `FPDFText_GetCharBox` on the `(2.N)` runs | text block right edge 540.60 bp, bottom margin 56.91 bp |
| float caption vs reference pages | defense render, pp. 11-108 | caption regex `(Figure\|Table) N –` vs every other `(Figure\|Table) N` occurrence | body pages only; pp. 1-10 excluded or the lists read as the render page |
| 100 bib entries, 0 duplicates, 0 dangling, 0 uncited | `references.bib` + 47 source files | `src_utils/_history/_round6/_bibaudit.py` | comment-stripped `\cite` extraction; the one `[` hit is `\citebrackets{[}{]}` at `0_main.tex:68`, not a key |
| 49 files scanned by the doubled-macro gate | `make check` output | the checker's own count | was 31 pre-split |
| 175 / 1126 / 11 / 1 / 0 lint hits | 47 source files | `src_utils/_history/_round6/_lint_subset.py` | comment-stripped; triage in 4.4 |
| 49 unlisted acronym-shaped tokens; CoUrb 46, FiLM 21, MobiWac 24 | `chapters/*.tex` + `chapters/*/*.tex` | comment-stripped, math and macros removed, then a literal count for the three | the macro-stripping sweep cannot see mixed-case acronyms, hence the separate count |
| combo builds 95 pages | `/tmp/swtest/src/build/{comboA,combo}.pdf` | `Output written on` + text-layer probe | `main_ppgc.tex` and `main.tex` each under `\FINALBUILD` |
| 10 footnote dests → physical page 1, in all three builds | the three renders | `FPDF_GetNamedDest` + `FPDFDest_GetDestPageIndex`, 0-indexed then +1 | resolved page index, NOT mere existence in the name tree — existence was my first and wrong test |
| footnote text on pp. 27, 28, 31, 34, 35, 40, 44, 50, 58, 70, 106 (defense) | defense render | count of glyphs below 10.5 pt nominal with box bottom < 260 bp, threshold 60 per page | the comparator that makes page 1 wrong; pp. 50 and 70 are `\footnotesize` table notes, not footnotes |
| 10 live link annotations targeting p.1, on pp. 27, 28, 31, 34, 35, 40, 44, 58, 106 (x2) | defense render | `FPDFAnnot_GetLink` → `FPDFLink_GetDest` → target page index, excluding p.1 itself as a source | matches the source inventory exactly: 6 Ch.3 + 1 Ch.4 + 1 Ch.5 + 2 Appendix E |
| control anchors `chapter.5`→57, `section.5.6`→68, `cite.silva2025mtlnet`→82 | defense render | same instrument | validates that a 0 index means a broken anchor, not a misread |
| patched build: 108 pp, tex_errors=0, dest 0, footnote dests 0, footnote links to p.1 zero, text SHA identical, `pages differing: NONE` | `/tmp/fntest/dissertacao/src/build/main.pdf` | three-pass `make`-equivalent with `-halt-on-error`, then `_fnlinks.py` and `_pxdiff.py` | one added line: `\PassOptionsToPackage{hyperfootnotes=false}{hyperref}` before `\documentclass` |
| `\hypersetup{hyperfootnotes=false}` does NOT work | `/tmp/fn_b3.log` | `Package hyperref Warning: Option 'hyperfootnotes' has already been used`; dest warnings still 10 | the option is load-time only; recorded because it is the obvious first attempt |

### 5.2 Repository documents consulted

| document | what I took from it |
|---|---|
| `reviewers/README.md` | the common protocol, severity scale, output contract, fail-closed and fresh-eyes rules |
| `reviewers/18_visual_presentation.md`, `13_ufv_compliance.md`, `19_latex_source_reviewer.md` | the three checklists and their hard limits |
| `AGENT_GUARDRAILS.md` sections 1-3, 7 | the number protocol (quote, never compute; convention named), the bias list, "trusting the tolerant tool", "a gate that has never fired" |
| `UFV_COMPLIANCE.md` sections 1-3 | the two deliverable shapes, the formatting table, the numbering rule and its worked example, the system-field keyword rules, the Art. 21/22 prerequisites |
| `WRITING_LAW.md` section 5 | in-figure text near body size; captions above tables and below figures; booktabs; grayscale-safe dual encoding |
| `TEMPLATE.md` sections 0, 2, 3 | the settled font stack, the numeric-citation decision, the two-build toggle, the script-generated table rule |
| `CLAUDE.md` section 1 | venue/status/date facts; the Art. 21 comprovante action |
| `src_utils/_history/_round6/ANCHORS.md` | the cite-the-phrase rule; the near-blank p.4 record (section 2 item 3); the Appendix B float record (section 2 item 1); the `FPDFText_GetFontSize` correction |
| `src_utils/_history/_round6/12_figures.md` | the 93.2 / 66.3 percent figures and their instrument; the CoUrb 5.37 pt / 45 percent note; the nominal-vs-geometry trap |
| `src_utils/_history/_round6/13_layout_measured.md` | the register-probe margin figures, re-derived here from the render rather than taken |
| `src_utils/LEFT_OUT.md` | LO-3 (`\campus` renders nowhere), LO-5 (fig1 upright placement), LO-6 (Ch.4 label size) |
| `src_utils/_history/_round6/AGENT_BRIEF.md` | the build recipe, `tex_errors=0` as part of every build claim, the render-not-text-layer rule |
| `src_utils/check.sh` and the five checker scripts | the gate's own defect history; the glob fix; the self-test discipline |
| `src/Makefile`, `main.tex`, `main_ppgc.tex`, `0_main.tex`, `abntex2-UFV.sty` | the three-target structure, the two switches, the preamble, the front-matter machinery |

---

## 6 · What I could not confirm

1. **The anti-plagiarism certificate, the termo de assentimento and the BBT authorization.**
   Not establishable from the repository. `[VERIFY: process prerequisites — author to confirm with
   the secretariat.]`
2. **The Art. 22 twenty-day calendar math.** No defense date exists in the source
   (`\databanca{[defense date --- pending]}`), so the arithmetic has no input.
   `[VERIFY: set the defense date, then re-check the filing deadline.]`
3. **Whether the defense build is required to carry a capa.** `UFV_COMPLIANCE.md` section 1
   describes a cover page for that build and the document opens on the folha de rosto. The
   operative authority is the PPGCC pre-textual checklist, which I did not open this session.
   `[VERIFY: the pre-textual checklist's cover requirement for the defense build; `\imprimircapa`
   exists in the .sty and is called by neither build.]`
4. **The correct value of `\finalbuildfirstpage`.** Today's front matter implies 8; the
   compliance doc says the AcademicoPG RASCUNHO PDF is authoritative, and that PDF does not exist
   until after the defense. C-1 establishes that 11 is wrong; it does not establish that 8 is
   final. `[VERIFY: reconcile against the RASCUNHO after the deposit.]`
5. **Whether `chktex`/`lacheck` would report anything my subset does not.** The two binaries are
   absent from this machine. My ten checks cover their load-bearing classes for this document, not
   their full rule sets. `[VERIFY: run the real linters on a machine with a full TeX Live, or
   accept the subset.]`
6. **The Ch.3 figure's regeneration path.** I measured its label size but did not look for its
   source; the equivalent search for the Ch.4 figure is recorded in `12_figures.md` and found only
   a `.drawio`. Whether `cbic_mtlnet_arch.png` has a recoverable source is unestablished.
   `[VERIFY: locate a source for figures/cbic_mtlnet_arch.png before proposing a re-export.]`
7. **Whether the four two-page float gaps (V-5) can be closed** without introducing worse
   placement. I measured the gaps; I did not test a `\FloatBarrier` or a re-order.
8. **Whether clickable footnotes can be RESTORED rather than switched off** (E-5). I tested and
   measured the switch-off route (`\PassOptionsToPackage{hyperfootnotes=false}{hyperref}`, no render
   change, warnings and broken links to zero). The alternative is loading `hyperref` explicitly
   ahead of the class machinery so its footnote anchors initialize; that reorders a preamble whose
   load order is deliberate and commented, and I did not build it.
   `[VERIFY: if the author wants working footnote links rather than none, the hyperref load-order
   change needs its own build and its own margin re-measurement.]`

---

## 6b · Reproducing these measurements

Four scripts written this session, all read-only, all committed beside this report:

| script | what it measures |
|---|---|
| `_measure_glyphs.py <pdf> --pages N ...` | on-page glyph size from **geometry**, calibrated against the body font on the same page. Use this for any in-figure type-size question; the nominal-size API is blind to `\includegraphics` scale. The body size is always the modal nominal size on the page being measured, not an option, so the calibration can never be carried over from another page. |
| `_pxdiff.py A.pdf B.pdf` | per-pixel page comparison of two PDFs, plus the `/CreationDate` and `/ID` that explain a hash difference with no render difference. |
| `_bibaudit.py` (run from `src/`) | duplicate keys, same-author-year fragmentation with titles, dangling and uncited keys. |
| `_lint_subset.py` (run from `src/`) | **nine** load-bearing ChkTeX/lacheck classes, since neither binary exists on this machine. Its header names the two classes it does NOT implement, so its silence is not mistaken for coverage. |
| `_kwaudit.py <pdf> <resumo_pg> <abstract_pg>` | the keyword blocks against the UFV system-field rules, read off the render. |
| `_fnlinks.py <pdf> ...` | where each footnote destination actually LANDS versus where its footnote text sits, plus the live link annotations that point there and control anchors on the same document. Existence of a destination is not the test; this is (E-5). Fails on the current build, passes on the one-line-patched build. |

`_evidence/` holds four crops that are the visual basis of V-1 and the Ch.4 comparison:
`p34_figband.png` (the Ch.3 figure at 12 px/pt), `cbic_lbl_residualblock.png` (the 10 px cap-height
label), `p47_figband.png`, `p47_label_spatial.png`. Full-page rasters are not committed; regenerate
any page with `pypdfium2` at `scale=2.2` from `build/main.pdf`.

---

## 7 · Out-of-scope handoffs (one line each)

- **Persona 05 / 06:** `2_fundamentals.tex:170` cites another paper's "Equation 2" and quotes
  `0.7388 ± 0.0205 → 0.8186 ± 0.0123` on a stated convention. I checked the markup, not the
  values or the source.
- **Persona 07:** `apx_b_errata.tex:307` "This article differs from the other two" is the sentence
  E-1 trips on; my finding is about the gate, not about whether the claim is right.
- **Persona 03:** the same sentence is the only place in the document using paper voice in a way a
  reader might misread; a reword would close E-1 at zero claim cost.
- **Persona 06:** the sumário's page numbers in the **final** build (Introduction 11,
  References 80, Appendix E 106) do not match that PDF's own pages; this is a consequence of C-1,
  and the numbers themselves need re-reading once the offset is fixed.


---

<!-- estado-rodada -->
> **Rodada encerrada · último toque 2026-07-28 · sem autoridade.**
> Este ficheiro é registo de proveniência do que foi discutido nesta passagem, não fonte
> de um facto corrente. O que ficou decidido está em [`VEREDITOS.md`](../../../VEREDITOS.md);
> os valores entregues estão em `CLAUDE.md` §0.1. Não copie nada daqui sem confirmar lá.
