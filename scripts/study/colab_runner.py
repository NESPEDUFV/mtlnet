"""Run study tests on Google Colab and package results for import on the main machine.

Designed to parallelize ablations: assign `test_id`s to Colab sessions while the
primary machine handles others. Each test produces a portable tarball under
Drive that `/study import` can consume.

Typical Colab flow (inside a notebook cell):

    # cell 1 — bootstrap (first time per session)
    !python /content/PoiMtlNet/scripts/study/colab_runner.py bootstrap --drive-root /content/drive/MyDrive/mestrado/PoiMtlNet

    # cell 2 — list planned tests
    !python /content/PoiMtlNet/scripts/study/colab_runner.py list --phase P1

    # cell 3 — run one
    !python /content/PoiMtlNet/scripts/study/colab_runner.py run --phase P1 --test-id P1_AL_smoke

    # the tarball path is printed at the end. Sync Drive, then on the Mac:
    # /study import --run-dir <unpacked> --phase P1 --test-id P1_AL_smoke

Also importable: `from colab_runner import colab_bootstrap; colab_bootstrap(...)`.
"""

from __future__ import annotations

import argparse
import json
import os
import shlex
import shutil
import subprocess
import sys
import tarfile
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# Resolve REPO_ROOT based on this file's location. Colab clones to /content/PoiMtlNet
# so this works both there and on the Mac.
REPO_ROOT = Path(__file__).resolve().parents[2]
STATE_PATH = REPO_ROOT / "docs" / "studies" / "state.json"

COLAB_DEFAULT_DRIVE = Path("/content/drive/MyDrive/mestrado/PoiMtlNet")
DEFAULT_REPO_URL = "https://github.com/VitorHugoOli/PoiMtlNet.git"


# ---------------------------------------------------------------------------
# Bootstrap (setup)
# ---------------------------------------------------------------------------


def _run(cmd: list[str], *, check: bool = True, cwd: Path | None = None, quiet: bool = False) -> int:
    if not quiet:
        print(f"$ {' '.join(shlex.quote(c) for c in cmd)}")
    proc = subprocess.run(cmd, cwd=cwd)
    if check and proc.returncode != 0:
        raise SystemExit(f"command failed (exit {proc.returncode}): {cmd}")
    return proc.returncode


def _pip(*args: str, quiet: bool = True) -> None:
    flags = ["-q"] if quiet else []
    _run([sys.executable, "-m", "pip", "install", *flags, *args], quiet=quiet)


def colab_bootstrap(
    drive_root: Path | str = COLAB_DEFAULT_DRIVE,
    repo_dir: Path | str = Path("/content/PoiMtlNet"),
    repo_url: str = DEFAULT_REPO_URL,
    branch: str = "main",
    skip_pip: bool = False,
) -> dict[str, str]:
    """Mount Drive (no-op if already), clone/pull repo, install deps, set env vars.

    Safe to call multiple times. Returns a dict of resolved paths (same keys the
    notebook uses): DATA_ROOT, OUTPUT_DIR, RESULTS_ROOT, REPO_DIR.
    """
    drive_root = Path(drive_root)
    repo_dir = Path(repo_dir)

    # 1. Mount Drive (Colab only). Silently skip off-Colab.
    try:
        from google.colab import drive  # type: ignore

        if not Path("/content/drive").exists() or not any(Path("/content/drive").iterdir()):
            drive.mount("/content/drive")
        else:
            print("[bootstrap] Drive already mounted")
    except Exception:
        print("[bootstrap] not on Colab (google.colab unavailable) — skipping drive mount")

    # 2. Resolve layout and create dirs
    data_root = drive_root / "data"
    output_dir = drive_root / "output"
    results_root = drive_root / "results"
    for p in (data_root, output_dir, results_root):
        p.mkdir(parents=True, exist_ok=True)

    os.environ["DATA_ROOT"] = str(data_root)
    os.environ["OUTPUT_DIR"] = str(output_dir)
    os.environ["RESULTS_ROOT"] = str(results_root)

    print(f"[bootstrap] DATA_ROOT    = {data_root}")
    print(f"[bootstrap] OUTPUT_DIR   = {output_dir}")
    print(f"[bootstrap] RESULTS_ROOT = {results_root}")

    # 3. Clone / pull repo
    if repo_dir.exists():
        _run(["git", "-C", str(repo_dir), "fetch", "--quiet"])
        _run(["git", "-C", str(repo_dir), "checkout", branch])
        _run(["git", "-C", str(repo_dir), "pull", "--ff-only", "origin", branch])
    else:
        _run(["git", "clone", "--branch", branch, repo_url, str(repo_dir)])
    _run(["git", "-C", str(repo_dir), "log", "--oneline", "-3"], quiet=False)

    # 4. Install deps (Colab often already has most, we add the missing ones)
    if not skip_pip:
        reqs = repo_dir / "requirements_colab.txt"
        if reqs.exists():
            _pip("-r", str(reqs))
        # Extras the notebook adds
        _pip("cvxpy", "torch-geometric", "pytorch_warmup", "torchmetrics", "fvcore")
        try:
            import torch  # noqa
            tv = torch.__version__
            _pip("torch-scatter", "-f", f"https://data.pyg.org/whl/torch-{tv}.html")
            _pip("torch-sparse", "-f", f"https://data.pyg.org/whl/torch-{tv}.html")
            _pip("torch-cluster", "-f", f"https://data.pyg.org/whl/torch-{tv}.html")
        except Exception as exc:
            print(f"[bootstrap] WARN: skipping PyG scatter/sparse/cluster install: {exc}")

    # 5. sys.path so `scripts/train.py` resolves project modules
    for sub in ("src", "research"):
        p = str(repo_dir / sub)
        if p not in sys.path:
            sys.path.insert(0, p)

    return {
        "REPO_DIR": str(repo_dir),
        "DATA_ROOT": str(data_root),
        "OUTPUT_DIR": str(output_dir),
        "RESULTS_ROOT": str(results_root),
    }


