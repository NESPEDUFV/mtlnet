"""The joint model: two task encoders, a bidirectional cross-attention trunk, two heads.

Shape of one forward pass:

    category window [B,9,64] ──▶ cat encoder ──┐
                                               ├─▶ 2 × cross-attention block ──┐
    region window   [B,9,64] ──▶ reg encoder ──┘                               │
                                                                               ▼
                         cat head (GRU)  ◀── shared_cat [B,9,256]     shared_reg [B,9,256]
                                                                               │
                         reg head (dual tower) ◀───────────────────────────────┘
                              ▲
                              └── the RAW region window [B,9,64], un-mixed

The region head is the part worth reading twice. It has **two** backbones: a private one over the
raw region window — the same input the dedicated head sees — and a shared one over the trunk's
output. It fuses them additively, `feat = private + beta * project(shared)`, with `beta` learnable
from 0.1. So the trunk has to earn its contribution against a tower that already has the dedicated
model's input.

Two properties that are easy to lose and change what the model learns:

* **The second cross-attention direction reads the UPDATED first stream.** `b` queries the `a` that
  the previous line just wrote, not the `a` that entered the block. Reordering those two lines is a
  different architecture.
* **The trajectory-flow prior is absent, not zeroed** — see `stan.py` and R6.
"""

from __future__ import annotations

import torch
import torch.nn as nn

from .gru import CategoryHead
from .stan import StanBackbone


def task_encoder(in_size: int, hidden: int, out_size: int, *, num_layers: int = 2,
                 dropout: float = 0.1) -> nn.Sequential:
    """The per-task MLP encoder: `num_layers` hidden blocks, then a projection to `out_size`.

    Note the final block has a ReLU and a LayerNorm but NO dropout — asymmetric, and reproduced
    because it is what the trunk was trained with.
    """
    layers: list[nn.Module] = [
        nn.Linear(in_size, hidden), nn.ReLU(), nn.LayerNorm(hidden), nn.Dropout(dropout),
    ]
    for _ in range(num_layers - 1):
        layers += [nn.Linear(hidden, hidden), nn.ReLU(), nn.LayerNorm(hidden), nn.Dropout(dropout)]
    layers += [nn.Linear(hidden, out_size), nn.ReLU(), nn.LayerNorm(out_size)]
    return nn.Sequential(*layers)


class CrossAttentionBlock(nn.Module):
    """One bidirectional block: each stream attends to the other, then its own feed-forward."""

    def __init__(self, dim: int, num_heads: int, *, ffn_dim: int | None = None,
                 dropout: float = 0.15) -> None:
        super().__init__()
        ffn_dim = ffn_dim or dim
        self.cross_ab = nn.MultiheadAttention(dim, num_heads, dropout=dropout, batch_first=True)
        self.cross_ba = nn.MultiheadAttention(dim, num_heads, dropout=dropout, batch_first=True)
        self.ln_a1 = nn.LayerNorm(dim)
        self.ln_b1 = nn.LayerNorm(dim)
        self.ln_a2 = nn.LayerNorm(dim)
        self.ln_b2 = nn.LayerNorm(dim)
        self.ffn_a = _ffn(dim, ffn_dim, dropout)
        self.ffn_b = _ffn(dim, ffn_dim, dropout)

    def forward(self, a: torch.Tensor, b: torch.Tensor, *,
                a_pad_mask: torch.Tensor | None = None,
                b_pad_mask: torch.Tensor | None = None) -> tuple[torch.Tensor, torch.Tensor]:
        a_update, _ = self.cross_ab(query=a, key=b, value=b, key_padding_mask=b_pad_mask)
        a = self.ln_a1(a + a_update)

        # `b` queries the UPDATED `a`. The two streams converge within the block rather than
        # exchanging their entry states — swap this for the pre-update `a` and it is a different
        # architecture that trains and scores without complaint.
        b_update, _ = self.cross_ba(query=b, key=a, value=a, key_padding_mask=a_pad_mask)
        b = self.ln_b1(b + b_update)

        a = self.ln_a2(a + self.ffn_a(a))
        b = self.ln_b2(b + self.ffn_b(b))
        return a, b


