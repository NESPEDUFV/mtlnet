# Fixing the consecutive-visit link: the option space, and which ones are worth running

## What has to be true of any fix

The constraint is one sentence: **the vector used to predict visit t+1 must be computable from
information available before visit t+1 happens.** Everything below is a different way of satisfying
that, and they are not equally cheap or equally likely to preserve what the representation is for.

Two measurements from the audit bound the whole space, so they are worth restating before the options.

1. A representation trained forward-only, and read forward-only, reaches 0.1932 at Alabama against a
   label-only benchmark of 0.2669. So simply removing the backward edge does NOT recover a
   representation that beats counting the nine observed labels. Any option whose only move is
   "delete the backward edge" is already measured, and it is not enough.
2. The target's category one-hot occupies columns 0 to 6 of the target NODE, and the backward edge
   puts that node one hop from the last observed visit. The leak is therefore a feature copy, not a
   subtle statistical effect. That is what makes option D below interesting: the temporal and spatial
   columns of the target node are NOT unavailable at prediction time in the same way.

## The options

### A. Forward-only graph (already measured)

Drop `edges.append([tgt, src])` at construction. A visit sees only its past.

- Cost: one line in the preprocessor, one rebuild per dataset (about 2 to 17 minutes each).
- Measured result: Alabama 0.1932, Florida 0.2420, both BELOW the label-only benchmark.
- Verdict: correct but insufficient on its own. It fixes the integrity problem and leaves the
  representation with no demonstrated advantage for this task. Worth keeping as the honest baseline
  that every other option must beat.

### B. Masked target features, bidirectional graph

Keep both edge directions, but zero the CATEGORY columns of every node when computing the vector that
will be used to predict that node. Structurally similar to masked language modelling.

- Why it might beat A: the graph keeps its two-sided connectivity, so the encoder still learns from
  the full neighbourhood during training; only the label-bearing columns of the prediction target are
  withheld. Time and place of the next visit are frequently known at prediction time in a POI setting
  (a user asks "what should I do at 8pm near here"), so withholding only the category is arguably the
  right information set rather than a compromise.
- Cost: no rebuild needed for a first read, because the audit's intervention harness already computes
  exactly this (`zero_target_cat` on the reported weights). A proper version needs a rebuild so the
  encoder is TRAINED under masking, which is one build per dataset.
- Risk: if the encoder learns to reconstruct the masked category from the temporal and spatial
  columns of the same node, the leak returns in a less visible form. That is testable with the same
  probe ladder, and it must be tested rather than assumed.

### C. Time-respecting convolution (per-visit horizon)

Keep the graph bidirectional for structure, but make message passing time-aware: when computing the
vector for visit v, allow messages only from visits with timestamp <= t_v. This is the standard
temporal-graph-network treatment.

- Why it might beat A: A deletes the backward edge for ALL purposes, including for visits deep in the
  history whose successors are legitimately observable. C deletes it only where it would look ahead of
  the prediction point, so more of the graph survives.
- Cost: an encoder change plus a rebuild. Larger than A or B.
- Note: for the two-layer encoder here, C and A coincide at the last observed slot and differ only at
  earlier slots. The audit's F5 measurement suggests that difference is small, so C's extra cost may
  buy little. Measure A and B first.

### D. Keep the edge, change the node features

Remove the category one-hot from the check-in node features entirely and let the category be carried
only by the place embedding and the temporal columns.

- Why it might beat A: it attacks the actual mechanism. The leak is a one-hot copy; if the target node
  carries no category one-hot, there is nothing to copy, and the temporal and spatial information it
  does carry is largely available at prediction time.
- Cost: one change in `_build_node_features` plus a rebuild. Comparable to A.
- Risk: the category one-hot is presumably doing useful work for the OBSERVED visits, so removing it
  may cost accuracy for a reason unrelated to the leak. The control for that is to remove it only from
  the target's role, which converges on B.

### E. Train bidirectionally, deploy causally (explicitly, as a distillation)

Train the representation on the full graph as today, then distil into a student that sees only the
past, and report the student.

- Why it might beat A: the bidirectional teacher may learn better structure, and distillation is a
  standard way to transfer it into a causal student.
- Cost: highest of the set. Two training stages plus a distillation objective.
- Verdict: not worth attempting until A and B are measured, because it is only interesting if the
  bidirectional teacher's advantage survives the transfer, and the audit gives no evidence yet that
  there is transferable advantage to move.

### F. Re-scope the claim instead of changing the model

Keep the representation and report the reported numbers as retrospective annotation rather than
prediction.

- Cost: zero compute.
- Why it is on the list: for the annotation task the two-sided context is legitimate and the numbers
  are real. This is the honest fallback if every modelling option lands at the label-only benchmark.
- Why it is not the first choice: the dissertation's research question is about prediction.

## The empirical ranking, and what to run

Ranked by information gained per GPU-hour:

1. **B, masked target category, trained under masking.** Highest value: it is the only option that
   plausibly beats A while remaining honest, its first read is nearly free from existing artifacts,
   and it directly tests whether the representation's advantage was the copy or the neighbourhood.
