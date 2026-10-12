#!/usr/bin/env python3
"""Run a v18 study lane on Modal from a plain shell — no agent-harness compute API required.

WHY THIS EXISTS (read before reaching for run_modal_cell.py)
============================================================
`run_modal_cell.py` is written against `host.compute.create("byoc:modal")`, the compute API of
the Claude Science agent harness. **Claude Code does not have that API.** A Claude Code agent
has a terminal, the `modal` client and a token — nothing else. Every rule in MODAL_MANUAL.md
that is phrased in terms of `submit_job` / `./out/` harvest / `host.compute.ledger()` is
therefore unreachable from a Claude Code session, and an agent that tries anyway burns a turn
discovering it.

This script is the same discipline expressed in the plain SDK:

    submit_job + ./out/ harvest        ->  Sandbox.exec, harvest onto the Volume, download here
    host.compute.ledger()              ->  Sandbox.list()
    c.close(intent=...)                ->  sb.terminate(), verified, in a finally
    "the job is invisible while running" ->  live stdout streaming, so it never is

It also fixes the observability problem at the root. MODAL_MANUAL section 7 says a running job
cannot be tailed. That is true of `submit_job`; it is NOT true of a Sandbox — `sb.exec()`
returns a live stdout stream. So this runner is never blind, and the committed-heartbeat
mechanism (`watch_modal.py`) becomes a second, independent view rather than the only one.

USAGE
    # cheap CPU preflight: what is staged, is it materialized, does the engine pass
    python modal_lane.py --state alabama --preflight-only

    # a real lane
    python modal_lane.py --state alabama --seed 7 --cells cat,reg --gpu A100-40GB

    # see the plan and the cost without spending anything
    python modal_lane.py --state alabama --seed 7 --cells cat,reg --dry-run

CREDENTIALS
    Read from MODAL_TOKEN_ID / MODAL_TOKEN_SECRET, or from --env-file (default: the sibling
    `.env`, which holds a `modal token set --token-id ... --token-secret ...` line). Tokens are
    never written to ~/.modal.toml and never echoed.

WHAT IT GUARANTEES
    1. The sandbox is terminated in a `finally`, then the termination is VERIFIED against
       Modal rather than assumed. MODAL_MANUAL section 6 records a ledger that showed three
       sandboxes alive minutes after two were terminated; trusting the call is not enough.
    2. Results land on local disk before teardown, with a run_metadata.json that records the
       device actually served (Modal served an A100-SXM4-80GB for a request of A100-40GB),
       the billed resource shape, and the computed cost.
    3. Nothing runs until preflight passes.
"""
from __future__ import annotations

import argparse
import json
import os
import pathlib
import re
import shlex
import sys
import threading
import time

HERE = pathlib.Path(__file__).resolve().parent          # pipelines/modal
REPO_ROOT = HERE.parents[1]                             # repo root
# Both were derived by counting parents from the old home
# (docs/studies/closing_data/v18_2/scripts) and silently pointed outside the repo after the
# 2026-08-11 move. Anchor on HERE, which is the only path that travels with the file.

ENGINE = "check2hgi_v18"
V14 = "check2hgi_design_k_resln_mae_l0_1"
VOLUME = "poimtl-v18-data"
APP_NAME = "poimtl-v18-2-lane"

# ---------------------------------------------------------------- pricing
# modal.com/pricing, fetched 2026-08-10, in $/second. Kept here rather than in prose so a cost
# estimate is computed, never remembered. Modal bills GPU + CPU + memory per container-second:
# quoting the bare GPU rate understates an 8-CPU/64-GB A100-40GB container by 42 %.
GPU_USD_S = {
    "B300": 0.001972, "B200": 0.001736, "H200": 0.001261, "H100": 0.001097,
    "A100-80GB": 0.000694, "A100": 0.000583, "A100-40GB": 0.000583,
    "L40S": 0.000542, "A10": 0.000306, "L4": 0.000222, "T4": 0.000164,
}
CPU_USD_S = 0.0000131          # per physical core, minimum 0.125 cores
MEM_USD_S = 0.00000222         # per GiB


# MEASURED CALIBRATION (2026-08-10). On a GPU container the CPU/memory you REQUEST is a floor,
# not a cap: the GPU slot carries the host's per-GPU share. Billing for texas s7 on an H100 came
# in at exactly 3.0x the requested 8 CPU / 128 GiB on BOTH lines (memory $5.61 and CPU $2.07 over
# 1.83 h => ~384 GiB and ~24 cores). The alabama A100 cells show the same effect at ~2.5-2.7x.
# Costing from the request alone understated a real H100 cell by 52% ($9.79 modelled vs $14.92
# billed), which is exactly the kind of error that blew up the earlier budget plan. Apply the
# measured multiplier, and treat it as an empirical constant to be re-checked, not a law.
GPU_HOST_SHARE = 3.0     # requested CPU/RAM -> billed CPU/RAM on a GPU container (measured H100)


