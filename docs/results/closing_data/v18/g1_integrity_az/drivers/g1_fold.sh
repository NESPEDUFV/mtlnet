#!/usr/bin/env bash
# usage: g1_fold.sh <state> <fold> <max_lr_cat> [delivered=1]   -- one G1 fold, RESUMABLE, fail-stop
set -u; C="/Volumes/Vitor's SSD/ingred_g1"; cd "$C"; G="$C/g1_logs/g1_run.sh"; source "$C/g1_logs/g1_lib.sh"
ST=$1; F=$2; LR=$3; DEL=${4:-1}; S=results/g1/splits/${ST}_split_seed0_fold${F}.json; R=results/integ18_repr/$ST
export PYTHONPATH="$C/src:$C/research:$C/scripts:$C" MTL_RAM_HEADROOM_GB=4
A(){ .venv/bin/python g1_logs/g1_assert.py $ST $F $1 >> g1_logs/ASSERTS_${ST}.log 2>&1 || { echo "ASSERT FAIL $ST f$F $1"; tail -3 g1_logs/ASSERTS_${ST}.log; exit 1; }; }
T=${ST}_f$F
if ! done_ok ${T}_build; then for p in "$R/TO_F$F" "output/check2hgi_v18_to_f$F/$ST" "output/check2hgi_design_k_resln_mae_l0_1_to_f$F/$ST"; do [ -e "$p" ] && { echo "A3 FAIL exists $p"; exit 1; }; done; fi
[ -f $S ] || .venv/bin/python scripts/integrity_v2/freeze_split.py --state $ST --seed 0 --fold $F --n-folds 5 --engine check2hgi_dk_ovl --group-dtype int --out $S >> g1_logs/ASSERTS_${ST}.log 2>&1; A split
step ${T}_build - .venv/bin/python scripts/integrity_v2/build_study_repr.py --state $ST --cell TO_F$F --repr-seed 42 --epochs 500 --device cpu --encoder resln --forward-only --add-continuous-time --exclude-users-file $S --study-root results/integ18_repr; A build
step ${T}_infer - .venv/bin/python scripts/integrity_v2/infer_checkins.py --state $ST --checkpoint $R/TO_F$F/checkpoint.pt --readout prefix_forward_only --out $R/TO_F$F/win_matched.npz --self-test
step ${T}_mat - .venv/bin/python scripts/integrity_v2/materialize_engine.py --state $ST --arm-npz $R/TO_F$F/win_matched.npz --source-engine check2hgi_dk_ovl --dest-engine check2hgi_v18_to_f$F
mkdir -p output/check2hgi_v18_to_f$F/$ST/temp; cp output/check2hgi_dk_ovl/$ST/temp/sequences_next.parquet output/check2hgi_v18_to_f$F/$ST/temp/
ln -sfn "$C/output/check2hgi_design_k_resln_mae_l0_1/$ST/region_embeddings.parquet" output/check2hgi_v18_to_f$F/$ST/region_embeddings.parquet; A materialize
REC="--task next --state $ST --model next_gru --embedding-dim 64 --folds 5 --only-fold $F --epochs 50 --seed 0 --batch-size 8192 --max-lr $LR --logit-adjust-tau 0.5 --no-checkpoints"
G1_HEAVY=1 step ${T}_cat_to "$C/results/g1_cat_f$F/to/check2hgi_v18_to_f$F/$ST" env RESULTS_ROOT="$C/results/g1_cat_f$F/to" .venv/bin/python scripts/train.py $REC --engine check2hgi_v18_to_f$F
G1_HEAVY=1 step ${T}_cat_full "$C/results/g1_cat_f$F/full_cpu/check2hgi_v18/$ST" env OUTPUT_DIR="$C/output_fullcpu" RESULTS_ROOT="$C/results/g1_cat_f$F/full_cpu" .venv/bin/python scripts/train.py $REC --engine check2hgi_v18
[ "$DEL" = 1 ] && G1_HEAVY=1 step ${T}_cat_del "$C/results/g1_cat_f$F/delivered/check2hgi_v18/$ST" env RESULTS_ROOT="$C/results/g1_cat_f$F/delivered" .venv/bin/python scripts/train.py $REC --engine check2hgi_v18
step ${T}_regbuild - .venv/bin/python scripts/pre_freeze_gates/a4_build.py --state $ST --seed 0 --fold $F --split-json $S --device cpu; A region
PREC="--state $ST --heads next_stan_flow --input-type region --override-hparams freeze_alpha=True alpha_init=0.0 --engine-override check2hgi_v18 --folds 5 --only-fold $F --epochs 50 --seed 0 --target region --max-lr 0.003"
PENV="MTL_CHUNK_VAL_METRIC=1 MTL_STRICT=1 P1_HITS_FROM_RANK=0 P1_STREAM_GPU=0"
G1_HEAVY=1 step ${T}_reg_to - env $PENV .venv/bin/python -u scripts/p1_region_head_ablation.py $PREC --region-emb-source check2hgi_design_k_resln_mae_l0_1_to_f$F --tag g1_reg_to_${ST}_f$F
G1_HEAVY=1 step ${T}_reg_full - env $PENV .venv/bin/python -u scripts/p1_region_head_ablation.py $PREC --region-emb-source check2hgi_design_k_resln_mae_l0_1_fullcpu_s0 --tag g1_reg_fullcpu_s0_${ST}_f$F
[ "$DEL" = 1 ] && G1_HEAVY=1 step ${T}_reg_del - env $PENV .venv/bin/python -u scripts/p1_region_head_ablation.py $PREC --region-emb-source check2hgi_design_k_resln_mae_l0_1 --tag g1_reg_delivered_${ST}_f$F
echo "FOLD DONE $ST f$F $(date '+%F %T')"
if [ "${G1_DELETE_TO:-0}" = 1 ]; then
  for f in next.parquet next_region.parquet; do rm -f "${C:?}/output/check2hgi_v18_to_f${F:?}/${ST:?}/input/$f"; done
  echo "input parquets deleted $(date '+%F %T') after fold scored; rebuild: materialize_engine.py from $R/TO_F$F/win_matched.npz" > "$C/output/check2hgi_v18_to_f$F/$ST/input/DELETED.txt"
fi
