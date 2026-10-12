# 11 · POI / mobility expert — review v2

**VERDICT: SOUND WITH CORRECTIONS — two blockers, both about how external and historical
results are presented rather than about the final study's own measurements.**

Severity count: **2 BLOCKER · 8 MAJOR · 9 MINOR · 2 NIT** (21 findings).

Reviewed: defense build `src/dissertacao.pdf` (97 pages, mtime 11:42:18) and `src/build/main_final.pdf`
(mtime 14:14:03), against `src/chapters/*.tex` (Ch.2 mtime 14:11:19, Ch.5 mtime 11:38:38 — line numbers
below were re-pinned after those edits), `docs/context/`, `docs/results/`, `docs/studies/`,
`research/embeddings/`, `scripts/`, and the primary sources named in each finding. Note that
`dissertacao.pdf` (11:42) predates the last edit to `2_fundamentals.tex` and `apx_b_errata.tex` (14:11);
`main_final.pdf` (14:14) does not.

The core scientific claim of Chapter 5 survives this review. The next-region metric convention is
correct and its two conventions coincide arithmetically; the transition prior is handled properly and
disclosed accurately; the user-disjoint split is real; the task triple is kept distinct and the
exact-next-place non-claim is honored throughout. What fails is the presentation of (a) the static
category task inherited from Chapters 3 and 4 and (b) the external region baselines, which the chapter
designates as state of the art while its own floor says otherwise.

---

## BLOCKERS

### B-1 · The static category task of Chapters 3 and 4 has an input that determines its label, and the document says so nowhere — while the frame's central diagnosis leans on it

**Lens 3 (transductive-artifact leakage) / Lens 4 (trivial floors) — BLOCKER.**

The determinism is real and I re-derived it firsthand from the committed corpus, at every state, not
just the one the internal review measured:

| state | POIs | distinct fine-grained values | mapping to more than one target class |
|---|---:|---:|---:|
| Alabama | 11,848 | 284 | 0 |
| Arizona | 20,666 | 305 | 0 |
| Florida | 76,544 | 324 | 0 |
| California | 169,145 | 333 | 0 |
| Texas | 160,938 | 365 | 0 |

(measured on `data/checkins_by_state/<state>.parquet`, one row per `placeid`, `spot` against `category`.)

The chain is in code, each link readable:

- `research/embeddings/hgi/poi2vec.py:487` — `poi_embeddings[valid] = fclass_embeddings[fclass_values[valid]]`,
  under the printed comment at `:485-486`: *"CRITICAL OPERATION: Map each POI to its fclass embedding"*.
  The place vector is a pure function of the fine-grained category.
- `research/embeddings/dgi/preprocess.py:115` — `self.embedding_array = pd.get_dummies(self.pois['category'])`,
  and `:130` sets each node's feature to the neighbour mean of that same one-hot; `dgi/dgi.py:56` feeds
  `embedding_array_test` as `data.x`, and `model/DGIModule.py:52` instantiates `POIEncoder(7, hidden)`.
  The DGI node feature space *is* the seven-class target space.
- Composition: input determines label exactly, for the static task.

The repository already ran the decisive control and recorded the outcome. From
`docs/archive/fusion-study/results/P0/leakage_ablation/alabama/comparison.json`, permuting the
fine-grained column with the target column left intact:

| arm | category macro-F1 | sequential macro-F1 |
|---|---:|---:|
| baseline | 0.7855 | 0.2383 |
| `C_fclass_shuffle` | **0.1437** | 0.1988 |

1/7 = 0.1429. The static task collapses to chance; the sequential task barely moves. The repo's own
reading, `docs/archive/fusion-study/issues/HGI_LEAKAGE_EXPLAINED.md:78`: *"Next-POI mal se abalou"* —
the sequential task never rested on the shortcut.

