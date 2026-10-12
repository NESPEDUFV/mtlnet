# cat-arizona-p0s0

`61faa4b4abae1095` from `recipes/v19/cat.toml`

## Recipe

- family **cat** · state **arizona** · model_seed **0** · split_seed **0** · engine `check2hgi_v18`
- 50 epochs · batch 8192 · 5 folds · precision fp32
- scheduler onecycle · max_lr 0.0005
- cat head `next_gru` {'hidden_dim': 256, 'num_layers': 4, 'dropout': 0.1}

## Result

**Sealed.** The outer-test metric is not computed here — `mtlcheck compare` reads
the persisted predictions. See `docs/plans/EVALUATION_IMPLEMENTATION.md` §1.

Joint cell — two metrics, no single aggregate.

| fold | cat macro-F1 | reg Acc@10 | wall |
|---:|---:|---:|---:|
| 0 | ? | ? | 25s |
| 1 | ? | ? | 25s |
| 2 | ? | ? | 25s |
| 3 | ? | ? | 25s |
| 4 | ? | ? | 25s |

## Worth a look

Nothing flagged.

## Diagnostics

```json
{
 "best_epoch": 40,
 "best_value": 0.3194134831428528,
 "clipped_fraction_mean": 0.0244,
 "clipped_fraction_per_epoch": [
  0.7778,
  0.0,
  0.0,
  0.0,
  0.0,
  0.0,
  0.0,
  0.1111,
  0.1111,
  0.0556,
  0.0,
  0.1111,
  0.0556,
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
 "epochs_to_95pct": 10,
 "epochs_to_99pct": 26,
 "execution": {
  "compiled": true,
  "device": "cuda",
  "precision": "fp32",
  "probe": "n/a (no shared trunk)",
  "tf32": true
 },
 "grad_norm_max": 2.69464,
 "grad_norm_max_per_epoch": [
  2.69464,
  0.853636,
  0.637482,
  0.807825,
  0.811028,
  0.843067,
  0.968764,
  1.135744,
  1.159386,
  1.174148,
  0.833764,
  1.106074,
  1.095239,
  0.6807,
  0.746679,
  0.845686,
  0.696998,
  0.871081,
  0.687167,
  0.881542,
  0.715822,
  0.704428,
  0.759728,
  0.793303,
  0.889666,
  0.709311,
  0.561912,
  0.55099,
  0.495398,
  0.760687,
  0.512927,
  0.517033,
  0.623751,
  0.604222,
  0.553888,
  0.81275,
  0.45177,
  0.696633,
  0.581899,
  0.616373,
  0.51879,
  0.605123,
  0.485965,
  0.468692,
  0.501103,
  0.452181,
  0.427727,
  0.624402,
  0.564153,
  0.725221
 ],
 "grad_norm_mean": 0.4455,
 "grad_norm_per_epoch": [
  1.327572,
  0.676139,
  0.480057,
  0.426923,
  0.517988,
  0.535926,
  0.657862,
  0.676118,
  0.712584,
  0.778629,
  0.508941,
  0.726144,
  0.711246,
  0.412339,
  0.432461,
  0.5159,
  0.451463,
  0.452607,
  0.402201,
  0.629071,
  0.428352,
  0.45947,
  0.408392,
  0.58442,
  0.498063,
  0.381028,
  0.343888,
  0.389986,
  0.331983,
  0.412425,
  0.353048,
  0.342392,
  0.315798,
  0.367338,
  0.350552,
  0.321407,
  0.30483,
  0.326264,
  0.309264,
  0.34,
  0.306639,
  0.310589,
  0.277358,
  0.245958,
  0.25873,
  0.262679,
  0.242845,
  0.256776,
  0.230265,
  0.282102
 ],
 "lr_per_group_at_epoch_end": {
  "first": [
   2.528e-05
  ],
  "last": [
   1e-08
  ],
  "max_observed": [
   0.0005
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
 "peak_memory_gb": 3.266,
 "tail_spread_pct_of_best": 0.228,
 "train_seconds_per_epoch": 0.487,
 "train_seconds_total": 24.34,
 "val_seconds_per_epoch": 0.017,
 "val_seconds_total": 0.87,
 "val_share_of_wall": 0.0346
}
```
