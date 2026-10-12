# v18 — AUDIT

> The charter §6 self-checks, with their **measured values**. Regenerate with `verify_engines.py --write`.

> Generated 2026-08-07T20:31:55.596005+00:00.

Fail closed: a silent wrong number is far worse than a crash. `n/a` marks a check that does not apply to how this state was materialized, with the reason given.

**Overall: all states pass** (6 states checked).


## istanbul — ALL PASS

| check | verdict | measured |
|---|---|---|
| engine has input/next.parquet | PASS | `906 MiB` |
| engine has input/next_region.parquet | PASS | `855 MiB` |
| engine has temp/sequences_next.parquet | PASS | `6 MiB` |
| engine has region_embeddings.parquet | PASS | `symlink -> check2hgi_design_k_resln_mae_l0_1` |
| node layout | PASS | `['canonical_11', 'continuous_time_4']` |
| in_channels == 15 | PASS | `15` |
| causal_graph.forward_only | PASS | `True` |
| backward edges dropped | PASS | `881336 -> 440668 (dropped 440668)` |
| repr seed / epochs / encoder | PASS | `seed=42 epochs=500 encoder=resln best_epoch=499` |
| materialization method | PASS | `per-window npz via materialize_engine.py (win_matched.npz)` |
| readout equivalence vs per-window npz | PASS | `max 3.099e-06 (slot8 2.861e-06, mean 1.474e-07) over 271666 windows` |
| readout matches training graph | PASS | `prefix_forward_only` |
| held-out user encodability (--self-test) | PASS | `True` |
| retention >= 95% of source windows | PASS | `271666/271666 = 1.0000` |
| feature width 9 x 64 | PASS | `576 = 9 x 64` |
| next/next_region userid alignment | PASS | `271666 vs 271666 rows` |
| labels match the source row space | PASS | `identical` |
| userids match the source row space | PASS | `identical` |

## alabama — ALL PASS

| check | verdict | measured |
|---|---|---|
| engine has input/next.parquet | PASS | `319 MiB` |
| engine has input/next_region.parquet | PASS | `285 MiB` |
| engine has temp/sequences_next.parquet | PASS | `2 MiB` |
| engine has region_embeddings.parquet | PASS | `symlink -> check2hgi_design_k_resln_mae_l0_1` |
| node layout | PASS | `['canonical_11', 'continuous_time_4']` |
| in_channels == 15 | PASS | `15` |
| causal_graph.forward_only | PASS | `True` |
| backward edges dropped | PASS | `219976 -> 109988 (dropped 109988)` |
| repr seed / epochs / encoder | PASS | `seed=42 epochs=500 encoder=resln best_epoch=499` |
| materialization method | PASS | `per-window npz via materialize_engine.py (win_matched.npz)` |
| readout equivalence vs per-window npz | PASS | `max 2.384e-06 (slot8 2.384e-06, mean 1.407e-07) over 96326 windows` |
| readout matches training graph | PASS | `prefix_forward_only` |
| held-out user encodability (--self-test) | PASS | `True` |
| retention >= 95% of source windows | PASS | `96326/96326 = 1.0000` |
| feature width 9 x 64 | PASS | `576 = 9 x 64` |
| next/next_region userid alignment | PASS | `96326 vs 96326 rows` |
| labels match the source row space | PASS | `identical` |
| userids match the source row space | PASS | `identical` |

## arizona — ALL PASS

| check | verdict | measured |
|---|---|---|
| engine has input/next.parquet | PASS | `676 MiB` |
| engine has input/next_region.parquet | PASS | `609 MiB` |
| engine has temp/sequences_next.parquet | PASS | `5 MiB` |
| engine has region_embeddings.parquet | PASS | `symlink -> check2hgi_design_k_resln_mae_l0_1` |
| node layout | PASS | `['canonical_11', 'continuous_time_4']` |
| in_channels == 15 | PASS | `15` |
| causal_graph.forward_only | PASS | `True` |
| backward edges dropped | PASS | `457162 -> 228581 (dropped 228581)` |
| repr seed / epochs / encoder | PASS | `seed=42 epochs=500 encoder=resln best_epoch=498` |
| materialization method | PASS | `per-window npz via materialize_engine.py (win_matched.npz)` |
| readout equivalence vs per-window npz | PASS | `max 2.861e-06 (slot8 2.861e-06, mean 1.463e-07) over 200895 windows` |
| readout matches training graph | PASS | `prefix_forward_only` |
| held-out user encodability (--self-test) | PASS | `True` |
| retention >= 95% of source windows | PASS | `200895/200895 = 1.0000` |
| feature width 9 x 64 | PASS | `576 = 9 x 64` |
| next/next_region userid alignment | PASS | `200895 vs 200895 rows` |
| labels match the source row space | PASS | `identical` |
| userids match the source row space | PASS | `identical` |

