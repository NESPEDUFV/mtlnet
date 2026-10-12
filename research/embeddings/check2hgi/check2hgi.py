"""Check2HGI (Check-in Hierarchical Graph Infomax) embedding pipeline.

OPTIMIZED for CPU, CUDA, and MPS:
- Single encoder pass (embedding-level corruption)
- Mixed precision training (automatic device detection)
- Vectorized negative sampling
- torch.compile support for PyTorch 2.0+
"""

import argparse
import math
import pickle as pkl

import pandas as pd
import torch
import os
from torch.nn.utils import clip_grad_norm_
from torch.optim.lr_scheduler import StepLR, CosineAnnealingLR, LambdaLR
from torch_geometric.data import Data
from torch_geometric.loader import NeighborLoader
from tqdm import trange, tqdm

from configs.paths import IoPaths, EmbeddingEngine, Resources
from embeddings.check2hgi.model.Check2HGIModule import Check2HGI, corruption
from embeddings.check2hgi.model.CheckinEncoder import CheckinEncoder
from embeddings.check2hgi.model.variants import (
    GATTimeEncoder, ResidualLNEncoder,
    Time2VecCheckinEncoder, RGCNEncoder,
    Node2VecPOIHead,
    MultiViewWrapper,
)
from embeddings.check2hgi.model.Checkin2POI import Checkin2POI
from embeddings.check2hgi.preprocess import (
    preprocess_check2hgi, build_view2_graph_dict, build_view2_graph_file,
)

# Reuse POI2Region from HGI
from embeddings.hgi.model.RegionEncoder import POI2Region


def get_autocast_device_type(device):
    """Get the appropriate device type string for torch.autocast."""
    if isinstance(device, str):
        device_str = device
    else:
        device_str = str(device)

    if 'cuda' in device_str:
        return 'cuda'
    elif 'mps' in device_str:
        return 'mps'
    else:
        return 'cpu'


def supports_mixed_precision(device):
    device_type = get_autocast_device_type(device)
    if device_type == 'cuda':
        return True
    # MPS float16 can cause NaN issues with scatter/softmax operations
    # Disable by default for stability
    return False


def _multiview_train_step(model_wrapper, data_v1, data_v2, optimizer,
                          scheduler, args):
    """T5.3 — single full-batch optimization step for the MultiViewWrapper.

    Mirrors ``train_epoch_full_batch`` but routes through
    ``MultiViewWrapper.total_loss(data_v1, data_v2)`` so both encoders'
    contrastive losses + the λ_x · L_cross term are summed in one backward.
    Note: AMP is intentionally skipped here — the cross-view alignment loss
    benefits from fp32 numerics (cosine of two small embeddings) and the
    encoders already dominate the cost.
    """
    model_wrapper.train()
    optimizer.zero_grad()
    loss = model_wrapper.total_loss(data_v1, data_v2)
    loss.backward()
    clip_grad_norm_(model_wrapper.parameters(), max_norm=args.max_norm)
    optimizer.step()
    scheduler.step()
    return loss.item()


def train_epoch_full_batch(data, model, optimizer, scheduler, args, use_amp=False, device_type='cpu'):
    """Train Check2HGI model for one epoch (full batch mode).

    OPTIMIZED: Supports mixed precision training for faster execution.

    T2.4 DropEdge: if args.drop_edge_rate > 0, a fresh random mask is applied
    every epoch to the check-in edge_index / edge_weight before the forward
    pass. The mask drops a fraction `drop_edge_rate` of edges uniformly.
    Original `data` is left untouched (we wrap a temporary view).
    """
    model.train()
    optimizer.zero_grad()

    drop_rate = float(getattr(args, 'drop_edge_rate', 0.0) or 0.0)
    if drop_rate > 0.0 and hasattr(data, 'edge_index'):
        num_edges = data.edge_index.size(1)
        if bool(getattr(args, 'symmetric_drop_edge', False)):
            # T2.4 audit fix (2026-05-16 §14:45): user-sequence edges are
            # stored as paired (src→tgt, tgt→src) rows. The asymmetric
            # per-row Bernoulli (legacy below) drops the two directions
            # INDEPENDENTLY, leaving ~drop_rate × 2 (1 - drop_rate)
            # unidirectional edges — NOT the textbook DropEdge (Rong et al.
            # 2020) which drops unique undirected edges symmetrically.
            # Canonicalize each edge to (min, max), generate ONE Bernoulli
            # per unique undirected key, apply same decision to both rows.
            src_idx = data.edge_index[0]
            tgt_idx = data.edge_index[1]
            edge_key_min = torch.minimum(src_idx, tgt_idx).to(torch.int64)
            edge_key_max = torch.maximum(src_idx, tgt_idx).to(torch.int64)
            # Hash unique undirected key: min * (N+1) + max. N is conservative.
            N = int(max(src_idx.max().item(), tgt_idx.max().item())) + 1
            edge_key = edge_key_min * N + edge_key_max
            _, inverse = torch.unique(edge_key, return_inverse=True)
            n_unique = int(inverse.max().item()) + 1
            unique_keep = (
                torch.rand(n_unique, device=data.edge_index.device) >= drop_rate
            )
            keep_mask = unique_keep[inverse]
        else:
            keep_mask = torch.rand(num_edges, device=data.edge_index.device) >= drop_rate
        # Wrap data with masked edges. PyG Data objects accept attr access;
        # use a shallow copy + override only edge_* attrs.
        import copy as _copy
        data_view = _copy.copy(data)
        data_view.edge_index = data.edge_index[:, keep_mask]
        if hasattr(data, 'edge_weight') and data.edge_weight is not None:
            data_view.edge_weight = data.edge_weight[keep_mask]
        active = data_view
    else:
        active = data

    if use_amp and device_type != 'cpu':
        # Mixed precision for CUDA/MPS
        with torch.autocast(device_type=device_type, dtype=torch.float16):
            outputs = model(active)
            loss = model.loss(*outputs)
    else:
        outputs = model(active)
        loss = model.loss(*outputs)

    loss.backward()
    clip_grad_norm_(model.parameters(), max_norm=args.max_norm)
    optimizer.step()
    scheduler.step()

    return loss.item()


def train_epoch_mini_batch(data, loader, model, optimizer, args, use_amp=False, device_type='cpu'):
    """Train Check2HGI model for one epoch (mini-batch mode).

    OPTIMIZED: Supports mixed precision training for faster execution.
    """
    model.train()
    total_loss = 0
    num_batches = 0

    for batch in loader:
        batch = batch.to(args.device)
        optimizer.zero_grad()

        if use_amp and device_type != 'cpu':
            # Mixed precision for CUDA/MPS
            with torch.autocast(device_type=device_type, dtype=torch.float16):
                outputs = model(batch)
                loss = model.loss(*outputs)
        else:
            outputs = model(batch)
            loss = model.loss(*outputs)

        loss.backward()
        clip_grad_norm_(model.parameters(), max_norm=args.max_norm)
        optimizer.step()

        total_loss += loss.item()
        num_batches += 1

    return total_loss / max(num_batches, 1)


