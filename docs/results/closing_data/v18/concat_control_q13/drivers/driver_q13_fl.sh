#!/usr/bin/env bash
# Q13 -- Florida, os tres bracos. Mesma receita validada dos outros dois datasets.
# Florida ficou de fora da primeira onda porque o next.parquet do place embedding nunca tinha
# sido construido. Medido em 2026-08-16: disco com 37 GB livres, o arquivo construido ocupa
# 1,9 GB. Disco nunca foi o obstaculo.
set -u
cd /home/vitor.oliveira/PoiMtlNet
export PYTHONPATH=src
export DISABLE_AMP=1 MTL_DISABLE_AMP=1 MTL_STRICT=1 MTL_COMPILE_DYNAMIC=1
export PYTORCH_CUDA_ALLOC_CONF="expandable_segments:True"
export TORCHINDUCTOR_CACHE_DIR=$HOME/.inductor_cache_board
export OMP_NUM_THREADS=8
PY=/home/vitor.oliveira/.venv/bin/python
mkdir -p wave_logs
log(){ echo "[$(date -u +%H:%M:%S)] $*" | tee -a wave_logs/DRIVER_q13_fl.log; }
MIN_FREE_GB=15

run_arm(){
  local arm=$1 eng=$2 extra=${3:-}
  local free; free=$(df -BG --output=avail /home/vitor.oliveira | tail -1 | tr -dc '0-9')
  if [ "$free" -lt "$MIN_FREE_GB" ]; then log "ABORTA florida/$arm: disco ${free}G"; return 9; fi
  log "INICIA florida/$arm eng=$eng (disco ${free}G)"
  local t0=$SECONDS
  $PY -u scripts/train.py --task next --state florida --engine "$eng" \
    --model next_gru --folds 5 --epochs 50 --seed 0 \
    --batch-size 8192 --max-lr 0.0025 --logit-adjust-tau 0.5 \
    --gradient-accumulation-steps 1 $extra --compile --tf32 --no-checkpoints \
    > "wave_logs/q13f_${arm}_florida.log" 2>&1
  local rc=$?
  log "TERMINA florida/$arm rc=$rc ($((SECONDS-t0))s)"
  return $rc
}

if ! run_arm place   hgi_dk_ovl;                                then log "PARA florida/place";   exit 1; fi
if ! run_arm feat    hgi_ovl_feat "--model-param embed_dim=75"; then log "PARA florida/feat";    exit 1; fi
if ! run_arm checkin check2hgi_v18;                             then log "PARA florida/checkin"; exit 1; fi
log "FLORIDA COMPLETA"

