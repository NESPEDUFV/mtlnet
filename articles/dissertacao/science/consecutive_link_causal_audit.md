# Links between consecutive visits: a causal audit of the check-in representation

_Internal scientific record. Repository paths and operational names appear here and must not appear in dissertation prose._

> **Reading the absolute values in sections 1 to 7.** Every macro-F1 in the per-dataset sections below
> comes from a small category head written inside this study (hidden 128, one layer, 30 epochs, three
> head seeds, one fold). Those values are internally consistent, because all arms share that head, and
> they are the right basis for comparing arms to each other. They are NOT the dissertation's numbers
> and must not be placed beside Chapter 5's table. For the same arms measured with the reported
> dedicated model, see "The reported model" section further down; that is the section to quote.


# Alabama

## 1. What the graph makes possible

The check-in graph of alabama has 0 edges between different users, and every edge joins visits that are adjacent in time for one user. The graph is therefore a disjoint union of per-user paths, and two consequences follow that shape the rest of this study.

First, a user who was absent from representation training can still be encoded exactly. Encoding 30 held-out users alone reproduced their vectors from the full-graph pass to within 0.0e+00. The earlier audit could not do this and substituted one vector per place, keeping only the windows whose places appeared in training; that substitution is no longer needed.

Second, the path from the target visit into the history is short and not weak. Under two graph convolution layers the target reaches history slots [7, 8] and no others. The message from the target into the last observed visit carries a normalized weight whose median is 0.0273, against 0.7331 for that visit's own self-loop.

### 1.1 Which strict readout to use

Three ways to withhold the future were measured on the same windows. Cutting the user's path at the target moves only the slots the removed node can reach: the fraction of windows in which each slot changes, from the first to the last, is 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.05, 0.17, 0.44. Keeping only the nine observed visits also deletes the user's earlier history, which moves the first slot in 0.47 of windows for a reason unrelated to the leak. Dropping backward edges across the whole path recomputes every node's degree normalization and moves every slot (0.64 of slot-window pairs). The study therefore uses the cut at the target as its strict readout, and reports the edge-dropping variant only as a diagnostic.

## 2. Which task each channel can reach

The category stream consumes per-visit check-in vectors, so the consecutive-link path reaches it DIRECTLY: the target's own category is one hop from slot 8 and two from slot 7.

The region stream consumes region embeddings indexed by the historical places only. The target's region vector is NOT an input. A region embedding is a per-region constant for the whole dataset, so it carries no per-visit target information and the backward check-in edge cannot reach this stream at all. Region exposure runs instead through (a) whole-dataset representation training, which the users contrast measures, and (b) cross-attention from the category tower at prediction time.

Consequently, the check-in-level intervention is the right instrument for CATEGORY. For REGION the same intervention can only act through cross-attention, so a region effect under target perturbation is evidence about the joint topology, not about the backward edge. Both are reported, labelled distinctly.

## 3. Dependence is not carriage

A random-weight encoder of the same architecture already moves the last observed vector when the target's category changes, so movement alone establishes nothing. Two quantities are therefore separated: how far the vector moves, and whether the movement encodes which category the target was.

Read the unconditional median with care. About half of all windows have a near-zero temporal edge weight to their target, which is what a long gap between two visits produces, and those windows cannot move at all. The unconditional median therefore describes the gap, not the channel; the column that answers the question is the movement among windows that do move.

| arm | windows | share of windows that move | movement, all windows (median) | movement among those that move | separability by substituted category | shuffled-label floor |
|---|---:|---:|---:|---:|---:|---:|
| U1 | 4114 | 0.5401 | 0.0002 | 0.1947 | 0.0142 | 0.0002 |
| U0 | 4114 | 0.5421 | 0.0002 | 0.1989 | 0.0132 | 0.0002 |
| P1 | 4114 | 1.0000 | 0.2107 | 0.2107 | 0.0961 | 0.0002 |

## 4. What a probe can decode from one history vector

The question here is narrow: given ONE vector, the representation of the last visit a model is allowed to see, can a classifier read off the category of the NEXT visit? Every row is a different representation of that same vector, scored on the same windows with the same labels, so the rows are directly comparable to each other.

How to read the columns. `linear` and `nonlinear` are the two probes; the verdict follows the stronger one. The next three columns are the reference points a value must be judged against, not competitors: `nine-position label history` is a probe given ONLY the nine observed category labels and no embedding at all, which is the benchmark that matters, because a representation that cannot beat it adds nothing over counting what the user already did; `majority floor` is always predicting the commonest class; `shuffled-label floor` is the same probe on randomized labels, so it is the value that means no information. The last column is the smallest artificially injected signal this probe could detect, which bounds what a null result here can exclude.

The arms: `reported` is the configuration the dissertation used. `strict_prefix` is the same weights with the target visit removed from the graph. `trainonly` trained the representation without the validation users. `attention_control` is a graph-attention encoder included as a positive control. Arms ending in `_prefix` combine their training condition with the target removed.

| arm | windows | linear | nonlinear | nine-position label history | majority floor | shuffled-label floor | smallest detectable injection |
|---|---:|---:|---:|---:|---:|---:|---:|
| reported | 96326 | 0.3589 | 0.4345 | 0.2669 | 0.0728 | 0.0728 | 0.02 |
| reported_b | 96326 | 0.3626 | 0.4329 | 0.2669 | 0.0728 | 0.0731 | 0.02 |
| strict_prefix | 96326 | 0.1806 | 0.1975 | 0.2669 | 0.0728 | 0.0731 | 0.02 |
| trainonly | 96326 | 0.3590 | 0.4334 | 0.2669 | 0.0728 | 0.0728 | 0.02 |
| trainonly_prefix | 96326 | 0.1837 | 0.2005 | 0.2669 | 0.0728 | 0.0730 | 0.02 |
| attention_control | 96326 | 0.4953 | 0.6256 | 0.2669 | 0.0728 | 0.0729 | 0.02 |

