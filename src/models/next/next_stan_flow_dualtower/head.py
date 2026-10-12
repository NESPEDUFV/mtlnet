"""Dual-tower STAN-Flow reg head — T2.1 (mtl_improvement, reg-private dual-tower).

The centerpiece of Tier 2. The MTL reg head currently reads only the
cross-attn *shared* backbone output (a cat-shaped, joint-trained [B,9,256]
representation), which caps reg learning at ~12-17pp below the deployable
composite (the "regime finding": the gap is architectural, P4 + §6.4 — ~75% is
the *missing private backbone*). This head adds a **private full-STAN backbone
on the RAW [B,9,64] region sequence** — exactly the STL reg pathway — and fuses
it with the shared pathway at the pooled feature, then applies one classifier +
the α·log_T trajectory-flow prior.

Two towers, each a faithful replica of its reference path (distinct param names
so ``MTLnet._build_next_head``'s inject+filter can't silently mis-set them):

  * ``private_stan`` — raw 64-dim → STAN. **(c)-STL-ceiling faithful**:
    ``priv_num_heads=4``, ``priv_dropout=0.3``, ``d_model=128``, ``bias="alibi"``
    (the frozen ceiling used ``NextHeadSTAN`` defaults; see
    ``docs/studies/mtl_improvement/log.md`` T1.4 + ``T2.1_DUALTOWER_DESIGN.md``).
  * ``shared_stan`` — cross-attn output 256-dim → STAN. **(a)-baseline faithful**:
    ``num_heads`` (=8, INJECTED), ``dropout`` (=0.1, INJECTED), ``d_model=128``.

Fusion at the pooled ``[B, d_model]`` feature:
  * ``gated`` (b, PRIMARY): ``g = σ(W·[priv ; shared]); feat = g·priv + (1-g)·shared``
    — the only mode that tests whether the shared backbone *adds* to the private
    tower. Gate bias inits toward private (σ≈0.73) so the under-trained shared
    backbone must earn its weight.
  * ``private_only`` (a): ``feat = priv`` — composite trained jointly (control).
  * ``aux`` (c): ``feat = priv + β·aux_proj(shared)``, β learnable init 0.1
    (≈ private at init; dials in the cross-attn auxiliary if useful).

The two sub-STANs are used **only via ``forward_features``** (the pooled feature);
their internal classifiers are replaced with ``Identity`` to avoid two redundant
high-cardinality (≈ d_model × n_regions) projections. One fused classifier owns
the logits.

α·log_T prior plumbing (aux side-channel, per-fold seeded ``transition_path``) is
identical to ``NextHeadStanFlow`` so the per-fold head rebuild + ``--alpha-no-
weight-decay`` (reads ``model.next_poi.alpha``) keep working unchanged.
"""

from __future__ import annotations

from typing import Optional

import torch
import torch.nn as nn

from data.aux_side_channel import get_current_aux
from models.next.next_stan.head import NextHeadSTAN, _LEGACY_STAN_MASK
from models.next.next_stan_flow.head import _SKIP_INERT_PRIOR
from models.registry import register_model

_FUSION_MODES = ("gated", "private_only", "aux", "aux_gated")
_ALT_PRIV_HEADS = ("gru", "lstm", "tcn")


