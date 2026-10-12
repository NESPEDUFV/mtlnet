# 10 · MTL expert — domain review report (round v2, 2026-07-26)

> 🛑 **GERACAO SUPERADA — nenhum numero medido deste ficheiro pode ser citado.**
>
> Isto e a persona de especialista em MTL da ronda de revisao v2, corrido **antes** de a geracao v18 fechar o vazamento de rotulo no grafo de
> visitas consecutivas (fechado em 2026-08-13). As celulas de macro-F1 medidas aqui vem da
> geracao com vazamento e **nao sao as do documento entregue**.
>
> **Como reconhecer uma celula morta sem a copiar daqui:** a categoria entregue vive na casa dos
> **30 a 38**. Qualquer valor de categoria muito acima disso neste ficheiro e da geracao anterior.
>
> **O que este ficheiro ainda vale:** o registo de que estas questoes foram levantadas, por quem,
> e o que se decidiu. O raciocinio e o processo continuam legiveis. So os **valores medidos**
> e que caducaram.
>
> Antes de agir sobre qualquer coisa aqui, ler `VEREDITOS.md` na raiz da pasta.


**VERDICT: SOUND-WITH-CORRECTIONS.**

> The MTL content is, on the whole, more honest than most published MTL papers I read. The
> dissertation's headline mechanism claim is backed by a control that runs in the correct
> direction, its balancer negative aligns with the field's null rather than fighting it, and the
> capacity confound is disclosed rather than buried. Two corrections are needed before the advisor
> sees it: one attribution in Chapter 5 is stated at a strength its own control cannot reach
> (F-01), and one citing sentence in Chapter 5 names a method the internal audit says was never
> validly tested (F-02, already known to the author and consciously deferred). Everything else is
> MAJOR-and-below.

**Count by severity:** 1 BLOCKER · 5 MAJOR · 8 MINOR · 4 NIT · 3 [UNVERIFIED] · **21 findings.**

**Top 3:**
1. **F-01 (BLOCKER)** — the freeze control cannot distinguish "stronger shared trunk" from "the
   category stream's own encoder plus depth", and the repo holds the ablation that shows the
   cross-attention trunk contributes ~nothing at Florida under live training. The word "trunk"
   is doing work the evidence does not license.
2. **F-02 (MAJOR)** — Chapter 5 names PCGrad in a "none of the balancers improved" sentence that
   the internal audit says was never a valid PCGrad test, for a reason the added qualifier does
   not cover.
3. **F-03 (MAJOR)** — the gradient-cosine measurement is pooled over four datasets, one of which
   (Georgia) is **not** among the six the dissertation reports; the text says "three of our six".

---

## Scope and method

Read: Ch.2 §2.3 in full (`2_fundamentals.tex:313-428`), plus §2.2 and §2.5 for the arc claims;
the MTL claims in Ch.3, Ch.4, Ch.5; the frame claims in Ch.1 and Ch.6; Appendix B's Nash-MTL and
Ch.5 scope rows; Appendix D. Method descriptions were checked against the **primary sources**, not
against `docs/context/*` — Nash-MTL (arXiv:2202.01017, PDF opened and text-extracted this
session), Aligned-MTL (2305.19000, same), CAGrad (2110.14048, same), and abstracts for
1705.07115 / 1711.02257 / 2001.06782 / 1803.10704 / 1604.03539 / 2106.03760 / 1810.04650 /
1905.07553 / 2201.04122 / 2209.11379 / 2111.10603 / 2311.04698 / 2009.00909 / 2109.04617 /
2306.03792 via the arXiv API. Every number below is **quoted** from a committed file; nothing was
recomputed. PDF pages are from `src/dissertacao.pdf` (96 pp, defense build).

---

## RANKED FINDINGS

### F-01 · BLOCKER · Lens 4 (capacity) + Lens 5 (per-direction affinity) — the attribution "a stronger shared trunk" outruns its control

**Location:** `src/chapters/5_mobiwac.tex:694` (PDF p. 72); repeated `1_introduction.tex:95-96`
(p. 76), `6_conclusion.tex:141` (p. 76).

**Quote (Ch.5):**
> "We therefore attribute the category gain to a stronger shared trunk, not to the region task
> teaching the category one; and the gain requires no second model at serving time... We report
> this attribution as a finding, not a hypothesis."

**What the control establishes.** `W6_ENCODER_ISOLATION.md:20-24` is quoted correctly and its
verdict is the chapter's: with the region stream fixed at initialization, category reaches
63.50 / 63.67 / 79.79 at AL/AZ/FL, above the single-task score by +7.63 / +6.54 / +4.64. The
control **does** kill the "region task teaches category" reading. That half is solid and the
chapter is right to say so.

**Where the claim breaks.** The control is a *disjunction eliminator*, not a locator. Freezing the
region stream removes region training; it does not remove the category stream's private encoder,
the two per-stream FFNs, the eight LayerNorms, or the extra depth. So "the gain survives without a
trained region task" licenses at most: **the gain is not cross-task transfer; it comes from
something in the joint architecture that the dedicated model does not have.** The chapter jumps
from that to a named component — the *shared trunk* — and the repo contains the arm that tests
exactly that component, with the opposite answer:

`docs/findings/archive/F50/F50_T1_5_CROSSATTN_ABSORPTION.md:19-20, 37` (FL, 5f × 50 ep):
> "| cat F1 (macro) | 68.36 ± 0.74 | 68.32 ± 0.67 | **−0.04 ± 0.13** |"
> "the cross-attn shared backbone (5.5 M params) produces a model that is statistically
> indistinguishable from a model with no cross-attn at all."

and `:80`:
> "The shared cross-attn is **structurally a cat-side feature extractor** in this regime. The
> 'shared' framing is a misnomer at FL — by gradient mass it's 95% cat-only."

