# 20 — Build speed: a precompiled preamble, parallel targets, and an honest gate suite

**Track:** round 7, build speed. **Working dir for every command below:** `articles/dissertacao`,
with `source src_utils/texenv.sh` first, always.
**Machine:** darwin, 12 cores, 32 GiB. **TeX:** pdfTeX 3.141592653-2.6-1.40.29 (TeX Live 2026).
**Source measured at:** repo commit `0bfc9e5e` (HEAD moved from `adbb6952` to `0bfc9e5e` during
this round — other tracks were committing in parallel).

> **Read this first, because it governs how much of the report below is load-bearing.** Every
> timing here was measured in an **isolated snapshot** of `src/`, not in the repository tree.
> That was not tidiness. My first baseline run **failed**, and the failure is the reason step 2
> of this track exists — see §0.

---

## 0 · The measurement that failed first, and what it proved

The first baseline attempt ran `make defense && make final && make ppgc` in `src/` and died:

```
Runaway argument?
{\contentsline {subsection}{\numberline {4.3.1}Baseline: MTLnet with \ETC.
! File ended while scanning use of \@writefile.
l.60 \@input{chapters/4_courb.aux}
!  ==> Fatal error occurred, no output PDF file produced!
```

That reads exactly like a LaTeX defect in chapter 4. It is not one. Another session was building
the same tree at the same time, and the two builds share **one** `build/chapters/`; a concurrent
pass truncated `4_courb.aux` while my pass was reading it.

**The evidence, and its one limit.** Two observations support the diagnosis, both read from the
probe's own output: `build/chapters/4_courb.aux` and `build/main*.log` carried mtimes that
*advanced between successive probes* while no build of mine was running (`00:20:12` → `00:21:56`
→ `00:22:03`), and `uptime` reported a 1-minute load average of 10.23 on an otherwise idle
session. What did **not** corroborate it: the `ps` probe I ran at the same moment matched **zero**
`pdflatex`/`bibtex`/`make` processes. That is consistent with sampling between two of the other
session's passes rather than during one, but it is a negative result and it is recorded here as
such. The diagnosis rests on the advancing mtimes and the load average, not on `ps`.

```bash
# the probe, and what it actually returned (working dir: articles/dissertacao)
ps -Ao pid,etime,command | grep -i 'pdflatex\|bibtex\|make ' | grep -v grep   # -> no rows
uptime                                                                        # -> load 10.23
ls -lT src/build/chapters/4_courb.aux                                         # -> mtime advancing
```

Three consequences, all of which shaped this track:

1. **The collision in step 2 of the brief is real and it is not only about `make -j`.** Any two
   builds of this tree collide, including two people, or one person and one agent.
2. **It presents as a source error, in a file that is fine.** Under the errata regime, a
   phantom error in a *published* chapter is an expensive false alarm.
3. **Every number below was therefore measured in a private snapshot** (`rsync -a --exclude
   build/`), so no timing here is contaminated by another session's load, and nothing I ran
   disturbed anyone else's build. The snapshot's own `make` output was verified to reproduce the
   inherited 108/105/109 page counts with `tex_errors=0` before any timing was believed.

---

## 1 · What was built

The brief asked for four things. They landed as seven files, because the equivalence proof and
the standalone gate runner each needed a file of their own:

| # | File | What it is |
|---|---|---|
| 1 | `src_utils/mkformat.py` | derives the preamble/body split, builds the format dump, owns the staleness key |
| 2 | `src_utils/fastbuild.sh` | one target, three passes, loading the dump; refuses on a stale key |
| 3 | `src_utils/verify_format.py` | the equivalence proof: text layer, digits, media boxes, bookmarks |
| 4 | `src_utils/check_scripts.sh` | every standalone gate, one line each, with its own timing |
| 5 | `src/Makefile` | per-target aux trees, `all3`/`fast3`, and a named target per checker |
| 6 | `src_utils/check.sh` | per-gate timing table |
| 7 | `src_utils/check_verify_list.py` | the one gate above 0.3 s, parallelized |

### 1.1 · The format dump, and the two hazards the brief named

**The split is mechanical.** `mkformat.py` locates `\begin{document}` in `0_main.tex` and cuts
there; the two halves are complementary byte ranges of one file, so the body driver cannot
contain a preamble-only command and the preamble half cannot contain a second
`\begin{document}`. Measured on the emitted files: `grep -c 'documentclass\|usepackage\|
PassOptionsToPackage'` over `_body.tex` returns **0**, and the accelerated pass logs
`grep -c '^! '` = **0** — which is the check the brief asked for, rather than "a PDF appeared".

**A defect the split found in its own first version, worth recording because it was dangerous
rather than merely wrong.** `main.tex`'s header quotes the switch pattern inside a comment:

