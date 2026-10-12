"""HGI preprocessing module for creating hierarchical graph structures."""

import argparse
import json
import logging
import pickle as pkl
from itertools import combinations
from pathlib import Path
from warnings import simplefilter

import geopandas as gpd
import numpy as np
import pandas as pd
import scipy.spatial
import torch
from shapely import wkt
from sklearn.preprocessing import LabelEncoder

from configs.paths import IoPaths, Resources
from embeddings.hgi.utils import SpatialUtils, mode_or_first


DEFAULT_CROSS_REGION_WEIGHT = 0.7


class HGIPreprocess:
    """Preprocessing pipeline for HGI embeddings."""

    def __init__(self, pois_filename, boroughs_filename, temp_path,
                 cross_region_weight: float = DEFAULT_CROSS_REGION_WEIGHT,
                 shuffle_fclass_seed: int | None = None):
        self.pois_filename = pois_filename
        self.boroughs_filename = boroughs_filename
        self.temp_path = temp_path
        # Cross-region edge weight `w_r` (Eq. 2 of Huang et al., ISPRS 2023).
        # Paper uses 0.4 (Xiamen/Shenzhen); third-party reference uses 0.5.
        # On our Alabama sweep (w_r ∈ {0.4, 0.5, 0.6, 0.7}) Cat F1 rose monotonically
        # 0.74 → 0.82, so the optimum is dataset-specific. Default 0.7 is best-known
        # for US state-scale sparse datasets; sweep per state when tuning.
        self.cross_region_weight = float(cross_region_weight)
        # Leakage-ablation arm C: when set, the encoded fclass column is
        # randomly permuted across POIs right after LabelEncoding. Category
        # is NOT touched. Breaks the fclass→category determinism that makes
        # the Category task a near-trivial lookup on OSM data.
        self.shuffle_fclass_seed = shuffle_fclass_seed

    def _read_poi_data(self):
        """Load and prepare POI data."""
        self.pois = pd.read_parquet(self.pois_filename)

        # Check for required columns and provide helpful error messages
        required_cols = ['category', 'spot', 'placeid', 'latitude', 'longitude']
        missing_cols = [col for col in required_cols if col not in self.pois.columns]

        if missing_cols:
            raise ValueError(
                f"Missing required columns: {missing_cols}\n"
                f"Available columns: {self.pois.columns.tolist()}"
            )

        # Rename spot to fclass for internal consistency
        self.pois = self.pois.rename(columns={"spot": "fclass"})

        self.pois = self.pois.dropna(subset=["category"])

        # Create geometry column if not exists
        if 'geometry' not in self.pois.columns:
            self.pois['geometry'] = self.pois.apply(
                lambda x: f"POINT({x['longitude']} {x['latitude']})"
                if pd.notnull(x['longitude']) and pd.notnull(x['latitude'])
                else None,
                axis=1
            )

        # Handle duplicate placeids
        if not self.pois['placeid'].is_unique:
            agg_funcs = {
                'category': mode_or_first,
                'fclass': mode_or_first,
                'longitude': 'mean',  # Use mean to get centroid of multiple observations
                'latitude': 'mean',  # Use mean to get centroid of multiple observations
                'geometry': 'first'  # Will be recreated from mean lat/lon
            }
            for col in self.pois.columns:
                if col not in agg_funcs and col != 'placeid':
                    agg_funcs[col] = 'first'
            self.pois = self.pois.groupby('placeid').agg(agg_funcs).reset_index()

            # Recreate geometry from aggregated coordinates
            self.pois['geometry'] = self.pois.apply(
                lambda x: f"POINT({x['longitude']} {x['latitude']})"
                if pd.notnull(x['longitude']) and pd.notnull(x['latitude'])
                else None,
                axis=1
            )

        # Convert to GeoDataFrame. Drop POIs with null geometry — FSQ /
        # Massive-STEPS check-ins can carry missing coordinates (absent from US
        # Gowalla); leaving them None crashes the geom_type step below. This
        # mirrors POI-RGNN's NaN-coord drop and is a no-op for US states.
        self.pois["geometry"] = self.pois["geometry"].apply(
            lambda g: wkt.loads(g) if isinstance(g, str) else None
        )
        n_before = len(self.pois)
        self.pois = self.pois[self.pois["geometry"].notna()].reset_index(drop=True)
        if len(self.pois) < n_before:
            logging.info(
                f"[hgi-preprocess] dropped {n_before - len(self.pois)} POIs with null geometry "
                f"(no coordinates); kept {len(self.pois)}"
            )
        self.pois = gpd.GeoDataFrame(self.pois, geometry="geometry", crs="EPSG:4326")
        self.pois["geometry"] = self.pois["geometry"].apply(
            lambda x: x if x.geom_type == "Point" else x.centroid
        )

    def _read_boroughs_data(self):
        """Load boroughs/regions data and encode categories."""
        self.boroughs = pd.read_csv(self.boroughs_filename)
        self.boroughs["geometry"] = self.boroughs["geometry"].apply(wkt.loads)
        self.boroughs = gpd.GeoDataFrame(self.boroughs, geometry="geometry", crs="EPSG:4326")

        # Encode categories and save encoder objects
        self.category_encoder = LabelEncoder()
        self.pois["category"] = self.category_encoder.fit_transform(self.pois["category"].values)

        self.fclass_encoder = LabelEncoder()
        self.pois["fclass"] = self.fclass_encoder.fit_transform(self.pois["fclass"].values)

        # Leakage-ablation arm C: permute fclass values across POIs, keeping
        # category intact. This breaks the fclass→category determinism while
        # preserving graph topology, region assignment, and the downstream
        # MTL category target.
        if self.shuffle_fclass_seed is not None:
            rng = np.random.RandomState(self.shuffle_fclass_seed)
            self.pois["fclass"] = rng.permutation(self.pois["fclass"].values)
            print(
                f"  ⚠  ABLATION: fclass values shuffled across POIs "
                f"(seed={self.shuffle_fclass_seed})"
            )

        # Save the class lists for return dictionary
        self.category_classes = self.category_encoder.classes_.tolist()
        self.fclass_classes = self.fclass_encoder.classes_.tolist()

        # Validation after encoding
        print(f"  Encoded {len(self.category_classes)} categories: {self.category_classes[:5]}...")
        print(f"  Encoded {len(self.fclass_classes)} fclasses: {self.fclass_classes[:5]}...")

        # Check for NaN values after encoding
        nan_categories = self.pois['category'].isna().sum()
        nan_fclasses = self.pois['fclass'].isna().sum()

        if nan_categories > 0 or nan_fclasses > 0:
            print(f"  WARNING: Found {nan_categories} NaN categories and {nan_fclasses} NaN fclasses after encoding")

        # Spatial join with boroughs
        self.pois = self.pois[['placeid', 'category', 'fclass', 'geometry']].sjoin(
            self.boroughs, how='inner', predicate='intersects'
        )

    def _create_graph(self):
        """Create spatial graph using Delaunay triangulation."""
        points = np.array(self.pois.geometry.apply(lambda x: [x.x, x.y]).tolist())
        D = SpatialUtils.diagonal_length_bbox(self.pois.geometry.unary_union.envelope.bounds)

        # Delaunay triangulation
        triangles = scipy.spatial.Delaunay(points, qhull_options="QJ QbB Pp").simplices

        # Build edge list with weights
        edges = []
        seen = set()
        for simplex in triangles:
            for x, y in combinations(simplex, 2):
                if (x, y) not in seen and (y, x) not in seen:
                    seen.add((x, y))
                    dist = SpatialUtils.haversine_np(*points[x], *points[y])
                    w1 = np.log((1 + D ** 1.5) / (1 + dist ** 1.5))
                    # Eq. (2) of Huang et al. (ISPRS 2023): intra-region weight is
                    # always 1.0; cross-region weight `w_r` is configurable
                    # (paper 0.4, repro 0.5, our best on Alabama 0.7).
                    w2 = 1.0 if self.pois.iloc[x]["GEOID"] == self.pois.iloc[y]["GEOID"] else self.cross_region_weight
                    edges.append({'source': x, 'target': y, 'weight': w1 * w2})

        self.edges = pd.DataFrame(edges)

        # Normalize weights
        mi, ma = self.edges['weight'].min(), self.edges['weight'].max()
        self.edges['weight'] = (self.edges['weight'] - mi) / (ma - mi)

        # Save for POI2Vec
        self.edges.to_csv(str(self.temp_path / 'edges.csv'), index=False)
        self.pois[['placeid', 'category', 'fclass']].to_csv(str(self.temp_path / 'pois.csv'), index=False)

    def _compute_region_features(self):
        """Compute region-level features: areas, adjacency, and similarity."""
        unique_regions = self.pois['GEOID'].unique()
        region_to_idx = {region: idx for idx, region in enumerate(unique_regions)}

        # Map POIs to region indices
        self.region_id = self.pois['GEOID'].map(region_to_idx).values

        # Compute region areas in km² (project to metric CRS)
        boroughs_metric = self.boroughs.to_crs(3857)
        self.region_area = np.array([
            boroughs_metric[boroughs_metric['GEOID'] == r].geometry.iloc[0].area / 1e6
            for r in unique_regions
        ], dtype=np.float32)

        # Compute adjacency and similarity
        self.region_adjacency = self._compute_adjacency_matrix(unique_regions, region_to_idx)
        self.coarse_region_similarity = self._compute_similarity_matrix(unique_regions)

    def _compute_adjacency_matrix(self, unique_regions, region_to_idx):
        """Compute spatial adjacency matrix between regions."""
        valid_regions = self.boroughs[self.boroughs['GEOID'].isin(unique_regions)].copy()
        valid_regions['idx'] = valid_regions['GEOID'].map(region_to_idx)

        joined = gpd.sjoin(valid_regions, valid_regions, how='inner', predicate='intersects')
        edges = joined[joined['idx_left'] != joined['idx_right']]

        if len(edges) == 0:
            return np.zeros((2, 0), dtype=np.int64)

        return np.vstack([
            edges['idx_left'].values.astype(np.int64),
            edges['idx_right'].values.astype(np.int64)
        ])

    def _compute_similarity_matrix(self, unique_regions):
        """Compute region similarity from fclass distribution (cosine similarity)."""
        from sklearn.metrics.pairwise import cosine_similarity

        crosstab = pd.crosstab(self.pois['GEOID'], self.pois['fclass'])
        crosstab = crosstab.reindex(unique_regions, fill_value=0)

        return cosine_similarity(crosstab.values).astype(np.float32)

    def save_encoders(self):
        """Save encoder mappings to JSON for inspection."""
        encodings = {
            'category': {
                name: int(code)
                for name, code in zip(
                    self.category_encoder.classes_,
                    self.category_encoder.transform(self.category_encoder.classes_)
                )
            },
            'fclass': {
                name: int(code)
                for name, code in zip(
                    self.fclass_encoder.classes_,
                    self.fclass_encoder.transform(self.fclass_encoder.classes_)
                )
            }
        }

        output_file = Path(self.temp_path) / 'encodings.json'
        with open(output_file, 'w') as f:
            json.dump(encodings, f, indent=2)

        print(f"  Saved encodings to {output_file}")

    def _load_poi_embeddings(self, poi_emb_path, use_onehot_fallback=False):
        """Load pre-trained POI embeddings or use one-hot encoding.

        Args:
            poi_emb_path: Path to embedding file
            use_onehot_fallback: If True, use one-hot encoding for missing POIs
                               instead of zeros (default: False)
        """
        if poi_emb_path is None or not Path(poi_emb_path).exists():
            simplefilter(action="ignore", category=pd.errors.PerformanceWarning)
            return pd.get_dummies(self.pois['category'], dtype=int).values.astype(np.float32)

        blob = torch.load(poi_emb_path, map_location="cpu")

        if "in_embed.weight" in blob:
            embeddings = blob["in_embed.weight"].detach().cpu().numpy()
            placeids = blob.get("placeids", [])
        elif "embeddings" in blob:
            embeddings = blob["embeddings"].detach().cpu().numpy()
            placeids = blob.get("placeids", [])
        else:
            raise ValueError("Unknown embedding format")

        placeid_to_idx = {str(pid): i for i, pid in enumerate(placeids)}
        X = np.zeros((len(self.pois), embeddings.shape[1]), dtype=np.float32)

        missing_count = 0
        missing_indices = []
        for i, pid in enumerate(self.pois['placeid'].tolist()):
            if str(pid) in placeid_to_idx:
                X[i] = embeddings[placeid_to_idx[str(pid)]]
            else:
                missing_count += 1
                missing_indices.append(i)

        if missing_count > 0:
            print(f"  WARNING: {missing_count}/{len(self.pois)} POIs missing from embeddings")

            if use_onehot_fallback:
                print(f"  Using one-hot encoding based on fclass for missing POIs")
                # Get fclass values for missing POIs
                missing_fclasses = self.pois.iloc[missing_indices]['fclass'].values
                num_fclasses = len(self.fclass_classes)

                for idx, fclass in zip(missing_indices, missing_fclasses):
                    onehot = np.zeros(embeddings.shape[1])
                    # Use fclass as index (modulo embedding dim for safety)
                    onehot[fclass % embeddings.shape[1]] = 1.0
                    X[idx] = onehot
            else:
                print(f"  Filled with zeros (use use_onehot_fallback=True for one-hot encoding)")

        return X

    def get_data_torch(self, poi_emb_path=None, use_onehot_fallback=False):
        """Execute full preprocessing pipeline."""
        print("Reading POI data...")
        self._read_poi_data()

        print("Reading boroughs data...")
        self._read_boroughs_data()

        print("Creating spatial graph...")
        self._create_graph()

        print("Computing region features...")
        self._compute_region_features()

        print("Loading POI embeddings...")
        node_features = self._load_poi_embeddings(poi_emb_path, use_onehot_fallback)

        # Save encoders for debugging
        self.save_encoders()

        return {
            'node_features': node_features,
            'edge_index': self.edges[["source", "target"]].T.values,
            'edge_weight': self.edges["weight"].values,
            'region_id': self.region_id,
            'region_area': self.region_area,
            'coarse_region_similarity': self.coarse_region_similarity,
            'region_adjacency': self.region_adjacency,
            'number_pois': len(self.pois),
            'number_regions': len(np.unique(self.region_id)),
            'y': self.pois['category'].values,
            'place_id': self.pois['placeid'].values,
            'category_classes': self.category_classes,
            'fclass_classes': self.fclass_classes,
        }


