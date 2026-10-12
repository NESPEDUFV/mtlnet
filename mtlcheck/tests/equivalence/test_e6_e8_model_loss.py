"""E6, E7, E8 — the head and the criterion against the reference implementations.

These import the OLD repository directly and compare object to object. That is the only form of
equivalence test with no shared code between the two sides: same weights, same inputs, two
independently written forward passes.

E7 is a **checkpoint transplant**, not a shared-seed comparison. A clean-room rewrite does not
consume the global RNG in the same order, so "same seed -> same weights" is unachievable and no
float tolerance bridges different random initialisations. Loading the reference's own parameters
into the new module and comparing outputs tests what actually matters: that the two compute the same
function of the same weights.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pytest
import torch

from ._old_repo import OLD_REPO

OLD_SRC = OLD_REPO / "src"


@pytest.fixture(scope="module")
def old_repo():
    """Make the reference implementation importable, or skip."""
    if not OLD_SRC.exists():
        pytest.skip(f"reference repo absent: {OLD_SRC}")
    if str(OLD_SRC) not in sys.path:
        sys.path.insert(0, str(OLD_SRC))
    try:
        import losses.calibrated as calibrated
        from models.next.next_gru.head import NextHeadGRU
    except Exception as exc:                                  # pragma: no cover
        pytest.skip(f"reference modules not importable: {exc}")
    return {"calibrated": calibrated, "NextHeadGRU": NextHeadGRU}


# ---------------------------------------------------------------- E8 · the criterion

NUM_CLASSES = 7
# Deliberately skewed: a uniform prior makes the logit-adjustment offset a constant, which cancels
# in the softmax and would hide a wrong prior entirely.
SKEWED = [9000, 400, 12000, 300, 1500, 7000, 2200]


def _fixture():
    torch.manual_seed(0)
    logits = torch.randn(512, NUM_CLASSES, dtype=torch.float64).float()
    target = torch.randint(0, NUM_CLASSES, (512,))
    train_labels = torch.cat([torch.full((n,), c) for c, n in enumerate(SKEWED)])
    return logits, target, train_labels


@pytest.mark.equivalence
@pytest.mark.parametrize("config", [
    pytest.param({}, id="plain-CE"),
    pytest.param({"logit_adjust_tau": 0.5}, id="logit-adjust-0.5"),
    pytest.param({"logit_adjust_tau": 1.0}, id="logit-adjust-1.0"),
    pytest.param({"balanced_weights": True, "weight_reduction": "batch_mean"},
                 id="balanced-batch-mean"),
])
def test_e8_loss_matches_the_calibrated_reference(old_repo, config) -> None:
    """Against `CalibratedLoss` — the T1.4 arm's criterion."""
    from mtlcheck.train import losses

    logits, target, train_labels = _fixture()
    mine = losses.build(NUM_CLASSES, train_labels, **config)
    theirs = old_repo["calibrated"].build_calibrated_loss(
        NUM_CLASSES, train_labels,
        logit_adjust_tau=config.get("logit_adjust_tau", 0.0),
        tail_mode="balanced" if config.get("balanced_weights") else None,
    )
    ours, ref = mine(logits, target), theirs(logits, target)
    assert torch.allclose(ours, ref, atol=0, rtol=0), (
        f"loss differs: ours {ours.item():.10f} vs reference {ref.item():.10f}"
    )


