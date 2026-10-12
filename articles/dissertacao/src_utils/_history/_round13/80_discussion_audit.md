# 80 · Audit of §7 "Discussion and Limitations" (MobiWac chapter), claim by claim

**Round 13 · 2026-08-05 · READ-ONLY.** No `.tex` file was edited. `PENDENCIAS.md`, `ERRATA.md`,
`LEFT_OUT.md` and `NEEDS_SIGN_OFF.md` were not edited. This report proposes; the author decides.
No replacement prose is drafted, per the author's law.

**Repo root for every path below:** `/Users/vitor/Desktop/mestrado/ingred`.

**Both copies read fresh from disk this session, with `%` comments stripped (V4):**

- dissertation: `articles/dissertacao/src/chapters/5_mobiwac/07_discussion.tex` (168 lines raw,
  14 live sentences)
- submitted paper: `articles/[mobiwac]/src/sections/07_discussion.tex` (80 lines raw)

**V3 / V4 instrument validation, run before any verdict below.** The comment-stripping reader must
be able to SEE a retracted string in a comment and HIDE it from the live text; a stripper that
returns nothing everywhere is indistinguishable from a clean file.

```bash
for f in articles/dissertacao/src/chapters/5_mobiwac/07_discussion.tex \
         "articles/[mobiwac]/src/sections/07_discussion.tex"; do
  for pat in "The gain is substantial" "fixed fold partition"; do
    printf "%s %-28s raw=%s stripped=%s\n" "$f" "$pat" \
      "$(grep -c "$pat" "$f")" \
      "$(grep -vE '^[[:space:]]*%' "$f" | grep -c "$pat")"
  done
done
```

Result, copied from the run: on the **dissertation** copy `"The gain is substantial"` is
`raw=1 stripped=0` (the instrument sees it in the comment block and correctly removes it from live
text); on the **paper** copy the same string is `raw=1 stripped=1` (live there). `"fixed fold
partition"` is `raw=0 stripped=0` in both, which is a real absence rather than a blind instrument,
because the same reader resolved the other pattern in both directions on the same two files.

---

## 0 · THE FINDING THAT COMES BEFORE THE SENTENCE LIST: the two copies are NOT in sync

The standing policy for this chapter is that the dissertation copy and the submitted paper source
stay identical (`articles/dissertacao/src/tables/mobiwac/errata_scope.tex`, and `ERRATA.md:60-62`,
`:248-251`). **They are not, and the divergence is in the section under audit.** Measured on live
text only:

| | dissertation §7 | paper §7 |
|---|---|---|
| live characters | 2,577 | 2,931 |
| the three-sentence mechanism passage ("The gain is substantial … not settled by the controls reported here") | **commented out** at `:18-23` under the marker `%[AUTHOR COMMENT]` | **live** at `:16-19` |

