# 12_figures.md — three figures: two Portuguese-labelled, two below readable label size

**Written 2026-07-28.** Remit: `src/figures/**` and the `\includegraphics` lines that place them.
Everything measured this round is stated with the instrument that measured it. Where I could not
close an item, it carries a `[VERIFY]` flag rather than a smoothed-over sentence.

**Read this first, because it governs two of the three findings:** for anything visual I measured
the RENDER, not the text layer. A previous audit called the Portuguese figure labels "RESOLVED"
because PDF text extraction found no Portuguese. Both figures at issue are raster PNGs whose text
is not in the text layer at all: `arquitetura_modelo.png` carries a 24327-byte `tEXt` chunk and 18
`IDAT` chunks and no font, so `pdftotext` over the built document cannot see one word of it. The
labels were still there. Every claim below about what a figure says was established by decoding the
raster and looking at it, and, for the labels I changed, by looking at the rebuilt PDF page.

---

## 0 · Summary of the three items

| Item | Verdict | What is now true |
|---|---|---|
| 1. CoUrb architecture figure, six Portuguese labels (COD-017 / PENDENCIAS 3.2) | **DONE** | Translated in the `.drawio` source AND in the PNG. Zero pixels changed outside the six label rectangles. Confirmed in the rebuilt render on p.48. |
| 2. State-distribution figure, reported Portuguese words | **ESTABLISHED: no Portuguese text present** | All 24 text bands inventoried and viewed at native resolution: every one is English. **No change to the image; none needed.** The FILENAME is Portuguese, which is cosmetic; recommended, not applied. Regeneration from the corpora is **NOT RECOVERABLE** and I say why. |
| 3. Two Chapter 5 diagrams at 58 percent of body size (COD-017) | **PARTIAL** | `fig2_model` now measures **11.15 pt, 93.2 percent of body** (was 6.84 pt / 57.2). `fig1_dataflow` now measures **7.93 pt, 66.3 percent** (was 6.84 / 57.2) and does **not** reach "near body size". Author chose the upright placement over a rotated one that measured 10.53 pt. `fig1` therefore stays flagged. |

**Build after my edits, my change measured in isolation** (see §5 for why isolation was necessary):
`DEFENSE: pages=['105'] tex_errors=0 overfull_hbox=0 overfull_vbox=0 undef_cite=0 undef_ref=0
bibtex_problems=0 oversized_floats=0` and `FINAL: pages=['100'] tex_errors=0 overfull_hbox=0
overfull_vbox=0 undef_cite=0 undef_ref=0 bibtex_problems=0 oversized_floats=0`.
**Pagination moved by +1 page in both variants: 104 -> 105 defense, 99 -> 100 final.**

---

## 1 · Item 1 — the CoUrb architecture figure

### 1.1 What was wrong, measured

`src/figures/courb/arquitetura_modelo.png`, included at `chapters/4_courb.tex:104` (anchor phrase
`\includegraphics[width=\textwidth]{figures/courb/arquitetura_modelo.png}`), renders on **p.48** of
the defense build under an English caption and carried six Portuguese labels. I decoded the PNG and
viewed it. All six confirmed present, at these pixel locations (1102x348 raster, origin top-left):

| Portuguese label | ink bounding box in the PNG | drawio cell id |
|---|---|---|
| `Encoder Espacial` | x 103-209, y 19-30 | `enc_spatial_title` |
| `Coordenadas` / `(lat, lon)` | x 37-114, y 53-63 / x 54-99, y 69-81 | `input_coords` |
| `Encoder Temporal` | x 106-217, y 144-155 | `enc_temporal_title` |
| `Timestamps` / `(hora, dia)` | x 41-110, y 176-188 / x 47-105, y 192-204 | `input_time` |
| `Encoder Categórico` | x 100-222, y 258-270 | `enc_categ_title` |
| `Categorias` / `(POI graph)` | x 45-106, y 292-304 / x 43-109, y 308-320 | `input_cat_data` |

Note `Timestamps` and `(POI graph)` were already English; only the Portuguese half of those two
boxes changed.

### 1.2 No drawio renderer exists on this machine — checked, not assumed

- `command -v drawio` -> nothing.
- `/Applications/draw.io.app` and `/Applications/drawio.app` -> absent (I listed `/Applications`).
- `node`, `npx`, `inkscape`, `rsvg-convert`, `pdftocairo`, `gs`, `mutool`, `qpdf` -> **all MISSING**.

So neither the drawio CLI route nor an SVG-intermediate route was available.

### 1.3 The route I chose, and why: surgical text replacement in the raster

I rejected re-rendering the whole mxGraph myself. The file has ~40 cells with rounded corners,
dashed group borders at `dashPattern=8 4`, orthogonal edge routing with explicit waypoints, two
circled `⊕` glyphs and per-cell fill/stroke colours. Redrawing all of that would put every pixel of
a **published, co-authored** figure at risk in order to change six labels. The sanctioned change is
the language of six labels, so I changed six labels and nothing else.