def _ffn(dim: int, hidden: int, dropout: float) -> nn.Sequential:
    return nn.Sequential(
        nn.Linear(dim, hidden), nn.GELU(), nn.Dropout(dropout),
        nn.Linear(hidden, dim), nn.Dropout(dropout),
    )


class DualTowerRegionHead(nn.Module):
    """Region head with a private tower on the raw window and a shared tower on the trunk output."""

    def __init__(self, shared_dim: int, num_classes: int, *, raw_embed_dim: int = 64,
                 seq_length: int = 9, d_model: int = 128, shared_heads: int = 8,
                 shared_dropout: float = 0.1, private_heads: int = 4,
                 private_dropout: float = 0.3) -> None:
        super().__init__()
        # Both towers pool to [B, d_model]; neither owns a classifier, so the fused feature is
        # projected once instead of twice.
        self.private_stan = StanBackbone(raw_embed_dim, num_classes, seq_length=seq_length,
                                         d_model=d_model, num_heads=private_heads,
                                         dropout=private_dropout)
        self.private_stan.classifier = nn.Identity()
        self.shared_stan = StanBackbone(shared_dim, num_classes, seq_length=seq_length,
                                        d_model=d_model, num_heads=shared_heads,
                                        dropout=shared_dropout)
        self.shared_stan.classifier = nn.Identity()

        self.aux_proj = nn.Linear(d_model, d_model)
        self.beta = nn.Parameter(torch.tensor(0.1))
        self.classifier = nn.Sequential(
            nn.LayerNorm(d_model), nn.Dropout(shared_dropout), nn.Linear(d_model, num_classes),
        )

    def forward(self, shared: torch.Tensor, raw_region: torch.Tensor) -> torch.Tensor:
        if raw_region is None:
            # The reference zero-fills the private tower when its input is missing, which turns a
            # plumbing mistake into a quietly halved model. An absent input is an error here (R12).
            raise ValueError("the private tower needs the raw region window; none was passed")
        private = self.private_stan.features(raw_region)
        shared_feat = self.shared_stan.features(shared)
        return self.classifier(private + self.beta * self.aux_proj(shared_feat))


