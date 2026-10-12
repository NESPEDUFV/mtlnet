# 10 · MTL expert — round 9 audit (fresh eyes, cold read)

- **Persona:** `reviewers/10_mtl_expert.md` (multi-task learning domain reviewer; default prior = a tuned
  fixed-weight scalarization matches specialized MTL optimizers).
- **Build commit:** `901a0408`
- **Date:** 2026-07-30 (audit window opened 08:41 −03:00, findings written by 08:54, self-correction of
  this report's own count claims to 08:57; 30 min checkpoint honored with time to spare. The end time is
  the last `date` I ran, not a projection.)
- **Scope as assigned:** Ch.2 §2.3 in `chapters/2_fundamentals.tex` (with priority on the ~106 lines added
  today, L419–558, covering the total-loss objective, Pareto dominance/optimality/stationarity, and
  per-method guarantee levels), then the MTL claims of `chapters/3_cbic/` and `chapters/5_mobiwac/`.
- **What I actually read (source, not PDF):** `chapters/2_fundamentals.tex` L360–640 and L860–884;
  `chapters/apx_f_cosine.tex` L85–100, L282–345; `chapters/3_cbic.tex` L20–40; `chapters/3_cbic/method.tex`
  L12–252, `intro.tex` L22–32, `conclusion.tex` L12–23, `basis.tex` L31–65; `chapters/5_mobiwac/02_related.tex`
  L100–170, `04_method.tex` L33–44, `05_setup.tex` L32, `06_results.tex` L20; `src/references.bib` (the 15
  MTL keys cited in §2.3); `AGENT_GUARDRAILS.md` §1–§4b, `WRITING_LAW.md` (full), `GLOSSARY.md` §§1–7 headers.
  I did **not** open the built PDFs; every finding below is a source-tree location.
- **External records opened this session** (arXiv PDFs downloaded to `/tmp/mtlpdf/`, text extracted and
  searched with `pypdfium2`; page numbers are PDF pages of the version fetched):
  `2202.01017` (Nash-MTL, 19 pp), `2110.14048` (CAGrad, 20 pp), `2305.19000` (Aligned-MTL, 16 pp),
  `2001.06782` (PCGrad, 27 pp), `1810.04650` (MGDA/Sener-Koltun, 15 pp).
- **Commands run:**
  - `date`; `git log -1 --format='%H %ci'` (confirms `901a0408bdb2e8f795c399022611d76349b0fbec`, 2026-07-30 06:08:34 −0300)
  - `ls`, `wc -l`, `sed -n`, `awk 'NR>=a && NR<=b'`, `grep -n`, `grep -rn` over the files listed above
  - `curl -sL -o <name>.pdf https://arxiv.org/pdf/<id>` for the five arXiv ids above
  - `pypdfium2` page-by-page `get_text_range()` + `re.finditer` over the five extractions
  - **No build, no `make check`, no `make selftest`** (instructed; the tree was left untouched apart from
    this report file).

**Overall verdict for the MTL content: sound-with-corrections.** The new Pareto passage is the most
carefully sourced MTL prose in the volume, and every guarantee it states is traceable to a real theorem in
a real paper. Of the five methods the previous wave named, two are attributed cleanly end to end (Sener and
Koltun, and Aligned-MTL), one carries a blocker (PCGrad, finding 2: it is said to lack a property that a
paper cited in the same paragraph attributes to it), and two carry should-fix defects rather than errors of
fact (CAGrad's stated guarantee is the weaker of its two and is missing its precondition, finding 4;
Nash-MTL's own theorems are read correctly but one clause in the same sentence is cited to it that its paper
never states, finding 5).

A tally, since the per-clause and per-method counts differ and the difference matters. Seven distinct
guarantee or definition clauses live at `:431-448`. Six of the seven verified as written: Nash-MTL's
Pareto-stationarity definition and its Theorem 5.4/5.5 pair, CAGrad's fixed-point clause (true, but
incomplete), PCGrad's Theorem 2 inequality, the Sener-Koltun dominance/optimality/front definitions, and
the Aligned-MTL clause. One did not: PCGrad's "no Pareto claim at all". The single blocker is fixable in one
sentence.

