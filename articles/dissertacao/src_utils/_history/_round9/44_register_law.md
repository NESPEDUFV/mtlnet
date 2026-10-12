# 44 · The register law: British English, and phrasing that forces a second reading

**Round 9, 2026-07-30. Baseline `06529ed6`.**
Answers PENDENCIAS 2.22 points 8, 9 and 12.

> **One naming note before you read, because the letter moved under this report.** Everything below
> calls the cosine appendix **Appendix F**, which is what it printed as while this track measured it and
> what your points 8, 9 and 12 refer to. The parallel track then applied your point 0 and **relettered
> it to Appendix D** (commit `4eea637a`); the defense build now prints appendices A, B, C, D and the
> source file is still `chapters/apx_f_cosine.tex`. So: the letter in this report is the one you were
> reading from, the file path is current, and the gate is keyed on the path rather than the letter, so
> nothing in it went stale. Read "Appendix F" here as "the cosine appendix, now D".

---

## 0 · The finding that shaped everything else

Your instance was **not a spelling.**

> *"feature needs saying plainly"*

Every word in that phrase is spelled identically in British and American English. What is British is
the **construction**: `need` + gerund, where American English writes "needs to be said plainly." An
agent told "find the British English" reaches for a spelling list, and a spelling list returns clean
on your own example. That is why the rule and the gate both cover **spellings AND constructions**,
and why the gate's first construction rule is your sentence.

Measured before writing anything, from `articles/dissertacao/`:

```bash
grep -cin "british" WRITING_LAW.md AGENT_GUARDRAILS.md
# WRITING_LAW.md:0
# AGENT_GUARDRAILS.md:0
```

`WRITING_LAW.md` §1 did say "American English throughout" and named no British form, so an agent had
nothing to check against. Nothing at all addressed your second complaint.

---

## 1 · The sweep: what is measured, and how the instrument was proved

### 1.1 The instrument

Scope is **every live `.tex` under `src/`** (54 files, `build/` excluded) plus **`src/references.bib`**,
with comments stripped by the same `(?<!\\)%` rule the audit gate uses and **lines joined** before
matching. Three of this project's own traps are avoided by construction: provenance comments here
quote the sentences under review, a wrapped phrase is invisible to a per-line regex, and a British
spelling inside a `` ``...'' `` quotation may not be corrected without falsifying the quotation.

The `-ise` and `-our` families are **generated and then whitelisted**, not hand-listed. This matters,
and here is the proof it matters: my first `-our` pattern was `\b[A-Za-z]{3,}our\b` and it returned
**zero** while four real hits sat in the tree. The words present are `neighbourS` and
`neighbourHOOD` — neither ends at `our`. A hand-typed pattern finds only the wording its author
imagined (AGENT_GUARDRAILS §4b V17). The corrected pattern is `\b[A-Za-z]{3,}our[a-z]*\b` minus an
explicit list of words whose American spelling is also `-our` (four, hour, source, resource, course,
encourage, tourism, …).

### 1.2 The instrument proved in both directions, before any count was reported

Twenty British/American pairs, each asserted to fire on the British form and to stay silent on the
American one. This runs inside the gate's own `self_test()`, so the gate refuses to report anything
until it passes:

| planted | fires | American twin | silent |
|---|---|---|---|
| neighbours, behaviour, colour | yes | neighbors, behavior, color | yes |
| centre, metre, fibre | yes | center, meter, fiber | yes |
| modelled, travelled, labelled | yes | modeled, traveled, labeled | yes |
| analyse, analysed, analysing | yes | analyze, analyzed, analysis | yes |
| defence, licence, offence | yes | defense, license, offense | yes |
| whilst, amongst, towards | yes | while, among, toward | yes |
| catalogue, programme, grey | yes | catalog, program, gray | yes |
| learnt, judgement, per cent | yes | learned, judgment, percent | yes |
| skilful, normalisation | yes | skillful, normalization | yes |
| **needs saying** (your instance) | yes | **needs to be said** | yes |

Seventeen words that end in `-ise` or `-our` in **both** dialects are asserted **not** to fire
(surprise, comprises, exercised, supervising, revised, improvised, unsurprising, four, hours,
resources, encouraged, discourse, specialized, initialization, maximizing, sources, tourism). A
checker that "corrects" *surprise* to *surprize* would be worse than none.

