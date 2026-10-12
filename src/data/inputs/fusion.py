"""
Multi-embedding fusion for MTL inputs.

This module provides classes for aligning and fusing multiple embeddings from
different sources (HGI, Space2Vec, Time2Vec, etc.) into unified feature vectors.

Moved from src/etl/embedding_fusion.py to organize fusion logic with other
input generation components.

Architecture:
1. EmbeddingAligner - Aligns embeddings by POI ID or check-in ID
2. EmbeddingFuser - Concatenates aligned embeddings into unified feature space
3. MultiEmbeddingInputGenerator - Orchestrates the full pipeline
"""
import pandas as pd
import numpy as np
from typing import List
from pathlib import Path
from tqdm import tqdm

from configs.paths import IoPaths, EmbeddingEngine
from configs.embedding_fusion import EmbeddingSpec, EmbeddingLevel, FusionConfig
from configs.model import InputsConfig
from .core import (
    generate_sequences,
    PADDING_VALUE,
    convert_sequences_to_poi_embeddings,
    convert_user_checkins_to_sequences,
    save_next_input_dataframe,
    save_parquet,
    create_embedding_lookup,
    create_category_lookup,
    DEFAULT_BATCH_SIZE,
    MISSING_CATEGORY_VALUE,
)
from .loaders import EmbeddingLoader