> **REVIEW CORRECTION, 2026-07-30.** My first submission of this report filed **two** blockers and
> recommended an errata against published Ch.3 text. A reviewer caught both, and both were wrong:
> - **Finding 1 (Aligned-MTL) is WITHDRAWN.** I convicted the chapter on the paper's abstract without
>   opening pp12-13, where its theorems live; my search capped at six hits and never reached them. p12
>   Theorem 2 states exactly what the chapter says. The dissertation's ledger comment had cited those pages
>   correctly and I overrode it.
> - **The MGDA half of finding 8 is WITHDRAWN.** I claimed Sener and Koltun do not assert Pareto-set
>   convergence for MGDA when my own extraction of their p2 says they do.
> Both were errors in the same direction, against the text and against a ledger that was right, which is
> the direction a fresh-eyes auditor is most prone to and least entitled to. Counts below are corrected;
> the withdrawn recommendations must not be acted on.

---

## FINDINGS

### 1. WITHDRAWN (was BLOCKER) — the Aligned-MTL clause is correct; it is what the paper's own convergence section states. Residual nit only.

> **CORRECTION, 2026-07-30, after review.** I filed this as a blocker on the strength of the p1 abstract and
> the p2 marketing contrast. That was wrong, and it was wrong for a reason worth recording: my regex search
> over the PDF capped at six hits and returned only pp1, 2, 4, 5, so **I never opened pp12-13, where the
> paper's actual theorems live** — the very pages the dissertation's own ledger comment at `:467` names
> ("theorems pp12-13, 'converges linearly to a Pareto-stationary point' with pre-defined task weights").
> The ledger was right and I convicted it on an abstract. Having now read those pages:
> arXiv:2305.19000 p12, Convergence Analysis synopsis: "Our approach converges to a Pareto-stationary point
> with pre-defined tasks weights, thus providing more control over an optimization result." p12 Theorem 2:
> "A gradient descent with an aligned gradient and a step size α ≤ 1/Λ converges linearly to a
> Pareto-stationary point where ∇L0(θ) = 0." p5 likewise: "our MTL approach converges to a Pareto-stationary
> solution."
> The chapter's clause at `:440-441` ("Aligned-MTL converges to such a point for task weights fixed in
> advance") is therefore an accurate report of the paper's own stated guarantee, and the paragraph's frame
> ("Guarantees in this family are stated at that weaker level") is correct for it too. **No fix is required
> and no errata is owed.** The author should disregard the recommendation I originally filed here.

