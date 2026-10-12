# Where the category gain comes from: the shared-trunk attribution question

## 0. Why this document exists

The joint model's category advantage over the dedicated single-task model is established: `+5.34` to
`+9.40` macro-F1 points across the six datasets at `n=20` (four seeds x five folds), with a paired
test and Holm correction (`docs/studies/closing_data/v17_completion/CEILINGS_N20_FINAL.md:18-24`).

What is **not** established is the mechanism: which part of the joint architecture produces that
gain. That question has now been opened, closed, and reopened several times, each time from the same
raw evidence, because the answer was never written down in one place. This document is that place.
Read it before re-litigating the attribution.

The sentence at stake, which an earlier draft of Chapter 5 carried and which the author has twice
asked to restore, is:

> "the shared trunk carries the semantic context that lifts the next-category task"

**Status: not supported, and the wording is doubly wrong.** See §3 and §4.

---

## 0a. The two questions, answered directly

Everything below is evidence and provenance. These are the answers, stated first so nobody has to
reconstruct them.

**Scope, stated up front because it was initially missed.** The answers in this section concern the
**next-category** task. The region task has its own study, still running, and it is not a mirror image:
the region head has a private route around the stack, and region beats its dedicated ceiling at four of the
six datasets (FL, CA, TX, Istanbul) while merely matching at the other two. See §6h before drawing any
region conclusion from the numbers here.

### Does the cross-attention stack help with anything at all?

**Yes, by a small amount at the larger dataset, and by nothing detectable at the smaller one.** It is not
useless, and it is not the source of the headline gain. Measured by removing it and changing nothing else,
one seed and five folds:

One caveat governs every number in the table, and it is not a formality: removing the stack removes the
cross-task exchange **and** the `1.58M` parameters of per-stream depth that live inside the same blocks
(§6c.2). So these deficits bound what *the whole stack* is worth; they do not attribute anything to the
exchange specifically. That attribution needs the pending identity arm, which keeps the blocks and
neutralises only the mixing.

| what the stack is worth | delta | 90% interval | share of that task's own gain |
|---|---:|---|---|
| Florida, category | `-0.26` | `[-0.34, -0.18]` | `4.9%` of `+5.33` |
| Florida, region | `-0.10` | `[-0.17, -0.03]` | `13.5%` of `+0.72` |
| Alabama, category | `-0.17` | `[-0.41, +0.06]` | `2.3%` of `+7.70` |
| Alabama, region | `-0.27` | `[-0.67, +0.13]` | Alabama has no region gain to explain (`-0.31`) |

At Florida both intervals exclude zero, so removing the stack does make both tasks measurably worse there.
At Alabama neither interval excludes zero, so nothing is detectable at this sample size.

The honest summary is that the whole stack is worth a **bounded sub-quarter-point deficit at the larger
dataset — at most about five percent of the category gain — and nothing measurable at the smaller one.**
Two things must not be said. It is not "structurally dead": the Florida intervals exclude zero. And the
deficit is not attributable to the exchange, because the depth came out with it.

### Then how does the joint model still show that improvement?

Because the improvement does not **depend** on the interaction between the tasks. What is left when every
cross-task pathway is removed is the **category branch and the schedule it trains under**, and that alone
reproduces almost the whole advantage.

Note the verb. These arms are retrained after the ablation, so they establish non-dependence, not the
absence of a contribution: with the stack gone the category branch retrains and may absorb whatever the
stack had been supplying. "The gain does not require multi-task learning" is supported. "Multi-task
learning contributes nothing" is not, and must not be written.

Deliberately avoided here: **representational**. In this dissertation that word denotes the input
representation map, and both arms read the identical `check2hgi_dk_ovl` build — the input representation is
held fixed, not varied. The difference is architectural and in the training schedule.

The decisive arm is R2. Take the joint model, remove the cross-attention stack — which leaves the two
tasks sharing **zero** parameters, verified by backpropagating each loss separately — and additionally
remove the region loss entirely, confirmed by the region score collapsing to near zero. What is left is,
computationally, a lone category model. **It has now run at both datasets and it holds at both.**

### The nested decomposition

Each row removes one more thing than the row above it. All arms are paired on the same folds, one seed,
five folds, each run in the same job as its own comparand.

| | Alabama | Florida |
|---|---:|---:|
| dedicated single-task ceiling | `56.82` | `74.51` |
| joint model as shipped | `64.52` | `79.84` |
| **total category gain** | **`+7.70`** | **`+5.33`** |
| cost of removing the cross-attention stack | `-0.17` (`2.3%` of the gain) | `-0.26` (`4.9%`) |
| additional cost of then removing the region loss | `-0.03` (`0.4%`) | `+0.00` (`0.0%`) |
| **gain remaining with zero cross-task anything** | **`+7.50` = `97.4%`** | **`+5.07` = `95.2%`** |

The second-to-last row is the striking one. Having already removed the stack, additionally deleting the
entire region task costs `-0.029` points at Alabama (90 percent interval `[-0.200, +0.141]`) and `+0.003`
at Florida (interval `[-0.020, +0.025]`). The Florida interval is tight and centred on zero: **the region
task contributes nothing measurable to the category result.** That is the cleanest number in this whole
investigation, and it comes from the dataset where a multi-task reading had the best chance of surviving —
Florida is where the stack's contribution is detectable at all, and where an earlier study had reported a
positive region-to-category transfer term.

Both R2 arms are also equivalent to the full joint model within the pre-registered one-point margin
(Alabama `-0.204`, interval `[-0.412, +0.004]`; Florida `-0.256`, interval `[-0.320, -0.193]`).

So the chain is:

1. The dedicated baseline is a recurrent head reading the raw 64-dimensional check-in sequence, with no
   input encoder at all.
2. The joint model's category branch prepends a three-layer encoder (`64 -> 256 -> 256 -> 256`) and trains
   at a different batch size with per-head learning rates.
3. That difference — the added encoder depth, trained on that schedule — is what the gain rests on. It
   needs no second task, no shared parameters, and no exchange.
4. The stack as a whole then accounts for at most a few tenths of a point on top, at the larger dataset
   (the table above), and nothing measurable at the smaller one.

