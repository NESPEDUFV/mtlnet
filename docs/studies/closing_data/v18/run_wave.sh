#!/usr/bin/env bash
# v18 — run ONE wave (one seed) across all six states and all three model families.
#
#   bash docs/studies/closing_data/v18/run_wave.sh <SEED>
#
# Families, all on the v18 engine, recipe frozen at v17:
#   cat   dedicated next-category   train.py --task next --model next_gru  (per-state bs/lr)
#   reg   dedicated next-region     p1_region_head_ablation.py --heads next_stan_flow
#   joint v17 MTL                   train.py --task mtl (bs8192, per-head cat-lr 1e-3)
#
# Protocol notes that are NOT free choices:
#   - fp32 (MTL_DISABLE_AMP=1) + --compile --tf32 everywhere: this is what every published v17
#     comparand used. bf16 grad-NaNs on this A40 at CA/TX class counts, and a non-compiled v18
#     differenced against a compiled v17 would cross protocols.
#   - MTL_ONECYCLE_PER_HEAD_LR=1 is what makes --cat-lr/--reg-lr take effect at all. Without it
#     the scalar max_lr broadcasts to every group and the run is silently v16, not v17.
#   - --canon none + the full explicit recipe: auto-canon would pin the v14 substrate and
#     MTL_STRICT=1 would hard-fail the wrong-substrate guard.
#
# Resumable + idempotent: a cell whose sidecar exists is SKIPPED, loudly. Rundirs are captured by
# the launched PID, never by newest-mtime globbing (two jobs run concurrently by design).
set -uo pipefail
cd /home/vitor.oliveira/PoiMtlNet
source /home/vitor.oliveira/.venv/bin/activate
export PYTHONPATH=src
export PYTORCH_CUDA_ALLOC_CONF="expandable_segments:True"

SEED=${1:?usage: run_wave.sh <SEED>}
ENG=check2hgi_v18
V14=check2hgi_design_k_resln_mae_l0_1
BASE=docs/studies/closing_data/v18
SIDE=docs/results/closing_data/v18
LOGS=$BASE/logs/wave_s${SEED}
RUNNING=$BASE/logs/running.jsonl
DRV=$BASE/logs/wave_s${SEED}_DRIVER.log
mkdir -p "$LOGS" "$SIDE" "$BASE/logs"
SHA=$(git rev-parse HEAD)
RAM_FLOOR_GB=80          # a CA/TX MTL dataset build peaks ~66 GB host RAM; box is shared, 125 GB

log(){ echo "[$(date '+%F %T')] $*" | tee -a "$DRV"; }
phase(){ python "$BASE/status_update.py" --phase "wave${SEED}" >/dev/null 2>&1 || true; }
memavail_gb(){ awk '/MemAvailable/{printf "%.0f",$2/1048576}' /proc/meminfo; }
flag(){ echo "$*" >> "$BASE/logs/verify_flags.jsonl"; log "[VERIFY] $*"; }

# BOUNDED (fix 2026-08-10). This used to loop forever. On a shared box whose neighbour parks above
# the floor that is an indefinite silent stall: status.json still reads phase=waveN with running=[],
# and nothing ever sets blocked_on, so a reader cannot tell a waiting wave from a progressing one.
# Wait at most WAIT_RAM_MAX_S, then proceed anyway and say so loudly -- a cell that then dies to the
# OOM-killer is recoverable (every family checkpoints or is re-run by the retry pass), whereas a
# wave that waits until morning for nothing is not.
WAIT_RAM_MAX_S=${WAIT_RAM_MAX_S:-5400}
wait_ram(){
  local a
  a=$(memavail_gb)
  local waited=0
  while [ "$a" -lt "$RAM_FLOOR_GB" ]; do
    if [ "$waited" -ge "$WAIT_RAM_MAX_S" ]; then
      log "    [VERIFY] RAM still ${a} GB < ${RAM_FLOOR_GB} GB after $((waited/60)) min — PROCEEDING anyway"
      echo "{\"kind\":\"ram_wait_timeout\",\"seed\":$SEED,\"avail_gb\":$a,\"waited_s\":$waited}" \
        >> "$BASE/logs/verify_flags.jsonl"
      return 0
    fi
    [ $((waited % 600)) -eq 0 ] && log "    waiting for RAM: ${a} GB < ${RAM_FLOOR_GB} GB floor (shared box)"
    sleep 60; waited=$((waited+60)); a=$(memavail_gb)
  done
}