@pytest.mark.equivalence
def test_e8_balanced_default_matches_the_v17_incumbent() -> None:
    """Against `nn.CrossEntropyLoss(weight, reduction='mean')` — the criterion logit adjustment
    DISPLACED, and therefore the comparator the +2.86 pp gain was measured against.

    The two balanced variants are not interchangeable. Torch's weighted mean divides by the sum of
    the batch's weights; the per-row mean divides by the batch size. On this skewed prior they
    differ by a large factor, so picking the wrong one silently changes the training trajectory of
    the arm the lever is compared to.
    """
    from mtlcheck.train import losses

    logits, target, train_labels = _fixture()
    counts = losses.class_counts(train_labels, NUM_CLASSES).float()
    alpha = counts.sum() / (NUM_CLASSES * counts)          # sklearn 'balanced'

    mine = losses.build(NUM_CLASSES, train_labels, balanced_weights=True)   # default reduction
    reference = torch.nn.CrossEntropyLoss(weight=alpha, reduction="mean")

    ours, ref = mine(logits, target), reference(logits, target)
    assert torch.allclose(ours, ref, atol=0, rtol=0), (
        f"ours {ours.item():.10f} vs nn.CrossEntropyLoss {ref.item():.10f}"
    )

    other = losses.build(NUM_CLASSES, train_labels, balanced_weights=True,
                         weight_reduction="batch_mean")(logits, target)
    assert not torch.allclose(ours, other, rtol=1e-3), (
        "the two reductions agree here, so this test cannot tell them apart — pick a more skewed "
        "prior or a different batch"
    )


@pytest.mark.equivalence
def test_logit_adjustment_is_train_only(old_repo) -> None:
    """The offset is a constant vector applied inside the criterion — evaluation logits are raw.

    Stated because it is the property that makes the lever leak-free: if the adjustment reached the
    scoring path, the reported metric would be of a different classifier than the deployed one.
    """
    from mtlcheck.train import losses

    train_labels = torch.tensor([0] * 100 + [1] * 5)
    crit = losses.build(2, train_labels, logit_adjust_tau=0.5)
    assert crit.la_offset is not None and crit.la_offset.shape == (2,)

    logits = torch.randn(16, 2)
    # The criterion shifts its own copy; the caller's tensor is untouched, so whatever scores the
    # model sees exactly what the model produced.
    before = logits.clone()
    crit(logits, torch.randint(0, 2, (16,)))
    assert torch.equal(logits, before)


@pytest.mark.equivalence
def test_stacking_is_refused() -> None:
    from mtlcheck.train import losses
    with pytest.raises(ValueError, match="mutually exclusive"):
        losses.build(7, torch.zeros(10, dtype=torch.long),
                     logit_adjust_tau=0.5, balanced_weights=True)


# ---------------------------------------------------------------- E6 / E7 · the head

# The v18 category head reports this many parameters in a live run's own log. Pinned as a literal
# because it is an EXTERNAL observation: it does not come from either implementation, so it cannot
# drift with both of them.
V18_CAT_HEAD_PARAMS = 1_433_863
# And the dedicated region head's count, from the capacity analysis in the reference study's
# POSTPONED.md ("alabama 2,466,542 vs 417,117" — joint region pathway vs dedicated baseline).
V18_REG_HEAD_PARAMS = 417_117


@pytest.mark.equivalence
def test_e6_parameter_count_matches_the_run(old_repo) -> None:
    """Invariant S12, at the configuration that actually ran.

    The trap this guards: the reference CLI's `--model` swaps the head CLASS while its
    hyperparameters keep coming from the task factory, so the v18 category head is `next_gru` with
    4 layers and dropout 0.1 — not the module's own 2 and 0.3. An earlier version of this test
    compared both implementations at their MODULE defaults, which agreed perfectly while describing
    a model that never ran and is less than half the size.

    So the shape comes from the recipe, and the count is checked against a number observed outside
    both implementations.
    """
    from mtlcheck.config import load_recipe
    from mtlcheck.models.factory import build_head

    recipe = load_recipe("recipes/v18/cat.toml", state="alabama", seed=0)
    mine = build_head(recipe.train.cat_head, embed_dim=64, num_classes=7)
    n_mine = sum(p.numel() for p in mine.parameters())

    assert n_mine == V18_CAT_HEAD_PARAMS, (
        f"the recipe builds a {n_mine}-parameter head; the v18 run reports "
        f"{V18_CAT_HEAD_PARAMS}"
    )

    # And against the reference class, constructed the way the reference run constructs it.
    theirs = old_repo["NextHeadGRU"](embed_dim=64, num_classes=7,
                                     **recipe.train.cat_head.params)
    assert n_mine == sum(p.numel() for p in theirs.parameters())

    # The module-default construction is a DIFFERENT model — asserted so the two cannot be
    # confused again.
    from mtlcheck.models.gru import CategoryHead
    defaults = sum(p.numel() for p in CategoryHead(embed_dim=64, num_classes=7).parameters())
    assert defaults != n_mine, "module defaults now coincide with the run; this guard is moot"


