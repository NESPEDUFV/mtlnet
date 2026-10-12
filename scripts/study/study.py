"""Single-entry CLI behind the /study Skill.

Subcommands:
  init           — write $STUDY_DIR/state.json (guards against overwrite)
  status         — summarize state.json
  next           — launch next planned test in current phase (delegates to launch_test)
  import         — archive a run (delegates to archive_result)
  validate       — run input integrity checks for a state+engine
  analyze        — verdict a test (delegates to analyze_test)
  claim          — look up tests tied to a claim_id
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

from _state import (
    PHASES,
    RESULTS_DIR,
    STATE_PATH,
    STUDIES_DIR,
    empty_state,
    iter_tests,
    mutate_state,
    read_state,
    summarize_phase,
    write_state,
)

HERE = Path(__file__).resolve().parent


def _run(script: str, *args: str) -> int:
    cmd = [sys.executable, str(HERE / script), *args]
    proc = subprocess.run(cmd)
    return proc.returncode


def cmd_init(args: argparse.Namespace) -> int:
    if STATE_PATH.exists() and not args.force:
        print(f"[init] {STATE_PATH} already exists. Use --force to overwrite.")
        return 1
    write_state(empty_state())
    print(f"[init] wrote {STATE_PATH}")
    return 0


def cmd_status(args: argparse.Namespace) -> int:
    try:
        state = read_state()
    except FileNotFoundError as exc:
        print(exc)
        return 1
    print(f"study_version: {state.get('study_version')}")
    print(f"current_phase: {state.get('current_phase')}")
    print(f"last_update:   {state.get('last_update')}")
    print()
    for phase in PHASES:
        s = summarize_phase(state, phase)
        status = s["status"] or "planned"
        flag = "→" if phase == state.get("current_phase") else " "
        line = f"{flag} {phase}  [{status:<10}] tests={s['total_tests']:<3}"
        if s["by_status"]:
            line += "  " + " ".join(f"{k}={v}" for k, v in sorted(s["by_status"].items()))
        print(line)

    issues = state.get("open_issues", [])
    open_count = sum(1 for i in issues if i.get("status") == "open")
    if open_count:
        print(f"\nopen issues: {open_count}")
        for issue in issues:
            if issue.get("status") == "open":
                print(f"  [{issue['issue_id']}] {issue['type']}: {issue['description'][:120]}")
    return 0


def cmd_next(args: argparse.Namespace) -> int:
    forward = ["--phase", args.phase] if args.phase else []
    if args.test_id:
        forward += ["--test-id", args.test_id]
    if args.dry_run:
        forward += ["--dry-run"]
    if args.no_sync:
        forward += ["--no-sync"]
    if args.state:
        forward += ["--state", args.state]
    if args.tier:
        forward += ["--tier", args.tier]
    if args.arch:
        forward += ["--arch", args.arch]
    if args.optim:
        forward += ["--optim", args.optim]
    if args.max_runtime_min is not None:
        forward += ["--max-runtime-min", str(args.max_runtime_min)]
    if args.worker_id:
        forward += ["--worker-id", args.worker_id]
    return _run("launch_test.py", *forward)


def cmd_import(args: argparse.Namespace) -> int:
    extra: list[str] = [
        "--run-dir", args.run_dir,
        "--phase", args.phase,
        "--test-id", args.test_id,
    ]
    if args.claims:
        extra += ["--claims", *args.claims]
    if args.overwrite:
        extra += ["--overwrite"]
    return _run("archive_result.py", *extra)


def cmd_validate(args: argparse.Namespace) -> int:
    forward: list[str] = ["--state", args.state, "--engine", args.engine]
    if args.cross:
        forward += ["--cross", *args.cross]
    return _run("validate_inputs.py", *forward)


def cmd_analyze(args: argparse.Namespace) -> int:
    return _run(
        "analyze_test.py",
        "--phase", args.phase,
        "--test-id", args.test_id,
        "--tolerance", str(args.tolerance),
    )


def cmd_claim(args: argparse.Namespace) -> int:
    try:
        state = read_state()
    except FileNotFoundError as exc:
        print(exc)
        return 1
    print(f"claim {args.claim_id}: tests referencing this claim")
    any_found = False
    for phase, tid, entry in iter_tests(state):
        if args.claim_id in (entry.get("claim_ids") or []):
            any_found = True
            verdict = entry.get("verdict", "-")
            observed = entry.get("observed", {})
            print(
                f"  [{phase}] {tid}  status={entry.get('status', '?'):<10} "
                f"verdict={verdict:<20} joint={observed.get('joint_f1')}"
            )
    if not any_found:
        print("  (none)")
    return 0


def cmd_advance(args: argparse.Namespace) -> int:
    with mutate_state() as state:
        current = state.get("current_phase")
        if not current:
            print("[advance] no current_phase set")
            return 1
        s = summarize_phase(state, current)
        pending = [k for k in s["by_status"] if k in {"planned", "running"}]
        if pending and not args.force:
            print(f"[advance] phase {current} still has {s['by_status']} — pass --force to override")
            return 1
        state["phases"][current]["status"] = "completed"
        state["phases"][current]["finished"] = state.get("last_update")
        try:
            next_phase = PHASES[PHASES.index(current) + 1]
        except IndexError:
            print(f"[advance] {current} is the last phase; study complete")
            state["current_phase"] = None
            return 0
        state["current_phase"] = next_phase
        state["phases"][next_phase]["status"] = "running"
        state["phases"][next_phase]["started"] = state.get("last_update")
        print(f"[advance] {current} → {next_phase}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="study", description="Study coordinator CLI.")
    sub = p.add_subparsers(dest="command", required=True)

    sp = sub.add_parser("init", help="Initialize state.json")
    sp.add_argument("--force", action="store_true")
    sp.set_defaults(func=cmd_init)

    sp = sub.add_parser("status", help="Summarize study state")
    sp.set_defaults(func=cmd_status)

    sp = sub.add_parser("next", help="Launch next planned test")
    sp.add_argument("--phase", default=None)
    sp.add_argument("--test-id", default=None)
    sp.add_argument("--dry-run", action="store_true")
    sp.add_argument(
        "--no-sync", action="store_true",
        help="Do not update state.json running/completed status (parallel-safe mode).",
    )
    sp.add_argument("--state", "-s", default=None, help="Filter by state code(s), e.g. AL,AZ.")
    sp.add_argument("--tier", "-t", default=None, help="Filter by tier(s): screen,promote,confirm,heavy.")
    sp.add_argument("--arch", "-a", default=None, help="Filter by arch id(s).")
    sp.add_argument("--optim", "-o", default=None, help="Filter by optimizer id(s).")
    sp.add_argument("--max-runtime-min", type=int, default=None, metavar="N",
                    help="Skip tests whose tier estimate exceeds N minutes.")
    sp.add_argument("--worker-id", default=None, help="Heartbeat worker identifier.")
    sp.set_defaults(func=cmd_next)

    sp = sub.add_parser("import", help="Archive a run directory into $STUDY_DIR/results/")
    sp.add_argument("--run-dir", required=True)
    sp.add_argument("--phase", required=True)
    sp.add_argument("--test-id", required=True)
    sp.add_argument("--claims", nargs="*", default=None)
    sp.add_argument("--overwrite", action="store_true")
    sp.set_defaults(func=cmd_import)

    sp = sub.add_parser("validate", help="Validate inputs for a state+engine")
    sp.add_argument("--state", required=True)
    sp.add_argument("--engine", required=True)
    sp.add_argument("--cross", nargs="*", default=None)
    sp.set_defaults(func=cmd_validate)

    sp = sub.add_parser("analyze", help="Verdict an archived test")
    sp.add_argument("--phase", required=True)
    sp.add_argument("--test-id", required=True)
    sp.add_argument("--tolerance", type=float, default=0.03)
    sp.set_defaults(func=cmd_analyze)

    sp = sub.add_parser("claim", help="Show tests evidencing a claim")
    sp.add_argument("claim_id")
    sp.set_defaults(func=cmd_claim)

    sp = sub.add_parser("advance", help="Move current_phase forward if gate passes")
    sp.add_argument("--force", action="store_true")
    sp.set_defaults(func=cmd_advance)

    return p


def main() -> int:
    args = build_parser().parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
