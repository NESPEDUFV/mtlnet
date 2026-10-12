# More data, less quality: what would have to be true, and how to find out

_Internal scientific record. Repository paths and operational names appear here and must not appear in
dissertation prose._

## The problem, stated precisely

The enrichment study left one finding standing: on the dedicated protocol at Alabama, a model given
nothing but the nine observed category one-hots reaches 28.9964 macro-F1, and no honest check-in-level
arm reaches it. The best, elapsed time added to the canonical eleven columns, reaches 28.3461.

That is not a tolerable resting place for a representation whose purpose is to be generic. A generic
representation that loses to a seven-column one-hot on the very task it was built for has no claim to
generality, and "use the labels instead" is not a method. So the question is what would have to change
for the representation to be worth its cost, and whether more data is one of those things.

Two candidate explanations are on the table, and they are not the same claim.

**Claim A, the data claim.** The representation is underdetermined at this scale. Alabama has 113,846
check-ins over 11,848 places, so a per-place structure has on the order of ten visits per place to
learn from. With ten times the data the encoder would have enough signal, and the label-only baseline
would fall behind.

**Claim B, the capacity or pipeline claim.** Something in the encoder or in the place and region
embedding steps is throttling what the representation can express, independently of how much data is
available. Sixty-four output dimensions and two convolution layers are the two most obvious suspects,
and the hierarchical embedding steps that feed them are the next.

These predict different things and the study below separates them.

## What is already known, and what it does not settle

The strict arm sits BELOW its own label-only baseline at both datasets:

| dataset | windows | training users | reported probe | strict probe | label-only | strict minus label-only |
|---|---:|---:|---:|---:|---:|---:|
| Alabama | 96,326 | 882 | 0.4345 | 0.1975 | 0.2669 | −0.0694 |
| Florida | 23,679 | 145 | 0.4776 | 0.2388 | 0.3180 | −0.0792 |

The sign is identical at both, and the gap is slightly WIDER at the dataset with fewer windows, which
is the opposite of what Claim A predicts if window count were the operative variable. But this is not
a scaling curve and must not be read as one. Florida's window count here is the product of a
400-user subsample, not its natural size, and the two datasets differ in region count, place count,
density and geography as well as in size. Two points that differ in many ways cannot separate the
effect of one of them.

A real answer needs ONE dataset, subsampled at several fractions, with everything else held fixed.

## An arithmetic bound on what more data can buy

Before any curve is read, it is worth knowing what the counts already imply. These are quotients of
known Alabama totals, not model results.

| quantity | value |
|---|---:|
| visits per place | 9.6 |
| visits per region | 102.7 |
| visits per user | 103.4 |
| visits per DISTINCT node feature vector | 99 |

The last row is the decisive one. The encoder's input alphabet has 1,152 symbols, and at 113,846
visits it already observes each symbol about 99 times. Ten times the data would give roughly 988
observations per symbol. More samples of an alphabet that is already saturated adds nothing about the
alphabet; it helps only if what is being learned is the JOINT structure over sequences, and access to
that is limited by the receptive field rather than by volume.

The contrast with the pretext objective is instructive. That objective reconstructs a per-place mean
category composition, and 9.6 visits per place is genuinely thin: each place's target is a mean over
about ten samples. Ten times the data really would improve that estimate, to about 96 visits per place.

So the arithmetic predicted an asymmetry: more data should improve the PRETEXT task substantially
while doing little for the downstream one. **That prediction is wrong, and the measurement corrects
it.** The builder records its own best pretext loss at every fraction, and the loss RISES with data:

| training users | fraction | pretext loss |
|---:|---:|---:|
| 482 | 12.5 percent | 0.1576 |
| 964 | 25 percent | 0.1854 |
| 3,858 | 100 percent | 0.2120 |

More users make the pretext task HARDER, not better estimated. The reason is the negative sampling:
the discriminator must separate real encodings from feature-shuffled ones, and a larger, more
heterogeneous population of user sequences is simply harder to separate. A small subsample is easier
to fit.