**What survives, as a nit (author's call, and safe to decline).** The abstract and p2 present the
pre-defined weights as buying *control* over which Pareto-stationary point is reached (p2: Aligned-MTL
"drifts along the Pareto front and provably converges to the optimum w.r.t. pre-defined tasks weights"),
whereas the chapter's clause reads the fixed weights as a *condition attached to* a weaker guarantee. Both
describe the same theorem; the chapter picks the less flattering framing. Since the paragraph's purpose is
to grade guarantee strength honestly, one optional clause would capture what the fixed weights buy: "...for
task weights fixed in advance, which is what lets it target a chosen point on the front rather than an
arbitrary one". Purely additive.
Also unchanged from my original note, and the one thing here still worth acting on: the ledger at `:467`
types the record as "arXiv:2305.19000v1, 16 pp" while `references.bib:915` types it as CVPR 2023, pp.
20083-20093. The bib venue is what the reader sees; the comment should name the same record it cites.


---

### 2. BLOCKER — PCGrad is said to make "no Pareto claim at all", but CAGrad reports PCGrad's Pareto convergence and attributes it to PCGrad's own paper

**WHERE:** `src/chapters/2_fundamentals.tex:442–445` (prose); the measurement claim in the ledger at
`:475–479`.

**WHAT (verbatim, prose):**
> "PCGrad guarantees that one projected update leaves the
> multi-task loss no higher than the unmodified gradient would, under conditions on the two
> task gradients, on the curvature of the loss, and on the step size, and it makes no Pareto
> claim at all \cite{yu2020pcgrad}."

and the ledger's supporting measurement at `:475–476`: "MEASURED: the string \"Pareto\" occurs ZERO times
in the paper."

**WHY:** The grep is reproducible and I reproduced it — 0 occurrences of "pareto" across all 27 pages of
arXiv:2001.06782v4, against 185 occurrences of "gradient", so the instrument is sound and the
lexical fact is true. The *inference* drawn from it is not. CAGrad, which this same paragraph cites two
sentences earlier, states on the page I read (arXiv:2110.14048, p5): "Similar to MGDA, as shown in [41],
PCGrad also converges to an arbitrary Pareto point without explicit control of which point it will arrive
at", where [41] is the PCGrad paper. So a Pareto convergence property *is* attributed to PCGrad in the
literature this paragraph is built from, and is attributed to PCGrad's own analysis. Whether that
attribution is faithful to Theorem 1 of PCGrad (p4, the two-task convex convergence dichotomy, which I
located and which does not use the word) is a question the dissertation is not obliged to settle — but
asserting "no Pareto claim at all" as a property of the method, on the evidence of a word-search, is a
claim the sources do not support, and it is contradicted by a source cited in the same paragraph. This
also violates the persona's own standard about the difference between a measurement and the claim built
on it, and AGENT_GUARDRAILS §1 R3 (the citing sentence must be supported by the source).

The Theorem 2 half of the sentence is **correct and I verified it**: PCGrad p5 Theorem 2 gives
`L(θ_PCGrad) ≤ L(θ_MT)` under exactly three conditions, and its own gloss on p5 names them as "(i) the
angle between task gradients is not too small ... (ii) the difference in magnitude needs to be
sufficiently large ... (iii) the curvature of the multi-task gradient should be large ... (iv) the
learning rate should be big enough". One nuance: the chapter's "conditions on the two task gradients"
folds the paper's angle and magnitude conditions together (both live in condition (a)); accurate, and
worth keeping as-is for readability.

**FIX:** Narrow the claim to what was actually measured, and make it a statement about the paper's own
text rather than about the method: e.g. "and its paper states no Pareto property for it, though later
work reads its analysis as convergence to an arbitrary Pareto point \cite{liu2021cagrad}." Alternatively
delete the clause; the paragraph's point (guarantees in this family are heterogeneous and weaker than
Pareto optimality) survives without it. Author's call between the two.

---

### 3. SHOULD-FIX — the paragraph attributes the "arriving somewhere on the front" limitation to two papers as self-criticism; both papers raise it against *other* methods

**WHERE:** `src/chapters/2_fundamentals.tex:445–448`.

**WHAT (verbatim):**
> "Two of these papers state the residual limitation
> themselves: arriving somewhere on the front says nothing about where, so the balance
> between the tasks at that point remains uncontrolled
> \cite{liu2021cagrad,senushkin2023aligned}."

**WHY:** "state the residual limitation themselves" reads as both papers conceding the limitation applies
to their own method. In both sources it is a criticism of prior work motivating their own contribution.
CAGrad p1: "Previous work has proposed several heuristics to manipulate the task gradients for mitigating
this problem. But most of them lack convergence guarantee and/or could converge to any Pareto-stationary
point." Aligned-MTL p2: approaches aiming at a Pareto-stationary solution "terminate once the Pareto front
is first reached, as a result, they might provide a suboptimal solution", immediately followed by
"Differently, Aligned-MTL ...". The ledger comment at `:464–466` and `:468–470` quotes both passages
correctly, so the prose drifted from its own ledger. R2 again.

**FIX:** "Two of these papers name the limitation as the motivation for their own methods: ...". Cheap,
and it makes finding 1's repair land naturally.

---

### 4. SHOULD-FIX — CAGrad's guarantee is stated only at the Pareto-stationary level; the paper's headline guarantee is convergence to a minimum of the average loss, and it is conditional on `c`

