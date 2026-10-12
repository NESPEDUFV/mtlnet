"""P1 - Region-head ablation: single-task next_region on Check2HGI.

Tests N head variants at configurable folds x epochs.
Reports Acc@{1,5,10}, MRR, macro-F1 per head.

This version respects each head's module-default hyperparameters; we
only pass `embed_dim`, `num_classes`, and `seq_length` (for the
transformer head). Everything else (hidden_dim, dropout, num_layers)
falls back to the head's __init__ defaults unless explicitly overridden
via --override-hparams. This fixes a sandbagging bug where the earlier
revision forced hidden_dim=emb_dim*2 and dropout=0.1 on every head,
catastrophically mis-tuning the transformer and halving GRU/LSTM capacity.

Usage:
    # E1 fair re-baseline (all 5 heads at per-head defaults)
    python scripts/p1_region_head_ablation.py --folds 1 --epochs 30

    # E2 winner scaling (example)
    python scripts/p1_region_head_ablation.py --folds 1 --epochs 30 \
        --heads next_gru --override-hparams hidden_dim=384 num_layers=3 \
        --label-smoothing 0.1 --input-layernorm

    # E3 transformer rescue (per-head LR via --max-lr-transformer)
    python scripts/p1_region_head_ablation.py --folds 1 --epochs 30 \
        --heads next_mtl --max-lr 5e-4

    # E-region: region-embedding input variant
    python scripts/p1_region_head_ablation.py --folds 1 --epochs 30 \
        --heads next_gru --input-type region

    # E-concat: check-in + region concat input
    python scripts/p1_region_head_ablation.py --folds 1 --epochs 30 \
        --heads next_gru --input-type concat
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import pickle as pkl
import sys
import time
from pathlib import Path

_root = Path(__file__).resolve().parent.parent
_src = str(_root / "src")
if _src not in sys.path:
    sys.path.insert(0, _src)

import numpy as np
import pandas as pd
import torch
from sklearn.model_selection import StratifiedGroupKFold
from torch.nn import CrossEntropyLoss
from torch.utils.data import DataLoader

from losses.calibrated import build_calibrated_loss
from configs.globals import DEVICE
from configs.model import InputsConfig
from configs.paths import EmbeddingEngine, IoPaths, OUTPUT_DIR
from data.aux_side_channel import AuxPublishingLoader
from data.log_t_freshness import assert_log_t_fresh
from data.folds import (
    POIDataset,
    POIDatasetWithAux,
    _batched_collate,
    _convert_to_tensors,
    TaskType,
    load_next_data,
)
from models.registry import create_model
from tracking.metrics import (
    compute_classification_metrics,
    StreamingClsMetrics,
    ambiguity_strict,
)
from utils.seed import seed_everything

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Speed levers (opt-in, CUDA-only, numerically NON-identical — see SPEED_LEVERS.md).
# Set in main() from --compile/--tf32. Exposed so the STL reg ceiling can be run with
# the SAME execution recipe as the MTL champion cell (the board's "never mix
# compiled/non-compiled cells" rule — otherwise the reg MTL-vs-ceiling delta is
# confounded by the compile fp-ordering shift). NB: p1 trains fp32 (no autocast), so
# --tf32 has a LARGER matmul effect here than in the fp16-autocast MTL trainer — which
# is exactly why uniform application must be validated, not assumed.
_P1_USE_COMPILE = False


def _should_chunk_val_metric(n_val: int, n_classes: int) -> tuple[bool, float]:
    """[S2-analog OOM guard] Decide whether to score the val metric on CPU.

    The STL eval would otherwise ``torch.cat`` the FULL val logit ``[n_val, n_classes]``
    on the GPU and OOM at large-C overlap scale (TX overlap: 766083×6553×4B ≈ 20 GB; CA
    worse). Returns ``(chunk_on_cpu, full_val_logit_gb)``.

    Default-ON guard: chunking auto-enables when the full val logit would exceed
    ``P1_S2_AUTO_BUDGET_GB`` (default 4 GB, matching MTL's ``MTL_S2_AUTO_BUDGET_GB``),
    so a future agent/dev running p1 on a large-C overlap state NEVER hits the OOM even
    without setting any env. ``MTL_CHUNK_VAL_METRIC=1`` / ``P1_CHUNK_VAL_METRIC=1`` force
    it on. Scoring on CPU is identical-at-reporting-precision to the GPU path for the
    rank-based metrics (``compute_classification_metrics`` is device-agnostic + already
    chunked; rank uses strict ``>``). See ``OOM_MEMORY_FIX.md``; the streaming path that
    supersedes this offload is pinned by ``tests/test_tracking/test_streaming_cls_metrics.py``.
    (This docstring used to cite ``tests/test_training/test_p1_val_chunk_guard.py``, which has
    never existed in this repository's history.)
    """
    val_logit_gb = (n_val * n_classes * 4) / 1e9
    forced = (
        os.environ.get("MTL_CHUNK_VAL_METRIC", "").strip() in ("1", "true", "True")
        or os.environ.get("P1_CHUNK_VAL_METRIC", "").strip() in ("1", "true", "True")
    )
    budget_gb = float(os.environ.get("P1_S2_AUTO_BUDGET_GB", "4"))
    return (forced or val_logit_gb > budget_gb), val_logit_gb


ALL_HEADS = [
    "next_mtl", "next_gru", "next_lstm", "next_tcn_residual", "next_temporal_cnn",
    "next_stan", "next_getnext", "next_getnext_hard", "next_getnext_hard_hsm",
    # Paper-facing alias for next_getnext_hard (STAN backbone + α·log_T flow prior).
    "next_stan_flow",
]
# Per-head default max_lr for OneCycleLR. Transformer converges at much
# lower LRs; RNN/CNN heads tolerate 3e-3. Override via --max-lr.
_HEAD_MAX_LR = {
    "next_mtl": 5e-4,
    "next_gru": 3e-3,
    "next_lstm": 3e-3,
    "next_tcn_residual": 3e-3,
    "next_temporal_cnn": 3e-3,
    "next_stan": 3e-3,
    "next_getnext": 3e-3,
    "next_getnext_hard": 3e-3,
    "next_getnext_hard_hsm": 3e-3,
    "next_stan_flow": 3e-3,  # alias of next_getnext_hard
}

# Heads that require ``last_region_idx`` delivered via aux_side_channel.
# For single-task ablation we wire POIDatasetWithAux + AuxPublishingLoader
# around train/val DataLoaders when the head is in this set.
# Note: next_getnext/next_tgstan/next_stahyper also consume log_T but
# read last-step embedding from x[..., last_idx] internally — they
# don't need the aux side channel.
# 2026-06-12 (HANDOFF_AUDIT X2 / CODE_AUDIT P0-B): added next_stan_flow_dualtower —
# keep in sync with _HEADS_REQUIRING_AUX_MTL in src/data/folds.py.
_HEADS_REQUIRING_AUX = {
    "next_getnext_hard", "next_getnext_hard_hsm", "next_stan_flow",
    "next_stan_flow_dualtower",
}


def _load_region_embeddings(state: str, source: str = "check2hgi") -> tuple[np.ndarray, int]:
    """Load region_embeddings.parquet as [n_regions, D] array.

    ``source`` switches which engine's region embeddings are consulted.
    Only the region-embedding *lookup* changes; region labels, placeid→
    region map, and sequences are always taken from check2hgi for a
    like-for-like task definition (CH15 / P1.5).
    """
    if source == "check2hgi":
        path = IoPaths.CHECK2HGI.get_state_dir(state) / "region_embeddings.parquet"
    elif source == "hgi":
        path = IoPaths.HGI.get_state_dir(state) / "region_embeddings.parquet"
    elif source == "check2hgi_postpool":
        # Diagnostic substrate: POI-mean → region-mean of canonical C2HGI
        # check-in embeddings, built post-hoc by
        # ``scripts/probe/build_check2hgi_postpool_region.py``.
        path = IoPaths.CHECK2HGI.get_state_dir(state) / "region_embeddings_postpool.parquet"
    elif source == "check2hgi_poi2vec":
        # C2HGI variant trained with POI2Vec features appended to per-check-in
        # input (canonical 11-dim cat+temporal + 64-dim POI2Vec = 75-dim).
        # Built by ``scripts/probe/build_check2hgi_poi2vec.py``.
        path = Path("output/check2hgi_poi2vec") / state.lower() / "region_embeddings.parquet"
    elif source == "check2hgi_design_e":
        path = Path("output/check2hgi_design_e") / state.lower() / "region_embeddings.parquet"
    elif source == "check2hgi_design_b":
        path = Path("output/check2hgi_design_b") / state.lower() / "region_embeddings.parquet"
    elif source == "check2hgi_design_h":
        path = Path("output/check2hgi_design_h") / state.lower() / "region_embeddings.parquet"
    elif source == "check2hgi_design_d":
        path = Path("output/check2hgi_design_d") / state.lower() / "region_embeddings.parquet"
    elif source == "check2hgi_design_i":
        path = Path("output/check2hgi_design_i") / state.lower() / "region_embeddings.parquet"
    elif source == "check2hgi_design_j":
        path = Path("output/check2hgi_design_j") / state.lower() / "region_embeddings.parquet"
    elif source == "check2hgi_design_m":
        path = Path("output/check2hgi_design_m") / state.lower() / "region_embeddings.parquet"
    elif source == "check2hgi_resln":
        path = Path("output/check2hgi_resln") / state.lower() / "region_embeddings.parquet"
    elif source == "check2hgi_resln_design_b":
        path = Path("output/check2hgi_resln_design_b") / state.lower() / "region_embeddings.parquet"
    elif source == "check2hgi_resln_design_b_sidefeat":
        # v13+sidefeat — resln encoder + design_b POI2Vec residual + T4.3 side-features
        # stacked at the POI-pool boundary (reg path). Two distinct geometric axes.
        path = Path("output/check2hgi_resln_design_b_sidefeat") / state.lower() / "region_embeddings.parquet"
    elif source == "check2hgi_resln_design_j":
        path = Path("output/check2hgi_resln_design_j") / state.lower() / "region_embeddings.parquet"
    elif source.startswith("check2hgi_design_j_"):
        # J λ-sweep variants (e.g. check2hgi_design_j_l0_5 → λ=0.5)
        path = Path("output") / source / state.lower() / "region_embeddings.parquet"
    elif source.startswith("check2hgi_design_k"):
        # K = J + Delaunay POI-POI edges (HGI's spatial sauce on c2hgi POI level)
        path = Path("output") / source / state.lower() / "region_embeddings.parquet"
    elif source.startswith("check2hgi_substrate_s1"):
        # Phase 11 S1 — c2p hard-negative sampling on canonical c2hgi.
        # Variants suffixed with hardneg prob, e.g. check2hgi_substrate_s1_p0_25
        # Convention: ``check2hgi_substrate_s1`` (default 0.25) maps to the
        # canonical substrate-s1 dir; suffixed variants point at sweep arms.
        path = Path("output") / source / state.lower() / "region_embeddings.parquet"
    elif source.startswith("check2hgi_substrate_s4"):
        # Phase 11 S4 — DGI-style same-identity corrupted-feature c2p
        # negatives on canonical c2hgi.
        path = Path("output") / source / state.lower() / "region_embeddings.parquet"
    elif source.startswith("check2hgi_substrate_s3b_v2c"):
        # Phase 11 S3-b V2-c — S3-b + per-check-in POI2Vec anchor.
        path = Path("output") / source / state.lower() / "region_embeddings.parquet"
    elif source.startswith("check2hgi_substrate_s3b"):
        # Phase 11 S3-b — Replace POI2Region with Checkin2Region as the
        # primary region pathway. L_p2r → L_c2r (HGI-style foreign-region negs).
        path = Path("output") / source / state.lower() / "region_embeddings.parquet"
    elif source == "c2hgi_hgi_concat":
        # Design A — late-fusion concat. The reg input is per-step concat,
        # but per_step is consumed via input/next_region.parquet directly,
        # not by region-emb lookup. We never read this branch from the
        # region-emb-source code path; included for API consistency.
        # Use canonical c2hgi region embeddings as fallback.
        path = IoPaths.CHECK2HGI.get_state_dir(state) / "region_embeddings.parquet"
    elif source.startswith("check2hgi"):
        # generic fallback for any check2hgi_* variant dir (embedding_eval re-screen
        # builds: gcn_ctrl, v3c_wd05, t43_sidefeat, rgcn, ...). Region labels still
        # come from the canonical check2hgi partition (like-for-like task).
        path = Path("output") / source / state.lower() / "region_embeddings.parquet"
    else:
        raise ValueError(
            f"Unknown region-emb source: {source} "
            f"(expected 'check2hgi', 'hgi', 'check2hgi_postpool', 'check2hgi_poi2vec')."
        )
    df = pd.read_parquet(path)
    emb_cols = [c for c in df.columns if c.startswith("reg_")]
    df = df.sort_values("region_id").reset_index(drop=True)
    emb = df[emb_cols].to_numpy(dtype=np.float32)
    return emb, emb.shape[1]


def _load_graph_maps(state: str) -> tuple[dict, np.ndarray]:
    graph_path = IoPaths.CHECK2HGI.get_graph_data_file(state)
    with open(graph_path, "rb") as f:
        graph = pkl.load(f)
    placeid_to_idx = graph["placeid_to_idx"]
    poi_to_region = graph["poi_to_region"]
    if hasattr(poi_to_region, "cpu"):
        poi_to_region = poi_to_region.cpu().numpy()
    return placeid_to_idx, np.asarray(poi_to_region, dtype=np.int64)


def _build_region_sequence_tensor(
    state: str,
    region_emb_dim: int,
    region_emb_source: str = "check2hgi",
    seq_engine: EmbeddingEngine = EmbeddingEngine.CHECK2HGI,
) -> torch.Tensor:
    """Build [N, 9, D] tensor where each step is the region embedding of
    the region the user was in at that check-in.

    Padded positions (poi_k == -1) map to the zero vector so the heads'
    `x.abs().sum(dim=-1) == 0` padding mask logic works identically to
    the check-in path.

    ``region_emb_source`` selects which engine's region embeddings are
    used for the lookup (see ``_load_region_embeddings``). Default
    ``check2hgi`` preserves prior behaviour; ``hgi`` is used for the
    P1.5 substrate comparison (CH15).
    """
    # seq_engine selects the windowing the region sequence follows (default
    # CHECK2HGI non-overlapping). The overlap probe passes its own engine so the
    # region-emb sequence row-aligns with the overlapping next_region labels.
    seq_path = IoPaths.get_seq_next(state, seq_engine)
    seq_df = pd.read_parquet(seq_path)
    placeid_to_idx, poi_to_region = _load_graph_maps(state)
    region_emb, _ = _load_region_embeddings(state, source=region_emb_source)

    n = len(seq_df)
    seq_len = 9
    out = np.zeros((n, seq_len, region_emb_dim), dtype=np.float32)

    for i in range(seq_len):
        col = f"poi_{i}"
        placeids = seq_df[col].astype(np.int64).to_numpy()
        mask = placeids != -1
        valid = placeids[mask]
        # Vectorised placeid -> poi_idx lookup
        poi_idx = pd.Series(valid).map(placeid_to_idx).to_numpy(dtype=np.int64)
        region_idx = poi_to_region[poi_idx]
        out[np.where(mask)[0], i, :] = region_emb[region_idx]

    return torch.from_numpy(out)


def _load_checkin_region_data(state: str, engine_override: EmbeddingEngine | None = None):
    """Load check-in embedding tensor + region labels + stratification info.

    Returns a 7-tuple adding ``last_region_tensor`` to the historical
    6-tuple. ``last_region_tensor`` is None when the parquet lacks the
    ``last_region_idx`` column (older schema, pre-commit ``6a2f808``).

    ``engine_override`` lets probes (Design A concat fusion) point at a
    non-canonical input directory while still using check2hgi-derived
    region labels and graph maps.
    """
    engine = engine_override or EmbeddingEngine.CHECK2HGI
    X, y_cat, userids, emb_dim = load_next_data(state, engine)

    region_df = IoPaths.load_next_region(state, engine)
    y_region = region_df["region_idx"].to_numpy(dtype=np.int64)
    n_regions = int(y_region.max()) + 1

    # ``last_region_idx`` is only present in the post-6a2f808 schema. Older
    # parquets built before the B5 feature landed won't have it, so we
    # return None and let the caller decide how to handle that.
    last_region_tensor = None
    if "last_region_idx" in region_df.columns:
        last_region_np = region_df["last_region_idx"].to_numpy(dtype=np.int64)
        last_region_tensor = torch.from_numpy(np.ascontiguousarray(last_region_np))

    slide_window = InputsConfig.SLIDE_WINDOW
    x_tensor, _ = _convert_to_tensors(X, y_cat, TaskType.NEXT, embedding_dim=emb_dim, slide_window=slide_window)
    y_region_tensor = torch.from_numpy(np.ascontiguousarray(y_region, dtype=np.int64))

    return x_tensor, y_region_tensor, y_cat, userids, emb_dim, n_regions, last_region_tensor


def _load_data(state: str, input_type: str, region_emb_source: str = "check2hgi",
               engine_override: EmbeddingEngine | None = None):
    """Route to the correct input loader. Returns a 7-tuple:
    ``(x_tensor, y_region_tensor, y_cat, userids, emb_dim, n_regions, last_region_tensor)``.

    ``last_region_tensor`` is None when the underlying parquet lacks the
    ``last_region_idx`` column (pre-``6a2f808`` schema). Heads in
    ``_HEADS_REQUIRING_AUX`` refuse to run when it is None — that's a
    data-prep gap the user must resolve via ``scripts/regenerate_next_region.py``.
    """
    x_checkin, y_region_tensor, y_cat, userids, checkin_dim, n_regions, last_region_tensor = (
        _load_checkin_region_data(state, engine_override=engine_override)
    )

    if input_type == "checkin":
        return x_checkin, y_region_tensor, y_cat, userids, checkin_dim, n_regions, last_region_tensor

    # Build region-emb sequence and align row-for-row with the check-in tensor.
    # When an engine_override is set (e.g. the overlap probe), follow ITS windowing
    # so the region sequence row-aligns with the overridden next_region labels.
    _seq_eng = engine_override or EmbeddingEngine.CHECK2HGI
    x_region = _build_region_sequence_tensor(state, region_emb_dim=checkin_dim,
                                             region_emb_source=region_emb_source, seq_engine=_seq_eng)
    # Row counts must match (sequences_next.parquet is authoritative upstream).
    if x_region.shape[0] != x_checkin.shape[0]:
        raise RuntimeError(
            f"Row mismatch: region tensor has {x_region.shape[0]} rows, "
            f"checkin tensor has {x_checkin.shape[0]}. Regenerate inputs."
        )

    if input_type == "region":
        return x_region, y_region_tensor, y_cat, userids, checkin_dim, n_regions, last_region_tensor
    if input_type == "concat":
        x_concat = torch.cat([x_checkin, x_region], dim=-1)  # [N, 9, 128]
        return x_concat, y_region_tensor, y_cat, userids, checkin_dim * 2, n_regions, last_region_tensor
    raise ValueError(f"Unknown input_type: {input_type}")


def _append_visit_features(x_tensor, state: str, seq_engine: EmbeddingEngine | None):
    """A2: concat the canonical per-visit raw features onto each window position.

    Features align to the sequences the input was built from: ``seq_engine`` for the
    checkin path (engine_override), check2hgi otherwise. Raw load_city is the feature
    source; falls back to check2hgi metadata if the placeid-alignment assert trips
    (e.g. a state where check2hgi filtered the check-in set).
    """
    sys.path.insert(0, str(_root / "scripts"))
    from pre_freeze_gates.a2_features import build_per_visit_features

    seq_eng = seq_engine or EmbeddingEngine.CHECK2HGI
    seq_df = pd.read_parquet(IoPaths.get_seq_next(state, seq_eng))
    try:
        feat = build_per_visit_features(seq_df, IoPaths.load_city(state), validate=True)
    except AssertionError as e:
        logger.warning("visit-feat align vs raw checkins failed (%s); retrying with check2hgi metadata", e)
        meta = pd.read_parquet(
            IoPaths.CHECK2HGI.get_state_dir(state) / "embeddings.parquet",
            columns=["userid", "placeid", "datetime", "category"],
        )
        feat = build_per_visit_features(seq_df, meta, validate=True)
    ft = torch.from_numpy(feat)  # [N, 9, F]
    if ft.shape[:2] != x_tensor.shape[:2]:
        raise RuntimeError(f"visit-feat shape {tuple(ft.shape)} misaligned with x {tuple(x_tensor.shape)}")
    return torch.cat([x_tensor, ft], dim=-1), x_tensor.shape[-1] + ft.shape[-1]


def _dataloader(x, y, batch_size, shuffle, aux=None):
    """Build a DataLoader; if ``aux`` is provided, wrap with
    ``POIDatasetWithAux`` + ``AuxPublishingLoader`` so the head can read
    the auxiliary tensor via the thread-local side-channel. The training
    loop still sees ``(x, y)`` 2-tuples — the wrapper publishes + strips
    ``aux`` transparently.
    """
    if aux is None:
        ds = POIDataset(x, y, device=DEVICE)
        # POIDataset defines __getitems__ (batched index_select fetch, perf fix
        # 2026-06-24); it MUST be paired with the _batched_collate passthrough, else
        # default_collate re-stacks the already-batched tensors and raises a shape
        # mismatch (matches src/data/folds.py:454,498). Without this the checkin-modality
        # reg head crashed at collate ([B,9,64] vs [B]).
        return DataLoader(ds, batch_size=batch_size, shuffle=shuffle, num_workers=0,
                          collate_fn=_batched_collate)
    ds = POIDatasetWithAux(x, y, aux, device=DEVICE)
    base = DataLoader(ds, batch_size=batch_size, shuffle=shuffle, num_workers=0,
                      collate_fn=_batched_collate)
    return AuxPublishingLoader(base)


def _parse_overrides(raw: list[str] | None) -> dict:
    """Parse --override-hparams name=value pairs into a dict with type coercion."""
    if not raw:
        return {}
    out = {}
    for kv in raw:
        if "=" not in kv:
            raise ValueError(f"Override must be key=value, got: {kv}")
        k, v = kv.split("=", 1)
        # Coerce: int > float > str
        try:
            out[k] = int(v)
            continue
        except ValueError:
            pass
        try:
            out[k] = float(v)
            continue
        except ValueError:
            pass
        out[k] = v
    return out


def _build_head(head_name, emb_dim, n_classes, seq_length, overrides):
    """Instantiate a head passing only embed_dim + num_classes (+ seq_length
    for heads that require it), plus any explicit overrides the user passed.
    Everything else falls back to the head's __init__ defaults.
    """
    import inspect
    from models.registry import _MODEL_REGISTRY, _ensure_registered
    _ensure_registered()
    target_cls = _MODEL_REGISTRY[head_name]
    sig = inspect.signature(target_cls.__init__)
    accepted = {p.name for p in sig.parameters.values()
                if p.kind in (p.POSITIONAL_OR_KEYWORD, p.KEYWORD_ONLY)}

    kwargs = {"embed_dim": emb_dim, "num_classes": n_classes}
    # next_mtl is the only head that needs seq_length / num_heads to be
    # set; its defaults are reasonable except num_heads has no default.
    if head_name == "next_mtl":
        kwargs["seq_length"] = seq_length
        kwargs.setdefault("num_heads", 4)
        kwargs.setdefault("num_layers", 4)

    # Apply user overrides (only keys the target accepts)
    for k, v in overrides.items():
        if k in accepted:
            kwargs[k] = v
    return target_cls(**kwargs)


class _InputLN(torch.nn.Module):
    """Wraps a head with input LayerNorm over the embedding dimension."""
    def __init__(self, head, emb_dim):
        super().__init__()
        self.ln = torch.nn.LayerNorm(emb_dim)
        self.head = head

    def forward(self, x):
        # Preserve zero-padding: don't LayerNorm positions that are all-zero
        # (they would become non-zero after LN, breaking downstream padding
        # masks that use x.abs().sum(dim=-1) == 0).
        pad = (x.abs().sum(dim=-1, keepdim=True) == 0).float()
        x_ln = self.ln(x)
        x_out = x_ln * (1.0 - pad) + x * pad
        return self.head(x_out)


class _MTLPreencoder(torch.nn.Module):
    """Wrap a head with MTLnet's next_encoder stack as pre-processor.

    Mirrors ``MTLnet._build_encoder`` (Linear+ReLU+LayerNorm+Dropout stack)
    so single-task evaluation sees the same input distribution the MTL
    head would see — minus the cross-attn / shared-backbone blocks.
    Used by F41 (Exp D) to isolate the *upstream encoder* contribution of
    the CH18 STL-vs-MTL gap.

    Padding semantics are preserved: positions that were zero in the
    input are re-zeroed after the encoder so the head's padding mask
    (``x.abs().sum(-1) == 0``) still fires. In MTL this is enforced by
    the downstream cross-attn `mask.unsqueeze(-1)` step; we replicate it
    directly here.
    """

    def __init__(self, in_size, hidden_size, out_size, num_layers=2,
                 dropout=0.1, head=None):
        super().__init__()
        layers = [
            torch.nn.Linear(in_size, hidden_size),
            torch.nn.ReLU(),
            torch.nn.LayerNorm(hidden_size),
            torch.nn.Dropout(dropout),
        ]
        for _ in range(num_layers - 1):
            layers += [
                torch.nn.Linear(hidden_size, hidden_size),
                torch.nn.ReLU(),
                torch.nn.LayerNorm(hidden_size),
                torch.nn.Dropout(dropout),
            ]
        layers += [
            torch.nn.Linear(hidden_size, out_size),
            torch.nn.ReLU(),
            torch.nn.LayerNorm(out_size),
        ]
        self.encoder = torch.nn.Sequential(*layers)
        self.head = head

    def forward(self, x):
        pad_mask = (x.abs().sum(dim=-1, keepdim=True) == 0)  # [B, T, 1] bool
        x_enc = self.encoder(x)
        x_enc = x_enc.masked_fill(pad_mask, 0.0)
        return self.head(x_enc)


CANONICAL_METRICS: tuple[str, ...] = (
    "accuracy", "top5_acc", "top10_acc", "mrr", "f1",
)
"""Metrics tracked by ``_new_per_metric_tracker``. Same set used in MTL
``storage.py`` ``CANONICAL_BEST_METRICS`` for parity."""


def _new_per_metric_tracker() -> dict:
    """Empty per-metric best tracker for ``_update_per_metric_best``."""
    return {m: {"value": -1.0, "snapshot": {}} for m in CANONICAL_METRICS}


def _update_per_metric_best(tracker: dict, metrics: dict, epoch: int) -> None:
    """Update each metric's best snapshot if this epoch's value is higher.

    AUDIT-C1: emits a per-metric snapshot so the STL output JSON has
    ``per_metric_best.f1.f1`` (the metric *at its own best epoch*) instead
    of the legacy single-snapshot scheme that reported every metric at
    top10's best epoch.
    """
    for m in CANONICAL_METRICS:
        v = float(metrics.get(m, 0.0))
        if v > tracker[m]["value"]:
            tracker[m]["value"] = v
            tracker[m]["snapshot"] = dict(metrics)
            tracker[m]["snapshot"]["best_epoch"] = int(epoch)


def _train_single_task(head_name, x_tensor, y_tensor, train_idx, val_idx,
                       emb_dim, n_classes, epochs, batch_size, seed,
                       overrides, max_lr, label_smoothing, input_ln,
                       aux_tensor=None, mtl_preencoder=False,
                       preenc_hidden=256, preenc_layers=2,
                       preenc_dropout=0.1, loss_cfg=None):
    """Train a single-task model and return val metrics.

    ``aux_tensor`` — optional per-sample auxiliary int64 tensor (e.g.
    ``last_region_idx``). When the head is in ``_HEADS_REQUIRING_AUX``
    and ``aux_tensor`` is None, we raise because the head's forward pass
    would silently fall back to pure STAN and the comparison would be
    meaningless.
    """
    seed_everything(seed)

    if head_name in _HEADS_REQUIRING_AUX:
        if aux_tensor is None:
            raise RuntimeError(
                f"Head '{head_name}' requires 'last_region_idx' aux but the "
                f"parquet didn't contain it. Regenerate via "
                f"`scripts/regenerate_next_region.py --state <state>`."
            )

    x_train, y_train = x_tensor[train_idx], y_tensor[train_idx]
    x_val, y_val = x_tensor[val_idx], y_tensor[val_idx]

    if head_name in _HEADS_REQUIRING_AUX and aux_tensor is not None:
        aux_train = aux_tensor[train_idx]
        aux_val = aux_tensor[val_idx]
        train_dl = _dataloader(x_train, y_train, batch_size, True, aux=aux_train)
        val_dl = _dataloader(x_val, y_val, batch_size, False, aux=aux_val)
    else:
        train_dl = _dataloader(x_train, y_train, batch_size, True)
        val_dl = _dataloader(x_val, y_val, batch_size, False)

    seq_length = InputsConfig.SLIDE_WINDOW
    # Under --mtl-preencoder, the head's `embed_dim` must match the
    # preencoder's output dim (e.g. 256), not the raw input dim (64).
    # This mirrors MTL where the head receives the next_encoder output.
    head_embed_dim = preenc_hidden if mtl_preencoder else emb_dim
    head = _build_head(head_name, head_embed_dim, n_classes, seq_length, overrides)
    model = head
    if input_ln:
        model = _InputLN(head, head_embed_dim)
    if mtl_preencoder:
        model = _MTLPreencoder(
            in_size=emb_dim,
            hidden_size=preenc_hidden,
            out_size=preenc_hidden,
            num_layers=preenc_layers,
            dropout=preenc_dropout,
            head=model,
        )
    model = model.to(DEVICE)
    if _P1_USE_COMPILE and DEVICE.type == "cuda":
        # Match the MTL champion's --compile (kernel fusion); CUDA-only, fp-non-identical.
        # Mirror mtl_cv.py: the head is compiled in a TRAIN (grad) and an EVAL (no-grad)
        # variant + several batch-shape variants (overlap folds differ in size + the
        # partial last batch). The default dynamo cache_size_limit=8 is easily exceeded
        # → SILENT EAGER FALLBACK (the uniform ~770s/fold seen on the H100 board run,
        # ~2x the A40). Raise the limit and (MTL_COMPILE_DYNAMIC=1) use one symbolic-shape
        # graph so every variant stays compiled. Pure speed; no numeric change beyond the
        # compiled-vs-eager fp-ordering noise the --compile rule already accepts.
        import os as _os
        try:
            import torch._dynamo as _dyn
            _lim = int(_os.environ.get("MTL_COMPILE_CACHE_LIMIT", "64"))
            _dyn.config.cache_size_limit = max(_dyn.config.cache_size_limit, _lim)
            if hasattr(_dyn.config, "recompile_limit"):
                _dyn.config.recompile_limit = max(_dyn.config.recompile_limit, _lim)
        except Exception:
            pass
        _ckw = {}
        if _os.environ.get("MTL_COMPILE_DYNAMIC") == "1":
            _ckw["dynamic"] = True
        _cmode = _os.environ.get("MTL_COMPILE_MODE")
        if _cmode:
            _ckw["mode"] = _cmode
        model = torch.compile(model, **_ckw)

    optimizer = torch.optim.AdamW(model.parameters(), lr=1e-4, weight_decay=0.01)
    steps_per_epoch = len(train_dl)
    scheduler = torch.optim.lr_scheduler.OneCycleLR(
        optimizer, max_lr=max_lr, epochs=epochs, steps_per_epoch=steps_per_epoch,
    )
    # T1.4 loss calibration (leak-free): all class statistics come from the
    # TRAIN split only (``y_train`` here), never val. At all-default knobs the
    # criterion is bit-identical to CrossEntropyLoss(label_smoothing=...).
    lc = dict(loss_cfg or {})
    criterion = build_calibrated_loss(
        n_classes, y_train,
        label_smoothing=label_smoothing,
        focal_gamma=lc.get("focal_gamma", 0.0),
        logit_adjust_tau=lc.get("logit_adjust_tau", 0.0),
        tail_mode=lc.get("tail_mode", None),
        cb_beta=lc.get("cb_beta", 0.999),
        ldam_max_m=lc.get("ldam_max_m", 0.5),
        ldam_scale=lc.get("ldam_scale", 30.0),
        device=DEVICE,
    )

    # AUDIT-C1 fix: track per-metric best across all epochs, not just
    # top10. The legacy code picked top10-best then reported F1/MRR/Acc@1
    # at THAT epoch — mirroring (in opposite direction) the MTL F1-vs-
    # top10 mismatch. With per_metric_best we emit a separate
    # snapshot at each canonical metric's best epoch so downstream
    # comparisons can be apples-to-apples.
    per_metric_best: dict = _new_per_metric_tracker()

    _amb_worst, _to_cpu_last = {}, None
    for epoch in range(epochs):
        model.train()
        for x_batch, y_batch in train_dl:
            optimizer.zero_grad(set_to_none=True)
            out = model(x_batch)
            loss = criterion(out, y_batch)
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            optimizer.step()
            scheduler.step()

        # Val
        model.eval()
        # S2-analog for the STL ceiling (OOM_MEMORY_FIX.md): at large-C overlap scale the
        # full val logit [N_val, C] OOMs the GPU on torch.cat (TX overlap: ~18.7GB at 6553
        # regions; CA worse). compute_classification_metrics already chunks internally and is
        # device-agnostic (operates on the input's device; rank-of-target uses strict `>`), so
        # accumulating the val logits on CPU and scoring there is BYTE-IDENTICAL to the GPU path
        # for the rank-based metrics (top-k/MRR/NDCG) — validated on AL. The dataset stays on
        # GPU; only the val logits move, so the 18.7GB GPU cat is removed entirely. Auto-enable
        # when the full val logit would exceed a GPU budget, or via MTL_CHUNK_VAL_METRIC /
        # P1_CHUNK_VAL_METRIC; else keep the GPU path so small-state / frozen p1 numbers are untouched.
        _chunk_val, _val_logit_gb = _should_chunk_val_metric(len(x_val), n_classes)
        _stream = (os.environ.get("P1_STREAM_VAL", "1").strip() not in ("0", "false", "False")
                   and StreamingClsMetrics.should_stream(n_classes))
        # Suppressed when streaming: this message describes a full-logit CPU cat that no longer
        # happens, and under P1_STREAM_GPU=1 it would claim "on CPU" while scoring on the GPU,
        # contradicting the streamed log two lines below.
        # Keyed on the DECISION, not on the env var: with C <= 256 streaming is off regardless of
        # P1_STREAM_VAL, the full-logit CPU cat below really does happen, and reading the env var
        # here silently suppressed the one line that says so.
        if _chunk_val and epoch == 0 and not _stream:
            logger.info(
                "[p1 S2] scoring val metric on CPU (full val logit ~= %.1f GB, N_val=%d x C=%d) "
                "to avoid GPU OOM at overlap scale — byte-identical for rank-based metrics",
                _val_logit_gb, len(x_val), n_classes,
            )
        # ---- STREAMED val metric (P1_STREAM_VAL, default ON for C > 256) -------------------
        # The old path built the FULL [N_val, C] logit and scored it in one go. That tensor is
        # 20.1 GB at texas and 19.9 GB at california, which OOMs the GPU on the `torch.cat` — so
        # `_chunk_val` moved the whole thing to CPU instead. That works, and it is why the reg
        # cell is the one family that runs SLOWER on rented hardware: the scoring is CPU-bound
        # and a container has 8 cores against the A40 box's 32 (measured: arizona reg 343 s on an
        # H100 vs 185 s here; florida 455 s/fold vs 332 s/fold).
        #
        # Streaming removes the buffer instead of relocating it. Every metric this function
        # reports is a PER-ROW quantity: `argmax`, `topk(k, dim=-1)` and `_rank_of_target` all
        # depend on row i alone, so computing them per batch and concatenating the O(N) results
        # is the SAME arithmetic as computing them on the full [N, C] — not an approximation.
        # `StreamingClsMetrics` (tracking.metrics) owns those accumulators and reassembles the
        # identical dict. It is the SAME class `mtl_eval.py` uses for the joint's reg head (S2)
        # and `mtl_cv.py` for the S1 train metric — the pattern used to be copy-pasted into all
        # three, which is how the p1 copy shipped a read-before-assignment that killed every
        # streamed run. One implementation, one place to fix.
        #
        # Consequence: no O(N·C) buffer on any device, no CPU offload at any scale, and scoring
        # becomes homogeneous instead of switching behaviour at a 4 GB size threshold.
        #
        # Guard: `should_stream` gates on the cutoff above which `compute_classification_metrics`
        # leaves torchmetrics for the hand-rolled path — below it the two would not agree, so the
        # full path stays. Asking the class beats re-typing 256 in a fourth place. (Every state in
        # this study has C >= 520, so streaming is always on here.)
        if _stream:
            # DEVICE. Streaming removes the [N, C] buffer, so the OOM that `_chunk_val` exists to
            # prevent cannot happen any more and the CPU move is no longer NECESSARY. It is kept
            # by default anyway, because every reg cell banked in this study was CPU-scored and
            # switching device is the one thing that is NOT bit-identical: `topk`'s tie-break at
            # the k-boundary is a kernel detail (synthetic worst case on an H100: exact ties forced
            # at the boundary → CPU and GPU disagreed on 19950/20000 rows, top10_acc moved 3.0e-04).
            # On REAL arizona reg logits, measured: 0/100448 ties at BOTH boundaries and a worst
            # cross-device delta of 5.96e-08 with top10_acc bit-identical — so P1_STREAM_GPU=1 is
            # safe and 3.2x faster (57s→18s/fold). Default stays OFF only for homogeneity with the
            # banked CPU-scored cells; the diagnostic below re-checks the precondition every run.
            # DEFAULT FLIPPED 2026-08-10: scoring stays on the GPU. The reason it ever moved to
            # the host was the [N, C] buffer, and streaming removed that; what kept it there
            # afterwards was topk's kernel-dependent tie-break, and rank-derived hits removed that
            # too. What remains is pure cost: the per-batch `.to("cpu")` synchronised the host
            # every iteration and serialised the GPU — 6.4 s off an 17.9 s wall whose scoring was
            # only 2.87 s. Set P1_STREAM_GPU=0 to restore the CPU path.
            _to_cpu = _chunk_val and os.environ.get("P1_STREAM_GPU", "1").strip() not in ("1", "true", "True")
            if epoch == 0:
                logger.info(
                    "[p1 S2] STREAMED val metric on %s (per-row accumulators, no [N=%d x C=%d] "
                    "buffer; would have been %.1f GB) — same per-row ops as the full path",
                    "cpu" if _to_cpu else str(DEVICE), len(x_val), n_classes, _val_logit_gb,
                )
            # A/B EXPERIMENT (P1_SCORE_AB=1): score the SAME logits on BOTH devices in this one
            # run and report the per-metric delta. Comparing a fresh GPU-scored run against a
            # banked CPU-scored value would confound the scoring device with `--compile`
            # nondeterminism (CLAUDE.md: compiled numbers are within-fold-sigma, not
            # bit-reproducible), so the device question can only be answered inside a single run.
            _ab = os.environ.get("P1_SCORE_AB", "0").strip() in ("1", "true", "True")
            # Tie diagnostic. Costs one topk(max_k+1) per batch (2.9 ms at 2048x6553; a full
            # sort is 83.5 ms — an earlier version ran the sort EVERY epoch and logged only the
            # first, adding ~26 min/fold at texas). Cadence differs by role:
            #   CPU scoring  -> epoch 0 only. Informational; the device cannot affect the result.
            #   GPU scoring  -> EVERY epoch. Here it is a correctness GATE, and the banked number
            #     is `per_metric_best` over ALL epochs, not epoch 0's. Checking only the first
            #     epoch would let a tie at epoch 5 reach the board unseen — the metric that gets
            #     banked is chosen after every epoch, so the precondition has to hold at each one.
            _diag = (epoch == 0) or not _to_cpu
            # P1_HITS_FROM_RANK=0 restores the historical topk semantics. It exists because the
            # gate's own error message told operators to "re-run with hits_from_rank=False" while
            # no CLI flag or env var could actually do that -- advice you cannot follow is worse
            # than none, since it reads as a supported escape hatch. With streaming still on and
            # P1_STREAM_GPU=0, this reproduces the banked cells EXACTLY (CPU + topk) without the
            # [N, C] buffer, which is the configuration to use when a state trips the certificate.
            _hfr = os.environ.get("P1_HITS_FROM_RANK", "1").strip() not in ("0", "false", "False")
            acc = StreamingClsMetrics(n_classes, top_k=(5, 10),
                                      move_logits_to="cpu" if _to_cpu else None,
                                      diagnose_ties=_diag, hits_from_rank=_hfr)
            # No gate on the A/B arm: it scores the SAME logits, so `acc` above already
            # measures the ambiguity of these very rows. A second count would be the same
            # number at twice the price.
            acc_ab = (StreamingClsMetrics(n_classes, top_k=(5, 10),
                                          move_logits_to=str(DEVICE) if _to_cpu else "cpu",
                                          store_on="cpu", hits_from_rank=_hfr)
                      if (_ab and epoch == 0) else None)
            with torch.no_grad():
                for x_batch, y_batch in val_dl:
                    out = model(x_batch).detach()
                    acc.update(out, y_batch)
                    if acc_ab is not None:
                        acc_ab.update(out, y_batch)   # same logits, the OTHER device
                    del out
            metrics = acc.compute()
            _to_cpu_last = _to_cpu
            for _k, _v in acc.tie_counts.items():
                _amb_worst[f"top{_k}"] = max(_amb_worst.get(f"top{_k}", 0), int(_v))
            if _diag and acc.n_rows and (epoch == 0 or acc.has_ties):
                logger.info("[p1 S2] boundary ties on REAL val logits — %s. Both must read 0 "
                            "before P1_STREAM_GPU=1 is safe for a state with banked CPU cells.",
                            acc.tie_summary())
                # The precondition for GPU scoring is CHECKED per run, not extrapolated from the
                # state it was first measured on. A cell that ties while scoring on the GPU is not
                # homogeneous with its CPU-scored siblings, and the operator has to know before
                # the number is banked.
                if not _to_cpu and acc.has_ties:
                    # WHICH switch actually moves scoring to the CPU depends on why we are on the
                    # GPU. `_to_cpu = _chunk_val and not P1_STREAM_GPU`, so when `_chunk_val` is
                    # False (a state under the 4 GB budget, e.g. an ad-hoc small-state run) setting
                    # P1_STREAM_GPU=0 changes NOTHING — and under MTL_STRICT=1, which run_lane.sh
                    # sets for every cell, following that advice would just reproduce this error.
                    # P1_STREAM_GPU=0 only moves the DEVICE; hits stay rank-derived, so a tied
                    # cell still would not match a topk-scored sibling. The only switch that
                    # restores the banked semantics is the full legacy path.
                    _fix = ("P1_STREAM_VAL=0 (the legacy full-logit + topk path the banked cells "
                            "used; needs ~20 GB host RAM at TX/CA). P1_STREAM_GPU=0 is NOT the "
                            "fix — it changes the device, not the derivation")
                    _msg = (f"[p1 S2] epoch {epoch}: GPU scoring with boundary ties present "
                            f"({acc.tie_summary()}) — topk tie-break is kernel-dependent, so this "
                            f"cell may NOT match a CPU-scored sibling. Re-run with {_fix}.")
                    # Same decision as the accumulator's gate, read through the same function.
                    # These two used to read the environment independently and drifted apart.
                    if ambiguity_strict():
                        raise RuntimeError(_msg)
                    logger.warning(_msg)
            if acc_ab is not None:
                _m2 = acc_ab.compute()
                _worst = max((abs(float(metrics[k]) - float(_m2[k])), k) for k in metrics
                             if isinstance(metrics.get(k), float))
                logger.info("[p1 A/B] same logits, both devices — worst |delta| = %.3e on '%s' "
                            "(top10_acc: %.10f vs %.10f). Reporting quantum is 1e-6.",
                            _worst[0], _worst[1], metrics["top10_acc"], _m2["top10_acc"])
        else:
            all_logits, all_targets = [], []
            with torch.no_grad():
                for x_batch, y_batch in val_dl:
                    out = model(x_batch).detach()
                    if _chunk_val:
                        out = out.cpu()
                        y_batch = y_batch.cpu()
                    all_logits.append(out)
                    all_targets.append(y_batch)

            logits = torch.cat(all_logits)
            targets = torch.cat(all_targets)
            metrics = compute_classification_metrics(logits, targets, num_classes=n_classes, top_k=(5, 10))

        _update_per_metric_best(per_metric_best, metrics, epoch + 1)

    # Backward-compatible primary return: top10-best snapshot (same as
    # before). Downstream callers can read per_metric_best for clean
    # cross-metric reporting.
    best_metrics = dict(per_metric_best["top10_acc"]["snapshot"])
    # Durable trace of the certificate. Until now a tie-optimistic cell was recorded ONLY as a
    # line in the driver log, which is not what anyone reads when they later ask "is this number
    # comparable to its siblings?". Worst case over all epochs, so a clean cell reads 0 and a
    # dirty one cannot be mistaken for clean by looking at the JSON.
    best_metrics["ambiguous_rows"] = _amb_worst
    best_metrics["scored_on"] = "cpu" if _to_cpu_last else "gpu"
    best_metrics["per_metric_best"] = {
        m: per_metric_best[m]["snapshot"] for m in CANONICAL_METRICS
    }
    return best_metrics


def _checkpoint_path(out_dir: Path, state: str, input_type: str,
                     folds: int, epochs: int, tag: str | None) -> Path:
    """Checkpoint path keyed on the full run config.

    Uses the same filename discriminants as the final JSON output (state,
    input_type, folds, epochs, tag) so resume is automatic when the user
    re-invokes with identical CLI args.
    """
    tag_s = f"_{tag}" if tag else ""
    return out_dir / f"region_head_{state}_{input_type}_{folds}f_{epochs}ep{tag_s}.checkpoint.json"


def _load_checkpoint(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        with open(path) as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError) as e:
        logger.warning("Checkpoint at %s unreadable (%s) — starting fresh.", path, e)
        return {}


def _save_checkpoint(path: Path, payload: dict) -> None:
    """Atomic checkpoint write: serialise to a sibling temp file, then rename.

    Important for resume safety — if the process is killed mid-write, the
    old checkpoint is still valid rather than left half-written.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    with open(tmp, "w") as f:
        json.dump(payload, f, indent=2, default=str)
    tmp.replace(path)


def run_ablation(state: str, heads: list[str], folds: int, epochs: int,
                 batch_size: int, seed: int, input_type: str,
                 overrides: dict, max_lr: float | None,
                 label_smoothing: float, input_ln: bool,
                 tag: str | None, resume: bool = True,
                 region_emb_source: str = "check2hgi",
                 mtl_preencoder: bool = False,
                 preenc_hidden: int = 256,
                 preenc_layers: int = 2,
                 preenc_dropout: float = 0.1,
                 per_fold_transition_dir: str | None = None,
                 engine_override: EmbeddingEngine | None = None,
                 target: str = "region",
                 loss_cfg: dict | None = None,
                 add_visit_features: bool = False,
                 only_fold: int | None = None):
    logger.info("Loading data for %s (input_type=%s, region_emb=%s, target=%s, engine_override=%s, visit_feats=%s)...",
                state, input_type, region_emb_source, target, engine_override, add_visit_features)
    x_tensor, y_region, y_cat, userids, emb_dim, n_regions, last_region_tensor = _load_data(
        state, input_type, region_emb_source, engine_override=engine_override,
    )
    if add_visit_features:
        # A2 feature-concat control: append the per-visit raw features (= Check2HGI's
        # node features) to each window position. Aligned to the SAME sequences the
        # input tensor was built from (engine_override for checkin, check2hgi otherwise).
        x_tensor, emb_dim = _append_visit_features(x_tensor, state, engine_override)
        logger.info("  +visit-features: x=%s emb_dim=%d", tuple(x_tensor.shape), emb_dim)
    aux_hint = "present" if last_region_tensor is not None else "missing"
    if target == "category":
        y_tensor = torch.from_numpy(np.ascontiguousarray(y_cat, dtype=np.int64))
        n_classes = int(y_tensor.max().item()) + 1
        logger.info("x=%s, emb_dim=%d, target=category(%d classes), n_seqs=%d, last_region_idx=%s",
                    x_tensor.shape, emb_dim, n_classes, len(y_tensor), aux_hint)
    elif target == "region":
        y_tensor = y_region
        n_classes = n_regions
        logger.info("x=%s, emb_dim=%d, n_regions=%d, n_seqs=%d, last_region_idx=%s",
                    x_tensor.shape, emb_dim, n_regions, len(y_region), aux_hint)
    else:
        raise ValueError(f"--target must be region|category (got {target!r})")

    # [ONLY-FOLD] mirror train.py: force the canonical 5-split so fold k matches the
    # per-fold substrate cell (s0_f<k>) + the seeded log_T region_transition_log_..._fold{k+1}.
    # `splits` carries (true_fold_idx, (train_idx, val_idx)) so the log_T index is preserved.
    _n_splits = 5 if only_fold is not None else max(2, folds)
    sgkf = StratifiedGroupKFold(n_splits=_n_splits, shuffle=True, random_state=seed)
    _all_splits = list(sgkf.split(np.zeros(len(y_cat)), y_cat, groups=userids))
    if only_fold is not None:
        if not (0 <= only_fold < _n_splits):
            raise SystemExit(f"--only-fold {only_fold} out of range for n_splits={_n_splits}")
        splits = [(only_fold, _all_splits[only_fold])]
        n_target = 1
    else:
        splits = list(enumerate(_all_splits[:folds]))
        n_target = folds

    out_dir = Path("docs/results/P1")
    out_dir.mkdir(parents=True, exist_ok=True)
    # only-fold runs get a distinct checkpoint per fold so they never collide on resume.
    _ckpt_folds = folds if only_fold is None else 5
    _ckpt_tag = tag if only_fold is None else f"{tag or ''}_onlyfold{only_fold}"
    ckpt_path = _checkpoint_path(out_dir, state, input_type, _ckpt_folds, epochs, _ckpt_tag)
    ckpt = _load_checkpoint(ckpt_path) if resume else {}
    if ckpt:
        logger.info(
            "Resuming from checkpoint %s — existing heads: %s",
            ckpt_path,
            {h: len(ckpt.get("heads", {}).get(h, {}).get("per_fold", [])) for h in ckpt.get("heads", {})},
        )
    else:
        logger.info("No checkpoint — starting fresh. Will save to %s after each fold.", ckpt_path)

    # Seed the checkpoint shell with run-level metadata so a kill between
    # --resume invocations still carries seed / n_regions forward.
    results = dict(ckpt.get("heads", {}))
    for head_name in heads:
        head_max_lr = max_lr if max_lr is not None else _HEAD_MAX_LR.get(head_name, 3e-3)
        logger.info("=" * 60)
        logger.info("HEAD: %s (%d folds x %d epochs, max_lr=%.0e, ls=%.2f, input_ln=%s)",
                    head_name, folds, epochs, head_max_lr, label_smoothing, input_ln)
        logger.info("=" * 60)

        # Resume: start from where this head left off.
        head_state = results.get(head_name, {})
        fold_metrics: list = list(head_state.get("per_fold", []))
        completed = len(fold_metrics)
        if completed >= n_target:
            logger.info(
                "Head %s already has %d/%d folds — skipping (delete %s to re-run).",
                head_name, completed, folds, ckpt_path,
            )
            # Make sure aggregate is recomputed + emitted even if this head
            # was fully complete in a prior session. The final-table print
            # below reads ``aggregate`` unconditionally.
            if "aggregate" not in head_state:
                agg = {}
                for key in ["accuracy", "top5_acc", "top10_acc", "mrr", "f1"]:
                    vals = [m.get(key, 0.0) for m in fold_metrics]
                    agg[f"{key}_mean"] = float(np.mean(vals))
                    # AUDIT-C6: ddof=1 (sample std) matches MTL-side
                    # ``statistics.stdev`` so cross-pipeline σ comparisons
                    # use the same convention. For n=5 this is ~12% larger
                    # than population std (np.std default).
                    agg[f"{key}_std"] = float(np.std(vals, ddof=1)) if len(vals) > 1 else 0.0
                results[head_name] = {**head_state, "per_fold": fold_metrics, "aggregate": agg}
            continue
        if completed > 0:
            logger.info(
                "Head %s resuming at fold %d/%d (%d folds already in checkpoint).",
                head_name, completed, folds, completed,
            )

        for fold_idx, (train_idx, val_idx) in splits:
            if only_fold is None and fold_idx < completed:
                continue
            # AUDIT-C4 — when per_fold_transition_dir is set, override the
            # head's transition_path with the leak-free fold-specific file.
            # The fold split here uses the same StratifiedGroupKFold(seed=42)
            # as compute_region_transition.py --per-fold, so fold N here
            # matches region_transition_log_fold{N+1}.pt by construction.
            fold_overrides = dict(overrides)
            if per_fold_transition_dir is not None:
                # F51 seeded naming: region_transition_log_seed{S}_fold{N}.pt.
                # Trainer hard-fails on legacy unseeded files; STL is now
                # consistent. Falls back to legacy only if seeded missing
                # AND legacy present (loud warning) — for backwards compat
                # with old experiments still on the legacy path.
                pf_seeded = Path(per_fold_transition_dir) / f"region_transition_log_seed{seed}_fold{fold_idx + 1}.pt"
                pf_legacy = Path(per_fold_transition_dir) / f"region_transition_log_fold{fold_idx + 1}.pt"
                if pf_seeded.exists():
                    pf_path = pf_seeded
                elif pf_legacy.exists():
                    logger.warning(
                        "[C4 STL] using LEGACY unseeded log_T at %s — only valid "
                        "for seed=42; non-42 seeds leak val transitions. Build "
                        "seeded version with: python scripts/compute_region_transition.py "
                        "--state %s --per-fold --seed %d",
                        pf_legacy, state, seed,
                    )
                    pf_path = pf_legacy
                else:
                    raise FileNotFoundError(
                        f"per_fold_transition_dir set but neither {pf_seeded} "
                        f"nor legacy {pf_legacy} exists. Build seeded with: "
                        f"python scripts/compute_region_transition.py "
                        f"--state {state} --per-fold --seed {seed}"
                    )
                # Stale-log_T freshness preflight (CLAUDE.md hard rule; shared
                # portable util). The seeded file leaks +8..+12 pp into reg Acc@10
                # if it predates the next_region.parquet it was built from.
                assert_log_t_fresh(pf_path, state=state, seed=seed, n_splits=_n_splits)
                fold_overrides["transition_path"] = str(pf_path)
                logger.info("[C4 STL] fold %d using per-fold log_T %s", fold_idx, pf_path)
            t0 = time.time()
            metrics = _train_single_task(
                head_name, x_tensor, y_tensor, train_idx, val_idx,
                emb_dim, n_classes, epochs, batch_size, seed + fold_idx,
                fold_overrides, head_max_lr, label_smoothing, input_ln,
                aux_tensor=last_region_tensor,
                mtl_preencoder=mtl_preencoder,
                preenc_hidden=preenc_hidden,
                preenc_layers=preenc_layers,
                preenc_dropout=preenc_dropout,
                loss_cfg=loss_cfg,
            )
            elapsed = time.time() - t0
            fold_metrics.append(metrics)
            logger.info(
                "  fold %d: Acc@1=%.4f Acc@5=%.4f Acc@10=%.4f MRR=%.4f F1=%.4f (%.1fs, best_ep=%d)",
                fold_idx,
                metrics.get("accuracy", 0),
                metrics.get("top5_acc", 0),
                metrics.get("top10_acc", 0),
                metrics.get("mrr", 0),
                metrics.get("f1", 0),
                elapsed,
                metrics.get("best_epoch", 0),
            )

            # Checkpoint after every fold so a kill at any point loses at
            # most the in-progress fold. Atomic write via temp-rename keeps
            # the on-disk copy valid even if Python dies during save.
            results[head_name] = {
                "per_fold": fold_metrics,
                "config": {
                    "max_lr": head_max_lr,
                    "label_smoothing": label_smoothing,
                    "input_layernorm": input_ln,
                    "overrides": overrides,
                    "input_type": input_type,
                    "loss_cfg": loss_cfg,
                },
            }
            _save_checkpoint(ckpt_path, {
                "state": state, "folds": folds, "epochs": epochs, "seed": seed,
                "input_type": input_type, "n_regions": int(n_regions),
                "heads": results,
            })

        # Aggregate for this head now that all folds are done.
        agg = {}
        for key in ["accuracy", "top5_acc", "top10_acc", "mrr", "f1"]:
            vals = [m.get(key, 0.0) for m in fold_metrics]
            agg[f"{key}_mean"] = float(np.mean(vals))
            # AUDIT-C6: ddof=1 to match MTL-side ``statistics.stdev``
            agg[f"{key}_std"] = float(np.std(vals, ddof=1)) if len(vals) > 1 else 0.0

        # AUDIT-C1: per-metric aggregate. For each canonical metric, take
        # its value at ITS OWN best epoch in every fold and aggregate.
        # Pre-fix the only aggregate was at top10-best epoch — biased.
        agg_per_metric: dict = {}
        for selector in CANONICAL_METRICS:
            for reported in CANONICAL_METRICS:
                vals = [
                    m.get("per_metric_best", {}).get(selector, {}).get(reported, 0.0)
                    for m in fold_metrics
                ]
                agg_per_metric[f"{reported}_at_{selector}_best_mean"] = (
                    float(np.mean(vals)) if vals else 0.0
                )
                agg_per_metric[f"{reported}_at_{selector}_best_std"] = (
                    float(np.std(vals, ddof=1)) if len(vals) > 1 else 0.0
                )

        results[head_name] = {
            "per_fold": fold_metrics,
            "aggregate": agg,
            "aggregate_per_metric_best": agg_per_metric,
            "config": {
                "max_lr": head_max_lr,
                "label_smoothing": label_smoothing,
                "input_layernorm": input_ln,
                "overrides": overrides,
                "input_type": input_type,
            },
        }
        logger.info(
            "  AGGREGATE: Acc@1=%.4f+/-%.4f  Acc@10=%.4f+/-%.4f  MRR=%.4f+/-%.4f  F1=%.4f+/-%.4f",
            agg["accuracy_mean"], agg["accuracy_std"],
            agg["top10_acc_mean"], agg["top10_acc_std"],
            agg["mrr_mean"], agg["mrr_std"],
            agg["f1_mean"], agg["f1_std"],
        )

    # Summary table
    print("\n" + "=" * 80)
    print(f"P1 REGION-HEAD ABLATION - {state} - {folds}f x {epochs}ep - input={input_type}")
    print("=" * 80)
    print(f"{'Head':<25} {'Acc@1':>8} {'Acc@5':>8} {'Acc@10':>8} {'MRR':>8} {'F1':>8}")
    print("-" * 80)
    for head_name in heads:
        a = results[head_name]["aggregate"]
        print(f"{head_name:<25} {a['accuracy_mean']*100:>7.2f}% {a['top5_acc_mean']*100:>7.2f}% "
              f"{a['top10_acc_mean']*100:>7.2f}% {a['mrr_mean']*100:>7.2f}% {a['f1_mean']*100:>7.2f}%")

    # Markov baseline reference (per-fold Markov on region sequences — same
    # for all input types since Markov uses the region-transition graph, not
    # the embedding view). See docs/results/P0/...
    print("-" * 80)
    markov = {"alabama": "~21.3%", "florida": "~45.9%"}.get(state, "?")
    print(f"{'Markov 1-step (floor)':<25} {'~12%':>8} {'—':>8} {markov:>8} {'—':>8} {'—':>8}")
    print("=" * 80)

    # Save the final consolidated JSON (same schema as pre-resume version).
    tag_s = f"_{tag}" if tag else ""
    out_path = out_dir / f"region_head_{state}_{input_type}_{folds}f_{epochs}ep{tag_s}.json"
    with open(out_path, "w") as f:
        json.dump({"state": state, "folds": folds, "epochs": epochs, "seed": seed,
                    "input_type": input_type, "n_regions": int(n_regions),
                    "heads": results}, f, indent=2, default=str)
    logger.info("Saved: %s", out_path)

    # Remove the checkpoint once the final file is written — it served its
    # purpose. Leave the checkpoint in place if the aggregate JSON write
    # fails so the next invocation can retry without losing compute.
    try:
        ckpt_path.unlink(missing_ok=True)
        logger.info("Removed checkpoint %s (run complete).", ckpt_path)
    except OSError as e:
        logger.warning("Could not remove checkpoint %s: %s", ckpt_path, e)

    return results


def main():
    parser = argparse.ArgumentParser(description="P1 region-head ablation")
    parser.add_argument("--state", default="alabama")
    parser.add_argument("--heads", nargs="+", default=ALL_HEADS)
    parser.add_argument("--folds", type=int, default=1)
    parser.add_argument("--only-fold", type=int, default=None,
                        help="Run EXACTLY this 0-based fold of the canonical 5-split; preserves the "
                             "fold index for the seeded per-fold log_T (region_transition_log_seed{S}_fold{k+1}). "
                             "Takes precedence over --folds. Used for per-fold leak-safe baseline cells.")
    parser.add_argument("--epochs", type=int, default=30)
    parser.add_argument("--batch-size", type=int, default=2048)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--input-type", choices=["checkin", "region", "concat"], default="checkin")
    parser.add_argument("--override-hparams", nargs="*", default=None,
                        help="Override head defaults: key=value (e.g. hidden_dim=384)")
    parser.add_argument("--max-lr", type=float, default=None,
                        help="Override OneCycleLR max_lr (default: per-head)")
    parser.add_argument("--label-smoothing", type=float, default=0.0)
    parser.add_argument("--input-layernorm", action="store_true")
    parser.add_argument("--add-visit-features", dest="add_visit_features", action="store_true",
                        help="pre_freeze_gates A2: append the canonical per-visit raw features "
                             "(category one-hot + hour/dow sin/cos, = Check2HGI's node features) to "
                             "each window position of the input. Used to test whether HGI ⊕ raw "
                             "features closes Check2HGI's lift (feature-injection vs infomax-learning). "
                             "Faithful + alignment-validated; see scripts/pre_freeze_gates/a2_features.py.")
    parser.add_argument("--tag", type=str, default=None,
                        help="Suffix for result file (e.g. E1, E2_scale, E_region)")
    parser.add_argument("--resume", dest="resume", action="store_true", default=True,
                        help="Resume from checkpoint if one exists (default: on).")
    parser.add_argument("--no-resume", dest="resume", action="store_false",
                        help="Ignore any existing checkpoint and start fresh.")
    parser.add_argument("--region-emb-source",
                        default="check2hgi",
                        help="Which engine's region_embeddings.parquet to use for region/concat input_type. "
                             "Labels + sequences always come from check2hgi — only the embedding lookup changes. "
                             "Used for P1.5 embedding-substrate comparison (CH15). "
                             "'check2hgi_postpool' loads region_embeddings_postpool.parquet "
                             "(POI-mean → region-mean of canonical c2hgi check-in embeddings).")
    parser.add_argument("--mtl-preencoder", action="store_true",
                        help="Wrap the head with MTLnet's next_encoder stack (Linear+ReLU+LayerNorm+Dropout) "
                             "as a pre-processor, mirroring the MTL pipeline's upstream encoder without the "
                             "cross-attn / shared-backbone. Used by F41 (Exp D) to isolate the upstream "
                             "encoder contribution to the CH18 STL-vs-MTL region gap. Forces the head's "
                             "embed_dim to match --preenc-hidden.")
    parser.add_argument("--preenc-hidden", type=int, default=256,
                        help="Hidden / output dim of --mtl-preencoder (default 256, matches MTL shared_layer_size).")
    parser.add_argument("--preenc-layers", type=int, default=2,
                        help="Number of Linear blocks in --mtl-preencoder (default 2, matches MTL num_encoder_layers).")
    parser.add_argument(
        "--per-fold-transition-dir",
        dest="per_fold_transition_dir",
        type=str,
        default=None,
        metavar="DIR",
        help=(
            "AUDIT-C4 fix: directory containing per-fold transition matrices "
            "(``region_transition_log_fold{1..k}.pt``). When set, the trainer "
            "overrides ``transition_path`` per fold to the matching file, "
            "eliminating val→train leakage in the GETNext graph prior. "
            "Build with: python scripts/compute_region_transition.py "
            "--state STATE --per-fold"
        ),
    )
    parser.add_argument("--preenc-dropout", type=float, default=0.1,
                        help="Dropout in --mtl-preencoder (default 0.1, matches MTL encoder_dropout).")
    parser.add_argument("--engine-override", type=str, default=None,
                        choices=[None, "check2hgi", "check2hgi_poi2vec", "c2hgi_hgi_concat", "hgi",
                                 "check2hgi_resln", "check2hgi_resln_design_b",
                                 "check2hgi_resln_design_j",
                                 # T1.4: v14 substrate for the cat-arm STL ceiling
                                 # (cat uses check-in embeddings via next.parquet;
                                 # v14's ResLN+mae cat lever makes them distinct).
                                 "check2hgi_design_k_resln_mae_l0_1",
                                 "check2hgi_design_k_resln_l0_1",
                                 "check2hgi_design_k_l0_1", "check2hgi_dk_ovl", "hgi_dk_ovl",
                                 # closing_data board: substrate-column baseline engines (STL reg comparison)
                                 "baseline_b2c_onehot64", "baseline_geotree_skipgram",
                                 "check2hgi_ctle", "baseline_b2a_poi2vec",
                                 # v18: v17 recipe on the forward-only + elapsed-time substrate.
                                 # NOTE this list is a FOURTH allowlist, separate from the three in
                                 # src/configs/paths.py (enum, MTL_CHECK2HGI_ALLOWED_ENGINES, and
                                 # IoPaths.get_next_region). A new engine must be added here too or
                                 # the dedicated-region family dies at argparse with rc=2.
                                 "check2hgi_v18"],
                        help="Override the engine used to load next.parquet/next_region.parquet. "
                             "Region labels and graph maps still come from check2hgi. "
                             "Used by Design A probe and HGI-substrate category-injection probes.")
    parser.add_argument("--target", choices=["region", "category"], default="region",
                        help="Prediction target: 'region' (default, next-REGION) or 'category' "
                             "(next-CATEGORY, 7-class macro-F1; used by the merge_design study's "
                             "`cat = next_gru macro F1` protocol).")
    # T1.4 loss-calibration knobs (leak-free; class stats from train split only).
    parser.add_argument("--focal-gamma", type=float, default=0.0,
                        help="Focal focusing parameter (>0 enables focal). Cat-arm lever.")
    parser.add_argument("--logit-adjust-tau", type=float, default=0.0,
                        help="Menon ICLR'21 logit-adjustment temperature (>0 adds "
                             "tau*log P_train(y) to logits). Macro-F1-consistent; cat-arm primary.")
    parser.add_argument("--tail-loss", choices=["none", "balanced", "cb", "ldam"], default="none",
                        help="Imbalance handling: 'balanced' = sklearn balanced weights "
                             "(== compute_class_weights; reproduces the next_cv.py cat ceiling), "
                             "'cb' = Class-Balanced (Cui CVPR'19), 'ldam' = LDAM margins "
                             "(Cao NeurIPS'19). Cat baseline = balanced; reg-arm tail = cb/ldam.")
    parser.add_argument("--cb-beta", type=float, default=0.999,
                        help="Class-Balanced beta (only with --tail-loss cb).")
    parser.add_argument("--ldam-max-margin", type=float, default=0.5,
                        help="LDAM max per-class margin (only with --tail-loss ldam).")
    parser.add_argument("--ldam-scale", type=float, default=30.0,
                        help="LDAM logit scale (only with --tail-loss ldam).")
    parser.add_argument("--compile", dest="use_compile", action="store_true",
                        help="Wrap the head in torch.compile (CUDA only). Matches the "
                             "MTL champion's --compile so the STL reg ceiling shares the "
                             "board execution recipe. NUMERICALLY NON-IDENTICAL "
                             "(fused kernels) — opt-in; see SPEED_LEVERS.md.")
    parser.add_argument("--tf32", action="store_true",
                        help="Enable TF32 fp32 matmul + cudnn (CUDA only; no-op MPS/CPU). "
                             "NON-IDENTICAL (reduced matmul precision). Matches the MTL "
                             "board cell. NB p1 trains fp32, so tf32 bites harder here "
                             "than in the fp16-autocast MTL trainer.")
    args = parser.parse_args()

    global _P1_USE_COMPILE
    _P1_USE_COMPILE = bool(args.use_compile)
    if args.tf32:
        if torch.cuda.is_available():
            torch.set_float32_matmul_precision("high")
            torch.backends.cuda.matmul.allow_tf32 = True
            torch.backends.cudnn.allow_tf32 = True
            logger.info("TF32 enabled (matmul_precision=high, cudnn.allow_tf32=True)")
        else:
            logger.info("--tf32 requested but CUDA unavailable; ignored")
    if _P1_USE_COMPILE:
        logger.info("torch.compile enabled for the p1 head (CUDA only)")

    overrides = _parse_overrides(args.override_hparams)
    eo = EmbeddingEngine(args.engine_override) if args.engine_override else None
    loss_cfg = {
        "focal_gamma": args.focal_gamma,
        "logit_adjust_tau": args.logit_adjust_tau,
        "tail_mode": None if args.tail_loss == "none" else args.tail_loss,
        "cb_beta": args.cb_beta,
        "ldam_max_m": args.ldam_max_margin,
        "ldam_scale": args.ldam_scale,
    }
    run_ablation(
        args.state, args.heads, args.folds, args.epochs, args.batch_size, args.seed,
        args.input_type, overrides, args.max_lr, args.label_smoothing,
        args.input_layernorm, args.tag, resume=args.resume,
        region_emb_source=args.region_emb_source,
        mtl_preencoder=args.mtl_preencoder,
        preenc_hidden=args.preenc_hidden,
        preenc_layers=args.preenc_layers,
        preenc_dropout=args.preenc_dropout,
        per_fold_transition_dir=args.per_fold_transition_dir,
        engine_override=eo,
        target=args.target,
        loss_cfg=loss_cfg,
        add_visit_features=args.add_visit_features,
        only_fold=args.only_fold,
    )


if __name__ == "__main__":
    main()
