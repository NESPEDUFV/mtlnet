"""E11 and the runner's invariants — the ones that move every number without raising."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest
import torch

from mtlcheck.config import DataConfig, TaskFamily, load_recipe
from mtlcheck.data import dataset, loaders, splits
from mtlcheck.device import Precision, resolve
from mtlcheck.models import CategoryHead
from mtlcheck.train import runner

FIXTURE = Path(__file__).resolve().parents[1] / "fixtures" / "alabama_head2000"


def _recipe(**overrides):
    return load_recipe("recipes/v18/cat.toml", state="alabama", seed=0, **overrides)


@pytest.mark.equivalence
def test_e11_scheduler_advances_per_step_not_per_epoch() -> None:
    """S15 — the learning-rate series must complete exactly one cycle over the run.

    Stepping per epoch instead of per batch leaves the schedule mid-cycle: every rate after the
    first epoch is wrong, no shape changes, and nothing raises. The series is checked directly.
    """
    cfg = _recipe(epochs=4).train
    model = CategoryHead(embed_dim=64, num_classes=7)
    optimizer = torch.optim.AdamW(model.parameters(), lr=cfg.optim.lr)
    steps_per_epoch = 8
    scheduler = runner._build_scheduler(optimizer, cfg, steps_per_epoch)

    series = []
    for _ in range(cfg.epochs * steps_per_epoch):
        series.append(optimizer.param_groups[0]["lr"])
        optimizer.step()
        scheduler.step()

    assert len(series) == 32
    peak = max(series)
    # The sampled peak falls between two steps and never lands exactly on max_lr; what matters is
    # that the cycle is scaled to it, not that a sample coincides with it.
    assert peak == pytest.approx(cfg.optim.max_lr, rel=1e-2), (
        f"the cycle peaks at {peak}, not near the configured max_lr {cfg.optim.max_lr}"
    )
    # OneCycle ramps then anneals: the peak is interior, and the last rate is far below it.
    assert 0 < series.index(peak) < len(series) - 1
    assert series[-1] < peak / 100, "the schedule did not finish its anneal"

    # The discriminating check. Stepping once per EPOCH consumes 4 of the 32 budgeted steps, so the
    # cycle never anneals and the run ends near its peak — the failure this test exists for. If the
    # two series were not far apart here, the assertions above could not tell them apart.
    slow_opt = torch.optim.AdamW(CategoryHead(embed_dim=64, num_classes=7).parameters(),
                                 lr=cfg.optim.lr)
    slow_sched = runner._build_scheduler(slow_opt, cfg, steps_per_epoch)
    slow_series = []
    for _ in range(cfg.epochs):
        slow_opt.step()
        slow_sched.step()
        slow_series.append(slow_opt.param_groups[0]["lr"])
    assert slow_series[-1] > 10 * series[-1], (
        "a per-epoch-stepped schedule must end far from the anneal floor, or this test cannot "
        "distinguish the two stepping rules"
    )


@pytest.mark.equivalence
def test_steps_per_epoch_matches_the_loader() -> None:
    """The scheduler's budget and the loop's actual step count must be the same number."""
    stream = loaders.TaskStream(x=torch.zeros(2000, 9, 4), y=torch.zeros(2000, dtype=torch.long))
    for batch_size in (256, 512, 8192):
        counted = sum(1 for _ in loaders.batches(stream, batch_size, shuffle=False))
        assert counted == loaders.steps_per_epoch(len(stream), batch_size)


@pytest.mark.artifacts
def test_fold_seed_is_order_independent() -> None:
    """Fold k trains under `seed + k`, so its result does not depend on the folds before it."""
    from mtlcheck.seeding import fold_seed
    assert [fold_seed(7, k) for k in range(5)] == [7, 8, 9, 10, 11]


@pytest.mark.artifacts
def test_runner_trains_end_to_end_and_records_both_series() -> None:
    if not (FIXTURE / "input" / "next.parquet").exists():
        pytest.skip("fixture absent")

    resolved = _recipe(epochs=3, batch_size=256)
    spec = resolve(Precision.FP32, prefer="cpu")
    inputs = dataset.load("alabama", "check2hgi_v18", DataConfig(),
                          need_region_tower=False, substrate_dir=FIXTURE)
    folds = splits.build(inputs.y_category, inputs.userid, split_seed=0)

    result = runner.train_fold(resolved, inputs, folds[0], spec,
                               build_model=lambda d, c: CategoryHead(embed_dim=d, num_classes=c))

    assert len(result.train_loss) == 3
    assert len(result.val["cat"].values["f1"]) == 3
    assert result.selection["metric"] == "f1"
    assert 1 <= result.selection["epoch"] <= 3
    assert result.seed == 0, "fold 0 trains under the base seed"
    # The certificate is measured every epoch, not sampled once.
    assert set(result.ambiguous_rows) == {"top3", "top5"}


@pytest.mark.artifacts
def test_joint_family_is_refused_by_the_dedicated_runner() -> None:
    """A wrong-family call fails loudly rather than training something unintended.

    Now that the joint runner exists this is a misuse error, not an unimplemented one — the
    distinction matters to whoever reads the message.
    """
    if not (FIXTURE / "input" / "next.parquet").exists():
        pytest.skip("fixture absent")
    resolved = load_recipe("recipes/v18/joint.toml", state="alabama", seed=0, epochs=1)
    inputs = dataset.load("alabama", "check2hgi_v18", DataConfig(),
                          need_region_tower=False, substrate_dir=FIXTURE)
    folds = splits.build(inputs.y_category, inputs.userid, split_seed=0)
    with pytest.raises(ValueError, match="call train_joint_fold"):
        runner.train_fold(resolved, inputs, folds[0], resolve(Precision.FP32, prefer="cpu"),
                          build_model=lambda d, c: CategoryHead(embed_dim=d, num_classes=c))
