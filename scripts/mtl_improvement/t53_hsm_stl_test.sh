#!/bin/bash
# (b) T5.3 — does hierarchical softmax (HSM) beat FLAT softmax for the high-cardinality
# reg head? The HSM head (next_stan_flow_hsm) is SINGLE-pathway (no dual-tower), so we
# test the MECHANISM at the STL/ceiling level FIRST (cheap) before any dual-tower-HSM
# build: p1 at FL, next_stan_flow_hsm (hierarchy_path, prior-OFF via no transition_path)
# vs next_stan_flow (flat, prior-OFF). Both single-pathway, 5f seed0.
#   HSM >= flat (+>=0.5pp) -> worth building a dualtower-HSM head for G.
#   HSM <  flat            -> flat softmax sufficient at 4.7k classes (FALSIFIED), done.
#   CONC=2 setsid bash scripts/mtl_improvement/t53_hsm_stl_test.sh > /tmp/t53/run.log 2>&1 &
set -uo pipefail
REPO=/home/vitor.oliveira/PoiMtlNet; cd "$REPO"; export PYTHONPATH=src
PY=.venv/bin/python; V14=check2hgi_design_k_resln_mae_l0_1; ST=florida; SD=0; EPOCHS=50; CONC=${CONC:-2}
HIER="output/$V14/$ST/region_hierarchy.pt"
LOGDIR=/tmp/t53; mkdir -p "$LOGDIR"
MAN=scripts/mtl_improvement/t53_hsm_manifest.tsv; [ -f "$MAN" ] || : > "$MAN"
export OMP_NUM_THREADS=$((32 / CONC))
ts(){ date '+%Y-%m-%d %H:%M:%S'; }; say(){ echo "[$(ts)] T53 $*"; }
A0="freeze_alpha=True alpha_init=0.0"   # flat head: prior off
run(){ local head=$1; shift; local key="${head}|${ST}"
  grep -qF "$key	" "$MAN" && { say "skip $key"; return 0; }
  local tag="t53_${head}_${ST}_s${SD}"; local log="$LOGDIR/${head}.log"; say "start $head"
  $PY scripts/p1_region_head_ablation.py --state "$ST" --heads "$head" \
      --input-type region --region-emb-source "$V14" \
      --folds 5 --epochs "$EPOCHS" --batch-size 2048 --seed "$SD" --target region --tag "$tag" \
      --per-fold-transition-dir "output/check2hgi/$ST" "$@" > "$log" 2>&1 \
    && { printf '%s\t%s\tdocs/results/P1/region_head_%s_region_5f_50ep_%s.json\n' "$key" "$head" "$ST" "$tag" >>"$MAN"; say "done $head"; } \
    || say "FAIL $head — see $log"
}
say "=== T5.3 HSM-vs-flat STL test, FL seed0 ==="
# flat softmax (= the (c) ceiling head), prior off
run next_stan_flow --override-hparams $A0 &
while [ "$(jobs -rp|wc -l)" -ge "$CONC" ]; do sleep 8; done
# hierarchical softmax, prior off (no transition_path -> log_T zeros -> prior inert)
run next_stan_flow_hsm --override-hparams hierarchy_path="$HIER" alpha_init=0.0 &
while [ "$(jobs -rp|wc -l)" -ge "$CONC" ]; do sleep 8; done
wait; say "ALL DONE"
