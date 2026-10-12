"""What the model costs to run — the honest half of "one model, one forward, N tasks".

Nobody in this project has ever had this number. Every v18 log reads `FLOPS: 0 | Params: 0`, because
the reference routed FLOPs through fvcore and fvcore was not installed — a missing optional
dependency that failed to **zero** rather than failing loudly, for the entire life of the study. The
only FLOPs figures in the dissertation are transcribed from an earlier paper and carry a
prose/table contradiction nobody could re-measure.

So: `torch.utils.flop_counter.FlopCounterMode`, which ships with torch. No optional dependency, no
silent zero.

## Measured on the CPU, always — even when training runs on a GPU

FLOPs is meant to be a property of the model's arithmetic, not of the machine. It stops being one the
moment a module dispatches to a fused kernel the counter cannot see: `nn.GRU` on CUDA goes to cuDNN
and is counted at nearly zero, while the same module on CPU decomposes into the matmuls the counter
does intercept. Measured on the A40, the Alabama category head reported **3,584** FLOPs/sample —
exactly `2 x 256 x 7`, its final Linear alone, for a 1.43 M-parameter recurrent model. On CPU it
reports ~25.7 M, which is the right order.

So the measurement takes a CPU copy of the module and counts there. Two things follow, both good:
the recurrent heads are counted at all, and the number no longer depends on which machine ran the
cell — an A40 and a laptop now agree, which is the least a device-free quantity can offer.

The copy is deliberate. Moving the live model to CPU and back mid-run would touch the object the
training loop holds; a `deepcopy` of the base module costs one model's worth of host memory for a
few seconds at fold 0 and cannot perturb anything.

## Measured where the model is BUILT

Not on a reconstructed one. That is the R14 lesson, and it was expensive: the published capacity
audit counted a model assembled from module defaults (644,359 parameters) while the run used
1,433,863, and an arm advertised as "capacity-matched" actually ran at 230% of its target. A number
about the model must come from the object the run holds.

## Read it with two caveats attached

**FLOPs is not latency.** Attention is memory-bound, the compiler fuses, and a model with fewer FLOPs
can be slower. FLOPs and parameters are device-free and belong in the cost claim; wall-clock is
secondary and only comparable within one execution configuration.

**It may not flatter the thesis.** At Alabama the joint model is 4,197,621 parameters against
1,850,980 for the two dedicated models summed — 2.27x. The dissertation already carries a standing
guard not to promise lower compute cost, and this is why. Bank it anyway: a cost number that cuts
against the argument is exactly the number a committee asks for, and "we measured it" is a far
better position than "we did not".
"""

from __future__ import annotations

import logging
from typing import Any

import torch

logger = logging.getLogger(__name__)


#: Modules whose kernels the counter can miss. On CUDA `nn.GRU`/`LSTM`/`RNN` dispatch to fused cuDNN
#: kernels and are counted at nearly zero — which is why the measurement moved to CPU, where they
#: decompose into visible matmuls. The list is kept as a tripwire for the case where a CPU copy is
#: impossible or a future module fuses on CPU too; it no longer fires on the normal path.
UNCOUNTED_MODULES = ()

#: Backstop, not the primary signal. Below this ratio of measured FLOPs to `2 x parameters` the count
#: is not believable — every weight of a dense layer is used at least once per sample, so `2 x
#: params` is a floor. It is a backstop because it is DEVICE-DEPENDENT: on CPU a GRU decomposes into
#: ops the counter sees and coverage looks healthy; on CUDA the same module dispatches to a fused
#: cuDNN kernel and coverage collapses. The module-type check is what catches the known cases; this
#: catches the ones `UNCOUNTED_MODULES` has not learned about yet.
MIN_COVERAGE = 0.5


def uncounted(model: torch.nn.Module) -> list[str]:
    """Module types present in the model that the flop counter cannot see."""
    return sorted({type(m).__name__ for m in model.modules()
                   if isinstance(m, UNCOUNTED_MODULES)})


