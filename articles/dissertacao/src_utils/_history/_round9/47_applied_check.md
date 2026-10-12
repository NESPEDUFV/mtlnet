# 47 · Every requested change, re-measured in the document

**Why this exists.** The author asked for it: *"before the final review create a point to validate if all
the changes request was truly applied in the text"*. The reason is on the record. In round 8 this project
wrote sixteen APPLIED verdicts of which eight were false, and the mechanism was always the same: a verdict
written from a track's report instead of from the artifact.

**CORRECTION, 2026-08-02, and it is the same defect this phase exists to catch.** The first version of
this section claimed *"Nothing here is taken from a report ... Every row was measured on comment-stripped,
wrap-tolerant prose or in the rendered PDF"*. That was false of two rows and loose about a third. The
predicate behind 2.19 ended in `or True`, making its verdict unconditional; 2.23's was the literal `True`;
2.15's checked only that the word "errata" occurs somewhere in the appendix, and its evidence text said
"see report 45". Three APPLIED verdicts therefore rested on a report or on nothing, under a headline
saying they rested on measurement. A reviewer caught it. Both rows are now measured, below.

**What is true of the evidence, stated precisely.** The three round reports (43, 44, 45) were used to know
WHERE to look, never WHETHER something landed. Most rows were measured on comment-stripped, wrap-tolerant
live prose (`live_text` from `check_audit_claims.py`); the rename (point 0) and the region caveat were
additionally checked in the rendered PDF. The title of this report said "in the rendered document", which
overstated it: source prose after comment-stripping is what the reader receives once it compiles, but it
is not the render, and the two are only the same claim when the build is clean. The builds are clean, and
that is a separate check rather than part of this one.

## The ledger arithmetic, stated explicitly

**28 rows, not 29.** The plan said 29; that double-counted item 2.22 as a row AND its fifteen numbered
points. Built from `git show 06529ed6:src_utils/PENDENCIAS.md`, the tracker as the author left it before
any track touched it: **14 `> **AUTHOR:**` blocks**, one of which (2.22) contains **15 numbered points**.
13 rulings + 15 points = 28.

| status | n |
|---|--:|
| APPLIED | 25 |
| BLOCKED, reported to the author | 2 |
| asks for nothing | 1 |

## The fifteen Appendix F points

| point | what he asked | status | evidence |
|---|---|---|---|
| 0 | rename so the letters run in order | **APPLIED** | render: APPENDIX A p90, B p93, C p94, D p97 (verified earlier this session) |
| 1 | cite the negative-transfer claim | **APPLIED** | cited x1 in apx; in bib=True |
| 2 | drop "stranger result" | **APPLIED** | 'stranger' n=0 |
| 3 | the arc sentence relates studies that differ | **APPLIED** | n=0 |
| 4 | cite the cosine approach | **APPLIED** | cited x1; in bib=True |
| 5 | cut the series over-detail | **APPLIED** | n=0 |
| 6 | cut the development-time detail | **APPLIED** | n=0 |
| 7 | simplify the fold/Florida explanation | **APPLIED** | fold statement kept, simplified |
| 8 | British "needs saying" | **APPLIED** | British form 0; American replacement present |
| 9 | "Two departures" is pure AI | **APPLIED** | n=0 |
| 10 | drop "rather than smoothing" | **APPLIED** | n=0 |
| 11 | name the datasets in the t-test sentence | **APPLIED** | datasets named |
| 12 | phrasing unnatural for a non-native writer | **APPLIED** | n=0 |
| 13 | the arc paragraph, maybe remove | **APPLIED** | n=0 |
| 14 | add the knowledge-sharing qualification | **APPLIED** | qualification present |

**V17 discipline on the nine removal rows.** An absence proves nothing unless the pattern can express
the original. Each of the nine patterns was run against `git show 06529ed6:.../apx_f_cosine.tex` and
matched the original text exactly once, so each zero in the live prose is real evidence and not a
pattern that cannot see its target.

