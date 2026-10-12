#!/bin/bash
# Patient retry of the frozen-v14 Drive download (rate-limit cools down between tries).
cd /teamspace/studios/this_studio/PoiMtlNet
FID=137RBPqNgqcKQKy04K7G0NslaYnxSFfuz
OUT=output/_frozen_v14_dl/check2hgi_design_k_resln_mae_l0_1
for i in $(seq 1 40); do
  echo "[$(date '+%F %T')] attempt $i"
  gdown --folder "https://drive.google.com/drive/folders/$FID" -O "$OUT" --continue 2>&1 | tail -3
  # success check: FL + CA embeddings present and > 100MB
  fl=$(stat -c%s "$OUT/florida/embeddings.parquet" 2>/dev/null || echo 0)
  ca=$(stat -c%s "$OUT/california/embeddings.parquet" 2>/dev/null || echo 0)
  if [ "$fl" -gt 100000000 ] && [ "$ca" -gt 100000000 ]; then
    echo "[$(date '+%F %T')] SUCCESS: FL=$fl CA=$ca bytes"; exit 0
  fi
  echo "[$(date '+%F %T')] incomplete (FL=$fl CA=$ca), sleeping 300s"; sleep 300
done
echo "gave up after 40 attempts"
