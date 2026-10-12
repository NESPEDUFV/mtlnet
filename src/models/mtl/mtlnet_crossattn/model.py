"""Cross-attention MTLnet variant.

Replaces the shared-backbone architecture (FiLM + residual stack) with
two parallel task streams that exchange information via cross-attention.
Each cross-attention block is bidirectional: task A queries task B's
keys/values, task B queries task A's. No parameter sharing across
tasks (each stream keeps its own FFN); information sharing is
content-based via attention instead of parameter-based via shared
layers.

Rationale: the shared-backbone MTL architecture exhibits a
capacity-ceiling property (see docs/issues/check2hgi/
BACKBONE_DILUTION.md + FINAL_ABLATION_SUMMARY.md). Our λ=0.0 isolation
shows 5.4 pp of the 8 pp STL → MTL gap is architectural overhead from
the shared backbone. Cross-attention removes the shared backbone
entirely, keeping only per-task streams that cross-attend. Expected
lift per research/SOTA_MTL_ALTERNATIVES_V2.md: +3–5 pp region Acc@10.

Inductive bias: FiLM modulates a shared representation with a scalar
conditioned on task identity; cross-attention modulates with *content*.
For heterogeneous-input MTL (per-task modality = our P4 winner),
cross-attention is the natural generalisation.

References:
- MulT (Tsai et al., ACL 2019, arXiv:1906.00295) — canonical
  cross-modal transformer.
- InvPT (Ye & Xu, ECCV 2022, arXiv:2203.07997) — MTL dense prediction
  with task-interaction blocks.
"""

from __future__ import annotations

from typing import Any, Iterator, Optional, Tuple

import torch
from torch import nn

from configs.model import InputsConfig
from models.mtl.mtlnet.model import MTLnet
from models.registry import register_model
from tasks import LEGACY_CATEGORY_NEXT, TaskSet


def _masked_mean_seq(x: torch.Tensor, pad_mask: Optional[torch.Tensor]) -> torch.Tensor:
    """Mean over the sequence dim [B,T,D]→[B,D], skipping padded steps.
    ``pad_mask`` is True at padded positions (MultiheadAttention convention)."""
    if pad_mask is None:
        return x.mean(dim=1)
    keep = (~pad_mask).unsqueeze(-1).to(x.dtype)        # [B,T,1]
    denom = keep.sum(dim=1).clamp_min(1.0)              # [B,1]
    return (x * keep).sum(dim=1) / denom


