#!/bin/bash
# T2V.5/6/7 — flag-controllable winner-hypertuning on G (FL seed0, post-C25). Anchor: G
# reg 73.57 / cat 73.16. Arms:
#   T2V.7 (⭐ cat lever): G + logit-adjust τ∈{0.5,1.0} on the cat head (the (c) ceiling used la0.5;
#          G's cat is plain unweighted → does la lift it further?)
#   T2V.5 (reg-tower internals): G + priv d_model=256 ; G + priv_num_heads=8 (is the full STAN
#          over/under-provisioned? — accuracy + efficiency). [STAN→other-head swap needs new code.]
#   T2V.6 (optimizer/balancer): G + FAMO (O(1) gradient balancer — does it lift G or just confirm
#          static_weight is fine?). [per-task precision fp32-reg/fp16-cat needs code; full-fp32 already
#          tested = +0.13reg/−1.11cat trade.]
# CONC=2 (some arms heavier). PID capture. Launch:
#   CONC=2 setsid bash scripts/mtl_improvement/t2v567_hypertune.sh > /tmp/t2v567/run.log 2>&1 &
set -uo pipefail
REPO=/home/vitor.oliveira/PoiMtlNet; cd "$REPO"; PY=.venv/bin/python
V14=check2hgi_design_k_resln_mae_l0_1; ST=florida; SD=0; EPOCHS=50; CONC=${CONC:-2}
LOGDIR=/tmp/t2v567; mkdir -p "$LOGDIR"
MAN=scripts/mtl_improvement/t2v567_manifest.tsv; [ -f "$MAN" ] || : > "$MAN"
export OMP_NUM_THREADS=$((32 / CONC))
ts(){ date '+%Y-%m-%d %H:%M:%S'; }; say(){ echo "[$(ts)] T2V567 $*"; }

# G base recipe (prior-OFF aux dual-tower). $LOSS lets the FAMO arm override --mtl-loss.
base(){ echo "--task mtl --task-set check2hgi_next_region --engine $V14 --state $ST --seed $SD \
  --epochs $EPOCHS --folds 5 --batch-size 2048 \
  --cat-head next_gru --reg-head next_stan_flow_dualtower \
  --reg-head-param raw_embed_dim=64 --reg-head-param fusion_mode=aux \
  --reg-head-param freeze_alpha=True --reg-head-param alpha_init=0.0 \
  --task-a-input-type checkin --task-b-input-type region --log-t-kd-weight 0.0 \
  --scheduler onecycle --max-lr 3e-3 --cat-lr 1e-3 --reg-lr 3e-3 --shared-lr 1e-3 \
  --model mtlnet_crossattn_dualtower --per-fold-transition-dir output/$V14/$ST --no-checkpoints"; }

run(){ local tag=$1; shift; local extra="$*"; local key="${tag}|s${SD}"
  grep -qF "$key	" "$MAN" && { say "skip $key"; return 0; }
  local log="$LOGDIR/${tag}.log"; say "start $key"
  $PY scripts/train.py $(base) $extra > "$log" 2>&1 &
  local pid=$!; wait "$pid"
  if [ $? -eq 0 ]; then
    local rd; rd=$(ls -d results/$V14/$ST/mtlnet_*ep${EPOCHS}_*_${pid} 2>/dev/null | head -1)
    printf '%s\t%s\t%s\n' "$key" "$tag" "$rd" >>"$MAN"; say "done $key -> $rd"
  else say "FAIL $key — see $log"; fi
}

# tag | extra args
ARMS=(
  "t2v7_la05|--mtl-loss static_weight --category-weight 0.75 --logit-adjust-tau 0.5"
  "t2v7_la10|--mtl-loss static_weight --category-weight 0.75 --logit-adjust-tau 1.0"
  "t2v5_dmodel256|--mtl-loss static_weight --category-weight 0.75 --reg-head-param d_model=256"
  "t2v5_heads8|--mtl-loss static_weight --category-weight 0.75 --reg-head-param priv_num_heads=8"
  "t2v6_famo|--mtl-loss famo"
)
say "config: CONC=$CONC FL seed0 — T2V.5/6/7 flag-hypertune (5 arms)"
for spec in "${ARMS[@]}"; do
  tag=${spec%%|*}; extra=${spec#*|}
  run "$tag" $extra &
  while [ "$(jobs -rp | wc -l)" -ge "$CONC" ]; do sleep 5; done
done
wait
say "ALL DONE"
