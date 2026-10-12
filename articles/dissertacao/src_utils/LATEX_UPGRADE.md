# LATEX_UPGRADE.md — source/build engineering recommendations (persona 19)

> **Scope.** The three-entry-point build machinery of `src/` (`main.tex`, `0_main.tex`,
> `main_ppgc.tex`, `Makefile`) and its documentation. Research + recommendation only: no `.tex`,
> `.sty`, `.bst` or `.bib` file was modified. **Date:** 2026-07-28. **Method:** full read of
> `reviewers/19_latex_source_reviewer.md`, `CLAUDE.md`, `TEMPLATE.md`, `UFV_COMPLIANCE.md` §1–§2,
> `src_utils/README_SRC.md`, the four source files above and `src/0_main.tex` in full; inspection
> of the five example dissertations under `exemples/`; web research on LaTeX project-structure and
> conditional-build practice (TeX FAQ, jobname/`\def` command-line patterns, latexmk, abnTeX2
> ecosystem templates). All `file:line` references are against the 2026-07-28 tree.
>
> **Example-source availability, stated plainly:** only `exemples/germano/` contains LaTeX source
> (the UFVMastersTemplate2021 tree this skeleton was derived from). `canesche`, `lapsusvgi`,
> `passe` and `viegas` are PDF-only — nothing to inspect on the source side. Germano's tree is a
> flat single-preamble `0_main.tex` compiled directly, five root-level `\include`s, **no** dual-build
> switch, and the donor cruft the current preamble already stripped (`lipsum`, `xcolor` with
> `xcdraw`, `multirow`/`lscape` loaded twice, `[alf]` citations, `lmodern`). The current `src/`
> tree is already engineered *past* its donor; nothing in the examples argues for reverting any
> decision here.

---

## 1 · Verdicts on the five candidates

### Candidate 1 — move both `\newif`+`\ifdefined` blocks from `main.tex` into `0_main.tex`

**Partially valid — correct mechanics, but pointless as a standalone change; do it only as the
first half of candidate 2.**

The mechanics are right: a macro `\def`'d on the command line (`make final`) or in
`main_ppgc.tex` before `\input{main.tex}` is a global assignment and survives any number of
nested `\input`s, so the `\ifdefined\FINALBUILD` / `\ifdefined\APPROVALSHEET` tests
(`main.tex:43,49`) work identically from the top of `0_main.tex`. Locality of behavior is also
genuinely served: both switches are consumed only in `0_main.tex` (`0_main.tex:204`, `:215`,
`:436–440`).

Two qualifications:

1. **`\finalbuildfirstpage` must travel with them.** It is defined at `main.tex:72` and consumed
   at `0_main.tex:439`. Moving the switches but leaving the counter would leave `main.tex` as a
   one-constant-plus-`\input` file — a worse split than today's. The switches, the counter, and
   the C-1 measurement comment above it (`main.tex:54–71`) are one unit.
2. Done alone, candidate 1 reduces `main.tex` to a header comment plus one `\input` — pure
   indirection with no remaining job. That state should not be committed; it is only a waypoint.

### Candidate 2 — merge `0_main.tex` back into `main.tex` (one file)

**Valid in principle — the two-file split no longer earns its keep — but qualified on timing:
this is a post-defense refactor, or a single atomic commit with a full reference sweep. Not a
casual edit three weeks before the banca handoff.**

Why the merge is right in principle:

- The split's original reason (a shared body read by two independent full entry files) died on
  2026-07-28 when `main_ppgc.tex` became a two-content-line shim that reads `main.tex` — which
  then reads `0_main.tex`. That is a three-file chain where one file does nothing but forward.
  `main_ppgc.tex \input main.tex \input 0_main.tex` collapses cleanly to
  `main_ppgc.tex \input main.tex`.
- The general-LaTeX canon has no preference for a separate "body" file behind the entry point;
  what it does prescribe — `\include` per chapter, `\input` for fragments, one preamble, magic
  `% !TeX root` comments — is already honored and is unaffected by the merge. The abnTeX2
  ecosystem templates surveyed (UFPA/IFCE/UFSCar PPGCC models, ufscthesisx, the Germano donor
  itself) all compile the preamble file directly; none uses a dispatcher-plus-body split. No UFV
  or abnTeX2 norm speaks to source layout at all — UFV governs the delivered PDF, not the LaTeX
  (`README_SRC.md:83-84` already records this).
- The chapters' `% !TeX root = ../main.tex` directives already point at `main.tex`, not
  `0_main.tex` — the merge makes the declared root and the real preamble location coincide.

