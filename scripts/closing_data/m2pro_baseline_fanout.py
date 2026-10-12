#!/usr/bin/env python3
"""M2 Pro lane — substrate-column baseline embedding fan-out driver (P3 board).

Builds the LIGHT baseline embeddings (B2b skip-gram, POI2Vec faithful, CTLE) on the
GATED stride-1 overlap base, TRAIN-ONLY per fold, for states x seeds {0,1,7,100} x
5 folds. (B2c one-hot64 is per-state and built separately — it is fold-independent.)

Per cell:
  1. STAGE frozen check2hgi reads into a per-cell scratch OUTPUT_DIR (POI2Vec + CTLE
     use the non-namespaced CHECK2HGI probe-engine and must not clobber the frozen
     substrate; B2b writes to its own namespaced dir and needs no staging).
  2. BUILD with --stride 1 and MTL_RAM_HEADROOM_GB=2 (the 16 GB default guard is too
     aggressive on a 24 GB box; the fold-split read is <=0.1 GB).
  3. The builder asserts row-alignment (next==next_region==seq) + val-user disjointness.
  4. KEEP embeddings.parquet + provenance + leak/fold markers into a consolidated
     handoff dir; DELETE the regennable next/next_region/sequences (CUDA regenerates
     them deterministically — see M2PRO_BUILD_LOG.md §4). DISK is the binding constraint.

Disk-floor stop: aborts before a cell if free space < --disk-floor-gb.
Resumable: skips a cell whose handoff embeddings.parquet already exists.

Handoff layout (the orchestrator consolidates / registers engines for the CUDA score):
  output/board_baselines/<baseline>/<state>/s<seed>_f<fold>/
      embeddings.parquet  next_build_provenance.json  LEAK_MARKER.txt

This driver does NOT run the matched-head comparison (CUDA-only, device-class rule).

Usage:
  PYTHONPATH=src .venv/bin/python scripts/closing_data/m2pro_baseline_fanout.py \
      --baselines b2b poi2vec ctle --states alabama arizona \
      --seeds 0 1 7 100 --folds 0 1 2 3 4 [--dry-run]
"""
from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
OUTPUT = REPO / "output"
HANDOFF = OUTPUT / "board_baselines"
PY = str(REPO / ".venv" / "bin" / "python")

# Builders that use the non-namespaced CHECK2HGI probe-engine -> need staged scratch.
STAGED = {"poi2vec", "ctle"}

# Per-build thread cap (string for env). Set in main from --threads so
# workers * THREADS ~= physical cores (avoids torch/BLAS oversubscription).
THREADS = "2"

# Compute device for the sub-builders. Default "cpu" (the M2 Pro lane). The A40
# lane overrides to "cuda" via --device (the heavy CTLE/POI2Vec/b2b CA/TX/FL cells
# handed off per M2PRO_BUILD_LOG.md §8). Set in main from --device.
DEVICE = "cpu"


def free_gb(path: Path) -> float:
    st = os.statvfs(path)
    return st.f_bavail * st.f_frsize / (1024 ** 3)


def avail_ram_gb() -> float:
    """Available system RAM in GB; +inf if psutil can't answer (don't gate on a
    failed probe — macOS psutil intermittently raises under pressure)."""
    try:
        import psutil
        return psutil.virtual_memory().available / (1024 ** 3)
    except Exception:
        return float("inf")


def wait_for_ram(floor_gb: float, tag: str, stop) -> None:
    """Block until available RAM >= floor (concurrent builds each hold GB-scale
    data; dispatching a new one under low RAM crashed the box). Caps the wait so
    a wrong estimate can't deadlock — proceeds after ~120 s."""
    waited = 0
    while avail_ram_gb() < floor_gb and not stop.is_set() and waited < 120:
        if waited == 0:
            print(f"{tag}  WAIT-RAM (avail {avail_ram_gb():.1f} GB < {floor_gb} GB)", flush=True)
        time.sleep(5)
        waited += 5


