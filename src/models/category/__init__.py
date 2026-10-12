"""Category-head domain."""

from .category_attention.head import CategoryHeadAttentionPooling
from .category_dcn.head import DCNHead
from .category_ensemble.head import CategoryHeadEnsemble
from .category_gated.head import CategoryHeadGated
from .category_linear.head import CategoryHeadLinear
from .category_residual.head import CategoryHeadResidual
from .category_se.head import SEHead
from .category_single.head import CategoryHeadSingle
from .category_transformer.head import CategoryHeadTransformer

__all__ = [
    "CategoryHeadSingle",
    "CategoryHeadLinear",
    "CategoryHeadResidual",
    "CategoryHeadGated",
    "CategoryHeadEnsemble",
    "CategoryHeadAttentionPooling",
    "CategoryHeadTransformer",
    "DCNHead",
    "SEHead",
]