Why the timing qualification is not hand-wringing:

- **55 live references to `0_main`** exist in active (non-archive, non-review-report) docs and
  tooling — including `src_utils/check.sh:16` (greps `0_main.tex` by name), `CLAUDE.md`,
  `README_SRC.md`, `TEMPLATE.md`, `NORTH_STAR.md`, `science/AGENT_HANDOFF.md`, and four checker
  scripts. A merge that misses one leaves a gate silently linting a file that no longer exists —
  exactly the "checker certified a tree it wasn't reading" failure class round 6 just closed
  (`CLAUDE.md` §1). The gate suite's own history says: validate every touched checker in both
  directions after the rename.
- The build is currently verified green on all three targets (`CLAUDE.md` §1, measured
  2026-07-28). The merge buys maintainability, not correctness; the defense is ≈ Aug 21.

**Recommendation:** do candidates 1+2 as one commit, after the advisor/banca handoff pressure
passes — move switches + counter to the top, inline the body, delete `0_main.tex`, sweep all 55
references, re-run `make defense && make final && make ppgc` + `make check` + the checker
self-tests. Until then, the current three-file chain is documented and correct; it is ugly, not
wrong.

### Candidate 3 — eliminate `main_ppgc.tex`; inject `\APPROVALSHEET` from the Makefile

**Not recommended.** Three grounds, in descending weight:

1. **It breaks the Overleaf contract for the ppgc build.** `README_SRC.md:9-11` is explicit:
   `src/` must paste into Overleaf and compile standalone. Overleaf (and TeXShop/TeXstudio) can
   select `main_ppgc.tex` as the compile root and produce the defense+approval-sheet PDF with
   zero configuration; a command-line `\def` injection cannot be expressed there without a
   `latexmkrc` hack that would itself be a new non-obvious file. The `final` build already pays
   this price (it is Makefile-only today); extending that limitation to a second build to save a
   two-line file is a net loss. The author has the file open in an IDE — the direct-use case is
   real, not hypothetical.
2. **The drift risk the injection would guard against is already zero.** `main_ppgc.tex` contains
   exactly two content lines (`main_ppgc.tex:18-19`) and its header forbids adding content
   (`:13-15`, echoed at `README_SRC.md:72-74`). There is nothing left to drift.
3. It reverses a dated author decision (2026-07-28, quoted in `main_ppgc.tex:5-6`) for no
   compliance or correctness gain.

The *symmetric* move — see finding F-4 below — is the better direction: add a two-line
`main_final.tex` so all three builds are producible in a GUI/Overleaf, rather than delete the
one shim that already is.

### Candidate 4 — DRY the three Makefile recipes into a parametrized pattern

**Partially valid — legitimate, but low leverage; if the Makefile is touched, fix findings F-2
and F-3 in the same pass, which are worth more than the DRY itself.**

The three recipes (`Makefile:15-22`, `26-32`, `37-43`) are genuinely the same 3-pass shape
parametrized by (jobname, entry-expression), and a canned recipe removes the class of defect
where a pass count or flag is edited in one target and not the others:

```make
# sketch only — not applied
define TEXRUN
	@mkdir -p build build/chapters
	pdflatex $(TEXOPTS) -jobname=$(1) $(2)
	$(BIBINPUT) bibtex build/$(1) || true
	pdflatex $(TEXOPTS) -jobname=$(1) $(2)
	pdflatex $(TEXOPTS) -jobname=$(1) $(2)
endef
defense: ; $(call TEXRUN,main,main.tex) && cp build/main.pdf dissertacao.pdf
final:   ; $(call TEXRUN,main_final,"\def\FINALBUILD{}\input{main.tex}")
ppgc:    ; $(call TEXRUN,main_ppgc,main_ppgc.tex)
```

Qualifications: the whole Makefile is 51 lines and each recipe is six; `define`/`call` is
markedly less readable to a casual maintainer than three explicit blocks, and this Makefile has
exactly one maintainer. Cost ≈ benefit. Priority low on its own. The alternative modernization —
`latexmk` — is deliberately **not** recommended now: the three-pass fixed recipe is what
`build.sh` and the round-6 verification history are calibrated against, all three builds are
measured clean under it, and swapping the toolchain weeks before the defense re-opens a verified
surface for zero output difference. Revisit post-defense if at all.

### Candidate 5 — one canonical "three builds, one source" explanation; the others point to it