Two consequences follow, and the second is the important one.

First, pretext loss cannot serve as a progress signal in this study. It tracks task difficulty rather
than representation quality, so the diagnostic proposed above -- watch pretext fall while downstream
stalls -- is void and must not be used. Only the downstream metric counts.

Second, and this sharpens the author's concern rather than dissolving it: if the pretext objective
becomes harder as data grows while the downstream metric does not improve, then scale is working
AGAINST this objective. Each additional user contributes sequences the discriminator must separate
without contributing anything the downstream task can use. The mismatch would then not merely limit
the method, it would worsen with exactly the generality the representation is meant to provide. The
downstream side of the curve is what decides whether that reading is right.

This is also why the depth question is sequenced before the volume question. If a two-layer encoder can
only reach two visits either side, then the joint structure that volume would help with is not reachable
at any volume, and the scaling curve would be measuring the scaling of a model that cannot use what it
is given.

## The scaling study

Design. Take Alabama. Build the representation on a nested sequence of user fractions -- 12.5, 25, 50
and 100 percent of the training users -- with an identical recipe, identical seed, and the same
forward-only honest graph. Evaluate every fraction on the SAME held-out users and the SAME windows, so
the evaluation set is constant and only the representation's training data varies. Report the dedicated
model's macro-F1 against the label-only baseline computed on that same evaluation set.

Nested subsamples matter: each smaller fraction is a subset of the larger, so the curve measures
adding data rather than swapping data.

What each outcome would mean.

- **A rising curve that crosses the label-only baseline** supports Claim A and gives an estimate of the
  data volume at which the representation starts paying for itself. That is a publishable and honest
  answer: the method works, at a scale this dataset does not reach.
- **A rising curve that does NOT cross** bounds the claim quantitatively: extrapolate the slope and
  state how much data would be required. If the extrapolation is absurd, the method as specified does
  not scale into usefulness.
- **A flat curve** refutes Claim A at this range and points the whole investigation at Claim B.
- **A falling curve** would indicate that more users introduce more heterogeneity than the encoder can
  absorb, which is itself a finding about the objective rather than about volume.

Cost: four builds at Alabama, roughly three minutes each, plus four dedicated runs at about ninety
seconds. Cheap enough to run at two encoder sizes.

## The capacity study

The author's suspicion is that the output dimension or a step of the hierarchical embedding is the
constraint. Three sub-questions, each cheap and each separately interpretable.

### C1. Output width

Sweep the encoder's output dimension over 32, 64 (the frozen reference), 128 and 256, holding
everything else fixed. The downstream head infers its input width from the artifact, so this genuinely
changes the model the dedicated command builds.

The diagnostic already in hand constrains what to expect. The honest arms recover their own visit's
category from 64 dimensions at 0.987 macro-F1, so 64 dimensions are not too few to CARRY the input
information. If width were the binding constraint, the place arms would not have been able to spend
their 64 dimensions memorizing place identity to a 0.978 probe score. Width may still matter for
holding neighbourhood structure in ADDITION to the node's own features, which is what the sweep tests.

### C2. Depth and receptive field

Sweep the number of convolution layers over 1, 2 (reference), 3 and 4. Depth is not a capacity knob
here so much as a reach knob: k layers reach index distance k along the user's path, so a two-layer
encoder sees at most two visits either side. On a graph that is a disjoint union of per-user paths with
zero cross-user edges, that is a four-visit neighbourhood, which is a small fraction of a nine-visit
window.

This is the sub-question with the clearest mechanism behind it. If the representation is meant to
encode transition structure and can only see two steps, then most of the window's structure is
invisible to it, and the downstream recurrent head is doing all the sequence modelling itself. That
would explain why the representation adds nothing over the raw labels: the labels ARE the sequence, and
the encoder is contributing a two-step smoothing of them.

### C3. The hierarchical steps

The place embedding and region embedding blocks are produced by the earlier hierarchical stage, and
the enrichment study showed the place block is actively harmful when appended to the node features.
Two checks worth running before trusting either block anywhere:

- How much of a place embedding is recoverable from its own category alone? If a place vector is
  mostly a category one-hot in disguise, then it adds nothing the node already has. The earlier
  measurement -- a probe recovering a place's own category from its embedding at 0.667 against a
  0.321 floor -- suggests it carries substantially more than category, but that was not a
  variance-explained measurement and should be made one.
- Does the region embedding table carry per-region information beyond size and adjacency? A region
  vector that is essentially a size proxy would explain why the region task saturates around 70
  percent Acc@10 regardless of the check-in representation.

## The region-in-node arm

Added in this round and worth stating separately because it is both a candidate improvement and a test
of the enrichment study's diagnosis.

Adding the visit's own REGION embedding to its node features is legitimate: the region of an observed
visit is where the user already was, and the region tower already consumes exactly that information
indexed by historical place. The target's region is never added, which would be the region task's own
label.

The diagnostic value is that a region is coarse. Alabama has 1,109 regions against 11,848 places, so a
region signature carries roughly a tenth of the per-visit uniqueness that let the place block defeat
the real-versus-shuffled discriminator. The enrichment study's diagnosis predicts that a coarser
spatial signal should be usable where a near-unique one was not. If the region arm helps while the
place arm harmed, the hijacking account is confirmed and the design rule follows directly: spatial
context is welcome at a granularity coarse enough not to identify the node.

If the region arm ALSO harms, the account needs revision, because coarseness would then not be the
operative variable.

## Order of execution

1. Region-in-node arm, standardized and projected, alongside the elapsed-time arm that is the current
   best honest configuration. One build, one evaluation.
2. Depth sweep (C2), because it has the clearest mechanism and the diagnostic already argues against
   width being binding.
3. Width sweep (C1), at the best depth.
4. Scaling curve, at the best capacity found. Running it at the reference capacity first would risk
   measuring the scaling of a throttled model.
5. The hierarchical-step checks (C3), which are probes rather than builds and cost minutes.

Every arm is judged against the label-only baseline measured on the same protocol and the same
evaluation set, never against a probe value from a different instrument.

---

# RESULTS

All values from the dedicated protocol: `scripts/train.py --task next --model next_gru`, batch 2048,
OneCycle max_lr 0.005, 50 epochs, 5 folds, seed 0, scored at the f1-best epoch. Every arm trained AND
read forward-only. The bar is the label-only benchmark on this same protocol, 28.9964 plus or minus
0.97.

## The scaling curve is flat

| training users | fraction | macro-F1 | vs bar |
|---:|---:|---:|---:|
| 482 | 12.5 percent | 28.0617 ± 0.90 | −0.93 |
| 964 | 25 percent | 28.4510 ± 0.74 | −0.55 |
| 1,929 | 50 percent | 28.6036 ± 0.71 | −0.39 |
| 3,858 | 100 percent | 28.3461 | −0.65 |

The spread across an eight-fold range of training users is 0.54 points, SMALLER than the pooled fold
standard deviation of 0.78, and the full-data point is below the half-data point. Claim A, that the
representation is merely underdetermined at this scale, is refuted at this range.

Taking the fitted slope of +0.10 macro-F1 per doubling at face value, reaching the bar would require
roughly seventy-seven times the users, on the order of a third of a million at Alabama. The fit is not
significant against the fold spread, so this is a bound rather than a forecast, and the honest reading
is that this objective does not convert data into downstream quality at any accessible scale.

## Neither depth nor width is the constraint

| encoder layers | macro-F1 | reach along the user path |
|---:|---:|---|
| 1 | 28.3322 ± 0.83 | 1 visit either side |
| 2 (frozen reference) | 28.3461 | 2 either side |
| 3 | 28.3387 ± 0.90 | 3 either side |
| 4 | 28.0532 ± 1.09 | 4 either side |

One layer equals three to within 0.014 points. This refutes the mechanism that looked most plausible
before the measurement: a two-layer encoder reaches only four of the nine window visits, so widening
its reach should have mattered, and it does not. The encoder was not using graph structure that the
downstream task needed. Four layers is slightly worse, which is the signature of over-smoothing.

