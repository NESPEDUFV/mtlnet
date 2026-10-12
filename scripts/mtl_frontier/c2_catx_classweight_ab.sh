#!/bin/bash
# B (C2 memo evidence) — controlled class-weighting A/B at the paper's HEADLINE states CA + TX,
# on the paper's OWN config (v11 GCN substrate, B9 recipe, seed=42), to substantiate that
# "~half the −7…−17pp next-region cost is the C25 class-weighting confound" BEYOND FL (where
# the FL A/B already showed −6.71→−3.56, gap halved). Each state runs WEIGHTED vs UNWEIGHTED
# reg/cat CE — byte-identical except the class-weight flags (the clean one-knob comparand).
# The per-fold DELTA (unweighted − weighted) is the confound's reg recovery. seed=42 (the only
# leak-clean per-fold log_T built for CA/TX); 5 folds. --no-checkpoints.
# NOTE: this is GCN/v11 (paper-canon) territory — it does NOT touch champion G (v14). It measures
# the confound share at CA/TX to back the C2 reframing; full reg-PARITY at CA/TX still needs the
# v14 substrate (closing_data).
set -uo pipefail
REPO=/home/vitor.oliveira/PoiMtlNet; cd "$REPO"; export PYTHONPATH=src
PY=.venv/bin/python; ENG=check2hgi; EPOCHS=50; CONC=${CONC:-2}; SEED=42; BS=${BS:-2048}
# NOTE: CA/TX are the largest states (~4.7k/8.5k region logits); the B9 recipe OOMs the
# A40 at bs2048 even CONC=1. Run BS=512 CONC=1 — the confound A/B DELTA (weighted−unweighted
# reg, internally matched at the same BS) is batch-robust (the class-weighting effect is a
# per-fold/per-epoch loss-objective shift, present at any batch); only the absolute reg
# differs from the v11 bs2048 canon (noted in the C2 proposal).
LOGDIR=/tmp/c2ab; mkdir -p "$LOGDIR"
MAN=scripts/mtl_frontier/c2_catx_ab_manifest.tsv; : > "$MAN"
export OMP_NUM_THREADS=$((32 / CONC))
ts(){ date '+%Y-%m-%d %H:%M:%S'; }; say(){ echo "[$(ts)] C2AB $*"; }

# §0.1 paper-canon B9 recipe (large-state), KD-OFF for v11; arm = class-weighting on/off.
run(){ local st=$1 arm=$2   # arm = weighted | unweighted
  local cw_flags
  if [ "$arm" = "weighted" ]; then cw_flags="--reg-class-weights --cat-class-weights"
  else cw_flags="--no-reg-class-weights --no-cat-class-weights"; fi
  local tag="${st}_${arm}"; local log="$LOGDIR/${tag}.log"; say "start $tag"
  $PY scripts/train.py --task mtl --task-set check2hgi_next_region --engine "$ENG" \
      --state "$st" --seed "$SEED" --epochs "$EPOCHS" --folds 5 --batch-size "$BS" \
      --model mtlnet_crossattn \
      --mtl-loss static_weight --category-weight 0.75 \
      --scheduler cosine --max-lr 3e-3 --cat-lr 1e-3 --reg-lr 3e-3 --shared-lr 1e-3 \
      --alternating-optimizer-step --alpha-no-weight-decay --min-best-epoch 5 \
      --cat-head next_gru --reg-head next_getnext_hard \
      --task-a-input-type checkin --task-b-input-type region --log-t-kd-weight 0.0 \
      $cw_flags \
      --per-fold-transition-dir "output/$ENG/$st" --no-checkpoints > "$log" 2>&1 &
  local pid=$!; wait "$pid"
  if [ $? -eq 0 ]; then
    local rd; rd=$(ls -d results/$ENG/$st/mtlnet_*ep${EPOCHS}_*_${pid} 2>/dev/null | head -1)
    [ -z "$rd" ] && rd="UNKNOWN_pid${pid}"
    printf '%s\t%s\t%s\t%s\n' "$tag" "$st" "$arm" "$rd" >>"$MAN"; say "done $tag -> $rd"
  else say "FAIL $tag (see $log)"; fi
}

say "=== C2 class-weighting A/B at CA+TX (GCN/B9, seed42), CONC=$CONC ==="
for st in california texas; do
  run "$st" weighted   & while [ "$(jobs -rp|wc -l)" -ge "$CONC" ]; do sleep 8; done
  run "$st" unweighted & while [ "$(jobs -rp|wc -l)" -ge "$CONC" ]; do sleep 8; done
done
wait; say "ALL DONE -> $MAN"
