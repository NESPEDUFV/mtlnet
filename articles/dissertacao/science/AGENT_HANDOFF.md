# AGENT_HANDOFF.md — what a Claude Science agent needs before touching this repository

**Written 2026-07-27**, at the author's request, after five correction rounds on the dissertation.
**Audience:** the next Claude Science agent (or any AI assistant) asked to work on
`articles/dissertacao/`. **Author:** Vitor H. O. Silva, UFV/PPGCC, defense August 2026.

This file is not a summary of the dissertation and not a restatement of the law. Those exist:

| Read this | For |
|---|---|
| [`CLAUDE.md`](../CLAUDE.md) | the landing page, current state, decisions ledger, doc map |
| [`NORTH_STAR.md`](../NORTH_STAR.md) | the thesis, the arc, the chapter map, per-chapter errata |
| [`WRITING_LAW.md`](../WRITING_LAW.md) | the word-level law (register, canonical names, AI-tell bans) |
| [`GLOSSARY.md`](../GLOSSARY.md) | the fail-closed term registry |
| [`AGENT_GUARDRAILS.md`](../AGENT_GUARDRAILS.md) | the process law: citation, number and claim protocols |
| [`UFV_COMPLIANCE.md`](../UFV_COMPLIANCE.md) | the university's formatting requirements |
| [`src_utils/PENDENCIAS.md`](../src_utils/PENDENCIAS.md) | what currently needs the author |
| [`reviewers/README.md`](../reviewers/README.md) | the 19 review personas and when each is mandatory |

**What this file adds is the part no other document holds: the mistakes an agent working here
actually makes, and the mechanisms now in place to catch them.** Every entry below happened. Each
was found by review, almost never by the agent that caused it. Read this before you write anything;
it will save you from repeating a defect the author has already paid for once.

---

## 1 · The one rule that matters most

**A claim about your own verification is a claim, and it is the claim you are most likely to get
wrong.**

Across these rounds the work itself was usually right. What kept failing was the *record of the
checking*: source comments asserting a verification that had not run, commit messages recording
conditions that were false when written, file headers describing a check that never happened. Five
separate instances, all caught by review.

The mechanism behind every one of them is the same, and it is worth naming so you can avoid it:
**the cell that does the work is not the cell that should write the claim about it.** If you write
"verified" in the same breath as the edit, you are writing a prediction, not an observation. Do the
edit, run the check, read the result, *then* write what the result was.

Corollary: when you find you were wrong about something you already recorded, **correct it forward**.
The convention in this repo is a correction note attached to the commit (`git notes add`), not a
rewrite of history. Two commits carry such notes today. Hiding an error is worse than the error.

---

## 2 · Failure modes that have actually bitten this repository

### 2.1 Prose swallowed into a LaTeX comment (TEN instances)

A comment block written without a trailing newline pulls the following body line onto the comment.
The build succeeds. The sentence silently does not render. This has been the most persistent defect
in the repository: the regression suite pins **ten fixture cases**, covering six distinct source loci
across five files plus negative controls, and several of those were introduced *by edits fixing other
instances of it*. (The exact lifetime total is not worth asserting — what matters is that it recurs,
including under edits whose whole purpose was to fix it.)

- **Gate:** `src_utils/check_trapped_prose.py`, with `src_utils/test_trapped_prose.py` pinning every
  historical case. `check.sh` runs the fixtures **before** trusting the detector, because a green
  document means nothing when the checker is broken.
- **What defeated four earlier versions of that detector:** tuning it on the cases visible at the
  time. Length thresholds, vocabulary filters, sentence-completeness rules and parenthesis rules
  each missed the next instance. What works is the render test: extract the words after the last
  comment marker and check whether they appear in the built PDF.
- **When you edit:** end every comment block with a newline before the prose resumes. Then rebuild
  and run the gate. Do not assume.

### 2.1b A torn sentence: the opening clause simply gone (FOUR instances, in the Abstract)

