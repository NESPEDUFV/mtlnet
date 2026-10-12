#!/bin/bash
# T5.2 (proper) — cat-head encoder sweep UNDER champion G. The earlier T5.2 "DONE" rested on
# the Tier-S STL head search + the B-A4 cat-LOSS family; a clean cat-ENCODER swap under MTL-G
# across the registry was never run. Given the cat gain is ARCHITECTURE-driven (cat-transfer
# ablation), a better head on the cross-attn trunk could add. Swap --cat-head only; everything
# else = G. Score matched-metric (cat F1 target; reg-full non-inferior). FL+AL seed0.
# Usage: STATE=alabama CONC=5 setsid bash scripts/mtl_improvement/t52_cathead_sweep.sh > /tmp/t52/al.log 2>&1 &
set -uo pipefail
REPO=/home/vitor.oliveira/PoiMtlNet; cd "$REPO"; export PYTHONPATH=src
PY=.venv/bin/python; V14=check2hgi_design_k_resln_mae_l0_1
ST=${STATE:-alabama}; SD=0; EPOCHS=50; CONC=${CONC:-4}
LOGDIR=/tmp/t52/$ST; mkdir -p "$LOGDIR"
MAN=scripts/mtl_improvement/t52_cathead_manifest.tsv; [ -f "$MAN" ] || : > "$MAN"
export OMP_NUM_THREADS=$((32 / CONC))
ts(){ date '+%Y-%m-%d %H:%M:%S'; }; say(){ echo "[$(ts)] T52[$ST] $*"; }
COMMON=(--task mtl --canon none --task-set check2hgi_next_region --engine "$V14"
  --state "$ST" --seed "$SD" --epochs "$EPOCHS" --folds 5 --batch-size 2048
  --no-reg-class-weights --no-cat-class-weights
  --mtl-loss static_weight --category-weight 0.75
  --reg-head next_stan_flow_dualtower
  --reg-head-param raw_embed_dim=64 --reg-head-param fusion_mode=aux
  --reg-head-param freeze_alpha=True --reg-head-param alpha_init=0.0
  --task-a-input-type checkin --task-b-input-type region --log-t-kd-weight 0.0
  --scheduler onecycle --max-lr 3e-3 --cat-lr 1e-3 --reg-lr 3e-3 --shared-lr 1e-3
  --model mtlnet_crossattn_dualtower
  --per-fold-transition-dir "output/$V14/$ST" --no-checkpoints)
run(){ local head=$1; local key="cathead_${head}|${ST}"
  grep -qF "$key	" "$MAN" && { say "skip $key"; return 0; }
  local log="$LOGDIR/${head}.log"; say "start cat-head=$head"
  $PY scripts/train.py "${COMMON[@]}" --cat-head "$head" > "$log" 2>&1 &
  local pid=$!; wait "$pid"
  if [ $? -eq 0 ]; then
    local rd; rd=$(ls -d results/$V14/$ST/mtlnet_*ep${EPOCHS}_*_${pid} 2>/dev/null | head -1)
    [ -z "$rd" ] && rd=$(ls -dt results/$V14/$ST/mtlnet_*ep${EPOCHS}_* 2>/dev/null | head -1)
    printf '%s\t%s\t%s\n' "$key" "$head" "$rd" >>"$MAN"; say "done $head -> $rd"
  else say "FAIL $head — see $log"; fi
}
HEADS=(next_gru next_lstm next_transformer_relpos next_transformer_optimized next_single
       next_temporal_cnn next_tcn_residual next_conv_attn next_hybrid next_mamba)
say "=== T5.2 cat-head sweep under G: ${#HEADS[@]} heads seed0 CONC=$CONC ==="
for h in "${HEADS[@]}"; do
  run "$h" & while [ "$(jobs -rp|wc -l)" -ge "$CONC" ]; do sleep 8; done
done
wait; say "ALL DONE ($ST)"
