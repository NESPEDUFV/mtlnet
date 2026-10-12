# Maximizing the information a check-in representation can give the dedicated model

_Internal scientific record. Repository paths and operational names appear here and must not appear in
dissertation prose._

The previous study answered a narrow question: does the reported number depend on the target visit?
It does, by 28.63 macro-F1 points at Alabama on the reported dedicated model, and three structurally
different honest arms all land near 28, a span narrower than one fold standard deviation. That closes the
integrity question and opens a different one, which is the question actually worth asking now: what
would make an honest check-in-level representation worth more than 28?

The answer this document argues for is not another graph topology. It is that the encoder is starved of
information the dataset already contains.

## The measurement that reframes the problem

A check-in node's feature vector has eleven columns. Read from `preprocess.py` lines 615-642:

    category one-hot           7 columns
    hour-of-day sin, cos       2 columns
    day-of-week sin, cos       2 columns

That is the entire input. Everything else the encoder knows arrives through the graph. What follows is
in the data and absent from the node vector, measured on Alabama:

| information | present in the data | reaches the encoder |
|---|---|---|
| which place was visited | 11,848 distinct places | only through pooling to a place embedding; never as a node feature |
| coordinates | in the source data | not a node feature |
| time gap to the previous visit | yes | only as the scalar edge weight |
| absolute time | 861-day span | discarded; only hour and weekday survive |
| position in the user's history | yes | not encoded |

The consequence is quantitative and severe. The eleven columns admit only **1,152 distinct feature
vectors** across 113,846 check-ins. A median of **37 different places** share one feature vector, and
the worst collides **553 places**. Two visits to a coffee shop at 9am Monday and a different coffee
shop across the state at 9am Monday are, to the encoder, the same input.

That is the reason the honest arms sit at the label-only benchmark. Once the target's category is
withheld, an eleven-column input over a path graph has almost nothing left that the nine observed
labels do not already carry. It is not that the architecture failed to exploit the information; the
information was never in the node.

Two further reference points bound what any fix must beat:

- P(next category equals current category) is **0.329** on 400 Alabama users. A "repeat the current
  category" rule is that strong before any model is trained.
- P(next region equals current region) is **0.286**. Region is heavily autocorrelated, so a region
  result must be read against a stay-put rule, not against chance.

Nearly half of consecutive pairs (**46.8 percent**) carry an edge weight below 0.01, meaning the time
gap already almost disconnects them. So for half the data the graph is barely a sequence at all, and
the node's own features are effectively the whole input.

## The option space, ordered by expected information gain

### E1. Place identity in the node (highest value, lowest risk)

Concatenate the place's learned embedding, or a learned place id embedding, onto the check-in node
features. The place is already known at prediction time for every OBSERVED visit; nothing about this
is a leak.

- Why it should matter most: it moves the input from 1,152 distinct vectors to something on the order
  of the 11,848 places. The collision measurement above is the direct argument.
- Cost: a preprocessing change plus one rebuild per dataset (roughly 3 minutes at Alabama, 17 at
  Florida). No architecture change.
- Risk: a place id embedding on 11,848 places is a large parameter block relative to the data, so it
  may overfit. Mitigation is to use the frozen place embedding the pipeline already computes rather
  than a fresh learnable table.
- Integrity: the place of an OBSERVED visit is legitimate. Do not add the place of the target.

### E2. Continuous time and elapsed time in the node

Add elapsed time since the user's previous visit, time since their first visit, and a smooth encoding
of absolute date, alongside the existing cyclic columns.

- Why it should matter: the time gap currently lives only in a scalar edge weight, and for 46.8 percent
  of pairs that weight is below 0.01, which erases the distinction between a two-day gap and a
  two-month gap. Elapsed time is also the single most informative non-category signal in next-visit
  literature.
- Cost: a preprocessing change plus one rebuild. Cheapest option on the list.
- Integrity: elapsed time up to the LAST OBSERVED visit is legitimate. The gap to the target is not,
  and must not be added as a node feature on the observed visit.

### E3. Coordinates, encoded properly

Add a spatial encoding of the visit's coordinates rather than raw latitude and longitude. The
repository's own background material already names the candidates (Space2Vec, Sphere2Vec).

- Why it should matter: it gives the encoder a notion of nearness that place identity alone does not,
  so a user's spatial habit becomes learnable rather than memorized per place.
- Cost: a preprocessing change plus a rebuild; slightly more than E1 or E2 because the encoding has
  hyperparameters.
- Note: this partially overlaps E1. Run E1 first, then E3 on top, so the increment is attributable.

### E4. The target's time and place as an explicit query

