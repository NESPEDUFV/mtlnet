# 24 — The supplementary volume, the appendix move, and the gradient-cosine appendix

**Track:** the advisor's ruling on the appendices, plus a new appendix.
**Date:** 2026-07-29. **Inherited state:** commit `3bd47d5d`; defense 108 pp, academico 105 pp,
ppgc 109 pp; tex_errors 0, overfull 0, undefined 0, bibtex 0.

Every number below carries the command that produced it, per `AGENT_GUARDRAILS.md` §4b V1. All
commands run from `articles/dissertacao/` after `source src_utils/texenv.sh`.

---

## 1 · What changed

### Step 1 — `main_extra.tex`, a second deliverable

A new **separate document** (not a fourth build of the dissertation) carrying Appendix B (errata)
and Appendix D (the label-history benchmark).

- `src/main_extra.tex` — entry file and the canonical explanation of what the volume is.
- `src/0_extra.tex` — its own preamble, front matter, table of contents, opening statement
  (`About this volume`), the two appendices, and its own bibliography.
- `src/Makefile` — new target `extra` → `build/main_extra.pdf`, plus `check-extraxrefs`.

It does **not** follow the thin-shim pattern of `main_ppgc.tex`/`main_academico.tex`, and the
header says why: those two set a switch and `\input{main.tex}`, so they are the same document.
This one has a different title, a different reader, and must not acquire the dissertation's front
matter or its six chapters.

**Appendix letters B and D are preserved in the new volume** (`\setcounter{chapter}` before each
`\include`). Measured reason: `grep -n 'Appendix [A-E]' GLOSSARY.md` → lines 41, 51, 53, 73, where
41 and 73 name **Appendix B** as the errata appendix and 51 names **Appendix D** as the
label-history benchmark. Renumbering them A and B would silently repoint every external reference.
The main document's remaining appendices keep A, C, E for the same reason, so its lettering now
reads **A, C, E, F** with two deliberate gaps.

**Cross-volume references.** The two appendices contain 46 `\ref` sites into the dissertation
(`ch:cbic`, `ch:courb`, `ch:mobiwac`, `sec:intro:organization`, four float labels). Compiled
alone, every one would render `??`. `0_extra.tex` declares them as nine frozen
`\dissertationlabel{label}{number}` pairs, so no appendix prose was edited. Each is anchored on a
real `\hypertarget` in the opening statement, so no link is dead.

> Command: `python3 src_utils/check_extra_xrefs.py`
> → `OK — 9 frozen cross-volume label(s) covering 46 reference site(s); 9 verified against the main build`

### Step 2 — B and D out of the main document

`0_main.tex`: the two `\include`s removed; `\setcounter{chapter}` added so C and E keep their
letters.

**Eight `\ref`/prose pointers rewritten, not deleted** — anchored by phrase, per file:

| File | Was | Now |
|---|---|---|
| `chapters/1_introduction.tex` | "listed in the errata appendix" | "listed in the errata appendix of `\extravolume`" |
| `chapters/3_cbic.tex` (preface) | "listed in Appendix B" | "listed in Appendix~B of `\extravolume`" |
| `chapters/3_cbic/method.tex` (footnote) | `Appendix~\ref{apx:errata}` | `Appendix~B of \extravolume` |
| `chapters/3_cbic/method.tex` (×2 footnotes) | `Table~\ref{tab:apx:cbic-errata}` | `Appendix~B.1 of \extravolume` |
| `chapters/4_courb.tex` (preface) | `Appendix~\ref{apx:errata}` | `Appendix~B of \extravolume` |
| `chapters/5_mobiwac.tex` (preface) | "recorded in the errata appendix" | "recorded in Appendix~B of `\extravolume`" |
| `chapters/6_conclusion.tex` | `Appendix~\ref{apx:errata}` | `Appendix~B of \extravolume` |
| `chapters/apx_a_contributions.tex` | `Appendix~\ref{apx:ceiling}` | `Appendix~D of \extravolume` |
| `chapters/5_mobiwac/05_setup.tex` (×2) | `Appendix~\ref{apx:ceiling}` | `Appendix~D of \extravolume` |

`\extravolume` is one macro defined in `0_main.tex`, so all pointers name the volume identically.