class EmbeddingAligner:
    """
    Aligns embeddings from different sources by POI ID or check-in ID.

    Handles two alignment strategies:
    1. POI-level: Merge by placeid (for DGI, HGI, Space2Vec, etc.)
    2. Check-in-level: Merge by (userid, placeid, datetime) for Time2Vec
    """

    @staticmethod
    def align_poi_level(
        base_df: pd.DataFrame,
        embedding_dfs: List[pd.DataFrame],
        embedding_specs: List[EmbeddingSpec]
    ) -> pd.DataFrame:
        """
        Align multiple POI-level embeddings by placeid.

        Args:
            base_df: DataFrame with 'placeid' column (e.g., first embedding or checkins)
            embedding_dfs: List of embedding DataFrames to merge
            embedding_specs: Specs for dimension extraction

        Returns:
            DataFrame with concatenated embeddings aligned by placeid
        """
        result = base_df.copy()

        # Ensure placeid is int64 in base_df
        if 'placeid' in result.columns:
            result['placeid'] = result['placeid'].astype('int64')

        # Merge each embedding source by placeid
        for emb_df, spec in zip(embedding_dfs, embedding_specs):
            # Extract embedding columns (skip metadata columns like placeid, category)
            emb_cols = [str(i) for i in range(spec.dimension)]

            # Verify columns exist
            missing_cols = [c for c in emb_cols if c not in emb_df.columns]
            if missing_cols:
                raise KeyError(
                    f"{spec.engine.value} missing columns: {missing_cols[:5]}... "
                    f"(expected {spec.dimension} dims)"
                )

            emb_data = emb_df[['placeid'] + emb_cols].copy()

            # Ensure placeid is int64 in emb_data
            emb_data['placeid'] = emb_data['placeid'].astype('int64')

            # Deduplicate: drop identical rows; raise on conflicting duplicates
            dups = emb_data[emb_data.duplicated(subset=['placeid'], keep=False)]
            if not dups.empty:
                # Check whether all duplicates have identical embedding values
                conflict = dups[dups.duplicated(subset=['placeid'] + emb_cols, keep=False) == False]
                if not conflict.empty:
                    bad_ids = conflict['placeid'].unique()[:3].tolist()
                    raise ValueError(
                        f"{spec.engine.value}: duplicate placeid(s) {bad_ids} with DIFFERENT embedding "
                        f"values — cannot merge safely"
                    )
                n_before = len(emb_data)
                emb_data = emb_data.drop_duplicates(subset=['placeid'] + emb_cols)
                print(f"  INFO: Deduplicated {n_before - len(emb_data)} identical rows from {spec.engine.value} embeddings")

            # Rename columns to avoid conflicts: 0, 1, ... -> engine_0, engine_1, ...
            emb_data = emb_data.rename(columns={
                str(i): f"{spec.engine.value}_{i}" for i in range(spec.dimension)
            })

            # Left join on placeid
            pre_merge_len = len(result)
            result = result.merge(emb_data, on='placeid', how='left')
            if len(result) != pre_merge_len:
                raise ValueError(
                    f"Row count changed after merging {spec.engine.value}: "
                    f"{pre_merge_len} → {len(result)}. "
                    f"Likely duplicate placeids in base or embedding."
                )

        return result

    @staticmethod
    def align_checkin_level(
        checkins_df: pd.DataFrame,
        embedding_dfs: List[pd.DataFrame],
        embedding_specs: List[EmbeddingSpec]
    ) -> pd.DataFrame:
        """
        Align check-in-level embeddings by (userid, placeid, datetime).

        Critical: Check-in-level embeddings (Time2Vec) must be aligned by
        the composite key (userid, placeid, datetime) to ensure correct matching.
        POI-level embeddings can be aligned by just placeid.

        Args:
            checkins_df: DataFrame with check-ins (userid, placeid, datetime, category)
            embedding_dfs: List of embedding DataFrames to merge
            embedding_specs: Specs for dimension extraction

        Returns:
            DataFrame with aligned embeddings
        """
        result = checkins_df.copy()

        # Ensure placeid is int64 in result
        if 'placeid' in result.columns:
            result['placeid'] = result['placeid'].astype('int64')

        for emb_df, spec in zip(embedding_dfs, embedding_specs):
            emb_cols = [str(i) for i in range(spec.dimension)]

            # Verify columns exist
            missing_cols = [c for c in emb_cols if c not in emb_df.columns]
            if missing_cols:
                raise KeyError(
                    f"{spec.engine.value} missing columns: {missing_cols[:5]}... "
                    f"(expected {spec.dimension} dims)"
                )

            if spec.level == EmbeddingLevel.CHECKIN:
                # Align by composite key (userid, placeid, datetime)
                # Ensure datetime columns are compatible
                emb_df = emb_df.copy()
                emb_df['datetime'] = pd.to_datetime(emb_df['datetime'])
                result['datetime'] = pd.to_datetime(result['datetime'])

                emb_data = emb_df[['userid', 'placeid', 'datetime'] + emb_cols].copy()

                # Ensure placeid is int64
                emb_data['placeid'] = emb_data['placeid'].astype('int64')

                # Deduplicate: drop identical rows; raise on conflicting composite keys
                key_cols = ['userid', 'placeid', 'datetime']
                dups = emb_data[emb_data.duplicated(subset=key_cols, keep=False)]
                if not dups.empty:
                    conflict = dups[dups.duplicated(subset=key_cols + emb_cols, keep=False) == False]
                    if not conflict.empty:
                        raise ValueError(
                            f"{spec.engine.value}: duplicate composite key(s) with DIFFERENT embedding "
                            f"values — cannot merge safely"
                        )
                    n_before = len(emb_data)
                    emb_data = emb_data.drop_duplicates(subset=key_cols + emb_cols)
                    print(f"  INFO: Deduplicated {n_before - len(emb_data)} identical rows from {spec.engine.value} embeddings")

                # Rename columns
                emb_data = emb_data.rename(columns={
                    str(i): f"{spec.engine.value}_{i}" for i in range(spec.dimension)
                })

                # Merge on composite key
                pre_merge_len = len(result)
                result = result.merge(
                    emb_data,
                    on=['userid', 'placeid', 'datetime'],
                    how='left'
                )
                if len(result) != pre_merge_len:
                    raise ValueError(
                        f"Row count changed after merging {spec.engine.value}: "
                        f"{pre_merge_len} → {len(result)}. "
                        f"Likely duplicate keys in embedding or check-ins."
                    )

            elif spec.level == EmbeddingLevel.POI:
                # POI-level: just align by placeid
                emb_data = emb_df[['placeid'] + emb_cols].copy()

                # Ensure placeid is int64
                emb_data['placeid'] = emb_data['placeid'].astype('int64')

                # Deduplicate: drop identical rows; raise on conflicting placeids
                dups = emb_data[emb_data.duplicated(subset=['placeid'], keep=False)]
                if not dups.empty:
                    conflict = dups[dups.duplicated(subset=['placeid'] + emb_cols, keep=False) == False]
                    if not conflict.empty:
                        bad_ids = conflict['placeid'].unique()[:3].tolist()
                        raise ValueError(
                            f"{spec.engine.value}: duplicate placeid(s) {bad_ids} with DIFFERENT embedding "
                            f"values — cannot merge safely"
                        )
                    n_before = len(emb_data)
                    emb_data = emb_data.drop_duplicates(subset=['placeid'] + emb_cols)
                    print(f"  INFO: Deduplicated {n_before - len(emb_data)} identical rows from {spec.engine.value} embeddings")

                emb_data = emb_data.rename(columns={
                    str(i): f"{spec.engine.value}_{i}" for i in range(spec.dimension)
                })

                pre_merge_len = len(result)
                result = result.merge(emb_data, on='placeid', how='left')
                if len(result) != pre_merge_len:
                    raise ValueError(
                        f"Row count changed after merging {spec.engine.value}: "
                        f"{pre_merge_len} → {len(result)}. "
                        f"Likely duplicate placeids in embedding."
                    )

        return result


