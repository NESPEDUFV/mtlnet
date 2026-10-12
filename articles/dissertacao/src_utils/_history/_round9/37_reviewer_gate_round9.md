# 37_reviewer_gate_round9.md — the four G2/G3 fact gates, run against build `03b53d16`

Round 9, 2026-07-30. Four fresh-eyes personas in the documented gate-day order (04 concordance, 05
citations, 06 numbers, 07 claims/honesty), each given a 25-minute wall-clock checkpoint and told to
report unfinished work as unfinished. **All four reported unfinished scope**, which is what a bounded
pass is supposed to look like, and **all four overran the checkpoint**, which is not.

### The checkpoint was missed by every persona, and I first wrote that it was met

| persona | wall clock | over the 1,500 s checkpoint by |
|---|--:|--:|
| 05 citations | 1,598 s (26.6 min) | 98 s, 6.5% |
| 04 concordance | 1,618 s (27.0 min) | 118 s, 7.9% |
| 07 claims/honesty | 1,971 s (32.9 min) | 471 s, 31.4% |
| 06 numbers | 2,314 s (38.6 min) | 814 s, **54.3%** |

Mean 31.3 minutes against a 25-minute budget. The first version of this paragraph said "all four came
back inside it". The wall times were in the results I collected, and I did not read them before
writing the sentence — the fifth instance this round of asserting a measurement I already had. The
claim mattered more than most, because the same prompt that set the checkpoint cited the previous
round's overruns (45 min to 60, 90 to 219) as the defect the checkpoint existed to prevent, so
reporting compliance would have retired a control that had just failed.

**What the numbers actually say, now that they are read.** The checkpoint helped and did not hold. The
two prose-heavy gates landed within about 8 percent of budget, which is a different regime from the
last round's 143 percent overrun. The two that blew through it are the two that were told to trace
numbers and citations to external sources of record, and the worst was the numbers gate at 54 percent
over — the one whose scope is bounded by how many numerals a 102-page volume holds, which the prompt
did not narrow. **The instruction to report unfinished work as unfinished did hold, in all four
cases**, and that is the control that produced the useful part of this round: four honest coverage
maps instead of four claims of completeness.

**For the next wave:** the fix is not a longer checkpoint, it is a smaller scope per child. Give the
numbers gate one chapter range rather than a volume, and the citation gate a named entry list rather
than a bibliography.

**Build under review:** commit `03b53d16`; `main.pdf` 102 pp, `main_academico.pdf` 99 pp,
`main_ppgc.pdf` 103 pp, `main_extra.pdf` 20 pp. `make check` rc=0, `make selftest` rc=0, read directly.

| gate | persona | blockers | should-fix | nits | report |
|---|---|--:|--:|--:|---|
| G3 + L3/L4 | 04 concordance | 0 | 5 | 4 | `reviews/04_concordance.md` |
| G2 R1-R5 | 05 citations | 0 | 4 | 5 | `reviews/05_citation.md` |
| G2 N1-N5 | 06 numbers | **1** | 3 | 0 | `reviews/06_number.md` |
| G2 C1-C4 | 07 claims/honesty | **2** | 3 | 2 | `reviews/07_claim_honesty.md` |

## The three blockers, each re-verified by me in the source before being written down

A persona's self-report is not evidence (`AGENT_GUARDRAILS` L6). Every blocker below was opened and
confirmed independently; the check is named so the author can repeat it.

### B-1 · Appendix F claims hard sharing "costs nothing", and calls the wrong topology hard sharing
- **Where:** `chapters/apx_f_cosine.tex`:290, rendering at `main.pdf` p. 101.
- **Verbatim:** "That is why hard sharing costs nothing in this architecture, and why
  Chapter~\ref{ch:mobiwac} finds no balancer improving on a fixed loss weighting".
- **Confirmed, two independent defects in one clause.** First, the cost claim is unbounded and the
  document refutes it: `5_mobiwac/06_results.tex`:145-146 records the region gain running "from
  $-0.41$ at the smallest count to $+2.20$ at the largest", i.e. a **negative** cell. Second, the
  architecture it names is not hard sharing on this document's own definition:
  `5_mobiwac/01_introduction.tex` describes "a shared trunk (a cross-attention stack where the two
  tasks exchange semantic context) and a private spatial path for the region task".
- **Author's call.** The licensed statement is about the mechanism, not the cost, and the chapter
  already has one ("sharing stopped hurting").

### B-2 · The consolidated answer uses bare "everywhere" and collapses the region partition
- **Where:** `chapters/6_conclusion.tex`:106, rendering at `main.pdf` p. 79.
- **Verbatim:** "outperforms the dedicated models on the category task everywhere and outperforms or
  matches them on the region task."
