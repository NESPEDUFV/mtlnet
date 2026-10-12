# src/ — the dissertation working copy

Single-source LaTeX for Vitor H. O. Silva's UFV/PPGCC dissertation. Skeleton derived from the
Germano tree (`../exemples/germano/`, same advisor) per TEMPLATE.md §0; the kept-vs-stripped
ledger is the header comment of `0_main.tex`.

## Layout (restructured 2026-07-24; src_utils/ externalized 2026-07-24)

`src/` is kept as clean as possible so it can be pasted straight into Overleaf: it contains ONLY
what compiles. All support material lives in `src_utils/`, a SIBLING of `src/` (one level up),
never inside it.

```
articles/dissertacao/
  src/                        <-- paste THIS into Overleaf; compiles standalone
    main.tex                  entry point for the DEFENSE build (and, with \FINALBUILD, the deposit)
    main_ppgc.tex             entry point for defense + approval sheet; TWO lines of content
    content.tex               the document body (front matter + \include list); main*.tex wrap it
    abntex2-UFV.sty           UFV machinery (Germano tree)
    abntex2-num.bst           numeric bibliography style
    references.bib            single global bibliography
    chapters/                 six chapters + five appendices, PLUS three per-section directories:
                                3_cbic/    intro basis method results conclusion
                                4_courb/   intro related methodology results conclusion
                                5_mobiwac/ 01_introduction .. 08_conclusion
                              The three paper chapters were split on 2026-07-28 to match the
                              one-file-per-section layout of the original paper sources; each
                              chapter master now holds its preface and a list of \input lines.
                              ANY TOOL THAT GLOBS chapters/*.tex MISSES 55 PERCENT OF THE PROSE.
                              Four checkers had to be fixed for exactly this; use
                              chapters/*.tex AND chapters/*/*.tex.
    figures/ tables/          chapter assets (tables extracted one table per file)
    dissertacao.pdf           current DEFENSE build (only PDF at the root; copied from build/)
    Makefile                  build + lint targets
    build/                    ALL compile output lands here (gitignored)
  src_utils/                  <-- SIBLING of src/; NOT pasted into Overleaf
    README_SRC.md             this file
    check.sh                  lint hook (linted target is ../src)
    evidence/BIB_MERGE_REPORT.md       bibliography merge/key-mapping record
    _history/_archive/handoffs/HANDOFF_v1.md             author handoff note
    _history/_archive/reviews_v1/DECISOES_PENDENTES_ptBR.md  author decisions (pt-BR)
    evidence/cbic_recompute_result.md  + _history/_archive/handoffs/cbic_recompute_handoff.json  (CBIC dataset counts)
    adaptation_ledgers/       3_cbic / 4_courb / 5_mobiwac ADAPTATION_LEDGER.md (feed Appendix B)
    _history/_archive/reports_2026-07/FRAME_INTEGRATION_REPORT.md
    _history/                 closed audit rounds (_round6.._round14), reviews, specialists, _archive/
    evidence/                 provenance reports the delivered text cites (BIB, licensing, CBIC, ETL)
```

Nothing in `src/` `\input`s or references anything in `src_utils/` (the ledger/report references
in the chapter sources are provenance comments only), so pasting `src/` alone into Overleaf
compiles with no missing files.

## Build (two modes, one source; UFV_COMPLIANCE §1)

```
make            # or `make defense` -> build/main.pdf (108 pp), copied to ./dissertacao.pdf
make academico  # -> build/main_academico.pdf (105 pp; AcademicoPG body-only upload)
                # `make final` still works and forwards here, printing that it was renamed
                # on 2026-07-29; it does NOT write build/main_final.pdf any more.
make ppgc       # -> build/main_ppgc.pdf  (109 pp; the defense PDF plus the approval sheet)
make check      # the lint gates; see below
make clean      # empty build/
```

THREE targets, THREE entry files, ONE source, selected by two switches. `main.tex` is the real one;
`main_academico.tex` and `main_ppgc.tex` are two-line shims that set a switch and read it, so every
build is selectable as a compile root in Overleaf or a GUI editor.

