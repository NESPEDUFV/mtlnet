"""The health scalars — numbers the training loop already held and used to discard.

Every field here traces to a named incident. The fp16 collapse at CA epoch 30 was diagnosed from the
gradient-norm series and a non-finite counter, in FRESH instrumented runs, after the fact; three FL
cells were burned discovering that per-head learning rates were inert under OneCycle; a "compiled"
arm ran eager in silence because the artifact recorded the intention rather than the outcome.
"""

from __future__ import annotations

import pytest
import torch

from mtlcheck.config import load_recipe
from mtlcheck.train import diagnostics as diag
from mtlcheck.train import runner
from test_capture import _fold, _inputs, _spec


def test_grad_health_accumulates_on_device_and_syncs_once() -> None:
    """A naive `.item()` per tensor per step is ~2M host syncs over a fold, and it shows.

    So the accumulator holds device tensors and the host reads four numbers per EPOCH.
    """
    device = torch.device("cpu")
    health = diag.GradHealth(device, max_norm=1.0)
    sink = diag.FoldDiagnostics()

    for value in (0.5, 2.0, 4.0, float("inf")):
        health.observe(torch.tensor(value))
    health.flush(sink)

    # The mean is over the FINITE batches. It used to divide by 4, booking the non-finite batch as
    # a norm of 0.0 — so during the divergence these fields exist to diagnose, all three moved the
    # WRONG WAY: 90% of an epoch non-finite at a constant true norm of 3.0 read as [3.0, 0.3, 0.0],
    # i.e. unchanged behaviour reported as a tenfold calming. The old test asserted /4 under a
    # comment claiming inf was excluded, which locked the defect in.
    assert sink.grad_norm_mean[0] == pytest.approx((0.5 + 2.0 + 4.0) / 3)
    assert sink.grad_norm_max[0] == pytest.approx(4.0)
    # And a non-finite batch counts as clipped, because it is: clip_grad_norm_ scales by
    # 1/(inf + eps) = 0, i.e. maximally, and the step is still taken.
    assert sink.clipped_fraction[0] == pytest.approx(0.75), "2 over max_norm plus the inf"
    assert sink.nonfinite_batches == 1
    assert sink.nonfinite_per_epoch == [1], "with an epoch index, not just a total"

    health.flush(sink)
    assert len(sink.grad_norm_mean) == 1, "an empty epoch must not append a bogus row"


def test_a_joint_run_records_what_the_loop_already_computed() -> None:
    resolved = load_recipe("recipes/v18/joint.toml", state="alabama", seed=0, epochs=3,
                           batch_size=128, diagnostics=True)
    result = runner.train_joint_fold(resolved, _inputs(), _fold(sealed=True), _spec())
    d = result.diagnostics

    assert d["grad_norm_mean"] > 0 and d["grad_norm_max"] >= d["grad_norm_mean"]
    assert 0.0 <= d["clipped_fraction_mean"] <= 1.0
    assert d["nonfinite_batches"] == 0, "a healthy run has none; a number > 0 is the alarm"

    # Per-task losses: only the scalarised sum was recorded before, and the loss-balance question
    # cannot be asked afterwards without the components.
    assert len(d["train_loss_cat"]) == 3 and len(d["train_loss_reg"]) == 3
    weight = resolved.train.category_weight
    combined = weight * d["train_loss_cat"][0] + (1 - weight) * d["train_loss_reg"][0]
    assert combined == pytest.approx(result.train_loss[0], rel=1e-4), (
        "the two components must reconstruct the scalarised loss the optimiser actually saw")

    # The realised schedule, not the requested one.
    # Named for what it is: sampled AFTER the epoch's last scheduler.step(), which under a
    # per-batch OneCycle has already written the rate for the step that follows. The old label
    # "first_epoch" described epoch 2's opening rate, 22x what epoch 1 applied.
    lrs = d["lr_per_group_at_epoch_end"]
    assert len(lrs["first"]) == 3, "three groups: cat head, reg head, shared trunk"
    assert max(lrs["max_observed"]) > 0
    assert "not the applied peak" in lrs["note"]


def test_a_dedicated_run_records_them_too() -> None:
    resolved = load_recipe("recipes/v18/cat.toml", state="alabama", seed=0, epochs=3,
                           batch_size=128, diagnostics=True)
    d = runner.train_fold(resolved, _inputs(), _fold(sealed=True), _spec()).diagnostics
    assert d["grad_norm_mean"] > 0
    assert "train_loss_cat" not in d, "per-task components are a joint-only concept"


def test_a_collapse_is_distinguishable_from_its_own_reverse() -> None:
    """Run means are permutation-invariant, so they cannot answer "when did it break".

    The whole justification for these fields is that the CA divergence was diagnosed from a SERIES.
    Collapsed to means and a total, a fold that died at epoch 30 and its exact reverse produce a
    byte-identical block.
    """
    device = torch.device("cpu")

    def fold(nonfinite_epochs):
        sink = diag.FoldDiagnostics()
        health = diag.GradHealth(device, max_norm=1.0)
        for epoch in range(5):
            for _ in range(4):
                health.observe(torch.tensor(float("inf") if epoch in nonfinite_epochs else 2.0))
            health.flush(sink)
        return sink.summary()

    died_late = fold({3, 4})
    died_early = fold({0, 1})
    assert died_late["nonfinite_batches"] == died_early["nonfinite_batches"] == 8
    assert died_late["nonfinite_per_epoch"] != died_early["nonfinite_per_epoch"]
    assert died_late["nonfinite_per_epoch"] == [0, 0, 0, 4, 4]


def test_compile_counters_are_this_folds_delta_and_use_keys_that_exist() -> None:
    """Process-global counters, one process per wave: absolutes belong to whatever ran before.

    Measured, three cells in one process: graph_breaks 0 -> 3 -> 8, and an EAGER cell banked 3
    inherited from the compiled cell before it — the same high-water-mark defect reset_peak_memory
    exists to fix. And `recompiles` was never a real torch counter: reading it returned 0 forever
    and silently inserted the dead key, so the field could not tell compiled from eager at all.
    """
    before = diag.compile_snapshot()
    delta = diag.compile_counters(before)
    assert "recompiles" not in delta, "a key torch does not have is a permanent zero"
    assert set(delta) >= {"graph_breaks", "frames_total", "frames_ok"}
    assert all(v == 0 for v in delta.values()), "nothing compiled between the two calls"
