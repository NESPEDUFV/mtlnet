"""Conflict-Averse Gradient Descent (CAGrad) for multi-task learning.

Reference:
    Liu et al., "Conflict-Averse Gradient Descent for Multi-task Learning",
    NeurIPS 2021. https://arxiv.org/abs/2110.14048

Adapted from the official implementation:
    https://github.com/Cranial-XIX/CAGrad
and LibMTL integration:
    https://github.com/median-research-group/LibMTL
"""

from __future__ import annotations

from typing import Dict, List, Tuple, Union

import numpy as np
import torch
from scipy.optimize import minimize

from losses._common import as_parameter_list, compute_task_gradients, flatten_task_grads


class CAGradLoss:
    """CAGrad: maximizes worst local improvement within a conflict-averse ball.

    For n_tasks=2 the subproblem is a scalar optimization (fast).
    """

    def __init__(
        self,
        n_tasks: int,
        device: torch.device,
        c: float = 0.4,
        rescale: int = 1,
    ):
        if c < 0:
            raise ValueError(f"c must be >= 0, got {c}")
        if rescale not in (0, 1, 2):
            raise ValueError(f"rescale must be 0, 1, or 2, got {rescale}")
        self.n_tasks = n_tasks
        self.device = device
        self.c = float(c)
        self.rescale = int(rescale)

    def get_weighted_loss(
        self,
        losses: torch.Tensor,
        shared_parameters=None,
        **kwargs,
    ) -> Tuple[torch.Tensor, Dict]:
        raise NotImplementedError(
            "CAGrad manipulates gradients directly; use backward()."
        )

    def backward(
        self,
        losses: torch.Tensor,
        shared_parameters=None,
        task_specific_parameters=None,
        **kwargs,
    ) -> Tuple[Union[torch.Tensor, None], Union[Dict, None]]:
        params = as_parameter_list(shared_parameters)
        if not params:
            loss = losses.sum()
            loss.backward()
            return loss, {"weights": torch.ones(self.n_tasks, device=self.device)}

        # Compute per-task gradients over shared parameters.
        grads = []
        for i in range(self.n_tasks):
            task_grads = torch.autograd.grad(
                losses[i], params, retain_graph=True, allow_unused=True,
            )
            grads.append(flatten_task_grads(task_grads, params))
        grads = torch.stack(grads, dim=0)  # [n_tasks, D]

        # Average gradient.
        g_bar = grads.mean(dim=0)  # [D]
        g_bar_norm = g_bar.norm()

        if g_bar_norm < 1e-12:
            # Degenerate case: average gradient is zero.
            losses.sum().backward()
            return None, {"weights": torch.ones(self.n_tasks, device=self.device)}

        # Gram matrix for the optimization subproblem.
        GG = grads @ grads.t()  # [n_tasks, n_tasks]
        GG_np = GG.detach().cpu().numpy()
        g_bar_norm_np = g_bar_norm.detach().cpu().item()

        # Solve for w that maximizes the worst local improvement
        # within a ball of radius c * ||g_bar||.
        n = self.n_tasks
        w_init = np.ones(n) / n

        def _objective(w):
            # Minimize negative of (minimum task improvement).
            gw = w @ GG_np  # weighted gradient dot products
            # g_bar_dot_gw = sum of w_i * (g_bar . g_i) = g_bar . (sum w_i g_i)
            g_bar_dot = GG_np.mean(axis=0)  # [n_tasks], g_bar . g_i for each i
            lmbda_opt = gw @ w  # ||sum w_i g_i||^2
            return lmbda_opt  # quadratic form

        def _cagrad_objective(w):
            # CAGrad objective: find w in simplex such that
            # g_bar + c * ||g_bar|| * (G^T w / ||G^T w||) maximizes
            # min_i g_i^T d.
            Gw = GG_np @ w
            Gw_norm = np.sqrt(np.maximum(w @ Gw, 1e-20))
            # Improvement for each task:
            # g_i^T (g_bar + c * ||g_bar|| * G^T w / ||G^T w||)
            g_bar_dot_gi = GG_np.mean(axis=0)
            improvements = g_bar_dot_gi + self.c * g_bar_norm_np * (Gw / Gw_norm)
            return -np.min(improvements)

        constraints = {"type": "eq", "fun": lambda w: w.sum() - 1.0}
        bounds = [(0.0, 1.0)] * n

        result = minimize(
            _cagrad_objective,
            w_init,
            method="SLSQP",
            bounds=bounds,
            constraints=constraints,
            options={"maxiter": 50, "ftol": 1e-10},
        )
        w_opt = torch.from_numpy(result.x).to(dtype=grads.dtype, device=grads.device)

        # Compute the CAGrad direction: g_bar + c * ||g_bar|| * (G^T w / ||G^T w||).
        Gw = grads.t() @ w_opt  # [D]
        Gw_norm = Gw.norm().clamp_min(1e-12)
        g_cagrad = g_bar + self.c * g_bar_norm * (Gw / Gw_norm)

        # Apply rescaling.
        if self.rescale == 1:
            g_cagrad = g_cagrad / (1.0 + self.c ** 2)
        elif self.rescale == 2:
            g_cagrad = g_cagrad / (1.0 + self.c)

        # Set gradients on shared parameters.
        offset = 0
        for p in params:
            numel = p.numel()
            p.grad = g_cagrad[offset:offset + numel].view_as(p).clone()
            offset += numel

        # Set gradients on task-specific parameters via sum of losses.
        ts_params = as_parameter_list(task_specific_parameters)
        if ts_params:
            ts_grads = torch.autograd.grad(
                losses.sum(), ts_params, allow_unused=True,
            )
            for p, g in zip(ts_params, ts_grads):
                if g is not None:
                    p.grad = g

        return None, {"weights": w_opt.detach()}

    def __call__(self, losses: torch.Tensor, **kwargs):
        return self.backward(losses, **kwargs)

    def parameters(self) -> List[torch.Tensor]:
        return []


__all__ = ["CAGradLoss"]