def stage_scratch(state: str, scratch: Path) -> None:
    """Replicate the smoke-script staging: copy the frozen reads the builder OVERWRITES
    (embeddings/next/sequences), symlink the read-only ones (region/graph)."""
    real = OUTPUT / "check2hgi" / state
    dst = scratch / "check2hgi" / state
    (dst / "temp").mkdir(parents=True, exist_ok=True)
    (dst / "input").mkdir(parents=True, exist_ok=True)
    shutil.copy2(real / "temp" / "sequences_next.parquet", dst / "temp" / "sequences_next.parquet")
    shutil.copy2(real / "input" / "next.parquet", dst / "input" / "next.parquet")
    shutil.copy2(real / "embeddings.parquet", dst / "embeddings.parquet")
    for name, sub in [("region_embeddings.parquet", ""), ("checkin_graph.pt", "temp")]:
        link = dst / sub / name if sub else dst / name
        if link.exists() or link.is_symlink():
            link.unlink()
        link.symlink_to((real / sub / name if sub else real / name).resolve())


def builder_cmd(baseline: str, state: str, seed: int, fold: int, scratch: Path | None,
                work: Path):
    """Return (argv, env, native_engine_dir) for one cell. native_engine_dir is where
    the builder writes embeddings.parquet. All heavy transient writes (native dir /
    scratch) land under ``work`` (set to internal disk to spare a flaky external SSD);
    the frozen check2hgi substrate is READ from the external OUTPUT root."""
    # Cap per-build thread pools: torch/BLAS otherwise each grab ALL cores, so N
    # concurrent torch builds (ctle/poi2vec) oversubscribe badly (load >> ncpu,
    # per-cell time explodes). With THREADS_PER_BUILD set so workers*threads ~= cores,
    # each build gets a fair slice and net throughput scales.
    env = dict(os.environ, PYTHONPATH="src", MTL_RAM_HEADROOM_GB="2",
               PYTHONUNBUFFERED="1",  # else epoch prints block-buffer to the log file
               OMP_NUM_THREADS=THREADS, MKL_NUM_THREADS=THREADS,
               OPENBLAS_NUM_THREADS=THREADS, VECLIB_MAXIMUM_THREADS=THREADS,
               NUMEXPR_NUM_THREADS=THREADS, PYTORCH_NUM_THREADS=THREADS)
    if baseline == "b2b":
        # OUTPUT_DIR -> work (writes land internal); read frozen substrate from OUTPUT.
        env["OUTPUT_DIR"] = str(work)
        argv = [PY, "scripts/baselines/build_b2b_skipgram_substrate.py",
                "--state", state, "--seed", str(seed), "--fold", str(fold),
                "--n-splits", "5", "--epochs", "5", "--dim", "64",
                "--stride", "1", "--device", DEVICE,
                "--read-output-dir", str(OUTPUT)]
        native = work / f"b2b_skipgram_s{seed}_f{fold}" / state
    elif baseline == "poi2vec":
        env["OUTPUT_DIR"] = str(scratch)
        argv = [PY, "scripts/baselines/build_poi2vec_substrate.py", state,
                "--seed", str(seed), "--fold", str(fold), "--n-splits", "5",
                "--epochs", "30", "--embed-dim", "64", "--user-dim", "64",
                "--theta", "0.05", "--route-count", "4", "--context-window", "9",
                "--loss-form", "mixture", "--stride", "1", "--device", DEVICE]
        native = scratch / "check2hgi" / state
    elif baseline == "ctle":
        env["OUTPUT_DIR"] = str(scratch)
        argv = [PY, "scripts/baselines/build_ctle_substrate.py",
                "--state", state, "--seed", str(seed), "--fold", str(fold),
                "--pretrain-epochs", "10", "--batch-size", "256", "--max-len", "64",
                "--lr", "1e-3", "--stride", "1", "--device", DEVICE]
        native = scratch / "check2hgi_ctle" / state
    else:
        raise ValueError(baseline)
    return argv, env, native


