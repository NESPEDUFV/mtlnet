#!/bin/bash
# =============================================================================
# P3 BOARD DRIVER — the ONE sanctioned build+run path for the P3 board.
# =============================================================================
#
#   ┌───────────────────────────────────────────────────────────────────────┐
#   │  THIS SCRIPT IS THE ONLY SANCTIONED P3-BOARD PATH.                      │
#   │                                                                        │
#   │  The four P3-board values live HERE and NOWHERE ELSE:                  │
#   │      • stride        = 1   (fully overlapping windows, GATED)          │
#   │      • min_seq       = 10  (MIN_SEQUENCE_LENGTH override)              │
#   │      • --compile     (torch.compile, inductor)                         │
#   │      • --tf32        (TF32 matmul)                                     │
#   │                                                                        │
#   │  They are NOT global defaults. Every OTHER build/run path is FROZEN at │
#   │  stride=9 (non-overlap) / min_seq=5 / no-compile / no-tf32, producing │
#   │  byte-identical output to the v11/v14 substrates + the §0.1 numbers.   │
#   │  The recipe itself is already the default (canon v16); this driver     │
#   │  applies the windowing + perf knobs uniformly across all cells.        │
#   └───────────────────────────────────────────────────────────────────────┘
#
# OVERLAP-ENGINE ISOLATION (the whole point — the frozen v14 substrate is NEVER
# touched):
#   The stride-1 / min_seq=10 windowing is built into a SEPARATE engine dir
#   `check2hgi_dk_ovl` (OVL) via scripts/mtl_improvement/build_overlap_probe_engine.py.
#   That builder:
#     • symlinks the windowing-INDEPENDENT artifacts (embeddings / region / poi)
#       from the frozen v14 dir (identical bytes; never rewritten),
#     • builds the OVL engine's OWN overlapping next.parquet + sequences_next.parquet
#       (stride=1, GATED tail i.e. emit_tail=False at stride==1, min_seq=10),
#     • builds the OVL engine's OWN stride-1 next_region.parquet from those same
#       overlapping sequences (NOT a stride-9 canonical join).
#   The frozen v14 `next.parquet` / `sequences_next.parquet` / `next_region.parquet`
#   are read-only inputs here and stay byte-identical. NEVER clobber them.
#
# What it does, per state:
#   (a) build the OVL overlap engine for the state (reuses the frozen v14 embeddings
#       by symlink; builds the engine's own stride-1 inputs + next_region). The v14
#       substrate is untouched.
#   (b) build the seeded per-fold log_T (canonical region prior — substrate-INDEPENDENT)
#       and STAGE it (copy + touch) into the v14 dir, the dir the trainer reads via
#       --per-fold-transition-dir. Freshness is verified against the OVL engine's
#       stride-1 next_region.parquet (the windowing-matched parquet) — closing the
#       +8..+12pp stale-log_T trap.
#   (c) per (state,seed) in STATES × SEEDS: run train.py on the OVL engine, champion-G
#       (v16) recipe pinned EXPLICITLY (--canon none — see WHY-CANON-NONE below),
#       --compile --tf32, MTL_STRICT=1, with PID-suffix rundir capture (NEVER `ls -dt | head`).
#
# WHY-CANON-NONE: --canon v16 pins the v14 substrate; under MTL_STRICT=1 (which the
#   board sets so the overlap GATE guard is enforced) running v16 against the OVL
#   engine HARD-FAILS the wrong-substrate guard. So we pass `--canon none` and pin the
#   FULL champion-G recipe via explicit flags (model/heads/loss/selector/LRs/KD/
#   modality + the class-weight flags which default to None, not False). The effective
#   config == auto-v16 + engine override → byte-identical to the canon recipe, just on
#   the overlap engine. (Mirrors the validated board PR drivers a40_task1_fl_ab.sh /
#   h100_fl_cells.sh.)
#
# Preflight (refuses to launch otherwise):
#   • torch == 2.11.0+cu128
#   • log_T freshness: every staged region_transition_log_seed{S}_fold{N}.pt mtime
#     must be >= the OVL engine's next_region.parquet mtime.
#
# Usage:
#   bash scripts/closing_data/p3_board.sh --dry-run        # print plan, no exec
#   bash scripts/closing_data/p3_board.sh                  # run all states/seeds
#   bash scripts/closing_data/p3_board.sh --states "alabama florida" --seeds "0 1"
#
# GPU job — do NOT run on CPU-only / review machines. --dry-run is always safe.
# =============================================================================
set -euo pipefail

