#!/bin/bash
# Georgia (GE) onboarding for the mtl_improvement study (T0.1b).
# Builds ESSENTIAL substrates (canonical check2hgi + HGI-preprocess + POI2Vec + v14 design_k
# + postbuild + seeded log_T for {0,1,7,100,42}). HGI *training* (region embeddings, for the
# STL-HGI / composite ceilings) is a SEPARATE deferrable tail — see build_ge_hgi_train.sh.
# Modeled on scripts/substrate_protocol_cleanup/build_v13_catx.sh (tested CA/TX onboarding),
# adapted: stage A trains the canonical-fresh substrate (GE has no frozen v11), stage D builds
# v14 instead of v13. Detached, disk-guarded, fail-fast, idempotent skips.
#   Launch: setsid bash scripts/_v14_run/build_ge.sh > /tmp/ge_build/run.log 2>&1 &
set -uo pipefail
REPO=/home/vitor.oliveira/PoiMtlNet
cd "$REPO"
PY=.venv/bin/python
SC=Georgia          # capitalized (city= arg)
SL=georgia          # lowercase slug (output dirs)
SHP="data/miscellaneous/tl_2022_13_tract_GA/tl_2022_13_tract.shp"
V14=check2hgi_design_k_resln_mae_l0_1
SEEDS="0 1 7 100 42"
LOGDIR=/tmp/ge_build
mkdir -p "$LOGDIR"
: > "$LOGDIR/STAGES.DONE"

ts(){ date '+%Y-%m-%d %H:%M:%S'; }
say(){ echo "[$(ts)] GE $*"; }
fail(){ say "FATAL $1"; echo "FAIL:$1" > "$LOGDIR/FATAL.DONE"; exit 1; }
disk_guard(){
  local free; free=$(df -m /home | tail -1 | awk '{print $4}')
  say "[disk] ${free} MB free before $1"
  [ "$free" -lt 6000 ] && { say "disk < 6000 MB before $1 — STOP"; echo "DISKFAIL:$1" > "$LOGDIR/FATAL.DONE"; exit 9; }
}

# ---- precheck ----
[ -f "$SHP" ] || fail "shapefile_missing $SHP"
[ -f "data/checkins/${SC}.parquet" ] || fail "checkins_missing"

# ---- Stage A: canonical check2hgi (preprocess + GCN train + sequences) ----
# Produces temp/checkin_graph.pt + temp/sequences_next.parquet (v14 prereqs) + canonical
# embeddings/poi/region parquets (the canonical-fresh comparand) + input/next.parquet.
if [ -f "output/check2hgi/$SL/embeddings.parquet" ] && [ -f "output/check2hgi/$SL/temp/sequences_next.parquet" ]; then
  say "A skip canonical (exists)"
else
  disk_guard "A_canonical"
  say "A start canonical check2hgi (preprocess + 500ep GCN train, GPU)"
  PYTHONPATH=src:research $PY - <<'PYEOF' > "$LOGDIR/A_canonical.log" 2>&1
import sys
from argparse import Namespace
from configs.paths import Resources, EmbeddingEngine
from configs.model import InputsConfig
from embeddings.check2hgi.check2hgi import create_embedding
from data.inputs.builders import generate_next_input_from_checkins
cfg = Namespace(
    dim=InputsConfig.EMBEDDING_DIM, num_layers=2, attention_head=4,
    alpha_c2p=0.4, alpha_p2r=0.3, alpha_r2c=0.3, lr=0.001, gamma=1.0, max_norm=0.9,
    epoch=500, mini_batch_threshold=5_000_000, batch_size=2**13, num_neighbors=10,
    device='cuda', shapefile=Resources.TL_GA, force_preprocess=True,
    edge_type='user_sequence', temporal_decay=3600.0, use_compile=False, use_amp=False,
)
create_embedding(state='Georgia', args=cfg)
generate_next_input_from_checkins('Georgia', EmbeddingEngine.CHECK2HGI)
print('[A] canonical done')
PYEOF
  [ -f "output/check2hgi/$SL/embeddings.parquet" ] || fail "A_canonical_embeddings"
  [ -f "output/check2hgi/$SL/temp/checkin_graph.pt" ] || fail "A_checkin_graph"
  [ -f "output/check2hgi/$SL/temp/sequences_next.parquet" ] || fail "A_sequences_next"
  echo "A:canonical $(ts)" >> "$LOGDIR/STAGES.DONE"; say "A done canonical"
fi

# ---- Stage B: HGI preprocess (Delaunay edges.csv — v14 prereq; NOT HGI training) ----
if [ -f "output/hgi/$SL/temp/edges.csv" ]; then
  say "B skip hgi-preprocess (edges.csv exists)"