```
%       pdflatex "\newif\ifdefensebuild\defensebuildfalse\input{main.tex}"
```

A comment-blind `str.find()` for the `\newif` anchor lands **there**, 34 lines above the real
declaration, and slicing from the match offset drops the leading `%` — so that quoted command
becomes **live code inside the format**, recursively `\input`ting `main.tex`. The tell was the
size of the extracted region, and the honest version of that figure is worth stating because my
first write-up of it was wrong twice. **Measured on this tree:** the fixed extractor returns
**2,293 bytes**, of which **229 bytes in 5 lines** are live code and the rest is interleaved
provenance commentary sitting *between* the two `\newif` blocks, which must be carried along. A
comment-blind `find()` from first match to last spans **6,714 bytes** and *starts inside the
quoted command*. So the diagnostic is not a ratio, it is that the blind version begins in the
wrong place; I originally reported "2,809 bytes for a region that is 130", and neither number
survives re-measurement. `0_main.tex`
carries the same trap for `\begin{document}` ("would be too late"). Both anchors now go through
`find_live()`, which skips matches preceded by an unescaped `%` on the same line. This is
`AGENT_GUARDRAILS` §4b V4 arriving in a place nobody had thought to apply it — not a grep over
prose, but a *code generator* reading this source.

**The staleness guard has seven members**, and it is keyed on what the dump actually consumed
rather than on a guess: `main.tex`'s switch region, `0_main.tex`'s preamble region, the byte
offset of the split, `abntex2-UFV.sty`, `mkformat.py` itself, pdflatex's version banner, and the
size+mtime of **every file the dump loaded**, read back out of `mainpre.log`. That last member is
what closes it: the first six cover this repository, the seventh covers the class, package and
font-map files in the TeX trees.

`0_main.tex`'s **body** region is deliberately *not* in the key, and neither are `chapters/`,
`tables/`, `figures/` or `references.bib`. Those are read at run time on every pass, so a prose
edit must not trigger a 34-second re-dump — that would defeat the accelerator on exactly the edit
the author makes most. The self-test pins both directions of that: the key must **hold** on a
body-only edit and **move** on a preamble edit.

**Validated in both directions, measured** (experiment E, `bl/exp6.sh`):

```
format: fresh                                                    -> rc=0
(a \usepackage added to 0_main.tex's preamble)
format: stale: 0_main.tex:preamble, 0_main.tex:begindoc_offset    -> rc=1
fastbuild: REFUSING to build -- format: stale: ...                -> exit 3, no build
(0_main.tex restored)
format: fresh                                                    -> rc=0
```

The refusal matters more than a warning would. A stale format is silently wrong: the build
succeeds and the PDF is stale, which is `AGENT_HANDOFF` §2.3b with the tools swapped. So
`fastbuild.sh` exits rather than proceeding, and `make fast` runs `mkformat.py --build` first,
which re-dumps when the key moved and does nothing when it did not.

### 1.2 · The equivalence proof, and the tautology it caught in itself

Comparison surface: the **whole document's** extracted text with **digits masked**, plus three
secondary surfaces (digit sequence, per-page media boxes, bookmark tree). Whole-document, not
page-by-page, because a page-by-page diff drowns in false positives the moment one line reflows.

**The comparator's first run reported a perfect match for a build that never happened.** All
three targets came back `text IDENTICAL / digit sequence IDENTICAL / all media boxes equal /
bookmark tree IDENTICAL` — while `fastbuild.sh` had **refused** (correctly: I had pointed it at
the wrong tree, so its key was stale). The candidate PDFs were still the serial ones, and the
comparator had matched each reference against an unchanged copy of itself. A green result
carrying no information at all: `AGENT_GUARDRAILS` §7's "gate that has never fired", reached from
§2.2's direction, where identical outputs looked exactly like a converged result.