A distinct defect from 2.1, and one the trapped-prose detector cannot see. Compressing a block, an
assistant replaced a span that ENDED at a sentence terminator, and the replacement dropped the
following sentence's opening clause. Nothing is trapped anywhere; the text is absent, the line above
is ordinary body text, and the build is clean. It rendered on pages 3 and 4 as:

> "... through multi-task learning (MTL). **sharing parameters** between tasks can hurt one of them ..."

Four instances, all in the Resumo and Abstract, i.e. the first prose a committee member reads. Found
by persona 03 reading the front matter **as rendered prose**, not as source.

- **Gate:** `src_utils/check_torn_sentences.py` — a body line opening with a lowercase word whose
  preceding non-blank body line ends in a sentence terminator. Validated both ways: zero on the
  repaired tree, exactly the four real defects when reintroduced. In `check.sh`.
- **The subtler lesson.** Those deletions had *closed a near-blank page*, and I reported the closure
  as a compression success. The page had closed **partly because text was missing**, not only because
  the text was tighter. When a layout problem resolves after an edit, confirm the resolution came from
  the change you intended.
- **And a second-order version of the same error.** Writing up that correction, I stated the split
  backwards: "real compression was ~13 words, the other ~30 were deleted clauses". The measured
  numbers are the reverse — genuine gloss compression 23 (PT) / 19 (EN), accidental deletion 13 / 14 —
  and "~30" reconciles with no grouping of them. An audit caught it. **When you correct a number,
  recompute both sides of the correction from the printed measurements rather than reasoning about
  which way round they went.**

### 2.2 A no-op substitution read as a measurement (TWICE)

A parameter sweep whose arms never applied returns identical results across arms, and identical
results look exactly like a converged null.

- Once a regex wrote `\needspace{N\\onelineskip}` with a doubled backslash, and the later sweep arms
  used a single-backslash pattern that could not match it. Three arms never ran. The conclusion drawn
  from them was false, and it was written into a durable source comment and two commit messages.
- Once a shell heredoc regex raised `bad escape \o` on every iteration, printing three identical
  lines from one unchanged build.
- **Gate:** `src_utils/sweep_guard.py`. `substitute()` raises when a pattern matches nothing, applies
  the wrong number of times, or the replacement equals what was there; `assert_distinct()` raises
  when every arm of a sweep returns the same value. Its self-tests pin both historical cases and run
  in `check.sh`.
- **The lesson beyond the tooling:** when a sweep gives you the same answer for every setting,
  that is evidence about your harness before it is evidence about the world.

### 2.3 Trusting the build log's silence

`pdflatex` does not report every layout failure the same way, and two classes were invisible to a
naive check:

- **Wrapped warnings.** LaTeX breaks warnings at 79 columns, so a line-anchored grep misses them.
  Four citations shipped as `(??)` in both delivered PDFs while the checker reported zero undefined.
  **Always flatten the log before matching**, and read the `.blg` as a separate source of truth —
  a BibTeX error does not appear in the `.log` at all.
- **Floats taller than the text block.** Reported as `Float too large for page by Npt`, not as an
  overfull box. A table hung 163pt below the bottom margin across four "clean" builds until the
  author noticed by eye. `build.sh` now extracts and fails on that warning.
- **Locale-dependent tooling.** `check.sh` once used `tr | grep` on the build log, which aborts on an
  invalid UTF-8 byte present in every log — so under a UTF-8 locale everything past that byte went
  unexamined. Match logs in Python with permissive decoding, never with `tr`.

### 2.3b The source did not compile for six commits, and the checker reported it clean

**The worst instance of §2.3 to date, found 2026-07-28.** From commit `6d780b58` to `a880632b` the
opening brace of the `{\small ...}` group in `tables/frame/bib_errata.tex` was missing (lost in the
tables reorganization; the closing brace survived). Every build raised
`! Extra }, or forgotten \endgroup`. Six consecutive commit messages nonetheless carried
"104/99 pp, 0 overfull, 0 undefined".

**The mechanism is the important part: the two build paths disagreed, and the one that was believed
could not see the error.**