**Nothing of this reaches the reader.** Across all 97 rendered pages the string `fclass` occurs once
(p51, inside Chapter 4's encoder description); `permut`, `determines the label`, and `shortcut` occur
zero times. `shuffl` occurs on four pages (33, 60, 63, 66), but every occurrence is the infomax
training objective corrupting graph features (*"a random shuffling method"* p33; *"a copy with
shuffled node features"* p60; *"reject a shuffled one"* p63; *"contrasts real graph neighborhoods
against shuffled ones"* p66) — none of them is the fine-grained-category shuffle control, which
appears nowhere. Meanwhile `apx_a_contributions.tex` tells the board that a prior
submission was attacked for label leakage and that Chapter 5 answers with a dedicated audit. A
referee who reads that, then reads Chapter 4's headline — *"the proposed variants outperform MTLNet
in all 21 category-state combinations, with average gains per state of 20.2 to 22.0 percentage
points"* (`4_courb.tex:414`) — will ask why the chapter with the label-determined task received no
equivalent treatment.

**The frame makes it worse, not better.** `1_introduction.tex:114`: *"Category performance rose
sharply at every state tested. The diagnosis followed: at that stage of the research, the input
representation, not the sharing architecture, was the bottleneck."* The sharp rise is the static
task's 20.2–22.0 pp. Chapter 4's *sequential* result is far weaker — *"the proposed variants keep
the higher Average F1-Score per category in most category-state combinations, while the baseline
retains six of them"* (`4_courb.tex:356`). So the diagnosis step of the dissertation's arc is
narrated on the number that the shuffle control kills.

**My judgment as a mobility referee.**

1. *Is it fatal to the static task?* Yes, as instrumented. Classifying a place's coarse category from
   a vector built by table lookup on that place's fine category is not a prediction problem; it is
   the lookup. The 20.2–22.0 pp figure measures how well two encoders preserve a deterministic
   key, not representation quality. It cannot support any claim about representations for prediction.
2. *Does it touch the sequential task?* No. Arm C moves it by about 4 points, not to chance, and the
   sequential inputs are windows of nine preceding visits with the target excluded
   (`3_cbic.tex:161-167`, `4_courb.tex:123-125`). The sequential conclusions of both chapters stand.
3. *Is a scoping sentence enough?* **No.** A referee will demand four things, and a sentence carries
   at most one: (a) the measurement stated with its number and its scope (all five states, zero
   fine-grained values crossing a target class); (b) the static-task figures explicitly withdrawn from
   any claim about representation quality *for prediction*; (c) the shuffle control reported, because
   it is the evidence that separates "compromised task" from "compromised chapter"; (d) the explicit
   statement that the sequential task of both chapters is clean, with the code reference. That is an
   appendix, and the author already proposed one (`src_utils/PENDENCIAS.md:143-145`). Concur.
4. *Where must it be visible?* Not only in an appendix. `1_introduction.tex:114` must stop resting the
   diagnosis on the static number, and Chapter 6's limitations must carry it. A finding disclosed
   only in Appendix D-style back matter, while the introduction still narrates the compromised number
   as the turning point of the research, is disclosure that does not reach the reader who matters.
5. The published, co-authored status of Chapter 4 constrains *the reproduced prose*, not the frame.
   The appendix, the introduction sentence, and the Chapter 6 limitation are all frame prose and need
   no co-author notice; only a preface caveat inside Chapter 4 does. That ordering lets the honest
   version ship without waiting on the courtesy notice.

### B-2 · HMT-GRN, designated the primary external region comparison, sits below this chapter's own non-learned Markov floor on all six datasets — and the chapter prints both numbers without reconciling them

**Lens 4 (trivial floors) / Lens 5 (baseline re-implementation fairness) — BLOCKER.**

`5_mobiwac.tex:427`: *"The first role is played by the per-task state of the art, on our data, under
user-disjoint five-fold protocols."* `5_mobiwac.tex:632`: *"HMT-GRN ... is the primary external
comparison."* And `5_mobiwac.tex:771`: the first-order Markov region floor *"reaches $51$ to $72$
Acc@10 across the datasets; the joint model exceeds it by $4.9$ to $10.3$ points on all six
datasets."*

Both sets of numbers are individually traceable. Put in one table they say something the chapter
never says. Floors quoted from `docs/results/closing_data/markov_floor_stride1/<state>.json`
(`markov_1step_region_acc10_mean`); baselines quoted from `5_mobiwac.tex:620-625`:

| dataset | Markov floor | HMT-GRN | ReHDM | STAN |
|---|---:|---:|---:|---:|
| Arizona | 51.23 | 43.70 | 53.00 | 49.86 |
| California | 59.09 | 49.61 | 50.26 | 58.52 |
| Texas | 60.10 | 53.85 | 48.81 | 61.67 |
| Alabama | 62.26 | 57.05 | 65.38 | 60.72 |
| Istanbul | 65.06 | 60.40 | 69.33 | 61.86 |
| Florida | 72.47 | 63.74 | 64.49 | 72.99 |

HMT-GRN is below the floor at six of six. ReHDM at three of six. STAN at four of six. The dedicated
and joint columns are above it everywhere. A first-order transition table beats every external
published system on this task at most datasets.

That is not automatically a defect — a stride-1 sliding-window protocol makes the last visited region
extremely informative, and the repo records that 22.4% of Alabama windows contain their own target as
a genuine revisit (`docs/studies/archive/mtl_improvement/PIPELINE_AUDIT_2026-06-03.md:24`). A strong
persistence floor is a property of the protocol. But the chapter cannot call these systems "the
per-task state of the art, on our data" on one page and print a non-learned floor above all of them
twenty pages later without a paragraph reconciling the two. A referee will read the pair as evidence
that the re-implementations are under-trained or mis-adapted, and will discount the external
comparison entirely — including the parts that favor the contribution.

Note the repo carries the stale version of this claim too: `docs/results/closing_data/MACS_BOARD_RESULTS.md:47`
asserts *"HMT reg clears the Markov floor"*, which held against the older non-overlapping floor
(Alabama 47.01, `old_floor_nonoverlap` in the same JSON) and was never revisited when the floor was
recomputed under the shipped windowing (Alabama 62.26). The chapter quotes the new floor and the
board's baseline numbers, so it inherited an inconsistency rather than creating one.

**What a referee would accept:** a short paragraph in the results discussion stating (i) that the
sliding-window protocol makes region persistence unusually strong, with the revisit share as
evidence; (ii) that the externals fall below that floor at most datasets and why (region-native models
built for a geohash grid and their own split, re-adapted here); and (iii) that the controlled claim
therefore rests on the Dedicated column, which the chapter already says at `:767-770`. Chapter 5 is
a time capsule under review, so this is a camera-ready fix plus an Appendix B row for the
dissertation.

---

## MAJOR

### M-1 · ReHDM appears in a next-region column with its prediction target silently swapped

**Lens 5 — MAJOR.** `docs/baselines/next_region/rehdm.md:24` states the adaptation plainly:
*"Faithful from-scratch reproduction (paper protocol) with the predictor's output domain swapped from
`n_pois` to `n_regions`."* The paper is a next-POI recommender — Li et al., IJCAI 2025, *"Next POI
recommendation contributes to the prosperity of various intelligent location-based services"* — whose
regional encoding is one of six input IDs at quadkey level 10, not its target.

The chapter gives HMT-GRN a full deviation account (`:427-436`: kept skeleton, added per-fold prior,
dropped graph components and hierarchical search) and labels STAN *"our re-implementation"*
(`:633`). ReHDM gets *"a ReHDM reference"* (`:765`) and *"(its own protocol)"* (`:633`) — neither of
which tells the reader the output domain was changed. A reader comparing to the published ReHDM
numbers is comparing to a different model.

Second, the same record flags the two thinnest cells: *"CA/TX v4 = seed-42 partials (50.26/48.81,
both BELOW their best-simple floors 52.09/54.94 — coverage-only)"* (`rehdm.md:9-10`). The chapter
prints both values with only a single-seed dagger (`:635`). A published-SOTA baseline reported below
a trivial floor needs that said, not footnoted as a seed count.

### M-2 · The grid-cell formulation is attributed to a survey that says the opposite

**Lens 7 (problem-formulation comparability) — MAJOR.** `5_mobiwac.tex:143-145`: *"Predicting over a
partition of the map is also the standard formulation in the human-mobility literature, with a grid
cell as the target~\cite{luca2021mobilitysurvey}; our next-region task substitutes official
neighborhood-scale units for grid cells."*

I read the survey (arXiv 2012.02825, downloaded and text-extracted this session). It defines the task
over locations derived from stay points — *"forecasting which location an individual will visit given
historical data about their mobility"* — and names a POI variant: *"A variant of next-location
prediction aims at forecasting the next Point Of Interest"*. Tessellations and tiles are introduced
for a *different* task in its taxonomy: *"for crowd flow prediction, a spatial tessellation is used
to aggregate the flows of people moving among the tiles"*, and §3.2 opens *"Crowd flow prediction is
the problem of forecasting the incoming and outgoing flows of locations in a geographic region,
usually split into tiles on a spatial tessellation"*. I searched every co-occurrence of
tile/tessellation with next-location in the survey: none of them makes a map partition the standard
target of next-location prediction.

Chapter 2 does not repeat the error — `2_fundamentals.tex:46` cites the same survey correctly, for
*"several distinct problems, from crowd-flow estimation to next-location prediction"*. So the fix is
local to Chapter 5 (and to `articles/[mobiwac]/src/sections/02_related.tex:45`, which carries the same
sentence and is still under review, so it can be corrected in the camera-ready). The substantive
point the sentence wants — that region-level targets are established in the field — is defensible on
other citations already in the chapter (`zhu2022drrgnn`, `Lim2022`); it is the attribution to this
survey that fails.

### M-3 · Appendix D's ceiling and Chapter 5's screen are computed on a different window population from the reported results, and neither says so

**Lens 2 (window/sequence leakage) / Lens 9 (reproducibility) — MAJOR.**

Appendix D's table reports Windows: Alabama 12,709 · Arizona 26,396 · Florida 159,175 · California
358,302 · Istanbul 58,075. Chapter 5's dataset table reports 96,326 · 200,895 · 1,274,418 ·
2,925,466 · 271,666 (`5_mobiwac.tex:354-359`). Same datasets, counts differing by roughly 7.6×.

The cause is windowing, and I traced it to the file: `scripts/embedding_eval/autocorrelation_ceiling.py`
reads `output/check2hgi/<state>/input/next.parquet`, which holds 12,709 rows at Alabama (read
directly), built at stride 9 with `MIN_SEQ=5`; the reported results use gated stride-1 overlap
(`markov_floor_stride1/alabama.json` → `windowing: {"window_size": 9, "stride": 1,
"min_sequence_length": 10, "emit_tail": false, "note": "board check2hgi_dk_ovl protocol"}`, and
`old_floor_nonoverlap.windowing: "non-overlap (stride-9, MIN_SEQ=5, emit_tail=True)"`). I confirmed
the stride by inspecting consecutive windows for one user in `temp/sequences_next.parquet`.
`scripts/embedding_eval/leak_sniff.py` reads the same non-overlap file, so the screen and the ceiling
are internally consistent — it is the *results* that live on the other windowing.

Two consequences. First, a reader who lays the appendix table beside Table 8 sees an unexplained
factor of seven in the same quantity under the same name. Second, and more substantively, the label
autocorrelation of a window population depends on how the windows are cut, so the *"four to six
points"* gap that `5_mobiwac.tex:396` and Appendix D both report is a gap between two numbers measured
on two different window populations. Chapter 5 discloses that the screen ran on *"ancestor builds of
the representation"* — a statement about the encoder, not about the windowing — so this particular
mismatch is currently invisible.

Fix: one clause in Appendix D naming the windowing of its Windows column and stating that it matches
the screen rather than the results table, plus the same clause in `5_mobiwac.tex:396`. No number needs
to change.

### M-4 · §2.2 justifies retuning the place-level baseline with a number from the label-determined task

**Lens 5 — MAJOR.** `2_fundamentals.tex:169-173`: *"the cross-region edge weight of their Equation 2,
set to 0.4 for the dense Chinese cities they study, was raised to 0.7 for the sparser United States
state datasets used here, a change under which the category F1 on Alabama, over five folds, rose
monotonically from 0.74 to 0.82 across the swept values."*

Every checkable part is right. Huang et al. Eq. (2) is `ap(pi,pj) = log((1+L^1.5)/(1+l^1.5)) × wr`
with *"wr is a factor to differentiate intra- (wr = 1) and cross-region (wr = 0.4) edges"* (read from
the PDF in `science/articles/`). The sweep is real (`research/embeddings/hgi/README.md`) and the
shipped default is 0.7 (`hgi/preprocess.py:23`, `hgi/hgi.py:292`).

But the swept column that rose 0.7388 → 0.7678 → 0.7944 → 0.8186 is the README's **Cat F1** — the
*static* category task, the one B-1 shows is determined by its input. The same table's **Next F1**
column, which the chapter does not report, is flat: 0.2837 / 0.2750 / 0.2767 / 0.2837. So the
baseline that Chapter 5 beats by +27.63 to +39.62 macro-F1 on next category was tuned on a criterion
that belongs to a different, compromised task.

This one cuts *for* the author if stated: because the sequential column is flat across the sweep, no
choice of that weight would have helped HGI on next category, which is direct evidence that the
place-level baseline is not disadvantaged by the tuning decision. As written, the chapter takes the
credit-risky half of that fact and omits the exculpatory half. Say which task the 0.74–0.82 figure
belongs to, and add that the sequential metric was flat.

### M-5 · The Istanbul data vintage never appears, and its corpus spans two collection blocks nearly four years apart

**Lens 6 (dataset staleness) — MAJOR.** `6_conclusion.tex:175-176` states the Gowalla vintage
(*"collected between 2009 and 2011"*). No vintage is stated anywhere for Istanbul: `2017` and `2018`
appear in the frame only as citation keys.

From the shipped Istanbul check-in graph metadata (`output/check2hgi/istanbul/temp/checkin_graph.pt`):
range 2012-04-03 to 2018-10-19, with per-year counts 2012: 160,601 · 2013: 166,641 · **[gap]** ·
2017: 56,797 · 2018: 78,576. The source paper confirms the design: Massive-STEPS is *"derived from
the Semantic Trails dataset"* and provides *"high-quality check-ins from 2012-2013 and 2017-2018"*,
listing Semantic Trails' years as *"2012-2013, 2017-2018"* in its Table 1.

For a sliding-window protocol this is a construct-validity issue, not just a metadata omission:
1,710 users have visits in both blocks and 1,710 consecutive-visit gaps exceed two years, so those
users' windows straddle the collection gap and their "next visit" is a visit years later. The
reported horizon already shows the symptom — Istanbul's mean gap 287.7 hours against 23–39 elsewhere,
and only 82.0% of targets within a week versus 96–98% elsewhere
(`docs/results/closing_data/horizon_stride1/istanbul.json`) — and `5_mobiwac.tex:372-375` honestly
reports *"5 to 27 percent of targets lie over 3 days ahead"*. What is missing is the cause. Name the
two-block vintage, and either drop cross-gap windows or state that they are retained and how many
there are.

Related, and cheap: `2_fundamentals.tex:452` cites Massive-STEPS for the argument *"that the field has
leaned too long on decade-old datasets"* — an accurate reading of that paper — three sentences after
adopting a 2009–2011 corpus as the dataset of record. The tension is real and the chapter is stronger
if it names it rather than leaving it for the examiner.

### M-6 · §2.4 attributes the five state datasets to a release that is not the corpus consumed, and the document states two different vintages for them

**Lens 9 — MAJOR.** `2_fundamentals.tex:448-450`: *"Gowalla is the dataset of record, introduced with
the study of periodic and socially driven movement in LBSNs, and this work uses five United States
states from it \cite{cho2011gowalla}."*

The consumed corpus is a different artifact. I measured the committed parquets: the union range is
2009-01-21 to 2011-08-16 (Texas 2009-01-21 → 2011-08-16; California 2009-01-24 → 2011-08-14). The
repo's own licensing audit says so explicitly — `src_utils/evidence/DATASET_LICENSING_FINDINGS.md:21-22`:
*"The SNAP/cho2011 dump (Feb 2009-Oct 2010) is NOT the data source; cho2011gowalla is cited as the
LBSN reference only."* Chapter 5's data footnote does name the actual deposit (rendered p59: *"the
category-annotated Gowalla dump"* with the Figshare URL), so §2.4 contradicts the chapter it
introduces.

Consequence inside the document: Chapter 4 states *"mobility records collected between February 2009
and October 2010"* (rendered p57) — the SNAP window — while `6_conclusion.tex:175-176` states 2009 to
2011. Same five states, two vintages, in one volume. Chapter 4 is a time capsule, so the fix is an
Appendix B row plus a corrected §2.4 sentence that cites the LBSN paper as the LBSN reference and
names the consumed deposit for the corpus.

### M-7 · §2.4 defines two metrics that no chapter reports

**Lens 8 (metric conventions) — MAJOR.** `2_fundamentals.tex:467-476` promises two things the
document never delivers:

- *"which is why mean reciprocal rank accompanies it where the joint comparison needs a rank-sensitive
  figure"* (`:470`). In the rendered build, `reciprocal` appears on page 24 only; `MRR` and `Acc@5`
  appear zero times anywhere.
- *"the aggregate is the relative multi-task performance change, the average per-task percentage by
  which the joint model leads or trails the dedicated single-task models \cite{maninis2019attentive}"*
  (`:475-476`). `relative multi-task` also appears on page 24 only.

A fundamentals chapter whose job is to fix the document's evaluation conventions cannot name two
metrics that never recur; an examiner will look for them. Both are available if the author prefers to
deliver rather than retract — the evaluator computes `mrr_indist` and the Markov floor JSONs carry
`mrr_mean` per dataset — but as it stands one of the two sentences has to go.

### M-8 · The ">99% of test visits" fairness figure has no committed measurement under the shipped windowing

**Lens 8 / Lens 9 — MAJOR, [UNVERIFIED].** `5_mobiwac.tex:632`: *"HMT-GRN (region-native, on our
folds, scored on visits whose region appears in training, $>$99\% of test visits in every dataset and
fold)"*.

