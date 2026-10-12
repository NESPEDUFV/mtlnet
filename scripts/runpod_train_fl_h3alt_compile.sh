#!/usr/bin/env bash
# H3-alt FL — torch.compile perf-variant.
#
# Same recipe as scripts/runpod_train_fl_h3alt.sh, plus `--compile`.
# First fold pays compile overhead (~30-90s); steady-state ~1.2-1.5x.
# DO NOT use for paper / NORTH_STAR claims — inductor may pick different
# numeric kernels per shape, breaking bit-reproducibility.

set -euo pipefail
export TAG="${TAG:-compile}"
export EXTRA_FLAGS="${EXTRA_FLAGS:-} --compile"
exec bash "$(dirname "$0")/runpod_train_fl_h3alt.sh"