class _AltPrivTower(nn.Module):
    """Alternative private reg tower (GRU / LSTM / TCN) for the T2V.5 head-swap.

    Maps a raw region sequence ``[B, S, in_dim]`` to a pooled ``[B, d_model]``
    feature — the SAME contract as ``NextHeadSTAN.forward_features`` — so it
    drops into the dual-tower head's ``private_stan`` slot unchanged. Padded
    steps (all-zero rows, the project pad convention) are masked out of the pool.
    Used only when ``priv_head != "stan"``; the champion (priv_head="stan", the
    default) is unaffected and bit-identical.
    """

    def __init__(self, kind: str, in_dim: int, d_model: int, dropout: float):
        super().__init__()
        if kind not in _ALT_PRIV_HEADS:
            raise ValueError(f"priv_head must be one of {('stan',) + _ALT_PRIV_HEADS}, got {kind!r}")
        self.kind = kind
        self.d_model = int(d_model)
        if kind in ("gru", "lstm"):
            rnn = nn.GRU if kind == "gru" else nn.LSTM
            # 2-layer bidirectional to roughly match the STAN tower's capacity.
            self.rnn = rnn(in_dim, d_model, num_layers=2, batch_first=True,
                           bidirectional=True, dropout=float(dropout))
            self.proj = nn.Linear(2 * d_model, d_model)
        else:  # tcn — dilated causal-ish Conv1d stack over the time axis
            self.tcn = nn.Sequential(
                nn.Conv1d(in_dim, d_model, kernel_size=3, padding=1),
                nn.GELU(), nn.Dropout(float(dropout)),
                nn.Conv1d(d_model, d_model, kernel_size=3, padding=2, dilation=2),
                nn.GELU(), nn.Dropout(float(dropout)),
            )
            self.proj = nn.Linear(d_model, d_model)
        self.norm = nn.LayerNorm(d_model)

    def forward_features(self, x: torch.Tensor) -> torch.Tensor:
        # x: [B, S, in_dim]; pad steps are all-zero rows.
        mask = (x.abs().sum(dim=-1) != 0).float()  # [B, S] 1 at valid steps
        denom = mask.sum(dim=1, keepdim=True).clamp(min=1.0)  # [B,1]
        if self.kind in ("gru", "lstm"):
            out, _ = self.rnn(x)            # [B, S, 2*d_model]
            out = self.proj(out)           # [B, S, d_model]
        else:
            out = self.tcn(x.transpose(1, 2)).transpose(1, 2)  # [B, S, d_model]
            out = self.proj(out)
        # masked mean-pool over valid steps
        pooled = (out * mask.unsqueeze(-1)).sum(dim=1) / denom  # [B, d_model]
        return self.norm(pooled)