I scanned every JSON under `docs/` and `results/` for `ood_fraction` (8,517 and 5,542 files
respectively). No record carries a coverage fraction on a fold of stride-1 size. The records that do
exist sit on the non-overlapping windowing, and they are below 99%:

| record | fold size | in-distribution share |
|---|---:|---|
| `docs/results/B3_validation/al_5f50ep_b3.json` (this baseline, Alabama) | 2,541.8 = 12,709/5 | mean 97.04%, worst fold 96.18% |
| `docs/results/B3_validation/az_5f50ep_b3.json` (this baseline, Arizona) | 5,279.2 = 26,396/5 | mean 98.01%, worst fold 97.52% |
| best value found anywhere (`results/check2hgi_design_k…`, Florida) | — | 99.49% |
| worst value found anywhere (`results/check2hgi`, Alabama) | — | 95.64% |

The only shipped-windowing artifact for this baseline on disk,
`results/baseline_b3_hmt_grn_style/alabama/b3_seed0_folds5.json`, records no coverage field at all and
declares `"windowing": "stride-9 (current)"`.

I am **not** asserting the claim is false: coverage should rise under stride-1 (7.6× more windows means
a larger training region vocabulary per fold), so >99% is plausible. But it is currently unmeasured in
the repository, and the nearest same-baseline, same-metric measurements are 96–98% at two of the six
datasets. Under the number protocol this figure is not quotable. Either compute it on the shipped
folds and commit the output, or weaken the parenthetical to what the artifacts support.