**The gain is therefore real and correctly reported; only its explanation changes.** The joint model does
beat the dedicated model, at every dataset, by the margins the board records. What is not supported is
attributing that to task interaction. And this is not a new suspicion: the project's own earlier
decomposition had already measured cross-task transfer at Alabama as `-0.67` points and concluded the joint
architecture was functioning as a better category encoder rather than a teacher.

**Two limits, stated because they are the first two questions a committee will ask.** First, these arms
show the gain does not depend on any cross-task pathway; they do not isolate which part of the branch
produces it, because the encoder and the schedule were never varied independently. Establishing that
requires rebuilding the dedicated baseline with the same encoder, which no study in the record has done for
the category task — the one prior encoder-transplant experiment was region-side only. Second, this is one
seed at two datasets, not the `n=20` the board uses. It is enough to redirect the mechanism sentence, and
it is not yet a board-grade number.

## 1. The vocabulary trap, before any evidence

"Shared trunk" is the dissertation's reader-facing name for the cross-attention stack. It is a
useful name for prose but it misdescribes the topology, and that matters for a mechanism claim:

- No weight in the stack is used by both tasks. Each stream keeps its own feed-forward network and
  its own layer norms (`src/models/mtl/mtlnet_crossattn/model.py:1-9` docstring: "No parameter
  sharing across tasks (each stream keeps its own FFN); information sharing is content-based via
  attention"). The stack is an *interaction subsystem*, not classical hard sharing.
- So "the shared trunk carries the semantic context" asserts both a mechanism (content transfer)
  and a topology (sharing) that the code does not implement.

Anyone rewriting this sentence should describe what the stack does (each stream reads the other's
keys and values) rather than what its nickname implies.

---

## 2. The four existing studies: what each measures

Audited 2026-08-05 against their source artifacts. Verdict for all four: **citable with scope
stated**; none is citable as a settled mechanism result.

| Study | What it varies | Scope | Category result |
|---|---|---|---|
| F50 | cross-attention ON vs OFF | Florida only, 1 seed x 5 folds, pre-v17 stack | `68.36 +- 0.74` vs `68.32 +- 0.67`, delta `-0.04 +- 0.13`, paired Wilcoxon `p=0.6250` |
| F52 | mixing output zeroed (identity cross-attention) | Florida only, 1 seed | `68.64 +- 0.91` vs `68.59 +- 0.79`, delta `+0.05` |
| F53 | cross-attention ON vs OFF swept across category-loss weight | Florida only, 1 seed, pre-P4 stack | identical at every weight; the "hyperparameter-dormant cross-attention" hypothesis is refuted in the source's own words |
| CSLSL cascade | five pins at once (see §3) | AL/AZ/FL/Istanbul, seed 0 x 5 folds | delta cat `+0.20 / +0.20 / +0.01 / -0.20` |

Two corrections to how these have been quoted:

1. **F52's "+0.30, p=0.81" is a REGION delta, not category.** The column header in
   `docs/findings/F50_RESULTS_TABLE.md:32` reads `Δreg vs H3-alt`. The category figures are the ones
   in the table above. A Chapter 5 comment block quoted the region value as if it were category; the
   inference was unaffected but the metric was wrong. Fixed 2026-08-05.
2. **The `-16.16 pp` figure used to defend F50's null is a REGION delta at Florida only**, and its
   sign flips across datasets (`AL +6.48`, `AZ -6.02`, `FL -16.16`;
   `docs/CLAIMS_AND_HYPOTHESES.md:502-504`). Its comparand, an STL value of `82.44`, is separately
   marked inflated in the project's own leak audit. It is therefore weak support for a claim about
   the *category* gain, which is why Chapter 5 stops at "we do not present the ablation as evidence
   against it either" rather than arguing the stack contributes.

---

## 3. The cascade arm: the confound is ASYMMETRIC

This is the single most misread item in the record, and it has been misread in both directions.

**The arm applies five pins together**, not one (`scripts/baselines/b4_cascade.py:141-155`):
`disable_cross_attn=True` plus `cond_coupling=posterior`, `cond_signal=softmax`, `cond_inject=add`,
`cond_detach=True`. So it removes the interaction stack *and* adds a directed category-to-region
conditioning edge in the same arm. That edge is heavily learned: its norm grows from `0.291` to
`4.613` during training at Florida (`CSLSL_CASCADE.md:80-83`).

**Region and joint columns: confounded.** The new edge can substitute for whatever the stack was
carrying toward the region task. The `0.02 pp` joint tie therefore compares *coupling topologies*
(chain versus parallel) and says nothing about the stack in isolation. **Do not cite the joint tie
as evidence about the stack.** An earlier version of this session's own analysis did exactly that.

**Category column: not confounded.** `cond_detach=True` detaches the posterior before injection
(`src/models/next/next_stan_flow_dualtower/head.py:456-457`) and the injection enters only the
region head's fused feature (`head.py:481-486`). No signal from that edge reaches the category path
in either direction, forward or backward. With the stack disabled the category path is exactly
`category_encoder -> cat_final_ln -> next_gru` (`mtlnet_crossattn_dualtower/model.py:63,72,81`), and
the two final layer norms are per-stream, exchanging nothing.

So the cascade's **category** deltas are a legitimate observation of category performance without
the interaction stack: essentially unchanged at four datasets, at seed 0 with `n=5`. That is the
record's only multi-dataset observation of its kind. It is not `n=20` and it carries the same
compensation caveat as F50: the category stream retrains under the new topology and may absorb what
the stack previously supplied.

---

## 4. What the freeze-region control does and does not establish

`W6_ENCODER_ISOLATION.md` fixes the region stream at its initial values so it can neither learn nor
teach, and the full category gain survives: `+7.63 / +6.54 / +4.64` over the dedicated ceiling at
AL/AZ/FL (`W6:20-24`), within `0.3` points of the unablated joint model.

**That control eliminates a hypothesis; it does not locate a component.** It removes region
*training*, so it cannot separate the interaction stack from the category stream's own encoder, the
per-stream feed-forward networks, or the extra depth. The study's own text concedes this at `W6:15`.

**The trap:** the W6 document is banner-titled "the joint CATEGORY win is the shared TRUNK", and
that banner overstates its own design. Chapter 5 is more honest than the document that generated the
claim. Do not "fix" the chapter toward the banner.

What the control does establish is the negative result, and Chapter 5 says exactly this: the gain is
**not** region-to-category transfer.

---

## 5. Component inventory: where the gain could enter

The joint model's category path has strictly more machinery than the dedicated model, which is why
"which component" is a real question rather than a rhetorical one.

| Component | Joint vs dedicated | Isolating control in the record? |
|---|---|---|
| Category input encoder MLP (64->256->256->256) | MORE (dedicated has none; its GRU reads the raw 64-d sequence) | pre-v17 era only, scale-conditional |
| Cross-attention read of the region stream | MORE | no clean v17 arm (F50/F53 are pre-v17, Florida only) |
| Per-stream FFN + layer norms in each block | MORE | pre-v17 only (F52, Florida) |
| `cat_final_ln` | MORE | none |
| GRU head depth and width | same topology, slightly more input params | none |
| Joint training signal | MORE | freeze-region control (see §4) |
| Optimizer recipe and batch size | DIFFERENT | tested and rejected: transplanting the joint recipe onto the bare dedicated model made it *worse* |
| Checkpoint selection rule | DIFFERENT | ruled out, `<= 0.06` points |

The decisive gap: **no control isolates the category tower's own capacity from the interaction
stack on the shipped v17 configuration.**

---

## 6. Pre-registration for the new runs (fixed 2026-08-05, BEFORE any number was read)

`STATISTICAL_PROTOCOL.md` §0 forbids reusing an equivalence margin across axes. The existing two-point
margin is pinned to the MTL-versus-dedicated **region** parity claim. The claim here is a new axis:
joint versus trunk-ablated joint, on **category**. It therefore needs its own margin, pinned in
advance.

**delta_cat = 1.0 macro-F1 point**, two-sided TOST on the paired per-fold differences.

Justification, anchored in the board rather than in preference: the category gains this margin must
not swamp run from `+5.34` (Florida) to `+9.40` (Arizona) points
(`CEILINGS_N20_FINAL.md:18-24`). One point is below a fifth of the smallest of them, so declaring
equivalence within this margin cannot be confused with declaring the gain itself absent.

**Design.** All arms use the canonical v17 recipe (`mtl_v17_complete_picture.md` §10.1) with
`--shared-lr 3e-3` at AL/AZ/FL and `1e-3` elsewhere (§10.2), five folds, seeds `{0,1,7,100}`, so
`n=20` paired (seed, fold) cells, scored by the matched scorer, category metric = 7-class macro-F1.
Comparand = the existing v17 board runs; no new comparand runs are needed.

| Arm | Change from canonical | Question it answers |
|---|---|---|
| E1 | `--model-param disable_cross_attn=True` and nothing else | does the category gain depend on the interaction stack? |
| E2 | E1 plus `--category-weight 1.0 --freeze-reg-stream` | does it depend on the region task at all, i.e. is the category tower alone enough? |

**What each outcome licenses, written before the runs so it cannot be chosen afterwards:**

- E1 equivalent within `delta_cat` and E2 equivalent to the joint model while above the dedicated
  ceiling: the gain is produced by the category branch itself under the joint recipe, and requires
  neither the region task nor the cross-attention exchange. This is an architecture-and-training
  effect, not cross-task transfer.
- E1 shows the joint model above the ablated arm: the exchange contributes to category. Quantify the
  share and scope the statement to the datasets where it holds. Only this outcome would license a
  sentence naming the stack, and it would have to name it as the *interaction* subsystem rather than
  as a shared trunk (§1).
- E2 falls back to the dedicated ceiling while E1 ties: the driver is the joint loss signal rather
  than the exchange.
- E2 above the joint model: the region task actively costs category performance. Report as bounded
  negative transfer.

A null in E1 is **not** evidence that the stack does nothing. The compensation reading applies to it
as much as to F50: with the stack removed, the category stream retrains and may absorb what the
stack supplied. What a null licenses is a statement about *dependence*, not about *contribution*.

---

## 6a. Validation of the instrument, before trusting any number

The host's own notes record three ways a job there returns exit code 0 having measured nothing (a
missing interpreter, an opt-in diagnostic left off, a wall-clock kill), so the ablation was validated
as an instrument before its results were read. Four checks, all run 2026-08-05:

