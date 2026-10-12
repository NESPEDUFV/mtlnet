"""MTL architecture domain."""

from .mtlnet.model import MTLnet
from .mtlnet_cgc.model import MTLnetCGC
from .mtlnet_crossattn.model import MTLnetCrossAttn
from .mtlnet_crossattn_dualtower.model import MTLnetCrossAttnDualTower
from .mtlnet_crossattn_dualtower_catpriv.model import MTLnetCrossAttnDualTowerCatPriv
from .mtlnet_crossattn_dualtower_swiglu.model import MTLnetCrossAttnDualTowerSwiGLU
from .mtlnet_crossattn_mult.model import MTLnetCrossAttnMulT
from .mtlnet_crossattn_swiglu.model import MTLnetCrossAttnSwiGLU
from .mtlnet_crossattn_xstitch.model import MTLnetCrossAttnXStitch
from .mtlnet_crossstitch.model import MTLnetCrossStitch
from .mtlnet_dselectk.model import MTLnetDSelectK
from .mtlnet_mmoe.model import MTLnetMMoE
from .mtlnet_ple.model import MTLnetPLE

__all__ = [
    "MTLnet", "MTLnetCGC", "MTLnetCrossAttn", "MTLnetCrossAttnDualTower",
    "MTLnetCrossAttnDualTowerCatPriv", "MTLnetCrossAttnDualTowerSwiGLU", "MTLnetCrossAttnMulT", "MTLnetCrossAttnSwiGLU",
    "MTLnetCrossAttnXStitch", "MTLnetCrossStitch", "MTLnetMMoE", "MTLnetDSelectK", "MTLnetPLE",
]
