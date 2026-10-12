"""GeoTreeSkipGram — geographically-tree-regularized skip-gram, per-POI 64-d substrate.

⚠ This is NOT POI2Vec (Feng et al., AAAI 2017), despite an earlier mislabel. It is
an honest geo-regularized skip-gram kept as its own baseline. The FAITHFUL AAAI'17
POI2Vec lives in ``scripts/baselines/poi2vec_lib/`` (CBOW + fixed midpoint-grid tree
+ overlap-area phi + user latent). The audit
(docs/studies/closing_data/BASELINES_IMPL_AUDIT.md) found this module diverges from
POI2Vec on its DEFINING mechanism, so it was relabeled (class GeoPOI2Vec→GeoTreeSkipGram).

Method (what this actually is):
  word2vec/skip-gram over POI check-in sequences, with a soft GEOGRAPHICAL
  regularizer injected through a binary tree over a recursive rectangular partition
  of the map (hierarchical-softmax style). Each POI routes to leaf path(s); routing
  probabilities are shared across spatially-near POIs, pulling geographically close
  POIs together. A POI near a split line contributes to both children via a heuristic
  multi-leaf influence weight phi. Output = a per-POI latent table (center embeddings),
  the standalone per-POI 64-d column this baseline emits.

How it DIFFERS from AAAI'17 POI2Vec (i.e. why it is not POI2Vec):
  (1) objective = skip-gram (single center→context pair); the paper is CBOW (sum a
      context window, route the TARGET POI's tree path against it).
  (2) phi = ad-hoc boundary-fraction heuristic; the paper's phi = normalized OVERLAP
      AREA of a POI's theta-buffered box with each leaf rectangle.
  (3) tree = data-dependent median kd-tree; the paper's = FIXED recursive rectangular
      midpoint grid to a theta cell size.
  (4) no user latent; the paper includes a user term in the objective.

Board integration (unchanged): SC-substrate-column — the per-POI table plugs UNDER
the matched champion heads via train.py --engine; downstream is next-category
(macro-F1) + next-region (Acc@10), leak-safe per (state,seed,fold) train-only
pretraining. theta/tree-depth is a configurable hyper-parameter.
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
# Geographical binary tree (the paper's spatial partition + influence weights)
# ----------------------------------------------------------------------------
@dataclass
class GeoTree:
    """A recursive rectangular partition expressed as a binary routing tree.

    Internal nodes split the current bbox along its longer axis at the median
    of the POIs falling inside it. Each internal node owns one routing vector
    (the hierarchical-softmax inner node). Each POI is routed to the leaf(s) it
    falls in; a POI within ``boundary_frac`` of a split line is routed to BOTH
    children (the paper's multi-leaf geographical influence), with influence
    weights phi splitting its gradient mass between the paths.
    """
    n_internal: int
    # For each placeid-index: list of (path_node_ids, path_dirs, phi) tuples.
    # path_node_ids[j] -> internal node id traversed at step j
    # path_dirs[j]     -> +1 (right) / -1 (left) target sign for that node
    # phi              -> influence weight of this path (paths per POI sum to 1)
    poi_paths: List[List[Tuple[np.ndarray, np.ndarray, float]]] = field(default_factory=list)


def build_geo_binary_tree(
    poi_xy: np.ndarray,
    max_depth: int = 12,
    min_leaf: int = 8,
    boundary_frac: float = 0.0,
) -> GeoTree:
    """Build the spatial binary tree over POI coordinates.

    Args:
        poi_xy: [n_poi, 2] (lon, lat) per POI index.
        max_depth: maximum tree depth (paper: tuned per dataset, D3).
        min_leaf: stop splitting when <= this many POIs in a node.
        boundary_frac: if > 0, POIs within this fraction of a node's split span
            of the split line route to BOTH children (multi-leaf influence, D-paper).

    Returns:
        GeoTree with per-POI hierarchical-softmax paths + influence weights.
    """
    n_poi = poi_xy.shape[0]
    # Each POI accumulates a list of partial paths: (node_ids, dirs, phi).
    # Represent a path-in-progress as (list_of_node_ids, list_of_dirs, phi).
    paths_per_poi: List[List[Tuple[List[int], List[int], float]]] = [
        [([], [], 1.0)] for _ in range(n_poi)
    ]
    node_counter = {"n": 0}  # internal node id allocator

    # Work queue: (poi index array, depth). We carry per-(poi,path) bookkeeping
    # by indexing into paths_per_poi[poi][path_slot]; the queue tracks which
    # (poi, path_slot) pairs live in this node.
    # Use a stack of (members, depth) where members = list of (poi, slot).
    root_members = [(p, 0) for p in range(n_poi)]
    stack: List[Tuple[List[Tuple[int, int]], int]] = [(root_members, 0)]

    while stack:
        members, depth = stack.pop()
        if len(members) <= min_leaf or depth >= max_depth:
            continue
        pts = poi_xy[[m[0] for m in members]]
        mins = pts.min(axis=0)
        maxs = pts.max(axis=0)
        span = maxs - mins
        if span.max() <= 0:
            continue
        axis = int(np.argmax(span))
        coords = pts[:, axis]
        split = float(np.median(coords))
        node_id = node_counter["n"]
        node_counter["n"] += 1
        tol = boundary_frac * float(span[axis]) if boundary_frac > 0 else 0.0

        left_members: List[Tuple[int, int]] = []
        right_members: List[Tuple[int, int]] = []
        for (poi, slot), c in zip(members, coords):
            node_ids, dirs, phi = paths_per_poi[poi][slot]
            near_boundary = tol > 0 and abs(c - split) <= tol
            if near_boundary:
                # multi-leaf influence: clone path, send to both children at half phi
                left_path = (node_ids + [node_id], dirs + [-1], phi * 0.5)
                right_path = (node_ids + [node_id], dirs + [+1], phi * 0.5)
                paths_per_poi[poi][slot] = left_path
                paths_per_poi[poi].append(right_path)
                new_slot = len(paths_per_poi[poi]) - 1
                left_members.append((poi, slot))
                right_members.append((poi, new_slot))
            elif c < split:
                paths_per_poi[poi][slot] = (node_ids + [node_id], dirs + [-1], phi)
                left_members.append((poi, slot))
            else:
                paths_per_poi[poi][slot] = (node_ids + [node_id], dirs + [+1], phi)
                right_members.append((poi, slot))
        if left_members:
            stack.append((left_members, depth + 1))
        if right_members:
            stack.append((right_members, depth + 1))

    # Freeze into numpy arrays per POI.
    poi_paths: List[List[Tuple[np.ndarray, np.ndarray, float]]] = []
    for slots in paths_per_poi:
        frozen = []
        for node_ids, dirs, phi in slots:
            if not node_ids:
                continue
            frozen.append((
                np.asarray(node_ids, dtype=np.int64),
                np.asarray(dirs, dtype=np.float32),
                float(phi),
            ))
        if not frozen:
            # POI never split (degenerate): give it an empty path; it will only
            # learn via the center table, no hierarchical-softmax signal.
            frozen = [(np.zeros(0, np.int64), np.zeros(0, np.float32), 1.0)]
        poi_paths.append(frozen)
    return GeoTree(n_internal=node_counter["n"], poi_paths=poi_paths)


# ----------------------------------------------------------------------------
# The skip-gram + geo-hierarchical-softmax model
# ----------------------------------------------------------------------------
class GeoTreeSkipGram(nn.Module):
    """GeoTreeSkipGram: center POI embeddings + geographical-binary-tree hierarchical softmax.

    For a (center_poi, context_poi) skip-gram pair, the probability of the
    context POI is the product of binary routing probabilities along the
    context POI's geographical-tree path, each routing being
    sigmoid(dir * <center_emb, node_vec>). Paths with heuristic influence weight
    phi are summed (a multi-leaf geographical influence). This is a geo-regularized
    softmax that injects spatial structure into the latent space. NOTE: this is a
    skip-gram with a tree regularizer, NOT the faithful AAAI'17 POI2Vec (which is
    CBOW with overlap-area phi + a midpoint grid + a user term — see poi2vec_lib/).

    Exported substrate = ``in_embed.weight`` (per-POI 64-d latent table).
    """

    def __init__(self, n_poi: int, tree: GeoTree, embed_dim: int = 64):
        super().__init__()
        self.n_poi = n_poi
        self.embed_dim = embed_dim
        self.in_embed = nn.Embedding(n_poi, embed_dim)
        # one routing vector per internal tree node (+1 dummy for empty paths)
        self.node_vec = nn.Embedding(max(tree.n_internal, 1), embed_dim)
        nn.init.uniform_(self.in_embed.weight, -0.5 / embed_dim, 0.5 / embed_dim)
        nn.init.zeros_(self.node_vec.weight)
        self.tree = tree

    def build_path_index(self):
        """Precompute, per context POI, a FLAT packed representation of all its
        tree-path (node_id, dir, phi) edges, so a skip-gram batch can be scored
        with a single vectorized scatter instead of a Python per-sample loop.

        Stores, for each POI i:
          self._edge_off[i]      -> start offset into the flat edge arrays
          self._edge_cnt[i]      -> number of edges for POI i
        and the flat arrays (over ALL pois' edges):
          self._edge_node[e], self._edge_dir[e], self._edge_phi[e]
        """
        offs = np.zeros(self.n_poi + 1, dtype=np.int64)
        node_flat: list[int] = []
        dir_flat: list[float] = []
        phi_flat: list[float] = []
        for i, paths in enumerate(self.tree.poi_paths):
            cnt = 0
            for node_ids, dirs, phi in paths:
                if node_ids.size == 0:
                    continue
                for nid, d in zip(node_ids.tolist(), dirs.tolist()):
                    node_flat.append(int(nid))
                    dir_flat.append(float(d))
                    phi_flat.append(float(phi))
                    cnt += 1
            offs[i + 1] = offs[i] + cnt
        dev = self.in_embed.weight.device
        self._edge_off = torch.from_numpy(offs).to(dev)
        self._edge_node = torch.tensor(node_flat or [0], dtype=torch.long, device=dev)
        self._edge_dir = torch.tensor(dir_flat or [0.0], dtype=torch.float32, device=dev)
        self._edge_phi = torch.tensor(phi_flat or [0.0], dtype=torch.float32, device=dev)

    def path_loss(self, center_idx: torch.Tensor, context_idx: torch.Tensor) -> torch.Tensor:
        """Vectorized NLL of context POIs given centers, via the geo tree.

        Gathers each context POI's flat path edges, scores them against the
        paired center embedding, and aggregates log-sigmoid by sample. ~100x
        faster than the per-sample Python loop; numerically identical.
        """
        if not hasattr(self, "_edge_off"):
            self.build_path_index()
        device = self.in_embed.weight.device
        B = center_idx.shape[0]
        center_emb = self.in_embed(center_idx)  # [B, D]

        offs = self._edge_off
        starts = offs[context_idx]              # [B]
        ends = offs[context_idx + 1]            # [B]
        cnts = (ends - starts)                  # [B]
        total_edges = int(cnts.sum().item())
        if total_edges == 0:
            return center_emb.new_zeros(()) + 0.0 * center_emb.sum()

        # Build the flat edge list for this batch + a sample-id per edge.
        # arange within each sample: position = global_pos - starts[sample]
        sample_of_edge = torch.repeat_interleave(torch.arange(B, device=device), cnts)
        # cumulative base per sample
        base = starts[sample_of_edge]                       # [E]
        within = torch.arange(total_edges, device=device) - \
            torch.repeat_interleave(torch.cumsum(cnts, 0) - cnts, cnts)
        edge_pos = base + within                            # [E] index into flat arrays
        nids = self._edge_node[edge_pos]                    # [E]
        dirs = self._edge_dir[edge_pos]                     # [E]
        phis = self._edge_phi[edge_pos]                     # [E]
        nv = self.node_vec(nids)                            # [E, D]
        ce = center_emb[sample_of_edge]                     # [E, D]
        scores = dirs * (nv * ce).sum(dim=1)               # [E]
        logp = F.logsigmoid(scores) * phis                 # [E] (weighted by influence)
        # sum per sample -> NLL = -sum; mean over batch
        per_sample = torch.zeros(B, device=device).scatter_add_(0, sample_of_edge, logp)
        return (-per_sample).mean()

    @torch.no_grad()
    def export_table(self) -> np.ndarray:
        return self.in_embed.weight.detach().cpu().numpy().astype(np.float32)
