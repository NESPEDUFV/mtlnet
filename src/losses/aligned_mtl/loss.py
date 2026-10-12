"""Aligned-MTL: Independent Component Alignment for Multi-Task Learning.

Reference:
    Senushkin et al., "Independent Component Alignment for Multi-Task
    Learning", CVPR 2023. https://arxiv.org/abs/2305.19000

Adapted from the LibMTL integration:
    https://github.com/median-research-group/LibMTL
"""

from __future__ import annotations

from typing import Dict, List, Tuple, Union

import torch

from losses._common import as_parameter_list, flatten_task_grads


class AlignedMTLLoss:
    """Aligned-MTL: aligns principal components of the gradient matrix.

    Makes aligned gradients orthogonal and of equal magnitude via
    eigendecomposition of the Gram matrix. For n_tasks=2 the
    eigendecomposition is on a 2x2 matrix (negligible cost).
    """

    def __init__(
        self,
        n_tasks: int,
        device: torch.device,
    ):
        self.n_tasks = n_tasks
        self.device = device

    def get_weighted_loss(
        self,
        losses: torch.Tensor,
        shared_parameters=None,
        **kwargs,
    ) -> Tuple[torch.Tensor, Dict]:
        raise NotImplementedError(
            "Aligned-MTL manipulates gradients directly; use backward()."
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
        G = torch.stack(grads, dim=0)  # [n_tasks, D]

        # Gram matrix M = G G^T (n_tasks x n_tasks).
        M = G @ G.t()

        # Eigendecomposition (M is symmetric positive semi-definite).
        lmbda, V = torch.linalg.eigh(M)

        # Filter by numerical tolerance (condition number check).
        tol = lmbda.max() * max(M.shape) * torch.finfo(M.dtype).eps
        rank_mask = lmbda > tol

        if rank_mask.sum() == 0:
            # Degenerate: all eigenvalues below tolerance.
            losses.sum().backward()
            return None, {"weights": torch.ones(self.n_tasks, device=self.device)}

        # Keep only significant eigenvalues.
        lmbda_r = lmbda[rank_mask]
        V_r = V[:, rank_mask]

        # Alignment: rescale so all singular values equal the minimum.
        # sigma_inv = diag(1 / sqrt(lmbda_r))
        # sigma_min = diag(sqrt(lmbda_r.min()))
        # B = V_r @ sigma_inv @ sigma_min @ V_r^T
        # alpha = B @ ones
        sigma_inv = torch.diag(1.0 / lmbda_r.sqrt())
        sigma_min_val = lmbda_r.min().sqrt()
        B = V_r @ sigma_inv @ V_r.t() * sigma_min_val

        alpha = B.sum(dim=1)  # [n_tasks]

        # Clamp negative weights (can happen with numerical noise).
        alpha = alpha.clamp(min=0.0)
        alpha_sum = alpha.sum().clamp(min=1e-12)
        alpha = alpha / alpha_sum * self.n_tasks

        # Combine gradients: g_aligned = sum_i alpha_i * g_i.
        g_aligned = alpha @ G  # [D]

        # Set gradients on shared parameters.
        offset = 0
        for p in params:
            numel = p.numel()
            p.grad = g_aligned[offset:offset + numel].view_as(p).clone()
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

        return None, {"weights": alpha.detach()}

    def __call__(self, losses: torch.Tensor, **kwargs):
        return self.backward(losses, **kwargs)

    def parameters(self) -> List[torch.Tensor]:
        return []


__all__ = ["AlignedMTLLoss"]
