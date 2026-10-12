"""Enroll P1 planned tests into state.json from the P1_grid.yaml grid spec.

Generates test IDs matching: P1_<STATE>_<stage>_<arch>_<optim>_seed<N>
Example:                      P1_AL_screen_dsk42_aligned_mtl_seed42

Reads the grid from docs/archive/fusion-study/phases/P1_grid.yaml (or --grid-file).
Idempotent: running twice does not duplicate entries.

Usage
-----
    # Dry-run — lists what would be enrolled without touching state.json
    python scripts/study/enroll_p1.py --dry-run

    # Enroll all P1a screen tests
    python scripts/study/enroll_p1.py --stage screen

    # Enroll all stages (screen + promote + confirm) for Alabama only
    python scripts/study/enroll_p1.py --state AL

    # Custom grid file
    python scripts/study/enroll_p1.py --grid-file path/to/P1_grid.yaml
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

# Resolve repo root from this file's location
_REPO_ROOT = Path(__file__).resolve().parents[2]
_STUDY_SCRIPTS = Path(__file__).resolve().parent

# Make _state importable (scripts/study lives on path)
if str(_STUDY_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_STUDY_SCRIPTS))

from _state import STUDIES_DIR, _normalize_state, get_test, mutate_state, read_state, set_test, utcnow  # noqa: E402

DEFAULT_GRID_FILE = STUDIES_DIR / "phases" / "P1_grid.yaml"

# Tier → approximate minutes (used by --max-runtime-min filter in launch_test.py).
# Must stay in sync with TIER_MINUTES in launch_test.py.
TIER_MINUTES: dict[str, int] = {
    "screen": 3,
    "promote": 6,
    "confirm": 30,
    "heavy": 120,
}


def _load_grid(grid_file: Path) -> dict[str, Any]:
    """Load grid YAML; require PyYAML."""
    try:
        import yaml  # type: ignore
    except ImportError as exc:
        raise SystemExit(
            "PyYAML is required: pip install pyyaml"
        ) from exc
    with grid_file.open() as fh:
        return yaml.safe_load(fh)


def _make_test_id(state: str, stage: str, arch_id: str, optim_id: str, seed: int) -> str:
    return f"P1_{state}_{stage}_{arch_id}_{optim_id}_seed{seed}"


def _make_entry(
    test_id: str,
    state: str,
    stage: str,
    arch: dict[str, Any],
    optim: dict[str, Any],
    stage_cfg: dict[str, Any],
    claim_ids: list[str],
    seed: int,
    engine_defaults: dict[str, Any] | None = None,
) -> dict[str, Any]:
    engine = "fusion"
    config: dict[str, Any] = {
        "state": _normalize_state(state),  # AL → alabama (scripts/train.py expects full name)
        "engine": engine,
        "task": "mtl",
        "arch": arch["id"],
        "model": arch["model"],
        "model_params": arch.get("model_params") or {},
        "optim": optim["id"],
        "mtl_loss": optim["id"],
        "stage": stage,
        "tier": stage_cfg["tier"],
        "seed": seed,
        "epochs": stage_cfg["epochs"],
        "folds": stage_cfg["folds"],
        "batch_size": stage_cfg["batch_size"],
        "gradient_accumulation_steps": stage_cfg["gradient_accumulation_steps"],
    }
    # Inject engine defaults (e.g. embedding_dim=128 for fusion) so launch_test.py
    # forwards --embedding-dim to train.py. Without this, fusion would silently
    # train with feature_size=64.
    for k, v in ((engine_defaults or {}).get(engine) or {}).items():
        config.setdefault(k, v)
    # Gradient-surgery methods require grad_accum=1; already set in grid but add note.
    if optim["id"] in {"cagrad", "aligned_mtl", "pcgrad"}:
        config["gradient_accumulation_steps"] = 1

    expected: dict[str, Any] = dict(stage_cfg.get("expected") or {})

    return {
        "test_id": test_id,
        "phase": "P1",
        "status": "planned",
        "claim_ids": list(claim_ids),
        "description": (
            f"P1 {stage}: {arch['id']} × {optim['id']} on {state} (fusion, seed {seed})"
        ),
        "config": config,
        "expected": expected,
        "enrolled_at": utcnow(),
    }


def generate_entries(
    grid: dict[str, Any],
    *,
    filter_states: list[str] | None = None,
    filter_stages: list[str] | None = None,
    filter_archs: list[str] | None = None,
    filter_optims: list[str] | None = None,
) -> list[tuple[str, dict[str, Any]]]:
    """Return list of (test_id, entry) for the full or filtered grid."""
    seed = grid.get("default_seed", 42)
    claim_ids = grid.get("claim_ids", ["C02", "C03", "C04", "C05"])
    engine_defaults = grid.get("engine_defaults") or {}
    archs = grid["archs"]
    optimizers = grid["optimizers"]
    states = grid["states"]
    stages = grid["stages"]

    if filter_states:
        states = [s for s in states if s in filter_states]
    if filter_stages:
        stages = {k: v for k, v in stages.items() if k in filter_stages}
    if filter_archs:
        archs = [a for a in archs if a["id"] in filter_archs]
    if filter_optims:
        optimizers = [o for o in optimizers if o["id"] in filter_optims]

    entries: list[tuple[str, dict[str, Any]]] = []
    for state in states:
        for stage, stage_cfg in stages.items():
            for arch in archs:
                for optim in optimizers:
                    test_id = _make_test_id(state, stage, arch["id"], optim["id"], seed)
                    entry = _make_entry(
                        test_id=test_id,
                        state=state,
                        stage=stage,
                        arch=arch,
                        optim=optim,
                        stage_cfg=stage_cfg,
                        claim_ids=claim_ids,
                        seed=seed,
                        engine_defaults=engine_defaults,
                    )
                    entries.append((test_id, entry))
    return entries


def enroll(
    grid_file: Path,
    *,
    dry_run: bool = False,
    filter_states: list[str] | None = None,
    filter_stages: list[str] | None = None,
    filter_archs: list[str] | None = None,
    filter_optims: list[str] | None = None,
) -> int:
    grid = _load_grid(grid_file)
    entries = generate_entries(
        grid,
        filter_states=filter_states,
        filter_stages=filter_stages,
        filter_archs=filter_archs,
        filter_optims=filter_optims,
    )

    if dry_run:
        # Print grouped summary
        from collections import defaultdict
        groups: dict[tuple[str, str], list[str]] = defaultdict(list)
        for tid, entry in entries:
            stage = entry["config"]["stage"]
            state = entry["config"]["state"]
            groups[(stage, state)].append(tid)

        total = 0
        for (stage, state), tids in sorted(groups.items()):
            print(f"  {stage} × {state.upper():>3}:  {len(tids):3d} tests")
            for t in tids:
                print(f"    {t}")
            total += len(tids)
        print(f"\nTotal: {total} tests (dry-run — state.json NOT modified)")
        return 0

    # Real enrollment: idempotent merge into state.json
    state_json = read_state()
    new_count = 0
    skip_count = 0
    for test_id, entry in entries:
        existing = get_test(state_json, "P1", test_id)
        if existing is not None:
            skip_count += 1
        else:
            set_test(state_json, "P1", test_id, entry)
            new_count += 1

    if new_count > 0:
        # Use mutate_state's write via a manual approach to preserve atomicity
        from _state import write_state
        write_state(state_json)
        print(f"[enroll] enrolled {new_count} new P1 tests into state.json")
    else:
        print(f"[enroll] all {skip_count} tests already enrolled — no changes")
    if skip_count > 0:
        print(f"[enroll] skipped {skip_count} already-enrolled tests (idempotent)")
    return 0


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(
        prog="enroll_p1",
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    p.add_argument(
        "--grid-file",
        type=Path,
        default=DEFAULT_GRID_FILE,
        help=f"Path to P1_grid.yaml (default: {DEFAULT_GRID_FILE})",
    )
    p.add_argument("--dry-run", action="store_true", help="List tests without modifying state.json.")
    p.add_argument("--state", nargs="*", metavar="STATE",
                   help="Filter by state code(s), e.g. AL AZ (default: all)")
    p.add_argument("--stage", nargs="*", metavar="STAGE",
                   help="Filter by stage(s): screen promote confirm (default: all)")
    p.add_argument("--arch", nargs="*", metavar="ARCH",
                   help="Filter by arch id(s): base cgc22 cgc21 mmoe4 dsk42 (default: all)")
    p.add_argument("--optim", nargs="*", metavar="OPTIM",
                   help="Filter by optimizer id(s) (default: all)")
    args = p.parse_args(argv)

    if not args.grid_file.exists():
        print(f"[enroll] grid file not found: {args.grid_file}", file=sys.stderr)
        return 2

    return enroll(
        args.grid_file,
        dry_run=args.dry_run,
        filter_states=args.state,
        filter_stages=args.stage,
        filter_archs=args.arch,
        filter_optims=args.optim,
    )


if __name__ == "__main__":
    sys.exit(main())
