#!/usr/bin/env bash
# G1 Florida once-per-state FULL arms, RESUMABLE: FULL_CPU category (seed 42, CPU) + FULL_CPU_S0 region (design_k seed 0, CPU)
set -u; C="/Volumes/Vitor's SSD/ingred_g1fl"; cd "$C"; G="$C/g1_logs/g1_run.sh"; source "$C/g1_logs/g1_lib.sh"; ST=florida; R=results/integ18_repr/$ST
export G1_HEAVY=1; export PYTHONPATH="$C/src:$C/research:$C/scripts:$C" MTL_RAM_HEADROOM_GB=4
D=output/check2hgi_v18_fullcpu/$ST
step fl_full_build - .venv/bin/python scripts/integrity_v2/build_study_repr.py --state $ST --cell FULL_CPU --repr-seed 42 --epochs 500 --device cpu --encoder resln --forward-only --add-continuous-time --study-root results/integ18_repr
step fl_full_infer - .venv/bin/python scripts/integrity_v2/infer_checkins.py --state $ST --checkpoint $R/FULL_CPU/checkpoint.pt --readout prefix_forward_only --out $R/FULL_CPU/win_matched.npz --self-test
step fl_full_mat - .venv/bin/python scripts/integrity_v2/materialize_engine.py --state $ST --arm-npz $R/FULL_CPU/win_matched.npz --source-engine check2hgi_dk_ovl_srcview --dest-engine check2hgi_v18_fullcpu
mkdir -p $D/temp; cp output/check2hgi_dk_ovl/$ST/temp/sequences_next.parquet $D/temp/
ln -sfn "$C/output/check2hgi_dk_ovl/$ST/input/next_region.parquet" $D/input/next_region.parquet
ln -sfn "$C/output/check2hgi_design_k_resln_mae_l0_1/$ST/region_embeddings.parquet" $D/region_embeddings.parquet
.venv/bin/python - <<'PY' >> g1_logs/ASSERTS_florida.log 2>&1 || { echo "FULL identity FAIL"; exit 1; }
import json, numpy as np, pandas as pd
from pathlib import Path
from integrity_v2.materialize_engine import load_arm
b = json.load(open("results/integ18_repr/florida/FULL_CPU/build.json")); assert b["training_users"]["n_excluded_users"] == 0 and b["graph"]["restricted"] is False and b["epochs"] == 500
m = json.load(open("output/check2hgi_v18_fullcpu/florida/materialize.json"))
d = pd.read_parquet("output/check2hgi_dk_ovl/florida/input/next.parquet", columns=["userid", "next_category"])
x = pd.read_parquet("output/check2hgi_v18_fullcpu/florida/input/next.parquet", columns=["userid", "next_category"])
assert m["n_windows"] == m["n_windows_source"] == len(d) and (x.userid.astype("int64").values == d.userid.astype("int64").values).all() and (x.next_category.values == d.next_category.values).all()
_, rows = load_arm(Path("results/integ18_repr/florida/FULL_CPU/win_matched.npz"), d); assert (rows == np.arange(len(d))).all(), "rows not identity"
print(f"FULL_CPU florida OK: build unrestricted, n_windows={m['n_windows']} rows == arange vs dk_ovl, best_epoch={b['best_epoch']}")
PY
step fl_full_s0_regbuild - .venv/bin/python scripts/probe/build_design_k_delaunay.py --state $ST --seed 0 --device cpu --epochs 500 --out-suffix resln_mae_l0_1_fullcpu_s0
echo "PRELUDE DONE $(date '+%F %T')"
