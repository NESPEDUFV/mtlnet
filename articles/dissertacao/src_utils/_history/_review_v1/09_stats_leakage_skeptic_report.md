# 09 · Stats & leakage skeptic — review report (v1)

> Persona: methods-and-statistics reviewer with a data-leakage specialty. Read-only.
> Scope: src/chapters/{3_cbic,4_courb,5_mobiwac}.tex + statistical claims in ch 1/2/6.
> Sources of truth read this session:
> - docs/studies/pre_freeze_gates/A4_RESULTS.md (transductivity audit)
> - docs/studies/closing_data/v17_completion/STATISTICAL_PROTOCOL.md (+ deviation log §8)
> - docs/studies/closing_data/RESULTS_BOARD.md (Ch.5 numbers source of truth)
> - NORTH_STAR.md §4 (per-chapter honesty items) + §6 (story spine)
> STATUS: IN PROGRESS — written incrementally.

## Evidence base digest (what the text SHOULD carry)

### Leakage defenses (the audit is the answer; verify numbers + scope)
- **User-disjoint folds** (StratifiedGroupKFold, seed): the sanctioned defense why overlap
  windows cannot leak. Must be STATED as the reason overlap cannot leak.
- **Transductive substrate (A4 audit):** Check2HGI trains on ALL check-ins incl. val users.
  Measured inflation ≈ 0:
  - reg: AL -0.33pp, AZ +0.01pp, FL -0.12pp (within fold noise)
  - cat (POI-level proxy, in-coverage subset): AL +0.29pp (66.8%), AZ +0.27pp (71.9%), FL +0.00pp (86.9%)
  - CAVEATS that must travel: (1) cat is a POI-level PROXY on ~67% in-coverage subset, not
    exact check-in-level; (2) residual (contextual per-visit component + cold-POI remainder)
    not directly measurable on transductive substrate; bounded by inductive-Check2HGI future work.
  - SCOPE: only AL/AZ/FL audited. CA/TX/Istanbul NOT audited.
  - Within-user future-edge channel: bidirectional consecutive-visit edges, finite receptive field.
- **Tuning leakage:** no third split -> epoch selection/tuning consult eval folds. Deltas
  protected (both arms share the bias); ABSOLUTE numbers are selection-biased -> must be stated
  where absolutes are read.
- **Dev-seed contamination:** reporting seeds {0,1,7,100}; held-out seed discipline.
- **Preprocessing symmetry:** identical filtering/windowing for every compared model.

### Statistics (STATISTICAL_PROTOCOL.md)
- n=20 = 4 seeds {0,1,7,100} x 5 folds (FL aux may reach n=25 with seed 42).
- Family A (headline): cat -> paired Wilcoxon superiority, one-sided; reg -> TOST non-inferiority.
- delta_reg = 2 pp, PRE-REGISTERED per-axis (NOT inherited from substrate-axis delta), user-confirm.
- Holm-Bonferroni within cat-superiority (6 states); reg TOST cells NOT pooled into cat Holm family.
- Single-seed n=5 ceiling: p=0.0312 one-sided / 0.0625 two-sided (5/5 folds).
- Pairing ONLY on same folds (user-disjoint gated overlap). Overlap-vs-non-overlap = unpaired.
- Selection convention: JOINT-BEST (geom_simple selector, one saved model/fold) as of 2026-07-18
  author switch; board-of-record is per-task diagnostic-best (do not mix).
- Joint-best re-run verdicts (2026-07-18 deviation log, NO verdict changed):
  - cat superiority + Holm m=6 all reject (worst adj p = 1.0e-06)
  - reg TOST non-inferior: AL (-0.41, 90% CI -0.63..-0.20), AZ (0.00, CI -0.08..+0.07)
  - reg superiority: Istanbul (+0.19, CI +0.15..+0.23, 20/20), FL (+0.71, CI +0.67..+0.76),
    TX (+2.11, CI +2.10..+2.13), CA (+2.20, CI +2.19..+2.21)

### Per-chapter honesty items (NORTH_STAR §4)
- Ch.3 CBIC: CBIC-era protocol; Nash-MTL "consistently better" predates solver-bug; time-index claims.
- Ch.4 CoUrb: split is STRATIFIED BY SAMPLE, NOT user-disjoint (weaker than Ch.5 — say so).
  Verified firsthand: plain StratifiedKFold on samples, userid dropped before splitting;
  a user's windows can span train and test.
- Ch.5 MobiWac: region verbs bound to tests (outperforms Istanbul/FL/TX/CA, matches AL/AZ,
  never upgrade AZ); "submitted, under review"; restore leak-audit prose + statistical protocol detail.