| output dimension | macro-F1 |
|---:|---:|
| 32 | 27.9737 ± 0.82 |
| 64 (frozen reference) | 28.3461 |
| 128 | 27.7271 ± 1.15 |

The frozen 64 is the best of the three and doubling makes it worse, so capacity was not short. Caveat:
the 32 and 128 arms also re-express the place-table anchor, because that anchor is a fixed 64-d
distillation target in the recipe, so they are not pure width contrasts. A genuine capacity shortage
would nonetheless have shown up as 128 above 64.

One structural finding worth recording independently of the numbers. The output width appears as a hard
constant in at least three places: the encoder, the Delaunay place-table anchor (which fails outright
on a different width until the anchor is projected), and the downstream head's configured embedding
dimension, which defaults to 64 and is not inferred from the artifact. Changing the representation's
width is a coordinated edit across stages rather than a flag.

## Region identity in the node harms, like place identity

| arm | channels | pretext loss | macro-F1 | vs forward-only |
|---|---:|---:|---:|---:|
| forward-only canonical | 11 | 0.2112 | 27.5127 | — |
| canonical + elapsed | 15 | 0.2120 | 28.3461 | +0.83 |
| canonical + region proj 8 | 19 | 0.0642 | 26.9601 ± 1.59 | −0.55 |
| canonical + region proj 8 + elapsed | 23 | 0.0664 | 26.9747 ± 1.31 | −0.54 |

The prediction that a coarser spatial signal would be usable where a near-unique one was not is
refuted twice: the pretext loss collapses to 0.0642, further than raw 64-dimensional place identity at
0.0875, and the downstream score falls half a point below the forward-only baseline.

A retraction belongs here. The first region builds contained no region data at all. The region table
names its dimensions `reg_0` through `reg_63` while the parser expected `0` through `63`, so a
zero-width block was concatenated silently and both arms were byte-equivalent to their own baselines at
eleven and fifteen channels. Their pretext losses were briefly read as evidence that the region block
was safe. A zero-width enrichment block is now a hard failure, together with an assertion that the
number of assembled blocks equals the number requested.

## What the mechanism evidence supports, and what it does not

Measured over all Alabama users:

| block | adjacent-visit agreement | chance under the marginal | lift |
|---|---:|---:|---:|
| region | 0.2554 | 0.0067 | 38.3x |
| place | 0.0670 | 0.0005 | 147.6x |
| elapsed-time bin | 0.1432 | 0.0945 | 1.5x |

What holds: the two blocks that harm are both far above chance in how predictable they are from a
node's neighbourhood, while the one that helps is barely above chance. That supports a general rule --
a block the graph can already anticipate from the neighbourhood becomes a shortcut for the
real-versus-shuffled discriminator, and adding it costs downstream quality.

What does not hold: the proposed explanation for why region collapses the objective HARDER than place
fails on its own criterion, because place has the higher predictability lift. The ordering between
place and region is unexplained and is recorded as unexplained. An earlier note also described
consecutive visits as usually falling in the same region; the measured adjacent-visit agreement is
0.2554, a minority, and the 0.286 quoted previously was a 400-user estimate of that same quantity
rather than a separate, stronger statistic.

## Where this leaves the question

Five candidate explanations for the plateau have been tested and refuted: under-training, lossy
compression, insufficient depth, insufficient width, and insufficient data. Every legitimate
information channel added so far, place and region, makes matters worse, and the only gain is elapsed
time at +0.83 points, which leaves the best honest arm 0.65 below a seven-column one-hot.

The answer to "how much more data would be better" is therefore: none, at this objective. The curve is
flat over an eight-fold range while the pretext loss rises, which means scale makes the pretext task
harder without making the representation more useful. A generic representation cannot be bought with
more data or with richer inputs here; it requires an objective that rewards predicting the next
category rather than discriminating shuffled nodes and reconstructing place-level category
composition. That is the one lever this study has not pulled, and it is now the only one with evidence
behind it.