| Path | Flag | Behaviour on this source |
|---|---|---|
| `make defense` | `-halt-on-error` | dies at the error, produces **no PDF** |
| `build.sh` | `-interaction=nonstopmode` | pdflatex **recovers** and writes a 104-page PDF |

`build.sh` then measured that PDF and reported `pages=['104'] overfull_hbox=0 undef_cite=0
undef_ref=0 oversized_floats=0`, because it never looked for TeX errors at all. Its only
"no PDF produced" branch could not fire, since a PDF *was* produced.

Two things made this survive so long. The recovered PDF was **not junk**: its single visible defect
was one appendix table rendering at body size instead of `\small`, which nobody would notice without
comparing. And nobody ran `make`, which would have failed on the first pass.

- **Gate:** `build.sh` now extracts every `! ...` line plus the fatal notice, reports `tex_errors=N`,
  prints the first five, states that the nonstopmode PDF is not the document, and fails. Validated
  in both directions against the `ac87e5d7` tree (reports 1) and the fixed tree (reports 0).
- **The rules.** `tex_errors=0` is part of every build claim from now on. **A PDF existing is not
  evidence the source is correct.** When two tools disagree about the same artifact, the one
  reporting success is the one to distrust. And nonstopmode is for *reading* a log, never for
  certifying a build: run `make` too, because `-halt-on-error` is the honest signal.
- **Also:** `src_utils/texenv.sh` now holds the three environment variables this stack needs, each
  with its failure mode written down. A wrong `TEXMFVAR` produces
  `Font ntx-Regular-tlf-ot1r at 657 not found`, which looks like a missing font and is a missing
  font *map*; `kpsewhich -var-value TEXMFVAR` reports an unreadable path here, so it cannot be
  probed and must be set.

### 2.4 Stale committed build residue

`chapters/*.aux` and `main.aux` had been committed at the source root. BibTeX resolves those paths
relative to the source directory, so they shadowed `build/` and fed it a pre-rename citation key.
That is what produced the four `(??)` citations. They are now gitignored with the reason recorded.
**Never commit `.aux`, `.bbl`, `.blg`, `.log`, `.toc`, `.lof` or `.lot` at `src/`.**

### 2.4b An artifact saved from a stale workspace copy (TWICE)

The workspace and the repository are different directories. A deliverable is written in the repo, then
copied to the workspace, then saved as an artifact from there. Twice the copy silently did not happen:
a `cd` earlier in the same shell cell had moved the working directory, so a `cp <repo file> .` landed
somewhere else, and the save promoted the PREVIOUS workspace file.

**This failure is invisible at save time.** The artifact store deduplicates identical content, so the
save echoes the old version's size and checksum and reports success. The second occurrence shipped a
register artifact that did not contain the section the accompanying message promised.

- **Gate:** `src_utils/sync_deliverables.py --workspace <abs path>` copies with absolute paths on both
  sides, re-reads both files, compares sha256, and fails on mismatch. `--require FILE='substring'`
  additionally asserts the new content is present in the copy, which is the check that catches this
  class. Validated both ways: exits 1 on a stale copy, 0 when correct.
- **The rule:** never `cd` and `cp` in the same cell when the destination is relative. Use absolute
  paths for both sides, and verify by checksum rather than by the copy command's silence.

### 2.5 Build tooling living only in `/tmp`

The build script lived in `/tmp` for a whole session and was swept mid-session, which silently turned
"rebuild and check" into "check a stale PDF". That is the mechanism by which three broken sentences
shipped. It is now committed at `src_utils/build.sh` and fails loudly when no PDF is produced.

It also carried a path bug for a long time — it `cd`s into `$SRC` and then passed `$SRC` again to its
own verifier — masked because it was always invoked from one directory. **Resolve script paths from
`BASH_SOURCE` before any `cd`**, the way `check.sh` does for `SRCROOT` and `UTILS`.

### 2.6 Records that drift from the thing they describe