def cost_usd(gpu: str | None, cpu: float, memory_mb: int, seconds: float) -> float:
    g = GPU_USD_S.get((gpu or "").split(":")[0], 0.0)
    share = GPU_HOST_SHARE if g > 0 else 1.0   # CPU-only tiers bill what you ask for
    return (g + share * (cpu * CPU_USD_S + (memory_mb / 1024.0) * MEM_USD_S)) * seconds


def rate_usd_h(gpu: str | None, cpu: float, memory_mb: int) -> float:
    return cost_usd(gpu, cpu, memory_mb, 3600.0)


# ---------------------------------------------------------------- credentials
def load_tokens(env_file: pathlib.Path | None, profile: str | None = None) -> tuple[str, str]:
    """Resolve one credential pair, and REFUSE to guess when the .env holds more than one.

    THE FAILURE THIS PREVENTS (2026-08-10). The .env grew a second account and this function
    still did `re.search(...)`, which returns the FIRST match. A florida run was therefore
    submitted against the exhausted account while a freshly funded one sat unused in line 3 of
    the same file, and nothing in the output said which account it had picked. Money moves here;
    a silent first-match is not acceptable. With several profiles present you must name one with
    --profile, and the chosen profile is always printed before anything is submitted.
    """
    tid, tsec = os.environ.get("MODAL_TOKEN_ID"), os.environ.get("MODAL_TOKEN_SECRET")
    if tid and tsec and not profile:
        print(f"account   : from MODAL_TOKEN_ID env (…{tid[-6:]})")
        return tid, tsec
    if tid and profile:
        # An explicit --profile must WIN over an exported token, and loudly. Operating two
        # workspaces from one shell means MODAL_TOKEN_ID is routinely left over from the previous
        # account; silently preferring it would bill the wrong workspace while the command line
        # says otherwise -- the worst kind of wrong, because the transcript looks correct.
        print(f"account   : --profile {profile} OVERRIDES the exported MODAL_TOKEN_ID "
              f"(…{tid[-6:]}) in this shell")
    if not (env_file and env_file.exists()):
        sys.exit("no Modal credentials: set MODAL_TOKEN_ID/MODAL_TOKEN_SECRET or pass --env-file")

    found: list[tuple[str, str, str]] = []          # (profile, token_id, token_secret)
    for line in env_file.read_text().splitlines():
        m1 = re.search(r"--token-id\s+(\S+)", line)
        m2 = re.search(r"--token-secret\s+(\S+)", line)
        if not (m1 and m2):
            m1 = re.search(r"MODAL_TOKEN_ID\s*=\s*(\S+)", line)
            m2 = re.search(r"MODAL_TOKEN_SECRET\s*=\s*(\S+)", line)
        if m1 and m2:
            mp = re.search(r"--profile[= ](\S+)", line)
            found.append((mp.group(1) if mp else f"line{len(found)+1}", m1.group(1), m2.group(1)))

    if not found:
        sys.exit(f"no credentials parsed from {env_file}")
    names = [f[0] for f in found]
    if profile:
        hit = [f for f in found if f[0] == profile]
        if not hit:
            sys.exit(f"--profile {profile!r} not in {env_file} (has: {', '.join(names)})")
        sel = hit[0]
    elif len(found) == 1:
        sel = found[0]
    else:
        sys.exit(f"{env_file} holds {len(found)} accounts ({', '.join(names)}) — refusing to "
                 f"guess which one to bill. Re-run with --profile <name>.")
    print(f"account   : {sel[0]}  (…{sel[1][-6:]})")
    return sel[1], sel[2]


# ---------------------------------------------------------------- image
def build_image(modal):
    """The pins from modal/poimtl_gpu.py, kept identical so a rented cell reproduces the origin
    host's numerics rather than an approximation.

    ORDERING IS LOAD-BEARING: torch first, from the cu128 index, as its own layer, so the PyG
    resolver in the next layer sees it satisfied and cannot drag in a CPU wheel. The third layer
    comes from the repo's declared manifest, not from grepping imports — the first build of this
    image was hand-listed, shipped without torchmetrics (imported at module scope by next_cv.py)
    and died 17 s into a GPU tier.
    """
    return (
        modal.Image.debian_slim(python_version="3.12")
        .apt_install("git", "curl", "zstd")
        .pip_install("torch==2.11.0+cu128",
                     extra_index_url="https://download.pytorch.org/whl/cu128")
        .pip_install("torch_geometric==2.7.0")
        .pip_install(
            "numpy==2.0.2", "pandas==2.2.3", "pyarrow==24.0.0", "scikit-learn==1.8.0",
            "scipy==1.16.3", "tqdm==4.67.1", "pyyaml==6.0.3", "matplotlib==3.9.4",
            "torchmetrics==1.9.0", "networkx==3.2.1", "h5py==3.13.0", "psutil==7.0.0",
            "numba==0.60.0", "hydra-core==1.3.2", "omegaconf==2.3.0",
            "pytorch-warmup==0.2.0", "shapely==2.1.2", "geopandas==1.0.1", "cvxpy==1.6.4",
            "modal",   # the heartbeat commits the Volume from inside the container
        )
        .env({
            # NOT pinned to 8 any more. os.cpu_count() reports the HOST's cores rather than the
            # container's allocation, so an unset value spawns a thread storm -- but hard-coding 8
            # was the opposite mistake and it cost real time: florida's reg cell spends a long
            # phase scoring a 4.5 GiB logit tensor ON CPU ("to avoid GPU OOM at overlap scale"),
            # and 8 threads made that phase ~1.37x SLOWER than the same cell on the 32-core A40 --
            # on an A100. Worse, a GPU container is billed for the host's per-GPU CPU share
            # (~3x the request, measured), so capping at 8 meant paying for ~24 cores and using 8.
            # modal_lane.py now sets both vars from --cpu at submit time; this is only the default.
            "OMP_NUM_THREADS": "8", "MKL_NUM_THREADS": "8",
            "PYTORCH_CUDA_ALLOC_CONF": "expandable_segments:True",
        })
    )


