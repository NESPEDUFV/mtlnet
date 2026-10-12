#!/bin/bash
# R2 (mtl_frontier) — STEM-AFTB per-layer/direction gating sweep over champion G.
# Baseline = pure champion G (v16, KD-OFF); variants add --model-param aftb_spec=<spec>
# on the 2-block cross-attn. Gate: ≥0.3pp EITHER head over G, AL+FL seed0 → multi-seed.
#   ab = cat reads reg forward-only (detach reg K/V in cross_ab → reg pathway gets no cat grad)
#   ba = reg reads cat forward-only (detach cat K/V in cross_ba → cat pathway gets no reg grad)
# Configs (2 blocks): base | aftb_all(ab+ba,ab+ba) | aftb_late(none,ab+ba) |
#   aftb_early(ab+ba,none) | reg_protect(ab,ab) | cat_protect(ba,ba)
set -uo pipefail
REPO=/home/vitor.oliveira/PoiMtlNet; cd "$REPO"; export PYTHONPATH=src
PY=.venv/bin/python; V14=check2hgi_design_k_resln_mae_l0_1; EPOCHS=50; CONC=${CONC:-2}
LOGDIR=/tmp/r2_aftb; mkdir -p "$LOGDIR"
MAN=scripts/mtl_frontier/r2_aftb_manifest.tsv; : > "$MAN"
export OMP_NUM_THREADS=$((32 / CONC))
ts(){ date '+%Y-%m-%d %H:%M:%S'; }; say(){ echo "[$(ts)] R2 $*"; }

# args: tag state spec("" = baseline G)
run(){ local tag=$1 st=$2 spec=$3
  local log="$LOGDIR/${tag}.log"; say "start $tag (state=$st spec='${spec:-NONE}')"
  local specflag=(); [ -n "$spec" ] && specflag=(--model-param "aftb_spec=$spec")
  $PY scripts/train.py --task mtl --canon none --task-set check2hgi_next_region \
      --engine "$V14" --state "$st" --seed 0 --epochs "$EPOCHS" --folds 5 --batch-size 2048 \
      --no-reg-class-weights --no-cat-class-weights \
      --mtl-loss static_weight --category-weight 0.75 \
      --cat-head next_gru --reg-head next_stan_flow_dualtower \
      --reg-head-param raw_embed_dim=64 --reg-head-param fusion_mode=aux \
      --reg-head-param freeze_alpha=True --reg-head-param alpha_init=0.0 \
      --task-a-input-type checkin --task-b-input-type region \
      --log-t-kd-weight 0.0 \
      --scheduler onecycle --max-lr 3e-3 --cat-lr 1e-3 --reg-lr 3e-3 --shared-lr 1e-3 \
      --model mtlnet_crossattn_dualtower "${specflag[@]}" \
      --per-fold-transition-dir "output/$V14/$st" --no-checkpoints > "$log" 2>&1 &
  local pid=$!; wait "$pid"
  if [ $? -eq 0 ]; then
    local rd; rd=$(ls -d results/$V14/$st/mtlnet_*ep${EPOCHS}_*_${pid} 2>/dev/null | head -1)
    [ -z "$rd" ] && rd="UNKNOWN_pid${pid}"
    printf '%s\t%s\t%s\t%s\n' "$tag" "$st" "$spec" "$rd" >>"$MAN"; say "done $tag -> $rd"
  else say "FAIL $tag (see $log)"; fi
}

declare -A SPEC=( [base]="" [aftb_all]="ab+ba,ab+ba" [aftb_late]="none,ab+ba" \
  [aftb_early]="ab+ba,none" [reg_protect]="ab,ab" [cat_protect]="ba,ba" )
ORDER=(base aftb_all aftb_late aftb_early reg_protect cat_protect)

say "=== R2 AFTB sweep, AL then FL, seed0, CONC=$CONC ==="
for st in alabama florida; do
  for cfg in "${ORDER[@]}"; do
    run "${cfg}_${st}" "$st" "${SPEC[$cfg]}" & \
      while [ "$(jobs -rp|wc -l)" -ge "$CONC" ]; do sleep 8; done
  done
done
wait; say "ALL DONE -> $MAN"