---

## MINOR

### m-1 · The region label space is POI-populated tracts, not tracts

**Lens 7 — MINOR.** `5_mobiwac.tex:313`: *"1,109 regions in Alabama"*; `:235`: *"from 520 classes
(Istanbul) to 8,501 (California)"*. The label space is the set of tracts that contain at least one
POI, not the state's tracts:

| state | regions in label space (`checkin_graph.pt`) | tracts in the 2022 TIGER file (DBF record count) |
|---|---:|---:|
| Alabama | 1,109 | 1,437 |
| Arizona | 1,547 | 1,765 |
| Florida | 4,703 | 5,160 |
| California | 8,501 | 9,129 |

The reported numbers are the true label-set sizes and `:235` says *"candidate regions"*, so nothing is
inflated. But *"the region unit is a census tract"* invites the reader to assume the full partition,
and a reproducer needs the filter. One clause fixes it.

### m-2 · The tract partition postdates the check-ins by a decade

**Lens 6 — MINOR.** Every tract shapefile in `data/miscellaneous/` is TIGER 2022
(`tl_2022_01_tract_AL`, `…_04_…AZ`, `…_06_…CA`, `…_12_…FL`, `…_48_…TX`), and
`tl_2022_01_tract.shp.iso.xml` identifies its geography as *"2020 Census"*. The visits are 2009–2011.
Tract boundaries were redrawn in 2010 and again in 2020, so a 2009 visit is labelled with a polygon
that did not exist at the time. The task remains internally consistent — the label is well defined and
the same partition is used everywhere — but this is a standard referee question about a
census-geography target and it is answered nowhere. One sentence in the data description.