# ---------------------------------------------------------------- in-container scripts
PREFLIGHT_SH = r"""
set -uo pipefail
echo "=== container ==="
python -c 'import sys; print("python", sys.version.split()[0])'
python - <<'PY'
try:
    import torch
    print("torch", torch.__version__, "cuda_avail", torch.cuda.is_available())
    if torch.cuda.is_available():
        print("device", torch.cuda.get_device_name(0),
              round(torch.cuda.get_device_properties(0).total_memory / 2**30, 1), "GiB")
except Exception as e:
    print("torch import FAILED:", e)
PY
command -v nvidia-smi >/dev/null && nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv,noheader
echo "=== volume ==="
for d in /data /data/repo /data/seed /data/scripts; do
  printf '%-16s ' "$d"; ls "$d" 2>/dev/null | tr '\n' ' '; echo
done
echo "=== repo ==="
cd /data/repo 2>/dev/null || { echo "FATAL: no /data/repo"; exit 3; }
echo "cwd=$(pwd)"
echo "venv present: $([ -x .venv/bin/python ] && echo yes || echo 'NO -> run_lane.sh must resolve PY from PATH')"
echo "=== engines materialized under output/ ==="
ls output 2>/dev/null || echo "  (no output/ -- no engine has been materialized on this volume)"
for st in __STATES__; do
  echo "--- $st ---"
  for p in "output/__ENG__/$st/input/next.parquet" \
           "output/__ENG__/$st/input/next_region.parquet" \
           "output/__ENG__/$st/region_embeddings.parquet" \
           "output/__ENG__/$st/temp/sequences_next.parquet" \
           "output/__V14__/$st/region_embeddings.parquet" \
           "output/check2hgi/$st/temp/checkin_graph.pt"; do
    if [ -s "$p" ]; then printf '  OK   %-72s %s\n' "$p" "$(du -h "$p" | cut -f1)"
    elif [ -e "$p" ]; then printf '  ZERO %s (exists but 0 bytes -- counts as missing)\n' "$p"
    else printf '  MISS %s\n' "$p"; fi
  done
done
echo "=== preflight.py verdict ==="
S=pipelines/modal
if [ -s /data/scripts/v18_2_scripts.tgz ]; then
  mkdir -p pipelines && tar xzf /data/scripts/v18_2_scripts.tgz -C pipelines 2>/dev/null
fi
if [ -f "$S/preflight.py" ]; then
  for st in __STATES__; do
    echo "--- $st ---"; python "$S/preflight.py" --state "$st" --cells __CELLS__ || echo "  (preflight FAILED for $st)"
  done
else
  echo "  (no preflight.py on the volume -- upload the scripts bundle with --stage-scripts)"
fi
echo PREFLIGHT_REPORT_DONE
"""

def _amb_env() -> str:
    """Forward MTL_AMBIGUITY_STRICT into the container when the operator set it here.

    Without this the only way to accept a tie-optimistic cell was to drop MTL_STRICT wholesale,
    which also disarms the canon-recipe and overlap-provenance guards that have nothing to do
    with tie-breaks. The ambiguity count is recorded in the cell artifact either way.
    """
    v = os.environ.get("MTL_AMBIGUITY_STRICT")
    return f"MTL_AMBIGUITY_STRICT={v} " if v is not None else ""