Two more repo records point the same way. `cat_transfer_and_T53.md:21-22` decomposes the gain into
an "architecture" term (+3.22 AL / +2.27 FL) and a region-transfer term (−0.67 AL / +0.93 FL) —
i.e. the surviving gain is the *architecture* term, which is not the same object as "the shared
trunk". And `CSLSL_CASCADE.md:19` reports that the cascade arm **severs the symmetric channel
entirely** (`disable_cross_attn=True`) and still ties the joint model to within Δjoint ≤ 0.02 pp
at AL/AZ/FL/Istanbul. Chapter 5 itself reports that tie at `:731-736` (p. 74) and reads it as a
defense of parallel coupling — but a reader who takes both paragraphs seriously notices that the
arm which removes the trunk's cross-stream mixing loses nothing, while the paragraph 40 lines
earlier credits the trunk with the whole gain. Those two readings cannot both stand as written.

**Why this is a BLOCKER and not a MAJOR.** Ch.5 explicitly forecloses hedging: *"We report this
attribution as a finding, not a hypothesis."* A specialist referee who reads the released code
will run `--disable-cross-attn` before believing "trunk", and the repo's own answer at FL is
Δcat −0.04. This is the kill-shot shape the Common protocol §5 names: not a wrong number, but a
named mechanism the document asserts as settled while holding disconfirming evidence for that
exact mechanism.

**The examiner's question:** *"Your control freezes the region stream. It does not remove the
shared trunk. What does the joint model score with the cross-attention stack removed and
everything else held fixed — and if that number is also high, what exactly is 'the trunk'
contributing?"*

**Suggested direction (not applied).** The honest claim the evidence supports is architectural
without naming the component: *the category gain is a property of the joint architecture, not of
the region task's training signal*, plus the negative statement the control does prove. If the
author wants a locating claim, the arm that settles it is one run of the joint model with the
cross-attention stack disabled at AL/AZ/FL under the shipped v17 recipe — the flag exists
(`disable_cross_attn`, `mtlnet_crossattn/model.py:264`) and the cascade cell already runs it, so
this is hours of compute, not a new study. **[UNVERIFIED]** whether the F50 absorption result
survives on the shipped `check2hgi_dk_ovl` substrate: I found no re-run of `--disable-cross-attn`
as a pure ablation under v14/v17 outside the cascade cell (searched `docs/studies/closing_data/`,
`docs/results/closing_data/`, `docs/studies/archive/mtl_improvement/`). The F50 numbers are on an
earlier substrate generation and I do not claim they transfer; the point stands regardless,
because the *chapter* offers no evidence isolating the trunk on any substrate.

---

### F-02 · MAJOR · Lens 1 (scalarization skepticism) — PCGrad is named in a claim the audit says was never a valid PCGrad test

**Location:** `5_mobiwac.tex:182-187` (PDF p. 61).

**Quote:**
> "Reports find that gradient-balancing methods, which re-weight the tasks' updates during
> training (PCGrad, Nash-MTL), rarely improve on a well-tuned fixed weighting with two tasks. We
> confirm this: none of the balancers that we tried at their default configurations, including the
> two named above, improved on a tuned fixed task weighting in our model."

**Evidence.** `T4_audit_and_verdict.md:12-14`:
> "the three gradient-surgery methods (CAGrad/PCGrad/Aligned-MTL) **never validly tested
> individually** under G — as wired they collapse to ≈`equal_weight`"

and `:26-31`: the private region tower sits outside `shared_parameters()`, these methods apply
their surgical gradient only to shared parameters, so ">80% of the reg pathway trains at unit
weight always... these 3 cells **don't count** as balancer tests." I confirmed the partition in
source: `mtlnet_crossattn/model.py:554-561` yields only the cross-attention blocks and the two
final LayerNorms as shared, with `reg_specific_parameters()` at `:578-583` holding the region
encoder and head.

The chapter's own comment block already diagnoses this exactly (`:195-200`) and records the
minimal repair, marked *not applied* per the author's ruling. So this finding is not new
information for the author — it is a reviewer's independent confirmation that the deferred
objection is real, and my judgement of its severity. **The qualifier "at their default
configurations" does not answer it.** PCGrad's exclusion is a *wiring* fact, invariant to
configuration: it would collapse to equal weighting at every configuration under this
architecture. A referee who reads the audit will read the sentence as claiming a test that the
repo says did not happen.

**Suggested direction (not applied).** Either drop the two words naming PCGrad and let Nash-MTL
carry the named evidence (Nash-MTL is recorded as correctly wired and adapting, `T4:37-39` — a
genuinely valid test), or keep PCGrad and add its own scope: that under this architecture the
gradient-surgery family reduces to equal weighting, which was screened and lost. The second is
strictly more informative and is itself a publishable methodological observation.

---

### F-03 · MAJOR · Lens 2 (measured gradient claims) — the cosine pool includes a dataset the dissertation does not report

**Location:** `5_mobiwac.tex:202-206` (PDF p. 62); `6_conclusion.tex:145-148` (p. 77).

**Quote (Ch.5):**
> "the cosine similarity between the next-category and next-region updates on the shared trunk
> averages $+0.001$ across training (four seeds each on three of our six datasets, per-dataset
> means within $\pm0.003$)."

**Evidence.** `WHY_ORTHOGONAL_AND_NO_MODERN_OPTIMIZERS.md:29-31`:
> "pooled mean **+0.0008** over the **16 champion-G runs (4 states × 4 seeds {0,1,7,100})**,
> n = 3,797 epoch-fold points (per-state: FL +0.0007, AL +0.0032, AZ −0.0005, GE −0.0004...)"

The fourth state is **Georgia**. I confirmed this is not a typo: `plot_grad_cosine.py:19-24`
enumerates `florida, alabama, arizona, georgia`, and `R0_matched_metric_bar.json` carries
`g_rundirs` with all four seeds {0,1,7,100} for each of those four states — Georgia included.
Georgia is not one of the dissertation's six datasets (`1_introduction.tex:168-170`: Alabama,
Arizona, Florida, California, Texas + Istanbul).

