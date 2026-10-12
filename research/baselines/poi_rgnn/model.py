"""Faithful POI-RGNN port (Capanema 2023, Ad Hoc Networks).

Architecture mirror of ``mtl_poi/src/models/rgnn/rgnn_torch.py::MFA_RNN``:

  * Multi-modal embeddings: category(emb 7), hour(emb 3), distance(emb 3),
    duration(emb 3), distance×duration weighted product (emb 3).
  * GRU(35) + custom Keras-style multi-head attention (4 heads, key_dim=2).
  * Three parallel 2-layer DenseGCNConv branches over per-fold category
    graph (adj normalised symmetrically, dist-feat, dur-feat,
    dist*dur-feat). Each branch yields [B, n_cat, 10] flattened.
  * Four prediction heads (y_sup, spatial, gnn, gnn_puro) combined via
    entropy-weighted learnable scalars (CombinePredictionsLayer).
  * Outputs LOGITS over n_categories (here: 7).

Adaptations:

  * ``cat_dist_matrix`` and ``cat_dur_matrix`` are FOLD-LEVEL constants
    (computed by trainer on train rows only); the model receives them as
    a single ``[n_cat, n_cat]`` tensor and broadcasts in the GCN forward.
  * Uses PAD=0 for hour/dist/dur tokens so embedding tables have +1 size
    over the paper's index range.
"""

from __future__ import annotations

import math

import torch
import torch.nn as nn
import torch.nn.functional as F


class _EntropyLayer(nn.Module):
    def forward(self, p: torch.Tensor) -> torch.Tensor:
        eps = 1e-10
        p = torch.clamp(p, eps, 1.0 - eps)
        p = p / p.sum(dim=1, keepdim=True)
        return -(p * torch.log(p)).sum(dim=1)


class _MultiplyByWeight(nn.Module):
    def __init__(self, init: float = 0.1):
        super().__init__()
        self.w = nn.Parameter(torch.tensor(init, dtype=torch.float32))

    def forward(self, a, b):
        return self.w * (a * b)


class _CombinePredictions(nn.Module):
    def __init__(self):
        super().__init__()
        self.entropy_w_1 = nn.Parameter(torch.tensor(0.5))
        self.base_w_1 = nn.Parameter(torch.tensor(1.0))
        self.spatial_scalar = nn.Parameter(torch.tensor(-0.2))
        self.entropy_w_2 = nn.Parameter(torch.tensor(0.5))
        self.base_w_2 = nn.Parameter(torch.tensor(1.0))
        self.gnn_scalar = nn.Parameter(torch.tensor(8.0))
        self.entropy_w_3 = nn.Parameter(torch.tensor(0.5))
        self.base_w_3 = nn.Parameter(torch.tensor(1.0))
        self.gnn_puro_scalar = nn.Parameter(torch.tensor(8.0))

    def forward(self, r_ent, g_ent, gp_ent, y_sup, spatial, gnn, gnn_puro):
        eps = 1e-10
        t1 = ((1.0 / (r_ent.mean() + eps) + self.entropy_w_1) * self.base_w_1) * y_sup
        t2 = self.spatial_scalar * spatial
        t3 = self.gnn_scalar * (
            (1.0 / (g_ent.mean() + eps) + self.entropy_w_2) * self.base_w_2
        ) * gnn
        t4 = self.gnn_puro_scalar * (
            (1.0 / (gp_ent.mean() + eps) + self.entropy_w_3) * self.base_w_3
        ) * gnn_puro
        return t1 + t2 + t3 + t4


class _TFStyleMHA(nn.Module):
    """Keras MHA(num_heads, key_dim) — key/value dims independent of input."""

    def __init__(self, input_dim: int, num_heads: int, key_dim: int):
        super().__init__()
        self.num_heads = num_heads
        self.key_dim = key_dim
        total = num_heads * key_dim
        self.w_q = nn.Linear(input_dim, total)
        self.w_k = nn.Linear(input_dim, total)
        self.w_v = nn.Linear(input_dim, total)
        self.w_o = nn.Linear(total, input_dim)

    def forward(self, x):
        B, T, _ = x.shape
        Q = self.w_q(x).view(B, T, self.num_heads, self.key_dim).transpose(1, 2)
        K = self.w_k(x).view(B, T, self.num_heads, self.key_dim).transpose(1, 2)
        V = self.w_v(x).view(B, T, self.num_heads, self.key_dim).transpose(1, 2)
        attn = torch.matmul(Q, K.transpose(-2, -1)) / math.sqrt(self.key_dim)
        attn = F.softmax(attn, dim=-1)
        out = torch.matmul(attn, V).transpose(1, 2).reshape(B, T, self.num_heads * self.key_dim)
        return self.w_o(out)


class _DenseGCN(nn.Module):
    """Spektral-style dense GCN. ``normalize=False`` matches reference."""

    def __init__(self, in_f, out_f, activation: str | None = "swish"):
        super().__init__()
        self.weight = nn.Parameter(torch.empty(in_f, out_f))
        self.bias = nn.Parameter(torch.zeros(out_f))
        nn.init.xavier_uniform_(self.weight)
        self.activation = activation

    def forward(self, x, adj):
        # x: [B, N, in_f]; adj: [B, N, N] (already normalized)
        if x.dim() == 2:
            x = x.unsqueeze(0)
        if adj.dim() == 2:
            adj = adj.unsqueeze(0).expand(x.size(0), -1, -1)
        out = torch.bmm(adj, x @ self.weight) + self.bias
        if self.activation == "swish":
            out = F.silu(out)
        return out


