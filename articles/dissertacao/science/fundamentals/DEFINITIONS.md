# DEFINITIONS.md — the twelve definitions of Chapter 2, consolidated and validated

> **STATUS: a design document, not chapter text. Nothing here is applied to `../../../../src`.**
> The single working copy of the chapter is `../../src/chapters/2_fundamentals.tex` (single-source rule,
> `../../../../CLAUDE.md` §1), and this folder is frozen as the provenance record of how Chapter 2 was built. This
> file belongs to that record: it is the design the application pass will work from. **Six of the seven
> gating decisions are settled** (AD-1 thirteen definitions, AD-3 both of Chapter 5's streams named, AD-4
> conditionally, AD-5 both registry rows, AD-6 sharpen the D2 sentence, AD-7 rename D13's task indices).
> **AD-2 is OPEN.** I reported it answered on 2026-08-03 and RETRACTED that the same day: the answer rested
> on an unverified identification of two different files, and closing it needs one artifact from the
> published run. §10 carries every ruling with its evidence, the AD-2 row carries the retraction, and
> `src_utils/PENDENCIAS.md` §6.13 through §6.21 carry the record.
>
> **AND ONE ITEM LARGER THAN ANY OF THE SIX IS UNDECIDED: inverting §2.1 and §2.2.** He proposed it in
> answer to AD-4 — representations first, then the tasks trainable on them — and it is a better fix
> for the forward dependency than the design's, because nothing has to move. It is also a
> CHAPTER-STRUCTURE change that edits the fixed chapter map (`NORTH_STAR.md:73-80`), so it needs a
> decision stated as such. **The eight-step edit plan was written for the OTHER shape and does not
> survive the inversion; it must be redone BEFORE any edit, not after.** He asked to apply only once
> the definitions close: "depois dessas definicoes podemos aplicado". Nothing is authorized yet. Do not edit the chapter from this file; approve the decisions, then the edit plan in
> `../src_utils/_history/_round12/49_definitions_validation_and_plan.md` applies it.

## Why this document exists

The author read the twelve numbered definitions and found four problems:

> "In Definition 2.7, shouldn't the place embedding be denoted as $e_{p_i}$ for a given place $p_i$? The
> second, and more critical, issue is a dependency conflict: Definition 2.2 depends on Definition 2.8.
> Currently, Definition 2.2 defines the history in terms of raw check-ins, whereas our model consumes the
> check-in embedding history. Similarly, Definition 2.3 relies on Definition 2.7, which is only defined
> later in the text. Furthermore, Definition 2.6 should consume a history of $e_{p_i}$, as specified
> elsewhere in the text."

All four were measured against the live source before anything was designed
(`../src_utils/_history/_round12/46_definition_dependency_audit.md`), the layering question was settled against
four literature sources opened in session (`../src_utils/_history/_round12/48_history_formulation_literature.md`),
and the design below was then put through an adversarial validation pass by a second agent
(`../src_utils/_history/_round12/49_definitions_validation_and_plan.md`).

## What the validation changed, and why this copy is the one to read

The validation pass rebuilt the dependency graph independently, enumerated all 21 gate probes that target
the chapter against the PROPOSED text, and found **five defects, all of wording and none structural.**
Every one was then re-verified in the live source before being corrected here. This file carries those
corrections inline; the original draft is preserved unedited at
`../src_utils/_history/_round12/47_definitions_consolidated.md`.

| id | what was wrong | the evidence that settled it |
|---|---|---|
| **F-1** | The draft stated Chapter 5's instantiation as $\rho(x_i)=\mathbf{e}_{x_i}$ alone. The joint model reads **two** elementwise streams. | `5_mobiwac/04_method.tex:27`: "the region task reads the same window of visits, each visit now represented by the trained vector of its region node". Applied verbatim, Chapter 2 would have misstated the input of the study the whole arc resolves on. |
| **F-2** | "Every predictive model in this dissertation reads $\rho(H_i)$" is false of the static task. | `2_fundamentals.tex:116-124`: $g_{\mathrm{cat}}(\mathbf{e}_p)\longrightarrow c_p$, with no history in it. That is the task `apx_b_static_scope.tex` exists to keep separate. |
| **F-3** | "the three studies hold the tasks fixed" — the studied task PAIR changes at Chapter 5. | `2_fundamentals.tex:140-142`. The accurate phrasing is "hold the task DEFINITIONS fixed". |
| **F-4** | The draft said the studies zero-pad short windows. | `5_mobiwac/05_setup.tex:28`: "we keep only the full-length window ending there and drop these padded duplicates". Chapter 5 drops rather than pads. |
| **F-5** | The proposed $d$ registry row implied the letter was unclaimed. | Measured live: `$d$` once, `d_{ij}` four times, `d_{\mathrm{shared}}` three times. No collision inside Chapter 2, but the row needs a chapter-local scope note. Contrast $\rho$: zero live occurrences, genuinely free. |

Two findings of the design pass are worth keeping in view because neither the author nor I had listed
them:

- **$c_p$ is a free symbol in Definition 2.3 today.** It occurs exactly once in the live prose, inside
  that definition's own equation, with no prior introduction, and `GLOSSARY.md` §1.1 already uses it in
  the $g_{\mathrm{cat}}$ row. The registry anticipated a binding the chapter never made.
- **The author's $e_{p_i}$ question is half right, and the half matters.** $\mathbf{e}_p$ stays in the
  static task, which is quantified over POIs with no check-in index in it; renaming there would make a
  static task look sequential. What a history POSITION carries is $\mathbf{e}_{p_j}$, the composition of
  $j \mapsto p_j$ with $p \mapsto \mathbf{e}_p$, and the design lifts that composition out of prose into
  an equation. His finding 4 then dissolves: $f_{\mathrm{place}}(H_i) \longrightarrow p_i$ is correct as
  written.

**Zero gate probes break.** All 21 probes targeting `chapters/2_fundamentals.tex` hold against the current
text (verified independently) and against the proposed text (verified by the validation pass, by
enumerating the parsed probe tuple). The three probe-pinned strings — `R12-eqxi`, `R12-fplace`,
`R12-fplace2` — are carried character-for-character below and must stay that way through application.

---

## 0. The verdict on the author's four findings, in one screen

| Finding | Verdict | Resolution here |
|---|---|---|
| 1. Definition 2.3 consumes $\mathbf{e}_p$, defined only in 2.7 | CONFIRMED (mechanically, audit §1; re-read at `2_fundamentals.tex:116-124` and `:434-437`) | Move the two representation definitions ahead of the tasks (§2 below). |
| 2. Definition 2.2 defines the history over raw tuples while the models consume representations | CONFIRMED as a gap, but the fix is NOT to redefine $H_i$. The literature (4 of 4, doc 48) and MobiWac's own problem statement keep the sequence over raw observations. The gap is the missing, named data-to-representation map. | Keep $H_i$ raw; introduce a representation map $\rho$ before the tasks, with the factorization "every model reads $\rho(H_i)$" stated once (§3). |
| 3. Should $\mathbf{e}_p$ be $\mathbf{e}_{p_i}$? | The audit's position is TESTED AND UPHELD: both forms are needed and not interchangeable. | $\mathbf{e}_p$ stays in the static task; a history position $j$ carries $\mathbf{e}_{p_j}$, and the composition is made explicit in a displayed equation, not prose (§4). |
| 4. Definition 2.6 consumes the wrong history | CONFIRMED as a consequence of finding 2, and it dissolves with it: with $H_i$ raw and the factorization stated, $f_{\mathrm{place}}(H_i) \longrightarrow p_i$ is exactly right as written. | No change to the statement of 2.6; the pinned strings survive verbatim (§7). |

One finding of my own, which the design must not paper over: **the second study's input is not purely
place-level.** CoUrb's Time2Vec component encodes "the temporal values of each check-in (hour of day and
day of week)" (`4_courb/methodology.tex:144-153`), so the ST-MTLNet input at a history position depends
on the check-in's timestamp, not only on its POI. The chapter's current prose says the second study
supplies context "while retaining a place-level input" (`2_fundamentals.tex:472-474`). The encoder-map
formulation below accommodates this exactly (it is one more instantiation of $\rho$); how the prose
names it is flagged in UNFINISHED.