**Why the two table pointers became section pointers.** Measured across the two builds' aux trees:
the appendix letter and its section numbers survive the move (`apx:errata` B→B,
`apx:errata:cbic` B.1→B.1) but **table numbers do not** (`tab:apx:cbic-errata` 11→1), because table
counters restart in a document holding two appendices instead of five. Writing "Table 11" would be
wrong and "Table 1" would drift; the stable target is the section.

### Step 3 — Appendix F, the gradient-cosine appendix (NEW)

`src/chapters/apx_f_cosine.tex` + `src/tables/frame/cosine.tex` +
`src/figures/fig_gradient_cosine.png`, placed after the existing appendices in the **main**
document at the author's request. **Chapter 5's body prose is untouched.**

Source of record: `src_utils/_history/_round7/gradient_cosine_observations.parquet` (3,900 rows).
Derivation: `src_utils/_history/_round7/cosine_stats.py`, which asserts its own structure before computing.

> Command: `python3 src_utils/_history/_round7/cosine_stats.py`
> → `STRUCTURE OK  states=['alabama','arizona','florida','georgia']  rows=3900  per-state={'alabama':250,'arizona':250,'florida':3150,'georgia':250}`

**The result, at the independent unit:**

| dataset | unit | n | obs | mean | 95% CI | TOST p | t p | sign p (floor) | slope p |
|---|---|--:|--:|--:|---|--:|--:|--:|--:|
| florida | configuration mean | 12 | 3,150 | +0.00026 | [−0.00118, +0.00170] | 1.3e−16 | 0.6965 | 0.7744 (0.0005) | 0.7108 |
| alabama | fold mean | 5 | 250 | +0.01119 | [+0.00399, +0.01840] | 5.8e−05 | 0.0125 | 0.0625 (0.0625) | 0.0058 |
| arizona | fold mean | 5 | 250 | +0.00150 | [−0.00511, +0.00812] | 1.7e−05 | 0.5621 | 1.0000 (0.0625) | 0.5685 |
| georgia | fold mean | 5 | 250 | +0.00385 | [+0.00158, +0.00612] | 3.0e−07 | 0.0093 | 0.0625 (0.0625) | 0.0470 |

Pooled: mean +0.001182, **91.28%** of observations inside ±0.05, range [−0.3407, +0.5802].
Equivalence holds at **every** unit (observation, fold series, configuration) for all four.

---

## 2 · Three things the data forced the prose to say carefully

**(a) The unit of independence.** The 50 per-epoch cosines within a fold are one training
trajectory, not 50 independent draws. Every reported p-value is on fold means (n=5) or
configuration means (n=12). Observation-level tests are anti-conservative and none is quoted as
significance.

**(b) Alabama and Georgia are NOT reported as significantly positive.** Both have 5/5 positive fold
means and a t-test that rejects (p=0.0125, p=0.0093), but the exact sign test returns **0.0625 for
both, which is its floor at n=5** — no distribution-free test can reach 0.05 there. The appendix
says the tendency *recurs across datasets* (a real observation, stronger than either alone) and
that *five folds per dataset cannot establish it*. The table prints the floor beside the p-value
in a `†` footnote so the reading cannot be lost.

**(c) The equivalence is about the MEAN, not every observation.** 91.28% of observations lie inside
the margin and the tails reach −0.34/+0.58. The prose and the figure caption both say so; "all
observations" would have been false.

**Georgia is not one of the dissertation's six datasets.** Measured:
`grep -v '^[[:space:]]*%' tables/mobiwac/datasets.tex | grep -E '^(AL|AZ|FL|TX|CA|Istanbul)'` → six
rows, no Georgia; and `chapters/5_mobiwac/02_related.tex` says outright "and Georgia, which this
dissertation does not otherwise use". The appendix therefore names which **three** of its four
datasets are the dissertation's and what the fourth is. It also flags that Ch.5's related-work
section already reports this diagnostic on the same four states with **different** numbers
(+0.001 pooled, largest per-dataset +0.0032) from a development-time preparation — close to my
pooled +0.00118 but *not* to my largest per-dataset +0.0112. Two separate measurements; the
appendix says so rather than letting a reader read a contradiction.

**The extension claim is bounded to what was varied.** Twelve configurations (loss weight,
schedule, procedure) answer "you tuned your way into it": all 12 equivalent on their own folds,
means spanning [−0.00261, +0.00457]. Four datasets answer "it is a quirk of Florida". Neither
touches **architecture** — every run is MTLnet cross-attention — so the appendix says the property
is suggested to belong to the *task pair*, states that architecture is the one factor not varied
and the one most likely to change the answer, and specifies the run a reader would need.

