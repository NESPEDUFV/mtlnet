"""Baseline MTLnet architecture."""

from __future__ import annotations

import inspect
from typing import Any, Iterator, Optional, Tuple

import torch
from torch import nn

from configs.model import InputsConfig
from models.category import CategoryHeadTransformer
from models.mtl._components import FiLMLayer, ResidualBlock
from models.next import NextHeadMTL
from models.registry import _MODEL_REGISTRY, create_model, register_model
from tasks import LEGACY_CATEGORY_NEXT, TaskSet


def _filter_kwargs(target_cls: type, kwargs: dict[str, Any]) -> dict[str, Any]:
    """Drop kwargs that ``target_cls.__init__`` wouldn't accept.

    Heads in this codebase have divergent constructor signatures:
    ``NextHeadMTL`` wants ``num_heads`` / ``seq_length`` / ``num_layers``;
    ``NextLSTM`` wants ``hidden_dim`` and not ``num_heads``. The MTLnet
    builder injects every plausible context arg as a default; this helper
    then filters down to the subset that ``target_cls`` actually accepts
    before the registry call — avoiding ``TypeError: got an unexpected
    keyword argument`` on heads with narrower signatures.
    """
    sig = inspect.signature(target_cls.__init__)
    accepts = {
        p.name for p in sig.parameters.values()
        if p.kind in (p.POSITIONAL_OR_KEYWORD, p.KEYWORD_ONLY)
    }
    return {k: v for k, v in kwargs.items() if k in accepts}