The commenting-out landed today, in `71d119ce` ("fix(protocol): the fold partition is drawn per seed,
not fixed at 42"), whose own diff shows the three sentences moved from live text into a
`%[AUTHOR COMMENT]` block in the dissertation copy **and left untouched in the paper copy**
(`git show 71d119ce -- articles/dissertacao/src/chapters/5_mobiwac/07_discussion.tex`, and the
corresponding paper hunk, which only re-wraps lines and adds the audit note). That commit's message
does not mention the change; its declared scope is the fold/seed correction across five files.

Two consequences the author needs before rewriting:

1. **The mechanism passage is the subject of a closed sign-off (NEEDS_SIGN_OFF 28, closed
   2026-08-05) whose recorded outcome is the softened three-sentence wording in BOTH texts**
   (`src_utils/_history/NEEDS_SIGN_OFF.md:1532-1536`, and `ERRATA.md:212-220` which logs the same edit for
   the paper). Commenting it out of the dissertation is a third state that neither the sign-off nor
   the errata records.
2. A parallel editing lane was active in this tree today. I cannot establish from the repository
   whether the comment-out was intentional; the `%[AUTHOR COMMENT]` marker suggests it was a
   deliberate parking of the passage for the author's attention, not an accident.
   **[VERIFY: whether the `%[AUTHOR COMMENT]` block at `07_discussion.tex:18-23` is a deliberate
   removal the author wants, or a parked edit. If deliberate, the paper copy at `:16-19` must
   follow, and `ERRATA.md` entry 2 of the 2026-08-05 block must be amended, because it currently
   records the opposite.]**

The sentence list in Part 4 is numbered over the **dissertation** live text (14 sentences). The
paper's three extra live sentences are audited as items 1a-1c.

---

## PART 1 · TRACE EVERY NUMBER

### (a) "at California, ten regions out of 8,501 contain the true next region 65.69 percent of the time"

**Status: TRACED — every component sourced. Scope clause: INCOMPLETE (one convention missing).**

| component | source, file:line, opened this session |
|---|---|
| `8{,}501` regions at California | `articles/dissertacao/src/tables/mobiwac/results.tex:53` (region block, CA row) and `:35` (category block); dataset table `src/tables/mobiwac/datasets.tex:35` |
| `65.69` | `src/tables/mobiwac/results.tex:53`, the CA joint region cell: `\textbf{65.69}\sd{0.02}$^{\uparrow}$` |
| the cell's convention | same file `:49-50`: "Joint and dedicated entries: four seeds $\times$ five folds; $\pm$: sd across seeds" |
| what Acc@10 counts | `src/chapters/5_mobiwac/05_setup.tex:201-202`: "the fraction of test visits whose true region appears among the model's ten highest-scoring guesses (a visit whose true region is absent from that fold's training data counts as an error)" |
| independent confirmation of the cell | `docs/studies/closing_data/RESULTS_BOARD.md:30` (`CA (8501) … 65.69±0.02 … n=20`) and `:37` (`CA … reg 65.693 ±0.017`); whitelist `articles/[mobiwac]/PAPER_PLAN.md §3` "Joint reg cells: … CA 65.69" |

**Consistency with the chapter's own table: YES, exact.** The prose figure is the table cell to the
digit.

**The scope gap.** The prose says "contain the true next region 65.69 percent of the time" with no
convention. `WRITING_LAW.md §3` requires every number to carry its reference point *and* its
convention (metric, selection rule, n). Here the metric is implicit (Acc@10, defined two sections
earlier), the selection rule is the joint-best convention, and n is four seeds × five folds. The
adjacent sentence [3] *does* carry its convention ("a single seed over five folds"), which makes the
asymmetry visible to a reader: two numbers side by side, one with its footing and one without. Note
also that "contain the true next region … of the time" silently converts a per-visit accuracy into a
frequency statement about a shortlist, which is a fair reading of Acc@10 but is not the metric's own
wording.

### (b) "over 500 times better than picking ten at random"

**Status: THE RATIO IS NOT STATED BY ANY SOURCE OF RECORD FOR THIS CHAPTER. It was computed, and
the source it was computed from is a superseded value. §2 (N2) violation. RECOMMEND DELETE.**

Four separate defects, each with its own evidence (V13 — reported per claim, not pooled):

1. **The ratio is a derived quantity, and `AGENT_GUARDRAILS §2 N2` forbids exactly this**: "No
   mental arithmetic, rounding, aggregation, percentage conversion, or delta-taking in prose.
   Derived quantities come from a script committed to the repo … then are quoted." The only place in
   the repository that states an enrichment ratio for California is a **planning document**, not a
   results record: `articles/[mobiwac]/MOBILITY_SCIENCE_BRIDGE_PLAN.md:77-84`, a table headed
   "enrichment over chance" giving `California | 8,501 | 65.66% | 0.12% | ≈547×`. `:88-93` of that
   same file is the "Ready-to-paste replacement" sentence containing the phrase "more than five
   hundred times better than picking ten at random". So the prose descends from a *proposal* in a
   plan file, not from a measurement record. `docs/studies/closing_data/RESULTS_BOARD.md` (the
   chapter's declared single source of truth, `AGENT_GUARDRAILS N1`) contains no such ratio;
   `grep -rn "547\|five hundred"` over the article tree returns only the plan file, this same phrase
   at `:442` and `:717`, and the analysis note below.

2. **The ratio was computed from a value the paper has since superseded.** The plan's 547× uses
   `65.66%`, the seed-0 five-fold California figure. The chapter reports `65.69` (n=20). The prose
   now pairs the *new* numerator with a ratio derived from the *old* one. The two happen to round
   the same way, which is precisely why this survived: an unreconciled derivation that lands in the
   right place reads as verified.

3. **The denominator is a floor this project's own record tells the reader NOT to use.**
   `articles/[mobiwac]/BRIDGING_METRICS.md:21-22`: random top-10 = 10/n_regions, and then, in the
   file's own words, "The headline reg Acc@10 (~60–77) should be read against the **Markov-1
   floor**, not the ~1 % random floor." I opened the underlying JSON and counted the cell rather
   than trusting the table (V8): `docs/results/P0/simple_baselines/california/next_region.json`
   gives `aggregate/random/acc10_mean = 0.0011768859597505001` and, in the same file,
   `aggregate/markov_1step_region/acc10_mean = 0.5208956360464413`. Against the Markov-1 region
   floor the chapter itself adopts, California's joint cell is not a multiple of 500; the ratio
   exists only against the floor the project retired. `05_setup.tex:200-203` states the region
   metric's reference point as "the dedicated model", not a random draw.

4. **The section's own results text already states the random-draw comparison, differently and with
   a hedge.** `src/chapters/5_mobiwac/06_results.tex:45-47`: "a random region top-ten guess is right
   at most about two percent of the time". That is the *maximum across datasets* (Istanbul, 1.92%,
   `BRIDGING_METRICS.md:19`), stated as a bound. §7's ratio takes the same floor at a different
   dataset and turns it into a multiplier without saying so.

**One thing this finding does NOT establish**, and it matters for the rewrite: the underlying
*enrichment* observation is real and computable; what is unsourced is the specific ratio "over 500
times", stated in prose as if quoted. The honest options are to delete the clause, or to state the
random floor as a value with its source and let the reader see the scale — the second is a new claim
and needs the author's sign-off (`C2`).

**A recorded honesty flag already anticipated this whole sentence.**
`../../../science/storyline/archive/PROCESS_REVIEW.md` (seccao `06_honesty_under_pressure/honesty_flags.md`, flag F7)
(= `handoff/STORY_REVIEW.md:520-525`, flag **F7**): the "65.69%, 500× better than random" line is
named as a *temptation*, ruled usable as motivation only if it carries its convention and the "not a
measured service result" hedge, and marked **[VERIFY at adaptation]**. The [VERIFY] was never
discharged for the ratio.

### (c) "the ten shortlisted regions lie a median of 3 to 8 kilometers from the shortlist's centroid, against 17 to 176 kilometers for ten regions drawn at random from the same candidate set (median over 10,000 draws)"

**Status: TRACED, and the scope clause matches the source. This is the best-sourced number in the
section. Two sub-clauses need care.**

Source of record: `articles/[mobiwac]/analysis/shortlist_compactness_RESULTS.md`, the "Matched
random comparator" block added 2026-07-20, `:149-201`. I did not stop at its table — I opened the
JSON and counted the cells in the column the prose came for (V8):

```python
# articles/[mobiwac]/analysis/shortlist_compactness_matched.json  -> matched/<state>/centroid_spread_mean_km/p50_km
istanbul 16.6406   arizona 87.7855   alabama 135.9728   florida 176.1644     (n_draws = 10000 each, seed 0)
# articles/[mobiwac]/analysis/shortlist_compactness_<state>.json -> pooled/in_distribution/centroid_spread_mean_km
istanbul p50=2.8583 (n=271,486) | arizona 6.0927 (200,372) | alabama 6.2368 (95,799) | florida 7.5289 (1,273,246)
```

- **"3 to 8 kilometers":** the four in-distribution medians are 2.86 / 6.09 / 6.24 / 7.53, so the
  stated range is a correct rounded envelope (2.86 rounds to 3, 7.53 to 8). The prose does not say
  "in-distribution", and the record insists the two subsets are "reported SEPARATELY, never pooled"
  (`shortlist_compactness_RESULTS.md:7-8`); the OOD medians are 3.66 / 14.00 / 12.55 / 11.99 and
  would break the range. The counts are small (180 / 523 / 527 / 1,172 visits) but the omission is a
  scope clause, not a rounding question.
- **"17 to 176 kilometers":** 16.64 rounds to 17 and 176.16 to 176; the source's own reading uses
  exactly this phrasing (`:188`, "now \"17 to 176 km\"").
- **"median over 10,000 draws":** `n_draws = 10000`, `seed = 0`, "uniform without replacement",
  confirmed in the JSON per state.
- **"a single seed over five folds":** matches the record's provenance (`:26-29`, seed 0 × 5 folds)
  and its Istanbul caveat (`:38-49`).
- **"from the same candidate set":** the record says **pool** — "the model's candidate-region
  vocabulary (`checkin_graph.pt` `region_to_idx` joined to `boroughs_area.csv` polygon centroids)"
  (`matched.json` `pool` field, and `:163-167`). The drafted sentence at `:197-201` says "candidate
  pool"; the live prose says "candidate set". Harmless in meaning; worth knowing the source word
  differs, because "candidate set" is not a registered term (Part 3, glossary).
- **The comparator is symmetric, and that was a deliberate fix.** `:149-157` records that an earlier
  version of this sentence compared a ten-region shortlist against a **two-region** random pair
  (the 20-241 km figure), that a readability reviewer flagged the asymmetry, and that the author
  ruled it be recomputed as ten random regions. A rewrite must not reach back for "20 to 241".
- **Reproduce-first gate:** `:169-176` records that the two-region floor recomputes bit-exactly from
  local inputs and the shortlist side verifies against its recorded JSON. I confirmed the four
  `pair_floor_recomputed` values against `pair_floor_published` inside the JSON itself; they agree.

**Consistency with `docs/studies/closing_data/`:** none of (c) lives there. This metric is an
`articles/[mobiwac]/analysis/` product, not a board cell, which is consistent with its status as
motivation. `RESULTS_BOARD.md` is the source of truth for (a) and it confirms it.

---

## PART 2 · THE LEAKAGE CHANNEL: is its absence from §7 a defect?

### (i) Verdict: **GENUINE GAP.**

Three facts establish it, each with its own evidence.

1. **§7 claims completeness.** Sentence [5] is "Three limits qualify these results." A closed
   enumeration is a completeness claim; `ERRATA.md:73-80` records that this paragraph was *changed
   from "Two limits" to "Three limits"* precisely to add a disclosed threat that was missing, which
   establishes that the count is treated in this project as the paragraph's own inventory of
   threats.
2. **The channel is disclosed in the same chapter as a threat to validity, in the author's own
   voice.** `src/chapters/5_mobiwac/05_setup.tex:82-84` (live, comment-stripped): "In the Check2HGI
   graph, each visit node is linked to the visit that follows it. Because category is a node input
   feature, the vector of an earlier visit could absorb the category of the next one." The screen is
   at `:84-88`, its numbers at `:90-94`, and its **three stated limits** at `:125-129`: "The probe is
   linear, was run only at Florida with one random initialization over five user-grouped folds, and
   evaluated ancestor builds of Check2HGI rather than the build that produced the reported results.
   Passing this screen therefore bounds only the information exposed by a linear read. It does not
   establish what a nonlinear sequence model could recover."
3. **§7 mentions none of it.** Measured on live text: zero occurrences of "consecutive", "node",
   "probe", "screen", "absorb", or "linear" in the live §7 of either copy. The one limit §7 *does*
   raise about the representation is a **different** channel — sentence [6], places unseen during
   training (transductive), which `src_utils/_history/_round13/72_leak_screening_search.md` explicitly
   separates from the forward edge: the transductive record is A4, "a different channel from the
   forward edge".

Two further records make the gap sharper rather than softer:

- `src_utils/_history/_round13/71_graphnode_features.md` establishes, measured with a validated instrument,
  that the category one-hot *is* columns 0-6 of the check-in node feature vector, and (at `:216-217`)
  that the forward adjacency is present at Alabama in 96,326 windows with 0 not adjacent. That is
  evidence the channel is **open**, not that it leaks.
- `72_leak_screening_search.md`'s one-line answer: the screen "does **not** establish that the graph
  channel carries no usable next-category information, and by its own recorded finding the linear
  form of the screen is provably able to miss a leak" — the record it cites,
  `docs/results/embedding_eval/rescreen_cat/RESCREEN.md:94-95`, notes the linear gate **missed** one
  leak.

**The counter-argument, stated so the author can weigh it:** §7 of a submitted paper is a
half-page, the channel is disclosed at length in §5 with its limits, and one could argue §7's
"Three limits" enumerates the limits *of the results* while §5 enumerates the limits *of the
integrity audit*. That reading is available. It is weakened by the fact that the enumeration already
contains one representation-integrity limit (sentence [6]), so the paragraph's scope demonstrably
includes that class of threat.

### (ii) The narrowest closing sentence — its BASIS, not its wording

I do not draft it (the author's law reserves the prose). What I can state is the exact material a
one-clause addition may draw on without inventing a claim, all of it already live in `05_setup.tex`:

- the mechanism, `:82-84`: each visit node is linked to the visit that follows it; category is a
  node input feature; the vector of an earlier visit **could absorb** the category of the next one
  (modal, not asserted);
- that it was **screened during development** with a **linear probe** on the last vector of each
  window, `:84-86`;
- the three limits at `:125-129`: linear probe; Florida only, one random initialization over five
  folds; **ancestor builds** rather than the build behind the reported results;
- the bounded conclusion the chapter already permits, `:128-129`: passing the screen "bounds only
  the information exposed by a linear read" and "does not establish what a nonlinear sequence model
  could recover".

Anything beyond that set — a quantified leak, a statement that the channel does not leak, a
statement that it does — is a new claim requiring `C2` sign-off. The safe form is a pointer plus the
residual, i.e. name the channel, name that it was screened, and carry the "bounds only a linear
read" limit; the cross-reference target already exists (`sec:mobiwac:setup-windows`, the label §7
sentence [8] already cites).

---

## PART 3 · WHAT ELSE FROM THE DISSERTATION BEARS ON §7

### 3.1 · The fold/seed finding of today — "the selection rule is the same for both models on the same folds"

**CONFIRMED TRUE as written.** The author's reading is correct, and it is correct for the reason he
gives (within-run comparison), which I verified against the primary record rather than the audit
note that asserts it.

- `science/fold_partition_and_seeds.md §7`: "Pairing the joint model against the dedicated model
  WITHIN one seed is still sound, because both arms run under the same seed and therefore the same
  partition. What is not available is the assumption that fold k of seed 0 is fold k of seed 1."
- `GLOSSARY.md §3`, seed row: a seed sets initialization **and** partition; "within one seed the
  compared models read the same folds"; the ban is on "'same folds' as a property **across** seeds
  (it holds only within a seed)". §7's clause is scoped to the two models, not across seeds, so it
  falls on the permitted side of that ban.
- The corrected `05_setup.tex:205` now states the same thing in the seed definition: "within a seed
  both models read the same folds".

**Any OTHER sentence in §7 that assumes a fixed partition: NONE.** Measured on live text of both
copies: zero occurrences of "partition", "resampl", "initializat", "seed 42", and "42".
**Correction to my own first pass, recorded rather than silently fixed:** I first wrote that "fixed"
was also zero. It is **2** in each copy, and I had to read both to clear them — sentence [9]'s "one
configuration held fixed across all six datasets" (a hyperparameter configuration, not a data split)
and sentence [13]'s "a fixed per-visit vector" (not re-trained per consumer). Neither is a partition
claim, so the verdict stands, but a count I published as zero was wrong; the positive control on the
same instrument returns fold 5, seed 1, region 7, dedicated 4, so the zeros above are real absences.
The only seed reference in live §7 is "a single seed over five folds" in sentence [3], which is a
statement about the shortlist study's own repetition count, not about the partition — and it is
correct against `shortlist_compactness_RESULTS.md:26-29`. Sentence [9]'s "on the same folds" is the
one occurrence of the concept, and it is the one just confirmed.

**A consequence for the rewrite, from the corrected record.** `ERRATA.md:294-298` now states that
the reported intervals **do** cover split-resampling variability (each seed resamples the split),
bounded by "four draws sample that variability rather than characterize it". §7 makes no claim about
what the intervals cover, so nothing in it is falsified — but a rewrite that reaches for a
"what the intervals cover" sentence must use the corrected form, not the pre-2026-08-04 one, and see
3.5 below before adding any such sentence at all.

### 3.2 · The Istanbul data window (two blocks, 2012-2013 and 2017-2018, ~70.7% in the earlier block)

**Bears on §7 only indirectly; §7 makes no recency or generalization claim it contradicts.**

- Live §7 mentions no dataset vintage, no recency, and no generalization-to-today claim (zero
  occurrences of "recent", "modern", "2012", "2017", "current").
- The finding is already carried where it belongs: `src/chapters/6_conclusion.tex:302-307`, the Data
  vintage limitation — Gowalla "January 2009 to August 2011", and Istanbul "not appreciably more
  recent for most of its volume: its check-ins fall in two separate periods, 2012 to 2013 and 2017
  to 2018, with none in between, and roughly seven in ten belong to the earlier period"
  (source record: `src_utils/_history/_round13/70_massivesteps_validation.md`, which measured the on-disk
  window as 2012-04-03 to 2018-10-19 and 70.7% in the earlier block).
- **Where it does touch §7:** sentences [2]-[4] motivate a present-day mobility-aware service on
  data whose newest block is 2018 and whose bulk is 2012-2013, and sentence [3]'s comparator is
  built from Istanbul among four datasets. This is a *reading* risk, not a false statement, and
  sentence [4] already hedges it as motivation. I recommend NOT importing the vintage limitation
  into §7: it is a chapter-level limitation the frame already states, and duplicating it here would
  trip the cross-chapter duplication rule (`L3`). Recorded so the author can decide, not flagged as
  a defect.

### 3.3 · Gradient orthogonality (Appendix F) and the nineteen-balancer screen

**§7 draws no mechanism conclusion, and should not start.** This is the correct state, and the
reason is worth stating so a rewrite does not "improve" it:

- `apx_f_cosine.tex:100-101` states the gradients are "statistically indistinguishable from
  orthogonal on every dataset measured", and `:456`, `:473` bound what that explains: it explains
  why a balancer had nothing to resolve, and "says nothing" beyond that.
- `GLOSSARY.md §4`, gradient-conflict row: define it in §2.3, "**report no value there**", and
  "Never call a near-zero cosine 'no conflict detected' where the appendix's equivalence test
  supports the positive statement".
- The mechanism question §7 currently touches (in the paper copy, and in the commented block in the
  dissertation copy) is the *locus of the category gain*, which four experiments constrain — the
  cross-attention ablation at Florida (−0.04 ± 0.13, paired Wilcoxon p = 0.6250), the zeroed-mixing
  arm, the category-weight sweep, and the cascade arm (`ERRATA.md:222-228`). The settled position,
  recorded twice (`ERRATA.md:212-228`, `NEEDS_SIGN_OFF.md:1525-1536`), is: the gain is a property of
  the **joint architecture**, no component is named, and the freeze control is scoped to **three**
  datasets.
- **Therefore: adding an orthogonality sentence to §7 would be a new claim (C2) AND would risk the
  glossary's "report no value there" rule.** The balancer screen belongs to `02_related.tex:138`,
  where it already lives with its scope (nineteen balancers, one seed, Alabama and Florida —
  `ERRATA.md:90-100`).

### 3.4 · The capacity-matched control and the fixed-region control

**§7 does not attribute the gain to anything those controls exclude — in the DISSERTATION copy,
because the attribution sentence is currently commented out. In the PAPER copy it does attribute,
and that attribution is the one the record supports.**

- The fixed-region control (Ch.6 §6.2 restatement at `6_conclusion.tex:198-207`): it excludes
  region-task **training transfer** as the cause, and explicitly "does not distinguish among the
  category encoder, the feed-forward blocks, the added depth, cross-attention, or a combination".
  Its scope is Alabama, Arizona, Florida — three of six.
- The capacity-matched control (`6_conclusion.tex:218-238`): widening the dedicated category model
  to the joint model's parameter budget recovers **none** of the gain (AL 56.16 ± 1.89 widened vs
  56.82 ± 0.03 tuned vs joint 64.51 ± 0.09; CA 69.88 ± 0.26 vs 70.60 ± 0.07 vs 77.05 ± 0.01). It
  excludes "model size alone".