**Valid, with one load-bearing correction to the proposal: the canonical copy must be the
`main.tex` header, not `src_utils/README_SRC.md`.** `README_SRC.md` lives *outside* `src/` and
does not travel with the Overleaf paste (`README_SRC.md:9-11, 36`); if it became the sole full
explanation, the pasted tree would carry only pointers to a file the Overleaf reader does not
have. The entry file's header is the one copy guaranteed to be in front of whoever opens the
source. So: `main.tex` header = canonical (what the switches are, what each build is);
`README_SRC.md` keeps the *operational* detail that genuinely belongs outside the paste (TeX
tree, `texenv.sh`, gate suite, verification protocol) plus a pointer; `Makefile` header and
`CLAUDE.md` §1 shrink to two lines plus a pointer each.

That this duplication is already drifting is measurable today — see F-1 (a documented build
command that produces the wrong PDF) and the "four lines"/"two lines" contradiction:
`main.tex:12` and `main_ppgc.tex:9` say `main_ppgc.tex` is a "four-line file";
`README_SRC.md:17,72` and `CLAUDE.md` §1 say "TWO lines". The file has exactly two content lines.
Four copies of one story, two of them wrong on a checkable fact, is the argument for this
candidate written by the tree itself.

---

## 2 · Additional findings

### F-1 (HIGH) — `main.tex:28-32` documents a `make final` command that silently produces the DEFENSE build

The header comment says the final build is produced by
`pdflatex "\newif\ifdefensebuild\defensebuildfalse\input{main.tex}"` and that "`make final` does
exactly this" (`main.tex:30-32`). Neither is true: `Makefile:28` injects `\def\FINALBUILD{}`.
Worse than stale — the documented command is *actively wrong*: after the command-line
`\newif\ifdefensebuild\defensebuildfalse`, `main.tex:42` re-executes `\newif\ifdefensebuild`
(resetting the switch) and `main.tex:43` finds `\FINALBUILD` undefined, so the run sets
`\defensebuildtrue` and emits the full-front-matter defense document under a `main` jobname the
operator believes is the deposit body. This is persona 19's charter defect class verbatim ("a
two-build switch that silently produces the wrong PDF") living in a comment that invites the
operator to trigger it. Related: `main.tex:40-41` attributes the nested-`\if` scanning problem to
`\ifdefined` — inverted; the scanning hazard belongs to the raw `\newif`-on-command-line pattern
that `\ifdefined` was adopted to *avoid* (cf. the correct statement at `main.tex:15-16` and
`README_SRC.md:63-64`). **Direction:** rewrite `main.tex:28-32` to quote the actual `Makefile:28`
command, and fix the `:40-41` attribution. One comment block; zero output change; removes a
wrong-PDF trap.

### F-2 (MEDIUM) — `Makefile` `bibtex … || true` masks fatal BibTeX errors

`Makefile:18,29,40`: `bibtex` exits 1 on warnings, 2 on errors, 3 on fatal errors; `|| true`
flattens all of them. The `|| true` exists to survive warning-level exits, but it also lets a
build with a fatal `.bib` failure sail through `-halt-on-error` pdflatex passes on a stale or
empty `.bbl` — the exact ".blg never reaches the .log" blind spot the persona's procedure step 4
names, currently caught only downstream by `build.sh`/`check.sh`. **Direction:** tolerate exit 1
only, e.g. `$(BIBINPUT) bibtex build/main; test $$? -le 1`. Three lines (or one, after
candidate 4).

### F-3 (MEDIUM) — the Makefile does not preflight the TeX environment it documents as mandatory

`README_SRC.md:98-105` documents two failure modes of running `make` without
`source src_utils/texenv.sh`, the second of which ("Font ntx-Regular-tlf-ot1r not found") is
explicitly called misleading and cost real diagnosis time (`CLAUDE.md` §1 repeats the warning).
The Makefile itself performs no check. **Direction:** a two-line guard target, e.g.
`@test -n "$$TEXMFHOME" || { echo "TEXMFHOME unset - run: source ../src_utils/texenv.sh"; exit 1; }`,
prerequisite of the three build targets. Converts a documented foot-gun into an immediate,
self-explaining failure.

### F-4 (LOW) — optional: a two-line `main_final.tex` for build-tool parity

The inverse of candidate 3: today the deposit build — the one PDF actually uploaded to
AcademicoPG — is the only build that *cannot* be produced from a GUI editor or Overleaf, because
it exists solely as a Makefile command-line injection (`Makefile:28`). A `main_final.tex`
containing `\def\FINALBUILD{}` + `\input{main.tex}` (the exact `main_ppgc.tex` pattern,
`main_ppgc.tex:18-19`, with the same "do not add content" header) would make all three builds
selectable as a compile root anywhere, at the same zero drift risk. Costs one more entry file and
touches the "THREE targets, TWO entry files" story in four documents — hence LOW, and best bundled
with candidate 5's documentation consolidation if adopted. `make final` would then compile
`main_final.tex` and lose the injection entirely.

