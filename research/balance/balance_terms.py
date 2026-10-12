"""Two auxiliary terms that target the measured failure, kept out of the frozen model code.

WHAT WAS MEASURED (docs/studies/balance/FINDINGS.md, Alabama, L1 linear probe on frozen vectors):

    arm                 category   place   region   effective rank / 64
    forward-only          0.988    0.176    0.067        8.43
    + elapsed time        0.988    0.170    0.082       10.25
    + region identity     0.910    0.786    0.964        8.43
    + place identity      0.733    0.865    0.531       19.45

Adding an input factor raises that factor's recoverability and LOWERS the category's. The
representation substitutes rather than accumulates, and it does so with most of its dimensions idle:
the forward-only arm uses 8.4 of 64 directions by participation ratio.

WHAT THE LITERATURE CALLS THIS. The substitution is feature suppression, characterised for contrastive
objectives by Robinson et al., "Can contrastive learning avoid shortcut solutions?" (NeurIPS 2021,
arXiv:2106.11230): with several predictive features available, the encoder uses a subset and ignores
the rest, and adjustments that improve one feature typically harm another. Their remedy, implicit
feature modification, perturbs the discrimination task rather than the encoder. The idle-dimension
half is dimensional collapse, surveyed in the SSL cookbook (arXiv:2304.12210) and attacked by
whitening and covariance-regularisation methods (arXiv:2408.07519, arXiv:2402.09586).

The two terms below are the cheapest faithful adaptations of those two lines to this model. Neither
changes the encoder, the graph, or the three hierarchical boundary losses; both are additive
penalties on the check-in-level embedding, so setting their weights to zero reproduces the frozen
recipe bit for bit.

  T1 VARIANCE-COVARIANCE (anti-collapse). The variance hinge and off-diagonal covariance penalty of
     VICReg. The hinge pushes every dimension's standard deviation to at least a target, which is
     what fills idle directions; the covariance term decorrelates them, which is what stops a new
     factor from being written on top of an existing one instead of beside it. Directly addresses the
     8.4-of-64 measurement.

  T2 FACTOR-PRESERVATION (anti-suppression). An explicit linear-decodability floor for the factor we
     do not want traded away. A small linear head predicts the visit's own category from the
     embedding, and its cross-entropy is added to the objective. This does NOT make the model
     supervised for the downstream task: the visit's own category is an observed input column, already
     present in the node features, and the target visit's category is never involved. It is a
     statement that whatever else the embedding learns, this coordinate must remain linearly present.

     Honest reading of what T2 can and cannot show. Because the probe we evaluate with is also a
     linear category decoder, T2 optimises something close to the metric. A T2 gain in category
     recoverability is therefore NOT evidence on its own; the informative quantities are (a) whether
     the OTHER factors survive at the same time, which is what "balance" means, and (b) whether the
     downstream score moves, which T2 does not optimise. This caveat is repeated in the report.
"""
from __future__ import annotations

import torch
import torch.nn as nn
import torch.nn.functional as F


def variance_covariance_terms(z: torch.Tensor, gamma: float = 1.0) -> tuple[torch.Tensor, torch.Tensor]:
    """VICReg's variance hinge and off-diagonal covariance penalty for one embedding matrix.

    Args:
        z: [N, D] embeddings.
        gamma: target standard deviation per dimension.

    Returns:
        (variance_term, covariance_term), both scalars, both zero for a whitened representation with
        unit per-dimension standard deviation.
    """
    n, d = z.shape
    zc = z - z.mean(dim=0, keepdim=True)
    std = torch.sqrt(zc.var(dim=0) + 1e-4)
    var_term = F.relu(gamma - std).mean()
    cov = (zc.T @ zc) / max(1, n - 1)
    off = cov - torch.diag_embed(torch.diagonal(cov))
    cov_term = off.pow(2).sum() / d
    return var_term, cov_term


class CategoryPreservationHead(nn.Module):
    """A linear decodability floor for the visit's own category.

    One matrix, no hidden layer, deliberately: the point is to require that the category stay LINEARLY
    present, which is exactly the property the L1 probe measures and the property that collapsed from
    0.988 to 0.733 when place identity was added. A deeper head would let the embedding hide the
    category behind a nonlinearity and still satisfy the term.
    """

    def __init__(self, dim: int, n_classes: int = 7):
        super().__init__()
        self.fc = nn.Linear(dim, n_classes)

    def forward(self, z: torch.Tensor, y: torch.Tensor) -> torch.Tensor:
        return F.cross_entropy(self.fc(z), y)


def balance_loss(z: torch.Tensor,
                 y_cat: torch.Tensor | None = None,
                 head: CategoryPreservationHead | None = None,
                 lambda_var: float = 0.0,
                 lambda_cov: float = 0.0,
                 lambda_cat: float = 0.0,
                 gamma: float = 1.0) -> tuple[torch.Tensor, dict]:
    """Assemble the auxiliary terms. All-zero weights return an exact zero, so the frozen path is
    unchanged rather than merely approximately unchanged."""
    parts: dict[str, float] = {}
    total = z.new_zeros(())
    if lambda_var > 0.0 or lambda_cov > 0.0:
        v, c = variance_covariance_terms(z, gamma=gamma)
        total = total + lambda_var * v + lambda_cov * c
        parts["variance"] = float(v.detach())
        parts["covariance"] = float(c.detach())
    if lambda_cat > 0.0:
        if head is None or y_cat is None:
            raise ValueError("lambda_cat > 0 requires both a head and category targets")
        ce = head(z, y_cat)
        total = total + lambda_cat * ce
        parts["category_ce"] = float(ce.detach())
    return total, parts
