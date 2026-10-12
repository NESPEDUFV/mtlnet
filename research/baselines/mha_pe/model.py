"""Faithful MHA+PE port (Zeng, He, Tang, Wen 2019, IDEAL).

Mirror of ``nest_poi/tcc_pedro/src/model/next_pytorch_new.py::NEXT``:

  * Sinusoidal positional encoding added to category(7-d) and hour(3-d)
    embeddings.
  * GRU(in=10, hidden=22) over the concatenated 9-d input.
  * Multi-head self-attention over the GRU output.
  * Concat [MHA_out, spatial_emb_with_PE, hour_emb_with_PE] per
    timestep, flatten, Linear → n_categories logits.

Adaptations (documented in ``mha_pe.md``):

  * **Drop user embedding.** Reference uses 2-d learned per-user
    embedding concatenated to GRU output before MHA, evaluated under
    warm-user splits. Cold-user StratifiedGroupKFold makes a per-user
    embedding random for held-out users → noise. Dropped to avoid
    pretending we have signal we don't (same reasoning as Faithful
    STAN). MHA `embed_dim` becomes 22 (was 24); `num_heads=2` so
    head_dim=11 stays integer.
  * **Output LOGITS, not softmax probabilities.** Reference applies
    `F.softmax` in `forward` (correct for Keras CCE; double-softmax
    bug under PyTorch CE). We output raw logits + use
    `nn.CrossEntropyLoss`.
"""

from __future__ import annotations

import math

import torch
import torch.nn as nn


class _PositionalEncoding(nn.Module):
    def __init__(self, maxlen: int, d_model: int):
        super().__init__()
        pe = torch.zeros(maxlen, d_model)
        position = torch.arange(0, maxlen, dtype=torch.float).unsqueeze(1)
        div_term = torch.exp(
            torch.arange(0, d_model, 2).float()
            * (-math.log(10000.0) / d_model)
        )
        pe[:, 0::2] = torch.sin(position * div_term[: (d_model + 1) // 2])
        pe[:, 1::2] = torch.cos(position * div_term[: d_model // 2])
        self.register_buffer("pe", pe.unsqueeze(0))

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return x + self.pe[:, : x.size(1)]


class MHAPE(nn.Module):
    def __init__(
        self,
        n_categories: int = 7,
        step_size: int = 8,
        d_cat: int = 7,
        d_hour: int = 3,
        gru_hidden: int = 22,
        n_heads: int = 2,
        dropout: float = 0.5,
    ):
        super().__init__()
        if gru_hidden % n_heads != 0:
            raise ValueError(
                f"gru_hidden ({gru_hidden}) must be divisible by n_heads ({n_heads})"
            )

        self.cat_emb = nn.Embedding(n_categories, d_cat)
        self.hour_emb = nn.Embedding(48, d_hour)
        self.pe_cat = _PositionalEncoding(maxlen=step_size, d_model=d_cat)
        self.pe_hour = _PositionalEncoding(maxlen=step_size, d_model=d_hour)

        self.gru = nn.GRU(d_cat + d_hour, gru_hidden, batch_first=True)
        self.dropout = nn.Dropout(dropout)
        self.mha = nn.MultiheadAttention(
            embed_dim=gru_hidden, num_heads=n_heads, batch_first=True
        )
        self.head = nn.Linear(
            (gru_hidden + d_cat + d_hour) * step_size, n_categories
        )

    def forward(self, cat: torch.Tensor, hour: torch.Tensor) -> torch.Tensor:
        # cat / hour: [B, T] long
        s = self.pe_cat(self.cat_emb(cat))           # [B, T, 7]
        h = self.pe_hour(self.hour_emb(hour))        # [B, T, 3]
        x = torch.cat([s, h], dim=-1)                # [B, T, 10]
        gru_out, _ = self.gru(x)                     # [B, T, 22]
        gru_out = self.dropout(gru_out)
        attn_out, _ = self.mha(gru_out, gru_out, gru_out)  # [B, T, 22]
        feat = torch.cat([attn_out, s, h], dim=-1)   # [B, T, 32]
        flat = feat.reshape(feat.size(0), -1)
        flat = self.dropout(flat)
        return self.head(flat)