def measure_flops(model: torch.nn.Module, sample: tuple[torch.Tensor, ...],
                  batch_sizes: tuple[int, ...] = (1, 2048)) -> dict[str, Any]:
    """Forward FLOPs at one or more batch sizes, on a CPU copy of the model as it was built.

    Returns per-batch-size totals plus the per-sample figure, which is the comparable one: a joint
    forward serves two tasks, so "per sample" is what a joint-vs-two-dedicated comparison divides.

    Runs in `eval` mode under `no_grad` — this is inference cost. Training cost is roughly 3x by the
    usual convention, and stating the convention beats baking a multiplier into the number.
    """
    try:
        from torch.utils.flop_counter import FlopCounterMode
    except ImportError:                                        # pragma: no cover — torch >= 2.0
        return {"error": "torch.utils.flop_counter unavailable"}

    import copy

    # A CPU copy of the UNCOMPILED module: fused accelerator kernels are invisible to the counter,
    # and the live model must not be touched. `_orig_mod` because a compiled wrapper adds a graph
    # this measurement has no use for.
    base = getattr(model, "_orig_mod", model)
    try:
        measured = copy.deepcopy(base).to("cpu").eval()
    except Exception as exc:                                   # pragma: no cover
        return {"error": f"could not copy the model to CPU: {exc}"}
    sample = tuple(t.detach().to("cpu") for t in sample)

    out: dict[str, Any] = {"mode": "forward/inference", "measured_on": "cpu", "by_batch": {}}
    try:
        for size in batch_sizes:
            batch = tuple(_resize(t, size) for t in sample)
            counter = FlopCounterMode(display=False)
            try:
                with counter, torch.no_grad():
                    measured(*batch)
            except Exception as exc:                           # a shape the model will not take
                logger.warning("FLOPs at batch %d failed: %s", size, exc)
                continue
            total = int(counter.get_total_flops())
            out["by_batch"][str(size)] = {"flops": total, "per_sample": total / size}
        if not out["by_batch"]:
            return {"error": "no batch size could be measured"}
        largest = max(out["by_batch"], key=lambda k: int(k))
        out["flops_per_sample"] = out["by_batch"][largest]["per_sample"]
        out["measured_at_batch"] = int(largest)

        # The guard. A FLOPs number that silently omits the model's main module is worse than no
        # number, because it is quotable — and the reference's fvcore path already taught this
        # project that a cost counter can fail to zero and be believed for a year.
        parameters = sum(p.numel() for p in measured.parameters())
        coverage = out["flops_per_sample"] / (2 * parameters) if parameters else 0.0
        out["coverage_ratio"] = round(coverage, 4)
        missing = uncounted(measured)
        if missing or coverage < MIN_COVERAGE:
            out["incomplete"] = True
            out["uncounted_modules"] = missing
            logger.warning(
                "FLOPs are INCOMPLETE: %.0f per sample against %d parameters (ratio %.4f)%s. "
                "Do not quote this as the model's cost.",
                out["flops_per_sample"], parameters, coverage,
                f"; the counter cannot see {missing}" if missing else "")
    finally:
        del measured
    return out


def _resize(tensor: torch.Tensor, size: int) -> torch.Tensor:
    """A batch of exactly `size`, by repeating rows — FLOPs depend on shape, not on values."""
    if tensor.shape[0] == size:
        return tensor
    if tensor.shape[0] > size:
        return tensor[:size]
    repeats = (size + tensor.shape[0] - 1) // tensor.shape[0]
    return tensor.repeat(repeats, *([1] * (tensor.dim() - 1)))[:size]


def cost_summary(parameter_counts: dict[str, int], flops: dict[str, Any]) -> dict[str, Any]:
    """The two device-free numbers a cost claim rests on, side by side."""
    out: dict[str, Any] = {"parameters": int(parameter_counts.get("total", 0))}
    if "flops_per_sample" in flops:
        out["flops_per_sample"] = float(flops["flops_per_sample"])
        out["measured_at_batch"] = int(flops["measured_at_batch"])
    # Carried into the summary, not just the log: whoever compares two arms must see that one of
    # them is undercounted, and a warning printed during training is not there when they look.
    if flops.get("incomplete"):
        out["flops_incomplete"] = True
        out["uncounted_modules"] = flops.get("uncounted_modules", [])
        out["coverage_ratio"] = flops.get("coverage_ratio")
    if "error" in flops:
        out["flops_error"] = flops["error"]
    return out


def comparable(*summaries: dict[str, Any]) -> bool:
    """Whether a set of cost summaries may be compared at all. Any incomplete one poisons the set."""
    return not any(s.get("flops_incomplete") for s in summaries)


__all__ = ["measure_flops", "cost_summary", "comparable", "uncounted",
           "UNCOUNTED_MODULES", "MIN_COVERAGE"]