**Establishing the font before touching a pixel.** The drawio cells specify `fontSize=13` and the
PNG exported at scale 1.0 (I verified the mapping: the `#CDEB8B` "Shared Layers Module" fill sits at
drawio (670,328.75)-(810,378.75) and at PNG px (647,146)-(785,193), i.e. `px = drawio - 24` in x and
`- 184` in y, scale exactly 1.0 with a 6 px border). I then fitted the face by rendering existing
**English** labels and comparing ink extents:

| existing English label | original ink | Helvetica 13 px render | delta |
|---|---|---|---|
| `Location Encoder` | 100 x 11 px | 100 x 10 px | +0 / -1 |
| `MTLNet` (bold) | 47 x 8 px | 46 x 9 px | -1 / +1 |
| `Shared Layers Module` (bold) | 136 px wide | 139 px wide | +3 |

Helvetica 13 px, `/System/Library/Fonts/Helvetica.ttc` faces 0 (Regular), 1 (Bold), 2 (Oblique).
Label colours were read out of the raster and match the drawio spec exactly: `#B35A00` = (179,90,0)
spatial, `#336699` = (51,102,153) temporal, `#2D6A2D` = (45,106,45) categorical, black in the input
boxes on the `#DAE8FC` = (218,232,252) fill.

**Fidelity check on the shared word.** "Encoder" appears in both the old and new spatial title. I
recovered the alpha coverage of both and aligned them: best x-offset 48 px, original ink sum 188.5
against new 196.3, **ratio 1.0414**. The new type is the same weight as the old to within 4 percent,
which is sub-pixel rendering phase, not a different font.

### 1.4 Translations applied

Matched to the terms Chapter 4's own English prose uses, verified in `4_courb.tex`: `:98` reads "a
continuous spatial \textit{encoder}, a temporal \textit{encoder} (Time2Vec), and a hierarchical
categorical \textit{encoder} (HGI)"; the subsection headings at `:132`, `:159`, `:174` read
"Spatial Encoder", "Temporal Encoder", "Categorical Encoder"; `:172` reads "hour of day and day of
week".

| was | now |
|---|---|
| Encoder Espacial | Spatial Encoder |
| Coordenadas (lat, lon) | Coordinates (lat, lon) |
| Encoder Temporal | Temporal Encoder |
| Timestamps (hora, dia) | Timestamps (hour, day) |
| Encoder Categórico | Categorical Encoder |
| Categorias (POI graph) | Categories (POI graph) |

`MTLNet` is **unchanged**, as instructed: that is the published CoUrb figure's spelling.
`GLOSSARY.md:44` registers `ST-MTLNet` with a capital N as "a separate registered name, not the
MTLnet rule with a prefix ... it is the published title of the CoUrb paper and keeps that form",
and `4_courb.tex:7-9` records that the 26 prose sites were normalized to `MTLnet` while the
ST-MTLNet form was deliberately left alone. Grep confirms exactly one `MTLNet` and zero `MTLnet` in
the drawio.

### 1.5 Verification of the PNG edit

Pixel diff, new against original, both RGBA 1102x348:

- **5636 px changed of 383496 (1.47 percent).**
- **ZERO changed pixels outside the six declared label rectangles.** I asserted this against an
  explicit allow-list of the six rectangles.
- Changed-row bands are exactly the nine text lines: 18-31, 53-63, 69-81, 144-156, 176-188, 192-204,
  258-270, 292-304, 308-320. Changed-column band is a single run, 37-223.
- **Alpha channel byte-identical** (all 255 before and after).
- Dimensions and mode preserved: 1102x348 RGBA, so `width=\textwidth` places it identically and
  pagination cannot move from this figure.
- File size 90932 -> 53768 bytes. The whole difference is metadata and compression, not content: the
  original carried a 24327-byte `tEXt` chunk (the embedded drawio source drawio writes on export)
  and 18 `IDAT` chunks; mine has one 53711-byte `IDAT` and no `tEXt`. **The `.drawio` file is now
  the source of record for this figure**, which is better than a copy buried in a PNG comment, but
  it is a real difference and I am naming it.

**Render confirmed, not text-extracted.** I rebuilt and rendered p.48 at 4x. The six labels read
Spatial Encoder / Coordinates (lat, lon) / Temporal Encoder / Timestamps (hour, day) / Categorical
Encoder / Categories (POI graph); `MTLNet`, `Location Encoder`, `Time2Vec`, `PoiEncoder + HGI`,
`Category Encoder`, `Next POI Encoder`, `Shared Layers Module`, `CategoryHead`, `NextHead`,
`Category Output`, `Next POI Output` are untouched.