**1. The flag is not a no-op — measured in the forward pass and in the backward pass.** The model was
instantiated twice, once per setting, with the cross-attention blocks wrapped in a counting shim and a
fixed input seed:

| setting | blocks present | blocks called | category output sum | block params receiving nonzero gradient |
|---|---|---|---|---|
| `disable_cross_attn=False` | 2 | **2** | `2.67125` | **1,583,104** of 1,583,104 |
| `disable_cross_attn=True` | 2 | **0** | `2.08030` | **0** of 1,583,104 |

Maximum absolute difference in the category logits: `0.538498`. The gradient column is the decisive
one: under the ablation the entire cross-attention stack is excluded from training, not merely skipped
at inference. The blocks remain constructed (so the parameter count printed in the training log is
unchanged between arms — do not use that log line to tell the arms apart), but they receive no
gradient and cannot influence the fit.

**1a. Confirmed in the real training runs, not only in the synthetic probe.** The two Alabama arms
diverge from the very first epoch on the same fold with the same seed: fold-1 validation category F1
is `0.1737` in the ablation against `0.1584` in the baseline
(`metrics/fold1_next_category_val.csv` in each run directory). Identical data, identical partition and
identical seed cannot produce divergent epoch-1 curves unless the model itself differs.

**2. The command-line boolean survives parsing.** `scripts/train.py:1283-1295` maps the literal
`"True"` to a real Python bool. Its own docstring records why this matters: `json.loads` rejects
Python-style literals, so without the mapping `KEY=False` would stay the string `"False"`, and
`bool("False")` is `True` — silently inverting every boolean parameter. Passing
`--model-param disable_cross_attn=True` therefore sets a real bool, not a truthy string.