So "three of our six datasets" is a *subset* description of a *four-state pool*, and the
$+0.001$ pooled figure and the $\pm0.003$ per-dataset bound are computed over the four. Read
strictly, the sentence attributes to three named-in-scope datasets a number whose pool contains a
fourth out-of-scope one. Every individual number is quoted correctly; the *scope sentence* is
what is off. Note this cuts in the dissertation's favour on generality (the finding replicates on
a state the thesis never reports) — which is exactly why saying so is cheap.

**Suggested direction (not applied).** State the pool as it is: four Gowalla states, three of
which are among the six reported here, four seeds each. **[UNVERIFIED]** I could not confirm
whether the printed $+0.001$ is the four-state pooled mean (+0.0008 rounds to +0.001) or a
three-state recomputation excluding Georgia; the run directories the plot reads
(`results/check2hgi_design_k_resln_mae_l0_1/...`) are not present on this machine, and the
protocol forbids me recomputing. If it is the four-state figure, the scope sentence is the only
repair needed; if a three-state figure was computed, its source file should be named.

---

### F-04 · MAJOR · Lens 3 (negative transfer) — Ch.1 and Ch.6 report negative transfer as a CBIC finding when the chapter offers it as a candidate

**Location:** `6_conclusion.tex:84-86` (PDF p. 76); `1_introduction.tex:83-85` (p. 14).

**Quote (Ch.6):**
> "the joint model of Chapter 3 did not consistently outperform two dedicated models, and negative
> transfer between the static and the sequential task was among its candidate causes."