Page counts in the governance files drifted three times (87/83, 89/84, 103/98, 104/99), every time
caught by review rather than by the edit that caused it. The page-drift note in `codex_reviewer.md`
is load-bearing: it tells a reader how far every `file:line` in that review has moved.

- **Gate:** `src_utils/sync_page_counts.py` reads the count from the build logs, checks all ten
  recorded claims, exits 1 naming the stale file, and repairs with `--write`. `check.sh` runs it.
- The same class of drift hit the `[NEEDS SIGN-OFF]` inventory twice. Regenerate that table from
  measurement, never by hand, and give it a total row so the rows and the headline cannot disagree.

### 2.7 Probes that lie

Several conclusions were nearly published from broken probes. Each was caught by noticing a result
that did not make sense:

- `git` invoked from the analysis kernel returned **empty** because it could not read the user's
  config, making a count meaningless. Route git through the shell.
- A citation-usage check counted a **commented-out** `\cite` as a live citation.
- A table parser grabbed the wrong column, then silently dropped every row wrapped in `\textbf{}`.
- A margin check flagged 19 pages as overflowing; they were **descenders** (`g`, `p`) on lines
  sitting legitimately on the margin.
- An attempt to derive a reference ceiling assumed stride-1 windows; the data disagreed at 18%
  agreement, and the assumption was wrong.

**When a probe gives you a surprising number, suspect the probe first.** Verify it against a case
whose answer you already know.

### 2.7b A remote job that exits 0 having measured nothing (THREE times in one night)

**Found 2026-07-29**, on the `nespedgpu` host, while producing data for the gradient-cosine appendix.
Three consecutive submissions of the same script reported success or ran clean, and the first two
produced no usable data at all. Each failure was a different mechanism and each was invisible in the
job's own status:

1. **`rc=127`, six times, in one second.** A submitted job runs in a NON-LOGIN shell: there is no
   conda and no venv on `PATH`, `which python` returns nothing, and only `/usr/bin/python3` exists
   (without torch). The script called bare `python`. Because the loop swallowed each return code and
   the tarball step still ran, the wrapper exited 0 and `compute_done` reported **success** with
   `output_file_count: 0`. Fix: call the repo's interpreter by absolute path
   (`/home/vitor.oliveira/PoiMtlNet/.venv/bin/python`) and probe it before the loop.
2. **Clean runs, empty column.** Three states then trained to `rc=0` and harvested 5 well-formed
   diagnostics CSVs each — with **every `grad_cosine_shared` cell empty** and `grad_norm_*` all
   `0.0`. The diagnostic is **opt-in**: `src/training/runners/mtl_cv.py:1520` gates it on
   `MTL_TRAIN_DIAGNOSTICS=1`, which defaults **off** (flipped 2026-07-01 because the batch-0 cosine
   costs two extra full backwards per epoch with `retain_graph`). With it off the column is written
   as `NaN`. Training numerics are unaffected either way, so turning it on does not change the model.
3. **The `orphaned` status is a false alarm on this host** (already in the provider notes): the
   daemon's poller flags a job orphaned within minutes while the process is alive and the GPU busy.
   `orphaned` is not evidence of failure, and `success` is not evidence of data.

**What I did wrong, and it is the reusable part.** After (2) I told a sub-agent that per-state data
was arriving, because the job said `rc=0` and the files had the right shape and row count. **I had
not opened one.** A file is not data. The check that would have caught it is one line:

```bash
awk -F, 'NR>1 && $2 != "" && $2 != "nan" {c++} END {print c+0}' fold1_diagnostics.csv
```

**The gate now in the run script:** a state counts as harvested only when its cosine column carries
numbers, and the wrapper exits non-zero when nothing was harvested — so a run that measures nothing
can no longer present as a green job with an empty tarball.

**The rule.** Before reporting that a remote job produced data, open one output file and count the
non-empty cells in the column you came for. Exit status, file count, file size and header shape are
all satisfied by an empty result.

### 2.7c Concurrent jobs on one GPU: OOM, and a harvest race that duplicates data silently