**3. The two arms are genuinely different runs.** They land in different run directories, each ending
in its own training process id (`..._3161037` for the baseline, `..._3163304` for the ablation), which
is how the host's notes say to attribute output — never by recency, which has previously made two
concurrent jobs resolve to the same directory and produce byte-identical "different" results. The job
script also refuses to finish if the two score files hash identically, so a harvest fault cannot
present as a tie.

**4. The baseline reproduces the board.** This is the strongest check available, because it validates
the whole chain at once — data build, fold partition, recipe, scorer. The freshly run comparand scored
`64.5197` category macro-F1 at Alabama against the board's recorded `64.54`
(`CEILINGS_N20_FINAL.md:18`), a difference of `0.02` points. If any link in the chain had drifted,
this number would not have landed.

Both arms also ran inside a single job, so the fold partition, the device, and the code state are
identical between them by construction, which is what makes the per-fold pairing valid rather than
assumed.

**One provenance gap found while validating, worth fixing before the full statistical run.** The run
directory's `summary/full_summary.json` records aggregation and loss statistics but **not the model
parameters**, so `disable_cross_attn` appears nowhere in the saved artifacts of either arm. Nothing in
a harvested run directory, on its own, says which arm it is. For this smoke test the attribution is
sound because both arms ran from one script that captured each training process id and resolved the
directory by that id, and the arms are distinguishable by their epoch-1 curves — but a later reader
holding only the directories could not tell them apart. Before the `n=20` run, either write the
resolved model parameters into the run directory or keep the launcher's own mapping of process id to
arm alongside the results. The host's notes already record one case where selecting a run directory by
recency silently produced byte-identical "different" results.

## 6b. First results (smoke test, seed 0, five folds)

Deliberately scoped as a fast check rather than the full statistical run, on the author's
instruction: establish the direction first, then decide how far to take it.

**Alabama.** Baseline `64.5197`, ablation `64.3454`, delta `-0.1743` points
(per-fold `-0.4311, +0.0685, -0.4158, -0.1570, +0.0637`, sd `0.2450`).

- Two-sided paired Wilcoxon: `W=3.0`, `p=0.3125` — no detectable difference.
- 90 percent confidence interval on the difference: `[-0.4080, +0.0593]`.
- TOST against the pre-registered `1.0` point margin: `p=0.0008` — **equivalent within the margin**.

For scale, the joint model's category gain over the dedicated model at Alabama is `+7.72` points, so
the effect of removing the entire cross-attention stack is `2.3` percent of the gain it was supposed
to explain. The whole confidence interval sits inside half the margin.

**Florida is still running** and must be collected before this section is read as a two-dataset
result. Until it lands, the above is one dataset at one seed: a direction, not a result.

How to collect it (the job outlives any session, and the daemon's `compute_done` notification on this
host is unreliable — it fires within seconds with status `orphaned` while the job runs for hours, so
poll the status file instead of waiting for it):

```
job id   4a20643d-0c0e-48c4-990a-7ee33f2252d2
state    cat /home/vitor.oliveira/.claude-science-scratch/.claude-science/jobs/4a20643d-0c0e-48c4-990a-7ee33f2252d2/_status.json
results  /home/vitor.oliveira/e1_smoke_fl/{baseline,ablation}_score.json
```

The job script refuses to report success unless both arms produced a score file and the two files
differ, so a green exit with identical or missing scores cannot occur silently. When both files exist,
the paired test is the same one used for Alabama: take `cat_per_fold` from each, difference them
fold-by-fold, then a two-sided Wilcoxon and a TOST against the pre-registered `1.0` point margin.

Progress observed at 03:14Z: baseline arm at epoch 31, GPU at 98 percent. Florida is far more expensive
per fold than Alabama (which took roughly nine minutes for both arms), and it has five folds across two
arms remaining, so budget hours rather than minutes.

## 6c. Two structural facts that constrain any mechanism claim

Both were established by reading the model source in full rather than from the study documents, and
both were missed by every prior pass over this question.

### 6c.1 The two tasks are not symmetric, so an ablation does not mean the same thing on each

The region head receives the raw un-mixed sequence directly, alongside the interaction stack's output:
`out_next = self.next_poi(shared_next, raw_region_seq=next_input)`
(`mtlnet_crossattn_dualtower/model.py:129`). That is the whole point of the dual-tower design, and the
docstring says so: the private backbone processes "the un-mixed region pathway exactly as the STL reg
head does" (`:1-10`).

**The category path has no such bypass.** It reads only `self.cat_final_ln(a)` (`:72`), where `a` is
whatever the stack produced.

Measured consequence, same seed and same input, forward pass only:

| ablation | max change in category output | max change in region output |
|---|---|---|
| `disable_cross_attn` | `0.419372` | `0.045506` |
| `identity_cross_attn` | `0.464697` | `0.052482` |

Ablating the stack perturbs the category output roughly **nine times more** than the region output.
That ratio is the quantitative signature of the bypass, and it has a direct design consequence: the
region task is structurally insulated from the stack, so a cat-side ablation measured on region has
very little room to show an effect. A null there would be close to uninformative — it is what the
architecture predicts regardless of whether the category stream contributes anything.

### 6c.2 `disable_cross_attn` removes more than the exchange

Skipping the block loop (`:64-70`) removes the cross-task attention **and** everything else inside
those blocks, including each stream's own feed-forward network and layer norms — `1,583,104`
parameters in total, which the parent's `shared_parameters()` also counts as shared.

This cuts both ways and must be stated whichever way the result falls:

- The Alabama null is therefore **more** surprising, not less: removing the exchange plus 1.58M
  parameters of per-stream depth cost `0.17` points.
- But a non-null could **not** have been attributed to the mixing, because the depth was removed at
  the same time.

`identity_cross_attn` is the cleaner contrast for attribution — the blocks stay, with mixing
neutralised — and it is confirmed working on this model (table above). Any claim that the *exchange*
specifically matters should rest on that arm, not on `disable_cross_attn`.

### 6c.3 The rival ablation was already run, and it reconciles with the null

`mtlnet_crossattn_dualtower_catpriv` gives the category head its own private tower, symmetric to what
the champion does for region. Its docstring predicts a null and states the intended narrative: "reg
needs a private pathway, cat wants the shared one". That is the opposite of what our ablation found, so
one of them looked wrong.

