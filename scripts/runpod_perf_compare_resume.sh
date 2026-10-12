#!/usr/bin/env bash
# Resume driver: re-runs the compile variant (with the donated_buffer fix
# applied to scripts/train.py) and then runs the bs2048 variant, then
# emits the comparison table covering all four variants.
#
# Used after the original perf_compare driver bailed when the compile
# variant crashed on the first attempt.

set -uo pipefail

WORKTREE="${WORKTREE:-/workspace/PoiMtlNet}"
cd "${WORKTREE}"
PY="${WORKTREE}/.venv/bin/python"
RESULTS_DIR="${WORKTREE}/results/check2hgi/florida"
LOG_DIR="${WORKTREE}/logs"
COMPARE_DIR="${WORKTREE}/docs/results/perf_compare"
mkdir -p "${LOG_DIR}" "${COMPARE_DIR}"

log() { echo "[$(date '+%H:%M:%S')] [perf-compare-resume] $*"; }

run_variant() {
    local tag="$1" launcher="$2" run_dir_glob="$3"
    log "starting variant: ${tag} via ${launcher}"
    local stamp; stamp=$(date +%Y%m%d_%H%M%S)
    local logf="${LOG_DIR}/fl_h3alt_${tag}_${stamp}.log"
    bash "${launcher}" 2>&1 | tee "${logf}"
    local rc=${PIPESTATUS[0]}
    log "variant ${tag} exit=${rc}; log=${logf}"
    if [[ $rc -eq 0 ]]; then
        local latest
        latest=$(ls -dt "${RESULTS_DIR}/"${run_dir_glob} 2>/dev/null | head -1)
        if [[ -n "$latest" ]]; then
            echo "${tag}" > "${latest}/.runpod_tag"
            log "tagged ${latest} as ${tag}"
        fi
    fi
    return $rc
}

run_variant compile "${WORKTREE}/scripts/runpod_train_fl_h3alt_compile.sh" 'mtlnet_lr*_bs1024_ep50_*'
run_variant bs2048  "${WORKTREE}/scripts/runpod_train_fl_h3alt_bs2048.sh"  'mtlnet_lr*_bs2048_ep50_*'

TABLE="${COMPARE_DIR}/fl_h3alt_perf_compare_$(date +%Y%m%d_%H%M%S).md"
"${PY}" "${WORKTREE}/scripts/runpod_perf_summarise.py" \
    --results-dir "${RESULTS_DIR}" \
    --output "${TABLE}"
log "table: ${TABLE}"
[[ -f "$TABLE" ]] && cat "$TABLE"
