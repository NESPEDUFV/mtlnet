"""Retaining weights — the one artifact that turns a campaign into a script.

The audit of this project's history put a taxonomy behind what is otherwise a storage argument. Of
everything anyone has wanted to know after the fact, almost nothing depends on the exact minibatch;
almost everything is a pure function of the weights plus data:

| class | needs | examples |
|---|---|---|
| A | a bit-identical re-run | gradient cosine, ‖Δθ‖, forgetting counts |
| **B** | **a checkpoint at that epoch** | CKA, calibration, FLOPs, re-scoring, the T6 accumulation curve |
| C | the saved logits only | ECE@k, temperature scaling, Acc@k at any k |

**Class B is almost everything, so retention — not the field list — is the highest-leverage
decision.** The precedent is Pythia (Biderman et al., ICML 2023), which publishes 154 checkpoints per
model precisely so training-dynamics questions can be answered without re-running.

The bill this pays, from the project's own record: probes ran `--no-checkpoints`, so champion G's
independent load-and-rescore check was skipped for want of a `.pt`, and T2P.0 was re-trained at two
states purely to recover weights it had already computed and discarded.

## Two policies, and the delete that makes the second affordable

`selected` keeps one file per fold — the checkpoint the selector chose, which is the model any
deployment claim is about. It belongs to CONFIRMATORY cells, not to every run: a screening cell
cannot consume a checkpoint (§5 re-fits winners under sealed confirmation, and under sealing a
screening cell never evaluates the outer fold), so retaining one is write-only output, and at
hundreds of cells a week it is tens of GB of it.

`every` keeps one file per epoch, and is what §8a's `a1` requires: `a1` is a **max over the eligible
epochs** of the outer score, and a max cannot be sampled. Measured on 753 real 50-epoch curves, an
8-point log grid discards a maximum averaging 1.16 pp — two to three times the entire quantity §8a
exists to measure.

**And `every` is TRANSIENT.** The protocol prices §8a as "≈ 6% of bridge compute plus *transient*
checkpoint storage" and scopes its scorer per state — "refuses to run until all seeds × folds of a
state are complete". So the shape is a pipeline, one state at a time:

    train state → quarantined scorer → append a1/b1/b2 to the sink → DELETE → next state

Peak ~42 GB for days on a 2.2 TB box; permanent output, a few KB of scalars. Retaining every epoch
of every state and never deleting is not §8a being expensive — it is half of §8a, and the half that
costs 125 GB.

Before deleting, the scorer must run the free end-to-end check: **b1 at the selected epoch has to
equal the banked one-shot outer evaluation exactly.** That certifies the whole scoring pass against
a number already in `result.json`, and only then are the weights really scaffolding.

⚠ **The consumer does not exist yet.** Nothing in `src/mtlcheck/` loads a retained checkpoint —
there is no §8a scorer and no T6 script. This module was built before the thing that reads it, which
inverts the plan's own build order. Do not retain at scale until the scorer has run on one state:
the unloadable-checkpoint defect (keys prefixed by `torch.compile`) is exactly what happens when the
consumer arrives after the compute is spent.

`log_spaced` is gone. Its only consumer was T6, whose weights are a subset of what §8a already holds
transiently — so it was a third policy, and a standing "latent per-epoch outer evaluation" surface,
buying nothing.
"""

from __future__ import annotations

import json
import logging
import os
from pathlib import Path
from uuid import uuid4
from typing import Any

import torch

logger = logging.getLogger(__name__)

def snapshot(model: torch.nn.Module) -> dict[str, torch.Tensor]:
    """A CPU copy of the weights, detached from the graph and from the live model.

    `.clone()` rather than a reference: the training step mutates these tensors in place, so a
    reference is a checkpoint of whatever the model happens to hold when someone finally reads it.
    """
    base = getattr(model, "_orig_mod", model)
    return {k: v.detach().cpu().clone() for k, v in base.state_dict().items()}