### 1.6 A size finding on this figure, for the record

Not in my remit to fix, and I did not: this raster's labels are drawn at 13 px in a 1102 px-wide
image placed at `width=\textwidth` = 455.0 pt, i.e. **0.41289 pt per pixel, so the labels print at
about 5.37 pt**, against an 11.96 pt body. That is roughly 45 percent of body size, *smaller* than
the two Chapter 5 diagrams that COD-017 flags. Measured directly on the render, the ink height of
"Location Encoder" on p.48 is 4.17 pt at 12 px/pt. Changing it means re-exporting the drawio at a
larger font, which is a content change to a published figure. **Recommendation, for the author to
decide: raise the drawio `fontSize` from 13 to about 20 and re-export at the same pixel width.**
`[VERIFY: the CoUrb architecture figure's own labels print at about 5.37 pt, 45 percent of body.
Untouched this round because the sanctioned change was the language of six labels only.]`

---

## 2 · Item 2 — the state-distribution figure

### 2.1 Established: there is no Portuguese text in this image

`src/figures/courb/distribuicao_estados.png`, included at `chapters/4_courb.tex:284`. 5389x1643 px,
RGBA, 300 dpi. I did not judge from a downscale. I inventoried **every** dark-ink row band in the
full raster (threshold: all channels below 120) and then viewed each at native resolution:

**24 text/ink bands, all accounted for:**

| rows | what it is | language |
|---|---|---|
| 30-65 | the three panel titles | `Florida`, `California`, `Texas` — English (proper nouns) |
| 132-194, 307-369, 482-544, 657-719 | left panel y-axis: rotated title + numeric ticks | `Latitude` — **English** |
| 740-823 | continuation of the rotated `Latitude` glyph column | English |
| 826-894 | x-axis numeric ticks | numerals |
| 1007-1069, 1182-1244, 1357-1420 | remaining y-axis ticks | numerals |
| 1508-1521 | x-axis tick marks | none |
| 1537-1579 | **legend** | `Food`, `Shopping` — **English** |
| 1581-1612 | x-axis title | `Longitude` — **English** |

Crops I actually looked at, at native resolution or 2x downscale of native (never more):
- `(0,0,1886,871)`, `(1796,0,3682,871)`, `(3592,0,5389,871)` — the three panel titles.
- `(0,821,1886,1643)`, `(1796,821,3682,1643)`, `(3592,821,5389,1643)` — plot bodies and x-axes.
- `(0,1490,1800,1643)`, `(1800,1490,3600,1643)`, `(3600,1490,5389,1643)` — x-axis titles + legend.
- `(0,700,320,920)`, `(1790,700,2110,920)`, `(3585,700,3905,920)` — the rotated y-axis titles.

**Verdict: fully English. I recommend NO change to the image.** The author's report of Portuguese
words ("essa tambem tem palavras em portgues") does not hold for this file. The most likely source
of the impression is the **filename**, which is Portuguese and is visible in the `.tex`.

### 2.2 The filename is Portuguese — recommended, deliberately not done

`distribuicao_estados.png` is a Portuguese filename inside an English document. It is cosmetic: it
appears in no rendered output. Renaming it means editing the `\includegraphics` path at
`4_courb.tex:284`, which is inside my remit but is a change the author did not ask for and which
touches a published chapter's source. **Recommendation:** rename to `state_distribution.png` and
update `4_courb.tex:284` in the same commit. I did not do it unilaterally. The same applies to
`arquitetura_modelo.png`/`.drawio` (`model_architecture`), for consistency, if the author wants it.

### 2.3 The three sibling per-state files are also English

`/Users/vitor/Desktop/mestrado/temp/tarik-new/article/_CoUrb_2026__MTL_LocEnc/imagens/subáreas/`
(note: the directory is `subáreas` with an acute accent, not `subareas` as the task brief spelled
it; that is why a literal path probe would miss it). `florida.png`, `california.png`, `texas.png`,
each 5381-5382 x 1834. Same band inventory, same result: `Latitude`, `Longitude`, `Food`,
`Shopping`, numerals. Viewed the Florida left-edge and bottom crops at native resolution.

`distribuicao_estados.png` there is **byte-identical** to the dissertation's copy:
`md5 = 727c260c54f68f405f201759d15e8181` for both.

### 2.4 Regeneration is NOT RECOVERABLE — failing closed, with the measurement

No generator exists. I searched the whole `tarik-new` tree for anything producing this figure: only
two files mention it, `sections/results.tex` and `sections/results_alt.tex`, and both only
`\includegraphics` it. The three notebooks do not produce it. `SIREN_Nova_Implementacao.ipynb` is
the only one with axis labels `Latitude`/`Longitude`, and its cell 22 is a **t-SNE** scatter of
location embeddings coloured by coordinate, not a geographic scatter of POIs. `HGI.ipynb` and
`hgi.py` contain lowercase `latitude`/`longitude` as dataframe columns only. The figure is not under
version control in that tree either (`git log` for its path returns nothing).

