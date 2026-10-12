# Storyline — the settled narrative content of the frame chapters

> **2026-09-30:** os rascunhos `.tex` desta pasta sairam da arvore -- eram uma copia superada do texto entregue, com numeros de outra geracao. Os ledgers de citacao (`*_citations.md`) ficam. Tudo recuperavel na tag `dissertacao-pre-organizacao` do PoiMtlNet.

> **⏸ FROZEN 2026-07-24 — IMPORTED into `../../../../src`.** The frame chapters drafted here
> (`drafts/1_introduction.tex`, `drafts/6_conclusion.tex`) were imported into the assembled v1 at
> `../src/chapters/{1_introduction,6_conclusion}.tex` (Phase 3). **`../../../../src` is now the single
> working copy** (single-source rule, CLAUDE.md §1). Do NOT edit the drafts here to change the
> dissertation text — edit `src/chapters/` and rebuild. This folder is kept as the provenance
> record of how the frame narrative was settled; `1_citations.md` / `6_citations.md` remain the
> citation ledgers for those chapters.

Restructured 2026-07-23 (author request): this folder now mirrors the `fundamentals/` pattern —
**one folder per content topic, holding the settled information the text renders**, not the
process that produced it. The process (reviews, iterations, sign-off rounds) is preserved under
`archive` and `audit`.

## Content folders (what the frame chapters say, with licenses)

| Folder | Topic | Rendered in |
|---|---|---|
| `01_motivation_and_stakes` | stakes, 93% regularity, beyond-mobility breadth, the engineering wish | Ch.1 §1.1–1.2 |
| `02_tasks_and_scope` | the four tasks, the pair evolution, the task-choice defense, empirical scope | Ch.1 §1.1/§1.4; Ch.2 §2.1 |
| `03_question_and_arc` | the research question, the three-beat arc with licensed wording, the title | Ch.1 §1.3 |
| `04_organization_and_authorship` | coletânea declaration, verified venues, authorship transparency, standing devices | Ch.1 §1.5 |
| `05_contributions` | the four-group taxonomy with each item's license | Ch.1 §1.6; Ch.6 §6.1 |
| `06_answer_and_mechanism` | the consolidated answer, the three-link mechanism chain, the gradient picture | Ch.6 §6.2 |
| `07_limitations_and_future_work` | six limitations 1:1 with future work, the confound concession | Ch.6 §6.3–6.4 |

## drafts/ — the texts themselves

