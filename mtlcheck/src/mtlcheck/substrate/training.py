"""The substrate training loop, and the tensors it consumes.

Full-batch: one forward over the entire graph per epoch, no minibatching, no dataloader. There is no
validation set — this is a pretext task, and the selected checkpoint is the one with the **lowest
training loss**, which is what the frozen recipe does. Recorded plainly rather than fixed: it is the
definition of the artifact, and every banked substrate was chosen that way.

Adam, not AdamW, and `weight_decay=0.0`, so the two are the same here anyway — but the reference says
Adam and the difference would matter the moment someone sets a decay.

## R16 — the reference build is not reproducible, and this one is

Measured on the A40: the reference, run twice with the same seed on the same machine, produces loss
curves that **diverge at epoch 4-5** and end at 0.2236 against 0.2321. The cause is the three scatter
operations in each forward — the two attention pools and the reconstruction decoder — whose CUDA
atomics accumulate floats in nondeterministic order. Over 500 epochs of a non-convex objective that
grows into embeddings agreeing at cosine 0.99, not 1.0.

So a banked substrate is one **sample**, not a function of its seed, and no implementation can
reproduce it exactly — the reference included.

`torch.use_deterministic_algorithms(True)` closes it completely: two runs, `max|Δ| = 0.0`, never
diverging, for **12.5% more wall time**. It is ON by default here. It cannot recover the banked
artifacts (nothing can), so nothing is lost by choosing it, and what is gained is that a build made
today can be made again tomorrow. Pass `deterministic=False` to reproduce the reference's behaviour,
including its irreproducibility.
"""

from __future__ import annotations

import hashlib
import logging
import math
import os
import time
from dataclasses import dataclass, replace

import torch
from torch.nn.utils import clip_grad_norm_

from .. import seeding
from ..config import SubstrateConfig
from .model import Check2HGI

logger = logging.getLogger(__name__)


@dataclass
class SubstrateData:
    """Everything one full-batch step reads. A plain container, moved between devices explicitly."""

    x: torch.Tensor
    edge_index: torch.Tensor
    edge_weight: torch.Tensor
    checkin_to_poi: torch.Tensor
    poi_to_region: torch.Tensor
    region_adjacency: torch.Tensor
    region_area: torch.Tensor
    coarse_region_similarity: torch.Tensor
    poi_delaunay_edge_index: torch.Tensor
    poi_recon_target: torch.Tensor

    def to(self, device: torch.device) -> "SubstrateData":
        moved = {f: getattr(self, f).to(device) for f in self.__dataclass_fields__}
        return replace(self, **moved)

    @property
    def num_checkins(self) -> int:
        return int(self.x.shape[0])


@dataclass
class SubstrateRun:
    """What a build produced, and what it would take to explain the result without re-running it."""

    checkin: torch.Tensor
    place: torch.Tensor
    region: torch.Tensor
    state_dict: dict[str, torch.Tensor]
    best_epoch: int
    best_loss: float
    losses: list[float]
    seconds: float
    n_params: int
    hard_negatives: bool
    peak_memory_bytes: int | None
    deterministic: bool              # what was REQUESTED
    deterministic_achieved: bool     # whether the guarantee actually holds (see enable_determinism)
    seed: int | None                 # None means the initialisation was NOT seeded by this code
    init_fingerprint: str
    nondeterministic_ops: list[str]  # ops that fell back despite determinism being requested

    @property
    def epochs_to_within_one_percent(self) -> int:
        """When the loss first came within 1% of its best — the curve's shape in one number."""
        if not self.losses:
            return 0
        threshold = self.best_loss + abs(self.best_loss) * 0.01
        for i, value in enumerate(self.losses, start=1):
            if value <= threshold:
                return i
        return len(self.losses)


class NonDeterministicOps:
    """Collect the ops that fall back to a non-deterministic kernel under `warn_only=True`.

    `use_deterministic_algorithms(True, warn_only=True)` is the right setting — the alternative
    raises on ops with no deterministic implementation and would make the substrate unbuildable —
    but on its own it turns a guarantee into a warning nobody reads. Measured here: `_bincount_cuda`
    is the only one on this path, and it is harmless because it sums exact small integers in fp32,
    where addition is associative. That reasoning is only checkable if the list is recorded, so it
    is recorded.
    """

    def __init__(self) -> None:
        self.ops: set[str] = set()

    def __enter__(self) -> "NonDeterministicOps":
        import warnings

        self._catcher = warnings.catch_warnings(record=True)
        self._records = self._catcher.__enter__()
        warnings.simplefilter("always", UserWarning)
        return self

    def __exit__(self, *exc) -> None:
        import re

        for record in self._records:
            text = str(record.message)
            if "does not have a deterministic implementation" in text:
                match = re.match(r"\s*(\S+)\s+does not have", text)
                self.ops.add(match.group(1) if match else text[:60])
        self._catcher.__exit__(*exc)
        if self.ops:
            logger.info("non-deterministic fallbacks used: %s", ", ".join(sorted(self.ops)))