@pytest.mark.equivalence
def test_e6_region_head_parameter_count_matches_the_study() -> None:
    """The dedicated region head's capacity, against the figure the capacity analysis quotes.

    Load-bearing: whether the joint model's region advantage at the large states is multi-task
    sharing or simply parameters is an open question, and the experiment that would settle it
    compares capacity-matched arms. A head that silently changes width closes it by accident.
    """
    from mtlcheck.config import load_recipe
    from mtlcheck.models.factory import build_head

    recipe = load_recipe("recipes/v18/reg.toml", state="alabama", seed=0)
    head = build_head(recipe.train.reg_head, embed_dim=64, num_classes=1109)
    assert sum(p.numel() for p in head.parameters()) == V18_REG_HEAD_PARAMS


@pytest.mark.equivalence
def test_factory_refuses_an_unknown_hyperparameter() -> None:
    """A dropped hyperparameter is how a model ends up a different size than its recipe claims."""
    from mtlcheck.config import HeadConfig
    from mtlcheck.models.factory import build_head

    with pytest.raises(ValueError, match="does not accept"):
        build_head(HeadConfig(name="next_gru", params={"hiden_dim": 256}),
                   embed_dim=64, num_classes=7)


@pytest.mark.equivalence
def test_e7_forward_matches_under_transplanted_weights(old_repo) -> None:
    """Load the reference's parameters into the new module; the outputs must agree."""
    from mtlcheck.models.gru import CategoryHead

    torch.manual_seed(1234)
    theirs = old_repo["NextHeadGRU"](embed_dim=64, num_classes=7).eval()
    mine = CategoryHead(embed_dim=64, num_classes=7).eval()

    # The two modules were written independently but land on the same state-dict keys, which is
    # itself worth asserting — a silent rename would make the transplant a no-op.
    assert set(mine.state_dict()) == set(theirs.state_dict()), (
        f"state-dict keys differ: only ours {set(mine.state_dict()) - set(theirs.state_dict())}, "
        f"only theirs {set(theirs.state_dict()) - set(mine.state_dict())}"
    )
    mine.load_state_dict(theirs.state_dict())

    x = torch.randn(64, 9, 64)
    with torch.no_grad():
        assert torch.allclose(mine(x), theirs(x), atol=1e-6, rtol=0)


@pytest.mark.equivalence
def test_e7_agrees_under_trailing_padding(old_repo) -> None:
    """With trailing padding the two last-valid-step rules coincide, so outputs still match.

    The new module locates the last valid step by position rather than by count. Under the padding
    layout the reference assumes — strictly trailing — the two are the same index, and this pins
    that they are.
    """
    from mtlcheck.models.gru import CategoryHead

    torch.manual_seed(7)
    theirs = old_repo["NextHeadGRU"](embed_dim=64, num_classes=7).eval()
    mine = CategoryHead(embed_dim=64, num_classes=7).eval()
    mine.load_state_dict(theirs.state_dict())

    x = torch.randn(32, 9, 64)
    x[:, 6:, :] = 0.0                       # trailing padding: last valid step is 5
    with torch.no_grad():
        assert torch.allclose(mine(x), theirs(x), atol=1e-6, rtol=0)


@pytest.mark.equivalence
def test_last_valid_index_is_robust_to_interior_padding() -> None:
    """Where the reference's counting rule is wrong, the new rule is right.

    Unreachable on v18 data (stride-1 windows have no padding), so this changes no number. It is
    here because the counting rule's correctness depends on an invariant nothing verifies, and the
    next windowing change would break it silently.
    """
    from mtlcheck.models.gru import last_valid_index

    x = torch.randn(1, 9, 4)
    x[0, 3, :] = 0.0                        # a hole in the middle; last valid step is still 8
    assert last_valid_index(x).item() == 8

    x[0, 7:, :] = 0.0                       # now the last valid step is 6, with a hole at 3
    assert last_valid_index(x).item() == 6
    # The counting rule would answer 9 - 3 - 1 = 5 here, reading the wrong timestep.
    counted = int((x.abs().sum(dim=-1) != 0).sum(dim=1).item()) - 1
    assert counted == 5 and counted != 6


