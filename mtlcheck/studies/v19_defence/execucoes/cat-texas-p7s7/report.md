# cat-texas-p7s7

`cd26e7836bc2eb00` from `recipes/v19/cat.toml`

## Recipe

- family **cat** · state **texas** · model_seed **7** · split_seed **7** · engine `check2hgi_v18`
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
| 1 | ? | ? | 476s |
| 2 | ? | ? | 477s |
| 3 | ? | ? | 477s |
| 4 | ? | ? | 476s |

## Worth a look

- selection landed on the FIRST or LAST epoch in fold(s) [0, 2] — the schedule is probably mis-sized (50 epochs)
- ties at the decision boundary: [(0, {'top3': 0, 'top5': 1})]

## Diagnostics

```json
{
 "best_epoch": 50,
 "best_value": 0.3641148805618286,
 "clipped_fraction_mean": 0.0004,
 "clipped_fraction_per_epoch": [
  0.0213,
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
  "frames_ok": 0,
  "frames_total": 0,
  "graph_breaks": 0,
  "unique_graph_breaks": 0
 },
 "epochs_to_95pct": 1,
 "epochs_to_99pct": 5,
 "execution": {
  "compiled": true,
  "device": "cuda",
  "precision": "fp32",
  "probe": "n/a (no shared trunk)",
  "tf32": true
 },
 "grad_norm_max": 5.296251,
 "grad_norm_max_per_epoch": [
  5.296251,
  0.730886,
  0.702462,
  0.576034,
  0.601783,
  0.522164,
  0.473605,
  0.405423,
  0.382894,
  0.26143,
  0.181437,
  0.132226,
  0.113869,
  0.119734,
  0.104469,
  0.102802,
  0.105805,
  0.111493,
  0.110967,
  0.102548,
  0.110749,
  0.111103,
  0.116434,
  0.114726,
  0.119116,
  0.13578,
  0.115205,
  0.119849,
  0.126926,
  0.117857,
  0.119219,
  0.11181,
  0.112253,
  0.117022,
  0.123749,
  0.112766,
  0.107733,
  0.112723,
  0.102929,
  0.114733,
  0.098552,
  0.112251,
  0.117934,
  0.121384,
  0.103074,
  0.10987,
  0.110254,
  0.125025,
  0.106795,
  0.120771
 ],
 "grad_norm_mean": 0.107621,
 "grad_norm_per_epoch": [
  0.458199,
  0.364031,
  0.329835,
  0.299814,
  0.289119,
  0.253644,
  0.233734,
  0.209689,
  0.169942,
  0.129054,
  0.103338,
  0.083226,
  0.071902,
  0.065796,
  0.063,
  0.061007,
  0.06114,
  0.061107,
  0.06174,
  0.061897,
  0.063617,
  0.063715,
  0.066171,
  0.067326,
  0.067022,
  0.068736,
  0.068292,
  0.069422,
  0.069713,
  0.068315,
  0.068648,
  0.068829,
  0.068958,
  0.0668,
  0.066354,
  0.065855,
  0.064752,
  0.064129,
  0.063379,
  0.062939,
  0.06273,
  0.062196,
  0.061947,
  0.061694,
  0.061943,
  0.061337,
  0.06115,
  0.061353,
  0.06132,
  0.061197
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
 "peak_memory_gb": 11.101,
 "tail_spread_pct_of_best": 0.111,
 "train_seconds_per_epoch": 9.196,
 "train_seconds_total": 459.78,
 "val_seconds_per_epoch": 0.345,
 "val_seconds_total": 17.27,
 "val_share_of_wall": 0.0362
}
```