It was run, and the record resolves the tension (`CHAMPION.md:26`). Giving category a private tower is
`+1.61` points at Florida but **craters** small states: `AL 37.66` (`-15.25` versus the champion),
`AZ 42.02` (`-12.45`), with region flat everywhere. The documented cause is not overfitting but
**underfitting**: category train-F1 caps at `0.45` against `0.98` for the shipped head, with a tiny
train-validation gap. The region head is built for thousands of classes; run off-label on a 7-class
target at small data it never converges. That line is recorded as closed.

**The reconciliation, and it sharpens the whole question.** The catpriv result is not evidence that
category needs the *shared* pathway. It is evidence that category needs *that specific head*, the GRU
one, rather than a heavy flow-attention tower. Both findings then agree on the same conclusion: what
carries the category gain is the **category branch and its head under the joint recipe**, not the
cross-task exchange. Category does not need a private tower, and — per the Alabama arm — it does not
need the shared stack either.

## 6d. What the ablation actually built, and why it reframes the question

An independent review raised this, and it is the most consequential finding of the round. It was
verified directly rather than accepted: each loss was backpropagated separately and the parameters
receiving gradient from each were intersected.

| setting | params touched by category loss only | by region loss only | **by BOTH** |
|---|---|---|---|
| trunk on | 82 tensors | 123 tensors | **54 tensors = 1,354,752 scalars** |
| trunk off | 34 tensors | 69 tensors | **0 tensors = 0 scalars** |

With the stack disabled, the two tasks share **no parameter and no computation**. The final layer norms
are per-stream (`mtlnet_crossattn/model.py:401-402`), and the region head already had its own bypass.

**So the ablated arm is not "the joint model without its trunk". It is two single-task models that
happen to be trained in one process.** And that arm scored `64.3454` category macro-F1 at Alabama,
against the dedicated single-task ceiling of `56.82` (`CEILINGS_N20_FINAL.md:18`) — roughly `+7.5`
points above it, which is essentially the entire `+7.72` point gain the joint model is credited with.

This inverts the question. The finding is not "the exchange does not matter, so some other joint
component carries the gain". It is that **the gain may not be a multi-task effect at all**: what beats
the dedicated model is plausibly the category branch's own architecture and training recipe — the input
encoder the dedicated model lacks, plus the batch size, schedule and per-head learning rates — none of
which require a second task. The project's own earlier decomposition points the same way, having
measured cross-task transfer at Alabama as `-0.67` points.

**Consequence for the defence, and it is not a small one.** The sentence under revision was about
*which component* of the joint model carries the category gain. If the next arm confirms this reading,
the honest sentence is about something else entirely: that the joint model's category advantage is an
architecture-and-recipe advantage which the dedicated baseline could in principle also have, and the
multi-task framing is not what produces it. That is a defensible and more interesting claim than
naming a component, but it must be stated deliberately rather than discovered by a reviewer.

**The arbitrating run is cheap and must come before any wording.** Take the ablation arm and set
`--category-weight 1.0`, which removes the region loss entirely. If category holds near `64.3`, the
region task contributes nothing to it and the gain is architecture-plus-recipe. If it drops toward
`56.8`, the joint loss signal matters even with no shared parameters, which would be a genuine and
publishable multi-task effect. Alabama and Florida, one seed, five folds.

## 6e. The probe set, ordered by what it discriminates

Reviewed independently and reordered as a result: the arbitrating arm comes first, because until it
lands the other probes refine a question that may be the wrong one. All at one seed and five folds, on
Alabama and Florida, per the author's instruction to stay fast rather than reach `n=20`.

| arm | change from canonical | what it discriminates | status |
|---|---|---|---|
| **R2** | `disable_cross_attn=True` **and** `--category-weight 1.0` | whether the region task contributes anything to the category result. With no shared parameters and no region loss, a category score near `64.3` means the gain is architecture and recipe, not multi-task. | **running**, Alabama, job `7b1005f6` |
| **R1** | `identity_cross_attn=True` | separates the *exchange* from the `1.58M` parameters of per-stream depth that `disable_cross_attn` also removes. Required before any sentence attributes anything to the exchange. | pending |
| **R3** | `zero_cat_kv=True`, Florida only | the content mirror the author asked about: keeps both losses on and zeroes only the category content the region stream reads. Florida only, because Alabama has no region gain to explain (`-0.31`). | pending |

`--category-weight 1.0` was verified to zero the region loss exactly: the static-weight loss builds its
weights as `[1.0 - category_weight, category_weight]` (`src/losses/static_weight/loss.py:36`), and no
guard couples that value to a freeze flag.

**Two arms were considered and rejected, with reasons, so they are not retried later.**

`--freeze-cat-stream` is the obvious-looking mirror and it is the wrong instrument. Its own coherence
guard forces `--category-weight 0.0` (`scripts/train.py:1487-1499`) because freezing the stream while
still applying the category loss is incoherent. So it freezes a *randomly initialised* category stream
and trains region alone: single-task region training, not the champion with its category side muted. It
answers a different question than the one asked.

Re-running the category-private tower was also rejected. It is not a rival hypothesis but a confounded
one: it swaps the category head from the GRU to the flow-attention tower at the same time, and the
record already documents both its Florida gain and its multi-state falsification (§6c.3).

## 6f. Two reporting corrections accepted from the review

**Report the interval, not the p-value.** The TOST arithmetic reproduces independently
(`t(4) = 7.54`), but the small p is driven entirely by a tiny fold-level standard deviation and rests on
three things this experiment cannot support: normality of five paired differences at four degrees of
freedom, independence of folds that in fact share four fifths of their training users pairwise, and zero
between-seed variance from a single seed. The two-sided Wilcoxon at `n=5` also has a p-floor of `0.0625`,
so `p=0.3125` says only "no detectable difference at this power", which is trivially true.

The citable form is therefore: *delta `-0.17` points, 90 percent interval `[-0.41, +0.06]`, inside the
pre-registered one-point margin, at one state and one seed, provisional.* The interval's upper end being
positive is part of the message: a zero or trivially positive contribution is not excluded, which is
exactly what "does not carry the gain" should mean.