# ---------------------------------------------------------------- the region head

@pytest.fixture(scope="module")
def old_stan(old_repo):
    from models.next.next_stan_flow.head import NextHeadStanFlow
    return NextHeadStanFlow


@pytest.mark.equivalence
def test_region_head_parameter_count_matches(old_stan) -> None:
    """S12 again — the region path's capacity is the open question about this system."""
    from mtlcheck.models.stan import RegionHead

    mine = RegionHead(embed_dim=64, num_classes=1109)
    theirs = old_stan(embed_dim=64, num_classes=1109, freeze_alpha=True, alpha_init=0.0)

    n_mine = sum(p.numel() for p in mine.parameters())
    # The reference counts alpha as a buffer under freeze_alpha, so parameters exclude it; the
    # [C, C] log_T is also a buffer. Both are absent here by construction (R6).
    n_theirs = sum(p.numel() for p in theirs.parameters())
    assert n_mine == n_theirs, f"parameters: ours {n_mine}, reference {n_theirs}"


@pytest.mark.equivalence
def test_region_head_forward_matches_under_transplant(old_stan) -> None:
    """The reference's own weights, loaded into the port, must produce the same logits.

    Run at v18's configuration (`freeze_alpha=True, alpha_init=0.0`), where the reference's prior
    contributes an exact zero — so the two are computing the same function, and any difference is a
    defect in the backbone port rather than a missing term.
    """
    from mtlcheck.models.stan import RegionHead

    torch.manual_seed(99)
    theirs = old_stan(embed_dim=64, num_classes=1109, freeze_alpha=True, alpha_init=0.0).eval()
    mine = RegionHead(embed_dim=64, num_classes=1109).eval()

    reference_state = {k: v for k, v in theirs.state_dict().items()
                       if not k.startswith(("alpha", "log_T"))}
    assert set(mine.state_dict()) == set(reference_state), (
        f"state-dict keys differ: only ours {set(mine.state_dict()) - set(reference_state)}, "
        f"only theirs {set(reference_state) - set(mine.state_dict())}"
    )
    mine.load_state_dict(reference_state)

    x = torch.randn(48, 9, 64)
    with torch.no_grad():
        assert torch.allclose(mine(x), theirs(x), atol=1e-5, rtol=0)


@pytest.mark.equivalence
def test_region_head_matches_with_trailing_padding(old_stan) -> None:
    """Padded windows exercise the mask path: keys hidden, all-padding rows guarded."""
    from mtlcheck.models.stan import RegionHead

    torch.manual_seed(3)
    theirs = old_stan(embed_dim=64, num_classes=300, freeze_alpha=True, alpha_init=0.0).eval()
    mine = RegionHead(embed_dim=64, num_classes=300).eval()
    mine.load_state_dict({k: v for k, v in theirs.state_dict().items()
                          if not k.startswith(("alpha", "log_T"))})

    x = torch.randn(16, 9, 64)
    x[:8, 5:, :] = 0.0            # trailing padding
    x[8, :, :] = 0.0              # a fully padded row — the NaN guard
    with torch.no_grad():
        ours, ref = mine(x), theirs(x)
    assert torch.isfinite(ours).all(), "the all-padding row produced a non-finite logit"
    assert torch.allclose(ours, ref, atol=1e-5, rtol=0)


@pytest.mark.equivalence
def test_alibi_bias_initialisation_matches(old_stan) -> None:
    """The position-bias prior is part of the model's inductive bias, not an implementation detail."""
    from mtlcheck.models.stan import RegionHead

    mine = RegionHead(embed_dim=64, num_classes=50)
    theirs = old_stan(embed_dim=64, num_classes=50, freeze_alpha=True, alpha_init=0.0)
    assert torch.allclose(mine.stan.trajectory_block.attn.pair_bias,
                          theirs.stan.trajectory_block.attn.pair_bias, atol=0, rtol=0)
