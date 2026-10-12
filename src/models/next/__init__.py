"""Next-head domain."""

from .next_conv_attn.head import NextHeadConvAttn
from .next_gru.head import NextHeadGRU
from .next_gru_simgcl.head import NextHeadGRUSimGCL
from .next_hybrid.head import NextHeadHybrid
from .next_lstm.head import NextHeadLSTM
from .next_mamba.head import NextHeadMamba
from .next_mtl.head import NextHeadMTL
from .next_getnext.head import NextHeadGETNext
from .next_stan_flow.head import (
    NextHeadStanFlow,
    NextHeadGETNextHard,  # legacy alias (renamed 2026-05-01)
)
from .next_stan_flow_hsm.head import (
    NextHeadStanFlowHSM,
    NextHeadGETNextHardHSM,  # legacy alias (renamed 2026-05-01)
)
from .next_stan_flow_dualtower.head import NextHeadStanFlowDualTower
from .next_single.head import NextHeadSingle
from .next_stahyper.head import NextHeadSTAHyper
from .next_stan.head import NextHeadSTAN
from .next_tcn_residual.head import NextHeadTCNResidual
from .next_tgstan.head import NextHeadTGSTAN
from .next_temporal_cnn.head import NextHeadTemporalCNN
from .next_transformer_optimized.head import NextHeadTransformerOptimized
from .next_transformer_relpos.head import NextHeadTransformerRelPos

__all__ = [
    "NextHeadSingle",
    "NextHeadMTL",
    "NextHeadLSTM",
    "NextHeadMamba",
    "NextHeadGRU",
    "NextHeadGRUSimGCL",
    "NextHeadSTAN",
    "NextHeadGETNext",
    "NextHeadStanFlow",
    "NextHeadStanFlowHSM",
    "NextHeadStanFlowDualTower",
    # Legacy class-name aliases (renamed 2026-05-01 → STAN-Flow). Both names
    # resolve to the same class object via the ``X = Y`` alias in head.py.
    "NextHeadGETNextHard",
    "NextHeadGETNextHardHSM",
    "NextHeadTGSTAN",
    "NextHeadSTAHyper",
    "NextHeadTemporalCNN",
    "NextHeadHybrid",
    "NextHeadTransformerOptimized",
    "NextHeadTCNResidual",
    "NextHeadConvAttn",
    "NextHeadTransformerRelPos",
]
