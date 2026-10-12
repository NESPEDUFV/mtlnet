#!/usr/bin/env bash
# v2 (D2b 17571c16): cat arms with MTL_DATASET_CPU=1 + CPU-residency probe. G1 FL one fold, author-approved CRITICAL-tier watchdog, knowladge's order: cat FULL, cat TO, [md5 assert], reg FULL (p1 measurement), regbuild, reg TO.
# usage: g1_fl_fold_ordered.sh <fold>   (TO build + readout + materialize for the fold must already exist or are run first)
set -u; C="/Volumes/Vitor's SSD/ingred_g1fl"; cd "$C"; G="$C/g1_logs/g1_run_crit.sh"; source "$C/g1_logs/g1_lib.sh"
ST=florida; F=$1; LR=0.005; S=results/g1/splits/${ST}_split_seed0_fold${F}.json; R=results/integ18_repr/$ST; T=${ST}_f$F
export PYTHONPATH="$C/src:$C/research:$C/scripts:$C" MTL_RAM_HEADROOM_GB=4
A(){ .venv/bin/python g1_logs/g1_assert.py $ST $F $1 >> g1_logs/ASSERTS_${ST}.log 2>&1 || { echo "ASSERT FAIL $ST f$F $1"; tail -3 g1_logs/ASSERTS_${ST}.log; exit 1; }; }
nocache(){ for d in output/check2hgi_v18_to_f$F/$ST output_fullcpu/check2hgi_v18/$ST output/check2hgi_dk_ovl/$ST; do [ -e "$d/folds" ] && { echo "CACHE PRESENT $d/folds -> refusing (eager rebuild_dataloaders would bypass D2)"; exit 1; }; done; echo "no fold cache on FL paths (f$F) $(date +%T)" >> g1_logs/ASSERTS_${ST}.log; }
onfly(){ grep -q "Generating folds on the fly" "g1_logs/$1/out.log" || { echo "ASSERT FAIL $1: folds not generated on the fly"; exit 1; }; echo "$1: 'Generating folds on the fly' OK" >> g1_logs/ASSERTS_${ST}.log; }
# --- TO substrate for this fold (skips if already done) ---
if ! grep -q "A1/A2 OK florida f$F" g1_logs/ASSERTS_${ST}.log 2>/dev/null; then
  [ -f $S ] || .venv/bin/python scripts/integrity_v2/freeze_split.py --state $ST --seed 0 --fold $F --n-folds 5 --engine check2hgi_dk_ovl --group-dtype int --out $S >> g1_logs/ASSERTS_${ST}.log 2>&1
  grep -q "A5 OK florida f$F" g1_logs/ASSERTS_${ST}.log || A split
  step ${T}_build - .venv/bin/python scripts/integrity_v2/build_study_repr.py --state $ST --cell TO_F$F --repr-seed 42 --epochs 500 --device cpu --encoder resln --forward-only --add-continuous-time --exclude-users-file $S --study-root results/integ18_repr; A build
