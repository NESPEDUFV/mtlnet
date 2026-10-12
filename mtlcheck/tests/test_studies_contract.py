"""The anti-drift contract for `studies/`, enforced rather than documented.

Why this test exists, concretely. In the reference repository a study kept its own copy of the
epoch/validation loop (`scripts/p1_region_head_ablation.py`, ~280 lines). That copy fell behind the
fixes in `src/` and shipped a CPU-scoring path for two months after the shared trainer had been
corrected — roughly 39% of a cell's wall-clock, undetected, because nothing forced the study to use
the library. A second study kept its matrix in 30+ shell drivers, one of which leaked an
`export MTL_DISABLE_AMP=1` between cells and silently ran 8 of 10 category cells at a precision
their own provenance files denied.

Both failures share one cause: a study was allowed to contain executable science. So it is not.

A study MAY contain: prose, wave manifests (data), status.json, read-only analysis, its board.
A study MAY NOT contain: a training loop, model/metric/scoring code, a copied driver, torch.
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

STUDIES = Path(__file__).resolve().parents[1] / "studies"

# Analysis scripts legitimately import the package to read results. They must not import a
# framework — that is the signature of a copied training loop.
BANNED_IMPORTS = {"torch", "torchmetrics", "sklearn", "lightning", "transformers"}

# Bulk belongs in runs/ or artifacts/, which are gitignored and resolvable from one root. The old
# repo scattered it across docs/results/, per-study logs/ and data/ sidecars, which is why its
# status.json ended up pointing at two different result roots.
MAX_FILE_BYTES = 1_000_000

TRAINING_MARKERS = (".backward(", "optimizer.step(", "loss.backward", "DataLoader(")


def _python_files() -> list[Path]:
    if not STUDIES.exists():
        return []
    return [p for p in STUDIES.rglob("*.py") if "archive" not in p.parts]


@pytest.mark.parametrize("path", _python_files(), ids=lambda p: str(p))
def test_study_python_imports_no_framework(path: Path) -> None:
    """Analysis code may import mtlcheck; it may not import a training framework."""
    tree = ast.parse(path.read_text(), filename=str(path))
    imported: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module and node.level == 0:
            imported.add(node.module.split(".")[0])

    offending = imported & BANNED_IMPORTS
    assert not offending, (
        f"{path.relative_to(STUDIES)} imports {sorted(offending)}. A study parameterizes a run "
        f"through a recipe, it does not implement one. If you need new behaviour, add it to "
        f"src/mtlcheck/ behind a config field and reference it by recipe."
    )


@pytest.mark.parametrize("path", _python_files(), ids=lambda p: str(p))
def test_study_python_has_no_training_loop(path: Path) -> None:
    source = path.read_text()
    found = [m for m in TRAINING_MARKERS if m in source]
    assert not found, (
        f"{path.relative_to(STUDIES)} contains training-loop markers {found}. This is exactly the "
        f"copied-driver pattern that drifted for two months in the reference repository."
    )


def test_studies_carry_no_bulk() -> None:
    """Boards and logs are kilobytes. Anything larger belongs in runs/ or artifacts/."""
    if not STUDIES.exists():
        pytest.skip("no studies yet")
    oversized = [
        (p.relative_to(STUDIES), p.stat().st_size)
        for p in STUDIES.rglob("*")
        if p.is_file() and p.stat().st_size > MAX_FILE_BYTES
    ]
    assert not oversized, (
        f"oversized files under studies/: {oversized}. Bulk output goes to runs/<study>/<cell-id>/ "
        f"(gitignored, resolvable from one root); studies/ keeps the committed record only."
    )


def test_studies_have_no_shell_drivers() -> None:
    """The experiment matrix is a manifest, and the executor is in the package."""
    if not STUDIES.exists():
        pytest.skip("no studies yet")
    shells = [p.relative_to(STUDIES) for p in STUDIES.rglob("*.sh") if "archive" not in p.parts]
    assert not shells, (
        f"shell drivers under studies/: {shells}. Waves are declarative TOML; `mtlcheck wave run` "
        f"executes them. A shell driver is where environment state leaks between cells."
    )
