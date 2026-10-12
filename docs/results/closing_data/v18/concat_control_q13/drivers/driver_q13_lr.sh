#!/usr/bin/env bash
# Q13 -- Arizona e Florida refeitos com a TAXA DE APRENDIZADO DO PROPRIO DATASET.
#
# POR QUE. A receita nao e uma so: cada dataset tem sua taxa, registrada no seu sidecar.
#   alabama 0.0025 | arizona 0.0005 | florida 0.005 | california 0.005 | texas 0.005 | istanbul 0.0005
# A primeira onda usou 0.0025 em todos, que e a taxa de Alabama. O controle de fidelidade por MEDIA
# passou mesmo assim (Arizona 31.9660 contra 31.9278 reportado), mas por FOLD nao bate: as
# diferencas chegam a 0.21 ponto e trocam de sinal. Em Alabama, com a taxa certa, a diferenca por
# fold e exatamente zero nos cinco folds. Essa igualdade e a unica evidencia de que o braco
# reproduz de fato; media proxima nao e.
set -u
cd /home/vitor.oliveira/PoiMtlNet
export PYTHONPATH=src
export DISABLE_AMP=1 MTL_DISABLE_AMP=1 MTL_STRICT=1 MTL_COMPILE_DYNAMIC=1
export PYTORCH_CUDA_ALLOC_CONF="expandable_segments:True"
export TORCHINDUCTOR_CACHE_DIR=$HOME/.inductor_cache_board
export OMP_NUM_THREADS=8
PY=/home/vitor.oliveira/.venv/bin/python
mkdir -p wave_logs
log(){ echo "[$(date -u +%H:%M:%S)] $*" | tee -a wave_logs/DRIVER_q13_lr.log; }

run_arm(){
  local st=$1 arm=$2 eng=$3 lr=$4 extra=${5:-}
  local free; free=$(df -BG --output=avail /home/vitor.oliveira | tail -1 | tr -dc '0-9')
  if [ "$free" -lt 15 ]; then log "ABORTA $st/$arm: disco ${free}G"; return 9; fi
  log "INICIA $st/$arm eng=$eng lr=$lr (disco ${free}G)"
  local t0=$SECONDS
  $PY -u scripts/train.py --task next --state "$st" --engine "$eng" \
    --model next_gru --folds 5 --epochs 50 --seed 0 \
    --batch-size 8192 --max-lr "$lr" --logit-adjust-tau 0.5 \
    --gradient-accumulation-steps 1 $extra --compile --tf32 --no-checkpoints \
    > "wave_logs/q13lr_${arm}_${st}.log" 2>&1
  local rc=$?
  log "TERMINA $st/$arm rc=$rc ($((SECONDS-t0))s)"
  return $rc
}

if ! run_arm arizona place   hgi_dk_ovl    0.0005;                              then log "PARA arizona/place";   exit 1; fi
if ! run_arm arizona feat    hgi_ovl_feat  0.0005 "--model-param embed_dim=75"; then log "PARA arizona/feat";    exit 1; fi
if ! run_arm arizona checkin check2hgi_v18 0.0005;                              then log "PARA arizona/checkin"; exit 1; fi
if ! run_arm florida place   hgi_dk_ovl    0.005;                               then log "PARA florida/place";   exit 1; fi
if ! run_arm florida feat    hgi_ovl_feat  0.005 "--model-param embed_dim=75";  then log "PARA florida/feat";    exit 1; fi
if ! run_arm florida checkin check2hgi_v18 0.005;                               then log "PARA florida/checkin"; exit 1; fi
log "ONDA COM TAXAS POR DATASET COMPLETA"