fi
step ${T}_infer - .venv/bin/python scripts/integrity_v2/infer_checkins.py --state $ST --checkpoint $R/TO_F$F/checkpoint.pt --readout prefix_forward_only --out $R/TO_F$F/win_matched.npz --self-test
step ${T}_mat - .venv/bin/python scripts/integrity_v2/materialize_engine.py --state $ST --arm-npz $R/TO_F$F/win_matched.npz --source-engine check2hgi_dk_ovl_srcview --dest-engine check2hgi_v18_to_f$F
D=output/check2hgi_v18_to_f$F/$ST; mkdir -p $D/temp; cp output/check2hgi_dk_ovl/$ST/temp/sequences_next.parquet $D/temp/
ln -sfn "$C/output/check2hgi_dk_ovl/$ST/input/next_region.parquet" $D/input/next_region.parquet
ln -sfn "$C/output/check2hgi_design_k_resln_mae_l0_1/$ST/region_embeddings.parquet" $D/region_embeddings.parquet; A materialize
dsnote(){ echo "note: dataset CPU-resident (MTL_DATASET_CPU=1, D2b 17571c16); the device choice does not change the numbers (docs/studies/closing_data/v18/gpu_queue/dataset_cpu_proof: base == cpu+D2b byte-identical)" >> "g1_logs/$1/RUN.txt"; }
dsprobe(){ # same code + env, AL inputs (tiny): the switch makes the loader tensors CPU-resident. Size-independent (env checked before any size logic in _dataset_device).
  r=$(MTL_DATASET_CPU=1 OUTPUT_DIR=/Users/vitor/dcpu_scratch/output DATA_ROOT=/Users/vitor/dcpu_scratch/data .venv/bin/python /Users/vitor/dcpu_scratch/probe_device.py 2>/dev/null | grep "MTL_DATASET_CPU=")
  echo "$r" >> g1_logs/ASSERTS_${ST}.log; echo "$r" | grep -q "train.features.device=cpu val.features.device=cpu" || { echo "ASSERT FAIL dataset not CPU-resident under MTL_DATASET_CPU=1: $r"; exit 1; }
  echo "dataset CPU-resident under MTL_DATASET_CPU=1 (probe, commit $(git rev-parse --short HEAD)) OK" >> g1_logs/ASSERTS_${ST}.log; }
# --- category arms ---
dsprobe
REC="--task next --state $ST --model next_gru --embedding-dim 64 --folds 5 --only-fold $F --epochs 50 --seed 0 --batch-size 8192 --max-lr $LR --logit-adjust-tau 0.5 --no-checkpoints"
nocache; step ${T}_cat_full "$C/results/g1_cat_f$F/full_cpu/check2hgi_v18/$ST" env MTL_DATASET_CPU=1 OUTPUT_DIR="$C/output_fullcpu" RESULTS_ROOT="$C/results/g1_cat_f$F/full_cpu" .venv/bin/python scripts/train.py $REC --engine check2hgi_v18; onfly ${T}_cat_full; dsnote ${T}_cat_full
nocache; step ${T}_cat_to "$C/results/g1_cat_f$F/to/check2hgi_v18_to_f$F/$ST" env MTL_DATASET_CPU=1 RESULTS_ROOT="$C/results/g1_cat_f$F/to" .venv/bin/python scripts/train.py $REC --engine check2hgi_v18_to_f$F; onfly ${T}_cat_to; dsnote ${T}_cat_to
# --- inputs md5 assert before region arms ---
( cd /Users/vitor/g1_fl_scratch && while read -r h f; do [ "$(md5 -q "$f")" = "$h" ] || { echo "MD5 MISMATCH $f"; exit 1; }; done < INPUT_MD5S_box.txt ) || { echo "ASSERT FAIL FL input md5"; exit 1; }; echo "FL inputs md5-equal to box (f$F) $(date +%T)" >> g1_logs/ASSERTS_${ST}.log
# --- region arms ---
PREC="--state $ST --heads next_stan_flow --input-type region --override-hparams freeze_alpha=True alpha_init=0.0 --engine-override check2hgi_dk_ovl --folds 5 --only-fold $F --epochs 50 --seed 0 --target region --max-lr 0.003"
PENV="MTL_CHUNK_VAL_METRIC=1 MTL_STRICT=1 P1_HITS_FROM_RANK=0 P1_STREAM_GPU=0"
step ${T}_reg_full - env $PENV .venv/bin/python -u scripts/p1_region_head_ablation.py $PREC --region-emb-source check2hgi_design_k_resln_mae_l0_1_fullcpu_s0 --tag g1_reg_fullcpu_s0_${ST}_f$F
step ${T}_regbuild - .venv/bin/python scripts/pre_freeze_gates/a4_build.py --state $ST --seed 0 --fold $F --split-json $S --device cpu --cleanup-pseudo; A region
step ${T}_reg_to - env $PENV .venv/bin/python -u scripts/p1_region_head_ablation.py $PREC --region-emb-source check2hgi_design_k_resln_mae_l0_1_to_f$F --tag g1_reg_to_${ST}_f$F
echo "FOLD DONE $ST f$F $(date '+%F %T')"
