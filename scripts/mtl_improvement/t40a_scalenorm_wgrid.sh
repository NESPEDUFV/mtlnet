#!/bin/bash
# T4.0a completion — scale-norm NEEDS its w re-tuned (the card: "divide each CE by log(num_classes),
# THEN re-tune w"). At G's default cw=0.75 the post-norm balance is ~13x cat-heavy → reg starves
# (FL reg 35.47). Post-norm, the cw that BALANCES the two equal-scale tasks is cw≈0.19 at FL
# (1.95(1-cw)=8.46cw). Grid reg-favorable cw ∈ {0.10,0.20,0.35} with --loss-scale-norm, AL+FL seed0.
#   STATE=florida CONC=2 setsid bash scripts/mtl_improvement/t40a_scalenorm_wgrid.sh > /tmp/t40a/fl.log 2>&1 &
set -uo pipefail
REPO=/home/vitor.oliveira/PoiMtlNet; cd "$REPO"; export PYTHONPATH=src
PY=.venv/bin/python; V14=check2hgi_design_k_resln_mae_l0_1
ST=${STATE:-alabama}; SD=0; EPOCHS=50; CONC=${CONC:-2}
LOGDIR=/tmp/t40a/$ST; mkdir -p "$LOGDIR"
MAN=scripts/mtl_improvement/t40a_wgrid_manifest.tsv; [ -f "$MAN" ] || : > "$MAN"
export OMP_NUM_THREADS=$((32 / CONC))
ts(){ date '+%Y-%m-%d %H:%M:%S'; }; say(){ echo "[$(ts)] T40A[$ST] $*"; }
COMMON=(--task mtl --canon none --task-set check2hgi_next_region --engine "$V14"
  --state "$ST" --seed "$SD" --epochs "$EPOCHS" --folds 5 --batch-size 2048
  --no-reg-class-weights --no-cat-class-weights
  --cat-head next_gru --reg-head next_stan_flow_dualtower
  --reg-head-param raw_embed_dim=64 --reg-head-param fusion_mode=aux
  --reg-head-param freeze_alpha=True --reg-head-param alpha_init=0.0
  --task-a-input-type checkin --task-b-input-type region --log-t-kd-weight 0.0
  --scheduler onecycle --max-lr 3e-3 --cat-lr 1e-3 --reg-lr 3e-3 --shared-lr 1e-3
  --model mtlnet_crossattn_dualtower --loss-scale-norm
  --per-fold-transition-dir "output/$V14/$ST" --no-checkpoints)
run_cw(){ local cw=$1; local key="scalenorm_cw${cw}|${ST}"
  grep -qF "$key	" "$MAN" && { say "skip $key"; return 0; }
  local log="$LOGDIR/cw${cw}.log"; say "start cw=$cw"
  $PY scripts/train.py "${COMMON[@]}" --mtl-loss static_weight --category-weight "$cw" > "$log" 2>&1 &
  local pid=$!; wait "$pid"
  if [ $? -eq 0 ]; then
    local rd; rd=$(ls -d results/$V14/$ST/mtlnet_*ep${EPOCHS}_*_${pid} 2>/dev/null | head -1)
    [ -z "$rd" ] && rd=$(ls -dt results/$V14/$ST/mtlnet_*ep${EPOCHS}_* 2>/dev/null | head -1)
    printf '%s\tscalenorm_cw%s\t%s\n' "$key" "$cw" "$rd" >>"$MAN"; say "done cw=$cw -> $rd"
  else say "FAIL cw=$cw"; fi
}
say "=== T4.0a scale-norm cw-grid {0.10,0.20,0.35} seed0 ==="
for cw in 0.10 0.20 0.35; do
  run_cw "$cw" & while [ "$(jobs -rp | wc -l)" -ge "$CONC" ]; do sleep 8; done
done
wait
say "ALL DONE ($ST)"