---

## FINDINGS (incremental — appended as chapters are read)

## CHAPTER 5 (MobiWac) — findings (PRIMARY TARGET)

### Numbers that TRACE (verified against sources of truth — do not edit away)
- Region TOST/superiority CIs all match STATISTICAL_PROTOCOL.md §8 joint-best deviation log EXACTLY:
  AL (-0.41; -0.63..-0.20), AZ (0.00; -0.08..+0.07), FL (+0.71; +0.67..+0.76),
  Istanbul (+0.19; +0.15..+0.23), TX (+2.10..+2.13), CA (+2.19..+2.21). ✓
- Transductivity paragraph numbers match A4_RESULTS.md: reg -0.33..+0.01 (AL/AZ/FL),
  cat 0.00..+0.29, coverage 67-87%. ✓ Scope correctly limited to AL/AZ/FL; residual
  (unseen-place visits) named. ✓
- Freeze/W6 control "within 0.3" matches RESULTS_BOARD §1c (max |Δ|=0.28). ✓
- Region-gain monotonicity -0.41 -> +2.20 across US states matches table; co-variation
  with corpus size honestly hedged ("not a precise law"). ✓
- CI convention (90%) announced in §5.3 before first use in §5.6; correct for both
  one-sided superiority (a=0.05) and TOST (1-2a). ✓
- External-baseline disclaimer present: "these externals run on their own embeddings...
  the controlled comparison remains the Dedicated column." ✓ (defense correctly carried)
- User-disjoint fold rationale STATED as the reason overlap cannot leak: "we split by user...
  so all of a user's windows fall in the same fold and overlap cannot leak: a test user's
  visits never appear in training." ✓ (the sanctioned defense, correctly scoped)
- Region-transition prior: built per-fold train-only; joint/dedicated do not use it; only
  HMT-GRN does. Consistent with champion alpha=0 (RESULTS_BOARD MTL_SKIP_INERT_LOGT). ✓

### FINDING M1 [MAJOR] — reported superiority test differs from pre-registered test; deviation unlogged; n=4 parametric assumption undefended
QUOTE (§5.3, setup, 05_setup.tex:42 / chapter 2_... line ~ "Metrics and statistical tests"):
  "The assignment and the margin were fixed in an analysis plan during development and are
   released with the code; superiority is tested with a paired $t$ on the per-seed means and
   reported with the 90\% confidence interval of the paired difference."
ATTACK: The committed pre-registration (docs/studies/closing_data/v17_completion/STATISTICAL_PROTOCOL.md
  §2) pre-registers "paired Wilcoxon signed-rank on the matched per-fold Deltas, multi-seed
  pooled (n=20)" for ALL superiority claims. The paper reports a paired t on per-seed means (n=4).
  The paper's OWN section-plan comment (05_setup.tex:5) still reads "paired Wilcoxon for beats".
  The protocol deviation log (§8) records ONLY the joint-best convention switch, NOT a test switch;
  its "worst adjusted p=1.0e-06" is a Wilcoxon-n=20 figure, whereas the chapter reports "paired t,
  corrected p<0.001". CRITICAL: a Wilcoxon signed-rank at n=4 has a minimum one-sided p of
  2^-4 = 0.0625 -- it CANNOT reach significance at the per-seed-mean pairing the paper adopts.
  So the switch to a PARAMETRIC t is load-bearing for significance at n=4, and it rests on a
  normality assumption 4 points cannot support (df=3). An examiner asks: which test was
  pre-registered, why does the reported one differ, and is the deviation logged?
NUANCE (not a method flaw): pairing per-seed means (n=4) is arguably MORE honest than per-fold
  n=20 (folds within a seed share a split -> not independent; seeds are the true replicate).
  The effect sizes are 50-450x the cross-seed sd, so no reasonable test fails to reject.
TO SURVIVE: (a) name the specific artifact that pre-registered the paired-t/per-seed-mean design,
  OR acknowledge it as a deviation from the pre-registered per-fold Wilcoxon, adopted BECAUSE
  seeds are the independent replication unit; (b) defend the parametric choice at n=4 in one
  clause (effect >> cross-seed sd; Wilcoxon cannot resolve at n=4), so the df=3 attack is
  pre-empted; (c) reconcile the "released with the code" analysis plan with STATISTICAL_PROTOCOL.md.