def enable_determinism() -> bool:
    """Make the scatter reductions deterministic. Returns whether the cuBLAS side is also pinned.

    `CUBLAS_WORKSPACE_CONFIG` is read when cuBLAS initialises, so setting it here is too late if a
    matmul already ran. The CLI sets it before importing torch; this returns False when it did not,
    rather than claiming a guarantee it cannot make.
    """
    torch.use_deterministic_algorithms(True, warn_only=True)
    torch.backends.cudnn.benchmark = False
    pinned = os.environ.get("CUBLAS_WORKSPACE_CONFIG") in (":4096:8", ":16:8")
    if not pinned:
        os.environ["CUBLAS_WORKSPACE_CONFIG"] = ":4096:8"
        logger.warning("CUBLAS_WORKSPACE_CONFIG was not set before torch initialised; "
                       "scatter reductions are deterministic but cuBLAS may not be")
    return pinned


def build(config: SubstrateConfig, data: SubstrateData, *, in_channels: int, num_places: int,
          num_regions: int, poi2vec_table: torch.Tensor, delaunay_edge_index: torch.Tensor,
          delaunay_edge_weight: torch.Tensor, recon_target_dim: int, device: torch.device,
          deterministic: bool = True, log_every: int = 25) -> tuple[Check2HGI, SubstrateRun]:
    """Seed, construct, train. **The entry point for building a substrate.**

    This exists because `config.repr_seed` was, until it did, a field nobody read. Weight
    initialisation happens in the constructor, so a caller who trains a model it built itself has
    already consumed the RNG before any seeding inside `train` could matter — and two builds
    recorded as "seed 42" then differ, which is exactly what happened here (0.20984 against 0.21627,
    both labelled seed 42, twice the reference's entire seed dispersion apart).

    A config field that silently does nothing is the defect class this rewrite exists to remove. So
    the seed is applied HERE, before construction, and the resulting initialisation is fingerprinted
    into the run so a manifest can never again claim a seed it did not use.
    """
    seeding.seed_everything(config.repr_seed)
    model = Check2HGI(in_channels, num_places, num_regions, poi2vec_table, delaunay_edge_index,
                      delaunay_edge_weight, recon_target_dim, config)
    run = train(model, data, config, device=device, deterministic=deterministic,
                log_every=log_every, seed=config.repr_seed)
    return model, run


def init_fingerprint(model: torch.nn.Module) -> str:
    """A short hash of the initial parameters — proof of which initialisation a run actually used."""
    digest = hashlib.sha256()
    for name, tensor in sorted(model.state_dict().items()):
        digest.update(name.encode())
        digest.update(tensor.detach().cpu().numpy().tobytes())
    return digest.hexdigest()[:16]


def train(model: Check2HGI, data: SubstrateData, config: SubstrateConfig, *,
          device: torch.device, log_every: int = 25,
          deterministic: bool = True, seed: int | None = None) -> SubstrateRun:
    """Run the pretext objective to convergence and return the best state plus its provenance.

    Prefer `build`, which owns the seeding. Called directly, this seeds the training loop but cannot
    seed the initialisation that already happened — so `seed` is recorded as None and the manifest
    says the initialisation was not seeded by this code, rather than implying it was.
    """
    achieved = enable_determinism() if deterministic else False
    fallbacks = NonDeterministicOps()
    fingerprint = init_fingerprint(model)
    if seed is not None:
        seeding.seed_everything(seed)
    model = model.to(device)
    data = data.to(device)
    optimizer = torch.optim.Adam(model.parameters(), lr=config.lr,
                                 weight_decay=config.weight_decay)

    if device.type == "cuda":
        torch.cuda.reset_peak_memory_stats(device)

    n_params = sum(p.numel() for p in model.parameters())
    logger.info("substrate build: %d params · %d epochs · %s",
                n_params, config.epochs, device)

    best_loss, best_epoch, best_state = math.inf, 0, None
    losses: list[float] = []
    started = time.perf_counter()

    fallbacks.__enter__()
    for epoch in range(1, config.epochs + 1):
        model.train()
        optimizer.zero_grad()
        loss = model.loss(model(data))
        loss.backward()
        clip_grad_norm_(model.parameters(), max_norm=config.max_norm)
        optimizer.step()

        value = float(loss.item())
        losses.append(value)
        if value < best_loss:
            best_loss, best_epoch = value, epoch
            best_state = {k: v.detach().clone() for k, v in model.state_dict().items()}
        if epoch % log_every == 0 or epoch == config.epochs:
            logger.info("epoch %d/%d · loss %.4f · best %.4f @%d",
                        epoch, config.epochs, value, best_loss, best_epoch)

    fallbacks.__exit__(None, None, None)
    seconds = time.perf_counter() - started
    assert best_state is not None, "no epoch ran"

    model.load_state_dict(best_state)
    model.eval()
    with torch.no_grad():
        model(data)
        checkin, place, region = model.embeddings()

    peak = torch.cuda.max_memory_allocated(device) if device.type == "cuda" else None
    logger.info("substrate built: best %.4f @%d · %.1f s (%.2f s/epoch)",
                best_loss, best_epoch, seconds, seconds / config.epochs)

    return SubstrateRun(
        checkin=checkin, place=place, region=region,
        state_dict={k: v.cpu() for k, v in best_state.items()},
        best_epoch=best_epoch, best_loss=best_loss, losses=losses, seconds=seconds,
        n_params=n_params, hard_negatives=model.hard_negatives, peak_memory_bytes=peak,
        deterministic=deterministic, deterministic_achieved=achieved, seed=seed,
        init_fingerprint=fingerprint, nondeterministic_ops=sorted(fallbacks.ops),
    )


__all__ = ["SubstrateData", "SubstrateRun", "build", "train", "init_fingerprint"]