### m-3 · The Istanbul unit is a volunteer-mapped layer described as "official"

**Lens 7 — MINOR.** `5_mobiwac.tex:145` says the task *"substitutes official neighborhood-scale units
for grid cells"* and `:235` calls the mahalle *"a municipal neighborhood"*. The layer on disk is
`data/miscellaneous/istanbul_mahalle/istanbul_mahalle.geojson`, 972 features, whose properties are
OpenStreetMap tags (`admin_level: '8'`, `network: 'TR34-villages'`, `@id: 'relation/1275322'`),
acquired via Overpass by `scripts/second_dataset/acquire_istanbul_mahalle.py` — whose own docstring
says the primary region definition *"needs real admin polygons"* because no clean government layer was
available (`research/embeddings/hgi/CLAUDE.md:120`: *"Non-US regions … there's no TIGER shapefile"*).
520 of the 972 are populated. "Official" overstates a provenance the repo describes accurately;
"administrative neighborhood boundaries from OpenStreetMap" costs the same space and is defensible.

### m-4 · The granularity-matched Istanbul variant was built to answer the coarseness objection and is never mentioned

**Lens 7 — MINOR.** `5_mobiwac.tex:791` hedges: *"Acc@10, since region counts differ across datasets
(520 mahalle here)"*. The repo built the direct answer:
`docs/studies/second_dataset/STATS_T1.md:95-97` describes an H3 resolution-9 variant of **2,585 cells**
as *"SECONDARY — synthetic grid; granularity-matched to NYC (1,912) and the Gowalla band; retires the
'is the 520-way result an artifact of coarseness?' objection"*, and the artifacts exist
(`output/check2hgi/istanbul/h3/input/next_region_labels.parquet`, 60,091 rows, plus per-fold priors for
five seeds). I could find no result computed under it — the one RESULTS file under the H3 name reports
the 520-region mahalle numbers. Either run it or state in the limitations that a granularity-matched
variant was prepared and not evaluated; leaving a prepared sensitivity check unmentioned invites the
objection it was built to retire.