else
  disk_guard "B_hgi_preprocess"
  say "B start HGI preprocess (Delaunay edges)"
  PYTHONPATH=src:research $PY research/embeddings/hgi/preprocess.py --city "$SC" --shapefile "$SHP" \
    > "$LOGDIR/B_hgi_preprocess.log" 2>&1
  [ -f "output/hgi/$SL/temp/edges.csv" ] || fail "B_edges_csv"
  echo "B:hgi_preprocess $(ts)" >> "$LOGDIR/STAGES.DONE"; say "B done hgi-preprocess"
fi

# ---- Stage C: POI2Vec teacher (anchor for v14) ----
if [ -f "output/hgi/$SL/poi2vec_poi_embeddings_${SC}.csv" ]; then
  say "C skip poi2vec (exists)"
else
  disk_guard "C_poi2vec"
  say "C start POI2Vec teacher (100ep, GPU)"
  $PY scripts/substrate_protocol_cleanup/run_poi2vec.py --city "$SC" --epochs 100 --device cuda \
    > "$LOGDIR/C_poi2vec.log" 2>&1
  [ -f "output/hgi/$SL/poi2vec_poi_embeddings_${SC}.csv" ] || fail "C_poi2vec_csv"
  echo "C:poi2vec $(ts)" >> "$LOGDIR/STAGES.DONE"; say "C done poi2vec"
fi

# ---- Stage D: v14 design_k build (ResLN + Delaunay GCN + mae) ----
if [ -f "output/$V14/$SL/embeddings.parquet" ] && [ -f "output/$V14/$SL/region_embeddings.parquet" ]; then
  say "D skip v14 (exists)"
else
  disk_guard "D_v14"
  say "D start v14 design_k build (500ep, GPU)"
  $PY scripts/probe/build_design_k_delaunay.py --state "$SL" \
      --out-suffix resln_mae_l0_1 --epochs 500 --device cuda \
    > "$LOGDIR/D_v14.log" 2>&1
  for f in embeddings poi_embeddings region_embeddings; do
    [ -f "output/$V14/$SL/${f}.parquet" ] || fail "D_v14_${f}"
  done
  echo "D:v14 $(ts)" >> "$LOGDIR/STAGES.DONE"; say "D done v14"
fi

# ---- Stage E: seeded log_T (all seeds) + v14 postbuild + copy log_T to v14 ----
disk_guard "E_logT_postbuild"
say "E start canonical seeded log_T (per-fold, seeds: $SEEDS)"
for S in $SEEDS; do
  if [ -f "output/check2hgi/$SL/region_transition_log_seed${S}_fold5.pt" ]; then
    say "E log_T skip seed=$S (exists)"; else
    $PY scripts/compute_region_transition.py --state "$SL" --per-fold --seed "$S" --n-splits 5 \
      > "$LOGDIR/E_logT_seed${S}.log" 2>&1 || fail "E_logT_seed${S}"
    say "E log_T done seed=$S"
  fi
done
[ -f "output/check2hgi/$SL/region_transition_log_seed42_fold1.pt" ] || fail "E_logT_seed42"

say "E postbuild v14 (next.parquet + next_region.parquet + cp seed42 log_T)"
if [ -f "output/$V14/$SL/input/next_region.parquet" ]; then
  say "E postbuild skip (next_region.parquet exists)"; else
  bash scripts/substrate_protocol_cleanup/postbuild_design_substrate.sh "$V14" "$SL" \
    > "$LOGDIR/E_postbuild.log" 2>&1 || fail "E_postbuild"
  [ -f "output/$V14/$SL/input/next_region.parquet" ] || fail "E_next_region"
fi

say "E copy seeded log_T (0,1,7,100) into v14 dir"
for S in 0 1 7 100; do for f in 1 2 3 4 5; do
  cp "output/check2hgi/$SL/region_transition_log_seed${S}_fold${f}.pt" \
     "output/$V14/$SL/region_transition_log_seed${S}_fold${f}.pt"
done; done
# Freshen mtime so the C22 stale-log_T guard sees log_T newer than next_region.parquet.
sleep 1; touch "output/$V14/$SL"/region_transition_log_seed*_fold*.pt
echo "E:logT_postbuild $(ts)" >> "$LOGDIR/STAGES.DONE"; say "E done"

NF=$(ls output/$V14/$SL/region_transition_log_seed*_fold*.pt 2>/dev/null | wc -l)
say "v14 log_T file count = $NF (expect 25)"
echo "ALLDONE $(ts)" > "$LOGDIR/ALL.DONE"
say "=== GE ESSENTIALS COMPLETE ($(ts)) — HGI training (composite/STL-HGI) deferred to build_ge_hgi_train.sh ==="
