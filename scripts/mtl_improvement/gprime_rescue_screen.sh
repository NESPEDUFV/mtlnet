#!/bin/bash
# G' SMALL-STATE RESCUE SCREEN (1-seed, AL + FL).
# Advisor finding: G' catpriv cat head UNDERFITS small-state 7-class category
# (AL train-F1 caps at 0.45 vs the GRU head's 0.98) — over-regularized
# (priv_dropout=0.3) + a GRU-tuned LR schedule. NOT overfitting. So it may be
# RESCUABLE by lowering regularization / softening the schedule / shrinking the tower.
# Test the top levers at seed 0 on AL (worst crater, train-F1 0.45) + FL (must keep +1.61).
# Target: AL cat back to >= G (52.91) WITHOUT losing FL's gain (74.77).
#   CONC=2 setsid bash scripts/mtl_improvement/gprime_rescue_screen.sh > /tmp/gprs/run.log 2>&1 &
set -uo pipefail
REPO=/home/vitor.oliveira/PoiMtlNet; cd "$REPO"; PY=.venv/bin/python
V14=check2hgi_design_k_resln_mae_l0_1; EPOCHS=50; CONC=${CONC:-2}; SEED=0
LOGDIR=/tmp/gprs; mkdir -p "$LOGDIR"
MAN=scripts/mtl_improvement/gprime_rescue_manifest.tsv; [ -f "$MAN" ] || : > "$MAN"
export OMP_NUM_THREADS=$((32 / CONC))
ts(){ date '+%Y-%m-%d %H:%M:%S'; }; say(){ echo "[$(ts)] GPRS $*"; }
# reg head (unchanged from G' / G champion reg path)
DT="--reg-head-param raw_embed_dim=64 --reg-head-param fusion_mode=aux --reg-head-param freeze_alpha=True --reg-head-param alpha_init=0.0"
# cat head base aux+prior-OFF params (lever overrides appended per-arm)
CT_BASE="--cat-head-param raw_embed_dim=64 --cat-head-param fusion_mode=aux --cat-head-param freeze_alpha=True --cat-head-param alpha_init=0.0"

# arms: name | extra cat-head-params | cat-lr override (empty=1e-3 default)
# L0 base (reference) ; L1 priv_dropout 0.1 ; L2 cat-lr 3e-4 ; L3 small tower ; L12 combo ; L13 dropout+small
run_arm(){
  local st=$1 arm=$2 ; local key="${arm}|${st}|s${SEED}"
  grep -qF "$key	" "$MAN" && { say "skip $key"; return 0; }
  local CT="$CT_BASE" CATLR="1e-3"
  case "$arm" in
    L0_base)       ;;
    L1_drop01)     CT="$CT --cat-head-param priv_dropout=0.1" ;;
    L2_catlr3e4)   CATLR="3e-4" ;;
    L3_small)      CT="$CT --cat-head-param d_model=64 --cat-head-param priv_num_heads=2" ;;
    L12_drop_lr)   CT="$CT --cat-head-param priv_dropout=0.1"; CATLR="3e-4" ;;
    L13_drop_small) CT="$CT --cat-head-param priv_dropout=0.1 --cat-head-param d_model=64 --cat-head-param priv_num_heads=2" ;;
    *) say "unknown arm $arm"; return 1 ;;
  esac
  local log="$LOGDIR/${arm}_${st}.log"; say "start $key (cat-lr=$CATLR)"
  $PY scripts/train.py --task mtl --task-set check2hgi_next_region --engine $V14 --state "$st" --seed "$SEED" \
      --epochs $EPOCHS --folds 5 --batch-size 2048 --mtl-loss static_weight --category-weight 0.75 \
      --model mtlnet_crossattn_dualtower_catpriv \
      --cat-head next_stan_flow_dualtower $CT --reg-head next_stan_flow_dualtower $DT \
      --task-a-input-type checkin --task-b-input-type region --log-t-kd-weight 0.0 \
      --scheduler onecycle --max-lr 3e-3 --cat-lr "$CATLR" --reg-lr 3e-3 --shared-lr 1e-3 \
      --per-fold-transition-dir output/$V14/$st --no-checkpoints > "$log" 2>&1 &
  local pid=$!; wait "$pid"
  if [ $? -eq 0 ]; then local rd; rd=$(ls -d results/$V14/$st/mtlnet_*ep${EPOCHS}_*_${pid} 2>/dev/null | head -1)
    printf '%s\t%s\t%s\n' "$key" "$arm" "$rd" >>"$MAN"; say "done $key -> $rd"
  else say "FAIL $key — see $log"; fi
}

ARMS="L0_base L1_drop01 L2_catlr3e4 L3_small L12_drop_lr L13_drop_small"
say "config: CONC=$CONC seed=$SEED arms='$ARMS' states='alabama florida'"
# AL first (fast, the key diagnostic), then FL (confirm no regression)
for st in alabama florida; do
  for arm in $ARMS; do
    run_arm "$st" "$arm" & while [ "$(jobs -rp | wc -l)" -ge "$CONC" ]; do sleep 5; done
  done
done
wait
say "ALL DONE"