This is careful and correct — "among its candidate causes" is the right register, and the
formal definition in Ch.2 (`:340-342`, p. 22: *"joint training can leave a task worse off than its
single-task model, a failure known as negative transfer"*) matches Zhang et al.'s per-task-drop
definition (arXiv:2009.00909). **The gap is elsewhere:** the definition requires an *equally
tuned* single-task comparator, and Chapter 3 does not report the per-arm tuning budget anywhere.
I grepped `3_cbic.tex` for tuning vocabulary (`hyperparam|Optuna|grid|sweep|tun(ed|ing)|learning
rate`) and found no statement of how the dedicated arms were tuned relative to the joint model.
So a referee cannot tell whether CBIC's null is negative transfer, an under-tuned baseline, or
seed noise — and the dissertation invites the question by naming negative transfer.

Chapter 5's dedicated arms are the opposite case and are handled well: `5_mobiwac.tex:516` and
`:762` disclose that the dedicated arm gets the *wider* search ("a per-dataset sweep over batch
size and learning rate against one configuration held fixed across all six datasets for the joint
model"), and `CEILINGS_N20_FINAL.md` records that the tempting "matched-knob" variant was
**rejected as baseline sabotage**. That is a strong credibility signal (see below) and it makes
Ch.3's silence more conspicuous by contrast.

**Suggested direction (not applied).** Chapter 3 is a time capsule and its prose cannot change
outside Appendix B — but the frame can. One clause in Ch.1 or Ch.6, or a line in Ch.2 §2.3 where
negative transfer is defined, noting that a negative-transfer diagnosis requires an
equally-tuned single-task comparator and that Chapter 3 did not establish one, would convert a
weakness into a demonstrated understanding of the standard. Ch.5's disclosure shows the author
already knows the standard.

---

### F-05 · MAJOR · Lens 4 — the freeze control is more conditioned than the chapter says; two conditions are in comments only

**Location:** `5_mobiwac.tex:685-694` (PDF p. 72), comments at `:711-714`.

The chapter discloses the single random initialization over five folds (`:691-692`) — good, and
correctly time-indexed. Two conditions from the source record are not surfaced:

1. **The region loss was off, not merely the weights fixed.** `W6:10-11`: *"Freeze the **region**
   stream... via `--freeze-reg-stream`, and zero the reg loss (`--category-weight 1.0`)."* The
   chapter says only "we fix the region pathway at its initial values at the start of training so
   it can neither learn nor teach the category task". Zeroing the loss is a *stronger and cleaner*
   intervention than freezing weights, so this omission understates the control's rigor — but it
   also changes what the arm is. With `category-weight 1.0` the run is a **single-task category
   model wearing the joint architecture**, which is precisely the framing that makes F-01's
   objection unavoidable. Stating it costs nothing and pre-empts the discovery.
2. **Dropout stayed active in the "fixed" stream.** `W6` closing note: *"`model.train()` at each
   epoch start re-enabled dropout in the frozen stream for all epochs after the freeze — the
   'frozen-at-init' stream was dropout-stochastic during training. Directional conclusions stand."*
   The record's own judgement is that the conclusions stand, and I agree (dropout adds noise, not
   learned signal). But "fix the region pathway at its initial values" is now a slightly
   idealized description of what ran.

**Suggested direction (not applied).** Surface (1) in prose — it strengthens the control. For (2),
a short footnote in the author's own honesty idiom ("the fixed stream retained its dropout during
training, which adds noise rather than learned signal") costs one line and removes a
gotcha that a referee reading the released code would find.

---

### F-06 · MAJOR · Lens 7 (compute honesty) — Ch.3's Nash-MTL cost claim is unsupported by the source, and this is the one Nash statement Appendix B does *not* cover

**Location:** `3_cbic.tex:237` (PDF p. 36).

**Quote:**
> "Nash-MTL is architecture-agnostic and requires only two matrix-vector products per iteration."

I extracted the full text of arXiv:2202.01017. "architecture-agnostic" is faithful — the paper
writes that its axiomatic approach is *"agnostic to the architecture used."* The cost half is not:
the string "matrix-vector" does not occur in the paper, and the method's per-step cost is an
iterative concave-convex procedure (the paper describes "a variation of the concave-convex
procedure (CCP)") plus a full backward per task. The chapter's own comment at `:252-258` already
reports this, with the implementation evidence (`optim_niter = 20` default, each pass a cvxpy/ECOS
solve) and the note that it is *"[REPORTED, NOT CORRECTED]"* — the author's judgement call.

I am flagging it at MAJOR anyway, for a reason the comment does not state: **this is the only
remaining Nash-MTL misstatement in the document, and Appendix B's Nash row (`:146-155`, p. 88)
corrects the *neighbouring clause* in the same sentence.** A referee who reads the errata row for
"gradient signs" and then reads the surviving "two matrix-vector products" in the corrected
sentence will reasonably ask why one half was audited and the other left. Cost claims are also the
easiest thing for an examiner to check, and understating a competitor optimizer's cost cuts
*against* the dissertation's own scalarization-first argument — the true cost is an argument in
the author's favour.

**Suggested direction (not applied).** Either add the row (the errata mechanism exists and this is
squarely a factual defect in the published article) or drop the clause. Appendix B already carries
a "deliberately preserved" section (`:160`), so a third option is to name it there as knowingly
left.

---

### F-07 · MINOR · Lens 4 — Nash-MTL's corrected description is right; the correction is verified

**Location:** `3_cbic.tex:237`; Appendix B row `apx_b_errata.tex:146-155` (PDF p. 88).

The prior round's correction — from "reliance on gradient signs rather than scales" to invariance
to the scale of the individual task gradients — is **correct**, and the errata row's reasoning is
sound. From the paper: Axiom 2.4 is *"Invariance to affine transformation"*, and the authors gloss
it as meaning *"the solution does not take into account the gradients' norms but rather treats all
of them the same, as if they were normalized."* Figure 1's discussion states Nash-MTL *"is
invariant to changes in loss scale."* I also confirmed the errata row's negative claim: "sign"
appears in the paper only inside an unrelated bibliography entry, never as a mechanism. The
chapter's earlier axiom list at `:224` ("scale-invariant to arbitrary loss re-weightings") is
consistent, and the equation at `:234` matches the paper's $(G^\top G)\alpha = \alpha^{-1}$ form.

Recorded as a MINOR finding rather than under "what holds" because of one wording nuance an
examiner may raise: Axiom 2.4 in the paper is invariance to **affine** transformation of utilities
($\tilde u_i = c_i u_i + b_i$, $c_i>0$), of which scale invariance is the multiplicative part. The
chapter's ordinal "the second of the axioms listed above" points at its own `:224` list, which is
internally consistent, so nothing is wrong — but "scale invariance" naming Axiom 2.4 is a slight
narrowing of the axiom's statement. No result depends on it.

---

### F-08 · MINOR · Lens 1 — Ch.2's balancer descriptions are faithful; one is loose

**Location:** `2_fundamentals.tex:349-362` (PDF p. 22).

Checked each against the primary source. Faithful: **uncertainty weighting** (homoscedastic
uncertainty, learned jointly — matches 1705.07115); **GradNorm** (dynamically tuning gradient
magnitudes so tasks train at comparable rates — matches 1711.02257); **DWA** (weights from the
recent rate of loss change — matches 1803.10704); **PCGrad** (projects a task's gradient off any
conflicting task's gradient — 2001.06782 says "onto the normal plane of the gradient of any other
task that has a conflicting gradient", correct); **Nash-MTL** (bargaining game, Nash solution as
joint direction — correct); **FAMO** ("reduces the cost of balancing by tracking loss decreases in
constant time and space rather than reading every task gradient at each step" — 2306.03792's
$\mathcal{O}(1)$ space and time against prior methods' $\mathcal{O}(k)$, correct and unusually
well put); **MMoE**, **PLE**, **DSelect-k**, **cross-stitch** (all four match their abstracts,
including cross-stitch as "a learned linear combination of two task networks' activations at each
layer").

Two worth noting:

- **CAGrad**, `:356-357`: *"seeks an update close to the average gradient while bounding conflict,
  with convergence guarantees."* The paper's objective is
  $\max_d \min_i \langle g_i, d\rangle$ s.t. $\|d-g_0\| \le c\|g_0\|$ — it **maximizes the worst
  local improvement** *within a ball around the average gradient*. The chapter has the constraint
  ("close to the average gradient") and the guarantee right, but "bounding conflict" describes the
  objective as a bound when it is a maximin. A precise one-clause version: *maximizes the worst
  per-task improvement within a ball around the average gradient*. MINOR because the sentence is
  not wrong in effect, and the chapter correctly groups CAGrad under methods acting on gradient
  directions.
- **Aligned-MTL**, `:359-361`: *"aligns the principal components of the gradient system and uses
  its condition number as a stability criterion."* Verified verbatim against 2305.19000 — the
  paper proposes "using a condition number of a linear system of gradients as a stability
  criterion" and aligns "principal components of a gradient matrix". This one is exactly right.

---

### F-09 · MINOR · Lens 1 — the skeptic canon is present and correctly positioned; four canon items are absent

**Location:** `2_fundamentals.tex:363-372` (PDF p. 23).

The skeptic block is the strongest paragraph in §2.3 and it is positioned correctly — *after* the
balancer family, as a tempering result, with the dissertation's own stance stated
(`:370-372`: *"a fixed-weight baseline is a serious competitor, and a balancer earns its place
only by outperforming it"*). Present and cited: Kurin (2201.04122), Xin (2209.11379), RLW
(2111.10603), Vandenhende + Yu surveys, Standley (1905.07553), MGDA (1810.04650), Caruana,
Ruder, Kendall, GradNorm, DWA, PCGrad, CAGrad, Nash-MTL, FAMO, MMoE, PLE, DSelect-k, cross-stitch.

Absent from `src/references.bib` (searched by arXiv id, author surname, and title substring):
**Hu et al. 2308.13985**, **Royer et al. 2310.08910**, **Elich et al. 2311.04698**, **TAG
2109.04617**, **Zhang et al. negative-transfer survey 2009.00909**, **Crawshaw 2009.09796**.

I do **not** recommend adding all six — the persona forbids demanding padding, and a thin
fundamentals chapter is a design choice the author has defended. Two are worth their space
because the document makes claims they speak to directly:

- **Elich et al. 2311.04698** bears on Ch.5's cosine argument. Its finding is that angular
  gradient conflict is *not* uniquely an MTL phenomenon and that **magnitude** differences are the
  distinguishing factor, with Adam partially normalizing scale. The dissertation's "cosine ≈ 0 so
  a balancer has nothing to resolve" is a *conflict-direction* argument; Elich is the paper that
  says direction is the wrong axis to look at. Citing it would show the argument was made against
  the strongest available objection rather than around it — and the repo already holds the
  magnitude evidence (F-13 below).
- **Zhang et al. 2009.00909** is the standard reference for the negative-transfer definition that
  `:340-342` states. Right now that definition rests on `standley2020tasks`, which is a
  task-grouping paper (*"Which Tasks Should Be Learned Together"*), not a negative-transfer one.
  The sentence it supports at `:342-344` — "Which tasks help each other and which interfere cannot
  be assumed away" — *is* Standley's claim, so the citation is not wrong; the definitional
  sentence just has no source of its own.

---

### F-10 · MINOR · Lens 2 — the "no conflict to resolve" inference is stated as mechanism where it is one of two channels, and the repo says so

**Location:** `5_mobiwac.tex:206-209` (p. 62); `6_conclusion.tex:149-152` (p. 77).

**Quote (Ch.6):**
> "Under the check-in-level representation the two sequential tasks coexist with essentially
> orthogonal gradients: sharing stopped hurting. This also explains why gradient-balancing
> optimizers had little to correct, in this configuration, and why a tuned fixed weighting
> sufficed."

The scoping here is careful — "in this configuration", "a finding for this pair of tasks, not a
general rule" (Ch.5 `:208-209`). What neither chapter states is the limit the repo's own analysis
puts on the cosine's reach, `WHY_ORTHOGONAL:34-36`:
> "orthogonality rules out two things: (a) the tasks hurting each other through the shared trunk,
> and (b) the *naive* 'they descend together' form of help. But MTL transfer has a **second
> channel the cosine does not capture: the shared representation.**"

That distinction is load-bearing for the dissertation, not against it: it is exactly why a
near-zero cosine and a real category gain are *consistent* rather than in tension, and it is the
answer to the sharpest question an examiner can ask here ("if the gradients are orthogonal, where
does your gain come from?"). Right now that answer lives only in the repo. One clause would
install it.

---

### F-11 · MINOR · Lens 6 (checkpoint honesty) — the convention discipline holds, and one hidden note should surface

**Location:** `5_mobiwac.tex:520` and comment `:526-530`; `6_conclusion.tex:102` and comment
`:103-108`.

I checked this hard because it is where MTL papers usually cheat, and the document is clean.
Ch.5 `:520` names the joint-best convention (one saved checkpoint, both heads read at the
geometric-mean-selected epoch) and keeps diagnostic-best as a robustness bound. This matches
`JOINT_BEST_RESULTS.md`, which records that the deployable single checkpoint reproduces the
reported table to within ≤ 0.06 pp (category) and ≤ 0.11 pp (region) with no verdict change.
Ch.6's capacity paragraph carries a gate fix (64.54 → 64.51) explicitly to avoid blurring the two
conventions. Guardrail N5 is being enforced, visibly, by the author.

The one wrinkle: the freeze control's "within 0.3" comparand is on the **diagnostic-best**
convention of the development configuration, which `:706-710` documents in a comment and `:692-694`
handles in prose by naming the development scores (63.56 / 63.39 / 79.82) rather than the Table 3
cells. That is the correct repair and it works. But the *reason* — that the 0.3 cannot be read
against Table 3 because the conventions differ — is comment-only. A reader who tries to verify 0.3
against Table 3's 64.51 / 65.79 / 79.84 will fail and will not know why.

---

### F-12 · MINOR · Lens 5 — per-direction affinity: the text does not claim the untested direction, but it does not name the gap either

**Location:** `5_mobiwac.tex:685-694`; `6_conclusion.tex:92-96`.

Checked as instructed. The document is disciplined here: I grepped every occurrence of
"teach"/"transfer" in Ch.1, Ch.2, Ch.5, Ch.6 and found **no** claim that category teaches region.
Both freeze-control passages state only the negative (region does not teach category) plus the
architectural positive. That is the correct restraint, and it deserves credit.

The gap is that the *other* direction was measured and is not mentioned. `cat_transfer_and_T53.md`
records a multi-seed decomposition in which genuine region→category transfer is **+0.93 at FL and
−0.67 at AL** — small, and sign-flipping with dataset size. That is a more interesting and more
honest statement than silence: it says the transfer channel exists, is small, and is not uniformly
positive. Its own caveat is also worth knowing (`:25-27`): the reg-OFF isolation is not perfectly
clean, because "the cat stream still attends to the reg stream's K/V in the bidirectional
cross-attn even at reg-weight 0" — which is the same imperfection that limits the W6 control, and
which I confirmed in source (`mtlnet_crossattn/model.py:168-171`: `cross_ab` queries `a` against
`kv_b = b` unconditionally unless `detach_ab` is set).

**Suggested direction (not applied).** Future work the text should name, not an experiment to
demand. One sentence: the reverse direction was not isolated in this work, and the development
measurement that touched it found the effect small and dataset-dependent.

---

### F-13 · MINOR · Lens 2 (Elich) — the magnitude story is absent, and the repo holds it

**Location:** absent from `5_mobiwac.tex` §Related and `6_conclusion.tex`.

The 2026 skeptical literature says the discriminating quantity between MTL and STL is gradient
**magnitude**, not angle (2311.04698). The repo measured exactly that:
`F50_T1_5_CROSSATTN_ABSORPTION.md:47-60` reports a reg/cat gradient-norm ratio of 0.03–0.06 on the
shared parameters across most of training, concluding *"For a 50-epoch run, >80% of the wall-clock
time the shared cross-attn is being trained ~exclusively by cat-side gradient."*

This is the missing keystone of the dissertation's own argument, and it points the same way as
every other piece: if the shared parameters see ~95% category gradient, then (a) no balancer can
help, (b) the "shared" trunk is functionally a category encoder, and (c) the category gain being
architecture rather than transfer is *predicted*, not merely observed. It also supplies the
magnitude-axis answer to Elich. **[UNVERIFIED]** whether the ratio holds on the shipped substrate
— the measurement is from the F50 generation, and the diagnostic is default-OFF in the current
runner (`mtl_cv.py:1522-1527`: diagnostics run only when `MTL_TRAIN_DIAGNOSTICS=1`), so I cannot
confirm current-generation values exist. If they do not, this stays unstated; if they do, it is
the single highest-value addition available to Ch.5.

---

### F-14 · MINOR · Lens 4 — the parameter-count disclosure is correct and correctly framed

**Location:** `5_mobiwac.tex:272-278` (p. 64); `6_conclusion.tex:96-119` (p. 76).

Verified, and this is a credibility signal rather than a defect — logged so the author knows not to
touch it. Ch.5 states the joint model is larger than both dedicated models combined (about 4.2 M
at Alabama against 1.1 M for the two dedicated models; 5.2 against 2.0 at California) and frames
the benefit as operational, not arithmetic. Ch.6's capacity-matched control is exactly the arm the
cross-stitch literature established as necessary (1604.03539 used capacity-matched ensembles), and
its numbers trace to `capacity_matched_stl_cat/README.md` (hidden_dim 752 = 101.9% of the joint
model's parameter count; widened model 69.88 ± 0.26 against 70.60 ± 0.07 at its own tuned narrow
width). The observation at `:116-119` that the widened model's best configuration uses a *lower*
learning rate than the narrow one — evidence the sweep found the wide model's own optimum rather
than reusing the narrow model's — is the kind of detail that makes a referee trust the rest.

One residue: `:100-102` gives Alabama's capacity arm as "56.16 macro-F1" with no dispersion, and
the chapter's own comment (`:133-135`) notes the source README gives std 1.89 for that arm. With
std 1.89 against a 56.82 dedicated ceiling, the Alabama capacity arm and the ceiling overlap
substantially — which does not affect the conclusion (neither recovers the joint model's 64.51)
but does mean the "0.66 below" framing is inside noise at that dataset. California's 0.26 std
carries the claim.

---

### F-15 · MINOR · Lens 3 — Ch.3's "hard sharing frequently matches or exceeds" leans on Standley for a claim Standley does not make

**Location:** `3_cbic.tex:210` (PDF p. 35).

**Quote:**
> "**Empirical Performance:** In practice, hard parameter sharing frequently matches or exceeds
> the performance of more complex architectures on many benchmarks, while offering faster training
> and inference \cite{standley2020tasks}."

Standley et al. (1905.07553) argue close to the opposite emphasis: joint training "often leads to
inferior overall performance as task objectives can compete", and their contribution is a
framework for *splitting* tasks across networks so competing tasks are separated. Their headline is
that a task-grouping assignment beats "not only a single large multi-task neural network but also
many single-task networks" — i.e. neither pole wins; the grouping does.

Chapter 3 is a time capsule and this is reproduced published text, so it cannot be silently
changed. I am recording it because the ML-expert reviewer is the reader who will notice, and
because there is a zero-cost containment already in use elsewhere in this document: the chapter
preface (`:21-31`) time-indexes the chapter's conclusions and its Nash-MTL preference. A referee
who checks this citation will find a published-text defect, not a dissertation-authored one — and
Appendix B exists for precisely that. **Suggested direction (not applied):** author's judgement
whether it warrants an Appendix B row; if not, it should at least be on the known-issues list so
it is not a surprise at the defense.

---

### F-16 · MINOR · Lens 4 — Ch.2's placement of the joint model on the sharing spectrum is defensible and matches the code

**Location:** `2_fundamentals.tex:324-338` (PDF p. 21-22).

Checked against source because the persona asks whether the self-placement is defensible. It is.
The chapter claims the joint model adopts the principle of "keeping shared and task-specific
components side by side rather than forcing one common trunk... though it realizes it with
cross-attention rather than expert gating" (`:335-338`). Ch.5 `:260-263` describes the mechanism as
attention letting each stream read the other's features "while each keeps its own feed-forward
weights", concluding "The tasks therefore share by exchanging information between per-task
streams, not by owning hidden layers in common."

Source confirms both: `_CrossAttnBlock` (`mtlnet_crossattn/model.py:54`) holds separate
`cross_ab`/`cross_ba` attention modules and separate `ffn_a`/`ffn_b` (`:136`, `:143`), applied per
stream at `:201-202`. The docstring at `:555-557` even flags the subtlety honestly — parameters
"shared by both tasks conceptually via information exchange, even though each task has its own FFN
weights within a block". Ch.3's placement as hard sharing is likewise correct and matches its own
parameter partition (`3_cbic.tex:260-269`: shared = task embedding + FiLM + shared layers).

One consequence worth the author's awareness: because the cross-attention modules are the *only*
truly shared weights, and they are the component F-01 questions, the sharing-spectrum story and
the mechanism story stand or fall together. Getting F-01's wording right also settles this.

---

### F-17 · NIT · Lens 5 — Ch.2's lineage table is accurate as representation history; it is not MTL history

**Location:** `2_fundamentals.tex:249-265`, Table 2.x (PDF p. 22).

Every row checks out against the glossary and the chapters: DGI as unsupervised place embeddings by
local-patch/global-summary mutual information (consistent with how Ch.4 `:57` and the chapter's own
citation ledger characterize it; I did not open the DGI paper this session); HGI extending
graph infomax over the POI/region/city hierarchy (matches `huang2023hgi` as Ch.4 `:57` describes
it); MTLnet as "First joint model: place embedding, FiLM conditioning, and hard parameter sharing.
Null result for that configuration."; ST-MTLNet keeping MTLnet and replacing the input; Check2HGI;
the joint model. The status line correctly marks the last two as submitted/under review. The
attribution fix recorded in the chapter's ledger (`:300-301`) — that MTLnet uses only the place
embedding plus per-task FiLM, and the decomposed encoders are CoUrb's contribution — is correctly
reflected.

The NIT: as **MTL history** the table has four rows about representations and two about sharing, so
the sharing axis (hard → cross-attention with a private path) appears only as a clause inside the
MTLnet and joint-model rows. Since the chapter's thesis is that representation dominates, this
imbalance is arguably the point — the table *shows* the asymmetry the thesis claims. If the author
wants it to read as lineage on both axes, a "sharing topology" column would do it in one edit. Not
a defect.

---

### F-18 · NIT · Lens 8 — no balancer weight trajectories are reported

**Location:** `5_mobiwac.tex:185-187`.

Attack question 8 asks whether adaptive weights ever deviated from ~constant, since converging
weights mean a static weight replicates them cheaper. The document does not report this. The repo
appears to hold it (`docs/studies/archive/mtl_improvement/figs/t4_loss_weight_trajectories_FL.png`
is referenced in `CLAIMS_AND_HYPOTHESES.md:19`; I did not open the figure and make no claim about
its contents — **[UNVERIFIED]**). Also relevant and quotable if the author wants it: `T4:32-34`
records GradNorm's weight range as 0.016, unable to reach the champion's 0.25/0.75 split, and DWA
"pinned ≈1.0". Those are the concrete numbers behind "the balancers had little to correct". Not
needed for the gate; a strong response-letter answer.

---

### F-19 · NIT · Lens 1 — Ch.2's §2.5 restatement of the skeptic finding is the sharpest MTL sentence in the frame

**Location:** `2_fundamentals.tex:594-599` (PDF p. 25).

> "Multi-task learning is the mechanism that would let the two tasks share what they have in
> common, but it is not a free gain. Naive hard sharing can leave a task worse than its
> single-task model, and the elaborate gradient balancers proposed to prevent this frequently do
> not outperform a well-tuned fixed-weight baseline. Whether joint training helps therefore cannot
> be assumed; it has to be measured, against the dedicated single-task models, under a protocol
> that does not flatter it."

Logged so it is not touched in any trimming pass. It states the field's null, the reason the
question is open, and the standard of proof, in three sentences, without citing anything twice.

---

### F-20 · NIT · Lens 6 — Appendix D's ceiling is label-only and correctly bounded

**Location:** `apx_d_ceiling.tex` (PDF pp. 95-96).

Outside my primary scope but adjacent to the MTL claims, so noted in one line as the protocol
directs. The appendix computes a label-only autocorrelation ceiling for next category from the
label sequence alone, under the dissertation's own protocol (five folds grouped by user, macro-F1,
averaged over folds), and it is explicitly a *weaker absolute claim* than the prior Chapter 5
wording. That is the right direction of travel and it does not touch any MTL claim: the joint-model
comparisons are all against the dedicated models, not against this ceiling.

---

### F-21 · [UNVERIFIED] · Lens 9 — loss shaping across arms

**Location:** `5_mobiwac.tex:269-270`.

Attack question 9 asks whether loss-shaping choices are identical across joint and dedicated arms.
Ch.5 `:269` states class weighting was tested on both outputs of the joint model and lowered both
metrics, so it is off there; and the recipe record (`v17_completion/README.md:79-80`) shows
`--no-{reg,cat}-class-weights` in the joint recipe. The dedicated category ceiling sweep
(`cat_ceiling_sweep/sweep.sh:31-33`) varies only batch size and learning rate and passes no
class-weight flag, which is consistent with weighting off on both sides. **I could not confirm the
defaults are identical across the two entry points** (`--task mtl` vs `--task next`) without
reading further into the argument parser than a read-only pass warrants. Reported as unverified,
not as a defect. One sentence stating that loss shaping is off in both arms would close it.

Related and worth the author's awareness: the joint model trains under a **per-head learning-rate
regime** (`RESULTS_BOARD.md:21`: "bs=8192 + cat-lr 1e-3 via `--onecycle-per-head-lr`", cat/reg/
shared 1e-3/3e-3/1e-3), which the dedicated arms do not have — they sweep a single learning rate.
This is not a confound in the dissertation's favour (the dedicated arm gets the wider search, as
Ch.5 discloses), but "per-head learning rates" is an architectural affordance of the joint model
that the chapter does not name, and an examiner asking "what does the joint model have that the
dedicated one does not" would find it.

---

## Credibility signals present (what an MTL expert would trust here)

1. **The balancer negative aligns with the field's null and cites the skeptics.** Kurin, Xin, and
   RLW are all cited *in the fundamentals*, positioned as a tempering result, with the
   dissertation's stance stated explicitly. Most POI-MTL papers cite only pro-balancer work.
2. **The baseline was protected from sabotage, on the record.** `CEILINGS_N20_FINAL.md` rejects the
   matched-knob variant that would have inflated the category gain: *"That is baseline sabotage
   (advisor panel unanimous); kept only as a labeled iso-budget ablation, never the headline."* The
   dedicated category model is tuned per dataset, best-versus-best, and Ch.5 `:762` discloses that
   the *comparator* receives the wider search.
3. **The parameter asymmetry is disclosed where the gain is claimed**, with a capacity-matched
   control that fails to recover the gain (F-14). The document never credits the parameter count.
4. **Verbs are bound to tests.** Superiority for category (paired $t$ on per-seed means, Holm
   across six), non-inferiority for region (TOST, ±2 pp), with the pre-registration limits stated:
   the plan covered tests per task, did not cover region superiority, and the four region gains are
   labeled secondary results outside it. At Arizona the interval centered on zero is reported as a
   match, and at Alabama a statistically significant deficit *inside* the margin is reported as
   such — not upgraded.
5. **Checkpoint convention is named and the two conventions never blur** (F-11), enforced by a
   visible gate fix in Ch.6.
6. **The negative result is time-indexed rather than disowned.** Ch.3's preface: *"Its conclusions
   are the conclusions of the time, for the configuration studied here."*
7. **The Nash-MTL preference is contained.** The preface flags it as weakened by a later finding,
   and the pointer was corrected in a prior round to say Chapter 5 (not "the following chapters")
   is the one that does not rely on it — correct, since Ch.4 `:115` does train with it.
8. **The cascade control was run and reported as a tie, not a win.** Ch.5 `:734-736`: *"We read
   this as a defense of the parallel design, not a claim that we outperform the cascade."*
9. **The cosine claim is scoped in prose**, including the earlier data preparation and the
   "finding for this pair of tasks, not a general rule" limit — the exact scoping the persona's
   lens 2 demands, present without being asked.

## Unstated defenses (facts the repo holds that the text does not)

1. **The gradient-magnitude asymmetry** — reg/cat norm ratio 0.03–0.06 on shared parameters over
   most of training (F-13). Answers Elich on the axis Elich says matters, and predicts the
   architecture-not-transfer result.
2. **The cosine's own limit** — orthogonality rules out mutual harm and naive co-descent but not
   the shared-representation channel (F-10). This is the answer to "if gradients are orthogonal,
   where does the gain come from?"
3. **Gradient surgery is architecturally excluded, not merely unhelpful** — the private region
   tower sits outside `shared_parameters()`, so CAGrad/PCGrad/Aligned-MTL reduce to equal
   weighting under this design (F-02). A real methodological finding, currently a liability
   instead.
4. **The orthogonality is intrinsic, not manufactured by the private tower** —
   `orthogonality_intrinsic_test.md` reports cos ≈ 0 persisting in a fully-shared model where the
   region gradient is *larger* than the category one (ratio 1.26 AL / 1.78 FL). This pre-empts the
   sharpest available objection to the cosine argument: that the dual-tower design creates the
   orthogonality it then cites. Nowhere in the document.
5. **The reverse transfer direction was measured** — +0.93 FL / −0.67 AL, small and sign-flipping
   (F-12).
6. **The balancer weight ranges** — GradNorm's 0.016 range and DWA's ≈1.0 pinning (F-18).
7. **The Arizona ceiling sensitivity** — two arms screened at 2 of 4 seeds scored ~57.0 against the
   reported 56.43 ceiling; the chapter carries this as a hidden comment under a
   provide-on-request policy (`5_mobiwac.tex:632-637`). Defensible as a policy; the author should
   know it is the one place where a referee recomputing from the sweep files could arrive at a
   smaller Arizona gain (~+8.8 rather than +9.35 — still the largest).
8. **The freeze control zeroed the region loss** — a stronger intervention than the prose claims
   (F-05).

## Open questions only the author can answer

1. **F-01:** is there any arm — any substrate generation — in which the joint model was run with
   the cross-attention stack disabled and everything else fixed, *outside* the cascade cell? If
   yes, its numbers decide whether "trunk" survives as the named mechanism. If no, is one such run
   at AL/AZ/FL affordable before the defense, or should the claim be reworded to the architectural
   statement the control actually proves?
2. **F-03:** was the printed $+0.001$ computed over the four-state pool (FL/AL/AZ/**GE**) or
   recomputed over the three in-scope datasets? If recomputed, which file holds it?
3. **F-02:** is the ruling to keep PCGrad in that sentence final, now that a second independent
   reviewer reaches the same conclusion the drafting agent did?
4. **F-06:** does the "two matrix-vector products" clause get an Appendix B row, a place in the
   deliberately-preserved list, or removal?
5. **F-13:** do current-generation gradient-norm-ratio diagnostics exist on
   `check2hgi_dk_ovl`, or is that measurement only on the F50 substrate?

## Out-of-scope handoffs (one line each)

- Appendix D's ceiling arithmetic and the Chapter 5 "Integrity of the representation" rewrite are
  in another persona's lane; I read both only far enough to confirm they touch no MTL claim.
- `1_introduction.tex:151-153` describes objective 1 as benefiting "its two category tasks" — a
  task-naming question for the terminology reviewer, not an MTL one.
- `2_fundamentals.tex:465-467` uses the relative multi-task performance change ($\Delta_m$) as an
  aggregate; Ch.5 uses the geometric mean of the two task metrics for checkpoint selection. Two
  different aggregates for related purposes, each correctly defined where used — flagged for the
  consistency reviewer, not a defect in either place.

---

### Protocol compliance

Read-only: no file in the repository was modified except this report. No git command was run; no
build was invoked. Every finding carries a verbatim quote plus `file:line` and, where the claim is
reader-facing, a PDF page from the 96-page defense build. Every number is quoted from a committed
file, named at the point of use; none was computed or re-derived. Three items are marked
[UNVERIFIED] with the reason and the place I looked. Method descriptions were checked against
primary sources opened this session (Nash-MTL, Aligned-MTL, and CAGrad as extracted PDFs; the
remaining fifteen via arXiv metadata), not against the repo's internal notes.


---

<!-- estado-rodada -->
> **Rodada encerrada · último toque 2026-07-26 · sem autoridade.**
> Este ficheiro é registo de proveniência do que foi discutido nesta passagem, não fonte
> de um facto corrente. O que ficou decidido está em [`VEREDITOS.md`](../../../VEREDITOS.md);
> os valores entregues estão em `CLAUDE.md` §0.1. Não copie nada daqui sem confirmar lá.
