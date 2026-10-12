# Integrity re-run on the delivered protocol — prep package

> **Status 2026-10-02: the three patches are applied (`d01cd2a8`) and Alabama is done** (seed 0,
> 5 folds, on the Mac): category TO − FULL = −0.108 ± 0.099 (p = 0.07), region −0.014 ± 0.376
> (p = 0.94). Evidence and protocol: `docs/results/closing_data/v18/g1_integrity_al/` (`5cd62589`).
> Florida is running from an external-SSD clone; Arizona's inputs are staged. The "prepared, not
> run" status below is the record of 2026-10-01.

**Status 2026-10-01: prepared, not run. Not on nespedgpu.** The box hard-reset four times
(2026-09-30, boots 05:19, 05:22, 16:46, 21:28), each time 7–70 s into the Alabama fold-0 train-only
build below, while a steady 300 W matmul stress test survived. The last run carried a 1 s fsync'd
monitor: nothing was near a limit (GPU ≤100.5 W / 59 °C, CPU ≤68 °C, ~3 % busy, 124 GB RAM free, no
swap), and the journal ends with no shutdown sequence and no kernel lines. The run moves to another
machine; logs in `/dados/poimtlnet/integrity_v18/logs/` on nespedgpu.

> ⚠ **2026-10-01 correction: the splits in §0 were NOT the delivered folds.**
> `scripts/integrity_v2/freeze_split.py` passes `groups=userid.astype(str)` to StratifiedGroupKFold.
> `train.py` (`FoldCreator`), `p1_region_head_ablation.py` and `b3_hmt_grn.py` pass the int64 userids
> from `load_next_data`. SGKF sorts the groups, string order is not integer order, and the two
> partitions differ: at AL and AZ, seed 0, **0 of 5 folds equal, not even as a permutation**
> (sklearn 1.8.0). Integer labels with string userids reproduce `freeze_split` 5/5, so the cast is the
> whole cause; label encoding does not matter. This README's earlier §0 said the rules were identical.
> That was wrong. Assertion #5 (§3) would have aborted the run on it, but the plan was wrong.
> **Fix:** `freeze_split_group_dtype.patch` adds `--group-dtype {str,int}` (default `str`, unchanged,
> because integrity_v2's own results depend on it). With `--group-dtype int` the patched script
> reproduces `train.py`'s folds **5/5 at AL and AZ** (verified 2026-10-01 on nespedgpu from a temporary
> copy; repo untouched).

**What it is.** Ch. 5 reports a "whole-dataset training" check (region −0.33…+0.01 Acc@10, category
0.00…+0.29 macro-F1). That number came from A4 (`scripts/pre_freeze_gates/a4_*.py`), which ran on a
different protocol from the delivered cells:

| | A4 | delivered |
|---|---|---|
| rows | canonical stride-9, **12,709** at AL | `dk_ovl` stride-1, **96,326** |
| region log_T prior | **on** | **off** |
| epochs / device | 30 / CPU | 50 / CUDA fp32 |
| held-out users vs the delivered folds | canonical-row split | 74–82 % (AL) / 78–82 % (AZ) of each delivered fold's val users were on A4's training side (AL fold 0: 183 of 222), measured against `train.py`'s real folds |

The author ruled (2026-09-30) that both halves are re-run on the delivered protocol: AL/AZ/FL, seed 0,
5 folds. Rules: new names only, no existing `output/` engine overwritten, never `regen_emb_alpha.py`,
nothing deleted.

## Files here

| file | what |
|---|---|
| `README.md` | this plan |
| `paths_to_f_enum.patch` | adds `CHECK2HGI_V18_TO_F{0..4}` to `EmbeddingEngine` (additive, end of enum). Needed because `train.py --engine` is a closed enum |
| `a4_build_dk_ovl.patch` | `scripts/pre_freeze_gates/a4_build.py`: split from a frozen `dk_ovl` JSON; output as a NEW engine `check2hgi_design_k_resln_mae_l0_1_to_f<F>`; fresh pseudo tag `a4dk`; refuses to overwrite; keeps pseudo artifacts by default; `--device` passthrough; writes `build.json` provenance |
| `freeze_split_group_dtype.patch` | `scripts/integrity_v2/freeze_split.py`: adds `--group-dtype {str,int}`, default `str` (unchanged). `int` reproduces `train.py`'s folds; records `group_dtype` in the JSON. Added 2026-10-01, see the correction above |

