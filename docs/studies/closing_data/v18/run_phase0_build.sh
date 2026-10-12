#!/usr/bin/env bash
# v18 Phase 0 — build the leak-free representation for all six states, once per state.
#
# v18 = v17 recipe on a substrate whose consecutive-visit graph is FORWARD-ONLY (training AND
# readout) plus 4 elapsed-time node columns => in_channels 15 (canonical 11 + continuous_time 4).
#
# The representation does NOT depend on the downstream training seed: one engine per state, fixed
# repr seed 42 (matching the study builds), shared by all four waves.
#
# Alabama is NOT rebuilt: cell E2 of the integrity_v2 study is bit-for-bit this definition
# (--forward-only --add-continuous-time, seed 42, 500 ep, resln, dim 64, 2 layers, all users,
# self_test true). It is materialized into the v18 engine from its existing npz.
#
# Resumable + idempotent: every stage skips when its output exists, and says so.
set -uo pipefail
cd /home/vitor.oliveira/PoiMtlNet
source /home/vitor.oliveira/.venv/bin/activate
export PYTHONPATH=src:research
export PYTORCH_CUDA_ALLOC_CONF="expandable_segments:True"

ENG=check2hgi_v18
SRC=check2hgi_dk_ovl                                  # row space + region labels
V14=check2hgi_design_k_resln_mae_l0_1                 # region embeddings (symlinked, never copied)
ROOT=results/$ENG                                     # representation runs
BASE=docs/studies/closing_data/v18
DRV=$BASE/logs/phase0_DRIVER.log
mkdir -p "$BASE/logs" "$ROOT"
log(){ echo "[$(date '+%F %T')] $*" | tee -a "$DRV"; }

# ---- one state: build -> infer -> materialize -> complete the engine dir -----------------------
build_state(){
  local st=$1
  local cell_dir="$ROOT/$st/V18"
  local npz="$cell_dir/win_matched.npz"
  local blog="$BASE/logs/phase0_${st}.log"
  mkdir -p "$cell_dir"

  # 1. representation
  if [ -f "$cell_dir/checkpoint.pt" ] && [ -f "$cell_dir/build.json" ]; then
    log "  SKIP build   $st (checkpoint + build.json exist)"
  else
    log "  BUILD        $st (500 ep, resln, dim 64, forward-only + continuous-time)"
    local t0=$SECONDS
    python scripts/integrity_v2/build_study_repr.py \
      --state "$st" --cell V18 --repr-seed 42 --epochs 500 --device cuda --encoder resln \
      --study-root "$ROOT" --forward-only --add-continuous-time \
      >> "$blog" 2>&1 || { log "  FAIL build $st (see $blog)"; return 1; }
    log "  built        $st in $((SECONDS-t0))s"
  fi

  # 2. readout — MUST match the training graph; never pass --allow-direction-mismatch
  if [ -f "$npz" ]; then
    log "  SKIP infer   $st (npz exists)"
  else
    log "  INFER        $st (readout prefix_forward_only, --self-test)"
    local t0=$SECONDS
    python scripts/integrity_v2/infer_checkins.py \
      --state "$st" --checkpoint "$cell_dir/checkpoint.pt" \
      --readout prefix_forward_only --out "$npz" --self-test \
      >> "$blog" 2>&1 || { log "  FAIL infer $st (see $blog)"; return 1; }
    log "  inferred     $st in $((SECONDS-t0))s"
  fi

  materialize_state "$st" "$npz" || return 1
}

# ---- turn an npz into a complete engine directory ---------------------------------------------
materialize_state(){
  local st=$1 npz=$2
  local dest="output/$ENG/$st"
  local blog="$BASE/logs/phase0_${st}.log"

  if [ -f "$dest/input/next.parquet" ] && [ -f "$dest/input/next_region.parquet" ]; then
    log "  SKIP materi. $st (input parquets exist)"
  else
    log "  MATERIALIZE  $st"
    python scripts/integrity_v2/materialize_engine.py \
      --state "$st" --arm-npz "$npz" --source-engine "$SRC" --dest-engine "$ENG" \
      >> "$blog" 2>&1 || { log "  FAIL materialize $st (see $blog)"; return 1; }
  fi

  # A v18 engine dir needs FOUR things, not just the two parquets materialize writes.
  # temp/sequences_next.parquet is the PLACE sequence: data, identical across arms -> copy.
  mkdir -p "$dest/temp"
  if [ ! -f "$dest/temp/sequences_next.parquet" ]; then
    cp "output/$SRC/$st/temp/sequences_next.parquet" "$dest/temp/sequences_next.parquet" \
      || { log "  FAIL seq copy $st"; return 1; }
    log "  copied       $st temp/sequences_next.parquet"
  fi
  # region_embeddings.parquet is SYMLINKED from the v14 engine so the two provably share one
  # table -- a region contrast must not be confounded by different region vectors.
  if [ ! -e "$dest/region_embeddings.parquet" ]; then
    ln -s "$(realpath "output/$V14/$st/region_embeddings.parquet")" "$dest/region_embeddings.parquet" \
      || { log "  FAIL region symlink $st"; return 1; }
    log "  symlinked    $st region_embeddings.parquet -> $V14"
  fi
  log "  ENGINE READY $st"
}