class JointModel(nn.Module):
    """Two encoders, a cross-attention trunk, and the two task heads."""

    def __init__(self, *, feature_size: int = 64, shared_dim: int = 256,
                 n_categories: int = 7, n_regions: int = 1109, seq_length: int = 9,
                 num_heads: int = 4,       # the TRUNK's head count. The reference's model-level
                                           # num_heads=8 is injected into the dual-tower's SHARED
                                           # STAN, not into the cross-attention blocks, whose own
                                           # default is 4 and which no v18 driver overrides.
                 num_blocks: int = 2, encoder_hidden: int = 256,
                 num_encoder_layers: int = 2, encoder_dropout: float = 0.1,
                 trunk_dropout: float = 0.15, cat_head_params: dict | None = None,
                 reg_head_params: dict | None = None) -> None:
        super().__init__()
        self.category_encoder = task_encoder(feature_size, encoder_hidden, shared_dim,
                                             num_layers=num_encoder_layers,
                                             dropout=encoder_dropout)
        self.region_encoder = task_encoder(feature_size, encoder_hidden, shared_dim,
                                           num_layers=num_encoder_layers,
                                           dropout=encoder_dropout)
        self.blocks = nn.ModuleList([
            CrossAttentionBlock(shared_dim, num_heads, ffn_dim=shared_dim, dropout=trunk_dropout)
            for _ in range(num_blocks)
        ])
        self.cat_final_ln = nn.LayerNorm(shared_dim)
        self.reg_final_ln = nn.LayerNorm(shared_dim)

        self.category_head = CategoryHead(shared_dim, n_categories,
                                          **_head_kwargs(cat_head_params, CategoryHead))
        reg_kwargs = _head_kwargs(reg_head_params, DualTowerRegionHead)
        reg_kwargs.setdefault("raw_embed_dim", feature_size)
        reg_kwargs.setdefault("seq_length", seq_length)
        self.region_head = DualTowerRegionHead(shared_dim, n_regions, **reg_kwargs)

    def forward(self, category_input: torch.Tensor,
                region_input: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor]:
        cat_mask = _pad_mask(category_input)
        reg_mask = _pad_mask(region_input)
        category_input = category_input.masked_fill(cat_mask.unsqueeze(-1), 0)
        region_input = region_input.masked_fill(reg_mask.unsqueeze(-1), 0)

        a = self.category_encoder(category_input)
        b = self.region_encoder(region_input)
        for block in self.blocks:
            a, b = block(a, b, a_pad_mask=cat_mask, b_pad_mask=reg_mask)

        shared_cat = self.cat_final_ln(a).masked_fill(cat_mask.unsqueeze(-1), 0)
        shared_reg = self.reg_final_ln(b).masked_fill(reg_mask.unsqueeze(-1), 0)

        return (self.category_head(shared_cat),
                self.region_head(shared_reg, raw_region=region_input))

    def shared_parameters(self):
        """The trunk ONLY: cross-attention blocks and the two final norms.

        The task encoders are deliberately NOT here. The reference groups each encoder with its own
        head — cat encoder + cat head at `cat_lr`, region encoder + region head at `reg_lr` — and
        leaves only the blocks and final norms shared. Putting the encoders here instead trains the
        region encoder at the shared rate (1e-3) where v18 trains it at 3e-3, a 3x difference at
        every state, with every coverage and bijectivity check still passing.
        """
        yield from self.blocks.parameters()
        yield from self.cat_final_ln.parameters()
        yield from self.reg_final_ln.parameters()

    def shared_parameter_groups(self):
        """The trunk, split into the groups the gradient probe reports separately.

        `a` is the category stream and `b` the region stream, so `cross_ab`/`ffn_a` update the
        category side of the trunk and `cross_ba`/`ffn_b` the region side. That split is the point:
        a "shared" trunk whose two halves each serve one task is functionally two private
        half-trunks, and only a per-group reading can tell that apart from genuine sharing.
        """
        groups: dict[str, list] = {"cross_ab": [], "cross_ba": [], "ffn_a": [], "ffn_b": [],
                                   "norms": [], "final_ln": []}
        for block in self.blocks:
            groups["cross_ab"] += list(block.cross_ab.parameters())
            groups["cross_ba"] += list(block.cross_ba.parameters())
            groups["ffn_a"] += list(block.ffn_a.parameters())
            groups["ffn_b"] += list(block.ffn_b.parameters())
            for norm in (block.ln_a1, block.ln_b1, block.ln_a2, block.ln_b2):
                groups["norms"] += list(norm.parameters())
        groups["final_ln"] = list(self.cat_final_ln.parameters()) + list(self.reg_final_ln.parameters())
        return {name: params for name, params in groups.items() if params}

    def category_parameters(self):
        """Category encoder + category head."""
        yield from self.category_encoder.parameters()
        yield from self.category_head.parameters()

    def region_parameters(self):
        """Region encoder + region head, private tower included."""
        yield from self.region_encoder.parameters()
        yield from self.region_head.parameters()


def _head_kwargs(params: dict | None, cls) -> dict:
    """Recipe entries a head accepts, with the inert-prior markers checked and dropped.

    `freeze_alpha` / `alpha_init` describe the trajectory-flow prior, which this port implements as
    an ABSENT branch rather than a multiply by zero. They are therefore not constructor arguments —
    but a recipe asking for an ACTIVE prior must not be silently built without one, so the values
    are verified before they are dropped.
    """
    params = dict(params or {})
    freeze = params.pop("freeze_alpha", True)
    alpha = params.pop("alpha_init", 0.0)
    if not (freeze and float(alpha) == 0.0):
        raise ValueError(
            f"the recipe asks for an ACTIVE trajectory-flow prior (freeze_alpha={freeze}, "
            f"alpha_init={alpha}), which this port does not implement. Building without it would "
            f"be a silently different model."
        )
    import inspect
    accepted = set(inspect.signature(cls.__init__).parameters)
    unexpected = set(params) - accepted
    if unexpected:
        raise ValueError(f"{cls.__name__} does not accept {sorted(unexpected)}")
    return params


def _pad_mask(x: torch.Tensor) -> torch.Tensor:
    return x.abs().sum(dim=-1) == 0


__all__ = ["JointModel", "DualTowerRegionHead", "CrossAttentionBlock", "task_encoder"]