**The canonical explanation of the build shape lives in the `src/main.tex` header comment, not
here.** What each build is, which switch selects it, why both switches use the `\ifdefined` guard
pattern, and what the nested-`\if` scanning hazard actually is: read it there. That file is inside
`src/`, so it travels with an Overleaf paste and is in front of whoever opens the source; this
README is a sibling of `src/` and does not travel. Until 2026-07-29 the same story was told five
times across the tree and three of the copies had drifted, one of them documenting a `make final`
command that silently produced the defense document. One telling, in the file a reader already has
open, is the fix.

What this file keeps is the material that genuinely belongs outside the paste and is not in that
header: the TeX tree and `texenv.sh`, the verification protocol, and the gate suite (all below).

`main_ppgc.tex` holds two lines of content, and so does `main_academico.tex`: each sets one switch
and `\input`s `main.tex`, so no build can drift from another except where a switch says it should.
Do not add content to either. Anything belonging in every build belongs in `0_main.tex`; anything
belonging only to one build is gated there on `\ifapprovalsheet` or `\ifdefensebuild`.

**The deposit build numbers from a different page than the other two.** It has 7 pre-textual pages
against the defense build's 10, so `\finalbuildfirstpage` in `main.tex` is **8**, not 11. It was 11
until 2026-07-28, which made every printed page number in the deposited PDF run three ahead of its
physical page. If you change the front matter, re-derive it: count pre-textual pages in the render and
add one (UFV_COMPLIANCE §4.4).

UFV: two BUILDS are required (full-front-matter defense PDF + body-only AcademicoPG upload); the
manual governs the submission and the final PDF, not the LaTeX source.

Each target compiles into its OWN aux tree at `build/<stem>-aux/` and its `.pdf`, `.log` and `.blg`
are copied back into `build/`, so every documented path (`build/main.pdf`, `build/main_academico.log`,
and the rest) stays true while the three targets can run concurrently — `make all3`. Before
2026-07-29 they shared one `build/chapters/`, and two simultaneous builds corrupted each other's aux;
the reasoning and the exact error message it produces are in the `\include` block of `0_main.tex`.
Input paths (`figures/`, `chapters/`) resolve relative to the src root regardless of the output
directory, so no `graphicspath` change is needed.

## TeX tree

Requires TeX Live with `abntex2`, `newtx`, `fontaxes`, `xstring`, `enumitem`, `multirow`,
`adjustbox`, `collectbox`, `xkeyval`, `subfig`, `lastpage`, `textcase`, `xurl`, `kastrup`,
`tex-gyre`, `txfonts`. On this machine those live in a **usermode tree** at `$HOME/Library/texmf`,
not in the system TeX Live tree, and `pdflatex` itself is at `/Library/TeX/texbin`, which is not on
a non-interactive `PATH`.

**`source src_utils/texenv.sh` before `make`.** It sets the four variables and records why each is
needed. Two distinct failures if you skip it, and the second one misleads:

| Missing | Symptom | What it actually is |
|---|---|---|
| `TEXMFHOME` | `LaTeX Error: File 'abntex2.cls' not found` | honest: the class is not on the path |
| `TEXMFVAR` | `!pdfTeX error: Font ntx-Regular-tlf-ot1r at 657 not found ==> Fatal error occurred, no output PDF file produced!` | **not** a missing font. Both the `.tfm` and the `.pfb` are present in the home tree. What is missing is the font **map**: newtx registers its 36 `ntx-*` entries in the usermode updmap output at `$TEXMFHOME/.texmf-var/fonts/map/pdftex/updmap/pdftex.map`, and the system map has none. `kpsewhich -var-value TEXMFVAR` reports an unreadable path here, so the value cannot be probed and must be set. |

`build.sh` carries the same defaults so it works when invoked directly.

## Verifying a build

Run **both** tools and read `tex_errors`:

```
source src_utils/texenv.sh
(cd src && make defense && make academico)   # -halt-on-error -> the honest pass/fail
./src_utils/build.sh src both            # the report, including tex_errors
```

`build.sh` runs `-interaction=nonstopmode`, under which pdflatex **recovers** from an error and still
writes a PDF. That is how commits `6d780b58` through `a880632b` shipped "104/99 pp, 0 overfull,
0 undefined" out of a source tree carrying `! Extra }, or forgotten \endgroup` (a brace lost from the
`{\small ...}` group in `tables/frame/bib_errata.tex` during the tables reorganization). `make`
produced nothing that whole time; nobody ran it. `build.sh` now reports `tex_errors=N` and fails on
it. **A PDF existing is not evidence the source is correct.**

## The gate suite, and why each gate exists

`make check` runs `src_utils/check.sh`. It should exit **0**. It exited **2** for the whole of round 6
on two false positives while six commit messages said "all gates pass" — read the exit code, not the
output. The false positives are now exempted where the exemption is true (`apx_b_errata.tex` may say
"this article", because it is discussing the articles; "Pareto" is the optimization term and was never
a verdict verb) and each exemption carries its reasoning in `check.sh`.

Beyond the word sweeps, five gates exist for **silent** defect classes: things that compile clean,
raise no LaTeX warning, and still reach the reader wrong. Each self-tests in both directions before it
reports; **if one prints only OK and no self-test line, distrust it.**

| Gate | The class | Why nothing else sees it |
|---|---|---|
| `build.sh` `tex_errors` | The source does not compile | `nonstopmode` recovers and writes a full PDF, which the script measured and certified clean |
| `check_trapped_prose.py` | A prose line swallowed by an unterminated comment | Builds clean; the reader sees a sentence with a piece missing. Twelve instances to date |
| `check_torn_sentences.py` | A body line opening mid-sentence, its antecedent gone | Same: legal LaTeX, broken prose |
| `check_doubled_macro.py` | `\\ref{...}` with a doubled backslash | pdflatex raises nothing (both halves are legal) and `undef_ref` stays truthfully at 0, because there is no reference to leave undefined |
| `check_tex_root.py` | A `% !TeX root` directive missing, or naming a file that does not exist | Invisible to `make`, which reads `main.tex` and never looks at a magic comment. Two separate instances in one week |
| `check_negative_parallelism.py` | Density of `rather than` / `X, not Y` / `instead of` above a ceiling | It was a standing instruction in a review report, and a guard that lives in a report is a guard nobody checks |

**Adding a gate: validate it in BOTH directions before trusting it.** Run it against a tree where the
defect is present and confirm it fails, then against the fixed tree and confirm it passes. Four of this
repository's checkers were wrong at least once by being tuned only on the case in front of them. One
specific trap, learned the hard way: a detector that compares source against a **rendered** artifact
must be tested against the render built *from that source*. Copying a fixed PDF into a broken tree
makes such a gate report OK, correctly, and look blind.

## Compliance decisions baked in

- Font: `newtxtext,newtxmath` (Times; manual §8); abnTeX2 heading fonts remapped to Times bold.
- Citations: `abntex2cite [num]` — single global numeric scheme (decision #5, Viegas-style).
- Margins: 3 cm top/left, 2 cm bottom/right (`\setlrmarginsandblock`/`\setulmarginsandblock` +
  `\checkandfixthelayout[fixed]` under `\OnehalfSpacing`, verified vs manual §7).
- Spacing: `\OnehalfSpacing` (manual §7). Page numbers: top-right arabic. A4.
- Title: set to the working option; alternates in the `0_main.tex` comment (pending advisor).
- Final build: pre-body pages empty pagestyle; body counter `\finalbuildfirstpage` in `main.tex`
  ([VERIFY] tune against the AcademicoPG RASCUNHO PDF post-upload).
- Chapter prefaces: `\begin{chapterpreface}...\end{chapterpreface}` (the italic time-capsule).