def keep_and_trim(baseline, state, seed, fold, native: Path):
    """Copy embeddings + markers to the handoff dir, then delete the regennable
    next/next_region. For staged builders the scratch is rmtree'd by the caller;
    for the non-staged b2b the native engine dir (which holds the multi-GB
    next/next_region) must be reclaimed HERE or it accumulates (FL/CA/TX b2b is
    3-11 GB/cell)."""
    hd = HANDOFF / baseline / state / f"s{seed}_f{fold}"
    hd.mkdir(parents=True, exist_ok=True)
    emb = native / "embeddings.parquet"
    assert emb.exists(), f"missing embeddings.parquet for {baseline}/{state} s{seed} f{fold}: {emb}"
    shutil.copy2(emb, hd / "embeddings.parquet")
    for marker in ["input/next_build_provenance.json", "CTLE_FOLD.txt"]:
        src = native / marker
        if src.exists():
            shutil.copy2(src, hd / Path(marker).name)
    (hd / "LEAK_MARKER.txt").write_text(
        f"baseline={baseline} state={state} seed={seed} fold={fold} stride=1 gated\n"
        f"TRAIN-ONLY per fold; row-align (next==next_region==seq) + val-user disjoint "
        f"asserted by the builder. next/next_region dropped (regen on CUDA, --stride 1).\n"
    )
    # Reclaim the non-staged native engine dir (embeddings already copied above).
    if baseline not in STAGED and native.exists():
        shutil.rmtree(native, ignore_errors=True)


