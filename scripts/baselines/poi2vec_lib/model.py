"""Faithful POI2Vec (Feng et al., "POI2Vec: Geographical Latent Representation for
Predicting Future Visitors", AAAI 2017; reference impl github.com/yongqyu/POI2Vec).

This is the FAITHFUL AAAI'17 POI2Vec, built as a class-(A) SC-substrate-column
baseline: it emits a per-POI 64-d table that plugs UNDER the matched champion heads
via train.py --engine. It is NOT the geotree_skipgram baseline (which gets all four
of POI2Vec's defining mechanisms wrong). The four things implemented RIGHT here:

  1. FIXED recursive rectangular MIDPOINT tree over the state bbox. Each node's
     rectangle is split at its GEOMETRIC midpoint, ALTERNATING the split axis by
     depth parity (lon at even depth, lat at odd depth), recursing until the cell
     size <= theta degrees on BOTH axes. Breadth-first node numbering. This geometry
     is DATA-INDEPENDENT (depends only on bbox + theta) -> build once, fold-independent,
     leak-safe (coords are not labels). See ``MidpointGeoTree``.

  2. OVERLAP-AREA phi. Each POI gets a theta-sized axis-aligned box around its
     (lon,lat); we intersect that box with every LEAF rectangle it overlaps and set
     phi_leaf = intersection_area / sum_of_intersection_areas (so sum(phi)=1 per POI).
     Capped to the top ``route_count`` leaves (renormalized). A POI fully inside one
     leaf gets phi=[1.0]. See ``build_poi_routes``.

  3. CBOW forward + hierarchical softmax + USER term. Per training example: take a
     CONTEXT WINDOW of POIs, SUM their input (context) embeddings + the user vector,
     and route the TARGET POI's tree path(s) against that summed vector. Path prob =
     product over the target POI's tree-path edges of sigmoid(dir * <ctx_sum, node_vec>);
     because the target routes to MULTIPLE leaves, per-leaf path probs are combined
     weighted by phi. The user term is negative-sampled (NOT full O(n_poi) softmax —
     the A40 OOMs on big states). See ``POI2VecAAAI.forward_nll``.

  4. Tables: poi_embed[n_poi,64] (input/context embeddings -- THIS is the exported
     substrate), user_embed[n_user,64], node_vec[n_internal,64] routing vectors.
     EXPORT ONLY poi_embed (``export_table``).

DIM = 64 is MATCHED to the board (the paper uses 200-d; matching to 64 keeps the
substrate-axis comparison clean — documented as an intentional matched-protocol
deviation in README_poi2vec.md).

Loss form (DOCUMENTED, see README_poi2vec.md §loss):
  The paper's per-example probability is the multi-leaf combination
    pr = 1 - prod_leaf (1 - pr_user * pr_path_leaf)        (paper Eq. for routing to
                                                            multiple leaves)
  We use the NUMERICALLY-STABLE NLL surrogate
    nll = -log( sum_leaf  phi_leaf * pr_user * pr_path_leaf + eps )
  This is the phi-weighted-mixture form (a valid lower-variance surrogate of the
  paper's noisy-OR; the noisy-OR can underflow to log(0) when all leaf probs are
  small early in training). The deviation is documented explicitly. We ALSO expose
  the paper's exact noisy-OR (``loss_form="noisy_or"``) for audit; the default is the
  stable mixture (``loss_form="mixture"``). The user softmax is approximated by
  negative sampling (binary log-sigmoid on the true user + k sampled users), the
  reference impl's approach for tractable large n_user.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Dict, List, Tuple

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F


# ----------------------------------------------------------------------------
# (1) FIXED recursive rectangular midpoint tree  +  (2) overlap-area phi
# ----------------------------------------------------------------------------
@dataclass
class MidpointGeoTree:
    """A FIXED recursive rectangular midpoint partition of the state bbox.

    DATA-INDEPENDENT geometry: each internal node owns a rectangle [lon0,lat0,lon1,lat1];
    it is split at its geometric midpoint along an axis chosen by depth parity
    (even depth -> split longitude, odd depth -> split latitude). Recursion stops when
    BOTH side lengths are <= theta (degrees). Internal nodes are numbered breadth-first.

    Attributes:
        theta:        target leaf cell size (degrees).
        bbox:         (lon0, lat0, lon1, lat1) of the whole state.
        n_internal:   number of internal (routing) nodes.
        n_leaf:       number of leaves.
        leaf_rects:   [n_leaf,4] (lon0,lat0,lon1,lat1) per leaf.
        leaf_path_nodes: List[np.ndarray] per leaf -> internal node ids on the
                      root->leaf path.
        leaf_path_dirs:  List[np.ndarray] per leaf -> +1 (right/high) / -1 (left/low)
                      at each internal node on the path.
    """
    theta: float
    bbox: Tuple[float, float, float, float]
    n_internal: int
    n_leaf: int
    leaf_rects: np.ndarray
    leaf_path_nodes: List[np.ndarray] = field(default_factory=list)
    leaf_path_dirs: List[np.ndarray] = field(default_factory=list)


def build_midpoint_tree(bbox: Tuple[float, float, float, float],
                        theta: float = 0.05,
                        max_depth: int = 40,
                        even_axis: int = 0) -> MidpointGeoTree:
    """Build the FIXED recursive rectangular midpoint tree (POI2Vec mechanism #1).

    Args:
        bbox: (lon_min, lat_min, lon_max, lat_max) over ALL POI coords for the state.
        theta: leaf cell size (degrees). Recursion stops when both side lengths <= theta.
        max_depth: hard safety cap on depth.
        even_axis: which axis is split at EVEN depth (0=lon, 1=lat); odd depth uses the
            other. Default lon@even, lat@odd.

    Breadth-first construction: we expand level by level so internal node ids are
    assigned in BFS order. A node that needs no further split (both sides <= theta)
    becomes a leaf. Returns a MidpointGeoTree.
    """
    lon0, lat0, lon1, lat1 = (float(bbox[0]), float(bbox[1]),
                              float(bbox[2]), float(bbox[3]))
    # Guard against degenerate bbox (single point / zero span on an axis).
    eps = 1e-9
    if lon1 - lon0 < eps:
        lon1 = lon0 + max(theta, eps)
    if lat1 - lat0 < eps:
        lat1 = lat0 + max(theta, eps)

    # BFS queue of (rect, depth, path_nodes, path_dirs). We allocate internal-node ids
    # in pop order (BFS) and collect leaves.
    from collections import deque

    leaf_rects: List[Tuple[float, float, float, float]] = []
    leaf_path_nodes: List[List[int]] = []
    leaf_path_dirs: List[List[int]] = []
    next_internal_id = 0

    def is_leaf(rect):
        w = rect[2] - rect[0]
        h = rect[3] - rect[1]
        return (w <= theta + 1e-12) and (h <= theta + 1e-12)

    q = deque()
    q.append(((lon0, lat0, lon1, lat1), 0, [], []))
    while q:
        rect, depth, pnodes, pdirs = q.popleft()
        if is_leaf(rect) or depth >= max_depth:
            leaf_rects.append(rect)
            leaf_path_nodes.append(list(pnodes))
            leaf_path_dirs.append(list(pdirs))
            continue
        # split at geometric midpoint, axis by depth parity
        axis = even_axis if (depth % 2 == 0) else (1 - even_axis)
        nid = next_internal_id
        next_internal_id += 1
        if axis == 0:  # split longitude
            mid = 0.5 * (rect[0] + rect[2])
            left = (rect[0], rect[1], mid, rect[3])    # low  lon  -> dir -1
            right = (mid, rect[1], rect[2], rect[3])   # high lon  -> dir +1
        else:          # split latitude
            mid = 0.5 * (rect[1] + rect[3])
            left = (rect[0], rect[1], rect[2], mid)    # low  lat  -> dir -1
            right = (rect[0], mid, rect[2], rect[3])   # high lat  -> dir +1
        q.append((left, depth + 1, pnodes + [nid], pdirs + [-1]))
        q.append((right, depth + 1, pnodes + [nid], pdirs + [+1]))

    leaf_rects_arr = np.asarray(leaf_rects, dtype=np.float64)
    return MidpointGeoTree(
        theta=theta,
        bbox=(lon0, lat0, lon1, lat1),
        n_internal=next_internal_id,
        n_leaf=len(leaf_rects),
        leaf_rects=leaf_rects_arr,
        leaf_path_nodes=[np.asarray(p, dtype=np.int64) for p in leaf_path_nodes],
        leaf_path_dirs=[np.asarray(d, dtype=np.float32) for d in leaf_path_dirs],
    )


def _rect_overlap_area(box, rect) -> float:
    """Axis-aligned intersection area of two rects (lon0,lat0,lon1,lat1)."""
    ox0 = max(box[0], rect[0])
    oy0 = max(box[1], rect[1])
    ox1 = min(box[2], rect[2])
    oy1 = min(box[3], rect[3])
    w = ox1 - ox0
    h = oy1 - oy0
    if w <= 0.0 or h <= 0.0:
        return 0.0
    return float(w * h)


def build_poi_routes(poi_xy: np.ndarray,
                     tree: MidpointGeoTree,
                     theta: float,
                     route_count: int = 4) -> List[Tuple[np.ndarray, np.ndarray]]:
    """Compute per-POI (leaf_ids, phi) via OVERLAP AREA (POI2Vec mechanism #2).

    Each POI gets a theta-SIDED axis-aligned box centered at (lon,lat) (half-width
    theta/2 on each side). We intersect that box with each LEAF rectangle and set
    phi_leaf = intersection_area / sum_of_intersection_areas, capped to the top
    ``route_count`` leaves (renormalized so sum(phi)=1). A POI fully inside one leaf
    gets phi=[1.0] on that leaf.

    Returns: per-POI list of (leaf_ids: int64[k], phi: float32[k]) with sum(phi)=1
    and k <= route_count. POIs with no overlap (NaN/out-of-bbox coords) get the single
    nearest leaf by center distance with phi=[1.0] (degenerate fallback, documented).
    """
    n_poi = poi_xy.shape[0]
    rects = tree.leaf_rects                       # [n_leaf,4]
    leaf_cx = 0.5 * (rects[:, 0] + rects[:, 2])
    leaf_cy = 0.5 * (rects[:, 1] + rects[:, 3])
    half = 0.5 * float(theta)
    routes: List[Tuple[np.ndarray, np.ndarray]] = []
    for i in range(n_poi):
        lon, lat = float(poi_xy[i, 0]), float(poi_xy[i, 1])
        if not (math.isfinite(lon) and math.isfinite(lat)):
            # degenerate: nearest leaf center
            j = int(np.argmin((leaf_cx - 0.0) ** 2 + (leaf_cy - 0.0) ** 2))
            routes.append((np.asarray([j], np.int64), np.asarray([1.0], np.float32)))
            continue
        # Vectorized rect-overlap area over ALL leaves at once. The previous pure-Python
        # `for j in range(n_leaf): areas[j] = _rect_overlap_area(box, rects[j])` was
        # O(n_poi * n_leaf) ~ 11B scalar calls (~3 h/cell) at large-state scale
        # (CA: 169,145 POIs x 65,536 leaves). This numpy form is BIT-IDENTICAL to the
        # scalar _rect_overlap_area (same float64 max/min/sub/mul; np.where reproduces
        # the w<=0|h<=0 -> 0.0 guard). Verified leaf_ids + phi byte-exact across
        # overlap / no-overlap / on-edge / NaN / out-of-bbox / tie cases.
        b0, b1, b2, b3 = lon - half, lat - half, lon + half, lat + half
        w = np.minimum(b2, rects[:, 2]) - np.maximum(b0, rects[:, 0])
        h = np.minimum(b3, rects[:, 3]) - np.maximum(b1, rects[:, 1])
        areas = np.where((w > 0.0) & (h > 0.0), w * h, 0.0)
        total = areas.sum()
        if total <= 0.0:
            # POI outside every leaf (out of bbox) -> nearest leaf center, phi=1
            j = int(np.argmin((leaf_cx - lon) ** 2 + (leaf_cy - lat) ** 2))
            routes.append((np.asarray([j], np.int64), np.asarray([1.0], np.float32)))
            continue
        # top route_count leaves by overlap area
        nz = np.nonzero(areas > 0.0)[0]
        if len(nz) > route_count:
            order = nz[np.argsort(-areas[nz])][:route_count]
        else:
            order = nz[np.argsort(-areas[nz])]
        phi = areas[order]
        phi = phi / phi.sum()                     # renormalize after capping
        routes.append((order.astype(np.int64), phi.astype(np.float32)))
    return routes


# ----------------------------------------------------------------------------
# (3) + (4) CBOW + hierarchical softmax + negative-sampled user term
# ----------------------------------------------------------------------------
class POI2VecAAAI(nn.Module):
    """Faithful AAAI'17 POI2Vec.

    Tables:
      poi_embed [n_poi, D]   -- input/context embeddings; THIS is the exported substrate.
      user_embed[n_user, D]  -- per-user latent (paper's pr_user factor).
      node_vec  [n_internal, D] -- hierarchical-softmax routing vectors.

    Forward (per example): SUM context-POI ``poi_embed`` over the window (+ user vector),
    route the TARGET POI's tree path(s) against that summed vector, combine per-leaf
    path probs by phi. pr_path_leaf = prod_edge sigmoid(dir * <ctx_sum, node_vec>).
    The user term is negative-sampled (binary objective on the true user + k sampled).

    Exports only ``poi_embed`` (``export_table``).
    """

    def __init__(self, n_poi: int, n_user: int, tree: MidpointGeoTree,
                 routes: List[Tuple[np.ndarray, np.ndarray]],
                 embed_dim: int = 64, route_count: int = 4,
                 n_neg_user: int = 5, loss_form: str = "mixture"):
        super().__init__()
        assert loss_form in ("mixture", "noisy_or"), loss_form
        self.n_poi = n_poi
        self.n_user = max(int(n_user), 1)
        self.embed_dim = embed_dim
        self.route_count = route_count
        self.n_neg_user = n_neg_user
        self.loss_form = loss_form
        self.tree = tree

        self.poi_embed = nn.Embedding(n_poi, embed_dim)
        self.user_embed = nn.Embedding(self.n_user, embed_dim)
        self.node_vec = nn.Embedding(max(tree.n_internal, 1), embed_dim)
        nn.init.uniform_(self.poi_embed.weight, -0.5 / embed_dim, 0.5 / embed_dim)
        nn.init.uniform_(self.user_embed.weight, -0.5 / embed_dim, 0.5 / embed_dim)
        nn.init.zeros_(self.node_vec.weight)

        # Precompute a FLAT packed edge list per POI: concatenation over the POI's
        # routed leaves of (node_id, dir, leaf_phi). For a target POI we score every
        # edge against the context sum, log-sigmoid, then aggregate per-leaf
        # (product over the leaf path) weighted by phi. We pack:
        #   _poi_edge_off[i] : start offset into flat edge arrays for POI i
        #   _poi_edge_cnt[i] : number of edges for POI i
        # flat arrays over all POIs:
        #   _edge_node[e], _edge_dir[e], _edge_leafslot[e] (local leaf index within POI),
        #   _edge_phi[e] (phi of the leaf this edge belongs to)
        # plus per-POI leaf count (_poi_nleaf[i]) for the per-leaf reduction.
        self._build_edge_index(routes)

    def _build_edge_index(self, routes):
        offs = [0]
        node_flat: List[int] = []
        dir_flat: List[float] = []
        leafslot_flat: List[int] = []     # local leaf index 0..k-1 within this POI
        phi_flat: List[float] = []        # phi of the leaf each edge belongs to
        nleaf_per_poi: List[int] = []
        leaf_base = [0]                   # cumulative leaf count -> global leaf slot base
        for i in range(self.n_poi):
            leaf_ids, phi = routes[i]
            cnt = 0
            for li in range(len(leaf_ids)):
                lid = int(leaf_ids[li])
                pnodes = self.tree.leaf_path_nodes[lid]
                pdirs = self.tree.leaf_path_dirs[lid]
                for nid, d in zip(pnodes.tolist(), pdirs.tolist()):
                    node_flat.append(int(nid))
                    dir_flat.append(float(d))
                    leafslot_flat.append(li)
                    phi_flat.append(float(phi[li]))
                    cnt += 1
            offs.append(offs[-1] + cnt)
            nleaf_per_poi.append(len(leaf_ids))
            leaf_base.append(leaf_base[-1] + len(leaf_ids))
        self.register_buffer("_poi_edge_off",
                             torch.tensor(offs, dtype=torch.long), persistent=False)
        self.register_buffer("_edge_node",
                             torch.tensor(node_flat or [0], dtype=torch.long), persistent=False)
        self.register_buffer("_edge_dir",
                             torch.tensor(dir_flat or [0.0], dtype=torch.float32), persistent=False)
        self.register_buffer("_edge_leafslot",
                             torch.tensor(leafslot_flat or [0], dtype=torch.long), persistent=False)
        self.register_buffer("_edge_phi",
                             torch.tensor(phi_flat or [0.0], dtype=torch.float32), persistent=False)
        self.register_buffer("_poi_nleaf",
                             torch.tensor(nleaf_per_poi or [0], dtype=torch.long), persistent=False)
        self.register_buffer("_poi_leaf_base",
                             torch.tensor(leaf_base, dtype=torch.long), persistent=False)

    def context_sum(self, context_idx: torch.Tensor, context_mask: torch.Tensor,
                    user_idx: torch.Tensor) -> torch.Tensor:
        """SUM the context POIs' input embeddings over the window + the user vector.

        Args:
            context_idx: [B, W] padded POI indices (pad = any value; masked out).
            context_mask: [B, W] bool, True where a real context POI.
            user_idx: [B] user indices.
        Returns: [B, D] context sum (+ user vector).
        """
        ce = self.poi_embed(context_idx.clamp(min=0))         # [B,W,D]
        m = context_mask.unsqueeze(-1).to(ce.dtype)           # [B,W,1]
        ctx = (ce * m).sum(dim=1)                             # [B,D]
        ctx = ctx + self.user_embed(user_idx)                 # + user term
        return ctx

    def forward_nll(self, context_idx, context_mask, target_idx, user_idx) -> torch.Tensor:
        """Per-batch mean NLL of the target POIs under CBOW + hierarchical softmax
        with overlap-area phi, plus the negative-sampled user term.

        Returns scalar loss (mean over batch).
        """
        device = self.poi_embed.weight.device
        B = target_idx.shape[0]
        ctx = self.context_sum(context_idx, context_mask, user_idx)   # [B,D]

        # ---- gather the target POIs' flat edges ----
        offs = self._poi_edge_off
        starts = offs[target_idx]                 # [B]
        ends = offs[target_idx + 1]               # [B]
        cnts = ends - starts                      # [B] edges per sample
        total_edges = int(cnts.sum().item())
        # leaf bookkeeping
        nleaf = self._poi_nleaf[target_idx]       # [B] leaves per sample

        if total_edges == 0:
            path_nll = ctx.new_zeros(B)
        else:
            sample_of_edge = torch.repeat_interleave(torch.arange(B, device=device), cnts)  # [E]
            base = starts[sample_of_edge]                                                    # [E]
            within = torch.arange(total_edges, device=device) - \
                torch.repeat_interleave(torch.cumsum(cnts, 0) - cnts, cnts)
            epos = base + within                       # [E] index into flat edge arrays
            nids = self._edge_node[epos]               # [E]
            dirs = self._edge_dir[epos]                # [E]
            phis = self._edge_phi[epos]                # [E] (leaf phi, repeated per edge)
            lslot = self._edge_leafslot[epos]          # [E] local leaf id within sample

            nv = self.node_vec(nids)                   # [E,D]
            ce = ctx[sample_of_edge]                   # [E,D]
            scores = dirs * (nv * ce).sum(dim=1)       # [E]
            logsig = F.logsigmoid(scores)              # [E] = log sigmoid(dir<ctx,node>)

            # Aggregate to a per-(sample,leaf) log-path-prob: sum logsig over the
            # leaf's path edges. Global leaf slot = leaf_base[sample] + lslot.
            total_leaves = int(nleaf.sum().item())
            # Build a contiguous global leaf index over THIS batch.
            #   batch_leaf_base[b] = cumulative leaves before sample b
            batch_leaf_base = torch.cumsum(nleaf, 0) - nleaf          # [B]
            global_leaf = batch_leaf_base[sample_of_edge] + lslot     # [E] in [0,total_leaves)

            log_path = torch.zeros(total_leaves, device=device).scatter_add_(
                0, global_leaf, logsig)                               # [L] log prod sigmoid
            # phi per leaf (take first edge's phi per leaf; phi is constant within a leaf)
            leaf_phi = torch.zeros(total_leaves, device=device)
            leaf_phi.scatter_(0, global_leaf, phis)                   # overwrite -> leaf phi
            # sample id per leaf
            leaf_sample = torch.repeat_interleave(torch.arange(B, device=device), nleaf)  # [L]

            # path prob per leaf
            pr_path = torch.exp(log_path).clamp(min=1e-12, max=1.0)   # [L]

            # [MF1] Geographical path probability ONLY (pure hierarchical softmax over
            # the target's tree leaves, area-phi weighted). The user factor enters EXACTLY
            # ONCE, via the negative-sampled term below — NOT also as a path gate. Since
            # pr_user is per-SAMPLE (user-level), -log(pr_path) - log(pr_user) =
            # -log(pr_path * pr_user) reproduces the paper's MULTIPLICATIVE pr = pr_user *
            # pr_path with a single user factor (the earlier build double-counted it as
            # pr_user^2: a per-leaf gate AND the separate term).
            if self.loss_form == "noisy_or":
                # 1 - prod_leaf (1 - pr_path_leaf)  (multi-leaf combination)
                one_minus = (1.0 - pr_path.clamp(0.0, 1.0 - 1e-7))
                log_one_minus = torch.log(one_minus.clamp(min=1e-12))
                sum_log = torch.zeros(B, device=device).scatter_add_(0, leaf_sample, log_one_minus)
                pr = (1.0 - torch.exp(sum_log)).clamp(min=1e-12, max=1.0)   # [B]
                path_nll = -torch.log(pr)
            else:
                # stable mixture: nll = -log( sum_leaf phi * pr_path + eps )
                contrib = leaf_phi * pr_path                               # [L]
                mix = torch.zeros(B, device=device).scatter_add_(0, leaf_sample, contrib)  # [B]
                path_nll = -torch.log(mix.clamp(min=1e-12))

        # ---- user factor: negative-sampled binary objective (the SOLE user term) ----
        # Positive: log sigmoid(<ctx, user_true>). Negatives: k random users,
        # log sigmoid(-<ctx, user_neg>). word2vec NEG approximation of the paper's pr_user
        # softmax (tractable; avoids O(n_poi)). [MF1] This is now the ONLY place the user
        # factor enters; combined with path_nll it yields pr = pr_path * pr_user.
        pos = F.logsigmoid((ctx * self.user_embed(user_idx)).sum(dim=1))   # [B]
        if self.n_neg_user > 0 and self.n_user > 1:
            neg_idx = torch.randint(0, self.n_user, (B, self.n_neg_user), device=device)
            neg_emb = self.user_embed(neg_idx)                              # [B,k,D]
            neg_score = (neg_emb * ctx.unsqueeze(1)).sum(dim=2)             # [B,k]
            neg = F.logsigmoid(-neg_score).sum(dim=1)                       # [B]
        else:
            neg = pos.new_zeros(B)
        user_nll = -(pos + neg)

        return (path_nll + user_nll).mean()

    @torch.no_grad()
    def export_table(self) -> np.ndarray:
        """EXPORT ONLY poi_embed (the per-POI input/context substrate)."""
        return self.poi_embed.weight.detach().cpu().numpy().astype(np.float32)