**WHERE:** `src/chapters/2_fundamentals.tex:439–440` ("the fixed
points of CAGrad are Pareto-stationary \cite{liu2021cagrad}") and `:532–534` ("CAGrad maximizes the worst
per-task improvement among updates that stay within a ball around the average gradient, with convergence
guarantees \cite{liu2021cagrad}").

**WHAT (verbatim, `:439–440`):**
> "the fixed
> points of CAGrad are Pareto-stationary \cite{liu2021cagrad};"

**WHY:** True as far as it goes — CAGrad p5 Theorem 3.2(1): "For any c ≥ 1, all the fixed points of CAGrad
are Pareto-stationary points" — but the chapter drops the `c ≥ 1` precondition and, more importantly,
drops part (2), which is the guarantee CAGrad advertises: p5 Theorem 3.2(2) bounds `Σ‖∇L₀(θ_t)‖²` for
`0 ≤ c < 1` and concludes "the algorithm converges to a stationary point of ∇L₀", i.e. of the average
loss; the abstract (p1) states it as "provably converges to a minimum over the average loss". The two
halves are mutually exclusive in `c`, and the practical regime is the second one: p3 declares "c ∈ [0, 1)
is a pre-specified hyper-parameter", and the experiments search `c ∈ {0.1,...,0.9}` (p7, p17). So the
chapter attributes to CAGrad the weaker of its two guarantees, under the branch of the constant that its
own experiments do not use. In a paragraph whose entire purpose is to grade guarantee strength per method,
that is a substantive omission rather than a compression.

**FIX:** Add the constant and the second branch in one clause: "the fixed points of CAGrad are
Pareto-stationary when its trade-off constant is at least one, and for smaller values it converges to a
stationary point of the average loss \cite{liu2021cagrad}". The description at `:532–534` is otherwise
accurate — I re-verified the maximin reading that the `[v2 review F-08]` comment at `:551–558` records
(p3 Eq. 3: `max_d min_{i∈[K]} ⟨g_i, d⟩ s.t. ‖d − g₀‖ ≤ c‖g₀‖`), so that earlier correction holds.

---

### 5. SHOULD-FIX — Nash-MTL and MGDA attributions are correct, but "necessary ... without being sufficient" is cited to the wrong one of the two papers that state it

**WHERE:** `src/chapters/2_fundamentals.tex:434–436`.

**WHAT (verbatim):**
> "A point is Pareto-stationary when some
> convex combination of the task gradients is zero, which is necessary for Pareto
> optimality without being sufficient \cite{nash}."

**WHY:** The definition half is verbatim-supported by Nash-MTL p2: "a point is called Pareto stationary if
there exists a convex combination of the gradients at this point that equals zero. Pareto stationarity is
a necessary condition for Pareto optimality." But that page does **not** say it is insufficient — I
searched all 19 pages of arXiv:2202.01017 for "sufficien" and got **zero** hits. The insufficiency is
stated by Sener and Koltun, arXiv:1810.04650 p4: "Although every Pareto optimal point is Pareto
stationary, the reverse may not be true." The ledger at `:482–484` quotes exactly that line under
`sener2018mgda`, so again the ledger is right and the `\cite` on the page is not. Under R3 the citing
sentence must be supported by the work it cites.
The rest of the Nash-MTL clause is **verified correct**: p6 Theorem 5.4 gives a sequence that "has a
subsequence that converges to a Pareto stationary point", and p6 Theorem 5.5 begins "If we also assume
convexity, we can strengthen our claim". The chapter's "only under an added convexity assumption on the
losses that a deep network does not satisfy" is a fair reading. Worth knowing for the defense, and
optional in text: Theorem 5.4 also rests on Assumption 5.1 (linear independence of task gradients off
Pareto-stationary points), which the paper itself calls "a stronger assumption than Pareto stationarity"
(p6).

**FIX:** `\cite{nash,sener2018mgda}` on that sentence, or split it so the insufficiency clause carries
`sener2018mgda`. One-character-class fix; no prose change needed.

---

### 6. SHOULD-FIX — §2.3 defines gradient conflict by cosine only, then reads near-zero cosine as "conflict absent"; the field's counter-argument (magnitude dominance) is neither cited nor named, and the chapter's own sources supply it

**WHERE:** `src/chapters/2_fundamentals.tex:494–503` (definition and the reading), with
`chapters/apx_f_cosine.tex:91–93` supplying the justification.

**WHAT (verbatim, `:497`):**
> "Orthogonality is not a conflict resolved but a conflict absent, which
> puts a limit on what any of these methods can contribute."

and, at `apx_f_cosine.tex:92–93`: "The cosine is the
right quantity because it is scale-free: it reads how the two requested updates are aligned and
ignores how large they are, which differs between the tasks and drifts during training."

**WHY:** The appendix names the exact reason the inference does not follow and then treats it as a virtue.
Angular conflict is one of two mechanisms; magnitude imbalance is the other, and it is the one the
gradient-*magnitude* balancers named twenty lines earlier exist for. GradNorm is described in this same
section at `:527–529` as rescaling "per-task gradient magnitudes so that tasks train at comparable rates"
— so the chapter itself documents a family of methods whose target the cosine cannot see. PCGrad, the
paper cited for the conflict definition, requires magnitude difference as a *separate* condition, not a
consequence of the angle: p1 "We hypothesize that such conflict is detrimental when a) conflicting
gradients coincide with b) high positive curvature and c) a large difference in gradient magnitudes", and
p5 condition (a)/(ii) makes the magnitude gap load-bearing in Theorem 2. Therefore "conflict absent" and
"a limit on what any of these methods can contribute" overreach the measurement: orthogonality rules out
*angular* interference, not dominance by a larger-norm task. The persona's lens 2 (Elich et al.,
arXiv:2311.04698 — magnitude differences dominate; that record I did **not** open this session, so I
attribute the point to PCGrad p1 and to the chapter's own GradNorm sentence, both of which I did read).
This matters beyond §2.3: `apx_f_cosine.tex:288–292` runs the same inference to the conclusion "the
measurement explains the finding", and §2.5 at `2_fundamentals.tex:867–870` inherits it.