---

## 3 · Measurements, before and after

| What | Before (`3bd47d5d`) | After | How |
|---|---|---|---|
| defense pages | 108 | 101 | `bash src_utils/build.sh src both` |
| academico pages | 105 | 98 | same |
| ppgc pages | 109 | 102 | `build/main_ppgc.log` |
| supplementary volume | did not exist | 19 pp | `build/main_extra.log` |
| tex_errors, all builds | 0 | 0 | `build.sh` + `make` (`-halt-on-error`) exit 0 |
| overfull hbox/vbox | 0 | 0 | `build.sh` |
| undefined refs / cites | 0 / 0 | 0 / 0 | `build.sh`; `??` count in the render = 0 |
| `make check` | RC=0 | RC=0 | `(cd src && make check)` |
| main-document appendices | A B C D E | A C E F | rendered headings in `build/main.pdf` |

**Overleaf viability of the supplementary volume.** Verified by running the bare sequence in a copy
of `src/` with `build/` excluded, no `make`, no format dump:

```
pdflatex main_extra && bibtex main_extra && pdflatex main_extra && pdflatex main_extra
```

→ rc=0 on all four, **19 pages, tex_errors 0, undefined refs 0, undefined cites 0, overfull 0,
4 `\bibitem` in `main_extra.bbl`, 0 BibTeX warnings**.

**The bibtex argument is asymmetric and it matters.** With no `-output-directory` the aux lands at
the source root, so the argument is `main_extra`; under `make extra` it is
`build/main_extra-aux/main_extra`. Measured: the wrong form exits **1** with
`I couldn't open file name 'build/main_extra.aux'`, which **stops an `&&` chain** and, in a
click-to-compile editor, silently leaves every citation unresolved. Both forms are written down in
`main_extra.tex` and in the Makefile recipe.

---

## 4 · New gate: `check_extra_xrefs.py`

Guards the nine frozen cross-volume numbers in three directions — **STALE** (frozen value ≠ the
number the main build printed), **MISSING** (a `\ref` target neither defined in the volume nor
declared), **DEAD** (a declaration nothing references). The third matters because a dead
declaration is what makes the other two look green.

Validated in **both** directions before it reports, via `--selftest` which builds a synthetic tree
per defect:

> `python3 src_utils/check_extra_xrefs.py --selftest`
> ```
> selftest PASS: correct tree passes
> selftest PASS: stale number detected
> selftest PASS: missing declaration detected
> selftest PASS: dead declaration detected
> selftest PASS: absent aux skips loudly
> ```

The self-test runs before the gate every time; if it fails, the gate refuses to report. Wired into
the Makefile as `check-extraxrefs`.

---

## 5 · Defects I introduced and fixed, and what caught each

Recorded because the mechanism is what generalizes.

1. **A past-tense "VERIFIED" claim written before the verification.** `main_extra.tex`'s header
   said the bare Overleaf sequence had been run and pointed at a transcript, before any such run
   existed — and the sequence it quoted (`bibtex build/main_extra`) turns out to **fail**. Caught by
   an audit. Fixed by actually running it and quoting the measured output; the header now records
   that the earlier claim was wrong, so the next reader does not restore it.
2. **The same defect in a second file.** The Makefile comment carried the identical claim. Both are
   now anchored to the run's printed numbers rather than to a pointer.
3. **A fabricated citation key.** The appendix cited `\cite{lakens2017equivalence}` — a key invented
   from the author's name and the topic. The build caught it as one undefined citation. The real key,
   already used by Ch.5 for the same procedure, is `lakens2017tost`, verified against the
   `references.bib` entry.
4. **Trapped prose — the repository's most persistent defect class, reintroduced inside a comment
   about verification.** My `[round7]` block ran straight into the following prose line, so the
   **entire margin-justification paragraph** — the appendix's explanation of why ±0.05 is the right
   threshold — was absent from the PDF with a clean build. Caught by `check_trapped_prose.py`.
   Fixed with a blank comment line; verified present in the render, not just in the source.
