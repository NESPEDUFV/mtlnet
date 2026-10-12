"""POI2HGI preprocessing module for creating hierarchical graph structures with temporal features."""

import argparse
import pickle as pkl
from itertools import combinations
from pathlib import Path
from warnings import simplefilter

import geopandas as gpd
import numpy as np
import pandas as pd
import scipy.spatial
from shapely import wkt
from sklearn.preprocessing import LabelEncoder

from configs.paths import IoPaths, Resources
from embeddings.hgi.utils import SpatialUtils, mode_or_first


class POI2HGIPreprocess:
    """Preprocessing pipeline for POI2HGI embeddings with temporal features."""

    def __init__(self, pois_filename, boroughs_filename, temp_path):
        self.pois_filename = pois_filename
        self.boroughs_filename = boroughs_filename
        self.temp_path = temp_path
        self.category_classes = None

    def _read_poi_data(self):
        """Load and prepare POI data with temporal information."""
        self.checkins = pd.read_parquet(self.pois_filename)

        if "category" not in self.checkins.columns:
            raise ValueError("Column 'category' missing from input data.")

        self.checkins = self.checkins.dropna(subset=["category"])

        # Parse datetime
        if 'local_datetime' in self.checkins.columns:
            self.checkins['datetime'] = pd.to_datetime(self.checkins['local_datetime'])
        elif 'datetime' in self.checkins.columns:
            self.checkins['datetime'] = pd.to_datetime(self.checkins['datetime'])
        else:
            raise ValueError("Column 'datetime' or 'local_datetime' missing from input data.")

        # Extract temporal features per check-in
        self.checkins['hour'] = self.checkins['datetime'].dt.hour
        self.checkins['dayofweek'] = self.checkins['datetime'].dt.dayofweek

        # Create geometry column if not exists
        if 'geometry' not in self.checkins.columns:
            self.checkins['geometry'] = self.checkins.apply(
                lambda x: f"POINT({x['longitude']} {x['latitude']})"
                if pd.notnull(x['longitude']) and pd.notnull(x['latitude'])
                else None,
                axis=1
            )

        # Aggregate to POI level - compute temporal features per POI
        self.pois = self._aggregate_to_pois()

        # Convert to GeoDataFrame
        self.pois["geometry"] = self.pois["geometry"].apply(wkt.loads)
        self.pois = gpd.GeoDataFrame(self.pois, geometry="geometry", crs="EPSG:4326")
        self.pois["geometry"] = self.pois["geometry"].apply(
            lambda x: x if x.geom_type == "Point" else x.centroid
        )

    def _aggregate_to_pois(self):
        """Aggregate check-ins to POI level with temporal features."""
        # Group by placeid and compute temporal distributions
        grouped = self.checkins.groupby('placeid')

        # Compute hour histogram (24 bins)
        hour_hist = grouped['hour'].apply(
            lambda x: np.histogram(x, bins=24, range=(0, 24), density=True)[0]
        )

        # Compute day-of-week histogram (7 bins)
        dow_hist = grouped['dayofweek'].apply(
            lambda x: np.histogram(x, bins=7, range=(0, 7), density=True)[0]
        )

        # Compute mean hour and dow (for sin/cos encoding)
        mean_hour = grouped['hour'].mean()
        mean_dow = grouped['dayofweek'].mean()

        # Visit count
        visit_count = grouped.size()

        # Get first category, geometry, lat/lon for each POI
        first_vals = grouped.agg({
            'category': mode_or_first,
            'geometry': 'first',
            'latitude': 'first',
            'longitude': 'first'
        }).reset_index()

        # Combine all features
        pois_df = first_vals.copy()
        pois_df['hour_hist'] = hour_hist.values.tolist()
        pois_df['dow_hist'] = dow_hist.values.tolist()
        pois_df['mean_hour'] = mean_hour.values
        pois_df['mean_dow'] = mean_dow.values
        pois_df['visit_count'] = visit_count.values

        return pois_df

    def _read_boroughs_data(self):
        """Load boroughs/regions data and encode categories."""
        self.boroughs = pd.read_csv(self.boroughs_filename)
        self.boroughs["geometry"] = self.boroughs["geometry"].apply(wkt.loads)
        self.boroughs = gpd.GeoDataFrame(self.boroughs, geometry="geometry", crs="EPSG:4326")

        # Encode categories (for output only, not used as features)
        le = LabelEncoder()
        self.pois["category_encoded"] = le.fit_transform(self.pois["category"].values)
        self.category_classes = le.classes_

        # Spatial join with boroughs
        self.pois = self.pois.sjoin(
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
                    w2 = 1.0 if self.pois.iloc[x]["GEOID"] == self.pois.iloc[y]["GEOID"] else 0.4
                    edges.append({'source': x, 'target': y, 'weight': w1 * w2})

        self.edges = pd.DataFrame(edges)

        # Normalize weights
        mi, ma = self.edges['weight'].min(), self.edges['weight'].max()
        self.edges['weight'] = (self.edges['weight'] - mi) / (ma - mi)

    def _compute_region_features(self):
        """Compute region-level features: areas, adjacency, and similarity."""
        unique_regions = self.pois['GEOID'].unique()
        region_to_idx = {region: idx for idx, region in enumerate(unique_regions)}

        # Map POIs to region indices
        self.region_id = self.pois['GEOID'].map(region_to_idx).values

        # Compute region areas
        self.region_area = np.array([
            self.boroughs[self.boroughs['GEOID'] == r].geometry.iloc[0].area
            for r in unique_regions
        ], dtype=np.float32)

        # Compute adjacency and similarity
        self.region_adjacency = self._compute_adjacency_matrix(unique_regions, region_to_idx)
        self.coarse_region_similarity = self._compute_temporal_similarity_matrix(region_to_idx, len(unique_regions))

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

    def _compute_temporal_similarity_matrix(self, region_to_idx, num_regions):
        """Compute region similarity based on temporal patterns (not category)."""
        similarity = np.zeros((num_regions, num_regions), dtype=np.float32)

        # Get temporal features per region
        region_temporal = {}
        for region, idx in region_to_idx.items():
            region_pois = self.pois[self.pois['GEOID'] == region]
            # Aggregate hour histograms for POIs in this region
            hour_hists = np.array(region_pois['hour_hist'].tolist())
            dow_hists = np.array(region_pois['dow_hist'].tolist())

            if len(hour_hists) > 0:
                # Mean temporal distribution for region
                region_hour = hour_hists.mean(axis=0)
                region_dow = dow_hists.mean(axis=0)
                region_temporal[idx] = np.concatenate([region_hour, region_dow])
            else:
                region_temporal[idx] = np.zeros(31)  # 24 + 7

        # Compute cosine similarity between regions
        for i in range(num_regions):
            for j in range(i, num_regions):
                if i in region_temporal and j in region_temporal:
                    vec_i = region_temporal[i]
                    vec_j = region_temporal[j]
                    norm_i = np.linalg.norm(vec_i)
                    norm_j = np.linalg.norm(vec_j)
                    if norm_i > 0 and norm_j > 0:
                        sim = np.dot(vec_i, vec_j) / (norm_i * norm_j)
                        similarity[i, j] = sim
                        similarity[j, i] = sim

        return similarity

    def _build_temporal_features(self):
        """Build temporal feature matrix for POIs (36 dimensions)."""
        features = []

        for idx, row in self.pois.iterrows():
            # Hour histogram (24 dims)
            hour_hist = np.array(row['hour_hist'])

            # Day-of-week histogram (7 dims)
            dow_hist = np.array(row['dow_hist'])

            # Sin/cos encoding of mean hour (2 dims)
            mean_hour = row['mean_hour']
            hour_sin = np.sin(2 * np.pi * mean_hour / 24)
            hour_cos = np.cos(2 * np.pi * mean_hour / 24)

            # Sin/cos encoding of mean dow (2 dims)
            mean_dow = row['mean_dow']
            dow_sin = np.sin(2 * np.pi * mean_dow / 7)
            dow_cos = np.cos(2 * np.pi * mean_dow / 7)

            # Log visit count (1 dim)
            visit_count_log = np.log1p(row['visit_count'])

            # Concatenate all features
            poi_features = np.concatenate([
                hour_hist,  # 24
                dow_hist,  # 7
                [hour_sin, hour_cos],  # 2
                [dow_sin, dow_cos],  # 2
                [visit_count_log]  # 1
            ])  # Total: 36

            features.append(poi_features)

        features = np.array(features, dtype=np.float32)

        # Normalize visit count (last dimension) to [0, 1]
        features[:, -1] = (features[:, -1] - features[:, -1].min()) / (features[:, -1].max() - features[:, -1].min() + 1e-8)

        return features

    def get_data_torch(self):
        """Execute full preprocessing pipeline."""
        print("Reading POI data with temporal features...")
        self._read_poi_data()

        print("Reading boroughs data...")
        self._read_boroughs_data()

        print("Creating spatial graph...")
        self._create_graph()

        print("Computing region features...")
        self._compute_region_features()

        print("Building temporal features...")
        node_features = self._build_temporal_features()

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
            'y': self.pois['category_encoded'].values,
            'place_id': self.pois['placeid'].values,
            'category_classes': self.category_classes,
        }


