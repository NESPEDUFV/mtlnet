#!/usr/bin/env bash
# Q13 -- o controle de concatenacao na escala da Tabela 9.
#
# TRES BRACOS por dataset, mesma semente, mesmas dobras, mesma receita:
#   place   -- place embedding sozinho                (reproduz a coluna Place level)
#   feat    -- place embedding + as 11 features por visita  (o controle de concatenacao)
#   checkin -- representacao por check-in             (reproduz a coluna Check-in level)
#
# RECEITA VALIDADA, do sidecar do resultado reportado: next_gru, bs 8192, max_lr 0.0025,
# logit_adjust_tau 0.5, 5 folds, 50 epocas, fp32, compile+tf32. Com ela o braco place em Alabama
# da 29,7261 na epoca 16, o valor reportado exato. Nem run_hgi_ovl_cat_cell.sh (26,35) nem o
# harness p1 (28,83) reproduzem.
#
# SELECAO: macro-F1 na epoca de melhor macro-F1, dos CSVs de validacao por fold.
#
# O braco feat roda como engine propria, hgi_ovl_feat, cujo next.parquet ja traz o place embedding
# com as features concatenadas: 9 blocos de 75 em vez de 64. Por isso ele leva
# --model-param embed_dim=75. Nenhum codigo compartilhado foi alterado.
set -u
cd /home/vitor.oliveira/PoiMtlNet
export PYTHONPATH=src
export DISABLE_AMP=1 MTL_DISABLE_AMP=1 MTL_STRICT=1 MTL_COMPILE_DYNAMIC=1
export PYTORCH_CUDA_ALLOC_CONF="expandable_segments:True"
export TORCHINDUCTOR_CACHE_DIR=$HOME/.inductor_cache_board
export OMP_NUM_THREADS=8
PY=/home/vitor.oliveira/.venv/bin/python
mkdir -p wave_logs

log(){ echo "[$(date -u +%H:%M:%S)] $*" | tee -a wave_logs/DRIVER_q13_final.log; }
MIN_FREE_GB=15

run_arm(){
  local st=$1 arm=$2 eng=$3 extra=${4:-}
  local free; free=$(df -BG --output=avail /home/vitor.oliveira | tail -1 | tr -dc '0-9')
  if [ "$free" -lt "$MIN_FREE_GB" ]; then log "ABORTA $st/$arm: disco ${free}G"; return 9; fi
  log "INICIA $st/$arm eng=$eng (disco ${free}G)"
  local t0=$SECONDS
  $PY -u scripts/train.py --task next --state "$st" --engine "$eng" \
    --model next_gru --folds 5 --epochs 50 --seed 0 \
    --batch-size 8192 --max-lr 0.0025 --logit-adjust-tau 0.5 \
    --gradient-accumulation-steps 1 $extra --compile --tf32 --no-checkpoints \
    > "wave_logs/q13f_${arm}_${st}.log" 2>&1
  local rc=$?
  log "TERMINA $st/$arm rc=$rc ($((SECONDS-t0))s)"
  return $rc
}

if ! run_arm alabama feat    hgi_ovl_feat "--model-param embed_dim=75"; then log "PARA alabama/feat";    exit 1; fi
if ! run_arm alabama checkin check2hgi_v18;                             then log "PARA alabama/checkin"; exit 1; fi
if ! run_arm arizona place   hgi_dk_ovl;                                then log "PARA arizona/place";   exit 1; fi
if ! run_arm arizona feat    hgi_ovl_feat "--model-param embed_dim=75"; then log "PARA arizona/feat";    exit 1; fi
if ! run_arm arizona checkin check2hgi_v18;                             then log "PARA arizona/checkin"; exit 1; fi
log "ONDA Q13 COMPLETA (alabama + arizona)"

