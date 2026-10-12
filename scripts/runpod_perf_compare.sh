#!/usr/bin/env bash
# Perf-variant A/B/C driver for FL H3-alt.
#
#   1. Tags the currently-running baseline (mtl_fl_h3alt tmux session) once
#      it finishes, so we can locate its summary later.
#   2. Runs the TF32 variant 5f x 50ep.
#   3. Runs the torch.compile variant 5f x 50ep.
#   4. Emits a comparison table vs the NORTH_STAR FL H3-alt published
#      numbers (cat F1 67.92 +/- 0.72, reg Acc@10_indist 71.96 +/- 0.68).
#
# Sequencing matters — never run two GPU jobs concurrently on a single
# 4090. Total wall-clock with the current pace (~38 min/variant) is
# roughly 80 min after the baseline lands.
#
# Usage (drop into tmux yourself; the script does not detach):
#   tmux new -s perf-compare 'bash scripts/runpod_perf_compare.sh'
#
# Override which variants run via VARIANTS env (space-separated subset of
# "tf32 compile"). Skip the baseline-wait via SKIP_BASELINE_WAIT=1 if
# you've already tagged the run dir manually.

set -uo pipefail

WORKTREE="${WORKTREE:-/workspace/PoiMtlNet}"
cd "${WORKTREE}"
RESULTS_DIR="${WORKTREE}/results/check2hgi/florida"
LOG_DIR="${WORKTREE}/logs"
COMPARE_DIR="${WORKTREE}/docs/results/perf_compare"
mkdir -p "${LOG_DIR}" "${COMPARE_DIR}"

VARIANTS="${VARIANTS:-tf32 compile}"
BASELINE_TAG="${BASELINE_TAG:-baseline}"

PY="${WORKTREE}/.venv/bin/python"

log() { echo "[$(date '+%H:%M:%S')] [perf-compare] $*"; }

# ── 1. Wait for baseline + tag it ───────────────────────────────────────────
tag_latest_run() {
    local tag="$1"
    local latest
    latest=$(ls -dt "${RESULTS_DIR}/"*_lr*_bs1024_ep50_* 2>/dev/null | head -1)
    if [[ -z "$latest" ]] || [[ ! -d "$latest" ]]; then
        log "WARN: no run dir found to tag with '${tag}'"
        return 1
    fi
    if [[ -f "${latest}/.runpod_tag" ]]; then
        local existing
        existing=$(cat "${latest}/.runpod_tag")
        if [[ "$existing" != "$tag" ]]; then
            log "WARN: ${latest}/.runpod_tag already says '${existing}', not overwriting with '${tag}'"
            return 1
        fi
    fi
    echo "$tag" > "${latest}/.runpod_tag"
    log "tagged ${latest} as ${tag}"
}

if [[ "${SKIP_BASELINE_WAIT:-0}" != "1" ]]; then
    log "waiting for baseline tmux session 'mtl_fl_h3alt' to finish ..."
    while tmux has-session -t mtl_fl_h3alt 2>/dev/null; do
        sleep 30
    done
    log "baseline session ended."
    tag_latest_run "${BASELINE_TAG}"
fi

# ── 2. Run variants sequentially ────────────────────────────────────────────
run_variant() {
    local tag="$1" launcher="$2"
    log "starting variant: ${tag} via ${launcher}"
    local stamp
    stamp=$(date +%Y%m%d_%H%M%S)
    local logf="${LOG_DIR}/fl_h3alt_${tag}_${stamp}.log"
    bash "${launcher}" 2>&1 | tee "${logf}"
    local rc=${PIPESTATUS[0]}
    log "variant ${tag} exit=${rc}; log=${logf}"
    if [[ $rc -eq 0 ]]; then
        tag_latest_run "${tag}"
    fi
    return $rc
}

for variant in $VARIANTS; do
    case "$variant" in
        tf32)    run_variant tf32    "${WORKTREE}/scripts/runpod_train_fl_h3alt_tf32.sh" ;;
        compile) run_variant compile "${WORKTREE}/scripts/runpod_train_fl_h3alt_compile.sh" ;;
        *)       log "unknown variant '${variant}', skipping" ;;
    esac
done

# ── 3. Comparison table ─────────────────────────────────────────────────────
log "building comparison table ..."
TABLE="${COMPARE_DIR}/fl_h3alt_perf_compare_$(date +%Y%m%d_%H%M%S).md"
"${PY}" "${WORKTREE}/scripts/runpod_perf_summarise.py" \
    --results-dir "${RESULTS_DIR}" \
    --output "${TABLE}"
rc=$?
log "summariser exit=${rc}"
log "table: ${TABLE}"
[[ -f "$TABLE" ]] && cat "$TABLE"