**Found 2026-07-29**, producing the per-dataset gradient-cosine data. After a six-datasets-in-one job
was killed at the host's ~35 min wall-clock cap, I split the largest dataset into five per-fold jobs
and submitted all five at once, alongside two other datasets. Seven concurrent jobs, one A40, 46 GiB.
Three failures, each instructive:

1. **CUDA out of memory.** Three of the five folds died with `Process 947712 has 4.17 GiB memory in
   use. Process 947858 has 4.01 GiB memory in use`. Parallel submission on a **single-GPU** host does
   not parallelize anything — it converts a queue into a memory fight. Submit sequentially, or one
   job at a time, and let the cap decide how much fits.

2. **The cap fired again on the two datasets that were sharing the GPU**, so contention turned a job
   that would have fit into one that did not.

3. **THE ONE THAT WOULD HAVE REACHED THE DISSERTATION.** Two folds reported success and their
   harvested CSVs were **byte-identical on the host** (same md5). Two genuinely distinct run
   directories existed — but the harvest step selects the newest `mtlnet_*` directory with
   `find -newer <sentinel>`, and with concurrent jobs that is a **race**: both jobs resolved to the
   same directory. Compounding it, `--only-fold k` writes its output as `fold1_diagnostics.csv` for
   **every** k, so the filename carries no fold identity and nothing downstream can attribute a file
   to a fold.

   The result was two files claiming to be different folds, actually one run duplicated, with no
   evidence on disk to tell them apart. Had they been used, the appendix would have reported a
   five-dataset result containing one fabricated fold. **The data was discarded**, and the dataset is
   still listed as outstanding rather than partially reported.

**The rules.** On a single-accelerator host, run jobs sequentially. Never select an output directory
by recency when more than one job can be writing — pass an explicit output path, or derive the
directory from the job's own identifier. And when a tool names its output the same thing regardless of
which slice it computed, the slice identity must be carried by the directory you put it in, checked
before the file is used: two files that should differ and do not are evidence of a harvest fault, not
of an interesting result.

### 2.8 The claim about the work, written from intent instead of output (TWELVE instances in one day)

**This is now the largest failure class in this repository, and §2.1 through §2.7 are all special
cases of it.** Round 6 (2026-07-28) ran 13.3 hours and 61 commits; 17 were rework, 14 of those
genuine, and **12 of the 14 were a wrong statement about the work** rather than about the
dissertation. Zero were fabricated citations. The science protocols held. What failed was every
sentence of the form *"the sweep covered N files"*, *"all gates pass"*, *"every command was
executed"*.

The mechanisms, because the mechanism is what generalizes. Each bullet is tagged with its root cause
from `AGENT_GUARDRAILS.md` §4b, so the grouping is checkable rather than asserted. **R1 (5) + R2 (4)
+ R4 (3) = the twelve** meta-claim defects; **R3 (1) + R5 (1)** are the other two genuine rework
commits, kept here because they carry the same lesson without being the same defect. Note the
bullets are **six illustrations of fourteen commits**, not one bullet each: R1's five instances and
R2's four are described together where they share a mechanism. Count the commits from the §4b
table, not from these bullets:

- **[R1] The producing code contained a skip, and the claim did not mention it.** A sweep reported
  "19 blocks, 0 failing" while its own loop began `if "make" in code: continue` — four blocks never
  ran and the skips were counted as passes. The same shape twice more: `make check` exited 2 for a
  full day while six commit messages said all gates pass (the output was read for known-good lines
  instead of for `$?`), and a page-count syncer printed `SKIP` and exited 0 when its pattern stopped
  matching, so nobody was checking four page-count claims.
- **[R2] The instrument could not see the thing being claimed.** `FPDFText_GetFontSize` reports the size
  declared *inside* an embedded XObject and ignores `\includegraphics` scaling, so it read 6.97 pt
  for a figure rendering at 11.15 pt. The reading was correct; the question was wrong. Ask what an
  instrument is blind to *before* building a claim on it.