### m-5 · Appendix D overstates why Texas is absent

**Lens 9 — MINOR.** Appendix D: *"Texas is absent because the artifacts the computation needs, the
check-in graph and the window file, were not retained for that dataset … recomputing the ceiling
there would require re-running preprocessing."* The JSON's own skip record agrees on the mechanism
(`"FileNotFoundError: texas: missing output/check2hgi/texas/temp/checkin_graph.pt"`). But the repo
already solved this for two other label-only computations: both `compute_markov_floor_stride1.py` and
`compute_horizon_stride1.py` reconstruct the Texas stream from raw
(`horizon_stride1/texas.json` → `"checkin_stream": ".../data/checkins/Texas.parquet (raw; … REBUILT
…)"`), and both report Texas at 3,830,414 windows with `exact_match: true` against Table 8. So the
ceiling at Texas is one loader swap away, not a preprocessing re-run. Either reuse that loader or say
that a rebuild path exists and was not taken.

### m-6 · "Every metric is read against reference points" is not true of Chapters 3 and 4

**Lens 8 — MINOR.** `2_fundamentals.tex:482`: *"Every metric is read against reference points"*,
followed by the majority-class floor and the Markov floor. Neither chapter reports either: no
occurrence of `majority`, `floor`, `Markov`, or `chance` in `3_cbic.tex` or `4_courb.tex`. §2.4
already handles the analogous problem correctly for inference — *"the tests set out below license
verbs in Chapter~\ref{ch:mobiwac} alone"* (`:503-505`) — so the floors sentence needs the same
scoping. (The macro-averaging convention *is* honored: `3_cbic.tex:294` reports the macro average and
`4_courb.tex:252` the *"Average F1-Score per category"*, which is the same quantity under the
published name.)

### m-7 · The naming bridge is adequate for a linear reader and absent from every navigational surface

