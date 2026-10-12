# The decision

The consecutive-visit link is a genuine leak for next-category prediction, and it is large. The
reported check-in-level representation lets the category head see a feature of the visit it is being
asked to predict. The measurement that decides this was made on the dissertation's OWN dedicated
model, not on a head written inside the study: at Alabama, the reported configuration reaches 56.86
macro-F1 and cutting the user's path at the target drops it to 28.23, a loss of 28.63 points, half the
reported value. That reproduction agrees with the published single-seed ceiling run, 55.87, to within
a point.

The number that settles it is not the size of the drop but where the drop lands. A probe given nothing
but the nine observed category labels reaches 26.69, and every honest arm lands between 27.5 and 28.5.
The check-in-level representation, once the target's own category is withheld, carries little beyond
the observed label sequence. What the reported configuration adds over that benchmark is the target.

Three structurally different ways of withholding it agree, which is what rules out an artefact of any
one intervention: withholding at readout gives 28.23, training and reading forward-only gives 27.51,
and keeping both edge directions while stripping category identity from every backward message gives
28.47. The spread across those three is smaller than one fold standard deviation. Removing the
category one-hot from the node features altogether goes the other way and costs a further 10 points,
17.46, which is 9.2 BELOW the label-only benchmark; that bounds from the opposite side how much of the
representation's legitimate value is the observed visits' own categories.

The convergence pattern is the corroborating detail. The reported run is still improving at epochs 43
to 50, while all three honest arms peak between epochs 5 and 12 and then overfit, which is the
behaviour of a model with little left to extract.

A note on instruments. The study's own smaller head measured a 35.43-point drop on a base of 61.27,
which is 57.8 percent of its base, against 50.4 percent for the reported model. The study head
therefore OVERSTATED the effect on both the absolute and the proportional measure. Its numbers were
never comparable to the published table, and only the reported-model row belongs beside Chapter 5.

Two further comparisons close the alternative explanations.

The whole-dataset question is separately clean. Training the representation on every user, then
predicting for users the representation never saw, costs 0.33 points with an interval of -0.11 to
+1.56. That is inside the two-point margin and inside the build-to-build spread, which a second
representation seed puts at 0.05 points. So the transductive concern that the earlier audit raised
does not, by itself, inflate the reported number. When the training-user restriction and the causal
graph are applied together, the loss is 35.33 points, indistinguishable from the causal graph alone.
All of the effect is the edge; none of it is the users.

The controls hold, with one exception that is recorded rather than smoothed over. A destruction
applied to a visit outside every slot's receptive field moves no vector and costs exactly zero
points, so the pipeline is not merely reacting to being perturbed. The same destruction applied to a
legitimately observed visit in the middle of the window costs 0.87 points at Alabama and 1.52 at
Florida (matched regime, the quotable one), which is the scale of losing one available visit. The
target's 34.71 points is forty times that. A graph-attention encoder, used as a positive control,
decodes the target category at 0.6256 against the reported encoder's 0.4345.

**The exception.** This study pre-registered a gate requiring the attention control to move more than
the convolutional encoder on EVERY instrument. It does so on four of five (zeroing, shuffling and
resampling the target's features, and dropping the target node), but it FAILS on the fifth: perturbing
the edge weight moves the attention control by a median 0.024 against the convolutional encoder's
0.180, roughly seven times less. The gate is therefore not met as written.

The failure is interpretable and does not undermine the decodability comparison the control exists to
calibrate. The two encoders consume the edge weight differently: the convolutional encoder multiplies
messages by the normalized scalar weight directly, so redrawing it changes every message, whereas the
attention encoder learns its own attention coefficients and treats the supplied weight as one input
among several. A control that is LESS sensitive to edge-weight noise while being MORE sensitive to
target identity is behaving as an attention mechanism should. But the gate was written before this was
understood, it is not met, and the honest report is that the control passes on the identity
instruments and fails on the weight instrument.

# What this study does not close

It is one fold, seed 0, at two datasets. The conclusion it supports is about the existence and the
approximate size of the effect, not about its variance across folds. The effect is roughly seventeen
times the two-point margin, so fold-to-fold variation of the size seen elsewhere in this project
cannot plausibly reverse the sign, but a precise magnitude would need the full five-fold, four-seed
protocol.

The strict readout is not a pure subtraction. Cutting the path at the target removes the leak, and it
also removes some legitimate structure, because the last three slots are recomputed with fewer
neighbours and a different degree normalization. The observed-visit placebo bounds that cost at 0.87
points, small against 35, but not zero. The honest statement is therefore that the strict number is a
lower bound on what a leak-free check-in-level representation could achieve, not an estimate of it.

Next region is not settled here, and the reason is structural rather than a matter of effort. The
region stream consumes region embeddings indexed by the historical places, so the target's region
vector is not an input and a region embedding is a per-region constant for the whole dataset. The
backward check-in edge cannot reach that stream. Region exposure, if any exists, would have to run
through whole-dataset representation training or through cross-attention from the category tower,
which are different channels needing different instruments.

The joint model is not measured here. Every number in this report comes from a dedicated
single-task category head trained on the representation under test. The joint model adds
cross-attention between towers, and whether the category tower's access to the target propagates
into the region tower is exactly the question this design cannot answer.

Three channels remain open and are not touched by this study: the place-level pooling that
aggregates a place's visits across the whole dataset at representation-training time; the masked
reconstruction objective, which by construction uses a place's later visits as targets; and the
region-transition prior, whose per-fold construction is a separate audit.

# What follows for the dissertation

The reported next-category numbers for the check-in-level representation cannot be presented as
prediction-time performance. Either the representation is rebuilt so that a visit's vector depends
only on visits at or before it, and the numbers are regenerated, or the reported numbers are
explicitly labelled as measured under a protocol in which the target visit is present in the graph.

The second option is weak, because the strict result sits below the label-only benchmark, which means
the contribution the dissertation attributes to the check-in-level representation for this task is
not demonstrated once the target is withheld.

The recommended path is the first: make the graph causal at construction, rebuild, and re-run. The
change is small and local; the exactness result in section 1 means it does not disturb the held-out
protocol, and the study-only builder in this study already saves the encoder needed to verify it.