mark_running(){
  local st=$1; local fam=$2; local pid=$3
  echo "{\"state\":\"$st\",\"seed\":$SEED,\"family\":\"$fam\",\"pid\":$pid,\"started_at\":\"$(date -Iseconds)\"}" >> "$RUNNING"
  phase
}

# ---------------------------------------------------------------- APPROVED v18 RECIPE (2026-08-09)
# Superseding the CEILINGS_N20_FINAL tiers, which were tuned on the LEAKED substrate.
# Source: docs/studies/closing_data/v18/FINAL_SETTINGS.md (author-approved).
#
#   dedicated cat : bs8192 everywhere; per-state max_lr; logit-adjust tau=0.5 REPLACES class weights
#   dedicated reg : UNCHANGED (tau=0 -- logit adjustment significantly HURTS Acc@10 at AL and IST)
#   joint MTL     : bs8192; category_weight 0.50; logit-adjust tau=0.5 (cat head only);
#                   cat-lr 1e-3 small / 2e-3 large
cat_bs(){ echo 8192; }                    # was alabama|istanbul 2048 -- retuned, 5-fold at AL/AZ/IST
cat_lr(){ case $1 in alabama) echo 0.0025 ;; arizona|istanbul) echo 0.0005 ;; *) echo 0.005 ;; esac; }
mtl_catlr(){ case $1 in alabama|arizona|istanbul) echo 0.001 ;; *) echo 0.002 ;; esac; }
LA_TAU=0.5                                # dedicated-cat + MTL-cat only; NEVER the region head

sidecar_write(){  # state family wall rundir cat reg
  local st=$1; local fam=$2; local wall=$3; local rd=$4; local cv=$5; local rv=$6
  local rec
  case $fam in
    cat)   rec="bs$(cat_bs "$st") lr$(cat_lr "$st") logit_adjust_tau=$LA_TAU (replaces class weighting)" ;;
    reg)   rec="max_lr 3e-3 freeze_alpha logit_adjust_tau=0 (OFF: hurts Acc@10, AL -1.84 / IST -2.75)" ;;
    joint) rec="bs8192 cat-lr $(mtl_catlr "$st") cw0.50 logit_adjust_tau=$LA_TAU (cat head only)" ;;
  esac
  python - "$SIDE/${st}_s${SEED}_${fam}.json" "$st" "$SEED" "$fam" "$wall" "$rd" "$cv" "$rv" "$SHA" "$rec" <<'PY'
import json, sys
out, st, sd, fam, wall, rd, cv, rv, sha, rec = sys.argv[1:11]
def f(x):
    try: return float(x)
    except Exception: return None
json.dump({
    "state": st, "seed": int(sd), "family": fam,
    "wall_seconds": int(float(wall)), "rundir": rd or None,
    "cat": f(cv), "reg": f(rv),
    "commit_sha": sha,
    "v18_config": {"engine": "check2hgi_v18", "forward_only": True, "in_channels": 15,
                   "node_layout": ["canonical_11", "continuous_time_4"], "repr_seed": 42},
    "protocol": {"precision": "fp32 (MTL_DISABLE_AMP=1, pinned per-command)", "compile": True, "tf32": True,
                 "folds": 5, "epochs": 50,
                 "cat_metric": "macro-F1 at f1-best epoch (diag-best)",
                 "reg_metric": "top10_acc_indist * (1 - ood_fraction) * 100 at indist-best epoch"},
    "recipe": rec,
    "recipe_version": "v18-approved-2026-08-09 (FINAL_SETTINGS.md)",
}, open(out, "w"), indent=2)
print(out)
PY
}