# ---------------------------------------------------------------------------
# Config (the P3-board constants live HERE)
# ---------------------------------------------------------------------------
V14_ENGINE="check2hgi_design_k_resln_mae_l0_1"   # frozen v14 substrate (NEVER rebuilt / clobbered)
OVL_ENGINE="check2hgi_dk_ovl"                     # overlap (stride-1) probe engine — built per state
STRIDE=1                                           # P3 board: fully overlapping windows (GATED tail)
MIN_SEQ=10                                         # P3 board: MIN_SEQUENCE_LENGTH override
CANON="v16"                                        # champion G recipe (pinned EXPLICITLY; see WHY-CANON-NONE)
REQUIRED_TORCH="2.11.0+cu128"

DEFAULT_STATES=(alabama arizona georgia florida california texas)
DEFAULT_SEEDS=(0 1 7 100)

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$REPO"
export PYTHONPATH="src${PYTHONPATH:+:$PYTHONPATH}"
PY="$REPO/.venv/bin/python"
[ -x "$PY" ] || PY="python3"

# ---------------------------------------------------------------------------
# Board execution environment (perf knobs + per-state device discipline).
# compile + tf32 are passed per-cell; the shared inductor cache is set here so
# every cell reuses the same compiled kernels.
# ---------------------------------------------------------------------------
export MTL_STRICT=1                                # enforce the overlap GATE guard (gated tail required)
export MTL_COMPILE_DYNAMIC=1                        # dynamic-shape inductor (overlap row counts vary)
export TORCHINDUCTOR_CACHE_DIR="${TORCHINDUCTOR_CACHE_DIR:-$HOME/.inductor_cache_board}"
export MTL_CHUNK_VAL_METRIC=1                       # chunk the val-metric logits (large states)
# pipeline_audit 2026-07-01 (V6) — the board precision invariant is fp32 for
# ALL states (bf16 costs ~1pp at large C; fp16 NaN-collapses CA/TX; the fp32
# STL ceilings must be compared at matched precision). This script previously
# set NO precision env: small states silently ran fp16-autocast and large
# states ran auto-fp32-train + fp16-eval (mixed regime). Overridable.
export MTL_DISABLE_AMP="${MTL_DISABLE_AMP:-1}"
export PYTORCH_CUDA_ALLOC_CONF="${PYTORCH_CUDA_ALLOC_CONF:-expandable_segments:True}"
export OMP_NUM_THREADS="${OMP_NUM_THREADS:-24}"
# NEVER set MTL_DATASET_GPU=1 here: CA/TX region-MTL OOMs with redundant GPU copies;
# the auto-fit dataset-device path (folds._dataset_device) is the validated default.
unset MTL_DATASET_GPU 2>/dev/null || true

# ---------------------------------------------------------------------------
# Arg parsing
# ---------------------------------------------------------------------------
DRY_RUN=0
STATES=("${DEFAULT_STATES[@]}")
SEEDS=("${DEFAULT_SEEDS[@]}")
while [ $# -gt 0 ]; do
    case "$1" in
        --dry-run) DRY_RUN=1; shift ;;
        --states)  read -r -a STATES <<< "$2"; shift 2 ;;
        --seeds)   read -r -a SEEDS  <<< "$2"; shift 2 ;;
        -h|--help) grep '^#' "$0" | sed 's/^# \{0,1\}//'; exit 0 ;;
        *) echo "ERR unknown arg: $1 (see --help)"; exit 2 ;;
    esac
done