class EmbeddingFuser:
    """
    Fuses aligned embeddings into concatenated feature vectors.
    """

    @staticmethod
    def fuse_embeddings(
        df: pd.DataFrame,
        embedding_specs: List[EmbeddingSpec],
        output_prefix: str = "fused"
    ) -> pd.DataFrame:
        """
        Concatenate embedding columns into unified feature space.

        Args:
            df: DataFrame with aligned embeddings (engine_0, engine_1, ...)
            embedding_specs: List of specs (defines order and dimensions)
            output_prefix: Prefix for output columns (e.g., 'fused' -> fused_0, fused_1, ...)

        Returns:
            DataFrame with concatenated embeddings in columns: prefix_0, prefix_1, ...
        """
        result = df.copy()
        fused_embeddings = []

        # Concatenate in order of specs
        for spec in embedding_specs:
            # Extract columns for this engine
            engine_cols = [f"{spec.engine.value}_{i}" for i in range(spec.dimension)]

            # Check for missing values
            missing_count = result[engine_cols].isna().sum().sum()
            if missing_count > 0:
                print(f"WARNING: {missing_count} missing values in {spec.engine.value} embeddings")
                # Fill with zeros for missing POIs
                result[engine_cols] = result[engine_cols].fillna(0.0)

            fused_embeddings.extend(engine_cols)

        # Rename to unified naming: fused_0, fused_1, ..., fused_127
        total_dim = sum(spec.dimension for spec in embedding_specs)
        rename_map = {
            old_col: f"{output_prefix}_{i}"
            for i, old_col in enumerate(fused_embeddings)
        }
        result = result.rename(columns=rename_map)

        return result


