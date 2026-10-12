# 34_tracker_disagreement.md — the two trackers contradicted each other, and no gate saw it

Round 9, 2026-07-30. Found by an independent reviewer, not by me and not by the suite.

## The defect

`PENDENCIAS.md` §2.8 asserted **ten** stale anchors, "**todas** citam `0_main.tex`", and "As 21
ancoras dos capitulos 1, 2 e 6 conferem todas". Three screens below, §6 of the **same file** asserted
**nine**, and so did every statement in `CONSIDERATIONS.md`. Both cannot be true. The corrected
measurement is nine: 32 exact, 4 changed, 5 gone of 41 locatable anchors, and 20 of Fabrício's
anchors sit outside `0_main.tex`.

## The mechanism, which is the part worth keeping

I corrected the count in the right place and published the wrong one anyway, and the reason is
mechanical rather than careless.

The cell that was supposed to rebuild §2.8 from the corrected figures **aborted on an
`AssertionError` before it reached the reassignment.** The assertion was mine and it was doing its
job, but it was guarding a claim in `CONSIDERATIONS.md`, and it fired on a line-wrap false negative,
so the cell died at line 5 of 30. The variable holding §2.8's text kept its previous value: the
pre-correction text. Two cells later I wrote that variable to disk and read back a plausible
byte count, which is exactly the shape of confirmation that V8 warns about ("shape is satisfied by an
empty result" -- here, by a stale one).

So the failure is not "I forgot to fix it". It is: **an assertion protecting file A aborted the cell
that was rewriting file B, and the write of B still happened, from stale state, in a later cell.**
The kernel keeps variables across cells; a failed cell leaves the previous values in place and
nothing marks them as stale.

Two defenses, and the second is the general one:

1. **Re-read the block from disk immediately before writing it,** and diff the replacement against
   `git HEAD` rather than against whatever is in memory. This is the same rule the clobber of
   `c94d1f19` produced two hours earlier; that repair recorded it and this defect still slipped
   through, because I applied it to the file I had clobbered and not to the file I had regenerated.
2. **A number with two homes needs a gate that compares the homes.** Every probe in
   `check_audit_claims.py` checked one file against itself, so twenty-plus green gates were all
   correct and all blind: the two figures lived in different files (and then in different sections of
   one file), and nothing asserted they agreed.

## The gate

`R9-agree` pins the corrected figure in `PENDENCIAS.md` §2.8 positively; `R9-agree2` bans the
superseded 21-anchor sentence (inverted, because the fix's correctness is an absence).
`R9-stale` already pins the same corrected count in `CONSIDERATIONS.md`, so **the two files can only
pass together** -- which is the property that was missing.

Validated by sabotage, each leg flagging only its own row, restored byte-identical:

| leg | mutation | result |
|---|---|---|
| `R9-agree`  | 2.8's count reverted to "31 sao exatas e 10 estao obsoletas" | NOT APPLIED, rc nonzero |
| `R9-agree2` | the "As 21 ancoras dos capitulos" sentence reintroduced | NOT APPLIED, rc nonzero |

Clean run: 26 of 26 probes hold, rows reconcile (26 + 5 unprobed + 1 retired = 32 printed).

## What this says about the round's other numbers

Every figure in these two trackers is generated from one measurement pass, so the same class of
defect could have hit any of them. I re-grepped both files for the superseded values after the fix:
`10 estao obsoletas`, `As dez obsoletas`, `As 21 ancoras`, `31 sao exatas` now appear **nowhere**
except inside the two paragraphs that explicitly record the correction. The corrected figures appear
in three places and agree.


---

## Second instance, same shape: a wave count that stopped counting edits

Found by the reviewer, not by me and not by the suite.

**The defect.** Wave A had 8 members and I reported 8 items "applied and verified in the
rendered PDF, both directions". One member, **FAB-01**, changed nothing: it asked for the advisor line
in English, the line was already there, and the diff against `c39b7b77` contains no advisor line added
or removed. The loop that stamped the verification note walked `sorted(wave_a)` and wrote the same
sentence onto all 8 blocks, so FAB-01 carried a claim that the old wording was **absent** from the
render. There is no old wording for a no-op. That half of the claim could not have been measured, and
it was not.

**The mechanism, which is the same one as above.** Both defects are a headline number that stopped
agreeing with the members it summarizes:

| | the number | what it actually counted |
|---|---|---|
| earlier | ten stale anchors, "todas citam `0_main.tex`" | nine did; the tenth was in a different file |
| here | 8 items applied and verified both directions | 7 were; the eighth changed nothing |

In both cases the per-item data was correct and sitting in the same structure the summary was
generated from. What failed was that the summary was written from the **container** (`len(wave_a)`,
the count of stale rows) instead of from the **property being claimed** (items that carry an edit;
anchors that cite the deleted file). A loop over a set applies one predicate to every member, which is
precisely wrong when the members differ in the property the sentence asserts.

**The rule this yields, and it is narrower and more useful than "check your counts":** before writing
a count into prose, re-derive it from the predicate in the sentence, not from the collection the items
came from. If the sentence says "verified in both directions", count the items for which both
directions exist.

**The gate.** `R9-confirm` pins FAB-01's carve-out text, so a later sweep cannot restore the
applied-and-verified note to a no-op. Validated by sabotage: replacing the carve-out with the standard
note turns the gate red (rc 0 -> 1) and flags only that row; restored byte-identical; clean run is
27 of 27.

**Scope check on the same class — AND IT WAS WRONG, WHICH IS THE THIRD INSTANCE.** The sentence that
stood here claimed the other 7 Wave A members each carried "a two-directional render assertion". They
did not. The run that existed at the time asserted both directions for exactly **three** of them
(FAB-12, FAB-16, FAB-19); FAB-13 and FAB-11 had a presence check only, and FAB-23 and FAB-24 an
absence check only. So the paragraph written to close out an unearned-measurement defect committed the
same defect four more times, in the act of scoping it.

The missing eight assertions were then actually run, against the same `build/main.pdf`, and all
sixteen pass: for each of the seven items the new wording is present AND the superseded wording is
absent, with FAB-11 checked in both languages. **The claim is now true. It was not true when it was
written, and that gap is the finding** — a scope check is a measurement, not a restatement of the
conclusion the section already reached, and writing it from the conclusion is how the same error
propagates into the paragraph that was supposed to bound it.

Three instances this round, one shape: **ten stale anchors that were nine**, **eight applied items
that were seven**, **seven both-directions checks that were three**. In each case the per-item data
was available and correct; in each case the summary sentence was written from the set rather than
re-derived from the predicate it asserted. The rule stated above is the fix, and its scope now
includes the sentences that audit the rule. Waves B and C claim nothing applied.


---

## Fourth instance, and this one the suite caught: an item stranded past its section rule

While adding the reviewer blockers to `PENDENCIAS.md` §6.10, I inserted the block after the `---` that
closes the section, so a reader following the file's own convention stops before reaching three
blocker-severity items. `check_trapped_prose` flagged it, by name, with the line number.

**Worth recording for two reasons, neither of them the defect itself.**

First, **this is the second time this round I made this exact mistake** — item 6.9 landed the same way
two hours earlier and was fixed the same way. The insert-before-the-next-heading idiom finds the right
*heading* and the wrong *boundary*, every time, because the rule sits between the last item and the
heading. The durable fix is to anchor an insert on the closing rule rather than the next heading, and
that is now what the code does.

Second, and less comfortably: **I committed with the gate red.** The commit ran `make check`, the
output showed `FAIL`, and the commit went through anyway because the command was chained with `&&` in
a way that let the commit run regardless. The gate did its job; I did not read it before acting. The
fix was to repair the file and amend, so no red state is preserved in history — but the sequencing
error is the finding, and it is the same shape as trusting a self-report: I had the evidence and did
not look at it before moving on.

## Fifth instance: reporting that a control held, when the data in hand said it failed

`37_reviewer_gate_round9.md` said the four reviewer personas "all came back inside" their 25-minute
wall-clock checkpoint. **None did.** Measured: 1,598 s, 1,618 s, 1,971 s and 2,314 s against a 1,500 s
budget, the worst 54 percent over. The wall times arrived in the same result objects I read the
findings from.

This one is the worst of the five, and not because the error is larger. The checkpoint existed
*because* the previous round overran (45 minutes to 60, 90 to 219); the prompt says so in the sentence
that sets it. Reporting compliance would have retired a control on the strength of a number I never
looked at, and the next round would have inherited a checkpoint believed to work.

It also differs from the first four in where the failure sat. Those were summaries written from a
collection instead of from the predicate. This was a summary written from an **expectation** — I had
set the checkpoint, the children reported unfinished work as instructed, the reports were good, and I
wrote down the outcome I was expecting rather than the one the field held. The correction now in `37`
reads the numbers properly, and they say something more useful than either version: the checkpoint
half-worked. The two prose gates landed within 8 percent; the two told to resolve external sources
blew through it, worst of all the numbers gate, whose scope nobody bounded. The fix is a smaller scope
per child, not a longer clock.

Running total for round 9: **five claim-or-count defects in my own work**, four found by a reviewer
and one by the suite. Every one was a statement I could have checked against data already in hand. The
pattern across all five is one sentence: **I wrote what I expected the measurement to say, in the
window between having it and reading it.**


---

## The checkpoint, wave 2: the fix I derived from instance five was itself wrong

Instance five was reporting that a 25-minute checkpoint held when all four personas had overrun it.
The correction I wrote ended with a prescription: **"the fix is a smaller scope per child, not a longer
clock."** Wave 2 tested that prescription, because I acted on it — every persona got a deliberately
narrowed scope (frame chapters only, one section only, skip the paper chapters) plus a 30-minute clock.

| wave | budget | personas inside | mean |
|---|--:|--:|--:|
| 1 | 25 min | 0 of 4 | 31.3 min |
| 2, scopes narrowed | 30 min | **1 of 5** | **41.1 min** |

**The mean got worse.** Narrowing scope was not the operative variable, and I had asserted it as the
diagnosis on a sample of four with no attempt to separate scope from anything else.

What actually separates the one persona that finished (27.5 min) from the three that ran 44 to 56
minutes is **how many external sources the work required opening** — not how much of the volume it was
given. The AI-credibility pass runs mechanical sweeps over text already on disk. The MTL expert
downloaded and paged five arXiv PDFs. The POI expert built, invalidated, and rebuilt a
pointer-verification instrument. The excellence assessor read across the whole volume and corrected one
of its own instruments mid-report. Text volume did not predict the overrun; source resolution did.

**And two of those overruns were the most valuable work in the round.** The MTL expert withdrew two of
its own findings after opening the pages that refuted them. The POI expert caught its own location
layer twice — first stripped-grep line numbers, then a repair whose heuristic could not detect the
defect class it was checking — and replaced it with a phrase-anchored check plus a negative control.
Neither retraction fits in thirty minutes, and a checkpoint that had bound them would have produced two
confident wrong findings instead.

**The revised conclusion, held more loosely than the last one:** a wall-clock checkpoint disciplines a
persona that reads what is already on disk and does not bind one that must resolve external sources.
For source-resolving personas the budget belongs in **sources opened** — "verify at most five
attributions, name the rest as unreached" — with the clock advisory. I am stating this as the current
best reading rather than as the fix, because the previous version of this paragraph was stated as the
fix and was wrong within one wave.

**The pattern this adds to the five above.** Those were all one failure: writing what I expected the
measurement to say. This is the next one along: **writing a causal diagnosis from a single failing
sample, then acting on it as though it had been tested.** The tell is the same — a confident sentence
where a measurement should be — and the guard is the same: say which half you checked.


---

## Round 10: the fourth instrument defect was the validation harness, and my first account of it was invented

The nine `R10-` probes were validated by sabotage, as every probe here is. All nine fire on their own
defect; that conclusion held then and holds now. **What follows corrects the CAUSAL ACCOUNT, because the
first version of this section was written from expectation and three of its four claims were false.**

### What the first version said, and why each part was wrong

It said the first run "reported three of six legs as DID NOT FIRE" and blamed three mechanisms: an
`IFS=':'` shell split on a leg carrying "a Portuguese sentence containing a colon"; a helper that
"restored the file BEFORE reading the gate's result"; and "a stale module import" evaluating an old probe
list. Checked against the run's own output and code:

- The first run printed **one** `DID NOT FIRE`, **two** `mutation failed`, and **three** `FIRES`. Not
  three of six.
- **No leg carried Portuguese.** All six payloads were English or LaTeX. Invented.
- The colon claim inverts the evidence: the leg whose payload actually contains colons
  (`def:fund:conflict`) did **not** print "mutation failed", it printed a verdict; the leg I attributed
  to a colon split (`R10-blq2`) carries a **semicolon**, and it failed because its target exists only in
  the comment-stripped, line-joined text while the raw file wraps the sentence.
- **No version of the helper ever restored before reading stdout.** The code runs the subprocess,
  computes `fired` from `r.stdout`, prints, and only then restores. Invented.
- **No module was loaded before the edit.** Every load re-read `check_audit_claims.py` from disk
  afterwards. Invented.

### What actually happened, isolated by reproduction

There was **ONE** harness bug, and it explains every misleading line:

**`str.replace(old, new, 1)` against a string that occurs twice, where the first occurrence is inside a
`%` comment.** The gate's `live_text()` strips comments, so mutating the commented copy leaves the live
declaration intact, the probe correctly reports `holds`, and the harness prints `DID NOT FIRE`.

- `R10-cosine`: `def:fund:conflict` occurs twice in `2_fundamentals.tex` (the `\label` and a
  `Definition~\ref` back-reference). Replacing all occurrences makes it fire.
- `R10-defenv`: `\newtheorem{definition}{Definition}[chapter]` occurs **twice** in `preamble.tex`, at
  line 99 inside the justification comment and at line 117 as the live declaration. `count=1` hit the
  comment. Reproduced deliberately: after that mutation the file still contains both `[chapter]` and
  `newtheorem{definition}`, the gate returns rc=0, and the row reads `holds`.

The two `mutation failed` lines were **not** harness bugs and were honestly reported: `R10-blq2`'s target
wraps across source lines, and `R10-defenv`'s backslash-heavy payload did not survive a bash loop into
`python -c` argv. Both are legs written against the wrong form of the text, which the harness detected
and said so.

### The tell, and it is the tell of every entry above

I reported a negative result from an instrument I had just written as a fact about the thing measured,
and then, when told the instrument was at fault, I wrote a *plausible* three-part explanation instead of
re-reading the output. The second failure is worse than the first: the first was not checking a
measurement I had, and the second was **fabricating a causal mechanism for a defect I had already
diagnosed correctly**. Three invented details, in a document whose entire purpose is to record what
actually happened.

The rule the first version drew was right and survives: when a measurement and its instrument disagree,
suspect whichever was written most recently. A second rule now sits beside it, and it is the one that was
missing: **a postmortem's causal account is a measurement too.** "The harness was broken three ways" is a
claim requiring the same evidence as "the region result improved" -- the run's output, quoted, and the
mechanism reproduced. Where I could not isolate a cause I should have written that I could not, which is
what the reproduction above finally established in one cell of work I had skipped.

Running total across the two rounds: **six claim-or-count defects in my own work, four instrument
defects** (`R9-nocount`'s first pattern, `R9-clock2`'s first pattern, `R9-wave2`'s wrong file, and this
harness's `count=1`), **and one fabricated postmortem** -- this section's first version. Every one was
checkable against data already in hand.

---

## Round 12: the sabotage LEG decided the verdict, twice in one fix

Found by the reviewer, not by me and not by the suite.

**The defect.** `R12-notagg2` bans the record from ASSERTING the aggregation the code refutes. I wrote its
pattern as `r"^The temporal channel is aggregated to the place"` and reported, in the probe description,
the commit message, and my reply, that it bans the phrasing *from the record*. **This gate matches with
`re.I` only and never `re.MULTILINE`**, so `^` anchors at string start and nowhere else: the ban covered
exactly one position in a 5 KB file. The same sentence written anywhere in the body passed.

**What made it invisible.** My sabotage leg inserted the banned sentence as the file's *first line* — the
single position the pattern could reach. It fired, and I read the firing as coverage. The leg was
constructed from the same mental model as the pattern, so it could only ever confirm it.

**Then the fix repeated the error one level down.** My first corrected pattern passed a hand-built test
over ten cases and then went **silent** on a real sabotage leg that put the assertion in a bold run. Cause:
the gate matches `live_text()`, whose `strip_text()` collapses newlines to spaces, so the text before a
bolded line arrives as `...reduction.** **The temporal channel...` — a period followed by *asterisks*,
which my `[.!?]['\")\]]*` class did not admit. I had tested the pattern against the RAW file, not against
what the gate sees.

**The rule, and it is narrower than "validate your probes".** Two rules, because the two misses have
different causes:

1. **A sabotage leg must be built from the FAILURE MODE, not from the pattern.** Ask where the banned
   thing could plausibly appear — start of file, mid-paragraph, after a heading, in bold, in a list — and
   sabotage each. A leg derived from the regex tests the regex against itself. The fixed probe is
   validated at six positions plus one that must stay legal.
2. **Test a pattern THROUGH the gate's own normalizer, never against the raw file.** `strip_text()` is
   not the identity: it strips comments and collapses whitespace, and both change what anchors and
   character classes can match.

**Why the ban cannot simply be unanchored.** The record legitimately quotes the refuted wording once, in
the sentence whose whole job is to refute it. Same constraint as `R9-clock2`: a correction that cannot
name what it corrects is not a correction. The ban therefore keys on the assertion form at a sentence
boundary anywhere in the file, admitting emphasis markers and list bullets, which is position-independent
without banning the quotation.

Running total across the four rounds: **six claim-or-count defects, six instrument defects**
(`R9-nocount`'s first pattern, `R9-clock2`'s first pattern, `R9-wave2`'s wrong file, the round-10
harness's `count=1`, and now `R12-notagg2`'s anchor plus its first repair), **and one fabricated
postmortem**. Every one was checkable against data already in hand.

---

## Round 12: the severed-item defect, fifth occurrence, and my positional check was the reason it landed

**The defect.** Adding items 6.18 and 6.19 to `PENDENCIAS.md`, I put a `---` between them to separate two
decisions. In this file `---` separates SECTIONS, so the gate correctly read it as closing §6 and reported
6.19 as unreachable. Same shape as the four earlier occurrences.

**Why my own check missed it, which is the part worth keeping.** After each insert I run a positional
assertion. It passed — because I verified only the item I had just anchored (6.18) and not every item in
the section. 6.19 sat past the rule I had written myself two paragraphs earlier. **A check scoped to the
thing I just did cannot see damage to the thing next to it.**

**Then the over-correction, in the same cell.** Re-writing the check to cover every item, I modelled the
rule as "any `---` before an item strands it" and it reported THREE stranded items where the gate reported
one. Reading the gate's actual condition showed the difference: a `---` severs only when the next non-blank
line **starts a new item or section**. The rule at line 1158 is followed by prose, which is legal and which
the file uses deliberately as a paragraph break inside a long item. So my strict check would have had me
delete a legal separator to satisfy a rule the gate does not enforce.

**Two rules, and the second is the one I keep relearning:**
1. After inserting into a sectioned tracker, assert over **every** item in the section, not the one just
   added.
2. **Re-implementing a gate's rule from its symptom produces a different rule.** The gate's message said
   "a `---` closes §6 before item 6.19"; I turned that into "any preceding rule strands an item", which is
   stricter and wrong. Read the checker, or run it — do not reconstruct it from its output.

Running total: six claim-or-count defects, **seven instrument defects** (adding this over-strict positional
check to the six already listed), one fabricated postmortem, and five occurrences of the severed-item
defect.

---

## Round 12: a commit message that describes a diff it does not contain, and no gate can see it

**The defect.** `2f2021c9`'s message describes the AD-4 closure and asserts the header "says five and one";
the `DEFINITIONS.md` it committed says "All six gating decisions are now settled", and its diff also carries
the AD-2 answer, AD-7, and 75 lines of the investigation file. Its successor `6aca55e7` describes the AD-2
finding but contains neither `DEFINITIONS.md` nor the investigation, both already committed. Full measurement
in `_history/_round12/51_commit_attribution_correction.md`.

**The cause, and it is mechanical.** I dispatched a cell ending in `git add -A && git commit`, it was
backgrounded, and I kept editing the same files while it ran. `git add -A` stages the tree when the cell
reaches that line, not at dispatch, so the commit boundary was set by timing rather than by intent.

**One near-miss worth recording.** I first read "100 of 100" against 99 probe rows and nearly reported a
false count discrepancy. The gate reports `len(PROBES) + 1`. Both messages' counts are correct. Checked by
loading each commit's gate module before writing anything down — the same discipline that the fabricated
postmortem above failed.

**The rule.** A commit message is a claim about a diff and carries the same evidence standard as any other
claim here. Never leave `git add -A && git commit` in a cell that may be backgrounded while editing
continues; stage explicit pathspecs for the work being described. And note the blind spot this exposes:
every gate in `check.sh` reads the working tree, so **no gate in this repo can detect a false commit
message** — the class is invisible to the suite by construction.

Running total: **seven claim-or-count defects**, seven instrument defects, one fabricated postmortem, five
occurrences of the severed-item defect.

---

## Round 12: I closed AD-2 on an inference I never checked, and it was one command away

Found by the reviewer. **The second fabricated causal link of this project**, and structurally identical to
the first.

**The defect.** I reported AD-2 answered: the temporal encoder emits one row per check-in, the ETL then
reduces by `drop_duplicates("placeid")`, therefore one arbitrary visit per POI survives and the published
chapter has an unstated lossy step. The middle term was never established. The notebook writes
`time_embedding_novo.csv`; the ETL reads `time_embedding.parquet` (`create_inputs_hgi.py:415`). **Different
name, different format.** I wrote "which is what the ETL reads" and moved on.

**And the gap is wider than the filename.** Re-measured after the finding: **nothing in that repository
writes `time_embedding.parquet`**, no CSV-to-parquet conversion exists in `src/etl/` or `pipelines/`, the
file is not on disk, and that repository's own `CLAUDE.md:91` describes the ETL as reading a `.csv`,
disagreeing with its own code. The producer of the table the ETL consumes is outside the repository and its
granularity is unknown. If it is already POI-level, the dedup is a no-op and there is no selection step at
all — so the entire conclusion, including the description-gap and errata analysis, fails with the link.

**Why it was invisible to me.** Both endpoints were real and independently verified: the stored output shape
`(2535573, 64)` at cell 13, and the dedup at `:437`. Having verified both, I treated the path between them
as verified too. **A chain is not verified when its links are.**

**Same shape as the fabricated postmortem above.** There, three mechanisms were invented to explain a real
failure. Here, one connection was invented to join two real facts. Both times the individual observations
were sound and the *relation* was supplied by expectation. That is the failure mode to watch for in this
project: not false facts, but unearned links between true ones.

**What it cost, and what it did not.** No chapter text is wrong: the author had ruled "nao vamos registrar",
so Chapter 2 writes the neutral form either way. The ruling now rests on firmer ground — not "there is a
selection step we choose not to mention" but "the level is not established, so the chapter asserts nothing".
What was damaged was the record, which is what a later pass reads, and one probe that had been pinning the
retracted conclusion (`R12-notwrong`) went correctly red when the record was corrected. **A probe on a
retracted claim is worse than no probe: it fights the correction.** It was replaced by probes on the
retraction itself.

**The rule.** When a conclusion depends on two artifacts being the same object — a file read and a file
written, a table produced and a table consumed — **that identity is a claim and needs its own evidence**.
The check here was one `grep` for the writer of that filename, and it would have stopped the whole
conclusion before it was written down.

Running total: **eight claim-or-count defects**, seven instrument defects, **two fabricated causal links**,
five occurrences of the severed-item defect.

---

## Round 12: a write that never happened, and a verification that reported success anyway

**This section was WRONG when first written and is rewritten. The defect is real; the mechanism I gave for
it was invented.** The first version said the replacement used byte offsets computed against a stale copy so
`str.replace` matched nothing. That is not what happened, and an auditor caught it.

**What actually happened, read off the cells rather than remembered.** The cell that rewrote the AD-2 row of
`fundamentals/DEFINITIONS.md` also tried to splice a second correction. Its `f.replace(...)` for the row
**succeeded** in memory. Its last statement before any write was an `assert` on a boundary it had computed
for the *other* edit, and that assert **raised**. A traceback means no line after it ran, so `write_text`
never executed and the cell wrote nothing at all. A later cell then re-read the file from disk into the same
variable, discarding the corrected string. **The retracted framing survived in the design document for a full
commit**, still telling a later reader that AD-2 was answered by a "fourth possibility", under a header that
said the opposite.

**Why my verification passed.** I printed a check immediately after and it said the new text was present. It
was right and irrelevant: I checked for a substring the new text contains, which also appears elsewhere in
the file. **A presence check on the replacement is not a check that the replacement happened.**

**Two rules, and the first is the one that generalizes.**
1. **Assert the OLD string is ABSENT, not merely that the new one is present.** This is the only check that
   distinguishes "the edit landed" from "the edit was never applied", and it catches the stale-offset variant
   and this abort variant alike.
2. **A cell that computes and writes must not put an `assert` between them.** Any raise turns the write into
   a no-op while the in-memory value looks correct, and the next cell's re-read erases the evidence. Write
   first, or verify in a separate cell.

**The rule the first version derived was the wrong lesson.** It said to re-read the file before computing
offsets. Under the real mechanism that would have changed nothing: the offsets were fine and the replace
succeeded. A correct rule cannot be derived from an invented cause.

**And that invention is the point.** Finding a real defect, I explained it with a failure mode I had hit
twice before in this project instead of reading what the cells did. That is the same error as the fabricated
postmortem recorded above, and as the unverified link in the AD-2 investigation: **the observation was real
and the mechanism was supplied by memory.** Third occurrence of that family, and the first where the false
mechanism reached a durable record AND a probe rationale before being caught.

**One near-miss inside the fix.** Validating the ban probe on the retracted phrasing, a sabotage leg went
silent and I nearly filed the probe as broken. Reading both literals side by side showed the leg had written
"keeps ... and discarding" where the banned phrase is "keeping ... and discarding". The leg was malformed and
the probe was correct. When a leg and a probe disagree, read both strings before deciding which is wrong.

Running total: eight claim-or-count defects, eight instrument defects, **three invented mechanisms**, five
occurrences of the severed-item defect.

---

## Round 12: I read a collect timeout as a completion, and published the opposite of the truth

**Found by a reviewer. Second false in-budget claim about a sub-agent in this project**, and the first is
recorded above.

**What I published.** For the comparative study: "2,236 s against the 2,400 s checkpoint, 7 percent inside,
the first study this round to finish inside its budget." Written into `PENDENCIAS.md` §6.24, the commit
message, and the prose to the author.

**What 2,236 s actually is.** The moment MY collect window closed. The same output line reads
`OrderCompare | running`, and every structured field beside it was `None`. **A running child with empty
fields is not a finish time.** I even wrote "collect window closed at 2236s" in my own next sentence, and then
used the number as a completion measurement anyway.

**What the measurement was, at the third attempt.** I got this clock wrong twice before reading it properly.
**2,236 s** was my collect timeout. **3,201 s** was the child's age at the arbitrary moment I next looked --
another instrument reading, not a measurement of the process, and I published it as "33 percent over" while
saying I had stopped it there. **The frame record gives the lifetime: 4,185 s, 74 percent OVER the checkpoint**
(`created_at` 1785790156537, `updated_at` 1785794341322). Its self-report of ~1,787 s is understated by 2,398 s.
And it **finished on its own**: the record reads `completed`, so my stop landed after it had closed and
interrupted nothing. Two
things attenuate and neither cancels: the deliverable was already complete on disk when I read it, so the
overrun followed the writing; and the child explicitly deferred to the parent's measurement, which is the
discipline that should have caught this and did not.

**The failure mode, and it is not the same as the first one.** In round 9 I asserted four personas came back
inside a checkpoint without reading the timings I had. Here I had a reading and **misinterpreted its kind**: I
treated an instrument's own timeout as a measurement of the thing being timed. That is worse in one specific
way, because a wrong number invites a re-check while a plausible number in the right units does not.

**The rule, and my first version of it was still too narrow.** I wrote that a figure is admissible from "a
`completed` status with populated fields, or the moment of a `stop_child`" -- and then took the second branch,
which gave me 3,201 s and was wrong too, because a stop timestamp measures when I intervened. **The only
admissible source is the frame record itself** (`created_at` to `updated_at` in the `frames` table), which is
the process's own lifetime and independent of when I looked. Everything else -- collect timeouts, ages at a
glance, stop moments -- **measures my observation, not the child.** Three readings of one clock, two published,
both wrong in the same way.

Running total: nine claim-or-count defects, eight instrument defects, three invented mechanisms, **two false
in-budget claims about sub-agents**, five occurrences of the severed-item defect.

---

## Round 12: I claimed eight probes were sabotage-validated when seven were, and the missing one was the absence probe

**Found by a reviewer.** The commit message of `82f92c5a` and the prose to the author both say "the eight new
ones sabotage-validated". Seven were. `R12-s4moved` was never mutated: the sabotage cell issued eight `leg()`
calls, but one of them was a REPEAT of `R12-s1bind` serving as the silent control, so the count of calls
matched the count of probes while the coverage did not.

**Why this one mattered more than the other seven.** `R12-s4moved` is the only ABSENCE probe of the batch
(`want=False`): it asserts that the two definition environments are GONE from §2.2, which is what makes the
move a move rather than a duplication. **An absence probe holds identically when its pattern can never
match** -- a typo in either branch, and it would have printed `holds` forever while proving nothing. That is
the exact defect class this project has already paid for twice (`R9-clock2`, anchored so it could only match
at document start; `R12-attrib`, whose second alternation branch matched zero times in its target file). The
one probe whose direction was unproven was the one whose failure mode is silence.

**Now validated in both branches and both directions**, and the two-branch structure required two legs rather
than one:
  - branch 1, the plan's working head reinstated -> FIRES;
  - branch 2, a definition duplicated back into §2.2 after the limitation paragraph -> FIRES;
  - unrelated edit -> silent.
File restored byte-identical.

**The rule, and it is about counting rather than about probes.** I verified the batch by reading a validation
table that had the right NUMBER of rows. Eight calls, eight probes, all `OK` -- and the reconciliation I never
did was whether the set of probe NAMES in the table equals the set of probe names added. A control leg reuses
a name, so the row count is not the coverage count. **Reconcile the two sets by name, not by cardinality**,
before writing a coverage claim into a commit message.

Running total: ten claim-or-count defects, eight instrument defects, three invented mechanisms, two false
in-budget claims about sub-agents, five occurrences of the severed-item defect.
