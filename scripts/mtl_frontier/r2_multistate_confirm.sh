#!/bin/bash
# R2 multi-state confirm of the best AFTB config aftb_late (none,ab+ba) vs base (G).
#   AZ + GE seed0 (does the AL cat lift appear at other small states?)
#   FL {1,7,100} (multi-seed confirm of the FL null)
# base FL seed0 + aftb_late FL seed0 already exist in r2_aftb_manifest.
set -uo pipefail
REPO=/home/vitor.oliveira/PoiMtlNet; cd "$REPO"; export PYTHONPATH=src
PY=.venv/bin/python; V14=check2hgi_design_k_resln_mae_l0_1; EPOCHS=50; CONC=${CONC:-2}
SPEC_LATE="none,ab+ba"
LOGDIR=/tmp/r2_ms; mkdir -p "$LOGDIR"
MAN=scripts/mtl_frontier/r2_multistate_manifest.tsv; : > "$MAN"
export OMP_NUM_THREADS=$((32 / CONC))
ts(){ date '+%Y-%m-%d %H:%M:%S'; }; say(){ echo "[$(ts)] R2MS $*"; }

run(){ local tag=$1 st=$2 sd=$3 spec=$4
  local log="$LOGDIR/${tag}.log"; say "start $tag (state=$st seed=$sd spec='${spec:-NONE}')"
  local specflag=(); [ -n "$spec" ] && specflag=(--model-param "aftb_spec=$spec")
  $PY scripts/train.py --task mtl --canon none --task-set check2hgi_next_region \
      --engine "$V14" --state "$st" --seed "$sd" --epochs "$EPOCHS" --folds 5 --batch-size 2048 \
      --no-reg-class-weights --no-cat-class-weights \
      --mtl-loss static_weight --category-weight 0.75 \
      --cat-head next_gru --reg-head next_stan_flow_dualtower \
      --reg-head-param raw_embed_dim=64 --reg-head-param fusion_mode=aux \
      --reg-head-param freeze_alpha=True --reg-head-param alpha_init=0.0 \
      --task-a-input-type checkin --task-b-input-type region --log-t-kd-weight 0.0 \
      --scheduler onecycle --max-lr 3e-3 --cat-lr 1e-3 --reg-lr 3e-3 --shared-lr 1e-3 \
      --model mtlnet_crossattn_dualtower "${specflag[@]}" \
      --per-fold-transition-dir "output/$V14/$st" --no-checkpoints > "$log" 2>&1 &
  local pid=$!; wait "$pid"
  if [ $? -eq 0 ]; then
    local rd; rd=$(ls -d results/$V14/$st/mtlnet_*ep${EPOCHS}_*_${pid} 2>/dev/null | head -1)
    [ -z "$rd" ] && rd="UNKNOWN_pid${pid}"
    printf '%s\t%s\t%s\t%s\t%s\n' "$tag" "$st" "$sd" "$spec" "$rd" >>"$MAN"; say "done $tag -> $rd"
  else say "FAIL $tag (see $log)"; fi
}

say "=== R2 multi-state confirm: aftb_late vs base. AZ/GE seed0 + FL {1,7,100}, CONC=$CONC ==="
# Small states first (fast): AZ + GE seed0
for st in arizona georgia; do
  run base_${st}_s0  $st 0 ""           & while [ "$(jobs -rp|wc -l)" -ge "$CONC" ]; do sleep 8; done
  run late_${st}_s0  $st 0 "$SPEC_LATE" & while [ "$(jobs -rp|wc -l)" -ge "$CONC" ]; do sleep 8; done
done
# FL multi-seed {1,7,100}
for sd in 1 7 100; do
  run base_florida_s${sd}  florida $sd ""           & while [ "$(jobs -rp|wc -l)" -ge "$CONC" ]; do sleep 8; done
  run late_florida_s${sd}  florida $sd "$SPEC_LATE" & while [ "$(jobs -rp|wc -l)" -ge "$CONC" ]; do sleep 8; done
done
wait; say "ALL DONE -> $MAN"