### FINDING M2 [MAJOR] — region SUPERIORITY is a post-hoc upgrade from the pre-registered non-inferiority framing; superiority family not enumerated or multiplicity-corrected
QUOTE (§5.6): "On region (Acc@10), the joint model outperforms the dedicated ceiling at
  Florida, Texas, California, and Istanbul, and stays a non-inferior match (TOST, +-2pp) at
  Alabama and Arizona."
  + setup claim: "where the joint model was expected to outperform, we test superiority;
  where it was expected only to match the dedicated model, we test non-inferiority."
ATTACK: STATISTICAL_PROTOCOL.md §1 (Family A) pre-registers region as NON-INFERIORITY for the
  whole family ("reg -> non-inferiority (MTL not worse than STL by more than delta_reg)");
  §7 DO-WRITE pins "non-inferior on next-region... TOST, delta_reg=2pp" as the intended framing.
  Per-state region SUPERIORITY (FL/TX/CA/Istanbul) appears only in the 2026-07-18 §8 deviation
  log, AFTER results. Pre-closing-board expectation was region COST (BRACIS "MTL pays 7-17pp"),
  making a pre-registered region-superiority assignment implausible. So the sentence "we fix the
  assignment in advance... superiority where expected to outperform" overclaims pre-registration
  for the per-state region split. Moreover, category superiority is Holm-corrected across 6 states,
  but the 4 region-superiority claims are reported via CIs with NO enumerated family and NO
  multiplicity correction (persona item 10: nothing tested outside a family silently). Asymmetry.
NUANCE: reporting superiority when you pre-committed to the weaker non-inferiority bar is
  conservative in spirit, and TX/CA CIs (+2.10.., +2.19..) are so far from 0 that correction is
  immaterial. The problem is the PRE-REGISTRATION CLAIM + missing family enumeration, not the result.
TO SURVIVE: state that region was pre-registered as non-inferiority, and that superiority at the
  large states is a stronger result confirmed post-hoc (CI cleared zero), not a pre-assigned
  direction; enumerate the region-superiority comparisons as a family and either correct them or
  note the CIs are far enough from zero that correction does not change the verdict.

### FINDING M3 [MAJOR] — no-third-split disclosed as mechanism, but its consequence (selection-biased absolutes) is not stated where absolutes are read
QUOTE (§5.5): "The held-out fold is the validation data; we reserve no third split."
  + (§5.6) "every reported model is one saved artifact per fold, read at its
  validation-selected epoch".
ATTACK: With no third split, epoch selection (and any development tuning done "on validation")
  consults the SAME fold used for the reported score, so ALL absolute numbers (Tables 2-3) are
  optimistically selection-biased. The text discloses the MECHANISM but never states the
  CONSEQUENCE. Persona-mandated check: "verify the text states this consequence where absolutes
  are read." The delta-protection logic (both arms selected identically -> bias cancels in the
  difference) is the defense that makes the headline valid, and it is implicit but never stated.
TO SURVIVE: one sentence -- "because epoch selection consults the evaluation fold, the absolute
  scores are an optimistic estimate; the joint-vs-dedicated comparison is unaffected because both
  models are selected the same way on the same folds, so the bias cancels in the difference."
  Also state whether development tuning used a held-out seed disjoint from {reporting seeds};
  if not, seed-level absolutes carry additional recipe-selection bias.

### FINDING M4 [MINOR] — category transductivity measurement is a POI-level proxy at a coarser granularity than the representation it certifies; not labeled as such
QUOTE (§5.5): "Rebuilding the representation per fold, from that fold's training users only,
  moves both tasks by at most a third of a point (region -0.33 to +0.01; category 0.00 to +0.29...)"
ATTACK: A4_RESULTS.md caveat (1): the category inflation is measured via a POI-LEVEL proxy on the
  in-coverage subset, "not the exact check-in-level setup". The chapter's unified "rebuilding the
  representation... moves both tasks" implies one identical measurement for both; the coverage
  caveat (67-87%) is stated but the granularity (POI-level, not per-visit) is not. Also A4 flags
  the measurement is non-deterministic across runs (cat run-variance ~+-0.5-0.6pp; a re-run gave
  +0.88 vs committed +0.29), so the point decimals are one draw.
TO SURVIVE: add "for the category task this is measured at the place level, on visits to
  training-seen places" and lean on "within fold noise" rather than the exact +0.29 decimal.
  (Text does NOT claim more coverage than the audit has -- this is a labeling refinement, not
  an overclaim; hence MINOR.)

### FINDING M5 [MINOR] — mechanism control (freeze) and cascade tie are single-seed (n=5) results stated with headline-strength verbs
QUOTE (§5.6): "We report this attribution as a finding, not a hypothesis." (freeze/trunk control)
  + "the difference is about zero and neither task moves by more than a quarter of a point" (cascade)