Give the model, at prediction time, what a deployed system genuinely knows about the next step: when
it is being asked, and optionally where. Predict the category conditioned on that query.

- Why this is different from every arm tested so far: all five arms in the audit withheld the target
  entirely. This withholds only the target's CATEGORY, which is the one thing that must be withheld,
  while supplying time and place, which a real query supplies.
- Why it is the most interesting and the most expensive: the module has no incremental inference path
  at all, so this is a new architecture rather than a graph edit. It is also the honest version of the
  intuition behind the masked-backward arm, which failed only because it still withheld everything.
- Integrity: this is the boundary case that needs the most care. The target's TIME is defensible (a
  query has a timestamp). The target's PLACE is defensible for a "what should I do at this place"
  product and NOT defensible for "where will this user go next," and the dissertation predicts next
  region, so supplying the target's place would leak the region task outright. Recommendation: supply
  time only, and state the choice.

### E5. Richer edges rather than richer nodes

Add place-to-place co-visitation edges, spatial proximity edges, or same-category edges, so the two-hop
neighbourhood of a visit contains more than the two adjacent visits of one user.

- Why it might matter: the graph is currently a disjoint union of per-user paths with zero cross-user
  edges. A two-layer encoder therefore sees at most four other visits, all from the same user. Almost
  all of the "graph" in this graph representation is unused.
- Cost: a preprocessing change plus a rebuild, but the edge count grows and the build slows.
- Risk: the audit's central lesson applies with full force. Any new edge must be checked for whether it
  can carry the target's category into an observed visit's receptive field. A same-category edge would
  do exactly that and must not be added. This option needs the same reach test the audit already
  built before any number from it is trusted.

### E6. Sequence-level pretraining instead of infomax

Replace or augment the infomax objective with a next-visit prediction objective on the OBSERVED prefix,
so the representation is trained for the downstream task rather than for reconstruction.

- Why it might matter: the current objective reconstructs place-level category composition, which is
  why option D failed so badly when the category columns were removed. An objective aligned with the
  downstream task would produce a representation whose value does not depend on a copied label.
- Cost: highest on the list. A new training objective plus rebuilds.
- Note: this is the option most likely to actually beat 28, and the least likely to fit the remaining
  schedule. Worth stating as future work with the measurement that motivates it.

## The recommended sequence

Ordered by information gained per GPU-hour, and structured so each result interprets the next:

1. **E1 place identity** and **E2 continuous time** together, as a single arm, then each alone if the
   combination helps. Both are preprocessing changes, both are legitimate at prediction time, and the
   collision measurement predicts E1 should dominate.
2. **E3 spatial encoding** on top of the winner of step 1.
3. **E4 time-only query**, if steps 1 and 2 clear the 28-point plateau, since it needs an architecture
   that does not yet exist and should not be built speculatively.
4. **E5 and E6** as documented future work, with E5 explicitly gated on the reach test.

Every arm is judged against reference points measured on the SAME protocol as the arm: the reported
value with the leak (56.86) and the honest plateau (about 28), both from the dedicated model at five
folds. A label-only benchmark on that protocol is being measured separately, by running the same
dedicated command on an engine whose input is the nine observed category one-hots alone; the 0.2669
figure that appears in the audit is a study-instrument probe value and may not be differenced against
dedicated-model scores. An arm that does not clear 28 by more than a fold standard deviation has not
moved the problem.

---

# RESULTS: what enrichment did, and why the objective is the real constraint

All values from the dedicated protocol: `scripts/train.py --task next --model next_gru`, batch 2048,
OneCycle max_lr 0.005, 50 epochs, 5 folds, seed 0, scored at the f1-best epoch. Every enrichment arm
is trained AND read forward-only, so all are honest by construction and comparable to each other. The
pretext column is the representation builder's own best training loss, which turns out to be the most
informative number in the table.

| arm | channels | pretext loss | macro-F1 | vs label-only bar |
|---|---:|---:|---:|---:|
| reported, target visible | 11 | 0.2174 | 56.86 | +27.86 |
| **label-only, nine one-hots** | 7 | — | **28.9964** | **the bar** |
| E2 canonical + elapsed time | 15 | 0.2120 | 28.35 | −0.65 |
| forward-only canonical | 11 | 0.2112 | 27.51 | −1.48 |
| E4 + place standardized, projected to 8 | 19 | 0.1022 | 27.10 | −1.89 |
| E5 + place proj 8 + elapsed | 23 | 0.1016 | 27.03 | −1.96 |
| E12 + raw place + elapsed | 79 | 0.0753 | 26.42 | −2.57 |
| E3 + place standardized, full 64 | 75 | 0.0770 | 25.77 | −3.23 |
| E1 + raw place | 75 | 0.0875 | 25.65 | −3.35 |

