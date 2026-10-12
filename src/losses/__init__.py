"""Canonical public exports for loss classes and registry helpers.

Import from this module (or from each variant package) as the canonical API.
"""

from losses.aligned_mtl.loss import AlignedMTLLoss
from losses.bayesagg_mtl.loss import BayesAggMTLLoss
from losses.cagrad.loss import CAGradLoss
from losses.dwa.loss import DWALoss
from losses.db_mtl.loss import DBMTLLoss
from losses.equal_weight.loss import EqualWeightLoss
from losses.excess_mtl.loss import ExcessMTLLoss
from losses.fairgrad.loss import FairGradLoss
from losses.famo.loss import FAMOLoss
from losses.focal.loss import FocalLoss
from losses.go4align.loss import GO4AlignLoss
from losses.gradnorm.loss import GradNormLoss
from losses.naive.loss import NaiveLoss
from losses.nash_mtl.loss import NashMTL, WeightMethod
from losses.pcgrad.loss import PCGrad
from losses.random_weight.loss import RandomWeightLoss
from losses.registry import create_loss, list_losses
from losses.static_weight.loss import StaticWeightLoss
from losses.stch.loss import STCHLoss
from losses.uncertainty_weighting.loss import UncertaintyWeightingLoss
from losses.uw_so.loss import SoftOptimalUncertaintyWeightingLoss

__all__ = [
    "WeightMethod",
    "NashMTL",
    "AlignedMTLLoss",
    "CAGradLoss",
    "DWALoss",
    "FocalLoss",
    "PCGrad",
    "GradNormLoss",
    "NaiveLoss",
    "EqualWeightLoss",
    "StaticWeightLoss",
    "UncertaintyWeightingLoss",
    "SoftOptimalUncertaintyWeightingLoss",
    "RandomWeightLoss",
    "FAMOLoss",
    "FairGradLoss",
    "BayesAggMTLLoss",
    "GO4AlignLoss",
    "ExcessMTLLoss",
    "STCHLoss",
    "DBMTLLoss",
    "create_loss",
    "list_losses",
]