ATTACK: The freeze control (RESULTS_BOARD §1c, W6) and the cascade tie (§1b) are both seed-0 n=5
  "provisional" per the board, embedded in a chapter whose headline is n=20 (four seeds). The
  strong verb "a finding, not a hypothesis" rests on a single-seed probe at 3 of 6 datasets.
  Dispersion discipline: the single-seed footing should be explicit next to these claims.
TO SURVIVE: state the freeze control and cascade comparison are seed-0 (five folds) results;
  soften "a finding, not a hypothesis" to match the single-seed evidence, or note the n.

### FINDING M6 [MINOR / VERIFY] — "13 to 27 points" region-prior inflation figure not traced to a source this session
QUOTE (§5.5): "...after an earlier whole-dataset version inflated region accuracy by 13 to 27 points."
ATTACK: A number (guardrails N1: traceable to a source file/page). Not located in A4_RESULTS.md,
  STATISTICAL_PROTOCOL.md, or RESULTS_BOARD.md. It is a self-deprecating leakage-magnitude claim
  (supports rigor), so low risk, but must trace. HANDOFF to number auditor (06).
TO SURVIVE: cite the leak-audit doc/page for "13 to 27 points". [VERIFY]


---
## UPDATES to preliminary MobiWac findings after cross-chapter + source verification
- **M1 ELEVATED to BLOCKER** and reframed as B1 below (Ch.2 defines the superiority test as
  paired Wilcoxon; Ch.5 reports paired t -> direct cross-chapter contradiction, not just a
  pre-registration deviation).
- **M6 RESOLVED (number traces):** "13 to 27 points" region-prior inflation is corroborated by
  docs/research/evaluation_protocol_review.md:39 ("~13-27 pp"), docs/context/DATA_SPLITS.md:58
  ("13-27 pp on FL-style states"), docs/NORTH_STAR.md:120/132, and
  docs/archive/.../PAPER_PREP_TRACKER.md:19 ("13-27 pp asymmetrically, more for MTL than STL at AL").
  The chapter's use ("Our joint and dedicated models do not use this prior") is consistent with the
  v17 champion (MTL_SKIP_INERT_LOGT default-on, alpha=0). No longer a [VERIFY]. Keep as-is.

## CHAPTER 3 (CBIC) + CHAPTER 4 (CoUrb) + FRAME (Ch.1/2/6) — findings

### VERIFIED FIRSTHAND this session (code + sources)
- CoUrb split: /Users/vitor/.../tarik-new/PoiMtlNet_Novo/src/etl/mtl/create_fold.py --
  `StratifiedKFold(n_splits, shuffle=True, random_state)` on sample rows, `userid` DROPPED before
  split (x_next = df_next.drop(columns=['next_category','userid'])); category side splits on
  placeid. NO GroupKFold / StratifiedGroupKFold anywhere in the project code. => sample-stratified,
  users span train/test. Matches NORTH_STAR §4 Ch.4 firsthand note exactly. CBIC shares this
  PoiMtlNet lineage (CoUrb's baseline IS CBIC's MTLnet); CBIC's own text claims only "5-fold
  cross-validation" (articles/CBIC___MTL/sections/results.tex:20) -- silent on granularity.
- CoUrb audited numbers trace to articles/CoUrb_2026/slides/judge_feedback.md: strict count
  15/21 + 1 technical tie (FL Outdoors 21.61 baseline vs 21.59 best variant); per-state means
  FL +20.24 / CA +20.91 / TX +21.98 = "20.2-22.0 pp best-of-two". Ch.4 uses these EXACTLY,
  including the best-of-two caveat and the FL-Outdoors tie. Errata applied correctly. HOLDS.
- Ch.6 capacity baseline 56.16 traces to storyline/audit/capacity_baseline_experiment.md:107,111
  (bs2048@lr0.0025, n=20, 56.16 +-1.88 vs dedicated 56.82). HOLDS.

### FINDING B1 [BLOCKER] — the superiority test is named differently in Ch.2 and Ch.5, and neither the deviation from the pre-registered Wilcoxon nor the n=4 parametric choice is defended
QUOTE Ch.2 (2_fundamentals.tex:442-445): "The paired Wilcoxon signed-rank test compares two
  models across the paired results without assuming normality, and it is the test that licenses
  the verb ``outperforms''~\cite{wilcoxon1945}"
QUOTE Ch.5 (5_mobiwac.tex:349, §5.3): "superiority is tested with a paired $t$ on the per-seed
  means and reported with the 90\% confidence interval of the paired difference." (and :551
  "paired $t$, corrected p<0.001")
