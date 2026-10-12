#!/bin/bash
# (a) Cat-transfer ablation — is the +3pp MTL-cat gain region-DRIVEN (transfer) or
# ARCHITECTURE-driven (the cross-attn shared trunk)? Run G's exact recipe but
# --category-weight 1.0 -> reg loss weight = 0 -> reg contributes ZERO gradient ->
# the shared trunk + cat head train cat-ONLY (with the cross-attn architecture, NO
# region co-training). Compare cat-F1 to G (cw0.75, reg ON) and the STL cat ceiling.
#   cat(cw1.0) ≈ G  -> the gain is the architecture/pipeline (NOT region transfer)
#   cat(cw1.0) <  G  -> region co-training drives the transfer
# FL+AL seed0.  STATE=florida CONC=2 setsid bash .../cat_transfer_ablation.sh ...
set -uo pipefail
REPO=/home/vitor.oliveira/PoiMtlNet; cd "$REPO"; export PYTHONPATH=src
PY=.venv/bin/python; V14=check2hgi_design_k_resln_mae_l0_1; SD=0; EPOCHS=50; CONC=${CONC:-2}
LOGDIR=/tmp/catabl; mkdir -p "$LOGDIR"
MAN=scripts/mtl_improvement/cat_transfer_manifest.tsv; [ -f "$MAN" ] || : > "$MAN"
export OMP_NUM_THREADS=$((32 / CONC))
ts(){ date '+%Y-%m-%d %H:%M:%S'; }; say(){ echo "[$(ts)] CATABL $*"; }
run(){ local st=$1; local key="catonly_cw1.0|${st}"
  grep -qF "$key	" "$MAN" && { say "skip $key"; return 0; }
  local log="$LOGDIR/${st}.log"; say "start $st (cw=1.0, reg OFF)"
  $PY scripts/train.py --task mtl --canon none --task-set check2hgi_next_region --engine "$V14" \
      --state "$st" --seed "$SD" --epochs "$EPOCHS" --folds 5 --batch-size 2048 \
      --no-reg-class-weights --no-cat-class-weights \
      --mtl-loss static_weight --category-weight 1.0 \
      --cat-head next_gru --reg-head next_stan_flow_dualtower \
      --reg-head-param raw_embed_dim=64 --reg-head-param fusion_mode=aux \
      --reg-head-param freeze_alpha=True --reg-head-param alpha_init=0.0 \
      --task-a-input-type checkin --task-b-input-type region --log-t-kd-weight 0.0 \
      --scheduler onecycle --max-lr 3e-3 --cat-lr 1e-3 --reg-lr 3e-3 --shared-lr 1e-3 \
      --model mtlnet_crossattn_dualtower \
      --per-fold-transition-dir "output/$V14/$st" --no-checkpoints > "$log" 2>&1 &
  local pid=$!; wait "$pid"
  if [ $? -eq 0 ]; then
    local rd; rd=$(ls -d results/$V14/$st/mtlnet_*ep${EPOCHS}_*_${pid} 2>/dev/null | head -1)
    [ -z "$rd" ] && rd=$(ls -dt results/$V14/$st/mtlnet_*ep${EPOCHS}_* 2>/dev/null | head -1)
    printf '%s\tcatonly\t%s\n' "$key" "$rd" >>"$MAN"; say "done $st -> $rd"
  else say "FAIL $st"; fi
}
say "=== cat-transfer ablation (cw=1.0, reg OFF), FL+AL seed0 ==="
run florida & while [ "$(jobs -rp|wc -l)" -ge "$CONC" ]; do sleep 8; done
run alabama & while [ "$(jobs -rp|wc -l)" -ge "$CONC" ]; do sleep 8; done
wait; say "ALL DONE"
