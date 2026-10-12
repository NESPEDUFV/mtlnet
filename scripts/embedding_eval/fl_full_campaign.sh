#!/usr/bin/env bash
# Full FL L0->L2 campaign for the 5 re-screen candidates (+ gcn control).
# Builds the 3 missing FL variants, generates next-cat inputs, then screens
# L0/L1 (cat+reg) and runs L2 (next-cat STL + next-reg STL).
set -u
cd "$(dirname "$0")/../.."
PY=.venv/bin/python; LD=docs/results/embedding_eval/l2l3/logs; ER=docs/results/embedding_eval
mkdir -p "$LD"
CANDS="check2hgi_v3c_wd05 check2hgi_t24_dropedge check2hgi_t43_sidefeat check2hgi_gat check2hgi_rgcn check2hgi_t61_p2p"
ALL="check2hgi check2hgi_gcn_ctrl $CANDS"          # + frozen ref + control
L2SET="check2hgi_gcn_ctrl $CANDS"                  # control + candidates for L2

flags_for() { case "$1" in
  check2hgi_gcn_ctrl)     echo "--encoder gcn --weight-decay 0.0";;
  check2hgi_v3c_wd05)     echo "--encoder gcn --weight-decay 0.05";;
  check2hgi_t24_dropedge) echo "--encoder gcn --drop-edge-rate 0.1 --symmetric-drop-edge";;
  check2hgi_t43_sidefeat) echo "--encoder gcn --use-side-features --side-features-subset no_covisit";;
  check2hgi_gat)          echo "--encoder gat";;
  check2hgi_rgcn)         echo "--encoder rgcn --edge-type both";;
  check2hgi_t61_p2p)      echo "--encoder gcn --p2p-lambda 0.3";;
esac; }

echo "### [0] build missing FL variants @ $(date +%H:%M:%S)"
for v in check2hgi_t24_dropedge check2hgi_gat check2hgi_t61_p2p; do
  [ -f "output/$v/florida/embeddings.parquet" ] && { echo "  skip $v (built)"; continue; }
  bash scripts/embedding_eval/rescreen_build.sh "$v" florida 500 -- $(flags_for "$v") \
    && echo "  OK build $v" || echo "  FAIL build $v"
done

echo "### [1] generate next-cat inputs for all variants @ $(date +%H:%M:%S)"
for v in check2hgi_gcn_ctrl $CANDS; do
  [ -f "output/$v/florida/input/next.parquet" ] && { echo "  skip inputs $v"; continue; }
  $PY -c "import sys; sys.path[:0]=['src']; from data.inputs.builders import generate_next_input_from_checkins as g; from configs.paths import EmbeddingEngine as E; g('florida', E('$v'))" \
    && echo "  OK inputs $v" || echo "  FAIL inputs $v"
done

echo "### [2] L0/L1 FL (cat run.py + reg region_eval) @ $(date +%H:%M:%S)"
$PY scripts/embedding_eval/run.py --engines $ALL --states florida --tasks cat \
  --ref-engine check2hgi_gcn_ctrl --out $ER/fl_rescreen
$PY scripts/embedding_eval/region_eval.py --engines $ALL --state florida 2>/dev/null \
  | grep -vi warning > $ER/region_eval/florida_rescreen_full.txt

echo "### [3] L2 next-cat FL (train.py --task next) @ $(date +%H:%M:%S)"
for v in $L2SET; do
  $PY scripts/train.py --task next --state florida --engine "$v" --seed 42 \
    --epochs 50 --folds 5 --batch-size 2048 --model next_gru --max-lr 0.01 --no-checkpoints \
    > $LD/l2cat_${v}_florida.log 2>&1 && echo "  OK L2cat $v" || echo "  FAIL L2cat $v"
done

echo "### [4] L2 next-reg FL (p1) for the not-yet-done @ $(date +%H:%M:%S)"
for v in check2hgi_v3c_wd05 check2hgi_t24_dropedge check2hgi_gat check2hgi_t61_p2p; do
  [ -f "$LD/l2reg_${v}_florida.log" ] && grep -q AGGREGATE "$LD/l2reg_${v}_florida.log" && { echo "  skip L2reg $v"; continue; }
  $PY scripts/p1_region_head_ablation.py --state florida --heads next_stan_flow \
    --input-type region --region-emb-source "$v" --folds 5 --epochs 50 --seed 42 --tag "$v" \
    > $LD/l2reg_${v}_florida.log 2>&1 && echo "  OK L2reg $v" || echo "  FAIL L2reg $v"
done
echo "### FL FULL CAMPAIGN DONE @ $(date +%H:%M:%S)"
