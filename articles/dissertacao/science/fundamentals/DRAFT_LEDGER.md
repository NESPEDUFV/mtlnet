# DRAFT_LEDGER — citation & number ledger for the 2.1-2.5 LaTeX drafts

> **2026-09-30:** os rascunhos `.tex` desta pasta sairam da arvore -- eram uma copia superada do texto entregue, com numeros de outra geracao. Os ledgers de citacao (`*_citations.md`) ficam. Tudo recuperavel na tag `dissertacao-pre-organizacao` do PoiMtlNet.

<!-- WRITING_LAW requires each draft to ship with a numbers/citation ledger. Each .tex file carries its
     own per-section ledger as a trailing LaTeX comment; this file is the consolidated view for the review
     pass. Draft 1, 2026-07-21. -->

## Word budget (each section <= 1,500 words; thin chapter ~8-12pp)
| Section | ~prose words | File |
|---|---|---|
| 2.1 POI-prediction tasks | ~750 | 2.1_poi_prediction_tasks/2.1_poi_prediction_tasks.tex |
| 2.2 Representations for mobility | ~810 | 2.2_representations_for_mobility/2.2_representations_for_mobility.tex |
| 2.3 Multi-task learning | ~750 | 2.3_multi_task_learning/2.3_multi_task_learning.tex |
| 2.4 Datasets and evaluation | ~685 | 2.4_datasets_and_evaluation/2.4_datasets_and_evaluation.tex |
| 2.5 Relevance | ~540 | 2.5_relevance/2.5_relevance.tex |
| **Total** | **~3,535** | + fundamentals.tex (wrapper), model_lineage_table.tex |

## Numbers used (each traceable; quoted, not computed)
| Number | Where | Source | Status |
|---|---|---|---|
| **93% potential predictability** | 2.1, 2.4 | song2010limits, Science 327:1018 | VERIFIED firsthand from PDF this session. The "80%" is a low-predictability example (Pmax=0.2), NOT a population figure -- deliberately not quoted. |
| **seven categories** (Community/Entertainment/Food/Nightlife/Outdoors/Shopping/Travel) | 2.1 | docs/context/TASKS.md | repo-internal taxonomy, quoted |
| region counts "a few hundred to several thousand" | 2.1 | qualitative; exact per-dataset counts deferred to Ch.5 | not a Ch.2 number |
| **Food ~ a third of check-ins** | 2.4 | docs/context/TASKS.md (~32-34%) | quoted qualitatively, NOT recomputed in prose |
| **Acc@10** ("ten highest-ranked") | 2.4 | metric definition | convention |
| **two-point margin** (TOST) | 2.4, 2.5 | GLOSSARY / METRICS.md | convention |
| **four of six datasets** + region non-inferiority at the other two | 2.5 | NORTH_STAR §6 result summary | bound to paired tests + TOST; AZ never upgraded |

## Citations: 67 distinct keys, ALL resolve against the project bib universe (0 dangling)
- New keys (in `_bib/new_references_ch2.bib`, 26): kong2018hstlstm, lian2020geosan, mikolov2013word2vec,
  perozzi2014deepwalk, kipf2017gcn, hamilton2017graphsage, belghazi2018mine, hjelm2019dim, kazemi2019time2vec,
  ruder2017mtloverview, tang2020ple, hazimeh2021dselectk, kendall2018uncertainty, liu2021cagrad, lin2022rlw,
  yang2015tsmc, sokolova2009measures, gambs2012mmc, kohavi1995crossval, pedregosa2011sklearn, wilcoxon1945,
  lakens2017tost, maninis2019attentive, (+ lin2017focal, leskovec2016snap, he2016lbpr held in the bib, not all cited).
- Coverage-addition keys threaded (ALREADY in project bibs, existing keys, no new entry): sener2018mgda,
  standley2020tasks, yu2024survey (CBIC); silva2019urbancomputing (MobiWac);
  rußwurm2024geographiclocationencodingspherical (CoUrb).
- All other keys are pre-existing project-bib keys.

## Errata flagged inline (LaTeX comments) for the author to apply to the global bib
- misra2016cross -> DOI 10.1109/CVPR.2016.433 ; velivckovic2017graph -> cite ICLR 2018 ;
  church2017word2vec -> mikolov2013word2vec ; navon2022nashmtl -> consolidate double-key/slash ;
  velickovic2019deep -> consolidate DGI triple-key ; capanema2023poirgnn -> correct POI-RGNN paper.
  Full table: articles/CBIC___MTL/ERRATA.md and _bib/BIB_NOTES.md.

