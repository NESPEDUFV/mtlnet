"""Loss registry — select loss functions by name from config.

Usage:
    from losses.registry import create_loss

    loss = create_loss("nash_mtl", n_tasks=2, device=device)
    loss = create_loss("focal", alpha=weights, gamma=2.0)

Canonical names and short aliases live in ``_CANONICAL`` / ``_ALIASES``
below. Registration happens lazily on first ``create_loss`` /
``list_losses`` call so importing ``losses.registry`` stays cheap.
"""

from typing import Type

_LOSS_REGISTRY: dict[str, type] = {}
_REGISTERED = False


def _canonical_entries() -> list[tuple[str, Type]]:
    """Import loss classes lazily and return (name, cls) pairs.

    One import site for every supported loss — do not add aliases here;
    put them in ``_alias_entries`` below.
    """
    from losses.nash_mtl import NashMTL
    from losses.equal_weight.loss import EqualWeightLoss
    from losses.static_weight.loss import StaticWeightLoss
    from losses.scheduled_static.loss import ScheduledStaticWeightLoss
    from losses.uncertainty_weighting.loss import UncertaintyWeightingLoss
    from losses.uw_so.loss import SoftOptimalUncertaintyWeightingLoss
    from losses.random_weight.loss import RandomWeightLoss
    from losses.famo.loss import FAMOLoss
    from losses.fairgrad.loss import FairGradLoss
    from losses.bayesagg_mtl.loss import BayesAggMTLLoss
    from losses.go4align.loss import GO4AlignLoss
    from losses.excess_mtl.loss import ExcessMTLLoss
    from losses.stch.loss import STCHLoss
    from losses.db_mtl.loss import DBMTLLoss
    from losses.cagrad.loss import CAGradLoss
    from losses.aligned_mtl.loss import AlignedMTLLoss
    from losses.dwa.loss import DWALoss
    from losses.focal import FocalLoss
    from losses.pcgrad import PCGrad
    from losses.gradnorm import GradNormLoss
    from losses.naive import NaiveLoss

    return [
        ("nash_mtl", NashMTL),
        ("equal_weight", EqualWeightLoss),
        ("static_weight", StaticWeightLoss),
        ("scheduled_static", ScheduledStaticWeightLoss),
        ("uncertainty_weighting", UncertaintyWeightingLoss),
        ("uw_so", SoftOptimalUncertaintyWeightingLoss),
        ("random_weight", RandomWeightLoss),
        ("famo", FAMOLoss),
        ("fairgrad", FairGradLoss),
        ("bayesagg_mtl", BayesAggMTLLoss),
        ("go4align", GO4AlignLoss),
        ("excess_mtl", ExcessMTLLoss),
        ("stch", STCHLoss),
        ("db_mtl", DBMTLLoss),
        ("cagrad", CAGradLoss),
        ("aligned_mtl", AlignedMTLLoss),
        ("dwa", DWALoss),
        ("focal", FocalLoss),
        ("pcgrad", PCGrad),
        ("gradnorm", GradNormLoss),
        ("naive", NaiveLoss),
    ]


# Short aliases → canonical name. Keep this list small and opinionated;
# if a name is ambiguous, require the canonical spelling in configs.
_ALIASES: dict[str, str] = {
    "rlw": "random_weight",
    "bayesagg": "bayesagg_mtl",
    "excessmtl": "excess_mtl",
}


def _ensure_registered() -> None:
    """Populate the registry once per process."""
    global _REGISTERED
    if _REGISTERED:
        return

    for name, cls in _canonical_entries():
        if name in _LOSS_REGISTRY and _LOSS_REGISTRY[name] is not cls:
            raise ValueError(
                f"Loss '{name}' already registered by "
                f"{_LOSS_REGISTRY[name].__name__}; cannot re-register with "
                f"{cls.__name__}"
            )
        _LOSS_REGISTRY[name] = cls

    for alias, canonical in _ALIASES.items():
        if canonical not in _LOSS_REGISTRY:
            raise ValueError(
                f"Alias '{alias}' points to unknown loss '{canonical}'"
            )
        _LOSS_REGISTRY[alias] = _LOSS_REGISTRY[canonical]

    _REGISTERED = True


def create_loss(name: str, **kwargs):
    """Instantiate a registered loss by name."""
    _ensure_registered()
    if name not in _LOSS_REGISTRY:
        raise KeyError(
            f"Loss '{name}' not registered. "
            f"Available: {sorted(_LOSS_REGISTRY.keys())}"
        )
    return _LOSS_REGISTRY[name](**kwargs)


def list_losses() -> list[str]:
    """Return sorted list of registered loss names."""
    _ensure_registered()
    return sorted(_LOSS_REGISTRY.keys())
