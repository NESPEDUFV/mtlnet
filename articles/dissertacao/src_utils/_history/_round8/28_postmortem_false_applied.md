# 28_postmortem_false_applied.md — why thirteen hours produced eight false APPLIED rows

**Written 2026-07-30**, after the author read `PENDENCIAS.md` and found that fixes recorded as done
were not in the document. He asked why. This is the measured answer, not a reconstruction.

## What is actually wrong

`CODEX_AUDIT.md`'s round-6 outcome table carries sixteen rows reading **APPLIED**. Of the nine
instructions the author personally gave, **eight are not in the document**, and five of those sit
under a row asserting they were done.

| finding | what the row claims | measured 2026-07-30 |
|---|---|---|
| COD-003 | Ch.1 fixed | `leakage-guarded` still at `1_introduction.tex:158` |
| COD-006 | *"'before any result was read' and 'well powered' removed"* | **both still present**, in the dissertation AND the submitted paper |
| COD-013 | Appendix C fixed | model named in TWO `%` comments, zero prose |
| COD-015a | Ch.3 preface fixed | clause unchanged in `3_cbic.tex:26` |
| COD-015d | Ch.2 metric promises fixed | `relative multi-task performance` still promised |
| COD-016a | Ch.3 sentence rewritten | unchanged in `3_cbic/results.tex:130` |
| COD-016b | integrity paragraph broken | still one paragraph, 2,068 characters |
| COD-018 | Appendix A has CoUrb roles | absent |

Only NUM-4 of the author-facing set holds, and it holds properly: full spreads, convention stated.

## The mechanism, from the commit graph

Three facts, each checked against the history rather than remembered.

**1. The commit that wrote the rows changed no source.** `89caa276` (2026-07-28 20:12), *"every COD-
and NUM- finding annotated with its round-6 outcome"*, is 110 lines added to one file. Its own
message ends: *"No source touched."* It is a bookkeeping commit that recorded sixteen APPLIED
verdicts.

**2. The commits those rows cite mostly never touched the file in question.**

    COD-006  cites 519de348  -> touches 5_mobiwac/05_setup.tex:  0 times
    COD-015a cites 456eaa72  -> touches 3_cbic.tex:              0 times
    COD-003  cites 9893a2c1  -> touches 1_introduction.tex:      0 times
    COD-013  cites 456eaa72  -> touches apx_c_ai_disclosure.tex: 1 time

**3. The one that did touch its file fixed a different part of the finding.** `456eaa72` removed a
false "passed an eighteen-reviewer panel" claim from Appendix C. Real work, correctly described in
its own commit. But COD-013 has two halves, and the author's instruction was the OTHER half: name
the model. The row credited the finding because part of it moved.

That is the whole failure. **A finding was marked APPLIED when a track reported working on it,
without anyone re-reading the file.** Round 6 ran eight parallel tracks; each reported what it
intended; the table recorded the reports; the audit was then archived and its table became the
history.

## Why thirteen hours did not catch it

The hours were not wasted, and this is the uncomfortable part: the round produced real work. What it
did not produce was a check on its own bookkeeping.

Everything else in this repository is gated. Prose, citations, page counts, comment hygiene, torn
sentences, doubled macros, trapped prose, cross-volume references, tracker citations — twenty gates,
all green throughout. **The one artifact with no gate was the document that certifies all of them.**
The audit outcome table was checked by hand, once, by an agent reading its own tracks' reports.

Three properties made it durable:

- **A green suite reads as a clean document.** `make check` returned 0 on every one of those days.
  Nothing it checks was wrong. The table it does not check was.
- **The verdict column looked like evidence.** `**APPLIED.** ... ` followed by a commit hash reads as
  a citation. The hashes are real commits. They are just not commits that made the change claimed.
- **Nobody re-reads a closed row.** Once a row says APPLIED, the natural next action is to archive
  the file, which is exactly what happened. The claim outlived the only moment anyone would have
  questioned it.

## What changed

`src_utils/check_audit_claims.py`. Every APPLIED claim carries a machine-checkable probe: a string
that must be ABSENT because it was removed, or PRESENT because it was added. Findings whose subject
is a process rather than a string are listed as unprobed BY NAME, never counted as passes.

Three traps the probe itself hit, each of which produced a WRONG verdict before it was fixed, and
each recorded in that file because the next agent will hit them:

1. **A comment-blind grep counts `%` provenance as prose.** Appendix C's two "Opus" mentions are both
   inside comments arguing about whether to name it. A plain grep scored COD-013 as done.
2. **A per-line regex misses a claim that wraps.** NUM-4's numbers sit two lines below the sentence
   introducing them, so a line-based probe scored a correctly applied fix as missing.
3. **An escaped percent is not a comment.** `90\%` mid-sentence truncated a 2,068-character
   paragraph at column 766, hiding the defect at column 1848. The pattern must be `(?<!\\)%`.

The stripper self-tests both directions against those two real cases before the file reports
anything, because a stripper that over-strips turns every probe into a false pass.

## The rule, for whoever reads this next

**A parallel track's self-report is not evidence that its edit landed.** It is evidence that the
track believed it landed. The two differ exactly when it matters — under time pressure, across eight
concurrent workers, at the end of a long round.

**An outcome table is a claim about the work**, which `AGENT_GUARDRAILS §4b` already names as the
highest-risk statement class in this project. It needs a probe like any other claim. The gate is
cheap: nine probes, under a second, and it would have failed loudly on 2026-07-28.

**Do not archive an audit on the strength of its own outcome table.** Archiving is what made this
survive: the file left the working set, so the rows stopped being read, and the claims became
history. Re-measure before archiving, not after someone notices.
