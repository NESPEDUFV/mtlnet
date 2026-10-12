#!/usr/bin/env bash
# Build the stackable re-screen candidates on the ResLN encoder base (v13 encoder),
# then L0-screen vs check2hgi_resln. Waits for the GPU (MTL head-to-head) to clear.
# gat/rgcn excluded (encoder-level swaps, leak-disqualified). Design-B POI2Vec
# injection NOT included (separate build path build_design_b_poi_pool.py).
set -u
cd "$(dirname "$0")/../.."
PY=.venv/bin/python; LD=docs/results/embedding_eval/l2l3/logs; ER=docs/results/embedding_eval

echo "### wait for GPU (MTL head-to-head) to clear @ $(date +%H:%M:%S)"
while ps aux | grep -qE '[t]rain.py|[r]egen_emb'; do sleep 30; done
sleep 3; echo "### GPU clear @ $(date +%H:%M:%S)"

flags_for() { case "$1" in
  check2hgi_resln_v3c)      echo "--encoder resln --weight-decay 0.05";;
  check2hgi_resln_dropedge) echo "--encoder resln --drop-edge-rate 0.1 --symmetric-drop-edge";;
  check2hgi_resln_sidefeat) echo "--encoder resln --use-side-features --side-features-subset no_covisit";;
  check2hgi_resln_p2p)      echo "--encoder resln --p2p-lambda 0.3";;
esac; }
CANDS="check2hgi_resln_v3c check2hgi_resln_dropedge check2hgi_resln_sidefeat check2hgi_resln_p2p"

echo "### [0] build candidates on ResLN base (FL) @ $(date +%H:%M:%S)"
for v in $CANDS; do
  [ -f "output/$v/florida/embeddings.parquet" ] && { echo "  skip $v"; continue; }
  bash scripts/embedding_eval/rescreen_build.sh "$v" florida 500 -- $(flags_for "$v") \
    && echo "  OK build $v" || echo "  FAIL build $v"
done

echo "### [1] generate next-cat inputs @ $(date +%H:%M:%S)"
for v in $CANDS; do
  [ -f "output/$v/florida/input/next.parquet" ] && continue
  $PY -c "import sys; sys.path[:0]=['src']; from data.inputs.builders import generate_next_input_from_checkins as g; from configs.paths import EmbeddingEngine as E; g('florida', E('$v'))" \
    && echo "  OK inputs $v" || echo "  FAIL inputs $v"
done

echo "### [2] L0 screen vs check2hgi_resln base @ $(date +%H:%M:%S)"
ALL="check2hgi_resln $CANDS"
$PY scripts/embedding_eval/run.py --engines $ALL --states florida --tasks cat \
  --ref-engine check2hgi_resln --out $ER/fl_resln_cands
$PY scripts/embedding_eval/region_eval.py --engines $ALL --state florida 2>/dev/null \
  | grep -vi warning > $ER/region_eval/florida_resln_cands.txt
$PY scripts/embedding_eval/leak_sniff.py --engines $ALL --state florida --control check2hgi_resln \
  --out $ER/rescreen_cat/leak_sniff_resln_fl.csv > $LD/leak_resln_fl.log 2>&1
echo "### RESLN CANDIDATES CAMPAIGN DONE @ $(date +%H:%M:%S)"
