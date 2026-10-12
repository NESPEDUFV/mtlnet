"""Shared gradient utilities for multitask loss weighting variants."""

from __future__ import annotations

from typing import List, Tuple, Union

import torch


def as_parameter_list(
    parameters: Union[
        List[torch.nn.Parameter],
        Tuple[torch.nn.Parameter, ...],
        torch.Tensor,
        None,
    ],
) -> list[torch.nn.Parameter]:
    """Normalize parameter inputs into a concrete list."""
    if parameters is None:
        return []
    if isinstance(parameters, torch.Tensor):
        return [parameters]
    return [param for param in parameters if param is not None]


def flatten_task_grads(
    grads: tuple[torch.Tensor | None, ...],
    parameters: list[torch.nn.Parameter],
) -> torch.Tensor:
    """Flatten gradient tuple into one vector, filling missing grads with zeros."""
    chunks = []
    for grad, param in zip(grads, parameters):
        if grad is None:
            chunks.append(torch.zeros_like(param).reshape(-1))
        else:
            chunks.append(grad.reshape(-1))
    if not chunks:
        if parameters:
            return torch.empty(0, device=parameters[0].device)
        return torch.empty(0)
    return torch.cat(chunks, dim=0)


def compute_task_gradients(
    losses: torch.Tensor,
    shared_parameters: Union[
        List[torch.nn.Parameter],
        Tuple[torch.nn.Parameter, ...],
        torch.Tensor,
        None,
    ],
) -> torch.Tensor:
    """Compute per-task gradients over a shared-parameter set."""
    parameters = as_parameter_list(shared_parameters)
    if not parameters:
        return torch.empty(losses.shape[0], 0, device=losses.device, dtype=losses.dtype)

    gradients = []
    for loss in losses:
        task_grads = torch.autograd.grad(
            loss,
            parameters,
            retain_graph=True,
            allow_unused=True,
        )
        gradients.append(flatten_task_grads(task_grads, parameters))
    return torch.stack(gradients, dim=0)