def preprocess_hgi(city, city_shapefile, poi_emb_path=None, cta_file=None,
                   use_onehot_fallback=False,
                   cross_region_weight: float = DEFAULT_CROSS_REGION_WEIGHT,
                   shuffle_fclass_seed: int | None = None):
    """Main preprocessing function for HGI (Phase 3a only).

    Args:
        cross_region_weight: Eq. (2) cross-region edge weight `w_r`. Defaults to
            DEFAULT_CROSS_REGION_WEIGHT (0.7). Paper uses 0.4, third-party
            reference 0.5. Sweep per dataset when tuning — Alabama's optimum
            (0.7) differs from the paper's Xiamen/Shenzhen value (0.4).
        shuffle_fclass_seed: Leakage-ablation arm C. When set, permutes the
            encoded fclass column across POIs (category untouched). Use the
            same seed across the Phase 3a and Phase 4 preprocess calls so
            POI2Vec training and region similarity see a consistent shuffle.
    """
    temp_folder = IoPaths.HGI.get_temp_dir(city)
    temp_folder.mkdir(parents=True, exist_ok=True)

    output_folder = IoPaths.HGI.get_output_dir(city)
    output_folder.mkdir(parents=True, exist_ok=True)

    checkins = IoPaths.get_city(city)
    boroughs_path = Path(cta_file) if cta_file else IoPaths.HGI.get_boroughs_file(city)

    # Create boroughs file if not exists
    if cta_file is None and not boroughs_path.exists():
        print(f"Creating boroughs file from shapefile: {city_shapefile}")
        census = gpd.read_file(city_shapefile).to_crs(4326)
        census[['GEOID', 'geometry']].to_csv(boroughs_path, index=False)

    # Run preprocessing (Phase 3a: create graph structure)
    pre = HGIPreprocess(str(checkins), str(boroughs_path), temp_folder,
                        cross_region_weight=cross_region_weight,
                        shuffle_fclass_seed=shuffle_fclass_seed)
    print(f"  Cross-region edge weight w_r = {pre.cross_region_weight}")
    data = pre.get_data_torch(poi_emb_path=poi_emb_path, use_onehot_fallback=use_onehot_fallback)

    print(f"✓ Phase 3a complete: Delaunay graph created")
    print(f"  POIs: {data['number_pois']}, Regions: {data['number_regions']}, Edges: {len(data['edge_weight'])}")
    print(f"  Intermediate files saved to: {temp_folder}")
    print(f"    - edges.csv (Delaunay graph)")
    print(f"    - pois.csv (POI-region mapping)")
    print(f"    - encodings.json (category/fclass mappings)")

    # IMPORTANT: Return data dict instead of saving pickle
    # The pickle should be saved in Phase 4 (separate script)
    return data


