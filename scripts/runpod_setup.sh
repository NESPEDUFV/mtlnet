#!/usr/bin/env bash
# RunPod (CUDA) one-shot environment setup for the worktree-check2hgi-mtl branch.
#
# What it does:
#   1. Verifies we are inside the expected worktree branch.
#   2. Verifies CUDA driver visibility (nvidia-smi).
#   3. Pins uv cache + temp to ${WORKTREE}/.uv-cache + ${WORKTREE}/.tmp
#      (RunPod's overlay root is ~20 GB and uv's torch+cu128 install fills it).
#   4. Installs uv if missing, then creates `.venv` (Python 3.12).
#   5. Installs torch==2.11.0+cu128 + torchvision from the PyTorch cu128 index.
#   6. Installs the PyG companion ops (torch-scatter / torch-sparse /
#      torch-cluster / torch-geometric) against the live torch version.
#   7. Installs the remaining project requirements (torch lines stripped).
#   8. Installs gdown for the data-fetch helper.
#   9. Sanity-checks `torch.cuda.is_available()` + PyG ops importable.
#
# Re-runnable: skips venv/uv install if already present; pip resolver
# treats already-satisfied requirements as no-ops.
#
# After this script: source .venv/bin/activate
# Then either:   bash scripts/runpod_fetch_data.sh florida
# Or directly:   bash scripts/runpod_train_fl_h3alt.sh   (if data already present)

set -euo pipefail

WORKTREE="${WORKTREE:-$(pwd)}"
EXPECTED_BRANCH="${EXPECTED_BRANCH:-worktree-check2hgi-mtl}"
PY_VER="${PY_VER:-3.12}"
TORCH_VER="${TORCH_VER:-2.11.0+cu128}"
TORCH_INDEX="${TORCH_INDEX:-https://download.pytorch.org/whl/cu128}"

cd "$WORKTREE"

# Storage layout on RunPod (counter-intuitive!):
#
#   /workspace  — mfs-backed, `df` reports hundreds of TB free, but each pod
#                 has a tight per-pod quota (~3.5 GB on the pod we tested).
#                 Use it ONLY for training data + results, never the venv.
#   /           — overlay, ~20 GB free per pod. Big enough for venv + cache.
#                 Ephemeral (lost on pod restart) but that's fine since we
#                 rebuild via this script.
#
# So: venv goes on `/` (default /opt/poimtlnet-venv), uv cache stays on `/`
# (default /root/.cache/uv), and we symlink `${WORKTREE}/.venv` to the real
# location so anything that does `source .venv/bin/activate` still works.
VENV_PATH="${VENV_PATH:-/opt/poimtlnet-venv}"
export UV_CACHE_DIR="${UV_CACHE_DIR:-/root/.cache/uv}"
export UV_LINK_MODE="${UV_LINK_MODE:-copy}"
export TMPDIR="${TMPDIR:-/tmp}"
mkdir -p "${UV_CACHE_DIR}" "${TMPDIR}" "$(dirname "${VENV_PATH}")"

echo "================================================================"
echo "[runpod-setup] worktree       = ${WORKTREE}"
echo "[runpod-setup] expected branch= ${EXPECTED_BRANCH}"
echo "[runpod-setup] VENV_PATH      = ${VENV_PATH}"
echo "[runpod-setup] UV_CACHE_DIR   = ${UV_CACHE_DIR}"
echo "[runpod-setup] TMPDIR         = ${TMPDIR}"
echo "================================================================"

# 1. Branch check
current_branch="$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo unknown)"
echo "[runpod-setup] current branch = ${current_branch}"
if [[ "$current_branch" != "$EXPECTED_BRANCH" ]]; then
    echo "[runpod-setup] WARN: not on '${EXPECTED_BRANCH}'."
    echo "[runpod-setup] Run: git checkout ${EXPECTED_BRANCH}"
    echo "[runpod-setup] Or set ALLOW_BRANCH_MISMATCH=1 to suppress this."
    if [[ "${ALLOW_BRANCH_MISMATCH:-0}" != "1" ]]; then
        exit 1
    fi
fi