### F-5 (LOW) — `main_ppgc.tex` line-count self-description

`main.tex:12` and `main_ppgc.tex:9` say "four-line file"; the file has two content lines
(`main_ppgc.tex:18-19`) and every other document says two. Trivial, but it is a checkable fact
stated wrongly inside the file itself; fix in the same pass as candidate 5 / F-1.

---

## 3 · Do not touch (already well engineered — protect from future refactors)

- **The `\ifdefined\MACRO` guard pattern itself** (`main.tex:42-49`). It is the correct,
  FAQ-endorsed way to receive a command-line/pre-file `\def`; do not "simplify" it back to raw
  `\newif` manipulation on the command line (that is the F-1 trap).
- **`main_ppgc.tex` as a no-content shim** and its header contract ("Do not add content here",
  `main_ppgc.tex:13-15`). The anti-drift design is sound; the only valid edits are comment fixes.
- **The measured-defect comment blocks**: the C-1 `\finalbuildfirstpage` derivation
  (`main.tex:54-71`) and the E-5 `hyperfootnotes` load-time note with its
  `\PassOptionsToPackage` placement (`0_main.tex:21-26, 174-191`). Each records a real shipped
  defect, its measurement, and why the fix lives where it lives. If candidate 2 merges the files,
  these blocks move intact.
- **The preamble hygiene already done** (`0_main.tex:1-66`): donor cruft stripped with a
  kept/stripped/changed ledger in the header; `amssymb`/`amsfonts` dropped with the `\Bbbk`-clash
  reason recorded; single `multirow`; no `lipsum`/`xcdraw`; `newtxtext,newtxmath` per manual §8;
  the `\citebrackets`/`\@biblabel` hooks each carrying their abntex2cite.sty line citations. This
  is the standard the persona audits *for* — do not let a template "refresh" reintroduce the
  Germano donor's duplicates.
- **`% !TeX root` directives in every chapter file** + `check_tex_root.py` (two real incidents in
  one week per `README_SRC.md:143`).
- **The build/verification discipline**: `-halt-on-error` in `TEXOPTS` (`Makefile:9`),
  `-output-directory=build` with the pre-created `build/chapters/` for `\include` aux files,
  `build.sh`'s `tex_errors` count, and the both-directions checker-validation rule
  (`README_SRC.md:146-151`). These exist because their absence shipped wrong artifacts.
- **`\include` per chapter + per-section `\input` under `chapters/3_cbic/`, `4_courb/`,
  `5_mobiwac/`** — canonical large-document structure (aux-file page/number preservation per
  chapter, fragment inputs below), and four checkers are already calibrated to the two-level glob.

---

## 4 · Author-decided additions (2026-07-28, post-review)

Not part of the original 5 candidates or persona 19's findings — decided directly by the author
after reading this file's F-4 (§2) and the Overleaf-contract argument in Candidate 3 (§1). Recorded
here as an approved-but-not-yet-applied item; implement together as one change.

### A-1 — rename the `final` build to `academico` throughout (target, jobname, output file)

`make final` → `make academico`; `build/main_final.pdf` → `build/main_academico.pdf`. Rationale
(author): "final" is ambiguous next to `defense`/`ppgc` (final of what?); "academico" names what
the build actually is — the AcademicoPG deposit body. Touches: `Makefile` (target name, `-jobname`,
comments), `main.tex` header comment (the "THREE builds" table), and the live docs that name the
`final` target (`CLAUDE.md`, `PLAN.md`, `science/AGENT_HANDOFF.md`, `reviewers/19_latex_source_reviewer.md`,
`src_utils/README_SRC.md`) — NOT the frozen historical/audit reports (`_history/_round6/`, `_history/_review_v1/2/3`,
`_history/_archive/`, `PENDENCIAS.md`, `CODEX_AUDIT.md`, etc.), same rule as every prior rename in this doc.

### A-2 — adopt F-4: a thin `main_academico.tex` entry file, same pattern as `main_ppgc.tex`

