"""Check2HGI preprocessing module for creating check-in graph structures."""

import argparse
import pickle as pkl
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd
from shapely import wkt
from sklearn.preprocessing import LabelEncoder

from configs.paths import IoPaths, Resources


class Check2HGIPreprocess:
    """Preprocessing pipeline for Check2HGI embeddings."""

    def __init__(self, checkins_file, boroughs_file, temp_path, edge_type='user_sequence',
                 temporal_decay=3600.0, build_poi_delaunay: bool = False,
                 build_poi_aggregates: bool = False,
                 build_covisit_pairs: bool = False, covisit_k: int = 3,
                 covisit_dedup: bool = True,
                 c3_alpha_delaunay: float = 1.0, c3_w_r: float = 1.0):
        """
        Initialize preprocessor.

        Args:
            checkins_file: Path to check-in parquet file
            boroughs_file: Path to boroughs/regions CSV file
            temp_path: Path to save intermediate files
            edge_type: Type of edges ('user_sequence', 'same_poi', 'both')
            temporal_decay: Decay parameter for temporal edge weights (seconds)
            build_poi_delaunay: T5.2a / T5.2b — when True, also build a
                POI-level Delaunay triangulation and cache its undirected
                edge list under data dict key ``poi_delaunay_edge_index``.
                Shared between T5.2a (Node2Vec walks over POI graph) and
                T5.2b (masked-POI decoder neighbour aggregation). Default
                False reproduces canonical preprocess exactly.
            build_poi_aggregates: T5.2b — when True, also compute per-POI
                feature aggregates (mean category one-hot of constituent
                check-ins + log visit count). Cached under
                ``poi_category_aggregate`` (P, num_categories) and
                ``poi_visit_count_log`` (P,). These are the reconstruction
                targets for the masked-POI decoder.

                Leak note: both aggregates are derivable from the encoder's
                INPUT features (check-in category one-hot already lives in
                ``data.x``). Reconstructing them adds STRUCTURE (the
                decoder must predict from POI Delaunay neighbours) but no
                NEW information. This is GraphMAE-spirit, leak-safe by
                construction. The user-held-out IJM probe is the
                empirical guardrail. Default False reproduces canonical.
        """
        self.checkins_file = checkins_file
        self.boroughs_file = boroughs_file
        self.temp_path = Path(temp_path)
        self.edge_type = edge_type
        self.temporal_decay = temporal_decay
        self.build_poi_delaunay = bool(build_poi_delaunay)
        self.build_poi_aggregates = bool(build_poi_aggregates)
        # T6.1 — co-visit POI-POI pair index. When True, enumerate unique
        # unordered (poi_a, poi_b) pairs that co-visit within ``covisit_k``
        # consecutive check-ins by the same user (POI_a ≠ POI_b). Cached on
        # the dict as ``covisit_pairs`` ([N_pairs, 2] int64). Cost is
        # O(N_checkins × k) at preprocess time; trivial compared to graph
        # build. Default False keeps canonical preprocess bit-identical.
        self.build_covisit_pairs = bool(build_covisit_pairs)
        self.covisit_k = int(covisit_k)
        if self.covisit_k < 2:
            raise ValueError(f"covisit_k must be >= 2 (got {self.covisit_k})")
        # T6.1 implementation-robustness option (advisor 2026-05-19): keep
        # multiplicity in the co-visit pair table. Default True (dedup) matches
        # the original T6.1 sweep. False emits one row per raw co-visit
        # adjacency — hub POIs naturally get over-sampled when the trainer
        # samples B pairs uniformly each step (weighted-by-multiplicity).
        self.covisit_dedup = bool(covisit_dedup)
        # T6.2 — composite C3 edge-weight multipliers. Defaults (1.0, 1.0)
        # are no-ops; the existing temporal-decay user_sequence edges are
        # returned unchanged. When either is ≠ 1.0, the user-sequence
        # edges are re-weighted:
        #   edge_weight(A→B) *= α_delaunay if POI(A) and POI(B) are
        #     Delaunay-adjacent (per the POI-level Delaunay graph from
        #     ``_build_poi_delaunay_edges``); else *= 1.
        #   edge_weight(A→B) *= w_r if region(A) ≠ region(B); else *= 1.
        # Tests the user's C3 hypothesis (HGI-style spatial geometry as
        # edge-weights on the check-in graph). Requires build_poi_delaunay
        # to be True (auto-enabled in the caller when c3 multipliers ≠ 1).
        self.c3_alpha_delaunay = float(c3_alpha_delaunay)
        self.c3_w_r = float(c3_w_r)

    def _load_checkins(self):
        """Load and prepare check-in data."""
        print("Loading check-in data...")
        self.checkins = pd.read_parquet(self.checkins_file)

        # Ensure required columns exist
        required = ['userid', 'placeid', 'datetime', 'category', 'latitude', 'longitude']
        missing = [c for c in required if c not in self.checkins.columns]
        if missing:
            raise ValueError(f"Missing required columns: {missing}")

        # Sort by user and time (essential for user_sequence edges)
        self.checkins = self.checkins.sort_values(['userid', 'datetime']).reset_index(drop=True)

        # Encode categories
        self.le_category = LabelEncoder()
        self.checkins['category_encoded'] = self.le_category.fit_transform(
            self.checkins['category'].fillna('Unknown')
        )

        # Create geometry for spatial join
        self.checkins['geometry'] = self.checkins.apply(
            lambda row: f"POINT({row['longitude']} {row['latitude']})"
            if pd.notnull(row['longitude']) and pd.notnull(row['latitude'])
            else None,
            axis=1
        )

        print(f"Loaded {len(self.checkins)} check-ins, {self.checkins['placeid'].nunique()} POIs")

    def _load_boroughs(self):
        """Load boroughs/regions data."""
        print("Loading boroughs data...")
        self.boroughs = pd.read_csv(self.boroughs_file)
        self.boroughs['geometry'] = self.boroughs['geometry'].apply(wkt.loads)
        self.boroughs = gpd.GeoDataFrame(self.boroughs, geometry='geometry', crs='EPSG:4326')

    def _assign_regions(self):
        """Assign each check-in and POI to a region via spatial join."""
        print("Assigning regions...")

        # Create unique POI dataframe with representative coordinates
        pois = self.checkins.groupby('placeid').agg({
            'latitude': 'first',
            'longitude': 'first',
            'category_encoded': 'first',
            'geometry': 'first'
        }).reset_index()

        # Convert to GeoDataFrame
        pois['geometry'] = pois['geometry'].apply(wkt.loads)
        pois = gpd.GeoDataFrame(pois, geometry='geometry', crs='EPSG:4326')

        # Spatial join with boroughs
        pois = pois.sjoin(self.boroughs, how='left', predicate='intersects')

        # Handle POIs outside any region (assign to nearest or drop)
        pois = pois.dropna(subset=['GEOID'])

        # Create POI to region mapping
        unique_regions = pois['GEOID'].unique()
        self.region_to_idx = {r: i for i, r in enumerate(unique_regions)}
        pois['region_idx'] = pois['GEOID'].map(self.region_to_idx)

        # Store POI info
        self.pois = pois
        self.num_regions = len(unique_regions)

        # Create placeid to POI index mapping
        valid_placeids = set(pois['placeid'].tolist())
        self.placeid_to_idx = {pid: i for i, pid in enumerate(pois['placeid'].tolist())}

        # Filter check-ins to only those with valid POIs
        self.checkins = self.checkins[self.checkins['placeid'].isin(valid_placeids)].reset_index(drop=True)

        # Map check-ins to POI indices
        self.checkins['poi_idx'] = self.checkins['placeid'].map(self.placeid_to_idx)

        print(f"Assigned to {self.num_regions} regions, {len(self.pois)} POIs")

    def _build_user_sequence_edges(self):
        """Build edges connecting consecutive check-ins by the same user."""
        print("Building user sequence edges...")

        edges = []
        weights = []

        # Group by user and iterate
        for userid, group in self.checkins.groupby('userid'):
            if len(group) < 2:
                continue

            indices = group.index.tolist()
            times = group['datetime'].tolist()

            for i in range(len(indices) - 1):
                src = indices[i]
                tgt = indices[i + 1]

                # Compute temporal weight (exponential decay)
                time_gap = (times[i + 1] - times[i]).total_seconds()
                weight = np.exp(-time_gap / self.temporal_decay)

                # Bidirectional edges
                edges.append([src, tgt])
                edges.append([tgt, src])
                weights.append(weight)
                weights.append(weight)

        if edges:
            edge_index = np.array(edges).T
            edge_weight = np.array(weights)
        else:
            edge_index = np.zeros((2, 0), dtype=np.int64)
            edge_weight = np.zeros(0, dtype=np.float32)

        print(f"Built {len(weights)} user sequence edges")
        return edge_index, edge_weight

    def _build_same_poi_edges(self, max_edges_per_poi=50):
        """Build edges connecting check-ins at the same POI."""
        print("Building same-POI edges...")

        edges = []
        weights = []

        # Group by POI
        for placeid, group in self.checkins.groupby('placeid'):
            if len(group) < 2:
                continue

            indices = group.index.tolist()

            # Limit edges per POI to avoid explosion
            if len(indices) > max_edges_per_poi:
                # Sample subset
                sampled = np.random.choice(indices, max_edges_per_poi, replace=False).tolist()
            else:
                sampled = indices

            # Connect all pairs in sample
            for i, src in enumerate(sampled):
                for tgt in sampled[i + 1:]:
                    edges.append([src, tgt])
                    edges.append([tgt, src])
                    weights.append(1.0)
                    weights.append(1.0)

        if edges:
            edge_index = np.array(edges).T
            edge_weight = np.array(weights)
        else:
            edge_index = np.zeros((2, 0), dtype=np.int64)
            edge_weight = np.zeros(0, dtype=np.float32)

        print(f"Built {len(weights)} same-POI edges")
        return edge_index, edge_weight

    def _build_delaunay_lifted_edges(self, k_per_neighbor: int = 5):
        """T4.4 — Lift POI-level Delaunay edges to check-in level.

        Build POI-POI edges from a Delaunay triangulation over POI lat/lon,
        then expand to check-in pairs: for each Delaunay (poi_a, poi_b)
        pair, connect up to ``k_per_neighbor`` representative check-ins at
        poi_a to up to ``k_per_neighbor`` at poi_b (bidirectional).

        Each check-in ends up with at most ~K × N_delaunay_neighbours (~5 × 7
        = 35) spatial-edge neighbours — well under the 50-cap from spec.

        Uniform edge weights (1.0) — no R-GCN dependency, no edge_attr leak
        surface (T3.3 lesson). The spatial topology is the signal; the encoder
        sees these as just-another-GCN-edge alongside user_sequence.
        """
        import scipy.spatial
        from itertools import combinations as _combinations
        print(f"Building Delaunay-lifted spatial edges (k_per_neighbor={k_per_neighbor})...")

        # 1. POI lat/lon → Delaunay triangulation.
        poi_coords = np.array(
            self.pois.geometry.apply(lambda x: [x.x, x.y]).tolist(), dtype=np.float64
        )
        if len(poi_coords) < 3:
            print("[T4.4] fewer than 3 POIs; no Delaunay possible")
            return np.zeros((2, 0), dtype=np.int64), np.zeros(0, dtype=np.float32)
        triangles = scipy.spatial.Delaunay(
            poi_coords, qhull_options="QJ QbB Pp"
        ).simplices

        # 2. Dedup Delaunay POI-pairs.
        poi_pairs = set()
        for tri in triangles:
            for a, b in _combinations(tri.tolist(), 2):
                if a == b:
                    continue
                poi_pairs.add((a, b) if a < b else (b, a))
        print(f"[T4.4]   {len(poi_pairs)} unique Delaunay POI-POI edges")

        # 3. Index check-ins per POI.
        # ``self.checkins`` rows have integer position == check-in idx (the
        # preprocess output order; matches checkin_to_poi at the dict layer).
        # We need poi_idx per row; the POI mapping is on self.checkins via
        # the 'placeid'→placeid_to_idx remap done in _assign_regions.
        placeid_to_idx = self.placeid_to_idx
        from collections import defaultdict as _dd
        poi_to_checkins = _dd(list)
        for cidx, pid in enumerate(self.checkins['placeid'].values):
            pidx = placeid_to_idx.get(pid)
            if pidx is None:
                continue
            poi_to_checkins[pidx].append(cidx)

        # 4. Lift POI-POI edges to check-in pairs (bidirectional).
        rng = np.random.default_rng(seed=42)
        src_list, dst_list = [], []
        for poi_a, poi_b in poi_pairs:
            ca = poi_to_checkins.get(poi_a, [])
            cb = poi_to_checkins.get(poi_b, [])
            if not ca or not cb:
                continue
            sa = ca if len(ca) <= k_per_neighbor else rng.choice(ca, k_per_neighbor, replace=False).tolist()
            sb = cb if len(cb) <= k_per_neighbor else rng.choice(cb, k_per_neighbor, replace=False).tolist()
            for u in sa:
                for v in sb:
                    src_list.append(u); dst_list.append(v)
                    src_list.append(v); dst_list.append(u)

        if not src_list:
            return np.zeros((2, 0), dtype=np.int64), np.zeros(0, dtype=np.float32)

        edge_index = np.array([src_list, dst_list], dtype=np.int64)
        edge_weight = np.ones(len(src_list), dtype=np.float32)
        print(f"[T4.4]   {len(src_list)} Delaunay-lifted check-in edges (bidirectional)")
        return edge_index, edge_weight

    def _build_poi_delaunay_edges(self):
        """T5.2a / T5.2b — POI-level Delaunay triangulation edges.

        Builds a POI-POI graph (NOT check-in level — T4.4 closure note in
        INDEX.html flagged that check-in-level Delaunay over-smoothed).
        Output is a deduplicated undirected edge list shared by T5.2a
        (Node2Vec random walks) and T5.2b (masked-POI decoder neighbour
        aggregation).

        Returns:
            np.ndarray of shape (2, E_poi) with int64 dtype, where each
            column is an undirected POI pair (a, b) with a < b. Empty
            (2, 0) array if fewer than 3 POIs.
        """
        import scipy.spatial
        from itertools import combinations as _combinations
        print("Building POI-level Delaunay edges (T5.2a/T5.2b shared)...")

        poi_coords = np.array(
            self.pois.geometry.apply(lambda x: [x.x, x.y]).tolist(),
            dtype=np.float64,
        )
        if len(poi_coords) < 3:
            print("[poi-delaunay] fewer than 3 POIs; no Delaunay possible")
            return np.zeros((2, 0), dtype=np.int64)

        triangles = scipy.spatial.Delaunay(
            poi_coords, qhull_options="QJ QbB Pp"
        ).simplices

        poi_pairs = set()
        for tri in triangles:
            for a, b in _combinations(tri.tolist(), 2):
                if a == b:
                    continue
                poi_pairs.add((a, b) if a < b else (b, a))

        if not poi_pairs:
            return np.zeros((2, 0), dtype=np.int64)

        edges = np.array(sorted(poi_pairs), dtype=np.int64).T  # (2, E)
        print(f"[poi-delaunay]   {edges.shape[1]} unique POI-POI Delaunay edges")
        return edges

    def _build_covisit_pairs(self):
        """T6.1 — enumerate co-visit (poi_a, poi_b) pairs within
        ``self.covisit_k`` consecutive check-ins by the same user.

        Uses the already-sorted ``self.checkins`` (sorted by userid, datetime
        per ``_load_checkins``). For each consecutive offset δ ∈ [1, k-1]:
          * pair check-in i with check-in i+δ when userid matches AND
            POI(i) ≠ POI(i+δ).
          * record the unordered pair (min(poi_i, poi_j), max(poi_i, poi_j)).

        Output behaviour depends on ``self.covisit_dedup``:
          * True (default; original T6.1 design): deduplicate to unique pairs.
            Each pair contributes once regardless of how often it co-visits.
          * False (T6.1 implementation-robustness option; advisor 2026-05-19):
            keep multiplicity — emit one row per raw co-visit adjacency. Hub
            POIs get over-represented in the pair table; uniform sampling of
            B pairs at training time becomes weighted-by-multiplicity in
            expectation. Tests whether dedup was throwing away the popularity
            signal that the load-bearing version of the hypothesis needs.

        Output: int64 array shape [N_pairs, 2] saved under the dict key
        ``covisit_pairs``. Consumed by ``Check2HGIModule._poi_covisit_infonce``
        when ``p2p_lambda > 0``.

        Complexity: O(N_checkins × k) regardless of dedup mode (set-based
        dedup is O(N_pairs) extra; we skip that step when dedup=False).
        """
        dedup_label = "unique" if self.covisit_dedup else "with-multiplicity"
        print(f"[t6.1] enumerating co-visit POI pairs (k={self.covisit_k}, "
              f"{dedup_label})...")
        c2p = self.checkins['poi_idx'].values.astype(np.int64)
        uid = self.checkins['userid'].values
        N = len(c2p)

        # Collect per-offset pair lists. With dedup=True we coalesce via a
        # Python set (tuples are hashable, ~5-10 s wall on FL scale). With
        # dedup=False we just concatenate — no hashing, lower wall cost; the
        # output is bigger but cheap to store (int64 pairs).
        if self.covisit_dedup:
            pairs = set()
            for delta in range(1, self.covisit_k):
                a = c2p[:-delta]
                b = c2p[delta:]
                same_user = uid[:-delta] == uid[delta:]
                valid = same_user & (a != b)
                ia = a[valid]
                ib = b[valid]
                lo = np.minimum(ia, ib)
                hi = np.maximum(ia, ib)
                for x, y in zip(lo.tolist(), hi.tolist()):
                    pairs.add((x, y))
            if not pairs:
                print("[t6.1]   0 co-visit pairs (no eligible adjacencies)")
                return np.zeros((0, 2), dtype=np.int64)
            arr = np.array(sorted(pairs), dtype=np.int64)
            print(f"[t6.1]   {arr.shape[0]} unique co-visit POI pairs")
            return arr

        # Multiplicity-preserving path.
        lo_chunks = []
        hi_chunks = []
        for delta in range(1, self.covisit_k):
            a = c2p[:-delta]
            b = c2p[delta:]
            same_user = uid[:-delta] == uid[delta:]
            valid = same_user & (a != b)
            ia = a[valid]
            ib = b[valid]
            lo_chunks.append(np.minimum(ia, ib))
            hi_chunks.append(np.maximum(ia, ib))
        if not lo_chunks:
            print("[t6.1]   0 co-visit pairs (no eligible adjacencies)")
            return np.zeros((0, 2), dtype=np.int64)
        lo_all = np.concatenate(lo_chunks)
        hi_all = np.concatenate(hi_chunks)
        arr = np.stack([lo_all, hi_all], axis=1).astype(np.int64)
        # Report dedup statistics so the user can see the multiplicity ratio.
        n_raw = int(arr.shape[0])
        # Cheap unique count via pair encoding (assumes max poi idx < 2^31).
        max_poi = int(c2p.max()) + 1
        encoded = lo_all.astype(np.int64) * max_poi + hi_all.astype(np.int64)
        n_unique = int(np.unique(encoded).size)
        ratio = n_raw / max(n_unique, 1)
        print(f"[t6.1]   {n_raw} raw co-visit POI pairs ({n_unique} unique; "
              f"multiplicity ratio {ratio:.2f}x)")
        return arr

    def _compute_poi_feature_aggregates(self):
        """T5.2b — per-POI feature aggregates used as masked-recon targets.

        For each POI, compute:
          * mean category one-hot of constituent check-ins (P, num_cat),
            i.e. the empirical category distribution over the visits to
            that POI; and
          * log(1 + visit_count) (P,), a calibration of how popular the
            POI is.

        Both quantities are functions of the INPUT to the encoder (check-in
        category one-hot already lives in ``data.x``); reconstructing them
        adds no NEW information about the held-out fclass label. The signal
        the decoder is forced to learn is purely STRUCTURAL — predict a
        POI's category distribution from its Delaunay neighbours' POI
        embeddings, when the POI's own embedding has been masked out.

        Returns:
            poi_category_aggregate: np.ndarray[float32] (num_pois, num_cat)
            poi_visit_count_log:    np.ndarray[float32] (num_pois,)
        """
        print("Computing per-POI feature aggregates (T5.2b targets)...")
        num_pois = len(self.pois)
        num_cat = len(self.le_category.classes_)

        poi_idx = self.checkins['poi_idx'].values.astype(np.int64)
        cat_idx = self.checkins['category_encoded'].values.astype(np.int64)

        # Vectorised: scatter-add counts then normalise.
        counts = np.zeros((num_pois, num_cat), dtype=np.float64)
        np.add.at(counts, (poi_idx, cat_idx), 1.0)
        totals = counts.sum(axis=1, keepdims=True)              # (P, 1)
        # POIs with 0 visits would only arise via filter mismatch; guard.
        safe = np.where(totals > 0, totals, 1.0)
        poi_category_aggregate = (counts / safe).astype(np.float32)

        visit_count = totals.squeeze(-1).astype(np.float64)
        poi_visit_count_log = np.log1p(visit_count).astype(np.float32)
        print(f"[poi-aggregates]   {num_pois} POIs × {num_cat} cats; "
              f"log-visit range "
              f"[{poi_visit_count_log.min():.2f}, {poi_visit_count_log.max():.2f}]")
        return poi_category_aggregate, poi_visit_count_log

    def _apply_c3_composite_weights(self, edge_index, edge_weight):
        """T6.2 — apply Delaunay-multiplier and cross-region-penalty to the
        user-sequence edge weights.

        For each edge (src, tgt) in ``edge_index``:
          * delaunay_mult = ``c3_alpha_delaunay`` if (poi(src), poi(tgt)) is
            in the POI-Delaunay adjacency set (built by
            ``_build_poi_delaunay_edges`` and stored on ``self`` before this
            call); else 1.0.
          * crossregion_mult = ``c3_w_r`` if region(src) ≠ region(tgt);
            else 1.0.
          * edge_weight[e] *= delaunay_mult * crossregion_mult.

        At default (α=1, w_r=1) this is a no-op. Vectorised — no Python loop
        per edge. Requires ``self.poi_delaunay_edges`` (the Delaunay POI-POI
        edge index) to be present.
        """
        if not hasattr(self, 'poi_delaunay_edges') or self.poi_delaunay_edges is None:
            raise RuntimeError(
                "[T6.2] _apply_c3_composite_weights requires "
                "self.poi_delaunay_edges to be set first. Build the POI "
                "Delaunay graph via build_poi_delaunay=True before applying "
                "the C3 composite weights."
            )
        print(f"[t6.2] applying C3 composite weights: "
              f"α_delaunay={self.c3_alpha_delaunay} w_r={self.c3_w_r}")

        c2p = self.checkins['poi_idx'].values.astype(np.int64)
        p2r = self.pois['region_idx'].values.astype(np.int64)
        num_pois = int(c2p.max()) + 1

        # Build Delaunay POI-POI adjacency hash. ``poi_delaunay_edges`` is
        # (2, E_poi); for fast (poi_a, poi_b) ∈ adjacency lookup, encode
        # each undirected pair as ``min*num_pois + max`` and store in a set.
        pd_a = self.poi_delaunay_edges[0]
        pd_b = self.poi_delaunay_edges[1]
        pd_lo = np.minimum(pd_a, pd_b).astype(np.int64)
        pd_hi = np.maximum(pd_a, pd_b).astype(np.int64)
        delaunay_keys = set((pd_lo * num_pois + pd_hi).tolist())

        # Per-edge POI and region lookups.
        src = edge_index[0]
        tgt = edge_index[1]
        poi_src = c2p[src]
        poi_tgt = c2p[tgt]
        reg_src = p2r[poi_src]
        reg_tgt = p2r[poi_tgt]

        # Delaunay multiplier: vectorised set membership via encoded key.
        e_lo = np.minimum(poi_src, poi_tgt).astype(np.int64)
        e_hi = np.maximum(poi_src, poi_tgt).astype(np.int64)
        e_keys = (e_lo * num_pois + e_hi).tolist()
        is_delaunay = np.fromiter(
            (k in delaunay_keys for k in e_keys),
            dtype=bool, count=len(e_keys),
        )
        # Also mask out self-loops (poi_src == poi_tgt) — same-POI pairs are
        # trivially NOT Delaunay (they're the same node, not an edge).
        is_delaunay = is_delaunay & (poi_src != poi_tgt)

        # Cross-region penalty: edge crosses regions when src/tgt POI region differ.
        is_cross_region = reg_src != reg_tgt

        delaunay_mult = np.where(is_delaunay, self.c3_alpha_delaunay, 1.0)
        crossregion_mult = np.where(is_cross_region, self.c3_w_r, 1.0)
        weight_mult = (delaunay_mult * crossregion_mult).astype(np.float32)
        new_edge_weight = (edge_weight * weight_mult).astype(np.float32)

        n_delaunay = int(is_delaunay.sum())
        n_cross = int(is_cross_region.sum())
        print(f"[t6.2]   {n_delaunay} / {len(e_keys)} edges Delaunay-adjacent "
              f"({100*n_delaunay/len(e_keys):.1f}%); "
              f"{n_cross} / {len(e_keys)} edges cross-region "
              f"({100*n_cross/len(e_keys):.1f}%)")
        return new_edge_weight

    def _build_edges(self):
        """Build edges based on edge_type.

        Returns ``(edge_index, edge_weight, edge_type)`` where ``edge_type`` is
        a per-edge int64 array of relation indices. For single-relation graphs
        (``user_sequence`` or ``same_poi``) it is all-zeros. For ``both`` it
        encodes 0 = user_sequence, 1 = same_poi — required by the T3.3 R-GCN
        variant which aggregates separately per relation. For
        ``user_seq_delaunay`` (T4.4) it stays all-zeros (uniform GCN, no
        relation typing — the Delaunay leak corner only opens up under
        per-relation parameterisation, which was T3.3's downfall).
        """
        if self.edge_type == 'user_sequence':
            e, w = self._build_user_sequence_edges()
            return e, w, np.zeros(w.shape[0], dtype=np.int64)
        elif self.edge_type == 'same_poi':
            e, w = self._build_same_poi_edges()
            return e, w, np.zeros(w.shape[0], dtype=np.int64)
        elif self.edge_type == 'both':
            e1, w1 = self._build_user_sequence_edges()
            e2, w2 = self._build_same_poi_edges()
            edge_index = np.concatenate([e1, e2], axis=1)
            edge_weight = np.concatenate([w1, w2])
            edge_type = np.concatenate([
                np.zeros(w1.shape[0], dtype=np.int64),
                np.ones(w2.shape[0], dtype=np.int64),
            ])
            return edge_index, edge_weight, edge_type
        elif self.edge_type == 'user_seq_delaunay':
            # T4.4 — user_sequence + Delaunay-lifted spatial edges, uniform
            # GCN aggregation (no R-GCN; edge_type all-zeros).
            e1, w1 = self._build_user_sequence_edges()
            e2, w2 = self._build_delaunay_lifted_edges()
            edge_index = np.concatenate([e1, e2], axis=1)
            edge_weight = np.concatenate([w1, w2])
            return edge_index, edge_weight, np.zeros(edge_weight.shape[0], dtype=np.int64)
        else:
            raise ValueError(f"Unknown edge_type: {self.edge_type}")

    def _build_node_features(self):
        """Build check-in node features: category one-hot + temporal encoding."""
        print("Building node features...")

        num_checkins = len(self.checkins)
        num_categories = len(self.le_category.classes_)

        # Category one-hot
        category_onehot = np.zeros((num_checkins, num_categories), dtype=np.float32)
        category_onehot[np.arange(num_checkins), self.checkins['category_encoded'].values] = 1.0

        # Temporal encoding (sin/cos for hour and day of week)
        # Parse datetime
        dt = pd.to_datetime(self.checkins['datetime'])
        hour = dt.dt.hour.values
        dow = dt.dt.dayofweek.values

        temporal = np.zeros((num_checkins, 4), dtype=np.float32)
        temporal[:, 0] = np.sin(2 * np.pi * hour / 24)  # hour_sin
        temporal[:, 1] = np.cos(2 * np.pi * hour / 24)  # hour_cos
        temporal[:, 2] = np.sin(2 * np.pi * dow / 7)    # dow_sin
        temporal[:, 3] = np.cos(2 * np.pi * dow / 7)    # dow_cos

        # Concatenate
        node_features = np.concatenate([category_onehot, temporal], axis=1)

        print(f"Node features shape: {node_features.shape}")
        return node_features

    def _compute_region_features(self):
        """Compute region-level features: areas, adjacency, and similarity."""
        print("Computing region features...")

        # Unique regions with POIs
        unique_regions = list(self.region_to_idx.keys())

        # Compute region areas
        region_area = np.zeros(self.num_regions, dtype=np.float32)
        for geoid, idx in self.region_to_idx.items():
            region_row = self.boroughs[self.boroughs['GEOID'] == geoid]
            if len(region_row) > 0:
                region_area[idx] = region_row.geometry.iloc[0].area

        # Compute adjacency
        region_adjacency = self._compute_adjacency_matrix(unique_regions)

        # Compute similarity (simple: based on POI counts)
        coarse_similarity = self._compute_similarity_matrix()

        return region_area, region_adjacency, coarse_similarity

    def _compute_adjacency_matrix(self, unique_regions):
        """Compute spatial adjacency matrix between regions."""
        valid_regions = self.boroughs[self.boroughs['GEOID'].isin(unique_regions)].copy()
        valid_regions['idx'] = valid_regions['GEOID'].map(self.region_to_idx)

        joined = gpd.sjoin(valid_regions, valid_regions, how='inner', predicate='intersects')
        edges = joined[joined['idx_left'] != joined['idx_right']]

        if len(edges) == 0:
            return np.zeros((2, 0), dtype=np.int64)

        return np.vstack([
            edges['idx_left'].values.astype(np.int64),
            edges['idx_right'].values.astype(np.int64)
        ])

    def _compute_similarity_matrix(self):
        """Compute region similarity based on shared POI categories."""
        similarity = np.eye(self.num_regions, dtype=np.float32) * 0.5

        # Count category distribution per region
        poi_region = self.pois[['region_idx', 'category_encoded']].values
        num_categories = len(self.le_category.classes_)

        region_cat_counts = np.zeros((self.num_regions, num_categories))
        for region_idx, cat_idx in poi_region:
            region_cat_counts[int(region_idx), int(cat_idx)] += 1

        # Normalize
        row_sums = region_cat_counts.sum(axis=1, keepdims=True)
        row_sums[row_sums == 0] = 1
        region_cat_dist = region_cat_counts / row_sums

        # Cosine similarity
        norms = np.linalg.norm(region_cat_dist, axis=1, keepdims=True)
        norms[norms == 0] = 1
        normalized = region_cat_dist / norms
        similarity = np.dot(normalized, normalized.T)

        return similarity.astype(np.float32)

    def get_data(self):
        """Execute full preprocessing pipeline and return data dict."""
        self._load_checkins()
        self._load_boroughs()
        self._assign_regions()

        # Build edges (T3.3 plumbing: per-edge relation index for R-GCN)
        edge_index, edge_weight, edge_type = self._build_edges()

        # T6.2 — composite C3 edge weights (HGI-style Delaunay multiplier +
        # cross-region penalty applied to user_sequence temporal-decay weights).
        # Requires the POI-Delaunay graph; build it eagerly here so that
        # ``self.poi_delaunay_edges`` is set before the multiplier is applied.
        # We auto-enable ``build_poi_delaunay`` so the same graph is included
        # in the output dict (for any downstream use that needs it).
        _c3_active = (self.c3_alpha_delaunay != 1.0 or self.c3_w_r != 1.0)
        if _c3_active:
            self.poi_delaunay_edges = self._build_poi_delaunay_edges()
            self.build_poi_delaunay = True   # ensure it's emitted in the dict below
            edge_weight = self._apply_c3_composite_weights(edge_index, edge_weight)

        # Normalize edge weights
        if len(edge_weight) > 0:
            mi, ma = edge_weight.min(), edge_weight.max()
            if ma > mi:
                edge_weight = (edge_weight - mi) / (ma - mi)

        # Build node features
        node_features = self._build_node_features()

        # Build hierarchical mappings
        checkin_to_poi = self.checkins['poi_idx'].values.astype(np.int64)
        poi_to_region = self.pois['region_idx'].values.astype(np.int64)

        # Compute region features
        region_area, region_adjacency, coarse_similarity = self._compute_region_features()

        # Metadata for output
        metadata = self.checkins[['userid', 'placeid', 'datetime', 'category']].copy()

        out = {
            'node_features': node_features,
            'edge_index': edge_index,
            'edge_weight': edge_weight.astype(np.float32),
            'edge_type': edge_type.astype(np.int64),
            'checkin_to_poi': checkin_to_poi,
            'poi_to_region': poi_to_region,
            'region_adjacency': region_adjacency,
            'region_area': region_area,
            'coarse_region_similarity': coarse_similarity,
            'num_checkins': len(self.checkins),
            'num_pois': len(self.pois),
            'num_regions': self.num_regions,
            'metadata': metadata,
            'placeid_to_idx': self.placeid_to_idx,
            'region_to_idx': self.region_to_idx,
        }

        # T5.2a / T5.2b — optional POI-level Delaunay edge list (gated by
        # ``build_poi_delaunay``). Cached in the same pickle so subsequent
        # runs reuse it; consumed by both T5.2a (Node2Vec walks) and T5.2b
        # (masked-POI decoder neighbour aggregation).
        # If T6.2 already built the Delaunay graph above, reuse it (don't
        # rebuild) — ``self.poi_delaunay_edges`` is set in that case.
        if self.build_poi_delaunay:
            if hasattr(self, 'poi_delaunay_edges') and self.poi_delaunay_edges is not None:
                out['poi_delaunay_edge_index'] = self.poi_delaunay_edges
            else:
                out['poi_delaunay_edge_index'] = self._build_poi_delaunay_edges()

        # T5.2b — optional per-POI reconstruction targets (gated by
        # ``build_poi_aggregates``).
        if self.build_poi_aggregates:
            poi_cat_agg, poi_visit_log = self._compute_poi_feature_aggregates()
            out['poi_category_aggregate'] = poi_cat_agg
            out['poi_visit_count_log'] = poi_visit_log

        # T6.1 — optional co-visit POI-POI pair list (gated by
        # ``build_covisit_pairs``). Consumed by Check2HGIModule's 4th boundary
        # when ``p2p_lambda > 0``.
        if self.build_covisit_pairs:
            out['covisit_pairs'] = self._build_covisit_pairs()

        return out