class FoldCheckpoints:
    """Collects one fold's retained weights and writes them under a run directory.

    Writes as it goes rather than at the end: a cell that dies at fold 4 keeps folds 0-3, and the
    peak memory is one snapshot rather than the whole trajectory.
    """

    def __init__(self, directory: Path | None, fold: int, policy: str, epochs: int) -> None:
        self.directory = Path(directory) / "checkpoints" if directory is not None else None
        self.fold = fold
        self.policy = policy
        self.wanted = tuple(range(epochs + 1)) if policy == "every" else ()
        self.written: dict[str, Any] = {}
        if self.directory is not None and policy != "none":
            self.directory.mkdir(parents=True, exist_ok=True)

    @property
    def active(self) -> bool:
        return self.directory is not None and self.policy != "none"

    def maybe_trajectory(self, model: torch.nn.Module, epoch: int) -> None:
        """Retain this epoch if the policy asks for it. `epoch` is 1-based; 0 is initialisation."""
        if not self.active or epoch not in self.wanted:
            return
        self._write(snapshot(model), f"fold{self.fold}_epoch{epoch}.pt", f"epoch{epoch}")

    def selected(self, state: dict[str, torch.Tensor], epoch: int, selector: float | None) -> None:
        """Retain THE checkpoint the selector chose — the model a deployment claim is about."""
        if not self.active:
            return
        self._write(state, f"fold{self.fold}_selected.pt", "selected")
        self.written["selected_epoch"] = int(epoch)
        if selector is not None:
            self.written["selected_value"] = float(selector)

    def _write(self, state: dict[str, torch.Tensor], name: str, key: str) -> None:
        path = self.directory / name
        # Atomic, and uniquely named per process. `id(state)` was neither: it is a memory address,
        # reused after garbage collection, so a crash left multi-MB orphans that no sweep could
        # recognise. The sibling staging sites in result.py and dataset.py already use the pid.
        staging = path.with_name(f"{name}.{os.getpid()}.{uuid4().hex[:8]}.tmp")
        try:
            torch.save(state, staging)
            os.replace(staging, path)
        finally:
            staging.unlink(missing_ok=True)
        self.written[key] = name

    def manifest(self) -> dict[str, Any]:
        # The fold id travels IN the entry. Without it a fan-out's merged manifest is a list of
        # anonymous rows whose files are named by a fold the index does not mention.
        return {"fold": self.fold, **self.written} if self.written else {}


def write_manifest(directory: Path, folds: list[dict[str, Any]], *,
                   policy: str, extra: dict[str, Any] | None = None) -> Path | None:
    """One index for a cell's retained weights, so a reader never globs and guesses."""
    if policy == "none" or not any(folds):
        return None
    path = Path(directory) / "checkpoints" / "manifest.json"
    path.parent.mkdir(parents=True, exist_ok=True)

    # MERGE, do not overwrite. `--only-folds` is a supported mode and the run directory is shared,
    # so a plain write left five checkpoints on disk and three in the index. Keyed by fold id.
    merged: dict[int, dict] = {}
    if path.exists():
        try:
            for entry in json.loads(path.read_text()).get("folds", []):
                if isinstance(entry, dict) and "fold" in entry:
                    merged[int(entry["fold"])] = entry
        except (json.JSONDecodeError, ValueError):
            logger.warning("unreadable checkpoint manifest at %s; rewriting", path)
    for entry in folds:
        if entry:
            merged[int(entry.get("fold", -1))] = entry

    payload = {"policy": policy, "folds": [merged[k] for k in sorted(merged)], **(extra or {})}
    staging = path.with_name(f"manifest.{os.getpid()}.tmp")
    try:
        staging.write_text(json.dumps(payload, indent=1))
        os.replace(staging, path)
    finally:
        staging.unlink(missing_ok=True)
    logger.info("checkpoints: %s policy, %d folds retained under %s", policy, len(folds), path.parent)
    return path


__all__ = ["FoldCheckpoints", "snapshot", "write_manifest"]
