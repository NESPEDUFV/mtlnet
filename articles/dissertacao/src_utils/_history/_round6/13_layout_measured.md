# LAYOUT_MEASURED.md — the page geometry, probed from the compiled document

**Measured 2026-07-28** by compiling a one-page probe carrying `0_main.tex`'s exact preamble and
printing the memoir length registers with `\typeout`. This is the geometry the document actually
has, not the geometry the preamble asks for.

| Register | pt | cm | UFV manual §7 | Verdict |
|---|---:|---:|---|---|
| `paperwidth` | 597.51 | 21.00 | A4 | exact |
| `paperheight` | 845.05 | 29.70 | A4 | exact |
| `spinemargin` (left) | 85.36 | **3.00** | 3 cm | **exact** |
| `foremargin` (right) | 56.91 | **2.00** | 2 cm | **exact** |
| `uppermargin` (top) | 85.36 | **3.00** | 3 cm | **exact** |
| `lowermargin` (bottom) | 56.91 | **2.00** | 2 cm | **exact** |
| `textwidth` | 455.00 | 15.99 | derived | consistent |
| `textheight` | 702.78 | 24.70 | derived | consistent |
| `baselineskip` | 17.99 | | 1.5 spacing on 12 pt | **1.500x** exact |
| `headheight` | 14.50 | 0.51 | not specified | |
| `footskip` | 30.00 | 1.05 | not specified | |

Consistency: the vertical registers sum to 845.05 pt against a paper height of 845.05 pt (delta
0.00). The horizontal registers sum to 597.26 pt against 597.51 pt, a **0.24 pt** shortfall, which is
`\checkandfixthelayout[fixed]` refusing to round the text width to a whole number of points. 0.24 pt
is 0.008 cm and is invisible.

**So the four margins and the line spacing are exactly what the manual requires, verified by
measurement rather than by reading the preamble.** The `[fixed]` argument in
`\checkandfixthelayout[fixed]` is load-bearing: without it memoir rounds the text block to whole
lines and the bottom margin drifts to 1.5 to 1.6 cm, which is the defect the preamble comment at
`0_main.tex:30-33` records as gate D-1.

## The author's question: is local formatting doing work that should be global?

Full inventory of every non-comment size, spacing and box override in `src/`:

| Command | Count | Where | Verdict |
|---|---:|---|---|
| `\renewcommand` | 24 | `0_main.tex` preamble only | **correctly global** (caption names, heading fonts, `\@biblabel`) |
| `\vspace` | 26 | `0_main.tex` front matter (12), `abntex2-UFV.sty` (10), two table files (4) | front matter and the sty are structural; the table cases are caption-to-note gaps |
| `\centering` | 22 | inside `figure`/`table` environments | **correct** (float-local by definition) |
| `\large` | 14 | `abntex2-UFV.sty` (11), `0_main.tex` front matter (3) | title-page typography, structural |
| `\small` | 5 | the four errata tables + `bib_errata` | **legitimately local**: dense quoted-prose tables |
| `\footnotesize` | 5 | table notes and `longtable` continuation lines | **legitimately local** |
| `\singlespacing` | 3 | folha de rosto, Resumo, Abstract | **required**: ABNT sets front matter single-spaced |
| `\scriptsize` | 2 | `5_mobiwac.tex:430, :518` | inside the `\sd{}` macro for the plus-minus spread; correct |
| `\setlength{\tabcolsep}` | 1 | `tables/mobiwac/datasets.tex:22` | one wide table; local is right |
| `\raggedright` | 1 | `tables/frame/lineage.tex:19` | one column of a table |
| `\adjustbox`/`resizebox` | 5 | four wide result tables | **legitimately local** |
| `\needspace` | 0 | — | removed in round 5, replaced by a `minipage` |

**Finding: nothing global is being simulated locally.** Every override is either in the preamble
(where global belongs), in the `.sty` (structural), or attached to one float that genuinely differs
from body text. The two patterns worth noting are conventions rather than defects:

1. `\small` is set **inside** `\begin{table}` in four errata tables, but **outside** as a
   `{\small ...}` group wrapping `bib_errata.tex` — because that one is a `longtable`, which is not a
   float and so has no group of its own to set it in. That asymmetry is exactly what made the lost
   brace of `6d780b58` possible, and it is now commented in the file.
2. Two table files place a `\footnotesize` note **after** `\end{tabular}` inside the float. That is
   the repository's convention for a table note and is consistent across both.

**Compared against the Germano exemplar** (same advisor, defended): that tree sets `\singlespacing`
and `\vspace` in the same front-matter positions and wraps one table in `{\footnotesize ...}`. The
practice here matches it.

**Recommendation: no change.** The author's suspicion was reasonable and the measurement does not
support it. What the inventory does argue for is a one-line comment on the two `\small` conventions
so the next agent does not "normalize" the `longtable` group away.


---

<!-- estado-rodada -->
> **Rodada encerrada · último toque 2026-07-28 · sem autoridade.**
> Este ficheiro é registo de proveniência do que foi discutido nesta passagem, não fonte
> de um facto corrente. O que ficou decidido está em [`VEREDITOS.md`](../../../VEREDITOS.md);
> os valores entregues estão em `CLAUDE.md` §0.1. Não copie nada daqui sem confirmar lá.