## Writing-law mechanical checks (self-run this session)
- em-dashes: 0 ; triple-dash: 0 ; contractions: 0 (possessives user's/model's/task's are correct, not contractions).
- Banned AI-tell words: 0 (removed "genuinely" from 2.5).
- Repo codenames: 0 ; forbidden result verbs after review fixes (beats/wins/ties/Pareto): 0
  (NOTE: draft-1 self-cert wrongly said 0 while 4 instances of "beat" were present; the fact gate caught this;
  all 4 are now reworded to "outperform"/"do not outperform").
- "does not predict the exact next place" stated once, in 2.1, after the three targets are defined.
- Status wording "submitted, under review" present for the MobiWac work (2.5, lineage table).
- Metrics defined defensively (macro-F1, Acc@10, Δm, floors) with formula/plain reading/boundary (see 2.4 + addendum).

## What the review pass should check (not self-certifiable)
- Claim-support: does each cited sentence match what the source actually says? (fact gate)
- Domain correctness of the MTL and POI/representation characterizations. (domain experts)
- Prose burstiness / AI-tell distributional check beyond the token list. (style)

---

## Specialist review outcome (2026-07-21) + fixes applied (draft 2)

Two independent read-only panels reviewed the draft-1 sections:
- **G2 Fact gate** (DISSERTATION_FACT_GATE, personas 05 citation / 06 number / 07 honesty): verdict GATE FAIL
  (2 BLOCKER, 6 SHOULD-FIX, 8 NOTE). 67 cite keys, 0 dangling; 32 DOIs re-resolved firsthand (27 exact, 1
  wrong-paper). Full report: fact_gate_report.md.
- **Domain panel** (DISSERTATION_REVIEWER, persona 10 MTL / 11 POI-mobility): verdict SOUND-WITH-CORRECTIONS
  (1 BLOCKER, 5 SHOULD-FIX, 3 NOTE). Full report: domain_review_report.md.

### BLOCKERS — fixed
1. **2.2 Check2HGI mis-cited to `silva2025mtlnet`** (that key = the CBIC/MTLnet paper, not Check2HGI; the
   MobiWac work has no bib entry and is submitted/under review). FIX: removed the cite; Check2HGI now defers to
   `\ref{ch:mobiwac}` + the lineage table (as the table already did). No published-status implication.
2. **2.2 encoder attribution inverted** ("Chapters 3 and 4 use FiLM and these encoders"). MTLnet (Ch.3) uses
   only the place embedding + per-task FiLM; the decomposed spatial/temporal/categorical encoders are CoUrb's
   (Ch.4) contribution, and this is the arc's turning point. FIX: FiLM described as per-task conditioning;
   context described as entering by decomposition in Ch.4 only; Space2Vec noted as named-but-not-adopted.
3. **`misra2016cross` DOI = wrong paper** (`.434` = Deep Metric Learning; correct Cross-Stitch = `.433`).
   Author-owned CBIC bib fix — already recorded in articles/CBIC___MTL/ERRATA.md (item 4, verified).

### SHOULD-FIX — fixed
- **Region-as-end-target contradiction (2.1 vs 2.3)**: 2.3 universal scoped to the multi-task co-equal setting;
  single-task region prediction (zhu2022drrgnn, 2.1) explicitly acknowledged.
- **Negative transfer miscredited to `Zhang2020` (iMTL recommender)**: definition folded onto the already-cited,
  verified `standley2020tasks`; `Zhang2020` cite removed from 2.3.
- **FiLM mechanism inverted**: corrected to per-task γ/β conditioning; context enters by concatenation (matches
  GLOSSARY + CBIC/CoUrb method sources).
- **Missing scalarization-skeptic anchor**: added Kurin et al. NeurIPS 2022 "In Defense of the Unitary
  Scalarization" (`kurin2022scalarization`, arXiv:2201.04122); arXiv record + claim verified firsthand this
  session; NeurIPS 2022 venue seen in a search-result title only ([VERIFY] flagged in the bib comment; entry carries no DOI).
- **93% ceiling over-applied to category/region**: rescoped in 2.4 to a next-location predictability bound; the
  dedicated single-task model named as the operative ceiling for the two studied tasks.
- **Dataset count "two" but three named**: Foursquare (yang2015tsmc) marked context-only, explicitly not used;
  "the two" = Gowalla + Massive-STEPS/Istanbul.
- **Win-verb unbound in 2.5**: now "by paired superiority tests, outperforms ... and matches ... by
  non-inferiority testing"; forward-points to Ch.5.
- **Banned "beat" x4** (2.3 x2, 2.4 x1, 2.5 x1): all reworded to "outperform"/"do not outperform".
- **"descends from PLE" imprecise**: reworded to the structured-sharing PRINCIPLE the joint model adopts
  (realized with cross-attention, not expert gating).
- **pedregosa2011sklearn date mismatch**: single-cite ruling retained (author decision); splitter behavior
  stated defensively; ledger notes StratifiedGroupKFold is a v1.0/2021 feature.

### NOTES — recorded for the author (not blocking; several are adaptation-time actions)
- Food "roughly a third" is a single representative state (Alabama check-in dist., Food 34.2%); addendum
  provenance pointer to be corrected to the check-in table, not the 32.5% POI-count table.
- "four of six datasets" + two-point margin: the routing that stood here sent the reader to a board
  that is dead for this dissertation. Ch.5 numbers come from the table file itself,
  `src/tables/mobiwac/*.tex`, whose per-value provenance comment is what the fact gate follows
  (`CLAUDE.md` §0.1). The claim itself is time-indexed: see `VEREDITOS.md` V6.
- OOD region metric foreshadowed in 2.4 (unseen region = miss); full OOD-Acc@10 definition deferred to Ch.5.
- DGI triple-key and Nash-MTL slash-key consolidation before compiling the single global bib (in BIB_NOTES §B).
- kohavi1995crossval claim PLAUSIBLE (Zenodo re-deposit id); confirm original IJCAI-95 text at adaptation.
- FPMC (Rendle 2010) optionally added at the head of the next-place lineage; kept representative by design.
- Massive-STEPS is a 2025 preprint; re-check for a peer-reviewed version before the August 2026 defense.

### Not applied (out of the fundamentals scope, routed to the author)
- Kurin theory follow-ups (Hu 2308.13985, Royer 2310.08910) and evaluation-critique canon (Dacrema, Sánchez &
  Bellogín, POI Pitfalls) — 2.5 is citation-free by design; if any is wanted it belongs at the first mention of
  evaluation rigor in 2.4. Left to the author.
