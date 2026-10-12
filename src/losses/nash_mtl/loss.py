import copy
import logging
import random
from typing import Dict, List, Tuple, Union
from abc import abstractmethod
import numpy as np
import torch
import cvxpy as cp

logger = logging.getLogger(__name__)

class WeightMethod:
    def __init__(self, n_tasks: int, device: torch.device):
        super().__init__()
        self.n_tasks = n_tasks
        self.device = device

    @abstractmethod
    def get_weighted_loss(
        self,
        losses: torch.Tensor,
        shared_parameters: Union[List[torch.nn.parameter.Parameter], torch.Tensor],
        task_specific_parameters: Union[
            List[torch.nn.parameter.Parameter], torch.Tensor
        ],
        last_shared_parameters: Union[List[torch.nn.parameter.Parameter], torch.Tensor],
        representation: Union[torch.nn.parameter.Parameter, torch.Tensor],
        **kwargs,
    ):
        pass

    def backward(
        self,
        losses: torch.Tensor,
        shared_parameters: Union[
            List[torch.nn.parameter.Parameter], torch.Tensor
        ] = None,
        task_specific_parameters: Union[
            List[torch.nn.parameter.Parameter], torch.Tensor
        ] = None,
        last_shared_parameters: Union[
            List[torch.nn.parameter.Parameter], torch.Tensor
        ] = None,
        representation: Union[List[torch.nn.parameter.Parameter], torch.Tensor] = None,
        **kwargs,
    ) -> Tuple[Union[torch.Tensor, None], Union[dict, None]]:
        """

        Parameters
        ----------
        losses :
        shared_parameters :
        task_specific_parameters :
        last_shared_parameters : parameters of last shared layer/block
        representation : shared representation
        kwargs :

        Returns
        -------
        Loss, extra outputs
        """
        loss, extra_outputs = self.get_weighted_loss(
            losses=losses,
            shared_parameters=shared_parameters,
            task_specific_parameters=task_specific_parameters,
            last_shared_parameters=last_shared_parameters,
            representation=representation,
            **kwargs,
        )
        loss.backward()
        return loss, extra_outputs

    def __call__(
        self,
        losses: torch.Tensor,
        shared_parameters: Union[
            List[torch.nn.parameter.Parameter], torch.Tensor
        ] = None,
        task_specific_parameters: Union[
            List[torch.nn.parameter.Parameter], torch.Tensor
        ] = None,
        **kwargs,
    ):
        return self.backward(
            losses=losses,
            shared_parameters=shared_parameters,
            task_specific_parameters=task_specific_parameters,
            **kwargs,
        )

    def parameters(self) -> List[torch.Tensor]:
        """return learnable parameters"""
        return []

_NASH_SOLVER_FALLBACK = ("ECOS", "SCS")