Every probe split is user-disjoint and every value is the mean over 10 classifier seeds.

## 5. What the predictor's own metric does

**What is compared here.** Each row is the same trained-from-scratch category predictor fed a DIFFERENT representation of the same validation windows, with the same labels. The comparison is always row-against-the-reported-row, and the `drop` columns are that difference in macro-F1 points. A positive drop means the arm is WORSE than the reported configuration.

**These absolute values are not the dissertation's.** The head here is this study's own small model at one fold, not the tuned `next_gru` at n=20, so the reported row will not match Chapter 5's table. Only the differences between rows carry, and only within this table.

The dedicated category model is trained on the reported representation (0.6127 macro-F1 over 3 seeds) and then each arm is evaluated in two regimes. Transfer keeps those frozen weights, so it bounds how much the fitted predictor leans on the target. Matched retrains on the arm's own representation, which is the contrast that answers what the reported number becomes under a protocol that never sees the future.

| arm | transfer macro-F1 | transfer drop | matched macro-F1 | matched drop | matched 95% CI |
|---|---:|---:|---:|---:|---:|
| zero_target_cat | 0.2747 | +33.80 | 0.2655 | +34.71 | +22.58 to +45.99 |
| resample_target_all | 0.2351 | +37.75 | 0.2549 | +35.77 | +23.91 to +47.03 |
| redraw_edge | 0.4895 | +12.32 | 0.5482 | +6.45 | -4.62 to +16.23 |
| placebo_far_future | 0.6127 | +0.00 | 0.6127 | +0.00 | +0.00 to +0.00 |
| placebo_observed | 0.5897 | +2.29 | 0.6039 | +0.87 | +0.13 to +1.73 |
| strict_prefix | 0.2714 | +34.13 | 0.2583 | +35.43 | +22.78 to +46.64 |
| trainonly_full | 0.1265 | +48.61 | 0.6094 | +0.33 | -0.11 to +1.56 |
| trainonly_prefix | 0.1296 | +48.31 | 0.2594 | +35.33 | +23.69 to +47.07 |
| build_variance_U1b | 0.1058 | +50.69 | 0.6122 | +0.05 | -0.70 to +0.79 |

## 6. Is the loss a leak, or a train-and-deploy mismatch?

An objection worth taking seriously: the encoder is supposed to learn transition structure, and withholding the target at readout from weights that were trained with it present measures a mismatch between training and deployment as much as it measures a leak. The arm below removes that objection. It trains the representation on a forward-only graph, so no visit sees its own future at any point, in training or at readout. If the check-in-level representation carries transferable structure, this arm should beat the label-only benchmark.

**What is compared.** Every row is the same probe on the same windows; the rows differ only in which edges existed when the representation was built (`training graph`) and which existed when the vectors were read out (`readout`). The last column is the difference against the label-only benchmark, so a NEGATIVE value means the embedding is worse than simply counting the nine observed category labels.

| arm | training graph | readout | nonlinear probe | vs label-only benchmark |
|---|---|---|---:|---:|
| reported | bidirectional | target present, both directions | 0.4345 | +16.75 |
| strict_readout_biTrained | bidirectional | path cut at target | 0.1975 | -6.94 |
| causal_C1_matched | forward-only | cut at target AND forward-only (matched) | 0.1932 | -7.37 |
| causal_C1_mismatched | forward-only | cut at target only (deliberate mismatch) | 0.1946 | -7.23 |

The label-only benchmark is 0.2669, a linear probe on the nine observed category labels and nothing else.

In the predictor's own metric:

| arm | matched macro-F1 | change from reported | 95% CI |
|---|---:|---:|---:|
| reported | 0.6127 | reference | |
| strict_readout_biTrained | 0.2583 | +35.43 | +22.78 to +46.64 |
| causal_C1_matched | 0.2588 | +35.38 | +23.37 to +46.60 |
| causal_C1_mismatched | 0.2605 | +35.22 | +22.87 to +45.63 |

## 7. The pre-registered comparisons