- The paper copy's live sentence ("a property of the joint architecture rather than of cross-task
  transfer: at the three datasets where the region pathway is held at its initial values") is
  exactly the freeze control's own scope, and names no component. **It is compliant.**
- **A hard boundary the record sets:** `NEEDS_SIGN_OFF.md:1544-1546` records that the
  capacity-matched baseline was deliberately *removed* from this sentence because it is a
  post-submission control **Chapter 5 does not report** — citing it here "would be pointing at the
  void"; it belongs to Chapter 6. A rewrite must not import it into §7.

### 3.5 · Recorded decisions a rewrite must not silently reverse

**This is the load-bearing part of Part 3.** Four decisions, in the author's own record.

**D1 — The fixed-partition caveat was DELETED from §7 on the author's explicit instruction, and the
reason recorded for the deletion was corrected today.** The full sequence, so a rewrite gets it
right:

- The deleted sentence, verbatim from `ERRATA.md:231-233`: *"The four seeds also reuse one fixed
  fold partition, so the reported intervals cover variation across random initializations and not
  across resampled user splits."*
- The author's instruction, verbatim, `NEEDS_SIGN_OFF.md:1575-1576`: *"Essa frase eu acho que tá
  errada, faça uma avalaição nos documentos que temos, pq já verificamos algo realcionado a isso.
  De qualquer forma vamos remove-la por hora, tanto daqui quanto do artigo original."*