- **[R2] A line-based `grep` missed a match sharing a source line with another.** Gave 8-of-12 where the
  truth was 9-of-13, and the omitted file was one the author needed to publish. Related and separate:
  greps over this source **must strip comments first**, because the provenance comments quote the
  strings being searched for — an unfiltered `\path{}` count annotated `# 13` returned 15, a sweep
  promising 3 prose hits returned 4, and one promising **zero** returned 5. Filter the *file*
  (`grep -vn '^[[:space:]]*%'`), not the `grep -n` output: `:[0-9]*: *%` misses an indented comment.
- **[R3] A record's superseded revision was read as current.** Files under `docs/studies/` keep their own
  prior revisions inline under headings that say `(superseded)`. A search landing inside one found a
  real sentence that had stopped being true, and the flag it raised would have weakened a correct
  claim in the abstract, the conclusion and a paper under review. **Anchor on the revision header.**
- **[R4] Correcting the number at its source did not correct the claim.** When 8-of-12 became 9-of-13, the
  old figure survived in four other durable records, including the author's own push list — which
  listed eight files when nine needed pushing. After any count fix, grep the *superseded value*.
- **[R5] A new guard was itself defective.** The gate written to catch this class recursed into its own
  caller (taking `make check` from 1 s to 297 s) and its first fix reported zero skips while still
  recursing, because a broad "is this just a `cd` note?" test sat *above* the narrow recursion guard
  and swallowed the cases it existed for. **Ordering is load-bearing; a skip is never silent.**

**The gate:** `src_utils/check_verify_list.py`, run by `check.sh`. It executes every command
documented in the author-facing files, asserts the ones carrying an `# EXPECT:` annotation, and
reports *executed-but-not-asserted* as its own category so the verified count cannot be inflated.
Extend it rather than writing a fresh unverified claim. The law is `AGENT_GUARDRAILS.md` §4b.

**The one-line version, if you remember nothing else:** *before writing a number about your own
work, read the tool's last lines again and copy from them.* These cost 2.4 hours, and every
one was caught by somebody else re-running the check.

---

## 3 · How to work here

### 3.1 The errata regime — the single most important thing to understand

Chapters 3, 4 and 5 **reproduce published or submitted articles**. They are a time capsule.

- **Published text (CBIC ch.3, CoUrb ch.4):** you may not silently edit it. A change is either a
  footnote or an entry in Appendix B's errata tables, which now live in `src/tables/<article>/`.
- **Submitted-and-under-review text (MobiWac ch.5):** the author's standing ruling as of 2026-07-27
  is that a **minor** correction does **not** need an erratum — apply it to
  `articles/[mobiwac]/src/` as well, keep the two texts identical, and log it in
  `articles/[mobiwac]/ERRATA.md`. Only corrections too elaborate for a paper under review stay
  errata (currently two: one cites Appendix D, one cites the dissertation's own results table).
- **Frame text (ch.1, ch.2, ch.6, appendices):** freely editable, no errata cost.
- **When you port a correction to the paper**, remember the two traps that caught me: dissertation
  labels are prefixed (`sec:mobiwac:setup-windows`) and do not exist in the paper
  (`sec:setup-windows`), and phrases like "this chapter's claims" must become "the paper's claims".

### 3.2 The glossaries — and the one that is easy to miss

`GLOSSARY.md` is fail-closed: a term not in the registry may not be used. But **for Chapter 5 there
is a second, stricter glossary that wins**: `articles/[mobiwac]/GLOSSARY.md`, 393 lines, with a
26-row jargon-to-plain substitution table carrying a verdict column (keep / gloss once / avoid /
never) and a section of words to avoid or always explain.

Persona 03's own brief names that file as authoritative for Chapter 5 — and its 2026-07-26 report
contained zero references to it, so the law went unapplied for a full round. I then introduced a
never-use word (`arm`, "clinical-trial word, foreign to this audience") into Chapter 5 myself, and
my port carried it into the paper. **If you touch Chapter 5, lint against that file row by row.**

Distinguish carefully: a banned word describing **another paper's** method is usually legitimate
("activity" when reporting what MCARNN predicts); the same word in **our own** claims is not.

### 3.3 Numbers

`AGENT_GUARDRAILS.md` §2 is the law; three practical notes from experience:

- **Quote, never compute.** Every number traces to a committed file. If it does not exist there,
  flag `[VERIFY]` rather than deriving it.
- **A number is not just a value, it is a quantity.** Twice a figure was replaced by a *different
  quantity* that happened to be numerically close: a place-level share standing in for a
  region-level one, and a model's top-1 accuracy standing in for a persistence share (32.06 against
  the true 32.91). Both passed casual review precisely because the magnitudes looked right. State
  what the number measures, on which windows, under which protocol.
