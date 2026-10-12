"""Tests for NashMTL loss function.

These tests guard against the regression where Nash-MTL silently degrades
to fixed [1, 1] task weights when its cvxpy solver (ECOS) is missing or
otherwise raises a SolverError. See solve_optimization() in nash_mtl.py.
"""

import numpy as np
import pytest
import torch
import torch.nn as nn

from losses.nash_mtl import NashMTL


def _make_two_task_problem(seed: int = 0):
    """Tiny shared-trunk + 2-head regression problem."""
    torch.manual_seed(seed)
    shared = nn.Linear(4, 4)
    head1 = nn.Linear(4, 1)
    head2 = nn.Linear(4, 1)
    x = torch.randn(8, 4)
    y1 = torch.randn(8, 1)
    y2 = torch.randn(8, 1)
    return shared, head1, head2, x, y1, y2


def _losses(shared, head1, head2, x, y1, y2, scale2: float = 1.0):
    s = shared(x)
    p1 = head1(s)
    p2 = head2(s)
    l1 = ((p1 - y1) ** 2).mean()
    l2 = scale2 * ((p2 - y2) ** 2).mean()
    return torch.stack([l1, l2])


class TestNashMTL:
    def test_initialization_picks_a_solver(self):
        nash = NashMTL(n_tasks=2, device=torch.device("cpu"))
        assert nash._solver in ("ECOS", "SCS")
        assert nash.n_tasks == 2
        assert np.allclose(nash.prvs_alpha, np.ones(2))

    def test_solve_optimization_actually_changes_alpha(self):
        """Regression: ECOS missing used to leave alpha == [1, 1] forever."""
        nash = NashMTL(n_tasks=2, device=torch.device("cpu"),
                       update_weights_every=1, optim_niter=20)
        nash._init_optim_problem()

        # Strongly imbalanced gradient Gram matrix → solver MUST move alpha
        # away from the warm-start [1, 1].
        gtg = np.array([[0.27, 0.08], [0.08, 0.95]], dtype=np.float64)
        nash.normalization_factor = np.array([2.69])
        alpha = nash.solve_optimization(gtg)

        assert alpha is not None, "solve_optimization returned None"
        assert not np.allclose(alpha, np.ones(2)), (
            "Nash-MTL alpha is stuck at [1, 1] — solver likely failed silently"
        )
        # Task 1 has lower diagonal → should get higher weight
        assert alpha[0] > alpha[1], f"unexpected alpha ordering: {alpha}"
        assert nash._solver_failures == 0

    def test_backward_updates_alpha_across_steps(self):
        shared, head1, head2, x, y1, y2 = _make_two_task_problem()
        nash = NashMTL(n_tasks=2, device=torch.device("cpu"),
                       max_norm=0, update_weights_every=1, optim_niter=20)
        opt = torch.optim.SGD(
            list(shared.parameters())
            + list(head1.parameters())
            + list(head2.parameters()),
            lr=0.01,
        )

        seen_alphas = []
        for _ in range(4):
            opt.zero_grad()
            losses = _losses(shared, head1, head2, x, y1, y2, scale2=4.0)
            _, extras = nash.backward(
                losses=losses,
                shared_parameters=list(shared.parameters()),
                task_specific_parameters=list(head1.parameters())
                + list(head2.parameters()),
            )
            opt.step()
            alpha = np.asarray(extras["weights"], dtype=np.float64)
            seen_alphas.append(alpha)

        seen_alphas = np.stack(seen_alphas)
        # No collapse to constant [1, 1]
        assert not np.allclose(seen_alphas, 1.0), (
            f"alpha never moved from [1,1]:\n{seen_alphas}"
        )
        # Solver shouldn't be falling back constantly
        assert nash._solver_failures == 0

    def test_update_weights_every_skips_solve(self):
        """When step % update_weights_every != 0, alpha is reused unchanged."""
        shared, head1, head2, x, y1, y2 = _make_two_task_problem()
        nash = NashMTL(n_tasks=2, device=torch.device("cpu"),
                       max_norm=0, update_weights_every=4, optim_niter=20)
        sp = list(shared.parameters())
        tp = list(head1.parameters()) + list(head2.parameters())

        # Step 0 → solve. Steps 1-3 → reuse.
        alphas = []
        for _ in range(5):
            losses = _losses(shared, head1, head2, x, y1, y2, scale2=4.0)
            _, extras = nash.backward(
                losses=losses, shared_parameters=sp, task_specific_parameters=tp
            )
            alphas.append(np.asarray(extras["weights"], dtype=np.float64).copy())
            shared.zero_grad(); head1.zero_grad(); head2.zero_grad()

        # alphas[1] == alphas[2] == alphas[3] (cached); alphas[4] is a fresh solve
        assert np.allclose(alphas[1], alphas[2])
        assert np.allclose(alphas[2], alphas[3])

    def test_grad_clipping_respects_max_norm(self):
        shared, head1, head2, x, y1, y2 = _make_two_task_problem()
        nash = NashMTL(n_tasks=2, device=torch.device("cpu"),
                       max_norm=0.1, update_weights_every=1, optim_niter=20)

        losses = _losses(shared, head1, head2, x, y1, y2, scale2=100.0)
        nash.backward(
            losses=losses,
            shared_parameters=list(shared.parameters()),
            task_specific_parameters=list(head1.parameters())
            + list(head2.parameters()),
        )
        total_sq = sum(
            p.grad.detach().pow(2).sum().item()
            for p in shared.parameters() if p.grad is not None
        )
        assert total_sq ** 0.5 <= 0.1 + 1e-5

    def test_extras_weights_match_prvs_alpha(self):
        shared, head1, head2, x, y1, y2 = _make_two_task_problem()
        nash = NashMTL(n_tasks=2, device=torch.device("cpu"),
                       max_norm=0, update_weights_every=1, optim_niter=20)
        losses = _losses(shared, head1, head2, x, y1, y2, scale2=2.0)
        _, extras = nash.backward(
            losses=losses,
            shared_parameters=list(shared.parameters()),
            task_specific_parameters=list(head1.parameters())
            + list(head2.parameters()),
        )
        assert np.allclose(
            np.asarray(extras["weights"], dtype=np.float64),
            np.asarray(nash.prvs_alpha, dtype=np.float64),
        )

    def test_solve_optimization_rejects_nan_alpha(self):
        """If the cvxpy solver leaves non-finite alpha, prvs_alpha is preserved."""
        # optim_niter=1 so the loop runs exactly one iteration: solve poisons
        # alpha_param._value to NaN, alpha_t = self.alpha_param.value picks
        # the NaN up, and the loop exits naturally. Then the guard at the
        # end of solve_optimization should reject it and keep prvs_alpha.
        nash = NashMTL(n_tasks=2, device=torch.device("cpu"),
                       update_weights_every=1, optim_niter=1)
        nash._init_optim_problem()
        # Seed a known-good prvs_alpha by running one real solve first.
        nash.solve_optimization(
            np.array([[0.27, 0.08], [0.08, 0.95]], dtype=np.float64)
        )
        good_alpha = nash.prvs_alpha.copy()
        failures_before = nash._solver_failures

        # cvxpy's public setter validates `nonneg=True` and would reject NaN,
        # so write directly into the private _value slot — that's exactly the
        # failure mode the guard is meant to catch (cvxpy returning a
        # degenerate solution that propagates non-finite values).
        def poisoned_solve(**kwargs):
            nash.alpha_param._value = np.array([np.nan, np.nan])

        nash.prob.solve = poisoned_solve

        # Use a *different* gtg for the second solve so the stop-criterion's
        # "is alpha_t already a Nash equilibrium for this gtg" check returns
        # False and the loop body actually runs to the alpha_t reassignment.
        result = nash.solve_optimization(
            np.array([[0.95, 0.04], [0.04, 0.31]], dtype=np.float64)
        )
        # Guard must reject the NaN and keep the previous good alpha.
        assert np.all(np.isfinite(result)), f"alpha leaked NaN: {result}"
        assert np.allclose(result, good_alpha)
        assert nash._solver_failures > failures_before