## florida — ALL PASS

| check | verdict | measured |
|---|---|---|
| engine has input/next.parquet | PASS | `3378 MiB` |
| engine has input/next_region.parquet | PASS | `3312 MiB` |
| engine has temp/sequences_next.parquet | PASS | `37 MiB` |
| engine has region_embeddings.parquet | PASS | `symlink -> check2hgi_design_k_resln_mae_l0_1` |
| node layout | PASS | `['canonical_11', 'continuous_time_4']` |
| in_channels == 15 | PASS | `15` |
| causal_graph.forward_only | PASS | `True` |
| backward edges dropped | PASS | `2771964 -> 1385982 (dropped 1385982)` |
| repr seed / epochs / encoder | PASS | `seed=42 epochs=500 encoder=resln best_epoch=500` |
| materialization method | PASS | `one-shot full-graph forward-only export (embeddings_insample.parquet), wind` |
| readout equivalence vs per-window npz | PASS | `max 3.099e-06 (slot8 3.099e-06, mean 1.457e-07) over 1274418 windows` |
| readout matches training graph | PASS | `prefix_forward_only` |
| held-out user encodability (--self-test) | PASS | `True` |
| retention >= 95% of source windows | PASS | `1274418/1274418 = 1.0000` |
| feature width 9 x 64 | PASS | `576 = 9 x 64` |
| next/next_region userid alignment | PASS | `1274418 vs 1274418 rows` |
| labels match the source row space | PASS | `identical` |
| userids match the source row space | PASS | `identical` |

## texas — ALL PASS

| check | verdict | measured |
|---|---|---|
| engine has input/next.parquet | PASS | `9668 MiB` |
| engine has input/next_region.parquet | PASS | `9526 MiB` |
| engine has temp/sequences_next.parquet | PASS | `128 MiB` |
| engine has region_embeddings.parquet | PASS | `symlink -> check2hgi_design_k_resln_mae_l0_1` |
| node layout | PASS | `['canonical_11', 'continuous_time_4']` |
| in_channels == 15 | PASS | `15` |
| causal_graph.forward_only | PASS | `True` |
| backward edges dropped | PASS | `8102496 -> 4051248 (dropped 4051248)` |
| repr seed / epochs / encoder | PASS | `seed=42 epochs=500 encoder=resln best_epoch=500` |
| materialization method | PASS | `one-shot full-graph forward-only export (embeddings_insample.parquet), wind` |
| readout equivalence vs per-window npz | n/a | `not measured for this state (identity established at alabama/arizona/istanbul over every window; forward_only guard enforced in code)` |
| held-out user encodability (--self-test) | n/a | `no per-window npz for this state; F2 verified at the states that ran the readout` |
| retention >= 95% of source windows | PASS | `3830414/3830414 = 1.0000` |
| feature width 9 x 64 | PASS | `576 = 9 x 64` |
| next/next_region userid alignment | PASS | `3830414 vs 3830414 rows` |
| labels match the source row space | PASS | `identical` |
| userids match the source row space | PASS | `identical` |

## california — ALL PASS

| check | verdict | measured |
|---|---|---|
| engine has input/next.parquet | PASS | `7367 MiB` |
| engine has input/next_region.parquet | PASS | `7276 MiB` |
| engine has temp/sequences_next.parquet | PASS | `102 MiB` |
| engine has region_embeddings.parquet | PASS | `symlink -> check2hgi_design_k_resln_mae_l0_1` |
| node layout | PASS | `['canonical_11', 'continuous_time_4']` |
| in_channels == 15 | PASS | `15` |
| causal_graph.forward_only | PASS | `True` |
| backward edges dropped | PASS | `6268580 -> 3134290 (dropped 3134290)` |
| repr seed / epochs / encoder | PASS | `seed=42 epochs=500 encoder=resln best_epoch=500` |
| materialization method | PASS | `one-shot full-graph forward-only export (embeddings_insample.parquet), wind` |
| readout equivalence vs per-window npz | n/a | `not measured for this state (identity established at alabama/arizona/istanbul over every window; forward_only guard enforced in code)` |
| held-out user encodability (--self-test) | n/a | `no per-window npz for this state; F2 verified at the states that ran the readout` |
| retention >= 95% of source windows | PASS | `2925466/2925466 = 1.0000` |
| feature width 9 x 64 | PASS | `576 = 9 x 64` |
| next/next_region userid alignment | PASS | `2925466 vs 2925466 rows` |
| labels match the source row space | PASS | `identical` |
| userids match the source row space | PASS | `identical` |
