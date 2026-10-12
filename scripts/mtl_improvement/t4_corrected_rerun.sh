#!/bin/bash
# T4 CORRECTED re-run (post-audit 2026-06-08). The T4.1 default screen was PARTIALLY INVALID:
#  - gradient-surgery (cagrad/pcgrad/aligned_mtl) only reweight SHARED params; G's private reg
#    tower trains at unit weight -> they collapse to ~equal weighting (a dual-tower×surgery
#    limitation). MOOT here: grad-cosine(cat,reg) ≈ 0 at AL+FL -> NO conflict to surge.
#  - gradnorm (lr=1e-3 too small + sum=2 centering), nash (max_norm=1.0 vs canonical 2.2) were
#    misconfigured. fairgrad/dwa pinned at equal.
# This re-runs the two things that ACTUALLY matter per audit + literature (Xin'22):
#  (1) STATIC cw-sweep {0.50,0.60,0.66,0.80} — ensure G's 0.75 is the best static (fair baseline).
#  (2) gradnorm @ lr=0.05 + nash @ max_norm=2.2 — the valid adaptive methods, properly tuned.
# All under G arch, single-seed (seed0), FL+AL. Usage:
#   STATE=florida CONC=2 setsid bash scripts/mtl_improvement/t4_corrected_rerun.sh > /tmp/t4c/fl.log 2>&1 &
set -uo pipefail
REPO=/home/vitor.oliveira/PoiMtlNet; cd "$REPO"; export PYTHONPATH=src
PY=.venv/bin/python; V14=check2hgi_design_k_resln_mae_l0_1
ST=${STATE:-alabama}; SD=0; EPOCHS=50; CONC=${CONC:-2}
LOGDIR=/tmp/t4c/$ST; mkdir -p "$LOGDIR"
MAN=scripts/mtl_improvement/t4_corrected_manifest.tsv; [ -f "$MAN" ] || : > "$MAN"
export OMP_NUM_THREADS=$((32 / CONC))
ts(){ date '+%Y-%m-%d %H:%M:%S'; }; say(){ echo "[$(ts)] T4C[$ST] $*"; }
COMMON=(--task mtl --canon none --task-set check2hgi_next_region --engine "$V14"
  --state "$ST" --seed "$SD" --epochs "$EPOCHS" --folds 5 --batch-size 2048
  --no-reg-class-weights --no-cat-class-weights
  --cat-head next_gru --reg-head next_stan_flow_dualtower
  --reg-head-param raw_embed_dim=64 --reg-head-param fusion_mode=aux
  --reg-head-param freeze_alpha=True --reg-head-param alpha_init=0.0
  --task-a-input-type checkin --task-b-input-type region --log-t-kd-weight 0.0
  --scheduler onecycle --max-lr 3e-3 --cat-lr 1e-3 --reg-lr 3e-3 --shared-lr 1e-3
  --model mtlnet_crossattn_dualtower
  --per-fold-transition-dir "output/$V14/$ST" --no-checkpoints)

run(){ local key=$1; shift; local fk="${key}|${ST}"
  grep -qF "$fk	" "$MAN" && { say "skip $fk"; return 0; }
  local log="$LOGDIR/${key}.log"; say "start $key"
  $PY scripts/train.py "${COMMON[@]}" "$@" > "$log" 2>&1 &
  local pid=$!; wait "$pid"
  if [ $? -eq 0 ]; then
    local rd; rd=$(ls -d results/$V14/$ST/mtlnet_*ep${EPOCHS}_*_${pid} 2>/dev/null | head -1)
    [ -z "$rd" ] && rd=$(ls -dt results/$V14/$ST/mtlnet_*ep${EPOCHS}_* 2>/dev/null | head -1)
    printf '%s\t%s\t%s\n' "$fk" "$key" "$rd" >>"$MAN"; say "done $key -> $rd"
  else say "FAIL $key — see $log"; fi
}

say "=== T4 corrected re-run, seed0, CONC=$CONC ==="
# (1) static cw sweep (fair-baseline; 0.75 already = G)
run static_cw0.50 --mtl-loss static_weight --category-weight 0.50 &
while [ "$(jobs -rp|wc -l)" -ge "$CONC" ]; do sleep 8; done
run static_cw0.60 --mtl-loss static_weight --category-weight 0.60 &
while [ "$(jobs -rp|wc -l)" -ge "$CONC" ]; do sleep 8; done
run static_cw0.66 --mtl-loss static_weight --category-weight 0.66 &
while [ "$(jobs -rp|wc -l)" -ge "$CONC" ]; do sleep 8; done
run static_cw0.80 --mtl-loss static_weight --category-weight 0.80 &
while [ "$(jobs -rp|wc -l)" -ge "$CONC" ]; do sleep 8; done
# (2) retuned adaptive methods
run gradnorm_lr0.05 --mtl-loss gradnorm --mtl-loss-param lr=0.05 --mtl-loss-param alpha=1.5 &
while [ "$(jobs -rp|wc -l)" -ge "$CONC" ]; do sleep 8; done
run nash_mn2.2 --mtl-loss nash_mtl --mtl-loss-param max_norm=2.2 &
while [ "$(jobs -rp|wc -l)" -ge "$CONC" ]; do sleep 8; done
wait
say "ALL DONE ($ST)"