class MultiEmbeddingInputGenerator:
    """
    Main orchestrator for multi-embedding input generation.

    Generates category and next-POI task inputs with fused embeddings.
    """

    def __init__(self, state: str, fusion_config: FusionConfig):
        """
        Initialize generator.

        Args:
            state: State name (e.g., 'florida', 'alabama')
            fusion_config: Fusion configuration
        """
        self.state = state
        self.config = fusion_config
        self.loader = EmbeddingLoader(state)

    def _has_checkin_level(self) -> bool:
        """Check if next_embeddings contains any check-in-level embeddings."""
        return any(
            spec.level == EmbeddingLevel.CHECKIN
            for spec in self.config.next_embeddings
        )

    def generate_category_input(self, output_path: str):
        """
        Generate category task input with fused embeddings.

        Output format: placeid | category | 0 | 1 | ... | (total_dim-1)

        Args:
            output_path: Path to save category parquet file
        """
        print(f"\n=== Generating Category Input ===")
        print(f"Embeddings: {self.config.get_category_engines()}")
        print(f"Total dimension: {self.config.get_category_dim()}")

        # Load all category embedding sources
        embedding_dfs = [
            self.loader.load(spec) for spec in self.config.category_embeddings
        ]

        # Use first embedding as base (has placeid + category)
        base_df = embedding_dfs[0][['placeid', 'category']].copy()
        print(f"Base POIs: {len(base_df)}")

        # Align all embeddings by placeid
        print("Aligning embeddings...")
        aligned_df = EmbeddingAligner.align_poi_level(
            base_df, embedding_dfs, self.config.category_embeddings
        )

        # Fuse embeddings
        print("Fusing embeddings...")
        fused_df = EmbeddingFuser.fuse_embeddings(
            aligned_df, self.config.category_embeddings, output_prefix="fused"
        )

        # Extract final columns: placeid, category, fused_0..fused_(total_dim-1)
        total_dim = self.config.get_category_dim()
        final_cols = ['placeid', 'category'] + [f'fused_{i}' for i in range(total_dim)]
        output_df = fused_df[final_cols]

        # Rename fused columns to numeric (for compatibility with existing code)
        output_df = output_df.rename(columns={
            f'fused_{i}': str(i) for i in range(total_dim)
        })

        # Save
        save_parquet(output_df, output_path)

        print(f"✓ Category input saved: {output_path}")
        print(f"  Shape: {output_df.shape}")
        print(f"  Columns: {list(output_df.columns[:5])}... {list(output_df.columns[-2:])}")

    def generate_next_input(self, sequences_output_path: str, embeddings_output_path: str):
        """
        Generate next-POI task input with fused embeddings.

        Process:
        1. Load check-ins
        2. Align all embeddings (POI-level + check-in-level)
        3. Generate sequences using existing logic from create_input.py
        4. Convert sequences to embedding format (flatten window)

        Output format: 0 | 1 | ... | (window*dim-1) | next_category | userid

        Args:
            sequences_output_path: Path to save intermediate sequences
            embeddings_output_path: Path to save final next-POI parquet file
        """
        print(f"\n=== Generating Next-POI Input ===")
        print(f"Embeddings: {self.config.get_next_engines()}")
        print(f"Total dimension: {self.config.get_next_dim()}")

        # Load check-ins
        print("Loading check-ins...")
        checkins_df = IoPaths.load_city(self.state)

        # Parse datetime and sort
        checkins_df['datetime'] = pd.to_datetime(checkins_df['datetime'])
        checkins_df = checkins_df.sort_values(['userid', 'datetime']).reset_index(drop=True)

        # Deduplicate check-ins (raw data may have duplicate rows)
        n_before = len(checkins_df)
        checkins_df = checkins_df.drop_duplicates(
            subset=['userid', 'placeid', 'datetime']
        ).reset_index(drop=True)
        n_deduped = n_before - len(checkins_df)
        if n_deduped > 0:
            print(f"  INFO: Removed {n_deduped} duplicate check-in rows")
        print(f"Check-ins: {len(checkins_df)}")

        # Load all next-POI embedding sources
        embedding_dfs = [
            self.loader.load(spec) for spec in self.config.next_embeddings
        ]

        # Align embeddings (handles both POI-level and check-in-level)
        print("Aligning embeddings...")
        aligned_df = EmbeddingAligner.align_checkin_level(
            checkins_df, embedding_dfs, self.config.next_embeddings
        )

        # Fuse embeddings
        print("Fusing embeddings...")
        fused_df = EmbeddingFuser.fuse_embeddings(
            aligned_df, self.config.next_embeddings, output_prefix="fused"
        )

        # Branch based on embedding type
        if self._has_checkin_level():
            print("Using check-in-level conversion (position-based lookup)...")
            self._generate_next_input_checkin_level(
                fused_df, sequences_output_path, embeddings_output_path
            )
        else:
            print("Using POI-level conversion (dictionary lookup)...")
            self._generate_next_input_poi_level(
                fused_df, sequences_output_path, embeddings_output_path
            )

    def _generate_next_input_poi_level(
        self,
        fused_df: pd.DataFrame,
        sequences_output_path: str,
        embeddings_output_path: str
    ):
        """
        Generate next-POI input using POI-level dictionary lookup.

        Used when all embeddings are POI-level (same embedding for same POI).
        """
        window_size = InputsConfig.SLIDE_WINDOW
        total_dim = self.config.get_next_dim()

        # Generate sequences per user
        print("Generating sequences...")
        user_sequences = []
        for userid, user_df in fused_df.groupby('userid'):
            places = user_df['placeid'].tolist()
            seqs = generate_sequences(places)

            for seq in seqs:
                seq_with_userid = seq + [userid]
                user_sequences.append(seq_with_userid)

        # Create sequences DataFrame
        seq_cols = [f'poi_{i}' for i in range(window_size)] + ['target_poi', 'userid']
        sequences_df = pd.DataFrame(user_sequences, columns=seq_cols)

        # Save intermediate sequences
        save_parquet(sequences_df, sequences_output_path)
        print(f"Sequences saved: {len(sequences_df)} sequences → {sequences_output_path}")

        # Convert sequences to embeddings using POI dictionary lookup
        print("Converting to embeddings...")
        fused_cols = [f'fused_{i}' for i in range(total_dim)]
        poi_embeddings = fused_df.groupby('placeid')[fused_cols].first()

        # Rename columns to numeric for compatibility with core function
        renamed_embeddings = poi_embeddings.rename(columns={
            f'fused_{i}': str(i) for i in range(total_dim)
        }).reset_index()

        # Create lookups using core functions
        embedding_lookup = create_embedding_lookup(renamed_embeddings, total_dim)
        category_lookup = create_category_lookup(fused_df)

        # Use centralized POI-level conversion
        all_results = convert_sequences_to_poi_embeddings(
            sequences_df, embedding_lookup, category_lookup,
            window_size, total_dim, DEFAULT_BATCH_SIZE
        )

        # Build and save the output DataFrame to the caller-specified path
        num_features = window_size * total_dim
        emb_cols = list(map(str, range(num_features)))
        arr = np.array(all_results)  # (N, num_features + 2), object dtype
        output_df = pd.DataFrame(arr[:, :num_features].astype(np.float32), columns=emb_cols)
        output_df['next_category'] = arr[:, num_features].tolist()
        output_df['userid'] = arr[:, num_features + 1].tolist()
        save_parquet(output_df, embeddings_output_path)
        print(f"✓ Next-POI input saved (POI-level): {embeddings_output_path}")

    def _generate_next_input_checkin_level(
        self,
        fused_df: pd.DataFrame,
        sequences_output_path: str,
        embeddings_output_path: str
    ):
        """
        Generate next-POI input using position-based lookup for check-in-level embeddings.

        Used when any embedding is check-in-level (Time2Vec, Check2HGI).
        Each position in the sequence maps directly to a row in the user's history.
        """
        total_dim = self.config.get_next_dim()
        fused_cols = [f'fused_{i}' for i in range(total_dim)]
        window_size = InputsConfig.SLIDE_WINDOW

        # Process each user using shared function
        all_results = []
        all_sequences = []

        for userid, user_df in tqdm(fused_df.groupby('userid'), desc="Processing users"):
            user_df = user_df.reset_index(drop=True)

            results, sequences = convert_user_checkins_to_sequences(
                user_df, fused_cols, window_size, total_dim
            )

            all_results.extend(results)
            all_sequences.extend(sequences)

        # Save intermediate sequences
        seq_cols = [f'poi_{i}' for i in range(window_size)] + ['target_poi', 'userid']
        sequences_df = pd.DataFrame(all_sequences, columns=seq_cols)
        save_parquet(sequences_df, sequences_output_path)
        print(f"Sequences saved: {len(sequences_df)} sequences → {sequences_output_path}")

        # Save output to the caller-specified path
        num_features = window_size * total_dim
        emb_cols = list(map(str, range(num_features)))
        arr = np.array(all_results)  # (N, num_features + 2), object dtype
        output_df = pd.DataFrame(arr[:, :num_features].astype(np.float32), columns=emb_cols)
        output_df['next_category'] = arr[:, num_features].tolist()
        output_df['userid'] = arr[:, num_features + 1].tolist()
        save_parquet(output_df, embeddings_output_path)
        print(f"✓ Next-POI input saved (check-in level): {embeddings_output_path}")
