# 47_definitions_consolidated.md — the twelve definitions of Chapter 2, consolidated for mathematical correctness

Round 12, 2026-08-03. A DESIGN DOCUMENT, not an edit: no `.tex` file was touched. A later pass applies
this, and the author approves every word before it lands. Measured against the live
`src/chapters/2_fundamentals.tex` (1521 lines) at the tree following the round-12 state; every claim
about what a study does cites the chapter file and line read this session.

Inputs this document builds on, all read this session:

- `src_utils/_history/_round12/46_definition_dependency_audit.md` (the measurement; findings 1-4)
- `src_utils/_history/_round12/48_history_formulation_literature.md` (4-of-4 literature evidence on history
  formulation; constrains the layering decision)
- `src/chapters/2_fundamentals.tex:66-190` (Definitions 2.1-2.6 and surrounding prose),
  `:420-500` (Definitions 2.7-2.8), `:678-700` (2.9-2.11), `:885-896` (2.12)
- `src/chapters/5_mobiwac/03_problem.tex:12` and `04_method.tex:22,:27` (versions of record)
- `src/chapters/3_cbic/method.tex:53,:64-65` and `src/chapters/4_courb/methodology.tex:89-95,:144-153`
  (what the two earlier studies actually feed their models)
- `GLOSSARY.md` §1, §1.1; `src_utils/PENDENCIAS.md` §6.13 (the two pending registry rows);
  `src_utils/check_audit_claims.py` (probe strings, read, not edited);
  `AGENT_GUARDRAILS.md` (headings and §4b in full); `WRITING_LAW.md` (headings and the §1 mechanics
  rules at lines 33-68: American English, no contractions); `NORTH_STAR.md` (the arc beat at lines
  330-350: the task-pair acknowledgment and the static-task corollary);
  `src/chapters/apx_b_static_scope.tex` (opening, the static task's definition and scope).

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
is a property of the data, the model is not — every predictive model in this dissertation reads
$\rho(H_i)$ rather than $H_i$ itself, and the three studies hold the tasks fixed while they vary
$\rho$. The instantiations, each verified against its chapter:

- Chapters 3 and 4 (place-level): position $j$ of the window carries a vector that is a function of
  the visited POI (and, in Chapter 4, of the visit's timestamp through the temporal encoder). CBIC:
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
- Correctness: well-formed for $i > \ell$; the studies handle shorter prefixes by zero-padding
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

- Introduces: $\mathbf{e}_{x_i}$ (registry row pending, PENDENCIAS §6.13). Consumes: $x_i$ (D1).
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

Followed by the factorization remark (prose, not part of the definition): every predictive model in
this dissertation reads $\rho(H_i)$ rather than $H_i$ itself. Chapters 3 and 4 instantiate $\rho$ at
the place level, $\rho(x_j) = \mathbf{e}_{p_j}$ in Chapter 3, with Chapter 4 concatenating spatial,
temporal, and categorical components; Chapter 5 instantiates it at the check-in level, $\rho(x_i) =
\mathbf{e}_{x_i}$. The three studies hold Definitions D6-D8 fixed and vary $\rho$.

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

- Introduces: $f_{\mathrm{place}}$ (registry row pending, PENDENCIAS §6.13). Consumes: $H_i$ (D2),
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

**D13. Gradient conflict** (was 2.12; label `def:fund:conflict`; statement unchanged)

> Let $\mathbf{g}_i$ and $\mathbf{g}_j$ be the gradients of two task losses with respect to the shared
> parameters, and let $\varphi_{ij}$ be the angle between them, so that
> $$\cos\varphi_{ij} = \frac{\mathbf{g}_i^{\top}\mathbf{g}_j}{\lVert \mathbf{g}_i \rVert\, \lVert
> \mathbf{g}_j \rVert}.$$
> The two tasks conflict at that point when $\cos\varphi_{ij} < 0$~\cite{yu2020pcgrad}.

- Introduces: $\mathbf{g}_i$, $\varphi_{ij}$ (locally bound by its own "Let"). Consumes: the notion of
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
   The two rows already pending in PENDENCIAS §6.13 ($\mathbf{e}_{x_i}$ and $f_{\mathrm{place}}(H_i)$)
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
| `R9-conflict`, `R10-cosine` | cosine prose; `def:fund:conflict` | NOT TOUCHED. D13 is unchanged. |
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
| $\rho$ | A representation map: assigns to each check-in $x_i$ a vector $\rho(x_i) \in \mathbb{R}^{d}$, extended elementwise to histories, $\rho(H_i) = (\rho(x_{i-\ell}), \ldots, \rho(x_{i-1}))$. | Every model of this dissertation reads $\rho(H_i)$; the studies vary $\rho$ and hold the tasks fixed. Chapters 3-4: place-level instantiation; Chapter 5: $\rho(x_i) = \mathbf{e}_{x_i}$. Verified unoccupied: `\rho` occurs zero times in the live frame tree with comments stripped. |
| $d$ | The representation dimension, the codomain dimension of $\rho$. | 64 in Chapters 3 and 5, 192 in Chapter 4 (`3_cbic/method.tex:53`, `4_courb/methodology.tex:89`, `5_mobiwac/04_method.tex:22`); kept generic in the definitions. |
| (amendment to the $\mathbf{e}_p$ row's Notes) | Add: "at history position $j$, the place-level instantiation feeds $\mathbf{e}_{p_j}$, the embedding of the POI visited at check-in $j$." | Makes the composition of finding 3 registry-visible without a new symbol. |
| (amendment to the $x_i$ row's Notes) | Add: "$c_i = c_{p_i}$ and $r_i = r_{p_i}$: a check-in's category and region are the visited POI's attributes." | Binds $c_p$, $r_p$, which the $g_{\mathrm{cat}}$ row already uses. |

The two rows pending in PENDENCIAS §6.13 ($\mathbf{e}_{x_i}$; $f_{\mathrm{place}}(H_i)$) are
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
4. **The task/check-in index overloading in D13** ($i, j$ index tasks there, check-ins elsewhere).
   Flagged with the cost of the cosmetic fix; not settled.
5. **MobiWac padding convention.** CBIC and CoUrb zero-padding was verified at the cited lines; the
   MobiWac chapter's handling of histories shorter than the window was not re-verified this session
   (`5_mobiwac/05_setup.tex` was not read). D2 does not depend on it, but the prose remark about
   padding should be checked against Chapter 5 before the application pass writes it.
6. **Renumbering ripple outside the chapter — CLOSED, kept here for the record.** Three checks, each
   run over the whole `src/` tree, every `.tex` file, comments stripped, all returning empty:
   (a) `def:fund:` referenced outside `2_fundamentals.tex` — zero hits; (b) hardcoded
   `Definition[~ ]2.N` or `Definição[~ ]2.N` in live prose — zero hits (the "Definition 2.N" strings
   found earlier live in provenance comments of `2_fundamentals.tex` only, which comment-stripping
   excludes); (c) `\rho` — zero hits, so the new symbol overloads nothing. Check (b) was initially run
   only over `chapters/` without comment stripping; the tree-wide comment-stripped rerun (this
   session, after the first draft of this document) is what closes the item. The renumbering from the
   reorder is therefore contained entirely within the chapter and resolved by `\ref` automatically.


---

<!-- estado-rodada -->
> **Rodada encerrada · último toque 2026-08-03 · sem autoridade.**
> Este ficheiro é registo de proveniência do que foi discutido nesta passagem, não fonte
> de um facto corrente. O que ficou decidido está em [`VEREDITOS.md`](../../../VEREDITOS.md);
> os valores entregues estão em `CLAUDE.md` §0.1. Não copie nada daqui sem confirmar lá.
