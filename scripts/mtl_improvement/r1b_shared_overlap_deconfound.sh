#!/bin/bash
# R1b — DE-CONFOUND for R1 (advisor 2026-06-08). R1's "+4.89 overlap absorption" vs the OLD-regime
# "+0.50" confounds TWO changes: class-weighted->unweighted (C25) AND shared->private dual-tower.
# This isolates the tower: run the SHARED-backbone reg arm (mtlnet_crossattn + next_stan_flow,
# prior-OFF) under the SAME C25-unweighted onecycle recipe at AL seed42, overlap vs non-overlap.
#   If shared+unweighted MTL reg lift ~= +4.9 (like the tower) -> C25 is the absorber, NOT the tower.
#   If shared+unweighted MTL reg lift << tower's +4.89        -> the PRIVATE TOWER is the absorber.
# This is G minus the private tower (everything else identical). log_T inert (prior-OFF + KD-off).
#   CONC=1 setsid bash scripts/mtl_improvement/r1b_shared_overlap_deconfound.sh > /tmp/r1b/run.log 2>&1 &
set -uo pipefail
REPO=/home/vitor.oliveira/PoiMtlNet; cd "$REPO"; export PYTHONPATH=src
PY=.venv/bin/python; V14=check2hgi_design_k_resln_mae_l0_1; OVL=check2hgi_dk_ovl
ST=alabama; SD=42; EPOCHS=50
LOGDIR=/tmp/r1b; mkdir -p "$LOGDIR"
MAN=scripts/mtl_improvement/r1b_shared_manifest.tsv; [ -f "$MAN" ] || : > "$MAN"
export OMP_NUM_THREADS=24
ts(){ date '+%Y-%m-%d %H:%M:%S'; }; say(){ echo "[$(ts)] R1b $*"; }

# SHARED-backbone reg arm = base_a (mtlnet_crossattn) + next_stan_flow prior-OFF (no private tower)
shared_run(){ local regime=$1 engine=$2; local key="shared|${regime}"
  grep -qF "$key	" "$MAN" && { say "skip $key"; return 0; }
  local log="$LOGDIR/${key//|/_}.log"; say "start $key (engine=$engine)"
  $PY scripts/train.py --task mtl --task-set check2hgi_next_region --engine "$engine" \
      --state "$ST" --seed "$SD" --epochs "$EPOCHS" --folds 5 --batch-size 2048 \
      --mtl-loss static_weight --category-weight 0.75 \
      --cat-head next_gru --reg-head next_stan_flow \
      --reg-head-param freeze_alpha=True --reg-head-param alpha_init=0.0 \
      --task-a-input-type checkin --task-b-input-type region --log-t-kd-weight 0.0 \
      --scheduler onecycle --max-lr 3e-3 --cat-lr 1e-3 --reg-lr 3e-3 --shared-lr 1e-3 \
      --model mtlnet_crossattn \
      --per-fold-transition-dir "output/$V14/$ST" --no-checkpoints > "$log" 2>&1 &
  local pid=$!; wait "$pid"
  if [ $? -eq 0 ]; then
    local rd; rd=$(ls -d results/$engine/$ST/mtlnet_*ep${EPOCHS}_*_${pid} 2>/dev/null | head -1)
    [ -z "$rd" ] && rd=$(ls -dt results/$engine/$ST/mtlnet_*ep${EPOCHS}_* 2>/dev/null | head -1)
    printf '%s\tshared\t%s\n' "$key" "$rd" >>"$MAN"; say "done $key -> $rd"
  else say "FAIL $key — see $log"; return 1; fi
}

say "=== R1b shared-backbone (no private tower) overlap de-confound, AL seed42 ==="
shared_run nonoverlap "$V14"
shared_run overlap    "$OVL"
say "ALL DONE"