**FIX:** Two sentences, no new experiment. (a) In §2.3, after the definition, state that the cosine
measures angular conflict only and that magnitude imbalance is a separate mechanism the cosine does not
detect, which is what the magnitude-balancing methods target. (b) Weaken "what any of these methods can
contribute" to "what the direction-based methods among them can contribute", which is what the evidence
supports. The chapter is already carrying a `[NEEDS SIGN-OFF]` on this passage (`:519–523`), so this
belongs in that same decision. Author's call on whether to cite Elich et al. as the canonical anchor
after someone opens it.

---

### 7. SHOULD-FIX — the scalarization-skeptic prior is cited but never bound to a tuning budget, and the chapter's own standard ("a balancer earns its place only by outperforming it") is not met by the screen that Ch.5 reports

**WHERE:** `src/chapters/2_fundamentals.tex:548–550` (the standard);
`chapters/5_mobiwac/02_related.tex:111–117` (the evidence).

**WHAT (verbatim, Ch.2 `:548–550`):**
> "The dissertation takes the cautious
> position these results support: a fixed-weight baseline is a serious competitor, and a
> balancer earns its place only by outperforming it."

**WHAT (verbatim, Ch.5 `:111–113`):**
> "We confirm this at scale: of nineteen loss and gradient
> balancers screened at their default configurations at a single seed on two datasets,
> Alabama and Florida, including the two methods named above, none improved on a tuned fixed
> task weighting across both tasks and both datasets."

**WHY:** The asymmetry is disclosed honestly on the Ch.5 side (defaults, one seed, two datasets) and the
comparator is described as *tuned*, so the sentence as written is a comparison of untuned adaptive methods
against a tuned baseline. That is exactly the confound Kurin and Xin warn about, in the direction that
favors the dissertation's own conclusion. Ch.5 says "We confirm this at scale", and "at scale" is doing
work the design does not support: nineteen arms at one seed on two datasets is breadth, not budget parity.
Ch.2 then states the standard ("earns its place only by outperforming it") without noting that the
converse standard — a balancer is only ruled out when swept with the baseline's budget — was not met.
This is the persona's lens 1 and attack question 1, and it is the single most likely question from an ML
examiner on this material.
Nothing here requires a new experiment. It requires the sentence to say what the screen can and cannot
license. Note also the repo's own unapplied recommendation at `5_mobiwac/02_related.tex:125–130`: the
"default configurations" qualifier does not cover PCGrad, whose exclusion is a wiring result (the region
tower sits outside `shared_parameters()`), so naming PCGrad as screened evidence overstates what was
tested. That is the author's ruling to revisit, not mine to change, but it compounds this finding.