The corpora at `/Users/vitor/Desktop/mestrado/data/checkins_by_state/*.parquet` do contain the
needed fields (`placeid`, `latitude`, `longitude`, `category`, `spot`; 21 columns). But **the
published sub-area selection rule cannot be reconstructed**, and here is the arithmetic that
establishes it. Reading each panel's axis ranges off the tick labels and querying unique POIs inside
that window:

| panel | window (lon, lat) | unique POIs in state | inside the window | of those, Food+Shopping |
|---|---|---|---|---|
| Florida | -80.150..-80.115, 25.775..25.810 | 76,544 | 924 | **531** (Food 361, Shopping 170) |
| California | -118.355..-118.320, 34.085..34.120 | 169,145 | 1,126 | **532** (Food 297, Shopping 235) |
| Texas | -96.815..-96.780, 32.770..32.805 | 160,938 | 1,831 | **703** (Food 400, Shopping 303) |

The caption at `4_courb.tex:285` states the sub-regions carry "about 100 POIs per region". Counting
the plotted markers in the published raster by connected-component analysis on the two legend
colours ((237,116,125) Food, (249,165,76) Shopping) gives **coloured-pixel budgets consistent with
roughly 163 to 307 markers per panel** (Florida 51,509 px, California 48,790 px, Texas 92,136 px,
against a ~300 px single-marker core; heavy overlap makes this a lower bound, and the blob counts
alone are 82 to 169 per category). So the published figure plots neither "about 100" nor the 531 to
703 that the axis window contains. There is an unrecorded subsampling or density-grid step between
the corpus and the figure, and **its rule is not in the repository**.

**I did not regenerate it.** A plot that looked like the published figure but plotted a different
POI set would be worse than the current state, which is a correct published figure with an English
label set and a Portuguese filename. `[VERIFY: the published sub-area selection rule for
distribuicao_estados.png is unrecorded. 531 to 703 Food+Shopping POIs fall in each panel's axis
window; the caption says about 100 per region; marker counting suggests roughly 163 to 307 plotted.
The figure is not reproducible from the corpora without that rule. No change made, and none is
needed, because the labels are already English.]`

---

## 3 · Item 3 — the two Chapter 5 diagrams

### 3.1 The source DOES exist, in the paper folder

Contrary to "there is no generator", both diagrams are **TikZ**, at
`articles/[mobiwac]/src/figs/fig1_dataflow.tex` (4899 bytes) and `.../fig2_model.tex` (5511 bytes).
Both are dual-mode: standalone-compilable, or `\input`-able when `\FIGINPUT` is defined. The paper
includes them at `articles/[mobiwac]/src/main.tex:102` via
`\resizebox{0.66\textwidth}{!}{\input{figs/fig1_dataflow}}` and `:114` via
`\resizebox{\columnwidth}{!}{\input{figs/fig2_model}}`.

I compiled both. Both build clean. **But they do not reproduce the committed PDFs:**

| figure | committed in `src/figures/mobiwac/` | rebuilt from `[mobiwac]/src/figs/` |
|---|---|---|
| fig1_dataflow | 391.170 x 177.718 pt | 397.529 x 178.139 pt |
| fig2_model | 283.636 x 196.499 pt | 291.668 x 197.087 pt |

The **text content is character-for-character identical** in both cases (I compared the extracted
strings). The geometry differs by 6 to 8 pt in width. I tried `border=0pt/1pt/4pt`, `[T1]{fontenc}`,
and `lmodern`: none lands on the committed size. `src_v1/figs/` holds an **older, different** design
(fig1 says "raw check-in trail", "POI" instead of "place", one vector set instead of two; fig2 says
"GRU category head" and "shared bidirectional cross-attention"), so it is not the missing variant
either. The committed PDFs are `pdfTeX-1.40.29`, `CreationDate D:20260723144921` and `...922`, one
second apart, so they were built together by a wrapper whose exact preamble is not in the tree.
`[VERIFY: the exact standalone preamble that produced the committed fig1_dataflow.pdf and
fig2_model.pdf is not recoverable from the repository. The TikZ sources at
articles/[mobiwac]/src/figs/ carry identical text but compile 6 to 8 pt wider.]`

### 3.2 Why regeneration at 9 to 10 pt was rejected: it breaks the figures, measured

Regenerating at a larger base font is the preferred fix, so I tried it before falling back. At
`\documentclass[border=4pt,11pt]{standalone}` the label nominal size rises 6.97 -> 7.97 pt. It also
breaks both layouts, because the TikZ node boxes are dimensioned in **millimetres** and do not grow
with the type:

