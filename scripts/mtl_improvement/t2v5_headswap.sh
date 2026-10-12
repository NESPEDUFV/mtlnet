#!/bin/bash
# T2V.5 head-swap (CRITIQUE §6.2) — swap STAN in G's private reg tower for {gru,lstm,tcn},
# matched d_model, FL seed0. + T2V.6 per-task-LR arm (reg-head-lr). Anchor: G(stan) 73.57/73.16.
# Waits for the GPU to free (t2vflag flag-arms), then runs. CONC=2. PID capture.
#   CONC=2 setsid bash scripts/mtl_improvement/t2v5_headswap.sh > /tmp/t2v5h/run.log 2>&1 &
set -uo pipefail
REPO=/home/vitor.oliveira/PoiMtlNet; cd "$REPO"; PY=.venv/bin/python
V14=check2hgi_design_k_resln_mae_l0_1; ST=florida; SD=0; EPOCHS=50; CONC=${CONC:-2}
LOGDIR=/tmp/t2v5h; mkdir -p "$LOGDIR"
MAN=scripts/mtl_improvement/t2v5_headswap_manifest.tsv; [ -f "$MAN" ] || : > "$MAN"
export OMP_NUM_THREADS=$((32 / CONC))
ts(){ date '+%Y-%m-%d %H:%M:%S'; }; say(){ echo "[$(ts)] T2V5H $*"; }
say "waiting for GPU to free..."; while true; do p=$(pgrep -fc 'scripts/[t]rain.py'); [ "${p:-0}" -gt 0 ] || break; sleep 60; done
say "GPU free — starting head-swap"
GBASE="--reg-head next_stan_flow_dualtower --reg-head-param raw_embed_dim=64 --reg-head-param fusion_mode=aux --reg-head-param freeze_alpha=True --reg-head-param alpha_init=0.0"
base(){ echo "--task mtl --task-set check2hgi_next_region --engine $V14 --state $ST --seed $SD \
  --epochs $EPOCHS --folds 5 --batch-size 2048 --mtl-loss static_weight --category-weight 0.75 \
  --cat-head next_gru $GBASE --task-a-input-type checkin --task-b-input-type region --log-t-kd-weight 0.0 \
  --scheduler onecycle --max-lr 3e-3 --cat-lr 1e-3 --reg-lr 3e-3 --shared-lr 1e-3 \
  --model mtlnet_crossattn_dualtower --per-fold-transition-dir output/$V14/$ST --no-checkpoints"; }
run(){ local tag=$1; shift; local extra="$*"; local key="${tag}|s${SD}"
  grep -qF "$key	" "$MAN" && { say "skip $key"; return 0; }
  local log="$LOGDIR/${tag}.log"; say "start $key"
  $PY scripts/train.py $(base) $extra > "$log" 2>&1 &
  local pid=$!; wait "$pid"
  if [ $? -eq 0 ]; then local rd; rd=$(ls -d results/$V14/$ST/mtlnet_*ep${EPOCHS}_*_${pid} 2>/dev/null | head -1)
    printf '%s\t%s\t%s\n' "$key" "$tag" "$rd" >>"$MAN"; say "done $key -> $rd"
  else say "FAIL $key — see $log"; fi
}
ARMS=(
  "t2v5_priv_gru|--reg-head-param priv_head=gru"
  "t2v5_priv_lstm|--reg-head-param priv_head=lstm"
  "t2v5_priv_tcn|--reg-head-param priv_head=tcn"
  "t2v6_reghlr1e4|--reg-head-lr 1e-4"
)
say "config: CONC=$CONC FL seed0 — T2V.5 head-swap {gru,lstm,tcn} + T2V.6 reg-head-lr"
for spec in "${ARMS[@]}"; do
  tag=${spec%%|*}; extra=${spec#*|}
  run "$tag" $extra &
  while [ "$(jobs -rp | wc -l)" -ge "$CONC" ]; do sleep 5; done
done
wait
say "ALL DONE"