@register_model("next_stan_flow_dualtower")
class NextHeadStanFlowDualTower(nn.Module):
    """Reg-private dual-tower STAN-Flow head (gated / private_only / aux fusion).

    Parameters
    ----------
    embed_dim:
        Dim of the SHARED pathway input ``x`` (= shared_layer_size, 256;
        injected by ``MTLnet._build_next_head``). Drives ``shared_stan``.
    num_classes, seq_length:
        Region label space + window length.
    d_model:
        STAN hidden width for BOTH towers (the frozen (c) ceiling used 128;
        not injected — head default). Gate/aux fusion requires both towers at
        ``d_model``.
    num_heads, dropout:
        SHARED-tower STAN heads/dropout. **Injected** by ``_build_next_head``
        (model ``num_heads``=8, ``dropout``=0.1) → faithful (a)-baseline replica.
    bias_init:
        STAN pairwise-bias init for both towers ("alibi", the ceiling default).
    raw_embed_dim:
        Dim of the RAW region sequence handed to ``private_stan`` (64). Pass via
        ``--reg-head-param raw_embed_dim=64``.
    priv_num_heads, priv_dropout:
        PRIVATE-tower STAN heads/dropout. **Distinct names** so the inject+filter
        cannot override them — STL-ceiling-faithful defaults (4 / 0.3).
    fusion_mode:
        ``{"gated"(b), "private_only"(a), "aux"(c)}``.
    transition_path, alpha_init, freeze_alpha:
        α·log_T prior — identical semantics to ``NextHeadStanFlow``. The primary
        T2.1 arm runs prior-ON (matches the (a) baseline); the prior-OFF control
        passes ``freeze_alpha=True alpha_init=0.0``.
    """

    def __init__(
        self,
        embed_dim: int,
        num_classes: int,
        seq_length: int = 9,
        d_model: int = 128,
        num_heads: int = 8,
        dropout: float = 0.1,
        bias_init: str = "alibi",
        raw_embed_dim: int = 64,
        priv_num_heads: int = 4,
        priv_dropout: float = 0.3,
        priv_head: str = "stan",
        fusion_mode: str = "gated",
        transition_path: Optional[str] = None,
        colocation_path: Optional[str] = None,
        alpha_init: float = 0.1,
        freeze_alpha: bool = False,
        cond_coupling: str = "none",
        cond_dim: int = 7,
        cond_detach: bool = False,
        cond_signal: str = "softmax",
        cond_temp: float = 1.0,
        cond_topk: int = 0,
        cond_inject: str = "add",
        cond_logit_prior: bool = False,
        priv_grm: bool = False,
    ):
        super().__init__()
        # R10 P4 (mtl_frontier) — enable the intra-tower GRM gated read on the PRIVATE
        # reg STAN tower only (the reg workhorse). Default OFF → champion G bit-identical.
        self._priv_grm = bool(priv_grm)
        if fusion_mode not in _FUSION_MODES:
            raise ValueError(
                f"fusion_mode must be one of {_FUSION_MODES}, got {fusion_mode!r}"
            )
        self.fusion_mode = str(fusion_mode)
        self._num_classes = int(num_classes)
        self.d_model = int(d_model)
        self.priv_head = str(priv_head)

        # --- Private tower: raw [B,9,64] region sequence → [B, d_model] pooled.
        #     ``priv_head="stan"`` (DEFAULT) = the (c)-STL-ceiling-faithful STAN
        #     (priv_num_heads=4, priv_dropout=0.3, d_model=128) — bit-identical to
        #     the champion G. T2V.5 (CRITIQUE §6.2): swap in a GRU/LSTM/TCN private
        #     tower (matched d_model) to test whether STAN is over-provisioned or
        #     beaten as the private reg backbone. Each alt tower exposes the same
        #     ``forward_features([B,S,raw_embed_dim]) -> [B,d_model]`` interface, so
        #     the rest of the head (fusion / prior / classifier) is unchanged.
        if self.priv_head == "stan":
            self.private_stan = NextHeadSTAN(
                embed_dim=int(raw_embed_dim),
                num_classes=num_classes,
                seq_length=seq_length,
                d_model=self.d_model,
                num_heads=int(priv_num_heads),
                dropout=float(priv_dropout),
                bias_init=bias_init,
                grm_read=self._priv_grm,  # R10 P4 — gate the private reg tower's trajectory read
            )
            # Drop the sub-STAN's own classifier — we pool via forward_features and
            # own the logits with a single fused classifier (avoids a redundant
            # d_model × n_regions projection per tower).
            self.private_stan.classifier = nn.Identity()
        else:
            self.private_stan = _AltPrivTower(
                kind=self.priv_head,
                in_dim=int(raw_embed_dim),
                d_model=self.d_model,
                dropout=float(priv_dropout),
            )

        # --- Shared tower: cross-attn output [B,9,256] → STAN backbone.
        #     (a)-baseline faithful (num_heads/dropout injected). Built only for
        #     modes that consume the shared pathway. NOTE (2026-06-17 audit fix):
        #     "aux_gated" MUST be here — it was omitted, so aux_gated silently ran
        #     with shared_stan=None (shared pathway severed → priv + γ·aux_proj(0)
        #     = priv + γ·bias), invalidating the FU2 mechanistic claim. Champion G
        #     uses "aux" (already listed) so G is unaffected by this fix.
        if self.fusion_mode in ("gated", "aux", "aux_gated"):
            self.shared_stan = NextHeadSTAN(
                embed_dim=int(embed_dim),
                num_classes=num_classes,
                seq_length=seq_length,
                d_model=self.d_model,
                num_heads=int(num_heads),
                dropout=float(dropout),
                bias_init=bias_init,
            )
            self.shared_stan.classifier = nn.Identity()
        else:
            self.shared_stan = None

        # --- Fusion modules.
        if self.fusion_mode == "gated":
            # Per-dim sigmoid gate over [priv ; shared]; bias init +1.0 → σ≈0.73
            # toward private so the shared backbone must earn its weight.
            self.gate_net = nn.Linear(2 * self.d_model, self.d_model)
            nn.init.constant_(self.gate_net.bias, 1.0)
        elif self.fusion_mode == "aux":
            self.aux_proj = nn.Linear(self.d_model, self.d_model)
            self.beta = nn.Parameter(torch.tensor(0.1))
        elif self.fusion_mode == "aux_gated":
            # mtl_frontier Idea 2 — the input-dependent generalization of `aux`'s
            # SCALAR β: feat = priv + γ(·)·aux_proj(shared), γ=σ(MLP([priv;shared]))
            # per-dim, input-conditioned. Tests "use the shared pathway for SOME
            # check-ins, not others" — which a scalar β (X3: β→0 by gradient)
            # cannot express. The additive sibling of `gated` (convex, lost to aux).
            # γ-bias init −2.0 → γ≈0.12 ≈ champion β=0.1 (clean comparand).
            self.aux_proj = nn.Linear(self.d_model, self.d_model)
            self.aux_gate = nn.Linear(2 * self.d_model, self.d_model)
            nn.init.constant_(self.aux_gate.bias, -2.0)
            self.last_aux_gamma = None  # C28 trajectory diagnostic (mean γ)

        # --- Conditional coupling (mtl_frontier — iMTL/GETNext pattern): inject
        # the cat head's PREDICTION as an INPUT FEATURE to the reg head, fused
        # additively into the pooled feature before the classifier, trained +
        # at inference (unlike the train-only KD priors R1/R3). This conditions
        # the region prediction on the predicted category — changing the reg
        # head's input distribution rather than re-gating an orthogonal gradient.
        #   cond_coupling="posterior" → feed softmax(cat_logits) [B, cond_dim].
        # cond_proj is ZERO-INIT so the untrained head ≡ champion G; the model
        # learns the coupling from there. cond_detach controls whether the
        # cat→reg gradient flows (False = true iMTL end-to-end).
        #
        # R-CC+ (mtl_frontier, 2026-06-16) — extend the one direction that
        # produced real transfer. Three orthogonal axes, all default-off so
        # champion G is bit-identical:
        #   cond_signal  : how the cat prediction is shaped *before* projection
        #                  (model-side, read off this head): softmax(=existing
        #                  posterior) | calibrated(τ=cond_temp) | argmax(discrete
        #                  one-hot, GETNext form) | topk(cond_topk-sparse mask).
        #   cond_inject  : where the cat signal enters the reg head:
        #                  add(=existing additive fused-feature) | film(γ,β on the
        #                  fused feature, zero-init→identity) | concat_seq(broadcast
        #                  into the private-STAN input sequence, GETNext-faithful
        #                  input-side, zero-init→no-op) | none(feature-side off,
        #                  for a pure output-side prior).
        #   cond_logit_prior : output-side learned cat→region logit map
        #                  (CatDM/LBPR sibling), zero-init→no-op.
        self.cond_coupling = str(cond_coupling)
        self.cond_detach = bool(cond_detach)
        self.cond_signal = str(cond_signal)
        self.cond_temp = float(cond_temp)
        self.cond_topk = int(cond_topk)
        self.cond_inject = str(cond_inject)
        self.cond_logit_prior = bool(cond_logit_prior)
        if self.cond_coupling not in ("none", "posterior", "features"):
            raise ValueError(f"cond_coupling must be none|posterior|features, got {cond_coupling!r}")
        if self.cond_signal not in ("softmax", "calibrated", "argmax", "topk"):
            raise ValueError(f"cond_signal must be softmax|calibrated|argmax|topk, got {cond_signal!r}")
        if self.cond_inject not in ("add", "film", "concat_seq", "none"):
            raise ValueError(f"cond_inject must be add|film|concat_seq|none, got {cond_inject!r}")
        if self.cond_coupling != "none":
            # feature/input-side injection module (exactly one, zero-init → ≡ G)
            if self.cond_inject == "add":
                self.cond_proj = nn.Linear(int(cond_dim), self.d_model)
                nn.init.zeros_(self.cond_proj.weight)
                nn.init.zeros_(self.cond_proj.bias)
            elif self.cond_inject == "film":
                # FiLM on the fused feature: feat ← (1+γ)·feat + β. Zero-init the
                # projection → γ=0, β=0 → (1+0)·feat+0 ≡ champion G.
                self.cond_film = nn.Linear(int(cond_dim), 2 * self.d_model)
                nn.init.zeros_(self.cond_film.weight)
                nn.init.zeros_(self.cond_film.bias)
            elif self.cond_inject == "concat_seq":
                # Input-side: broadcast-add a cat embedding to every *valid* step
                # of the raw region sequence before the private tower (GETNext:
                # the predicted category modulates the input). Project cond_dim →
                # raw_embed_dim, zero-init → no change ≡ champion G. Added only on
                # non-pad steps so the private STAN's pad mask is preserved.
                self.cond_seq_proj = nn.Linear(int(cond_dim), int(raw_embed_dim))
                nn.init.zeros_(self.cond_seq_proj.weight)
                nn.init.zeros_(self.cond_seq_proj.bias)
            # cond_inject == "none": no feature/input injection (pure logit prior).
            if self.cond_logit_prior:
                # Output-side learned cat→region prior added to the logits;
                # zero-init → no-op ≡ champion G.
                self.cond_logit = nn.Linear(int(cond_dim), int(num_classes))
                nn.init.zeros_(self.cond_logit.weight)
                nn.init.zeros_(self.cond_logit.bias)
            self.last_cond_norm = None  # C28 diagnostic — mean ‖injected delta‖

        # --- Fused classifier (mirrors NextHeadSTAN.classifier structure).
        self.classifier = nn.Sequential(
            nn.LayerNorm(self.d_model),
            nn.Dropout(float(dropout)),
            nn.Linear(self.d_model, num_classes),
        )

        # --- α·log_T trajectory-flow prior (identical to NextHeadStanFlow).
        if bool(freeze_alpha):
            self.register_buffer("alpha", torch.tensor(float(alpha_init)))
        else:
            self.alpha = nn.Parameter(torch.tensor(float(alpha_init)))
        # Mirror NextHeadStanFlow._inert_prior (see _SKIP_INERT_PRIOR there): a frozen
        # α == 0.0 makes _apply_prior an exact bitwise no-op, so it is skipped.
        self._inert_prior = (
            _SKIP_INERT_PRIOR and bool(freeze_alpha) and float(alpha_init) == 0.0
        )

        if transition_path is not None:
            payload = torch.load(
                transition_path, map_location="cpu", weights_only=False
            )
            log_T = payload["log_transition"] if isinstance(payload, dict) else payload
            log_T = log_T.float()
            if log_T.shape[0] < num_classes or log_T.shape[1] < num_classes:
                raise ValueError(
                    f"Transition matrix shape {tuple(log_T.shape)} is smaller "
                    f"than num_classes={num_classes}. Rebuild for this state."
                )
            log_T = log_T[:num_classes, :num_classes].contiguous()
            self.register_buffer("log_T", log_T)
        else:
            self.register_buffer("log_T", torch.zeros(num_classes, num_classes))

        # --- R1 (mtl_frontier) co-location prior P(region|cat), [num_classes, n_cats].
        # log P(region|cat), column-normalized; consumed ONLY by the trainer's
        # log_C-KD branch (mtl_cv.py) — NOT by _apply_prior (this is a KD teacher
        # factor, not an additive logit prior). Buffer so it moves to device with
        # the model and is fold-scoped (the head is rebuilt per fold). Absent →
        # zeros (the KD branch's weight==0 fast path makes that a strict no-op).
        if colocation_path is not None:
            cpayload = torch.load(colocation_path, map_location="cpu", weights_only=False)
            log_C = cpayload["log_colocation"] if isinstance(cpayload, dict) else cpayload
            log_C = log_C.float()
            if log_C.shape[0] < num_classes:
                raise ValueError(
                    f"Co-location matrix rows {log_C.shape[0]} < num_classes="
                    f"{num_classes} (regions). Rebuild for this state: "
                    f"scripts/compute_region_colocation.py --per-fold."
                )
            log_C = log_C[:num_classes, :].contiguous()
            self.register_buffer("log_C", log_C)
            # R3 (mtl_frontier) reverse arm — log P(cat|region) [num_classes, n_cats],
            # row-normalized. Teacher for the cat head: Σ_r P(cat|r)·P̂_reg(r). Consumed
            # by the trainer's reverse cat-KD branch. Absent in legacy R1 files → None.
            log_C_rev = cpayload.get("log_cat_given_region") if isinstance(cpayload, dict) else None
            if log_C_rev is not None:
                log_C_rev = log_C_rev.float()[:num_classes, :].contiguous()
                self.register_buffer("log_C_rev", log_C_rev)
            else:
                self.register_buffer("log_C_rev", None, persistent=False)
        else:
            self.register_buffer("log_C", None, persistent=False)
            self.register_buffer("log_C_rev", None, persistent=False)

    # ------------------------------------------------------------------
    def _fuse(
        self,
        priv_feat: Optional[torch.Tensor],
        shared_feat: Optional[torch.Tensor],
        ref: torch.Tensor,
    ) -> torch.Tensor:
        """Combine pooled [B, d_model] tower features per ``fusion_mode``.

        ``ref`` supplies device/dtype/batch for the defensive zero-fill on the
        ``raw_region_seq is None`` probe path (never the training/eval path).
        """
        b = ref.size(0)
        if priv_feat is None:
            priv_feat = ref.new_zeros(b, self.d_model)
        if self.fusion_mode == "private_only":
            return priv_feat
        if shared_feat is None:
            shared_feat = ref.new_zeros(b, self.d_model)
        if self.fusion_mode == "gated":
            g = torch.sigmoid(
                self.gate_net(torch.cat([priv_feat, shared_feat], dim=-1))
            )
            return g * priv_feat + (1.0 - g) * shared_feat
        if self.fusion_mode == "aux_gated":
            gamma = torch.sigmoid(
                self.aux_gate(torch.cat([priv_feat, shared_feat], dim=-1))
            )
            self.last_aux_gamma = float(gamma.detach().mean())
            return priv_feat + gamma * self.aux_proj(shared_feat)
        # aux
        return priv_feat + self.beta * self.aux_proj(shared_feat)

    def _apply_prior(self, logits: torch.Tensor) -> torch.Tensor:
        """Add α·log_T[last_region_idx]; keep α in-graph on the no-aux path."""
        if self._inert_prior:
            # Frozen α == 0.0 ⇒ prior adds an exact bitwise zero; skip the [B, C]
            # gather. α is a buffer here, so no autograd-graph obligation.
            return logits
        aux = get_current_aux()  # [B] int64 last_region_idx, or None
        if aux is None:
            # Defensive (eval outside AuxPublishingLoader / FLOPs probe / unit
            # test): keep α (and the prior pathway) in the autograd graph via a
            # zero-coefficient multiply so PCGrad's task-param enumeration never
            # hits ``p.grad is None``. Mirrors NextHeadStanFlow.forward.
            return logits + self.alpha * 0.0
        if aux.device != logits.device:
            aux = aux.to(logits.device)
        pad_mask = (aux < 0) | (aux >= self._num_classes)
        safe_idx = aux.clamp(min=0, max=self._num_classes - 1)
        transition_prior = self.log_T[safe_idx]  # [B, num_classes]
        # masked_fill is the identity for an all-False mask → apply it unconditionally
        # (byte-identical value, minus the host sync / graph break of the old ``.any()`` guard).
        # MTL_STAN_LEGACY_MASK=1 restores the guard for bit-exact --compile repro of pre-P1 cells.
        if _LEGACY_STAN_MASK:
            if pad_mask.any():
                transition_prior = transition_prior.masked_fill(pad_mask.unsqueeze(-1), 0.0)
        else:
            transition_prior = transition_prior.masked_fill(pad_mask.unsqueeze(-1), 0.0)
        return logits + self.alpha * transition_prior

    def forward(
        self,
        x: torch.Tensor,
        raw_region_seq: Optional[torch.Tensor] = None,
        cat_cond: Optional[torch.Tensor] = None,
    ) -> torch.Tensor:
        """Args:
        x: SHARED pathway [B, S, embed_dim=256] (cross-attn output).
        raw_region_seq: RAW [B, S, raw_embed_dim=64] region sequence — the
            model subclass passes the post-pad-mask ``next_input`` here.
        cat_cond: [B, cond_dim] cat-head prediction for conditional coupling
            (the model passes softmax(cat_logits) when cond_coupling != none).
        """
        # R-CC+ conditioning signal (None unless the head opts in AND the model
        # supplied a cat prediction — e.g. the disjoint ``next_forward`` path
        # passes cat_cond=None, so conditioning is inert there, exactly like the
        # original additive cc).
        c = None
        if self.cond_coupling != "none" and cat_cond is not None:
            c = (cat_cond.detach() if self.cond_detach else cat_cond).float()

        # Input-side injection (GETNext-faithful): modulate the raw region
        # sequence BEFORE the private tower. Only on valid (non-pad) steps so the
        # private STAN's abs-sum pad mask is preserved.
        if c is not None and self.cond_inject == "concat_seq" and raw_region_seq is not None:
            valid = (raw_region_seq.abs().sum(dim=-1, keepdim=True) != 0).to(raw_region_seq.dtype)
            delta_seq = self.cond_seq_proj(c.to(raw_region_seq.dtype)).unsqueeze(1)  # [B,1,raw]
            raw_region_seq = raw_region_seq + delta_seq * valid
            self.last_cond_norm = float(delta_seq.detach().norm(dim=-1).mean())

        priv_feat = (
            self.private_stan.forward_features(raw_region_seq)
            if raw_region_seq is not None
            else None
        )
        shared_feat = (
            self.shared_stan.forward_features(x)
            if self.shared_stan is not None
            else None
        )
        feat = self._fuse(priv_feat, shared_feat, ref=x)

        # Feature-side injection on the fused pooled feature.
        if c is not None and self.cond_inject in ("add", "film"):
            cc = c.to(feat.dtype)
            if self.cond_inject == "add":
                cond = self.cond_proj(cc)
                self.last_cond_norm = float(cond.detach().norm(dim=-1).mean())
                feat = feat + cond
            else:  # film
                gamma, beta = self.cond_film(cc).chunk(2, dim=-1)
                self.last_cond_norm = float(
                    (gamma.detach().norm(dim=-1) + beta.detach().norm(dim=-1)).mean()
                )
                feat = (1.0 + gamma) * feat + beta

        logits = self.classifier(feat)

        # Output-side learned cat→region prior (CatDM/LBPR sibling).
        if c is not None and self.cond_logit_prior:
            lp = self.cond_logit(c.to(logits.dtype))
            self.last_cond_norm = float(lp.detach().norm(dim=-1).mean())
            logits = logits + lp

        return self._apply_prior(logits)


__all__ = ["NextHeadStanFlowDualTower"]