- **fig1_dataflow:** the `trained with no task labels (infomax)` annotation runs into the
  neighbouring box. The `sliding windows` box's left border sits at x = 219.50 pt; the closing
  parenthesis of `(infomax)` ends at x = 221.68 pt. **The text crosses 2.18 pt inside the box.** In
  the committed 10pt figure the same clearance is **+14.85 pt**.
- **fig2_model:** the bold `shared trunk (bidirectional cross-attention x2)` title, 138.83 pt wide
  at 10pt inside a 197.83 pt box, becomes **198.17 pt wide and protrudes 0.50 pt past the fill**.

Both measured on rendered rasters at 6 to 10 px/pt, not judged by eye. Fixing them properly means
re-dimensioning nodes, i.e. redesigning a figure of a paper that is **under review** with a
submitted source that must stay identical. Out of scope for a size fix.

### 3.3 What I did instead, and the measurement discipline that made it honest

These are vector PDFs placed at natural size inside a 455.0 pt text block (`\textwidth` probed
directly by compiling a stub against the real `\documentclass[12pt,a4paper,...]{abntex2}`: 455.0 pt
wide, 708.0 pt high). fig1 was using 391.170 of 455.0 pt; fig2 only 283.636, i.e. **62 percent of
the available width**. Scaling the placement scales the type.

**A measurement trap worth recording, because it would have produced a false claim.**
`FPDFText_GetFontSize` reports the **nominal** size declared inside the embedded XObject and is
blind to the `\includegraphics` scale. After my edit it still returns 6.97 pt on both pages. Had I
reported that, I would have said the fix did nothing. The true on-page size has to come from glyph
**geometry**. Calibrating on the body font on the same page (nominal 11.96 pt; its `o` char-box
measures 5.607 pt, so 2.1330 nominal pt per pt of `o` height) and measuring the in-figure `o`:

| figure | `o` box before | `o` box after | effective size before | after | percent of 11.96 pt body |
|---|---|---|---|---|---|
| fig1_dataflow | 3.208 pt | 3.718 pt | 6.84 pt | **7.93 pt** | 57.2 -> **66.3** |
| fig2_model | 3.208 pt | 5.227 pt | 6.84 pt | **11.15 pt** | 57.2 -> **93.2** |

Cross-check from the nominal size times the placement scale: fig1 6.97 x (455.0/391.170) = 8.11 pt;
fig2 6.97 x (455.0/283.636) = 11.18 pt. The two independent routes agree to within 0.2 pt.

**Glyphs below 9 pt** in the rebuilt defense PDF, by the same nominal-size instrument the round-6
anchor used: still 350 on the fig1 page and 312 on the fig2 page, because that instrument reads
nominal size. On the geometry measure, fig2's labels are no longer below 9 pt and fig1's still are.

### 3.4 The fig1 placement decision, and the option that was measured and not taken

fig1 is 391.170 pt wide naturally, so full `\textwidth` is only a 1.1632x scale and 8.11 pt is the
ceiling for an upright placement. Reaching 9.5 pt needs 1.3630x = 533.16 pt, which overflows the
455.0 pt block. I built and measured the alternative:
`\includegraphics[angle=90,height=0.86\textheight]` gives **10.53 pt, 88.1 percent of body**, builds
105 pp with `tex_errors=0` and zero overfull boxes.

**The author chose the upright placement**, on the grounds that rotating the page turns the
diagram's deliberate left-to-right data flow into a bottom-to-top one and costs the reader a page
turn. So fig1 ships at 66.3 percent of body and COD-017 stays open for it.
`[VERIFY: fig1_dataflow now measures 7.93 pt, 66.3 percent of an 11.96 pt body. WRITING_LAW 5 asks
for in-figure text "near body size"; this is an improvement from 57.2 percent but does not meet it.
The rotated placement that reaches 88.1 percent was built and measured and declined by the author on
reading-orientation grounds. Closing this properly requires re-dimensioning the TikZ node widths in
articles/[mobiwac]/src/figs/fig1_dataflow.tex, which is a change to an under-review paper's source
and outside this round's remit.]`

---

## 4 · Edits applied

| file:line | change |
|---|---|
| `src/figures/courb/arquitetura_modelo.drawio` (6 `value=` attributes, cells `enc_spatial_title`, `input_coords`, `enc_temporal_title`, `input_time`, `enc_categ_title`, `input_cat_data`) | six Portuguese labels translated; every geometry, style, colour and `fontSize` byte untouched; `MTLNet` untouched |
| `src/figures/courb/arquitetura_modelo.png` (binary) | same six labels repainted in Helvetica 13 px; 5636 px changed, zero outside the six label rectangles; 1102x348 RGBA preserved |
| `src/chapters/5_mobiwac.tex:254` | `\includegraphics{...fig1_dataflow.pdf}` -> `\includegraphics[width=\textwidth]{...}`, plus a 10-line comment recording the measurement and the rejected regeneration |
| `src/chapters/5_mobiwac.tex:328` | `\includegraphics{...fig2_model.pdf}` -> `\includegraphics[width=\textwidth]{...}`, plus a 6-line comment |