say(){ echo "[p3_board] $*"; }
hdr(){
    echo "=============================================================================="
    echo "  P3 BOARD — the ONLY sanctioned P3-board build+run path"
    echo "  stride=$STRIDE  min_seq=$MIN_SEQ  --compile  --tf32   (canon $CANON, all cells uniform)"
    echo "  These knobs live in THIS script — they are NOT global defaults."
    echo "  Every other path stays frozen at stride=9 / min_seq=5 / no-compile / no-tf32."
    echo "  overlap engine (built per state, isolated): $OVL_ENGINE"
    echo "  frozen v14 substrate (read-only, NEVER touched): $V14_ENGINE"
    echo "  states: ${STATES[*]}"
    echo "  seeds:  ${SEEDS[*]}"
    [ "$DRY_RUN" -eq 1 ] && echo "  MODE:   DRY-RUN (plan only, no execution)"
    echo "=============================================================================="
}

# ---------------------------------------------------------------------------
# Preflights
# ---------------------------------------------------------------------------
preflight_torch(){
    local got
    got="$("$PY" -c 'import torch; print(torch.__version__)' 2>/dev/null || echo MISSING)"
    if [ "$got" != "$REQUIRED_TORCH" ]; then
        echo "ERR torch version mismatch: have '$got', require '$REQUIRED_TORCH'"
        return 1
    fi
    say "torch $got OK"
}

# mtime helper that works on both GNU (Linux) and BSD (macOS) stat
mtime(){ stat -c %Y "$1" 2>/dev/null || stat -f %m "$1"; }

# Freshness: the staged log_T (in the v14 dir, where the trainer reads it) must be
# NEWER than the OVL engine's stride-1 next_region.parquet (the windowing-matched
# parquet the prior must align with). This is the real stale-log_T guard for the
# board: a log_T built before the overlap next_region was rebuilt would silently
# leak +8..+12pp into reg Acc@10.
preflight_logT_fresh(){
    local state="$1" seed="$2"
    local v14_dir="output/${V14_ENGINE}/${state}"
    local ovl_next_region="output/${OVL_ENGINE}/${state}/input/next_region.parquet"
    [ -f "$ovl_next_region" ] || { echo "ERR OVL next_region missing: $ovl_next_region (build the overlap engine first)"; return 1; }
    local nr_m; nr_m="$(mtime "$ovl_next_region")"
    for f in 1 2 3 4 5; do
        local lt="$v14_dir/region_transition_log_seed${seed}_fold${f}.pt"
        [ -f "$lt" ] || { echo "ERR missing staged log_T $lt"; return 1; }
        [ "$(mtime "$lt")" -ge "$nr_m" ] || { echo "ERR STALE log_T $lt (< OVL next_region)"; return 1; }
    done
    say "log_T freshness OK ($state seed=$seed, 5 folds, vs OVL next_region)"
}

# ---------------------------------------------------------------------------
# Build steps
# ---------------------------------------------------------------------------
# (a) Build the isolated OVL overlap engine for the state. This is the PROVEN
#     builder: it symlinks the frozen v14 embeddings/region/poi (read-only),
#     builds the engine's OWN stride-1 (GATED) next.parquet + sequences, then
#     builds the engine's OWN stride-1 next_region.parquet. The frozen v14
#     next.parquet / sequences_next.parquet / next_region.parquet are NEVER
#     written. min_seq=10 is the builder's board default (argv[2]=stride=1
#     auto-gates emit_tail=False).
build_inputs(){
    local state="$1"
    local v14_dir="output/${V14_ENGINE}/${state}"
    [ -f "$v14_dir/embeddings.parquet" ] || { echo "ERR frozen v14 embeddings missing: $v14_dir/embeddings.parquet (do NOT rebuild — restore from manifest)"; return 1; }
    say "[$state] (a) build OVL overlap engine '$OVL_ENGINE' (stride=$STRIDE, gated tail, min_seq=$MIN_SEQ; v14 untouched)"
    "$PY" scripts/mtl_improvement/build_overlap_probe_engine.py "$state" "$STRIDE" "$MIN_SEQ"
}