# ---------------------------------------------------------------------------
# Test lookup + execution
# ---------------------------------------------------------------------------


def _load_state(state_path: Path | None = None) -> dict[str, Any]:
    path = state_path or STATE_PATH
    if not path.exists():
        raise SystemExit(
            f"state.json not found at {path}. The Colab worker reads tests from "
            "the committed state.json — push enrollment changes from the Mac first."
        )
    with path.open() as fh:
        return json.load(fh)


def _find_test(state: dict[str, Any], phase: str, test_id: str) -> dict[str, Any]:
    entry = state.get("phases", {}).get(phase, {}).get("tests", {}).get(test_id)
    if entry is None:
        raise SystemExit(f"no test {test_id} under phase {phase} in state.json")
    return entry


def _build_command(config: dict[str, Any]) -> list[str]:
    cmd: list[str] = [sys.executable, "scripts/train.py"]
    arg_map = {
        "task": "--task", "state": "--state", "engine": "--engine",
        "model_name": "--model", "candidate": "--candidate",
        "mtl_loss": "--mtl-loss", "seed": "--seed",
        "epochs": "--epochs", "folds": "--folds",
        "embedding_dim": "--embedding-dim",
        "gradient_accumulation_steps": "--gradient-accumulation-steps",
        "next_target": "--next-target", "category_weight": "--category-weight",
    }
    for key, flag in arg_map.items():
        if config.get(key) is not None:
            cmd.extend([flag, str(config[key])])
    for k, v in (config.get("model_params") or {}).items():
        cmd.extend(["--model-param", f"{k}={v}"])
    for k, v in (config.get("mtl_loss_params") or {}).items():
        cmd.extend(["--mtl-loss-param", f"{k}={v}"])
    if config.get("mtl_loss") in {"cagrad", "aligned_mtl", "pcgrad"}:
        if "--gradient-accumulation-steps" not in cmd:
            cmd.extend(["--gradient-accumulation-steps", "1"])
    return cmd


def _detect_run_dir(config: dict[str, Any], before: set[Path]) -> Path | None:
    engine = config.get("engine")
    state_name = config.get("state")
    if not (engine and state_name):
        return None
    # IoPaths.get_results_dir uses RESULTS_ROOT env var; default is <repo>/results
    results_root = Path(os.environ.get("RESULTS_ROOT", REPO_ROOT / "results"))
    parent = results_root / engine / state_name
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


def _package_artifact(run_dir: Path, out_dir: Path, test_id: str, meta: dict[str, Any]) -> Path:
    """Tar the run_dir + write a companion metadata JSON — everything needed for import."""
    out_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    archive = out_dir / f"{test_id}_{stamp}.tar.gz"
    with tarfile.open(archive, "w:gz") as tar:
        tar.add(run_dir, arcname=run_dir.name)
    meta_path = archive.with_suffix(".meta.json")
    with meta_path.open("w") as fh:
        json.dump(meta, fh, indent=2)
    return archive