Line numbers as of 2026-07-28, after my own comment insertions. Anchor phrases, which will outlive
them: `width=\textwidth]{figures/mobiwac/fig1_dataflow.pdf}` and
`width=\textwidth]{figures/mobiwac/fig2_model.pdf}`.

Nothing outside `src/figures/**` and those two `\includegraphics` lines was edited.

---

## 5 · Build result, and a contaminated measurement I had to isolate

**My baseline, taken before any edit:** `DEFENSE: pages=['104'] tex_errors=0 overfull_hbox=0
overfull_vbox=0 undef_cite=0 undef_ref=0 bibtex_problems=0 oversized_floats=0`, `FINAL:
pages=['99'] ... overfull_hbox=0`. This matches ANCHORS.md.

**First rebuild after my edits reported `overfull_hbox=1`, a 113.58371 pt box "in paragraph at lines
112--113".** That is not mine, and I checked rather than assumed. The box is in
`src/tables/frame/bib_errata.tex:112`, an Appendix B table outside my remit, and it comes from a
**parallel agent's in-flight edit**: the file's mtime is `2026-07-28 10:12:57`, later than my
baseline build, `git diff` shows +19 lines against HEAD, and the offending key
`mai2023sphere2vecgeneralpurposelocationrepresentation` (52 characters, `\texttt`, does not
line-break, in a `p{0.42\textwidth}` column) **does not exist in HEAD at all**. That agent's own
comment at `:16-21` documents the same box and says it rebuilt to zero overfull, so the two of us
were measuring each other's half-finished trees.

**So I measured my change alone.** I copied the whole `dissertacao/` folder to `/tmp/iso_build/`,
reverted only the two files the parallel agents are holding (`tables/frame/bib_errata.tex` and
`references.bib`) to `HEAD` inside the copy, confirmed my three edits were present and the long key
absent, and built:

```
DEFENSE: pages=['105'] tex_errors=0 overfull_hbox=0 overfull_vbox=0 undef_cite=0 undef_ref=0
         bibtex_problems=0 oversized_floats=0
FINAL:   pages=['100'] tex_errors=0 overfull_hbox=0 overfull_vbox=0 undef_cite=0 undef_ref=0
         bibtex_problems=0 oversized_floats=0
```

**`tex_errors=0` on both. Zero overfull boxes attributable to my edits. Zero oversized floats.**
`make defense` and `make final`, which pass `-halt-on-error`, both produced PDFs, so the source
compiles for real and not merely under `nonstopmode` recovery.

### 5.1 Pagination moved: +1 page in each variant

**104 -> 105 defense, 99 -> 100 final.** Cause: fig2_model grows from 196.499 to 315.22 pt tall
(1.6042x), and fig1_dataflow from 177.718 to 206.72 pt, so 148 pt of new float height enters
Chapter 5. The two diagrams still land on **pp. 62 and 65** of the defense build, the same pages
ANCHORS.md §2 item 2 records; the added page falls later in the chapter.

The CoUrb architecture figure did **not** move pagination: the PNG kept its exact pixel dimensions
and `width=\textwidth` placement, and it still renders on **p.48**.

### 5.2 `make check` now fails, on page-count claims only, in files outside my remit

```
== recorded page counts vs the measured build ==
measured from the build logs: defense 105 pp, final 100 pp
  STALE CLAUDE.md, PLAN.md, src_utils/PENDENCIAS.md (x2), src_utils/codex_reviewer.md
10 claim(s) stale; re-run with --write to fix
  -> run: python3 src_utils/sync_page_counts.py --write
```

Every other gate passes: repo codenames OK, unresolved `\ref`/`\cite` OK, bibtex OK, sweep-guard
self-tests OK (4), word-count claims reconcile, torn-sentence suspects 0, trapped-prose suspects 0.

**I did not run `sync_page_counts.py --write`.** It rewrites `CLAUDE.md`, `PLAN.md`,
`PENDENCIAS.md` and `codex_reviewer.md`, all outside my remit and all likely being edited by
parallel agents right now; and the count it would write (105/100) is only correct once every
agent's edits are in. **Recommendation: whoever commits last this round runs
`python3 src_utils/sync_page_counts.py --write` against the final tree.** Stated here rather than
done, as instructed.

### 5.3 Two downstream re-checks my pagination shift creates

Both are named in ANCHORS.md as things to re-check after pagination moves, and both are outside my
remit:

1. **The Appendix B float.** ANCHORS.md §2 item 1 says the oversized float is gone and what remains
   is to re-check after pagination moves. My isolated build reports `oversized_floats=0`, so it is
   still clear at 105/100 pp — but that build reverts the parallel agent's two new Appendix B rows,
   so it is not the final tree.