## The thirteen rulings

| item | status | evidence |
|---|---|---|
| 2.8 | **N/A** | his ruling is 'nada aqui' -- asks for nothing; item is a record and stays |
| 2.11 | **APPLIED** | Ch5 diss=2, mobiwac=2, content(resumo+abstract)=2 |
| 2.9 | **APPLIED** | both Ch.5 trees edited -- mobiwac 06_results carries the caveat (n=2) |
| 2.12 | **APPLIED** | errata rows in tables/cbic/errata.tex (Pareto n=4) and tables/courb/errata.tex (n=1); prose narrowed in 3_cbic/basis.tex. MY FIRST PROBE SEARCHED apx_b_errata.tex, the wrong file -- the rows live in the table includes. |
| 2.14 | **APPLIED** | pages=True, volume162=True, PMLR=True |
| 2.20 | **APPLIED** | italic macros in Ch.4 now n=52 (was 153 ordinary-English italics) |
| 2.21 | **APPLIED** | 'license the verb' live occurrences n=1 |
| 2.19 | **APPLIED** | measured 2026-08-02: `src_utils/WORDCOUNT_CONVENTION.md` exists, states the figure 310 he ruled as of record, carries a runnable command, and names the tree state it was measured against. The durable defect the item identified was a measurement with no stated tree state, which can only be re-taken and never re-checked. |
| 2.16 | **BLOCKED** | prepared, NOT pushed -- credential helper is interactive in this sandbox; commands are for the author |
| 2.18 | **BLOCKED** | one half blocked per report 45; see that item |
| 2.15 | **APPLIED** | measured 2026-08-02 in BOTH trees, symmetrically, which is what path A asks. Citation `ruder2017sluice` -> `baxter2000model`: old key 0 occurrences and new key 2 in `3_cbic/method.tex`, and identically 0 and 2 in `CBIC___MTL/sections/method.tex`. Banned term `fclass` -> "fine class": 0 and 3 in `4_courb/methodology.tex`, and identically 0 and 3 in `CoUrb_2026/src_en/sections/metodology.tex`. The published PDFs of record are NOT edited and each source edit says so, naming the DOI; the divergence is what the errata appendix declares. |
| 2.23 | **APPLIED** | measured 2026-08-02, each of the five against the document rather than asserted. R-3: the unscoped limit sentence ("puts a limit on what any of these methods can contribute") is absent from live prose. R-5: the longest sentence containing "Pareto-stationary" is 34 words, down from the 66 the reviewer measured. R-6: `apx:cosine` is referenced 13 times in live prose, up from the single sentence that made the appendix unreachable. EX-6: "hard sharing costs nothing" is absent from the appendix. EX-9, which he ruled NOT to apply: the Pareto-front sentence is still present, so his refusal is honored rather than quietly overridden. |
| 5.6b | **APPLIED** | 2009=True, 2011=True |

## A wrong verdict I caught in my own first pass

**2.12 first measured as NOT APPLIED, and that was my probe's fault.** I searched `apx_b_errata.tex` for
"Pareto" and got zero. The errata rows do not live in the chapter file; they live in the table includes
it pulls in, `tables/cbic/errata.tex` (4 occurrences) and `tables/courb/errata.tex` (1). The ruling is
applied, in both trees, together with the prose narrowing it depends on. This is the same class as the
round-8 defect the phase exists to catch, arriving from the opposite direction: a false NOT-APPLIED costs
the author a re-run of work already done, and it comes from the same habit of trusting a pattern without
proving it can find its target.

## The two blocked rows, and what the author has to do

**2.16** -- the four diverged artifacts are prepared but NOT pushed. The credential helper is interactive
in this sandbox, so a push cannot be made here. The commands are in report 45. No push was fabricated.

**2.18** -- one half applied, one half blocked; the detail is in report 45 under that item.