def build_view2_graph_dict(canonical_dict):
    """T5.3 — Build a View-2 graph dict derived from the canonical (View-1) dict.

    View 2 is built explicitly around POI categorical structure:
      * Edges: same_poi only (no user_sequence, no temporal edges).
      * Node features: category one-hot only (drops the 4 temporal sin/cos
        columns of canonical layout). The discarded columns are not zero-
        padded — feature dim shrinks to ``num_categories``.
      * Uniform edge weights (1.0) — temporal decay is the leak vector that
        View 2 is engineered to avoid.
      * Same checkin_to_poi / poi_to_region as View 1 so the two views
        share POI identity (required for cross-view POI-level alignment).

    No new leak channel: the View-2 features are a strict subset of the
    View-1 input features (the category one-hot block). The novelty is
    structural — View 2 carries no temporal or sequential edges.

    Args:
        canonical_dict: dict produced by ``Check2HGIPreprocess.get_data()``.

    Returns:
        dict with same schema as canonical, but with view-2 edges + features.
    """
    canonical_x = canonical_dict['node_features']
    if canonical_x.shape[1] < 5:
        raise ValueError(
            f"build_view2_graph_dict: node_features shape {canonical_x.shape} "
            f"too small for canonical layout (expected C+4 with C>=1)."
        )
    num_categories = canonical_x.shape[1] - 4
    # Category one-hot only — first C columns of canonical.
    view2_features = canonical_x[:, :num_categories].astype(np.float32)

    # Build same-POI edges from checkin_to_poi (no need to re-load raw checkins).
    checkin_to_poi = canonical_dict['checkin_to_poi']
    max_edges_per_poi = 50
    rng = np.random.default_rng(seed=42)
    # Group check-in indices by POI via argsort + run-length encoding (faster
    # than pandas groupby on multi-million-row arrays).
    order = np.argsort(checkin_to_poi, kind='stable')
    sorted_pois = checkin_to_poi[order]
    sorted_cidx = order
    # Boundaries between POI groups.
    breaks = np.flatnonzero(np.diff(sorted_pois)) + 1
    starts = np.concatenate([[0], breaks])
    ends = np.concatenate([breaks, [len(sorted_pois)]])
    src_list, tgt_list = [], []
    for s, e in zip(starts.tolist(), ends.tolist()):
        if e - s < 2:
            continue
        indices = sorted_cidx[s:e]
        if len(indices) > max_edges_per_poi:
            indices = rng.choice(indices, max_edges_per_poi, replace=False)
        n = len(indices)
        # All unordered pairs (i, j), append bidirectional.
        for i in range(n):
            for j in range(i + 1, n):
                src_list.append(int(indices[i])); tgt_list.append(int(indices[j]))
                src_list.append(int(indices[j])); tgt_list.append(int(indices[i]))
    if src_list:
        edge_index = np.array([src_list, tgt_list], dtype=np.int64)
        edge_weight = np.ones(edge_index.shape[1], dtype=np.float32)
    else:
        edge_index = np.zeros((2, 0), dtype=np.int64)
        edge_weight = np.zeros(0, dtype=np.float32)

    out = dict(canonical_dict)  # shallow copy — keeps shared metadata refs
    out['node_features'] = view2_features
    out['edge_index'] = edge_index
    out['edge_weight'] = edge_weight
    out['edge_type'] = np.zeros(edge_weight.shape[0], dtype=np.int64)
    return out