2. **The Resumo page and the near-blank p.4.** ANCHORS.md §2 item 3 fixes p.4 as the
   `Palavras-chave:` page. My isolated build still lists page 4 among the low-text pages in both
   variants, so it did not move, but the Resumo rewrite is another agent's work.

---

## 6 · Source ledger

Every reference is a file in this repository or on this machine, opened by me this session. No
external citations were needed for this task, and none were added.

### 6.1 Numbers -> source -> field -> convention

| number | source | field | convention |
|---|---|---|---|
| body text 11.96 pt | `src/build/main.pdf` pp. 59-66 | `FPDFText_GetFontSize` per character, modal value | nominal font size of the embedded font, as declared in the PDF |
| labels 6.97 pt (and 7.27 pt on a handful of glyphs) | `src/figures/mobiwac/fig1_dataflow.pdf`, `fig2_model.pdf` | same | nominal; **blind to `\includegraphics` scale**, see §3.3 |
| 350 / 312 glyphs below 9 pt | `src/build/main.pdf` pp. 62, 65 | count of characters with nominal size < 9.0, excluding spaces/newlines | ANCHORS.md reports 449 and 427; my count excludes whitespace, which is the difference |
| 6.84 -> 7.93 pt (fig1), 6.84 -> 11.15 pt (fig2) | `/tmp/iso_build/.../build/main.pdf` pp. 62, 65 | `FPDFText_GetCharBox` height of the letter `o`, median | geometry, calibrated against body `o` = 5.607 pt at nominal 11.96 pt on the same page |
| 10.53 pt (rotated fig1) | `/tmp/iso_rot/.../build/main.pdf` p. 63 | `FPDFText_GetCharBox` **width** of `o` (glyph rotated 90 deg) | same calibration |
| `\textwidth` = 455.0 pt, `\textheight` = 708.0 pt | compiled stub against `\documentclass[12pt,a4paper,oneside,openright,english,brazil]{abntex2}` | `\the\textwidth` via `\typeout` | matches `abntex2-UFV.sty:26-27`, `\setlrmarginsandblock{3cm}{2cm}` |
| natural figure sizes 391.170 x 177.718 and 283.636 x 196.499 pt | the two committed figure PDFs | page width/height via pypdfium2 | PDF points |
| 1102 x 348 px, RGBA, 90932 -> 53768 bytes | `arquitetura_modelo.png` | PIL size/mode, `os.path.getsize` | before and after my edit |
| 5636 changed px, 0 outside the six rectangles | before/after rasters | per-pixel RGB inequality | RGBA compared channel-wise; alpha identical |
| 5389 x 1643 px, 300 dpi, 24 ink bands | `distribuicao_estados.png` | PIL + row-band analysis at threshold `max(RGB) < 120` | native resolution, no downscale |
| md5 `727c260c54f68f405f201759d15e8181` | both copies of `distribuicao_estados.png` | `md5 -q` | identical bytes |
| 76,544 / 169,145 / 160,938 unique POIs; 531 / 532 / 703 Food+Shopping in-window | `data/checkins_by_state/{Florida,California,Texas}.parquet` | `drop_duplicates("placeid")`, then coordinate window, then `category in {Food, Shopping}` | POI-level (deduplicated by `placeid`), not check-in level |
| ~163 to 307 plotted markers per panel | `distribuicao_estados.png` | coloured-pixel budget / ~300 px marker core, plus connected-component counts | lower bound; markers overlap heavily |
| ink ratio 1.0414 on the shared word "Encoder" | before/after rasters | recovered alpha coverage, best-offset aligned | sub-pixel phase, not a weight change |
| clearance +14.85 -> -2.18 pt (fig1 at 11pt) | committed vs `/tmp/tikzval/v_fig1_dataflow_11pt.pdf` | box border x from raster fill analysis at 10 px/pt; `)` right edge from `FPDFText_GetCharBox` | negative = text inside the adjacent box |
| 138.83 -> 198.17 pt title width in a 197.83 pt box (fig2 at 11pt) | same pair | exact-colour bbox of `blue!8` fill and `blue!30!black` title at 6 px/pt | protrusion 0.50 pt |
| pages 104/99 -> 105/100, `tex_errors=0` | `src_utils/build.sh . both` | `Output written on ... (N pages` and `^! ` counts | baseline before edits; isolated tree after |

### 6.2 Repository documents consulted

