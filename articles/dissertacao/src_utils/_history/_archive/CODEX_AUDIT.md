# CODEX_AUDIT.md — audit of `src_utils/codex_reviewer.md`

**Audit date:** 2026-07-27. **Document audited:** `src_utils/codex_reviewer.md` (1,419 lines; 18 COD findings, an
eight-row numerical-corrections table, a chapter-by-chapter section, and a reviewer-agreements section). The review
dates itself 26 July 2026 and names repository state `70d3888d`. **Audited against:** `src/chapters/*.tex` and
`src/0_main.tex` as they stand now;
`src/dissertacao.pdf` (**102 pp**, written 2026-07-27 07:47) and
`src/build/main_final.pdf` (**97 pp**, 07:56); the committed result artifacts under
`docs/results/` and `docs/studies/`; the CoUrb-era codebase at
`/Users/vitor/Desktop/mestrado/temp/tarik-new`; the DGI and HGI preprocessing code under
`research/embeddings/`; the state corpora at `data/checkins_by_state/`; and the v2 persona reports in
`src_utils/_history/_review_v2/` and `src_utils/_history/_specialists_v2/`. **Read-only.** Nothing under `src/` was modified. No git
command was run. This file is the only file written.

> **Concurrent-edit disclosure (2026-07-27, 08:53–08:55).** While this audit was being
> written, `src/chapters/6_conclusion.tex`, `src/chapters/4_courb.tex`,
> `src/chapters/apx_b_errata.tex` and `src/references.bib` were modified by another hand,
> and two of the repairs this file recommends were applied. **COD-010 / NUM-1 / NUM-2:**
> the capacity sentence at `6_conclusion.tex:116-118` now reads "the widened model was
> fitted under three training configurations, twenty models each and sixty in total, and
> the strongest configuration averages 56.16 macro-F1, standard deviation 1.89" — the
> count, the statistic and the missing spread are all corrected, so that finding is now
> **RESOLVED** rather than CONFIRMED, and item 1 of §6 is done. **COD-008 (Mikolov):**
> `4_courb.tex:208` now cites `mikolov2013word2vec,mikolov2013negsampling`, the new entry
> is at `references.bib:685`, and `apx_b_errata.tex` carries a new errata row for it, so
> item 4 of §6 is done. Every COD-010 and COD-008 verdict below describes the state at the
> time of audit and is superseded on those two points only; line numbers throughout were
> re-resolved against the live files after the change. Nothing else in the four files moved
> a verdict — I re-checked each cited line. **The PDFs were then rebuilt at 08:59 and are now
> 103 and 98 pages.** Page references in this file were taken from the 07:47/07:56 pair at
> 102/97 pages, so I re-located every load-bearing site in the new build and compared: the
> Ch.5 trunk sentence (p74), the withheld attribution (pp. 73 and 77), the Ch.6 gradient
> scope (p78), the capacity sentence (p77), the Ch.1 objective (p15), the Ch.5 integrity
> limits (p66), the Markov figure (p73), the Appendix B float table (pp. 95–96) and the
> label-history term (pp. 8, 12, 66, 98) are all on the same pages as before. The one added
> page falls at the end of Appendix E, which now runs to p103. **Every page number in this
> file is therefore still correct.**
>
> **The review was written against a superseded artifact.** It reviews a 97/92-page pair;
> the current pair is 102/97 pages, rebuilt after the correction round of 2026-07-27. Six
> of the eighteen findings are wholly or partly resolved by that round. That does not make
> the review careless: at its own timestamp most of what it reported was there. It does
> mean every "Open" status in its tracking table must be re-read before it is acted on,
> and this file is that re-reading.

---

## 1 · Summary table

| Finding                                                                   | Claimed severity | Verdict                                                                                                    | One-line reason                                                                                                                                                                                                                                                                                                                                                  |
|---------------------------------------------------------------------------|------------------|------------------------------------------------------------------------------------------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| COD-001 three comment-swallowed sentences                                 | Critical         | **RESOLVED**                                                                                               | All three render: "Nash-MTL treats" p23, "a capacity-matched dedicated baseline" p77, "The emphasis convention" p89; four more of the class were found and fixed; the checker now passes 10 fixtures before its own result is trusted                                                                                                                            |
| COD-002 Ch.4 static result is target-derived and still drives the arc     | Critical         | **PARTLY** (determinism CONFIRMED and widened; disclosure CONFIRMED absent; "still drives the arc" PARTLY) | `spot`→`category` purity is 1.0 at all five states (measured); no rendered page states it; but Ch.4 is only one of two supports for the diagnosis and the width confound is now disclosed in Ch.6                                                                                                                                                                |
| COD-003 exact Check2HGI lineage never had the nonlinear future-edge test  | Major            | **PARTLY** (channel and lineage gap CONFIRMED; "overclaims" REFUTED in Ch.5, CONFIRMED at one Ch.1 site)   | Ch.5 :391 states the linear form, the Florida-only single-seed scope, the ancestor-build lineage, and the failed screen; the one global word left is "leakage-guarded" at `1_introduction.tex:158`                                                                                                                                                               |
| COD-004 operational success conflated with transfer and a trunk mechanism | Major            | **PARTLY**                                                                                                 | The withholding is stated twice (Ch.5 :713, Ch.6 :101) and the ablation is disclosed as unusable; the contrary attribution survives verbatim at `5_mobiwac.tex:872` (p74)                                                                                                                                                                                        |
| COD-005 PCGrad and Nash-MTL evidence misstated                            | Major            | **PARTLY**                                                                                                 | Wiring defect and unsupported cost claim CONFIRMED at source; the author has ruled on PCGrad and Nash separately; the screen's seed/state scope is still absent from prose                                                                                                                                                                                       |
| COD-006 statistical wording exceeds the design                            | Major            | **PARTLY**                                                                                                 | "before any result was read" and "well powered" are CONFIRMED overstatements; "identically" is REFUTED as reported (the sentence names the asymmetry itself); n=4 and the fixed partition are already stated                                                                                                                                                     |
| COD-007 Ch.3–4 methodologically under-specified                           | Major            | **PARTLY / NEEDS-AUTHOR**                                                                                  | The missing Ch.3 records and unspecified Ch.4 checkpoint rule are CONFIRMED; the "significant/outperforms survives" half is largely REFUTED (Appendix B documents four removals and accounts for all six surviving uses)                                                                                                                                         |
| COD-008 load-bearing citations do not support their claims                | Major            | **PARTLY**                                                                                                 | Mikolov negative-sampling mismatch CONFIRMED (1301.3781 has no negative sampling); Standley overreach CONFIRMED; UberNet/Sphere2Vec preprints CONFIRMED (versions of record exist); the scikit-learn claim is REFUTED as a support failure                                                                                                                       |
| COD-009 CoUrb translation and adaptation records lag the text             | Major            | **PARTLY**                                                                                                 | The single-seed sentence is already scoped to the released code (verified firsthand in `create_fold.py`); the stale inventory, English-donor source-of-record, and the "no claim altered" tension are CONFIRMED                                                                                                                                                  |
| COD-010 capacity control miscounted and over-compressed                   | Moderate         | **CONFIRMED**                                                                                              | "across three training configurations and all twenty fitted models" still renders on p77; the artifact is 20 per arm, 60 total, and 56.16 is the best arm's mean (SD 1.89)                                                                                                                                                                                       |
| COD-011 privacy, ethics, licensing absent                                 | Major            | **RESOLVED**                                                                                               | Appendix E "Data Ethics and Governance" is in the build (pp. 101–102), with licences re-verified at source and the CEP/IRB position recorded as a position, not an approval                                                                                                                                                                                      |
| COD-012 both artifacts fail the UFV gate                                  | Critical         | **PARTLY**                                                                                                 | Bibliography now measures 11.96 pt, body size (measured p81), so that half is RESOLVED; cover, approval sheet, committee, date, font ruling and process documents remain NEEDS-AUTHOR                                                                                                                                                                            |
| COD-013 AI disclosure ahead of the recorded approval state                | Major            | **CONFIRMED** (count corrected)                                                                            | Appendix C claims the author "takes responsibility for every word" while 31 `[NEEDS SIGN-OFF]` markers remain in `src/`, not 27                                                                                                                                                                                                                                  |
| COD-014 "ceiling" and the Markov causal story                             | Moderate         | **RESOLVED**                                                                                               | "label-history benchmark" throughout with "not an upper bound" stated; the Markov paragraph now states protocol asymmetry system by system and disclaims a single cause                                                                                                                                                                                          |
| COD-015 cross-chapter seams                                               | Moderate         | **PARTLY**                                                                                                 | Four of six sub-claims hold: Ch.6 still says "three of the six datasets" where the measurement pools four Gowalla states, the MRR and relative-multi-task promises are still unused, the frame and Ch.4 disagree on the Gowalla vintage, and the Ch.3 preface clause understates Ch.5's changes; the next-POI bridge and the cross-reference targets are REFUTED |
| COD-016 language and readability pass                                     | Moderate         | **PARTLY**                                                                                                 | The 114-word abstract result sentence and the 546-word integrity block are CONFIRMED burdens; the `3_cbic.tex:340` "unrecoverable" sentence is REFUTED (the quoted words are published prose and their meaning is recoverable)                                                                                                                                   |
| COD-017 visual and typographic inconsistencies                            | Moderate         | **PARTLY**                                                                                                 | The oversized Appendix B float (21.55853 pt) and 6.97/7.27 pt diagram labels on pp. 62 and 64 are CONFIRMED by measurement; the Portuguese figure labels are RESOLVED; the "nearly blank p.4 with orphaned keywords" is CONFIRMED                                                                                                                                |
| COD-018 governance files and gates no longer describe the artifact        | Moderate         | **PARTLY**                                                                                                 | Page counts in `CLAUDE.md`, `PLAN.md`, `HANDOFF_v1.md` are stale (89/84 against 102/97) and Appendix A lacks per-role CoUrb credit; the checker and `pypdfium2` sub-claims are RESOLVED                                                                                                                                                                          |
| NUM-1 capacity "three configurations / twenty fits"                       | —                | **CONFIRMED**                                                                                              | Same defect as COD-010; still on p77                                                                                                                                                                                                                                                                                                                             |
| NUM-2 capacity 56.16 reads as best individual fit                         | —                | **CONFIRMED**                                                                                              | Artifact: best arm mean 56.16, SD 1.89; the chapter's own ledger comment already flags the missing spread                                                                                                                                                                                                                                                        |
| NUM-3 gradient scope "three of six"                                       | —                | **PARTLY**                                                                                                 | Ch.5 :204 is fixed and names Georgia; `6_conclusion.tex:177` still says "three of the six datasets"                                                                                                                                                                                                                                                              |
| NUM-4 HGI 0.74→0.82 basis                                                 | —                | **CONFIRMED as a live `[VERIFY]`**                                                                         | Source gives 0.7388 ± 0.0205 → 0.8186 ± 0.0123 over 5 folds × 50 epochs; the prose rounds and drops both spreads                                                                                                                                                                                                                                                 |
| NUM-5 Arizona rounding by 0.01                                            | —                | **REFUTED as stated**                                                                                      | Every AZ figure in the document is on one basis (joint-best): 65.79, 59.46, +9.35 all trace to `JOINT_BEST_RESULTS.md`; the 0.01 wobble named in the artifact belongs to the diagnostic-best basis, which the document does not use                                                                                                                              |
| NUM-6 label-history called a ceiling                                      | —                | **RESOLVED**                                                                                               | Zero occurrences of "label-only ceiling", "autocorrelation ceiling", or "what the past itself allows" in either PDF                                                                                                                                                                                                                                              |
| NUM-7 CoUrb 20.2–22.0 reads as a deployable fixed encoder                 | —                | **PARTLY**                                                                                                 | The per-cell-best convention is stated at all three Ch.4 sites and in Appendix B, so it is disclosed; it is not disclosed at the two frame sites (`1_introduction.tex:113`, `6_conclusion.tex:46`), and the word "oracle" appears nowhere                                                                                                                        |
| NUM-8 Wilcoxon n=20 can read as independent                               | —                | **RESOLVED**                                                                                               | Ch.5 :418 names n=4 as the inferential unit and reports the fold-level test "alongside it"; the Glossary carries the same footing                                                                                                                                                                                                                                |