### 1.3 The measured result, per file, every hit

**TWELVE hit lines over ELEVEN sites**, and the convention matters because the two numbers differ:
one sentence can trip two rules. Per class: **5 A1 spellings, 1 A2 construction, 6 B shapes.** This is
a clean document; the defects are few and specific.

> **This count was wrong in the first version of this report, which said "nine hits" over a
> ten-row table.** Caught by review, not by me, and it is AGENT_GUARDRAILS §4b V13's fourth instance
> exactly: *a table whose headline counts N must have N rows.* The nine came from adding up prose
> categories in my head; the ten-row table then merged the two idioms of one Appendix F sentence into
> one row and **omitted the cosine sentence's chained-qualification hit entirely** — so the total was
> wrong and a real hit was missing from a table titled "every hit". Re-measured below by running the
> gate over the tree as it stood at `06529ed6`, with `OPEN_REGISTER` emptied so nothing is held open
> or suppressed and every hit prints:

```bash
cd /tmp && rm -rf baseline_tree && mkdir baseline_tree
cd /Users/vitor/Desktop/mestrado/ingred
git archive 06529ed6 articles/dissertacao/src | tar -x -C /tmp/baseline_tree   # 54 .tex
# copy src_utils/check_register.py in with OPEN_REGISTER replaced by (), then:
cd /tmp/baseline_tree/articles/dissertacao && python3 src_utils/check_register.py
# rc=1, "FAIL: 6 British spelling/construction hit(s) and 6 hard-phrasing shape(s)"
```

| # | file | class | hit | provenance | disposition |
|--:|---|---|---|---|---|
| 1 | `chapters/3_cbic/method.tex` | A1 spelling | `neighbours` | **our own footnote** | **FIXED** |
| 2 | `chapters/3_cbic/method.tex` | A1 spelling | `neighbourhood` | **our own footnote** | **FIXED** |
| 3 | `tables/frame/bib_errata.tex` | A1 spelling | `neighbours` | **our own table cell** | **FIXED** |
| 4 | `tables/frame/bib_errata.tex` | A1 spelling | `neighbourhood` | **our own table cell** | **FIXED** |
| 5 | `chapters/3_cbic/conclusion.tex` | A1 spelling | `towards` | **published CBIC prose** | **YOURS** (§4) |
| 6 | `chapters/apx_f_cosine.tex` | A2 construction | `needs saying` | our prose | other track (§5) |
| 7 | `chapters/apx_f_cosine.tex` | B shape | delayed subject: *"Two departures … appear"* | our prose | other track (§5) |
| 8 | `chapters/apx_f_cosine.tex` | B shape | idiom: *"point away from trouble"* | our prose | other track (§5) |
| 9 | `chapters/apx_f_cosine.tex` | B shape | idiom: *"in any case"* (same eight-word sentence as 8) | our prose | other track (§5) |
| 10 | `chapters/apx_f_cosine.tex` | B shape | chained qualification, 3 qualifiers / 2 commas: *"…the decline stays inside the margin…"* | our prose | other track (§5) |
| 11 | `chapters/2_fundamentals.tex` | B shape | chained qualification, 3 qualifiers / 3 commas | our prose | **FIXED** |
| 12 | `chapters/6_conclusion.tex` | B shape | delayed subject: *"no such identity … exists"* | our prose | **FIXED** |

**Twelve rows, twelve hit lines.** Rows 8 and 9 are the same sentence (two idioms in eight words,
which the gate names separately and should), so the count of distinct defective **sites** is **11**.
Row 10 also carried an abstract-agent hit under the gate's first B4 rule, which would have made
thirteen lines; B4 was narrowed on the merits (§5.1) and that sentence is now carried by the
chained-qualification rule alone. Every figure in this paragraph comes from the run above, not from
addition.

**Disposition reconciles with the rows, both directions:** 6 FIXED by this track (rows 1-4, 11, 12),
5 closed by the Appendix F track (rows 6-10), 1 open for the author (row 5). 6 + 5 + 1 = 12.

