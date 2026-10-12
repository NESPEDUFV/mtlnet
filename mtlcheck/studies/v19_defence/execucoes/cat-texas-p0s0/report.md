# cat-texas-p0s0

`b21794c9127bcdb9` from `recipes/v19/cat.toml`

## Recipe

- family **cat** · state **texas** · model_seed **0** · split_seed **0** · engine `check2hgi_v18`
- 50 epochs · batch 8192 · 5 folds · precision fp32
- scheduler onecycle · max_lr 0.005
- cat head `next_gru` {'hidden_dim': 256, 'num_layers': 4, 'dropout': 0.1}

## Result

**Sealed.** The outer-test metric is not computed here — `mtlcheck compare` reads
the persisted predictions. See `docs/plans/EVALUATION_IMPLEMENTATION.md` §1.

Joint cell — two metrics, no single aggregate.

| fold | cat macro-F1 | reg Acc@10 | wall |
|---:|---:|---:|---:|
| 0 | ? | ? | 478s |
| 1 | ? | ? | 477s |
| 2 | ? | ? | 476s |
| 3 | ? | ? | 477s |
| 4 | ? | ? | 477s |

## Worth a look

- selection landed on the FIRST or LAST epoch in fold(s) [4] — the schedule is probably mis-sized (50 epochs)

## Diagnostics

```json
{
 "best_epoch": 48,
 "best_value": 0.3658721148967743,
 "clipped_fraction_mean": 0.0005,
 "clipped_fraction_per_epoch": [
  0.0274,
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
  0.0,
  0.0,
  0.0
 ],
 "compile_counters": {
  "frames_ok": 9,
  "frames_total": 10,
  "graph_breaks": 3,
  "unique_graph_breaks": 1
 },
 "epochs_to_95pct": 1,
 "epochs_to_99pct": 6,
 "execution": {
  "compiled": true,
  "device": "cuda",
  "precision": "fp32",
  "probe": "n/a (no shared trunk)",
  "tf32": true
 },
 "grad_norm_max": 2.793551,
 "grad_norm_max_per_epoch": [
  2.793551,
  0.703785,
  0.759225,
  0.577862,
  0.61855,
  0.586305,
  0.49176,
  0.440769,
  0.289937,
  0.235678,
  0.214232,
  0.124257,
  0.128263,
  0.103224,
  0.099033,
  0.103699,
  0.099501,
  0.104037,
  0.105656,
  0.111341,
  0.106198,
  0.111559,
  0.113733,
  0.116525,
  0.112277,
  0.112899,
  0.110191,
  0.112844,
  0.326303,
  0.111216,
  0.109242,
  0.125726,
  0.109333,
  0.109267,
  0.129164,
  0.114621,
  0.101299,
  0.111036,
  0.100523,
  0.107761,
  0.104142,
  0.109163,
  0.103463,
  0.106694,
  0.116856,
  0.101608,
  0.114467,
  0.108065,
  0.104035,
  0.099711
 ],
 "grad_norm_mean": 0.105669,
 "grad_norm_per_epoch": [
  0.459002,
  0.361032,
  0.330807,
  0.283611,
  0.270212,
  0.252359,
  0.23973,
  0.211317,
  0.160744,
  0.124301,
  0.099588,
  0.082939,
  0.071228,
  0.064137,
  0.060991,
  0.060437,
  0.059161,
  0.060983,
  0.061928,
  0.062619,
  0.0663,
  0.064213,
  0.06626,
  0.066874,
  0.067395,
  0.068113,
  0.068371,
  0.067316,
  0.067874,
  0.068262,
  0.065836,
  0.066109,
  0.06589,
  0.06375,
  0.063034,
  0.062773,
  0.061941,
  0.061427,
  0.061503,
  0.061723,
  0.060978,
  0.060663,
  0.060271,
  0.060239,
  0.060111,
  0.060157,
  0.059539,
  0.060057,
  0.05969,
  0.059629
 ],
 "lr_per_group_at_epoch_end": {
  "first": [
   0.00025247
  ],
  "last": [
   2e-08
  ],
  "max_observed": [
   0.005
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
 "peak_memory_gb": 11.102,
 "tail_spread_pct_of_best": 0.127,
 "train_seconds_per_epoch": 9.192,
 "train_seconds_total": 459.58,
 "val_seconds_per_epoch": 0.346,
 "val_seconds_total": 17.28,
 "val_share_of_wall": 0.0362
}
```