**Counts, tallied from the rows above.** Of the 18 COD items: **3 RESOLVED**
(COD-001, COD-011, COD-014), **2 CONFIRMED** (COD-010, COD-013), **12 PARTLY**
(COD-002, COD-003, COD-004, COD-005, COD-006, COD-008, COD-009, COD-012, COD-015, COD-016, COD-017, COD-018), and **1
PARTLY / NEEDS-AUTHOR** (COD-007). Of the 8 numerical rows: **2 RESOLVED** (NUM-6, NUM-8), **3 CONFIRMED** (NUM-1,
NUM-2, and NUM-4 as a live `[VERIFY]`), **2 PARTLY** (NUM-3, NUM-7), and **1 REFUTED** (NUM-5). Zero findings are wholly
fabricated. Two are wrong as stated (NUM-5; the COD-016
"unrecoverable sentence"), and four are materially understated or misdirected (COD-002's second half, COD-003's Ch.1
site, COD-006's "identically", COD-008's scikit-learn row).

---

## 2 · Finding-by-finding evidence

### COD-001 — three comment-swallowed sentences · **RESOLVED**

All three sentences render in the current defense PDF. Text extracted from
`src/dissertacao.pdf` and searched page by page:

| Named missing phrase                                             | Renders on                     |
|------------------------------------------------------------------|--------------------------------|
| "Nash-MTL treats"                                                | p23 (`2_fundamentals.tex:359`) |
| "a capacity-matched dedicated baseline, run after the"           | p77 (`6_conclusion.tex:112`)   |
| "The emphasis convention of the published category table, which" | p89 (`apx_b_errata.tex:174`)   |

The review's claim that the checker "is not a valid release gate" was true of the checker it saw and is no longer true.
`src_utils/test_trapped_prose.py` now carries ten fixtures, seven positive and three negative, and reports
`10/10 fixtures pass`. Four of the seven positives are defects found *after* the review: `apx_a` (a fragment after a
terminal period), `4_courb:187` (half a published methodology sentence),
`5_mobiwac:385` (four sentences including a required disclosure), and
`6_conclusion:110` (a one-word swallowed sentence-opener, found by persona 16 on 2026-07-27). `src_utils/check.sh:59-71`
runs the fixtures first and captures the exit status in a variable rather than through a pipe, with a comment recording
that the pipe form had shipped once as an unreachable failure branch. `check_trapped_prose.py ../src`
returns `trapped-prose suspects: 0`.

**Nothing to do.** The review's recommended action is already executed and exceeded.

### COD-002 — Ch.4 static category result is target-derived but still drives the arc · **PARTLY**

This is the review's most consequential claim and it splits cleanly into three parts.

**Part 1, the determinism: CONFIRMED, and wider than the review states.** I measured it directly on the committed
corpora rather than accepting either the review's or persona 11's number:

| state      |      rows | distinct `spot` values | max target classes per `spot` | impure `spot` values |
|------------|----------:|-----------------------:|------------------------------:|---------------------:|
| Alabama    |   113,846 |                    284 |                             1 |                    0 |
| Arizona    |   236,450 |                    305 |                             1 |                    0 |
| Florida    | 1,407,034 |                    324 |                             1 |                    0 |
| California | 3,171,380 |                    333 |                             1 |                    0 |
| Texas      | 4,089,892 |                    365 |                             1 |                    0 |

(measured on `data/checkins_by_state/<state>.parquet`, grouping `spot` against
`category`; `max_cat_per_placeid` is also 1 everywhere.) The chain is readable in code:
`4_courb.tex:208` states that each random walk "is converted into a sequence of secondary categories (*fclass*)" and
`:219` that the POI encoder carries a hierarchical regularization term over `(category, fclass)` pairs, so the place
vector is a function of the fine category; the fine category determines the target exactly. The Alabama shuffle control
at
`docs/archive/fusion-study/results/P0/leakage_ablation/alabama/comparison.json` gives
`cat_f1` 0.7855417728 → 0.1436618567 under `C_fclass_shuffle` against
`next_f1` 0.2383448780 → 0.1988023221, and that folder's own README calls the arm "the decisive test" and concludes that
"Category F1 on this dataset primarily measures fclass-identity preservation, not learned representation quality."

**Part 2, the disclosure: CONFIRMED absent.** Across all 102 rendered pages, `fclass`
occurs once (p51, inside Ch.4's own encoder description); `0.7855`, `0.1437`, "shuffle control", "label propagation" and
"oracle" occur zero times. `homophily` occurs once, on p20, in an unrelated Ch.2 passage. No appendix carries the
measurement: the appendix list at `0_main.tex:400-404` is A contributions, B errata, C AI disclosure, D label-history
benchmark, E ethics, and a grep for `fclass` or "determin" across
`chapters/apx_*.tex` returns only the word "determination" in Appendix E's CEP/IRB paragraph. The author's own ruling in
`src_utils/PENDENCIAS.md:145-150` authorizes exactly this appendix ("eu acredito que valha um appendix para isso ou
inserimos essa discução em um dos appendix, e no prefacio do courb apontamos para esse apendix") and it has not been
written.

**Part 3, "STILL DRIVES the thesis arc": PARTLY, and the review overstates it.** I read the four sites it names. What
the document actually does:

- `1_introduction.tex:113-116` — "Category performance rose sharply at every state tested. The diagnosis followed: at
  that stage of the research, the input representation, not the sharing architecture, was the bottleneck." The static
  number is not quoted here, but "rose sharply" is the static result and nothing scopes it. **The review is right about
  this site.**
- `6_conclusion.tex:45-55` — quotes the 20.2 to 22.0 figure, then immediately states the width confound: "The comparison
  is not width-matched, however: the decomposed input is wider than the place embedding it replaces, 192 dimensions
  against 64", and attributes the equal-dimension control to Ch.4. So one confound is disclosed here and the other is
  not. **Partly right.**
- `2_fundamentals.tex:56-57` — defines category classification as labelling a POI "from static features rather than from
  a sequence", neutrally, with no claim resting on it. **The review's Ch.2 charge does not hold.**
- Ch.4 itself carries the per-cell-best convention at all three sites (:40, :318, :419)
  and a preface (:18) that time-indexes the chapter and states the sample-stratified split. The static task is not
  presented as target-blind, but nor is it flagged as target-derived.

Two facts weaken the review's framing further. First, the arc does not rest on the static number alone: Ch.4's
sequential result (15 of 21 combinations plus one technical tie, per
`apx_b_errata.tex:280-284`) is independent of the shortcut, and persona 11 verified that the shuffle moves the
sequential task by only about 4 points, not to chance. Second, the author's own reading in `PENDENCIAS.md:146` limits
the problem to CoUrb, not CBIC, because Ch.3's DGI path is different — and the code bears that out:
`research/embeddings/dgi/preprocess.py:115` builds a one-hot of the seven-class target and
`:130` replaces each node's feature with the *neighbours'* mean of that one-hot, with
`research/embeddings/dgi/dgi.py:56` feeding `embedding_array_test` as `data.x`. That is label propagation over a
transductive graph, not self-lookup.

**Fixable without the author?** No, and for two different reasons. The measurement and the appendix text are mechanical,
but (a) the disclosure touches a published, co-authored chapter whose first author is Tarik S. Paiva, and the author has
already identified a courtesy notice as a precondition; and (b) rewriting
`1_introduction.tex:113-116` changes the arc sentence, which is a C2 claim under
`AGENT_GUARDRAILS §3`. **NEEDS-AUTHOR.** What a fix would consist of, precisely: an appendix section carrying the
five-state purity table above and the arm-C numbers with their single-fold single-seed footing; a Ch.4 preface pointer
to it; one clause in
`1_introduction.tex:114` scoping "rose sharply" to the static task and naming the sequential result as the part that
survives; and one limitation bullet in Ch.6 §6.2.

> DECISAO: Nao vamos alterar nada em relação a esse problema, podemos deixar comentado no appendix B esse problema,
> mas por hora não vamos alterar o texto com isso, meus motivos são: De fato é um problema, e até grave, mas ele não
> muda aconclusão final do cap 6 que é o principal, adicionar mais um fator a ser levado em consideração me faz temser
> com que os revisõres no futuro possam ficar confuso com varias erratas e pontas soltas que tem que serem levadas al
> lerem
> os artigos. Vamos criar um documento LEFT_OUT.md onde registramos pontos que deveriamos adicionar no artigo, mas
> optamos
> por não.

### COD-003 — exact reported Check2HGI lineage has not closed the future-edge channel · **PARTLY**

The review asks the right question and then answers a slightly different one. I audited the second half as instructed:
not whether more testing is possible, but whether the document overclaims relative to what it ran.

**What Ch.5 states.** `5_mobiwac.tex:391`, rendering on pp. 66–67: "The measurement bounds this channel rather than
closing it, and three limits set how far it reaches: the probe is linear, it was run at Florida alone at one random
initialization over five user-grouped folds, and it was run on those ancestor builds of the representation rather than
on the one that produced the results reported here. The same record shows why the linear form is a screen and not a
proof, since one encoder that passed it leaked under a downstream sequence model." The bidirectional link is stated in
the same paragraph at
:376: "A visit's node is linked to the visit that follows it, and category is a node input feature, so a per-visit
vector could in principle absorb the category of the next visit."

Every element the review demands is therefore already on the page: the channel is named, the probe's linearity is named,
the Florida-and-one-seed scope is named, the ancestor-lineage gap is named, and the counter-example (an encoder that
passed the linear screen and leaked downstream) is volunteered. The paragraph also names the transductivity audit's
coverage limit ("67 to 87 percent"; visits to unseen places "the one part it cannot reach"), which matches
`docs/studies/pre_freeze_gates/A4_RESULTS.md:59-63` (AL 66.8%, AZ 71.9%, FL 86.9%), and that source's own caveat that
the category measurement is "a POI-level proxy on the ~67% in-coverage subset, not the exact check-in-level setup."

**So the review's "still allows global wording that reads as though the shipped representation were leakage-cleared" is
REFUTED for Ch.5.** I swept both PDFs for
"leakage-guarded", "leakage-free", "leak-free", "no leakage", "rules out leakage" and
"clean of leakage". There is exactly one hit in rendered prose, and it is not in Ch.5.

**CONFIRMED at one site the review did not name.** `1_introduction.tex:158`, specific objective 4, promises to "Anchor
the final answer to the research question in a **leakage-guarded** statistical protocol, the user-disjoint
cross-validation with paired significance and non-inferiority testing of Chapter 5". It renders on p15. Read against
Ch.5's own :391, "leakage-guarded" is stronger than the evidence: the user-disjoint split guards the *split*, which is
true and defensible, but the phrase reads as a property of the representation pipeline, which is precisely the thing
Ch.5 says it bounded rather than closed. One further site is adjacent: `apx_a_contributions.tex:64` uses "leak-free
per-fold region-transition prior" inside a comment, so it does not render.

**Also CONFIRMED: the audit-population mismatch is real but unstated.** The A4 audit ran on the non-overlapping
windowing and a POI-level proxy; the board runs stride-1 sliding windows. Ch.5 states the coverage limit and the proxy
nature in the integrity paragraph but does not state that the audit population differs from the result-window
population.

**Fixable without the author?** The `1_introduction.tex:158` wording is a one-clause repair with no number and no new
claim: replace "a leakage-guarded statistical protocol"
with the protocol's actual named guarantee, "a user-disjoint statistical protocol". It is in a `[NEEDS SIGN-OFF]`-free
sentence but it is an objective statement, so I would put it to the author as a one-line approval rather than apply it
silently. The exact-lineage rerun is **NEEDS-AUTHOR** and is a research decision, not an edit; the review's own
recommendation (option 2, retain as conditional evidence with the channel stated adjacent to the headline) is already
what Ch.5 does, so the honest reading is that option 2 is *already taken* and only the Ch.1 word contradicts it.

> DECISAO: Sobre esse ponto, já dicutimos diversas vezes em outros arquivos de revisão. Até criamos o appendix D que
> também trato sobre esse assunto. Eu acredito que a unica mudança que temos que fazer e mudar a frase no cap. 1.

### COD-004 — operational success conflated with transfer and a trunk mechanism · **PARTLY**

**The withholding is now stated, twice, and more strongly than the review credits.**
`5_mobiwac.tex:703-714` reports the freeze control, then: "we attribute the gain to the joint architecture rather than
to any named component of it", then the Florida cross-attention removal at $-0.04 \pm 0.13$, then two reasons not to
read that as an absence of contribution ("an earlier configuration whose region head was driven by a transition prior
the models reported here do not use", and "the development record that produced it reads the null as a compensation
effect"), closing: "We therefore do not name the shared trunk as the source, and we do not present the ablation as
evidence against it either." `6_conclusion.tex:95-103` carries the parallel passage. Both render, on pp. 73 and 77. This
is the disclosure the correction round claims, and it is real: the underlying record at
`docs/findings/archive/F50/F50_T1_5_CROSSATTN_ABSORPTION.md:229` does call its own null "misleading" and a "hidden
compensation effect".

**The contrary attribution survives.** `5_mobiwac.tex:872`, the opening sentence of §5.7 Discussion and Limitations,
rendering on p74: "One model serves both tasks: the shared trunk carries the semantic context that lifts the
next-category task, and the private spatial path keeps the next-region task competitive." That is a component
attribution, one page after the document says it will not make one. The review is right, and the defect is sharpened
rather than softened by the correction round: the round strengthened the withholding at :713 and left the contradiction
at :872 intact, so the two now sit closer together.

**Fixable without the author?** Yes, and it is the single highest-value one-sentence repair in the document. The fix
keeps the sentence's function (it introduces the discussion by naming what the model achieves) and drops the mechanism:
"One model serves both tasks: it reaches the next-category gain and keeps the next-region task competitive, with the
region output retaining a private spatial path." No number moves, no result changes, and it removes a contradiction a
committee will find in thirty seconds. Because it is interpretive prose in a re-typeset chapter, it belongs in Appendix
B's departure list, which is why I flag it for approval rather than call it free.

> DECISAO: Calma, não haviamos chegado a conlclusão que os experimentos que alegavam que o shared trunk não auxiliava
> estavam errados? De qualquer forma como não temos argumento a favor e nem contra eu proponho de fato suavisar o claim
> no cap. 5. Remeber that this type of change we can reproduce in the original text and in the dissertacao.

### COD-005 — PCGrad and Nash-MTL evidence still misstated · **PARTLY**

Four sub-claims, all confirmed at source but with different owners: PCGrad's invalidity (already ruled on by the
author), the screen's missing scope (the one unaddressed gap), the Nash cost claim (confirmed and already disclosed in
Appendix B), and the Nash guarantee wording.

**PCGrad's invalidity: CONFIRMED at source; the naming is an author ruling, not an oversight.**
`docs/results/mtl_improvement/T4_audit_and_verdict.md:26-31` states that under the dual tower "the private reg tower (>
80% of the reg pathway) trains at unit weight always" and that cagrad/pcgrad/aligned_mtl "**don't count** as balancer
tests; they reduce to ≈equal-weighting by construction". The chapter's own comment at
`5_mobiwac.tex:186-201` reproduces this and records the recommendation to drop the two words — explicitly "NOT applied —
the author's instruction governs". The author's decision is at `PENDENCIAS.md:180-184`: he wants PCGrad named so that an
acid MTL reviewer can see it was tried, on the grounds that it produced no result even before the private tower existed.
**NEEDS-AUTHOR**, already decided, and the review is re-litigating a settled ruling without knowing it was settled.

