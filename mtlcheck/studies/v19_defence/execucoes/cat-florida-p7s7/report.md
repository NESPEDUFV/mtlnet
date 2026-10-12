# cat-florida-p7s7

`05c3acc18bc5a079` from `recipes/v19/cat.toml`

## Recipe

- family **cat** · state **florida** · model_seed **7** · split_seed **7** · engine `check2hgi_v18`
- 50 epochs · batch 8192 · 5 folds · precision fp32
- scheduler onecycle · max_lr 0.005
- cat head `next_gru` {'hidden_dim': 256, 'num_layers': 4, 'dropout': 0.1}

## Result

**Sealed.** The outer-test metric is not computed here — `mtlcheck compare` reads
the persisted predictions. See `docs/plans/EVALUATION_IMPLEMENTATION.md` §1.

Joint cell — two metrics, no single aggregate.

| fold | cat macro-F1 | reg Acc@10 | wall |
|---:|---:|---:|---:|
| 0 | ? | ? | 161s |
| 1 | ? | ? | 161s |
| 2 | ? | ? | 160s |
| 3 | ? | ? | 160s |
| 4 | ? | ? | 160s |

## Worth a look

- every fold peaked in the first third of the schedule (latest was epoch 10 of 50) — a shorter schedule may score HIGHER, not just faster; at alabama that was worth +0.35 pp

## Diagnostics

```json
{
 "best_epoch": 10,
 "best_value": 0.3888140618801117,
 "clipped_fraction_mean": 0.0018,
 "clipped_fraction_per_epoch": [
  0.0917,
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
 "epochs_to_99pct": 4,
 "execution": {
  "compiled": true,
  "device": "cuda",
  "precision": "fp32",
  "probe": "n/a (no shared trunk)",
  "tf32": true
 },
 "grad_norm_max": 5.391775,
 "grad_norm_max_per_epoch": [
  5.391775,
  0.708066,
  0.819652,
  0.583813,
  0.672808,
  0.601687,
  0.580025,
  0.550689,
  0.640757,
  0.466714,
  0.451979,
  0.403672,
  0.385682,
  0.339858,
  0.223355,
  0.260496,
  0.196889,
  0.166041,
  0.16453,
  0.136365,
  0.13689,
  0.123552,
  0.142117,
  0.124409,
  0.114718,
  0.11346,
  0.119509,
  0.118379,
  0.11559,
  0.110593,
  0.119773,
  0.121584,
  0.121372,
  0.122981,
  0.127062,
  0.129331,
  0.129341,
  0.131524,
  0.136746,
  0.141206,
  0.148202,
  0.151003,
  0.153795,
  0.157035,
  0.15996,
  0.159827,
  0.163288,
  0.168637,
  0.163276,
  0.16554
 ],
 "grad_norm_mean": 0.178921,
 "grad_norm_per_epoch": [
  0.562773,
  0.352293,
  0.467594,
  0.325282,
  0.354229,
  0.346057,
  0.319031,
  0.296699,
  0.285532,
  0.277627,
  0.238058,
  0.220416,
  0.220321,
  0.19334,
  0.158372,
  0.144765,
  0.128728,
  0.123349,
  0.11415,
  0.107586,
  0.105016,
  0.102387,
  0.101693,
  0.101786,
  0.100965,
  0.101431,
  0.102926,
  0.10092,
  0.102493,
  0.102597,
  0.105197,
  0.10728,
  0.110264,
  0.112692,
  0.11464,
  0.118363,
  0.122463,
  0.125611,
  0.129535,
  0.134187,
  0.138855,
  0.142483,
  0.1463,
  0.149161,
  0.151813,
  0.15346,
  0.155436,
  0.156483,
  0.156563,
  0.156843
 ],
 "lr_per_group_at_epoch_end": {
  "first": [
   0.00025251
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
 "peak_memory_gb": 5.583,
 "tail_spread_pct_of_best": 0.124,
 "train_seconds_per_epoch": 3.11,
 "train_seconds_total": 155.51,
 "val_seconds_per_epoch": 0.108,
 "val_seconds_total": 5.42,
 "val_share_of_wall": 0.0337
}
```
