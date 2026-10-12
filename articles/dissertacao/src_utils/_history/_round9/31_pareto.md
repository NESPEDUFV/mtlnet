# 31_pareto.md — the Pareto foundations of §2.3, and the glossary gap that came with them

**Round 9, track "Pareto". Written 2026-07-30. Baseline tree: HEAD `d4078c75` (NOT the `b89a9876`
the brief names; the parallel track had already committed).**

**Why this exists.** `CONSIDERATIONS.md:1228`, the author's own words: *"On the MTL fundamentals that
we need to improve do we talk about the optimality of pareto, and do we need to talk about it? I have
a feeling that since we talk a bit of the balancers we need at least breif take about this."* He is
right, and the gap is measurable. Measured at the baseline tree, from
`articles/dissertacao`:

```bash
grep -ci pareto src/chapters/2_fundamentals.tex   # 0
grep -c  'Nash-MTL' src/chapters/2_fundamentals.tex  # 2 live prose + 1 in the section ledger comment
grep -ci pareto GLOSSARY.md                       # 0
```

The chapter names the balancers and never defines the notion their guarantees are stated about. This
also closes PENDENCIAS **2.12**, whose recorded decision is `DESICAO: A.` (register the term).

---

## §1 · What the five methods actually claim

Every statement below was located in the paper's own PDF, downloaded from arXiv **this session** and
read with `pypdfium2`. Page numbers are the PDF's own pages. The four attribute fields (authors,
title, venue, year) were checked against the arXiv Atom API this session; every `booktitle` already
in `src/references.bib` agrees with the venue in the paper's arXiv comment field.