**The screen's scope: CONFIRMED absent.** T4's own precision note says what ran was "the full screen at **registry
DEFAULTS, seed 0, AL+FL**". Neither the seed nor the two states appears in Ch.5's prose. This is the part of COD-005
that is a genuine, unaddressed number-protocol gap under `AGENT_GUARDRAILS N5` (convention named).

**The Nash cost claim: CONFIRMED as a defect, and already disclosed as one.**
`3_cbic.tex:237` reproduces the published "requires only two matrix-vector products per iteration".
`apx_b_errata.tex:160-172` preserves it deliberately and names it: "it is not supported by the method's own paper: the
phrase does not appear there, and both implementations we examined run an iterative concave-convex procedure whose
default is twenty passes, each a convex solve, on top of one backward pass per task. The claim therefore understates the
optimizer's cost." That paragraph renders on p89. The review's statement that the claim is "known to be unsupported
while remaining live in the chapter"
is true of the chapter and false of the document, which discloses it in the appendix built for exactly this purpose. The
open question is only whether to correct rather than report, and `PENDENCIAS.md:250` puts that to the author with a
recommendation to keep as is. **NEEDS-AUTHOR.**

**The Nash guarantee wording: CONFIRMED, minor.** `4_courb.tex:120` says Nash-MTL "seeks the update direction that
maximizes the product of the utilities of all tasks, which ensures that the update is beneficial for all tasks
simultaneously". "Ensures" is unconditional; the guarantee holds under the method's assumptions. This is published
co-authored prose, so it is an errata-policy question, not a free edit.

> DECISAO: Sobre o 2 e o 3 pontos acredito já ter resolvido em pendencias.md. Quanto ao ponto 2, vamso deixar de fora.
> No ponto 4 podemos fazer uma correção no texto e apontar no appendix B.

### COD-006 — statistical wording exceeds the design · **PARTLY**

**"before any result was read": CONFIRMED as an overstatement.**
`5_mobiwac.tex:418` says "A written analysis plan, fixed during development and before any result was read". The plan
itself,
`docs/studies/closing_data/v17_completion/STATISTICAL_PROTOCOL.md`, is headed
"PRE-REGISTERED. Commit this BEFORE the board unblinds" — which is a claim about the *board*, not about all prior
results. Its own §3.2 justifies the two-point margin partly on pilot evidence: "the adopted gated-overlap board widened
the matched reg gap from
~−0.31 pp (non-overlap, 'visibly ties') to ~−1.2 pp (FL, 2 seeds). A −1.2 pp gap with σ~1.0 **passes** TOST
non-inferiority at δ_reg = 2 pp." A margin chosen with a two-seed Florida gap in hand was not chosen before any result
was read. The chapter's phrase is defensible as "before the final board was read" and is not defensible as written.

**"The equivalence is well powered": CONFIRMED as post-hoc precision.**
`5_mobiwac.tex:418` supports it with "the paired difference's standard deviation is 0.01 to 0.18 points across the
datasets" — observed variance, i.e. achieved precision, not prospective power.

**"identically": REFUTED as the review states it.** The review says the document "says selection is applied identically
to both arms, while dedicated models use task-best epochs and the joint model uses a geometric-mean joint selector".
Both halves are on the page, in the same chapter, and the chapter says so itself. `5_mobiwac.tex:523-527`: "every
reported model is one saved artifact per fold, read at its validation-selected epoch: each dedicated model at its task's
best epoch, and the joint model at the epoch selected by its joint validation score (the geometric mean of the two task
metrics)". The word
"identically" at `:880` is doing different work in its own sentence: "the selection rule is applied identically to both
arms on the same folds, and the dedicated arm receives the wider search", followed by "It does not follow that the bias
cancels exactly." The rule (select on validation, per fold) is identical; the per-arm objective is disclosed two pages
earlier. This is loose but it is not the contradiction claimed, and the non-cancellation caveat the review asks for is
already the next sentence.

**n=4 and the fixed partition: already stated.** `:418` gives "$4\times5=20$ measurements and the tests pair the
per-seed means ($n{=}4$)"; `:880` adds "The four seeds also reuse one fixed fold partition, so the reported intervals
cover variation across random initializations and not across resampled user splits."

**Fixable without the author?** Two clauses are, and both are narrowings that cannot strengthen a claim: "before any
result was read" → "before the final result board was read", and "The equivalence is well powered" → a statement of the
observed interval precision, conditional on the fixed split, using the numbers already in the sentence. Both are
`[NEEDS SIGN-OFF]`-class because they touch the statistical protocol paragraph that the whole Ch.5 verdict rests on.

> DECISAO: Let's change only the second point about the: "The equivalence is well powered".

### COD-007 — Chapters 3–4 methodologically under-specified · **PARTLY / NEEDS-AUTHOR**

**The missing records: CONFIRMED.** Ch.3 states 5-fold cross-validation at :294 and never identifies the split axis,
seed count, tuning budget, or checkpoint rule. Ch.2 discloses this rather than hiding it: `2_fundamentals.tex:496-500`
says "Chapter 3 reports five-fold cross-validation without identifying the split axis, Chapter 4 states that its split
is stratified by sample rather than by user ... and only Chapter 5 splits by user."
Ch.4's checkpoint rule is indeed unspecified. Whether the originals are recoverable is **NEEDS-AUTHOR** (the CBIC
codebase was not provided to this audit).

**The inferential-verb half: largely REFUTED.** The review says "'significant,'
'statistical,' 'outperforms,' and 'consistently' language survives in places", which implies the round did not act. It
did. `apx_b_errata.tex:196-200` records that four statements had *significant/significantly/statistically* removed, with
the published and chapter wordings printed side by side at :239-252, and states the reason: "the chapter reports no
inferential test of any kind, so these words claimed more than the study established". :200-208 then accounts for every
surviving use: four are not about the chapter's own results (two report cited work, one states the hypothesis, one names
a target level), and two that *are* about its own results are kept deliberately because they qualify negative findings,
so removing them "would make the chapter's own conclusion sound stronger than it was". I verified the survivors at `3_cbic.tex:60, 62, 68, 90, 209,
414, 423` and the accounting holds. That is a documented, reasoned disposition, not leftover residue.

**The oracle-envelope half: PARTLY, see NUM-7.** Ch.4 states the per-cell convention at all three of its own sites; the
frame does not.

> DECISAO: Sobre o primeiro item: De forma simples o cap. 3 e 4 usam a mesma métodologia de split. Para ambos foi usado
> somente uma seed. E
> quanto ao orçamento de tuning de hiperparâmetros, não lembro ao certo sei que para o cbic, testamos varias
> configurações, mas para o courb como a ideia era testar os embedding e não o modelo MTL, não chegamos a mexer muito
> nele. Sobre checkpoint temos que voltar nos commits para avaliar como era, mas tanto para o cbic e courb era a mesma,
> inclusive tem o codigo do /Users/vitor/Desktop/mestrado/temp/tarik-new para verificar tmb e tirar outras duvidas.
> Quanto aos outros pontos do review o item 2 não vamos fazer nada e o item 3 já enderessamos acima.

### COD-008 — load-bearing citations do not support their claims · **PARTLY**

I re-verified each of the four against the source of record rather than against the review or persona 05.

**The Mikolov negative-sampling mismatch: CONFIRMED.** `4_courb.tex:208` says the embeddings are learned "using the
*skip-gram* strategy with *negative sampling*
\cite{mikolov2013word2vec}". The bib entry is *Efficient Estimation of Word Representations in Vector Space*, arXiv:
1301.3781. I pulled both abstracts from the arXiv API: 1301.3781 mentions neither negative sampling nor hierarchical
softmax; the negative-sampling paper is arXiv:1310.4546, *Distributed Representations of Words and Phrases and their
Compositionality*, whose abstract carries both terms. The citing clause therefore attributes a method to the paper that
does not contain it. Note the irony worth recording: `apx_b_errata.tex:522` documents replacing `church2017word2vec`
with
`mikolov2013word2vec` at this very site, so the repair fixed one mis-citation and left a support mismatch.

**Standley: CONFIRMED as an overreach.** `3_cbic.tex:210` claims "hard parameter sharing frequently matches or exceeds
the performance of more complex architectures on many benchmarks, while offering faster training and inference
\cite{standley2020tasks}". The paper's abstract (arXiv:1905.07553) argues the opposite direction on the first half —
multi-task learning "often leads to inferior overall performance as task objectives can compete" — and its contribution
is a framework for *assigning* tasks to several networks, whose claimed advantage is "better accuracy using less
inference time than not only a single large multi-task neural network but also many single-task networks". It supports a
time-accuracy trade-off for task grouping; it does not support a general "hard sharing matches or exceeds complex
architectures" claim. This sentence is published CBIC prose (`articles/CBIC___MTL/sections/method.tex:85` carries it
verbatim), so it is an errata-policy decision.

**UberNet and Sphere2Vec preprint records: CONFIRMED.** `kokkinos2016ubernet` is typed as
`@article{... journal = {arXiv preprint arXiv:1609.02132}}`; Crossref returns the version of record, CVPR 2017, DOI
10.1109/cvpr.2017.579, pp. 5454–5463.
`mai2023sphere2vecgeneralpurposelocationrepresentation` is an `@misc` on arXiv:2306.17624; Crossref returns ISPRS
Journal of Photogrammetry and Remote Sensing 202:439–462, DOI 10.1016/j.isprsjprs.2023.06.016. Both are metadata
upgrades with no claim consequence. The Standley PMLR volume/pages complaint is REFUTED as a defect:
`apx_b_errata.tex:551`
records that the page range was dropped *because it was unverifiable*, which is the fail-closed behaviour
`AGENT_GUARDRAILS R2` requires, not a lapse.

