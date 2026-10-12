#!/bin/bash
# R5 — per-instance log_T-KD gating. Comparand = champion G + GLOBAL log_T-KD W=0.2
# (gate=none); variants redistribute that (batch-mean-fixed) weight by Markov-coverage
# of the sample's last-region log_T row (coverage_max = teacher max-prob; coverage_entropy
# = normalized 1-H). Mean-1 per batch → total KD budget == global-W (tests redistribution,
# not strength). Falsifier: gated ≤ global-W everywhere. AL+FL seed0 → multi-seed on a
# positive. Gate ≥0.3 either head (promote → STOP for user). --no-checkpoints.
set -uo pipefail
REPO=/home/vitor.oliveira/PoiMtlNet; cd "$REPO"; export PYTHONPATH=src
PY=.venv/bin/python; V14=check2hgi_design_k_resln_mae_l0_1; EPOCHS=50; CONC=${CONC:-2}
LOGDIR=/tmp/r5; mkdir -p "$LOGDIR"
MAN=scripts/mtl_frontier/r5_screen_manifest.tsv; : > "$MAN"
export OMP_NUM_THREADS=$((32 / CONC))
ts(){ date '+%Y-%m-%d %H:%M:%S'; }; say(){ echo "[$(ts)] R5 $*"; }

# run <tag> <state> <gate>   (gate=none = global-W baseline)
run(){ local tag=$1 st=$2 gate=$3
  local log="$LOGDIR/${tag}.log"; say "start $tag (st=$st gate=$gate)"
  $PY scripts/train.py --task mtl --canon none --task-set check2hgi_next_region \
      --engine "$V14" --state "$st" --seed 0 --epochs "$EPOCHS" --folds 5 --batch-size 2048 \
      --no-reg-class-weights --no-cat-class-weights \
      --mtl-loss static_weight --category-weight 0.75 \
      --cat-head next_gru --reg-head next_stan_flow_dualtower \
      --reg-head-param raw_embed_dim=64 --reg-head-param fusion_mode=aux \
      --reg-head-param freeze_alpha=True --reg-head-param alpha_init=0.0 \
      --task-a-input-type checkin --task-b-input-type region \
      --log-t-kd-weight 0.2 --log-t-kd-gate "$gate" \
      --scheduler onecycle --max-lr 3e-3 --cat-lr 1e-3 --reg-lr 3e-3 --shared-lr 1e-3 \
      --model mtlnet_crossattn_dualtower \
      --per-fold-transition-dir "output/$V14/$st" --no-checkpoints > "$log" 2>&1 &
  local pid=$!; wait "$pid"
  if [ $? -eq 0 ]; then
    local rd; rd=$(ls -d results/$V14/$st/mtlnet_*ep${EPOCHS}_*_${pid} 2>/dev/null | head -1)
    [ -z "$rd" ] && rd="UNKNOWN_pid${pid}"
    printf '%s\t%s\t%s\t%s\n' "$tag" "$st" "$gate" "$rd" >>"$MAN"; say "done $tag -> $rd"
  else say "FAIL $tag (see $log)"; fi
}

say "=== R5 per-instance KD gating screen, AL+FL seed0, CONC=$CONC ==="
for st in alabama florida; do
  run "base_${st}"     "$st" none             &  while [ "$(jobs -rp|wc -l)" -ge "$CONC" ]; do sleep 8; done
  run "covmax_${st}"   "$st" coverage_max     &  while [ "$(jobs -rp|wc -l)" -ge "$CONC" ]; do sleep 8; done
  run "coventr_${st}"  "$st" coverage_entropy &  while [ "$(jobs -rp|wc -l)" -ge "$CONC" ]; do sleep 8; done
done
wait; say "ALL DONE -> $MAN"
