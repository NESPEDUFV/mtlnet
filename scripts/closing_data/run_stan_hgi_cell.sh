#!/bin/bash
# Blocker 4 Phase 1 — STAN-stl_hgi re-footed to the board (seed 0, stride-1 overlap, HGI substrate).
# Mirrors the board STL reg-ceiling recipe (h100 Cell 2 -> region_head_<state>_..._ovl_stl_reg_s0.json),
# swapping only: head next_stan_flow -> next_stan, region-emb-source V14 -> hgi. next_stan uses an ALiBi
# recency prior (NOT the log_T transition prior), so --per-fold-transition-dir is omitted (also lets CA run
# without a log_T rebuild). Overlap windowing + region labels come from --engine-override check2hgi_dk_ovl;
# embeddings from --region-emb-source hgi.
#
# Usage: run_stan_hgi_cell.sh <state>
set -uo pipefail
REPO=/home/vitor.oliveira/PoiMtlNet; cd "$REPO"
export PYTHONPATH=src
export DISABLE_AMP=1 MTL_DISABLE_AMP=1                 # board fp32 gate
export PYTORCH_CUDA_ALLOC_CONF="expandable_segments:True"
export TORCHINDUCTOR_CACHE_DIR=$HOME/.inductor_cache_board
export P1_S2_AUTO_BUDGET_GB=10                         # chunked val metric -> no OOM at large-C overlap (FL/CA/TX)
export OMP_NUM_THREADS=8
PY=.venv/bin/python

ST="${1:?usage: run_stan_hgi_cell.sh <state>}"
EP=50; F=5; SD=0
L=/tmp/stan_hgi/$ST; mkdir -p "$L"
say(){ echo "[$(date '+%F %T')] [$ST] $*"; }

# MTL reg @10 board thresholds (gate: STAN-HGI must land below these)
declare -A MTL=( [alabama]=69.81 [arizona]=59.34 [florida]=77.28 [california]=65.66 [texas]=67.02 )

say "STAN-HGI region-STL on check2hgi_dk_ovl (next_stan, region-emb hgi), seed $SD, 5f/50ep, compile+tf32, fp32"
$PY -u scripts/p1_region_head_ablation.py \
    --state "$ST" --heads next_stan --folds "$F" --epochs "$EP" --seed "$SD" \
    --input-type region --region-emb-source hgi \
    --engine-override check2hgi_dk_ovl \
    --target region --compile --tf32 \
    --tag "STAN_HGI_OVL_${ST}_5f50ep_s0" > "$L/stan.log" 2>&1
rc=$?; [ $rc -ne 0 ] && { say "FAIL rc=$rc"; tail -25 "$L/stan.log"; exit $rc; }

RD="docs/results/P1/region_head_${ST}_region_5f_50ep_STAN_HGI_OVL_${ST}_5f50ep_s0.json"
$PY - "$ST" "$RD" "${MTL[$ST]:-0}" <<'PY'
import sys, json
from pathlib import Path
st, rd, thr = sys.argv[1], sys.argv[2], float(sys.argv[3])
d = json.load(open(rd))
h = d["heads"]["next_stan"]
agg = h["aggregate"]
acc10 = agg["top10_acc_mean"] * 100.0
std = agg.get("top10_acc_std", 0.0) * 100.0
pf = [round(f.get("top10_acc", f.get("acc10", 0))*100, 2) for f in h.get("per_fold", [])]
eps = [f.get("best_epoch") for f in h.get("per_fold", [])]
gate = "OK (STAN < MTL)" if acc10 < thr else "FAIL (STAN >= MTL!)"
out = {
  "state": st, "baseline": "STAN_stl_hgi_board_refooted", "head": "next_stan",
  "footing": "seed 0, stride-1 overlap (check2hgi_dk_ovl), HGI region-emb, fp32, compile+tf32",
  "stan_hgi_acc10_mean": round(acc10, 4), "stan_hgi_acc10_std": round(std, 4),
  "stan_hgi_acc10_per_fold": pf, "best_epochs": eps,
  "mtl_reg_acc10_board": thr, "gate_stan_below_mtl": gate, "source_json": rd,
}
dst = Path("docs/results/closing_data/baseline_compare")/f"{st}_stan_hgi_ovl_s0.json"
dst.parent.mkdir(parents=True, exist_ok=True)
dst.write_text(json.dumps(out, indent=2))
print(f"[stan-hgi] {st}: Acc@10 {acc10:.2f} ±{std:.2f}  vs MTL reg {thr}  -> {gate}  ({dst})")
PY
say "CELL COMPLETE"
