"""
Check2HGI: Check-in Hierarchical Graph Infomax module.

4-level hierarchy: Check-in -> POI -> Region -> City
Based on HGI by Weiming Huang, Daokun Zhang, and Gengchen Mai
"""

import random
import torch
import torch.nn as nn
from torch_geometric.nn.inits import reset, uniform


EPS = 1e-7


def corruption(x):
    """
    Corruption function to generate negative samples through random permutation.

    Args:
        x: Features [num_nodes, dim]

    Returns:
        Corrupted features (randomly permuted)
    """
    return x[torch.randperm(x.size(0), device=x.device)]


class Check2HGI(nn.Module):
    """
    Check-in Hierarchical Graph Infomax Module.

    This model learns hierarchical representations across four levels:
    1. Check-in level: Individual check-in events
    2. POI level: Aggregated check-ins within each POI
    3. Region level: Aggregated POIs within geographic regions
    4. City level: Aggregated regions for the entire city

    The model maximizes mutual information across these hierarchical levels.
    """

    def __init__(
        self,
        hidden_channels,
        checkin_encoder,
        checkin2poi,
        poi2region,
        region2city,
        corruption,
        alpha_c2p=0.4,
        alpha_p2r=0.3,
        alpha_r2c=0.3,
        c2p_hard_neg_prob=0.0,
        c2p_corrupted_neg=False,
        p2r_hard_neg_prob=None,
        p2r_hard_neg_min_batch=50000,
        p2r_hard_neg_sim_range=(0.6, 0.8),
        # T4.3 — POI side-features (popularity / hours / co-visit).
        # When ``side_feature_dim`` > 0, build a post-pool injection path
        # that augments POI embeddings with derived per-POI features.
        side_feature_dim: int = 0,
        side_feature_hidden: int = 16,
        # T4.1 — GraphMAE masked feature reconstruction.
        # When ``mae_lambda`` > 0, run a separate masked-input encoder pass
        # plus a decoder that reconstructs the masked node features. The
        # SCE loss is added to the total with coefficient ``mae_lambda``.
        mae_lambda: float = 0.0,
        mae_mask_rate: float = 0.5,
        mae_gamma: float = 3.0,
        mae_in_channels: int | None = None,
        # T5.2a — Joint Node2Vec POI-POI skip-gram auxiliary head.
        # When ``n2v_lambda`` > 0 and ``n2v_head`` is attached via
        # ``attach_node2vec_head``, the skip-gram loss is added to the
        # total: ``L_total += n2v_lambda * L_skipgram``.
        # ``n2v_align_lambda`` (audit-fix blocker #1): when > 0, also add an
        # alignment term ``λ_align · (1 − cos(pos_poi_emb, n2v_head.poi_table.weight))``
        # averaged over batch POIs so skip-gram gradients reach the c2hgi
        # encoder transitively (the export path). Default 0.0 preserves the
        # T5.2a-as-shipped behavior; turn on by passing ``--n2v-align-lambda``.
        n2v_lambda: float = 0.0,
        n2v_align_lambda: float = 0.0,
        # T5.1 — Native learned POI ID embedding (additive post-pool).
        # When ``use_poi_id_embedding`` is True, build an
        # ``nn.Embedding(num_pois, D)`` and add ``poi_id_gamma * poi_table.weight``
        # to the POI pool BEFORE the side-feature injection and BEFORE
        # the p2r aggregation. ``num_pois`` MUST be supplied when enabling
        # the table — it sizes the embedding once at construction and
        # is NEVER hard-coded.
        # CRITICAL — init MUST be 'zero' or 'gaussian' (small). Importing
        # HGI's POI2Vec to warm-start is the merge-family path and is
        # OUT OF SCOPE here.
        use_poi_id_embedding: bool = False,
        poi_id_gamma: float = 0.3,
        poi_id_init: str = "zero",
        poi_id_init_std: float = 0.01,
        num_pois: int | None = None,
        # T5.2b — Masked POI feature-aggregate reconstruction. When
        # ``mae_poi_lambda`` > 0, attach a ``MaskedPOIDecoder`` that
        # consumes the pooled POI embeddings + POI Delaunay edges + a
        # per-POI feature aggregate target (mean category one-hot ∨ log
        # visit count). The SCE/MSE loss is added with coefficient
        # ``mae_poi_lambda``. Defaults reproduce canonical behaviour.
        mae_poi_lambda: float = 0.0,
        mae_poi_mask_rate: float = 0.15,
        mae_poi_gamma: float = 3.0,
        mae_poi_target_dim: int = 0,
        mae_poi_aggr: str = "mean",
        mae_poi_target_kind: str = "category_aggregate",
        mae_poi_loss_kind: str = "sce",
        # T6.4 — Tier-6 loss-shape options.
        # ``p2r_use_infonce``: replace the JSD-style binary p2r loss with
        #   InfoNCE over the full batch (each POI's positive region scored
        #   against ALL regions in batch via softmax / cross-entropy).
        #   Default False → byte-identical to canonical.
        # ``p2r_infonce_temperature``: τ for the softmax (smaller = harder).
        # ``two_pass_corruption``: when True, ``forward`` performs a SECOND
        #   independent feature-corruption pass and uses its outputs as the
        #   negatives for the p2r and r2c boundaries (decoupling them from
        #   the c2p negative chain). The c2p negative is still drawn from
        #   the first pass. Default False → byte-identical to canonical.
        p2r_use_infonce: bool = False,
        p2r_infonce_temperature: float = 0.1,
        two_pass_corruption: bool = False,
        # T6.1 — POI↔POI co-visit InfoNCE 4th boundary (LOAD-BEARING for next-reg
        # gap; tests the user's "POI-feature promotion" hypothesis without free
        # parameters or external Node2Vec alignment).
        # ``p2p_lambda``: coefficient on the 4th boundary loss. Default 0 ⇒
        #   canonical bit-identical (no extra forward op, no extra parameters).
        # ``p2p_temperature``: τ for the InfoNCE softmax (smaller = harder).
        # ``p2p_batch_size``: number of (anchor, positive) co-visit pairs sampled
        #   per training step. The OTHER positives in the batch act as in-batch
        #   negatives (standard SimCLR/MoCo-style InfoNCE). Default 1024.
        # ``p2p_hard_neg_only``: if True, only consider negatives from a DIFFERENT
        #   region than the anchor (filters within-region positives out of the
        #   negative set). Default False = standard in-batch negatives.
        # ``p2p_share_pool``: True ⇒ z_p comes from the existing Checkin2POI
        #   (single pool, two objectives — per user-aligned 2026-05-18 decision).
        #   False is reserved for an ablation that uses a parallel POI-pool head;
        #   not implemented in this default-off-only landing. Always True for now.
        p2p_lambda: float = 0.0,
        p2p_temperature: float = 0.1,
        p2p_batch_size: int = 1024,
        p2p_hard_neg_only: bool = False,
        # T6.1 implementation-robustness option (advisor 2026-05-19): symmetric
        # InfoNCE loss — average cross-entropy(anchor → positive) and
        # cross-entropy(positive → anchor). Default False = the original
        # asymmetric anchor-only version (matches the prior T6.1 sweep
        # numerics). True follows the canonical SimCLR formulation.
        p2p_symmetric: bool = False,
        # ──────────────────────────────────────────────────────────────────
        # v13 / v14 — Graduated reg-path POI augmentation (formerly the
        # scripts/probe Design B / Design K subclasses). A POI2Vec / learnable
        # POI table is injected into the REG path only (poi2region / p2r / r2c),
        # while the CAT path (c2p, pos_poi_emb_pure) stays byte-identical to
        # canonical. The reg-path canonical POI pool is DETACHED before the
        # augmentation so reg-axis gradients never reach the check-in encoder.
        #
        # ``reg_poi_mode``:
        #   "none"              — default; build NOTHING new, forward unchanged
        #                         (bit-identical to canonical).
        #   "poi2vec_residual"  — Design B / v13: poi_emb_for_reg =
        #                         detach(pool) + γ·Linear(POI2Vec_frozen).
        #   "delaunay_gcn"      — Design K / v14: pre_gcn = detach(pool) +
        #                         γ·poi_table; poi_emb_for_reg =
        #                         PReLU(GCNConv(pre_gcn, delaunay_edges));
        #                         + anchor_lambda·‖poi_table − POI2Vec‖² loss.
        #
        # Supporting tensors (passed by train_check2hgi from the loaders that
        # mirror the probe scripts):
        #   ``poi2vec_table``      — (num_pois, 64) frozen POI2Vec (both modes).
        #   ``delaunay_edge_index``/``delaunay_edge_weight`` — POI-POI Delaunay
        #                            edges remapped to c2hgi POI idx (gcn mode).
        #   ``num_pois``           — already accepted above (T5.1); sizes the
        #                            learnable poi_table in delaunay_gcn mode.
        reg_poi_mode: str = "none",
        gamma_init: float = 1.0,
        anchor_lambda: float = 0.0,
        poi2vec_table: "torch.Tensor | None" = None,
        delaunay_edge_index: "torch.Tensor | None" = None,
        delaunay_edge_weight: "torch.Tensor | None" = None,
    ):
        """
        Initialize Check2HGI module.

        Args:
            hidden_channels: Hidden dimension
            checkin_encoder: Check-in level encoder (GCN)
            checkin2poi: Check-in to POI aggregation module
            poi2region: POI to region aggregation module (reused from HGI)
            region2city: Region to city aggregation function
            corruption: Corruption function for negative sampling
            alpha_c2p: Weight for check-in to POI loss
            alpha_p2r: Weight for POI to region loss
            alpha_r2c: Weight for region to city loss
        """
        super(Check2HGI, self).__init__()

        self.hidden_channels = hidden_channels
        self.checkin_encoder = checkin_encoder
        self.checkin2poi = checkin2poi
        self.poi2region = poi2region
        self.region2city = region2city
        self.corruption = corruption

        # Loss weights (should sum to 1)
        self.alpha_c2p = alpha_c2p
        self.alpha_p2r = alpha_p2r
        self.alpha_r2c = alpha_r2c

        # Phase-11 substrate audit: optional hard-negative mining at the
        # check-in↔POI boundary. With probability `c2p_hard_neg_prob`, the
        # negative POI for a check-in is drawn from the same region as the
        # check-in's true POI (different POI) instead of from the global pool.
        # Default 0.0 reproduces canonical c2hgi exactly.
        self.c2p_hard_neg_prob = c2p_hard_neg_prob

        # Phase-11 S4: when True, c2p negatives reuse the already-computed
        # corrupted-feature POI embeddings (`neg_poi_emb`) at the SAME POI
        # identity as the positive — DGI-style "is this the true encoding
        # of POI X, or a corrupted-feature encoding?" The corruption
        # forward pass is paid for unconditionally; this flag wires its
        # output into the c2p loss instead of letting it only feed r2c.
        # Mutually exclusive with c2p_hard_neg_prob > 0.
        self.c2p_corrupted_neg = c2p_corrupted_neg
        if c2p_corrupted_neg and c2p_hard_neg_prob > 0:
            raise ValueError(
                "c2p_corrupted_neg=True is mutually exclusive with "
                "c2p_hard_neg_prob > 0 (both modify the same negative)."
            )

        # T2.1 p2r hard-negative knobs (overrides the canonical 25% baked into
        # `_sample_negative_indices_with_similarity`):
        #   `p2r_hard_neg_prob=None` → canonical legacy behaviour (25% with
        #     batch < `p2r_hard_neg_min_batch` guard).
        #   `p2r_hard_neg_prob=<float>` → override the rate explicitly.
        #     0.0 disables hard negs; >0 forces hard-neg sampling regardless
        #     of batch size (i.e. enables it for FL too) when batch < min.
        #   `p2r_hard_neg_min_batch` controls the batch-size gate.
        #   `p2r_hard_neg_sim_range` controls the similarity window
        #     (default (0.6, 0.8) — the canonical band).
        self.p2r_hard_neg_prob = p2r_hard_neg_prob
        self.p2r_hard_neg_min_batch = int(p2r_hard_neg_min_batch)
        self.p2r_hard_neg_sim_range = tuple(p2r_hard_neg_sim_range)

        # Bilinear transformation weights for discrimination at each boundary
        self.weight_c2p = nn.Parameter(torch.Tensor(hidden_channels, hidden_channels))
        self.weight_p2r = nn.Parameter(torch.Tensor(hidden_channels, hidden_channels))
        self.weight_r2c = nn.Parameter(torch.Tensor(hidden_channels, hidden_channels))

        # T4.3 — POI side-feature post-pool injector. Built only when enabled
        # so the canonical (side_feature_dim=0) recipe is bit-identical.
        # Injection point: AFTER ``checkin2poi`` attention pool, BEFORE
        # ``poi2region``. Architecture: ``Linear(side_dim → side_hidden)`` →
        # concat with poi_emb → ``Linear(D + side_hidden → D)``. The side
        # features never enter the attention pool (avoids the S3-b V2-c
        # failure mode flagged in the C7-CONCERNS register).
        self.side_feature_dim = int(side_feature_dim)
        if self.side_feature_dim > 0:
            # Side projection: PReLU between proj & concat to break linearity
            # and let the encoder learn non-trivial reweightings of the raw
            # 32-d feature vector before concat (audit advisor recommendation 4).
            self.side_proj = nn.Sequential(
                nn.Linear(self.side_feature_dim, int(side_feature_hidden)),
                nn.PReLU(),
            )
            # Post-pool projection: LayerNorm after the Linear to match the
            # canonical p2r input distribution (otherwise the augmented norm
            # is larger than the pre-aug one and the p2r sigmoid saturates).
            self.pool_post_proj = nn.Sequential(
                nn.Linear(hidden_channels + int(side_feature_hidden), hidden_channels),
                nn.LayerNorm(hidden_channels),
            )
            self.side_feature_hidden = int(side_feature_hidden)
        else:
            self.side_proj = None
            self.pool_post_proj = None
            self.side_feature_hidden = 0

        # T4.1 — GraphMAE masked feature reconstruction. Built only when
        # enabled; the masked encoder pass is an extra forward over the
        # check-in graph (so total cost is ~3 encoder forwards per step
        # instead of the canonical 2). The decoder is a 2-layer MLP that
        # reconstructs the original (unmasked) input features.
        self.mae_lambda = float(mae_lambda)
        self.mae_mask_rate = float(mae_mask_rate)
        self.mae_gamma = float(mae_gamma)
        if self.mae_lambda > 0.0:
            if mae_in_channels is None:
                raise ValueError(
                    "mae_lambda > 0 requires mae_in_channels (input feature "
                    "dim) so the decoder output shape can match data.x"
                )
            self.mae_in_channels = int(mae_in_channels)
            # Mask token: small-random init (BERT/GraphMAE convention). Zero
            # init collides with padding semantics and starves the encoder
            # of useful gradient at epoch 1 (audit advisor recommendation 5).
            _mask = torch.empty(self.mae_in_channels)
            nn.init.normal_(_mask, mean=0.0, std=0.02)
            self.mask_token = nn.Parameter(_mask)
            self.mae_decoder = nn.Sequential(
                nn.Linear(hidden_channels, hidden_channels),
                nn.PReLU(),
                nn.Linear(hidden_channels, self.mae_in_channels),
            )
        else:
            self.mae_in_channels = 0
            self.mask_token = None
            self.mae_decoder = None
        # Loss term computed inside ``forward``, consumed by ``loss``.
        self._mae_loss = None

        # T5.2a — Node2Vec POI head plumbing. Head is attached AFTER __init__
        # via ``attach_node2vec_head`` so the table size (num_pois) is known
        # only from the preprocessed data. Loss is fetched inside ``loss()``.
        self.n2v_lambda = float(n2v_lambda)
        self.n2v_align_lambda = float(n2v_align_lambda)
        self.n2v_head = None      # set by attach_node2vec_head
        self._n2v_epoch_id = 0    # bumped externally by the training loop
        # Set by forward() so loss() can access the POI ids appearing in the
        # batch for the alignment term. Reset at the top of every forward().
        self._n2v_batch_poi_ids = None

        # T5.1 — Native learned POI ID embedding. Built lazily only when
        # enabled, so the canonical recipe is bit-identical (no extra
        # parameters, no extra forward op). The table is sized at
        # construction by ``num_pois`` (read by the caller from the
        # preprocessed graph's ``num_nodes_by_type['poi']`` equivalent
        # = ``city_dict['num_pois']``) — never hard-coded.
        self.use_poi_id_embedding = bool(use_poi_id_embedding)
        self.poi_id_gamma = float(poi_id_gamma)
        self.poi_id_init = str(poi_id_init)
        self.poi_id_init_std = float(poi_id_init_std)
        if self.use_poi_id_embedding:
            if num_pois is None or int(num_pois) <= 0:
                raise ValueError(
                    "use_poi_id_embedding=True requires num_pois (positive int) "
                    "from the preprocessed graph (city_dict['num_pois']). "
                    "Do NOT hard-code; read it from the graph cache."
                )
            if self.poi_id_init not in ("zero", "gaussian"):
                raise ValueError(
                    f"poi_id_init must be 'zero' or 'gaussian'; got {self.poi_id_init!r}. "
                    f"POI2Vec warm-start is explicitly out of scope for T5.1 "
                    f"(merge-family — handled in a separate Tier)."
                )
            self.num_pois_at_build = int(num_pois)
            self.poi_id_table = nn.Embedding(self.num_pois_at_build, int(hidden_channels))
            with torch.no_grad():
                if self.poi_id_init == "zero":
                    self.poi_id_table.weight.zero_()
                else:
                    self.poi_id_table.weight.normal_(mean=0.0, std=self.poi_id_init_std)
        else:
            self.num_pois_at_build = 0
            self.poi_id_table = None

        # T5.2b — Masked POI feature-aggregate decoder. Built only when
        # enabled; the decoder is consumed in ``forward`` after Checkin2POI
        # pool and BEFORE poi2region, on a SEPARATE clone of pos_poi_emb
        # so the contrastive c2p/p2r pathways are unaffected. The target
        # tensor is expected to live on ``data.poi_recon_target``
        # (P, target_dim); the POI-POI Delaunay edge list on
        # ``data.poi_delaunay_edge_index`` (2, E_poi). Both are wired by
        # train_check2hgi() when ``mae_poi_lambda`` > 0.
        self.mae_poi_lambda = float(mae_poi_lambda)
        if self.mae_poi_lambda > 0.0:
            if mae_poi_target_dim <= 0:
                raise ValueError(
                    "mae_poi_lambda > 0 requires mae_poi_target_dim > 0 "
                    "(set by train_check2hgi from data.poi_recon_target.shape[1])."
                )
            # Local import to avoid a circular import at module load time:
            # variants.py imports Check2HGI from this module.
            from embeddings.check2hgi.model.variants import MaskedPOIDecoder
            self.mae_poi_decoder = MaskedPOIDecoder(
                hidden_channels=hidden_channels,
                target_dim=int(mae_poi_target_dim),
                mask_rate=float(mae_poi_mask_rate),
                gamma=float(mae_poi_gamma),
                aggr=str(mae_poi_aggr),
                target_kind=str(mae_poi_target_kind),
                loss_kind=str(mae_poi_loss_kind),
            )
        else:
            self.mae_poi_decoder = None
        self._mae_poi_loss = None

        # T6.4 — Tier-6 loss-shape state.
        self.p2r_use_infonce = bool(p2r_use_infonce)
        self.p2r_infonce_temperature = float(p2r_infonce_temperature)
        if self.p2r_infonce_temperature <= 0.0:
            raise ValueError("p2r_infonce_temperature must be > 0")
        self.two_pass_corruption = bool(two_pass_corruption)
        # Stashed by forward() so loss() can use them for InfoNCE without
        # changing the return-tuple signature. Reset every forward call.
        self._t6_pos_region_full = None     # [N_regions, D]
        self._t6_poi_to_region = None       # [N_pois]   int64

        # T6.1 — POI↔POI co-visit InfoNCE 4th boundary state.
        # Zero new parameters at __init__ — the 4th boundary uses the existing
        # Checkin2POI pool's output z_p (stashed by forward() as
        # ``self._t6_pos_poi_emb``). Co-visit pair indices are expected on
        # ``data.covisit_pairs`` (shape [N_pairs, 2], int64) — built by the
        # preprocess (see ``preprocess.py::_build_covisit_pairs``). At λ=0
        # this entire path is bypassed and the forward+loss are bit-identical
        # to the canonical recipe.
        self.p2p_lambda = float(p2p_lambda)
        self.p2p_temperature = float(p2p_temperature)
        if self.p2p_temperature <= 0.0:
            raise ValueError("p2p_temperature must be > 0")
        self.p2p_batch_size = int(p2p_batch_size)
        if self.p2p_batch_size <= 1:
            raise ValueError("p2p_batch_size must be > 1 (in-batch negatives need ≥ 1 other positive)")
        self.p2p_hard_neg_only = bool(p2p_hard_neg_only)
        self.p2p_symmetric = bool(p2p_symmetric)
        self._t6_pos_poi_emb = None         # [N_pois, D]   — stashed by forward()
        self._t6_covisit_pairs = None       # [N_pairs, 2]  — stashed by forward()

        # ──────────────────────────────────────────────────────────────────
        # v13 / v14 — reg-path POI augmentation (graduated from the probe
        # subclasses). Built ONLY when reg_poi_mode != "none" so the canonical
        # path is bit-identical (no extra params, no extra forward op).
        self.reg_poi_mode = str(reg_poi_mode)
        self.anchor_lambda = float(anchor_lambda)
        self._anchor_loss = None
        if self.reg_poi_mode not in ("none", "poi2vec_residual", "delaunay_gcn"):
            raise ValueError(
                f"reg_poi_mode must be 'none', 'poi2vec_residual', or "
                f"'delaunay_gcn'; got {self.reg_poi_mode!r}"
            )
        self.reg_side_proj = None
        if self.reg_poi_mode == "none":
            self.poi2vec_proj = None
            self.reg_poi_table = None
            self.poi_gcn = None
            self.poi_gcn_act = None
            self.reg_gamma = None
        else:
            self.reg_gamma = nn.Parameter(torch.tensor(float(gamma_init)))
            if self.reg_poi_mode == "poi2vec_residual":
                # Design B / v13 — detach(pool) + γ·Linear(POI2Vec_frozen).
                if poi2vec_table is None:
                    raise ValueError(
                        "reg_poi_mode='poi2vec_residual' requires poi2vec_table "
                        "(num_pois, 64) — load it in train_check2hgi."
                    )
                poi2vec_dim = int(poi2vec_table.shape[1])
                self.poi2vec_proj = nn.Linear(poi2vec_dim, hidden_channels, bias=True)
                self.register_buffer("reg_poi2vec_table", poi2vec_table.float())
                self.reg_poi_table = None
                self.poi_gcn = None
                self.poi_gcn_act = None
            else:  # delaunay_gcn — Design K / v14
                if num_pois is None or int(num_pois) <= 0:
                    raise ValueError(
                        "reg_poi_mode='delaunay_gcn' requires num_pois "
                        "(positive int) to size the learnable poi_table."
                    )
                if poi2vec_table is None:
                    raise ValueError(
                        "reg_poi_mode='delaunay_gcn' requires poi2vec_table "
                        "(num_pois, D-or-64) to init/anchor the poi_table."
                    )
                if delaunay_edge_index is None or delaunay_edge_weight is None:
                    raise ValueError(
                        "reg_poi_mode='delaunay_gcn' requires delaunay_edge_index "
                        "and delaunay_edge_weight."
                    )
                from torch_geometric.nn import GCNConv
                self.reg_poi_table = nn.Embedding(int(num_pois), hidden_channels)
                with torch.no_grad():
                    self.reg_poi_table.weight.copy_(poi2vec_table.float())
                self.register_buffer("reg_poi2vec_anchor", poi2vec_table.float())
                self.register_buffer("reg_delaunay_edge_index", delaunay_edge_index.long())
                self.register_buffer("reg_delaunay_edge_weight", delaunay_edge_weight.float())
                self.poi_gcn = GCNConv(hidden_channels, hidden_channels,
                                       cached=True, bias=True)
                self.poi_gcn_act = nn.PReLU(hidden_channels)
                self.poi2vec_proj = None
                # design_k+sidefeat (CORRECTED, pre-GCN): when side features
                # are enabled WITH delaunay_gcn, the probe injects them as an
                # ADDITIVE pre-GCN POI feature (Linear(side_dim→D)→PReLU, added
                # into pre_gcn) so they diffuse through the spatial graph —
                # NOT the canonical post-pool concat+LayerNorm. To preserve
                # forward-equivalence with Check2HGI_DesignK, the canonical
                # T4.3 side path (self.side_proj/pool_post_proj) is BYPASSED
                # for this mode (see forward()); we build the additive proj here.
                if self.side_feature_dim > 0:
                    self.reg_side_proj = nn.Sequential(
                        nn.Linear(self.side_feature_dim, hidden_channels),
                        nn.PReLU(),
                    )
                    # Disable the canonical concat-style side path so forward
                    # doesn't double-inject (it would otherwise concat AFTER
                    # the GCN). The additive pre-GCN proj fully replaces it.
                    self.side_proj = None
                    self.pool_post_proj = None
                else:
                    self.reg_side_proj = None

        # Store embeddings for extraction
        self.checkin_embedding = torch.tensor(0)
        self.poi_embedding = torch.tensor(0)
        self.region_embedding = torch.tensor(0)

        self.reset_parameters()

    def reset_parameters(self):
        """Reset model parameters."""
        reset(self.checkin_encoder)
        reset(self.checkin2poi)
        reset(self.poi2region)
        uniform(self.hidden_channels, self.weight_c2p)
        uniform(self.hidden_channels, self.weight_p2r)
        uniform(self.hidden_channels, self.weight_r2c)

    def attach_node2vec_head(self, head):
        """T5.2a — register the Node2VecPOIHead as a submodule.

        Done as a separate step from __init__ because the head needs
        ``num_pois`` and the Delaunay edge index from the preprocessed
        graph (only available after data is loaded). This is the SOLE
        registration site — do not also call ``add_module`` from the
        caller.

        NOTE: ``self.n2v_head = None`` was set in ``__init__`` (line 247) to
        record the "not attached yet" state. ``nn.Module.add_module`` raises
        ``KeyError`` if the attribute already exists, so we must clear the
        sentinel first (a regression introduced and caught by the post-fix
        T5.1 audit on 2026-05-17).
        """
        if "n2v_head" in self._modules:
            del self._modules["n2v_head"]
        # Plain attribute assignment of an ``nn.Module`` value also registers
        # it as a submodule via ``nn.Module.__setattr__`` — equivalent to
        # ``add_module`` but tolerant of a pre-existing ``None`` sentinel.
        # Use ``object.__delattr__`` to clear the sentinel without recursing
        # back through ``nn.Module.__setattr__``.
        try:
            object.__delattr__(self, "n2v_head")
        except AttributeError:
            pass
        self.n2v_head = head

    def set_n2v_epoch(self, epoch_id: int) -> None:
        """Bump the cached-walks epoch id so the next ``loss()`` call
        triggers a fresh walk batch (T5.2a spec: one walk batch per epoch)."""
        self._n2v_epoch_id = int(epoch_id)

    def forward(self, data):
        """
        Forward pass to generate check-in, POI, region, and city representations.

        Args:
            data: PyTorch Geometric Data object with:
                - x: Check-in features [num_checkins, dim]
                - edge_index: Check-in graph connectivity [2, num_edges]
                - edge_weight: Edge weights [num_edges]
                - checkin_to_poi: POI assignment for each check-in [num_checkins]
                - poi_to_region: Region assignment for each POI [num_pois]
                - region_adjacency: Region adjacency graph [2, num_region_edges]
                - region_area: Area of each region [num_regions]
                - coarse_region_similarity: Region similarity matrix
                - num_pois: Number of unique POIs
                - num_regions: Number of unique regions

        Returns:
            Tuple of embeddings and negative samples for loss computation
        """
        num_pois = data.num_pois
        num_regions = data.num_regions

        # Level 1: Check-in encoding (positive samples)
        # T3.3 plumbing: optionally pass edge_type (per-edge relation index)
        # for R-GCN. Encoders that don't use it ignore the kwarg.
        _edge_type = getattr(data, 'edge_type', None)
        _enc_kwargs = {'edge_type': _edge_type} if _edge_type is not None else {}
        pos_checkin_emb = self.checkin_encoder(
            data.x, data.edge_index, data.edge_weight, **_enc_kwargs
        )

        # Level 1: Check-in encoding (negative samples with corrupted features)
        cor_x = self.corruption(data.x)
        neg_checkin_emb = self.checkin_encoder(
            cor_x, data.edge_index, data.edge_weight, **_enc_kwargs
        )

        # Level 2: POI encoding (aggregate check-ins to POIs)
        pos_poi_emb = self.checkin2poi(pos_checkin_emb, data.checkin_to_poi, num_pois)
        neg_poi_emb = self.checkin2poi(neg_checkin_emb, data.checkin_to_poi, num_pois)

        # T5.1 — Native learned POI ID embedding (additive post-pool).
        # Add ``poi_id_gamma * poi_id_table.weight`` to the per-POI pool
        # for BOTH pos and neg. The table is indexed by POI id (same as
        # poi_emb rows), so the "+ table.weight" is a single broadcast
        # add — no per-row indexing needed at training time. Negatives
        # also get their corresponding table row added, so the c2p
        # discriminator cannot reach zero loss using only the table:
        # the pooled check-in signal stays in the gradient chain (the
        # negative POI is a DIFFERENT POI whose pool is unrelated, even
        # though both POIs have their own table slot added).
        #
        # Injection point: AFTER checkin2poi pool, BEFORE side-feature
        # injection and BEFORE p2r aggregation. This way the table is
        # trained by all 3 boundaries (c2p, p2r, r2c).
        #
        # Default opt-out: when use_poi_id_embedding=False, this whole
        # block is skipped — behaviour byte-identical to canonical.
        # When poi_id_gamma=0, defensive identity path returns the
        # untouched pool (caller could set gamma=0 for an ablation).
        if self.poi_id_table is not None and self.poi_id_gamma != 0.0:
            if int(num_pois) != self.num_pois_at_build:
                raise ValueError(
                    f"Check2HGI.forward: num_pois={num_pois} != "
                    f"self.num_pois_at_build={self.num_pois_at_build}. "
                    f"T5.1 POI ID table was sized at construction; rebuild "
                    f"the model if the POI inventory changed."
                )
            _poi_id_bump = self.poi_id_gamma * self.poi_id_table.weight
            pos_poi_emb = pos_poi_emb + _poi_id_bump
            neg_poi_emb = neg_poi_emb + _poi_id_bump

        # T4.3 — POI side-feature post-pool injection. Restricted to the p2r
        # pathway only — the c2p discriminator uses the PRE-augmentation
        # POI embedding (pos_poi_emb_pure) so side-feature gradients do NOT
        # flow back into the check-in encoder via the c2p path. Otherwise
        # side-feature info would leak into checkin_emb and inflate the
        # downstream leak probe (T4.3 audit advisor blocker 2, 2026-05-16).
        side_features = getattr(data, "side_features", None)
        pos_poi_emb_pure = pos_poi_emb     # for c2p
        neg_poi_emb_pure = neg_poi_emb     # for c2p

        # ──────────────────────────────────────────────────────────────────
        # v13 / v14 — reg-path POI augmentation (graduated from the probe
        # Design B / Design K subclasses). Inserted AFTER pos_poi_emb_pure is
        # captured (so the c2p / cat boundary keeps the canonical pool) and
        # BEFORE the canonical side-feature concat (so the downstream side
        # block + poi2region + p2r all operate on the augmented reg emb,
        # exactly as the probe subclasses do). The canonical pool is DETACHED
        # before augmentation so reg-axis gradients never reach the encoder.
        # Default (reg_poi_mode="none") skips this block entirely → unchanged.
        if self.reg_poi_mode == "poi2vec_residual":
            # Design B / v13.
            poi2vec_residual = self.poi2vec_proj(self.reg_poi2vec_table)  # [P, D]
            pos_poi_emb = pos_poi_emb.detach() + self.reg_gamma * poi2vec_residual
            neg_poi_emb = neg_poi_emb.detach() + self.reg_gamma * poi2vec_residual
            # The downstream canonical side block (if side_proj is set) then
            # concat+LN-projects these, matching Check2HGI_DesignB exactly.
        elif self.reg_poi_mode == "delaunay_gcn":
            # Design K / v14.
            poi_residual = self.reg_poi_table.weight                      # [P, D]
            pos_pre_gcn = pos_poi_emb.detach() + self.reg_gamma * poi_residual
            neg_pre_gcn = neg_poi_emb.detach() + self.reg_gamma * poi_residual
            # Side features (if any) inject PRE-GCN, additively (probe order).
            if self.reg_side_proj is not None and side_features is not None:
                side_h_pre = self.reg_side_proj(side_features)            # [P, D]
                pos_pre_gcn = pos_pre_gcn + side_h_pre
                neg_pre_gcn = neg_pre_gcn + side_h_pre
            pos_poi_emb = self.poi_gcn_act(
                self.poi_gcn(pos_pre_gcn, self.reg_delaunay_edge_index,
                             self.reg_delaunay_edge_weight))
            neg_poi_emb = self.poi_gcn_act(
                self.poi_gcn(neg_pre_gcn, self.reg_delaunay_edge_index,
                             self.reg_delaunay_edge_weight))

        if self.side_proj is not None and side_features is not None:
            if side_features.shape[0] != num_pois:
                raise ValueError(
                    f"side_features.shape[0]={side_features.shape[0]} != "
                    f"num_pois={num_pois}"
                )
            if side_features.shape[1] != self.side_feature_dim:
                raise ValueError(
                    f"side_features.shape[1]={side_features.shape[1]} != "
                    f"side_feature_dim={self.side_feature_dim}"
                )
            side_h = self.side_proj(side_features)        # (P, side_hidden)
            # Augmented versions ONLY for p2r downstream:
            pos_poi_emb = self.pool_post_proj(
                torch.cat([pos_poi_emb, side_h], dim=-1)
            )
            neg_poi_emb = self.pool_post_proj(
                torch.cat([neg_poi_emb, side_h], dim=-1)
            )

        # Level 3: Region encoding (aggregate POIs to regions)
        # Uses the AUGMENTED poi_emb (the intended injection point).
        pos_region_emb = self.poi2region(pos_poi_emb, data.poi_to_region, data.region_adjacency)
        neg_region_emb = self.poi2region(neg_poi_emb, data.poi_to_region, data.region_adjacency)

        # T6.4 / T2.3 — two-pass feature corruption. Independent second
        # corruption draw + encoder pass + pool + region aggregation;
        # its output replaces ``neg_region_emb`` so the p2r and r2c
        # negatives are decoupled from the c2p negative chain. The c2p
        # negative still uses the first-pass ``neg_poi_emb`` /
        # ``neg_poi_emb_pure`` so c2p discrimination is unchanged.
        # Cost: +1 encoder pass + 1 pool + 1 region aggregation per step.
        if self.two_pass_corruption:
            cor_x_2 = self.corruption(data.x)
            neg_checkin_emb_2 = self.checkin_encoder(
                cor_x_2, data.edge_index, data.edge_weight, **_enc_kwargs
            )
            neg_poi_emb_2 = self.checkin2poi(
                neg_checkin_emb_2, data.checkin_to_poi, num_pois
            )
            # T5.1 bump consistency: apply the same broadcast add to the
            # second-pass neg pool so it remains the same "stratum" as the
            # first-pass pool (otherwise the discriminator can detect the
            # missing T5.1 bias as a shortcut). When T5.1 is off this is
            # a no-op.
            if self.poi_id_table is not None and self.poi_id_gamma != 0.0:
                neg_poi_emb_2 = neg_poi_emb_2 + (self.poi_id_gamma * self.poi_id_table.weight)
            # Side-feature projection: mirror the augmented path used for
            # the canonical p2r pathway above. When side features are off
            # this is a no-op (side_proj is None).
            if self.side_proj is not None and side_features is not None:
                side_h_2 = self.side_proj(side_features)
                neg_poi_emb_2 = self.pool_post_proj(
                    torch.cat([neg_poi_emb_2, side_h_2], dim=-1)
                )
            neg_region_emb = self.poi2region(
                neg_poi_emb_2, data.poi_to_region, data.region_adjacency
            )

        # T5.2b — Masked POI feature-aggregate reconstruction. Operates on
        # the PRE-augmentation pooled POI emb (so side-feature gradients
        # never reach the POI-level decoder), but AFTER the canonical
        # Checkin2POI pool. The decoder takes a separate path that does
        # NOT feed into the contrastive c2p/p2r/r2c losses; the loss is
        # accumulated below and added in loss() with coefficient
        # ``mae_poi_lambda``.
        #
        # Inputs read off ``data``:
        #   * ``data.poi_delaunay_edge_index``: (2, E_poi) int64 — required.
        #   * ``data.poi_recon_target``: (P, target_dim) float — required.
        # If either is absent, raise loudly — silently dropping the auxiliary
        # would defeat the purpose.
        self._mae_poi_loss = None
        if self.mae_poi_lambda > 0.0 and self.mae_poi_decoder is not None:
            poi_edges = getattr(data, "poi_delaunay_edge_index", None)
            recon_target = getattr(data, "poi_recon_target", None)
            if poi_edges is None or recon_target is None:
                raise ValueError(
                    "mae_poi_lambda > 0 requires data.poi_delaunay_edge_index "
                    "and data.poi_recon_target on the input Data object. "
                    "Did you forget to call preprocess with "
                    "build_poi_delaunay=True and build_poi_aggregates=True?"
                )
            # NB: pass the PRE-augmentation POI emb (pos_poi_emb_pure) so
            # side features don't reach this decoder (mirrors the c2p
            # isolation from T4.3).
            self._mae_poi_loss = self.mae_poi_decoder(
                pos_poi_emb_pure, poi_edges, recon_target,
            )

        # T4.1 — GraphMAE masked feature reconstruction.
        # Separate forward over a masked input: replace mask_rate of nodes'
        # features with the learned [MASK] token, run the encoder, decode
        # back to feature space, compute SCE loss on the masked positions.
        # The reconstruction is sequestered from the contrastive pipeline —
        # it only contributes the auxiliary L_mae term added in loss().
        self._mae_loss = None
        if self.mae_lambda > 0.0 and self.mae_decoder is not None:
            with torch.no_grad():
                N = data.x.size(0)
                mask = torch.rand(N, device=data.x.device) < self.mae_mask_rate
            if mask.any():
                x_masked = data.x.clone()
                x_masked[mask] = self.mask_token
                masked_emb = self.checkin_encoder(
                    x_masked, data.edge_index, data.edge_weight, **_enc_kwargs
                )
                recon = self.mae_decoder(masked_emb)                       # (N, F)
                # SCE (Scaled Cosine Error, GraphMAE Eq. 5):
                #   L = ((1 − cos_sim(recon, x))^γ).mean()
                # over masked positions only.
                recon_m = recon[mask]
                x_m = data.x[mask]
                cos = torch.nn.functional.cosine_similarity(
                    recon_m, x_m, dim=-1, eps=EPS
                )
                self._mae_loss = ((1.0 - cos).clamp(min=0.0) ** self.mae_gamma).mean()

        # Level 4: City encoding (aggregate regions)
        city_emb = self.region2city(pos_region_emb, data.region_area)

        # Store for later extraction
        self.checkin_embedding = pos_checkin_emb
        self.poi_embedding = pos_poi_emb
        self.region_embedding = pos_region_emb

        # T5.2a alignment (audit blocker #1): cache the POI embedding with
        # gradient attached so loss() can pull skip-gram gradients back into
        # the c2hgi encoder via the export path. Only relevant when an n2v
        # head is attached AND --n2v-align-lambda > 0; otherwise this is a
        # cheap reference assignment with no compute impact.
        self._n2v_pos_poi_emb = pos_poi_emb

        # T6.4 / T2.2 — stash the FULL region-emb matrix and the POI→region
        # assignment so loss() can compute InfoNCE over all regions without
        # changing the return-tuple signature. Only used when
        # ``self.p2r_use_infonce`` is True. Both references attach to the
        # current computation graph so gradients flow correctly.
        self._t6_pos_region_full = pos_region_emb
        self._t6_poi_to_region = data.poi_to_region

        # T6.1 — stash the pooled POI emb matrix + co-visit pair list so
        # loss() can compute the POI↔POI InfoNCE 4th boundary. Only used when
        # ``self.p2p_lambda > 0``; otherwise no extra compute / memory.
        #
        # We use ``pos_poi_emb_pure`` here (NOT the T4.3-augmented
        # ``pos_poi_emb``) so the 4th boundary operates on the Checkin2POI
        # pool's direct output — consistent with the c2p boundary and the
        # user's 2026-05-18 design ("single pool, two objectives"). T4.3
        # side-feature gradients should not leak into the POI↔POI objective
        # the same way they don't leak into c2p (T4.3 audit advisor blocker
        # 2, 2026-05-16). At default-off T4.3, ``pos_poi_emb_pure`` and
        # ``pos_poi_emb`` are the same tensor; at T4.3-on, this selection
        # gates the side features out of T6.1's gradient path.
        self._t6_pos_poi_emb = pos_poi_emb_pure
        self._t6_covisit_pairs = getattr(data, 'covisit_pairs', None)

        # Prepare outputs for loss computation
        # Check-in to POI: each check-in vs its POI
        # T4.3: use PURE (pre-augmentation) POI embedding to keep the c2p
        # discriminator from learning side-feature shortcuts.
        pos_poi_expanded = pos_poi_emb_pure[data.checkin_to_poi]

        # Generate negative POI assignments for check-ins
        if self.c2p_corrupted_neg:
            # S4: same POI identity, but encoded from corrupted features.
            # neg_poi_emb is already computed (lines above); reuse it.
            neg_poi_expanded = neg_poi_emb_pure[data.checkin_to_poi]
        else:
            if self.c2p_hard_neg_prob > 0.0:
                neg_poi_indices = self._sample_hard_negative_indices_c2p(
                    data, num_pois
                )
            else:
                neg_poi_indices = self._sample_negative_indices(
                    data.checkin_to_poi, num_pois, data.x.device
                )
            neg_poi_expanded = pos_poi_emb_pure[neg_poi_indices]

        # POI to Region: each POI vs its region
        pos_region_expanded = pos_region_emb[data.poi_to_region]

        # Generate negative region assignments for POIs
        neg_region_indices = self._sample_negative_indices_with_similarity(
            data.poi_to_region, num_regions,
            data.coarse_region_similarity, data.x.device
        )
        neg_region_expanded = pos_region_emb[neg_region_indices]

        return (
            pos_checkin_emb, pos_poi_expanded, neg_poi_expanded,
            pos_poi_emb, pos_region_expanded, neg_region_expanded,
            pos_region_emb, neg_region_emb, city_emb
        )

    def _sample_negative_indices(self, assignment, num_targets, device):
        """Sample negative indices (different from positive assignment) - VECTORIZED."""
        batch_size = assignment.size(0)

        # Generate random indices in [0, num_targets-1]
        neg_indices = torch.randint(0, num_targets - 1, (batch_size,), device=device)

        # Shift indices >= assignment to avoid collision
        # If neg >= pos, then neg = neg + 1 (skips the positive index)
        neg_indices = torch.where(neg_indices >= assignment, neg_indices + 1, neg_indices)

        return neg_indices

    def _sample_hard_negative_indices_c2p(self, data, num_pois):
        """Hard-negative sampling at the check-in↔POI boundary.

        For each check-in: with probability ``self.c2p_hard_neg_prob``, return
        a POI index drawn uniformly from the same region as the check-in's
        true POI (excluding that true POI itself). Otherwise fall back to the
        global random sampler.

        Vectorised: per-region POI buckets are cached on ``data`` between
        calls. Pure tensor ops on device.
        """
        device = data.x.device
        checkin_to_poi = data.checkin_to_poi          # [N_checkins]
        poi_to_region = data.poi_to_region            # [N_pois]
        num_regions = int(data.num_regions)
        N = checkin_to_poi.size(0)

        # Build/reuse per-region POI bucket lookup tables on ``data``.
        cache = getattr(data, "_c2hgi_c2p_hardneg_cache", None)
        if cache is None or cache.get("num_pois") != int(num_pois):
            poi_region_cpu = poi_to_region.detach().cpu()
            sort_idx = torch.argsort(poi_region_cpu, stable=True)      # [N_pois]
            sizes = torch.bincount(poi_region_cpu, minlength=num_regions)  # [R]
            offsets = torch.zeros(num_regions + 1, dtype=torch.long)
            offsets[1:] = sizes.cumsum(0)
            cache = {
                "num_pois": int(num_pois),
                "sort_idx": sort_idx.to(device),
                "sizes": sizes.to(device),
                "offsets": offsets.to(device),
            }
            data._c2hgi_c2p_hardneg_cache = cache

        sort_idx = cache["sort_idx"]
        sizes = cache["sizes"]
        offsets = cache["offsets"]

        # 1. Default: uniform random over global POI pool, excluding the true POI.
        rand_neg = torch.randint(0, num_pois - 1, (N,), device=device)
        rand_neg = torch.where(rand_neg >= checkin_to_poi, rand_neg + 1, rand_neg)

        # 2. Hard candidates: same-region different-POI for each check-in.
        pos_poi = checkin_to_poi
        pos_region = poi_to_region[pos_poi]                            # [N]
        region_size = sizes[pos_region]                                # [N]

        # Singleton-region check-ins (region has only their own POI) have no
        # valid hard negative — fall back to random for those rows.
        has_hard = region_size > 1                                     # [N]

        # Sample a uniform offset in [0, region_size-1) for each check-in;
        # the −1 reserves the slot we will skip past the positive POI.
        # Clamp denominator to avoid division by zero where region_size==1.
        denom = (region_size - 1).clamp(min=1)
        local_off = (torch.rand(N, device=device) * denom.float()).long()
        local_off = local_off.clamp(max=denom - 1)

        # Resolve to a global POI id from the per-region bucket, skipping
        # the positive POI's local position. We compute the positive POI's
        # local rank within its region bucket once, then shift offsets ≥
        # that rank by +1.
        region_starts = offsets[pos_region]                            # [N]
        # Find pos_poi's position inside its region bucket.
        # sort_idx[region_starts[i] : region_starts[i]+region_size[i]] is the
        # bucket. We need the index k s.t. sort_idx[region_starts[i]+k]==pos_poi.
        # Compute it via a search on the (small) bucket. For full vectorisation
        # we exploit that sort is stable on poi_to_region; within a bucket the
        # POI ids appear in ascending POI-id order, so:
        #   pos_local_rank = pos_poi - sort_idx[region_starts]   ← only valid
        #     when bucket POIs are a contiguous range; not guaranteed.
        # Safer: reverse-map. Build a per-POI local-rank tensor once.
        if "poi_local_rank" not in cache:
            local_rank = torch.empty(num_pois, dtype=torch.long, device=device)
            arange_total = torch.arange(sort_idx.size(0), device=device)
            within_bucket = arange_total - offsets[poi_to_region[sort_idx]]
            local_rank[sort_idx] = within_bucket
            cache["poi_local_rank"] = local_rank
        pos_local_rank = cache["poi_local_rank"][pos_poi]              # [N]

        # Skip past the positive's slot.
        shifted = torch.where(local_off >= pos_local_rank, local_off + 1, local_off)
        # Clamp to within-bucket range so singleton regions (region_size==1)
        # do not index past their own bucket. The clamped value for singletons
        # collides with pos_poi but ``has_hard`` masks them out below.
        max_off_in_bucket = (region_size - 1).clamp(min=0)             # [N]
        shifted = torch.minimum(shifted, max_off_in_bucket)
        hard_neg = sort_idx[region_starts + shifted]                   # [N]

        # 3. Mix: with prob c2p_hard_neg_prob choose hard, else random.
        use_hard = (torch.rand(N, device=device) < self.c2p_hard_neg_prob) & has_hard
        return torch.where(use_hard, hard_neg, rand_neg)

    def _sample_negative_indices_with_similarity(self, assignment, num_targets, similarity, device):
        """Sample negative indices using hard negative strategy - VECTORIZED.

        T2.1 hooks: behaviour is controlled by three module-level attributes:
          - ``p2r_hard_neg_prob``: ``None`` → legacy 25% hard-neg gated by
            ``batch_size < p2r_hard_neg_min_batch``; ``float`` → override
            the rate explicitly (0.0 disables; >0 always tries, with the
            same batch-size gate).
          - ``p2r_hard_neg_min_batch``: int, default 50000.
          - ``p2r_hard_neg_sim_range``: (lo, hi) similarity band, default (0.6, 0.8).
        """
        batch_size = assignment.size(0)

        # Default: random negative (different from positive)
        neg_indices = torch.randint(0, num_targets - 1, (batch_size,), device=device)
        neg_indices = torch.where(neg_indices >= assignment, neg_indices + 1, neg_indices)

        # Resolve effective rate. ``None`` reproduces legacy canonical (0.25).
        effective_prob = 0.25 if self.p2r_hard_neg_prob is None else float(self.p2r_hard_neg_prob)
        if (similarity is not None
                and batch_size < self.p2r_hard_neg_min_batch
                and effective_prob > 0.0):
            sim_lo, sim_hi = self.p2r_hard_neg_sim_range
            hard_mask = torch.rand(batch_size, device=device) < effective_prob

            if hard_mask.any():
                for i in hard_mask.nonzero(as_tuple=True)[0].tolist():
                    pos_idx = assignment[i].item()
                    sim = similarity[pos_idx]
                    candidates = ((sim > sim_lo) & (sim < sim_hi)).nonzero(as_tuple=True)[0]
                    candidates = candidates[candidates != pos_idx]
                    if len(candidates) > 0:
                        neg_indices[i] = candidates[torch.randint(len(candidates), (1,)).item()]

        return neg_indices

    def discriminate(self, emb1, emb2, weight, sigmoid=True):
        """
        Bilinear discrimination between two embedding sets.

        Args:
            emb1: First embeddings [N, D]
            emb2: Second embeddings [N, D] (aligned with emb1)
            weight: Bilinear weight matrix [D, D]
            sigmoid: Whether to apply sigmoid

        Returns:
            Discrimination scores [N]
        """
        projected = torch.matmul(emb1, weight)
        scores = (projected * emb2).sum(dim=1)
        return torch.sigmoid(scores) if sigmoid else scores

    def discriminate_global(self, emb, summary, weight, sigmoid=True):
        """
        Bilinear discrimination between embeddings and global summary.

        Args:
            emb: Embeddings [N, D]
            summary: Global summary [D]
            weight: Bilinear weight matrix [D, D]
            sigmoid: Whether to apply sigmoid

        Returns:
            Discrimination scores [N]
        """
        value = torch.matmul(emb, torch.matmul(weight, summary))
        return torch.sigmoid(value) if sigmoid else value

    def _poi_covisit_infonce(self) -> torch.Tensor:
        """T6.1 — POI↔POI co-visit InfoNCE 4th boundary.

        Pulls together the pooled-POI embeddings of POIs that co-visit within
        the same user-session window (computed at preprocess time, stored on
        ``data.covisit_pairs``) and pushes apart in-batch POIs from other
        co-visit pairs. Single deployable model — shares the Checkin2POI pool
        parameters with the existing c2p / p2r boundaries (zero new parameters
        introduced at __init__).

        Implementation: in-batch InfoNCE (SimCLR-style).
            anchors  = z_poi[a]      shape [B, D]
            positives = z_poi[p]     shape [B, D]
            scores   = anchors @ positives.T / τ     shape [B, B]
            target   = arange(B)     each row's positive is on the diagonal
            loss     = cross_entropy(scores, target)

        For each anchor a, the negatives are the OTHER positives in the batch —
        i.e. POIs that the same OR different user co-visited within their own
        sessions. This is the standard in-batch-negatives contract; we get B−1
        free negatives per anchor without an explicit negative-sampling step.

        If ``p2p_hard_neg_only`` is True, the off-diagonal pairs whose anchor
        and positive share the same region are masked out (so the loss only
        penalises "fails to discriminate from a different-region POI"). This
        is the harder variant and may regress on small states where many POIs
        share regions; default False keeps the standard in-batch contract.

        Returns the scalar mean InfoNCE loss; caller adds it with coefficient
        ``self.p2p_lambda``. Gradients flow back through z_poi and therefore
        through Checkin2POI and the check-in encoder.
        """
        z_poi = self._t6_pos_poi_emb                  # [N_pois, D]
        pairs = self._t6_covisit_pairs                # [N_pairs, 2]
        N_pairs = pairs.size(0)
        if N_pairs == 0:
            return torch.zeros((), device=z_poi.device)

        # Sample B pairs per step. If fewer pairs than batch size are
        # available, use them all (no replacement). Random sampling is the
        # cheap unbiased estimator.
        B = min(self.p2p_batch_size, N_pairs)
        if N_pairs > B:
            idx = torch.randperm(N_pairs, device=pairs.device)[:B]
            pair_batch = pairs[idx]
        else:
            pair_batch = pairs

        anchor_idx = pair_batch[:, 0]                  # [B]
        pos_idx = pair_batch[:, 1]                     # [B]
        anchors = z_poi[anchor_idx]                    # [B, D]
        positives = z_poi[pos_idx]                     # [B, D]

        # L2-normalise so the cosine-similarity scale is stable regardless of
        # the pooled vector's norm (standard contrastive practice; without it
        # the temperature interacts with the encoder's output magnitude).
        anchors = torch.nn.functional.normalize(anchors, dim=-1, eps=EPS)
        positives = torch.nn.functional.normalize(positives, dim=-1, eps=EPS)

        # [B, B] similarity matrix. The (i, i) entry is the true positive pair;
        # the (i, j ≠ i) entries are in-batch negatives.
        scores = torch.matmul(anchors, positives.t()) / self.p2p_temperature

        if self.p2p_hard_neg_only:
            # Mask out off-diagonal entries where anchor and positive share a
            # region. Without ``data.poi_to_region`` stashed on self, we can
            # fall back gracefully by using the stashed _t6_poi_to_region
            # (always present when p2r InfoNCE is on, but we don't require it).
            poi_to_region = self._t6_poi_to_region
            if poi_to_region is not None:
                anchor_regions = poi_to_region[anchor_idx]    # [B]
                pos_regions = poi_to_region[pos_idx]          # [B]
                # mask[i, j] = True if anchor i and positive j are in the same
                # region AND i ≠ j (don't mask the diagonal — it's the true pos).
                same_region = anchor_regions.unsqueeze(1) == pos_regions.unsqueeze(0)
                diag = torch.eye(B, dtype=torch.bool, device=scores.device)
                mask_out = same_region & ~diag
                scores = scores.masked_fill(mask_out, float('-inf'))

        target = torch.arange(B, device=scores.device, dtype=torch.long)
        ce_a = torch.nn.functional.cross_entropy(scores, target)
        if self.p2p_symmetric:
            # SimCLR-style: average of (anchor → positive) and (positive →
            # anchor) directions so both columns of the similarity matrix
            # contribute gradient. Doubles effective signal at fixed B.
            ce_p = torch.nn.functional.cross_entropy(scores.t(), target)
            return 0.5 * (ce_a + ce_p)
        return ce_a

    def anchor_loss(self) -> torch.Tensor:
        """v14 (delaunay_gcn) — POI2Vec anchor regulariser.

        Pulls the learnable reg-path POI table toward the frozen POI2Vec
        anchor: ``mean(‖poi_table − POI2Vec‖²)``. Mirrors
        ``Check2HGI_DesignK.anchor_loss`` exactly. Returns a zero scalar when
        the delaunay_gcn path is not active.
        """
        if self.reg_poi_mode != "delaunay_gcn" or self.reg_poi_table is None:
            return torch.zeros(())
        return ((self.reg_poi_table.weight - self.reg_poi2vec_anchor) ** 2).mean()

    def loss(self, pos_checkin, pos_poi_exp, neg_poi_exp,
             pos_poi, pos_region_exp, neg_region_exp,
             pos_region, neg_region, city):
        """
        Compute the hierarchical mutual information maximization objective.

        3 boundary losses:
        1. Check-in ↔ POI
        2. POI ↔ Region
        3. Region ↔ City

        T5.3 — Multi-view co-training. The cross-view alignment term is
        NOT added here; the wrapper ``MultiViewWrapper`` (in
        ``variants.py``) holds TWO Check2HGI instances and combines their
        per-view 3-boundary losses with a POI-level alignment:
            ``L_total = L_v1 + L_v2 + λ_x · L_cross(poi_v1, poi_v2)``.
        Keeping ``Check2HGI.loss`` strictly per-view makes the single-view
        default path bit-equivalent to canonical (T5.3 default opt-out).
        """
        # Loss 1: Check-in to POI
        pos_c2p = self.discriminate(pos_checkin, pos_poi_exp, self.weight_c2p)
        neg_c2p = self.discriminate(pos_checkin, neg_poi_exp, self.weight_c2p)
        loss_c2p = -torch.log(pos_c2p + EPS).mean() - torch.log(1 - neg_c2p + EPS).mean()

        # Loss 2: POI to Region
        if self.p2r_use_infonce:
            # T6.4 / T2.2 — InfoNCE over the full region pool. For each POI p,
            # score(p, r) = pos_poi[p] @ W_p2r @ pos_region[r]. The target is
            # poi_to_region[p]. Cross-entropy implements the InfoNCE bound.
            # Uses the FULL region matrix as the negative pool — no separate
            # neg-sampling step, so the T2.3 "two-pass corruption for p2r"
            # path has no effect when this branch is active (no negative
            # region tensor is consumed).
            if self._t6_pos_region_full is None or self._t6_poi_to_region is None:
                raise RuntimeError(
                    "p2r_use_infonce requires forward() to have been called "
                    "first (stashes pos_region matrix + poi_to_region)."
                )
            projected = torch.matmul(pos_poi, self.weight_p2r)            # [P, D]
            scores = torch.matmul(projected, self._t6_pos_region_full.t())  # [P, R]
            scores = scores / self.p2r_infonce_temperature
            loss_p2r = torch.nn.functional.cross_entropy(
                scores, self._t6_poi_to_region.to(scores.device)
            )
        else:
            pos_p2r = self.discriminate(pos_poi, pos_region_exp, self.weight_p2r)
            neg_p2r = self.discriminate(pos_poi, neg_region_exp, self.weight_p2r)
            loss_p2r = -torch.log(pos_p2r + EPS).mean() - torch.log(1 - neg_p2r + EPS).mean()

        # Loss 3: Region to City
        pos_r2c = self.discriminate_global(pos_region, city, self.weight_r2c)
        neg_r2c = self.discriminate_global(neg_region, city, self.weight_r2c)
        loss_r2c = -torch.log(pos_r2c + EPS).mean() - torch.log(1 - neg_r2c + EPS).mean()

        # Combined loss
        total_loss = (
            self.alpha_c2p * loss_c2p +
            self.alpha_p2r * loss_p2r +
            self.alpha_r2c * loss_r2c
        )

        # T4.1 — fold in masked-recon auxiliary if forward computed one.
        if self.mae_lambda > 0.0 and self._mae_loss is not None:
            total_loss = total_loss + self.mae_lambda * self._mae_loss

        # T6.1 — POI↔POI co-visit InfoNCE 4th boundary.
        # Fired only when λ > 0 AND data.covisit_pairs was passed in. Otherwise
        # the loss formulation is byte-identical to canonical.
        if self.p2p_lambda > 0.0 and self._t6_pos_poi_emb is not None and \
                self._t6_covisit_pairs is not None and self._t6_covisit_pairs.numel() > 0:
            total_loss = total_loss + self.p2p_lambda * self._poi_covisit_infonce()

        # T5.2a — fold in joint Node2Vec POI-POI skip-gram auxiliary.
        # The head computes loss on demand from a per-epoch cached walk
        # batch (set_n2v_epoch is called by the trainer per epoch). At
        # λ=0 or with no attached head the auxiliary is a no-op.
        if self.n2v_lambda > 0.0 and self.n2v_head is not None:
            l_skipgram = self.n2v_head.compute_loss(epoch_id=self._n2v_epoch_id)
            total_loss = total_loss + self.n2v_lambda * l_skipgram

            # T5.2a alignment (audit blocker #1): bridge the private n2v POI
            # table to the c2hgi encoder via the export path. Without this
            # term, skip-gram trains ONLY n2v_head.poi_table and never
            # touches checkin_encoder / Checkin2POI / POI2Region, so the
            # exported pos_poi_emb is unaffected by T5.2a.
            #
            # Math: L_align = 1 − mean( cos(pos_poi_emb[i],
            #                              n2v_head.poi_table.weight[i]) )
            # across the POI dimension. Gradient flows BOTH ways (n2v
            # table is also pulled toward pos_poi_emb), but Pytorch's autograd
            # graph for ``pos_poi_emb`` runs back through Checkin2POI ⇒
            # CheckinEncoder, which is the desired path.
            if (
                self.n2v_align_lambda > 0.0
                and self._n2v_pos_poi_emb is not None
                and hasattr(self.n2v_head, "poi_table")
            ):
                _poi_emb = self._n2v_pos_poi_emb
                _n2v_table = self.n2v_head.poi_table.weight
                # Sanity: the two tables must have the same first dim. If
                # not (e.g. share_table is on so they ARE the same tensor),
                # the alignment is identically zero and we skip it.
                if _n2v_table.shape[0] == _poi_emb.shape[0] and _n2v_table.data_ptr() != _poi_emb.data_ptr():
                    _cos = torch.nn.functional.cosine_similarity(
                        _poi_emb, _n2v_table, dim=-1, eps=EPS
                    )
                    l_align = 1.0 - _cos.mean()
                    total_loss = total_loss + self.n2v_align_lambda * l_align

        # T5.2b — fold in masked-POI feature-aggregate auxiliary.
        if (self.mae_poi_lambda > 0.0
                and self._mae_poi_loss is not None
                and torch.is_tensor(self._mae_poi_loss)):
            total_loss = total_loss + self.mae_poi_lambda * self._mae_poi_loss

        # v14 (delaunay_gcn) — fold in the POI2Vec anchor regulariser.
        if self.reg_poi_mode == "delaunay_gcn" and self.anchor_lambda > 0.0:
            total_loss = total_loss + self.anchor_lambda * self.anchor_loss()

        return total_loss

    def get_embeddings(self):
        """
        Get the current embeddings at all levels.

        Returns:
            Tuple of (checkin_embedding, poi_embedding, region_embedding)
        """
        return (
            self.checkin_embedding.clone().cpu().detach(),
            self.poi_embedding.clone().cpu().detach(),
            self.region_embedding.clone().cpu().detach()
        )

    def __repr__(self):
        return f'{self.__class__.__name__}({self.hidden_channels})'