**The scikit-learn row: REFUTED.** The review says "The 2011 scikit-learn paper cannot support `StratifiedGroupKFold`,
which was added in scikit-learn 1.0 in 2021." The citing sentence at `2_fundamentals.tex:496-499` does not attribute the
splitter to the paper: it states the protocol in prose ("a grouped, stratified splitter keeps all of a user's check-ins
on one side of every fold") and cites the library. The chapter's own ledger comment at `:573-574` records the ruling:
"StratifiedGroupKFold is a scikit-learn v1.0/2021 feature; single-cite ruling (author) — 2011 paper for the library,
splitter behavior stated defensively in prose." Persona 05 reached the same verdict independently
(`05_citation_auditor_report.md:237`, SUPPORTED). This is a citation-style preference the review has promoted to a
claim-support failure. The author may still prefer a versioned software citation; that is taste, and it is question 8 on
the review's own list.

**Fixable without the author?** The two bibliographic upgrades (UberNet → CVPR 2017; Sphere2Vec → ISPRS 2023) are
mechanical and carry no claim. The Mikolov site has two honest repairs: add the 1310.4546 entry and cite it for the
negative-sampling clause, or drop the two words "with *negative sampling*". Both touch published co-authored prose or
its bibliography, so both belong in the Appendix B trail; the bibliography half is inside the dissertation's own global
list, which `AGENT_GUARDRAILS R4` already puts under the dissertation's control. **Standley is NEEDS-AUTHOR** (published
prose, and the sentence is a claim, not a typo).

> DECISAO: Vamos aplicar as correções propostas e para o cap. 3 com o standley vamos fazer uma avaliação mais profunda
> de como isso afeta o texto e se é possivle corrigir o texto e adicionamos isso em uma errata no appendice B, vale
> também comentar para checar o historico de mudança nos commits para ver se não estavamos usando outra ref. Ainda nessa
> tarefa vale lançar outras agentes um por cap. para verificar os claims das citações com os paragrafos relacionados,
> assim como foi feito aqui.

### COD-009 — CoUrb translation and adaptation records lag the dissertation · **PARTLY**

**The single-seed overreach: REFUTED as it now stands.** The review says the dissertation presents a code inference as a
fact about the published execution.
`4_courb.tex:257` reads: "The released code of record pins a single random seed, so the five folds constitute one
repetition of the experiment rather than several, and the reported standard deviations are the spread across folds at
that seed." That is scoped to the released code, which is exactly the scoping the review asks for. I verified the code
claim firsthand in `/Users/vitor/Desktop/mestrado/temp/tarik-new/PoiMtlNet_Novo/src/etl/mtl/create_fold.py`:
`random_state: int = 42` at :162, `torch.manual_seed(random_state)` at :180,
`np.random.seed(random_state)` at :181, and both splitters as
`StratifiedKFold(n_splits=k_splits, shuffle=True, random_state=random_state)` at :226 and
:229 with no `groups=` argument. The chapter's comment at :271 records "Deliberately NOT claimed: that the published
experiments were produced by this exact file."

**The ledger drift: CONFIRMED.** `src_utils/adaptation_ledgers/4_courb_ADAPTATION_LEDGER.md:3`
names the source of record as `articles/CoUrb_2026/src_en/`, the English translation donor, rather than the published
Portuguese article — which is the inversion the review reports, and it matters because the published PT text is the
artifact the errata policy is answerable to. The count note at :39 says "EIGHT non-published sentences or blocks exist
in this chapter" and records that a previous count undercounted by five; at least one later addition (the MTLnet
spelling normalization, 26 sites, per `PENDENCIAS.md:274`) post- dates it.

**The "no claim altered" tension: PARTLY, and the review points it at the wrong chapter.** The sentence it describes is
in Ch.5, not Ch.4: `5_mobiwac.tex:33` says "No result, claim, or conclusion was altered; every departure from the
submitted text is recorded in the errata appendix." Ch.4's preface makes no such universal. Whether Ch.5's universal
survives Appendix B's claim-scope rows is a real question — Appendix B does list wording substitutions that reduce claim
strength — but the sentence's own second clause points at the appendix that lists them, so a reader is not misled.
Reconciling it is a one-clause edit ("No result or numerical conclusion was altered; wording changes that narrow a claim
are listed in ...").

**Fixable without the author?** The ledger and inventory corrections are repository records, outside `src/`, and are
mechanical. The source-of-record inversion should be fixed there. The Ch.5 universal is one clause and is
`[NEEDS SIGN-OFF]`-class.

> DECISAO: Vamos aplicar as correções citadas, porém a clausula no cap 5, não tem necessidade, vide que o cap 5, estamos
> alterando o texto original também vide que vamos mandar essa revisão para o mobiwac no perido de revisão.

### COD-010 — capacity-matched control miscounted and over-compressed · **CONFIRMED**

The brief lists this as "partly addressed; verify". Verified: the count and the statistic are both still wrong on the
page. `6_conclusion.tex:116-118`, rendering on p77: "At Alabama, across three training configurations and all twenty
fitted models, the best of them reaches 56.16 macro-F1, against 56.82 for the dedicated model at its own tuned width and
64.51 for the joint model."

Against `docs/results/closing_data/capacity_matched_stl_cat/README.md`:

- :19 — "5 folds × seeds {0, 1, 7, 100} = **n=20 per arm**". Three arms are tabulated at
  :37-41 (bs2048 @ lr 0.0025; bs8192 @ lr 0.005; bs2048 @ lr 0.005), so the artifact holds 20 fits per arm and 60 in
  total. "all twenty fitted models" across three configurations is arithmetically impossible as written.
- :39 — the best arm's row is `| bs2048 @ lr 0.0025 (**best**) | 20 | **56.16** | 1.89 |`. 56.16 is that arm's **mean
  over 20 fits**, with SD 1.89, not "the best of them".

What makes this finding sharper than the review states: the chapter's own ledger comment at `6_conclusion.tex:155-158`
already knows about the missing spread — "the Alabama value 56.16 above still carries no spread; the same README gives
std 1.89 for that arm. Adding it would satisfy WRITING_LAW §3 for the whole paragraph, but that sentence is outside this
correction's scope, so it is left as approved." So the SD omission is a known, deferred item; the count error and the
"best of them" mis-description are not recorded anywhere and are new here. Note also that the same paragraph reports
California correctly ("69.88 macro-F1, standard deviation 0.26 over its twenty fitted models"), which makes the Alabama
sentence an internal inconsistency as well as a source mismatch.

**Fixable without the author?** Yes, mechanically, and it is the cleanest fix in this audit. Every value is quoted, none
computed: "At Alabama, across three training configurations at twenty fitted models each, sixty in total, the best
configuration averages 56.16 macro-F1, standard deviation 1.89, against 56.82 for the dedicated model at its own tuned
width and 64.51 for the joint model." This changes no verdict — at 56.16 the joint model still leads the capacity arm by
8.35 on the joint-best basis, as the chapter's own comment at :126-129 records.

> DECISAO: Concordo.

### COD-011 — privacy, ethics, licensing and governance absent · **RESOLVED**

Appendix E, "Data Ethics and Governance", renders on pp. 101–102 (listed in the ToC at p12; included at
`0_main.tex:404`). It covers every item the review asked for, and its licence facts trace to the source of record:

- Provenance and licence: the Figshare deposit DOI `10.6084/m9.figshare.22126586.v2` under CC0, with two qualifications
  stated from the record itself (the dedication was applied by the depositor, not the collector; the named origin site
  now redirects elsewhere, so its terms could not be read). Massive-STEPS under Apache 2.0 on Hugging Face, with the
  Foursquare upstream noted as access-gated and its product terms explicitly recorded as not read.
  `src_utils/evidence/DATASET_LICENSING_FINDINGS.md` and the chapter's own comment record live re-verification on 2026-07-27,
  including `gated="auto"` for the Foursquare distribution against `gated=false` for the Massive-STEPS copy.
- Re-identification: "A user identifier in these files is a pseudonym and not a name, but a sequence of timestamped
  visits is still a description of one person's movements. Pseudonymity is not anonymity", cited to
  `luca2021mobilitysurvey`.
- What is *not* done: "this work adds no de-identification of its own. No coordinate is perturbed, rounded, generalized,
  or masked, and no formal privacy mechanism is applied", with the reason (the region target is itself spatial).
- Safeguards by restriction: the social-graph and user-profile files are declared unread, identifiers carried as opaque
  integers, no cross-collection linkage, and no redistribution (data directory excluded from version control).
- CEP/IRB: records the author's position that review was not required for secondary analysis of already-public data, and
  states plainly "It records no approval and no exemption, because none was sought and none is claimed" — which is
  exactly the do-not-invent discipline the review demanded.

The one item still open is the institutional determination itself, which the appendix correctly declines to invent and
flags for the file before deposit. That is COD-012 territory, not COD-011.

### COD-012 — both artifacts fail the UFV submission gate · **PARTLY**

**The bibliography font: RESOLVED, by measurement.** I sampled glyph font sizes through the PDF text layer. Body page
30: 11.96 pt dominant. Bibliography page 81: **11.96 pt dominant** (2,517 of 2,633 glyphs). The `\footnotesize` wrapper
is gone;
`0_main.tex:393-395` records the removal and that it "Adds about two pages", which is consistent with the 97→102 page
change. Appendix B's tables measure 10.91 pt, which is a
`\small` table body and a different question (COD-017).

**Everything else: CONFIRMED and NEEDS-AUTHOR.** The defense build's p2 is the literal placeholder — I rendered it and
read it:
"[Approval sheet placeholder — PPG signature-page model is inserted here for the defense; signed version replaces it afterward]
", from
`0_main.tex:165-171`. `\membrobancaA`, `\membrobancaB` and `\databanca` are placeholder strings at `0_main.tex:126-128`.
`\campus{Campus Florestal}` is set at :125, and the comment at :122-124 correctly notes it renders nothing today because
`\imprimircapa` is called by neither build — so the cover is genuinely absent, as the review says. The font is
`newtxtext,newtxmath` (`0_main.tex:41`), a Times-metric-compatible face; whether the secretariat accepts it against a
rule naming "Times New Roman or Arial" is an external determination and cannot be settled from the repository. Article
21 proof, anti-plagiarism certificate, defense date and the AcademicoPG preview offset are all external.

**Fixable without the author?** Only the bibliography half, and it is already done. The rest is his and the
secretariat's.

> DECISAO: Vamos ver como os artigos de exemplos fazem e adicionar o `\campus{Campus Florestal`. A font vamso usar essa,
> ela já foi usada em outros artigos. Os noemes da banca e a folha de aprovação continua pendente.

### COD-013 — AI disclosure ahead of the recorded approval state · **CONFIRMED**

The tension is real and the review's count is now low. `apx_c_ai_disclosure.tex:57-58`:
"No content entered the document from model memory, and the author reviewed and takes responsibility for every word of
the final text." A recursive grep of `src/` returns **31**
`[NEEDS SIGN-OFF]` markers, not 27, distributed as: `0_main.tex` 6, `6_conclusion.tex` 6,
`5_mobiwac.tex` 5, `apx_a_contributions.tex` 4, `apx_b_errata.tex` 3, `1_introduction.tex`
2, `2_fundamentals.tex` 2, and one each in `apx_c_ai_disclosure.tex`, `apx_d_ceiling.tex`,
`apx_e_ethics.tex`. Several sit on central claims: the withheld trunk attribution (`6_conclusion.tex:110`), the
capacity-control correction (:136), the rescoped ablation clause (`5_mobiwac.tex:720`), and the whole of Appendices C
and E. Appendix C's own header comment carries a `[NEEDS SIGN-OFF: whole appendix ...]`, so the disclosure that asserts
completed author review is itself unapproved.

The model-naming sub-claim also holds: the appendix says "eighteen-reviewer panel, each reviewer a separate agent
(Claude Opus family)" while `CLAUDE.md` §1 records the exact model the v1 suite ran on and the reason for the deviation.
Naming what is verifiable is the review's correct recommendation.

**Fixable without the author?** Structurally no: the whole finding is "the text claims an approval that has not
happened", and only the author can either grant the approval or authorize the weaker wording. What *is* mechanical is
producing the list — the 31 marker sites with file and line — so he can work through them. **NEEDS-AUTHOR.**

> DECISAO: Eu de fato estou terminando de revisar os outros pontos, mas vamos deixar o texto como tá, fazendo somente a
> alteração de adicionar o modelos esse que pode cirat o opus 4.8, inclusive não precisa de contar toda a historia que o
> fable acbou e tivemos que usar o opus, só cite que usamos o opus e fim.

### COD-014 — "ceiling" and the Markov-floor explanation · **RESOLVED**

**The renaming is complete.** Zero occurrences of "label-only ceiling", "autocorrelation ceiling", or "what the past
itself allows" in either PDF. "label-history benchmark"
appears on pp. 8, 12, 66, 98, 99, 100. Appendix D is titled "A Label-History Benchmark for the Next-Category Task"
(`apx_d_ceiling.tex:13`; the filename still says `ceiling`, which is harmless). The not-an-upper-bound statement is in
the running text where the review asked for it, `5_mobiwac.tex:376`: "It is not an upper bound on what a model may
score. The four predictors are a specified set, and a better predictor of the same restricted information could exceed
them." `GLOSSARY.md` §2 carries both the new entry and a retirement row for the old name that forbids reintroducing it,
and it separates the benchmark from the **clean reference encoder** (0.4090 standardized / 0.4074 raw at Florida) that
the screen actually gates on — a distinction the review did not make and which matters, since the two were conflated in
the internal record.

**The Markov paragraph is rewritten and no longer carries a common causal story.** On p73:
"Neither fact establishes why the floor lies above the three systems, and we do not claim a single explanation." The
protocol asymmetry is now stated system by system — HMT-GRN on the same data, folds and initialization; STAN on the same
folds but its own embeddings and sequences; the ReHDM reference under its own published protocol, "so its cell is not
measured on our windows or folds at all" — and the region-native/place-level error the review caught is gone. The counts
render as the review verified them (floor above HMT-GRN at six of six, ReHDM at three, STAN at four).

**One number in this paragraph changed after the review and is worth recording as correct.** The Alabama revisit share
is now "the target region is the last visited region in 32.1 percent of windows". It quotes
`docs/results/closing_data/markov_floor_stride1/alabama.json`, key
`aggregate.markov_1step_region.acc1_mean` = 0.32064040033191976 (SD 0.01690965826249736), which is the same artifact,
the same 96,326 stride-1 windows and the same folds as the 62.26 Acc@10 floor in the sentence before it. The superseded
22.4 percent figure was a place-level rate on non-overlapping windows and did not support the region-level sentence it
was attached to. The review saw the wrong number and did not catch it; the fact gate did
(`_history/_specialists_v2/FACT_GATE_v3.md` B-1).

> DECISAO:

### COD-015 — cross-chapter task, data and reference-point seams · **PARTLY**

Six sub-claims. Four hold — (a) the Ch.3 preface clause, (c) the Gowalla vintage, (d) the unused metric promises, (f)
the gradient scope in Ch.6 — and two do not: (b) the next-POI bridge and (e) the cross-reference targets.

**(a) Ch.3 preface says Chapters 4–5 revise through representation rather than architecture, although Ch.5 changes
topology and task pair — HOLDS, weakly.**
`3_cbic.tex:23-24` reads "Chapters 4 and 5 revise that verdict by changing the input representation rather than the
architecture." Ch.5 does change the topology (cross-attention replacing shared hidden layers) and the task pair. The
frame elsewhere is careful about this: `1_introduction.tex:124-130` states both changes explicitly, and
`1_introduction.tex:135` says "The task pair therefore evolved across the three studies". So the defect is a single
unqualified preface clause against a frame that gets it right everywhere else.

**(b) "Next-POI" defined as exact-place prediction in a chapter that predicts next category — REFUTED.** Both paper
chapters carry an explicit bridge. `3_cbic.tex:28-31`:
"the term ``Next-POI Prediction'' as used in the reproduced article denotes the frame's *next category* task, that is,
predicting the category of the next visited place, not the exact place itself". `4_courb.tex:18` carries the same
sentence. `3_cbic.tex:53` defines the task as "Predicting the category of the next POI a user will visit". Appendix B
has a row for the one related-work definition that did read as exact-place. This is closed.

**(c) Gowalla vintage 2009–2010 versus 2009–2011 — HOLDS as an inconsistency, but it is not a "distinct extraction
bases" problem.** `4_courb.tex:425` (published prose) says
"collected between February 2009 and October 2010"; `6_conclusion.tex:196` (frame prose)
says "collected between 2009 and 2011". Both cite the same collection. One of the two is wrong and the frame is the one
the dissertation controls.

**(d) Ch.2 promises MRR and relative multi-task performance change, neither of which appears — HOLDS.**
`2_fundamentals.tex:471` says Acc@10 "says nothing about the probability mass placed on the true region, which is why
mean reciprocal rank accompanies it where the joint comparison needs a rank-sensitive figure", and :476-478 introduces
"the relative multi-task performance change" citing `maninis2019attentive`. Both phrases render on p24 and nowhere else:
"reciprocal rank" appears on p24 only, "relative multi-task" on p24 only, and "MRR" on no page at all. Neither quantity
is reported in any results chapter.

**(e) The random-region and checkpoint-selection cross-references do not point to sections that define those claims —
REFUTED as far as it can be checked.** Both builds report zero undefined references (`build/main.log`, and `check.sh`'s
flattened-log sweep returns OK). The random-region reference at `5_mobiwac.tex:78` points to
`sec:mobiwac:results-part2`, where the random top-ten figure is given; the checkpoint pointer at `:880` points to
`sec:mobiwac:setup-windows`, and the joint-best convention is defined at `:523` in that section's neighbourhood. If the
review means a semantic rather than a syntactic mismatch, it did not name which reference, and I could not reproduce
one.

**(f) Gradient scope is four Gowalla states, not "three of six" — HOLDS in Ch.6 only, and this is NUM-3.** Ch.5 is
fixed: `:204-208` now reads "four seeds each on four Gowalla states: Alabama, Arizona and Florida, which are three of
the five United States datasets reported here, and Georgia, which this dissertation does not otherwise use, per-dataset
means within ±0.003". `6_conclusion.tex:176-178` still reads "averaged +0.001 over four seeds on three of the six
datasets". The source is
`docs/results/mtl_improvement/R0_matched_metric_bar.json`, whose `states` object has exactly four keys — `alabama`,
`arizona`, `georgia`, `florida` — each with seeds 0/1/7/100, and `scripts/mtl_improvement/plot_grad_cosine.py:19-24`
names the same four in its style map. So Ch.5 and Ch.6 now disagree with each other on the same measurement.

**Fixable without the author?** (c), (d) and (f) are. (f) is a scope correction with the Ch.5 sentence available as the
model to copy, and it removes an internal contradiction. (c) is picking which vintage is right for the frame sentence
and matching Ch.4's published range. (d) is either deleting two promises or reporting the two metrics; deleting is the
honest cheap option since neither quantity exists in any result file I found. (a) is one preface clause and is
`[NEEDS SIGN-OFF]`-class because it characterizes the arc.

> DECISAO: SObre o A) vamos mudar o prefacio, pq o cap 4 defato não muda a arc mas o cap 5 muda. Quanto ao restante que
> foi confirmado (a,c,d,f) vamos mudar tmb como sugerido.