def lane_sh(state: str, seeds: list[int], cells: str, parallel: bool, stagger: int = 0) -> str:
    """The in-container lane command, for one or several seeds packed into ONE container.

    WHY PACK. Modal bills per container-second, so N cells in one container cost that container's
    WALL, not the sum of N containers. That is only a win when the cells do not saturate the GPU:
    cat/reg qualify (alabama's reg ran at ~65 % utilisation), a large-state joint does not
    (measured 89-99 %, where packing buys nothing and the extra RAM reservation loses money).

    WHY STAGGER. The dataset build is the RAM spike, not training. Launching every build at the
    same instant multiplies that peak; offsetting them costs a few seconds of wall and flattens it.

    Harvest goes to the VOLUME (/data/harvest/<state>_s<seed>), not a job-scoped ./out/: a Sandbox
    has no ./out/ mechanism and does not need one, since the Volume already survives teardown and
    the run clock, and the driver downloads from it directly.
    """
    par = "PARALLEL=1 " if parallel else ""
    mk = "\n".join(f'mkdir -p /data/harvest/{state}_s{sd} /data/live/{state}_s{sd}' for sd in seeds)
    launch = []
    for i, sd in enumerate(seeds):
        delay = f"sleep {stagger * i}; " if (stagger and i) else ""
        launch.append(
            f'( {delay}{_amb_env()}CELLS={cells} {par}HARVEST=1 '
            f'HARVEST_OUT=/data/harvest/{state}_s{sd} '
            f'LIVE_DIR=/data/live/{state}_s{sd} LIVE_VOLUME={VOLUME} '
            f'INDUCTOR_ROOT=/data/inductor REPO=/data/repo PY=/usr/local/bin/python '
            f'LANE_HOST="modal:$GPUNAME" '
            f'bash "$S/run_lane.sh" {state} {sd} {ENGINE} {V14} '
            f'docs/results/closing_data/v18_2 ) & P{sd}=$!')
    waits = "\n".join(f'wait ${{P{sd}}} || RC=1' for sd in seeds)
    copies = []
    for sd in seeds:
        copies.append(
            f'cp docs/results/closing_data/v18_2/{state}_s{sd}_*.json /data/harvest/{state}_s{sd}/ 2>/dev/null\n'
            f'mkdir -p /data/harvest/{state}_s{sd}/logs\n'
            f'for f in docs/results/closing_data/v18_2/logs/{state}_s{sd}*; do [ -f "$f" ] && '
            f'cp "$f" /data/harvest/{state}_s{sd}/logs/ 2>/dev/null; done')
    return f"""
set -uo pipefail
cd /data/repo || {{ echo NO_REPO; exit 3; }}
[ -s /data/scripts/v18_2_scripts.tgz ] || {{ echo "ABORT: no scripts bundle on the volume"; exit 8; }}
mkdir -p pipelines && tar xzf /data/scripts/v18_2_scripts.tgz -C pipelines || exit 8
S=pipelines/modal
ST={state}
mkdir -p /data/inductor
{mk}

# Preflight BEFORE the GPU does anything. Four launches died 40 s in on a missing file.
python "$S/preflight.py" --state $ST --cells {cells} || {{ echo PREFLIGHT_ABORT; exit 9; }}

# A sidecar means "this cell produced results", never "this cell was attempted".
for f in docs/results/closing_data/v18_2/{state}_s*_*.json; do [ -s "$f" ] || rm -f "$f"; done

# Use the cores we are actually billed for. A GPU container pays the host's per-GPU CPU share
# regardless of --cpu, so leaving OMP at the image default wastes what is already paid for.
export OMP_NUM_THREADS=$(nproc) MKL_NUM_THREADS=$(nproc)
echo "CPU: nproc=$(nproc)  OMP_NUM_THREADS=$OMP_NUM_THREADS"
GPUNAME=$(python -c 'import torch;print(torch.cuda.get_device_name(0))' 2>/dev/null || echo cpu)
command -v nvidia-smi >/dev/null && nvidia-smi --query-gpu=name,memory.total --format=csv,noheader
echo "PACKED_SEEDS={','.join(str(x) for x in seeds)} CELLS={cells} STAGGER={stagger}s"
echo "LANE_START $(date -Is)"
T0=$SECONDS
RC=0
{chr(10).join(launch)}
{waits}
echo "LANE_WALL=$((SECONDS-T0))s RC=$RC"

{chr(10).join(copies)}
python -c "import modal;modal.Volume.from_name('{VOLUME}').commit()" 2>/dev/null || true
for sd in {' '.join(str(x) for x in seeds)}; do echo "HARVEST_AT=/data/harvest/{state}_s$sd"; find /data/harvest/{state}_s$sd -type f | sed 's/^/  /'; done
echo CELL_DONE_RC=$RC
exit $RC
"""