def run_test(
    phase: str,
    test_id: str,
    *,
    artifacts_dir: Path | None = None,
    dry_run: bool = False,
    state_path: Path | None = None,
) -> int:
    state = _load_state(state_path)
    entry = _find_test(state, phase, test_id)
    config = entry.get("config") or {}
    if not config:
        raise SystemExit(f"{test_id}: missing `config` in state.json — nothing to run")

    cmd = _build_command(config)
    print(f"[colab] test_id={test_id}")
    print(f"[colab] cmd: {' '.join(shlex.quote(c) for c in cmd)}")
    if dry_run:
        print("[colab] dry-run — not executing")
        return 0

    engine = config.get("engine", "")
    state_name = config.get("state", "")
    results_root = Path(os.environ.get("RESULTS_ROOT", REPO_ROOT / "results"))
    parent = results_root / engine / state_name
    before = set(p for p in parent.iterdir() if p.is_dir()) if parent.exists() else set()

    t0 = time.time()
    proc = subprocess.run(cmd, cwd=REPO_ROOT)
    elapsed = time.time() - t0

    if proc.returncode != 0:
        print(f"[colab] training FAILED (exit {proc.returncode}) after {elapsed:.0f}s")
        return proc.returncode

    run_dir = _detect_run_dir(config, before)
    if run_dir is None:
        print("[colab] WARN: could not locate run_dir after training — nothing packaged")
        return 1
    print(f"[colab] run_dir: {run_dir}")

    git_commit = "unknown"
    try:
        git_commit = subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=REPO_ROOT, stderr=subprocess.DEVNULL
        ).decode().strip()
    except Exception:
        pass

    meta = {
        "test_id": test_id,
        "phase": phase,
        "claim_ids": entry.get("claim_ids") or [],
        "config": config,
        "run_dir_relative": run_dir.name,
        "run_dir_absolute": str(run_dir),
        "wall_clock_seconds": round(elapsed, 1),
        "git_commit": git_commit,
        "packaged_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "ran_on": os.environ.get("COLAB_RUNTIME_NAME") or "colab",
    }

    out_dir = Path(artifacts_dir) if artifacts_dir else (
        Path(os.environ.get("RESULTS_ROOT", REPO_ROOT / "results")) / "_study_artifacts"
    )
    archive = _package_artifact(run_dir, out_dir, test_id, meta)
    meta_path = archive.with_suffix(".meta.json")

    print()
    print(f"[colab] packaged → {archive}  ({archive.stat().st_size / 1e6:.1f} MB)")
    print(f"[colab] metadata → {meta_path}")
    print()
    print("On your primary machine, after syncing Drive:")
    print(f"  tar -xzf {archive.name} -C /tmp")
    print(
        f"  python scripts/study/study.py import "
        f"--run-dir /tmp/{run_dir.name} --phase {phase} --test-id {test_id} "
        f"--claims {' '.join(meta['claim_ids']) if meta['claim_ids'] else '<claims>'}"
    )
    return 0


def list_tests(phase: str | None, state_path: Path | None = None) -> int:
    state = _load_state(state_path)
    phases = [phase] if phase else ["P0", "P1", "P2", "P3", "P4", "P5", "P6"]
    any_printed = False
    for ph in phases:
        tests = state.get("phases", {}).get(ph, {}).get("tests", {})
        for tid, entry in tests.items():
            if phase is None and entry.get("status") != "planned":
                continue
            cfg = entry.get("config") or {}
            state_name = cfg.get("state", "?")
            engine = cfg.get("engine", "?")
            print(
                f"  [{ph}] {tid}  status={entry.get('status', '?'):<10} "
                f"state={state_name:<10} engine={engine:<10} "
                f"claims={entry.get('claim_ids') or []}"
            )
            any_printed = True
    if not any_printed:
        print(f"(no planned tests in {phase or 'any phase'})")
    return 0


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def _cmd_bootstrap(args: argparse.Namespace) -> int:
    colab_bootstrap(
        drive_root=args.drive_root,
        repo_dir=args.repo_dir,
        repo_url=args.repo_url,
        branch=args.branch,
        skip_pip=args.skip_pip,
    )
    return 0


def _cmd_run(args: argparse.Namespace) -> int:
    return run_test(
        phase=args.phase,
        test_id=args.test_id,
        artifacts_dir=Path(args.artifacts_dir) if args.artifacts_dir else None,
        dry_run=args.dry_run,
    )


def _cmd_list(args: argparse.Namespace) -> int:
    return list_tests(args.phase)


def main() -> int:
    p = argparse.ArgumentParser(prog="colab_runner", description="Colab study worker.")
    sub = p.add_subparsers(dest="command", required=True)

    sp = sub.add_parser("bootstrap", help="Mount Drive, clone repo, install deps.")
    sp.add_argument("--drive-root", default=str(COLAB_DEFAULT_DRIVE))
    sp.add_argument("--repo-dir", default="/content/PoiMtlNet")
    sp.add_argument("--repo-url", default=DEFAULT_REPO_URL)
    sp.add_argument("--branch", default="main")
    sp.add_argument("--skip-pip", action="store_true", help="Skip pip install (deps already set up).")
    sp.set_defaults(func=_cmd_bootstrap)

    sp = sub.add_parser("run", help="Run one planned test and package the result.")
    sp.add_argument("--phase", required=True)
    sp.add_argument("--test-id", required=True)
    sp.add_argument("--artifacts-dir", default=None,
                    help="Where to drop the tarball (default: $RESULTS_ROOT/_study_artifacts).")
    sp.add_argument("--dry-run", action="store_true")
    sp.set_defaults(func=_cmd_run)

    sp = sub.add_parser("list", help="List planned tests from state.json.")
    sp.add_argument("--phase", default=None)
    sp.set_defaults(func=_cmd_list)

    args = p.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
