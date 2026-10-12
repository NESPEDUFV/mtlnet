#!/usr/bin/env bash
# v18 Phase 0, FAST PATH — build + materialize from the one-shot full-graph export.
#
# The per-window `prefix_forward_only` readout costs one forward pass per window and is an IDENTITY
# on a forward-only graph (messages flow past -> future only, so a visit's vector cannot depend on
# anything after it). Verified over EVERY window at three states:
#   alabama 96,326 -> 2.384e-06 | arizona 200,895 -> 2.861e-06 | istanbul 271,666 -> 3.099e-06
# (mean ~1.4e-07 = float32 epsilon; slot 8, the truncation boundary, no worse than slot 0).
# materialize_from_insample.py hard-fails unless build.json reports forward_only, so this shortcut
# cannot be misapplied to a bidirectional arm where the rebuild does real work.
set -uo pipefail
cd /home/vitor.oliveira/PoiMtlNet
source /home/vitor.oliveira/.venv/bin/activate
export PYTHONPATH=src:research
export PYTORCH_CUDA_ALLOC_CONF="expandable_segments:True"

ENG=check2hgi_v18; SRC=check2hgi_dk_ovl; V14=check2hgi_design_k_resln_mae_l0_1
ROOT=results/$ENG
BASE=docs/studies/closing_data/v18
DRV=$BASE/logs/phase0_fast_DRIVER.log
mkdir -p "$BASE/logs"
log(){ echo "[$(date '+%F %T')] $*" | tee -a "$DRV"; }

do_state(){
  local st=$1
  local cell="$ROOT/$st/V18"
  local blog="$BASE/logs/phase0_${st}.log"
  mkdir -p "$cell"

  if [ -f "$cell/checkpoint.pt" ] && [ -f "$cell/build.json" ]; then
    log "  SKIP build $st (exists)"
  else
    log "  BUILD $st"
    local t0=$SECONDS
    python scripts/integrity_v2/build_study_repr.py \
      --state "$st" --cell V18 --repr-seed 42 --epochs 500 --device cuda --encoder resln \
      --study-root "$ROOT" --forward-only --add-continuous-time >> "$blog" 2>&1 \
      || { log "  FAIL build $st"; return 1; }
    log "  built $st in $((SECONDS-t0))s"
  fi

  if [ -f "output/$ENG/$st/input/next.parquet" ]; then
    log "  SKIP materialize $st (exists)"
  else
    log "  MATERIALIZE $st (one-shot export)"
    local t0=$SECONDS
    local extra=()
    [ -f "$cell/win_matched.npz" ] && extra=(--validate-against-npz "$cell/win_matched.npz")
    python scripts/integrity_v2/materialize_from_insample.py --state "$st" \
      --study-run "$cell" --source-engine "$SRC" --dest-engine "$ENG" "${extra[@]}" \
      >> "$blog" 2>&1 || { log "  FAIL materialize $st"; return 1; }
    log "  materialized $st in $((SECONDS-t0))s"
  fi

  local d="output/$ENG/$st"
  mkdir -p "$d/temp"
  [ -f "$d/temp/sequences_next.parquet" ] || cp "output/$SRC/$st/temp/sequences_next.parquet" "$d/temp/"
  [ -e "$d/region_embeddings.parquet" ] || \
    ln -s "$(realpath "output/$V14/$st/region_embeddings.parquet")" "$d/region_embeddings.parquet"
  log "  ENGINE READY $st"
}

log "===== v18 Phase 0 FAST PATH START (commit $(git rev-parse --short HEAD)) ====="
for st in "$@"; do do_state "$st"; done
log "===== v18 Phase 0 FAST PATH DONE ====="
