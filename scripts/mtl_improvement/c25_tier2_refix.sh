#!/bin/bash
# C25 TIER-2 RE-RUN under the fix — does any architecture change the orderings (vs the
# class-WEIGHTED Tier-2 verdict) and/or close the residual FL reg gap (v14 base_a 71.55 vs
# (c) ceiling 73.31 = −1.8pp, NOT class-weighting, NOT wd)? FL, multi-seed {0,1,7,100},
# UNWEIGHTED real-joint (the C25 default). base_a (= c25_revalidate v14 FL, 71.55) is the
# zero-point and is NOT re-run here. Arms:
#   prior_off  : mtlnet_crossattn + next_getnext_hard, α=0 prior-OFF  → decompose the prior
#                (base_a is prior-ON; the (c) ceiling is prior-OFF — is the FL gap the prior?)
#   dual_gated : mtlnet_crossattn_dualtower gated (T2.1)              → does the dual-tower now help?
#   crossstitch: mtlnet_crossstitch + next_getnext_hard (T2.2)        → the only arm that didn't lose before
#   hardshare  : mtlnet + next_getnext_hard (T2.0)                    → hard-share anchor
# Compare reg disjoint vs base_a (71.55) + (c) ceiling (73.31). Orderings flip vs class-weighted?
#   Launch: CONC=2 setsid bash scripts/mtl_improvement/c25_tier2_refix.sh > /tmp/c25t2/run.log 2>&1 &
set -uo pipefail
REPO=/home/vitor.oliveira/PoiMtlNet; cd "$REPO"
PY=.venv/bin/python; V14=check2hgi_design_k_resln_mae_l0_1
EPOCHS=50; CONC=${CONC:-2}; SEEDS=(0 1 7 100); ST=${ST:-florida}
LOGDIR=/tmp/c25t2; mkdir -p "$LOGDIR"
MAN=scripts/mtl_improvement/c25_tier2_refix_manifest.tsv; [ -f "$MAN" ] || : > "$MAN"
export OMP_NUM_THREADS=$((32 / CONC))
ts(){ date '+%Y-%m-%d %H:%M:%S'; }; say(){ echo "[$(ts)] C25T2 $*"; }

# unweighted real-joint (new default), onecycle, KD-OFF.
COMMON="--task mtl --task-set check2hgi_next_region --engine $V14 \
  --epochs $EPOCHS --folds 5 --batch-size 2048 \
  --mtl-loss static_weight --category-weight 0.75 \
  --cat-head next_gru --task-a-input-type checkin --task-b-input-type region --log-t-kd-weight 0.0 \
  --scheduler onecycle --max-lr 3e-3 --cat-lr 1e-3 --reg-lr 3e-3 --shared-lr 1e-3 \
  --per-fold-transition-dir output/$V14/$ST --no-checkpoints"

# tag | model | reg_head | extra-head-params
# (T2.3 stretch: mmoe/cgc -lite added 2026-06-05; the 4 base arms already in the manifest are skipped)
ARMS="prior_off|mtlnet_crossattn|next_getnext_hard|--reg-head-param freeze_alpha=True --reg-head-param alpha_init=0.0
dual_gated|mtlnet_crossattn_dualtower|next_stan_flow_dualtower|--reg-head-param raw_embed_dim=64 --reg-head-param fusion_mode=gated
crossstitch|mtlnet_crossstitch|next_getnext_hard|
hardshare|mtlnet|next_getnext_hard|
mmoe|mtlnet_mmoe|next_getnext_hard|
cgc|mtlnet_cgc|next_getnext_hard|"

run(){ # tag model reg_head extra seed
  local tag=$1 model=$2 rh=$3 extra=$4 sd=$5 key="${tag}|s${sd}"
  grep -qF "$key	" "$MAN" && { say "skip $key"; return 0; }
  local log="$LOGDIR/${tag}_s${sd}.log"; say "start $key (model=$model)"
  $PY scripts/train.py $COMMON --state "$ST" --seed "$sd" \
      --model "$model" --reg-head "$rh" $extra > "$log" 2>&1 &
  local pid=$!; wait "$pid"; local rc=$?
  if [ $rc -eq 0 ]; then
    local rd; rd=$(ls -d results/$V14/$ST/mtlnet_*ep${EPOCHS}_*_${pid} 2>/dev/null | head -1)
    printf '%s\t%s\t%s\n' "$key" "$tag" "$rd" >>"$MAN"; say "done $key -> $rd"
  else say "FAIL $key (rc=$rc) — see $log"; fi
}

say "config: CONC=$CONC state=$ST seeds='${SEEDS[*]}' arms=prior_off,dual_gated,crossstitch,hardshare unweighted"
while IFS= read -r spec; do
  [ -z "$spec" ] && continue
  IFS='|' read -r tag model rh extra <<< "$spec"
  for sd in "${SEEDS[@]}"; do
    run "$tag" "$model" "$rh" "$extra" "$sd" &
    while [ "$(jobs -rp | wc -l)" -ge "$CONC" ]; do sleep 5; done
  done
done <<< "$ARMS"
wait
say "ALL DONE"
