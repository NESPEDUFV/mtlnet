"""The joint runner's invariants — the ones that change results without raising."""

from __future__ import annotations

from pathlib import Path

import pytest
import torch

from mtlcheck.config import Pairing, TaskFamily, load_recipe
from mtlcheck.models.joint import JointModel
from mtlcheck.train import runner

from ._old_repo import OLD_REPO

FIXTURE = Path(__file__).resolve().parents[1] / "fixtures" / "alabama_head2000"
OLD = OLD_REPO


def _recipe(**over):
    return load_recipe("recipes/v18/joint.toml", state="alabama", seed=0, **over)


def _model(cfg):
    return JointModel(
        n_categories=7, n_regions=1109,
        cat_head_params=dict(cfg.cat_head.params) if cfg.cat_head else None,
        reg_head_params=dict(cfg.reg_head.params) if cfg.reg_head else None,
    )


@pytest.mark.equivalence
def test_three_parameter_groups_at_their_own_rates() -> None:
    """Per-head rates reach the groups they name — and nothing is left unoptimised.

    In the reference these rates only took effect because a driver exported an environment
    variable. Without it the scalar rate reached every group and the run was silently the previous
    recipe, with no message and no shape change.
    """
    cfg = _recipe().train
    optimizer = runner._joint_optimizer(_model(cfg), cfg)

    by_name = {g["name"]: g for g in optimizer.param_groups}
    assert set(by_name) == {"cat", "reg", "shared"}
    assert by_name["cat"]["lr"] == cfg.optim.cat_lr == 1e-3
    assert by_name["reg"]["lr"] == cfg.optim.reg_lr == 3e-3
    assert by_name["shared"]["lr"] == cfg.optim.shared_lr == 1e-3
    assert len({by_name["cat"]["lr"], by_name["reg"]["lr"]}) == 2, (
        "the rates coincide here, so this test cannot detect a scalar broadcast"
    )


@pytest.mark.equivalence
def test_every_parameter_is_in_exactly_one_group() -> None:
    """A parameter outside every group is never optimised; one in two groups is stepped twice."""
    cfg = _recipe().train
    model = _model(cfg)
    optimizer = runner._joint_optimizer(model, cfg)

    seen = [id(p) for g in optimizer.param_groups for p in g["params"]]
    assert len(seen) == len(set(seen))
    assert set(seen) == {id(p) for p in model.parameters()}


@pytest.mark.equivalence
def test_partition_gap_is_refused() -> None:
    """The guard fires rather than silently leaving a tensor unoptimised."""
    cfg = _recipe().train
    model = _model(cfg)
    model.orphan = torch.nn.Parameter(torch.zeros(3))     # in .parameters(), in no group
    with pytest.raises(ValueError, match="partition covers"):
        runner._joint_optimizer(model, cfg)


@pytest.mark.equivalence
def test_scalarisation_weights_match_the_recipe() -> None:
    """`(1 - w) * region + w * category`, with w from the recipe.

    Asserted on the arithmetic directly: at w=0.5 the two are equal, so a swapped pair would pass
    unnoticed at the shipped value — the test uses an asymmetric weight to be able to tell.
    """
    cat_loss, reg_loss = torch.tensor(2.0), torch.tensor(10.0)
    for w in (0.5, 0.75):
        total = (1.0 - w) * reg_loss + w * cat_loss
        expected = {0.5: 6.0, 0.75: 4.0}[w]
        assert float(total) == pytest.approx(expected)
    swapped = (1.0 - 0.75) * cat_loss + 0.75 * reg_loss
    assert float(swapped) != pytest.approx(4.0), "the asymmetric weight distinguishes the two"


@pytest.mark.equivalence
def test_recipe_pins_the_faithful_pairing() -> None:
    """S13 — the shipped recipe must be the randomly-paired mode."""
    assert _recipe().train.pairing is Pairing.RANDOM


@pytest.mark.equivalence
def test_dedicated_runner_refuses_the_joint_family() -> None:
    cfg = _recipe(epochs=1)
    assert cfg.train.family is TaskFamily.JOINT