class NashMTL(WeightMethod):
    def __init__(
        self,
        n_tasks: int,
        device: torch.device,
        max_norm: float = 1.0,
        update_weights_every: int = 1,
        optim_niter=20,
    ):
        super(NashMTL, self).__init__(
            n_tasks=n_tasks,
            device=device,
        )

        self.optim_niter = optim_niter
        self.update_weights_every = update_weights_every
        self.max_norm = max_norm

        self.prvs_alpha_param = None
        self.normalization_factor = np.ones((1,))
        self.init_gtg = self.init_gtg = np.eye(self.n_tasks)
        self.step = 0.0
        self.prvs_alpha = np.ones(self.n_tasks, dtype=np.float32)
        self.solver_failures = 0

        # Pick the solver once, fail loudly at construction time if none of
        # the supported solvers are available. The original upstream code
        # hard-codes ECOS inside a bare `except:`, which means a missing
        # `ecos` package degrades NashMTL into fixed [1,1] weights without
        # any warning. Detect that here.
        installed = set(cp.installed_solvers())
        for candidate in _NASH_SOLVER_FALLBACK:
            if candidate in installed:
                self._solver = candidate
                break
        else:
            raise RuntimeError(
                "NashMTL requires one of the cvxpy solvers "
                f"{_NASH_SOLVER_FALLBACK}, but none are installed. "
                f"Installed: {sorted(installed)}. "
                "Install ECOS with `pip install ecos`."
            )
        if self._solver != "ECOS":
            logger.warning(
                "NashMTL: ECOS not installed, falling back to %s. "
                "Results may differ slightly from the paper.",
                self._solver,
            )
        self._solver_failures = 0

    def _stop_criteria(self, gtg, alpha_t):
        return (
            (self.alpha_param.value is None)
            or (np.linalg.norm(gtg @ alpha_t - 1 / (alpha_t + 1e-10)) < 1e-3)
            or (
                np.linalg.norm(self.alpha_param.value - self.prvs_alpha_param.value)
                < 1e-6
            )
        )

    def solve_optimization(self, gtg: np.array):
        self.G_param.value = gtg
        self.normalization_factor_param.value = self.normalization_factor

        alpha_t = self.prvs_alpha
        for _ in range(self.optim_niter):
            # cvxpy declares alpha_param with nonneg=True. ECOS/SCS solvers
            # can return slightly-negative values or NaN due to numerical
            # precision on optimal_inaccurate solutions; also alpha_t can
            # be None after a SolverError branch. Normalise before the
            # validated assignment to avoid ValueError("Variable value
            # must be nonnegative").
            if alpha_t is None or not np.all(np.isfinite(alpha_t)):
                alpha_t = np.ones_like(self.prvs_alpha)
            alpha_t = np.maximum(np.asarray(alpha_t, dtype=np.float64), 1e-6)
            self.alpha_param.value = alpha_t
            self.prvs_alpha_param.value = alpha_t

            try:
                solve_kwargs = {"solver": self._solver, "warm_start": True}
                if self._solver == "ECOS":
                    solve_kwargs["max_iters"] = 100
                elif self._solver == "SCS":
                    solve_kwargs["max_iters"] = 2500
                self.prob.solve(**solve_kwargs)
            except cp.error.SolverError as exc:
                # Don't silently swallow — this is the failure mode that used
                # to collapse Nash-MTL to constant [1,1] weights. Log once
                # then keep the warm-start value as a last resort.
                if self._solver_failures == 0:
                    logger.error(
                        "NashMTL solver %s raised SolverError on step %s: %s. "
                        "Alpha will fall back to the warm-start value, which "
                        "degrades Nash-MTL to fixed task weights.",
                        self._solver, self.step, exc,
                    )
                self._solver_failures += 1
                self.alpha_param.value = self.prvs_alpha_param.value

            if self._stop_criteria(gtg, alpha_t):
                break

            alpha_t = self.alpha_param.value

        # Defensive: cvxpy can return slightly inaccurate solutions
        # ("optimal_inaccurate") and on rare degenerate Gram matrices that
        # leak NaN/Inf into alpha_t. Reject those silently and fall back to
        # the previous alpha so a single bad step can't poison the
        # weighted-loss multiplication and the optimizer state.
        if alpha_t is not None and np.all(np.isfinite(alpha_t)):
            self.prvs_alpha = alpha_t
        elif alpha_t is not None:
            if self._solver_failures == 0:
                logger.error(
                    "NashMTL solver %s returned non-finite alpha=%s on step %s; "
                    "keeping previous alpha=%s.",
                    self._solver, alpha_t, self.step, self.prvs_alpha,
                )
            self._solver_failures += 1

        return self.prvs_alpha

    def _calc_phi_alpha_linearization(self):
        G_prvs_alpha = self.G_param @ self.prvs_alpha_param
        prvs_phi_tag = 1 / self.prvs_alpha_param + (1 / G_prvs_alpha) @ self.G_param
        phi_alpha = prvs_phi_tag @ (self.alpha_param - self.prvs_alpha_param)
        return phi_alpha

    def _init_optim_problem(self):
        self.alpha_param = cp.Variable(shape=(self.n_tasks,), nonneg=True)
        self.prvs_alpha_param = cp.Parameter(
            shape=(self.n_tasks,), value=self.prvs_alpha
        )
        self.G_param = cp.Parameter(
            shape=(self.n_tasks, self.n_tasks), value=self.init_gtg
        )
        self.normalization_factor_param = cp.Parameter(
            shape=(1,), value=np.array([1.0])
        )

        self.phi_alpha = self._calc_phi_alpha_linearization()

        G_alpha = self.G_param @ self.alpha_param
        constraint = []
        for i in range(self.n_tasks):
            constraint.append(
                -cp.log(self.alpha_param[i] * self.normalization_factor_param)
                - cp.log(G_alpha[i])
                <= 0
            )
        obj = cp.Minimize(
            cp.sum(G_alpha) + self.phi_alpha / self.normalization_factor_param
        )
        self.prob = cp.Problem(obj, constraint)

    def get_weighted_loss(
        self,
        losses,
        shared_parameters,
        **kwargs,
    ):
        """

        Parameters
        ----------
        losses :
        shared_parameters : shared parameters
        kwargs :

        Returns
        -------

        """

        extra_outputs = dict()
        if self.step == 0:
            self._init_optim_problem()

        if (self.step % self.update_weights_every) == 0:
            self.step += 1

            grads = {}
            for i, loss in enumerate(losses):
                g = list(
                    torch.autograd.grad(
                        loss,
                        shared_parameters,
                        retain_graph=True,
                    )
                )
                grad = torch.cat([torch.flatten(grad) for grad in g])
                grads[i] = grad

            G = torch.stack(tuple(v for v in grads.values()))
            GTG = torch.mm(G, G.t())

            # Compute the norm and divide on-device. Only sync to CPU once
            # for the cvxpy/ECOS solver, which has to run on the host.
            norm = torch.norm(GTG).detach()
            GTG_norm = GTG / norm
            self.normalization_factor = norm.cpu().numpy().reshape((1,))
            alpha_np = self.solve_optimization(GTG_norm.detach().cpu().numpy())
            # Move alpha onto the same device/dtype as the losses so the
            # weighted-loss multiplication works on MPS (which doesn't
            # support float64) and CUDA (which can't mix devices).
            alpha = torch.as_tensor(
                alpha_np, dtype=losses.dtype, device=losses.device
            )

        else:
            self.step += 1
            alpha = torch.as_tensor(
                self.prvs_alpha, dtype=losses.dtype, device=losses.device)

        weighted_loss = sum([losses[i] * alpha[i] for i in range(len(alpha))])
        extra_outputs["weights"] = alpha
        return weighted_loss, extra_outputs

    def backward(
        self,
        losses: torch.Tensor,
        shared_parameters: Union[
            List[torch.nn.parameter.Parameter], torch.Tensor
        ] = None,
        task_specific_parameters: Union[
            List[torch.nn.parameter.Parameter], torch.Tensor
        ] = None,
        last_shared_parameters: Union[
            List[torch.nn.parameter.Parameter], torch.Tensor
        ] = None,
        representation: Union[List[torch.nn.parameter.Parameter], torch.Tensor] = None,
        **kwargs,
    ) -> Tuple[Union[torch.Tensor, None], Union[Dict, None]]:
        loss, extra_outputs = self.get_weighted_loss(
            losses=losses,
            shared_parameters=shared_parameters,
            **kwargs,
        )
        loss.backward()

        # make sure the solution for shared params has norm <= self.eps
        if self.max_norm > 0:
            torch.nn.utils.clip_grad_norm_(shared_parameters, self.max_norm)

        return loss, extra_outputs
