#!/bin/bash
# R7 — merge-vs-joint (ZipIt!/SIMO frontier). Train two independent single-task
# specialists in the champion-G dual-tower arch (cat-only cw=1.0, reg-only cw=0.0),
# FL seed0. The ENSEMBLE (cat-specialist's cat + reg-specialist's reg) is the *best-case*
# merge and a rigorous UPPER bound on any weight-merge (sharing weights can only constrain
# per-task performance). If even the ensemble loses to the JOINT champion G, no merge can
# match joint training. Tangent-space theory (Ortiz-Jimenez NeurIPS'23): from-scratch
# specialists don't share a basin → merge < joint. Expected: ensemble trades cat for reg
# and loses net (G's +2.6..4.1pp cat lift from joint trunk co-training is unrecoverable).
# --no-checkpoints (the ensemble bound needs only per-fold val metrics).
set -uo pipefail
REPO=/home/vitor.oliveira/PoiMtlNet; cd "$REPO"; export PYTHONPATH=src
PY=.venv/bin/python; V14=check2hgi_design_k_resln_mae_l0_1; EPOCHS=50; CONC=${CONC:-2}
ST=${ST:-florida}
LOGDIR=/tmp/r7; mkdir -p "$LOGDIR"
MAN=scripts/mtl_frontier/r7_specialists_manifest.tsv; : > "$MAN"
export OMP_NUM_THREADS=$((32 / CONC))
ts(){ date '+%Y-%m-%d %H:%M:%S'; }; say(){ echo "[$(ts)] R7 $*"; }

# run <tag> <category_weight>
run(){ local tag=$1 cw=$2
  local log="$LOGDIR/${tag}.log"; say "start $tag (st=$ST cw=$cw)"
  $PY scripts/train.py --task mtl --canon none --task-set check2hgi_next_region \
      --engine "$V14" --state "$ST" --seed 0 --epochs "$EPOCHS" --folds 5 --batch-size 2048 \
      --no-reg-class-weights --no-cat-class-weights \
      --mtl-loss static_weight --category-weight "$cw" \
      --cat-head next_gru --reg-head next_stan_flow_dualtower \
      --reg-head-param raw_embed_dim=64 --reg-head-param fusion_mode=aux \
      --reg-head-param freeze_alpha=True --reg-head-param alpha_init=0.0 \
      --task-a-input-type checkin --task-b-input-type region --log-t-kd-weight 0.0 \
      --scheduler onecycle --max-lr 3e-3 --cat-lr 1e-3 --reg-lr 3e-3 --shared-lr 1e-3 \
      --model mtlnet_crossattn_dualtower \
      --per-fold-transition-dir "output/$V14/$ST" --no-checkpoints > "$log" 2>&1 &
  local pid=$!; wait "$pid"
  if [ $? -eq 0 ]; then
    local rd; rd=$(ls -d results/$V14/$ST/mtlnet_*ep${EPOCHS}_*_${pid} 2>/dev/null | head -1)
    [ -z "$rd" ] && rd="UNKNOWN_pid${pid}"
    printf '%s\t%s\t%s\t%s\n' "$tag" "$ST" "$cw" "$rd" >>"$MAN"; say "done $tag -> $rd"
  else say "FAIL $tag (see $log)"; fi
}
say "=== R7 specialists ($ST seed0): cat-only cw=1.0, reg-only cw=0.0, CONC=$CONC ==="
run cat_specialist 1.0 & while [ "$(jobs -rp|wc -l)" -ge "$CONC" ]; do sleep 8; done
run reg_specialist 0.0 & while [ "$(jobs -rp|wc -l)" -ge "$CONC" ]; do sleep 8; done
wait; say "ALL DONE -> $MAN"