ATTACK: (a) CROSS-CHAPTER CONTRADICTION -- the fundamentals chapter binds the document's central
  verb "outperforms" to a paired WILCOXON signed-rank test; the results chapter reports a paired
  T-TEST. An examiner who reads both chapters sees the dissertation license its headline verb with
  two different tests. (b) DEVIATION FROM PRE-REGISTRATION -- STATISTICAL_PROTOCOL.md §2 pre-registers
  "paired Wilcoxon signed-rank on the matched per-fold Deltas, multi-seed pooled (n=20)"; the §8
  deviation log records ONLY the joint-best convention switch, not a test switch. The paper's own
  section plan (articles/[mobiwac]/src/sections/05_setup.tex:5) still says "paired Wilcoxon for
  beats", so the t-test is an undocumented late change. (c) n=4 PARAMETRIC UNDEFENDED -- pairing
  per-seed means gives n=4 (df=3); a Wilcoxon at n=4 has a floor of p=2^-4=0.0625 and CANNOT reach
  the reported p<0.001, so the switch to a parametric t is load-bearing for significance, and it
  rests on a normality assumption four points cannot support. The text neither flags the switch nor
  defends the parametric choice.
WHICH IS RIGHT: Ch.2 + the pre-registration agree on Wilcoxon; Ch.5 (following the paper body)
  uses paired t. They cannot both stand.
NUANCE (good-faith): pairing per-seed means (n=4) is arguably MORE honest than per-fold n=20
  (folds within a seed share a split, so they are not independent; the seed is the true replicate).
  And the category effect sizes are enormous (Delta +5.3..+9.4 vs cross-seed sd 0.01-0.10 => >50 sigma),
  so no reasonable test fails to reject. The problem is entirely TEXTUAL: two chapters name two tests
  and the choice is neither reconciled nor justified.