# ------------------------------------------------------------------ family (a): dedicated cat
cell_cat(){
  local st=$1
  local side="$SIDE/${st}_s${SEED}_cat.json"
  if [ -f "$side" ]; then log "  SKIP $st s$SEED cat (sidecar exists)"; return 0; fi
  local bs; bs=$(cat_bs "$st")
  local lr; lr=$(cat_lr "$st")
  local lg="$LOGS/${st}_cat.log"
  local t0=$SECONDS
  log "  START $st s$SEED cat (bs=$bs lr=$lr logit-adjust-tau=$LA_TAU)"
  # fp32 pinned explicitly (user decision 2026-08-07) -- never inherited from a leak.
  # --logit-adjust-tau REPLACES class weighting (next_cv.py:123-141 makes weighted CE the else
  # branch). Do NOT also pass --no-class-weights: stacking cratered in T1.4.
  env MTL_NO_TRAIN_DIAGNOSTICS=1 MTL_DISABLE_AMP=1 python scripts/train.py --task next --state "$st" --engine "$ENG" \
    --model next_gru --embedding-dim 64 --folds 5 --epochs 50 --seed "$SEED" \
    --batch-size "$bs" --max-lr "$lr" --logit-adjust-tau "$LA_TAU" \
    --compile --tf32 --no-checkpoints > "$lg" 2>&1 &
  local pid=$!
  mark_running "$st" cat "$pid"
  wait $pid; local rc=$?
  local rd; rd=$(ls -d results/$ENG/$st/next_*_${pid} 2>/dev/null | head -1)
  if [ $rc -ne 0 ] || [ -z "$rd" ]; then log "  FAIL  $st s$SEED cat rc=$rc rd='$rd' (see $lg)"; return 1; fi
  python scripts/closing_data/score_stl_cat_ceiling.py "$rd" --tag v18_${st}_cat_s${SEED} >> "$lg" 2>&1
  local v; v=$(python -c "import json;print(json.load(open('$rd/stl_cat_ceiling_score.json'))['cat_macro_f1_mean'])" 2>/dev/null)
  [ -z "$v" ] && { log "  FAIL  $st s$SEED cat: no score"; return 1; }
  sidecar_write "$st" cat $((SECONDS-t0)) "$rd" "$v" "" >/dev/null
  log "  DONE  $st s$SEED cat = $v  ($((SECONDS-t0))s)"
  phase
}