# (b) Build the seeded per-fold log_T (canonical region prior — substrate-INDEPENDENT)
#     and STAGE it into the v14 dir (the trainer reads --per-fold-transition-dir there).
#     compute_region_transition.py writes to output/check2hgi/<state>/; we copy + touch
#     into the v14 dir so it is newer than the OVL next_region (freshness guard).
#     Mirrors a40_tx_logt_stage.sh / h100_logt_stage.sh.
build_logT(){
    local state="$1" seed="$2"
    local v14_dir="output/${V14_ENGINE}/${state}"
    local canon_dir="output/check2hgi/${state}"
    say "[$state seed=$seed] (b) build canonical seeded per-fold log_T -> stage into v14 dir (copy+touch)"
    "$PY" scripts/compute_region_transition.py --state "$state" --per-fold --seed "$seed"
    for f in 1 2 3 4 5; do
        cp "$canon_dir/region_transition_log_seed${seed}_fold${f}.pt" \
           "$v14_dir/region_transition_log_seed${seed}_fold${f}.pt" \
           || { echo "ERR cp log_T fold$f ($state seed=$seed)"; return 1; }
    done
    sleep 1
    touch "$v14_dir"/region_transition_log_seed${seed}_fold*.pt
}

# ---------------------------------------------------------------------------
# Train step (PID-suffix rundir capture — NEVER ls -dt | head)
# Champion-G (v16) recipe pinned EXPLICITLY on the OVL engine. --canon none so the
# canon wrong-substrate guard does not hard-fail under MTL_STRICT=1 (see WHY-CANON-NONE
# in the header). Effective config == auto-v16 + engine override.
# ---------------------------------------------------------------------------
run_cell(){
    local state="$1" seed="$2"
    local v14_dir="output/${V14_ENGINE}/${state}"
    local logroot="/tmp/p3_board"; mkdir -p "$logroot"
    local runlog="$logroot/${state}_s${seed}.train.log"
    say "[$state seed=$seed] (c) train.py champion-G ($CANON, explicit) on $OVL_ENGINE --compile --tf32 -> $runlog"
    "$PY" scripts/train.py --task mtl --task-set check2hgi_next_region --engine "$OVL_ENGINE" \
        --state "$state" --seed "$seed" --epochs 50 --folds 5 --batch-size 2048 \
        --mtl-loss static_weight --category-weight 0.75 \
        --cat-head next_gru --reg-head next_stan_flow_dualtower \
        --reg-head-param raw_embed_dim=64 --reg-head-param fusion_mode=aux \
        --reg-head-param freeze_alpha=True --reg-head-param alpha_init=0.0 \
        --task-a-input-type checkin --task-b-input-type region --log-t-kd-weight 0.0 \
        --scheduler onecycle --max-lr 3e-3 --cat-lr 1e-3 --reg-lr 3e-3 --shared-lr 1e-3 \
        --model mtlnet_crossattn_dualtower \
        --checkpoint-selector geom_simple --no-reg-class-weights --no-cat-class-weights \
        --canon none \
        --compile --tf32 \
        --per-fold-transition-dir "$v14_dir" \
        > "$runlog" 2>&1 &
    local pid=$!
    say "[$state seed=$seed] launched PID=$pid; rundir captured by PID suffix (mtlnet_..._${pid})"
    wait "$pid"
    # PID-suffix rundir (C28): train.py names the rundir mtlnet_..._{PID}; resolve by suffix.
    # The per-cell result JSONs (fold*_info.json, classification reports) live in this rundir.
    local rundir
    rundir="$(ls -d results/${OVL_ENGINE}/${state}/mtlnet_*_${pid} 2>/dev/null | head -1 || true)"
    say "[$state seed=$seed] rundir=${rundir:-<not found: inspect $runlog>}"
    [ -n "$rundir" ] && echo "$rundir" > "$logroot/${state}_s${seed}.rundir"
}

