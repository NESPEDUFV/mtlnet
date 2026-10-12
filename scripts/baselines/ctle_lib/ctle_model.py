"""CTLE model: Context- and Time-aware Location Embedding (Lin et al., AAAI 2021).

Reference
---------
Yan Lin, Huaiyu Wan, Shengnan Guo, Youfang Lin.
"Pre-training Context and Time Aware Location Embeddings from Spatial-Temporal
Trajectories for User Next Location Prediction." AAAI 2021.
Code: https://github.com/Logan-Lin/CTLE

Faithful core
-------------
- Location token embedding table (one vector per *distinct location* — here the
  Gowalla ``placeid``), the unit CTLE pre-trains.
- A *temporal encoding* module added to each token (CTLE proposes a learnable
  continuous-time encoding; the canonical released variant is the ``temporal``
  position embedding over the discretised hour-of-day). We use the hour-of-day
  continuous Time2Vec-style sinusoid + linear (matches CTLE's "TemporalEncoding"
  spirit: a smooth, learnable function of the timestamp).
- A bidirectional Transformer encoder (``norm_first`` pre-LN) over the
  trajectory of (location_emb + temporal_emb) tokens. The encoder output at
  position i IS the *contextual* location embedding for that check-in — this is
  what makes CTLE per-visit / contextual (vs a static per-POI table).
- Two pre-training pretext heads:
    * MLM (Masked Language Model): predict the masked location id from the
      contextual output. Cross-entropy over the location vocabulary.
    * MH  (Masked Hour): predict the masked check-in's hour-of-day (24 classes)
      from the contextual output. Cross-entropy over 24 hours.
  Both share the same masking positions (BERT-style 15% mask, of which 80% ->
  [MASK], 10% random, 10% keep). MH is what makes CTLE *time-aware*.

Downstream emission
-------------------
After pre-training, we run the encoder over each user's full (UNMASKED)
trajectory and read the per-position encoder output as the 64-d contextual
check-in embedding. That is exactly CTLE's "downstream adaptation" step: feed
the pre-trained contextual location embeddings to the downstream predictor —
here the matched champion heads via the probe-engine substrate column.

Deviations (documented for the baseline audit)
----------------------------------------------
1. Downstream task = our TIGER-tract next-REGION + 7-root next-CATEGORY under the
   matched MTLnet heads, NOT CTLE's original next-location MC/RNN predictor. This
   isolates the *substrate* axis (contextualization control), the point of B1.
2. Temporal encoding: we use a Time2Vec-style continuous hour encoding (smooth,
   learnable) rather than CTLE's exact released positional-temporal variant; the
   MH objective is retained verbatim. Both are "time-aware embedding of the
   timestamp"; the substitution is a minor module swap, not an objective change.
3. Embedding dim pinned to 64 to match the board (CTLE default is 128). MLM/MH
   ratios + transformer depth/heads follow CTLE defaults (mask 0.15, 4 layers,
   8 heads, GELU, pre-LN), scaled to dim 64.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

import torch
import torch.nn as nn
import torch.nn.functional as F


# Special vocab ids reserved at the FRONT of the location vocabulary.
PAD_ID = 0      # padding token (short trajectories / right-pad)
MASK_ID = 1     # [MASK] token for MLM
N_SPECIAL = 2   # number of reserved special ids before real locations begin


@dataclass
class CTLEConfig:
    vocab_size: int          # N_SPECIAL + number of distinct locations
    embed_dim: int = 64
    n_layers: int = 4
    n_heads: int = 8
    ff_mult: int = 4
    dropout: float = 0.1
    max_len: int = 64        # max trajectory length fed to the encoder
    n_hours: int = 24        # MH classification space (hour-of-day)
    mask_ratio: float = 0.15


class TemporalEncoding(nn.Module):
    """Time2Vec-style continuous temporal encoding of hour-of-day.

    Maps a scalar hour t in [0,24) to an embed_dim vector:
      dim 0      : linear  w0*t + b0
      dim 1..D-1 : sin(w_k*t + b_k)
    Learnable frequencies/phases — the smooth, learnable temporal module CTLE
    adds to each location token. Faithful to CTLE's "time-aware" requirement.
    """

    def __init__(self, embed_dim: int):
        super().__init__()
        self.w = nn.Parameter(torch.randn(embed_dim) * 0.01)
        self.b = nn.Parameter(torch.zeros(embed_dim))

    def forward(self, hours: torch.Tensor) -> torch.Tensor:
        # hours: [B, L] float
        t = hours.unsqueeze(-1)                      # [B, L, 1]
        v = self.w * t + self.b                      # [B, L, D]
        out = v.clone()
        out[..., 1:] = torch.sin(v[..., 1:])
        return out                                   # [B, L, D]


class CTLE(nn.Module):
    """CTLE encoder + MLM/MH pretrain heads."""

    def __init__(self, cfg: CTLEConfig):
        super().__init__()
        self.cfg = cfg
        self.loc_embed = nn.Embedding(cfg.vocab_size, cfg.embed_dim, padding_idx=PAD_ID)
        self.temporal = TemporalEncoding(cfg.embed_dim)
        self.input_norm = nn.LayerNorm(cfg.embed_dim)
        self.dropout = nn.Dropout(cfg.dropout)

        layer = nn.TransformerEncoderLayer(
            d_model=cfg.embed_dim,
            nhead=cfg.n_heads,
            dim_feedforward=cfg.embed_dim * cfg.ff_mult,
            dropout=cfg.dropout,
            activation="gelu",
            batch_first=True,
            norm_first=True,
        )
        self.encoder = nn.TransformerEncoder(layer, num_layers=cfg.n_layers)

        # MLM head: contextual output -> location logits (weight-tied to loc table)
        self.mlm_head = nn.Linear(cfg.embed_dim, cfg.vocab_size, bias=True)
        self.mlm_head.weight = self.loc_embed.weight  # weight tying (BERT-style)
        # MH head: contextual output -> hour-of-day logits
        self.mh_head = nn.Linear(cfg.embed_dim, cfg.n_hours)

        nn.init.normal_(self.loc_embed.weight, std=0.02)
        with torch.no_grad():
            self.loc_embed.weight[PAD_ID].zero_()

    def encode(self, loc_ids: torch.Tensor, hours: torch.Tensor) -> torch.Tensor:
        """Return contextual per-position embeddings [B, L, D].

        loc_ids: [B, L] long (PAD_ID for padding, MASK_ID for masked positions)
        hours:   [B, L] float (hour-of-day; arbitrary at padded positions)
        """
        pad_mask = loc_ids.eq(PAD_ID)                # [B, L] True at padding
        x = self.loc_embed(loc_ids) + self.temporal(hours)
        x = self.dropout(self.input_norm(x))
        # src_key_padding_mask: True positions are ignored by attention.
        out = self.encoder(x, src_key_padding_mask=pad_mask)
        return out

    def forward(self, loc_ids, hours, mlm_targets, mh_targets, loss_mask):
        """Pretrain forward. Returns (total_loss, mlm_loss, mh_loss).

        mlm_targets: [B, L] long, original loc id at masked positions, -100 else
        mh_targets:  [B, L] long, original hour (0..23) at masked positions, -100 else
        loss_mask:   [B, L] bool, True at masked positions (for reporting only)
        """
        out = self.encode(loc_ids, hours)            # [B, L, D]
        mlm_logits = self.mlm_head(out)              # [B, L, V]
        mh_logits = self.mh_head(out)                # [B, L, 24]

        mlm_loss = F.cross_entropy(
            mlm_logits.reshape(-1, self.cfg.vocab_size),
            mlm_targets.reshape(-1),
            ignore_index=-100,
        )
        mh_loss = F.cross_entropy(
            mh_logits.reshape(-1, self.cfg.n_hours),
            mh_targets.reshape(-1),
            ignore_index=-100,
        )
        total = mlm_loss + mh_loss
        return total, mlm_loss, mh_loss


def build_mlm_mh_batch(loc_ids, hours, vocab_size, mask_ratio, generator):
    """BERT-style masking for a batch.

    loc_ids: [B, L] long (with PAD_ID padding, real ids >= N_SPECIAL)
    hours:   [B, L] long (hour-of-day)
    Returns: masked_loc_ids, mlm_targets, mh_targets, loss_mask
      - 15% of NON-PAD positions are selected; of those 80% -> [MASK],
        10% -> random real location, 10% -> unchanged.
      - mlm_targets / mh_targets carry the ORIGINAL value at selected positions,
        -100 elsewhere (ignored by CE).
    """
    device = loc_ids.device
    is_real = loc_ids.ge(N_SPECIAL)                  # only mask real locations
    prob = torch.rand(loc_ids.shape, generator=generator, device=device)
    select = (prob < mask_ratio) & is_real          # [B, L]

    masked = loc_ids.clone()
    mlm_targets = torch.full_like(loc_ids, -100)
    mh_targets = torch.full_like(loc_ids, -100)
    mlm_targets[select] = loc_ids[select]
    mh_targets[select] = hours[select]

    # 80/10/10 split among selected
    r = torch.rand(loc_ids.shape, generator=generator, device=device)
    do_mask = select & (r < 0.8)
    do_rand = select & (r >= 0.8) & (r < 0.9)
    masked[do_mask] = MASK_ID
    if do_rand.any():
        rand_ids = torch.randint(
            N_SPECIAL, vocab_size, (int(do_rand.sum().item()),),
            generator=generator, device=device,
        )
        masked[do_rand] = rand_ids
    # remaining 10% selected: keep original (already in `masked`)
    return masked, mlm_targets, mh_targets, select
