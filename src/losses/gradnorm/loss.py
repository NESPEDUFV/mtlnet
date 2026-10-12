"""GradNorm: Gradient Normalization for Adaptive Loss Balancing.

Reference: Chen et al., ICML 2018 (https://arxiv.org/abs/1711.02257)
Verified against: LibMTL (https://github.com/median-research-group/LibMTL/blob/main/LibMTL/weighting/GradNorm.py)

Algorithm (per-step):
  Given: task losses L_i, shared parameters W, task weights w_i > 0

  1.  G_i  = w_i * ||∇_W L_i||          (weighted grad norm for task i)
  2.  Ḡ    = mean(G_i)
  3.  r̃_i  = (L_i(t)/L_i(0)) / mean_j(L_j(t)/L_j(0))   (relative training rate)
  4.  T_i  = Ḡ · r̃_i^α                  (target gradient norm)
  5.  L_gn = Σ_i |G_i - T_i|            (GradNorm auxiliary loss)
  6.  ∂L_gn/∂scale_j computed analytically (no create_graph — fast on MPS)
  7.  w updated via SGD then L1-renormalised to sum = n_tasks

Performance choices:
  - Grad norms computed w.r.t. a SINGLE representative shared parameter
    (last in shared_parameters list, closest to output — matches the paper).
  - Analytical Jacobian replaces second-order autograd (create_graph=True),
    eliminating the MPS bottleneck while keeping the correct update signal.
"""

import torch
import torch.nn.functional as F
from typing import Dict, List, Tuple


class GradNormLoss:
    def __init__(
        self,
        n_tasks: int = 2,
        alpha: float = 1.5,
        lr: float = 1e-3,
        **kwargs,
    ):
        self.n_tasks = n_tasks
        self.alpha = alpha
        self.lr = lr

        # Task weights stored as raw logits; updated manually (no optimizer).
        # w_i = n_tasks * softmax(scale)_i  →  always positive, sum = n_tasks.
        self.loss_scale = torch.zeros(n_tasks)       # CPU, moved to device on use
        self._L0: torch.Tensor | None = None         # initial losses (recorded once)

    # ------------------------------------------------------------------
    # Runner interface
    # backward() → (loss, extras) with already_backpropagated = True
    # ------------------------------------------------------------------

    def backward(
        self,
        losses: torch.Tensor,
        shared_parameters: List[torch.nn.Parameter],
        **kwargs,
    ) -> Tuple[torch.Tensor, Dict]:
        device = losses.device

        # Normalised weights: positive, sum = n_tasks
        w = self.n_tasks * F.softmax(self.loss_scale.to(device), dim=-1)

        # ── Step 0: record initial losses on very first call ──────────
        if self._L0 is None:
            self._L0 = losses.detach().clone().clamp(min=1e-8)
            # First step: equal weighting, skip GradNorm update
            total_loss = (w.detach() * losses).sum()
            total_loss.backward()
            return total_loss.detach(), {"weights": w.detach()}

        # ── Step 1: compute per-task raw gradient norms ───────────────
        # Use the LAST shared parameter as the reference W (paper convention:
        # last shared layer, closest to the task heads).
        ref_param = shared_parameters[-1] if shared_parameters else None

        g_norms = torch.zeros(self.n_tasks, device=device)
        if ref_param is not None:
            for i in range(self.n_tasks):
                (g,) = torch.autograd.grad(
                    losses[i],
                    ref_param,
                    retain_graph=True,
                    allow_unused=True,
                )
                if g is not None:
                    g_norms[i] = g.detach().norm()
                # else stays 0.0

        # ── Step 2: weighted norms G_i = w_i * ||∇_W L_i|| ───────────
        w_d = w.detach()
        G = w_d * g_norms                             # [n_tasks]
        G_avg = G.mean()

        # ── Step 3: targets T_i = Ḡ · r̃_i^α ─────────────────────────
        L_ratio = losses.detach() / self._L0.to(device)
        r_tilde = (L_ratio / L_ratio.mean().clamp(min=1e-8)).clamp(min=1e-8)
        targets = (G_avg * r_tilde ** self.alpha).detach()   # [n_tasks]

        # ── Step 4: analytical gradient ∂L_gn/∂scale_j ───────────────
        # L_gn = Σ_i |G_i - T_i|,  G_i = n_tasks·softmax(scale)_i · g_i
        #
        # ∂G_i/∂scale_j = g_i · n_tasks · w_i · (δ_ij − w_j)
        #               = g_i · (jacobian of w w.r.t. scale)[i,j]
        #
        # ∂L_gn/∂scale_j = Σ_i sign(G_i−T_i) · g_i · jacobian[i,j]
        #                 = [sign(G−T) * g_norms] @ jacobian
        #
        # softmax Jacobian scaled by n_tasks:
        #   J[i,j] = n_tasks · w_i · (δ_ij − w_j)
        sign_diff = torch.sign(G - targets)                  # [n_tasks]
        # Correct Jacobian of w = n*softmax(s) w.r.t. s:
        #   ∂w_i/∂s_j = w_i·δ_ij − w_i·w_j/n
        #   J = diag(w) − (1/n)·w·wᵀ
        J = (
            torch.diag(w_d)
            - (1.0 / self.n_tasks) * w_d.unsqueeze(1) * w_d.unsqueeze(0)
        )                                                    # [n_tasks, n_tasks]
        grad_scale = (sign_diff * g_norms) @ J              # [n_tasks]

        # ── Step 5: SGD step + L1 renormalise (sum = n_tasks) ─────────
        with torch.no_grad():
            # NOTE: this is a *weight-space* SGD step using the *scale-space*
            # gradient (computed via the Jacobian J at the top of this block).
            # It is not the textbook scale-SGD `scale_new = scale_old − lr·grad_scale`
            # — but after the L1 renormalisation below it reaches the same
            # fixed point because `n*softmax(log(updated)) == updated` when
            # `sum(updated) == n_tasks`. The directional test in
            # `tests/test_losses/test_gradnorm.py` confirms the GradNorm
            # property (smaller-loss-ratio task → larger weight) empirically.
            updated = w_d - self.lr * grad_scale
            updated = updated.clamp(min=1e-8)
            # Renormalise so weights still sum to n_tasks
            updated = updated / updated.sum() * self.n_tasks
            # Encode the new weights as logits for next forward pass:
            # forward applies `n_tasks * softmax(loss_scale)`; storing log(w)
            # makes the next forward read out `w` exactly (because the L1
            # renormalisation above makes `softmax(log(w)) = w / n_tasks`).
            self.loss_scale = updated.clamp(min=1e-4).log().cpu()  # clamp prevents -inf silencing tasks

        # ── Step 6: model backward (detached weights, clean grads) ────
        total_loss = (w_d * losses).sum()
        total_loss.backward()

        return total_loss, {"weights": w_d}

    def get_weighted_loss(self, losses, shared_parameters, **kwargs):
        raise NotImplementedError  # force runner to use backward() path

    def parameters(self) -> List:
        return []  # loss_scale updated manually; not exposed to the optimizer
