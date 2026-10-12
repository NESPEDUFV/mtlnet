#!/bin/bash
# R2 (Tier 3) — dual-substrate routing HGI->reg, FL pilot. Does HGI's documented +0.36pp STL
# reg edge over v14 SURVIVE the joint dynamics under champion G? Uses the REGION_EMB_ENGINE
# env-var hook (src/data/folds.py:980): the reg PRIVATE tower consumes HGI region-emb while
# cat (task_a) + the shared aux pathway stay on v14. Inference-time swap, no rebuild (HGI
# region_embeddings.parquet on disk at FL, 64-dim, matches the dual-tower raw_embed_dim=64).
# Control = G-v14 FL from R0 (72.97 +/- 0.06 full top10_acc). Score matched-metric.
#   CONC=2 setsid bash scripts/mtl_improvement/r2_dual_substrate_routing.sh > /tmp/r2/run.log 2>&1 &
set -uo pipefail
REPO=/home/vitor.oliveira/PoiMtlNet; cd "$REPO"; export PYTHONPATH=src
PY=.venv/bin/python; V14=check2hgi_design_k_resln_mae_l0_1; ST=florida; EPOCHS=50
SEEDS=(0 1 7 100); CONC=${CONC:-2}
LOGDIR=/tmp/r2; mkdir -p "$LOGDIR"
MAN=scripts/mtl_improvement/r2_routing_manifest.tsv; [ -f "$MAN" ] || : > "$MAN"
export OMP_NUM_THREADS=$((32 / CONC))
export REGION_EMB_ENGINE=hgi   # <-- the routing hook: reg tower consumes HGI region-emb
ts(){ date '+%Y-%m-%d %H:%M:%S'; }; say(){ echo "[$(ts)] R2 $*"; }

g_hgi_run(){ local sd=$1; local key="g_hgi|s${sd}"
  grep -qF "$key	" "$MAN" && { say "skip $key"; return 0; }
  local log="$LOGDIR/${key//|/_}.log"; say "start $key (REGION_EMB_ENGINE=$REGION_EMB_ENGINE)"
  $PY scripts/train.py --task mtl --task-set check2hgi_next_region --engine "$V14" \
      --state "$ST" --seed "$sd" --epochs "$EPOCHS" --folds 5 --batch-size 2048 \
      --mtl-loss static_weight --category-weight 0.75 \
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
    [ -z "$rd" ] && rd=$(ls -dt results/$V14/$ST/mtlnet_*ep${EPOCHS}_* 2>/dev/null | head -1)
    printf '%s\tg_hgi\t%s\n' "$key" "$rd" >>"$MAN"; say "done $key -> $rd"
  else say "FAIL $key — see $log"; fi
}

say "=== R2 HGI->reg routing under G, FL {${SEEDS[*]}} CONC=$CONC ==="
for sd in "${SEEDS[@]}"; do
  g_hgi_run "$sd" & while [ "$(jobs -rp | wc -l)" -ge "$CONC" ]; do sleep 10; done
done
wait
say "ALL DONE"