| key | identifier (opened this session) | venue per arXiv comment | the exact claim, and where |
|---|---|---|---|
| `nash` | arXiv:2202.01017v2, 19 pp. | `ICML 2022` | **Theorem 5.4, p6**: for the stated step size, the iterate sequence *"has a subsequence that converges to a Pareto stationary point"*, and the losses converge to that point's values. **Theorem 5.5, p6 and restated p14**: *"if we also assume that all the loss functions are convex then the sequence ... converges to a Pareto optimal point"*. Definitions on **p2**. |
| `sener2018mgda` | arXiv:1810.04650v2, 15 pp. | `NeurIPS 2018` | **Definition 1, p3**: dominance and Pareto optimality, the Pareto set and the Pareto front. **p4**: *"Although every Pareto optimal point is Pareto stationary, the reverse may not be true"*, then Desideri's result that the solution is either 0 (KKT satisfied) *"or the solution gives a descent direction that improves all tasks"*. **Theorem 1, p6**: for MGDA-UB, either the point is Pareto stationary or the combination *"is a descent direction that decreases all objectives"*. The abstract (**p1**) claims Pareto optimality **for the upper bound**, *"under realistic assumptions"*. |
| `liu2021cagrad` | arXiv:2110.14048v2, 20 pp. | `NeurIPS 2021` | **Definition 3.1, p4**: Pareto dominance, Pareto optimality, and Pareto stationarity as $\min_{w} \lVert g_w(\theta)\rVert = 0$ over the probability simplex. **Theorem 3.2, p5**: *(1)* for any $c \ge 1$, *"all the fixed points of CAGrad are Pareto-stationary points"*; *(2)* for $0 \le c < 1$ *"the algorithm converges to a stationary point of $\nabla L_0$"*, the average loss. **p1** states the family criticism this dissertation should not paraphrase away: prior methods *"lack convergence guarantee and/or could converge to any Pareto-stationary point"*. |
| `senushkin2023aligned` | arXiv:2305.19000v1, 16 pp. | (no comment field; the bib's CVPR 2023 / pp. 20083--20093 was already verified in an earlier round and is not re-asserted here) | **Definition 1, p5**: Pareto stationarity, and *"All possible Pareto-stationary solutions form a Pareto set (or Pareto front)"*. **Theorems, p12 and p13**: gradient descent with an aligned gradient *"converges linearly to a Pareto-stationary point"* for task weights fixed in advance. Its whole argument against the family, **p2 and p5**: methods that converge to *an arbitrary* Pareto-stationary solution *"tend to overfit to a subset of tasks"*. |
| `yu2020pcgrad` | arXiv:2001.06782v4, 27 pp. | `NeurIPS 2020` | **THE WORD "PARETO" DOES NOT OCCUR IN THE PAPER.** Measured, and the instrument was validated on the same extraction: 27 pages, 90,294 characters, 185 occurrences of "gradient", 25 of "theorem", 14 of "cosine similarity", **0 of "Pareto"** (case-insensitive, both hyphen forms). What it proves instead: **Definition 1, p3**, gradients are *"conflicting when $\cos\phi_{ij} < 0$"*; **Theorem 1, p4**, in the two-task convex Lipschitz setting the update converges to either the optimum or a point where $\cos\phi_{12} = -1$; **Theorem 2, p5**, one PCGrad update attains a loss no higher than the plain multi-task gradient's **under three stated conditions** on the angle, the curvature and the step size. |

**The difference is the point, and it is not decoration.** Three of the five state their guarantee in
terms of Pareto stationarity (`nash`, `liu2021cagrad`, `senushkin2023aligned`), one states it as a
dichotomy between stationarity and a common descent direction (`sener2018mgda`), and one makes no
Pareto claim at all (`yu2020pcgrad`). Nash-MTL reaches Pareto *optimality* only with convexity added,
which a deep network does not give. Two of the papers make the sharpest point themselves: converging
to *some* point on the front says nothing about *which* point, so the task balance at the end is
unknown (`liu2021cagrad` p1, `senushkin2023aligned` p2/p5). A chapter that writes "these methods
converge to a Pareto-optimal solution" would be wrong about four of the five.

**Not opened, and therefore not cited:** Desideri's original MGDA paper. It has no entry in
`src/references.bib` (`grep -in desideri references.bib` -> rc=1, no output), it is reachable in this
sandbox only as a secondary reference inside the two papers above, and no sentence drafted here needs
it. The MGDA attribution in the new prose goes to `sener2018mgda`, which is the entry the document
already has and the form in which the dissertation uses the method.

---

## §2 · The two published sites, checked against the source

The brief says two sites. **There are five live occurrences in four files**, and the count matters
because a term-registration decision has to cover all of them. Measured with the comment-stripping
convention `AGENT_GUARDRAILS §4b V4` requires (strip the file, not the `grep -n` output):

```bash
cd articles/dissertacao/src
for f in $(grep -ril 'pareto' --include="*.tex" .); do \
  echo "$f live=$(grep -vn '^[[:space:]]*%' "$f" | grep -ci 'pareto')"; done
# ./tables/courb/errata.tex          live=1
# ./chapters/3_cbic/method.tex       live=1
# ./chapters/3_cbic/basis.tex        live=2
# ./chapters/4_courb/methodology.tex live=1
```

Each was then located in a **rendered** PDF, not in the source. **Every page number below is measured
against the 101-page defense build of this commit** (`cd src && make defense`) and the 20-page
supplementary build (`make extra`); the §2.3 passage this track adds costs one page, so all four
pre-existing sites moved by one from the 100-page pre-edit build, and the pre-edit figures 30/31/36/48
are superseded. A page number is only true of the build it was taken against, so the build is named
rather than assumed.

| site | renders at | is it published prose? | verdict against the source |
|---|---|---|---|
| `3_cbic/basis.tex` "MGDA finds Pareto-optimal descent directions" | defense **p31** | **yes, verbatim.** The whole sentence is a substring of `articles/CBIC___MTL/sections/basis.tex` (checked programmatically, not by eye) | **Defensible, and imprecise in the source's own terms.** `sener2018mgda` p4/p6 states the dichotomy: the direction either certifies Pareto stationarity or *"decreases all objectives"*; the paper's Pareto-*optimality* claim is for the upper bound under assumptions (p1), not for the descent direction. The published wording compresses that. **Leave it.** It is published prose, the compression is the one the MTL literature routinely makes, and nothing in the dissertation depends on it. |
| `3_cbic/basis.tex` "theoretical guarantees of Pareto efficiency ... remain open research directions" | defense **p32** | **yes, verbatim** | **Correct.** A statement about open problems, not about a method's guarantee. Nothing to fix. |
| `3_cbic/method.tex` "with $\eta$ chosen to ensure monotonic loss decrease and convergence to a Pareto-stationary point" | defense **p37** | **yes, verbatim** | **Correct, and precisely so.** Both halves are in `nash`: monotone decrease of every loss is used in the Theorem 5.4 proof (p6, *"the losses are monotonically decreasing and bounded below"*), and the destination is *Pareto stationary*, not Pareto optimal. The sentence does not overstate the guarantee. **Leave it.** |
| `4_courb/methodology.tex` "Away from a Pareto-stationary point, meaning a point at which some convex combination of the task gradients is zero, and under the method's assumption that the gradients are linearly independent there, that direction is a descent direction for every task" | defense **p49** | **no.** This is the dissertation's own errata-corrected sentence. The published PT source has **zero** occurrences of the term: 9 `.tex` files under `articles/CoUrb_2026/src`, 0 live "pareto" | **Correct on every clause.** The gloss is `nash` p2 verbatim in substance (*"a point is called Pareto stationary if there exists a convex combination of the gradients at this point that equals zero"*); the linear-independence condition is Assumption 5.1 (p3, p6); the descent-direction property is the authors' own (p6, *"our update rule is a descent direction for all tasks"*). Already listed in Appendix B. **Leave it.** |
| `tables/courb/errata.tex` the Appendix B row recording that correction | **extra volume p16** (this row is NOT in the defense build; `apx_b_errata` is included only from `main_extra.tex:249`) | n/a, it is the errata record | **Correct**, and it states the approximation caveat the method's paper carries. **Leave it.** |

**No errata matter arises from this track.** Every published sentence states its source's guarantee
correctly, and the one imprecision (MGDA "Pareto-optimal descent directions", p31) is inside
reproduced published prose where the errata regime's cost exceeds the reader's gain. It is recorded
here so the author can decide otherwise; **it was not edited.**

**One thing the author may want to know, since it is his own history.** In
`articles/[mobiwac]/REVIEW_GERMANO.md:778` the advisor asked for exactly this concept in the MobiWac
paper (*"pode parafrasear o pareto. Otimalidade de pareto que discute esse ponto"*), and the recorded
response declined it there on the grounds that no multi-objective citation existed in that paper's
bibliography to carry it. The dissertation does not have that problem: `sener2018mgda`, `nash`,
`liu2021cagrad` and `senushkin2023aligned` are all in `src/references.bib` and all four are cited in
§2.3 already. So the request he made on the paper is answerable in the frame chapter, which is the
right place for it anyway.

---

## §3 · Terms registered

Placement follows the author's chosen option (a) in PENDENCIAS_RESOLVIDOS 2.12 (arquivado 2026-08-02), which names §4 of the glossary.
Every definition is taken from a source opened this session, with the source named in the row.

| term | PT | source of the definition |
|---|---|---|
| Pareto dominance | dominância de Pareto | `liu2021cagrad` Def. 3.1 p4; `nash` p2; `sener2018mgda` Def. 1(a) p3 |
| Pareto optimality (Pareto front) | otimalidade de Pareto (fronteira de Pareto) | `nash` p2; `sener2018mgda` Def. 1(b) p3 |
| Pareto-stationary point | ponto Pareto-estacionário | `nash` p2 and p6; `liu2021cagrad` Def. 3.1 p4 |
| gradient conflict | conflito de gradientes | `yu2020pcgrad` Def. 1 p3 (the cosine, negative meaning conflict) |

**PT wording, flagged rather than settled.** `otimalidade de Pareto` is **not** coined here: it is
the author's own phrasing in `PENDENCIAS.md:98` and the advisor's in `REVIEW_GERMANO.md:778`. The
other three PT strings are standard renderings but are **not attested anywhere in this repository**,
so they are marked in the glossary as proposed and are listed in PENDENCIAS_RESOLVIDOS 2.12 (arquivado 2026-08-02) for a one-line
confirmation. None of the four appears in the Resumo or in any Portuguese surface today; the PT
column exists because §6 is the registry's convention, not because a PT surface needs them yet.

---

## §4 · The passage, and what it deliberately does not do

Drafted into §2.3 between the negative-transfer paragraph and the balancer catalogue, which is where
the reader meets the vocabulary. It does four things: writes the weighted-sum objective so the
balancers have something to attach to (advisor item **G8.1**); defines dominance, optimality and
Pareto stationarity once each; separates what each method proves from what the family is read as
proving; and defines gradient conflict as the cosine between per-task gradients (advisor items
**G8.4** and **G10**, `CONSIDERATIONS.md` work-list item 28), which is what makes Appendix F's
orthogonality result legible instead of, in the advisor's words, *"jogado no artigo e sem contexto"*.

**Scope held deliberately narrow, and the reasons are not stylistic.**

- **No number from Appendix F is repeated.** Work-list item 28 says define the measure in §2.3 and
  do not report the value there. The appendix is cited by `\ref{apx:cosine}` and never by dataset
  count, because the parallel track may be extending it from four datasets to six while this is
  written.
- **The mechanism claim is scoped to the architecture the appendix measured.** Appendix F's own
  `\label{apx:cosine:extension}` says its mechanism section *"applies only to models shaped like this
  one"*, so the new prose attributes the reading to the appendix and does not extend it to Chapter 3's
  model, which was never measured.
- **The rest of G8 was not executed.** No subsections were added, the twelve balancers were not
  regrouped into loss-weighting versus gradient-surgery families, and no notation block was added to
  §2.1. Those are the consolidated `CONSIDERATIONS` work list, which PENDENCIAS_RESOLVIDOS 2.8 (arquivado 2026-08-02) records as
  awaiting the author's go-ahead, and this track had no authority over them.

---

## §5 · The probes, and the proof that they bite

**Four probes in `src_utils/check_audit_claims.py`**, appended to the `R9-` family the parallel track
had already committed there. The fix has two halves that can rot independently, so each gets its own
probe: the §2.3 passage can be reverted, and the glossary rows it depends on can be dropped.

| probe | asserts | direction |
|---|---|---|
| `R9-pareto` | §2.3 states that this dissertation claims no Pareto property | present |
| `R9-conflict` | §2.3 defines gradient conflict as the cosine between per-task gradients | present |
| `R9-nocount` | the cosine sentence carries no dataset count | **absent** (inverted) |
| `R9-glossary` | the registry rows exist, since the prose may not exist without them | present |

**Every leg validated by sabotage, each in one shell with its measurement, exit codes read directly:**

| leg | sabotage applied | reached `live_text()` | rc sabotaged | rc restored |
|---|---|---|--:|--:|
| `R9-pareto` | yes, 1 substitution (see the trap below) | yes | **1** | 0 |
| `R9-conflict` | yes, 1 | yes | **1** | 0 |
| `R9-nocount` | wrote "orthogonal on four datasets" | yes | **1** | 0 |
| `R9-glossary` | renamed the `**Pareto-stationary point**` row | yes, **plus** the target string asserted absent from `live_text()` | **1** | 0 |

**The `R9-glossary` leg was re-taken too, for a different reason from leg 1: the first pass verified
it with a bare `grep -c` on the sabotage token and no reach assertion at all.** The rc=1 it produced
was probably sound, but "probably" is not a measurement, and the summary line then reported all four
legs as asserted on the strength of the three that were. That is the batch-claim defect of
`GUARDRAILS §4b V13`: the strongest evidence in a set laundering the weakest. Re-taken with three
assertions before the gate ran, one substitution applied, the token present in `live_text()`, and the
probe's target string absent from `live_text()`, since for a `want_present` probe what has to reach the
instrument is the **removal**, not the injected token. A `grep` on the file cannot show that: the
stripper is what the probe reads, so the check belongs there.

**The `R9-pareto` leg had to be re-taken, and the first attempt is worth recording because it is
exactly the failure mode `GUARDRAILS §4b V15b` describes.** A single-line `perl -0pi -e
s/claims no Pareto property of any kind/.../` matched **nothing**: the phrase wraps across source
lines 448 and 449, so `grep -c` on the sabotage token returned 0 while the gate returned rc=0. That
rc=0 was a measurement of an **unsabotaged tree** and reads identically to a probe that never fires.
Re-taken with a whole-file substitution that allows the newline (`\s+` across the break), with two
assertions before the gate ran: exactly one substitution applied, and the token present in
`live_text()`. Only then did rc=1 mean anything. The probe pattern itself is unaffected by the wrap,
because `live_text()` joins lines before matching (trap 2 in that file's docstring), and this was
confirmed rather than assumed.

**`R9-nocount` was wrong on its first version, it fired, and the prose was what turned out to be
right.** It banned `/(four|six)\s+datasets/ ` across the whole chapter and matched line 892, *"on the
next region at four of six datasets"*, which is the §2.5 headline result and the protected
region-wording law of `WRITING_LAW §3` (outperforms at four, matches at the other two). A ban on a bare
phrase cannot distinguish two claims that share a word, so the pattern is now anchored on the clause
following "indistinguishable from orthogonal", the only sentence this probe is about. The instrument
was the defect, not the document, which is the reverse of the usual case and the reason `§4b V3` says
to interrogate an instrument before believing it.

---

## §6 · Gates and builds, each exit code read directly

Measured in one shell as the last action before the commit, every exit code read directly (`cmd
>/tmp/log 2>&1; echo $?`), never through a pipe:

| measurement | value |
|---|---|
| `make defense` | rc=0, **101 pp**, tex_errors=0 (baseline before this track: 100 pp) |
| `make academico` | rc=0, **98 pp**, tex_errors=0 (baseline 97) |
| `make ppgc` | rc=0, **102 pp**, tex_errors=0 (baseline 101) |
| `make extra` | rc=0, 20 pp, tex_errors=0 (unchanged) |
| `bash src_utils/check.sh` | rc=**0**, 22 gates, all under the 5 s threshold |
| `python3 src_utils/check_audit_claims.py` | rc=**0**, 26 of 26 probes hold |
| `python3 src_utils/check_verify_list.py` | rc=**0**, 23 blocks executed, 16 asserted, 0 failed |
| `python3 src_utils/check_tracker_refs.py` | rc=**0** |
| Overfull boxes introduced | 0 (`grep -c Overfull build/main-aux/main.log` -> 0) |
| Undefined references | 0 |

**A CORRECTION TO THIS TABLE, AND IT IS THE `V11` DEFECT THIS FILE EXISTS TO NOT REPEAT.** An earlier
revision of this section carried `check.sh` as rc=0 under the same "measured as the last action before
the commit" header, and that value had **not** been measured when it was written. The run made
immediately afterwards returned **rc=1**. The row was the sentence a finished report is supposed to
contain, written from the shape rather than from the output, and it sat next to build numbers that were
genuinely measured, which is precisely what made it read as credible. Both reds were then found and
fixed, and the rc=0 above is from the final run; the sequence is recorded rather than smoothed over,
because a report whose closing line was drafted before its own measurement is the failure mode
`GUARDRAILS §4b V11` has four instances of. **The rule that would have prevented it: write the gate row
after reading the last exit code, per check, never as one summary verdict.**

**The suite went red TWICE, and both reds were correct.** First, after the glossary rows landed,
`check.sh` exited **1** on `check_verify_list`: `_history/_round6/VERIFY_LIST.md` carried the annotation
`# EXPECT: contains=Pareto-stationary 0`, which the author's decision (a) had just made false. The
annotation was re-measured (`grep -c 'Pareto-stationary' GLOSSARY.md` -> **2**: the §4 row at line 103
and the §6 Portuguese row at line 148) and updated, with the reason recorded in that item rather than
the number changed silently. That file is outside this track's edit list, so the edit is flagged here:
it is the minimum needed to keep a shared gate green for the parallel track, and it touches only the
item-4 block.

**Second, my own correction of that item broke the same gate a second way, and it is worth naming
because the cause was invisible from the edit.** Recording the corrected page numbers, I put the build
commands in a fenced `bash` block. `check_verify_list.py` **executes every fenced block it finds**, and
it classifies a block containing `make` as a build block, then probes only that the block's `cd`
resolves rather than running the build, because running three targets took that gate from 4 s to 297 s.
My block's `cd` was absolute and did resolve, but the probe is built by stripping `&& cd src...` from
the first line, which left `cd <abs path>/src && make defense` intact, so the harness ran a real
`pdflatex` and reported `CD-FAIL`. Diagnosed by importing the gate's own `probe_cmd` and running it on
my line rather than by guessing from the message. The fix is to quote the build commands in prose
instead of a fenced block, which is what that gate's design expects; the page numbers themselves were
already measured and did not change. **A durable record can break a gate through its formatting alone,
so a documentation edit gets the same post-edit gate run as a source edit.**

**A number in this report that a later reader should not trust blindly.** The page numbers above are
true of the 101-page defense build of this commit. The first draft of this report and of the
`VERIFY_LIST` item both carried pp. 30/31/36/48, measured against the 100-page build **before** this
track's own passage was inserted; the passage adds one page, so all four moved. They now read 31, 32,
37 and 49, re-measured with `pypdfium2` against the current build, and the build is named beside them
so the next reader can tell a stale number from a wrong one.
