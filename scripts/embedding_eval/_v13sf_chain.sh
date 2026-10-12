#!/usr/bin/env bash
set -e
cd /home/vitor.oliveira/PoiMtlNet
ENG=check2hgi_resln_design_b_sidefeat
OUT=output/$ENG/florida/region_embeddings.parquet
LOG=docs/results/embedding_eval/v13_sidefeat
# wait for build to finish writing region embeddings
while ! grep -q "wrote region_embeddings.parquet" "$LOG/build_fl.log" 2>/dev/null; do
  sleep 30
done
echo "[chain] build done; launching L2 region ablation" >> "$LOG/chain.log"
.venv/bin/python scripts/p1_region_head_ablation.py --state florida \
  --heads next_stan_flow --input-type region --region-emb-source $ENG \
  --folds 5 --epochs 50 --seed 42 --tag ${ENG}_v13sf \
  >> "$LOG/l2_fl.log" 2>&1
echo "[chain] L2 ablation done" >> "$LOG/chain.log"