2. **D, drop the category one-hot from node features.** Same cost as A, attacks the mechanism, and
   its result interprets B (if D and B agree, the category columns were the whole story).
3. **A, forward-only.** Already measured. Keep as the baseline.
4. **C, time-respecting convolution.** Run only if B or D shows promise, since it is a more expensive
   way of getting A's information set with more of the graph retained.
5. **E, distillation.** Only if a bidirectional advantage is demonstrated.
6. **F, re-scope.** The fallback, and the honest answer if 1 through 4 all land at the benchmark.

Every arm is judged against the forward-only baseline from option A, measured on the same protocol
as the arm. The label-only benchmark (0.2669 at Alabama, 0.3180 at Florida) is a STUDY-INSTRUMENT
value, comparable only to other study-instrument probe results, never to a dedicated-model score.

---

# RESULTS: the options, measured on the reported dedicated model

Every row below is the dissertation's own dedicated model: `scripts/train.py --task next --model
next_gru`, batch 2048, OneCycle max_lr 0.005, 50 epochs, 5 folds, seed 0, scored by
`scripts/closing_data/score_stl_cat_ceiling.py` at the f1-best epoch. All arms share the same 96,326
windows and the same labels; they differ only in how the check-in vectors were produced. n = 5 (one
seed by five folds); the published column is n = 20.

| arm | what changes | macro-F1 | vs reported | vs forward-only floor | best epochs |
|---|---|---:|---:|---:|---|
| reported | nothing; the target visit is present | **56.86** ± 1.98 | — | +29.35 | 46, 45, 50, 43, 50 |
| B, masked backward | backward messages carry no category | 28.47 ± 0.84 | −28.39 | +0.96 | 10, 8, 5, 12, 8 |
| target withheld | readout only, path cut at the target | 28.23 ± 1.36 | −28.63 | +0.71 | 4, 8, 5, 8, 8 |
| A, forward-only | no backward edge, trained and read | 27.51 ± 1.02 | −29.35 | — | 10, 11, 6, 8, 8 |
| D, no category one-hot | the input feature is removed | 17.46 ± 0.43 | −39.40 | −10.05 | 45, 48, 45, 49, 44 |

Reference point, PENDING on this protocol: the label-only benchmark is being measured by running the same dedicated command on an engine whose input is the nine observed category one-hots alone. The 0.2669 figure quoted elsewhere in this study came from a different model at one fold and cannot be differenced against these five-fold values.

## What the numbers say

**Option B does not rescue the representation.** It was the highest-ranked option before the
measurement, and the reasoning behind it still seems right: keep the two-sided neighbourhood, let the
future say when and where it happened, withhold only which category it was. It lands at 28.47, which
is 0.96 above the forward-only floor and 0.24 above simply withholding the target at readout. Both
gaps are inside one fold standard deviation. The honest reading is that B, A, and the readout-only
intervention are the same number, and that number is about 28.

So the 28-point loss is not an artefact of how the future was withheld. Three structurally different
ways of withholding it agree. What the reported configuration had over 28 was the target's own
category identity, and no rearrangement of the edge recovers it.

**Option D is worse than the floor, and its failure is informative.** Removing the category one-hot
from every node costs a further 10 points, landing 10.05 below the forward-only arm measured on the
same protocol. That is the
cleanest evidence in this study that the category one-hot is doing legitimate work: the OBSERVED
visits' categories are the representation's main useful signal, and deleting them to prevent the copy
throws away the signal along with the leak. It also converged slowly (best epochs in the forties),
unlike the other honest arms, which is the profile of a model still extracting something from a much
weaker input rather than one that has run out of signal in four epochs.

**The convergence pattern separates the reported arm from all four others.** The reported run is still
improving at epoch 43 to 50. The three honest arms peak between epoch 5 and 12 and then overfit. D is
the exception and its slow convergence comes from a different cause, a harder and poorer input.

## Where this leaves the option space

- A, B, C are all the same answer at about 28. C was ranked below B and there is no longer a reason to
  spend GPU time on it: it is a more expensive route to the information set A and B already share, and
  A and B agree to within a fold's noise.
- D is refuted, and usefully so. It bounds how much of the reported performance is legitimate
  category signal from the observed visits.
- E, distillation, has lost its premise. It was only worth attempting if a bidirectional teacher held
  transferable advantage; three independent honest arms landing at 28 says the advantage does not
  survive removal of the copied label, so there is nothing to distil.
- F, re-scoping the claim, is now the live option rather than the fallback.

The remaining modelling question is not on this list. Every arm here withholds the target's category
and keeps everything else fixed. What has not been tried is giving the representation something it
does not currently have: the target's TIME and PLACE as an explicit query. A deployed system usually
has both, and the audit found no incremental inference path in the module at all, so that
architecture does not exist yet. It is a design change rather than a fix to the leak, and it should be
argued on its own terms rather than as an integrity repair.
