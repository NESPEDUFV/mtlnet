# PROVENANCE — the 18 v17/dk_ovl MTL rundirs behind Table 3

Every "Joint (ours)" cell in the paper's Table 3 traces to these rundirs on the A40 training
checkout (branch `closing-data/v17-ceilings-n20`). They are keyed by the
launcher **PID** (the safe mapping — never `ls -dt | head`, which races under concurrency). Each was
independently confirmed by its own `a40_matched_score.json` `"seed"` field. Path prefix:
`results/check2hgi_dk_ovl/<state>/mtlnet_lr1.0e-04_bs8192_ep50_<ts>_<PID>`.

## Rundir map

| Dataset | seed | PID | driver / doc | verified |
|---|---:|---:|---|---|
| Istanbul | 0 | 3852943 | `v17_completion/h3_istanbul` (`run_step3_n20.sh`) | cat 63.318 / reg 75.407 ✓ |
| Istanbul | 1 | 3858409 | " | cat 63.332 / reg 75.484 ✓ |
| Istanbul | 7 | 3863852 | " | cat 63.359 / reg 75.392 ✓ |
| Istanbul | 100 | 3869098 | " | cat 63.306 / reg 75.477 ✓ |
| Alabama | 0 | 983885 | `perhead_lr_n20` (`run_n20_perhead.sh`, recipe `new`) | cat 64.584 / reg 69.862 ✓ |
| Alabama | 1 | 983884 | " | cat 64.669 / reg 69.719 ✓ |
| Alabama | 7 | 988104 | " | cat 64.404 / reg 69.813 ✓ |
| Alabama | 100 | 988155 | " | cat 64.505 / reg 69.809 ✓ |
| Arizona | 0 | 992231 | `perhead_lr_n20` (recipe `new`) | cat 65.832 / reg 59.621 ✓ |
| Arizona | 1 | 992283 | " | cat 65.806 / reg 59.532 ✓ |
| Arizona | 7 | 998602 | " | cat 65.851 / reg 59.606 ✓ |
| Arizona | 100 | 998757 | " | cat 65.852 / reg 59.493 ✓ |
| Florida | 0 | 1058652 | `perhead_lr_n20` (recipe **`new`** = bs8192, NOT `base` bs2048) | cat 79.844 / reg 77.391 ✓ |
| Florida | 1 | 1088683 | " | cat 79.806 / reg 77.420 ✓ |
| Florida | 7 | 1097178 | " | cat 79.885 / reg 77.413 ✓ |
| Florida | 100 | 1119752 | " | cat 79.857 / reg 77.460 ✓ |
| California | 0 | 1363454 | `catx_v17_seed0_5f` (v17, fp32) | cat 77.042 / reg 65.694 ✓ |
| Texas | 0 | 1419069 | `catx_v17_seed0_5f` (v17, fp32) | cat 77.227 / reg 67.072 ✓ |

`(cat/reg above = the committed diag-best fold-mean from each rundir's a40_matched_score.json — our scorer's
diag-best re-derivation reproduces every one of them exactly; that is parity-gate A.)`

**Excluded:** `results/check2hgi_dk_ovl/istanbul/mtlnet_..._341087` — tag `istanbul_cascade_v17_s0`, the P6
**cascade** ablation (cross-attention disabled). Not the champion MTL; not a Table-3 cell.

## Recipe (identical across the 18, per `run_n20_perhead.sh` / the catx + h3 drivers)
```
--task mtl --canon none --task-set check2hgi_next_region --engine check2hgi_dk_ovl
--epochs 50 --folds 5 --batch-size 8192
--mtl-loss static_weight --category-weight 0.75 --no-reg-class-weights --no-cat-class-weights
--cat-head next_gru --reg-head next_stan_flow_dualtower
--reg-head-param raw_embed_dim=64 fusion_mode=aux freeze_alpha=True alpha_init=0.0   (region prior OFF)
--task-a-input-type checkin --task-b-input-type region --log-t-kd-weight 0.0
--scheduler onecycle --max-lr 3e-3 --cat-lr 1e-3 --reg-lr 3e-3 --shared-lr 3e-3   (v17 per-head LR)
--model mtlnet_crossattn_dualtower --compile --tf32
MTL_DISABLE_AMP=1 (fp32), MTL_ONECYCLE_PER_HEAD_LR=1, MTL_STRICT=1, --no-checkpoints
```
`geom_simple` checkpoint selector (default), `--min-best-epoch` unset → `ExperimentConfig` default **0**
(the scorer's default matches; `JOINT_BEST_SCORING.md §1`). `--no-checkpoints` skipped saving *weights*, but
`folds/foldN_info.json → primary_checkpoint.epoch` still records the joint-checkpoint epoch → parity-gate B works.

## How each cell aggregates
- **n=20 (Istanbul, AL, AZ, FL):** cell = mean over the 4 seeds of each rundir's 5-fold mean; ± = cross-seed
  pstdev of the 4 per-seed means. (Matches the paper's "± is sd across seeds for four-seed cells".)
- **seed-0 5f (CA, TX):** cell = the single rundir's 5-fold mean; ± = fold pstdev. (Provisional; A1 n=20 pending.)

## Reproduce
```bash
# Run the durable scorer once for each recorded rundir from the repository root:
.venv/bin/python src/tracking/score_joint_best.py <rundir> --seed <seed> --tag <tag>
# -> writes joint_best_score.json into the rundir. Aggregate values are frozen in
# data/joint_best/j1_results.json and JOINT_BEST_RESULTS.md.
```