All three patches applied cleanly to the tree at the time of writing (`git apply --check`). **All three
were applied on 2026-10-01 in `d01cd2a8`** (author-approved queue item G1), with one addition:
`a4_build.py` asserts `group_dtype == 'int'` in the split JSON. Until 2026-10-02 this paragraph said
"Neither is applied".

Two traps the `a4_build` patch closes: the original skips when
`results/pre_freeze_gates/a4/<st>_s0_f<F>_regemb.parquet` exists, so an unpatched re-run silently
reuses the OLD wrong-split tables; and it writes to `results/` (on nespedgpu that is `/home`, full).

⚠ **Footprint that the patch does not remove.** The v14 builder (`scripts/probe/build_design_k_delaunay.py`)
hard-codes `REPO/"output"/...`, so pseudo-state SUBDIRS `<state>_a4dk_s0_f<F>` appear inside
`output/check2hgi/`, `output/hgi/` (symlinks) and `output/check2hgi_design_k_resln_mae_l0_1/`, plus
`data/checkins/<State>_a4dk_s0_f<F>.parquet`. New names, no existing state dir touched. A zero-footprint
version needs the builder's paths patched too.

## 0 · Already done (no GPU)

- ⚠ **`/dados/poimtlnet/integrity_v18/splits/` (15 files, 2026-09-30) are NOT the delivered folds.**
  They were made with the unpatched `freeze_split.py` (string userids). They are left in place,
  untouched, and must not be used. AL F0 is byte-identical to the committed
  `docs/results/check2hgi_integrity_v2/alabama/split_seed0_fold0.json`, which only shows that
  `freeze_split` reproduces itself; that committed split is also not the delivered fold.
- **The splits to use** (not generated yet), after `freeze_split_group_dtype.patch` is applied:
  `freeze_split.py --state <st> --seed 0 --fold <F> --n-folds 5 --engine check2hgi_dk_ovl --group-dtype int`
  for AL/AZ/FL × F0–4. Rows = the delivered engines: 96,326 / 200,895 / 1,274,418. With int groups,
  AL n_val per fold = 19,265 / 19,264 / 19,265 / 19,267 / 19,265.
- **The delivered fold rule.** `train.py`'s `FoldCreator` for NEXT = `StratifiedGroupKFold(shuffle=True,
  random_state=seed)` on the **int64** userids from `load_next_data`, y = next_category. `p1_region_head_ablation.py`
  and `b3_hmt_grn.py` use the same int64 userids, so category and region scoring folds agree. The delivered
  `check2hgi_v18` engines carry no frozen fold cache, so the delivered cells generated folds on the fly;
  the new arms do the same. `train.py` never writes a fold cache (it loads a frozen one or generates in memory).

## 1 · Category half, per state `st`, fold `F`

Needs only `paths_to_f_enum.patch`.
```
S=$R/splits/${st}_split_seed0_fold${F}.json
python scripts/integrity_v2/build_study_repr.py --state $st --cell TO_F$F --repr-seed 42 --epochs 500 \
  --device cuda --encoder resln --forward-only --add-continuous-time --exclude-users-file $S \
  --study-root $R/repr
python scripts/integrity_v2/infer_checkins.py --state $st --checkpoint $R/repr/$st/TO_F$F/checkpoint.pt \
  --readout prefix_forward_only --out $R/repr/$st/TO_F$F/win_matched.npz --self-test
python scripts/integrity_v2/materialize_engine.py --state $st --arm-npz $R/repr/$st/TO_F$F/win_matched.npz \
  --source-engine check2hgi_dk_ovl --dest-engine check2hgi_v18_to_f$F
