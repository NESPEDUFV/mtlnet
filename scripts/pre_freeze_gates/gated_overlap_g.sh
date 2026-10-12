#!/bin/bash
# Gated-overlap champion-G MTL run (M1 emit_tail gate validation).
# Runs champion-G (dual-tower, prior-OFF, KD-off) on the GATED check2hgi_dk_ovl
# engine for one (state, seed), captures the rundir by PID (no ls -dt race),
# and prints per-task diagnostic-best metrics for comparison vs the ungated R1 doc.
#   usage: gated_overlap_g.sh <state> <seed> [epochs] [folds]
set -uo pipefail
REPO=/home/vitor.oliveira/PoiMtlNet; cd "$REPO"; export PYTHONPATH=src
PY=.venv/bin/python
# S2 chunked val-metric — needed at overlap scale (8.5× rows) for the large-C
# states so the val metric doesn't materialize a full O(N_val·C) logit. Byte-identical.
export MTL_CHUNK_VAL_METRIC=1
export PYTORCH_CUDA_ALLOC_CONF="expandable_segments:True"
ST=${1:-alabama}; SD=${2:-42}; EPOCHS=${3:-50}; FOLDS=${4:-5}
V14=check2hgi_design_k_resln_mae_l0_1; OVL=check2hgi_dk_ovl
LOGDIR=/tmp/gate_eval; mkdir -p "$LOGDIR"
export OMP_NUM_THREADS=24
log="$LOGDIR/g_${OVL}_${ST}_s${SD}.log"
echo "[$(date '+%F %T')] START champion-G gated-overlap $ST seed=$SD ($EPOCHS ep, $FOLDS folds)"
$PY scripts/train.py --task mtl --task-set check2hgi_next_region --engine "$OVL" \
    --state "$ST" --seed "$SD" --epochs "$EPOCHS" --folds "$FOLDS" --batch-size 2048 \
    --mtl-loss static_weight --category-weight 0.75 \
    --cat-head next_gru --reg-head next_stan_flow_dualtower \
    --reg-head-param raw_embed_dim=64 --reg-head-param fusion_mode=aux \
    --reg-head-param freeze_alpha=True --reg-head-param alpha_init=0.0 \
    --task-a-input-type checkin --task-b-input-type region --log-t-kd-weight 0.0 \
    --scheduler onecycle --max-lr 3e-3 --cat-lr 1e-3 --reg-lr 3e-3 --shared-lr 1e-3 \
    --model mtlnet_crossattn_dualtower \
    --per-fold-transition-dir "output/$V14/$ST" --no-checkpoints > "$log" 2>&1 &
pid=$!; wait "$pid"; rc=$?
if [ $rc -ne 0 ]; then echo "[$(date '+%F %T')] FAIL rc=$rc — see $log"; tail -20 "$log"; exit $rc; fi
rd=$(ls -d results/$OVL/$ST/mtlnet_*ep${EPOCHS}_*_${pid} 2>/dev/null | head -1)
[ -z "$rd" ] && rd=$(ls -dt results/$OVL/$ST/mtlnet_*ep${EPOCHS}_* 2>/dev/null | head -1)
echo "[$(date '+%F %T')] DONE $ST seed=$SD -> $rd"
# aggregate per-task DIAGNOSTIC-BEST (fold_info.json), not joint full_summary
$PY - "$rd" <<'PY'
import sys, json, glob, os, numpy as np
rd=sys.argv[1]
cat=[]; reg=[]
for fi in sorted(glob.glob(os.path.join(rd, "**/fold_info.json"), recursive=True)):
    d=json.load(open(fi)); db=d.get("diagnostic_best_epochs", d)
    def dig(o,*ks):
        for k in ks:
            if isinstance(o,dict) and k in o: o=o[k]
            else: return None
        return o
    c=dig(db,"category","macro_f1") or dig(db,"cat","macro_f1")
    r=dig(db,"region","top10_acc_indist") or dig(db,"region","top10_acc")
    if c is not None: cat.append(c*100 if c<=1 else c)
    if r is not None: reg.append(r*100 if r<=1 else r)
def ms(x): return (np.mean(x), np.std(x), len(x)) if x else (float('nan'),float('nan'),0)
cm,cs,cn=ms(cat); rm,rs,rn=ms(reg)
print(f"  GATED-OVERLAP {os.path.basename(rd)}")
print(f"    cat macro-F1        = {cm:.2f} ± {cs:.2f} (n={cn})")
print(f"    reg top10_acc_indist= {rm:.2f} ± {rs:.2f} (n={rn})")
PY
