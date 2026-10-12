#!/usr/bin/env bash
# H3-alt FL — TF32 perf-variant.
#
# Same recipe as scripts/runpod_train_fl_h3alt.sh, plus `--tf32`.
# Used by scripts/runpod_perf_compare.sh to A/B against the baseline run.
# DO NOT use for paper / NORTH_STAR claims — TF32 introduces ~5-10 ULP
# drift on fp32 matmul outside autocast paths.

set -euo pipefail
export TAG="${TAG:-tf32}"
export EXTRA_FLAGS="${EXTRA_FLAGS:-} --tf32"
exec bash "$(dirname "$0")/runpod_train_fl_h3alt.sh"
