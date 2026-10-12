# reg-alabama-p13s13

`649aaea3413e46d4` from `recipes/v19/reg.toml`

## Recipe

- family **reg** · state **alabama** · model_seed **13** · split_seed **13** · engine `check2hgi_v18`
- 50 epochs · batch 2048 · 5 folds · precision fp32
- scheduler onecycle · max_lr 0.003
- reg head `next_stan_flow` {'d_model': 128, 'num_heads': 4, 'dropout': 0.3, 'seq_length': 9, 'freeze_alpha': True, 'alpha_init': 0.0}

## Result

**Sealed.** The outer-test metric is not computed here — `mtlcheck compare` reads
the persisted predictions. See `docs/plans/EVALUATION_IMPLEMENTATION.md` §1.

Joint cell — two metrics, no single aggregate.

| fold | cat macro-F1 | reg Acc@10 | wall |
|---:|---:|---:|---:|
| 0 | ? | ? | 4s |
| 1 | ? | ? | 4s |
| 2 | ? | ? | 4s |
| 3 | ? | ? | 4s |
| 4 | ? | ? | 4s |

## Worth a look

Nothing flagged.

## Diagnostics

```json
{
 "best_epoch": 37,
 "best_value": 0.7419288754463196,
 "clipped_fraction_mean": 0.1115,
 "clipped_fraction_per_epoch": [
  0.5758,
  0.0,
  0.0,
  0.0,
  0.0,
  0.0,
  0.0,
  0.3636,
  0.3939,
  0.5152,
  0.6364,
  0.4848,
  0.5758,
  0.4242,
  0.3939,
  0.2424,
  0.2424,
  0.2727,
  0.1515,
  0.0606,
  0.0909,
  0.0303,
  0.0606,
  0.0303,
  0.0,
  0.0303,
  0.0,
  0.0,
  0.0,
  0.0,
  0.0,
  0.0,
  0.0,
  0.0,
  0.0,
  0.0,
  0.0,
  0.0,
  0.0,
  0.0,
  0.0,
  0.0,
  0.0,
  0.0,
  0.0,
  0.0,
  0.0,
  0.0,
  0.0,
  0.0
 ],
 "compile_counters": {
  "frames_ok": 0,
  "frames_total": 0,
  "graph_breaks": 0,
  "unique_graph_breaks": 0
 },
 "epochs_to_95pct": 12,
 "epochs_to_99pct": 29,
 "execution": {
  "compiled": true,
  "device": "cuda",
  "precision": "fp32",
  "probe": "n/a (no shared trunk)",
  "tf32": true
 },
 "grad_norm_max": 1.353131,
 "grad_norm_max_per_epoch": [
  1.323194,
  0.942076,
  0.800148,
  0.688232,
  0.83998,
  0.981372,
  0.986509,
  1.353131,
  1.309502,
  1.330201,
  1.204131,
  1.33376,
  1.206938,
  1.194144,
  1.28805,
  1.112203,
  1.130816,
  1.142844,
  1.218758,
  1.079536,
  1.027998,
  1.032169,
  1.037807,
  1.036237,
  0.92445,
  1.073745,
  0.919066,
  0.864084,
  0.837972,
  0.921568,
  0.901274,
  0.847576,
  0.884277,
  0.925171,
  0.862592,
  0.841467,
  0.815812,
  0.784042,
  0.787838,
  0.851112,
  0.804347,
  0.796529,
  0.757615,
  0.76143,
  0.741588,
  0.773462,
  0.769971,
  0.771198,
  0.727864,
  0.756078
 ],
 "grad_norm_mean": 0.80483,
 "grad_norm_per_epoch": [
  1.063256,
  0.858399,
  0.741667,
  0.638017,
  0.688042,
  0.775066,
  0.824122,
  0.963323,
  1.009058,
  1.027354,
  1.031138,
  1.024946,
  1.014517,
  0.975351,
  0.984583,
  0.936111,
  0.951919,
  0.924578,
  0.890332,
  0.875205,
  0.858773,
  0.844342,
  0.836364,
  0.790506,
  0.811107,
  0.799086,
  0.793268,
  0.754575,
  0.742204,
  0.751221,
  0.776464,
  0.756425,
  0.753795,
  0.766959,
  0.731726,
  0.722356,
  0.713299,
  0.699832,
  0.693352,
  0.701853,
  0.706508,
  0.69096,
  0.67406,
  0.686092,
  0.673451,
  0.667092,
  0.673735,
  0.665074,
  0.66109,
  0.648969
 ],
 "lr_per_group_at_epoch_end": {
  "first": [
   0.00015159
  ],
  "last": [
   2e-08
  ],
  "max_observed": [
   0.00299999
  ],
  "note": "sampled after the epoch's final scheduler.step(); not the applied peak"
 },
 "nonfinite_batches": 0,
 "nonfinite_per_epoch": [
  0,
  0,
  0,
  0,
  0,
  0,
  0,
  0,
  0,
  0,
  0,
  0,
  0,
  0,
  0,
  0,
  0,
  0,
  0,
  0,
  0,
  0,
  0,
  0,
  0,
  0,
  0,
  0,
  0,
  0,
  0,
  0,
  0,
  0,
  0,
  0,
  0,
  0,
  0,
  0,
  0,
  0,
  0,
  0,
  0,
  0,
  0,
  0,
  0,
  0
 ],
 "peak_memory_gb": 0.505,
 "tail_spread_pct_of_best": 0.222,
 "train_seconds_per_epoch": 0.077,
 "train_seconds_total": 3.83,
 "val_seconds_per_epoch": 0.005,
 "val_seconds_total": 0.24,
 "val_share_of_wall": 0.0601
}
```
