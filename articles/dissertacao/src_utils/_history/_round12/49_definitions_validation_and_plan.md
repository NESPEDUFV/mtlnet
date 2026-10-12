# 49_definitions_validation_and_plan.md — adversarial validation of the consolidated design, and the update outline

Round 12, 2026-08-03. SECOND PASS: this document validates `_history/_round12/47_definitions_consolidated.md`
(the design) against the live tree and then outlines the edits. NO `.tex` file and NO probe file was
edited. Every claim below cites the file and line read this session. The design's own claims were
treated as claims to check, not facts to inherit; every graph, grep, and probe decision below was
reconstructed independently.

Files read this session (all under `articles/dissertacao/` unless noted):

- `src_utils/_history/_round12/47_definitions_consolidated.md` (the design), `46_definition_dependency_audit.md`,
  `48_history_formulation_literature.md`
- `src/chapters/2_fundamentals.tex` (1521 lines; definitions at 71, 80, 116, 126, 133, 167, 434, 461,
  678, 684, 693, 887 — re-derived by grep, matches audit 46's table exactly)
- `src/chapters/3_cbic/method.tex` (:15,:17,:53-54,:58,:64-65), `src/chapters/4_courb/methodology.tex`
  (:12,:17,:89-95,:99-134,:144-153), `src/chapters/5_mobiwac/03_problem.tex` (:12),
  `src/chapters/5_mobiwac/04_method.tex` (:15-33), `src/chapters/5_mobiwac/05_setup.tex` (:28)
- `src/chapters/apx_b_static_scope.tex` (:7-50), `src/preamble.tex` (:117)
- `src_utils/check_audit_claims.py` (full PROBES tuple parsed mechanically: 93 string probes, 21 with
  target `chapters/2_fundamentals.tex`; `live_text`/`strip_text` at :614-658; matcher at :701,
  `re.search(pat, live_text(path), re.I)` on whitespace-normalized comment-stripped text;
  `probe_root` self-test at :681 confirms `.tex` probes resolve under `src/`)
- `GLOSSARY.md` §1 and §1.1 (:35-60), `src_utils/PENDENCIAS.md` §6.13 and §6.14

Verdict in one line: **the design's ordering, layering, and probe claims hold; its factorization holds
for all three studies as mathematics; but the factorization REMARK as worded in design §5 D5 carries
two misstatements (Chapter 5's instantiation is incomplete, and "every predictive model" over-quantifies
into the static task) and one D2 annotation is false of Chapter 5 (padding). These must be fixed in the
application pass; none invalidates the design's structure.**

---

## PART A — adversarial validation

### A.1 Dependency order — VERIFIED

The graph was rebuilt from the design's §5 statements, symbol by symbol, not copied from its §1 table.
Providers, under the proposed order:

| Object | Introduces | Consumes | Provider position |
|---|---|---|---|
| notation prose | $\mathcal{U},\mathcal{P},\mathcal{C},\mathcal{R}$; $c_p$, $r_p$ | — | before all |
| D1 Check-in | $x_i, p_i, t_i, c_i, r_i$ | $\mathcal{P}$, $c_p$, $r_p$ | prose |
| D2 History | $H_i$, $\ell$ | $x_i$ | D1 |
| D3 Place embedding | $\mathbf{e}_p$ | $p\in\mathcal{P}$ | prose |
| D4 Check-in-level repr. | $\mathbf{e}_{x_i}$ | $x_i$ | D1 |
| D5 Representation map | $\rho$, $d$ | $x_i$, $H_i$, $\ell$; remark: $\mathbf{e}_p$, $\mathbf{e}_{x_i}$, $p_j$ | D1, D2, D3, D4 |
| D6 Category classification | $g_{\mathrm{cat}}$ | $\mathbf{e}_p$, $c_p$ | D3, prose |
| D7 Next-category | $f_{\mathrm{cat}}$ | $H_i$, $c_i$ | D2, D1 |
| D8 Next-region | $f_{\mathrm{reg}}$ | $H_i$, $r_i$ | D2, D1 |
| D9 Next-place | $f_{\mathrm{place}}$ | $H_i$, $p_i$ | D2, D1 |
| D10, D11 | topology names | none formal | — |
| D12 Negative transfer | phenomenon name | "dedicated single-task model" | GLOSSARY §2 (`GLOSSARY.md:60`, row confirmed present) |
| D13 Gradient conflict | $\mathbf{g}_i$, $\varphi_{ij}$ (own "Let") | shared parameters | D10 |

Every edge points strictly backward (to a lower position or to the notation prose). A linear order
whose every edge points backward is by construction acyclic and is its own topological order. The
single forward edge of the CURRENT text (2.3 at `2_fundamentals.tex:116-124` consuming $\mathbf{e}_p$
introduced at `:434-437` — re-confirmed by reading both spans this session) is removed by moving D3/D4
ahead of the tasks, and no new forward edge appears. The design's order realizes the graph. VERIFIED.

One prose-consistency note (not a dependency defect): §2.1 opens "This section defines the prediction
targets before reviewing the methods used for them" (`2_fundamentals.tex:26-27`). After the move, §2.1
also defines two representations and a map before the targets. The sentence remains literally true
(representations are not "methods reviewed"), but the author should see the new §2.1 shape — task
section now hosting representation definitions — when he signs off. Listed under author decisions.

### A.2 Well-formedness, per definition — VERIFIED (with the binding checks re-run)

- **$c_p$ is genuinely free today.** Comment-stripped chapter (via the same stripper discipline the
  gate uses): $c_p$ occurs exactly ONCE in live text, inside Definition 2.3's equation
  ($g_{\mathrm{cat}}(\mathbf{e}_p)\longrightarrow c_p$, stripped-line 68 / raw `:119`), with no prior
  introduction. Confirmed free. The proposed binding sentence ("Each POI $p\in\mathcal{P}$ carries a
  category $c_p\in\mathcal{C}$ and lies in a region $r_p\in\mathcal{R}$") is correct for the data:
  the category is a per-POI attribute (`3_cbic/method.tex:54`: "$c$ is the POI's ground-truth
  category"; the seven-class taxonomy is per place), and the region is a per-place attribute
  (`5_mobiwac/03_problem.tex:12`: "its \emph{region}, the place's census tract"). GLOSSARY §1.1's
  $g_{\mathrm{cat}}$ row already reads "whose target is the category $c_p$ of POI $p$"
  (`GLOSSARY.md:41` region of §1.1) — the registry anticipated the binding, as the design says.
- **$r_p$**: occurs ZERO times in live chapter text today (comment-stripped grep, this session), so
  binding it introduces a genuinely new symbol and overloads nothing.
- **D1's change** ($c_i=c_{p_i}$, $r_i=r_{p_i}$): faithful to the data (above) and loses no
  information, since the attribute maps' codomains are stated in the binding sentence. The current
  wording being replaced was read at `2_fundamentals.tex:76-77`.
- All other statements: free-symbol scan done per definition against the design's §5 texts. D2 binds
  $\ell$; D5's domain/codomain are explicit; D13 binds its symbols with its own "Let". The $i,j$
  task-versus-check-in overloading in D13 is real, is live today (`:887-896`), and the design flags
  it without changing it — acceptable, the two uses never co-occur in one formula.
- The design's internal annotations carry one small tension (D3's note says the codomain is
  "deliberately implicit"; D6's note says "domain $\mathbb{R}^d$"): annotations only, no chapter text
  is affected, noted for the record.

### A.3 The factorization claim — VERIFIED AS MATHEMATICS; the REMARK wording carries two defects

Tested against the three method chapters, read this session:

- **Chapter 3 instantiates $\rho$ at the place level.** `3_cbic/method.tex:53`: "Each POI is
  represented by its 64-dimensional DGI embedding $\mathbf{e}\!\in\!\mathbb{R}^{64}$." `:64`: "The
  input is the concatenation of the 64-dimensional embeddings of $p_1$--$p_9$, yielding a
  $9\!\times\!64=576$-dim vector." Position $j$ carries a function of $p_j$ alone:
  $\rho(x_j)=\mathbf{e}_{p_j}$. HOLDS.
- **Chapter 4 instantiates $\rho$ per check-in with mixed channels.** `4_courb/methodology.tex:95`:
  "Each check-in in the window is represented by the corresponding embedding, resulting in an input
  of $9 \times 192 = 1728$ dimensions"; `:93`: $\mathbf{E}_{cat} = [\mathbf{E}_{HGI} \|
  \mathbf{E}_{loc} \| \mathbf{E}_{time}]$. The temporal channel is per visit: `:144` "map the
  temporal values of each check-in (hour of day and day of week...)"; `:153` "the embedding
  $\mathbf{E}_{time} \in \mathbb{R}^{64}$, which represents the timestamp of each check-in." Every
  channel is a deterministic function of fields of the check-in tuple ($p_j$ for HGI, the coordinates
  of $p_j$ for loc, $t_j$ for time), so $\rho(x_j)$ is well defined on check-ins. HOLDS.
- **Chapter 5 instantiates $\rho$ at the check-in level — but on TWO streams.**
  `5_mobiwac/04_method.tex:22`: "we extract one 64-dimensional vector per check-in ... so a model
  sees a sequence of per-visit vectors rather than repeated per-place ones"; `:27`: "The category
  task reads the window of per-visit vectors (the semantic stream); the region task reads the same
  window of visits, each visit now represented by the trained vector of its region node from the same
  graph (the spatial stream)." Both streams are elementwise functions of the check-in (the second
  through $x_i \mapsto r_i \mapsto$ region-node vector), so a vector-valued
  $\rho(x_i) = (\mathbf{e}_{x_i}, \mathbf{e}^{\mathrm{reg}}_{r_i})$ satisfies the factorization.
  HOLDS as mathematics.

**DEFECT F-1 (the important finding).** The design's remark text (§5 D5) says "Chapter 5 instantiates
it at the check-in level, $\rho(x_i) = \mathbf{e}_{x_i}$" — full stop. That equation describes the
semantic stream only. The joint model's region task reads region-node vectors
(`5_mobiwac/04_method.tex:27`, quoted above), which are per REGION, not per visit: two visits to the
same region carry the same spatial vector. Applied verbatim, Chapter 2 would misstate the final
study's input in exactly the shape the design itself criticizes at `2_fundamentals.tex:472-474` for
Chapter 4. The fix is one clause (see Part B, step 3), and the underlying design (raw $H_i$ + named
$\rho$) is untouched by it. Note the symmetry the design missed: Chapter 5's input is itself hybrid —
per-visit on one stream, per-region on the other — so whatever ruling the author gives on PENDENCIAS
6.14 decision 2 for Chapter 4 should be checked for the analogous Chapter 5 sentence.

**DEFECT F-2 (quantifier).** The remark says "every predictive model in this dissertation reads
$\rho(H_i)$ rather than $H_i$ itself." The static classifier $g_{\mathrm{cat}}$ is a predictive model
of this dissertation and reads $\mathbf{e}_p$, never a history (`2_fundamentals.tex:116-124`;
`4_courb/methodology.tex:93` pairs $(\mathbf{E}_{cat}, c)$ per POI). The sentence must be scoped to
the sequential tasks (e.g., "every model of the sequential tasks in this dissertation reads
$\rho(H_i)$ rather than $H_i$ itself"). Without the scope, the remark drags the static task toward a
sequential reading — the exact failure A.4 guards.

**Minor F-3.** "the three studies hold the tasks fixed while they vary $\rho$": the studied task PAIR
changes at Chapter 5 (catclf+nextcat → nextcat+nextreg; `2_fundamentals.tex:140-142` states the
pairing). Say "hold the task definitions fixed" — the definitions are the fixed objects; which pair
each study runs is stated three definitions earlier.

**The three PENDENCIAS 6.14 decision-2 options, each tested against the factorization:**

1. **Call Chapter 4 hybrid.** Factorization TRUE ($\rho(x_j)$ is still an elementwise function of the
   check-in). The remark's clause "Chapters 3 and 4 instantiate $\rho$ at the place level" must be
   REWORDED (e.g., "Chapter 3 instantiates $\rho$ at the place level; Chapter 4 concatenates two
   per-place channels with a per-visit temporal channel"), and `2_fundamentals.tex:473-474` ("while
   retaining a place-level input") must change.
2. **Keep "place-level" with a one-sentence caveat.** Factorization TRUE. The remark keeps its clause
   and gains the caveat sentence naming the temporal channel as the exception; `:473-474` gains the
   same caveat.
3. **Keep as is.** Factorization TRUE. The remark works as the design wrote it (its §3 bullet already
   carries the parenthetical "and, in Chapter 4, of the visit's timestamp through the temporal
   encoder"); `:473-474` is unchanged.

So: the factorization itself is TRUE under all three options; options 1 and 2 require rewording of
the D5 remark and of `:472-474`; option 3 requires none. Under every option, DEFECTS F-1 and F-2
still need their fixes — they are independent of this decision.

### A.4 The static task — VERIFIED

D6 is quantified over POIs: input $\mathbf{e}_p$, target $c_p$, no check-in index in the statement
(design §5 D6, statement unchanged from `2_fundamentals.tex:116-124`). The design's §4 explicitly
rejects $\mathbf{e}_{p_i}$ there, with the correct reason. `apx_b_static_scope.tex:11-12` defines the
static task as "classify the category of a place from that place's own representation," and the
design preserves exactly that shape. The only threat to the static task in the whole design is the
over-quantified remark of DEFECT F-2, whose fix is specified above. With that fix, VERIFIED.

### A.5 Notation collisions — VERIFIED, with one registry note the design lacks

Re-measured tree-wide (all `.tex` under `src/`, excluding `build/`, comments stripped with the same
trailing-`%` discipline as the gate's stripper), this session:

- **$\rho$: ZERO occurrences anywhere** — frame chapters, paper chapters, appendices, tables,
  preamble. The design's claim ("zero times in the live frame tree") holds, and stronger: zero in the
  whole live tree. VERIFIED.
- **`def:fund:` outside `2_fundamentals.tex`: ZERO** live occurrences. Renumbering is contained.
- **Literal "Definition 2.N" / "Definição 2.N" in live prose: ZERO** tree-wide. The four raw-file
  hits (`2_fundamentals.tex:55-56,:160,:445,:452`) are all comment lines — verified by reading them.
- **$d$ is NOT tree-wide virgin, but nothing collides.** Chapter 2 live text today contains no
  standalone $d$, no $\mathbb{R}^d$ (grep over the stripped file: zero hits). The paper chapters DO
  use the letter: `3_cbic/method.tex:17` "$h_i \in \mathbb{R}^{d}$, where $d$ is the dimension of the
  output" (same meaning: an embedding dimension); `:15` $d_{ij}$ = geodesic distance; `:58` and
  `4_courb/methodology.tex:17,:132` $d_{\mathrm{shared}}$ = shared latent dimension;
  `4_courb/methodology.tex:144-151` uses $D$ for the Time2Vec dimension. No day-of-week $d$ anywhere.
  The subscripted forms ($d_{ij}$, $d_{\mathrm{shared}}$) are distinct symbols; the bare $d$ of
  `3_cbic/method.tex:17` means the same thing Chapter 2's $d$ will mean. No contradiction — but the
  design's §8 $d$-row should carry a scope note ("chapter-local; Chapter 3 uses $d$ for its GAT
  output dimension and $d_{ij}$ for geodesic distance"), because the row as proposed implies the
  letter is unclaimed. Registry note, not a defect.
- **$\mathbf{e}_{p_i}$ / $\mathbf{e}_{p_j}$: ZERO** live occurrences tree-wide — the design's "breaks
  nothing" claim for the composed form holds.

### A.6 Probe survival — VERIFIED: ZERO probes break

The PROBES tuple was parsed mechanically from `src_utils/check_audit_claims.py` this session: 93
string probes, of which exactly **21** target `chapters/2_fundamentals.tex` (matching the count the
author verified). The matcher is `re.search(pattern, live_text(path), re.I)` where `live_text`
comment-strips and whitespace-normalizes the WHOLE file into one string (`:614-658,:701`) — so every
probe is file-scoped, insensitive to line position and line wrapping. Each of the 21, decided against
the PROPOSED text:

| Probe | want | Decision under the design |
|---|---|---|
| COD-015d `relative multi-task performance` | absent | SURVIVES — design adds no such phrase |
| A23-R3 `limit on what any of these methods can contribute` | absent | SURVIVES — §2.3 untouched |
| A23-EX9 `corresponding loss vectors form the Pareto front` | present | SURVIVES — §2.3 untouched (`:732`) |
| R9-pareto `claims no Pareto property` | present | SURVIVES (`:850`) |
| R9-pareto2 `Pareto dominance` | present | SURVIVES (`:730`) |
| R9-pareto3 `Pareto optimal when no other setting dominates` | present | SURVIVES (`:731`) |
| R9-conflict `cosine between their gradients` | present | SURVIVES — D13 unchanged (`:898`) |
| R9-nocount `indistinguishable from orthogonal on ...` | absent | SURVIVES — nothing reintroduced |
| R10-cosine `def:fund:conflict` | present | SURVIVES — label and `:1040` ref unchanged |
| R10-novelty `none treats next category and next region as` | present | SURVIVES (`:1094`) |
| R10-hamtl `HAMTL sets location prediction...auxiliary task` | present | SURVIVES (`:1084`) |
| R11-aligned `condition number of the linear system of task gradients` | present | SURVIVES (`:1059`) |
| R11-aligned2 `adjusts the principal components of the gradient system` | absent | SURVIVES |
| R11-def27 `\label{def:fund:checkinlevel}` | present | SURVIVES — the label MOVES with D4 but stays in this file; probe is file-scoped |
| R11-hgi `repurposes that POI-level output for sequential prediction...` | present | SURVIVES (`:292`, §2.2 narrative kept) |
| R12-dwa `Dynamic Weight Average alongside their attention architecture` | present | SURVIVES (`:1031`) |
| R12-dwa2 `dynamic weight averaging` | absent | SURVIVES |
| R12-dwa3 `rate of change of that task's loss, measured as the ratio...` | present | SURVIVES (`:1032`) |
| R12-eqxi `assigns one vector $\mathbf{e}_{x_i}$ to each check-in` | present | SURVIVES ONLY IF the application pass carries D4's sentence character-for-character (design marks it VERBATIM; whitespace normalization tolerates re-wrapping but not rewording) |
| R12-fplace `f_{\mathrm{place}}(H_i)\longrightarrow p_i` | present | SURVIVES — D9 equation unchanged (`:170`); note the pattern has NO space around `\longrightarrow`, so the equation must keep its current spacing shape |
| R12-fplace2 `no chapter reports a result for $f_{\mathrm{place}}$` | present | SURVIVES — exclusion stays inside D9 (`:172-173`) |

**Probes that break: NONE.** The design's claim is confirmed by independent enumeration, with the
same standing obligation the design states: the three R12 pinned wordings (and the
`def:fund:checkinlevel` label) travel verbatim. The preamble probe (`check_audit_claims.py:405`,
`\newtheorem{definition}{Definition}[chapter]` in `preamble.tex:117`) is untouched.

### A.7 Glossary consistency — VERIFIED, with one row-content caveat

`GLOSSARY.md` §1.1 read this session (rows: sets; $x_i$; $H_i$; $\mathbf{e}_p$; $g_{\mathrm{cat}}$;
$f_{\mathrm{cat}}/f_{\mathrm{reg}}$).

- **Proposed $\rho$ row**: matches D5's statement; unoccupied (A.5). Consistent. Its Notes clause
  "Every model of this dissertation reads $\rho(H_i)$" inherits DEFECT F-2 — scope it to the
  sequential tasks in the row too.
- **Proposed $d$ row**: consistent, but "64 in Chapters 3 and 5" describes only the semantic stream
  of Chapter 5 (DEFECT F-1's ripple: the joint model's per-visit input is two 64-d streams,
  `5_mobiwac/04_method.tex:27`). The row should say "64 per stream in Chapter 5" or defer to the
  chapter. Plus the chapter-local scope note from A.5.
- **Amendment to $\mathbf{e}_p$ row** ("at history position $j$ ... $\mathbf{e}_{p_j}$"): does not
  contradict the existing row ("Static-task input; distinct from a per-visit Check2HGI vector",
  `GLOSSARY.md` §1.1) — it extends it. Consistent.
- **Amendment to $x_i$ row** ($c_i=c_{p_i}$, $r_i=r_{p_i}$): consistent with the existing Notes ("A
  category or region may be used as a target rather than as an observed input") — attribute origin
  and target role are orthogonal facts. Consistent.
- **No row treated as registered**: confirmed. The design's §8 header says PROPOSED; the two
  PENDENCIAS §6.13 rows ($\mathbf{e}_{x_i}$, $f_{\mathrm{place}}(H_i)$) are consumed as pending, and
  §6.13 confirms they are still awaiting the author's ruling. The design's compatibility statement
  with §6.13's options 1/2/3 is accurate as read against `PENDENCIAS.md` §6.13.

### A.8 One defect outside the seven items, found while checking D2's annotations

**DEFECT F-4.** The design's D2 note claims "the studies handle shorter prefixes by zero-padding
(`3_cbic/method.tex:65`, `4_courb/methodology.tex:95`)". True for Chapters 3 and 4 (both lines
verified). FALSE for Chapter 5: `5_mobiwac/05_setup.tex:28` — "every start position within the last
nine visits yields a shorter, padded window whose target is the same final visit; **we keep only the
full-length window ending there and drop these padded duplicates**." Chapter 5 DROPS padded windows.
This also CLOSES the design's UNFINISHED item 5 (it asked exactly for this check). Consequence for
the application pass: any padding remark written near D2 must be scoped to Chapters 3 and 4, or
dropped; it must not claim padding for "the studies."

### Part A verdict table

| Item | Verdict |
|---|---|
| 1. Dependency order | VERIFIED (graph rebuilt; acyclic; order realizes it) |
| 2. Well-formedness | VERIFIED ($c_p$ free today, binding correct for the data; $r_p$ unused today) |
| 3. Factorization | VERIFIED as mathematics for all three studies; DEFECTS F-1, F-2, F-3 in the remark's wording |
| 4. Static task | VERIFIED (conditional on the F-2 scope fix) |
| 5. Notation collisions | VERIFIED ($\rho$ virgin tree-wide; $d$ non-colliding but not virgin — registry note needed) |
| 6. Probe survival | VERIFIED — zero of 21 break, three verbatim strings obligatory |
| 7. Glossary consistency | VERIFIED (with the $d$-row and $\rho$-row Notes caveats) |

### Defect register (all in the design document, none in the live chapter beyond what the design already fixes)

- **F-1 (moderate).** D5 remark's Chapter 5 instantiation "$\rho(x_i)=\mathbf{e}_{x_i}$" omits the
  region stream (per-region vectors, `5_mobiwac/04_method.tex:27`); applied verbatim it misstates the
  final study's input. Fix: one clause (Part B step 3).
- **F-2 (moderate).** "every predictive model in this dissertation reads $\rho(H_i)$" over-quantifies
  into the static task. Fix: scope to the sequential tasks (chapter text AND proposed $\rho$ registry
  row).
- **F-3 (minor).** "hold the tasks fixed" → "hold the task definitions fixed" (the studied pair
  changes at Chapter 5).
- **F-4 (minor, closes design UNFINISHED 5).** Zero-padding is a Chapters-3-and-4 device only;
  Chapter 5 drops padded windows (`5_mobiwac/05_setup.tex:28`). Scope any padding prose accordingly.
- **F-5 (registry note).** $d$ is not unclaimed tree-wide (`3_cbic/method.tex:15,:17,:58`;
  `4_courb/methodology.tex:17,:132`); the proposed $d$ row needs a chapter-local scope note. No live
  collision.

---

## PART B — the update outline

Ordered edit plan. Steps 1-2 land green alone; **steps 3-5 must land in ONE commit** (moving a
definition out of §2.2 without inserting it in §2.1, or vice versa, either duplicates the labels
`def:fund:placelevel`/`def:fund:checkinlevel` (LaTeX multiply-defined-label warnings, and two rendered
definitions with one number sequence) or orphans the §2.2 back-references). Steps 6-8 land after.

**Blocking preconditions (author, before any edit):** decisions AD-1 through AD-4 below. Steps 1-2 are
decision-independent and may land first.

### Step 1 — `src/chapters/2_fundamentals.tex` (notation prose, after line 69)

Append to the notation sentence at `:68-69` ("Let $\mathcal{U}$, ... region classes."):

```
Each POI $p\in\mathcal{P}$ carries a category $c_p\in\mathcal{C}$ and lies in a region
$r_p\in\mathcal{R}$.
```

Why: binds $c_p$ (free today, A.2) and $r_p$ before D1 consumes them.

### Step 2 — same file, Definition `def:fund:checkin` (lines 76-77)

Replace exactly:

```
where $p_i\in\mathcal{P}$ is the visited POI, $t_i$ is its timestamp,
$c_i\in\mathcal{C}$ is its category, and $r_i\in\mathcal{R}$ is its region.
```

with:

```
where $p_i\in\mathcal{P}$ is the visited POI, $t_i$ is its timestamp,
$c_i=c_{p_i}$ is its category, and $r_i=r_{p_i}$ is its region.
```

Why: states that a check-in's category and region are the visited POI's attributes; makes
$\mathbf{e}_{p_j}$ well typed. No probe pins this span.

### Step 3 — same file, insert the new subsubsection (between the ledger comment ending at :109 and `\subsubsection{The three experimental tasks}` at :111)

Content, in order (head name is the author's; working head "Representations of a check-in"):

1. The moved Definition `def:fund:placelevel` — the environment at `:434-437` VERBATIM ("A place
   embedding assigns one vector $\mathbf{e}_p$ to each POI $p$, so every check-in at that POI enters
   the model with the same representation."), with its ROUND-11 provenance comment block moved along.
2. The moved Definition `def:fund:checkinlevel` — the environment at `:461-465` VERBATIM, including
   the probe-pinned sentence character-for-character: "A check-in-level representation assigns one
   vector $\mathbf{e}_{x_i}$ to each check-in $x_i$, so two visits to the same POI may enter the
   model with different representations." (`R12-eqxi`, `R11-def27`.) Provenance comment moves with it.
3. The representation map — as numbered Definition D5 `\label{def:fund:repmap}` OR as a displayed
   equation in prose, per AD-1:

```
A representation map assigns to each check-in a vector,
\begin{equation}
    \rho(x_i)\in\mathbb{R}^{d},
\end{equation}
and extends to histories elementwise,
\begin{equation}
    \rho(H_i)=\bigl(\rho(x_{i-\ell}),\ldots,\rho(x_{i-1})\bigr).
\end{equation}
```

4. The factorization remark, CORRECTED for F-1/F-2/F-3 (final wording subject to AD-2/AD-3; the
   corrected skeleton):

```
Every model of the sequential tasks in this dissertation reads $\rho(H_i)$ rather than
$H_i$ itself. Chapter~\ref{ch:cbic} instantiates $\rho$ at the place level,
$\rho(x_j)=\mathbf{e}_{p_j}$; Chapter~\ref{ch:courb} concatenates spatial, temporal, and
categorical components per check-in [wording per AD-2]; Chapter~\ref{ch:mobiwac}
instantiates it at the check-in level, reading per-visit vectors,
$\rho(x_i)=\mathbf{e}_{x_i}$ for the category stream, with the region stream carrying the
trained vector of the visit's region node [wording per AD-3]. The three studies hold the
task definitions fixed and vary $\rho$.
```

No padding remark here; if one is wanted near D2 it must be scoped per F-4.

### Step 4 — same file, §2.2 recall sites (same commit as step 3)

- At `:434-437`: remove the moved `def:fund:placelevel` environment; the limitation paragraph
  (`:439-444`) STAYS and already points via `\ref{def:fund:placelevel}` — now a backward reference.
  Adjust its lead-in only if the removal leaves the "The move from HGI to Check2HGI begins..."
  sentence (`:422-423`) dangling; minimal bridge prose, author-approved.
- At `:461-465`: remove the moved `def:fund:checkinlevel` environment; `:467` ("Check2HGI reaches the
  check-in level of Definition~\ref{def:fund:checkinlevel}...") STAYS, now backward.

### Step 5 — same file, `:472-474` (same commit; content per AD-2)

Current: "The second study supplies that context through separate encoders while retaining a
place-level input." Under AD-2 option 1: reword to the hybrid form. Option 2: keep and append the
one-sentence temporal-channel caveat. Option 3: unchanged.

### Step 6 — `GLOSSARY.md` §1.1 (AUTHOR'S HAND, not an agent edit)

Rows and amendments from design §8, with the Part A corrections: the $\rho$ row's Notes scoped to
sequential tasks (F-2); the $d$ row with "64 per stream in Chapter 5" and the chapter-local scope note
(F-1 ripple, F-5). Prerequisite: the two §6.13 rows per the author's §6.13 ruling.

### Step 7 — `src_utils/check_audit_claims.py`: probes to ADD (none to repin)

No existing probe needs repinning (A.6). New content deserves pins; proposed:

```
("R12-repmap",  "Ch.2 introduces the representation map over histories elementwise",
 "chapters/2_fundamentals.tex", r"extends to histories elementwise", True),
("R12-cpbind",  "Ch.2 notation prose binds the per-POI attributes c_p and r_p",
 "chapters/2_fundamentals.tex", r"carries a category \$c_p\\in\\mathcal\{C\}\$ and lies in a region", True),
("R12-cieq",    "Definition Check-in states c_i = c_{p_i}",
 "chapters/2_fundamentals.tex", r"c_i=c_\{p_i\}\$ is its category", True),
```

(Patterns written against the step-1/2/3 texts above; re-derive them from the text as actually landed
before committing.) **Each new probe requires sabotage validation:** mutate the target string in the
source, run the gate, READ THE RESULT (the exit code and the probe's own row, not the known-good
lines) BEFORE restoring, and when restoring replace ALL occurrences of the mutated string — a count=1
replace against a string that also appears in a provenance comment is a known false-pass in this
repository (CLAUDE.md read-first block; the comments quote pinned strings).

### Step 8 — cross-reference and gate sweep after the move

Renumbering is automatic (`\begin{definition}` order; `\newtheorem{definition}{Definition}[chapter]`,
`preamble.tex:117`). Verified clean already, re-run after landing, from `src/`:

```
cd src && for f in $(find . -name "*.tex" -not -path "./build/*"); do \
  grep -v '^[[:space:]]*%' "$f" | grep -nE 'Definition[~ ]2\.[0-9]|Defini..o[~ ]2\.[0-9]|def:fund:' \
  | sed "s|^|$f:|"; done
```

Expect: `def:fund:` hits only inside `2_fundamentals.tex` (today: refs at `:140,:141,:142,:439,:467,
:690,:720,:1040` plus the label lines, all in-file; zero literal "Definition 2.N" in live prose
anywhere). Then `make` (green build) and `python3 src_utils/check_audit_claims.py` reading the EXIT
CODE, not the output prose. Total: **8 steps** (steps 3-5 one commit).

### Author decisions required before landing (AD-)

1. **AD-1 (= PENDENCIAS 6.14 decision 1).** Twelve definitions or thirteen: $\rho$ as numbered
   Definition or as displayed equation in prose. Both fully specified; the plan is identical either
   way.
2. **AD-2 (= PENDENCIAS 6.14 decision 2).** How Chapter 2 names Chapter 4's input (hybrid / caveat /
   as-is). Factorization true under all three (A.3); options 1-2 change the D5 remark and `:472-474`.
3. **AD-3 (NEW, from DEFECT F-1).** How the D5 remark states Chapter 5's two-stream input: the
   corrected clause in step 3, or a shorter "instantiates $\rho$ at the check-in level" with the
   streams deferred to Chapter 5. Adjacent to AD-2 — the same place-versus-visit boundary, at the
   region stream.
4. **AD-4 (NEW, from A.1).** Sign-off on the §2.1 shape: the tasks section now hosts the
   representation definitions in a new subsubsection, whose head the author names.
5. **AD-5 (prerequisite, = PENDENCIAS 6.13).** The two registry rows ($\mathbf{e}_{x_i}$,
   $f_{\mathrm{place}}(H_i)$). Under §6.13 option 3 (withdraw both), D4 and D9 revert and this plan's
   steps 3-5 need re-scoping, as the design itself states.
6. **AD-6 (carried from design UNFINISHED 3).** The withholding sentence in D2 — keep or sharpen;
   plan carries it unchanged.

### UNFINISHED

None. All seven Part A items were checked against sources read this session; the design's UNFINISHED
item 5 (MobiWac padding) is closed by DEFECT F-4 with the citation.


---

<!-- estado-rodada -->
> **Rodada encerrada · último toque 2026-08-03 · sem autoridade.**
> Este ficheiro é registo de proveniência do que foi discutido nesta passagem, não fonte
> de um facto corrente. O que ficou decidido está em [`VEREDITOS.md`](../../../VEREDITOS.md);
> os valores entregues estão em `CLAUDE.md` §0.1. Não copie nada daqui sem confirmar lá.
