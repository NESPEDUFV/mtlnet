#!/bin/bash
# R2 AL multi-seed — base + 5 AFTB configs at seeds {1,7,100} (seed0 in r2_aftb_manifest).
# Per-config paired Wilcoxon vs base. PID-suffix capture; --no-checkpoints.
set -uo pipefail
REPO=/home/vitor.oliveira/PoiMtlNet; cd "$REPO"; export PYTHONPATH=src
PY=.venv/bin/python; V14=check2hgi_design_k_resln_mae_l0_1; EPOCHS=50; CONC=${CONC:-2}; ST=alabama
LOGDIR=/tmp/r2_alms; mkdir -p "$LOGDIR"
MAN=scripts/mtl_frontier/r2_al_multiseed_manifest.tsv; : > "$MAN"
export OMP_NUM_THREADS=$((32 / CONC))
ts(){ date '+%Y-%m-%d %H:%M:%S'; }; say(){ echo "[$(ts)] R2ALMS $*"; }

run(){ local tag=$1 sd=$2 spec=$3
  local log="$LOGDIR/${tag}.log"; say "start $tag (seed=$sd spec='${spec:-NONE}')"
  local specflag=(); [ -n "$spec" ] && specflag=(--model-param "aftb_spec=$spec")
  $PY scripts/train.py --task mtl --canon none --task-set check2hgi_next_region \
      --engine "$V14" --state "$ST" --seed "$sd" --epochs "$EPOCHS" --folds 5 --batch-size 2048 \
      --no-reg-class-weights --no-cat-class-weights \
      --mtl-loss static_weight --category-weight 0.75 \
      --cat-head next_gru --reg-head next_stan_flow_dualtower \
      --reg-head-param raw_embed_dim=64 --reg-head-param fusion_mode=aux \
      --reg-head-param freeze_alpha=True --reg-head-param alpha_init=0.0 \
      --task-a-input-type checkin --task-b-input-type region --log-t-kd-weight 0.0 \
      --scheduler onecycle --max-lr 3e-3 --cat-lr 1e-3 --reg-lr 3e-3 --shared-lr 1e-3 \
      --model mtlnet_crossattn_dualtower "${specflag[@]}" \
      --per-fold-transition-dir "output/$V14/$ST" --no-checkpoints > "$log" 2>&1 &
  local pid=$!; wait "$pid"
  if [ $? -eq 0 ]; then
    local rd; rd=$(ls -d results/$V14/$ST/mtlnet_*ep${EPOCHS}_*_${pid} 2>/dev/null | head -1)
    [ -z "$rd" ] && rd="UNKNOWN_pid${pid}"
    printf '%s\t%s\t%s\t%s\n' "$tag" "$sd" "$spec" "$rd" >>"$MAN"; say "done $tag -> $rd"
  else say "FAIL $tag (see $log)"; fi
}

declare -A SPEC=( [base]="" [aftb_all]="ab+ba,ab+ba" [aftb_late]="none,ab+ba" \
  [aftb_early]="ab+ba,none" [reg_protect]="ab,ab" [cat_protect]="ba,ba" )
ORDER=(base aftb_all aftb_late aftb_early reg_protect cat_protect)

say "=== R2 AL multi-seed {1,7,100} × 6 configs, CONC=$CONC ==="
for sd in 1 7 100; do
  for cfg in "${ORDER[@]}"; do
    run "${cfg}_s${sd}" "$sd" "${SPEC[$cfg]}" & \
      while [ "$(jobs -rp|wc -l)" -ge "$CONC" ]; do sleep 8; done
  done
done
wait; say "ALL DONE -> $MAN"