- What the agent recorded at the time (`ERRATA.md:236-241`, `NEEDS_SIGN_OFF.md:1578-1589`): the
  sentence was **verified true** before removal, the fixed partition being "the condition for those
  tests rather than a defect in them"; keeping it with that explanation was recommended and
  declined.
- **What today's correction changes, and what it does not** (`ERRATA.md:282-292`): *"THIS ENTRY
  CORRECTS THE RECORD IN ENTRY 3 OF THE PREVIOUS BLOCK ABOVE … That explanation is wrong."* The
  folds were generated per seed, not frozen. **"The deletion itself stands and was the author's
  call; what does not stand is the reason recorded for it."**
- **The consequence for the rewrite: the deleted sentence is now BOTH removed by author instruction
  AND factually false.** Its first half ("reuse one fixed fold partition") is refuted by
  `science/fold_partition_and_seeds.md §7`, which lists that exact wording under MAY NOT; its second
  half understated the intervals. So a rewrite must not reinstate it in any form — not as the
  original sentence, not as a "corrected" version. If the author wants an intervals-coverage
  sentence at all, it is a **new** sentence needing sign-off, and its content is the corrected one
  (each seed resamples the split; four draws sample rather than characterize that variability).
  Note the author's own hedge in his instruction: *"por hora"* — for now. He left the door open;
  walking through it is his call, not a rewrite's.