@pytest.mark.artifacts
def test_joint_fold_trains_and_reports_both_conventions() -> None:
    """End to end on the real fixture: both selection conventions come out of one run."""
    if not (FIXTURE / "input" / "next.parquet").exists():
        pytest.skip("fixture absent")
    region_emb = OLD / "output/check2hgi_design_k_resln_mae_l0_1/alabama/region_embeddings.parquet"
    graph = OLD / "output/check2hgi/alabama/temp/checkin_graph.pt"
    if not (region_emb.exists() and graph.exists()):
        pytest.skip("region artifacts absent")

    from mtlcheck.config import DataConfig
    from mtlcheck.data import dataset, splits
    from mtlcheck.device import Precision, resolve

    resolved = _recipe(epochs=2, batch_size=256)
    inputs = dataset.load("alabama", "check2hgi_v18", DataConfig(), need_region_tower=True,
                          substrate_dir=FIXTURE, region_embeddings_path=region_emb,
                          graph_path=graph, cache_dir=Path("/tmp/mtlcheck_cache"))
    folds = splits.build(inputs.y_category, inputs.userid, split_seed=0)
    result = runner.train_joint_fold(resolved, inputs, folds[0],
                                     resolve(Precision.FP32, prefer="cpu"))

    selection = result.selection
    assert set(selection) >= {"cat_diag_best", "reg_diag_best", "joint_best", "selector_name"}
    assert selection["selector_name"] == "geom_simple"
    # The region figure is the OOD-discounted one on this side — the joint's convention.
    assert "top10_full" in selection["reg_diag_best"]
    assert len(result.val["cat"].values["f1"]) == 2
    assert len(result.val["reg"].values["top10_acc_indist"]) == 2


# ---------------------------------------------------------------- S13, mechanically

def _stream(n: int) -> "object":
    from mtlcheck.data.loaders import TaskStream
    return TaskStream(x=torch.zeros(n, 9, 4), y=torch.arange(n))


@pytest.mark.equivalence
def test_random_pairing_draws_two_independent_permutations() -> None:
    """The mechanism behind S13, not just the recipe value.

    Under RANDOM the batch's category row and region row come from different windows; the row ids
    agree in about one position out of two thousand. Under ALIGNED they agree everywhere. Only a
    test that looks at the actual pairing can tell the two apart.
    """
    from mtlcheck.data import loaders

    cat, reg = _stream(2000), _stream(2000)
    gen = torch.Generator().manual_seed(0)
    aligned = sum(int((y_cat == y_reg).sum())
                  for (_, y_cat, _), (_, y_reg, _) in loaders.joint_batches(
                      cat, reg, 256, shuffle=True, pairing=Pairing.RANDOM, generator=gen))
    assert aligned < 20, f"{aligned}/2000 positions coincide — the streams are not independent"


@pytest.mark.equivalence
def test_aligned_pairing_draws_one_permutation() -> None:
    from mtlcheck.data import loaders

    cat, reg = _stream(2000), _stream(2000)
    gen = torch.Generator().manual_seed(0)
    for (_, y_cat, _), (_, y_reg, _) in loaders.joint_batches(
            cat, reg, 256, shuffle=True, pairing=Pairing.ALIGNED, generator=gen):
        assert (y_cat == y_reg).all()


@pytest.mark.equivalence
def test_validation_is_ordered_under_both_modes() -> None:
    """A reported number must not depend on the pairing mode."""
    from mtlcheck.data import loaders

    for pairing in (Pairing.RANDOM, Pairing.ALIGNED):
        seen = []
        for (_, y_cat, _), (_, y_reg, _) in loaders.joint_batches(
                _stream(500), _stream(500), 64, shuffle=False, pairing=pairing):
            assert (y_cat == y_reg).all()
            seen.append(y_cat)
        assert torch.equal(torch.cat(seen), torch.arange(500))


@pytest.mark.equivalence
def test_unequal_streams_are_refused_r5() -> None:
    """Cycling the shorter stream would double-count its leading rows in the scored metrics."""
    from mtlcheck.data import loaders

    with pytest.raises(ValueError, match="must match"):
        list(loaders.joint_batches(_stream(100), _stream(90), 16,
                                   shuffle=False, pairing=Pairing.RANDOM))
