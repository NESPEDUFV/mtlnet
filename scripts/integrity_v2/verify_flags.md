
# [VERIFY] flags and what a reviewer could not confirm

1. **[VERIFY] One fold, one seed.** Every number is seed 0, fold 0. The design supports the existence
   and approximate size of the effect, not its variance across folds. The effect is roughly seventeen
   times the two-point margin, so fold variation of the size seen elsewhere in this project cannot
   plausibly reverse the sign, but a precise magnitude needs the full protocol.

2. **[VERIFY] Florida uses a 400-user subsample** (seed 12345), applied identically to every arm;
   Alabama uses all 3858 users. The subsample costs probe sensitivity: the smallest detectable
   injected signal is 0.05 at Florida against 0.02 at Alabama for the reported arm.

3. **[VERIFY] The strict readout is not a pure subtraction.** Cutting the path at the target removes
   the leak and also some legitimate structure, since the last three slots are recomputed with fewer
   neighbours and a different degree normalization. The observed-visit placebo bounds that cost at
   0.87 points (Alabama) and 1.52 (Florida), both matched-regime values. The forward-only build is
   the cleaner instrument, and it agrees with the readout-only intervention closely at Alabama
   (35.38 against 35.43, a 0.05-point gap) but less closely at Florida (31.96 against 31.17, a
   0.79-point gap). On the probes the two differ by 0.43 points at Alabama and 0.31 at Florida. Both
   gaps are small against the 31-to-35-point effect and both arms sit far below the label-only
   benchmark, so the two instruments agree on the CONCLUSION; they are not numerically
   interchangeable, and the Florida gap is larger than the Alabama one.

4. **[VERIFY] The pre-registered control gate is NOT fully met.** The gate required the
   graph-attention control to move more than the convolutional encoder on every instrument. It does
   so on four of five but fails on edge-weight perturbation, where it moves about seven times less
   (median 0.024 against 0.180). Section 3 states this and gives the mechanical reason; the
   decodability comparison the control calibrates is unaffected, but the gate as written is not
   satisfied.

5. **[VERIFY] Head architecture is this study's own, not the dissertation's.** The category head here
   is a small sequence model trained for 30 epochs on the nine-slot tensor, not the reported
   `next_gru` head inside the joint model. Absolute macro-F1 values are therefore not comparable to
   the dissertation's tables; only the WITHIN-study contrasts between arms are.

6. **[VERIFY] The joint model was not run.** Every number comes from a dedicated single-task category
   head. Whether the category tower's access to the target propagates into the region tower through
   cross-attention is untested.

7. **[VERIFY] No incremental inference path exists in the representation code.** A search of the
   check-in-level representation module found no encode, infer, or transform entry point that maps an
   arriving check-in plus its history to a vector. Embeddings are produced by one whole-graph pass in
   which every visit's successor is already present. A deployed system would need such a path, and
   its behaviour therefore cannot be measured from the current artifacts.

8. **[VERIFY] The per-window prefix self-test is a consistency check, not an independent
   verification.** Its index remap is the identity, so it exercises the same code path it is checking
   and can only catch nondeterminism or slicing errors. The real guard on the prefix scheme is the
   independently measured structural fact in section 1.

9. **[VERIFY] Three results were retracted during this study** and are not in the tables above.
   (a) A Florida ladder that paired on 2731 of 23679 windows, caused by two row-id index spaces; now
   guarded by label AND user agreement assertions plus a 95 percent pairing-retention floor. (b) A
   counterfactual whose intervention was applied per visit rather than per window, which measured the
   cost of destroying observed history rather than the target. (c) A forward-only arm read under a
   readout that still carried backward edges inside the observed window, a train and deploy mismatch
   in the arm meant to remove one; the corrected arm moved the number by 0.14 to 0.18 points and
   inference now refuses a direction mismatch. Alabama reproduced within 0.10 points after every fix,
   which is how each was confirmed harmless or harmful.

10. **[VERIFY] The shuffle arm was corrected after the reported runs.** It permuted target categories
    within each user, which is the identity for users with a single window group, so a share of
    windows received no perturbation. It now draws from a global pool. The arm is reported in the
    intervention tables for completeness; its earlier values understate the perturbation and no
    conclusion rests on it.

11. **[VERIFY] `redraw_target_edge_weight` is ambiguous** and is reported without interpretation. Its
    matched drop (6.45 at Alabama, a Florida interval spanning zero) sits between the placebo and the
    identity interventions, and this study does not separate loss of temporal information from
    renormalization of the neighbourhood.

12. **No literature claim is made in this report.** Every number is computed from repository
    artifacts named in the ledger. Nothing is attributed to a published source, so the citation
    protocol does not apply.