| document | what I took from it |
|---|---|
| `src_utils/_history/_round6/AGENT_BRIEF.md` | the build recipe, the `tex_errors=0` requirement, the render-not-text-layer rule, the deliverable shape |
| `src_utils/_history/_round6/ANCHORS.md` | §1 the COD-017 site; §2 item 2 the 11.96 / 6.97 / 7.27 pt and pp. 62 and 65 measurements; §5 the cite-the-phrase rule |
| `WRITING_LAW.md:146-147` | "in-figure text near body size", the requirement Item 3 is measured against |
| `GLOSSARY.md:41` | `MTLnet` canonical for prose, `MTLNet` is the published CoUrb typesetting |
| `GLOSSARY.md:44` | `ST-MTLNet` is a separately registered name keeping its capital N |
| `chapters/4_courb.tex:7-9` | the 26-site MTLnet normalization deliberately spared the ST-MTLNet form |
| `chapters/4_courb.tex:98,132,159,172,174` | the English terms the six translations were matched to |
| `chapters/4_courb.tex:104,284,285` | the two figure inclusion sites and the state-figure caption's "about 100 POIs per region" |
| `abntex2-UFV.sty:26-27` | the 3/2 cm margins behind `\textwidth` = 455.0 pt |
| `0_main.tex:43-44` | `graphicx` and `adjustbox` already loaded, so the rotated option needed no new package |
| `articles/[mobiwac]/src/figs/fig1_dataflow.tex`, `fig2_model.tex` | the TikZ sources; node dimensions in mm, which is why an 11pt base font breaks them |
| `articles/[mobiwac]/src/main.tex:102,114` | how the paper places them (`\resizebox`), confirming they are meant to be scaled |
| `src_utils/build.sh` | the gate; why `tex_errors` exists and why a PDF existing is not evidence |

---

## 7 · What I could not confirm

1. **The exact preamble that produced the two committed Chapter 5 figure PDFs.** The TikZ sources
   carry identical text but compile 6 to 8 pt wider under every variant I tried. I therefore did
   **not** replace the committed PDFs; both remain the published bytes, and only their placement
   changed.
2. **The sub-area selection rule for the state-distribution figure.** Unrecorded anywhere in the
   repository or in `tarik-new`. The figure is not reproducible from the corpora. This costs
   nothing today, because the figure needs no change.
3. **Whether `make check` passes on the final tree.** It fails now on 10 stale page-count claims in
   four files outside my remit, all of which the round's last committer should refresh with
   `sync_page_counts.py --write`.
4. **Whether the Appendix B float and the Resumo page survive the final pagination.** Clear in my
   isolated build (`oversized_floats=0`), but that build reverts two parallel agents' in-flight
   edits, so it is not the tree that will ship.
5. **The 449 / 427 glyph counts in ANCHORS.md §2 item 2.** I measure 350 and 312 on the same pages
   with the same instrument; the difference is whitespace handling. Not a defect in either record,
   but the numbers are not interchangeable and I did not reconcile them character by character.
6. **Whether the author wants the CoUrb architecture figure's own labels enlarged** (§1.6: about
   5.37 pt, roughly 45 percent of body, i.e. smaller than the diagrams COD-017 flags). Left
   untouched because it is a published figure and the sanctioned change was the language of six
   labels.

---

## 8 · Recommendations for files outside my remit

1. `python3 src_utils/sync_page_counts.py --write`, run by the round's last committer, to move
   `CLAUDE.md`, `PLAN.md`, `PENDENCIAS.md` and `codex_reviewer.md` from 104/99 to the final count.
2. Rename `distribuicao_estados.png` -> `state_distribution.png` and update `4_courb.tex:284`; the
   image itself needs no change. Optionally `arquitetura_modelo.*` -> `model_architecture.*`.
3. Re-export `arquitetura_modelo.drawio` with `fontSize` raised from 13 to about 20, at the same
   1102 px width, if the author accepts a label-size change to a published figure. The `.drawio` is
   now in the tree, so this is a two-minute edit for anyone with drawio installed.
4. Appendix B, `tables/frame/bib_errata.tex:112`: the 113.58371 pt overfull box from the long
   `\texttt` key. That agent's own comment says the row should name the work rather than print the
   key, as the Rußwurm row above it does; the fix appears not to have been applied to the Sphere2Vec
   row. Flagging across remits, not editing.
5. If COD-017 must close for `fig1_dataflow`, the only route that does not rotate the page is
   re-dimensioning the TikZ node widths in `articles/[mobiwac]/src/figs/fig1_dataflow.tex` and
   regenerating. That is a change to an under-review paper's source and, per AGENT_BRIEF §4, would
   have to be applied to both the dissertation and `articles/[mobiwac]/src/` and recorded in that
   article's errata.


---

<!-- estado-rodada -->
> **Rodada encerrada · último toque 2026-07-28 · sem autoridade.**
> Este ficheiro é registo de proveniência do que foi discutido nesta passagem, não fonte
> de um facto corrente. O que ficou decidido está em [`VEREDITOS.md`](../../../VEREDITOS.md);
> os valores entregues estão em `CLAUDE.md` §0.1. Não copie nada daqui sem confirmar lá.