- **Confirmed against the law, which is unusually explicit here.** `WRITING_LAW.md`:83 reads: the
  region-count scaling claim is scoped to the five U.S. states; **bare "everywhere" never**. Line 75
  separately bans "outperforms region everywhere". And "outperforms or matches" discards the
  four-of-six / TOST partition that the protected wording requires and that the same chapter states
  correctly on the preceding page.
- **Author's call.** This is the single most-quoted sentence in the dissertation.

### B-3 · Two size-span factors derived in prose, with no ledger and no script
- **Where:** `chapters/apx_f_cosine.tex`:317-319, rendering at `main.pdf` p. 101.
- **Verbatim:** "this axis spans a factor of thirty-six in volume and one of sixteen in the size of
  the region label set".
- **Confirmed, and the numbers are RIGHT:** 4,089,892 / 113,846 = 35.92 and 8,501 / 520 = 16.35, and
  the four endpoints are themselves clean in `datasets.tex`. The finding is not an arithmetic error.
  It is that both factors are **computed in prose**, which `AGENT_GUARDRAILS` N2/N3 forbid — quote,
  never compute — so nothing regenerates or re-checks them when a dataset changes.
- **Cheapest fix:** state the four endpoint counts, which are already traceable, and drop the ratios;
  or add them to the appendix's ledger with the command that produces them.

## What the gates verified as INTACT, which matters as much as the findings

The honesty gate's inventory is the load-bearing one: **zero** BRACIS mentions in any of the four
volumes; **zero** instances of "beats", "wins", or a Pareto-dominance claim; the Arizona result never
upgraded from a match to a gain ("a match, not a gain", p. 73); the Alabama deficit stated plainly
rather than buried; MobiWac described as "submitted, under review" at **all five** status sites with
no "accepted" anywhere; the three time-capsule prefaces present; the Pareto non-claim sentence
present; the cosine result traveling with its full four-state scope; and the Resumo/Abstract pair
claim-for-claim parallel across both languages. The concordance gate found the cross-reference graph
clean (113 labels, 269 references, no duplicates, no dangling, no `??` in the rendered PDF) and found
the protected region wording, the 5.3-9.4 category range, and the n=20 arithmetic concordant at every
site it checked. The citation gate resolved 26 entries against Crossref/arXiv/DataCite/OpenAlex and
found **no fabricated or unresolvable reference**, no duplicate keys for one work, and a rendered
reference list numbered 1-99 with no gaps.

## A finding that corrected ME, not the document

The citation gate went looking for the two GNN references Germano asked for and reported that neither
`bruna2014spectral` nor `scarselli2009gnn` exists in `references.bib` or is cited anywhere. **That is
correct and it is the intended state**: both were verified this session but GER-01 is in Wave B,
behind another agent's open edit of Chapter 2, so nothing was inserted. Worth recording because a
reader of my source ledger could mistake "verified" for "in the document".

More usefully, the same gate found that the repository had **already verified `wang2025hamtl`** —
`references.bib`:1148-1152 carries a provenance block recording a read of the Springer article page on
2026-07-06 and its finding that HAMTL's location target is venue-level. I had written that paper up as
content-unknown because *this session* could not open it. The correction is in
`36_source_ledger.md` and in FAB-28's block: the item stays blocked, but the question the author
actually cares about is probably already answered, on the repo's own record.

## Unfinished, reported by the gates themselves

None of the four covered its whole scope, and each said so. The largest gaps, in the order I would
close them:

1. **Chapters 3 and 4 were not audited for numbers at all** (roughly 40 percent of the volume's
   numeral tokens). The numbers gate routed them to the published papers' tables and did not open
   them.
2. **Chapter 2 §2.3's new Pareto material was not citation-audited.** The attributions at
   `2_fundamentals.tex`:431-448 (`sener2018mgda`, `nash`, `liu2021cagrad`, `senushkin2023aligned`,
   `yu2020pcgrad`) are the highest-value target for the next pass — new prose, five attributions, and
   the honesty gate already flagged one clause there as possibly the writer's gloss rather than the
   source's claim.
3. **73 of 99 bibliography entries unchecked at attribute level**; claim-support sampling reached 4
   sites against the 20 percent floor R3 asks for.
4. **Only `main.pdf` was read by three of the four gates.** The other three volumes were swept, not
   read.

## The six style/readability personas did not run

Gate-day order puts 03 style, 01 cold reader, 15 readability, 16 AI credibility, 18 visual and 19
LaTeX source after the fact gates. They are **not run** in this round. Two of the three blockers are
prose-level claims the author must settle first, and running a style pass over sentences that are
about to change would produce a report stale on arrival — which is the defect this round was told to
avoid.
