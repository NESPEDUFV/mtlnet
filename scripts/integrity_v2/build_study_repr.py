"""Study-only Check2HGI builder: same v14 Design-K recipe, but it SAVES the encoder and can
restrict representation training to the training users of one fold.

Why this script exists. The frozen v14 builder (scripts/probe/build_design_k_delaunay.py) keeps
the selected state in memory and writes only the three Parquet tables, so the trained network
cannot be resumed from its output directory. Every causal intervention in this study needs the
weights, because an intervention recomputes vectors under changed inputs. This script is a copy
of that recipe with three additions and no changes to the objective, the optimizer, or the
selection rule:

  1. --save-checkpoint      persist the selected state_dict plus full provenance
  2. --exclude-users-file   drop a fold's validation users from representation training
  3. --study-root           write everywhere EXCEPT the frozen engine directories

It never writes into output/check2hgi_design_k_resln_mae_l0_1/ or output/check2hgi_dk_ovl/.

Restricting the training users requires reindexing the hierarchy, because dropping check-ins
leaves some places with no training evidence at all (measured: 4.9% of Alabama places, 3.6% of
Florida places when one fold's users are removed). Keeping them in the index space would feed
zero-vector places to the discriminator as easy negatives and give the masked-place decoder a
zero reconstruction target. So places and regions are reindexed to the training-only space, and
the spatial scaffolding is remapped through place identifiers rather than positions.

Held-out inference needs NONE of that machinery: the check-in encoder consumes only node
features and the per-user sequence edges, and the check-in graph is a disjoint union of per-user
paths, so a held-out user encoded alone reproduces its full-graph vectors exactly (phase 0, F1
and F2). Inference lives in infer_checkins.py.

SCOPE LIMIT, carried forward from the earlier fold audit deliberately. The HGI Delaunay edges and
the POI2Vec table are full-dataset artifacts and are held FIXED across arms. They are a
place-spatial prior, not a check-in-level channel, so holding them fixed isolates the check-in
channel under study. A fully inductive rebuild of the spatial scaffolding is out of scope and is
recorded as an open channel in the report.

Usage:
    PYTHONPATH=src:research .venv/bin/python scripts/integrity_v2/build_study_repr.py \
        --state alabama --cell U1 --repr-seed 42 --epochs 500 --device cuda \
        --study-root results/check2hgi_integrity_v2
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import pickle
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
import torch
from torch.nn.utils import clip_grad_norm_
from torch.optim.lr_scheduler import StepLR
from torch_geometric.data import Data
from tqdm import trange

REPO = Path(__file__).resolve().parents[2]
N_CAT_FEATURES = 7   # node features are [category one-hot (7) | temporal (4)]
sys.path.insert(0, str(REPO / "src"))
sys.path.insert(0, str(REPO / "research"))
sys.path.insert(0, str(REPO / "scripts"))

from embeddings.check2hgi.model.Check2HGIModule import corruption          # noqa: E402
from embeddings.check2hgi.model.CheckinEncoder import CheckinEncoder        # noqa: E402
from embeddings.check2hgi.model.variants import ResidualLNEncoder, GATTimeEncoder  # noqa: E402
from embeddings.check2hgi.model.Checkin2POI import Checkin2POI              # noqa: E402
from embeddings.hgi.model.RegionEncoder import POI2Region                   # noqa: E402
from embeddings.check2hgi.reg_poi_aug import load_poi2vec_table             # noqa: E402
from probe.build_design_k_delaunay import (                                 # noqa: E402
    Check2HGI_DesignK, load_delaunay_edges, _compute_poi_category_aggregate,
)

# ---- the reported v14 recipe, pinned here so a default change upstream cannot drift the study --
V14 = dict(dim=64, num_layers=2, attention_head=4, alpha_c2p=0.4, alpha_p2r=0.3, alpha_r2c=0.3,
           mae_poi_lambda=0.3, mae_poi_mask_rate=0.15, mae_poi_gamma=3.0, anchor_lambda=0.1,
           gamma_init=1.0, lr=1e-3, weight_decay=0.0, max_norm=0.9, lr_gamma=1.0, epochs=500,
           encoder="resln", dropout=0.1)


def _revision() -> str:
    try:
        return subprocess.run(["git", "rev-parse", "HEAD"], cwd=str(REPO),
                              capture_output=True, text=True, check=True).stdout.strip()
    except Exception:
        return "unknown"


def _sha256(path: Path, cap: int = 64 << 20) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        while chunk := fh.read(1 << 20):
            h.update(chunk)
            if fh.tell() > cap:
                h.update(b"TRUNCATED")
                break
    return h.hexdigest()


def _arr_sha256(a: np.ndarray) -> str:
    return hashlib.sha256(np.ascontiguousarray(a).tobytes()).hexdigest()


def restrict_to_users(d: dict, keep_users: np.ndarray | None) -> tuple[dict, dict]:
    """Return (graph_dict, stats). With keep_users=None the graph is returned untouched.

    Reindexes check-ins, places and regions into the training-only space. Edge weights are NOT
    renormalized: the global min-max constants are (0.0, 1.0) on both the full and the restricted
    edge sets at both datasets (measured in phase 0), so recomputing them is a no-op, and keeping
    the frozen constants makes the arms differ only in which users were present.
    """
    md = d["metadata"].reset_index(drop=True)
    uid = md["userid"].to_numpy()
    n_full = len(md)
    if keep_users is None:
        stats = {"restricted": False, "n_checkins": n_full,
                 "n_pois": int(d["num_pois"]), "n_regions": int(d["num_regions"])}
        return d, stats

    keep_node = np.isin(uid, keep_users)
    node_new = -np.ones(n_full, dtype=np.int64)
    node_new[keep_node] = np.arange(int(keep_node.sum()))

    ei = np.asarray(d["edge_index"]); ew = np.asarray(d["edge_weight"], dtype=np.float32)
    keep_edge = keep_node[ei[0]] & keep_node[ei[1]]
    ei2 = np.stack([node_new[ei[0, keep_edge]], node_new[ei[1, keep_edge]]])
    ew2 = ew[keep_edge]

    # places that retain at least one training check-in
    c2p = np.asarray(d["checkin_to_poi"])
    poi_keep = np.unique(c2p[keep_node])
    poi_new = -np.ones(int(d["num_pois"]), dtype=np.int64)
    poi_new[poi_keep] = np.arange(len(poi_keep))
    c2p2 = poi_new[c2p[keep_node]]
    assert (c2p2 >= 0).all()

    p2r = np.asarray(d["poi_to_region"])
    reg_keep = np.unique(p2r[poi_keep])
    reg_new = -np.ones(int(d["num_regions"]), dtype=np.int64)
    reg_new[reg_keep] = np.arange(len(reg_keep))
    p2r2 = reg_new[p2r[poi_keep]]
    assert (p2r2 >= 0).all()

    ra = np.asarray(d["region_adjacency"])
    if ra.size:
        km = np.isin(ra[0], reg_keep) & np.isin(ra[1], reg_keep)
        ra2 = np.stack([reg_new[ra[0, km]], reg_new[ra[1, km]]])
    else:
        ra2 = np.zeros((2, 0), dtype=np.int64)

    sim = np.asarray(d["coarse_region_similarity"])
    sim2 = sim[np.ix_(reg_keep, reg_keep)] if sim.ndim == 2 and sim.size else sim

    placeid_to_idx = {pid: int(poi_new[i]) for pid, i in d["placeid_to_idx"].items()
                      if poi_new[i] >= 0}

    out = dict(d)
    out["node_features"] = np.asarray(d["node_features"])[keep_node]
    out["edge_index"] = ei2
    out["edge_weight"] = ew2
    out["checkin_to_poi"] = c2p2
    out["poi_to_region"] = p2r2
    out["region_adjacency"] = ra2
    out["region_area"] = np.asarray(d["region_area"])[reg_keep]
    out["coarse_region_similarity"] = sim2
    out["num_checkins"] = int(keep_node.sum())
    out["num_pois"] = int(len(poi_keep))
    out["num_regions"] = int(len(reg_keep))
    out["metadata"] = md[keep_node].reset_index(drop=True)
    out["placeid_to_idx"] = placeid_to_idx
    out.pop("poi_category_aggregate", None)      # must be recomputed from training check-ins only
    out.pop("poi_visit_count_log", None)

    stats = {
        "restricted": True,
        "n_checkins": int(keep_node.sum()), "n_checkins_full": n_full,
        "checkin_frac_kept": float(keep_node.mean()),
        "n_pois": int(len(poi_keep)), "n_pois_full": int(d["num_pois"]),
        "pois_dropped_no_training_visit": int(d["num_pois"]) - int(len(poi_keep)),
        "n_regions": int(len(reg_keep)), "n_regions_full": int(d["num_regions"]),
        "regions_dropped": int(d["num_regions"]) - int(len(reg_keep)),
        "n_users_kept": int(np.unique(uid[keep_node]).size),
        "edge_weight_min": float(ew2.min()) if ew2.size else 0.0,
        "edge_weight_max": float(ew2.max()) if ew2.size else 0.0,
    }
    return out, stats


def build(state: str, args) -> dict:

    # Capacity overrides. V14 is the frozen reference recipe; a sweep must vary FROM it visibly rather
    # than silently mutate it, so the overrides are applied to a local copy and recorded in the
    # manifest. dim changes the artifact width the downstream head sees; num_layers changes the
    # encoder's receptive field (k layers reach index distance k along the user's path).
    global V14
    _V14_REF = dict(V14)
    if args.dim or args.num_layers:
        V14 = dict(V14)
        if args.dim:
            V14["dim"] = int(args.dim)
        if args.num_layers:
            V14["num_layers"] = int(args.num_layers)
    state_lc = state.lower()
    seed = int(args.repr_seed)
    torch.manual_seed(seed); np.random.seed(seed)

    graph_path = REPO / "output" / "check2hgi" / state_lc / "temp" / "checkin_graph.pt"
    with open(graph_path, "rb") as fh:
        d_full = pickle.load(fh)

    keep_users = None
    excl_meta = {"exclude_users_file": None, "n_excluded_users": 0}
    if args.exclude_users_file:
        excl = json.loads(Path(args.exclude_users_file).read_text())
        val_users = np.asarray(excl["val_users"])
        all_users = d_full["metadata"]["userid"].to_numpy()
        keep_users = np.setdiff1d(np.unique(all_users), val_users)
        excl_meta = {"exclude_users_file": str(args.exclude_users_file),
                     "n_excluded_users": int(len(val_users)),
                     "split": {k: excl[k] for k in ("state", "seed", "fold", "n_folds", "engine")
                               if k in excl},
                     "val_users_sha256": _arr_sha256(np.sort(val_users))}

    # Nested user fraction, for the data-scaling curve.
    #
    # The curve must measure ADDING data, not swapping it, so the fractions are nested: users are
    # ordered once by a fixed seed and each fraction takes a prefix of that order, making every
    # smaller set a strict subset of every larger one. It composes with --exclude-users-file, and the
    # order matters: validation users are removed FIRST, then the fraction is taken from what remains,
    # so the held-out evaluation set is identical at every fraction and only the representation's
    # training data varies.
    frac_meta = {"user_fraction": None}
    if args.user_fraction is not None and args.user_fraction < 1.0:
        assert 0.0 < args.user_fraction <= 1.0, "--user-fraction must be in (0, 1]"
        pool = (np.unique(d_full["metadata"]["userid"].to_numpy()) if keep_users is None
                else np.asarray(keep_users))
        order = np.random.default_rng(int(args.user_fraction_seed)).permutation(pool.size)
        k = max(1, int(round(pool.size * args.user_fraction)))
        keep_users = np.sort(pool[order[:k]])
        frac_meta = {"user_fraction": float(args.user_fraction),
                     "user_fraction_seed": int(args.user_fraction_seed),
                     "pool_users": int(pool.size), "kept_users": int(k),
                     "nested": ("users are permuted once by the seed and each fraction takes a prefix, "
                                "so a smaller fraction is a strict subset of a larger one"),
                     "kept_users_sha256": _arr_sha256(keep_users)}
        print(f"[{state_lc}/{args.cell}] user fraction {args.user_fraction}: "
              f"{k} of {pool.size} users", flush=True)

    d, gstats = restrict_to_users(d_full, keep_users)

    # ------------------------------------------------------------------------------------------
    # NODE ENRICHMENT (E1 place identity, E2 continuous time)
    #
    # The motivating measurement, on Alabama: a check-in node carries eleven columns -- a 7-way
    # category one-hot plus hour and weekday as sin/cos pairs. Those eleven columns admit only 1152
    # distinct feature vectors across 113,846 visits, so a MEDIAN of 37 different places (worst case
    # 553) share one input vector. Two visits at unrelated places, same category and same hour, are
    # literally the same input to the encoder.
    #
    # That is the likeliest reason every honest arm plateaus at the label-only benchmark: once the
    # target's category is withheld, an eleven-column input over a per-user path has almost nothing
    # the nine observed labels do not already carry. The information was never in the node.
    #
    # Both additions below are legitimate at prediction time for OBSERVED visits: a system knows
    # where the user has been and when. Neither touches the target.
    enrich_meta: dict = {}
    if args.add_place_identity or args.add_continuous_time or args.add_region_identity:
        nf = np.asarray(d["node_features"], dtype=np.float32)
        md_e = d["metadata"].reset_index(drop=True)
        blocks = [nf]
        names = [f"canonical_{nf.shape[1]}"]

        # A note on WHY the place block needs the two options below.
        #
        # The pretext task builds negatives by permuting node feature ROWS (Check2HGIModule.py:27,
        # torch.randperm), so the discriminator is asked: real node encoding, or feature-shuffled one?
        # With the canonical eleven columns that is hard -- only 1152 distinct vectors exist, so a
        # permuted row often looks plausible and the encoder must use the GRAPH to tell them apart.
        # That pressure is where the sequence learning comes from.
        #
        # Appending a near-unique 64-d place signature makes the discrimination trivial: after
        # permutation the place block no longer agrees with the node's neighbourhood, so real and fake
        # separate on that block alone, with no graph reasoning. Measured: the pretext loss falls 59
        # percent (0.2112 to 0.0875) while the downstream score falls 1.86 points. A pretext loss
        # improving as the downstream metric degrades is the signature of a shortcut.
        #
        # Two mitigations, each addressing one half of the mechanism:
        #   --place-project-dim  reduces the block's capacity so it cannot carry a unique signature
        #   --place-standardize  removes the scale advantage (the raw block's mean|x| is 5.1x the
        #                        category one-hot's and its max is 12.5 against 1.0)
        if args.add_place_identity:
            # E1: the place's own frozen embedding, joined by place id. The pipeline already computes
            # a place-level representation, so reusing it avoids fitting a fresh 11,848-row learnable
            # table on this much data, which would overfit. Places with no row get zeros, which the
            # encoder can distinguish from any real place because the frozen rows are dense.
            pe_path = REPO / "output" / "hgi" / state_lc / "poi_embeddings.parquet"
            if not pe_path.exists():
                pe_path = REPO / "output" / "hgi" / state_lc / "embeddings.parquet"
            pe = pd.read_parquet(pe_path)
            key = "placeid" if "placeid" in pe.columns else pe.columns[0]
            dim_cols = sorted([c for c in pe.columns if str(c).isdigit()], key=int)
            lut = {str(k): i for i, k in enumerate(pe[key].astype(str).to_numpy())}
            P = pe[dim_cols].to_numpy(dtype=np.float32)
            rows = np.array([lut.get(str(p), -1) for p in md_e["placeid"].astype(str).to_numpy()])
            block = np.zeros((len(md_e), P.shape[1]), dtype=np.float32)
            hit = rows >= 0
            block[hit] = P[rows[hit]]
            tag = f"place_embedding_{P.shape[1]}"
            if args.place_standardize:
                # per-column zero mean, unit variance, so the block competes with the canonical
                # columns on equal numeric footing instead of dominating the first layer by scale
                mu, sd = block.mean(0, keepdims=True), block.std(0, keepdims=True)
                block = (block - mu) / np.clip(sd, 1e-6, None)
                block = np.clip(block, -3.0, 3.0).astype(np.float32)   # cap the 12.5 outliers
                tag += "_std"
            if args.place_project_dim and args.place_project_dim < block.shape[1]:
                # A FIXED random projection, seeded, applied identically at build and at readout.
                # Reducing to k dimensions destroys the per-place uniqueness that makes the
                # discriminator's job trivial while preserving coarse spatial and semantic
                # neighbourhood structure (Johnson-Lindenstrauss). Deterministic from the seed, so
                # inference can reproduce it exactly rather than approximately.
                rp = np.random.default_rng(1234).normal(
                    0.0, 1.0 / np.sqrt(args.place_project_dim),
                    size=(block.shape[1], args.place_project_dim)).astype(np.float32)
                block = (block @ rp).astype(np.float32)
                tag += f"_proj{args.place_project_dim}"
            blocks.append(block); names.append(tag)
            enrich_meta["place_identity"] = {
                "source": str(pe_path.relative_to(REPO)), "dim": int(P.shape[1]),
                "places_matched": int(hit.sum()), "places_total": int(len(md_e)),
                "match_rate": float(hit.mean()),
                "legitimacy": "the place of an OBSERVED visit is known at prediction time",
                "standardized": bool(args.place_standardize),
                "projected_dim": int(args.place_project_dim) or None,
                "shortcut_note": ("negatives are row-permuted features, so a per-place unique "
                                  "signature lets the discriminator separate real from fake without "
                                  "using the graph; projection and standardization remove that"),
            }

        if args.add_region_identity:
            # E6: the REGION the visit happened in, as a node feature.
            #
            # Legitimacy. The region of an OBSERVED visit is where the user already was, so it is
            # known at prediction time; the region tower already consumes exactly this information as
            # its own input stream, indexed by historical place. What must never be added is the
            # TARGET's region, which is the region task's label. Nothing here touches the target.
            #
            # Why it might help where place identity did not. A region is a coarse bucket -- 1,109
            # census tracts against 11,848 places at Alabama -- so it carries roughly a tenth of the
            # per-visit uniqueness that let the place block defeat the shuffled-versus-real
            # discriminator. If the hijacking diagnosis is right, a coarser spatial signal should be
            # usable where a near-unique one was not. That makes this arm a test of the diagnosis as
            # well as a candidate improvement.
            #
            # The same two mitigations apply and are recommended: standardize and project.
            re_path = REPO / "output" / "check2hgi_design_k_resln_mae_l0_1" / state_lc / "region_embeddings.parquet"
            if not re_path.exists():
                re_path = REPO / "output" / "hgi" / state_lc / "region_embeddings.parquet"
            rdf = pd.read_parquet(re_path)
            # The region table names its key `region_id` and its dimensions `reg_0..reg_63`, NOT the
            # digit-named `0..63` the place table uses. Assuming the place convention here produced a
            # ZERO-WIDTH block that concatenated silently and made two arms indistinguishable from
            # their own baselines. Both conventions are accepted now, and the assertion below makes a
            # zero-width block impossible to ship again.
            rkey = next((k for k in ("region_id", "region_idx") if k in rdf.columns), rdf.columns[0])
            rdims = sorted([c for c in rdf.columns if str(c).isdigit()], key=int)
            if not rdims:
                rdims = sorted([c for c in rdf.columns if str(c).startswith("reg_")
                                and str(c)[4:].isdigit()], key=lambda c: int(str(c)[4:]))
            assert rdims, (f"no dimension columns found in {re_path.name}; "
                           f"columns are {list(rdf.columns)[:6]}")
            R = rdf[rdims].to_numpy(dtype=np.float32)
            rlut = {int(k): i for i, k in enumerate(rdf[rkey].to_numpy())}
            # visit -> place -> region, using the graph's own maps so no new join can go wrong
            c2p_e = np.asarray(d["checkin_to_poi"]); p2r_e = np.asarray(d["poi_to_region"])
            reg_of_visit = p2r_e[c2p_e]
            rr2 = np.array([rlut.get(int(v), -1) for v in reg_of_visit])
            rblk = np.zeros((len(md_e), R.shape[1]), dtype=np.float32)
            rh = rr2 >= 0
            rblk[rh] = R[rr2[rh]]
            rtag = f"region_embedding_{R.shape[1]}"
            if args.place_standardize:
                mu, sd = rblk.mean(0, keepdims=True), rblk.std(0, keepdims=True)
                rblk = np.clip((rblk - mu) / np.clip(sd, 1e-6, None), -3.0, 3.0).astype(np.float32)
                rtag += "_std"
            if args.place_project_dim and args.place_project_dim < rblk.shape[1]:
                rp = np.random.default_rng(5678).normal(
                    0.0, 1.0 / np.sqrt(args.place_project_dim),
                    size=(rblk.shape[1], args.place_project_dim)).astype(np.float32)
                rblk = (rblk @ rp).astype(np.float32)
                rtag += f"_proj{args.place_project_dim}"
            blocks.append(rblk); names.append(rtag)
            enrich_meta["region_identity"] = {
                "source": str(re_path.relative_to(REPO)), "dim": int(R.shape[1]),
                "regions_matched": int(rh.sum()), "visits_total": int(len(md_e)),
                "distinct_regions": int(len(np.unique(reg_of_visit))),
                "standardized": bool(args.place_standardize),
                "projected_dim": int(args.place_project_dim) or None,
                "legitimacy": ("the region of an OBSERVED visit is where the user already was and is "
                               "already an input to the region tower; the TARGET's region is never "
                               "added"),
                "why_coarser_may_work": ("1,109 regions against 11,848 places, so about a tenth of "
                                         "the per-visit uniqueness that let the place block defeat "
                                         "the real-versus-shuffled discriminator"),
            }
            print(f"[{state_lc}/{args.cell}] region block: {rblk.shape[1]} cols, "
                  f"{int(len(np.unique(reg_of_visit)))} distinct regions, matched {rh.mean():.4f}",
                  flush=True)

        if args.add_continuous_time:
            # E2: elapsed time. The gap between consecutive visits currently lives ONLY in the scalar
            # edge weight, and 46.8 percent of Alabama's edges carry a weight below 0.01, which erases
            # the difference between a two-day and a two-month gap. These columns restore it. All are
            # measured up to the visit itself, never forward to the target.
            dtv = pd.to_datetime(md_e["datetime"])
            uidv = md_e["userid"].to_numpy()
            t = dtv.astype("int64").to_numpy() / 1e9 / 3600.0          # hours since epoch
            gap = np.zeros(len(t), dtype=np.float32)
            since_first = np.zeros(len(t), dtype=np.float32)
            for u in np.unique(uidv):
                m = np.where(uidv == u)[0]
                tu = t[m]
                gap[m[1:]] = np.diff(tu)
                since_first[m] = tu - tu[0]
            block = np.stack([
                np.log1p(np.clip(gap, 0, None)) / 10.0,               # log hours since previous visit
                np.log1p(np.clip(since_first, 0, None)) / 10.0,       # log hours since first visit
                np.clip(gap, 0, 24.0) / 24.0,                         # same-day gap, linear
                (gap == 0).astype(np.float32),                        # first visit indicator
            ], axis=1).astype(np.float32)
            blocks.append(block); names.append("continuous_time_4")
            enrich_meta["continuous_time"] = {
                "columns": ["log1p_gap_hours/10", "log1p_since_first_hours/10",
                            "gap_clipped_24h/24", "is_first_visit"],
                "median_gap_hours": float(np.median(gap[gap > 0])),
                "p90_gap_hours": float(np.percentile(gap[gap > 0], 90)),
                "legitimacy": ("all measured up to the visit itself; the gap to the TARGET is never "
                               "added, which would be the leak this study exists to prevent"),
            }

        # A requested enrichment that contributes ZERO columns is a silent no-op: the arm builds,
        # trains, scores, and is indistinguishable from its own baseline, so any conclusion drawn from
        # it is about the baseline. That happened once (a region block named its columns reg_N while
        # the parser expected N, giving region_embedding_0_std at width zero) and produced two void
        # arms whose numbers were briefly read as a confirmation. Fail closed instead.
        for _blk, _nm in zip(blocks[1:], names[1:]):
            assert _blk.shape[1] > 0, (
                f"enrichment block '{_nm}' contributed 0 columns; a requested block must add width "
                "or the arm is identical to its baseline")
        _requested = sum([bool(args.add_place_identity), bool(args.add_region_identity),
                          bool(args.add_continuous_time)])
        assert len(blocks) - 1 == _requested, (
            f"{_requested} enrichment blocks requested but {len(blocks)-1} assembled: {names}")

        d = dict(d)
        d["node_features"] = np.concatenate(blocks, axis=1).astype(np.float32)
        enrich_meta["layout"] = names
        enrich_meta["in_channels"] = int(d["node_features"].shape[1])
        print(f"[{state_lc}/{args.cell}] enriched node features: {nf.shape[1]} -> "
              f"{d['node_features'].shape[1]} channels ({' + '.join(names)})", flush=True)

    # Forward-only (causal) training graph. The canonical preprocessor emits both directions of
    # every consecutive-visit edge (preprocess.py lines 196-197), so a visit's vector is convolved
    # over a neighbourhood that includes the visit AFTER it. Dropping the backward direction here
    # makes the representation trained under the same information a deployed system would have:
    # a visit may see its past, never its future.
    #
    # This is the arm that answers whether the representation learns transferable transition
    # structure as opposed to reading the target's own identity. Every other arm in this study reads
    # causally from weights TRAINED bidirectionally, which bounds the honest number from below but
    # cannot estimate it. Only a forward-only BUILD can.
    causal_meta = {"forward_only": False}
    if args.forward_only:
        ei = np.asarray(d["edge_index"]); ew = np.asarray(d["edge_weight"], dtype=np.float32)
        # The check-in graph is a disjoint union of per-user paths whose node ids are in visit order
        # (established as structural fact F1), so "forward" is exactly src < tgt. Same-POI edges, if
        # present, are not temporal and are left untouched; this build uses the sequence graph only.
        fwd = ei[0] < ei[1]
        n_before = int(ei.shape[1])
        d = dict(d)
        d["edge_index"] = ei[:, fwd]
        d["edge_weight"] = ew[fwd]
        causal_meta = {
            "forward_only": True,
            "edges_before": n_before,
            "edges_after": int(fwd.sum()),
            "dropped_backward": int(n_before - int(fwd.sum())),
            "rule": "kept edges with src < tgt; node ids are in per-user visit order (fact F1)",
            "semantics": ("a visit's representation is computed from its own past only, at TRAINING "
                          "time as well as at readout, which is the deployed information set"),
        }
        print(f"[{state_lc}/{args.cell}] forward-only graph: {causal_meta['edges_after']} of "
              f"{n_before} edges kept ({causal_meta['dropped_backward']} backward dropped)", flush=True)

    # OPTION B: keep the graph bidirectional, but make the BACKWARD edge carry no category identity.
    #
    # The reasoning, which is the author's own architectural argument taken seriously. An encoder is
    # supposed to learn transition structure from two-sided context; what it must not do is read the
    # label it is about to be asked for. Those two can be separated. A backward message from visit
    # v+1 into visit v is legitimate insofar as it carries WHEN and WHERE the next visit happened,
    # information a deployed system often has (a user asking "what should I do at 8pm near here"
    # supplies both), and illegitimate insofar as it carries WHICH CATEGORY, which is the answer.
    #
    # Implementation: duplicate every check-in node. The original keeps its full features and is used
    # wherever the node is a SOURCE of forward messages. A twin with the category columns zeroed
    # replaces it as the source of BACKWARD messages. Forward edges point from the original, backward
    # edges from the twin, so a node's own representation still sees its past in full while its future
    # reaches it stripped of category identity.
    #
    # This keeps the neighbourhood, keeps the temporal signal, and removes exactly the copied answer.
    if args.mask_backward_category:
        nf = np.asarray(d["node_features"])
        ei = np.asarray(d["edge_index"]); ew = np.asarray(d["edge_weight"], dtype=np.float32)
        n = nf.shape[0]
        # Same hazard as option D, arriving from the other side: the reconstruction target is a
        # scatter-mean of the category columns over places. The twins carry ZEROED category columns
        # and are mapped to a sentinel place, so if the target were derived after this rewrite the
        # sentinel would acquire a spurious row and (were the mapping ever changed) real places could
        # be diluted by zero rows. Pin the target to the ORIGINAL features and place map now.
        if "poi_category_aggregate" not in d:
            c2p0 = np.asarray(d["checkin_to_poi"])
            npoi0 = int(d["num_pois"])
            agg = np.zeros((npoi0, N_CAT_FEATURES), dtype=np.float32)
            cnt = np.zeros(npoi0, dtype=np.float32)
            np.add.at(agg, c2p0, nf[:, :N_CAT_FEATURES].astype(np.float32))
            np.add.at(cnt, c2p0, 1.0)
            d = dict(d)
            d["poi_category_aggregate"] = agg / np.clip(cnt, 1.0, None)[:, None]
            print(f"[{state_lc}/{args.cell}] pinned poi_category_aggregate to the original "
                  f"{npoi0} places before adding twins", flush=True)
        twin = nf.copy(); twin[:, :N_CAT_FEATURES] = 0.0
        nf2 = np.concatenate([nf, twin], axis=0)          # ids n..2n-1 are the category-free twins
        fwd = ei[0] < ei[1]
        ei_f = ei[:, fwd]
        ei_b = ei[:, ~fwd].copy()
        ei_b[0] = ei_b[0] + n                              # backward messages leave from the twin
        d = dict(d)
        d["node_features"] = nf2
        d["edge_index"] = np.concatenate([ei_f, ei_b], axis=1)
        d["edge_weight"] = np.concatenate([ew[fwd], ew[~fwd]])
        # The twins must exist as message SOURCES without becoming extra check-ins anywhere else.
        # Checkin2POI pools EVERY row of x into its place, so naively duplicating checkin_to_poi
        # would pool each place's visits twice and change the place embeddings -- a second,
        # unintended intervention on top of the one under test. Mapping the twins to a sentinel
        # place index that no real place occupies keeps them out of the pool while keeping the
        # array long enough to index by node id.
        c2p = np.asarray(d["checkin_to_poi"])
        sentinel = int(d["num_pois"])          # one past the last real place
        d["checkin_to_poi"] = np.concatenate([c2p, np.full(n, sentinel, dtype=c2p.dtype)])
        d["num_pois"] = sentinel + 1
        # the sentinel place needs a region too, or poi_to_region indexing goes out of bounds
        p2r = np.asarray(d["poi_to_region"])
        d["poi_to_region"] = np.concatenate([p2r, np.array([0], dtype=p2r.dtype)])
        # num_pois grew by one, so every per-place array must grow with it, including the pinned
        # reconstruction target. The sentinel's row is zeros: no real check-in maps to it.
        pca = np.asarray(d["poi_category_aggregate"], dtype=np.float32)
        if pca.shape[0] == sentinel:
            d["poi_category_aggregate"] = np.concatenate(
                [pca, np.zeros((1, pca.shape[1]), dtype=np.float32)], axis=0)
        causal_meta.setdefault("masked_backward_category", {})["twin_isolation"] = (
            f"twins mapped to sentinel place {sentinel} (num_pois {sentinel} -> {sentinel + 1}) so "
            "they contribute no messages to any real place's pooled embedding")
        causal_meta["masked_backward_category"] = {
            "nodes_before": int(n), "nodes_after": int(nf2.shape[0]),
            "forward_edges": int(fwd.sum()), "backward_edges": int((~fwd).sum()),
            "rule": ("backward messages originate from a twin node whose category one-hot is zeroed; "
                     "forward messages are unchanged"),
            "readout_nodes": "the first n nodes only; twins exist purely as message sources",
            "rationale": ("separates the legitimate part of two-sided context (when and where the "
                          "next visit happened) from the illegitimate part (which category it was)"),
        }
        print(f"[{state_lc}/{args.cell}] masked-backward: {n} -> {nf2.shape[0]} nodes, "
              f"{int(fwd.sum())} forward + {int((~fwd).sum())} backward edges", flush=True)

    # OPTION D: remove the category one-hot from the node features entirely.
    #
    # This attacks the mechanism rather than the topology. The audit established that a check-in
    # node's features are [category one-hot (7) | temporal (4)] and that the backward edge places the
    # target node one hop from the last observed visit, so what leaks is a one-hot COPY. If no node
    # carries a category one-hot, there is nothing to copy, and the temporal columns that remain are
    # largely knowable before the visit happens.
    #
    # The cost this arm pays, and it is a real one: the observed visits lose their category identity
    # too, which is information a deployed system legitimately has. So this arm is not the honest
    # upper bound; it is the test of whether the one-hot was the whole story. Compare it against the
    # forward-only arm, which keeps the one-hot and removes the edge.
    if args.drop_category_features:
        nf = np.asarray(d["node_features"])
        d = dict(d)
        # The masked-place reconstruction objective takes its TARGET from these same columns: it
        # scatter-means node_features[:, :7] over places to build poi_category_aggregate. Deleting
        # the columns therefore deletes the supervision signal as well as the input feature, which
        # would confound "the encoder cannot see the category" with "the encoder is no longer trained
        # to predict category composition". Precompute the target from the ORIGINAL features first,
        # so the arm removes the INPUT only and the training objective is unchanged.
        if "poi_category_aggregate" not in d:
            c2p = np.asarray(d["checkin_to_poi"])
            npoi = int(d["num_pois"])
            agg = np.zeros((npoi, N_CAT_FEATURES), dtype=np.float32)
            cnt = np.zeros(npoi, dtype=np.float32)
            np.add.at(agg, c2p, nf[:, :N_CAT_FEATURES].astype(np.float32))
            np.add.at(cnt, c2p, 1.0)
            d["poi_category_aggregate"] = agg / np.clip(cnt, 1.0, None)[:, None]
            print(f"[{state_lc}/{args.cell}] precomputed poi_category_aggregate from the original "
                  f"features ({npoi} places) so dropping the input does not remove the target",
                  flush=True)
        d["node_features"] = nf[:, N_CAT_FEATURES:]
        causal_meta["dropped_category_features"] = {
            "columns_removed": N_CAT_FEATURES,
            "in_channels_before": int(nf.shape[1]),
            "in_channels_after": int(nf.shape[1] - N_CAT_FEATURES),
            "rationale": ("the leak is a one-hot copy through the backward edge; with no category "
                          "one-hot on any node there is nothing to copy"),
            "cost": ("observed visits also lose their category identity, which a deployed system "
                     "would have, so this is a mechanism test rather than an honest upper bound"),
        }
        print(f"[{state_lc}/{args.cell}] dropped {N_CAT_FEATURES} category columns: "
              f"{nf.shape[1]} -> {nf.shape[1] - N_CAT_FEATURES} input channels", flush=True)

    in_channels = int(np.asarray(d["node_features"]).shape[1])
    num_pois, num_regions = int(d["num_pois"]), int(d["num_regions"])
    print(f"[{state_lc}/{args.cell}] checkins={d['num_checkins']} pois={num_pois} "
          f"regions={num_regions} feat={in_channels} restricted={gstats['restricted']}", flush=True)

    device = torch.device(args.device)
    poi2vec = load_poi2vec_table(state, num_pois, d["placeid_to_idx"])
    # The Delaunay place table is initialized and anchored from this fixed 64-d table, so a width sweep
    # fails outright unless the anchor is brought to the same width. This is an architectural constraint
    # of the recipe, not an incidental bug: the 64 is baked into the distillation target.
    #
    # For dim != 64 the anchor is mapped with a FIXED seeded random projection (or padded with zeros
    # when widening), which preserves relative geometry up to a Johnson-Lindenstrauss distortion while
    # keeping the arm reproducible. It is a deviation from the frozen recipe and is recorded as one:
    # a width arm is therefore not a pure width contrast, it is width plus a re-expressed anchor, and
    # the report must say so rather than present it as an isolated capacity result.
    anchor_meta = {"anchor_dim_native": int(poi2vec.shape[1]), "anchor_adapted": False}
    if int(poi2vec.shape[1]) != int(V14["dim"]):
        import torch as _t
        src_d, dst_d = int(poi2vec.shape[1]), int(V14["dim"])
        if dst_d < src_d:
            _rp = _t.from_numpy(np.random.default_rng(90210).normal(
                0.0, 1.0 / np.sqrt(dst_d), size=(src_d, dst_d)).astype(np.float32))
            poi2vec = (poi2vec.float() @ _rp)
            how = f"random projection {src_d}->{dst_d} (seed 90210)"
        else:
            pad = _t.zeros((poi2vec.shape[0], dst_d - src_d), dtype=_t.float32)
            poi2vec = _t.cat([poi2vec.float(), pad], dim=1)
            how = f"zero padding {src_d}->{dst_d}"
        anchor_meta = {"anchor_dim_native": src_d, "anchor_adapted": True,
                       "anchor_dim_used": dst_d, "method": how,
                       "caveat": ("the place-table anchor is a fixed 64-d distillation target in the "
                                  "frozen recipe, so a width arm changes BOTH the encoder width and "
                                  "the anchor's expression; it is not an isolated width contrast")}
        print(f"[{state_lc}/{args.cell}] anchor adapted: {how}", flush=True)
    del_ei, del_ew = load_delaunay_edges(state, d["placeid_to_idx"], num_pois,
                                         poi_to_region=np.asarray(d["poi_to_region"]),
                                         cross_region_weight=1.0, edge_power=1.0)

    data = Data(
        x=torch.tensor(np.asarray(d["node_features"]), dtype=torch.float32),
        edge_index=torch.tensor(np.asarray(d["edge_index"]), dtype=torch.int64),
        edge_weight=torch.tensor(np.asarray(d["edge_weight"]), dtype=torch.float32),
        checkin_to_poi=torch.tensor(np.asarray(d["checkin_to_poi"]), dtype=torch.int64),
        poi_to_region=torch.tensor(np.asarray(d["poi_to_region"]), dtype=torch.int64),
        region_adjacency=torch.tensor(np.asarray(d["region_adjacency"]), dtype=torch.int64),
        region_area=torch.tensor(np.asarray(d["region_area"]), dtype=torch.float32),
        coarse_region_similarity=torch.tensor(np.asarray(d["coarse_region_similarity"]),
                                              dtype=torch.float32),
        num_pois=num_pois, num_regions=num_regions,
    )
    recon_target = _compute_poi_category_aggregate(d, num_pois)
    data.poi_delaunay_edge_index = del_ei
    data.poi_recon_target = recon_target
    data = data.to(device)

    if args.encoder == "resln":
        checkin_encoder = ResidualLNEncoder(in_channels, V14["dim"],
                                           num_layers=V14["num_layers"], dropout=V14["dropout"])
    elif args.encoder == "gat":
        # positive control: attention over the bidirectional user-sequence edges, conditioned on
        # the temporal edge weight. Known to make the next category far easier to recover.
        checkin_encoder = GATTimeEncoder(in_channels, V14["dim"], num_layers=V14["num_layers"],
                                         heads=V14["attention_head"], dropout=0.0,
                                         use_edge_attr=True)
    elif args.encoder == "gcn":
        checkin_encoder = CheckinEncoder(in_channels, V14["dim"], num_layers=V14["num_layers"])
    else:
        raise ValueError(args.encoder)

    model = Check2HGI_DesignK(
        hidden_channels=V14["dim"], checkin_encoder=checkin_encoder,
        checkin2poi=Checkin2POI(V14["dim"], V14["attention_head"]),
        poi2region=POI2Region(V14["dim"], V14["attention_head"]),
        region2city=lambda z, area: torch.sigmoid((z.transpose(0, 1) * area).sum(dim=1)),
        corruption=corruption,
        alpha_c2p=V14["alpha_c2p"], alpha_p2r=V14["alpha_p2r"], alpha_r2c=V14["alpha_r2c"],
        reg_poi_mode="delaunay_gcn", num_pois=num_pois, poi2vec_table=poi2vec,
        gamma_init=V14["gamma_init"], anchor_lambda=V14["anchor_lambda"],
        delaunay_edge_index=del_ei, delaunay_edge_weight=del_ew,
        side_feature_dim=0, side_feature_hidden=16,
        mae_poi_lambda=V14["mae_poi_lambda"], mae_poi_mask_rate=V14["mae_poi_mask_rate"],
        mae_poi_gamma=V14["mae_poi_gamma"], mae_poi_target_dim=int(recon_target.shape[1]),
        mae_poi_aggr="mean", mae_poi_target_kind="category_aggregate", mae_poi_loss_kind="sce",
        hgi_poi_target=None,
    ).to(device)
    n_params = sum(p.numel() for p in model.parameters())
    print(f"[{state_lc}/{args.cell}] params={n_params:,} encoder={args.encoder}", flush=True)

    optimizer = torch.optim.Adam(model.parameters(), lr=V14["lr"],
                                 weight_decay=V14["weight_decay"])
    scheduler = (StepLR(optimizer, step_size=1, gamma=V14["lr_gamma"])
                 if V14["lr_gamma"] != 1.0 else None)

    lowest, best_epoch, best_state = math.inf, 0, None
    t = trange(1, args.epochs + 1, desc=f"{state_lc}/{args.cell}")
    for epoch in t:
        model.train(); optimizer.zero_grad()
        loss = model.loss(*model(data))
        loss.backward()
        clip_grad_norm_(model.parameters(), max_norm=V14["max_norm"])
        optimizer.step()
        if scheduler is not None:
            scheduler.step()
        l = float(loss.item())
        if l < lowest:                              # minimum TRAINING loss, as in the frozen recipe
            lowest, best_epoch = l, epoch
            best_state = {k: v.detach().clone() for k, v in model.state_dict().items()}
        if epoch % 25 == 0 or epoch == args.epochs:
            t.set_postfix(loss=f"{l:.4f}", best_ep=best_epoch, refresh=False); t.refresh()

    print(f"[{state_lc}/{args.cell}] best_epoch={best_epoch} loss={lowest:.4f}", flush=True)
    # NOTE: the line above prints even when epochs=0 (best_epoch=0, loss=inf) -- a log-grep
    # for a clean-looking line would misread an epochs=0 floor-arm build as an ordinary run.
    # Check build.json's "epochs" field / the exit code, not this line, to tell them apart.
    if args.epochs == 0:
        # FLOOR ARM: the architecture at initialization, before any optimizer step. There is no
        # "lowest-loss checkpoint" to select when no step is taken, so this is a DIFFERENT quantity
        # from what epochs>0 produces, not the same procedure with a zero. Stated so nobody later
        # reads the two as one series.
        best_state = {k: v.detach().clone() for k, v in model.state_dict().items()}
    elif best_state is None:
        raise RuntimeError(
            f"{args.epochs} epochs ran and no checkpoint was selected: every training loss was "
            f"non-finite (lowest={lowest}). This previously surfaced as 'load_state_dict got "
            f"NoneType'. Refusing to write an artifact."
        )
    model.load_state_dict(best_state); model.eval()
    with torch.no_grad():
        _ = model(data)
        checkin_emb, poi_emb, region_emb = model.get_embeddings()

    out_dir = REPO / args.study_root / state_lc / args.cell
    out_dir.mkdir(parents=True, exist_ok=True)

    # in-sample export (training users only when restricted) -- the readout for held-out users is
    # produced by infer_checkins.py from the checkpoint below
    md = d["metadata"]
    emb = checkin_emb.numpy()
    # The masked-backward arm appends a category-free TWIN for every check-in as a message source.
    # Twins are not check-ins: there is no metadata row for them and they must never be exported or
    # read out. Keep the first len(md) rows, which are the real nodes in their original order.
    if len(emb) != len(md):
        assert len(emb) == 2 * len(md), (
            f"embedding rows ({len(emb)}) are neither the metadata length ({len(md)}) nor twice it; "
            "the node set was changed in a way this export does not understand")
        emb = emb[:len(md)]
    df = pd.DataFrame(emb, columns=[str(i) for i in range(emb.shape[1])])
    for col in ("datetime", "category", "placeid", "userid"):
        df.insert(0, col, md[col].values)
    df.to_parquet(out_dir / "embeddings_insample.parquet", index=False)

    prov = {
        "study": "check2hgi_integrity_v2",
        "cell": args.cell, "state": state_lc,
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "revision": _revision(), "command": " ".join(sys.argv),
        "recipe": V14, "encoder": args.encoder, "epochs": args.epochs,
        "repr_seed": seed, "device": str(device), "torch_version": torch.__version__,
        "selection": "minimum full-graph training loss (as in the frozen v14 builder)",
        "best_epoch": best_epoch, "best_loss": lowest, "n_params": int(n_params),
        "graph": {"path": str(graph_path.relative_to(REPO)),
                  "sha256_first64MB": _sha256(graph_path), **gstats},
        "training_users": excl_meta,
        "spatial_scaffolding": {
            "delaunay_edges": f"output/hgi/{state_lc}/temp/edges.csv",
            "poi2vec": f"output/hgi/{state_lc}/poi2vec_poi_embeddings_{state.capitalize()}.csv",
            "held_fixed_across_arms": True,
            "scope_note": ("full-dataset place-spatial prior, held fixed on purpose so the "
                           "contrast isolates the check-in channel; recorded as an open channel"),
        },
        "node_feature_schema": {
            "width": in_channels, "layout": "7 category one-hot + hour sin/cos + dow sin/cos",
            "category_vocabulary_source": "configs.globals.CATEGORIES_MAP",
        },
        "exports": {
            "embeddings_insample.parquet": {
                "rows": int(len(df)),
                "sha256": _sha256(out_dir / "embeddings_insample.parquet"),
                "note": "training users only when the cell is restricted",
            }},
    }
    # The training-graph direction must travel with the weights: a checkpoint trained forward-only
    # and read with a bidirectional readout (or the reverse) would be a silent mismatch.
    prov["causal_graph"] = causal_meta
    prov["node_enrichment"] = enrich_meta
    prov["user_fraction"] = frac_meta
    prov["anchor"] = anchor_meta
    prov["capacity"] = {"dim": V14["dim"], "num_layers": V14["num_layers"],
                        "reference_dim": _V14_REF["dim"],
                        "reference_num_layers": _V14_REF["num_layers"],
                        "overridden": bool(args.dim or args.num_layers)}
    if args.save_checkpoint:
        ck_path = out_dir / "checkpoint.pt"
        torch.save({
            "state_dict": {k: v.cpu() for k, v in best_state.items()},
            "checkin_encoder_class": type(checkin_encoder).__name__,
            "checkin_encoder_kwargs": {"in_channels": in_channels, "hidden_channels": V14["dim"],
                                       "num_layers": V14["num_layers"],
                                       "dropout": (V14["dropout"] if args.encoder == "resln" else 0.0),
                                       **({"heads": V14["attention_head"], "use_edge_attr": True}
                                          if args.encoder == "gat" else {})},
            "encoder": args.encoder, "provenance": prov,
            "forward_only": bool(args.forward_only),
        }, ck_path)
        prov["exports"]["checkpoint.pt"] = {"sha256": _sha256(ck_path),
                                            "contains": "selected state_dict + constructor args"}
        print(f"[{state_lc}/{args.cell}] wrote {ck_path}", flush=True)

    (out_dir / "build.json").write_text(json.dumps(prov, indent=2))
    print(f"[{state_lc}/{args.cell}] wrote {out_dir}/build.json", flush=True)
    return prov


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--state", required=True)
    ap.add_argument("--cell", required=True,
                    help="arm label, e.g. U1 (all users), U0 (training users only), P1 (control)")
    ap.add_argument("--repr-seed", type=int, default=42)
    ap.add_argument("--user-fraction", type=float, default=None,
                    help="train the representation on this NESTED fraction of the available users, "
                         "for the data-scaling curve. Applied AFTER --exclude-users-file so the "
                         "evaluation set is identical at every fraction.")
    ap.add_argument("--user-fraction-seed", type=int, default=7)
    ap.add_argument("--dim", type=int, default=None,
                    help="override the V14 output dimension (default 64). The downstream head infers "
                         "its input width from the artifact, so a different dim changes the model the "
                         "dedicated command builds; that is the point of the capacity sweep.")
    ap.add_argument("--num-layers", type=int, default=None,
                    help="override the V14 encoder depth (default 2). Depth sets the receptive field: "
                         "k layers reach index distance k, so this also changes how much of the user's "
                         "path a vector can see.")
    ap.add_argument("--epochs", type=int, default=V14["epochs"])
    ap.add_argument("--device", default="cuda")
    ap.add_argument("--encoder", default="resln", choices=("resln", "gat", "gcn"))
    ap.add_argument("--exclude-users-file", default=None,
                    help="JSON with {'val_users': [...]}; those users are dropped from training")
    ap.add_argument("--study-root", default="results/check2hgi_integrity_v2")
    ap.add_argument("--add-place-identity", action="store_true",
                    help="E1: concatenate the visited place's frozen embedding onto the check-in "
                         "node features. Legitimate: the place of an observed visit is known.")
    ap.add_argument("--add-region-identity", action="store_true",
                    help="E6: add the region embedding of the visit's own region. Legitimate (the "
                         "region of an observed visit is known); coarser than place identity, so it "
                         "also tests whether the shortcut was driven by per-visit uniqueness.")
    ap.add_argument("--place-project-dim", type=int, default=0,
                    help="reduce the place block to this many dimensions via a fixed seeded random "
                         "projection, removing the per-place uniqueness the discriminator exploits "
                         "as a shortcut while keeping coarse neighbourhood structure")
    ap.add_argument("--place-standardize", action="store_true",
                    help="per-column standardize and clip the place block so it does not dominate "
                         "the canonical columns by scale (raw mean|x| is 5.1x, max 12.5 vs 1.0)")
    ap.add_argument("--add-continuous-time", action="store_true",
                    help="E2: add elapsed-time columns (gap to previous visit, time since first "
                         "visit). Legitimate: measured up to the visit itself, never to the target.")
    ap.add_argument("--mask-backward-category", action="store_true",
                    help="OPTION B: keep both edge directions, but make backward messages originate "
                         "from a twin node whose category one-hot is zeroed, so the future reaches "
                         "the past stripped of the answer while keeping its time and place")
    ap.add_argument("--drop-category-features", action="store_true",
                    help="OPTION D: remove the 7 category one-hot columns from every check-in node, "
                         "so the backward edge has no category identity to copy")
    ap.add_argument("--forward-only", action="store_true",
                    help="train on a causal graph: drop the backward direction of every "
                         "consecutive-visit edge, so no visit sees its own future at any point")
    ap.add_argument("--save-checkpoint", action="store_true", default=True)
    args = ap.parse_args()

    frozen = ("check2hgi_design_k_resln_mae_l0_1", "check2hgi_dk_ovl")
    assert not any(f in args.study_root for f in frozen), \
        f"refusing to write into a frozen engine directory: {args.study_root}"
    build(args.state, args)


if __name__ == "__main__":
    main()
