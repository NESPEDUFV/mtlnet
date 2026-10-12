"""Smoke-test the study coordinator tooling against real artifacts.

Uses an existing fusion/alabama run as the "training output", then:
  1. init a fresh state.json (in a tmp location)
  2. enroll a fake test into P1 with expected ranges
  3. run validate_inputs on alabama+fusion
  4. run dry-run launch (should not mutate state)
  5. run archive (simulates worker post-training)
  6. run analyze
  7. verify final state.json shape

Exit 0 = all green. Print WARN/FAIL lines and exit non-zero otherwise.

Run from repo root: `.venv/bin/python scripts/study/_smoke_test.py`
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parent.parent


def run(cmd: list[str], **kw) -> subprocess.CompletedProcess:
    kw.setdefault("cwd", REPO_ROOT)
    kw.setdefault("capture_output", True)
    kw.setdefault("text", True)
    return subprocess.run(cmd, **kw)


def find_sample_run() -> Path:
    candidates = list((REPO_ROOT / "results" / "fusion" / "alabama").glob("mtlnet_*"))
    candidates = [p for p in candidates if (p / "summary" / "full_summary.json").exists()]
    if not candidates:
        raise SystemExit("smoke: no fusion/alabama run to test with")
    candidates.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    return candidates[0]


def main() -> int:
    results: list[tuple[str, bool, str]] = []

    def check(label: str, ok: bool, detail: str = "") -> None:
        results.append((label, ok, detail))
        marker = "PASS" if ok else "FAIL"
        print(f"  [{marker}] {label}{': ' + detail if detail else ''}")

    sample_run = find_sample_run()
    print(f"[smoke] sample run: {sample_run.relative_to(REPO_ROOT)}")

    with tempfile.TemporaryDirectory(prefix="study_smoke_") as tmpdir:
        tmp = Path(tmpdir)
        fake_studies = tmp / "docs" / "studies"
        fake_studies.mkdir(parents=True)
        fake_state = fake_studies / "state.json"
        fake_results = fake_studies / "results"

        # Use env-var redirection of state location? Simpler: monkeypatch via env.
        # Actually our scripts hardcode STATE_PATH to repo path. Back up and restore.
        real_state = REPO_ROOT / "docs" / "studies" / "state.json"
        real_results = REPO_ROOT / "docs" / "studies" / "results"
        backup_state = None
        backup_results = None
        try:
            if real_state.exists():
                backup_state = real_state.read_text()
            if real_results.exists():
                backup_results = tmp / "results_backup"
                shutil.copytree(real_results, backup_results)

            # 1. init fresh
            p = run([sys.executable, "scripts/study/study.py", "init", "--force"])
            check("init", p.returncode == 0, p.stdout.strip() or p.stderr.strip())

            # 2. enroll a fake test in P1
            state = json.loads(real_state.read_text())
            state["phases"]["P1"]["tests"]["P1_AL_smoke"] = {
                "test_id": "P1_AL_smoke",
                "phase": "P1",
                "claim_ids": ["C01", "C99"],
                "status": "planned",
                "config": {
                    "task": "mtl",
                    "state": "alabama",
                    "engine": "fusion",
                    "model_name": "mtlnet_dselectk",
                    "mtl_loss": "equal_weight",
                    "seed": 42,
                    "epochs": 50,
                    "folds": 5,
                    "embedding_dim": 128,
                },
                "expected": {
                    "joint_range": [0.30, 0.60],
                    "cat_f1_range": [0.70, 0.90],
                    "next_f1_range": [0.20, 0.35],
                },
            }
            real_state.write_text(json.dumps(state, indent=2))
            check("enroll test", True)

            # 3. validate (real data)
            p = run([sys.executable, "scripts/study/study.py", "validate",
                     "--state", "alabama", "--engine", "fusion"])
            check("validate fusion", p.returncode in (0, 1), p.stdout.splitlines()[-1] if p.stdout else "")

            # 4. dry-run next — should NOT mark test running
            p = run([sys.executable, "scripts/study/study.py", "next",
                     "--phase", "P1", "--test-id", "P1_AL_smoke", "--dry-run"])
            s = json.loads(real_state.read_text())
            test_status = s["phases"]["P1"]["tests"]["P1_AL_smoke"]["status"]
            check("dry-run preserves planned", test_status == "planned",
                  f"status={test_status}, stdout={p.stdout.strip()[:200]}")

            # 5. archive from sample run (simulate worker post-training)
            p = run([sys.executable, "scripts/study/study.py", "import",
                     "--run-dir", str(sample_run),
                     "--phase", "P1", "--test-id", "P1_AL_smoke",
                     "--claims", "C01", "C99"])
            ok = p.returncode == 0
            check("import archives summary", ok, p.stdout.strip() or p.stderr.strip())

            archived = REPO_ROOT / "docs" / "studies" / "results" / "P1" / "P1_AL_smoke"
            check("archive dir exists", archived.is_dir(), str(archived))
            check("full_summary.json copied", (archived / "full_summary.json").exists())
            check("metadata.json written", (archived / "metadata.json").exists())

            meta = json.loads((archived / "metadata.json").read_text())
            obs = meta.get("observed", {})
            check("observed.cat_f1 present", obs.get("cat_f1") is not None, f"cat_f1={obs.get('cat_f1')}")
            check("observed.next_f1 present", obs.get("next_f1") is not None, f"next_f1={obs.get('next_f1')}")
            check("joint_f1 computed", isinstance(obs.get("joint_f1"), float),
                  f"joint_f1={obs.get('joint_f1')}")
            check("claim_ids in metadata", meta.get("claim_ids") == ["C01", "C99"])

            s = json.loads(real_state.read_text())
            entry = s["phases"]["P1"]["tests"]["P1_AL_smoke"]
            check("state status = archived", entry["status"] == "archived", entry["status"])
            check("state observed linked", entry.get("observed", {}).get("joint_f1") is not None)

            # 6. analyze
            p = run([sys.executable, "scripts/study/study.py", "analyze",
                     "--phase", "P1", "--test-id", "P1_AL_smoke"])
            check("analyze runs", p.returncode == 0, p.stdout.strip())

            s = json.loads(real_state.read_text())
            entry = s["phases"]["P1"]["tests"]["P1_AL_smoke"]
            check("verdict assigned", "verdict" in entry, f"verdict={entry.get('verdict')}")
            check("verdict_detail assigned", "verdict_detail" in entry)

            # 7. claim lookup
            p = run([sys.executable, "scripts/study/study.py", "claim", "C01"])
            check("claim lookup finds test", "P1_AL_smoke" in p.stdout, p.stdout.strip()[:200])

            # 8. surprising verdict path — shove in a bad expected range
            state = json.loads(real_state.read_text())
            state["phases"]["P1"]["tests"]["P1_AL_smoke_bad"] = {
                "test_id": "P1_AL_smoke_bad",
                "phase": "P1",
                "claim_ids": ["C01"],
                "status": "archived",
                "observed": {"joint_f1": 0.55, "cat_f1": 0.82, "next_f1": 0.28},
                "expected": {
                    "joint_range": [0.90, 0.99],  # impossible
                    "cat_f1_range": [0.95, 0.99],
                    "next_f1_range": [0.95, 0.99],
                },
            }
            real_state.write_text(json.dumps(state, indent=2))
            p = run([sys.executable, "scripts/study/study.py", "analyze",
                     "--phase", "P1", "--test-id", "P1_AL_smoke_bad"])
            s = json.loads(real_state.read_text())
            entry = s["phases"]["P1"]["tests"]["P1_AL_smoke_bad"]
            check("surprising verdict detected", entry.get("verdict") == "surprising",
                  f"verdict={entry.get('verdict')}")
            check("surprising opens issue",
                  any(i["test_id"] == "P1_AL_smoke_bad" for i in s.get("open_issues", [])))

            # 9. status prints something
            p = run([sys.executable, "scripts/study/study.py", "status"])
            check("status runs", p.returncode == 0 and "current_phase" in p.stdout)

        finally:
            # Restore original state.json + results dir
            if backup_state is not None:
                real_state.write_text(backup_state)
            else:
                if real_state.exists():
                    real_state.unlink()
            if backup_results is not None:
                if real_results.exists():
                    shutil.rmtree(real_results)
                shutil.copytree(backup_results, real_results)

    failures = [r for r in results if not r[1]]
    print(f"\n[smoke] {len(results) - len(failures)}/{len(results)} passed")
    if failures:
        for label, _, detail in failures:
            print(f"  FAIL: {label}{' — ' + detail if detail else ''}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
