"""What a finished cell writes to disk.

One schema, written by the runner, containing the resolved configuration that produced it. The
reference wrote provenance by hand in a shell driver — which is how ten cells came to carry
`"precision": "fp32"` while autocast had run them in fp16. Here the provenance is not a claim about
the run; it is the object the run used.

Deliberately not compatible with the reference's sidecars (author decision): the old format spread
one cell's truth across a driver-written JSON, a scorer-written JSON and a metrics directory, and
carried fields nothing validated.
"""

from __future__ import annotations

import hashlib
import json
import os
import platform
import subprocess
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

import torch

SCHEMA_VERSION = 1


@dataclass
class CellResult:
    """One (family, state, seed) cell: what was asked for, what ran, and what came out."""

    schema_version: int
    cell_id: str
    family: str
    state: str
    seed: int
    engine: str

    config: dict[str, Any]           # the RESOLVED configuration
    config_fingerprint: str
    environment: dict[str, Any]

    aggregate: dict[str, Any]        # fold-mean, dispersion, and the lane it belongs to
    folds: list[dict[str, Any]]      # per-fold selection + the epoch series behind it

    #: What resume compares. Separate from the full fingerprint on purpose: telemetry changes must
    #: not invalidate a banked cell, because invalidating one triggers a second sealed read.
    science_fingerprint: str = ""
    warnings: list[str] = field(default_factory=list)
    #: Qual substrato produziu este número, por nível — ver `substrate/identity.py`. Antes de
    #: 2026-08-19 nada aqui registrava isso, e duas células sobre substratos diferentes eram
    #: indistinguíveis, o que fazia o resume servir número velho como novo. Fica entre os campos
    #: COM default: um campo defaultado antes de `folds` quebra a dataclass inteira.
    substrate: dict[str, Any] = field(default_factory=dict)

    def write(self, directory: Path) -> Path:
        directory.mkdir(parents=True, exist_ok=True)
        path = directory / "result.json"
        # Atomic: a fold fan-out has several processes writing under one cell, and a half-written
        # result that still parses is worse than one that is missing.
        staging = path.with_suffix(f".{os.getpid()}.tmp")
        staging.write_text(json.dumps(asdict(self), indent=1, sort_keys=False))
        os.replace(staging, path)
        return path

    @classmethod
    def read(cls, path: Path) -> "CellResult":
        payload = json.loads(Path(path).read_text())
        if payload.get("schema_version") != SCHEMA_VERSION:
            raise ValueError(
                f"{path}: schema version {payload.get('schema_version')} is not {SCHEMA_VERSION}"
            )
        return cls(**payload)


def environment() -> dict[str, Any]:
    """What the run actually executed on.

    Recorded rather than assumed, because compiled numbers are not bit-reproducible across inductor
    sessions and MPS, CUDA and CPU differ in reduction order. A result that does not say where it
    ran cannot be compared with one that does.
    """
    info: dict[str, Any] = {
        "torch": torch.__version__,
        "python": platform.python_version(),
        "platform": platform.platform(),
        "device": _device_name(),
        "git_commit": _git_commit(),
        "code_fingerprint": _code_fingerprint(),
    }
    return info


def _device_name() -> str:
    if torch.cuda.is_available():
        return f"cuda:{torch.cuda.get_device_name(0)}"
    if torch.backends.mps.is_available():
        return "mps"
    return "cpu"


def _code_fingerprint() -> str:
    """A digest of the package source, because `git_commit` is None wherever runs actually happen.

    The A40 holds an rsync'd copy of `src/`, not a checkout, so every remote result records
    `git_commit: null` — and this bit immediately: two arms of the probe-cost study were run either
    side of a change to the probe itself, under configs differing only by a flag, with nothing in
    the artifact able to say the code had moved. That is the same shape as the sidecar that claimed
    `"fp32"` while the run was fp16: a field that cannot contradict a false belief.

    A hash over the sources is version control this deployment actually has. It answers "was this
    the same code?" — not "which commit?", which `git_commit` still answers where it can.
    """
    root = Path(__file__).resolve().parents[1]
    digest = hashlib.sha256()
    for path in sorted(root.rglob("*.py")):
        digest.update(path.relative_to(root).as_posix().encode())
        digest.update(path.read_bytes())
    return digest.hexdigest()[:16]


def _git_commit() -> str | None:
    try:
        out = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True,
                             timeout=5, cwd=Path(__file__).resolve().parent)
        return out.stdout.strip() or None if out.returncode == 0 else None
    except Exception:
        return None


def build(resolved, fold_results, aggregate: dict, *, warnings: list[str] | None = None,
          substrate: dict[str, Any] | None = None) -> CellResult:
    """Assemble a `CellResult` from a finished run."""
    train = resolved.train
    return CellResult(
        schema_version=SCHEMA_VERSION,
        cell_id=resolved.cell_id,
        family=train.family.value,
        state=train.state,
        seed=train.seed,
        engine=train.engine,
        config=resolved.to_dict(),
        config_fingerprint=resolved.fingerprint(),
        # What resume compares. Separate from the full fingerprint on purpose: telemetry changes
        # must not invalidate a banked cell (and so must not trigger a second sealed read).
        science_fingerprint=resolved.science_fingerprint(),
        environment=environment(),
        aggregate=aggregate,
        substrate=substrate or {},
        folds=[{
            "fold": r.fold,
            "seed": r.seed,
            "wall_seconds": round(r.wall_seconds, 2),
            # Which held-out stream the epoch series came from. The joint family banks no aggregate,
            # so for it this is the ONLY place the seal is recorded.
            "eval_stream": r.eval_stream,
            "selection": r.selection,
            "ambiguous_rows": r.ambiguous_rows,
            "train_loss": r.train_loss,
            "val": {task: series.values for task, series in r.val.items()},
            # Computed by the runner under --diagnostics and, until 2026-08-17, dropped here — so a
            # profiling run banked no profile and the question it was launched to answer had to be
            # asked again. Empty dict when diagnostics were off.
            "diagnostics": r.diagnostics,
            "parameter_counts": r.parameter_counts,
            # Fold 0 only — the model is identical across folds, and measuring five times would
            # bank five copies of one number.
            **({"flops": r.flops} if r.flops else {}),
        } for r in fold_results],
        warnings=list(warnings or []),
    )


__all__ = ["CellResult", "build", "environment", "SCHEMA_VERSION"]
