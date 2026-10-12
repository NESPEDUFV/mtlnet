#!/bin/bash
# T2V.1 — multi-seed (c)/(d) STL ceilings {0,1,7,100} to SEED-MATCH G (CRITIQUE §3 G1, the #1 gate).
# The frozen (c)/(d) are seed=42 ONLY; G is {0,1,7,100} (disjoint seeds) → re-run the ceilings at
# G's seeds so every G−ceiling Δ is seed-matched. Configs = the FROZEN winners:
#   (c) reg = next_stan_flow α=0 (p1_region_head_ablation, v14 region-emb)   [α=0 wins reg everywhere]
#   (c) cat = next_gru + logit-adjust τ=0.5 (train.py --task next, the la05 repin winner)
#   (d) reg = max(v14-α0, HGI-α0); HGI region-emb is on disk ONLY at FL → (d) recomputed at FL only
#             (AL/AZ/GE HGI margin ≤0.7pp + substrate absent → (d) stays seed-42 there, flagged).
# STL runs (light) → CONC up. PID/JSON-tag capture. Launch:
#   CONC=3 setsid bash scripts/mtl_improvement/t2v1_ceilings_multiseed.sh > /tmp/t2v1/run.log 2>&1 &
set -uo pipefail
REPO=/home/vitor.oliveira/PoiMtlNet; cd "$REPO"; export PYTHONPATH=src
PY=.venv/bin/python; V14=check2hgi_design_k_resln_mae_l0_1
EPOCHS=50; CONC=${CONC:-3}; SEEDS=(0 1 7 100)
LOGDIR=/tmp/t2v1; mkdir -p "$LOGDIR"
MAN=scripts/mtl_improvement/t2v1_ceilings_manifest.tsv; [ -f "$MAN" ] || : > "$MAN"
export OMP_NUM_THREADS=$((32 / CONC))
ts(){ date '+%Y-%m-%d %H:%M:%S'; }; say(){ echo "[$(ts)] T2V1 $*"; }
A0="freeze_alpha=True alpha_init=0.0"

# (c)/(d) REG ceiling — p1 ablation, next_stan_flow α=0. eng ∈ {v14, hgi}.
reg_run(){ local st=$1 eng=$2 sd=$3; local key="creg|${eng}|${st}|s${sd}"
  grep -qF "$key	" "$MAN" && { say "skip $key"; return 0; }
  local tag="t2v1_creg_${eng}_${st}_s${sd}"; local log="$LOGDIR/${key//|/_}.log"; say "start $key"
  $PY scripts/p1_region_head_ablation.py --state "$st" --heads next_stan_flow \
      --input-type region --region-emb-source "$eng" --override-hparams $A0 \
      --folds 5 --epochs "$EPOCHS" --batch-size 2048 --seed "$sd" --target region --tag "$tag" \
      --per-fold-transition-dir "output/check2hgi/$st" > "$log" 2>&1 \
    && { printf '%s\tcreg\tdocs/results/P1/region_head_%s_region_5f_50ep_%s.json\n' "$key" "$st" "$tag" >>"$MAN"; say "done $key"; } \
    || say "FAIL $key — see $log"
}

# (c) CAT ceiling — train.py --task next, next_gru + logit-adjust τ=0.5 (la05).
cat_run(){ local st=$1 sd=$2; local key="ccat|${st}|s${sd}"
  grep -qF "$key	" "$MAN" && { say "skip $key"; return 0; }
  local log="$LOGDIR/${key//|/_}.log"; say "start $key"
  $PY scripts/train.py --task next --state "$st" --engine "$V14" --model next_gru \
      --seed "$sd" --epochs "$EPOCHS" --folds 5 --batch-size 2048 \
      --logit-adjust-tau 0.5 --no-checkpoints > "$log" 2>&1 &
  local pid=$!; wait "$pid"
  if [ $? -eq 0 ]; then
    local rd; rd=$(ls -d results/$V14/$st/next_*ep${EPOCHS}_*_${pid} 2>/dev/null | head -1)
    printf '%s\tccat\t%s\n' "$key" "$rd" >>"$MAN"; say "done $key -> $rd"
  else say "FAIL $key"; fi
}

say "config: CONC=$CONC seeds='${SEEDS[*]}' — (c)reg+(c)cat AL/AZ/GE/FL + (d)HGI-reg FL"
queue(){ # fn args...
  "$@" & while [ "$(jobs -rp | wc -l)" -ge "$CONC" ]; do sleep 5; done
}
for sd in "${SEEDS[@]}"; do
  for st in alabama arizona georgia florida; do
    queue reg_run "$st" "$V14" "$sd"
    queue cat_run "$st" "$sd"
  done
  queue reg_run florida hgi "$sd"     # (d) composite HGI arm — FL only (substrate on disk)
done
wait
say "ALL DONE"