def build_view2_graph_file(city: str):
    """T5.3 — Build & cache the View-2 graph for ``city`` derived from the
    canonical Check2HGI cache. Returns the output path.

    The canonical (View-1) graph file must already exist at
    ``IoPaths.CHECK2HGI.get_graph_data_file(city)``. The View-2 cache is
    written sibling to it as ``view2_graph.pt``.
    """
    canonical_path = IoPaths.CHECK2HGI.get_graph_data_file(city)
    if not canonical_path.exists():
        raise FileNotFoundError(
            f"Canonical Check2HGI graph not found at {canonical_path}; "
            f"run preprocess_check2hgi first."
        )
    with open(canonical_path, 'rb') as f:
        canonical_dict = pkl.load(f)
    view2_dict = build_view2_graph_dict(canonical_dict)
    view2_path = canonical_path.parent / "view2_graph.pt"
    with open(view2_path, 'wb') as f:
        pkl.dump(view2_dict, f)
    print(f"[T5.3] Saved view2 graph: {view2_path}  "
          f"features={view2_dict['node_features'].shape}  "
          f"edges={view2_dict['edge_index'].shape[1]}")
    return view2_path


def preprocess_check2hgi(city, city_shapefile, edge_type='user_sequence',
                          temporal_decay=3600.0, cta_file=None,
                          build_poi_delaunay: bool = False,
                          build_poi_aggregates: bool = False,
                          build_covisit_pairs: bool = False,
                          covisit_k: int = 3,
                          covisit_dedup: bool = True,
                          c3_alpha_delaunay: float = 1.0,
                          c3_w_r: float = 1.0,
                          build_view2: bool = False):
    """
    Main preprocessing function for Check2HGI.

    Args:
        city: City/state name
        city_shapefile: Path to census tract shapefile
        edge_type: Type of edges ('user_sequence', 'same_poi', 'both')
        temporal_decay: Decay parameter for temporal edge weights
        cta_file: Optional path to pre-computed boroughs file
        build_poi_delaunay: T5.2a / T5.2b — when True, cache a POI-level
            Delaunay triangulation edge list under
            ``poi_delaunay_edge_index``. Default False reproduces canonical.
        build_poi_aggregates: T5.2b — when True, cache per-POI feature
            aggregates (category mean one-hot + log visit count) under
            ``poi_category_aggregate`` and ``poi_visit_count_log``. Default
            False reproduces canonical.
    """
    temp_folder = IoPaths.CHECK2HGI.get_temp_dir(city)
    temp_folder.mkdir(parents=True, exist_ok=True)

    output_folder = IoPaths.CHECK2HGI.get_output_dir(city)
    output_folder.mkdir(parents=True, exist_ok=True)

    checkins_file = IoPaths.get_city(city)
    boroughs_path = Path(cta_file) if cta_file else temp_folder / "boroughs_area.csv"

    # Create boroughs file if not exists
    if cta_file is None and not boroughs_path.exists():
        print(f"Creating boroughs file from shapefile: {city_shapefile}")
        census = gpd.read_file(city_shapefile).to_crs(4326)
        census[['GEOID', 'geometry']].to_csv(boroughs_path, index=False)

    pre = Check2HGIPreprocess(
        checkins_file=str(checkins_file),
        boroughs_file=str(boroughs_path),
        temp_path=temp_folder,
        edge_type=edge_type,
        temporal_decay=temporal_decay,
        build_poi_delaunay=build_poi_delaunay,
        build_poi_aggregates=build_poi_aggregates,
        build_covisit_pairs=build_covisit_pairs,
        covisit_k=covisit_k,
        covisit_dedup=covisit_dedup,
        c3_alpha_delaunay=c3_alpha_delaunay,
        c3_w_r=c3_w_r,
    )

    data = pre.get_data()

    output_path = IoPaths.CHECK2HGI.get_graph_data_file(city)
    with open(output_path, 'wb') as f:
        pkl.dump(data, f)

    print(f"Saved: {output_path}")
    print(f"Check-ins: {data['num_checkins']}, POIs: {data['num_pois']}, "
          f"Regions: {data['num_regions']}, Edges: {len(data['edge_weight'])}")

    # T5.3 — optionally also write the View-2 graph derived from canonical.
    # Gated by build_view2 flag so canonical preprocess is unchanged when off.
    if build_view2:
        view2_dict = build_view2_graph_dict(data)
        view2_path = output_path.parent / "view2_graph.pt"
        with open(view2_path, 'wb') as f:
            pkl.dump(view2_dict, f)
        print(f"[T5.3] Saved view2 graph: {view2_path}  "
              f"features={view2_dict['node_features'].shape}  "
              f"edges={view2_dict['edge_index'].shape[1]}")

    return output_path


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Preprocess check-in data for Check2HGI')
    parser.add_argument('--city', type=str, default='Texas')
    parser.add_argument('--shapefile', type=str, default=str(Resources.TL_TX))
    parser.add_argument('--edge_type', type=str, default='user_sequence',
                        choices=['user_sequence', 'same_poi', 'both'])
    parser.add_argument('--temporal_decay', type=float, default=3600.0,
                        help='Decay parameter for temporal edge weights (seconds)')
    parser.add_argument('--cta', type=str, default=None)

    args = parser.parse_args()
    preprocess_check2hgi(
        city=args.city,
        city_shapefile=args.shapefile,
        edge_type=args.edge_type,
        temporal_decay=args.temporal_decay,
        cta_file=args.cta
    )
