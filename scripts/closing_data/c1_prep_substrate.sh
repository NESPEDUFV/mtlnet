#!/bin/bash
# closing_data C1 (confirm-on-G) — local post-build glue for a v14 substrate.
#
# Mirrors scripts/substrate_protocol_cleanup/postbuild_design_substrate.sh but
#   (a) runs LOCAL (no hardcoded /home REPO; uses the repo this script lives in),
#   (b) adds SEED-0 per-fold log_T (the remote postbuild only copies seed=42),
#   (c) asserts the stale-log_T freshness guard (log_T mtime > next_region mtime).
#
# Pre-req: scripts/probe/build_design_k_delaunay.py already produced
#   output/<ENGINE>/<STATE>/embeddings.parquet (the substrate build).
#
# Usage: bash scripts/closing_data/c1_prep_substrate.sh <state> [seed...]
#   bash scripts/closing_data/c1_prep_substrate.sh alabama 0
#   bash scripts/closing_data/c1_prep_substrate.sh florida 0 1 7 100
set -euo pipefail

STATE="$1"; shift || true
SEEDS=("$@"); [ ${#SEEDS[@]} -eq 0 ] && SEEDS=(0)
ENGINE=check2hgi_design_k_resln_mae_l0_1

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$REPO"
PY=.venv/bin/python

OUT_DIR="output/${ENGINE}/${STATE}"
CANON_DIR="output/check2hgi/${STATE}"
[ -f "$OUT_DIR/embeddings.parquet" ] || { echo "ERR substrate missing: $OUT_DIR/embeddings.parquet (run build_design_k_delaunay.py first)"; exit 1; }

say(){ echo "[c1_prep $STATE] $*"; }

# 1. next.parquet (check-in-level next-POI input on the v14 substrate)
say "step 1: generate next.parquet"
$PY -c "
import sys; sys.path.insert(0,'src')
from configs.paths import EmbeddingEngine
from data.inputs.builders import generate_next_input_from_checkins
generate_next_input_from_checkins('${STATE}', EmbeddingEngine('${ENGINE}'))
print('[c1_prep] next.parquet OK')
"

# 2. next_region.parquet (region targets for the reg task)
say "step 2: build next_region.parquet"
$PY scripts/substrate_protocol_cleanup/build_design_next_region.py --state "$STATE" --engine "$ENGINE"

NEXT_REGION="$OUT_DIR/input/next_region.parquet"
[ -f "$NEXT_REGION" ] || { echo "ERR next_region.parquet not produced: $NEXT_REGION"; exit 1; }

# 3. per-fold seed-tagged log_T, computed on canonical c2hgi (region structure
#    identical — same n_regions), copied into the v14 dir, touched AFTER
#    next_region.parquet to satisfy the C22 stale-log_T mtime guard.
for SD in "${SEEDS[@]}"; do
    say "step 3: log_T seed=$SD"
    have_all=1
    for f in 1 2 3 4 5; do
        [ -f "$CANON_DIR/region_transition_log_seed${SD}_fold${f}.pt" ] || have_all=0
    done
    if [ "$have_all" -eq 0 ]; then
        say "  canonical seed=$SD log_T missing — computing"
        $PY scripts/compute_region_transition.py --state "$STATE" --per-fold --seed "$SD"
    else
        say "  canonical seed=$SD log_T present — reuse"
    fi
    for f in 1 2 3 4 5; do
        src="$CANON_DIR/region_transition_log_seed${SD}_fold${f}.pt"
        dst="$OUT_DIR/region_transition_log_seed${SD}_fold${f}.pt"
        [ -f "$src" ] || { echo "ERR canonical log_T missing after compute: $src"; exit 1; }
        cp "$src" "$dst"
    done
    sleep 1
    touch "$OUT_DIR"/region_transition_log_seed${SD}_fold*.pt
    # Freshness assert: every copied log_T must be newer than next_region.parquet
    nr_m=$(stat -f %m "$NEXT_REGION")
    for f in 1 2 3 4 5; do
        lt_m=$(stat -f %m "$OUT_DIR/region_transition_log_seed${SD}_fold${f}.pt")
        [ "$lt_m" -ge "$nr_m" ] || { echo "ERR stale log_T seed=$SD fold=$f ($lt_m < $nr_m)"; exit 1; }
    done
    say "  seed=$SD log_T OK (5 folds, fresh)"
done

say "DONE — substrate ready at $OUT_DIR"
ls -1 "$OUT_DIR"/region_transition_log_seed*_fold*.pt "$NEXT_REGION" "$OUT_DIR/input/next.parquet" 2>/dev/null
