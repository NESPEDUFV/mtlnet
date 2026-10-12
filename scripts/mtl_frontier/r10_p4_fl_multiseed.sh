#!/bin/bash
# A (R10 P4 measured close) — multi-seed the FL crosser P4 (intra-tower GRM, "in a tower":
# --reg-head-param priv_grm=True) vs matched champion G at FL {1,7,100} (seed0 already in
# r10_placement_manifest). P4 FL seed0 cat +0.324 is identical to the original R10 cross-attn
# +0.324 (washed to +0.085) → multi-seed to confirm it washes out (regime-bounded intra-task
# placement). --no-checkpoints.
set -uo pipefail
REPO=/home/vitor.oliveira/PoiMtlNet; cd "$REPO"; export PYTHONPATH=src
PY=.venv/bin/python; V14=check2hgi_design_k_resln_mae_l0_1; EPOCHS=50; CONC=${CONC:-2}
ST=florida; SEEDS=(1 7 100)
LOGDIR=/tmp/r10p4ms; mkdir -p "$LOGDIR"
MAN=scripts/mtl_frontier/r10_p4_fl_multiseed_manifest.tsv; : > "$MAN"
export OMP_NUM_THREADS=$((32 / CONC))
ts(){ date '+%Y-%m-%d %H:%M:%S'; }; say(){ echo "[$(ts)] P4MS $*"; }

run(){ local tag=$1 seed=$2; shift 2
  local log="$LOGDIR/${tag}_s${seed}.log"; say "start $tag s$seed extra=[$*]"
  $PY scripts/train.py --task mtl --canon none --task-set check2hgi_next_region \
      --engine "$V14" --state "$ST" --seed "$seed" --epochs "$EPOCHS" --folds 5 --batch-size 2048 \
      --no-reg-class-weights --no-cat-class-weights --mtl-loss static_weight --category-weight 0.75 \
      --cat-head next_gru --reg-head next_stan_flow_dualtower \
      --reg-head-param raw_embed_dim=64 --reg-head-param fusion_mode=aux \
      --reg-head-param freeze_alpha=True --reg-head-param alpha_init=0.0 "$@" \
      --task-a-input-type checkin --task-b-input-type region --log-t-kd-weight 0.0 \
      --scheduler onecycle --max-lr 3e-3 --cat-lr 1e-3 --reg-lr 3e-3 --shared-lr 1e-3 \
      --model mtlnet_crossattn_dualtower \
      --per-fold-transition-dir "output/$V14/$ST" --no-checkpoints > "$log" 2>&1 &
  local pid=$!; wait "$pid"
  if [ $? -eq 0 ]; then
    local rd; rd=$(ls -d results/$V14/$ST/mtlnet_*ep${EPOCHS}_*_${pid} 2>/dev/null | head -1)
    [ -z "$rd" ] && rd="UNKNOWN_pid${pid}"
    printf '%s\t%s\t%s\t%s\n' "$tag" "$ST" "$seed" "$rd" >>"$MAN"; say "done $tag s$seed -> $rd"
  else say "FAIL $tag s$seed (see $log)"; fi
}

say "=== R10 P4 FL multi-seed {1,7,100} (+seed0 reused), CONC=$CONC ==="
for seed in "${SEEDS[@]}"; do
  run "base"       "$seed" &  while [ "$(jobs -rp|wc -l)" -ge "$CONC" ]; do sleep 8; done
  run "p4_privgrm" "$seed" --reg-head-param priv_grm=True &  while [ "$(jobs -rp|wc -l)" -ge "$CONC" ]; do sleep 8; done
done
wait; say "ALL DONE -> $MAN"
