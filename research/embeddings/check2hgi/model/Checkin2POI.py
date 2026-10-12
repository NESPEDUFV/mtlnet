"""Check-in to POI aggregation encoder for Check2HGI."""

import torch
import torch.nn as nn
import torch.nn.functional as F
from torch_geometric.utils import softmax as pyg_softmax, scatter


class Checkin2POI(nn.Module):
    """
    Check-in to POI encoder for hierarchical graph representation.

    This encoder aggregates check-in level representations within each POI using
    attention-based pooling (similar to PMA from Set Transformer).
    """

    def __init__(self, hidden_channels, num_heads=4,
                 t63_enabled: bool = False, t63_num_pois: int | None = None,
                 t63_rank: int = 8):
        """
        Initialize Checkin2POI encoder.

        Args:
            hidden_channels: Dimension of check-in embeddings
            num_heads: Number of attention heads
            t63_enabled: T6.1 / T6.3 — when True, add a rank-r per-POI bias
                to the attention LOGIT (NOT to input or pooled output).
                Default False ⇒ canonical bit-identical.
            t63_num_pois: Required when t63_enabled=True. Sets the size of
                the per-POI bias table.
            t63_rank: rank-r of the per-POI bias (default 8). Spec sweep
                r ∈ {4, 8}. Zero-init for v keeps step-0 forward
                byte-identical to canonical.
        """
        super(Checkin2POI, self).__init__()
        self.hidden_channels = hidden_channels
        self.num_heads = num_heads

        # Attention projections
        self.fc_q = nn.Linear(hidden_channels, hidden_channels)
        self.fc_k = nn.Linear(hidden_channels, hidden_channels)
        self.fc_v = nn.Linear(hidden_channels, hidden_channels)
        self.fc_o = nn.Linear(hidden_channels, hidden_channels)

        # Learnable seed vector (shared query for all POIs)
        self.S = nn.Parameter(torch.Tensor(1, hidden_channels))
        nn.init.xavier_uniform_(self.S)

        # Pre-compute scaling constant (avoid tensor creation every forward pass)
        self.register_buffer('scale', torch.sqrt(torch.tensor(hidden_channels, dtype=torch.float32)))

        # PReLU activation
        self.prelu = nn.PReLU()

        # T6.3 — low-rank per-POI bias at the attention LOGIT only.
        # Mechanism: for each check-in c with poi p=checkin_to_poi[c], add a
        # per-check-in scalar bias to its attention score given by
        #   bias_c = (U @ v_p) · K_c
        # where v ∈ R^{N_pois×r} (per-POI rank-r free vector) and
        #       U ∈ R^{r×D}      (shared projection to key space).
        # The bias only re-weights which check-ins attend to each POI; v never
        # enters the input layer and never enters the pooled output directly.
        # Zero-init v ⇒ step-0 forward bit-identical to canonical (the bias
        # term is identically zero); Xavier-init U is mathematically inert
        # while v=0 but lets gradient flow once v starts moving.
        self.t63_enabled = bool(t63_enabled)
        self.t63_rank = int(t63_rank)
        if self.t63_enabled:
            if t63_num_pois is None or int(t63_num_pois) <= 0:
                raise ValueError(
                    "T6.3 (t63_enabled=True) requires t63_num_pois (positive int) "
                    "from the preprocessed graph. Do NOT hard-code; read from "
                    "city_dict['num_pois']."
                )
            self.t63_num_pois = int(t63_num_pois)
            self.t63_v = nn.Embedding(self.t63_num_pois, self.t63_rank)
            with torch.no_grad():
                self.t63_v.weight.zero_()
            self.t63_U = nn.Linear(self.t63_rank, hidden_channels, bias=False)
            # Xavier-init U (the bias is identically zero at step 0 because
            # v is zero; Xavier U just sets the initial gradient direction).
            nn.init.xavier_uniform_(self.t63_U.weight)
        else:
            self.t63_num_pois = 0
            self.t63_v = None
            self.t63_U = None

    def forward(self, x, checkin_to_poi, num_pois):
        """
        Aggregate check-in embeddings to POIs using attention.

        Args:
            x: Check-in embeddings [num_checkins, hidden_channels]
            checkin_to_poi: POI assignment for each check-in [num_checkins]
            num_pois: Total number of POIs

        Returns:
            POI embeddings [num_pois, hidden_channels]
        """
        # Project K and V (check-ins)
        K = self.fc_k(x)  # [num_checkins, hidden_channels]
        V = self.fc_v(x)  # [num_checkins, hidden_channels]

        # Project Q (shared seed)
        Q = self.fc_q(self.S)  # [1, hidden_channels]

        # Multi-head splitting
        dim_split = self.hidden_channels // self.num_heads

        # Split K, V into heads: [num_checkins, num_heads, dim_split]
        K_split = K.view(-1, self.num_heads, dim_split)
        V_split = V.view(-1, self.num_heads, dim_split)

        # Split Q: [1, num_heads, dim_split]
        Q_split = Q.view(1, self.num_heads, dim_split)

        # Attention scores: (K * Q).sum(-1) / sqrt(d)
        # [num_checkins, num_heads]
        scores = (K_split * Q_split).sum(dim=-1)
        scores = scores / self.scale

        # T6.3 — add the rank-r per-POI bias to the attention logits.
        # For each check-in c with poi p = checkin_to_poi[c]:
        #   bias_c = (U @ v[p]) · K_c     ∈ R   (per head)
        # We index v rows by checkin_to_poi (N_checkins lookups), project
        # via U to D-dim, split into heads, and dot with K_split per head.
        # At t63_v zero-init this bias is identically zero (step-0 forward
        # bit-identical to canonical).
        if self.t63_enabled:
            # v_per_checkin: [num_checkins, rank]
            v_per_checkin = self.t63_v(checkin_to_poi)
            # Uv: [num_checkins, D] — project rank → D
            Uv = self.t63_U(v_per_checkin)
            # Reshape to heads: [num_checkins, num_heads, dim_split]
            Uv_split = Uv.view(-1, self.num_heads, dim_split)
            # Bias per (check-in, head): (Uv_split * K_split).sum(-1) / scale
            bias = (Uv_split * K_split).sum(dim=-1) / self.scale
            scores = scores + bias

        # Segmented softmax over check-ins within each POI
        alpha = pyg_softmax(scores, checkin_to_poi, num_nodes=num_pois)

        # Weighted aggregation
        # V_split: [num_checkins, num_heads, dim_split]
        # alpha: [num_checkins, num_heads] -> [num_checkins, num_heads, 1]
        weighted_V = V_split * alpha.unsqueeze(-1)

        # Ensure contiguous for efficient scatter (especially on MPS)
        weighted_V = weighted_V.contiguous()

        # Sum per POI (scatter_add)
        # poi_agg: [num_pois, num_heads, dim_split]
        poi_agg = scatter(weighted_V, checkin_to_poi, dim=0, dim_size=num_pois, reduce='add')

        # Concatenate heads: [num_pois, hidden_channels]
        poi_agg = poi_agg.view(num_pois, self.hidden_channels)

        # Residual connection with broadcast Q
        Q_broadcast = Q.repeat(num_pois, 1)
        O = Q_broadcast + poi_agg

        # Output projection with activation
        O = O + F.relu(self.fc_o(O))

        # Final activation
        O = self.prelu(O)

        # Replace NaN values with 0 (for POIs with no check-ins)
        O = torch.nan_to_num(O, nan=0.0)

        return O

    def __repr__(self):
        return (f'{self.__class__.__name__}('
                f'hidden={self.hidden_channels}, '
                f'heads={self.num_heads})')