# 2. CUDA driver visibility
if ! command -v nvidia-smi >/dev/null 2>&1; then
    echo "[runpod-setup] ERROR: nvidia-smi not found. Is this a CUDA pod?"
    exit 1
fi
# Avoid SIGPIPE on `nvidia-smi | head` under set -o pipefail
nvidia-smi 2>&1 | sed -n '1,5p' || true
echo ""

# 3. uv
if ! command -v uv >/dev/null 2>&1; then
    echo "[runpod-setup] installing uv ..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="${HOME}/.local/bin:${PATH}"
fi
echo "[runpod-setup] uv = $(uv --version)"

# 4. venv (on overlay /, symlinked from ${WORKTREE}/.venv)
if [[ ! -d "${VENV_PATH}" ]]; then
    echo "[runpod-setup] creating venv at ${VENV_PATH} (python ${PY_VER}) ..."
    uv venv --python "${PY_VER}" "${VENV_PATH}"
fi
# Symlink so `source .venv/bin/activate` (and every script that hard-codes
# `.venv/bin/python`) keeps working from the worktree.
if [[ -L "${WORKTREE}/.venv" ]] || [[ ! -e "${WORKTREE}/.venv" ]]; then
    ln -snf "${VENV_PATH}" "${WORKTREE}/.venv"
elif [[ ! "$(readlink -f "${WORKTREE}/.venv")" == "$(readlink -f "${VENV_PATH}")" ]]; then
    echo "[runpod-setup] WARN: ${WORKTREE}/.venv is a real dir, not a symlink to ${VENV_PATH}."
    echo "[runpod-setup] Move or remove it manually if you want the on-overlay venv."
fi
# shellcheck disable=SC1091
source "${VENV_PATH}/bin/activate"
echo "[runpod-setup] python = $(python --version) @ $(which python)"

# 5. torch + cu128
echo "[runpod-setup] installing torch==${TORCH_VER} + torchvision ..."
uv pip install \
    "torch==${TORCH_VER}" \
    torchvision \
    --index-url "${TORCH_INDEX}"

TV=$(python -c 'import torch; print(torch.__version__)')
echo "[runpod-setup] torch installed = ${TV}"

# 6. PyG ops (scatter / sparse / cluster) — must match live torch
echo "[runpod-setup] installing PyG add-ons against torch=${TV} ..."
uv pip install \
    torch-scatter \
    torch-sparse \
    torch-cluster \
    -f "https://data.pyg.org/whl/torch-${TV}.html"
uv pip install torch-geometric

# 7. Project deps (torch lines stripped — already installed above)
echo "[runpod-setup] installing remaining project requirements ..."
STRIP_RE='^(torch==|torchvision==|torch-geometric|torch_cluster|torch_scatter|torch_sparse)'
TMP_REQ="$(mktemp "${TMPDIR}/req.XXXXXX.txt")"
grep -vE "${STRIP_RE}" requirements.txt > "${TMP_REQ}"
uv pip install -r "${TMP_REQ}"
rm -f "${TMP_REQ}"

# 8. gdown
uv pip install gdown

# 9. Sanity
echo ""
echo "[runpod-setup] sanity check ..."
python - <<'PY'
import torch
print(f"torch          = {torch.__version__}")
print(f"cuda available = {torch.cuda.is_available()}")
if torch.cuda.is_available():
    print(f"device         = {torch.cuda.get_device_name(0)}")
    print(f"capability     = {torch.cuda.get_device_capability(0)}")
import torch_geometric, torch_scatter, torch_sparse, torch_cluster  # noqa
print(f"torch_geometric= {torch_geometric.__version__}")
print(f"torch_scatter  = {torch_scatter.__version__}")
print(f"torch_sparse   = {torch_sparse.__version__}")
print(f"torch_cluster  = {torch_cluster.__version__}")
PY

echo ""
echo "================================================================"
echo "[runpod-setup] DONE."
echo "  Activate:   source .venv/bin/activate"
echo "  Fetch data: bash scripts/runpod_fetch_data.sh <florida|california|texas>"
echo "  Train FL:   bash scripts/runpod_train_fl_h3alt.sh"
echo "================================================================"