**Zero hits** for: `-ise`/`-isation` (**29** words in the tree match the `-ise`-family candidate
pattern and the whitelist judges **0** of them British; an earlier exploratory sweep reported 56 with
a looser pattern that also swept `-ization` nouns such as *initialization*, which are already
American and were never candidates),
`-yse`, `-re`, doubled `l`, single `l`, `-ce` nouns, `whilst`/`amongst`, `learnt`-family, `grey`,
`programme`, `catalogue`, `judgement`, `per cent`, oe/ae digraphs, `different to`, bare institution
nouns, `have got`, `shall`, `at the weekend`, `was sat`, collective plurals, `providing that`. Each of
those zeros comes from a pattern proved able to find the form when planted (§1.2), which is the
difference between an absence and an unmeasured section.

### 1.4 Two findings the source sweep could not produce

Both came from sweeping the **rendered PDF**, and both are worth more than the hits they found.

**(i) The gate's scope stopped short of the page.** The `.tex`-only version reported clean while
`towards` printed on **page 82 of the defense build**. The bibliography is not a `.tex` file. Scope
now includes `references.bib`, but only the fields **we** author (`note`, `annote`, `abstract`,
`howpublished`, `addendum`). `title`, `journal`, `booktitle`, `series` and `author` are attributes of
record under AGENT_GUARDRAILS §1 R2, and the one British form in the bibliography is inside `Xu2023`'s
title:

> `title = {TME: Tree-guided Multi-task Embedding Learning towards Semantic Venue Annotation}`

Checked against the source of record this session, Crossref `10.1145/3582553`, which returns that
title **with `towards`**. Correcting it would corrupt a citation attribute the protocol requires be
exact. It is out of scope by design, and the gate says so in its own OK line.

**(ii) A false positive the source tree could never have shown.** `analyses` is **both** the British
verb inflection (*he analyses*) and the correct **American plural** of a `-ysis` noun (*the analyses
agree*). My `-yse` rule flagged it. The noun plurals are now excluded by name, re-validated in both
directions: `analyse`/`analysed`/`analysing`/`paralyse`/`catalyse` fire; `analyses`/`paralyses`/
`catalyses`/`analysis`/`hypotheses`/`analyzes` do not.

---

## 2 · The rules I wrote

### 2.1 `WRITING_LAW.md` §1 — the British ban

Two bullets added after the "American English throughout" bullet. The first names both halves:

- **Spellings**, as classes rather than a word list: `-ize`/`-ization`, `-yze`, `-or`, `-er`, single
  `l` before a vowel suffix and double `l` where American doubles it, `-se` nouns, `while`, `among`,
  `toward` without the `-s`, `learned`/`spelled`/`burned`, `program`, `catalog`, `gray`, `judgment`,
  `aging`, `percent`, `skeptic`, `inquiry`, `oriented`, `focused`, no oe/ae digraph. **With the
  explicit warning** that words ending in `-ise` in both dialects (surprise, comprise, exercise,
  advertise, supervise, revise, devise, improvise, compromise, franchise, arise, precise, premise)
  are **not** British and must not be "corrected."
- **Constructions**, which no spelling list reaches: `need`/`want` + gerund (**your instance quoted in
  the law**), `different to`/`than`, bare institution nouns, `have got`, `shall`, `at the weekend`,
  `was sat`/`was stood`, collective noun with plural verb, `providing that`.
- **Two carve-outs**, both narrow: a verbatim quotation keeps its source's spelling; a British form
  in reproduced published prose of one of the three papers is an **errata decision** under
  NORTH_STAR §5.7, brought to you with its cost, never changed quietly.

### 2.2 `WRITING_LAW.md` §1 — the hard-phrasing ban

"Avoid awkward phrasing" is unenforceable, so the rule names **shapes**, each seeded from one of your
three sentences, with your own words on each quoted in the law:

1. **Inverted or delayed subjects.** A named subject held from its verb by a modifier chain with an
   intransitive verb of appearance at the end of the clause (*"Two departures from that flat picture
   **appear**"*), and the cleft that does the same job (*"What carries that diagnosis is…"*). Remedy:
   name the subject and let it act.
2. **An abstract noun as subject where a person or thing would do.** A number does not move or point:
   *"the decline **stays** inside the margin while **moving** toward zero rather than away from it"*
   asks the reader to animate a statistic.
3. **Chained qualification inside one sentence.** Three or more qualifying connectives plus two or
   more commas, each clause narrowing the last. §3 of the law requires the qualifications to be
   **present**, not **stacked**.
4. **Idiom that is native literary register rather than academic register.** *"point away from
   trouble"*, *"in any case"*, *"at any rate"*, *"by the same token"*, *"not least"*, *"if anything"*.
   This extends §4's idiom rule from phrasal-verb metaphors to literary connective idiom, which is
   the class the earlier sweeps let through.

**Your test is the test, both halves of it:** would a Brazilian non-native writer of academic English
produce this sentence, and can a non-native reader take it in on **one** reading. Technical
difficulty is not a defense: keep the term, define it once, simplify around it.

**It cross-references persona 15 rather than inventing a second method.** Your commit `89b7eca1`
added the first-read comprehension method to `reviewers/15_readability_editor.md` (review method,
lens 2, verdict PASS / NEEDS REVISION with zero passages needing a second reading), and
AGENT_GUARDRAILS §5 makes that verdict part of G3. The law points at it and states plainly that **a
green gate is not a first-read PASS.**

### 2.3 `AGENT_GUARDRAILS.md` §4b V16 — second and third instances

V16 existed because you found one sentence that passed every rule and still had no business in the
document. These are the same shape, so they belong there rather than in a new rule. Three details are
recorded because they generalize:

- The first **is not a spelling**, so the checker an agent would build finds nothing.
- The other two **are not errors under any rule the project had**. They are grammatical, honest,
  measured, cited, and unusable on one reading by the audience they are written for.
- All three arrived in **one** reading, of **one** appendix, in a tree where **24 gates were green
  and every one of them was correct**. That is a standing finding about the instrumentation, not
  about you — the same conclusion V12 reaches from the opposite direction. The entry says that when
  you find a fourth class, the right response is to write the rule **and** ask what should have
  surfaced it unprompted.

A row was added to §7's bias table: *writing for a native reader*.

---

## 3 · The gate: `src_utils/check_register.py`, gate 25

### 3.1 Which half is mechanical, stated in the docstring

- **Class A — British spellings and constructions — is mechanical and gated hard.** A word either is
  the British form or is not.
- **Class B — hard phrasing — is partly judgment.** Four shapes are expressible and gated. What is
  **not** expressible, and is **not** claimed, is the general question of whether a sentence reads on
  the first pass. That is persona 15's verdict. The docstring, the failure message and the OK line
  all say so.

### 3.2 Not gated on purpose, and reported to you instead

**Quotation-final period placement.** American style puts the period inside the closing quotation
mark; **13 sites** put it outside:

```bash
cd articles/dissertacao && python3 - <<'PY'
import re, sys; sys.path.insert(0,"src_utils")
from check_register import live_text, SRC
from collections import Counter
c = Counter()
for f in sorted(p for p in SRC.rglob("*.tex") if "build" not in p.parts):
    n = len(re.findall(r"[a-z]''\s*\.", live_text(f)))
    if n: c[str(f.relative_to(SRC))] = n
for k, v in sorted(c.items(), key=lambda x: -x[1]): print(f"  {v}  {k}")
print("  TOTAL:", sum(c.values()))
PY
```

| file | sites |
|---|---|
| `tables/cbic/errata.tex` | 5 |
| `tables/courb/errata.tex` | 3 |
| `chapters/3_cbic/method.tex` | 2 |
| `tables/cbic/errata_wording.tex` | 2 |
| `chapters/apx_b_errata.tex` | 1 |
| **TOTAL** | **13** |

Every one sits in an errata table or a correction row where the quoted string **is the evidence**.
Moving a period inside a quotation alters the quotation. That is a decision about the errata
convention, not a spelling error, so I did not gate it and did not touch it. If you want it changed,
it is mechanical and I can do all 13 in one pass.

### 3.3 The open register, and why it retires itself

Five hits are not this gate's to fix. They are listed **by name** with an owner, printed as `OPEN`,
and excluded from the failure count — a skip is never silent (§4b V7). The entry is **self-retiring**:
if the defect is ever **gone**, the gate **fails** and demands the entry's deletion, so a stale
exemption cannot sit there hiding the next regression in the same place. Validated (leg D below).

### 3.4 Two-directional validation, six legs, sabotage and measurement in ONE shell

Every leg asserted **both** that the file changed **and** that the change reaches `live_text()`
before any exit code was read (§4b V15b: a sabotage that lands in a comment reads exactly like a
probe that never fires). The restore was confirmed by **sha256**, not assumed.

```
LEG A  Class A2 -- plant your own "feature needs saying plainly" in a LIVE line
  precondition OK: file changed AND token present in live_text()
  LEG_A_RC=1
  NAMED: chapters/2_fundamentals.tex: [A2 construction] need / want + gerund
  RESTORED_RC=0

LEG B  Class A1 -- plant "behaviour", then its American twin "behavior"
  planted=behaviour  RC=1   NAMED: matched: 'behaviour'
  planted=behavior   RC=0   American 'behavior' correctly NOT flagged

LEG C  Class B -- plant each of your three flagged sentences
  [point 9  delayed subject]            RC=1  NAMED: [B shape] delayed subject before a
                                              clause-final appearance verb
  [point 12 idiom]                      RC=1  NAMED: [B shape] native-literary idiom  ('point
                                              away from trouble' AND 'in any case', named
                                              separately: two idioms in eight words)
  [point 12 abstract agent + chained]   RC=1  NAMED: [B shape] abstract noun as the agent of a
                                              motion or volition verb; [B shape] chained
                                              qualification inside one sentence

LEG D  a stale OPEN entry must FAIL, not silently pass
  LEG_D_RC=1
  NAMED: STALE OPEN-REGISTER ENTRY: chapters/3_cbic/conclusion.tex '...' (the defect is fixed)

LEG E  a British form in an AUTHORED bib field (note)
  precondition OK: 'behaviour' present in a parsed AUTHORED field
  LEG_E_RC=1   NAMED: references.bib (note): [A1 spelling] -our for -or

LEG F  the SAME words in a TITLE field must NOT fire (attribute of record)
  precondition OK: 'Behaviour and colour' IS in the bib text the parser reads
  LEG_F_RC=0   references.bib findings: 0

FINAL  restore verified by hash, then the clean measurement
  distinct hashes for 2_fundamentals (want 1): 1
  distinct hashes for the gate (want 1):       1
  distinct hashes for references.bib (want 1): 1
  CLEAN_TREE_RC=0
VALIDATION_FAILED_FLAG=0
```

### 3.5 Wired into `check.sh`, and proved in `make selftest`

Gate 25, placed before the audit-claims gate, with a comment naming **which author instance each
half answers** (points 8, 9 and 12 quoted, with your notes on each), stating that scope includes
`references.bib` and why titles are excluded, and stating that a green result is not a first-read
PASS. Runs in **0.28 s**.

A **fixture pair** was added under `_fixtures/check_register/`, so the gate is now `PROVEN` in
`make selftest` rather than merely present. Two shapes of the fixture are load-bearing and are
documented in its README: twenty filler chapters (the gate refuses to report below a 20-file scope
floor) and stubs at the two real open-register paths (an entry whose needle is absent makes the gate
fail, correctly). Its `references.bib` carries `towards`, `Behaviour` and `Colour` inside `title` and
`journal`, and **both** sides must stay silent on them.

**One thing I found while wiring it, unrelated to the register but a coverage claim:**
`selftest_all.py` printed *"14 checkers"* for a directory holding **seventeen**.
`check_audit_claims` (the gate that re-measures every APPLIED claim) and
`check_process_narration` were absent from its own coverage table, so the report has been describing
a smaller surface than the tree has. Both added; the header count derives from the tuple and now
reconciles at 17. This is §4b V13's fourth instance again: a total that does not reconcile with its
own rows.

---

## 4 · The one hit I left for you, with its cost

**`chapters/3_cbic/conclusion.tex`, rendered on p. 43 of the defense build:**

> "The representation learned by the shared layers might have become biased **towards** the features
> required for the simpler, static classification task, inadvertently hindering its effectiveness for
> the more complex sequential prediction task."

**It is verbatim published CBIC 2025 prose.** Measured, not assumed: the string
`might have become biased towards the features required for the simpler, static classification task`
is a literal substring of `articles/CBIC___MTL/sections/conclusion.tex:13`. It is also the **only**
British form in the entire published CBIC source (one `towards`, zero `-our`, zero `-ise`), and the
CoUrb-EN and MobiWac sources have none at all.

**Cost of fixing:** one row in `tables/cbic/errata_wording.tex`, which already carries **fourteen**
wording rows of exactly this class ("By leveraging shared information" → "By using shared
information"; "These findings underscore that" → "These findings indicate that"; and twelve more),
all under the caption *"claim strength unchanged or reduced, never raised."* Changing `towards` to
`toward` changes no claim. (Counted by splitting the tabular body on `\\` between `\midrule` and
`\bottomrule` — a `grep -c` on the row-opening quote returns 63, which counts every `` `` `` in the
file rather than every row, and would have been the wrong number in this report.)

**Cost of not fixing:** the document contains one British spelling, in a chapter of published prose,
which the errata regime already exists to record. The gate holds it open **by name** and fails if the
entry ever goes stale, so it cannot be quietly forgotten either way.

**I did not apply it.** Under NORTH_STAR §5.7 a departure from a published source is yours to approve,
and this one is a matter of vocabulary rather than of correctness.

> **Your call:** (a) change it and add the errata row — one line, same class as the six already
> there; or (b) leave it, and the open-register entry becomes a permanent record of the decision.

---

## 5 · The Appendix F track's four hits — reported, and now CLOSED by that track

`chapters/apx_f_cosine.tex` and `tables/frame/cosine.tex` are owned by the parallel track, so I swept
them and edited neither. Its four register hits, all in `apx_f_cosine.tex`, were rendering on p. 99 of
the defense build:

| your point | the text that was there | class | remedy the law prescribes |
|---|---|---|---|
| **8** | "one feature **needs saying** plainly" | British `need`+gerund | "needs to be said plainly" |
| **9** | "**Two departures from that flat picture appear**, and both are worth reporting rather than smoothing" | delayed subject | name the subject: "The figure shows two departures." |
| **12** | "**Both point away from trouble in any case.**" | two literary idioms in eight words | state the reading: "Neither departure indicates a conflict." |
| **12** | "the **decline stays** inside the margin throughout **while moving** toward zero rather than away from it" | chained qualification (3 qualifiers, 2 commas) | split it |

**All four are now GONE**, and this is the part worth reading, because it is the only evidence that the
self-retiring open register works. That track landed its rewrite at 16:46. On the next run this gate
went **RED**, naming all four entries as `STALE OPEN-REGISTER ENTRY … (the defect is fixed)` and
demanding their deletion. **Nobody had to remember to come back.** The exemption could not outlive its
defect, which is what §4b V14 asks of every APPLIED claim, and the four entries were deleted from
`OPEN_REGISTER` with the mechanism recorded in a comment where they used to be.

Re-swept after their rewrite: `apx_f_cosine.tex` **0 hits**, `tables/frame/cosine.tex` **0 hits**. Its
replacement sentence reads *"A positive cosine means the two tasks cooperate slightly, and the
declining cosines stay inside the margin and move toward zero, not away from it"* — no British form,
one qualifier, and the subject named first.

### 5.1 Their rewrite exposed a real defect in my own detector, and I fixed it on the merits

The first version of the abstract-agent rule (B4) also listed **motion** verbs, and it fired on their
corrected sentence. Two facts convicted the rule rather than the sentence:

1. **The remedy the rule itself printed** prescribed *"the mean **falls** toward zero"* — a motion
   verb. The rule was recommending a rewrite of the shape it banned.
2. It fired on *"the declining **cosines** … **move** toward zero"* while staying silent on *"the
   **mean** falls toward zero"*, and the only difference is that `cosine` happened to be in the noun
   list and `mean` did not. **A detector whose verdict turns on which noun someone thought to type is
   measuring its own list, not the prose.**

B4 is now scoped to verbs of **volition, cognition and speech** — a quantity that *refuses*, *prefers*
or *admits* has been animated; one that *rises*, *falls* or *moves* has not. Your point-12 sentence is
still caught, by the **chained-qualification** rule, which is the rule that actually describes what
made it hard: three qualifiers and two commas. That reassignment is asserted in the gate's self-test,
so a later widening of B4 cannot quietly become the only thing covering your instance, and four
literal-motion sentences from this document are asserted **not** to fire.

---

## 6 · Builds and gates, exit codes read directly and never through a pipe

Measured as the last actions before each commit (§4b V11):

**With this track's four fixes and nothing else** (measured after them, before the Appendix F track
landed):

| target | pages | tex_errors | make rc |
|---|--:|--:|--:|
| `make defense` | **102** | 0 | 0 |
| `make academico` | **99** | 0 | 0 |
| `make ppgc` | **103** | 0 | 0 |
| `make extra` | **20** | 0 | 0 |

Identical to the baseline measured at `06529ed6` before any edit: 102 / 99 / 103 / 20, zero TeX errors.
**The four prose fixes on this track changed no page count**, which is what you would expect from two
American respellings and two sentences rewritten at the same length.

**Re-measured at 16:47, after the Appendix F track landed its rewrite** (202 insertions, 61 deletions
in `apx_f_cosine.tex`, uncommitted at that moment):

| target | pages | tex_errors | make rc |
|---|--:|--:|--:|
| `make defense` | **101** | 0 | 0 |
| `make academico` | **98** | 0 | 0 |
| `make ppgc` | **102** | 0 | 0 |
| `make extra` | **20** | 0 | 0 |

**The one-page drop is that track's, not this one's**, and the attribution is measured rather than
inferred: `git log --name-only` over this track's commits lists only `2_fundamentals.tex`,
`3_cbic/method.tex`, `6_conclusion.tex` and `tables/frame/bib_errata.tex`, the 102-page measurement
postdates all four of them, and the only source file changed between the two measurements is
`apx_f_cosine.tex`. **I did not run `sync_page_counts.py --write`**: the recorded counts in `CLAUDE.md`,
`PLAN.md` and `codex_reviewer.md` belong to whoever lands that appendix rewrite, and re-stamping them
from a tree holding another track's uncommitted work would put a number in your durable records whose
provenance is a working directory. `make check` is therefore RED on that one gate at handoff, with
`sync_page_counts` naming all seven stale claims. §8 says so plainly.

**While this track's work was the only uncommitted change in the tree**, read directly before each of
its three commits:

```
bash src_utils/check.sh            -> rc=0   (25 gates, all under the 5s threshold; suite total
                                              2.455s to 2.842s across runs in this round)
python3 src_utils/selftest_all.py  -> rc=0   (5 PROVEN, 0 FAILED, 17 checkers reported)
python3 src_utils/check_register.py -> rc=0  (54 .tex + references.bib; 5 hits held OPEN by name)
```

**At handoff, with the Appendix F track's rewrite in the tree uncommitted**, and this is the state you
will actually see:

```
bash src_utils/check.sh            -> rc=1   ONE gate red: "recorded page counts vs the measured
                                              build", 7 stale claims, all of them the 102/99/103 ->
                                              101/98/102 drop caused by that track's rewrite. The
                                              other 24 gates pass.
python3 src_utils/selftest_all.py  -> rc=0   (5 PROVEN, 0 FAILED)
python3 src_utils/check_register.py -> rc=0  (54 .tex + references.bib; 1 hit held OPEN, the
                                              published CBIC `towards` in §4)
```

I am reporting the red rather than clearing it, because clearing it means writing a page count into
`CLAUDE.md` and `PLAN.md` that was measured from a tree containing another track's uncommitted work.
`python3 src_utils/sync_page_counts.py --write` fixes all seven in one command once that rewrite is
committed.

Gate count went **24 → 25**: `git show 06529ed6:…/check.sh | grep -c '^gate "=='` returns 24 at the
baseline, and the current suite reports 25. `check_register` costs **0.27 s**, measured in the timing
table on the run that made this line.

---

## 7 · The four fixes, each with its rendered evidence

Every one verified in **both** directions in the rendered PDF: new text present, old text absent.
Page numbers are the defense build (102 pp) unless stated.

### 7.1 `chapters/3_cbic/method.tex` — footnote 3, **p. 34**

`neighbours` → `neighbors`, `neighbourhood` → `neighborhood`. **Rendered:**

> "The released implementation feeds the network the mean of the one-hot vectors of a POI's graph
> **neighbors**, with the POI's own vector excluded, rather than the POI's own one-hot vector
> (`research/embeddings/dgi/preprocess.py`). … The distinction matters for how the embedding should be
> read: the input describes a POI's **neighborhood**, so the static task the embedding supports is
> spatial homophily rather than recall of the POI's own label."

**No errata row owed, and this was measured rather than assumed.** Neither string occurs anywhere in
`articles/CBIC___MTL/sections/*.tex`; that source contains no "released implementation" text at all.
The footnote is this dissertation's own addition. The published sentence it annotates is untouched,
and it already writes `neighbors` American in the body at line 21 of the same file — the footnote was
the file's only British spelling. Also at p. 31 (academico) and p. 35 (ppgc).

### 7.2 `tables/frame/bib_errata.tex` — **p. 13 of the supplementary volume**

Same pair, in the errata row that describes that footnote. **Rendered:**

> "The released implementation feeds the mean of the one-hot vectors of a POI's graph **neighbors**,
> with the POI's own vector excluded. | Published sentence preserved; a footnote records what the code
> does and why the distinction matters. The embedding therefore describes a **neighborhood** rather
> than a POI's own label, so the static task it supports is spatial homophily."

This row prints in `make extra` only; Appendix B is in the supplementary volume, so the defense build
does not carry it. Same provenance measurement: our own prose, no errata row owed.

### 7.3 `chapters/6_conclusion.tex` — **p. 78**

Was: *"What carries that diagnosis is the direction and the size of the effect on the sequential task,
where no such identity between input and target **exists**, and Chapter 5 **is what tests it**."*
Three defects of the shapes you named: a cleft opening that delays the subject to mid-sentence, an
existential clause ending in "exists", and a second cleft. **Rendered now:**

> "The sequential task carries that diagnosis, because its input does not determine its target, and
> the direction and the size of the effect there are what Chapter 5 tests."

**Claim unchanged.** The sequential task still carries the diagnosis, the reason is still the absence
of the input-to-target identity Appendix B records for the static task, and Chapter 5 is still named
as what tests it. Also p. 75 (academico), p. 79 (ppgc).

### 7.4 `chapters/2_fundamentals.tex` — **p. 22**

Was one 38-word sentence with three qualifying connectives, three commas, and its main verb held to
word 21: *"The principle these architectures share, keeping shared and task-specific components side
by side rather than forcing one common trunk, is the one the joint model of Chapter 5 adopts, though
it realizes it with cross-attention rather than expert gating."* **Rendered now, as two sentences:**

> "These architectures share one principle: they keep shared and task-specific components side by side
> instead of forcing one common trunk. The joint model of Chapter 5 adopts that principle and realizes
> it with cross-attention rather than expert gating."

**Claim unchanged.** One `rather than` became `instead of` so the split does not raise the
negative-parallelism density that gate 20 holds under a ceiling; the second is kept because it scopes
how the principle is realized. Also p. 19 (academico), p. 23 (ppgc).

---

## 8 · What is left, and for whom

**Yours (§4):** the `towards` in published CBIC prose. One errata row, or a recorded decision to
leave it.

**Yours if you want it (§3.2):** the 13 quotation-final periods outside the quotation mark. Not
gated, not touched — the quoted strings are evidence in errata tables, and moving a period inside a
quotation alters the quotation.

**The Appendix F track's (§5): CLOSED by that track.** Your four instances from points 8, 9 and 12 are
gone from the source and the appendix now sweeps clean for both classes. The gate went red naming all
four exemptions as stale, which is how I learned they had landed, and the entries were deleted.

**Whoever commits the Appendix F rewrite (§6):** run `python3 src_utils/sync_page_counts.py --write`.
Seven page-count claims across `CLAUDE.md`, `PLAN.md` and `codex_reviewer.md` are stale by one page
because of that rewrite, and `make check` is red on that one gate until they are re-stamped. Not mine
to stamp from a tree holding someone else's uncommitted work.

**Nothing else was left undone on this track.** The four fixes outside those two files are applied and
verified in the render; the rules are written into both law files; the gate is wired, validated in six
directions, proved in `make selftest`, and has already caught one real defect in itself (§5.1) and
retired four of its own exemptions without being asked.

**One thing I would flag as my own judgment rather than measurement.** The Class B half of the gate
catches four shapes and cannot catch "this needs a second reading." I have said so in the docstring,
the failure message, the OK line, the law and this report, because the risk of a partly-mechanical
gate is precisely that a green run gets read as a clean chapter. Persona 15's first-read verdict is
the other half, and it is not optional.