class _CrossAttnBlock(nn.Module):
    """One bidirectional cross-attention + FFN block.

    Forward takes two streams `a` and `b` of shape [B, T, D]:
      a ← LN( a + CrossAttn(Q=a, K=b, V=b) )
      b ← LN( b + CrossAttn(Q=b, K=a, V=a) )
      a ← LN( a + FFN(a) )
      b ← LN( b + FFN(b) )

    Separate FFNs per task, no parameter sharing. Pad masks
    (`a_pad_mask`, `b_pad_mask`) are True where the step is padding
    so attention skips those positions.
    """

    def __init__(
        self,
        dim: int,
        num_heads: int,
        ffn_dim: int,
        dropout: float,
        detach_kv: bool = False,
        identity_attn: bool = False,
        zero_cat_kv: bool = False,
        detach_ab: bool = False,
        detach_ba: bool = False,
        grm_gate: bool = False,
    ):
        super().__init__()
        self.detach_kv = bool(detach_kv)
        # R10 (mtl_frontier) — Gated Residual Memory read (arXiv:2602.24281 primitive,
        # "on the layers"). Per-sample, per-dim input-dependent gate γ∈[0,1]^d on each
        # stream's cross-attn read of the OTHER stream: a ← LN(a + γ_a⊙CrossAttn(a,b)).
        # γ_a = σ(W_a · masked-mean_seq(a)). A continuous, input-conditioned
        # generalization of R2's binary detach masks (R2 gated the gradient; GRM gates
        # the forward read magnitude, gradient flows through γ). Bias init +2 → γ≈0.88
        # so the untrained block ≈ champion G (full read), with room to modulate down.
        self.grm_gate = bool(grm_gate)
        if self.grm_gate:
            self.grm_a = nn.Linear(dim, dim)
            self.grm_b = nn.Linear(dim, dim)
            nn.init.constant_(self.grm_a.bias, 2.0)
            nn.init.constant_(self.grm_b.bias, 2.0)
            # R10 diagnostic — last-batch mean γ per stream (detached floats), so
            # the trainer can log the TRAINED gate trajectory (init≈0.88; if it
            # stays ≈0.88 the gate found no reason to modulate, if it moves the
            # gate learned input-conditioning — either way a non-trivial null check).
            self.last_gamma_a = None
            self.last_gamma_b = None
        # R2 (mtl_frontier) STEM-AFTB — DIRECTIONAL stop-grad, per block.
        #   detach_ab: detach b's (reg) K/V in cross_ab (Q=cat) → cat reads reg
        #     forward-only; L_cat does NOT backprop into the reg pathway here.
        #   detach_ba: detach a's (cat) K/V in cross_ba (Q=reg) → reg reads cat
        #     forward-only; L_reg does NOT backprop into the cat pathway here.
        # detach_kv=True is the symmetric both-directions case (F50 P2) and is
        # honored as (detach_ab=detach_ba=True). All-Forward Task-specific-Backward
        # (STEM, AAAI'24) = both True at every block.
        self.detach_ab = bool(detach_ab) or self.detach_kv
        self.detach_ba = bool(detach_ba) or self.detach_kv
        # substrate-protocol-cleanup Tier C3 — runtime ablation that zeroes
        # the cat-stream K/V tensors before they participate in
        # ``cross_ab`` (Q from reg queries cat keys/values). Reg-side K/V
        # (used by ``cross_ba``) stays intact. Forward-only ablation
        # (reversible by flag); projection weights are NOT zeroed. See
        # ``docs/studies/substrate-protocol-cleanup/INDEX.md`` §C3.
        self.zero_cat_kv = bool(zero_cat_kv)
        # F52 P5 — when ``identity_attn`` is set, the cross-attention output
        # is replaced with zero so the residual `a + a_upd` reduces to `a`.
        # Per-task FFNs and LayerNorms still run. Decomposes "is the
        # productive part of the cross-attn block the K/V mixing or just
        # the FFN+LN structure?" If P5 ≈ H3-alt, mixing is dead. If
        # P5 ≈ P1 (no_crossattn), even the FFN+LN doesn't add value.
        self.identity_attn = bool(identity_attn)
        self.cross_ab = nn.MultiheadAttention(
            dim, num_heads, dropout=dropout, batch_first=True
        )
        self.cross_ba = nn.MultiheadAttention(
            dim, num_heads, dropout=dropout, batch_first=True
        )
        self.ln_a1 = nn.LayerNorm(dim)
        self.ln_b1 = nn.LayerNorm(dim)
        self.ln_a2 = nn.LayerNorm(dim)
        self.ln_b2 = nn.LayerNorm(dim)
        self.ffn_a = nn.Sequential(
            nn.Linear(dim, ffn_dim),
            nn.GELU(),
            nn.Dropout(dropout),
            nn.Linear(ffn_dim, dim),
            nn.Dropout(dropout),
        )
        self.ffn_b = nn.Sequential(
            nn.Linear(dim, ffn_dim),
            nn.GELU(),
            nn.Dropout(dropout),
            nn.Linear(ffn_dim, dim),
            nn.Dropout(dropout),
        )

    def forward(
        self,
        a: torch.Tensor,
        b: torch.Tensor,
        a_pad_mask: Optional[torch.Tensor] = None,
        b_pad_mask: Optional[torch.Tensor] = None,
    ) -> Tuple[torch.Tensor, torch.Tensor]:
        # F50 P2 — when ``detach_kv`` is set, .detach() K/V so gradients from
        # L_reg do NOT flow back through cross_ba into category_encoder (and
        # symmetrically L_cat does not flow into next_encoder). Direct test of
        # the F49 Layer 2 silent-gradient mechanism under full-MTL training.
        if self.identity_attn:
            # F52 P5 — short-circuit cross-attention output to zero. Streams
            # pass through ln_a1/ln_b1 + per-task FFN+ln_a2/ln_b2 only.
            a = self.ln_a1(a)
            b = self.ln_b1(b)
        else:
            kv_b = b.detach() if self.detach_ab else b
            a_upd, _ = self.cross_ab(
                query=a, key=kv_b, value=kv_b, key_padding_mask=b_pad_mask
            )
            if self.grm_gate:
                # γ_a from a's pre-update masked-mean → how much a reads from b.
                _ga = torch.sigmoid(self.grm_a(_masked_mean_seq(a, a_pad_mask)))
                self.last_gamma_a = float(_ga.detach().mean())
                a_upd = _ga.unsqueeze(1) * a_upd
            a = self.ln_a1(a + a_upd)
            # b queries a (uses updated a as K/V so the two streams converge
            # symmetrically; this is MulT's "late" bidirectional pattern)
            kv_a = a.detach() if self.detach_ba else a
            # substrate-protocol-cleanup Tier C3 — zero the cat-stream K/V
            # tensors going into ``cross_ba`` (where reg's Q queries cat's
            # K/V). Forward-only ablation: weights of self.cross_ba.in_proj
            # are untouched, only the K/V activations from cat are
            # silenced. softmax(Q K^T) V then reduces to zero regardless
            # of Q, so cat contributes nothing to reg's update via this
            # path. The reciprocal cross_ab (Q=cat queries reg's K/V) is
            # left intact — the test target is reg dynamics under a cat-
            # silenced K/V channel, not a fully decoupled stream.
            if self.zero_cat_kv:
                kv_a = torch.zeros_like(kv_a)
            b_upd, _ = self.cross_ba(
                query=b, key=kv_a, value=kv_a, key_padding_mask=a_pad_mask
            )
            if self.grm_gate:
                _gb = torch.sigmoid(self.grm_b(_masked_mean_seq(b, b_pad_mask)))
                self.last_gamma_b = float(_gb.detach().mean())
                b_upd = _gb.unsqueeze(1) * b_upd
            b = self.ln_b1(b + b_upd)
        # Per-stream FFN
        a = self.ln_a2(a + self.ffn_a(a))
        b = self.ln_b2(b + self.ffn_b(b))
        return a, b


