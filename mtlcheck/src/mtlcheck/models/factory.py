"""Build a head from its recipe entry.

Small on purpose. Its whole job is to make the head's shape come from the configuration rather than
from a module default — the trap documented in `config.HeadConfig`, where the reference's `--model`
flag swaps the class while the hyperparameters keep arriving from somewhere else entirely.
"""

from __future__ import annotations

import torch.nn as nn

from ..config import HeadConfig
from .gru import CategoryHead
from .stan import RegionHead

_HEADS = {
    "next_gru": CategoryHead,
    "next_stan_flow": RegionHead,
}

# Accepted in a recipe and not passed to the constructor. The reference's factory hands one dict of
# model_params to every head class and lets unused keys fall away; naming them here keeps that
# behaviour without letting a TYPO fall away with them.
_IGNORED = {"next_gru": {"seq_length", "num_heads"},
            "next_stan_flow": {"freeze_alpha", "alpha_init"}}


def build_head(config: HeadConfig, *, embed_dim: int, num_classes: int) -> nn.Module:
    if config.name not in _HEADS:
        raise ValueError(f"unknown head {config.name!r}; known: {sorted(_HEADS)}")

    # The prior markers are not constructor arguments here — the prior is an absent branch, not a
    # multiply by zero. But dropping them unread would let a recipe asking for an ACTIVE prior build
    # a prior-less head with no error, which is the exact failure this module's own message decries.
    if config.name == "next_stan_flow":
        freeze = config.params.get("freeze_alpha", True)
        alpha = float(config.params.get("alpha_init", 0.0))
        if not (freeze and alpha == 0.0):
            raise ValueError(
                f"head {config.name!r} was asked for an ACTIVE trajectory-flow prior "
                f"(freeze_alpha={freeze}, alpha_init={alpha}); this port implements only the inert "
                f"configuration v18 runs, and building without the prior would be a different model"
            )

    params = {k: v for k, v in config.params.items() if k not in _IGNORED[config.name]}
    unexpected = set(params) - set(_signature(_HEADS[config.name]))
    if unexpected:
        raise ValueError(
            f"head {config.name!r} does not accept {sorted(unexpected)}. A silently dropped "
            f"hyperparameter is how a model ends up a different size than its recipe claims."
        )
    return _HEADS[config.name](embed_dim=embed_dim, num_classes=num_classes, **params)


def _signature(cls) -> set[str]:
    import inspect
    return set(inspect.signature(cls.__init__).parameters) - {"self", "embed_dim", "num_classes"}


__all__ = ["build_head"]