# ---------------------------------------------------------------- volume download
def download_tree(vol, remote_dir: str, local_dir: pathlib.Path) -> list[str]:
    """Pull a Volume subtree to local disk.

    Two things about the SDK that cost a re-download when guessed instead of checked:

    * `Volume.iterdir()` is **recursive**, so the whole subtree arrives from one call and an
      explicit stack walk would visit every directory twice.
    * `FileEntryType` is an **IntEnum**, and since Python 3.11 `str()` on an IntEnum returns
      the *number* ("2"), not "FileEntryType.DIRECTORY". A `"dir" in str(e.type).lower()` test
      is therefore always False, every directory gets treated as a file, and the download dies
      on `[Errno 17] File exists` the moment a directory shares a name with a path already
      created for one of its children. Match on `e.type.name`.
    """
    got: list[str] = []
    base = remote_dir.strip("/")
    try:
        entries = list(vol.iterdir(remote_dir))
    except Exception as exc:
        print(f"  ! cannot list {remote_dir}: {exc}")
        return got
    for e in entries:
        path = (e.path if hasattr(e, "path") else str(e)).lstrip("/")
        if getattr(getattr(e, "type", None), "name", "") == "DIRECTORY":
            continue
        rel = path[len(base):].lstrip("/") if path.startswith(base) else pathlib.Path(path).name
        dst = local_dir / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        try:
            with open(dst, "wb") as fh:
                for chunk in vol.read_file(path):
                    fh.write(chunk)
            got.append(rel)
        except Exception as exc:
            print(f"  ! could not download {path}: {exc}")
    return got


def fetch_harvest(modal, volume_name: str, remote: str, dest: pathlib.Path,
                  expect: list[str], tries: int = 6, delay: int = 5):
    """Download the harvest, RE-INSTANTIATING the Volume handle on every attempt.

    THE BUG THIS EXISTS FOR (found on the alabama s100 joint cell, 2026-08-10):
    a `modal.Volume` handle created *before* the job does not see the container's
    `Volume.commit()` afterwards — and `vol.reload()` does not fix it. The driver downloaded the
    files that existed when it started and silently missed every file the run produced: the joint
    sidecar, `a40_matched_score.json`, `joint_best_score.json`, the joint log and the whole
    `rundirs/` tree. It reported success. A fresh `Volume.from_name()` in the same process saw
    all 19 files immediately.

    On a 4-hour california joint that failure mode is expensive and silent: the run succeeds, the
    numbers exist on the Volume, and the archive comes home empty of exactly the cell you paid
    for. So: new handle each attempt, retry until the expected sidecars appear, and return what
    is still missing so the caller can fail loudly instead of reporting a clean exit.
    """
    got: list[str] = []
    missing = list(expect)
    for attempt in range(1, tries + 1):
        vol = modal.Volume.from_name(volume_name)      # FRESH — do not reuse the pre-job handle
        try:
            vol.reload()
        except Exception:
            pass
        got = download_tree(vol, remote, dest)
        missing = [e for e in expect if not any(g.endswith(e) for g in got)]
        if not missing:
            return got, []
        if attempt < tries:
            print(f"  harvest incomplete after attempt {attempt} "
                  f"(missing {missing}) — the commit may still be propagating; retry in {delay}s")
            time.sleep(delay)
    return got, missing


def parse_values(local_dir: pathlib.Path) -> dict:
    """Report numbers, not filenames. Reads the scorers' own outputs — never a re-derivation."""
    out: dict = {}
    for p in local_dir.rglob("*_cat.json"):
        try:
            d = json.loads(p.read_text())
            if d.get("family") == "cat":
                out["cat"] = d.get("cat")
                out["cat_wall_s"] = d.get("wall_seconds")
        except Exception:
            pass
    for p in local_dir.rglob("*_reg.json"):
        try:
            d = json.loads(p.read_text())
            if d.get("family") == "reg":
                out["reg"] = d.get("reg")
                out["reg_wall_s"] = d.get("wall_seconds")
        except Exception:
            pass
    for p in local_dir.rglob("*_joint.json"):
        try:
            d = json.loads(p.read_text())
            if d.get("family") == "joint":
                out["joint_cat"] = d.get("cat")
                out["joint_reg"] = d.get("reg")
                out["joint_wall_s"] = d.get("wall_seconds")
        except Exception:
            pass
    return out


# ---------------------------------------------------------------- teardown
def terminate_verified(modal, sb, label: str) -> dict:
    """Terminate, then CHECK. MODAL_MANUAL section 6 records a ledger that reported sandboxes
    alive for minutes after they were terminated, so a successful call is not evidence."""
    rep = {"label": label, "sandbox_id": None, "terminated": False, "poll": None, "strays": []}
    try:
        rep["sandbox_id"] = sb.object_id
    except Exception:
        pass
    for attempt in range(3):
        try:
            sb.terminate()
        except Exception as exc:
            rep[f"terminate_error_{attempt}"] = str(exc)
        time.sleep(2)
        try:
            code = sb.poll()
        except Exception:
            code = None
        rep["poll"] = code
        if code is not None:
            rep["terminated"] = True
            break
    try:
        strays = []
        for other in modal.Sandbox.list():
            if other.poll() is None:
                strays.append(other.object_id)
        rep["strays"] = strays
    except Exception as exc:
        rep["stray_check_error"] = str(exc)
    return rep


