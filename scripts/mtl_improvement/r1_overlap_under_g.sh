#!/bin/bash
# R1 (Tier 3) — overlap-under-G: does G's PRIVATE reg tower absorb the dense-supervision
# lift the SHARED backbone wasted? The prior overlap MTL run (2026-06-03) was OLD-regime
# (class-weighted, shared next_stan reg) → STL reg lift +5.13 but MTL reg lift only +0.50
# (gap WIDENED). R1 re-runs the SAME windowing contrast under champion G (dual-tower,
# post-C25 unweighted). Clean seed-42 paired 2×2 in the CURRENT harness:
#   {non-overlap v14, overlap dk_ovl} × {STL reg ceiling (p1 α0), champion G}
# Reg scored matched-metric: G-full = indist*(1-ood) (R0 method); ceiling = p1 full top10_acc.
# Mechanism gate: does ΔG−ceiling change between non-overlap and overlap?
#   CONC=1 setsid bash scripts/mtl_improvement/r1_overlap_under_g.sh > /tmp/r1/run.log 2>&1 &
set -uo pipefail
REPO=/home/vitor.oliveira/PoiMtlNet; cd "$REPO"; export PYTHONPATH=src
PY=.venv/bin/python
V14=check2hgi_design_k_resln_mae_l0_1; OVL=check2hgi_dk_ovl
ST=alabama; SD=42; EPOCHS=50
LOGDIR=/tmp/r1; mkdir -p "$LOGDIR"
MAN=scripts/mtl_improvement/r1_overlap_manifest.tsv; [ -f "$MAN" ] || : > "$MAN"
export OMP_NUM_THREADS=24
ts(){ date '+%Y-%m-%d %H:%M:%S'; }; say(){ echo "[$(ts)] R1 $*"; }
A0="freeze_alpha=True alpha_init=0.0"

# --- STL reg ceiling (p1, next_stan_flow α=0) — eng selects WINDOWING via --engine-override ---
ceil_run(){ local regime=$1 eng_override=$2; local key="ceil|${regime}"
  grep -qF "$key	" "$MAN" && { say "skip $key"; return 0; }
  local tag="r1_ceil_${regime}_${ST}_s${SD}"; local log="$LOGDIR/${key//|/_}.log"; say "start $key"
  local eo=(); [ -n "$eng_override" ] && eo=(--engine-override "$eng_override")
  $PY scripts/p1_region_head_ablation.py --state "$ST" --heads next_stan_flow \
      --input-type region --region-emb-source "$V14" --override-hparams $A0 \
      --folds 5 --epochs "$EPOCHS" --batch-size 2048 --seed "$SD" --target region --tag "$tag" \
      "${eo[@]}" --per-fold-transition-dir "output/check2hgi/$ST" > "$log" 2>&1 \
    && { printf '%s\tceil\tdocs/results/P1/region_head_%s_region_5f_50ep_%s.json\n' "$key" "$ST" "$tag" >>"$MAN"; say "done $key"; } \
    || { say "FAIL $key — see $log"; return 1; }
}

# --- champion G (dual-tower aux prior-OFF) — --engine selects the substrate/windowing ---
g_run(){ local regime=$1 engine=$2; local key="g|${regime}"
  grep -qF "$key	" "$MAN" && { say "skip $key"; return 0; }
  local log="$LOGDIR/${key//|/_}.log"; say "start $key (engine=$engine)"
  $PY scripts/train.py --task mtl --task-set check2hgi_next_region --engine "$engine" \
      --state "$ST" --seed "$SD" --epochs "$EPOCHS" --folds 5 --batch-size 2048 \
      --mtl-loss static_weight --category-weight 0.75 \
      --cat-head next_gru --reg-head next_stan_flow_dualtower \
      --reg-head-param raw_embed_dim=64 --reg-head-param fusion_mode=aux \
      --reg-head-param freeze_alpha=True --reg-head-param alpha_init=0.0 \
      --task-a-input-type checkin --task-b-input-type region --log-t-kd-weight 0.0 \
      --scheduler onecycle --max-lr 3e-3 --cat-lr 1e-3 --reg-lr 3e-3 --shared-lr 1e-3 \
      --model mtlnet_crossattn_dualtower \
      --per-fold-transition-dir "output/$V14/$ST" --no-checkpoints > "$log" 2>&1 &
  local pid=$!; wait "$pid"
  if [ $? -eq 0 ]; then
    local rd; rd=$(ls -d results/$engine/$ST/mtlnet_*ep${EPOCHS}_*_${pid} 2>/dev/null | head -1)
    [ -z "$rd" ] && rd=$(ls -dt results/$engine/$ST/mtlnet_*ep${EPOCHS}_* 2>/dev/null | head -1)
    printf '%s\tg\t%s\n' "$key" "$rd" >>"$MAN"; say "done $key -> $rd"
  else say "FAIL $key — see $log"; return 1; fi
}

say "=== R1 overlap-under-G: AL seed42 paired 2x2 (current harness) ==="
ceil_run nonoverlap ""        # STL reg ceiling, non-overlap (v14 windowing)
ceil_run overlap   "$OVL"     # STL reg ceiling, overlap (dk_ovl windowing)
g_run    nonoverlap "$V14"    # champion G, non-overlap
g_run    overlap    "$OVL"    # champion G, overlap
say "ALL DONE"
