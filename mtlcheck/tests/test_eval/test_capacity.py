"""FLOPs — the number this project has never had.

Every v18 log reads `FLOPS: 0 | Params: 0`, because the reference routed FLOPs through fvcore and
fvcore was not installed: a missing optional dependency that failed to ZERO rather than failing
loudly, for the life of the study. Hence torch's in-tree counter and no optional dependency.
"""

from __future__ import annotations

import pytest
import torch

from mtlcheck.config import load_recipe
from mtlcheck.train import capacity, runner
from test_capture import _fold, _inputs, _spec


def test_flops_scale_with_the_batch_and_the_per_sample_figure_does_not() -> None:
    """Per-sample is the comparable figure: a joint forward serves two tasks at once."""
    model = torch.nn.Sequential(torch.nn.Flatten(), torch.nn.Linear(9 * 64, 128),
                                torch.nn.ReLU(), torch.nn.Linear(128, 7))
    out = capacity.measure_flops(model, (torch.randn(1, 9, 64),), batch_sizes=(1, 8))

    assert out["by_batch"]["8"]["flops"] == 8 * out["by_batch"]["1"]["flops"]
    assert out["by_batch"]["8"]["per_sample"] == pytest.approx(out["by_batch"]["1"]["per_sample"])
    assert out["measured_at_batch"] == 8, "the per-sample figure is quoted at the largest batch"


def test_a_shape_the_model_refuses_degrades_rather_than_crashes() -> None:
    class Fussy(torch.nn.Module):
        def forward(self, x):
            if x.shape[0] > 4:
                raise RuntimeError("nope")
            return x.sum()

    out = capacity.measure_flops(Fussy(), (torch.randn(1, 3),), batch_sizes=(2, 64))
    assert "2" in out["by_batch"] and "64" not in out["by_batch"]
    assert out["measured_at_batch"] == 2


def test_the_cost_of_a_joint_cell_is_recorded_on_fold_zero_only() -> None:
    resolved = load_recipe("recipes/v18/joint.toml", state="alabama", seed=0, epochs=2,
                           batch_size=128)
    first = runner.train_joint_fold(resolved, _inputs(), _fold(sealed=True), _spec())
    assert first.flops["flops_per_sample"] > 0

    from mtlcheck.data import splits
    import numpy as np
    other = splits.Fold(index=1, train=_fold(True).train, val=_fold(True).val,
                        inner_val=_fold(True).inner_val)
    later = runner.train_joint_fold(resolved, _inputs(), other, _spec())
    assert later.flops == {}, "the model is identical across folds; measuring five times banks five"

    summary = capacity.cost_summary(first.parameter_counts, first.flops)
    assert summary["parameters"] == first.parameter_counts["total"]
    assert "flops_per_sample" in summary


def test_a_recurrent_head_is_counted_rather_than_reported_as_free() -> None:
    """The defect that forced the CPU measurement, now the regression test for its fix.

    Measured on the A40, the real Alabama category head reported 3,584 FLOPs/sample — exactly
    2 x 256 x 7, its final Linear alone, for a 1.43 M-parameter GRU: nn.GRU dispatches to fused
    cuDNN kernels the counter never sees. Taken at face value that made the joint model look 8.5x
    more expensive than two dedicated ones, when most of the ratio was one arm undercounted by three
    orders of magnitude. On CPU the same module decomposes into visible matmuls.
    """
    class Recurrent(torch.nn.Module):
        def __init__(self):
            super().__init__()
            self.gru = torch.nn.GRU(64, 256, batch_first=True)
            self.classifier = torch.nn.Linear(256, 7)

        def forward(self, x):
            out, _ = self.gru(x)
            return self.classifier(out[:, -1])

    model = Recurrent()
    out = capacity.measure_flops(model, (torch.randn(1, 9, 64),), batch_sizes=(4,))

    assert out["measured_on"] == "cpu"
    assert not out.get("incomplete"), "a GRU must be counted, not flagged, once measured on CPU"
    # The classifier alone would be 2 x 256 x 7 = 3,584. The recurrent body dwarfs it.
    assert out["flops_per_sample"] > 100 * 3584
    assert out["coverage_ratio"] > capacity.MIN_COVERAGE


def test_measuring_never_touches_the_live_model() -> None:
    """It works on a deepcopy, so a model training on an accelerator is not moved or re-moded.

    Moving the live model to CPU and back mid-run would touch the object the training loop holds;
    leaving it in eval would silently disable dropout for the rest of the fold.
    """
    model = torch.nn.Sequential(torch.nn.Flatten(), torch.nn.Linear(9 * 64, 7))
    model.train()
    before = model[1].weight.clone()

    capacity.measure_flops(model, (torch.randn(1, 9, 64),), batch_sizes=(2,))

    assert model.training, "the live model must stay in the mode it arrived in"
    assert torch.equal(model[1].weight, before), "and its weights must be untouched"


def test_a_dense_model_is_not_flagged() -> None:
    """The guard must not cry wolf on the models it CAN count."""
    model = torch.nn.Sequential(torch.nn.Flatten(), torch.nn.Linear(9 * 64, 256),
                                torch.nn.ReLU(), torch.nn.Linear(256, 7))
    out = capacity.measure_flops(model, (torch.randn(1, 9, 64),), batch_sizes=(4,))
    assert not out.get("incomplete")
    assert out["coverage_ratio"] >= capacity.MIN_COVERAGE
    assert capacity.comparable(capacity.cost_summary({"total": 1}, out))


def test_the_coverage_backstop_still_fires_on_something_uncountable() -> None:
    """The type list is a tripwire for known cases; this catches the ones it has not learned."""
    class Opaque(torch.nn.Module):
        def __init__(self):
            super().__init__()
            self.weight = torch.nn.Parameter(torch.randn(4096, 4096))

        def forward(self, x):
            return x + self.weight.sum()          # touches every weight, counts as no matmul

    out = capacity.measure_flops(Opaque(), (torch.randn(1, 4),), batch_sizes=(2,))
    assert out["incomplete"] is True
    assert out["coverage_ratio"] < capacity.MIN_COVERAGE