## Elapsed time is the only enrichment that helps

E2 gains 0.83 points over the eleven-column baseline from four columns, and it does so without
disturbing what the representation retains. That last part matters and is measured below.

## Place identity actively harms, and the reason is the training objective

Adding a 64-d place embedding costs 1.86 points. That is not a capacity problem and not a tuning
problem; both were tested and refuted.

**Under-training is refuted.** E2 trained for 150 epochs instead of 50 gives 28.3201 against 28.3461,
a change of −0.03, and its best epochs remain between 7 and 13 out of 150. A ten-fold lower peak
learning rate gives 28.0797. Three times the schedule changes nothing.

**Lossy compression is refuted.** A linear probe recovers the OWN category of the visit a vector
represents at 0.9870 macro-F1 for the forward-only arm and 0.9876 for E2, against a majority-class
floor of 0.3389. The honest representations preserve the feature essentially perfectly. There is no
bottleneck to blame.

**The mechanism is representation hijacking, driven by how negatives are made.** The pretext task
builds negatives by permuting node feature ROWS (`Check2HGIModule.py` line 27, `torch.randperm`), so
the discriminator is asked whether an encoding is real or feature-shuffled. With eleven columns that is
genuinely hard: only 1,152 distinct feature vectors exist, so a permuted row often looks plausible and
the encoder must use the GRAPH to separate them. That pressure is where any sequence learning comes
from. Appending a near-unique 64-d place signature makes the discrimination solvable from that block
alone, and the encoder duly reallocates itself:

| probe target | forward-only | + raw place | change |
|---|---:|---:|---:|
| own place, top 20 | 0.4660 | 0.9782 | **+0.512** |
| own category | 0.9870 | 0.7371 | **−0.250** |
| own hour bucket | 0.9958 | 0.5526 | **−0.443** |
| pretext loss | 0.2112 | 0.0875 | **−59 percent** |

The encoder becomes a place identifier and forgets both the category and the time. A pretext loss
falling by 59 percent while the downstream metric falls is the definition of a shortcut: the objective
became easier without the representation becoming better.

## The repair works in direction, not in magnitude

Two mitigations, each aimed at one half of the mechanism. Standardizing the place block removes its
scale advantage (raw mean absolute value 5.1 times the category one-hot's, maximum 12.5 against 1.0).
A fixed seeded random projection to eight dimensions destroys per-place uniqueness while keeping coarse
neighbourhood structure.

Scale was not the problem: standardizing alone moved the score by +0.12 and left the pretext loss
collapsed at 0.0770. Uniqueness was: projecting to eight dimensions raised the pretext loss to 0.1022,
about forty percent of the way back to the canonical 0.2112, and recovered 1.45 downstream points.
The predicted direction, confirmed.

But the repair is partial. E4 at 27.10 is still 0.41 BELOW the plain eleven-column baseline, and E5 at
27.03 is 1.31 below elapsed time alone. Closing the shortcut undoes most of the damage place identity
caused without making place identity worth having.

## What this changes about the option space

The information-starvation diagnosis at the top of this document was correct about the facts and wrong
about the remedy. The eleven-column input really does admit only 1,152 distinct vectors, and 37 places
really do share a median feature vector. But feeding the encoder more information does not help,
because the objective decides what survives the encoding, and this objective rewards memorizing
whatever most easily distinguishes a real node from a shuffled one.

That reorders the list:

- **E1 place identity: refuted.** Harmful raw, still slightly harmful once the shortcut is closed.
- **E2 elapsed time: the one confirmed gain**, +0.83, from four cheap columns.
- **E3 spatial encoding: not worth running.** It is a richer version of the same place information
  that E1 showed the objective misuses, and it would face the same hijacking with a larger block.
- **E5 richer edges: now contraindicated on these grounds too,** independently of the reach hazard
  already noted. More edge types give the discriminator more shortcuts.
- **E6 sequence-level pretraining: promoted to the only remaining lever with evidence behind it.**
  Under-training and compression are both refuted, so the binding constraint is the objective itself. A
  representation trained to discriminate shuffled nodes and reconstruct place-level category
  composition is not being asked to be good at next-category prediction. Aligning the pretext task with
  the downstream task is the change the measurements point at.
- **E4 target time as an explicit query: still open,** and now more attractive, because it changes what
  the model is asked to predict rather than what the encoder is fed.

The honest summary for the dissertation: no enrichment tested closes the gap to a model that simply
counts the nine observed category labels. The best honest arm remains 0.65 below that bar. That is a
statement about the pretext objective, and it is a defensible piece of future work rather than a
failure to tune.