- `1_introduction.tex` + `1_citations.md` — Chapter 1, draft 2 (post four-persona review,
  post author's three points, venues verified). The `.tex` header carries the title decision
  block for the advisor.
- `6_conclusion.tex` + `6_citations.md` — Chapter 6, draft 1 (all signed-off beats;
  California partial marked; capacity-baseline prominence = author decision).
- The citation ledgers are the AUDIT TRAIL: every cite/number → source → verification record →
  revision history. Start there to audit how the final texts were reached.

## audit/ — the binding decisions and reviews

- `AVAL_NECESSARIA_ptBR.md`, `_2`, `_3` — the three author sign-off rounds (11 + 4 + 3 items),
  with the author's inline decisions. These LICENSE the frame's connective claims.
- `ch1_beat_budget.md` — the placement contract (approved D3): every move, one home;
  Ch.1 narrates, prefaces/recaps/Ch.6 litigate.
- `ch1_review.md` — the four-persona review of Ch.1 draft 1 (all findings + what was fixed).
- `capacity_baseline_experiment.md` — the D1 experiment: design and licensing contract
  (written BEFORE any run), parameter audit, Alabama n=20 verdict, California status,
  the mechanism read.

## archive/process/ — the full working record (kept, not curated)

The seven-lens narrative review (01–07), the second-pass audits (08–09), the specialist and
full-arc re-review waves (10–11), and the superseded PANORAMA/README. Nothing here is a source
of truth; when a process file and a content folder disagree, the content folder (and the
ledgers in `drafts`) win.

---

> **Consolidado em 2026-08-28.** As sete seccoes abaixo estavam em sete pastas com um
> ficheiro cada. O conteudo esta VERBATIM; so os cabecalhos `##` sao novos. O caminho antigo
> de cada uma esta no seu cabecalho.


---

## `01_motivation_and_stakes/motivation_and_stakes.md`

# Motivation and stakes — the settled content

> What the frame chapters SAY about why this work matters, with each claim's license.
> Rendered in: Ch.1 §1.1 (`drafts/1_introduction.tex`). Process trail: `archive/process/09`.

## The stakes (Ch.1 opening funnel)

1. **The data**: check-ins from location-based social networks; "at large scale" (NO quantity —
   "billions" was removed as unledgered; do not reintroduce a number without an opened source).
2. **The regularity**: potential predictability of an individual's next location "about
   93 percent" — `song2010limits` (Science 327:1018, opened firsthand). Always "potential
   predictability" (upper bound), never achieved accuracy.
3. **What a service does with the two predictions**: recommender ranks candidates of the right
   type (category); navigation/transit prepares for where the user heads (region); platform
   allocates attention and resources by area.

## Beyond-mobility breadth (author-approved Item 11; all anchors verified by opened abstracts)

- Human mobility informs urban planning, disease spreading, pollution analysis →
  `luca2021mobilitysurvey` (abstract lists exactly these).
- Place categories = the semantic characterization location-based services rely on → `Xu2023`
  (abstract: categories "serve as excellent semantic characterization of the venues").
  NOT "urban planning" — that framing was CBIC's, not Xu's.
- Encoder provenance: "part of the representation machinery ... the spatial location encoders of
  the second study, was first validated on geospatial tasks such as species recognition and
  remote sensing classification" → `mai2023sphere2vec` + `wu2024torchspatial`. Scoped to the
  CoUrb encoders only — never "the representation machinery" unqualified.
- MTL breadth: vision (`kokkinos2016ubernet`), clinical multilabel diagnosis
  (`lipton2015learning`), instruction-tuned language models (`wei2022finetuned` = FLAN — the
  wording must say instruction tuning across tasks, not classic NLP MTL).

## The engineering wish (the tension beat)

Operational simplicity ONLY: one artifact to train, version, deploy; one forward pass, both
answers. **Never "lower cost"** (F3 guard: the joint model is larger and cost more to train —
disclosed, not hidden). The threat: negative transfer. The open question at research start:
does joint training help this pair, and what does the answer depend on.

## Sources of truth

Citation ledger with verification records: `drafts/1_citations.md`. Verified breadth analysis:
`archive/process/09_application_scope_breadth/`.

---

## `02_tasks_and_scope/tasks_and_scope.md`

# Tasks and scope — the settled content

> What the frame chapters SAY about the prediction tasks and the empirical scope.
> Rendered in: Ch.1 §1.1 (definitions + fourth task) and §1.4 (scope). Full treatment: Ch.2 §2.1.
> Process trail: `archive/process/02_task_choice_endorsement/` (the task-pair analysis).

## The four tasks (canonical names, GLOSSARY)

| Task | Definition | Role in this dissertation |
|---|---|---|
| next category | category of the next visited place (7 top-level classes) | end target, all three studies |
| next region | official geographic unit of the next visit (census tract / mahalle; 520–8,501 classes) | end target, Chapter 5 |
| next place | the exact establishment | NOT predicted anywhere; said once, early |
| category classification | static classification of a place's category | tasks 1–2's partner in Chapters 3–4; replaced in Chapter 5 |

## The task-pair evolution (author-approved Item 1 — named plainly, never hidden)

CBIC/CoUrb pair = category classification + next category (static + sequential).
MobiWac pair = next category + next region (both sequential).
The pair changed BECAUSE the representation changed: under a per-visit vector the static task
becomes "a less natural fit than the sequential tasks" (approved corollary form — never
"incoherent"; pooling visit vectors into a place vector remains possible).

## The task-choice defense (three legs, approved forms)

1. **Utility**: what a mobility-aware service can act on (category = intent, region = where to
   prepare).
2. **Standing**: "both are established end targets in the literature on the way to the harder
   next-place problem" — the FALLBACK form. The comparative form ("more present in the
   literature") stays out until an opened anchor supports it (N1 leg 2, still gated).
3. **Not easier**: the class-count fact (region alone spans hundreds to several thousand
   classes) lives in the task DEFINITION, not as a defensive tail (cold-reader fix: Ch.1
   narrates; §2.1 and the Ch.5 recap litigate difficulty).

## Empirical scope (Ch.1 §1.4)

- Data: Gowalla, five U.S. states (Alabama, Arizona, Florida, California, Texas), 2009–2010
  vintage + Istanbul (Massive-STEPS). "Two sources", not "all experiments use both".
- Targets: 7-class taxonomy (Community/Entertainment/Food/Nightlife/Outdoors/Shopping/Travel);
  regions = census tracts (US) / mahalles (Istanbul).
- Single-model constraint: one artifact, one forward pass, both predictions (design-time
  assumption, distinct from Ch.6 limitations).

---

## `03_question_and_arc/question_and_arc.md`

# Research question and the arc — the settled content

> The one question and the three-beat arc as the frame tells them.
> Rendered in: Ch.1 §1.3 (`drafts/1_introduction.tex`), closed by Ch.6 §6.2.
> Process trail: `archive/process/01_arc_and_logline/`, `11_full_arc_rereview/`.

## The research question (verbatim spine)

**Does multi-task learning help point-of-interest prediction — next category and next region —
and what does the answer depend on?**

## The arc, beat by beat (with the licensed wording)

1. **CBIC (Ch.3, setup)** — MTLnet: place-level graph embedding + hard sharing beneath the two
   task heads; tasks = category classification + next category. "Did not consistently
   outperform" the dedicated models ("beat" is banned) and "cost more to train". Reported as a
   finding with THREE candidate explanations (task dissimilarity / representation too poor /
   restrictiveness of hard sharing). Time-indexed: "held for the configuration of its time".
   NEVER: "CBIC called for better representations" (its future work proposed the architecture
   door). Approved form: the null was hypothesized and the results "lend weight to" it.
2. **CoUrb (Ch.4, diagnosis)** — tested the representation explanation FIRST "as the cheapest
   controlled test among the three" (no door metaphor in prose). Architecture fixed, input
   replaced (64-d monolithic DGI → decomposed spatial+temporal+categorical). Category macro-F1
   +20.2 to +22.0 pp (AUDITED values — the paper's published 16/21 was recounted to 15/21+1 tie;
   use audited numbers + errata note). Diagnosis time-indexed: "at that stage of the research".
   Boundary (approved Item 6): CoUrb's only baseline is MTLnet — it does not revisit
   MTL-vs-single-task; Chapter 5 reopens that question.
3. **MobiWac (Ch.5, resolution)** — the mechanism-as-hypothesis sentence: any place-level
   embedding gives a place the same vector on every visit; "cannot tell a weekday lunch from a
   Saturday night out". Check-in level = one vector per visit. TWO changes, both named, always:
   representation AND sharing topology (cross-attention between two task-specific streams,
   acting on another of CBIC's candidate explanations). The pair settles on next category +
   next region. Payoff with bound verbs: category outperforms at all six datasets (five U.S.
   states + Istanbul — count precedes the claim); region outperforms at four of six, TOST
   non-inferior (±2 pp) at Alabama and Arizona. Status: submitted, under review.

## The two-factor law (F1)

Every payoff summary names BOTH factors — the check-in-level representation AND the redesigned
sharing topology. Never representation alone.

## Working title (D2, advisor decides)

"Multi-Task Learning for Point-of-Interest Classification and Prediction Tasks: The Role of the Check-in-Level Representation" — with three alternates in the `drafts/1_introduction.tex`
header comment block.

---

## `04_organization_and_authorship/organization_and_authorship.md`

# Organization and authorship — the settled content

> The coletânea declaration, chapter map, venue records, and authorship transparency.
> Rendered in: Ch.1 §1.5. Placement law: `audit/ch1_beat_budget.md` (Ch.1 narrates;
> prefaces/recaps/Ch.6 litigate).

## The coletânea declaration (the "magic sentence" pattern, Viegas precedent)

The dissertation is a collection of three studies presented in the order they happened
(negative result → diagnosis → resolution), each chapter an independent article re-typeset in a
unified format, faithful to "the published text of each article, or, in the case of the article
under review, to the submitted manuscript" (NOT "version of record" — MobiWac has none yet);
post-publication corrections live in the errata appendix, never silently edited.

## Venues (VERIFIED against official records, 2026-07-23 — see drafts/1_citations.md)

| Ch. | Venue (full, verified) | Status | Authorship |
|---|---|---|---|
| 3 | XVII Congresso Brasileiro de Inteligência Computacional (CBIC 2025), DOI 10.21528/CBIC2025-1191324 | published (EN) | Vitor 1st |
| 4 | X Workshop de Computação Urbana (CoUrb 2026), with SBRC 2026, DOI 10.5753/courb.2026.22960 | published (PT; chapter = EN translation) | Tarik S. Paiva 1st; Vitor 2nd, contributed the MTLnet baseline, presented at the event |
| 5 | 23rd ACM International Symposium on Mobility Management and Wireless Access (MobiWac 2026) | **submitted, under review** — update on decision | Vitor 1st |

## Standing devices (every chapter)

- **Time-capsule preface**: one italic paragraph per article chapter — venue, status, what later
  chapters revise.
- **Recap subsections**: Ch.4 recaps "The MTLnet framework"; Ch.5 recaps both prior artifacts
  by name (Viegas pattern; NO bridge table — Item 10 resolution).
- **Status wording**: MobiWac is always "submitted, under review" — in §1.2, §1.5, and Ch.5's
  preface; never "accepted/published".

## Objectives ↔ chapters (1:1, Ch.1 §1.4)

1. Naive hard-sharing joint model vs dedicated, on the two category tasks → Ch.3.
2. Representation diagnosis, architecture held fixed → Ch.4.
3. Check-in-level representation + joint model for the final pair → Ch.5.
4. Leakage-guarded protocol (user-disjoint CV + paired significance + non-inferiority) is
   CH.5'S protocol; Ch.6 consolidates under it. NEVER imply Ch.3–4 used it (Ch.4 verified
   sample-stratified — see `audit/` UW-3 record in archive/process/08).

---

## `05_contributions/contributions.md`

# Contributions — the settled content

> The four-group taxonomy as rendered in Ch.1 §1.6, with each item's license.
> Closed in Ch.6 §6.1 (per-chapter contribution paragraphs).

| Group | The claim (licensed form) | License / guard |
|---|---|---|
| Theoretical | The input representation, together with the sharing topology built on it, dominates whether MTL helps these POI prediction tasks; a null under place-level coexists with a positive under check-in-level | two-factor law F1: BOTH factors, always |
| Software | MTLnet (Ch.3); the check-in-level representation + joint model (Ch.5); "the reproducible training and evaluation pipelines behind the experiments of Chapters 3 and 5" | scoped to Ch.3+5 — NOT "every number in this document" (Ch.4's pipeline is Tarik's repo) |
| Empirical | Six-dataset benchmark, joint vs dedicated, next category + next region, user-disjoint CV, n=20 (4 seeds × 5 folds), paired tests, non-inferiority margins, leakage audit | protocol belongs to Ch.5 |
| Practical | One deployable model serving both services, "outperforming the dedicated models on the category task and outperforming or remaining non-inferior to them on the region task", single artifact + single forward pass | verbs bound to tests — "matches or exceeds" was rejected by review; never upgrade AL/AZ |

## Products list (excellence reviewer, pending author placement decision)

2 published DOIs + 1 under-review manuscript + code repositories + the evaluation protocol.
Where the committee finds it: short appendix or per-chapter footnotes — OPEN, author decides.

---

## `06_answer_and_mechanism/answer_and_mechanism.md`

# The consolidated answer and the mechanism — the settled content

> The dissertation's answer to its question, and WHY the joint model wins, with every claim's
> evidence chain. Rendered in: Ch.6 §6.2 (`drafts/6_conclusion.tex`).
> Experiment record: `audit/capacity_baseline_experiment.md` (design + licensing contract +
> results). Number ledger: `drafts/6_citations.md`.

## The answer (conditional — the condition IS the finding)

- Place-level embedding + naive hard sharing → **no** (Ch.3, for that configuration).
- Check-in-level representation + sharing topology built for it → **yes** (Ch.5): category
  outperforms everywhere; region outperforms at 4/6, TOST non-inferior (±2 pp) at AL/AZ.
- What the answer depends on: the representation, together with the sharing topology built
  on it (two factors, always).

## The mechanism chain (three links, each with its evidence and license)

1. **Not task-teaching**: freeze control (MobiWac §6, IN-PAPER, citable from Ch.5) — region
   pathway frozen, category gain survives, at the three datasets where the control ran
   (AL/AZ/FL). "A stronger shared trunk, not the region task teaching the category one."
2. **Not parameter count**: capacity-matched dedicated baseline (POST-SUBMISSION frame
   analysis — never a Ch.5 result; the prose must say when it was run).
   - Alabama, FINAL (n=20, 3 recipes): wide dedicated (h=672, ~4.2M params = joint budget)
     best arm 56.16 ±1.88 vs narrow dedicated optimum 56.82 ±0.03 vs joint 64.54.
   - California, PARTIAL at draft time (n=15, first arm): 68.35 ±0.53 vs ceiling 70.60 vs
     joint 77.05 — same direction. REPLACE with final verdict when job 4cff4b00 completes.
   - Param audit reproduces the paper quote: AL 4,197,621 vs 1,061,476 combined (3.95×);
     CA 5,151,189 vs 2,015,044 (2.56×).
3. **What remains — the shared trunk**: cross-attention stack trained on both tasks' signals
   builds a representation the dedicated model cannot reach at any width tried; width without
   the second task's signal has no new information to spend parameters on.

## The gradient picture (N3 beat — the FULL scope travels with the number, verbatim)

Cosine similarity between the two tasks' gradients averaged **+0.001**, over **four seeds on
three of the six datasets**, measured **during development on an earlier preparation of the
data**, **directional conflict only**, **a finding for this pair of tasks, not a general rule**.
Reading: "sharing stopped hurting" — NEVER "the tasks teach each other". Explains why gradient
balancers had little to correct in this configuration.

## Banned vocabulary in this section

"knowledge gate" (author shorthand — translates to the paper's sharing-by-exchange wording);
any parameter-count credit for the win (it is disclosed as COST); "lower cost"; upgrades of
AL/AZ region results.

---

## `07_limitations_and_future_work/limitations_and_future_work.md`

# Limitations and future work — the settled content

> Six limitations, each tied 1:1 to a future-work item. Rendered in: Ch.6 §6.3–6.4
> (`drafts/6_conclusion.tex`).

| # | Limitation | Future-work item (1:1) |
|---|---|---|
| 1 | Gowalla vintage (2009–2010) | newer and denser traces |
| 2 | 7-class taxonomy coarseness | finer-grained taxonomies |
| 3 | Transductive representation (no unseen places/users without retraining) | inductive variant of the check-in-level representation |
| 4 | No next-place task | add exact next place as third target; cascade lineage (Ch.5 §2.3) suggests category/region as structure, not competition |
| 5 | Single non-U.S. city (Istanbul) | more cities outside the U.S. |
| 6 | **Task-pair confound** (signed-off concession): the pair changed together with representation+topology; no single ablation separates them; Ch.4 is the fixed-pair control for the DIAGNOSIS, not the joint win; capacity baseline closes the parameter-count explanation; pair homogeneity remains a possible contributor to the SIZE of the win | **fixed-pair ablation**: Ch.5 joint model on the Ch.3 task pair under the check-in representation |

## Guards

- The concession (item 6) is signed-off text (storyline archive/process/02 §3.4 → AVAL round 1
  Item 4); its prominence is fixed by the D1 licensing contract — the capacity-baseline
  paragraph in §6.2 may shrink to a sentence but not disappear.
- Final remarks close the honest arc: "the negative result ... worked through, it was the
  contribution's first half." No new claims may enter the final remarks.
- Every limitation is CONCRETE (a banca can test it); never pad with generic limitations
  ("more data would help") that have no paired future-work item.