5. **A wrong interval bound.** Wrote Florida's configuration-mean span as [−0.00214, …]; −0.00214 is
   the second-lowest value, the minimum is −0.00261. Caught by an audit against my own printed
   output. `cosine_stats.py` now prints the span so it is quoted rather than eyeballed.
6. **A mis-cited provenance line.** A `0_main.tex` comment cited `GLOSSARY.md:51` as naming
   "Appendix B"; line 51 names Appendix D, and the Appendix-B references are lines 41 and 73. The
   lettering decision was unaffected but the cited evidence was wrong.
7. **A dataset list not revisited when the count changed.** The unit sentence said "fold means for
   Alabama and Arizona" while the table below it listed four datasets. **Caught by reading the
   rendered page**, not the source.
8. **An unsourced size claim.** "Alabama and Georgia are the smallest datasets here" — Georgia is
   not in the dissertation's dataset table, so no committed artifact states its size and I had not
   measured it. Replaced with a precision statement derivable from the observations themselves.

Two instrument failures worth recording. My own file-attribution parser for overfull boxes printed
**0** while `build.sh` correctly reported **2** — I distrusted the tool reporting success, per
§2.3b, and located the boxes by line number instead. And `make ppgc`/`all3` failed repeatedly with
`Extra }` and `Missing \begin{document}` from **truncated aux files** left by interrupted
concurrent builds, not from any source defect (the source is brace-balanced). `rm -rf build` and a
serial rebuild clears it; `-j3` on a tree another process is building is the cause.

---

## 6 · `[VERIFY]` flags

- **`[VERIFY]` per-dataset extension to California, Texas, Istanbul.** Not measured. Their
  observations are not in the parquet, so the appendix stops at four datasets and says so in the
  prose, the table caption, the figure caption and the extension section. The flag in
  `apx_f_cosine.tex` names the jobs and records three superseded runtime estimates (47×, stale-log,
  3.3×) with the lesson each carries. **No runtime figure appears in the appendix prose** — a
  runtime is not a result, and each of these was wrong before it was right.
- **`[VERIFY]` architecture coverage is zero.** Every observation is MTLnet cross-attention. The
  appendix states this as a bound, not a hedge, and specifies the experiment that would settle it.

## 7 · `[NEEDS SIGN-OFF]`

1. **`apx_f_cosine.tex`, the whole appendix.** New frame prose making a **mechanistic claim**
   (orthogonality explains why a balancer has nothing to fix and why hard sharing is not costly
   here, which is why the representation mattered more than the sharing scheme) and a **bounded
   extension claim**. Neither is in any paper's claim whitelist → new claims under
   `AGENT_GUARDRAILS` §3 C2.
2. **`0_extra.tex`, `About this volume`.** New frame prose asserting that *the dissertation is
   complete without this volume* — a claim about the main document that is the author's to make.
3. **`chapters/5_mobiwac/05_setup.tex`, two pointer targets in an under-review chapter.**
   Author-authorized in session after being shown the parity measurement: the submitted manuscript
   contains **zero** occurrences of `Appendix`, `apx:` or `label-history` (raw grep, comments
   included) and says "on three grounds" where the dissertation says "four", so the paragraph is
   already a dissertation-only expansion and these pointers have no counterpart in the manuscript.
   An `ERRATA.md` entry is owed in `articles/[mobiwac]/` if that paragraph ever enters the
   manuscript.
4. **Eight rewritten errata pointers** across the frame and the two published chapters' prefaces.
   Preface prose is dissertation-authored, so no errata row is owed, but they are public pointers.

## 8 · What I did not do

- Did not touch Chapter 5's body prose beyond the two authorized pointer targets.
- Did not add a Ch.5 pointer to Appendix F — that would be an edit to an under-review chapter for
  no reader benefit; the appendix is reachable from the table of contents.
- Did not measure California, Texas, or Istanbul.
- Did not re-fix the `apx_d_ceiling.tex:110` trapped-prose instance (fixed separately by the author).


---

<!-- estado-rodada -->
> **Rodada encerrada · último toque 2026-07-29 · sem autoridade.**
> Este ficheiro é registo de proveniência do que foi discutido nesta passagem, não fonte
> de um facto corrente. O que ficou decidido está em [`VEREDITOS.md`](../../../VEREDITOS.md);
> os valores entregues estão em `CLAUDE.md` §0.1. Não copie nada daqui sem confirmar lá.