**The phrase "shared trunk" fails in both directions, not just one.** §1 noted the stack shares no
weights. The review adds the converse: the project's own `shared_parameters()` accessor
(`mtlnet_crossattn/model.py:554-561`) includes the two final layer norms, and those are **outside** the
ablated loop — they keep training in both arms. So the ablation boundary and the project's own definition
of "shared" disagree at both edges: most of what the ablation removes is per-task (the feed-forward
networks), and part of what the accessor calls shared is not removed at all. Any sentence using the term
needs that footnote, or should avoid the term.

**Determinism confirmed as a side effect.** The R2 job re-ran the same champion baseline independently and
reproduced all five per-fold category values to four decimal places
(`64.6783, 65.7154, 66.0751, 65.2073, 60.9224`). Fold construction, data build and recipe are
reproducible across jobs, which is what allows arms from different jobs to be compared when they must be.

## 6g. Results: all three arms landed, and they answer the question

One seed, five folds, each arm run in the same job as its own comparand. Integrity guards passed on both
jobs: distinct run directories resolved by training process id, differing score hashes, both arms exiting
zero.

| arm | dataset | baseline | arm | delta | 90% interval | vs dedicated ceiling |
|---|---|---:|---:|---:|---|---|
| E1 trunk off, both losses | Alabama | `64.5197` | `64.3454` | `-0.1743` | `[-0.41, +0.06]` | `+7.53` pp = **97.5%** of the gain |
| E1 trunk off, both losses | Florida | `79.8387` | `79.5798` | `-0.2588` | `[-0.34, -0.18]` | `+5.07` pp = **94.9%** of the gain |
| **R2 trunk off, region loss removed** | Alabama | `64.5197` | `64.3160` | `-0.2037` | `[-0.41, +0.00]` | `+7.50` pp = **97.1%** of the gain |

All three are inside the pre-registered one-point margin. Florida's interval excludes zero, so the stack
makes a real but tiny contribution there — roughly a quarter of a point out of a `5.34` point gain. The
region side of the same arms is analysed in §0a: it too degrades slightly at Florida (`-0.10`, interval
excluding zero) and not detectably at Alabama.

Note the two are not in tension. Equivalence within a one-point margin and a nonzero contribution of a
quarter point are both true at once, and saying only one of them would misreport the result. The stack
contributes; it does not carry the gain.

**R2 carries a strong internal check.** With `--category-weight 1.0` the region score collapsed from
`69.80` to `1.13`, which confirms the region loss was genuinely removed rather than merely down-weighted.
So R2 is a category model that shares no parameter with any region computation and receives no region
gradient at all — and it still scores `64.32`, recovering `97.1` percent of the joint model's advantage
over the dedicated baseline.

### What this licenses, and what it does not

**Supported.** The category advantage over the dedicated single-task model does not come from multi-task
learning. It survives removing the cross-attention exchange, removing the per-stream depth inside those
blocks, removing every shared parameter, and removing the region loss entirely. Two datasets at opposite
ends of the scale range agree.

**Therefore the remaining explanation is the category pathway itself and the recipe it is trained under.**
The joint model's category branch has an input encoder that the dedicated baseline lacks — the dedicated
ceiling model is the GRU head reading the raw 64-dimensional sequence directly — and it trains at a
different batch size with per-head learning rates. Nothing in that requires a second task.

**Not supported, and worth stating plainly.** These arms do not identify *which* part of the pathway
matters, because the encoder and the recipe were never varied. Confirming that would need a dedicated
baseline rebuilt with the same encoder and recipe, which is a different experiment from any run here.
Nor does this reach `n=20`: it is one seed at two datasets, so it is strong enough to redirect the
mechanism sentence but not yet to be quoted as a board-grade result.

### The obvious attack, and why the record already answers it

A committee will say: *you never gave the dedicated baseline the same encoder and recipe, so your gain is
a baseline-tuning artefact.* On the recipe half, the record answers this decisively and in the direction
opposite to the objection.

The dedicated ceiling was tuned **best-versus-best**, each arm at its own optimum, with its own sweep over
batch size and learning rate (`CEILINGS_N20_FINAL.md:41-52`). The joint model's batch size *was* tried on
it: at Alabama the dedicated model peaks at the smaller batch and **loses about `0.35` points** at the
joint model's larger one, while at the three large states the larger batch is the dedicated optimum and is
what the ceiling uses.

Better still, forcing the recipe to match was tried and **deliberately rejected as baseline sabotage**.
That variant put Alabama at `53.58`, *below* the dedicated optimum, which would have inflated the reported
category gain to `+10.96` rather than `+7.72`. It is retained only as a labelled iso-budget ablation and
was never the headline (`CEILINGS_N20_FINAL.md:54-56`).

So the reported gain is measured against a baseline tuned in its own favour, and the recipe cannot be the
explanation at Alabama, since the dedicated model was *offered* the joint model's batch size and did worse
with it. What remains unmatched is the **encoder**: the dedicated model is the GRU head reading the raw
64-dimensional sequence, with no input encoder at all. That is an architectural difference between two
models each tuned at its own optimum, which is the standard and defensible form of such a comparison — not
a tuning artefact.

**The wording consequence.** The sentence under revision asked which component of the joint architecture
carries the category gain. The premise was wrong: no cross-task component carries it. The defensible
claim is that the joint model packages a better category pathway and training recipe, and its advantage
over the dedicated baseline is representational rather than multi-task. That is a more interesting claim
than naming a component, and it is also more exposed — a reviewer may ask why the dedicated baseline was
not given the same encoder. The honest answer is that the comparison is between two models as built and
tuned, and this ablation shows where the difference lives.

## 6h. The region side — a different question, and why

Everything above concerns the **category** task. The region task is not the mirror image of it, and the
asymmetry is structural rather than a matter of emphasis.

**The region task already has a private route around the stack.** The head receives `raw_region_seq` and
fuses it with the stack output, so removing the stack removes an auxiliary term rather than the region
task's whole input (§6c.1). Measured: with the stack disabled the region output moves by `0.040` while the
category output moves by `0.419`. A null on the region side is therefore weaker evidence than the same
null on the category side — it is close to what the architecture predicts either way.

