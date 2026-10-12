# Review 11 - POI / mobility expert (fresh-eyes audit)

**Persona:** `reviewers/11_poi_mobility_expert.md` (next-location / POI-recommendation domain reviewer)
**Build commit:** `901a0408`
**Date:** 2026-07-30 (UTC), session start 11:41Z, checkpoint honored at 11:53Z
**Verdict for the POI/mobility content in scope:** **sound-with-corrections**
**Read-only.** I edited nothing but this file.

## Scope actually read

Narrowed scope as briefed. Files read in full or in the stated line ranges, from the checkout at
`/Users/vitor/Desktop/mestrado/ingred/articles/dissertacao`:

- Law files: `AGENT_GUARDRAILS.md` (L1-200: §0-§4b), `WRITING_LAW.md` (L1-120: §1-§4), `GLOSSARY.md` (all 193 lines), `reviewers/11_poi_mobility_expert.md`.
- `src/chapters/2_fundamentals.tex` L1-384 (§2.1 and §2.2 complete) and L615-844 (§2.4 complete). **§2.3 skipped per brief.**
- Chapter 5: `src/chapters/5_mobiwac/01_introduction.tex`, `02_related.tex`, `03_problem.tex`, `05_setup.tex` (all complete), `04_method.tex` (grep-scoped), `06_results.tex` L1-130 and L280-387, `07_discussion.tex` (grep-scoped), `08_conclusion.tex` (grep-scoped).
- Tables: `src/tables/mobiwac/datasets.tex`, `src/tables/mobiwac/results.tex`, `src/tables/frame/lineage.tex`.
- Cross-checks outside scope, read only to confirm a claim is or is not carried elsewhere: `src/chapters/1_introduction.tex` (grep), `src/chapters/6_conclusion.tex` L120-170 + L249, `src/chapters/3_cbic/method.tex:54`, `src/chapters/4_courb/methodology.tex:95`.
- **PDFs: not read.** See UNFINISHED. Every location below is `file:line` in the *source*, so the author can re-verify without a build. **Caveat on the location layer, corrected twice on 2026-07-30 after review, and the second correction is the instructive one.** My finding-by-finding sweep re-resolved cited phrases against the unstripped file, but it covered only a subset of the pointers, and three shipped in the first version of this report as *stripped-grep* numbering (`1_introduction.tex:31`/`:143`, correct values 63/193; `05_setup.tex:9`, correct value 22). My first repair then added a sweep that flagged only pointers landing on a blank line, a pure-comment span, or a bare structural line, and I concluded from it that no stale pointer remained. **That conclusion did not follow from that instrument.** A stale pointer landing on ordinary prose passes such a check silently, which is exactly the class being repaired: `1_introduction.tex:143` reads `other two.`, ordinary prose, and the heuristic would have cleared it. Caught in review, not by me, and it is the AGENT_GUARDRAILS 4b R2/V3 failure in its textbook form, a clean result from an instrument blind to the defect.

The sweep is now **phrase-anchored**: every pointer is paired with a literal substring that must occur inside the cited span, taken from this report's own quote or from the sentence attributed to that location, so a pointer landing on the wrong prose fails. Its verbatim output at the saved revision is `claim pointers: 45 | anchor-verified: 45 | FAILED: 0 | no anchor: 0 | excluded as historical: 4`, over 61 pointer instances in the prose. The four exclusions are this caveat's own record of the stale values (`1_introduction.tex:143`, `05_setup.tex:9`, `02_related.tex:65`, and one repeat), which are history rather than claims and are named in an explicit list in the script rather than skipped by line position. Anchoring found one further defect the heuristic had cleared, now fixed: `02_related.tex:65` was cited for "rather than the exact place", which begins on line 65 and completes on line 66, so the pointer is now `:65-66`. **Negative control (V3), because a clean result from an unvalidated instrument is what got me here:** run against the two known-stale pointers of the first correction, the anchored check reports the anchor absent at both `1_introduction.tex:143` and `05_setup.tex:9`, so it demonstrably fires on the defect class. What it still cannot check is whether a *verified* pointer is the *most apt* location for the claim, or whether my reading of the quoted sentence is right, so a reader auditing a specific finding should still open the span rather than trust the sweep.
- **Chapters 3, 4 and §2.3: not read.** Per brief.

### Commands I ran (runnable from `articles/dissertacao/src` unless noted)

Comment-stripping per AGENT_GUARDRAILS 4b V4 (`grep -v '^[[:space:]]*%' "$f" | grep -n ...`), because this
tree quotes the searched strings inside provenance comments. All line numbers reported in findings were
then re-resolved against the *unstripped* file with a literal-phrase `grep -n` **for the pointers inside the five findings**; three pointers in the supporting lists were not covered by that sweep and were corrected after review (see the caveat above). The sweep command was:

```bash
# from articles/dissertacao/src -- run per literal phrase, prints the unstripped line number
grep -n "<literal phrase from the quote>" <file>
```

```bash
# from articles/dissertacao
git rev-parse --short HEAD                                  # -> 901a0408
grep -n '^.section\|^.subsection\|^.chapter' src/chapters/2_fundamentals.tex
wc -l src/chapters/2_fundamentals.tex src/chapters/5_mobiwac/*.tex

# from articles/dissertacao/src   (representative; the same idiom was run per pattern group)
for f in chapters/*.tex chapters/5_mobiwac/*.tex; do out=$(grep -v '^[[:space:]]*%' "$f" \
  | grep -n -i "temporal split\|chronolog\|time-based split\|split in time"); \
  [ -n "$out" ] && { echo "--$f"; echo "$out"; }; done
for f in chapters/*.tex chapters/5_mobiwac/*.tex; do out=$(grep -v '^[[:space:]]*%' "$f" \
  | grep -n -i "revisit\|persistence\|previously visited\|explore"); \
  [ -n "$out" ] && { echo "--$f"; echo "$out"; }; done
grep -v '^[[:space:]]*%' chapters/2_fundamentals.tex | grep -c -i "window\|sliding\|overlap\|stride"
grep -v '^[[:space:]]*%' chapters/5_mobiwac/05_setup.tex | grep -c -i "window\|sliding\|overlap\|stride"
grep -v '^[[:space:]]*%' chapters/2_fundamentals.tex | grep -n -i "transduct\|leak\|audit\|unseen\|cold.start"
grep -v '^[[:space:]]*%' chapters/5_mobiwac/05_setup.tex | grep -c -i "transduct\|leak\|audit\|unseen"
grep -n "<literal phrase>" chapters/5_mobiwac/05_setup.tex     # to resolve every quoted line number
```

Pointer sweep added after review, runnable from `articles/dissertacao`; it is the evidence for the
caveat above and it re-runs against this file as saved:

```python
# Phrase-anchored pointer check. Runnable from articles/dissertacao. Every pointer in this report is
# paired with a literal substring that MUST occur inside the cited span; a pointer landing on the
# wrong prose therefore FAILS, which the earlier blank/comment/structural heuristic could not detect.
import re, pathlib
ANCHORS = {
 "src/chapters/3_cbic/method.tex:54": "ordered chronologically per user",
 "src/chapters/4_courb/methodology.tex:95": "Non-overlapping windows of size",
 "chapters/4_courb/methodology.tex:95": "Non-overlapping windows of size",
 "src/chapters/2_fundamentals.tex:615-622": "A claim about mobility prediction is only as trustworthy",
 "src/chapters/5_mobiwac/05_setup.tex:30": "overlapping sliding windows of nine visits",
 "05_setup.tex:30": "overlapping sliding windows of nine visits",
 "05_setup.tex:32": "overlap cannot leak",
 "src/chapters/2_fundamentals.tex:125-380": "How a place is represented determines",
 "src/chapters/5_mobiwac/05_setup.tex:64": "on four grounds",
 "2_fundamentals.tex:228-231": "extends the",
 "05_setup.tex:66": "bounds the training signal and not the inputs",
 "2_fundamentals.tex:146-148": "generalize to nodes unseen during training",
 "src/chapters/2_fundamentals.tex:53-61": "asks for the map",
 "src/chapters/5_mobiwac/03_problem.tex:13": "a municipal neighborhood",
 "03_problem.tex:13": "a municipal neighborhood",
 "05_setup.tex:22": "The region unit is a census tract",
 "src/tables/mobiwac/datasets.tex:30-35": "8{,}501",
 "tables/mobiwac/datasets.tex:30-35": "8{,}501",
 "02_related.tex:69-71": "substitutes official neighborhood-scale units for grid cells",
 "2_fundamentals.tex:55": "mahalle",
 "chapters/1_introduction.tex:63": "mahalle",
 "src/chapters/2_fundamentals.tex:734-744": "Every metric is read against reference points",
 "src/chapters/5_mobiwac/06_results.tex:301-302": "the last visited region in",
 "06_results.tex:299-302": "advance one visit at a time",
 "06_results.tex:301": "the last visited region in",
 "06_results.tex:301-302": "the last visited region in",
 "src/chapters/2_fundamentals.tex:643-647": "accuracy at 10",
 "src/chapters/5_mobiwac/05_setup.tex:129-131": "macro-averaged F1",
 "05_setup.tex:134": "acts on which region will be busy",
 "07_discussion.tex:68-71": "anticipatory",
 "06_results.tex:384-385": "The comparable quantity is the gain over the ceiling",
 "02_related.tex:65-66": "rather than the exact place",
 "06_results.tex:282-293": "above every external baseline reported",
 "05_setup.tex:156": "The comparisons play three roles",
 "2_fundamentals.tex:752-755": "stratify by sample rather than by user",
 "05_setup.tex:68": "Rebuilding the representation per fold",
 "05_setup.tex:70": "region-transition prior",
 "tables/mobiwac/results.tex:59-64": "STAN partial folds",
 "2_fundamentals.tex:738-744": "it is not, however, a ceiling on",
 "chapters/6_conclusion.tex:249-251": "Data vintage",
 "07_discussion.tex:74": "epoch selection consults the fold",
 "01_introduction.tex:27": "fn:mobiwac:code",
 "05_setup.tex:64-75": "on four grounds",
 "2_fundamentals.tex:188-190": "VERIFY: averaging convention",
 "05_setup.tex:131": "counts as an error",
}
# Pointers the report cites as the STALE values it corrected. They are historical record, not claims,
# and must not be anchor-checked. Named explicitly instead of skipped by line number (a positional skip
# is the kind of instrument that silently drifts).
HISTORICAL = {"1_introduction.tex:31", "1_introduction.tex:143", "05_setup.tex:9",
              "chapters/1_introduction.tex:143", "chapters/5_mobiwac/05_setup.tex:9",
              "02_related.tex:65"}
rep = pathlib.Path("src_utils/_history/_round9/reviews/11_poi_mobility_expert.md").read_text().splitlines()
roots = [pathlib.Path(p) for p in (".", "src", "src/chapters", "src/chapters/5_mobiwac",
         "src/chapters/3_cbic", "src/chapters/4_courb", "src/tables/mobiwac", "src/tables/frame")]
pat = re.compile(r"([A-Za-z0-9_/\.\[\]]+\.tex):(\d+)(?:-(\d+))?")
def span_of(ptr):
    f, a, b = pat.match(ptr).group(1), *pat.match(ptr).group(2, 3)
    p = next((r/f for r in roots if (r/f).exists()), None)
    if p is None: return None
    L = p.read_text().splitlines()
    return "\n".join(L[int(a)-1:(int(b) if b else int(a))])
seen, ok, fail, noanchor, hist, fenced = set(), 0, [], [], set(), False
for l in rep:
    if l.lstrip()[:3] == chr(96)*3: fenced = not fenced; continue   # chr(96)*3 = a markdown fence
    if fenced: continue                        # skip this script's own text, incl. its control block
    for m in pat.finditer(l):
        ptr = m.group(0)
        if ptr in seen or ptr in hist: continue
        if ptr in HISTORICAL: hist.add(ptr); continue
        seen.add(ptr)
        anc, sp = ANCHORS.get(ptr), span_of(ptr)
        if sp is None: fail.append((ptr, "UNRESOLVED PATH"))
        elif anc is None: noanchor.append(ptr)
        elif anc in sp: ok += 1
        else: fail.append((ptr, f"ANCHOR {anc!r} NOT IN SPAN"))
print(f"claim pointers: {len(seen)} | anchor-verified: {ok} | FAILED: {len(fail)} "
      f"| no anchor: {len(noanchor)} | excluded as historical: {len(hist)}")
for x in fail + [(q, "NO ANCHOR") for q in noanchor]: print("  ", x)

# V3 NEGATIVE CONTROL: the check must FAIL on the two known-stale pointers of the first correction.
for bad, anc in [("chapters/1_introduction.tex:143", "mahalle"),
                 ("chapters/5_mobiwac/05_setup.tex:9", "The region unit is a census tract")]:
    print(f"   control {bad}: anchor present? {anc in span_of(bad)}   <- must be False")
# OBSERVED at the saved revision, extracted from this file and run verbatim, output copied:
#   claim pointers: 45 | anchor-verified: 45 | FAILED: 0 | no anchor: 0 | excluded as historical: 4
#      control chapters/1_introduction.tex:143: anchor present? False   <- must be False
#      control chapters/5_mobiwac/05_setup.tex:9: anchor present? False   <- must be False
```

**Instrument validation (V3), because three of my five findings are absence claims.** Each absence
pattern was proved able to fire before I trusted a zero:

| Pattern | On §2.1/2.2/2.4 live prose | On a file that must hit | Verdict |
|---|--:|--:|---|
| `window\|sliding\|overlap\|stride` | **0** | `05_setup.tex` = **8** | instrument sees the words |
| `transduct\|leak\|audit\|unseen` (excl. GraphSAGE "unseen") | **0** substantive | `05_setup.tex` = **4** | instrument sees the words |
| `temporal split\|chronolog\|time-based split` | **0** in Ch.2 and Ch.5 | whole `chapters/` tree = **2**, both `chronologically` in Ch.3/Ch.4 method text | instrument sees the words; no chapter states a temporal axis |
| bare `temporal` | 4 in Ch.2 | 5 files | not a dead pattern |