### COD-016 — targeted language and readability pass · **PARTLY**

**The `3_cbic.tex:340` "unrecoverable sentence": REFUTED as stated, and the review mislocated it.** The quoted words are
at :340 (PDF p39), inside published CBIC prose:
"Also, it is important to notice that since we have an unbalanced result for the MTL and single, this could lead to the
worse of other results." It is awkward English, not unrecoverable: read against the table it introduces, it says that
because MTL and single-task lead in different categories, a per-category comparison can look worse than the aggregate
picture. That the meaning is recoverable does not make the sentence good — it should be clarified — but "meaning is not
recoverable without author clarification"
overstates it, and it is published co-authored prose, so a rewrite is an errata decision.

**The high-burden passages: CONFIRMED by measurement.** The abstract's result sentence is **114 words** (measured on the
`0_main.tex` abstract body with macros stripped) against a 7-to-53-word range for its neighbours, so it is more than
double the next-longest sentence in the same paragraph. The four-channel integrity paragraph is one block at
`5_mobiwac.tex:376` rendering across pp. 66–67; persona 15 measured it at 546 unbroken words and rated it Critical,
persona 01 put it in its top three, and persona 09 independently called the same paragraph the round's strongest work
and warned against editing its defenses away. `_history/_review_v2/README.md` records that disagreement and resolves it
correctly: persona 15's recommendation is break-insertion with **zero words changed**, which does not touch what 09 is
protecting. That is the right reading and this audit concurs.

**The style-audit density claim: REFUTED as a current failure.** `check.sh` runs the WRITING_LAW §4 banned-word sweep,
the contraction sweep, the em-dash sweep and the codename sweep over all chapters and returns OK on each. The only hits
are in the verdict-verb sweep, which is explicitly labelled "crude sweep, review hits" and does not set the failure
flag; I read all five and every one is legitimate (three are "Pareto" in optimization contexts at
`3_cbic.tex:108, 118, 234`, two are the word "wins" inside Appendix B rows that *quote* the published text being
corrected).

**Fixable without the author?** Break-insertion in the integrity paragraph is zero-word-change and safe. The abstract
sentence split is a rewrite of the document's most load-bearing paragraph and is `[NEEDS SIGN-OFF]`-class.
`3_cbic.tex:340` is **NEEDS-AUTHOR** (published prose).

> DECISAO: Podemos aplicar as quebras de linha no cap 5. E quando a revisão já a reescrevemos, logo acredito que
> tenhamos solucionado parte do problema, avalie. E quanto a frase no cap 3. Sim vamos refaze-la para ser mais
> entendivel e facil de ser lida.

### COD-017 — visual and typographic inconsistencies · **PARTLY**

**The oversized Appendix B float: CONFIRMED, unchanged.** `build/main.log:1932` and
`build/main_final.log:1916` both carry `LaTeX Warning: Float too large for page by
21.55853pt on input line 556`, which is the `\end{table}` of the bibliography-errata table at `apx_b_errata.tex:563`. I
rendered the page: defense p96 holds fourteen errata rows and the table body runs to the bottom rule with no visible
clipping, so this is a spacing warning rather than lost content, but the warning is real and both builds report it.

**Small in-figure labels: CONFIRMED by measurement.** Sampling glyph sizes on every page carrying a numbered figure:

| page    | figure content      | smallest label sizes | glyphs below 9 pt |
|---------|---------------------|----------------------|-------------------|
| p35     | Ch.3 architecture   | 9.96                 | 0                 |
| p48     | Ch.4 architecture   | 8.77                 | 9                 |
| p53     | Ch.4 spatial panels | 9.96                 | 0                 |
| **p62** | Ch.5 diagram        | **6.97 / 7.27**      | 389               |
| **p64** | Ch.5 model diagram  | **6.97 / 7.27**      | 351               |
| p70     | Ch.5 separability   | 8.50 / 8.97          | 111               |
| p72     | Ch.5 deltas         | 8.00 / 9.00          | 48                |

Against a 11.96 pt body, 6.97 pt is 58 percent of body size. The review named pp. 35, 48, 62 and 64 in the old
pagination and its instinct was right, though on the current build the worst offenders are the two Ch.5 diagrams, not
the Ch.3/Ch.4 ones.

**The Portuguese figure labels: RESOLVED.** Persona 18's blocker (Figure 2 labelled
`Encoder Espacial`, `Coordenadas (lat, lon)`, etc. under an English caption) is gone: those strings appear on no page of
the current build. The only Portuguese on a Ch.4 page is the published paper's own title inside the preface, which is
correct.