---

## 1. The dependency graph, and why the proposed order is sound

Symbols and where they are introduced under the proposed design (sets $\mathcal{U}, \mathcal{P},
\mathcal{C}, \mathcal{R}$ and the per-POI attributes $c_p, r_p$ live in the notation prose immediately
before Definition 1, as the sets already do at `2_fundamentals.tex:68-70`):

| Edge (consumer $\to$ provider) | Symbol carried |
|---|---|
| D2 $\to$ D1 | $x_i$ |
| D3 $\to$ notation prose | $p \in \mathcal{P}$ |
| D4 $\to$ D1 | $x_i$ |
| D5 $\to$ D1, D2 | $x_i$, $H_i$ |
| D5 (instantiation remark) $\to$ D3, D4, D1 | $\mathbf{e}_p$, $\mathbf{e}_{x_i}$, $p_j$ |
| D6 $\to$ D3, notation prose | $\mathbf{e}_p$, $c_p$ |
| D7 $\to$ D2, D1 | $H_i$, $c_i$ |
| D8 $\to$ D2, D1 | $H_i$, $r_i$ |
| D9 $\to$ D2, D1 | $H_i$, $p_i$ |
| D10, D11 $\to$ (none; cite ruder2017mtloverview) | — |
| D12 $\to$ GLOSSARY term "dedicated single-task model" | — |
| D13 $\to$ D10 (the notion of shared parameters) | — |

Proposed order: D1 Check-in, D2 Check-in history, D3 Place embedding, D4 Check-in-level
representation, D5 Representation map (NEW, see §3 for the fallback that keeps the count at twelve),
D6 Category classification, D7 Next-category, D8 Next-region, D9 Next-place, D10 Hard sharing,
D11 Soft sharing, D12 Negative transfer, D13 Gradient conflict.

**Acyclicity and topological consistency.** Every edge above points from a higher number to a strictly
lower number or to the notation prose that precedes all definitions. A directed graph whose every edge
goes from a later node to an earlier node in a fixed linear order has no cycle, and the linear order is
by construction a topological order of it. Under the CURRENT order the single forward edge is
2.3 $\to$ 2.7 (audit finding 1); the proposed order removes it and introduces no new forward edge.

**Where the definitions physically sit.** D1-D9 all land in Section 2.1 (the existing
"Task boundaries and notation" subsection and its two subsubsections, `2_fundamentals.tex:39,:66,:111`);
D3-D5 form a new subsubsection between "Check-ins and histories" and "The three experimental tasks"
(working head: "Representations of a check-in" — the author names it). No new `\section` is created;
the chapter's five-section skeleton (tasks, representations, MTL, datasets, relevance) is untouched.
Section 2.2 keeps its entire narrative (one-hot to DGI to HGI to Check2HGI, the losses, the lineage
table) and now RECALLS Definitions D3/D4 by `\ref` at `2_fundamentals.tex:420-468` instead of stating
them there; the limitation paragraph (`:439-444`) and the CTLE contrast stay where they are, pointing
backward.

---

## 2. The ordering decision, and the alternatives rejected

**Chosen: move the two representation definitions (and the new map) ahead of the tasks.** The static
task genuinely consumes a representation — that is what the study does
(`3_cbic/method.tex:53`: "Each POI is represented by its 64-dimensional DGI embedding"; GLOSSARY §1:
"classify a POI's category from its representation") — so the representation must be defined first.
This is the minimal move that removes the one forward edge.

Rejected alternatives, with their costs:

1. **Move the tasks after the representations section.** Rejected: the chapter's stated design is
   targets first ("This section defines the prediction targets before reviewing the methods used for
   them", `2_fundamentals.tex:27-28`), Section 2.1 is titled by the tasks, and the whole related-work
   architecture of the chapter (next-place models at `:148`, category/region-as-targets at `:192`)
   hangs off the task definitions. Cost of the move: a chapter restructure to fix one edge.
2. **A promissory prose introduction of $\mathbf{e}_p$ in the notation block, full definition kept at
   its current line.** Rejected: it reproduces the current defect in a weaker form — the reader meets
   the symbol with an IOU, and the fail-closed registry style of this repository treats the definition
   as the introduction.
3. **Have the static task consume something other than a representation.** Rejected: it would falsify
   what all three studies do and contradict GLOSSARY §1.

---

## 3. The layering decision (finding 2): raw history plus a named representation map

**Chosen design.** $H_i$ stays a sequence of check-in tuples exactly as Definition 2.2 has it. A new,
named object — the representation map $\rho$ — is introduced BEFORE the tasks, together with its
elementwise extension to histories:

$$\rho(x_i) \in \mathbb{R}^{d}, \qquad \rho(H_i) = \bigl(\rho(x_{i-\ell}), \ldots, \rho(x_{i-1})\bigr).$$

Immediately after it, one remark states the factorization that resolves the author's finding: the task
is a property of the data, the model is not — every model of the sequential tasks reads
$\rho(H_i)$ rather than $H_i$ itself, and the three studies hold the task DEFINITIONS fixed while they vary
$\rho$. The instantiations, each verified against its chapter:

- Chapters 3 and 4 (place-level): position $j$ of the window carries a vector that is a function of
the visited POI. **Chapter 4's temporal component: the level is NOT established, and the earlier claim here was retracted
  on 2026-08-03.** This paragraph previously said the component is learned per check-in and then reduced to
  one row per POI by `drop_duplicates("placeid")`, so that the vector was a function of the POI and of one
  selected visit to it. **That rested on an unverified identification of two different files and is
  withdrawn**: the ETL reads `time_embedding.parquet` (`create_inputs_hgi.py:415`), nothing in that
  repository writes that parquet, and no CSV-to-parquet conversion exists, so it may already be POI-level,
  in which case the dedup is a no-op. Full boundary in
  `../src_utils/_history/_round12/50_courb_temporal_level_investigation.md`.

  **What IS established:** the temporal encoder emits one row per check-in (`Time_Encoder.ipynb` cell 13,
  stored output `(2535573, 64)` against 2{,}535{,}573 check-ins), and the category-task path dedups by
  `placeid` (`PoiMtlNet_Novo/src/etl/create_inputs_hgi.py:437`). **What is NOT:** whether the table that
  dedup consumes is per-check-in or already per-POI. `[VERIFY: the granularity of time_embedding.parquet as
  consumed by the published CoUrb run.]`

  **WHAT THE CHAPTER WRITES, and the author's ruling now rests on firmer ground.** Under his ruling of
  2026-08-03 (PENDENCIAS_RESOLVIDOS §6.18 (arquivado 2026-08-03), option 2, "nao vamos registrar") the chapter says only **"a vector that is
  a function of the visited POI"**, with no temporal qualification. The reason is no longer "there is a
  selection step we choose not to mention" but the stronger one: **the level of Chapter 4's temporal input
  is not established, so the chapter asserts nothing about it.** Both "of the visit's timestamp" and
  "aggregated" stay forbidden, now because neither is established rather than because one was disproved.
  **"Do not register" is not a licence to write the wrong thing.** Probes `R12-dropdup`, `R12-shape`,
  `R12-notwrong` and `R12-notagg2` hold this record in place. CBIC:
  "the concatenation of the 64-dimensional embeddings of $p_1$--$p_9$" (`3_cbic/method.tex:64`), i.e.
  $\rho(x_j) = \mathbf{e}_{p_j}$. CoUrb: "Each check-in in the window is represented by the
  corresponding embedding" with $\mathbf{E}_{cat} = [\mathbf{E}_{HGI} \| \mathbf{E}_{loc} \|
  \mathbf{E}_{time}]$ (`4_courb/methodology.tex:93-95`).
- Chapter 5 (check-in-level): $\rho(x_i) = \mathbf{e}_{x_i}$, "one 64-dimensional vector per check-in
  ... a sequence of per-visit vectors rather than repeated per-place ones"
  (`5_mobiwac/04_method.tex:22`).

**Why the tasks keep the RAW history as their argument** (the option the parent left open): the task
definitions stay $f_{\mathrm{cat}}(H_i) \longrightarrow c_i$, $f_{\mathrm{reg}}(H_i) \longrightarrow
r_i$, $f_{\mathrm{place}}(H_i) \longrightarrow p_i$, unchanged. The load-bearing reason, not the
convention: the dissertation's central claim is that the representation is the dominant factor, and
that claim is only expressible if the task is the SAME OBJECT across all three studies while $\rho$
varies. It also matches the field's form (4 of 4 sources in doc 48, with CTLE the decisive case), it
matches MobiWac's own problem statement, a version of record ("Given a user's time-ordered check-in
history, we predict two properties of the next visit", `5_mobiwac/03_problem.tex:12`), it keeps the
GLOSSARY §1.1 rows for $H_i$, $f_{\mathrm{cat}}(H_i)$, $f_{\mathrm{reg}}(H_i)$ true as registered, and
it preserves the pinned probe strings verbatim (§7).

Rejected alternatives:

1. **Redefine $H_i$ as a sequence of embeddings.** Rejected on four grounds: the task definition would
   change between chapters, destroying the fixed reference point of the central claim; it contradicts
   the 4-of-4 literature pattern (doc 48); it puts Chapter 2 at odds with `5_mobiwac/03_problem.tex`,
   a version of record; and it falsifies the registered $H_i$ row in GLOSSARY §1.1.
2. **Two history objects, raw $H_i$ and encoded $\widehat{H}_i$, with the tasks consuming the encoded
   one.** Rejected: tasks over an encoded history make the task depend on the encoder, which is the
   same defect as option 1 in a second notation; it doubles the symbols for one concept; and it breaks
   probe `R12-fplace` (the pinned equation has $H_i$ as the argument).
3. **Parameterize the history by its element type** ($H_i^V$ for a value space $V$). Rejected: generic
   type machinery is heavier than a fundamentals chapter needs, and the tasks would still consume a
   representation-dependent object, so it inherits the defect of option 2 at a higher notation cost.
4. **Tasks take the encoder as a parameter** ($f^{\rho}_{\mathrm{cat}}(H_i)$). Rejected: same defect in
   different syntax — the measured quantities in the studies are the composites, no paper chapter
   indexes a task by its encoder, and the superscript would have to be carried through every results
   table reference for consistency.

**Is $\rho$ a thirteenth numbered definition or a displayed equation in prose?** Both work; the count
is the author's call. The definition form is proposed below (D5) because the map is the pivot of the
dissertation's claim and deserves the same formal standing as the objects it connects. The fallback
that keeps the count at exactly twelve: state D5's content as a displayed equation plus the remark, in
the same position, with no definition environment. Everything else in this document is unchanged under
the fallback.

---

## 4. The $\mathbf{e}_p$ versus $\mathbf{e}_{p_i}$ decision (finding 3)

The audit's position was tested against the chapter and the studies, and it holds; here is the test
rather than the inheritance.

- **In the static task, $\mathbf{e}_p$ is correct and $\mathbf{e}_{p_i}$ would be wrong.** Definition
  "Category classification" is quantified over POIs: its input is the representation of a POI $p$, its
  target is $c_p$, and no check-in index exists in its statement (`2_fundamentals.tex:116-124`). The
  study behaves accordingly: the static pairs are $(\mathbf{E}_{cat}, c)$ per POI
  (`4_courb/methodology.tex:93`), not per visit. Writing $\mathbf{e}_{p_i}$ there would import a
  sequence index into a task whose whole point is that it has none — it would make the static task
  look sequential. The repo's governing documents guard the same boundary: `NORTH_STAR.md:335-337`
  requires the task pair to be "named plainly, never narrated as one experiment on a constant pair",
  and `apx_b_static_scope.tex` defines the static task as classifying "the category of a place from
  that place's own representation" (both read this session).
- **At a history position, $\mathbf{e}_{p_j}$ is correct and $\mathbf{e}_p$ alone is not.** Position
  $j$ of a place-level window carries the embedding of the POI visited at check-in $j$: the
  composition of $j \mapsto p_j$ (Definition "Check-in") with $p \mapsto \mathbf{e}_p$ (Definition
  "Place embedding"). CBIC feeds exactly this (`3_cbic/method.tex:64`).

So the author's proposed rename is REJECTED for the definition of the place embedding itself and
ACCEPTED, in the composed form $\mathbf{e}_{p_j}$, at history positions. The composition moves from
prose into symbols: it is the displayed instantiation equation of the representation map,