**Four of the six datasets are worth running.** Region beats its dedicated ceiling at CA (`+2.20`), TX
(`+2.11`), FL (`+0.72`) **and Istanbul (`+0.28`)**; at AL (`-0.31`) and AZ (`+0.10`) it merely matches
within the two-point margin (`CEILINGS_N20_FINAL.md:19-28`, whose prose names all four: "and at Istanbul
(+0.28, non-US corpus, 520 mahalle)"). Ablating at AL or AZ would ask which component produces a gain that
is not there, and would return a null by construction, so those two stay out.

*Correction, recorded because the first version of this study got it wrong.* An earlier scoping named only
three datasets and dropped Istanbul with no stated reason. That was wrong on both counts: Istanbul does beat
its region ceiling, and it is the **cheapest** of the four (`1.7G` of built input against FL `7.7G`, CA
`17G`, TX `21G`) as well as the only non-US corpus — so it is the single arm that tests whether any region
finding generalizes beyond the Gowalla US states. It now runs first. The mis-scoped job was stopped twelve
minutes in and relaunched.

### One instrument was tested and rejected before spending compute

`zero_cat_kv` looks like the natural mirror: it zeroes the category-side keys and values that the region
stream reads, keeping both losses on. On the shipped two-block model it is **not one-directional**, and
that disqualifies it here. Measured on the same seed and input, varying only the block count:

| blocks | perturbation of category output | of region output |
|---|---:|---:|
| 1 | `0.000000` | `0.021590` |
| **2 (the shipped configuration)** | **`0.098790`** | `0.057558` |
| 3 | `0.219863` | `0.043669` |

The cause is the ordered update (`mtlnet_crossattn/model.py:168-200`). Within a block, the category stream
reads the region stream *first* — before the zeroing takes effect — so at one block the category output is
untouched, exactly `0.000000`. The region stream then reads the zeroed category content. But at block two
the category stream reads the *already-altered* region stream and is contaminated, and at the shipped
two-block depth it ends up perturbed **more** than the region stream it was supposed to isolate. No claim
of the form "the category side only" can rest on this arm.

### The arms actually running

The instrument used instead is the symmetric counterpart of what answered the category question. Verified
before launch: with the stack off and only the region loss active, **zero** category-side parameters
receive gradient, so the category stream stays at its initial values and cannot act as a helper.

| arm | pins added to the canonical recipe | question |
|---|---|---|
| baseline | none | paired comparand, same job |
| rg1 | `disable_cross_attn=True` | what is the whole stack worth to the region task? |
| rg2 | `disable_cross_attn=True` and `--category-weight 0.0` | does the region result need the category **task** at all? |

One seed, five folds, three arms per dataset, all three in one job so the fold partition, device and code
state are identical. Job `8bbb543b`. Guards: run directories resolved by each training process id, a
requirement that all three score files hash differently, a free-disk check before each arm, and a
skip-if-already-scored check so an interrupted run resumes instead of repeating.

### Run order: a one-fold triage pass first, five folds second

On the author's instruction, the region study runs as a **screen** first — three arms at one fold per
dataset — so that a large effect can close the question early instead of after `39h` of compute. Job
`f99e457b`, results under `region_1fold/`. The five-fold pass follows for whatever the screen leaves
open.

What the screen can and cannot settle is worth stating before its numbers arrive, so the reading is not
chosen afterwards. One fold gives **one number per arm**: no dispersion, no paired test, no interval. So:

- If rg2 collapses toward the region ceiling — a several-point drop — one fold shows it unambiguously and
  the region question is answered.
- If the arms land within a few tenths of each other, that is **not a null result**. It is an inconclusive
  screen, and the five-fold pass is then mandatory, because the fold-to-fold spread of this metric is wider
  than the effects at stake (the Florida category folds span `79.04` to `80.67`).

**One flag choice is load-bearing: `--only-fold 0`, never `--folds 1`.** The runner documents the trap at
`mtl_cv.py:680-688` — `--folds N` overrides the split to `max(2, N)`, so a one-fold run against a
five-fold-built transition prior "silently leaks 30-40% of val transitions into the prior, inflating reg
`top10_acc_indist` by 13-23 pp". Since region `top10` is precisely the metric under study, that leak would
manufacture the effect being looked for. `--only-fold` instead runs exactly fold 0 **of** the canonical
five-way split (`train.py:1092-1103`). Verified in the running job: the log builds all five folds
(`Fold 1/5` through `Fold 5/5`) and trains only the first, and the job asserts `n_folds == 1` in each score
file before accepting a dataset.

Two incidental findings from that verification, both benign here but worth recording:

1. The leak guard never fires for this configuration anyway. The champion pins the region prior off
   (`freeze_alpha=True`, `alpha_init=0.0`) with knowledge distillation off, so the runner takes the
   `[log_T-inert skip]` path and the prior is inert — output byte-identical. Non-inert priors are never
   skipped, so the guard still protects every configuration that *can* leak.
2. Folds are generated on the fly rather than frozen for all four datasets, and the runner warns that
   paired tests want frozen splits. Checked empirically instead of assumed: independently launched runs
   hours apart produced **identical** fold membership (Alabama `879/222` users, Florida `8484/2138`), and
   the category baselines reproduced their per-fold values to four decimals across separate jobs. The split
   is deterministic, so the pairing is sound. Freezing them would still be worth doing before the `n=20`
   promotion.

### Measured cost, and why five folds remain the measurement

Timed on the stopped run rather than estimated: one Florida epoch takes `0.50` minutes, so the cost is
`dataset size x 50 epochs` and the fold count is a multiplier on top, not the driver.

| dataset | built input | one fold | five folds | three arms at five folds |
|---|---:|---:|---:|---:|
| Istanbul | `1.7G` | `6m` | `28m` | **`1.4h`** |
| Florida | `7.7G` | `25m` | `126m` | `6.3h` |
| California | `17G` | `56m` | `278m` | `13.9h` |
| Texas | `21G` | `69m` | `344m` | `17.2h` |

The one-fold column is the triage pass, the five-fold column is the measurement. All three arms at one fold
cost about `18m` at Istanbul and `75m` at Florida, so the screen covers both cheap datasets inside two
hours; the same two at five folds cost about `7.7h`.

Note what the table implies about ordering, because it is counterintuitive: **all three arms at five folds
on Istanbul (`83m`) cost less than one arm at one fold on Texas (`69m`)**. Dataset size dominates the fold
count, so cheapest-first ordering is what buys information early — not fold reduction on the expensive
datasets. If the screen is inconclusive, the right next step is five folds on Istanbul and Florida rather
than one fold on California and Texas.

**What the outcomes will license.** If rg2 holds near the baseline at all three datasets, the region gain
is likewise not a multi-task effect and the dissertation's mechanism statement becomes symmetric across
both tasks. If rg2 falls back toward the region ceiling while rg1 holds, then the category *task* — not the
exchange — is what the region result depends on, which would be the first positive cross-task finding in
this whole investigation and would need `n=20` before it could be written. If rg1 itself falls, the stack
matters more to region than to category, which the private bypass makes unlikely but which would be worth
knowing.

### Triage result: Istanbul

Landed in about thirteen minutes for all three arms. Three distinct score hashes, `n_folds == 1` asserted
in each, run directories resolved by training process id.

| arm | region | category |
|---|---:|---:|
| baseline | `76.7195` | `64.2676` |
| rg1, stack removed | `76.6293` | `63.9675` |
| rg2, stack removed **and** category task removed | `76.5814` | `9.3102` |

**On the region task — the question being asked — nothing moves.** Removing the stack costs `-0.090`;
additionally deleting the entire category task costs a further `-0.048`, for `-0.138` in total. All three
arms sit above the dedicated region ceiling of `75.16`.

**The category column is the control that makes this credible, and it is dramatic.** In rg2 the category
score falls to `9.31` — near chance for seven classes — which is exactly what `--category-weight 0.0` should
produce: the category head never trained. So the region numbers in that row were produced by a model with
**no trained category stream at all**, and the region task lost `0.14` points. That is as direct a test of
"does region need the category task" as this codebase can express, and the answer at Istanbul is no.

*One arithmetic caution, stated so it is not misread later.* It is tempting to write that rg2 "retains 500
percent of the region gain", because `76.58` minus the ceiling `75.16` is `+1.42` against a board gain of
`+0.28`. That comparison is invalid: `76.58` is one fold at one seed, while `75.16` and the `+0.28` gain are
`n=20` figures. The one-fold baseline here is itself `76.72`, well above the `n=20` joint value of `75.44`,
so this fold is simply an easy one. **The only valid comparisons in this table are the within-column,
same-fold deltas** — which is why the screen reports those and not a percentage of the board gain.

**What this settles and what it does not.** The screen was pre-declared to be conclusive only if rg2
collapsed toward the ceiling; it did not, so by that rule this is a **strong indication, not a measurement**:
one fold gives no dispersion and no interval. But the effect size is informative in itself — a `0.14` point
total movement is far too small to be the source of a gain, and the category-collapse control rules out the
arm having silently failed. The five-fold pass is still needed to put an interval on it, and the remaining
datasets matter more than folds here: Istanbul's board gain is the smallest of the four (`+0.28`), while
California (`+2.20`) and Texas (`+2.11`) have real gains to explain.

## 7. Decisions already taken (do not reopen without new evidence)

| Date | Decision |
|---|---|
| 2026-08-04 | The Chapter 5 sentence names no component. Softened to a substantial architecture-level gain, scoped to the three datasets the freeze-region control covers. Errata row 2 in `articles/[mobiwac]/ERRATA.md`. |
| 2026-08-04 | The fixed-partition caveat was removed from Chapter 5 and the article on the author's instruction, *against* the evidence: the caveat was verified TRUE, and the frozen partition is the condition that licenses the paired tests. Errata row 3 records this so the deletion is not later mistaken for the correction of an error. |
| 2026-08-05 | delta_cat pinned at 1.0 point for the ablation axis, before any result was read (§6). |
| 2026-08-05 | The cascade's joint tie is retired as trunk evidence; only its category column is used (§3). |
| 2026-08-05 | R2 confirmed at both Alabama and Florida. Removing the region task after the stack costs `-0.03` and `+0.00` respectively, so the region task contributes nothing measurable to the category result. The mechanism question is answered at the level of dependence: the gain does not require multi-task learning. |
| 2026-08-05 | Wording rulings, from the review. Write "the gain does not require multi-task learning", never "multi-task learning contributes nothing" — retrained ablations establish non-dependence only. Do not write "representational": that word denotes the input representation map in this dissertation, and both arms read the same `check2hgi_dk_ovl` build, so the input representation is held fixed. Write "architectural". Do not attribute the stack's small deficit to the exchange: the ablation removes exchange and depth together. |

---

## 8. Open items

- **The Chapter 5 sentence is now ready to be written, and it is the author's call.** The evidence supports
  a sentence about non-dependence: the category advantage does not require the cross-task exchange, the
  shared parameters, or the region task. What it does not yet support is naming which part of the category
  branch produces it. Two defensible forms: state the non-dependence result and stop, or state it and name
  the added encoder depth as the remaining candidate while saying no control has isolated it.
- The identity arm (`identity_cross_attn=True`) remains unrun. It is the only way to say anything about the
  *exchange* specifically rather than the stack as a whole, and it would cost two runs.
- The dedicated baseline has never been rebuilt with the joint model's encoder for the **category** task
  (the one prior encoder-transplant study was region-side only). That is the experiment a committee will
  ask for if the claim is sharpened beyond non-dependence.
- Everything here is one seed. Promoting any of it to a board-grade number means the four-seed protocol.
- The private spatial path clause. "The private spatial path keeps the next-region task competitive"
  has **no isolating control anywhere in the record**, yet it is asserted in the introduction and the
  conclusion. This is the highest-severity open defect on the mechanism axis and it is not fixed by
  the runs above, which address category.
- Per-run wall-clock times for Texas, California, Arizona and Florida are unmeasured; only Alabama
  (`1.3 min`) and Istanbul (`19.3 min`) are on record for a five-fold run with
  `--no-checkpoints`.