# ---------------------------------------------------------------------------
# Plan / execute
# ---------------------------------------------------------------------------
print_plan(){
    echo "PLAN (the exact commands the live run would execute):"
    echo "  preflight: $PY -c 'import torch; assert torch.__version__==\"$REQUIRED_TORCH\"'"
    echo "  env: MTL_STRICT=1  MTL_COMPILE_DYNAMIC=1  TORCHINDUCTOR_CACHE_DIR=$TORCHINDUCTOR_CACHE_DIR"
    for state in "${STATES[@]}"; do
        echo "  --- state=$state ---"
        echo "  (a) $PY scripts/mtl_improvement/build_overlap_probe_engine.py $state $STRIDE $MIN_SEQ"
        echo "      -> builds output/$OVL_ENGINE/$state (own stride-1 next/sequences/next_region; v14 untouched)"
        for seed in "${SEEDS[@]}"; do
            echo "  (b) $PY scripts/compute_region_transition.py --state $state --per-fold --seed $seed   (+copy/touch into output/$V14_ENGINE/$state)"
        done
        for seed in "${SEEDS[@]}"; do
            echo "  (pre) log_T freshness check (5 folds) for seed=$seed  (staged log_T vs OVL next_region)"
            echo "  (c) $PY scripts/train.py --task mtl --task-set check2hgi_next_region --engine $OVL_ENGINE --state $state --seed $seed \\"
            echo "          --canon none [+ explicit champion-G pins] --compile --tf32 --per-fold-transition-dir output/$V14_ENGINE/$state   [rundir captured by \$! PID suffix]"
        done
    done
    echo "TOTAL cells: $(( ${#STATES[@]} * ${#SEEDS[@]} ))  (${#STATES[@]} states × ${#SEEDS[@]} seeds), uniform --compile --tf32 --stride $STRIDE --min-seq $MIN_SEQ on engine $OVL_ENGINE"
}

main(){
    hdr
    if [ "$DRY_RUN" -eq 1 ]; then
        print_plan
        echo
        say "DRY-RUN complete — nothing executed (no frozen artifact touched)."
        return 0
    fi

    # ── LAUNCH CONFIRMATION ───────────────────────────────────────────────────
    # The 3 launch-blockers found by the 2026-06-19 adversarial review are FIXED
    # (2026-06-22): the build now goes through the isolated OVL overlap engine
    # (scripts/mtl_improvement/build_overlap_probe_engine.py), which (1) never
    # clobbers the frozen v14 next.parquet/sequences/next_region (it builds its OWN
    # in a separate dir, symlinking only the windowing-independent embeddings),
    # (2) builds next_region from the engine's OWN stride-1 sequences (no canonical
    # stride-9 join), and (3) log_T is staged into the v14 dir and freshness-checked
    # against the OVL stride-1 next_region (the +8..+12pp stale-log_T trap is closed).
    # Blocker #4 (M1 tail-gate) is auto-handled: the builder gates emit_tail=False at
    # stride==1, the ADOPTED board recipe.
    #
    # This is a GPU job that runs the full $(( ${#STATES[@]} * ${#SEEDS[@]} ))-cell
    # board. The torch + log_T-freshness preflights below still gate it. Set
    # P3_BOARD_CONFIRM=1 to skip this confirmation in non-interactive runs.
    if [ "${P3_BOARD_CONFIRM:-0}" != "1" ]; then
        echo "‼ p3_board: about to launch a LIVE $(( ${#STATES[@]} * ${#SEEDS[@]} ))-cell GPU run"
        echo "  states: ${STATES[*]}   seeds: ${SEEDS[*]}   engine: $OVL_ENGINE (v14 read-only)"
        echo "  --dry-run previews the plan without executing anything."
        if [ -t 0 ]; then
            read -r -p "  Proceed? [y/N] " _ans
            case "$_ans" in
                y|Y|yes|YES) ;;
                *) echo "  aborted (no artifact touched)."; exit 0 ;;
            esac
        else
            echo "  non-interactive shell: set P3_BOARD_CONFIRM=1 to proceed. Aborting (no artifact touched)."
            exit 0
        fi
    fi

    preflight_torch

    for state in "${STATES[@]}"; do
        build_inputs "$state"
        for seed in "${SEEDS[@]}"; do
            build_logT "$state" "$seed"
        done
    done

    for state in "${STATES[@]}"; do
        for seed in "${SEEDS[@]}"; do
            preflight_logT_fresh "$state" "$seed"
        done
    done

    for state in "${STATES[@]}"; do
        for seed in "${SEEDS[@]}"; do
            run_cell "$state" "$seed"
        done
    done

    say "DONE — all $(( ${#STATES[@]} * ${#SEEDS[@]} )) cells complete."
}

main
