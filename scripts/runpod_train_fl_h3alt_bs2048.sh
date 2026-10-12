#!/usr/bin/env bash
# H3-alt FL — batch=2048 perf-variant.
#
# Same recipe as scripts/runpod_train_fl_h3alt.sh, but BATCH=2048
# (NORTH_STAR is locked at 1024 for FL). Halves the per-epoch step
# count; should reduce kernel-launch overhead, the suspected bottleneck
# given 15% GPU utilisation at b=1024.
#
# Quality risk: doubles the effective batch → halves the noise injected
# per step → may converge to a different optimum. Treat as a separate
# data point, not a NORTH_STAR replacement.

set -euo pipefail
export TAG="${TAG:-bs2048}"
export BATCH="${BATCH:-2048}"
exec bash "$(dirname "$0")/runpod_train_fl_h3alt.sh"
