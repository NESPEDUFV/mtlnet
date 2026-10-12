"""What a run reports about itself beyond its final number.

A cell's headline metric says whether it worked. These say *how* — and they are what you read when
something drifts, when a state behaves unlike its siblings, or when you need to know whether two
implementations agree for the right reasons rather than by cancellation.

Four families, all cheap enough to leave on:

* **Wall, split by phase.** Train and validation timed separately per epoch. A regression that moves
  only validation is a scoring problem; one that moves only training is not.
* **Convergence shape.** Not just which epoch was best, but how long it took to get near it — the
  epoch that first reaches 95% and 99% of the run's best. Two runs can share a best epoch and reach
  it very differently.
* **Gradient geometry (joint only).** The cosine between the two tasks' gradients over the SHARED
  trunk, with each task's norm. This is the quantity that decides whether multi-task training is a
  conflict to be managed or two tasks that happen to share a body: at cosine ~0 the gradients are
  orthogonal, and gradient-surgery methods have nothing to project. The reference measures it once
  per epoch on the first batch, and reports +0.001 with sd ~0.012 — which is why every surgery
  method it tried came out null.
* **Peak memory**, because the reference's large states are memory-bound and the number is free.

Measured on the first batch of each epoch, matching the reference so the values are comparable.

⚠ **A diagnostics run is not bit-comparable to one without.** The gradient geometry needs
`retain_graph`, which inductor's donated buffers forbid, so enabling diagnostics under `--compile`
also disables that optimisation — a different compile configuration, and compiled numbers are not
bit-reproducible across configurations anyway. The reference hits the same wall and resolves it the
same way: its loss-weight probe RE-RUNS its baseline arm with diagnostics rather than comparing
against the wave's numbers. Do the same.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field

import torch


@dataclass
class FoldDiagnostics:
    """Per-epoch diagnostics for one fold."""

    train_seconds: list[float] = field(default_factory=list)
    val_seconds: list[float] = field(default_factory=list)
    grad_cosine: list[float] = field(default_factory=list)
    grad_norm_cat: list[float] = field(default_factory=list)
    grad_norm_reg: list[float] = field(default_factory=list)
    #: Per trunk group, per epoch: {"cross_ab": {"cosine": .., "norm_cat": .., "norm_reg": ..}, ...}
    grad_groups: list[dict] = field(default_factory=list)

    # --- health scalars. All accumulated ON DEVICE and read once per epoch: a naive `.item()` per
    # tensor per step is ~2M host syncs over a fold and is visible on the clock.
    #: Pre-clip gradient norm, the value `clip_grad_norm_` already returns and used to discard.
    grad_norm_mean: list[float] = field(default_factory=list)
    grad_norm_max: list[float] = field(default_factory=list)
    #: Batches whose gradient exceeded max_grad_norm and was scaled down.
    clipped_fraction: list[float] = field(default_factory=list)
    #: Non-finite gradient events. The fp16 collapse forensics were reconstructed from exactly this
    #: in fresh instrumented runs; banked, that diagnosis would have been a query.
    nonfinite_batches: int = 0
    #: Per epoch, because the whole justification for these fields is that the CA divergence was
    #: diagnosed from a SERIES. Collapsed to run means, a fold that died at epoch 30 and its exact
    #: reverse produce a byte-identical block — 190 non-finite batches over 50 epochs is
    #: indistinguishable from 190 in two.
    nonfinite_per_epoch: list[int] = field(default_factory=list)
    #: Realised learning rate per optimizer group per epoch. Three FL cells were burned discovering
    #: per-head LR was inert under OneCycle — this records what the schedule DID, not what was asked.
    learning_rates: list[list[float]] = field(default_factory=list)
    #: Per-task training loss (joint only); only the scalarised sum was recorded before.
    train_loss_cat: list[float] = field(default_factory=list)
    train_loss_reg: list[float] = field(default_factory=list)
    #: torch.compile counters. A "compiled" arm once ran eager in silence; recording the INTENT is
    #: not the same as recording whether compilation held.
    compile_counters: dict = field(default_factory=dict)
    peak_memory_bytes: int = 0

    #: How the cell actually executed. Set by the runner, recorded in the artifact, because the
    #: profiling wave was captioned "eager" while six of its nine cells ran compiled and nothing
    #: written down could have contradicted that.
    execution: dict = field(default_factory=dict)

    def summary(self, metric_series: list[float] | None = None) -> dict:
        out: dict = {
            **({"execution": self.execution} if self.execution else {}),
            "train_seconds_total": round(sum(self.train_seconds), 2),
            "val_seconds_total": round(sum(self.val_seconds), 2),
            "train_seconds_per_epoch": round(_mean(self.train_seconds), 3),
            "val_seconds_per_epoch": round(_mean(self.val_seconds), 3),
            "val_share_of_wall": round(
                sum(self.val_seconds) / max(sum(self.train_seconds) + sum(self.val_seconds), 1e-9), 4),
        }
        if self.peak_memory_bytes:
            out["peak_memory_gb"] = round(self.peak_memory_bytes / 2**30, 3)
        if self.grad_cosine:
            finite = [c for c in self.grad_cosine if c == c]      # drop NaN
            out |= {
                "grad_cosine_mean": round(_mean(finite), 6),
                "grad_cosine_std": round(_std(finite), 6),
                "grad_cosine_negative_fraction": round(
                    sum(1 for c in finite if c < 0) / max(len(finite), 1), 4),
                "grad_norm_cat_mean": round(_mean(self.grad_norm_cat), 6),
                "grad_norm_reg_mean": round(_mean(self.grad_norm_reg), 6),
            }
        if self.grad_groups:
            names = sorted({k for g in self.grad_groups for k in g})
            grouped: dict[str, dict] = {}
            for name in names:
                rows = [g[name] for g in self.grad_groups if name in g]
                cosines = [r["cosine"] for r in rows
                           if r.get("cosine") is not None and r["cosine"] == r["cosine"]]
                # Dispersion and the parameter count, not just a mean. The point of T2 is comparing
                # groups, and their null floors differ by ~23x (d = 1,024 to 526,336) — two rounded
                # means read as a 200x difference on quantities whose per-batch sd is ~0.015.
                grouped[name] = {
                    "cosine_mean": round(_mean(cosines), 6) if cosines else None,
                    "cosine_std": round(_std(cosines), 6) if len(cosines) > 1 else None,
                    "negative_fraction": (round(sum(1 for c in cosines if c < 0) / len(cosines), 4)
                                          if cosines else None),
                    "n_epochs": len(cosines),
                    "n_params": rows[0].get("n_params") if rows else None,
                    "norm_cat_mean": round(_mean([r["norm_cat"] for r in rows]), 6),
                    "norm_reg_mean": round(_mean([r["norm_reg"] for r in rows]), 6),
                }
            out["grad_by_group"] = grouped
        if self.grad_norm_mean:
            out |= {
                "grad_norm_mean": round(_mean(self.grad_norm_mean), 6),
                "grad_norm_max": round(max(self.grad_norm_max), 6),
                "clipped_fraction_mean": round(_mean(self.clipped_fraction), 4),
                "nonfinite_batches": int(self.nonfinite_batches),
                # The series, ~200 floats. Means are permutation-invariant and a sum has no epoch
                # index, so without these the artifact cannot answer "when did it break".
                "grad_norm_per_epoch": [round(v, 6) for v in self.grad_norm_mean],
                "grad_norm_max_per_epoch": [round(v, 6) for v in self.grad_norm_max],
                "clipped_fraction_per_epoch": [round(v, 4) for v in self.clipped_fraction],
                "nonfinite_per_epoch": list(self.nonfinite_per_epoch),
            }
        if self.learning_rates:
            # AT EPOCH END, and named so. Read after the last scheduler.step(), which under a
            # per-batch OneCycle has already written the rate for the step that FOLLOWS: the value
            # labelled "first_epoch" was epoch 2's opening rate, 22x the rate epoch 1 actually
            # applied. R1 (per-head LR inert) is still served — the three groups are sampled at one
            # instant — but the label now says what the number is.
            out["lr_per_group_at_epoch_end"] = {
                "first": [round(v, 8) for v in self.learning_rates[0]],
                "max_observed": [round(max(e[i] for e in self.learning_rates), 8)
                                 for i in range(len(self.learning_rates[0]))],
                "last": [round(v, 8) for v in self.learning_rates[-1]],
                "note": "sampled after the epoch's final scheduler.step(); not the applied peak",
            }
        if self.train_loss_cat:
            out |= {"train_loss_cat": [round(v, 6) for v in self.train_loss_cat],
                    "train_loss_reg": [round(v, 6) for v in self.train_loss_reg]}
        if self.compile_counters:
            out["compile_counters"] = self.compile_counters
        if metric_series:
            out |= convergence(metric_series)
        return out


def convergence(series: list[float]) -> dict:
    """How quickly the run approached its own best.

    `epochs_to_95` / `epochs_to_99` are the first epochs reaching that fraction of the run's best
    value. Two runs with the same best epoch can differ sharply here, and a rewrite that trains a
    subtly different model usually shows up in the approach before it shows up in the peak.
    """
    if not series:
        return {}
    best = max(series)
    if best <= 0:
        return {"best_epoch": series.index(best) + 1, "best_value": best}
    out = {"best_epoch": series.index(best) + 1, "best_value": best}
    for fraction, name in ((0.95, "epochs_to_95pct"), (0.99, "epochs_to_99pct")):
        target = best * fraction
        reached = next((i + 1 for i, v in enumerate(series) if v >= target), None)
        out[name] = reached
    # Late-epoch stability: how much the last five epochs vary relative to the best.
    tail = series[-5:]
    out["tail_spread_pct_of_best"] = round((max(tail) - min(tail)) / best * 100, 3) if len(tail) > 1 else 0.0
    return out


def enable_retain_graph() -> None:
    """Turn off inductor's donated buffers so `retain_graph=True` is legal under `--compile`.

    Donated buffers let the compiled backward reuse activation memory, which is incompatible with
    taking a second gradient through the same graph. Called once, only when diagnostics are on.
    """
    try:
        import torch._functorch.config as functorch_config
        functorch_config.donated_buffer = False
    except Exception:                                          # pragma: no cover
        pass


def gradient_geometry(cat_loss: torch.Tensor, reg_loss: torch.Tensor,
                      shared: list[torch.nn.Parameter],
                      groups: dict[str, list] | None = None):
    """`(cosine, cat_norm, reg_norm)` of the two tasks' gradients over the SHARED trunk.

    Both gradients are taken with respect to the same parameters, without accumulating into `.grad`,
    so the training step is unaffected. `allow_unused` covers trunk tensors a task does not reach —
    they contribute zeros, which is what the reference does and what keeps the two vectors the same
    length.

    Costs two extra backward passes over the trunk on one batch per epoch.
    """
    if not shared:
        return (float("nan"), 0.0, 0.0, {}) if groups is not None else (float("nan"), 0.0, 0.0)

    cat_grads = torch.autograd.grad(cat_loss, shared, retain_graph=True, allow_unused=True)
    reg_grads = torch.autograd.grad(reg_loss, shared, retain_graph=True, allow_unused=True)
    # Computed from the SAME two gradient lists: the decomposition is free.
    per_group = group_geometry(cat_grads, reg_grads, shared, groups) if groups is not None else {}

    cat_flat = _flatten(cat_grads, shared)
    reg_flat = _flatten(reg_grads, shared)
    cat_norm = torch.norm(cat_flat)
    reg_norm = torch.norm(reg_flat)

    denominator = cat_norm * reg_norm
    cosine = (float(torch.dot(cat_flat, reg_flat) / denominator) if denominator > 0
              else float("nan"))
    scalars = (cosine, float(cat_norm), float(reg_norm))
    return (*scalars, per_group) if groups is not None else scalars


def gradient_geometry_sidecar(model, batch, cat_criterion, reg_criterion, autocast,
                              shared: list[torch.nn.Parameter], device,
                              groups: dict[str, list] | None = None):
    """The same quantity, on the probe's OWN eager graph — so training can stay compiled.

    Two things make this correct rather than merely cheaper.

    **One forward, not two.** Both gradients come from a single forward, so they share every dropout
    mask — the joint model carries dropout in the encoders (0.1), the trunk attention and FFNs (0.15)
    and the private tower (0.3). Measuring each task under its OWN forward would give them
    independent masks, the uncorrelated noise would not cancel, and the cosine would be
    systematically attenuated toward zero. A probe biased toward "orthogonal" cannot support a claim
    whose content is orthogonality.

    **Forked RNG.** The extra forward would otherwise consume the training stream's dropout draws and
    shift every subsequent mask, so probe-on would stop being byte-identical to probe-off. Forking
    keeps the training trajectory exactly what it would have been.

    Run on `_orig_mod` when the model is compiled: same parameters (compile wraps, it does not copy),
    but the graph is eager, so `retain_graph` is legal and the compiled backward is never involved.
    The probe's masks are a fresh draw rather than the training step's actual masks — same
    distribution, different realisation, so the per-epoch value samples the same estimand rather than
    being the literal step gradient.
    """
    base = getattr(model, "_orig_mod", model)
    (x_cat, y_cat, _), (x_reg, y_reg, _) = batch
    # The generator family must match the one dropout draws from. `fork_rng` defaults to
    # device_type="cuda", so on MPS only the CPU generator was saved while nn.Dropout used the MPS
    # one — measured end to end, probe-on and probe-off diverged from epoch 1 and selected DIFFERENT
    # checkpoints. The probe silently changed the run it was measuring.
    fork = ({"devices": [device.index or 0], "device_type": device.type}
            if device.type in ("cuda", "mps") else {"devices": []})
    was_training = base.training
    with torch.random.fork_rng(**fork):
        base.train(was_training)
        with autocast():
            cat_logits, reg_logits = base(x_cat, x_reg)
            cat_loss = cat_criterion(cat_logits, y_cat)
            reg_loss = reg_criterion(reg_logits, y_reg)
        return gradient_geometry(cat_loss, reg_loss, shared, groups)


def group_geometry(cat_grads, reg_grads, parameters: list[torch.nn.Parameter],
                   groups: dict[str, list]) -> dict[str, dict[str, float]]:
    """Per-group cosine and norms, from gradients ALREADY taken — no extra backward.

    A single scalar cosine over the whole trunk can average a conflicted block against an orthogonal
    one and report the mean as if it described both. *Gradient Vaccine* (Wang et al., ICLR 2021)
    shows per-layer distributions differing materially from the global figure, which is precisely
    the case a null-surgery result needs to rule out.

    Here it also answers a structural question the scalar cannot: `cross_ab`/`ffn_a` update the
    category side of the trunk and `cross_ba`/`ffn_b` the region side, so their separate norms show
    whether the shared trunk is really shared or is two private half-trunks sharing an address.
    """
    index = {id(p): i for i, p in enumerate(parameters)}
    out: dict[str, dict[str, float]] = {}
    for name, params in groups.items():
        positions = [index[id(p)] for p in params if id(p) in index]
        if not positions:
            continue
        left = _flatten([cat_grads[i] for i in positions], [parameters[i] for i in positions])
        right = _flatten([reg_grads[i] for i in positions], [parameters[i] for i in positions])
        cat_norm, reg_norm = torch.norm(left), torch.norm(right)

        # A group whose two supports are DISJOINT has a cosine of exactly 0 by construction, not by
        # measurement: `final_ln` merges cat_final_ln and reg_final_ln, and neither loss reaches the
        # other's parameters, so `_flatten` zero-fills and the dot product is 0 every batch of every
        # fold. Reported as a number it would be the most orthogonal group in every run — at the
        # group whose name most invites "even the shared output norms are orthogonal". None, not 0.
        overlap = ((left != 0) & (right != 0)).any()
        denominator = cat_norm * reg_norm
        out[name] = {
            "cosine": (float(torch.dot(left, right) / denominator)
                       if bool(overlap) and denominator > 0 else None),
            "norm_cat": float(cat_norm),
            "norm_reg": float(reg_norm),
            "n_params": int(left.numel()),
        }
    return out


def _flatten(grads, parameters) -> torch.Tensor:
    parts = [
        (grad if grad is not None else torch.zeros_like(param)).reshape(-1)
        for grad, param in zip(grads, parameters)
    ]
    return torch.cat(parts) if parts else torch.empty(0)


class Phase:
    """Time one phase of an epoch, on the device's clock rather than the host's.

    CUDA launches are asynchronous, so a bare `perf_counter` around a training step measures how
    long it took to ENQUEUE the work, not to do it. The work then lands wherever the next
    synchronisation happens — typically an `.item()` inside the next phase — so the phases do not
    just have wrong values, they have each other's. Measured on the A40 before this fix: a train
    phase reporting 1.06 s against ~21.7 s of real work, which made validation look like 55% of the
    epoch when it is nearer 6%.

    That is worse than no timing at all: every one of these numbers exists to answer "what should I
    optimise?", and they pointed at the wrong phase.

    Synchronising costs a stall per phase per epoch. Diagnostics are opt-in and already buy accuracy
    with speed, so this is the right trade here — but it does mean a run with `--diagnostics` is
    slightly slower than one without, and its wall-clock should not be compared to a bare run's.
    """

    def __init__(self, sink: list[float], device: torch.device | None = None) -> None:
        self.sink = sink
        self._sync = device is not None and device.type == "cuda"

    def _barrier(self) -> None:
        if self._sync:
            torch.cuda.synchronize()

    def __enter__(self) -> "Phase":
        self._barrier()
        self._start = time.perf_counter()
        return self

    def __exit__(self, *_exc) -> None:
        self._barrier()
        self.sink.append(time.perf_counter() - self._start)


class GradHealth:
    """Accumulates the gradient-norm series on device, reading the host once per epoch.

    `clip_grad_norm_` already computes the pre-clip norm and returns it; the loop threw it away. It
    is the cheapest forensic signal there is — the fp16 divergence at CA epoch 30 was diagnosed from
    this series and a non-finite counter, in fresh instrumented runs, after the fact.
    """

    def __init__(self, device: torch.device, max_norm: float) -> None:
        self.max_norm = max_norm
        self._total = torch.zeros((), device=device)
        self._peak = torch.zeros((), device=device)
        self._clipped = torch.zeros((), device=device)
        self._nonfinite = torch.zeros((), device=device)
        self._finite = torch.zeros((), device=device)
        self._batches = 0

    def observe(self, norm: torch.Tensor) -> None:
        """One batch's pre-clip norm. No `.item()` — everything stays on the accelerator.

        A non-finite batch is an EVENT, not a very large number, and it is excluded from the mean
        and the max rather than booked as zero. Booking it as zero made all three scalars move the
        wrong way during the divergence they exist to diagnose: with 90% of an epoch non-finite at a
        constant true norm of 3.0, the series read `[3.0, 0.3, 0.0]` — unchanged gradient behaviour
        reported as a tenfold calming.

        It also counts as CLIPPED, because it is: `clip_grad_norm_` with an infinite total scales
        the gradient by `1/(inf + eps) = 0`, i.e. maximally, and the step is still taken (there is
        no GradScaler and no skip-step anywhere in this trainer).
        """
        finite = torch.isfinite(norm)
        safe = torch.where(finite, norm, torch.zeros_like(norm))
        self._total += safe
        torch.maximum(self._peak, safe, out=self._peak)
        self._clipped += ((safe > self.max_norm) | ~finite).to(safe.dtype)
        self._nonfinite += (~finite).to(safe.dtype)
        self._finite += finite.to(safe.dtype)
        self._batches += 1

    def flush(self, sink: "FoldDiagnostics", extra: list[torch.Tensor] = ()) -> list[float]:
        """One host sync per epoch. `extra` rides along so callers need not add their own."""
        if not self._batches:
            return [float(t.detach().cpu()) for t in extra]
        stacked = torch.stack([self._total, self._peak, self._clipped, self._nonfinite,
                               self._finite, *[t.detach().reshape(()) for t in extra]]).cpu()
        total, peak, clipped, nonfinite, finite = (float(v) for v in stacked[:5])
        # Divided by the FINITE count: a mean over batches whose value was discarded is not a mean.
        sink.grad_norm_mean.append(total / finite if finite else float("nan"))
        sink.grad_norm_max.append(peak)
        sink.clipped_fraction.append(clipped / self._batches)
        sink.nonfinite_per_epoch.append(int(nonfinite))
        sink.nonfinite_batches += int(nonfinite)
        self._total.zero_(); self._peak.zero_(); self._clipped.zero_()
        self._nonfinite.zero_(); self._finite.zero_()
        self._batches = 0
        return [float(v) for v in stacked[5:]]


def compile_snapshot() -> dict:
    """The dynamo counters as they stand, for differencing at fold end.

    Process-global and never cleared — `torch._dynamo.reset()` does not touch them — and a wave runs
    every cell in one process. Absolute values therefore belong to whatever ran before: measured,
    three cells in one process read graph_breaks 0 -> 3 -> 8, and an EAGER cell banked a count of 3
    inherited from the compiled cell before it. This is the same high-water-mark defect that
    `reset_peak_memory` exists to fix, one field over.
    """
    try:
        from torch._dynamo.utils import counters
        return {"graph_breaks": int(sum(counters["graph_break"].values())),
                "unique_graph_breaks": len(counters["graph_break"]),
                "frames_total": int(counters["frames"].get("total", 0)),
                "frames_ok": int(counters["frames"].get("ok", 0))}
    except Exception:                                          # pragma: no cover
        return {}


def compile_counters(before: dict) -> dict:
    """This fold's compilation activity: the delta against `before`.

    `recompiles` is gone. torch 2.11 has no such counter bucket and `counters` is a defaultdict, so
    reading it returned 0 forever AND silently inserted the dead key — a field that could not
    distinguish a compiled run from an eager one, which is precisely the ambiguity it was added to
    remove. `frames_total`/`frames_ok` are real and do distinguish them.
    """
    after = compile_snapshot()
    if not after:
        return {}
    return {k: after.get(k, 0) - before.get(k, 0) for k in after}


def reset_peak_memory(device: torch.device) -> None:
    """Zero the peak counter so a fold measures ITS OWN peak.

    `max_memory_allocated` is a process-lifetime high-water mark. A wave runs every cell in one
    process, so without this each cell inherits the largest peak seen so far — which is how the
    profiling wave reported 3.418 GB for all three region cells, a value belonging to the category
    cell that ran before them. Measured in a fresh process, reg/alabama peaks at 0.505 GB: the
    banked number was 6.8x too large, and it was the number anyone would have used to size FL/CA/TX.

    Called before the fold's tensors are moved to the device, so the resident data counts.
    """
    if device.type == "cuda":
        torch.cuda.reset_peak_memory_stats(device)


def peak_memory(device: torch.device) -> int:
    if device.type == "cuda":
        return int(torch.cuda.max_memory_allocated())
    if device.type == "mps":
        return int(torch.mps.current_allocated_memory())
    return 0


def _mean(values: list[float]) -> float:
    return sum(values) / len(values) if values else 0.0


def _std(values: list[float]) -> float:
    if len(values) < 2:
        return 0.0
    mean = _mean(values)
    return (sum((v - mean) ** 2 for v in values) / (len(values) - 1)) ** 0.5


__all__ = ["FoldDiagnostics", "GradHealth", "gradient_geometry", "gradient_geometry_sidecar",
           "group_geometry", "compile_counters", "convergence", "Phase", "peak_memory"]