# ---- self-checks that must pass before any training uses this engine --------------------------
verify_state(){
  local st=$1
  python - "$st" "$ENG" "$SRC" "$ROOT" <<'PY' 2>&1 | tee -a "$DRV"
import json, sys, pathlib
import pandas as pd
st, eng, src, root = sys.argv[1:5]
ok = True
def chk(cond, msg):
    global ok
    print(f"  [{'PASS' if cond else 'FAIL'}] {st}: {msg}")
    ok = ok and bool(cond)

bj = pathlib.Path(root)/st/"V18"/"build.json"
if bj.exists():
    b = json.loads(bj.read_text())
    lay = (b.get("node_enrichment") or {}).get("layout")
    chk(lay == ["canonical_11", "continuous_time_4"], f"build layout {lay}")
    chk(b.get("node_feature_schema", {}).get("width") == 15,
        f"in_channels {b.get('node_feature_schema',{}).get('width')} (want 15)")
    cg = b.get("causal_graph") or {}
    chk(cg.get("forward_only") is True, f"forward_only {cg.get('forward_only')}")
    chk(cg.get("edges_after") == cg.get("edges_before", 0) - cg.get("dropped_backward", -1),
        f"edges {cg.get('edges_before')} -> {cg.get('edges_after')}")
else:
    print(f"  [note] {st}: no V18/build.json (reused cell) -- checked at its own build.json")

meta = pathlib.Path(root)/st/"V18"/"win_matched.npz.meta.json"
if meta.exists():
    m = json.loads(meta.read_text())
    chk(m.get("readout") == "prefix_forward_only", f"readout {m.get('readout')}")
    chk(m.get("self_test") is True, f"self_test {m.get('self_test')}")

# row pairing vs the source arm: ids, labels, userids, >=95% retention
d = pathlib.Path("output")/eng/st/"input"
s = pathlib.Path("output")/src/st/"input"
a = pd.read_parquet(d/"next.parquet", columns=["userid", "next_category"])
c = pd.read_parquet(s/"next.parquet", columns=["userid", "next_category"])
r = pd.read_parquet(d/"next_region.parquet", columns=["userid"])
chk(len(a)/len(c) >= 0.95, f"retention {len(a)}/{len(c)} = {len(a)/len(c):.4f}")
chk(a["userid"].equals(r["userid"]), "next/next_region userid alignment")
nf = len(pd.read_parquet(d/"next.parquet").columns) - 2
chk(nf % 9 == 0 and nf // 9 == 64, f"feature width {nf} = 9 x {nf//9}")
chk((pathlib.Path("output")/eng/st/"region_embeddings.parquet").is_symlink(),
    "region_embeddings.parquet is a symlink")
print(f"  ==> {st}: {'ALL PASS' if ok else 'HAS FAILURES'}")
sys.exit(0 if ok else 1)
PY
}

# ================================================================================================
log "===== v18 Phase 0 START — commit $(git rev-parse --short HEAD) ====="

# Alabama: reuse the already-built E2 cell (same definition), materialize only. No GPU.
AL_NPZ=results/check2hgi_integrity_v2/alabama/E2/win_matched.npz
log "alabama: reusing integrity_v2 cell E2 as the v18 representation (identical definition)"
mkdir -p "$ROOT/alabama/V18"
for f in build.json checkpoint.pt win_matched.npz win_matched.npz.meta.json; do
  [ -e "$ROOT/alabama/V18/$f" ] || ln -s "$(realpath results/check2hgi_integrity_v2/alabama/E2/$f)" "$ROOT/alabama/V18/$f"
done
materialize_state alabama "$AL_NPZ" && verify_state alabama

# Smallest first, so a failure surfaces cheap. 2-wide only for the two small states; FL/CA/TX
# run 1-wide (their MTL dataset builds peak ~66 GB host RAM on this shared 125 GB box).
log "--- small states (2-wide): istanbul, arizona"
build_state istanbul  & P1=$!
build_state arizona   & P2=$!
wait $P1; wait $P2
verify_state istanbul; verify_state arizona

for st in florida california texas; do
  log "--- large state (1-wide): $st"
  build_state "$st" && verify_state "$st"
done

log "===== v18 Phase 0 COMPLETE ====="
for st in istanbul alabama arizona florida california texas; do
  d="output/$ENG/$st/input/next.parquet"
  [ -f "$d" ] && log "  ready: $st ($(du -h "$d" | cut -f1))" || log "  MISSING: $st"
done