class POIRGNN(nn.Module):
    def __init__(self, n_categories: int = 7, step_size: int = 9):
        super().__init__()
        self.n_cat = n_categories
        self.step = step_size

        # Embeddings — +1 over the paper to reserve index 0 for PAD.
        self.emb_cat = nn.Embedding(n_categories, 7)  # cat tokens are 0..6, no PAD needed (real tokens fill all 9 positions)
        self.emb_hour = nn.Embedding(49, 3)
        self.emb_dist = nn.Embedding(52, 3)
        self.emb_dur = nn.Embedding(50, 3)

        self.gru = nn.GRU(input_size=7 + 3 + 3 + 3 + 3, hidden_size=35, batch_first=True)
        self.drop_gru = nn.Dropout(0.5)
        self.mha = _TFStyleMHA(input_dim=35, num_heads=4, key_dim=2)

        # 3 parallel 2-layer GCN stacks (input dim = n_cat).
        self.gcn_dist_1 = _DenseGCN(n_categories, 22)
        self.drop_d1 = nn.Dropout(0.5)
        self.gcn_dist_2 = _DenseGCN(22, 10)
        self.drop_d2 = nn.Dropout(0.5)

        self.gcn_dur_1 = _DenseGCN(n_categories, 22)
        self.gcn_dur_2 = _DenseGCN(22, 10)
        self.drop_dur = nn.Dropout(0.3)

        self.gcn_dd_1 = _DenseGCN(n_categories, 22)
        self.gcn_dd_2 = _DenseGCN(22, 10)
        self.drop_dd = nn.Dropout(0.3)

        gru_flat = step_size * 35
        self.dense_y_sup = nn.Linear(gru_flat * 2, n_categories)
        self.drop_y_sup = nn.Dropout(0.3)
        self.dense_gnn = nn.Linear(gru_flat * 2 + 10 * n_categories * 3, n_categories)
        self.dense_gnn_puro = nn.Linear(10 * n_categories * 3, n_categories)
        self.dense_spatial = nn.Linear(step_size * 7, n_categories)

        self.dist_dur_mul = _MultiplyByWeight(0.1)
        self.entropy = _EntropyLayer()
        self.combine = _CombinePredictions()

    def forward(self, cat, hour, dist, dur, adj, cat_dist, cat_dur):
        # cat: [B, T] long; adj/cat_dist/cat_dur: [n_cat, n_cat] (broadcast in GCN)
        B = cat.size(0)
        e_cat = self.emb_cat(cat)        # [B, T, 7]
        e_hour = self.emb_hour(hour)      # [B, T, 3]
        e_dist = self.emb_dist(dist)      # [B, T, 3]
        e_dur = self.emb_dur(dur)         # [B, T, 3]
        e_dd = self.dist_dur_mul(e_dist, e_dur)

        spatial_flat = e_cat.reshape(B, -1)                       # [B, T*7]
        gru_in = torch.cat([e_cat, e_hour, e_dist, e_dur, e_dd], dim=2)
        gru_out, _ = self.gru(gru_in)
        gru_out = self.drop_gru(gru_out)
        att_out = self.mha(gru_out)
        gru_flat = gru_out.reshape(B, -1)
        att_flat = att_out.reshape(B, -1)

        # GCN branches over [n_cat × n_cat] feature matrices.
        # Use cat_dist/cat_dur themselves as node features (matches reference).
        x_d = self.drop_d1(self.gcn_dist_1(cat_dist, adj))
        x_d = self.drop_d2(self.gcn_dist_2(x_d, adj))
        x_d_flat = x_d.reshape(x_d.size(0), -1).expand(B, -1)

        x_du = self.gcn_dur_1(cat_dur, adj)
        x_du = self.drop_dur(self.gcn_dur_2(x_du, adj))
        x_du_flat = x_du.reshape(x_du.size(0), -1).expand(B, -1)

        x_dd_in = cat_dist * cat_dur
        x_dd = self.gcn_dd_1(x_dd_in, adj)
        x_dd = self.drop_dd(self.gcn_dd_2(x_dd, adj))
        x_dd_flat = x_dd.reshape(x_dd.size(0), -1).expand(B, -1)

        y_sup = torch.cat([gru_flat, att_flat], dim=1)
        y_sup = self.drop_y_sup(y_sup)
        y_sup_logits = self.dense_y_sup(y_sup)

        gnn_logits = self.dense_gnn(
            torch.cat([gru_flat, att_flat, x_d_flat, x_du_flat, x_dd_flat], dim=1)
        )
        gnn_puro_logits = self.dense_gnn_puro(
            torch.cat([x_d_flat, x_du_flat, x_dd_flat], dim=1)
        )
        spatial_logits = self.dense_spatial(spatial_flat)

        r_ent = self.entropy(F.softmax(y_sup_logits, dim=1))
        g_ent = self.entropy(F.softmax(gnn_logits, dim=1))
        gp_ent = self.entropy(F.softmax(gnn_puro_logits, dim=1))

        return self.combine(
            r_ent, g_ent, gp_ent, y_sup_logits, spatial_logits, gnn_logits, gnn_puro_logits
        )
