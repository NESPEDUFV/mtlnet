"""Capturing predictions: the sealed evaluation, and the two ways it can lie.

Real runs on synthetic tensors rather than source-text assertions, because the two defects this
covers are both behavioural: rows persisted from a checkpoint the selector did not pick, and a joint
cell persisting two tasks at two epochs — which would describe two virtual models under a headline
that claims one.
"""

from __future__ import annotations

import numpy as np
import pytest

from mtlcheck.config import load_recipe
from mtlcheck.data import dataset, splits
from mtlcheck.device import resolve
from mtlcheck.train import runner

N, WINDOW, DIM = 480, 9, 64


def _inputs(seed: int = 0, n_regions: int = 12) -> dataset.Inputs:
    rng = np.random.default_rng(seed)
    users = np.repeat(np.arange(N // 4), 4).astype(np.int64)
    y_cat = rng.integers(0, 7, N).astype(np.int64)
    y_reg = rng.integers(0, n_regions, N).astype(np.int64)
    # A weak but real signal, so the epoch series moves and the argmax is not an artefact of noise.
    checkin = rng.normal(0, 1, (N, WINDOW, DIM)).astype(np.float32)
    checkin[np.arange(N), 0, y_cat] += 3.0
    region = rng.normal(0, 1, (N, WINDOW, DIM)).astype(np.float32)
    region[np.arange(N), 0, y_reg % DIM] += 3.0
    return dataset.Inputs(
        state="alabama", engine="check2hgi", checkin=checkin, region=region,
        y_category=y_cat, y_region=y_reg,
        last_region=rng.integers(0, n_regions, N).astype(np.int64),
        userid=users, n_categories=7, n_regions=n_regions)


def _ood_inputs(seed: int = 5) -> dataset.Inputs:
    """Region inputs where a quarter of the rows carry a region PRIVATE to one user.

    Without this the two region lanes are the same series: with every region present in training,
    `ood_fraction` is 0 and `top10_acc_indist == top10_acc`, so a test on the fixture above cannot
    tell the selected lane from the diagnostic one.
    """
    rng = np.random.default_rng(seed)
    users = np.repeat(np.arange(N // 4), 4).astype(np.int64)
    shared = rng.integers(0, 20, N)
    private = 20 + users
    y_reg = np.where(rng.random(N) < 0.25, private, shared).astype(np.int64)

    region = rng.normal(0, 1, (N, WINDOW, DIM)).astype(np.float32)
    region[np.arange(N), 0, y_reg % DIM] += 3.0
    return dataset.Inputs(
        state="alabama", engine="check2hgi",
        checkin=rng.normal(0, 1, (N, WINDOW, DIM)).astype(np.float32), region=region,
        y_category=rng.integers(0, 7, N).astype(np.int64), y_region=y_reg,
        last_region=rng.integers(0, 20, N).astype(np.int64),
        userid=users, n_categories=7, n_regions=20 + N // 4)


def _fold(sealed: bool) -> splits.Fold:
    """One fold over user blocks, user-disjoint by construction."""
    users = np.repeat(np.arange(N // 4), 4)
    val = np.flatnonzero(users >= 96)
    inner = np.flatnonzero((users >= 76) & (users < 96)) if sealed else None
    train = np.flatnonzero(users < (76 if sealed else 96))
    return splits.Fold(index=0, train=train, val=val, inner_val=inner)


def _spec():
    return resolve(load_recipe("recipes/v18/cat.toml", state="alabama", seed=0).train.precision,
                   prefer="cpu")


@pytest.mark.parametrize("family,recipe", [("cat", "recipes/v18/cat.toml"),
                                           ("reg", "recipes/v18/reg.toml")])
def test_a_dedicated_cell_persists_rows_from_the_selected_checkpoint(family, recipe) -> None:
    """The cross-check must PASS, not merely exist.

    The region arm is the one that mattered: the runner tracked gated `top10_acc_indist` while the
    selector returned the ungated argmax of raw `top10_acc`, so a region cell aborted whenever the
    two lanes peaked at different epochs — which is most of them. One lane is now frozen for both.
    """
    resolved = load_recipe(recipe, state="alabama", seed=0, epochs=4, batch_size=128)
    fold = _fold(sealed=True)
    result = runner.train_fold(resolved, _inputs(), fold, _spec(), capture_predictions=True)

    assert result.eval_stream == "inner_val", "a sealed fold must score its epochs on the inner split"
    assert result.rows is not None
    assert len(result.rows["y_true"]) == len(fold.val), "rows must cover exactly the outer fold"
    assert set(result.rows.keys()) >= {"y_true", "y_pred", "rank_of_true"}
    assert 1 <= result.selection["epoch"] <= resolved.train.epochs


def test_a_joint_cell_persists_both_tasks_at_one_epoch() -> None:
    """One checkpoint, two tasks, the same epoch — the property the headline claims.

    Persisting each task at its own best would report a pair of virtual models: two epochs, two sets
    of weights, one sentence saying "one model, one forward". It also never happened before this,
    because the joint runner had no capture path at all and the CLI silently dropped the request.
    """
    resolved = load_recipe("recipes/v18/joint.toml", state="alabama", seed=0,
                           epochs=4, batch_size=128)
    fold = _fold(sealed=True)
    result = runner.train_joint_fold(resolved, _inputs(), fold, _spec(), capture_predictions=True)

    assert result.eval_stream == "inner_val"
    assert result.rows is not None and set(result.rows) == {"epoch", "cat", "reg"}
    for task in ("cat", "reg"):
        assert len(result.rows[task]["y_true"]) == len(fold.val)
    assert 1 <= result.rows["epoch"] <= resolved.train.epochs


def test_an_unsealed_fold_is_recorded_as_such_rather_than_refused() -> None:
    """The legacy path still runs — the bridge wave needs it — but it never claims to be sealed."""
    resolved = load_recipe("recipes/v18/cat.toml", state="alabama", seed=0, epochs=3,
                           batch_size=128)
    result = runner.train_fold(resolved, _inputs(), _fold(sealed=False), _spec())
    assert result.eval_stream == "outer_fold"


def test_the_aggregate_refuses_folds_from_two_streams() -> None:
    """Averaging an inner-validation fold with an outer one averages two estimands."""
    resolved = load_recipe("recipes/v18/cat.toml", state="alabama", seed=0, epochs=3,
                           batch_size=128)
    sealed = runner.train_fold(resolved, _inputs(), _fold(sealed=True), _spec())
    legacy = runner.train_fold(resolved, _inputs(), _fold(sealed=False), _spec())

    assert runner.evaluate_folds([sealed])["eval_stream"] == "inner_val"
    with pytest.raises(ValueError, match="different streams"):
        runner.evaluate_folds([sealed, legacy])


def test_the_region_selection_lane_is_the_raw_one_and_the_runner_follows_it() -> None:
    """Frozen: raw `top10_acc` selects, in-distribution stays a diagnostic.

    Raw top-10 is the reported estimand (protocol §1: no train-label bookkeeping exists at
    inference), so it is the lane the persisted checkpoint must be chosen on. Asserted on a series
    where the two lanes peak at DIFFERENT epochs — on a series where they agree, this test would
    pass against either rule.
    """
    from mtlcheck.train import scoring

    series = {
        "top10_acc":        [0.50, 0.62, 0.58, 0.55],     # peaks at epoch 2
        "top10_acc_indist": [0.50, 0.60, 0.70, 0.55],     # peaks at epoch 3
        "ood_fraction":     [0.10, 0.10, 0.10, 0.10],
    }
    chosen = scoring.single_task_best(series, "top10_acc_indist")
    assert chosen["epoch"] == 2 and chosen["metric"] == "top10_acc"
    assert chosen["joint_convention"]["epoch"] == 3, "the diagnostic lane is still reported"

    gated = scoring.single_task_best(series, "top10_acc_indist", min_best_epoch=2)
    assert gated["epoch"] == 3, "min_best_epoch must gate the SELECTED lane, not be ignored"


def test_a_region_cell_with_real_ood_still_captures() -> None:
    """The end-to-end version of the above: the cross-check must survive a divergent-lane run."""
    resolved = load_recipe("recipes/v18/reg.toml", state="alabama", seed=0, epochs=6,
                           batch_size=128)
    fold = _fold(sealed=True)
    result = runner.train_fold(resolved, _ood_inputs(), fold, _spec(), capture_predictions=True)

    ood = result.val["reg"].values["ood_fraction"]
    assert max(ood) > 0, "this fixture must actually hold out regions, or it tests nothing"
    raw = result.val["reg"].values["top10_acc"]
    indist = result.val["reg"].values["top10_acc_indist"]
    assert raw != indist, "with OOD present the two lanes must be different series"
    assert result.rows is not None and len(result.rows["y_true"]) == len(fold.val)
    assert result.selection["epoch"] == int(np.argmax(raw)) + 1


def test_the_joint_capture_cross_checks_its_epoch_against_the_scorer() -> None:
    """The dedicated path had this guard and the joint one did not.

    Under the legacy `joint_f1_mean` selector the tracker and `standard_scores` read different
    inputs — the tracker omitted `reg_f1` — and diverged on half of a 2 000-trial fuzz. The rows
    would then come from one epoch while result.json reported another, both plausible, neither
    naming the other. Exercised on the legacy selector, since geom_simple ignores the field.
    """
    resolved = load_recipe("recipes/v18/joint.toml", state="alabama", seed=0, epochs=5,
                           batch_size=128, selector="joint_f1_mean")
    result = runner.train_joint_fold(resolved, _inputs(), _fold(sealed=True), _spec(),
                                     capture_predictions=True)
    assert result.rows["epoch"] == result.selection["joint_best"]["epoch"]


def test_the_probe_does_not_perturb_training() -> None:
    """Probe-on must produce the SAME model as probe-off.

    The sidecar runs an extra forward, which would otherwise consume the training stream's dropout
    draws and shift every subsequent mask — so the probe would silently change the run it measures.
    `fork_rng` is what prevents that, and this is the test that would fail without it.
    """
    common = dict(state="alabama", seed=0, epochs=3, batch_size=128, diagnostics=True)
    # grad_geometry=False EXPLICITLY. Omitting it used to resolve to the default, which after the
    # 2026-08-18 flip is True — so the test compared probe-on against probe-on and passed even with
    # fork_rng neutered to a nullcontext. A neutrality test whose two arms are identical is not one.
    off = runner.train_joint_fold(
        load_recipe("recipes/v18/joint.toml", **common, grad_geometry=False),
        _inputs(), _fold(sealed=True), _spec())
    on = runner.train_joint_fold(
        load_recipe("recipes/v18/joint.toml", **common, grad_geometry=True),
        _inputs(), _fold(sealed=True), _spec())

    assert off.diagnostics["execution"]["probe"] == "off"
    assert on.diagnostics["execution"]["probe"] == "eager_sidecar", "the arms must actually differ"
    assert on.diagnostics["grad_cosine_mean"] == on.diagnostics["grad_cosine_mean"]  # not NaN
    assert on.train_loss == off.train_loss, "the probe changed the training trajectory"
    assert on.selection["joint_best"] == off.selection["joint_best"]


def test_the_sidecar_measures_the_in_graph_quantity() -> None:
    """With dropout off, the sidecar's own forward is the training forward — same number, exactly.

    That equality is the whole argument for one forward rather than two: under dropout the two
    gradients must share their masks, and a design that gave each task its own forward would
    attenuate the cosine toward zero — biasing a probe toward the very conclusion it is used to
    support. Here dropout is disabled so the comparison isolates the graph, not the masks.
    """
    import torch

    from mtlcheck.models.joint import JointModel
    from mtlcheck.train import diagnostics as diag

    torch.manual_seed(0)
    model = JointModel(feature_size=DIM, n_categories=7, n_regions=12,
                       trunk_dropout=0.0, encoder_dropout=0.0).eval()
    shared = list(model.shared_parameters())
    x_cat = torch.randn(64, WINDOW, DIM)
    x_reg = torch.randn(64, WINDOW, DIM)
    y_cat = torch.randint(0, 7, (64,))
    y_reg = torch.randint(0, 12, (64,))
    criterion = torch.nn.CrossEntropyLoss()

    cat_logits, reg_logits = model(x_cat, x_reg)
    in_graph = diag.gradient_geometry(criterion(cat_logits, y_cat),
                                      criterion(reg_logits, y_reg), shared)

    import contextlib
    sidecar = diag.gradient_geometry_sidecar(
        model, ((x_cat, y_cat, None), (x_reg, y_reg, None)), criterion, criterion,
        contextlib.nullcontext, shared, torch.device("cpu"))

    assert sidecar == pytest.approx(in_graph, abs=1e-9)


def test_the_probe_decomposes_the_trunk_by_group() -> None:
    """A single scalar can average a conflicted block against an orthogonal one.

    It also cannot answer the structural question: `cross_ab`/`ffn_a` update the category side of
    the trunk and `cross_ba`/`ffn_b` the region side, so a "shared" trunk whose halves each serve
    one task is two private half-trunks sharing an address. Only per-group norms show that.
    """
    resolved = load_recipe("recipes/v18/joint.toml", state="alabama", seed=0, epochs=3,
                           batch_size=128, diagnostics=True, grad_geometry=True)
    result = runner.train_joint_fold(resolved, _inputs(), _fold(sealed=True), _spec())

    groups = result.diagnostics["grad_by_group"]
    assert set(groups) == {"cross_ab", "cross_ba", "ffn_a", "ffn_b", "norms", "final_ln"}
    for name, stats in groups.items():
        assert {"cosine_mean", "cosine_std", "negative_fraction", "n_params"} <= set(stats)
        if stats["cosine_mean"] is not None:
            assert -1.0001 <= stats["cosine_mean"] <= 1.0001, f"{name} cosine out of range"

    # final_ln merges cat_final_ln and reg_final_ln, whose supports are DISJOINT — neither loss
    # reaches the other's parameters. Its cosine is 0 by construction, not by measurement, so it
    # would have been the most orthogonal group in every run, at the group whose name most invites
    # "even the shared output norms are orthogonal". None, not 0.
    assert groups["final_ln"]["cosine_mean"] is None
    assert groups["final_ln"]["norm_cat_mean"] > 0 and groups["final_ln"]["norm_reg_mean"] > 0
    assert groups["cross_ab"]["cosine_mean"] is not None, "a genuinely shared group still reports"

    # The decomposition costs no extra backward: it reuses the two gradient lists the scalar used.
    import inspect

    from mtlcheck.train import diagnostics as diag
    source = inspect.getsource(diag.gradient_geometry)
    assert source.count("torch.autograd.grad") == 2, "the decomposition must not add a backward"
