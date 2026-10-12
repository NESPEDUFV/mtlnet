#!/bin/bash
# T2V.4 — alt-arch FAIR re-rank (CRITIQUE §6.4–6.6, the one dominant P1 test). The pre-C25
# "architecture-capacity falsified 5 ways" rests on alt-archs ranked UNDER the class-weighting
# confound AND at a single un-swept category-weight (Xin NeurIPS'22: per-arch loss-weight tuning
# dominates → comparing archs at one fixed scalarization manufactures illusory rankings). So:
# re-rank the standalone alternatives POST-C25 (unweighted), each at its OWN best category-weight
# {0.5,0.65,0.75}, 1-seed FL → promote any that ties/beats G (73.57) to multi-seed.
# Archs: hard-share (mtlnet), CrossStitch, MMoE-lite, CGC-lite — each with next_getnext_hard reg.
# Anchors: G 73.57 (dual-tower aux), base_a 71.55. Faithful learned-gate CGC ONLY if a -lite surprises.
# Self-sequences behind any running train.py (WAIT poll). Launch:
#   CONC=3 setsid bash scripts/mtl_improvement/t2v4_altarch_rerank.sh > /tmp/t2v4/run.log 2>&1 &
set -uo pipefail
REPO=/home/vitor.oliveira/PoiMtlNet; cd "$REPO"; PY=.venv/bin/python
V14=check2hgi_design_k_resln_mae_l0_1; ST=florida; SD=0; EPOCHS=50; CONC=${CONC:-3}
LOGDIR=/tmp/t2v4; mkdir -p "$LOGDIR"
MAN=scripts/mtl_improvement/t2v4_manifest.tsv; [ -f "$MAN" ] || : > "$MAN"
export OMP_NUM_THREADS=$((32 / CONC))
ts(){ date '+%Y-%m-%d %H:%M:%S'; }; say(){ echo "[$(ts)] T2V4 $*"; }

# wait for the GPU to free (t2v23 runs finish first)
say "waiting for GPU to free..."
while true; do p=$(pgrep -fc 'scripts/[t]rain.py'); [ "${p:-0}" -gt 0 ] || break; sleep 60; done
say "GPU free — starting alt-arch re-rank"

COMMON="--task mtl --task-set check2hgi_next_region --engine $V14 --state $ST --seed $SD \
  --epochs $EPOCHS --folds 5 --batch-size 2048 --mtl-loss static_weight \
  --cat-head next_gru --reg-head next_getnext_hard \
  --task-a-input-type checkin --task-b-input-type region --log-t-kd-weight 0.0 \
  --scheduler onecycle --max-lr 3e-3 --cat-lr 1e-3 --reg-lr 3e-3 --shared-lr 1e-3 \
  --per-fold-transition-dir output/$V14/$ST --no-checkpoints"

ARCHS="hardshare:mtlnet crossstitch:mtlnet_crossstitch mmoe:mtlnet_mmoe cgc:mtlnet_cgc"
CATW="0.50 0.65 0.75"

run(){ local arch=$1 model=$2 cw=$3; local key="${arch}|cw${cw}"
  grep -qF "$key	" "$MAN" && { say "skip $key"; return 0; }
  local log="$LOGDIR/${arch}_cw${cw}.log"; say "start $key (model=$model)"
  $PY scripts/train.py $COMMON --model "$model" --category-weight "$cw" > "$log" 2>&1 &
  local pid=$!; wait "$pid"
  if [ $? -eq 0 ]; then
    local rd; rd=$(ls -d results/$V14/$ST/mtlnet_*ep${EPOCHS}_*_${pid} 2>/dev/null | head -1)
    printf '%s\t%s\t%s\n' "$key" "$arch" "$rd" >>"$MAN"; say "done $key -> $rd"
  else say "FAIL $key"; fi
}

say "config: CONC=$CONC FL seed0 — archs={hardshare,crossstitch,mmoe,cgc} x catw={$CATW} post-C25"
for spec in $ARCHS; do
  arch=${spec%%:*}; model=${spec##*:}
  for cw in $CATW; do
    run "$arch" "$model" "$cw" &
    while [ "$(jobs -rp | wc -l)" -ge "$CONC" ]; do sleep 5; done
  done
done
wait
say "ALL DONE"