- **When you compute something new, commit a generator.** `scripts/embedding_eval/` has two examples
  that gate themselves: `autocorrelation_ceiling.py` and `region_persistence.py`, which refuse to
  emit a number when their window count disagrees with the artifact they are compared against.

### 3.4 The review personas are not optional

`reviewers/` holds 19 briefs; `reviewers/README.md` says when each is mandatory. Two are load-bearing
and were both skipped for a full round:

- **03 (style auditor)** is the G3 gate, required before *every* advisor handoff.
- **16 (AI-credibility)** is required before advisor and committee builds. Its first run on the
  current text found a doubled backslash rendering a macro name onto the page.

Findings from these personas have been consistently better than my own self-checks. Treat a persona
report as evidence and verify each finding against the source yourself — several have been wrong, and
saying so with evidence is part of the job.

### 3.5 Build and gate, every time

```
cd articles/dissertacao
source src_utils/texenv.sh         # REQUIRED: PATH, TEXMFHOME, TEXMFVAR, TEXMFCONFIG. See below.
(cd src && make defense && make final)   # -halt-on-error: the HONEST pass/fail signal
./src_utils/build.sh src both      # the report: pages, tex_errors, overfull, undefined, oversized floats
cp src/build/main.pdf src/dissertacao.pdf
python3 src_utils/sync_deliverables.py --workspace <abs>   # before ANY save_artifacts
./src_utils/check.sh               # sweep-guard tests, page-count sync, trapped-prose fixtures,
                                   # torn-sentence check, style lint
python3 src_utils/sync_page_counts.py --write   # if the page count moved
```

**Run `make` as well as `build.sh`, and read `tex_errors`.** `build.sh` uses
`-interaction=nonstopmode`, under which pdflatex recovers from an error and still writes a PDF; that
is how a source tree with a LaTeX error passed six builds (§2.3b). `make` uses `-halt-on-error` and
produces nothing when the source is broken, which is the signal you want. `build.sh` now reports
`tex_errors=N` and fails on it, so either tool catches it today, but running both is cheap and the
two disagreeing is the diagnostic.

**Source `src_utils/texenv.sh` first**, or the build fails in one of two ways. Without `TEXMFHOME`:
`abntex2.cls not found`, which is honest. With the wrong `TEXMFVAR`:
`!pdfTeX error: Font ntx-Regular-tlf-ot1r at 657 not found ==> Fatal error`, which is misleading —
the `.tfm` and `.pfb` are both present in the home tree, and what is missing is the font *map* that
newtx writes into the usermode updmap output. `kpsewhich -var-value TEXMFVAR` reports an unreadable
path on this machine, so the value cannot be probed and the script sets it explicitly.

`check.sh` currently exits 1 on **two known false positives**, both of which must stay: the word
"Pareto" in `3_cbic.tex` trips the banned-verdict-verb sweep (it is the technical term,
Pareto-optimal and Pareto-stationary, in published text), and `apx_b_errata.tex:242` trips the
"this article" sweep in a sentence that is deliberately about the MobiWac *article* rather than about
the chapter. Read the output rather than the exit code, and do not "fix" those.

### 3.6 Commit style