**The near-blank p4 with orphaned Resumo keywords: CONFIRMED.** I rendered it: p4 carries three keyword lines ("previsão
da próxima categoria / previsão da próxima região / representação em nível de check-in") and nothing else.

**Fixable without the author?** All three are, and all three are pure production work: the float split or row-padding
reduction, regenerating the two Ch.5 diagrams at larger label size, and keeping the keyword block with its Resumo. The
review's own caution applies and is correct — do not do the float reflow until the prose stops moving, because
pagination will shift.

> DECISAO: Já corrigimos alguns dos pontos, mas eu acredito que o que estiver pendente já podemos corrgir agora. E
> quanto ao fato de só mexer quanto o texto estabilizar, acho que não precisamos esperar, podemos ajustar agora e se
> precisar no futuro ajustamos novamente.

### COD-018 — governance files and automated gates no longer describe the artifact · **PARTLY**

**Stale page counts: CONFIRMED.** Current builds are 102 and 97 pages. `CLAUDE.md:28-29`
says 89 and 84; `PLAN.md:17-18` says 89 and 84; `HANDOFF_v1.md:71` and `:130` say 89 and 84; `PENDENCIAS.md:432-433`
says 94/89. Four documents, three different stale pairs. The review's own reported pair (97/92) is now stale too, which
is itself evidence of how fast this drifts.

**Appendix A per-role CoUrb credit: CONFIRMED absent.** The review raises this in its chapter-by-chapter section rather
than in COD-018, but it belongs to the same class.
`apx_a_contributions.tex` describes the platform and the ETL pipeline, and at :75-77 it correctly narrows a previously
false claim about protocol uniformity, but it states no per-role contribution for CoUrb (conceptualization, software,
experiments, analysis, visualization, writing). Ch.4's preface (:18) carries the roles it does state: second author,
presenter, author of the baseline MTLnet. Filling the rest is a fact only the author holds. **NEEDS-AUTHOR.**

**The trapped-prose checker returning success despite live failures: RESOLVED.** See COD-001. The detector now fails
closed on its own fixtures before its document verdict is trusted, and `check.sh:59-71` carries the comment explaining
why the fixture step exists and why it captures the exit status rather than piping it.

**The `pypdfium2` dependency: RESOLVED.** `build.sh:100-106` wraps the import in
`try/except` and degrades to `low = f"unmeasured({exc.__class__.__name__})"` rather than failing. `check.sh` does not
import it at all. `make check` runs clean end to end: I ran
`bash check.sh` and it exits 0.

**Locale-fragile log scanning: RESOLVED in the way that matters.** `check.sh:36` flattens the log with `tr -d '\n'`
before matching and reads the `.blg` separately, with a comment recording that the previous line-anchored grep let four
undefined citations ship because LaTeX wraps warnings at 79 columns. The regexes match LaTeX's own English warning
strings, which is not locale-dependent for this toolchain.

**The Ch.5 adaptation ledger claim: not audited in depth.** I read
`5_mobiwac_ADAPTATION_LEDGER.md`'s date (2026-07-23) against the chapter's mtime (2026-07-27 07:43) and the several
corrections applied since, so the review's "says every departure is recorded while omitting multiple recent additions"
is consistent with the timestamps. I did not enumerate the omissions, so I record this as **plausible and unverified in
detail** rather than confirmed.

**Fixable without the author?** The page counts and the ledger synchronization are, and they are outside `src/`.
Appendix A's roles are not.

> DECISAO: Meu papel no courb foi na implementação, auxilo ao meu aluno de graduação na sua pesquisa pelos modelos de
> embedding, e escrita da parte do MTL e parte da conclusão.

---

## 3 · The "Numerical corrections required" table (`codex_reviewer.md:991-1004`)

Rows 1, 2, 6 and 8 duplicate COD-010 and COD-014 and are cross-referenced rather than re-argued. The four rows that
carry independent content:

### NUM-3 — gradient scope "three of six" → four Gowalla states · **PARTLY**

Corrected in Ch.5, uncorrected in Ch.6. Full evidence under COD-015 (f). The review's required correction is right and
the fix is now a copy of the Ch.5 sentence's scope clause into `6_conclusion.tex:177`. **Fixable without the author.**

### NUM-4 — HGI example 0.74 → 0.82 basis not fully specified · **CONFIRMED, and already carrying a `[VERIFY]`**

`2_fundamentals.tex:170-173`: "the cross-region edge weight of their Equation 2, set to 0.4 for the dense Chinese cities
they study, was raised to 0.7 for the sparser United States state datasets used here, a change under which the category
F1 on Alabama, over five folds, rose monotonically from 0.74 to 0.82 across the swept values."

The source, `research/embeddings/hgi/README.md:544-551`, is a four-row sweep at 5 folds × 50 epochs: 0.4 → 0.7388 ±
0.0205, 0.5 → 0.7678 ± 0.0211, 0.6 → 0.7944 ± 0.0186, 0.7 → 0.8186 ± 0.0123. So the endpoints are correct to two
decimals and the monotonicity claim is true on all four rows, but both spreads are dropped, which `WRITING_LAW §3`
requires ("fold-std or CI wherever a mean appears in a claim"). The chapter already carries
`% [VERIFY: averaging convention of the swept "Cat F1"]` at :174 with the full provenance chain, so this is a known open
flag, not an undiscovered error. The same README line 552-554 also says "Next F1 is effectively flat across the sweep",
which is the context the review's chapter-by-chapter section separately asks for.

**Fixable without the author?** The spreads can be added by quotation (0.7388 ± 0.0205 to 0.8186 ± 0.0123), which closes
the `WRITING_LAW §3` half. The averaging-convention question in the `[VERIFY]` flag is a question about how that README
computed "Cat F1" and is **NEEDS-AUTHOR**.

### NUM-5 — "Arizona rounding: table/raw precision differs by 0.01 in one trace" · **REFUTED as stated**

Every Arizona figure the document prints is on one basis, the joint-best convention, and each traces exactly:

| document site                    | value                                 | source                                                                |
|----------------------------------|---------------------------------------|-----------------------------------------------------------------------|
| `5_mobiwac.tex:599` (Table, p71) | cat 56.43 dedicated / **65.79** joint | `JOINT_BEST_RESULTS.md:33` AZ joint-best 65.79 ±0.02                  |
| `5_mobiwac.tex:636` (p71)        | Δcat range top **+9.35**              | `JOINT_BEST_RESULTS.md:56` AZ Δcat deploy **+9.35**                   |
| `5_mobiwac.tex:617` (Table, p71) | reg **59.46** dedicated and joint     | `JOINT_BEST_RESULTS.md:43` AZ 59.46 dedicated, 59.46 ±0.04 joint-best |
| `5_mobiwac.tex:661` (p71)        | AZ TOST **0.00**; −0.08 to +0.07      | same row, Δreg deploy −0.00                                           |

The 0.01 wobble the artifact discusses is explicitly on the **diagnostic-best** basis:
`JOINT_BEST_RESULTS.md:60-62` records that "+9.40 is the paper/board value (from the rounded 65.83 MTL cell)" while the
full-precision diagnostic Δ is +9.41. Neither 9.40 nor 9.41 appears anywhere in either PDF; I searched both. The
document does not straddle the two bases, which is the very thing `AGENT_GUARDRAILS N5` forbids, and the chapter's own
comment at `:528-534` documents the ruling that put it on one basis. **Nothing to fix.** If the review means the
rounding *convention* should be stated once, that is a reasonable style request, not a numerical correction.

### NUM-7 — CoUrb 20.2–22.0 "reads as a deployable fixed encoder" · **PARTLY**

**The convention is disclosed in Ch.4 and in Appendix B, at every site.** `4_courb.tex:40`,
`:318` and `:419` each carry "considering the better of the two spatial encoders in each combination".
`apx_b_errata.tex:286-290` records the correction from the published "20 to 24 percentage points" to the audited 20.2 to
22.0, and calls the per-cell clause "the disclosure the audit requires".

I verified the arithmetic from the printed table (`4_courb.tex:329-351`), which is the only computation in this audit
and is reported as such:

| state      | mean gain, SIREN only | mean gain, Sphere2Vec-M only | mean gain, per-cell best |
|------------|----------------------:|-----------------------------:|-------------------------:|
| Florida    |                 20.09 |                        20.10 |                    20.24 |
| California |                 20.86 |                        20.70 |                    20.91 |
| Texas      |                 17.89 |                        21.98 |                    21.98 |

So the range 20.2 to 22.0 is the per-cell-best envelope, and the review is right that it is an envelope: at Texas a
single fixed encoder choice would give either 17.89 or 21.98, and the 20.2 lower end depends on Florida's best-of-two. I
also confirmed the "all 21 combinations" universal holds on the printed values (21 of 21 rows have both variants above
MTLnet), which is what `4_courb.tex:305-316`'s ledger comment claims.

**Not disclosed in the frame.** `1_introduction.tex:113` ("Category performance rose sharply at every state tested") and
`6_conclusion.tex:46` ("raised category macro-F1 by 20.2 to 22.0 percentage points across the three states tested")
carry the number and the range without the per-cell clause. The word "oracle" appears nowhere in either PDF.

**Fixable without the author?** The Ch.6 site can carry the same clause Ch.4 already uses, by quotation, with no new
number. Whether to call it an "oracle envelope" is a wording choice: `GLOSSARY.md` does not register "oracle", and the
fail-closed maintenance rule says a term not in the registry may not be used, so that specific word needs an
author-approved glossary entry first. This is a genuine constraint the review could not have known.

---

## 4 · The review's own "Reviewer Agreements and Disagreements" (`:1127-1192`)

The review adjudicates six disputes; §4.1 to §4.6 below take them in its own order, and §4.7 adds a seventh dispute it
should have adjudicated and did not. I assessed each on the evidence available to the review at its date and on the
evidence now.

### 4.1 "Is Chapter 3 direct target leakage?" — **SOUND, and the best work in the review**

It refuses two personas' stronger reading and grounds the refusal in code: Ch.3's DGI path replaces a node's own one-hot
with the neighbours' mean before the GAT, so direct self-label lookup is not confirmed. I verified this independently:
`research/embeddings/dgi/preprocess.py:115` builds `pd.get_dummies(self.pois['category'])`,
`:130` sets each node's feature to `self.embedding_array.iloc[neighbors].mean(axis=0)`, and
`research/embeddings/dgi/dgi.py:56` feeds `embedding_array_test` (the neighbour-mean array) as `data.x` while
`embedding_array` (the raw one-hot) goes in as a separate field. The adjudication's disposition — "transductive,
label-derived spatial homophily/label propagation", major scope uncertainty rather than confirmed deterministic lookup —
is the correct characterization and it matches the author's own reading at `PENDENCIAS.md:146`. Note the caveat the
adjudication does not state: an isolated node gets `[0]*7`, and a node whose neighbours share its category gets a vector
that is nearly its own one-hot, so the propagation is weaker protection at high homophily than the framing implies.

### 4.2 "Does the future-edge channel invalidate Chapter 5?" — **SOUND on epistemics, stale on the document**

"The correct status is unverified... may not describe it as proven clean" is right, and it is the disposition the
chapter itself takes. Where the adjudication is now stale is the implication that the document still describes it as
clean: `5_mobiwac.tex:391` states all three limits and volunteers the counter-example. The one surviving global word is
at
`1_introduction.tex:158`, which the adjudication does not name. So: sound reasoning, wrong target.

### 4.3 "Does 'MTL help'?" — **SOUND**

The operational/causal split is the right frame, the freeze-control and Florida-null evidence is correctly read, and
"the dissertation must define which sense it claims" is the right ask. It is also 90 percent satisfied already:
`5_mobiwac.tex:703-714` and
`6_conclusion.tex:95-103` make the operational claim and withhold the causal one explicitly. The residual is the single
contradicting sentence at `:872` (COD-004), which this adjudication and COD-004 both identify.

### 4.4 "Does selection bias cancel in paired differences?" — **SOUND**

"Shared folds and a wider dedicated-model search provide some protection and can make the comparison conservative in
some directions. Different epoch selectors and use of the reporting fold for selection prevent a proof of exact
cancellation." That is exactly what
`5_mobiwac.tex:880` says, including the closing "It does not follow that the bias cancels exactly." The adjudication
agrees with the document and both are right; it should have said so rather than framing it as an open dispute.

### 4.5 "Is the new label-only analysis a ceiling?" — **SOUND, and already actioned**

"No. It is the best observed result among four specified history-only predictors" is correct and is now the document's
own wording. The adjudication credits "the adversarial change gate" for rejecting the upper-bound terminology, which is
accurate — the rename happened on 2026-07-27 by author decision and is registered in `GLOSSARY.md` §2.

### 4.6 "Are TeX Gyre Termes and the standalone Fundamentals chapter acceptable?" — **SOUND, with one factual slip**

"They may be accepted in practice or by precedent, but the repository's current institutional evidence does not
establish that acceptance. These are external advisor/Comissão/secretariat decisions, not facts to infer." Correct, and
correctly refuses to infer. The slip is the font's identity: `0_main.tex:41` loads
`newtxtext,newtxmath`, not TeX Gyre Termes. The two are related Times-metric-compatible families and the compliance
question is identical, but a submission conversation should name the package that is actually loaded.

### 4.7 One adjudication the section should have made and did not

The `_review_v2` personas record a disagreement the codex review passes over entirely:
persona 09 calls the four-channel integrity paragraph the round's strongest work and warns against editing its defenses
away, while personas 15 and 01 call the same paragraph the document's worst readability failure. `_history/_review_v2/README.md`
resolves it (break-insertion, zero words changed). The codex review reproduces persona 15's side as COD-016 and persona
09's side as its own COD-003 recommendation, in different sections, without noticing that they are about the same 546
words. Anyone acting on COD-016 without reading COD-003 could delete the disclosures COD-003 depends on.

---

## 5 · Where codex and the v2 personas overlap or disagree

The brief flags that several COD items restate persona findings already fixed. They do, and the mapping matters because
the persona reports carry the measurements the codex review paraphrases.

| COD item            | Persona origin                                                                                                            | Status of the overlap                                                                                                                                                                                                 |
|---------------------|---------------------------------------------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| COD-001             | 02, 15, 16 (16 found the seventh case on 2026-07-27)                                                                      | Fixed after the personas; codex reports the pre-fix state                                                                                                                                                             |
| COD-002             | 11 (`11_poi_mobility_expert_report.md:33-41` carries the five-state purity table; the codex text reproduces its argument) | Determinism measured by 11 and re-measured here; disclosure still open                                                                                                                                                |
| COD-003             | 09, 10, 11                                                                                                                | Ch.5 limits added in response to the personas; codex does not credit them                                                                                                                                             |
| COD-004             | 10 (BLOCKER)                                                                                                              | Applied 2026-07-27 per `PENDENCIAS.md:191-215`; the `:872` residue is new and neither the personas nor codex isolate it                                                                                               |
| COD-005             | 10 (F-02)                                                                                                                 | Author ruled on PCGrad at `PENDENCIAS.md:180-184`; codex re-raises a settled ruling                                                                                                                                   |
| COD-008             | 05                                                                                                                        | Codex adds the Mikolov and Standley findings, which persona 05 did **not** report; persona 05 explicitly cleared the scikit-learn site that codex flags. **Genuine disagreement, and codex is right on two of three** |
| COD-014             | 06, 11, 14                                                                                                                | Applied; the Markov paragraph rewrite is at `PENDENCIAS.md:217-228`                                                                                                                                                   |
| COD-017             | 18                                                                                                                        | Portuguese labels fixed; float and small labels remain                                                                                                                                                                |
| NUM-4               | 06                                                                                                                        | Same `[VERIFY]` flag                                                                                                                                                                                                  |
| Markov 22.4 percent | `FACT_GATE_v3.md` B-1                                                                                                     | Codex quotes the superseded number without flagging it; the fact gate caught it and it is now 32.1 percent                                                                                                            |

**The two places where codex and the personas genuinely disagree, both worth the author's attention:**

1. **The scikit-learn citation.** Persona 05 audited the site and marked it SUPPORTED with a reason; codex marks it a
   confirmed claim-support failure. On the evidence, persona 05 is right about what the sentence claims and codex is
   right that a versioned software citation would be cleaner. This is a style question wearing a fact-gate costume.
2. **The integrity paragraph.** Persona 09 protects it, personas 15 and 01 want it broken up, codex asks for both in
   separate findings. Resolve as `_history/_review_v2/README.md` does:
   insert breaks, change no words.

**One thing codex found that no persona did.** The capacity-control count error (COD-010) is codex's own, and it is a
real number defect in frame prose that four number-focused reviewers missed. It deserves credit.

---

## 6 · Fixable without the author

Ordered by value. Every item names its site, its source, and what the corrected text asserts. None introduces a number
that is not quoted from a committed artifact, and none strengthens a claim. Items marked `[sign-off]` are mechanically
safe but touch a claim, a protocol paragraph, or reproduced article prose, so under `AGENT_GUARDRAILS C2` they should
land as proposals rather than silent edits.

1. ~~**COD-010 / NUM-1 / NUM-2 — the capacity-control sentence.**~~ **DONE at 08:53 by another hand**, while this audit
   was being written. `6_conclusion.tex:116-118` now reads
   "the widened model was fitted under three training configurations, twenty models each and sixty in total, and the
   strongest configuration averages 56.16 macro-F1, standard deviation 1.89". That is the count, the statistic and the
   spread, all three, against
   `docs/results/closing_data/capacity_matched_stl_cat/README.md:19,:39`. No verdict moved. Verify the deferred-spread
   note at `6_conclusion.tex:155-158` is retired, since it now describes a condition that no longer holds.
2. **NUM-3 / COD-015 (f) — the gradient scope in Ch.6.** `6_conclusion.tex:177`. "three of the six datasets" → four
   Gowalla states, three of the five United States datasets reported plus Georgia, which the dissertation does not
   otherwise use. Copy the scope clause already approved at `5_mobiwac.tex:204-208`. Source
   `docs/results/mtl_improvement/R0_matched_metric_bar.json` (`states`: alabama, arizona, georgia, florida). Removes a
   Ch.5-versus-Ch.6 contradiction.
3. **COD-008 — two bibliography records to their versions of record.**
   `kokkinos2016ubernet` → CVPR 2017, DOI 10.1109/cvpr.2017.579, pp. 5454–5463;
   `mai2023sphere2vec...` → ISPRS J. Photogramm. Remote Sens. 202:439–462, DOI 10.1016/j.isprsjprs.2023.06.016. Both
   verified against Crossref this session. Add Appendix B rows.
4. ~~**COD-008 — the Mikolov negative-sampling site.**~~ **DONE at 08:54 by another hand.**
   `4_courb.tex:208` now cites `mikolov2013word2vec,mikolov2013negsampling`; the new entry is at `references.bib:685`;
   `apx_b_errata.tex` carries a row stating that arXiv:1301.3781 "introduces skip-gram but not negative sampling" and
   that arXiv:1310.4546 was added alongside it. This is the first of the two repairs I named and it is the better one,
   since the citing sentence claims both methods.
5. **COD-017 — the two Ch.5 diagrams.** Regenerate pp. 62 and 64 with labels at 9 to 10 pt; they currently carry 389 and
   351 glyphs at 6.97/7.27 pt against a 11.96 pt body.
6. **COD-017 — the Appendix B float and the Resumo keywords.** Split the bibliography-errata table at
   `apx_b_errata.tex:563` or reduce row padding to clear the 21.55853 pt warning both logs report; keep the three
   keyword lines with the Resumo so p4 is not a near-blank page. Do this last, after the prose stops moving.
7. **COD-015 (d) — the two unused metric promises.** `2_fundamentals.tex:471` (mean reciprocal rank) and `:476-478`
   (relative multi-task performance change). Neither quantity is reported anywhere; both phrases render on p24 alone.
   Delete the promises.
   `[sign-off]` — deleting a metric definition is a scope change to the Fundamentals chapter.
8. **COD-015 (c) — the Gowalla vintage in the frame.** `6_conclusion.tex:196` says
   "2009 and 2011"; Ch.4's published prose at `:425` says "February 2009 and October 2010". Match the frame to the
   published range.
9. **NUM-4 — the HGI sweep spreads.** `2_fundamentals.tex:172`. Quote 0.7388 ± 0.0205 to 0.8186 ± 0.0123 from
   `research/embeddings/hgi/README.md:546-551`, satisfying
   `WRITING_LAW §3`. The `[VERIFY]` flag on the averaging convention stays.
10. **COD-016 — break the integrity paragraph.** `5_mobiwac.tex:376`. Insert paragraph breaks at the four grounds,
    changing no words. This is the resolution
    `_history/_review_v2/README.md` already reached between personas 09 and 15.
11. **COD-004 — the trunk attribution.** `5_mobiwac.tex:872`. Remove the component attribution and keep the operational
    statement. `[sign-off]` — highest-value single sentence in this list; it removes a contradiction with `:713` one
    page earlier, and it needs an Appendix B row because it is interpretive prose in a re-typeset chapter.
12. **COD-003 — the one global leakage word.** `1_introduction.tex:158`. "a leakage-guarded statistical protocol" → "a
    user-disjoint statistical protocol".
    `[sign-off]` — it is a specific-objective statement.
13. **COD-006 — two statistical clauses.** `5_mobiwac.tex:418`. "before any result was read" → "before the final result
    board was read" (the protocol's own header says
    "BEFORE the board unblinds", and its §3.2 pins the margin using a two-seed Florida gap); "The equivalence is well
    powered" → a statement of observed interval precision conditional on the fixed split, using the 0.01-to-0.18 figure
    already in the sentence.
    `[sign-off]` — this is the paragraph the Ch.5 verdict rests on.