# then, as run_phase0_build.sh materialize_state(): copy temp/sequences_next.parquet from
# output/check2hgi_dk_ovl/$st/, and SYMLINK region_embeddings.parquet from
# output/check2hgi_design_k_resln_mae_l0_1/$st/ (never copy)
```
- `--exclude-users-file` drops the validation users' nodes and edges and recomputes the place
  aggregates from training check-ins only (`restrict_to_users`). It records `n_excluded_users`, a
  sha256 of the sorted val users, and the graph stats in `build.json`.
- `infer_checkins.py` with no `--users-from` encodes ALL users with the train-only weights. Held-out
  users are encoded inductively; the check-in graph is a disjoint union of per-user paths and carries
  no place identity. This closes the 67–87% place-coverage proxy the original check needed, so it is a
  better measurement, not a straight repeat, and should be described that way.

Train, both arms, same session, identical flags: `cell_cat()` from `run_wave.sh` plus `--only-fold`.
```
env MTL_NO_TRAIN_DIAGNOSTICS=1 MTL_DISABLE_AMP=1 RESULTS_ROOT=$R/results python scripts/train.py \
  --task next --state $st --engine <check2hgi_v18_to_f$F | check2hgi_v18> --model next_gru --embedding-dim 64 \
  --folds 5 --only-fold $F --epochs 50 --seed 0 --batch-size 8192 \
  --max-lr <AL 0.0025 | AZ 0.0005 | FL 0.005> --logit-adjust-tau 0.5 --compile --tf32 --no-checkpoints
python scripts/closing_data/score_stl_cat_ceiling.py <rundir> --tag integ18_cat_<to|full>_${st}_f$F
```
Why the full arm is re-run rather than quoted from the delivered per-fold values: `--only-fold` and
`torch.compile` move a fold's number by up to ~0.3 pp relative to its place in the 5-fold run
(repo-root `CLAUDE.md`, the P1 note), which is the size of the effect being measured. Paired,
same-session arms remove that. Confirm on first use that the scorer handles a single-fold rundir.

## 2 · Region half, per `st`, `F`

Needs `a4_build_dk_ovl.patch`.
```
python scripts/pre_freeze_gates/a4_build.py --state $st --seed 0 --fold $F --split-json $S --device cuda
#   -> output/check2hgi_design_k_resln_mae_l0_1_to_f$F/$st/region_embeddings.parquet (+ build.json)
env MTL_CHUNK_VAL_METRIC=1 MTL_DISABLE_AMP=1 MTL_STRICT=1 RESULTS_ROOT=$R/results \
  python -u scripts/p1_region_head_ablation.py --state $st --heads next_stan_flow --input-type region \
  --region-emb-source <check2hgi_design_k_resln_mae_l0_1_to_f$F | check2hgi_design_k_resln_mae_l0_1> \
  --override-hparams freeze_alpha=True alpha_init=0.0 --engine-override check2hgi_v18 \
  --folds 5 --only-fold $F --epochs 50 --seed 0 --target region --max-lr 0.003 --compile --tf32 \
  --tag integ18_reg_<to|full>_${st}_f$F
