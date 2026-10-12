#!/bin/bash
# mtl_frontier follow-up screens (user ideas, advisor-structured):
#   Idea2 aux_gated : reg-head input-dependent β  vs champion G (aux)         — AL+FL s0
#   Idea1 R10-other : GRM at AZ/GE s0 + AL {1,7,100} vs champion G            — reuse baselines
#   Idea3 stack     : G+log_T-KD+log_C-KD+rev-cat-KD+aftb_late+GRM vs G+log_T-KD — AL+FL s0
# Comparand baselines REUSED from disk; only the new arms run here. --no-checkpoints, PID capture.
set -uo pipefail
REPO=/home/vitor.oliveira/PoiMtlNet; cd "$REPO"; export PYTHONPATH=src
PY=.venv/bin/python; V14=check2hgi_design_k_resln_mae_l0_1; EPOCHS=50; CONC=${CONC:-2}
LOGDIR=/tmp/followup; mkdir -p "$LOGDIR"
MAN=scripts/mtl_frontier/followup_manifest.tsv; : > "$MAN"
export OMP_NUM_THREADS=$((32 / CONC))
ts(){ date '+%Y-%m-%d %H:%M:%S'; }; say(){ echo "[$(ts)] FU $*"; }

# args: tag state seed  + extra flags as $4...
run(){ local tag=$1 st=$2 sd=$3; shift 3; local extra=("$@")
  local log="$LOGDIR/${tag}.log"; say "start $tag (st=$st sd=$sd) extra='${extra[*]}'"
  $PY scripts/train.py --task mtl --canon none --task-set check2hgi_next_region \
      --engine "$V14" --state "$st" --seed "$sd" --epochs "$EPOCHS" --folds 5 --batch-size 2048 \
      --no-reg-class-weights --no-cat-class-weights \
      --mtl-loss static_weight --category-weight 0.75 \
      --cat-head next_gru --reg-head next_stan_flow_dualtower \
      --reg-head-param raw_embed_dim=64 \
      --reg-head-param freeze_alpha=True --reg-head-param alpha_init=0.0 \
      --task-a-input-type checkin --task-b-input-type region \
      --scheduler onecycle --max-lr 3e-3 --cat-lr 1e-3 --reg-lr 3e-3 --shared-lr 1e-3 \
      --model mtlnet_crossattn_dualtower \
      --per-fold-transition-dir "output/$V14/$st" --no-checkpoints "${extra[@]}" > "$log" 2>&1 &
  local pid=$!; wait "$pid"
  if [ $? -eq 0 ]; then
    local rd; rd=$(ls -d results/$V14/$st/mtlnet_*ep${EPOCHS}_*_${pid} 2>/dev/null | head -1)
    [ -z "$rd" ] && rd="UNKNOWN_pid${pid}"
    printf '%s\t%s\t%s\t%s\n' "$tag" "$st" "$sd" "$rd" >>"$MAN"; say "done $tag -> $rd"
  else say "FAIL $tag (see $log)"; fi
}

AUX=(--reg-head-param fusion_mode=aux)            # champion fusion
AUXG=(--reg-head-param fusion_mode=aux_gated)     # Idea 2
KDOFF=(--log-t-kd-weight 0.0)
STACK=(--reg-head-param fusion_mode=aux --log-t-kd-weight 0.2 --log-t-kd-tau 1.0 \
       --log-c-kd-weight 0.2 --cat-kd-weight 0.2 --log-c-kd-warmup-epochs 15 --log-c-kd-ec-lambda 0.3 \
       --model-param "aftb_spec=none,ab+ba" --model-param crossattn_grm=True)

say "=== follow-up screens, small-states first, CONC=$CONC ==="
# Idea 1 (small/mid states, fast): GRM at AZ/GE s0 + AL {1,7,100}
for st in arizona georgia; do
  run "i1_grm_${st}_s0" "$st" 0 "${AUX[@]}" "${KDOFF[@]}" --model-param crossattn_grm=True \
    & while [ "$(jobs -rp|wc -l)" -ge "$CONC" ]; do sleep 8; done
done
for sd in 1 7 100; do
  run "i1_grm_alabama_s${sd}" alabama "$sd" "${AUX[@]}" "${KDOFF[@]}" --model-param crossattn_grm=True \
    & while [ "$(jobs -rp|wc -l)" -ge "$CONC" ]; do sleep 8; done
done
# Idea 2: aux_gated AL+FL s0 (vs champion G aux)
run i2_auxgated_alabama_s0 alabama 0 "${AUXG[@]}" "${KDOFF[@]}" \
  & while [ "$(jobs -rp|wc -l)" -ge "$CONC" ]; do sleep 8; done
run i2_auxgated_florida_s0 florida 0 "${AUXG[@]}" "${KDOFF[@]}" \
  & while [ "$(jobs -rp|wc -l)" -ge "$CONC" ]; do sleep 8; done
# Idea 3: best-stack AL+FL s0 (vs G+log_T-KD)
run i3_stack_alabama_s0 alabama 0 "${STACK[@]}" \
  & while [ "$(jobs -rp|wc -l)" -ge "$CONC" ]; do sleep 8; done
run i3_stack_florida_s0 florida 0 "${STACK[@]}" \
  & while [ "$(jobs -rp|wc -l)" -ge "$CONC" ]; do sleep 8; done
wait; say "ALL DONE -> $MAN"