TO SURVIVE: pick ONE test name and use it in both chapters. If the paired t on per-seed means is
  what actually ran, (i) change Ch.2 to bind "outperforms" to the paired t (or to "a paired
  superiority test" generically), (ii) add one clause in Ch.5 defending the parametric choice at
  n=4 (effect >> cross-seed sd; Wilcoxon cannot resolve at n=4), and (iii) log the deviation from
  the pre-registered Wilcoxon in the analysis-plan record. If Wilcoxon is what ran, correct Ch.5's
  "paired t" to "paired Wilcoxon" and reconcile with the n=4 pairing (Wilcoxon at n=4 cannot give
  p<0.001 -- so this direction forces per-fold n=20 pairing instead). This is THE single weakest
  methodological sentence in the experimental chapters.

### FINDING B2 [MAJOR] — Ch.2 presents user-disjoint CV as the dissertation-wide protocol, but only Ch.5 uses it; Ch.3/Ch.4 are sample-stratified (users span train/test)
QUOTE Ch.2 (2_fundamentals.tex, §2.4): "Estimates use stratified k-fold cross-validation, and the
  folds are formed so that no user spans a split: a grouped, stratified splitter keeps all of a
  user's check-ins on one side of every fold, so that measured accuracy reflects generalization to
  new users rather than memorization of familiar ones."
  + §2 intro: "the datasets, metrics, and validation protocol used throughout (Section 2.4)"
  + §2.5: "User-disjoint cross-validation ... [is] what separate[s] a real improvement from a
  hopeful one."
ATTACK: The fundamentals chapter frames ONE validation protocol -- user-disjoint (grouped)
  cross-validation -- as the protocol of the whole dissertation ("used throughout"). But this is
  true ONLY for Ch.5. VERIFIED FIRSTHAND: the Ch.3 (CBIC) and Ch.4 (CoUrb) code uses plain
  StratifiedKFold on sample rows with userid dropped (create_fold.py) -- a user's windows can fall
  on both sides of a split. Ch.4 discloses this honestly (preface + setup: "stratified by sample,
  not by user, so the check-ins of one user may appear in both training and validation"). Ch.3 is
  SILENT (says only "5-fold cross-validation"). So a reader who takes Ch.2 at its word will
  wrongly believe CBIC and CoUrb were leakage-guarded, and Ch.4's own disclosure then CONTRADICTS
  Ch.2. (Ch.1 objective 4 gets it right -- it scopes user-disjoint CV "of Chapter 5" -- which makes
  Ch.2's unscoped generalization the outlier.)
WHY IT MATTERS: the arc's whole rhetorical strength is honesty about protocol evolution; a framing
  chapter that over-generalizes the strongest protocol to the two weaker studies undercuts exactly
  that. It also hands an examiner a "your own fundamentals chapter misdescribes two of your three
  studies" line.
NOT A METHOD FLAW: CBIC's null and CoUrb's representation-gain are both same-split A/B comparisons
  (paired Delta protected); the sample-stratified split inflates absolutes but not the within-study
  contrast, and both studies are time-indexed. The fix is textual.
TO SURVIVE: scope Ch.2's user-disjoint claim to Ch.5 (e.g. "the final study adopts user-disjoint
  cross-validation; the earlier two used sample-stratified splits, a weaker protocol the arc treats
  as a limitation"). Add one sentence to Ch.3's setup mirroring Ch.4's disclosure so CBIC is not the
  only silent chapter.

### FINDING B3 [MAJOR] — region SUPERIORITY at FL/TX/CA/Istanbul is presented as pre-assigned, but the protocol pre-registered region as NON-INFERIORITY; the region-superiority family is neither enumerated nor Holm-corrected (category is)
QUOTE Ch.5 (§5.3): "where the joint model was expected to outperform, we test superiority; where it
  was expected only to match the dedicated model, we test non-inferiority."
  + (§5.6): "On region (Acc@10), the joint model outperforms the dedicated ceiling at Florida,
  Texas, California, and Istanbul, and stays a non-inferior match (TOST, +-2pp) at Alabama and Arizona."
ATTACK: STATISTICAL_PROTOCOL.md §1 (Family A) pre-registers region as NON-INFERIORITY for the whole
  family ("reg -> non-inferiority"); §7 DO-WRITE pins "non-inferior on next-region ... TOST". The
  per-state region SUPERIORITY claims appear only in the 2026-07-18 §8 deviation log, AFTER the
  board unblinded. The pre-closing expectation was a region COST (the superseded BRACIS "MTL pays
  7-17 pp"), so a pre-registered region-superiority assignment is not credible. Thus the §5.3
  sentence "where the joint model was expected to outperform, we test superiority" overstates
  pre-registration for the region axis. Separately (multiplicity, persona item 10): category
  superiority is Holm-corrected across 6 states, but the FOUR region-superiority claims are read off
  CIs with NO enumerated family and NO correction -- an asymmetry a reviewer will name.
NUANCE: reporting superiority when you pre-committed to the weaker non-inferiority bar is
  conservative, and the TX/CA CIs (+2.10..+2.13, +2.19..+2.21) are far enough from 0 that correction
  is immaterial; FL/Istanbul are smaller (+0.71, +0.19) but still CI-clear of 0.
TO SURVIVE: state that region was pre-registered as non-inferiority and that the large-state region
  superiority is a stronger result CONFIRMED post-hoc (CI cleared zero), not a pre-assigned direction;
  enumerate the region-superiority comparisons as a family and either Holm-correct them or note the
  CIs are far enough from zero that correction does not move the verdict.

### FINDING B4 [MAJOR] — "we reserve no third split" is disclosed as a fact but its consequence (all absolute numbers are selection-biased) is never stated; the delta-protection defense is left implicit
QUOTE Ch.5 (§5.5): "The held-out fold is the validation data; we reserve no third split."
  + (§5.6): "every reported model is one saved artifact per fold, read at its validation-selected epoch"
ATTACK: with no third split, epoch selection (and any "tuned once on validation during development"
  choice, §5.4) consults the SAME fold that produces the reported score, so every absolute number in
  Tables 2-3 is optimistically selection-biased. The text states the mechanism but never states the
  consequence, and never states the defense that rescues the headline: because BOTH arms are selected
  the same way on the same folds, the bias is common-mode and cancels in the joint-vs-dedicated
  DIFFERENCE. Persona-mandated check: "verify the text states this consequence where absolutes are read."
TO SURVIVE: one sentence where the absolutes are introduced -- "because epoch selection consults the
  evaluation fold, the absolute scores are optimistic; the joint-vs-dedicated comparison is unaffected,
  as both models are selected identically on the same folds and the bias cancels in the difference."
  Also state whether development tuning used a seed held out from the reporting seeds {0,1,7,100}; if
  not, seed-level absolutes carry recipe-selection bias too.

### FINDING B5 [MINOR] — Ch.2 says the pipeline uses class-weighted cross-entropy; Ch.5's final models use plain unweighted CE and explicitly reject class-weighting
QUOTE Ch.2 (§2.4): "The training pipeline counters the same imbalance with class-weighted cross-entropy."
QUOTE Ch.5 (§5.4, Eq 5.1): "$L_{cat}$ and $L_{reg}$ are plain unweighted cross-entropy losses" +
  "Class-weighting, tested on both outputs, lowered both region accuracy and category macro-F1."
ATTACK: direct methodological contradiction. Ch.2 (framing) asserts class-weighted CE is the
  pipeline's imbalance remedy; Ch.5 (the model that carries the headline) uses UNWEIGHTED CE and
  reports that class-weighting HURT. macro-F1 (not class weighting) is the actual imbalance remedy in
  Ch.5. Minor because it does not touch a result, but a careful reader sees the frame misdescribe the
  final model's loss. (Partly out of my lane -- hand to claim/concordance auditors 04/07.)
TO SURVIVE: change Ch.2 to say imbalance is handled by macro-F1 as the reporting metric (and that
  class-weighting was tested and not adopted in the final model), or scope the class-weighted-CE claim
  to whichever earlier study used it.

### FINDING B6 [MINOR] — same joint AL-category quantity is 64.51 in Ch.5 and 64.54 in Ch.6
QUOTE Ch.5 (Table 3, :479): joint AL category "\textbf{64.51}\sd{0.09}" (joint-best convention).
QUOTE Ch.6 (:78): "64.54 for the joint model" (in the capacity-baseline paragraph).
ATTACK: 64.54 is the diag-best v17 board value (RESULTS_BOARD §1); 64.51 is the joint-best value the
  dissertation Table 3 now reports (post-2026-07-18 switch). The capacity-baseline paragraph compares
  against the OLD convention while Table 3 reports the NEW one, so the same headline quantity (joint
  model, Alabama, category) reads as two different numbers across chapters. An examiner cross-checking
  the two chapters sees the inconsistency.
TO SURVIVE: use the joint-best 64.51 in Ch.6 to match Table 3, or footnote that the capacity
  comparison is against the diag-best board value. (Hand to number auditor 06 / concordance 04.)

### FINDING B7 [MINOR] — mechanism (freeze) control and cascade tie carry headline-strength verbs on single-seed (n=5) evidence
QUOTE Ch.5 (§5.6): "We report this attribution as a finding, not a hypothesis." (freeze/trunk control)
  + "the difference is about zero and neither task moves by more than a quarter of a point" (cascade).
ATTACK: the freeze control (RESULTS_BOARD §1c W6, seed-0 5-fold, 3 of 6 datasets) and the cascade tie
  (§1b, seed-0 5-fold, both flagged "n=5 provisional") sit inside a chapter whose headline is n=20.
  "A finding, not a hypothesis" is strong for a single-seed probe. Dispersion discipline: the n and
  seed footing belong next to these claims.
TO SURVIVE: state that the freeze control and cascade comparison are seed-0 (five-fold) results;
  either soften "a finding, not a hypothesis" or note the single-seed footing explicitly.

### FINDING B8 [MINOR] — category transductivity number is a POI-level proxy at a coarser granularity than the representation it certifies; not labeled, and non-deterministic across runs
QUOTE Ch.5 (§5.5): "Rebuilding the representation per fold, from that fold's training users only,
  moves both tasks by at most a third of a point (region -0.33 to +0.01; category 0.00 to +0.29 ...),
  within fold noise."
ATTACK: A4_RESULTS.md caveat (1): category inflation is measured on a POI-LEVEL proxy over the
  in-coverage subset, "not the exact check-in-level setup"; and it is non-deterministic (a re-run
  gave +0.88 vs the committed +0.29; run-variance ~+-0.5-0.6 pp). The chapter's unified "moves both
  tasks" implies one identical measurement for both heads; the coverage caveat (67-87%) is stated but
  the granularity (POI-level, not per-visit) is not, and the exact +0.29 decimal is one draw.
NOT AN OVERCLAIM: the text does NOT claim more coverage than the audit has (67-87% and the
  unseen-place residual are both stated). This is a labeling refinement, hence MINOR.
TO SURVIVE: add "for the category task this is measured at the place level, on visits to
  training-seen places" and lean on "within fold noise" rather than the +0.29 point value.

### OUT-OF-SCOPE HANDOFFS (one line each)
- Ch.2 §2.4 introduces mean reciprocal rank (MRR) as part of the region metric set ("accompanies
  it where the joint comparison needs a rank-sensitive figure"), but Ch.5 reports only Acc@10 --
  MRR appears in no Ch.5 table. Metric-set overclaim -> concordance (04) / number (06).
- Ch.2 cites pedregosa2011sklearn (2011) for StratifiedGroupKFold, a scikit-learn v1.0/2021 feature
  (ledger acknowledges the anachronism as an author ruling) -> citation auditor (05).
- CoUrb (Ch.4) has no leak audit equivalent to Ch.5's A4, and its transductive-embedding channel
  (DGI/HGI trained on the whole dataset) is undisclosed; the sample-stratified split IS disclosed.
  Delta protected, absolutes inflated -> claim/honesty auditor (07) if a fuller CoUrb caveat is wanted.

## WHAT HOLDS (defenses present and correctly scoped -- do NOT edit away)
1. Ch.5 §5.5 user-disjoint rationale is stated AS the reason overlap cannot leak ("all of a user's
   windows fall in the same fold and overlap cannot leak: a test user's visits never appear in
   training"). Exactly the sanctioned defense; keep verbatim.
2. Ch.5 A4 leak-audit prose is faithful to A4_RESULTS.md: reg -0.33..+0.01, cat 0.00..+0.29,
   coverage 67-87%, scope AL/AZ/FL, and the unseen-place residual named as the one part it cannot
   reach. Correctly does NOT claim CA/TX/Istanbul coverage.
3. Ch.5 region-transition prior: built per-fold train-only; joint/dedicated do not use it (only
   HMT-GRN does); the 13-27 pp full-data inflation is disclosed as the reason. All trace.
4. Ch.5 external-baseline denominator: HMT-GRN scored on region-in-training visits, ">99% of test
   visits", subset size disclosed; the joint model counts unseen-region visits as errors (harder
   convention on itself) -> the asymmetry is conservative for the joint model and disclosed. Holds.
5. Ch.5 Table 2 vs Table 3 convention asymmetry (single-recipe matched A/B vs n=20 best-vs-best
   tuned ceilings) is DISCLOSED ("keeps one fixed configuration, not the per-dataset-tuned dedicated
   model of Table 3"). Holds.
6. Ch.5 region verbs bound to tests: TOST +-2pp with 90% CIs at AL/AZ, superiority CIs above 0 at
   FL/TX/CA/Istanbul, AZ (0.00; -0.08..+0.07) reported as a match NOT a gain, AL deficit stated
   plainly. All CIs match STATISTICAL_PROTOCOL.md §8 to the decimal. Never upgrades AZ. Holds.
7. Ch.5 diag-best robustness note ("<=0.06 category, <=0.11 region") present so no claim depends on
   the selection convention. Holds.
8. Ch.4 (CoUrb) split disclosure is exemplary (preface + setup both state sample-stratified, weaker
   than Ch.5, time-indexed) and uses the AUDITED win-count (15/21 + 1 technical tie) and pp-gain
   (+20.2-22.0, best-of-two) that match judge_feedback.md. Errata correctly applied. Holds.
9. Ch.3 (CBIC) preface time-indexes both the null ("conclusion of the time, for that configuration")
   and the Nash-MTL preference (weakened by a later finding), and Ch.5/Ch.6 do not rely on Nash-MTL.
   The claim-discipline from NORTH_STAR §4 Ch.3 is honored. Holds.
10. Ch.6 capacity-matched baseline (56.16 at AL, n=20; CA partial n=15 disclosed) is a clean
    parameter-count control, reported with reading (i) of the pre-registered three; number traces.
    Honestly labeled as post-submission frame-level analysis. Holds.

## VERDICT (persona output contract)
**SURVIVES WITH CORRECTIONS.**
Weakest methodological sentence (Ch.5 §5.3): "superiority is tested with a paired $t$ on the
per-seed means and reported with the 90\% confidence interval of the paired difference." -- it
contradicts Ch.2's paired-Wilcoxon binding, deviates unlogged from the pre-registered Wilcoxon, and
rests on an undefended n=4 parametric assumption.
No finding is "the method is flawed": the deltas are common-mode-protected, effect sizes dwarf the
dispersion, the leak audit is real and correctly scoped, and most defenses already exist in the
text. Every correction is TEXTUAL (reconcile the test name across chapters; scope the user-disjoint
claim to Ch.5; state the selection-bias consequence and its cancellation; enumerate/label the
region-superiority family; fix the 64.51/64.54 and class-weighting mismatches). None requires a new
experiment.


---

<!-- estado-rodada -->
> **Rodada encerrada · último toque 2026-07-24 · sem autoridade.**
> Este ficheiro é registo de proveniência do que foi discutido nesta passagem, não fonte
> de um facto corrente. O que ficou decidido está em [`VEREDITOS.md`](../../../VEREDITOS.md);
> os valores entregues estão em `CLAUDE.md` §0.1. Não copie nada daqui sem confirmar lá.