# ------------------------------------------------------------------ family (b): dedicated reg
cell_reg(){
  local st=$1
  local side="$SIDE/${st}_s${SEED}_reg.json"
  if [ -f "$side" ]; then log "  SKIP $st s$SEED reg (sidecar exists)"; return 0; fi
  local lg="$LOGS/${st}_reg.log"
  local tag="v18_${st}_reg_s${SEED}"
  local t0=$SECONDS
  log "  START $st s$SEED reg"
  # MTL_CHUNK_VAL_METRIC=1 used to force the val metric onto the CPU, and this comment used to
  # explain at length why that was necessary. Both are now out of date -- the real fix it called
  # for ("stream the val metric on GPU as mtl_eval.py does") LANDED on 2026-08-10:
  #   * streaming removed the [N, C] buffer, so the flag is no longer a memory guard at any size;
  #   * hits are derived from the rank (`hit@k == rank <= k`) instead of from topk, so the
  #     k-boundary tie-break that made CPU-vs-GPU scoring differ is gone -- integer comparisons
  #     are the same on both devices -- and P1_STREAM_GPU now defaults to ON;
  #   * an ambiguity certificate is measured every run and warns if any row could differ.
  # The flag is kept because it is what the banked cells were launched with and it now selects
  # nothing but the (unused) legacy path; `_should_chunk_val_metric` covers TX/CA on its own.
  # Measured after the change, full arizona cell: 240 s -> 147 s, all five folds identical to
  # 4 dp, worst numeric key 3.576e-08. Set P1_STREAM_GPU=0 to score on the CPU as before.
  # MTL_STRICT=1 arms the ambiguity certificate: if any val row's hit@k is genuinely undetermined
  # (the target sits in a tie group straddling k) the cell ABORTS instead of banking a number
  # whose semantics differ from its CPU/topk-scored siblings. Warn-only was not enough for an
  # unattended wave -- the warning lands in this cell's log and nowhere a reader would look.
  # [2026-10-07] P1_HITS_FROM_RANK=0 P1_STREAM_GPU=0: score as the banked cells were scored (CPU +
  # topk). With the GPU-streaming default, this recipe ABORTS at Florida under MTL_STRICT=1 (one row
  # ambiguous at the 10/11 boundary, measured on nespedgpu 2026-10-07 at c7f34917). With these two
  # values the same run completes and reproduces the printed FL cell (76.6989 vs 76.6998).
  # p1_region_head_ablation.py's own comment names this the configuration that reproduces the banked cells EXACTLY.
  env MTL_CHUNK_VAL_METRIC=1 MTL_DISABLE_AMP=1 MTL_STRICT=1 P1_HITS_FROM_RANK=0 P1_STREAM_GPU=0 \
    python -u scripts/p1_region_head_ablation.py --state "$st" --heads next_stan_flow \
    --input-type region --region-emb-source "$V14" \
    --override-hparams freeze_alpha=True alpha_init=0.0 \
    --engine-override "$ENG" --folds 5 --epochs 50 --seed "$SEED" --target region \
    --max-lr 0.003 --compile --tf32 --tag "$tag" > "$lg" 2>&1 &
  local pid=$!
  mark_running "$st" reg "$pid"
  wait $pid; local rc=$?
  local rj="docs/results/P1/region_head_${st}_region_5f_50ep_${tag}.json"
  if [ $rc -ne 0 ] || [ ! -f "$rj" ]; then log "  FAIL  $st s$SEED reg rc=$rc (see $lg)"; return 1; fi
  local v; v=$(python -c "import json;d=json.load(open('$rj'));print(round(d['heads']['next_stan_flow']['aggregate']['top10_acc_mean']*100,4))" 2>/dev/null)
  [ -z "$v" ] && { log "  FAIL  $st s$SEED reg: no score"; return 1; }
  sidecar_write "$st" reg $((SECONDS-t0)) "$rj" "" "$v" >/dev/null
  log "  DONE  $st s$SEED reg = $v  ($((SECONDS-t0))s)"
  phase
}

