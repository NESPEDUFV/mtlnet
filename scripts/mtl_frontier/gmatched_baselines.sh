#!/bin/bash
# Audit fix (user-flagged seed0 artifact): fresh MATCHED champion-G baselines with
# REPLICATES, on the CURRENT code, to (a) give same-code matched baselines for the
# conditional-coupling re-eval and (b) measure the run-to-run non-determinism floor
# (G replicate A vs B per seed). FL {0,1,7,100} × 2 replicates = 8 runs (FL = the
# only state tight enough, ~0.11 cat noise, for a real effect to survive).
set -uo pipefail
REPO=/home/vitor.oliveira/PoiMtlNet; cd "$REPO"; export PYTHONPATH=src
PY=.venv/bin/python; V14=check2hgi_design_k_resln_mae_l0_1; ST=florida; CONC=${CONC:-2}
LOGDIR=/tmp/gmatch; mkdir -p "$LOGDIR"
MAN=scripts/mtl_frontier/gmatched_manifest.tsv; : > "$MAN"
export OMP_NUM_THREADS=$((32 / CONC))
ts(){ date '+%Y-%m-%d %H:%M:%S'; }; say(){ echo "[$(ts)] GM $*"; }
run(){ local rep=$1 sd=$2; local tag="g_${ST}_s${sd}_r${rep}"; local log="$LOGDIR/${tag}.log"
  say "start $tag"
  $PY scripts/train.py --task mtl --canon none --task-set check2hgi_next_region \
    --engine "$V14" --state "$ST" --seed "$sd" --epochs 50 --folds 5 --batch-size 2048 \
    --no-reg-class-weights --no-cat-class-weights --mtl-loss static_weight --category-weight 0.75 \
    --cat-head next_gru --reg-head next_stan_flow_dualtower \
    --reg-head-param raw_embed_dim=64 --reg-head-param fusion_mode=aux \
    --reg-head-param freeze_alpha=True --reg-head-param alpha_init=0.0 \
    --task-a-input-type checkin --task-b-input-type region --log-t-kd-weight 0.0 \
    --scheduler onecycle --max-lr 3e-3 --cat-lr 1e-3 --reg-lr 3e-3 --shared-lr 1e-3 \
    --model mtlnet_crossattn_dualtower \
    --per-fold-transition-dir "output/$V14/$ST" --no-checkpoints > "$log" 2>&1 &
  local pid=$!; wait "$pid"
  local rd; rd=$(ls -d results/$V14/$ST/mtlnet_*ep50_*_${pid} 2>/dev/null | head -1)
  printf '%s\t%s\t%s\t%s\n' "$tag" "$sd" "$rep" "$rd" >>"$MAN"; say "done $tag -> $rd"
}
say "=== fresh matched champion-G FL {0,1,7,100} × 2 replicates, CONC=$CONC ==="
for rep in a b; do for sd in 0 1 7 100; do
  run "$rep" "$sd" & while [ "$(jobs -rp|wc -l)" -ge "$CONC" ]; do sleep 8; done
done; done
wait; say "ALL DONE -> $MAN"
