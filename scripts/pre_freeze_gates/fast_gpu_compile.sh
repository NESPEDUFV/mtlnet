#!/bin/bash
# FAST closers for Q1 (CA/TX dataset-on-GPU + MTL_DATASET_GPU=1 fit) and Q3 (compile+tf32
# speed gain at huge states). Short fold-1 runs (peak VRAM hits in epoch 1; steady epoch
# time in epochs 2+). Champion-G gated overlap. Run ALONE (clean timing) — the waiter
# below sequences it after FL.  usage: fast_gpu_compile.sh
set -uo pipefail
REPO=/home/vitor.oliveira/PoiMtlNet; cd "$REPO"; export PYTHONPATH=src
PY=.venv/bin/python; export OMP_NUM_THREADS=24
export MTL_CHUNK_VAL_METRIC=1 PYTORCH_CUDA_ALLOC_CONF="expandable_segments:True"
export MTL_DATASET_GPU=1                       # Q1: FORCE dataset onto GPU
V14=check2hgi_design_k_resln_mae_l0_1; OVL=check2hgi_dk_ovl
L=/tmp/gate_eval/fast; mkdir -p "$L"
say(){ echo "[$(date '+%F %T')] FAST $*" | tee -a "$L/run.log"; }

cell(){ # state mode(off|on)  -> short fold-1 6-epoch run, capture peak VRAM + wall
  local ST=$1 mode=$2; local knobs=""; [ "$mode" = on ] && knobs="--compile --tf32"
  export TORCHINDUCTOR_CACHE_DIR="$L/ind_${ST}_${mode}"
  local clog="$L/${ST}_${mode}.log"; say "$ST $mode (MTL_DATASET_GPU=1 $knobs)"
  ( mx=0; while kill -0 $$ 2>/dev/null; do u=$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits 2>/dev/null|head -1); [ -n "$u" ]&&[ "$u" -gt "$mx" ]&&{ mx=$u; echo $mx>"$L/vram_${ST}_${mode}"; }; sleep 2; done ) &
  local samp=$!; local t0=$(date +%s)
  $PY scripts/train.py --task mtl --task-set check2hgi_next_region --engine "$OVL" \
    --state "$ST" --seed 42 --epochs 6 --folds 1 --batch-size 2048 \
    --mtl-loss static_weight --category-weight 0.75 \
    --cat-head next_gru --reg-head next_stan_flow_dualtower \
    --reg-head-param raw_embed_dim=64 --reg-head-param fusion_mode=aux \
    --reg-head-param freeze_alpha=True --reg-head-param alpha_init=0.0 \
    --task-a-input-type checkin --task-b-input-type region --log-t-kd-weight 0.0 \
    --scheduler onecycle --max-lr 3e-3 --cat-lr 1e-3 --reg-lr 3e-3 --shared-lr 1e-3 \
    --model mtlnet_crossattn_dualtower $knobs \
    --per-fold-transition-dir "output/$V14/$ST" --no-checkpoints > "$clog" 2>&1
  local rc=$?; kill $samp 2>/dev/null
  echo $(( $(date +%s) - t0 )) > "$L/wall_${ST}_${mode}"
  say "$ST $mode rc=$rc wall=$(cat "$L/wall_${ST}_${mode}")s peakVRAM=$(cat "$L/vram_${ST}_${mode}" 2>/dev/null)MiB"
}

say "=== FAST Q1+Q3 (TX huge + CA) ==="
cell texas off ; cell texas on
cell california off ; cell california on

say "=== SUMMARY ==="
$PY - "$L" <<'PY' 2>&1 | tee -a "$L/run.log"
import sys,glob,re,os
L=sys.argv[1]
def rd(f):
    try: return open(f).read().strip()
    except: return None
def epoch_secs(clog):
    # parse tqdm 'Epoch N/6 ... [MM:SS<' final per-epoch elapsed; approximate steady via wall/epochs
    return None
print(f"\n========= FAST Q1 (fit) + Q3 (compile speed) — MTL_DATASET_GPU=1, fold-1/6ep =========")
for ST in ("texas","california"):
    wo,wn=rd(f"{L}/wall_{ST}_off"),rd(f"{L}/wall_{ST}_on")
    vo,vn=rd(f"{L}/vram_{ST}_off"),rd(f"{L}/vram_{ST}_on")
    sp=""
    if wo and wn and int(wn)>0:
        # 6-epoch wall incl. ~1 compile-warmup epoch on 'on'; steady speedup is a bit better
        sp=f" | 6ep wall {int(wo)}s->{int(wn)}s ({(int(wo)/int(wn)-1)*100:+.0f}%, warmup-included)"
    print(f"  {ST:11} fit: peakVRAM off={vo}MiB on={vn}MiB (A40=46068){sp}")
    for m in ("off","on"):
        oom=any('out of memory' in open(g).read().lower() for g in [f"{L}/{ST}_{m}.log"] if os.path.exists(g))
        print(f"      {ST}_{m}: {'GPU-OOM!' if oom else 'FIT (trained fold-1)'}")
PY
say "DONE"