`draft(ai):` for new prose, `fix:` for corrections, `refactor:` for structure, `docs:` for records.
Write the message so the author can audit the change without opening the diff: what changed, what
the evidence was, and what you verified afterwards. When a message turns out to have been wrong,
attach a `git notes` correction rather than rewriting it.

---

## 4 · Repository geography

```
articles/dissertacao/
  CLAUDE.md NORTH_STAR.md WRITING_LAW.md GLOSSARY.md      the law; read before writing
  AGENT_GUARDRAILS.md UFV_COMPLIANCE.md PLAN.md TEMPLATE.md
  src/                      LaTeX source
    main.tex                34 lines: mode switch + one \input. ONE source, TWO build modes
    0_main.tex              preamble + front matter + chapter includes
    chapters/               one file per chapter
    tables/<article>/       one file per table, \input from its chapter (cbic/ courb/ mobiwac/ frame/)
    figures/<article>/       same convention
    build/                  all output; gitignored
  src_utils/                tooling + the live registers
    build.sh check.sh       build and gate
    check_trapped_prose.py test_trapped_prose.py sweep_guard.py sync_page_counts.py
    PENDENCIAS.md           what needs the author
    codex_reviewer.md CODEX_VS_PERSONAS.md                  external review + the persona seam
                              (CODEX_AUDIT.md moved to _history/_archive/ on 2026-07-29; its nine still-open
                               points were lifted into PENDENCIAS.md §5 before the move)
    _history/_review_v2/ _review_v3/ _history/_specialists_v2/                persona reports
    _history/_archive/               superseded working files, with a README index
  reviewers/                the 19 persona briefs
  science/                  this file, plus the science background prompts
  exemples/                 five exemplar dissertations (PDF); Germano is the closest precedent
articles/[mobiwac]/         the submitted paper: its own GLOSSARY.md and ERRATA.md are authoritative
articles/CBIC___MTL/        the published CBIC article (version of record for ch.3)
articles/CoUrb_2026/        the published CoUrb article (version of record for ch.4)
docs/                       results, studies and protocol records; numbers trace here
```

---

## 5 · Things about this author that will make you more useful

- **He audits.** Every claim you make will be checked, and he has caught errors in five separate
  rounds. Self-reported success is not trusted here, and should not be.
- **He asks "what do you think?" and means it.** When he proposes something, an opinion with evidence
  is worth more than compliance. Twice a measurement changed his mind, and twice it changed mine —
  including one case where his hypothesis about a data leak was refuted by measuring the data.
- **He objects to specifics, not vibes.** "Appendix D is confusing" turned out to be a concept
  collision between two similarly-named quantities plus a term defined only in another chapter — not
  sentence length, which measured *shortest in the document*. Measure before you rewrite.
- **He owns every word.** You draft; he approves. When something needs his call — a co-author
  courtesy notice, a claim about the program's practice, a sentence in his own name about his own
  process — record it in `PENDENCIAS.md` and stop. Do not write it for him.
- **Comment density is a live complaint.** Provenance comments earn their place; process narration
  ("why I changed this in July") does not. When I measured, 1,254 of 1,324 comment lines were
  provenance-bearing, so there was less fat than either of us assumed — but the 16 table files had
  repeated the same 8-line paragraph 16 times, which was real and is now in one README.

---

## 6 · Open threads as of 2026-07-27

Read `src_utils/PENDENCIAS.md` for the authoritative list. The shape of it:

- **Administrative and blocking:** committee names and defense date, cover and approval sheet, the
  advisor bundle (English frame, CoUrb inclusion, final title, errata policy), 32 `[NEEDS SIGN-OFF]`
  markers.
- **Scientific exposure:** the Chapter 4 static-task scope, which is measured and unfavourable and
  needs a co-author courtesy notice before anything is written about it.
- **Advisor's second point:** where his in-text markings of the odd term insertions are. Persona 03
  is running against the MobiWac glossary, but his own list is the ground truth and has not arrived.
- **Deliberately deferred:** the Chapter 4 figure relabelling (blocked on source art), the
  reproducibility appendix (worth doing — four of five exemplars have one — but only once the text
  settles).
