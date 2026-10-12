"""Launch the next planned test from state.json.

A test entry is expected to carry:
  - test_id, phase, claim_ids
  - config: {state, engine, task?, model_name?, mtl_loss?, seed, epochs, folds,
             arch?, optim?, tier?, ...}
  - (optional) command: pre-built CLI; if present, used verbatim
  - (optional) expected: {joint_range, cat_f1_range, ...}

New in parallel-infra update
------------------------------
  --no-sync       Write results to disk but do NOT update state.json.
                  Heartbeat still runs.  Use for parallel-worker mode.
  --state/-s      Filter planned tests by state code(s) (comma-separated or multi).
  --tier/-t       Filter by tier (screen, promote, confirm, heavy).
  --arch/-a       Filter by arch id.
  --optim/-o      Filter by optimizer id.
  --max-runtime-min N  Skip tests whose tier estimate exceeds N minutes.
  --worker-id     Override the worker identifier in heartbeat filenames.
                  Falls back to $WORKER_ID env var then socket.gethostname().

This script does NOT enumerate the full phase grid — that lives in phase docs.
It just picks one entry marked `planned` (filtered if flags given) and runs it.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shlex
import socket
import subprocess
import sys
import threading
import time
from pathlib import Path
from typing import Any

from _state import (
    REPO_ROOT,
    TIER_MINUTES,
    find_all_planned,
    find_next_planned,
    mutate_state,
    read_state,
    utcnow,
)


# ---------------------------------------------------------------------------
# Command building
# ---------------------------------------------------------------------------


def _build_command(config: dict[str, Any]) -> list[str]:
    cmd: list[str] = [sys.executable, "scripts/train.py"]
    arg_map = {
        "task": "--task",
        "state": "--state",
        "engine": "--engine",
        "model_name": "--model",
        "model": "--model",       # alias used by enroll_p1
        "candidate": "--candidate",
        "mtl_loss": "--mtl-loss",
        "seed": "--seed",
        "epochs": "--epochs",
        "folds": "--folds",
        "embedding_dim": "--embedding-dim",
        "gradient_accumulation_steps": "--gradient-accumulation-steps",
        "batch_size": "--batch-size",
        "next_target": "--next-target",
        "category_weight": "--category-weight",
    }
    # model_name and model are aliases; only emit one flag
    used_model_flag = False
    for key, flag in arg_map.items():
        if key in ("model_name", "model"):
            if used_model_flag:
                continue
            if key in config and config[key] is not None:
                cmd.extend([flag, str(config[key])])
                used_model_flag = True
            continue
        if key in config and config[key] is not None:
            cmd.extend([flag, str(config[key])])

    for k, v in (config.get("model_params") or {}).items():
        cmd.extend(["--model-param", f"{k}={v}"])
    for k, v in (config.get("mtl_loss_params") or {}).items():
        cmd.extend(["--mtl-loss-param", f"{k}={v}"])

    if config.get("mtl_loss") in {"cagrad", "aligned_mtl", "pcgrad"}:
        if "--gradient-accumulation-steps" not in cmd:
            cmd.extend(["--gradient-accumulation-steps", "1"])

    if config.get("tier") in {"screen", "promote"}:
        cmd.append("--no-checkpoints")

    return cmd


# ---------------------------------------------------------------------------
# Git helpers
# ---------------------------------------------------------------------------


def _current_commit() -> str:
    try:
        out = subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=REPO_ROOT, stderr=subprocess.DEVNULL
        )
        return out.decode().strip()
    except Exception:
        return "unknown"


# ---------------------------------------------------------------------------
# Preflight (file existence)
# ---------------------------------------------------------------------------


def _preflight(config: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    engine = config.get("engine")
    state = config.get("state")
    if not engine or not state:
        errors.append("config missing engine/state")
        return errors
    cat = REPO_ROOT / "output" / engine / state / "input" / "category.parquet"
    nxt = REPO_ROOT / "output" / engine / state / "input" / "next.parquet"
    task = config.get("task", "mtl")
    if task in {"mtl", "category"} and not cat.exists():
        errors.append(f"missing {cat}")
    if task in {"mtl", "next"} and not nxt.exists():
        errors.append(f"missing {nxt}")
    return errors


# ---------------------------------------------------------------------------
# Hash-check (integrity preflight)
# ---------------------------------------------------------------------------


def _sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()


def _hash_preflight(config: dict[str, Any]) -> list[str]:
    """Check SHA-256 of input parquets against fold meta.  Returns list of error strings."""
    errors: list[str] = []
    engine = config.get("engine")
    state = config.get("state")
    if not engine or not state:
        return errors  # basic preflight will catch this

    task = config.get("task", "mtl")
    folds_dir = REPO_ROOT / "output" / engine / state / "folds"
    meta_file = folds_dir / f"fold_indices_{task}.meta.json"

    if not meta_file.exists():
        freeze_cmd = (
            f"python scripts/study/freeze_folds.py "
            f"--state {state} --engine {engine} --task {task}"
        )
        errors.append(
            f"Fold meta not found: {meta_file}\n"
            f"  Run: {freeze_cmd}"
        )
        return errors

    try:
        meta = json.loads(meta_file.read_text())
    except Exception as exc:
        errors.append(f"Cannot read fold meta {meta_file}: {exc}")
        return errors

    sigs = meta.get("inputs_signatures") or {}
    for name, sig_entry in sigs.items():
        # Paths stored as repo-relative posix strings
        rel_path = sig_entry.get("path") or sig_entry.get("file_path")
        stored_sha = sig_entry.get("sha256")
        if not rel_path or not stored_sha:
            continue
        parquet_path = REPO_ROOT / rel_path
        if not parquet_path.exists():
            errors.append(f"Input parquet missing: {parquet_path}")
            continue
        actual_sha = _sha256_file(parquet_path)
        if actual_sha != stored_sha:
            freeze_cmd = (
                f"python scripts/study/freeze_folds.py "
                f"--state {state} --engine {engine} --task {task} --force"
            )
            errors.append(
                f"Hash mismatch for {parquet_path.name}:\n"
                f"  stored : {stored_sha}\n"
                f"  actual : {actual_sha}\n"
                f"  To refreeze: {freeze_cmd}"
            )
    return errors


# ---------------------------------------------------------------------------
# Heartbeat daemon
# ---------------------------------------------------------------------------


def _resolve_worker_id(worker_id_arg: str | None) -> str:
    if worker_id_arg:
        return worker_id_arg
    env_id = os.environ.get("WORKER_ID")
    if env_id:
        return env_id
    try:
        return socket.gethostname()
    except Exception:
        return "unknown"


class _HeartbeatThread(threading.Thread):
    """Daemon thread that writes a heartbeat file every `interval` seconds."""

    def __init__(self, path: Path, interval: float = 300.0) -> None:
        super().__init__(daemon=True)
        self._path = path
        self._interval = interval
        self._stop_event = threading.Event()

    def run(self) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        while not self._stop_event.wait(timeout=self._interval):
            try:
                self._path.write_text(utcnow())
            except Exception:
                pass

    def stop(self, remove: bool = True) -> None:
        self._stop_event.set()
        self.join(timeout=10)
        if remove:
            try:
                self._path.unlink(missing_ok=True)
            except Exception:
                pass


# ---------------------------------------------------------------------------
# Run-dir detection
# ---------------------------------------------------------------------------


def _detect_run_dir(config: dict[str, Any], before: set[Path]) -> Path | None:
    """Glob the results dir for a newly-created training run matching config."""
    engine = config.get("engine")
    state = config.get("state")
    if not (engine and state):
        return None
    parent = REPO_ROOT / "results" / engine / state
    if not parent.exists():
        return None
    candidates = [
        p for p in parent.iterdir()
        if p.is_dir() and p not in before and (p / "summary" / "full_summary.json").exists()
    ]
    if not candidates:
        return None
    candidates.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    return candidates[0]


# ---------------------------------------------------------------------------
# Core launch logic
# ---------------------------------------------------------------------------


def launch(
    phase: str | None,
    test_id: str | None,
    dry_run: bool,
    *,
    no_sync: bool = False,
    filter_states: list[str] | None = None,
    filter_tiers: list[str] | None = None,
    filter_archs: list[str] | None = None,
    filter_optims: list[str] | None = None,
    max_runtime_min: int | None = None,
    worker_id: str | None = None,
    heartbeat_interval: float = 300.0,
) -> int:
    # Resolve target test + build command WITHOUT mutating state yet.
    state = read_state()
    if test_id:
        phase = phase or state.get("current_phase")
        phase_tests = state.get("phases", {}).get(phase, {}).get("tests", {})
        entry = phase_tests.get(test_id)
        if entry is None:
            print(f"[launch] no test {test_id} in phase {phase}", file=sys.stderr)
            return 2
    else:
        if dry_run:
            # Show filtered queue without launching
            matches = find_all_planned(
                state, phase,
                filter_states=filter_states,
                filter_tiers=filter_tiers,
                filter_archs=filter_archs,
                filter_optims=filter_optims,
                max_runtime_min=max_runtime_min,
            )
            if not matches:
                print(f"[launch] no planned tests match filters in phase "
                      f"{phase or state.get('current_phase')}")
                return 1
            print(f"[launch] dry-run — {len(matches)} test(s) matching filters:")
            for ph, tid, e in matches:
                cfg = e.get("config", {})
                tier = cfg.get("tier", "?")
                print(f"  [{ph}] {tid}  tier={tier}")
            print("[launch] dry-run — state unchanged, not executing")
            return 0

        found = find_next_planned(
            state, phase,
            filter_states=filter_states,
            filter_tiers=filter_tiers,
            filter_archs=filter_archs,
            filter_optims=filter_optims,
            max_runtime_min=max_runtime_min,
        )
        if found is None:
            print(f"[launch] no planned tests match filters in phase "
                  f"{phase or state.get('current_phase')}")
            return 1
        phase, test_id, entry = found

    config = entry.get("config", {})

    errors = _preflight(config)
    if errors:
        print(f"[launch] preflight failed for {test_id}:")
        for e in errors:
            print(f"  FAIL  {e}")
        return 2

    hash_errors = _hash_preflight(config)
    if hash_errors:
        print(f"[launch] hash-check FAILED for {test_id}:")
        for e in hash_errors:
            print(f"  FAIL  {e}")
        return 3

    if entry.get("command"):
        cmd = shlex.split(entry["command"])
    else:
        cmd = _build_command(config)

    print(f"[launch] {test_id}")
    print(f"  cmd: {' '.join(shlex.quote(c) for c in cmd)}")
    if no_sync:
        print("  mode: --no-sync (state.json will NOT be updated)")

    if dry_run:
        print("[launch] dry-run — state unchanged, not executing")
        return 0

    # Snapshot existing run dirs BEFORE training so we can identify the new one.
    engine = config.get("engine", "")
    state_name = config.get("state", "")
    parent_dir = REPO_ROOT / "results" / engine / state_name
    before_run_dirs = set(p for p in parent_dir.iterdir() if p.is_dir()) if parent_dir.exists() else set()

    resolved_worker_id = _resolve_worker_id(worker_id)
    heartbeat_path = parent_dir / test_id / f".worker-{resolved_worker_id}.heartbeat"

    if not no_sync:
        with mutate_state() as st:
            st["phases"][phase]["tests"][test_id] = {
                **entry,
                "command": " ".join(shlex.quote(c) for c in cmd),
                "git_commit": _current_commit(),
                "started_at": utcnow(),
                "status": "running",
            }

    # Start heartbeat
    hb = _HeartbeatThread(heartbeat_path, interval=heartbeat_interval)
    hb.start()
    # Write initial heartbeat immediately
    try:
        heartbeat_path.parent.mkdir(parents=True, exist_ok=True)
        heartbeat_path.write_text(utcnow())
    except Exception:
        pass

    env = os.environ.copy()
    t0 = time.time()
    try:
        proc = subprocess.run(cmd, cwd=REPO_ROOT, env=env)
    except KeyboardInterrupt:
        hb.stop(remove=False)  # leave heartbeat stale on interrupt
        print("[launch] interrupted", file=sys.stderr)
        if not no_sync:
            with mutate_state() as st:
                st["phases"][phase]["tests"][test_id].update(
                    {"status": "failed", "finished_at": utcnow(), "notes": "interrupted"}
                )
        return 130

    elapsed = time.time() - t0
    hb.stop(remove=True)  # clean exit → remove heartbeat

    run_dir = _detect_run_dir(config, before_run_dirs)

    if not no_sync:
        with mutate_state() as st:
            entry_out = st["phases"][phase]["tests"][test_id]
            entry_out["finished_at"] = utcnow()
            entry_out["wall_clock_seconds"] = round(elapsed, 1)
            if run_dir is not None:
                entry_out["run_dir"] = str(run_dir.relative_to(REPO_ROOT))
            if proc.returncode == 0:
                entry_out["status"] = "completed"
                where = entry_out.get("run_dir", "(run_dir not detected)")
                print(f"[launch] completed in {elapsed:.0f}s.")
                print(f"  run_dir: {where}")
                print(f"  next:    /study import --run-dir {where} --phase {phase} --test-id {test_id}")
            else:
                entry_out["status"] = "failed"
                entry_out["notes"] = f"exit_code={proc.returncode}"
                print(f"[launch] FAILED (exit {proc.returncode}) after {elapsed:.0f}s")
    else:
        if proc.returncode == 0:
            where = str(run_dir.relative_to(REPO_ROOT)) if run_dir else "(run_dir not detected)"
            print(f"[launch] completed in {elapsed:.0f}s (--no-sync: state.json unchanged).")
            print(f"  run_dir: {where}")
            print(
                f"  import:  python scripts/study/archive_result.py "
                f"--run-dir {where} --phase {phase} --test-id {test_id} --no-state"
            )
        else:
            print(f"[launch] FAILED (exit {proc.returncode}) after {elapsed:.0f}s "
                  f"(--no-sync: state.json unchanged)")

    return proc.returncode


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def _parse_csv(val: str | None) -> list[str] | None:
    if val is None:
        return None
    return [v.strip() for v in val.split(",") if v.strip()]


def main() -> int:
    parser = argparse.ArgumentParser(description="Launch the next planned study test.")
    parser.add_argument("--phase", default=None, help="Phase to launch from (default: current_phase).")
    parser.add_argument("--test-id", default=None, help="Explicit test_id (overrides filters).")
    parser.add_argument("--dry-run", action="store_true", help="Print command/queue without executing.")
    parser.add_argument(
        "--no-sync", action="store_true",
        help="Do not update state.json running/completed status. Heartbeat still writes.",
    )
    # Filters
    parser.add_argument(
        "--state", "-s", default=None,
        help="Comma-separated state code(s) to filter on, e.g. AL,AZ.",
    )
    parser.add_argument(
        "--tier", "-t", default=None,
        help="Comma-separated tier(s): screen,promote,confirm,heavy.",
    )
    parser.add_argument(
        "--arch", "-a", default=None,
        help="Comma-separated arch id(s): base,cgc22,cgc21,mmoe4,dsk42.",
    )
    parser.add_argument(
        "--optim", "-o", default=None,
        help="Comma-separated optimizer id(s).",
    )
    parser.add_argument(
        "--max-runtime-min", type=int, default=None, metavar="N",
        help="Skip tests whose tier estimate exceeds N minutes.",
    )
    parser.add_argument(
        "--worker-id", default=None,
        help="Worker identifier for heartbeat file names (default: $WORKER_ID or hostname).",
    )
    args = parser.parse_args()
    return launch(
        args.phase,
        args.test_id,
        args.dry_run,
        no_sync=args.no_sync,
        filter_states=_parse_csv(args.state),
        filter_tiers=_parse_csv(args.tier),
        filter_archs=_parse_csv(args.arch),
        filter_optims=_parse_csv(args.optim),
        max_runtime_min=args.max_runtime_min,
        worker_id=args.worker_id,
    )


if __name__ == "__main__":
    sys.exit(main())