def preprocess_poi2hgi(city, city_shapefile, cta_file=None):
    """Main preprocessing function for POI2HGI."""
    temp_folder = IoPaths.POI2HGI.get_temp_dir(city)
    temp_folder.mkdir(parents=True, exist_ok=True)

    output_folder = IoPaths.POI2HGI.get_output_dir(city)
    output_folder.mkdir(parents=True, exist_ok=True)

    checkins = IoPaths.get_city(city)
    boroughs_path = Path(cta_file) if cta_file else IoPaths.POI2HGI.get_boroughs_file(city)

    # Create boroughs file if not exists
    if cta_file is None and not boroughs_path.exists():
        print(f"Creating boroughs file from shapefile: {city_shapefile}")
        census = gpd.read_file(city_shapefile).to_crs(4326)
        census[['GEOID', 'geometry']].to_csv(boroughs_path, index=False)

    pre = POI2HGIPreprocess(str(checkins), str(boroughs_path), temp_folder)
    data = pre.get_data_torch()

    output_path = IoPaths.POI2HGI.get_graph_data_file(city)
    with open(output_path, "wb") as f:
        pkl.dump(data, f)

    print(f"Saved: {output_path}")
    print(f"POIs: {data['number_pois']}, Regions: {data['number_regions']}, Edges: {len(data['edge_weight'])}")
    print(f"Node features shape: {data['node_features'].shape}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Preprocess POI data for POI2HGI')
    parser.add_argument('--city', type=str, default='Alabama')
    parser.add_argument('--shapefile', type=str, default=Resources.TL_AL)
    parser.add_argument('--cta', type=str, default=None)

    args = parser.parse_args()
    preprocess_poi2hgi(city=args.city, city_shapefile=args.shapefile, cta_file=args.cta)