The fix is `same_file()`, and its reasoning is the useful part: **two pdflatex runs of the same
source never produce identical bytes** — `/CreationDate`, `/ModDate` and the `/ID` trailer change
every run. So byte-identity does not mean "equivalent", it means "this is the same file", and it
is now reported as a **failure of the comparison**, not as its strongest possible pass. Validated
both ways (4 of the comparator's 9 self-test checks): it rejects a path compared with itself and a
byte-identical copy, accepts two genuinely different files, and `compare()` refuses the pair.

Re-running the same comparison that had passed:

```
defense: NOT AN INDEPENDENT BUILD -- byte-identical, which two pdflatex runs never are
      A comparison of a file with itself proves nothing. Build the candidate, then compare.
verify_format: 3 of 3 targets compared, 0 skipped   -> rc=1
```

**One more instrument defect, found by using it.** `difflib.SequenceMatcher(autojunk=False)` over
two 275,000-character fingerprints ran about **eleven minutes** on the first real mismatch — long
enough that the run looked hung rather than informative. Replaced with a common-prefix scan, which
finds the same first divergence in milliseconds.

**And a third, which is the same tautology wearing different clothes.** The bookmark-tree check
caught an exception and returned `["UNREADABLE:<ExceptionName>"]` as the outline. Two *unreadable*
outlines then compared **equal**, and the comparator printed `bookmark tree IDENTICAL (1 entries)`
— a pass that means "I could not read either file". Two empty outlines had the same problem. Both
now report `UNVERIFIED` and **fail** the comparison, with the exception name for each side. Four
more self-test checks pin it (13 total now), and the real PDFs still report `IDENTICAL` at
110/107/110 entries, so the fix did not simply break the check into always-failing.

Worth naming the pattern, since it appeared three times in one comparator: **every "equal" branch
needs to answer "equal to what, and did I actually look?"** A sentinel compared with itself, a file
compared with its own copy, and an empty result compared with another empty result all satisfy
`a == b` while establishing nothing.

---

## 2 · What changed, by phrase

Anchored by phrase, never by line number.

**`src/Makefile`** — rewritten around per-target aux trees.
- Every recipe's `-output-directory=build` became `-output-directory=build/<stem>-aux`, with
  `@cp build/<stem>-aux/<stem>.pdf ... .log ... .blg build/` afterwards. **Only those three files
  are copied back.** The `.aux`/`.toc`/`.lof`/`.lot` deliberately are not: a copy of an aux file
  in a directory BibTeX also searches is how four `(??)` citations shipped in both PDFs
  (`AGENT_HANDOFF` §2.4).
- Every documented path therefore stays true — `build/main.pdf`, `build/main.log`,
  `build/main.blg` are what `check.sh`, `sync_page_counts.py`, `build.sh`, `CLAUDE.md` and
  `README_SRC.md` all name. Verified: `sync_page_counts.py` reads `src/build/<stem>.log` and
  passes.
- `bibtex ... || true` became `bibtex ...; test $$? -le 1`, closing `LATEX_UPGRADE.md` F-2:
  `|| true` flattened exit 2 and 3 (real BibTeX errors) into success.
- New: `all3` (`$(MAKE) -j3` inside the recipe, so a caller who forgets `-j3` does not silently
  get the serial time), `fast`/`fast3`/`format`/`format-status`/`verify-equiv`, twelve
  `check-*` targets, `check-scripts`, `sync-pages`, `help`.

**`src_utils/check.sh`** — each `echo "== ... =="` gate header became `gate "== ... =="` (18 of
them at the time; the count is **computed at run time, not hardcoded**, so a gate added by another
track is picked up automatically — the suite reported 19 within the hour), and `gate_report` runs
before `exit $FAIL`. The clock is `perl -MTime::HiRes`, not `$EPOCHREALTIME`: this machine's
`/bin/bash` is 3.2.57 and that variable arrived in bash 5.

**The harness discloses its own cost, and my first disclosure of it understated the truth by
about 3x.** I measured a bare clock read — 20 calls in 0.151 s, ~6 ms — and wrote that into the
footer as the per-boundary cost. But a `gate` call spawns **three** perl processes, not one: the
`$(_now)` inside the arithmetic, the arithmetic itself, and the `$(_now)` that opens the next
gate. Measured as the boundary is actually spelled: **20 full boundaries in 0.348 s, ~17 ms
each**, so the 20 boundaries cost ~0.34 s of the suite's runtime rather than the ~0.14 s I first
claimed. The footer now computes from a named `SECS_PER_BOUNDARY=0.017` and says where the three
spawns go. A timing harness that is wrong about its own cost is worse than none, and the way to
get this right is to time *the thing as written*, not its cheapest component.

The footer also no longer states the per-gate thresholds as if they were properties of the
current run. It attributes them to the recorded round-7 measurement and points the reader at the
column above for today's numbers — the previous wording ("Round 7 measured every gate below
0.3 s") would go stale silently the moment a gate slowed down.

**`src_utils/check_verify_list.py`** — the block loop split into `classify()` (one classifier,
called twice, so the plan and the report cannot disagree about a block's kind) and a
`ThreadPoolExecutor` pass. Results are printed in **document order, not completion order**, so the
output stays byte-comparable with its serial form. Also fixed: the inner `for kind, want in exps`
shadowed the outer block-kind variable; it is `etype` now.

**Nothing under `src/chapters/`, `src/tables/` or `src/figures/` was touched.** No prose changed.

---

## 3 · Timing table

All times wall clock, `TIMEFORMAT='%3R'`, measured in the isolated snapshot at source state
`0bfc9e5e`+working-tree, each arm from a **cold** aux tree (aux trees, per-target PDFs and logs
all removed before the arm starts).

**Read the caveat before the numbers.** Other sessions in this round were building and committing
throughout, so absolute wall times here carry machine-contention noise. Two measured spreads, both
same-command-same-tree: `make defense` came in at **105, 111, 122.7 and 128 s** across four runs,
and `make fast3` at **20.7 s and 61.1 s** across two. Ratios *within* one arm-set are the
trustworthy part; the absolute seconds are an envelope, not a constant, and the 3x spread on
`fast3` is the reason this paragraph is above the table rather than in a footnote. Every figure
below is one measured run, and the run that produced it is named.

### 3.1 · Per-target build cost

| arm | command | defense | academico | ppgc | three-target total |
|---|---|--:|--:|--:|--:|
| **A** serial, plain (baseline) | `make defense` / `academico` / `ppgc` | 122.7 s | 120.1 s | 136.1 s | **379 s** |
| **C** serial, format-accelerated | `fastbuild.sh <target>` | 15.4 s | 14.4 s | 15.5 s | **45 s** |

Arm A: `bl/exp7.log` §A, `make_errors=0` on all three, pages 108/105/109, `tex_errors=0` on all
three. Arm C: `bl/exp6.sh` §C, `tex_errors=0` on all three, same page counts.

**The format dump costs 33.7 s to build** (`bl/exp6.sh` §C, `mkformat.py --build --force`), once,
and only when the preamble moves. So the first accelerated build of a session that changed the
preamble is ~49 s, and every one after it is ~15 s.

**Per-target speedup, format vs plain, same tree and same aux layout: 122.7 → 15.4 s (8.0x) for
defense, 120.1 → 14.4 s (8.3x), 136.1 → 15.5 s (8.8x).** Three-target serial: **379 → 45 s
(8.4x)**, or 379 → 79 s (4.8x) if the dump has to be rebuilt in the same session.

### 3.2 · Concurrency

Same tree, same cold protocol, `bl/exp7.log`:

| arm | command | wall time | vs serial | pages | `tex_errors` |
|---|---|--:|--:|---|--:|
| A serial, plain | three `make` invocations | 379 s | — | 108/105/109 | 0/0/0 |
| **B concurrent, plain** | `make all3` (`-j3`) | **157.9 s** | **2.4x** | 108/105/109 | 0/0/0 |
| C serial, accelerated | three `fastbuild.sh` | 45 s | 8.4x | 108/105/109 | 0/0/0 |
| **D concurrent, accelerated** | `make fast3` | **20.7 s** | **18.3x** | 108/105/109 | 0/0/0 |

`make all3` reported `make_errors=0`. Concurrency is not free: three targets in parallel take
157.9 s where the slowest alone takes 136.1 s, because they contend for the same 12 cores and the
same disk. The gain is 2.4x, not 3x, and that is the honest figure.

**The combination is the useful one.** `make fast3` builds all three deliverables in 20.7 s
against 379 s for the plain serial path they replace.

> **`make fast3` initially reported `make_errors=5` while producing three correct PDFs, and the
> fault was mine, in `fastbuild.sh`.** `ERRS=$(grep -c '^! ' log || echo 0)` — `grep -c` exits **1
> when the count is zero**, so on every *clean* build the `|| echo 0` fallback fired, `ERRS` became
> the two words `"0 0"`, the `[ "$ERRS" = "0" ]` test failed, and the script exited 1 after a
> perfectly good build. `make` then printed `*** [fast3-academico] Error 1` and
> `Waiting for unfinished jobs` while all three PDFs sat at 108/105/109 pages with `tex_errors=0`
> and passed equivalence 3 of 3. **A build that succeeds while its runner reports failure is the
> mirror image of §2.3b, and worse in one respect: it trains the operator to ignore the exit
> code.** Fixed to `grep -c ... | tail -1` (the pipeline's status is `tail`'s, so grep's exit code
> is discarded while its output is kept), plus a guard that fails when the log carries no page
> count at all. Validated both directions in isolation: the old form yields `"0\n0"` and fails on a
> clean log; the new form passes on a clean log and still returns 2 on a log with two `! ` lines.

### 3.3 · Where the time actually goes

The inherited claim was that the preamble is ~87% of a pass, and the measurements above are
consistent with it: three passes plus BibTeX cost ~120 s plain and ~15 s with the preamble
precompiled, so what the format removes is close to all of it. The dump itself takes 33.7 s, which
is about the cost of one plain pass — as expected, since building it *is* one pass over the
preamble.

---

## 4 · The gate suite: measured, and mostly left alone

The brief's instruction was not to parallelize for its own sake, and the measurement supports
that. `make check`, with the new timing table, run from `articles/dissertacao`:

```bash
source src_utils/texenv.sh && bash src_utils/check.sh     # every gate, timed
```

Two runs are shown: the state I measured **before** parallelizing the one slow gate, and the state
of the suite as it stands now. The gate list grew from 18 to 19 between them (another track added
the comment-hygiene gate), which is why the totals are not a clean subtraction — and which is the
point of the table being generated rather than typed.

| gate | before (18 gates) | now (19 gates) |
|---|--:|--:|
| em-dashes | 0.020 | 0.019 |
| 'this paper' / 'this article' | 0.021 | 0.021 |
| contractions | 0.046 | 0.044 |
| WRITING_LAW §4 banned words | 0.118 | 0.117 |
| banned verdict verbs | 0.030 | 0.029 |
| 'Pareto' occurrences (informational) | 0.022 | 0.022 |
| repo codenames | 0.036 | 0.032 |
| unresolved `\ref`/`\cite` | 0.036 | 0.044 |
| sweep-guard self-tests | 0.026 | 0.026 |
| recorded page counts | 0.033 | 0.034 |
| word-count claims | 0.030 | 0.029 |
| torn sentences | 0.037 | 0.038 |
| coverage claims (GUARDRAILS 4b V1) | 0.040 | 0.042 |
| **the author-facing verification commands** | **0.927** | **0.365** |
| TeX root directives | 0.046 | 0.045 |
| negative-parallelism density | 0.057 | 0.055 |
| doubled backslash before a reference macro | 0.053 | 0.053 |
| comment hygiene (added by another track) | — | 0.084 |
| prose trapped inside a `%` comment | 0.233 | 0.230 |
| **sum of gates** | **1.811** | **1.329** |
| suite total (incl. ~0.15 s of clock probes and the table) | 2.016 | 1.533 |

**One gate was above 0.3 s, so exactly one was parallelized.** `check_verify_list.py` was 0.93 s
of the 2.0 s suite. Profiled before touching it: 19 fenced bash blocks in the author-facing docs,
of which **15 execute as commands** (2 skipped to avoid recursion, 1 is a build block probed for
path resolution only, 1 is a bare `cd` note), and those 15 subprocesses sum to **0.846 s** with
the slowest single block at **0.296 s**. That is I/O-bound subprocess waiting, so threads are the
right shape and 0.296 s is the floor.

Measured, three runs each, both versions run from `src_utils/` so `Path(__file__).parent.parent`
resolves identically:

| version | run 1 | run 2 | run 3 | blocks executed | output sha256 |
|---|--:|--:|--:|--:|---|
| serial (HEAD `0bfc9e5e`) | 0.86 s | 0.89 s | 0.84 s | 15 | `7f20b91b…` |
| threaded | 0.35 s | 0.35 s | 0.35 s | 15 | `7f20b91b…` |

**Output is byte-identical**, and identical across all three threaded runs — which is the check
that matters, because a gate whose output reorders run to run cannot be diffed.

> **A measurement error I made and caught, recorded because it is the exact shape of §2.8.** My
> first comparison ran the HEAD version from `/tmp`, where its `Path(__file__).parent.parent`
> resolves to `/`. It found no documents, executed **zero** blocks, and finished in 0.04 s — and
> 0.04 s against 0.35 s reads as "the parallel version is 9x slower". The baseline was an empty
> run. `0 documented command(s) executed` was printed in its own output, and I nearly compared
> against it anyway.

The remaining 17 gates are **not** parallelized: forking to save 30 ms costs more than it saves.
The timing table exists so the next gate that grows past a second is visible on the run that made
it slow.

`check_scripts.sh` gives the standalone gates names and runs them without a build:

```bash
(cd src && make check-scripts)      # 13 gates, 0 skipped, all OK
```

Measured 1.855 s on its first run and 1.182-1.256 s on four later ones; the first run pays the
Python interpreter's cold start for thirteen separate processes.

It does **not** stop at the first failure, so one run reports everything broken. It is not a
replacement for `make check`, which also runs the inline shell sweeps and the compiled-log gates.

---

## 5 · The equivalence proof

Run in the snapshot, reference = the serial plain build of the same tree, candidate = the
accelerated build. `--all` compares four surfaces.

**Format-accelerated vs serial plain, all three targets** (`bl/exp6.sh` §C, after the confound in
§6 was removed):

```
defense:   text IDENTICAL (digits masked, 275465 chars)  digit sequence IDENTICAL (4495 runs)
           108 pages, all media boxes equal              bookmark tree IDENTICAL (110 entries)
academico: text IDENTICAL (digits masked, 270385 chars)  digit sequence IDENTICAL (4480 runs)
           105 pages, all media boxes equal              bookmark tree IDENTICAL (107 entries)
ppgc:      text IDENTICAL (digits masked, 275594 chars)  digit sequence IDENTICAL (4495 runs)
           109 pages, all media boxes equal              bookmark tree IDENTICAL (110 entries)
verify_format: 3 of 3 targets compared, 0 skipped for want of a PDF        -> rc=0
```

**Concurrent plain vs serial plain, all three targets** (`bl/exp7.log` §B): the same three blocks,
same character counts (275465 / 270385 / 275594), same digit-run counts (4495 / 4480 / 4495), same
bookmark trees (110 / 107 / 110 entries), `3 of 3 targets compared, 0 skipped`.

**Concurrent accelerated vs serial plain** (`bl/exp7.log` §D): identical on all the same surfaces,
`3 of 3 targets compared, 0 skipped` — measured on the run whose exit status was wrong, which is
what established that the *PDFs* were fine and only the *reporting* was broken.

**The fallback, measured** (`bl/exp7.log` §F): with `build/fmt/` deleted entirely,
`make defense` builds normally in 100.6 s, `make_errors=0`, 108 pp, `tex_errors=0`, and
`mkformat.py --status` correctly reports `no format dump present` with `rc=1`. The format is an
accelerator; nothing requires it. That matters for Overleaf, which cannot load a local dump.

### 5.1 · The decisive test, run after a stale cell reported the opposite

A background cell that had been running across two source re-syncs landed reporting **`text
DIFFERS` on all three targets**, with the divergence being a citation rendering `[##]` where the
reference had `[#]` — a renumbered bibliography. That contradicts everything above, and two causes
demanded opposite conclusions: either the format dump renumbers citations, in which case the
accelerator must be **retracted**, or the two arms were not built from the same source.

Circumstantial evidence favoured the second (that cell overlapped another of my own on the same
tree, each re-`rsync`ed `src/` from a repository other tracks were committing to, and three commits
touched `src/chapters/` and `src/tables/` between its reference and its candidate), but *almost
certainly* is not a measurement. So `bl/exp8.sh` was built to discriminate: **one snapshot, taken
once, never re-synced, both arms from those exact bytes, on a machine confirmed to have zero
`pdflatex` processes running**, with the source hashed before and after so a mid-test change would
void the result rather than corrupt it.

```
ARM 1  serial plain, cold:  defense 166.3 s | academico 151.3 s | ppgc 180.1 s
                            108 / 105 / 109 pp, tex_errors=0, make errors=0
ARM 2  make fast3, cold, SAME source:  55.0 s, make errors=0
                            108 / 105 / 109 pp, tex_errors=0 on all three

.bbl COMPARISON (the file that fixes citation numbering):
  main            .bbl EQUAL  7b057adac6eb1fc5
  main_academico  .bbl EQUAL  7b057adac6eb1fc5
  main_ppgc       .bbl EQUAL  7b057adac6eb1fc5

VERDICT: text IDENTICAL on all three (275465 / 270385 / 275594 chars), digit sequences
IDENTICAL (4495 / 4480 / 4495 runs), all media boxes equal, bookmark trees IDENTICAL
(110 / 107 / 110). 3 of 3 compared, 0 skipped, rc=0.
```

**The renumbering is not caused by the format dump.** The `.bbl` files are byte-equal, and the
`.bbl` is what fixes the numbering, so the two arms could not have numbered differently. The
earlier `DIFFERS` came from comparing PDFs built from two different source states.

> **My own void-guard fired, and the guard was the defect.** `exp8.sh` ended with
> `SOURCE CHANGED MID-TEST -- THE TEST IS VOID`. It was wrong: the hash globbed `*.tex` across the
> whole tree including `build/fmt/`, which is where `mkformat.py` **generates** `_pre.tex`,
> `_body.tex` and the three `_run_*.tex` drivers during arm 2 — five files that cannot exist during
> arm 1. Confirmed by arithmetic rather than by argument: the hash is over **58** files, **53** of
> them outside `build/`, and the source-only hash of those 53 is `9dcc7bfb…` — byte-identical to
> the "before" value the script printed *and* to the live repository's `src/` right now. So the 53
> real source files never moved, and the delta is exactly the 5 generated ones.
>
> Recorded rather than quietly corrected, because this is the *fourth* variant of one pattern in
> this track: a check whose scope did not match the question it was asked. It is also the least
> bad kind — it failed **closed**, refusing to certify a result it could not vouch for. A guard
> that cries wolf costs a diagnosis; a guard that stays silent costs a shipped defect.

**A separate, tighter check on the one target where a difference had appeared** (`bl/exp4.sh`):
built defense both ways from a fully cold tree with the *same* Makefile, and compared the `.bbl`
BibTeX produced in each — the `.bbl` is what fixes citation numbering, so if it agrees the
numbering cannot differ. `sha256` of both: `7b057adac6eb1fc5…`, **equal**; 100 `\bibitem` entries
in each; 400 `bibcite` in each aux; first three keys identical in both; and the two PDFs
text-identical on all four surfaces.

The instrument's blind spots are stated in `verify_format.py`'s docstring rather than left implicit:
digit masking would hide a wrong *number* (which is why `--numbers` compares digit sequences
separately), and the text layer does not carry figure raster content, rule positions, fonts,
colours or kerning (which is why media boxes and the bookmark tree are compared too). A build that
changed only a figure's pixels would pass. I judge that acceptable for a change that touches
neither figures nor graphics packages, and it is recorded so the next reader can disagree.

---

## 6 · What went wrong on the way, and what each attempt actually proved

Five of my own measurement attempts were invalid. Each is listed because the *mechanism* is the
reusable part, and because three of them are §2.8 shapes committed by an agent who had just read
§2.8.

| # | The attempt | Why it was invalid | What it cost |
|---|---|---|---|
| 1 | baseline in `src/` | another session's build truncated `4_courb.aux` mid-read | nothing — it **found** the defect step 2 exists to fix |
| 2 | `bl/exp2.sh` | pointed `fastbuild.sh` at the repo, not the snapshot; the guard refused; the comparator then matched the reference against itself and reported a perfect match | the tautology, which produced `same_file()` |
| 3 | `bl/exp3.sh` | serial arm used the OLD Makefile (shared aux), accelerated arm the NEW one, so the comparison was not format-vs-no-format; showed a renumbered bibliography that was a **confound, not a finding** | ~25 min, plus the 11-minute `difflib` hang it exposed |
| 4 | `bl/exp5.sh` | a concurrent `final`→`academico` rename landed mid-run; the copied Makefile had the alias, the copied entry files did not; `make final` failed in 0.9 s and the reference held 2 of 3 PDFs | one arm-set |
| 5 | `bl/exp6.sh` §D | the snapshot had `src/` but not `src_utils/`, and the Makefile reaches its tooling as `../src_utils`; `make fast3` died in 0.028 s for want of the script, not for any reason about the format | one arm |

**And one reporter defect of my own, which is the §2.3b shape exactly.** My stage reporter read
`build/<stem>.log`, which **survives** a cold wipe of the PDFs — so for the arm that produced
nothing it printed `main 108pp tex_errors=0`. A leftover file measured and presented as a
measurement of this run. `bl/exp7.sh`'s reporter requires the PDF *and* the log to exist and prints
`NO-BUILD` otherwise.

**The generalizable lesson, since this round is collecting them:** every one of these was caught by
a number that did not make sense (a 2,293-byte switch region where 229 bytes are live; 0.04 s for a
gate that runs 15 subprocesses; a perfect match from a build that refused; 0.9 s for a three-pass
build). None was caught by reading my own code. `AGENT_GUARDRAILS` §4b V3 — *distrust a clean result
from an unvalidated instrument* — is the rule that would have caught all five, and the corollary
this round adds is that **an implausibly good number deserves the same suspicion as an implausibly
bad one.**

### 6.1 · Nine claims about my own tooling that an audit pass found wrong

Recorded in full because this is §2.8's class arriving in a track whose author had just read §2.8,
and because the pattern across the nine is uniform: **each was written from what I had measured
adjacent to the claim, rather than from measuring the claim.** All nine are corrected in commit
`445bb172`, each against a fresh measurement.

| what I wrote | what re-measurement gave |
|---|---|
| harness costs ~7.5 ms per boundary (~0.14 s total) | ~17 ms per boundary, **~0.34 s** — a `gate` call spawns three perl processes, not one |
| `bookmark tree IDENTICAL` | two *unreadable* outlines were comparing equal; now `UNVERIFIED` and a failure |
| switch region "2,809 bytes for a region that is 130" | **2,293 bytes**, of which **229 in 5 lines** are live; blind `find()` spans 6,714 and starts inside the quoted command |
| "~32 s per pass, ~28 s preamble, ~87%" as measured here | inherited from the brief; this session measured whole-build 122.7 → 15.4 s and never decomposed a pass |
| re-dump takes "~28 s" | **33.7 s** and **36.0 s**, the two runs there were |
| footer: "round 7 measured every gate below 0.3 s" | true of the recorded run, stated as if it described the current one; now attributed |
| report: "Four things" | seven files (the brief asked for four; they landed as seven) |
| `check-scripts` "~1.9 s" | 1.855 s cold, **1.182–1.256 s** warm across four runs |
| report: "18 gates" | 19 — another track added one within the hour |

Three of the nine deserve their names said plainly. **The harness one** is the sharpest: I timed a
bare clock read and wrote that down as the cost of a boundary that does three of them plus
arithmetic. Timing a component and reporting it as the whole is the same error shape as
`FPDFText_GetFontSize` reading inside an XObject (§2.8, R2) — the reading was right, the question
was wrong. **The outline one** is a gate that could not fail. **The "~32 s per pass" one** is a
brief's inherited number laundered into a docstring under a "Measured on this machine" header, with
a date and a commit hash attached to lend it weight it had not earned — and that dressing is what
makes it worse than a bare guess.

---

## 7 · `[VERIFY]` flags and what I could not confirm

- **[RESOLVED after the checkpoint]** The concurrency arms completed and are in §3.2: `all3`
  157.9 s, `fast3` 20.7 s, both equivalent 3 of 3. The brief's inherited figures (291 s serial,
  45.3 s for three concurrent *first passes*) are **not** what this table measures — 45.3 s was
  three single passes, and every arm here is a full three-pass build with BibTeX. Do not compare
  the two directly.
- **[RESOLVED] `fast3` exit status.** Confirmed end to end after the fix, cold tree:
  `make fast3` → `make_errors=0`, all three `fastbuild` lines reporting `tex_errors=0` at
  105/108/109 pages, equivalence `3 of 3 targets compared, 0 skipped`, `compare rc=0`. That run
  took **61.1 s** rather than the 20.7 s of the earlier one — same command, same tree, 3x the wall
  time, which is the clearest single illustration of the contention caveat in §3: two other
  sessions were building and committing during it. Both runs produced correct, equivalent PDFs.
- **[VERIFY: absolute wall times]** Every second in §3 was measured while other sessions were
  building the same repository. `make defense` alone varied 105–128 s across four runs. Re-measure
  on an idle machine before quoting any absolute figure; the ratios are the durable claim.
- **[VERIFY: `make check` exit code]** The suite exits 0 on the current tree in my runs. The two
  known false positives `AGENT_HANDOFF` §3.5 documents (the technical term "Pareto" in published
  CBIC text; `apx_b_errata.tex`'s deliberate "this article") did **not** fire during this round —
  both are now exempted in `check.sh` by earlier commits. I did not re-verify that those exemptions
  are still correct; that is not this track's scope.
- **[VERIFY: page counts unchanged]** 108/105/109 with `tex_errors=0` was reproduced in the
  snapshot for every arm that completed. I did **not** run a fresh three-target build in the
  repository tree itself, because other sessions were building it concurrently and a collision
  there would corrupt their work. `sync_page_counts.py` passes against the logs on disk.
- **Could not confirm:** whether `make -j3` is safe under a *shared* `TEXMFVAR` font-map
  regeneration. `build.sh` regenerates the user map when it is missing; three concurrent
  `updmap-user` runs would race. It did not occur in any run here (the map was already present
  every time), and neither `make` path calls `updmap-user`, so the exposure is limited to
  `build.sh` — but it is unexercised, not proven safe.
- **Not attempted:** `latexmk`. `LATEX_UPGRADE.md` §1 candidate 4 rules it out explicitly for the
  pre-defense window, and the format dump gets the speedup without swapping the toolchain.

---

## 8 · Commands, for re-running any claim here

```bash
cd /Users/vitor/Desktop/mestrado/ingred/articles/dissertacao
source src_utils/texenv.sh

(cd src && make help)                    # every target
(cd src && make check)                   # THE gate, now with the per-gate timing table
(cd src && make check-scripts)           # 13 standalone gates, ~1.2 s warm, no build needed
(cd src && make format-status)           # is the dump fresh? rc=0 fresh, rc=1 stale/absent
(cd src && make fast)                    # defense, format-accelerated
(cd src && make all3)                    # three targets, concurrent
(cd src && make verify-equiv)            # the whole proof: plain -> reference -> fast -> compare

python3 src_utils/mkformat.py --selftest      # 10/10, split + key, both directions
python3 src_utils/verify_format.py --selftest #  9/9, comparator, both directions
```


---

<!-- estado-rodada -->
> **Rodada encerrada · último toque 2026-07-29 · sem autoridade.**
> Este ficheiro é registo de proveniência do que foi discutido nesta passagem, não fonte
> de um facto corrente. O que ficou decidido está em [`VEREDITOS.md`](../../../VEREDITOS.md);
> os valores entregues estão em `CLAUDE.md` §0.1. Não copie nada daqui sem confirmar lá.