# ------------------------------------------------------------------ family (c): joint v17 MTL
cell_joint(){
  local st=$1
  local side="$SIDE/${st}_s${SEED}_joint.json"
  if [ -f "$side" ]; then log "  SKIP $st s$SEED joint (sidecar exists)"; return 0; fi
  case $st in florida|california|texas) wait_ram ;; esac
  local lg="$LOGS/${st}_joint.log"
  local t0=$SECONDS
  local clr; clr=$(mtl_catlr "$st")
  log "  START $st s$SEED joint (bs8192, cat-lr $clr, cw0.50, logit-adjust-tau=$LA_TAU, fp32, compile)"
  # NO bare `export` here: a shell function's exports persist into LATER cells, which is what made
  # the cat cells fp16-or-fp32 depending on resume state (see PRECISION_CAVEAT.md).
  env MTL_DISABLE_AMP=1 MTL_CHUNK_VAL_METRIC=1 MTL_STRICT=1 MTL_COMPILE_DYNAMIC=1 \
      MTL_ONECYCLE_PER_HEAD_LR=1 MTL_RAM_HEADROOM_GB=12 \
      TORCHINDUCTOR_CACHE_DIR="$HOME/.inductor_cache_v18_${st}_s${SEED}" \
    python scripts/train.py --task mtl --canon none --task-set check2hgi_next_region --engine "$ENG" \
    --state "$st" --seed "$SEED" --epochs 50 --folds 5 --batch-size 8192 \
    --mtl-loss static_weight --category-weight 0.50 --no-reg-class-weights --no-cat-class-weights \
    --logit-adjust-tau "$LA_TAU" \
    --cat-head next_gru --reg-head next_stan_flow_dualtower \
    --reg-head-param raw_embed_dim=64 --reg-head-param fusion_mode=aux \
    --reg-head-param freeze_alpha=True --reg-head-param alpha_init=0.0 \
    --task-a-input-type checkin --task-b-input-type region --log-t-kd-weight 0.0 \
    --scheduler onecycle --max-lr 3e-3 --cat-lr "$clr" --reg-lr 3e-3 --shared-lr 1e-3 \
    --model mtlnet_crossattn_dualtower --checkpoint-selector geom_simple --compile --tf32 \
    --per-fold-transition-dir "output/$V14/$st" --no-checkpoints > "$lg" 2>&1 &
  local pid=$!
  mark_running "$st" joint "$pid"
  wait $pid; local rc=$?
  local rd; rd=$(ls -d results/$ENG/$st/mtlnet_*bs8192_ep50_*_${pid} 2>/dev/null | head -1)
  if [ $rc -ne 0 ] || [ -z "$rd" ]; then log "  FAIL  $st s$SEED joint rc=$rc rd='$rd' (see $lg)"; return 1; fi
  # diag-best (Table-3 convention)
  python scripts/closing_data/a40_score_matched.py "$rd" --seed "$SEED" --tag v18_${st}_joint_s${SEED} > "$LOGS/${st}_joint_score.txt" 2>&1
  # joint-best (the single served checkpoint, JOINT_BEST_SCORING.md)
  python scripts/closing_data/score_joint_best.py "$rd" --seed "$SEED" --tag v18_${st}_joint_s${SEED} >> "$LOGS/${st}_joint_score.txt" 2>&1 || true
  local cv rv
  cv=$(python -c "import json;print(json.load(open('$rd/a40_matched_score.json'))['cat_macro_f1_mean'])" 2>/dev/null)
  rv=$(python -c "import json;print(json.load(open('$rd/a40_matched_score.json'))['reg_full_top10_mean'])" 2>/dev/null)
  [ -z "$cv" ] && { log "  FAIL  $st s$SEED joint: no score"; return 1; }
  sidecar_write "$st" joint $((SECONDS-t0)) "$rd" "$cv" "$rv" >/dev/null
  log "  DONE  $st s$SEED joint cat=$cv reg=$rv  ($((SECONDS-t0))s)"
  # §6.6 per-state sanity — v17 published values (CEILINGS_N20_FINAL.md)
  python - "$st" "$cv" "$rv" <<'PY' | tee -a "$DRV" >> "$BASE/logs/verify_flags.jsonl"
import sys
V17 = {"alabama": (64.54, 69.80), "arizona": (65.83, 59.56), "florida": (79.85, 77.42),
       "california": (77.05, 65.69), "texas": (77.24, 67.06), "istanbul": (63.33, 75.44)}
st, cv, rv = sys.argv[1], float(sys.argv[2]), float(sys.argv[3])
c17, r17 = V17[st]
if abs(cv - c17) < 5:
    print(f"{st}: cat {cv:.2f} is within 5 pp of v17 {c17:.2f} -- INVESTIGATE the forward-only path")
if abs(rv - r17) > 2:
    print(f"{st}: reg moved {rv-r17:+.2f} pp vs v17 {r17:.2f} (>2 pp) -- INVESTIGATE")
PY
  phase
}

run_state(){   # all three families for one state, sequentially
  local st=$1
  log "== $st (seed $SEED) =="
  cell_cat   "$st" || true
  cell_reg   "$st" || true
  cell_joint "$st" || true
}

# ================================================================================================
log "===== v18 WAVE seed=$SEED START — commit ${SHA:0:8} ====="
phase

# Small states run 2-wide. Large states (FL/TX/CA) run strictly 1-wide: their MTL dataset build
# peaks ~66 GB host RAM, and catx_v17_seed0_5f/RESULTS.md records 2-wide as infeasible there.
log "--- small states 2-wide: istanbul, alabama, arizona"
run_state istanbul & A=$!
run_state alabama  & B=$!
wait $A; wait $B
run_state arizona

log "--- large states 1-wide: florida, texas, california"
for st in florida texas california; do
  run_state "$st"
done

log "===== v18 WAVE seed=$SEED COMPLETE ====="
phase
python "$BASE/status_update.py" --phase "wave${SEED}" | tee -a "$DRV"