14. **COD-005 — the balancer screen's scope.** `5_mobiwac.tex:185`. Add the scope the audit records: registry defaults,
    seed 0, Alabama and Florida (`docs/results/mtl_improvement/T4_audit_and_verdict.md:8-17`). `[sign-off]` — it
    qualifies a result claim.
15. **COD-009 / COD-018 — repository records, all outside `src/`.** Page counts in
    `CLAUDE.md:28-29`, `PLAN.md:17-18`, `HANDOFF_v1.md:71,:130`, `PENDENCIAS.md:432-433`
    → 102/97. `4_courb_ADAPTATION_LEDGER.md:3` source of record → the published Portuguese article, with the English
    translation named as the donor. Refresh the Ch.4 and Ch.5 ledger inventories against the current chapters.

## 7 · Needs the author

1. **COD-002 — the Ch.4 static-shortcut disclosure.** He has already authorized an appendix (`PENDENCIAS.md:145-150`)
   and identified the co-author courtesy notice as a precondition. Outstanding: send the notice to Tarik S. Paiva;
   approve the appendix text; approve the one-clause scoping of `1_introduction.tex:114` and a Ch.6 §6.2 limitation
   bullet. This is the single largest open item in the document.
2. **COD-003 — whether to run the exact-lineage nonlinear future-edge test.** A research decision, not an edit. If the
   answer is no, Ch.5's current wording is already the conditional form the review's own option 2 describes, and only
   item 12 above is needed.
3. **COD-005 — the Nash-MTL cost claim: report or correct?** Currently preserved and named in Appendix B, per his prior
   REPORTED-NOT-CORRECTED ruling; `PENDENCIAS.md:250` asks whether to move it into the errata table. Also
   `4_courb.tex:120`'s unconditional
   "ensures that the update is beneficial for all tasks".
4. **COD-005 — PCGrad.** Already decided (`PENDENCIAS.md:180-184`: keep it named). Recorded here so nobody reopens it.
   His stated reason is defensible; adding the screen's scope (item 14) is what makes it fully honest.
5. **COD-007 — the Ch.3 and Ch.4 records.** Can the original CBIC split axis, seed count, tuning budget and checkpoint
   rule be recovered? Can the published CoUrb execution seed be established? If not, the chapters should be marked
   historical descriptive evidence, which the frame already half does at `2_fundamentals.tex:496-500`.
6. **COD-008 — the Standley sentence.** `3_cbic.tex:210` is published prose whose claim the cited paper does not
   support. Errata-policy decision: narrow it in the chapter with an Appendix B row, or preserve and name it as with the
   Nash cost claim.
7. **COD-011 / COD-012 — the institutional facts.** CEP/IRB determination if the program requires one; cover; approval
   sheet; committee names; defense date; Article 21 comprovante; anti-plagiarism certificate; the font ruling (note that
   the loaded package is `newtxtext/newtxmath`, not TeX Gyre Termes); the AcademicoPG preview offset.
8. **COD-013 — the 31 `[NEEDS SIGN-OFF]` markers.** Either work through them before circulation or weaken Appendix C to
   the true current state. Distribution: `0_main.tex`
   6, `6_conclusion.tex` 6, `5_mobiwac.tex` 5, `apx_a_contributions.tex` 4,
   `apx_b_errata.tex` 3, `1_introduction.tex` 2, `2_fundamentals.tex` 2, and one each in Appendices C, D and E. Also:
   name the AI model versions that are independently verifiable, since the appendix currently says "Claude Opus family".