@register_model("mtlnet_crossattn")
class MTLnetCrossAttn(MTLnet):
    """MTLnet variant using cross-attention between task streams.

    Construction mostly inherits from MTLnet (task encoders, heads,
    register of task_set etc.). `_build_shared_backbone` is overridden
    to register cross-attention blocks in place of FiLM + shared_layers.
    `forward` is overridden to route through the cross-attention stack.
    """

    def __init__(
        self,
        feature_size: int,
        shared_layer_size: int,
        num_classes: int,
        num_heads: int,
        num_layers: int,
        seq_length: int,
        num_shared_layers: int,
        encoder_layer_size: int = 256,
        num_encoder_layers: int = 2,
        encoder_dropout: float = 0.1,
        shared_dropout: float = 0.15,
        num_crossattn_blocks: int = 2,
        num_crossattn_heads: int = 4,
        crossattn_ffn_dim: Optional[int] = None,
        detach_crossattn_kv: bool = False,
        aftb_spec: Optional[str] = None,
        crossattn_grm: bool = False,
        disable_cross_attn: bool = False,
        identity_cross_attn: bool = False,
        zero_cat_kv: bool = False,
        no_task_encoders: bool = False,
        linear_encoders: bool = False,
        linear_ln_encoders: bool = False,
        category_head: Optional[str] = None,
        next_head: Optional[str] = None,
        category_head_params: Optional[dict[str, Any]] = None,
        next_head_params: Optional[dict[str, Any]] = None,
        task_set: Optional[TaskSet] = None,
    ):
        self._num_crossattn_blocks = int(num_crossattn_blocks)
        self._num_crossattn_heads = int(num_crossattn_heads)
        self._crossattn_ffn_dim = (
            int(crossattn_ffn_dim) if crossattn_ffn_dim is not None else int(shared_layer_size)
        )
        self._detach_crossattn_kv = bool(detach_crossattn_kv)
        # R2 (mtl_frontier) STEM-AFTB spec — per-block directional stop-grad.
        # Format: comma-separated per-block tokens, each a '+'-join of directions
        # from {ab, ba} (or 'none'/'' for no detach). 'ab' = cat reads reg
        # forward-only (detach reg K/V in cross_ab); 'ba' = reg reads cat
        # forward-only (detach cat K/V in cross_ba). Length MUST equal
        # num_crossattn_blocks. None → no AFTB (champion G). detach_crossattn_kv
        # (symmetric, all-blocks) still works and is OR-ed in per block.
        self._aftb_per_block = self._parse_aftb_spec(
            aftb_spec, int(num_crossattn_blocks)
        )
        self._crossattn_grm = bool(crossattn_grm)   # R10 GRM-gated read
        self._disable_cross_attn = bool(disable_cross_attn)
        self._identity_cross_attn = bool(identity_cross_attn)
        self._zero_cat_kv = bool(zero_cat_kv)
        self._no_task_encoders = bool(no_task_encoders)
        self._linear_encoders = bool(linear_encoders)
        self._linear_ln_encoders = bool(linear_ln_encoders)
        if self._disable_cross_attn and self._identity_cross_attn:
            raise ValueError(
                "disable_cross_attn and identity_cross_attn are mutually exclusive"
            )
        _enc_modes = sum(int(x) for x in (self._no_task_encoders, self._linear_encoders, self._linear_ln_encoders))
        if _enc_modes > 1:
            raise ValueError(
                "no_task_encoders, linear_encoders, linear_ln_encoders are mutually exclusive"
            )
        if self._no_task_encoders and feature_size != shared_layer_size:
            raise ValueError(
                f"no_task_encoders=True requires feature_size == shared_layer_size; "
                f"got feature_size={feature_size}, shared_layer_size={shared_layer_size}. "
                f"Pass --model-param shared_layer_size={feature_size} to align them."
            )
        super().__init__(
            feature_size=feature_size,
            shared_layer_size=shared_layer_size,
            num_classes=num_classes,
            num_heads=num_heads,
            num_layers=num_layers,
            seq_length=seq_length,
            num_shared_layers=num_shared_layers,
            encoder_layer_size=encoder_layer_size,
            num_encoder_layers=num_encoder_layers,
            encoder_dropout=encoder_dropout,
            shared_dropout=shared_dropout,
            category_head=category_head,
            next_head=next_head,
            category_head_params=category_head_params,
            next_head_params=next_head_params,
            task_set=task_set,
        )
        if self._no_task_encoders:
            # mtl-exploration smoke (2026-05-14): replace per-task MLP encoders
            # with identity to feed raw 64-dim embeddings directly into the
            # cross-attention stack. Requires feature_size == shared_layer_size
            # (checked above). Heads receive embed_dim = feature_size and project
            # internally (next_stan_flow: Linear(embed_dim, d_model);
            # next_gru: GRU(input_size=embed_dim, hidden_size=hidden_dim)).
            self.category_encoder = nn.Identity()
            self.next_encoder = nn.Identity()
        elif self._linear_encoders:
            # mtl-exploration cells B+C (2026-05-15): replace per-task 2-layer
            # MLP encoder with a single nn.Linear(feature_size, shared_layer_size).
            # No ReLU / LayerNorm / Dropout — purely linear projection. Isolates
            # whether the encoder's non-linearity/depth or its dim-lift is what
            # the AZ/FL Δ depends on (paired with shared_layer_size choice).
            self.category_encoder = nn.Linear(feature_size, shared_layer_size)
            self.next_encoder = nn.Linear(feature_size, shared_layer_size)
        elif self._linear_ln_encoders:
            # mtl-exploration cell E (2026-05-15): Linear + LayerNorm, no
            # non-linearity. Thin hybrid between cell C (Linear only) and the
            # baseline 2-MLP. Tests whether the LayerNorm in the original
            # encoder is what recovers the small (~0.2 pp) cat lift over
            # cell C at AZ. If yes, the encoder MLP simplifies to
            # ``Linear → LayerNorm`` (saves ~150K params per encoder vs
            # baseline; ~0 extra params vs cell C plus a single LN).
            self.category_encoder = nn.Sequential(
                nn.Linear(feature_size, shared_layer_size),
                nn.LayerNorm(shared_layer_size),
            )
            self.next_encoder = nn.Sequential(
                nn.Linear(feature_size, shared_layer_size),
                nn.LayerNorm(shared_layer_size),
            )

    @staticmethod
    def _parse_aftb_spec(spec, num_blocks: int):
        """Parse an AFTB spec string → list of (detach_ab, detach_ba) per block.

        ``None`` / '' → all-False (champion G, full bidirectional gradient).
        Else comma-separated per-block tokens; each token is a '+'-join of
        {ab, ba} (or 'none'). Length must equal ``num_blocks``.
        """
        if spec is None or str(spec).strip() == "":
            return [(False, False)] * num_blocks
        tokens = [t.strip().lower() for t in str(spec).split(",")]
        if len(tokens) != num_blocks:
            raise ValueError(
                f"aftb_spec has {len(tokens)} blocks but num_crossattn_blocks="
                f"{num_blocks}; spec={spec!r}. One comma-separated token per block."
            )
        out = []
        for tok in tokens:
            dirs = set() if tok in ("none", "") else {d.strip() for d in tok.split("+")}
            bad = dirs - {"ab", "ba"}
            if bad:
                raise ValueError(f"aftb_spec token {tok!r} has bad directions {bad}; use ab/ba/none")
            out.append(("ab" in dirs, "ba" in dirs))
        return out

    def _build_shared_backbone(
        self,
        shared_layer_size: int,
        num_shared_layers: int,
        shared_dropout: float,
    ) -> None:
        """Override MTLnet's FiLM + shared_layers with cross-attention blocks."""
        # We don't use FiLM or a residual stack. Each task stream keeps
        # its encoder output; cross-attention exchanges content.
        self.crossattn_blocks = nn.ModuleList(
            [
                _CrossAttnBlock(
                    dim=shared_layer_size,
                    num_heads=self._num_crossattn_heads,
                    ffn_dim=self._crossattn_ffn_dim,
                    dropout=shared_dropout,
                    detach_kv=self._detach_crossattn_kv,
                    identity_attn=self._identity_cross_attn,
                    zero_cat_kv=self._zero_cat_kv,
                    detach_ab=self._aftb_per_block[i][0],
                    detach_ba=self._aftb_per_block[i][1],
                    grm_gate=self._crossattn_grm,
                )
                for i in range(self._num_crossattn_blocks)
            ]
        )
        if self._crossattn_grm:
            import logging as _lg
            _lg.getLogger(__name__).info(
                "[R10 GRM] input-dependent gated cross-attn read ENABLED "
                "(%d blocks, per-dim γ init≈0.88).", self._num_crossattn_blocks)
        if any(ab or ba for ab, ba in self._aftb_per_block):
            import logging as _logging
            _logging.getLogger(__name__).info(
                "[R2 AFTB] per-block (detach_ab, detach_ba): %s "
                "(ab=cat-reads-reg-readonly, ba=reg-reads-cat-readonly)",
                self._aftb_per_block,
            )
        # Final layer norms on each stream
        self.cat_final_ln = nn.LayerNorm(shared_layer_size)
        self.next_final_ln = nn.LayerNorm(shared_layer_size)

    def forward(
        self,
        inputs: Tuple[torch.Tensor, torch.Tensor],
    ) -> Tuple[torch.Tensor, torch.Tensor]:
        category_input, next_input = inputs

        pad_value = InputsConfig.PAD_VALUE
        mask = (next_input.abs().sum(dim=-1) == pad_value)
        next_input = next_input.masked_fill(mask.unsqueeze(-1), 0)

        mask_a = None
        if self._task_a_is_sequential:
            mask_a = (category_input.abs().sum(dim=-1) == pad_value)
            category_input = category_input.masked_fill(mask_a.unsqueeze(-1), 0)

        enc_cat = self.category_encoder(category_input)
        enc_next = self.next_encoder(next_input)

        # Run cross-attention stack. mask_a / mask are True at padding
        # positions, which is what MultiheadAttention's key_padding_mask
        # expects. F50 P1: when ``disable_cross_attn`` is set, skip the
        # entire cross-attn stack (incl. per-task FFNs that live inside
        # each block) — pure parallel encoders → final LN → heads. Tests
        # whether the cross-attn shared layer is contributing at FL or
        # is null/hurting.
        a, b = enc_cat, enc_next
        if not self._disable_cross_attn:
            for block in self.crossattn_blocks:
                a, b = block(
                    a, b,
                    a_pad_mask=mask_a if self._task_a_is_sequential else None,
                    b_pad_mask=mask,
                )

        shared_cat = self.cat_final_ln(a)
        shared_next = self.next_final_ln(b)

        # Re-zero at original pad positions (same pattern as other MTL
        # variants) so sequential heads (GRU, LSTM, TCN) that rely on
        # x.abs().sum(-1) == 0 to identify padding still work correctly.
        if self._task_set is not LEGACY_CATEGORY_NEXT:
            shared_next = shared_next.masked_fill(mask.unsqueeze(-1), 0)
            if self._task_a_is_sequential and mask_a is not None:
                shared_cat = shared_cat.masked_fill(mask_a.unsqueeze(-1), 0)

        if self._task_a_is_sequential:
            out_cat = self.category_poi(shared_cat)
        else:
            out_cat = self.category_poi(shared_cat.squeeze(1)).view(
                -1, self.num_classes_task_a
            )
        # Residual skip: if the reg head has been built with
        # `enable_residual_skip=True`, hand it the raw next_input alongside
        # the shared backbone output. Lets the head reach back to the
        # un-mixed region-identity signal that the cross-attn backbone
        # strips. See `docs/findings/B9_STL_STAN_SWAP_AZ_FL.md`
        # Round 2 — the MTL→STL gap on reg is largely architectural.
        if getattr(self.next_poi, "_uses_residual", False):
            out_next = self.next_poi(shared_next, residual_input=next_input)
        else:
            out_next = self.next_poi(shared_next)
        return out_cat, out_next

    def cat_forward(self, category_input: torch.Tensor) -> torch.Tensor:
        """Run the category subgraph with a zero-B stream.

        The inherited ``MTLnet.cat_forward`` references ``self.film`` /
        ``self.shared_layers`` which do not exist on this subclass — see
        ``docs/issues/check2hgi/CROSSATTN_PARTIAL_FORWARD_CRASH.md``.
        This override feeds a zero-valued, fully-padded B stream into the
        cross-attention stack, which makes the B contribution to A's
        representation an exact zero (the cross-attention block's
        ``key_padding_mask`` masks the entire B side, so the attention
        output over B is zero; the block's per-stream FFN still runs).

        NOT bit-exact with ``forward((cat, real_b))[0]`` — cross-attention
        genuinely mixes the two streams during joint training. This is a
        deterministic "cat-only" approximation useful for isolating the A
        head in evaluation; callers that need the joint output must call
        ``forward((cat, next))[0]`` directly.
        """
        pad_value = InputsConfig.PAD_VALUE
        mask_a = None
        if self._task_a_is_sequential:
            mask_a = (category_input.abs().sum(dim=-1) == pad_value)
            category_input = category_input.masked_fill(mask_a.unsqueeze(-1), 0)

        enc_cat = self.category_encoder(category_input)
        # Synthetic zero B stream matching cross-attention's expected
        # shape ``[B, T, D]`` for sequential task A (or ``[B, 1, D]``
        # when A is flat). Using V = 0 drives attention's
        # ``softmax(QKᵀ) @ V`` contribution from B to exactly zero
        # without needing a fully-True key_padding_mask (which triggers
        # softmax-over-all-masked → NaN in PyTorch's MHA).
        t_b = enc_cat.size(1) if enc_cat.dim() == 3 else 1
        enc_next = torch.zeros(
            enc_cat.size(0), t_b, enc_cat.size(-1),
            device=enc_cat.device, dtype=enc_cat.dtype,
        )
        if enc_cat.dim() == 2:
            enc_cat = enc_cat.unsqueeze(1)

        a, b = enc_cat, enc_next
        if not self._disable_cross_attn:
            for block in self.crossattn_blocks:
                # No b_pad_mask — the zero values of B already zero the A ← B
                # attention output, and a fully-True pad mask would NaN the
                # B ← A softmax for the B stream.
                a, b = block(a, b, a_pad_mask=mask_a, b_pad_mask=None)
        shared_cat = self.cat_final_ln(a)

        if self._task_set is not LEGACY_CATEGORY_NEXT and mask_a is not None:
            shared_cat = shared_cat.masked_fill(mask_a.unsqueeze(-1), 0)

        if self._task_a_is_sequential:
            return self.category_poi(shared_cat)
        return self.category_poi(shared_cat.squeeze(1)).view(
            -1, self.num_classes_task_a
        )

    def next_forward(self, next_input: torch.Tensor) -> torch.Tensor:
        """Run the next subgraph with a zero-A stream — see ``cat_forward``
        for the partial-forward caveat."""
        pad_value = InputsConfig.PAD_VALUE
        mask = (next_input.abs().sum(dim=-1) == pad_value)
        next_input = next_input.masked_fill(mask.unsqueeze(-1), 0)

        enc_next = self.next_encoder(next_input)
        # Synthetic zero A stream. When task-A is sequential we mirror
        # its length; when flat we use a single timestep so the cross-
        # attention shapes line up. V = 0 already zeroes B's cross-
        # attention contribution from A; no ``a_pad_mask`` (see
        # cat_forward docstring on the NaN-from-fully-masked softmax).
        t_a = enc_next.size(1) if self._task_a_is_sequential else 1
        enc_cat = torch.zeros(
            enc_next.size(0), t_a, enc_next.size(-1),
            device=enc_next.device, dtype=enc_next.dtype,
        )

        a, b = enc_cat, enc_next
        if not self._disable_cross_attn:
            for block in self.crossattn_blocks:
                a, b = block(a, b, a_pad_mask=None, b_pad_mask=mask)
        shared_next = self.next_final_ln(b)

        if self._task_set is not LEGACY_CATEGORY_NEXT:
            shared_next = shared_next.masked_fill(mask.unsqueeze(-1), 0)

        return self.next_poi(shared_next)

    def shared_parameters(self) -> Iterator[nn.Parameter]:
        """Parameters of the cross-attention stack (shared by both tasks
        conceptually via information exchange, even though each task has
        its own FFN weights within a block)."""
        for block in self.crossattn_blocks:
            yield from block.parameters()
        yield from self.cat_final_ln.parameters()
        yield from self.next_final_ln.parameters()

    def task_specific_parameters(self) -> Iterator[nn.Parameter]:
        """Parameters of the two task encoders + both heads."""
        yield from self.category_encoder.parameters()
        yield from self.next_encoder.parameters()
        yield from self.category_poi.parameters()
        yield from self.next_poi.parameters()

    def cat_specific_parameters(self) -> Iterator[nn.Parameter]:
        """Cat-only parameters: cat encoder + cat head. Excludes shared
        cross-attn and final_ln, which stay in ``shared_parameters``.
        Used by the per-head-LR optimizer (F48-H3) to give the cat tower
        a different LR from the reg tower."""
        yield from self.category_encoder.parameters()
        yield from self.category_poi.parameters()

    def reg_specific_parameters(self) -> Iterator[nn.Parameter]:
        """Reg/next-only parameters: next encoder + next head. Excludes
        shared cross-attn and final_ln. Used by the per-head-LR
        optimizer (F48-H3)."""
        yield from self.next_encoder.parameters()
        yield from self.next_poi.parameters()


__all__ = ["MTLnetCrossAttn"]
