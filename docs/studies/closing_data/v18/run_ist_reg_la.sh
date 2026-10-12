#!/usr/bin/env bash
# v18 — logit adjustment on the DEDICATED REGION head at istanbul (second state).
#
# WHY. Alabama (5 folds) said logit adjustment must stay OFF for region, and said it in the shape the
# theory predicts: macro-F1 UP +0.377 (p=0.0008) while every frequency-weighted metric went DOWN
# (Acc@10 -1.841 p=0.0002, Acc@5 -2.083, Acc@1 -1.242, MRR -1.590). That is Bayes-consistency for
# BALANCED error trading against the reported Acc@10.
#
# Istanbul is the useful second state: it is the region-strongest dataset (~75-77 Acc@10 vs alabama's
# ~70) and has a different region-class count, so if the sign holds there it is a property of the
# metric rather than of alabama.
#
# Both arms run fresh so the comparison is paired on the same 5 folds and same seed.
set -uo pipefail
cd /home/vitor.oliveira/PoiMtlNet
source /home/vitor.oliveira/.venv/bin/activate
ENG=check2hgi_v18
BASE=docs/studies/closing_data/v18
OUT=$BASE/logs/ist_reg; mkdir -p "$OUT"
D=$BASE/logs/ist_reg_DRIVER.log
log(){ echo "[$(date '+%F %T')] ISTREG: $*" | tee -a "$D"; }

reg_arm(){ # state tau
  local st=$1
  local tau=$2
  local tag="v18_${st}_reg_la${tau}_s0"
  local lg="$OUT/${tag}.log"
  local t0=$SECONDS
  log "RUN  $tag [logit-adjust-tau=$tau]"
  env PYTHONPATH=src MTL_CHUNK_VAL_METRIC=1 MTL_DISABLE_AMP=1 \
      PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True \
      TORCHINDUCTOR_CACHE_DIR="$HOME/.inductor_v18reg_${st}" \
    python -u scripts/p1_region_head_ablation.py --state "$st" --heads next_stan_flow \
      --input-type region --region-emb-source check2hgi_design_k_resln_mae_l0_1 \
      --override-hparams freeze_alpha=True alpha_init=0.0 \
      --engine-override "$ENG" --folds 5 --epochs 50 --seed 0 --target region \
      --max-lr 0.003 --logit-adjust-tau "$tau" --compile --tf32 --tag "$tag" > "$lg" 2>&1 &
  local pid=$!; wait $pid; local rc=$?
  [ $rc -ne 0 ] && { log "FAIL $tag rc=$rc (see $lg)"; return 1; }
  log "DONE $tag ($((SECONDS-t0))s)"
}

log "===== istanbul dedicated region: tau=0 vs tau=0.5 ====="
reg_arm istanbul 0.0
reg_arm istanbul 0.5
log "===== COMPLETE ====="
