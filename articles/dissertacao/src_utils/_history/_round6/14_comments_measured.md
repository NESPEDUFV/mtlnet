# COMMENTS_MEASURED.md — the author's comment-volume question, measured by block

**The author's words:** *"algo que está me incomodando bastante e o execcso de comments, e algo bom
e necessario para mantermos o track de varis inforamcoes criticas, mas sera que não teria como
cortar alguns comentarios ou ser mais direto."*

A prior round answered this with a by-block classification and reported that mechanical compression
of the 48 largest blocks would yield 6 percent, not the 40 percent first estimated. **This round
re-measured from scratch** rather than quoting that, because the tree has changed since (tables were
extracted, chapters edited, this round's own edits landed).

## The measurement

`src/` LaTeX, non-comment lines excluded, comment lines grouped into consecutive **blocks**, each
block classified by whether it contains at least one traceable fact: a file path, a `:line`
reference, a decimal number, a date, a commit hash, a DOI or arXiv id, a page reference, or a review
finding id.

| | Count |
|---|---:|
| total lines in `src/*.tex` | 4,480 |
| comment lines | 1,269 (28 percent) |
| comment blocks | 141 |
| blocks carrying **no** traceable fact | 25 |
| lines in those fact-free blocks | **52** |
| **fact-carrying comment lines** | **1,217 of 1,269 (95 percent)** |

Per file, the heaviest are `apx_a_contributions.tex` at 55 percent, `apx_b_errata.tex` 39 percent,
`5_mobiwac.tex` 38 percent, `0_main.tex` 35 percent, `2_fundamentals.tex` 35 percent.

## What the 52 fact-free lines actually are

Reading all 25 blocks: **18 of them are in `0_main.tex` and are structural section banners** —
`% ---------- DEFENSE BUILD: full front matter ----------`, `% Resumo (PT)`, `% Abstract (EN)`,
`% PRE-TEXTUAL`, `% TEXTUAL`, `% POST-TEXTUAL`, `% Lists (both builds...)`. They are the navigation
of a 445-line preamble and front matter. Removing them would make that file harder to read, not
leaner. Separately, **41 comment lines are purely decorative** (rows of dashes and equals signs
forming banner rules), 15 of them in `0_main.tex`.

The remaining fact-free blocks are the author's own `[NEEDS SIGN-OFF]` markers, whose text explains a
rewrite in prose without citing a file. Those are his decision queue and must stay until he clears them.

> **CORRECTION, 2026-07-28 (finding 751724c3).** This paragraph originally said "the remaining 7
> fact-free blocks are `[NEEDS SIGN-OFF]` markers", which the listing above it contradicts: only some
> are. Re-measured on the current tree with the same classifier, now covering `chapters/*/*.tex` as
> well (the per-section split moved most of the prose there, and the original run could not see it):
>
> **27 fact-free blocks, of which 5 are `[NEEDS SIGN-OFF]` markers.** The other 22 are structural
> banners and section labels in `0_main.tex` (19 of them: `% PRE-TEXTUAL`, `% Resumo (PT)`,
> `% ---------- DEFENSE BUILD ----------`, and the two multi-line provenance notes this round added
> about the hyperref option), one round-5 decision note in `apx_b_errata.tex`, and two blank comment
> lines in `3_cbic/method.tex`.
>
> The paragraph's conclusion is unchanged and is in fact strengthened: the fact-free residue is
> **navigation and sign-off queue**, not commentary, so there is still nothing here to compress. What
> was wrong was the attribution of all of it to one cause. The lesson is the smaller one this round
> kept relearning: a count and a classification are two different measurements, and quoting the first
> as though it settled the second is how a report contradicts its own table.

## Why the big blocks cannot be compressed

The 51 blocks of 8 or more lines total 957 comment lines, and they are where the volume lives. Two
examples, read in full:

- **`5_mobiwac.tex:617` (44 lines)** records why one sentence's attribution was downgraded. It names
  the persona and report that found it, the control that cannot support the original claim and why
  (a disjunction eliminator, not a locator), the repository arm that tests the component directly
  with its numbers (68.36 ± 0.74 against 68.32 ± 0.67, delta −0.04 ± 0.13), the paired Wilcoxon
  result, the file and line of each, and the statement that both figures are quoted rather than
  recomputed.
- **`5_mobiwac.tex:702` (46 lines)** carries the six per-dataset Markov floors with their JSON key,
  the externals' cells, a persistence figure with its generating script and a window-count gate
  (96,326 = 96,326, PASS), a `[correction]` recording that an earlier version of that same figure
  quoted the wrong quantity (a fitted transition table's top-1 accuracy standing in for a share of
  windows), the arithmetic of a derived range verified per dataset, and a note that an internal
  board file still asserts a superseded conclusion.

**That is not commentary. That is the audit trail the number protocol requires**, and
`AGENT_GUARDRAILS N3` makes it mandatory: "any number an agent writes must be traceable to its source
file". Cutting it would not make the source more direct; it would make the next fact gate unable to
follow a figure back to its artifact, which is precisely how the wrong-quantity defect recorded
inside that very block was caught.

## Recommendation

**No compression pass.** The measurement does not support one: 95 percent of comment lines carry a
fact, and the 5 percent that do not are section banners in the preamble plus the author's own
sign-off queue.

Two things that would genuinely reduce what a reader has to walk past, both cheap and neither
losing a fact:

1. **The 41 decorative rule lines** (`% ------------------`) can go. They are pure visual noise in a
   file that already uses blank lines as separators. Saves 41 lines, loses nothing.
2. **The provenance blocks could move** out of the `.tex` files into a per-chapter provenance file
   under `src_utils/`, leaving a one-line pointer at each site. This is the pattern the tables/
   reorganization already used successfully (`tables/README.md` hoisted an 8-line paragraph that had
   been repeated in 16 files, removing 129 comment lines with zero loss). **But it has a real cost
   here that it did not have there:** a provenance comment next to its value is read by whoever edits
   that value; a provenance file one directory away is not. The fact gate follows the comment because
   it is adjacent. I do not recommend this without the author's explicit call, and if he wants it, it
   should be done chapter by chapter with the gate re-run after each.

**What the volume is actually telling us** is that this document has been corrected many times and
each correction was recorded where it happened. That is the property that has caught six of this
round's defects. The honest answer to the author's discomfort is that the comments are the reason the
prose can be trusted, and the price is that the source reads like a lab notebook.


---

<!-- estado-rodada -->
> **Rodada encerrada · último toque 2026-07-28 · sem autoridade.**
> Este ficheiro é registo de proveniência do que foi discutido nesta passagem, não fonte
> de um facto corrente. O que ficou decidido está em [`VEREDITOS.md`](../../../VEREDITOS.md);
> os valores entregues estão em `CLAUDE.md` §0.1. Não copie nada daqui sem confirmar lá.