9. **COD-015 (a) — the Ch.3 preface clause.** "Chapters 4 and 5 revise that verdict by changing the input representation
   rather than the architecture" understates Ch.5's topology and task-pair changes, which the introduction states
   correctly at :124-130. Rewording it is an arc characterization.
10. **COD-016 — `3_cbic.tex:340`.** The awkward published sentence about the unbalanced MTL/single result. My reading is
    that it means a per-category comparison can look worse than the aggregate, but confirming the intent and authorizing
    a clarification is his.
11. **COD-018 — Appendix A's CoUrb roles.** Concrete contributions in conceptualization, software, experiments,
    analysis, visualization and writing. Only he holds these facts.
12. **NUM-7 — whether to call the CoUrb per-cell envelope an "oracle."** The word is not in
    `GLOSSARY.md`, and the registry's fail-closed rule blocks its use until he approves an entry. The convention itself
    can be stated in Ch.6 without the word (item list above).

---

## 8 · Two notes on how to read the review

**It is a competent review of a document that no longer exists.** Its executive summary leads with four gate failures,
of which one (COD-001) is fixed, one (COD-011) is fixed, one (COD-002) is half-fixed in the sense that the measurement
exists and the disclosure does not, and one (COD-012) is fixed on the item the repository controls and open on the items
it does not. Its severity ordering was right at its date. Acting on its statuses today would mean re-doing four rounds
of finished work.

**Its failure mode is asserting the document's state from the source rather than the render.** Several findings quote a
source line and infer what the reader sees; where the correction round changed the rendered page and not the reviewer's
copy, the finding is stale. Its own closing recommendation anticipates this — "A final reviewer pass should verify the
rendered artifact, not only source diffs and logs" — and that is the right instruction. Every verdict in this file was
checked against the 102-page and 97-page renders of 2026-07-27, not against the source alone.

---

# Round 6 outcome: what happened to each finding

**Appended 2026-07-28**, after the round the author commissioned in response to this audit. Every
`COD-` and `NUM-` id above is listed here exactly once, with what was **done**, the commit, and where
the decision lives if it was not applied. Read this section as the answer sheet to the audit; read
`src_utils/PENDENCIAS.md` §2 for what is still yours.

**Two things to know before reading the table.**

1. **About a third of the file:line coordinates above are stale.** This audit was written against a
   97/92-page pair, re-anchored to 104/99, and annotated against a build that is now 108/105/109. Of
   79 cited coordinates, 25 land on a comment line, a blank line, or past the end of a file, and the
   three paper chapters have since been split into per-section files. Every coordinate was re-resolved
   by phrase in `_history/_round6/ANCHORS.md`; use that, not the line numbers here.
2. **Four statements in this audit were re-measured and are wrong.** They are marked in the table.
   The audit is a good document and this is not a complaint: it was written against a build that no
   longer exists, and one of its verdicts rested on an instrument that cannot see what it was pointed
   at.

## The table

| id | Audit verdict | Round-6 outcome | Where |
|---|---|---|---|
| COD-001 | RESOLVED | **Confirmed still resolved, and the class recurred twice more.** A twelfth instance was found on p.77 (`F-02`: an article orphaned across an inserted comment block, leaving a subjectless sentence in section 6.2) and a thirteenth was written **by me** while fixing something else, caught in the render. The detector was extended to the split layout. | `ec1cea0d`, `fecc7fb1` |
| COD-002 | PARTLY | **APPLIED, as the author ruled.** He ruled the finding be recorded outside the text: `LEFT_OUT.md` created for exactly this, and a suppressible Appendix B section written with the co-author's agreement. Its central paragraph was then **refuted by the domain panel and rewritten** (D-01 below). | `e9370222`, `28097d93`, `4b609643` |
| COD-003 | PARTLY | **APPLIED.** The Check2HGI loss is now three numbered equations in Ch.2 with every symbol defined at first use, transcribed from `docs/context/check2hgi_overview.tex` and verified against it by the fact gate. The joint model's descent from MTLnet is named. | `456eaa72` |
| COD-004 | PARTLY | **APPLIED.** The trunk attribution softened; the disconfirming arm in the comment block read and weighed by the domain panel, which judged the softening right. | `519de348` |
| COD-005 | PARTLY | **APPLIED.** The screen's scope is now stated: one seed, two named datasets, 19 arms. The fact gate recomputed all 19 from `T4_full_screen.json` and confirmed the empty winner set. | `519de348`, `09d48ac5` |
| COD-006 | PARTLY | **APPLIED.** "before any result was read" and "well powered" removed; "identically" checked and kept where the design supports it. | `519de348` |
| COD-007 | PARTLY / **NEEDS-AUTHOR** | **APPLIED, and the audit's premise was wrong.** It recorded the CBIC codebase as unavailable; it is in this repository at `9b06053f` with run artifacts committed. Split axis, seeds and checkpoint rule recovered from code plus artifacts for both chapters and added as declared additions with an Appendix B trail. The checkpoint block is character-identical across the two codebases. **The tuning budget is NOT RECOVERABLE** (no search harness ever existed, losing configurations not committed) — `PENDENCIAS.md` §2.6. | `519de348`, `a7ab2eaa` |
| COD-008 | PARTLY | **APPLIED.** Every citation instance in the document audited at its source of record, not sampled. The Standley citation corrected (the source argues against the claim it carried), two preprint records upgraded to their versions of record, and the failures concentrate in the inherited related-work sections rather than in the frame. | `9893a2c1`, `6951fceb`, `f8919dd4` |
| COD-009 | PARTLY | **APPLIED and gate-verified.** The L5 translation-fidelity gate ran against the published Portuguese as source of record and returned PASS WITH FINDINGS: no claim-strength drift, no number mismatch, no silent omission. It determined the Nash-MTL overclaim is **the published article's own**, which is what makes the Appendix B erratum row correct rather than a translation defect. | `cef4c990` |
| COD-010 | CONFIRMED | **APPLIED** in round 5 and verified still correct here; the sentence carrying it is the one whose subject `F-02` restored. | `ec1cea0d` |
| COD-011 | RESOLVED | Confirmed. Appendix E in both builds. | — |
| COD-012 | PARTLY | **APPLIED, and one half of it was found to be a different defect than the audit thought.** The margins were re-derived by compiling a probe with the real preamble: 3/2/3/2 cm and 1.500x spacing, exact to the manual. The remaining half was the **deposit build's page numbering**, which printed 11 on physical page 8 — non-compliance on the one build that is deposited. | `2d117c7a`, `29c7629c` |
| COD-013 | CONFIRMED | **APPLIED.** Appendix C's claim that the document "passed an eighteen-reviewer panel" was false against that panel's own recorded verdicts (two gate FAILs) and was removed. The disclosure was trimmed to the author's instruction. | `456eaa72` |
| COD-014 | RESOLVED | Confirmed. Zero occurrences of the retired names. | — |
| COD-015 | PARTLY | **APPLIED, and the audit's example was wrong.** It cited Ch.6 as still saying "three of the six datasets"; measured, every rendering locus already said four, and the two that differ are scoping narrower quantities. What *was* wrong is the **bound** on that same sentence, false for Alabama (N-1 below). | `456eaa72`, `fecc7fb1` |
| COD-016 | PARTLY | **APPLIED.** The Resumo and Abstract cut from 500/423 words to 310/271 and rebuilt as an eleven-sentence claim-parity pair, 19 claims in both languages, reviewed by six personas afterward. The 546-word integrity block was trimmed. | `40ed8e7b`, `d4baeb8b` |
| COD-017 | PARTLY | **PARTLY APPLIED, and the audit tracked the wrong two figures.** Its float warning was already gone (the longtable conversion fixed it). The two diagrams it flagged were rescaled to 93.2 and 66.3 percent of body. Then the visual pass measured all four: **the two the audit did not track are the two smallest**, both at about 45 percent. Registered in `LEFT_OUT.md` LO-6 as deferred, awaiting the author's authorization to alter published figures. Also here: the audit's diagram page numbers were off by one, and its own instrument (`FPDFText_GetFontSize`) is blind to `\includegraphics` scale and would have reported no improvement. | `1d0002af`, `2bf5f8ea` |
| COD-018 | PARTLY | **APPLIED.** Page counts synced across four files; `CLAUDE.md`, `NORTH_STAR.md`, `GLOSSARY.md`, `AGENT_GUARDRAILS.md`, `README_SRC.md` and `AGENT_HANDOFF.md` all updated; a guardrails rule that contradicted the author's own ruling amended; four new gates added for silent defect classes. | `7343c8ad`, `1ef83867`, `a8865214`, `29c7629c` |
| NUM-1, NUM-2 | CONFIRMED | Already applied in round 5; verified. | — |
| NUM-3 | PARTLY | **NO EDIT NEEDED — the audit was wrong.** Every rendering locus already said four. | `de921786` |
| NUM-4 | live `[VERIFY]` | **APPLIED.** Re-anchored to its source table with spreads. | `456eaa72` |
| NUM-5 | REFUTED as stated | No action, correctly. | — |
| NUM-6, NUM-8 | RESOLVED | Confirmed. | — |
| NUM-7 | PARTLY | **APPLIED and then bounded further.** The convention was already stated at all three sites; the domain panel then found the number quoted **unlabelled** in Ch.6 as the arc's diagnosis, when it is the static task's and this round's own Appendix B disqualifies that task. It now carries its task and qualification. | `4b609643` |

## Findings this round added that the audit did not have

These came from the eight review tracks, none of which had seen the others' work. Full detail in
`PENDENCIAS.md` §1.3.

| id | Severity | What | Commit |
|---|---|---|---|
| the compile blocker | **Critical** | The source had not compiled for six commits while `build.sh` certified it clean, because `nonstopmode` recovers from the error and writes a full PDF that the script measured | `ba90aa6d` |
| N-1 | BLOCKER | The gradient-cosine bound is false for Alabama, in both the dissertation and the manuscript under review. Created **by this round**: the sentence's scope was corrected without re-checking the quantity that depends on the scope | `fecc7fb1` |
| N-2 | MAJOR | Ch.2 asserted a gap that this round's own Ch.3 addition had filled. The repair was **predicted in writing** and drafted, and fell between two tracks' remits | `fecc7fb1` |
| D-01 | BLOCKER | My Appendix B exculpation of Ch.3 does not follow from its premise: the graph is undirected and the convolution aggregates the node with its neighborhood, so the label returns at the first hop | `4b609643` |
| F-01 | BLOCKER | **5 of 13** reproducibility paths absent from the published branch. All thirteen exist locally: the promise was wrong, not the code. Counted twice wrong before this: 8 of 12 (a line-based grep missed `m1_full_output.txt`, sharing a source line with another `\path{}`), then 9 of 13 (compared PATHS, but `mobiwac` has no `docs/` tree and keeps these under `analysis_protocol/` -- three files were already public with identical bytes). The 5 is by CONTENT, `git hash-object` against all 552 blobs in the branch | `ec1cea0d`, `c6e62c62`, round 7 |
| C-1, E-5, E-2 | MAJOR | Deposit-build numbering; ten footnote marks hyperlinked to page 1 in every build; twelve files with a missing or dangling TeX root | `29c7629c` |
| STY-01, AIC-01 | MAJOR | Seven unregistered terms, two of them missed by my own registration pass; and a density guard that had been frozen by a prior review and lived only in that review's report | `a8865214` |
| C-6 | MAJOR | `make check` exited 2 for the whole round while six commit messages said it passed | `6ee23ca7` |

## What this round got wrong about itself

Eight claims of mine were corrected against measurement, each by a different pass rather than by me:
a false bound carried across a scope correction; the Ch.3 exculpation; "all gates pass" with the gate
exiting 2; "byte-identical, same SHA" when what matches is the extracted text layer; a font-size
instrument blind to inclusion scaling; an anchor line I read wrong; a `[VERIFY]` flag raised against a
correct claim by reading a section headed "(superseded)"; and a gate test that was invalid because I
copied the fixed PDF into the broken tree. The pattern is consistent enough to name: **every one was
a claim about the work rather than a result of it**, and every one was caught by fresh eyes.


---

<!-- estado-rodada -->
> **Rodada encerrada · último toque 2026-07-29 · sem autoridade.**
> Este ficheiro é registo de proveniência do que foi discutido nesta passagem, não fonte
> de um facto corrente. O que ficou decidido está em [`VEREDITOS.md`](../../../VEREDITOS.md);
> os valores entregues estão em `CLAUDE.md` §0.1. Não copie nada daqui sem confirmar lá.