**D2 — The mechanism attribution was softened and the stronger wording was refused, against the
author's initial request.** `NEEDS_SIGN_OFF.md:1516-1523` is his request to restore *"the shared
trunk carries the semantic context that lifts the next-category task"*; `:1525-1536` is the recorded
outcome — **not restored**, because four studies show the gain survives the trunk's removal, and his
final ruling was *"suavizar, sem desenvolver alem disso por hora"* (soften, and go no further for
now). `ERRATA.md:212-228` logs the same. A rewrite may not name the shared trunk, or any component,
as the source of the category gain.

**D3 — "applied identically" was deliberately narrowed to "is the same for both models on the same
folds … with each model selected on its own validation objective".** `ERRATA.md:139-148`, with the
stated reason: the procedure is shared, the objective is not, and making a mitigation sound stronger
than it is understates a limitation. A rewrite must not re-collapse this to "identically".

**D4 — "arm" is banned; the substitution "both models" / "the dedicated model" is the recorded
one.** `ERRATA.md:66-67` of the 2026-07-27 block and the round-5 comment at `07_discussion.tex:161-163`
(MobiWac GLOSSARY §3: "clinical-trial word, foreign to this audience").

Also checked: `src_utils/LEFT_OUT.md` contains no entry bearing on §7 (the one hit for
"discussion" at `:235` concerns another paper's method). `articles/[mobiwac]/PAPER_PLAN.md:572-576`
authorizes the usage sketch as *"Usage illustration (storytelling, not a claim) … Frame it as
motivation and future work, with no measured number"* — which is worth flagging: the sketch now
carries three measured numbers. Sentence [4]'s hedge is doing the work that the plan expected the
absence of numbers to do.

### 3.6 · GLOSSARY compliance (fail-closed: a term not in the registry may not be used)

`GLOSSARY.md §1` states the rule; §7 uses several terms that are not registered. Counted on live
text of the dissertation copy (both copies are identical in this respect):

| term in live §7 | occurrences | in `GLOSSARY.md`? | note |
|---|---:|---|---|
| **anticipatory set** | 1 | **NO** (0 hits for "anticipatory") | The concept is authorized as an illustration in `PAPER_PLAN.md:574` ("an anticipatory prefetch set"), but the dissertation registry has no entry. |
| **shortlist / shortlisted** | 2 | **NO** (0 hits) | Central to sentence [3]; carries a definition load ("the shortlist's centroid"). |
| **candidate set** | 1 | **NO** (0 hits) | The source record's word is "pool" (`matched.json` `pool`); neither is registered. |
| **centroid** | 1 | **NO** (0 hits) | Geometric term the sentence relies on. |
| **mobility-aware service** | 1 | **NO** (0 hits for "mobility-aware") | Appears in Ch.5 and Ch.1; registered nowhere. |
| **comparator** | 1 | **NO** (0 hits) | And see 4.10 — it is also ambiguous here. |
| **conservative** (of a difference) | 1 | **NO** | Statistical-register use. |
| **optimistic** (of a score) | 1 | **NO** | Same class. |
| private spatial path / region output | 1 each | **YES** | `GLOSSARY §2`, "the joint model" row: "region output (trunk + private spatial path)". |
| dedicated single-task model | 4 | **YES** | `GLOSSARY §2`. |
| forward pass | 1 | **YES** | `GLOSSARY §2`, same row. |
| next category / next region | — | **YES** | `GLOSSARY §1`. |
| epoch | 2 | **YES** | via the "early stopping" row and Ch.5's own gloss. |
| fold | 2 | **YES** | `GLOSSARY §3`. |

**Positive control for this instrument (V17):** the same case-insensitive search over the same file
returns 4 for "shared trunk", 4 for "next region", 1 for "private spatial path" and 1 for
"region output", so a zero is a real absence and not a pattern that cannot match.

**How to read this.** Seven unregistered terms is a lot for fourteen sentences, and most of them
carry the usage-sketch paragraph. This is a registry gap to close (the author adds rows; an agent
may only propose), not necessarily seven prose defects — but under the fail-closed rule the
paragraph currently cannot pass a `L2` lint. It is the strongest structural argument for rewriting
sentences [2]-[4] as a unit rather than patching them.

---

## PART 4 · VERDICT PER SENTENCE

Live text, comments stripped, **dissertation** copy (14 sentences). Items 1a-1c are the paper
copy's three extra live sentences. `KEEP-WITH-SCOPE` means the sentence is true but a scope or
convention clause is missing.

**1.** *"One model serves both tasks, in one forward pass it outperforms the dedicated category
model at all six datasets, and on region it outperforms the dedicated model at four of them and
matches it within a two-point margin at the other two, with the region output keeping a private
spatial path (Table 3; Figure 4)."*
**REWRITE — for punctuation only, not for content.** The claim is exactly right and fully
licensed: `06_results.tex:42-44` states the same split; `PAPER_PLAN.md §3` licenses "beats category
everywhere; beats region at Istanbul and the large states; matches region within a two-point margin
at AL/AZ"; Arizona is not upgraded; both verbs are bound to their tests per `WRITING_LAW §3`; the
table and figure are named. **What is wrong is a comma splice** introduced when the paper's two
sentences were merged into one on 2026-08-04 (`git log -S`, commit `9be36e8e`): the paper copy reads
"One model serves both tasks. In one forward pass it outperforms…". The dissertation's single
sentence joins two independent clauses with a comma. It also breaks parity with the paper copy for
no recorded reason.

**2.** *"A service could treat the model's top-ranked next regions as an anticipatory set: at
California, ten regions out of 8,501 contain the true next region 65.69 percent of the time, over
500 times better than picking ten at random."*
**REWRITE — delete the ratio clause; the rest is KEEP-WITH-SCOPE.** Two independent defects.
(a) "over 500 times better than picking ten at random" is a computed ratio whose only repository
source is a planning document's proposal (`MOBILITY_SCIENCE_BRIDGE_PLAN.md:77-93`, `≈547×`), derived
from the superseded `65.66` and from the random floor that `BRIDGING_METRICS.md:22` tells the reader
not to use — an `AGENT_GUARDRAILS §2 N2` violation, and the exact clause honesty flag F7 marked
`[VERIFY at adaptation]`. (b) The 65.69 half is correct to the digit
(`src/tables/mobiwac/results.tex:53`) but carries no convention, while the very next sentence
carries one; `WRITING_LAW §3` requires it. Also: "anticipatory set" is unregistered (§3.6).

**3.** *"On four datasets (Alabama, Arizona, Florida, and Istanbul; a single seed over five folds),
the ten shortlisted regions lie a median of 3 to 8 kilometers from the shortlist's centroid, against
17 to 176 kilometers for ten regions drawn at random from the same candidate set (median over 10,000
draws)."*
**KEEP-WITH-SCOPE.** Every number traces and the scope clause is unusually complete: the four
datasets are named, the seed/fold convention is stated, the comparator is matched (ten vs ten, per
the author's own 2026-07-20 ruling at `shortlist_compactness_RESULTS.md:149-157`), and the draw
count is given. Verified by opening the JSONs and counting the cells, not by reading the summary
table. **The missing clause:** the 3-8 km range is the **in-distribution** figure, and the source
record insists in-distribution and OOD "are reported SEPARATELY, never pooled" (`:7-8`); the OOD
medians (3.66 / 14.00 / 12.55 / 11.99) would not fit the stated range. Three unregistered terms
(shortlist, centroid, candidate set).

**4.** *"This remains motivation, not a measured service result."*
**KEEP.** It is the hedge `PAPER_PLAN.md:572-576` requires and the one honesty flag F7 names as the
condition for using these numbers at all. It is currently carrying more weight than the plan
intended (the plan expected "no measured number" in the sketch), which is an argument for keeping it
verbatim, not for softening it.

**5.** *"Three limits qualify these results."*
**REWRITE — the count is the problem, not the sentence.** The enumeration is a completeness claim
and the chapter discloses a fourth threat to validity it omits: the forward-edge channel between
consecutive visits (`05_setup.tex:82-84`, with its three limits at `:125-129`). See Part 2. The
narrow repair is either a fourth limit or a wording that does not assert an exhaustive count; which
one is the author's call, and the fourth-limit route needs only material already live in
`05_setup.tex`.

**6.** *"First, our representation is trained once over all places; visits to places never seen
during training are the single effect that we cannot fully isolate."*
**KEEP-WITH-SCOPE.** The transductive limit is real and separately recorded (A4;
`05_setup.tex:36-40`, differences −0.33 to +0.01 Acc@10 at AL/AZ/FL). **"the single effect that we
cannot fully isolate"** is the strained clause: it is a universal about the whole study, and
`05_setup.tex:125-129` names another effect the chapter cannot fully isolate (what a nonlinear read
could recover from the forward edge). The two sit four paragraphs apart in the same chapter and
disagree. Narrowing "the single effect" to its own scope (the representation's training coverage)
would resolve it without touching the finding.

**7.** *"A planned follow-up trains it on each fold's training places only and embeds unseen
visits."*
**KEEP.** A statement of future work, no number, matches the plan's own wording
(`PAPER_PLAN.md:566-568`, "a planned training-only variant is meant to close that gap").

**8.** *"Second, epoch selection consults the fold that the score is then read on (Section 5.2), so
every absolute score reported here is optimistic."*
**KEEP.** Accurate and appropriately blunt; `06_results.tex:52-57` states the selection rule it
refers to, and the cross-reference target `sec:mobiwac:setup-windows` exists in the same chapter.
"optimistic" is unregistered but is ordinary statistical English, not project jargon — propose the
row rather than change the word.

**9.** *"The comparison between the joint model and the dedicated models is affected far less, for
two reasons we can state outright: the selection rule is the same for both models on the same folds,
an epoch chosen on validation and read on that fold, with each model selected on its own validation
objective (Section 6.2), and the dedicated model receives the wider search, a per-dataset sweep over
batch size and learning rate against one configuration held fixed across all six datasets for the
joint model."*
**REWRITE — the SECOND reason is scoped wider than its evidence. The first reason is confirmed
true.** Reported separately so one does not launder the other (V13):
- *Reason one, "the selection rule is the same for both models on the same folds":* **TRUE as
  written**, confirmed in Part 3.1 against `science/fold_partition_and_seeds.md §7` and
  `GLOSSARY §3`, not merely against the audit note that asserts it. Its narrowing to "each model
  selected on its own validation objective" is decision **D3** and must survive.
- *Reason two, "the dedicated model receives the wider search, a per-dataset sweep over batch size
  and learning rate":* **over-general.** The chapter's own results section states the sweep covers
  the dedicated **category** model only: `06_results.tex:95` (identical at `articles/[mobiwac]/src/
  sections/06_results.tex:50`) — "The dedicated category model is tuned per dataset over batch size
  and learning rate **(the dedicated region models use the strongest fixed configuration)**". The
  primary record agrees: `docs/studies/closing_data/v17_completion/CEILINGS_N20_FINAL.md:41-53` is a
  *category* ceiling sweep, per state. So for the region comparison, both sides run a fixed
  configuration and the "wider search" mitigation does not hold. §7 states it of "the dedicated
  model", unqualified, inside the paragraph that bounds the optimistic-score bias for **both**
  tasks. This is the same defect class as the "identically" correction of `ERRATA.md:139-148`: a
  mitigation made to sound stronger than the evidence supports, which understates a limitation.

**10.** *"The residual therefore favors the comparator, which makes the reported difference
conservative."*
**KEEP-WITH-SCOPE — it inherits sentence 9's scope defect.** "therefore" carries the conclusion
from *both* reasons in [9]; with reason two holding only for category, the "conservative" reading is
supported for the category comparison and not established for region. Whatever scope [9] gains, this
sentence must match. Separately, "the comparator" is unregistered and ambiguous here: the registered
name is "dedicated single-task model" (`GLOSSARY §2`, which also says "never bare 'baseline'"), and
§7 elsewhere in the same paragraph calls it "the dedicated model" — a synonym cycle
`WRITING_LAW §1` forbids.

**11.** *"It does not follow that the bias cancels exactly."*
**KEEP.** Deliberate and recorded: `ERRATA.md` (2026-07-26 REV-003 block, and the round-5 comment at
`07_discussion.tex:151-153`) documents that the drafted source claimed the bias "cancels in the
difference" and that this text deliberately declines that. `ERRATA.md:147-148` records it as
untouched by the later narrowing. Do not merge it into [10].

**12.** *"Third, we do not build or evaluate a mobility-aware service, this is a background
motivation, and this chapter's claims are the prediction results themselves."*
**REWRITE — punctuation, and parity.** The content is right and required (it is the third limit
`ERRATA.md:73-80` added). But the dissertation copy joins independent clauses with a comma ("service,
this is a background motivation"), where the paper copy uses a semicolon ("service; it is background
motivation"). Both copies were reflowed in today's commit `71d119ce`; the dissertation's version
acquired the comma splice and the words "this is a" in that reflow. "this chapter's claims" vs the
paper's "the paper's claims" is a deliberate, recorded adaptation (`ERRATA.md:79-80`) and must stay
different.

**13.** *"Our representation is a fixed per-visit vector that any downstream model can consume."*
**KEEP.** Consistent with `GLOSSARY §2`'s Check2HGI row ("yields one vector per **visit**") and with
`6_conclusion.tex`. "fixed" here means "not re-trained per consumer", which is a plain-English use
rather than the banned repo sense of "frozen" (`WRITING_LAW §2`); worth a read-aloud check, since the
adjacent chapters use "fixed" for configurations too.

**14.** *"Moura et al. [moura2025mobilityaware], whose structural analysis of tourist check-ins
reads past visits only, name machine learning as a next step; this study moves in that direction."*
**KEEP.** The bib entry resolves and is complete in the version of record:
`articles/[mobiwac]/src/references.bib:546-552` — Moura, Aquino, Loureiro, *On the Design of
Mobility-Aware Systems: A Tourist's Perspective*, Proc. IEEE/ACM MSWiM, pp. 667-674, 2025,
DOI `10.1109/MSWiM67937.2025.11308734`. **[VERIFY: I did not open the Moura PDF this session, so
the claim-support half of `R1(c)` — that the paper's structural analysis reads past visits only and
names machine learning as a next step — is inherited from the MobiWac bibliography's own verified
record rather than re-confirmed here. The bibliography is the declared donor of record
(`AGENT_GUARDRAILS R1`), and this sentence is unchanged published-submission prose, so I flag it
rather than re-verify within the time box.]**

### The paper copy's three extra live sentences

**1a.** *"The gain is substantial, and where we could test it the gain is a property of the joint
architecture rather than of cross-task transfer:"* — **KEEP.** This is the exact wording the closed
sign-off approved (`NEEDS_SIGN_OFF.md:1534-1536`) and `ERRATA.md:212-220` logs.
**1b.** *"at the three datasets where the region pathway is held at its initial values, the category
gain survives in full."* — **KEEP.** The three-dataset scope is deliberate and load-bearing:
`NEEDS_SIGN_OFF.md:1540-1543` records that dropping it would turn a 3-of-6 result into a 6-of-6 one
in the reading. Matches `06_results.tex:200-210` (AL, AZ, FL; 63.50 / 63.67 / 79.79).
**1c.** *"Which component of that architecture produces the gain is not settled by the controls
reported here (Section 6.2)."* — **KEEP as a claim; FLAG as the author's stated dislike.** It is
true and required by D2. But `NEEDS_SIGN_OFF.md:1517-1519` is the author saying, verbatim, that we
cannot say *"Which part of the joint architecture produces the category gain is not settled"* — and
this is that sentence, in the paper copy, under a nearly identical wording. The sign-off closed by
softening the *preceding* sentences and keeping this clause verbatim
(`NEEDS_SIGN_OFF.md:1536`, "A frase ficou assim"), so the author's objection to the clause itself
was answered by context rather than by removal. **Given that the dissertation copy now has the whole
passage commented out under `%[AUTHOR COMMENT]`, this is very likely the sentence the parking is
about.** It is his call; the constraint from the evidence is only that no rewrite may replace it with
a claim naming the trunk (D2).

---

## [VERIFY] FLAGS

1. **[VERIFY]** Whether the `%[AUTHOR COMMENT]` block at
   `articles/dissertacao/src/chapters/5_mobiwac/07_discussion.tex:18-23` is a deliberate removal or
   a parked edit. It desynchronizes the dissertation from the submitted paper source
   (`articles/[mobiwac]/src/sections/07_discussion.tex:16-19`, still live), against the standing
   parity policy, and it contradicts `ERRATA.md:212-220` and `NEEDS_SIGN_OFF.md:1532-1536`, which
   both record that wording as applied to both texts. Not resolvable from the repository.
2. **[VERIFY]** Sentence 14's claim-support half (Moura et al. "reads past visits only", "name
   machine learning as a next step"). The bib record is complete and the DOI is in the version of
   record; the PDF was not opened this session. Inherited from the MobiWac bibliography.
3. **[VERIFY]** Whether an "anticipatory set" / "shortlist" / "centroid" / "candidate set" /
   "mobility-aware service" / "comparator" registry row is wanted, or whether the usage-sketch
   paragraph should be rewritten to avoid the unregistered terms. Under `GLOSSARY §1` the paragraph
   cannot pass a fail-closed lint as it stands; only the author can add rows.
4. **[VERIFY]** If the ratio clause in sentence 2 is to be replaced by a random-floor value rather
   than deleted, the floor and its source must be chosen by the author: the file that computes it
   (`BRIDGING_METRICS.md:21`, `docs/results/P0/simple_baselines/california/next_region.json`,
   `aggregate/random/acc10_mean = 0.001177`) is the same file that tells the reader at `:22` to use
   the Markov-1 floor instead. Either choice is a new claim (`C2`).
5. **[VERIFY — not investigated, time box]** Whether the dissertation's Ch.1 or Ch.6 repeats the
   "over 500 times" ratio anywhere. `V6` says correcting a number at its source is not correcting
   the claim. I searched the article tree and the round-13 records and found the phrase only in
   `MOBILITY_SCIENCE_BRIDGE_PLAN.md` (`:90`, `:442`, `:717`) and in the two §7 copies, but I did not
   run an exhaustive sweep of every frame chapter for paraphrases of the ratio ("more than five
   hundred", "orders of magnitude better than chance", etc.). Recommend that sweep before the
   rewrite lands.

## WHAT I DID NOT DO

- No `.tex`, `PENDENCIAS.md`, `ERRATA.md`, `LEFT_OUT.md` or `NEEDS_SIGN_OFF.md` file was edited.
- No replacement prose was drafted.
- I did not recompute any reported number to "check" it. Where I opened a JSON, it was to count the
  cells behind a value the prose quotes (V8) and to read the value the record already states, never
  to substitute my own arithmetic for the document's.
- I did not open the Moura et al. PDF (flag 2), and did not sweep the frame chapters for
  paraphrases of the 500× ratio (flag 5).