def train_check2hgi(city, args):
    """Train Check2HGI model and generate embeddings.

    OPTIMIZED:
    - Single encoder pass (2x speedup on encoder)
    - Mixed precision training (1.5-2x speedup on GPU/MPS)
    - torch.compile for additional optimization
    - Embedding extraction only at end (reduced CPU transfers)
    """
    # Bit-reproducibility (Tier-3 audit 2026-05-16, FINDING 1):
    # Encoder construction (nn.Parameter(torch.randn(...)) at variants.py and
    # CheckinEncoder) consumes from the global PRNG. Without an explicit seed
    # here, the encoder init depends on the OS-level entropy at process
    # start, making per-seed runs not bit-reproducible (the sign-test across
    # seeds remains statistically valid — each seed's INDEPENDENT random
    # init captures real init variance — but the headline number is not
    # reproducible from a re-run). Honour ``args.seed`` (defaults to 42).
    _ssl_seed = int(getattr(args, "seed", 42))
    import random as _py_random
    import numpy as _np
    _py_random.seed(_ssl_seed)
    _np.random.seed(_ssl_seed)
    torch.manual_seed(_ssl_seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(_ssl_seed)

    output_folder = IoPaths.CHECK2HGI.get_state_dir(city)
    output_folder.mkdir(parents=True, exist_ok=True)

    # Load preprocessed data
    data_path = IoPaths.CHECK2HGI.get_graph_data_file(city)
    print(f"Loading data: {data_path}")

    with open(data_path, 'rb') as handle:
        city_dict = pkl.load(handle)

    in_channels = city_dict['node_features'].shape[1]
    num_checkins = city_dict['num_checkins']
    num_pois = city_dict['num_pois']
    num_regions = city_dict['num_regions']

    print(f"Check-ins: {num_checkins}, POIs: {num_pois}, Regions: {num_regions}, Features: {in_channels}")

    # Create PyTorch Geometric Data object
    # Keep on CPU initially for DataLoader compatibility (especially MPS)
    _data_kwargs = dict(
        x=torch.tensor(city_dict['node_features'], dtype=torch.float32),
        edge_index=torch.tensor(city_dict['edge_index'], dtype=torch.int64),
        edge_weight=torch.tensor(city_dict['edge_weight'], dtype=torch.float32),
        checkin_to_poi=torch.tensor(city_dict['checkin_to_poi'], dtype=torch.int64),
        poi_to_region=torch.tensor(city_dict['poi_to_region'], dtype=torch.int64),
        region_adjacency=torch.tensor(city_dict['region_adjacency'], dtype=torch.int64),
        region_area=torch.tensor(city_dict['region_area'], dtype=torch.float32),
        coarse_region_similarity=torch.tensor(city_dict['coarse_region_similarity'], dtype=torch.float32),
        num_pois=num_pois,
        num_regions=num_regions,
    )
    # T3.3 plumbing: expose per-edge relation index for R-GCN (only present
    # on freshly-preprocessed graphs; legacy cached graphs omit it).
    if 'edge_type' in city_dict:
        _data_kwargs['edge_type'] = torch.tensor(city_dict['edge_type'], dtype=torch.int64)
    data = Data(**_data_kwargs)

    # T6.1 — attach the co-visit POI-POI pair list when present in the cache.
    # Consumed at training time by Check2HGIModule._poi_covisit_infonce()
    # when p2p_lambda > 0. Stored on `data` so the trainer's `batch.to(device)`
    # picks it up automatically.
    if 'covisit_pairs' in city_dict:
        data.covisit_pairs = torch.as_tensor(city_dict['covisit_pairs'], dtype=torch.int64)

    metadata = city_dict['metadata']

    # Initialize model components
    # T3 encoder swap.
    # **v12 DEFAULT FLIP (2026-05-30): `args.encoder` now defaults to "resln"
    # (ResidualLNEncoder, T3.2) — the best STL cat encoder (cat F1 +0.86 FL /
    # +1.48 AL / +1.70 AZ, 5/5 seeds, canonical_improvement T3.2). This affects
    # FUTURE Check2HGI builds ONLY; the frozen v11 paper substrate on disk
    # (output/check2hgi/<state>/) was built with GCN and must NOT be
    # overwritten. Pass --encoder gcn to rebuild the v11 (GCN) substrate.
    # NOTE: ResLN gives NO MTL benefit (the regime finding) — its value is
    # STL/representation-quality, not MTL reg/cat. See
    # docs/results/CANONICAL_VERSIONS.md (v11 GCN vs v12 ResLN).**
    # Other choices:
    #   "gcn"     — CheckinEncoder, the canonical 2-layer GCN (v11 paper substrate).
    #   "gat"     — GATTimeEncoder, attention with optional edge-weight conditioning (T3.1).
    #   "resln"   — ResidualLNEncoder, GCN-family with residual + LayerNorm (T3.2, v12 default).
    #   "time2vec"— Time2VecCheckinEncoder, learned-frequency replacement for the
    #               4 fixed sin/cos temporal cols (T3.4).
    #   "rgcn"    — RGCNEncoder, relation-typed aggregation; requires K≥2 relations
    #               i.e. a graph preprocessed with edge_type='both' (T3.3 Option A).
    _encoder_name = getattr(args, 'encoder', 'resln') or 'resln'
    if getattr(args, 'encoder', None) in (None, 'resln'):
        print(
            "[encoder] default ResLN (v12); pass --encoder gcn for v11"
        )
    if _encoder_name == 'gat':
        _gat_heads = int(getattr(args, 'gat_heads', 4))
        _gat_dropout = float(getattr(args, 'encoder_dropout', 0.0) or 0.0)
        _gat_use_edge_attr = bool(getattr(args, 'gat_use_edge_attr', True))
        checkin_encoder = GATTimeEncoder(in_channels, args.dim, num_layers=args.num_layers,
                                          heads=_gat_heads, dropout=_gat_dropout,
                                          use_edge_attr=_gat_use_edge_attr)
        print(f"[encoder] GATTimeEncoder heads={_gat_heads} dropout={_gat_dropout} use_edge_attr={_gat_use_edge_attr}")
    elif _encoder_name == 'resln':
        _resln_dropout = float(getattr(args, 'encoder_dropout', 0.0) or 0.0)
        checkin_encoder = ResidualLNEncoder(in_channels, args.dim, num_layers=args.num_layers,
                                             dropout=_resln_dropout)
        print(f"[encoder] ResidualLNEncoder dropout={_resln_dropout}")
    elif _encoder_name == 'time2vec':
        _t2v_dim = int(getattr(args, 'time2vec_dim', 8))
        _t2v_dropout = float(getattr(args, 'encoder_dropout', 0.0) or 0.0)
        _t2v_warm = bool(getattr(args, 'time2vec_warm_start', False))
        # The preprocess output is [category_onehot (num_cat), temporal (4)].
        # Number of categories = in_channels - 4.
        _num_cat = in_channels - 4
        checkin_encoder = Time2VecCheckinEncoder(
            in_channels, args.dim, num_categories=_num_cat,
            num_layers=args.num_layers, time2vec_dim=_t2v_dim,
            dropout=_t2v_dropout, warm_start=_t2v_warm,
        )
        print(f"[encoder] Time2VecCheckinEncoder d_t={_t2v_dim} num_cat={_num_cat} dropout={_t2v_dropout} warm_start={_t2v_warm}")
    elif _encoder_name == 'rgcn':
        if not hasattr(data, 'edge_type'):
            raise ValueError(
                "encoder='rgcn' requires the preprocessed graph to expose "
                "per-edge relation index. Re-preprocess with edge_type='both' "
                "(force_preprocess=True) and try again."
            )
        _num_relations = int(getattr(args, 'rgcn_num_relations', 2))
        _num_bases = getattr(args, 'rgcn_num_bases', 2)
        if isinstance(_num_bases, str) and _num_bases.lower() == 'none':
            _num_bases = None
        if _num_bases is not None:
            _num_bases = int(_num_bases)
        _rgcn_aggr = str(getattr(args, 'rgcn_aggr', 'sum'))
        _rgcn_dropout = float(getattr(args, 'encoder_dropout', 0.0) or 0.0)
        checkin_encoder = RGCNEncoder(
            in_channels, args.dim, num_relations=_num_relations,
            num_layers=args.num_layers, num_bases=_num_bases,
            dropout=_rgcn_dropout, aggr=_rgcn_aggr,
        )
        print(f"[encoder] RGCNEncoder K={_num_relations} bases={_num_bases} aggr={_rgcn_aggr} dropout={_rgcn_dropout}")
    else:
        checkin_encoder = CheckinEncoder(in_channels, args.dim, num_layers=args.num_layers)
        print(f"[encoder] CheckinEncoder (canonical GCN)")
    # T6.3 — low-rank per-POI bias at the Checkin2POI attention-logit. Gated
    # by ``args.t63_enabled``; default off ⇒ canonical bit-identical.
    _t63_enabled = bool(getattr(args, 't63_enabled', False))
    _t63_rank = int(getattr(args, 't63_rank', 8))
    if _t63_enabled:
        print(f"[T6.3] Checkin2POI per-POI bias enabled rank={_t63_rank} num_pois={num_pois}")
    checkin2poi = Checkin2POI(
        args.dim, args.attention_head,
        t63_enabled=_t63_enabled,
        t63_num_pois=int(num_pois) if _t63_enabled else None,
        t63_rank=_t63_rank,
    )
    poi2region = POI2Region(args.dim, args.attention_head)

    def region2city(z, area):
        return torch.sigmoid((z.transpose(0, 1) * area).sum(dim=1))

    # T4.3 — side-feature plumbing. If --use-side-features is set, load the
    # precomputed (num_pois, side_feature_dim) tensor from disk and attach to
    # the Data object so the forward pass can inject it post-pool.
    _use_side_features = bool(getattr(args, 'use_side_features', False))
    _side_feature_dim = 0
    _side_feature_hidden = int(getattr(args, 'side_feature_hidden', 16))
    if _use_side_features:
        from pathlib import Path as _Path
        _sf_path = _Path(IoPaths.CHECK2HGI.get_state_dir(city)) / "poi_side_features.pt"
        if not _sf_path.exists():
            raise FileNotFoundError(
                f"--use-side-features requires precomputed {_sf_path}. Run "
                f"`python scripts/compute_poi_side_features.py --state {city}` first."
            )
        _sf_payload = torch.load(_sf_path, weights_only=False)
        _sf_tensor = _sf_payload["features"].to(dtype=torch.float32)
        if _sf_tensor.shape[0] != int(num_pois):
            raise ValueError(
                f"side_features rows {_sf_tensor.shape[0]} != num_pois {num_pois}; "
                f"recompute side features (preprocess cache changed)."
            )
        # Attach to data (moved to device with the rest below).
        data.side_features = _sf_tensor
        _side_feature_dim = int(_sf_tensor.shape[1])
        print(f"[T4.3] side_features attached shape={tuple(_sf_tensor.shape)} "
              f"hidden={_side_feature_hidden}")

    # T4.1 — GraphMAE plumbing.
    _mae_lambda = float(getattr(args, 'mae_lambda', 0.0) or 0.0)
    _mae_mask_rate = float(getattr(args, 'mae_mask_rate', 0.5) or 0.5)
    _mae_gamma = float(getattr(args, 'mae_gamma', 3.0) or 3.0)
    if _mae_lambda > 0.0:
        print(f"[T4.1] GraphMAE enabled λ={_mae_lambda} mask_rate={_mae_mask_rate} γ={_mae_gamma}")

    # T5.2a — Joint Node2Vec POI-POI skip-gram plumbing.
    # Default λ=0.0 → head not constructed, no behavior change. When enabled,
    # we require ``poi_delaunay_edge_index`` in the preprocessed graph
    # (built when ``args.build_poi_delaunay=True`` was passed at preprocess).
    _n2v_lambda = float(getattr(args, 'n2v_lambda', 0.0) or 0.0)
    if _n2v_lambda > 0.0:
        if 'poi_delaunay_edge_index' not in city_dict:
            raise RuntimeError(
                "T5.2a: --use-node2vec-poi requires the preprocessed graph to "
                "include 'poi_delaunay_edge_index'. Re-run preprocess with "
                "build_poi_delaunay=True (force_preprocess=True is set "
                "automatically by regen_emb_t3.py when --use-node2vec-poi is on)."
            )
        print(f"[T5.2a] Node2Vec POI-POI skip-gram enabled λ={_n2v_lambda} "
              f"walk_length={getattr(args, 'n2v_walk_length', 10)} "
              f"num_walks={getattr(args, 'n2v_num_walks', 5)} "
              f"p={getattr(args, 'n2v_p', 1.0)} q={getattr(args, 'n2v_q', 1.0)} "
              f"share_with_poi_id={bool(getattr(args, 'n2v_share_table_with_poi_id', False))} "
              f"align_lambda={float(getattr(args, 'n2v_align_lambda', 0.0) or 0.0)}")

    # T5.1 — Native learned POI ID embedding plumbing.
    # Pull ``num_pois`` from the preprocessed graph (NEVER hard-coded).
    _use_poi_id_embedding = bool(getattr(args, 'use_poi_id_embedding', False))
    _poi_id_gamma = float(getattr(args, 'poi_id_gamma', 0.3) or 0.3)
    _poi_id_init = str(getattr(args, 'poi_id_init', 'zero'))
    if _use_poi_id_embedding:
        print(f"[T5.1] POI ID embedding enabled γ={_poi_id_gamma} "
              f"init={_poi_id_init} num_pois={num_pois}")

    # T5.2b — Masked POI feature-aggregate plumbing. Default opt-out
    # (mae_poi_lambda=0 ⇒ canonical behaviour preserved bit-for-bit).
    _mae_poi_lambda = float(getattr(args, 'mae_poi_lambda', 0.0) or 0.0)
    _mae_poi_mask_rate = float(getattr(args, 'mae_poi_mask_rate', 0.15) or 0.15)
    _mae_poi_gamma = float(getattr(args, 'mae_poi_gamma', 3.0) or 3.0)
    _mae_poi_target_kind = str(getattr(args, 'mae_poi_target', 'category_aggregate'))
    _mae_poi_aggr = str(getattr(args, 'mae_poi_aggr', 'mean'))
    _mae_poi_loss_kind = str(getattr(args, 'mae_poi_loss_kind', 'sce'))
    _mae_poi_target_dim = 0
    if _mae_poi_lambda > 0.0:
        # Required: POI Delaunay edges + per-POI reconstruction target.
        # Both are produced by preprocess_check2hgi(build_poi_delaunay=True,
        # build_poi_aggregates=True). If the cached graph predates T5.2b,
        # rebuild it (set --force-preprocess at the regen script entry).
        if 'poi_delaunay_edge_index' not in city_dict:
            raise ValueError(
                "[T5.2b] mae_poi_lambda > 0 but cached graph has no "
                "'poi_delaunay_edge_index'. Re-run preprocess with "
                "build_poi_delaunay=True (force_preprocess=True from regen_emb_t3)."
            )
        if 'poi_category_aggregate' not in city_dict:
            raise ValueError(
                "[T5.2b] mae_poi_lambda > 0 but cached graph has no "
                "'poi_category_aggregate'. Re-run preprocess with "
                "build_poi_aggregates=True (force_preprocess=True)."
            )
        # Build the target tensor according to mae_poi_target choice.
        _cat_agg = torch.tensor(city_dict['poi_category_aggregate'], dtype=torch.float32)
        _visit_log = torch.tensor(
            city_dict['poi_visit_count_log'], dtype=torch.float32
        ).unsqueeze(-1)  # (P, 1)
        if _mae_poi_target_kind == 'category_aggregate':
            recon_target = _cat_agg                                # (P, num_cat)
        elif _mae_poi_target_kind == 'visit_count_log':
            recon_target = _visit_log                              # (P, 1)
        elif _mae_poi_target_kind == 'both':
            recon_target = torch.cat([_cat_agg, _visit_log], dim=-1)  # (P, num_cat+1)
        else:
            raise ValueError(
                f"[T5.2b] mae_poi_target must be 'category_aggregate', "
                f"'visit_count_log', or 'both'; got {_mae_poi_target_kind!r}"
            )
        # MSE for visit_count_log (unbounded scalar); SCE for the others
        # (cosine-on-distribution natural for category_aggregate).
        if _mae_poi_target_kind == 'visit_count_log' and _mae_poi_loss_kind == 'sce':
            print("[T5.2b] auto-switching loss_kind to 'mse' for visit_count_log target.")
            _mae_poi_loss_kind = 'mse'

        _mae_poi_target_dim = int(recon_target.shape[1])
        _poi_edges_t = torch.tensor(
            city_dict['poi_delaunay_edge_index'], dtype=torch.int64
        )
        # Attach to Data; moved to device with the rest below.
        data.poi_delaunay_edge_index = _poi_edges_t
        data.poi_recon_target = recon_target
        print(f"[T5.2b] MaskedPOI decoder enabled λ={_mae_poi_lambda} "
              f"mask_rate={_mae_poi_mask_rate} γ={_mae_poi_gamma} "
              f"target={_mae_poi_target_kind} ({_mae_poi_target_dim}d) "
              f"aggr={_mae_poi_aggr} loss={_mae_poi_loss_kind} "
              f"edges={_poi_edges_t.shape[1]}")

    # ──────────────────────────────────────────────────────────────────────
    # v13 / v14 — reg-path POI augmentation (graduated from scripts/probe).
    # Default reg_poi_mode='none' ⇒ NOTHING loaded, model bit-identical.
    #   v13 = --reg-poi-mode poi2vec_residual --encoder resln
    #   v14 = --reg-poi-mode delaunay_gcn --encoder resln --mae-poi-lambda 0.3
    #         --anchor-lambda 0.1
    _reg_poi_mode = str(getattr(args, 'reg_poi_mode', 'none') or 'none')
    _reg_gamma_init = float(getattr(args, 'gamma_init', 1.0) or 1.0)
    _reg_anchor_lambda = float(getattr(args, 'anchor_lambda', 0.0) or 0.0)
    _poi2vec_table = None
    _delaunay_ei = None
    _delaunay_ew = None
    if _reg_poi_mode != 'none':
        from embeddings.check2hgi.reg_poi_aug import (
            load_poi2vec_table as _load_poi2vec_table,
            load_delaunay_edges as _load_delaunay_edges,
        )
        _placeid_to_idx = city_dict['placeid_to_idx']
        _poi2vec_table = _load_poi2vec_table(city, int(num_pois), _placeid_to_idx)
        print(f"[reg_poi] mode={_reg_poi_mode} γ_init={_reg_gamma_init} "
              f"anchor_λ={_reg_anchor_lambda} poi2vec_table={tuple(_poi2vec_table.shape)}")
        if _reg_poi_mode == 'delaunay_gcn':
            _delaunay_ei, _delaunay_ew = _load_delaunay_edges(
                city, _placeid_to_idx, int(num_pois),
                poi_to_region=city_dict['poi_to_region'])
            print(f"[reg_poi] delaunay edges={_delaunay_ei.shape[1]}")

    model = Check2HGI(
        hidden_channels=args.dim,
        checkin_encoder=checkin_encoder,
        checkin2poi=checkin2poi,
        poi2region=poi2region,
        region2city=region2city,
        corruption=corruption,
        alpha_c2p=args.alpha_c2p,
        alpha_p2r=args.alpha_p2r,
        alpha_r2c=args.alpha_r2c,
        c2p_hard_neg_prob=getattr(args, 'c2p_hard_neg_prob', 0.0),
        c2p_corrupted_neg=getattr(args, 'c2p_corrupted_neg', False),
        p2r_hard_neg_prob=getattr(args, 'p2r_hard_neg_prob', None),
        p2r_hard_neg_min_batch=getattr(args, 'p2r_hard_neg_min_batch', 50000),
        p2r_hard_neg_sim_range=getattr(args, 'p2r_hard_neg_sim_range', (0.6, 0.8)),
        side_feature_dim=_side_feature_dim,
        side_feature_hidden=_side_feature_hidden,
        mae_lambda=_mae_lambda,
        mae_mask_rate=_mae_mask_rate,
        mae_gamma=_mae_gamma,
        mae_in_channels=in_channels if _mae_lambda > 0.0 else None,
        n2v_lambda=_n2v_lambda,
        n2v_align_lambda=float(getattr(args, 'n2v_align_lambda', 0.0) or 0.0),
        use_poi_id_embedding=_use_poi_id_embedding,
        poi_id_gamma=_poi_id_gamma,
        poi_id_init=_poi_id_init,
        num_pois=int(num_pois) if _use_poi_id_embedding else None,
        mae_poi_lambda=_mae_poi_lambda,
        mae_poi_mask_rate=_mae_poi_mask_rate,
        mae_poi_gamma=_mae_poi_gamma,
        mae_poi_target_dim=_mae_poi_target_dim,
        mae_poi_aggr=_mae_poi_aggr,
        mae_poi_target_kind=_mae_poi_target_kind,
        mae_poi_loss_kind=_mae_poi_loss_kind,
        # T6.4 — Tier-6 loss-shape options (default off ⇒ canonical).
        p2r_use_infonce=bool(getattr(args, 'p2r_use_infonce', False)),
        p2r_infonce_temperature=float(getattr(args, 'p2r_infonce_temperature', 0.1)),
        two_pass_corruption=bool(getattr(args, 'two_pass_corruption', False)),
        # T6.1 — POI↔POI co-visit InfoNCE 4th boundary (default off ⇒ canonical).
        p2p_lambda=float(getattr(args, 'p2p_lambda', 0.0) or 0.0),
        p2p_temperature=float(getattr(args, 'p2p_temperature', 0.1) or 0.1),
        p2p_batch_size=int(getattr(args, 'p2p_batch_size', 1024) or 1024),
        p2p_hard_neg_only=bool(getattr(args, 'p2p_hard_neg_only', False)),
        p2p_symmetric=bool(getattr(args, 'p2p_symmetric', False)),
        # v13 / v14 — reg-path POI augmentation (default off ⇒ canonical).
        reg_poi_mode=_reg_poi_mode,
        gamma_init=_reg_gamma_init,
        anchor_lambda=_reg_anchor_lambda,
        poi2vec_table=_poi2vec_table,
        delaunay_edge_index=_delaunay_ei,
        delaunay_edge_weight=_delaunay_ew,
    ).to(args.device)

    # T6.1 — sanity: if p2p_lambda > 0, the preprocess must have populated
    # ``data.covisit_pairs``. The cache-detection block above forces a fresh
    # preprocess when the artefact is missing, so this is a belt-and-braces
    # check that catches stale code paths or missing args.
    if float(getattr(args, 'p2p_lambda', 0.0) or 0.0) > 0.0:
        if getattr(data, 'covisit_pairs', None) is None:
            raise ValueError(
                "[T6.1] p2p_lambda > 0 but data.covisit_pairs is None. "
                "Run preprocess with build_covisit_pairs=True (force_preprocess=True "
                "is added automatically when --p2p-lambda > 0, but the cached "
                "graph may need to be rebuilt explicitly the first time)."
            )
        _n_covisit = int(data.covisit_pairs.size(0))
        print(f"[T6.1] POI-co-visit InfoNCE 4th boundary enabled "
              f"lambda={float(args.p2p_lambda)} tau={float(getattr(args, 'p2p_temperature', 0.1))} "
              f"batch={int(getattr(args, 'p2p_batch_size', 1024))} k={int(getattr(args, 'p2p_covisit_k', 3))} "
              f"hard_neg_only={bool(getattr(args, 'p2p_hard_neg_only', False))} "
              f"n_covisit_pairs={_n_covisit}")

    # T5.2a — construct + attach Node2Vec head AFTER model is on device.
    # The head's parameters (separate POI table by default) are then
    # picked up by the optimizer constructed below.
    if _n2v_lambda > 0.0:
        _n2v_edge_index = torch.tensor(
            city_dict['poi_delaunay_edge_index'], dtype=torch.long
        )
        # Optional T5.1 coupling: share_table_with_poi_id reuses the T5.1
        # POI identity table when present. T5.1's hook on the Check2HGI
        # model is named ``poi_id_table`` (per audit-corrected contract).
        # If the user passes --n2v-share-table-with-poi-id but T5.1 is NOT
        # enabled, treat that as a configuration error rather than a silent
        # fallback (audit T5.2a blocker #2).
        _share = bool(getattr(args, 'n2v_share_table_with_poi_id', False))
        _external = getattr(model, 'poi_id_table', None) if _share else None
        if _share and _external is None:
            raise ValueError(
                "--n2v-share-table-with-poi-id requires --use-poi-id-embedding "
                "to be enabled in the same run (T5.1 hook ``poi_id_table`` not "
                "found on the model)."
            )
        n2v_head = Node2VecPOIHead(
            num_pois=num_pois,
            embedding_dim=args.dim,
            edge_index=_n2v_edge_index,
            walk_length=int(getattr(args, 'n2v_walk_length', 10)),
            context_size=int(getattr(args, 'n2v_context_size', 5)),
            walks_per_node=int(getattr(args, 'n2v_num_walks', 5)),
            p=float(getattr(args, 'n2v_p', 1.0)),
            q=float(getattr(args, 'n2v_q', 1.0)),
            num_negatives=int(getattr(args, 'n2v_num_negatives', 5)),
            share_table=_share,
            external_table=_external,
        ).to(args.device)
        # ``attach_node2vec_head`` registers via ``add_module`` so optimizer
        # picks up the parameters; the redundant outer ``add_module`` was
        # dropped per audit cleanup #3.
        model.attach_node2vec_head(n2v_head)

    # ------------------------------------------------------------------
    # T5.3 — Multi-view co-training (cross-view POI alignment)
    # ------------------------------------------------------------------
    # Default opt-out: when ``use_multiview`` is False the pre-existing
    # single-view ``model`` is left untouched and trained as canonical.
    # When True, we build a second Check2HGI (View 2) over the same_poi-only
    # / category-one-hot graph, wrap (V1, V2) in MultiViewWrapper, and
    # route the full-batch training loop through wrapper.total_loss.
    _use_multiview = bool(getattr(args, 'use_multiview', False))
    multiview_wrapper = None
    data_v2 = None
    if _use_multiview:
        _mv_lambda = float(getattr(args, 'multiview_lambda', 0.3) or 0.3)
        _mv_loss = str(getattr(args, 'multiview_loss', 'cosine') or 'cosine')
        _mv_share = bool(getattr(args, 'multiview_share_encoder', False))
        _mv_export = str(getattr(args, 'multiview_export_view', 'v1') or 'v1')
        _mv_temp = float(getattr(args, 'multiview_temperature', 0.2) or 0.2)

        # 1. Ensure the View-2 cache exists; build from canonical if missing.
        view2_path = data_path.parent / "view2_graph.pt"
        if not view2_path.exists():
            print(f"[T5.3] View-2 cache missing → building from canonical at {view2_path}")
            build_view2_graph_file(city)

        with open(view2_path, 'rb') as _f:
            view2_dict = pkl.load(_f)
        v2_in_channels = view2_dict['node_features'].shape[1]
        print(f"[T5.3] View 2: features={view2_dict['node_features'].shape} "
              f"edges={view2_dict['edge_index'].shape[1]} "
              f"(category-one-hot only, same_poi-only edges)")

        # 2. Construct the View-2 PyG Data object — identical schema to V1
        # but with view-2 node features / edges. checkin_to_poi mappings are
        # shared so the POI-level alignment is well-defined.
        v2_data_kwargs = dict(
            x=torch.tensor(view2_dict['node_features'], dtype=torch.float32),
            edge_index=torch.tensor(view2_dict['edge_index'], dtype=torch.int64),
            edge_weight=torch.tensor(view2_dict['edge_weight'], dtype=torch.float32),
            checkin_to_poi=torch.tensor(view2_dict['checkin_to_poi'], dtype=torch.int64),
            poi_to_region=torch.tensor(view2_dict['poi_to_region'], dtype=torch.int64),
            region_adjacency=torch.tensor(view2_dict['region_adjacency'], dtype=torch.int64),
            region_area=torch.tensor(view2_dict['region_area'], dtype=torch.float32),
            coarse_region_similarity=torch.tensor(view2_dict['coarse_region_similarity'], dtype=torch.float32),
            num_pois=num_pois,
            num_regions=num_regions,
        )
        if 'edge_type' in view2_dict:
            v2_data_kwargs['edge_type'] = torch.tensor(view2_dict['edge_type'], dtype=torch.int64)
        data_v2 = Data(**v2_data_kwargs)

        # 3. Build View-2 Check2HGI: same architecture as canonical, but with
        # a fresh CheckinEncoder sized to view-2's feature dim, fresh
        # Checkin2POI / POI2Region heads, and the same loss weights. We do
        # NOT propagate T4.x/T5.x add-ons (side features, MAE, Node2Vec) to
        # View 2 — keep it minimal so V2's signal is purely "POI category
        # structure under same_poi-only edges". The default opt-out for
        # other T5 features is honoured.
        checkin_encoder_v2 = CheckinEncoder(
            v2_in_channels, args.dim, num_layers=args.num_layers
        )
        checkin2poi_v2 = Checkin2POI(args.dim, args.attention_head)
        poi2region_v2 = POI2Region(args.dim, args.attention_head)

        model_v2 = Check2HGI(
            hidden_channels=args.dim,
            checkin_encoder=checkin_encoder_v2,
            checkin2poi=checkin2poi_v2,
            poi2region=poi2region_v2,
            region2city=region2city,
            corruption=corruption,
            alpha_c2p=args.alpha_c2p,
            alpha_p2r=args.alpha_p2r,
            alpha_r2c=args.alpha_r2c,
        ).to(args.device)

        # 4. Wrap. View 1 is the existing ``model``; the wrapper takes over
        # as the optimizer target so its parameters (V1 + V2 + shared
        # discriminators) all get gradient updates.
        multiview_wrapper = MultiViewWrapper(
            model_v1=model,
            model_v2=model_v2,
            cross_lambda=_mv_lambda,
            cross_loss=_mv_loss,
            cross_temperature=_mv_temp,
            share_encoder=_mv_share,
        ).to(args.device)
        print(f"[T5.3] MultiViewWrapper enabled λ_x={_mv_lambda} loss={_mv_loss} "
              f"share_encoder={_mv_share} export_view={_mv_export} "
              f"(2× compute when share_encoder=False)")

    print(f"Parameters: {sum(p.numel() for p in model.parameters()):,}")
    if multiview_wrapper is not None:
        print(f"Multi-view total parameters: "
              f"{sum(p.numel() for p in multiview_wrapper.parameters()):,}")

    # Note: torch.compile is NOT compatible with PyTorch Geometric's dynamic
    # scatter operations used in this model (POI2Region uses pyg_softmax with
    # dynamic tensor sizes). Skipping compilation.
    if args.use_compile:
        print("Warning: torch.compile disabled - incompatible with PyG scatter operations")

    # Setup mixed precision training
    device_type = get_autocast_device_type(args.device)
    use_amp = args.use_amp and supports_mixed_precision(args.device)
    if use_amp:
        print(f"Using mixed precision training (device: {device_type})")
    else:
        print(f"Using full precision training (device: {device_type})")

    # T1.5 optimizer hygiene knobs (default = canonical Adam + constant LR; opt-in).
    weight_decay = float(getattr(args, 'weight_decay', 0.0) or 0.0)
    scheduler_type = getattr(args, 'scheduler', 'step') or 'step'
    warmup_pct = float(getattr(args, 'warmup_pct', 0.0) or 0.0)
    eta_min_ratio = float(getattr(args, 'eta_min_ratio', 0.01) or 0.01)
    # T5.3 — when multi-view is enabled, the optimizer target is the wrapper
    # so View 2's parameters get gradient updates too.
    _opt_target = multiview_wrapper if multiview_wrapper is not None else model
    if weight_decay > 0:
        optimizer = torch.optim.AdamW(_opt_target.parameters(), lr=args.lr, weight_decay=weight_decay)
        print(f"[opt] AdamW lr={args.lr} wd={weight_decay}")
    else:
        optimizer = torch.optim.Adam(_opt_target.parameters(), lr=args.lr)
        print(f"[opt] Adam lr={args.lr} (no WD)")

    total_steps = int(args.epoch)
    if scheduler_type == 'cosine':
        if warmup_pct > 0:
            warmup_steps = max(1, int(warmup_pct * total_steps))

            def _lr_lambda(step):
                if step < warmup_steps:
                    return float(step + 1) / float(warmup_steps)
                progress = (step - warmup_steps) / max(1.0, float(total_steps - warmup_steps))
                return 0.5 * (1.0 + math.cos(math.pi * progress))

            scheduler = LambdaLR(optimizer, lr_lambda=_lr_lambda)
            print(f"[sched] warmup-cosine warmup_pct={warmup_pct} eta_min_ratio={eta_min_ratio}")
        else:
            scheduler = CosineAnnealingLR(
                optimizer, T_max=total_steps, eta_min=args.lr * eta_min_ratio
            )
            print(f"[sched] cosine T_max={total_steps} eta_min_ratio={eta_min_ratio}")
    elif scheduler_type == 'warmup_constant':
        warmup_steps = max(1, int(warmup_pct * total_steps))

        def _lr_lambda_wc(step):
            return min(1.0, float(step + 1) / float(warmup_steps))

        scheduler = LambdaLR(optimizer, lr_lambda=_lr_lambda_wc)
        print(f"[sched] warmup-constant warmup_pct={warmup_pct}")
    else:
        # Default — canonical StepLR (constant when gamma=1.0). Bit-equivalent.
        scheduler = StepLR(optimizer, step_size=1, gamma=args.gamma)

    # Choose training mode based on data size
    use_mini_batch = num_checkins > args.mini_batch_threshold

    if use_mini_batch:
        print(f"Using mini-batch training (threshold: {args.mini_batch_threshold})")
        # Keep data on CPU for DataLoader (MPS/CUDA tensors can't be shared across workers)
        # Batches will be moved to device during training
        num_workers = min(8, os.cpu_count() or 1)
        loader = NeighborLoader(
            data,
            num_neighbors=[args.num_neighbors] * args.num_layers,
            batch_size=args.batch_size,
            shuffle=True,
            input_nodes=None,
            num_workers=num_workers,
            pin_memory=True if torch.cuda.is_available() else False,
            prefetch_factor=5 if num_workers > 0 else None,
            persistent_workers = num_workers > 0,
        )
    else:
        print("Using full-batch training")
        # Move entire dataset to device for full-batch mode
        data = data.to(args.device)
        loader = None
        if data_v2 is not None:
            data_v2 = data_v2.to(args.device)

    # T5.3 — multi-view does not support mini-batch yet (NeighborLoader would
    # need to be sharded per-view, and the cross-view POI alignment assumes
    # the full POI set is materialised in each step). Fall back to a clear
    # error so users don't silently get a single-view run.
    if multiview_wrapper is not None and use_mini_batch:
        raise NotImplementedError(
            "T5.3: --use-multiview is only wired through full-batch training. "
            "num_checkins exceeds mini_batch_threshold — bump --mini-batch-threshold "
            "or run on a smaller state."
        )

    # Training loop
    # OPTIMIZED: Track best epoch, only extract embeddings at the end
    t = trange(1, args.epoch + 1, desc="Training Check2HGI")
    lowest_loss = math.inf
    best_epoch = 0
    # T5.3 — state tracking object is the wrapper when multiview is on so V2
    # weights are restored along with V1 at the end of training.
    _ckpt_target = multiview_wrapper if multiview_wrapper is not None else model

    for epoch in t:
        # T5.2a — bump cached-walks epoch id so the Node2Vec head re-samples
        # walks once at the start of each epoch (spec: "one batch of walks
        # per epoch"). No-op when the head is not attached.
        if hasattr(model, 'set_n2v_epoch'):
            model.set_n2v_epoch(epoch)
        if multiview_wrapper is not None:
            # T5.3 full-batch step routes through wrapper.total_loss.
            loss = _multiview_train_step(
                multiview_wrapper, data, data_v2, optimizer, scheduler, args
            )
        elif use_mini_batch:
            loss = train_epoch_mini_batch(data, loader, model, optimizer, args, use_amp, device_type)
        else:
            loss = train_epoch_full_batch(data, model, optimizer, scheduler, args, use_amp, device_type)

        if loss < lowest_loss:
            lowest_loss = loss
            best_epoch = epoch
            # Save model state instead of extracting embeddings every time
            best_state = {k: v.clone() for k, v in _ckpt_target.state_dict().items()}

        t.set_postfix(loss=f'{loss:.4f}', best=f'{lowest_loss:.4f}', best_epoch=best_epoch)

    # Load best model and extract embeddings only once at the end
    print(f"Loading best model from epoch {best_epoch}")
    _ckpt_target.load_state_dict(best_state)

    # Final forward pass to get embeddings
    # Move data to device if needed (for mini-batch mode where data stayed on CPU).
    # Use a generic parameter-iteration check (encoder-agnostic; GATv2Conv has
    # `lin_l/lin_r` rather than `lin`).
    _enc_param = next(model.checkin_encoder.parameters())
    if data.x.device != _enc_param.device:
        data = data.to(args.device)
        if data_v2 is not None:
            data_v2 = data_v2.to(args.device)

    if multiview_wrapper is not None:
        multiview_wrapper.eval()
        _export_view = str(getattr(args, 'multiview_export_view', 'v1') or 'v1')
        with torch.no_grad():
            # Run both views so their internal embedding caches are populated.
            multiview_wrapper(data, data_v2)
            checkin_emb, poi_emb, region_emb = multiview_wrapper.get_embeddings(
                which=_export_view
            )
        print(f"[T5.3] Exporting {_export_view} embeddings (per spec: V1 by default — "
              f"cat-friendly view).")
    else:
        model.eval()
        with torch.no_grad():
            _ = model(data)
            checkin_emb, poi_emb, region_emb = model.get_embeddings()

    # Save check-in embeddings
    output_path = IoPaths.get_embedd(city, EmbeddingEngine.CHECK2HGI)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    embeddings_np = checkin_emb.numpy()

    df = pd.DataFrame(embeddings_np, columns=[f'{i}' for i in range(embeddings_np.shape[1])])
    df.insert(0, 'datetime', metadata['datetime'].values)
    df.insert(0, 'category', metadata['category'].values)
    df.insert(0, 'placeid', metadata['placeid'].values)
    df.insert(0, 'userid', metadata['userid'].values)
    df.to_parquet(output_path, index=False)
    print(f"Check-in embeddings: {output_path} {embeddings_np.shape}")

    # Also save POI embeddings for reference
    poi_output_path = output_folder / "poi_embeddings.parquet"
    poi_emb_np = poi_emb.numpy()
    poi_df = pd.DataFrame(poi_emb_np, columns=[f'{i}' for i in range(poi_emb_np.shape[1])])

    # Get placeid mapping
    placeid_to_idx = city_dict['placeid_to_idx']
    idx_to_placeid = {v: k for k, v in placeid_to_idx.items()}
    poi_df.insert(0, 'placeid', [idx_to_placeid.get(i, i) for i in range(len(poi_df))])
    poi_df.to_parquet(poi_output_path, index=False)
    print(f"POI embeddings: {poi_output_path} {poi_emb_np.shape}")

    # Save region embeddings
    region_output_path = output_folder / "region_embeddings.parquet"
    region_emb_np = region_emb.numpy()
    region_df = pd.DataFrame(region_emb_np, columns=[f'reg_{i}' for i in range(region_emb_np.shape[1])])
    region_df.insert(0, 'region_id', range(num_regions))
    region_df.to_parquet(region_output_path, index=False)
    print(f"Region embeddings: {region_output_path} {region_emb_np.shape}")


def create_embedding(state: str, args):
    """Run full Check2HGI pipeline: Preprocess -> Train."""
    city = state
    shapefile_path = args.shapefile
    graph_data_file = IoPaths.CHECK2HGI.get_graph_data_file(city)

    # T5.2a / T5.2b / T5.3 — cache-miss diagnostics for the auxiliary
    # artefacts. Any of:
    #   * T5.2a (Node2Vec) needs poi_delaunay_edge_index;
    #   * T5.2b (masked-POI decoder) needs poi_delaunay_edge_index AND
    #     poi_category_aggregate;
    #   * T5.3 (multi-view) needs a separate view2_graph.pt cache.
    # If the canonical graph exists but lacks the artefacts we need, force
    # a fresh preprocess (cheap one-time cost). The View-2 file is built
    # from the canonical cache after preprocess completes.
    _need_poi_delaunay_n2v = float(getattr(args, 'n2v_lambda', 0.0) or 0.0) > 0.0
    _need_poi_delaunay_mae = float(getattr(args, 'mae_poi_lambda', 0.0) or 0.0) > 0.0
    _need_poi_delaunay = _need_poi_delaunay_n2v or _need_poi_delaunay_mae
    _need_poi_aggregates = _need_poi_delaunay_mae
    _need_view2 = bool(getattr(args, 'use_multiview', False))
    # T6.1 — POI↔POI co-visit pairs cache. Built when p2p_lambda > 0.
    _need_covisit_pairs = float(getattr(args, 'p2p_lambda', 0.0) or 0.0) > 0.0
    _covisit_k = int(getattr(args, 'p2p_covisit_k', 3) or 3)
    # advisor 2026-05-19: dedup=True is the original T6.1 sweep behavior;
    # False is the implementation-robustness option (multiplicity-weighted).
    _covisit_dedup = not bool(getattr(args, 'p2p_no_dedup', False))
    # T6.2 — composite C3 edge weights (HGI-style Delaunay multiplier +
    # cross-region penalty). Defaults (1.0, 1.0) are no-ops; any ≠ 1.0
    # triggers force_preprocess so the new weights take effect.
    _c3_alpha_delaunay = float(getattr(args, 'c3_alpha_delaunay', 1.0) or 1.0)
    _c3_w_r = float(getattr(args, 'c3_w_r', 1.0) or 1.0)
    _c3_active = (_c3_alpha_delaunay != 1.0 or _c3_w_r != 1.0)

    _cache_missing_poi_artefacts = False
    if graph_data_file.exists() and (_need_poi_delaunay or _need_covisit_pairs or _c3_active) and not args.force_preprocess:
        try:
            with open(graph_data_file, 'rb') as _f:
                _peek = pkl.load(_f)
            _missing_delaunay = _need_poi_delaunay and 'poi_delaunay_edge_index' not in _peek
            _missing_aggregates = (
                _need_poi_aggregates and 'poi_category_aggregate' not in _peek
            )
            _missing_covisit = _need_covisit_pairs and 'covisit_pairs' not in _peek
            _cache_missing_poi_artefacts = _missing_delaunay or _missing_aggregates or _missing_covisit
            del _peek
        except Exception:
            _cache_missing_poi_artefacts = True

    if graph_data_file.exists() and not args.force_preprocess and not _cache_missing_poi_artefacts:
        print(f"Using existing graph data: {graph_data_file}")
        if _need_view2:
            view2_path = graph_data_file.parent / "view2_graph.pt"
            if not view2_path.exists():
                print(f"[T5.3] building view2 graph from canonical cache → {view2_path}")
                build_view2_graph_file(city)
    else:
        if _cache_missing_poi_artefacts:
            print("[T5.2a/T5.2b/T6.1] cached graph lacks required artefacts; "
                  "forcing fresh preprocess.")
        print("Preprocessing...")
        preprocess_check2hgi(
            city=city,
            city_shapefile=str(shapefile_path),
            edge_type=args.edge_type,
            temporal_decay=args.temporal_decay,
            build_poi_delaunay=_need_poi_delaunay,
            build_poi_aggregates=_need_poi_aggregates,
            build_covisit_pairs=_need_covisit_pairs,
            covisit_k=_covisit_k,
            covisit_dedup=_covisit_dedup,
            c3_alpha_delaunay=_c3_alpha_delaunay,
            c3_w_r=_c3_w_r,
            build_view2=_need_view2,
        )

    print("Training Check2HGI...")
    train_check2hgi(city, args)


run_pipeline = create_embedding  # Backwards compatibility


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Check2HGI Embedding Pipeline')

    # Data
    parser.add_argument('--city', type=str, default='Texas')
    parser.add_argument('--shapefile', type=str, default=str(Resources.TL_AL))

    # Pipeline
    parser.add_argument('--force_preprocess', action='store_true')
    parser.add_argument('--edge_type', type=str, default='user_sequence',
                        choices=['user_sequence', 'same_poi', 'both'])
    parser.add_argument('--temporal_decay', type=float, default=3600.0)

    # Model
    parser.add_argument('--dim', type=int, default=64)
    parser.add_argument('--num_layers', type=int, default=2)
    parser.add_argument('--attention_head', type=int, default=4)
    parser.add_argument('--alpha_c2p', type=float, default=0.4)
    parser.add_argument('--alpha_p2r', type=float, default=0.3)
    parser.add_argument('--alpha_r2c', type=float, default=0.3)
    parser.add_argument('--c2p_hard_neg_prob', type=float, default=0.0,
                        help='Phase-11 S1: hard-negative probability at the '
                             'check-in↔POI boundary (same-region different-POI). '
                             'Default 0.0 reproduces canonical c2hgi.')
    parser.add_argument('--c2p_corrupted_neg', action='store_true', default=False,
                        help='Phase-11 S4: use corrupted-feature same-identity '
                             'c2p negatives (DGI-style). Mutually exclusive with '
                             'c2p_hard_neg_prob > 0. Default False reproduces canonical c2hgi.')

    # v13 / v14 — reg-path POI augmentation (graduated from scripts/probe).
    parser.add_argument('--reg-poi-mode', dest='reg_poi_mode', type=str,
                        default='none',
                        choices=['none', 'poi2vec_residual', 'delaunay_gcn'],
                        help="Reg-path POI augmentation. 'none' (default) = "
                             "canonical bit-identical. 'poi2vec_residual' = v13 "
                             "Design B (detach+γ·Linear(POI2Vec)). 'delaunay_gcn' "
                             "= v14 Design K (PReLU(GCN(detach+γ·poi_table, "
                             "Delaunay))) + anchor regulariser.")
    parser.add_argument('--gamma-init', dest='gamma_init', type=float, default=1.0,
                        help='Initial γ (reg-path POI residual scale). v13/v14.')
    parser.add_argument('--anchor-lambda', dest='anchor_lambda', type=float,
                        default=0.0,
                        help='λ on ‖poi_table − POI2Vec‖² (delaunay_gcn/v14 only). '
                             'v14 default recipe uses 0.1.')
    # Training
    parser.add_argument('--lr', type=float, default=0.001)
    parser.add_argument('--gamma', type=float, default=1.0)
    parser.add_argument('--max_norm', type=float, default=0.9)
    parser.add_argument('--epoch', type=int, default=500)

    # Mini-batch settings
    parser.add_argument('--mini_batch_threshold', type=int, default=5_000_000,
                        help='Use mini-batch training if num_checkins > threshold')
    parser.add_argument('--batch_size', type=int, default=2**13)
    parser.add_argument('--num_neighbors', type=int, default=10)

    # Device
    parser.add_argument('--device', type=str, default='cpu',
                        help='Device: cpu, cuda, cuda:0, mps')

    # Performance optimizations
    parser.add_argument('--use_amp', action='store_true', default=True,
                        help='Use automatic mixed precision (AMP) for faster training on CUDA')
    parser.add_argument('--no_amp', action='store_false', dest='use_amp',
                        help='Disable automatic mixed precision')
    parser.add_argument('--use_compile', action='store_true', default=False,
                        help='(Not recommended) torch.compile is incompatible with PyG scatter ops')

    args = parser.parse_args()

    print(f"Check2HGI Pipeline | City: {args.city} | Device: {args.device}")
    print(f"Edge type: {args.edge_type} | Temporal decay: {args.temporal_decay}")
    print(f"AMP: {args.use_amp} | Compile: {args.use_compile}")
    create_embedding(state=args.city, args=args)
    print("Done!")
