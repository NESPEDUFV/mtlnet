#!/usr/bin/env bash
# Tier B RE-AUDIT D1 — alpha-dominance test at AL (seed=42, 5 folds, H3-alt, --no-checkpoints).
# Two cells, both with the reg head's alpha frozen to 0 (disable alpha.log_T prior):
#   d1_design_b_a0   : --engine check2hgi_design_b
#   d1_canonical_a0  : --engine check2hgi   (matched alpha=0 control)
# Output dir is controlled by RESULTS_ROOT env var; the run lands at
#   $RESULTS_ROOT/{engine}/alabama/mtlnet_.../metrics/
# Detached megascript; writes DONE marker on completion.
set -u
cd /home/vitor.oliveira/PoiMtlNet
PY=.venv/bin/python
BASE=docs/results/substrate_protocol_cleanup/tier_b/reaudit_d1
mkdir -p "$BASE"
MARK="$BASE/DONE"
rm -f "$MARK"

# H3-alt small-state recipe (AL): constant scheduler, NO alternating/alpha-no-wd/min-best.
# Heads: cat=next_gru, reg=next_getnext_hard (alias next_stan_flow), alpha frozen=0.
common=(--task mtl --task-set check2hgi_next_region --state alabama --seed 42
        --epochs 50 --folds 5 --batch-size 2048 --model mtlnet_crossattn
        --mtl-loss static_weight --category-weight 0.75
        --scheduler constant --max-lr 3e-3
        --cat-head next_gru --reg-head next_getnext_hard
        --task-a-input-type checkin --task-b-input-type region
        --reg-head-param freeze_alpha=true --reg-head-param alpha_init=0.0
        --no-checkpoints)

run_cell () {
  local engine="$1"; local tag="$2"
  local cell="$BASE/$tag"
  mkdir -p "$cell"
  echo "[$(date -u +%H:%M:%S)] START $tag engine=$engine alpha=0" | tee -a "$cell/run.log"
  RESULTS_ROOT="$PWD/$cell" $PY scripts/train.py "${common[@]}" --engine "$engine" \
      --per-fold-transition-dir output/check2hgi/alabama \
      >> "$cell/run.log" 2>&1
  echo "[$(date -u +%H:%M:%S)] EXIT $tag rc=$?" | tee -a "$cell/run.log"
}

run_cell check2hgi_design_b d1_design_b_a0
run_cell check2hgi          d1_canonical_a0

echo "ALL_DONE $(date -u +%FT%TZ)" > "$MARK"