$$\rho(x_j) = \mathbf{e}_{p_j} \quad \text{(place-level instantiation, Chapters 3 and 4)},$$

which is the clause of the current Definition 2.7 ("every check-in at that POI enters the model with
the same representation", `2_fundamentals.tex:435-436`) stated as mathematics. Measured in the audit
and re-confirmed: no $\mathbf{e}_{p_i}$-style notation exists anywhere in the live tree today, so the
choice breaks nothing.

---

## 5. The thirteen definitions, restated in final form

Notation conventions: no em-dash, no contractions, American English (WRITING_LAW). Statement wording
that a probe pins is carried verbatim and marked. The numbering below is positional (D1-D13); rendered
numbers follow from `\begin{definition}` order automatically, and no live prose hardcodes a definition
number (verified: the only "Definition 2.N" strings in the chapter are inside provenance comments,
`2_fundamentals.tex:55-56,:160,:445,:452`).

Before D1, the notation prose (currently `2_fundamentals.tex:68-70`) gains one sentence binding the
per-POI attributes: "Let $\mathcal{U}$, $\mathcal{P}$, $\mathcal{C}$, and $\mathcal{R}$ denote the sets
of users, POIs, category classes, and region classes. Each POI $p \in \mathcal{P}$ carries a category
$c_p \in \mathcal{C}$ and lies in a region $r_p \in \mathcal{R}$." Grounding: the region is an
attribute of the place ("its region, the place's census tract", `5_mobiwac/03_problem.tex:12`), and the
category is a per-POI label under the seven-class taxonomy (`3_cbic/method.tex:21`). This binds $c_p$,
which is currently FREE in Definition 2.3 (it appears in the task statement with no introduction —
a well-formedness defect the author's findings did not list; GLOSSARY §1.1 already uses $c_p$ in its
$g_{\mathrm{cat}}$ row, so the registry anticipated the binding).

---

**D1. Check-in** (was 2.1; label `def:fund:checkin`; statement unchanged except one binding clause)

> The $i$th check-in of user $u$ is the tuple
> $$x_i = (u, p_i, t_i, c_i, r_i),$$
> where $p_i \in \mathcal{P}$ is the visited POI, $t_i$ is its timestamp, $c_i = c_{p_i}$ is its
> category, and $r_i = r_{p_i}$ is its region.

- Introduces: $x_i$, $p_i$, $t_i$, $c_i$, $r_i$.
- Consumes: $\mathcal{P}$ and the attribute maps $c_p$, $r_p$ from the notation prose.
- Changed: "$c_i \in \mathcal{C}$ is its category" becomes "$c_i = c_{p_i}$ is its category" (same for
  $r_i$). Why: it states the fact the studies rely on — a check-in's category and region are the
  visited POI's attributes, not independent fields — and it makes the later composition
  $\mathbf{e}_{p_j}$ well-typed. The membership statements $c_i \in \mathcal{C}$, $r_i \in \mathcal{R}$
  follow from the attribute maps' codomains, so no information is lost.
- Correctness: well-formed; all symbols on the right are bound; the index $i$ ranges over user $u$'s
  chronologically ordered check-ins (the ordering is stated in the surrounding prose today and should
  remain there).

**D2. Check-in history** (was 2.2; label `def:fund:history`; statement unchanged)

> The check-in history of length $\ell$ preceding check-in $x_i$ is the ordered sequence
> $$H_i = (x_{i-\ell}, \ldots, x_{i-1}).$$
> A target label is withheld from it when one of the sequential tasks is trained.

- Introduces: $H_i$, $\ell$. Consumes: $x_i$ (D1).
- Changed: nothing. The element type is the raw tuple, which §3 argues is correct rather than a defect.
- Correctness: well-formed for $i > \ell$. Shorter prefixes are handled DIFFERENTLY BY STUDY, so the
  prose must not generalize: Chapters 3 and 4 zero-pad, while Chapter 5 DROPS the padded windows
  (`5_mobiwac/05_setup.tex:28`, quoted: "we keep only the full-length window ending there and drop
  these padded duplicates"). The superseded wording said the studies zero-pad
  (`3_cbic/method.tex:65`, `4_courb/methodology.tex:95`), a model-side device that does not belong in
  the data definition. Recommend the surrounding prose keep the padding remark where the models are
  discussed, not here. Note (minor, author's call): since $H_i$ ends at $x_{i-1}$, the target $x_i$ is
  excluded by construction; the withholding sentence is about the observed fields of PAST check-ins
  remaining legitimate inputs while the target's own label never enters. If the sentence is kept, its
  referent could be sharpened; it is not mathematically wrong.

**D3. Place embedding** (was 2.7; label `def:fund:placelevel`; statement unchanged, moved)

> A place embedding assigns one vector $\mathbf{e}_p$ to each POI $p$, so every check-in at that POI
> enters the model with the same representation.

- Introduces: $\mathbf{e}_p$. Consumes: $p \in \mathcal{P}$ (notation prose).
- Changed: position only (from `2_fundamentals.tex:434` to the new representations subsubsection of
  Section 2.1). Section 2.2's limitation paragraph (`:439-444`) stays in Section 2.2 and now points
  backward via `\ref{def:fund:placelevel}`.
- Correctness: well-formed; the codomain $\mathbb{R}^{d}$ is deliberately implicit here and explicit in
  D5, since $d$ differs across studies (64 in Chapters 3 and 5, 192 concatenated in Chapter 4;
  `3_cbic/method.tex:53`, `4_courb/methodology.tex:89-95`).

**D4. Check-in-level representation** (was 2.8; label `def:fund:checkinlevel`; statement unchanged,
moved; probe `R12-eqxi` pins the wording — carried VERBATIM)

> A check-in-level representation assigns one vector $\mathbf{e}_{x_i}$ to each check-in $x_i$, so two
> visits to the same POI may enter the model with different representations.

- Introduces: $\mathbf{e}_{x_i}$ (registry row pending, PENDENCIAS_RESOLVIDOS §6.13 (arquivado 2026-08-03)). Consumes: $x_i$ (D1).
- Changed: position only. The Check2HGI narrative that follows it today (`:467-468` and the losses at
  `:489-556`) stays in Section 2.2, pointing backward.
- Correctness: well-formed; the contrast with D3 is now adjacent (the two definitions sit together),
  which is where the chapter's central contrast belongs.

**D5. Representation map** (NEW; proposed label `def:fund:repmap`; see §3 for the twelve-definition
fallback)

> A representation map assigns to each check-in a vector,
> $$\rho(x_i) \in \mathbb{R}^{d},$$
> and extends to histories elementwise,
> $$\rho(H_i) = \bigl(\rho(x_{i-\ell}), \ldots, \rho(x_{i-1})\bigr).$$

Followed by the factorization remark (prose, not part of the definition): every model of the
SEQUENTIAL tasks in this dissertation reads $\rho(H_i)$ rather than $H_i$ itself. The static task is
outside the factorization: $g_{\mathrm{cat}}$ reads $\mathbf{e}_p$ and never a history
(`2_fundamentals.tex:116-124`). Chapters 3 and 4 instantiate $\rho$ at
the place level, $\rho(x_j) = \mathbf{e}_{p_j}$ in Chapter 3, with Chapter 4 concatenating spatial,
temporal, and categorical components; Chapter 5 instantiates it at the check-in level, with TWO
elementwise streams rather than one: the category task reads $\rho(x_i) = \mathbf{e}_{x_i}$, the
per-visit vector, and the region task reads the trained vector of that visit's region node from the
same graph (`5_mobiwac/04_method.tex:27`, quoted: "the region task reads the same window of visits,
each visit now represented by the trained vector of its region node"). The three studies hold
Definitions D6-D8 fixed and vary $\rho$.

- Introduces: $\rho$, $d$. Consumes: $x_i$, $H_i$ (D1, D2); the remark consumes $\mathbf{e}_p$ (D3),
  $\mathbf{e}_{x_i}$ (D4), $p_j$ (D1).
- Why it exists: it is the named function findings 2 and 4 were missing, it is where the data layer
  and the representation layer meet, and it is the formal statement of the dissertation's claim shape
  (same task, varying representation).
- Correctness: well-formed; domain is the set of check-ins, codomain $\mathbb{R}^{d}$; the elementwise
  extension is standard and total on histories.

**D6. Category classification** (was 2.3; label `def:fund:catclf`; statement unchanged)

> Category classification predicts the category of a POI from its representation:
> $$g_{\mathrm{cat}}(\mathbf{e}_p) \longrightarrow c_p.$$
> At evaluation time, POI $p$ is held out from the classifier-training fold, so "unknown POI" means
> unknown to the classifier, not necessarily absent from the graph used to learn $\mathbf{e}_p$.

- Introduces: $g_{\mathrm{cat}}$. Consumes: $\mathbf{e}_p$ (D3, now BACKWARD — this removes the
  chapter's one forward dependency), $c_p$ (notation prose, now bound).
- Changed: nothing in the statement; both consumed symbols are now defined before use.
- Correctness: well-formed; domain $\mathbb{R}^{d}$, codomain $\mathcal{C}$; static (quantified over
  POIs, no check-in index), which is what the studies run (`4_courb/methodology.tex:93`) and what
  GLOSSARY §1 and the static-scope appendix require.

**D7. Next-category prediction** (was 2.4; label `def:fund:nextcat`; statement unchanged)

> Next-category prediction maps a check-in history to the category of the next visit:
> $$f_{\mathrm{cat}}(H_i) \longrightarrow c_i.$$

- Introduces: $f_{\mathrm{cat}}$. Consumes: $H_i$ (D2), $c_i$ (D1).
- Correctness: well-formed; domain the set of histories, codomain $\mathcal{C}$; the raw-history
  argument is argued in §3. Matches the GLOSSARY §1.1 row exactly.

**D8. Next-region prediction** (was 2.5; label `def:fund:nextreg`; statement unchanged)

> Next-region prediction maps a check-in history to the region of the next visit:
> $$f_{\mathrm{reg}}(H_i) \longrightarrow r_i.$$

- Introduces: $f_{\mathrm{reg}}$. Consumes: $H_i$ (D2), $r_i$ (D1).
- Correctness: as D7, codomain $\mathcal{R}$.

**D9. Next-place prediction** (was 2.6; label `def:fund:nextplace`; statement unchanged; probes
`R12-fplace` and `R12-fplace2` pin the equation and the exclusion — carried VERBATIM)

> Next-place prediction maps a check-in history to the identity of the next visited POI:
> $$f_{\mathrm{place}}(H_i) \longrightarrow p_i.$$
> It is named to delimit the scope of the dissertation, and no chapter reports a result for
> $f_{\mathrm{place}}$.

- Introduces: $f_{\mathrm{place}}$ (registry row pending, PENDENCIAS_RESOLVIDOS §6.13 (arquivado 2026-08-03)). Consumes: $H_i$ (D2),
  $p_i$ (D1).
- Correctness: well-formed, codomain $\mathcal{P}$; the scope exclusion stays inside the definition
  environment, beside the function, per `R12-fplace2`. Finding 4 dissolves under §3: the task-level
  statement over the raw history is correct, and the model-level consumption of representations is
  D5's factorization, which applies to $f_{\mathrm{place}}$'s solvers in the literature exactly as it
  does to ours.

**D10. Hard parameter sharing** (was 2.9; label `def:fund:hard`; statement unchanged)

> Hard parameter sharing passes all inputs through a single shared trunk before branching to
> task-specific output heads, so every task uses the same hidden
> representations~\cite{ruder2017mtloverview}.

- Introduces: the topology name. Consumes: nothing formal.
- Correctness: qualitative by design; a fundamentals chapter defining a topology family in words, with
  the citation carrying the formal weight, is well-formed for its purpose. No free mathematical symbol.

**D11. Soft parameter sharing** (was 2.10; label `def:fund:soft`; statement unchanged)

> Soft parameter sharing gives each task its own complete network and couples the networks by
> penalizing differences between their parameters~\cite{ruder2017mtloverview}.

- As D10.

**D12. Negative transfer** (was 2.11; label `def:fund:negtransfer`; statement unchanged)

> Negative transfer occurs when joint training leaves a task worse than its dedicated single-task
> model.

- Consumes: the registered term "dedicated single-task model" (GLOSSARY §2). No formal symbol.
- Correctness: qualitative and evaluable — "worse" is bound elsewhere in the chapter to the metrics
  and tests of Section 2.4, which is the right division of labor; the definition names the phenomenon,
  the evaluation section makes it measurable.

**D13. Gradient conflict** (was 2.12; label `def:fund:conflict`; **indices renamed per AD-7**, statement
otherwise unchanged)

> Let $\mathbf{g}_a$ and $\mathbf{g}_b$ be the gradients of two task losses with respect to the shared
> parameters, and let $\varphi_{ab}$ be the angle between them, so that
> $$\cos\varphi_{ab} = \frac{\mathbf{g}_a^{\top}\mathbf{g}_b}{\lVert \mathbf{g}_a \rVert\, \lVert
> \mathbf{g}_b \rVert}.$$
> The two tasks conflict at that point when $\cos\varphi_{ab} < 0$~\cite{yu2020pcgrad}.

**Why $a$ and $b$ rather than $i$ and $j$ (AD-7, his option 1).** Everywhere else in the chapter $i$ indexes
a check-in ($x_i$, $H_i$, $\mathbf{e}_{x_i}$); here the subscripts index tasks, and a reader following the
indices across the chapter reads the same letter as two different things. The source uses $i$ and $j$ for
tasks (`yu2020pcgrad`), so this departs from the source's notation deliberately and only in the letters: no
quantity, relation or claim changes, and the citation still carries the definition. Live-tree scope for the
edit: `2_fundamentals.tex:888-895`, six lines, and the symbols occur **nowhere else in the tree**.

- Introduces: $\mathbf{g}_a$, $\varphi_{ab}$ (locally bound by its own "Let"). Consumes: the notion of
  shared parameters (D10).
- Correctness: well-formed and self-contained; the subscripts $i, j$ here index TASKS, while the same
  letters index check-ins in D1-D9. This overloading is live today and has not confused a reader
  because the two uses never co-occur in one formula; flagged as a note, not a change (a rename to
  task indices $k, k'$ would touch `eq:fund:cosine`, Appendix F, and probe `R9-conflict`'s
  neighborhood for a purely cosmetic gain).

---

## 6. What must not change — verified

1. **The three tasks stay formally distinct.** D6, D7, D8 are three definitions with three function
   symbols, two argument types (a POI representation versus a raw history), and three codomains; D9
   names the excluded fourth. GLOSSARY §1's per-paper mapping is untouched.
2. **The static task stays static.** D6 is quantified over POIs; no check-in index appears in it; §4
   rejects the rename that would have blurred this.
3. **Next place keeps its scope exclusion beside its function.** The exclusion sentence is inside D9's
   definition environment, immediately after the equation, exactly as pinned by `R12-fplace2`.
4. **Gate probes.** See §7: this design breaks none, provided the application pass carries four pinned
   strings verbatim.
5. **GLOSSARY §1.1 is the author's registry.** No row is written by this document; §8 PROPOSES rows.
   The two rows already pending in PENDENCIAS_RESOLVIDOS §6.13 (arquivado 2026-08-03) ($\mathbf{e}_{x_i}$ and $f_{\mathrm{place}}(H_i)$)
   are consumed as pending, not as registered.

## 7. Probe impact — every probe checked against the design

Probes read from `src_utils/check_audit_claims.py` (read only; not edited). All probes that pin
`chapters/2_fundamentals.tex` strings were enumerated mechanically this session.

| Probe | Pinned string (regex, abbreviated) | Impact under this design |
|---|---|---|
| `R12-eqxi` | `assigns one vector $\mathbf{e}_{x_i}$ to each check-in` | NOT BROKEN. D4 carries the sentence verbatim; the definition moves, the probe is file-scoped, not line-scoped. |
| `R12-fplace` | `f_{\mathrm{place}}(H_i)\longrightarrow p_i` | NOT BROKEN. D9 keeps the raw history as the argument (§3), so the equation is unchanged. |
| `R12-fplace2` | `no chapter reports a result for $f_{\mathrm{place}}$` | NOT BROKEN. The exclusion stays beside the function inside D9. |
| `NUM-4` | `0.8186` in `chapters/apx_g_hgi_tuning.tex` | NOT TOUCHED. Different file; no number in this design. |
| `R11-def27` | `\label{def:fund:checkinlevel}` | NOT BROKEN. The label moves with its definition and remains in the same file. |
| `R9-conflict`, `R10-cosine` | cosine prose; `def:fund:conflict` | **NOT TOUCHED, re-verified after AD-7.** D13's statement is unchanged but its INDICES are renamed ($i,j \to a,b$). Tested against the live chapter text with the rename applied: `R9-conflict` matches `cosine between their gradients` (prose, no symbols) and `R10-cosine` matches the label `def:fund:conflict`. Both hold before and after. |
| `R9-pareto*`, `R10-novelty`, `R10-hamtl`, `R11-aligned*`, `R11-hgi`, `R12-dwa*`, `COD-015d`, `A23-R3` | various Section 2.3 strings and absence probes | NOT TOUCHED. This design does not alter Section 2.3 prose or reintroduce any banned string. |

The list of probes this design BREAKS is therefore EMPTY, with one obligation on the application pass:
the four wordings marked VERBATIM in §5 (D4's sentence, D9's equation and exclusion) must be carried
character-for-character, and `src_utils/check.sh` must be run after application as the mechanical
confirmation. If the author instead adopts any wording change to those strings, the probe must be
updated in the same commit (audit §"what this means", constraint 2), which is his call, not this
document's.

## 8. Registry rows PROPOSED (the table is the author's; nothing here is registered)

| Symbol | Proposed definition | Notes |
|---|---|---|
| $\rho$ | A representation map: assigns to each check-in $x_i$ a vector $\rho(x_i) \in \mathbb{R}^{d}$, extended elementwise to histories, $\rho(H_i) = (\rho(x_{i-\ell}), \ldots, \rho(x_{i-1}))$. | Every model of the SEQUENTIAL tasks reads $\rho(H_i)$ (the static task reads $\mathbf{e}_p$ and is outside the factorization); the studies vary $\rho$ and hold the task DEFINITIONS fixed. Chapters 3-4: place-level instantiation; Chapter 5: two streams, $\rho(x_i) = \mathbf{e}_{x_i}$ for category and the region-node vector for region. Verified unoccupied: `\rho` occurs zero times in the live frame tree with comments stripped. |
| $d$ | The representation dimension, the codomain dimension of $\rho$. | 64 in Chapters 3 and 5, 192 in Chapter 4 (`3_cbic/method.tex:53`, `4_courb/methodology.tex:89`, `5_mobiwac/04_method.tex:22`); kept generic in the definitions. **SCOPE NOTE, and it is why this row needs one:** the letter $d$ is NOT unclaimed. Measured live with comments stripped, `$d$` occurs once, `d_{ij}` four times (a geodesic distance, `3_cbic/method.tex`) and `d_{\mathrm{shared}}` three times (a shared-trunk width). None of these is in Chapter 2, so there is no collision inside the chapter, but the row must say that $d$ is the representation dimension IN CHAPTER 2 rather than a document-wide reservation. Contrast $\rho$, which is genuinely free: zero live occurrences tree-wide. |
| (amendment to the $\mathbf{e}_p$ row's Notes) | Add: "at history position $j$, the place-level instantiation feeds $\mathbf{e}_{p_j}$, the embedding of the POI visited at check-in $j$." | Makes the composition of finding 3 registry-visible without a new symbol. |
| (amendment to the $x_i$ row's Notes) | Add: "$c_i = c_{p_i}$ and $r_i = r_{p_i}$: a check-in's category and region are the visited POI's attributes." | Binds $c_p$, $r_p$, which the $g_{\mathrm{cat}}$ row already uses. |

The two rows pending in PENDENCIAS_RESOLVIDOS §6.13 (arquivado 2026-08-03) ($\mathbf{e}_{x_i}$; $f_{\mathrm{place}}(H_i)$) are
prerequisites of this design and are NOT re-proposed here; this design is compatible with his option 1
(register both) and option 2 (register only $\mathbf{e}_{x_i}$) — under option 2 the $f_{\mathrm{place}}$
symbol still appears in D9 as it does today, which is the state his option 2 describes. Under his
option 3 (withdraw both symbols), D4 and D9 revert to their pre-round-12 wordings and this design's
ordering and $\rho$ layer still stand, but findings 2 and 4 reopen at the wording level.

## 9. UNFINISHED

1. **The CoUrb instantiation's name.** The chapter prose says the second study supplies context "while
   retaining a place-level input" (`2_fundamentals.tex:472-474`), but its temporal component encodes
   each check-in's own timestamp (`4_courb/methodology.tex:144-153`), so ST-MTLNet's window positions
   are not constant across visits to one POI. The $\rho$ formalization states Chapter 4's
   instantiation correctly without forcing the binary; whether the frame keeps calling it place-level
   (defensible: the LEARNED vectors are per-place, the temporal channel is a deterministic function of
   the timestamp field, not a learned per-visit representation) is a wording ruling only the author
   can make. Not settled here.
2. **Thirteen definitions or twelve.** Both forms are fully specified (§3, §5 D5); the choice is the
   author's. Not settled here.
3. **The withholding sentence in D2.** A sharper referent is recommended but no replacement wording is
   proposed, because the sentence is his and it is not mathematically wrong. Not settled.
4. ~~**The task/check-in index overloading in D13**~~ **CLOSED 2026-08-03 as AD-7: rename to $a,b$.** See the AD-7 row in §10 and D13's restated form in §5. It was raised here and never became a decision until the author was asked directly.
   Flagged with the cost of the cosmetic fix; not settled.
5. **MobiWac padding convention.** CBIC and CoUrb zero-padding was verified at the cited lines; the
   MobiWac chapter's handling of histories shorter than the window was not re-verified this session
   (`5_mobiwac/05_setup.tex` was not read). D2 does not depend on it, but the prose remark about
   padding should be checked against Chapter 5 before the application pass writes it.
6. **Renumbering ripple outside the chapter — CLOSED, kept here for the record.** Three checks, each
   run over the whole `../../../../src` tree, every `.tex` file, comments stripped, all returning empty:
   (a) `def:fund:` referenced outside `2_fundamentals.tex` — zero hits; (b) hardcoded
   `Definition[~ ]2.N` or `Definição[~ ]2.N` in live prose — zero hits (the "Definition 2.N" strings
   found earlier live in provenance comments of `2_fundamentals.tex` only, which comment-stripping
   excludes); (c) `\rho` — zero hits, so the new symbol overloads nothing. Check (b) was initially run
   only over `chapters/` without comment stripping; the tree-wide comment-stripped rerun (this
   session, after the first draft of this document) is what closes the item. The renumbering from the
   reorder is therefore contained entirely within the chapter and resolved by `\ref` automatically.

---

## 10. The gating decisions: six closed, AD-2 reopened, plus one larger undecided item

Nothing in this design is applied until AD-2 is settled and the structural question below is answered. **AD-1, AD-3, AD-4 (conditionally), AD-5 and AD-6 are CLOSED as of 2026-08-03.** AD-2 is open and its question changed shape: see
`../src_utils/_history/_round12/50_courb_temporal_level_investigation.md`, which is the code study he asked for
and which refutes the premise the decision was framed on. **AD-4, AD-5 and AD-6 are also closed** as of the
same date: AD-4 conditionally, with a title he later had to reopen (he revoked `place representation` from
the registry hours after naming it), and with the condition that the
section inversion of §11 may remove the need for the subsection at all; AD-5 with both registry rows
authorized and the $\rho$ row now required rather than optional; AD-6 to sharpen the D2 sentence. The rows
above carry each ruling with its evidence.

| id | the decision | where it is recorded |
|---|---|---|
| **AD-1** | ~~Twelve definitions or thirteen.~~ **RESOLVED 2026-08-03: THIRTEEN.** His words: "Vamos de treze." $\rho$ enters as a numbered Definition, so the chapter becomes 2.1-2.13 and the factorization carries the same visual weight as the objects it relates. The twelve-definition fallback in §3 is now dead and is kept only as the record of the alternative. Mechanical consequence, verified not assumed: renumbering shifts every definition after $\rho$, so each `\ref{def:fund:*}` must be re-checked at application; probe `R11-def27` pins `\label{def:fund:checkinlevel}`, a LABEL and not a number, so renumbering cannot break it (confirmed against the parsed probe tuple). | PENDENCIAS_RESOLVIDOS §6.14 (arquivado 2026-08-03) decision 1, closed |
| **AD-2** | **STILL OPEN. My "answered" claim of 2026-08-03 was RETRACTED the same day, because it rested on an unverified link between two files.** I had asserted that the per-check-in matrix the temporal notebook writes (`time_embedding_novo.csv`) is the table the ETL reads, but the ETL reads `time_embedding.**parquet**` (`create_inputs_hgi.py:415`), **nothing in that repository writes that parquet**, no CSV-to-parquet conversion exists, and the file is not on disk, so its granularity is unknown. If it is already POI-level the `drop_duplicates("placeid")` at `:437` is a no-op and there is no selection step at all. **What holds:** the encoder emits one row per check-in (`Time_Encoder.ipynb` cell 13 stored output `(2535573, 64)`), the dedup is in the category-task path, and the temporal channel is in that input. **What would close it is one artifact** the author does not have: the CoUrb-era `time_embedding.parquet`, where `len(df)` against the state's POI and check-in counts decides it. **Closed as `[VERIFY]` at his instruction** ("Vamos de B, e matamos esse assunto") and documented as `LO-12` in `../../src_utils/LEFT_OUT.md`. Retraction and boundary in `../src_utils/_history/_round12/50_courb_temporal_level_investigation.md`. | PENDENCIAS_RESOLVIDOS §6.15 (arquivado 2026-08-03), §6.21, §6.22 — reopened, then closed as LEFT_OUT |
| **AD-3** | ~~How Chapter 2 states Chapter 5's two-stream input.~~ **RESOLVED 2026-08-03: NAME BOTH STREAMS.** He confirmed the defect and supplied the mechanism: "o HGI produz dois embeddings finais um de regiao e outro de checking, e usamos essas duas entradas, respectivamentte, next-region e next-category" — two final embeddings of the same trained graph, feeding the two tasks respectively. That is what §5's D5 remark now says, with the `04_method.tex:27` quote. His "respectively" is what settles it in favor of naming both rather than deferring to Chapter 5. | PENDENCIAS_RESOLVIDOS §6.14 (arquivado 2026-08-03) decision 3, closed |
| **AD-4** | **CONDITIONAL, and its title is now UNRESOLVED again through no fault of the ruling.** He gave "Check-in and place representation" on 2026-08-03; later the same day he revoked `place representation` from the registry ("vamos usar so place embedding para evitar conflitos e interpretacoes dubias"), so the second half of that title is no longer admissible under the fail-closed rule. **I am not spending a decision of his on it**, because the title may be moot: AD-4 was always conditional ("maybe with this inversion we even need this new section"), and if the §11 inversion proceeds the representation definitions are already in the right section and the subsubsection does not exist. Candidates when it is needed: (a) "Check-in and place embedding", both halves registered but not his wording; (b) "Place embedding and check-in-level representation", literally the two Definition titles, but that is the dual head round 11 deliberately split. **Nothing is created either way.** | PENDENCIAS_RESOLVIDOS §6.16 (arquivado 2026-08-03) and §6.22, conditional; title deferred to the inversion |
| **AD-5** | ~~The two registry rows already pending.~~ **RESOLVED 2026-08-03: BOTH AUTHORIZED** ($\mathbf{e}_{x_i}$ and $f_{\mathrm{place}}(H_i)$). And a consequence of AD-1: with thirteen definitions the $\rho$ row is no longer optional but **REQUIRED**, because $\rho$ becomes a numbered object of the chapter rather than prose notation. | PENDENCIAS_RESOLVIDOS §6.13 (arquivado 2026-08-03) and §6.16, closed |
| **AD-6** | ~~Keep or sharpen the D2 withholding sentence.~~ **RESOLVED 2026-08-03: SHARPEN** ("vamos afia-la"). Measuring what it must say found the real defect, which is not vagueness: as written, "A target label is withheld from it" invites the reading that categories are STRIPPED from the history, and `5_mobiwac/05_setup.tex:76` says the opposite — "a per-visit vector legitimately carries more than the previous category, including the place, its neighborhood, and the hour of the visit". What is withheld lives in $x_i$, which $H_i$'s index range already excludes. The sharper sentence must name the target AS A FUNCTION OF THE TASK ($c_i$ for next category, $r_i$ for next region), say it comes from $x_i$, and say what REMAINS available. | PENDENCIAS_RESOLVIDOS §6.16 (arquivado 2026-08-03), closed |
| **AD-7** | ~~The index overloading in D13.~~ **RESOLVED 2026-08-03: RENAME THE INDICES** (his option 1). In D13 $\mathbf{g}_i$, $\mathbf{g}_j$ and $\varphi_{ij}$ index **tasks**, while $i$ indexes **check-ins** everywhere else in the chapter ($x_i$, $H_i$, $\mathbf{e}_{x_i}$). The rename frees $i$ for check-ins throughout. **Scope measured, and smaller than the cost note implied:** the symbols occur in exactly six live lines, all inside the D13 block at `2_fundamentals.tex:888-895`, and **nowhere else in the tree**; the appendix on gradient cosine refers to the concept in a comment and never to the label or the symbols, so the earlier claim that a rename "requires checking the appendix" was wider than the evidence. `R10-cosine` pins the label `def:fund:conflict`, which a rename does not touch. **Applied with the redesign, not before:** §5's D13 specifies the statement as unchanged, so editing the chapter now would put the chapter and this design out of step during the window when the redesign is still pending. | PENDENCIAS_RESOLVIDOS §6.19 (arquivado 2026-08-03), closed |

Two further registry rows are PROPOSED in §8 ($\rho$ and $d$) plus two amendments to existing rows. The
notation table is the author's; nothing in this document is registered, and no agent may add a row.


---

## 11. UNDECIDED, and larger than any of the six: inverting §2.1 and §2.2

He raised this answering AD-4, and it is not AD-4. AD-4 asked for the title of a subsubsection; this
changes the chapter's section order. Recorded separately because the two decisions differ in kind and in
cost.

**His proposal, verbatim:** "podemos mudar a ordem e talvez faca ate mais sentido vide que o se primeiro
falarmos de represetnacao e fazermos a definicao formal em representacao a sequencia natual seria falar
das tarefas que podemos treinar com essas representacoes." Representations first, with the formal
definitions there; then the tasks trainable on them. And his own caution: "a narrativa tem que esta acima
desse problema, temos que ter muito cuidade."

**His argument is better than the design's.** The design moves two definitions INTO the tasks section to
remove the forward dependency. He removes it at the root: with representations first, nothing has to move,
because the tasks then consume objects the reader already holds. The reading order also comes to mirror the
dissertation's own thesis, that the representation is the dominant factor. If this is adopted, the
subsubsection of AD-4 is probably unnecessary, which is exactly what he anticipated.

**The cost, measured rather than estimated:**

| cost | what it is | size |
|---|---|---|
| cross-references | **three** live references to the two section labels, ALL inside `2_fundamentals.tex` (`sec:fund:tasks` ×1, `sec:fund:repr` ×2). Nothing outside the chapter points at either. | small |
| prose that becomes FALSE | `2_fundamentals.tex:14-20`, the chapter opening, states the order in prose with the refs ("It **first** distinguishes the POI prediction tasks… It **then** traces mobility representations"); and `:27`, the §2.1 opening, IS the justification of the present order ("This section defines the prediction targets **before** reviewing the methods used for them"). The second does not merely go stale, it becomes a false statement about the chapter's own structure. | two rewrites |
| **chapter structure** | the 2.1–2.5 order is fixed in the chapter map, `NORTH_STAR.md:73-80`, and the project scope says not to invent sections. Inverting 2.1 and 2.2 **edits the map**. | **this is why it is his call** |
| gates | **none.** Every `check_*.py` and `check.sh` was checked: the four files mentioning "2.1" mean PENDENCIAS item numbers or test fixtures, not the chapter. `R11-fab15` pins a sentence in the INTRODUCTION. | zero |
| side effect | `fundamentals/` has directories `2.1_poi_prediction_tasks` and `2.2_representations_for_mobility`. The folder is frozen provenance and those names record how the chapter WAS built, so not an error, but they would describe a different order. | note only |

**The consequence for the edit plan, and it is why this cannot be decided after application starts.** The
eight-step plan in `../src_utils/_history/_round12/49_definitions_validation_and_plan.md` was written on the
assumption that the representation definitions move UP into §2.1. Under the inversion that assumption is
void: two whole sections trade places and the two prose passages above must be rewritten. **The plan must
be redone before any edit, not adjusted after one.**

Nothing here is authorized. His work order: "depois dessas definicoes podemos aplicado."

## 12. Where the rest of the trail is

| file | what it holds |
|---|---|
| `../src_utils/_history/_round12/46_definition_dependency_audit.md` | the four findings measured against the live source, with the dependency graph and the one forward edge |
| `../src_utils/_history/_round12/48_history_formulation_literature.md` | the four literature sources (CSLSL, CTLE, HAMTL, and the dissertation's own MobiWac chapter) that settled the layering, and the credibility argument stated as narrowly as the evidence allows |
| `../src_utils/_history/_round12/47_definitions_consolidated.md` | the original design draft, preserved unedited, before the five corrections above |
| `../src_utils/_history/_round12/49_definitions_validation_and_plan.md` | the adversarial validation and the eight-step edit plan, including which steps must land in one commit and the sabotage-validation requirement for every probe |