# ---------------------------------------------------------------- main
def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--state", required=True,
                    help="one state; --preflight-only also accepts a comma-separated list")
    ap.add_argument("--seed", default="0",
                    help="one seed, or a comma list to PACK several into one container "
                         "(only for cells that do not saturate the GPU -- cat/reg, not joint)")
    ap.add_argument("--stagger", type=int, default=0,
                    help="seconds between packed seed launches; spreads the dataset-build RAM peak")
    ap.add_argument("--cells", default="cat,reg,joint")
    ap.add_argument("--gpu", default="A100-40GB")
    ap.add_argument("--cpu", type=float, default=8)
    ap.add_argument("--memory", type=int, default=65536, help="MiB")
    ap.add_argument("--timeout", type=int, default=None,
                    help="sandbox run clock, seconds (default 10800 for a lane, 900 preflight)")
    ap.add_argument("--parallel", action="store_true",
                    help="run cat/reg/joint concurrently on one card (PARALLEL=1)")
    ap.add_argument("--preflight-only", action="store_true",
                    help="CPU tier, no GPU: report volume + engine state, then exit")
    ap.add_argument("--stage-scripts", action="store_true",
                    help="upload scripts/ to the volume as v18_2_scripts.tgz before running")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--refetch", action="store_true",
                    help="download an existing harvest from the Volume and exit. No container, "
                         "no cost. Use when a run succeeded but its archive came home partial.")
    ap.add_argument("--env-file", type=pathlib.Path, default=HERE / ".env")
    ap.add_argument("--profile", default=None,
                    help="which account in --env-file to bill. REQUIRED when the file holds "
                         "more than one; the script refuses to guess.")
    ap.add_argument("--archive-root", type=pathlib.Path,
                    default=REPO_ROOT / "docs/results/closing_data/v18_2/modal_runs")
    args = ap.parse_args()

    if args.timeout is None:
        # A short clock on the cheap job matters: if this driver is SIGKILLed the `finally`
        # never runs, and the sandbox then bills until its own clock expires. The run clock is
        # the only teardown guarantee that survives the death of the thing holding the handle.
        args.timeout = 900 if args.preflight_only else 10800
    gpu = None if args.preflight_only else args.gpu
    cpu = 4 if args.preflight_only else args.cpu
    mem = 16384 if args.preflight_only else args.memory
    rate = rate_usd_h(gpu, cpu, mem)

    print(f"lane      : {args.state} seed(s) {args.seed}  cells={args.cells}"
          f"{'  PARALLEL' if args.parallel else ''}")
    print(f"tier      : gpu={gpu or 'none (CPU)'}  cpu={cpu}  mem={mem} MiB")
    print(f"rate      : ${rate:.4f}/h  "
          f"(gpu ${GPU_USD_S.get((gpu or '').split(':')[0], 0)*3600:.3f} + "
          f"cpu ${cpu*CPU_USD_S*3600:.3f} + mem ${mem/1024*MEM_USD_S*3600:.3f})")
    print(f"run clock : {args.timeout}s  -> worst case ${rate*args.timeout/3600:.2f}")
    if args.dry_run:
        # Render the in-container script and assert what it will actually launch. The seed-list
        # plumbing bug of 2026-08-10 (a string iterated character-by-character into lanes
        # "s7 s, s1 s0 s0") got past a dry run that returned before lane_sh was ever called, and
        # was only visible once a billed container had started. Never again: dry-run compiles.
        sds = [int(x) for x in str(args.seed).split(",") if str(x).strip()]
        if not args.preflight_only:
            sc = lane_sh(args.state.split(",")[0], sds, args.cells, args.parallel, args.stagger)
            # line looks like: ... bash "$S/run_lane.sh" <state> <seed> <engine> ...
            launched = [l.split("run_lane.sh")[1].replace('"', " ").split()[1]
                        for l in sc.splitlines() if "run_lane.sh" in l and "bash" in l]
            print(f"\n  would launch seeds : {launched}")
            print(f"  expected           : {[str(x) for x in sds]}")
            assert launched == [str(x) for x in sds], "SEED PLUMBING BROKEN -- refusing"
            mode = ("PARALLEL — families share the GPU" if args.parallel
                    else "SERIAL — cat, then reg, then joint, one after another")
            print(f"  cells per seed     : {args.cells}   stagger {args.stagger}s")
            print(f"  execution mode     : {mode}")
            if not args.parallel and len(args.cells.split(",")) > 1:
                # Omitting --parallel silently serialises the families inside each seed. That
                # happened on the florida run and cost ~20 min of wall for no reason: the dry run
                # printed the cell list but never said they would run one at a time.
                print("  !! no --parallel: the families will run ONE AT A TIME inside each seed.")
                print("     For short cells (cat/reg) that is usually not what you want.")
        print("\n--dry-run: nothing submitted.")
        return 0

    tid, tsec = load_tokens(args.env_file, args.profile)
    os.environ["MODAL_TOKEN_ID"], os.environ["MODAL_TOKEN_SECRET"] = tid, tsec
    import modal

    if args.refetch:
        # Pure recovery: the run already happened and its output is on the Volume, which survives
        # teardown and the run clock. Nothing is submitted and nothing bills.
        sds = [int(x) for x in str(args.seed).split(",") if str(x).strip()]
        tag = sds[0] if len(sds) == 1 else "-".join(str(x) for x in sds)
        dest = args.archive_root / f"{args.state}_s{tag}_refetch_{time.strftime('%Y%m%d_%H%M%S')}"
        dest.mkdir(parents=True, exist_ok=True)
        got, missing = [], []
        for sd in sds:
            sub = dest / f"s{sd}" if len(sds) > 1 else dest
            sub.mkdir(parents=True, exist_ok=True)
            exp = [f"{args.state}_s{sd}_{fam}.json"
                   for fam in (c.strip() for c in args.cells.split(",")) if fam]
            g, m = fetch_harvest(modal, VOLUME, f"/harvest/{args.state}_s{sd}", sub, exp)
            got += [f"s{sd}/{x}" for x in g]; missing += m
        vals = parse_values(dest)
        (dest / "run_metadata.json").write_text(json.dumps(
            {"kind": "refetch", "state": args.state, "seed": args.seed, "cells": args.cells,
             "source": f"{VOLUME}:/harvest/{args.state}_s{{{args.seed}}}", "files": got, "values": vals,
             "harvest_incomplete": missing or None,
             "archived_at": time.strftime("%Y-%m-%dT%H:%M:%S%z")}, indent=2))
        print(f"refetched {len(got)} file(s) -> {dest}")
        print(f"values   : {json.dumps(vals)}")
        if missing:
            print(f"!! still missing: {missing}")
        return 1 if missing else 0

    vol = modal.Volume.from_name(VOLUME, create_if_missing=False)

    if args.stage_scripts:
        import tarfile, tempfile
        with tempfile.TemporaryDirectory() as td:
            tgz = pathlib.Path(td) / "v18_2_scripts.tgz"
            with tarfile.open(tgz, "w:gz") as tf:
                tf.add(HERE, arcname="modal")
            with vol.batch_upload(force=True) as up:
                up.put_file(tgz, "/scripts/v18_2_scripts.tgz")
        # "printing a checkmark does not mean the file is there" -- verify the byte count.
        size = next((e.size for e in vol.iterdir("/scripts")
                     if str(getattr(e, "path", e)).endswith("v18_2_scripts.tgz")), None)
        print(f"staged    : /scripts/v18_2_scripts.tgz ({size})")

    app = modal.App.lookup(APP_NAME, create_if_missing=True)
    image = build_image(modal)

    states = [x.strip() for x in args.state.split(",") if x.strip()]
    if not args.preflight_only and len(states) != 1:
        sys.exit("--state takes exactly one state for a lane run")
    seeds = [int(x) for x in str(args.seed).split(",") if str(x).strip()]
    seed_tag = seeds[0] if len(seeds) == 1 else "-".join(str(x) for x in seeds)
    if len(seeds) > 1 and "joint" in args.cells:
        print("refusing: joint cells saturate the GPU (measured 89-99%), so packing seeds buys "
              "no throughput and costs extra RAM. Run joint one seed per container.")
        return 2
    script = (PREFLIGHT_SH.replace("__STATES__", " ".join(states))
              .replace("__ENG__", ENGINE).replace("__V14__", V14)
              .replace("__CELLS__", args.cells)
              if args.preflight_only else lane_sh(states[0], seeds, args.cells,
                                                    args.parallel, args.stagger))

    stamp = time.strftime("%Y%m%d_%H%M%S")
    kind = "preflight" if args.preflight_only else "lane"
    dest = args.archive_root / f"{states[0]}_s{seed_tag}_{kind}_{stamp}"
    dest.mkdir(parents=True, exist_ok=True)
    console = dest / "console.log"

    sb = None
    t0 = time.time()
    rc, meta_extra = None, {}
    lines: list[str] = []      # hoisted: the finally block reads it even on an early failure
    try:
        print("\ncreating sandbox (first run builds the image; later runs reuse it) ...")
        # enable_output streams the IMAGE BUILD to the terminal. Without it the first run looks
        # hung for the whole torch+PyG build, which is the exact "am I blind?" state this
        # runner exists to remove.
        try:
            _out_ctx = modal.enable_output()
            _out_ctx.__enter__()
        except Exception:
            _out_ctx = None
        sb = modal.Sandbox.create(
            "sleep", "infinity", app=app, image=image, gpu=gpu, cpu=cpu, memory=mem,
            volumes={"/data": vol}, timeout=args.timeout + 600, workdir="/data/repo",
        )
        if _out_ctx is not None:
            try:
                _out_ctx.__exit__(None, None, None)
            except Exception:
                pass
        print(f"sandbox   : {sb.object_id}   (streaming live below)\n" + "-" * 72)

        proc = sb.exec("bash", "-lc", script, timeout=args.timeout)

        def pump(stream, tag):
            for line in stream:
                s = line.rstrip("\n")
                lines.append(s)
                print(s if tag == "out" else f"[stderr] {s}", flush=True)

        th = threading.Thread(target=pump, args=(proc.stderr, "err"), daemon=True)
        th.start()
        pump(proc.stdout, "out")
        th.join(timeout=10)
        rc = proc.wait()
        print("-" * 72 + f"\nexit code : {rc}")
        console.write_text("\n".join(lines) + "\n")

        if not args.preflight_only:
            print("\ndownloading harvest from the volume ...")
            # One expected sidecar per (seed, cell). If a cell ran, its sidecar exists; if it is
            # absent after the retries the harvest is incomplete and we say so, rather than
            # archiving a partial directory under a green exit code.
            got, missing = [], []
            for sd in seeds:
                sub = dest / f"s{sd}" if len(seeds) > 1 else dest
                sub.mkdir(parents=True, exist_ok=True)
                exp = [f"{states[0]}_s{sd}_{fam}.json"
                       for fam in (c.strip() for c in args.cells.split(",")) if fam]
                g, m = fetch_harvest(modal, VOLUME, f"/harvest/{states[0]}_s{sd}", sub, exp)
                got += [f"s{sd}/{x}" for x in g]; missing += m
            print(f"  {len(got)} file(s) -> {dest}")
            meta_extra["files"] = got
            meta_extra["values"] = parse_values(dest)
            if missing:
                meta_extra["harvest_incomplete"] = missing
                print(f"  !! HARVEST INCOMPLETE — missing {missing}")
                # `remote` was a single-seed local that the multi-seed refactor removed; two
                # references survived it, and this one sat in the harvest-FAILURE branch — so the
                # message telling you how to recover your data was itself a NameError, exactly
                # when you needed it. Rebuild the path from the args that are actually in scope.
                _rem = ", ".join(f"/harvest/{args.state}_s{sd}"
                                 for sd in str(args.seed).split(",") if sd.strip())
                print(f"     the data is still on the Volume at {_rem}; re-fetch with")
                print(f"     modal_lane.py --state {args.state} --seed {args.seed} --refetch")
                rc = rc or 4
    except KeyboardInterrupt:
        print("\ninterrupted -- tearing the sandbox down before exiting")
        rc = 130
    except Exception as exc:
        print(f"\nERROR: {exc}")
        rc = rc if rc is not None else 1
        meta_extra["error"] = str(exc)
    finally:
        wall = time.time() - t0
        sweep = terminate_verified(modal, sb, f"{args.state} s{args.seed}") if sb else {
            "terminated": True, "note": "no sandbox was created"}
        meta = {
            "kind": kind, "state": states[0], "seed": seeds if len(seeds) > 1 else seeds[0],
            "cells": args.cells, "stagger_s": args.stagger,
            "parallel": bool(args.parallel),
            "requested": {"gpu": gpu, "cpu": cpu, "memory_mb": mem},
            # Record the device ACTUALLY served, not the tier requested: Modal served an
            # A100-SXM4-80GB against a request for A100-40GB, and a wall attributed to the
            # wrong silicon is how the void speedup table happened.
            "device_served": next((l.split(",")[0].strip() for l in lines
                                   if any(k in l for k in ("A100", "H100", "H200", "L40S",
                                                           "A10", "L4", "T4", "B200"))), None),
            "exit_code": rc,
            "wall_seconds": round(wall, 1),
            "rate_usd_per_hour": round(rate, 4),
            "cost_usd_estimate": round(cost_usd(gpu, cpu, mem, wall), 4),
            "cost_basis": "modal.com/pricing 2026-08-10: GPU + CPU + memory, per container-second",
            "volume": VOLUME, "app": APP_NAME,
            "engine": ENGINE, "v14": V14,
            "started_at": time.strftime("%Y-%m-%dT%H:%M:%S%z", time.localtime(t0)),
            "teardown": sweep,
            **meta_extra,
        }
        (dest / "run_metadata.json").write_text(json.dumps(meta, indent=2))
        print(f"\nteardown  : terminated={sweep.get('terminated')} "
              f"poll={sweep.get('poll')} strays={sweep.get('strays')}")
        print(f"cost      : ~${meta['cost_usd_estimate']:.3f} for {wall:.0f}s")
        print(f"archive   : {dest}")
        if sweep.get("strays"):
            print("  !! live sandboxes remain -- they bill until the idle window closes:")
            for s in sweep["strays"]:
                print(f"     modal.Sandbox.from_id('{s}').terminate()")
    return 0 if rc == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