**Lens 7 — MINOR.** The prefaces are explicit and well written (`3_cbic.tex:27-31`: *"the term
``Next-POI Prediction'' as used in the reproduced article denotes the frame's \emph{next category}
task … not the exact place itself"*; the Chapter 4 preface repeats it), and the abstract and
`1_introduction.tex` state the non-claim plainly. But the old name still governs everywhere a referee
navigates: the List of Figures (p6), List of Tables (p7 — *"Average F1-Score (%) per model and state
for the Next-POI Prediction task"*), the table of contents (pp10–11), 18 running headers (pp27–42, 56,
57), and Chapter 3's own title line, whose bracketed short title repeats the full published title
(`3_cbic.tex:11`). So the document contains a chapter titled with a task the document says it does not
perform, and a reader who skims front matter and table captions meets the old name without the bridge.

For a mobility reader I judge this **sufficient but fragile**: the definitions are correct wherever
the term is introduced (`3_cbic.tex` numbered list, `4_courb.tex:24`), so nobody who reads a
definition is misled. The cheapest hardening is one footnote on the first results table of each
published chapter, and a one-line note in the front matter; the published titles should stay as
published.

### m-8 · Istanbul's counts differ from the published table with no reconciliation

**Lens 9 — MINOR.** Table 8 reports Istanbul at 462,615 check-ins / 23,694 users / 29,816 POIs
(`5_mobiwac.tex:354`). Massive-STEPS' own Table 2 reports Istanbul at 544,471 check-ins / 23,700 users
/ 53,812 POIs (read from the preprint). The difference is documented internally —
`docs/studies/second_dataset/STATS_T1.md:106`: *"Null-coord check-ins | 62,621 (11.5%) | dropped"* —
but the chapter states no filtering at all for Istanbul, and a referee holding the benchmark paper
open will see two POI counts differing by 24,000. One clause naming the null-coordinate drop closes it.

### m-9 · The monotonicity reading is unhedged where the reader meets it first

**Lens 7 — MINOR.** `5_mobiwac.tex:72` (chapter summary): *"the region result moves monotonically with
the region count"*. The results section is properly careful about the same reading at `:642-643`:
*"region count and corpus size co-vary here, so we read the trend across the points rather than as a
precise law."* With six datasets and two confounded axes, "monotonically" is the stronger word and it
appears where the hedge does not. Move the qualifier forward.

---

## NITS

### n-1 · The inflation figure drops its approximation marker
`5_mobiwac.tex:376-395` reports the whole-dataset prior *"inflated region accuracy by 13 to 27
points"*. The source record is `docs/research/evaluation_protocol_review.md:39`: *"leaked ~13–27 pp
into the reg prior"*. The tilde is load-bearing in a document this careful about conventions.

### n-2 · "a representative state" is doing work a named state would do better
`2_fundamentals.tex:458-459`: *"The Food class alone accounts for roughly a third of the check-ins in a
representative state."* True of Alabama (33.75% of check-ins; Table 8's next-visit majority 34.2%),
but Florida's majority share is 24.7% in the same table. Name the state.

---

## Credibility signals present

These are the things that would make me trust the final study, and they are unusually strong for a
master's dissertation in this area.

1. **The three prediction targets are held apart with discipline, and the non-claim is stated where it
   counts.** `2_fundamentals.tex:50-63` defines next place, next category, next region, and a fourth
   static task, then states *"It does not predict the exact next place; that target is named only to
   hold it apart from the two the dissertation studies."* The abstract and Chapter 5 (`:235`) repeat it.
   I found no sentence anywhere in 97 pages that implies exact-place prediction.
2. **The next-region metric is defined honestly and its two conventions coincide.** `5_mobiwac.tex:418-420`:
   *"a visit whose true region is absent from that fold's training data counts as an error."* The
   reported cells use `top10_acc_indist · (1 − ood_fraction)`
   (`docs/studies/closing_data/joint_best/JOINT_BEST_SCORING.md:19`), which reduces to hits over all
   validation rows — arithmetically the same denominator as the Markov floor's unrestricted scoring
   (`markov1_region_fold` in `compute_markov_floor_stride1.py:297-330`, train-only transition counts,
   global top-10 fallback). The floor comparison at `:771` is therefore apples to apples. This is the
   detail most often botched in region-level papers, and it is right here.
3. **The region-transition prior is handled correctly and described accurately.** Verified end to end:
   the whole-dataset version was the leak vector (`evaluation_protocol_review.md:39`); priors are now
   per fold and per seed (`output/check2hgi/<state>/region_transition_log_seed*_fold*.pt`); the shipped
   joint model folds the prior out entirely, provably (`src/training/runners/mtl_cv.py:552-574`
   `_log_t_is_inert`: α frozen at 0 and all distillation routes off, default-on skip); the dedicated
   region ceiling was measured prior-off (`CEILINGS_N20_FINAL.md:64`); and the baseline that does use
   it declares it as a deviation (`b3_seed0_folds5.json` → *"per-fold train-only region transition
   prior"*). `5_mobiwac.tex:376-395` states exactly this. **This lens finds nothing to report.**
4. **The user-disjoint split is real and the overlap question was actually asked.** Stratified grouped
   folds by user id, all of a user's windows in one fold, verified in the splitter and in the audit
   (`PIPELINE_AUDIT_2026-06-03.md:22-24`, including the honest note that the 22.4% target-in-history
   rate is *"legitimate user revisits, unchanged by overlap"*). The protocol strengthening across the
   three studies is disclosed rather than smoothed (`2_fundamentals.tex:503-508`).
5. **Cited systems are described as their own authors describe them, with two exceptions (M-1, M-2).**
   I checked against sources of record: HMT-GRN's hierarchical beam search over region and POI
   distributions; CatDM's category-based candidate pruning; DRRGNN's per-person activity regions
   (`5_mobiwac.tex:159-161` even notes *"over regions discovered per person rather than a fixed
   citywide partition"*); GETNext's global trajectory-flow map; GeoSAN's hierarchical gridding;
   STAN's non-adjacent visit correlations; CTLE's visit-dependent vectors; Time2Vec, SIREN, Space2Vec,
   Sphere2Vec at their own origins; MCARNN's parallel activity-plus-location pairing (I read the full
   text: it explicitly rejects *"a rigid human-defined modeling strategy"* in either direction, so
   "in parallel" is fair). POI-RGNN could be checked only against title and venue — the source of
   record returns no abstract.
6. **A claim about a competitor's ablation was verified in the competitor's paper.** `5_mobiwac.tex:777`
   says CSLSL *"reports its chain outperforming a shared-trunk parallel variant on its own
   benchmarks"*. I read the full text: it proposes five task-relation variants including a
   shared-bottom parallel arm and reports the causal chain ahead of it. Checking a rival's internal
   ablation before using it to motivate your own design choice is rare and correct.
7. **The HGI repurposing is declared.** `2_fundamentals.tex:166-169` states that Huang et al. present
   HGI for urban region representation and evaluate it on region-level estimation, so this work
   repurposes its POI-level output for a sequential task their paper does not address. Confirmed
   against the paper's abstract and its three downstream tasks (urban function, population density,
   housing price). Very few dissertations disclose a baseline repurposing this cleanly.
8. **The predictability bound is correctly rescoped.** `2_fundamentals.tex:486-489` binds the 93%
   figure to *"predicting the next location at coarse resolution"* and states it is *"not, however, a
   ceiling on seven-class category macro-F1 or on region ranking, which are different label spaces."*
   Read against the source PDF, that is the right reading of a number this field routinely misuses.
9. **The label-only ceiling separates two quantities the internal record conflated.** Appendix D's
   distinction between the ceiling (a property of the label sequence) and the clean reference encoder
   is correct, its numbers all read back from `autocorrelation_ceiling.json`, and its conclusion is
   the weaker and honest one: the screen *"bounds encoders against each other rather than against an
   absolute standard."* The Istanbul ambiguity sensitivity (0.3009 against 0.3016) is reported.

---

## Unstated defenses — facts the repository holds that the text does not use

Each of these would answer a question a referee is likely to ask, and costs a sentence.

1. **A stronger leak gate exists, was run, and is the authoritative one.** `5_mobiwac.tex:396`
   discloses that the probe is linear and that one encoder passed it and leaked under a sequence
   model — but stops there, which leaves the impression that the screen is all there was.
   `docs/results/embedding_eval/rescreen_cat/RESCREEN.md` records the follow-up: *"The authoritative
   leak gate is L2-next-cat-F1 vs the same-protocol control"*, catching both problem encoders
   (0.96 and 0.754 against a control at 0.646), with the per-step linear probe explicitly demoted to
   *"a cheap pre-screen for scale-independent leaks only."* Naming the stronger gate turns a declared
   weakness into a two-gate audit.
2. **The transductive channel was measured, not assumed.** Rebuilding the representation per fold from
   training users only moves both tasks by at most a third of a point — this *is* in the text
   (`:376-395`), including the honest coverage caveat (67–87% of visits). Worth knowing that the
   underlying record (`A4_RESULTS.md:20`) also quantifies the inductive gap in region terms:
   *"AL inductive gap 2.6–2.8% of regions absent from train"*, which is the same order as the OOD
   fractions above and corroborates the region side independently.
3. **The revisit rate is measured and benign.** 22.4% of Alabama windows contain their target in their
   own history, audited as *"legitimate user revisits"* with the demoted target removed from its own
   history at emission (`WINDOWING_AUDIT.md:13`). No repeat-versus-explore intuition appears anywhere
   in the text. For a mobility audience this is a standard descriptive statistic and it also supplies
   the explanation B-2 needs for why the persistence-style floor is so strong.
4. **The category crosswalk for Istanbul was built and its divergences catalogued.** Chapter 5 says
   only *"Istanbul's source collection maps its places onto the same seven labels"* (`:235`).
   `docs/studies/second_dataset/category_map.md` documents the crosswalk and its judgement calls, and
   `STATS_T1.md:107-108` records that Istanbul's category profile diverges sharply from the U.S. one
   (Outdoors 26.8% against 12.9%, Nightlife 4.8% against 10.5%), arguing this makes Istanbul *"a
   stronger external-validity probe"*. That argument belongs in the external-validity subsection; as
   written the reader cannot tell whether the mapping was principled.
5. **The prediction horizon was characterized per dataset.** `:372-375` reports the median and the
   over-three-days share. The committed record has the full distribution and a window-count gate
   against Table 8 (`horizon_stride1/*.json`, `within_1pct: true` at every dataset, exact at five of
   six). If the Istanbul vintage sentence lands (M-5), these numbers are the evidence for it.

---

## Scope notes

- I did not review MTL architecture, optimizer, or statistical-test content except where a dataset,
  task, or metric claim depended on it; personas 9 and 10 own those.
- Prose, style, and glossary compliance are out of scope; I flagged wording only where it changes what
  a mobility claim asserts (M-2, m-3).
- Every number above is quoted from a committed file, a primary source I opened this session, or a
  first-hand measurement of a committed data file that I identify as such (the fine-grained-category
  table in B-1, the Gowalla and Istanbul date ranges, the tract and mahalle polygon counts, the
  cross-block user and gap counts). Where I could not verify, the finding is marked [UNVERIFIED]
  (M-8) rather than asserted.
- Two chapters in scope are time capsules. Corrections in B-1 (Chapter 4 preface), B-2, M-1, M-2, and
  M-6 (Chapter 4's vintage sentence) touch reproduced prose and need Appendix B rows; everything in
  Chapter 2, Chapter 6, Appendix D, and the introduction is frame prose and needs none. B-2, M-1 and
  M-2 also live in the paper still under review, where they can be fixed in the camera-ready rather
  than declared as errata.


---

<!-- estado-rodada -->
> **Rodada encerrada · último toque 2026-07-26 · sem autoridade.**
> Este ficheiro é registo de proveniência do que foi discutido nesta passagem, não fonte
> de um facto corrente. O que ficou decidido está em [`VEREDITOS.md`](../../../VEREDITOS.md);
> os valores entregues estão em `CLAUDE.md` §0.1. Não copie nada daqui sem confirmar lá.