**FIX:** In Ch.2, one clause after the standard: note that the screen behind this position compared
balancers at default configurations against a tuned fixed weighting, so it bounds the balancers'
out-of-the-box behavior rather than their tuned ceiling. In Ch.5, "at scale" is the word to drop or
qualify. Author's call on the PCGrad naming, which is already logged there.

---

### 8. NIT — MGDA is used as the source of the Pareto definitions but is never introduced as a method, while methods that build on it are

**WHERE:** `src/chapters/2_fundamentals.tex:417`, `:431`, `:480–487` (ledger), and the balancer list at
`:525–541` where MGDA does not appear.

**WHAT (verbatim, `:414–417`):**
> "The effect is not incidental: because the tasks can
> conflict, minimizing a weighted sum of their losses is only valid when they do not,
> and multi-task learning is more honestly cast as a multi-objective problem with no
> single optimum \cite{sener2018mgda}."

**WHY:** `sener2018mgda` is cited three times as the authority for the multi-objective framing and the
Pareto vocabulary, and the balancer paragraph then lists eight methods without the one that paper
proposes. CAGrad p5 and p13 describe themselves partly by reduction to MGDA ("CAGrad with c = 0 and c = 10
roughly recovers the final performance of GD and MGDA", p7), and Ch.3's own background already names it:
`chapters/3_cbic/basis.tex:44` "MGDA finds Pareto-optimal descent directions \cite{sener2018mgda}". A
fundamentals chapter that grades guarantee strength across five methods and omits the family's origin
leaves the reader unable to place CAGrad's and Nash-MTL's claims. The ledger at `:485–487` explains,
correctly and defensibly, why *Désidéri's* original paper is not cited (no bib entry, not opened) — that
is a different question from whether Sener and Koltun's method is named, and their record *is* opened and
cited. Not a blocker: nothing false is stated, and the persona's canon list is a presence check, not a
padding mandate.
> **CORRECTION, 2026-07-30, after review.** A paragraph stood here claiming that
> `chapters/3_cbic/basis.tex:44` ("MGDA finds Pareto-optimal descent directions") asserts something "the
> Sener-Koltun paper does not claim", and inviting the author to consider an errata footnote against
> published text. **That was wrong, and my own extraction of the paper refutes it.** arXiv:1810.04650 p2:
> "One such approach is the multiple-gradient descent algorithm (MGDA), which uses gradient-based
> optimization and provably converges to a point on the Pareto set (Désidéri, 2012)." The paper does assert
> Pareto-set convergence for MGDA, so the Ch.3 sentence is supported by the work it cites. **No errata is
> owed and no fix is required**; the author should disregard that recommendation. I had read the p2 quote in
> this session and still wrote the denial from the p4 stationarity passage alone, which is precisely the
> failure the citation protocol exists to prevent.
> For the record, the p4 passage remains true and is not in tension with p2: "Although every Pareto optimal
> point is Pareto stationary, the reverse may not be true" is a statement about what the *first-order
> condition* certifies, while the p2 sentence reports the convergence result Désidéri proves for the
> algorithm. §2.3's new paragraph and the Ch.3 sentence are consistent, and a reader reading in order meets
> no contradiction.

**FIX:** One clause in the balancer paragraph placing MGDA as the multiple-gradient-descent origin whose
solution the later methods refine, cited to `sener2018mgda` (already in the bib, already opened). For the
Ch.3 line, the author decides between an errata footnote and leaving it.

---

### 9. NIT — the hard-versus-soft spectrum and negative transfer are correct and well-built; two gaps are worth naming, neither false

**WHERE:** `src/chapters/2_fundamentals.tex:394–408` (spectrum), `:410–417` (negative transfer).

**WHAT (verbatim, `:410–412`):**
> "Sharing is not free. When tasks pull the shared parameters in different directions,
> joint training can leave a task worse off than its single-task model, a failure
> known as negative transfer."

**WHY:** This is the right definition (per-task degradation against the single-task model) and it is the
one the dissertation's own evaluation uses, so the chapter is internally consistent. Two things a demanding
examiner would ask for and not find. First, the definition binds negative transfer to gradient
conflict ("When tasks pull the shared parameters in different directions") — but the volume's own
Appendix F reports orthogonality *and* Ch.3 reports a null result, so the chapter's causal framing of
negative transfer excludes the shared-trunk-capacity mechanism that `chapters/3_cbic/conclusion.tex:20`
actually hypothesizes ("Architectural Restrictiveness ... may have been too restrictive"). Distinguishing
interference from capacity in the definition would let Ch.3's own hypotheses land. Second, the
spectrum paragraph covers hard sharing, soft sharing, cross-stitch, MMoE, PLE, DSelect-k and lands the
cross-attention connection at `:407–408` — complete enough for a thin fundamentals chapter — but capacity
is never named as a confound in MTL-versus-STL comparison anywhere in §2.3 (my grep for
capacity/parameter-count terms over L383–572 returned nothing on point). Ch.5 does disclose it, precisely,
at `chapters/5_mobiwac/04_method.tex:40–43`: "it is larger than either dedicated model ... about 4.2
million parameters at Alabama against 1.1 million for the two dedicated models combined (5.2 against 2.0
at California)". Since §2.3 is the section that teaches the reader how to read an MTL-versus-STL
comparison, one sentence there would arm the reader before Ch.5 needs it.

**FIX:** Optional, and both are additions rather than corrections: (a) widen the negative-transfer
sentence to name capacity contention alongside conflicting updates as causes; (b) one sentence noting that
a joint model and two dedicated models rarely have matched parameter counts, so a comparison states the
asymmetry. Author's call; the chapter is not wrong without them.

---

## CREDIBILITY SIGNALS PRESENT (what an MTL expert would trust here)

- The scalarization-skeptic block is present and positioned as the section's closing position, not buried:
  `2_fundamentals.tex:541–550` cites RLW, Xin, and Kurin, and the chapter takes the skeptical side.
- The new Pareto paragraph refuses the claim it would have been easiest to make:
  `:448–450` "This dissertation therefore claims no Pareto property of any kind for its models."
- Five of the seven guarantee and definition clauses at `:431-448` verified as written at the source PDF
  (see the tally in the verdict above), and where the prose drifted (findings 3, 5) the ledger comments
  already held the correct quote — the ledger is doing its job even where the prose slipped past it.
- The `[v2 review F-08]` CAGrad maximin correction at `:551–558` is faithful to arXiv:2110.14048 p3 Eq. 3.
  I re-verified it rather than trusting it; it holds.
- The Ch.5 conservative-by-design framing (`5_mobiwac/02_related.tex:105–107`) and the fixed-weight
  rationale (`04_method.tex:33–38`, "kept simple by design so that any improvement ... comes from the
  shared representation, not from an adaptive weighting scheme") are the right defense for this arc.
- Capacity is disclosed with numbers where the gain is claimed (`04_method.tex:40–43`).
- Ch.3's Nash-MTL preference is time-indexed and containment-worded at `3_cbic.tex:31–33` ("a conclusion of
  the time, weakened by a later finding about the optimizer implementation").
- The Ch.5 gradient-cosine scope correction at `02_related.tex:156–165` names four Gowalla states and flags
  Georgia as not otherwise used — the kind of scope statement that usually goes missing.

## UNSTATED DEFENSES (facts the repo holds that the audited text does not carry)

- The equal-tuning question for the STL comparators: my greps for tuning-budget language over
  `5_mobiwac/05_setup.tex`, `06_results.tex`, and `2_fundamentals.tex` returned nothing on point. If the
  dedicated models were tuned independently, that sentence is missing where the win is claimed.
- The screen's wiring caveat for PCGrad exists in the repo (`02_related.tex:121–124`, quoting
  `T4_audit_and_verdict.md:26–31`) but not in the text, while PCGrad is named in the prose as screened.
- §2.3 nowhere names the parameter-count asymmetry that Ch.5 discloses (finding 9).

## COUNTS

**blockers: 1 / should-fix: 5 / nits: 3**

Counts after the review correction above. The blocker is finding 2 (PCGrad). Finding 1 is withdrawn and
survives only as a nit (optional framing clause), which is why the nit count rises from 2 to 3; the
numbering of findings 2-9 is unchanged so earlier cross-references still resolve. Withdrawn and requiring
no action: finding 1's original blocker, and the MGDA/errata paragraph formerly inside finding 8.

## SCOPE NOTE

The narrowed scope was right for the clock and right for the value: the surviving blocker is inside the
~106 lines added today, in the exact clause range (`:431–448`) the previous wave flagged. Verifying the
guarantee attributions against five source PDFs consumed roughly half the window; that is the irreducible
cost of the task as specified, and it is the part that could not have been done from the source tree alone.
One lesson for whoever runs this gate next, paid for by my two withdrawn findings: a capped regex over a
PDF is a sampling instrument, not a reading. Both of my errors came from convicting a sentence on an
abstract or an introduction while the governing theorem sat on a page my search never returned. When the
text under audit already cites specific pages (this one did, at `:467`), open those pages before
contradicting them.

## UNFINISHED

- **Two of my own findings were withdrawn after review and are recorded above rather than deleted**
  (finding 1's blocker; the MGDA/errata paragraph in finding 8). Neither should be acted on. The pages that
  refuted them (arXiv:2305.19000 pp12-13; arXiv:1810.04650 p2) have now been read, so those two questions
  are closed, not merely deferred.
- **The remaining findings were not re-verified against pages beyond those I opened.** Findings 2, 4, 5, 6
  and 7 rest on the page anchors quoted in each. Given that two of my findings failed for exactly this
  reason, a re-checker should treat every page citation here as the specific thing to confirm, in particular
  finding 4's reading of CAGrad Theorem 3.2 parts (1) and (2), which I read on p5 only.
- **`3_cbic/method.tex:197–216` (the Nash-MTL exposition) was read but not verified clause-by-clause
  against arXiv:2202.01017.** I read the passage and its three-axiom description (scale-invariance,
  benefit to all tasks, proportional fairness) looks consistent with the paper's §2.2, and I verified the
  paper's Theorem 5.4/5.5 for §2.3's purposes — but I did not locate each of Ch.3's axioms, the
  `(GᵀG)α = 1/α` system at `:210`, or the "monotonic loss decrease and convergence to a Pareto-stationary
  point" clause at `:210` on a specific page. That last clause is the one I would check first: it is the
  same guarantee-strength question as finding 4, in a chapter whose text is published.
- **Ch.4 (CoUrb) was outside the assigned scope and I did not open it.** Its MTL claims are unaudited by me.
- **The built PDFs were not opened.** All findings are source-tree locations; nothing here is a claim about
  rendered pages, page numbering, or how the passage reads in the volume.
- **Elich et al. (arXiv:2311.04698) was not opened**, so finding 6 rests on PCGrad p1 and the chapter's own
  GradNorm sentence rather than on the canonical magnitude-dominance record. Anyone extending finding 6
  should open it before citing it.
- **No claim in this report is about `make check`, `make selftest`, or the build.** I ran none of them,
  as instructed, and I assert nothing about their status beyond quoting the task's own statement.


---

<!-- estado-rodada -->
> **Rodada encerrada · último toque 2026-07-30 · sem autoridade.**
> Este ficheiro é registo de proveniência do que foi discutido nesta passagem, não fonte
> de um facto corrente. O que ficou decidido está em [`VEREDITOS.md`](../../../../VEREDITOS.md);
> os valores entregues estão em `CLAUDE.md` §0.1. Não copie nada daqui sem confirmar lá.