def create_hgi_graph_pickle(city, poi_emb_path=None, use_onehot_fallback=False,
                            cross_region_weight: float = DEFAULT_CROSS_REGION_WEIGHT):
    """Phase 4: Create final HGI graph pickle file."""
    data = preprocess_hgi(city, None, poi_emb_path, None, use_onehot_fallback,
                          cross_region_weight=cross_region_weight)

    output_path = IoPaths.HGI.get_graph_data_file(city)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "wb") as f:
        pkl.dump(data, f)

    print(f"✓ Phase 4 complete: Graph pickle saved to {output_path}")
    return output_path


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Preprocess POI data for HGI')
    parser.add_argument('--city', type=str, default='Alabama')
    parser.add_argument('--shapefile', type=str, default=Resources.TL_AL)
    parser.add_argument('--poi_emb', type=str, default=None)
    parser.add_argument('--cta', type=str, default=None)
    parser.add_argument('--use_onehot_fallback', action='store_true',
                        help='Use one-hot encoding for POIs missing embeddings')
    parser.add_argument('--save_pickle', action='store_true',
                        help='Save pickle file (Phase 4) instead of just returning data (Phase 3a)')
    parser.add_argument('--cross_region_weight', type=float, default=DEFAULT_CROSS_REGION_WEIGHT,
                        help=(f'Cross-region edge weight w_r (Eq. 2). '
                              f'Default {DEFAULT_CROSS_REGION_WEIGHT}. Paper 0.4, repro 0.5. '
                              f'Sweep per dataset when tuning.'))

    args = parser.parse_args()

    if args.save_pickle:
        create_hgi_graph_pickle(city=args.city, poi_emb_path=args.poi_emb,
                                use_onehot_fallback=args.use_onehot_fallback,
                                cross_region_weight=args.cross_region_weight)
    else:
        preprocess_hgi(city=args.city, city_shapefile=args.shapefile,
                       poi_emb_path=args.poi_emb, cta_file=args.cta,
                       use_onehot_fallback=args.use_onehot_fallback,
                       cross_region_weight=args.cross_region_weight)