Confirmed by the author (this file's §2 F-4 argument: the deposit build is currently the *only* one
that cannot be opened/compiled from Overleaf or a GUI editor, because it exists solely as a
Makefile command-line injection). Two content lines, mirroring `main_ppgc.tex:18-19`:
```latex
\def\ACADEMICOBUILD{}
\input{main.tex}
```
`make academico` then compiles `main_academico.tex` directly (`pdflatex $(TEXOPTS) main_academico.tex`),
same 3-pass recipe as `defense`/`ppgc`, instead of the current
`pdflatex ... -jobname=main_final "\def\FINALBUILD{}\input{main.tex}"` injection. This makes all
three builds symmetric: three thin/real entry files, each Overleaf-selectable as the compile root.

### A-3 — rename the internal switch macro `\FINALBUILD` → `\ACADEMICOBUILD`

Confirmed by the author, for full-stack consistency (target, file, PDF, and the LaTeX macro all say
"academico" — no `\FINALBUILD` left in the source once the external names change). Touches
`main.tex:38-43` (the `\newif`/`\ifdefined` guard — see Candidate 1/2 above, this migrates together
with those switches if 1+2 are ever applied) and `main_academico.tex` (A-2) once it exists.

**Bundling note:** A-1/A-2/A-3 are independent of Candidates 1–2 (moving the switches into
`0_main.tex` / merging the files) — they can be applied now, before or without that larger merge,
since they only rename things, not relocate the switch logic. If Candidates 1+2 are later applied,
do the rename first (fewer moving parts) or in the same atomic commit — not two separate reference
sweeps of overlapping files.

---

## 5 · Sources consulted

**Internal:** `reviewers/19_latex_source_reviewer.md`; `CLAUDE.md`; `TEMPLATE.md` (full);
`UFV_COMPLIANCE.md` §1–§2; `src_utils/README_SRC.md`; `src/main.tex`; `src/0_main.tex`;
`src/main_ppgc.tex`; `src/Makefile`; `src_utils/check.sh` (grep-level); chapter `% !TeX root`
headers.

**Example dissertations:** `exemples/germano/Dissertação_Mestrado___Germano/` (full source:
`0_main.tex`, `texto.tex`, README — flat single-preamble tree, direct-compile, no dual build,
donor cruft as described in §1); `exemples/canesche/`, `exemples/lapsusvgi/`, `exemples/passe/`,
`exemples/viegas/` — **PDF-only, no source to inspect**.

**Web:**
- TeX FAQ, "Conditional compilation and comments" — `\includeonly`, `\newif`, command-line
  switch patterns: https://texfaq.org/FAQ-conditional
- Leo3418, "Build the Same LaTeX Input File Differently According to Command-Line Options"
  (2024) — the `-jobname` + command-line `\def` pattern the Makefile's `final` target uses:
  https://leo3418.github.io/2024/06/21/latex-file-cmdline-build-options.html
- UKUUG, "LaTeX and Makefiles" — `-jobname` + `\def` injection in Make recipes:
  https://www.usenix.org.uk/content/latex.html
- LaTeX2e unofficial reference manual, "Jobname": https://latexref.xyz/Jobname.html
- latexmk manual (Debian manpages) — jobname handling, rerun automation:
  https://manpages.debian.org/testing/latexmk/latexmk.1.en.html
- ETH blog, "Make a thesis with latexmk and Makefile" — latexmk-inside-Make convention:
  https://blogs.ethz.ch/daesters/2020/12/30/make-a-thesis-with-latex-with-latexmk-and-makefile/
- LaTeX Cloud Studio, "Managing Large Documents" — `\input` vs `\include`, per-chapter layout:
  https://resources.latex-cloud-studio.com/learn/latex/how-to/large-documents
- abnTeX2-ecosystem PPGCC templates (structure survey — all direct-compile, chapters via
  `\include`, no dispatcher/body split, no dual-build convention found):
  https://github.com/ovitor/modelo-dissertacao-ppgcc ,
  https://github.com/omadson/modelo-dissertacao-ppgcc ,
  https://github.com/alvesmgabriel/ppgccufscar2 ,
  https://github.com/UFSC/ufscthesisx ,
  https://www.overleaf.com/latex/templates/template-para-dissertacao-e-tese-de-doutorado-do-ppgcc-ufpa-universidade-federal-do-para/kdhwnkzqbpww
- abnTeX2 UFV contribution (Smarzaro TCC model PR — confirms no official UFV LaTeX norm on
  source layout): https://github.com/abntex/abntex2-contrib/pull/3/files

No UFV/PPGCC or abnTeX2 source found imposes any normative expectation on single- vs multi-file
LaTeX source or on how dual defense/deposit builds are produced; the norms govern the delivered
PDFs (`UFV_COMPLIANCE.md` §1). All structural recommendations above are therefore engineering
judgment, not compliance requirements.