Thresholds fixed before results were read: a change of at least 2.0 macro-F1 points is material (the dissertation's own registered margin); 0.5 to 2.0 points is detectable but below that margin; invariance means a relative change at or below 1e-05.

| comparison | measured | pre-registered branch |
|---|---:|---|
| zero_target_cat | +34.71 points | material |
| resample_target_all | +35.77 points | material |
| redraw_edge | +6.45 points | material |
| placebo_far_future | +0.00 points | no material effect detected (this arm must show no effect; a nonzero value indicts the pipeline) |
| placebo_observed | +0.87 points | detectable, below the margin |
| strict_prefix | +35.43 points | material |
| trainonly_full | +0.33 points | no material effect detected |
| trainonly_prefix | +35.33 points | material |
| build_variance_U1b | +0.05 points | no material effect detected |

# Florida

## 1. What the graph makes possible

The check-in graph of florida has 0 edges between different users, and every edge joins visits that are adjacent in time for one user. The graph is therefore a disjoint union of per-user paths, and two consequences follow that shape the rest of this study.

First, a user who was absent from representation training can still be encoded exactly. Encoding 30 held-out users alone reproduced their vectors from the full-graph pass to within 0.0e+00. The earlier audit could not do this and substituted one vector per place, keeping only the windows whose places appeared in training; that substitution is no longer needed.

Second, the path from the target visit into the history is short and not weak. Under two graph convolution layers the target reaches history slots [7, 8] and no others. The message from the target into the last observed visit carries a normalized weight whose median is 0.2784, against 0.5019 for that visit's own self-loop.

### 1.1 Which strict readout to use

Three ways to withhold the future were measured on the same windows. Cutting the user's path at the target moves only the slots the removed node can reach: the fraction of windows in which each slot changes, from the first to the last, is 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.19, 0.33, 0.54. Keeping only the nine observed visits also deletes the user's earlier history, which moves the first slot in 0.52 of windows for a reason unrelated to the leak. Dropping backward edges across the whole path recomputes every node's degree normalization and moves every slot (0.70 of slot-window pairs). The study therefore uses the cut at the target as its strict readout, and reports the edge-dropping variant only as a diagnostic.

## 2. Which task each channel can reach

The category stream consumes per-visit check-in vectors, so the consecutive-link path reaches it DIRECTLY: the target's own category is one hop from slot 8 and two from slot 7.

The region stream consumes region embeddings indexed by the historical places only. The target's region vector is NOT an input. A region embedding is a per-region constant for the whole dataset, so it carries no per-visit target information and the backward check-in edge cannot reach this stream at all. Region exposure runs instead through (a) whole-dataset representation training, which the users contrast measures, and (b) cross-attention from the category tower at prediction time.

Consequently, the check-in-level intervention is the right instrument for CATEGORY. For REGION the same intervention can only act through cross-attention, so a region effect under target perturbation is evidence about the joint topology, not about the backward edge. Both are reported, labelled distinctly.

## 3. Dependence is not carriage

A random-weight encoder of the same architecture already moves the last observed vector when the target's category changes, so movement alone establishes nothing. Two quantities are therefore separated: how far the vector moves, and whether the movement encodes which category the target was.

Read the unconditional median with care. About half of all windows have a near-zero temporal edge weight to their target, which is what a long gap between two visits produces, and those windows cannot move at all. The unconditional median therefore describes the gap, not the channel; the column that answers the question is the movement among windows that do move.

| arm | windows | share of windows that move | movement, all windows (median) | movement among those that move | separability by substituted category | shuffled-label floor |
|---|---:|---:|---:|---:|---:|---:|
| U1 | 4039 | 0.6994 | 0.1283 | 0.1992 | 0.0352 | 0.0002 |
| U0 | 4039 | 0.6992 | 0.1535 | 0.2426 | 0.0337 | 0.0002 |
| P1 | 4039 | 1.0000 | 0.1883 | 0.1883 | 0.0784 | 0.0002 |

## 4. What a probe can decode from one history vector

The question here is narrow: given ONE vector, the representation of the last visit a model is allowed to see, can a classifier read off the category of the NEXT visit? Every row is a different representation of that same vector, scored on the same windows with the same labels, so the rows are directly comparable to each other.

How to read the columns. `linear` and `nonlinear` are the two probes; the verdict follows the stronger one. The next three columns are the reference points a value must be judged against, not competitors: `nine-position label history` is a probe given ONLY the nine observed category labels and no embedding at all, which is the benchmark that matters, because a representation that cannot beat it adds nothing over counting what the user already did; `majority floor` is always predicting the commonest class; `shuffled-label floor` is the same probe on randomized labels, so it is the value that means no information. The last column is the smallest artificially injected signal this probe could detect, which bounds what a null result here can exclude.

The arms: `reported` is the configuration the dissertation used. `strict_prefix` is the same weights with the target visit removed from the graph. `trainonly` trained the representation without the validation users. `attention_control` is a graph-attention encoder included as a positive control. Arms ending in `_prefix` combine their training condition with the target removed.

| arm | windows | linear | nonlinear | nine-position label history | majority floor | shuffled-label floor | smallest detectable injection |
|---|---:|---:|---:|---:|---:|---:|---:|
| reported | 23679 | 0.4075 | 0.4776 | 0.3180 | 0.0719 | 0.1103 | 0.05 |
| strict_prefix | 23679 | 0.2426 | 0.2388 | 0.3180 | 0.0719 | 0.1057 | 0.02 |
| trainonly | 23679 | 0.3993 | 0.4789 | 0.3180 | 0.0719 | 0.1044 | 0.02 |
| trainonly_prefix | 23679 | 0.2485 | 0.2390 | 0.3180 | 0.0719 | 0.1039 | 0.02 |
| attention_control | 23679 | 0.5041 | 0.5866 | 0.3180 | 0.0719 | 0.0978 | 0.02 |

Every probe split is user-disjoint and every value is the mean over 10 classifier seeds.

## 5. What the predictor's own metric does

**What is compared here.** Each row is the same trained-from-scratch category predictor fed a DIFFERENT representation of the same validation windows, with the same labels. The comparison is always row-against-the-reported-row, and the `drop` columns are that difference in macro-F1 points. A positive drop means the arm is WORSE than the reported configuration.

**These absolute values are not the dissertation's.** The head here is this study's own small model at one fold, not the tuned `next_gru` at n=20, so the reported row will not match Chapter 5's table. Only the differences between rows carry, and only within this table.

The dedicated category model is trained on the reported representation (0.6272 macro-F1 over 3 seeds) and then each arm is evaluated in two regimes. Transfer keeps those frozen weights, so it bounds how much the fitted predictor leans on the target. Matched retrains on the arm's own representation, which is the contrast that answers what the reported number becomes under a protocol that never sees the future.

| arm | transfer macro-F1 | transfer drop | matched macro-F1 | matched drop | matched 95% CI |
|---|---:|---:|---:|---:|---:|
| zero_target_cat | 0.3256 | +30.17 | 0.3220 | +30.52 | +17.87 to +41.09 |
| resample_target_all | 0.2719 | +35.54 | 0.3124 | +31.49 | +18.70 to +41.55 |
| redraw_edge | 0.5655 | +6.17 | 0.5807 | +4.66 | -6.34 to +12.05 |
| placebo_far_future | 0.6272 | +0.00 | 0.6272 | +0.00 | +0.00 to +0.00 |
| placebo_observed | 0.6110 | +1.62 | 0.6121 | +1.52 | -0.12 to +2.06 |
| strict_prefix | 0.3212 | +30.60 | 0.3156 | +31.17 | +18.14 to +41.82 |
| trainonly_full | 0.1421 | +48.51 | 0.6178 | +0.95 | -0.35 to +3.31 |
| trainonly_prefix | 0.1352 | +49.21 | 0.3118 | +31.54 | +18.12 to +42.46 |

## 6. Is the loss a leak, or a train-and-deploy mismatch?

An objection worth taking seriously: the encoder is supposed to learn transition structure, and withholding the target at readout from weights that were trained with it present measures a mismatch between training and deployment as much as it measures a leak. The arm below removes that objection. It trains the representation on a forward-only graph, so no visit sees its own future at any point, in training or at readout. If the check-in-level representation carries transferable structure, this arm should beat the label-only benchmark.

**What is compared.** Every row is the same probe on the same windows; the rows differ only in which edges existed when the representation was built (`training graph`) and which existed when the vectors were read out (`readout`). The last column is the difference against the label-only benchmark, so a NEGATIVE value means the embedding is worse than simply counting the nine observed category labels.

| arm | training graph | readout | nonlinear probe | vs label-only benchmark |
|---|---|---|---:|---:|
| reported | bidirectional | target present, both directions | 0.4776 | +15.96 |
| strict_readout_biTrained | bidirectional | path cut at target | 0.2388 | -7.92 |
| causal_C1_matched | forward-only | cut at target AND forward-only (matched) | 0.2420 | -7.60 |
| causal_C1_mismatched | forward-only | cut at target only (deliberate mismatch) | 0.2402 | -7.78 |

The label-only benchmark is 0.3180, a linear probe on the nine observed category labels and nothing else.

In the predictor's own metric:

| arm | matched macro-F1 | change from reported | 95% CI |
|---|---:|---:|---:|
| reported | 0.6272 | reference | |
| strict_readout_biTrained | 0.3156 | +31.17 | +18.14 to +41.82 |
| causal_C1_matched | 0.3077 | +31.96 | +19.01 to +41.63 |
| causal_C1_mismatched | 0.3127 | +31.45 | +18.48 to +41.54 |

## 7. The pre-registered comparisons

Thresholds fixed before results were read: a change of at least 2.0 macro-F1 points is material (the dissertation's own registered margin); 0.5 to 2.0 points is detectable but below that margin; invariance means a relative change at or below 1e-05.

| comparison | measured | pre-registered branch |
|---|---:|---|
| zero_target_cat | +30.52 points | material |
| resample_target_all | +31.49 points | material |
| redraw_edge | +4.66 points | material |
| placebo_far_future | +0.00 points | no material effect detected (this arm must show no effect; a nonzero value indicts the pipeline) |
| placebo_observed | +1.52 points | detectable, below the margin |
| strict_prefix | +31.17 points | material |
| trainonly_full | +0.95 points | detectable, below the margin |
| trainonly_prefix | +31.54 points | material |

# Numbers ledger

| value | unit | file | field | meaning | dataset |
|---:|---|---|---|---|---|
| 0 | edges | `f0_structure.json :: per_state.alabama` | `F1_disjoint_user_paths.cross_user_edges` | cross-user check-in edges | alabama |
| 0.0 | abs | `f0_structure.json :: per_state.alabama` | `F2_heldout_exactness.max_abs_diff_vs_full_graph` | held-out user encoded alone vs inside the full graph | alabama |
| 0.027262988017628567 | coefficient | `f0_structure.json :: per_state.alabama` | `F3_backward_coefficient.backward_coef_median` | GCN-normalized weight of the message from the target into the last observed visit | alabama |
| 0.7330569469861861 | coefficient | `f0_structure.json :: per_state.alabama` | `F3_backward_coefficient.self_loop_coef_median` | the same node's self-loop weight | alabama |
| 0.11110752166080734 | relative | `f0_structure.json :: per_state.alabama` | `F4_receptive_field.slot8_rel_change_median` | movement of the last observed vector when the target's category is zeroed | alabama |
| 0.07444444444444444 | fraction | `f0_structure.json :: per_state.alabama` | `F5_truncation_vs_edge_drop.R_prefix_cut_at_target.mean_frac_slots_moved` | share of slot-window pairs moved by the prefix readout | alabama |
| 0.15925925925925927 | fraction | `f0_structure.json :: per_state.alabama` | `F5_truncation_vs_edge_drop.R_window_nine_nodes_only.mean_frac_slots_moved` | share of slot-window pairs moved by the window readout | alabama |
| 0.6437037037037037 | fraction | `f0_structure.json :: per_state.alabama` | `F5_truncation_vs_edge_drop.R_fwd_backward_edges_dropped.mean_frac_slots_moved` | share of slot-window pairs moved by the edge_drop readout | alabama |
| 0.5401069518716578 | fraction | `alabama/intervention.json` | `arms.U1.zero_cat.frac_windows_moved` | share of windows whose last observed vector moves when the target category is zeroed | alabama |
| 0.1946765035390854 | relative | `alabama/intervention.json` | `arms.U1.zero_cat.rel_linf_median_among_moved` | movement among windows that move (the unconditional median is dominated by windows with a near-zero edge weight to the target) | alabama |
| 0.014165699829113209 | ratio | `alabama/intervention.json` | `arms.U1.carriage.fisher_ratio_by_substituted_class` | separability of the history vector by which category was substituted | alabama |
| 0.00018282973594316084 | ratio | `alabama/intervention.json` | `arms.U1.carriage.fisher_ratio_shuffled_labels_control` | the same statistic with labels shuffled: the floor it must beat | alabama |
| 0.5420515313563442 | fraction | `alabama/intervention.json` | `arms.U0.zero_cat.frac_windows_moved` | share of windows whose last observed vector moves when the target category is zeroed | alabama |
| 0.1989426612854004 | relative | `alabama/intervention.json` | `arms.U0.zero_cat.rel_linf_median_among_moved` | movement among windows that move (the unconditional median is dominated by windows with a near-zero edge weight to the target) | alabama |
| 0.013215070305532105 | ratio | `alabama/intervention.json` | `arms.U0.carriage.fisher_ratio_by_substituted_class` | separability of the history vector by which category was substituted | alabama |
| 0.0001940856860756518 | ratio | `alabama/intervention.json` | `arms.U0.carriage.fisher_ratio_shuffled_labels_control` | the same statistic with labels shuffled: the floor it must beat | alabama |
| 1.0 | fraction | `alabama/intervention.json` | `arms.P1.zero_cat.frac_windows_moved` | share of windows whose last observed vector moves when the target category is zeroed | alabama |
| 0.210731640458107 | relative | `alabama/intervention.json` | `arms.P1.zero_cat.rel_linf_median_among_moved` | movement among windows that move (the unconditional median is dominated by windows with a near-zero edge weight to the target) | alabama |
| 0.09614182794198264 | ratio | `alabama/intervention.json` | `arms.P1.carriage.fisher_ratio_by_substituted_class` | separability of the history vector by which category was substituted | alabama |
| 0.0001766238857745572 | ratio | `alabama/intervention.json` | `arms.P1.carriage.fisher_ratio_shuffled_labels_control` | the same statistic with labels shuffled: the floor it must beat | alabama |
| 0.43445134689153375 | macro-F1 | `alabama/probe_ladder.json` | `arms.reported.slot8.mlp.mean` | nonlinear probe on the last observed vector | alabama |
| 0.02 | epsilon | `alabama/probe_ladder.json` | `arms.reported.calibration_slot8.min_detectable_epsilon` | smallest injected signal this probe detects | alabama |
| 0.43286969243664697 | macro-F1 | `alabama/probe_ladder.json` | `arms.reported_b.slot8.mlp.mean` | nonlinear probe on the last observed vector | alabama |
| 0.02 | epsilon | `alabama/probe_ladder.json` | `arms.reported_b.calibration_slot8.min_detectable_epsilon` | smallest injected signal this probe detects | alabama |
| 0.1975291485631855 | macro-F1 | `alabama/probe_ladder.json` | `arms.strict_prefix.slot8.mlp.mean` | nonlinear probe on the last observed vector | alabama |
| 0.02 | epsilon | `alabama/probe_ladder.json` | `arms.strict_prefix.calibration_slot8.min_detectable_epsilon` | smallest injected signal this probe detects | alabama |
| 0.4333500928235944 | macro-F1 | `alabama/probe_ladder.json` | `arms.trainonly.slot8.mlp.mean` | nonlinear probe on the last observed vector | alabama |
| 0.02 | epsilon | `alabama/probe_ladder.json` | `arms.trainonly.calibration_slot8.min_detectable_epsilon` | smallest injected signal this probe detects | alabama |
| 0.2005235368338158 | macro-F1 | `alabama/probe_ladder.json` | `arms.trainonly_prefix.slot8.mlp.mean` | nonlinear probe on the last observed vector | alabama |
| 0.02 | epsilon | `alabama/probe_ladder.json` | `arms.trainonly_prefix.calibration_slot8.min_detectable_epsilon` | smallest injected signal this probe detects | alabama |
| 0.6255868538962515 | macro-F1 | `alabama/probe_ladder.json` | `arms.attention_control.slot8.mlp.mean` | nonlinear probe on the last observed vector | alabama |
| 0.02 | epsilon | `alabama/probe_ladder.json` | `arms.attention_control.calibration_slot8.min_detectable_epsilon` | smallest injected signal this probe detects | alabama |
| 0.6126598097592716 | macro-F1 | `alabama/counterfactual.json` | `intact.mean_macro_f1` | the reported representation | alabama |
| 34.711402022415164 | macro-F1 points | `alabama/counterfactual.json` | `arms.zero_target_cat.matched.drop_points` | change from the reported representation, zero_target_cat, retrained | alabama |
| 35.77387844150745 | macro-F1 points | `alabama/counterfactual.json` | `arms.resample_target_all.matched.drop_points` | change from the reported representation, resample_target_all, retrained | alabama |
| 6.447565025215796 | macro-F1 points | `alabama/counterfactual.json` | `arms.redraw_edge.matched.drop_points` | change from the reported representation, redraw_edge, retrained | alabama |
| 0.0 | macro-F1 points | `alabama/counterfactual.json` | `arms.placebo_far_future.matched.drop_points` | change from the reported representation, placebo_far_future, retrained | alabama |
| 0.873312368312773 | macro-F1 points | `alabama/counterfactual.json` | `arms.placebo_observed.matched.drop_points` | change from the reported representation, placebo_observed, retrained | alabama |
| 35.43453359175238 | macro-F1 points | `alabama/counterfactual.json` | `arms.strict_prefix.matched.drop_points` | change from the reported representation, strict_prefix, retrained | alabama |
| 0.3288338628693932 | macro-F1 points | `alabama/counterfactual.json` | `arms.trainonly_full.matched.drop_points` | change from the reported representation, trainonly_full, retrained | alabama |
| 35.33051886873694 | macro-F1 points | `alabama/counterfactual.json` | `arms.trainonly_prefix.matched.drop_points` | change from the reported representation, trainonly_prefix, retrained | alabama |
| 0.047618508631352974 | macro-F1 points | `alabama/counterfactual.json` | `arms.build_variance_U1b.matched.drop_points` | change from the reported representation, build_variance_U1b, retrained | alabama |
| 0 | edges | `f0_structure.json :: per_state.florida` | `F1_disjoint_user_paths.cross_user_edges` | cross-user check-in edges | florida |
| 0.0 | abs | `f0_structure.json :: per_state.florida` | `F2_heldout_exactness.max_abs_diff_vs_full_graph` | held-out user encoded alone vs inside the full graph | florida |
| 0.27843745391358676 | coefficient | `f0_structure.json :: per_state.florida` | `F3_backward_coefficient.backward_coef_median` | GCN-normalized weight of the message from the target into the last observed visit | florida |
| 0.5019444299590399 | coefficient | `f0_structure.json :: per_state.florida` | `F3_backward_coefficient.self_loop_coef_median` | the same node's self-loop weight | florida |
| 1.3826515861642536e-07 | relative | `f0_structure.json :: per_state.florida` | `F4_receptive_field.slot8_rel_change_median` | movement of the last observed vector when the target's category is zeroed | florida |
| 0.11814814814814815 | fraction | `f0_structure.json :: per_state.florida` | `F5_truncation_vs_edge_drop.R_prefix_cut_at_target.mean_frac_slots_moved` | share of slot-window pairs moved by the prefix readout | florida |
| 0.2285185185185185 | fraction | `f0_structure.json :: per_state.florida` | `F5_truncation_vs_edge_drop.R_window_nine_nodes_only.mean_frac_slots_moved` | share of slot-window pairs moved by the window readout | florida |
| 0.6966666666666667 | fraction | `f0_structure.json :: per_state.florida` | `F5_truncation_vs_edge_drop.R_fwd_backward_edges_dropped.mean_frac_slots_moved` | share of slot-window pairs moved by the edge_drop readout | florida |
| 0.6994305521168606 | fraction | `florida/intervention.json` | `arms.U1.zero_cat.frac_windows_moved` | share of windows whose last observed vector moves when the target category is zeroed | florida |
| 0.1992228627204895 | relative | `florida/intervention.json` | `arms.U1.zero_cat.rel_linf_median_among_moved` | movement among windows that move (the unconditional median is dominated by windows with a near-zero edge weight to the target) | florida |
| 0.035241918705334045 | ratio | `florida/intervention.json` | `arms.U1.carriage.fisher_ratio_by_substituted_class` | separability of the history vector by which category was substituted | florida |
| 0.00018305681568249853 | ratio | `florida/intervention.json` | `arms.U1.carriage.fisher_ratio_shuffled_labels_control` | the same statistic with labels shuffled: the floor it must beat | florida |
| 0.6991829660807131 | fraction | `florida/intervention.json` | `arms.U0.zero_cat.frac_windows_moved` | share of windows whose last observed vector moves when the target category is zeroed | florida |
| 0.24258220195770264 | relative | `florida/intervention.json` | `arms.U0.zero_cat.rel_linf_median_among_moved` | movement among windows that move (the unconditional median is dominated by windows with a near-zero edge weight to the target) | florida |
| 0.03372404522300333 | ratio | `florida/intervention.json` | `arms.U0.carriage.fisher_ratio_by_substituted_class` | separability of the history vector by which category was substituted | florida |
| 0.00017965062670056382 | ratio | `florida/intervention.json` | `arms.U0.carriage.fisher_ratio_shuffled_labels_control` | the same statistic with labels shuffled: the floor it must beat | florida |
| 1.0 | fraction | `florida/intervention.json` | `arms.P1.zero_cat.frac_windows_moved` | share of windows whose last observed vector moves when the target category is zeroed | florida |
| 0.18825572729110718 | relative | `florida/intervention.json` | `arms.P1.zero_cat.rel_linf_median_among_moved` | movement among windows that move (the unconditional median is dominated by windows with a near-zero edge weight to the target) | florida |
| 0.07837117825034476 | ratio | `florida/intervention.json` | `arms.P1.carriage.fisher_ratio_by_substituted_class` | separability of the history vector by which category was substituted | florida |
| 0.0001759734777529717 | ratio | `florida/intervention.json` | `arms.P1.carriage.fisher_ratio_shuffled_labels_control` | the same statistic with labels shuffled: the floor it must beat | florida |
| 0.4775976091427028 | macro-F1 | `florida/probe_ladder.json` | `arms.reported.slot8.mlp.mean` | nonlinear probe on the last observed vector | florida |
| 0.05 | epsilon | `florida/probe_ladder.json` | `arms.reported.calibration_slot8.min_detectable_epsilon` | smallest injected signal this probe detects | florida |
| 0.2388403576648261 | macro-F1 | `florida/probe_ladder.json` | `arms.strict_prefix.slot8.mlp.mean` | nonlinear probe on the last observed vector | florida |
| 0.02 | epsilon | `florida/probe_ladder.json` | `arms.strict_prefix.calibration_slot8.min_detectable_epsilon` | smallest injected signal this probe detects | florida |
| 0.47892405024933266 | macro-F1 | `florida/probe_ladder.json` | `arms.trainonly.slot8.mlp.mean` | nonlinear probe on the last observed vector | florida |
| 0.02 | epsilon | `florida/probe_ladder.json` | `arms.trainonly.calibration_slot8.min_detectable_epsilon` | smallest injected signal this probe detects | florida |
| 0.23899964363401974 | macro-F1 | `florida/probe_ladder.json` | `arms.trainonly_prefix.slot8.mlp.mean` | nonlinear probe on the last observed vector | florida |
| 0.02 | epsilon | `florida/probe_ladder.json` | `arms.trainonly_prefix.calibration_slot8.min_detectable_epsilon` | smallest injected signal this probe detects | florida |
| 0.5866352107442846 | macro-F1 | `florida/probe_ladder.json` | `arms.attention_control.slot8.mlp.mean` | nonlinear probe on the last observed vector | florida |
| 0.02 | epsilon | `florida/probe_ladder.json` | `arms.attention_control.calibration_slot8.min_detectable_epsilon` | smallest injected signal this probe detects | florida |
| 0.6272474089261492 | macro-F1 | `florida/counterfactual.json` | `intact.mean_macro_f1` | the reported representation | florida |
| 30.524388677987606 | macro-F1 points | `florida/counterfactual.json` | `arms.zero_target_cat.matched.drop_points` | change from the reported representation, zero_target_cat, retrained | florida |
| 31.488671284307472 | macro-F1 points | `florida/counterfactual.json` | `arms.resample_target_all.matched.drop_points` | change from the reported representation, resample_target_all, retrained | florida |
| 4.658888075944734 | macro-F1 points | `florida/counterfactual.json` | `arms.redraw_edge.matched.drop_points` | change from the reported representation, redraw_edge, retrained | florida |
| 0.0 | macro-F1 points | `florida/counterfactual.json` | `arms.placebo_far_future.matched.drop_points` | change from the reported representation, placebo_far_future, retrained | florida |
| 1.5151043303576306 | macro-F1 points | `florida/counterfactual.json` | `arms.placebo_observed.matched.drop_points` | change from the reported representation, placebo_observed, retrained | florida |
| 31.167054902439574 | macro-F1 points | `florida/counterfactual.json` | `arms.strict_prefix.matched.drop_points` | change from the reported representation, strict_prefix, retrained | florida |
| 0.9495293868193588 | macro-F1 points | `florida/counterfactual.json` | `arms.trainonly_full.matched.drop_points` | change from the reported representation, trainonly_full, retrained | florida |
| 31.540467524082317 | macro-F1 points | `florida/counterfactual.json` | `arms.trainonly_prefix.matched.drop_points` | change from the reported representation, trainonly_prefix, retrained | florida |

# The reported model: the study's numbers restated in the dissertation's own units

Every metric in the sections above comes from a small category head written inside this study: hidden
128, one layer, 30 epochs, three head seeds, one fold. That head is adequate for comparing arms to
each other, because every arm shares it, but its absolute values are not the dissertation's and must
never be placed beside Chapter 5's table. Two facts make that concrete. Its architecture and protocol
differ from the reported dedicated model on every axis (hidden 256 and two layers against 128 and
one; n = 20 against one fold; macro-F1 at the f1-best epoch against the final epoch; a per-dataset
recipe against one setting everywhere). And the resulting gaps run in OPPOSITE directions at the two
datasets, higher at Alabama and lower at Florida, so no single correction reconciles them.

The arms were therefore re-materialized as ordinary engine directories and run through the reported
command unchanged: `scripts/train.py --task next --model next_gru`, batch 2048, OneCycle max_lr 0.005,
50 epochs, 5 folds, seed 0, scored by `scripts/closing_data/score_stl_cat_ceiling.py` at the f1-best
epoch. All arms share the same 96,326 windows and the same labels.

## Harness validation

| run | macro-F1 | n | note |
|---|---:|---:|---|
| published seed-0 ceiling run | 55.87 ± 2.39 | 5 | `docs/results/closing_data/h100/alabama_s0_stl_cat_ceiling.json`; the like-for-like comparand |
| reproduced here | 56.86 ± 1.98 | 5 | +0.99 points, inside both fold spreads |
| published n = 20 column | 56.82 ± 0.03 | 20 | four seeds averaged; the ± is a SEED spread, not comparable to a one-seed fold spread |

The reproduction agrees with the published single-seed run to within a point, well inside the fold
standard deviation of either. It should not be compared to the n = 20 mean, and the close agreement
with that mean is coincidental.

## The board

| arm | what changes | macro-F1 | vs reported | best epochs |
|---|---|---:|---:|---|
| reported | nothing; the target visit is present | **56.86** ± 1.98 | — | 46, 45, 50, 43, 50 |
| masked backward | backward messages carry no category | 28.47 ± 0.84 | −28.39 | 10, 8, 5, 12, 8 |
| target withheld | readout only, path cut at the target | 28.23 ± 1.36 | −28.63 | 4, 8, 5, 8, 8 |
| forward-only | no backward edge, trained and read | 27.51 ± 1.02 | −29.35 | 10, 11, 6, 8, 8 |
| no category one-hot | the input feature is removed | 17.46 ± 0.43 | −39.40 | 45, 48, 45, 49, 44 |

Reference point, measured on THIS protocol: a model given nine one-hots of the observed visits' own categories, zero-padded to 64 so `next_gru` builds an identical architecture, reaches **28.9964 ± 0.97**. Every arm above except the reported one is BELOW that value: masked backward by 0.53, target withheld by 0.77, forward-only by 1.48, and no-category-one-hot by 11.54. So once the target's category is withheld, the check-in-level representation is not merely no better than counting the nine observed labels, it is slightly worse. (The study-instrument figure of 0.2669 in section 4 was measured with a different model at one fold and must not be differenced against these five-fold values.)

Three structurally different ways of withholding the target's category agree at about 28, so the loss
is not an artefact of any one intervention. The reported configuration is still improving at epoch 43
to 50, while every honest arm peaks between epoch 5 and 12 and then overfits, which is the profile of
a model that has run out of signal. Removing the category one-hot entirely costs a further 10 points
and falls 10.05 below the forward-only arm measured on the same protocol, which bounds from the other
side how much of the representation's legitimate value is the observed visits' own categories.

For the option space these numbers close, and the one modelling question they leave open, see
`consecutive_link_fix_options.md` in this directory.


# Region: the joint model, and whether the leak reaches the second task

The audit's first phase mapped which task stream each channel can reach and predicted that the
consecutive-visit link cannot touch the region task: the region tower consumes region embeddings
indexed by the HISTORICAL places, and a region embedding is a per-region constant for the whole
dataset, so no per-visit target information can travel through it. This section tests that prediction
directly rather than resting on the code reading.

## Protocol

The reported joint command, verbatim from `scripts/closing_data/board_h100_mtl.sh`, with only
`--engine` varied: `--task mtl --task-set check2hgi_next_region`, cross-attention dual tower, static
weighting with category weight 0.75, `next_gru` category head, `next_stan_flow_dualtower` region head,
50 epochs, 5 folds, seed 0, and the same region-transition prior directory. Scored by
`scripts/closing_data/a40_score_matched.py`.

The two metrics are different quantities and must not be interchanged. Category is macro-F1 at the
f1-best epoch. Region is Acc@10, computed as `top10_acc_indist * (1 - ood_fraction)` at the
indist-best epoch, which is the reported region metric. The region MACRO-F1 column of the same file is
a real number (7.62 here) but is NOT what the dissertation reports.

The strict arm required two files beyond its embeddings, both handled so they cannot confound the
contrast. `sequences_next.parquet` holds the PLACE sequence, which is data rather than representation
and identical across arms; it was copied with a userid-equality check, and the loader re-verifies that
alignment on every load. `region_embeddings.parquet` was SYMLINKED rather than copied, so the two arms
provably share one table (1,109 regions by 65 columns, byte-identical) and a region difference cannot
be attributed to different region vectors.

## Result

| arm | category macro-F1 | region Acc@10 |
|---|---:|---:|
| reported representation | 63.44 ± 1.73 | 69.84 ± 3.12 |
| target withheld | 27.35 ± 0.86 | 69.86 ± 3.26 |
| difference | **−36.09** | **+0.01** |

Region moves by one hundredth of a point, which is a three-hundredth of its own fold standard
deviation. The per-fold values are preserved almost exactly: 72.01, 69.19, 73.24, 70.55, 64.23 becomes
72.13, 68.93, 73.58, 70.51, 64.13. Category loses 36.09 points, 57 percent of its value.

The prediction is confirmed. **Alabama's published region result is not implicated in this leak.** The
category result is.

One residual signal is worth recording rather than dismissing. The region tower's best epochs shift
later under the strict representation, from 28, 31, 32, 32, 25 to 42, 38, 40, 35, 45. The region task
takes longer to reach its peak when cross-attention has nothing useful to offer it, which is a
statement about the joint topology rather than about the backward edge, and it arrives at the same
value.

## Reproduction fidelity, both tasks

| quantity | published (n=20) | reproduced here (n=5) | gap |
|---|---:|---:|---:|
| joint category macro-F1 | 64.51 ± 0.09 | 63.44 ± 1.73 | −1.07 |
| joint region Acc@10 | 69.70 ± 0.09 | 69.84 ± 3.12 | +0.14 |

Region reproduces to 0.14 points. Category lands 1.07 points low, inside the fold spread of 1.73 but
on the low side, which is expected for one seed against a four-seed mean. Both published figures come
from `articles/dissertacao/src/chapters/5_mobiwac/06_results.tex` lines 128 to 130.

# The decision

The consecutive-visit link is a genuine leak for next-category prediction, and it is large. The
reported check-in-level representation lets the category head see a feature of the visit it is being
asked to predict. The measurement that decides this was made on the dissertation's OWN dedicated
model, not on a head written inside the study: at Alabama, the reported configuration reaches 56.86
macro-F1 and cutting the user's path at the target drops it to 28.23, a loss of 28.63 points, half the
reported value. That reproduction agrees with the published single-seed ceiling run, 55.87, to within
a point.

The number that settles it is not the size of the drop but where the drop lands. Every honest arm
lands between 27.5 and 28.5, a span narrower than one fold standard deviation, while the reported
configuration sits at 56.86. And a model given nothing but the nine observed category one-hots, run
through the same dedicated command, reaches 28.9964. Every honest arm is BELOW that. So the
check-in-level representation, once the target's own category is withheld, does not merely fail to
improve on counting the observed label sequence; it is slightly worse than it, while costing a
representation-training stage.

Three structurally different ways of withholding it agree, which is what rules out an artefact of any
one intervention: withholding at readout gives 28.23, training and reading forward-only gives 27.51,
and keeping both edge directions while stripping category identity from every backward message gives
28.47. The spread across those three is smaller than one fold standard deviation. Removing the
category one-hot from the node features altogether goes the other way and costs a further 10 points,
17.46, which is 10.05 below the forward-only arm measured on the SAME protocol; that bounds from the
opposite side how much of the representation's legitimate value is the observed visits' own
categories.

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
