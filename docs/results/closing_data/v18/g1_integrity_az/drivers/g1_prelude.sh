#!/usr/bin/env bash
# usage: g1_prelude.sh <state>  -- once-per-state FULL arms in the AL clone: FULL_CPU category (seed 42, CPU) + FULL_CPU_S0 region (seed 0, CPU)
set -u; C="/Volumes/Vitor's SSD/ingred_g1"; cd "$C"; G="$C/g1_logs/g1_run.sh"; ST=$1; R=results/integ18_repr/$ST
export PYTHONPATH="$C/src:$C/research:$C/scripts:$C" MTL_RAM_HEADROOM_GB=4
ok(){ grep -q "^rc=0" "$C/g1_logs/$1/RUN.txt" && ! [ -e "$C/g1_logs/$1/ABORTED" ] && grep -q "guard OK" "$C/g1_logs/$1/RUN.txt" || { echo "STEP FAIL $1"; exit 1; }; }
D=output/check2hgi_v18_fullcpu/$ST
for p in "$R/FULL_CPU" "$D" "output/check2hgi_design_k_resln_mae_l0_1_fullcpu_s0/$ST"; do [ -e "$p" ] && { echo "A3 FAIL exists $p"; exit 1; }; done
"$G" ${ST}_full_build .venv/bin/python scripts/integrity_v2/build_study_repr.py --state $ST --cell FULL_CPU --repr-seed 42 --epochs 500 --device cpu --encoder resln --forward-only --add-continuous-time --study-root results/integ18_repr; ok ${ST}_full_build
"$G" ${ST}_full_infer .venv/bin/python scripts/integrity_v2/infer_checkins.py --state $ST --checkpoint $R/FULL_CPU/checkpoint.pt --readout prefix_forward_only --out $R/FULL_CPU/win_matched.npz --self-test; ok ${ST}_full_infer
.venv/bin/python scripts/integrity_v2/materialize_engine.py --state $ST --arm-npz $R/FULL_CPU/win_matched.npz --source-engine check2hgi_dk_ovl --dest-engine check2hgi_v18_fullcpu >> g1_logs/ASSERTS_${ST}.log 2>&1 || exit 1
mkdir -p $D/temp; cp output/check2hgi_dk_ovl/$ST/temp/sequences_next.parquet $D/temp/
ln -s "$C/output/check2hgi_design_k_resln_mae_l0_1/$ST/region_embeddings.parquet" $D/region_embeddings.parquet
.venv/bin/python - $ST <<'PY' >> g1_logs/ASSERTS_${ST}.log 2>&1 || { echo "FULL check FAIL"; exit 1; }
import sys, json, pandas as pd; st = sys.argv[1]
b = json.load(open(f"results/integ18_repr/{st}/FULL_CPU/build.json")); assert b["training_users"]["n_excluded_users"] == 0 and b["graph"]["restricted"] is False and b["epochs"] == 500
m = json.load(open(f"output/check2hgi_v18_fullcpu/{st}/materialize.json"))
d = pd.read_parquet(f"output/check2hgi_v18/{st}/input/next.parquet", columns=["userid", "next_category"])
x = pd.read_parquet(f"output/check2hgi_v18_fullcpu/{st}/input/next.parquet", columns=["userid", "next_category"])
assert m["n_windows"] == m["n_windows_source"] == len(d) and (x.userid.astype("int64").values == d.userid.astype("int64").values).all() and (x.next_category.values == d.next_category.values).all()
print(f"FULL_CPU {st} OK: unrestricted build, n_windows={m['n_windows']}, rows/labels equal to delivered v18, best_epoch={b['best_epoch']}")
PY
"$G" ${ST}_full_s0_regbuild .venv/bin/python scripts/probe/build_design_k_delaunay.py --state $ST --seed 0 --device cpu --epochs 500 --out-suffix resln_mae_l0_1_fullcpu_s0; ok ${ST}_full_s0_regbuild
echo "PRELUDE DONE $ST $(date '+%F %T')"