```
- This is `cell_reg()` verbatim plus `--only-fold` and the region source.
- `p1` resolves any source starting with `check2hgi_design_k` to `output/<source>/<state>/region_embeddings.parquet`,
  so `p1` needs no change.
- `p1` writes its JSON to `docs/results/P1/` (≈19 KB each, 30 files).
- The prior is off (`freeze_alpha=True alpha_init=0.0`). Confirm on first use that `p1` does not require
  the per-fold `region_transition_log_seed0_fold<F+1>.pt` to exist for an inert prior.

## 3 · Integrity assertions (each run aborts on failure)

1. **Category `build.json`.** `training_users.n_excluded_users == len(split val_users)`,
   `val_users_sha256` equals the sha of the split's sorted val users, graph `restricted: true`, `epochs: 500`.
2. **Zero validation users in each fold's training graph.** No val userid in the restricted graph's
   metadata (category). `a4_build` asserts it on the training check-ins and records it (region).
3. **Fresh builds only.** Each `TO_F` cell dir and each new engine dir must not exist before its build.
4. **No rows dropped.** materialize `n_windows == n_windows_source`; a dropped row shifts the split.
5. **Same fold for representation and scoring.** Before training, SGKF(seed 0) over the engine's
   `load_next_data` rows, with the **int64** userids `train.py` uses, reproduces the split JSON's
   `val_idx_sha256`. This is the check that catches a string-userid split (the 2026-10-01 correction).
6. **Region table complete.** The remapped table has the full region count; `absent_from_train` is recorded.
7. **Frozen engines untouched.** Nothing under `output/check2hgi`, `output/check2hgi_v18` or
   `output/check2hgi_design_k_resln_mae_l0_1` changes except the new `*_a4dk_*` pseudo subdirs
   (`find -newer`, as in the floor arm).
8. **Disk.** Free space on the results disk logged at the start and end of every job; abort below 2 GB.

## 4 · Timing

- **Measured (partial).** The AL fold-0 train-only build ran at **4.8–5.1 it/s** on the RTX 6000 Ada,
  about 100 s for 500 epochs plus ~20 s setup. That is from the two build logs, before each reset.
  No readout or training time was reached.
- **Extrapolated.**
  - Category builds: AL ~2, AZ ~4, FL ~15–20 min each.
  - Prefix readout: O(n²) per user; FL dominates, ≈1 h for 5 folds.
  - Training: each single-fold launch pays a ~2 min `torch.compile` warm-up, so 30 launches ≈ 1 h of
    overhead alone.
  - **Total ≈ 7–11 GPU-h for both halves.** The FL terms are the uncertain ones.
- **The first step on any machine** should be one AL fold of each half, timed, before the rest.

## 5 · Running it somewhere other than nespedgpu (H100 / RunPod)

Only paths change. The commands and flags above stay the same.

- **Work root** `R=/dados/poimtlnet/integrity_v18` → any disk with ~20 GB free (e.g. `/workspace/integrity_v18`).
  `RESULTS_ROOT=$R/results` follows it.
- **Splits.** Do NOT copy `$R/splits/` from nespedgpu (string-userid splits, not the delivered folds).
  Generate them on the target with the patched `freeze_split.py --group-dtype int` (§0), then check
  assertion #5 before any build: SGKF(seed 0) over the engine's `load_next_data` rows (int64 userids) must
  reproduce each split's `val_idx_sha256`. AL n_val per fold should read 19,265 / 19,264 / 19,265 / 19,267 / 19,265.
- **Inputs the repo's `output/` and `data/` must hold** (on nespedgpu both are symlinks into `/dados`):
  - `output/check2hgi/<st>/temp/checkin_graph.pt`: read by `build_study_repr.py`, `infer_checkins.py`,
    the v14 builder, and the `a4_build` region remap.
  - `output/check2hgi_dk_ovl/<st>/`: `input/next.parquet`, `input/next_region.parquet`,
    `temp/sequences_next.parquet`, `materialize_engine.py`'s source, and `freeze_split.py`.
  - `output/check2hgi_v18/<st>/`: the full-data category arm.
  - `output/check2hgi_design_k_resln_mae_l0_1/<st>/region_embeddings.parquet`: the full-data region
    arm and the symlink target.
  - `output/hgi/<st>/`: `temp/{edges.csv,pois.csv}`, `poi_embeddings.parquet`,
    `poi2vec_poi_embeddings_<State>.csv` (the Delaunay/POI2Vec scaffolding for both builders).
  - `data/checkins/<State>.parquet` and the TIGER shapefiles
    `data/miscellaneous/tl_2022_{01,04,12}_tract_{AL,AZ,FL}/` (the region half).
  - `docs/infra/data/drive_download.md` describes fetching these from Drive.
- **`a4_build` hard-codes the design_k subprocess interpreter** as `<repo>/.venv/bin/python`. A machine
  whose venv lives elsewhere needs a `.venv` symlink at the repo root.
- **torch 2.11.0+cu128.** `train.py` warns on any other version, and `MTL_STRICT=1` (set on the region
  cells) hard-fails some guards.
- **fp32 stays** (`MTL_DISABLE_AMP=1`): bf16 grad-NaNs at large class counts on the A40 are documented.
- **Run every job under `tmux` + `nohup`.** An SSH drop killed an un-tmuxed timing run once.