No skips, no `continue`, no `except: pass` in anything above. I ran no build, no `make check`, no
`make selftest`, per brief.

---

## Findings

### 1. SHOULD-FIX - §2.4 promises a protocol section but never discloses window construction, so the chapter's own leakage argument is unstated in the frame

**WHERE:** `src/chapters/2_fundamentals.tex:615-622` (the section's purpose statement) and `:746-755`
(the protocol paragraph); the absence spans the whole of §2.4. Counterpart that holds the facts:
`src/chapters/5_mobiwac/05_setup.tex:30` and `:32`.

**WHAT.** §2.4 opens (`:618-622`):

> "A claim about mobility prediction is only as trustworthy as the data it is measured on and the protocol that measures it. This section fixes both: the datasets the dissertation uses, the metrics and reference points each result is read against, the validation protocol that keeps the estimate honest, and the tests that license the verbs used to report a comparison."

The protocol paragraph then delivers the split axis only (`:746-751`):

> "The validation protocol guards against the most damaging error in this setting, a user whose check-ins appear in both training and test. Estimates use stratified k-fold cross-validation \cite{kohavi1995crossval}, and the folds are formed so that no user spans a split"

Measured: the words *window*, *sliding*, *overlap*, *stride* occur **zero** times in §2.1-§2.5 live
prose (one occurrence in the whole file, inside a comment). Chapter 5 carries all of it at
`05_setup.tex:30`: "we build time-ordered overlapping sliding windows of nine visits, one starting at
each visit", plus the padded-duplicate drop, and at `:32` the licence: "all of a user's windows fall in
the same fold and overlap cannot leak: a test user's visits never appear in training."

**WHY.** Overlapping stride-1 windows are the field's single most common silent leak vector, and the
combination that makes them safe is *precisely* user-disjoint folds. §2.4 states the fold axis and
omits the window construction, which leaves the frame with the half of the argument that is not
load-bearing. Two consequences inside the document, both mine to point at rather than to fix:

- The chapter that reports the *unit of analysis* for every number in the dissertation never says
  what that unit is. Chapters 3 and 4 use **non-overlapping** windows (`chapters/4_courb/methodology.tex:95`:
  "Non-overlapping windows of size $L_h = 9$ are extracted"; GLOSSARY §3 *sliding windows* row records
  the same contrast), and Chapter 5 uses overlapping ones. §2.4's paragraph on how the protocol
  "strengthened from one study to the next" (`:752-755`) names only the split axis, so a reader is not
  told the windowing changed too.
- §2.4 asserts stratified k-fold with grouping but never states *what the strata are*. Chapter 5 does
  (`05_setup.tex:32`: "stratified on the next-category label"). In the frame, "stratified" is unbound.

This is a §2.4 gap, not a Chapter 5 gap; per WRITING_LAW §1 ("background always tied to its downstream
use") and per persona lens 2, which asks for the overlap-cannot-leak argument stated explicitly.

**FIX.** Two sentences in the protocol paragraph at `:746-755`, quoting Chapter 5 rather than
recomputing: name the window unit (nine visits, one per starting position in Chapter 5; non-overlapping
in Chapters 3 and 4), name the stratification label, and carry over the one-clause licence from
`05_setup.tex:32` that overlap cannot leak *because* folds are user-disjoint. Whether the frame should
also carry the padded-duplicate rule is the author's call; I would leave that in Chapter 5.

---

### 2. SHOULD-FIX - the frame never states that the representation is trained transductively, so §2.2's argument and §2.4's protocol both read cleaner than the study is

**WHERE:** absence across `src/chapters/2_fundamentals.tex:125-380` (§2.2) and `:615-784` (§2.4).
The facts exist at `src/chapters/5_mobiwac/05_setup.tex:64` (the four grounds), `:66` (label-free
scope), `:68` (the audit numbers and their coverage), and `:89` (the three residual limits).

**WHAT.** §2.2 develops the whole representation line and, at the check-in level, says only
(`2_fundamentals.tex:228-231`):

> "It extends the graph-infomax hierarchy with a fourth level below the place, the check-in, and is trained without task labels in the same infomax spirit"

and after the equations (`:256-257`):

> "No target label appears in any of the three equations, which is the sense in which the representation is trained without task labels."

Chapter 5 is markedly more careful about exactly this inference (`05_setup.tex:66`):

> "That bounds the training signal and not the inputs, since each visit's own category enters as a node feature (Section~\ref{sec:mobiwac:method-rep}); the fourth ground below measures what that feature can carry between visits."

Measured: `transduct|leak|audit|unseen|cold-start` appears **zero** times in §2.1-§2.5 live prose apart
from the GraphSAGE inductive sentence at `2_fundamentals.tex:146-148`; the same pattern hits four times
in `05_setup.tex`. The GLOSSARY registers both **transductive** and **leakage audit** (§3) and marks
the latter "Ch.5 §5.2 material".

**WHY.** This is the "label-free therefore safe" reasoning that persona lens 3 exists to attack, and
§2.2 states the label-free premise twice with no counterweight. It is not wrong (nothing in §2.2 claims
safety), but it is the frame's *only* statement about how the representation is fitted, and Chapter 5's
own text says the premise bounds the training signal and not the inputs. Two further gaps follow:

- §2.2 explicitly teaches the inductive/transductive distinction at `:146-148` ("GraphSAGE learns
  aggregator functions that generalize to nodes unseen during training, making the embedding
  inductive"), then never says on which side of that distinction this dissertation's own
  representations fall. A domain examiner who reads that sentence will ask, and the answer in Chapter 5
  is "transductive, trained once on the whole dataset, with a measured audit and a stated residual".
- §2.4's protocol paragraph guards the *fold* channel and is silent on the *artifact* channel, so
  §2.4 as written asserts that user-disjoint folds are what "keeps the estimate honest" (`:621`)
  when Chapter 5 needs four grounds to make that stand.

**FIX.** One sentence in §2.2 at the check-in-level paragraph (`:228-231`) or in §2.4's protocol
paragraph: the representations in this dissertation are fitted once over the full corpus
(transductive), so a label-free objective bounds the training signal and not the inputs, and
Chapter 5 measures the residual channels. Quote Chapter 5's audit numbers only if the author wants
them in the frame; the pointer alone discharges the honesty obligation, and per N1 the numbers belong
to Ch.5's source of record.

---

### 3. SHOULD-FIX - the region unit is named everywhere but justified nowhere; §2.1's cardinality claim about places is unsourced in a chapter that scopes region counts out

**WHERE:** `src/chapters/2_fundamentals.tex:53-61` (§2.1 task definitions and the cardinality
sentence). Counterpart: `src/chapters/5_mobiwac/03_problem.tex:13` and `05_setup.tex:22`;
`src/tables/mobiwac/datasets.tex:30-35` (the region-count column).

**WHAT.** §2.1 `:53-55`:

> "\emph{Next-region prediction} asks for the map partition the next POI falls in, a census tract in the United States datasets and a \emph{mahalle} in Istanbul."

and `:57-61`:

> "The distinction between these targets is not cosmetic. The number of candidate places runs to tens of thousands, whereas there are seven categories and, depending on the dataset, from a few hundred to several thousand regions, so the tasks differ in difficulty, in the baselines that apply, and in what a correct answer means."

The chapter's own ledger scopes the counts out (`:119-120`): "region counts stated qualitatively here;
exact per-dataset counts belong to Ch.5, not Ch.2."

**WHY.** Three separate things, one location:

1. **No justification of the unit, anywhere in scope.** A census tract and a mahalle are
   administrative units defined for census enumeration and municipal administration, not for mobility.
   The document's strongest defence of the choice is Chapter 5's *service* framing
   (`03_problem.tex:13`: "A census tract is a neighborhood, not a radio cell", with radio-level
   decisions scoped out) and `02_related.tex:69-71`, which says the standard formulation uses a grid
   cell and that "our next-region task substitutes official neighborhood-scale units for grid cells."
   That is a substitution stated, not argued. §2.1 introduces the unit with no argument at all. The
   defence question is direct and predictable: why an administrative partition rather than a grid or a
   data-driven partition, and what does the choice cost in comparability against the grid-cell
   literature? Persona lens 7 asks for the construction to be justified; §2.1 is where that belongs,
   and it is absent. The author owns which answer to give.
2. **`mahalle` is used in §2.1 without a gloss.** `2_fundamentals.tex:55` italicizes it and stops.
   Chapter 5 glosses it at `03_problem.tex:13` ("the \emph{mahalle}, a municipal neighborhood") and
   `chapters/1_introduction.tex:63` and `:193` also use it bare. WRITING_LAW §1 requires one definition
   at first use, and GLOSSARY §3 *region* says "name the unit at first use". In the volume's reading
   order the first use is Chapter 1; the *fundamentals* chapter, whose job is to define terms once,
   passes it through ungLossed too.
3. **"tens of thousands" of candidate places has no source pointer in the ledger.** §2.1's ledger
   (`:119-120`) lists the quoted numbers as "only 93% ..., 'seven categories', region counts" and does
   not account for this quantity. It is in fact supported by `tables/mobiwac/datasets.tex:30-35` (POIs
   11,848 at AL to 169,145 at CA), which the sentence does not point at. Under N3 every numeral needs a
   ledger line; a magnitude claim in words is still a numeral claim, and this one is the load-bearing
   half of the "not cosmetic" argument.

**FIX.** (a) Add two clauses to §2.1 justifying the region unit: an official partition is what a
service can act on and what census covariates attach to, and it is the substitution for the
literature's grid cell that `02_related.tex:69-71` already names, with the comparability cost stated.
(b) Gloss `mahalle` at `:55` with Chapter 5's own words, "a municipal neighborhood". (c) Add the POI
count range to the §2.1 ledger, or point the sentence at Table 5.1. Item (a)'s content is the author's
call; (b) and (c) are mechanical.

---

### 4. SHOULD-FIX - the reader is never given the revisitation intuition, and the one number that supplies it sits in Ch.5 attached to a different argument

**WHERE:** `src/chapters/2_fundamentals.tex:734-744` (the reference-points paragraph) and
`:643-649` (the Acc@10 definition). The number that would do the work:
`src/chapters/5_mobiwac/06_results.tex:301-302`.

**WHAT.** §2.4 `:734-737`:

> "Every metric is read against reference points. The majority-class floor, which always predicts the most frequent category, is the level a learned category model must clear. A first-order transition model, a mobility Markov chain over the training partition, is the corresponding non-learned floor for the sequential targets \cite{gambs2012mmc}."

Chapter 5, in the paragraph reconciling the floor against the external systems (`06_results.tex:299-302`):

> "Those windows advance one visit at a time, so the region of the last visit is a strong predictor of the next one, and a first-order transition table reads exactly that signal. At Alabama the target region is the last visited region in $32.9$ percent of windows."

Measured: `revisit|persistence|previously visited|explore` returns nothing in §2.1-§2.5 live prose and
nothing in Chapter 5 outside that paragraph (the two hits in `02_related.tex` are the words "revisited"
and "underexplored" in unrelated senses).

**WHY.** Persona lens 4 and attack question 5: on stride-1 windows a large share of both targets is
carried by persistence, and a reader who does not know that misreads every absolute Acc@10 in the
document. Chapter 5 has the number and states the mechanism, but deploys it defensively, to explain why
a non-learned floor beats three published systems. §2.4 defines the floors as things a model "must
clear" without telling the reader *why* a first-order table is strong here. The information is in the
document; its placement means the frame's reader meets Acc@10 (`:643-649`) with no sense of what an
easy fraction of the task looks like.

Note that §2.4 is scrupulous where it matters most: the Song et al. bound is explicitly refused as a
ceiling on these label spaces (`:738-741`, "it is not, however, a ceiling on seven-class category
macro-F1 or on region ranking, which are different label spaces"), and the operative ceiling is named
as the dedicated single-task model (`:742-744`). That is the correct treatment and it is why this
finding is should-fix rather than blocker.

**FIX.** One clause in §2.4's reference-points paragraph, quoting Chapter 5's mechanism sentence, not
its number: on windows that advance one visit at a time, the previous region is itself a strong
predictor, which is why the first-order transition floor is high and why absolute Acc@10 must be read
against it. If the author wants the 32.9 percent figure in the frame, it is quotable from
`06_results.tex:301` with its scope (Alabama, that windowing) attached; under N1 I would leave the
number in Ch.5.

---

### 5. NIT - §2.4 names Acc@10 as the primary region metric without justifying K, in a chapter whose own argument makes K a scoping decision

**WHERE:** `src/chapters/2_fundamentals.tex:643-647`. Counterpart:
`src/chapters/5_mobiwac/05_setup.tex:129-131` and the margin rationale at `:134`.

**WHAT.** `:643-647`:

> "For next region, the primary metric is accuracy at 10 (Acc@10), the fraction of cases where the true region appears in the model's ten highest-ranked predictions; it is a ranking metric and says nothing about the probability mass placed on the true region, so a model can rank the true region tenth as cheaply as first."

**WHY.** The limitation of the metric is stated well and honestly; what is missing is why ten, when
the label space ranges from 520 to 8,501 classes and the frame itself insists (§2.1 `:57-61`) that
cardinality changes what a correct answer means. Ten of 520 is roughly one in fifty of the space; ten
of 8,501 is roughly one in eight hundred and fifty. Chapter 5 supplies the adjacent argument for the
*margin* (`05_setup.tex:134`: a service "acts on which region will be busy, not on a single rank
position"), which is exactly the reasoning that would justify a shortlist of ten, and Chapter 5's
discussion (`07_discussion.tex:68-71`) treats the top ten as an anticipatory set. §2.4 never borrows
it. Persona lens 8 asks for K justified. Nit rather than should-fix because the document does not
compare Acc@10 across datasets as if it were commensurable: `06_results.tex:384-385` states the
opposite outright ("The comparable quantity is the gain over the ceiling, not the absolute Acc@10,
since region counts differ across datasets").

**FIX.** Half a sentence at `:643`: ten is the size of a shortlist a service can act on, which is
also the basis of the two-point margin in Chapter 5, and the quantity compared across datasets is the
gain over the dedicated model rather than the absolute Acc@10.

---

## Credibility signals present (verified in the text, at these locations)

These are the defences the persona file says the dissertation holds; I confirmed each is **stated**,
not merely true in the repo:

- **Three-task distinction held cleanly.** §2.1 `:50-63` defines all three and closes with "It does
  not predict the exact next place; that target is named only to hold it apart from the two the
  dissertation studies." §2.1 `:79-80` closes the next-place lineage paragraph with "every model named
  in this paragraph predicts the exact next place." Chapter 5 repeats the disclaimer at
  `03_problem.tex:13` and `02_related.tex:65-66`. I found **no** conflation of the three anywhere in
  the scope I read, including where it would be easiest to slip: `06_results.tex:282-293` compares
  against place-targeted systems and says what was dropped from each (`05_setup.tex:156`: HMT-GRN's
  "graph components and hierarchical beam search, which exist to serve its next-place target, a target
  that we do not predict"). This is the single strongest thing in the scoped text.
- **The place-level/check-in-level argument is correct as a mobility claim**, and is argued rather than
  asserted: §2.2 `:192-201` states the static-vector property and why it matters, and grounds it on
  CTLE `\cite{lin2021ctle}` as prior evidence rather than on the dissertation's own result. The
  qualification that HGI is repurposed from a region-representation method (`:164-167`) and retuned
  (`:167-174`, cross-region weight 0.4 to 0.7) is exactly the disclosure a domain reviewer looks for
  and is rare in this literature.
- **Split axis stated and its strengthening disclosed**, including the weaker earlier protocol:
  `2_fundamentals.tex:752-755` ("Chapters 3 and 4 both stratify by sample rather than by user, so that
  the check-ins of one user may appear in both training and validation, and only Chapter 5 splits by
  user"), and the statistical scoping at `:767-770`.
- **Overlap-cannot-leak stated at Chapter 5**: `05_setup.tex:32`.
- **Transductive audit with coverage and residual**: `05_setup.tex:68` (per-fold rebuild moves both
  tasks "by at most a third of a point ... at Alabama, Arizona, and Florida", coverage "67 to 87
  percent", and the unseen-places residual named as the part it cannot reach), with the three limits at
  `:89` (linear probe, Florida at one initialization, ancestor builds).
- **Per-fold transition prior with the cautionary record**: `05_setup.tex:70` (built per fold "after an
  earlier whole-dataset version inflated region accuracy by 13 to 27 points"), plus the statement that
  our models do not use it and HMT-GRN does.
- **Baseline provenance at the point of comparison**: `05_setup.tex:156` gives each baseline its own
  sentence (re-implemented / same folds but own embeddings and sequences / own published protocol), and
  the results table repeats the asymmetries in its own footnote (`tables/mobiwac/results.tex:59-64`:
  STAN partial folds TX 4/5 and CA 2/5, ReHDM single seed at TX and CA).
- **Song et al. refused as a ceiling on these tasks**: `2_fundamentals.tex:738-744`, and rescoped in
  §2.1 at `:35-39`.
- **Label-cardinality tabled** and the region-count column ordering the results:
  `tables/mobiwac/datasets.tex:30-35`, with `03_problem.tex:13` giving the range in prose.
- **Dataset vintage stated as a limitation**, with the extraction range distinguished from the cited
  authors' collection range: `chapters/6_conclusion.tex:249-251`.
- **Selection optimism admitted outright**: `07_discussion.tex:74` ("epoch selection consults the fold
  that the score is then read on ..., so every absolute score reported here is optimistic"), including
  that the four seeds reuse one fixed fold partition.
- **Code and data released**: `01_introduction.tex:27` footnote (repository plus both public sources).

## Unstated defenses (facts the repo or a neighboring chapter holds that the scoped text does not carry)

Each of these is a finding above; collected here as the persona's output contract asks.

1. Window construction and the overlap-cannot-leak licence: in `05_setup.tex:30,32`, absent from §2.4 (finding 1).
2. Transductivity of the representation and the audit: in `05_setup.tex:64-75`, absent from §2.2 and §2.4 (finding 2).
3. The region-unit substitution argument: partly in `02_related.tex:69-71` and `03_problem.tex:13`, absent from §2.1 (finding 3a).
4. The `mahalle` gloss: in `03_problem.tex:13`, absent at first use in §2.1 (finding 3b).
5. Region persistence on stride-1 windows: in `06_results.tex:301-302`, absent from §2.4 (finding 4).
6. The shortlist rationale that would justify K = 10: in `05_setup.tex:134`, absent from §2.4 (finding 5).

## Scope comment (asked for by the brief)

The narrowing was right for the clock, with one consequence worth recording: four of my five findings
are *frame-versus-chapter placement* defects, i.e. Chapter 5 carries a defence that §2.1/2.2/2.4 does
not. That class is only visible when both halves are in scope, and this brief had both. It would have
been invisible to a Chapter-5-only or a Chapter-2-only reviewer. If a later round narrows further, keep
one persona holding both ends.

I found **no blocker** in the scoped text. I looked specifically for the defects that kill this kind of
work at a defense and did not find them: no cross-cardinality Acc@K comparison, no next-place claim
smuggled in through category or region, no undisclosed protocol asymmetry at a point of comparison, no
verb unbound from its test in the scoped prose, no absolute number presented without a reference point.
Saying so is the result, per rule 5.

---

## COUNTS

**blockers: 0 / should-fix: 4 / nits: 1**

## UNFINISHED

The following were in my scope or adjacent to it and I did **not** reach them. I ran out of the
30-minute checkpoint at 11:53Z (start 11:41Z) and stopped, per instruction.

1. **The PDFs were not opened at all.** Every finding is against the LaTeX source at commit
   `901a0408`. I did not verify that the passages I quote render as quoted on `src/build/main.pdf`
   pp. ~59-75, and I did not check Chapter 5's figures (`fig1_dataflow`, `fig3_embquality`,
   `fig4_deltas`) or the rendered tables for anything a domain reader would object to. The brief gave
   PDF pages as an acceptable location form and I used source locations instead; a page-level
   re-verification is owed if the author wants one.
2. **No citation was resolved against Crossref, arXiv or a publisher record this session, and I assert
   nothing about any reference's existence or attribute fidelity.** In particular I did **not** check
   `gambs2012mmc`, `kohavi1995crossval`, `sokolova2009measures`, `wongso2025massivesteps`,
   `zhu2022drrgnn`, `capanema2023poirgnn`, `sun2025kgtb` or `li2025rehdm`, and I did not verify that
   any citing sentence in §2.1/2.2/2.4 is supported by its source. Two ledger flags I *read* but did
   not adjudicate, listed so they are not lost: the `[VERIFY: averaging convention of the swept "Cat
   F1"]` at `2_fundamentals.tex:188-190`, and the `kohavi1995crossval` "claim PLAUSIBLE (Zenodo
   re-deposit id)" note at `:833-834`. Both are the citation auditor's remit, not mine, but both sit
   inside my scope's prose.
3. **The must-cite canon was not audited for coverage.** I did not check the presence or positioning
   of Dacrema (arXiv:1907.06902), Sanchez & Bellogin (doi:10.1145/3510409), POI Pitfalls
   (arXiv:2507.13725), the mie-lab benchmark (arXiv:2212.01953), Pappalardo 2015, FPMC, LSTPM,
   Graph-Flashback, STHGCN, CSLSL as a *canon* entry, ROTAN, or the LLM-era next-location work. The
   persona file asks for a presence/positioning check and I did not run it. My impression from what I
   read is that the evaluation-critique canon is thin in §2.4 (I saw no critique-canon citation in the
   protocol or metrics paragraphs), but I did not sweep the bibliography, so that is an impression and
   not a finding.
4. **No number in Chapter 5 was traced to its source of record.** I quoted printed cells only, and
   only to locate arguments. I did not open `docs/studies/closing_data/RESULTS_BOARD.md`,
   `PAPER_PLAN.md §3`, `A4_RESULTS.md`, or any JSON, and I recomputed nothing.
5. **Persona lens 5 (baseline re-implementation fairness) was read but not pressed.** I confirmed each
   baseline carries a provenance sentence at `05_setup.tex:156`; I did not check whether the
   re-implementations used the same stride, min-sequence-length or padding policy as the proposed
   model, which is the field trap that lens names. That check needs the released code, which I did not
   open.
6. **Cold-start handling (lens/attack question 10) was only partially checked.** I found the
   unseen-region convention (`05_setup.tex:131`, absent regions count as errors) and the unseen-places
   residual (`:68`, `07_discussion.tex:74`); I did not establish how unseen *users* are handled under a
   user-disjoint split, nor whether that handling is quantified anywhere.
7. **§2.3, Chapter 3 and Chapter 4 were not read**, per brief. Their MTL and protocol content is
   persona 10's and the concordance reviewer's remit. My finding 1 touches
   `chapters/4_courb/methodology.tex:95` for the non-overlapping-window contrast only; I read that one
   line and nothing else in Chapter 4.


---

<!-- estado-rodada -->
> **Rodada encerrada · último toque 2026-07-30 · sem autoridade.**
> Este ficheiro é registo de proveniência do que foi discutido nesta passagem, não fonte
> de um facto corrente. O que ficou decidido está em [`VEREDITOS.md`](../../../../VEREDITOS.md);
> os valores entregues estão em `CLAUDE.md` §0.1. Não copie nada daqui sem confirmar lá.
