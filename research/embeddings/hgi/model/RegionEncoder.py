"""POI-to-Region encoder for HGI."""

import torch
import torch.nn as nn
from torch_geometric.nn import GCNConv

from embeddings.hgi.model.SetTransformer import PMA


class POI2Region(nn.Module):
    """
    POI-to-Region encoder for hierarchical graph representation.

    This encoder aggregates POI-level representations within each region using
    attention-based pooling (PMA), then applies region-level graph convolution
    based on region adjacency.
    """

    def __init__(self, hidden_channels, num_heads):
        """
        Initialize POI2Region encoder.

        Args:
            hidden_channels: Dimension of POI embeddings
            num_heads: Number of attention heads for PMA
        """
        super(POI2Region, self).__init__()
        self.hidden_channels = hidden_channels
        self.num_heads = num_heads

        # Pooling by Multihead Attention (aggregates POIs to 1 region embedding)
        self.PMA = PMA(dim=hidden_channels, num_heads=num_heads, num_seeds=1, ln=False)

        # Region-level graph convolution
        self.conv = GCNConv(hidden_channels, hidden_channels, cached=True, bias=True)

        # PReLU activation (channelwise — matches canonical RightBank/HGI)
        self.prelu = nn.PReLU(hidden_channels)

    def forward(self, x, zone, region_adjacency):
        """
        Aggregate POI embeddings to regions and apply region-level GCN.

        Args:
            x: POI embeddings [num_pois, hidden_channels]
            zone: Region assignment for each POI [num_pois]
            region_adjacency: Region adjacency graph edges [2, num_region_edges]

        Returns:
            Region embeddings [num_regions, hidden_channels]
        """
        # Initialize region embeddings
        num_regions = zone.max() + 1
        region_emb = x.new_zeros((num_regions, x.size()[1]))

        # Aggregate POIs to regions using attention (Vectorized PMA)
        
        # We need to implement PMA/MAB logic but for a graph (ragged) batch.
        # PMA(X) = MAB(S, X) where S is seed.
        # MAB(Q, K, V) = Softmax(Q K^T / sqrt(d)) V
        
        # Here Q = S (1 seed vector per region).
        # Since S is the same learned parameter for ALL regions, we can treat it as a shared query.
        
        # Dimensions:
        # x: [num_pois, dim] (These are K and V inputs)
        # zone: [num_pois] (Region ID for each POI)
        # S: [1, 1, dim] (Learned Seed) -> [1, dim]
        
        # 1. Projections
        # Note: We need to access the weights from the existing self.PMA module to maintain
        # compatibility with saved models if possible, or we reimplement access to them.
        # self.PMA.mab.fc_k, self.PMA.mab.fc_v, self.PMA.mab.fc_q
        
        mab = self.PMA.mab
        
        # Project K and V (POIs)
        # K_pois: [num_pois, dim]
        K_pois = mab.fc_k(x)
        V_pois = mab.fc_v(x)
        
        # Project Q (Seed)
        # S: [1, 1, dim] -> [1, dim]
        Q_seed = mab.fc_q(self.PMA.S).squeeze(0) 
        
        # 2. Multi-head splitting
        # dim_split = dim // num_heads
        dim_split = self.hidden_channels // self.num_heads
        N = x.size(0)

        # Split K, V into heads: [num_pois, num_heads, dim_split]
        # Direct view is correct: feature slice [h*d:(h+1)*d] maps to head h.
        # NOTE: torch.cat(split, 0).view(-1, H, d) is WRONG because it produces
        # [H*N, d] where heads are in blocks of N, not interleaved — view then
        # scrambles head/poi assignment. Use view directly instead.
        K_split = K_pois.view(N, self.num_heads, dim_split)
        V_split = V_pois.view(N, self.num_heads, dim_split)

        # Split Q: [1, num_heads, dim_split]
        Q_split = Q_seed.view(1, self.num_heads, dim_split)
        
        # 3. Attention Scores
        # Score = Q * K^T
        # Q: [1, heads, d], K: [P, heads, d]
        # We want Score[P, heads].
        # Since Q is shared for all regions, we can just do elementwise mult sum?
        # Q * K = [P, heads, d]. sum(-1) -> [P, heads].
        # effectively: (K_split * Q_split).sum(dim=-1)
        
        # shape: [num_pois, num_heads]
        scores = (K_split * Q_split).sum(dim=-1)
        scores = scores / torch.sqrt(torch.tensor(self.hidden_channels, dtype=torch.float32).to(x.device))
        
        # 4. Segmented Softmax
        # We need softmax over POIs *within each region* (defined by `zone` index)
        # from torch_geometric.utils import softmax
        # But we need to import it.
        # import inside method or at top? Let's fix imports in separate tool call if needed, 
        # but torch_geometric.utils is standard.
        from torch_geometric.utils import softmax as pyg_softmax
        
        # We need to expand zone to heads if we want individual softmax per head? 
        # Usually softmax is per query. Here each region has 1 query.
        # So for each head, for each region, we softmax over the POIs in that region.
        
        # scores: [num_pois, num_heads]
        # zone: [num_pois]
        # We can treat each head as a separate channel or flatten?
        # pyg_softmax expects src and index.
        # It handles multi-dimensional src correctly (softmaxing over index dim usually).
        # Let's verify: src [N, Heads], index [N]. 
        # Result: [N, Heads] where sum over index is 1 for each head.
        
        alpha = pyg_softmax(scores, zone, num_nodes=num_regions)
        
        # 5. Weighted Aggregation
        # Out = alpha * V
        # V_split: [num_pois, num_heads, dim_split]
        # alpha: [num_pois, num_heads] -> expand to [num_pois, num_heads, 1]
        
        weighted_V = V_split * alpha.unsqueeze(-1)
        
        # Sum relative to region (scatter_add)
        from torch_geometric.utils import scatter
        
        # region_agg: [num_regions, num_heads, dim_split]
        region_agg = scatter(weighted_V, zone, dim=0, dim_size=num_regions, reduce='add')
        
        # 6. Concatenate Heads and Output Projection
        # [num_regions, num_heads * dim_split] -> [num_regions, dim]
        region_agg = region_agg.view(num_regions, self.hidden_channels)
        
        # Output Linear + Residual + Norm (MAB logic)
        # Original MAB: O = Q + A V ?
        # Wait, MAB(Q, K, V) = LayerNorm(Q + Attention(Q,K,V))
        # Here Q matches dimensions of Output?
        # Q is [1, dim]. Output is [num_regions, dim].
        # We should broadcast Q to num_regions.
        
        Q_broadcast = Q_seed.repeat(num_regions, 1)
        
        # Apply output projection from MAB
        # In MAB: O = cat(...)
        # O = O + F.relu(self.fc_o(O)) (this is the FFN part, separate from attention block)
        # Wait, structure of MAB in SetTransformer.py:
        # O = Q_ + A.bmm(V_)  (Attention result)
        # O = O if ln0 is None else ln0(O)
        # O = O + F.relu(fc_o(O))
        # O = O if ln1 is None else ln1(O)
        
        # Note: MAB implementation in SetTransformer checks for ln0/ln1 existence.
        
        O = Q_broadcast + region_agg # Residual connection to Query
        
        if getattr(mab, 'ln0', None) is not None:
             O = mab.ln0(O)
             
        # FFN part
        # Note: In MAB, it's O + F.relu(fc_o(O)). Wait, usually it is O + O2... 
        # Line 63 of SetTransformer.py: O = O + F.relu(self.fc_o(O))
        # This looks slightly weird (normally O + FFN(O)) but let's follow the code.
        
        import torch.nn.functional as F
        O = O + F.relu(mab.fc_o(O))
        
        if getattr(mab, 'ln1', None) is not None:
            O = mab.ln1(O)
            
        region_emb = O

        # Apply region-level GCN on adjacency graph
        region_emb = self.conv(region_emb, region_adjacency)

        # Apply activation
        region_emb = self.prelu(region_emb)

        # Replace NaN values with 0 (for regions with no POIs or no neighbors)
        region_emb = torch.nan_to_num(region_emb, nan=0.0)

        return region_emb

    def __repr__(self):
        return (f'{self.__class__.__name__}('
                f'hidden={self.hidden_channels}, '
                f'heads={self.num_heads})')