@register_model("mtlnet")
class MTLnet(nn.Module):
    """Baseline shared-backbone multitask architecture.

    Head selection can be overridden via ``category_head`` / ``next_head``
    (registry names) plus ``category_head_params`` / ``next_head_params``
    (kwargs forwarded to the head constructor). The defaults reproduce the
    historical `CategoryHeadTransformer` + `NextHeadMTL` configuration
    bit-exactly so existing regression floors stay valid.

    ``task_set`` opts in to alternate 2-task topologies (e.g. the
    check2HGI ``{next_category, next_region}`` pair where both slots are
    sequential ``next_mtl`` heads with different ``num_classes``). When
    ``task_set is None`` the legacy ``{category, next}`` pair is used and
    every code path hits the pre-parameterisation branches — the
    regression floors in ``tests/test_regression`` stay pinned.
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
        category_head: Optional[str] = None,
        next_head: Optional[str] = None,
        category_head_params: Optional[dict[str, Any]] = None,
        next_head_params: Optional[dict[str, Any]] = None,
        task_set: Optional[TaskSet] = None,
        use_adashare: bool = False,
        adashare_init_logit: float = 2.0,
        adashare_temperature: float = 0.5,
    ):
        super().__init__()
        self._task_set = task_set if task_set is not None else LEGACY_CATEGORY_NEXT
        # AdaShare per-task binary routing through shared residual blocks.
        # use_adashare=False preserves legacy bit-exact. When True,
        # each of the (num_shared_layers - 1) ResidualBlocks becomes
        # gateable per task via a learnable logit; gate=1 → block applied,
        # gate=0 → skip connection only. The first preproc block
        # (Linear+LeakyReLU+LayerNorm+Dropout) is always applied because
        # it sets up the 256-dim representation space.
        self._use_adashare = bool(use_adashare)
        self._adashare_temperature = float(adashare_temperature)

        # Attribute names keep the legacy ``category_*`` / ``next_*``
        # vocabulary. The ``_task_set`` above is the source of truth for
        # task-level metadata (label space, primary metric, input rank);
        # the attribute names are a stable interface for the runner and
        # tests and do not imply semantics beyond "slot A" / "slot B".
        task_a, task_b = self._task_set.task_a, self._task_set.task_b

        # When ``task_set is None`` (legacy), resolve num_classes from
        # the constructor arg exactly as before — this preserves the
        # bit-exact contract with pre-parameterisation checkpoints.
        self.num_classes_task_a = (
            num_classes if task_set is None else task_a.num_classes
        )
        self.num_classes_task_b = (
            num_classes if task_set is None else task_b.num_classes
        )
        # Back-compat alias — some external code reads ``self.num_classes``.
        self.num_classes = self.num_classes_task_a

        self._task_a_is_sequential = task_a.is_sequential
        self._task_b_is_sequential = task_b.is_sequential

        self.category_encoder = self._build_encoder(
            in_size=feature_size,
            hidden_size=encoder_layer_size,
            num_layers=num_encoder_layers,
            out_size=shared_layer_size,
            dropout=encoder_dropout,
        )
        self.next_encoder = self._build_encoder(
            in_size=feature_size,
            hidden_size=encoder_layer_size,
            num_layers=num_encoder_layers,
            out_size=shared_layer_size,
            dropout=encoder_dropout,
        )

        self._build_shared_backbone(
            shared_layer_size=shared_layer_size,
            num_shared_layers=num_shared_layers,
            shared_dropout=shared_dropout,
        )

        # Resolve head factories. ``task_set is None`` → legacy path
        # where ``category_head`` / ``next_head`` + ``*_head_params``
        # args drive construction (``None`` → hardcoded historical
        # default inside the private builders). ``task_set`` provided →
        # read names and params from the preset.
        if task_set is None:
            task_a_head_name, task_a_head_params = category_head, category_head_params
            task_b_head_name, task_b_head_params = next_head, next_head_params
        else:
            task_a_head_name, task_a_head_params = task_a.head_factory, task_a.head_params
            task_b_head_name, task_b_head_params = task_b.head_factory, task_b.head_params

        # Task-A head: branch on is_sequential. Legacy category slot is
        # flat → ``_build_category_head`` path (hits the historical
        # default when ``name is None``). Non-legacy sequential-A slots
        # (e.g. CHECK2HGI_NEXT_REGION's ``next_category``) use the
        # next-head factory so the head's forward receives [B, T, D].
        if self._task_a_is_sequential:
            self.category_poi = self._build_next_head(
                name=task_a_head_name,
                shared_layer_size=shared_layer_size,
                num_classes=self.num_classes_task_a,
                num_heads=num_heads,
                num_layers=num_layers,
                seq_length=seq_length,
                overrides=task_a_head_params,
            )
        else:
            self.category_poi = self._build_category_head(
                name=task_a_head_name,
                shared_layer_size=shared_layer_size,
                num_classes=self.num_classes_task_a,
                num_heads=num_heads,
                num_layers=num_layers,
                overrides=task_a_head_params,
            )
        self.next_poi = self._build_next_head(
            name=task_b_head_name,
            shared_layer_size=shared_layer_size,
            num_classes=self.num_classes_task_b,
            num_heads=num_heads,
            num_layers=num_layers,
            seq_length=seq_length,
            overrides=task_b_head_params,
        )

    def _build_shared_backbone(
        self,
        shared_layer_size: int,
        num_shared_layers: int,
        shared_dropout: float,
    ) -> None:
        """Register the shared mixing block on ``self``.

        Hook for subclasses. The baseline uses FiLM + a stack of
        residual blocks; MMoE/CGC/DSelect-k variants override this to
        register a mixture-of-experts block instead — without paying
        for (and then `del`-ing) the baseline FiLM/shared_layers
        allocation at init time.
        """
        self.task_embedding = nn.Embedding(2, shared_layer_size)
        self.film = FiLMLayer(
            emb_dim=shared_layer_size, layer_size=shared_layer_size
        )
        self.shared_layers = self._build_shared_layers(
            layer_size=shared_layer_size,
            num_blocks=num_shared_layers,
            dropout=shared_dropout,
        )
        # AdaShare gates: per-task logits over the (num_shared_layers - 1)
        # ResidualBlocks in self.shared_layers. The first 4 modules in the
        # Sequential (Linear + LeakyReLU + LayerNorm + Dropout) form a
        # preprocessing block that is always applied (it defines the
        # 256-dim representation). The subsequent ResidualBlocks are
        # gate-able.
        if self._use_adashare:
            num_residual_blocks = max(0, num_shared_layers - 1)
            # Shape: [2 tasks, num_residual_blocks]. Initialised positive
            # so at step 0 sigmoid(logit) ≈ 0.88 ("mostly open" — the
            # block is likely used), giving the optimizer room to close
            # gates if that helps a given task.
            self.adashare_logits = nn.Parameter(
                torch.full((2, num_residual_blocks), 2.0)
            )
            self._adashare_num_residual_blocks = num_residual_blocks
        else:
            self._adashare_num_residual_blocks = 0

    @staticmethod
    def _build_category_head(
        name: Optional[str],
        shared_layer_size: int,
        num_classes: int,
        num_heads: int,
        num_layers: int,
        overrides: Optional[dict[str, Any]],
    ) -> nn.Module:
        """Instantiate the category head.

        When ``name`` is None, build the historical default
        (``CategoryHeadTransformer`` with 2 tokens of half-width) directly
        — this path is deliberately not routed through the registry so
        parameter ordering and RNG consumption stay bit-exact with the
        pre-parameterization model.
        """
        if name is None:
            return CategoryHeadTransformer(
                input_dim=shared_layer_size,
                num_tokens=2,
                token_dim=shared_layer_size // 2,
                num_layers=num_layers,
                num_heads=num_heads,
                dropout=0.1,
                num_classes=num_classes,
            )
        # Inject every plausible default from MTLnet's init context;
        # filter down to what this head's __init__ actually accepts so
        # heads with narrower signatures don't get unexpected kwargs.
        # Overrides win over defaults.
        defaults: dict[str, Any] = {
            "input_dim": shared_layer_size,
            "embed_dim": shared_layer_size,
            "num_classes": num_classes,
            "num_heads": num_heads,
            "num_layers": num_layers,
            "num_tokens": 2,
            "token_dim": shared_layer_size // 2,
            "dropout": 0.1,
        }
        defaults.update(overrides or {})
        target_cls = _MODEL_REGISTRY.get(name)
        if target_cls is None:
            # Lazily populate via create_model's registration side-effect.
            return create_model(name, **defaults)
        return create_model(name, **_filter_kwargs(target_cls, defaults))

    @staticmethod
    def _build_next_head(
        name: Optional[str],
        shared_layer_size: int,
        num_classes: int,
        num_heads: int,
        num_layers: int,
        seq_length: int,
        overrides: Optional[dict[str, Any]],
    ) -> nn.Module:
        """Instantiate the next-POI head (see ``_build_category_head``)."""
        if name is None:
            return NextHeadMTL(
                shared_layer_size,
                num_classes,
                num_heads,
                seq_length,
                num_layers,
                dropout=0.1,
            )
        # Same "inject + filter" pattern as _build_category_head so
        # heads like next_lstm (which don't accept num_heads) don't
        # error on unexpected kwargs.
        defaults: dict[str, Any] = {
            "embed_dim": shared_layer_size,
            "input_dim": shared_layer_size,
            "num_classes": num_classes,
            "num_heads": num_heads,
            "num_layers": num_layers,
            "seq_length": seq_length,
            "dropout": 0.1,
        }
        defaults.update(overrides or {})
        target_cls = _MODEL_REGISTRY.get(name)
        if target_cls is None:
            return create_model(name, **defaults)
        return create_model(name, **_filter_kwargs(target_cls, defaults))

    def _build_encoder(
        self,
        in_size: int,
        hidden_size: int,
        num_layers: int,
        out_size: int,
        dropout: float,
    ) -> nn.Sequential:
        layers = [
            nn.Linear(in_size, hidden_size),
            nn.ReLU(),
            nn.LayerNorm(hidden_size),
            nn.Dropout(dropout),
        ]
        for _ in range(num_layers - 1):
            layers += [
                nn.Linear(hidden_size, hidden_size),
                nn.ReLU(),
                nn.LayerNorm(hidden_size),
                nn.Dropout(dropout),
            ]
        layers += [
            nn.Linear(hidden_size, out_size),
            nn.ReLU(),
            nn.LayerNorm(out_size),
        ]
        return nn.Sequential(*layers)

    def _build_shared_layers(
        self,
        layer_size: int,
        num_blocks: int,
        dropout: float,
    ) -> nn.Sequential:
        layers = [
            nn.Linear(layer_size, layer_size),
            nn.LeakyReLU(),
            nn.LayerNorm(layer_size),
            nn.Dropout(dropout),
        ]
        for _ in range(num_blocks - 1):
            layers.append(ResidualBlock(layer_size, dropout))
        return nn.Sequential(*layers)

    @staticmethod
    def _gumbel_sigmoid(
        logits: torch.Tensor,
        temperature: float,
        training: bool,
    ) -> torch.Tensor:
        """Binary gate via Gumbel-sigmoid with straight-through estimator.

        Train: sample via Gumbel noise + sigmoid, then hard-threshold
        with straight-through (forward binary, backward soft).
        Eval: deterministic sigmoid threshold at 0.5.
        """
        if training:
            # Sample two Gumbel noises (u1 for gate=1, u2 for gate=0)
            # via the standard Gumbel-trick formula: g = -log(-log(U))
            # with U ~ Uniform(0, 1). Safe-guarded against log(0).
            u = torch.rand_like(logits)
            u = u.clamp(min=1e-8, max=1.0 - 1e-8)
            g1 = -torch.log(-torch.log(u))
            u2 = torch.rand_like(logits)
            u2 = u2.clamp(min=1e-8, max=1.0 - 1e-8)
            g0 = -torch.log(-torch.log(u2))
            # Binary concrete: logit for "gate=1" vs "gate=0".
            y_soft = torch.sigmoid((logits + g1 - g0) / temperature)
            y_hard = (y_soft > 0.5).to(y_soft.dtype)
            # Straight-through: forward uses y_hard, backward uses y_soft.
            return y_hard + (y_soft - y_soft.detach())
        else:
            return (torch.sigmoid(logits) > 0.5).to(logits.dtype)

    def _adashare_forward(self, x: torch.Tensor, task_id: int) -> torch.Tensor:
        """Route through shared_layers with per-task binary block gates.

        The first 4 modules of shared_layers (Linear, LeakyReLU,
        LayerNorm, Dropout) form an always-applied preprocessing block.
        The subsequent ResidualBlocks are gated: gate=1 means apply the
        block, gate=0 means skip (use the identity). Gates are sampled
        per forward pass via Gumbel-sigmoid (train) or thresholded
        sigmoid (eval).
        """
        # Preprocessing block (always applied).
        for i in range(4):
            x = self.shared_layers[i](x)
        # Gated ResidualBlocks.
        gates = self._gumbel_sigmoid(
            self.adashare_logits[task_id],
            self._adashare_temperature,
            self.training,
        )
        for i in range(self._adashare_num_residual_blocks):
            block = self.shared_layers[4 + i]
            block_out = block(x)
            gate = gates[i]
            x = gate * block_out + (1 - gate) * x
        return x

    def forward(
        self,
        inputs: Tuple[torch.Tensor, torch.Tensor],
    ) -> Tuple[torch.Tensor, torch.Tensor]:
        # This method interleaves the category and next paths intentionally:
        # under train-mode dropout, the RNG state advances across both paths
        # in a specific order, and the regression floors in
        # tests/test_regression were calibrated against that order. Do not
        # refactor into sequential `_forward_category` + `_forward_next`
        # calls without recalibrating — the bit-exact contract only holds
        # for cat_forward / next_forward in eval mode (no dropout).
        category_input, next_input = inputs

        pad_value = InputsConfig.PAD_VALUE
        mask = (next_input.abs().sum(dim=-1) == pad_value)
        next_input = next_input.masked_fill(mask.unsqueeze(-1), 0)

        # Sequential task_a (non-legacy task sets, e.g. check2HGI) needs
        # the same pad-masking treatment as task_b. Guarded by the flag
        # so the legacy flat-category path is bit-exact preserved.
        if self._task_a_is_sequential:
            mask_a = (category_input.abs().sum(dim=-1) == pad_value)
            category_input = category_input.masked_fill(mask_a.unsqueeze(-1), 0)

        enc_cat = self.category_encoder(category_input)
        enc_next = self.next_encoder(next_input)

        b_cat = enc_cat.size(0)
        b_next = enc_next.size(0)
        id_cat = torch.zeros(b_cat, dtype=torch.long, device=enc_cat.device)
        id_next = torch.ones(b_next, dtype=torch.long, device=enc_next.device)

        emb_cat = self.task_embedding(id_cat)
        emb_next = self.task_embedding(id_next)

        mod_cat = self.film(enc_cat, emb_cat)
        mod_next = self.film(enc_next, emb_next)

        if self._use_adashare:
            shared_cat = self._adashare_forward(mod_cat, task_id=0)
            shared_next = self._adashare_forward(mod_next, task_id=1)
        else:
            shared_cat = self.shared_layers(mod_cat)
            shared_next = self.shared_layers(mod_next)

        # Re-zero shared_{cat,next} at the ORIGINAL pad positions before
        # the heads. After {category,next}_encoder + FiLM + shared_layers,
        # originally-zero pad steps become non-zero (bias/gamma/beta
        # additions), so heads that detect padding via ``x.abs().sum(-1)
        # == 0`` (GRU, LSTM, TCN, Transformer) see a fully-dense sequence
        # and treat pad as real data. Sequential GRU/LSTM are particularly
        # sensitive because their "take last valid timestep" rule then
        # points into noise. Guarded on the non-legacy path so
        # LEGACY_CATEGORY_NEXT regression tests stay bit-exact.
        if self._task_set is not LEGACY_CATEGORY_NEXT:
            shared_next = shared_next.masked_fill(mask.unsqueeze(-1), 0)
            if self._task_a_is_sequential:
                shared_cat = shared_cat.masked_fill(mask_a.unsqueeze(-1), 0)

        # Sequence-head task_a (e.g. next_mtl for next_category) consumes
        # [B, T, D] directly and returns [B, num_classes]. Flat-head
        # task_a (legacy CategoryHeadTransformer) needs the squeeze+view
        # contract — preserved to keep pinned checkpoints valid.
        if self._task_a_is_sequential:
            out_cat = self.category_poi(shared_cat)
        else:
            out_cat = self.category_poi(shared_cat.squeeze(1)).view(
                -1, self.num_classes_task_a
            )
        out_next = self.next_poi(shared_next)
        return out_cat, out_next

    def cat_forward(self, category_input: torch.Tensor) -> torch.Tensor:
        """Run only the category subgraph.

        Exists so inference and ablation code can evaluate one head
        without feeding a dummy zero-tensor on the unused side.
        In eval mode (no dropout) the output is bit-exactly equal to
        ``forward((x, anything))[0]`` — see tests/test_models/test_mtlnet.py
        for the pinned contract. In train mode it will differ because
        Dropout samples a different RNG subsequence; use only for eval.
        """
        if self._task_a_is_sequential:
            pad_value = InputsConfig.PAD_VALUE
            mask = (category_input.abs().sum(dim=-1) == pad_value)
            category_input = category_input.masked_fill(mask.unsqueeze(-1), 0)

        enc = self.category_encoder(category_input)
        task_id = torch.zeros(enc.size(0), dtype=torch.long, device=enc.device)
        task_emb = self.task_embedding(task_id)
        modulated = self.film(enc, task_emb)
        shared = self.shared_layers(modulated)
        if self._task_a_is_sequential:
            return self.category_poi(shared)
        return self.category_poi(shared.squeeze(1)).view(-1, self.num_classes_task_a)

    def next_forward(self, next_input: torch.Tensor) -> torch.Tensor:
        """Run only the next-POI subgraph (see ``cat_forward``)."""
        pad_value = InputsConfig.PAD_VALUE
        mask = (next_input.abs().sum(dim=-1) == pad_value)
        next_input = next_input.masked_fill(mask.unsqueeze(-1), 0)

        enc = self.next_encoder(next_input)
        task_id = torch.ones(enc.size(0), dtype=torch.long, device=enc.device)
        task_emb = self.task_embedding(task_id)
        modulated = self.film(enc, task_emb)
        shared = self.shared_layers(modulated)
        return self.next_poi(shared)

    def shared_parameters(self) -> Iterator[nn.Parameter]:
        return (
            p
            for name, p in self.named_parameters()
            if "shared_layers" in name
            or "task_embedding" in name
            or "film" in name
        )

    def task_specific_parameters(self) -> Iterator[nn.Parameter]:
        # AdaShare gates are per-task (shape [2, num_blocks]) and control
        # whether each shared block fires for each task, so they belong in
        # the task-specific bucket. They must be enumerated here otherwise
        # gradient-surgery losses (PCGrad / CAGrad / AlignedMTL) leave
        # p.grad is None for every step — see
        # docs/issues/check2hgi/MTL_PARAM_PARTITION_BUG.md.
        return (
            p
            for name, p in self.named_parameters()
            if any(
                key in name
                for key in (
                    "category_encoder",
                    "next_encoder",
                    "category_poi",
                    "next_poi",
                    "adashare_logits",
                )
            )
        )

    def cat_specific_parameters(self) -> Iterator[nn.Parameter]:
        """Cat-only params (cat encoder + cat head) for the per-head-LR
        optimizer (F48-H3). Added 2026-06-04 so the hard-share anchor (T2.0,
        mtl_improvement) can run under the SAME per-head onecycle recipe as the
        cross-attn arms — a clean dose-response comparison. Excludes the shared
        trunk (film/task_embedding/shared_layers), which stays in
        ``shared_parameters``. Mirrors ``MTLnetCrossStitch``."""
        yield from self.category_encoder.parameters()
        yield from self.category_poi.parameters()

    def reg_specific_parameters(self) -> Iterator[nn.Parameter]:
        """Reg/next-only params (next encoder + next head) for the per-head-LR
        optimizer. See ``cat_specific_parameters``."""
        yield from self.next_encoder.parameters()
        yield from self.next_poi.parameters()


__all__ = ["MTLnet"]
