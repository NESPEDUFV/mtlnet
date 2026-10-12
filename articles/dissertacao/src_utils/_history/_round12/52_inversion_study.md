# 52 — Study: inverting §2.1 (tasks) and §2.2 (representations) in Chapter 2

<!-- Round 12, 2026-08-03. AUTHORIZED SCOPE: the STUDY only ("Use um fable 5 para explorar e validar a
     inversao", PENDENCIAS §6.20 item 1). NOTHING in this document is authorized to be applied; the
     author decides. This file is the single write of this task; no .tex, GLOSSARY, NORTH_STAR, or
     tracker was edited. Every claim carries file:line against the tree as read on 2026-08-03
     (a parallel agent is active; DEFINITIONS.md changed on disk mid-session and was re-read before
     quoting; quotes here are from the 15:06 copy). -->

The question: Chapter 2 currently runs 2.1 POI prediction tasks, 2.2 Representations for mobility,
2.3 Multi-task learning, 2.4 Datasets and evaluation, 2.5 Relevance. The author proposes inverting
2.1 and 2.2, with the formal definitions living in the representations section, so that the tasks
section then describes "as tarefas que podemos treinar com essas representacoes" (his words,
`fundamentals/DEFINITIONS.md:607-609`). His caution: "a narrativa tem que esta acima desse problema,
temos que ter muito cuidade" (`DEFINITIONS.md:610-611`).

---


> **Wall clock, recorded by the parent rather than self-reported.** This study ran **3,442 s (57.4 min)**
> against a **40-minute (2,400 s) checkpoint**: **43 percent over**. It reported "nothing in the assigned
> scope is unfinished", and its scope claims check out where I sampled them, but the overrun is the pattern
> every wave in this project has shown and it is recorded rather than rounded away.
>
> **The parent verified, and did not take on trust:** the three cross-references (`:15`, `:17`, `:197`), the
> two labels (`:25`, `:210`), zero references outside the chapter, `DEFINITIONS.md:613`, `NORTH_STAR.md:73-75`,
> that commit `0bbe3caa` is the author's own `src_clean` pass and is where the order-justifying sentence first
> enters the tree, and that the two prose sites it quotes are LIVE text rather than comments. **One claim
> failed that check and is corrected in the [VERIFY] list below.**
## 1. The historical finding: no recorded rationale for tasks-first exists

**The direct answer: the `fundamentals/` folder records NO argument for placing tasks before
representations.** The sweep that the parent ran found nothing, and this study confirms it. Files
read in full this session: `README.md`, `GAP_STATUS.md`, `OPEN_QUESTIONS.md`, `DRAFT_LEDGER.md`,
`COVERAGE_EVALUATION.md`, `FRONTIER_INTEGRATION.md`, `DEFINITIONS.md`, `fundamentals.tex`,
`model_lineage_table.md`/`.tex`, all three `_review/` reports, the five section directories
(each `.tex` draft and each `*_citations.md`, plus `2.4_metrics_addendum.md` and
`2.5_relevance_plan.md`), and keyword sweeps over `_verification/`. None argues the ordering.
The reviews audit citations, numbers, and domain claims; the one ordering statement any reviewer
made concerns the lineage INSIDE 2.2, not the section order ("The representation lineage is in the
correct order", `fundamentals/_review/domain_review_report.md:233`).

**What the folder shows instead: the order was inherited from the chapter map, not argued.**

1. The order arrived as a specification. `COVERAGE_EVALUATION.md:8-12` treats it as given input:
   "NORTH_STAR Ch.2 spec: 2.1 tasks (category/region/place distinct) -> 2.2 representations
   (one-hot -> DGI/HGI -> check-in level) -> ...". The map itself (`NORTH_STAR.md:73-80`) states
   the five sections with parenthetical content notes and no ordering rationale, and the beats
   paragraph (`NORTH_STAR.md:369-375`) repeats the sequence as arrows, again without a reason.
   The section drafts of 2026-07-21 (`DRAFT_LEDGER.md:5`, "Draft 1, 2026-07-21") were written into
   directories already named `2.1_poi_prediction_tasks` and `2.2_representations_for_mobility`.
   The git history cannot see further back (the repository's first commit containing
   `NORTH_STAR.md` is `bb64e220`, 2026-07-23, which postdates the folder's drafting), so how the
   map itself was first ordered is not recoverable from version control. [VERIFY: whether any
   pre-repo planning artifact argued the order; nothing on disk does.]

2. The nearest thing to an implicit rationale is a design principle, not an ordering argument.
   The 2.1 citation map opens with its goal: "establish the task space and separate the three
   prediction targets the dissertation keeps distinct, then situate the sequence-model lineage"
   (`fundamentals/2.1_poi_prediction_tasks/2.1_citations.md:22`), and its row 2 carries the
   principle behind it: "the prediction target must be named precisely" (same file, row for
   `luca2021mobilitysurvey`). That explains why 2.1 exists and what it must do; it does not say
   2.1 must come before 2.2.

3. **The explicit in-prose justification of the present order is RECENT, and it is the author's
   own.** The sentence "This section defines the prediction targets before reviewing the methods
   used for them" (`src/chapters/2_fundamentals.tex:27-28`) does not exist in the frozen draft
   (the 2.1 draft opens directly with the LBSN sentence,
   `fundamentals/2.1_poi_prediction_tasks/2.1_poi_prediction_tasks.tex:8`) and does not exist in
   the pre-merge `src/` tree (checked at `807183c1~1`). It first appears in the author's own
   revision tree at `src_clean/chapters/2_fundamentals.tex:19`, created in commit `0bbe3caa`
   (2026-08-02, "create a new src_clean where I author is doing a pass in the text and clean it")
   and merged into `src/` in `807183c1` (2026-08-02). The same holds for the chapter opening
   "It first distinguishes the POI prediction tasks ... It then traces mobility representations"
   (`src/chapters/2_fundamentals.tex:14-20`; first at `src_clean/chapters/2_fundamentals.tex:7`).
   [VERIFY: whether the author personally composed those sentences or approved them inside his
   pass; the commit shows only that they entered with his tree.] Either way, the consequence for
   this decision is the same: the only prose defending tasks-first was added on 2026-08-02,
   eleven days after the chapter was drafted, and by or under the author himself, one day before
   he proposed the inversion. It is a restatement of the existing order, not an original reason
   for it.

4. One prior decision DID consider and reject the inversion, on cost and not on narrative:
   `DEFINITIONS.md:149-153` (rejected alternative 1) declined to "move the tasks after the
   representations section" because the stated design was targets-first (quoting the :27 sentence,
   which per item 3 above is itself recent), because "Section 2.1 is titled by the tasks", because
   the related-work architecture "hangs off the task definitions", and because the cost would be
   "a chapter restructure to fix one edge". That is the July-design agent weighing edit cost
   against a one-edge fix; it is not a recorded narrative rationale from the original planning.

**Conclusion of the historical question: the absence is confirmed. Tasks-first was inherited from
the chapter map as a specification; the only explicit defense of it in prose postdates the chapter
and traces to the author's own 2026-08-02 pass. There is no original recorded rationale for the
inversion to violate.**

---

## 2. The narrative argument, both directions

### 2a. The strongest case FOR the inversion

1. **It removes the forward dependency at the root.** The audited defect is that Definition 2.3
   (the static task, `def:fund:catclf`) consumes $\mathbf{e}_p$
   (`src/chapters/2_fundamentals.tex:116-124`) while the place embedding is defined 300 lines
   later (`:434-437`). With representations first, the tasks consume objects the reader already
   holds; no definition has to move into a foreign section, and AD-4's compensating subsubsection
   inside §2.1 loses its function, exactly as the author anticipated ("maybe with this inversion
   we even need this new section", recorded at `DEFINITIONS.md` AD-4 row and pinned by probe
   `R12-ad4cond`, `src_utils/check_audit_claims.py:617-619`).

2. **The dependency graph points that way.** Every symbol edge in the thirteen-definition design
   runs from tasks to representations or to notation, never the reverse
   (`DEFINITIONS.md:101-115`): D6 (static task) consumes $\mathbf{e}_p$ (D3), D7/D8 consume $H_i$
   (D2), and the representation definitions consume only the notation sets and the check-in.
   Representations-first is the topological order of the actual symbol graph, once D1/D2
   accompany it (see §4 item 1 below for that qualification).

3. **The reading order comes to mirror the dissertation's answer.** The thesis is that the
   representation is the dominant factor; §2.2 is "the chapter's spine"
   (`fundamentals/README.md:32`). Representation-first makes the chapter's physical order
   restate its central claim, and the author's formulation gives the tasks section a natural
   new opening: the tasks one can train on these representations.

4. **The static task reads most naturally after the representation.** "Category classification
   predicts the category of a POI from its representation" (`:117`); the study it abstracts fed
   DGI embeddings to a classifier (`DEFINITIONS.md:141-144`, quoting `3_cbic/method.tex:53`).
   A reader who already holds $\mathbf{e}_p$ meets this definition self-contained.

### 2b. The strongest case AGAINST the inversion

1. **The reader meets the solution space before the problem.** §2.2's whole argument is
   teleological: "This section traces the representations used in the dissertation and explains
   why the final study moves from a place embedding to a check-in-level representation"
   (`:212-213`). The WHY is task-driven. The limitation that powers the chapter's pivot, "a
   weekday morning and a Saturday night at the same place have identical inputs at the
   representation level" (`:439-441`), is only a defect relative to a prediction target that
   varies across visits to one place. Without the targets in hand, the stakes of the static-vector
   limitation are carried by nothing. The mitigation is real but costs prose: the chapter opening
   (rewritten anyway) must state the two targets informally before §2.2 uses them.

2. **§2.2 already speaks task vocabulary that the definitions would no longer precede.** Live
   sites, comment-stripped: "trained without category or region labels" (`:253`), "No label of
   any downstream task enters that comparison" (`:272`), "repurposes that POI-level output for
   sequential prediction" (`:292`), "the best category F1" (`:300`), "condition its shared layers
   on task identity" (`:484`), the Model lineage subsection's "task-specific input encoders,
   output heads" (`:563-564`), and the lineage table's "one model for both tasks, next category
   and next region" (`src/tables/frame/lineage.tex:34`). None of these breaks a build, but each
   would then lean on an informal forward anchor rather than on a definition already given, which
   is the current defect in mirror image, at lower severity (informal anchors are prose, not
   symbols).

3. **The papers themselves are problem-first, and the chapter mirrors them today.** MobiWac's
   problem statement precedes its method ("Given a user's time-ordered check-in history, we
   predict two properties of the next visit", `src/chapters/5_mobiwac/03_problem.tex:12`), and
   the field convention the chapter's related-work follows is to name the target before the
   machinery. The banca reads three problem-first papers after a fundamentals chapter; making
   that chapter method-first is a deliberate divergence that must be owned, not an oversight.

4. **The thesis-mirror argument cuts both ways, and this is the strongest honest counterpoint.**
   The dissertation's central claim is only expressible because "the task is the SAME OBJECT
   across all three studies while $\rho$ varies" (`DEFINITIONS.md:211-213`). The tasks are the
   arc's invariant; the representation is its moving part. Tasks-first mirrors the DESIGN of the
   argument (fix the reference point, then vary the lever); representations-first mirrors its
   ANSWER (the lever is what mattered). Both are faithful mirrors of the thesis. The inversion's
   narrative gain is therefore real but not unopposed, and the choice between the two mirrors is
   an authorial one, which is consistent with the author's own caution that the narrative stands
   above the dependency problem.

5. **The chapter's entry point currently lives in §2.1.** Lines 27-38 supply the domain context
   (LBSNs, what a check-in records, the 93 percent predictability bound) that the whole chapter,
   including §2.2, presupposes. Under the inversion, either that material migrates (more content
   movement than a section swap) or the chapter opens cold on representation methods. This is a
   solvable layout question, but it is not free, and it is not in the measured cost table.

---

## 3. The cost table, verified, with corrections

Each row of `DEFINITIONS.md` §11 (same table in `src_utils/PENDENCIAS.md` §6.16) was re-measured
against the live tree this session.

| claimed cost | verdict | evidence |
|---|---|---|
| three live cross-references to the two labels, all inside `2_fundamentals.tex` (`sec:fund:tasks` x1, `sec:fund:repr` x2) | **CONFIRMED** | `grep -rn` over all `src/**/*.tex`: refs at `2_fundamentals.tex:15` (tasks), `:17` and `:197` (repr); labels at `:25`, `:210`. Zero references outside the chapter (build artifacts excluded). |
| `:14-20` and `:27` must be rewritten | **CONFIRMED, and UNDERCOUNTED** (see corrections 1 and 2) | `:14-20` narrates the order ("It first distinguishes ... It then traces"); `:27-28` justifies it and becomes false under the inversion. Both read verbatim this session. |
| the order is fixed in `NORTH_STAR.md:73-80`; inverting edits the chapter map | **CONFIRMED** | `NORTH_STAR.md:73` "2 FUNDAMENTALS", `:74` "2.1 POI prediction tasks", `:75` "2.2 Representations for mobility"; the beats paragraph repeats the order at `:369-375`. |
| zero gates or probes constrain the order | **CONFIRMED** | Grep of every `check_*.py` and `check.sh` for the ordering strings ("first distinguishes", "then traces", "targets before reviewing", "preceding sections introduce"): zero hits. The "2.1"/"2.2" mentions in the check files are PENDENCIAS item numbers, dates, or fixtures (for example `check_audit_claims.py:132-140`, `check_tracker_refs.py:5`). `R11-def27` pins the LABEL `def:fund:checkinlevel` (`check_audit_claims.py:469`), file-scoped, position-independent. `R11-fab15` pins an introduction sentence (`check_audit_claims.py:485`). |
| side effect: `fundamentals/` directory names record the old order | **CONFIRMED, note only** | Directories exist as named; the folder is frozen provenance (`fundamentals/README.md:3-9`). |

**Corrections (undercounted or unlisted costs):**

1. **A third in-chapter prose site states the order.** §2.5 opens: "The preceding sections
   introduce the prediction targets, the representations, multitask learning, and the evaluation
   protocol one at a time" (`2_fundamentals.tex:1409-1410`). The enumeration follows the current
   order. It does not become false in the way `:27` does (a list is not a sequencing claim), but
   leaving it unreordered after the inversion would be exactly the kind of stale mirror the
   writing law's clarity rule exists to catch. One-line rewrite; the cost table says "two
   rewrites" and it should say three.

2. **One site outside the chapter mirrors the order.** The introduction's organization bullet:
   "Chapter~\ref{ch:fundamentals} defines the shared background: POI prediction tasks, mobility
   representations, multitask learning, datasets, metrics, and evaluation protocols"
   (`src/chapters/1_introduction.tex:258-260`). Same class as correction 1: stale ordering, not
   falsehood; one-line touch in a file the cost table says is untouched ("Nothing outside the
   chapter points at either" is true for \ref targets but not for prose order).

3. **"Two whole sections trade places" understates the move: content must migrate between
   sections.** The notation prose (sets $\mathcal{U},\mathcal{P},\mathcal{C},\mathcal{R}$,
   `2_fundamentals.tex:68-70`) and Definitions 2.1/2.2 (check-in `:71-78`, history `:80-86`)
   live in §2.1 today, and §2.2's definitions consume them: the place embedding needs
   $p \in \mathcal{P}$ and the check-in-level representation needs $x_i$ (`:435`, `:461-463`).
   Under the inversion these must move into the leading representations section (or into a
   pre-section notation block), which is what the author's own proposal implies ("fazermos a
   definicao formal em representacao"). The swap is a restructure with migration, not a
   transposition of two blocks. `DEFINITIONS.md` §11 already concludes the eight-step plan "must
   be redone BEFORE any edit" (pinned by probe `R12-planvoid`, `check_audit_claims.py:625-629`),
   so this correction sharpens the record rather than contradicting it; but the redone plan will
   be larger than the current one, not a reindexing of it.

4. **The task-vocabulary sites inside §2.2 are an unlisted rewrite class.** The seven sites in
   §2b item 2 above would, after the inversion, use task terms before the task definitions. Each
   needs either an informal anchor in the rewritten chapter opening or a local rewording. Small
   per-site cost, but it belongs in the plan, and no document lists it.

5. **`src_clean/chapters/2_fundamentals.tex` also carries the old order** (its lines 7 and 19 are
   the origin of the two order-stating sentences). It is the author's superseded provenance tree,
   not a build input, so this is a note in the same class as the `fundamentals/` directory names.

---

## 4. What else breaks that nobody has listed

1. **The 2.1-to-2.2 bridge inverts its rhetoric.** "This per-visit view motivates the
   representation discussed in Section~\ref{sec:fund:repr}" (`2_fundamentals.tex:194-197`) is a
   forward motivation today. After the inversion the \ref still resolves, but the sentence
   becomes a backward recall wearing a forward-pointing verb; the CTLE strand and the
   "end targets" subsection (`:192-206`) need a rewritten seam, and a NEW bridge must be written
   at the end of the (now first) representations section into the tasks section. The three-\ref
   count captures none of this because the breakage is rhetorical, not referential.

2. **§2.5's synthesis order becomes a decision.** "The argument begins with the targets"
   (`:1425`) currently matches the chapter's physical order. After the inversion the synthesis
   would begin where the chapter no longer begins. Nothing is false; but whether §2.5 re-argues
   in the new order or deliberately keeps targets-first (the invariant-first mirror of §2b item 4)
   is an authorial choice the redone plan must surface, not silently decide.

3. **Pending trackers are keyed to the current section numbering.** These are open items that
   would point at the wrong sections after a swap (§2.1 and §2.2 exchange numbers; 2.3-2.5 keep
   theirs):
   - The author's own feedback list, `src_utils/PENDENCIAS.md` §4 items 16, 17 (§2.1.1.1),
     18, 19, 20 (§2.2.2), 21 (§2.2.3.1), 22 (§2.2.3.2) (`PENDENCIAS.md:1643-1662`). These are
     unapplied edits to the exact subsections being swapped. Applying them before the inversion,
     or re-anchoring them after it, is a sequencing decision; doing neither guarantees a future
     agent edits the wrong section.
   - `src_utils/_history/NEEDS_SIGN_OFF.md` item 7, "na secao 2.1" (`NEEDS_SIGN_OFF.md:169-171`), among
     the 56 open markers (count verified: 56 `###` headings).
   - `NORTH_STAR.md:203-208` pins a not-yet-drafted paragraph to "Section 2.2, next to the
     place-level-to-check-in-level move". Content-anchored as well as number-anchored, so it
     survives with a number edit, but it is a live pointer the inversion must update.
   - `storyline/README.md:21` maps `02_tasks_and_scope/` to "Ch.2 §2.1".
4. **The design document itself.** `DEFINITIONS.md` §1 "Where the definitions physically sit"
   (`:127-137`) places D1-D9 in Section 2.1 and prescribes that Section 2.2 "RECALLS Definitions
   D3/D4 by \ref"; §5's restated definitions carry the same assumption. Under the inversion the
   design's placement layer is void along with the plan. §11 says the plan must be redone; it
   should be recorded that the placement sections of the design document are part of what gets
   redone, or a future pass will apply §1 as written.
5. **Checked and NOT broken, for the record:** §2.3's opening consumes both tasks and
   representations ("static category classification from a place representation with
   next-category prediction from a check-in history", `:649-651`) and follows both sections in
   either order. §2.4 references the tasks and metrics only. The in-chapter forward refs at
   `:852` and `:1485` target `sec:fund:eval` and are order-neutral. No probe pins any
   order-dependent string (§3 above). The GLOSSARY carries no section-number reference to 2.1 or
   2.2. Nothing in `src/chapters/3_cbic/`, `4_courb/`, `5_mobiwac/`, or the appendices references
   either label.

---

## 5. Recommendation

**Recommendation (this is a recommendation; the author decides, and nothing is authorized):
INVERT, WITH CONDITIONS. If the conditions are unacceptable, the fallback is the already-validated
option (a), not a partial inversion.**

Reasoning, in the order it decided:

1. **The historical objection dissolves.** The strongest possible reason to keep the order would
   have been an original, recorded rationale. Section 1 shows there is none: the order was
   inherited as a specification, and the only prose defending it postdates the chapter and traces
   to the author's own 2026-08-02 pass. The inversion violates no recorded design intent.
2. **The dependency argument genuinely favors it.** Representations-first is the topological
   order of the chapter's own symbol graph; the alternative fix (option (a), the AD-4
   subsubsection) achieves acyclicity by placing representation definitions inside the tasks
   section, an arrangement the author himself finds less natural, and which the design document
   already concedes is the weaker argument (`DEFINITIONS.md:613`, "His argument is better than
   the design's").
3. **The narrative loss is real but boundable.** Everything the reader loses (§2b) is repairable
   with prose that must be rewritten anyway: the chapter opening can name the two targets
   informally in two sentences before §2.2 uses them, and the migration of the notation and
   check-in definitions into the representations section is coherent (representations of WHAT is
   answered by defining the check-in first). The one unrepairable trade is the divergence from
   the papers' problem-first shape (§2b item 3) and the choice between the two thesis mirrors
   (§2b item 4); both are authorial judgments, and the author's proposal indicates his judgment
   already leans to the answer-mirror.
4. **The measured costs are small and now fully enumerated.** Three refs, three in-chapter
   rewrites plus one introduction line, the content migration of §3 correction 3, the seam
   rewrites of §4 item 1, the tracker re-anchoring of §4 item 3, and the NORTH_STAR map edit.
   Zero gates. Nothing outside the chapter breaks referentially.

**The conditions:**

- **C1.** The eight-step plan is redone from scratch before any edit
  (`_history/_round12/49_definitions_validation_and_plan.md` is void under the inversion, as its own
  record states), and the redone plan includes: the notation + D1/D2 migration (§3 correction 3),
  the task-vocabulary anchors (§3 correction 4), the two seam rewrites (§4 item 1), and the
  §2.5 enumerations (§3 correction 1, §4 item 2).
- **C2.** The author himself edits `NORTH_STAR.md:73-80` (the chapter map is his; the project
  scope forbids agents to restructure it) and rules on the §2.5 synthesis order (§4 item 2).
- **C3.** The pending items keyed to current numbering (§4 item 3, especially his own feedback
  items 16-22) are either applied before the inversion or re-anchored in the same commit, so no
  tracker points at the wrong section afterward.
- **C4.** The four probe-pinned strings of the definitions design (D4's sentence, D9's equation
  and exclusion, `def:fund:checkinlevel`) are carried verbatim through the move, and
  `src_utils/check.sh` runs after application, exactly as `DEFINITIONS.md` §7 already requires.
- **C5.** AD-4's subsubsection is dropped, not created, consistent with the author's own
  condition recorded on it (probe `R12-ad4cond`).

**Why not KEEP:** keeping is defensible purely on cost, but the costs are now measured and small,
the historical record offers no rationale to defend, and the design document itself concedes the
author's ordering argument beats the plan's. Keeping would preserve a structure whose only written
justification was added last week as a description of the status quo.

**Why not unconditional INVERT:** the author's own caution is the condition set. The narrative
repairs (C1) and the map edit (C2) are exactly where "a narrativa tem que estar acima desse
problema" bites, and they are his calls, not an agent's.

---

## Source ledger

| claim | source, read this session |
|---|---|
| proposal + caution verbatim | `fundamentals/DEFINITIONS.md:607-611` (15:06 copy) |
| no ordering rationale in `fundamentals/` | full read of the folder's documents, §1 above |
| order inherited as spec | `fundamentals/COVERAGE_EVALUATION.md:8-12`; `NORTH_STAR.md:73-80`, `:369-375` |
| :27 sentence provenance | `git log -S`: absent from `fundamentals/2.1_.../2.1_poi_prediction_tasks.tex:8` and from `807183c1~1`; present from `0bbe3caa` (`src_clean/chapters/2_fundamentals.tex:19`), merged in `807183c1` |
| July rejection of inversion | `fundamentals/DEFINITIONS.md:149-153` |
| dependency graph | `fundamentals/DEFINITIONS.md:101-125` |
| task-vocabulary sites in §2.2 | `src/chapters/2_fundamentals.tex:253, 272, 292, 300, 484, 563-570`; `src/tables/frame/lineage.tex:34` |
| limitation sentence | `src/chapters/2_fundamentals.tex:439-441` |
| MobiWac problem-first | `src/chapters/5_mobiwac/03_problem.tex:12` |
| three refs / two labels | grep over `src/**/*.tex`, hits at `2_fundamentals.tex:15, 17, 25, 197, 210` only |
| zero gates | grep over `src_utils/check_*.py`, `check.sh`; probe list at `check_audit_claims.py:469, 485, 617-629` |
| tracker staleness | `src_utils/PENDENCIAS.md:1643-1662`; `src_utils/_history/NEEDS_SIGN_OFF.md:169-171`; `NORTH_STAR.md:203-208`; `storyline/README.md:21` |
| study authorization scope | `src_utils/PENDENCIAS.md:1356-1360` (§6.20 item 1) |

## [VERIFY] flags

1. **[CORRECTED BY THE PARENT, 2026-08-03.]** The study wrote that "git history begins 2026-07-23", and that
   is **false about the repository**: `git rev-list --max-parents=0` gives a root of **2025-03-08**, and there
   are **2,049 commits, 1,666 of them before 2026-07-23**. **The conclusion survives, for a different and
   stronger reason than the one given.** Of those 1,666 earlier commits, exactly **one** touches
   `articles/dissertacao/` at all: `bb4449c8` (2026-07-20), which adds a `.gitignore` and nothing else. The
   chapter-map line "2.1 POI prediction tasks" first enters the tree in `bb64e220`. So there is no earlier
   dissertation history in which a tasks-first rationale could hide, and the finding stands. It stands on a
   measurement of what the early commits CONTAIN rather than on a wrong claim about when history starts.
   `[VERIFY: whether any planning artifact OUTSIDE this repository argued the order; nothing on disk does.]`
2. [VERIFY: whether the author personally composed the `:27` and `:14-20` sentences inside his
   `src_clean` pass or approved an assistant's wording; commit `0bbe3caa` attributes the tree to
   his pass but does not distinguish keystrokes.]
3. [VERIFY: the 56 NEEDS_SIGN_OFF markers were counted (`###` headings = 56) but not individually
   re-audited for openness this session; only item 7's section-number anchoring was read.]

## UNFINISHED

Nothing in the assigned scope is unfinished. Not attempted, by scope: no redone edit plan for the
inversion (that work is gated behind the author's decision and would be a new round-12 document),
and no re-audit of the 56 NEEDS_SIGN_OFF markers beyond the one that names a section number.