def main():
    global THREADS, DEVICE, OUTPUT, HANDOFF
    ap = argparse.ArgumentParser()
    ap.add_argument("--baselines", nargs="+", default=["b2b", "poi2vec", "ctle"])
    ap.add_argument("--states", nargs="+", required=True)
    ap.add_argument("--seeds", nargs="+", type=int, default=[0, 1, 7, 100])
    ap.add_argument("--folds", nargs="+", type=int, default=[0, 1, 2, 3, 4])
    ap.add_argument("--disk-floor-gb", type=float, default=18.0,
                    help="abort before a cell if free space < this (CA/TX spike ~9 GB)")
    ap.add_argument("--workers", type=int, default=1,
                    help="concurrent cells (each build uses ~2 cores / ~1-2 GB at small "
                         "states). 1=serial. Keep low (1-2) for CA/TX (~9 GB transient "
                         "spike/cell + heavier I/O).")
    ap.add_argument("--work-dir", default=str(OUTPUT / "_scratch"),
                    help="root for ALL heavy transient writes (b2b native dir, "
                         "POI2Vec/CTLE scratch, logs). Point at an internal disk "
                         "(e.g. /private/tmp/board_work) to spare a flaky external "
                         "SSD — only the small final embeddings are written to the "
                         "external handoff. Frozen check2hgi is READ from OUTPUT.")
    ap.add_argument("--threads", type=int, default=3,
                    help="threads per build (torch/BLAS). Tune so workers*threads ~= "
                         "physical cores; default 3 (4 workers x 3 = 12 cores).")
    ap.add_argument("--ram-floor-gb", type=float, default=5.0,
                    help="a build waits before launching until this much RAM is free "
                         "(concurrent builds each hold GB-scale data; low RAM crashed "
                         "the box). Raise for big-state poi2vec/ctle.")
    ap.add_argument("--device", default="cpu",
                    help="compute device for the sub-builders. 'cpu' = M2 Pro lane; "
                         "'cuda' = A40 lane (the heavy CTLE/POI2Vec/b2b CA/TX/FL cells "
                         "handed off per M2PRO_BUILD_LOG.md §8).")
    ap.add_argument("--output-root", default=str(OUTPUT),
                    help="root that holds the frozen check2hgi substrate (READ) and "
                         "receives the deliverables (default = this checkout's output/). "
                         "On the A40 the driver runs from the worktree but must read/write "
                         "the MAIN repo's output/, so point this there.")
    ap.add_argument("--handoff-dir", default=None,
                    help="where the kept embeddings.parquet land "
                         "(default <output-root>/board_baselines). On a tight disk point "
                         "this at a scratch volume (e.g. /tmp/board_baselines) and migrate "
                         "to the repo output/ as space frees.")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    THREADS = str(args.threads)
    DEVICE = args.device
    OUTPUT = Path(args.output_root)
    HANDOFF = Path(args.handoff_dir) if args.handoff_dir else (OUTPUT / "board_baselines")

    work = Path(args.work_dir)
    work.mkdir(parents=True, exist_ok=True)
    cells = [(b, st, sd, fd)
             for b in args.baselines for st in args.states
             for sd in args.seeds for fd in args.folds]
    print(f"=== M2 Pro baseline fan-out: {len(cells)} cells "
          f"(baselines={args.baselines} states={args.states} "
          f"seeds={args.seeds} folds={args.folds}) ===", flush=True)
    print(f"    ext disk free={free_gb(OUTPUT):.1f} GB  floor={args.disk_floor_gb} GB  "
          f"work_dir={work} (free={free_gb(work):.1f} GB)", flush=True)

    state = {"done": 0, "skipped": 0, "failed": 0}
    lock = threading.Lock()
    stop = threading.Event()

    def run_cell(i, b, st, sd, fd):
        tag = f"[{i}/{len(cells)}] {b}/{st} s{sd} f{fd}"
        hd_emb = HANDOFF / b / st / f"s{sd}_f{fd}" / "embeddings.parquet"
        if hd_emb.exists():
            print(f"{tag}  SKIP (handoff exists)", flush=True)
            with lock:
                state["skipped"] += 1
            return
        if stop.is_set():
            return
        fg_ext, fg_work = free_gb(OUTPUT), free_gb(work)
        if fg_ext < args.disk_floor_gb or fg_work < args.disk_floor_gb:
            which = "ext" if fg_ext < args.disk_floor_gb else "work"
            print(f"{tag}  STOP: {which} disk low (ext={fg_ext:.1f} work={fg_work:.1f} GB "
                  f"< floor {args.disk_floor_gb} GB)", flush=True)
            stop.set()
            return
        if args.dry_run:
            print(f"{tag}  (dry-run)  free={fg_ext:.1f} GB", flush=True)
            return

        scratch = (work / f"{b}_{st}_s{sd}_f{fd}") if b in STAGED else None
        t0 = time.time()
        try:
            wait_for_ram(args.ram_floor_gb, tag, stop)
            if stop.is_set():
                return
            if scratch is not None:
                if scratch.exists():
                    shutil.rmtree(scratch)
                scratch.mkdir(parents=True)
                stage_scratch(st, scratch)
            argv, env, native = builder_cmd(b, st, sd, fd, scratch, work)
            log = work / f"log_{b}_{st}_s{sd}_f{fd}.txt"
            log.parent.mkdir(parents=True, exist_ok=True)
            with open(log, "w") as lf:
                r = subprocess.run(argv, env=env, cwd=str(REPO), stdout=lf,
                                   stderr=subprocess.STDOUT)
            if r.returncode != 0:
                print(f"{tag}  FAIL (exit {r.returncode}) — see {log}", flush=True)
                with lock:
                    state["failed"] += 1
                return
            keep_and_trim(b, st, sd, fd, native)
        except Exception as e:  # never let one cell kill the pool
            print(f"{tag}  FAIL ({type(e).__name__}: {e})", flush=True)
            with lock:
                state["failed"] += 1
            return
        finally:
            if scratch is not None and scratch.exists():
                shutil.rmtree(scratch)
        with lock:
            state["done"] += 1
        print(f"{tag}  OK  {time.time()-t0:.0f}s  free={free_gb(OUTPUT):.1f} GB", flush=True)

    if args.workers <= 1:
        for i, (b, st, sd, fd) in enumerate(cells, 1):
            if stop.is_set():
                break
            run_cell(i, b, st, sd, fd)
    else:
        print(f"    parallel: {args.workers} workers", flush=True)
        with ThreadPoolExecutor(max_workers=args.workers) as ex:
            futs = [ex.submit(run_cell, i, *c) for i, c in enumerate(cells, 1)]
            for _ in as_completed(futs):
                pass

    print(f"=== fan-out end: done={state['done']} skipped={state['skipped']} "
          f"failed={state['failed']} free={free_gb(OUTPUT):.1f} GB ===", flush=True)


if __name__ == "__main__":
    main()
